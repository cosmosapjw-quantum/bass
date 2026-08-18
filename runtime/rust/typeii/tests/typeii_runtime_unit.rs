use bianchi_rustcore::generated::typeii_runtime::{expm_action, phi1_action, KrylovOptions};

#[test]
fn expm_action_matches_diagonal_exact() {
    let a = |x: &[f64]| vec![-2.0 * x[0], -0.5 * x[1], 0.0 * x[2]];
    let y = vec![1.2, -0.7, 0.3];
    let got = expm_action(&a, &y, 0.4, KrylovOptions::full(3)).unwrap();
    let want = vec![1.2 * (-0.8f64).exp(), -0.7 * (-0.2f64).exp(), 0.3];
    let err = got.iter().zip(want).map(|(x, z)| (x-z).abs()).fold(0.0, f64::max);
    assert!(err < 1e-13, "err={err} got={got:?}");
}

#[test]
fn phi1_action_matches_diagonal_exact() {
    let a = |x: &[f64]| vec![-2.0 * x[0], -0.5 * x[1], 0.0 * x[2]];
    let b = vec![1.2, -0.7, 0.3];
    let h = 0.4;
    let got = phi1_action(&a, &b, h, KrylovOptions::full(4)).unwrap();
    let p = |z: f64| if z.abs() < 1e-14 { 1.0 } else { z.exp_m1()/z };
    let want = vec![p(-0.8)*1.2, p(-0.2)*(-0.7), 0.3];
    let err = got.iter().zip(want).map(|(x, z)| (x-z).abs()).fold(0.0, f64::max);
    assert!(err < 1e-13, "err={err} got={got:?}");
}

#[test]
fn truncated_krylov_basis_fails_closed_until_adaptive_backend_exists() {
    let a = |x: &[f64]| vec![-0.2*x[0], -0.7*x[1], -1.3*x[2], -2.1*x[3]];
    let y = vec![1.0, -0.4, 0.8, 0.3];
    let opts = KrylovOptions { m_max: 2, tol: 1e-12, max_splits: 18 };
    let err = expm_action(&a, &y, 0.6, opts).unwrap_err();
    match err {
        bianchi_rustcore::generated::typeii_runtime::RuntimeError::SubspaceTooSmall { requested, dimension } => {
            assert_eq!(requested, 2);
            assert_eq!(dimension, 4);
        }
        other => panic!("unexpected error: {other:?}"),
    }
}
