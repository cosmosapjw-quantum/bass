//! Linear homogeneous Bianchi-I collisionless memory, orthonormal STF basis.
//! All densities returned as a^4 rho / rho_crit0, with mass/temperature in eV.
//! The normalization is the species' massless a^4 density in the same units.
use super::sphere::gauss_legendre;
#[derive(Clone, Debug)]
pub struct FermiMemory {
    mass_ev: f64,
    temperature_ev: f64,
    y: Vec<f64>,
    weights: Vec<f64>,
    norm: f64,
}
#[derive(Clone, Debug)]
pub struct MemoryResponse {
    pub rho_a4: f64,
    pub pressure_a4: f64,
    pub chi_a4: f64,
    pub dchi_a4: f64,
    pub stress_a4: [f64; 5],
    pub preferred: [f64; 5],
    pub memory_energy_a4: f64,
    pub memory_dissipation_a4: f64,
}
impl FermiMemory {
    pub fn new(
        mass_ev: f64,
        temperature_ev: f64,
        omega_rel: f64,
        n: usize,
    ) -> Result<Self, String> {
        if !mass_ev.is_finite()
            || mass_ev < 0.
            || !temperature_ev.is_finite()
            || temperature_ev <= 0.
            || !omega_rel.is_finite()
            || omega_rel <= 0.
            || !(16..=1024).contains(&n)
        {
            return Err("massive memory domain".into());
        }
        let (x, w) = gauss_legendre(n);
        let y: Vec<_> = x.iter().map(|x| 30. * (x + 1.)).collect();
        let weights: Vec<_> = w.iter().map(|w| 30. * w).collect();
        let norm = omega_rel
            / y.iter()
                .zip(&weights)
                .map(|(y, w)| w * y.powi(3) / (1. + y.exp()))
                .sum::<f64>();
        Ok(Self {
            mass_ev,
            temperature_ev,
            y,
            weights,
            norm,
        })
    }
    pub fn nodes(&self) -> &[f64] {
        &self.y
    }
    pub fn response(
        &self,
        a: f64,
        beta: [f64; 5],
        memory: &[[f64; 5]],
    ) -> Result<MemoryResponse, String> {
        if !a.is_finite()
            || a <= 0.
            || memory.len() != self.y.len()
            || !beta
                .iter()
                .chain(memory.iter().flatten())
                .all(|x| x.is_finite())
        {
            return Err("memory input".into());
        }
        let x = a * self.mass_ev / self.temperature_ev;
        let mut r = MemoryResponse {
            rho_a4: 0.,
            pressure_a4: 0.,
            chi_a4: 0.,
            dchi_a4: 0.,
            stress_a4: [0.; 5],
            preferred: [0.; 5],
            memory_energy_a4: 0.,
            memory_dissipation_a4: 0.,
        };
        for ((&y, &w), j) in self.y.iter().zip(&self.weights).zip(memory) {
            let e = y.hypot(x);
            let f = 1. / (1. + y.exp());
            let ww = w * self.norm;
            r.rho_a4 += ww * y * y * e * f;
            r.pressure_a4 += ww * y.powi(4) * f / (3. * e);
            let chi = 2. / 15. * ww * y.powi(5) * f * (1. - f) / e;
            let dc = -chi * (x / e).powi(2);
            r.chi_a4 += chi;
            r.dchi_a4 += dc;
            for k in 0..5 {
                let v = beta[k] - j[k];
                r.stress_a4[k] -= chi * v;
                r.preferred[k] += chi * j[k];
                r.memory_energy_a4 += chi * v * v;
                r.memory_dissipation_a4 -= dc * v * v;
            }
        }
        if !r.chi_a4.is_finite()
            || r.chi_a4 <= 0.
            || ![
                r.rho_a4,
                r.pressure_a4,
                r.dchi_a4,
                r.memory_energy_a4,
                r.memory_dissipation_a4,
            ]
            .iter()
            .chain(r.stress_a4.iter())
            .all(|v| v.is_finite())
        {
            return Err("memory quadrature nonfinite".into());
        }
        for k in 0..5 {
            r.preferred[k] /= r.chi_a4;
        }
        Ok(r)
    }
}
