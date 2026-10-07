// Exact function bodies selected from actual BASS microphysics/tests.rs.
use bianchi_rustcore::microphysics::rei;
use rei_microphysics::{ForwardError,GroupParams,PchipTable,State,C_LIGHT,MPC_CM};
fn close(a: f64, b: f64) {
    assert!(
        (a - b).abs() < 1e-11 * (1.0 + a.abs() + b.abs()),
        "{a:e} != {b:e}"
    );
}

fn rei_table() -> PchipTable {
    PchipTable::new(
        vec![-2.0, 0.0, 2.0],
        [vec![0.0; 2], vec![0.0; 2], vec![0.25; 2], vec![-3.0, -2.5]],
    )
    .unwrap()
}

fn rei_state() -> State {
    State {
        n_comoving_per_cmpc3: [1.0, 2.0, 3.0, 4.0],
        x_hii: 0.8,
        helium: [0.6, 0.3, 0.1],
        u_erg_per_cm3: 1e-12,
        gamma_hi_per_s: 1e-12,
    }
}

fn rei_params() -> GroupParams {
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
        lowgroup_log_opacity: [rei_table(), rei_table()],
    }
}

#[test]
fn rei_canonical_extremes_tables_and_ownership() {
    let normal = rei::transform(&[0.0; 9]);
    close(normal.helium.iter().sum(), 1.0);
    let mut z = [0.0; 9];
    z[0] = -745.0;
    assert_eq!(
        rei::transform(&z).n_comoving_per_cmpc3[0],
        f64::from_bits(1)
    );
    let table = rei_table();
    close(rei::pchip(&table, 0.0).unwrap(), -2.5);
    close(rei::pchip(&table, 0.5).unwrap(), -2.375);
    assert!(matches!(
        rei::pchip(&table, 2.1),
        Err(ForwardError::OutsideTableDomain { .. })
    ));
    let state = rei_state();
    let mut params = rei_params();
    let a = rei::opacity(&state, &params).unwrap();
    params.sigma_hi_cm2[0] *= 100.0;
    params.sigma_hi_cm2[1] *= 100.0;
    assert_eq!(rei::opacity(&state, &params).unwrap(), a);
    params.lowgroup_log_opacity[0] =
        PchipTable::new(vec![1.0, 2.0], [vec![0.0], vec![0.0], vec![0.0], vec![0.0]]).unwrap();
    assert!(matches!(
        rei::opacity(&state, &params),
        Err(ForwardError::OutsideTableDomain { .. })
    ));
}

#[test]
fn rei_groups_telescoping_gamma_projection_and_negative_transfer() {
    let state = rei_state();
    let params = rei_params();
    let source = rei::photon_source(&state, &[1.0; 4], &params).unwrap();
    let opacity = rei::opacity(&state, &params).unwrap();
    let attenuation: f64 = (0..4)
        .map(|g| {
            C_LIGHT * (1.0 + params.redshift) / MPC_CM * opacity[g] * state.n_comoving_per_cmpc3[g]
        })
        .sum();
    let redshift_edge =
        params.hubble_per_s * params.redshift_coeff[0] * state.n_comoving_per_cmpc3[0];
    close(source.iter().sum(), 1.0 - attenuation - redshift_edge);
    let gamma = rei::gamma_species(&state, &params);
    close(gamma.hi_per_s, gamma.group_hi_per_s.iter().sum());
    assert!(gamma.hei_per_s > 0.0 && gamma.heii_per_s > 0.0);
    assert_eq!(
        rei::positive_projection(&[1.0, 3.0], 8.0).unwrap(),
        vec![2.0, 6.0]
    );
    let lift = rei::signed_transfer(-4.0, &[1.0, 3.0]).unwrap();
    assert_eq!(lift.signed, vec![-1.0, -3.0]);
}

#[test]
fn exact_git_dependency_identity_is_frozen_in_manifest_and_lock() {
    const REC: &str = "d3cc6e0120061f113d28e7a3a55a2e3dd561e81e";
    const REI: &str = "41e4592aa494b48929dcd23fc8504c169a98a908";
    let manifest = include_str!("../../bass/_rustcore/Cargo.toml");
    let lock = include_str!("../../bass/_rustcore/Cargo.lock");
    for sha in [REC, REI] {
        assert!(manifest.contains(&format!("rev = \"{sha}\"")));
        assert!(lock.contains(sha));
    }
    assert!(!manifest.contains("branch ="));
}
