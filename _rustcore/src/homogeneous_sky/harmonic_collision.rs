//! Grid-free cold, elastic, finite-bulk-tilt bolometric Thomson cells.
//! R115/R116: continuum implicit stage with a padded spectral resolvent,
//! not the resolvent of the projected collision generator. No angular
//! synthesis or quadrature in this module. All coefficients use the
//! propagation dyad and the same spin convention as spin_sht.
use super::{rows, CollisionEvent, CollisionScheme, GAIN, M, SDIRK_GAMMA, V};
use crate::geom::lie::{constant_coefficients, linear_coefficients, quadratic_coefficients};
use crate::kinetic::sky_spectrum::normalized_wigner_d_table;
use crate::kinetic::spin_sht::{index, modes, C64};
use crate::kinetic::wigner::{gaunt, LogFactorial};
use nalgebra::{Matrix3, SMatrix, SVector, Vector3};
use std::f64::consts::SQRT_2;

const INV_TOL: f64 = 1e-10;
const CG_TOL: f64 = 2e-14;
const SPINS: [i64; 3] = [0, 2, -2];
type CV = Vector3<C64>;
type CM = Matrix3<C64>;
type Six = SVector<f64, 6>;
type Flat = Vec<C64>;
type SixMatrix = SMatrix<f64, 6, 6>;

#[derive(Debug, Clone, Default)]
pub struct CellDiagnostics {
    /// Max residual/(lower spectral bound * norm(solution)), including l=W+1
    /// residual, of each individual inverse multiplication. Not a bound on
    /// the complete collision or source solve, which also accumulates errors.
    pub max_inverse_relative_bound: f64,
    /// Condition estimate (Frobenius) of six-dimensional source system.
    pub source_condition: f64,
    pub source_relative_residual: f64,
    pub work_lmax: usize,
}

fn dot(x: &[C64], y: &[C64]) -> f64 {
    x.iter().zip(y).map(|(a, b)| (a.conj() * b).re).sum()
}
fn norm(x: &[C64]) -> f64 {
    dot(x, x).sqrt()
}
fn basis(k: usize) -> M {
    let mut s = M::zeros();
    let (i, j) = [(0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2)][k];
    if i == j {
        s[(i, j)] = 1.;
    } else {
        s[(i, j)] = 1. / SQRT_2;
        s[(j, i)] = 1. / SQRT_2;
    }
    s
}
fn physical(v: &Six) -> M {
    (0..6).fold(M::zeros(), |acc, k| acc + v[k] * basis(k))
}

/// Coefficients of M^*S = D² J^T S J on the normal transverse screen.
/// D J m_+ = K_+ m_+, K_+ = gamma I - i gamma [beta x] - k beta beta^T,
/// where m_+=e_theta+i e_phi. K is constant on the sphere.
/// Scalar trace: m_+^T K_+^T S K_- m_-; spin+2: m_+^T K_+^T S K_+ m_+.
/// Scalar lies in l<=2, spin+/-2 exactly in l=2.
fn adjoint_low(beta: V, s: M) -> [Vec<C64>; 3] {
    let g = 1. / (1. - beta.norm_squared()).sqrt();
    let k = g * g / (1. + g);
    let cross = M::new(
        0., -beta.z, beta.y, beta.z, 0., -beta.x, -beta.y, beta.x, 0.,
    );
    let kp = CM::from_fn(|i, j| {
        C64::new(
            g * if i == j { 1. } else { 0. } - k * beta[i] * beta[j],
            -g * cross[(i, j)],
        )
    });
    let sm = s.map(|v| C64::new(v, 0.));
    let l = kp.transpose() * sm * kp.conjugate();
    let lp = kp.transpose() * sm * kp;
    let real = M::from_fn(|i, j| 0.5 * (l[(i, j)].re + l[(j, i)].re));
    let quad = quadratic_coefficients(&rows(&real));
    let lin = linear_coefficients(&[
        (l[(1, 2)] - l[(2, 1)]).im,
        (l[(2, 0)] - l[(0, 2)]).im,
        (l[(0, 1)] - l[(1, 0)]).im,
    ]);
    let constant = constant_coefficients(real.trace());
    let a0 = (0..9).map(|i| constant[i] - quad[i] + lin[i]).collect();
    let mut ap = vec![C64::new(0., 0.); 9];
    let mut am = ap.clone();
    // At mu=0, m_+(phi) has exactly these three Fourier coefficients.
    // Product has spin+2, l=2 only, so divide the finite convolution
    // by the nonzero normalized Wigner column at the equator. This
    // is algebraic coefficient extraction, not spherical quadrature.
    let v = [
        CV::new(C64::new(0.5, 0.), C64::new(0., 0.5), C64::new(0., 0.)),
        CV::new(C64::new(0., 0.), C64::new(0., 0.), C64::new(-1., 0.)),
        CV::new(C64::new(-0.5, 0.), C64::new(0., 0.5), C64::new(0., 0.)),
    ];
    let pos = normalized_wigner_d_table(0., -2, 2);
    let neg = normalized_wigner_d_table(0., 2, 2);
    for m in -2i64..=2 {
        let mut coeff = C64::new(0., 0.);
        for j in -1i64..=1 {
            let p = m - j;
            if p.abs() <= 1 {
                coeff += (v[(j + 1) as usize].transpose() * lp * v[(p + 1) as usize])[(0, 0)];
            }
        }
        let sign = if m.rem_euclid(2) == 0 { 1. } else { -1. };
        let lam = if m >= 0 {
            pos[3 + m as usize]
        } else {
            sign * neg[3 + (-m) as usize]
        };
        ap[index(2, m)] = coeff / lam;
        am[index(2, -m)] = ap[index(2, m)].conj() * sign;
    }
    [a0, ap, am]
}

