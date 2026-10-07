//! Frozen Host acceptance: Dossier I §§5.1, 6.2–6.6, geometric length units.
use bianchi_rustcore::geom::exceptional_initial::{CauchyData, ExceptionalGeometry, Expansion};
use bianchi_rustcore::geom::group::BianchiGroup;

const TOL: f64 = 2e-13;
fn close(a: f64, b: f64) {
    assert!(
        (a - b).abs() <= 2e-12 * a.abs().max(b.abs()).max(1.0),
        "{a} != {b}"
    );
}
fn vacuum(in_plane: [f64; 3]) -> CauchyData {
    CauchyData {
        in_plane,
        flux: [0.0; 3],
        kappa: 1.0,
        rho: 0.0,
        lambda: 0.0,
    }
}
#[test]
fn both_zero_row_charts_check_the_other_equation() {
    let g = ExceptionalGeometry::new(1.0, 0.0, 3.0, 0.0, TOL).unwrap();
    let s = g.solve_transverse([3.0, 0.0], 2.0, 4.0).unwrap();
    close(s.shear[0], 1.0);
    close(s.shear[1], 4.0);
    assert!(g.solve_transverse([0.0, 1.0], 1.0, 0.0).is_err());
    let g = ExceptionalGeometry::new(1.0, 0.0, -3.0, 0.0, TOL).unwrap();
    let s = g.solve_transverse([0.0, 3.0], 2.0, 4.0).unwrap();
    close(s.shear[0], 4.0);
    close(s.shear[1], 1.0);
    assert!(g.solve_transverse([1.0, 0.0], 1.0, 0.0).is_err());
}
#[test]
fn orthogonal_solution_projectors_and_free_amplitude() {
    let g = ExceptionalGeometry::new(1.0, 2.0, 3.0, 0.0, TOL).unwrap();
    let s = g.solve_transverse([3.0, -1.0], 2.0, 4.0).unwrap();
    close(s.shear[0], 1.0);
    close(s.shear[1], 4.0);
    close(s.shear.iter().map(|v| v * v).sum(), 17.0);
    for (m, want) in [
        (s.image_projector, [[0.9, -0.3], [-0.3, 0.1]]),
        (s.row_projector, [[1.0, 0.0], [0.0, 0.0]]),
    ] {
        for i in 0..2 {
            for j in 0..2 {
                close(m[i][j], want[i][j]);
            }
        }
    }
    close(s.kernel[0], 0.0);
    close(s.kernel[1], 1.0);
    close(s.range_residual, 0.0);
    for v in s.constraint_residual {
        close(v, 0.0);
    }
    assert!(g.solve_transverse([3.0, 1.0], 2.0, 0.0).is_err());
}
#[test]
fn vacuum_family_satisfies_all_constraints_and_curvature() {
    let g = ExceptionalGeometry::new(1.0, 2.0, 3.0, 0.0, TOL).unwrap();
    let group = BianchiGroup::new([0.0, 2.0, 0.0, 0.0, 0.0, 3.0], [1.0, 0.0, 0.0]);
    for u in [-2.0, 0.0, 1.5] {
        for v in [-0.3, 0.0, 2.0] {
            for w in [-1.0, 0.0, 0.7] {
                let data = vacuum([w, v / 3.0, v]);
                let r = g.initial_data(data, u, Expansion::Expanding).unwrap();
                let h2 = (13.0 + u * u + (w + v / 6.0).powi(2) + 13.0 * v * v / 12.0) / 3.0;
                close(r.hubble * r.hubble, h2);
                close(r.scalar_curvature, -26.0);
                close(r.scalar_curvature, -6.0 * group.curvature().0);
                let s = r.shear;
                close(s[0][0] + s[1][1] + s[2][2], 0.0);
                close(
                    -3.0 * s[0][0] + 3.0 * (s[0][0] + 2.0 * s[1][1]) - 2.0 * s[1][2],
                    0.0,
                );
                close(-6.0 * s[0][1], 0.0);
                close(2.0 * s[0][1], 0.0);
                let norm: f64 = s.iter().flatten().map(|x| x * x).sum();
                close(6.0 * r.hubble * r.hubble + r.scalar_curvature - norm, 0.0);
                for residual in r.momentum_residual {
                    close(residual, 0.0);
                }
                close(r.hamiltonian_residual, 0.0);
                // Positive budgets avoid a floating cancellation at the exact boundary.
                if u != 0.0 {
                    close(g.amplitude_budget(data, r.hubble).unwrap(), u * u);
                }
                let c = g.initial_data(data, -u, Expansion::Contracting).unwrap();
                close(c.hubble, -r.hubble);
                close(c.shear[0][2], -r.shear[0][2]);
            }
        }
    }
}
#[test]
fn amplitude_budget_and_longitudinal_constraint_are_independent() {
    let g = ExceptionalGeometry::new(1.0, 0.0, 3.0, 0.0, TOL).unwrap();
    let d = vacuum([0.0; 3]);
    close(g.amplitude_budget(d, 2.0).unwrap(), 0.0);
    close(g.amplitude_budget(d, 3.0).unwrap(), 15.0);
    close(g.amplitude_budget(d, -3.0).unwrap(), 15.0);
    assert!(g.amplitude_budget(d, 1.0).is_err());
    assert!(g
        .initial_data(vacuum([0.0, 1.0, 0.0]), 0.0, Expansion::Expanding)
        .is_err());
    assert!(g.amplitude_budget(vacuum([0.0, 1.0, 0.0]), 3.0).is_err());
    let mut m = vacuum([0.0, 1.0, 0.0]);
    m.flux = [-3.0, 3.0, 0.0];
    m.kappa = 2.0;
    m.rho = 4.0;
    let r = g.initial_data(m, 0.5, Expansion::Expanding).unwrap();
    close(r.shear[0][1], 1.0);
    close(g.amplitude_budget(m, r.hubble).unwrap(), 0.25);
    let mut d = d;
    d.lambda = -20.0;
    assert!(g.initial_data(d, 0.0, Expansion::Expanding).is_err());
}
#[test]
fn geometry_scaling_and_transverse_rotation_preserve_minimum_norm() {
    for scale in [1e-100, 1e-20, 1.0, 1e20, 1e100] {
        for theta in [0.0_f64, 0.3, 1.0, 2.0] {
            let (s, c) = theta.sin_cos();
            // n' = R n R^T, q'=R q; R=[[c,-s],[s,c]].
            let b = (2.0 * c * c - 6.0 * c * s) * scale;
            let d = (2.0 * s * s + 6.0 * c * s) * scale;
            let n23 = (2.0 * c * s + 3.0 * (c * c - s * s)) * scale;
            let g = ExceptionalGeometry::new(scale, b, n23, d, TOL).unwrap();
            let q = [(3.0 * c + s) * scale * scale, (3.0 * s - c) * scale * scale];
            let r = g.solve_transverse(q, 2.0, 0.0).unwrap();
            close(r.shear[0] / scale, c);
            close(r.shear[1] / scale, s);
            close(r.shear[0].hypot(r.shear[1]) / scale, 1.0);
        }
    }
}
#[test]
fn invalid_and_unrepresentable_inputs_fail_explicitly() {
    for (a, b, c, d, t) in [
        (0.0, 0.0, 0.0, 0.0, TOL),
        (1.0, 1.0, 0.0, 1.0, TOL),
        (f64::NAN, 0.0, 3.0, 0.0, TOL),
        (1.0, 0.0, 3.0, 0.0, -1.0),
        (1.0, 0.0, 3.0, 0.0, 1e-3),
    ] {
        assert!(ExceptionalGeometry::new(a, b, c, d, t).is_err());
    }
    let g = ExceptionalGeometry::new(1.0, 0.0, 3.0, 0.0, TOL).unwrap();
    for k in [0.0, -1.0, f64::INFINITY] {
        assert!(g.solve_transverse([0.0; 2], k, 0.0).is_err());
    }
    assert!(g.solve_transverse([f64::NAN, 0.0], 1.0, 0.0).is_err());
    assert!(g.solve_transverse([0.0; 2], 1.0, f64::NAN).is_err());
    // Underflow cannot hide flux outside the range.
    assert!(g
        .solve_transverse([0.0, f64::from_bits(1)], f64::from_bits(1), 0.0)
        .is_err());
    assert!(g.solve_transverse([f64::MAX, 0.0], f64::MAX, 0.0).is_err());
    let mut d = vacuum([0.0; 3]);
    d.rho = -1.0;
    assert!(g.initial_data(d, 0.0, Expansion::Expanding).is_err());
    assert!(g.amplitude_budget(vacuum([0.0; 3]), f64::NAN).is_err());
}
