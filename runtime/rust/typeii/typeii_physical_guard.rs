//! Checked physical carrier for polarized Type-II collision and Kato actions.
//!
//! The generated kernels retain nine real storage components per angular node:
//! six for the real symmetric part and three for the imaginary antisymmetric
//! part of a Hermitian coherency tensor.  This is only an embedding.  The
//! physical carrier is the four-real-dimensional screen subspace satisfying
//! `J = P(e) J P(e)` at every node.

use super::typeii_polarized::{collision_generator_apply_polarized, kato_apply_polarized};

type Mat3 = [[f64; 3]; 3];

pub const DIRECTION_UNIT_TOLERANCE: f64 = 1e-10;

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum ScreenInputPolicy {
    Reject { tolerance: f64 },
    Project,
}

#[derive(Clone, Debug, PartialEq)]
pub enum PhysicalCarrierError {
    EmptyGrid,
    DirectionWeightMismatch {
        directions: usize,
        weights: usize,
    },
    DimensionMismatch {
        expected: usize,
        actual: usize,
    },
    InvalidAxis {
        axis: usize,
    },
    NonFiniteVelocity,
    SuperluminalVelocity {
        velocity: f64,
    },
    NonFiniteVelocityDerivative,
    NonFiniteDirection {
        node: usize,
        component: usize,
    },
    NonUnitDirection {
        node: usize,
        norm: f64,
        tolerance: f64,
    },
    NonFiniteWeight {
        node: usize,
    },
    NonPositiveWeight {
        node: usize,
        weight: f64,
    },
    NonFiniteState {
        index: usize,
    },
    InvalidTolerance {
        field: &'static str,
        requested: f64,
    },
    NonPhysicalScreenState {
        max_leakage: f64,
        tolerance: f64,
    },
    OperatorDimensionMismatch {
        expected: usize,
        actual: usize,
    },
    OperatorOutputNonFinite {
        index: usize,
    },
    OperatorOutputLeakage {
        max_leakage: f64,
        tolerance: f64,
    },
    ScreenProjectionArithmeticNonFinite {
        index: usize,
    },
    ScreenLeakageArithmeticNonFinite {
        index: usize,
    },
    CoherencyDiagnosticNonFinite {
        node: usize,
    },
}

#[inline]
fn mm(a: &Mat3, b: &Mat3) -> Mat3 {
    let mut out = [[0.0; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            for k in 0..3 {
                out[i][j] += a[i][k] * b[k][j];
            }
        }
    }
    out
}

#[inline]
fn projector(direction: [f64; 3]) -> Mat3 {
    let norm_squared = direction.iter().map(|value| value * value).sum::<f64>();
    let mut out = [[0.0; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            out[i][j] = if i == j { 1.0 } else { 0.0 } - direction[i] * direction[j] / norm_squared;
        }
    }
    out
}

#[inline]
fn canonicalize_direction_unchecked(direction: [f64; 3]) -> [f64; 3] {
    let norm = direction
        .iter()
        .map(|value| value * value)
        .sum::<f64>()
        .sqrt();
    [
        direction[0] / norm,
        direction[1] / norm,
        direction[2] / norm,
    ]
}

pub(crate) fn canonicalize_directions_unchecked(directions: &[[f64; 3]]) -> Vec<[f64; 3]> {
    directions
        .iter()
        .map(|&direction| canonicalize_direction_unchecked(direction))
        .collect()
}

#[inline]
fn unpack9(packed: &[f64]) -> Mat3 {
    [
        [packed[0], packed[3] + packed[8], packed[4] - packed[7]],
        [packed[3] - packed[8], packed[1], packed[5] + packed[6]],
        [packed[4] + packed[7], packed[5] - packed[6], packed[2]],
    ]
}

#[inline]
fn pack9(matrix: &Mat3) -> [f64; 9] {
    [
        matrix[0][0],
        matrix[1][1],
        matrix[2][2],
        0.5 * (matrix[0][1] + matrix[1][0]),
        0.5 * (matrix[0][2] + matrix[2][0]),
        0.5 * (matrix[1][2] + matrix[2][1]),
        0.5 * (matrix[1][2] - matrix[2][1]),
        0.5 * (matrix[2][0] - matrix[0][2]),
        0.5 * (matrix[0][1] - matrix[1][0]),
    ]
}

