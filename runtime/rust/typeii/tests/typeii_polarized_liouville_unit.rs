use bianchi_rustcore::generated::typeii_physical_guard::{
    minimum_coherency_eigenvalue, ScreenInputPolicy,
};
use bianchi_rustcore::generated::typeii_polarized_liouville::{
    liouville_coefficients, polarized_bolometric_rhs, transport_characteristic,
    transport_characteristic_profile, transport_typeii_characteristic,
    typeii_background_from_state, HomogeneousRayBackground, PolarizedLiouvilleError,
    MAX_MIDPOINT_BISECTIONS,
};

fn max_abs(a: &[f64], b: &[f64]) -> f64 {
    a.iter()
        .zip(b)
        .map(|(x, y)| (x - y).abs())
        .fold(0.0, f64::max)
}

#[test]
fn flrw_characteristic_keeps_direction_and_scales_bolometric_coherency() {
    let direction = [0.0, 0.0, 1.0];
    let state = [0.7, 0.3, 0.0, 0.1, 0.0, 0.0, 0.0, 0.0, 0.2];
    let background = HomogeneousRayBackground {
        expansion: 1.0,
        ..HomogeneousRayBackground::zero()
    };
    let result = transport_characteristic(
        direction,
        &background,
        &background,
        0.2,
        1,
        &state,
        ScreenInputPolicy::Reject { tolerance: 1e-14 },
    )
    .unwrap();

    assert!(max_abs(&result.direction, &direction) < 1e-14);
    assert!((result.log_energy_shift + 0.2).abs() < 2e-14);
    assert!((result.log_bolometric_shift + 0.8).abs() < 2e-14);
    assert!(result.screen_connection_integral.abs() < 1e-14);
    let expected: Vec<f64> = state.iter().map(|x| x * (-0.8_f64).exp()).collect();
    assert!(max_abs(&result.coherency, &expected) < 3e-14);
}

#[test]
fn pure_screen_twist_rotates_linear_polarization_even_when_direction_is_fixed() {
    let direction = [0.0, 0.0, 1.0];
    let state = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0];
    let omega = 0.7;
    let step = 0.4;
    let background = HomogeneousRayBackground {
        triad_rotation: [0.0, 0.0, omega],
        ..HomogeneousRayBackground::zero()
    };
    let result = transport_characteristic(
        direction,
        &background,
        &background,
        step,
        1,
        &state,
        ScreenInputPolicy::Reject { tolerance: 1e-14 },
    )
    .unwrap();
    let angle = omega * step;
    let (s, c) = angle.sin_cos();
    let expected = [c * c, s * s, 0.0, s * c, 0.0, 0.0, 0.0, 0.0, 0.0];
    assert!(max_abs(&result.direction, &direction) < 1e-14);
    assert!(max_abs(&result.coherency, &expected) < 3e-14);
    assert!((result.screen_connection_integral - angle).abs() < 2e-14);
}

fn dot3(a: [f64; 3], b: [f64; 3]) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}

fn norm3(a: [f64; 3]) -> f64 {
    dot3(a, a).sqrt()
}

fn normalize3(a: [f64; 3]) -> [f64; 3] {
    let n = norm3(a);
    [a[0] / n, a[1] / n, a[2] / n]
}

fn cross3(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
}

fn pack9(m: [[f64; 3]; 3]) -> [f64; 9] {
    [
        m[0][0],
        m[1][1],
        m[2][2],
        0.5 * (m[0][1] + m[1][0]),
        0.5 * (m[0][2] + m[2][0]),
        0.5 * (m[1][2] + m[2][1]),
        0.5 * (m[1][2] - m[2][1]),
        0.5 * (m[2][0] - m[0][2]),
        0.5 * (m[0][1] - m[1][0]),
    ]
}

fn tangent_frame(e: [f64; 3]) -> ([f64; 3], [f64; 3]) {
    let e = normalize3(e);
    let seed = if e[0].abs() < 0.8 {
        [1.0, 0.0, 0.0]
    } else {
        [0.0, 1.0, 0.0]
    };
    let parallel = dot3(seed, e);
    let u = normalize3([
        seed[0] - parallel * e[0],
        seed[1] - parallel * e[1],
        seed[2] - parallel * e[2],
    ]);
    (u, cross3(e, u))
}

