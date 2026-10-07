//! Frozen analytic contract: Dossier III §§1.17, 1.21–22; V §12.1.
use bianchi_rustcore::microphysics::frame::MaterialFrame;
use bianchi_rustcore::microphysics::visibility::{
    compare_opacity, integrate_visibility, ElectronState, C_M_S, SIGMA_T_M2,
};

fn close(a: f64, b: f64, tol: f64) {
    assert!((a - b).abs() <= tol, "{a:e} != {b:e}");
}

#[test]
fn chemistry_and_tilt_use_one_proper_electron_density() {
    let state = ElectronState::new(10.0, 2.0, 0.5, 0.25, 0.5).unwrap();
    close(state.number_density_m3(), 7.5, 1e-14);
    let rest = MaterialFrame::new([0.0; 3]).unwrap();
    let moving = MaterialFrame::new([0.6, 0.0, 0.0]).unwrap();
    let q = state
        .scattering_rate_per_normal_second(rest, [1.0, 0.0, 0.0])
        .unwrap();
    close(q / (C_M_S * SIGMA_T_M2), 7.5, 1e-14);
    close(
        state
            .scattering_rate_per_normal_second(moving, [1.0, 0.0, 0.0])
            .unwrap()
            / q,
        0.5,
        1e-14,
    );
    close(
        state
            .scattering_rate_per_normal_second(moving, [-1.0, 0.0, 0.0])
            .unwrap()
            / q,
        2.0,
        1e-14,
    );
    let neutral = ElectronState::new(10.0, 2.0, 0.0, 0.0, 0.0).unwrap();
    assert_eq!(neutral.number_density_m3(), 0.0);
    assert_eq!(
        ElectronState::new(10.0, 2.0, 1.0, 0.0, 1.0)
            .unwrap()
            .number_density_m3(),
        14.0
    );
}

#[test]
fn constant_rate_matches_analytic_visibility_and_finite_mass() {
    let v = integrate_visibility(&[0.0, 0.5, 1.0, 2.0], &[0.7; 3], 0.0).unwrap();
    for (i, &t) in [0.0, 0.5, 1.0, 2.0].iter().enumerate() {
        close(v.optical_depth[i], 0.7 * (2.0 - t), 3e-16);
        close(v.survival[i], (-0.7_f64 * (2.0 - t)).exp(), 3e-16);
    }
    close(
        v.interval_probability.iter().sum::<f64>(),
        -(-1.4_f64).exp_m1(),
        4e-16,
    );
    close(
        v.interval_probability.iter().sum::<f64>() + v.survival[0],
        1.0,
        4e-16,
    );
    for i in 0..3 {
        close(
            v.interval_probability[i],
            v.survival[i + 1] - v.survival[i],
            2e-16,
        );
    }
}

#[test]
fn observer_tail_is_explicit_and_transparent_cells_are_valid() {
    let v = integrate_visibility(&[0.0, 1.0, 3.0, 4.0], &[0.0, 0.5, 0.0], 2.0).unwrap();
    assert_eq!(v.optical_depth, vec![3.0, 3.0, 2.0, 2.0]);
    assert_eq!(v.interval_probability[0], 0.0);
    assert_eq!(v.interval_probability[2], 0.0);
    close(
        v.interval_probability[1],
        (-2.0_f64).exp() * -(-1.0_f64).exp_m1(),
        1e-16,
    );
    close(
        v.interval_probability.iter().sum::<f64>() + v.survival[0],
        (-2.0_f64).exp(),
        1e-16,
    );
}

#[test]
fn thin_cell_probability_does_not_cancel_and_thick_limit_is_finite() {
    let thin = integrate_visibility(&[0.0, 1.0], &[1e-18], 0.0).unwrap();
    assert!(thin.interval_probability[0] > 0.0);
    close(thin.interval_probability[0] / 1e-18, 1.0, 1e-15);
    let thick = integrate_visibility(&[0.0, 1.0, 2.0], &[1000.0, 1000.0], 0.0).unwrap();
    assert_eq!(thick.survival, vec![0.0, 0.0, 1.0]);
    assert_eq!(thick.interval_probability, vec![0.0, 1.0]);
}

#[test]
fn cumulative_opacity_bounds_control_survival_and_interval_mass() {
    let t = [0.0, 0.25, 1.0, 2.0];
    let q = [0.2, 0.0, 2.0];
    let r = [0.1, 0.4, 1.7];
    let a = integrate_visibility(&t, &q, 0.0).unwrap();
    let b = integrate_visibility(&t, &r, 0.0).unwrap();
    let c = compare_opacity(&t, &q, &r).unwrap();
    for (i, e) in [0.625, 0.6, 0.3, 0.0].iter().enumerate() {
        close(c.opacity_l1_tail[i], *e, 2e-16);
        close(c.survival_error_bound[i], -(-e).exp_m1(), 2e-16);
        assert!((a.survival[i] - b.survival[i]).abs() <= c.survival_error_bound[i] + 1e-15);
    }
    for i in 0..3 {
        close(
            c.interval_probability_error_bound[i],
            c.survival_error_bound[i] + c.survival_error_bound[i + 1],
            1e-15,
        );
        assert!(
            (a.interval_probability[i] - b.interval_probability[i]).abs()
                <= c.interval_probability_error_bound[i] + 1e-15
        );
    }
    let zero = compare_opacity(&t, &q, &q).unwrap();
    assert_eq!(zero.opacity_l1_tail, vec![0.0; 4]);
}

#[test]
fn invalid_domains_and_nonfinite_arithmetic_return_errors() {
    for args in [
        [-1.0, 1.0, 0.0, 0.0, 0.0],
        [1.0, f64::NAN, 0.0, 0.0, 0.0],
        [1.0, 1.0, 1.01, 0.0, 0.0],
        [1.0, 1.0, 0.0, -0.1, 0.0],
        [1.0, 1.0, 0.0, 0.8, 0.3],
        [f64::MAX, f64::MAX, 1.0, 0.0, 1.0],
    ] {
        assert!(ElectronState::new(args[0], args[1], args[2], args[3], args[4]).is_err());
    }
    let neutral = ElectronState::new(1.0, 0.0, 0.0, 0.0, 0.0).unwrap();
    assert!(neutral
        .scattering_rate_per_normal_second(MaterialFrame::new([0.0; 3]).unwrap(), [0.0; 3])
        .is_err());
    for (t, q, tail) in [
        (vec![], vec![], 0.0),
        (vec![0.0], vec![], 0.0),
        (vec![0.0, 1.0], vec![], 0.0),
        (vec![1.0, 0.0], vec![1.0], 0.0),
        (vec![0.0, 0.0], vec![1.0], 0.0),
        (vec![0.0, f64::NAN], vec![1.0], 0.0),
        (vec![0.0, 1.0], vec![-1.0], 0.0),
        (vec![0.0, 1.0], vec![f64::INFINITY], 0.0),
        (vec![0.0, 1.0], vec![1.0], -1.0),
        (vec![0.0, 1.0], vec![1.0], f64::NAN),
        (vec![-f64::MAX, f64::MAX], vec![0.0], 0.0),
        (vec![0.0, 2.0], vec![f64::MAX], 0.0),
        (vec![0.0, 1.0, 2.0], vec![f64::MAX; 2], 0.0),
    ] {
        assert!(
            integrate_visibility(&t, &q, tail).is_err(),
            "{t:?} {q:?} {tail}"
        );
    }
    assert!(compare_opacity(&[0.0, 1.0], &[0.0], &[-1.0]).is_err());
    assert!(compare_opacity(&[0.0, 1.0], &[0.0], &[]).is_err());
}
