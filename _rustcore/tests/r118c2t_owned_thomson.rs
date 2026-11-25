use bianchi_rustcore::kinetic::owned_thomson::ThomsonOwner;
#[test]
fn isotropic_no_duplicate_photons() {
    let m = ThomsonOwner::new(0., 24, 8, 16, 4, 8, 16).unwrap();
    let s = m.initial(1. / 21., [0.; 5]).unwrap();
    let r = m.matter(&s).unwrap();
    assert!((r.photon_rho * (1. / 21_f64).powi(4) / 5.4437488671046486e-5 - 1.).abs() < 1e-13);
    assert!(m.constraint(&s).unwrap().abs() < 1e-13);
    let (t, err) = m.step(&s, 0.001, 100., 100.).unwrap();
    assert!(err < 1e-12 && t.geometry.h < s.geometry.h);
    assert!(t.geometry.s.iter().all(|x| x.abs() < 1e-12));
}
