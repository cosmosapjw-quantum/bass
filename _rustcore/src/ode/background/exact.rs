//! Exact dyadic arithmetic for RF-02C event-polynomial isolation.
//!
//! Each finite IEEE-754 binary64 value is decoded from its bits and represented
//! as a reduced rational without a decimal or binary64 round trip. Polynomial
//! division, square-free decomposition, and Sturm counting therefore operate
//! over Q and never infer a multiple root from sampled signs.

use num_bigint::BigInt;
use num_rational::BigRational;
use num_traits::{One, Signed, ToPrimitive, Zero};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum ExactArithmeticError {
    NonfiniteCoefficient,
    ZeroDivisor,
    InexactDivision,
    RootIsolationFailure,
    RootRepresentationFailure,
}

pub(crate) fn f64_bits_to_rational(bits: u64) -> Result<BigRational, ExactArithmeticError> {
    let sign_is_negative = bits >> 63 != 0;
    let exponent_bits = ((bits >> 52) & 0x7ff) as i32;
    let fraction_bits = bits & ((1_u64 << 52) - 1);

    if exponent_bits == 0x7ff {
        return Err(ExactArithmeticError::NonfiniteCoefficient);
    }
    if exponent_bits == 0 && fraction_bits == 0 {
        return Ok(BigRational::from_integer(BigInt::zero()));
    }

    let (significand, exponent) = if exponent_bits == 0 {
        (fraction_bits, -1074)
    } else {
        (fraction_bits | (1_u64 << 52), exponent_bits - 1023 - 52)
    };
    let mut numerator = BigInt::from(significand);
    if sign_is_negative {
        numerator = -numerator;
    }
    if exponent >= 0 {
        numerator <<= exponent as usize;
        Ok(BigRational::from_integer(numerator))
    } else {
        let denominator = BigInt::one() << (-exponent) as usize;
        Ok(BigRational::new(numerator, denominator))
    }
}

