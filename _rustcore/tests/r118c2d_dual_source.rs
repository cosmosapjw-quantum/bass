use bianchi_rustcore::homogeneous_sky::dual_source::{Cell, DualTransport, Reconstruction};
#[test]
fn exponential_recovers_positive_moments_and_subinterval() {
    for r in [
        0.,
        1e-14,
        1e-6,
        0.1,
        0.499999999,
        0.5,
        0.500000001,
        0.9,
        1. - 1e-14,
        1.,
    ] {
        let q = Reconstruction::new(Cell {
            left: 1. - r,
            right: r,
        })
        .unwrap();
        let (n, x) = q.portion(0., 1.).unwrap();
        assert!(
            (n - 1.).abs() < 2e-14 && (x - r).abs() < 2e-14,
            "{r} {n} {x}"
        );
        let (n1, x1) = q.portion(0., 0.4).unwrap();
        let (n2, x2) = q.portion(0.4, 1.).unwrap();
        // No atom placed exactly at the internal split for this set.
        assert!((n1 + n2 - n).abs() < 2e-14 && (x1 + x2 - x).abs() < 2e-14);
    }
}
#[test]
fn signed_live_drift_closes_number_and_centered_energy() {
    let tr = DualTransport::new(vec![-4., -2., 0., 1., 2., 4.], 1e15, 1e11, -2., 2.).unwrap();
    let m = vec![
        Cell {
            left: 0.1,
            right: 0.2,
        },
        Cell {
            left: 0.7,
            right: 0.1,
        },
        Cell {
            left: 0.5,
            right: 0.5,
        },
        Cell {
            left: 0.1,
            right: 0.8,
        },
        Cell {
            left: 0.1,
            right: 0.2,
        },
    ];
    for dz in [-1e-4, 0., 1e-4] {
        let q = tr.shift(&m, dz).unwrap();
        assert!(
            q.number_defect < 2e-14 && q.centered_defect < 2e-14 && q.core_number_defect < 2e-14
        );
        assert!(q.cells.iter().all(|c| c.left >= 0. && c.right >= 0.));
        assert_eq!(q.atom_energy, 0.);
    }
}
#[test]
fn degenerate_node_at_face_has_one_owner() {
    let tr = DualTransport::new(vec![-4., -2., 0., 2., 4.], 1e15, 1e11, -2., 2.).unwrap();
    let m = vec![
        Cell {
            left: 0.,
            right: 1.,
        },
        Cell {
            left: 0.,
            right: 0.,
        },
        Cell {
            left: 0.,
            right: 0.,
        },
        Cell {
            left: 0.,
            right: 0.,
        },
    ];
    let q = tr.shift(&m, 0.).unwrap();
    assert_eq!(q.cells[0].right, 1.);
    let q = tr.shift(&m, 1e-8).unwrap();
    assert!((q.red_in - 1.).abs() < 2e-14);
    assert!(q.number_defect < 2e-14 && q.centered_defect < 2e-14);
}

#[test]
fn centered_event_transfer_tracks_small_physical_signal() {
    use bianchi_rustcore::homogeneous_sky::positive_event::{Block, Graph, Mode};
    let g = Graph::new(
        vec![
            Mode {
                g: 2.,
                pi: 0.2,
                p: 5e-27,
            },
            Mode {
                g: 3.,
                pi: 0.25,
                p: 5.0001e-27,
            },
        ],
        vec![[0., 0., 1.]],
        vec![1.],
        vec![Block {
            i: 0,
            j: 1,
            w: vec![0.05],
        }],
    )
    .unwrap();
    let old = vec![0.4, 0.1];
    let step = g
        .step_with_detuning(&old, &[1.], 0.3, &[-0.5, 0.5])
        .unwrap();
    let delta = 0.5 * (step.mass[1] - old[1]) - 0.5 * (step.mass[0] - old[0]);
    assert!((step.centered_exchange - delta).abs() < 2e-15);
    assert!(step.centered_defect < 2e-14);
}

#[test]
fn separate_core_and_exterior_centered_energy_balance() {
    let tr = DualTransport::new(vec![-4., -2., 0., 1., 2., 4.], 1e15, 1e11, -2., 2.).unwrap();
    let m = vec![
        Cell {
            left: 0.1,
            right: 0.2,
        },
        Cell {
            left: 0.7,
            right: 0.1,
        },
        Cell {
            left: 0.5,
            right: 0.5,
        },
        Cell {
            left: 0.1,
            right: 0.8,
        },
        Cell {
            left: 0.1,
            right: 0.2,
        },
    ];
    for dz in [-1e-3, -1e-4, 0., 1e-4, 1e-3] {
        let q = tr.shift(&m, dz).unwrap();
        assert!(q.core_centered_defect < 3e-14 && q.exterior_centered_defect < 3e-14);
        assert!(q.core_work_x.is_finite() && q.face_x.is_finite());
    }
}
