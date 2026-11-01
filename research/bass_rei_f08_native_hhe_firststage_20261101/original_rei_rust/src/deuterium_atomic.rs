//! Explicit H-equality D atomic approximation and isotope-native point RHS.
//!
//! GRACKLE_3_4_1_H_EQUALITY_D_ATOMIC_V1 reuses the selected H CI, Case-A RR,
//! RR kinetic cooling and CE coefficients. The D photo cross section is the
//! existing HI fit gated at the caller's D binding threshold. Neither is an
//! exact isotope-specific atomic calculation. No abundances, donor, default
//! activation, expansion or cosmological integration are supplied here.

use crate::deuterium_charge_exchange::{
    step_frozen_rates, DhEnergyDefect, DhError, DhState, DhStep, Savin2002,
};
use crate::rate_table::{IgmRateBackend, PreparedIgmRates};
use crate::{Absorber, AtomicProvider, ForwardError, HHeModel, IsotopeNumberState, IsotopeSpecies};

pub const MODEL_ID: &str = "GRACKLE_3_4_1_H_EQUALITY_D_ATOMIC_V1";
pub const GRACKLE_COMMIT: &str = "af7939494ce65007887ada7b98d1813df6843346";
pub const PHOTO_APPROXIMATION: &str = "threshold-corrected H-equality: sigma_D(E)=sigma_HI(E) for E>=chi_D, zero below; not exact D cross section";

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum DAtomicError {
    InvalidInput,
    NonFiniteInput,
    Arithmetic,
    TemperatureDomain,
    PhotonEnergyDomain,
    PhotoThresholdMismatch,
    HydrogenProvider,
    ChargeExchange(DhError),
}

fn nonnegative(value: f64) -> Result<f64, DAtomicError> {
    if !value.is_finite() {
        Err(DAtomicError::NonFiniteInput)
    } else if value < 0.0 {
        Err(DAtomicError::InvalidInput)
    } else {
        Ok(value)
    }
}

fn arithmetic(value: f64) -> Result<f64, DAtomicError> {
    if value.is_finite() {
        Ok(value)
    } else {
        Err(DAtomicError::Arithmetic)
    }
}

fn product(factors: &[f64]) -> Result<f64, DAtomicError> {
    for &factor in factors {
        nonnegative(factor)?;
    }
    if factors.contains(&0.0) {
        return Ok(0.0);
    }
    let mut value = 1.0;
    for &factor in factors {
        value = arithmetic(value * factor)?;
        if value == 0.0 {
            return Err(DAtomicError::Arithmetic);
        }
    }
    Ok(value)
}

fn ev_j() -> f64 {
    HHeModel::controlled_fixture().ev_erg * 1e-7
}

/// Both binding energies are explicit and used by every channel and CX.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct DAtomicProvider {
    chi_h_ev: f64,
    chi_d_ev: f64,
    threshold_source: &'static str,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct DAtomicRates {
    pub temperature_k: f64,
    pub ci_m3_s: f64,
    pub rr_case_a_m3_s: f64,
    pub rr_kinetic_j_m3_s: f64,
    pub ce_j_m3_s: f64,
    pub ci_floor_m3_s: f64,
    pub ce_cap_j_m3_s: f64,
    pub model_id: &'static str,
    pub source_commit: &'static str,
}

/// A bin-integrated, angle-integrated photon flux [m^-2 s^-1].
/// The caller supplies its transport/source conversion exactly once; no 4pi,
/// speed of light, or coordinate Jacobian is inserted by this interface.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct DPhotoBin {
    pub energy_ev: f64,
    pub photon_flux_m2_s: f64,
}

/// Constructed from actual cross-section/energy products with one threshold.
/// Private fields prevent independently guessed heat/Gamma pairs.
#[derive(Clone, Debug, PartialEq)]
pub struct DPhotoInput {
    gamma_s: f64,
    heat_j_per_absorber_s: f64,
    energy_j_per_absorber_s: f64,
    chi_d_ev: f64,
    threshold_source: &'static str,
    source: &'static str,
}

impl DPhotoInput {
    pub fn gamma_s(&self) -> f64 {
        self.gamma_s
    }
    pub fn heat_j_per_absorber_s(&self) -> f64 {
        self.heat_j_per_absorber_s
    }
    pub fn energy_j_per_absorber_s(&self) -> f64 {
        self.energy_j_per_absorber_s
    }
    pub fn source(&self) -> &'static str {
        self.source
    }
}

