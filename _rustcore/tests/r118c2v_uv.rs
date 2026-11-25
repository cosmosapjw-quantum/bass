use bianchi_rustcore::kinetic::{
    owned_vlasov::OwnedState,
    uv_feedback::{Gas, UvModel},
};
use nalgebra::Matrix3;
#[test]
fn source_absorption_and_work_balance() {
    let m = UvModel::new(1. / 21., 0.19, 8, 16, 64, 1.).unwrap();
    let mut s = m.empty();
    let a = 1. / 21.;
    let g = |a: f64| OwnedState {
        a,
        h: 60.,
        s: [0.; 5],
        f: Matrix3::identity(),
    };
    let gas = Gas {
        ne_m3: 10.,
        absorbers_m3: [1e5, 1e4, 0.],
    };
    m.advance(&mut s, &g(a), &g(a * 1.0005), &g(a * 1.001), 1e12, gas)
        .unwrap();
    let x = m.moments(&s, &g(a * 1.001)).unwrap();
    assert!(x.0 > 0. && s.emitted > 0. && s.absorbed > 0.);
    assert!((x.0 + s.reservoir + s.work).abs() < 1e-12);
    assert!((x.1.trace() - x.0).abs() < 1e-12);
}
#[test]
fn zero_strength_recovers_existing_owner() {
    use bianchi_rustcore::kinetic::owned_thomson::ThomsonOwner;
    let m = ThomsonOwner::new(0.01, 24, 8, 16, 4, 8, 16).unwrap();
    let uv = UvModel::new(1. / 21., 0.19, 8, 16, 64, 0.).unwrap();
    let s = m.initial(1. / 21., [0.01, 0., 0., 0., 0.]).unwrap();
    let gas = Gas {
        ne_m3: 10.,
        absorbers_m3: [1e5, 1e4, 0.],
    };
    let (x, _) = m.step(&s, 0.001, 10., 10.).unwrap();
    let (y, u, _) = m
        .step_uv(&s, &uv, &uv.empty(), 0.001, gas, gas, gas, true)
        .unwrap();
    assert_eq!(x.geometry.h, y.geometry.h);
    assert_eq!(x.geometry.s, y.geometry.s);
    assert_eq!(x.geometry.f, y.geometry.f);
    assert_eq!(x.sky.coefficients, y.sky.coefficients);
    assert_eq!(u.emitted, 0.);
}
