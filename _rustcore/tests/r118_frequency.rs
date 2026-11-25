use bianchi_rustcore::homogeneous_sky::{
    frequency::{replay_frequency, FrequencyGrid, Line, LineHistory, VelocityNode},
    replay::StepRecord,
    spectral::replay_rays,
    CollisionEvent, CollisionScheme,
};
use bianchi_rustcore::kinetic::lie_history::RayNode;
fn rec(a: f64, b: f64, events: Vec<CollisionEvent>) -> StepRecord {
    StepRecord {
        left: RayNode {
            eta: a,
            ..Default::default()
        },
        right: RayNode {
            eta: b,
            ..Default::default()
        },
        first: events,
        second: vec![],
    }
}
fn event(t: f64, b: [f64; 3], scheme: CollisionScheme) -> CollisionEvent {
    CollisionEvent {
        depth: t,
        beta: b,
        gain_map: None,
        scheme,
        sources: vec![],
    }
}
#[test]
fn moving_mesh_flrw_preserves_number_and_free_spectrum() {
    let g = FrequencyGrid::new(-12., 5., 256).unwrap();
    let r = [rec(0., 0.7, vec![])];
    let s = replay_frequency(&r, 4, 8, &g, None).unwrap();
    assert!((s.history[0].number_centered - 1.).abs() < 2e-10);
    assert!((s.history[1].number_centered - s.history[0].number_centered).abs() < 2e-13);
    assert!((s.history[1].energy_centered - s.history[0].energy_centered).abs() < 2e-13);
    assert!(s.history[1].min_screen_relative >= -1e-10);
    assert!((s.samples()[0].log_shift + 0.7).abs() < 1e-13);
}
#[test]
fn finite_tilt_collision_conserves_number_with_boundary_ledger() {
    let r = [rec(
        0.,
        0.1,
        vec![event(0.15, [0.2, -0.1, 0.05], CollisionScheme::Sdirk2)],
    )];
    let oracle = replay_rays(&r, 4, 8).unwrap();
    let mut errors = vec![];
    for n in [128, 256, 512, 1024] {
        let g = FrequencyGrid::new(-12., 5., n).unwrap();
        let s = replay_frequency(&r, 4, 8, &g, None).unwrap();
        let q = &s.history[1];
        assert!(s.max_number_defect < 2e-12);
        assert!(s.max_material_energy_defect < 2e-12);
        assert!(q.min_screen_relative >= -1e-10);
        let error = (q.energy_centered - oracle.history[1].energy_comoving).abs();
        errors.push(error);
    }
    eprintln!("frequency grid B4 errors {:?}", errors);
    assert!(errors.windows(2).all(|w| w[1] < w[0]) && errors[3] < 3e-4);
    let g = FrequencyGrid::new(-1., 1., 80).unwrap();
    let s = replay_frequency(&r, 4, 8, &g, None).unwrap();
    assert!(s.history[1].escaped_number_centered > 0.);
    assert!(s.max_number_defect < 2e-12);
}
#[test]
fn finite_line_turning_point_is_not_a_sobolev_singularity() {
    let g = FrequencyGrid::new(-2., 2., 128).unwrap();
    let r: Vec<_> = (0..64)
        .map(|i| rec(i as f64 * 0.4 / 64., (i + 1) as f64 * 0.4 / 64., vec![]))
        .collect();
    let v: Vec<_> = (0..=64)
        .map(|i| {
            let t = i as f64 * 0.4 / 64.;
            VelocityNode {
                eta: t,
                beta: [0., 0., (-t + 3. * (t - 0.2).powi(2)).tanh()],
            }
        })
        .collect();
    let h = LineHistory::new(Line::new(0., 0.04, 0.08, 0.).unwrap(), v, 2).unwrap();
    let s = replay_frequency(&r, 4, 8, &g, Some(&h)).unwrap();
    assert!(s.min_drift.unwrap() < 0. && s.max_drift.unwrap() > 0.);
    assert!(s.turning_rays > 0);
    assert!(s.history.last().unwrap().line_number_centered < 0.);
    assert!(s.max_line_number_defect < 2e-12);
    assert!(s.samples().iter().all(|q| q
        .occupation
        .iter()
        .all(|m| m.iter().flatten().all(|x| x.is_finite()))));
}
#[test]
fn invalid_line_and_grid_are_rejected() {
    assert!(FrequencyGrid::new(1., -1., 128).is_err());
    assert!(Line::new(0., 0., 1., 0.).is_err());
    assert!(Line::new(0., 0.1, -1., 0.).is_err());
    assert!(LineHistory::new(
        Line::new(0., 0.1, 1., 0.).unwrap(),
        vec![
            VelocityNode {
                eta: 0.,
                beta: [1., 0., 0.]
            },
            VelocityNode {
                eta: 1.,
                beta: [0.; 3]
            }
        ],
        1
    )
    .is_err());
}