fn validate_directions(directions: &[[f64; 3]]) -> Result<(), PhysicalCarrierError> {
    if directions.is_empty() {
        return Err(PhysicalCarrierError::EmptyGrid);
    }
    for (node, direction) in directions.iter().enumerate() {
        for (component, value) in direction.iter().enumerate() {
            if !value.is_finite() {
                return Err(PhysicalCarrierError::NonFiniteDirection { node, component });
            }
        }
        let norm = direction
            .iter()
            .map(|value| value * value)
            .sum::<f64>()
            .sqrt();
        if !norm.is_finite() || (norm - 1.0).abs() > DIRECTION_UNIT_TOLERANCE {
            return Err(PhysicalCarrierError::NonUnitDirection {
                node,
                norm,
                tolerance: DIRECTION_UNIT_TOLERANCE,
            });
        }
    }
    Ok(())
}

fn validate_state(directions: &[[f64; 3]], state: &[f64]) -> Result<(), PhysicalCarrierError> {
    let expected = 9 * directions.len();
    if state.len() != expected {
        return Err(PhysicalCarrierError::DimensionMismatch {
            expected,
            actual: state.len(),
        });
    }
    if let Some(index) = state.iter().position(|value| !value.is_finite()) {
        return Err(PhysicalCarrierError::NonFiniteState { index });
    }
    Ok(())
}

fn validate_tolerance(field: &'static str, tolerance: f64) -> Result<(), PhysicalCarrierError> {
    if !(tolerance >= 0.0 && tolerance.is_finite()) {
        return Err(PhysicalCarrierError::InvalidTolerance {
            field,
            requested: tolerance,
        });
    }
    Ok(())
}

pub fn validate_physical_operator_inputs(
    directions: &[[f64; 3]],
    weights: &[f64],
    velocity: f64,
    axis: usize,
    state: &[f64],
) -> Result<(), PhysicalCarrierError> {
    validate_directions(directions)?;
    validate_state(directions, state)?;
    if directions.len() != weights.len() {
        return Err(PhysicalCarrierError::DirectionWeightMismatch {
            directions: directions.len(),
            weights: weights.len(),
        });
    }
    for (node, &weight) in weights.iter().enumerate() {
        if !weight.is_finite() {
            return Err(PhysicalCarrierError::NonFiniteWeight { node });
        }
        if weight <= 0.0 {
            return Err(PhysicalCarrierError::NonPositiveWeight { node, weight });
        }
    }
    if axis >= 3 {
        return Err(PhysicalCarrierError::InvalidAxis { axis });
    }
    if !velocity.is_finite() {
        return Err(PhysicalCarrierError::NonFiniteVelocity);
    }
    if velocity.abs() >= 1.0 {
        return Err(PhysicalCarrierError::SuperluminalVelocity { velocity });
    }
    Ok(())
}

pub(crate) fn project_screen_state_unchecked(directions: &[[f64; 3]], state: &[f64]) -> Vec<f64> {
    let mut out = vec![0.0; state.len()];
    for (node, &direction) in directions.iter().enumerate() {
        let p = projector(direction);
        let coherency = unpack9(&state[9 * node..9 * node + 9]);
        let projected = mm(&mm(&p, &coherency), &p);
        out[9 * node..9 * node + 9].copy_from_slice(&pack9(&projected));
    }
    out
}

pub fn project_screen_state(
    directions: &[[f64; 3]],
    state: &[f64],
) -> Result<Vec<f64>, PhysicalCarrierError> {
    validate_directions(directions)?;
    validate_state(directions, state)?;
    let projected = project_screen_state_unchecked(directions, state);
    validate_screen_projection(&projected)?;
    Ok(projected)
}

pub fn max_screen_leakage(
    directions: &[[f64; 3]],
    state: &[f64],
) -> Result<f64, PhysicalCarrierError> {
    let projected = project_screen_state(directions, state)?;
    checked_max_screen_leakage(state, &projected)
}

