use bianchi_rustcore::generated::typeii_collision;
use bianchi_rustcore::generated::typeii_collision_ap::{
    collision_generator_apply_ap, collision_generator_apply_polarized_ap_physical,
    equilibrium_state as scalar_equilibrium_state, left_invariant as scalar_left_invariant,
};
use bianchi_rustcore::generated::typeii_krylov_adapt::{
    AdaptiveKrylovError, AdaptiveKrylovOptions,
};
use bianchi_rustcore::generated::typeii_physical_guard::{
    collision_apply_physical, enforce_screen_state, max_screen_leakage,
    minimum_coherency_eigenvalue, project_screen_state, PhysicalCarrierError, ScreenInputPolicy,
};
use bianchi_rustcore::generated::typeii_polarized;
use bianchi_rustcore::generated::typeii_polarized_runtime_physical::{
    frozen_collision_step_physical_adaptive, frozen_collision_step_physical_adaptive_with_policy,
    frozen_kato_step_physical_adaptive, PhysicalCollisionPolicy, PhysicalPolarizedRuntimeError,
};
use nalgebra::DMatrix;

type Mat3 = [[f64; 3]; 3];

fn grid6() -> ([[f64; 3]; 6], [f64; 6]) {
    let weight = 4.0 * std::f64::consts::PI / 6.0;
    (
        [
            [1.0, 0.0, 0.0],
            [-1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, -1.0, 0.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, -1.0],
        ],
        [weight; 6],
    )
}

fn lebedev26() -> (Vec<[f64; 3]>, Vec<f64>) {
    let pi = std::f64::consts::PI;
    let a = 1.0 / 3.0_f64.sqrt();
    let b = 1.0 / 2.0_f64.sqrt();
    let mut directions = Vec::new();
    let mut weights = Vec::new();
    for axis in 0..3 {
        for sign in [-1.0, 1.0] {
            let mut direction = [0.0; 3];
            direction[axis] = sign;
            directions.push(direction);
            weights.push(4.0 * pi / 21.0);
        }
    }
    for zero in 0..3 {
        let live: Vec<_> = (0..3).filter(|&axis| axis != zero).collect();
        for sign0 in [-1.0, 1.0] {
            for sign1 in [-1.0, 1.0] {
                let mut direction = [0.0; 3];
                direction[live[0]] = sign0 * b;
                direction[live[1]] = sign1 * b;
                directions.push(direction);
                weights.push(16.0 * pi / 105.0);
            }
        }
    }
    for x in [-1.0, 1.0] {
        for y in [-1.0, 1.0] {
            for z in [-1.0, 1.0] {
                directions.push([x * a, y * a, z * a]);
                weights.push(9.0 * pi / 70.0);
            }
        }
    }
    (directions, weights)
}

fn dot3(a: [f64; 3], b: [f64; 3]) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}

fn cross(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
}

fn tangent_frame(direction: [f64; 3]) -> ([f64; 3], [f64; 3]) {
    let mut axis = 0usize;
    if direction[1].abs() < direction[axis].abs() {
        axis = 1;
    }
    if direction[2].abs() < direction[axis].abs() {
        axis = 2;
    }
    let mut seed = [0.0; 3];
    seed[axis] = 1.0;
    let parallel = dot3(seed, direction);
    let mut u = [
        seed[0] - parallel * direction[0],
        seed[1] - parallel * direction[1],
        seed[2] - parallel * direction[2],
    ];
    let norm = dot3(u, u).sqrt();
    for value in &mut u {
        *value /= norm;
    }
    (u, cross(direction, u))
}

fn outer(a: [f64; 3], b: [f64; 3]) -> Mat3 {
    let mut out = [[0.0; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            out[i][j] = a[i] * b[j];
        }
    }
    out
}

fn add(a: &Mat3, b: &Mat3) -> Mat3 {
    let mut out = [[0.0; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            out[i][j] = a[i][j] + b[i][j];
        }
    }
    out
}

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

fn unpack9(packed: &[f64]) -> Mat3 {
    [
        [packed[0], packed[3] + packed[8], packed[4] - packed[7]],
        [packed[3] - packed[8], packed[1], packed[5] + packed[6]],
        [packed[4] + packed[7], packed[5] - packed[6], packed[2]],
    ]
}

