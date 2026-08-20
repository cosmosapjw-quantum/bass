use bianchi_rustcore::generated::typeii_krylov_adapt::{
    adaptive_expm_action, adaptive_expm_action_with_residual_budget_divisor, adaptive_phi1_action,
    adaptive_t_phi1_action, kato_aem2_step_adaptive, AdaptiveKrylovError, AdaptiveKrylovOptions,
    AdaptiveKrylovStats, AdaptiveKrylovTargetSemantics,
};

fn norm2(values: &[f64]) -> f64 {
    values.iter().map(|value| value * value).sum::<f64>().sqrt()
}

#[test]
fn standalone_phi1_honors_requested_normwise_target_for_small_times() {
    let n = 48usize;
    let b_diag: Vec<f64> = (0..n)
        .map(|i| -0.1 * (50.0_f64 / 0.1).powf(i as f64 / (n - 1) as f64))
        .collect();
    let b: Vec<f64> = (0..n)
        .map(|i| ((37 * i + 11) % 53) as f64 / 53.0 + 0.125)
        .collect();
    let options = AdaptiveKrylovOptions {
        m_init: 8,
        m_min: 6,
        m_max: 16,
        tol: 1e-12,
        max_substeps: 128,
        max_rejects: 64,
    };
    let requested_target = options.tol * norm2(&b).max(1.0);

    for t in [1e-6, 1e-8, 1e-10, 1e-12, -1e-8] {
        let apply = |x: &[f64]| {
            x.iter()
                .zip(&b_diag)
                .map(|(x, bi)| bi / t * x)
                .collect::<Vec<_>>()
        };
        let expected: Vec<f64> = b_diag
            .iter()
            .zip(&b)
            .map(|(bi, b)| ((bi.exp() - 1.0) / bi) * b)
            .collect();
        let (actual, stats) = adaptive_phi1_action(&apply, &b, t, options)
            .expect("original adaptive phi1 API returned success");
        let error = actual
            .iter()
            .zip(&expected)
            .map(|(actual, expected)| actual - expected)
            .collect::<Vec<_>>();
        let error_norm = norm2(&error);
        println!(
            "t={t:e} error_norm={error_norm:e} requested_target={requested_target:e} old_max_error_ratio={:e}",
            stats.max_error_ratio
        );
        assert!(
            error_norm <= requested_target,
            "standalone phi1 returned success outside its requested normwise target: \
             t={t:e} error_norm={error_norm:e} requested_target={requested_target:e} \
             old_max_error_ratio={:e} stats={stats:?}",
            stats.max_error_ratio,
        );
    }
}

#[test]
fn finite_large_nilpotent_norm_does_not_return_unchanged_success() {
    let n = 40usize;
    let mut state = vec![0.0; n];
    state[0] = 1.0;
    let op = |x: &[f64]| {
        let mut out = vec![0.0; n];
        out[1] = 1e200 * x[0];
        out
    };
    let options = AdaptiveKrylovOptions {
        m_init: 6,
        m_min: 4,
        m_max: 8,
        tol: 1e-10,
        max_substeps: 32,
        max_rejects: 32,
    };

    match adaptive_expm_action(&op, &state, 1.0, options) {
        Ok((actual, stats)) => {
            assert_eq!(actual[0], 1.0, "unexpected first component: {stats:?}");
            assert_eq!(
                actual[1], 1e200,
                "overflowing the norm must not trigger false happy breakdown: {stats:?}"
            );
        }
        Err(AdaptiveKrylovError::DidNotConverge { stats, .. }) => {
            assert!(stats.nonfinite_rejections > 0, "{stats:?}");
            assert!(stats.projected_exponentials > 0, "{stats:?}");
        }
        Err(AdaptiveKrylovError::ProjectionArithmeticNonFinite { stats }) => {
            assert!(stats.matvecs > 0, "{stats:?}");
        }
        Err(error) => {
            panic!("finite nilpotent action failed without a diagnostic ledger: {error:?}")
        }
    }
}

#[test]
fn nonfinite_time_fails_before_the_identity_return() {
    let identity = |x: &[f64]| x.to_vec();
    let error = adaptive_expm_action(
        &identity,
        &[1.0, 2.0, 3.0],
        f64::NAN,
        AdaptiveKrylovOptions {
            m_init: 2,
            m_min: 2,
            m_max: 3,
            tol: 1e-10,
            max_substeps: 8,
            max_rejects: 8,
        },
    );
    assert!(
        error.is_err(),
        "NaN time returned unchanged success: {error:?}"
    );
}

#[test]
fn phi_zero_time_still_validates_options() {
    let identity = |x: &[f64]| x.to_vec();
    let result = adaptive_phi1_action(
        &identity,
        &[1.0, 2.0, 3.0],
        0.0,
        AdaptiveKrylovOptions {
            m_init: 2,
            m_min: 2,
            m_max: 3,
            tol: f64::NAN,
            max_substeps: 8,
            max_rejects: 8,
        },
    );
    assert!(
        result.is_err(),
        "zero-time phi1 bypassed invalid options: {result:?}"
    );
}

#[test]
fn t_phi1_zero_time_rejects_nonfinite_input() {
    let identity = |x: &[f64]| x.to_vec();
    let result = adaptive_t_phi1_action(
        &identity,
        &[f64::INFINITY],
        0.0,
        AdaptiveKrylovOptions {
            m_init: 2,
            m_min: 2,
            m_max: 2,
            tol: 1e-10,
            max_substeps: 8,
            max_rejects: 8,
        },
    );
    assert!(
        matches!(result, Err(AdaptiveKrylovError::InputNotFinite)),
        "zero-time scaled phi1 certified nonfinite input: {result:?}"
    );
}

#[test]
fn all_action_apis_validate_input_and_augmented_operator_boundaries() {
    let identity = |x: &[f64]| x.to_vec();
    let options = AdaptiveKrylovOptions {
        m_init: 2,
        m_min: 2,
        m_max: 3,
        tol: 1e-10,
        max_substeps: 8,
        max_rejects: 8,
    };
    assert!(matches!(
        adaptive_expm_action(&identity, &[f64::INFINITY], 0.0, options),
        Err(AdaptiveKrylovError::InputNotFinite)
    ));
    assert!(matches!(
        adaptive_phi1_action(&identity, &[f64::INFINITY], 0.0, options),
        Err(AdaptiveKrylovError::InputNotFinite)
    ));

    let wrong_dimension = |_x: &[f64]| Vec::new();
    assert!(matches!(
        adaptive_phi1_action(&wrong_dimension, &[1.0, 2.0], 1.0, options),
        Err(AdaptiveKrylovError::OperatorDimensionMismatch { .. })
    ));
    let nan_operator = |_x: &[f64]| vec![f64::NAN, 0.0];
    assert!(matches!(
        adaptive_t_phi1_action(&nan_operator, &[1.0, 2.0], 1.0, options),
        Err(AdaptiveKrylovError::OperatorReturnedNonFinite { .. })
    ));
}