impl DAtomicProvider {
    /// No automatic 0.0037 eV choice: the caller names/provides its threshold.
    pub fn new(
        chi_h_ev: f64,
        chi_d_ev: f64,
        threshold_source: &'static str,
    ) -> Result<Self, DAtomicError> {
        nonnegative(chi_h_ev)?;
        nonnegative(chi_d_ev)?;
        if chi_h_ev <= 0.0 || chi_d_ev <= chi_h_ev || threshold_source.is_empty() {
            return Err(DAtomicError::InvalidInput);
        }
        Ok(Self {
            chi_h_ev,
            chi_d_ev,
            threshold_source,
        })
    }

    pub fn chi_h_ev(self) -> f64 {
        self.chi_h_ev
    }
    pub fn chi_d_ev(self) -> f64 {
        self.chi_d_ev
    }
    pub fn threshold_source(self) -> &'static str {
        self.threshold_source
    }
    pub fn defect(self) -> DhEnergyDefect {
        DhEnergyDefect {
            delta_chi_j: (self.chi_d_ev - self.chi_h_ev) * ev_j(),
            source: self.threshold_source,
        }
    }

    /// Reuse the existing operational 1..=1e6 K provider without a second fit.
    pub fn rates(self, temperature_k: f64) -> Result<DAtomicRates, DAtomicError> {
        if !temperature_k.is_finite() {
            return Err(DAtomicError::NonFiniteInput);
        }
        if !(1.0..=1e6).contains(&temperature_k) {
            return Err(DAtomicError::TemperatureDomain);
        }
        let prepared = IgmRateBackend::Direct.prepare(temperature_k)
            .map_err(|_| DAtomicError::HydrogenProvider)?;
        Ok(self.rates_from_prepared(&prepared))
    }

    /// Project the selected H-equality channels from the same prepared bundle.
    /// Its temperature and numerical evaluator remain available on the bundle.
    pub fn rates_from_prepared(self, prepared: &PreparedIgmRates) -> DAtomicRates {
        let temperature_k = prepared.temperature_k();
        let h = prepared.rates();
        DAtomicRates {
            temperature_k,
            ci_m3_s: h.ci_cm3_s[0] * 1e-6,
            rr_case_a_m3_s: h.rr_cm3_s[0] * 1e-6,
            rr_kinetic_j_m3_s: h.rr_cooling_erg_cm3_s[0] * 1e-13,
            ce_j_m3_s: h.ce_erg[0] * 1e-13,
            ci_floor_m3_s: h.diagnostics.ci_floor_cm3_s[0] * 1e-6,
            ce_cap_j_m3_s: h.diagnostics.ce_cap_erg[0] * 1e-13,
            model_id: MODEL_ID,
            source_commit: GRACKLE_COMMIT,
        }
    }

    pub fn cross_section_m2(self, energy_ev: f64) -> Result<f64, DAtomicError> {
        nonnegative(energy_ev)?;
        if energy_ev > 50_000.0 {
            return Err(DAtomicError::PhotonEnergyDomain);
        }
        if energy_ev < self.chi_d_ev {
            return Ok(0.0);
        }
        AtomicProvider::reference()
            .cross_section(Absorber::HI, energy_ev)
            .map(|sigma_cm2| sigma_cm2 * 1e-4)
            .map_err(|_: ForwardError| DAtomicError::HydrogenProvider)
    }

    pub fn photo_input(
        self,
        bins: &[DPhotoBin],
        source: &'static str,
    ) -> Result<DPhotoInput, DAtomicError> {
        if source.is_empty() {
            return Err(DAtomicError::InvalidInput);
        }
        let mut gamma_s = 0.0;
        let mut heat = 0.0;
        let mut energy = 0.0;
        for bin in bins {
            nonnegative(bin.photon_flux_m2_s)?;
            let sigma = self.cross_section_m2(bin.energy_ev)?;
            let events = product(&[sigma, bin.photon_flux_m2_s])?;
            gamma_s = arithmetic(gamma_s + events)?;
            if events != 0.0 {
                heat =
                    arithmetic(heat + product(&[events, bin.energy_ev - self.chi_d_ev, ev_j()])?)?;
                energy = arithmetic(energy + product(&[events, bin.energy_ev, ev_j()])?)?;
            }
        }
        Ok(DPhotoInput {
            gamma_s,
            heat_j_per_absorber_s: heat,
            energy_j_per_absorber_s: energy,
            chi_d_ev: self.chi_d_ev,
            threshold_source: self.threshold_source,
            source,
        })
    }

    /// Explicit externally bound absorption moments. The caller must obtain
    /// Gamma and heat from the same D absorption events and identify that
    /// source; this validation does not establish a spectrum or photon budget.
    pub fn photo_input_from_bound_rates(
        self,
        gamma_s: f64,
        heat_j_per_absorber_s: f64,
        source: &'static str,
    ) -> Result<DPhotoInput, DAtomicError> {
        nonnegative(gamma_s)?;
        nonnegative(heat_j_per_absorber_s)?;
        if source.is_empty() || (gamma_s == 0.0 && heat_j_per_absorber_s != 0.0) {
            return Err(DAtomicError::InvalidInput);
        }
        Ok(DPhotoInput {
            gamma_s,
            heat_j_per_absorber_s,
            energy_j_per_absorber_s: arithmetic(
                self.chi_d_ev * ev_j() * gamma_s + heat_j_per_absorber_s,
            )?,
            chi_d_ev: self.chi_d_ev,
            threshold_source: self.threshold_source,
            source,
        })
    }

    /// Optional reuse of the standalone exact frozen-rate CX map, with the
    /// very same binding defect as the point RHS. No full-chemistry step here.
    /// Do not also integrate an RHS with DChargeExchange::Savin2002 during
    /// this split substep; that would count the CX reaction twice.
    pub fn step_charge_exchange(
        self,
        state: DhState,
        temperature_k: f64,
        dt_s: f64,
    ) -> Result<DhStep, DAtomicError> {
        let rates = Savin2002::rates(temperature_k).map_err(DAtomicError::ChargeExchange)?;
        step_frozen_rates(state, rates, dt_s, self.defect()).map_err(DAtomicError::ChargeExchange)
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum DChargeExchange {
    Disabled,
    Savin2002,
}

/// D+ supplies one electron, one heavy ion and Z^2=1 to caller-owned global
/// electron, free-free and CMB routines. No such power is duplicated here.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct DPlasmaContributions {
    pub electrons_m3: f64,
    pub ions_m3: f64,
    pub freefree_z2_ions_m3: f64,
}

