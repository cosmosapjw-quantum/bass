use bianchi_rustcore::homogeneous_sky::{
    field::HarmonicSky, harmonic_collision::continuum_cell, scatter_with, CollisionScheme,
};
use bianchi_rustcore::kinetic::spin_sht::{index, C64};

fn fixture(l: usize) -> HarmonicSky {
    let mut h = HarmonicSky::isotropic(l, 64, 128, true).unwrap();
    h.coefficients[0][index(1, 0)] = C64::new(0.07, 0.);
    h.coefficients[0][index(2, 2)] = C64::new(0.04, -0.02);
    h.coefficients[0][index(2, -2)] = h.coefficients[0][index(2, 2)].conj();
    h.coefficients[0][index(5, 0)] = C64::new(0.03, 0.);
    h.coefficients[1][index(2, 1)] = C64::new(0.02, 0.03);
    h.coefficients[2][index(2, -1)] = -h.coefficients[1][index(2, 1)].conj();
    h.coefficients[1][index(4, 2)] = C64::new(0.006, -0.007);
    h.coefficients[2][index(4, -2)] = h.coefficients[1][index(4, 2)].conj();
    h
}
#[test]
fn continuum_cells_agree_with_refined_ray_oracle() {
    let l = 6;
    for (beta, work) in [
        ([0., 0., 0.], 8),
        ([0.03, -0.02, 0.01], 20),
        ([0.3, -0.2, 0.1], 36),
        ([0., 0., 0.85], 84),
    ] {
        for scheme in [CollisionScheme::BackwardEuler, CollisionScheme::Sdirk2] {
            let mut h = fixture(l);
            let mut rays = h.photons().unwrap();
            let (out, event, diagnostics) =
                continuum_cell(&h.coefficients, l, work, beta, 0.3, scheme).unwrap();
            let oracle = scatter_with(&mut rays, 0.3, beta, scheme).unwrap();
            h.absorb(&rays).unwrap();
            let err = out
                .iter()
                .flatten()
                .zip(h.coefficients.iter().flatten())
                .map(|(a, b)| (a - b).norm())
                .fold(0., f64::max);
            let src_err = event
                .sources
                .iter()
                .flatten()
                .flatten()
                .zip(oracle.sources.iter().flatten().flatten())
                .map(|(a, b)| (a - b).abs())
                .fold(0., f64::max);
            eprintln!("beta={beta:?} scheme={scheme:?} work={work} modes={err:e} source={src_err:e} bound={:e}",diagnostics.max_inverse_relative_bound);
            assert!(err < 2e-9 && src_err < 2e-8);
        }
    }
}
#[test]
fn invalid_and_zero_depth() {
    let h = fixture(6);
    assert!(continuum_cell(
        &h.coefficients,
        6,
        6,
        [1., 0., 0.],
        1.,
        CollisionScheme::BackwardEuler
    )
    .is_err());
    assert!(continuum_cell(
        &h.coefficients,
        6,
        6,
        [0.8, 0., 0.],
        1.,
        CollisionScheme::BackwardEuler
    )
    .is_err());
    let (out, event, _) = continuum_cell(
        &h.coefficients,
        6,
        6,
        [0.2, 0., 0.],
        0.,
        CollisionScheme::Sdirk2,
    )
    .unwrap();
    assert_eq!(out, h.coefficients);
    assert!(event.sources.is_empty());
}

#[test]
fn coupled_recoil_route_preserves_exchange_and_matches_refined_grid() {
    use bianchi_rustcore::homogeneous_sky::{
        field::Route,
        material::Material,
        replay::los_sky,
        solve::{solve_general, Settings, SolveOptions},
    };
    use bianchi_rustcore::kinetic::radiation_feedback::{ExpansionEquation, LieUpdate};
    let cfg = Settings {
        family: "I",
        shear: 0.04,
        duration: 0.04,
        steps: 8,
        nmu: 10,
        nphi: 24,
        active: true,
        recoil: true,
        dust_fraction: 0.8,
        dust_beta: [0.1, 0.03, -0.02],
        collision: CollisionScheme::Sdirk2,
        omega_lambda: 0.,
        lie_update: LieUpdate::Congruence,
    };
    let mat = Material::constant(cfg.duration, 0.3, [0.; 3]).unwrap();
    let run = |route| {
        solve_general(
            &cfg,
            &mat,
            None,
            None,
            ExpansionEquation::Raychaudhuri,
            0.157,
            &SolveOptions {
                route,
                ..Default::default()
            },
        )
        .unwrap()
    };
    let a = run(Route::HarmonicContinuum {
        lmax: 8,
        n_theta: 24,
        n_phi: 48,
        work_lmax: 24,
    });
    let b = run(Route::Harmonic {
        lmax: 8,
        n_theta: 24,
        n_phi: 48,
    });
    let m = |sol: &bianchi_rustcore::homogeneous_sky::solve::Solution| {
        los_sky(&sol.records, [0.01, -0.02, 0.03], 16, 32)
            .unwrap()
            .modes(6)
            .unwrap()
    };
    let aa = m(&a);
    let bb = m(&b);
    let err = aa
        .iter()
        .zip(bb)
        .flat_map(|(x, y)| x.alm.into_iter().flatten().zip(y.alm.into_iter().flatten()))
        .map(|(x, y)| (x - y).abs())
        .fold(0., f64::max);
    let exchange = a
        .history
        .iter()
        .map(|s| s.collision_energy_defect.abs())
        .fold(0., f64::max);
    eprintln!("coupled max mode error {err:e}; exchange defect {exchange:e}");
    assert!(err < 2e-10 && exchange < 2e-12);
    assert!(a
        .records
        .iter()
        .flat_map(|r| r.first.iter().chain(&r.second))
        .all(|e| e.gain_map.is_none()));
}

#[test]
fn optically_thin_equilibrium_does_not_drift() {
    let mut h = HarmonicSky::isotropic(2, 5, 10, true).unwrap().coefficients;
    let before = h.clone();
    for _ in 0..2000 {
        h = continuum_cell(&h, 2, 2, [0.; 3], 1e-9, CollisionScheme::Sdirk2)
            .unwrap()
            .0;
    }
    let err = h
        .iter()
        .flatten()
        .zip(before.iter().flatten())
        .map(|(a, b)| (a - b).norm())
        .fold(0., f64::max);
    eprintln!("2000 optically thin equilibrium cells max drift={err:e}");
    assert!(err < 1e-13);
}

#[test]
fn rejects_nonphysical_spin_slots_and_reality_violation() {
    let mut h = fixture(6).coefficients;
    h[1][0] = C64::new(0.1, 0.);
    assert!(continuum_cell(&h, 6, 20, [0.; 3], 0.1, CollisionScheme::BackwardEuler).is_err());
    let mut h = fixture(6).coefficients;
    h[0][index(2, -2)] = C64::new(0., 0.);
    assert!(continuum_cell(&h, 6, 20, [0.; 3], 0.1, CollisionScheme::BackwardEuler).is_err());
}