fn physical_basis(direction: [f64; 3]) -> [Mat3; 4] {
    let (u, v) = tangent_frame(direction);
    let uu = outer(u, u);
    let vv = outer(v, v);
    let uv = outer(u, v);
    let vu = outer(v, u);
    let mut basis = [[[0.0; 3]; 3]; 4];
    for i in 0..3 {
        for j in 0..3 {
            basis[0][i][j] = 0.5 * (uu[i][j] + vv[i][j]);
            basis[1][i][j] = 0.5 * (uu[i][j] - vv[i][j]);
            basis[2][i][j] = 0.5 * (uv[i][j] + vu[i][j]);
            basis[3][i][j] = 0.5 * (uv[i][j] - vu[i][j]);
        }
    }
    basis
}

fn coefficient(matrix: &Mat3, basis: &Mat3) -> f64 {
    let mut numerator = 0.0;
    let mut denominator = 0.0;
    for i in 0..3 {
        for j in 0..3 {
            numerator += matrix[i][j] * basis[i][j];
            denominator += basis[i][j] * basis[i][j];
        }
    }
    numerator / denominator
}

fn aberrate_y(direction: [f64; 3], velocity: f64) -> ([f64; 3], f64) {
    if velocity == 0.0 {
        return (direction, 1.0);
    }
    let gamma = 1.0 / (1.0 - velocity * velocity).sqrt();
    let doppler = gamma * (1.0 - velocity * direction[1]);
    let mut out = direction;
    out[1] += (gamma - 1.0) * direction[1] - gamma * velocity;
    for value in &mut out {
        *value /= doppler;
    }
    let norm = dot3(out, out).sqrt();
    for value in &mut out {
        *value /= norm;
    }
    (out, doppler)
}

fn paired_grid(
    rest_directions: &[[f64; 3]],
    rest_weights: &[f64],
    velocity: f64,
) -> (Vec<[f64; 3]>, Vec<f64>) {
    let mut directions = Vec::with_capacity(rest_directions.len());
    let mut weights = Vec::with_capacity(rest_weights.len());
    for (&direction, &weight) in rest_directions.iter().zip(rest_weights) {
        let (normal_direction, _) = aberrate_y(direction, -velocity);
        let (_, doppler_to_rest) = aberrate_y(normal_direction, velocity);
        directions.push(normal_direction);
        weights.push(weight * doppler_to_rest * doppler_to_rest);
    }
    (directions, weights)
}

fn max_abs(values: &[f64]) -> f64 {
    values.iter().map(|value| value.abs()).fold(0.0, f64::max)
}

fn norm2(values: &[f64]) -> f64 {
    values.iter().map(|value| value * value).sum::<f64>().sqrt()
}

fn stokes_matrix(direction: [f64; 3], intensity: f64, q: f64, u0: f64, v0: f64) -> Mat3 {
    let (u, v) = tangent_frame(direction);
    let mut matrix = [[0.0; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            matrix[i][j] = 0.5 * (intensity + q) * u[i] * u[j]
                + 0.5 * (intensity - q) * v[i] * v[j]
                + 0.5 * (u0 + v0) * u[i] * v[j]
                + 0.5 * (u0 - v0) * v[i] * u[j];
        }
    }
    matrix
}

fn adaptive_options() -> AdaptiveKrylovOptions {
    AdaptiveKrylovOptions {
        m_init: 12,
        m_min: 8,
        m_max: 20,
        tol: 1e-11,
        max_substeps: 4096,
        max_rejects: 4096,
    }
}

