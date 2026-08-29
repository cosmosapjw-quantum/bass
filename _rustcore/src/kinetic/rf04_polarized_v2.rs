//! RF-04 polarized v2 route owner.
//!
//! Task RF04-POL-SCHEMA-01 intentionally lands the typed request/result
//! boundary before the numerical implementation.  The placeholder validators
//! make the retained RED reach assertions rather than import or compile
//! failures.  Tasks RF04-POL-GEOMETRY-02 and RF04-POL-COMPOSE-03 replace the
//! placeholder disposition without changing the frozen public route identity.

use std::fmt;

pub const SCHEMA_ID: &str = "bass-rf04-typeii-polarized-route/v2";
pub const TRAJECTORY_ROUTE_ID: &str = "kinetic.typeii.polarized_trajectory_v2";
pub const BATCH_ROUTE_ID: &str = "kinetic.typeii.polarized_batch_v2";

#[derive(Clone, Debug, PartialEq)]
pub struct RemapPlanV1 {
    pub schema_id: String,
    pub target_offsets: Vec<usize>,
    pub source_indices: Vec<usize>,
    pub weights: Vec<f64>,
    pub direction_grid_sha256: String,
    pub builder_id: String,
    pub builder_version: String,
    pub plan_sha256: String,
    pub minimum_transport_dot: f64,
}

#[derive(Clone, Debug, Default, PartialEq)]
pub struct PolarizedTrajectoryV2 {
    pub radiation_history: Vec<Vec<f64>>,
}

#[derive(Clone, Debug, Default, PartialEq)]
pub struct PolarizedBatchV2 {
    pub final_radiation: Vec<Vec<f64>>,
    pub member_status: Vec<i32>,
    pub member_completed_steps: Vec<i64>,
    pub member_error_code: Vec<Option<String>>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum Rf04PolarizedV2Error {
    Input { code: &'static str, detail: String },
    Capability { code: &'static str, detail: String },
    NotImplemented { code: &'static str, detail: String },
}

impl Rf04PolarizedV2Error {
    pub fn code(&self) -> &'static str {
        match self {
            Self::Input { code, .. }
            | Self::Capability { code, .. }
            | Self::NotImplemented { code, .. } => code,
        }
    }
}

impl fmt::Display for Rf04PolarizedV2Error {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        let detail = match self {
            Self::Input { detail, .. }
            | Self::Capability { detail, .. }
            | Self::NotImplemented { detail, .. } => detail,
        };
        write!(formatter, "{}: {detail}", self.code())
    }
}

impl std::error::Error for Rf04PolarizedV2Error {}

/// Validate a caller-supplied content-addressed CSR remap plan.
///
/// The numerical validator lands in RF04-POL-GEOMETRY-02.  Returning a typed
/// placeholder here is deliberate RED scaffolding: the focused tests compile,
/// call the production owner, and fail on the missing behavior.
pub fn validate_remap_plan_v1(
    _plan: &RemapPlanV1,
    _directions: &[[f64; 3]],
    _expected_direction_grid_sha256: &str,
) -> Result<(), Rf04PolarizedV2Error> {
    Err(Rf04PolarizedV2Error::NotImplemented {
        code: "RF04_POLARIZED_V2_NOT_IMPLEMENTED",
        detail: "content-addressed remap-plan validation is pending RF04-POL-GEOMETRY-02"
            .to_string(),
    })
}

/// Check that public history rows stay on the fixed Eulerian caller grid.
///
/// This placeholder exists so the history-association RED is an assertion
/// failure rather than an unresolved symbol.
pub fn validate_fixed_eulerian_history_shape(
    _history: &[Vec<f64>],
    _accepted_steps: usize,
    _direction_count: usize,
) -> Result<(), Rf04PolarizedV2Error> {
    Err(Rf04PolarizedV2Error::NotImplemented {
        code: "RF04_POLARIZED_V2_NOT_IMPLEMENTED",
        detail: "fixed-Eulerian history validation is pending RF04-POL-COMPOSE-03".to_string(),
    })
}
