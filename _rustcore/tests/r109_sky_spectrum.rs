use bianchi_rustcore::kinetic::sky_spectrum::{analyze, outer, products, Mode, SkySample};
use bianchi_rustcore::kinetic::sphere::SphereGrid;
use std::f64::consts::PI;

fn verify(x: f64, y: f64, tol: f64) {
    assert!(
        (x - y).abs() <= tol,
        "{x} differs from {y} by {}, tolerance {tol}",
        (x - y).abs()
    );
}

#[test]
fn independent_healpix_spin_transform_and_complex_reality() {
    let mut sky = Vec::new();
    let mut expected = Vec::new();
    for row in include_str!("fixtures/r109_healpix_sky.txt").lines() {
        if row.starts_with('#') {
            continue;
        }
        let (kind, values) = row.split_once(' ').unwrap();
        let v: Vec<f64> = values
            .split_whitespace()
            .map(|x| x.parse().unwrap())
            .collect();
        if kind == "p" {
            sky.push(SkySample {
                direction: [v[0], v[1], v[2]],
                weight: v[3],
                t: v[4],
                q: v[5],
                u: v[6],
            });
        } else {
            expected.push((
                v[0] as usize,
                v[1] as i32,
                [[v[2], v[3]], [v[4], v[5]], [v[6], v[7]]],
            ));
        }
    }
    let modes = analyze(&sky, 4).unwrap();
    assert_eq!(modes.len(), 25);
    for (l, m, want) in expected {
        let center = l * (l + 1);
        let pos = &modes[center + m as usize];
        let neg = &modes[center - m as usize];
        assert_eq!((pos.ell, pos.m), (l, m));
        assert_eq!((neg.ell, neg.m), (l, -m));
        let parity = if m % 2 == 0 { 1.0 } else { -1.0 };
        for (j, [re, im]) in want.into_iter().enumerate() {
            verify(pos.alm[j][0], re, 2e-14);
            verify(pos.alm[j][1], im, 2e-14);
            verify(neg.alm[j][0], parity * re, 2e-14);
            verify(neg.alm[j][1], -parity * im, 2e-14);
        }
    }
}

#[test]
fn observer_tilted_blackbody_dipole_and_bolometric_energy() {
    // A moving observer sees T(s)/T0=1/[gamma(1-beta.s)].
    // The bolometric monopole is independently given by a boosted isotropic stress tensor.
    let g = SphereGrid::new(16, 36);
    let beta: f64 = 0.45;
    let gamma = (1.0 - beta * beta).sqrt().recip();
    let axis = [2.0 / 3.0, -1.0 / 3.0, 2.0 / 3.0];
    let mut sky = Vec::new();
    for (n, &w) in g.ehat.chunks_exact(3).zip(&g.w) {
        let d = (gamma * (1.0 - beta * (n[0] * axis[0] + n[1] * axis[1] + n[2] * axis[2]))).recip();
        sky.push(SkySample {
            direction: [n[0], n[1], n[2]],
            weight: w,
            t: d.powi(4),
            q: 0.0,
            u: 0.0,
        });
    }
    let modes = analyze(&sky, 6).unwrap();
    let root4pi = (4.0 * PI).sqrt();
    verify(
        modes[0].alm[0][0] / root4pi,
        gamma * gamma * (1.0 + beta * beta / 3.0),
        2e-12,
    );
    // integral( x D^4 ) /4pi = (4/3)gamma^2 beta * axis_x
    let flux = (4.0 / 3.0) * gamma * gamma * beta;
    let norm = (6.0 * PI).sqrt();
    verify(modes[3].alm[0][0], -norm * flux * axis[0], 2e-12);
    verify(modes[3].alm[0][1], norm * flux * axis[1], 2e-12);
    verify(
        modes[2].alm[0][0],
        (12.0 * PI).sqrt() * flux * axis[2],
        2e-12,
    );
    assert!(modes
        .iter()
        .all(|v| v.alm[1..].iter().flatten().all(|x| *x == 0.0)));
}

#[test]
fn pole_screen_and_partial_solid_angle_are_well_defined() {
    let p = SkySample {
        direction: [0.0, 0.0, 1.0],
        weight: 0.3,
        t: 1.0,
        q: 1.0,
        u: -0.5,
    };
    let modes = analyze(&[p], 5).unwrap();
    verify(modes[0].alm[0][0], 0.3 / (4.0 * PI).sqrt(), 1e-15);
    let amp = 0.3 * (5.0 / (4.0 * PI)).sqrt();
    verify(modes[8].alm[1][0], -amp / 2.0, 1e-15);
    verify(modes[8].alm[2][0], amp / 4.0, 1e-15);
    let south = SkySample {
        direction: [0.0, 0.0, -1.0],
        ..p
    };
    let modes = analyze(&[south], 5).unwrap();
    verify(modes[8].alm[1][0], -amp / 2.0, 1e-15);
    verify(modes[8].alm[2][0], -(-0.5) * amp / 2.0, 1e-15);
    assert!(analyze(&[SkySample { weight: -1.0, ..p }], 2).is_err());
    assert!(analyze(
        &[SkySample {
            direction: [0.0, 0.0, 1.2],
            ..p
        }],
        2
    )
    .is_err());
    assert!(analyze(&[SkySample { u: f64::NAN, ..p }], 2).is_err());
    assert!(analyze(&[], 2).is_err());
}

#[test]
fn nine_cross_products_are_hermitian_and_retain_phase() {
    let a = Mode {
        ell: 2,
        m: 1,
        alm: [[1.0, 2.0], [0.5, -1.0], [-3.0, 4.0]],
    };
    let b = Mode {
        ell: 3,
        m: 2,
        alm: [[3.0, 1.0], [-2.0, 0.5], [1.0, -1.0]],
    };
    for i in 0..3 {
        for j in 0..3 {
            let ab = outer(&a, &b)[i][j];
            let ba = outer(&b, &a)[j][i];
            assert_eq!(ab, [ba[0], -ba[1]]);
        }
    }
    assert_eq!(products(&a, &b)[1], [-1.0, -4.5]);
    assert_eq!(products(&a, &a)[1], [-1.5, 2.0]);
}

#[test]
fn scalar_and_spin_addition_theorems_on_one_off_grid_ray() {
    let s = SkySample {
        direction: [0.36, -0.48, 0.8],
        weight: 1.0,
        t: 1.0,
        q: 0.6,
        u: 0.8,
    };
    let l = 192;
    let modes = analyze(&[s], l).unwrap();
    let mut summed = [0.0; 3];
    for row in &modes[l * l..(l + 1) * (l + 1)] {
        for (i, [re, im]) in row.alm.into_iter().enumerate() {
            summed[i] += re * re + im * im;
        }
    }
    let expected = (2 * l + 1) as f64 / (4.0 * PI);
    verify(summed[0], expected, 2e-11);
    verify(summed[1] + summed[2], expected, 2e-11);
}