fn physical_coherency(e: [f64; 3], a: f64, b: f64, q: f64, v: f64) -> [f64; 9] {
    let (u, w) = tangent_frame(e);
    let mut m = [[0.0; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            m[i][j] = a * u[i] * u[j]
                + b * w[i] * w[j]
                + q * (u[i] * w[j] + w[i] * u[j])
                + v * (u[i] * w[j] - w[i] * u[j]);
        }
    }
    pack9(m)
}

fn test_background() -> HomogeneousRayBackground {
    HomogeneousRayBackground {
        expansion: 0.8,
        shear: [[-0.3, 0.04, 0.11], [0.04, 0.2, -0.05], [0.11, -0.05, 0.1]],
        structure_n: [[0.7, 0.03, -0.02], [0.03, -0.2, 0.06], [-0.02, 0.06, 0.4]],
        class_b_a: [0.09, -0.04, 0.03],
        triad_rotation: [0.13, -0.17, 0.08],
    }
}

#[test]
fn minkowski_limit_is_identity() {
    let direction = normalize3([0.3, -0.4, 0.7]);
    let state = physical_coherency(direction, 0.8, 0.4, 0.1, 0.05);
    let zero = HomogeneousRayBackground::zero();
    let result = transport_characteristic(
        direction,
        &zero,
        &zero,
        2.0,
        3,
        &state,
        ScreenInputPolicy::Reject { tolerance: 1e-13 },
    )
    .unwrap();
    assert!(max_abs(&result.direction, &direction) < 2e-14);
    assert!(max_abs(&result.coherency, &state) < 3e-14);
    assert!(result.log_energy_shift.abs() < 1e-15);
    assert!(result.screen_connection_integral.abs() < 1e-15);
}

#[test]
fn typeii_adapter_matches_direction_and_screen_authority_formulas() {
    let state = [0.21, -0.04, 0.07, 0.83, 0.37];
    let e = normalize3([0.31, -0.52, 0.79]);
    let background = typeii_background_from_state(&state).unwrap();
    let got = liouville_coefficients(e, &background).unwrap();
    let sqrt3 = 3.0_f64.sqrt();
    let sigma = [
        [-2.0 * state[0], 0.0, sqrt3 * state[2]],
        [0.0, state[0] + sqrt3 * state[1], 0.0],
        [sqrt3 * state[2], 0.0, state[0] - sqrt3 * state[1]],
    ];
    let se = [dot3(sigma[0], e), dot3(sigma[1], e), dot3(sigma[2], e)];
    let see = dot3(e, se);
    let shear_v = [
        -se[0] + see * e[0],
        -se[1] + see * e[1],
        -se[2] + see * e[2],
    ];
    let omega = [0.0, sqrt3 * state[2], 0.0];
    let ne = [state[3] * e[0], 0.0, 0.0];
    let structure_v = cross3([omega[0] + ne[0], omega[1], omega[2]], e);
    let expected_v = [
        shear_v[0] + structure_v[0],
        shear_v[1] + structure_v[1],
        shear_v[2] + structure_v[2],
    ];
    assert!(max_abs(&got.direction_rate, &expected_v) < 3e-15);
    assert!(dot3(e, got.direction_rate).abs() < 2e-15);
    assert!((got.log_energy_rate + 1.0 + see).abs() < 2e-15);
    let expected_omega = sqrt3 * state[2] * e[1] + state[3] * e[0] * e[0] - 0.5 * state[3];
    assert!((got.screen_connection_rate - expected_omega).abs() < 2e-15);
}

#[test]
fn global_electron_tilt_does_not_enter_geometric_liouville_coefficients() {
    let first = [0.2, -0.03, 0.04, 0.7, -0.8];
    let mut second = first;
    second[4] = 0.91;
    let b1 = typeii_background_from_state(&first).unwrap();
    let b2 = typeii_background_from_state(&second).unwrap();
    assert_eq!(b1, b2);
    let e = normalize3([0.4, 0.2, -0.9]);
    assert_eq!(
        liouville_coefficients(e, &b1).unwrap(),
        liouville_coefficients(e, &b2).unwrap()
    );
}

