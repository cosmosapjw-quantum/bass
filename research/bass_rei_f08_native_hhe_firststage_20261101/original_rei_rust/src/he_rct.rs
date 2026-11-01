//! Opt-in ground-state HeIII + HI radiative charge transfer (RCT).
//!
//! This module adds a source-count ledger and an explicitly supplied escaped
//! photon mean-energy closure to the existing static H/He RHS. It does not admit
//! either nominal rate as physically certified, infer a spectrum, or modify the
//! production microstep. All densities are proper cm^-3; rates are per proper s.
use crate::{hhe_rhs, ForwardError, HHeModel, HHeRhs, HHeState};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum RctSource {
    Kf96Nominal,
    Gm25Constant,
}

/// Explicit scenario mapping, not a claim of isotope resolution in KF96.
/// Gas-rest common-T Maxwell distributions, zero relative drift, H(1s), 4HeIII,
/// HeII(1s) final state, and one spontaneous photon. No reverse/RA/NRCT channel.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum RctScenario {
    W82GroundStateCommonTemperatureZeroDrift,
}

#[derive(Clone, Copy, Debug)]
pub struct RctSourceRecord {
    pub source_id: &'static str,
    pub rate_source: &'static str,
    pub mechanism_doi: &'static str,
    pub snapshot_commit: &'static str,
    pub provider_git_blob: &'static str,
    pub packet_git_blob: &'static str,
    pub minimum_k: f64,
    pub maximum_k: f64,
    pub lower_endpoint_approximate_in_source: bool,
    pub coefficient_cm3_s: f64,
    pub isotope_source_resolved: bool,
    pub physical_admission: bool,
    pub source_conflict_resolved: bool,
    pub uncertainty: Option<f64>,
    pub photon_energy_moment_ev: Option<f64>,
}

impl RctSource {
    pub fn record(self) -> RctSourceRecord {
        let (
            source_id,
            rate_source,
            provider_git_blob,
            packet_git_blob,
            minimum_k,
            maximum_k,
            lower_endpoint_approximate_in_source,
            coefficient_cm3_s,
        ) = match self {
            Self::Kf96Nominal => (
                "KF96_HEIII_HI_RCT_NOMINAL_V1",
                "10.1086/192335 Eq.7 Table1 He2+",
                "a2cdc62b238bea64d2dfe587f7efccc6ce3728e2",
                "aaceceb59007c81328a3185d826dca7526039d1e",
                1000.0,
                1e7,
                true,
                1e-14,
            ),
            Self::Gm25Constant => (
                "GM25_W82_RCX_CONSTANT_200_10000_K_V1",
                "arXiv:2511.21966v1 Appendix B.3",
                "c3f5cb56b7f5babcbead21694de31b57ca4ff992",
                "a93d3cf75e69390275c956a3b1b73912eaee0519",
                200.0,
                10000.0,
                false,
                1.7e-13,
            ),
        };
        RctSourceRecord {
            source_id,
            rate_source,
            mechanism_doi: "10.1103/PhysRevA.26.3164",
            snapshot_commit: "21d5b8075429903d195d6e0e0c24a10c00b21063",
            provider_git_blob,
            packet_git_blob,
            minimum_k,
            maximum_k,
            lower_endpoint_approximate_in_source,
            coefficient_cm3_s,
            // Explicit W82 scenario, not new isotope-data admission.
            isotope_source_resolved: false,
            physical_admission: false,
            source_conflict_resolved: false,
            uncertainty: None,
            photon_energy_moment_ev: None,
        }
    }
}

/// Private fields prevent bypass of source choice and conflict acknowledgment.
/// No default source, automatic source switch, extrapolation, or clamping.
#[derive(Clone, Copy, Debug)]
pub struct RctProvider {
    source: RctSource,
    scenario: RctScenario,
}

impl RctProvider {
    pub fn new(
        source: RctSource,
        scenario: RctScenario,
        acknowledge_seventeen_fold_source_conflict: bool,
    ) -> Result<Self, ForwardError> {
        if !acknowledge_seventeen_fold_source_conflict {
            return Err(ForwardError::InvalidInput(
                "RCT_SOURCE_CONFLICT_NOT_ACKNOWLEDGED",
            ));
        }
        Ok(Self { source, scenario })
    }
    pub fn source(&self) -> RctSource {
        self.source
    }
    pub fn scenario(&self) -> RctScenario {
        self.scenario
    }
    pub fn record(&self) -> RctSourceRecord {
        self.source.record()
    }
    pub fn coefficient_cm3_s(&self, temperature_k: f64) -> Result<f64, ForwardError> {
        let r = self.record();
        if !temperature_k.is_finite() || !(r.minimum_k..=r.maximum_k).contains(&temperature_k) {
            return Err(ForwardError::InvalidInput("RCT_TEMPERATURE_DOMAIN"));
        }
        Ok(r.coefficient_cm3_s)
    }