#[test]
fn longitudinal_raw_null_is_rejected_or_projected_by_checked_carrier() {
    let (directions, weights) = grid6();
    let mut state = vec![0.0; 9 * directions.len()];
    for (node, &direction) in directions.iter().enumerate() {
        let a = [0.3 + 0.1 * node as f64, -0.2, 0.5];
        let b = [-0.4, 0.2 + 0.03 * node as f64, 0.1];
        let longitudinal = add(&outer(direction, a), &outer(b, direction));
        state[9 * node..9 * node + 9].copy_from_slice(&pack9(&longitudinal));
    }
    let raw = typeii_polarized::collision_generator_apply_polarized(
        &directions,
        &weights,
        0.1,
        1,
        &state,
    );
    assert!(max_abs(&raw) < 1e-13, "raw negative control changed");

    let rejected = collision_apply_physical(
        &directions,
        &weights,
        0.1,
        1,
        &state,
        ScreenInputPolicy::Reject { tolerance: 1e-12 },
        1e-12,
    );
    assert!(matches!(
        rejected,
        Err(PhysicalCarrierError::NonPhysicalScreenState { .. })
    ));

    let projected = enforce_screen_state(&directions, &state, ScreenInputPolicy::Project).unwrap();
    assert!(max_screen_leakage(&directions, &projected).unwrap() < 2e-15);
    assert!(max_abs(&projected) < 2e-15);
}

#[test]
fn malformed_physical_inputs_fail_closed_without_panics() {
    let (directions, weights) = grid6();
    let state = typeii_polarized::equilibrium_state_polarized(&directions, 0.0, 1);

    assert!(matches!(
        collision_apply_physical(
            &directions,
            &weights[..5],
            0.0,
            1,
            &state,
            ScreenInputPolicy::Project,
            1e-12,
        ),
        Err(PhysicalCarrierError::DirectionWeightMismatch { .. })
    ));
    assert!(matches!(
        collision_apply_physical(
            &directions,
            &weights,
            f64::NAN,
            1,
            &state,
            ScreenInputPolicy::Project,
            1e-12,
        ),
        Err(PhysicalCarrierError::NonFiniteVelocity)
    ));
    assert!(matches!(
        collision_apply_physical(
            &directions,
            &weights,
            0.0,
            3,
            &state,
            ScreenInputPolicy::Project,
            1e-12,
        ),
        Err(PhysicalCarrierError::InvalidAxis { axis: 3 })
    ));
    let mut bad_directions = directions;
    bad_directions[0] = [2.0, 0.0, 0.0];
    assert!(matches!(
        project_screen_state(&bad_directions, &state),
        Err(PhysicalCarrierError::NonUnitDirection { node: 0, .. })
    ));
    assert!(matches!(
        enforce_screen_state(
            &directions,
            &state,
            ScreenInputPolicy::Reject {
                tolerance: f64::NAN,
            },
        ),
        Err(PhysicalCarrierError::InvalidTolerance { .. })
    ));

    let runtime_error = frozen_collision_step_physical_adaptive(
        &directions,
        &weights,
        0.0,
        1,
        f64::NAN,
        &state,
        ScreenInputPolicy::Project,
        adaptive_options(),
    )
    .unwrap_err();
    assert!(matches!(
        runtime_error,
        PhysicalPolarizedRuntimeError::Adaptive(AdaptiveKrylovError::NonFiniteTime)
    ));
}

