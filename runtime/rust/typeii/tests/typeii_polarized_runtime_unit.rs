use bianchi_rustcore::generated::typeii_polarized::{
    collision_generator_apply_polarized, equilibrium_state_polarized, kato_apply_polarized,
    projector_apply_polarized, projector_dv_apply_polarized,
};
use bianchi_rustcore::generated::typeii_polarized_runtime::{
    frozen_collision_step, frozen_kato_step,
};
use bianchi_rustcore::generated::typeii_runtime::KrylovOptions;

#[path = "support/typeii_v_schedule.rs"]
mod typeii_v_schedule;

fn rest_grid6() -> ([[f64; 3]; 6], [f64; 6]) {
    let w = 4.0 * std::f64::consts::PI / 6.0;
    (
        [
            [1., 0., 0.],
            [-1., 0., 0.],
            [0., 1., 0.],
            [0., -1., 0.],
            [0., 0., 1.],
            [0., 0., -1.],
        ],
        [w; 6],
    )
}

fn aberrate(e: [f64; 3], v: f64) -> ([f64; 3], f64) {
    if v.abs() < 1e-15 {
        return (e, 1.0);
    }
    let g = 1.0 / (1.0 - v * v).sqrt();
    let d = g * (1.0 - v * e[1]);
    let mut x = e;
    x[1] += (g - 1.0) * e[1] - g * v;
    for z in &mut x {
        *z /= d;
    }
    let n = x.iter().map(|z| z * z).sum::<f64>().sqrt();
    for z in &mut x {
        *z /= n;
    }
    (x, d)
}

fn paired_grid(v: f64) -> (Vec<[f64; 3]>, Vec<f64>) {
    let (er, wr) = rest_grid6();
    let mut en = Vec::new();
    let mut wn = Vec::new();
    for i in 0..6 {
        let (x, _) = aberrate(er[i], -v);
        let (_, d) = aberrate(x, v);
        en.push(x);
        wn.push(wr[i] * d * d);
    }
    (en, wn)
}

fn max_abs(x: &[f64]) -> f64 {
    x.iter().map(|z| z.abs()).fold(0.0, f64::max)
}

#[test]
fn paired_boosted_equilibrium_is_collision_null() {
    let v = 0.1;
    let (e, w) = paired_grid(v);
    let y = equilibrium_state_polarized(&e, v, 1);
    let c = collision_generator_apply_polarized(&e, &w, v, 1, &y);
    assert!(max_abs(&c) < 2e-13, "right-null defect={:e}", max_abs(&c));
}

#[test]
fn fixed_normal_low_order_grid_is_negative_control() {
    let (e, w) = rest_grid6();
    let v = 0.1;
    let y = equilibrium_state_polarized(&e, v, 1);
    let c = collision_generator_apply_polarized(&e, &w, v, 1, &y);
    let defect = max_abs(&c);
    assert!(
        (defect - 0.009605220075000013).abs() < 3e-14,
        "defect={defect:e}"
    );
}

#[test]
fn finite_v_action_matches_independent_python_dense_gold() {
    let v = 0.1;
    let (e, w) = paired_grid(v);
    let y: Vec<f64> = (0..9 * e.len()).map(|i| i as f64 / 17.0 - 1.0).collect();
    let got = collision_generator_apply_polarized(&e, &w, v, 1, &y);
    let expected = [
        0.012007840371060263,
        1.188776196734966,
        0.8639050859883518,
        -0.11947650315986655,
        -0.041542999368048936,
        0.4133476247093694,
        0.4917164183011797,
        0.04941935947765025,
        0.0,
        0.008968512570116207,
        0.8878827444415045,
        0.3397874389295284,
        0.0892355733679843,
        -0.0007060480708921454,
        -0.0070250896053104875,
        -0.09089777693465026,
        0.009135570314232011,
        0.0,
    ];
    let err = got[..18]
        .iter()
        .zip(expected)
        .map(|(a, b)| (a - b).abs())
        .fold(0.0, f64::max);
    assert!(err < 4e-13, "gold error={err:e}");
}

