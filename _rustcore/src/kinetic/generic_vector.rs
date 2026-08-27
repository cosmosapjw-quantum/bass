//! Default-off generic-vector paired collision/projector/Kato host kernel.
//!
//! This is the native half of a bounded parity path.  It does not replace an
//! existing runtime route: callers must opt in explicitly at the Python host
//! boundary.  The finite carrier and normalization conventions are frozen by
//! the external BASS scientific oracle at commit
//! `58d649d438415def3e646d8eee8d0e1f3159ed7f`.

use std::fmt;

use nalgebra::{DMatrix, DVector, Matrix3, Vector3};

const FOUR_PI: f64 = 4.0 * std::f64::consts::PI;
const THOMSON_GAIN: f64 = 3.0 / (8.0 * std::f64::consts::PI);
const UNIT_DIRECTION_TOLERANCE: f64 = 3.0e-13;

#[derive(Clone, Debug, PartialEq)]
pub enum GenericVectorHostError {
    Disabled,
    InvalidInput(String),
}

impl fmt::Display for GenericVectorHostError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Disabled => formatter.write_str(
                "generic-vector host route is default-off; pass enabled=True explicitly",
            ),
            Self::InvalidInput(message) => formatter.write_str(message),
        }
    }
}

#[derive(Clone, Debug)]
pub struct ActiveGenericVectorHost {
    pub gamma: f64,
    pub alpha: f64,
    pub global_rate: f64,
    pub e_normal: Vec<[f64; 3]>,
    pub w_normal: Vec<f64>,
    pub doppler: Vec<f64>,
    pub direction_factor: Vec<f64>,
    pub node_rate: Vec<f64>,
    pub equilibrium: DVector<f64>,
    pub equilibrium_dot: DVector<f64>,
    pub normalized_left: DVector<f64>,
    pub normalized_left_dot: DVector<f64>,
    pub collision: DMatrix<f64>,
    pub projector: DMatrix<f64>,
    pub projector_dot: DMatrix<f64>,
    pub kato: DMatrix<f64>,
}

#[derive(Clone, Debug)]
pub enum GenericVectorHostDisposition {
    Active(Box<ActiveGenericVectorHost>),
    CollisionOff { state_size: usize },
}

#[derive(Clone, Debug)]
struct PairedBundle {
    e_rest: Vec<Vector3<f64>>,
    e_normal: Vec<Vector3<f64>>,
    w_normal: Vec<f64>,
    doppler: Vec<f64>,
    direction_factor: Vec<f64>,
    screen_map: Vec<Matrix3<f64>>,
    gamma: f64,
    equilibrium: DVector<f64>,
    equilibrium_dot: DVector<f64>,
    normalized_left: DVector<f64>,
    normalized_left_dot: DVector<f64>,
    projector: DMatrix<f64>,
    projector_dot: DMatrix<f64>,
    kato: DMatrix<f64>,
}

fn invalid(message: impl Into<String>) -> GenericVectorHostError {
    GenericVectorHostError::InvalidInput(message.into())
}

fn all_finite(values: impl IntoIterator<Item = f64>) -> bool {
    values.into_iter().all(f64::is_finite)
}

fn validate_grid(
    directions: &[[f64; 3]],
    weights: &[f64],
) -> Result<Vec<Vector3<f64>>, GenericVectorHostError> {
    if directions.is_empty() {
        return Err(invalid("rest quadrature must contain at least one node"));
    }
    if directions.len() != weights.len() {
        return Err(invalid(
            "rest directions and weights must have equal length",
        ));
    }
    if !all_finite(weights.iter().copied()) || weights.iter().any(|weight| *weight <= 0.0) {
        return Err(invalid("rest weights must be finite and positive"));
    }
    directions
        .iter()
        .enumerate()
        .map(|(index, direction)| {
            if !all_finite(direction.iter().copied()) {
                return Err(invalid(format!(
                    "rest direction {index} contains a non-finite component"
                )));
            }
            let vector = Vector3::new(direction[0], direction[1], direction[2]);
            if (vector.norm() - 1.0).abs() > UNIT_DIRECTION_TOLERANCE {
                return Err(invalid(format!(
                    "rest direction {index} is not unit length"
                )));
            }
            Ok(vector)
        })
        .collect()
}

