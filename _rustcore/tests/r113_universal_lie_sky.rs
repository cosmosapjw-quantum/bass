//! R113 verification: harmonic (Lie spin-harmonic) route, neutrinos and frames.
use bianchi_rustcore::homogeneous_sky::{
    field::{HarmonicSky, Route},
    frames::{combine, energy_frame},
    material::Material,
    observed_sky, scatter_with,
    solve::{solve_general, Settings, Solution, SolveOptions},
    CollisionScheme,
};
use bianchi_rustcore::kinetic::radiation_feedback::{ExpansionEquation, LieUpdate};
use bianchi_rustcore::kinetic::sky_spectrum::analyze;
use bianchi_rustcore::kinetic::spin_sht::{index, random_real_coefficients, C64};

fn settings(family: &str, shear: f64, duration: f64, steps: usize) -> Settings<'_> {
    Settings {
        family,
        shear,
        duration,
        steps,
        nmu: 12,
        nphi: 28,
        active: true,
        recoil: false,
        dust_fraction: 0.,
        dust_beta: [0.; 3],
        collision: CollisionScheme::BackwardEuler,
        omega_lambda: 0.,
        lie_update: LieUpdate::Additive,
    }
}

fn run(cfg: &Settings, mat: &Material, opts: &SolveOptions) -> Solution {
    solve_general(
        cfg,
        mat,
        None,
        None,
        ExpansionEquation::Raychaudhuri,
        0.5,
        opts,
    )
    .unwrap()
}

/// V6: rest-electron harmonic collision equals the PSTF backward-Euler closed form.
#[test]
fn rest_electron_harmonic_collision_is_the_exact_pstf_backward_euler_step() {
    let lmax = 8;
    let mut h = HarmonicSky::isotropic(lmax, lmax + 3, 2 * lmax + 6, true).unwrap();
    let [mut a0, ap, am] = random_real_coefficients(lmax, lmax, 5);
    a0[0] += C64::new(10.0 * (4.0 * std::f64::consts::PI).sqrt(), 0.0);
    h.coefficients = vec![a0, ap, am];
    let before = h.coefficients.clone();
    let tau = 0.7;
    let mut grid = h.photons().unwrap();
    scatter_with(&mut grid, tau, [0.; 3], CollisionScheme::BackwardEuler).unwrap();
    h.absorb(&grid).unwrap();
    let after = &h.coefficients;
    // HEALPix E: d/dtau (I, E) = A (I, E), A = [[-9/10, 3/(5 sqrt6)], [sqrt6/10, -2/5]].
    let s6 = 6f64.sqrt();
    let a = [[-0.9, 3.0 / (5.0 * s6)], [s6 / 10.0, -0.4]];
    let m = [
        [1.0 - tau * a[0][0], -tau * a[0][1]],
        [-tau * a[1][0], 1.0 - tau * a[1][1]],
    ];
    let det = m[0][0] * m[1][1] - m[0][1] * m[1][0];
    let inv = [
        [m[1][1] / det, -m[0][1] / det],
        [-m[1][0] / det, m[0][0] / det],
    ];
    let e = |c: &Vec<Vec<C64>>, k: usize| -(c[1][k] + c[2][k]) * 0.5;
    let b = |c: &Vec<Vec<C64>>, k: usize| (c[1][k] - c[2][k]) * C64::new(0.0, 0.5);
    let mut worst: f64 = 0.0;
    for l in 0..=lmax {
        for mm in -(l as i64)..=(l as i64) {
            let k = index(l, mm);
            let (i_want, e_want, b_want) = match l {
                0 => (before[0][k], C64::new(0., 0.), C64::new(0., 0.)),
                2 => (
                    before[0][k] * inv[0][0] + e(&before, k) * inv[0][1],
                    before[0][k] * inv[1][0] + e(&before, k) * inv[1][1],
                    b(&before, k) / (1.0 + tau),
                ),
                _ => (
                    before[0][k] / (1.0 + tau),
                    e(&before, k) / (1.0 + tau),
                    b(&before, k) / (1.0 + tau),
                ),
            };
            worst = worst
                .max((after[0][k] - i_want).norm())
                .max((e(after, k) - e_want).norm())
                .max((b(after, k) - b_want).norm());
        }
    }
    eprintln!("V6 max deviation {worst:e}");
    assert!(worst < 2e-13, "max deviation {worst:e}");
}

