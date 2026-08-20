//! Adaptive truncated Krylov exponential/phi-action backend.
//! The residual controller uses a projected residual heuristic. `tol` is a requested
//! initial-state-scaled target, not a rigorous bound for arbitrary nonnormal semigroups.
//! Every successful action records its residual-target semantics in the returned stats;
//! no success variant in this module certifies total forward error.

use nalgebra::DMatrix;

const ACCEPT_DELTA: f64 = 1.0;
const GAMMA_REJECT: f64 = 0.6;
const GAMMA_ACCEPT: f64 = 0.9;
const KAPPA: f64 = 2.0;
const GLOBAL_TOL_SAFETY: f64 = 0.1;
const HYSTERESIS_CLEAN_ACCEPTS: usize = 3;
const HYSTERESIS_CLEAN_RATIO: f64 = GAMMA_ACCEPT;
// Conservative binary64 request floor. This rejects targets that are plainly
// below scalar arithmetic resolution without pretending to bound accumulated
// basis, Padé, or forward error.
const ARITHMETIC_TOLERANCE_FACTOR: f64 = 32.0;
// Repeated squaring amplifies roundoff exponentially; attempts requiring more
// work are rejected so the outer controller can reduce tau within its budgets.
const MAX_PADE_SQUARINGS: u32 = 64;

#[derive(Clone, Copy, Debug)]
pub struct AdaptiveKrylovOptions {
    pub m_init: usize,
    pub m_min: usize,
    pub m_max: usize,
    pub tol: f64,
    pub max_substeps: usize,
    pub max_rejects: usize,
}

/// Machine-readable meaning of a successful residual-controller action.
/// Neither variant is a forward-error certificate.
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub enum AdaptiveKrylovTargetSemantics {
    /// The requested target controls only the projected residual estimate.
    #[default]
    ResidualEstimateOnly,
    /// A caller-supplied heuristic divisor tightened the residual budget.
    /// The divisor has no operator-bound or forward-error semantics.
    CallerDividedResidualEstimate { divisor: f64 },
    /// An aggregate combines working actions with different residual semantics.
    MixedResidualEstimates,
}

#[derive(Clone, Debug, Default)]
pub struct AdaptiveKrylovStats {
    pub accepted_steps: usize,
    pub rejected_steps: usize,
    /// Reduced Ritz/Padé attempts that were nonfinite or numerically unusable.
    pub nonfinite_rejections: usize,
    pub matvecs: usize,
    pub projected_exponentials: usize,
    pub max_basis: usize,
    pub final_basis: usize,
    /// Compatibility alias of `max_attempt_error_ratio`.
    pub max_error_ratio: f64,
    /// Maximum finite attempted error ratio. Nonfinite attempts are counted separately.
    pub max_attempt_error_ratio: f64,
    pub max_accepted_error_ratio: f64,
    pub last_accepted_error_ratio: f64,
    pub projection_builds: usize,
    pub projection_reuses: usize,
    pub basis_extensions: usize,
    pub basis_extension_columns: usize,
    pub tau_reductions: usize,
    pub tau_recoveries: usize,
    pub rejection_episodes: usize,
    pub max_rejection_streak: usize,
    pub hysteresis_accepts: usize,
    pub basis_shrink_deferrals: usize,
    pub basis_shrinks: usize,
    pub joint_tau_growth_basis_shrinks: usize,
    pub minimum_clean_accepts_before_basis_shrink: usize,
    /// One-based projected-attempt ordinal, or zero when the event did not occur.
    pub first_basis_extension_attempt: usize,
    /// One-based projected-attempt ordinal, or zero when the event did not occur.
    pub first_tau_reduction_attempt: usize,
    pub iop2_columns: usize,
    pub full_mgs_columns: usize,
    pub full_mgs_passes: usize,
    pub selective_reorthogonalizations: usize,
    /// Maximum defect against the full attained basis, including IOP(2) columns.
    pub max_iop2_orthogonality_defect: f64,
    pub max_full_mgs_orthogonality_defect: f64,
    pub target_semantics: AdaptiveKrylovTargetSemantics,
}

impl AdaptiveKrylovStats {
    /// Merge a later action ledger without erasing the last accepted state when
    /// that later action accepted no steps.
    pub fn accumulate(&mut self, src: &Self) {
        let destination_had_work = self.has_work();
        let source_has_work = src.has_work();
        if source_has_work {
            if !destination_had_work {
                self.target_semantics = src.target_semantics;
            } else if self.target_semantics != src.target_semantics {
                self.target_semantics = AdaptiveKrylovTargetSemantics::MixedResidualEstimates;
            }
        }
        let attempt_offset = self.projected_exponentials;
        if self.first_basis_extension_attempt == 0 && src.first_basis_extension_attempt > 0 {
            self.first_basis_extension_attempt = attempt_offset + src.first_basis_extension_attempt;
        }
        if self.first_tau_reduction_attempt == 0 && src.first_tau_reduction_attempt > 0 {
            self.first_tau_reduction_attempt = attempt_offset + src.first_tau_reduction_attempt;
        }
        self.accepted_steps += src.accepted_steps;
        self.rejected_steps += src.rejected_steps;
        self.nonfinite_rejections += src.nonfinite_rejections;
        self.matvecs += src.matvecs;
        self.projected_exponentials += src.projected_exponentials;
        self.max_basis = self.max_basis.max(src.max_basis);
        self.max_attempt_error_ratio = self
            .max_attempt_error_ratio
            .max(src.max_attempt_error_ratio);
        self.max_accepted_error_ratio = self
            .max_accepted_error_ratio
            .max(src.max_accepted_error_ratio);
        self.projection_builds += src.projection_builds;
        self.projection_reuses += src.projection_reuses;
        self.basis_extensions += src.basis_extensions;
        self.basis_extension_columns += src.basis_extension_columns;
        self.tau_reductions += src.tau_reductions;
        self.tau_recoveries += src.tau_recoveries;
        self.rejection_episodes += src.rejection_episodes;
        self.max_rejection_streak = self.max_rejection_streak.max(src.max_rejection_streak);
        self.hysteresis_accepts += src.hysteresis_accepts;
        self.basis_shrink_deferrals += src.basis_shrink_deferrals;
        self.basis_shrinks += src.basis_shrinks;
        self.joint_tau_growth_basis_shrinks += src.joint_tau_growth_basis_shrinks;
        if src.minimum_clean_accepts_before_basis_shrink > 0
            && (self.minimum_clean_accepts_before_basis_shrink == 0
                || src.minimum_clean_accepts_before_basis_shrink
                    < self.minimum_clean_accepts_before_basis_shrink)
        {
            self.minimum_clean_accepts_before_basis_shrink =
                src.minimum_clean_accepts_before_basis_shrink;
        }
        self.iop2_columns += src.iop2_columns;
        self.full_mgs_columns += src.full_mgs_columns;
        self.full_mgs_passes += src.full_mgs_passes;
        self.selective_reorthogonalizations += src.selective_reorthogonalizations;
        self.max_iop2_orthogonality_defect = self
            .max_iop2_orthogonality_defect
            .max(src.max_iop2_orthogonality_defect);
        self.max_full_mgs_orthogonality_defect = self
            .max_full_mgs_orthogonality_defect
            .max(src.max_full_mgs_orthogonality_defect);
        if src.accepted_steps > 0 {
            self.final_basis = src.final_basis;
            self.last_accepted_error_ratio = src.last_accepted_error_ratio;
        }
        self.max_error_ratio = self.max_attempt_error_ratio;
    }