#[test]
fn finite_step_has_the_declared_instantaneous_tensor_rhs() {
    let direction = normalize3([0.2, -0.6, 0.7]);
    let state = physical_coherency(direction, 0.9, 0.35, -0.08, 0.04);
    let background = test_background();
    let (de, dj, _) = polarized_bolometric_rhs(
        direction,
        &background,
        &state,
        ScreenInputPolicy::Reject { tolerance: 1e-13 },
    )
    .unwrap();
    let h = 1e-5;
    let plus = transport_characteristic(
        direction,
        &background,
        &background,
        h,
        1,
        &state,
        ScreenInputPolicy::Reject { tolerance: 1e-13 },
    )
    .unwrap();
    let minus = transport_characteristic(
        direction,
        &background,
        &background,
        -h,
        1,
        &state,
        ScreenInputPolicy::Reject { tolerance: 1e-13 },
    )
    .unwrap();
    let de_fd = [
        (plus.direction[0] - minus.direction[0]) / (2.0 * h),
        (plus.direction[1] - minus.direction[1]) / (2.0 * h),
        (plus.direction[2] - minus.direction[2]) / (2.0 * h),
    ];
    let dj_fd: Vec<f64> = plus
        .coherency
        .iter()
        .zip(&minus.coherency)
        .map(|(a, b)| (a - b) / (2.0 * h))
        .collect();
    assert!(max_abs(&de_fd, &de) < 2e-9);
    assert!(max_abs(&dj_fd, &dj) < 8e-9);
}

#[test]
fn lie_congruence_preserves_screen_carrier_cone_and_v_zero_lane() {
    let direction = normalize3([0.4, -0.5, 0.7]);
    let state = physical_coherency(direction, 0.9, 0.3, 0.12, 0.0);
    let initial_min = minimum_coherency_eigenvalue(&[direction], &state).unwrap();
    let mut end = test_background();
    end.expansion = 0.5;
    end.triad_rotation = [-0.07, 0.21, -0.12];
    end.structure_n[0][0] = 0.95;
    let result = transport_characteristic(
        direction,
        &test_background(),
        &end,
        0.7,
        48,
        &state,
        ScreenInputPolicy::Reject { tolerance: 1e-13 },
    )
    .unwrap();
    assert!(
        result.max_screen_leakage < 4e-15,
        "{}",
        result.max_screen_leakage
    );
    let expected_min = initial_min * result.log_bolometric_shift.exp();
    assert!((result.minimum_coherency_eigenvalue - expected_min).abs() < 2e-13);
    assert!(result.coherency[6].abs() < 2e-14);
    assert!(result.coherency[7].abs() < 2e-14);
    assert!(result.coherency[8].abs() < 2e-14);
}

#[test]
fn symmetric_midpoint_transport_roundtrips_when_background_path_is_reversed() {
    let direction = normalize3([0.23, 0.71, -0.66]);
    let state = physical_coherency(direction, 0.75, 0.45, -0.09, 0.03);
    let start = test_background();
    let mut end = start;
    end.expansion = 1.1;
    end.shear[0][2] = -0.08;
    end.shear[2][0] = -0.08;
    end.structure_n[1][2] = -0.04;
    end.structure_n[2][1] = -0.04;
    end.triad_rotation = [-0.1, 0.05, 0.19];
    let forward = transport_characteristic(
        direction,
        &start,
        &end,
        0.35,
        96,
        &state,
        ScreenInputPolicy::Reject { tolerance: 1e-13 },
    )
    .unwrap();
    let backward = transport_characteristic(
        forward.direction,
        &end,
        &start,
        -0.35,
        96,
        &forward.coherency,
        ScreenInputPolicy::Reject { tolerance: 1e-12 },
    )
    .unwrap();
    let direction_error = max_abs(&backward.direction, &direction);
    let coherency_error = max_abs(&backward.coherency, &state);
    let log_error = (forward.log_energy_shift + backward.log_energy_shift).abs();
    println!(
        "TYPEII_LIOUVILLE_ROUNDTRIP direction={direction_error:.16e} coherency={coherency_error:.16e} log_energy={log_error:.16e}"
    );
    assert!(direction_error < 2e-12);
    assert!(coherency_error < 3e-12);
    assert!(log_error < 2e-12);
}

