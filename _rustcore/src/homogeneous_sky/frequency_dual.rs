//! R118-C1: positive, two-moment conservative nodal photon measure.
//! Each node carries an integrated emission-coordinate number screen,
//! not a sampled occupation. Linear barycentric deposition in energy
//! preserves number AND energy (including the zero-exterior ledger).
//! R118-C2 bounded model: reversible, angle-coherent dilute frequency
//! diffusion; not a calibrated atomic redistribution kernel.
use super::*;

const E_PER_N: f64 = NORM3 / NORM4;
type Field = Vec<Vec<M>>;
fn energy_nodes(g: &FrequencyGrid) -> Vec<f64> {
    g.edges.iter().map(|x| x.exp()).collect()
}

/// Positive hat projection of an occupation f(u) in x=exp(u):
/// sum masses = int exp(3u) f du, sum x*masses = int exp(4u) f du
/// at the same quadrature accuracy. No moment inversion or PSD clipping.
pub fn project_number_nodes(g: &FrequencyGrid, f: impl Fn(f64) -> f64) -> Result<Vec<f64>, String> {
    let mut m = vec![0.; g.bins() + 1];
    for (i, v) in g.edges.windows(2).enumerate() {
        let (l, r) = (v[0], v[1]);
        let mid = 0.5 * (l + r);
        let h = 0.5 * (r - l);
        let den = (r - l).exp_m1();
        for k in 0..4 {
            for sign in [-1., 1.] {
                let u = mid + sign * h * GX[k];
                let w = h * GW[k] * (3. * u).exp() * f(u);
                let b = (u - l).exp_m1() / den;
                if !w.is_finite() || w < 0. || !(0. ..=1.).contains(&b) {
                    return Err("invalid nodal number projection".into());
                }
                m[i] += (1. - b) * w;
                m[i + 1] += b * w;
            }
        }
    }
    Ok(m)
}
#[derive(Clone, Copy, Debug)]
struct Deposit {
    lo: usize,
    right: f64,
}
const OUT: usize = usize::MAX;
fn deposit(z: &[f64], v: f64, j: &mut usize) -> Deposit {
    if v < z[0] || v > z[z.len() - 1] {
        return Deposit { lo: OUT, right: 0. };
    }
    while *j + 1 < z.len() && z[*j + 1] <= v {
        *j += 1;
    }
    if *j == z.len() - 1 {
        return Deposit { lo: *j, right: 0. };
    }
    let t = (v - z[*j]).exp_m1() / (z[*j + 1] - z[*j]).exp_m1();
    Deposit { lo: *j, right: t }
}
fn values(r: &Ray, x: &[f64], eta: f64) -> (f64, f64) {
    let nscale = r.w / (4. * PI * NORM3) * (3. * (r.shift + eta)).exp();
    let enscale = nscale * E_PER_N * (r.shift + eta).exp();
    (
        nscale * r.f.iter().map(|q| q.trace()).sum::<f64>(),
        enscale * r.f.iter().zip(x).map(|(q, x)| q.trace() * x).sum::<f64>(),
    )
}
fn nscale(r: &Ray, eta: f64) -> f64 {
    r.w / (4. * PI * NORM3) * (3. * (r.shift + eta)).exp()
}
#[derive(Clone, Copy, Default)]
struct Exchange {
    escape_n: f64,
    escape_e: f64,
    escape_rest: f64,
    raw_rest: f64,
    raw_normal: f64,
    numerical_second_moment: f64,
}
impl Exchange {
    fn add(&mut self, x: Self, h: f64) {
        self.escape_n += h * x.escape_n;
        self.escape_e += h * x.escape_e;
        self.escape_rest += h * x.escape_rest;
        self.raw_rest += h * x.raw_rest;
        self.raw_normal += h * x.raw_normal;
        self.numerical_second_moment += h * x.numerical_second_moment;
    }
}
struct Term {
    d: f64,
    scale: f64,
    into_rest: M,
    out: M,
    z: Vec<f64>,
    x: Vec<f64>,
}
struct Plan {
    t: Vec<Term>,
    maps: Vec<Vec<Deposit>>,
    nf: usize,
}
impl Plan {
    fn new(rays: &[Ray], g: &FrequencyGrid, eta: f64, beta: V) -> Result<Self, String> {
        let ph = rays
            .iter()
            .map(|r| Photon {
                direction: r.e,
                weight: r.w,
                screen: projector(&r.e) * 0.5,
            })
            .collect::<Vec<_>>();
        let map = gain_map(&ph, beta)?;
        let nf = g.bins() + 1;
        let nr = rays.len();
        let mut t = Vec::with_capacity(nr);
        for r in rays {
            let (e, j, d) = boost(r.e, beta)?;
            let (_, inv, _) = boost(e, -beta)?;
            let z = g
                .edges
                .iter()
                .map(|u| u + (r.shift + eta + d.ln()))
                .collect::<Vec<_>>();
            let x = z.iter().map(|z| z.exp()).collect::<Vec<_>>();
            let scale = nscale(r, eta);
            if !scale.is_finite()
                || scale <= 0.
                || x.iter().any(|v| !v.is_finite() || *v <= 0.)
                || z.windows(2).any(|v| v[1] <= v[0])
            {
                return Err("invalid dual material-frequency coordinates".into());
            }
            t.push(Term {
                d,
                scale,
                into_rest: j * d.sqrt(),
                out: inv * projector(&e) * map * (GAIN * r.w / (d * d)).sqrt(),
                z,
                x,
            });
        }
        // Receiver-major maps. Log grids are sorted; a two-pointer
        // search and expm1 weights avoid near-coincident-node cancellation.
        let mut maps = Vec::with_capacity(nr * nr);
        for dest in &t {
            for source in &t {
                let mut j = 0;
                let p = source
                    .z
                    .iter()
                    .map(|v| deposit(&dest.z, *v, &mut j))
                    .collect::<Vec<_>>();
                if p.iter().any(|p| !(0. ..=1.).contains(&p.right)) {
                    return Err("nonconvex frequency deposition".into());
                }
                maps.push(p);
            }
        }
        Ok(Self { t, maps, nf })
    }
    // State Q is normal angular-integrated centered number mass. In
    // material angular-number coordinates D*J Q J^T is the donor source.
    // The normal-clock gain to receiver i is area_i*GAIN*Jinv G_i S G_i^T Jinv^T.
    // Its loss is D_i Q_i; no extra D multiplies the gain.
    fn gain(&self, x: &Field, audit: bool) -> Result<(Field, Exchange), String> {
        let nr = self.t.len();
        let rest: Field = x
            .iter()
            .zip(&self.t)
            .map(|(v, t)| {
                v.iter()
                    .map(|q| t.into_rest * *q * t.into_rest.transpose())
                    .collect()
            })
            .collect();
        let mut ex = Exchange::default();
        let mut full_e = M::zeros();
        if audit {
            for (v, t) in rest.iter().zip(&self.t) {
                for (q, z) in v.iter().zip(&t.x) {
                    full_e += *q * *z;
                }
            }
        }
        let mut gain = Vec::with_capacity(nr);
        for i in 0..nr {
            let t = &self.t[i];
            let mut a = vec![M::zeros(); self.nf];
            let (mut outside_n, mut outside_e) = (M::zeros(), M::zeros());
            let mut spread = M::zeros();
            for (j, source) in rest.iter().enumerate() {
                let p = &self.maps[i * nr + j];
                for (k, (m, dst)) in source.iter().zip(p).enumerate() {
                    if dst.lo == OUT {
                        if audit {
                            outside_n += m;
                            outside_e += *m * self.t[j].x[k];
                        }
                    } else if dst.right == 0. {
                        a[dst.lo] += m;
                    } else {
                        a[dst.lo] += *m * (1. - dst.right);
                        a[dst.lo + 1] += *m * dst.right;
                        if audit {
                            let x = self.t[j].x[k];
                            spread += *m * ((x - t.x[dst.lo]) * (t.x[dst.lo + 1] - x));
                        }
                    }
                }
            }
            let apply = |v: M| t.out * v * t.out.transpose();
            if audit {
                let n = apply(outside_n).trace();
                let e = E_PER_N * apply(outside_e).trace();
                ex.escape_n += n;
                ex.escape_rest += e;
                ex.escape_e += e / t.d;
                let loss = x[i]
                    .iter()
                    .zip(&t.x)
                    .map(|(q, z)| q.trace() * z)
                    .sum::<f64>()
                    * t.d;
                let raw = E_PER_N * (apply(full_e).trace() - loss);
                ex.raw_rest += raw;
                ex.raw_normal += raw / t.d;
                ex.numerical_second_moment += apply(spread).trace();
            }
            for m in &mut a {
                *m = apply(*m);
            }
            gain.push(a);
        }
        Ok((gain, ex))
    }
    fn norm(&self, f: impl Fn(usize, usize) -> M) -> f64 {
        let mut n = 0.;
        for i in 0..self.t.len() {
            for j in 0..self.nf {
                n += f(i, j).norm();
            }
        }
        n
    }
    fn stage(&self, input: &Field, h: f64) -> Result<(Field, Exchange, usize, f64), String> {
        let nr = self.t.len();
        let scale = self.norm(|i, j| input[i][j]).max(f64::MIN_POSITIVE);
        let mut current = input.clone();
        for k in 1..=80 {
            let (gain, _) = self.gain(&current, false)?;
            let next: Field = (0..nr)
                .map(|i| {
                    let inv = 1. / (1. + h * self.t[i].d);
                    (0..self.nf)
                        .map(|j| inv * (input[i][j] + h * gain[i][j]))
                        .collect()
                })
                .collect();
            let change = self.norm(|i, j| next[i][j] - current[i][j]) / scale;
            current = next;
            if !change.is_finite() {
                return Err("dual frequency stage nonfinite".into());
            }
            if change <= 16. * f64::EPSILON {
                let (gain, ex) = self.gain(&current, true)?;
                let residual = self.norm(|i, j| {
                    current[i][j] - input[i][j] - h * (gain[i][j] - self.t[i].d * current[i][j])
                }) / scale;
                if residual <= 128. * f64::EPSILON {
                    return Ok((current, ex, k, residual));
                }
            }
        }
        Err("dual frequency stage did not converge".into())
    }
}
fn collide(
    rays: &mut [Ray],
    g: &FrequencyGrid,
    x: &[f64],
    eta: f64,
    ev: &CollisionEvent,
    a: &mut Audit,
) -> Result<(), String> {
    let beta = V::from(ev.beta);
    validate_cell(ev.depth, &beta)?;
    if ev.depth == 0. {
        return Ok(());
    }
    let max_d = (1. + beta.norm()) / (1. - beta.norm_squared()).sqrt();
    let n = (max_d * ev.depth).ceil().max(1.) as usize;
    if n > 256 {
        return Err("dual frequency event requires more than 256 depth subcells".into());
    }
    let h = ev.depth / n as f64;
    let plan = Plan::new(rays, g, eta, beta)?;
    a.events += 1;
    for _ in 0..n {
        let input: Field = rays
            .iter()
            .zip(&plan.t)
            .map(|(r, t)| r.f.iter().map(|q| *q * t.scale).collect())
            .collect();
        let d = if ev.scheme == CollisionScheme::Sdirk2 {
            SDIRK_GAMMA * h
        } else {
            h
        };
        let (y1, e1, k1, r1) = plan.stage(&input, d)?;
        let mut ex = Exchange::default();
        let result = if ev.scheme == CollisionScheme::Sdirk2 {
            let q: Field = input
                .iter()
                .zip(&y1)
                .map(|(x, y)| {
                    x.iter()
                        .zip(y)
                        .map(|(x, y)| *x + (1. + SQRT_2) * (*y - *x))
                        .collect()
                })
                .collect();
            let (y2, e2, k2, r2) = plan.stage(&q, d)?;
            ex.add(e1, (1. - SDIRK_GAMMA) * h);
            ex.add(e2, d);
            a.max_fv_iterations = a.max_fv_iterations.max(k1).max(k2);
            a.max_fv_residual = a.max_fv_residual.max(r1).max(r2);
            y2
        } else {
            ex.add(e1, h);
            a.max_fv_iterations = a.max_fv_iterations.max(k1);
            a.max_fv_residual = a.max_fv_residual.max(r1);
            y1
        };
        let (mut n0, mut e0, mut en0, mut n1, mut e1, mut en1) = (0., 0., 0., 0., 0., 0.);
        for (i, (ray, v)) in rays.iter_mut().zip(result).enumerate() {
            let t = &plan.t[i];
            let (n, e) = values(ray, x, eta);
            n0 += n;
            e0 += t.d * e;
            en0 += e;
            if v.iter()
                .any(|m| screen_min_rel(m).map_or(true, |q| q < -1e-10))
            {
                return Err("non-PSD dual frequency node".into());
            }
            ray.f = v.into_iter().map(|m| m / t.scale).collect();
            let (n, e) = values(ray, x, eta);
            n1 += n;
            e1 += t.d * e;
            en1 += e;
        }
        let nd = (n1 - n0 + ex.escape_n).abs() / n0.max(f64::MIN_POSITIVE);
        let ed = ex.raw_rest.abs() / e0.max(f64::MIN_POSITIVE);
        let proj = e1 - e0 + ex.escape_rest - ex.raw_rest;
        if ![nd, ed, proj, ex.escape_n, ex.escape_e]
            .iter()
            .all(|v| v.is_finite())
        {
            return Err("nonfinite dual collision ledger".into());
        }
        a.escape_n += ex.escape_n;
        a.escape_e += ex.escape_e;
        a.max_number = a.max_number.max(nd);
        a.max_rest = a.max_rest.max(ed);
        a.max_project = a.max_project.max(proj.abs() / e0.max(f64::MIN_POSITIVE));
        a.thomson_proj += proj;
        a.thomson_normal += ex.raw_normal;
        a.thomson_normal_proj += en1 - en0 + ex.escape_e - ex.raw_normal;
        a.dual_second_moment += ex.numerical_second_moment;
        a.subcells += 1;
    }
    Ok(())
}