    fn has_work(&self) -> bool {
        self.accepted_steps > 0
            || self.rejected_steps > 0
            || self.matvecs > 0
            || self.projected_exponentials > 0
            || self.max_basis > 0
    }
}

#[derive(Debug, Clone)]
pub enum AdaptiveKrylovError {
    InvalidOptions,
    InvalidResidualBudgetDivisor {
        requested: f64,
    },
    ToleranceBelowArithmeticFloor {
        requested: f64,
        floor: f64,
    },
    InvalidKatoDomain {
        field: &'static str,
    },
    NonFiniteTime,
    InputNotFinite,
    OperatorDimensionMismatch {
        stats: AdaptiveKrylovStats,
    },
    OperatorReturnedNonFinite {
        stats: AdaptiveKrylovStats,
    },
    ProjectionArithmeticNonFinite {
        stats: AdaptiveKrylovStats,
    },
    SingularPadeSolve,
    DidNotConverge {
        error_ratio: f64,
        stats: AdaptiveKrylovStats,
    },
    KatoSubactionFailed {
        source: Box<AdaptiveKrylovError>,
        stats: AdaptiveKrylovStats,
    },
}

impl AdaptiveKrylovError {
    pub fn stats(&self) -> Option<&AdaptiveKrylovStats> {
        match self {
            Self::OperatorDimensionMismatch { stats }
            | Self::OperatorReturnedNonFinite { stats }
            | Self::ProjectionArithmeticNonFinite { stats }
            | Self::DidNotConverge { stats, .. }
            | Self::KatoSubactionFailed { stats, .. } => Some(stats),
            _ => None,
        }
    }

    fn with_prior_stats(self, prior: &AdaptiveKrylovStats) -> Self {
        if !prior.has_work() {
            return self;
        }
        let mut merged = prior.clone();
        if let Some(local) = self.stats() {
            merged.accumulate(local);
        }
        Self::KatoSubactionFailed {
            source: Box::new(self),
            stats: merged,
        }
    }
}

fn stable_norm2(values: &[f64]) -> Option<f64> {
    let mut scale = 0.0;
    let mut sum_squares = 1.0;
    for &value in values {
        if !value.is_finite() {
            return None;
        }
        let magnitude = value.abs();
        if magnitude == 0.0 {
            continue;
        }
        if scale < magnitude {
            let ratio = scale / magnitude;
            sum_squares = 1.0 + sum_squares * ratio * ratio;
            scale = magnitude;
        } else {
            let ratio = magnitude / scale;
            sum_squares += ratio * ratio;
        }
    }
    if scale == 0.0 {
        return Some(0.0);
    }
    let norm = scale * sum_squares.sqrt();
    norm.is_finite().then_some(norm)
}

fn checked_dot(a: &[f64], b: &[f64]) -> Option<f64> {
    let mut sum = 0.0;
    let mut correction = 0.0;
    for (&x, &y) in a.iter().zip(b) {
        let term = x * y;
        if !term.is_finite() {
            return None;
        }
        let next = sum + term;
        if !next.is_finite() {
            return None;
        }
        let increment = if sum.abs() >= term.abs() {
            (sum - next) + term
        } else {
            (term - next) + sum
        };
        correction += increment;
        if !correction.is_finite() {
            return None;
        }
        sum = next;
    }
    let result = sum + correction;
    result.is_finite().then_some(result)
}

fn matrix_is_finite(matrix: &DMatrix<f64>) -> bool {
    matrix.iter().all(|value| value.is_finite())
}

fn checked_matrix_one_norm(matrix: &DMatrix<f64>) -> Option<f64> {
    let mut result: f64 = 0.0;
    for j in 0..matrix.ncols() {
        let mut sum = 0.0;
        for i in 0..matrix.nrows() {
            sum += matrix[(i, j)].abs();
            if !sum.is_finite() {
                return None;
            }
        }
        result = result.max(sum);
    }
    Some(result)
}

