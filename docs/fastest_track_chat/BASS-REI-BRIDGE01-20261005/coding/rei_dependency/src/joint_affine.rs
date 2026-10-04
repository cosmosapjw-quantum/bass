//! Outward-rounded differences of two affine enclosures over one parent box.
//!
//! The caller must separately prove that each map's nonlinear residual lies in
//! its supplied remainder. This module only combines those inputs; it does not
//! certify a physical discrete map or change a historical acceptance decision.

use crate::ForwardError;

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct ClosedInterval {
    pub lower: f64,
    pub upper: f64,
}

impl ClosedInterval {
    pub fn new(lower: f64, upper: f64) -> Result<Self, ForwardError> {
        if !lower.is_finite() || !upper.is_finite() {
            return Err(ForwardError::InvalidInput("JOINT_INTERVAL_NONFINITE"));
        }
        if lower > upper {
            return Err(ForwardError::InvalidInput("JOINT_INTERVAL_REVERSED"));
        }
        Ok(Self { lower, upper })
    }

    pub fn point(value: f64) -> Result<Self, ForwardError> {
        Self::new(value, value)
    }

    pub fn contains(self, value: f64) -> bool {
        value.is_finite() && self.lower <= value && value <= self.upper
    }

    fn is_zero(self) -> bool {
        self.lower == 0.0 && self.upper == 0.0
    }

    fn checked(self) -> Result<Self, ForwardError> {
        Self::new(self.lower, self.upper)
    }

    fn add(self, other: Self) -> Result<Self, ForwardError> {
        if self.is_zero() {
            return Ok(other);
        }
        if other.is_zero() {
            return Ok(self);
        }
        Ok(Self {
            lower: down(self.lower + other.lower)?,
            upper: up(self.upper + other.upper)?,
        })
    }

    fn sub(self, other: Self) -> Result<Self, ForwardError> {
        if other.is_zero() {
            return Ok(self);
        }
        if self.is_zero() {
            return Ok(Self {
                lower: -other.upper,
                upper: -other.lower,
            });
        }
        // Equal point operands are identical binary64 values, so their exact
        // difference is zero. Intervals with width are never cancelled here.
        if self.lower == self.upper && other.lower == other.upper && self.lower == other.lower {
            return Self::point(0.0);
        }
        Ok(Self {
            lower: down(self.lower - other.upper)?,
            upper: up(self.upper - other.lower)?,
        })
    }

    fn mul(self, other: Self) -> Result<Self, ForwardError> {
        if self.is_zero() || other.is_zero() {
            return Self::point(0.0);
        }
        let products = [
            self.lower * other.lower,
            self.lower * other.upper,
            self.upper * other.lower,
            self.upper * other.upper,
        ];
        if products.iter().any(|x| !x.is_finite()) {
            return Err(ForwardError::InvalidInput("JOINT_ARITHMETIC_OVERFLOW"));
        }
        let lower = products.iter().copied().fold(f64::INFINITY, f64::min);
        let upper = products.iter().copied().fold(f64::NEG_INFINITY, f64::max);
        Ok(Self {
            lower: down(lower)?,
            upper: up(upper)?,
        })
    }
}

fn down(value: f64) -> Result<f64, ForwardError> {
    if !value.is_finite() {
        return Err(ForwardError::InvalidInput("JOINT_ARITHMETIC_OVERFLOW"));
    }
    let bound = value.next_down();
    if !bound.is_finite() {
        return Err(ForwardError::InvalidInput("JOINT_ARITHMETIC_OVERFLOW"));
    }
    Ok(bound)
}

fn up(value: f64) -> Result<f64, ForwardError> {
    if !value.is_finite() {
        return Err(ForwardError::InvalidInput("JOINT_ARITHMETIC_OVERFLOW"));
    }
    let bound = value.next_up();
    if !bound.is_finite() {
        return Err(ForwardError::InvalidInput("JOINT_ARITHMETIC_OVERFLOW"));
    }
    Ok(bound)
}

/// Intervals for deviations from a single, caller-chosen reference state.
/// Every coordinate in both images must refer to this same state.
#[derive(Clone, Copy, Debug)]
pub struct JointParent<'a> {
    pub coordinate_id: &'a str,
    pub deviations: &'a [ClosedInterval],
}

/// `offset + sum(coefficients[i] * deviation[i]) + remainder`.
///
/// Coefficients and offset are exact binary64 input values for this arithmetic
/// contract. Any error in their derivation must be included in `remainder`.
#[derive(Clone, Copy, Debug)]
pub struct AffineEnclosure<'a> {
    pub parent_id: &'a str,
    pub offset: f64,
    pub coefficients: &'a [f64],
    pub remainder: ClosedInterval,
}

/// Enclose `full(x) - two_half(x)` with both maps evaluated at the same `x`.
/// The independently certified map remainders are treated as uncorrelated.
pub fn joint_affine_difference(
    parent: JointParent<'_>,
    full: AffineEnclosure<'_>,
    two_half: AffineEnclosure<'_>,
) -> Result<ClosedInterval, ForwardError> {
    if parent.coordinate_id.is_empty()
        || parent.coordinate_id != full.parent_id
        || parent.coordinate_id != two_half.parent_id
    {
        return Err(ForwardError::InvalidInput("JOINT_PARENT_ID_MISMATCH"));
    }
    if parent.deviations.is_empty()
        || parent.deviations.len() != full.coefficients.len()
        || parent.deviations.len() != two_half.coefficients.len()
    {
        return Err(ForwardError::InvalidInput(
            "JOINT_PARENT_DIMENSION_MISMATCH",
        ));
    }
    for deviation in parent.deviations {
        deviation.checked()?;
    }
    full.remainder.checked()?;
    two_half.remainder.checked()?;
    let mut difference =
        ClosedInterval::point(full.offset)?.sub(ClosedInterval::point(two_half.offset)?)?;
    for (index, deviation) in parent.deviations.iter().enumerate() {
        let coefficient = ClosedInterval::point(full.coefficients[index])?
            .sub(ClosedInterval::point(two_half.coefficients[index])?)?;
        difference = difference.add(coefficient.mul(*deviation)?)?;
    }
    difference.add(full.remainder.sub(two_half.remainder)?)
}

/// A strict synthetic local-error decision. `false` never writes a state.
pub fn below_strict_error_limit(
    difference: ClosedInterval,
    limit: f64,
) -> Result<bool, ForwardError> {
    difference.checked()?;
    if !limit.is_finite() || limit < 0.0 {
        return Err(ForwardError::InvalidInput("JOINT_ERROR_LIMIT_INVALID"));
    }
    Ok(difference.lower > -limit && difference.upper < limit)
}
