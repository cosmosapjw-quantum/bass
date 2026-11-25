use bianchi_rustcore::homogeneous_sky::birth_packets::{BirthPackets, Packet};
#[test]
fn positive_endpoint_compression_preserves_number_energy_and_threshold_ownership() {
    let mut b = BirthPackets::new(vec![[0., 0., 1.], [0., 0., -1.]], vec![0.5, 0.5]).unwrap();
    for ray in 0..2 {
        for (i, e) in [
            13.65, 13.66, 13.67, 24.58, 24.59, 24.60, 54.41, 54.42, 54.43,
        ]
        .iter()
        .enumerate()
        {
            b.packets.push(Packet {
                ray,
                energy_ev: *e,
                per_h: (i + 1) as f64 * 1e-4,
                birth_eta: i as f64,
                birth_energy_ev: *e,
            });
        }
    }
    let old = b.clone();
    let r = b.compress(0.04).unwrap();
    assert!(r.after < r.before);
    assert!(r.max_number_relative < 2e-14 && r.max_energy_relative < 2e-14);
    for p in &b.packets {
        assert!(p.per_h >= 0.);
        assert!(old
            .packets
            .iter()
            .any(|o| o.ray == p.ray && o.energy_ev == p.energy_ev && o.birth_eta == p.birth_eta));
    }
    for ray in 0..2 {
        for (l, h) in [(13.6, 24.59), (24.59, 54.42), (54.42, 101.)] {
            let f = |x: &BirthPackets| {
                x.packets
                    .iter()
                    .filter(|p| p.ray == ray && p.energy_ev >= l && p.energy_ev < h)
                    .fold([0., 0.], |a, p| {
                        [a[0] + p.per_h, a[1] + p.per_h * p.energy_ev]
                    })
            };
            let a = f(&old);
            let q = f(&b);
            for i in 0..2 {
                assert!((a[i] - q[i]).abs() < 2e-14 * a[i].max(1e-30));
            }
        }
    }
}
#[test]
fn equal_support_and_invalid_input() {
    let mut b = BirthPackets::new(vec![[0., 0., 1.]], vec![1.]).unwrap();
    for n in [1., 2., 3.] {
        b.packets.push(Packet {
            ray: 0,
            energy_ev: 14.,
            per_h: n,
            birth_eta: 0.,
            birth_energy_ev: 14.,
        });
    }
    b.compress(0.01).unwrap();
    assert_eq!(b.packets.len(), 1);
    assert_eq!(b.inventory(), (6., 84.));
    assert!(b.compress(0.).is_err());
    b.packets[0].per_h = -1.;
    assert!(b.compress(0.01).is_err());
    assert_eq!(b.packets[0].per_h, -1.);
}

#[test]
fn same_ray_lrs_stress_is_invariant_under_compression() {
    let mut b = BirthPackets::new(
        vec![[0., 0., 1.], [0., 0., -1.], [1., 0., 0.]],
        vec![0.25, 0.25, 0.5],
    )
    .unwrap();
    for ray in 0..3 {
        for i in 0..5 {
            let e = 20. + i as f64 * 0.01;
            b.packets.push(Packet {
                ray,
                energy_ev: e,
                per_h: 0.01,
                birth_eta: 0.,
                birth_energy_ev: e,
            });
        }
    }
    let old = b.lrs_stress(100.).unwrap();
    b.compress(0.04).unwrap();
    let new = b.lrs_stress(100.).unwrap();
    for (x, y) in [
        (old.rho_j_m3, new.rho_j_m3),
        (old.p_parallel_j_m3, new.p_parallel_j_m3),
        (old.p_perp_j_m3, new.p_perp_j_m3),
    ] {
        assert!((x - y).abs() < 2e-14 * x.abs());
    }
    assert_eq!(new.flux_z_j_m3, 0.);
}
