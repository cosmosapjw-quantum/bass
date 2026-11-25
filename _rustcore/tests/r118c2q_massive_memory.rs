use bianchi_rustcore::kinetic::massive_memory::FermiMemory;
#[test]
fn massless_and_massive_memory_contract() {
    let sp = FermiMemory::new(0., 1.68e-4, 3.756e-5, 128).unwrap();
    let beta = [0.01, -0.02, 0.03, 0., 0.01];
    let j = vec![[0.02, 0.01, -0.01, 0., 0.]; sp.nodes().len()];
    let x = sp.response(0.2, beta, &j).unwrap();
    assert!((x.chi_a4 / x.rho_a4 - 8. / 15.).abs() < 1e-13);
    assert!(x.dchi_a4.abs() < 1e-25);
    for k in 0..5 {
        assert!((x.stress_a4[k] + x.chi_a4 * (beta[k] - j[0][k])).abs() < 1e-16);
    }
    let m = FermiMemory::new(0.05, 1.68e-4, 3.756e-5, 128).unwrap();
    let r = m.response(0.2, beta, &j).unwrap();
    assert!(r.dchi_a4 < 0. && r.chi_a4 < x.chi_a4);
    assert!(r.memory_energy_a4 > 0.);
    assert!(m.response(0.2, beta, &j[..2]).is_err());
}

fn expected(
    a: f64,
    b: f64,
    t: f64,
    scheme: bianchi_rustcore::homogeneous_sky::CollisionScheme,
) -> [f64; 2] {
    use bianchi_rustcore::homogeneous_sky::CollisionScheme;
    let c = [-0.9 * a - 0.4 * b, -0.15 * a - 0.4 * b];
    let p = [-(c[0] + 0.3 * a) / 0.7, -(c[1] + 0.3 * b) / 0.7];
    let r = |lambda: f64| {
        let z = t * lambda;
        match scheme {
            CollisionScheme::BackwardEuler => 1. / (1. - z),
            CollisionScheme::Sdirk2 => {
                let g = 1. - std::f64::consts::FRAC_1_SQRT_2;
                (1. + (1. - 2. * g) * z) / (1. - g * z).powi(2)
            }
        }
    };
    [
        r(-1.) * p[0] + r(-0.3) * (a - p[0]),
        r(-1.) * p[1] + r(-0.3) * (b - p[1]),
    ]
}

#[test]
fn five_component_thomson_response_matches_native_screen() {
    use bianchi_rustcore::{
        homogeneous_sky::{field::HarmonicSky, scatter_with, CollisionScheme},
        kinetic::spin_sht::SpinSht,
    };
    use nalgebra::{Matrix3, Vector3};
    let r = 1. / 2_f64.sqrt();
    let t = 1. / 6_f64.sqrt();
    let bases = [
        Matrix3::from_diagonal(&Vector3::new(r, -r, 0.)),
        Matrix3::from_diagonal(&Vector3::new(-t, -t, 2. * t)),
        Matrix3::new(0., r, 0., r, 0., 0., 0., 0., 0.),
        Matrix3::new(0., 0., r, 0., 0., 0., r, 0., 0.),
        Matrix3::new(0., 0., 0., 0., 0., r, 0., r, 0.),
    ];
    let (l, nt, np) = (4, 12, 24);
    let sht = SpinSht::new(l, nt, np).unwrap();
    let render = |a: [f64; 5], b: [f64; 5]| {
        let aa = (0..5).fold(Matrix3::zeros(), |s, k| s + bases[k] * a[k]);
        let bb = (0..5).fold(Matrix3::zeros(), |s, k| s + bases[k] * b[k]);
        let mut iv = Vec::new();
        let mut qv = Vec::new();
        let mut uv = Vec::new();
        for d in sht.grid.ehat.chunks_exact(3) {
            let n = Vector3::new(d[0], d[1], d[2]);
            let h = (d[0] * d[0] + d[1] * d[1]).sqrt();
            let th = Vector3::new(d[2] * d[0] / h, d[2] * d[1] / h, -h);
            let ph = Vector3::new(-d[1] / h, d[0] / h, 0.);
            iv.push(1. + n.dot(&(aa * n)));
            qv.push((2. / 3.) * (th.dot(&(bb * th)) - ph.dot(&(bb * ph))));
            uv.push((4. / 3.) * th.dot(&(bb * ph)));
        }
        (iv, qv, uv)
    };
    let mut worst = 0_f64;
    let mut count = 0;
    for j in 0..6 {
        let a = std::array::from_fn(|k| {
            if j == 5 {
                0.01 * (k as f64 - 2.)
            } else if k == j {
                0.02
            } else {
                0.
            }
        });
        let b = std::array::from_fn(|k| {
            if j == 5 {
                0.006 * (2. - k as f64)
            } else if k == (j + 2) % 5 {
                -0.03
            } else {
                0.
            }
        });
        let (iv, qv, uv) = render(a, b);
        for tau in [0., 0.032, 0.7, 4.] {
            for scheme in [CollisionScheme::BackwardEuler, CollisionScheme::Sdirk2] {
                let mut sky = HarmonicSky::isotropic(l, nt, np, true).unwrap();
                sky.coefficients = sht.from_stokes(&iv, &qv, &uv).into();
                let mut rays = sky.photons().unwrap();
                scatter_with(&mut rays, tau, [0.; 3], scheme).unwrap();
                sky.absorb(&rays).unwrap();
                let (i, q, u) = sht.to_stokes(
                    &sky.coefficients[0],
                    Some((&sky.coefficients[1], &sky.coefficients[2])),
                );
                let aa = std::array::from_fn(|k| expected(a[k], b[k], tau, scheme)[0]);
                let bb = std::array::from_fn(|k| expected(a[k], b[k], tau, scheme)[1]);
                let (ri, rq, ru) = render(aa, bb);
                for (got, want) in i
                    .iter()
                    .chain(&q)
                    .chain(&u)
                    .zip(ri.iter().chain(&rq).chain(&ru))
                {
                    worst = worst.max((got - want).abs());
                }
                count += 1;
            }
        }
    }
    eprintln!("{count} general STF Thomson cases; residual={worst:e}");
    assert!(worst < 5e-13);
}
