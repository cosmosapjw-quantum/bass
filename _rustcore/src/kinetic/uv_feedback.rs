//! Research-only general Bianchi-I UV transport with pressureless energy exchange.
//! Gas absorbers prescribed; no autonomous gas chemistry or cooling closure.
use super::{
    owned_vlasov::{Matter, OwnedState},
    sphere::{gauss_legendre, SphereGrid},
};
use nalgebra::{Matrix3, Vector3};
const H0: f64 = 2.1842852410855023e-18;
const C: f64 = 299792458.;
const EV: f64 = 1.602176634e-19;
const RHO0: f64 = 3. * C * C * H0 * H0 / (8. * std::f64::consts::PI * 6.67430e-11);
#[derive(Clone, Copy, Debug)]
pub struct Gas {
    pub ne_m3: f64,
    pub absorbers_m3: [f64; 3],
}
#[derive(Clone, Debug)]
pub struct UvState {
    n: Vec<f64>,
    pub reservoir: f64,
    pub work: f64,
    pub emitted: f64,
    pub absorbed: f64,
    pub births: f64,
    pub absorbed_n: f64,
}
pub struct UvModel {
    a0: f64,
    nh0: f64,
    dir: Vec<Vector3<f64>>,
    weights: Vec<f64>,
    q: Vec<f64>,
    source: Vec<(f64, f64)>,
    strength: f64,
}
fn sigma(e: f64, i: usize) -> f64 {
    let p = [
        [13.60, 0.4298, 5.475e4, 32.88, 2.963, 0., 0., 0.],
        [24.59, 13.61, 949.2, 1.469, 3.188, 2.039, 0.4434, 2.136],
        [54.42, 1.720, 1.369e4, 32.88, 2.963, 0., 0., 0.],
    ][i];
    if e < p[0] {
        return 0.;
    }
    let x = e / p[1] - p[6];
    let y = x.hypot(p[7]);
    1e-22
        * p[2]
        * ((x - 1.).powi(2) + p[5] * p[5])
        * y.powf(p[4] / 2. - 5.5)
        * (1. + (y / p[3]).sqrt()).powf(-p[4])
}
impl UvModel {
    pub fn new(
        a0: f64,
        nh0: f64,
        nt: usize,
        np: usize,
        nq: usize,
        strength: f64,
    ) -> Result<Self, String> {
        if a0 <= 0.
            || nh0 <= 0.
            || nq < 16
            || nt < 4
            || np < 8
            || strength < 0.
            || ![a0, nh0, strength].iter().all(|v| v.is_finite())
        {
            return Err("UV model domain".into());
        }
        let g = SphereGrid::new(nt, np);
        let dir = g
            .ehat
            .chunks_exact(3)
            .map(Vector3::from_column_slice)
            .collect();
        let weights =
            g.w.iter()
                .map(|x| x / (4. * std::f64::consts::PI))
                .collect();
        let q = (0..nq)
            .map(|i| 6.8 * (768_f64 / 6.8).powf(i as f64 / (nq - 1) as f64))
            .collect();
        let (x, w) = gauss_legendre(24);
        let mut source = Vec::new();
        for e in [13.6, 24.59, 54.42, 100.].windows(2) {
            for (&x, &w) in x.iter().zip(&w) {
                let v = (e[1] + e[0]) / 2. + (e[1] - e[0]) * x / 2.;
                let wt =
                    w * (e[1] - e[0]) / 2. * v * v / (v / (8.617333262145e-5 * 50000.)).exp_m1();
                source.push((v, wt));
            }
        }
        let total = source.iter().map(|x| x.1).sum::<f64>();
        for x in &mut source {
            x.1 /= total;
        }
        Ok(Self {
            a0,
            nh0,
            dir,
            weights,
            q,
            source,
            strength,
        })
    }
    pub fn empty(&self) -> UvState {
        UvState {
            n: vec![0.; self.dir.len() * self.q.len()],
            reservoir: 0.,
            work: 0.,
            emitted: 0.,
            absorbed: 0.,
            births: 0.,
            absorbed_n: 0.,
        }
    }
    fn rays(&self, g: &OwnedState) -> Result<Vec<(f64, Vector3<f64>, f64)>, String> {
        if g.a <= 0. || (g.f.determinant() - 1.).abs() > 1e-7 {
            return Err("UV coframe".into());
        }
        let inv = g.f.try_inverse().ok_or("UV inverse")?.transpose();
        Ok(self
            .dir
            .iter()
            .zip(&self.weights)
            .map(|(n, w)| {
                let v = inv * n;
                let d = v.norm();
                (self.a0 / g.a * d, v / d, w / d.powi(3))
            })
            .collect())
    }
    pub fn moments(&self, s: &UvState, g: &OwnedState) -> Result<(f64, Matrix3<f64>), String> {
        let mut u = 0.;
        let mut p = Matrix3::zeros();
        for (j, (r, n, _)) in self.rays(g)?.into_iter().enumerate() {
            let e = r * self
                .q
                .iter()
                .zip(&s.n[j * self.q.len()..(j + 1) * self.q.len()])
                .map(|(e, n)| e * n)
                .sum::<f64>();
            u += e;
            p += e * n * n.transpose();
        }
        Ok((u, p))
    }
    pub fn add_matter(&self, s: &UvState, g: &OwnedState, m: &mut Matter) -> Result<(), String> {
        let (u, p) = self.moments(s, g)?;
        let fac = self.nh0 * EV / RHO0 / g.a.powi(3);
        m.rho += fac * (u + s.reservoir);
        m.pressure += fac * p;
        m.photon_rho += fac * u;
        if m.rho <= 0. {
            return Err("UV total density".into());
        }
        Ok(())
    }
    fn source_rate(&self, a: f64) -> f64 {
        let z = 1. / a;
        let sfr = 0.015 * z.powf(2.7) / (1. + (z / 2.9).powf(5.6));
        let ly = 1. / (0.00038 * 0.002_f64.powf(0.227) + 0.01858) - 2.55_f64.log10();
        self.strength * 0.2 * 10_f64.powf(ly) * sfr / (3.0856775814913673e22_f64.powi(3) * self.nh0)
    }
    pub fn advance(
        &self,
        s: &mut UvState,
        old: &OwnedState,
        mid: &OwnedState,
        end: &OwnedState,
        dt: f64,
        gas: Gas,
    ) -> Result<(), String> {
        if dt < 0. || !dt.is_finite() || !gas.absorbers_m3.iter().all(|x| *x >= 0. && x.is_finite())
        {
            return Err("UV stage domain".into());
        }
        let old_u = self.moments(s, old)?.0;
        let mid_old = self.moments(s, mid)?.0;
        let rays = self.rays(mid)?;
        let wn = rays.iter().map(|r| r.2).sum::<f64>();
        let source_n = self.source_rate(mid.a) * dt;
        let nq = self.q.len();
        let mut emitted = 0.;
        let mut abs = 0.;
        let mut an = 0.;
        let mut n = s.n.clone();
        for (j, (r, _, w)) in rays.iter().enumerate() {
            let mut b = vec![0.; nq];
            for &(e, weight) in &self.source {
                let q = e / r;
                let k = self.q.partition_point(|x| *x <= q);
                if k == 0 || k >= nq {
                    return Err("UV source grid outside".into());
                }
                let t = (q - self.q[k - 1]) / (self.q[k] - self.q[k - 1]);
                let v = source_n * w / wn * weight;
                b[k - 1] += v * (1. - t);
                b[k] += v * t;
            }
            for k in 0..nq {
                let i = j * nq + k;
                let e = r * self.q[k];
                let tau = C
                    * dt
                    * (0..3)
                        .map(|a| gas.absorbers_m3[a] * sigma(e, a))
                        .sum::<f64>();
                let lose = -(-tau).exp_m1();
                let gain = if tau == 0. { 1. } else { lose / tau };
                let bg = if tau < 1e-4 {
                    tau * (0.5 - tau / 6. + tau * tau / 24. - tau * tau * tau / 120.)
                } else {
                    1. - gain
                };
                let removed = n[i] * lose + b[k] * bg;
                n[i] = n[i] * (-tau).exp() + b[k] * gain;
                emitted += b[k] * e;
                abs += removed * e;
                an += removed;
            }
        }
        s.n = n;
        s.reservoir += abs - emitted;
        s.emitted += emitted;
        s.absorbed += abs;
        s.births += source_n;
        s.absorbed_n += an;
        let mid_new = self.moments(s, mid)?.0;
        let end_u = self.moments(s, end)?.0;
        s.work += (old_u - mid_old) + (mid_new - end_u);
        let def = (end_u + s.reservoir + s.work).abs();
        if def > 2e-10 * s.emitted.max(1.)
            || (s.n.iter().sum::<f64>() + s.absorbed_n - s.births).abs() > 2e-10 * s.births.max(1.)
        {
            return Err("UV energy/number ledger".into());
        }
        Ok(())
    }
}