#[test]
fn late_operator_dimension_failure_preserves_attained_work_ledger() {
    use std::cell::Cell;

    let calls = Cell::new(0usize);
    let operator = |x: &[f64]| {
        let call = calls.get();
        calls.set(call + 1);
        if call == 0 {
            let mut out = vec![0.0; x.len()];
            out[1] = x[0];
            out
        } else {
            vec![0.0; x.len() - 1]
        }
    };
    let error = adaptive_expm_action(
        &operator,
        &[1.0, 0.0, 0.0, 0.0],
        1.0,
        AdaptiveKrylovOptions {
            m_init: 3,
            m_min: 2,
            m_max: 3,
            tol: 1e-10,
            max_substeps: 8,
            max_rejects: 8,
        },
    )
    .unwrap_err();
    let stats = match error {
        AdaptiveKrylovError::OperatorDimensionMismatch { stats } => stats,
        other => panic!("unexpected error: {other:?}"),
    };
    assert_eq!(calls.get(), 2);
    assert_eq!(stats.matvecs, 2);
    assert_eq!(stats.projection_builds, 1);
    assert_eq!(stats.max_basis, 1);
    assert_eq!(stats.final_basis, 0);
    assert_eq!(stats.iop2_columns, 1);
}

#[test]
fn direct_t_phi1_controls_the_scaled_return_value() {
    let n = 40usize;
    let t = 1e-8;
    let scaled_diagonal: Vec<f64> = (0..n)
        .map(|i| -0.1 * (50.0_f64 / 0.1).powf(i as f64 / (n - 1) as f64))
        .collect();
    let diagonal: Vec<f64> = scaled_diagonal.iter().map(|value| value / t).collect();
    let b: Vec<f64> = (0..n)
        .map(|i| ((29 * i + 13) % 61) as f64 / 47.0 + 0.2)
        .collect();
    let op = |x: &[f64]| {
        x.iter()
            .zip(&diagonal)
            .map(|(x, d)| x * d)
            .collect::<Vec<_>>()
    };
    let options = AdaptiveKrylovOptions {
        m_init: 8,
        m_min: 6,
        m_max: 16,
        tol: 1e-12,
        max_substeps: 128,
        max_rejects: 64,
    };
    let (actual, stats) = adaptive_t_phi1_action(&op, &b, t, options).unwrap();
    let exact: Vec<f64> = b
        .iter()
        .zip(&scaled_diagonal)
        .map(|(b, z)| t * b * z.exp_m1() / z)
        .collect();
    let error = norm2(
        &actual
            .iter()
            .zip(&exact)
            .map(|(x, y)| x - y)
            .collect::<Vec<_>>(),
    );
    let requested_target = options.tol * norm2(&b).max(1.0);
    assert!(
        error <= requested_target,
        "scaled return missed its direct requested target: error={error:e} \
         target={requested_target:e} stats={stats:?}"
    );
}

#[test]
fn finite_ritz_nonfinite_extends_but_nan_operator_is_fatal() {
    let y = vec![1.0, 1.0, 1.0, 0.3];
    let alpha = 1200.0;
    let beta = 4000.0;
    let stable_jordan = |x: &[f64]| {
        vec![
            -alpha * x[0] + beta * x[1],
            -alpha * x[1] + beta * x[2],
            -alpha * x[2],
            -alpha * x[3],
        ]
    };
    let options = AdaptiveKrylovOptions {
        m_init: 2,
        m_min: 2,
        m_max: 3,
        tol: 1e-10,
        max_substeps: 128,
        max_rejects: 64,
    };
    let (actual, stats) = adaptive_expm_action(&stable_jordan, &y, 1.0, options).unwrap();
    assert!(actual.iter().all(|value| *value == 0.0));
    assert_eq!(stats.nonfinite_rejections, 1, "{stats:?}");
    assert_eq!(stats.basis_extensions, 1, "{stats:?}");
    assert_eq!(stats.max_basis, 3, "{stats:?}");
    assert!(stats.max_attempt_error_ratio.is_finite(), "{stats:?}");
    assert!(stats.max_attempt_error_ratio <= 1.0, "{stats:?}");
    assert_eq!(
        stats.max_error_ratio, stats.max_attempt_error_ratio,
        "{stats:?}"
    );

    let nan_operator = |_x: &[f64]| vec![f64::NAN, 0.0, 0.0, 0.0];
    let error = adaptive_expm_action(&nan_operator, &y, 1.0, options).unwrap_err();
    assert!(matches!(
        error,
        AdaptiveKrylovError::OperatorReturnedNonFinite { .. }
    ));
}

#[test]
fn finite_physical_output_with_unrepresentable_projection_norm_fails_distinctly() {
    let huge_finite = |_x: &[f64]| vec![f64::MAX, f64::MAX];
    let error = adaptive_expm_action(
        &huge_finite,
        &[1.0, 0.0],
        1.0,
        AdaptiveKrylovOptions {
            m_init: 2,
            m_min: 2,
            m_max: 2,
            tol: 1e-10,
            max_substeps: 8,
            max_rejects: 8,
        },
    )
    .unwrap_err();
    assert!(matches!(
        error,
        AdaptiveKrylovError::ProjectionArithmeticNonFinite { .. }
    ));
}

#[test]
fn budget_error_preserves_complete_nonfinite_stats() {
    let y = vec![1.0, 1.0, 1.0, 0.3];
    let op = |x: &[f64]| {
        vec![
            -1200.0 * x[0] + 4000.0 * x[1],
            -1200.0 * x[1] + 4000.0 * x[2],
            -1200.0 * x[2],
            -1200.0 * x[3],
        ]
    };
    let error = adaptive_expm_action(
        &op,
        &y,
        1.0,
        AdaptiveKrylovOptions {
            m_init: 2,
            m_min: 2,
            m_max: 3,
            tol: 1e-10,
            max_substeps: 128,
            max_rejects: 1,
        },
    )
    .unwrap_err();
    let stats = error.stats().expect("budget errors must retain statistics");
    assert!(matches!(error, AdaptiveKrylovError::DidNotConverge { .. }));
    assert_eq!(stats.nonfinite_rejections, 1, "{stats:?}");
    assert_eq!(stats.rejected_steps, 1, "{stats:?}");
    assert_eq!(stats.projected_exponentials, 1, "{stats:?}");
    assert_eq!(stats.matvecs, 3, "{stats:?}");
    assert_eq!(stats.max_basis, 3, "{stats:?}");
    assert_eq!(stats.basis_extensions, 1, "{stats:?}");
}

