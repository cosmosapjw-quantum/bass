use rei_microphysics::*;

fn close(a: f64, b: f64) {
    assert!((a - b).abs() <= 5e-13 * b.abs(), "{a:e} != {b:e}");
}
fn table() -> PchipTable {
    PchipTable::new(
        vec![-2.0, 0.0, 2.0],
        [vec![0.0; 2], vec![0.0; 2], vec![0.25; 2], vec![-3.0, -2.5]],
    )
    .unwrap()
}
fn state() -> State {
    State {
        n_comoving_per_cmpc3: [1.0, 2.0, 3.0, 4.0],
        x_hii: 0.8,
        helium: [0.6, 0.3, 0.1],
        u_erg_per_cm3: 1e-12,
        gamma_hi_per_s: 1e-12,
    }
}
fn params() -> GroupParams {
    GroupParams {
        redshift: 3.0,
        n_h_proper_per_cm3: 1.2e-5,
        n_he_proper_per_cm3: 1e-6,
        hubble_per_s: 1e-16,
        sigma_hi_cm2: [6e-18, 2e-18, 1e-18, 2e-19],
        sigma_hei_cm2: [0.0, 7e-18, 3e-18, 5e-19],
        sigma_heii_cm2: [0.0, 0.0, 0.0, 1e-18],
        redshift_coeff: [1.0, 2.0, 3.0, 4.0],
        source_fraction: [0.4, 0.3, 0.2, 0.1],
        lowgroup_log_opacity: [table(), table()],
    }
}
#[test]
fn specified_mass_and_signed_examples() {
    assert_eq!(
        positive_mass_projection(&[1.0, 3.0], 8.0).unwrap(),
        vec![2.0, 6.0]
    );
    let s = signed_transfer_lift(-4.0, &[1.0, 3.0]).unwrap();
    assert_eq!(s.positive, vec![0.0, 0.0]);
    assert_eq!(s.negative, vec![1.0, 3.0]);
    assert_eq!(s.signed, vec![-1.0, -3.0]);
}
#[test]
fn zero_support_is_function_specific() {
    assert_eq!(
        positive_mass_projection(&[0.0, 0.0], 0.0).unwrap(),
        vec![0.0, 0.0]
    );
    assert_eq!(
        positive_mass_projection(&[], 0.0).unwrap(),
        Vec::<f64>::new()
    );
    assert!(positive_mass_projection(&[], 1.0).is_err());
    assert!(signed_transfer_lift(0.0, &[0.0, 0.0]).is_err());
    assert!(signed_transfer_lift(0.0, &[]).is_err());
}
#[test]
fn error_precedence_and_nonfinite_inputs() {
    assert_eq!(
        positive_mass_projection(&[f64::NAN], -1.0)
            .unwrap_err()
            .code(),
        "PRIOR_NOT_FINITE"
    );
    assert_eq!(
        positive_mass_projection(&[-1.0], -1.0).unwrap_err().code(),
        "INVALID_TOTAL"
    );
    assert_eq!(
        positive_mass_projection(&[-1.0], 0.0).unwrap_err().code(),
        "NEGATIVE_PRIOR"
    );
    assert_eq!(
        signed_transfer_lift(f64::NAN, &[0.0]).unwrap_err().code(),
        "INVALID_CONDITIONAL_MASS_PRIOR"
    );
    assert_eq!(
        signed_transfer_lift(f64::INFINITY, &[1.0])
            .unwrap_err()
            .code(),
        "NONFINITE_RATE"
    );
    assert!(positive_mass_projection(&[f64::INFINITY], 0.0).is_err());
}
#[test]
fn overflow_is_not_silently_renormalized() {
    assert_eq!(
        positive_mass_projection(&[1e308, 1e308], 1.0).unwrap(),
        vec![0.0, 0.0]
    );
    assert_eq!(
        signed_transfer_lift(-4.0, &[1e308, 1e308]).unwrap().signed,
        vec![0.0, 0.0]
    );
}
#[test]
fn pchip_knots_interior_and_domain() {
    let t = table();
    for (x, y) in [(-2.0, -3.0), (0.0, -2.5), (2.0, -2.0), (0.5, -2.375)] {
        assert_eq!(pchip_eval(&t, x).unwrap(), y);
    }
    assert!(matches!(
        pchip_eval(&t, 2.0 + f64::EPSILON * 2.0),
        Err(ForwardError::OutsideTableDomain { .. })
    ));
    assert!(pchip_eval(&t, -2.0 - f64::EPSILON * 2.0).is_err());
    assert!(pchip_eval(&t, f64::NAN).is_err());
    assert!(PchipTable::new(vec![0.0, 0.0], [vec![0.0], vec![0.0], vec![0.0], vec![0.0]]).is_err());
}
#[test]
fn pchip_uses_right_interval_at_interior_knot() {
    let t = PchipTable::new(
        vec![-2.0, 0.0, 2.0],
        [vec![0.0; 2], vec![0.0; 2], vec![0.0; 2], vec![17.0, 29.0]],
    )
    .unwrap();
    assert_eq!(pchip_eval(&t, 0.0).unwrap(), 29.0);
}
#[test]
fn transform_is_max_shifted_without_floors() {
    let mut z = [0.0; 9];
    z[5] = 1000.0;
    z[6] = 999.0;
    let s = transform_z_to_y(&z);
    assert_eq!(s.n_comoving_per_cmpc3, [1.0; 4]);
    assert_eq!(s.x_hii, 0.5);
    close(s.helium.iter().sum(), 1.0);
    z[5] = f64::NAN;
    assert!(transform_z_to_y(&z).helium.iter().all(|x| x.is_nan()));
}
#[test]
fn opacity_ownership_and_proper_units() {
    let s = state();
    let mut p = params();
    let a = opacity_cMpc_inv(&s, &p).unwrap();
    p.sigma_hi_cm2[0] *= 1e6;
    p.sigma_hi_cm2[1] *= 1e6;
    let b = opacity_cMpc_inv(&s, &p).unwrap();
    assert_eq!(a, b);
    p.sigma_hei_cm2[1] *= 2.0;
    let c = opacity_cMpc_inv(&s, &p).unwrap();
    close(
        c[1] - b[1],
        p.n_he_proper_per_cm3 * s.helium[0] * 7e-18 * MPC_CM / 4.0,
    );
    let alpha_si = (p.n_h_proper_per_cm3 * 1e6) * (1.0 - s.x_hii) * (p.sigma_hi_cm2[2] / 1e4);
    let he_si = (p.n_he_proper_per_cm3 * 1e6) * s.helium[0] * (p.sigma_hei_cm2[2] / 1e4);
    close(a[2], (alpha_si + he_si) * (MPC_CM / 100.0) / 4.0);
}
#[test]
fn gamma_has_one_comoving_factor_and_no_table_dependency() {
    let mut s = state();
    let mut p = params();
    let a = gamma_species(&s, &p);
    p.redshift = 0.0;
    let b = gamma_species(&s, &p);
    close(a.hi_per_s / b.hi_per_s, 64.0);
    s.gamma_hi_per_s = 1e-200;
    assert_eq!(gamma_species(&s, &p).hi_per_s, b.hi_per_s);
    let si = (C_LIGHT / 100.0) / (MPC_CM / 100.0).powi(3)
        * p.sigma_hi_cm2
            .iter()
            .zip(s.n_comoving_per_cmpc3)
            .map(|(sig, n)| sig / 1e4 * n)
            .sum::<f64>();
    close(b.hi_per_s, si);
}
#[test]
fn isolated_groups_and_no_emissivity() {
    let mut s = state();
    let p = params();
    for g in 0..4 {
        s.n_comoving_per_cmpc3 = [0.0; 4];
        s.n_comoving_per_cmpc3[g] = 1.0;
        let rhs = photon_rates(&s, &[0.0; 4], &p).unwrap();
        for (i, value) in rhs.iter().enumerate() {
            if i == g {
                assert!(*value < 0.0);
            } else if i + 1 == g {
                close(*value, p.hubble_per_s * p.redshift_coeff[g]);
            } else {
                assert_eq!(*value, 0.0);
            }
        }
    }
    s.n_comoving_per_cmpc3 = [0.0; 4];
    assert_eq!(
        photon_rates(&s, &[10.0; 4], &p).unwrap(),
        [4.0, 3.0, 2.0, 1.0]
    );
}
#[test]
fn redshift_internal_transfer_telescopes() {
    let s = state();
    let mut p = params();
    p.hubble_per_s = 0.1;
    let rhs = photon_rates(&s, &[0.0; 4], &p).unwrap();
    let k = opacity_cMpc_inv(&s, &p).unwrap();
    let total: f64 = (0..4)
        .map(|g| rhs[g] + C_LIGHT * 4.0 / MPC_CM * k[g] * s.n_comoving_per_cmpc3[g])
        .sum();
    close(total, -0.1);
}
#[test]
fn four_site_calls_do_not_share_state() {
    let p = params();
    let mut sites = Vec::new();
    for i in 0..4 {
        let mut s = state();
        s.x_hii = 0.1 + 0.2 * i as f64;
        sites.push(s);
    }
    let first: Vec<_> = sites
        .iter()
        .map(|s| opacity_cMpc_inv(s, &p).unwrap())
        .collect();
    for i in (0..4).rev() {
        assert_eq!(opacity_cMpc_inv(&sites[i], &p).unwrap(), first[i]);
    }
    assert_ne!(first[0][2], first[3][2]);
}
#[test]
fn registry_does_not_admit_missing_physical_sources() {
    assert_eq!(coverage::PORTED_FUNCTIONS.len(), 7);
    for key in ["P0_C8", "C9_CP0", "HOST4_H19", "HH_R10"] {
        assert!(matches!(
            coverage::require_physical_source(key),
            Err(ForwardError::MissingAuthority(_))
        ));
    }
}

