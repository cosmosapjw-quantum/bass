use rei_microphysics::{
    ft03_adaptive_step, ft03_coefficients, ft03_implicit_step, ft03_rhs, ft03_try_step, Ft03Model,
    StepControl,
};
fn close(a: f64, b: f64) {
    assert!(
        (a - b).abs() <= 3e-12 * b.abs().max(1e-300),
        "{a:e} vs {b:e}"
    );
}
#[test]
fn published_fit_and_moment_point_reference() {
    let v = ft03_coefficients(30000.0).unwrap();
    let actual = v
        .alpha_rr_cm3_s
        .into_iter()
        .chain(v.log_slope)
        .chain(v.log_slope_derivative)
        .chain(v.rr_kinetic_erg_cm3_s)
        .chain(v.beta_ci_cm3_s)
        .chain(v.alpha_dr_cm3_s)
        .chain(v.dr_energy_erg);
    let expected = [
        1.8989314378527196e-13,
        2.0594903997646117e-13,
        1.0536861560842736e-12,
        -0.7763199242832295,
        -0.654,
        -0.701056518737482,
        -0.06693540654698026,
        0.0,
        -0.04248111838815904,
        5.691941629541094e-25,
        7.216633870077423e-25,
        3.486838792878432e-24,
        5.885814622779521e-11,
        2.86510875469318e-13,
        7.71901755775352e-19,
        5.826225596344116e-17,
        7.617714637062894e-19,
        6.488547095141264e-11,
        7.786256514169465e-11,
    ];
    for (x, y) in actual.zip(expected) {
        close(x, y);
    }
    let v = ft03_coefficients(32000.0).unwrap();
    let actual = v
        .alpha_rr_cm3_s
        .into_iter()
        .chain(v.log_slope)
        .chain(v.log_slope_derivative)
        .chain(v.rr_kinetic_erg_cm3_s)
        .chain(v.beta_ci_cm3_s)
        .chain(v.alpha_dr_cm3_s)
        .chain(v.dr_energy_erg);
    let expected = [
        1.8058809416796577e-13,
        1.974372014836284e-13,
        1.006984602325377e-12,
        -0.7806797073266705,
        -0.654,
        -0.7038305634437977,
        -0.06817145008497011,
        0.0,
        -0.043487020347531644,
        5.739111839267533e-25,
        7.379596405546555e-25,
        3.542106318632422e-24,
        8.446551486447847e-11,
        5.419020004356384e-13,
        2.969083741119464e-18,
        1.4078549597448073e-16,
        2.238917334405752e-18,
        6.488547095141264e-11,
        7.786256514169465e-11,
    ];
    for (x, y) in actual.zip(expected) {
        close(x, y);
    }
    let v = ft03_coefficients(40000.0).unwrap();
    let actual = v
        .alpha_rr_cm3_s
        .into_iter()
        .chain(v.log_slope)
        .chain(v.log_slope_derivative)
        .chain(v.rr_kinetic_erg_cm3_s)
        .chain(v.beta_ci_cm3_s)
        .chain(v.alpha_dr_cm3_s)
        .chain(v.dr_energy_erg);
    let expected = [
        1.5145405274168137e-13,
        1.7062781842557062e-13,
        8.596696700309442e-13,
        -0.7963696803910019,
        -0.654,
        -0.7139322133521508,
        -0.07245613134430252,
        0.0,
        -0.04708236314345136,
        5.885301523771656e-25,
        7.971929973668121e-25,
        3.731941933343564e-24,
        2.530144131624191e-10,
        3.736146475985687e-12,
        1.712634738505078e-16,
        1.9003518007027917e-15,
        5.438039684749646e-17,
        6.488547095141264e-11,
        7.786256514169465e-11,
    ];
    for (x, y) in actual.zip(expected) {
        close(x, y);
    }
    let v = ft03_coefficients(50000.0).unwrap();
    let actual = v
        .alpha_rr_cm3_s
        .into_iter()
        .chain(v.log_slope)
        .chain(v.log_slope_derivative)
        .chain(v.rr_kinetic_erg_cm3_s)
        .chain(v.beta_ci_cm3_s)
        .chain(v.alpha_dr_cm3_s)
        .chain(v.dr_energy_erg);
    let expected = [
        1.2656273893806087e-13,
        1.474587980476599e-13,
        7.321868393221613e-13,
        -0.8130145359087628,
        -0.654,
        -0.724855700279413,
        -0.07672169612225747,
        0.0,
        -0.0508507791694337,
        6.002147996700656e-25,
        8.611808019379264e-25,
        3.917939839559872e-24,
        6.206967333470373e-10,
        1.8004708786742314e-11,
        4.479061309971467e-15,
        1.4255481015487447e-14,
        6.526687510134747e-16,
        6.488547095141264e-11,
        7.786256514169465e-11,
    ];
    for (x, y) in actual.zip(expected) {
        close(x, y);
    }
    let v = ft03_coefficients(75000.0).unwrap();
    let actual = v
        .alpha_rr_cm3_s
        .into_iter()
        .chain(v.log_slope)
        .chain(v.log_slope_derivative)
        .chain(v.rr_kinetic_erg_cm3_s)
        .chain(v.beta_ci_cm3_s)
        .chain(v.alpha_dr_cm3_s)
        .chain(v.dr_energy_erg);
    let expected = [
        9.042976908648944e-14,
        1.1311156367086382e-13,
        5.433517833319147e-13,
        -0.8456626761821834,
        -0.654,
        -0.7469252813568127,
        -0.08425152852616315,
        0.0,
        -0.058085757298764557,
        6.127137991913492e-25,
        9.908819453320487e-25,
        4.237051191056172e-24,
        2.147412846483968e-09,
        1.56500164378334e-10,
        3.6427934861911826e-13,
        1.7804461353694282e-13,
        1.5253747506896874e-14,
        6.488547095141264e-11,
        7.786256514169465e-11,
    ];
    for (x, y) in actual.zip(expected) {
        close(x, y);
    }
    let v = ft03_coefficients(90000.0).unwrap();
    let actual = v
        .alpha_rr_cm3_s
        .into_iter()
        .chain(v.log_slope)
        .chain(v.log_slope_derivative)
        .chain(v.rr_kinetic_erg_cm3_s)
        .chain(v.beta_ci_cm3_s)
        .chain(v.alpha_dr_cm3_s)
        .chain(v.dr_energy_erg);
    let expected = [
        7.739890723263623e-14,
        1.0039740121826772e-13,
        4.737085694979169e-13,
        -0.8613189071661759,
        -0.654,
        -0.7578231798171778,
        -0.08746914384489224,
        0.0,
        -0.061471538487599786,
        6.142493151312766e-25,
        1.0554037341212852e-24,
        4.3686215085683735e-24,
        3.306943706075414e-09,
        3.3079355102730895e-10,
        1.6092997552463917e-12,
        3.8487371700462693e-13,
        4.0632937948532216e-14,
        6.488547095141264e-11,
        7.786256514169465e-11,
    ];
    for (x, y) in actual.zip(expected) {
        close(x, y);
    }
    let v = ft03_coefficients(100000.0).unwrap();
    let actual = v
        .alpha_rr_cm3_s
        .into_iter()
        .chain(v.log_slope)
        .chain(v.log_slope_derivative)
        .chain(v.rr_kinetic_erg_cm3_s)
        .chain(v.beta_ci_cm3_s)
        .chain(v.alpha_dr_cm3_s)
        .chain(v.dr_energy_erg);
    let expected = [
        7.064976805174455e-14,
        9.371240259275016e-14,
        4.372052667393455e-13,
        -0.8706296092367392,
        -0.654,
        -0.7644042544764803,
        -0.08926176378661653,
        0.0,
        -0.06345634189088326,
        6.13903812359729e-25,
        1.094588089484771e-24,
        4.4402546361568754e-24,
        4.124345804303112e-09,
        4.847872068177812e-10,
        3.4015247544930602e-12,
        5.539399153357309e-13,
        6.492003711994412e-14,
        6.488547095141264e-11,
        7.786256514169465e-11,
    ];
    for (x, y) in actual.zip(expected) {
        close(x, y);
    }
    let v = ft03_coefficients(110000.0).unwrap();
    let actual = v
        .alpha_rr_cm3_s
        .into_iter()
        .chain(v.log_slope)
        .chain(v.log_slope_derivative)
        .chain(v.rr_kinetic_erg_cm3_s)
        .chain(v.beta_ci_cm3_s)
        .chain(v.alpha_dr_cm3_s)
        .chain(v.dr_energy_erg);
    let expected = [
        6.499739119772945e-14,
        8.804937069727283e-14,
        4.0636685733049505e-13,
        -0.8792124980655419,
        -0.654,
        -0.7705384265899774,
        -0.09083439134360427,
        0.0,
        -0.06526580246564047,
        6.127944995356942e-25,
        1.13128645476914e-24,
        4.501908534915135e-24,
        4.956330382570125e-09,
        6.660900986319579e-10,
        6.296955059900666e-12,
        7.360739202009664e-13,
        9.396088297584347e-14,
        6.488547095141264e-11,
        7.786256514169465e-11,
    ];
    for (x, y) in actual.zip(expected) {
        close(x, y);
    }
}
#[test]
fn guard_refuses_extrapolation() {
    for t in [0.0, -1.0, 29999.0, 110001.0, f64::NAN, f64::INFINITY] {
        assert!(ft03_coefficients(t).is_err());
    }
    assert!(ft03_coefficients(30000.0).is_ok());
    assert!(ft03_coefficients(110000.0).is_ok());
}
#[test]
fn controlled_initial_and_verner_binding() {
    let m = Ft03Model::controlled().unwrap();
    let s = m.initial_state();
    assert_eq!(s.fractions, [0.9, 0.3, 0.6]);
    close(m.gas.temperature(&s).unwrap(), 50000.0);
    assert_eq!(m.gas.photon_energy_ev, [20.0, 35.0, 70.0]);
    for (x, y) in s.photon_cm3.into_iter().zip([5e-6, 5e-7, 1e-7]) {
        close(x, y);
    }
    close(m.gas.sigma_cm2[0][0], 2.2111029840392129e-18);
    close(m.gas.sigma_cm2[0][1], 4.5101616132931812e-19);
    close(m.gas.sigma_cm2[0][2], 5.7734278524344784e-20);
    close(m.gas.sigma_cm2[1][0], 0.0);
    close(m.gas.sigma_cm2[1][1], 4.0653262472373684e-18);
    close(m.gas.sigma_cm2[1][2], 9.6054574607813123e-19);
    close(m.gas.sigma_cm2[2][0], 0.0);
    close(m.gas.sigma_cm2[2][1], 0.0);
    close(m.gas.sigma_cm2[2][2], 8.00711463442348e-19);
}
#[test]
fn all_event_owners_and_energy_rhs() {
    let m = Ft03Model::controlled().unwrap();
    let s = m.initial_state();
    let f = ft03_rhs(&m, &s).unwrap();
    let g = m.gas;
    let chi = g.threshold_ev;
    let binding = g.ev_erg
        * (g.n_h_cm3 * chi[0] * f.derivative[0]
            + g.n_he_cm3 * (chi[1] * f.derivative[1] + (chi[1] + chi[2]) * f.derivative[2]));
    let photon = g.ev_erg
        * (0..3)
            .map(|k| g.photon_energy_ev[k] * f.derivative[k + 4])
            .sum::<f64>();
    let e = f.derivative[3] + binding + photon + f.escaped_energy_rate;
    assert!(e.abs() / 1e-27 < 1e-12);
    for k in 0..3 {
        close(
            -f.derivative[k + 4],
            (0..3).map(|i| f.photo_per_cm3_s[i][k]).sum(),
        );
    }
    assert!(f.dr_per_cm3_s.iter().all(|v| *v > 0.0));
}
#[test]
fn zero_step_and_transactional_reject() {
    let m = Ft03Model::controlled().unwrap();
    let mut s = m.initial_state();
    let old = s;
    assert_eq!(
        ft03_implicit_step(&m, &s, 0.0, StepControl::default())
            .unwrap()
            .state,
        s
    );
    assert!(ft03_try_step(
        &m,
        &mut s,
        1e11,
        StepControl {
            max_iterations: 0,
            ..StepControl::default()
        }
    )
    .is_err());
    assert_eq!(s, old);
    assert!(ft03_try_step(&m, &mut s, -1.0, StepControl::default()).is_err());
    assert_eq!(s, old);
}
#[test]
fn actual_temperature_feedback_and_implicit_residual() {
    let m = Ft03Model::controlled().unwrap();
    let old = m.initial_state();
    let z = ft03_implicit_step(&m, &old, 1e11, StepControl::default()).unwrap();
    let f = ft03_rhs(&m, &z.state).unwrap();
    let before = old.coordinates();
    let after = z.state.coordinates();
    let scale = [
        1.0,
        1.0,
        1.0,
        old.u_erg_cm3,
        old.photon_cm3[0],
        old.photon_cm3[1],
        old.photon_cm3[2],
    ];
    for k in 0..7 {
        assert!((after[k] - before[k] - 1e11 * f.derivative[k]).abs() / scale[k] < 2e-11);
    }
    assert!(z.residual_norm < 1e-14);
    let t = m.gas.temperature(&z.state).unwrap();
    assert!((t - 50000.0).abs() > 0.01);
    assert!(
        ft03_coefficients(t).unwrap().alpha_rr_cm3_s
            != ft03_coefficients(50000.0).unwrap().alpha_rr_cm3_s
    );
}
#[test]
fn finite_nonlinear_controlled_reference_and_refinement() {
    let m = Ft03Model::controlled().unwrap();
    let initial = m.initial_state();
    let total = m.gas.total_energy(&initial).unwrap();
    let expected = [
        0.9996103763929391,
        0.34353587128805174,
        0.6036005180228474,
        10.751154212350176,
    ];
    let mut previous = f64::INFINITY;
    for dt in [1e11, 5e10, 2.5e10] {
        let mut s = initial;
        let mut t = 0.0;
        while t < 1e14 {
            let h = f64::min(dt, 1e14 - t);
            let z = ft03_adaptive_step(&m, &s, h, StepControl::default()).unwrap();
            assert!(z.local_error < 2e-4);
            s = z.state;
            t += h;
        }
        let obs = [
            s.fractions[0],
            s.fractions[1],
            s.fractions[2],
            m.gas.temperature(&s).unwrap().ln(),
        ];
        let e = (0..4)
            .map(|k| (obs[k] - expected[k]).abs())
            .fold(0.0, f64::max);
        assert!(e < 2e-4, "dt={dt},err={e}");
        assert!(e < previous);
        previous = e;
        assert!((m.gas.total_energy(&s).unwrap() / total - 1.0).abs() < 1e-12);
    }
}
#[test]
fn physical_domain_and_helium_zero_boundary() {
    let m = Ft03Model::controlled().unwrap();
    let mut s = m.initial_state();
    s.u_erg_cm3 *= 0.1;
    assert!(ft03_rhs(&m, &s).is_err());
    s = m.initial_state();
    s.fractions = [0.5, 0.25, 0.75];
    s.u_erg_cm3 = 1.5
        * m.gas.kb_erg_k
        * 50000.0
        * (m.gas.n_h_cm3 + m.gas.n_he_cm3 + m.gas.electron_density(&s).unwrap());
    let f = ft03_rhs(&m, &s).unwrap();
    assert_eq!(f.photo_per_cm3_s[1], [0.0; 3]);
    assert_eq!(f.collision_per_cm3_s[1], 0.0);
    assert!(f.photo_per_cm3_s.iter().flatten().all(|v| *v >= 0.0));
}