#[test]
fn accepted_substep_budget_preserves_complete_stats() {
    let n = 48usize;
    let diagonal: Vec<f64> = (0..n)
        .map(|i| -(1.0 + 99.0 * i as f64 / (n - 1) as f64))
        .collect();
    let op = |x: &[f64]| {
        x.iter()
            .zip(&diagonal)
            .map(|(x, d)| x * d)
            .collect::<Vec<_>>()
    };
    let state: Vec<f64> = (0..n)
        .map(|i| 0.2 + ((31 * i + 7) % 59) as f64 / 43.0)
        .collect();
    let error = adaptive_expm_action(
        &op,
        &state,
        1.0,
        AdaptiveKrylovOptions {
            m_init: 4,
            m_min: 4,
            m_max: 4,
            tol: 1e-8,
            max_substeps: 1,
            max_rejects: 64,
        },
    )
    .unwrap_err();
    let stats = error.stats().expect("substep budget lost its ledger");
    assert!(matches!(error, AdaptiveKrylovError::DidNotConverge { .. }));
    assert_eq!(stats.accepted_steps, 1, "{stats:?}");
    assert!(stats.rejected_steps > 0, "{stats:?}");
    assert_eq!(stats.projection_builds, 1, "{stats:?}");
    assert_eq!(stats.matvecs, 4, "{stats:?}");
    assert_eq!(stats.max_basis, 4, "{stats:?}");
    assert_eq!(stats.final_basis, 4, "{stats:?}");
}

#[test]
fn aggregate_stats_does_not_erase_last_accept_on_zero_source() {
    let mut total = AdaptiveKrylovStats {
        accepted_steps: 1,
        final_basis: 7,
        max_error_ratio: 9.0,
        max_attempt_error_ratio: 9.0,
        max_accepted_error_ratio: 0.8,
        last_accepted_error_ratio: 0.7,
        ..AdaptiveKrylovStats::default()
    };
    total.accumulate(&AdaptiveKrylovStats::default());
    assert_eq!(total.final_basis, 7);
    assert_eq!(total.last_accepted_error_ratio, 0.7);
    assert_eq!(total.max_error_ratio, total.max_attempt_error_ratio);
}

#[test]
fn aggregate_target_semantics_tracks_first_work_and_mixed_actions() {
    let divided = AdaptiveKrylovTargetSemantics::CallerDividedResidualEstimate { divisor: 3.0 };
    let mut total = AdaptiveKrylovStats::default();
    let divided_work = AdaptiveKrylovStats {
        accepted_steps: 1,
        target_semantics: divided,
        ..AdaptiveKrylovStats::default()
    };
    total.accumulate(&divided_work);
    assert_eq!(
        total.target_semantics, divided,
        "first working source was lost"
    );

    total.accumulate(&AdaptiveKrylovStats::default());
    assert_eq!(
        total.target_semantics, divided,
        "empty default source changed established semantics"
    );

    total.accumulate(&AdaptiveKrylovStats {
        accepted_steps: 1,
        target_semantics: AdaptiveKrylovTargetSemantics::ResidualEstimateOnly,
        ..AdaptiveKrylovStats::default()
    });
    assert_eq!(
        total.target_semantics,
        AdaptiveKrylovTargetSemantics::MixedResidualEstimates
    );
}

#[test]
fn rejected_state_reuses_projection_without_extra_matvecs() {
    let n = 48usize;
    let diagonal: Vec<f64> = (0..n)
        .map(|i| -(1.0 + 99.0 * i as f64 / (n - 1) as f64))
        .collect();
    let op = |x: &[f64]| {
        x.iter()
            .zip(&diagonal)
            .map(|(x, d)| x * d)
            .collect::<Vec<_>>()
    };
    let state: Vec<f64> = (0..n)
        .map(|i| 0.2 + ((31 * i + 7) % 59) as f64 / 43.0)
        .collect();
    let options = AdaptiveKrylovOptions {
        m_init: 4,
        m_min: 4,
        m_max: 4,
        tol: 1e-8,
        max_substeps: 4096,
        max_rejects: 4096,
    };
    let (_, stats) = adaptive_expm_action(&op, &state, 1.0, options).unwrap();
    assert!(stats.rejected_steps > 0, "probe did not reject: {stats:?}");
    assert_eq!(stats.projection_builds, stats.accepted_steps, "{stats:?}");
    assert_eq!(stats.projection_reuses, stats.rejected_steps, "{stats:?}");
    assert_eq!(
        stats.projected_exponentials,
        stats.projection_builds + stats.projection_reuses,
        "{stats:?}"
    );
    assert_eq!(stats.matvecs, 4 * stats.projection_builds, "{stats:?}");
    assert_eq!(stats.basis_extensions, 0, "{stats:?}");
    assert_eq!(stats.tau_reductions, stats.rejected_steps, "{stats:?}");
}

#[test]
fn basis_extends_at_fixed_tau_before_tau_reduction() {
    let n = 40usize;
    let diagonal: Vec<f64> = (0..n)
        .map(|i| -(0.1 + 99.9 * i as f64 / (n - 1) as f64))
        .collect();
    let op = |x: &[f64]| {
        x.iter()
            .zip(&diagonal)
            .map(|(x, d)| x * d)
            .collect::<Vec<_>>()
    };
    let state: Vec<f64> = (0..n)
        .map(|i| 0.3 + ((17 * i + 11) % 53) as f64 / 37.0)
        .collect();
    let (_, stats) = adaptive_expm_action(
        &op,
        &state,
        1.0,
        AdaptiveKrylovOptions {
            m_init: 2,
            m_min: 2,
            m_max: 4,
            tol: 1e-8,
            max_substeps: 4096,
            max_rejects: 4096,
        },
    )
    .unwrap();
    assert!(stats.basis_extensions > 0, "{stats:?}");
    assert!(stats.tau_reductions > 0, "{stats:?}");
    assert!(stats.first_basis_extension_attempt > 0, "{stats:?}");
    assert!(
        stats.first_basis_extension_attempt < stats.first_tau_reduction_attempt,
        "tau reduced before capacity extension: {stats:?}"
    );
}

