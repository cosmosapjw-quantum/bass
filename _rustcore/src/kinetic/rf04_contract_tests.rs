//! RF-04 internal contract tests with non-degenerate angular resolution.

use nalgebra::DMatrix;

use super::rf04_typeii::{
    parse_carrier, parse_quadrature_route, require_supported, rf04_deterministic_batch_probe,
    scalar_raw_batch, scalar_raw_trajectory, Carrier, QuadratureRoute,
};

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
    for zero_axis in 0..3 {
        let live_axes: Vec<_> = (0..3).filter(|&axis| axis != zero_axis).collect();
        for sign0 in [-1.0, 1.0] {
            for sign1 in [-1.0, 1.0] {
                let mut direction = [0.0; 3];
                direction[live_axes[0]] = sign0 * b;
                direction[live_axes[1]] = sign1 * b;
                directions.push(direction);
                weights.push(16.0 * pi / 105.0);
            }
        }
    }
    for sign0 in [-1.0, 1.0] {
        for sign1 in [-1.0, 1.0] {
            for sign2 in [-1.0, 1.0] {
                directions.push([sign0 * a, sign1 * a, sign2 * a]);
                weights.push(9.0 * pi / 70.0);
            }
        }
    }
    (directions, weights)
}

fn l2_design(directions: &[[f64; 3]]) -> DMatrix<f64> {
    DMatrix::from_fn(directions.len(), 5, |row, column| {
        let [x, y, z] = directions[row];
        [
            x * x - y * y,
            2.0 * z * z - x * x - y * y,
            x * y,
            x * z,
            y * z,
        ][column]
    })
}

#[test]
fn rf04_physics_grid_resolves_all_l2_modes_and_fourth_moments() {
    let (directions, weights) = lebedev26();
    let singular_values = l2_design(&directions).svd(false, false).singular_values;
    assert_eq!(
        singular_values
            .iter()
            .filter(|&&value| value > 1e-13)
            .count(),
        5
    );

    let delta = |i: usize, j: usize| if i == j { 1.0 } else { 0.0 };
    for i in 0..3 {
        for j in 0..3 {
            for k in 0..3 {
                for l in 0..3 {
                    let observed: f64 = directions
                        .iter()
                        .zip(&weights)
                        .map(|(n, w)| w * n[i] * n[j] * n[k] * n[l])
                        .sum();
                    let expected = (4.0 * std::f64::consts::PI / 15.0)
                        * (delta(i, j) * delta(k, l)
                            + delta(i, k) * delta(j, l)
                            + delta(i, l) * delta(j, k));
                    assert!((observed - expected).abs() < 4e-15);
                }
            }
        }
    }
}

#[test]
fn rf04_route_capabilities_are_distinct_and_fail_closed() {
    assert_eq!(
        parse_carrier("scalar_intensity_v1").unwrap(),
        Carrier::ScalarIntensity
    );
    assert_eq!(
        parse_carrier("polarized_rank9_v1").unwrap(),
        Carrier::PolarizedRank9
    );
    assert!(parse_carrier("stokes4_silent_projection").is_err());
    assert_eq!(
        parse_quadrature_route("fixed_grid_raw_v1").unwrap(),
        QuadratureRoute::FixedGridRaw
    );
    assert_eq!(
        parse_quadrature_route("fixed_grid_ap_corrected_v1").unwrap(),
        QuadratureRoute::FixedGridApCorrected
    );
    assert_ne!(
        parse_quadrature_route("paired_rest_to_normal_reference_v1").unwrap(),
        parse_quadrature_route("fixed_grid_ap_corrected_v1").unwrap()
    );
    assert!(parse_quadrature_route("fixed_grid_claimed_ap_without_correction").is_err());
}

#[test]
fn rf04_scalar_raw_serial_and_independent_parallel_batches_are_bit_identical() {
    let serial = rf04_deterministic_batch_probe(1).unwrap();
    let parallel = rf04_deterministic_batch_probe(4).unwrap();
    assert!(!serial.is_empty());
    assert_eq!(serial, parallel);
}

fn scalar_fixture() -> (
    Vec<[f64; 3]>,
    Vec<f64>,
    Vec<f64>,
    Vec<[f64; 5]>,
    Vec<[f64; 5]>,
    Vec<[f64; 5]>,
    Vec<f64>,
    Vec<f64>,
) {
    let (directions, weights) = lebedev26();
    let initial = directions
        .iter()
        .map(|e| 1.0 + 0.18 * e[0] * e[1] - 0.13 * e[1] * e[2] + 0.09 * e[0] * e[2])
        .collect();
    (
        directions,
        weights,
        initial,
        vec![[0.25, 0.05, 1.0 / 30.0, 0.8, 0.08]],
        vec![[0.253, 0.048, 1.0 / 30.0 + 0.0015, 0.794, 0.0825]],
        vec![[0.257, 0.046, 1.0 / 30.0 + 0.0035, 0.787, 0.0855]],
        vec![0.18],
        vec![8.0e-4],
    )
}