pub fn enforce_screen_state(
    directions: &[[f64; 3]],
    state: &[f64],
    policy: ScreenInputPolicy,
) -> Result<Vec<f64>, PhysicalCarrierError> {
    validate_directions(directions)?;
    validate_state(directions, state)?;
    let projected = project_screen_state_unchecked(directions, state);
    validate_screen_projection(&projected)?;
    match policy {
        ScreenInputPolicy::Project => Ok(projected),
        ScreenInputPolicy::Reject { tolerance } => {
            validate_tolerance("screen_input_tolerance", tolerance)?;
            let leakage = checked_max_screen_leakage(state, &projected)?;
            if leakage > tolerance {
                Err(PhysicalCarrierError::NonPhysicalScreenState {
                    max_leakage: leakage,
                    tolerance,
                })
            } else {
                Ok(projected)
            }
        }
    }
}

fn tangent_frame(direction: [f64; 3]) -> ([f64; 3], [f64; 3]) {
    let direction = canonicalize_direction_unchecked(direction);
    let mut axis = 0usize;
    if direction[1].abs() < direction[axis].abs() {
        axis = 1;
    }
    if direction[2].abs() < direction[axis].abs() {
        axis = 2;
    }
    let mut seed = [0.0; 3];
    seed[axis] = 1.0;
    let parallel = seed.iter().zip(direction).map(|(a, b)| a * b).sum::<f64>();
    let mut u = [0.0; 3];
    for i in 0..3 {
        u[i] = seed[i] - parallel * direction[i];
    }
    let norm = u.iter().map(|value| value * value).sum::<f64>().sqrt();
    for value in &mut u {
        *value /= norm;
    }
    let v = [
        direction[1] * u[2] - direction[2] * u[1],
        direction[2] * u[0] - direction[0] * u[2],
        direction[0] * u[1] - direction[1] * u[0],
    ];
    (u, v)
}

fn bilinear(left: [f64; 3], matrix: &Mat3, right: [f64; 3]) -> f64 {
    let mut value = 0.0;
    for i in 0..3 {
        for j in 0..3 {
            value += left[i] * matrix[i][j] * right[j];
        }
    }
    value
}

/// Minimum eigenvalue of the physical two-by-two Hermitian coherency matrix.
/// This is a diagnostic for tested states, not a generic positivity theorem.
pub fn minimum_coherency_eigenvalue(
    directions: &[[f64; 3]],
    state: &[f64],
) -> Result<f64, PhysicalCarrierError> {
    validate_directions(directions)?;
    validate_state(directions, state)?;
    let physical = project_screen_state(directions, state)?;
    let mut minimum = f64::INFINITY;
    for (node, &direction) in directions.iter().enumerate() {
        let matrix = unpack9(&physical[9 * node..9 * node + 9]);
        let (u, v) = tangent_frame(direction);
        let a = bilinear(u, &matrix, u);
        let d = bilinear(v, &matrix, v);
        let uv = bilinear(u, &matrix, v);
        let vu = bilinear(v, &matrix, u);
        let symmetric = 0.5 * (uv + vu);
        let antisymmetric = 0.5 * (uv - vu);
        let discriminant = ((a - d) * (a - d)
            + 4.0 * (symmetric * symmetric + antisymmetric * antisymmetric))
            .sqrt();
        let eigenvalue = 0.5 * (a + d - discriminant);
        if !eigenvalue.is_finite() {
            return Err(PhysicalCarrierError::CoherencyDiagnosticNonFinite { node });
        }
        minimum = minimum.min(eigenvalue);
    }
    Ok(minimum)
}

fn validate_operator_output(expected: usize, output: &[f64]) -> Result<(), PhysicalCarrierError> {
    if output.len() != expected {
        return Err(PhysicalCarrierError::OperatorDimensionMismatch {
            expected,
            actual: output.len(),
        });
    }
    if let Some(index) = output.iter().position(|value| !value.is_finite()) {
        return Err(PhysicalCarrierError::OperatorOutputNonFinite { index });
    }
    Ok(())
}

fn validate_screen_projection(output: &[f64]) -> Result<(), PhysicalCarrierError> {
    if let Some(index) = output.iter().position(|value| !value.is_finite()) {
        return Err(PhysicalCarrierError::ScreenProjectionArithmeticNonFinite { index });
    }
    Ok(())
}

