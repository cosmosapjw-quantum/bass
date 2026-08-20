use bianchi_rustcore::generated::typeii_krylov_adapt::{
    adaptive_expm_action, adaptive_phi1_action, kato_aem2_step_adaptive, AdaptiveKrylovError,
    AdaptiveKrylovOptions,
};
use bianchi_rustcore::generated::typeii_runtime::{
    expm_action, kato_aem2_step, phi1_action, KrylovOptions,
};

fn max_abs(a: &[f64], b: &[f64]) -> f64 {
    a.iter()
        .zip(b)
        .map(|(x, y)| (x - y).abs())
        .fold(0.0, f64::max)
}
fn opts(mmax: usize) -> AdaptiveKrylovOptions {
    AdaptiveKrylovOptions {
        m_init: 8.min(mmax),
        m_min: 6.min(mmax),
        m_max: mmax,
        tol: 1e-10,
        max_substeps: 128,
        max_rejects: 64,
    }
}

#[test]
fn truncated_exp_and_phi1_match_full_reference() {
    let n = 48usize;
    let d: Vec<f64> = (0..n).map(|i| -0.25 - 0.15 * i as f64).collect();
    let op = |x: &[f64]| x.iter().zip(&d).map(|(x, d)| x * d).collect::<Vec<_>>();
    let y: Vec<f64> = (0..n)
        .map(|i| ((17 * i + 3) % 31) as f64 / 19.0 - 0.7)
        .collect();
    let t = 1.75;
    let er = expm_action(&op, &y, t, KrylovOptions::full(n)).unwrap();
    let (ea, se) = adaptive_expm_action(&op, &y, t, opts(12)).unwrap();
    assert!(
        max_abs(&ea, &er) < 3e-10,
        "exp err={} stats={se:?}",
        max_abs(&ea, &er)
    );
    assert!(se.max_basis <= 12 && se.matvecs < 80);
    let pr = phi1_action(&op, &y, t, KrylovOptions::full(n + 1)).unwrap();
    let (pa, sp) = adaptive_phi1_action(&op, &y, t, opts(12)).unwrap();
    assert!(
        max_abs(&pa, &pr) < 4e-10,
        "phi1 err={} stats={sp:?}",
        max_abs(&pa, &pr)
    );
    assert!(sp.max_basis <= 12);
}

#[test]
fn nonnormal_and_large_n_lanes_remain_genuinely_truncated() {
    let n = 64usize;
    let jordan = |x: &[f64]| {
        let mut y = vec![0.0; n];
        for i in 0..n {
            y[i] = -1.5 * x[i];
            if i + 1 < n {
                y[i] += 7.0 * x[i + 1];
            }
        }
        y
    };
    let y: Vec<f64> = (0..n)
        .map(|i| ((19 * i + 5) % 41) as f64 / 31.0 - 0.55)
        .collect();
    let r = expm_action(&jordan, &y, 0.8, KrylovOptions::full(n)).unwrap();
    let (a, s) = adaptive_expm_action(
        &jordan,
        &y,
        0.8,
        AdaptiveKrylovOptions {
            m_init: 10,
            m_min: 8,
            m_max: 16,
            tol: 2e-9,
            max_substeps: 256,
            max_rejects: 96,
        },
    )
    .unwrap();
    assert!(max_abs(&a, &r) < 2e-8 && s.max_basis <= 16);

    let n = 512usize;
    let d: Vec<f64> = (0..n)
        .map(|i| -0.25 - 7.0 * i as f64 / (n - 1) as f64)
        .collect();
    let op = |x: &[f64]| x.iter().zip(&d).map(|(x, d)| x * d).collect::<Vec<_>>();
    let y: Vec<f64> = (0..n)
        .map(|i| ((29 * i + 11) % 67) as f64 / 43.0 - 0.65)
        .collect();
    let exact: Vec<f64> = y
        .iter()
        .zip(&d)
        .map(|(y, d)| y * (1.75 * d).exp())
        .collect();
    let (a, s) = adaptive_expm_action(&op, &y, 1.75, opts(12)).unwrap();
    assert!(
        max_abs(&a, &exact) < 3e-10,
        "large err={} stats={s:?}",
        max_abs(&a, &exact)
    );
    assert!(s.max_basis <= 12 && s.matvecs < n);
}

