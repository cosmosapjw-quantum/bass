//! Cold elastic Thomson spectral moment transport on a fixed accepted BASS
//! geometry and collision schedule. Centered Mellin B3/B4, log raw M0..M2.
//! Independent angular gain normalization and independent spectral sources.
//! Spectral pass does not change material velocities, chemistry or geometry.
use super::{field::HarmonicSky, recoil::gain_map, replay::StepRecord, *};
use crate::kinetic::spin_sht::C64;
use nalgebra::SMatrix;

pub const CARRIERS: [&str; 5] = ["B3", "B4", "M0", "M1", "M2"];
#[derive(Clone, Debug)]
struct Bundle {
    e: V,
    w: f64,
    m: [M; 5],
}
impl Bundle {
    fn initial(p: &Photon) -> Self {
        Self {
            e: p.direction,
            w: p.weight,
            m: [p.screen, p.screen, p.screen, M::zeros(), M::zeros()],
        }
    }
    fn photon(&self, k: usize) -> Photon {
        Photon {
            direction: self.e,
            weight: self.w,
            screen: self.m[k],
        }
    }
    fn boost(&self, b: V) -> Result<Self, String> {
        let (e, j, d) = super::boost(self.e, b)?;
        let l = d.ln();
        let v = |k: usize| j * self.m[k] * j.transpose();
        Ok(Self {
            e,
            w: self.w / (d * d),
            m: [
                v(0) * d.powi(3),
                v(1) * d.powi(4),
                v(2),
                v(3) + l * v(2),
                v(4) + 2. * l * v(3) + l * l * v(2),
            ],
        })
    }
    fn geometric(&mut self, l: &RayNode, r: &RayNode) -> Result<(), String> {
        let s = advance_ray(l, r, self.e.into())?;
        let rot = M::from_fn(|i, j| s.rotation[i][j]);
        let x = s.log_energy + (r.eta - l.eta);
        let m = self.m.map(|v| rot * v * rot.transpose());
        self.m = [
            m[0] * (3. * x).exp(),
            m[1] * (4. * x).exp(),
            m[2],
            m[3] + x * m[2],
            m[4] + 2. * x * m[3] + x * x * m[2],
        ];
        self.e = V::from(s.e);
        self.w *= s.log_area.exp();
        Ok(())
    }
}
struct Rest {
    d: f64,
    area: f64,
    lift_back: M,
    projector: M,
}
/// Solve all five independent material-frame sources with the same 6x6
/// matrix. Return increments, not overwritten O(1) fields, to avoid thin
/// collision drift. Raw signed log moments must NOT use positivity checks
/// intended for bolometric intensity.
fn implicit_increment(terms: &[Rest], input: &[[M; 5]], depth: f64) -> Result<Vec<[M; 5]>, String> {
    let mut lhs = SMatrix::<f64, 6, 6>::identity();
    let mut rhs = SMatrix::<f64, 6, 5>::zeros();
    let mut alpha = Vec::with_capacity(terms.len());
    const PAIRS: [(usize, usize); 6] = [(0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2)];
    for (t, m) in terms.iter().zip(input) {
        let z = depth * t.d;
        if !z.is_finite() {
            return Err("spectral cell optical depth overflow".into());
        }
        let a = z / (1. + z);
        let tr = 1. / (1. + z);
        alpha.push(a);
        for k in 0..5 {
            let v = pack(m[k]) * (t.area * tr);
            for j in 0..6 {
                rhs[(j, k)] += v[j];
            }
        }
        let gp = &t.projector;
        for (row, &(i, j)) in PAIRS.iter().enumerate() {
            for (col, &(k, l)) in PAIRS.iter().enumerate() {
                let v = gp[(i, k)] * gp[(j, l)] + if k == l { 0. } else { gp[(i, l)] * gp[(j, k)] };
                lhs[(row, col)] -= t.area * a * GAIN * v;
            }
        }
    }
    let source = lhs
        .lu()
        .solve(&rhs)
        .ok_or("singular spectral Thomson source")?;
    let s: [M; 5] = std::array::from_fn(|k| unpack(source.column(k).into_owned()));
    Ok(terms
        .iter()
        .zip(input)
        .zip(alpha)
        .map(|((t, m), a)| {
            std::array::from_fn(|k| {
                a * (GAIN * t.projector * s[k] * t.projector.transpose() - m[k])
            })
        })
        .collect())
}
fn collide(rays: &mut [Bundle], ev: &CollisionEvent) -> Result<(f64, f64), String> {
    let beta = V::from(ev.beta);
    validate_cell(ev.depth, &beta)?;
    if ev.depth == 0. {
        return Ok((0., 0.));
    }
    // Same gain-normalization construction as BASS recoil but recomputed
    // on THIS mesh. A saved B4 source is not a source for B3 or M_k.
    let photons: Vec<_> = rays.iter().map(|r| r.photon(1)).collect();
    let map = gain_map(&photons, beta)?;
    let mut terms = Vec::with_capacity(rays.len());
    let mut inputs = Vec::with_capacity(rays.len());
    for r in rays.iter() {
        let (e, j, d) = super::boost(r.e, beta)?;
        let (_, inv, _) = super::boost(e, -beta)?;
        terms.push(Rest {
            d,
            area: r.w / (d * d),
            lift_back: inv,
            projector: projector(&e) * map,
        });
        let l = d.ln();
        let v = r.m.map(|m| j * m * j.transpose());
        inputs.push([
            v[0] * d.powi(3),
            v[1] * d.powi(4),
            v[2],
            v[3] + l * v[2],
            v[4] + 2. * l * v[3] + l * l * v[2],
        ]);
    }
    let delta = match ev.scheme {
        CollisionScheme::BackwardEuler => implicit_increment(&terms, &inputs, ev.depth)?,
        CollisionScheme::Sdirk2 => {
            let d = ev.depth * SDIRK_GAMMA;
            let a = implicit_increment(&terms, &inputs, d)?;
            let q: Vec<_> = inputs
                .iter()
                .zip(&a)
                .map(|(x, dx)| std::array::from_fn(|k| x[k] + (1. + SQRT_2) * dx[k]))
                .collect();
            let b = implicit_increment(&terms, &q, d)?;
            a.iter()
                .zip(b)
                .map(|(x, y)| std::array::from_fn(|k| (1. + SQRT_2) * x[k] + y[k]))
                .collect()
        }
    };
    let mut dn = 0.;
    let mut de = 0.;
    let mut n = 0.;
    let mut en = 0.;
    for ((r, t), dm) in rays.iter_mut().zip(terms).zip(delta) {
        let l = t.d.ln();
        let v = dm.map(|m| t.lift_back * m * t.lift_back.transpose());
        let out = [
            v[0] / t.d.powi(3),
            v[1] / t.d.powi(4),
            v[2],
            v[3] - l * v[2],
            v[4] - 2. * l * v[3] + l * l * v[2],
        ];
        n += r.w * r.m[0].trace();
        en += r.w * t.d * r.m[1].trace();
        dn += r.w * out[0].trace();
        de += r.w * t.d * out[1].trace();
        for (x, dx) in r.m.iter_mut().zip(out) {
            *x += 0.5 * (dx + dx.transpose());
        }
        check_bundle(r)?;
    }
    Ok((
        dn.abs() / n.abs().max(f64::MIN_POSITIVE),
        de.abs() / en.abs().max(f64::MIN_POSITIVE),
    ))
}