#[test]
fn moving_paired_grid_physical_kernel_has_one_equilibrium_null_mode() {
    let velocity = 0.1;
    let (rest_directions, rest_weights) = lebedev26();
    let (directions, weights) = paired_grid(&rest_directions, &rest_weights, velocity);
    let bases: Vec<_> = directions
        .iter()
        .map(|&direction| physical_basis(direction))
        .collect();
    let dimension = 4 * directions.len();
    let mut matrix = DMatrix::<f64>::zeros(dimension, dimension);
    for column in 0..dimension {
        let node = column / 4;
        let mode = column % 4;
        let mut state = vec![0.0; 9 * directions.len()];
        state[9 * node..9 * node + 9].copy_from_slice(&pack9(&bases[node][mode]));
        let output = collision_apply_physical(
            &directions,
            &weights,
            velocity,
            1,
            &state,
            ScreenInputPolicy::Reject { tolerance: 2e-13 },
            2e-12,
        )
        .unwrap();
        for output_node in 0..directions.len() {
            let coherency = unpack9(&output[9 * output_node..9 * output_node + 9]);
            for output_mode in 0..4 {
                matrix[(4 * output_node + output_mode, column)] =
                    coefficient(&coherency, &bases[output_node][output_mode]);
            }
        }
    }

    let svd = matrix.svd(false, true);
    let singular = svd.singular_values.as_slice();
    let maximum = singular.iter().copied().fold(0.0, f64::max);
    let relative_threshold = 2e-11 * maximum.max(1.0);
    let null_indices: Vec<_> = singular
        .iter()
        .enumerate()
        .filter_map(|(index, &value)| (value <= relative_threshold).then_some(index))
        .collect();
    assert_eq!(null_indices.len(), 1, "singular={singular:?}");

    let equilibrium = typeii_polarized::equilibrium_state_polarized(&directions, velocity, 1);
    let residual = collision_apply_physical(
        &directions,
        &weights,
        velocity,
        1,
        &equilibrium,
        ScreenInputPolicy::Reject { tolerance: 2e-13 },
        2e-12,
    )
    .unwrap();
    let residual_relative = norm2(&residual) / norm2(&equilibrium);
    assert!(residual_relative < 2e-12, "residual={residual_relative:e}");

    let mut equilibrium_coordinates = Vec::with_capacity(dimension);
    for node in 0..directions.len() {
        let matrix = unpack9(&equilibrium[9 * node..9 * node + 9]);
        for mode in 0..4 {
            equilibrium_coordinates.push(coefficient(&matrix, &bases[node][mode]));
        }
    }
    let coordinate_norm = norm2(&equilibrium_coordinates);
    let v_t = svd.v_t.unwrap();
    let null_row = v_t.row(null_indices[0]);
    let alignment = null_row
        .iter()
        .zip(&equilibrium_coordinates)
        .map(|(a, b)| a * b)
        .sum::<f64>()
        .abs()
        / coordinate_norm;
    println!(
        "PHYSICAL_NULLITY velocity={velocity:e} dimension={dimension} nullity={} sigma_min={:e} sigma_gap={:e} residual_relative={residual_relative:e} equilibrium_alignment={alignment:e}",
        null_indices.len(),
        singular[null_indices[0]],
        singular.iter().copied().filter(|value| *value > relative_threshold).fold(f64::INFINITY, f64::min),
    );
    assert!(alignment > 1.0 - 2e-10, "alignment={alignment:e}");
}

#[test]
fn fixed_grid_raw_and_opt_in_ap_residuals_are_reported_separately() {
    let (directions, weights) = grid6();
    let velocity = 0.1;
    let nu = 230.0;
    let equilibrium = scalar_equilibrium_state(&directions, &weights, velocity, 1).unwrap();
    let raw = typeii_collision::collision_generator_apply(
        &directions,
        &weights,
        velocity,
        1,
        &equilibrium,
    );
    let corrected =
        collision_generator_apply_ap(&directions, &weights, velocity, 1, &equilibrium).unwrap();
    let raw_residual = norm2(&raw);
    let corrected_residual = norm2(&corrected);
    assert!(raw_residual > 1e-5);
    assert!(corrected_residual < 2e-14);
    for alpha in [1.0, 1e3, 1e5] {
        println!(
            "FIXED_GRID_AP alpha={alpha:e} nu={nu:e} raw_residual={raw_residual:e} raw_stiffness_amplification={:e} corrected_residual={corrected_residual:e} corrected_stiffness_amplification={:e} continuum_law_modified=false",
            alpha * nu * raw_residual,
            alpha * nu * corrected_residual,
        );
    }

    let state: Vec<_> = (0..directions.len())
        .map(|index| ((17 * index + 3) % 29) as f64 / 13.0 - 1.0)
        .collect();
    let corrected_state =
        collision_generator_apply_ap(&directions, &weights, velocity, 1, &state).unwrap();
    let invariant =
        scalar_left_invariant(&directions, &weights, velocity, 1, &corrected_state).unwrap();
    assert!(invariant.abs() < 2e-14, "left invariant={invariant:e}");
}

