//! Compatibility with monolithic_model_b2a.py blob 3d806e1c... only.
//! Table-domain rejection is the documented intentional API restriction.
use crate::{ForwardError, GammaSpecies, GroupParams, State};

pub const C_LIGHT: f64 = 2.99792458e10;
pub const MPC_CM: f64 = 3.085677581491367e24;

#[derive(Debug, Clone)]
pub struct PchipTable {
    knots: Vec<f64>,
    coeffs: [Vec<f64>; 4],
}
impl PchipTable {
    /// Coefficients are degree-major: cubic, quadratic, linear, constant.
    /// No coefficient fitting, extrapolation, clipping, or FMA is performed.
    pub fn new(knots: Vec<f64>, coeffs: [Vec<f64>; 4]) -> Result<Self, ForwardError> {
        if knots.len() < 2
            || knots.iter().any(|x| !x.is_finite())
            || knots.windows(2).any(|w| w[0] >= w[1])
            || coeffs
                .iter()
                .any(|c| c.len() != knots.len() - 1 || c.iter().any(|x| !x.is_finite()))
        {
            return Err(ForwardError::InvalidInput("BAD_TABLE"));
        }
        Ok(Self { knots, coeffs })
    }
}

pub fn pchip_eval(table: &PchipTable, x: f64) -> Result<f64, ForwardError> {
    if !x.is_finite() {
        return Err(ForwardError::InvalidInput("NONFINITE_X"));
    }
    let lower = table.knots[0];
    let upper = table.knots[table.knots.len() - 1];
    if x < lower || x > upper {
        return Err(ForwardError::OutsideTableDomain { x, lower, upper });
    }
    let i = (table.knots.partition_point(|k| *k <= x) - 1).min(table.knots.len() - 2);
    let dx = x - table.knots[i];
    let c = &table.coeffs;
    Ok(((c[0][i] * dx + c[1][i]) * dx + c[2][i]) * dx + c[3][i])
}

/// Rust f64 exponential semantics are canonical: representable positive
/// subnormals remain nonzero; sufficiently small inputs underflow to zero.
/// NaN and infinities follow the operations below without clipping or FTZ.
pub fn transform_z_to_y(z: &[f64; 9]) -> State {
    let logits = [0.0, z[5], z[6]];
    let helium = if logits.iter().any(|v| v.is_nan()) {
        [f64::NAN; 3]
    } else {
        let m = logits.iter().copied().fold(f64::NEG_INFINITY, f64::max);
        let e = logits.map(|v| (v - m).exp());
        let sum = e[0] + e[1] + e[2];
        e.map(|v| v / sum)
    };
    State {
        n_comoving_per_cmpc3: [z[0].exp(), z[1].exp(), z[2].exp(), z[3].exp()],
        x_hii: 1.0 / (1.0 + (-z[4]).exp()),
        helium,
        u_erg_per_cm3: z[7].exp(),
        gamma_hi_per_s: z[8].exp(),
    }
}

/// cMpc^-1. The effective HI lowgroup owner must not be counted twice.
#[allow(non_snake_case)]
pub fn opacity_cMpc_inv(state: &State, p: &GroupParams) -> Result<[f64; 4], ForwardError> {
    let x = (state.gamma_hi_per_s / 1.0e-12).ln();
    let low0 = pchip_eval(&p.lowgroup_log_opacity[0], x)?.exp();
    let low1 = pchip_eval(&p.lowgroup_log_opacity[1], x)?.exp();
    let n_hi = p.n_h_proper_per_cm3 * (1.0 - state.x_hii);
    let n_hei = p.n_he_proper_per_cm3 * state.helium[0];
    let n_heii = p.n_he_proper_per_cm3 * state.helium[1];
    let factor = MPC_CM / (1.0 + p.redshift);
    let hi = p.sigma_hi_cm2.map(|s| n_hi * s * factor);
    let hei = p.sigma_hei_cm2.map(|s| n_hei * s * factor);
    let heii = p.sigma_heii_cm2.map(|s| n_heii * s * factor);
    Ok([
        low0,
        low1 + hei[1],
        hi[2] + hei[2],
        hi[3] + hei[3] + heii[3],
    ])
}

/// Comoving count per cMpc^3 per second. Scalar emissivity broadcasting is an
/// adapter operation: pass [e; 4], not a newly normalized spectral model.
pub fn photon_rates(
    state: &State,
    emissivity: &[f64; 4],
    p: &GroupParams,
) -> Result<[f64; 4], ForwardError> {
    let kappa = opacity_cMpc_inv(state, p)?;
    let a = kappa.map(|k| C_LIGHT * (1.0 + p.redshift) / MPC_CM * k);
    let r = p.redshift_coeff.map(|v| p.hubble_per_s * v);
    let n = state.n_comoving_per_cmpc3;
    let mut rhs =
        std::array::from_fn(|g| emissivity[g] * p.source_fraction[g] - (a[g] + r[g]) * n[g]);
    for g in 0..3 {
        rhs[g] += r[g + 1] * n[g + 1];
    }
    Ok(rhs)
}

/// s^-1. N alone is converted from comoving density with (1+z)^3 once.
/// This function does not query an opacity table or the GammaHI state field.
pub fn gamma_species(state: &State, p: &GroupParams) -> GammaSpecies {
    let prefactor = C_LIGHT * (1.0 + p.redshift).powi(3) / MPC_CM.powi(3);
    let hi: [f64; 4] =
        std::array::from_fn(|g| prefactor * p.sigma_hi_cm2[g] * state.n_comoving_per_cmpc3[g]);
    let hei: [f64; 4] =
        std::array::from_fn(|g| prefactor * p.sigma_hei_cm2[g] * state.n_comoving_per_cmpc3[g]);
    let heii: [f64; 4] =
        std::array::from_fn(|g| prefactor * p.sigma_heii_cm2[g] * state.n_comoving_per_cmpc3[g]);
    GammaSpecies {
        hi_per_s: hi.iter().sum(),
        hei_per_s: hei.iter().sum(),
        heii_per_s: heii.iter().sum(),
        group_hi_per_s: hi,
    }
}
