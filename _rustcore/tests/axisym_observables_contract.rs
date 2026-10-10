use bianchi_rustcore::microphysics::axisym_observables::{
    fixed_time_optical_depth, with_observer_tail, FixedTimeSlab, ObserverTail,
};
use bianchi_rustcore::microphysics::visibility::{C_M_S, SIGMA_T_M2};
#[test]
fn fixed_proper_time_is_direction_free_and_clips_cells() {
    let s = fixed_time_optical_depth(&[0., 1., 3.], &[2., 4.], 0.5, 2.).unwrap();
    assert_eq!(s.optical_depth, C_M_S * SIGMA_T_M2 * (2. * 0.5 + 4. * 1.));
    assert!(with_observer_tail(s, ObserverTail::Unknown)
        .unwrap()
        .total_optical_depth
        .is_none());
    assert_eq!(
        with_observer_tail(s, ObserverTail::Known(2.))
            .unwrap()
            .total_optical_depth,
        Some(s.optical_depth + 2.)
    );
}
#[test]
fn bad_clock_or_density_is_rejected() {
    assert!(fixed_time_optical_depth(&[0., 1.], &[-1.], 0., 1.).is_err());
    assert!(fixed_time_optical_depth(&[0., 1.], &[1.], -1., 1.).is_err());
    let slab = fixed_time_optical_depth(&[0., 1.], &[1.], 0., 1.).unwrap();
    assert!(with_observer_tail(
        FixedTimeSlab {
            optical_depth: f64::NAN,
            ..slab
        },
        ObserverTail::Unknown
    )
    .is_err());
    let thin = fixed_time_optical_depth(&[0., 1e308], &[1e-308], 0., 1e308).unwrap();
    assert!(thin.optical_depth > 0.0);
    assert!(with_observer_tail(
        FixedTimeSlab {
            optical_depth: 1.5e308,
            ..slab
        },
        ObserverTail::Known(1e308)
    )
    .is_err());
}