fn checked_max_screen_leakage(
    state: &[f64],
    projected: &[f64],
) -> Result<f64, PhysicalCarrierError> {
    let mut maximum = 0.0_f64;
    for (index, (value, physical)) in state.iter().zip(projected).enumerate() {
        let leakage = (value - physical).abs();
        if !leakage.is_finite() {
            return Err(PhysicalCarrierError::ScreenLeakageArithmeticNonFinite { index });
        }
        maximum = maximum.max(leakage);
    }
    Ok(maximum)
}

pub(crate) fn collision_apply_projected_unchecked(
    directions: &[[f64; 3]],
    weights: &[f64],
    velocity: f64,
    axis: usize,
    state: &[f64],
) -> Vec<f64> {
    let canonical_directions = canonicalize_directions_unchecked(directions);
    let physical = project_screen_state_unchecked(&canonical_directions, state);
    let raw = collision_generator_apply_polarized(
        &canonical_directions,
        weights,
        velocity,
        axis,
        &physical,
    );
    project_screen_state_unchecked(&canonical_directions, &raw)
}

pub(crate) fn kato_apply_projected_unchecked(
    directions: &[[f64; 3]],
    weights: &[f64],
    velocity: f64,
    velocity_derivative: f64,
    axis: usize,
    state: &[f64],
) -> Vec<f64> {
    let canonical_directions = canonicalize_directions_unchecked(directions);
    let physical = project_screen_state_unchecked(&canonical_directions, state);
    let raw = kato_apply_polarized(
        &canonical_directions,
        weights,
        velocity,
        velocity_derivative,
        axis,
        &physical,
    );
    project_screen_state_unchecked(&canonical_directions, &raw)
}

pub fn collision_apply_physical(
    directions: &[[f64; 3]],
    weights: &[f64],
    velocity: f64,
    axis: usize,
    state: &[f64],
    input_policy: ScreenInputPolicy,
    output_tolerance: f64,
) -> Result<Vec<f64>, PhysicalCarrierError> {
    validate_physical_operator_inputs(directions, weights, velocity, axis, state)?;
    validate_tolerance("screen_output_tolerance", output_tolerance)?;
    let canonical_directions = canonicalize_directions_unchecked(directions);
    let input = enforce_screen_state(&canonical_directions, state, input_policy)?;
    let raw =
        collision_generator_apply_polarized(&canonical_directions, weights, velocity, axis, &input);
    validate_operator_output(state.len(), &raw)?;
    let projected = project_screen_state_unchecked(&canonical_directions, &raw);
    validate_screen_projection(&projected)?;
    let leakage = checked_max_screen_leakage(&raw, &projected)?;
    if leakage > output_tolerance {
        return Err(PhysicalCarrierError::OperatorOutputLeakage {
            max_leakage: leakage,
            tolerance: output_tolerance,
        });
    }
    Ok(projected)
}

#[allow(clippy::too_many_arguments)]
pub fn kato_apply_physical(
    directions: &[[f64; 3]],
    weights: &[f64],
    velocity: f64,
    velocity_derivative: f64,
    axis: usize,
    state: &[f64],
    input_policy: ScreenInputPolicy,
    output_tolerance: f64,
) -> Result<Vec<f64>, PhysicalCarrierError> {
    validate_physical_operator_inputs(directions, weights, velocity, axis, state)?;
    if !velocity_derivative.is_finite() {
        return Err(PhysicalCarrierError::NonFiniteVelocityDerivative);
    }
    validate_tolerance("screen_output_tolerance", output_tolerance)?;
    let canonical_directions = canonicalize_directions_unchecked(directions);
    let input = enforce_screen_state(&canonical_directions, state, input_policy)?;
    let raw = kato_apply_polarized(
        &canonical_directions,
        weights,
        velocity,
        velocity_derivative,
        axis,
        &input,
    );
    validate_operator_output(state.len(), &raw)?;
    let projected = project_screen_state_unchecked(&canonical_directions, &raw);
    validate_screen_projection(&projected)?;
    let leakage = checked_max_screen_leakage(&raw, &projected)?;
    if leakage > output_tolerance {
        return Err(PhysicalCarrierError::OperatorOutputLeakage {
            max_leakage: leakage,
            tolerance: output_tolerance,
        });
    }
    Ok(projected)
}
