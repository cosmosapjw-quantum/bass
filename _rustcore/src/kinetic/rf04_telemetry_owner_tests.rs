//! Focused authenticated-host baseline regressions for LOCAL-01.

use super::typeii_physical_guard::ScreenInputPolicy;
use super::typeii_polarized_liouville::{
    transport_characteristic, transport_characteristic_profile, typeii_background_from_state,
    HomogeneousRayBackground, PolarizedLiouvilleError, MAX_MIDPOINT_BISECTIONS,
};

fn projector_state(direction: [f64; 3]) -> [f64; 9] {
    let [x, y, z] = direction;
    [
        1.0 - x * x,
        1.0 - y * y,
        1.0 - z * z,
        -x * y,
        -x * z,
        -y * z,
        0.0,
        0.0,
        0.0,
    ]
}

fn telemetry_background(strength: f64, fraction: f64) -> HomogeneousRayBackground {
    HomogeneousRayBackground {
        expansion: 0.0,
        shear: [[0.0; 3]; 3],
        structure_n: [
            [strength * (1.0 + 0.1 * fraction), 0.0, 0.0],
            [0.0; 3],
            [0.0; 3],
        ],
        class_b_a: [0.0; 3],
        triad_rotation: [0.0, 0.04 * strength, 0.0],
    }
}

fn hostile_background() -> HomogeneousRayBackground {
    let base = HomogeneousRayBackground {
        expansion: 0.8,
        shear: [[-0.3, 0.04, 0.11], [0.04, 0.2, -0.05], [0.11, -0.05, 0.1]],
        structure_n: [[0.7, 0.03, -0.02], [0.03, -0.2, 0.06], [-0.02, 0.06, 0.4]],
        class_b_a: [0.09, -0.04, 0.03],
        triad_rotation: [0.13, -0.17, 0.08],
    };
    let factor = 1.0e6;
    HomogeneousRayBackground {
        expansion: 0.2,
        shear: base.shear.map(|row| row.map(|value| factor * value)),
        structure_n: base.structure_n.map(|row| row.map(|value| factor * value)),
        class_b_a: base.class_b_a.map(|value| factor * value),
        triad_rotation: base.triad_rotation.map(|value| factor * value),
    }
}

#[test]
fn no_split_receipt_counts_each_root_panel_once() {
    let direction = [0.0, 0.0, 1.0];
    let result = transport_characteristic_profile(
        direction,
        0.25,
        3,
        &projector_state(direction),
        ScreenInputPolicy::Reject { tolerance: 1.0e-13 },
        |_| HomogeneousRayBackground::zero(),
    )
    .unwrap();

    assert_eq!(result.internal_bisection_count, 0);
    assert_eq!(result.max_internal_bisection_depth, 0);
    assert_eq!(result.accepted_subinterval_count, 3);
}

#[test]
fn nested_split_receipt_distinguishes_total_events_from_depth() {
    let direction = [0.3, 0.4, 0.8660254037844386];
    let root_panels = 4_u64;
    let result = transport_characteristic_profile(
        direction,
        4.0,
        root_panels as usize,
        &projector_state(direction),
        ScreenInputPolicy::Reject { tolerance: 1.0e-10 },
        |fraction| telemetry_background(100.0, fraction),
    )
    .unwrap();

    assert!(
        result.internal_bisection_count > result.max_internal_bisection_depth as u64,
        "split events must not be reported as recursion depth"
    );
    assert_eq!(
        result.accepted_subinterval_count,
        root_panels + result.internal_bisection_count
    );
}

#[test]
fn several_root_panel_counts_obey_the_binary_tree_identity() {
    let direction = [0.0, 0.0, 1.0];
    for root_panels in [1_u64, 4, 7] {
        let result = transport_characteristic_profile(
            direction,
            0.5,
            root_panels as usize,
            &projector_state(direction),
            ScreenInputPolicy::Reject { tolerance: 1.0e-13 },
            |_| HomogeneousRayBackground::zero(),
        )
        .unwrap();
        assert_eq!(
            result.accepted_subinterval_count,
            root_panels + result.internal_bisection_count
        );
    }
}

#[test]
fn bounded_midpoint_failure_returns_error_instead_of_a_receipt() {
    let direction = [0.0, 0.0, 1.0];
    let background = hostile_background();
    let error = transport_characteristic(
        direction,
        &background,
        &background,
        1.0,
        1,
        &projector_state(direction),
        ScreenInputPolicy::Reject { tolerance: 1.0e-13 },
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
fn finite_inputs_do_not_return_a_nonfinite_energy_receipt() {
    let direction = [0.0, 0.0, 1.0];
    let background = HomogeneousRayBackground {
        expansion: 1.0,
        ..HomogeneousRayBackground::zero()
    };
    let result = transport_characteristic(
        direction,
        &background,
        &background,
        1.0e308,
        1,
        &projector_state(direction),
        ScreenInputPolicy::Reject { tolerance: 1.0e-13 },
    );

    assert!(matches!(
        result,
        Err(PolarizedLiouvilleError::NonFiniteOutput { .. })
    ));
}

#[test]
fn finite_typeii_state_does_not_return_a_nonfinite_background() {
    let result = typeii_background_from_state(&[f64::MAX, 0.0, 0.0, 1.0, 0.0]);
    assert!(matches!(
        result,
        Err(PolarizedLiouvilleError::NonFiniteBackground { .. })
    ));
}
