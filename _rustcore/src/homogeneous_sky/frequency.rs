//! R118-B: frequency-resolved cold polarized transport on an accepted BASS
//! history. Lagrangian ray log-frequency grids, conservative number projection.
//! Finite-width prescribed true absorption/emission is NOT a resonant
//! redistribution or a population solver. No new feedback on the history.
//! x=h_P nu/(k_B T_emit); each ray's edges are log x = u + shift.
use super::{rec_bridge::material_expansion_factor, recoil::gain_map, replay::StepRecord, *};
use crate::kinetic::lie_hierarchy::lie_data;

#[path = "frequency_dual.rs"]
pub mod dual;
#[path = "frequency_projected.rs"]
mod projected;
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum FrequencyMethod {
    /// Resolve on the union partition, then project once per collision.
    UnionProjection,
    /// Project the generator and solve BE/SDIRK in finite-volume space.
    Projected,
}

const NORM3: f64 = 2.4041138063191885;
const NORM4: f64 =
    std::f64::consts::PI * std::f64::consts::PI * std::f64::consts::PI * std::f64::consts::PI / 15.;
const GX: [f64; 4] = [
    0.1834346424956498,
    0.5255324099163290,
    0.7966664774136267,
    0.9602898564975363,
];
const GW: [f64; 4] = [
    0.3626837833783620,
    0.3137066458778873,
    0.2223810344533745,
    0.1012285362903763,
];
fn integral(p: f64, a: f64, b: f64) -> f64 {
    (p * a).exp() * (p * (b - a)).exp_m1() / p
}
fn quad(a: f64, b: f64, f: impl Fn(f64) -> f64) -> f64 {
    let mid = 0.5 * (a + b);
    let h = 0.5 * (b - a);
    h * (0..4)
        .map(|i| GW[i] * (f(mid - h * GX[i]) + f(mid + h * GX[i])))
        .sum::<f64>()
}
fn planck(u: f64) -> f64 {
    let x = u.exp();
    if x > 700. {
        0.
    } else {
        1. / x.exp_m1()
    }
}
#[derive(Clone, Debug)]
pub struct FrequencyGrid {
    edges: Vec<f64>,
    w3: Vec<f64>,
    w4: Vec<f64>,
    initial: Vec<f64>,
}
impl FrequencyGrid {
    pub fn new(lo: f64, hi: f64, n: usize) -> Result<Self, String> {
        if !lo.is_finite()
            || !hi.is_finite()
            || lo < -40.
            || hi > 10.
            || hi <= lo
            || !(8..=8192).contains(&n)
        {
            return Err("frequency grid needs -40<=lo<hi<=10 and 8..8192 bins".into());
        }
        let edges = (0..=n)
            .map(|i| {
                if i == n {
                    hi
                } else {
                    lo + (hi - lo) * i as f64 / n as f64
                }
            })
            .collect::<Vec<_>>();
        let w3 = edges
            .windows(2)
            .map(|x| integral(3., x[0], x[1]))
            .collect::<Vec<_>>();
        let w4 = edges
            .windows(2)
            .map(|x| integral(4., x[0], x[1]))
            .collect::<Vec<_>>();
        if w3.iter().chain(&w4).any(|w| !w.is_finite() || *w <= 0.) {
            return Err("frequency cells have nonpositive or nonfinite integral".into());
        }
        let initial: Vec<f64> = edges
            .windows(2)
            .zip(&w3)
            .map(|(x, w)| quad(x[0], x[1], |u| (3. * u).exp() * planck(u)) / w)
            .collect();
        if initial.iter().any(|v| !v.is_finite() || *v < 0.) {
            return Err("invalid Planck projection".into());
        }
        Ok(Self {
            edges,
            w3,
            w4,
            initial,
        })
    }
    pub fn edges(&self) -> &[f64] {
        &self.edges
    }
    pub fn bins(&self) -> usize {
        self.w3.len()
    }
}
#[derive(Clone, Copy, Debug)]
pub struct VelocityNode {
    pub eta: f64,
    pub beta: [f64; 3],
}
#[derive(Clone, Copy, Debug)]
pub struct Line {
    center: f64,
    width: f64,
    strength: f64,
    source: f64,
}
impl Line {
    /// Gaussian normalized in d log(nu_material). strength is integrated
    /// material extinction in normal H units, so normal clock rate is D*strength*phi.
    /// source is an isotropic occupation number (not intensity or a population).
    pub fn new(center: f64, width: f64, strength: f64, source: f64) -> Result<Self, String> {
        if ![center, width, strength, source]
            .iter()
            .all(|v| v.is_finite())
            || width <= 0.
            || strength < 0.
            || source < 0.
            || width < 1e-9
            || width > 10.
            || strength > 1e8
            || source > 1e10
        {
            return Err("invalid/beyond-bounded-domain prescribed line".into());
        }
        Ok(Self {
            center,
            width,
            strength,
            source,
        })
    }
    fn profile(&self, z: f64) -> f64 {
        let x = (z - self.center) / self.width;
        (-0.5 * x * x).exp() / (self.width * (2. * PI).sqrt())
    }
    /// Positive profile quadrature, split at multiples of the line width.
    /// This computes the projected generator, not a projection of exp(-tau).
    fn profile_integrals(&self, a: f64, b: f64, shift: f64) -> (f64, f64) {
        if self.strength == 0. {
            return (0., 0.);
        }
        let c = self.center - shift;
        if self.profile(c.clamp(a, b) + shift) == 0. {
            return (0., 0.);
        }
        let mut l = a;
        let (mut q3, mut q4) = (0., 0.);
        let mut add = |l: f64, r: f64| {
            let m = 0.5 * (l + r);
            let h = 0.5 * (r - l);
            for i in 0..4 {
                for sign in [-1., 1.] {
                    let u = m + sign * h * GX[i];
                    let w = h * GW[i] * (3. * u).exp() * self.profile(u + shift);
                    q3 += w;
                    q4 += w * u.exp();
                }
            }
        };
        for i in -12..=12 {
            let r = c + i as f64 * self.width;
            if r > l && r < b {
                add(l, r);
                l = r;
            }
        }
        add(l, b);
        (q3, q4)
    }
}
#[derive(Clone, Debug)]
pub struct LineHistory {
    line: Line,
    velocity: Vec<VelocityNode>,
    substeps: usize,
}
impl LineHistory {
    pub fn new(line: Line, velocity: Vec<VelocityNode>, substeps: usize) -> Result<Self, String> {
        if velocity.len() < 2
            || velocity[0].eta != 0.
            || !(1..=1024).contains(&substeps)
            || velocity.iter().any(|v| {
                !v.eta.is_finite()
                    || !v.beta.iter().all(|x| x.is_finite())
                    || V::from(v.beta).norm_squared() >= 1.
            })
            || velocity.windows(2).any(|p| p[1].eta <= p[0].eta)
        {
            return Err("invalid line velocity schedule or quadrature subdivision".into());
        }
        Ok(Self {
            line,
            velocity,
            substeps,
        })
    }
    pub fn velocity_at(&self, eta: f64) -> Result<([f64; 3], [f64; 3]), String> {
        if !eta.is_finite()
            || eta < 0.
            || eta > self.velocity.last().unwrap().eta + 32. * f64::EPSILON * (1. + eta.abs())
        {
            return Err("line velocity history does not cover requested clock".into());
        }
        let i = self
            .velocity
            .partition_point(|v| v.eta <= eta)
            .saturating_sub(1)
            .min(self.velocity.len() - 2);
        let a = self.velocity[i];
        let b = self.velocity[i + 1];
        let h = b.eta - a.eta;
        let u = (eta - a.eta) / h;
        Ok((
            std::array::from_fn(|k| a.beta[k] + u * (b.beta[k] - a.beta[k])),
            std::array::from_fn(|k| (b.beta[k] - a.beta[k]) / h),
        ))
    }
}
#[derive(Clone, Debug)]
struct Ray {
    e: V,
    w: f64,
    shift: f64,
    f: Vec<M>,
    last_sign: i8,
    turned: bool,
}
impl Ray {
    fn new(p: &Photon, g: &FrequencyGrid) -> Self {
        Self {
            e: p.direction,
            w: p.weight,
            shift: 0.,
            f: g.initial.iter().map(|x| p.screen * *x).collect(),
            last_sign: 0,
            turned: false,
        }
    }
    fn geometric(&mut self, l: &RayNode, r: &RayNode) -> Result<(), String> {
        let s = advance_ray(l, r, self.e.into())?;
        let rot = M::from_fn(|i, j| s.rotation[i][j]);
        for f in &mut self.f {
            *f = rot * *f * rot.transpose();
        }
        self.e = V::from(s.e);
        self.w *= s.log_area.exp();
        self.shift += s.log_energy;
        if !self.w.is_finite() || self.w <= 0. || !self.shift.is_finite() {
            return Err("frequency characteristic overflow".into());
        }
        Ok(())
    }
    fn values(&self, g: &FrequencyGrid, eta: f64) -> (f64, f64) {
        let d = self.shift + eta;
        let n = self
            .f
            .iter()
            .zip(&g.w3)
            .map(|(x, w)| x.trace() * w)
            .sum::<f64>();
        let e = self
            .f
            .iter()
            .zip(&g.w4)
            .map(|(x, w)| x.trace() * w)
            .sum::<f64>();
        (
            self.w / (4. * PI) * n * (3. * d).exp() / NORM3,
            self.w / (4. * PI) * e * (4. * d).exp() / NORM4,
        )
    }
}
fn screen_min_rel(m: &M) -> Result<f64, String> {
    if !m.iter().all(|v| v.is_finite()) {
        return Err("nonfinite frequency coherency".into());
    }
    let scale = m.iter().map(|v| v.abs()).fold(0., f64::max);
    if scale == 0. {
        return Ok(0.);
    }
    let q = m / scale;
    let tr = q.trace();
    let disc = (2. * q.norm_squared() - tr * tr).max(0.).sqrt();
    Ok(0.5 * (tr - disc))
}
#[derive(Clone, Debug)]
pub struct FrequencySample {
    pub direction: [f64; 3],
    pub weight: f64,
    pub log_shift: f64,
    pub occupation: Vec<[[f64; 3]; 3]>,
}
#[derive(Clone, Debug, Default)]
pub struct FrequencySnapshot {
    pub eta: f64,
    pub number_centered: f64,
    pub energy_centered: f64,
    pub number_flux: [f64; 3],
    pub escaped_number_centered: f64,
    pub escaped_energy_centered: f64,
    pub line_number_centered: f64,
    pub line_normal_energy_centered: f64,
    pub line_material_energy_centered: f64,
    /// Projection defects in material energy on the normal hypersurface.
    pub line_projection_energy_centered: f64,
    pub thomson_projection_energy_centered: f64,
    pub line_normal_projection_energy_centered: f64,
    pub thomson_normal_energy_centered: f64,
    pub thomson_normal_projection_energy_centered: f64,
    pub geometric_energy_centered: f64,
    pub min_screen_relative: f64,
}
#[derive(Clone, Debug, Default)]
struct Audit {
    dual_second_moment: f64,
    escape_n: f64,
    escape_e: f64,
    line_n: f64,
    line_e: f64,
    line_material_e: f64,
    line_proj: f64,
    thomson_proj: f64,
    line_normal_proj: f64,
    thomson_normal: f64,
    thomson_normal_proj: f64,
    geom_energy: f64,
    max_number: f64,
    max_rest: f64,
    max_project: f64,
    max_line_n: f64,
    max_fv_residual: f64,
    max_fv_iterations: usize,
    events: usize,
    subcells: usize,
    line_cells: usize,
    min_drift: Option<f64>,
    max_drift: Option<f64>,
}
fn snapshot(
    rays: &[Ray],
    g: &FrequencyGrid,
    eta: f64,
    a: &Audit,
) -> Result<FrequencySnapshot, String> {
    let mut s = FrequencySnapshot {
        eta,
        escaped_number_centered: a.escape_n,
        escaped_energy_centered: a.escape_e,
        line_number_centered: a.line_n,
        line_normal_energy_centered: a.line_e,
        line_material_energy_centered: a.line_material_e,
        line_projection_energy_centered: a.line_proj,
        thomson_projection_energy_centered: a.thomson_proj,
        line_normal_projection_energy_centered: a.line_normal_proj,
        thomson_normal_energy_centered: a.thomson_normal,
        thomson_normal_projection_energy_centered: a.thomson_normal_proj,
        geometric_energy_centered: a.geom_energy,
        ..Default::default()
    };
    for r in rays {
        let (n, e) = r.values(g, eta);
        s.number_centered += n;
        s.energy_centered += e;
        for k in 0..3 {
            s.number_flux[k] += n * r.e[k];
        }
        for f in &r.f {
            s.min_screen_relative = s.min_screen_relative.min(screen_min_rel(f)?);
        }
    }
    if !s.number_centered.is_finite()
        || !s.energy_centered.is_finite()
        || s.min_screen_relative < -1e-10
    {
        return Err(format!(
            "invalid or non-PSD frequency snapshot: {}",
            s.min_screen_relative
        ));
    }
    Ok(s)
}

