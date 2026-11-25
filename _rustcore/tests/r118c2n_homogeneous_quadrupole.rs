use bianchi_rustcore::{
    homogeneous_sky::{field::HarmonicSky, scatter_with, CollisionScheme},
    kinetic::spin_sht::{index, SpinSht},
};
fn expected(a: f64, b: f64, t: f64, scheme: CollisionScheme) -> [f64; 2] {
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
fn native_thomson_axisymmetric_response_matches_two_mode_matrix() {
    let (l, nt, np) = (4, 12, 24);
    let sht = SpinSht::new(l, nt, np).unwrap();
    let mu: Vec<f64> = sht.grid.ehat.chunks_exact(3).map(|e| e[2]).collect();
    let mut worst: f64 = 0.;
    for (a, b) in [(0.02, 0.), (0., 0.03), (-0.04, 0.02)] {
        let i: Vec<f64> = mu.iter().map(|m| 1. + a * (3. * m * m - 1.) / 2.).collect();
        let q: Vec<f64> = mu.iter().map(|m| b * (1. - m * m)).collect();
        let u = vec![0.; mu.len()];
        for tau in [0., 0.032, 0.7, 4.] {
            for scheme in [CollisionScheme::BackwardEuler, CollisionScheme::Sdirk2] {
                let mut h = HarmonicSky::isotropic(l, nt, np, true).unwrap();
                h.coefficients = sht.from_stokes(&i, &q, &u).into();
                let mut rays = h.photons().unwrap();
                scatter_with(&mut rays, tau, [0.; 3], scheme).unwrap();
                h.absorb(&rays).unwrap();
                let (iv, qv, uv) = sht.to_stokes(
                    &h.coefficients[0],
                    Some((&h.coefficients[1], &h.coefficients[2])),
                );
                let [aa, bb] = expected(a, b, tau, scheme);
                for k in 0..mu.len() {
                    let m = mu[k];
                    worst = worst
                        .max((iv[k] - 1. - aa * (3. * m * m - 1.) / 2.).abs())
                        .max((qv[k] - bb * (1. - m * m)).abs())
                        .max(uv[k].abs());
                }
                let e20 = -(h.coefficients[1][index(2, 0)] + h.coefficients[2][index(2, 0)]) * 0.5;
                assert!((e20.re + bb * (32. * std::f64::consts::PI / 15.).sqrt()).abs() < 5e-13);
                assert!(e20.im.abs() < 5e-13);
            }
        }
    }
    eprintln!("24 native scattering cases, max I/Q/U residual={worst:e}");
    assert!(worst < 5e-13);
}