#[test]
fn optically_thick_finite_line_relaxes_without_negative_transmission() {
    let g = FrequencyGrid::new(-0.04, 0.04, 8).unwrap();
    let r = [rec(0., 0.01, vec![])];
    let h = LineHistory::new(
        Line::new(0., 0.5, 1e6, 0.23).unwrap(),
        vec![
            VelocityNode {
                eta: 0.,
                beta: [0.; 3],
            },
            VelocityNode {
                eta: 0.01,
                beta: [0.; 3],
            },
        ],
        1,
    )
    .unwrap();
    let s = replay_frequency(&r, 4, 8, &g, Some(&h)).unwrap();
    for q in s.samples() {
        for f in q.occupation {
            let tr = f[0][0] + f[1][1] + f[2][2];
            assert!((tr - 0.23).abs() < 5e-13);
        }
    }
    assert!(s.max_line_number_defect < 2e-12);
}

#[test]
fn normal_energy_ledger_separates_geometry_line_scattering_and_projection() {
    let r = [rec(
        0.,
        0.1,
        vec![event(0.3, [0.2, -0.1, 0.05], CollisionScheme::Sdirk2)],
    )];
    let g = FrequencyGrid::new(-1., 1., 128).unwrap();
    let line = LineHistory::new(
        Line::new(0., 0.08, 0.1, 0.2).unwrap(),
        vec![
            VelocityNode {
                eta: 0.,
                beta: [0.2, -0.1, 0.05],
            },
            VelocityNode {
                eta: 0.1,
                beta: [0.2, -0.1, 0.05],
            },
        ],
        4,
    )
    .unwrap();
    let s = replay_frequency(&r, 4, 8, &g, Some(&line)).unwrap();
    assert!(s.normal_energy_balance_defect().abs() < 2e-12);
    assert!(s.number_continuity_defect(&r).unwrap().abs() < 2e-12);
    let q = s.history.last().unwrap();
    assert!(q.escaped_energy_centered > 0.);
    assert!(q.thomson_normal_projection_energy_centered.abs() > 0.);
    assert!(q.line_normal_projection_energy_centered.abs() > 0.);
    assert!(s.max_material_energy_defect < 2e-12);
}
#[test]
fn observer_frequency_grid_boost_is_covariant_without_remapping() {
    let g = FrequencyGrid::new(-2., 2., 32).unwrap();
    let r = [rec(
        0.,
        0.03,
        vec![event(
            0.1,
            [0.2, -0.1, 0.05],
            CollisionScheme::BackwardEuler,
        )],
    )];
    let s = replay_frequency(&r, 4, 8, &g, None).unwrap();
    let b = [0.3, 0.1, -0.2];
    let gamma = 1. / (1. - b.iter().map(|v| v * v).sum::<f64>()).sqrt();
    for (x, y) in s.samples().iter().zip(s.observer_samples(b).unwrap()) {
        let d = gamma * (1. - x.direction.iter().zip(b).map(|(u, v)| u * v).sum::<f64>());
        assert!((y.log_shift - x.log_shift - d.ln()).abs() < 1e-15);
        assert!((y.weight - x.weight / (d * d)).abs() < 1e-15);
        for (f, fo) in x.occupation.iter().zip(&y.occupation) {
            let tr = |m: &[[f64; 3]; 3]| m[0][0] + m[1][1] + m[2][2];
            assert!((tr(f) - tr(fo)).abs() < 2e-14 * tr(f).abs().max(1.));
        }
    }
}

#[test]
fn projected_sdirk_resolves_time_order_at_fixed_frequency_mesh() {
    use bianchi_rustcore::homogeneous_sky::frequency::{
        replay_frequency_with_method, FrequencyMethod,
    };
    let g = FrequencyGrid::new(-4., 3., 64).unwrap();
    let mut en = Vec::new();
    for n in [2, 4, 8, 16] {
        let records: Vec<_> = (0..n)
            .map(|i| {
                rec(
                    i as f64 * 0.1 / n as f64,
                    (i + 1) as f64 * 0.1 / n as f64,
                    vec![event(
                        0.3 / n as f64,
                        [0.2, -0.1, 0.05],
                        CollisionScheme::Sdirk2,
                    )],
                )
            })
            .collect();
        let s = replay_frequency_with_method(&records, 4, 8, &g, None, FrequencyMethod::Projected)
            .unwrap();
        assert!(s.max_fv_stage_residual < 2e-13);
        assert!(s.max_number_defect < 2e-12);
        assert!(s.normal_energy_balance_defect().abs() < 2e-12);
        en.push(s.history.last().unwrap().energy_centered);
    }
    let ratio = (en[1] - en[2]).abs() / (en[2] - en[3]).abs();
    eprintln!("projected FV energy sequence {en:?}, final ratio {ratio:e}");
    assert!(ratio > 3.7 && ratio < 4.4);
}
