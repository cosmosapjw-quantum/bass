use bianchi_rustcore::kinetic::{b3_coupling::b3_source, spin_sht::C64};
#[test]
fn coefficient_and_antisymmetry() {
    let mut s = [C64::new(0., 0.); 5];
    let mut e = s;
    s[4] = C64::new(1., 0.);
    e[3] = C64::new(1., 0.);
    let b = b3_source(&s, &e, 4.);
    assert!((b[6].im - 5. / (7. * std::f64::consts::PI).sqrt()).abs() < 1e-14);
    let r = b3_source(&e, &s, 4.);
    for k in 0..7 {
        assert!((b[k] + r[k]).norm() < 1e-14);
    }
}
#[test]
fn all_stf_pairs_native_and_direct_projection() {
    use bianchi_rustcore::{
        geom::lie::{photon_potentials, quadratic_coefficients},
        kinetic::{
            lie_hierarchy::{lie_data, LieHierarchy},
            lie_history::RayNode,
            memory_mixture::stf_matrix,
            spin_sht::{index, SpinSht},
        },
    };
    let h = LieHierarchy::new(5, true, 4.).unwrap();
    let sht = SpinSht::new(5, 12, 24).unwrap();
    let mut worst = 0_f64;
    let mut norm = 0_f64;
    let mut diag = 0_f64;
    for i in 0..5 {
        for j in 0..5 {
            let s = stf_matrix(std::array::from_fn(|k| if i == k { 1. } else { 0. }));
            let e = stf_matrix(std::array::from_fn(|k| if j == k { 1. } else { 0. }));
            let mut q = vec![];
            let mut u = vec![];
            let mut sv = vec![];
            for v in sht.grid.ehat.chunks_exact(3) {
                let n = nalgebra::Vector3::from_column_slice(v);
                let r = n.x.hypot(n.y);
                let p = nalgebra::Vector3::new(-n.y / r, n.x / r, 0.);
                let t = p.cross(&n);
                q.push((2. / 3.) * (t.dot(&(e * t)) - p.dot(&(e * p))));
                u.push((4. / 3.) * t.dot(&(e * p)));
                sv.push(n.dot(&(s * n)));
            }
            let z = vec![0.; sht.len()];
            let a = sht.from_stokes(&z, &q, &u);
            let mut y = h.zero_state();
            let mut ee = [C64::new(0., 0.); 5];
            for m in -2..=2 {
                let k = index(2, m);
                ee[(m + 2) as usize] = -(a[1][k] + a[2][k]) * 0.5;
                y[1][k] = -ee[(m + 2) as usize];
                y[2][k] = y[1][k];
            }
            let rows = std::array::from_fn(|i| std::array::from_fn(|j| s[(i, j)]));
            let ss = quadratic_coefficients(&rows);
            let sc = std::array::from_fn(|k| ss[k + 4]);
            let b = b3_source(&sc, &ee, 4.);
            let node = RayNode {
                shear: rows,
                ..Default::default()
            };
            let mut r = h.zero_state();
            h.rhs(&photon_potentials(&lie_data(&node)), &y, &mut r);
            let pp = sht.from_stokes(
                &z,
                &q.iter()
                    .zip(&sv)
                    .map(|(a, b)| -4. * a * b)
                    .collect::<Vec<_>>(),
                &u.iter()
                    .zip(&sv)
                    .map(|(a, b)| -4. * a * b)
                    .collect::<Vec<_>>(),
            );
            for m in -3..=3 {
                let k = index(3, m);
                let got = C64::new(0., 0.5) * (r[1][k] - r[2][k]);
                let ref0 = C64::new(0., 0.5) * (pp[1][k] - pp[2][k]);
                let v = b[(m + 3) as usize];
                worst = worst.max((got - v).norm()).max((ref0 - v).norm());
                norm = norm.max(v.norm());
                if i == 0 && j == 1 {
                    diag = diag.max(v.norm())
                }
                if i == j {
                    assert!(v.norm() < 1e-13)
                }
            }
        }
    }
    eprintln!(
        "basis pairs=25 max_abs={worst:e} max_source={norm:e} commuting_nonproportional={diag:e}"
    );
    assert!(worst < 1e-12 && diag > 0.1);
}