fn expm_pade13(matrix: &DMatrix<f64>) -> Result<DMatrix<f64>, ()> {
    if matrix.nrows() != matrix.ncols() || !matrix_is_finite(matrix) {
        return Err(());
    }
    let n = matrix.nrows();
    if n == 0 {
        return Ok(DMatrix::zeros(0, 0));
    }
    let theta13 = 5.371_920_351_148_152_f64;
    let norm = checked_matrix_one_norm(matrix).ok_or(())?;
    let squarings = if norm <= theta13 || norm == 0.0 {
        0
    } else {
        let estimate = (norm / theta13).log2().ceil().max(0.0);
        if !estimate.is_finite() || estimate > f64::from(MAX_PADE_SQUARINGS) {
            return Err(());
        }
        estimate as u32
    };
    let scale = 2_f64.powi(-(squarings as i32));
    if !(scale > 0.0 && scale.is_finite()) {
        return Err(());
    }
    let a = matrix * scale;
    if !matrix_is_finite(&a) {
        return Err(());
    }
    let eye = DMatrix::<f64>::identity(n, n);
    let a2 = &a * &a;
    let a4 = &a2 * &a2;
    let a6 = &a4 * &a2;
    if !matrix_is_finite(&a2) || !matrix_is_finite(&a4) || !matrix_is_finite(&a6) {
        return Err(());
    }
    let b = [
        64_764_752_532_480_000.0,
        32_382_376_266_240_000.0,
        7_771_770_303_897_600.0,
        1_187_353_796_428_800.0,
        129_060_195_264_000.0,
        10_559_470_521_600.0,
        670_442_572_800.0,
        33_522_128_640.0,
        1_323_241_920.0,
        40_840_800.0,
        960_960.0,
        16_380.0,
        182.0,
        1.0,
    ];
    let u_inner = &a6 * (&a6 * b[13] + &a4 * b[11] + &a2 * b[9])
        + &a6 * b[7]
        + &a4 * b[5]
        + &a2 * b[3]
        + &eye * b[1];
    let u = &a * &u_inner;
    let v = &a6 * (&a6 * b[12] + &a4 * b[10] + &a2 * b[8])
        + &a6 * b[6]
        + &a4 * b[4]
        + &a2 * b[2]
        + &eye * b[0];
    if !matrix_is_finite(&u_inner) || !matrix_is_finite(&u) || !matrix_is_finite(&v) {
        return Err(());
    }
    let p = &v + &u;
    let q = &v - &u;
    if !matrix_is_finite(&p) || !matrix_is_finite(&q) {
        return Err(());
    }
    let mut result = q.lu().solve(&p).ok_or(())?;
    if !matrix_is_finite(&result) {
        return Err(());
    }
    for _ in 0..squarings {
        result = &result * &result;
        if !matrix_is_finite(&result) {
            return Err(());
        }
    }
    Ok(result)
}

struct Projection {
    basis: Vec<Vec<f64>>,
    h: DMatrix<f64>,
    k: usize,
    beta: f64,
    residual_h: f64,
    happy_breakdown: bool,
}

#[derive(Clone, Copy)]
enum ProjectionFailure {
    DimensionMismatch,
    OperatorNonFinite,
    ArithmeticNonFinite,
}

impl ProjectionFailure {
    fn into_error(self, stats: AdaptiveKrylovStats) -> AdaptiveKrylovError {
        match self {
            Self::DimensionMismatch => AdaptiveKrylovError::OperatorDimensionMismatch { stats },
            Self::OperatorNonFinite => AdaptiveKrylovError::OperatorReturnedNonFinite { stats },
            Self::ArithmeticNonFinite => {
                AdaptiveKrylovError::ProjectionArithmeticNonFinite { stats }
            }
        }
    }
}

fn new_projection(y: &[f64], capacity: usize) -> Result<Projection, ProjectionFailure> {
    let beta = stable_norm2(y).ok_or(ProjectionFailure::ArithmeticNonFinite)?;
    if y.is_empty() || beta == 0.0 {
        return Ok(Projection {
            basis: Vec::new(),
            h: DMatrix::zeros(0, 0),
            k: 0,
            beta,
            residual_h: 0.0,
            happy_breakdown: true,
        });
    }
    let capacity = capacity.min(y.len()).max(1);
    let first: Vec<f64> = y.iter().map(|value| value / beta).collect();
    if !first.iter().all(|value| value.is_finite()) {
        return Err(ProjectionFailure::ArithmeticNonFinite);
    }
    Ok(Projection {
        basis: vec![first],
        h: DMatrix::zeros(capacity + 1, capacity),
        k: 0,
        beta,
        residual_h: 0.0,
        happy_breakdown: false,
    })
}

