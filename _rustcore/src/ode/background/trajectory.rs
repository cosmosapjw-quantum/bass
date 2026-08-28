//! RF-02C Rust-owned scalar-background trajectory execution.
//!
//! A complete member trajectory is owned by this module.  Python supplies only
//! immutable inputs; accepted BDF steps, certified event carriers, exact-root
//! selection, and the Type-IX identity restart all remain on this side of the
//! FFI boundary.

use diffsol::{
    BdfState, NalgebraLU, NalgebraMat, NalgebraVec, OdeBuilder, OdeSolverMethod, OdeSolverState,
    Vector,
};
use rayon::prelude::*;
use std::cmp::Ordering;
use std::collections::BTreeSet;
use std::panic::{catch_unwind, AssertUnwindSafe};

use crate::ode::charts::{self, Chart, MAX_STATES};

use super::carrier::{certify_step, CertifiedSubsegment};
use super::events::{
    builtin_registry, direction_is_eligible, evaluate_expression, isolate_exact_roots,
    isolate_rearm_points, stored_event_epsilon, EventDefinition, EventDirection, EventFailure,
    IsolatedRoot, RootIsolation, CARRIER_MAX_DEPTH, EVENT_ATOL, EVENT_RTOL, REGISTRY_SHA256,
};
use super::history::{
    AllowedRearmSide, BackgroundParameters, BackgroundPhase, EventLatchRecord, EventRecord,
    FailureCode, FailureRecord, GeometryHistory, GeometrySample, NamedValue, RootDirectionClass,
    SampleKind, SegmentRecord, SegmentStatus, SolverTolerances, StateDigest, TrajectoryStatus,
    TransitionRecord, TypeIxDiagnostics, IDENTITY_STATE_MAP, TYPE_IX_PHASE_TRANSITION,
    TYPE_IX_RECOLLAPSE_EVENT,
};
use super::type_ix_dae;

const STEP_BUDGET: u64 = 10_000_000;
const ROUTE_IDENTITY: &str = "bass-rf02c-public-execution-route/v2";
const NATIVE_IDENTITY: &str = "bass-rf02c-native-background-execution-v2";

/// Explicit projection selection.  No projection mode is inferred from chart
/// or solver state.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum ProjectionMode {
    Off,
    CheckedInitial,
    CheckedChunkBoundary,
}

/// Immutable input to one serial, native-owned RF-02C trajectory.
#[derive(Clone, Debug)]
pub(crate) struct BackgroundRequest {
    pub chart: Chart,
    pub chart_label: &'static str,
    pub initial_state: Vec<f64>,
    pub requested_taus: Vec<f64>,
    pub gamma: f64,
    pub kappa: f64,
    pub rtol: f64,
    pub atol: f64,
    pub projection_mode: ProjectionMode,
}

#[derive(Clone, Debug)]
struct RuntimeLatch {
    armed: bool,
    consumed: bool,
    epsilon_bits: Option<u64>,
}

impl RuntimeLatch {
    fn initially_armed() -> Self {
        Self {
            armed: true,
            consumed: false,
            epsilon_bits: None,
        }
    }
}

#[derive(Clone, Debug)]
struct RootCandidate {
    event_index: usize,
    tau: f64,
    tau_bits: u64,
    theta: f64,
    isolated: IsolatedRoot,
    epsilon_bits: u64,
    subsegment_index: usize,
}

#[derive(Clone, Debug)]
struct SelectedRoot {
    winner: RootCandidate,
    state: Vec<f64>,
    raw_value: f64,
}

#[derive(Clone, Debug, Default, PartialEq)]
struct CertificateReplayAudit {
    rejected_step_widths: Vec<f64>,
    accepted_sample_step_widths: Vec<f64>,
}

#[derive(Clone, Copy, Debug)]
struct CertificateLocalReplay {
    until_tau: f64,
    step_cap: f64,
    depth: usize,
}

fn chart_kappa(chart: &Chart) -> f64 {
    match *chart {
        Chart::ClassB { kappa, .. } => kappa,
        _ => 0.0,
    }
}

fn is_type_ix(chart: &Chart) -> bool {
    matches!(chart, Chart::TypeIXD { .. })
}

fn type_ix_state(state: &[f64]) -> Result<[f64; 7], ExecutionError> {
    state.try_into().map_err(|_| {
        ExecutionError::new(
            FailureCode::AcceptedSampleSchemaMismatch,
            "Type-IX DAE requires the frozen seven-component state",
        )
    })
}

fn check_type_ix_regularity(state: &[f64], rtol: f64, atol: f64) -> Result<(), ExecutionError> {
    let state = type_ix_state(state)?;
    type_ix_dae::regularity_gate(&state, rtol, atol).map_err(|code| {
        ExecutionError::new(
            code,
            "Type-IX DAE algebraic Jacobian is singular at the caller domain scale",
        )
    })
}

fn phase_for_chart(chart_label: &str) -> BackgroundPhase {
    if chart_label == "type_ix_d_future" {
        BackgroundPhase::Expanding
    } else {
        BackgroundPhase::Named("default".to_owned())
    }
}

fn actual_before(lhs: f64, rhs: f64, forward: bool) -> bool {
    if forward {
        lhs < rhs
    } else {
        lhs > rhs
    }
}

fn actual_at_or_before(lhs: f64, rhs: f64, forward: bool) -> bool {
    lhs.to_bits() == rhs.to_bits() || actual_before(lhs, rhs, forward)
}

fn tau_tie(lhs: f64, rhs: f64) -> f64 {
    EVENT_ATOL + EVENT_RTOL * 1.0f64.max(lhs.abs()).max(rhs.abs())
}

fn polynomial_value(bits: &[u64], theta: f64) -> Result<f64, EventFailure> {
    let mut value = 0.0;
    for coefficient_bits in bits.iter().rev() {
        let coefficient = f64::from_bits(*coefficient_bits);
        if !coefficient.is_finite() {
            return Err(EventFailure::CarrierNonfinite);
        }
        value = value * theta + coefficient;
        if !value.is_finite() {
            return Err(EventFailure::CarrierNonfinite);
        }
    }
    Ok(value)
}

fn state_at_theta(subsegment: &CertifiedSubsegment, theta: f64) -> Result<Vec<f64>, EventFailure> {
    subsegment.evaluate_state(theta)
}

fn root_tau(subsegment: &CertifiedSubsegment, theta: f64) -> Result<f64, EventFailure> {
    let tau = if theta.to_bits() == 0.0f64.to_bits() {
        subsegment.tau0
    } else if theta.to_bits() == 1.0f64.to_bits() {
        subsegment.tau1
    } else {
        (subsegment.tau1 - subsegment.tau0).mul_add(theta, subsegment.tau0)
    };
    if tau.is_finite() {
        Ok(tau)
    } else {
        Err(EventFailure::CarrierNonfinite)
    }
}

fn direction_class(direction: EventDirection) -> RootDirectionClass {
    match direction {
        EventDirection::Decreasing => RootDirectionClass::Decreasing,
        EventDirection::Any => RootDirectionClass::Tangential,
        EventDirection::Increasing => RootDirectionClass::Increasing,
    }
}

fn event_failure_code(failure: EventFailure) -> FailureCode {
    match failure {
        EventFailure::UnsupportedExpression => FailureCode::UnsupportedEventExpression,
        EventFailure::CarrierNonfinite => FailureCode::EventCarrierNonfinite,
        EventFailure::CarrierCertificateFailure => FailureCode::EventCarrierCertificateFailure,
        EventFailure::NonadvancingAcceptedStep => FailureCode::NonadvancingAcceptedStep,
        EventFailure::RootRepresentationFailure => FailureCode::EventRootRepresentationFailure,
    }
}

fn candidate_order(
    lhs: &RootCandidate,
    rhs: &RootCandidate,
    registry: &[EventDefinition],
    forward: bool,
) -> Ordering {
    let time_order = if forward {
        lhs.tau.total_cmp(&rhs.tau)
    } else {
        rhs.tau.total_cmp(&lhs.tau)
    };
    time_order
        .then_with(|| {
            registry[lhs.event_index]
                .priority
                .cmp(&registry[rhs.event_index].priority)
        })
        .then_with(|| lhs.event_index.cmp(&rhs.event_index))
}

