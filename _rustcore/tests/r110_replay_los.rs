//! R110: line-of-sight replay, ring harmonic analysis, SDIRK2 Thomson cells,
//! Lambda and Lie-type certificates (research/r110_cloud_highl_sky/THEORY.md V1-V12).
use bianchi_rustcore::geom::group::BianchiGroup;
use bianchi_rustcore::homogeneous_sky::{
    initial_sky,
    material::Material,
    replay::{arrival, los_sky, replay, trace_back, StepRecord},
    solve::{solve_with_expansion, Settings, Solution},
    CollisionEvent, CollisionScheme,
};
use bianchi_rustcore::kinetic::lie_history::{LieInitial, RayNode};
use bianchi_rustcore::kinetic::radiation_feedback::{ExpansionEquation, LieUpdate};
use bianchi_rustcore::kinetic::sky_spectrum::{analyze, analyze_rings, Mode};
use bianchi_rustcore::kinetic::sphere::gauss_legendre;
use nalgebra::{Matrix3, Rotation3, Vector3};

#[allow(clippy::too_many_arguments)]
fn settings(
    family: &'static str,
    shear: f64,
    duration: f64,
    steps: usize,
    mesh: (usize, usize),
    feedback: &str,
    dust: (f64, [f64; 3]),
    collision: CollisionScheme,
) -> Settings<'static> {
    Settings {
        family,
        shear,
        duration,
        steps,
        nmu: mesh.0,
        nphi: mesh.1,
        active: feedback != "tracer",
        recoil: feedback == "recoil",
        dust_fraction: dust.0,
        dust_beta: dust.1,
        collision,
        omega_lambda: 0.,
        lie_update: LieUpdate::Additive,
    }
}

fn solve(cfg: &Settings, mat: &Material, lie: Option<&LieInitial>) -> Solution {
    solve_with_expansion(cfg, mat, lie, None, ExpansionEquation::Raychaudhuri).unwrap()
}

fn viii() -> LieInitial {
    let t = |v: [f64; 6]| [[v[0], v[3], v[4]], [v[3], v[1], v[5]], [v[4], v[5], v[2]]];
    LieInitial {
        shear: t([0.17, -0.13, -0.04, 0.042, -0.028, 0.034]),
        n: t([-0.35, 0.53, 0.72, 0., 0., 0.]),
        a: [0.; 3],
    }
}

fn max_abs(m: &[[f64; 3]; 3]) -> f64 {
    m.iter().flatten().fold(0., |a, b| a.max(b.abs()))
}

fn sub(a: &[[f64; 3]; 3], b: &[[f64; 3]; 3]) -> [[f64; 3]; 3] {
    std::array::from_fn(|i| std::array::from_fn(|j| a[i][j] - b[i][j]))
}

/// Forward rays and their replays from the same initial bundles (V3) and the
/// backward trace of their final directions (V4).
fn check_replay(cfg: &Settings, mat: &Material, lie: Option<&LieInitial>) -> (f64, f64) {
    let sol = solve(cfg, mat, lie);
    let initial = initial_sky(cfg.nmu, cfg.nphi).unwrap();
    assert_eq!(initial.len(), sol.photons.len());
    let mut worst_screen = 0f64;
    let mut worst_trace = 0f64;
    for (start, forward) in initial.iter().zip(&sol.photons) {
        let replayed = replay(&sol.records, start.clone()).unwrap();
        let scale = max_abs(&forward.screen());
        worst_screen =
            worst_screen.max(max_abs(&sub(&replayed.screen(), &forward.screen())) / scale);
        assert_eq!(replayed.direction(), forward.direction());
        assert_eq!(replayed.weight(), forward.weight());
        let back = trace_back(&sol.records, forward.direction()).unwrap();
        let d = Vector3::from(back) - Vector3::from(start.direction());
        worst_trace = worst_trace.max(d.norm());
    }
    (worst_screen, worst_trace)
}