    /// Number-only ledger; missing photon/heat moments remain explicitly absent.
    /// Fractions of an absent nuclear species receive zero RCT derivative.
    /// (The baseline HHe RHS separately uses virtual per-capita equations.)
    pub fn events(
        &self,
        model: &HHeModel,
        state: &HHeState,
    ) -> Result<RctEventLedger, ForwardError> {
        model.validate_state(state)?;
        let temperature_k = model.temperature(state)?;
        let k = self.coefficient_cm3_s(temperature_k)?;
        let n_hi = model.n_h_cm3 * (1.0 - state.fractions[0]);
        let n_heiii = model.n_he_cm3 * state.fractions[2];
        let event_rate = (k * n_hi) * n_heiii;
        let dh = if model.n_h_cm3 == 0.0 {
            0.0
        } else {
            event_rate / model.n_h_cm3
        };
        let dhe = if model.n_he_cm3 == 0.0 {
            0.0
        } else {
            event_rate / model.n_he_cm3
        };
        let q_ev = model.threshold_ev[2] - model.threshold_ev[0];
        if !q_ev.is_finite() || q_ev <= 0.0 {
            return Err(ForwardError::InvalidInput("RCT_Q_DOMAIN"));
        }
        let chemical = -(q_ev * model.ev_erg) * event_rate;
        if [n_hi, n_heiii, event_rate, dh, dhe, chemical]
            .iter()
            .any(|x| !x.is_finite())
        {
            return Err(ForwardError::InvalidInput("RCT_OVERFLOW"));
        }
        Ok(RctEventLedger {
            source: self.source,
            temperature_k,
            coefficient_cm3_s: k,
            n_hi_cm3: n_hi,
            n_heiii_cm3: n_heiii,
            event_rate_cm3_s: event_rate,
            species_rate_cm3_s: [-event_rate, event_rate, 0.0, event_rate, -event_rate, 0.0],
            fraction_rate_s: [dh, dhe, -dhe],
            free_electron_rate_cm3_s: 0.0,
            emitted_photon_count_cm3_s: event_rate,
            q_ev,
            chemical_energy_rate_erg_cm3_s: chemical,
            thermal_photon_closure: RctClosureStatus::IncompleteScalarOnly,
        })
    }