struct Multiplication {
    n: usize,
    active: usize,
    entries: Vec<(usize, usize, C64)>,
    speed: f64,
}
impl Multiplication {
    fn new(w: usize, beta: V) -> Self {
        // Include l=W+1 to evaluate the full residual of a padded solve.
        let n = modes(w + 1);
        let active = modes(w);
        let lf = LogFactorial::new(2 * w + 12);
        let lin = linear_coefficients(&beta.into());
        let mut entries = Vec::new();
        for (slot, &s) in SPINS.iter().enumerate() {
            for l in s.unsigned_abs() as usize..=w + 1 {
                for m in -(l as i64)..=l as i64 {
                    for big_m in -1i64..=1 {
                        let coef = lin[index(1, big_m)];
                        if coef.norm_sqr() == 0. {
                            continue;
                        }
                        for lp in
                            l.saturating_sub(1).max(s.unsigned_abs() as usize)..=(l + 1).min(w)
                        {
                            let mp = m - big_m;
                            if mp.abs() > lp as i64 {
                                continue;
                            }
                            let c = coef * gaunt(&lf, s, l as i64, m, 1, big_m, lp as i64).g;
                            if c.norm_sqr() > 0. {
                                entries.push((slot * n + index(l, m), slot * n + index(lp, mp), c));
                            }
                        }
                    }
                }
            }
        }
        Self {
            n,
            active,
            entries,
            speed: beta.norm(),
        }
    }
    /// Apply I - t beta.e, keeping outer row for continuum residual.
    fn apply(&self, x: &[C64], t: f64, out: &mut [C64], outer: bool) {
        out.copy_from_slice(x);
        for &(i, j, c) in &self.entries {
            out[i] -= t * c * x[j];
        }
        if !outer {
            for s in 0..3 {
                out[s * self.n + self.active..(s + 1) * self.n].fill(C64::new(0., 0.));
            }
        }
    }
    fn embed(&self, a: &[Vec<C64>]) -> Flat {
        let mut x = vec![C64::new(0., 0.); 3 * self.n];
        for s in 0..3 {
            x[s * self.n..s * self.n + a[s].len()].copy_from_slice(&a[s]);
        }
        x
    }
    fn project(&self, a: &[C64], l: usize) -> Vec<Vec<C64>> {
        (0..3)
            .map(|s| a[s * self.n..s * self.n + modes(l)].to_vec())
            .collect()
    }
    /// Solve (a I - a t beta.e)x = rhs with positive spectrum. CG on
    /// padded harmonic space; check true continuum residual including l=W+1.
    fn inverse(
        &self,
        rhs: &[C64],
        a: f64,
        t: f64,
        diag: &mut CellDiagnostics,
    ) -> Result<Flat, String> {
        if !a.is_finite() || a <= 0. || !(0.0..=1.0).contains(&t) {
            return Err("invalid rational multiplier".into());
        }
        let b: Flat = rhs.iter().map(|z| z / a).collect();
        let bn = norm(&b);
        if !bn.is_finite() {
            return Err("nonfinite rational RHS".into());
        }
        if bn == 0. {
            return Ok(b);
        }
        if t == 0. || self.speed == 0. {
            return Ok(b);
        }
        let mut x = vec![C64::new(0., 0.); b.len()];
        let mut r = b.clone();
        let mut p = r.clone();
        let mut ap = x.clone();
        let mut rr = dot(&r, &r);
        for _ in 0..512 {
            self.apply(&p, t, &mut ap, false);
            let den = dot(&p, &ap);
            if !den.is_finite() || den <= 0. {
                return Err("nonpositive CG denominator".into());
            }
            let alpha = rr / den;
            for i in 0..x.len() {
                x[i] += alpha * p[i];
                r[i] -= alpha * ap[i];
            }
            let next = dot(&r, &r);
            if next.sqrt() <= CG_TOL * bn {
                break;
            }
            if !next.is_finite() {
                return Err("nonfinite CG residual".into());
            }
            let ratio = next / rr;
            for i in 0..p.len() {
                p[i] = r[i] + ratio * p[i];
            }
            rr = next;
        }
        self.apply(&x, t, &mut ap, true);
        for i in 0..ap.len() {
            ap[i] -= b[i];
        }
        let bound = norm(&ap) / ((1. - t * self.speed) * norm(&x));
        if !bound.is_finite() || bound > INV_TOL {
            return Err(format!("rational multiplier unresolved: relative inverse bound {bound:e}; increase work_lmax"));
        }
        diag.max_inverse_relative_bound = diag.max_inverse_relative_bound.max(bound);
        Ok(x)
    }
}