fn extend_projection<F>(
    apply: &F,
    projection: &mut Projection,
    target_m: usize,
    stats: &mut AdaptiveKrylovStats,
) -> Result<(), ProjectionFailure>
where
    F: Fn(&[f64]) -> Vec<f64>,
{
    if projection.happy_breakdown || projection.k >= target_m {
        return Ok(());
    }
    let n = projection.basis[0].len();
    let target_m = target_m.min(projection.h.ncols());
    while projection.k < target_m && !projection.happy_breakdown {
        let j = projection.k;
        let mut w = apply(&projection.basis[j]);
        stats.matvecs += 1;
        if w.len() != n {
            return Err(ProjectionFailure::DimensionMismatch);
        }
        if !w.iter().all(|value| value.is_finite()) {
            return Err(ProjectionFailure::OperatorNonFinite);
        }
        let pre_norm = stable_norm2(&w).ok_or(ProjectionFailure::ArithmeticNonFinite)?;
        let full_mgs = projection.h.ncols() >= n;
        let first_index = if full_mgs { 0 } else { j.saturating_sub(1) };
        let passes = if full_mgs { 2 } else { 1 };
        if full_mgs {
            stats.full_mgs_columns += 1;
            stats.full_mgs_passes += passes;
        } else {
            stats.iop2_columns += 1;
        }
        for _ in 0..passes {
            for i in first_index..=j {
                let hij = checked_dot(&projection.basis[i], &w)
                    .ok_or(ProjectionFailure::ArithmeticNonFinite)?;
                let updated_h = projection.h[(i, j)] + hij;
                if !updated_h.is_finite() {
                    return Err(ProjectionFailure::ArithmeticNonFinite);
                }
                projection.h[(i, j)] = updated_h;
                for r in 0..n {
                    w[r] -= hij * projection.basis[i][r];
                    if !w[r].is_finite() {
                        return Err(ProjectionFailure::ArithmeticNonFinite);
                    }
                }
            }
        }
        let after_local = stable_norm2(&w).ok_or(ProjectionFailure::ArithmeticNonFinite)?;
        if !full_mgs && after_local < 0.5 * pre_norm {
            stats.selective_reorthogonalizations += 1;
            for i in 0..=j {
                let hij = checked_dot(&projection.basis[i], &w)
                    .ok_or(ProjectionFailure::ArithmeticNonFinite)?;
                let updated_h = projection.h[(i, j)] + hij;
                if !updated_h.is_finite() {
                    return Err(ProjectionFailure::ArithmeticNonFinite);
                }
                projection.h[(i, j)] = updated_h;
                for r in 0..n {
                    w[r] -= hij * projection.basis[i][r];
                    if !w[r].is_finite() {
                        return Err(ProjectionFailure::ArithmeticNonFinite);
                    }
                }
            }
        }
        let hn = stable_norm2(&w).ok_or(ProjectionFailure::ArithmeticNonFinite)?;
        projection.h[(j + 1, j)] = hn;
        projection.k = j + 1;
        stats.max_basis = stats.max_basis.max(projection.k);
        projection.residual_h = hn;
        if hn == 0.0 {
            projection.happy_breakdown = true;
            projection.residual_h = 0.0;
            continue;
        }
        // At full capacity there is no later column to extend, and in an
        // n-dimensional full-MGS lane a normalized (n+1)th residual would be
        // roundoff amplified rather than an attained basis vector.
        if projection.k >= projection.h.ncols() {
            continue;
        }
        let next: Vec<f64> = w.into_iter().map(|value| value / hn).collect();
        if !next.iter().all(|value| value.is_finite()) {
            return Err(ProjectionFailure::ArithmeticNonFinite);
        }
        let mut defect: f64 = 0.0;
        // IOP(2) still orthogonalizes only against the two most recent vectors;
        // telemetry measures the result against every attained basis vector.
        for basis in &projection.basis[..=j] {
            defect = defect.max(
                checked_dot(basis, &next)
                    .ok_or(ProjectionFailure::ArithmeticNonFinite)?
                    .abs(),
            );
        }
        if full_mgs {
            stats.max_full_mgs_orthogonality_defect =
                stats.max_full_mgs_orthogonality_defect.max(defect);
        } else {
            stats.max_iop2_orthogonality_defect = stats.max_iop2_orthogonality_defect.max(defect);
        }
        projection.basis.push(next);
    }
    Ok(())
}

fn projected_candidate(projection: &Projection, t: f64, n: usize) -> Result<(Vec<f64>, f64), ()> {
    if projection.k == 0 {
        return Ok((vec![0.0; n], 0.0));
    }
    let hm = projection
        .h
        .view((0, 0), (projection.k, projection.k))
        .into_owned();
    if !matrix_is_finite(&hm) {
        return Err(());
    }
    let mut augmented = DMatrix::<f64>::zeros(projection.k + 1, projection.k + 1);
    for i in 0..projection.k {
        for j in 0..projection.k {
            augmented[(i, j)] = t * hm[(i, j)];
        }
    }
    // Keep the augmentation column dimensionless. Scaling the entire block by
    // a large |t| leaves the wanted first column unchanged in exact arithmetic,
    // but makes an irrelevant off-diagonal entry dominate Padé scaling.
    augmented[(0, projection.k)] = 1.0;
    if !matrix_is_finite(&augmented) {
        return Err(());
    }
    let exponential = expm_pade13(&augmented)?;
    let mut out = vec![0.0; n];
    for i in 0..projection.k {
        let coefficient = projection.beta * exponential[(i, 0)];
        if !coefficient.is_finite() {
            return Err(());
        }
        for r in 0..n {
            let term = coefficient * projection.basis[i][r];
            if !term.is_finite() {
                return Err(());
            }
            out[r] += term;
            if !out[r].is_finite() {
                return Err(());
            }
        }
    }
    let estimate = if projection.happy_breakdown || projection.residual_h == 0.0 {
        0.0
    } else {
        projection.beta
            * projection.residual_h.abs()
            * t.abs()
            * exponential[(projection.k - 1, projection.k)].abs()
    };
    if !estimate.is_finite() {
        return Err(());
    }
    Ok((out, estimate))
}

fn validate_options(options: AdaptiveKrylovOptions) -> Result<(), AdaptiveKrylovError> {
    if options.m_min < 2
        || options.m_init < options.m_min
        || options.m_init > options.m_max
        || options.m_max < options.m_min
        || !(options.tol > 0.0 && options.tol.is_finite())
        || options.max_substeps == 0
        || options.max_rejects == 0
    {
        return Err(AdaptiveKrylovError::InvalidOptions);
    }
    Ok(())
}

fn validate_public_input(
    values: &[f64],
    t: f64,
    options: AdaptiveKrylovOptions,
    target_semantics: AdaptiveKrylovTargetSemantics,
) -> Result<f64, AdaptiveKrylovError> {
    validate_options(options)?;
    let arithmetic_floor = ARITHMETIC_TOLERANCE_FACTOR * f64::EPSILON;
    if options.tol < arithmetic_floor {
        return Err(AdaptiveKrylovError::ToleranceBelowArithmeticFloor {
            requested: options.tol,
            floor: arithmetic_floor,
        });
    }
    if !t.is_finite() {
        return Err(AdaptiveKrylovError::NonFiniteTime);
    }
    if !values.iter().all(|value| value.is_finite()) {
        return Err(AdaptiveKrylovError::InputNotFinite);
    }
    stable_norm2(values).ok_or_else(|| AdaptiveKrylovError::ProjectionArithmeticNonFinite {
        stats: AdaptiveKrylovStats {
            target_semantics,
            ..AdaptiveKrylovStats::default()
        },
    })
}

