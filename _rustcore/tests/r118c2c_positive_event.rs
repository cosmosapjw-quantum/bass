use bianchi_rustcore::homogeneous_sky::positive_event::{
    pair_exact, Block, Graph, Mode, Transport,
};
#[test]
fn exact_pair_positivity_number_and_semigroup() {
    for dt in [1e-9, 0.1, 1., 1e5] {
        let a = pair_exact(1., 0., 2., 3., 0.1, 0.2, 0.05, dt).unwrap();
        assert!(a.0 >= 0. && a.1 >= 0. && (a.0 + a.1 - 1.).abs() < 2e-15);
        let b = pair_exact(1., 0., 2., 3., 0.1, 0.2, 0.05, dt / 2.).unwrap();
        let c = pair_exact(b.0, b.1, 2., 3., 0.1, 0.2, 0.05, dt / 2.).unwrap();
        assert!((a.0 - c.0).abs() + (a.1 - c.1).abs() < 2e-13);
    }
    let x = 2. * 0.1 / (1. - 0.1);
    let y = 3. * 0.2 / (1. - 0.2);
    let a = pair_exact(x, y, 2., 3., 0.1, 0.2, 0.05, 1e9).unwrap();
    assert!((a.0 - x).abs() + (a.1 - y).abs() < 2e-15);
}
fn graph() -> Graph {
    Graph::new(
        vec![
            Mode {
                g: 2.,
                pi: 0.2,
                p: 5e-27,
            },
            Mode {
                g: 3.,
                pi: 0.3,
                p: 6e-27,
            },
        ],
        vec![[0., 0., 1.], [0., 0., -1.]],
        vec![0.5, 0.5],
        vec![
            Block {
                i: 0,
                j: 1,
                w: vec![0.1, 0.2, 0.2, 0.1],
            },
            Block {
                i: 0,
                j: 0,
                w: vec![0., 0.1, 0.1, 0.],
            },
        ],
    )
    .unwrap()
}
#[test]
fn graph_quasipositive_action_and_clock_weighted_step() {
    let g = graph();
    let c = [0.7, 1.3];
    let f = [0., 0., 0.5, 0.];
    let m = g.to_mass(&f, &c).unwrap();
    let a = g.action(&m, &c).unwrap();
    assert!(a.rate[0] > 0. && a.rate[1] > 0. && a.rate[3] >= 0.);
    let s = g.step(&m, &c, 0.7).unwrap();
    assert!(s.mass.iter().all(|x| *x >= 0.));
    assert!(s.number_defect < 2e-14 && s.force_defect < 2e-14);
}
#[test]
fn conditional_live_boundary_exchange_conserves() {
    let x = Transport::new(vec![-1., 0., 1., 2., 3.], 1e15, 1e11, 0., 2.).unwrap();
    let a = x.shift(&[0., 1., 1., 0.], -0.3e-4).unwrap();
    assert!(a.red_out > 0. && a.blue_in == 0.);
    let b = x.shift(&a.mass, 0.3e-4).unwrap();
    assert!(b.red_in > 0. && b.blue_out > 0.);
    assert!(a.number_defect < 2e-14 && b.number_defect < 2e-14);
    assert!(a.energy_defect < 2e-14 && b.energy_defect < 2e-14);
    assert_eq!(a.atom_energy, 0.);
}

#[test]
fn face_transfer_and_zone_projection_are_independently_resolved() {
    let tr = Transport::new(vec![-4., -2., 0., 1., 2., 4.], 1e15, 1e11, -2., 2.).unwrap();
    for dz in [-1e-4, 0., 1e-4] {
        let q = tr.shift(&[0.2, 0.7, 1., 0.5, 2.], dz).unwrap();
        assert!(q.core_number_defect < 2e-14);
        assert!(q.exterior_number_defect < 2e-14);
        assert!((q.projection_core + q.projection_exterior - q.projection).abs() < 1e-32);
    }
}
