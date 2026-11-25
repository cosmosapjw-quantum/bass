use bianchi_rustcore::homogeneous_sky::{
    replay::StepRecord,
    spectral::{replay_harmonic, replay_rays},
    CollisionEvent, CollisionScheme,
};
use bianchi_rustcore::kinetic::lie_history::RayNode;
fn event(depth: f64, beta: [f64; 3], scheme: CollisionScheme) -> CollisionEvent {
    // Only kinematic inputs belong to spectral replay. The original
    // bolometric source is deliberately not supplied.
    CollisionEvent {
        depth,
        beta,
        scheme,
        gain_map: None,
        sources: vec![],
    }
}
fn record(a: RayNode, b: RayNode, events: Vec<CollisionEvent>) -> StepRecord {
    StepRecord {
        left: a,
        right: b,
        first: events,
        second: vec![],
    }
}
#[test]
fn isotropic_expansion_and_rest_scattering_have_no_centered_distortion() {
    let a = RayNode {
        eta: 0.,
        ..Default::default()
    };
    let b = RayNode {
        eta: 0.7,
        ..a.clone()
    };
    let records = [record(
        a,
        b,
        vec![event(0.7, [0.; 3], CollisionScheme::Sdirk2)],
    )];
    let sky = replay_harmonic(&records, 6, 16, 32).unwrap();
    for q in sky.samples().unwrap() {
        assert!((q.b3 - 1.).abs() < 1e-12 && (q.b4 - 1.).abs() < 1e-12);
        assert!(q.mean_log_t.abs() < 1e-14 && q.variance.abs() < 1e-14);
    }
    assert!(sky.max_collision_number_defect < 1e-12);
}
#[test]
fn moving_thomson_creates_distortion_and_preserves_number() {
    let a = RayNode {
        eta: 0.,
        ..Default::default()
    };
    let b = RayNode {
        eta: 0.1,
        ..a.clone()
    };
    for scheme in [CollisionScheme::BackwardEuler, CollisionScheme::Sdirk2] {
        let records = [record(
            a.clone(),
            b.clone(),
            vec![event(0.15, [0.2, -0.1, 0.05], scheme)],
        )];
        let h = replay_harmonic(&records, 16, 40, 80).unwrap();
        let r = replay_rays(&records, 40, 80).unwrap();
        assert!(h.max_collision_number_defect < 2e-12 && r.max_collision_number_defect < 2e-12);
        assert!(h.max_collision_rest_energy_defect < 2e-12);
        let hs = h.samples().unwrap();
        let rs = r.samples().unwrap();
        assert!(hs.iter().any(|q| q.variance > 1e-3));
        let gap = hs
            .iter()
            .zip(rs)
            .map(|(a, b)| {
                (a.variance - b.variance)
                    .abs()
                    .max((a.b3 - b.b3).abs())
                    .max((a.b4 - b.b4).abs())
            })
            .fold(0., f64::max);
        eprintln!(
            "moving beta={} scheme={scheme:?} gap={gap:e} mean variance={:e}",
            0.229,
            h.history.last().unwrap().mean_variance
        );
        assert!(gap < 1e-8);
        for q in &hs {
            assert!(q.variance >= -1e-10 && q.y_m >= -1e-10);
        }
    }
}
#[test]
fn collisionless_anisotropic_redshift_changes_temperature_not_spectrum() {
    let a = RayNode {
        eta: 0.,
        shear: [[0.08, 0., 0.], [0., -0.03, 0.], [0., 0., -0.05]],
        ..Default::default()
    };
    let b = RayNode {
        eta: 0.3,
        ..a.clone()
    };
    let records = [record(a, b, vec![])];
    let h = replay_harmonic(&records, 12, 24, 48).unwrap();
    let r = replay_rays(&records, 24, 48).unwrap();
    let hs = h.samples().unwrap();
    let rs = r.samples().unwrap();
    assert!(hs.iter().any(|q| q.mean_log_t.abs() > 0.01));
    // Different ray directions at the final slice; compare invariants, not
    // array-indexed angular samples.
    assert!(hs.iter().map(|q| q.variance.abs()).fold(0., f64::max) < 2e-8);
    assert!(rs.iter().map(|q| q.variance.abs()).fold(0., f64::max) < 1e-16);
    assert!((h.history.last().unwrap().number_comoving - 1.).abs() < 1e-9);
}

