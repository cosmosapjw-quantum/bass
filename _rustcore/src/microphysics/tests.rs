use super::{
    frame::{FrameError, MaterialFrame},
    rec::{self, RecHostError},
    rei,
};
use rec_microphysics::{
    coverage::{d86_w, CoverageError},
    he_singlet::{
        BoundBoundChannel, CoverageState, Mat2, Mat3, PBoundFreeTable, PairInput, SBoundFreeTable,
        SourceState, WeightedBbMode,
    },
    ledger::{assemble_he_event_ledger, ChannelRates, HeEnergies},
};
use rei_microphysics::{ForwardError, GroupParams, PchipTable, State, C_LIGHT, MPC_CM};

fn close(a: f64, b: f64) {
    assert!(
        (a - b).abs() < 1e-11 * (1.0 + a.abs() + b.abs()),
        "{a:e} != {b:e}"
    );
}
fn wp() -> Mat3 {
    Mat3::scalar(1.0)
}
fn screen() -> [[f64; 2]; 3] {
    [[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]]
}
fn rec_state() -> SourceState {
    SourceState::simple(2.0, 0.5, wp(), 1.0, 1.0, 9000.0).unwrap()
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
fn material_frame_and_two_clocks_are_distinct() {
    let zero = MaterialFrame::new([0.0; 3]).unwrap();
    close(zero.doppler([1.0, 0.0, 0.0]).unwrap(), 1.0);
    let tilted = MaterialFrame::new([0.6, 0.0, 0.0]).unwrap();
    let d1 = tilted.doppler([1.0, 0.0, 0.0]).unwrap();
    let d2 = tilted.doppler([-1.0, 0.0, 0.0]).unwrap();
    close(d1, 0.5);
    close(d2, 2.0);
    assert_ne!(d1, 1.0 / tilted.gamma());
    close(
        tilted.material_energy_ev(20.0, [1.0, 0.0, 0.0]).unwrap(),
        10.0,
    );
    close(
        tilted
            .photon_normal_time_source(3.0, [1.0, 0.0, 0.0])
            .unwrap(),
        1.5,
    );
    close(tilted.atomic_normal_time_source(3.0).unwrap(), 2.4);
    close(
        tilted
            .pair_material_fraction([10.0, 5.0], [[1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]], 15.0)
            .unwrap(),
        1.0 / 3.0,
    );
    assert!(matches!(
        tilted.pair_material_fraction([10.0, 5.0], [[1.0, 0.0, 0.0], [1.0, 0.0, 0.0]], 15.0),
        Err(FrameError::PairEnergyMismatch { .. })
    ));
    // kinetic::comoving::Frame has a grid matrix, not a velocity.
    let grid = crate::kinetic::comoving::Frame::identity();
    assert_eq!(grid.apply(&[1.0, 0.0, 0.0]), [1.0, 0.0, 0.0]);
}

#[test]
fn rec_bb_stimulation_and_signed_ledger() {
    let modes = [WeightedBbMode {
        v: screen(),
        f: Mat2::zero(),
        weight_sr: 1.0,
    }];
    let vacuum = rec::bound_bound(
        MaterialFrame::new([0.0; 3]).unwrap(),
        &[[1.0, 0.0, 0.0]],
        BoundBoundChannel::He584,
        0.0,
        wp(),
        &modes,
    )
    .unwrap();
    assert!(vacuum.material.atomic_b.trace().re < 0.0);
    let stimulated = [WeightedBbMode {
        f: Mat2::scalar(2.0),
        ..modes[0]
    }];
    let inverse = rec::bound_bound(
        MaterialFrame::new([0.6, 0.0, 0.0]).unwrap(),
        &[[1.0, 0.0, 0.0]],
        BoundBoundChannel::He584,
        100.0,
        wp(),
        &stimulated,
    )
    .unwrap();
    assert!(inverse.material.atomic_b.trace().re > 0.0);
    assert!(inverse.material.event_rate < 0.0);
    close(
        inverse.photon_c_normal[0].trace().re,
        inverse.material.angular_c[0].trace().re * 0.5,
    );
    close(
        inverse.atomic_b_normal.trace().re,
        inverse.material.atomic_b.trace().re * 0.8,
    );
    let rates = ChannelRates {
        r584: 2.0,
        rir: -3.0,
        rp: 5.0,
        rs: -7.0,
        r2g: 11.0,
    };
    let e = HeEnergies::canonical();
    let h_kin = -8.0;
    let bf_photon = e.chi_p * rates.rp + e.chi_s * rates.rs + h_kin;
    let ledger = assemble_he_event_ledger(rates, e, bf_photon, h_kin).unwrap();
    close(ledger.he_nuclei_residual, 0.0);
    close(ledger.charge_minus_e_residual, 0.0);
    close(ledger.photon_number_source, 23.0);
    close(ledger.energy_residual, 0.0);
}

#[test]
fn rec_bf_uses_material_energy_and_preserves_missing_authority() {
    let frame = MaterialFrame::new([0.6, 0.0, 0.0]).unwrap();
    let state = rec_state();
    let p = PBoundFreeTable::jacobs_high_length();
    let s = SBoundFreeTable::jacobs_high_length();
    let ep = state.constants.chi_p_ev + 1.2 * state.constants.rydberg_ev;
    let es = state.constants.chi_s_ev + 1.2 * state.constants.rydberg_ev;
    let p_out = rec::p_bound_free(frame, ep / 0.5, [1.0, 0.0, 0.0], &state, p).unwrap();
    let s_out = rec::s_bound_free(frame, es / 0.5, [1.0, 0.0, 0.0], &state, s).unwrap();
    assert_eq!(p_out.material.coverage, CoverageState::Represented);
    assert_eq!(s_out.material.coverage, CoverageState::Represented);
    assert!(p_out.material.event_rate_density.is_finite());
    assert!(s_out.material.event_rate_density.is_finite());
    close(
        p_out.photon_c_normal.trace().re,
        0.5 * p_out.material.photon_c.trace().re,
    );
    close(
        p_out.atomic_b_normal_per_material_measure.trace().re,
        0.8 * p_out.material.atomic_b.trace().re,
    );
    close(
        s_out.photon_c_normal.trace().re,
        0.5 * s_out.material.photon_c.trace().re,
    );
    close(
        s_out.atomic_s_normal_per_material_measure,
        0.8 * s_out.material.atomic_s_density,
    );
    let below = rec::p_bound_free(
        frame,
        (state.constants.chi_p_ev - 0.01) / 0.5,
        [1.0, 0.0, 0.0],
        &state,
        p,
    )
    .unwrap();
    assert_eq!(
        below.material.coverage,
        CoverageState::PhysicalZeroBelowThreshold
    );
    let missing = rec::p_bound_free(
        frame,
        (state.constants.chi_p_ev + 1.6 * state.constants.rydberg_ev) / 0.5,
        [1.0, 0.0, 0.0],
        &state,
        p,
    )
    .unwrap_err();
    assert!(matches!(
        missing,
        RecHostError::Source(CoverageError::MissingAuthority { .. })
    ));
}

#[test]
fn rec_pair_uses_independent_dopplers_and_d86_domain() {
    let frame = MaterialFrame::new([0.6, 0.0, 0.0]).unwrap();
    let state = rec_state();
    close(d86_w(0.5).unwrap(), 145.142);
    close(d86_w(0.5125).unwrap(), (145.142 + 144.921) / 2.0);
    let delta = state.constants.delta_s_ev;
    let input = PairInput {
        y: 0.0,
        f1: Mat2::zero(),
        f2: Mat2::zero(),
        v1: screen(),
        v2: screen(),
    };
    let pair = rec::two_photon_pair(
        frame,
        [delta, delta / 4.0],
        [[1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]],
        input,
        &state,
    )
    .unwrap();
    close(pair.material.energy1_j, pair.material.energy2_j);
    assert_eq!(pair.material.photon_tags_per_event, 2);
    let interior = rec::two_photon_pair(
        frame,
        [delta * 0.5125 / 0.5, delta * 0.4875 / 2.0],
        [[1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]],
        input,
        &state,
    )
    .unwrap();
    close(interior.material.w_s_inv, (145.142 + 144.921) / 2.0);
    close(
        pair.tagged_c_normal_per_partner_sr[0].trace().re,
        pair.material.tagged_c1_per_partner_sr.trace().re * 0.5,
    );
    close(
        pair.tagged_c_normal_per_partner_sr[1].trace().re,
        pair.material.tagged_c2_per_partner_sr.trace().re * 2.0,
    );
    let err = rec::two_photon_pair(
        frame,
        [delta * 0.02 / 0.5, delta * 0.98 / 2.0],
        [[1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]],
        input,
        &state,
    )
    .unwrap_err();
    assert!(matches!(
        err,
        RecHostError::Source(CoverageError::OutOfBand { .. })
    ));
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
    let manifest = include_str!("../../Cargo.toml");
    let lock = include_str!("../../Cargo.lock");
    for sha in [REC, REI] {
        assert!(manifest.contains(&format!("rev = \"{sha}\"")));
        assert!(lock.contains(sha));
    }
    assert!(!manifest.contains("branch ="));
}
