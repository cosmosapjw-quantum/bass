//! Opt-in isotope-native D0 + H+ <-> D+ + H0, in proper SI units.
//!
//! The kinetic map is exact only for frozen coefficients and fixed proper
//! volume. Updating temperature-dependent rates, expansion, and the remaining
//! D chemistry belongs to the caller; this is not a full D history provider.

/// Explicit proper densities [m^-3] and thermal energy density [J m^-3].
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct DhState {
    pub h0_m3: f64,
    pub hp_m3: f64,
    pub d0_m3: f64,
    pub dp_m3: f64,
    pub thermal_j_m3: f64,
}

/// The electron density is the H+/D+ neutrality closure, not a new species input.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct DhTotals {
    pub hydrogen_m3: f64,
    pub deuterium_m3: f64,
    pub positive_charge_m3: f64,
    pub baryons_m3: f64,
    pub electrons_m3: f64,
    pub thermal_particles_m3: f64,
}

impl DhState {
    pub fn totals(self) -> Result<DhTotals, DhError> {
        for value in [
            self.h0_m3,
            self.hp_m3,
            self.d0_m3,
            self.dp_m3,
            self.thermal_j_m3,
        ] {
            valid_nonnegative(value)?;
        }
        let hydrogen_m3 = self.h0_m3 + self.hp_m3;
        let deuterium_m3 = self.d0_m3 + self.dp_m3;
        let positive_charge_m3 = self.hp_m3 + self.dp_m3;
        let totals = DhTotals {
            hydrogen_m3,
            deuterium_m3,
            positive_charge_m3,
            baryons_m3: hydrogen_m3 + 2.0 * deuterium_m3,
            electrons_m3: positive_charge_m3,
            thermal_particles_m3: hydrogen_m3 + deuterium_m3 + positive_charge_m3,
        };
        for value in [
            totals.hydrogen_m3,
            totals.deuterium_m3,
            totals.positive_charge_m3,
            totals.baryons_m3,
            totals.thermal_particles_m3,
        ] {
            finite_arithmetic(value)?;
        }
        Ok(totals)
    }
}

/// Coefficients [m^3 s^-1], their temperature/domain [K], and explicit source.
/// Public fields also permit explicitly identified manufactured test rates.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct DhRates {
    pub forward_m3_s: f64,
    pub reverse_m3_s: f64,
    pub temperature_k: f64,
    pub minimum_k: f64,
    pub maximum_k: f64,
    pub source: &'static str,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct DhEnergyDefect {
    /// chi_D - chi_H [J per forward event], independently supplied.
    pub delta_chi_j: f64,
    pub source: &'static str,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum DhError {
    InvalidInput,
    NonFiniteInput,
    OutsideTemperatureDomain,
    NegativeFinalDensity,
    NegativeFinalThermalEnergy,
    ArithmeticOverflow,
}

fn valid_nonnegative(value: f64) -> Result<(), DhError> {
    if !value.is_finite() {
        Err(DhError::NonFiniteInput)
    } else if value < 0.0 {
        Err(DhError::InvalidInput)
    } else {
        Ok(())
    }
}

fn finite_arithmetic(value: f64) -> Result<(), DhError> {
    if value.is_finite() {
        Ok(())
    } else {
        Err(DhError::ArithmeticOverflow)
    }
}

impl DhRates {
    fn validate(self) -> Result<(), DhError> {
        for value in [
            self.forward_m3_s,
            self.reverse_m3_s,
            self.temperature_k,
            self.minimum_k,
            self.maximum_k,
        ] {
            valid_nonnegative(value)?;
        }
        if self.minimum_k <= 0.0 || self.maximum_k < self.minimum_k || self.source.is_empty() {
            return Err(DhError::InvalidInput);
        }
        if !(self.minimum_k..=self.maximum_k).contains(&self.temperature_k) {
            return Err(DhError::OutsideTemperatureDomain);
        }
        Ok(())
    }
}

pub struct Savin2002;

impl Savin2002 {
    pub const SOURCE: &'static str =
        "Savin (2002), ApJ 566 599-603, DOI 10.1086/324218, Eq. (6), Table 2";
    pub const MINIMUM_K: f64 = 2.7;
    pub const MAXIMUM_K: f64 = 200_000.0;

