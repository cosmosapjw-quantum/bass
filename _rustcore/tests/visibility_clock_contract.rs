use bianchi_rustcore::microphysics::frame::MaterialFrame;
use bianchi_rustcore::microphysics::rei_visibility::{integrate_rei_visibility, ReiOpacityCell};
use bianchi_rustcore::microphysics::visibility::{integrate_visibility, ElectronState, VisibilityError, C_M_S, SIGMA_T_M2};
use bianchi_rustcore::microphysics::visibility_clock::{integrate_clock_visibility, ClockVisibilityError, RayClock, RayClockGrid};

fn close(a: f64, b: f64) {
    assert!((a - b).abs() <= 2e-14 * a.abs().max(b.abs()).max(1e-300), "{a:e} != {b:e}");
}

#[test]
fn three_clocks_preserve_depth_survival_mass_with_varying_cell_a() {
    let q = [0.5, 2.0, 0.0];
    let a = [0.5, 2.0, 0.25];
    let t = [0.0, 1.0, 7.0, 8.0];
    let eta = [0.0, 2.0, 5.0, 9.0];
    let chi = eta.map(|v| C_M_S * v);
    let grids = [
        RayClockGrid::NormalSeconds { edges_seconds: &t },
        RayClockGrid::ConformalSeconds { edges_seconds: &eta, scale_factors: &a },
        RayClockGrid::ConformalLengthMeters { edges_meters: &chi, scale_factors: &a },
    ];
    for grid in grids {
        let out = integrate_clock_visibility(grid, &q, 0.3).unwrap();
        for (got, want) in out.normal_interval_seconds.iter().zip([1.0, 6.0, 1.0]) { close(*got, want); }
        for (got, want) in out.visibility.optical_depth.iter().zip([12.8, 12.3, 0.3, 0.3]) { close(*got, want); }
        for (survival, tau) in out.visibility.survival.iter().zip(&out.visibility.optical_depth) { close(*survival, (-tau).exp()); }
        close(out.visibility.interval_probability.iter().sum::<f64>() + out.visibility.survival[0], (-0.3_f64).exp());
        assert_eq!(out.visibility.interval_probability[2], 0.0);
    }
}

#[test]
fn normal_clock_reuses_existing_result_without_modification() {
    let t = [-3.0, 0.0, 8.0];
    let q = [1e-18, 0.2];
    let old = integrate_visibility(&t, &q, 0.1).unwrap();
    let new = integrate_clock_visibility(RayClockGrid::NormalSeconds { edges_seconds: &t }, &q, 0.1).unwrap();
    assert_eq!(new.clock, RayClock::NormalSeconds);
    assert_eq!(new.visibility.optical_depth, old.optical_depth);
    assert_eq!(new.visibility.survival, old.survival);
    assert_eq!(new.visibility.interval_probability, old.interval_probability);
}

#[test]
fn exact_effective_scale_factor_preserves_frozen_q_for_varying_a() {
    // a(eta)=1+eta; t=eta+eta^2/2; exact cell averages are 1.5 and 3.
    let eta = [0.0, 1.0, 3.0];
    let t = [0.0, 1.5, 7.5];
    let q = [2.0, 5.0];
    let out = integrate_clock_visibility(RayClockGrid::ConformalSeconds { edges_seconds: &eta, scale_factors: &[1.5, 3.0] }, &q, 0.7).unwrap();
    let normal = integrate_visibility(&t, &q, 0.7).unwrap();
    for (x, y) in out.visibility.optical_depth.iter().zip(normal.optical_depth) { close(*x, y); }
    close(out.visibility.optical_depth[0], 33.7);
    let wrong = integrate_clock_visibility(RayClockGrid::ConformalSeconds { edges_seconds: &eta, scale_factors: &[1.0, 2.0] }, &q, 0.7).unwrap();
    assert!((wrong.visibility.optical_depth[0] - 33.7).abs() > 1.0);
}

#[test]
fn physical_electron_state_has_one_doppler_factor_and_conformal_length_c_cancels() {
    let e = ElectronState::new(1e20, 0.0, 0.5, 0.0, 0.0).unwrap();
    let frame = MaterialFrame::new([0.6, 0.0, 0.0]).unwrap();
    let q = e.scattering_rate_per_normal_second(frame, [1.0, 0.0, 0.0]).unwrap();
    let out = integrate_clock_visibility(RayClockGrid::ConformalLengthMeters { edges_meters: &[0.0, 2.0*C_M_S], scale_factors: &[0.25] }, &[q], 0.0).unwrap();
    close(out.interval_rates_per_clock_unit[0], 0.25 * SIGMA_T_M2 * 5e19 * 0.5);
    close(out.visibility.optical_depth[0], C_M_S * SIGMA_T_M2 * 5e19 * 0.5 * 0.5);
}

