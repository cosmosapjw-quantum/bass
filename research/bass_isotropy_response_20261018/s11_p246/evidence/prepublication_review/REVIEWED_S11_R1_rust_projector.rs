//! Positive, reflection-even angular projection for a *new* isotropic birth.
//!
//! This module owns no existing photon stock, native spectral bins or cosmology.
//! It minimizes KL(w || prior), imposing E[P2]=E[P4]=0 (order 4), and also
//! E[P6]=0 (order 6). The dual is log-sum-exp; its Hessian is the centered
//! covariance. All moment constraints are solved simultaneously. Input arrays
//! are borrowed immutably and returned weights are fresh. No weights are clipped.
//!
//! The convex-hull preflight encloses the *exact* squares of input binary64 mu.
//! Its positive intervals are sufficient strict-interior certificates. An
//! interval overlapping zero, or insufficient rank, is explicitly unresolved.
//! Newton success is provisional: an independent exact-arithmetic observer must
//! apply the project's 3e-15 normalization / P2 / P4 / P6 gate to the returned
//! binary64 weights and directions. The fixed 8e-16 internal guard is stricter;
//! it is not a configurable replacement for the exact project gate.

const MAX_RAYS: usize = 4096;
const MAX_ITERATIONS: usize = 160;
const MAX_BACKTRACK: usize = 60;
const TARGET: f64 = 2.0e-16;
const FINAL_GUARD: f64 = 8.0e-16;
const ARMIJO: f64 = 1.0e-4;

#[derive(Debug, Clone)]
pub struct ProjectError {
    pub status: &'static str,
    pub message: String,
}

fn error(status: &'static str, message: impl Into<String>) -> ProjectError {
    ProjectError {
        status,
        message: message.into(),
    }
}

#[derive(Debug, Clone)]
pub struct SupportCertificate {
    pub distinct_squared_nodes: usize,
    pub facet_count: usize,
    pub minimum_certified_slack_lower: f64,
}

#[derive(Debug, Clone)]
pub struct Projected {
    pub weights: Vec<f64>,
    pub lambda: Vec<f64>,
    pub iterations: usize,
    /// Normalization minus one, followed by P2, P4, and (if order=6) P6.
    pub residuals: Vec<f64>,
    pub support: SupportCertificate,
}

#[derive(Clone, Copy, Debug)]
struct Interval {
    lo: f64,
    hi: f64,
}

// Next representable endpoints, including signed zero and subnormals. No
// floating-point environment change is required; arithmetic remains binary64
// round-to-nearest with gradual underflow and without fast-math.
fn down(x: f64) -> f64 {
    if x.is_nan() || x == f64::NEG_INFINITY {
        return x;
    }
    if x == 0.0 {
        return -f64::from_bits(1);
    }
    f64::from_bits(if x > 0.0 {
        x.to_bits() - 1
    } else {
        x.to_bits() + 1
    })
}

fn up(x: f64) -> f64 {
    if x.is_nan() || x == f64::INFINITY {
        return x;
    }
    if x == 0.0 {
        return f64::from_bits(1);
    }
    f64::from_bits(if x > 0.0 {
        x.to_bits() + 1
    } else {
        x.to_bits() - 1
    })
}

impl Interval {
    fn point(x: f64) -> Self {
        Self { lo: x, hi: x }
    }
    fn rational(n: f64, d: f64) -> Self {
        let x = n / d;
        Self {
            lo: down(x),
            hi: up(x),
        }
    }
    fn add(self, rhs: Self) -> Self {
        Self {
            lo: down(self.lo + rhs.lo),
            hi: up(self.hi + rhs.hi),
        }
    }
    fn sub(self, rhs: Self) -> Self {
        Self {
            lo: down(self.lo - rhs.hi),
            hi: up(self.hi - rhs.lo),
        }
    }
    fn mul(self, rhs: Self) -> Self {
        let products = [
            self.lo * rhs.lo,
            self.lo * rhs.hi,
            self.hi * rhs.lo,
            self.hi * rhs.hi,
        ];
        let lo = products.iter().copied().fold(f64::INFINITY, f64::min);
        let hi = products.iter().copied().fold(f64::NEG_INFINITY, f64::max);
        Self {
            lo: down(lo),
            hi: up(hi),
        }
    }
    fn neg(self) -> Self {
        Self {
            lo: -self.hi,
            hi: -self.lo,
        }
    }
    fn squared_mu(mu: f64) -> Self {
        let q = Self::point(mu).mul(Self::point(mu));
        // The separately established input domain proves 0 <= mu^2 <= 1.
        Self {
            lo: q.lo.max(0.0),
            hi: q.hi.min(1.0),
        }
    }
}

