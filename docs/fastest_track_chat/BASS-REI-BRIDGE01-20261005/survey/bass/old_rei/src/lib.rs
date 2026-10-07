//! Rust-only fixed-input microphysics kernels, not a thermochemistry solver.
//! f64 tests are implementation evidence, not a validated enclosure.
//! N is comoving count per cMpc^3; atomic densities are proper cm^-3.
#![forbid(unsafe_code)]

pub mod coverage;
mod group_rates;
mod lift;

pub use group_rates::{
    gamma_species, opacity_cMpc_inv, pchip_eval, photon_rates, transform_z_to_y, PchipTable,
    C_LIGHT, MPC_CM,
};
pub use lift::{positive_mass_projection, signed_transfer_lift};

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