fn clipped_basis(m: usize, proposed: isize, options: AdaptiveKrylovOptions) -> usize {
    let low = ((3 * m) / 4).max(options.m_min);
    let high = ((4 * m + 2) / 3).min(options.m_max);
    (proposed.max(low as isize) as usize)
        .min(high)
        .clamp(options.m_min, options.m_max)
}

fn convergence_error(stats: AdaptiveKrylovStats, error_ratio: f64) -> AdaptiveKrylovError {
    AdaptiveKrylovError::DidNotConverge { error_ratio, stats }
}

pub fn adaptive_expm_action<F>(
    apply: &F,
    y: &[f64],
    t: f64,
    options: AdaptiveKrylovOptions,
) -> Result<(Vec<f64>, AdaptiveKrylovStats), AdaptiveKrylovError>
where
    F: Fn(&[f64]) -> Vec<f64>,
{
    adaptive_expm_action_impl(
        apply,
        y,
        t,
        options,
        1.0,
        AdaptiveKrylovTargetSemantics::ResidualEstimateOnly,
    )
}

/// Runs the same residual controller after dividing its residual budget by a
/// caller-supplied heuristic divisor. The divisor is only a budget-allocation
/// input: it is not validated against `apply` and does not certify forward error,
/// even when the caller obtained it from an independent semigroup bound.
pub fn adaptive_expm_action_with_residual_budget_divisor<F>(
    apply: &F,
    y: &[f64],
    t: f64,
    options: AdaptiveKrylovOptions,
    residual_budget_divisor: f64,
) -> Result<(Vec<f64>, AdaptiveKrylovStats), AdaptiveKrylovError>
where
    F: Fn(&[f64]) -> Vec<f64>,
{
    if !(residual_budget_divisor >= 1.0 && residual_budget_divisor.is_finite()) {
        return Err(AdaptiveKrylovError::InvalidResidualBudgetDivisor {
            requested: residual_budget_divisor,
        });
    }
    adaptive_expm_action_impl(
        apply,
        y,
        t,
        options,
        residual_budget_divisor,
        AdaptiveKrylovTargetSemantics::CallerDividedResidualEstimate {
            divisor: residual_budget_divisor,
        },
    )
}