fn quadratic_mean(a: Interval, b: Interval) -> Interval {
    Interval::rational(1.0, 5.0)
        .sub(a.add(b).mul(Interval::rational(1.0, 3.0)))
        .add(a.mul(b))
}

fn cubic_mean(a: Interval, b: Interval, c: Interval) -> Interval {
    Interval::rational(1.0, 7.0)
        .sub(a.add(b).add(c).mul(Interval::rational(1.0, 5.0)))
        .add(
            a.mul(b)
                .add(a.mul(c))
                .add(b.mul(c))
                .mul(Interval::rational(1.0, 3.0)),
        )
        .sub(a.mul(b).mul(c))
}

fn support_preflight(mu: &[f64], order: u8) -> Result<SupportCertificate, ProjectError> {
    let mut absolute: Vec<f64> = mu.iter().map(|x| x.abs()).collect();
    absolute.sort_by(|a, b| a.total_cmp(b));
    // Distinct nonnegative binary64 mu imply distinct exact real mu^2, even if
    // two rounded products coincide. Deduplicate directions, not rounded z.
    absolute.dedup_by(|a, b| *a == *b);
    let nodes: Vec<Interval> = absolute.iter().map(|&x| Interval::squared_mu(x)).collect();
    let m = nodes.len();
    let needed = order as usize / 2 + 1;
    if m < needed {
        return Err(error(
            "FEASIBILITY_UNRESOLVED",
            format!(
                "{} distinct squared nodes; full-rank order {} requires at least {}",
                m, order, needed
            ),
        ));
    }
    let mut facets: Vec<(String, Interval)> = Vec::new();
    if order == 4 {
        // Consecutive chords and the endpoint chord bound the parabola hull.
        for i in 0..m - 1 {
            facets.push((
                format!("P24_lower_{}", i),
                quadratic_mean(nodes[i], nodes[i + 1]),
            ));
        }
        facets.push((
            "P24_upper".into(),
            quadratic_mean(nodes[0], nodes[m - 1]).neg(),
        ));
        // Redundant full-rank checks retained as explicit physical diagnostics.
        facets.push((
            "mean_above_min".into(),
            Interval::rational(1.0, 3.0).sub(nodes[0]),
        ));
        facets.push((
            "mean_below_max".into(),
            nodes[m - 1].sub(Interval::rational(1.0, 3.0)),
        ));
    } else {
        // Facets of the 3D moment-curve polytope, for sorted z_0 < ... < z_m-1.
        // E[(z-z_0)(z-z_i)(z-z_i+1)] > 0, i=1..m-2;
        // -E[(z-z_i)(z-z_i+1)(z-z_m-1)] > 0, i=0..m-3.
        for i in 1..m - 1 {
            facets.push((
                format!("P246_lower_{}", i),
                cubic_mean(nodes[0], nodes[i], nodes[i + 1]),
            ));
        }
        for i in 0..m - 2 {
            facets.push((
                format!("P246_upper_{}", i),
                cubic_mean(nodes[i], nodes[i + 1], nodes[m - 1]).neg(),
            ));
        }
    }
    let mut ambiguous = None;
    let mut minimum = f64::INFINITY;
    for (name, slack) in &facets {
        if slack.hi < 0.0 {
            return Err(error(
                "INFEASIBLE_SUPPORT",
                format!(
                    "{} has negative exact-slack enclosure [{:.17e},{:.17e}]",
                    name, slack.lo, slack.hi
                ),
            ));
        }
        if !(slack.lo > 0.0) && ambiguous.is_none() {
            ambiguous = Some(format!(
                "{} exact-slack enclosure overlaps zero [{:.17e},{:.17e}]",
                name, slack.lo, slack.hi
            ));
        }
        minimum = minimum.min(slack.lo);
    }
    if let Some(message) = ambiguous {
        return Err(error("FEASIBILITY_UNRESOLVED", message));
    }
    Ok(SupportCertificate {
        distinct_squared_nodes: m,
        facet_count: facets.len(),
        minimum_certified_slack_lower: minimum,
    })
}