// Additional fixed source-closeout witnesses. These do not change the C1 JSON
// inputs or its f64 tolerance. The cubic below tests evaluation, not fitting.
#[test]
fn full_cubic_on_nonuniform_knots_preserves_coefficient_layout() {
    // p(x)=x^3-2*x^2+x/2+1, expanded about each left knot.
    let t = PchipTable::new(
        vec![-2.0, 0.5, 4.0],
        [
            vec![1.0, 1.0],
            vec![-8.0, -0.5],
            vec![20.5, -0.75],
            vec![-16.0, 0.875],
        ],
    )
    .unwrap();
    for (x, y) in [
        (-2.0, -16.0),
        (-1.0, -2.5),
        (0.0, 1.0),
        (0.5, 0.875),
        (1.0, 0.5),
        (2.0, 2.0),
        (3.0, 11.5),
        (4.0, 35.0),
    ] {
        assert_eq!(pchip_eval(&t, x).unwrap(), y);
    }
}
#[test]
fn minimal_table_and_each_invalid_constructor_branch() {
    let t = PchipTable::new(vec![0.0, 2.0], [vec![1.0], vec![2.0], vec![3.0], vec![4.0]]).unwrap();
    assert_eq!(pchip_eval(&t, 1.0).unwrap(), 10.0);
    assert_eq!(pchip_eval(&t, 2.0).unwrap(), 26.0);
    for knots in [vec![], vec![0.0], vec![1.0, 0.0], vec![0.0, f64::INFINITY]] {
        assert_eq!(
            PchipTable::new(knots, [vec![0.0], vec![0.0], vec![0.0], vec![0.0]])
                .unwrap_err()
                .code(),
            "BAD_TABLE"
        );
    }
    assert_eq!(
        PchipTable::new(vec![0.0, 1.0], [vec![], vec![0.0], vec![0.0], vec![0.0]])
            .unwrap_err()
            .code(),
        "BAD_TABLE"
    );
    assert_eq!(
        PchipTable::new(
            vec![0.0, 1.0],
            [vec![0.0], vec![0.0], vec![f64::NAN], vec![0.0]]
        )
        .unwrap_err()
        .code(),
        "BAD_TABLE"
    );
}
#[test]
fn table_errors_propagate_to_opacity_and_photon_rates() {
    let mut s = state();
    let p = params();
    for gamma in [0.0, -1.0, f64::NAN, f64::INFINITY] {
        s.gamma_hi_per_s = gamma;
        assert_eq!(opacity_cMpc_inv(&s, &p).unwrap_err().code(), "NONFINITE_X");
        assert_eq!(
            photon_rates(&s, &[0.0; 4], &p).unwrap_err().code(),
            "NONFINITE_X"
        );
    }
    for gamma in [1e-100, 1e100] {
        s.gamma_hi_per_s = gamma;
        assert_eq!(
            opacity_cMpc_inv(&s, &p).unwrap_err().code(),
            "OUTSIDE_TABLE_DOMAIN"
        );
        assert_eq!(
            photon_rates(&s, &[0.0; 4], &p).unwrap_err().code(),
            "OUTSIDE_TABLE_DOMAIN"
        );
    }
}
#[test]
fn gamma_ignores_all_unused_state_and_thermochemistry_fields() {
    let mut s = state();
    let mut p = params();
    let before = gamma_species(&s, &p);
    s.x_hii = f64::NAN;
    s.helium = [f64::NAN; 3];
    s.u_erg_per_cm3 = f64::NAN;
    s.gamma_hi_per_s = f64::NAN;
    p.n_h_proper_per_cm3 = f64::NAN;
    p.n_he_proper_per_cm3 = f64::NAN;
    p.hubble_per_s = f64::NAN;
    p.redshift_coeff = [f64::NAN; 4];
    p.source_fraction = [f64::NAN; 4];
    // Construction requires valid tables; gamma must not evaluate either.
    let unrelated = PchipTable::new(
        vec![100.0, 200.0],
        [vec![3.0], vec![4.0], vec![5.0], vec![6.0]],
    )
    .unwrap();
    p.lowgroup_log_opacity = [unrelated.clone(), unrelated];
    let after = gamma_species(&s, &p);
    assert_eq!(before.hi_per_s, after.hi_per_s);
    assert_eq!(before.hei_per_s, after.hei_per_s);
    assert_eq!(before.heii_per_s, after.heii_per_s);
    assert_eq!(before.group_hi_per_s, after.group_hi_per_s);
}
#[test]
fn opacity_ignores_photon_count_and_thermal_energy() {
    let mut s = state();
    let p = params();
    let before = opacity_cMpc_inv(&s, &p).unwrap();
    s.n_comoving_per_cmpc3 = [f64::NAN; 4];
    s.u_erg_per_cm3 = f64::NAN;
    assert_eq!(before, opacity_cMpc_inv(&s, &p).unwrap());
}
#[test]
fn photon_emission_is_affine_and_not_renormalized() {
    let s = state();
    let p = params();
    let e = [1e-16, 2e-16, 3e-16, 4e-16];
    let zero = photon_rates(&s, &[0.0; 4], &p).unwrap();
    let added = photon_rates(&s, &e, &p).unwrap();
    for g in 0..4 {
        let expected = zero[g] + e[g] * p.source_fraction[g];
        let scale = zero[g].abs() + (e[g] * p.source_fraction[g]).abs();
        assert!((added[g] - expected).abs() <= 5e-13 * scale);
    }
}
#[test]
fn lift_zero_entries_and_signed_decomposition_preserve_locked_totals() {
    let p = [0.0, 2.0, 0.0, 6.0];
    assert_eq!(
        positive_mass_projection(&p, 16.0).unwrap(),
        vec![0.0, 4.0, 0.0, 12.0]
    );
    for rate in [-8.0, 0.0, 8.0] {
        let s = signed_transfer_lift(rate, &p).unwrap();
        assert_eq!(s.signed.iter().sum::<f64>(), rate);
        for i in 0..p.len() {
            assert_eq!(s.positive[i] - s.negative[i], s.signed[i]);
            assert!(s.positive[i] >= 0.0 && s.negative[i] >= 0.0);
            assert_eq!(s.positive[i] * s.negative[i], 0.0);
        }
    }
}
#[test]
fn transform_preserves_extreme_classifications_without_floor() {
    let mut z = [0.0; 9];
    z[0] = -1000.0;
    z[1] = 1000.0;
    z[4] = f64::NEG_INFINITY;
    z[5] = f64::NEG_INFINITY;
    z[6] = f64::NEG_INFINITY;
    z[7] = -1000.0;
    z[8] = f64::INFINITY;
    let s = transform_z_to_y(&z);
    assert_eq!(s.n_comoving_per_cmpc3[0], 0.0);
    assert_eq!(s.n_comoving_per_cmpc3[1], f64::INFINITY);
    assert_eq!(s.x_hii, 0.0);
    assert_eq!(s.helium, [1.0, 0.0, 0.0]);
    assert_eq!(s.u_erg_per_cm3, 0.0);
    assert_eq!(s.gamma_hi_per_s, f64::INFINITY);
}

