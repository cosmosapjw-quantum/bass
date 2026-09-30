//! BASS frame/clock adaptation for admitted selected-He Rust sources.
//! Atomic rates remain per material energy/angle measure; only their time
//! derivative is converted here. A normal-measure integral needs its own
//! explicitly supplied Lorentz Jacobian at the transport boundary.
use rec_microphysics::coverage::CoverageError;
use rec_microphysics::he_singlet::{
    BoundBoundChannel, BoundBoundOutput, Mat2, Mat3, PBoundFreeOutput, PBoundFreeTable, PairInput,
    SBoundFreeOutput, SBoundFreeTable, SourceState, TwoPhotonPairOutput, WeightedBbMode,
};

use super::frame::{FrameError, MaterialFrame};

#[derive(Debug)]
pub enum RecHostError {
    Frame(FrameError),
    Source(CoverageError),
}
impl From<FrameError> for RecHostError {
    fn from(value: FrameError) -> Self {
        Self::Frame(value)
    }
}
impl From<CoverageError> for RecHostError {
    fn from(value: CoverageError) -> Self {
        Self::Source(value)
    }
}

fn checked_scale_mat2(value: Mat2, scale: f64) -> Result<Mat2, RecHostError> {
    let scaled = value.scale(scale);
    if scaled
        .0
        .iter()
        .flatten()
        .any(|z| !z.re.is_finite() || !z.im.is_finite())
    {
        return Err(FrameError::NonFiniteSource.into());
    }
    Ok(scaled)
}

fn checked_scale_mat3(value: Mat3, scale: f64) -> Result<Mat3, RecHostError> {
    let scaled = value.scale(scale);
    if scaled
        .0
        .iter()
        .flatten()
        .any(|z| !z.re.is_finite() || !z.im.is_finite())
    {
        return Err(FrameError::NonFiniteSource.into());
    }
    Ok(scaled)
}

fn checked_divide_scalar(value: f64, divisor: f64) -> Result<f64, RecHostError> {
    let scaled = value / divisor;
    if !scaled.is_finite() {
        return Err(FrameError::NonFiniteSource.into());
    }
    Ok(scaled)
}

#[derive(Debug)]
pub struct BoundBoundNormalTime {
    pub material: BoundBoundOutput,
    /// Occupation source for each ray, per normal time.
    pub photon_c_normal: Vec<Mat2>,
    /// Proper atomic density source per normal time.
    pub atomic_b_normal: Mat3,
    pub event_rate_normal: f64,
}
#[derive(Debug)]
pub struct PBoundFreeNormalTime {
    pub material: PBoundFreeOutput,
    pub photon_c_normal: Mat2,
    /// Per material dE and dOmega, per normal time; no measure Jacobian applied.
    pub atomic_b_normal_per_material_measure: Mat3,
    pub event_rate_normal_per_material_measure: f64,
}
#[derive(Debug)]
pub struct SBoundFreeNormalTime {
    pub material: SBoundFreeOutput,
    pub photon_c_normal: Mat2,
    pub atomic_s_normal_per_material_measure: f64,
    pub event_rate_normal_per_material_measure: f64,
}
#[derive(Debug)]
pub struct PairNormalTime {
    pub material: TwoPhotonPairOutput,
    pub tagged_c_normal_per_partner_sr: [Mat2; 2],
    pub atomic_event_normal_per_material_measure: f64,
}

pub fn bound_bound(
    frame: MaterialFrame,
    normal_directions: &[[f64; 3]],
    channel: BoundBoundChannel,
    lower: f64,
    upper: Mat3,
    modes: &[WeightedBbMode],
) -> Result<BoundBoundNormalTime, RecHostError> {
    if normal_directions.len() != modes.len() {
        return Err(FrameError::ModeDirectionMismatch.into());
    }
    let dopplers: Vec<_> = normal_directions
        .iter()
        .map(|d| frame.doppler(*d))
        .collect::<Result<_, _>>()?;
    let material = rec_microphysics::he_singlet::he_bb_source(channel, lower, upper, modes)?;
    let photon_c_normal = material
        .angular_c
        .iter()
        .zip(dopplers)
        .map(|(c, d)| checked_scale_mat2(*c, d))
        .collect::<Result<_, _>>()?;
    let atomic_b_normal = checked_scale_mat3(material.atomic_b, 1.0 / frame.gamma())?;
    let event_rate_normal = checked_divide_scalar(material.event_rate, frame.gamma())?;
    Ok(BoundBoundNormalTime {
        material,
        photon_c_normal,
        atomic_b_normal,
        event_rate_normal,
    })
}

