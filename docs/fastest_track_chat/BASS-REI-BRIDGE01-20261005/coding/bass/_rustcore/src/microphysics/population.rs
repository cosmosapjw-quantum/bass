//! Frozen positive population polynomial from Dossier V §14.4, equations (187)–(189).
//!
//! Supplied `rates[i][j]` is the nonnegative off-diagonal transfer rate of
//! `G` from state `j` to state `i` in weighted coordinates `x = W p`.
//! Supplied diagonal entries are zero; `G[j][j]` is defined here as minus
//! its column outflow. This is a fixed finite generator, not a rate model.

/// Invalid physical input, unsupported finite domain, or nonfinite arithmetic.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum PopulationError {
    InvalidStateCount,
    ShapeMismatch,
    InvalidWeight,
    InvalidRate,
    InvalidPopulation,
    InvalidStep,
    InvalidOrder,
    MeanTooLarge,
    ArithmeticOverflow,
    WeightedStateUnderflow,
}

impl std::fmt::Display for PopulationError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{self:?}")
    }
}

impl std::error::Error for PopulationError {}

/// Frozen generator on 1–32 nonnegative population coordinates.
#[derive(Clone, Debug)]
pub struct FrozenPopulation {
    weights: Vec<f64>,
    rates: Vec<Vec<f64>>,
    outflow: Vec<f64>,
    lambda: f64,
}

/// Tail-lumped polynomial action and its analytic truncation bound.
#[derive(Clone, Debug)]
pub struct PopulationAdvance {
    pub populations: Vec<f64>,
    /// `2 P(Poisson(lambda*h)>m) * sum_j weights[j]*initial[j]`.
    /// This bounds truncation against the frozen exact exponential in weighted
    /// L1, excluding floating roundoff and any variation of the rates.
    pub weighted_l1_error_bound: f64,
}

impl FrozenPopulation {
    /// Validate a supplied off-diagonal weighted-coordinate rate table.
    pub fn new(weights: &[f64], rates: &[Vec<f64>]) -> Result<Self, PopulationError> {
        let n = weights.len();
        if !(1..=32).contains(&n) {
            return Err(PopulationError::InvalidStateCount);
        }
        if rates.len() != n || rates.iter().any(|row| row.len() != n) {
            return Err(PopulationError::ShapeMismatch);
        }
        if weights.iter().any(|&w| !w.is_finite() || w <= 0.0) {
            return Err(PopulationError::InvalidWeight);
        }
        for (i, row) in rates.iter().enumerate() {
            for (j, &rate) in row.iter().enumerate() {
                if !rate.is_finite() || rate < 0.0 || (i == j && rate != 0.0) {
                    return Err(PopulationError::InvalidRate);
                }
            }
        }
        let mut outflow = vec![0.0; n];
        for (j, outgoing) in outflow.iter_mut().enumerate() {
            for (i, row) in rates.iter().enumerate() {
                if i != j {
                    *outgoing += row[j];
                    if !outgoing.is_finite() {
                        return Err(PopulationError::ArithmeticOverflow);
                    }
                }
            }
        }
        let lambda = outflow.iter().copied().fold(0.0_f64, f64::max);
        Ok(Self {
            weights: weights.to_vec(),
            rates: rates.to_vec(),
            outflow,
            lambda,
        })
    }