#[test]
fn transform_uses_rust_binary64_underflow() {
    let mut z = [0.0; 9];
    for (exponent, expected) in [
        (0.0, 1.0),
        (-708.0, (-708.0_f64).exp()),
        (-709.0, (-709.0_f64).exp()),
        (-745.0, f64::from_bits(1)),
        (-746.0, 0.0),
    ] {
        z[0] = exponent;
        let actual = transform_z_to_y(&z).n_comoving_per_cmpc3[0];
        assert_eq!(actual, expected, "exp({exponent})");
    }
    z[0] = -708.0;
    assert!(transform_z_to_y(&z).n_comoving_per_cmpc3[0] >= f64::MIN_POSITIVE);
    z[0] = -709.0;
    let subnormal = transform_z_to_y(&z).n_comoving_per_cmpc3[0];
    assert!(subnormal > 0.0 && subnormal < f64::MIN_POSITIVE);
    z[0] = -745.0;
    assert_eq!(transform_z_to_y(&z).n_comoving_per_cmpc3[0].to_bits(), 1);
}

#[test]
fn transform_finite_invariants_and_nonfinite_contract() {
    let z = [0.0, -708.0, -709.0, -745.0, 0.0, 1.0, -2.0, 0.0, -708.0];
    let s = transform_z_to_y(&z);
    assert!(s.n_comoving_per_cmpc3.iter().all(|v| *v > 0.0));
    assert!(s.u_erg_per_cm3 > 0.0 && s.gamma_hi_per_s > 0.0);
    assert!(s.x_hii > 0.0 && s.x_hii < 1.0);
    assert!(s.helium.iter().all(|v| *v >= 0.0 && *v <= 1.0));
    close(s.helium.iter().sum(), 1.0);
    let mut edge = [0.0; 9];
    edge[4] = 1000.0;
    assert_eq!(transform_z_to_y(&edge).x_hii, 1.0);
    edge[4] = -1000.0;
    assert_eq!(transform_z_to_y(&edge).x_hii, 0.0);
    edge[0] = f64::NAN;
    assert!(transform_z_to_y(&edge).n_comoving_per_cmpc3[0].is_nan());
    edge[0] = f64::INFINITY;
    assert_eq!(
        transform_z_to_y(&edge).n_comoving_per_cmpc3[0],
        f64::INFINITY
    );
    edge[0] = f64::NEG_INFINITY;
    assert_eq!(transform_z_to_y(&edge).n_comoving_per_cmpc3[0], 0.0);
    edge[5] = f64::INFINITY;
    assert!(transform_z_to_y(&edge).helium.iter().all(|v| v.is_nan()));
}

