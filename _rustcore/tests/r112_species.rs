use bianchi_rustcore::kinetic::tilted_dust::Dust;
#[test]
fn unequal_mass_counterflow() {
    let f = 0.157;
    let d = Dust::opposed_species(0.8, f, [0.3, -0.2, 0.1]).unwrap();
    let a = d.beam(0).unwrap();
    let b = d.beam(1).unwrap();
    assert!(
        (a.normal_mass_density / (a.normal_mass_density + b.normal_mass_density) - f).abs() < 1e-14
    );
    let m = d.moments().unwrap();
    assert!((m.energy - 0.8).abs() < 1e-14);
    assert!(m.flux.iter().all(|v| v.abs() < 1e-14));
    assert!((a.beta[0] - 0.3).abs() < 1e-14);
    let mut kicked = d.clone();
    kicked.kick(0, [0.001, 0., 0.]).unwrap();
    assert_eq!(kicked.beam(1).unwrap().momentum_density, b.momentum_density);
    assert_eq!(
        kicked.beam(0).unwrap().normal_mass_density,
        a.normal_mass_density
    );
}
#[test]
fn coflow_and_invalid() {
    let d = Dust::coflow_species(0.8, 0.157, [0.2, 0., 0.]).unwrap();
    assert!((d.moments().unwrap().flux[0] - 0.16).abs() < 1e-14);
    assert!((d.beam(0).unwrap().energy / 0.8 - 0.157).abs() < 1e-14);
    for f in [0., 1., f64::NAN] {
        assert!(Dust::opposed_species(1., f, [0.; 3]).is_err());
    }
    let old = Dust::opposed(0.8, [0.2, 0., 0.]).unwrap();
    let new = Dust::opposed_species(0.8, 0.5, [0.2, 0., 0.]).unwrap();
    assert_eq!(
        old.moments().unwrap().energy.to_bits(),
        new.moments().unwrap().energy.to_bits()
    );
}