#[test]
fn rejection_budget_fails_closed() {
    let n = 48usize;
    let op = |x: &[f64]| {
        x.iter()
            .enumerate()
            .map(|(i, x)| -(20.0 + i as f64) * x)
            .collect::<Vec<_>>()
    };
    let e = adaptive_expm_action(
        &op,
        &vec![1.0; n],
        10.0,
        AdaptiveKrylovOptions {
            m_init: 4,
            m_min: 4,
            m_max: 4,
            tol: 1e-14,
            max_substeps: 2,
            max_rejects: 1,
        },
    )
    .unwrap_err();
    assert!(matches!(e, AdaptiveKrylovError::DidNotConverge { .. }));
}

fn lebedev26() -> (Vec<[f64; 3]>, Vec<f64>) {
    let pi = std::f64::consts::PI;
    let a = 1.0 / 3.0_f64.sqrt();
    let b = 1.0 / 2.0_f64.sqrt();
    let mut e = Vec::new();
    let mut w = Vec::new();
    for k in 0..3 {
        for s in [-1.0, 1.0] {
            let mut x = [0.0; 3];
            x[k] = s;
            e.push(x);
            w.push(4.0 * pi / 21.0);
        }
    }
    for z in 0..3 {
        let id: Vec<_> = (0..3).filter(|&i| i != z).collect();
        for s1 in [-1.0, 1.0] {
            for s2 in [-1.0, 1.0] {
                let mut x = [0.0; 3];
                x[id[0]] = s1 * b;
                x[id[1]] = s2 * b;
                e.push(x);
                w.push(16.0 * pi / 105.0);
            }
        }
    }
    for x in [-1.0, 1.0] {
        for y in [-1.0, 1.0] {
            for z in [-1.0, 1.0] {
                e.push([x * a, y * a, z * a]);
                w.push(9.0 * pi / 70.0);
            }
        }
    }
    (e, w)
}

#[test]
fn deep_stiff_small_collision_uses_stable_full_capacity_projection() {
    let (e, w) = lebedev26();
    let v = 0.0498;
    let scale = 1.0e5 * 230.0;
    let op = |x: &[f64]| {
        bianchi_rustcore::generated::typeii_collision::collision_generator_apply(&e, &w, v, 1, x)
            .into_iter()
            .map(|z| scale * z)
            .collect::<Vec<_>>()
    };
    let y: Vec<f64> = e
        .iter()
        .map(|d| 1.0 + 0.15 * d[0] - 0.12 * d[1] + 0.08 * (d[2] * d[2] - 1.0 / 3.0))
        .collect();
    let r = expm_action(&op, &y, 0.0125, KrylovOptions::full(y.len())).unwrap();
    let o = AdaptiveKrylovOptions {
        m_init: 12,
        m_min: 8,
        m_max: 32,
        tol: 2e-10,
        max_substeps: 32,
        max_rejects: 64,
    };
    let (a, s) = adaptive_expm_action(&op, &y, 0.0125, o).unwrap();
    assert!(
        max_abs(&a, &r) < 2e-9 && s.accepted_steps <= 4,
        "err={} stats={s:?}",
        max_abs(&a, &r)
    );
}

#[test]
fn source_state_kato_aem2_matches_full_backend_with_only_action_swap() {
    let (e, w) = lebedev26();
    let h = 0.001;
    let gamma = 1.3;
    let s0 = [0.2375, 0.0, -0.11295198246134101, 0.865, 0.05];
    let sm = [
        0.237483198522475,
        0.000012265009715214,
        -0.11293368496280672,
        0.8650058629844937,
        0.049991577928173256,
    ];
    let s1 = [
        0.23746641180283926,
        0.000024519691346677,
        -0.11291538561917082,
        0.8650117491959564,
        0.04998315715921075,
    ];
    let opacity = 239.77404039036273;
    let y: Vec<f64> = (0..e.len())
        .map(|i| ((19 * i + 7) % 37) as f64 / 23.0 + 0.2)
        .collect();
    let r = kato_aem2_step(
        &e,
        &w,
        1,
        gamma,
        h,
        1.0,
        &s0,
        &sm,
        &s1,
        opacity,
        &y,
        KrylovOptions::full(y.len() + 1),
    )
    .unwrap();
    let (a, s) = kato_aem2_step_adaptive(
        &e,
        &w,
        1,
        gamma,
        h,
        1.0,
        &s0,
        &sm,
        &s1,
        opacity,
        &y,
        AdaptiveKrylovOptions {
            m_init: 12,
            m_min: 8,
            m_max: 32,
            tol: 2e-10,
            max_substeps: 512,
            max_rejects: 256,
        },
    )
    .unwrap();
    assert!(
        max_abs(&a, &r) < 2e-9,
        "err={} stats={s:?}",
        max_abs(&a, &r)
    );
}