/// First-order Bianchi I with collisionless radiation (THEORY D7):
/// Sigma' = -Sigma - (8/5) Psi, Psi' = Sigma.
fn first_order_shear(s0: f64, eta: f64) -> f64 {
    let n = 20000;
    let h = eta / n as f64;
    let f = |y: [f64; 2]| [-y[0] - 1.6 * y[1], y[0]];
    let mut y = [s0, 0.0];
    for _ in 0..n {
        let k1 = f(y);
        let k2 = f([y[0] + 0.5 * h * k1[0], y[1] + 0.5 * h * k1[1]]);
        let k3 = f([y[0] + 0.5 * h * k2[0], y[1] + 0.5 * h * k2[1]]);
        let k4 = f([y[0] + h * k3[0], y[1] + h * k3[1]]);
        for i in 0..2 {
            y[i] += h / 6.0 * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i]);
        }
    }
    y[0]
}

/// V9 and V11: collisionless radiation stress in Bianchi I for both routes; the
/// neutrino split of identical collisionless radiation leaves the geometry unchanged.
#[test]
fn collisionless_stress_follows_first_order_law_and_neutrino_split_is_neutral() {
    let s0 = 1e-3;
    let duration = 3.0;
    let cfg = settings("I", s0, duration, 300);
    let mat = Material::constant(duration, 0., [0.; 3]).unwrap();
    for route in [Route::Rays, Route::harmonic(10)] {
        let base = run(
            &cfg,
            &mat,
            &SolveOptions {
                route: route.clone(),
                neutrino_fraction: 0.,
                recombination: None,
            },
        );
        let split = run(
            &cfg,
            &mat,
            &SolveOptions {
                route: route.clone(),
                neutrino_fraction: 0.4,
                recombination: None,
            },
        );
        let mut worst: f64 = 0.0;
        let mut split_gap: f64 = 0.0;
        for (k, snap) in base.history.iter().enumerate().step_by(25) {
            let law = first_order_shear(s0, snap.node.eta);
            worst = worst.max((snap.node.shear[0][0] - law).abs() / s0);
            let other = &split.history[k];
            split_gap = split_gap.max((other.node.shear[0][0] - snap.node.shear[0][0]).abs() / s0);
            assert!(other.omega_neutrino > 0.0 && other.neutrino.is_some());
        }
        eprintln!("V9 {route:?}: first-order deviation {worst:e}; V11 split gap {split_gap:e}");
        assert!(
            split_gap < 1e-11,
            "neutrino split changed the geometry: {split_gap:e}"
        );
        assert!(
            worst < 1e-2,
            "{route:?}: first-order law deviation {worst:e}"
        );
        // Oscillatory decay: the shear changes sign before eta = 3 (roots -1/2 +- 1.16 i).
        assert!(base.history.iter().any(|s| s.node.shear[0][0] < 0.0));
    }
}

/// FLRW with photons and neutrinos: H = exp(-2 eta) and an isotropic sky.
#[test]
fn flrw_with_neutrinos_keeps_radiation_expansion_and_isotropy() {
    let cfg = settings("FLRW", 0.0, 0.5, 20);
    let mat = Material::constant(0.5, 0., [0.; 3]).unwrap();
    for route in [Route::Rays, Route::harmonic(6)] {
        let sol = run(
            &cfg,
            &mat,
            &SolveOptions {
                route,
                neutrino_fraction: 0.41,
                recombination: None,
            },
        );
        let last = &sol.history.last().unwrap().node;
        assert!((last.hubble_ratio - (-1.0f64).exp()).abs() < 1e-12);
        let sky = observed_sky(&sol.photons, [0.; 3]).unwrap();
        let modes = analyze(&sky, 4).unwrap();
        for m in modes.iter().filter(|m| m.ell > 0) {
            assert!(m.alm.iter().flatten().all(|x| x.abs() < 1e-12));
        }
    }
}

