//! RF-02C normalized background-geometry history and byte-identity records.
//!
//! This module deliberately contains no chart equations or solver logic.  It
//! owns only the V2 history schema, typed terminal/failure states, and the
//! byte-identity checks used when an event root is restarted.

use std::fmt;

pub(crate) const HISTORY_SCHEMA: &str = "bass-background-geometry-history/v2";
pub(crate) const TYPE_IX_RECOLLAPSE_EVENT: &str = "type_ix_recollapse";
pub(crate) const TYPE_IX_PHASE_TRANSITION: &str = "type_ix_expanding_to_contracting";
pub(crate) const IDENTITY_STATE_MAP: &str = "identity";

/// Lowercase fixed-width encoding required for every public `tau_bits` field.
pub(crate) fn tau_bits_hex(bits: u64) -> String {
    format!("{bits:016x}")
}

/// The same fixed-width encoding is used for persisted `epsilon_g_bits`.
pub(crate) fn epsilon_bits_hex(bits: u64) -> String {
    format!("{bits:016x}")
}

/// SHA-256 digest of frozen-order state component bytes.
#[derive(Clone, Copy, PartialEq, Eq, Hash)]
pub(crate) struct StateDigest([u8; 32]);

impl StateDigest {
    /// Hash each component as its unsigned IEEE-754 `to_bits`, big endian.
    pub(crate) fn from_state(state: &[f64]) -> Self {
        let mut hasher = Sha256::new();
        for value in state {
            hasher.update(&value.to_bits().to_be_bytes());
        }
        Self(hasher.finalize())
    }

    pub(crate) fn from_bytes(bytes: [u8; 32]) -> Self {
        Self(bytes)
    }

    pub(crate) fn as_bytes(&self) -> &[u8; 32] {
        &self.0
    }

    pub(crate) fn to_hex(self) -> String {
        hex_lower(&self.0)
    }
}

impl fmt::Debug for StateDigest {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter.write_str(&hex_lower(&self.0))
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) enum BackgroundPhase {
    /// Non-transition charts retain the caller-selected phase label without
    /// assigning it new scientific meaning.
    Named(String),
    Expanding,
    Contracting,
}