/// Scan all certified subsegments.  Root ownership is `(0,1]`, except that
/// the first carrier of the external trajectory may own theta=0.
fn select_root(
    subsegments: &[CertifiedSubsegment],
    registry: &[EventDefinition],
    latches: &mut [RuntimeLatch],
    forward: bool,
    owns_external_theta_zero: bool,
    kappa: f64,
) -> Result<Option<SelectedRoot>, EventFailure> {
    let mut candidates = Vec::new();
    let mut deduplicated = BTreeSet::new();

    for (subsegment_index, subsegment) in subsegments.iter().enumerate() {
        for event_polynomial in &subsegment.event_polynomials {
            let event_index = event_polynomial.declaration_index;
            let event = registry
                .get(event_index)
                .ok_or(EventFailure::UnsupportedExpression)?;
            let latch = latches
                .get_mut(event_index)
                .ok_or(EventFailure::UnsupportedExpression)?;
            if latch.consumed {
                continue;
            }
            let epsilon_bits = latch.epsilon_bits.unwrap_or(stored_event_epsilon(
                &event_polynomial.coefficient_bits,
                EVENT_RTOL,
                EVENT_ATOL,
            )?);

            // A latched event can rearm and encounter a later raw root inside
            // this same carrier.  Thresholds and raw roots are processed in
            // increasing theta, which is always actual integration order.
            let mut rearm_points = if latch.armed {
                Vec::new()
            } else {
                isolate_rearm_points(
                    &event_polynomial.coefficient_bits,
                    epsilon_bits,
                    event.direction,
                    !forward,
                )?
            };
            rearm_points.sort_unstable();

            let isolated = isolate_exact_roots(
                &event_polynomial.coefficient_bits,
                event.direction,
                !forward,
            )?;
            let roots = match isolated {
                RootIsolation::ContinuumZero => {
                    // Remaining in the zero band cannot rearm by itself.
                    continue;
                }
                RootIsolation::Roots(roots) => roots,
            };

            for root in roots {
                let theta = f64::from_bits(root.theta_bits);
                let may_own_theta_zero = owns_external_theta_zero && subsegment_index == 0;
                if root.theta_bits == 0.0f64.to_bits() && !may_own_theta_zero {
                    continue;
                }

                if !latch.armed {
                    let rearm = rearm_points
                        .iter()
                        .copied()
                        .map(f64::from_bits)
                        .find(|threshold| *threshold < theta);
                    if let Some(threshold) = rearm {
                        let probe = 0.5 * (threshold + theta);
                        let raw = polynomial_value(&event_polynomial.coefficient_bits, probe)?;
                        let epsilon = f64::from_bits(epsilon_bits);
                        latch.armed = match event.direction {
                            EventDirection::Decreasing => raw > epsilon,
                            EventDirection::Increasing => raw < -epsilon,
                            EventDirection::Any => raw.abs() > epsilon,
                        };
                    }
                }
                if !latch.armed || !direction_is_eligible(root.direction, event.direction) {
                    continue;
                }
                let tau = root_tau(subsegment, theta)?;
                if !deduplicated.insert((event_index, tau.to_bits())) {
                    continue;
                }
                candidates.push(RootCandidate {
                    event_index,
                    tau,
                    tau_bits: tau.to_bits(),
                    theta,
                    isolated: root,
                    epsilon_bits,
                    subsegment_index,
                });
            }

            // Accepted endpoints are assertions in addition to within-carrier
            // threshold isolation.
            if !latch.armed {
                let raw_end = polynomial_value(&event_polynomial.coefficient_bits, 1.0)?;
                let epsilon = f64::from_bits(epsilon_bits);
                latch.armed = match event.direction {
                    EventDirection::Decreasing => raw_end > epsilon,
                    EventDirection::Increasing => raw_end < -epsilon,
                    EventDirection::Any => raw_end.abs() > epsilon,
                };
            }
        }
    }

    if candidates.is_empty() {
        return Ok(None);
    }
    candidates.sort_by(|lhs, rhs| candidate_order(lhs, rhs, registry, forward));
    let first_tau = candidates[0].tau;
    let mut simultaneous_candidates = candidates
        .into_iter()
        .take_while(|candidate| {
            (candidate.tau - first_tau).abs() <= tau_tie(candidate.tau, first_tau)
        })
        .collect::<Vec<_>>();
    simultaneous_candidates.sort_by(|lhs, rhs| {
        registry[lhs.event_index]
            .priority
            .cmp(&registry[rhs.event_index].priority)
            .then_with(|| lhs.event_index.cmp(&rhs.event_index))
    });
    let winner = simultaneous_candidates.remove(0);
    let subsegment = &subsegments[winner.subsegment_index];
    let state = state_at_theta(subsegment, winner.theta)?;
    let raw_value = evaluate_expression(&registry[winner.event_index].expression, &state, kappa)?;
    let epsilon = f64::from_bits(winner.epsilon_bits);
    if raw_value.abs() > epsilon {
        return Err(EventFailure::RootRepresentationFailure);
    }
    Ok(Some(SelectedRoot {
        winner,
        state,
        raw_value,
    }))
}

#[derive(Clone, Debug)]
struct ExecutionError {
    code: FailureCode,
    detail: String,
}

impl ExecutionError {
    fn new(code: FailureCode, detail: impl Into<String>) -> Self {
        Self {
            code,
            detail: detail.into(),
        }
    }
}

impl From<EventFailure> for ExecutionError {
    fn from(failure: EventFailure) -> Self {
        Self::new(event_failure_code(failure), format!("{failure:?}"))
    }
}

fn replayable_certificate_failure(code: FailureCode) -> bool {
    matches!(
        code,
        FailureCode::AcceptedSampleConstraintFailure
            | FailureCode::EventCarrierCertificateFailure
            | FailureCode::EventRootRepresentationFailure
    )
}

fn refine_certificate_replay(
    current: Option<CertificateLocalReplay>,
    tau0: f64,
    tau1: f64,
) -> Result<CertificateLocalReplay, ExecutionError> {
    let width = (tau1 - tau0).abs();
    let midpoint = tau0.midpoint(tau1);
    let depth = current.map_or(1, |replay| replay.depth + 1);
    if depth > CARRIER_MAX_DEPTH
        || !width.is_finite()
        || width == 0.0
        || midpoint.to_bits() == tau0.to_bits()
        || midpoint.to_bits() == tau1.to_bits()
    {
        return Err(ExecutionError::new(
            FailureCode::EventCarrierCertificateFailure,
            "Type-IX certificate-local replay exhausted the frozen depth-24 bound",
        ));
    }
    Ok(CertificateLocalReplay {
        until_tau: current.map_or(tau1, |replay| replay.until_tau),
        step_cap: 0.5 * width,
        depth,
    })
}

fn replay_stop_tau(replay: CertificateLocalReplay, tau: f64, final_tau: f64, forward: bool) -> f64 {
    let candidate = if forward {
        tau + replay.step_cap
    } else {
        tau - replay.step_cap
    };
    let interval_limit = if actual_before(final_tau, replay.until_tau, forward) {
        final_tau
    } else {
        replay.until_tau
    };
    if actual_before(interval_limit, candidate, forward) {
        interval_limit
    } else {
        candidate
    }
}

fn request_chart_label(chart: &Chart) -> Option<&'static str> {
    match chart {
        Chart::ClassA { .. } => Some("class_a"),
        Chart::ClassB { .. } => Some("class_b"),
        Chart::Exceptional { .. } => Some("exceptional"),
        Chart::TypeIXD { future: false, .. } => Some("type_ix_d"),
        Chart::TypeIXD { future: true, .. } => Some("type_ix_d_future"),
        Chart::ClassATilted { .. } | Chart::ClassBTilted { .. } => None,
    }
}

fn request_chart_gamma(chart: &Chart) -> Option<f64> {
    match *chart {
        Chart::ClassA { gamma }
        | Chart::ClassB { gamma, .. }
        | Chart::Exceptional { gamma }
        | Chart::TypeIXD { gamma, .. } => Some(gamma),
        Chart::ClassATilted { .. } | Chart::ClassBTilted { .. } => None,
    }
}

fn new_history(request: &BackgroundRequest) -> GeometryHistory {
    let state_names = charts::scalar_state_names(&request.chart)
        .unwrap_or(&[])
        .iter()
        .map(|name| (*name).to_owned())
        .collect();
    GeometryHistory::new(
        ROUTE_IDENTITY,
        NATIVE_IDENTITY,
        REGISTRY_SHA256,
        request.chart_label,
        phase_for_chart(request.chart_label),
        BackgroundParameters {
            gamma: request.gamma,
            kappa: request.kappa,
        },
        SolverTolerances {
            rtol: request.rtol,
            atol: request.atol,
        },
        state_names,
    )
}

fn fail_history(history: &mut GeometryHistory, error: ExecutionError) {
    history.status = if history.samples.len() > 1 || !history.events.is_empty() {
        TrajectoryStatus::FailedAfterAcceptedPrefix
    } else {
        TrajectoryStatus::Failed
    };
    history.failure = Some(FailureRecord::new(error.code, error.detail));
}

fn validate_request(request: &BackgroundRequest) -> Result<(), ExecutionError> {
    let expected_label = request_chart_label(&request.chart).ok_or_else(|| {
        ExecutionError::new(
            FailureCode::InvalidInput,
            "chart is outside the RF-02C scalar closure",
        )
    })?;
    if expected_label != request.chart_label {
        return Err(ExecutionError::new(
            FailureCode::AcceptedSampleSchemaMismatch,
            "chart label does not match the compiled chart",
        ));
    }
    if request_chart_gamma(&request.chart).map(f64::to_bits) != Some(request.gamma.to_bits())
        || chart_kappa(&request.chart).to_bits() != request.kappa.to_bits()
    {
        return Err(ExecutionError::new(
            FailureCode::InvalidInput,
            "parameter bytes do not match the compiled chart",
        ));
    }
    if request.chart_label == "class_b"
        && (request.kappa - charts::KAPPA_EXCEPTIONAL).abs() < charts::KAPPA_EXCEPTIONAL_TOL
    {
        return Err(ExecutionError::new(
            FailureCode::InvalidInput,
            "class_b is degenerate near kappa=-9; use exceptional",
        ));
    }
    let n = request.chart.nstates();
    if request.initial_state.len() != n {
        return Err(ExecutionError::new(
            FailureCode::AcceptedSampleSchemaMismatch,
            format!("expected {n} state components"),
        ));
    }
    if request.requested_taus.is_empty()
        || !request.initial_state.iter().all(|value| value.is_finite())
        || !request.requested_taus.iter().all(|value| value.is_finite())
        || !request.gamma.is_finite()
        || !request.kappa.is_finite()
        || !request.rtol.is_finite()
        || !request.atol.is_finite()
        || request.rtol < 0.0
        || request.atol < 0.0
        || request.rtol + request.atol == 0.0
    {
        return Err(ExecutionError::new(
            FailureCode::InvalidInput,
            "trajectory inputs and tolerances must be finite and valid",
        ));
    }
    if request.requested_taus.len() > 1 {
        let forward = request.requested_taus[1] > request.requested_taus[0];
        if request.requested_taus[1].to_bits() == request.requested_taus[0].to_bits()
            || request
                .requested_taus
                .windows(2)
                .any(|pair| !actual_before(pair[0], pair[1], forward))
        {
            return Err(ExecutionError::new(
                FailureCode::InvalidInput,
                "requested times must be strictly monotone in one direction",
            ));
        }
    }
    Ok(())
}

fn projection_failure_code(code: charts::ProjectionFailureCode) -> FailureCode {
    use charts::ProjectionFailureCode as Projection;
    match code {
        Projection::ProjectionInvalidInput => FailureCode::ProjectionInvalidInput,
        Projection::ProjectionSingular => FailureCode::ProjectionSingular,
        Projection::ProjectionNonfinite => FailureCode::ProjectionNonfinite,
        Projection::ProjectionNonMonotone => FailureCode::ProjectionNonMonotone,
        Projection::ProjectionNotConverged => FailureCode::ProjectionNotConverged,
        Projection::ProjectionPhysicalDomain => FailureCode::ProjectionPhysicalDomain,
    }
}