#[test]
fn left_invariant_is_preserved_on_paired_grid() {
    let v = 0.1;
    let (e, w) = paired_grid(v);
    let y: Vec<f64> = (0..9 * e.len())
        .map(|i| ((i * 17 + 3) % 29) as f64 / 13.0 - 1.0)
        .collect();
    let c = collision_generator_apply_polarized(&e, &w, v, 1, &y);
    let mut s = 0.0;
    for i in 0..e.len() {
        let tr = c[9 * i] + c[9 * i + 1] + c[9 * i + 2];
        s += w[i] * (1.0 - v * e[i][1]) * tr / (4.0 * std::f64::consts::PI);
    }
    assert!(s.abs() < 3e-14, "left invariant={s:e}");
}

#[test]
fn projector_is_idempotent_and_kato_commutator_holds() {
    let v = 0.05;
    let vd = 0.03;
    let (e, w) = paired_grid(v);
    let y: Vec<f64> = (0..9 * e.len())
        .map(|i| ((i * 11 + 5) % 31) as f64 / 17.0 - 0.7)
        .collect();
    let py = projector_apply_polarized(&e, &w, v, 1, &y);
    let pp = projector_apply_polarized(&e, &w, v, 1, &py);
    let pdef = pp
        .iter()
        .zip(&py)
        .map(|(a, b)| (a - b).abs())
        .fold(0.0, f64::max);
    assert!(pdef < 3e-14, "P2 defect={pdef:e}");
    let kpy = kato_apply_polarized(&e, &w, v, vd, 1, &py);
    let ky = kato_apply_polarized(&e, &w, v, vd, 1, &y);
    let pky = projector_apply_polarized(&e, &w, v, 1, &ky);
    let pd = projector_dv_apply_polarized(&e, &w, v, 1, &y);
    let err = kpy
        .iter()
        .zip(pky)
        .zip(pd)
        .map(|((a, b), d)| (a - b - vd * d).abs())
        .fold(0.0, f64::max);
    assert!(err < 5e-13, "commutator defect={err:e}");
}

#[test]
fn frozen_collision_exponential_matches_python_dense_gold() {
    let v = 0.1;
    let (e, w) = paired_grid(v);
    let y: Vec<_> = (0..54).map(|i| i as f64 / 17.0 - 1.0).collect();
    let z = frozen_collision_step(&e, &w, v, 1, 0.2, &y, KrylovOptions::full(54)).unwrap();
    let gold = [
        -0.9978212422935848,
        -0.7254794576531316,
        -0.7260658319458733,
        -0.8452077772285294,
        -0.7724268740094725,
        -0.6290594559386385,
        -0.556041029149626,
        -0.5790876615963299,
        -0.5294117647058824,
        -0.46896094718290027,
        -0.2506631828718346,
        -0.2917523802846686,
        -0.2779263347866812,
        -0.23523898719885444,
        -0.17592204720163962,
        -0.13234145985202306,
        -0.05734668654114272,
        -4.957059219137091e-20,
    ];
    let err = z[..18]
        .iter()
        .zip(gold)
        .map(|(a, b)| (a - b).abs())
        .fold(0.0, f64::max);
    assert!(err < 2e-12, "err={err:e}");
}

#[test]
fn frozen_kato_exponential_matches_python_dense_gold() {
    let v = 0.05;
    let (e, w) = paired_grid(v);
    let y = equilibrium_state_polarized(&e, v, 1);
    let z = frozen_kato_step(&e, &w, v, 0.03, 1, 0.1, &y, KrylovOptions::full(54)).unwrap();
    let gold = [
        0.001256029200115464,
        0.5011556508461252,
        0.5024116800462411,
        -0.025089163622282692,
        0.,
        0.,
        0.,
        0.,
        0.,
        0.001256029200115464,
        0.5011556508461253,
        0.5024116800462409,
        0.025089163622282692,
        0.,
        0.,
        0.,
        0.,
        0.,
    ];
    let err = z[..18]
        .iter()
        .zip(gold)
        .map(|(a, b)| (a - b).abs())
        .fold(0.0, f64::max);
    assert!(err < 2e-12, "err={err:e}");
}

#[path = "support/typeii_polarized_tail.rs"]
mod tail;