/// V7 (lite): both representations of the same tilted class-B problem agree at low l,
/// and the harmonic route converges toward the ray route with lmax.
#[test]
fn harmonic_and_ray_routes_agree_on_a_tilted_class_b_sky() {
    let mut cfg = settings("VIIh:0.25", 0.12, 0.2, 16);
    cfg.recoil = true;
    cfg.dust_fraction = 0.3;
    cfg.dust_beta = [0.05, -0.02, 0.01];
    cfg.nmu = 18;
    cfg.nphi = 40;
    let mat = Material::constant(0.2, 0.25, [0.; 3]).unwrap();
    let beta_o = [0.02, -0.01, 0.015];
    let modes_of = |route: Route| {
        let sol = run(
            &cfg,
            &mat,
            &SolveOptions {
                route,
                neutrino_fraction: 0.,
                recombination: None,
            },
        );
        let sky = observed_sky(&sol.photons, beta_o).unwrap();
        (
            analyze(&sky, 3).unwrap(),
            sol.history.last().unwrap().node.shear,
        )
    };
    let (rays, rays_shear) = modes_of(Route::Rays);
    let scale = rays
        .iter()
        .filter(|m| m.ell > 0)
        .flat_map(|m| m.alm[0])
        .fold(0.0f64, |a, x| a.max(x.abs()));
    let diff = |other: &[bianchi_rustcore::kinetic::sky_spectrum::Mode]| {
        rays.iter()
            .zip(other)
            .filter(|(m, _)| m.ell > 0)
            .map(|(a, b)| {
                (0..3)
                    .flat_map(|x| (0..2).map(move |y| (x, y)))
                    .map(|(x, y)| (a.alm[x][y] - b.alm[x][y]).abs())
                    .fold(0.0, f64::max)
            })
            .fold(0.0, f64::max)
            / scale
    };
    let (h8, s8) = modes_of(Route::harmonic(8));
    let (h16, s16) = modes_of(Route::harmonic(16));
    let d8 = diff(&h8);
    let d16 = diff(&h16);
    let shear_gap = |s: [[f64; 3]; 3]| {
        (0..3)
            .flat_map(|i| (0..3).map(move |j| (i, j)))
            .map(|(i, j)| (s[i][j] - rays_shear[i][j]).abs())
            .fold(0.0, f64::max)
    };
    eprintln!(
        "V7 lite: rel diff l<=3 lmax8 {d8:e} lmax16 {d16:e}; shear gap {:e} {:e}",
        shear_gap(s8),
        shear_gap(s16)
    );
    assert!(d16 < 5e-3 && d16 <= d8 + 1e-12, "{d8:e} {d16:e}");
    assert!(shear_gap(s16) < 1e-5);
}

