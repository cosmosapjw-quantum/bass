//! R113 V12-V13 (BASS side): matched implicit hydrogen recombination coupled to
//! the transported sky (THEORY D9, REC `matched_history`).
use bianchi_rustcore::homogeneous_sky::{
    field::Route,
    ionization::Ionization,
    material::Material,
    solve::{solve_general, MatchedRecombination, Settings, Solution, SolveOptions},
    CollisionScheme,
};
use bianchi_rustcore::kinetic::radiation_feedback::{ExpansionEquation, LieUpdate};
use std::path::Path;

const N_H: f64 = 253202790.82151973;
const H_EMIT: f64 = 5.148602492099132e-14;
const T_UNIT: f64 = 2.72548 * 1101.0;
const MATTER: f64 = 0.7554963357761493;

fn table() -> Ionization {
    let path = Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("../research/r109_native_sky/hyrec_1100/hyrec_xe.tsv");
    Ionization::load(&path, N_H, H_EMIT).unwrap()
}

fn settings(family: &str, shear: f64, steps: usize, beta: [f64; 3]) -> Settings<'_> {
    Settings {
        family,
        shear,
        duration: 0.2,
        steps,
        nmu: 10,
        nphi: 24,
        active: true,
        recoil: true,
        dust_fraction: MATTER,
        dust_beta: beta,
        collision: CollisionScheme::BackwardEuler,
        omega_lambda: 0.,
        lie_update: LieUpdate::Additive,
    }
}

fn run(cfg: &Settings, route: Route, matched: bool) -> Result<Solution, String> {
    let ion = table();
    let mat = Material::constant(cfg.duration, 0., [0.; 3])?;
    let opts = SolveOptions {
        route,
        neutrino_fraction: 0.,
        recombination: matched.then_some(MatchedRecombination {
            t_unit_k: T_UNIT,
            n_h_emit_m3: N_H,
            h_emit_s: H_EMIT,
            stop_eta: None,
        }),
    };
    solve_general(
        cfg,
        &mat,
        None,
        Some(&ion),
        ExpansionEquation::Raychaudhuri,
        0.157,
        &opts,
    )
}

fn final_offset(sol: &Solution) -> f64 {
    sol.history.last().unwrap().delta_xe
}

/// FLRW: the matched offset vanishes with the background discretization error
/// (second order in d_eta), and the coupling is a no-op on the Thomson history
/// up to that offset.
#[test]
fn flrw_offset_vanishes_at_the_background_order() {
    let offsets: Vec<f64> = [24, 48, 96]
        .iter()
        .map(|&n| final_offset(&run(&settings("FLRW", 0., n, [0.; 3]), Route::Rays, true).unwrap()))
        .collect();
    println!("V12 FLRW offsets {offsets:?}");
    assert!(offsets[2].abs() < 1e-10);
    for pair in offsets.windows(2) {
        let ratio = pair[0] / pair[1];
        assert!((3.5..4.5).contains(&ratio), "order ratio {ratio}");
    }
    let off = run(&settings("FLRW", 0., 48, [0.; 3]), Route::Rays, false).unwrap();
    let on = run(&settings("FLRW", 0., 48, [0.; 3]), Route::Rays, true).unwrap();
    let (a, b) = (
        off.history.last().unwrap().proper_depth,
        on.history.last().unwrap().proper_depth,
    );
    assert!(off.history.iter().all(|s| s.delta_xe == 0.));
    assert!(((a - b) / a).abs() < 1e-8, "{a} vs {b}");
}

/// Anisotropic tilted Bianchi I: a finite positive response, converged in d_eta,
/// and the same on the ray and spin-harmonic routes.
#[test]
fn bianchi_response_is_converged_and_route_independent() {
    let beta = [1e-3, 0., 0.];
    let coarse = final_offset(&run(&settings("I", 0.01, 24, beta), Route::Rays, true).unwrap());
    let rays = final_offset(&run(&settings("I", 0.01, 48, beta), Route::Rays, true).unwrap());
    let harmonic =
        final_offset(&run(&settings("I", 0.01, 48, beta), Route::harmonic(8), true).unwrap());
    println!("V13 Bianchi I offsets coarse {coarse:e} rays {rays:e} harmonic {harmonic:e}");
    assert!(rays > 0. && rays.is_finite());
    assert!(((coarse - rays) / rays).abs() < 0.03);
    assert!(((harmonic - rays) / rays).abs() < 0.03);
}