fn prepare_initial_state(request: &BackgroundRequest) -> Result<Vec<f64>, ExecutionError> {
    if request.projection_mode == ProjectionMode::Off {
        return Ok(request.initial_state.clone());
    }
    let projected = charts::project_constraints_checked(
        &request.chart,
        &request.initial_state,
        request.rtol,
        request.atol,
    );
    if !projected.certificate.accepted {
        let code = projected
            .certificate
            .failure_code
            .map(projection_failure_code)
            .unwrap_or(FailureCode::ProjectionNotConverged);
        return Err(ExecutionError::new(
            code,
            "checked initial projection failed",
        ));
    }
    Ok(projected.state[..projected.state_len].to_vec())
}

fn make_sample(
    request: &BackgroundRequest,
    registry: &[EventDefinition],
    sample_index: usize,
    segment_id: usize,
    phase: BackgroundPhase,
    sample_kind: SampleKind,
    tau: f64,
    state: Vec<f64>,
    enforce_domain: bool,
) -> Result<GeometrySample, ExecutionError> {
    let n = request.chart.nstates();
    if state.len() != n {
        return Err(ExecutionError::new(
            FailureCode::AcceptedSampleSchemaMismatch,
            "accepted state shape does not match the frozen schema",
        ));
    }
    if !tau.is_finite() || !state.iter().all(|value| value.is_finite()) {
        return Err(ExecutionError::new(
            FailureCode::AcceptedSampleNonfinite,
            "accepted time/state is non-finite",
        ));
    }
    let state_norm = state
        .iter()
        .fold(0.0f64, |maximum, value| maximum.max(value.abs()));
    let scale = request.atol + request.rtol * 1.0f64.max(state_norm);
    if !scale.is_finite() || scale <= 0.0 {
        return Err(ExecutionError::new(
            FailureCode::AcceptedSampleNonfinite,
            "accepted-sample scale is non-finite",
        ));
    }

    let constraint_names = charts::scalar_constraint_names(&request.chart).ok_or_else(|| {
        ExecutionError::new(
            FailureCode::AcceptedSampleSchemaMismatch,
            "compiled chart has no scalar constraint schema",
        )
    })?;
    let mut constraint_buffer = [0.0f64; 2];
    let constraint_count =
        charts::constraint_values(&request.chart, &state, &mut constraint_buffer).map_err(
            |detail| ExecutionError::new(FailureCode::AcceptedSampleSchemaMismatch, detail),
        )?;
    let equality_constraints = constraint_names
        .iter()
        .zip(&constraint_buffer[..constraint_count])
        .map(|(name, value)| NamedValue::new(*name, *value))
        .collect::<Vec<_>>();
    let normalized_constraint_residual = constraint_buffer[..constraint_count]
        .iter()
        .fold(0.0f64, |maximum, value| maximum.max(value.abs() / scale));
    if !normalized_constraint_residual.is_finite() || normalized_constraint_residual > 1.0 {
        let constraints = constraint_names
            .iter()
            .zip(&constraint_buffer[..constraint_count])
            .map(|(name, value)| format!("{name}={value:.17e}"))
            .collect::<Vec<_>>()
            .join(",");
        return Err(ExecutionError::new(
            FailureCode::AcceptedSampleConstraintFailure,
            format!(
                "tau={tau:.17e} kind={} normalized equality residual \
                 {normalized_constraint_residual:.17e} exceeds one; scale={scale:.17e}; \
                 constraints=[{constraints}]",
                sample_kind.as_str(),
            ),
        ));
    }

    let mut raw_margins = Vec::with_capacity(registry.len());
    let mut certificate_margins = Vec::with_capacity(registry.len());
    for event in registry {
        let raw = evaluate_expression(&event.expression, &state, request.kappa)?;
        let certificate = raw + scale;
        if !certificate.is_finite() {
            return Err(ExecutionError::new(
                FailureCode::AcceptedSampleNonfinite,
                "domain certificate is non-finite",
            ));
        }
        if enforce_domain && event.id.starts_with("domain.") && certificate < 0.0 {
            return Err(ExecutionError::new(
                FailureCode::AcceptedSampleDomainFailure,
                format!("{} certificate is negative", event.margin_id),
            ));
        }
        raw_margins.push(NamedValue::new(event.margin_id, raw));
        certificate_margins.push(NamedValue::new(event.margin_id, certificate));
    }

    let omega = charts::omega(&request.chart, &state);
    if !omega.is_finite() {
        return Err(ExecutionError::new(
            FailureCode::AcceptedSampleNonfinite,
            "Omega is non-finite",
        ));
    }
    let type_ix = match request.chart {
        Chart::TypeIXD { .. } => Some(TypeIxDiagnostics {
            h_bar: state[0],
            sigma2: (state[1] * state[1] + state[2] * state[2] + state[3] * state[3]) / 6.0,
            definition: constraint_buffer[0],
            trace: constraint_buffer[1],
        }),
        _ => None,
    };
    Ok(GeometrySample::new(
        sample_index,
        segment_id,
        phase,
        sample_kind,
        tau,
        state,
        omega,
        equality_constraints,
        normalized_constraint_residual,
        raw_margins,
        certificate_margins,
        type_ix,
    ))
}

fn append_sample(
    history: &mut GeometryHistory,
    sample: GeometrySample,
) -> Result<usize, ExecutionError> {
    history.append_sample(sample).map_err(|error| {
        ExecutionError::new(
            FailureCode::HistoryInvariantViolation,
            format!("sample invariant: {error:?}"),
        )
    })
}

fn append_segment(
    history: &mut GeometryHistory,
    segment: SegmentRecord,
) -> Result<usize, ExecutionError> {
    history.append_segment(segment).map_err(|error| {
        ExecutionError::new(
            FailureCode::HistoryInvariantViolation,
            format!("segment invariant: {error:?}"),
        )
    })
}

fn initial_epsilon(coefficient_bits: &[u64]) -> Result<f64, ExecutionError> {
    Ok(f64::from_bits(stored_event_epsilon(
        coefficient_bits,
        EVENT_RTOL,
        EVENT_ATOL,
    )?))
}

fn zero_length_initial_epsilon(raw: f64) -> f64 {
    EVENT_ATOL + EVENT_RTOL * 1.0f64.max(raw.abs())
}

fn one_sided_polynomial_sign(coefficient_bits: &[u64]) -> Result<i8, ExecutionError> {
    for bits in coefficient_bits {
        let value = f64::from_bits(*bits);
        if !value.is_finite() {
            return Err(EventFailure::CarrierNonfinite.into());
        }
        if value > 0.0 {
            return Ok(1);
        }
        if value < 0.0 {
            return Ok(-1);
        }
    }
    Ok(0)
}

fn initial_domain_from_first_carrier(
    history: &mut GeometryHistory,
    registry: &[EventDefinition],
    first: &CertifiedSubsegment,
    latches: &mut [RuntimeLatch],
) -> Result<(), ExecutionError> {
    let initial = history.samples.first_mut().ok_or_else(|| {
        ExecutionError::new(
            FailureCode::HistoryInvariantViolation,
            "missing initial sample",
        )
    })?;
    for event_polynomial in &first.event_polynomials {
        let event_index = event_polynomial.declaration_index;
        let event = &registry[event_index];
        if !event.id.starts_with("domain.") {
            continue;
        }
        let epsilon = initial_epsilon(&event_polynomial.coefficient_bits)?;
        let raw = initial.raw_margin(event.margin_id).ok_or_else(|| {
            ExecutionError::new(
                FailureCode::HistoryInvariantViolation,
                "missing initial domain margin",
            )
        })?;
        if raw < -epsilon {
            return Err(ExecutionError::new(
                FailureCode::InitialDomainViolation,
                format!("{} is outside its initial domain", event.margin_id),
            ));
        }
        if raw.abs() <= epsilon {
            let sign = one_sided_polynomial_sign(&event_polynomial.coefficient_bits)?;
            let fires = match event.direction {
                EventDirection::Decreasing => sign < 0,
                EventDirection::Increasing => sign > 0,
                EventDirection::Any => true,
            };
            latches[event_index].epsilon_bits = Some(epsilon.to_bits());
            latches[event_index].armed = fires;
            if fires {
                // The same stored sample becomes the unique event-root sample;
                // no duplicate initial/root bytes are introduced.
                initial.sample_kind = SampleKind::EventRoot;
            }
        }
    }
    Ok(())
}

fn validate_zero_length_initial(
    sample: &GeometrySample,
    registry: &[EventDefinition],
) -> Result<(), ExecutionError> {
    for event in registry
        .iter()
        .filter(|event| event.id.starts_with("domain."))
    {
        let raw = sample.raw_margin(event.margin_id).ok_or_else(|| {
            ExecutionError::new(
                FailureCode::HistoryInvariantViolation,
                "missing zero-length initial margin",
            )
        })?;
        if raw < -zero_length_initial_epsilon(raw) {
            return Err(ExecutionError::new(
                FailureCode::InitialDomainViolation,
                format!("{} is outside its initial domain", event.margin_id),
            ));
        }
    }
    Ok(())
}

fn vector_from_solver(vector: &NalgebraVec<f64>, n: usize) -> Result<Vec<f64>, ExecutionError> {
    let state = (0..n)
        .map(|index| vector.get_index(index))
        .collect::<Vec<_>>();
    if state.iter().all(|value| value.is_finite()) {
        Ok(state)
    } else {
        Err(ExecutionError::new(
            FailureCode::AcceptedSampleNonfinite,
            "solver returned a non-finite state",
        ))
    }
}

fn allowed_rearm_side(direction: EventDirection, consumed: bool) -> AllowedRearmSide {
    if consumed {
        return AllowedRearmSide::Never;
    }
    match direction {
        EventDirection::Decreasing => AllowedRearmSide::AbovePositiveEpsilon,
        EventDirection::Increasing => AllowedRearmSide::BelowNegativeEpsilon,
        EventDirection::Any => AllowedRearmSide::EitherOutsideZeroBand,
    }
}

