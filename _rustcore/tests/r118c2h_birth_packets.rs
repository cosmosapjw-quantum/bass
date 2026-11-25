use bianchi_rustcore::{
    homogeneous_sky::birth_packets::{BirthPackets, Packet},
    kinetic::lie_history::RayNode,
};
#[test]
fn transport_retains_birth_energy_support_and_crossing_is_owned_once() {
    let mut p = BirthPackets::new(vec![[0., 0., 1.], [0., 0., -1.]], vec![0.5, 0.5]).unwrap();
    p.packets.push(Packet {
        ray: 0,
        energy_ev: 13.7,
        per_h: 2.,
        birth_eta: 0.,
        birth_energy_ev: 13.7,
    });
    p.packets.push(Packet {
        ray: 1,
        energy_ev: 14.,
        per_h: 3.,
        birth_eta: 0.,
        birth_energy_ev: 14.,
    });
    let a = RayNode::default();
    let mut b = a.clone();
    b.eta = 0.01;
    let m = p.transport(&a, &b).unwrap();
    assert_eq!(p.packets.len(), 1);
    assert_eq!(m.boundary_n, 2.);
    assert!((m.boundary_u - 2. * 13.6).abs() < 1e-12);
    assert!((p.packets[0].energy_ev - 14. * (-0.01_f64).exp()).abs() < 1e-12);
    assert!(
        (m.redshift_work + m.boundary_u + p.inventory().1 - (2. * 13.7 + 3. * 14.)).abs() < 1e-12
    );
    assert!((p.inventory().0 + m.boundary_n - 5.).abs() < 1e-12);
}
#[test]
fn rejects_non_unimodular_and_contracting_geometry() {
    let mut p = BirthPackets::new(vec![[0., 0., 1.]], vec![1.]).unwrap();
    let a = RayNode::default();
    let mut b = a.clone();
    b.eta = 0.01;
    b.a = [0.1, 0., 0.];
    assert!(p.transport(&a, &b).is_err());
    b.a = [0.; 3];
    b.shear = [[1., 0., 0.], [0., 1., 0.], [0., 0., -2.]];
    assert!(p.transport(&a, &b).is_err());
}