fn vector3(value: [f64; 3], name: &str) -> Result<Vector3<f64>, GenericVectorHostError> {
    if !all_finite(value) {
        return Err(invalid(format!("{name} must be finite")));
    }
    Ok(Vector3::new(value[0], value[1], value[2]))
}

fn screen_projector(direction: &Vector3<f64>) -> Matrix3<f64> {
    Matrix3::identity() - direction * direction.transpose()
}

fn pack9(matrix: &Matrix3<f64>) -> [f64; 9] {
    [
        matrix[(0, 0)],
        matrix[(1, 1)],
        matrix[(2, 2)],
        0.5 * (matrix[(0, 1)] + matrix[(1, 0)]),
        0.5 * (matrix[(0, 2)] + matrix[(2, 0)]),
        0.5 * (matrix[(1, 2)] + matrix[(2, 1)]),
        0.5 * (matrix[(1, 2)] - matrix[(2, 1)]),
        0.5 * (matrix[(2, 0)] - matrix[(0, 2)]),
        0.5 * (matrix[(0, 1)] - matrix[(1, 0)]),
    ]
}

fn unpack9(values: &[f64]) -> Matrix3<f64> {
    Matrix3::new(
        values[0],
        values[3] + values[8],
        values[4] - values[7],
        values[3] - values[8],
        values[1],
        values[5] + values[6],
        values[4] + values[7],
        values[5] - values[6],
        values[2],
    )
}

fn set_packed(target: &mut DVector<f64>, node: usize, matrix: &Matrix3<f64>) {
    let packed = pack9(matrix);
    for (component, value) in packed.into_iter().enumerate() {
        target[9 * node + component] = value;
    }
}