#[test]
fn rf04_scalar_raw_owner_matches_independent_dense_fixture() {
    // Defect caught: missing or reordered K/C/AEM2 subactions change the state array.
    let (directions, weights, initial, q1, mid, q3, opacity, step_size) = scalar_fixture();
    let result = scalar_raw_trajectory(
        &initial,
        &directions,
        &weights,
        &q1,
        &mid,
        &q3,
        &opacity,
        &step_size,
        1.3,
        1.0,
        1,
    )
    .expect("scalar raw owner must execute");
    let expected = [
        0.9984197109558022,
        0.9984192901013926,
        0.9956916422695978,
        0.9957868459972262,
        0.9962624914961313,
        0.9962627950300579,
        0.9312367742316672,
        1.0606983868480948,
        1.0607663773811882,
        0.9313019422630551,
        1.0420138772798384,
        0.95265010466186,
        0.9526495924373469,
        1.0420137946065073,
        1.0867693563914869,
        0.9073855466142473,
        0.907320870686618,
        1.0868379443988714,
        1.0431561597921593,
        1.070006032090829,
        1.0099927109359692,
        0.8640534471539171,
        0.8640015535212223,
        1.0099381826314209,
        1.0700613026933572,
        1.043211232718528,
    ];
    assert_eq!(result.radiation_history.len(), 2);
    assert_eq!(result.radiation_history[0], initial);
    let error = result.radiation_history[1]
        .iter()
        .zip(expected)
        .map(|(observed, reference)| (observed - reference).abs())
        .fold(0.0_f64, f64::max);
    assert!(error < 2.0e-11, "dense fixture error={error:e}");
    assert_eq!(
        result.diagnostics.equilibrium_null_residual,
        result.diagnostics.right_kernel_residual
    );
    assert_eq!(result.diagnostics.projected_residual_estimate.len(), 1);
}

#[test]
fn rf04_scalar_raw_one_node_schema_boundary_matches_dense_fixture() {
    // Defect caught: the frozen schema permits M=1 even though the donor's
    // nominal Krylov option floor is two; its active basis must still clip to one.
    let directions = vec![[1.0, 0.0, 0.0]];
    let weights = vec![4.0 * std::f64::consts::PI];
    let initial = vec![1.2];
    let result = scalar_raw_trajectory(
        &initial,
        &directions,
        &weights,
        &[[0.25, 0.05, 1.0 / 30.0, 0.8, 0.08]],
        &[[0.253, 0.048, 1.0 / 30.0 + 0.0015, 0.794, 0.0825]],
        &[[0.257, 0.046, 1.0 / 30.0 + 0.0035, 0.787, 0.0855]],
        &[0.18],
        &[8.0e-4],
        1.3,
        1.0,
        1,
    )
    .expect("one-node scalar route must satisfy the frozen public schema");
    assert_eq!(result.radiation_history[0], initial);
    assert!((result.radiation_history[1][0] - 1.1981890444967072).abs() < 2.0e-12);
    assert!(result.diagnostics.projected_residual_estimate[0].is_finite());
}

#[test]
fn rf04_scalar_raw_executor_rejects_known_but_unimplemented_combinations() {
    // Defect caught: parsing a known A1 enum is mistaken for executable capability.
    let error = require_supported(
        Carrier::PolarizedRank9,
        QuadratureRoute::PairedRestToNormalReference,
    )
    .unwrap_err();
    assert_eq!(error.code(), "RF04_UNSUPPORTED_CAPABILITY");
    let error = require_supported(
        Carrier::ScalarIntensity,
        QuadratureRoute::FixedGridApCorrected,
    )
    .unwrap_err();
    assert_eq!(error.code(), "RF04_UNSUPPORTED_CAPABILITY");
}

#[test]
fn rf04_scalar_raw_batch_isolates_invalid_member_after_shared_plan_validation() {
    // Defect caught: one malformed member aborts or corrupts otherwise valid members.
    let (directions, weights, initial, q1, mid, q3, opacity, step_size) = scalar_fixture();
    let mut invalid = initial.clone();
    invalid[0] = f64::NAN;
    let result = scalar_raw_batch(
        &[initial.clone(), invalid, initial],
        &directions,
        &weights,
        &q1,
        &mid,
        &q3,
        &opacity,
        &step_size,
        1.3,
        1.0,
        1,
    )
    .expect("shared plan is valid");
    assert_eq!(result.member_status, [0, 1, 0]);
    assert!(result.final_radiation[1].iter().all(|value| value.is_nan()));
    assert_eq!(result.member_completed_steps, [1, 0, 1]);
    assert_eq!(
        result.member_error_code[1].as_deref(),
        Some("RF04_NONPHYSICAL_CARRIER")
    );
}