fn check_bundle(r: &Bundle) -> Result<(), String> {
    if !r.w.is_finite()
        || r.w <= 0.
        || !r.e.iter().all(|x| x.is_finite())
        || r.m.iter().any(|m| !m.iter().all(|x| x.is_finite()))
        || r.m[..3].iter().any(|m| m.trace() <= 0.)
    {
        return Err("nonfinite or nonpositive primary spectral moment".into());
    }
    Ok(())
}
#[derive(Clone, Debug)]
pub struct Sample {
    pub direction: [f64; 3],
    pub weight: f64,
    pub b3: f64,
    pub b4: f64,
    pub m0: f64,
    pub mean_log_t: f64,
    pub variance: f64,
    pub y_m: f64,
    /// Smallest screen eigenvalue among B3,B4,M0,M2, and 4x4 moment Gram.
    /// A finite-band projection is not generally realizability-preserving.
    pub min_primary_eigenvalue: f64,
    pub min_log_gram_eigenvalue: f64,
    pub screens: [[[f64; 3]; 3]; 5],
}
impl Sample {
    fn from_bundle(r: &Bundle) -> Result<Self, String> {
        check_bundle(r)?;
        let [b3, b4, m0, m1, m2] = r.m.map(|m| m.trace());
        let mean = m1 / m0;
        let variance = m2 / m0 - mean * mean;
        let y_m = ((b4 / m0).ln() - (4. / 3.) * (b3 / m0).ln()) / 4.;
        if ![mean, variance, y_m].iter().all(|x| x.is_finite()) {
            return Err("nonfinite derived spectral moment".into());
        }
        let e = r.e;
        let seed = if e.z.abs() < 0.8 { V::z() } else { V::x() };
        let t = (seed - e.dot(&seed) * e).normalize();
        let p = e.cross(&t);
        let screen = |m: M| {
            nalgebra::Matrix2::new(
                t.dot(&(m * t)),
                t.dot(&(m * p)),
                p.dot(&(m * t)),
                p.dot(&(m * p)),
            )
        };
        let g = |m: M| screen(m).symmetric_eigen().eigenvalues.min();
        let primary = [0, 1, 2, 4]
            .iter()
            .map(|&i| g(r.m[i]))
            .fold(f64::INFINITY, f64::min);
        let a = screen(r.m[2]);
        let b = screen(r.m[3]);
        let c = screen(r.m[4]);
        let gram = SMatrix::<f64, 4, 4>::from_fn(|i, j| match (i / 2, j / 2) {
            (0, 0) => a[(i % 2, j % 2)],
            (1, 1) => c[(i % 2, j % 2)],
            _ => b[(i % 2, j % 2)],
        });
        Ok(Self {
            direction: e.into(),
            weight: r.w,
            b3,
            b4,
            m0,
            mean_log_t: mean,
            variance,
            y_m,
            min_primary_eigenvalue: primary,
            min_log_gram_eigenvalue: gram.symmetric_eigen().eigenvalues.min(),
            screens: std::array::from_fn(|i| rows(&r.m[i])),
        })
    }
}
#[derive(Clone, Debug)]
pub struct Snapshot {
    pub eta: f64,
    /// Normal-frame number density and flux, divided by the emission density
    /// and multiplied by exp(3 eta). Class B has N'=2 A dot F.
    pub number_comoving: f64,
    pub number_flux_comoving: [f64; 3],
    pub energy_comoving: f64,
    pub mean_variance: f64,
    pub min_variance: f64,
    pub max_variance: f64,
    pub mean_y_m: f64,
    pub min_y_m: f64,
    pub max_m0_defect: f64,
    pub min_primary_eigenvalue: f64,
    pub min_log_gram_eigenvalue: f64,
}
fn snapshot(rays: &[Bundle], eta: f64) -> Result<Snapshot, String> {
    let mut s = Snapshot {
        eta,
        number_comoving: 0.,
        number_flux_comoving: [0.; 3],
        energy_comoving: 0.,
        mean_variance: 0.,
        min_variance: f64::INFINITY,
        max_variance: f64::NEG_INFINITY,
        mean_y_m: 0.,
        min_y_m: f64::INFINITY,
        max_m0_defect: 0.,
        min_primary_eigenvalue: f64::INFINITY,
        min_log_gram_eigenvalue: f64::INFINITY,
    };
    let mut area = 0.;
    for r in rays {
        let q = Sample::from_bundle(r)?;
        area += q.weight;
        s.number_comoving += q.weight * q.b3 / (4. * PI);
        for i in 0..3 {
            s.number_flux_comoving[i] += q.weight * q.b3 * q.direction[i] / (4. * PI);
        }
        s.energy_comoving += q.weight * q.b4 / (4. * PI);
        s.mean_variance += q.weight * q.variance;
        s.mean_y_m += q.weight * q.y_m;
        s.min_variance = s.min_variance.min(q.variance);
        s.max_variance = s.max_variance.max(q.variance);
        s.min_y_m = s.min_y_m.min(q.y_m);
        s.max_m0_defect = s.max_m0_defect.max((q.m0 - 1.).abs());
        s.min_primary_eigenvalue = s.min_primary_eigenvalue.min(q.min_primary_eigenvalue);
        s.min_log_gram_eigenvalue = s.min_log_gram_eigenvalue.min(q.min_log_gram_eigenvalue);
    }
    if !area.is_finite() || area <= 0. {
        return Err("invalid spectral quadrature area".into());
    }
    s.mean_variance /= area;
    s.mean_y_m /= area;
    Ok(s)
}
pub struct SpectralSky {
    rays: Vec<Bundle>,
    pub history: Vec<Snapshot>,
    pub max_collision_number_defect: f64,
    pub max_collision_rest_energy_defect: f64,
    /// [carrier][spin slot][signed harmonic index], available in harmonic route.
    pub coefficients: Option<Vec<Vec<Vec<C64>>>>,
    pub collision_events: usize,
}
impl SpectralSky {
    /// Necessary, not sufficient, realizability checks on sampled normal-frame
    /// accepted history. The absolute tolerance is explicit and no negative
    /// moments are clipped. Consumers must not treat a warning as admission.
    pub fn sampled_necessary_checks(&self, tol: f64) -> Result<bool, String> {
        if !tol.is_finite() || tol < 0. {
            return Err("invalid spectral realizability tolerance".into());
        }
        Ok(self.history.iter().all(|q| {
            q.min_variance >= -tol
                && q.min_y_m >= -tol
                && q.min_primary_eigenvalue >= -tol
                && q.min_log_gram_eigenvalue >= -tol
                && q.max_m0_defect <= tol
        }))
    }
    pub fn samples(&self) -> Result<Vec<Sample>, String> {
        self.rays.iter().map(Sample::from_bundle).collect()
    }
    /// A true boost of the five carriers (direction remains propagation).
    /// The FLRW-centered reference is the same scalar on this event.
    pub fn observer_samples(&self, beta: [f64; 3]) -> Result<Vec<Sample>, String> {
        self.rays
            .iter()
            .map(|r| Sample::from_bundle(&r.boost(V::from(beta))?))
            .collect()
    }
    /// Trapezoidal check of continuum class-B number continuity:
    /// e^(3 eta) n'/redshift correction = 2 A dot e^(3 eta) flux.
    /// Residual includes history quadrature error (not a discrete identity).
    pub fn number_continuity_defect(&self, records: &[StepRecord]) -> Result<f64, String> {
        validate_records(records)?;
        if self.history.len() != records.len() + 1 {
            return Err("spectral history length mismatch".into());
        }
        let mut integrated = 0.;
        for (r, s) in records.iter().zip(self.history.windows(2)) {
            if s[0].eta != r.left.eta || s[1].eta != r.right.eta {
                return Err("spectral continuity clock mismatch".into());
            }
            let rhs = |n: &RayNode, q: &Snapshot| {
                n.a.iter()
                    .zip(q.number_flux_comoving)
                    .map(|(a, b)| a * b)
                    .sum::<f64>()
            };
            integrated += (r.right.eta - r.left.eta) * (rhs(&r.left, &s[0]) + rhs(&r.right, &s[1]));
        }
        Ok(self.history.last().unwrap().number_comoving
            - self.history[0].number_comoving
            - integrated)
    }
    pub fn bolometric_gap(&self, photons: &[Photon]) -> Result<f64, String> {
        if photons.len() != self.rays.len() {
            return Err("incompatible energy comparison mesh".into());
        }
        let eta = self.history.last().ok_or("empty spectral history")?.eta;
        let scale = (-4. * eta).exp();
        let mut gap: f64 = 0.;
        let mut norm: f64 = 0.;
        for (r, p) in self.rays.iter().zip(photons) {
            if (r.e - p.direction).norm() > 1e-11 {
                return Err("incompatible energy comparison directions".into());
            }
            gap = gap.max((scale * r.m[1] - p.screen).norm());
            norm = norm.max(p.screen.norm());
        }
        Ok(gap / norm.max(f64::MIN_POSITIVE))
    }
}
fn validate_records(records: &[StepRecord]) -> Result<(), String> {
    if records.is_empty() || records[0].left.eta != 0. {
        return Err("spectral replay needs nonempty emission history from eta=0".into());
    }
    for (i, r) in records.iter().enumerate() {
        crate::kinetic::lie_hierarchy::lie_data(&r.left).validate()?;
        crate::kinetic::lie_hierarchy::lie_data(&r.right).validate()?;
        if !r.left.eta.is_finite()
            || !r.right.eta.is_finite()
            || r.right.eta <= r.left.eta
            || (i > 0
                && (records[i - 1].right.eta != r.left.eta
                    || crate::kinetic::lie_hierarchy::lie_data(&records[i - 1].right)
                        != crate::kinetic::lie_hierarchy::lie_data(&r.left)))
        {
            return Err("invalid spectral replay clock".into());
        }
    }
    Ok(())
}
fn apply_events(
    rays: &mut [Bundle],
    events: &[CollisionEvent],
    number: &mut f64,
    energy: &mut f64,
    count: &mut usize,
) -> Result<(), String> {
    for ev in events {
        let (n, e) = collide(rays, ev)?;
        *number = number.max(n);
        *energy = energy.max(e);
        *count += 1;
    }
    Ok(())
}
pub fn replay_rays(records: &[StepRecord], nmu: usize, nphi: usize) -> Result<SpectralSky, String> {
    validate_records(records)?;
    let mut rays = initial_sky(nmu, nphi)?
        .iter()
        .map(Bundle::initial)
        .collect::<Vec<_>>();
    let mut history = vec![snapshot(&rays, 0.)?];
    let (mut number, mut energy, mut count) = (0., 0., 0);
    for r in records {
        apply_events(&mut rays, &r.first, &mut number, &mut energy, &mut count)?;
        for p in &mut rays {
            p.geometric(&r.left, &r.right)?;
        }
        apply_events(&mut rays, &r.second, &mut number, &mut energy, &mut count)?;
        history.push(snapshot(&rays, r.right.eta)?);
    }
    Ok(SpectralSky {
        rays,
        history,
        max_collision_number_defect: number,
        max_collision_rest_energy_defect: energy,
        coefficients: None,
        collision_events: count,
    })
}
struct HarmonicMoments {
    b3: HarmonicSky,
    b4: HarmonicSky,
    logs: [HarmonicSky; 3],
}
impl HarmonicMoments {
    fn new(l: usize, nt: usize, np: usize) -> Result<Self, String> {
        let b3 = HarmonicSky::with_carrier(l, nt, np, true, 3.)?;
        let b4 = HarmonicSky::with_carrier(l, nt, np, true, 4.)?;
        let m0 = HarmonicSky::with_carrier(l, nt, np, true, 0.)?;
        let mut m1 = m0.clone();
        m1.coefficients
            .iter_mut()
            .flatten()
            .for_each(|z| *z = C64::new(0., 0.));
        Ok(Self {
            b3,
            b4,
            logs: [m0, m1.clone(), m1],
        })
    }
    fn fields(&self) -> [&HarmonicSky; 5] {
        [
            &self.b3,
            &self.b4,
            &self.logs[0],
            &self.logs[1],
            &self.logs[2],
        ]
    }
    fn rays(&self) -> Result<Vec<Bundle>, String> {
        let grids = self
            .fields()
            .iter()
            .map(|h| h.photons())
            .collect::<Result<Vec<_>, _>>()?;
        Ok(grids[0]
            .iter()
            .enumerate()
            .map(|(i, p)| Bundle {
                e: p.direction,
                w: p.weight,
                m: std::array::from_fn(|k| grids[k][i].screen),
            })
            .collect())
    }
    fn stream(&mut self, l: &RayNode, r: &RayNode) -> Result<(), String> {
        self.b3.stream_centered(l, r)?;
        self.b4.stream_centered(l, r)?;
        HarmonicSky::stream_log_triplet(&mut self.logs, l, r)
    }
    fn collision_segment(
        &mut self,
        events: &[CollisionEvent],
        number: &mut f64,
        energy: &mut f64,
        count: &mut usize,
    ) -> Result<(), String> {
        if events.is_empty() {
            return Ok(());
        }
        let before = self.rays()?;
        let mut after = before.clone();
        apply_events(&mut after, events, number, energy, count)?;
        let [m0, m1, m2] = &mut self.logs;
        for (k, h) in [&mut self.b3, &mut self.b4, m0, m1, m2]
            .into_iter()
            .enumerate()
        {
            let b = before.iter().map(|r| r.photon(k)).collect::<Vec<_>>();
            let a = after.iter().map(|r| r.photon(k)).collect::<Vec<_>>();
            h.absorb_delta(&b, &a)?;
        }
        Ok(())
    }
}
/// Independent harmonic transport on the accepted geometry/bulk-velocity
/// schedule; all five collisions use a resolved normalized angular mesh.
/// Not the grid-free R116-A continuum collision, and not independent recoil.
pub fn replay_harmonic(
    records: &[StepRecord],
    l: usize,
    nt: usize,
    np: usize,
) -> Result<SpectralSky, String> {
    validate_records(records)?;
    let mut h = HarmonicMoments::new(l, nt, np)?;
    let mut history = vec![snapshot(&h.rays()?, 0.)?];
    let (mut number, mut energy, mut count) = (0., 0., 0);
    for r in records {
        h.collision_segment(&r.first, &mut number, &mut energy, &mut count)?;
        h.stream(&r.left, &r.right)?;
        h.collision_segment(&r.second, &mut number, &mut energy, &mut count)?;
        history.push(snapshot(&h.rays()?, r.right.eta)?);
    }
    Ok(SpectralSky {
        rays: h.rays()?,
        history,
        max_collision_number_defect: number,
        max_collision_rest_energy_defect: energy,
        coefficients: Some(h.fields().iter().map(|h| h.coefficients.clone()).collect()),
        collision_events: count,
    })
}
