//! Focused authenticated-host baseline regressions for LOCAL-01.

use super::typeii_physical_guard::ScreenInputPolicy;
use super::typeii_polarized_liouville::{
    transport_characteristic, typeii_background_from_state, HomogeneousRayBackground,
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

    if let Ok(receipt) = result {
        assert!(receipt.log_energy_shift.is_finite());
        assert!(receipt.log_bolometric_shift.is_finite());
        assert!(receipt.screen_connection_integral.is_finite());
    }
}

#[test]
fn finite_typeii_state_does_not_return_a_nonfinite_background() {
    let result = typeii_background_from_state(&[f64::MAX, 0.0, 0.0, 1.0, 0.0]);
    if let Ok(background) = result {
        let values = background
            .shear
            .into_iter()
            .flatten()
            .chain(background.structure_n.into_iter().flatten())
            .chain(background.class_b_a)
            .chain(background.triad_rotation);
        assert!(values.into_iter().all(f64::is_finite));
    }
}
