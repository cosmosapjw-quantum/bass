//! Rust-only fixed-input microphysics kernels and synthetic static H/He microsteps.
//! f64 tests are implementation evidence, not a validated enclosure.
//! The original four-group N is comoving count per cMpc^3; atomic densities are proper cm^-3.
//! Synthetic three-group H/He photons are proper cm^-3.
#![forbid(unsafe_code)]

mod adaptive_history;
mod angular_photons;
mod atomic_provider;
pub mod axisym_contract;
pub mod axisym_coupling;
pub mod axisym_radiation;
pub mod axisym_sources;
mod bianchi_i;
pub mod coverage;
pub mod deuterium_charge_exchange;
mod ft03_controlled;
mod ft03_interval;
mod ft03_rates;
mod group_rates;
mod hhe_events;
mod homogeneous_rates;
mod hydrogen_step;
mod interval_ad;
mod interval_math;
pub mod isotope_state;
mod joint_affine;
mod lift;
mod microstep;
mod thermal;

pub use adaptive_history::{
    certified_ft03_trial, scaled as ft03_scaled, try_certified_ft03_step, CertifiedTrial, RootSite,
};
pub use angular_photons::{PhotonBins, PhotonGrid, PhotonPacket, RadiationState};
pub use atomic_provider::{
    Absorber, AtomicProvider, CoefficientUnits, ObservableKind, RawCoefficient, RawProcess,
    RawRecord, RecombinationCase, SourceFrame, TemperatureDomain,
};
pub use axisym_contract::{
    AxisymContractError, AxisymRunContract, AxisymmetryStatus, Clock, ClosureChoice, ExecutionMode,
    Frame, GeometryOnlyAdmission, ICProviderRecord, MuReflectionStatus, ProviderDomain,
    ProviderErrorStatus, ProviderRecord, RadiationUnits, SourceProviderRecord, SymmetryRecord,
};
pub use axisym_coupling::{isotropic_expansion_terms, IsotropicExpansionTerms};
pub use axisym_radiation::{AxisymPhotonLedgerContract, AxisymPhotonStep};
pub use axisym_sources::{
    validate_routing, ExcessPartition, PhotoEventLedger, PhotonRouting, PrimaryPhotoEvent,
};
pub use bianchi_i::{
    AxisymmetricPoint, CharacteristicRay, ConstantAxisymmetricBackground, ConstantHubbleBackground,
    GeometryBackground, GeometrySnapshot, RayDerivative,
};
pub use ft03_controlled::{
    ft03_adaptive_step, ft03_implicit_step, ft03_rhs, ft03_try_step, Ft03Events, Ft03Model,
    Ft03Rhs, Ft03Step, FT03_MODEL_ID,
};
pub use ft03_interval::ft03_interval_rhs;
pub use ft03_rates::{ft03_coefficients, Ft03Coefficients};
pub use group_rates::{
    gamma_species, opacity_cMpc_inv, pchip_eval, photon_rates, transform_z_to_y, PchipTable,
    C_LIGHT, MPC_CM,
};
pub use hhe_events::{hhe_rhs, HHeEvents, HHeModel, HHeRhs, HHeState};
pub use homogeneous_rates::{
    homogeneous_opacity, homogeneous_photo_rates, HomogeneousPhotoRates, OpacityOwners, PhotonNode,
};
pub use hydrogen_step::{hydrogen_step, HydrogenRates, HydrogenStep};
pub use interval_ad::Jet;
pub use interval_math::Interval;
pub use isotope_state::{
    IsotopeNumberMoments, IsotopeNumberState, IsotopeSpecies, LegacyHHeEosSnapshot,
    LegacyHHeProjection,
};
pub use joint_affine::{
    below_strict_error_limit, joint_affine_difference, AffineEnclosure, ClosedInterval, JointParent,
};
pub use lift::{positive_mass_projection, signed_transfer_lift};
pub use microstep::{adaptive_hhe_step, implicit_hhe_step, try_hhe_step, HHeStep, StepControl};

#[derive(Debug, Clone)]
pub struct State {
    pub n_comoving_per_cmpc3: [f64; 4],
    pub x_hii: f64,
    /// HeI, HeII, HeIII fractions.
    pub helium: [f64; 3],
    pub u_erg_per_cm3: f64,
    pub gamma_hi_per_s: f64,
}

#[derive(Debug, Clone)]
pub struct GroupParams {
    pub redshift: f64,
    pub n_h_proper_per_cm3: f64,
    pub n_he_proper_per_cm3: f64,
    pub hubble_per_s: f64,
    pub sigma_hi_cm2: [f64; 4],
    pub sigma_hei_cm2: [f64; 4],
    pub sigma_heii_cm2: [f64; 4],
    pub redshift_coeff: [f64; 4],
    pub source_fraction: [f64; 4],
    pub lowgroup_log_opacity: [PchipTable; 2],
}

#[derive(Debug, Clone)]
pub struct GammaSpecies {
    pub hi_per_s: f64,
    pub hei_per_s: f64,
    pub heii_per_s: f64,
    pub group_hi_per_s: [f64; 4],
}

#[derive(Debug, Clone)]
pub struct SignedLift {
    pub positive: Vec<f64>,
    pub negative: Vec<f64>,
    pub signed: Vec<f64>,
}

#[derive(Debug, Clone)]
pub enum ForwardError {
    InvalidInput(&'static str),
    OutsideTableDomain { x: f64, lower: f64, upper: f64 },
    InfeasibleZeroPriorSupport,
    MissingAuthority(&'static str),
}

impl ForwardError {
    pub fn code(&self) -> &'static str {
        match self {
            Self::InvalidInput(code) => code,
            Self::OutsideTableDomain { .. } => "OUTSIDE_TABLE_DOMAIN",
            Self::InfeasibleZeroPriorSupport => "INFEASIBLE_ZERO_PRIOR_SUPPORT",
            Self::MissingAuthority(_) => "MISSING_AUTHORITY",
        }
    }
}
impl std::fmt::Display for ForwardError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.code())
    }
}
impl std::error::Error for ForwardError {}

pub mod flrw_three_equations;

pub mod he_rct;

pub mod coupled_primary;
pub mod rux_adapter;

pub mod igm_background;
pub mod igm_state;
pub mod igm_rates;
pub mod igm_thermal;
pub mod axbi_rates;
pub mod axbi_background;
pub mod axbi_sources;
pub mod axbi_driver;
pub mod axbi_covariant_transport;
pub mod axbi_parallel;
pub mod axbi_q_reference;
pub mod axbi_q_advance;
pub mod axbi_q_capacity;
pub mod axbi_q_grid;
pub mod axbi_q_closure;

pub mod deuterium_atomic;
