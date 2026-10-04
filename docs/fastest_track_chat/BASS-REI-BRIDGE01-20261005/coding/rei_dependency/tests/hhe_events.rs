use rei_microphysics::{hhe_rhs, implicit_hhe_step, try_hhe_step, HHeModel, HHeState, StepControl};
fn close(a: f64, b: f64, scale: f64) {
    assert!((a - b).abs() / scale < 1e-12, "{a:e} != {b:e}");
}
#[test]
fn equation_of_state_charge_and_rhs_energy() {
    let m = HHeModel::controlled_fixture();
    let s = HHeState::controlled_fixture(&m);
    close(
        m.electron_density(&s).unwrap(),
        1e-4 * 0.01 + 8.3e-6 * (0.019 + 2.0 * 0.001),
        1e-4,
    );
    close(m.temperature(&s).unwrap(), 1e4, 1e4);
    let f = hhe_rhs(&m, &s).unwrap();
    let chi = m.threshold_ev;
    let ev = m.ev_erg;
    let binding = ev
        * (m.n_h_cm3 * chi[0] * f.derivative[0]
            + m.n_he_cm3 * (chi[1] * f.derivative[1] + (chi[1] + chi[2]) * f.derivative[2]));
    let photons = ev
        * (0..3)
            .map(|g| m.photon_energy_ev[g] * f.derivative[g + 4])
            .sum::<f64>();
    close(
        f.derivative[3] + binding + photons + f.escaped_energy_rate,
        0.0,
        1e-27,
    );
    for g in 0..3 {
        close(
            -f.derivative[g + 4],
            (0..3).map(|a| f.photo_per_cm3_s[a][g]).sum(),
            1e-17,
        );
    }
}
#[test]
fn zero_duration_identity() {
    let m = HHeModel::controlled_fixture();
    let s = HHeState::controlled_fixture(&m);
    let z = implicit_hhe_step(&m, &s, 0.0, StepControl::default()).unwrap();
    assert_eq!(s, z.state);
    assert_eq!(z.events.photo_per_cm3, [[0.0; 3]; 3]);
    assert_eq!(z.events.collision_per_cm3, [0.0; 3]);
    assert_eq!(z.events.recombination_per_cm3, [0.0; 3]);
}
#[test]
fn implicit_residual_and_integrated_event_ledger() {
    let m = HHeModel::controlled_fixture();
    let old = HHeState::controlled_fixture(&m);
    let z = implicit_hhe_step(&m, &old, 1e9, StepControl::default()).unwrap();
    let f = hhe_rhs(&m, &z.state).unwrap();
    let y = old.coordinates();
    let new = z.state.coordinates();
    let scales = [1.0, 1.0, 1.0, old.u_erg_cm3, 2e-5, 2e-6, 2e-7];
    for k in 0..7 {
        assert!((new[k] - y[k] - 1e9 * f.derivative[k]).abs() / scales[k] < 2e-11);
    }
    let j: [f64; 3] = std::array::from_fn(|a| {
        z.events.photo_per_cm3[a].iter().sum::<f64>() + z.events.collision_per_cm3[a]
            - z.events.recombination_per_cm3[a]
    });
    close(m.n_h_cm3 * (new[0] - y[0]), j[0], m.n_h_cm3);
    close(m.n_he_cm3 * (new[1] - y[1]), j[1] - j[2], m.n_he_cm3);
    close(m.n_he_cm3 * (new[2] - y[2]), j[2], m.n_he_cm3);
    for g in 0..3 {
        close(
            old.photon_cm3[g] - z.state.photon_cm3[g],
            (0..3).map(|a| z.events.photo_per_cm3[a][g]).sum(),
            old.photon_cm3[g],
        );
    }
    close(
        m.total_energy(&old).unwrap(),
        m.total_energy(&z.state).unwrap(),
        m.total_energy(&old).unwrap(),
    );
}
#[test]
fn rejected_candidate_writes_nothing() {
    let m = HHeModel::controlled_fixture();
    let mut s = HHeState::controlled_fixture(&m);
    let old = s;
    let bad = StepControl {
        max_iterations: 0,
        ..StepControl::default()
    };
    assert!(try_hhe_step(&m, &mut s, 1e9, bad).is_err());
    assert_eq!(s, old);
    assert!(try_hhe_step(&m, &mut s, -1.0, StepControl::default()).is_err());
    assert_eq!(s, old);
}
#[test]
fn malformed_domains_reject() {
    let m = HHeModel::controlled_fixture();
    let mut s = HHeState::controlled_fixture(&m);
    s.fractions = [0.5, 0.9, 0.2];
    assert!(hhe_rhs(&m, &s).is_err());
    s = HHeState::controlled_fixture(&m);
    s.photon_cm3[0] = -1.0;
    assert!(hhe_rhs(&m, &s).is_err());
    s = HHeState::controlled_fixture(&m);
    s.u_erg_cm3 = f64::NAN;
    assert!(hhe_rhs(&m, &s).is_err());
    let mut bad = m;
    bad.sigma_cm2[1][0] = 1e-18;
    assert!(hhe_rhs(&bad, &HHeState::controlled_fixture(&bad)).is_err());
}
#[test]
fn pure_event_limits_have_expected_owners() {
    for mode in 0..3 {
        let mut m = HHeModel::controlled_fixture();
        if mode != 0 {
            m.sigma_cm2 = [[0.0; 3]; 3];
        }
        if mode != 1 {
            m.beta_cm3_s = [0.0; 3];
        }
        if mode != 2 {
            m.alpha_cm3_s = [0.0; 3];
        }
        let old = HHeState::controlled_fixture(&m);
        let z = implicit_hhe_step(&m, &old, 1e9, StepControl::default()).unwrap();
        if mode != 0 {
            assert_eq!(old.photon_cm3, z.state.photon_cm3);
            assert_eq!(z.events.photo_per_cm3, [[0.0; 3]; 3]);
        }
        if mode != 1 {
            assert_eq!(z.events.collision_per_cm3, [0.0; 3]);
        }
        if mode != 2 {
            assert_eq!(z.events.recombination_per_cm3, [0.0; 3]);
            assert_eq!(z.state.escaped_erg_cm3, 0.0);
        }
        close(
            m.total_energy(&old).unwrap(),
            m.total_energy(&z.state).unwrap(),
            m.total_energy(&old).unwrap(),
        );
    }
}
#[test]
fn pure_h_and_pure_he_density_limits() {
    for a in 0..2 {
        let mut m = HHeModel::controlled_fixture();
        if a == 0 {
            m.n_he_cm3 = 0.0;
        } else {
            m.n_h_cm3 = 0.0;
        }
        let old = HHeState::controlled_fixture(&m);
        let z = implicit_hhe_step(&m, &old, 1e9, StepControl::default()).unwrap();
        close(
            m.total_energy(&old).unwrap(),
            m.total_energy(&z.state).unwrap(),
            m.total_energy(&old).unwrap(),
        );
    }
}
