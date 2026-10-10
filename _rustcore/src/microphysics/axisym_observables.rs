//! Fixed-proper-time Thomson slabs.  This is not a redshift inversion or cosmic-tail model.
use super::visibility::{VisibilityError, C_M_S, SIGMA_T_M2};
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum ObserverTail {
    Unknown,
    Known(f64),
}
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct FixedTimeSlab {
    pub optical_depth: f64,
    /// Start of the finite integration bound in proper seconds.
    pub proper_start_s: f64,
    /// End of the finite integration bound in proper seconds; it can precede an unknown tail.
    pub proper_end_s: f64,
}
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct TailAwareSlab {
    pub slab: FixedTimeSlab,
    pub total_optical_depth: Option<f64>,
}
/// Externally resolved directional observed-z endpoints; no inversion is performed here.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct DirectionalRedshiftEndpoint {
    /// Unit photon direction measured in the observer frame.
    pub direction: [f64; 3],
    pub observed_redshift: f64,
    /// Emitter proper time.
    pub proper_start_s: f64,
    /// Observer proper time; hold common for a fixed-observer direction pair.
    pub proper_end_s: f64,
    /// Supplied photon energy ratio `E_observer / E_emitter` from the geodesic map.
    pub mapped_energy_ratio: f64,
}
impl DirectionalRedshiftEndpoint {
    pub fn validate(self) -> Result<(), VisibilityError> {
        let norm2: f64 = self.direction.into_iter().map(|x| x * x).sum();
        if !self.observed_redshift.is_finite()
            || self.observed_redshift <= -1.0
            || !self.proper_start_s.is_finite()
            || !self.proper_end_s.is_finite()
            || self.proper_start_s > self.proper_end_s
            || !self.mapped_energy_ratio.is_finite()
            || self.mapped_energy_ratio <= 0.0
            || !norm2.is_finite()
            || (norm2 - 1.0).abs() > 32.0 * f64::EPSILON
        {
            return Err(VisibilityError::InvalidGrid);
        }
        let expected = 1.0 / (1.0 + self.observed_redshift);
        if (self.mapped_energy_ratio - expected).abs() > 64.0 * f64::EPSILON * expected {
            return Err(VisibilityError::InvalidRate);
        }
        Ok(())
    }
}
/// Integrates `c sigma_T n_e` once over a requested proper-time interval.
pub fn fixed_time_optical_depth(
    edges_s: &[f64],
    ne_m3: &[f64],
    start_s: f64,
    end_s: f64,
) -> Result<FixedTimeSlab, VisibilityError> {
    if edges_s.len() < 2
        || ne_m3.len() + 1 != edges_s.len()
        || !start_s.is_finite()
        || !end_s.is_finite()
        || start_s > end_s
        || start_s < edges_s[0]
        || end_s > *edges_s.last().unwrap()
    {
        return Err(VisibilityError::InvalidGrid);
    }
    let mut tau = 0.;
    for (i, n) in ne_m3.iter().enumerate() {
        if !n.is_finite() || *n < 0. {
            return Err(VisibilityError::InvalidDensity);
        }
        let lo = edges_s[i];
        let hi = edges_s[i + 1];
        if !lo.is_finite() || !hi.is_finite() || hi <= lo {
            return Err(VisibilityError::InvalidGrid);
        }
        let dt = (hi.min(end_s) - lo.max(start_s)).max(0.);
        let column_m2 = n * dt;
        let increment = C_M_S * SIGMA_T_M2 * column_m2;
        if !column_m2.is_finite() || !increment.is_finite() {
            return Err(VisibilityError::NonFiniteArithmetic);
        }
        tau += increment;
    }
    if !tau.is_finite() {
        return Err(VisibilityError::NonFiniteArithmetic);
    }
    Ok(FixedTimeSlab {
        optical_depth: tau,
        proper_start_s: start_s,
        proper_end_s: end_s,
    })
}
pub fn with_observer_tail(
    slab: FixedTimeSlab,
    tail: ObserverTail,
) -> Result<TailAwareSlab, VisibilityError> {
    if !slab.optical_depth.is_finite()
        || slab.optical_depth < 0.0
        || !slab.proper_start_s.is_finite()
        || !slab.proper_end_s.is_finite()
        || slab.proper_start_s > slab.proper_end_s
    {
        return Err(VisibilityError::NonFiniteArithmetic);
    }
    match tail {
        ObserverTail::Unknown => Ok(TailAwareSlab {
            slab,
            total_optical_depth: None,
        }),
        ObserverTail::Known(x) if x.is_finite() && x >= 0. => {
            let total = slab.optical_depth + x;
            if !total.is_finite() {
                return Err(VisibilityError::NonFiniteArithmetic);
            }
            Ok(TailAwareSlab {
                slab,
                total_optical_depth: Some(total),
            })
        }
        _ => Err(VisibilityError::InvalidObserverDepth),
    }
}
