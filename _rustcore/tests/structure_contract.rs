//! Dossier I §8.1 and V §14.4: independently fixed analytic checks.
use bianchi_rustcore::kinetic::realizability::{check_moments, MomentKind};
use bianchi_rustcore::microphysics::population::FrozenPopulation;
fn close(a: f64, b: f64, t: f64) {
    assert!((a - b).abs() <= t, "{a:e} != {b:e}");
}
#[test]
fn isotropic_beam_vacuum_and_unphysical_flux() {
    let iso = check_moments(
        3.0,
        [0.0; 3],
        [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
        MomentKind::Photons,
        1e-12,
    )
    .unwrap();
    assert!(iso.admissible);
    let beam = check_moments(
        2.0,
        [2.0, 0.0, 0.0],
        [[2.0, 0.0, 0.0], [0.0; 3], [0.0; 3]],
        MomentKind::Photons,
        1e-12,
    )
    .unwrap();
    assert!(beam.admissible);
    assert!(
        check_moments(
            0.0,
            [0.0; 3],
            [[0.0; 3]; 3],
            MomentKind::MassiveOrMixed,
            1e-12
        )
        .unwrap()
        .admissible
    );
    assert!(
        !check_moments(
            0.0,
            [1e-100, 0.0, 0.0],
            [[0.0; 3]; 3],
            MomentKind::MassiveOrMixed,
            1e-12
        )
        .unwrap()
        .admissible
    );
    assert!(
        !check_moments(
            1.0,
            [0.1, 0.0, 0.0],
            [[0.0; 3]; 3],
            MomentKind::MassiveOrMixed,
            1e-12
        )
        .unwrap()
        .admissible
    );
    assert!(
        !check_moments(
            1.0,
            [0.0; 3],
            [[0.4, 0.0, 0.0], [0.0, 0.4, 0.0], [0.0, 0.0, 0.4]],
            MomentKind::MassiveOrMixed,
            1e-12
        )
        .unwrap()
        .admissible
    );
    assert!(
        !check_moments(1.0, [0.0; 3], [[0.0; 3]; 3], MomentKind::Photons, 1e-12)
            .unwrap()
            .admissible
    );
}
#[test]
fn positive_particle_sums_rotation_and_scale() {
    let mut q = [0.0; 3];
    let mut s = [[0.0; 3]; 3];
    let rho = 4.0;
    for (w, v) in [
        (1.0, [0.6, 0.8, 0.0]),
        (2.0, [-0.8, 0.6, 0.0]),
        (1.0, [0.0, 0.0, 1.0]),
    ] {
        for i in 0..3 {
            q[i] += w * v[i];
            for j in 0..3 {
                s[i][j] += w * v[i] * v[j];
            }
        }
    }
    assert!(
        check_moments(rho, q, s, MomentKind::Photons, 1e-12)
            .unwrap()
            .admissible
    );
    // Orthogonal cyclic rotation changes components but not the necessary verdict.
    let perm = [2, 0, 1];
    let mut qr = [0.0; 3];
    let mut sr = [[0.0; 3]; 3];
    for i in 0..3 {
        qr[i] = q[perm[i]];
        for j in 0..3 {
            sr[i][j] = s[perm[i]][perm[j]];
        }
    }
    for f in [1e-200, 1.0, 1e200] {
        let mut a = qr;
        let mut b = sr;
        for i in 0..3 {
            a[i] *= f;
            for value in &mut b[i] {
                *value *= f;
            }
        }
        assert!(
            check_moments(rho * f, a, b, MomentKind::Photons, 1e-12)
                .unwrap()
                .admissible
        );
    }
}

#[test]
fn unsupported_weighted_underflow_is_rejected_instead_of_erasing_equilibrium() {
    use bianchi_rustcore::microphysics::population::PopulationError;
    let u = f64::from_bits(1);
    let generator = FrozenPopulation::new(&[u, u], &[vec![0.0, 1.0], vec![1.0, 0.0]]).unwrap();
    for p in [[1.0, 1.0], [0.25, 0.25]] {
        assert_eq!(
            generator.advance(&p, 1.0, 2).unwrap_err(),
            PopulationError::WeightedStateUnderflow
        );
    }
    assert_eq!(
        generator.advance(&[1.0, 1.0], 0.0, 2).unwrap().populations,
        vec![1.0, 1.0]
    );
}
#[test]
fn moment_bad_domain_and_asymmetry() {
    assert!(check_moments(
        f64::NAN,
        [0.0; 3],
        [[0.0; 3]; 3],
        MomentKind::Photons,
        1e-12
    )
    .is_err());
    assert!(check_moments(1.0, [0.0; 3], [[0.0; 3]; 3], MomentKind::Photons, -1.0).is_err());
    assert!(
        !check_moments(
            -1.0,
            [0.0; 3],
            [[0.0; 3]; 3],
            MomentKind::MassiveOrMixed,
            1e-12
        )
        .unwrap()
        .admissible
    );
    assert!(
        !check_moments(
            1.0,
            [0.0; 3],
            [[0.3, 0.2, 0.0], [0.0, 0.3, 0.0], [0.0, 0.0, 0.4]],
            MomentKind::Photons,
            1e-12
        )
        .unwrap()
        .admissible
    );
}
// Input rates are off-diagonal rates of G in weighted-population coordinates.
// G_ij is transfer from j to i; diagonal entries of the supplied rate table are zero.
#[test]
fn population_weighted_inventory_stationary_and_zero_generator() {
    let g = FrozenPopulation::new(&[2.0, 1.0], &[vec![0.0, 3.0], vec![1.0, 0.0]]).unwrap();
    let a = g.advance(&[0.5, 0.0], 0.7, 24).unwrap();
    assert!(a.populations.iter().all(|x| *x >= 0.0));
    close(2.0 * a.populations[0] + a.populations[1], 1.0, 2e-14);
    let eq = g.advance(&[1.5, 1.0], 1.0, 32).unwrap();
    close(eq.populations[0], 1.5, 2e-14);
    close(eq.populations[1], 1.0, 2e-14);
    let zero = FrozenPopulation::new(&[2.0, 1.0], &[vec![0.0; 2], vec![0.0; 2]]).unwrap();
    let z = zero.advance(&[0.25, 0.5], 1e100, 0).unwrap();
    assert_eq!(z.populations, vec![0.25, 0.5]);
    assert_eq!(z.weighted_l1_error_bound, 0.0);
    assert_eq!(
        g.advance(&[0.5, 0.0], 0.0, 5).unwrap().populations,
        vec![0.5, 0.0]
    );
}
#[test]
fn population_two_state_analytic_error_matches_poisson_bound() {
    let g = FrozenPopulation::new(&[2.0, 1.0], &[vec![0.0, 3.0], vec![1.0, 0.0]]).unwrap();
    let h = 0.5;
    let weighted0 = 0.75 + 0.25 * (-4.0_f64 * h).exp();
    let mut previous = 2.0;
    for m in [0, 1, 3, 8, 24] {
        let a = g.advance(&[0.5, 0.0], h, m).unwrap();
        let err = (2.0 * a.populations[0] - weighted0).abs()
            + (a.populations[1] - (1.0 - weighted0)).abs();
        assert!(err <= a.weighted_l1_error_bound + 3e-14);
        assert!(a.weighted_l1_error_bound <= previous + 1e-14);
        previous = a.weighted_l1_error_bound;
    }
    let a = g.advance(&[0.5, 0.0], h, 24).unwrap();
    close(2.0 * a.populations[0], weighted0, 2e-14);
    // m=0 returns identity; true bound is 2 P(Poisson(1.5)>0) times initial weighted mass.
    let a = g.advance(&[0.5, 0.0], h, 0).unwrap();
    assert_eq!(a.populations, vec![0.5, 0.0]);
    close(a.weighted_l1_error_bound, 2.0 * -(-1.5_f64).exp_m1(), 2e-14);
}
#[test]
fn population_bad_domains_are_typed_errors() {
    assert!(FrozenPopulation::new(&[], &[]).is_err());
    assert!(FrozenPopulation::new(&[0.0], &[vec![0.0]]).is_err());
    assert!(FrozenPopulation::new(&[1.0, 1.0], &[vec![0.0, -1.0], vec![0.0, 0.0]]).is_err());
    assert!(FrozenPopulation::new(&[1.0], &[vec![1.0]]).is_err());
    assert!(FrozenPopulation::new(&[1.0, 1.0], &[vec![0.0]]).is_err());
    let g = FrozenPopulation::new(&[1.0, 1.0], &[vec![0.0, 1.0], vec![1.0, 0.0]]).unwrap();
    assert!(g.advance(&[-1.0, 1.0], 1.0, 4).is_err());
    assert!(g.advance(&[1.0], 1.0, 4).is_err());
    assert!(g.advance(&[1.0, 0.0], -1.0, 4).is_err());
    assert!(g.advance(&[1.0, 0.0], f64::NAN, 4).is_err());
    assert!(g.advance(&[1.0, 0.0], 65.0, 4).is_err());
    assert!(g.advance(&[1.0, 0.0], 1.0, 1025).is_err());
}
