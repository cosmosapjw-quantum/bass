//! RF-04 internal contract tests with non-degenerate angular resolution.

use nalgebra::DMatrix;

use super::rf04_typeii::{
    parse_carrier, parse_quadrature_route, rf04_deterministic_batch_probe, Carrier, QuadratureRoute,
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
fn rf04_scalar_and_independent_parallel_batches_are_bit_identical() {
    let serial = rf04_deterministic_batch_probe(1).unwrap();
    let parallel = rf04_deterministic_batch_probe(4).unwrap();
    assert!(!serial.is_empty());
    assert_eq!(serial, parallel);
}
