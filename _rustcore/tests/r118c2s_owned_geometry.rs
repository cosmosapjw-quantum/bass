use bianchi_rustcore::kinetic::owned_vlasov::{OwnedModel, OwnedState};
use nalgebra::Matrix3;
#[test]
fn isotropic_and_noncommuting_owner() {
    let m = OwnedModel::new(0.01, 24, 8, 16).unwrap();
    let a = 1. / 21.;
    let s = m.initial(a, [0.; 5]).unwrap();
    assert!(m.constraint(&s).unwrap().abs() < 1e-13);
    let t = m.step(&s, 0.001).unwrap();
    assert!(t.a > s.a && t.h < s.h);
    assert!((t.f.determinant() - 1.).abs() < 1e-13);
    let z = OwnedModel::new(0., 24, 8, 16).unwrap();
    let s = z.initial(a, [0.; 5]).unwrap();
    let t = z.step(&s, 0.01).unwrap();
    assert!((t.f - Matrix3::identity()).norm() < 1e-14);
    assert!(t.s.iter().all(|x| x.abs() < 1e-14));
    let bad = OwnedState { h: -1., ..s };
    assert!(z.step(&bad, 0.01).is_err());
}