fn characteristic_error(
    coarse: &bianchi_rustcore::generated::typeii_polarized_liouville::PolarizedCharacteristicResult,
    reference: &bianchi_rustcore::generated::typeii_polarized_liouville::PolarizedCharacteristicResult,
) -> f64 {
    max_abs(&coarse.direction, &reference.direction)
        .max(max_abs(&coarse.coherency, &reference.coherency))
        .max((coarse.log_energy_shift - reference.log_energy_shift).abs())
        .max((coarse.screen_connection_integral - reference.screen_connection_integral).abs())
}

#[test]
fn time_dependent_characteristic_is_second_order() {
    let direction = normalize3([0.32, -0.44, 0.84]);
    let state = physical_coherency(direction, 0.8, 0.35, 0.07, -0.02);
    let start = [0.24, 0.015, -0.07, 0.82, 0.1];
    let end = [0.18, -0.055, 0.09, 0.71, -0.7];
    let solve = |n| {
        transport_typeii_characteristic(
            direction,
            &start,
            &end,
            0.6,
            n,
            &state,
            ScreenInputPolicy::Reject { tolerance: 1e-13 },
        )
        .unwrap()
    };
    let reference = solve(8192);
    let e4 = characteristic_error(&solve(4), &reference);
    let e8 = characteristic_error(&solve(8), &reference);
    let e16 = characteristic_error(&solve(16), &reference);
    let e32 = characteristic_error(&solve(32), &reference);
    println!(
        "TYPEII_LIOUVILLE_CONVERGENCE n=4,8,16,32 errors={e4:.16e},{e8:.16e},{e16:.16e},{e32:.16e} ratios={:.12},{:.12},{:.12}",
        e4 / e8,
        e8 / e16,
        e16 / e32,
    );
    assert!(e4 / e8 > 3.6, "e4={e4} e8={e8}");
    assert!(e8 / e16 > 3.6, "e8={e8} e16={e16}");
    assert!(e16 / e32 > 3.6, "e16={e16} e32={e32}");
}

fn curved_background(fraction: f64) -> HomogeneousRayBackground {
    let f2 = fraction * fraction;
    let sigma_00 = -0.18 + 0.07 * fraction + 0.09 * f2;
    let sigma_11 = 0.11 - 0.05 * fraction + 0.03 * f2;
    HomogeneousRayBackground {
        expansion: 0.7 + 0.2 * fraction + 0.12 * f2,
        shear: [
            [
                sigma_00,
                0.03 + 0.02 * f2,
                0.08 - 0.13 * fraction + 0.04 * f2,
            ],
            [0.03 + 0.02 * f2, sigma_11, -0.04 + 0.06 * fraction],
            [
                0.08 - 0.13 * fraction + 0.04 * f2,
                -0.04 + 0.06 * fraction,
                -sigma_00 - sigma_11,
            ],
        ],
        structure_n: [
            [0.65 + 0.2 * f2, 0.02 * fraction, -0.03 + 0.01 * f2],
            [0.02 * fraction, -0.12 + 0.04 * fraction, 0.05 - 0.02 * f2],
            [-0.03 + 0.01 * f2, 0.05 - 0.02 * f2, 0.31 - 0.06 * fraction],
        ],
        class_b_a: [0.04 - 0.03 * fraction, -0.02 + 0.04 * f2, 0.01 * fraction],
        triad_rotation: [0.06 + 0.03 * f2, -0.09 + 0.07 * fraction, 0.04 - 0.02 * f2],
    }
}

fn externally_piecewise_linear_solution(
    panels: usize,
    direction: [f64; 3],
    state: &[f64],
) -> ([f64; 3], Vec<f64>, f64, f64) {
    let total_step = 0.7;
    let mut direction = direction;
    let mut state = state.to_vec();
    let mut log_energy = 0.0;
    let mut screen_connection = 0.0;
    for panel in 0..panels {
        let left = panel as f64 / panels as f64;
        let right = (panel + 1) as f64 / panels as f64;
        let result = transport_characteristic(
            direction,
            &curved_background(left),
            &curved_background(right),
            total_step / panels as f64,
            64,
            &state,
            ScreenInputPolicy::Reject { tolerance: 1e-12 },
        )
        .unwrap();
        direction = result.direction;
        state = result.coherency;
        log_energy += result.log_energy_shift;
        screen_connection += result.screen_connection_integral;
    }
    (direction, state, log_energy, screen_connection)
}