fn append_root_records(
    request: &BackgroundRequest,
    registry: &[EventDefinition],
    history: &mut GeometryHistory,
    segment_id: usize,
    phase: &BackgroundPhase,
    selected: &SelectedRoot,
    latches: &mut [RuntimeLatch],
) -> Result<(usize, EventLatchRecord), ExecutionError> {
    let event = &registry[selected.winner.event_index];
    let reuses_initial_root = history.samples.first().is_some_and(|sample| {
        matches!(
            sample.sample_kind,
            SampleKind::Initial | SampleKind::EventRoot
        ) && sample.segment_id == segment_id
            && &sample.phase == phase
            && sample.tau_bits == selected.winner.tau_bits
            && sample.state.len() == selected.state.len()
            && sample
                .state
                .iter()
                .zip(&selected.state)
                .all(|(stored, selected)| stored.to_bits() == selected.to_bits())
    });
    let sample_index = if reuses_initial_root {
        history.samples[0].sample_kind = SampleKind::EventRoot;
        0
    } else {
        history.samples.len()
    };
    if !reuses_initial_root {
        let root_sample = make_sample(
            request,
            registry,
            sample_index,
            segment_id,
            phase.clone(),
            SampleKind::EventRoot,
            selected.winner.tau,
            selected.state.clone(),
            true,
        )?;
        append_sample(history, root_sample)?;
    }
    let stored_root = &history.samples[sample_index];
    let raw_margin = stored_root.raw_margin(event.margin_id).ok_or_else(|| {
        ExecutionError::new(
            FailureCode::HistoryInvariantViolation,
            "selected root sample is missing its raw margin",
        )
    })?;
    let certificate_margin = stored_root
        .certificate_margin(event.margin_id)
        .ok_or_else(|| {
            ExecutionError::new(
                FailureCode::HistoryInvariantViolation,
                "selected root sample is missing its certificate margin",
            )
        })?;
    if raw_margin.to_bits() != selected.raw_value.to_bits() {
        return Err(ExecutionError::new(
            FailureCode::EventRootRepresentationFailure,
            "selected root AST value changed before storage",
        ));
    }

    let event_sequence = history.events.len();
    let epsilon_g = f64::from_bits(selected.winner.epsilon_bits);
    history
        .append_event(EventRecord {
            event_sequence,
            event_id: event.id.to_owned(),
            margin_id: event.margin_id.to_owned(),
            root_multiplicity: selected.winner.isolated.multiplicity,
            direction_class: direction_class(selected.winner.isolated.direction),
            priority: event.priority,
            simultaneous_group: event_sequence,
            sample_index,
            tau_bits: selected.winner.tau_bits,
            epsilon_g,
            epsilon_g_bits: selected.winner.epsilon_bits,
            raw_margin,
            certificate_margin,
            segment_terminal: event.segment_terminal,
            trajectory_terminal: event.trajectory_terminal,
            transition_id: event.transition_id.map(str::to_owned),
        })
        .map_err(|error| {
            ExecutionError::new(
                FailureCode::HistoryInvariantViolation,
                format!("event invariant: {error:?}"),
            )
        })?;

    let consumed = event.one_shot_after_transition && event.transition_id.is_some();
    latches[selected.winner.event_index] = RuntimeLatch {
        armed: false,
        consumed,
        epsilon_bits: Some(selected.winner.epsilon_bits),
    };
    let root_state_sha256 = StateDigest::from_state(&selected.state);
    let latch = EventLatchRecord {
        event_id: event.id.to_owned(),
        margin_id: event.margin_id.to_owned(),
        direction: direction_class(event.direction),
        epsilon_g,
        epsilon_g_bits: selected.winner.epsilon_bits,
        root_tau_bits: selected.winner.tau_bits,
        root_state_sha256,
        allowed_rearm_side: allowed_rearm_side(event.direction, consumed),
        consumed,
    };
    latch
        .verify_restart(selected.winner.tau, &selected.state)
        .map_err(|code| ExecutionError::new(code, "root/latch bytes do not match"))?;
    Ok((sample_index, latch))
}

fn integrate_impl(
    request: &BackgroundRequest,
    history: &mut GeometryHistory,
    replay_audit: &mut CertificateReplayAudit,
) -> Result<(), ExecutionError> {
    validate_request(request)?;
    let registry = builtin_registry(request.chart_label)?;
    let initial_state = prepare_initial_state(request)?;
    let initial_tau = request.requested_taus[0];
    let final_tau = *request
        .requested_taus
        .last()
        .expect("validated nonempty requested times");
    let forward = final_tau >= initial_tau;
    let initial_phase = phase_for_chart(request.chart_label);

    if is_type_ix(&request.chart) {
        check_type_ix_regularity(&initial_state, request.rtol, request.atol)?;
    }

    let initial_sample = make_sample(
        request,
        &registry,
        0,
        0,
        initial_phase.clone(),
        SampleKind::Initial,
        initial_tau,
        initial_state.clone(),
        is_type_ix(&request.chart),
    )?;
    append_sample(history, initial_sample)?;

    if final_tau.to_bits() == initial_tau.to_bits() {
        validate_zero_length_initial(&history.samples[0], &registry)?;
        let certificate_ok = registry
            .iter()
            .filter(|event| event.id.starts_with("domain."))
            .all(|event| {
                history.samples[0]
                    .certificate_margin(event.margin_id)
                    .is_some_and(|margin| margin >= 0.0)
            });
        if !certificate_ok {
            return Err(ExecutionError::new(
                FailureCode::AcceptedSampleDomainFailure,
                "zero-length initial certificate is negative",
            ));
        }
        append_segment(
            history,
            SegmentRecord {
                segment_id: 0,
                chart: request.chart_label.to_owned(),
                phase: initial_phase.clone(),
                tau_start_bits: initial_tau.to_bits(),
                tau_end_bits: initial_tau.to_bits(),
                start_sample_index: 0,
                end_sample_index: 0,
                status: SegmentStatus::Completed,
            },
        )?;
        history.final_phase = initial_phase;
        history.status = TrajectoryStatus::Completed;
        return Ok(());
    }

    run_segment_loop(
        request,
        history,
        &registry,
        vec![RuntimeLatch::initially_armed(); registry.len()],
        1,
        0,
        0,
        initial_tau,
        initial_phase,
        true,
        initial_state,
        final_tau,
        forward,
        replay_audit,
    )
}

