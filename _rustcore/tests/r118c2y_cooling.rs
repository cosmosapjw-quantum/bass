use bianchi_rustcore::kinetic::{cooling_rays::CoolingRays, owned_vlasov::OwnedState};
use nalgebra::Matrix3;
#[test]
fn emission_and_flrw_work() {
    let a = 1. / 21.;
    let r = CoolingRays::new(a, 8, 16).unwrap();
    let s = r.empty();
    let g = |a: f64| OwnedState {
        a,
        h: 50.,
        s: [0.; 5],
        f: Matrix3::identity(),
    };
    let (x, w) = r.advance(&s, &g(a), &g(2. * a), &g(3. * a), 1.).unwrap();
    let (u, p) = r.moments(&x, &g(3. * a)).unwrap();
    assert!((u - 2. / 3.).abs() < 1e-14);
    assert!((u + w - 1.).abs() < 1e-14);
    assert!((p - Matrix3::identity() * u / 3.).norm() < 1e-14);
    assert!(r.advance(&s, &g(a), &g(2. * a), &g(3. * a), -1.).is_err());
    let (y, w2) = r
        .advance(&x, &g(3. * a), &g(4. * a), &g(5. * a), 0.)
        .unwrap();
    assert!((r.moments(&y, &g(5. * a)).unwrap().0 + w2 - u).abs() < 1e-14);
}
