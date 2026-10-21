//! Typed input contract for prescribed axisymmetric Bianchi-I geometry.
//!
//! `Option` records pending physical inputs without inventing values.  This is
//! a geometry-only execution boundary, not an implementation of a physical
//! ionization history or of `AXI_IC_SCHEMA.json`.
use crate::{ConstantAxisymmetricBackground, ForwardError, GeometryBackground};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ExecutionMode {
    GeometryOnly,
    PhysicalHistory,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Clock {
    GasProperSeconds,
    Other,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Frame {
    NonRotatingComovingOrthonormalTetrad,
    Other,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum RadiationUnits {
    SiPhotonNumberDensity,
    Other,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum AxisymmetryStatus {
    Unknown,
    CommonZAxis,
    Violated,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum MuReflectionStatus {
    Unknown,
    Even,
    NotEven,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ProviderErrorStatus {
    Unknown,
    Quantified,
}

#[derive(Clone, Debug, PartialEq)]
pub struct ProviderDomain {
    pub proper_time_s: [f64; 2],
    pub temperature_k: Option<[f64; 2]>,
    pub photon_energy_j: Option<[f64; 2]>,
}

#[derive(Clone, Debug, PartialEq)]
pub struct ProviderRecord {
    pub identity: String,
    pub version: Option<String>,
    pub domain: Option<ProviderDomain>,
    pub interpolation: Option<String>,
    pub error_status: ProviderErrorStatus,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct SymmetryRecord {
    pub axisymmetry: AxisymmetryStatus,
    pub mu_reflection: MuReflectionStatus,
}

#[derive(Clone, Debug, PartialEq)]
pub struct ICProviderRecord {
    pub provider: ProviderRecord,
    pub symmetry: SymmetryRecord,
}

#[derive(Clone, Debug, PartialEq)]
pub struct SourceProviderRecord {
    pub provider: ProviderRecord,
    pub symmetry: SymmetryRecord,
}

#[derive(Clone, Debug, PartialEq)]
pub enum ClosureChoice {
    CaseAExplicitDiffuse { provider: ProviderRecord },
    FullCoupledOts { provider: ProviderRecord },
}

#[derive(Clone, Debug, PartialEq)]
pub struct AxisymRunContract {
    pub background: ConstantAxisymmetricBackground,
    pub clock: Clock,
    pub frame: Frame,
    pub radiation_units: RadiationUnits,
    pub physical_ic: Option<ICProviderRecord>,
    pub source: Option<SourceProviderRecord>,
    pub atomic_provider: Option<ProviderRecord>,
    pub closure: Option<ClosureChoice>,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct GeometryOnlyAdmission;

#[derive(Debug)]
pub enum AxisymContractError {
    InvalidGeometry(ForwardError),
    UnsupportedClock,
    UnsupportedFrame,
    UnsupportedRadiationUnits,
    MissingPhysicalInitialCondition,
    MissingSource,
    MissingAtomicProvider,
    MissingClosure,
    PhysicalExecutionNotImplemented,
}

impl AxisymRunContract {
    pub fn pending_geometry(background: ConstantAxisymmetricBackground) -> Self {
        Self {
            background,
            clock: Clock::GasProperSeconds,
            frame: Frame::NonRotatingComovingOrthonormalTetrad,
            radiation_units: RadiationUnits::SiPhotonNumberDensity,
            physical_ic: None,
            source: None,
            atomic_provider: None,
            closure: None,
        }
    }

    pub fn validate_for(
        &self,
        mode: ExecutionMode,
    ) -> Result<GeometryOnlyAdmission, AxisymContractError> {
        if self.clock != Clock::GasProperSeconds {
            return Err(AxisymContractError::UnsupportedClock);
        }
        if self.frame != Frame::NonRotatingComovingOrthonormalTetrad {
            return Err(AxisymContractError::UnsupportedFrame);
        }
        if self.radiation_units != RadiationUnits::SiPhotonNumberDensity {
            return Err(AxisymContractError::UnsupportedRadiationUnits);
        }
        self.background
            .snapshot(self.background.time_domain_s[0])
            .map_err(AxisymContractError::InvalidGeometry)?;
        self.background
            .snapshot(self.background.reference_time_s)
            .map_err(AxisymContractError::InvalidGeometry)?;
        self.background
            .snapshot(self.background.time_domain_s[1])
            .map_err(AxisymContractError::InvalidGeometry)?;
        match mode {
            ExecutionMode::GeometryOnly => Ok(GeometryOnlyAdmission),
            ExecutionMode::PhysicalHistory => {
                if self.physical_ic.is_none() {
                    Err(AxisymContractError::MissingPhysicalInitialCondition)
                } else if self.source.is_none() {
                    Err(AxisymContractError::MissingSource)
                } else if self.atomic_provider.is_none() {
                    Err(AxisymContractError::MissingAtomicProvider)
                } else if self.closure.is_none() {
                    Err(AxisymContractError::MissingClosure)
                } else {
                    Err(AxisymContractError::PhysicalExecutionNotImplemented)
                }
            }
        }
    }
}
