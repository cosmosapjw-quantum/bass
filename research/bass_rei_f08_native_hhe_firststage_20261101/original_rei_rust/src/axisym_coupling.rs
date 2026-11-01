//! Manufactured scalar-expansion identities; it does not compose source/absorption into H/He RHS.
//! Inputs are proper nuclear/photon number densities and proper photon energy density.
//! The temperature term assumes fixed-composition, nonrelativistic, isotropic one-temperature
//! gas with zero heating; individual photon energy is not represented by the `-4 H rho` term.
use crate::ForwardError;
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct IsotropicExpansionTerms {
    pub nuclear_density_dot_per_s: f64,
    pub photon_number_dot_per_s: f64,
    pub photon_energy_dot_per_s: f64,
    pub temperature_dot_k_s: f64,
}
pub fn isotropic_expansion_terms(
    hubble_per_s: f64,
    nuclear_density: f64,
    photon_number: f64,
    photon_energy: f64,
    temperature_k: f64,
) -> Result<IsotropicExpansionTerms, ForwardError> {
    if ![
        hubble_per_s,
        nuclear_density,
        photon_number,
        photon_energy,
        temperature_k,
    ]
    .iter()
    .all(|x| x.is_finite())
        || nuclear_density < 0.
        || photon_number < 0.
        || photon_energy < 0.
        || temperature_k < 0.
    {
        return Err(ForwardError::InvalidInput("AXISYM_EXPANSION_DOMAIN"));
    }
    let o = IsotropicExpansionTerms {
        nuclear_density_dot_per_s: -3. * hubble_per_s * nuclear_density,
        photon_number_dot_per_s: -3. * hubble_per_s * photon_number,
        photon_energy_dot_per_s: -4. * hubble_per_s * photon_energy,
        temperature_dot_k_s: -2. * hubble_per_s * temperature_k,
    };
    if [
        o.nuclear_density_dot_per_s,
        o.photon_number_dot_per_s,
        o.photon_energy_dot_per_s,
        o.temperature_dot_k_s,
    ]
    .iter()
    .all(|x| x.is_finite())
    {
        Ok(o)
    } else {
        Err(ForwardError::InvalidInput("AXISYM_EXPANSION_OVERFLOW"))
    }
}
