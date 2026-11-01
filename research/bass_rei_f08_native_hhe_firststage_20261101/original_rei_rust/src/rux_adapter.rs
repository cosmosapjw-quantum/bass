//! Explicit scenario boundary for the conditional warm `PrimaryStage` path.
//! No cosmology, emissivity history, or cold EoR provider is supplied here.

use crate::coupled_primary::{PrimaryPacket, PrimaryStage, PrimaryState};
use crate::ForwardError;

#[derive(Clone, Debug, PartialEq)]
pub struct ProperClock {
    pub origin: String,
    pub seconds_since_origin: f64,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum HydrogenDensity {
    ProperCm3(f64),
    ComovingCm3 { value: f64, scale_factor: f64 },
}

impl HydrogenDensity {
    pub fn proper_cm3(self) -> Result<f64, ForwardError> {
        let value = match self {
            Self::ProperCm3(value) => value,
            Self::ComovingCm3 { value, scale_factor } => {
                if !scale_factor.is_finite() || scale_factor <= 0.0 {
                    return Err(ForwardError::InvalidInput("RUX_SCALE_FACTOR"));
                }
                value / scale_factor.powi(3)
            }
        };
        if !value.is_finite() || value <= 0.0 {
            return Err(ForwardError::InvalidInput("RUX_PROPER_H_DENSITY"));
        }
        Ok(value)
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum PhotonSourceRole {
    /// Explicit existing packet stock, in photons per hydrogen nucleus.
    InitialStock,
    /// An emissivity needs a separate time/source callback and event owner.
    ExternalEmissivity,
    /// An imposed UVB rate is not a packet stock.
    ImposedUvb,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum PrimaryClosure {
    HomogeneousCaseAEscape,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum EventOwner {
    /// PrimaryStage owns packet absorption, ionization, heating, escape and work.
    PrimaryStage,
    External,
}

#[derive(Clone, Debug)]
pub struct ScenarioInput {
    pub clock: ProperClock,
    pub hydrogen_density: HydrogenDensity,
    pub helium_to_hydrogen: f64,
    pub mean_hubble_per_s: f64,
    pub fractions: [f64; 3],
    pub thermal_ev_per_h: f64,
    pub escape_ev_per_h: f64,
    pub packets: Vec<PrimaryPacket>,
    pub source_role: PhotonSourceRole,
    pub closure: PrimaryClosure,
    pub event_owner: EventOwner,
}

pub fn bind_primary(input: ScenarioInput) -> Result<(PrimaryStage, PrimaryState), ForwardError> {
    if input.clock.origin.trim().is_empty()
        || !input.clock.seconds_since_origin.is_finite()
        || input.clock.seconds_since_origin < 0.0
    {
        return Err(ForwardError::InvalidInput("RUX_CLOCK_ORIGIN"));
    }
    if input.source_role != PhotonSourceRole::InitialStock {
        return Err(ForwardError::MissingAuthority("RUX_SOURCE_CALLBACK"));
    }
    if input.event_owner != EventOwner::PrimaryStage {
        return Err(ForwardError::MissingAuthority("RUX_EVENT_OWNER"));
    }
    if !input.helium_to_hydrogen.is_finite()
        || input.helium_to_hydrogen <= 0.0
        || !input.mean_hubble_per_s.is_finite()
        || input.mean_hubble_per_s < 0.0
        || !input.thermal_ev_per_h.is_finite()
        || input.thermal_ev_per_h <= 0.0
        || !input.escape_ev_per_h.is_finite()
        || input.escape_ev_per_h < 0.0
    {
        return Err(ForwardError::InvalidInput("RUX_PRIMARY_INPUT"));
    }
    let [hii, heii, heiii] = input.fractions;
    if !input.fractions.iter().all(|x| x.is_finite())
        || !(0.0..=1.0).contains(&hii)
        || heii < 0.0
        || heiii < 0.0
        || heii + heiii > 1.0
    {
        return Err(ForwardError::InvalidInput("RUX_SPECIES_FRACTIONS"));
    }
    if input.packets.is_empty()
        || input.packets.iter().any(|p| {
            !p.energy_ev.is_finite()
                || p.energy_ev <= 0.0
                || !p.per_h.is_finite()
                || p.per_h < 0.0
        })
    {
        return Err(ForwardError::InvalidInput("RUX_PACKET_STOCK"));
    }
    let n_h_cm3 = input.hydrogen_density.proper_cm3()?;
    let stage = PrimaryStage {
        n_h_cm3,
        f_he: input.helium_to_hydrogen,
        h_mean_per_s: input.mean_hubble_per_s,
    };
    let state = PrimaryState {
        fractions: input.fractions,
        w_ev_per_h: input.thermal_ev_per_h,
        escape_ev_per_h: input.escape_ev_per_h,
        packets: input.packets,
    };
    // The underlying provider retains its existing warm-domain check at the step.
    Ok((stage, state))
}
