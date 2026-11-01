//! Proper-time point chemistry and thermal ledger. No time integration.
//! Case A escape, clumping=1, primary-only externally specified photo rates.
//! Positive nonnormal input/intermediate arithmetic is rejected, not clipped.
//! The source CI floors/CE caps are the documented exception in igm_rates.
use crate::{igm_state::IgmGasState, ForwardError};
#[derive(Clone, Copy, Debug, Default)]
pub struct IgmPhotoInput {
    /// HI, HeI, HeII externally supplied ionizations per absorber per second.
    pub gamma_s: [f64; 3],
    /// HI, HeI, HeII heat power per absorber, NOT energy per event.
    /// Must vanish if the matching Gamma vanishes.
    pub heat_erg_per_absorber_s: [f64; 3],
}
#[derive(Clone, Copy, Debug, Default)]
pub struct IgmPointRhs {
    pub fraction_dt: [f64; 3],
    /// Chemical number-density derivatives: HI,HII,HeI,HeII,HeIII,e.
    pub species_chemical_cm3_s: [f64; 6],
    pub w_dt_erg_per_h_s: f64,
    pub temperature_dt_k_s: f64,
    pub photo_events_cm3_s: [f64; 3],
    pub ci_events_cm3_s: [f64; 3],
    pub rr_events_cm3_s: [f64; 3],
    pub dr_events_cm3_s: f64,
    pub ci_thermal_sink_erg_cm3_s: [f64; 3],
    pub rr_thermal_sink_erg_cm3_s: [f64; 3],
    pub dr_thermal_sink_erg_cm3_s: f64,
    pub ce_thermal_sink_erg_cm3_s: [f64; 3],
    pub freefree_thermal_sink_erg_cm3_s: f64,
    pub thermal_micro_erg_cm3_s: f64,
    pub binding_micro_erg_cm3_s: f64,
    pub escape_erg_cm3_s: f64,
    /// Signed INTO gas. CMB reservoir rate is its negative.
    pub cmb_to_gas_erg_cm3_s: f64,
    pub photo_input_erg_cm3_s: f64,
    pub expansion_work_erg_cm3_s: f64,
    pub ci_floor_events_cm3_s: [f64; 3],
    pub ce_cap_cooling_erg_cm3_s: [f64; 3],
    pub excluded_dr_cooling_erg_cm3_s: f64,
}

use crate::{igm_rates::igm_rates, rate_table::PreparedIgmRates, HHeModel};
// CODATA 2022: https://physics.nist.gov/cuu/pdf/wall_2022.pdf
// sigma_T and electron mass; a_rad = 4*sigma_SB/c.
// sigma_SB follows the exact SI kB,h,c blackbody expression (converted to cgs).
const SIGMA_T_CM2: f64 = 6.6524587051e-25;
const ELECTRON_MASS_G: f64 = 9.1093837139e-28;
const PLANCK_ERG_S: f64 = 6.62607015e-27;
fn invalid() -> ForwardError {
    ForwardError::InvalidInput("IGM_RHS_DOMAIN_OR_ARITHMETIC")
}
fn finite(x: f64) -> Result<f64, ForwardError> {
    if x == 0.0 || x.is_normal() {
        Ok(x)
    } else {
        Err(invalid())
    }
}
fn nonnegative(x: f64) -> Result<f64, ForwardError> {
    finite(x)?;
    if x >= 0.0 {
        Ok(x)
    } else {
        Err(invalid())
    }
}
fn mul(xs: &[f64]) -> Result<f64, ForwardError> {
    for &x in xs {
        nonnegative(x)?;
    }
    if xs.contains(&0.0) {
        return Ok(0.0);
    }
    let mut y = 1.0;
    for &x in xs {
        y *= x;
        if !y.is_normal() {
            return Err(invalid());
        }
    }
    Ok(y)
}
fn divide(x: f64, y: f64) -> Result<f64, ForwardError> {
    finite(x)?;
    if !y.is_normal() || y <= 0.0 {
        return Err(invalid());
    }
    let v = x / y;
    finite(v)?;
    if x != 0.0 && v == 0.0 {
        return Err(invalid());
    }
    Ok(v)
}
/// Immutable point evaluator. Errors return no partially updated state.
/// Admission uses the recovered EOS temperature strictly, not an originally
/// requested constructor temperature. Even sub-ulp endpoint reconstruction
/// outside 1..=1e6 K is rejected; no state/evaluation projection is performed.
/// `h` is nonnegative expansion s^-1; no coordinate conversion is hidden here.
/// Fractions for an absent helium element have exactly zero derivatives.
pub fn igm_point_rhs(
    state: &IgmGasState,
    nh: f64,
    nhe: f64,
    h: f64,
    tcmb: f64,
    photo: IgmPhotoInput,
) -> Result<IgmPointRhs, ForwardError> {
    igm_point_rhs_impl(state, nh, nhe, h, tcmb, photo, None)
}