#[allow(clippy::too_many_arguments)]
fn run_segment_loop(
    request: &BackgroundRequest,
    history: &mut GeometryHistory,
    registry: &[EventDefinition],
    mut latches: Vec<RuntimeLatch>,
    mut requested_cursor: usize,
    mut segment_id: usize,
    mut segment_start_sample: usize,
    mut segment_start_tau: f64,
    mut phase: BackgroundPhase,
    mut first_external_carrier: bool,
    mut initial_state: Vec<f64>,
    final_tau: f64,
    forward: bool,
    replay_audit: &mut CertificateReplayAudit,
) -> Result<(), ExecutionError> {
    'segments: loop {
        let n = request.chart.nstates();
        let solver_initial = initial_state.clone();
        let rhs_chart = request.chart;
        let jac_chart = request.chart;
        let mass_is_type_ix = is_type_ix(&request.chart);
        let rhs_rtol = request.rtol;
        let rhs_atol = request.atol;
        let jac_rtol = request.rtol;
        let jac_atol = request.atol;
        let mut builder = OdeBuilder::<NalgebraMat<f64>>::new()
            .t0(segment_start_tau)
            .rtol(request.rtol)
            .atol([request.atol])
            .rhs_implicit(
                move |y: &NalgebraVec<f64>,
                      _parameters: &NalgebraVec<f64>,
                      _tau: f64,
                      output: &mut NalgebraVec<f64>| {
                    let mut state = [0.0f64; MAX_STATES];
                    for (index, value) in state.iter_mut().enumerate().take(n) {
                        *value = y.get_index(index);
                    }
                    let mut derivative = [0.0f64; MAX_STATES];
                    if let Chart::TypeIXD { .. } = rhs_chart {
                        let type_ix_state: [f64; 7] = state[..n]
                            .try_into()
                            .expect("compiled Type-IX schema has seven components");
                        match type_ix_dae::dae_rhs(&rhs_chart, &type_ix_state, rhs_rtol, rhs_atol) {
                            Ok(value) => derivative[..7].copy_from_slice(&value),
                            Err(_) => derivative[..7].fill(f64::NAN),
                        }
                    } else {
                        charts::rhs(&rhs_chart, &state[..n], &mut derivative[..n]);
                    }
                    for (index, value) in derivative.iter().enumerate().take(n) {
                        output.set_index(index, *value);
                    }
                },
                move |y: &NalgebraVec<f64>,
                      _parameters: &NalgebraVec<f64>,
                      _tau: f64,
                      tangent: &NalgebraVec<f64>,
                      output: &mut NalgebraVec<f64>| {
                    let mut state = [0.0f64; MAX_STATES];
                    let mut vector = [0.0f64; MAX_STATES];
                    for index in 0..n {
                        state[index] = y.get_index(index);
                        vector[index] = tangent.get_index(index);
                    }
                    let mut product = [0.0f64; MAX_STATES];
                    if let Chart::TypeIXD { .. } = jac_chart {
                        let type_ix_state: [f64; 7] = state[..n]
                            .try_into()
                            .expect("compiled Type-IX schema has seven components");
                        let type_ix_vector: [f64; 7] = vector[..n]
                            .try_into()
                            .expect("compiled Type-IX schema has seven components");
                        match type_ix_dae::dae_jvp(
                            &jac_chart,
                            &type_ix_state,
                            &type_ix_vector,
                            jac_rtol,
                            jac_atol,
                        ) {
                            Ok(value) => product[..7].copy_from_slice(&value),
                            Err(_) => product[..7].fill(f64::NAN),
                        }
                    } else {
                        charts::jac_mul(&jac_chart, &state[..n], &vector[..n], &mut product[..n]);
                    }
                    for (index, value) in product.iter().enumerate().take(n) {
                        output.set_index(index, *value);
                    }
                },
            )
            .mass(
                move |input: &NalgebraVec<f64>,
                      _parameters: &NalgebraVec<f64>,
                      _tau: f64,
                      beta: f64,
                      output: &mut NalgebraVec<f64>| {
                    for index in 0..n {
                        let previous = output.get_index(index);
                        let mass_input = if mass_is_type_ix
                            && type_ix_dae::TYPE_IX_DAE_MASS_DIAGONAL[index] == 0.0
                        {
                            0.0
                        } else {
                            input.get_index(index)
                        };
                        output.set_index(index, mass_input + beta * previous);
                    }
                },
            )
            .init(
                move |_parameters: &NalgebraVec<f64>, _tau: f64, output: &mut NalgebraVec<f64>| {
                    for (index, value) in solver_initial.iter().enumerate() {
                        output.set_index(index, *value);
                    }
                },
                n,
            );
        // The builder derives the initial magnitude from the caller's state
        // and tolerances.  Only backward integration supplies the sign that
        // diffsol otherwise defaults to positive.
        if !forward {
            builder = builder.h0(-1.0);
        }
        let problem = builder.build().map_err(|error| {
            ExecutionError::new(
                FailureCode::SolverFailure,
                format!("BDF build failed: {error}"),
            )
        })?;
        let mut solver = if is_type_ix(&request.chart) {
            // `OdeSolverProblem::bdf` makes a DAE initial state consistent by
            // changing the algebraic variables.  That is appropriate for a
            // generic DAE but forbidden at an RF-02C event restart: the root
            // state is the frozen Hermite state and must enter the next
            // segment byte-for-byte.  Build the BDF state without that
            // reconstruction and seed its derivative with the unchanged full
            // physical Type-IX RHS (not the two algebraic residual rows).
            let mut state = BdfState::<NalgebraVec<f64>>::new_without_initialise(&problem)
                .map_err(|error| {
                    ExecutionError::new(
                        FailureCode::SolverFailure,
                        format!("BDF state init failed: {error}"),
                    )
                })?;
            let mut physical_derivative = vec![0.0; n];
            charts::rhs(&request.chart, &initial_state, &mut physical_derivative);
            {
                let mut state_mut = state.as_mut();
                for (index, value) in physical_derivative.iter().enumerate() {
                    state_mut.dy.set_index(index, *value);
                }
                state_mut.set_step_size(problem.h0, &problem.atol, problem.rtol, &problem.eqn, 1);
            }
            problem
                .bdf_solver::<NalgebraLU<f64>>(state)
                .map_err(|error| {
                    ExecutionError::new(
                        FailureCode::SolverFailure,
                        format!("BDF init failed: {error}"),
                    )
                })?
        } else {
            problem.bdf::<NalgebraLU<f64>>().map_err(|error| {
                ExecutionError::new(
                    FailureCode::SolverFailure,
                    format!("BDF init failed: {error}"),
                )
            })?
        };

        if is_type_ix(&request.chart) {
            let solver_state = vector_from_solver(solver.state().y, n)?;
            if solver_state
                .iter()
                .zip(&initial_state)
                .any(|(actual, expected)| actual.to_bits() != expected.to_bits())
            {
                return Err(ExecutionError::new(
                    FailureCode::RestartIdentityMismatch,
                    "Type-IX BDF construction changed the initial state bytes",
                ));
            }
        }

        let mut step_count = 0u64;
        let mut certificate_replay: Option<CertificateLocalReplay> = None;
        'steps: loop {
            let tau0 = solver.state().t;
            let y0 = vector_from_solver(solver.state().y, n)?;
            if is_type_ix(&request.chart) {
                // The DAE algebraic rows are nonlinear in the public state.
                // A diffsol checkpoint invalidates both the RHS and combined
                // BDF Jacobians.  Do that at every accepted-state boundary so
                // a stale multistep factorisation cannot define the algebraic
                // constraint solve.  The returned state is deliberately not
                // used here; the immediately following solver clone is the
                // complete local-replay checkpoint.
                drop(solver.checkpoint());
            }
            if certificate_replay.is_some_and(|replay| {
                replay.until_tau.to_bits() == tau0.to_bits()
                    || actual_before(replay.until_tau, tau0, forward)
            }) {
                certificate_replay = None;
            }
            let mut pre_step_solver = if is_type_ix(&request.chart) {
                Some(solver.clone())
            } else {
                None
            };
            let saved_latches = latches.clone();
            let saved_requested_cursor = requested_cursor;
            let saved_first_external_carrier = first_external_carrier;
            let saved_sample_len = history.samples.len();
            let saved_initial_kind = history.samples.first().map(|sample| sample.sample_kind);
            if let Some(replay) = certificate_replay {
                let stop_tau = replay_stop_tau(replay, tau0, final_tau, forward);
                let stop_roundoff = 100.0 * f64::EPSILON * (tau0.abs() + solver.state().h.abs());
                let stop_gap = (stop_tau - tau0).abs();
                if stop_gap <= stop_roundoff
                    && ((replay.until_tau - tau0).abs() <= stop_roundoff
                        || (final_tau - tau0).abs() <= stop_roundoff)
                {
                    certificate_replay = None;
                } else if stop_tau.to_bits() == tau0.to_bits()
                    || !actual_before(tau0, stop_tau, forward)
                    || stop_gap <= stop_roundoff
                {
                    return Err(ExecutionError::new(
                        FailureCode::EventCarrierCertificateFailure,
                        format!(
                            "Type-IX certificate-local replay stop did not advance: \
                             tau={tau0:.17e}, stop={stop_tau:.17e}, until={:.17e}, \
                             cap={:.17e}, depth={}, roundoff={stop_roundoff:.17e}",
                            replay.until_tau, replay.step_cap, replay.depth,
                        ),
                    ));
                } else {
                    solver.set_stop_time(stop_tau).map_err(|error| {
                        ExecutionError::new(
                            FailureCode::SolverFailure,
                            format!("BDF replay step cap failed: {error}"),
                        )
                    })?;
                }
            }
            solver.step().map_err(|error| {
                ExecutionError::new(
                    FailureCode::SolverFailure,
                    format!("BDF step failed: {error}"),
                )
            })?;
            step_count += 1;
            if step_count > STEP_BUDGET {
                return Err(ExecutionError::new(
                    FailureCode::SolverFailure,
                    "BDF step budget exceeded",
                ));
            }
            let accepted_tau = solver.state().t;
            if accepted_tau.to_bits() == tau0.to_bits()
                || !actual_before(tau0, accepted_tau, forward)
            {
                return Err(ExecutionError::new(
                    FailureCode::NonadvancingAcceptedStep,
                    format!("accepted step did not advance from {tau0:e}"),
                ));
            }
            macro_rules! replay_or_return {
                ($error:expr, $record_sample_rejection:expr) => {{
                    let error = $error;
                    if is_type_ix(&request.chart) && replayable_certificate_failure(error.code) {
                        let rejected_width = (accepted_tau - tau0).abs();
                        let refined =
                            refine_certificate_replay(certificate_replay, tau0, accepted_tau)?;
                        if $record_sample_rejection {
                            replay_audit.rejected_step_widths.push(rejected_width);
                        }
                        solver = pre_step_solver.take().expect("Type-IX checkpoint exists");
                        latches = saved_latches.clone();
                        requested_cursor = saved_requested_cursor;
                        first_external_carrier = saved_first_external_carrier;
                        history.samples.truncate(saved_sample_len);
                        if let (Some(kind), Some(initial)) =
                            (saved_initial_kind, history.samples.first_mut())
                        {
                            initial.sample_kind = kind;
                        }
                        certificate_replay = Some(refined);
                        continue 'steps;
                    }
                    return Err(error);
                }};
            }
            let accepted_state = vector_from_solver(solver.state().y, n)?;
            if is_type_ix(&request.chart) {
                if let Err(error) =
                    check_type_ix_regularity(&accepted_state, request.rtol, request.atol)
                {
                    replay_or_return!(error, false);
                }
                if let Err(error) = make_sample(
                    request,
                    registry,
                    history.samples.len(),
                    segment_id,
                    phase.clone(),
                    SampleKind::Requested,
                    accepted_tau,
                    accepted_state.clone(),
                    true,
                ) {
                    // A diffsol step whose DAE endpoint misses the frozen
                    // certificate is not an accepted RF-02C step.  Restore
                    // the exact pre-step checkpoint and retry at half width;
                    // do not project or commit the endpoint.
                    replay_or_return!(error, false);
                }
            }
            let scan_tau = if actual_before(final_tau, accepted_tau, forward) {
                final_tau
            } else {
                accepted_tau
            };
            let y1 = if scan_tau.to_bits() == accepted_tau.to_bits() {
                accepted_state
            } else {
                let interpolated = solver.interpolate(scan_tau).map_err(|error| {
                    ExecutionError::new(
                        FailureCode::SolverFailure,
                        format!("endpoint interpolation failed: {error}"),
                    )
                })?;
                vector_from_solver(&interpolated, n)?
            };
            let mut dense_error: Option<ExecutionError> = None;
            let subsegments_result = certify_step(
                &request.chart,
                request.kappa,
                tau0,
                &y0,
                scan_tau,
                &y1,
                request.rtol,
                request.atol,
                &registry,
                |tau| match solver.interpolate(tau) {
                    Ok(vector) => match vector_from_solver(&vector, n) {
                        Ok(state) => Ok(state),
                        Err(error) => {
                            dense_error = Some(error);
                            Err(EventFailure::CarrierNonfinite)
                        }
                    },
                    Err(error) => {
                        dense_error = Some(ExecutionError::new(
                            FailureCode::SolverFailure,
                            format!("carrier interpolation failed: {error}"),
                        ));
                        Err(EventFailure::CarrierCertificateFailure)
                    }
                },
            );
            let subsegments = match subsegments_result {
                Ok(subsegments) => subsegments,
                Err(failure) => {
                    let error = dense_error.unwrap_or_else(|| {
                    ExecutionError::new(
                        event_failure_code(failure),
                        format!(
                            "{failure:?} while certifying accepted interval [{tau0:e}, {scan_tau:e}]"
                        ),
                    )
                    });
                    replay_or_return!(error, false);
                }
            };

            if first_external_carrier {
                let first = subsegments.first().ok_or_else(|| {
                    ExecutionError::new(
                        FailureCode::EventCarrierCertificateFailure,
                        "certified step has no subsegments",
                    )
                })?;
                initial_domain_from_first_carrier(history, &registry, first, &mut latches)?;
                for event in registry
                    .iter()
                    .filter(|event| event.id.starts_with("domain."))
                {
                    if history.samples[0]
                        .certificate_margin(event.margin_id)
                        .is_some_and(|margin| margin < 0.0)
                    {
                        return Err(ExecutionError::new(
                            FailureCode::AcceptedSampleDomainFailure,
                            format!("initial {} certificate is negative", event.margin_id),
                        ));
                    }
                }
            }

            let selected = match select_root(
                &subsegments,
                &registry,
                &mut latches,
                forward,
                first_external_carrier,
                request.kappa,
            ) {
                Ok(selected) => selected,
                Err(failure) => replay_or_return!(ExecutionError::from(failure), true),
            };
            first_external_carrier = false;
            let root_limit = selected.as_ref().map(|root| root.winner.tau);

            if let Some(root) = selected.as_ref() {
                match make_sample(
                    request,
                    &registry,
                    history.samples.len(),
                    segment_id,
                    phase.clone(),
                    SampleKind::EventRoot,
                    root.winner.tau,
                    root.state.clone(),
                    true,
                ) {
                    Ok(_) => {
                        if certificate_replay.is_some() {
                            while replay_audit.accepted_sample_step_widths.len()
                                < replay_audit.rejected_step_widths.len()
                            {
                                replay_audit
                                    .accepted_sample_step_widths
                                    .push((accepted_tau - tau0).abs());
                            }
                        }
                    }
                    Err(error) => replay_or_return!(error, true),
                }
            }

            while requested_cursor < request.requested_taus.len() {
                let requested_tau = request.requested_taus[requested_cursor];
                if !actual_at_or_before(requested_tau, scan_tau, forward) {
                    break;
                }
                if root_limit
                    .is_some_and(|root_tau| !actual_before(requested_tau, root_tau, forward))
                {
                    break;
                }
                let state = if requested_tau.to_bits() == scan_tau.to_bits() {
                    y1.clone()
                } else {
                    let vector = solver.interpolate(requested_tau).map_err(|error| {
                        ExecutionError::new(
                            FailureCode::SolverFailure,
                            format!("requested interpolation failed: {error}"),
                        )
                    })?;
                    vector_from_solver(&vector, n)?
                };
                let sample = match make_sample(
                    request,
                    &registry,
                    history.samples.len(),
                    segment_id,
                    phase.clone(),
                    SampleKind::Requested,
                    requested_tau,
                    state,
                    true,
                ) {
                    Ok(sample) => sample,
                    Err(error) => replay_or_return!(error, true),
                };
                if certificate_replay.is_some() {
                    while replay_audit.accepted_sample_step_widths.len()
                        < replay_audit.rejected_step_widths.len()
                    {
                        replay_audit
                            .accepted_sample_step_widths
                            .push((accepted_tau - tau0).abs());
                    }
                }
                append_sample(history, sample)?;
                requested_cursor += 1;
            }

            let Some(selected) = selected else {
                if scan_tau.to_bits() == final_tau.to_bits() {
                    let end_sample_index =
                        history.samples.len().checked_sub(1).ok_or_else(|| {
                            ExecutionError::new(
                                FailureCode::HistoryInvariantViolation,
                                "completed segment has no sample",
                            )
                        })?;
                    if history.samples[end_sample_index].tau_bits != final_tau.to_bits() {
                        return Err(ExecutionError::new(
                            FailureCode::HistoryInvariantViolation,
                            "requested endpoint was not stored",
                        ));
                    }
                    append_segment(
                        history,
                        SegmentRecord {
                            segment_id,
                            chart: request.chart_label.to_owned(),
                            phase: phase.clone(),
                            tau_start_bits: segment_start_tau.to_bits(),
                            tau_end_bits: final_tau.to_bits(),
                            start_sample_index: segment_start_sample,
                            end_sample_index,
                            status: SegmentStatus::Completed,
                        },
                    )?;
                    history.final_phase = phase;
                    history.status = TrajectoryStatus::Completed;
                    return Ok(());
                }
                continue;
            };

            // Requested samples strictly before the root have been appended.
            // The carrier state is evaluated once and stored before any event
            // or transition record.
            let event = &registry[selected.winner.event_index];
            let (root_sample_index, latch_record) = append_root_records(
                request,
                &registry,
                history,
                segment_id,
                &phase,
                &selected,
                &mut latches,
            )?;
            let event_sequence = history.events.len() - 1;

            if let Some(transition_id) = event.transition_id {
                if transition_id != TYPE_IX_PHASE_TRANSITION
                    || event.id != TYPE_IX_RECOLLAPSE_EVENT
                    || request.chart_label != "type_ix_d_future"
                    || phase != BackgroundPhase::Expanding
                    || event.trajectory_terminal
                    || !event.segment_terminal
                    || !latch_record.consumed
                {
                    return Err(ExecutionError::new(
                        FailureCode::UnsupportedTransition,
                        "event requested a transition outside the frozen Type-IX identity map",
                    ));
                }
                let root_digest = StateDigest::from_state(&selected.state);
                if root_digest != latch_record.root_state_sha256
                    || selected.winner.tau_bits != latch_record.root_tau_bits
                {
                    return Err(ExecutionError::new(
                        FailureCode::RestartIdentityMismatch,
                        "transition root bytes changed before restart",
                    ));
                }
                history
                    .append_transition(TransitionRecord {
                        transition_sequence: history.transitions.len(),
                        transition_id: TYPE_IX_PHASE_TRANSITION.to_owned(),
                        event_sequence,
                        sample_index: root_sample_index,
                        tau_bits: selected.winner.tau_bits,
                        from_chart: request.chart_label.to_owned(),
                        from_phase: BackgroundPhase::Expanding,
                        to_chart: request.chart_label.to_owned(),
                        to_phase: BackgroundPhase::Contracting,
                        state_map: IDENTITY_STATE_MAP.to_owned(),
                        state_bytes_preserved: true,
                    })
                    .map_err(|error| {
                        ExecutionError::new(
                            FailureCode::HistoryInvariantViolation,
                            format!("transition invariant: {error:?}"),
                        )
                    })?;
                append_segment(
                    history,
                    SegmentRecord {
                        segment_id,
                        chart: request.chart_label.to_owned(),
                        phase: phase.clone(),
                        tau_start_bits: segment_start_tau.to_bits(),
                        tau_end_bits: selected.winner.tau_bits,
                        start_sample_index: segment_start_sample,
                        end_sample_index: root_sample_index,
                        status: SegmentStatus::TransitionRequired,
                    },
                )?;

                if (selected.winner.tau - final_tau).abs()
                    <= tau_tie(selected.winner.tau, final_tau)
                {
                    history.final_phase = BackgroundPhase::Contracting;
                    history.status = TrajectoryStatus::CompletedAtTransition;
                    return Ok(());
                }

                // Atomic restart: bytes are copied from the unique root sample,
                // then rechecked before constructing a fresh BDF method.  No
                // epsilon time/state nudge and no duplicate initial sample.
                latch_record
                    .verify_restart(selected.winner.tau, &selected.state)
                    .map_err(|code| {
                        ExecutionError::new(code, "identity restart receipt mismatch")
                    })?;
                while requested_cursor < request.requested_taus.len()
                    && request.requested_taus[requested_cursor].to_bits()
                        == selected.winner.tau_bits
                {
                    requested_cursor += 1;
                }
                initial_state = selected.state;
                segment_start_tau = selected.winner.tau;
                segment_start_sample = root_sample_index;
                segment_id += 1;
                phase = BackgroundPhase::Contracting;
                history.final_phase = phase.clone();
                continue 'segments;
            }

            let status = if event.id.starts_with("domain.") {
                SegmentStatus::DomainBoundary
            } else if event.trajectory_terminal {
                SegmentStatus::EventTerminated
            } else {
                return Err(ExecutionError::new(
                    FailureCode::UnsupportedTransition,
                    "nonterminal event has no frozen transition",
                ));
            };
            append_segment(
                history,
                SegmentRecord {
                    segment_id,
                    chart: request.chart_label.to_owned(),
                    phase: phase.clone(),
                    tau_start_bits: segment_start_tau.to_bits(),
                    tau_end_bits: selected.winner.tau_bits,
                    start_sample_index: segment_start_sample,
                    end_sample_index: root_sample_index,
                    status,
                },
            )?;
            history.final_phase = phase;
            history.status = if event.id.starts_with("domain.") {
                TrajectoryStatus::DomainBoundary
            } else {
                TrajectoryStatus::FailedAfterAcceptedPrefix
            };
            return Ok(());
        }
    }
}

