use bianchi_rustcore::homogeneous_sky::resonance::{
    bose_pair_be, voigt_h, AtomicLine, Material, Patch,
};
#[test]
fn source_atomic_normalization_and_voigt() {
    let h = AtomicLine::hydrogen();
    let he = AtomicLine::helium();
    assert!((h.nu0() / 2.4660677e15 - 1.).abs() < 2e-7);
    assert!((he.oscillator_strength() - 0.27625).abs() < 2e-5);
    assert!((voigt_h(0.001, 0.).unwrap() - 0.9988726200811514).abs() < 3e-10);
    assert!((voigt_h(0.001, 10.).unwrap() - 5.728717502841746e-6).abs() < 3e-12);
    let m = Material::new(3000., 250e6, 1., 1.).unwrap();
    let c = h.calibrate(m).unwrap();
    assert!(c.doppler_fraction > 2e-5 && c.doppler_fraction < 3e-5);
    assert!(c.sigma_integral_m2_hz > 1e-6 && c.sigma_integral_m2_hz < 2e-6);
    assert!(c.peak_scattering_s > 0.5 && c.peak_scattering_s < 2.);
}
#[test]
fn stiff_linear_patch_conserves_and_keeps_wien_null() {
    let m = Material::new(3000., 250e6, 1., 1.).unwrap();
    let p = Patch::new(AtomicLine::hydrogen(), m, 12., 128).unwrap();
    let w = p.wien(1e-3).unwrap();
    let y = p.be_step(&w, 1e10).unwrap();
    let e = y.iter().zip(&w).map(|(a, b)| (a - b).abs()).sum::<f64>() / w.iter().sum::<f64>();
    assert!(e < 1e-10, "Wien error {e}");
    let mut pulse = vec![0.; w.len()];
    pulse[64] = 1.;
    let y = p.be_step(&pulse, 1e10).unwrap();
    assert!(y.iter().all(|x| *x >= 0.));
    assert!((y.iter().sum::<f64>() - 1.).abs() < 1e-10);
    let delta = p.energy_change_j(&pulse, &y).unwrap();
    assert!(delta.is_finite());
}
#[test]
fn bose_pair_null_and_number_conservation() {
    let v0 = 0.1;
    let v1 = 0.2;
    let eps0: f64 = 0.2;
    let eps1: f64 = 0.4;
    let a = 3.;
    let b = a * v0 / v1 * (eps1 - eps0).exp();
    let l = v0 / eps0.exp_m1();
    let r = v1 / eps1.exp_m1();
    let (x, y) = bose_pair_be(l, r, v0, v1, a, b, 1e6).unwrap();
    assert!((x - l).abs() + (y - r).abs() < 1e-11);
    let (x, y) = bose_pair_be(1., 0., v0, v1, a, b, 1e6).unwrap();
    assert!(x >= 0. && y >= 0. && (x + y - 1.).abs() < 1e-15);
}

#[test]
fn positive_dipole_moment_corrects_core_not_wing() {
    use bianchi_rustcore::homogeneous_sky::resonance::{voigt_dipole_moment, DiffusionProfile};
    let a = 0.0008614435022174598;
    let ratio = voigt_dipole_moment(a, 0.).unwrap() / voigt_h(a, 0.).unwrap();
    assert!(ratio > 0.300 && ratio < 0.302);
    let wing = voigt_dipole_moment(a, 100.).unwrap() / voigt_h(a, 100.).unwrap();
    assert!((wing - 1.).abs() < 0.001);
    let p = Patch::with_profile(
        AtomicLine::hydrogen(),
        Material::new(3000., 250e6, 1., 1.).unwrap(),
        40.,
        128,
        true,
        DiffusionProfile::DipoleMoment,
    )
    .unwrap();
    let w = p.wien(1e-4).unwrap();
    assert!(p.be_audit(&w, 1e10).unwrap().continuity_l1 < 1e-10);
}
#[test]
fn scalar_bose_chain_keeps_planck_and_preserves_number() {
    use bianchi_rustcore::homogeneous_sky::resonance::DiffusionProfile;
    let p = Patch::with_profile(
        AtomicLine::hydrogen(),
        Material::new(3000., 250e6, 1., 1.).unwrap(),
        12.,
        128,
        false,
        DiffusionProfile::DipoleMoment,
    )
    .unwrap();
    let eps0 = 6.62607015e-34 * p.calibration.nu0_hz / (1.380649e-23 * p.material.temperature_k);
    let eq = p.bose(eps0 - 3.).unwrap();
    let s = p.bose_step(&eq, 1e5).unwrap();
    let norm = eq.iter().sum::<f64>();
    assert!(
        s.step
            .mass
            .iter()
            .zip(&eq)
            .map(|(a, b)| (a - b).abs())
            .sum::<f64>()
            / norm
            < 1e-10
    );
    let pulse: Vec<_> =
        p.x.iter()
            .zip(&p.volume)
            .map(|(x, w)| w * 0.01 * (-0.5 * (x - 2.).powi(2)).exp())
            .collect();
    let s = p.bose_step(&pulse, 1e4).unwrap();
    assert!(s.step.number_defect < 1e-11 && s.step.mass.iter().all(|x| *x >= 0.));
    assert!(s.nonlinear_scaled_residual < 1e-11);
}

#[test]
fn signed_frequency_drift_remap_conserves_number_and_scaled_energy() {
    let p = Patch::new(
        AtomicLine::hydrogen(),
        Material::new(3000., 250e6, 1., 1.).unwrap(),
        12.,
        128,
    )
    .unwrap();
    let mut m = vec![0.; p.x.len()];
    m[64] = 1.;
    let a = p
        .shift_log(&m, 4. * p.calibration.doppler_fraction)
        .unwrap();
    let b = p
        .shift_log(&a.mass, -4. * p.calibration.doppler_fraction)
        .unwrap();
    assert!(a.number_defect < 2e-13 && b.number_defect < 2e-13);
    assert!(a.energy_defect < 2e-13 && b.energy_defect < 2e-13);
    assert_eq!(a.escaped_mass, 0.);
    assert_eq!(b.escaped_mass, 0.);
    assert!((b.mass.iter().sum::<f64>() - 1.).abs() < 2e-13);
    let out = p
        .shift_log(&m, 40. * p.calibration.doppler_fraction)
        .unwrap();
    assert!(
        (out.escaped_mass - 1.).abs() < 2e-13
            && out.number_defect < 2e-13
            && out.energy_defect < 2e-13
    );
}
