//! Fixed-input Thomson visibility for a single ray in a common H/He material frame.
//!
//! Nuclear densities are proper number densities in m^-3; the supplied ionization
//! fractions belong to that same material frame. Rates are per second of the
//! Bianchi normal ray clock. The rates and time edges are supplied externally:
//! this module does not evolve chemistry, geometry, or the photon distribution.
//! In particular, a scalar rest-frame opacity schedule is not a directional
//! normal-clock rate and must not be passed in as though it already includes
//! the ray's Doppler factor.

use super::frame::{FrameError, MaterialFrame};

/// Speed of light in vacuum, in m s^-1.
pub const C_M_S: f64 = 299_792_458.0;
/// Thomson cross section, in m^2.
pub const SIGMA_T_M2: f64 = 6.652_458_7e-29;

/// Invalid physical input or nonfinite floating-point arithmetic.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum VisibilityError {
    InvalidDensity,
    InvalidFraction,
    InvalidGrid,
    InvalidRate,
    InvalidObserverDepth,
    NonFiniteArithmetic,
    Frame(FrameError),
}

impl From<FrameError> for VisibilityError {
    fn from(error: FrameError) -> Self {
        Self::Frame(error)
    }
}

/// A validated proper electron density shared by chemistry and Thomson opacity.
#[derive(Clone, Copy, Debug)]
pub struct ElectronState {
    number_density_m3: f64,
}

impl ElectronState {
    /// Build `n_e = n_H x_HII + n_He (x_HeII + 2 x_HeIII)`.
    ///
    /// All inputs must be finite. Nuclear densities are nonnegative proper
    /// densities in m^-3 in one material frame. Ionization fractions are
    /// nonnegative, with `x_HII <= 1` and `x_HeII + x_HeIII <= 1`.
    pub fn new(
        n_h_m3: f64,
        n_he_m3: f64,
        x_hii: f64,
        x_heii: f64,
        x_heiii: f64,
    ) -> Result<Self, VisibilityError> {
        if !n_h_m3.is_finite() || !n_he_m3.is_finite() || n_h_m3 < 0.0 || n_he_m3 < 0.0 {
            return Err(VisibilityError::InvalidDensity);
        }
        if !x_hii.is_finite()
            || !x_heii.is_finite()
            || !x_heiii.is_finite()
            || !(0.0..=1.0).contains(&x_hii)
            || x_heii < 0.0
            || x_heiii < 0.0
            || x_heii + x_heiii > 1.0
        {
            return Err(VisibilityError::InvalidFraction);
        }

        let number_density_m3 = n_h_m3 * x_hii + n_he_m3 * (x_heii + 2.0 * x_heiii);
        if !number_density_m3.is_finite() {
            return Err(VisibilityError::NonFiniteArithmetic);
        }
        Ok(Self { number_density_m3 })
    }

    /// Proper electron number density, in m^-3.
    pub fn number_density_m3(self) -> f64 {
        self.number_density_m3
    }

    /// Directional Thomson rate `q = c n_e sigma_T D` per normal ray second.
    ///
    /// The material frame validates the unit ray direction and computes
    /// `D = gamma (1 - beta · e)` here, exactly once. The returned rate already
    /// includes `D`; a consumer must not multiply by it again. Direction is
    /// checked even when `n_e` is zero.
    pub fn scattering_rate_per_normal_second(
        self,
        frame: MaterialFrame,
        e_normal: [f64; 3],
    ) -> Result<f64, VisibilityError> {
        let doppler = frame.doppler(e_normal)?;
        let rate = self.number_density_m3 * (C_M_S * SIGMA_T_M2) * doppler;
        if !rate.is_finite() {
            return Err(VisibilityError::NonFiniteArithmetic);
        }
        Ok(rate)
    }
}

/// Piecewise-constant visibility on a finite normal-time interval.
#[derive(Clone, Debug)]
pub struct VisibilityResult {
    /// Backward optical depth at each edge, including the observer tail.
    pub optical_depth: Vec<f64>,
    /// `exp(-optical_depth)` at each edge; the first value is unscattered mass.
    pub survival: Vec<f64>,
    /// Probability mass within each interval, without finite-interval renormalization.
    pub interval_probability: Vec<f64>,
}

