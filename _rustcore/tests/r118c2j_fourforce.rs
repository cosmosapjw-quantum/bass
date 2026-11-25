use bianchi_rustcore::{
    homogeneous_sky::birth_packets::{BirthPackets, Packet},
    kinetic::lie_history::RayNode,
};
#[test]
fn axial_threshold_crossing_uses_actual_direction() {
    let mut p = BirthPackets::new(vec![[0.8, 0., 0.6]], vec![1.]).unwrap();
    p.packets.push(Packet {
        ray: 0,
        energy_ev: 13.7,
        per_h: 2.,
        birth_eta: 0.,
        birth_energy_ev: 13.7,
    });
    let mut a = RayNode::default();
    a.shear = [[-0.1, 0., 0.], [0., -0.1, 0.], [0., 0., 0.2]];
    let mut b = a.clone();
    b.eta = 0.1;
    let r = p.transport(&a, &b).unwrap();
    assert_eq!(p.packets.len(), 0);
    let mut lo = 0.;
    let mut hi = 0.1;
    for _ in 0..60 {
        let t = (lo + hi) * 0.5_f64;
        let e = 13.7 * (0.64 * (-1.8_f64 * t).exp() + 0.36 * (-2.4_f64 * t).exp()).sqrt();
        if e > 13.6 {
            lo = t
        } else {
            hi = t
        }
    }
    let t = (lo + hi) * 0.5;
    let want = 2. * 13.7 * 0.6 * (-1.2 * t).exp();
    assert!((r.boundary_pz - want).abs() < 1e-11);
    assert!((r.boundary_pz + r.redshift_pz - 2. * 13.7 * 0.6).abs() < 1e-12);
}
#[test]
fn absorption_energy_species_and_momentum_from_actual_survivors() {
    use bianchi_rustcore::homogeneous_sky::rei_live::absorption_budget;
    use rei_microphysics::{igm_state::IgmGasState, Absorber, AtomicProvider, HHeModel};
    let mut p = BirthPackets::new(vec![[0., 0., 1.]], vec![1.]).unwrap();
    p.packets.push(Packet {
        ray: 0,
        energy_ev: 30.,
        per_h: 0.01,
        birth_eta: 0.,
        birth_energy_ev: 30.,
    });
    let nh = 1e-3;
    let fhe = 0.08;
    let g = IgmGasState::from_temperature([0.1, 0.2, 0.], nh, nh * fhe, 1000.).unwrap();
    let c = HHeModel::controlled_fixture();
    let pr = AtomicProvider::reference();
    let lam = c.c_cm_s
        * (nh * 0.9 * pr.cross_section(Absorber::HI, 30.).unwrap()
            + nh * fhe * 0.8 * pr.cross_section(Absorber::HeI, 30.).unwrap());
    let dt = 1e9;
    let n = 0.01 / (1. + dt * lam);
    let a = absorption_budget(&p, &[n], g, nh, fhe, dt, false).unwrap();
    assert!((a.energy - 30. * (0.01 - n)).abs() < 1e-14);
    assert_eq!(a.pz, a.energy);
    assert!((a.binding + a.heat - a.energy).abs() < 1e-14);
    assert!(a.events[0] > 0. && a.events[1] > 0. && a.events[2] == 0.);
    assert_eq!(
        absorption_budget(&p, &[n], g, nh, fhe, dt, true)
            .unwrap()
            .pz,
        0.
    );
}