fn adaptive_expm_action_impl<F>(
    apply: &F,
    y: &[f64],
    t: f64,
    options: AdaptiveKrylovOptions,
    residual_budget_divisor: f64,
    target_semantics: AdaptiveKrylovTargetSemantics,
) -> Result<(Vec<f64>, AdaptiveKrylovStats), AdaptiveKrylovError>
where
    F: Fn(&[f64]) -> Vec<f64>,
{
    let initial_norm = validate_public_input(y, t, options, target_semantics)?;
    let initial_stats = AdaptiveKrylovStats {
        target_semantics,
        ..AdaptiveKrylovStats::default()
    };
    if t == 0.0 || y.is_empty() || initial_norm == 0.0 {
        return Ok((y.to_vec(), initial_stats));
    }
    let total = t.abs();
    let sign = t.signum();
    let initial_scale = initial_norm.max(1.0);
    let tolerance = options.tol * GLOBAL_TOL_SAFETY * initial_scale / residual_budget_divisor;
    if !(tolerance > 0.0 && tolerance.is_finite()) {
        return Err(AdaptiveKrylovError::ProjectionArithmeticNonFinite {
            stats: initial_stats,
        });
    }
    let mut remaining = total;
    let mut tau = total;
    let capacity = options.m_max.min(y.len()).max(1);
    let mut m = options
        .m_init
        .min(capacity)
        .max(options.m_min.min(capacity));
    let mut state = y.to_vec();
    let mut stats = initial_stats;
    let mut last_error_ratio = f64::INFINITY;
    let mut recovery_basis_floor = 0usize;
    let mut clean_accept_streak = 0usize;
    while remaining > 0.0 {
        if stats.accepted_steps >= options.max_substeps {
            return Err(convergence_error(stats, last_error_ratio));
        }
        tau = tau.min(remaining);
        if !(tau > 0.0 && tau.is_finite()) {
            return Err(convergence_error(stats, last_error_ratio));
        }
        let mut projection = match new_projection(&state, capacity) {
            Ok(projection) => projection,
            Err(error) => return Err(error.into_error(stats)),
        };
        stats.projection_builds += 1;
        if let Err(error) = extend_projection(apply, &mut projection, m, &mut stats) {
            return Err(error.into_error(stats));
        }
        stats.max_basis = stats.max_basis.max(projection.k);
        let mut attempt_in_projection = 0usize;
        let mut rejected_current_state = false;
        let mut rejection_streak = 0usize;

        loop {
            if stats.rejected_steps >= options.max_rejects {
                return Err(convergence_error(stats, last_error_ratio));
            }
            attempt_in_projection += 1;
            if attempt_in_projection > 1 {
                stats.projection_reuses += 1;
            }
            stats.projected_exponentials += 1;
            let candidate_result = projected_candidate(&projection, sign * tau, state.len());
            let (candidate, estimate, reduced_nonfinite) = match candidate_result {
                Ok((candidate, estimate)) => (candidate, estimate, false),
                Err(()) => (Vec::new(), f64::INFINITY, true),
            };
            let error_ratio = if reduced_nonfinite {
                f64::INFINITY
            } else if estimate == 0.0 {
                0.0
            } else {
                (estimate / tolerance) * (total / tau)
            };
            last_error_ratio = error_ratio;
            if error_ratio.is_finite() {
                stats.max_attempt_error_ratio = stats.max_attempt_error_ratio.max(error_ratio);
                stats.max_error_ratio = stats.max_attempt_error_ratio;
            }

            if error_ratio.is_finite() && error_ratio <= ACCEPT_DELTA {
                let next_remaining = remaining - tau;
                if !(next_remaining.is_finite() && next_remaining < remaining) {
                    return Err(convergence_error(stats, error_ratio));
                }
                state = candidate;
                remaining = next_remaining.max(0.0);
                stats.accepted_steps += 1;
                stats.final_basis = projection.k;
                stats.max_accepted_error_ratio = stats.max_accepted_error_ratio.max(error_ratio);
                stats.last_accepted_error_ratio = error_ratio;

                let clean_accept = !rejected_current_state && error_ratio <= HYSTERESIS_CLEAN_RATIO;
                if clean_accept {
                    clean_accept_streak += 1;
                } else {
                    clean_accept_streak = 0;
                }
                let safe_error_ratio = error_ratio.max(1e-16);
                let proposed = m as f64 + (safe_error_ratio / GAMMA_ACCEPT).ln() / KAPPA.ln();
                let candidate_m = clipped_basis(m, proposed.ceil() as isize, options).min(capacity);
                let old_m = m;
                let mut next_m = candidate_m;
                let q = ((projection.k as f64) / 4.0 - 1.0).max(1.0);
                let mut tau_factor = if error_ratio == 0.0 {
                    5.0
                } else {
                    (GAMMA_ACCEPT / error_ratio)
                        .powf(1.0 / (q + 1.0))
                        .clamp(0.5, 5.0)
                };
                // Unbounded five-fold accepted-step growth recreates a
                // reject/accept saw-tooth even when the basis is retained.
                tau_factor = tau_factor.min(1.5);

                if recovery_basis_floor > 0 {
                    stats.hysteresis_accepts += 1;
                    if next_m < recovery_basis_floor {
                        stats.basis_shrink_deferrals += 1;
                    }
                    next_m = next_m.max(recovery_basis_floor).min(capacity);
                    // The acceptance that closes a rejection episode holds tau;
                    // subsequent clean recovery accepts grow it only gently.
                    tau_factor = if rejected_current_state {
                        tau_factor.min(1.0)
                    } else {
                        tau_factor.min(1.1)
                    };
                    if clean_accept && clean_accept_streak >= HYSTERESIS_CLEAN_ACCEPTS {
                        recovery_basis_floor = 0;
                        clean_accept_streak = 0;
                        tau_factor = tau_factor.min(1.0);
                    }
                } else if next_m < old_m {
                    if clean_accept_streak >= HYSTERESIS_CLEAN_ACCEPTS {
                        stats.basis_shrinks += 1;
                        if stats.minimum_clean_accepts_before_basis_shrink == 0 {
                            stats.minimum_clean_accepts_before_basis_shrink = clean_accept_streak;
                        } else {
                            stats.minimum_clean_accepts_before_basis_shrink = stats
                                .minimum_clean_accepts_before_basis_shrink
                                .min(clean_accept_streak);
                        }
                        tau_factor = tau_factor.min(1.0);
                        clean_accept_streak = 0;
                    } else {
                        stats.basis_shrink_deferrals += 1;
                        next_m = old_m;
                    }
                }
                if next_m < old_m && tau_factor > 1.0 + 16.0 * f64::EPSILON {
                    stats.joint_tau_growth_basis_shrinks += 1;
                }
                m = next_m;
                if remaining > 0.0 {
                    let next_tau = (tau * tau_factor).min(remaining);
                    if next_tau > tau * (1.0 + 16.0 * f64::EPSILON) {
                        stats.tau_recoveries += 1;
                    }
                    tau = next_tau;
                }
                break;
            }

            stats.rejected_steps += 1;
            rejection_streak += 1;
            if rejection_streak == 1 {
                stats.rejection_episodes += 1;
            }
            stats.max_rejection_streak = stats.max_rejection_streak.max(rejection_streak);
            rejected_current_state = true;
            clean_accept_streak = 0;
            if !error_ratio.is_finite() {
                stats.nonfinite_rejections += 1;
            }
            if m < capacity {
                if stats.first_basis_extension_attempt == 0 {
                    stats.first_basis_extension_attempt = stats.projected_exponentials;
                }
                stats.basis_extensions += 1;
                let new_m = if error_ratio.is_finite() {
                    let proposed = m as f64 + (error_ratio / GAMMA_ACCEPT).ln() / KAPPA.ln();
                    let grown = clipped_basis(m, proposed.ceil() as isize, options);
                    grown.max((m + 1).min(capacity)).min(capacity)
                } else {
                    ((4 * m + 2) / 3).max(m + 1).min(capacity)
                };
                let old_k = projection.k;
                let extension = extend_projection(apply, &mut projection, new_m, &mut stats);
                stats.basis_extension_columns += projection.k.saturating_sub(old_k);
                if let Err(error) = extension {
                    return Err(error.into_error(stats));
                }
                m = new_m;
                stats.max_basis = stats.max_basis.max(projection.k);
                recovery_basis_floor = recovery_basis_floor.max(projection.k);
            } else {
                if stats.first_tau_reduction_attempt == 0 {
                    stats.first_tau_reduction_attempt = stats.projected_exponentials;
                }
                stats.tau_reductions += 1;
                recovery_basis_floor = recovery_basis_floor.max(projection.k);
                let q = ((m as f64) / 4.0 - 1.0).max(1.0);
                let factor = if error_ratio.is_finite() {
                    (GAMMA_REJECT / error_ratio)
                        .powf(1.0 / (q + 1.0))
                        .clamp(0.2, 0.9)
                } else {
                    0.2
                };
                let new_tau = (tau * factor).min(remaining);
                if !(new_tau > 0.0 && new_tau.is_finite() && new_tau < tau) {
                    return Err(convergence_error(stats, error_ratio));
                }
                tau = new_tau;
            }
        }
    }
    Ok((state, stats))
}