#[test]
fn high_group_atomic_owners_remain_explicit() {
    let s = state();
    let mut p = params();
    let before = opacity_cMpc_inv(&s, &p).unwrap();
    let factor = MPC_CM / (1.0 + p.redshift);
    p.sigma_hi_cm2[2] += 2e-18;
    p.sigma_heii_cm2[3] += 3e-18;
    let after = opacity_cMpc_inv(&s, &p).unwrap();
    assert_eq!(after[0], before[0]);
    assert_eq!(after[1], before[1]);
    close(
        after[2] - before[2],
        p.n_h_proper_per_cm3 * (1.0 - s.x_hii) * 2e-18 * factor,
    );
    close(
        after[3] - before[3],
        p.n_he_proper_per_cm3 * s.helium[1] * 3e-18 * factor,
    );
}

#[test]
fn gamma_group_species_have_separate_atomic_accumulations() {
    let mut s = state();
    let mut p = params();
    p.redshift = 0.0;
    let prefactor = C_LIGHT / MPC_CM.powi(3);
    for g in 0..4 {
        s.n_comoving_per_cmpc3 = [0.0; 4];
        s.n_comoving_per_cmpc3[g] = 2.0;
        let rates = gamma_species(&s, &p);
        close(rates.hi_per_s, prefactor * p.sigma_hi_cm2[g] * 2.0);
        close(rates.hei_per_s, prefactor * p.sigma_hei_cm2[g] * 2.0);
        close(rates.heii_per_s, prefactor * p.sigma_heii_cm2[g] * 2.0);
        for i in 0..4 {
            if i == g {
                close(rates.group_hi_per_s[i], rates.hi_per_s);
            } else {
                assert_eq!(rates.group_hi_per_s[i], 0.0);
            }
        }
    }
}

#[test]
fn finite_projection_totals_and_signed_reconstruction() {
    let prior = [0.0, 1.0, 2.0, 3.0];
    for total in [0.0, 6.0, 12.0] {
        let projected = positive_mass_projection(&prior, total).unwrap();
        close(projected.iter().sum(), total);
        assert_eq!(projected[0], 0.0);
    }
    for rate in [-12.0, 0.0, 12.0] {
        let lift = signed_transfer_lift(rate, &prior).unwrap();
        close(lift.signed.iter().sum(), rate);
        for i in 0..prior.len() {
            assert_eq!(lift.positive[i] - lift.negative[i], lift.signed[i]);
        }
    }
}
