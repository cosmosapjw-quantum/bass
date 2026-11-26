use bianchi_rustcore::kinetic::{cooling_rays::CoolingRays, owned_vlasov::OwnedState};
use nalgebra::Matrix3;
#[test]
fn spectral_energy_partition() {
    let a = 1. / 21.;
    let c = CoolingRays::new(a, 4, 8).unwrap();
    let edges = [0., 0.001, 0.01, 0.1, f64::INFINITY];
    let g = |a| OwnedState {
        a,
        h: 50.,
        s: [0.; 5],
        f: Matrix3::identity(),
    };
    let s = vec![0.; c.empty().len() * 4];
    let (v, w) = c
        .advance_freefree(&s, &edges, &g(a), &g(2. * a), &g(3. * a), 1., 0.01)
        .unwrap();
    let u = c.spectral_energy(&v, &edges, &g(3. * a)).unwrap();
    assert!((u.iter().sum::<f64>() - 2. / 3.).abs() < 1e-14);
    assert!((u.iter().sum::<f64>() + w - 1.).abs() < 1e-14);
    assert!((u[0] / (2. / 3.) - (-0.05_f64).exp_m1().abs()).abs() < 1e-14);
    assert!(c
        .advance_freefree(&s, &edges, &g(a), &g(a), &g(a), 1., -1.)
        .is_err());
}
