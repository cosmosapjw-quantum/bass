#[path = "support/typeii_fixture_generated.rs"]
mod fixture;

use bianchi_rustcore::generated::typeii_background;
use fixture::{
    SplitMix64, FORMULA_AUTHORITY_LABEL_SHA256, GENERATED_BACKGROUND_ACTUAL_SHA256,
    RNG_U64_KNOWN_ANSWER, SPLITMIX64_SEED, TYPEII_SAMPLES,
};

fn max_abs(a: &[f64], b: &[f64]) -> f64 {
    a.iter()
        .zip(b)
        .map(|(x, y)| (x - y).abs())
        .fold(0.0, f64::max)
}

fn rk4_step(state: &[f64; 5], dt: f64, gamma: f64) -> [f64; 5] {
    let k1 = typeii_background::rhs(state, gamma);
    let mut work = [0.0; 5];
    for i in 0..5 {
        work[i] = state[i] + 0.5 * dt * k1[i];
    }
    let k2 = typeii_background::rhs(&work, gamma);
    for i in 0..5 {
        work[i] = state[i] + 0.5 * dt * k2[i];
    }
    let k3 = typeii_background::rhs(&work, gamma);
    for i in 0..5 {
        work[i] = state[i] + dt * k3[i];
    }
    let k4 = typeii_background::rhs(&work, gamma);
    let mut next = [0.0; 5];
    for i in 0..5 {
        next[i] = state[i] + dt * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i]) / 6.0;
    }
    next
}

fn receipt_constrained_opacity(index: usize, tau: f64) -> f64 {
    const VALUES: [f64; 3] = [240.13336620482818, 100.08485094440381, 13.322173705416928];
    match index {
        0 => return VALUES[0],
        200 => return VALUES[1],
        400 => return VALUES[2],
        _ => {}
    }
    let x = tau / 0.1;
    let weights = [
        0.5 * (x - 1.0) * (x - 2.0),
        -x * (x - 2.0),
        0.5 * x * (x - 1.0),
    ];
    (weights[0] * VALUES[0].ln() + weights[1] * VALUES[1].ln() + weights[2] * VALUES[2].ln()).exp()
}

#[test]
fn splitmix64_rust_lane_matches_generated_known_answers() {
    let mut rng = SplitMix64::new(SPLITMIX64_SEED);
    for expected in RNG_U64_KNOWN_ANSWER {
        assert_eq!(rng.next_u64(), expected);
    }
}

#[test]
fn source_rhs_rk4_reconstructs_all_401_samples() {
    assert_eq!(TYPEII_SAMPLES.len(), 401);
    let mut state = TYPEII_SAMPLES[0].state;
    for (index, sample) in TYPEII_SAMPLES.iter().enumerate() {
        assert_eq!(sample.tau, index as f64 * 0.0005);
        assert!(
            max_abs(&state, &sample.state) < 3e-15,
            "index={index} state_err={}",
            max_abs(&state, &sample.state)
        );
        let runtime_rhs = typeii_background::rhs(&sample.state, 1.3);
        assert!(
            max_abs(&runtime_rhs, &sample.rhs) < 3e-15,
            "index={index} rhs_err={}",
            max_abs(&runtime_rhs, &sample.rhs)
        );
        if index + 1 < TYPEII_SAMPLES.len() {
            state = rk4_step(&state, 0.0005, 1.3);
        }
    }
}

#[test]
fn opacity_schedule_reconstructs_receipt_constrained_surrogate() {
    for (index, sample) in TYPEII_SAMPLES.iter().enumerate() {
        let expected = receipt_constrained_opacity(index, sample.tau);
        assert!(
            (sample.opacity - expected).abs() <= 2e-13 * expected.max(1.0),
            "index={index} got={} expected={expected}",
            sample.opacity
        );
    }
    assert_eq!(TYPEII_SAMPLES[0].opacity, 240.13336620482818);
    assert_eq!(TYPEII_SAMPLES[200].opacity, 100.08485094440381);
    assert_eq!(TYPEII_SAMPLES[400].opacity, 13.322173705416928);
}

#[test]
fn historical_public_sigma_m_literals_remain_distinct_compatibility_anchors() {
    let midpoint_historical = 0.000012265009715214_f64;
    let endpoint_historical = 0.000024519691346677_f64;
    assert_eq!(
        (midpoint_historical - TYPEII_SAMPLES[1].state[1]).abs(),
        1.3605942747788556e-14
    );
    assert_eq!(
        (endpoint_historical - TYPEII_SAMPLES[2].state[1]).abs(),
        8.957157593219266e-14
    );
    assert_eq!(
        FORMULA_AUTHORITY_LABEL_SHA256,
        "3ecf0dbc8b47a8af83da81e9ed37823b6922e139e420c5bfa2e071b6bbabe361"
    );
    assert_eq!(
        GENERATED_BACKGROUND_ACTUAL_SHA256,
        "0f1f31dad4c106fa22ac1ea8e95651ede24a32d24400629e10f8271d99490d15"
    );
    assert_ne!(
        FORMULA_AUTHORITY_LABEL_SHA256,
        GENERATED_BACKGROUND_ACTUAL_SHA256
    );
}