#[test]
fn paired_rest_to_normal_grid_remains_the_reference_lane() {
    let velocity = 0.1;
    let (rest_directions, rest_weights) = grid6();
    let (directions, weights) = paired_grid(&rest_directions, &rest_weights, velocity);
    let equilibrium = scalar_equilibrium_state(&directions, &weights, velocity, 1).unwrap();
    let raw_equilibrium = typeii_collision::collision_generator_apply(
        &directions,
        &weights,
        velocity,
        1,
        &equilibrium,
    );
    assert!(norm2(&raw_equilibrium) < 2e-13);

    let state: Vec<_> = (0..directions.len())
        .map(|index| 0.2 + 0.1 * index as f64)
        .collect();
    let raw =
        typeii_collision::collision_generator_apply(&directions, &weights, velocity, 1, &state);
    let corrected =
        collision_generator_apply_ap(&directions, &weights, velocity, 1, &state).unwrap();
    let difference = raw
        .iter()
        .zip(&corrected)
        .map(|(a, b)| a - b)
        .collect::<Vec<_>>();
    println!(
        "PAIRED_REFERENCE raw_equilibrium_residual={:e} raw_vs_corrected={:e}",
        norm2(&raw_equilibrium),
        norm2(&difference),
    );
    assert!(norm2(&difference) < 3e-13);
}

fn gauss_legendre(order: usize) -> (Vec<f64>, Vec<f64>) {
    let mut nodes = vec![0.0; order];
    let mut weights = vec![0.0; order];
    for root in 0..order.div_ceil(2) {
        let mut z = (std::f64::consts::PI * (root as f64 + 0.75) / (order as f64 + 0.5)).cos();
        let mut derivative = 0.0;
        for _ in 0..32 {
            let mut p_nm2 = 0.0;
            let mut p_nm1 = 1.0;
            for degree in 1..=order {
                let p_n = ((2 * degree - 1) as f64 * z * p_nm1 - (degree - 1) as f64 * p_nm2)
                    / degree as f64;
                p_nm2 = p_nm1;
                p_nm1 = p_n;
            }
            derivative = order as f64 * (z * p_nm1 - p_nm2) / (z * z - 1.0);
            let next = z - p_nm1 / derivative;
            if (next - z).abs() <= 2.0e-15 {
                z = next;
                break;
            }
            z = next;
        }
        let weight = 2.0 / ((1.0 - z * z) * derivative * derivative);
        nodes[root] = -z;
        nodes[order - 1 - root] = z;
        weights[root] = weight;
        weights[order - 1 - root] = weight;
    }
    (nodes, weights)
}

fn product_sphere_grid(n_theta: usize, n_phi: usize) -> (Vec<[f64; 3]>, Vec<f64>) {
    let (z_nodes, z_weights) = gauss_legendre(n_theta);
    let mut directions = Vec::with_capacity(n_theta * n_phi);
    let mut weights = Vec::with_capacity(n_theta * n_phi);
    for (&z, &z_weight) in z_nodes.iter().zip(&z_weights) {
        let radius = (1.0 - z * z).max(0.0).sqrt();
        for azimuth in 0..n_phi {
            let phi = 2.0 * std::f64::consts::PI * azimuth as f64 / n_phi as f64;
            directions.push([radius * phi.cos(), radius * phi.sin(), z]);
            weights.push(z_weight * 2.0 * std::f64::consts::PI / n_phi as f64);
        }
    }
    (directions, weights)
}

fn off_equilibrium_field(direction: [f64; 3]) -> f64 {
    (0.37 * direction[0] - 0.21 * direction[1] + 0.19 * direction[2]).exp()
        * (1.0 + 0.13 * direction[0] * direction[1])
}

fn continuum_collision_action(
    evaluation_directions: &[[f64; 3]],
    quadrature_directions: &[[f64; 3]],
    quadrature_weights: &[f64],
    velocity: f64,
) -> Vec<f64> {
    evaluation_directions
        .iter()
        .map(|&evaluation_direction| {
            let (evaluation_rest, evaluation_doppler) = aberrate_y(evaluation_direction, velocity);
            let mut integral = 0.0;
            for (&quadrature_direction, &quadrature_weight) in
                quadrature_directions.iter().zip(quadrature_weights)
            {
                let (quadrature_rest, quadrature_doppler) =
                    aberrate_y(quadrature_direction, velocity);
                let cosine = dot3(evaluation_rest, quadrature_rest);
                let kernel = 3.0 * (1.0 + cosine * cosine) / (16.0 * std::f64::consts::PI);
                let rest_weight = quadrature_weight / quadrature_doppler.powi(2);
                integral += kernel
                    * rest_weight
                    * quadrature_doppler.powi(4)
                    * off_equilibrium_field(quadrature_direction);
            }
            let rate = 1.0 - velocity * evaluation_direction[1];
            rate * evaluation_doppler.powi(-4)
                * (integral
                    - evaluation_doppler.powi(4) * off_equilibrium_field(evaluation_direction))
        })
        .collect()
}

