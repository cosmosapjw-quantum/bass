use bianchi_rustcore::homogeneous_sky::{
    frequency::dual::replay_temperature_mixture, replay::StepRecord, spectral::replay_rays,
    CollisionEvent, CollisionScheme,
};
use bianchi_rustcore::kinetic::lie_history::RayNode;
fn rec(depth: f64, beta: [f64; 3]) -> StepRecord {
    StepRecord {
        left: RayNode::default(),
        right: RayNode {
            eta: 0.1,
            ..Default::default()
        },
        first: vec![CollisionEvent {
            depth,
            beta,
            gain_map: None,
            scheme: CollisionScheme::Sdirk2,
            sources: vec![],
        }],
        second: vec![],
    }
}
#[test]
fn temperature_measure_collisionless_exact_planck_and_derivative() {
    let h = [rec(0., [0.; 3])];
    let s = replay_temperature_mixture(&h, 4, 8, 128, 1.).unwrap();
    for q in s.samples([0.; 3]).unwrap() {
        let y = 10. * 0.1f64.exp();
        let (f, slope) = q.evaluate(10.).unwrap();
        assert!((f * y.exp_m1() - 1.).abs() < 2e-13);
        assert!((slope / (-y * f * (1. + f)) - 1.).abs() < 2e-13);
    }
}
#[test]
fn temperature_measure_tilt_matches_mellin_and_stays_positive() {
    let h = [rec(0.15, [0.2, -0.1, 0.05])];
    let s = replay_temperature_mixture(&h, 4, 8, 256, 2.).unwrap();
    let m = replay_rays(&h, 4, 8).unwrap().samples().unwrap();
    for (q, r) in s.samples([0.; 3]).unwrap().iter().zip(m) {
        assert!(q.components.iter().all(|v| v.weight >= -1e-15));
        let b = q.moments(0.1);
        assert!((b.0 / r.b3 - 1.).abs() < 2e-11 && (b.1 / r.b4 - 1.).abs() < 2e-11);
    }
    assert!(s.escape_number < 2e-11);
}

#[test]
fn sparse_temperature_tail_bound_is_explicit() {
    let mut records = Vec::new();
    for i in 0..32 {
        let mut r = rec(0.2, [0.0001, 0.00003, 0.]);
        r.left.eta = i as f64 / 1024.;
        r.right.eta = (i + 1) as f64 / 1024.;
        records.push(r);
    }
    let s = replay_temperature_mixture(&records, 4, 8, 128, 0.25).unwrap();
    assert!(s.discarded_tail_number_bound < 1e-270);
    assert!(s.discarded_tail_energy_bound < 1e-270);
    assert!(s
        .samples([0.; 3])
        .unwrap()
        .iter()
        .all(|q| q.components.iter().all(|c| c.weight >= 0.)));
}