    /// Table-2 analytic fits, converted from cm^3/s by exactly 10^-6.
    /// Reported fit deviations (<6% forward, <4% reverse) are not an estimate
    /// of total atomic uncertainty or of cosmological prediction error.
    pub fn rates(temperature_k: f64) -> Result<DhRates, DhError> {
        if !temperature_k.is_finite() {
            return Err(DhError::NonFiniteInput);
        }
        if !(Self::MINIMUM_K..=Self::MAXIMUM_K).contains(&temperature_k) {
            return Err(DhError::OutsideTemperatureDomain);
        }
        let t = temperature_k;
        let forward_cm3_s = 2.00e-10 * t.powf(0.402) * (-37.1 / t).exp() - 3.31e-17 * t.powf(1.48);
        let reverse_cm3_s = 2.06e-10 * t.powf(0.396) * (-33.0 / t).exp() + 2.03e-9 * t.powf(-0.332);
        let rates = DhRates {
            forward_m3_s: forward_cm3_s * 1e-6,
            reverse_m3_s: reverse_cm3_s * 1e-6,
            temperature_k,
            minimum_k: Self::MINIMUM_K,
            maximum_k: Self::MAXIMUM_K,
            source: Self::SOURCE,
        };
        rates.validate()?;
        Ok(rates)
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum DhMethodScope {
    ExactFrozenRatesFixedProperVolume,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct DhStep {
    pub state: DhState,
    /// Forward-positive signed event extent [m^-3].
    pub extent_m3: f64,
    pub chemical_delta_j_m3: f64,
    pub thermal_delta_j_m3: f64,
    pub electron_delta_m3: f64,
    pub totals_before: DhTotals,
    pub totals_after: DhTotals,
    pub rates: DhRates,
    pub defect: DhEnergyDefect,
    pub scope: DhMethodScope,
}

/// Transactional value API: rejection cannot mutate the supplied state.
/// No abundances, initial conditions, thresholds, or activation are defaulted.
pub fn step_frozen_rates(
    state: DhState,
    rates: DhRates,
    dt_s: f64,
    defect: DhEnergyDefect,
) -> Result<DhStep, DhError> {
    let totals_before = state.totals()?;
    rates.validate()?;
    valid_nonnegative(dt_s)?;
    if !defect.delta_chi_j.is_finite() {
        return Err(DhError::NonFiniteInput);
    }
    if defect.source.is_empty() {
        return Err(DhError::InvalidInput);
    }
    let density_scale = state
        .h0_m3
        .max(state.hp_m3)
        .max(state.d0_m3)
        .max(state.dp_m3);
    let rate_scale = rates.forward_m3_s.max(rates.reverse_m3_s);
    let mut extent_m3 = 0.0;
    if dt_s != 0.0 && rate_scale != 0.0 && density_scale != 0.0 {
        // Normalize both density and rate before products, avoiding overflow in
        // F, K and the nonnegative discriminant. This is the same Riccati map.
        let h0 = state.h0_m3 / density_scale;
        let hp = state.hp_m3 / density_scale;
        let d0 = state.d0_m3 / density_scale;
        let dp = state.dp_m3 / density_scale;
        let kf = rates.forward_m3_s / rate_scale;
        let kr = rates.reverse_m3_s / rate_scale;
        let f = kf * d0 * hp - kr * dp * h0;
        if f != 0.0 {
            let a = h0 + hp;
            let b = d0 + dp;
            let c = hp + dp;
            let k = kf * (d0 + hp) + kr * (dp + h0);
            let d = (kf * (b - c) - kr * (a - c)).hypot(2.0 * (kf * kr * a * b).sqrt());
            // Smallest*largest first avoids avoidable intermediate overflow.
            // Infinite tau is the well-defined stiff limit, not an exponential.
            let mut factors = [rate_scale, density_scale, dt_s];
            factors.sort_by(f64::total_cmp);
            let tau = (factors[0] * factors[2]) * factors[1];
            if tau != 0.0 {
                let z = 0.5 * d * tau;
                // q = 1/theta, using the small-argument limit explicitly.
                let q = if d == 0.0 || z.abs() < 1e-8 {
                    1.0 / tau
                } else {
                    0.5 * d / z.tanh()
                };
                extent_m3 = density_scale * (f / (q + 0.5 * k));
            }
        }
    }
    finite_arithmetic(extent_m3)?;
    let chemical_delta_j_m3 = defect.delta_chi_j * extent_m3;
    finite_arithmetic(chemical_delta_j_m3)?;
    let thermal_delta_j_m3 = -chemical_delta_j_m3;
    let new_state = DhState {
        h0_m3: state.h0_m3 + extent_m3,
        hp_m3: state.hp_m3 - extent_m3,
        d0_m3: state.d0_m3 - extent_m3,
        dp_m3: state.dp_m3 + extent_m3,
        thermal_j_m3: state.thermal_j_m3 + thermal_delta_j_m3,
    };
    for value in [
        new_state.h0_m3,
        new_state.hp_m3,
        new_state.d0_m3,
        new_state.dp_m3,
    ] {
        finite_arithmetic(value)?;
        if value < 0.0 {
            return Err(DhError::NegativeFinalDensity);
        }
    }
    finite_arithmetic(new_state.thermal_j_m3)?;
    if new_state.thermal_j_m3 < 0.0 {
        return Err(DhError::NegativeFinalThermalEnergy);
    }
    Ok(DhStep {
        state: new_state,
        extent_m3,
        chemical_delta_j_m3,
        thermal_delta_j_m3,
        electron_delta_m3: 0.0,
        totals_before,
        totals_after: new_state.totals()?,
        rates,
        defect,
        scope: DhMethodScope::ExactFrozenRatesFixedProperVolume,
    })
}