fn external_background_error(
    coarse: &([f64; 3], Vec<f64>, f64, f64),
    reference: &bianchi_rustcore::generated::typeii_polarized_liouville::PolarizedCharacteristicResult,
) -> f64 {
    max_abs(&coarse.0, &reference.direction)
        .max(max_abs(&coarse.1, &reference.coherency))
        .max((coarse.2 - reference.log_energy_shift).abs())
        .max((coarse.3 - reference.screen_connection_integral).abs())
}

#[test]
fn external_background_panel_refinement_is_second_order() {
    // Break caught: refining only internal substeps while retaining one endpoint
    // lerp can hide the dominant external background-reconstruction error.
    let direction = normalize3([0.29, -0.51, 0.81]);
    let state = physical_coherency(direction, 0.82, 0.33, -0.06, 0.025);
    let reference = transport_characteristic_profile(
        direction,
        0.7,
        8192,
        &state,
        ScreenInputPolicy::Reject { tolerance: 1e-13 },
        curved_background,
    )
    .unwrap();
    let e1 = external_background_error(
        &externally_piecewise_linear_solution(1, direction, &state),
        &reference,
    );
    let e2 = external_background_error(
        &externally_piecewise_linear_solution(2, direction, &state),
        &reference,
    );
    let e4 = external_background_error(
        &externally_piecewise_linear_solution(4, direction, &state),
        &reference,
    );
    assert!(e1 / e2 > 3.4, "e1={e1} e2={e2}");
    assert!(e2 / e4 > 3.4, "e2={e2} e4={e4}");
}

#[test]
fn noncontractive_coarse_midpoint_is_boundedly_subdivided() {
    // Break caught: a valid finite characteristic was rejected solely because
    // one coarse implicit-midpoint fixed point missed the 32-iteration bound.
    let direction = [0.0, 0.0, 1.0];
    let state = [1.0, 0.5, 0.0, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0];
    let strong = scaled_test_background(2.0);
    let coarse = transport_characteristic(
        direction,
        &strong,
        &strong,
        1.0,
        1,
        &state,
        ScreenInputPolicy::Reject { tolerance: 1e-13 },
    )
    .unwrap();
    let explicit_halves = transport_characteristic(
        direction,
        &strong,
        &strong,
        1.0,
        2,
        &state,
        ScreenInputPolicy::Reject { tolerance: 1e-13 },
    )
    .unwrap();
    assert!(characteristic_error(&coarse, &explicit_halves) < 2e-13);
}

fn scaled_test_background(factor: f64) -> HomogeneousRayBackground {
    let base = test_background();
    let scale = |value: f64| factor * value;
    HomogeneousRayBackground {
        expansion: 0.2,
        shear: base.shear.map(|row| row.map(scale)),
        structure_n: base.structure_n.map(|row| row.map(scale)),
        class_b_a: base.class_b_a.map(scale),
        triad_rotation: base.triad_rotation.map(scale),
    }
}

#[test]
fn midpoint_subdivision_budget_is_finite_and_fail_closed() {
    let error = transport_characteristic(
        [0.0, 0.0, 1.0],
        &scaled_test_background(1.0e6),
        &scaled_test_background(1.0e6),
        1.0,
        1,
        &[1.0, 0.5, 0.0, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0],
        ScreenInputPolicy::Reject { tolerance: 1e-13 },
    )
    .unwrap_err();
    assert!(matches!(
        error,
        PolarizedLiouvilleError::MidpointDidNotConverge {
            bisections: MAX_MIDPOINT_BISECTIONS,
            ..
        }
    ));
}