/// Prescribed dilute, angle-coherent frequency diffusion. The Gaussian
/// envelope uses the associated Line's center/width, while the separate
/// coefficient is the peak log-frequency diffusion per material ray clock.
/// theta=T_bath/T_emit. No population, stimulated term or atom recoil kernel.
#[derive(Clone, Copy, Debug)]
pub struct Redistribution {
    diffusion: f64,
    theta: f64,
}
impl Redistribution {
    pub fn new(diffusion: f64, theta: f64) -> Result<Self, String> {
        if !diffusion.is_finite()
            || diffusion < 0.
            || diffusion > 1e8
            || !theta.is_finite()
            || !(1e-8..=1e6).contains(&theta)
        {
            return Err("invalid prescribed redistribution parameters".into());
        }
        Ok(Self { diffusion, theta })
    }
}
/// Exact two-state reversible relaxation: p is left-to-right fraction,
/// q right-to-left. Detailed balance pi_L*p=pi_R*q; p+q=1-exp(-rate*h).
pub fn reversible_pair_weights(
    log_l: f64,
    log_r: f64,
    rate: f64,
    h: f64,
) -> Result<(f64, f64), String> {
    if !log_l.is_finite()
        || !log_r.is_finite()
        || !rate.is_finite()
        || rate < 0.
        || !h.is_finite()
        || h < 0.
    {
        return Err("invalid reversible pair".into());
    }
    let alpha = -(-rate * h).exp_m1();
    let t = (log_l - log_r).abs().min(f64::MAX);
    let e = (-t).exp();
    let small = alpha * e / (1. + e);
    let large = alpha / (1. + e);
    Ok(if log_r >= log_l {
        (large, small)
    } else {
        (small, large)
    })
}
#[derive(Clone, Copy, Default, Debug)]
pub struct RedistributionSnapshot {
    pub eta: f64,
    pub normal_energy: f64,
    pub material_energy: f64,
}
#[derive(Clone, Default, Debug)]
pub struct DualStats {
    /// Cumulative local increase of the centered material-frame squared
    /// photon energy moment from barycentric remap only. It is measured
    /// on the normal hypersurface and is not heat or a conserved charge.
    pub numerical_second_energy_moment: f64,
    pub max_number_defect: f64,
    pub max_material_energy_defect: f64,
    pub max_projection_energy_defect: f64,
    pub max_line_number_defect: f64,
    pub max_fv_stage_residual: f64,
    pub max_fv_stage_iterations: usize,
    pub collision_events: usize,
    pub collision_subcells: usize,
    pub line_cells: usize,
    pub min_drift: Option<f64>,
    pub max_drift: Option<f64>,
    pub turning_rays: usize,
    pub redistribution_cells: usize,
    pub max_redistribution_number_defect: f64,
    pub max_redistribution_energy_defect: f64,
    pub max_pair_balance_defect: f64,
}
#[derive(Default)]
struct RedistAudit {
    normal: f64,
    material: f64,
    count: usize,
    max_n: f64,
    max_e: f64,
    max_db: f64,
}
fn redistribute_ray(
    r: &mut Ray,
    g: &FrequencyGrid,
    x: &[f64],
    weights: &[f64],
    eta: f64,
    d: f64,
    h: f64,
    line: &Line,
    model: &Redistribution,
    a: &mut RedistAudit,
) -> Result<(), String> {
    if model.diffusion == 0. || h == 0. {
        return Ok(());
    }
    let (n0, e0) = values(r, x, eta);
    let scale = nscale(r, eta) * E_PER_N * (r.shift + eta).exp();
    let shift = r.shift + d.ln();
    let mut transfer = 0.;
    // Strang even/odd edge sweeps. Pair equilibrium weights are nodal
    // phase-space measures times exp(-h nu_material/kT_bath).
    for (parity, dt) in [(0, h * 0.5), (1, h), (0, h * 0.5)] {
        for i in (parity..x.len() - 1).step_by(2) {
            let l = g.edges[i];
            let u = g.edges[i + 1];
            let du = u - l;
            let z = (0.5 * (l + u) + shift - line.center) / line.width;
            let k = model.diffusion * (-0.5 * z * z).exp();
            if k == 0. {
                continue;
            }
            let rate = 2. * d * k / (du * du);
            let ll = weights[i].ln() - x[i] * shift.exp() / model.theta;
            let lr = weights[i + 1].ln() - x[i + 1] * shift.exp() / model.theta;
            let (p, q) = reversible_pair_weights(ll, lr, rate, dt)?;
            let left = r.f[i];
            let right = r.f[i + 1];
            let delta = p * left - q * right;
            r.f[i] = (1. - p) * left + q * right;
            r.f[i + 1] = p * left + (1. - q) * right;
            transfer += scale * (x[i + 1] - x[i]) * delta.trace();
            let m = ll.max(lr);
            let pl = (ll - m).exp();
            let pr = (lr - m).exp();
            a.max_db = a.max_db.max((pl * p - pr * q).abs() / (pl + pr));
        }
    }
    let (n1, e1) = values(r, x, eta);
    a.max_n = a.max_n.max((n1 - n0).abs() / n0.max(f64::MIN_POSITIVE));
    a.max_e = a
        .max_e
        .max((e1 - e0 - transfer).abs() / e0.max(f64::MIN_POSITIVE));
    a.normal += transfer;
    a.material += d * transfer;
    Ok(())
}
fn line_cell(
    rays: &mut [Ray],
    g: &FrequencyGrid,
    x: &[f64],
    weights: &[f64],
    node: &RayNode,
    h: f64,
    line: &LineHistory,
    red: Option<&Redistribution>,
    a: &mut Audit,
    ra: &mut RedistAudit,
) -> Result<(), String> {
    let (beta, db) = line.velocity_at(node.eta)?;
    let b = V::from(beta);
    let (mut n0, mut n1, mut dn, mut de, mut dm, mut dp, mut dpm) = (0., 0., 0., 0., 0., 0., 0.);
    for r in rays {
        let (_, _, d) = boost(r.e, b)?;
        let drift = -d * material_expansion_factor(node, r.e.into(), beta, db)?;
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
        let nh = nscale(r, node.eta);
        let eh = nh * E_PER_N * (r.shift + node.eta).exp();
        let shift = r.shift + d.ln();
        let source = projector(&r.e) * (0.5 * line.line.source);
        let mut absorb = |r: &mut Ray, dt: f64| {
            let (n, e) = values(r, x, node.eta);
            n0 += n;
            let old_de = de;
            for i in 0..x.len() {
                let tau = dt * d * line.line.strength * line.line.profile(g.edges[i] + shift);
                let alpha = -(-tau).exp_m1();
                let old = r.f[i];
                let src = source * weights[i];
                let delta = alpha * (src - old);
                r.f[i] = (1. - alpha) * old + alpha * src;
                let ne = nh * delta.trace();
                let en = eh * x[i] * delta.trace();
                dn += ne;
                de += en;
                dm += d * en;
            }
            let (n, e1) = values(r, x, node.eta);
            n1 += n;
            let p = e1 - e - (de - old_de);
            dp += p;
            dpm += d * p;
        };
        if let Some(model) = red {
            absorb(r, h * 0.5);
            redistribute_ray(r, g, x, weights, node.eta, d, h, &line.line, model, ra)?;
            absorb(r, h * 0.5);
        } else {
            absorb(r, h);
        }
    }
    if red.is_some() {
        ra.count += 1;
    }
    a.max_line_n = a
        .max_line_n
        .max((n1 - n0 - dn).abs() / n0.max(f64::MIN_POSITIVE));
    a.line_n += dn;
    a.line_e += de;
    a.line_material_e += dm;
    a.line_proj += dpm;
    a.line_normal_proj += dp;
    a.line_cells += 1;
    Ok(())
}
fn geometric_all(
    rays: &mut [Ray],
    x: &[f64],
    l: &RayNode,
    r: &RayNode,
    a: &mut Audit,
) -> Result<(), String> {
    for ray in rays {
        let before = values(ray, x, l.eta).1;
        ray.geometric(l, r)?;
        a.geom_energy += values(ray, x, r.eta).1 - before;
    }
    Ok(())
}
fn geometry(
    rays: &mut [Ray],
    g: &FrequencyGrid,
    x: &[f64],
    weights: &[f64],
    l: &RayNode,
    r: &RayNode,
    line: Option<&LineHistory>,
    red: Option<&Redistribution>,
    a: &mut Audit,
    ra: &mut RedistAudit,
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
            geometric_all(rays, x, &left, &middle, a)?;
            line_cell(rays, g, x, weights, &middle, t[1] - t[0], line, red, a, ra)?;
            geometric_all(rays, x, &middle, &right, a)?;
        }
    } else {
        geometric_all(rays, x, l, r, a)?;
    }
    Ok(())
}
fn snapshot(rays: &[Ray], x: &[f64], eta: f64, a: &Audit) -> Result<FrequencySnapshot, String> {
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
        let (n, e) = values(r, x, eta);
        s.number_centered += n;
        s.energy_centered += e;
        for i in 0..3 {
            s.number_flux[i] += n * r.e[i];
        }
        for f in &r.f {
            s.min_screen_relative = s.min_screen_relative.min(screen_min_rel(f)?);
        }
    }
    if !s.number_centered.is_finite()
        || !s.energy_centered.is_finite()
        || s.min_screen_relative < -1e-10
    {
        return Err("invalid dual nodal snapshot".into());
    }
    Ok(s)
}
#[derive(Clone, Debug)]
pub struct DualSample {
    pub direction: [f64; 3],
    pub weight: f64,
    pub log_shift: f64,
    /// Integral of emission-coordinate e^(3u) occupation assigned to each
    /// node. Under observer boost ONLY shift, screen and solid angle change.
    pub number_mass: Vec<[[f64; 3]; 3]>,
}
pub struct DualSky {
    rays: Vec<Ray>,
    pub history: Vec<FrequencySnapshot>,
    pub redistribution: Vec<RedistributionSnapshot>,
    pub stats: DualStats,
}
impl DualSky {
    pub fn samples(&self) -> Vec<DualSample> {
        self.rays
            .iter()
            .map(|r| DualSample {
                direction: r.e.into(),
                weight: r.w,
                log_shift: r.shift,
                number_mass: r.f.iter().map(rows).collect(),
            })
            .collect()
    }
    pub fn observer_samples(&self, beta: [f64; 3]) -> Result<Vec<DualSample>, String> {
        self.rays
            .iter()
            .map(|r| {
                let (e, j, d) = boost(r.e, V::from(beta))?;
                Ok(DualSample {
                    direction: e.into(),
                    weight: r.w / (d * d),
                    log_shift: r.shift + d.ln(),
                    number_mass: r
                        .f
                        .iter()
                        .map(|m| rows(&(j * *m * j.transpose())))
                        .collect(),
                })
            })
            .collect()
    }
    pub fn normal_energy_balance_defect(&self) -> f64 {
        let b = self.history.last().unwrap();
        b.energy_centered - self.history[0].energy_centered + b.escaped_energy_centered
            - b.geometric_energy_centered
            - b.thomson_normal_energy_centered
            - b.thomson_normal_projection_energy_centered
            - b.line_normal_energy_centered
            - b.line_normal_projection_energy_centered
            - self.redistribution.last().unwrap().normal_energy
    }
    pub fn number_continuity_defect(&self, records: &[StepRecord]) -> Result<f64, String> {
        if self.history.len() != records.len() + 1 {
            return Err("dual history length mismatch".into());
        }
        let mut flux = 0.;
        for (r, s) in records.iter().zip(self.history.windows(2)) {
            if r.left.eta != s[0].eta || r.right.eta != s[1].eta {
                return Err("dual history clock mismatch".into());
            }
            let f = |n: &RayNode, q: &FrequencySnapshot| {
                n.a.iter()
                    .zip(q.number_flux)
                    .map(|(a, b)| a * b)
                    .sum::<f64>()
            };
            flux += (r.right.eta - r.left.eta) * (f(&r.left, &s[0]) + f(&r.right, &s[1]));
        }
        let q = self.history.last().unwrap();
        Ok(
            q.number_centered - self.history[0].number_centered + q.escaped_number_centered
                - q.line_number_centered
                - flux,
        )
    }
}
pub fn replay_dual_frequency(
    records: &[StepRecord],
    nmu: usize,
    nphi: usize,
    g: &FrequencyGrid,
    line: Option<&LineHistory>,
    red: Option<&Redistribution>,
) -> Result<DualSky, String> {
    if records.is_empty() || records[0].left.eta != 0. || red.is_some() && line.is_none() {
        return Err("invalid dual replay input or missing redistribution line history".into());
    }
    let nr = nmu
        .checked_mul(nphi)
        .ok_or("dual angular allocation overflow")?;
    if nr > 256
        || nr
            .checked_mul(nr)
            .and_then(|v| v.checked_mul(g.bins() + 1))
            .is_none_or(|v| v > 20_000_000)
    {
        return Err("dual remap plan exceeds bounded allocation".into());
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
            return Err("discontinuous dual replay geometry or clock".into());
        }
    }
    if let Some(l) = line {
        l.velocity_at(records.last().unwrap().right.eta)?;
    }
    let x = energy_nodes(g);
    let masses = project_number_nodes(g, planck)?;
    let weights = project_number_nodes(g, |_| 1.)?;
    let mut rays = initial_sky(nmu, nphi)?
        .iter()
        .map(|p| Ray {
            e: p.direction,
            w: p.weight,
            shift: 0.,
            f: masses.iter().map(|v| p.screen * *v).collect(),
            last_sign: 0,
            turned: false,
        })
        .collect::<Vec<_>>();
    let mut a = Audit::default();
    let mut ra = RedistAudit::default();
    let mut history = vec![snapshot(&rays, &x, 0., &a)?];
    let mut redistribution = vec![RedistributionSnapshot::default()];
    for r in records {
        for ev in &r.first {
            collide(&mut rays, g, &x, r.left.eta, ev, &mut a)?;
        }
        geometry(
            &mut rays, g, &x, &weights, &r.left, &r.right, line, red, &mut a, &mut ra,
        )?;
        for ev in &r.second {
            collide(&mut rays, g, &x, r.right.eta, ev, &mut a)?;
        }
        history.push(snapshot(&rays, &x, r.right.eta, &a)?);
        redistribution.push(RedistributionSnapshot {
            eta: r.right.eta,
            normal_energy: ra.normal,
            material_energy: ra.material,
        });
    }
    let stats = DualStats {
        numerical_second_energy_moment: a.dual_second_moment,
        max_number_defect: a.max_number,
        max_material_energy_defect: a.max_rest,
        max_projection_energy_defect: a.max_project,
        max_line_number_defect: a.max_line_n,
        max_fv_stage_residual: a.max_fv_residual,
        max_fv_stage_iterations: a.max_fv_iterations,
        collision_events: a.events,
        collision_subcells: a.subcells,
        line_cells: a.line_cells,
        min_drift: a.min_drift,
        max_drift: a.max_drift,
        turning_rays: rays.iter().filter(|r| r.turned).count(),
        redistribution_cells: ra.count,
        max_redistribution_number_defect: ra.max_n,
        max_redistribution_energy_defect: ra.max_e,
        max_pair_balance_defect: ra.max_db,
    };
    Ok(DualSky {
        rays,
        history,
        redistribution,
        stats,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn full_reversible_chain_preserves_discrete_wien_screen() {
        let g = FrequencyGrid::new(-2., 2., 128).unwrap();
        let x = energy_nodes(&g);
        let weights = project_number_nodes(&g, |_| 1.).unwrap();
        let theta = 0.13;
        let p = Photon::isotropic([0., 0., 1.], 1.).unwrap();
        let screen = M::from_diagonal(&V::new(0.2, 0.8, 0.));
        let mut ray = Ray {
            e: p.direction,
            w: 1.,
            shift: 0.,
            f: weights
                .iter()
                .zip(&x)
                .map(|(w, x)| screen * (*w * (-x / theta).exp()))
                .collect(),
            last_sign: 0,
            turned: false,
        };
        let old = ray.f.clone();
        let model = Redistribution::new(0.1, theta).unwrap();
        let line = Line::new(0., 1., 0., 0.).unwrap();
        let mut audit = RedistAudit::default();
        for _ in 0..32 {
            redistribute_ray(
                &mut ray, &g, &x, &weights, 0., 1., 0.1, &line, &model, &mut audit,
            )
            .unwrap();
        }
        let n = old.iter().map(|m| m.norm()).sum::<f64>();
        let err = old
            .iter()
            .zip(&ray.f)
            .map(|(x, y)| (x - y).norm())
            .sum::<f64>()
            / n;
        eprintln!(
            "discrete polarized Wien equilibrium relative L1 {err:e}, energy ledger {:e}",
            audit.normal
        );
        assert!(err < 1e-13);
        assert!(audit.normal.abs() < 1e-15);
    }
}
