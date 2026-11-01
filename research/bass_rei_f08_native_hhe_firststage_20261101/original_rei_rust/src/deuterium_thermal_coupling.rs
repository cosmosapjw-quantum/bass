//! Explicit component ownership, not a full-network composition or timestep.
//! The guarantee applies to this interface; legacy low-level kernels remain
//! available for callers who intentionally bypass this component.
use crate::deuterium_atomic::{d_atomic_rhs,DAtomicError,DAtomicProvider,DAtomicRhs,
    DChargeExchange,DPhotoInput};
use crate::deuterium_charge_exchange::DhState;
use crate::deuterium_thermal_charge_exchange::{integrate_si,savin_provider,
    ThermalCxControls,ThermalCxSiResult};
use crate::{IsotopeNumberState,IsotopeSpecies};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum CxOwnership { AtomicRhs, ThermalSubstep }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ThermalCouplingError { AtomicRhsOwnsCx, UnsupportedSpectator, InvalidState }

/// Private immutable provider/owner: no independently selectable RHS CX flag.
#[derive(Clone, Copy, Debug)]
pub struct ThermalCxComponent { provider:DAtomicProvider, owner:CxOwnership }
#[derive(Clone, Debug)]
pub struct OwnedAtomicContribution {
    pub owner:CxOwnership,
    /// Instantaneous species derivatives and powers [J m^-3 s^-1].
    /// This method advances no state and integrates no energy.
    pub instantaneous_atomic_rhs:DAtomicRhs,
}
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct IntegratedCxEnergy {
    pub chemical_delta_j_m3:f64,
    pub thermal_delta_j_m3:f64,
    pub photon_input_j_m3:f64,
    pub escaped_j_m3:f64,
}
#[derive(Clone, Debug)]
pub struct OwnedThermalSubstep {
    pub owner:CxOwnership,
    pub thermal_map:ThermalCxSiResult,
    /// By-value last accepted state; partial results are not a full-dt commit.
    pub isotope_state:Option<IsotopeNumberState>,
    /// One integrated CX ledger, never a second instantaneous cooling power.
    pub integrated_cx_energy:Option<IntegratedCxEnergy>,
}
impl ThermalCxComponent {
    pub fn new(provider:DAtomicProvider,owner:CxOwnership) -> Self {Self {provider,owner}}
    pub fn owner(&self) -> CxOwnership {self.owner}
    pub fn rhs(&self,state:&IsotopeNumberState,temperature_k:f64,photo:&DPhotoInput)
        -> Result<OwnedAtomicContribution,DAtomicError> {
        let cx=match self.owner {
            CxOwnership::AtomicRhs=>DChargeExchange::Savin2002,
            CxOwnership::ThermalSubstep=>DChargeExchange::Disabled,
        };
        Ok(OwnedAtomicContribution {owner:self.owner,
            instantaneous_atomic_rhs:d_atomic_rhs(self.provider,state,temperature_k,photo,cx)?})
    }
    pub fn thermal_substep(&self,state:&IsotopeNumberState,thermal_j_m3:f64,
        requested_s:f64,controls:ThermalCxControls)
        -> Result<OwnedThermalSubstep,ThermalCouplingError> {
        // Ownership guard precedes provider calls, conversion and integration.
        if self.owner!=CxOwnership::ThermalSubstep {
            return Err(ThermalCouplingError::AtomicRhsOwnsCx);
        }
        use IsotopeSpecies::{H1Neutral,H1Ionized,DNeutral,DIonized};
        for species in IsotopeSpecies::ALL {
            if !matches!(species,H1Neutral|H1Ionized|DNeutral|DIonized)
                && state.density_m3(species)!=0.0 {
                return Err(ThermalCouplingError::UnsupportedSpectator);
            }
        }
        let initial=DhState {h0_m3:state.density_m3(H1Neutral),
            hp_m3:state.density_m3(H1Ionized),d0_m3:state.density_m3(DNeutral),
            dp_m3:state.density_m3(DIonized),thermal_j_m3};
        // Exactly the bound atomic provider's defect, never a second parameter.
        let thermal_map=integrate_si(initial,self.provider.defect(),&savin_provider(),requested_s,controls);
        let isotope_state=if let Some(s)=thermal_map.state_si {
            let mut values=[0.0;13];
            values[H1Neutral as usize]=s.h0_m3;values[H1Ionized as usize]=s.hp_m3;
            values[DNeutral as usize]=s.d0_m3;values[DIonized as usize]=s.dp_m3;
            Some(IsotopeNumberState::new(values).map_err(|_|ThermalCouplingError::InvalidState)?)
        } else {None};
        let integrated_cx_energy=match (thermal_map.integrated_chemical_delta_j_m3,
            thermal_map.integrated_thermal_delta_j_m3) {
            (Some(chemical),Some(thermal))=>Some(IntegratedCxEnergy {
                chemical_delta_j_m3:chemical,thermal_delta_j_m3:thermal,
                photon_input_j_m3:0.0,escaped_j_m3:0.0}),
            _=>None,
        };
        Ok(OwnedThermalSubstep {owner:self.owner,thermal_map,isotope_state,integrated_cx_energy})
    }
}