/// Integrate a nonnegative, piecewise-constant rate along one normal-clock ray.
///
/// `time_edges_seconds` are finite and strictly increasing. Each rate in s^-1
/// applies on the corresponding interval. The nonnegative dimensionless
/// `observer_optical_depth` is the optical depth beyond the last edge, so its
/// survival factor remains explicit even when the observed tail is nonzero.
/// A finite interval retains its unscattered probability rather than being
/// renormalized to unit mass. A cell's mass is evaluated as
/// `exp(-tau_right) * -expm1(-q * dt)` to avoid cancellation for thin cells.
pub fn integrate_visibility(
    time_edges_seconds: &[f64],
    interval_rates_s_inverse: &[f64],
    observer_optical_depth: f64,
) -> Result<VisibilityResult, VisibilityError> {
    validate_grid_and_rates(time_edges_seconds, interval_rates_s_inverse)?;
    if !observer_optical_depth.is_finite() || observer_optical_depth < 0.0 {
        return Err(VisibilityError::InvalidObserverDepth);
    }

    let n = interval_rates_s_inverse.len();
    let mut optical_depth = vec![0.0; n + 1];
    let mut survival = vec![0.0; n + 1];
    let mut interval_probability = vec![0.0; n];
    optical_depth[n] = observer_optical_depth;
    survival[n] = (-observer_optical_depth).exp();

    for i in (0..n).rev() {
        let dt = time_edges_seconds[i + 1] - time_edges_seconds[i];
        let cell_depth = interval_rates_s_inverse[i] * dt;
        let depth = optical_depth[i + 1] + cell_depth;
        if !cell_depth.is_finite() || !depth.is_finite() {
            return Err(VisibilityError::NonFiniteArithmetic);
        }
        optical_depth[i] = depth;
        survival[i] = (-depth).exp();
        interval_probability[i] = survival[i + 1] * -(-cell_depth).exp_m1();
    }
    Ok(VisibilityResult {
        optical_depth,
        survival,
        interval_probability,
    })
}

/// Bounds for two opacity histories sampled on the same ray clock and edges.
#[derive(Clone, Debug)]
pub struct OpacityComparison {
    /// Backward integral of the absolute rate difference, at every edge.
    pub opacity_l1_tail: Vec<f64>,
    /// Bound `1 - exp(-E)` on the difference in edge survival probabilities.
    pub survival_error_bound: Vec<f64>,
    /// Sum of endpoint survival bounds for each interval's probability mass.
    pub interval_probability_error_bound: Vec<f64>,
}

/// Bound survival and interval-mass errors from two piecewise-constant rates.
///
/// Both nonnegative rates must refer to the same ray, normal-time grid, and
/// observer optical-depth boundary. A common observer tail cancels from the
/// opacity difference, so it is absent from this API. The backward quantity
/// `E(t) = integral_t^last |q - q_ref| dt` bounds each survival difference by
/// `1 - exp(-E)`, and each interval-mass difference by the sum of its endpoint
/// bounds. These integral bounds do not bound visibility peak height or location.
pub fn compare_opacity(
    time_edges_seconds: &[f64],
    interval_rates_s_inverse: &[f64],
    reference_rates_s_inverse: &[f64],
) -> Result<OpacityComparison, VisibilityError> {
    validate_grid_and_rates(time_edges_seconds, interval_rates_s_inverse)?;
    validate_grid_and_rates(time_edges_seconds, reference_rates_s_inverse)?;

    let n = interval_rates_s_inverse.len();
    let mut opacity_l1_tail = vec![0.0; n + 1];
    let mut survival_error_bound = vec![0.0; n + 1];
    let mut interval_probability_error_bound = vec![0.0; n];
    for i in (0..n).rev() {
        let dt = time_edges_seconds[i + 1] - time_edges_seconds[i];
        let increment = (interval_rates_s_inverse[i] - reference_rates_s_inverse[i]).abs() * dt;
        let tail = opacity_l1_tail[i + 1] + increment;
        if !increment.is_finite() || !tail.is_finite() {
            return Err(VisibilityError::NonFiniteArithmetic);
        }
        opacity_l1_tail[i] = tail;
        survival_error_bound[i] = -(-tail).exp_m1();
        interval_probability_error_bound[i] = survival_error_bound[i] + survival_error_bound[i + 1];
    }
    Ok(OpacityComparison {
        opacity_l1_tail,
        survival_error_bound,
        interval_probability_error_bound,
    })
}

fn validate_grid_and_rates(
    time_edges_seconds: &[f64],
    interval_rates_s_inverse: &[f64],
) -> Result<(), VisibilityError> {
    if time_edges_seconds.len() < 2
        || interval_rates_s_inverse.len() != time_edges_seconds.len() - 1
    {
        return Err(VisibilityError::InvalidGrid);
    }
    for edges in time_edges_seconds.windows(2) {
        if !edges[0].is_finite() || !edges[1].is_finite() || edges[1] <= edges[0] {
            return Err(VisibilityError::InvalidGrid);
        }
        if !(edges[1] - edges[0]).is_finite() {
            return Err(VisibilityError::NonFiniteArithmetic);
        }
    }
    if interval_rates_s_inverse
        .iter()
        .any(|rate| !rate.is_finite() || *rate < 0.0)
    {
        return Err(VisibilityError::InvalidRate);
    }
    Ok(())
}