struct Terms {
    d: f64,
    area: f64,
    gp: M,
    lift: M,
    back: M,
    edges: Vec<f64>,
}
struct Stage {
    lu: nalgebra::linalg::LU<f64, nalgebra::Const<6>, nalgebra::Const<6>>,
    alpha: Vec<f64>,
    tr: Vec<f64>,
}
impl Stage {
    fn new(t: &[Terms], h: f64) -> Result<Self, String> {
        let mut lhs = SMatrix::<f64, 6, 6>::identity();
        let mut alpha = Vec::with_capacity(t.len());
        let mut tr = Vec::with_capacity(t.len());
        const P: [(usize, usize); 6] = [(0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2)];
        for r in t {
            let z = h * r.d;
            if !z.is_finite() {
                return Err("frequency collision depth overflow".into());
            }
            let a = z / (1. + z);
            alpha.push(a);
            tr.push(1. / (1. + z));
            for (i, &(x, y)) in P.iter().enumerate() {
                for (j, &(u, v)) in P.iter().enumerate() {
                    let q = r.gp[(x, u)] * r.gp[(y, v)]
                        + if u == v {
                            0.
                        } else {
                            r.gp[(x, v)] * r.gp[(y, u)]
                        };
                    lhs[(i, j)] -= r.area * a * GAIN * q;
                }
            }
        }
        Ok(Self {
            lu: lhs.lu(),
            alpha,
            tr,
        })
    }
    fn solve(&self, t: &[Terms], input: &[M], out: &mut [M]) -> Result<(), String> {
        let mut rhs = M::zeros();
        for (i, r) in t.iter().enumerate() {
            rhs += r.area * self.tr[i] * input[i];
        }
        let src = unpack(
            self.lu
                .solve(&pack(rhs))
                .ok_or("singular frequency Thomson source")?,
        );
        for (i, r) in t.iter().enumerate() {
            out[i] = self.tr[i] * input[i] + (self.alpha[i] * GAIN) * r.gp * src * r.gp.transpose();
        }
        Ok(())
    }
}
fn collide_once(
    rays: &mut [Ray],
    g: &FrequencyGrid,
    eta: f64,
    beta: V,
    depth: f64,
    scheme: CollisionScheme,
    a: &mut Audit,
) -> Result<(), String> {
    let ph = rays
        .iter()
        .map(|r| Photon {
            direction: r.e,
            weight: r.w,
            screen: projector(&r.e) * 0.5,
        })
        .collect::<Vec<_>>();
    let map = gain_map(&ph, beta)?;
    let mut t = Vec::with_capacity(rays.len());
    let mut union = Vec::with_capacity(rays.len() * (g.bins() + 1));
    let mut n0 = 0.;
    let mut e0 = 0.;
    let mut normal_e0 = 0.;
    for r in rays.iter() {
        let (e, j, d) = boost(r.e, beta)?;
        let (_, inv, _) = boost(e, -beta)?;
        let edges = g
            .edges
            .iter()
            .map(|u| u + r.shift + d.ln() + eta)
            .collect::<Vec<_>>();
        union.extend_from_slice(&edges);
        let (n, en) = r.values(g, eta);
        n0 += n;
        e0 += d * en;
        normal_e0 += en;
        t.push(Terms {
            d,
            area: r.w / (d * d),
            gp: projector(&e) * map,
            lift: j,
            back: inv,
            edges,
        });
    }
    union.sort_by(f64::total_cmp);
    union.dedup();
    let st = Stage::new(
        &t,
        depth
            * if scheme == CollisionScheme::Sdirk2 {
                SDIRK_GAMMA
            } else {
                1.
            },
    )?;
    let nr = rays.len();
    let nf = g.bins();
    let rest: Vec<Vec<M>> = rays
        .iter()
        .zip(&t)
        .map(|(r, t)| {
            r.f.iter()
                .map(|f| t.lift * *f * t.lift.transpose())
                .collect()
        })
        .collect();
    let mut result = vec![vec![M::zeros(); nf]; nr];
    let mut index = vec![0usize; nr];
    let mut active = vec![None; nr];
    let mut inp = vec![M::zeros(); nr];
    let mut mid = inp.clone();
    let mut out = inp.clone();
    let mut q = inp.clone();
    let mut esc_n = 0.;
    let mut esc_e = 0.;
    let mut esc_rest = 0.;
    let mut raw_rest = 0.;
    let mut raw_normal = 0.;
    // Exact common material-frequency partition of every moving normal mesh.
    // z is centered by +eta solely to keep weights well scaled.
    for u in union.windows(2) {
        let (l, r) = (u[0], u[1]);
        if r <= l {
            continue;
        }
        let w3 = integral(3., l, r);
        let w4 = integral(4., l, r);
        for i in 0..nr {
            let e = &t[i].edges;
            while index[i] < nf && e[index[i] + 1] <= l {
                index[i] += 1;
            }
            active[i] = if index[i] < nf && e[index[i]] <= l {
                Some(index[i])
            } else {
                None
            };
            inp[i] = active[i].map_or(M::zeros(), |j| rest[i][j]);
        }
        st.solve(&t, &inp, &mut mid)?;
        if scheme == CollisionScheme::Sdirk2 {
            for i in 0..nr {
                q[i] = inp[i] + (1. + SQRT_2) * (mid[i] - inp[i]);
            }
            st.solve(&t, &q, &mut out)?;
        } else {
            out.copy_from_slice(&mid);
        }
        for i in 0..nr {
            let tr = out[i].trace();
            if screen_min_rel(&out[i])? < -1e-10 {
                return Err("non-PSD frequency Thomson subinterval".into());
            }
            let w = rays[i].w / (4. * PI * t[i].d.powi(3));
            let delta = w * w4 * (tr - inp[i].trace()) / NORM4;
            raw_rest += delta;
            raw_normal += delta / t[i].d;
            if let Some(j) = active[i] {
                let edges = &t[i].edges;
                let f = w3 / integral(3., edges[j], edges[j + 1]);
                result[i][j] += f * t[i].back * out[i] * t[i].back.transpose();
            } else {
                esc_n += w * w3 * tr / NORM3;
                esc_rest += w * w4 * tr / NORM4;
                esc_e += w * w4 * tr / (NORM4 * t[i].d);
            }
        }
    }
    let mut n1 = 0.;
    let mut e1 = 0.;
    let mut normal_e1 = 0.;
    for (i, (r, f)) in rays.iter_mut().zip(result).enumerate() {
        r.f = f;
        let (n, e) = r.values(g, eta);
        n1 += n;
        e1 += t[i].d * e;
        normal_e1 += e;
    }
    let nd = (n1 - n0 + esc_n).abs() / n0.max(f64::MIN_POSITIVE);
    let ed = raw_rest.abs() / e0.max(f64::MIN_POSITIVE);
    let proj = e1 - e0 + esc_rest - raw_rest;
    if ![nd, ed, proj, esc_n, esc_e].iter().all(|v| v.is_finite()) {
        return Err("nonfinite frequency collision ledger".into());
    }
    a.escape_n += esc_n;
    a.escape_e += esc_e;
    a.max_number = a.max_number.max(nd);
    a.max_rest = a.max_rest.max(ed);
    a.max_project = a.max_project.max(proj.abs() / e0.max(f64::MIN_POSITIVE));
    a.thomson_proj += proj;
    a.thomson_normal += raw_normal;
    a.thomson_normal_proj += normal_e1 - normal_e0 + esc_e - raw_normal;
    a.subcells += 1;
    Ok(())
}
fn events(
    rays: &mut [Ray],
    g: &FrequencyGrid,
    eta: f64,
    evs: &[CollisionEvent],
    a: &mut Audit,
    method: FrequencyMethod,
) -> Result<(), String> {
    for ev in evs {
        let b = V::from(ev.beta);
        validate_cell(ev.depth, &b)?;
        if ev.depth == 0. {
            continue;
        }
        a.events += 1;
        // Sufficient positivity condition: 1-(1+sqrt2)*alpha >= 0 in
        // stage-2 input. Use a conservative max depth*D<=1 per spectral cell.
        let max_d = (1. + b.norm()) / (1. - b.norm_squared()).sqrt();
        let count = if ev.scheme == CollisionScheme::Sdirk2 || method == FrequencyMethod::Projected
        {
            (ev.depth * max_d).ceil().max(1.) as usize
        } else {
            1
        };
        if count > 256 {
            return Err("frequency event requires >256 depth subcells".into());
        }
        for _ in 0..count {
            match method {
                FrequencyMethod::UnionProjection => {
                    collide_once(rays, g, eta, b, ev.depth / count as f64, ev.scheme, a)?
                }
                FrequencyMethod::Projected => projected::projected_once(
                    rays,
                    g,
                    eta,
                    b,
                    ev.depth / count as f64,
                    ev.scheme,
                    a,
                )?,
            }
        }
    }
    Ok(())
}