fn source(m: &Multiplication, w: &[Flat], f: &[C64]) -> Six {
    // Frobenius on real screen matrices is half the intensity product
    // plus one quarter for each of the two signed spin products.
    Six::from_fn(|k, _| {
        let mut v = 0.;
        for s in 0..3 {
            let a = s * m.n;
            v += if s == 0 { 0.5 } else { 0.25 } * dot(&w[k][a..a + 9], &f[a..a + 9]);
        }
        v
    })
}

/// Solve one continuum BE or SDIRK2 cell and project only its final output.
/// Input is a real polarized field with exactly three signed-spin slots.
/// The caller owns positivity validation of the projected field and recoil.
/// No silent clipping or quadrature fallback is used. Work band is explicit
/// and each inverse is rejected if its continuum residual is unresolved.
pub fn continuum_cell(
    coefficients: &[Vec<C64>],
    lmax: usize,
    work_lmax: usize,
    beta: [f64; 3],
    depth: f64,
    scheme: CollisionScheme,
) -> Result<(Vec<Vec<C64>>, CollisionEvent, CellDiagnostics), String> {
    let b = V::from(beta);
    super::validate_cell(depth, &b)?;
    if lmax < 2
        || work_lmax < lmax
        || work_lmax > 256
        || coefficients.len() != 3
        || coefficients.iter().any(|a| {
            a.len() != modes(lmax) || a.iter().any(|x| !x.re.is_finite() || !x.im.is_finite())
        })
    {
        return Err("invalid continuum collision band or coefficients".into());
    }
    // The source is real symmetric; accepting arbitrary complex spin
    // fields would silently discard an unphysical imaginary source.
    let amplitude = coefficients
        .iter()
        .flatten()
        .map(|z| z.norm())
        .fold(0., f64::max);
    let tol = 1e-11 * amplitude;
    for l in 0..=lmax {
        for m in -(l as i64)..=l as i64 {
            let i = index(l, m);
            let j = index(l, -m);
            let parity = if m.rem_euclid(2) == 0 { 1. } else { -1. };
            if (coefficients[0][i] - parity * coefficients[0][j].conj()).norm() > tol
                || (coefficients[1][i] - parity * coefficients[2][j].conj()).norm() > tol
                || (l < 2 && (coefficients[1][i].norm() > tol || coefficients[2][i].norm() > tol))
            {
                return Err("nonphysical signed harmonic reality or spin slots".into());
            }
        }
    }
    let mut event = CollisionEvent {
        depth,
        beta,
        gain_map: None,
        scheme,
        sources: Vec::new(),
    };
    let mut diag = CellDiagnostics {
        work_lmax,
        ..Default::default()
    };
    if depth == 0. {
        return Ok((coefficients.to_vec(), event, diag));
    }
    let mul = Multiplication::new(work_lmax, b);
    let g = 1. / (1. - b.norm_squared()).sqrt();
    let w: Vec<_> = (0..6)
        .map(|k| mul.embed(&adjoint_low(b, basis(k))))
        .collect();
    let mut rg = Vec::with_capacity(6);
    let d = if scheme == CollisionScheme::Sdirk2 {
        depth * SDIRK_GAMMA
    } else {
        depth
    };
    let a = 1. + d * g;
    let t = d * g / a;
    for v in &w {
        let mut x = v.clone();
        for _ in 0..5 {
            x = mul.inverse(&x, g, 1., &mut diag)?;
        }
        x.iter_mut().for_each(|z| *z *= GAIN);
        rg.push(mul.inverse(&x, a, t, &mut diag)?);
    }
    let mut lhs = SixMatrix::identity();
    for j in 0..6 {
        lhs.set_column(
            j,
            &(lhs.column(j).into_owned() - d * source(&mul, &w, &rg[j])),
        );
    }
    let inv = lhs.try_inverse().ok_or("singular continuum gain source")?;
    diag.source_condition = lhs.norm() * inv.norm();
    if !diag.source_condition.is_finite() || diag.source_condition * f64::EPSILON > 1e-8 {
        return Err("ill-conditioned continuum gain source; subdivide depth".into());
    }
    let f0 = mul.embed(coefficients);
    let mut stage = |f: &[C64]| -> Result<(Flat, M), String> {
        let mut out = mul.inverse(f, a, t, &mut diag)?;
        let rhs = source(&mul, &w, &out);
        let s = inv * rhs;
        let residual = (lhs * s - rhs).norm() / rhs.norm().max(f64::MIN_POSITIVE);
        if !residual.is_finite() || residual > 1e-10 {
            return Err("unresolved continuum source solve".into());
        }
        diag.source_relative_residual = diag.source_relative_residual.max(residual);
        if d * g <= 1. {
            // Rf - f = -d D Rf in the continuum. Form the small
            // increment directly rather than overwrite the O(1) monopole
            // with two nearly equal floating-point quantities.
            let mut loss = vec![C64::new(0., 0.); out.len()];
            mul.apply(&out, 1., &mut loss, false);
            for i in 0..out.len() {
                let gain = (0..6).fold(C64::new(0., 0.), |acc, j| acc + s[j] * rg[j][i]);
                out[i] = f[i] + d * (gain - g * loss[i]);
            }
        } else {
            for j in 0..6 {
                for (z, c) in out.iter_mut().zip(&rg[j]) {
                    *z += d * s[j] * c;
                }
            }
        }
        if out.iter().any(|z| !z.re.is_finite() || !z.im.is_finite()) {
            return Err("nonfinite continuum cell".into());
        }
        Ok((out, physical(&s)))
    };
    let (f1, s1) = stage(&f0)?;
    event.sources.push(rows(&s1));
    let out = if scheme == CollisionScheme::Sdirk2 {
        let z: Flat = f0
            .iter()
            .zip(f1)
            .map(|(a, b)| a + (1. + SQRT_2) * (b - a))
            .collect();
        let (f2, s2) = stage(&z)?;
        event.sources.push(rows(&s2));
        f2
    } else {
        f1
    };
    Ok((mul.project(&out, lmax), event, diag))
}

