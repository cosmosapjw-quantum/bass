//! Frozen follow-up acceptance oracle: frame validity and finite time sources.
use bianchi_rustcore::microphysics::{
    frame::{FrameError, MaterialFrame},
    rec::{self, RecHostError},
};
use rec_microphysics::he_singlet::{BoundBoundChannel, Mat2, Mat3, WeightedBbMode};

#[test]
fn rejects_negative_doppler_without_normalizing_direction() {
    let beta = f64::from_bits(1.0f64.to_bits() - 1);
    let frame = MaterialFrame::new([beta, 0.0, 0.0]).unwrap();
    assert!(matches!(
        frame.doppler([1.0 + 2e-13, 0.0, 0.0]),
        Err(FrameError::InvalidDirection)
    ));
    assert!(frame.doppler([1.0, 0.0, 0.0]).unwrap() > 0.0);
}

#[test]
fn source_overflow_and_nonfinite_inputs_are_typed() {
    let frame = MaterialFrame::new([0.6, 0.0, 0.0]).unwrap();
    assert!(matches!(
        frame.photon_normal_time_source(f64::MAX, [-1.0, 0.0, 0.0]),
        Err(FrameError::NonFiniteSource)
    ));
    for bad in [f64::NAN, f64::INFINITY, f64::NEG_INFINITY] {
        assert!(matches!(
            frame.photon_normal_time_source(bad, [1.0, 0.0, 0.0]),
            Err(FrameError::NonFiniteSource)
        ));
        assert!(matches!(
            frame.atomic_normal_time_source(bad),
            Err(FrameError::NonFiniteSource)
        ));
    }
    assert_eq!(
        frame
            .photon_normal_time_source(-3.0, [1.0, 0.0, 0.0])
            .unwrap(),
        -1.5
    );
    assert_eq!(
        frame
            .photon_normal_time_source(0.0, [1.0, 0.0, 0.0])
            .unwrap(),
        0.0
    );
    assert_eq!(frame.atomic_normal_time_source(-3.0).unwrap(), -2.4);
}

#[test]
fn invalid_kinematics_and_pair_constraints_remain_errors() {
    for beta in [
        [1.0, 0.0, 0.0],
        [f64::NAN, 0.0, 0.0],
        [f64::INFINITY, 0.0, 0.0],
    ] {
        assert!(matches!(
            MaterialFrame::new(beta),
            Err(FrameError::InvalidVelocity)
        ));
    }
    let frame = MaterialFrame::new([0.0; 3]).unwrap();
    for direction in [
        [0.0; 3],
        [2.0, 0.0, 0.0],
        [f64::NAN, 0.0, 0.0],
        [f64::INFINITY, 0.0, 0.0],
    ] {
        assert!(matches!(
            frame.doppler(direction),
            Err(FrameError::InvalidDirection)
        ));
    }
    for energy in [0.0, -1.0, f64::NAN, f64::INFINITY] {
        assert!(matches!(
            frame.material_energy_ev(energy, [1.0, 0.0, 0.0]),
            Err(FrameError::InvalidEnergy)
        ));
    }
    assert!(matches!(
        frame.pair_material_fraction([1.0, 1.0], [[1.0, 0.0, 0.0]; 2], 3.0),
        Err(FrameError::PairEnergyMismatch { .. })
    ));
    assert!(matches!(
        rec::bound_bound(
            frame,
            &[],
            BoundBoundChannel::He584,
            1.0,
            Mat3::scalar(1.0),
            &[WeightedBbMode {
                v: [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]],
                f: Mat2::zero(),
                weight_sr: 1.0
            }]
        ),
        Err(RecHostError::Frame(FrameError::ModeDirectionMismatch))
    ));
}

#[test]
fn rec_preserves_finite_extreme_sources_and_child_errors() {
    let frame = MaterialFrame::new([-0.999_999_999_999, 0.0, 0.0]).unwrap();
    let modes = [WeightedBbMode {
        v: [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]],
        f: Mat2::zero(),
        weight_sr: 1.0,
    }];
    rec_microphysics::he_singlet::validate_screen(modes[0].v, Some([1.0, 0.0, 0.0])).unwrap();
    // The line-delta coefficient has a small dimensional prefactor: this large
    // population is still finite after the boost, not a host overflow fixture.
    let material = rec_microphysics::he_singlet::he_bb_source(
        BoundBoundChannel::He584,
        0.0,
        Mat3::scalar(1e294),
        &modes,
    )
    .unwrap();
    assert!(material.angular_c[0]
        .0
        .iter()
        .flatten()
        .all(|z| z.re.is_finite() && z.im.is_finite()));
    let converted = rec::bound_bound(
        frame,
        &[[1.0, 0.0, 0.0]],
        BoundBoundChannel::He584,
        0.0,
        Mat3::scalar(1e294),
        &modes,
    )
    .unwrap();
    assert_eq!(
        converted.photon_c_normal[0],
        material.angular_c[0].scale(frame.doppler([1.0, 0.0, 0.0]).unwrap())
    );
    assert_eq!(
        converted.event_rate_normal,
        material.event_rate / frame.gamma()
    );
    assert!(matches!(
        rec::bound_bound(
            frame,
            &[[1.0, 0.0, 0.0]],
            BoundBoundChannel::He584,
            0.0,
            Mat3::scalar(f64::MAX),
            &modes
        ),
        Err(RecHostError::Source(_))
    ));
}