/// Evaluate the unchanged event/energy ledger using one temperature-bound bundle.
/// A composition or energy change requires preparation at the new exact EOS T.
pub fn igm_point_rhs_with_prepared(
    state: &IgmGasState,
    nh: f64,
    nhe: f64,
    h: f64,
    tcmb: f64,
    photo: IgmPhotoInput,
    prepared: &PreparedIgmRates,
) -> Result<IgmPointRhs, ForwardError> {
    igm_point_rhs_impl(state, nh, nhe, h, tcmb, photo, Some(prepared))
}

fn igm_point_rhs_impl(
    state: &IgmGasState,
    nh: f64,
    nhe: f64,
    h: f64,
    tcmb: f64,
    photo: IgmPhotoInput,
    prepared: Option<&PreparedIgmRates>,
) -> Result<IgmPointRhs, ForwardError> {
    nonnegative(h)?;
    if !tcmb.is_normal() || tcmb <= 0.0 {
        return Err(invalid());
    }
    for i in 0..3 {
        nonnegative(photo.gamma_s[i])?;
        nonnegative(photo.heat_erg_per_absorber_s[i])?;
        if photo.gamma_s[i] == 0.0 && photo.heat_erg_per_absorber_s[i] != 0.0 {
            return Err(invalid());
        }
    }
    let eos = state.eos(nh, nhe)?;
    let t = eos.temperature_k;
    let ne = eos.electron_density_cm3;
    let rates = match prepared {
        Some(bundle) => {
            if bundle.temperature_k() != t {
                return Err(ForwardError::InvalidInput("IGM_PREPARED_TEMPERATURE_MISMATCH"));
            }
            bundle.rates()
        }
        None => igm_rates(t)?,
    };
    let c = HHeModel::controlled_fixture();
    let [x, y, z] = state.fractions;
    let abs = [
        mul(&[nh, 1.0 - x])?,
        mul(&[nhe, 1.0 - (y + z)])?,
        mul(&[nhe, y])?,
    ];
    let ions = [mul(&[nh, x])?, mul(&[nhe, y])?, mul(&[nhe, z])?];
    let mut out = IgmPointRhs::default();
    let mut photo_heat = 0.0;
    let mut photo_bind = 0.0;
    let mut capture_bind = 0.0;
    for i in 0..3 {
        let chi = mul(&[c.threshold_ev[i], c.ev_erg])?;
        out.photo_events_cm3_s[i] = mul(&[abs[i], photo.gamma_s[i]])?;
        out.ci_events_cm3_s[i] = mul(&[ne, abs[i], rates.ci_cm3_s[i]])?;
        out.rr_events_cm3_s[i] = mul(&[ne, ions[i], rates.rr_cm3_s[i]])?;
        out.ci_thermal_sink_erg_cm3_s[i] = mul(&[chi, out.ci_events_cm3_s[i]])?;
        out.rr_thermal_sink_erg_cm3_s[i] = mul(&[ne, ions[i], rates.rr_cooling_erg_cm3_s[i]])?;
        out.ci_floor_events_cm3_s[i] = mul(&[ne, abs[i], rates.diagnostics.ci_floor_cm3_s[i]])?;
        photo_heat += mul(&[abs[i], photo.heat_erg_per_absorber_s[i]])?;
        photo_bind += mul(&[chi, out.photo_events_cm3_s[i]])?;
        capture_bind += mul(&[chi, out.rr_events_cm3_s[i]])?;
    }
    out.dr_events_cm3_s = mul(&[ne, ions[1], rates.dr_cm3_s])?;
    out.dr_thermal_sink_erg_cm3_s = mul(&[ne, ions[1], rates.dr_cooling_erg_cm3_s])?;
    out.excluded_dr_cooling_erg_cm3_s =
        mul(&[ne, ions[1], rates.diagnostics.dr_excluded_erg_cm3_s])?;
    capture_bind += mul(&[c.threshold_ev[1], c.ev_erg, out.dr_events_cm3_s])?;
    let pref = [
        mul(&[ne, abs[0]])?,
        mul(&[ne, ne, ions[1]])?,
        mul(&[ne, ions[1]])?,
    ];
    for (i, &density) in pref.iter().enumerate() {
        out.ce_thermal_sink_erg_cm3_s[i] = mul(&[density, rates.ce_erg[i]])?;
        out.ce_cap_cooling_erg_cm3_s[i] = mul(&[density, rates.diagnostics.ce_cap_erg[i]])?;
    }
    out.freefree_thermal_sink_erg_cm3_s = mul(&[
        ne,
        ions[0] + ions[1] + 4.0 * ions[2],
        rates.freefree_erg_cm3_s,
    ])?;
    let forward: [f64; 3] =
        std::array::from_fn(|i| out.photo_events_cm3_s[i] + out.ci_events_cm3_s[i]);
    let net_h = forward[0] - out.rr_events_cm3_s[0];
    let net_he1 = forward[1] - out.rr_events_cm3_s[1] - out.dr_events_cm3_s;
    let net_he2 = forward[2] - out.rr_events_cm3_s[2];
    let dne = net_h + net_he1 + net_he2;
    out.species_chemical_cm3_s = [-net_h, net_h, -net_he1, net_he1 - net_he2, net_he2, dne];
    out.fraction_dt = [
        divide(net_h, nh)?,
        if nhe == 0.0 {
            0.0
        } else {
            divide(net_he1 - net_he2, nhe)?
        },
        if nhe == 0.0 {
            0.0
        } else {
            divide(net_he2, nhe)?
        },
    ];
    // Nonrelativistic Thomson CMB exchange. Blackbody a_rad derived from exact
    // Planck, Boltzmann and c owners; it does not inherit Grackle's rounded
    // comp_rate normalized to a fixed present-day CMB temperature.
    let a_rad = 8.0 * std::f64::consts::PI.powi(5) * c.kb_erg_k.powi(4)
        / (15.0 * PLANCK_ERG_S.powi(3) * c.c_cm_s.powi(3));
    let cmb_coeff = 4.0 * SIGMA_T_CM2 * a_rad * c.kb_erg_k / (ELECTRON_MASS_G * c.c_cm_s);
    let delta = finite(tcmb - t)?;
    out.cmb_to_gas_erg_cm3_s =
        mul(&[cmb_coeff, ne, tcmb, tcmb, tcmb, tcmb, delta.abs()])? * delta.signum();
    let ci = out.ci_thermal_sink_erg_cm3_s.iter().sum::<f64>();
    let radiative_kin = out.rr_thermal_sink_erg_cm3_s.iter().sum::<f64>()
        + out.dr_thermal_sink_erg_cm3_s
        + out.ce_thermal_sink_erg_cm3_s.iter().sum::<f64>()
        + out.freefree_thermal_sink_erg_cm3_s;
    out.thermal_micro_erg_cm3_s = photo_heat - ci - radiative_kin + out.cmb_to_gas_erg_cm3_s;
    out.binding_micro_erg_cm3_s = photo_bind + ci - capture_bind;
    out.escape_erg_cm3_s = capture_bind + radiative_kin;
    out.photo_input_erg_cm3_s = photo_bind + photo_heat;
    out.expansion_work_erg_cm3_s = mul(&[2.0, h, eos.u_erg_cm3])?;
    out.w_dt_erg_per_h_s = divide(
        out.thermal_micro_erg_cm3_s - out.expansion_work_erg_cm3_s,
        nh,
    )?;
    let particles = finite(nh + nhe + ne)?;
    out.temperature_dt_k_s = divide(
        2.0 * nh * out.w_dt_erg_per_h_s,
        3.0 * c.kb_erg_k * particles,
    )? - divide(t * dne, particles)?;
    for &v in out
        .fraction_dt
        .iter()
        .chain(out.species_chemical_cm3_s.iter())
    {
        finite(v)?;
    }
    for v in [
        photo_heat,
        photo_bind,
        capture_bind,
        ci,
        radiative_kin,
        out.thermal_micro_erg_cm3_s,
        out.binding_micro_erg_cm3_s,
        out.escape_erg_cm3_s,
        out.photo_input_erg_cm3_s,
        out.temperature_dt_k_s,
    ] {
        finite(v)?;
    }
    Ok(out)
}