#[test]
fn tau_recovers_without_basis_shrink_growth_sawtooth() {
    let n = 80usize;
    let diagonal: Vec<f64> = (0..n)
        .map(|i| -(0.1 + 99.9 * i as f64 / (n - 1) as f64))
        .collect();
    let op = |x: &[f64]| {
        x.iter()
            .zip(&diagonal)
            .map(|(x, d)| x * d)
            .collect::<Vec<_>>()
    };
    let state: Vec<f64> = (0..n)
        .map(|i| 0.2 + ((i * 19 + 5) % 47) as f64 / 31.0)
        .collect();
    let t = 5.0;
    let exact: Vec<f64> = state
        .iter()
        .zip(&diagonal)
        .map(|(y, d)| y * (t * d).exp())
        .collect();
    let options = AdaptiveKrylovOptions {
        m_init: 6,
        m_min: 4,
        m_max: 8,
        tol: 1e-9,
        max_substeps: 4096,
        max_rejects: 4096,
    };
    let (actual, stats) = adaptive_expm_action(&op, &state, t, options).unwrap();
    let error = norm2(
        &actual
            .iter()
            .zip(&exact)
            .map(|(x, y)| x - y)
            .collect::<Vec<_>>(),
    );
    let target = options.tol * norm2(&state).max(1.0);
    println!("TAU_LEDGER error={error:e} target={target:e} stats={stats:?}");
    assert!(error <= target, "{stats:?}");
    assert!(stats.rejected_steps > 0, "{stats:?}");
    assert!(stats.tau_recoveries > 0, "{stats:?}");
    assert_eq!(stats.joint_tau_growth_basis_shrinks, 0, "{stats:?}");
    assert!(stats.max_rejection_streak <= 12, "{stats:?}");
    assert!(
        stats.rejected_steps * 3 < stats.accepted_steps,
        "reject/regrow saw-tooth persists: {stats:?}"
    );
    assert!(
        stats.basis_shrinks == 0 || stats.minimum_clean_accepts_before_basis_shrink >= 3,
        "basis shrank without a sustained clean streak: {stats:?}"
    );
}

#[test]
fn oscillatory_lane_records_bounded_controller_ledger() {
    let blocks = 32usize;
    let n = 2 * blocks;
    let lo = 0.1_f64.ln();
    let hi = 300.0_f64.ln();
    let frequencies: Vec<f64> = (0..blocks)
        .map(|i| (lo + i as f64 / (blocks - 1) as f64 * (hi - lo)).exp())
        .collect();
    let op = |x: &[f64]| {
        let mut out = vec![0.0; n];
        for k in 0..blocks {
            out[2 * k] = -frequencies[k] * x[2 * k + 1];
            out[2 * k + 1] = frequencies[k] * x[2 * k];
        }
        out
    };
    let state: Vec<f64> = (0..n)
        .map(|i| ((i * 23 + 7) % 79) as f64 / 41.0 - 0.8)
        .collect();
    let mut exact = vec![0.0; n];
    for k in 0..blocks {
        let c = frequencies[k].cos();
        let s = frequencies[k].sin();
        exact[2 * k] = c * state[2 * k] - s * state[2 * k + 1];
        exact[2 * k + 1] = s * state[2 * k] + c * state[2 * k + 1];
    }
    let options = AdaptiveKrylovOptions {
        m_init: 8,
        m_min: 6,
        m_max: 12,
        tol: 1e-10,
        max_substeps: 4096,
        max_rejects: 4096,
    };
    let target = options.tol * norm2(&state).max(1.0);
    match adaptive_expm_action(&op, &state, 1.0, options) {
        Ok((actual, stats)) => {
            let error = norm2(
                &actual
                    .iter()
                    .zip(&exact)
                    .map(|(x, y)| x - y)
                    .collect::<Vec<_>>(),
            );
            println!(
                "OSCILLATORY_LEDGER global_l2_error={error:e} requested_target={target:e} \
                 accepted_steps={} rejected_steps={} nonfinite_rejections={} matvecs={} \
                 projected_exponentials={} max_basis={} max_attempt_error_ratio={:e} \
                 max_accepted_error_ratio={:e} last_accepted_error_ratio={:e} \
                 tau_reductions={} tau_recoveries={} rejection_episodes={} \
                 max_rejection_streak={} budget_exhausted=false",
                stats.accepted_steps,
                stats.rejected_steps,
                stats.nonfinite_rejections,
                stats.matvecs,
                stats.projected_exponentials,
                stats.max_basis,
                stats.max_attempt_error_ratio,
                stats.max_accepted_error_ratio,
                stats.last_accepted_error_ratio,
                stats.tau_reductions,
                stats.tau_recoveries,
                stats.rejection_episodes,
                stats.max_rejection_streak,
            );
            assert!(error <= target, "{stats:?}");
            assert!(stats.rejected_steps * 3 < stats.accepted_steps, "{stats:?}");
            assert_eq!(stats.joint_tau_growth_basis_shrinks, 0, "{stats:?}");
            assert!(
                stats.iop2_columns > 0 && stats.full_mgs_columns == 0,
                "{stats:?}"
            );
        }
        Err(AdaptiveKrylovError::DidNotConverge { stats, .. }) => {
            println!(
                "OSCILLATORY_LEDGER global_l2_error=unavailable requested_target={target:e} \
                 accepted_steps={} rejected_steps={} nonfinite_rejections={} matvecs={} \
                 projected_exponentials={} max_basis={} max_attempt_error_ratio={:e} \
                 max_accepted_error_ratio={:e} last_accepted_error_ratio={:e} \
                 tau_reductions={} tau_recoveries={} rejection_episodes={} \
                 max_rejection_streak={} budget_exhausted=true",
                stats.accepted_steps,
                stats.rejected_steps,
                stats.nonfinite_rejections,
                stats.matvecs,
                stats.projected_exponentials,
                stats.max_basis,
                stats.max_attempt_error_ratio,
                stats.max_accepted_error_ratio,
                stats.last_accepted_error_ratio,
                stats.tau_reductions,
                stats.tau_recoveries,
                stats.rejection_episodes,
                stats.max_rejection_streak,
            );
            assert!(
                stats.accepted_steps == options.max_substeps
                    || stats.rejected_steps == options.max_rejects
            );
            assert!(stats.max_basis <= options.m_max, "{stats:?}");
        }
        Err(other) => panic!("oscillatory lane failed outside its explicit budget: {other:?}"),
    }
}

#[test]
fn truncated_lane_records_iop2_and_matches_dense_diagonal_oracle() {
    let n = 64usize;
    let diagonal: Vec<f64> = (0..n)
        .map(|i| -0.25 - 7.0 * i as f64 / (n - 1) as f64)
        .collect();
    let op = |x: &[f64]| {
        x.iter()
            .zip(&diagonal)
            .map(|(x, d)| x * d)
            .collect::<Vec<_>>()
    };
    let state: Vec<f64> = (0..n)
        .map(|i| ((29 * i + 11) % 67) as f64 / 43.0 - 0.65)
        .collect();
    let exact: Vec<f64> = state
        .iter()
        .zip(&diagonal)
        .map(|(y, d)| y * (1.75 * d).exp())
        .collect();
    let options = AdaptiveKrylovOptions {
        m_init: 8,
        m_min: 6,
        m_max: 12,
        tol: 1e-10,
        max_substeps: 256,
        max_rejects: 128,
    };
    let (actual, stats) = adaptive_expm_action(&op, &state, 1.75, options).unwrap();
    let error = norm2(
        &actual
            .iter()
            .zip(&exact)
            .map(|(x, y)| x - y)
            .collect::<Vec<_>>(),
    );
    assert!(error <= options.tol * norm2(&state).max(1.0), "{stats:?}");
    assert!(stats.iop2_columns > 0, "{stats:?}");
    assert_eq!(stats.full_mgs_columns, 0, "{stats:?}");
    assert!(stats.max_iop2_orthogonality_defect < 1e-10, "{stats:?}");
}