#[test]
fn replay_reproduces_forward_rays_and_trace_back_inverts_them() {
    let dur = 0.35;
    let recoil_mat = Material::constant(dur, 0.22, [0.; 3]).unwrap();
    let tracer_mat = Material::constant(dur, 0.22, [0.14, -0.03, 0.02]).unwrap();
    let tilt = (0.22, [0.16, -0.08, 0.04]);
    let be = CollisionScheme::BackwardEuler;
    let sd = CollisionScheme::Sdirk2;
    let cases = [
        (
            "VIIh recoil BE",
            settings("VIIh:0.25", 0.18, dur, 12, (10, 24), "recoil", tilt, be),
            &recoil_mat,
            None,
        ),
        (
            "VIIh recoil SDIRK2",
            settings("VIIh:0.25", 0.18, dur, 12, (10, 24), "recoil", tilt, sd),
            &recoil_mat,
            None,
        ),
        (
            "VIstar tracer SDIRK2",
            settings("VIstar", 0.12, dur, 12, (10, 24), "tracer", (0., [0.; 3]), sd),
            &tracer_mat,
            None,
        ),
        (
            "VIII Lie coflow recoil",
            settings("I", 0.0, dur, 12, (10, 24), "recoil", (0.28, [0.; 3]), sd),
            &recoil_mat,
            Some(viii()),
        ),
    ];
    for (name, cfg, mat, lie) in cases {
        let (screen, trace) = check_replay(&cfg, mat, lie.as_ref());
        println!("{name}: replay screen max rel diff {screen:e}, trace-back {trace:e}");
        assert!(screen <= 1e-15, "{name}: replay differs from forward by {screen:e}");
        assert!(trace <= 1e-12, "{name}: trace-back error {trace:e}");
    }
}

#[test]
fn ring_transform_equals_per_sample_analysis() {
    let dur = 0.35;
    let mat = Material::constant(dur, 0.22, [0.; 3]).unwrap();
    let cfg = settings(
        "VIIh:0.25",
        0.18,
        dur,
        12,
        (10, 24),
        "recoil",
        (0.22, [0.16, -0.08, 0.04]),
        CollisionScheme::BackwardEuler,
    );
    let sol = solve(&cfg, &mat, None);
    let sky = los_sky(&sol.records, [0.1, 0.035, -0.025], 17, 34).unwrap();
    let ring = sky.modes(16).unwrap();
    let direct = analyze(&sky.samples, 16).unwrap();
    let scale = direct
        .iter()
        .flat_map(|m| m.alm.iter().flatten())
        .fold(0f64, |a, b| a.max(b.abs()));
    let diff = ring
        .iter()
        .zip(&direct)
        .flat_map(|(a, b)| {
            a.alm
                .iter()
                .flatten()
                .zip(b.alm.iter().flatten())
                .map(|(x, y)| (x - y).abs())
                .collect::<Vec<_>>()
        })
        .fold(0f64, f64::max);
    println!("ring vs per-sample max abs diff {diff:e} (scale {scale:e})");
    assert!(diff <= 1e-12 * scale);
    assert!(sky.max_landing_error < 1e-12);
}

/// Legendre P_l(x) by the three-term recursion (independent of the Wigner code).
fn legendre(lmax: usize, x: f64) -> Vec<f64> {
    let mut p = vec![1.0, x];
    for l in 1..lmax {
        let lf = l as f64;
        p.push(((2. * lf + 1.) * x * p[l] - lf * p[l - 1]) / (lf + 1.));
    }
    p.truncate(lmax + 1);
    p
}

fn flrw_records(steps: usize) -> Vec<StepRecord> {
    let cfg = settings(
        "FLRW",
        0.,
        0.3,
        steps,
        (8, 16),
        "active",
        (0., [0.; 3]),
        CollisionScheme::BackwardEuler,
    );
    solve(&cfg, &Material::constant(0.3, 0., [0.; 3]).unwrap(), None).records
}