fn weighted_relative_error(weights: &[f64], got: &[f64], expected: &[f64]) -> f64 {
    let numerator = weights
        .iter()
        .zip(got)
        .zip(expected)
        .map(|((&weight, &got), &expected)| weight * (got - expected).powi(2))
        .sum::<f64>()
        .sqrt();
    let denominator = weights
        .iter()
        .zip(expected)
        .map(|(&weight, &expected)| weight * expected * expected)
        .sum::<f64>()
        .sqrt();
    numerator / denominator
}

#[test]
fn ap_correction_converges_to_the_raw_continuum_action_off_equilibrium() {
    let velocity = 0.1;
    let (reference_directions, reference_weights) = product_sphere_grid(24, 48);
    let mut raw_errors = Vec::new();
    let mut corrected_errors = Vec::new();
    let mut raw_corrected_differences = Vec::new();

    for (n_theta, n_phi) in [(3, 6), (4, 8), (5, 10)] {
        let (directions, weights) = product_sphere_grid(n_theta, n_phi);
        let state = directions
            .iter()
            .copied()
            .map(off_equilibrium_field)
            .collect::<Vec<_>>();
        let raw =
            typeii_collision::collision_generator_apply(&directions, &weights, velocity, 1, &state);
        let corrected =
            collision_generator_apply_ap(&directions, &weights, velocity, 1, &state).unwrap();
        let reference = continuum_collision_action(
            &directions,
            &reference_directions,
            &reference_weights,
            velocity,
        );
        raw_errors.push(weighted_relative_error(&weights, &raw, &reference));
        corrected_errors.push(weighted_relative_error(&weights, &corrected, &reference));
        raw_corrected_differences.push(weighted_relative_error(&weights, &corrected, &raw));
    }

    for errors in [&raw_errors, &corrected_errors, &raw_corrected_differences] {
        assert!(
            errors[0] > errors[1] && errors[1] > errors[2],
            "errors={errors:?}"
        );
    }
    assert!(
        corrected_errors[2] < 2.0e-9,
        "corrected={corrected_errors:?}"
    );
    assert!(
        raw_corrected_differences[2] < 2.0e-9,
        "raw-ap={raw_corrected_differences:?}"
    );
}

fn cone_state(directions: &[[f64; 3]], boundary: bool) -> Vec<f64> {
    let mut state = Vec::with_capacity(9 * directions.len());
    for (node, &direction) in directions.iter().enumerate() {
        let phase = 0.37 * node as f64;
        let intensity = 1.0 + 0.1 * node as f64;
        let polarization = if boundary { intensity } else { 0.7 * intensity };
        state.extend_from_slice(&pack9(&stokes_matrix(
            direction,
            intensity,
            polarization * phase.cos(),
            polarization * phase.sin(),
            0.0,
        )));
    }
    state
}

fn circular_cone_boundary_state(directions: &[[f64; 3]], handedness: f64) -> Vec<f64> {
    let mut state = Vec::with_capacity(9 * directions.len());
    for &direction in directions {
        state.extend_from_slice(&pack9(&stokes_matrix(direction, 1.0, 0.0, 0.0, handedness)));
    }
    state
}