#[test]
fn full_capacity_lane_records_two_pass_mgs_and_orthogonality() {
    let diagonal = [
        -1.0,
        -1.0 - 1e-7,
        -1.0 - 2e-7,
        -1.0 - 4e-7,
        -1.0 - 8e-7,
        -1.0 - 16e-7,
    ];
    let op = |x: &[f64]| {
        x.iter()
            .zip(&diagonal)
            .map(|(x, d)| x * d)
            .collect::<Vec<_>>()
    };
    let state = vec![1.0, -0.7, 0.5, -0.3, 0.2, -0.1];
    let exact: Vec<f64> = state
        .iter()
        .zip(&diagonal)
        .map(|(y, d)| y * d.exp())
        .collect();
    let options = AdaptiveKrylovOptions {
        m_init: 6,
        m_min: 2,
        m_max: 8,
        tol: 1e-12,
        max_substeps: 32,
        max_rejects: 32,
    };
    let (actual, stats) = adaptive_expm_action(&op, &state, 1.0, options).unwrap();
    let error = norm2(
        &actual
            .iter()
            .zip(&exact)
            .map(|(x, y)| x - y)
            .collect::<Vec<_>>(),
    );
    assert!(error <= options.tol * norm2(&state).max(1.0), "{stats:?}");
    assert!(stats.full_mgs_columns > 0, "{stats:?}");
    assert_eq!(stats.iop2_columns, 0, "{stats:?}");
    assert_eq!(
        stats.full_mgs_passes,
        2 * stats.full_mgs_columns,
        "{stats:?}"
    );
    assert!(stats.max_full_mgs_orthogonality_defect < 1e-12, "{stats:?}");
}

fn lebedev26() -> (Vec<[f64; 3]>, Vec<f64>) {
    let pi = std::f64::consts::PI;
    let a = 1.0 / 3.0_f64.sqrt();
    let b = 1.0 / 2.0_f64.sqrt();
    let mut directions = Vec::new();
    let mut weights = Vec::new();
    for k in 0..3 {
        for sign in [-1.0, 1.0] {
            let mut direction = [0.0; 3];
            direction[k] = sign;
            directions.push(direction);
            weights.push(4.0 * pi / 21.0);
        }
    }
    for zero in 0..3 {
        let indices: Vec<_> = (0..3).filter(|index| *index != zero).collect();
        for sign1 in [-1.0, 1.0] {
            for sign2 in [-1.0, 1.0] {
                let mut direction = [0.0; 3];
                direction[indices[0]] = sign1 * b;
                direction[indices[1]] = sign2 * b;
                directions.push(direction);
                weights.push(16.0 * pi / 105.0);
            }
        }
    }
    for x in [-1.0, 1.0] {
        for y in [-1.0, 1.0] {
            for z in [-1.0, 1.0] {
                directions.push([x * a, y * a, z * a]);
                weights.push(9.0 * pi / 70.0);
            }
        }
    }
    (directions, weights)
}

#[test]
fn kato_invalid_domain_is_rejected_without_generated_kernel_panic() {
    let (directions, weights) = lebedev26();
    let state = [0.0, 0.0, 0.0, 0.0, 0.1];
    let y = vec![1.0; directions.len()];
    let options = AdaptiveKrylovOptions {
        m_init: 8,
        m_min: 6,
        m_max: 12,
        tol: 1e-10,
        max_substeps: 32,
        max_rejects: 32,
    };
    let outcome = std::panic::catch_unwind(|| {
        kato_aem2_step_adaptive(
            &directions,
            &weights,
            3,
            1.3,
            0.1,
            1.0,
            &state,
            &state,
            &state,
            2.0,
            &y,
            options,
        )
    });
    assert!(
        outcome.is_ok(),
        "invalid axis reached an asserting generated kernel"
    );
    assert!(matches!(
        outcome.unwrap(),
        Err(AdaptiveKrylovError::InvalidKatoDomain { field: "axis" })
    ));

    let mut invalid_velocity = state;
    invalid_velocity[4] = 1.0;
    assert!(matches!(
        kato_aem2_step_adaptive(
            &directions,
            &weights,
            1,
            1.3,
            0.1,
            1.0,
            &invalid_velocity,
            &state,
            &state,
            2.0,
            &y,
            options,
        ),
        Err(AdaptiveKrylovError::InvalidKatoDomain { field: "velocity" })
    ));

    let mut invalid_directions = directions.clone();
    invalid_directions[0][0] = f64::NAN;
    assert!(matches!(
        kato_aem2_step_adaptive(
            &invalid_directions,
            &weights,
            1,
            1.3,
            0.1,
            1.0,
            &state,
            &state,
            &state,
            2.0,
            &y,
            options,
        ),
        Err(AdaptiveKrylovError::InputNotFinite)
    ));

    let mut invalid_weights = weights.clone();
    invalid_weights[0] = 0.0;
    assert!(matches!(
        kato_aem2_step_adaptive(
            &directions,
            &invalid_weights,
            1,
            1.3,
            0.1,
            1.0,
            &state,
            &state,
            &state,
            2.0,
            &y,
            options,
        ),
        Err(AdaptiveKrylovError::InvalidKatoDomain { field: "weight" })
    ));

    assert!(matches!(
        kato_aem2_step_adaptive(
            &directions,
            &weights,
            1,
            1.3,
            f64::NAN,
            1.0,
            &state,
            &state,
            &state,
            2.0,
            &y,
            options,
        ),
        Err(AdaptiveKrylovError::NonFiniteTime)
    ));

    assert!(matches!(
        kato_aem2_step_adaptive(
            &directions,
            &weights,
            1,
            1.3,
            0.1,
            f64::MAX,
            &state,
            &state,
            &state,
            2.0,
            &y,
            options,
        ),
        Err(AdaptiveKrylovError::InvalidKatoDomain {
            field: "collision_scale"
        })
    ));
}