#[test]
fn positive_screen_twist_has_right_handed_basis_free_sign() {
    // Break caught: reversing the SO(3) generator sign leaves direction fixed
    // but reverses the physical tensor rotation.  No Q/U or E/B convention is
    // introduced: the assertion is directly on the rank-9 spatial carrier.
    let direction = [0.0, 0.0, 1.0];
    let state = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0];
    let solve = |omega| {
        let background = HomogeneousRayBackground {
            triad_rotation: [0.0, 0.0, omega],
            ..HomogeneousRayBackground::zero()
        };
        transport_characteristic(
            direction,
            &background,
            &background,
            0.4,
            1,
            &state,
            ScreenInputPolicy::Reject { tolerance: 1e-14 },
        )
        .unwrap()
    };
    let positive = solve(0.7);
    let negative = solve(-0.7);
    assert!(positive.coherency[3] > 0.0);
    assert!(negative.coherency[3] < 0.0);
    assert!((positive.coherency[3] + negative.coherency[3]).abs() < 3e-14);
    assert!(max_abs(&positive.direction, &direction) < 1e-14);
    assert!(max_abs(&negative.direction, &direction) < 1e-14);
}

#[test]
fn invalid_substeps_and_longitudinal_input_fail_closed() {
    let e = [0.0, 0.0, 1.0];
    let zero = HomogeneousRayBackground::zero();
    let state = [1.0, 0.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 0.0];
    let err = transport_characteristic(e, &zero, &zero, 0.1, 0, &state, ScreenInputPolicy::Project)
        .unwrap_err();
    assert!(matches!(
        err,
        PolarizedLiouvilleError::InvalidSubsteps { .. }
    ));
    let err = transport_characteristic(
        e,
        &zero,
        &zero,
        0.1,
        1,
        &state,
        ScreenInputPolicy::Reject { tolerance: 1e-14 },
    )
    .unwrap_err();
    assert!(matches!(err, PolarizedLiouvilleError::Carrier(_)));
}

#[test]
fn transverse_but_indefinite_coherency_fails_closed() {
    let direction = [0.0, 0.0, 1.0];
    let zero = HomogeneousRayBackground::zero();
    // Screen block diag(1, -1) has zero trace and a negative eigenvalue.
    let state = [1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0];
    let error = transport_characteristic(
        direction,
        &zero,
        &zero,
        0.1,
        1,
        &state,
        ScreenInputPolicy::Project,
    )
    .unwrap_err();
    assert!(matches!(error, PolarizedLiouvilleError::Carrier(_)));
}

fn unpack9(p: &[f64]) -> [[f64; 3]; 3] {
    [
        [p[0], p[3] + p[8], p[4] - p[7]],
        [p[3] - p[8], p[1], p[5] + p[6]],
        [p[4] + p[7], p[5] - p[6], p[2]],
    ]
}

fn transpose3(a: [[f64; 3]; 3]) -> [[f64; 3]; 3] {
    [
        [a[0][0], a[1][0], a[2][0]],
        [a[0][1], a[1][1], a[2][1]],
        [a[0][2], a[1][2], a[2][2]],
    ]
}