#[test]
fn thin_harmonic_collisions_do_not_accumulate_monopole_leakage() {
    let iso = HarmonicSky::isotropic(16, 19, 38, true).unwrap();
    let m_iso = iso.moments().unwrap();
    assert!((m_iso.area - 4.0 * std::f64::consts::PI).abs() < 1e-15);
    assert!((m_iso.energy - 4.0 * std::f64::consts::PI).abs() < 1e-14);
    assert_eq!(m_iso.flux, [0.0; 3]);
    let mut rand_sky = HarmonicSky::isotropic(12, 16, 32, true).unwrap();
    let [mut a0, ap, am] = random_real_coefficients(12, 8, 19);
    a0[0] = C64::new(30.0 * (4.0 * std::f64::consts::PI).sqrt(), 0.0);
    rand_sky.coefficients = vec![a0, ap, am];
    let m_ana = rand_sky.moments().unwrap();
    let m_quad = bianchi_rustcore::homogeneous_sky::moments(&rand_sky.photons().unwrap()).unwrap();
    assert!((m_ana.energy - m_quad.energy).abs() < 1e-13 * m_ana.energy);
    for i in 0..3 {
        assert!((m_ana.flux[i] - m_quad.flux[i]).abs() < 1e-13);
        for j in 0..3 {
            assert!((m_ana.pressure[i][j] - m_quad.pressure[i][j]).abs() < 1e-13);
        }
    }

    let mut cfg = settings("I", 5e-4, 4.0, 512);
    cfg.recoil = true;
    cfg.dust_fraction = 0.5;
    cfg.collision = CollisionScheme::Sdirk2;
    cfg.lie_update = LieUpdate::Congruence;
    let mat = Material::constant(4.0, 0.5, [0.; 3]).unwrap();

    let eval_l = |lmax: usize| {
        let sol = solve_general(
            &cfg,
            &mat,
            None,
            None,
            ExpansionEquation::Raychaudhuri,
            0.157,
            &SolveOptions {
                route: Route::harmonic(lmax),
                neutrino_fraction: 0.4,
                recombination: None,
            },
        )
        .unwrap();
        let last = sol.history.last().unwrap();
        let mut parts = vec![(sol.photon_scale, &last.radiation)];
        if let Some(nu) = &last.neutrino {
            parts.push((sol.neutrino_scale, nu));
        }
        let (_, rad_flux, rad_press) = combine(&parts).unwrap();
        let rad_beta = energy_frame(rad_flux, rad_press).unwrap();
        let frame_rad_norm = rad_beta.iter().map(|x| x * x).sum::<f64>().sqrt();
        let obs = last.host_beta;
        let sky = observed_sky(&sol.photons, obs).unwrap();
        let modes = analyze(&sky, 4).unwrap();
        let c2_tt = modes
            .iter()
            .filter(|m| m.ell == 2)
            .map(|m| m.alm[0][0] * m.alm[0][0] + m.alm[0][1] * m.alm[0][1])
            .sum::<f64>()
            / 5.0;
        let c4_tt = modes
            .iter()
            .filter(|m| m.ell == 4)
            .map(|m| m.alm[0][0] * m.alm[0][0] + m.alm[0][1] * m.alm[0][1])
            .sum::<f64>()
            / 9.0;
        let c4_ee = modes
            .iter()
            .filter(|m| m.ell == 4)
            .map(|m| m.alm[1][0] * m.alm[1][0] + m.alm[1][1] * m.alm[1][1])
            .sum::<f64>()
            / 9.0;
        (frame_rad_norm, c2_tt, c4_tt, c4_ee)
    };

    let (fr16, _, c4_tt_16, c4_ee_16) = eval_l(16);
    let (fr24, c2_tt_24, c4_tt_24, c4_ee_24) = eval_l(24);
    assert!(
        fr16 < 1e-15 && fr24 < 1e-15,
        "monopole drifted radiation frame: l16={fr16:e}, l24={fr24:e}"
    );
    let rel_c4_tt = (c4_tt_24 - c4_tt_16).abs() / c4_tt_24.max(1e-30);
    let norm_c4_ee = (c4_ee_24 - c4_ee_16).abs() / c2_tt_24.max(1e-30);
    assert!(
        rel_c4_tt < 1e-7,
        "C_4^TT shifted across harmonic lmax=16->24: {rel_c4_tt:e}"
    );
    assert!(
        norm_c4_ee < 1e-16,
        "C_4^EE sky-normalized shift exceeded sub-ULP bound: {norm_c4_ee:e}"
    );
}
