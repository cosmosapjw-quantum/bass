//! Positive bolometric collisionless cooling radiation on fixed canonical rays.
//! Energy per H, no photon-number or spectral absorption claim.
use super::{owned_vlasov::OwnedState, sphere::SphereGrid};
use nalgebra::{Matrix3, Vector3};
pub struct CoolingRays {
    a0: f64,
    dir: Vec<Vector3<f64>>,
    weights: Vec<f64>,
}
impl CoolingRays {
    pub fn new(a0: f64, nt: usize, np: usize) -> Result<Self, String> {
        if !a0.is_finite() || a0 <= 0. || nt < 4 || np < 8 || nt % 2 != 0 || np % 2 != 0 {
            return Err("cooling grid".into());
        }
        let g = SphereGrid::new(nt, np);
        Ok(Self {
            a0,
            dir: g
                .ehat
                .chunks_exact(3)
                .map(Vector3::from_column_slice)
                .collect(),
            weights: g
                .w
                .iter()
                .map(|w| w / (4. * std::f64::consts::PI))
                .collect(),
        })
    }
    pub fn empty(&self) -> Vec<f64> {
        vec![0.; self.dir.len()]
    }
    fn rays(&self, g: &OwnedState) -> Result<Vec<(f64, Vector3<f64>, f64)>, String> {
        if !g.a.is_finite()
            || g.a <= 0.
            || !g.f.iter().all(|x| x.is_finite())
            || (g.f.determinant() - 1.).abs() > 1e-7
        {
            return Err("cooling geometry".into());
        }
        let inv = g.f.try_inverse().ok_or("cooling inverse")?.transpose();
        Ok(self
            .dir
            .iter()
            .zip(&self.weights)
            .map(|(n, w)| {
                let p = inv * n;
                let d = p.norm();
                (self.a0 / g.a * d, p / d, w / d.powi(3))
            })
            .collect())
    }
    fn valid(&self, s: &[f64]) -> bool {
        s.len() == self.dir.len() && s.iter().all(|x| x.is_finite() && *x >= 0.)
    }
    pub fn moments(&self, s: &[f64], g: &OwnedState) -> Result<(f64, Matrix3<f64>), String> {
        if !self.valid(s) {
            return Err("cooling stock".into());
        }
        let mut u = 0.;
        let mut p = Matrix3::zeros();
        for (&q, (r, n, _)) in s.iter().zip(self.rays(g)?) {
            let e = q * r;
            u += e;
            p += e * n * n.transpose();
        }
        Ok((u, p))
    }
    pub fn advance(
        &self,
        s: &[f64],
        old: &OwnedState,
        mid: &OwnedState,
        end: &OwnedState,
        birth: f64,
    ) -> Result<(Vec<f64>, f64), String> {
        if !self.valid(s) || !birth.is_finite() || birth < 0. || old.a > mid.a || mid.a > end.a {
            return Err("cooling stage".into());
        }
        let a = self.rays(old)?;
        let m = self.rays(mid)?;
        let b = self.rays(end)?;
        let z = m.iter().map(|v| v.2).sum::<f64>();
        if z <= 0. || !z.is_finite() {
            return Err("cooling weights".into());
        }
        let mut out = s.to_vec();
        let mut work = 0.;
        for j in 0..s.len() {
            out[j] += birth * m[j].2 / (z * m[j].0);
            work += (a[j].0 - m[j].0) * s[j] + (m[j].0 - b[j].0) * out[j];
        }
        if !self.valid(&out) || !work.is_finite() {
            return Err("cooling result".into());
        }
        Ok((out, work))
    }
}

impl CoolingRays {
    fn valid_spectrum(&self, s: &[f64], edges: &[f64]) -> bool {
        edges.len() >= 2
            && edges[0] == 0.
            && *edges.last().unwrap() == f64::INFINITY
            && edges.windows(2).all(|w| w[0].is_finite() && w[1] > w[0])
            && s.len() == self.dir.len() * (edges.len() - 1)
            && s.iter().all(|v| v.is_finite() && *v >= 0.)
    }
    /// Energy per H in fixed reference-energy bands, evaluated at current coframe.
    pub fn spectral_energy(
        &self,
        s: &[f64],
        edges: &[f64],
        g: &OwnedState,
    ) -> Result<Vec<f64>, String> {
        if !self.valid_spectrum(s, edges) {
            return Err("cooling spectrum domain".into());
        }
        let n = edges.len() - 1;
        let mut out = vec![0.; n];
        for (j, (r, _, _)) in self.rays(g)?.iter().enumerate() {
            for k in 0..n {
                out[k] += s[j * n + k] * r;
            }
        }
        Ok(out)
    }
    /// Grey Gaunt free-free energy spectrum dU/dE ∝ exp(-E/kT).
    /// Energy only: no finite photon count in the zero-frequency band.
    pub fn advance_freefree(
        &self,
        s: &[f64],
        edges: &[f64],
        old: &OwnedState,
        mid: &OwnedState,
        end: &OwnedState,
        birth: f64,
        kt_ev: f64,
    ) -> Result<(Vec<f64>, f64), String> {
        if !self.valid_spectrum(s, edges)
            || !birth.is_finite()
            || birth < 0.
            || !kt_ev.is_finite()
            || kt_ev <= 0.
            || old.a > mid.a
            || mid.a > end.a
        {
            return Err("freefree spectrum domain".into());
        }
        let a = self.rays(old)?;
        let m = self.rays(mid)?;
        let b = self.rays(end)?;
        let z = m.iter().map(|v| v.2).sum::<f64>();
        if z <= 0. || !z.is_finite() {
            return Err("freefree weights".into());
        }
        let n = edges.len() - 1;
        let mut out = s.to_vec();
        let mut work = 0.;
        for j in 0..self.dir.len() {
            let q = birth * m[j].2 / (z * m[j].0);
            let fac = m[j].0 / kt_ev;
            for k in 0..n {
                let frac = (-fac * edges[k]).exp() * (-(-fac * (edges[k + 1] - edges[k])).exp_m1());
                let i = j * n + k;
                out[i] += q * frac;
                work += (a[j].0 - m[j].0) * s[i] + (m[j].0 - b[j].0) * out[i];
            }
        }
        if !self.valid_spectrum(&out, edges) || !work.is_finite() {
            return Err("freefree spectrum result".into());
        }
        Ok((out, work))
    }
}