fn mm3(a: [[f64; 3]; 3], b: [[f64; 3]; 3]) -> [[f64; 3]; 3] {
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

fn mv3(a: [[f64; 3]; 3], v: [f64; 3]) -> [f64; 3] {
    [dot3(a[0], v), dot3(a[1], v), dot3(a[2], v)]
}

fn rotate_packed(rotation: [[f64; 3]; 3], packed: &[f64]) -> [f64; 9] {
    pack9(mm3(mm3(rotation, unpack9(packed)), transpose3(rotation)))
}

fn rotate_background(
    rotation: [[f64; 3]; 3],
    background: HomogeneousRayBackground,
) -> HomogeneousRayBackground {
    HomogeneousRayBackground {
        expansion: background.expansion,
        shear: mm3(mm3(rotation, background.shear), transpose3(rotation)),
        structure_n: mm3(mm3(rotation, background.structure_n), transpose3(rotation)),
        class_b_a: mv3(rotation, background.class_b_a),
        triad_rotation: mv3(rotation, background.triad_rotation),
    }
}

#[test]
fn bolometric_tensor_rotation_does_not_change_trace_rate() {
    let direction = normalize3([0.2, -0.3, 0.93]);
    let state = physical_coherency(direction, 0.8, 0.4, 0.12, 0.07);
    let background = test_background();
    let (_, rhs, coefficients) = polarized_bolometric_rhs(
        direction,
        &background,
        &state,
        ScreenInputPolicy::Reject { tolerance: 1e-13 },
    )
    .unwrap();
    let trace = state[0] + state[1] + state[2];
    let trace_rhs = rhs[0] + rhs[1] + rhs[2];
    assert!((trace_rhs - coefficients.log_bolometric_rate * trace).abs() < 3e-14);
}

#[test]
fn generic_homogeneous_tensor_lane_is_covariant_under_proper_frame_rotation() {
    let angle = 0.41_f64;
    let (s, c) = angle.sin_cos();
    let rotation = [[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]];
    let direction = normalize3([0.37, -0.48, 0.79]);
    let state = physical_coherency(direction, 0.85, 0.31, -0.06, 0.025);
    let start = test_background();
    let mut end = start;
    end.expansion = 1.05;
    end.triad_rotation = [-0.06, 0.15, 0.21];
    end.class_b_a = [-0.03, 0.08, 0.05];
    let original = transport_characteristic(
        direction,
        &start,
        &end,
        0.31,
        64,
        &state,
        ScreenInputPolicy::Reject { tolerance: 1e-13 },
    )
    .unwrap();
    let rotated = transport_characteristic(
        mv3(rotation, direction),
        &rotate_background(rotation, start),
        &rotate_background(rotation, end),
        0.31,
        64,
        &rotate_packed(rotation, &state),
        ScreenInputPolicy::Reject { tolerance: 1e-13 },
    )
    .unwrap();
    assert!(max_abs(&rotated.direction, &mv3(rotation, original.direction)) < 3e-13);
    assert!(
        max_abs(
            &rotated.coherency,
            &rotate_packed(rotation, &original.coherency),
        ) < 5e-13
    );
    assert!((rotated.log_energy_shift - original.log_energy_shift).abs() < 2e-13);
    assert!(
        (rotated.screen_connection_integral - original.screen_connection_integral).abs() < 2e-13
    );
}

#[test]
fn exact_type_i_boundary_with_off_diagonal_shear_requires_an_explicit_gauge_choice() {
    let err = typeii_background_from_state(&[0.2, 0.0, 0.03, 0.0, 0.1]).unwrap_err();
    assert!(matches!(
        err,
        PolarizedLiouvilleError::DegenerateTypeIIGauge { .. }
    ));
    let regular = typeii_background_from_state(&[0.2, 0.0, 0.0, 0.0, 0.1]).unwrap();
    assert_eq!(regular.triad_rotation, [0.0; 3]);
}

// Generated from the independent coordinate-metric oracle, not from the Rust
// tetrad implementation.  Regenerate the literals from the repository root:
//   python3 compiler/validation/typeii_polarized_liouville_coordinate_oracle.py \
//     --print-rust-golden
// Validate their numerical (not byte-serialization) identity:
//   python3 compiler/validation/typeii_polarized_liouville_coordinate_oracle.py \
//     --check-rust-golden runtime/rust/typeii/tests/typeii_polarized_liouville_unit.rs
const COORDINATE_ORACLE_DIRECTION: [f64; 3] =
    [0.4473748161534887, -0.44457736075982984, 0.7760198091359887];
const COORDINATE_ORACLE_LOG_ENERGY_SHIFT: f64 = -0.08016379273330285;
const COORDINATE_ORACLE_SPATIAL_TRANSPORT: [[f64; 3]; 3] = [
    [
        0.9961054721833895,
        0.08026238004918093,
        0.036494364429974196,
    ],
    [
        -0.07953498528196087,
        0.9966115429613207,
        -0.0209670825928151,
    ],
    [
        -0.03805357279553649,
        0.01798284696861173,
        0.9991138788008092,
    ],
];

#[test]
fn independent_coordinate_bianchi_ii_oracle_matches_direction_redshift_and_screen_rotation() {
    let t0 = 1.0_f64;
    let step = 0.25_f64;
    let exponents = [0.4_f64, 0.7_f64, 0.25_f64];
    let direction = [0.4514616300345193, -0.39320851648167815, 0.8009803113515666];
    let state = physical_coherency(direction, 0.8, 0.35, 0.07, 0.02);
    let result = transport_characteristic_profile(
        direction,
        step,
        4096,
        &state,
        ScreenInputPolicy::Reject { tolerance: 1e-13 },
        |fraction: f64| {
            let t: f64 = t0 + step * fraction;
            let expansion = exponents.iter().sum::<f64>() / (3.0 * t);
            let shear = [
                [exponents[0] / t - expansion, 0.0, 0.0],
                [0.0, exponents[1] / t - expansion, 0.0],
                [0.0, 0.0, exponents[2] / t - expansion],
            ];
            HomogeneousRayBackground {
                expansion,
                shear,
                structure_n: [[t.powf(-0.55), 0.0, 0.0], [0.0; 3], [0.0; 3]],
                class_b_a: [0.0; 3],
                triad_rotation: [0.0; 3],
            }
        },
    )
    .unwrap();
    assert!(max_abs(&result.direction, &COORDINATE_ORACLE_DIRECTION) < 3e-10);
    assert!((result.log_energy_shift - COORDINATE_ORACLE_LOG_ENERGY_SHIFT).abs() < 5e-11);
    for i in 0..3 {
        assert!(
            max_abs(
                &result.spatial_transport[i],
                &COORDINATE_ORACLE_SPATIAL_TRANSPORT[i],
            ) < 3e-10
        );
    }
    assert!(result.transport_orthogonality_defect < 2e-13);
    assert!(result.transport_determinant_defect < 2e-13);
}

#[test]
fn diagonal_bianchi_i_direction_and_redshift_match_exact_tetrad_momenta() {
    let direction = normalize3([0.37, -0.52, 0.77]);
    let state = physical_coherency(direction, 0.8, 0.4, -0.05, 0.01);
    let expansion = 0.4_f64;
    let shear_diagonal = [-0.1_f64, 0.2_f64, -0.1_f64];
    let background = HomogeneousRayBackground {
        expansion,
        shear: [
            [shear_diagonal[0], 0.0, 0.0],
            [0.0, shear_diagonal[1], 0.0],
            [0.0, 0.0, shear_diagonal[2]],
        ],
        ..HomogeneousRayBackground::zero()
    };
    let step = 0.8_f64;
    let result = transport_characteristic(
        direction,
        &background,
        &background,
        step,
        1024,
        &state,
        ScreenInputPolicy::Reject { tolerance: 1e-13 },
    )
    .unwrap();
    let rates = [
        expansion + shear_diagonal[0],
        expansion + shear_diagonal[1],
        expansion + shear_diagonal[2],
    ];
    let momentum = [
        direction[0] * (-rates[0] * step).exp(),
        direction[1] * (-rates[1] * step).exp(),
        direction[2] * (-rates[2] * step).exp(),
    ];
    let energy = norm3(momentum);
    let expected_direction = [
        momentum[0] / energy,
        momentum[1] / energy,
        momentum[2] / energy,
    ];
    assert!(max_abs(&result.direction, &expected_direction) < 2e-9);
    assert!((result.log_energy_shift - energy.ln()).abs() < 2e-9);
}

#[test]
fn invalid_direction_and_non_geometric_backgrounds_fail_closed() {
    let state = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0];
    let zero = HomogeneousRayBackground::zero();
    let err = transport_characteristic(
        [0.0; 3],
        &zero,
        &zero,
        0.1,
        1,
        &state,
        ScreenInputPolicy::Project,
    )
    .unwrap_err();
    assert!(matches!(
        err,
        PolarizedLiouvilleError::InvalidDirection { .. }
    ));

    let mut nonsymmetric_shear = zero;
    nonsymmetric_shear.shear[0][1] = 0.2;
    let err = liouville_coefficients([0.0, 0.0, 1.0], &nonsymmetric_shear).unwrap_err();
    assert!(matches!(
        err,
        PolarizedLiouvilleError::BackgroundContractViolation { .. }
    ));

    let mut traced_shear = zero;
    traced_shear.shear[0][0] = 0.1;
    let err = liouville_coefficients([0.0, 0.0, 1.0], &traced_shear).unwrap_err();
    assert!(matches!(
        err,
        PolarizedLiouvilleError::BackgroundContractViolation { .. }
    ));

    let mut nonsymmetric_n = zero;
    nonsymmetric_n.structure_n[0][2] = -0.3;
    let err = liouville_coefficients([0.0, 0.0, 1.0], &nonsymmetric_n).unwrap_err();
    assert!(matches!(
        err,
        PolarizedLiouvilleError::BackgroundContractViolation { .. }
    ));
}