/// Energy and momentum change from the signed scalar monopole/dipole.
/// These are not quadrature sums. The normalization is the same as
/// HarmonicSky::moments (propagation rather than outward-sky direction).
fn exchange(before: &[C64], after: &[C64], scale: f64) -> (f64, V) {
    let pi = std::f64::consts::PI;
    let a0 = after[0] - before[0];
    let a10 = after[index(1, 0)] - before[index(1, 0)];
    let a11 = after[index(1, 1)] - before[index(1, 1)];
    let c = (8. * pi / 3.).sqrt();
    (
        scale * (4. * pi).sqrt() * a0.re,
        scale * V::new(-c * a11.re, c * a11.im, (4. * pi / 3.).sqrt() * a10.re),
    )
}
fn gamma(p: V) -> f64 {
    1f64.hypot(p.x).hypot(p.y).hypot(p.z)
}

struct Trial {
    sky: super::field::HarmonicSky,
    event: CollisionEvent,
    dp: V,
    de: f64,
}
fn trial(
    start: &super::field::HarmonicSky,
    work: usize,
    p0: V,
    mass: f64,
    depth: f64,
    scale: f64,
    scheme: CollisionScheme,
) -> Result<Option<Trial>, String> {
    let g0 = gamma(p0);
    let mut beta = p0 / g0;
    let mut prev: Option<(V, V)> = None;
    for _ in 0..18 {
        let (out, event, _) = match continuum_cell(
            &start.coefficients,
            start.lmax(),
            work,
            beta.into(),
            depth,
            scheme,
        ) {
            Ok(v) => v,
            Err(e) if e.starts_with("ill-conditioned continuum gain source") => return Ok(None),
            Err(e) => return Err(e),
        };
        let (de, dp) = exchange(&start.coefficients[0], &out[0], scale);
        let p1 = (mass * p0 - dp) / mass;
        let g1 = gamma(p1);
        if !de.is_finite() || !g1.is_finite() {
            return Err("nonfinite continuum recoil".into());
        }
        if (p1 - p0).norm() > 0.25 * g0 {
            return Ok(None);
        }
        let discrete = (p0 + p1) / (g0 + g1);
        let err = (discrete - beta).norm();
        if err <= 32. * f64::EPSILON * (1. + beta.norm()) {
            let mut sky = start.clone();
            sky.coefficients = out;
            if let Err(e) = sky.moments() {
                if e.starts_with("invalid radiation integral or negative transverse eigenvalue") {
                    return Ok(None);
                }
                return Err(e);
            }
            // Exact continuum electron-frame energy conservation, subject
            // to numerical residual/truncation. No energy adjustment.
            let scale_e =
                scale * (4. * std::f64::consts::PI).sqrt() * start.coefficients[0][0].re.abs();
            if (de - beta.dot(&dp)).abs() > 1e-9 * scale_e.max(f64::MIN_POSITIVE) {
                return Err("continuum recoil energy identity failed".into());
            }
            return Ok(Some(Trial { sky, event, dp, de }));
        }
        let residual = discrete - beta;
        let mut next = discrete;
        if let Some((old_r, old_v)) = prev {
            let dr = residual - old_r;
            let dr2 = dr.norm_squared();
            if dr2 > 0. {
                let correction = (discrete - old_v) * (dr.dot(&residual) / dr2);
                let candidate = discrete - correction;
                if correction.norm() <= 2. * err && candidate.norm_squared() < 1. {
                    next = candidate;
                }
            }
        }
        prev = Some((residual, discrete));
        beta = next;
    }
    Ok(None)
}

