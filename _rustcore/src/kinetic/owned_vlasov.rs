//! Research-only exact represented collisionless Bianchi I matter and geometry.
//! Densities divided by present critical energy density; h=H/H0.
use super::{
    lie_history::RayNode,
    memory_mixture::{stf_components, stf_matrix},
    radiation_feedback::advance_mixture,
    sphere::{gauss_legendre, SphereGrid},
};
use nalgebra::{Matrix3, Vector3};
const OG: f64 = 5.4437488671046486e-5;
const ON: f64 = 3.7562511328953514e-5;
const OM: f64 = 0.315;
const OL: f64 = 0.684908;
const T: f64 = 0.00016763891604963858;
#[derive(Clone, Debug)]
struct Particle {
    q: Vector3<f64>,
    w: f64,
    m: f64,
    photon: bool,
}
#[derive(Clone, Debug)]
pub struct OwnedModel {
    particles: Vec<Particle>,
    cold: f64,
}
#[derive(Clone, Debug)]
pub struct OwnedState {
    pub a: f64,
    pub h: f64,
    pub s: [f64; 5],
    pub f: Matrix3<f64>,
}
#[derive(Clone, Debug)]
pub struct Matter {
    pub rho: f64,
    pub pressure: Matrix3<f64>,
    pub photon_rho: f64,
}
fn rows(m: Matrix3<f64>) -> [[f64; 3]; 3] {
    std::array::from_fn(|i| std::array::from_fn(|j| m[(i, j)]))
}
impl OwnedModel {
    pub fn new(eps: f64, nr: usize, nt: usize, np: usize) -> Result<Self, String> {
        if !eps.is_finite() || eps.abs() > 0.1 || nr < 16 || nt < 4 || np < 8 {
            return Err("owner quadrature domain".into());
        }
        let grid = SphereGrid::new(nt, np);
        let (xx, ww) = gauss_legendre(nr);
        let ys: Vec<_> = xx.iter().map(|x| 30. * (1. + x)).collect();
        let norm = ys
            .iter()
            .zip(&ww)
            .map(|(&y, &w)| 30. * w * y.powi(3) / (1. + y.exp()))
            .sum::<f64>();
        let mut p = Vec::new();
        let mut cold = OM + ON;
        for (&mass, j) in [0.001, 0.05]
            .iter()
            .zip([[0., 1., 0., 0., 0.], [0., 0., 0.6, 0.8, 0.]])
        {
            let j = stf_matrix(j);
            let m = mass / T;
            let nr0 = ys
                .iter()
                .zip(&ww)
                .map(|(&y, &w)| 30. * w * y * y * y.hypot(m) / (1. + y.exp()))
                .sum::<f64>();
            cold -= ON / 2. * nr0 / norm;
            for (v, &w) in grid.ehat.chunks_exact(3).zip(&grid.w) {
                let n = Vector3::from_column_slice(v);
                let def = (-eps * n.dot(&(j * n))).exp();
                for (&y, &wr) in ys.iter().zip(&ww) {
                    let wt = ON / 2. * 30. * wr * y * y / (1. + (y * def).exp()) / norm * w
                        / (4. * std::f64::consts::PI);
                    p.push(Particle {
                        q: y * n,
                        w: wt,
                        m,
                        photon: false,
                    });
                }
            }
        }
        for (v, &w) in grid.ehat.chunks_exact(3).zip(&grid.w) {
            p.push(Particle {
                q: Vector3::from_column_slice(v),
                w: OG * w / (4. * std::f64::consts::PI),
                m: 0.,
                photon: true,
            });
        }
        if cold <= 0. {
            return Err("owner cold density".into());
        }
        Ok(Self { particles: p, cold })
    }
    pub fn matter(&self, a: f64, f: &Matrix3<f64>) -> Result<Matter, String> {
        self.matter_impl(a, f, true)
    }
    pub fn matter_without_photons(&self, a: f64, f: &Matrix3<f64>) -> Result<Matter, String> {
        self.matter_impl(a, f, false)
    }
    fn matter_impl(
        &self,
        a: f64,
        f: &Matrix3<f64>,
        include_photons: bool,
    ) -> Result<Matter, String> {
        if !a.is_finite()
            || a <= 0.
            || !f.iter().all(|v| v.is_finite())
            || (f.determinant() - 1.).abs() > 1e-7
        {
            return Err("owner coframe domain".into());
        }
        let inv = f.try_inverse().ok_or("singular coframe")?.transpose();
        let mut rho = self.cold * a;
        let mut pressure = Matrix3::zeros();
        let mut photon = 0.;
        for p in &self.particles {
            if p.photon && !include_photons {
                continue;
            }
            let v = inv * p.q;
            let e = v.norm().hypot(a * p.m);
            rho += p.w * e;
            pressure += (p.w / e) * (v * v.transpose());
            if p.photon {
                photon += p.w * e;
            }
        }
        let a4 = a.powi(4);
        Ok(Matter {
            rho: rho / a4,
            pressure: pressure / a4,
            photon_rho: photon / a4,
        })
    }
    pub fn initial(&self, a: f64, s: [f64; 5]) -> Result<OwnedState, String> {
        let f = Matrix3::identity();
        let m = self.matter(a, &f)?;
        let den = 1. - s.iter().map(|v| v * v).sum::<f64>() / 6.;
        if den <= 0. || !den.is_finite() {
            return Err("owner Gauss domain".into());
        }
        Ok(OwnedState {
            a,
            h: ((m.rho + OL) / den).sqrt(),
            s,
            f,
        })
    }
    pub fn constraint(&self, s: &OwnedState) -> Result<f64, String> {
        let m = self.matter(s.a, &s.f)?;
        Ok(1. - s.s.iter().map(|v| v * v).sum::<f64>() / 6. - (m.rho + OL) / s.h.powi(2))
    }
    fn node(&self, s: &OwnedState) -> Result<RayNode, String> {
        if !s.h.is_finite() || s.h <= 0. || !s.s.iter().all(|v| v.is_finite()) {
            return Err("owner expansion domain".into());
        }
        let m = self.matter(s.a, &s.f)?;
        Ok(RayNode {
            shear: rows(stf_matrix(s.s)),
            hubble_ratio: s.h,
            omega_lambda: OL / s.h.powi(2),
            omega_radiation: m.photon_rho / s.h.powi(2),
            ..Default::default()
        })
    }
    pub fn step(&self, s: &OwnedState, du: f64) -> Result<OwnedState, String> {
        if !du.is_finite() || du <= 0. || du > 0.1 {
            return Err("owner step domain".into());
        }
        let n = self.node(s)?;
        let m = self.matter(s.a, &s.f)?;
        let mid = advance_mixture(
            &n,
            &n,
            du / 2.,
            m.rho / s.h.powi(2),
            rows(m.pressure / m.rho),
            [0.; 3],
        )?;
        let sm = stf_components(Matrix3::from_fn(|i, j| mid.shear[i][j]));
        let half = OwnedState {
            a: s.a * (du / 2.).exp(),
            h: mid.hubble_ratio,
            s: sm,
            f: (stf_matrix(s.s) * (du / 2.)).exp() * s.f,
        };
        let hm = self.matter(half.a, &half.f)?;
        let at = self.node(&half)?;
        let out = advance_mixture(
            &n,
            &at,
            du,
            hm.rho / half.h.powi(2),
            rows(hm.pressure / hm.rho),
            [0.; 3],
        )?;
        Ok(OwnedState {
            a: s.a * du.exp(),
            h: out.hubble_ratio,
            s: stf_components(Matrix3::from_fn(|i, j| out.shear[i][j])),
            f: (stf_matrix(sm) * du).exp() * s.f,
        })
    }
}
