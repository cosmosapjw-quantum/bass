//! Fixed-input REC and REI Rust microphysics calls; no history integration.
use bianchi_rustcore::microphysics::{frame::MaterialFrame, rec, rei};
use rec_microphysics::{
    coverage::CoverageError,
    he_singlet::{
        validate_screen, BoundBoundChannel, CoverageState, Mat2, Mat3, PBoundFreeTable, PairInput,
        SBoundFreeTable, SourceState, WeightedBbMode,
    },
};
use rei_microphysics::{ForwardError, GroupParams, PchipTable, State};

fn table() -> PchipTable {
    PchipTable::new(
        vec![-2.0, 0.0, 2.0],
        [vec![0.0; 2], vec![0.0; 2], vec![0.25; 2], vec![-3.0, -2.5]],
    )
    .expect("fixed PCHIP table")
}

fn main() {
    println!("FIXED_INPUT_ONLY: no history integration or scientific admission");
    let ray = [1.0, 0.0, 0.0];
    let opposite = [-1.0, 0.0, 0.0];
    let stationary = MaterialFrame::new([0.0; 3]).expect("stationary frame");
    let moving = MaterialFrame::new([0.6, 0.0, 0.0]).expect("material velocity");
    for (name, frame) in [("stationary", stationary), ("moving", moving)] {
        let d_forward = frame.doppler(ray).expect("forward unit direction");
        let d_backward = frame.doppler(opposite).expect("backward unit direction");
        let e_normal_ev = 20.0;
        let e_material_ev = frame.material_energy_ev(e_normal_ev, ray).expect("energy");
        println!(
            "{name}: gamma={:.6}, D_forward={d_forward:.6}, D_backward={d_backward:.6}, E_normal={e_normal_ev:.6} eV, E_material={e_material_ev:.6} eV",
            frame.gamma()
        );
    }

    let frame = moving;
    let d_forward = frame.doppler(ray).expect("forward Doppler factor");
    let mut state = SourceState::simple(2.0, 0.5, Mat3::scalar(1.0), 1.0, 1.0, 9000.0)
        .expect("fixed material source state");
    // Collinear boosts leave these +/-x rays along +/-x in the material frame.
    let screen = [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]];
    validate_screen(screen, Some(ray)).expect("transverse material screen");
    validate_screen(screen, Some(opposite)).expect("transverse partner screen");
    state.v = screen;
    let bb = rec::bound_bound(
        frame,
        &[ray],
        BoundBoundChannel::He584,
        2.0,
        Mat3::scalar(1.0),
        &[WeightedBbMode {
            v: screen,
            f: Mat2::zero(),
            weight_sr: 1.0,
        }],
    )
    .expect("He584 bound-bound source");
    println!(
        "REC He584: photon occupation delta_J coefficient (J s^-1, normal time)={:?}; atomic source (m^-3 s^-1, normal time)={:?}; event rate={:.6e} m^-3 s^-1",
        bb.photon_c_normal[0], bb.atomic_b_normal, bb.event_rate_normal
    );

    let p_material_ev = state.constants.chi_p_ev + 1.2 * state.constants.rydberg_ev;
    let p_normal_ev = p_material_ev / d_forward;
    let p = rec::p_bound_free(
        frame,
        p_normal_ev,
        ray,
        &state,
        PBoundFreeTable::jacobs_high_length(),
    )
    .expect("represented p bound-free source");
    println!(
        "REC p bound-free: E_normal={p_normal_ev:.6} eV, E_material={p_material_ev:.6} eV; photon occupation source per normal second={:?}; atomic source={:?}; event rate={:.6e} m^-3 s^-1 J^-1 sr^-1 per original material dE_J dOmega",
        p.photon_c_normal, p.atomic_b_normal_per_material_measure,
        p.event_rate_normal_per_material_measure
    );

    let s_material_ev = state.constants.chi_s_ev + 1.2 * state.constants.rydberg_ev;
    let s_normal_ev = s_material_ev / d_forward;
    let s = rec::s_bound_free(
        frame,
        s_normal_ev,
        ray,
        &state,
        SBoundFreeTable::jacobs_high_length(),
    )
    .expect("represented s bound-free source");
    println!(
        "REC s bound-free: E_normal={s_normal_ev:.6} eV, E_material={s_material_ev:.6} eV; photon occupation source per normal second={:?}; atomic source={:.6e}, event rate={:.6e} m^-3 s^-1 J^-1 sr^-1 per original material dE_J dOmega",
        s.photon_c_normal, s.atomic_s_normal_per_material_measure,
        s.event_rate_normal_per_material_measure
    );

    // D_forward=0.5 and D_backward=2, so the material energies sum to DeltaS.
    let delta_s_ev = state.constants.delta_s_ev;
    let pair_normal_ev = [delta_s_ev, delta_s_ev / 4.0];
    let pair = rec::two_photon_pair(
        frame,
        pair_normal_ev,
        [ray, opposite],
        PairInput {
            y: 0.0, // Replaced by the host with the Doppler-derived material fraction.
            f1: Mat2::zero(),
            f2: Mat2::zero(),
            v1: screen,
            v2: screen,
        },
        &state,
    )
    .expect("fixed moving two-photon pair");
    println!(
        "REC pair: E_normal={pair_normal_ev:?} eV, E_material=[{:.6}, {:.6}] eV; tagged occupation sources per normal second per partner sr={:?}; atomic event={:.6e} m^-3 s^-1 per original material dy dOmega1 dOmega2",
        frame.material_energy_ev(pair_normal_ev[0], ray).expect("pair energy 1"),
        frame.material_energy_ev(pair_normal_ev[1], opposite).expect("pair energy 2"),
        pair.tagged_c_normal_per_partner_sr,
        pair.atomic_event_normal_per_material_measure
    );

    let below = rec::p_bound_free(
        frame,
        0.9 * state.constants.chi_p_ev / d_forward,
        ray,
        &state,
        PBoundFreeTable::jacobs_high_length(),
    )
    .expect("below-threshold physical zero");
    assert!(matches!(
        below.material.coverage,
        CoverageState::PhysicalZeroBelowThreshold
    ));
    println!("REC below p threshold: {:?}", below.material.coverage);
    let outside_q = rec::p_bound_free(
        frame,
        (state.constants.chi_p_ev + 1.6 * state.constants.rydberg_ev) / d_forward,
        ray,
        &state,
        PBoundFreeTable::jacobs_high_length(),
    )
    .expect_err("q=1.6 lacks table authority");
    assert!(matches!(
        outside_q,
        rec::RecHostError::Source(CoverageError::MissingAuthority { .. })
    ));
    println!("REC q=1.6 typed domain error: {outside_q:?}");

    let transformed = rei::transform(&[0.0; 9]);
    println!("REI transform fixed z: {transformed:?}");
    let interpolation = rei::pchip(&table(), 0.0).expect("in-table PCHIP point");
    println!("REI PCHIP at x=0: {interpolation:.6}");
    let outside_table = rei::pchip(&table(), 2.1).expect_err("outside table domain");
    assert!(matches!(
        outside_table,
        ForwardError::OutsideTableDomain { .. }
    ));
    println!("REI PCHIP typed domain error: {outside_table:?}");

    // This explicit state keeps log(GammaHI / 1e-12 s^-1) inside the table.
    let rei_state = State {
        n_comoving_per_cmpc3: [1.0, 2.0, 3.0, 4.0],
        x_hii: 0.8,
        helium: [0.6, 0.3, 0.1],
        u_erg_per_cm3: 1.0e-12,
        gamma_hi_per_s: 1.0e-12,
    };
    let params = GroupParams {
        redshift: 3.0,
        n_h_proper_per_cm3: 1.2e-5,
        n_he_proper_per_cm3: 1.0e-6,
        hubble_per_s: 1.0e-16,
        sigma_hi_cm2: [6.0e-18, 2.0e-18, 1.0e-18, 2.0e-19],
        sigma_hei_cm2: [0.0, 7.0e-18, 3.0e-18, 5.0e-19],
        sigma_heii_cm2: [0.0, 0.0, 0.0, 1.0e-18],
        redshift_coeff: [1.0, 2.0, 3.0, 4.0],
        source_fraction: [0.4, 0.3, 0.2, 0.1],
        lowgroup_log_opacity: [table(), table()],
    };
    let opacity = rei::opacity(&rei_state, &params).expect("four-group opacity");
    println!("REI opacity: {opacity:?} cMpc^-1");
    let photon_source =
        rei::photon_source(&rei_state, &[1.0e-14; 4], &params).expect("four-group photon source");
    println!("REI photon source: {photon_source:?} comoving count cMpc^-3 s^-1");
    let gamma = rei::gamma_species(&rei_state, &params);
    println!(
        "REI photoionization gamma: HI={:.6e}, HeI={:.6e}, HeII={:.6e} s^-1",
        gamma.hi_per_s, gamma.hei_per_s, gamma.heii_per_s
    );
    let projected = rei::positive_projection(&[1.0, 3.0], 8.0).expect("positive mass projection");
    println!("REI positive projection: {projected:?} in input mass units");
    let signed = rei::signed_transfer(-4.0, &[1.0, 3.0]).expect("signed transfer lift");
    println!("REI signed transfer: {signed:?} in input rate units");
}
