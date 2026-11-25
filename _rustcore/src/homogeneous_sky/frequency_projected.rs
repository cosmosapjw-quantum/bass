//! Project the cold Thomson GENERATOR, not its resolvent. BE/SDIRK stages
//! solve the same finite-volume system at every depth. Positive gain and
//! diagonal loss permit a bounded fixed-point solve after depth subdivision.
use super::*;

type Field = Vec<Vec<M>>;
#[derive(Clone, Copy, Default)]
struct Exchange {
    escape_n: f64,
    escape_e: f64,
    escape_rest: f64,
    raw_rest: f64,
    raw_normal: f64,
}
impl Exchange {
    fn add(&mut self, x: Self, h: f64) {
        self.escape_n += h * x.escape_n;
        self.escape_e += h * x.escape_e;
        self.escape_rest += h * x.escape_rest;
        self.raw_rest += h * x.raw_rest;
        self.raw_normal += h * x.raw_normal;
    }
}
struct Plan {
    terms: Vec<Terms>,
    union: Vec<f64>,
    cell_weights: Vec<Vec<f64>>,
    number_weights: Vec<f64>,
    material_weights: Vec<f64>,
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
        let mut terms = Vec::new();
        let mut union = Vec::new();
        let mut cell_weights = Vec::new();
        let mut number_weights = Vec::new();
        let mut material_weights = Vec::new();
        for r in rays {
            let (e, j, d) = boost(r.e, beta)?;
            let (_, inv, _) = boost(e, -beta)?;
            let edges = g
                .edges
                .iter()
                .map(|u| u + r.shift + d.ln() + eta)
                .collect::<Vec<_>>();
            let weights = edges
                .windows(2)
                .map(|q| integral(3., q[0], q[1]))
                .collect::<Vec<_>>();
            if weights.iter().any(|w| !w.is_finite() || *w <= 0.) {
                return Err("invalid shifted frequency overlap cells".into());
            }
            union.extend_from_slice(&edges);
            cell_weights.push(weights);
            number_weights.push(r.w / (4. * PI) * (3. * (r.shift + eta)).exp() / NORM3);
            material_weights.push(r.w / (4. * PI * d.powi(3)));
            terms.push(Terms {
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
        Ok(Self {
            terms,
            union,
            cell_weights,
            number_weights,
            material_weights,
            nf: g.bins(),
        })
    }
    fn gain(&self, x: &Field, audit: bool) -> Result<(Field, Exchange), String> {
        let nr = self.terms.len();
        let rest: Field = x
            .iter()
            .zip(&self.terms)
            .map(|(f, t)| f.iter().map(|m| t.lift * *m * t.lift.transpose()).collect())
            .collect();
        let mut gain = vec![vec![M::zeros(); self.nf]; nr];
        let mut exchange = Exchange::default();
        let mut idx = vec![0usize; nr];
        let mut active = vec![false; nr];
        for u in self.union.windows(2) {
            let (l, r) = (u[0], u[1]);
            if r <= l {
                continue;
            }
            let w3 = integral(3., l, r);
            let w4 = if audit { integral(4., l, r) } else { 0. };
            let mut source = M::zeros();
            for i in 0..nr {
                let t = &self.terms[i];
                while idx[i] < self.nf && t.edges[idx[i] + 1] <= l {
                    idx[i] += 1
                }
                active[i] = idx[i] < self.nf && t.edges[idx[i]] <= l;
                if active[i] {
                    source += t.area * rest[i][idx[i]];
                }
            }
            for i in 0..nr {
                let t = &self.terms[i];
                let v = GAIN * t.gp * source * t.gp.transpose();
                if active[i] {
                    gain[i][idx[i]] +=
                        (w3 / self.cell_weights[i][idx[i]]) * t.back * v * t.back.transpose();
                }
                if audit {
                    let old = if active[i] {
                        rest[i][idx[i]].trace()
                    } else {
                        0.
                    };
                    let w = self.material_weights[i] * t.d;
                    let de = w * w4 * (v.trace() - old) / NORM4;
                    exchange.raw_rest += de;
                    exchange.raw_normal += de / t.d;
                    if !active[i] {
                        exchange.escape_n += w * w3 * v.trace() / NORM3;
                        exchange.escape_rest += w * w4 * v.trace() / NORM4;
                        exchange.escape_e += w * w4 * v.trace() / (NORM4 * t.d);
                    }
                }
            }
        }
        Ok((gain, exchange))
    }
    fn norm(&self, g: &FrequencyGrid, f: impl Fn(usize, usize) -> M) -> f64 {
        let mut norm = 0.;
        for i in 0..self.terms.len() {
            for j in 0..self.nf {
                norm += self.number_weights[i] * g.w3[j] * f(i, j).norm();
            }
        }
        norm
    }
    fn stage(
        &self,
        g: &FrequencyGrid,
        input: &Field,
        h: f64,
    ) -> Result<(Field, Exchange, usize, f64), String> {
        let nr = self.terms.len();
        let scale = self.norm(g, |i, j| input[i][j]).max(f64::MIN_POSITIVE);
        let mut current = input.clone();
        for k in 1..=80 {
            let (gain, _) = self.gain(&current, false)?;
            let next: Field = (0..nr)
                .map(|i| {
                    let z = h * self.terms[i].d;
                    let tr = 1. / (1. + z);
                    let alpha = z / (1. + z);
                    (0..self.nf)
                        .map(|j| tr * input[i][j] + alpha * gain[i][j])
                        .collect()
                })
                .collect();
            let change = self.norm(g, |i, j| next[i][j] - current[i][j]) / scale;
            current = next;
            if !change.is_finite() {
                return Err("nonfinite projected Thomson iteration".into());
            }
            if change <= 16. * f64::EPSILON {
                let (gain, ex) = self.gain(&current, true)?;
                let residual = self.norm(g, |i, j| {
                    current[i][j] - input[i][j] - h * self.terms[i].d * (gain[i][j] - current[i][j])
                }) / scale;
                if residual <= 128. * f64::EPSILON {
                    return Ok((current, ex, k, residual));
                }
            }
        }
        Err("projected frequency Thomson stage failed to converge".into())
    }
}

pub(super) fn projected_once(
    rays: &mut [Ray],
    g: &FrequencyGrid,
    eta: f64,
    beta: V,
    depth: f64,
    scheme: CollisionScheme,
    a: &mut Audit,
) -> Result<(), String> {
    let plan = Plan::new(rays, g, eta, beta)?;
    let input: Field = rays.iter().map(|r| r.f.clone()).collect();
    let h = if scheme == CollisionScheme::Sdirk2 {
        SDIRK_GAMMA * depth
    } else {
        depth
    };
    let (y1, x1, k1, r1) = plan.stage(g, &input, h)?;
    let mut ex = Exchange::default();
    let result = if scheme == CollisionScheme::Sdirk2 {
        let q: Field = input
            .iter()
            .zip(&y1)
            .map(|(x, y)| {
                x.iter()
                    .zip(y)
                    .map(|(u, v)| *u + (1. + SQRT_2) * (*v - *u))
                    .collect()
            })
            .collect();
        let (y2, x2, k2, r2) = plan.stage(g, &q, h)?;
        ex.add(x1, (1. - SDIRK_GAMMA) * depth);
        ex.add(x2, h);
        a.max_fv_iterations = a.max_fv_iterations.max(k1).max(k2);
        a.max_fv_residual = a.max_fv_residual.max(r1).max(r2);
        y2
    } else {
        ex.add(x1, h);
        a.max_fv_iterations = a.max_fv_iterations.max(k1);
        a.max_fv_residual = a.max_fv_residual.max(r1);
        y1
    };
    let (mut n0, mut e0, mut en0, mut n1, mut e1, mut en1) = (0., 0., 0., 0., 0., 0.);
    for (i, (ray, f)) in rays.iter_mut().zip(result).enumerate() {
        let d = plan.terms[i].d;
        let (n, e) = ray.values(g, eta);
        n0 += n;
        e0 += d * e;
        en0 += e;
        if f.iter()
            .any(|m| screen_min_rel(m).map_or(true, |x| x < -1e-10))
        {
            return Err("non-PSD projected frequency cell".into());
        }
        ray.f = f;
        let (n, e) = ray.values(g, eta);
        n1 += n;
        e1 += d * e;
        en1 += e;
    }
    let nd = (n1 - n0 + ex.escape_n).abs() / n0.max(f64::MIN_POSITIVE);
    let ed = ex.raw_rest.abs() / e0.max(f64::MIN_POSITIVE);
    let proj = e1 - e0 + ex.escape_rest - ex.raw_rest;
    if ![nd, ed, proj, ex.escape_n, ex.escape_e]
        .iter()
        .all(|v| v.is_finite())
    {
        return Err("nonfinite projected frequency ledger".into());
    }
    a.escape_n += ex.escape_n;
    a.escape_e += ex.escape_e;
    a.max_number = a.max_number.max(nd);
    a.max_rest = a.max_rest.max(ed);
    a.max_project = a.max_project.max(proj.abs() / e0.max(f64::MIN_POSITIVE));
    a.thomson_proj += proj;
    a.thomson_normal += ex.raw_normal;
    a.thomson_normal_proj += en1 - en0 + ex.escape_e - ex.raw_normal;
    a.subcells += 1;
    Ok(())
}
