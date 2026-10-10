use bianchi_rustcore::microphysics::{
    axisym_observables::fixed_time_optical_depth,
    frame::MaterialFrame,
    rei::electron_state_from_rei,
    visibility::{VisibilityError, C_M_S, SIGMA_T_M2},
};
use rei_microphysics::{GroupParams, PchipTable, State};

fn table() -> PchipTable {
    PchipTable::new(
        vec![-2., 0., 2.],
        [vec![0.; 2], vec![0.; 2], vec![0.25; 2], vec![-3., -2.5]],
    )
    .unwrap()
}
fn params() -> GroupParams {
    GroupParams {
        redshift: 3.,
        n_h_proper_per_cm3: 2.,
        n_he_proper_per_cm3: 3.,
        hubble_per_s: 1e-16,
        sigma_hi_cm2: [1.; 4],
        sigma_hei_cm2: [1.; 4],
        sigma_heii_cm2: [1.; 4],
        redshift_coeff: [1.; 4],
        source_fraction: [0.25; 4],
        lowgroup_log_opacity: [table(), table()],
    }
}
fn state(x_hii: f64, helium: [f64; 3]) -> State {
    State {
        n_comoving_per_cmpc3: [0.; 4],
        x_hii,
        helium,
        u_erg_per_cm3: 0.,
        gamma_hi_per_s: 0.,
    }
}

#[test]
fn converts_charge_weights_and_agrees_with_fixed_time_slab_at_zero_tilt() {
    let electrons = electron_state_from_rei(&state(0.5, [0.2, 0.3, 0.5]), &params()).unwrap();
    assert_eq!(electrons.number_density_m3(), 4.9e6);
    let rate = electrons
        .scattering_rate_per_normal_second(MaterialFrame::new([0.; 3]).unwrap(), [1., 0., 0.])
        .unwrap();
    assert_eq!(rate, C_M_S * SIGMA_T_M2 * 4.9e6);
    let slab = fixed_time_optical_depth(&[0., 2.], &[4.9e6], 0., 2.).unwrap();
    assert_eq!(slab.optical_depth, 2. * rate);
}

#[test]
fn neutral_and_invalid_legacy_fractions_are_explicit() {
    assert_eq!(
        electron_state_from_rei(&state(0., [1., 0., 0.]), &params())
            .unwrap()
            .number_density_m3(),
        0.
    );
    assert_eq!(
        electron_state_from_rei(&state(1.1, [1., 0., 0.]), &params()).unwrap_err(),
        VisibilityError::InvalidFraction
    );
    assert_eq!(
        electron_state_from_rei(&state(0., [0., 0.8, 0.3]), &params()).unwrap_err(),
        VisibilityError::InvalidFraction
    );
    assert_eq!(
        electron_state_from_rei(&state(0., [f64::NAN, 0., 0.]), &params()).unwrap_err(),
        VisibilityError::InvalidFraction
    );
    assert_eq!(
        electron_state_from_rei(&state(0., [1., 0.3, 0.5]), &params()).unwrap_err(),
        VisibilityError::InvalidFraction
    );
    let mut overflow = params();
    overflow.n_h_proper_per_cm3 = f64::MAX;
    assert_eq!(
        electron_state_from_rei(&state(1., [1., 0., 0.]), &overflow).unwrap_err(),
        VisibilityError::InvalidDensity
    );
}