    /// The supplied event-weighted mean photon energy is a research closure input.
    /// It is not predicted by the count provider, a group spectrum, or an OTS model.
    pub fn closed_events(
        &self,
        model: &HHeModel,
        state: &HHeState,
        closure: EscapingMeanPhotonEnergy,
    ) -> Result<ClosedRctLedger, ForwardError> {
        let event = self.events(model, state)?;
        let r = event.event_rate_cm3_s;
        let heat = ((event.q_ev - closure.mean_ev) * model.ev_erg) * r;
        let escape = (closure.mean_ev * model.ev_erg) * r;
        if !heat.is_finite() || !escape.is_finite() {
            return Err(ForwardError::InvalidInput("RCT_OVERFLOW"));
        }
        Ok(ClosedRctLedger {
            event,
            mean_escaped_photon_energy_ev: closure.mean_ev,
            closure_input_origin: "CALLER_SUPPLIED_NO_ATOMIC_MOMENT",
            thermal_energy_rate_erg_cm3_s: heat,
            escaped_energy_rate_erg_cm3_s: escape,
            escaped_photon_count_cm3_s: r,
            tracked_photon_rate_cm3_s: [0.0; 3],
            physical_closure_admission: false,
        })
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum RctClosureStatus {
    IncompleteScalarOnly,
}

#[derive(Clone, Copy, Debug)]
pub struct RctEventLedger {
    pub source: RctSource,
    pub temperature_k: f64,
    pub coefficient_cm3_s: f64,
    pub n_hi_cm3: f64,
    pub n_heiii_cm3: f64,
    pub event_rate_cm3_s: f64,
    /// HI, HII, HeI, HeII, HeIII, free electron (proper cm^-3 s^-1).
    pub species_rate_cm3_s: [f64; 6],
    /// x_HII, y_HeII, y_HeIII (s^-1).
    pub fraction_rate_s: [f64; 3],
    pub free_electron_rate_cm3_s: f64,
    pub emitted_photon_count_cm3_s: f64,
    pub q_ev: f64,
    pub chemical_energy_rate_erg_cm3_s: f64,
    pub thermal_photon_closure: RctClosureStatus,
}

#[derive(Clone, Copy, Debug)]
pub struct EscapingMeanPhotonEnergy {
    mean_ev: f64,
}
impl EscapingMeanPhotonEnergy {
    /// Strictly positive for the declared real emitted photon; no physical upper bound
    /// or moment accuracy is certified. Exact input provenance is owned by the caller.
    pub fn research_input_ev(mean_ev: f64) -> Result<Self, ForwardError> {
        if !mean_ev.is_finite() || mean_ev <= 0.0 {
            return Err(ForwardError::InvalidInput("RCT_ESCAPE_MOMENT_DOMAIN"));
        }
        Ok(Self { mean_ev })
    }
    pub fn mean_ev(&self) -> f64 {
        self.mean_ev
    }
}

#[derive(Clone, Copy, Debug)]
pub struct ClosedRctLedger {
    pub event: RctEventLedger,
    pub mean_escaped_photon_energy_ev: f64,
    /// Exact caller input/scenario provenance belongs to the external run manifest.
    pub closure_input_origin: &'static str,
    pub thermal_energy_rate_erg_cm3_s: f64,
    pub escaped_energy_rate_erg_cm3_s: f64,
    pub escaped_photon_count_cm3_s: f64,
    pub tracked_photon_rate_cm3_s: [f64; 3],
    pub physical_closure_admission: bool,
}

/// Disabled is the only default. Enabled requires both a selected provider and
/// a validated explicit escaped-photon energy moment; count-only cannot compose.
#[derive(Clone, Copy, Debug, Default)]
pub enum RctSelection {
    #[default]
    Disabled,
    Escaping {
        provider: RctProvider,
        closure: EscapingMeanPhotonEnergy,
    },
}

#[derive(Clone, Copy, Debug)]
pub struct CombinedRctRhs {
    pub baseline: HHeRhs,
    pub combined: HHeRhs,
    /// Separate event type: these are not electron-recombination events.
    pub rct: Option<ClosedRctLedger>,
}

pub fn combined_hhe_rhs(
    model: &HHeModel,
    state: &HHeState,
    selection: RctSelection,
) -> Result<CombinedRctRhs, ForwardError> {
    let baseline = hhe_rhs(model, state)?;
    let (provider, closure) = match selection {
        RctSelection::Disabled => {
            return Ok(CombinedRctRhs {
                baseline,
                combined: baseline,
                rct: None,
            })
        }
        RctSelection::Escaping { provider, closure } => (provider, closure),
    };
    let rct = provider.closed_events(model, state, closure)?;
    let mut combined = baseline;
    for i in 0..3 {
        combined.derivative[i] += rct.event.fraction_rate_s[i];
    }
    combined.derivative[3] += rct.thermal_energy_rate_erg_cm3_s;
    combined.escaped_energy_rate += rct.escaped_energy_rate_erg_cm3_s;
    if combined.derivative.iter().any(|x| !x.is_finite())
        || !combined.escaped_energy_rate.is_finite()
    {
        return Err(ForwardError::InvalidInput("RCT_COMPOSED_OVERFLOW"));
    }
    Ok(CombinedRctRhs {
        baseline,
        combined,
        rct: Some(rct),
    })
}

/// Typed FT03 wrapper. Ft03Model.gas deliberately has zero legacy alpha/beta;
/// passing that gas to combined_hhe_rhs would drop FT03 RR/CI/DR physics.
#[derive(Clone, Copy, Debug)]
pub struct CombinedFt03RctRhs {
    pub baseline: crate::Ft03Rhs,
    pub combined: crate::Ft03Rhs,
    pub rct: Option<ClosedRctLedger>,
}

/// Compose against the actual temperature-dependent FT03 RHS, preserving its
/// RR kinetic moments, two DR channels, CI and photo event inventories. This is
/// an RHS adapter only; the FT03 implicit stepper does not call it yet.
pub fn combined_ft03_rhs(
    model: &crate::Ft03Model,
    state: &HHeState,
    selection: RctSelection,
) -> Result<CombinedFt03RctRhs, ForwardError> {
    let baseline = crate::ft03_rhs(model, state)?;
    let (provider, closure) = match selection {
        RctSelection::Disabled => {
            return Ok(CombinedFt03RctRhs {
                baseline,
                combined: baseline,
                rct: None,
            })
        }
        RctSelection::Escaping { provider, closure } => (provider, closure),
    };
    let rct = provider.closed_events(&model.gas, state, closure)?;
    let mut combined = baseline;
    for i in 0..3 {
        combined.derivative[i] += rct.event.fraction_rate_s[i];
    }
    combined.derivative[3] += rct.thermal_energy_rate_erg_cm3_s;
    combined.escaped_energy_rate += rct.escaped_energy_rate_erg_cm3_s;
    if combined.derivative.iter().any(|x| !x.is_finite())
        || !combined.escaped_energy_rate.is_finite()
    {
        return Err(ForwardError::InvalidInput("RCT_COMPOSED_OVERFLOW"));
    }
    Ok(CombinedFt03RctRhs {
        baseline,
        combined,
        rct: Some(rct),
    })
}