#[test]
fn kato_later_failure_merges_earlier_successful_action_stats() {
    let (directions, weights) = lebedev26();
    let state_q1 = [0.2375, 0.0, -0.11295198246134101, 0.865, 0.05];
    let state_mid = [
        0.237483198522475,
        0.000012265009715214,
        -0.11293368496280672,
        0.8650058629844937,
        0.049991577928173256,
    ];
    let state_q3 = [
        0.23746641180283926,
        0.000024519691346677,
        -0.11291538561917082,
        0.8650117491959564,
        0.04998315715921075,
    ];
    let y: Vec<f64> = (0..directions.len())
        .map(|i| ((19 * i + 7) % 37) as f64 / 23.0 + 0.2)
        .collect();
    let error = kato_aem2_step_adaptive(
        &directions,
        &weights,
        1,
        1.3,
        0.001,
        1e8,
        &state_q1,
        &state_mid,
        &state_q3,
        239.77404039036273,
        &y,
        AdaptiveKrylovOptions {
            m_init: 4,
            m_min: 4,
            m_max: 4,
            tol: 1e-12,
            max_substeps: 1,
            max_rejects: 64,
        },
    )
    .unwrap_err();
    let stats = error
        .stats()
        .expect("Kato failure must expose merged stats");
    let source_stats = match &error {
        AdaptiveKrylovError::KatoSubactionFailed { source, .. } => match source.as_ref() {
            AdaptiveKrylovError::DidNotConverge { stats, .. } => stats,
            other => panic!("later Kato source failure was not preserved: {other:?}"),
        },
        other => panic!("later Kato failure was not wrapped: {other:?}"),
    };
    assert!(
        stats.accepted_steps >= 1,
        "earlier success was lost: {stats:?}"
    );
    assert!(stats.matvecs >= 4, "earlier work was lost: {stats:?}");
    assert!(stats.projected_exponentials >= 1, "{stats:?}");
    assert!(
        stats.matvecs > source_stats.matvecs,
        "outer ledger did not merge prior work"
    );
}

fn tiny_time_options(tol: f64) -> AdaptiveKrylovOptions {
    AdaptiveKrylovOptions {
        m_init: 2,
        m_min: 2,
        m_max: 4,
        tol,
        max_substeps: 32,
        max_rejects: 32,
    }
}

#[test]
fn finite_nonzero_tiny_time_exponential_is_not_silently_skipped() {
    let t = 1e-16;
    let op = |x: &[f64]| x.iter().map(|value| -value / t).collect::<Vec<_>>();
    let y = vec![1.0, -0.5, 0.25, -0.125];
    let options = tiny_time_options(1e-12);
    let (actual, stats) = adaptive_expm_action(&op, &y, t, options).unwrap();
    let exact_scale = (-1.0_f64).exp();
    let error = norm2(
        &actual
            .iter()
            .zip(&y)
            .map(|(value, initial)| value - exact_scale * initial)
            .collect::<Vec<_>>(),
    );
    assert!(
        error <= options.tol * norm2(&y).max(1.0),
        "{error:e} {stats:?}"
    );
    assert!(
        stats.accepted_steps > 0,
        "nonzero time recorded zero work: {stats:?}"
    );
}

#[test]
fn finite_nonzero_tiny_time_phi_actions_are_not_silently_skipped() {
    let t = 1e-16;
    let op = |x: &[f64]| x.iter().map(|value| -value / t).collect::<Vec<_>>();
    let b = vec![1.0, -0.5, 0.25, -0.125];
    let phi_scale = 1.0 - (-1.0_f64).exp();

    let phi_options = tiny_time_options(1e-12);
    let (phi, phi_stats) = adaptive_phi1_action(&op, &b, t, phi_options).unwrap();
    let phi_error = norm2(
        &phi.iter()
            .zip(&b)
            .map(|(value, source)| value - phi_scale * source)
            .collect::<Vec<_>>(),
    );
    assert!(
        phi_error <= phi_options.tol * norm2(&b).max(1.0),
        "{phi_error:e} {phi_stats:?}"
    );
    assert!(phi_stats.accepted_steps > 0, "{phi_stats:?}");

    let unsupported = tiny_time_options(1e-20);
    let floor_error = adaptive_t_phi1_action(&op, &b, t, unsupported).unwrap_err();
    assert!(matches!(
        floor_error,
        AdaptiveKrylovError::ToleranceBelowArithmeticFloor { requested, floor }
            if requested == unsupported.tol && floor > requested
    ));

    let tphi_options = tiny_time_options(1e-12);
    let (tphi, tphi_stats) = adaptive_t_phi1_action(&op, &b, t, tphi_options).unwrap();
    let tphi_error = norm2(
        &tphi
            .iter()
            .zip(&b)
            .map(|(value, source)| value - t * phi_scale * source)
            .collect::<Vec<_>>(),
    );
    assert!(tphi_error <= 1e-30, "{tphi_error:e} {tphi_stats:?}");
    assert!(
        tphi_stats.accepted_steps > 0,
        "nonzero time recorded zero work: {tphi_stats:?}"
    );
}

#[test]
fn below_binary64_arithmetic_floor_is_rejected_before_action() {
    let calls = std::cell::Cell::new(0usize);
    let op = |x: &[f64]| {
        calls.set(calls.get() + 1);
        vec![-2.3 * x[0]]
    };
    let requested = 1e-30;
    let error = adaptive_expm_action(
        &op,
        &[1.0],
        0.7,
        AdaptiveKrylovOptions {
            m_init: 2,
            m_min: 2,
            m_max: 2,
            tol: requested,
            max_substeps: 8,
            max_rejects: 8,
        },
    )
    .unwrap_err();
    match error {
        AdaptiveKrylovError::ToleranceBelowArithmeticFloor {
            requested: actual,
            floor,
        } => {
            assert_eq!(actual, requested);
            assert_eq!(floor, 32.0 * f64::EPSILON);
        }
        other => panic!("wrong failure for unsupported tolerance: {other:?}"),
    }
    assert_eq!(calls.get(), 0, "operator ran before tolerance validation");
}

#[test]
fn full_capacity_scalar_action_is_invariant_under_inverse_time_scaling() {
    let options = AdaptiveKrylovOptions {
        m_init: 2,
        m_min: 2,
        m_max: 2,
        tol: 1e-10,
        max_substeps: 32,
        max_rejects: 32,
    };
    let expected = (-1.0_f64).exp();
    for scale in [1.0, 1e-8, 1e-12, 1e-14, 1e-16] {
        let op = |x: &[f64]| vec![-scale * x[0]];
        let (actual, stats) = adaptive_expm_action(&op, &[1.0], 1.0 / scale, options).unwrap();
        let error = (actual[0] - expected).abs();
        eprintln!(
            "SCALAR_SCALE_RESULT scale={scale:e} t={:e} error={error:e} target={:e} stats={stats:?}",
            1.0 / scale,
            options.tol
        );
        assert!(
            error <= options.tol,
            "scaled scalar action missed target: scale={scale:e} error={error:e} stats={stats:?}"
        );
    }
}