#[test]
fn flrw_static_observer_is_isotropic_and_boosted_observer_is_exact_doppler() {
    let records = flrw_records(8);
    let lmax = 40;
    let still = los_sky(&records, [0.; 3], lmax + 1, 2 * lmax + 2).unwrap();
    let modes = still.modes(lmax).unwrap();
    let worst = modes
        .iter()
        .filter(|m| m.ell > 0)
        .flat_map(|m| m.alm.iter().flatten())
        .fold(0f64, |a, b| a.max(b.abs()));
    assert!(worst < 1e-14, "static FLRW anisotropy {worst:e}");

    // Boost along +z: T(n) = (b/artanh b)/(1 - b n_z) - 1 at every multipole.
    let b = 0.3f64;
    let norm = b / b.atanh();
    let moving = los_sky(&records, [0., 0., b], lmax + 1, 2 * lmax + 2).unwrap();
    let mut pointwise = 0f64;
    let mut polar = 0f64;
    for s in &moving.samples {
        let exact = norm / (1. - b * s.direction[2]) - 1.;
        pointwise = pointwise.max((s.t - exact).abs());
        polar = polar.max(s.q.abs()).max(s.u.abs());
    }
    assert!(pointwise < 2e-14 && polar < 1e-15, "{pointwise:e} {polar:e}");
    let modes: Vec<Mode> = moving.modes(lmax).unwrap();
    let (x, w) = gauss_legendre(200);
    let mut oracle = vec![0.0; lmax + 1];
    for (xi, wi) in x.iter().zip(&w) {
        let p = legendre(lmax, *xi);
        let f = norm / (1. - b * xi) - 1.;
        for l in 0..=lmax {
            oracle[l] += wi * p[l] * f;
        }
    }
    let pi = std::f64::consts::PI;
    let mut worst = 0f64;
    for m in &modes {
        let expected = if m.m == 0 {
            2. * pi * ((2 * m.ell + 1) as f64 / (4. * pi)).sqrt() * oracle[m.ell]
        } else {
            0.
        };
        worst = worst.max((m.alm[0][0] - expected).abs()).max(m.alm[0][1].abs());
        worst = worst.max(m.alm[1][0].abs()).max(m.alm[2][0].abs());
    }
    // a_10 = 0.62947 and a_50 = 3.7170e-4 from the mpmath oracle (THEORY_CHECKS.json);
    // flat index ell*(ell+1)+m gives 2 and 30.
    assert!((modes[2].alm[0][0] - 0.629_469_997_882_992_3).abs() < 1e-12);
    assert!((modes[30].alm[0][0] - 3.716_971_815_275_373e-4).abs() < 1e-15);
    assert!(worst < 1e-13, "boosted FLRW harmonic error {worst:e}");
}

fn constant_shear_records(steps: usize, duration: f64, shear: [[f64; 3]; 3]) -> Vec<StepRecord> {
    (0..steps)
        .map(|k| {
            let node = |i: usize| RayNode {
                eta: duration * i as f64 / steps as f64,
                shear,
                ..Default::default()
            };
            StepRecord {
                left: node(k),
                right: node(k + 1),
                first: vec![],
                second: vec![],
            }
        })
        .collect()
}

