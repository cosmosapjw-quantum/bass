use bianchi_rustcore::homogeneous_sky::birth_packets::{
    rate_moment_error, BirthPackets, Packet, RateGuard,
};
#[test]
fn nonlinear_guard_refines_curved_rate_groups_and_preserves_support() {
    let mut p = BirthPackets::new(vec![[0., 0., 1.]], vec![1.]).unwrap();
    for i in 0..33 {
        let e = 25. + i as f64 * 0.18;
        p.packets.push(Packet {
            ray: 0,
            energy_ev: e,
            per_h: 1e-4,
            birth_eta: 0.,
            birth_energy_ev: e,
        });
    }
    let g = RateGuard {
        absorber_cm3: [1e-3, 8e-5, 2e-5],
        dt_s: 1e10,
    };
    let mut old = p.clone();
    old.compress(0.25).unwrap();
    assert!(rate_moment_error(&p.packets, &old.packets, g).unwrap() > 1e-4);
    let mut q = p.clone();
    let r = q.compress_rate_checked(0.25, g, 1e-4).unwrap();
    assert!(r.rate_splits > 0 && r.max_rate_relative <= 1e-4);
    assert!(rate_moment_error(&p.packets, &q.packets, g).unwrap() <= 1e-4);
    let (n, u) = p.inventory();
    let (a, b) = q.inventory();
    assert!((n - a).abs() < 3e-14 * n && (u - b).abs() < 3e-14 * u);
    assert!(q
        .packets
        .iter()
        .all(|v| v.per_h >= 0. && p.packets.iter().any(|w| v.energy_ev == w.energy_ev)));
}
