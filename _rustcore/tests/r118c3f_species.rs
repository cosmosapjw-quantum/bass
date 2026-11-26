use bianchi_rustcore::kinetic::{owned_thomson::ThomsonOwner, owned_vlasov::OwnedModel};
#[test]
fn independent_species_identity_and_equivalence() {
    let specs = [
        (0.001, 0.5, [0., 0.02, 0., 0., 0.]),
        (0.05, 0.5, [0., 0., 0.012, 0.016, 0.]),
    ];
    let a = OwnedModel::new(0.02, 32, 8, 16).unwrap();
    let b = OwnedModel::with_species(&specs, 32, 8, 16).unwrap();
    let x = a.initial(1. / 21., [0.01, 0., 0., 0., 0.]).unwrap();
    let y = b.initial(x.a, x.s).unwrap();
    assert!((x.h / y.h - 1.).abs() < 1e-14);
    assert!(
        (a.matter(x.a, &x.f).unwrap().pressure - b.matter(y.a, &y.f).unwrap().pressure).norm()
            < 1e-12
    );
    assert!(OwnedModel::with_species(&[(0.01, 0.8, [0.; 5])], 32, 8, 16).is_err());
    let m = ThomsonOwner::with_species(&specs, 32, 8, 16, 4, 8, 16).unwrap();
    let s = m.initial(x.a, x.s).unwrap();
    assert!(m.constraint(&s).unwrap().abs() < 1e-14);
    let t = m.state_text(&s).unwrap();
    assert!(ThomsonOwner::new(0.02, 32, 8, 16, 4, 8, 16)
        .unwrap()
        .restore_state_text(&t)
        .is_err());
    assert!(m.restore_state_text(&t).is_ok());
}