#[test]
fn bianchi_i_free_streaming_matches_the_closed_form_at_high_multipole() {
    let r = Rotation3::from_euler_angles(0.3, -0.5, 0.8);
    let diag = Matrix3::from_diagonal(&Vector3::new(0.4, -0.3, -0.1));
    let shear = r.matrix() * diag * r.matrix().transpose();
    let shear_rows: [[f64; 3]; 3] =
        std::array::from_fn(|i| std::array::from_fn(|j| shear[(i, j)]));
    let duration = 0.7;
    let error = |steps: usize| {
        let records = constant_shear_records(steps, duration, shear_rows);
        let sky = los_sky(&records, [0.; 3], 33, 66).unwrap();
        // ln E = -D - ln|u|, u = exp(D Sigma) e_N; T from E^4 via I^(1/4).
        let exact: Vec<f64> = sky
            .samples
            .iter()
            .map(|s| {
                let e_end = -Vector3::from(s.direction);
                let u = (shear * duration).exp() * e_end;
                1. / u.norm()
            })
            .collect();
        let mean = exact.iter().zip(&sky.grid.w).map(|(t, w)| t * w).sum::<f64>()
            / sky.grid.w.iter().sum::<f64>();
        let worst = sky
            .samples
            .iter()
            .zip(&exact)
            .map(|(s, e)| (s.t - (e / mean - 1.)).abs())
            .fold(0f64, f64::max);
        let polar = sky
            .samples
            .iter()
            .map(|s| s.q.abs().max(s.u.abs()))
            .fold(0f64, f64::max);
        assert!(polar < 1e-15, "free streaming generated polarization {polar:e}");
        worst
    };
    let (e8, e16, e32) = (error(8), error(16), error(32));
    println!("Bianchi I closed form errors {e8:e} {e16:e} {e32:e}");
    // Second order of the midpoint characteristic map; 1.3e-6 at 32 steps.
    assert!(e32 < 2e-6 && e8 / e16 > 3.5 && e16 / e32 > 3.5);
}

#[test]
fn low_multipoles_agree_with_the_lagrangian_quadrature_to_its_weight_error() {
    // The forward samples are exact samples of the replay field; the remaining
    // difference is the forward quadrature, whose transported solid angles carry
    // the O(deta^2) midpoint Jacobian error. It must fall with the step, not the mesh.
    let dur = 0.35;
    let mat = Material::constant(dur, 0.22, [0.; 3]).unwrap();
    let obs = [0.1, 0.035, -0.025];
    let mut previous = f64::INFINITY;
    for steps in [12, 24, 48] {
        let cfg = settings(
            "VIIh:0.25",
            0.18,
            dur,
            steps,
            (16, 40),
            "recoil",
            (0.22, [0.16, -0.08, 0.04]),
            CollisionScheme::BackwardEuler,
        );
        let sol = solve(&cfg, &mat, None);
        let forward = analyze(
            &bianchi_rustcore::homogeneous_sky::observed_sky(&sol.photons, obs).unwrap(),
            4,
        )
        .unwrap();
        let los = los_sky(&sol.records, obs, 33, 66).unwrap().modes(4).unwrap();
        let mut worst = 0f64;
        // l = 0 of T vanishes by the monopole normalization on both grids.
        for (a, b) in forward.iter().zip(&los).filter(|(a, _)| a.ell > 0) {
            for f in 0..3 {
                let scale = forward
                    .iter()
                    .filter(|m| m.ell == a.ell)
                    .map(|m| m.alm[f][0].hypot(m.alm[f][1]))
                    .fold(0f64, f64::max);
                if scale > 0. {
                    let d = (a.alm[f][0] - b.alm[f][0]).hypot(a.alm[f][1] - b.alm[f][1]);
                    worst = worst.max(d / scale);
                }
            }
        }
        println!("steps {steps}: max relative |forward - LoS| at 1<=l<=4 {worst:e}");
        assert!(worst < 1e-4 && worst * 3.0 < previous);
        previous = worst;
    }
}

