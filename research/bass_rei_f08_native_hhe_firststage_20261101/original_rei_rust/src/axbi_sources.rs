//! Frozen conditional MD14 comoving emissivity and truncated stellar blackbody.
//!
//! Sources and scope are recorded in AX01 SCENARIO_LOCK. The analytic high-z
//! continuation and 50,000 K blackbody are explicit model choices, not empirical
//! calibration. This module injects photon numbers; it does not force Gamma,
//! add photoheat, absorb photons, or create recombination escape photons.
use crate::{ForwardError, HHeModel, MPC_CM};

pub const SOURCE_ID: &str = "MD14_Z002_FESC_BB50K_13P6_100_V1";
pub const ENERGY_SUPPORT_EV: [f64; 2] = [13.6, 100.0];
pub const REDSHIFT_SUPPORT: [f64; 2] = [4.0, 20.0];
#[derive(Clone, Copy, Debug)]
pub struct SpectralCell {
    pub lower_ev: f64,
    pub upper_ev: f64,
    /// Cell energy moment divided by its photon-number moment, not midpoint E.
    pub energy_ev: f64,
    pub photon_fraction: f64,
}
#[derive(Clone, Copy, Debug)]
pub struct AngularCell {
    pub mu: f64,
    /// Gauss-Legendre weight/2; total source is already 4pi-integrated.
    pub count_fraction: f64,
}
#[derive(Clone, Copy, Debug)]
pub struct EmissionRate {
    pub comoving_photons_per_s_cmpc3: f64,
    pub proper_photons_cm3_s: f64,
    pub per_h_s: f64,
}
#[derive(Clone, Debug)]
pub struct AxbiSource {
    pub spectral_cells: Vec<SpectralCell>,
    pub angular_cells: Vec<AngularCell>,
    pub normalization_relative_residual: f64,
    pub omitted_blackbody_tail_photon_fraction: f64,
    n_h0_cm3: f64,
    escape_fraction: f64,
}
fn invalid() -> ForwardError {
    ForwardError::InvalidInput("AXBI_SOURCE_DOMAIN_OR_QUADRATURE")
}
fn positive(x: f64) -> Result<f64, ForwardError> {
    if x.is_normal() && x > 0.0 {
        Ok(x)
    } else {
        Err(invalid())
    }
}
fn shape(energy_ev: f64) -> f64 {
    let c = HHeModel::controlled_fixture();
    let kt = c.kb_erg_k / c.ev_erg * 50000.0;
    energy_ev * energy_ev / (energy_ev / kt).exp_m1()
}
fn simpson(lo: f64, hi: f64, n: usize, energy_moment: bool) -> f64 {
    let step = (hi - lo) / n as f64;
    let mut sum = 0.0;
    for i in 0..=n {
        let e = lo + step * i as f64;
        let f = shape(e) * if energy_moment { e } else { 1.0 };
        sum += f * if i == 0 || i == n {
            1.0
        } else if i % 2 == 0 {
            2.0
        } else {
            4.0
        };
    }
    sum * step / 3.0
}
fn angular(n: usize) -> Result<Vec<AngularCell>, ForwardError> {
    if ![8, 16, 32].contains(&n) {
        return Err(invalid());
    }
    let mut out = vec![
        AngularCell {
            mu: 0.0,
            count_fraction: 0.0
        };
        n
    ];
    for i in 0..n / 2 {
        let mut x = (std::f64::consts::PI * (i as f64 + 0.75) / (n as f64 + 0.5)).cos();
        let mut converged = false;
        for _ in 0..32 {
            let (p, pm) = legendre(n, x);
            let d = n as f64 * (x * p - pm) / (x * x - 1.0);
            let next = x - p / d;
            if (next - x).abs() <= 2.0 * f64::EPSILON {
                x = next;
                converged = true;
                break;
            }
            x = next;
        }
        if !converged {
            return Err(invalid());
        }
        let (p, pm) = legendre(n, x);
        let d = n as f64 * (x * p - pm) / (x * x - 1.0);
        let weight = positive(1.0 / ((1.0 - x * x) * d * d))?;
        out[i] = AngularCell {
            mu: -x,
            count_fraction: weight,
        };
        out[n - 1 - i] = AngularCell {
            mu: x,
            count_fraction: weight,
        };
    }
    Ok(out)
}
fn legendre(n: usize, x: f64) -> (f64, f64) {
    let (mut pm, mut p) = (1.0, x);
    for k in 2..=n {
        let q = ((2 * k - 1) as f64 * x * p - (k - 1) as f64 * pm) / k as f64;
        pm = p;
        p = q;
    }
    (p, pm)
}
impl AxbiSource {
    /// Allowed source sensitivity fesc is explicit; baseline .2, variant .25.
    /// nH0 is the a=1 comoving hydrogen density in cm^-3, not an endpoint proper
    /// density. Baseline cells_per_segment=16, n_mu=8; resolutions are numeric.
    pub fn new(
        n_h0_cm3: f64,
        escape_fraction: f64,
        cells_per_segment: usize,
        n_mu: usize,
    ) -> Result<Self, ForwardError> {
        positive(n_h0_cm3)?;
        positive(escape_fraction)?;
        if escape_fraction > 1.0 || !(1..=1024).contains(&cells_per_segment) {
            return Err(invalid());
        }
        let edges = [13.6_f64, 24.59, 54.42, 100.0];
        let mut integrals = Vec::new();
        for segment in edges.windows(2) {
            for j in 0..cells_per_segment {
                let lo = if j == 0 {
                    segment[0]
                } else {
                    segment[0] * (segment[1] / segment[0]).powf(j as f64 / cells_per_segment as f64)
                };
                let hi = if j + 1 == cells_per_segment {
                    segment[1]
                } else {
                    segment[0]
                        * (segment[1] / segment[0]).powf((j + 1) as f64 / cells_per_segment as f64)
                };
                let count = positive(simpson(lo, hi, 32, false))?;
                let energy = positive(simpson(lo, hi, 32, true))?;
                integrals.push((lo, hi, count, energy));
            }
        }
        let normalization = positive(integrals.iter().map(|x| x.2).sum())?;
        let reference = positive(simpson(edges[0], edges[3], 4096, false))?;
        let normalization_relative_residual = (normalization / reference - 1.0).abs();
        if normalization_relative_residual > 1e-7 {
            return Err(invalid());
        }
        let spectral_cells = integrals
            .into_iter()
            .map(|(lower_ev, upper_ev, count, energy)| SpectralCell {
                lower_ev,
                upper_ev,
                energy_ev: energy / count,
                photon_fraction: count / normalization,
            })
            .collect();
        let tail = positive(simpson(100.0, 500.0, 4096, false))?;
        Ok(Self {
            spectral_cells,
            angular_cells: angular(n_mu)?,
            normalization_relative_residual,
            omitted_blackbody_tail_photon_fraction: tail / (reference + tail),
            n_h0_cm3,
            escape_fraction,
        })
    }
    /// Continuous total emissivity. No year conversion is applied: MD14 psi is
    /// Msun/yr/cMpc^3 and the yield is photons/s per (Msun/yr).
    pub fn at_redshift(&self, zbar: f64) -> Result<EmissionRate, ForwardError> {
        if !zbar.is_finite() || !(4.0..=20.0).contains(&zbar) {
            return Err(invalid());
        }
        let zp = 1.0 + zbar;
        let sfr = 0.015 * zp.powf(2.7) / (1.0 + (zp / 2.9).powf(5.6));
        let log_yield = 1.0 / (0.00038 * 0.002_f64.powf(0.227) + 0.01858) - 2.55_f64.log10();
        let comoving = positive(self.escape_fraction * 10_f64.powf(log_yield) * sfr)?;
        let per_volume = positive(comoving / MPC_CM.powi(3))?;
        Ok(EmissionRate {
            comoving_photons_per_s_cmpc3: comoving,
            proper_photons_cm3_s: positive(per_volume * zp.powi(3))?,
            per_h_s: positive(per_volume / self.n_h0_cm3)?,
        })
    }
    /// Source-only derivative for one discrete photon population, H^-1 s^-1.
    /// Driver time integration and photon evolution remain separate owners.
    pub fn cell_per_h_s(
        &self,
        zbar: f64,
        energy_index: usize,
        angle_index: usize,
    ) -> Result<f64, ForwardError> {
        let e = self.spectral_cells.get(energy_index).ok_or_else(invalid)?;
        let a = self.angular_cells.get(angle_index).ok_or_else(invalid)?;
        positive(self.at_redshift(zbar)?.per_h_s * e.photon_fraction * a.count_fraction)
    }
}
