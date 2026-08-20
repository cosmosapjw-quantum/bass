use bianchi_rustcore::generated::typeii_physical_guard::ScreenInputPolicy;
use bianchi_rustcore::generated::typeii_polarized_liouville::transport_typeii_characteristic;

#[allow(dead_code)]
#[path = "support/typeii_fixture_generated.rs"]
mod fixture;

fn max_abs(a: &[f64], b: &[f64]) -> f64 {
    a.iter()
        .zip(b)
        .map(|(x, y)| (x - y).abs())
        .fold(0.0, f64::max)
}

fn normalize(mut v: [f64; 3]) -> [f64; 3] {
    let n = v.iter().map(|x| x * x).sum::<f64>().sqrt();
    for x in &mut v {
        *x /= n;
    }
    v
}

fn physical_state(e: [f64; 3]) -> [f64; 9] {
    let seed = if e[0].abs() < 0.8 {
        [1.0, 0.0, 0.0]
    } else {
        [0.0, 1.0, 0.0]
    };
    let parallel = seed.iter().zip(e).map(|(a, b)| a * b).sum::<f64>();
    let u = normalize([
        seed[0] - parallel * e[0],
        seed[1] - parallel * e[1],
        seed[2] - parallel * e[2],
    ]);
    let v = [
        e[1] * u[2] - e[2] * u[1],
        e[2] * u[0] - e[0] * u[2],
        e[0] * u[1] - e[1] * u[0],
    ];
    let mut m = [[0.0; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            m[i][j] = 0.8 * u[i] * u[j]
                + 0.35 * v[i] * v[j]
                + 0.07 * (u[i] * v[j] + v[i] * u[j])
                + 0.02 * (u[i] * v[j] - v[i] * u[j]);
        }
    }
    [
        m[0][0],
        m[1][1],
        m[2][2],
        0.5 * (m[0][1] + m[1][0]),
        0.5 * (m[0][2] + m[2][0]),
        0.5 * (m[1][2] + m[2][1]),
        0.5 * (m[1][2] - m[2][1]),
        0.5 * (m[2][0] - m[0][2]),
        0.5 * (m[0][1] - m[1][0]),
    ]
}

fn evolve(substeps_per_interval: usize) -> (Vec<f64>, [f64; 3], f64, f64, f64, f64) {
    let mut direction = normalize([0.31, -0.42, 0.85]);
    let mut state = physical_state(direction).to_vec();
    let mut log_energy = 0.0;
    let mut screen_phase = 0.0;
    let mut maximum_leakage = 0.0_f64;
    let mut minimum_eigenvalue = f64::INFINITY;
    for pair in fixture::TYPEII_SAMPLES.windows(2) {
        let dt = pair[1].tau - pair[0].tau;
        let result = transport_typeii_characteristic(
            direction,
            &pair[0].state,
            &pair[1].state,
            dt,
            substeps_per_interval,
            &state,
            ScreenInputPolicy::Reject { tolerance: 1e-12 },
        )
        .unwrap();
        direction = result.direction;
        state = result.coherency;
        log_energy += result.log_energy_shift;
        screen_phase += result.screen_connection_integral;
        maximum_leakage = maximum_leakage.max(result.max_screen_leakage);
        minimum_eigenvalue = minimum_eigenvalue.min(result.minimum_coherency_eigenvalue);
    }
    (
        state,
        direction,
        log_energy,
        screen_phase,
        maximum_leakage,
        minimum_eigenvalue,
    )
}

fn trajectory_error(
    candidate: &(Vec<f64>, [f64; 3], f64, f64, f64, f64),
    reference: &(Vec<f64>, [f64; 3], f64, f64, f64, f64),
) -> f64 {
    max_abs(&candidate.0, &reference.0)
        .max(max_abs(&candidate.1, &reference.1))
        .max((candidate.2 - reference.2).abs())
        .max((candidate.3 - reference.3).abs())
}

#[test]
fn source_derived_typeii_trajectory_preserves_the_physical_screen_lane() {
    let n1 = evolve(1);
    let n2 = evolve(2);
    let n4 = evolve(4);
    let n8 = evolve(8);
    let reference = evolve(16);
    let e1 = trajectory_error(&n1, &reference);
    let e2 = trajectory_error(&n2, &reference);
    let e4 = trajectory_error(&n4, &reference);
    let e8 = trajectory_error(&n8, &reference);
    println!(
        "TYPEII_LIOUVILLE_SOURCE_RECEIPT errors={e1:.16e},{e2:.16e},{e4:.16e},{e8:.16e} ratios={:.12},{:.12},{:.12} log_energy={:.16e} screen_phase={:.16e} leakage={:.16e} min_eigenvalue={:.16e}",
        e1 / e2,
        e2 / e4,
        e4 / e8,
        n1.2,
        n1.3,
        n1.4,
        n1.5,
    );
    assert!(e1 / e2 > 3.5, "e1={e1} e2={e2}");
    assert!(e2 / e4 > 3.5, "e2={e2} e4={e4}");
    assert!(e4 / e8 > 3.5, "e4={e4} e8={e8}");
    assert!(n1.4 < 5e-14, "leakage={}", n1.4);
    assert!(n1.5 > 0.0, "minimum eigenvalue={}", n1.5);
}