fn augmented_options(options: AdaptiveKrylovOptions, dimension: usize) -> AdaptiveKrylovOptions {
    let mut result = options;
    result.m_max = result.m_max.min(dimension);
    result.m_init = result.m_init.min(result.m_max);
    result.m_min = result.m_min.min(result.m_init);
    result
}

/// Directly controls and returns `phi1(tA)b` using `[[tA,b/s],[0,0]]`
/// at unit time, with `s=max(||b||_2,1)` as the controller scale.
pub fn adaptive_phi1_action<F>(
    apply: &F,
    b: &[f64],
    t: f64,
    options: AdaptiveKrylovOptions,
) -> Result<(Vec<f64>, AdaptiveKrylovStats), AdaptiveKrylovError>
where
    F: Fn(&[f64]) -> Vec<f64>,
{
    let b_norm = validate_public_input(
        b,
        t,
        options,
        AdaptiveKrylovTargetSemantics::ResidualEstimateOnly,
    )?;
    if b.is_empty() {
        return Ok((Vec::new(), AdaptiveKrylovStats::default()));
    }
    if t == 0.0 || b_norm == 0.0 {
        return Ok((b.to_vec(), AdaptiveKrylovStats::default()));
    }
    let n = b.len();
    let scale = b_norm.max(1.0);
    let coupling: Vec<f64> = b.iter().map(|value| value / scale).collect();
    let arithmetic_failed = std::cell::Cell::new(false);
    let augmented_apply = |z: &[f64]| -> Vec<f64> {
        if z.len() != n + 1 {
            return Vec::new();
        }
        let raw = apply(&z[..n]);
        if raw.len() != n {
            return Vec::new();
        }
        if !raw.iter().all(|value| value.is_finite()) {
            let mut out = raw;
            out.push(0.0);
            return out;
        }
        let bottom = z[n];
        let mut out = Vec::with_capacity(n + 1);
        for i in 0..n {
            let value = t * raw[i] + coupling[i] * bottom;
            if !value.is_finite() {
                arithmetic_failed.set(true);
            }
            out.push(value);
        }
        out.push(0.0);
        out
    };
    let mut initial = vec![0.0; n + 1];
    initial[n] = scale;
    let result = adaptive_expm_action(
        &augmented_apply,
        &initial,
        1.0,
        augmented_options(options, n + 1),
    );
    match result {
        Ok((z, stats)) => Ok((z[..n].to_vec(), stats)),
        Err(AdaptiveKrylovError::OperatorReturnedNonFinite { stats })
            if arithmetic_failed.get() =>
        {
            Err(AdaptiveKrylovError::ProjectionArithmeticNonFinite { stats })
        }
        Err(error) => Err(error),
    }
}

/// Directly controls and returns `t*phi1(tA)b` using `[[A,b/s],[0,0]]`
/// at time `t`, with `s=max(||b||_2,1)` as the controller scale.
pub fn adaptive_t_phi1_action<F>(
    apply: &F,
    b: &[f64],
    t: f64,
    options: AdaptiveKrylovOptions,
) -> Result<(Vec<f64>, AdaptiveKrylovStats), AdaptiveKrylovError>
where
    F: Fn(&[f64]) -> Vec<f64>,
{
    let b_norm = validate_public_input(
        b,
        t,
        options,
        AdaptiveKrylovTargetSemantics::ResidualEstimateOnly,
    )?;
    if b.is_empty() {
        return Ok((Vec::new(), AdaptiveKrylovStats::default()));
    }
    if t == 0.0 || b_norm == 0.0 {
        return Ok((vec![0.0; b.len()], AdaptiveKrylovStats::default()));
    }
    let n = b.len();
    let scale = b_norm.max(1.0);
    let coupling: Vec<f64> = b.iter().map(|value| value / scale).collect();
    let arithmetic_failed = std::cell::Cell::new(false);
    let augmented_apply = |z: &[f64]| -> Vec<f64> {
        if z.len() != n + 1 {
            return Vec::new();
        }
        let raw = apply(&z[..n]);
        if raw.len() != n {
            return Vec::new();
        }
        if !raw.iter().all(|value| value.is_finite()) {
            let mut out = raw;
            out.push(0.0);
            return out;
        }
        let bottom = z[n];
        let mut out = Vec::with_capacity(n + 1);
        for i in 0..n {
            let value = raw[i] + coupling[i] * bottom;
            if !value.is_finite() {
                arithmetic_failed.set(true);
            }
            out.push(value);
        }
        out.push(0.0);
        out
    };
    let mut initial = vec![0.0; n + 1];
    initial[n] = scale;
    let result = adaptive_expm_action(
        &augmented_apply,
        &initial,
        t,
        augmented_options(options, n + 1),
    );
    match result {
        Ok((z, stats)) => Ok((z[..n].to_vec(), stats)),
        Err(AdaptiveKrylovError::OperatorReturnedNonFinite { stats })
            if arithmetic_failed.get() =>
        {
            Err(AdaptiveKrylovError::ProjectionArithmeticNonFinite { stats })
        }
        Err(error) => Err(error),
    }
}

fn action_with_aggregate(
    result: Result<(Vec<f64>, AdaptiveKrylovStats), AdaptiveKrylovError>,
    aggregate: &mut AdaptiveKrylovStats,
) -> Result<Vec<f64>, AdaptiveKrylovError> {
    match result {
        Ok((value, stats)) => {
            aggregate.accumulate(&stats);
            Ok(value)
        }
        Err(error) => Err(error.with_prior_stats(aggregate)),
    }
}

