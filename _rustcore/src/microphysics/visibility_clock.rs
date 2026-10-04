//! Explicit ray-clock conversion for a supplied piecewise-constant normal rate.
//!
//! This module changes integration coordinates, not chemistry or frames. Input
//! rates already include the directional Doppler factor once. In conformal
//! seconds dt = a d_eta; for conformal length chi = c eta, dt = (a/c) d_chi.
//! Proper electron densities must not receive another a^-3 factor here.

use super::visibility::{integrate_visibility, VisibilityError, VisibilityResult, C_M_S};

/// Units of the supplied increasing ray coordinate.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum RayClock {
    NormalSeconds,
    ConformalSeconds,
    ConformalLengthMeters,
}

/// Explicit coordinate edges and one dimensionless scale factor per interval.
///
/// Each normal rate is frozen on one physical interval. `scale_factors` are
/// finite positive constants on those intervals. A caller with varying a may
/// instead supply the exact ratio a_eff = Delta t / Delta eta. This preserves
/// integrated depth for the frozen normal-rate surrogate, not for an arbitrary
/// varying true rate. Midpoint/endpoint a values are not asserted exact.
/// This API does not infer a(t), time origins, or edge conversions.
#[derive(Clone, Copy, Debug)]
pub enum RayClockGrid<'a> {
    NormalSeconds { edges_seconds: &'a [f64] },
    ConformalSeconds { edges_seconds: &'a [f64], scale_factors: &'a [f64] },
    ConformalLengthMeters { edges_meters: &'a [f64], scale_factors: &'a [f64] },
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum ClockVisibilityError {
    ScaleFactorCountMismatch,
    InvalidScaleFactor,
    /// Overflow or loss to zero of a strictly positive converted quantity.
    UnrepresentableConversion,
    Visibility(VisibilityError),
}

impl From<VisibilityError> for ClockVisibilityError {
    fn from(error: VisibilityError) -> Self { Self::Visibility(error) }
}

/// Clock metadata and auditable conversion of the same supplied physical cells.
#[derive(Clone, Debug)]
pub struct ClockVisibilitySchedule {
    pub clock: RayClock,
    /// dt/d(clock): dimensionless for second clocks, s/m for conformal length.
    pub normal_seconds_per_clock_unit: Vec<f64>,
    /// Positive physical normal-time widths represented by the clock cells.
    pub normal_interval_seconds: Vec<f64>,
    /// q_t * dt/d(clock), per coordinate second or meter as identified by clock.
    pub interval_rates_per_clock_unit: Vec<f64>,
    pub visibility: VisibilityResult,
}

/// Integrate the same frozen normal rates in an explicitly identified clock.
///
/// `normal_rates_s_inverse` must already include D exactly once, as produced by
/// ElectronState or the typed REI bridge. The rate factors are 1, a, and a/c for
/// normal seconds, conformal seconds, and conformal meters respectively. The
/// existing host integral owns increasing-edge, rate, observer-tail validation,
/// stable thin-cell probabilities, and the finite-interval mass convention.
/// Conversion overflow and a positive value underflowing to zero are errors.
/// No frame factor, scale dilution, or finite-temperature certificate is added.
pub fn integrate_clock_visibility(
    grid: RayClockGrid<'_>,
    normal_rates_s_inverse: &[f64],
    observer_optical_depth: f64,
) -> Result<ClockVisibilitySchedule, ClockVisibilityError> {
    let (clock, edges, factors) = match grid {
        RayClockGrid::NormalSeconds { edges_seconds } =>
            (RayClock::NormalSeconds, edges_seconds, None),
        RayClockGrid::ConformalSeconds { edges_seconds, scale_factors } =>
            (RayClock::ConformalSeconds, edges_seconds, Some(scale_factors)),
        RayClockGrid::ConformalLengthMeters { edges_meters, scale_factors } =>
            (RayClock::ConformalLengthMeters, edges_meters, Some(scale_factors)),
    };
    if let Some(scale_factors) = factors {
        if scale_factors.len() != normal_rates_s_inverse.len() {
            return Err(ClockVisibilityError::ScaleFactorCountMismatch);
        }
        if scale_factors.iter().any(|a| !a.is_finite() || *a <= 0.0) {
            return Err(ClockVisibilityError::InvalidScaleFactor);
        }
    }
    // Validate before conversion: an invalid tiny negative rate must not become
    // negative zero through underflow and pass the downstream rate validator.
    if normal_rates_s_inverse.iter().any(|q| !q.is_finite() || *q < 0.0) {
        return Err(VisibilityError::InvalidRate.into());
    }
    let mut normal_seconds_per_clock_unit = Vec::with_capacity(normal_rates_s_inverse.len());
    let mut interval_rates_per_clock_unit = Vec::with_capacity(normal_rates_s_inverse.len());
    for (i, &q) in normal_rates_s_inverse.iter().enumerate() {
        let scale = match clock {
            RayClock::NormalSeconds => 1.0,
            RayClock::ConformalSeconds => factors.unwrap()[i],
            RayClock::ConformalLengthMeters => factors.unwrap()[i] / C_M_S,
        };
        let converted = q * scale;
        if !scale.is_finite() || scale <= 0.0 || !converted.is_finite()
            || (q > 0.0 && converted == 0.0)
        {
            return Err(ClockVisibilityError::UnrepresentableConversion);
        }
        normal_seconds_per_clock_unit.push(scale);
        interval_rates_per_clock_unit.push(converted);
    }
    let visibility = integrate_visibility(edges, &interval_rates_per_clock_unit, observer_optical_depth)?;
    let mut normal_interval_seconds = Vec::with_capacity(normal_rates_s_inverse.len());
    for (pair, &scale) in edges.windows(2).zip(&normal_seconds_per_clock_unit) {
        let dt = (pair[1] - pair[0]) * scale;
        if !dt.is_finite() || dt <= 0.0 {
            return Err(ClockVisibilityError::UnrepresentableConversion);
        }
        normal_interval_seconds.push(dt);
    }
    Ok(ClockVisibilitySchedule {
        clock, normal_seconds_per_clock_unit, normal_interval_seconds,
        interval_rates_per_clock_unit, visibility,
    })
}
