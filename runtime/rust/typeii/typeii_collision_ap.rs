//! Opt-in discrete asymptotic-preserving correction for fixed angular grids.
//!
//! The corrected discrete operator is `C_AP = (I-P) C (I-P)`, where `P` is
//! the selected discrete moving-equilibrium projector.  This removes a
//! fixed-grid equilibrium defect from the numerical lane.  It is not a change
//! to the continuum Thomson collision law, and paired rest-to-normal grids
//! remain the reference discretization.

use super::typeii_physical_guard::{
    canonicalize_directions_unchecked, project_screen_state_unchecked,
    validate_physical_operator_inputs, PhysicalCarrierError, ScreenInputPolicy,
};
use super::{typeii_collision, typeii_kato, typeii_polarized};

#[derive(Clone, Debug, PartialEq)]
pub enum DiscreteApError {
    EmptyGrid,
    DirectionWeightMismatch { directions: usize, weights: usize },
    DimensionMismatch { expected: usize, actual: usize },
    InvalidAxis { axis: usize },
    NonFiniteVelocity,
    SuperluminalVelocity { velocity: f64 },
    NonFiniteDirection { node: usize, component: usize },
    NonUnitDirection { node: usize, norm: f64 },
    NonFiniteWeight { node: usize },
    NonPositiveWeight { node: usize, weight: f64 },
    NonFiniteState { index: usize },
    DerivedProjectorNonFinite,
    OperatorOutputNonFinite { index: usize },
}

fn validate_scalar(
    directions: &[[f64; 3]],
    weights: &[f64],
    velocity: f64,
    axis: usize,
    state: Option<&[f64]>,
) -> Result<Vec<[f64; 3]>, DiscreteApError> {
    if directions.is_empty() {
        return Err(DiscreteApError::EmptyGrid);
    }
    if directions.len() != weights.len() {
        return Err(DiscreteApError::DirectionWeightMismatch {
            directions: directions.len(),
            weights: weights.len(),
        });
    }
    if axis >= 3 {
        return Err(DiscreteApError::InvalidAxis { axis });
    }
    if !velocity.is_finite() {
        return Err(DiscreteApError::NonFiniteVelocity);
    }
    if velocity.abs() >= 1.0 {
        return Err(DiscreteApError::SuperluminalVelocity { velocity });
    }
    let mut canonical_directions = Vec::with_capacity(directions.len());
    for (node, direction) in directions.iter().enumerate() {
        for (component, value) in direction.iter().enumerate() {
            if !value.is_finite() {
                return Err(DiscreteApError::NonFiniteDirection { node, component });
            }
        }
        let norm = direction
            .iter()
            .map(|value| value * value)
            .sum::<f64>()
            .sqrt();
        if !norm.is_finite() || (norm - 1.0).abs() > 1e-10 {
            return Err(DiscreteApError::NonUnitDirection { node, norm });
        }
        canonical_directions.push([
            direction[0] / norm,
            direction[1] / norm,
            direction[2] / norm,
        ]);
    }
    for (node, &weight) in weights.iter().enumerate() {
        if !weight.is_finite() {
            return Err(DiscreteApError::NonFiniteWeight { node });
        }
        if weight <= 0.0 {
            return Err(DiscreteApError::NonPositiveWeight { node, weight });
        }
    }
    if let Some(state) = state {
        if state.len() != directions.len() {
            return Err(DiscreteApError::DimensionMismatch {
                expected: directions.len(),
                actual: state.len(),
            });
        }
        if let Some(index) = state.iter().position(|value| !value.is_finite()) {
            return Err(DiscreteApError::NonFiniteState { index });
        }
    }
    Ok(canonical_directions)
}

fn scalar_projector_is_finite(factors: &typeii_kato::ProjectorFactors) -> bool {
    factors.denominator.is_finite()
        && factors.denominator > 0.0
        && factors.denominator_v.is_finite()
        && factors.r.iter().all(|value| value.is_finite())
        && factors.a.iter().all(|value| value.is_finite())
        && factors.rv.iter().all(|value| value.is_finite())
        && factors.av.iter().all(|value| value.is_finite())
}

pub fn equilibrium_state(
    directions: &[[f64; 3]],
    weights: &[f64],
    velocity: f64,
    axis: usize,
) -> Result<Vec<f64>, DiscreteApError> {
    let canonical_directions = validate_scalar(directions, weights, velocity, axis, None)?;
    let factors = typeii_kato::projector_factors(&canonical_directions, weights, velocity, axis);
    if !scalar_projector_is_finite(&factors) {
        return Err(DiscreteApError::DerivedProjectorNonFinite);
    }
    Ok(factors.r)
}

