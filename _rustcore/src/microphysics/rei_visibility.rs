//! Typed REI proper-density snapshots to the BASS Thomson visibility boundary.
//!
//! This density-only adapter validates the complete HHe source model/state, but
//! does not evaluate a chemistry RHS or certify its temperature domain. In
//! particular an FT03 snapshot outside its rate-fit window still has a defined
//! electron density. All nuclei share the supplied material frame. Caller-owned
//! normal-time cells are fixed snapshots, not a reconstructed chemistry history.
//! This is a modelling utility under the existing cold-Thomson approximation.
//! A finite-temperature snapshot is not a cold-electron validity certificate;
//! spectrum/tail support and polarized collision-kernel admission stay separate.

use super::frame::MaterialFrame;
use super::visibility::{integrate_visibility, ElectronState, VisibilityError, VisibilityResult};
use rei_microphysics::{ForwardError, Ft03Model, HHeModel, HHeState};

/// Exact conversion of number densities from cm^-3 to m^-3.
pub const CM3_TO_M3_NUMBER_DENSITY: f64 = 1_000_000.0;

#[derive(Clone, Debug)]
pub enum ReiVisibilityError {
    Source(ForwardError),
    DensityConversionOverflow,
    Visibility(VisibilityError),
}

impl From<ForwardError> for ReiVisibilityError {
    fn from(error: ForwardError) -> Self { Self::Source(error) }
}
impl From<VisibilityError> for ReiVisibilityError {
    fn from(error: VisibilityError) -> Self { Self::Visibility(error) }
}

/// Validate the actual source snapshot and convert its proper nuclear densities.
///
/// The source's public electron-density method owns full model/state validation.
/// `ElectronState` retains ownership of the BASS electron population expression.
/// This interface uses BASS c and sigma_T downstream; it does not certify that
/// arbitrary source constants agree with those used by another chemistry run.
pub fn electron_state_from_hhe(
    model: &HHeModel,
    state: &HHeState,
) -> Result<ElectronState, ReiVisibilityError> {
    model.electron_density(state)?;
    let n_h_m3 = model.n_h_cm3 * CM3_TO_M3_NUMBER_DENSITY;
    let n_he_m3 = model.n_he_cm3 * CM3_TO_M3_NUMBER_DENSITY;
    if !n_h_m3.is_finite() || !n_he_m3.is_finite() {
        return Err(ReiVisibilityError::DensityConversionOverflow);
    }
    let [x_hii, x_heii, x_heiii] = state.fractions;
    Ok(ElectronState::new(n_h_m3, n_he_m3, x_hii, x_heii, x_heiii)?)
}

/// Density-only FT03 adapter, with no evaluation or admission of the FT03 RHS.
pub fn electron_state_from_ft03(
    model: &Ft03Model,
    state: &HHeState,
) -> Result<ElectronState, ReiVisibilityError> {
    electron_state_from_hhe(&model.gas, state)
}

/// One externally chosen snapshot per normal-time interval.
#[derive(Clone, Copy, Debug)]
pub enum ReiOpacityCell<'a> {
    HHe { model: &'a HHeModel, state: &'a HHeState, frame: MaterialFrame, e_normal: [f64; 3] },
    Ft03 { model: &'a Ft03Model, state: &'a HHeState, frame: MaterialFrame, e_normal: [f64; 3] },
}

#[derive(Clone, Debug)]
pub struct ReiVisibilitySchedule {
    /// Proper electron densities of the supplied interval snapshots, in m^-3.
    pub electron_density_m3: Vec<f64>,
    /// Directional normal-clock rates. D is already included exactly once.
    pub interval_rates_s_inverse: Vec<f64>,
    pub visibility: VisibilityResult,
}

/// Build an auditable density/rate schedule and use the existing host integral.
///
/// Each input cell uses its own validated source model/state, material frame and
/// unit direction. No a^-3, conformal-time factor, filling factor or additional
/// Doppler factor is inferred. The supplied observer tail is preserved exactly.
pub fn integrate_rei_visibility(
    time_edges_seconds: &[f64],
    cells: &[ReiOpacityCell<'_>],
    observer_optical_depth: f64,
) -> Result<ReiVisibilitySchedule, ReiVisibilityError> {
    if time_edges_seconds.len() < 2 || cells.len() != time_edges_seconds.len() - 1 {
        return Err(VisibilityError::InvalidGrid.into());
    }
    let mut electron_density_m3 = Vec::with_capacity(cells.len());
    let mut interval_rates_s_inverse = Vec::with_capacity(cells.len());
    for cell in cells {
        let (electrons, frame, direction) = match *cell {
            ReiOpacityCell::HHe { model, state, frame, e_normal } =>
                (electron_state_from_hhe(model, state)?, frame, e_normal),
            ReiOpacityCell::Ft03 { model, state, frame, e_normal } =>
                (electron_state_from_ft03(model, state)?, frame, e_normal),
        };
        electron_density_m3.push(electrons.number_density_m3());
        interval_rates_s_inverse.push(electrons.scattering_rate_per_normal_second(frame, direction)?);
    }
    let visibility = integrate_visibility(time_edges_seconds, &interval_rates_s_inverse, observer_optical_depth)?;
    Ok(ReiVisibilitySchedule { electron_density_m3, interval_rates_s_inverse, visibility })
}