#[test]
fn finite_screen_projection_overflow_fails_closed() {
    let directions = [[0.0, 0.0, 1.0]];
    let mut finite = [0.0; 9];
    finite[3] = f64::MAX;
    finite[8] = f64::MAX;
    assert!(finite.iter().all(|value| value.is_finite()));

    assert!(matches!(
        project_screen_state(&directions, &finite),
        Err(PhysicalCarrierError::ScreenProjectionArithmeticNonFinite { .. })
    ));
    assert!(matches!(
        max_screen_leakage(&directions, &finite),
        Err(PhysicalCarrierError::ScreenProjectionArithmeticNonFinite { .. })
    ));
    assert!(matches!(
        enforce_screen_state(
            &directions,
            &finite,
            ScreenInputPolicy::Reject { tolerance: 0.0 },
        ),
        Err(PhysicalCarrierError::ScreenProjectionArithmeticNonFinite { .. })
    ));
}

#[test]
fn finite_screen_leakage_overflow_fails_closed() {
    let directions = [[-0.75_f64.sqrt(), 0.5, 0.0]];
    let mut finite = [0.0; 9];
    finite[0] = f64::MAX;
    finite[1] = -f64::MAX;
    let projected = project_screen_state(&directions, &finite).unwrap();
    assert!(projected.iter().all(|value| value.is_finite()));

    assert!(matches!(
        max_screen_leakage(&directions, &finite),
        Err(PhysicalCarrierError::ScreenLeakageArithmeticNonFinite { index: 0 })
    ));
    assert!(matches!(
        enforce_screen_state(
            &directions,
            &finite,
            ScreenInputPolicy::Reject {
                tolerance: f64::MAX
            },
        ),
        Err(PhysicalCarrierError::ScreenLeakageArithmeticNonFinite { index: 0 })
    ));
    let projected_by_policy =
        enforce_screen_state(&directions, &finite, ScreenInputPolicy::Project).unwrap();
    assert_eq!(projected_by_policy, projected);
}

#[test]
fn accepted_near_unit_directions_are_canonicalized_to_rank_two_screens() {
    let scale = 1.0 + 5.0e-11;
    let directions = [[scale, 0.0, 0.0]];
    let mut longitudinal = [0.0; 9];
    longitudinal[0] = 1.0e300;

    let once = project_screen_state(&directions, &longitudinal).unwrap();
    let twice = project_screen_state(&directions, &once).unwrap();
    let leakage = max_screen_leakage(&directions, &once).unwrap();
    println!(
        "CANONICAL_SCREEN input_norm={scale:.17e} once_longitudinal={:e} twice_longitudinal={:e} leakage={leakage:e}",
        once[0], twice[0],
    );
    assert_eq!(once[0], 0.0);
    assert_eq!(twice[0], 0.0);
    assert_eq!(leakage, 0.0);
}

#[test]
fn circular_v_cone_boundary_is_the_fourth_real_carrier_coordinate() {
    let (directions, weights) = grid6();
    for handedness in [-1.0, 1.0] {
        let state = circular_cone_boundary_state(&directions, handedness);
        let expected_p8 = 0.5 * handedness;
        assert!((state[9 * 4 + 8] - expected_p8).abs() < 2e-15);
        let input_margin = minimum_coherency_eigenvalue(&directions, &state).unwrap();
        assert!(input_margin.abs() < 2e-15, "margin={input_margin:e}");
        let (output, stats) = frozen_collision_step_physical_adaptive(
            &directions,
            &weights,
            0.0,
            1,
            20.0,
            &state,
            ScreenInputPolicy::Reject { tolerance: 2e-13 },
            adaptive_options(),
        )
        .unwrap();
        let output_margin = minimum_coherency_eigenvalue(&directions, &output).unwrap();
        let leakage = max_screen_leakage(&directions, &output).unwrap();
        println!(
            "CIRCULAR_V_CONE handedness={handedness:e} packed_p8={expected_p8:e} input_min_eigenvalue={input_margin:e} output_min_eigenvalue={output_margin:e} screen_leakage={leakage:e} accepted_actions={} rejected_actions={} max_basis={}",
            stats.accepted_steps,
            stats.rejected_steps,
            stats.max_basis,
        );
        assert!(output_margin > -2e-10);
        assert!(leakage < 2e-12);
    }
}