#[test]
fn observer_boost_shifts_mean_but_not_width_or_mellin_distortion() {
    let a = RayNode {
        eta: 0.,
        ..Default::default()
    };
    let b = RayNode {
        eta: 0.1,
        ..a.clone()
    };
    let records = [record(
        a,
        b,
        vec![event(0.2, [0.3, -0.1, 0.2], CollisionScheme::Sdirk2)],
    )];
    let h = replay_rays(&records, 24, 48).unwrap();
    let q = h.samples().unwrap();
    let beta = [-0.24, 0.31, 0.15];
    let o = h.observer_samples(beta).unwrap();
    let gamma = 1. / (1. - beta.iter().map(|b| b * b).sum::<f64>()).sqrt();
    for (x, y) in q.iter().zip(o) {
        let d = gamma
            * (1.
                - x.direction
                    .iter()
                    .zip(beta)
                    .map(|(e, b)| e * b)
                    .sum::<f64>());
        assert!((x.variance - y.variance).abs() < 2e-15);
        assert!((x.y_m - y.y_m).abs() < 2e-15);
        assert!((y.mean_log_t - x.mean_log_t - d.ln()).abs() < 2e-15);
        assert!((y.b3 - x.b3 * d.powi(3)).abs() < 4e-15);
        assert!((y.b4 - x.b4 * d.powi(4)).abs() < 8e-15);
    }
}
#[test]
fn thin_isotropic_cells_do_not_create_spurious_log_width() {
    let a = RayNode {
        eta: 0.,
        ..Default::default()
    };
    let b = RayNode {
        eta: 0.01,
        ..a.clone()
    };
    let records = [record(
        a,
        b,
        vec![event(1e-10, [0.; 3], CollisionScheme::Sdirk2); 512],
    )];
    let s = replay_harmonic(&records, 2, 6, 12).unwrap();
    assert!(s.history.last().unwrap().max_variance.abs() < 1e-25);
    assert!((s.history.last().unwrap().number_comoving - 1.).abs() < 1e-14);
    assert!(s
        .samples()
        .unwrap()
        .iter()
        .all(|q| q.mean_log_t == 0. && q.variance == 0.));
}

#[test]
fn underresolved_log_moment_projection_is_reported_not_clipped() {
    let a = RayNode {
        eta: 0.,
        shear: [[0.1, 0., 0.], [0., 0.1, 0.], [0., 0., -0.2]],
        ..Default::default()
    };
    let n = 32;
    let records: Vec<_> = (0..n)
        .map(|i| {
            record(
                RayNode {
                    eta: 0.3 * i as f64 / n as f64,
                    ..a.clone()
                },
                RayNode {
                    eta: 0.3 * (i + 1) as f64 / n as f64,
                    ..a.clone()
                },
                vec![],
            )
        })
        .collect();
    let low = replay_harmonic(&records, 2, 10, 24).unwrap();
    let high = replay_harmonic(&records, 12, 20, 40).unwrap();
    let q = low
        .history
        .iter()
        .map(|s| s.min_variance)
        .fold(0., f64::min);
    eprintln!(
        "low L=2 min variance {q:e}, high L=12 min variance {:e}",
        high.history
            .iter()
            .map(|s| s.min_variance)
            .fold(0., f64::min)
    );
    assert!(q < -1e-5);
    assert!(!low.sampled_necessary_checks(1e-9).unwrap());
    assert!(high.sampled_necessary_checks(1e-9).unwrap());
    assert!(high.sampled_necessary_checks(-1.).is_err());
}