pub fn d_plasma_contributions(state: &IsotopeNumberState) -> DPlasmaContributions {
    let dp = state.density_m3(IsotopeSpecies::DIonized);
    DPlasmaContributions {
        electrons_m3: dp,
        ions_m3: dp,
        freefree_z2_ions_m3: dp,
    }
}

/// Signed power densities [J m^-3 s^-1], positive escape and photon input.
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct DEnergyLedger {
    pub thermal: f64,
    pub chemical: f64,
    pub escape: f64,
    pub photon_input: f64,
}

impl DEnergyLedger {
    pub fn residual(self) -> f64 {
        self.thermal + self.chemical + self.escape - self.photon_input
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct DAtomicRhs {
    /// Chemical derivatives only [m^-3 s^-1], same registry order as state.
    pub species_m3_s: [f64; 13],
    pub electron_m3_s: f64,
    pub photo_events_m3_s: f64,
    pub ci_events_m3_s: f64,
    pub rr_events_m3_s: f64,
    pub cx_forward_events_m3_s: f64,
    pub cx_reverse_events_m3_s: f64,
    /// PI, CI, RR, CE, CX forward, CX reverse; one energy owner per channel.
    pub channel_energy: [DEnergyLedger; 6],
    pub energy: DEnergyLedger,
    pub ci_floor_events_m3_s: f64,
    pub ce_cap_cooling_j_m3_s: f64,
    pub electron_density_m3: f64,
    pub thermal_particle_density_m3: f64,
    /// D/CX contribution at the supplied common temperature, no expansion.
    pub temperature_k_s: f64,
    pub rates: DAtomicRates,
    pub plasma: DPlasmaContributions,
}

/// Isotope-native proper-volume point evaluator. Other isotopes contribute
/// their electrons to ne and remain passive. This is an additive D/CX RHS;
/// the caller owns H/He reactions, photon transport, free-free, CMB and FLRW.
pub fn d_atomic_rhs(
    provider: DAtomicProvider,
    state: &IsotopeNumberState,
    temperature_k: f64,
    photo: &DPhotoInput,
    cx: DChargeExchange,
) -> Result<DAtomicRhs, DAtomicError> {
    if photo.chi_d_ev != provider.chi_d_ev || photo.threshold_source != provider.threshold_source {
        return Err(DAtomicError::PhotoThresholdMismatch);
    }
    let rates = provider.rates(temperature_k)?;
    let moments = state.moments().map_err(|_| DAtomicError::Arithmetic)?;
    let ne = moments.neutral_free_electron_density_m3;
    let n = |species| state.density_m3(species);
    use IsotopeSpecies::{DIonized, DNeutral, H1Ionized, H1Neutral};
    let (d0, dp) = (n(DNeutral), n(DIonized));
    let pi = product(&[d0, photo.gamma_s])?;
    let ci = product(&[ne, d0, rates.ci_m3_s])?;
    let rr = product(&[ne, dp, rates.rr_case_a_m3_s])?;
    let (cxf, cxr) = match cx {
        DChargeExchange::Disabled => (0.0, 0.0),
        DChargeExchange::Savin2002 => {
            let r = Savin2002::rates(temperature_k).map_err(DAtomicError::ChargeExchange)?;
            (
                product(&[r.forward_m3_s, d0, n(H1Ionized)])?,
                product(&[r.reverse_m3_s, dp, n(H1Neutral)])?,
            )
        }
    };
    let chi = provider.chi_d_ev * ev_j();
    let pi_heat = product(&[d0, photo.heat_j_per_absorber_s])?;
    let pi_chemical = product(&[chi, pi])?;
    let ci_chemical = product(&[chi, ci])?;
    let rr_chemical_loss = product(&[chi, rr])?;
    let rr_kinetic = product(&[ne, dp, rates.rr_kinetic_j_m3_s])?;
    let ce = product(&[ne, d0, rates.ce_j_m3_s])?;
    let cxf_defect = product(&[provider.defect().delta_chi_j, cxf])?;
    let cxr_defect = product(&[provider.defect().delta_chi_j, cxr])?;
    let channel_energy = [
        DEnergyLedger {
            thermal: pi_heat,
            chemical: pi_chemical,
            escape: 0.0,
            photon_input: product(&[d0, photo.energy_j_per_absorber_s])?,
        },
        DEnergyLedger {
            thermal: -ci_chemical,
            chemical: ci_chemical,
            ..DEnergyLedger::default()
        },
        DEnergyLedger {
            thermal: -rr_kinetic,
            chemical: -rr_chemical_loss,
            escape: arithmetic(rr_kinetic + rr_chemical_loss)?,
            photon_input: 0.0,
        },
        DEnergyLedger {
            thermal: -ce,
            escape: ce,
            ..DEnergyLedger::default()
        },
        DEnergyLedger {
            thermal: -cxf_defect,
            chemical: cxf_defect,
            ..DEnergyLedger::default()
        },
        DEnergyLedger {
            thermal: cxr_defect,
            chemical: -cxr_defect,
            ..DEnergyLedger::default()
        },
    ];
    let mut energy = DEnergyLedger::default();
    for row in channel_energy {
        energy.thermal = arithmetic(energy.thermal + row.thermal)?;
        energy.chemical = arithmetic(energy.chemical + row.chemical)?;
        energy.escape = arithmetic(energy.escape + row.escape)?;
        energy.photon_input = arithmetic(energy.photon_input + row.photon_input)?;
    }
    let atomic_net = arithmetic(pi + ci - rr)?;
    let cx_net = arithmetic(cxf - cxr)?;
    let d_net = arithmetic(atomic_net + cx_net)?;
    let mut species_m3_s = [0.0; 13];
    species_m3_s[H1Neutral as usize] = cx_net;
    species_m3_s[H1Ionized as usize] = -cx_net;
    species_m3_s[DNeutral as usize] = -d_net;
    species_m3_s[DIonized as usize] = d_net;
    let particles = arithmetic(moments.heavy_particle_density_m3 + ne)?;
    let temperature_k_s = if particles == 0.0 {
        0.0
    } else {
        arithmetic(
            2.0 * energy.thermal
                / (3.0 * HHeModel::controlled_fixture().kb_erg_k * 1e-7 * particles)
                - temperature_k * atomic_net / particles,
        )?
    };
    Ok(DAtomicRhs {
        species_m3_s,
        electron_m3_s: atomic_net,
        photo_events_m3_s: pi,
        ci_events_m3_s: ci,
        rr_events_m3_s: rr,
        cx_forward_events_m3_s: cxf,
        cx_reverse_events_m3_s: cxr,
        channel_energy,
        energy,
        ci_floor_events_m3_s: product(&[ne, d0, rates.ci_floor_m3_s])?,
        ce_cap_cooling_j_m3_s: product(&[ne, d0, rates.ce_cap_j_m3_s])?,
        electron_density_m3: ne,
        thermal_particle_density_m3: particles,
        temperature_k_s,
        rates,
        plasma: d_plasma_contributions(state),
    })
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum DInventoryKind {
    ObservationConditionedPrimordialRatio,
    PublishedBbnConditionedRatio,
    ExplicitConditionalScenario,
}

/// Explicit number ratio n_D/n_1H. No value or ionic fraction is defaulted.
/// An observation-conditioned ratio is not a matched REC or new BBN donor.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct DInventory {
    pub ratio_d_to_h1: f64,
    pub uncertainty: Option<f64>,
    pub uncertainty_definition: &'static str,
    pub kind: DInventoryKind,
    pub source: &'static str,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum DInitialIonization {
    Explicit {
        fraction: f64,
        source: &'static str,
    },
    /// Conditional frozen H/D CX balance; PI/CI/RR and cosmological D
    /// recombination are neglected for this initialization only.
    FrozenChargeExchangeBalance {
        temperature_k: f64,
    },
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct ConditionalHDHe4State {
    pub state: IsotopeNumberState,
    pub inventory: DInventory,
    pub ionization: DInitialIonization,
    pub dplus_fraction: f64,
    pub baryon_density_m3: f64,
    pub inventory_scope: &'static str,
}

/// Construct ONLY an H1/D/He4 inventory with fixed nb=nH1+2nD+4nHe4.
/// This is explicitly conditional, not a matched REC donor. fHe is nHe4/nH1;
/// hplus and [He+,He++] fractions are explicit caller data. Neutron, T, He3
/// and any omitted nuclei are absent by this named model, not counted in nb.
/// A caller with those inventories must construct its complete isotope state
/// directly rather than using this three-nuclide normalization.
pub fn conditional_h1_d_he4_state(
    baryon_density_m3: f64,
    helium4_to_h1: f64,
    hplus_fraction: f64,
    helium4_ion_fractions: [f64; 2],
    inventory: DInventory,
    ionization: DInitialIonization,
) -> Result<ConditionalHDHe4State, DAtomicError> {
    for x in [
        baryon_density_m3,
        helium4_to_h1,
        hplus_fraction,
        helium4_ion_fractions[0],
        helium4_ion_fractions[1],
        inventory.ratio_d_to_h1,
    ] {
        nonnegative(x)?;
    }
    if baryon_density_m3 == 0.0
        || hplus_fraction > 1.0
        || helium4_ion_fractions[0] + helium4_ion_fractions[1] > 1.0
        || inventory.source.is_empty()
        || inventory.uncertainty_definition.is_empty()
    {
        return Err(DAtomicError::InvalidInput);
    }
    if let Some(uncertainty) = inventory.uncertainty {
        nonnegative(uncertainty)?;
    }
    let denominator = arithmetic(1.0 + 2.0 * inventory.ratio_d_to_h1 + 4.0 * helium4_to_h1)?;
    let nh = arithmetic(baryon_density_m3 / denominator)?;
    if nh == 0.0 {
        return Err(DAtomicError::Arithmetic);
    }
    let nd = product(&[inventory.ratio_d_to_h1, nh])?;
    let nhe = product(&[helium4_to_h1, nh])?;
    let xd = match ionization {
        DInitialIonization::Explicit { fraction, source } => {
            nonnegative(fraction)?;
            if fraction > 1.0 || source.is_empty() {
                return Err(DAtomicError::InvalidInput);
            }
            fraction
        }
        DInitialIonization::FrozenChargeExchangeBalance { temperature_k } => {
            let r = Savin2002::rates(temperature_k).map_err(DAtomicError::ChargeExchange)?;
            let forward = product(&[r.forward_m3_s, hplus_fraction])?;
            let reverse = product(&[r.reverse_m3_s, 1.0 - hplus_fraction])?;
            let relaxation = arithmetic(forward + reverse)?;
            if relaxation == 0.0 {
                return Err(DAtomicError::InvalidInput);
            }
            forward / relaxation
        }
    };
    let mut ns = [0.0; 13];
    use IsotopeSpecies::*;
    ns[H1Neutral as usize] = product(&[nh, 1.0 - hplus_fraction])?;
    ns[H1Ionized as usize] = product(&[nh, hplus_fraction])?;
    ns[DNeutral as usize] = product(&[nd, 1.0 - xd])?;
    ns[DIonized as usize] = product(&[nd, xd])?;
    ns[He4Neutral as usize] = product(&[
        nhe,
        1.0 - (helium4_ion_fractions[0] + helium4_ion_fractions[1]),
    ])?;
    ns[He4SinglyIonized as usize] = product(&[nhe, helium4_ion_fractions[0]])?;
    ns[He4DoublyIonized as usize] = product(&[nhe, helium4_ion_fractions[1]])?;
    let state = IsotopeNumberState::new(ns).map_err(|_| DAtomicError::Arithmetic)?;
    Ok(ConditionalHDHe4State {
        state,
        inventory,
        ionization,
        dplus_fraction: xd,
        baryon_density_m3,
        inventory_scope: "CONDITIONAL_H1_D_HE4_ONLY_NO_MATCHED_REC_DONOR",
    })
}