fn fwht(values: &mut [f64]) {
    let mut width = 1usize;
    while width < values.len() {
        for start in (0..values.len()).step_by(2 * width) {
            for j in 0..width {
                let a = values[start + j];
                let b = values[start + j + width];
                values[start + j] = a + b;
                values[start + j + width] = a - b;
            }
        }
        width *= 2;
    }
    let normalization = (values.len() as f64).sqrt();
    for value in values {
        *value /= normalization;
    }
}

#[test]
fn inverse_scaled_symmetric_hadamard_oracle_meets_target_or_fails_closed() {
    let n = 64usize;
    let scale = 1e-14;
    let t = 1.0 / scale;
    let diagonal: Vec<f64> = (0..n).map(|i| -scale * i as f64).collect();
    let op = |x: &[f64]| {
        let mut transformed = x.to_vec();
        fwht(&mut transformed);
        for (value, diagonal) in transformed.iter_mut().zip(&diagonal) {
            *value *= diagonal;
        }
        fwht(&mut transformed);
        transformed
    };
    let y: Vec<f64> = (0..n)
        .map(|i| ((29 * i + 5) % 71) as f64 / 37.0 - 0.7)
        .collect();
    let mut expected = y.clone();
    fwht(&mut expected);
    for (value, diagonal) in expected.iter_mut().zip(&diagonal) {
        *value *= (t * diagonal).exp();
    }
    fwht(&mut expected);
    for m_max in [12usize, 24usize] {
        let options = AdaptiveKrylovOptions {
            m_init: 8,
            m_min: 6,
            m_max,
            tol: 1e-10,
            max_substeps: 4096,
            max_rejects: 4096,
        };
        match adaptive_expm_action(&op, &y, t, options) {
            Ok((actual, stats)) => {
                let error = norm2(
                    &actual
                        .iter()
                        .zip(&expected)
                        .map(|(value, expected)| value - expected)
                        .collect::<Vec<_>>(),
                );
                let target = options.tol * norm2(&y).max(1.0);
                eprintln!(
                    "SCALED_HADAMARD_RESULT m_max={m_max} error={error:e} target={target:e} stats={stats:?}"
                );
                assert!(
                    error <= target,
                    "scaled symmetric action silently violated target: m_max={m_max} error={error:e} target={target:e} stats={stats:?}"
                );
            }
            Err(AdaptiveKrylovError::DidNotConverge { stats, .. }) => {
                eprintln!("SCALED_HADAMARD_FAIL_CLOSED m_max={m_max} stats={stats:?}")
            }
            Err(other) => panic!("scaled symmetric lane failed unexpectedly: {other:?}"),
        }
    }
}

fn jordan_oracle(n: usize, alpha: f64, beta: f64, t: f64) -> Vec<f64> {
    let mut expected = vec![0.0; n];
    expected[0] = (-alpha * t).exp();
    for k in 1..n {
        expected[k] = expected[k - 1] * beta * t / k as f64;
    }
    expected
}

#[test]
fn nonnormal_forward_violation_is_explicitly_residual_only_negative_control() {
    let n = 40usize;
    let alpha = 0.0_f64;
    let beta = 10.0_f64;
    let t = 1.0_f64;
    let op = |x: &[f64]| {
        let mut out = vec![0.0; n];
        for i in 0..n {
            out[i] -= alpha * x[i];
            if i + 1 < n {
                out[i + 1] += beta * x[i];
            }
        }
        out
    };
    let mut y = vec![0.0; n];
    y[0] = 1.0;
    let options = AdaptiveKrylovOptions {
        m_init: 4,
        m_min: 2,
        m_max: 6,
        tol: 1e-10,
        max_substeps: 4096,
        max_rejects: 4096,
    };
    let (actual, stats) = adaptive_expm_action(&op, &y, t, options).unwrap();
    let error = norm2(
        &actual
            .iter()
            .zip(jordan_oracle(n, alpha, beta, t))
            .map(|(value, expected)| value - expected)
            .collect::<Vec<_>>(),
    );
    let target = options.tol * norm2(&y).max(1.0);
    eprintln!(
        "NONNORMAL_RESIDUAL_ONLY_NEGATIVE_CONTROL error={error:e} target={target:e} stats={stats:?}"
    );
    assert!(
        error > target,
        "negative control no longer exposes the contract boundary"
    );
    assert_eq!(
        stats.target_semantics,
        AdaptiveKrylovTargetSemantics::ResidualEstimateOnly
    );
}

