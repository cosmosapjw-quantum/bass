//! Source-linked, opt-in original BASS Type-II normal-frame photon characteristic.
//! No RF-01 RuntimePlan dispatch or production collision activation.
//! Imported original generated/source Rust modules are byte-locked by external R7.
#![allow(dead_code)]

#[path = "../../../runtime/rust/typeii/typeii_physical_guard.rs"]
mod typeii_physical_guard;
#[path = "../../../generated/rust/typeii/typeii_polarized.rs"]
mod typeii_polarized;
#[path = "../../../runtime/rust/typeii/typeii_polarized_liouville.rs"]
mod typeii_polarized_liouville;

use super::typeii_host::{TypeIIHostError, TypeIIHostState};

const C_LIGHT_SI: f64 = 299_792_458.0;
const DIRECTION_TOLERANCE: f64 = 1.0e-10;

#[derive(Clone, Debug, PartialEq)]
pub enum PhotonHostError {
    Host(TypeIIHostError),
    Source(String),
    NonFiniteDirection,
    NonUnitDirection,
    NegativeElectronRestDensity,
    InvalidCrossSection,
    InvalidHubble,
    NonFiniteRate,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct SourcePhotonRates {
    /// d(n^i)/d tau_H, n a normal-frame unit photon direction.
    pub direction_rate: [f64; 3],
    /// d log(E_normal)/d tau_H, with d tau_H = H dt_normal.
    pub log_energy_rate: f64,
    /// d log(I_normal, bolometric)/d tau_H for collision-free propagation.
    pub log_bolometric_rate: f64,
    /// Photon screen-connection rate from the immutable original Liouville source.
    pub screen_connection_rate: f64,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct ThomsonProperDensity {
    /// Electron-rest proper free electron number density in SI m^-3, NOT normal density.
    pub electron_rest_number_density_per_m3: f64,
    /// Thomson cross-section in SI m^2.
    pub cross_section_m2: f64,
    /// Positive normal-congruence Hubble scalar in s^-1.
    pub normal_hubble_per_s: f64,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct ThomsonRayRate {
    /// Source generated scalar C already owns q=1-v2*n_y exactly once.
    /// A proper-density owner must therefore supply gamma*n_e^rest*sigma_T*c/H.
    pub scalar_prefactor_per_hubble_tau: f64,
    pub relative_flux_q: f64,
    pub electron_doppler_d: f64,
    pub line_optical_depth_rate_per_hubble_tau: f64,
}

fn checked_normal_direction(n: [f64; 3]) -> Result<(), PhotonHostError> {
    if !n.into_iter().all(|a| a.is_finite()) {
        return Err(PhotonHostError::NonFiniteDirection);
    }
    let norm2: f64 = n.into_iter().map(|a| a * a).sum();
    if !norm2.is_finite() || (norm2 - 1.0).abs() > DIRECTION_TOLERANCE {
        return Err(PhotonHostError::NonUnitDirection);
    }
    Ok(())
}

/// Calls the original Rust source Type-II tetrad background and Liouville coefficients.
/// Input TypeIIHostState enforces Gauss, Codazzi, normal frame, Hubble WE and Hubble tau.
pub fn source_photon_coefficients(
    host: &TypeIIHostState,
    normal_direction: [f64; 3],
) -> Result<SourcePhotonRates, PhotonHostError> {
    checked_normal_direction(normal_direction)?;
    let state = host.to_typeii().map_err(PhotonHostError::Host)?;
    let source_background = typeii_polarized_liouville::typeii_background_from_state(&state.x)
        .map_err(|error| PhotonHostError::Source(format!("{error:?}")))?;
    let rates =
        typeii_polarized_liouville::liouville_coefficients(normal_direction, &source_background)
            .map_err(|error| PhotonHostError::Source(format!("{error:?}")))?;
    Ok(SourcePhotonRates {
        direction_rate: rates.direction_rate,
        log_energy_rate: rates.log_energy_rate,
        log_bolometric_rate: rates.log_bolometric_rate,
        screen_connection_rate: rates.screen_connection_rate,
    })
}

/// Return the source-compatible scalar prefactor and the physical ray rate.
/// The original generated Type-II scalar collision C already multiplies q exactly once.
/// Gamma here is the *electron Lorentz factor*, not the gamma-law fluid index.
/// Electrons must be explicitly identified with velocity v2 in the source's normal frame.
pub fn thomson_ray_rate(
    host: &TypeIIHostState,
    normal_direction: [f64; 3],
    proper: ThomsonProperDensity,
) -> Result<ThomsonRayRate, PhotonHostError> {
    checked_normal_direction(normal_direction)?;
    let state = host.to_typeii().map_err(PhotonHostError::Host)?;
    if !proper.electron_rest_number_density_per_m3.is_finite()
        || proper.electron_rest_number_density_per_m3 < 0.0
    {
        return Err(PhotonHostError::NegativeElectronRestDensity);
    }
    if !proper.cross_section_m2.is_finite() || proper.cross_section_m2 <= 0.0 {
        return Err(PhotonHostError::InvalidCrossSection);
    }
    if !proper.normal_hubble_per_s.is_finite() || proper.normal_hubble_per_s <= 0.0 {
        return Err(PhotonHostError::InvalidHubble);
    }
    let v = state.x[4];
    let electron_gamma = 1.0 / (1.0 - v * v).sqrt();
    let relative_flux_q = 1.0 - v * normal_direction[1];
    let scalar_prefactor_per_hubble_tau = electron_gamma
        * proper.electron_rest_number_density_per_m3
        * proper.cross_section_m2
        * C_LIGHT_SI
        / proper.normal_hubble_per_s;
    let electron_doppler_d = electron_gamma * relative_flux_q;
    let line_optical_depth_rate_per_hubble_tau = scalar_prefactor_per_hubble_tau * relative_flux_q;
    if ![
        scalar_prefactor_per_hubble_tau,
        electron_doppler_d,
        line_optical_depth_rate_per_hubble_tau,
    ]
    .into_iter()
    .all(|x| x.is_finite() && x >= 0.0)
    {
        return Err(PhotonHostError::NonFiniteRate);
    }
    Ok(ThomsonRayRate {
        scalar_prefactor_per_hubble_tau,
        relative_flux_q,
        electron_doppler_d,
        line_optical_depth_rate_per_hubble_tau,
    })
}

/// Pure geometric dimensionless optical-depth factor for unit rest-opacity-per-Hubble-time.
pub fn unit_rest_optical_depth_factor(
    host: &TypeIIHostState,
    normal_direction: [f64; 3],
) -> Result<f64, PhotonHostError> {
    checked_normal_direction(normal_direction)?;
    let state = host.to_typeii().map_err(PhotonHostError::Host)?;
    let v = state.x[4];
    let q = 1.0 - v * normal_direction[1];
    let d = q / (1.0 - v * v).sqrt();
    if !d.is_finite() || d <= 0.0 {
        return Err(PhotonHostError::NonFiniteRate);
    }
    Ok(d)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::runtime::typeii_host::TypeIIState5;

    fn sample() -> TypeIIHostState {
        TypeIIState5::from_four(0.2375, 0.0, 0.865, 0.05, 1.3)
            .unwrap()
            .to_host()
            .unwrap()
    }

    fn dot(a: [f64; 3], b: [f64; 3]) -> f64 {
        a.iter().zip(b).map(|(x, y)| x * y).sum()
    }

    #[test]
    fn original_source_geodesic_direction_is_tangent_and_redshift_matches_shear() {
        let host = sample();
        let n = [
            0.4_f64,
            0.5,
            (1.0_f64 - 0.4_f64 * 0.4 - 0.5_f64 * 0.5).sqrt(),
        ];
        let result = source_photon_coefficients(&host, n).unwrap();
        assert!(dot(n, result.direction_rate).abs() < 4e-15);
        let manual = -1.0
            - dot(
                n,
                [
                    host.shear[(0, 0)] * n[0] + host.shear[(0, 2)] * n[2],
                    host.shear[(1, 1)] * n[1],
                    host.shear[(2, 0)] * n[0] + host.shear[(2, 2)] * n[2],
                ],
            );
        assert!((result.log_energy_rate - manual).abs() < 3e-15);
        assert!((result.log_bolometric_rate - 4.0 * manual).abs() < 3e-15);
        assert!(result.direction_rate[1].is_finite());
    }

    #[test]
    fn proper_density_rate_includes_gamma_once_and_internal_q_once() {
        let host = sample();
        let n = [0.0, 0.6, 0.8];
        let proper = ThomsonProperDensity {
            electron_rest_number_density_per_m3: 1.0e8,
            cross_section_m2: 6.652_458_732_1e-29,
            normal_hubble_per_s: 2.0e-14,
        };
        let result = thomson_ray_rate(&host, n, proper).unwrap();
        let gamma = 1.0 / (1.0 - 0.05_f64.powi(2)).sqrt();
        let q = 1.0 - 0.05 * 0.6;
        let expected_rest =
            proper.electron_rest_number_density_per_m3 * proper.cross_section_m2 * C_LIGHT_SI
                / proper.normal_hubble_per_s;
        assert!((result.scalar_prefactor_per_hubble_tau - gamma * expected_rest).abs() < 1e-12);
        assert!(
            (result.line_optical_depth_rate_per_hubble_tau - gamma * q * expected_rest).abs()
                < 1e-12
        );
        assert!((unit_rest_optical_depth_factor(&host, n).unwrap() - gamma * q).abs() < 1e-14);
        let wrong_double_q = gamma * q * q * expected_rest;
        assert!((result.line_optical_depth_rate_per_hubble_tau - wrong_double_q).abs() > 1e-3);
    }

    #[test]
    fn offslice_or_unphysical_input_fails_closed() {
        let host = sample();
        assert_eq!(
            source_photon_coefficients(&host, [2.0, 0.0, 0.0]).unwrap_err(),
            PhotonHostError::NonUnitDirection
        );
        let mut bad = host.clone();
        bad.group.n[1] = 0.1;
        assert!(matches!(
            source_photon_coefficients(&bad, [1.0, 0.0, 0.0]),
            Err(PhotonHostError::Host(_))
        ));
        let p = ThomsonProperDensity {
            electron_rest_number_density_per_m3: -1.0,
            cross_section_m2: 6.652e-29,
            normal_hubble_per_s: 1e-14,
        };
        assert_eq!(
            thomson_ray_rate(&host, [1.0, 0.0, 0.0], p).unwrap_err(),
            PhotonHostError::NegativeElectronRestDensity
        );
    }

    #[test]
    fn original_source_flrw_limit_has_stable_ray_and_e_minus_tau_energy() {
        let mut bg = typeii_polarized_liouville::HomogeneousRayBackground::zero();
        bg.expansion = 1.0;
        let n = [0.0, 0.0, 1.0];
        let r = typeii_polarized_liouville::liouville_coefficients(n, &bg).unwrap();
        assert_eq!(r.direction_rate, [0.0, 0.0, 0.0]);
        assert_eq!(r.log_energy_rate, -1.0);
        assert_eq!(r.log_bolometric_rate, -4.0);
    }
}