pub fn p_bound_free(
    frame: MaterialFrame,
    normal_energy_ev: f64,
    normal_direction: [f64; 3],
    state: &SourceState,
    table: PBoundFreeTable,
) -> Result<PBoundFreeNormalTime, RecHostError> {
    let d = frame.doppler(normal_direction)?;
    let material_energy = frame.material_energy_ev(normal_energy_ev, normal_direction)?;
    let material = rec_microphysics::he_singlet::he_p_bf_source(material_energy, state, table)?;
    let photon_c_normal = checked_scale_mat2(material.photon_c, d)?;
    let atomic_b_normal_per_material_measure =
        checked_scale_mat3(material.atomic_b, 1.0 / frame.gamma())?;
    let event_rate_normal_per_material_measure =
        checked_divide_scalar(material.event_rate_density, frame.gamma())?;
    Ok(PBoundFreeNormalTime {
        material,
        photon_c_normal,
        atomic_b_normal_per_material_measure,
        event_rate_normal_per_material_measure,
    })
}

pub fn s_bound_free(
    frame: MaterialFrame,
    normal_energy_ev: f64,
    normal_direction: [f64; 3],
    state: &SourceState,
    table: SBoundFreeTable,
) -> Result<SBoundFreeNormalTime, RecHostError> {
    let d = frame.doppler(normal_direction)?;
    let material_energy = frame.material_energy_ev(normal_energy_ev, normal_direction)?;
    let material = rec_microphysics::he_singlet::he_s_bf_source(material_energy, state, table)?;
    let photon_c_normal = checked_scale_mat2(material.photon_c, d)?;
    let atomic_s_normal_per_material_measure =
        checked_divide_scalar(material.atomic_s_density, frame.gamma())?;
    let event_rate_normal_per_material_measure =
        checked_divide_scalar(material.event_rate_density, frame.gamma())?;
    Ok(SBoundFreeNormalTime {
        material,
        photon_c_normal,
        atomic_s_normal_per_material_measure,
        event_rate_normal_per_material_measure,
    })
}

pub fn two_photon_pair(
    frame: MaterialFrame,
    normal_energy_ev: [f64; 2],
    normal_directions: [[f64; 3]; 2],
    mut material_input: PairInput,
    state: &SourceState,
) -> Result<PairNormalTime, RecHostError> {
    let d1 = frame.doppler(normal_directions[0])?;
    let d2 = frame.doppler(normal_directions[1])?;
    material_input.y = frame.pair_material_fraction(
        normal_energy_ev,
        normal_directions,
        state.constants.delta_s_ev,
    )?;
    let material = rec_microphysics::he_singlet::he_two_photon_pair_source(&material_input, state)?;
    let tagged_c_normal_per_partner_sr = [
        checked_scale_mat2(material.tagged_c1_per_partner_sr, d1)?,
        checked_scale_mat2(material.tagged_c2_per_partner_sr, d2)?,
    ];
    let atomic_event_normal_per_material_measure =
        checked_divide_scalar(material.event_rate_density, frame.gamma())?;
    Ok(PairNormalTime {
        material,
        tagged_c_normal_per_partner_sr,
        atomic_event_normal_per_material_measure,
    })
}

#[cfg(test)]
mod conversion_tests {
    use super::*;

    #[test]
    fn matrix_conversions_reject_real_and_imaginary_overflow() {
        for imaginary in [false, true] {
            let mut m2 = Mat2::zero();
            let mut m3 = Mat3::zero();
            if imaginary {
                m2.0[0][1].im = f64::MAX;
                m3.0[1][2].im = f64::MAX;
            } else {
                m2.0[0][1].re = f64::MAX;
                m3.0[1][2].re = f64::MAX;
            }
            assert!(matches!(
                checked_scale_mat2(m2, 2.0),
                Err(RecHostError::Frame(FrameError::NonFiniteSource))
            ));
            assert!(matches!(
                checked_scale_mat3(m3, 2.0),
                Err(RecHostError::Frame(FrameError::NonFiniteSource))
            ));
        }
    }

    #[test]
    fn matrix_conversions_reject_nonfinite_entries_and_keep_signed_sources() {
        for bad in [f64::NAN, f64::INFINITY, f64::NEG_INFINITY] {
            let mut m2 = Mat2::zero();
            let mut m3 = Mat3::zero();
            m2.0[1][0].im = bad;
            m3.0[2][1].re = bad;
            assert!(matches!(
                checked_scale_mat2(m2, 0.5),
                Err(RecHostError::Frame(FrameError::NonFiniteSource))
            ));
            assert!(matches!(
                checked_scale_mat3(m3, 0.5),
                Err(RecHostError::Frame(FrameError::NonFiniteSource))
            ));
        }
        let m2 = Mat2::scalar(-3.0);
        let m3 = Mat3::scalar(-7.0);
        assert_eq!(checked_scale_mat2(m2, 0.5).unwrap(), m2.scale(0.5));
        assert_eq!(checked_scale_mat3(m3, 0.8).unwrap(), m3.scale(0.8));
    }
}
