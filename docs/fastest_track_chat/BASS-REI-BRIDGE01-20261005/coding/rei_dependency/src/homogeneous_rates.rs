//! Primary-only homogeneous absorption ledger for bin-integrated photons.

use crate::{Absorber, AtomicProvider, ForwardError, C_LIGHT, MPC_CM};

const EV_ERG: f64 = 1.602176634e-12;
const BINDING_EV: [f64; 3] = [13.598434599702, 24.587389011, 54.41776];
const ABSORBERS: [Absorber; 3] = [Absorber::HI, Absorber::HeI, Absorber::HeII];

#[derive(Debug, Clone, Copy)]
pub struct PhotonNode {
    pub energy_ev: f64,
    /// Already quadrature weighted or bin integrated, per comoving cMpc^3.
    pub n_comoving_per_cmpc3: f64,
}

#[derive(Debug, Clone, Copy)]
pub struct OpacityOwners {
    pub kappa_per_cm: f64,
    pub fractions: [f64; 3],
}

#[derive(Debug, Clone, Copy)]
pub struct HomogeneousPhotoRates {
    pub gamma_per_s: [f64; 3],
    pub events_proper_per_cm3_s: [f64; 3],
    pub heat_erg_per_cm3_s: [f64; 3],
    pub binding_erg_per_cm3_s: [f64; 3],
    pub photon_loss_comoving_per_cmpc3_s: f64,
    pub absorbed_erg_per_cm3_s: f64,
}

fn nonnegative(v: f64) -> Result<f64, ForwardError> {
    if v.is_finite() && v >= 0.0 {
        Ok(v)
    } else {
        Err(ForwardError::InvalidInput(
            "HOMOGENEOUS_NONFINITE_OR_NEGATIVE",
        ))
    }
}

// This reference adapter promises consistent photon/species ledgers, not
// scaled arithmetic for extreme inputs. Reject zero/subnormal positive
// intermediate products, whose rounding can materially change owner counts.
fn product(a: f64, b: f64) -> Result<f64, ForwardError> {
    let value = nonnegative(a * b)?;
    if a > 0.0 && b > 0.0 && value < f64::MIN_POSITIVE {
        return Err(ForwardError::InvalidInput("HOMOGENEOUS_PRODUCT_UNDERFLOW"));
    }
    Ok(value)
}

fn cross_sections(provider: &AtomicProvider, energy_ev: f64) -> Result<[f64; 3], ForwardError> {
    Ok([
        provider.cross_section(ABSORBERS[0], energy_ev)?,
        provider.cross_section(ABSORBERS[1], energy_ev)?,
        provider.cross_section(ABSORBERS[2], energy_ev)?,
    ])
}

fn opacity_from_sigma(n: [f64; 3], sigma: [f64; 3]) -> Result<OpacityOwners, ForwardError> {
    let mut terms = [0.0; 3];
    for i in 0..3 {
        terms[i] = product(n[i], sigma[i])?;
    }
    let kappa = nonnegative(terms.iter().sum())?;
    let fractions = if kappa > 0.0 {
        [terms[0] / kappa, terms[1] / kappa, terms[2] / kappa]
    } else {
        [0.0; 3]
    };
    Ok(OpacityOwners {
        kappa_per_cm: kappa,
        fractions,
    })
}

/// Absorber density is proper cm^-3; returned opacity excludes any effective MFP.
pub fn homogeneous_opacity(
    provider: &AtomicProvider,
    n_absorber_proper_per_cm3: [f64; 3],
    energy_ev: f64,
) -> Result<OpacityOwners, ForwardError> {
    for value in n_absorber_proper_per_cm3 {
        nonnegative(value)?;
    }
    let sigma = cross_sections(provider, energy_ev)?;
    opacity_from_sigma(n_absorber_proper_per_cm3, sigma)
}

/// Per-node photon count is comoving; all event and energy rates are proper.
pub fn homogeneous_photo_rates(
    provider: &AtomicProvider,
    n: [f64; 3],
    mean_scale_factor: f64,
    nodes: &[PhotonNode],
) -> Result<HomogeneousPhotoRates, ForwardError> {
    for value in n {
        nonnegative(value)?;
    }
    if !mean_scale_factor.is_finite() || mean_scale_factor <= 0.0 {
        return Err(ForwardError::InvalidInput("MEAN_SCALE_FACTOR_INVALID"));
    }
    let proper_length = mean_scale_factor * MPC_CM;
    if !proper_length.is_finite() || proper_length <= 0.0 {
        return Err(ForwardError::InvalidInput("COMOVING_VOLUME_INVALID"));
    }
    let proper_volume = proper_length.powi(3);
    if !proper_volume.is_finite() || proper_volume <= 0.0 {
        return Err(ForwardError::InvalidInput("COMOVING_VOLUME_INVALID"));
    }
    let mut out = HomogeneousPhotoRates {
        gamma_per_s: [0.0; 3],
        events_proper_per_cm3_s: [0.0; 3],
        heat_erg_per_cm3_s: [0.0; 3],
        binding_erg_per_cm3_s: [0.0; 3],
        photon_loss_comoving_per_cmpc3_s: 0.0,
        absorbed_erg_per_cm3_s: 0.0,
    };
    for node in nodes {
        nonnegative(node.n_comoving_per_cmpc3)?;
        // Evaluate the fit even for zero density or photons, so its domain is enforced.
        let sigma = cross_sections(provider, node.energy_ev)?;
        let opacity = opacity_from_sigma(n, sigma)?;
        let nproper = nonnegative(node.n_comoving_per_cmpc3 / proper_volume)?;
        if node.n_comoving_per_cmpc3 > 0.0 && nproper < f64::MIN_POSITIVE {
            return Err(ForwardError::InvalidInput("PHOTON_CONVERSION_UNDERFLOW"));
        }
        let photon_loss = product(
            product(C_LIGHT, opacity.kappa_per_cm)?,
            node.n_comoving_per_cmpc3,
        )?;
        out.photon_loss_comoving_per_cmpc3_s =
            nonnegative(out.photon_loss_comoving_per_cmpc3_s + photon_loss)?;
        for i in 0..3 {
            let gamma = product(product(C_LIGHT, nproper)?, sigma[i])?;
            let events = product(n[i], gamma)?;
            let heat = product(product(events, node.energy_ev - BINDING_EV[i])?, EV_ERG)?;
            let binding = product(product(events, BINDING_EV[i])?, EV_ERG)?;
            out.gamma_per_s[i] = nonnegative(out.gamma_per_s[i] + gamma)?;
            out.events_proper_per_cm3_s[i] = nonnegative(out.events_proper_per_cm3_s[i] + events)?;
            out.heat_erg_per_cm3_s[i] = nonnegative(out.heat_erg_per_cm3_s[i] + heat)?;
            out.binding_erg_per_cm3_s[i] = nonnegative(out.binding_erg_per_cm3_s[i] + binding)?;
            out.absorbed_erg_per_cm3_s = nonnegative(
                out.absorbed_erg_per_cm3_s + product(product(events, node.energy_ev)?, EV_ERG)?,
            )?;
        }
    }
    Ok(out)
}