pub fn left_invariant(
    directions: &[[f64; 3]],
    weights: &[f64],
    velocity: f64,
    axis: usize,
    state: &[f64],
) -> Result<f64, DiscreteApError> {
    let canonical_directions = validate_scalar(directions, weights, velocity, axis, Some(state))?;
    let factors = typeii_kato::projector_factors(&canonical_directions, weights, velocity, axis);
    if !scalar_projector_is_finite(&factors) {
        return Err(DiscreteApError::DerivedProjectorNonFinite);
    }
    let value = factors
        .a
        .iter()
        .zip(state)
        .map(|(left, value)| left * value)
        .sum::<f64>();
    if !value.is_finite() {
        return Err(DiscreteApError::DerivedProjectorNonFinite);
    }
    Ok(value)
}

fn scalar_ap_unchecked(
    directions: &[[f64; 3]],
    weights: &[f64],
    velocity: f64,
    axis: usize,
    state: &[f64],
) -> Vec<f64> {
    let projected_input = typeii_kato::projector_apply(directions, weights, velocity, axis, state);
    let nonequilibrium: Vec<_> = state
        .iter()
        .zip(projected_input)
        .map(|(value, equilibrium)| value - equilibrium)
        .collect();
    let raw = typeii_collision::collision_generator_apply(
        directions,
        weights,
        velocity,
        axis,
        &nonequilibrium,
    );
    let projected_output = typeii_kato::projector_apply(directions, weights, velocity, axis, &raw);
    raw.into_iter()
        .zip(projected_output)
        .map(|(value, equilibrium)| value - equilibrium)
        .collect()
}

pub fn collision_generator_apply_ap(
    directions: &[[f64; 3]],
    weights: &[f64],
    velocity: f64,
    axis: usize,
    state: &[f64],
) -> Result<Vec<f64>, DiscreteApError> {
    let canonical_directions = validate_scalar(directions, weights, velocity, axis, Some(state))?;
    let factors = typeii_kato::projector_factors(&canonical_directions, weights, velocity, axis);
    if !scalar_projector_is_finite(&factors) {
        return Err(DiscreteApError::DerivedProjectorNonFinite);
    }
    let output = scalar_ap_unchecked(&canonical_directions, weights, velocity, axis, state);
    if let Some(index) = output.iter().position(|value| !value.is_finite()) {
        return Err(DiscreteApError::OperatorOutputNonFinite { index });
    }
    Ok(output)
}

/// Internal linear action in exact right-to-left order
/// `Q_screen Q_eq C_raw Q_eq Q_screen`.
pub(crate) fn collision_generator_apply_polarized_ap_projected_unchecked(
    directions: &[[f64; 3]],
    weights: &[f64],
    velocity: f64,
    axis: usize,
    state: &[f64],
) -> Vec<f64> {
    let canonical_directions = canonicalize_directions_unchecked(directions);
    let screen_input = project_screen_state_unchecked(&canonical_directions, state);
    let equilibrium_input = typeii_polarized::projector_apply_polarized(
        &canonical_directions,
        weights,
        velocity,
        axis,
        &screen_input,
    );
    let q_input: Vec<_> = screen_input
        .iter()
        .zip(equilibrium_input)
        .map(|(value, equilibrium)| value - equilibrium)
        .collect();
    let raw = typeii_polarized::collision_generator_apply_polarized(
        &canonical_directions,
        weights,
        velocity,
        axis,
        &q_input,
    );
    let equilibrium_output = typeii_polarized::projector_apply_polarized(
        &canonical_directions,
        weights,
        velocity,
        axis,
        &raw,
    );
    let q_output: Vec<_> = raw
        .iter()
        .zip(equilibrium_output)
        .map(|(value, equilibrium)| value - equilibrium)
        .collect();
    project_screen_state_unchecked(&canonical_directions, &q_output)
}

pub fn collision_generator_apply_polarized_ap_physical(
    directions: &[[f64; 3]],
    weights: &[f64],
    velocity: f64,
    axis: usize,
    state: &[f64],
    input_policy: ScreenInputPolicy,
) -> Result<Vec<f64>, PhysicalCarrierError> {
    validate_physical_operator_inputs(directions, weights, velocity, axis, state)?;
    let canonical_directions = canonicalize_directions_unchecked(directions);
    let input = super::typeii_physical_guard::enforce_screen_state(
        &canonical_directions,
        state,
        input_policy,
    )?;
    let output = collision_generator_apply_polarized_ap_projected_unchecked(
        &canonical_directions,
        weights,
        velocity,
        axis,
        &input,
    );
    if let Some(index) = output.iter().position(|value| !value.is_finite()) {
        return Err(PhysicalCarrierError::OperatorOutputNonFinite { index });
    }
    Ok(output)
}
