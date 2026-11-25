use bianchi_rustcore::kinetic::{magnetic_kernel::magnetic_rank3, memory_mixture::stf_matrix};
#[test]
fn exact_sharp_bounds_and_zero() {
    let s = stf_matrix([1., 0., 0., 0., 0.]);
    for (e, want) in [
        ([1., 0., 0., 0., 0.], 0.),
        ([0., 1., 0., 0., 0.], 0.5),
        ([0., 0., 1., 0., 0.], 0.1),
    ] {
        let m = magnetic_rank3(s, stf_matrix(e));
        assert!((m.iter().flatten().flatten().map(|x| x * x).sum::<f64>() - want).abs() < 1e-14);
    }
}
#[test]
fn native_harmonics_and_rotation_invariants() {
    use bianchi_rustcore::{
        geom::lie::quadratic_coefficients,
        kinetic::{
            b3_coupling::b3_source,
            magnetic_kernel::norm2,
            spin_sht::{SpinSht, C64},
        },
    };
    use nalgebra::{Rotation3, Vector3};
    let sht = SpinSht::new(4, 10, 20).unwrap();
    let mut worst = 0_f64;
    let mut checked = 0;
    for i in 0..5 {
        for j in 0..5 {
            for a in [0., 0.31, 0.79] {
                let r = Rotation3::from_euler_angles(a, -2. * a, 0.4 * a);
                let s = r.matrix()
                    * stf_matrix(std::array::from_fn(|k| if k == i { 1. } else { 0. }))
                    * r.matrix().transpose();
                let e = r.matrix()
                    * stf_matrix(std::array::from_fn(|k| if k == j { 1. } else { 0. }))
                    * r.matrix().transpose();
                let m = magnetic_rank3(s, e);
                let w = s.norm_squared() * e.norm_squared() - s.component_mul(&e).sum().powi(2);
                let q = 0.5 * w - 0.2 * (s * e - e * s).norm_squared();
                let n = norm2(&m);
                assert!((n - q).abs() < 1e-13);
                assert!(n >= w / 10. - 1e-13 && n <= w / 2. + 1e-13);
                for k in 0..3 {
                    assert!((0..3).map(|l| m[k][l][l]).sum::<f64>().abs() < 1e-13)
                }
                let mut qs = vec![];
                let mut us = vec![];
                for v in sht.grid.ehat.chunks_exact(3) {
                    let n = Vector3::from_column_slice(v);
                    let h = n.x.hypot(n.y);
                    let p = Vector3::new(-n.y / h, n.x / h, 0.);
                    let t = p.cross(&n);
                    qs.push(2. / 3. * (t.dot(&(e * t)) - p.dot(&(e * p))));
                    us.push(4. / 3. * t.dot(&(e * p)));
                }
                let c = sht.from_stokes(&vec![0.; sht.len()], &qs, &us);
                let ec: [C64; 5] = std::array::from_fn(|m| -(c[1][m + 4] + c[2][m + 4]) * 0.5);
                let sc = quadratic_coefficients(&std::array::from_fn(|i| {
                    std::array::from_fn(|j| s[(i, j)])
                }));
                let bs = b3_source(&std::array::from_fn(|k| sc[k + 4]), &ec, 4.);
                let expected = 64. * std::f64::consts::PI * 16. / 189. * n;
                let diff = (bs.iter().map(|x| x.norm_sqr()).sum::<f64>() - expected).abs();
                worst = worst.max(diff);
                checked += 1;
            }
        }
    }
    eprintln!("cases={checked} norm_square_max_abs={worst:e}");
    assert!(worst < 1e-11);
}