fn rational_integer(value: i64) -> BigRational {
    BigRational::from_integer(BigInt::from(value))
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct ExactPolynomial {
    /// Ascending coefficients after exact leading-zero trimming.
    coefficients: Vec<BigRational>,
}

impl ExactPolynomial {
    pub(crate) fn from_f64_bits(bits: &[u64]) -> Result<Self, ExactArithmeticError> {
        let coefficients = bits
            .iter()
            .copied()
            .map(f64_bits_to_rational)
            .collect::<Result<Vec<_>, _>>()?;
        Ok(Self::from_coefficients(coefficients))
    }

    pub(crate) fn from_coefficients(mut coefficients: Vec<BigRational>) -> Self {
        while coefficients.last().is_some_and(Zero::is_zero) {
            coefficients.pop();
        }
        Self { coefficients }
    }

    pub(crate) fn zero() -> Self {
        Self {
            coefficients: Vec::new(),
        }
    }

    pub(crate) fn constant(value: BigRational) -> Self {
        Self::from_coefficients(vec![value])
    }

    pub(crate) fn coefficients(&self) -> &[BigRational] {
        &self.coefficients
    }

    pub(crate) fn is_zero(&self) -> bool {
        self.coefficients.is_empty()
    }

    pub(crate) fn is_one(&self) -> bool {
        self.coefficients.len() == 1 && self.coefficients[0].is_one()
    }

    pub(crate) fn degree(&self) -> Option<usize> {
        self.coefficients.len().checked_sub(1)
    }

    fn leading(&self) -> Option<&BigRational> {
        self.coefficients.last()
    }

    pub(crate) fn derivative(&self) -> Self {
        let coefficients = self
            .coefficients
            .iter()
            .enumerate()
            .skip(1)
            .map(|(degree, coefficient)| coefficient * BigInt::from(degree))
            .collect();
        Self::from_coefficients(coefficients)
    }

    pub(crate) fn evaluate(&self, theta: &BigRational) -> BigRational {
        self.coefficients.iter().rev().fold(
            BigRational::from_integer(BigInt::zero()),
            |value, coefficient| value * theta + coefficient,
        )
    }

    pub(crate) fn add(&self, rhs: &Self) -> Self {
        let count = self.coefficients.len().max(rhs.coefficients.len());
        let coefficients = (0..count)
            .map(|index| {
                self.coefficients
                    .get(index)
                    .cloned()
                    .unwrap_or_else(BigRational::zero)
                    + rhs
                        .coefficients
                        .get(index)
                        .cloned()
                        .unwrap_or_else(BigRational::zero)
            })
            .collect();
        Self::from_coefficients(coefficients)
    }

    pub(crate) fn sub(&self, rhs: &Self) -> Self {
        self.add(&rhs.neg())
    }

    pub(crate) fn neg(&self) -> Self {
        Self::from_coefficients(
            self.coefficients
                .iter()
                .map(|coefficient| -coefficient)
                .collect(),
        )
    }

    pub(crate) fn mul(&self, rhs: &Self) -> Self {
        if self.is_zero() || rhs.is_zero() {
            return Self::zero();
        }
        let mut coefficients =
            vec![BigRational::zero(); self.coefficients.len() + rhs.coefficients.len() - 1];
        for (left_degree, left) in self.coefficients.iter().enumerate() {
            for (right_degree, right) in rhs.coefficients.iter().enumerate() {
                coefficients[left_degree + right_degree] += left * right;
            }
        }
        Self::from_coefficients(coefficients)
    }

    pub(crate) fn monic(&self) -> Self {
        let Some(leading) = self.leading() else {
            return Self::zero();
        };
        Self::from_coefficients(
            self.coefficients
                .iter()
                .map(|coefficient| coefficient / leading)
                .collect(),
        )
    }

    pub(crate) fn div_rem(&self, divisor: &Self) -> Result<(Self, Self), ExactArithmeticError> {
        let Some(divisor_degree) = divisor.degree() else {
            return Err(ExactArithmeticError::ZeroDivisor);
        };
        let mut remainder = self.clone();
        let mut quotient = match self.degree() {
            Some(degree) if degree >= divisor_degree => {
                vec![BigRational::zero(); degree - divisor_degree + 1]
            }
            _ => return Ok((Self::zero(), remainder)),
        };
        let divisor_leading = divisor.leading().expect("nonzero divisor").clone();

        while let Some(remainder_degree) = remainder.degree() {
            if remainder_degree < divisor_degree {
                break;
            }
            let degree = remainder_degree - divisor_degree;
            let scale = remainder.leading().expect("nonzero remainder") / &divisor_leading;
            quotient[degree] += &scale;
            let mut subtraction = vec![BigRational::zero(); degree + divisor.coefficients.len()];
            for (index, coefficient) in divisor.coefficients.iter().enumerate() {
                subtraction[degree + index] = coefficient * &scale;
            }
            remainder = remainder.sub(&Self::from_coefficients(subtraction));
        }
        Ok((Self::from_coefficients(quotient), remainder))
    }

    pub(crate) fn exact_div(&self, divisor: &Self) -> Result<Self, ExactArithmeticError> {
        let (quotient, remainder) = self.div_rem(divisor)?;
        if remainder.is_zero() {
            Ok(quotient)
        } else {
            Err(ExactArithmeticError::InexactDivision)
        }
    }

    pub(crate) fn gcd(&self, rhs: &Self) -> Result<Self, ExactArithmeticError> {
        let mut left = self.clone();
        let mut right = rhs.clone();
        while !right.is_zero() {
            let (_, remainder) = left.div_rem(&right)?;
            left = right;
            right = remainder;
        }
        Ok(left.monic())
    }

    /// Yun's characteristic-zero square-free decomposition. Each returned
    /// factor is monic and paired with the multiplicity of all of its roots.
    pub(crate) fn square_free_factors(&self) -> Result<Vec<(Self, usize)>, ExactArithmeticError> {
        if self.degree().is_none_or(|degree| degree == 0) {
            return Ok(Vec::new());
        }
        let polynomial = self.monic();
        let mut repeated = polynomial.gcd(&polynomial.derivative())?;
        let mut remaining = polynomial.exact_div(&repeated)?;
        let mut multiplicity = 1usize;
        let mut factors = Vec::new();

        while !remaining.is_one() {
            let shared = remaining.gcd(&repeated)?;
            let factor = remaining.exact_div(&shared)?.monic();
            if !factor.is_one() {
                factors.push((factor, multiplicity));
            }
            remaining = shared;
            repeated = repeated.exact_div(&remaining)?;
            multiplicity += 1;
        }
        Ok(factors)
    }

    pub(crate) fn sturm_sequence(&self) -> Result<Vec<Self>, ExactArithmeticError> {
        if self.is_zero() {
            return Ok(Vec::new());
        }
        let mut sequence = vec![self.clone(), self.derivative()];
        if sequence[1].is_zero() {
            sequence.pop();
            return Ok(sequence);
        }
        loop {
            let count = sequence.len();
            let (_, remainder) = sequence[count - 2].div_rem(&sequence[count - 1])?;
            if remainder.is_zero() {
                break;
            }
            sequence.push(remainder.neg());
        }
        Ok(sequence)
    }
}

fn rational_sign(value: &BigRational) -> i8 {
    if value.is_positive() {
        1
    } else if value.is_negative() {
        -1
    } else {
        0
    }
}

fn sturm_variations(sequence: &[ExactPolynomial], point: &BigRational) -> usize {
    let mut previous = 0i8;
    let mut variations = 0usize;
    for polynomial in sequence {
        let sign = rational_sign(&polynomial.evaluate(point));
        if sign == 0 {
            continue;
        }
        if previous != 0 && sign != previous {
            variations += 1;
        }
        previous = sign;
    }
    variations
}

fn sturm_root_count(
    sequence: &[ExactPolynomial],
    lower: &BigRational,
    upper: &BigRational,
) -> Result<usize, ExactArithmeticError> {
    sturm_variations(sequence, lower)
        .checked_sub(sturm_variations(sequence, upper))
        .ok_or(ExactArithmeticError::RootIsolationFailure)
}

#[derive(Clone, Debug)]
struct RationalRootBracket {
    lower: BigRational,
    upper: BigRational,
    exact: Option<BigRational>,
    multiplicity: usize,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) struct RepresentedExactRoot {
    pub theta_bits: u64,
    pub multiplicity: usize,
    /// Signs as theta increases from zero to one. Zero denotes the exterior
    /// side of an owned endpoint root.
    pub left_sign: i8,
    pub right_sign: i8,
}

fn floats_are_same_or_adjacent(lower: &BigRational, upper: &BigRational) -> bool {
    let (Some(lower_float), Some(upper_float)) = (lower.to_f64(), upper.to_f64()) else {
        return false;
    };
    if !(lower_float.is_finite() && upper_float.is_finite()) {
        return false;
    }
    lower_float.to_bits().abs_diff(upper_float.to_bits()) <= 1
}

fn refine_one_root(
    factor: &ExactPolynomial,
    sequence: &[ExactPolynomial],
    mut lower: BigRational,
    mut upper: BigRational,
    multiplicity: usize,
) -> Result<RationalRootBracket, ExactArithmeticError> {
    let two = rational_integer(2);
    for _ in 0..4096 {
        let midpoint = (&lower + &upper) / &two;
        if factor.evaluate(&midpoint).is_zero() {
            return Ok(RationalRootBracket {
                lower,
                upper,
                exact: Some(midpoint),
                multiplicity,
            });
        }
        if floats_are_same_or_adjacent(&lower, &upper) {
            return Ok(RationalRootBracket {
                lower,
                upper,
                exact: None,
                multiplicity,
            });
        }
        let left_count = sturm_root_count(sequence, &lower, &midpoint)?;
        match left_count {
            0 => lower = midpoint,
            1 => upper = midpoint,
            _ => return Err(ExactArithmeticError::RootIsolationFailure),
        }
    }
    Err(ExactArithmeticError::RootIsolationFailure)
}

#[allow(clippy::too_many_arguments)]
fn isolate_factor_recursive(
    factor: &ExactPolynomial,
    sequence: &[ExactPolynomial],
    lower: BigRational,
    upper: BigRational,
    root_count: usize,
    multiplicity: usize,
    output: &mut Vec<RationalRootBracket>,
    depth: usize,
) -> Result<(), ExactArithmeticError> {
    if root_count == 0 {
        return Ok(());
    }
    if root_count == 1 {
        output.push(refine_one_root(
            factor,
            sequence,
            lower,
            upper,
            multiplicity,
        )?);
        return Ok(());
    }
    if depth >= 4096 {
        return Err(ExactArithmeticError::RootIsolationFailure);
    }
    let midpoint = (&lower + &upper) / rational_integer(2);
    let left_count = sturm_root_count(sequence, &lower, &midpoint)?;
    let right_count = root_count
        .checked_sub(left_count)
        .ok_or(ExactArithmeticError::RootIsolationFailure)?;
    isolate_factor_recursive(
        factor,
        sequence,
        lower,
        midpoint.clone(),
        left_count,
        multiplicity,
        output,
        depth + 1,
    )?;
    isolate_factor_recursive(
        factor,
        sequence,
        midpoint,
        upper,
        right_count,
        multiplicity,
        output,
        depth + 1,
    )
}

fn next_down_nonnegative(value: f64) -> f64 {
    if value <= 0.0 {
        0.0
    } else {
        f64::from_bits(value.to_bits() - 1)
    }
}

fn next_up_at_most_one(value: f64) -> f64 {
    if value >= 1.0 {
        1.0
    } else if value == 0.0 {
        f64::from_bits(1)
    } else {
        f64::from_bits(value.to_bits() + 1)
    }
}

fn represented_root(
    polynomial: &ExactPolynomial,
    bracket: &RationalRootBracket,
) -> Result<u64, ExactArithmeticError> {
    let approximate = bracket
        .exact
        .as_ref()
        .and_then(ToPrimitive::to_f64)
        .or_else(|| ((&bracket.lower + &bracket.upper) / rational_integer(2)).to_f64())
        .ok_or(ExactArithmeticError::RootRepresentationFailure)?;
    let mut candidates = vec![
        approximate,
        next_down_nonnegative(approximate),
        next_up_at_most_one(approximate),
    ];
    if bracket.exact.is_none() {
        candidates.push(
            bracket
                .lower
                .to_f64()
                .ok_or(ExactArithmeticError::RootRepresentationFailure)?,
        );
        candidates.push(
            bracket
                .upper
                .to_f64()
                .ok_or(ExactArithmeticError::RootRepresentationFailure)?,
        );
    }
    candidates.retain(|candidate| candidate.is_finite() && (0.0..=1.0).contains(candidate));
    candidates.sort_by_key(|candidate| candidate.to_bits());
    candidates.dedup_by_key(|candidate| candidate.to_bits());

    let mut best: Option<(BigRational, u64)> = None;
    for candidate in candidates {
        let candidate_bits = candidate.to_bits();
        let exact_candidate = f64_bits_to_rational(candidate_bits)?;
        let residual = polynomial.evaluate(&exact_candidate).abs();
        match &best {
            None => best = Some((residual, candidate_bits)),
            Some((best_residual, best_bits))
                if residual < *best_residual
                    || (residual == *best_residual && candidate_bits < *best_bits) =>
            {
                best = Some((residual, candidate_bits));
            }
            _ => {}
        }
    }
    best.map(|(_, bits)| bits)
        .ok_or(ExactArithmeticError::RootRepresentationFailure)
}

fn bracket_side_signs(
    polynomial: &ExactPolynomial,
    lower: &BigRational,
    upper: &BigRational,
) -> Result<(i8, i8), ExactArithmeticError> {
    // A non-exact isolating bracket has non-root rational endpoints.  Their
    // signs are the exact open-interval signs adjacent to the sole enclosed
    // root. Sampling fixed fractions inside the bracket is unsound because a
    // root need not lie between those two samples.
    let left = rational_sign(&polynomial.evaluate(lower));
    let right = rational_sign(&polynomial.evaluate(upper));
    if left == 0 || right == 0 {
        Err(ExactArithmeticError::RootIsolationFailure)
    } else {
        Ok((left, right))
    }
}

fn exact_root_side_signs(
    polynomial: &ExactPolynomial,
    root: &BigRational,
    multiplicity: usize,
) -> Result<(i8, i8), ExactArithmeticError> {
    let mut first_nonzero_derivative = polynomial.clone();
    for _ in 0..multiplicity {
        first_nonzero_derivative = first_nonzero_derivative.derivative();
    }
    let right_sign = rational_sign(&first_nonzero_derivative.evaluate(root));
    if right_sign == 0 {
        return Err(ExactArithmeticError::RootIsolationFailure);
    }
    let left_sign = if multiplicity % 2 == 0 {
        right_sign
    } else {
        -right_sign
    };
    Ok((left_sign, right_sign))
}

/// Exact square-free/Sturm isolation of all roots on the closed unit interval.
/// Root ordering is increasing in carrier theta; integration-direction ordering
/// is applied by the event layer.
pub(crate) fn isolate_unit_roots(
    polynomial: &ExactPolynomial,
) -> Result<Vec<RepresentedExactRoot>, ExactArithmeticError> {
    if polynomial.is_zero() {
        return Ok(Vec::new());
    }
    let zero = rational_integer(0);
    let one = rational_integer(1);
    let linear_zero = ExactPolynomial::from_coefficients(vec![zero.clone(), one.clone()]);
    let linear_one = ExactPolynomial::from_coefficients(vec![-one.clone(), one.clone()]);
    let mut interior = polynomial.clone();
    let mut brackets = Vec::new();

    let mut zero_multiplicity = 0usize;
    while !interior.is_zero() && interior.evaluate(&zero).is_zero() {
        interior = interior.exact_div(&linear_zero)?;
        zero_multiplicity += 1;
    }
    if zero_multiplicity > 0 {
        brackets.push(RationalRootBracket {
            lower: zero.clone(),
            upper: one.clone(),
            exact: Some(zero.clone()),
            multiplicity: zero_multiplicity,
        });
    }

    let mut one_multiplicity = 0usize;
    while !interior.is_zero() && interior.evaluate(&one).is_zero() {
        interior = interior.exact_div(&linear_one)?;
        one_multiplicity += 1;
    }

    for (factor, multiplicity) in interior.square_free_factors()? {
        let sequence = factor.sturm_sequence()?;
        let count = sturm_root_count(&sequence, &zero, &one)?;
        isolate_factor_recursive(
            &factor,
            &sequence,
            zero.clone(),
            one.clone(),
            count,
            multiplicity,
            &mut brackets,
            0,
        )?;
    }
    if one_multiplicity > 0 {
        brackets.push(RationalRootBracket {
            lower: zero.clone(),
            upper: one.clone(),
            exact: Some(one.clone()),
            multiplicity: one_multiplicity,
        });
    }

    let mut roots = Vec::with_capacity(brackets.len());
    for bracket in brackets {
        let theta_bits = represented_root(polynomial, &bracket)?;
        let theta = f64::from_bits(theta_bits);
        let local_signs = match &bracket.exact {
            Some(exact) => exact_root_side_signs(polynomial, exact, bracket.multiplicity)?,
            None => bracket_side_signs(polynomial, &bracket.lower, &bracket.upper)?,
        };
        let (left_sign, right_sign) = if theta == 0.0 {
            (0, local_signs.1)
        } else if theta == 1.0 {
            (local_signs.0, 0)
        } else {
            local_signs
        };
        roots.push(RepresentedExactRoot {
            theta_bits,
            multiplicity: bracket.multiplicity,
            left_sign,
            right_sign,
        });
    }
    roots.sort_by_key(|root| root.theta_bits);
    if roots
        .windows(2)
        .any(|pair| pair[0].theta_bits == pair[1].theta_bits)
    {
        return Err(ExactArithmeticError::RootRepresentationFailure);
    }
    Ok(roots)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rf02c_exact_f64_to_dyadic_conversion_preserves_bits() {
        let fixtures = [0.0, -0.0, 0.5, -0.25, f64::from_bits(1), f64::MAX];
        for value in fixtures {
            let exact = f64_bits_to_rational(value.to_bits()).unwrap();
            assert_eq!(exact.to_f64(), Some(value));
        }
        assert_eq!(
            f64_bits_to_rational(f64::INFINITY.to_bits()),
            Err(ExactArithmeticError::NonfiniteCoefficient)
        );
    }

    #[test]
    fn rf02c_exact_polynomial_trims_and_evaluates_without_rounding() {
        let polynomial = ExactPolynomial::from_f64_bits(&[
            0.25f64.to_bits(),
            (-1.0f64).to_bits(),
            1.0f64.to_bits(),
            0.0f64.to_bits(),
        ])
        .unwrap();
        assert_eq!(polynomial.degree(), Some(2));
        let half = f64_bits_to_rational(0.5f64.to_bits()).unwrap();
        assert!(polynomial.evaluate(&half).is_zero());
        assert_eq!(polynomial.derivative().degree(), Some(1));
        assert!(!polynomial.is_zero());
    }

    #[test]
    fn rf02c_square_free_and_sturm_recover_endpoint_and_multiple_roots() {
        let polynomial = ExactPolynomial::from_f64_bits(&[
            0.0f64.to_bits(),
            0.25f64.to_bits(),
            (-1.0f64).to_bits(),
            1.0f64.to_bits(),
        ])
        .unwrap();
        let roots = isolate_unit_roots(&polynomial).unwrap();
        assert_eq!(roots.len(), 2);
        assert_eq!(roots[0].theta_bits, 0.0f64.to_bits());
        assert_eq!(roots[0].multiplicity, 1);
        assert_eq!(roots[1].theta_bits, 0.5f64.to_bits());
        assert_eq!(roots[1].multiplicity, 2);
    }
}