impl BackgroundPhase {
    pub(crate) fn as_str(&self) -> &str {
        match self {
            Self::Named(value) => value.as_str(),
            Self::Expanding => "expanding",
            Self::Contracting => "contracting",
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum SampleKind {
    Initial,
    Requested,
    EventRoot,
}

impl SampleKind {
    pub(crate) fn as_str(self) -> &'static str {
        match self {
            Self::Initial => "initial",
            Self::Requested => "requested",
            Self::EventRoot => "event_root",
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum SegmentStatus {
    Completed,
    DomainBoundary,
    EventTerminated,
    TransitionRequired,
    Failed,
}

impl SegmentStatus {
    pub(crate) fn as_str(self) -> &'static str {
        match self {
            Self::Completed => "COMPLETED",
            Self::DomainBoundary => "DOMAIN_BOUNDARY",
            Self::EventTerminated => "EVENT_TERMINATED",
            Self::TransitionRequired => "TRANSITION_REQUIRED",
            Self::Failed => "FAILED",
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum TrajectoryStatus {
    Completed,
    CompletedAtTransition,
    DomainBoundary,
    FailedAfterAcceptedPrefix,
    Failed,
}

impl TrajectoryStatus {
    pub(crate) fn as_str(self) -> &'static str {
        match self {
            Self::Completed => "COMPLETED",
            Self::CompletedAtTransition => "COMPLETED_AT_TRANSITION",
            Self::DomainBoundary => "DOMAIN_BOUNDARY",
            Self::FailedAfterAcceptedPrefix => "FAILED_AFTER_ACCEPTED_PREFIX",
            Self::Failed => "FAILED",
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(i8)]
pub(crate) enum RootDirectionClass {
    Decreasing = -1,
    Tangential = 0,
    Increasing = 1,
}

impl RootDirectionClass {
    pub(crate) fn as_i8(self) -> i8 {
        self as i8
    }
}

/// Typed RF-02C execution failures that can be persisted in a member result.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum FailureCode {
    InvalidInput,
    InitialDomainViolation,
    TypeIxDaeSingularChart,
    UnsupportedEventExpression,
    UnsupportedTransition,
    EventCarrierNonfinite,
    EventCarrierCertificateFailure,
    NonadvancingAcceptedStep,
    EventRootRepresentationFailure,
    RestartIdentityMismatch,
    AcceptedSampleNonfinite,
    AcceptedSampleSchemaMismatch,
    AcceptedSampleConstraintFailure,
    AcceptedSampleDomainFailure,
    ProjectionInvalidInput,
    ProjectionSingular,
    ProjectionNonfinite,
    ProjectionNonMonotone,
    ProjectionNotConverged,
    ProjectionPhysicalDomain,
    SolverFailure,
    HistoryInvariantViolation,
}

impl FailureCode {
    pub(crate) fn as_str(self) -> &'static str {
        match self {
            Self::InvalidInput => "INVALID_INPUT",
            Self::InitialDomainViolation => "INITIAL_DOMAIN_VIOLATION",
            Self::TypeIxDaeSingularChart => "TYPE_IX_DAE_SINGULAR_CHART",
            Self::UnsupportedEventExpression => "UNSUPPORTED_EVENT_EXPRESSION",
            Self::UnsupportedTransition => "UNSUPPORTED_TRANSITION",
            Self::EventCarrierNonfinite => "EVENT_CARRIER_NONFINITE",
            Self::EventCarrierCertificateFailure => "EVENT_CARRIER_CERTIFICATE_FAILURE",
            Self::NonadvancingAcceptedStep => "NONADVANCING_ACCEPTED_STEP",
            Self::EventRootRepresentationFailure => "EVENT_ROOT_REPRESENTATION_FAILURE",
            Self::RestartIdentityMismatch => "RESTART_IDENTITY_MISMATCH",
            Self::AcceptedSampleNonfinite => "ACCEPTED_SAMPLE_NONFINITE",
            Self::AcceptedSampleSchemaMismatch => "ACCEPTED_SAMPLE_SCHEMA_MISMATCH",
            Self::AcceptedSampleConstraintFailure => "ACCEPTED_SAMPLE_CONSTRAINT_FAILURE",
            Self::AcceptedSampleDomainFailure => "ACCEPTED_SAMPLE_DOMAIN_FAILURE",
            Self::ProjectionInvalidInput => "PROJECTION_INVALID_INPUT",
            Self::ProjectionSingular => "PROJECTION_SINGULAR",
            Self::ProjectionNonfinite => "PROJECTION_NONFINITE",
            Self::ProjectionNonMonotone => "PROJECTION_NON_MONOTONE",
            Self::ProjectionNotConverged => "PROJECTION_NOT_CONVERGED",
            Self::ProjectionPhysicalDomain => "PROJECTION_PHYSICAL_DOMAIN",
            Self::SolverFailure => "SOLVER_FAILURE",
            Self::HistoryInvariantViolation => "HISTORY_INVARIANT_VIOLATION",
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct FailureRecord {
    pub code: FailureCode,
    pub detail: String,
}

impl FailureRecord {
    pub(crate) fn new(code: FailureCode, detail: impl Into<String>) -> Self {
        Self {
            code,
            detail: detail.into(),
        }
    }
}

#[derive(Clone, Debug, PartialEq)]
pub(crate) struct NamedValue {
    pub name: String,
    pub value: f64,
}

impl NamedValue {
    pub(crate) fn new(name: impl Into<String>, value: f64) -> Self {
        Self {
            name: name.into(),
            value,
        }
    }
}

#[derive(Clone, Debug, PartialEq)]
pub(crate) struct TypeIxDiagnostics {
    pub h_bar: f64,
    pub sigma2: f64,
    pub definition: f64,
    pub trace: f64,
}

#[derive(Clone, Debug, PartialEq)]
pub(crate) struct GeometrySample {
    pub sample_index: usize,
    pub segment_id: usize,
    pub phase: BackgroundPhase,
    pub sample_kind: SampleKind,
    pub tau: f64,
    pub tau_bits: u64,
    pub state: Vec<f64>,
    pub state_sha256: StateDigest,
    pub omega: f64,
    pub equality_constraints: Vec<NamedValue>,
    pub normalized_constraint_residual: f64,
    pub domain_margins_raw: Vec<NamedValue>,
    pub domain_margins_certificate: Vec<NamedValue>,
    pub type_ix: Option<TypeIxDiagnostics>,
}

impl GeometrySample {
    #[allow(clippy::too_many_arguments)]
    pub(crate) fn new(
        sample_index: usize,
        segment_id: usize,
        phase: BackgroundPhase,
        sample_kind: SampleKind,
        tau: f64,
        state: Vec<f64>,
        omega: f64,
        equality_constraints: Vec<NamedValue>,
        normalized_constraint_residual: f64,
        domain_margins_raw: Vec<NamedValue>,
        domain_margins_certificate: Vec<NamedValue>,
        type_ix: Option<TypeIxDiagnostics>,
    ) -> Self {
        let tau_bits = tau.to_bits();
        let state_sha256 = StateDigest::from_state(&state);
        Self {
            sample_index,
            segment_id,
            phase,
            sample_kind,
            tau,
            tau_bits,
            state,
            state_sha256,
            omega,
            equality_constraints,
            normalized_constraint_residual,
            domain_margins_raw,
            domain_margins_certificate,
            type_ix,
        }
    }

    pub(crate) fn verify_identity(&self) -> Result<(), HistoryInvariantError> {
        if self.tau.to_bits() != self.tau_bits {
            return Err(HistoryInvariantError::TauBitsMismatch);
        }
        if StateDigest::from_state(&self.state) != self.state_sha256 {
            return Err(HistoryInvariantError::StateDigestMismatch);
        }
        Ok(())
    }

    pub(crate) fn raw_margin(&self, margin_id: &str) -> Option<f64> {
        named_value(&self.domain_margins_raw, margin_id)
    }

    pub(crate) fn certificate_margin(&self, margin_id: &str) -> Option<f64> {
        named_value(&self.domain_margins_certificate, margin_id)
    }
}

#[derive(Clone, Debug, PartialEq)]
pub(crate) struct EventRecord {
    pub event_sequence: usize,
    pub event_id: String,
    pub margin_id: String,
    pub root_multiplicity: usize,
    pub direction_class: RootDirectionClass,
    pub priority: u32,
    pub simultaneous_group: usize,
    pub sample_index: usize,
    pub tau_bits: u64,
    pub epsilon_g: f64,
    pub epsilon_g_bits: u64,
    pub raw_margin: f64,
    pub certificate_margin: f64,
    pub segment_terminal: bool,
    pub trajectory_terminal: bool,
    pub transition_id: Option<String>,
}

impl EventRecord {
    pub(crate) fn freeze_epsilon(&mut self, epsilon_g: f64) {
        self.epsilon_g = epsilon_g;
        self.epsilon_g_bits = epsilon_g.to_bits();
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct TransitionRecord {
    pub transition_sequence: usize,
    pub transition_id: String,
    pub event_sequence: usize,
    pub sample_index: usize,
    pub tau_bits: u64,
    pub from_chart: String,
    pub from_phase: BackgroundPhase,
    pub to_chart: String,
    pub to_phase: BackgroundPhase,
    pub state_map: String,
    pub state_bytes_preserved: bool,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum AllowedRearmSide {
    AbovePositiveEpsilon,
    BelowNegativeEpsilon,
    EitherOutsideZeroBand,
    Never,
}

impl AllowedRearmSide {
    pub(crate) fn as_str(self) -> &'static str {
        match self {
            Self::AbovePositiveEpsilon => "g_raw > epsilon_g",
            Self::BelowNegativeEpsilon => "g_raw < -epsilon_g",
            Self::EitherOutsideZeroBand => "abs(g_raw) > epsilon_g",
            Self::Never => "never",
        }
    }
}

#[derive(Clone, Debug, PartialEq)]
pub(crate) struct EventLatchRecord {
    pub event_id: String,
    pub margin_id: String,
    pub direction: RootDirectionClass,
    pub epsilon_g: f64,
    pub epsilon_g_bits: u64,
    pub root_tau_bits: u64,
    pub root_state_sha256: StateDigest,
    pub allowed_rearm_side: AllowedRearmSide,
    pub consumed: bool,
}

impl EventLatchRecord {
    pub(crate) fn verify_restart(&self, tau: f64, state: &[f64]) -> Result<(), FailureCode> {
        if tau.to_bits() != self.root_tau_bits
            || StateDigest::from_state(state) != self.root_state_sha256
            || self.epsilon_g.to_bits() != self.epsilon_g_bits
        {
            return Err(FailureCode::RestartIdentityMismatch);
        }
        Ok(())
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct SegmentRecord {
    pub segment_id: usize,
    pub chart: String,
    pub phase: BackgroundPhase,
    pub tau_start_bits: u64,
    pub tau_end_bits: u64,
    pub start_sample_index: usize,
    pub end_sample_index: usize,
    pub status: SegmentStatus,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub(crate) struct BackgroundParameters {
    pub gamma: f64,
    pub kappa: f64,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub(crate) struct SolverTolerances {
    pub rtol: f64,
    pub atol: f64,
}

#[derive(Clone, Debug, PartialEq)]
pub(crate) struct GeometryHistory {
    pub route_identity: String,
    pub native_identity: String,
    pub event_registry_hash: String,
    pub initial_chart: String,
    pub initial_phase: BackgroundPhase,
    pub final_chart: String,
    pub final_phase: BackgroundPhase,
    pub parameters: BackgroundParameters,
    pub solver_tolerances: SolverTolerances,
    pub state_names: Vec<String>,
    pub segments: Vec<SegmentRecord>,
    pub samples: Vec<GeometrySample>,
    pub events: Vec<EventRecord>,
    pub transitions: Vec<TransitionRecord>,
    pub status: TrajectoryStatus,
    pub failure: Option<FailureRecord>,
}

impl GeometryHistory {
    #[allow(clippy::too_many_arguments)]
    pub(crate) fn new(
        route_identity: impl Into<String>,
        native_identity: impl Into<String>,
        event_registry_hash: impl Into<String>,
        chart: impl Into<String>,
        phase: BackgroundPhase,
        parameters: BackgroundParameters,
        solver_tolerances: SolverTolerances,
        state_names: Vec<String>,
    ) -> Self {
        let chart = chart.into();
        Self {
            route_identity: route_identity.into(),
            native_identity: native_identity.into(),
            event_registry_hash: event_registry_hash.into(),
            initial_chart: chart.clone(),
            initial_phase: phase.clone(),
            final_chart: chart,
            final_phase: phase,
            parameters,
            solver_tolerances,
            state_names,
            segments: Vec::new(),
            samples: Vec::new(),
            events: Vec::new(),
            transitions: Vec::new(),
            status: TrajectoryStatus::Failed,
            failure: None,
        }
    }

    pub(crate) fn append_sample(
        &mut self,
        sample: GeometrySample,
    ) -> Result<usize, HistoryInvariantError> {
        if sample.sample_index != self.samples.len() {
            return Err(HistoryInvariantError::NonSequentialSample);
        }
        sample.verify_identity()?;
        let index = sample.sample_index;
        self.samples.push(sample);
        Ok(index)
    }

    pub(crate) fn append_event(
        &mut self,
        event: EventRecord,
    ) -> Result<usize, HistoryInvariantError> {
        if event.event_sequence != self.events.len() {
            return Err(HistoryInvariantError::NonSequentialEvent);
        }
        if event.epsilon_g.to_bits() != event.epsilon_g_bits {
            return Err(HistoryInvariantError::EpsilonBitsMismatch);
        }
        let sample = self
            .samples
            .get(event.sample_index)
            .ok_or(HistoryInvariantError::SampleReferenceOutOfRange)?;
        if sample.sample_kind != SampleKind::EventRoot {
            return Err(HistoryInvariantError::EventDoesNotReferenceRootSample);
        }
        if sample.tau_bits != event.tau_bits {
            return Err(HistoryInvariantError::TauBitsMismatch);
        }
        let raw = sample
            .raw_margin(&event.margin_id)
            .ok_or(HistoryInvariantError::MissingEventMargin)?;
        let certificate = sample
            .certificate_margin(&event.margin_id)
            .ok_or(HistoryInvariantError::MissingEventMargin)?;
        if raw.to_bits() != event.raw_margin.to_bits()
            || certificate.to_bits() != event.certificate_margin.to_bits()
        {
            return Err(HistoryInvariantError::EventMarginMismatch);
        }
        let index = event.event_sequence;
        self.events.push(event);
        Ok(index)
    }

    pub(crate) fn append_transition(
        &mut self,
        transition: TransitionRecord,
    ) -> Result<usize, HistoryInvariantError> {
        if transition.transition_sequence != self.transitions.len() {
            return Err(HistoryInvariantError::NonSequentialTransition);
        }
        let event = self
            .events
            .get(transition.event_sequence)
            .ok_or(HistoryInvariantError::EventReferenceOutOfRange)?;
        let sample = self
            .samples
            .get(transition.sample_index)
            .ok_or(HistoryInvariantError::SampleReferenceOutOfRange)?;
        if event.sample_index != transition.sample_index
            || event.tau_bits != transition.tau_bits
            || sample.tau_bits != transition.tau_bits
        {
            return Err(HistoryInvariantError::TransitionReferenceMismatch);
        }
        if transition.transition_id != TYPE_IX_PHASE_TRANSITION
            || event.event_id != TYPE_IX_RECOLLAPSE_EVENT
            || event.transition_id.as_deref() != Some(TYPE_IX_PHASE_TRANSITION)
            || transition.from_chart != "type_ix_d_future"
            || transition.to_chart != "type_ix_d_future"
            || transition.from_phase != BackgroundPhase::Expanding
            || transition.to_phase != BackgroundPhase::Contracting
            || transition.state_map != IDENTITY_STATE_MAP
            || !transition.state_bytes_preserved
        {
            return Err(HistoryInvariantError::UnsupportedTransition);
        }
        let index = transition.transition_sequence;
        self.transitions.push(transition);
        Ok(index)
    }

    pub(crate) fn append_segment(
        &mut self,
        segment: SegmentRecord,
    ) -> Result<usize, HistoryInvariantError> {
        if segment.segment_id != self.segments.len() {
            return Err(HistoryInvariantError::NonSequentialSegment);
        }
        let start = self
            .samples
            .get(segment.start_sample_index)
            .ok_or(HistoryInvariantError::SampleReferenceOutOfRange)?;
        let end = self
            .samples
            .get(segment.end_sample_index)
            .ok_or(HistoryInvariantError::SampleReferenceOutOfRange)?;
        let current_segment_start =
            start.segment_id == segment.segment_id && start.phase == segment.phase;
        // The sole V2 transition starts the contracting segment from the
        // already stored expanding root sample.  It deliberately does not
        // append a duplicate restart-initial sample.
        let atomic_transition_start = segment.segment_id > 0
            && start.sample_kind == SampleKind::EventRoot
            && start.segment_id + 1 == segment.segment_id
            && self.transitions.iter().any(|transition| {
                transition.sample_index == segment.start_sample_index
                    && transition.tau_bits == segment.tau_start_bits
                    && transition.to_chart == segment.chart
                    && transition.to_phase == segment.phase
            });
        if start.tau_bits != segment.tau_start_bits
            || end.tau_bits != segment.tau_end_bits
            || (!current_segment_start && !atomic_transition_start)
            || end.segment_id != segment.segment_id
            || end.phase != segment.phase
        {
            return Err(HistoryInvariantError::SegmentReferenceMismatch);
        }
        let index = segment.segment_id;
        self.segments.push(segment);
        Ok(index)
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum HistoryInvariantError {
    NonSequentialSample,
    NonSequentialEvent,
    NonSequentialTransition,
    NonSequentialSegment,
    TauBitsMismatch,
    StateDigestMismatch,
    EpsilonBitsMismatch,
    SampleReferenceOutOfRange,
    EventReferenceOutOfRange,
    EventDoesNotReferenceRootSample,
    MissingEventMargin,
    EventMarginMismatch,
    TransitionReferenceMismatch,
    SegmentReferenceMismatch,
    UnsupportedTransition,
}

fn named_value(values: &[NamedValue], name: &str) -> Option<f64> {
    values
        .iter()
        .find(|item| item.name == name)
        .map(|item| item.value)
}

fn hex_lower(bytes: &[u8]) -> String {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let mut result = String::with_capacity(bytes.len() * 2);
    for byte in bytes {
        result.push(HEX[(byte >> 4) as usize] as char);
        result.push(HEX[(byte & 0x0f) as usize] as char);
    }
    result
}

/// Small, dependency-free SHA-256 implementation used only for V2 state-byte
/// identity.  It consumes bytes exactly as supplied; no archive or text
/// normalization is involved.
struct Sha256 {
    state: [u32; 8],
    block: [u8; 64],
    block_len: usize,
    total_len: u64,
}

impl Sha256 {
    fn new() -> Self {
        Self {
            state: [
                0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab,
                0x5be0cd19,
            ],
            block: [0; 64],
            block_len: 0,
            total_len: 0,
        }
    }

    fn update(&mut self, mut bytes: &[u8]) {
        self.total_len = self
            .total_len
            .checked_add(bytes.len() as u64)
            .expect("RF-02C state-byte input length overflow");
        if self.block_len != 0 {
            let take = (64 - self.block_len).min(bytes.len());
            self.block[self.block_len..self.block_len + take].copy_from_slice(&bytes[..take]);
            self.block_len += take;
            bytes = &bytes[take..];
            if self.block_len == 64 {
                let block = self.block;
                compress(&mut self.state, &block);
                self.block_len = 0;
            } else {
                return;
            }
        }
        while bytes.len() >= 64 {
            let block: &[u8; 64] = bytes[..64].try_into().expect("fixed SHA-256 block");
            compress(&mut self.state, block);
            bytes = &bytes[64..];
        }
        self.block[..bytes.len()].copy_from_slice(bytes);
        self.block_len = bytes.len();
    }

    fn finalize(mut self) -> [u8; 32] {
        let bit_len = self.total_len.wrapping_mul(8);
        self.block[self.block_len] = 0x80;
        self.block_len += 1;
        if self.block_len > 56 {
            self.block[self.block_len..].fill(0);
            let block = self.block;
            compress(&mut self.state, &block);
            self.block = [0; 64];
        } else {
            self.block[self.block_len..56].fill(0);
        }
        self.block[56..64].copy_from_slice(&bit_len.to_be_bytes());
        let block = self.block;
        compress(&mut self.state, &block);

        let mut output = [0u8; 32];
        for (chunk, word) in output.chunks_exact_mut(4).zip(self.state) {
            chunk.copy_from_slice(&word.to_be_bytes());
        }
        output
    }
}

fn compress(state: &mut [u32; 8], block: &[u8; 64]) {
    const K: [u32; 64] = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4,
        0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe,
        0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f,
        0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
        0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc,
        0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
        0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116,
        0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7,
        0xc67178f2,
    ];
    let mut schedule = [0u32; 64];
    for (word, bytes) in schedule[..16].iter_mut().zip(block.chunks_exact(4)) {
        *word = u32::from_be_bytes(bytes.try_into().expect("fixed SHA-256 word"));
    }
    for index in 16..64 {
        let s0 = schedule[index - 15].rotate_right(7)
            ^ schedule[index - 15].rotate_right(18)
            ^ (schedule[index - 15] >> 3);
        let s1 = schedule[index - 2].rotate_right(17)
            ^ schedule[index - 2].rotate_right(19)
            ^ (schedule[index - 2] >> 10);
        schedule[index] = schedule[index - 16]
            .wrapping_add(s0)
            .wrapping_add(schedule[index - 7])
            .wrapping_add(s1);
    }

    let [mut a, mut b, mut c, mut d, mut e, mut f, mut g, mut h] = *state;
    for (word, constant) in schedule.into_iter().zip(K) {
        let sum1 = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
        let choose = (e & f) ^ ((!e) & g);
        let temp1 = h
            .wrapping_add(sum1)
            .wrapping_add(choose)
            .wrapping_add(constant)
            .wrapping_add(word);
        let sum0 = a.rotate_right(2) ^ a.rotate_right(13) ^ a.rotate_right(22);
        let majority = (a & b) ^ (a & c) ^ (b & c);
        let temp2 = sum0.wrapping_add(majority);
        h = g;
        g = f;
        f = e;
        e = d.wrapping_add(temp1);
        d = c;
        c = b;
        b = a;
        a = temp1.wrapping_add(temp2);
    }
    state[0] = state[0].wrapping_add(a);
    state[1] = state[1].wrapping_add(b);
    state[2] = state[2].wrapping_add(c);
    state[3] = state[3].wrapping_add(d);
    state[4] = state[4].wrapping_add(e);
    state[5] = state[5].wrapping_add(f);
    state[6] = state[6].wrapping_add(g);
    state[7] = state[7].wrapping_add(h);
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rf02c_history_sha256_known_vectors() {
        assert_eq!(
            hex_lower(&Sha256::new().finalize()),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        );
        let mut hasher = Sha256::new();
        hasher.update(b"a");
        hasher.update(b"bc");
        assert_eq!(
            hex_lower(&hasher.finalize()),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        );
    }

    #[test]
    fn rf02c_history_state_digest_uses_frozen_big_endian_component_bits() {
        let digest = StateDigest::from_state(&[0.0, -0.0, 1.0]);
        assert_eq!(
            digest.to_hex(),
            "234a0cc650b444c2a3945b4a093bb03089c31481a168167c31f9036cddd55fcd"
        );
        assert_ne!(
            StateDigest::from_state(&[-0.0, 0.0, 1.0]),
            StateDigest::from_state(&[0.0, -0.0, 1.0])
        );
        // Seven binary64 components occupy exactly 56 bytes, exercising the
        // two-block SHA-256 padding path used by the Type-IX state schema.
        assert_eq!(
            StateDigest::from_state(&[0.0; 7]).to_hex(),
            "d4817aa5497628e7c77e6b606107042bbba3130888c5f47a375e6179be789fbb"
        );
    }

    fn root_sample() -> GeometrySample {
        GeometrySample::new(
            0,
            0,
            BackgroundPhase::Expanding,
            SampleKind::EventRoot,
            3.5,
            vec![0.0, 1.0],
            0.5,
            Vec::new(),
            0.25,
            vec![NamedValue::new("H_bar", 0.0)],
            vec![NamedValue::new("H_bar", 1.0e-10)],
            Some(TypeIxDiagnostics {
                h_bar: 0.0,
                sigma2: 0.0,
                definition: 0.0,
                trace: 0.0,
            }),
        )
    }

    #[test]
    fn rf02c_history_freezes_tau_state_epsilon_and_margin_identity() {
        let mut history = GeometryHistory::new(
            "route",
            "native",
            "registry",
            "type_ix_d_future",
            BackgroundPhase::Expanding,
            BackgroundParameters {
                gamma: 1.0,
                kappa: 0.0,
            },
            SolverTolerances {
                rtol: 1.0e-10,
                atol: 1.0e-12,
            },
            vec!["H_bar".into(), "Sigma_p".into()],
        );
        let sample = root_sample();
        let tau_bits = sample.tau_bits;
        let state_sha256 = sample.state_sha256;
        history.append_sample(sample).unwrap();
        let epsilon_g = 1.01e-10;
        history
            .append_event(EventRecord {
                event_sequence: 0,
                event_id: TYPE_IX_RECOLLAPSE_EVENT.into(),
                margin_id: "H_bar".into(),
                root_multiplicity: 1,
                direction_class: RootDirectionClass::Decreasing,
                priority: 0,
                simultaneous_group: 0,
                sample_index: 0,
                tau_bits,
                epsilon_g,
                epsilon_g_bits: epsilon_g.to_bits(),
                raw_margin: 0.0,
                certificate_margin: 1.0e-10,
                segment_terminal: true,
                trajectory_terminal: false,
                transition_id: Some(TYPE_IX_PHASE_TRANSITION.into()),
            })
            .unwrap();
        history
            .append_transition(TransitionRecord {
                transition_sequence: 0,
                transition_id: TYPE_IX_PHASE_TRANSITION.into(),
                event_sequence: 0,
                sample_index: 0,
                tau_bits,
                from_chart: "type_ix_d_future".into(),
                from_phase: BackgroundPhase::Expanding,
                to_chart: "type_ix_d_future".into(),
                to_phase: BackgroundPhase::Contracting,
                state_map: IDENTITY_STATE_MAP.into(),
                state_bytes_preserved: true,
            })
            .unwrap();
        let latch = EventLatchRecord {
            event_id: TYPE_IX_RECOLLAPSE_EVENT.into(),
            margin_id: "H_bar".into(),
            direction: RootDirectionClass::Decreasing,
            epsilon_g,
            epsilon_g_bits: epsilon_g.to_bits(),
            root_tau_bits: tau_bits,
            root_state_sha256: state_sha256,
            allowed_rearm_side: AllowedRearmSide::Never,
            consumed: true,
        };
        latch
            .verify_restart(f64::from_bits(tau_bits), &[0.0, 1.0])
            .unwrap();
        assert_eq!(
            latch.verify_restart(f64::from_bits(tau_bits + 1), &[0.0, 1.0]),
            Err(FailureCode::RestartIdentityMismatch)
        );
        assert_eq!(
            latch.verify_restart(f64::from_bits(tau_bits), &[-0.0, 1.0]),
            Err(FailureCode::RestartIdentityMismatch)
        );
        assert_eq!(tau_bits_hex(tau_bits).len(), 16);
        assert_eq!(epsilon_bits_hex(epsilon_g.to_bits()).len(), 16);

        let requested = GeometrySample::new(
            1,
            1,
            BackgroundPhase::Contracting,
            SampleKind::Requested,
            4.0,
            vec![-0.1, 1.0],
            0.5,
            Vec::new(),
            0.25,
            vec![NamedValue::new("H_bar", -0.1)],
            vec![NamedValue::new("H_bar", -0.1 + 1.0e-10)],
            Some(TypeIxDiagnostics {
                h_bar: -0.1,
                sigma2: 0.0,
                definition: 0.0,
                trace: 0.0,
            }),
        );
        let requested_tau_bits = requested.tau_bits;
        history.append_sample(requested).unwrap();
        history
            .append_segment(SegmentRecord {
                segment_id: 0,
                chart: "type_ix_d_future".into(),
                phase: BackgroundPhase::Expanding,
                tau_start_bits: tau_bits,
                tau_end_bits: tau_bits,
                start_sample_index: 0,
                end_sample_index: 0,
                status: SegmentStatus::TransitionRequired,
            })
            .unwrap();
        history
            .append_segment(SegmentRecord {
                segment_id: 1,
                chart: "type_ix_d_future".into(),
                phase: BackgroundPhase::Contracting,
                tau_start_bits: tau_bits,
                tau_end_bits: requested_tau_bits,
                start_sample_index: 0,
                end_sample_index: 1,
                status: SegmentStatus::Completed,
            })
            .unwrap();
        assert_eq!(history.samples.len(), 2);
        assert_eq!(history.segments[1].start_sample_index, 0);
    }

    #[test]
    fn rf02c_history_rejects_nonidentity_or_misordered_transition() {
        let mut history = GeometryHistory::new(
            "route",
            "native",
            "registry",
            "type_ix_d_future",
            BackgroundPhase::Expanding,
            BackgroundParameters {
                gamma: 1.0,
                kappa: 0.0,
            },
            SolverTolerances {
                rtol: 1.0e-10,
                atol: 1.0e-12,
            },
            Vec::new(),
        );
        let sample = root_sample();
        let tau_bits = sample.tau_bits;
        history.append_sample(sample).unwrap();
        let epsilon_g = 1.0e-10;
        history
            .append_event(EventRecord {
                event_sequence: 0,
                event_id: TYPE_IX_RECOLLAPSE_EVENT.into(),
                margin_id: "H_bar".into(),
                root_multiplicity: 1,
                direction_class: RootDirectionClass::Decreasing,
                priority: 0,
                simultaneous_group: 0,
                sample_index: 0,
                tau_bits,
                epsilon_g,
                epsilon_g_bits: epsilon_g.to_bits(),
                raw_margin: 0.0,
                certificate_margin: 1.0e-10,
                segment_terminal: true,
                trajectory_terminal: false,
                transition_id: Some(TYPE_IX_PHASE_TRANSITION.into()),
            })
            .unwrap();
        let result = history.append_transition(TransitionRecord {
            transition_sequence: 0,
            transition_id: TYPE_IX_PHASE_TRANSITION.into(),
            event_sequence: 0,
            sample_index: 0,
            tau_bits,
            from_chart: "type_ix_d_future".into(),
            from_phase: BackgroundPhase::Expanding,
            to_chart: "type_ix_d_future".into(),
            to_phase: BackgroundPhase::Contracting,
            state_map: "reconstructed".into(),
            state_bytes_preserved: false,
        });
        assert_eq!(result, Err(HistoryInvariantError::UnsupportedTransition));
    }
}