/// Execute one complete RF-02C trajectory.  All failures, including an
/// internal diffsol panic, are returned as typed member history rather than
/// crossing the FFI boundary.
pub(crate) fn integrate_background(request: BackgroundRequest) -> GeometryHistory {
    let mut history = new_history(&request);
    let mut replay_audit = CertificateReplayAudit::default();
    let outcome = catch_unwind(AssertUnwindSafe(|| {
        integrate_impl(&request, &mut history, &mut replay_audit)
    }));
    match outcome {
        Ok(Ok(())) => {}
        Ok(Err(error)) => fail_history(&mut history, error),
        Err(payload) => {
            let detail = payload
                .downcast_ref::<&str>()
                .map(|value| (*value).to_owned())
                .or_else(|| payload.downcast_ref::<String>().cloned())
                .unwrap_or_else(|| "unknown native panic payload".to_owned());
            fail_history(
                &mut history,
                ExecutionError::new(
                    FailureCode::SolverFailure,
                    format!("native trajectory panic caught: {detail}"),
                ),
            );
        }
    }
    history
}

#[cfg(test)]
fn integrate_background_with_replay_audit(
    request: BackgroundRequest,
) -> (GeometryHistory, CertificateReplayAudit) {
    let mut history = new_history(&request);
    let mut replay_audit = CertificateReplayAudit::default();
    let outcome = catch_unwind(AssertUnwindSafe(|| {
        integrate_impl(&request, &mut history, &mut replay_audit)
    }));
    match outcome {
        Ok(Ok(())) => {}
        Ok(Err(error)) => fail_history(&mut history, error),
        Err(_) => fail_history(
            &mut history,
            ExecutionError::new(FailureCode::SolverFailure, "native trajectory panic caught"),
        ),
    }
    (history, replay_audit)
}

fn chart_from_history(history: &GeometryHistory) -> Result<Chart, ExecutionError> {
    let gamma = history.parameters.gamma;
    let kappa = history.parameters.kappa;
    match history.initial_chart.as_str() {
        "class_a" => Ok(Chart::ClassA { gamma }),
        "class_b" => Ok(Chart::ClassB { gamma, kappa }),
        "exceptional" => Ok(Chart::Exceptional { gamma }),
        "type_ix_d" => Ok(Chart::TypeIXD {
            gamma,
            future: false,
        }),
        "type_ix_d_future" => Ok(Chart::TypeIXD {
            gamma,
            future: true,
        }),
        _ => Err(ExecutionError::new(
            FailureCode::RestartIdentityMismatch,
            "restart chart is outside RF-02C",
        )),
    }
}