#[derive(Clone, Copy, Default)]
struct Sum {
    sum: f64,
    correction: f64,
}
impl Sum {
    fn add(&mut self, value: f64) {
        let next = self.sum + value;
        self.correction += if self.sum.abs() >= value.abs() {
            (self.sum - next) + value
        } else {
            (value - next) + self.sum
        };
        self.sum = next;
    }
    fn value(self) -> f64 {
        self.sum + self.correction
    }
}

fn dot(a: &[f64; 3], b: &[f64; 3], k: usize) -> f64 {
    let mut sum = Sum::default();
    for j in 0..k {
        sum.add(a[j] * b[j]);
    }
    sum.value()
}

fn legendre_even(mu: f64) -> [f64; 3] {
    let x = mu.abs();
    let mut out = [0.0; 3];
    let mut previous = 1.0;
    let mut current = x;
    for degree in 2..=6 {
        let next = (((2 * degree - 1) as f64) * x * current - ((degree - 1) as f64) * previous)
            / (degree as f64);
        if degree % 2 == 0 {
            out[degree / 2 - 1] = next;
        }
        previous = current;
        current = next;
    }
    out
}

#[derive(Clone)]
struct Evaluation {
    masses: Vec<f64>,
    mean: [f64; 3],
    covariance: [[f64; 3]; 3],
}

fn evaluate(
    log_prior: &[f64],
    features: &[[f64; 3]],
    lambda: &[f64; 3],
    k: usize,
) -> Option<Evaluation> {
    let mut logs = Vec::with_capacity(features.len());
    let mut largest = f64::NEG_INFINITY;
    for (q, phi) in log_prior.iter().zip(features) {
        let a = *q + dot(lambda, phi, k);
        if !a.is_finite() {
            return None;
        }
        largest = largest.max(a);
        logs.push(a);
    }
    let mut sum = Sum::default();
    let mut masses = Vec::with_capacity(logs.len());
    for value in logs {
        let p = (value - largest).exp();
        if !(p > 0.0 && p.is_finite()) {
            return None;
        }
        masses.push(p);
        sum.add(p);
    }
    let denominator = sum.value();
    for p in &mut masses {
        *p /= denominator;
        if !(*p > 0.0 && p.is_finite()) {
            return None;
        }
    }
    let mut moments = [Sum::default(); 3];
    for (mass, phi) in masses.iter().zip(features) {
        for j in 0..k {
            moments[j].add(mass * phi[j]);
        }
    }
    let mut mean = [0.0; 3];
    for j in 0..k {
        mean[j] = moments[j].value();
    }
    let mut centered = [[Sum::default(); 3]; 3];
    for (mass, phi) in masses.iter().zip(features) {
        for i in 0..k {
            for j in 0..=i {
                centered[i][j].add(mass * (phi[i] - mean[i]) * (phi[j] - mean[j]));
            }
        }
    }
    let mut covariance = [[0.0; 3]; 3];
    for i in 0..k {
        for j in 0..=i {
            covariance[i][j] = centered[i][j].value();
            covariance[j][i] = covariance[i][j];
        }
    }
    Some(Evaluation {
        masses,
        mean,
        covariance,
    })
}

fn norm(mean: &[f64; 3], k: usize) -> f64 {
    mean[..k].iter().map(|x| x.abs()).fold(0.0, f64::max)
}

fn cholesky_solve(matrix: &[[f64; 3]; 3], rhs: &[f64; 3], k: usize) -> Option<[f64; 3]> {
    let mut lower = [[0.0; 3]; 3];
    for i in 0..k {
        for j in 0..=i {
            let mut residual = Sum::default();
            residual.add(matrix[i][j]);
            for q in 0..j {
                residual.add(-lower[i][q] * lower[j][q]);
            }
            let value = residual.value();
            if i == j {
                if !(value > 0.0 && value.is_finite()) {
                    return None;
                }
                lower[i][j] = value.sqrt();
            } else {
                lower[i][j] = value / lower[j][j];
                if !lower[i][j].is_finite() {
                    return None;
                }
            }
        }
    }
    let mut work = [0.0; 3];
    for i in 0..k {
        let mut residual = Sum::default();
        residual.add(rhs[i]);
        for j in 0..i {
            residual.add(-lower[i][j] * work[j]);
        }
        work[i] = residual.value() / lower[i][i];
    }
    let mut solution = [0.0; 3];
    for i in (0..k).rev() {
        let mut residual = Sum::default();
        residual.add(work[i]);
        for j in i + 1..k {
            residual.add(-lower[j][i] * solution[j]);
        }
        solution[i] = residual.value() / lower[i][i];
        if !solution[i].is_finite() {
            return None;
        }
    }
    Some(solution)
}