fn build_bundle(
    e_rest_raw: &[[f64; 3]],
    w_rest: &[f64],
    beta_raw: [f64; 3],
    beta_dot_raw: [f64; 3],
) -> Result<PairedBundle, GenericVectorHostError> {
    let e_rest = validate_grid(e_rest_raw, w_rest)?;
    let beta = vector3(beta_raw, "beta")?;
    let beta_dot = vector3(beta_dot_raw, "beta_dot")?;
    let beta2 = beta.dot(&beta);
    if beta2 >= 1.0 {
        return Err(invalid("beta must satisfy |beta| < 1"));
    }

    let gamma = 1.0 / (1.0 - beta2).sqrt();
    let gamma_dot = gamma.powi(3) * beta.dot(&beta_dot);
    let h = gamma * gamma / (gamma + 1.0);
    let h_dot = gamma * (gamma + 2.0) / (gamma + 1.0).powi(2) * gamma_dot;
    let node_count = e_rest.len();
    let state_size = 9 * node_count;

    let mut e_normal = Vec::with_capacity(node_count);
    let mut doppler = Vec::with_capacity(node_count);
    let mut direction_factor = Vec::with_capacity(node_count);
    let mut w_normal = Vec::with_capacity(node_count);
    let mut screen_map = Vec::with_capacity(node_count);
    let mut equilibrium = DVector::zeros(state_size);
    let mut equilibrium_dot = DVector::zeros(state_size);
    let mut raw_left = DVector::zeros(state_size);
    let mut raw_left_dot = DVector::zeros(state_size);

    for (node, (rest_direction, &rest_weight)) in e_rest.iter().zip(w_rest.iter()).enumerate() {
        let scalar = rest_direction.dot(&beta);
        let scalar_dot = rest_direction.dot(&beta_dot);
        let coefficient = gamma + h * scalar;
        let coefficient_dot = gamma_dot + h_dot * scalar + h * scalar_dot;
        let denominator = gamma * (1.0 + scalar);
        let denominator_dot = gamma_dot * (1.0 + scalar) + gamma * scalar_dot;
        if !denominator.is_finite() || denominator <= 0.0 {
            return Err(invalid(
                "paired inverse-aberration denominator must be positive",
            ));
        }

        let direction = (rest_direction + coefficient * beta) / denominator;
        let direction_dot = (coefficient_dot * beta + coefficient * beta_dot) / denominator
            - direction * (denominator_dot / denominator);
        if (direction.norm() - 1.0).abs() > 8.0e-13 {
            return Err(invalid("paired normal direction lost unit normalization"));
        }

        let d = 1.0 / denominator;
        let d_dot = -denominator_dot / denominator.powi(2);
        let q = 1.0 - direction.dot(&beta);
        let q_dot = -(direction_dot.dot(&beta) + direction.dot(&beta_dot));
        if !q.is_finite() || q <= 0.0 || (d - gamma * q).abs() > 5.0e-12 {
            return Err(invalid("D = gamma (1 - beta dot e) consistency failed"));
        }
        let weight = rest_weight * d.powi(2);
        let weight_dot = 2.0 * weight * d_dot / d;

        let screen = screen_projector(&direction);
        let screen_dot =
            -(direction_dot * direction.transpose() + direction * direction_dot.transpose());
        let projected_beta = screen * beta;
        let map = screen
            + h * (beta * projected_beta.transpose())
            + gamma * (rest_direction * projected_beta.transpose());

        let equilibrium_tensor = 0.5 * d.powi(-4) * screen;
        let equilibrium_dot_tensor =
            -2.0 * d.powi(-5) * d_dot * screen + 0.5 * d.powi(-4) * screen_dot;
        set_packed(&mut equilibrium, node, &equilibrium_tensor);
        set_packed(&mut equilibrium_dot, node, &equilibrium_dot_tensor);

        let left_node = weight * q / FOUR_PI;
        let left_node_dot = (weight_dot * q + weight * q_dot) / FOUR_PI;
        for diagonal in 0..3 {
            raw_left[9 * node + diagonal] = left_node;
            raw_left_dot[9 * node + diagonal] = left_node_dot;
        }

        e_normal.push(direction);
        doppler.push(d);
        direction_factor.push(q);
        w_normal.push(weight);
        screen_map.push(map);
    }

    let normalization = raw_left.dot(&equilibrium);
    if !normalization.is_finite() || normalization <= 0.0 {
        return Err(invalid("paired left/right normalization must be positive"));
    }
    let normalization_dot = raw_left_dot.dot(&equilibrium) + raw_left.dot(&equilibrium_dot);
    let normalized_left = &raw_left / normalization;
    let normalized_left_dot =
        &raw_left_dot / normalization - &raw_left * (normalization_dot / normalization.powi(2));
    let projector = &equilibrium * normalized_left.transpose();
    let projector_dot = &equilibrium_dot * normalized_left.transpose()
        + &equilibrium * normalized_left_dot.transpose();
    let kato = &projector_dot * &projector - &projector * &projector_dot;

    if !all_finite(equilibrium.iter().copied())
        || !all_finite(equilibrium_dot.iter().copied())
        || !all_finite(normalized_left.iter().copied())
        || !all_finite(normalized_left_dot.iter().copied())
        || !all_finite(projector.iter().copied())
        || !all_finite(projector_dot.iter().copied())
        || !all_finite(kato.iter().copied())
    {
        return Err(invalid(
            "generic-vector bundle produced a non-finite output",
        ));
    }

    Ok(PairedBundle {
        e_rest,
        e_normal,
        w_normal,
        doppler,
        direction_factor,
        screen_map,
        gamma,
        equilibrium,
        equilibrium_dot,
        normalized_left,
        normalized_left_dot,
        projector,
        projector_dot,
        kato,
    })
}

fn collision_action(bundle: &PairedBundle, global_rate: f64, values: &[f64]) -> Vec<f64> {
    let node_count = bundle.e_rest.len();
    debug_assert_eq!(values.len(), 9 * node_count);
    let mut rest_state = Vec::with_capacity(node_count);
    let mut moment = Matrix3::zeros();
    for node in 0..node_count {
        let state = unpack9(&values[9 * node..9 * node + 9]);
        let map = &bundle.screen_map[node];
        let transformed = bundle.doppler[node].powi(4) * (map * state * map.transpose());
        let rest_weight = bundle.w_normal[node] / bundle.doppler[node].powi(2);
        moment += rest_weight * transformed;
        rest_state.push(transformed);
    }

    let mut output = vec![0.0; 9 * node_count];
    for node in 0..node_count {
        let rest_screen = screen_projector(&bundle.e_rest[node]);
        let gain = THOMSON_GAIN * (rest_screen * moment * rest_screen);
        let collision_rest = gain - rest_state[node];
        let map = &bundle.screen_map[node];
        let pulled = map.transpose() * collision_rest * map;
        let collision_normal =
            global_rate * bundle.direction_factor[node] * bundle.doppler[node].powi(-4) * pulled;
        let packed = pack9(&collision_normal);
        output[9 * node..9 * node + 9].copy_from_slice(&packed);
    }
    output
}