#[test]
fn actual_rei_state_rates_feed_all_clock_coordinates() {
    let model = rei_microphysics::HHeModel::controlled_fixture();
    let state = rei_microphysics::HHeState::controlled_fixture(&model);
    let frame = MaterialFrame::new([0.6, 0.0, 0.0]).unwrap();
    let cells = [ReiOpacityCell::HHe { model: &model, state: &state, frame, e_normal: [1.0, 0.0, 0.0] }; 2];
    let bridge = integrate_rei_visibility(&[0.0, 1e13, 3e13], &cells, 0.2).unwrap();
    let clock = integrate_clock_visibility(RayClockGrid::ConformalSeconds { edges_seconds: &[0.0, 2e13, 3e13], scale_factors: &[0.5, 2.0] }, &bridge.interval_rates_s_inverse, 0.2).unwrap();
    for (a,b) in bridge.visibility.optical_depth.iter().zip(clock.visibility.optical_depth) { close(*a,b); }
}

#[test]
fn invalid_scale_factors_and_array_mismatch_are_rejected_even_in_vacuum() {
    for a in [0.0, -0.0, -1.0, f64::NAN, f64::INFINITY] {
        assert_eq!(integrate_clock_visibility(RayClockGrid::ConformalSeconds { edges_seconds: &[0.0, 1.0], scale_factors: &[a] }, &[0.0], 0.0).unwrap_err(), ClockVisibilityError::InvalidScaleFactor);
    }
    assert_eq!(integrate_clock_visibility(RayClockGrid::ConformalSeconds { edges_seconds: &[0.0, 1.0], scale_factors: &[] }, &[0.0], 0.0).unwrap_err(), ClockVisibilityError::ScaleFactorCountMismatch);
}

#[test]
fn existing_invalid_grid_rate_and_tail_validation_remains_active() {
    for (edges, q, tail) in [
        (vec![0.0], vec![], 0.0),
        (vec![0.0, 1.0], vec![], 0.0),
        (vec![1.0, 0.0], vec![1.0], 0.0),
        (vec![0.0, 0.0], vec![1.0], 0.0),
        (vec![0.0, f64::NAN], vec![1.0], 0.0),
        (vec![0.0, 1.0], vec![-1.0], 0.0),
        (vec![0.0, 1.0], vec![f64::NAN], 0.0),
        (vec![0.0, 1.0], vec![1.0], -1.0),
        (vec![0.0, 1.0], vec![1.0], f64::INFINITY),
    ] {
        assert!(integrate_clock_visibility(RayClockGrid::NormalSeconds { edges_seconds: &edges }, &q, tail).is_err());
    }
    assert_eq!(integrate_clock_visibility(RayClockGrid::ConformalLengthMeters { edges_meters: &[0.0, 1.0], scale_factors: &[1e-300] }, &[-f64::from_bits(1)], 0.0).unwrap_err(), ClockVisibilityError::Visibility(VisibilityError::InvalidRate));
}

#[test]
fn conversion_overflow_and_underflow_cannot_silently_erase_opacity_or_time() {
    for (edges, a, q) in [
        (vec![0.0, 1.0], 2.0, f64::MAX),
        (vec![0.0, 2.0], f64::MAX, 0.0),
        (vec![0.0, 1.0], f64::from_bits(1), 0.5),
        (vec![0.0, 0.5], f64::from_bits(1), 0.0),
    ] {
        assert_eq!(integrate_clock_visibility(RayClockGrid::ConformalSeconds { edges_seconds: &edges, scale_factors: &[a] }, &[q], 0.0).unwrap_err(), ClockVisibilityError::UnrepresentableConversion);
    }
    assert_eq!(integrate_clock_visibility(RayClockGrid::ConformalLengthMeters { edges_meters: &[0.0, 1.0], scale_factors: &[f64::from_bits(1)] }, &[0.0], 0.0).unwrap_err(), ClockVisibilityError::UnrepresentableConversion);
}

#[test]
fn thin_and_opaque_cells_retain_existing_probability_convention() {
    let thin = integrate_clock_visibility(RayClockGrid::ConformalSeconds { edges_seconds: &[0.0, 2.0], scale_factors: &[0.5] }, &[1e-18], 0.0).unwrap();
    assert!(thin.visibility.interval_probability[0] > 0.0);
    close(thin.visibility.interval_probability[0], 1e-18);
    let thick = integrate_clock_visibility(RayClockGrid::ConformalSeconds { edges_seconds: &[0.0, 2.0], scale_factors: &[0.5] }, &[1000.0], 0.0).unwrap();
    assert_eq!(thick.visibility.survival, vec![0.0, 1.0]);
    assert_eq!(thick.visibility.interval_probability, vec![1.0]);
}
