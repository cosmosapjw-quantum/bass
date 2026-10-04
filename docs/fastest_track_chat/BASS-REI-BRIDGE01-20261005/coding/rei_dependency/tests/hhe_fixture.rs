use rei_microphysics::{adaptive_hhe_step, HHeModel, HHeState, StepControl};
#[test]
fn finite_mixed_fixture_converges_to_independent_reference() {
    let m = HHeModel::controlled_fixture();
    let initial = HHeState::controlled_fixture(&m);
    let energy = m.total_energy(&initial).unwrap();
    let expected = [
        0.2222193243515776,
        0.11628572981765692,
        0.001637763520978686,
        9.14583492004249,
    ];
    let mut previous = f64::INFINITY;
    for dt in [1e9, 5e8, 2.5e8] {
        let mut state = initial;
        let mut t = 0.0;
        let mut count = 0;
        while t < 1e12 {
            let h = f64::min(dt, 1e12 - t);
            let z = adaptive_hhe_step(&m, &state, h, StepControl::default()).unwrap();
            assert!(z.local_error < 2e-4);
            state = z.state;
            t += h;
            count += 1;
            assert!(
                state.fractions[0] >= 0.0
                    && state.fractions[0] <= 1.0
                    && state.fractions[1] >= 0.0
                    && state.fractions[2] >= 0.0
                    && state.fractions[1] + state.fractions[2] <= 1.0
            );
            assert!(state.photon_cm3.iter().all(|v| *v >= 0.0));
        }
        let obs = [
            state.fractions[0],
            state.fractions[1],
            state.fractions[2],
            m.temperature(&state).unwrap().ln(),
        ];
        let error = (0..4)
            .map(|k| (obs[k] - expected[k]).abs())
            .fold(0.0, f64::max);
        assert!(error < 2e-4, "dt={dt},err={error}");
        assert!(
            error < previous,
            "refinement must reduce global reference error"
        );
        previous = error;
        assert!((m.total_energy(&state).unwrap() / energy - 1.0).abs() < 1e-12);
        assert!(count >= 1000);
    }
}
