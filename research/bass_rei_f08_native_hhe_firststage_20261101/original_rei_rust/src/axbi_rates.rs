//! Campaign binding of the existing cold-through-reheated H/He point model.
//!
//! Grackle 3.4.1 literals are owned by `igm_rates`; event/energy ownership is
//! owned by `igm_point_rhs`. This adapter adds no coefficients or admission to
//! the FT03 interval model. The numerical operational domain does not assert
//! empirical fit accuracy, a continuum certificate, or a cosmological history.
use crate::{
    igm_rates::{igm_rates, IgmRates},
    igm_state::IgmGasState,
    igm_thermal::{igm_point_rhs_with_prepared, IgmPhotoInput, IgmPointRhs},
    rate_table::IgmRateBackend,
    ForwardError,
};

/// Identity shared by every point evaluation and any driver's point residual.
pub const AXBI_PROVIDER_ID: &str = "AXBI_GRACKLE_3_4_1_CASE_A_POINT_V1";
pub const GRACKLE_COMMIT: &str = "af7939494ce65007887ada7b98d1813df6843346";
pub const TEMPERATURE_DOMAIN_K: [f64; 2] = [1.0, 1.0e6];

#[derive(Clone, Copy, Debug)]
pub struct AxbiPoint {
    pub provider_id: &'static str,
    /// Actual temperature recovered from the unchanged ideal H/He EOS.
    pub temperature_k: f64,
    pub rates: IgmRates,
    pub rhs: IgmPointRhs,
}

/// Case-A capture escape, clumping=1, primary-only externally supplied photo
/// input. Proper densities are cm^-3, expansion is s^-1, CMB temperature is K;
/// returned derivatives use proper seconds and the existing erg energy owners.
///
/// Scalar coefficients accept exactly [1,1e6] K. The point call admits its EOS
/// recovered temperature, preserving strict endpoint checks without projection.
/// No interval evaluator exists for this selected model. A solver residual must
/// call this same point path and must label its convergence evidence empirically.
#[derive(Clone, Copy, Debug, Default)]
pub struct AxbiProvider;
impl AxbiProvider {
    pub fn rates(self, temperature_k: f64) -> Result<IgmRates, ForwardError> {
        igm_rates(temperature_k)
    }
    pub fn point(
        self,
        gas: &IgmGasState,
        n_h_cm3: f64,
        n_he_cm3: f64,
        mean_h_per_s: f64,
        tcmb_k: f64,
        photo: IgmPhotoInput,
    ) -> Result<AxbiPoint, ForwardError> {
        self.point_with_backend(&IgmRateBackend::Direct, gas, n_h_cm3, n_he_cm3,
            mean_h_per_s, tcmb_k, photo)
    }

    /// Explicit opt-in coefficient backend; the physical ledger is unchanged.
    /// No derivative/Jacobian or trajectory admission is supplied by this API.
    pub fn point_with_backend(
        self,
        backend: &IgmRateBackend,
        gas: &IgmGasState,
        n_h_cm3: f64,
        n_he_cm3: f64,
        mean_h_per_s: f64,
        tcmb_k: f64,
        photo: IgmPhotoInput,
    ) -> Result<AxbiPoint, ForwardError> {
        let temperature_k = gas.eos(n_h_cm3, n_he_cm3)?.temperature_k;
        let prepared = backend.prepare(temperature_k)?;
        let rhs = igm_point_rhs_with_prepared(gas, n_h_cm3, n_he_cm3,
            mean_h_per_s, tcmb_k, photo, &prepared)?;
        let rates = prepared.rates();
        Ok(AxbiPoint {
            provider_id: AXBI_PROVIDER_ID,
            temperature_k,
            rates,
            rhs,
        })
    }
}