fn collision_matrix(bundle: &PairedBundle, global_rate: f64) -> DMatrix<f64> {
    let state_size = bundle.equilibrium.len();
    let mut matrix = DMatrix::zeros(state_size, state_size);
    let mut basis = vec![0.0; state_size];
    for column in 0..state_size {
        basis[column] = 1.0;
        let output = collision_action(bundle, global_rate, &basis);
        basis[column] = 0.0;
        for row in 0..state_size {
            matrix[(row, column)] = output[row];
        }
    }
    matrix
}

pub fn execute(
    directions: &[[f64; 3]],
    weights: &[f64],
    beta: [f64; 3],
    beta_dot: [f64; 3],
    alpha: f64,
    enabled: bool,
) -> Result<GenericVectorHostDisposition, GenericVectorHostError> {
    if !enabled {
        return Err(GenericVectorHostError::Disabled);
    }
    validate_grid(directions, weights)?;
    if !alpha.is_finite() || alpha < 0.0 {
        return Err(invalid("alpha must be finite and nonnegative"));
    }
    if alpha == 0.0 {
        return Ok(GenericVectorHostDisposition::CollisionOff {
            state_size: 9 * directions.len(),
        });
    }

    let bundle = build_bundle(directions, weights, beta, beta_dot)?;
    let global_rate = alpha * bundle.gamma;
    let collision = collision_matrix(&bundle, global_rate);
    if !all_finite(collision.iter().copied()) {
        return Err(invalid("generic-vector collision operator is non-finite"));
    }
    let node_rate = bundle
        .doppler
        .iter()
        .map(|doppler| alpha * doppler)
        .collect();
    let e_normal = bundle
        .e_normal
        .iter()
        .map(|direction| [direction[0], direction[1], direction[2]])
        .collect();
    Ok(GenericVectorHostDisposition::Active(Box::new(
        ActiveGenericVectorHost {
            gamma: bundle.gamma,
            alpha,
            global_rate,
            e_normal,
            w_normal: bundle.w_normal,
            doppler: bundle.doppler,
            direction_factor: bundle.direction_factor,
            node_rate,
            equilibrium: bundle.equilibrium,
            equilibrium_dot: bundle.equilibrium_dot,
            normalized_left: bundle.normalized_left,
            normalized_left_dot: bundle.normalized_left_dot,
            collision,
            projector: bundle.projector,
            projector_dot: bundle.projector_dot,
            kato: bundle.kato,
        },
    )))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn grid6() -> ([[f64; 3]; 6], [f64; 6]) {
        (
            [
                [1.0, 0.0, 0.0],
                [-1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, -1.0, 0.0],
                [0.0, 0.0, 1.0],
                [0.0, 0.0, -1.0],
            ],
            [FOUR_PI / 6.0; 6],
        )
    }

    #[test]
    fn route_is_default_off() {
        let (directions, weights) = grid6();
        assert_eq!(
            execute(
                &directions,
                &weights,
                [0.1, 0.2, -0.1],
                [0.01, -0.02, 0.03],
                0.7,
                false,
            )
            .unwrap_err(),
            GenericVectorHostError::Disabled
        );
    }

    #[test]
    fn exact_vacuum_has_no_projector_disposition() {
        let (directions, weights) = grid6();
        let result = execute(
            &directions,
            &weights,
            [0.1, 0.2, -0.1],
            [0.01, -0.02, 0.03],
            0.0,
            true,
        )
        .unwrap();
        assert!(matches!(
            result,
            GenericVectorHostDisposition::CollisionOff { state_size: 54 }
        ));
    }
}
