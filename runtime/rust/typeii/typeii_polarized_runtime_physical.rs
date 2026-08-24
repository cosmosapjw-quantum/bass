//! Checked adaptive actions on the four-real-dimensional physical screen carrier.

use super::typeii_collision_ap::collision_generator_apply_polarized_ap_projected_unchecked;
use super::typeii_krylov_adapt::{
    adaptive_expm_action, AdaptiveKrylovError, AdaptiveKrylovOptions, AdaptiveKrylovStats,
};
use super::typeii_physical_guard::{
    canonicalize_directions_unchecked, collision_apply_projected_unchecked, enforce_screen_state,
    kato_apply_projected_unchecked, project_screen_state, validate_physical_operator_inputs,
    PhysicalCarrierError, ScreenInputPolicy,
};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum PhysicalCollisionPolicy {
    /// Raw quadrature discretization of the continuum collision operator.
    Raw,
    /// Opt-in discrete `Q_screen Q_eq C_raw Q_eq Q_screen` correction.
    /// This is not a modification of the continuum Thomson law.
    DiscreteApCorrection,
}

#[derive(Debug, Clone)]
pub enum PhysicalPolarizedRuntimeError {
    Carrier(PhysicalCarrierError),
    Adaptive(AdaptiveKrylovError),
}

pub fn frozen_collision_step_physical_adaptive(
    directions: &[[f64; 3]],
    weights: &[f64],
    velocity: f64,
    axis: usize,
    optical_depth: f64,
    state: &[f64],
    input_policy: ScreenInputPolicy,
    options: AdaptiveKrylovOptions,
) -> Result<(Vec<f64>, AdaptiveKrylovStats), PhysicalPolarizedRuntimeError> {
    frozen_collision_step_physical_adaptive_with_policy(
        directions,
        weights,
        velocity,
        axis,
        optical_depth,
        state,
        input_policy,
        PhysicalCollisionPolicy::Raw,
        options,
    )
}

#[allow(clippy::too_many_arguments)]
pub fn frozen_collision_step_physical_adaptive_with_policy(
    directions: &[[f64; 3]],
    weights: &[f64],
    velocity: f64,
    axis: usize,
    optical_depth: f64,
    state: &[f64],
    input_policy: ScreenInputPolicy,
    collision_policy: PhysicalCollisionPolicy,
    options: AdaptiveKrylovOptions,
) -> Result<(Vec<f64>, AdaptiveKrylovStats), PhysicalPolarizedRuntimeError> {
    validate_physical_operator_inputs(directions, weights, velocity, axis, state)
        .map_err(PhysicalPolarizedRuntimeError::Carrier)?;
    let canonical_directions = canonicalize_directions_unchecked(directions);
    let input = enforce_screen_state(&canonical_directions, state, input_policy)
        .map_err(PhysicalPolarizedRuntimeError::Carrier)?;
    let action = |vector: &[f64]| match collision_policy {
        PhysicalCollisionPolicy::Raw => collision_apply_projected_unchecked(
            &canonical_directions,
            weights,
            velocity,
            axis,
            vector,
        ),
        PhysicalCollisionPolicy::DiscreteApCorrection => {
            collision_generator_apply_polarized_ap_projected_unchecked(
                &canonical_directions,
                weights,
                velocity,
                axis,
                vector,
            )
        }
    };
    let (output, stats) = adaptive_expm_action(&action, &input, optical_depth, options)
        .map_err(PhysicalPolarizedRuntimeError::Adaptive)?;
    let output = project_screen_state(&canonical_directions, &output)
        .map_err(PhysicalPolarizedRuntimeError::Carrier)?;
    Ok((output, stats))
}

#[allow(clippy::too_many_arguments)]
pub fn frozen_kato_step_physical_adaptive(
    directions: &[[f64; 3]],
    weights: &[f64],
    velocity: f64,
    velocity_derivative: f64,
    axis: usize,
    step: f64,
    state: &[f64],
    input_policy: ScreenInputPolicy,
    options: AdaptiveKrylovOptions,
) -> Result<(Vec<f64>, AdaptiveKrylovStats), PhysicalPolarizedRuntimeError> {
    validate_physical_operator_inputs(directions, weights, velocity, axis, state)
        .map_err(PhysicalPolarizedRuntimeError::Carrier)?;
    if !velocity_derivative.is_finite() {
        return Err(PhysicalPolarizedRuntimeError::Carrier(
            PhysicalCarrierError::NonFiniteVelocityDerivative,
        ));
    }
    let canonical_directions = canonicalize_directions_unchecked(directions);
    let input = enforce_screen_state(&canonical_directions, state, input_policy)
        .map_err(PhysicalPolarizedRuntimeError::Carrier)?;
    let action = |vector: &[f64]| {
        kato_apply_projected_unchecked(
            &canonical_directions,
            weights,
            velocity,
            velocity_derivative,
            axis,
            vector,
        )
    };
    let (output, stats) = adaptive_expm_action(&action, &input, step, options)
        .map_err(PhysicalPolarizedRuntimeError::Adaptive)?;
    let output = project_screen_state(&canonical_directions, &output)
        .map_err(PhysicalPolarizedRuntimeError::Carrier)?;
    Ok((output, stats))
}