#[test]
fn rotated_lie_data_give_covariant_replayed_screens() {
    let dur = 0.35;
    let mat = Material::constant(dur, 0.22, [0.; 3]).unwrap();
    let cfg = settings(
        "I",
        0.,
        dur,
        12,
        (20, 48),
        "recoil",
        (0.28, [0.; 3]),
        CollisionScheme::Sdirk2,
    );
    let ic = viii();
    let r = Rotation3::from_euler_angles(0.41, -0.27, 1.13);
    let rm = *r.matrix();
    let rot = |m: [[f64; 3]; 3]| -> [[f64; 3]; 3] {
        let x = rm * Matrix3::from_fn(|i, j| m[i][j]) * rm.transpose();
        std::array::from_fn(|i| std::array::from_fn(|j| x[(i, j)]))
    };
    let rotated = LieInitial {
        shear: rot(ic.shear),
        n: rot(ic.n),
        a: (rm * Vector3::from(ic.a)).into(),
    };
    let beta = Vector3::new(0.13, -0.07, 0.04);
    let base = solve(&cfg, &mat, Some(&ic));
    let turned = solve(&cfg, &mat, Some(&rotated));
    let mut worst = 0f64;
    for k in 0..40 {
        let t = 0.7 * k as f64 + 0.1;
        let z = -1. + 2. * (k as f64 + 0.5) / 40.;
        let s = (1. - z * z).sqrt();
        let n = Vector3::new(s * t.cos(), s * t.sin(), z);
        let a = arrival(&base.records, beta.into(), n.into()).unwrap();
        let b = arrival(&turned.records, (rm * beta).into(), (rm * n).into()).unwrap();
        let expected = rot(a.screen);
        worst = worst.max(max_abs(&sub(&b.screen, &expected)) / max_abs(&expected));
    }
    println!("rotation covariance max relative screen difference {worst:e}");
    assert!(worst < 1e-9);
}

fn group(node: &RayNode) -> BianchiGroup {
    let n = &node.n;
    BianchiGroup::new([n[0][0], n[1][1], n[2][2], n[0][1], n[0][2], n[1][2]], node.a)
}

#[test]
fn congruence_update_preserves_lie_type_jacobi_and_h_for_all_families() {
    for family in [
        "I", "II", "III", "IV", "V", "VI0", "VIh", "VIstar", "VII0", "VIIh", "VIII", "IX",
        "VIh:-0.5", "VIIh:0.7",
    ] {
        let mut cfg = settings(
            family,
            0.06,
            0.3,
            16,
            (8, 16),
            "active",
            (0., [0.; 3]),
            CollisionScheme::BackwardEuler,
        );
        let mat = Material::constant(0.3, 0., [0.; 3]).unwrap();
        let mut drift = [0f64; 2];
        let mut labels = [("", ""); 2];
        for (k, update) in [LieUpdate::Additive, LieUpdate::Congruence].iter().enumerate() {
            cfg.lie_update = *update;
            let sol = solve(&cfg, &mat, None);
            let g0 = group(&sol.history[0].node);
            let g1 = group(&sol.history.last().unwrap().node);
            labels[k] = (g0.classify().name, g1.classify().name);
            if let (Some(k0), Some(k1)) = (g0.kappa(), g1.kappa()) {
                // Bianchi IV and V have kappa = 1/h = 0 exactly.
                drift[k] = if k0 == 0. { k1.abs() } else { ((k1 - k0) / k0).abs() };
            }
            if *update == LieUpdate::Congruence {
                assert_eq!(labels[k].0, labels[k].1, "{family} changed type");
                let j = Vector3::from(sol.history.last().unwrap().node.jacobi_residual).norm();
                assert!(j < 1e-14, "{family} Jacobi {j:e}");
            }
        }
        println!(
            "{family}: additive {:?} 1/h drift {:e}; congruence {:?} 1/h drift {:e}",
            labels[0], drift[0], labels[1], drift[1]
        );
        assert!(drift[1] < 1e-13, "{family}: congruence h drift {:e}", drift[1]);
    }
}

