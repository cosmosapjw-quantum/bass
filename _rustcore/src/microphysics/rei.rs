//! Thin BASS dispatch to the admitted Rust-only REI canonical functions.
use rei_microphysics::{ForwardError, GammaSpecies, GroupParams, PchipTable, SignedLift, State};

use super::visibility::{ElectronState, VisibilityError};

/// Converts a supplied legacy REI snapshot to BASS's proper-SI electron state.
///
/// This is a fixed-state receiver only: the REI parameter densities are proper
/// cm^-3 and are converted once to m^-3.  It does not evolve REI chemistry,
/// assign a Bianchi background, or determine an observer tail.
pub fn electron_state_from_rei(
    state: &State,
    params: &GroupParams,
) -> Result<ElectronState, VisibilityError> {
    let helium_sum = state.helium.iter().sum::<f64>();
    if state.helium.iter().any(|x| !x.is_finite() || *x < 0.0)
        || !helium_sum.is_finite()
        || (helium_sum - 1.0).abs() > 64.0 * f64::EPSILON
    {
        return Err(VisibilityError::InvalidFraction);
    }
    let n_h_m3 = params.n_h_proper_per_cm3 * 1_000_000.0;
    let n_he_m3 = params.n_he_proper_per_cm3 * 1_000_000.0;
    ElectronState::new(
        n_h_m3,
        n_he_m3,
        state.x_hii,
        state.helium[1],
        state.helium[2],
    )
}

pub fn transform(z: &[f64; 9]) -> State {
    rei_microphysics::transform_z_to_y(z)
}
pub fn pchip(table: &PchipTable, x: f64) -> Result<f64, ForwardError> {
    rei_microphysics::pchip_eval(table, x)
}
pub fn opacity(state: &State, params: &GroupParams) -> Result<[f64; 4], ForwardError> {
    rei_microphysics::opacity_cMpc_inv(state, params)
}
pub fn photon_source(
    state: &State,
    emissivity: &[f64; 4],
    params: &GroupParams,
) -> Result<[f64; 4], ForwardError> {
    rei_microphysics::photon_rates(state, emissivity, params)
}
pub fn gamma_species(state: &State, params: &GroupParams) -> GammaSpecies {
    rei_microphysics::gamma_species(state, params)
}
pub fn positive_projection(prior: &[f64], total: f64) -> Result<Vec<f64>, ForwardError> {
    rei_microphysics::positive_mass_projection(prior, total)
}
pub fn signed_transfer(rate: f64, prior: &[f64]) -> Result<SignedLift, ForwardError> {
    rei_microphysics::signed_transfer_lift(rate, prior)
}
