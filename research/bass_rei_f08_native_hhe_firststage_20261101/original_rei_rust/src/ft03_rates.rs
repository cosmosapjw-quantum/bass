//! Controlled FT03 Case A rates. These analytic fits are distinct from the raw
//! Grackle reference coefficients in `atomic_provider`.
use crate::ForwardError;

const KB: f64 = 1.380_649e-16;
const LAMBDA_K: [f64; 3] = [315_614.0, 570_670.0, 1_263_030.0];
const CI_A: [f64; 3] = [21.11, 32.38, 19.95];
const CI_P: [f64; 3] = [-1.089, -1.146, -1.089];
const CI_C: [f64; 3] = [0.354, 0.416, 0.553];
const CI_R: [f64; 3] = [0.874, 0.987, 0.735];
const CI_D: [f64; 3] = [1.101, 1.056, 1.275];

#[derive(Clone, Copy, Debug)]
pub struct Ft03Coefficients {
    pub alpha_rr_cm3_s: [f64; 3],
    pub log_slope: [f64; 3],
    pub log_slope_derivative: [f64; 3],
    pub rr_kinetic_erg_cm3_s: [f64; 3],
    pub beta_ci_cm3_s: [f64; 3],
    pub alpha_dr_cm3_s: [f64; 2],
    pub dr_energy_erg: [f64; 2],
}

pub fn ft03_coefficients(t: f64) -> Result<Ft03Coefficients, ForwardError> {
    if !t.is_finite() || !(30_000.0..=110_000.0).contains(&t) {
        return Err(ForwardError::InvalidInput("FT03_TEMPERATURE_DOMAIN"));
    }
    let mut alpha_rr = [0.0; 3];
    let mut g = [0.0; 3];
    let mut gp = [0.0; 3];
    let mut beta = [0.0; 3];
    for a in 0..3 {
        let l = LAMBDA_K[a] / t;
        if a == 1 {
            alpha_rr[a] = 3e-14 * l.powf(0.654);
            g[a] = -0.654;
        } else {
            let u = (l / 0.522).powf(0.470);
            let prefactor = if a == 2 { 2.0 } else { 1.0 };
            alpha_rr[a] = prefactor * 1.269e-13 * l.powf(1.503) / (1.0 + u).powf(1.923);
            g[a] = -1.503 + 1.923 * 0.470 * u / (1.0 + u);
            gp[a] = -1.923 * 0.470 * 0.470 * u / (1.0 + u).powi(2);
        }
        beta[a] = CI_A[a] * t.powf(-1.5) * (-l / 2.0).exp() * l.powf(CI_P[a])
            / (1.0 + (l / CI_C[a]).powf(CI_R[a])).powf(CI_D[a]);
    }
    let kinetic = std::array::from_fn(|a| KB * t * alpha_rr[a] * (1.5 + g[a]));
    let dr_a = 1.54e-9 * 11_605.0_f64.powf(1.5);
    let b1 = 40.496_643_948_336_62 * 11_605.0;
    let b2 = 8.099_328_789_667 * 11_605.0;
    let dr = [
        dr_a * t.powf(-1.5) * (-b1 / t).exp(),
        0.3 * dr_a * t.powf(-1.5) * (-(b1 + b2) / t).exp(),
    ];
    let energy = [KB * b1, KB * (b1 + b2)];
    if alpha_rr
        .iter()
        .chain(kinetic.iter())
        .chain(beta.iter())
        .chain(dr.iter())
        .chain(energy.iter())
        .any(|x| !x.is_finite() || *x < 0.0)
        || g.iter().chain(gp.iter()).any(|x| !x.is_finite())
    {
        return Err(ForwardError::InvalidInput("FT03_OVERFLOW"));
    }
    Ok(Ft03Coefficients {
        alpha_rr_cm3_s: alpha_rr,
        log_slope: g,
        log_slope_derivative: gp,
        rr_kinetic_erg_cm3_s: kinetic,
        beta_ci_cm3_s: beta,
        alpha_dr_cm3_s: dr,
        dr_energy_erg: energy,
    })
}