fn interpolate(l: &RayNode, r: &RayNode, t: f64) -> RayNode {
    if t == l.eta {
        return l.clone();
    }
    if t == r.eta {
        return r.clone();
    }
    let a = lie_data(l).lerp(&lie_data(r), (t - l.eta) / (r.eta - l.eta));
    RayNode {
        eta: t,
        shear: a.shear,
        n: a.n,
        a: a.a,
        rotation: a.rotation,
        ..l.clone()
    }
}
fn line_cell(
    rays: &mut [Ray],
    g: &FrequencyGrid,
    node: &RayNode,
    h: f64,
    line: &LineHistory,
    a: &mut Audit,
) -> Result<(), String> {
    let (beta, beta_prime) = line.velocity_at(node.eta)?;
    let b = V::from(beta);
    let mut n0 = 0.;
    let mut n1 = 0.;
    let mut dn = 0.;
    let mut de = 0.;
    let mut dm = 0.;
    let mut projected = 0.;
    let mut normal_projected = 0.;
    for r in rays.iter_mut() {
        let (_, _, d) = boost(r.e, b)?;
        let drift = -d * material_expansion_factor(node, r.e.into(), beta, beta_prime)?;
        a.min_drift = Some(a.min_drift.map_or(drift, |v| v.min(drift)));
        a.max_drift = Some(a.max_drift.map_or(drift, |v| v.max(drift)));
        let sign = if drift > 0. {
            1
        } else if drift < 0. {
            -1
        } else {
            0
        };
        if sign != 0 {
            if r.last_sign != 0 && sign != r.last_sign {
                r.turned = true;
            }
            r.last_sign = sign;
        }
        let (n, _) = r.values(g, node.eta);
        n0 += n;
        let w = r.w / (4. * PI);
        let s = r.shift + node.eta;
        let nweight = w * (3. * s).exp() / NORM3;
        let eweight = w * (4. * s).exp() / NORM4;
        let material_shift = r.shift + d.ln();
        let src = projector(&r.e) * (0.5 * line.line.source);
        for j in 0..g.bins() {
            let (l, u) = (g.edges[j], g.edges[j + 1]);
            let (i3, i4) = line.line.profile_integrals(l, u, material_shift);
            if i3 == 0. {
                continue;
            }
            let tau = h * d * line.line.strength * (i3 / g.w3[j]);
            let alpha = -(-tau).exp_m1();
            let w3 = g.w3[j] * alpha;
            // Time-integrated raw energy source from constant occupation
            // within this finite-volume bin: ratio of profile moments.
            let w4 = w3 * (i4 / i3);
            if !alpha.is_finite() || !(0. ..=1.).contains(&alpha) {
                return Err(format!(
                    "line transmission quadrature outside unit interval: {alpha}"
                ));
            }
            let old = r.f[j];
            let change = src - old;
            dn += nweight * w3 * change.trace();
            let de_raw = eweight * w4 * change.trace();
            de += de_raw;
            dm += d * de_raw;
            r.f[j] = (1. - alpha) * old + alpha * src;
            let delta = eweight * g.w4[j] * (r.f[j] - old).trace() - de_raw;
            projected += d * delta;
            normal_projected += delta;
        }
        n1 += r.values(g, node.eta).0;
    }
    a.max_line_n = a
        .max_line_n
        .max((n1 - n0 - dn).abs() / n0.max(f64::MIN_POSITIVE));
    a.line_n += dn;
    a.line_e += de;
    a.line_material_e += dm;
    a.line_proj += projected;
    a.line_normal_proj += normal_projected;
    a.line_cells += 1;
    Ok(())
}
fn geometric_all(
    rays: &mut [Ray],
    g: &FrequencyGrid,
    l: &RayNode,
    r: &RayNode,
    a: &mut Audit,
) -> Result<(), String> {
    // Discrete geometric work, measured on the same centered energy scale.
    // Not an independent physical energy-conservation test.
    for ray in rays {
        let before = ray.values(g, l.eta).1;
        ray.geometric(l, r)?;
        a.geom_energy += ray.values(g, r.eta).1 - before;
    }
    Ok(())
}
fn geometry(
    rays: &mut [Ray],
    g: &FrequencyGrid,
    l: &RayNode,
    r: &RayNode,
    line: Option<&LineHistory>,
    a: &mut Audit,
) -> Result<(), String> {
    if let Some(line) = line {
        let h = r.eta - l.eta;
        let mut times = (0..=line.substeps)
            .map(|i| {
                if i == line.substeps {
                    r.eta
                } else {
                    l.eta + h * i as f64 / line.substeps as f64
                }
            })
            .collect::<Vec<_>>();
        // A derivative discontinuity at a supplied velocity knot is an exact
        // splitting boundary, not averaged through a midpoint.
        times.extend(
            line.velocity
                .iter()
                .filter(|v| v.eta > l.eta && v.eta < r.eta)
                .map(|v| v.eta),
        );
        times.sort_by(f64::total_cmp);
        times.dedup();
        for t in times.windows(2) {
            let left = interpolate(l, r, t[0]);
            let right = interpolate(l, r, t[1]);
            let middle = interpolate(l, r, 0.5 * (t[0] + t[1]));
            geometric_all(rays, g, &left, &middle, a)?;
            line_cell(rays, g, &middle, t[1] - t[0], line, a)?;
            geometric_all(rays, g, &middle, &right, a)?;
        }
    } else {
        geometric_all(rays, g, l, r, a)?;
    }
    Ok(())
}
pub struct FrequencySky {
    rays: Vec<Ray>,
    pub history: Vec<FrequencySnapshot>,
    pub max_number_defect: f64,
    pub max_material_energy_defect: f64,
    pub max_projection_energy_defect: f64,
    pub max_line_number_defect: f64,
    pub max_fv_stage_residual: f64,
    pub max_fv_stage_iterations: usize,
    pub min_drift: Option<f64>,
    pub max_drift: Option<f64>,
    pub turning_rays: usize,
    pub collision_events: usize,
    pub collision_subcells: usize,
    pub line_cells: usize,
}
impl FrequencySky {
    /// Discrete signed centered normal energy ledger. The projection and
    /// geometric work terms are numerical bookkeeping, not physical heating.
    pub fn normal_energy_balance_defect(&self) -> f64 {
        let a = &self.history[0];
        let b = self.history.last().unwrap();
        b.energy_centered - a.energy_centered + b.escaped_energy_centered
            - b.geometric_energy_centered
            - b.thomson_normal_energy_centered
            - b.thomson_normal_projection_energy_centered
            - b.line_normal_energy_centered
            - b.line_normal_projection_energy_centered
    }
    /// Centered normal-frame number continuity on the accepted clock,
    /// including explicitly escaped and line-created/destroyed photons.
    /// The Class-B flux integral is trapezoidal (not a discrete identity).
    pub fn number_continuity_defect(&self, records: &[StepRecord]) -> Result<f64, String> {
        if self.history.len() != records.len() + 1 {
            return Err("frequency history length mismatch".into());
        }
        let mut flux = 0.;
        for (r, s) in records.iter().zip(self.history.windows(2)) {
            if r.left.eta != s[0].eta || r.right.eta != s[1].eta {
                return Err("frequency history clock mismatch".into());
            }
            let rhs = |n: &RayNode, q: &FrequencySnapshot| {
                n.a.iter()
                    .zip(q.number_flux)
                    .map(|(a, f)| a * f)
                    .sum::<f64>()
            };
            flux += (r.right.eta - r.left.eta) * (rhs(&r.left, &s[0]) + rhs(&r.right, &s[1]));
        }
        let first = &self.history[0];
        let last = self.history.last().unwrap();
        Ok(
            last.number_centered - first.number_centered + last.escaped_number_centered
                - last.line_number_centered
                - flux,
        )
    }
    pub fn samples(&self) -> Vec<FrequencySample> {
        self.rays
            .iter()
            .map(|r| FrequencySample {
                direction: r.e.into(),
                weight: r.w,
                log_shift: r.shift,
                occupation: r.f.iter().map(rows).collect(),
            })
            .collect()
    }
    /// Boost occupation invariantly, shifting its log-frequency grid and
    /// changing solid angle; no frequency resampling in the observer frame.
    pub fn observer_samples(&self, beta: [f64; 3]) -> Result<Vec<FrequencySample>, String> {
        let b = V::from(beta);
        self.rays
            .iter()
            .map(|r| {
                let (e, j, d) = boost(r.e, b)?;
                Ok(FrequencySample {
                    direction: e.into(),
                    weight: r.w / (d * d),
                    log_shift: r.shift + d.ln(),
                    occupation: r
                        .f
                        .iter()
                        .map(|f| rows(&(j * *f * j.transpose())))
                        .collect(),
                })
            })
            .collect()
    }
}
pub fn replay_frequency(
    records: &[StepRecord],
    nmu: usize,
    nphi: usize,
    g: &FrequencyGrid,
    line: Option<&LineHistory>,
) -> Result<FrequencySky, String> {
    replay_frequency_with_method(
        records,
        nmu,
        nphi,
        g,
        line,
        FrequencyMethod::UnionProjection,
    )
}
pub fn replay_frequency_with_method(
    records: &[StepRecord],
    nmu: usize,
    nphi: usize,
    g: &FrequencyGrid,
    line: Option<&LineHistory>,
    method: FrequencyMethod,
) -> Result<FrequencySky, String> {
    if records.is_empty() || records[0].left.eta != 0. {
        return Err("frequency replay requires an accepted history starting at emission".into());
    }
    if nmu
        .checked_mul(nphi)
        .is_none_or(|n| n > 4096 || n.checked_mul(g.bins()).is_none_or(|q| q > 4_000_000))
    {
        return Err("frequency ray mesh exceeds bounded allocation".into());
    }
    for (i, r) in records.iter().enumerate() {
        lie_data(&r.left).validate()?;
        lie_data(&r.right).validate()?;
        if !r.left.eta.is_finite()
            || !r.right.eta.is_finite()
            || r.right.eta <= r.left.eta
            || (i > 0
                && (records[i - 1].right.eta != r.left.eta
                    || lie_data(&records[i - 1].right) != lie_data(&r.left)))
        {
            return Err("discontinuous frequency replay geometry or clock".into());
        }
    }
    if let Some(l) = line {
        l.velocity_at(records.last().unwrap().right.eta)?;
    }
    let mut rays = initial_sky(nmu, nphi)?
        .iter()
        .map(|p| Ray::new(p, g))
        .collect::<Vec<_>>();
    let mut a = Audit::default();
    let mut history = vec![snapshot(&rays, g, 0., &a)?];
    for r in records {
        events(&mut rays, g, r.left.eta, &r.first, &mut a, method)?;
        geometry(&mut rays, g, &r.left, &r.right, line, &mut a)?;
        events(&mut rays, g, r.right.eta, &r.second, &mut a, method)?;
        history.push(snapshot(&rays, g, r.right.eta, &a)?);
    }
    let turning_rays = rays.iter().filter(|r| r.turned).count();
    Ok(FrequencySky {
        rays,
        history,
        max_number_defect: a.max_number,
        max_material_energy_defect: a.max_rest,
        max_projection_energy_defect: a.max_project,
        max_line_number_defect: a.max_line_n,
        max_fv_stage_residual: a.max_fv_residual,
        max_fv_stage_iterations: a.max_fv_iterations,
        min_drift: a.min_drift,
        max_drift: a.max_drift,
        turning_rays,
        collision_events: a.events,
        collision_subcells: a.subcells,
        line_cells: a.line_cells,
    })
}