    /// Apply `sum_{k=0}^{m-1} p_k T^k + P(N>=m) T^m` to the initial population.
    ///
    /// `N` is Poisson with mean `lambda*h`, `T = I + G/lambda`, and
    /// `p_k = exp(-lambda*h)(lambda*h)^k/k!`. Exact coefficients are positive
    /// and conservative. Floating coefficient normalization compensates only
    /// accumulated rounding; the returned theorem bound excludes roundoff.
    /// `h=0` or a zero generator returns exact identity and zero bound.
    /// Otherwise every positive initial weighted population must be at least
    /// `f64::MIN_POSITIVE`. Smaller values (including products rounded to zero)
    /// return `WeightedStateUnderflow`: Poisson products can erase such states.
    pub fn advance(
        &self,
        populations: &[f64],
        h: f64,
        m: usize,
    ) -> Result<PopulationAdvance, PopulationError> {
        if populations.len() != self.weights.len() {
            return Err(PopulationError::ShapeMismatch);
        }
        if populations.iter().any(|&p| !p.is_finite() || p < 0.0) {
            return Err(PopulationError::InvalidPopulation);
        }
        if !h.is_finite() || h < 0.0 {
            return Err(PopulationError::InvalidStep);
        }
        if m > 1024 {
            return Err(PopulationError::InvalidOrder);
        }
        if self.lambda == 0.0 || h == 0.0 {
            return Ok(PopulationAdvance {
                populations: populations.to_vec(),
                weighted_l1_error_bound: 0.0,
            });
        }
        let mean = self.lambda * h;
        if !mean.is_finite() {
            return Err(PopulationError::ArithmeticOverflow);
        }
        if mean > 64.0 {
            return Err(PopulationError::MeanTooLarge);
        }
        let mut initial = Vec::with_capacity(populations.len());
        let mut mass = 0.0;
        for (&w, &p) in self.weights.iter().zip(populations) {
            let value = w * p;
            mass += value;
            if !value.is_finite() || !mass.is_finite() {
                return Err(PopulationError::ArithmeticOverflow);
            }
            if p > 0.0 && value < f64::MIN_POSITIVE {
                return Err(PopulationError::WeightedStateUnderflow);
            }
            initial.push(value);
        }
        if m == 0 {
            let bound = 2.0 * (-(-mean).exp_m1()) * mass;
            if !bound.is_finite() {
                return Err(PopulationError::ArithmeticOverflow);
            }
            return Ok(PopulationAdvance {
                populations: populations.to_vec(),
                weighted_l1_error_bound: bound,
            });
        }

        let mut state = initial;
        let mut result = vec![0.0; state.len()];
        let mut pk = (-mean).exp();
        let mut coefficient_sum = 0.0;
        for k in 0..m {
            coefficient_sum += pk;
            for (result_i, &state_i) in result.iter_mut().zip(&state) {
                *result_i += pk * state_i;
            }
            state = self.apply_t(&state)?;
            pk *= mean / (k + 1) as f64;
        }
        let tail_at_m = poisson_tail_from_term(pk, mean, m);
        let tail_after_m = poisson_tail_from_term(pk * mean / (m + 1) as f64, mean, m + 1);
        let coefficient_total = coefficient_sum + tail_at_m;
        // Analytically this equals one; normalization removes only sum roundoff.
        if !coefficient_total.is_finite() || coefficient_total <= 0.0 {
            return Err(PopulationError::ArithmeticOverflow);
        }
        for (result_i, &state_i) in result.iter_mut().zip(&state) {
            *result_i = (*result_i + tail_at_m * state_i) / coefficient_total;
        }
        let mut output = Vec::with_capacity(result.len());
        for (&x, &w) in result.iter().zip(&self.weights) {
            let p = x / w;
            if !p.is_finite() || p < 0.0 {
                return Err(PopulationError::ArithmeticOverflow);
            }
            output.push(p);
        }
        let bound = 2.0 * tail_after_m * mass;
        if !bound.is_finite() {
            return Err(PopulationError::ArithmeticOverflow);
        }
        Ok(PopulationAdvance {
            populations: output,
            weighted_l1_error_bound: bound,
        })
    }

    fn apply_t(&self, x: &[f64]) -> Result<Vec<f64>, PopulationError> {
        let n = x.len();
        let mut next = vec![0.0; n];
        for (j, &xj) in x.iter().enumerate() {
            let staying = 1.0 - self.outflow[j] / self.lambda;
            next[j] += staying * xj;
            for (i, row) in self.rates.iter().enumerate() {
                if i != j {
                    next[i] += (row[j] / self.lambda) * xj;
                }
            }
        }
        if next.iter().any(|v| !v.is_finite()) {
            return Err(PopulationError::ArithmeticOverflow);
        }
        Ok(next)
    }
}

// Sum a Poisson upper tail directly, avoiding `1 - CDF` cancellation when tiny.
fn poisson_tail_from_term(mut term: f64, mean: f64, start: usize) -> f64 {
    let mut tail = 0.0;
    for k in start..=2048 {
        if term == 0.0 {
            break;
        }
        tail += term;
        term *= mean / (k + 1) as f64;
    }
    tail
}