#[test]
fn matched_recombination_requires_a_table_and_valid_anchors() {
    let cfg = settings("I", 0.01, 8, [0.; 3]);
    let mat = Material::constant(cfg.duration, 0., [0.; 3]).unwrap();
    let mut opts = SolveOptions {
        recombination: Some(MatchedRecombination {
            t_unit_k: T_UNIT,
            n_h_emit_m3: N_H,
            h_emit_s: H_EMIT,
            stop_eta: None,
        }),
        ..SolveOptions::default()
    };
    let ion = table();
    let no_table = solve_general(
        &cfg,
        &mat,
        None,
        None,
        ExpansionEquation::Raychaudhuri,
        0.157,
        &opts,
    );
    assert!(no_table.is_err());
    opts.recombination.as_mut().unwrap().t_unit_k = f64::NAN;
    assert!(solve_general(
        &cfg,
        &mat,
        None,
        Some(&ion),
        ExpansionEquation::Raychaudhuri,
        0.157,
        &opts,
    )
    .is_err());
}

/// The offset is held after the stop e-fold (REI handover), and is unchanged before it.
#[test]
fn stop_eta_holds_the_offset_and_leaves_earlier_steps_unchanged() {
    let cfg = settings("I", 0.01, 24, [1e-3, 0., 0.]);
    let ion = table();
    let mat = Material::constant(cfg.duration, 0., [0.; 3]).unwrap();
    let solve = |stop: Option<f64>| {
        let opts = SolveOptions {
            recombination: Some(MatchedRecombination {
                t_unit_k: T_UNIT,
                n_h_emit_m3: N_H,
                h_emit_s: H_EMIT,
                stop_eta: stop,
            }),
            ..SolveOptions::default()
        };
        solve_general(
            &cfg,
            &mat,
            None,
            Some(&ion),
            ExpansionEquation::Raychaudhuri,
            0.157,
            &opts,
        )
        .unwrap()
    };
    let full = solve(None);
    let held = solve(Some(0.1));
    let k = held.history.iter().position(|s| s.node.eta >= 0.1).unwrap();
    for (a, b) in full.history.iter().zip(&held.history).take(k + 1) {
        assert_eq!(a.delta_xe, b.delta_xe);
    }
    assert!(held.history[k..]
        .iter()
        .all(|s| s.delta_xe == held.history[k].delta_xe));
    assert!(full.history.last().unwrap().delta_xe != held.history[k].delta_xe);
}

/// A table with helium electrons (x_e > 1) leaves no hydrogen response while the
/// reference hydrogen is fully ionized, then responds once it recombines.
#[test]
fn fully_ionized_reference_has_no_response() {
    let path = Path::new(env!("CARGO_TARGET_TMPDIR")).join("r113_helium_table.tsv");
    std::fs::write(&path, "eta xe_per_H\n0 1.08\n0.05 1.08\n0.2 0.5\n").unwrap();
    let ion = Ionization::load(&path, N_H, H_EMIT).unwrap();
    let cfg = settings("I", 0.01, 24, [1e-3, 0., 0.]);
    let mat = Material::constant(cfg.duration, 0., [0.; 3]).unwrap();
    let opts = SolveOptions {
        recombination: Some(MatchedRecombination {
            t_unit_k: T_UNIT,
            n_h_emit_m3: N_H,
            h_emit_s: H_EMIT,
            stop_eta: None,
        }),
        ..SolveOptions::default()
    };
    let sol = solve_general(
        &cfg,
        &mat,
        None,
        Some(&ion),
        ExpansionEquation::Raychaudhuri,
        0.157,
        &opts,
    )
    .unwrap();
    for s in &sol.history {
        if ion.xe_at(s.node.eta).unwrap() >= 1.0 {
            assert_eq!(s.delta_xe, 0.0, "eta {}", s.node.eta);
        }
    }
    let last = sol.history.last().unwrap().delta_xe;
    assert!(last != 0.0 && last.is_finite());
}