#[test]
fn caller_divided_residual_budget_is_explicitly_not_forward_certified() {
    let n = 40usize;
    let alpha = 0.0_f64;
    let beta = 10.0_f64;
    let t = 1.0_f64;
    let divisor = ((beta - alpha) * t).exp();
    let op = |x: &[f64]| {
        let mut out = vec![0.0; n];
        for i in 0..n {
            out[i] -= alpha * x[i];
            if i + 1 < n {
                out[i + 1] += beta * x[i];
            }
        }
        out
    };
    let mut y = vec![0.0; n];
    y[0] = 1.0;
    let options = AdaptiveKrylovOptions {
        m_init: 4,
        m_min: 2,
        m_max: 6,
        tol: 1e-10,
        max_substeps: 4096,
        max_rejects: 4096,
    };
    let expected = jordan_oracle(n, alpha, beta, t);
    match adaptive_expm_action_with_residual_budget_divisor(&op, &y, t, options, divisor) {
        Ok((actual, stats)) => {
            let error = norm2(
                &actual
                    .iter()
                    .zip(expected)
                    .map(|(value, expected)| value - expected)
                    .collect::<Vec<_>>(),
            );
            let target = options.tol * norm2(&y).max(1.0);
            eprintln!(
                "DIVIDED_JORDAN_RESIDUAL_RESULT status=ok divisor={divisor:e} error={error:e} target={target:e} forward_certified=false stats={stats:?}"
            );
            assert_eq!(
                stats.target_semantics,
                AdaptiveKrylovTargetSemantics::CallerDividedResidualEstimate { divisor }
            );
        }
        Err(AdaptiveKrylovError::DidNotConverge { stats, .. }) => {
            eprintln!(
                "DIVIDED_JORDAN_RESIDUAL_RESULT status=fail_closed divisor={divisor:e} forward_certified=false stats={stats:?}"
            );
            assert_eq!(
                stats.target_semantics,
                AdaptiveKrylovTargetSemantics::CallerDividedResidualEstimate { divisor }
            );
        }
        Err(other) => panic!("divided residual lane failed outside its budget: {other:?}"),
    }

    for invalid in [0.5, f64::INFINITY, f64::NAN] {
        assert!(matches!(
            adaptive_expm_action_with_residual_budget_divisor(&op, &y, t, options, invalid),
            Err(AdaptiveKrylovError::InvalidResidualBudgetDivisor { .. })
        ));
    }

    // Even a divisor obtained from a valid semigroup-norm upper bound does not
    // turn this endpoint projected-residual heuristic into a forward certificate.
    let diagonal: Vec<f64> = (0..n)
        .map(|i| -0.1 - 19.9 * i as f64 / (n - 1) as f64)
        .collect();
    let state: Vec<f64> = (0..n)
        .map(|i| 0.2 + ((17 * i + 3) % 43) as f64 / 31.0)
        .collect();
    let coupling = 1e4_f64;
    let similarity = |x: &[f64]| {
        let mut transformed = x.to_vec();
        transformed[0] -= coupling * x[n - 1];
        let mut out: Vec<f64> = transformed
            .iter()
            .zip(&diagonal)
            .map(|(value, diagonal)| value * diagonal)
            .collect();
        out[0] += coupling * out[n - 1];
        out
    };
    let mut exact_transformed = state.clone();
    exact_transformed[0] -= coupling * state[n - 1];
    let mut exact: Vec<f64> = exact_transformed
        .iter()
        .zip(&diagonal)
        .map(|(value, diagonal)| value * (0.2 * diagonal).exp())
        .collect();
    exact[0] += coupling * exact[n - 1];
    let similarity_divisor = n as f64 + coupling * coupling;
    let similarity_options = AdaptiveKrylovOptions {
        m_init: 4,
        m_min: 2,
        m_max: 10,
        tol: 1e-10,
        max_substeps: 512,
        max_rejects: 512,
    };
    let (actual, stats) = adaptive_expm_action_with_residual_budget_divisor(
        &similarity,
        &state,
        0.2,
        similarity_options,
        similarity_divisor,
    )
    .unwrap();
    let error = norm2(
        &actual
            .iter()
            .zip(exact)
            .map(|(value, expected)| value - expected)
            .collect::<Vec<_>>(),
    );
    let target = similarity_options.tol * norm2(&state).max(1.0);
    eprintln!(
        "DIVIDED_SIMILARITY_NEGATIVE_CONTROL error={error:e} target={target:e} divisor={similarity_divisor:e} forward_certified=false stats={stats:?}"
    );
    assert!(
        error > target,
        "negative control stopped exposing the contract boundary"
    );
    assert_eq!(
        stats.target_semantics,
        AdaptiveKrylovTargetSemantics::CallerDividedResidualEstimate {
            divisor: similarity_divisor
        }
    );
}

#[test]
fn time_significant_residual_is_not_false_happy_breakdown() {
    let op = |x: &[f64]| vec![0.0, 1e-15 * x[0]];
    let options = AdaptiveKrylovOptions {
        m_init: 2,
        m_min: 2,
        m_max: 2,
        tol: 1e-12,
        max_substeps: 8,
        max_rejects: 8,
    };
    let (actual, stats) = adaptive_expm_action(&op, &[1.0, 0.0], 1e15, options).unwrap();
    let error = norm2(&[actual[0] - 1.0, actual[1] - 1.0]);
    assert!(error <= options.tol, "{error:e} {stats:?}");
    assert_eq!(
        stats.max_basis, 2,
        "tiny Arnoldi residual was discarded: {stats:?}"
    );
    assert_eq!(stats.final_basis, 2, "{stats:?}");
}

#[test]
fn telemetry_records_partial_rejected_state_extension_before_failure() {
    let calls = std::cell::Cell::new(0usize);
    let op = |x: &[f64]| {
        let call = calls.get();
        calls.set(call + 1);
        if call >= 5 {
            return vec![f64::NAN; x.len()];
        }
        let mut out = vec![0.0; x.len()];
        for i in 0..x.len() - 1 {
            out[i + 1] = 20.0 * x[i];
        }
        out
    };
    let error = adaptive_expm_action(
        &op,
        &[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        1.0,
        AdaptiveKrylovOptions {
            m_init: 4,
            m_min: 4,
            m_max: 8,
            tol: 1e-12,
            max_substeps: 8,
            max_rejects: 8,
        },
    )
    .unwrap_err();
    let stats = match error {
        AdaptiveKrylovError::OperatorReturnedNonFinite { stats } => stats,
        other => panic!("wrong failure class: {other:?}"),
    };
    assert_eq!(stats.accepted_steps, 0, "{stats:?}");
    assert_eq!(
        stats.max_basis, 5,
        "completed extension column was lost: {stats:?}"
    );
    assert_eq!(stats.basis_extension_columns, 1, "{stats:?}");
    assert_eq!(
        stats.final_basis, 0,
        "no projection was accepted: {stats:?}"
    );
}

#[test]
fn telemetry_reports_actual_accepted_basis_not_requested_controller_basis() {
    let zero = |x: &[f64]| vec![0.0; x.len()];
    let (actual, stats) = adaptive_expm_action(
        &zero,
        &[1.0, -0.5, 0.25, -0.125],
        1.0,
        AdaptiveKrylovOptions {
            m_init: 4,
            m_min: 2,
            m_max: 4,
            tol: 1e-12,
            max_substeps: 8,
            max_rejects: 8,
        },
    )
    .unwrap();
    let identity_error = norm2(
        &actual
            .iter()
            .zip([1.0, -0.5, 0.25, -0.125])
            .map(|(value, expected)| value - expected)
            .collect::<Vec<_>>(),
    );
    assert!(identity_error <= 1e-14, "{identity_error:e} {stats:?}");
    assert_eq!(stats.accepted_steps, 1, "{stats:?}");
    assert_eq!(stats.max_basis, 1, "{stats:?}");
    assert_eq!(
        stats.final_basis, 1,
        "requested basis leaked into telemetry: {stats:?}"
    );
}

#[test]
fn zero_attained_basis_is_not_replaced_by_requested_basis_on_failure() {
    let nonfinite = |x: &[f64]| vec![f64::NAN; x.len()];
    let error = adaptive_expm_action(
        &nonfinite,
        &[1.0, 0.0, 0.0, 0.0],
        1.0,
        AdaptiveKrylovOptions {
            m_init: 4,
            m_min: 2,
            m_max: 4,
            tol: 1e-12,
            max_substeps: 8,
            max_rejects: 8,
        },
    )
    .unwrap_err();
    let stats = error
        .stats()
        .expect("operator failure must retain telemetry");
    assert_eq!(stats.accepted_steps, 0, "{stats:?}");
    assert_eq!(stats.max_basis, 0, "{stats:?}");
    assert_eq!(
        stats.final_basis, 0,
        "requested basis leaked into telemetry: {stats:?}"
    );
}
