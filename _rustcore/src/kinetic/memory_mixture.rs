//! Opt-in linear matter adapter for the original Bianchi geometry stage.
//! Densities in present critical-density units; anisotropy first-order.
//! No production owner selection or finite-amplitude Vlasov closure.
use super::{
    lie_history::RayNode, massive_memory::FermiMemory, radiation_feedback::advance_mixture,
};
use nalgebra::Matrix3;
#[derive(Clone, Debug)]
pub struct MemorySpecies {
    pub provider: FermiMemory,
    pub memory: Vec<[f64; 5]>,
}
#[derive(Clone, Debug)]
pub struct MemoryMixture {
    species: Vec<MemorySpecies>,
    omega_gamma0: f64,
    omega_cold0: f64,
    omega_lambda0: f64,
}
#[derive(Clone, Debug)]
pub struct MixtureMoments {
    pub h_ratio: f64,
    pub omega: f64,
    pub omega_gamma: f64,
    pub omega_lambda: f64,
    pub dln_h: f64,
    pub pressure_fraction: [[f64; 3]; 3],
    pub pi: [f64; 5],
    pub memory_energy_a4: f64,
    pub memory_dissipation_a4: f64,
}
pub fn stf_matrix(v: [f64; 5]) -> Matrix3<f64> {
    let r = 1. / 2_f64.sqrt();
    let t = 1. / 6_f64.sqrt();
    Matrix3::new(
        r * v[0] - t * v[1],
        r * v[2],
        r * v[3],
        r * v[2],
        -r * v[0] - t * v[1],
        r * v[4],
        r * v[3],
        r * v[4],
        2. * t * v[1],
    )
}
pub fn stf_components(m: Matrix3<f64>) -> [f64; 5] {
    let r = 1. / 2_f64.sqrt();
    let t = 1. / 6_f64.sqrt();
    [
        r * (m[(0, 0)] - m[(1, 1)]),
        t * (2. * m[(2, 2)] - m[(0, 0)] - m[(1, 1)]),
        r * (m[(0, 1)] + m[(1, 0)]),
        r * (m[(0, 2)] + m[(2, 0)]),
        r * (m[(1, 2)] + m[(2, 1)]),
    ]
}
fn rows(m: Matrix3<f64>) -> [[f64; 3]; 3] {
    std::array::from_fn(|i| std::array::from_fn(|j| m[(i, j)]))
}
impl MemoryMixture {
    pub fn new(
        species: Vec<MemorySpecies>,
        omega_gamma0: f64,
        omega_cold0: f64,
        omega_lambda0: f64,
    ) -> Result<Self, String> {
        if species.is_empty()
            || ![omega_gamma0, omega_cold0, omega_lambda0]
                .iter()
                .all(|x| x.is_finite() && *x >= 0.)
            || omega_gamma0 == 0.
        {
            return Err("memory mixture domain".into());
        }
        for s in &species {
            s.provider.response(1., [0.; 5], &s.memory)?;
        }
        Ok(Self {
            species,
            omega_gamma0,
            omega_cold0,
            omega_lambda0,
        })
    }
    pub fn moments(
        &self,
        a: f64,
        beta: [f64; 5],
        photon_a: [f64; 5],
    ) -> Result<MixtureMoments, String> {
        if !a.is_finite() || a <= 0. || !beta.iter().chain(photon_a.iter()).all(|x| x.is_finite()) {
            return Err("mixture stage domain".into());
        }
        let mut den = self.omega_cold0 * a + self.omega_gamma0;
        let mut p = self.omega_gamma0 / 3.;
        let mut pi = [0.; 5];
        let mut mem = 0.;
        let mut loss = 0.;
        for sp in &self.species {
            let s = sp.provider.response(a, beta, &sp.memory)?;
            den += s.rho_a4;
            p += s.pressure_a4;
            mem += s.memory_energy_a4;
            loss += s.memory_dissipation_a4;
            for k in 0..5 {
                pi[k] += s.stress_a4[k];
            }
        }
        let tot = den + self.omega_lambda0 * a.powi(4);
        let mut pf = stf_matrix(std::array::from_fn(|k| {
            pi[k] + 2. / 15. * self.omega_gamma0 * photon_a[k]
        }));
        pf += Matrix3::identity() * p;
        pf /= den;
        let m = MixtureMoments {
            h_ratio: (tot / a.powi(4)).sqrt(),
            omega: den / tot,
            omega_gamma: self.omega_gamma0 / tot,
            omega_lambda: self.omega_lambda0 * a.powi(4) / tot,
            dln_h: -1.5 * (den + p) / tot,
            pressure_fraction: rows(pf),
            pi: pi.map(|x| x / tot),
            memory_energy_a4: mem,
            memory_dissipation_a4: loss,
        };
        if !m.h_ratio.is_finite() || m.h_ratio <= 0. || !pf.iter().all(|v| v.is_finite()) {
            return Err("mixture nonfinite".into());
        }
        Ok(m)
    }
    /// Evaluate the existing nonlinear geometry stage at a first-order matter
    /// state with prescribed isotropic H. Keeps the native cubic shear term;
    /// caller must keep perturbations small, not use this as nonlinear closure.
    pub fn shear_rhs(
        &self,
        a: f64,
        s: [f64; 5],
        beta: [f64; 5],
        photon_a: [f64; 5],
    ) -> Result<[f64; 5], String> {
        let m = self.moments(a, beta, photon_a)?;
        if !s.iter().all(|x| x.is_finite()) || s.iter().map(|x| x * x).sum::<f64>() > 1e-4 {
            return Err("linear mixture shear domain".into());
        }
        let at = RayNode {
            shear: rows(stf_matrix(s)),
            hubble_ratio: m.h_ratio,
            omega_lambda: m.omega_lambda,
            omega_radiation: m.omega_gamma,
            ..Default::default()
        };
        let dt = 0.001;
        let out = advance_mixture(&at, &at, dt, m.omega, m.pressure_fraction, [0.; 3])?;
        let d = (Matrix3::from_fn(|i, j| out.shear[i][j]) - stf_matrix(s)) / dt;
        Ok(stf_components(d))
    }
}
pub fn commutator_invariant(s: [f64; 5], p: [f64; 5]) -> f64 {
    let s = stf_matrix(s);
    let p = stf_matrix(p);
    let c = s * p - p * s;
    0.5 * c.norm_squared()
}
