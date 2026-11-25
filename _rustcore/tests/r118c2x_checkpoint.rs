use bianchi_rustcore::kinetic::owned_thomson::ThomsonOwner;
#[test]
fn harmonic_owner_state_exact() {
    let m = ThomsonOwner::new(0.03, 32, 8, 16, 4, 8, 16).unwrap();
    let s = m.initial(1. / 21., [0.01, 0., 0., 0., 0.0075]).unwrap();
    let (s, _) = m.step(&s, 1e-4, 10., 10.).unwrap();
    let q = m.state_text(&s).unwrap();
    let r = m.restore_state_text(&q).unwrap();
    assert_eq!(q, m.state_text(&r).unwrap());
    let (a, _) = m.step(&s, 1e-4, 10., 10.).unwrap();
    let (b, _) = m.step(&r, 1e-4, 10., 10.).unwrap();
    assert_eq!(m.state_text(&a).unwrap(), m.state_text(&b).unwrap());
}