/// Adaptive-Krylov counterpart of the accepted PR #6 Type-II Kato-AEM2 step.
/// The physics ordering/operators are unchanged. The integrator consumes the
/// scaled `t*phi1(tA)b` action directly, so no small-t division is present.
#[allow(clippy::too_many_arguments)]
pub fn kato_aem2_step_adaptive(
    directions: &[[f64; 3]],
    weights: &[f64],
    axis: usize,
    gamma: f64,
    h: f64,
    opacity_scale: f64,
    state_q1: &[f64; 5],
    state_mid: &[f64; 5],
    state_q3: &[f64; 5],
    opacity_mid: f64,
    y: &[f64],
    options: AdaptiveKrylovOptions,
) -> Result<(Vec<f64>, AdaptiveKrylovStats), AdaptiveKrylovError> {
    use super::typeii_background;
    use super::typeii_collision;
    use super::typeii_kato;
    use super::typeii_runtime;

    validate_options(options)?;
    if directions.len() != weights.len() || directions.len() != y.len() {
        return Err(AdaptiveKrylovError::OperatorDimensionMismatch {
            stats: AdaptiveKrylovStats::default(),
        });
    }
    if !h.is_finite() {
        return Err(AdaptiveKrylovError::NonFiniteTime);
    }
    if !gamma.is_finite()
        || !opacity_scale.is_finite()
        || !opacity_mid.is_finite()
        || !y.iter().all(|value| value.is_finite())
        || !weights.iter().all(|value| value.is_finite())
        || !directions.iter().flatten().all(|value| value.is_finite())
        || !state_q1.iter().all(|value| value.is_finite())
        || !state_mid.iter().all(|value| value.is_finite())
        || !state_q3.iter().all(|value| value.is_finite())
    {
        return Err(AdaptiveKrylovError::InputNotFinite);
    }
    if directions.is_empty() {
        return Err(AdaptiveKrylovError::InvalidKatoDomain {
            field: "empty_grid",
        });
    }
    if axis >= 3 {
        return Err(AdaptiveKrylovError::InvalidKatoDomain { field: "axis" });
    }
    if weights.iter().any(|weight| *weight <= 0.0) {
        return Err(AdaptiveKrylovError::InvalidKatoDomain { field: "weight" });
    }
    for direction in directions {
        let direction_norm = stable_norm2(direction).ok_or(AdaptiveKrylovError::InputNotFinite)?;
        if (direction_norm - 1.0).abs() > 1e-10 {
            return Err(AdaptiveKrylovError::InvalidKatoDomain {
                field: "direction_norm",
            });
        }
    }
    for state in [state_q1, state_mid, state_q3] {
        if state[4].abs() >= 1.0 {
            return Err(AdaptiveKrylovError::InvalidKatoDomain { field: "velocity" });
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
            return Err(AdaptiveKrylovError::InvalidKatoDomain {
                field: "projector_factors",
            });
        }
    }
    let collision_scale = opacity_scale * opacity_mid;
    if !collision_scale.is_finite() {
        return Err(AdaptiveKrylovError::InvalidKatoDomain {
            field: "collision_scale",
        });
    }
    let vd1 = typeii_background::rhs(state_q1, gamma)[4];
    let vdm = typeii_background::rhs(state_mid, gamma)[4];
    let vd3 = typeii_background::rhs(state_q3, gamma)[4];
    if !vd1.is_finite() || !vdm.is_finite() || !vd3.is_finite() {
        return Err(AdaptiveKrylovError::InvalidKatoDomain {
            field: "background_rhs",
        });
    }
    let mut stats = AdaptiveKrylovStats::default();

    let k1 = |x: &[f64]| typeii_kato::kato_apply(directions, weights, state_q1[4], vd1, axis, x);
    let ym = action_with_aggregate(adaptive_expm_action(&k1, y, 0.5 * h, options), &mut stats)?;

    let km = |x: &[f64]| typeii_kato::kato_apply(directions, weights, state_mid[4], vdm, axis, x);
    let aeff = |x: &[f64]| -> Vec<f64> {
        let mut a = match typeii_runtime::transport_apply(directions, state_mid, x) {
            Ok(value) => value,
            Err(_) => return vec![f64::NAN; x.len()],
        };
        let k = km(x);
        for i in 0..a.len() {
            a[i] -= k[i];
        }
        a
    };
    let collision = |x: &[f64]| -> Vec<f64> {
        typeii_collision::collision_generator_apply(directions, weights, state_mid[4], axis, x)
            .into_iter()
            .map(|value| collision_scale * value)
            .collect()
    };

    let half = 0.5 * h;
    let e_half = action_with_aggregate(
        adaptive_expm_action(&collision, &ym, half, options),
        &mut stats,
    )?;
    let a_ybar = aeff(&e_half);
    let tphi_half = action_with_aggregate(
        adaptive_t_phi1_action(&collision, &a_ybar, half, options),
        &mut stats,
    )?;
    let mut y_mid = e_half;
    for i in 0..y_mid.len() {
        y_mid[i] += tphi_half[i];
    }

    let e_full = action_with_aggregate(
        adaptive_expm_action(&collision, &ym, h, options),
        &mut stats,
    )?;
    let a_mid = aeff(&y_mid);
    let tphi_full = action_with_aggregate(
        adaptive_t_phi1_action(&collision, &a_mid, h, options),
        &mut stats,
    )?;
    let mut y_tilde = e_full;
    for i in 0..y_tilde.len() {
        y_tilde[i] += tphi_full[i];
    }

    let k3 = |x: &[f64]| typeii_kato::kato_apply(directions, weights, state_q3[4], vd3, axis, x);
    let out = action_with_aggregate(
        adaptive_expm_action(&k3, &y_tilde, half, options),
        &mut stats,
    )?;
    Ok((out, stats))
}
