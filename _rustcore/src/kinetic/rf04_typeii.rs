//! RF-04 Type-II public owner for the bounded scalar/fixed-grid/raw slice.
//!
//! The generated formulas and adaptive Kato-AEM2 implementation are linked
//! from their pinned repository locations. This module owns validation,
//! trajectory/batch semantics, diagnostics and capability admission only.

use rayon::prelude::*;
use std::fmt;

#[path = "../../../generated/rust/typeii/typeii_background.rs"]
mod typeii_background;
#[path = "../../../generated/rust/typeii/typeii_collision.rs"]
mod typeii_collision;
#[path = "../../../generated/rust/typeii/typeii_kato.rs"]
mod typeii_kato;
#[path = "../../../runtime/rust/typeii/typeii_krylov_adapt.rs"]
mod typeii_krylov_adapt;
#[path = "../../../runtime/rust/typeii/typeii_runtime.rs"]
mod typeii_runtime;

use typeii_krylov_adapt::{
    kato_aem2_step_adaptive, AdaptiveKrylovError, AdaptiveKrylovOptions, AdaptiveKrylovStats,
    AdaptiveKrylovTargetSemantics,
};

pub const SCHEMA_ID: &str = "bass-rf04-typeii-public-route/v1";
pub const TRAJECTORY_ROUTE_ID: &str = "kinetic.typeii.trajectory_v1";
pub const BATCH_ROUTE_ID: &str = "kinetic.typeii.batch_v1";

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum Carrier {
    ScalarIntensity,
    PolarizedRank9,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum QuadratureRoute {
    PairedRestToNormalReference,
    FixedGridRaw,
    FixedGridApCorrected,
}

#[derive(Clone, Debug, PartialEq)]
pub enum Rf04Error {
    Input { code: &'static str, detail: String },
    Capability { code: &'static str, detail: String },
    PhysicalDomain { code: &'static str, detail: String },
    Certificate { code: &'static str, detail: String },
    Member { code: &'static str, detail: String },
}

impl Rf04Error {
    pub fn code(&self) -> &'static str {
        match self {
            Self::Input { code, .. }
            | Self::Capability { code, .. }
            | Self::PhysicalDomain { code, .. }
            | Self::Certificate { code, .. }
            | Self::Member { code, .. } => code,
        }
    }

    fn with_step(self, step: usize) -> Self {
        let code = self.code();
        let detail = format!("step_index={step}; {self}");
        match self {
            Self::Input { .. } => Self::Input { code, detail },
            Self::Capability { .. } => Self::Capability { code, detail },
            Self::PhysicalDomain { .. } => Self::PhysicalDomain { code, detail },
            Self::Certificate { .. } => Self::Certificate { code, detail },
            Self::Member { .. } => Self::Member { code, detail },
        }
    }
}

impl fmt::Display for Rf04Error {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        let detail = match self {
            Self::Input { detail, .. }
            | Self::Capability { detail, .. }
            | Self::PhysicalDomain { detail, .. }
            | Self::Certificate { detail, .. }
            | Self::Member { detail, .. } => detail,
        };
        write!(formatter, "{}: {detail}", self.code())
    }
}

impl std::error::Error for Rf04Error {}

#[derive(Clone, Debug, Default)]
pub struct ActionLedger {
    pub accepted_steps: usize,
    pub rejected_steps: usize,
    pub nonfinite_rejections: usize,
    pub matvecs: usize,
    pub projected_exponentials: usize,
    pub max_basis: usize,
    pub final_basis: usize,
    pub max_attempt_error_ratio: f64,
    pub max_accepted_error_ratio: f64,
    pub last_accepted_error_ratio: f64,
    pub target_semantics: &'static str,
}

impl From<&AdaptiveKrylovStats> for ActionLedger {
    fn from(stats: &AdaptiveKrylovStats) -> Self {
        let target_semantics = match stats.target_semantics {
            AdaptiveKrylovTargetSemantics::ResidualEstimateOnly => {
                "PROJECTED_RESIDUAL_TARGET_RATIO_ONLY"
            }
            AdaptiveKrylovTargetSemantics::CallerDividedResidualEstimate { .. } => {
                "CALLER_DIVIDED_PROJECTED_RESIDUAL_TARGET_RATIO_ONLY"
            }
            AdaptiveKrylovTargetSemantics::MixedResidualEstimates => {
                "MIXED_PROJECTED_RESIDUAL_TARGET_RATIOS_ONLY"
            }
        };
        Self {
            accepted_steps: stats.accepted_steps,
            rejected_steps: stats.rejected_steps,
            nonfinite_rejections: stats.nonfinite_rejections,
            matvecs: stats.matvecs,
            projected_exponentials: stats.projected_exponentials,
            max_basis: stats.max_basis,
            final_basis: stats.final_basis,
            max_attempt_error_ratio: stats.max_attempt_error_ratio,
            max_accepted_error_ratio: stats.max_accepted_error_ratio,
            last_accepted_error_ratio: stats.last_accepted_error_ratio,
            target_semantics,
        }
    }
}

#[derive(Clone, Debug, Default)]
pub struct ScalarDiagnostics {
    pub equilibrium_null_residual: Vec<f64>,
    pub right_kernel_residual: Vec<f64>,
    pub left_invariant_drift: Vec<f64>,
    pub projected_residual_estimate: Vec<f64>,
    pub projector_idempotence_residual: Vec<f64>,
    pub positivity_margin: Vec<f64>,
    pub action_ledger: Vec<ActionLedger>,
}

#[derive(Clone, Debug, Default)]
pub struct ScalarTrajectory {
    pub radiation_history: Vec<Vec<f64>>,
    pub diagnostics: ScalarDiagnostics,
}

#[derive(Clone, Debug, Default)]
pub struct ScalarBatch {
    pub final_radiation: Vec<Vec<f64>>,
    pub member_status: Vec<i32>,
    pub member_completed_steps: Vec<i64>,
    pub member_error_code: Vec<Option<String>>,
}

pub fn parse_carrier(value: &str) -> Result<Carrier, Rf04Error> {
    match value {
        "scalar_intensity_v1" => Ok(Carrier::ScalarIntensity),
        "polarized_rank9_v1" => Ok(Carrier::PolarizedRank9),
        _ => Err(Rf04Error::Capability {
            code: "RF04_UNSUPPORTED_CAPABILITY",
            detail: format!("unsupported carrier {value:?}"),
        }),
    }
}

pub fn parse_quadrature_route(value: &str) -> Result<QuadratureRoute, Rf04Error> {
    match value {
        "paired_rest_to_normal_reference_v1" => Ok(QuadratureRoute::PairedRestToNormalReference),
        "fixed_grid_raw_v1" => Ok(QuadratureRoute::FixedGridRaw),
        "fixed_grid_ap_corrected_v1" => Ok(QuadratureRoute::FixedGridApCorrected),
        _ => Err(Rf04Error::Capability {
            code: "RF04_UNSUPPORTED_CAPABILITY",
            detail: format!("unsupported quadrature route {value:?}"),
        }),
    }
}

pub fn require_supported(carrier: Carrier, route: QuadratureRoute) -> Result<(), Rf04Error> {
    if carrier == Carrier::ScalarIntensity && route == QuadratureRoute::FixedGridRaw {
        Ok(())
    } else {
        Err(Rf04Error::Capability {
            code: "RF04_UNSUPPORTED_CAPABILITY",
            detail: format!("unsupported RF-04 slice combination {carrier:?}/{route:?}"),
        })
    }
}

#[allow(clippy::too_many_arguments)]
fn validate_common_plan(
    directions: &[[f64; 3]],
    weights: &[f64],
    background_q1: &[[f64; 5]],
    background_mid: &[[f64; 5]],
    background_q3: &[[f64; 5]],
    opacity_mid: &[f64],
    step_size: &[f64],
    gamma: f64,
    opacity_scale: f64,
    axis: usize,
) -> Result<(), Rf04Error> {
    if directions.len() < 2 || directions.len() != weights.len() {
        return Err(Rf04Error::Input {
            code: "RF04_INVALID_GRID",
            detail: "directions and weights must share at least two nodes".to_string(),
        });
    }
    if axis >= 3 {
        return Err(Rf04Error::Input {
            code: "RF04_INVALID_GRID",
            detail: "tilt axis must be 0, 1 or 2".to_string(),
        });
    }
    for (node, direction) in directions.iter().enumerate() {
        if !direction.iter().all(|value| value.is_finite()) {
            return Err(Rf04Error::Input {
                code: "RF04_INVALID_GRID",
                detail: format!("direction node {node} is nonfinite"),
            });
        }
        let norm = direction
            .iter()
            .map(|value| value * value)
            .sum::<f64>()
            .sqrt();
        if !norm.is_finite() || (norm - 1.0).abs() > 1.0e-10 {
            return Err(Rf04Error::Input {
                code: "RF04_INVALID_GRID",
                detail: format!("direction node {node} is not unit normalized"),
            });
        }
    }
    if weights
        .iter()
        .any(|value| !value.is_finite() || *value <= 0.0)
    {
        return Err(Rf04Error::Input {
            code: "RF04_INVALID_GRID",
            detail: "quadrature weights must be finite and strictly positive".to_string(),
        });
    }
    let steps = step_size.len();
    if steps == 0
        || background_q1.len() != steps
        || background_mid.len() != steps
        || background_q3.len() != steps
        || opacity_mid.len() != steps
    {
        return Err(Rf04Error::Input {
            code: "RF04_SCHEMA_MISMATCH",
            detail: "q1/mid/q3/opacity/step histories must share nonzero K".to_string(),
        });
    }
    if !gamma.is_finite() || !opacity_scale.is_finite() || opacity_scale < 0.0 {
        return Err(Rf04Error::Input {
            code: "RF04_INVALID_BACKGROUND",
            detail: "gamma and nonnegative opacity_scale must be finite".to_string(),
        });
    }
    for step in 0..steps {
        if !step_size[step].is_finite() || step_size[step] <= 0.0 {
            return Err(Rf04Error::Input {
                code: "RF04_INVALID_BACKGROUND",
                detail: format!("step_size[{step}] must be finite and positive"),
            });
        }
        if !opacity_mid[step].is_finite() || opacity_mid[step] < 0.0 {
            return Err(Rf04Error::Input {
                code: "RF04_INVALID_BACKGROUND",
                detail: format!("opacity_mid[{step}] must be finite and nonnegative"),
            });
        }
        for (stage, state) in [
            ("q1", &background_q1[step]),
            ("mid", &background_mid[step]),
            ("q3", &background_q3[step]),
        ] {
            if !state.iter().all(|value| value.is_finite()) || state[4].abs() >= 1.0 {
                return Err(Rf04Error::Input {
                    code: "RF04_INVALID_BACKGROUND",
                    detail: format!("{stage}[{step}] is outside the finite subluminal domain"),
                });
            }
            if !typeii_background::rhs(state, gamma)
                .iter()
                .all(|value| value.is_finite())
            {
                return Err(Rf04Error::Input {
                    code: "RF04_INVALID_BACKGROUND",
                    detail: format!("{stage}[{step}] produces a nonfinite background RHS"),
                });
            }
            let factors = typeii_kato::projector_factors(directions, weights, state[4], axis);
            if !(factors.denominator > 0.0 && factors.denominator.is_finite())
                || !factors.denominator_v.is_finite()
                || !factors
                    .r
                    .iter()
                    .chain(&factors.a)
                    .chain(&factors.rv)
                    .chain(&factors.av)
                    .all(|value| value.is_finite())
            {
                return Err(Rf04Error::Input {
                    code: "RF04_INVALID_BACKGROUND",
                    detail: format!("{stage}[{step}] has invalid projector factors"),
                });
            }
        }
    }
    Ok(())
}

fn validate_scalar_state(values: &[f64], dimension: usize) -> Result<(), Rf04Error> {
    if values.len() != dimension {
        return Err(Rf04Error::PhysicalDomain {
            code: "RF04_NONPHYSICAL_CARRIER",
            detail: format!(
                "scalar state length {} does not match {dimension}",
                values.len()
            ),
        });
    }
    if values
        .iter()
        .any(|value| !value.is_finite() || *value < 0.0)
    {
        return Err(Rf04Error::PhysicalDomain {
            code: "RF04_NONPHYSICAL_CARRIER",
            detail: "scalar radiation state must be finite and nonnegative".to_string(),
        });
    }
    Ok(())
}

fn adaptive_options(dimension: usize) -> AdaptiveKrylovOptions {
    let m_max = 20.min(dimension);
    let m_min = 8.min(m_max);
    let m_init = 12.min(m_max).max(m_min);
    AdaptiveKrylovOptions {
        m_init,
        m_min,
        m_max,
        tol: 1.0e-11,
        max_substeps: 4096,
        max_rejects: 4096,
    }
}

fn map_adaptive_error(error: AdaptiveKrylovError) -> Rf04Error {
    Rf04Error::Certificate {
        code: "RF04_KRYLOV_CERTIFICATE_FAILURE",
        detail: format!("adaptive Kato-AEM2 action failed: {error:?}"),
    }
}

fn maximum_absolute(values: &[f64]) -> f64 {
    values.iter().map(|value| value.abs()).fold(0.0, f64::max)
}

fn minimum(values: &[f64]) -> f64 {
    values.iter().copied().fold(f64::INFINITY, f64::min)
}

fn step_diagnostics(
    directions: &[[f64; 3]],
    weights: &[f64],
    axis: usize,
    state_mid: &[f64; 5],
    before: &[f64],
    after: &[f64],
) -> (f64, f64, f64) {
    let factors = typeii_kato::projector_factors(directions, weights, state_mid[4], axis);
    let raw_null = typeii_collision::collision_generator_apply(
        directions,
        weights,
        state_mid[4],
        axis,
        &factors.r,
    );
    let right_residual = maximum_absolute(&raw_null) / maximum_absolute(&factors.r);

    let state_scale = maximum_absolute(before).max(maximum_absolute(after));
    let left_denominator: f64 = factors.a.iter().map(|value| value.abs()).sum();
    let left_drift = if state_scale == 0.0 {
        0.0
    } else {
        factors
            .a
            .iter()
            .zip(before.iter().zip(after))
            .map(|(left, (old, new))| left * ((new - old) / state_scale))
            .sum::<f64>()
            .abs()
            / left_denominator
    };

    let n = directions.len();
    let mut idempotence = 0.0_f64;
    for i in 0..n {
        for j in 0..n {
            let pij = factors.r[i] * factors.a[j] / factors.denominator;
            let mut p2ij = 0.0;
            for k in 0..n {
                p2ij += (factors.r[i] * factors.a[k] / factors.denominator)
                    * (factors.r[k] * factors.a[j] / factors.denominator);
            }
            idempotence = idempotence.max((p2ij - pij).abs());
        }
    }
    (right_residual, left_drift, idempotence)
}

struct MemberFailure {
    completed_steps: usize,
    error: Rf04Error,
}

#[allow(clippy::too_many_arguments)]
fn run_member_validated(
    initial: &[f64],
    directions: &[[f64; 3]],
    weights: &[f64],
    background_q1: &[[f64; 5]],
    background_mid: &[[f64; 5]],
    background_q3: &[[f64; 5]],
    opacity_mid: &[f64],
    step_size: &[f64],
    gamma: f64,
    opacity_scale: f64,
    axis: usize,
) -> Result<ScalarTrajectory, MemberFailure> {
    validate_scalar_state(initial, directions.len()).map_err(|error| MemberFailure {
        completed_steps: 0,
        error,
    })?;
    let options = adaptive_options(directions.len());
    let mut history = Vec::with_capacity(step_size.len() + 1);
    history.push(initial.to_vec());
    let mut right = Vec::with_capacity(step_size.len());
    let mut drift = Vec::with_capacity(step_size.len());
    let mut idempotence = Vec::with_capacity(step_size.len());
    let mut residual = Vec::with_capacity(step_size.len());
    let mut action_ledger = Vec::with_capacity(step_size.len());

    for step in 0..step_size.len() {
        let before = history.last().expect("initial history row exists");
        let (after, stats) = kato_aem2_step_adaptive(
            directions,
            weights,
            axis,
            gamma,
            step_size[step],
            opacity_scale,
            &background_q1[step],
            &background_mid[step],
            &background_q3[step],
            opacity_mid[step],
            before,
            options,
        )
        .map_err(|error| MemberFailure {
            completed_steps: step,
            error: map_adaptive_error(error).with_step(step),
        })?;
        validate_scalar_state(&after, directions.len()).map_err(|error| MemberFailure {
            completed_steps: step,
            error: error.with_step(step),
        })?;
        let (right_step, drift_step, idempotence_step) = step_diagnostics(
            directions,
            weights,
            axis,
            &background_mid[step],
            before,
            &after,
        );
        right.push(right_step);
        drift.push(drift_step);
        idempotence.push(idempotence_step);
        residual.push(stats.max_accepted_error_ratio);
        action_ledger.push(ActionLedger::from(&stats));
        history.push(after);
    }
    let positivity_margin = history.iter().map(|row| minimum(row)).collect();
    Ok(ScalarTrajectory {
        radiation_history: history,
        diagnostics: ScalarDiagnostics {
            equilibrium_null_residual: right.clone(),
            right_kernel_residual: right,
            left_invariant_drift: drift,
            projected_residual_estimate: residual,
            projector_idempotence_residual: idempotence,
            positivity_margin,
            action_ledger,
        },
    })
}

#[allow(clippy::too_many_arguments)]
pub fn scalar_raw_trajectory(
    initial: &[f64],
    directions: &[[f64; 3]],
    weights: &[f64],
    background_q1: &[[f64; 5]],
    background_mid: &[[f64; 5]],
    background_q3: &[[f64; 5]],
    opacity_mid: &[f64],
    step_size: &[f64],
    gamma: f64,
    opacity_scale: f64,
    axis: usize,
) -> Result<ScalarTrajectory, Rf04Error> {
    validate_common_plan(
        directions,
        weights,
        background_q1,
        background_mid,
        background_q3,
        opacity_mid,
        step_size,
        gamma,
        opacity_scale,
        axis,
    )?;
    run_member_validated(
        initial,
        directions,
        weights,
        background_q1,
        background_mid,
        background_q3,
        opacity_mid,
        step_size,
        gamma,
        opacity_scale,
        axis,
    )
    .map_err(|failure| failure.error)
}

#[allow(clippy::too_many_arguments)]
pub fn scalar_raw_batch(
    initial: &[Vec<f64>],
    directions: &[[f64; 3]],
    weights: &[f64],
    background_q1: &[[f64; 5]],
    background_mid: &[[f64; 5]],
    background_q3: &[[f64; 5]],
    opacity_mid: &[f64],
    step_size: &[f64],
    gamma: f64,
    opacity_scale: f64,
    axis: usize,
) -> Result<ScalarBatch, Rf04Error> {
    validate_common_plan(
        directions,
        weights,
        background_q1,
        background_mid,
        background_q3,
        opacity_mid,
        step_size,
        gamma,
        opacity_scale,
        axis,
    )?;
    if initial.is_empty() {
        return Err(Rf04Error::Input {
            code: "RF04_SCHEMA_MISMATCH",
            detail: "batch must contain at least one member".to_string(),
        });
    }
    let results: Vec<Result<ScalarTrajectory, MemberFailure>> = initial
        .par_iter()
        .map(|member| {
            run_member_validated(
                member,
                directions,
                weights,
                background_q1,
                background_mid,
                background_q3,
                opacity_mid,
                step_size,
                gamma,
                opacity_scale,
                axis,
            )
        })
        .collect();
    let mut output = ScalarBatch::default();
    for result in results {
        match result {
            Ok(trajectory) => {
                output.final_radiation.push(
                    trajectory
                        .radiation_history
                        .last()
                        .expect("successful trajectory has a final row")
                        .clone(),
                );
                output.member_status.push(0);
                output
                    .member_completed_steps
                    .push(step_size.len().try_into().unwrap_or(i64::MAX));
                output.member_error_code.push(None);
            }
            Err(failure) => {
                output
                    .final_radiation
                    .push(vec![f64::NAN; directions.len()]);
                output.member_status.push(1);
                output
                    .member_completed_steps
                    .push(failure.completed_steps.try_into().unwrap_or(i64::MAX));
                output
                    .member_error_code
                    .push(Some(failure.error.code().to_string()));
            }
        }
    }
    Ok(output)
}

fn lebedev26() -> (Vec<[f64; 3]>, Vec<f64>) {
    let pi = std::f64::consts::PI;
    let a = 1.0 / 3.0_f64.sqrt();
    let b = 1.0 / 2.0_f64.sqrt();
    let mut directions = Vec::new();
    let mut weights = Vec::new();
    for axis in 0..3 {
        for sign in [-1.0, 1.0] {
            let mut direction = [0.0; 3];
            direction[axis] = sign;
            directions.push(direction);
            weights.push(4.0 * pi / 21.0);
        }
    }
    for zero_axis in 0..3 {
        let live_axes: Vec<_> = (0..3).filter(|&axis| axis != zero_axis).collect();
        for sign0 in [-1.0, 1.0] {
            for sign1 in [-1.0, 1.0] {
                let mut direction = [0.0; 3];
                direction[live_axes[0]] = sign0 * b;
                direction[live_axes[1]] = sign1 * b;
                directions.push(direction);
                weights.push(16.0 * pi / 105.0);
            }
        }
    }
    for sign0 in [-1.0, 1.0] {
        for sign1 in [-1.0, 1.0] {
            for sign2 in [-1.0, 1.0] {
                directions.push([sign0 * a, sign1 * a, sign2 * a]);
                weights.push(9.0 * pi / 70.0);
            }
        }
    }
    (directions, weights)
}

pub fn rf04_deterministic_batch_probe(threads: usize) -> Result<Vec<f64>, Rf04Error> {
    if threads == 0 {
        return Err(Rf04Error::Member {
            code: "RF04_MEMBER_FAILURE",
            detail: "thread count must be positive".to_string(),
        });
    }
    let (directions, weights) = lebedev26();
    let first: Vec<f64> = directions
        .iter()
        .map(|e| 1.0 + 0.18 * e[0] * e[1] - 0.13 * e[1] * e[2] + 0.09 * e[0] * e[2])
        .collect();
    let second: Vec<f64> = first
        .iter()
        .rev()
        .map(|value| 0.75 + 0.31 * value)
        .collect();
    let q1 = vec![
        [0.25, 0.05, 1.0 / 30.0, 0.8, 0.08],
        [0.254, 0.047, 1.0 / 30.0 + 0.002, 0.79, 0.086],
    ];
    let mid = q1
        .iter()
        .map(|row| {
            [
                row[0] + 0.003,
                row[1] - 0.002,
                row[2] + 0.0015,
                row[3] - 0.006,
                row[4] + 0.0025,
            ]
        })
        .collect::<Vec<_>>();
    let q3 = q1
        .iter()
        .map(|row| {
            [
                row[0] + 0.007,
                row[1] - 0.004,
                row[2] + 0.0035,
                row[3] - 0.013,
                row[4] + 0.0055,
            ]
        })
        .collect::<Vec<_>>();
    let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(threads)
        .build()
        .map_err(|error| Rf04Error::Member {
            code: "RF04_MEMBER_FAILURE",
            detail: format!("failed to construct bounded Rayon pool: {error}"),
        })?;
    let batch = pool.install(|| {
        scalar_raw_batch(
            &[first, second],
            &directions,
            &weights,
            &q1,
            &mid,
            &q3,
            &[0.18, 0.195],
            &[8.0e-4, 9.0e-4],
            1.3,
            1.0,
            1,
        )
    })?;
    Ok(batch.final_radiation.into_iter().flatten().collect())
}