// Local log-sum-exp difference log E_w exp(delta_lambda . phi). expm1/log1p
// retain the small change near the optimum; subtracting two rounded global
// objective values would create a separate precision ceiling.
fn objective_change(
    old: &Evaluation,
    features: &[[f64; 3]],
    delta: &[f64; 3],
    k: usize,
) -> Option<f64> {
    let mut change = Sum::default();
    let mut mass = Sum::default();
    for (p, phi) in old.masses.iter().zip(features) {
        let value = dot(delta, phi, k).exp_m1();
        if !value.is_finite() {
            return None;
        }
        change.add(p * value);
        mass.add(*p);
    }
    let bump = change.value() / mass.value();
    if !(bump > -1.0 && bump.is_finite()) {
        return None;
    }
    let value = bump.ln_1p();
    if value.is_finite() {
        Some(value)
    } else {
        None
    }
}

fn finish(
    mu: &[f64],
    evaluation: &Evaluation,
    lambda: &[f64; 3],
    k: usize,
    iterations: usize,
    support: SupportCertificate,
) -> Result<Projected, ProjectError> {
    let n = mu.len();
    let mut weights = vec![0.0; n];
    for (i, mass) in evaluation.masses.iter().enumerate() {
        let other = n - 1 - i;
        let p = if i == other { *mass } else { *mass / 2.0 };
        if !(p > 0.0 && p.is_finite()) {
            return Err(error(
                "NUMERIC_PRECISION_LIMIT",
                "a positive orbit mass cannot be split into positive binary64 ray weights",
            ));
        }
        weights[i] = p;
        weights[other] = p;
    }
    let mut sums = [Sum::default(); 4];
    for (&direction, &weight) in mu.iter().zip(&weights) {
        sums[0].add(weight);
        let phi = legendre_even(direction);
        for j in 0..k {
            sums[j + 1].add(weight * phi[j]);
        }
    }
    let mut residuals = Vec::with_capacity(k + 1);
    residuals.push(sums[0].value() - 1.0);
    for j in 0..k {
        residuals.push(sums[j + 1].value());
    }
    if residuals
        .iter()
        .any(|x| !x.is_finite() || x.abs() > FINAL_GUARD)
    {
        return Err(error(
            "NUMERIC_PRECISION_LIMIT",
            format!("fixed final binary64 guard not met: {:?}", residuals),
        ));
    }
    Ok(Projected {
        weights,
        lambda: lambda[..k].to_vec(),
        iterations,
        residuals,
        support,
    })
}