fn restart_impl(
    previous: &GeometryHistory,
    new_end: f64,
    output: &mut GeometryHistory,
    replay_audit: &mut CertificateReplayAudit,
) -> Result<(), ExecutionError> {
    if previous.route_identity != ROUTE_IDENTITY
        || previous.native_identity != NATIVE_IDENTITY
        || previous.event_registry_hash != REGISTRY_SHA256
        || previous.initial_chart != "type_ix_d_future"
        || previous.final_chart != "type_ix_d_future"
        || !new_end.is_finite()
    {
        return Err(ExecutionError::new(
            FailureCode::RestartIdentityMismatch,
            "restart route/native/registry/chart identity mismatch",
        ));
    }
    let chart = chart_from_history(previous)?;
    let expected_state_names = charts::scalar_state_names(&chart).ok_or_else(|| {
        ExecutionError::new(
            FailureCode::RestartIdentityMismatch,
            "restart chart has no frozen scalar state schema",
        )
    })?;
    if previous.state_names.len() != expected_state_names.len()
        || previous
            .state_names
            .iter()
            .zip(expected_state_names)
            .any(|(observed, expected)| observed != expected)
    {
        return Err(ExecutionError::new(
            FailureCode::RestartIdentityMismatch,
            "restart ordered state schema mismatch",
        ));
    }
    let transition = previous.transitions.last().ok_or_else(|| {
        ExecutionError::new(
            FailureCode::RestartIdentityMismatch,
            "restart history has no frozen transition",
        )
    })?;
    if transition.transition_id != TYPE_IX_PHASE_TRANSITION
        || transition.from_phase != BackgroundPhase::Expanding
        || transition.to_phase != BackgroundPhase::Contracting
        || !transition.state_bytes_preserved
    {
        return Err(ExecutionError::new(
            FailureCode::RestartIdentityMismatch,
            "restart transition receipt does not match V2",
        ));
    }
    let event = previous
        .events
        .get(transition.event_sequence)
        .ok_or_else(|| {
            ExecutionError::new(
                FailureCode::RestartIdentityMismatch,
                "restart transition references a missing event",
            )
        })?;
    let root = previous
        .samples
        .get(transition.sample_index)
        .ok_or_else(|| {
            ExecutionError::new(
                FailureCode::RestartIdentityMismatch,
                "restart transition references a missing root sample",
            )
        })?;
    if event.event_id != TYPE_IX_RECOLLAPSE_EVENT
        || event.transition_id.as_deref() != Some(TYPE_IX_PHASE_TRANSITION)
        || event.sample_index != root.sample_index
        || event.tau_bits != root.tau_bits
        || transition.tau_bits != root.tau_bits
        || root.sample_kind != SampleKind::EventRoot
        || root.phase != BackgroundPhase::Expanding
    {
        return Err(ExecutionError::new(
            FailureCode::RestartIdentityMismatch,
            "restart event/root identities do not match",
        ));
    }
    root.verify_identity().map_err(|error| {
        ExecutionError::new(
            FailureCode::RestartIdentityMismatch,
            format!("restart root identity: {error:?}"),
        )
    })?;
    let latch = EventLatchRecord {
        event_id: event.event_id.clone(),
        margin_id: event.margin_id.clone(),
        direction: RootDirectionClass::Decreasing,
        epsilon_g: event.epsilon_g,
        epsilon_g_bits: event.epsilon_g_bits,
        root_tau_bits: root.tau_bits,
        root_state_sha256: root.state_sha256,
        allowed_rearm_side: AllowedRearmSide::Never,
        consumed: true,
    };
    latch
        .verify_restart(root.tau, &root.state)
        .map_err(|code| ExecutionError::new(code, "stored restart latch does not match root"))?;
    if new_end <= root.tau {
        return Err(ExecutionError::new(
            FailureCode::InvalidInput,
            "restart endpoint must be later than the transition root",
        ));
    }

    let request = BackgroundRequest {
        chart,
        chart_label: "type_ix_d_future",
        initial_state: root.state.clone(),
        requested_taus: vec![root.tau, new_end],
        gamma: previous.parameters.gamma,
        kappa: previous.parameters.kappa,
        rtol: previous.solver_tolerances.rtol,
        atol: previous.solver_tolerances.atol,
        projection_mode: ProjectionMode::Off,
    };
    validate_request(&request)?;
    let registry = builtin_registry(request.chart_label)?;
    let recollapse_index = registry
        .iter()
        .position(|definition| definition.id == TYPE_IX_RECOLLAPSE_EVENT)
        .ok_or_else(|| {
            ExecutionError::new(
                FailureCode::RestartIdentityMismatch,
                "compiled registry is missing recollapse",
            )
        })?;
    let mut latches = vec![RuntimeLatch::initially_armed(); registry.len()];
    latches[recollapse_index] = RuntimeLatch {
        armed: false,
        consumed: true,
        epsilon_bits: Some(event.epsilon_g_bits),
    };

    // Keep the exact accepted prefix through the unique root, then rebuild the
    // contracting suffix from the stored bytes.  Any prior contracting suffix
    // is deliberately discarded from this returned continuation, not mutated.
    output.samples.truncate(root.sample_index + 1);
    output.events.truncate(event.event_sequence + 1);
    output
        .transitions
        .truncate(transition.transition_sequence + 1);
    output.segments.retain(|segment| {
        segment.segment_id == 0
            && segment.status == SegmentStatus::TransitionRequired
            && segment.end_sample_index == root.sample_index
    });
    if output.segments.len() != 1 {
        return Err(ExecutionError::new(
            FailureCode::RestartIdentityMismatch,
            "restart prefix does not contain exactly one expanding transition segment",
        ));
    }
    output.status = TrajectoryStatus::Failed;
    output.failure = None;
    output.final_phase = BackgroundPhase::Contracting;
    run_segment_loop(
        &request,
        output,
        &registry,
        latches,
        1,
        1,
        root.sample_index,
        root.tau,
        BackgroundPhase::Contracting,
        false,
        root.state.clone(),
        new_end,
        true,
        replay_audit,
    )
}

/// Continue a Type-IX transition from the stored root bytes and consumed
/// one-shot latch.  The returned history has one root sample and a rebuilt
/// contracting suffix; no time/state nudge is used.
pub(crate) fn restart_background(previous: &GeometryHistory, new_end: f64) -> GeometryHistory {
    let mut output = previous.clone();
    let mut replay_audit = CertificateReplayAudit::default();
    let outcome = catch_unwind(AssertUnwindSafe(|| {
        restart_impl(previous, new_end, &mut output, &mut replay_audit)
    }));
    match outcome {
        Ok(Ok(())) => {}
        Ok(Err(error)) => fail_history(&mut output, error),
        Err(_) => fail_history(
            &mut output,
            ExecutionError::new(FailureCode::SolverFailure, "native restart panic caught"),
        ),
    }
    output
}

/// Execute independent members in a private Rayon pool.  Indexed collection
/// preserves input order; each serial member catches and types its own failure.
pub(crate) fn integrate_background_batch(
    requests: Vec<BackgroundRequest>,
    threads: usize,
) -> Vec<GeometryHistory> {
    if requests.is_empty() {
        return Vec::new();
    }
    if threads == 0 {
        return requests
            .into_iter()
            .map(|request| {
                let mut history = new_history(&request);
                fail_history(
                    &mut history,
                    ExecutionError::new(FailureCode::InvalidInput, "threads must be positive"),
                );
                history
            })
            .collect();
    }
    let pool = match rayon::ThreadPoolBuilder::new().num_threads(threads).build() {
        Ok(pool) => pool,
        Err(error) => {
            return requests
                .into_iter()
                .map(|request| {
                    let mut history = new_history(&request);
                    fail_history(
                        &mut history,
                        ExecutionError::new(
                            FailureCode::InvalidInput,
                            format!("independent batch pool creation failed: {error}"),
                        ),
                    );
                    history
                })
                .collect();
        }
    };
    pool.install(|| requests.into_par_iter().map(integrate_background).collect())
}

#[cfg(test)]
mod trajectory_tests {
    use super::*;

    fn class_a_request(times: Vec<f64>) -> BackgroundRequest {
        BackgroundRequest {
            chart: Chart::ClassA { gamma: 1.0 },
            chart_label: "class_a",
            initial_state: vec![0.3, 0.0, 0.0, 0.0, 0.0],
            requested_taus: times,
            gamma: 1.0,
            kappa: 0.0,
            rtol: 1.0e-10,
            atol: 1.0e-12,
            projection_mode: ProjectionMode::Off,
        }
    }

    fn type_ix_request(gamma: f64, state: Vec<f64>, times: Vec<f64>) -> BackgroundRequest {
        BackgroundRequest {
            chart: Chart::TypeIXD {
                gamma,
                future: true,
            },
            chart_label: "type_ix_d_future",
            initial_state: state,
            requested_taus: times,
            gamma,
            kappa: 0.0,
            rtol: 1.0e-10,
            atol: 1.0e-12,
            projection_mode: ProjectionMode::Off,
        }
    }

    #[test]
    fn rf02c_trajectory_zero_length_keeps_one_initial_sample() {
        let history = integrate_background(class_a_request(vec![0.0]));
        assert_eq!(history.status, TrajectoryStatus::Completed);
        assert_eq!(history.samples.len(), 1);
        assert_eq!(history.samples[0].sample_kind, SampleKind::Initial);
        assert!(history.events.is_empty());
    }

    #[test]
    fn rf02c_trajectory_initial_domain_violation_is_typed() {
        let mut request = class_a_request(vec![0.0]);
        request.initial_state[0] = 2.0;
        let history = integrate_background(request);
        assert_eq!(history.status, TrajectoryStatus::Failed);
        assert_eq!(
            history.failure.as_ref().map(|failure| failure.code),
            Some(FailureCode::InitialDomainViolation)
        );

        let mut stepping_request = class_a_request(vec![0.0, 0.1]);
        stepping_request.initial_state[0] = 2.0;
        let stepping_history = integrate_background(stepping_request);
        assert_eq!(stepping_history.status, TrajectoryStatus::Failed);
        assert_eq!(
            stepping_history
                .failure
                .as_ref()
                .map(|failure| failure.code),
            Some(FailureCode::InitialDomainViolation)
        );
    }