/// Transactional continuum harmonic recoil. Only the baryon host receives
/// the exchange; stage records contain continuum gain (gain_map=None).
/// Sampled positivity check uses the existing diagnostic grid; failure is
/// not repaired by clipping. Subdivision is bounded, not a positivity proof.
pub(super) fn scatter_with_recoil(
    sky: &mut super::field::HarmonicSky,
    dust: &mut crate::kinetic::tilted_dust::Dust,
    work: usize,
    depth: f64,
    scale: f64,
    scheme: CollisionScheme,
    events: &mut Vec<CollisionEvent>,
) -> Result<f64, String> {
    if !depth.is_finite() || depth < 0. || !scale.is_finite() || scale < 0. {
        return Err("invalid continuum recoil depth or scale".into());
    }
    if depth == 0. {
        return Ok(0.);
    }
    let mass = dust.beam(0)?.normal_mass_density;
    if mass <= 0. || !mass.is_finite() {
        return Err("continuum recoil requires positive host mass".into());
    }
    sky.moments()?;
    let mut output = sky.clone();
    let mut updated = dust.clone();
    let mut accepted = Vec::new();
    let mut pending = vec![(depth, 0usize)];
    let mut defect = 0.;
    let mut count = 0;
    while let Some((h, level)) = pending.pop() {
        count += 1;
        if count > 4095 {
            return Err("continuum recoil exceeded 4095 trials".into());
        }
        let p0 = V::from(updated.streams[0].p);
        if let Some(t) = trial(&output, work, p0, mass, h, scale, scheme)? {
            updated.kick(0, (-t.dp).into())?;
            let p1 = V::from(updated.streams[0].p);
            defect += t.de + mass * ((p0 + p1) / (gamma(p0) + gamma(p1))).dot(&(p1 - p0));
            output = t.sky;
            accepted.push(t.event);
        } else {
            if level >= 24 || h * 0.5 == 0. {
                return Err("continuum recoil subdivision exhausted".into());
            }
            pending.extend([(h * 0.5, level + 1); 2]);
        }
    }
    if !defect.is_finite() {
        return Err("nonfinite continuum recoil defect".into());
    }
    *sky = output;
    *dust = updated;
    events.extend(accepted);
    Ok(defect)
}
