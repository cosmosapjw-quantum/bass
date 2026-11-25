use bianchi_rustcore::homogeneous_sky::{
    field::Route,
    material::Material,
    solve::{solve_general_species_sdirk, Settings, SolveOptions},
    CollisionScheme,
};
use bianchi_rustcore::kinetic::radiation_feedback::{ExpansionEquation, LieUpdate};
use rec_microphysics::species_thermal::{ReferenceHistory, SDIRK_GAMMA};
use rec_microphysics::thomson_history::C_SIGMA_T_M3_S;
fn reference() -> ReferenceHistory {
    let txt=format!("rec_species_reference_v1\nf_he 0.08\nhelium neutral\neta x_hi x_heii x_heiii w_k n_h_m3 h_s tr_k\n0 0.2 0 0 1800 1000000 1e-12 1000\n0.01 0.3 0 0 1700 {} 9.84e-13 {}\n",
        1e6*(-0.03f64).exp(),1000.*(-0.01f64).exp());
    ReferenceHistory::parse(&txt).unwrap()
}
#[test]
fn accepted_opacity_stage_is_owned_by_its_actual_charge_density_and_clock() {
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
    let opts = SolveOptions {
        route: Route::harmonic(4),
        ..Default::default()
    };
    let sol = solve_general_species_sdirk(
        &cfg,
        &m,
        None,
        ExpansionEquation::Raychaudhuri,
        0.157,
        &opts,
        &r,
    )
    .unwrap();
    assert_eq!(sol.coupled_stages.len(), 16);
    assert_eq!(sol.records.len(), 16);
    assert_eq!(sol.thermochemistry.len(), 9);
    let h = cfg.duration / cfg.steps as f64;
    for (j, (pair, rec)) in sol
        .coupled_stages
        .chunks_exact(2)
        .zip(sol.records.chunks_exact(2))
        .enumerate()
    {
        for (i, (s, q)) in pair.iter().zip(rec).enumerate() {
            assert_eq!(s.stage, i + 1);
            assert!((s.eta - (j as f64 + if i == 0 { SDIRK_GAMMA } else { 1. }) * h).abs() < 1e-15);
            let k = C_SIGMA_T_M3_S * s.n_h_m3 * s.xe / s.h_s;
            assert!((s.rate_used - k).abs() < 1e-12 * k.abs().max(1e-30));
            assert!(s.relative_residual < 1e-12);
            assert!(
                (s.depth - (s.eta - q.left.eta) * 0.5 * (s.rate_left + s.rate_used)).abs() < 1e-13
            );
            assert!(
                (q.first
                    .iter()
                    .chain(q.second.iter())
                    .map(|e| e.depth)
                    .sum::<f64>()
                    - s.depth)
                    .abs()
                    < 1e-13
            );
        }
        assert!((pair[0].rate_used - pair[1].rate_left).abs() < 1e-12 * pair[0].rate_used);
    }
    assert!(sol.history.last().unwrap().delta_xe.abs() > 0.);
    assert!(sol
        .thermochemistry
        .iter()
        .all(|s| s.diagnostics.thermal_balance_defect_j_per_h.abs() < 1e-27));
}

#[test]
fn nonuniform_macro_clock_has_exact_stage_ownership() {
    use bianchi_rustcore::homogeneous_sky::solve::solve_general_species_sdirk_on_grid;
    let r = reference();
    let cfg = Settings {
        family: "I",
        shear: 0.002,
        duration: 0.01,
        steps: 4,
        nmu: 8,
        nphi: 16,
        active: true,
        recoil: true,
        dust_fraction: 0.8,
        dust_beta: [0.001, 0., 0.],
        collision: CollisionScheme::Sdirk2,
        omega_lambda: 0.,
        lie_update: LieUpdate::Congruence,
    };
    let m = Material::constant(cfg.duration, 0., [0.; 3]).unwrap();
    let opts = SolveOptions {
        route: Route::harmonic(4),
        ..Default::default()
    };
    let edges = [0., 0.001, 0.004, 0.007, 0.01];
    let run = |e: &[f64]| {
        solve_general_species_sdirk_on_grid(
            &cfg,
            &m,
            None,
            ExpansionEquation::Raychaudhuri,
            0.157,
            &opts,
            &r,
            e,
        )
    };
    let sol = run(&edges).unwrap();
    for (i, st) in sol.coupled_stages.chunks_exact(2).enumerate() {
        assert_eq!(
            st[0].eta,
            edges[i] + SDIRK_GAMMA * (edges[i + 1] - edges[i])
        );
        assert_eq!(st[1].eta, edges[i + 1]);
        assert_eq!(sol.history[i + 1].node.eta, edges[i + 1]);
    }
    assert!(run(&[0., 0.001, 0.001, 0.007, 0.01]).is_err());
    assert!(run(&[0., 0.001, 0.004, 0.007, 0.009]).is_err());
}
