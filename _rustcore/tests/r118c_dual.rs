use bianchi_rustcore::homogeneous_sky::{
    frequency::{
        dual::{replay_dual_frequency, reversible_pair_weights, Redistribution},
        FrequencyGrid, Line, LineHistory, VelocityNode,
    },
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
fn line(eta: f64, center: f64, width: f64, strength: f64, source: f64) -> LineHistory {
    LineHistory::new(
        Line::new(center, width, strength, source).unwrap(),
        vec![
            VelocityNode {
                eta: 0.,
                beta: [0.; 3],
            },
            VelocityNode { eta, beta: [0.; 3] },
        ],
        2,
    )
    .unwrap()
}
#[test]
fn dual_projection_matches_both_planck_moments_and_free_transport() {
    let g = FrequencyGrid::new(-12., 5., 128).unwrap();
    let r = [rec(0., 0.4, vec![])];
    let s = replay_dual_frequency(&r, 4, 8, &g, None, None).unwrap();
    for q in &s.history {
        assert!((q.number_centered - 1.).abs() < 2e-10);
        assert!((q.energy_centered - 1.).abs() < 2e-10);
    }
    assert_eq!(s.samples()[0].number_mass.len(), 129);
}
#[test]
fn dual_thomson_matches_bolometric_and_boundary_invariants() {
    for scheme in [CollisionScheme::BackwardEuler, CollisionScheme::Sdirk2] {
        let r = [rec(0., 0.1, vec![event(0.15, [0.2, -0.1, 0.05], scheme)])];
        let oracle = replay_rays(&r, 4, 8).unwrap();
        for (lo, hi) in [(-12., 5.), (-1., 1.)] {
            let g = FrequencyGrid::new(lo, hi, 64).unwrap();
            let s = replay_dual_frequency(&r, 4, 8, &g, None, None).unwrap();
            assert!(s.stats.max_number_defect < 2e-12);
            assert!(s.stats.max_material_energy_defect < 2e-12);
            assert!(s.stats.max_projection_energy_defect < 2e-12);
            assert!(s.normal_energy_balance_defect().abs() < 2e-12);
            assert!(s.number_continuity_defect(&r).unwrap().abs() < 2e-12);
            let q = s.history.last().unwrap();
            if lo < -10. {
                assert!((q.energy_centered - oracle.history[1].energy_comoving).abs() < 2e-10);
            } else {
                assert!(q.escaped_number_centered > 1e-4);
            }
        }
    }
}
#[test]
fn line_absorption_emission_uses_actual_node_energy() {
    let g = FrequencyGrid::new(-2., 2., 128).unwrap();
    let r = [rec(0., 0.1, vec![])];
    for source in [0., 1.] {
        let l = line(0.1, 0., 0.1, 0.1, source);
        let s = replay_dual_frequency(&r, 4, 8, &g, Some(&l), None).unwrap();
        assert!(s.stats.max_line_number_defect < 2e-12);
        assert!(s.normal_energy_balance_defect().abs() < 2e-12);
        assert!(
            s.history
                .last()
                .unwrap()
                .line_projection_energy_centered
                .abs()
                < 2e-12
        );
    }
}
#[test]
fn reversible_pair_detailed_balance_and_positive_stiff_relaxation() {
    let a = 0.2f64;
    let b = 0.7f64;
    let (p, q) = reversible_pair_weights(a.ln(), b.ln(), 10., 0.3).unwrap();
    assert!((p * a - q * b).abs() < 1e-15);
    let (p, q) = reversible_pair_weights(a.ln(), b.ln(), 1e6, 1.).unwrap();
    assert!(p >= 0. && q >= 0. && p + q <= 1. + 1e-15);
    assert!((p * a - q * b).abs() < 1e-15);
    assert!(reversible_pair_weights(0., 0., -1., 1.).is_err());
}
#[test]
fn redistribution_has_number_and_bath_energy_ledger() {
    let g = FrequencyGrid::new(-2., 2., 128).unwrap();
    let r = [rec(0., 0.1, vec![])];
    let l = line(0.1, 0., 0.25, 0., 0.);
    let m = Redistribution::new(0.001, 0.15).unwrap();
    let s = replay_dual_frequency(&r, 4, 8, &g, Some(&l), Some(&m)).unwrap();
    assert!(s.stats.redistribution_cells > 0);
    assert!(
        (s.history.last().unwrap().number_centered - s.history[0].number_centered).abs() < 2e-12
    );
    assert!(s.stats.max_redistribution_number_defect < 2e-12);
    assert!(s.redistribution.last().unwrap().material_energy.abs() > 1e-8);
    assert!(s.normal_energy_balance_defect().abs() < 2e-12);
}

#[test]
fn higher_moment_numerical_diffusion_is_measured_not_heat() {
    let g = FrequencyGrid::new(-12., 5., 64).unwrap();
    let rest = [rec(
        0.,
        0.1,
        vec![event(0.2, [0.; 3], CollisionScheme::Sdirk2)],
    )];
    let moving = [rec(
        0.,
        0.1,
        vec![event(0.2, [0.2, -0.1, 0.05], CollisionScheme::Sdirk2)],
    )];
    let a = replay_dual_frequency(&rest, 4, 8, &g, None, None).unwrap();
    let b = replay_dual_frequency(&moving, 4, 8, &g, None, None).unwrap();
    assert_eq!(a.stats.numerical_second_energy_moment, 0.);
    assert!(b.stats.numerical_second_energy_moment > 1e-5);
    assert!(b.stats.max_projection_energy_defect < 2e-12);
    let g = FrequencyGrid::new(-12., 5., 128).unwrap();
    let c = replay_dual_frequency(&moving, 4, 8, &g, None, None).unwrap();
    assert!(c.stats.numerical_second_energy_moment < b.stats.numerical_second_energy_moment);
}
