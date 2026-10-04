//! Thin BASS dispatch to the admitted Rust-only REI canonical functions.
use rei_microphysics::{ForwardError, GammaSpecies, GroupParams, PchipTable, SignedLift, State};

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