/// Construct fresh positive weights on a fixed, exactly reflection-paired ray
/// set. `order` is 4 or 6. `declared_isotropic_birth` must explicitly be true.
/// Priors are positive and exactly paired but need not already sum to one.
/// Input directions and priors are never mutated, dropped, or re-ordered.
pub fn project(
    mu: &[f64],
    prior: &[f64],
    order: u8,
    declared_isotropic_birth: bool,
) -> Result<Projected, ProjectError> {
    if !declared_isotropic_birth {
        return Err(error(
            "NOT_ISOTROPIC_BIRTH",
            "projection requires an explicitly declared new isotropic birth",
        ));
    }
    if order != 4 && order != 6 {
        return Err(error("INVALID_INPUT", "order must be 4 or 6"));
    }
    if mu.is_empty() || mu.len() != prior.len() || mu.len() > MAX_RAYS {
        return Err(error(
            "INVALID_INPUT",
            "equal nonempty input arrays with at most 4096 rays are required",
        ));
    }
    let n = mu.len();
    for i in 0..n {
        if !mu[i].is_finite() || mu[i].abs() > 1.0 || !(prior[i] > 0.0 && prior[i].is_finite()) {
            return Err(error(
                "INVALID_INPUT",
                format!("nonfinite/domain/positive-prior violation at ray {}", i),
            ));
        }
        if i > 0 && mu[i] < mu[i - 1] {
            return Err(error("INVALID_INPUT", "directions must be sorted"));
        }
        if mu[i] != -mu[n - 1 - i] || prior[i] != prior[n - 1 - i] {
            return Err(error(
                "INVALID_INPUT",
                format!("exact reflection pairing violated at ray {}", i),
            ));
        }
    }
    let support = support_preflight(mu, order)?;
    let k = order as usize / 2;
    let orbits = (n + 1) / 2;
    let mut features = Vec::with_capacity(orbits);
    let mut log_prior = Vec::with_capacity(orbits);
    for i in 0..orbits {
        features.push(legendre_even(mu[i]));
        log_prior.push(
            prior[i].ln()
                + if i == n - 1 - i {
                    0.0
                } else {
                    std::f64::consts::LN_2
                },
        );
    }
    let largest = log_prior.iter().copied().fold(f64::NEG_INFINITY, f64::max);
    for q in &mut log_prior {
        *q -= largest;
    }
    let mut lambda = [0.0; 3];
    let mut state = evaluate(&log_prior, &features, &lambda, k).ok_or_else(|| {
        error(
            "NUMERIC_PRECISION_LIMIT",
            "initial normalized positive prior is outside binary64 probability range",
        )
    })?;
    let mut best = state.clone();
    let mut best_lambda = lambda;
    let mut best_norm = norm(&state.mean, k);
    let mut accepted_steps = 0;
    for _ in 0..MAX_ITERATIONS {
        let current_norm = norm(&state.mean, k);
        if current_norm <= TARGET {
            return finish(mu, &state, &lambda, k, accepted_steps, support);
        }
        let step = match cholesky_solve(&state.covariance, &state.mean, k) {
            Some(step) => step,
            None => {
                if best_norm <= FINAL_GUARD {
                    return finish(mu, &best, &best_lambda, k, accepted_steps, support);
                }
                return Err(error("NUMERIC_PRECISION_LIMIT","centered covariance is not positive definite in binary64; no clipping/pseudoinverse used"));
            }
        };
        let mut alpha = 1.0;
        let mut accepted = None;
        for _ in 0..MAX_BACKTRACK {
            let mut candidate_lambda = lambda;
            let mut delta = [0.0; 3];
            for j in 0..k {
                candidate_lambda[j] = lambda[j] - alpha * step[j];
                delta[j] = candidate_lambda[j] - lambda[j];
            }
            if delta[..k].iter().all(|x| *x == 0.0) {
                break;
            }
            if let Some(candidate) = evaluate(&log_prior, &features, &candidate_lambda, k) {
                let candidate_norm = norm(&candidate.mean, k);
                if candidate_norm < best_norm {
                    best_norm = candidate_norm;
                    best = candidate.clone();
                    best_lambda = candidate_lambda;
                }
                let slope = dot(&state.mean, &delta, k);
                let armijo = slope < 0.0
                    && objective_change(&state, &features, &delta, k)
                        .map(|change| change <= ARMIJO * slope)
                        .unwrap_or(false);
                // The residual merit below is used only in the local Newton
                // regime to survive objective-level rounding cancellation.
                // It does not relax the final moment or positivity gates.
                let local_merit = current_norm < 1.0e-6
                    && norm(&delta, k) < 0.5
                    && candidate_norm < (1.0 - ARMIJO * alpha) * current_norm;
                if armijo || local_merit || candidate_norm <= TARGET {
                    accepted = Some((candidate_lambda, candidate));
                    break;
                }
            }
            alpha *= 0.5;
        }
        match accepted {
            Some((next_lambda, next_state)) => {
                lambda = next_lambda;
                state = next_state;
                accepted_steps += 1;
            }
            None => {
                if best_norm <= FINAL_GUARD {
                    return finish(mu, &best, &best_lambda, k, accepted_steps, support);
                }
                return Err(error("NUMERIC_PRECISION_LIMIT",
                    format!("line search exhausted without admissible fixed-gate solution; best moment residual {:.17e}",best_norm)));
            }
        }
    }
    if best_norm <= FINAL_GUARD {
        return finish(mu, &best, &best_lambda, k, accepted_steps, support);
    }
    Err(error(
        "NUMERIC_PRECISION_LIMIT",
        format!(
            "iteration bound reached; best moment residual {:.17e}",
            best_norm
        ),
    ))
}
