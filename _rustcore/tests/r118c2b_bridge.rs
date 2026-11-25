use bianchi_rustcore::homogeneous_sky::rec_angular::{
    frame_map, Bridge, Direction, Grid, Network, Packet, Scope, Side, State,
};
use bianchi_rustcore::kinetic::lie_history::RayNode;
use nalgebra::DMatrix;
fn bridge() -> Bridge {
    let states = vec![
        State {
            label: "FR00".into(),
            lo: -21.25,
            hi: -16.25,
            g: 2.,
            pi: 0.8,
            p: 1e-27,
        },
        State {
            label: "FB02".into(),
            lo: 16.25,
            hi: 21.25,
            g: 3.,
            pi: 0.9,
            p: 1.1e-27,
        },
    ];
    let network = Network::new(
        states,
        1,
        vec![0., 0.6, 0.6, 0., 0., 0.1, 0.1, 0.],
        vec![0., 0., -0.1, -0.2],
    )
    .unwrap();
    let grid = Grid::new(
        vec![
            [1., 0., 0.],
            [-1., 0., 0.],
            [0., 1., 0.],
            [0., -1., 0.],
            [0., 0., 1.],
            [0., 0., -1.],
        ],
        vec![1. / 6.; 6],
        1,
    )
    .unwrap();
    Bridge::new(network, grid).unwrap()
}
#[test]
fn source_bose_action_jvp_and_equilibrium() {
    let b = bridge();
    let f = DMatrix::from_fn(6, 2, |i, j| 0.1 + 0.03 * i as f64 + 0.08 * j as f64);
    let a = b.action(&f, Scope::Full).unwrap();
    assert!(a.number_residual.abs() < 1e-14);
    let v = f.map(|x| 0.2 * x);
    let j = b.jvp(&f, &v, Scope::Full).unwrap();
    let eps = 1e-5;
    let fd = (b.action(&(&f + eps * &v), Scope::Full).unwrap().occupation
        - b.action(&(&f - eps * &v), Scope::Full).unwrap().occupation)
        / (2. * eps);
    assert!((j - fd).amax() < 1e-10);
    let f = b.equilibrium(0.2).unwrap();
    assert!(b.action(&f, Scope::Full).unwrap().occupation.amax() < 1e-14);
}
#[test]
fn native_be_number_and_frame_ledger() {
    let b = bridge();
    let f = DMatrix::from_fn(6, 2, |i, j| 0.1 + 0.03 * i as f64 + 0.08 * j as f64);
    let m = frame_map(&b.grid, &RayNode::default(), [0.3, 0.1, 0.], [0.; 3], 1e-13).unwrap();
    let a = b.action(&f, Scope::Full).unwrap();
    let q = b.normal_ledger(&a, &m).unwrap();
    assert!(q.number_per_eta.abs() < 0.1);
    assert!(q.force_relative_defect < 2e-14);
    let s = b
        .implicit(&f, 0.5, &vec![1.; 6], &DMatrix::zeros(6, 2))
        .unwrap();
    assert!(s.residual < 1e-11 && s.occupation.min() > 0.);
    assert!(
        (b.photon_number(&s.occupation, &vec![1.; 6]).unwrap()
            - b.photon_number(&f, &vec![1.; 6]).unwrap())
        .abs()
            < 1e-12
    );
}
#[test]
fn packet_face_energy_is_not_atom_heat() {
    let b = bridge();
    let p = Packet {
        side: Side::Blue,
        direction: Direction::IntoCom,
        frequency_hz: 5e14,
        number_per_h: 1e-4,
        energy_j_per_h: 6.62607015e-34 * 5e14 * 1e-4,
    };
    let (inc, l) = b.packet(&p, 2.).unwrap();
    assert!(inc.column(0).amax() == 0.);
    assert!((inc[(0, 1)] - 2e-4 / 3.).abs() < 1e-18);
    assert_eq!(l.atom_energy_j_per_h, 0.);
    assert_eq!(l.native_number_per_h + l.com_number_per_h, 0.);
    assert_eq!(l.native_energy_j_per_h + l.com_energy_j_per_h, 0.);
    assert!((l.centroid_proxy_j_per_h + l.unresolved_j_per_h - l.com_energy_j_per_h).abs() < 1e-36);
}

#[test]
fn collisionless_planck_sampler_rejects_scattered_history() {
    use bianchi_rustcore::homogeneous_sky::{
        rec_angular::sample_collisionless_planck, replay::StepRecord, CollisionEvent,
        CollisionScheme,
    };
    let b = bridge();
    let r = StepRecord {
        left: RayNode::default(),
        right: RayNode {
            eta: 0.1,
            ..Default::default()
        },
        first: vec![],
        second: vec![],
    };
    let m = frame_map(&b.grid, &r.right, [0.; 3], [0.; 3], 1e-13).unwrap();
    let s = sample_collisionless_planck(
        &b.network,
        &m,
        &[r.clone()],
        3000. * 0.1f64.exp(),
        2.466e15,
        5.8e10,
    )
    .unwrap();
    assert!(s
        .temperature_h
        .iter()
        .all(|t| (*t / 3000. - 1.).abs() < 1e-12));
    assert!(s.occupation.min() > 0.);
    let mut r = r;
    r.first.push(CollisionEvent {
        depth: 0.1,
        beta: [0.; 3],
        gain_map: None,
        scheme: CollisionScheme::BackwardEuler,
        sources: vec![],
    });
    assert!(sample_collisionless_planck(&b.network, &m, &[r], 3000., 2.466e15, 5.8e10).is_err());
}