#[test]
fn deep_collision_exponential_records_interior_and_cone_boundary_safety() {
    let velocity = 0.1;
    let (rest_directions, rest_weights) = grid6();
    let (directions, weights) = paired_grid(&rest_directions, &rest_weights, velocity);
    for boundary in [false, true] {
        let state = cone_state(&directions, boundary);
        let input_margin = minimum_coherency_eigenvalue(&directions, &state).unwrap();
        let (output, stats) = frozen_collision_step_physical_adaptive(
            &directions,
            &weights,
            velocity,
            1,
            20.0,
            &state,
            ScreenInputPolicy::Reject { tolerance: 2e-12 },
            adaptive_options(),
        )
        .unwrap();
        let output_margin = minimum_coherency_eigenvalue(&directions, &output).unwrap();
        let leakage = max_screen_leakage(&directions, &output).unwrap();
        println!(
            "CONE_EXP boundary={boundary} input_min_eigenvalue={input_margin:e} output_min_eigenvalue={output_margin:e} screen_leakage={leakage:e} accepted_actions={} rejected_actions={} nonfinite_rejections={} max_basis={}",
            stats.accepted_steps,
            stats.rejected_steps,
            stats.nonfinite_rejections,
            stats.max_basis,
        );
        assert!(output_margin > -2e-10, "margin={output_margin:e}");
        assert!(leakage < 2e-12, "leakage={leakage:e}");
        assert!(stats.accepted_steps > 0);
        assert!(stats.max_basis <= adaptive_options().m_max);
    }
}

#[test]
fn opt_in_polarized_ap_runtime_keeps_fixed_grid_equilibrium_stationary() {
    let (directions, weights) = grid6();
    let velocity = 0.1;
    let equilibrium = typeii_polarized::equilibrium_state_polarized(&directions, velocity, 1);
    let raw_residual = collision_apply_physical(
        &directions,
        &weights,
        velocity,
        1,
        &equilibrium,
        ScreenInputPolicy::Project,
        2e-12,
    )
    .unwrap();
    assert!(norm2(&raw_residual) > 1e-5);

    let corrected_residual = collision_generator_apply_polarized_ap_physical(
        &directions,
        &weights,
        velocity,
        1,
        &equilibrium,
        ScreenInputPolicy::Project,
    )
    .unwrap();
    assert!(norm2(&corrected_residual) < 2e-13);

    let (corrected, stats) = frozen_collision_step_physical_adaptive_with_policy(
        &directions,
        &weights,
        velocity,
        1,
        20.0,
        &equilibrium,
        ScreenInputPolicy::Project,
        PhysicalCollisionPolicy::DiscreteApCorrection,
        adaptive_options(),
    )
    .unwrap();
    let difference = corrected
        .iter()
        .zip(&equilibrium)
        .map(|(a, b)| a - b)
        .collect::<Vec<_>>();
    println!(
        "POLARIZED_AP_FIXED_GRID raw_residual={:e} corrected_residual={:e} corrected_step_error={:e} accepted_actions={} rejected_actions={} max_basis={} continuum_law_modified=false",
        norm2(&raw_residual),
        norm2(&corrected_residual),
        norm2(&difference),
        stats.accepted_steps,
        stats.rejected_steps,
        stats.max_basis,
    );
    assert!(norm2(&difference) < 2e-10);
    assert!(max_screen_leakage(&directions, &corrected).unwrap() < 2e-12);
}

#[test]
fn projected_kato_exponential_stays_on_the_four_real_screen_carrier() {
    let velocity = 0.05;
    let (rest_directions, rest_weights) = grid6();
    let (directions, weights) = paired_grid(&rest_directions, &rest_weights, velocity);
    let state = cone_state(&directions, false);
    let (output, stats) = frozen_kato_step_physical_adaptive(
        &directions,
        &weights,
        velocity,
        0.03,
        1,
        0.1,
        &state,
        ScreenInputPolicy::Reject { tolerance: 2e-12 },
        adaptive_options(),
    )
    .unwrap();
    let leakage = max_screen_leakage(&directions, &output).unwrap();
    println!(
        "KATO_SCREEN screen_leakage={leakage:e} accepted_actions={} rejected_actions={} nonfinite_rejections={} max_basis={}",
        stats.accepted_steps,
        stats.rejected_steps,
        stats.nonfinite_rejections,
        stats.max_basis,
    );
    assert!(leakage < 2e-12);
}
