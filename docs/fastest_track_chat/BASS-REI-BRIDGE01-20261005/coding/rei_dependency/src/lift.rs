//! Preserve node_lift_operator.py validation order, including zero support.
use crate::{ForwardError, SignedLift};

pub fn positive_mass_projection(prior: &[f64], total: f64) -> Result<Vec<f64>, ForwardError> {
    if prior.iter().any(|p| !p.is_finite()) {
        return Err(ForwardError::InvalidInput("PRIOR_NOT_FINITE"));
    }
    if !total.is_finite() || total < 0.0 {
        return Err(ForwardError::InvalidInput("INVALID_TOTAL"));
    }
    if prior.iter().any(|p| *p < 0.0) {
        return Err(ForwardError::InvalidInput("NEGATIVE_PRIOR"));
    }
    if total == 0.0 {
        return Ok(vec![0.0; prior.len()]);
    }
    let s: f64 = prior.iter().sum();
    if s <= 0.0 {
        return Err(ForwardError::InfeasibleZeroPriorSupport);
    }
    // Do not repair the original module's finite-input sum overflow behavior.
    Ok(prior.iter().map(|p| p * (total / s)).collect())
}

pub fn signed_transfer_lift(rate: f64, prior: &[f64]) -> Result<SignedLift, ForwardError> {
    if prior.iter().any(|p| !p.is_finite()) {
        return Err(ForwardError::InvalidInput(
            "CONDITIONAL_MASS_PRIOR_NOT_FINITE",
        ));
    }
    let s: f64 = prior.iter().sum();
    if prior.iter().any(|p| *p < 0.0) || s <= 0.0 {
        return Err(ForwardError::InvalidInput("INVALID_CONDITIONAL_MASS_PRIOR"));
    }
    if !rate.is_finite() {
        return Err(ForwardError::InvalidInput("NONFINITE_RATE"));
    }
    let positive: Vec<_> = prior.iter().map(|p| (p / s) * rate.max(0.0)).collect();
    let negative: Vec<_> = prior.iter().map(|p| (p / s) * (-rate).max(0.0)).collect();
    let signed = positive.iter().zip(&negative).map(|(p, n)| p - n).collect();
    Ok(SignedLift {
        positive,
        negative,
        signed,
    })
}