    #[test]
    fn rf02c_trajectory_class_a_flat_dust_matches_closed_form() {
        let history = integrate_background(class_a_request(vec![0.0, 0.1]));
        assert_eq!(
            history.status,
            TrajectoryStatus::Completed,
            "{:?}",
            history.failure
        );
        let sigma = history.samples.last().unwrap().state[0];
        let u0 = 0.3f64 * 0.3;
        let e = (-0.3f64).exp();
        let expected = (u0 * e / (1.0 - u0 + u0 * e)).sqrt();
        let scale = 1.0e-12 + 1.0e-10 * sigma.abs().max(expected.abs()).max(1.0);
        assert!((sigma - expected).abs() / scale <= 32.0);
    }

    #[test]
    fn rf02c_trajectory_backward_direction_uses_negative_builder_sign() {
        let history = integrate_background(class_a_request(vec![0.0, -0.1]));
        assert_eq!(
            history.status,
            TrajectoryStatus::Completed,
            "{:?}",
            history.failure
        );
        assert_eq!(
            history.samples.last().unwrap().tau.to_bits(),
            (-0.1f64).to_bits()
        );
        let sigma = history.samples.last().unwrap().state[0];
        let u0 = 0.3f64 * 0.3;
        let e = 0.3f64.exp();
        let expected = (u0 * e / (1.0 - u0 + u0 * e)).sqrt();
        let scale = 1.0e-12 + 1.0e-10 * sigma.abs().max(expected.abs()).max(1.0);
        assert!((sigma - expected).abs() / scale <= 32.0);
    }

    #[test]
    fn rf02c_trajectory_batch_order_failure_isolation_and_threads_are_identical() {
        let first = class_a_request(vec![0.0, 0.1]);
        let mut invalid = class_a_request(vec![0.0]);
        invalid.initial_state[0] = 2.0;
        let mut third = class_a_request(vec![0.0, 0.1]);
        third.initial_state[0] = 0.2;
        let requests = vec![first, invalid, third];
        let one = integrate_background_batch(requests.clone(), 1);
        let many = integrate_background_batch(requests, 4);
        assert_eq!(one, many);
        assert_eq!(
            one.iter().map(|history| history.status).collect::<Vec<_>>(),
            vec![
                TrajectoryStatus::Completed,
                TrajectoryStatus::Failed,
                TrajectoryStatus::Completed,
            ]
        );
    }

    #[test]
    fn rf02c_type_ix_dae_singular_chart_is_typed_before_solver_entry() {
        let request = type_ix_request(
            1.0,
            vec![1.0, 0.0, 0.0, 0.0, 1.0e-12, 1.0e-12, 1.0e-12],
            vec![0.0, 0.1],
        );
        let history = integrate_background(request);
        assert_eq!(history.status, TrajectoryStatus::Failed);
        assert_eq!(
            history.failure.as_ref().map(|failure| failure.code),
            Some(FailureCode::TypeIxDaeSingularChart)
        );
    }

    #[test]
    fn rf02c_type_ix_dae_static_oracle_remains_exact() {
        let n = 2.0f64.sqrt();
        let mut request = type_ix_request(
            2.0 / 3.0,
            vec![0.0, 0.0, 0.0, 0.0, n, n, n],
            vec![0.0, 0.25],
        );
        request.chart = Chart::TypeIXD {
            gamma: 2.0 / 3.0,
            future: false,
        };
        request.chart_label = "type_ix_d";
        let initial_state = request.initial_state.clone();
        let history = integrate_background(request);
        assert_eq!(
            history.status,
            TrajectoryStatus::Completed,
            "{:?}",
            history.failure
        );
        let final_state = &history.samples.last().unwrap().state;
        for (actual, expected) in final_state.iter().zip(&initial_state) {
            assert!((actual - expected).abs() <= 64.0 * f64::EPSILON);
        }
        assert!(history
            .samples
            .iter()
            .all(|sample| sample.normalized_constraint_residual <= 1.0));
    }

    #[test]
    fn rf02c_type_ix_dae_certificate_local_replay_closes_coarse_root() {
        let h0 = 0.8;
        let n0 = (2.0f64 * (1.0 - h0 * h0)).sqrt();
        let request = type_ix_request(1.0, vec![h0, 0.0, 0.0, 0.0, n0, n0, n0], vec![0.0, 4.0]);
        let (history, replay) = integrate_background_with_replay_audit(request);
        assert_eq!(
            history.status,
            TrajectoryStatus::Completed,
            "{:?}",
            history.failure
        );
        assert_eq!(history.events.len(), 1);
        assert_eq!(
            replay.rejected_step_widths.len(),
            replay.accepted_sample_step_widths.len()
        );
        for (rejected, accepted) in replay
            .rejected_step_widths
            .iter()
            .zip(&replay.accepted_sample_step_widths)
        {
            assert!(*accepted <= 0.5 * *rejected);
        }
        let root = &history.samples[history.events[0].sample_index];
        let event = &history.events[0];
        assert!(root.normalized_constraint_residual <= 1.0);
        assert_eq!(event.raw_margin.to_bits(), root.state[0].to_bits());
        assert!(event.raw_margin.abs() <= event.epsilon_g);
    }

    #[test]
    fn rf02c_trajectory_type_ix_recollapse_restarts_without_duplicate_root() {
        let h0 = 0.8;
        let n0 = (2.0f64 * (1.0 - h0 * h0)).sqrt();
        let request = BackgroundRequest {
            chart: Chart::TypeIXD {
                gamma: 1.0,
                future: true,
            },
            chart_label: "type_ix_d_future",
            initial_state: vec![h0, 0.0, 0.0, 0.0, n0, n0, n0],
            requested_taus: vec![0.0, 4.0],
            gamma: 1.0,
            kappa: 0.0,
            rtol: 1.0e-10,
            atol: 1.0e-12,
            projection_mode: ProjectionMode::Off,
        };
        let history = integrate_background(request);
        assert_eq!(
            history.status,
            TrajectoryStatus::Completed,
            "{:?}",
            history.failure
        );
        assert_eq!(history.events.len(), 1);
        assert_eq!(history.transitions.len(), 1);
        assert_eq!(history.segments.len(), 2);
        let event = &history.events[0];
        let transition = &history.transitions[0];
        assert_eq!(event.event_id, TYPE_IX_RECOLLAPSE_EVENT);
        assert_eq!(event.sample_index, transition.sample_index);
        let root_tau_bits = event.tau_bits;
        assert_eq!(
            history
                .samples
                .iter()
                .filter(|sample| sample.tau_bits == root_tau_bits)
                .count(),
            1
        );
        let root_tau = f64::from_bits(root_tau_bits);
        assert!((root_tau - 3.546706461783325).abs() <= 8.0 * tau_tie(root_tau, 3.546706461783325));
    }

    #[test]
    fn rf02c_type_ix_dae_restart_api_preserves_root_bytes() {
        let h0 = 0.8;
        let n0 = (2.0f64 * (1.0 - h0 * h0)).sqrt();
        let request = type_ix_request(1.0, vec![h0, 0.0, 0.0, 0.0, n0, n0, n0], vec![0.0, 3.8]);
        let first = integrate_background(request);
        assert_eq!(
            first.status,
            TrajectoryStatus::Completed,
            "{:?}",
            first.failure
        );
        let first_event = &first.events[0];
        let first_root = first.samples[first_event.sample_index].clone();

        let restarted = restart_background(&first, 4.0);
        assert_eq!(
            restarted.status,
            TrajectoryStatus::Completed,
            "{:?}",
            restarted.failure
        );
        assert_eq!(restarted.events.len(), 1);
        assert_eq!(restarted.transitions.len(), 1);
        let restarted_event = &restarted.events[0];
        let restarted_root = &restarted.samples[restarted_event.sample_index];
        assert_eq!(restarted_root.tau_bits, first_root.tau_bits);
        assert_eq!(restarted_root.state_sha256, first_root.state_sha256);
        assert_eq!(restarted_root.state.len(), first_root.state.len());
        for (actual, expected) in restarted_root.state.iter().zip(&first_root.state) {
            assert_eq!(actual.to_bits(), expected.to_bits());
        }
        assert_eq!(
            restarted
                .samples
                .iter()
                .filter(|sample| sample.tau_bits == first_root.tau_bits)
                .count(),
            1
        );
        assert_eq!(
            restarted.segments[1].start_sample_index,
            restarted_root.sample_index
        );

        let direct = integrate_background(type_ix_request(
            1.0,
            vec![h0, 0.0, 0.0, 0.0, n0, n0, n0],
            vec![0.0, 4.0],
        ));
        assert_eq!(
            direct.status,
            TrajectoryStatus::Completed,
            "{:?}",
            direct.failure
        );
        let restarted_final = &restarted.samples.last().unwrap().state;
        let direct_final = &direct.samples.last().unwrap().state;
        for (actual, expected) in restarted_final.iter().zip(direct_final) {
            let scale = 1.0e-12 + 1.0e-10 * actual.abs().max(expected.abs()).max(1.0);
            assert!((actual - expected).abs() / scale <= 32.0);
        }
    }

    #[test]
    fn rf02c_restart_rejects_mutated_ordered_state_schema() {
        let h0 = 0.8;
        let n0 = (2.0f64 * (1.0 - h0 * h0)).sqrt();
        let mut first = integrate_background(type_ix_request(
            1.0,
            vec![h0, 0.0, 0.0, 0.0, n0, n0, n0],
            vec![0.0, 3.8],
        ));
        first.state_names.fill("tampered".to_owned());

        let restarted = restart_background(&first, 4.0);

        assert_eq!(
            restarted.status,
            TrajectoryStatus::FailedAfterAcceptedPrefix
        );
        assert_eq!(
            restarted.failure.as_ref().map(|failure| failure.code),
            Some(FailureCode::RestartIdentityMismatch)
        );
    }

    #[test]
    fn rf02c_initial_recollapse_reuses_the_unique_initial_root_sample() {
        let n = 2.0f64.sqrt();
        let history = integrate_background(type_ix_request(
            1.0,
            vec![0.0, 0.0, 0.0, 0.0, n, n, n],
            vec![0.0, 0.1],
        ));

        assert_eq!(history.status, TrajectoryStatus::Completed);
        assert_eq!(history.events.len(), 1);
        assert_eq!(history.events[0].sample_index, 0);
        assert_eq!(history.samples[0].sample_kind, SampleKind::EventRoot);
        assert_eq!(
            history
                .samples
                .iter()
                .filter(|sample| sample.tau_bits == 0.0f64.to_bits())
                .count(),
            1
        );
    }
}