#[test]
fn lambda_cdm_flrw_follows_the_closed_form_hubble_rate_at_second_order() {
    let (omega_l, dust) = (0.3, 0.6);
    let duration = 1.2;
    let error = |steps: usize| {
        let mut cfg = settings(
            "FLRW",
            0.,
            duration,
            steps,
            (8, 16),
            "active",
            (dust, [0.; 3]),
            CollisionScheme::BackwardEuler,
        );
        cfg.omega_lambda = omega_l;
        let sol = solve(&cfg, &Material::constant(duration, 0., [0.; 3]).unwrap(), None);
        let (om_r, om_d) = ((1. - omega_l) * (1. - dust), (1. - omega_l) * dust);
        let mut worst = 0f64;
        let mut gauss = 0f64;
        for snap in &sol.history {
            let e = snap.node.eta;
            let h = (om_r * (-4. * e).exp() + om_d * (-3. * e).exp() + omega_l).sqrt();
            worst = worst.max((snap.node.hubble_ratio / h - 1.).abs());
            let lam = omega_l / snap.node.hubble_ratio.powi(2);
            assert!((snap.node.omega_lambda / lam - 1.).abs() < 1e-14);
            gauss = gauss.max(snap.node.gauss_residual.abs());
        }
        (worst, gauss)
    };
    let (e1, e2, e3) = (error(12), error(24), error(48));
    println!("LambdaCDM FLRW (h error, Gauss residual) {e1:?} {e2:?} {e3:?}");
    // The Gauss residual is a truncation diagnostic of the free Raychaudhuri step.
    assert!(e1.0 / e2.0 > 3.5 && e2.0 / e3.0 > 3.5 && e3.0 < 1e-4);
    assert!(e1.1 / e2.1 > 3.5 && e2.1 / e3.1 > 3.5);
}

#[test]
fn los_sky_rejects_negative_screen_eigenvalue_and_analyze_rings_checks_nyquist() {
    // Non-PSD synthetic source makes trace > 0 while yielding a negative transverse eigenvalue.
    let node0 = RayNode::default();
    let mut node1 = RayNode::default();
    node1.eta = 0.01;
    let rec = vec![StepRecord {
        left: node0,
        right: node1,
        first: vec![CollisionEvent {
            depth: 1.0,
            beta: [0.0; 3],
            gain_map: None,
            scheme: CollisionScheme::BackwardEuler,
            sources: vec![[
                [100.0, 0.0, 0.0],
                [0.0, -50.0, 0.0],
                [0.0, 0.0, 100.0],
            ]],
        }],
        second: vec![],
    }];
    let err = los_sky(&rec, [0.0; 3], 5, 10).err().unwrap();
    assert!(err.contains("negative transverse screen eigenvalue"), "{err}");
    let z = [0.5, -0.5];
    let w = [1.0, 1.0];
    let v = vec![0.0; 8];
    assert!(analyze_rings(&z, &w, 4, &v, &v, &v, 2).is_err());
    assert!(analyze_rings(&z, &w, 5, &v, &v, &v, 2).is_err());
    let v10 = vec![0.0; 10];
    assert!(analyze_rings(&z, &w, 5, &v10, &v10, &v10, 2).is_ok());
    assert!(analyze_rings(&z, &w, 5, &v10, &v10, &v10, 3).is_err());
}

#[test]
fn non_flrw_viih_with_lambda_preserves_type_and_gauss_reduced_matches_raychaudhuri() {
    let mat = Material::constant(0.6, 0.0, [0.0; 3]).unwrap();
    let run = |steps: usize, eq: ExpansionEquation| {
        let mut cfg = settings(
            "VIIh:0.4",
            0.05,
            0.6,
            steps,
            (8, 16),
            "active",
            (0.6, [0.0; 3]),
            CollisionScheme::Sdirk2,
        );
        cfg.omega_lambda = 0.2;
        cfg.lie_update = LieUpdate::Congruence;
        solve_with_expansion(&cfg, &mat, None, None, eq).unwrap()
    };
    let r1 = run(16, ExpansionEquation::Raychaudhuri);
    let r2 = run(32, ExpansionEquation::Raychaudhuri);
    let g2 = run(32, ExpansionEquation::GaussReduced);
    let last_r = &r2.history.last().unwrap().node;
    let last_g = &g2.history.last().unwrap().node;
    assert_eq!(group(&r2.history[0].node).classify().name, "VII_h");
    assert_eq!(group(last_r).classify().name, "VII_h");
    assert!((last_r.hubble_ratio / last_g.hubble_ratio - 1.0).abs() < 1e-4);
    assert!(last_r.gauss_residual.abs() * 3.5 < r1.history.last().unwrap().node.gauss_residual.abs());
}
