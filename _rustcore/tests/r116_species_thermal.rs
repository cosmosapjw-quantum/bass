use bianchi_rustcore::homogeneous_sky::{
    field::Route,
    ionization::Ionization,
    material::Material,
    solve::{solve_general_species_thermal, Settings, SolveOptions},
    CollisionScheme,
};
use bianchi_rustcore::kinetic::radiation_feedback::{ExpansionEquation, LieUpdate};
use rec_microphysics::species_thermal::ReferenceHistory;
fn reference() -> ReferenceHistory {
    let text=format!("rec_species_reference_v1\nf_he 0.08\nhelium neutral\neta x_hi x_heii x_heiii w_k n_h_m3 h_s tr_k\n0 0.2 0 0 1800 1000000 1e-12 1000\n0.01 0.3 0 0 1700 {} 9.84e-13 {}\n",
        1e6*(-0.03f64).exp(),1000.*(-0.01f64).exp());
    ReferenceHistory::parse(&text).unwrap()
}
#[test]
fn species_opacity_single_owner_no_negative_clipping() {
    let r = reference();
    let ion = Ionization::from_species_reference(&r).unwrap();
    assert!((ion.xe_at(0.005).unwrap() - 0.75).abs() < 1e-15);
    let c = ion
        .cells_with_strict_offset(0., 0.01, 1., 1., -0.1)
        .unwrap();
    let t = c.iter().map(|x| x.0).sum::<f64>();
    let exp = rec_microphysics::thomson_history::C_SIGMA_T_M3_S * 1e6 / 1e-12 * 0.0065;
    assert!((t - exp).abs() < 1e-15);
    assert!(ion
        .cells_with_strict_offset(0., 0.01, 1., 1., -0.71)
        .is_err());
}
#[test]
fn species_thermal_history_is_coupled_to_actual_host_and_clock() {
    let r = reference();
    let cfg = Settings {
        family: "I",
        shear: 0.005,
        duration: 0.01,
        steps: 8,
        nmu: 8,
        nphi: 16,
        active: true,
        recoil: true,
        dust_fraction: 0.8,
        dust_beta: [0.002, 0., 0.],
        collision: CollisionScheme::Sdirk2,
        omega_lambda: 0.,
        lie_update: LieUpdate::Congruence,
    };
    let m = Material::constant(cfg.duration, 0., [0.; 3]).unwrap();
    let sol = solve_general_species_thermal(
        &cfg,
        &m,
        None,
        ExpansionEquation::Raychaudhuri,
        0.157,
        &SolveOptions {
            route: Route::harmonic(4),
            ..Default::default()
        },
        &r,
    )
    .unwrap();
    assert_eq!(sol.thermochemistry.len(), 9);
    for (s, h) in sol.thermochemistry.iter().zip(sol.history.iter()) {
        s.state.validate(r.f_he()).unwrap();
        assert!((s.state.xe() - s.reference.xe() - h.delta_xe).abs() < 1e-15);
        assert!(s.n_h_m3 > 0. && s.expansion_ratio.is_none_or(f64::is_finite));
        assert!(s.diagnostics.thermal_balance_defect_j_per_h.abs() < 1e-27);
    }
    assert!(sol.history.last().unwrap().delta_xe.abs() > 0.);
}
