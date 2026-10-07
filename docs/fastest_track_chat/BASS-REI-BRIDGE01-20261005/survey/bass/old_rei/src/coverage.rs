//! Registry metadata is not a physical-source provider.
use crate::ForwardError;

pub const PORTED_FUNCTIONS: [&str; 7] = [
    "transform_z_to_y",
    "pchip_eval",
    "opacity_cMpc_inv",
    "photon_rates",
    "gamma_species",
    "positive_mass_projection",
    "signed_transfer_lift",
];
pub const SOURCE_SITES: [&str; 4] = [
    "population_t0",
    "population_t1_predictor",
    "thermal_tgamma",
    "thermal_t1_final",
];
pub const EXCLUDED: [&str; 6] = [
    "bernoulli_kl_mean_projection",
    "capacity_constrained_group_projection",
    "P0_C8",
    "C9_CP0",
    "HOST4_H19",
    "HH_R10",
];

/// Fail closed: no external physical rate is admitted by this compatibility port.
pub fn require_physical_source(_name: &str) -> Result<(), ForwardError> {
    Err(ForwardError::MissingAuthority(
        "NO_EXTERNAL_PHYSICAL_SOURCE_ADMITTED",
    ))
}
