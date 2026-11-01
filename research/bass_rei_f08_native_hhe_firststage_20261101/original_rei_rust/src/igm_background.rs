//! Source-explicit flat radiation + matter + Lambda FLRW background.
//!
//! Coordinates are absolute `ln(a)`, with a=1 today. This deliberately does NOT
//! implement `GeometryBackground::snapshot(t)`: no proper-time inversion is
//! available yet, and passing ln(a) as seconds would be incorrect.
use crate::{ForwardError, GeometrySnapshot};

// NIST CODATA central values, retrieved 2026-10-06:
// G: https://pml.nist.gov/cuu/pdf/RevModPhys.93.025010.pdf (2018 CODATA)
// mp: https://physics.nist.gov/cgi-bin/cuu/Value?mp%7Csearch_for=mass+of+proton
// SI -> cgs: G multiplied by 1e3; proton mass multiplied by 1e3.
const G_CGS: f64 = 6.67430e-8;
const PROTON_MASS_G: f64 = 1.672_621_925_95e-24;

/// All parameters are caller-supplied. `parameter_source` is attribution, not a
/// claim that an external source was verified. No observational default exists.
#[derive(Clone, Debug)]
pub struct FlatFlrwConfig {
    pub h0_per_s: f64,
    pub omega_r: f64,
    pub omega_m: f64,
    pub omega_b: f64,
    pub omega_lambda: f64,
    pub helium_mass_fraction: f64,
    pub tcmb0_k: f64,
    pub ln_a_min: f64,
    pub ln_a_max: f64,
    pub parameter_source: String,
}

#[derive(Clone, Debug)]
pub struct FlatFlrwBackground {
    config: FlatFlrwConfig,
    n_h0_cm3: f64,
    n_he0_cm3: f64,
}

#[derive(Clone, Copy, Debug)]
pub struct FlrwPoint {
    pub a: f64,
    pub redshift: f64,
    pub hubble_per_s: f64,
    pub n_h_cm3: f64,
    pub n_he_cm3: f64,
    pub tcmb_k: f64,
    pub dt_dln_a_s: f64,
    pub dt_dz_s: f64,
    pub geometry: GeometrySnapshot,
}

fn invalid() -> ForwardError {
    ForwardError::InvalidInput("IGM_BACKGROUND_DOMAIN")
}
fn positive(x: f64) -> Result<f64, ForwardError> {
    if x.is_normal() && x > 0.0 {
        Ok(x)
    } else {
        Err(invalid())
    }
}
fn nonnegative(x: f64) -> Result<f64, ForwardError> {
    if x == 0.0 {
        Ok(x)
    } else {
        positive(x)
    }
}
fn product(x: f64, y: f64) -> Result<f64, ForwardError> {
    nonnegative(x)?;
    nonnegative(y)?;
    if x == 0.0 || y == 0.0 {
        Ok(0.0)
    } else {
        positive(x * y)
    }
}

impl FlatFlrwBackground {
    /// Uses rho_crit0=3H0²/(8piG), mH=mp and mHe=4mp. The latter is an
    /// explicit nucleon-mass approximation, not exact atomic masses; binding
    /// and electron-mass corrections are neglected. Omega_r is independently
    /// specified, not inferred from Tcmb (it may include other radiation).
    ///
    /// Flatness tolerance is 1e-12 absolute; inputs are never renormalized.
    /// Positive subnormal intermediates are outside this numerical contract.
    pub fn new(config: FlatFlrwConfig) -> Result<Self, ForwardError> {
        positive(config.h0_per_s)?;
        positive(config.omega_b)?;
        positive(config.tcmb0_k)?;
        for x in [
            config.omega_r,
            config.omega_m,
            config.omega_lambda,
            config.helium_mass_fraction,
        ] {
            nonnegative(x)?;
        }
        if config.omega_b > config.omega_m
            || config.helium_mass_fraction >= 1.0
            || (config.omega_r + config.omega_m + config.omega_lambda - 1.0).abs() > 1e-12
            || !(config.omega_r + config.omega_m + config.omega_lambda).is_finite()
            || !config.ln_a_min.is_finite()
            || !config.ln_a_max.is_finite()
            || config.ln_a_min > config.ln_a_max
            || config.parameter_source.trim().is_empty()
        {
            return Err(invalid());
        }
        let rho_crit = positive(
            3.0 * positive(config.h0_per_s * config.h0_per_s)?
                / (8.0 * std::f64::consts::PI * G_CGS),
        )?;
        let rho_b = positive(config.omega_b * rho_crit)?;
        let n_h0_cm3 =
            positive(positive((1.0 - config.helium_mass_fraction) * rho_b)? / PROTON_MASS_G)?;
        let n_he0_cm3 =
            nonnegative(product(config.helium_mass_fraction, rho_b)? / (4.0 * PROTON_MASS_G))?;
        let bg = Self {
            config,
            n_h0_cm3,
            n_he0_cm3,
        };
        bg.at_ln_a(bg.config.ln_a_min)?;
        bg.at_ln_a(bg.config.ln_a_max)?;
        Ok(bg)
    }

    /// Absolute comoving hydrogen number density, cm^-3 at a=1.
    pub fn n_h_comoving_cm3(&self) -> f64 {
        self.n_h0_cm3
    }

    pub fn at_ln_a(&self, ln_a: f64) -> Result<FlrwPoint, ForwardError> {
        let c = &self.config;
        if !ln_a.is_finite() || ln_a < c.ln_a_min || ln_a > c.ln_a_max {
            return Err(invalid());
        }
        let a = positive(ln_a.exp())?;
        let inv_a = positive(1.0 / a)?;
        let inv_a3 = positive(inv_a.powi(3))?;
        let radiation = if c.omega_r == 0.0 {
            0.0
        } else {
            positive(c.omega_r * positive(inv_a.powi(4))?)?
        };
        let h = positive(
            c.h0_per_s * positive(radiation + product(c.omega_m, inv_a3)? + c.omega_lambda)?.sqrt(),
        )?;
        let redshift = inv_a - 1.0;
        if !redshift.is_finite() || redshift <= -1.0 {
            return Err(invalid());
        }
        let dt_dln_a_s = positive(1.0 / h)?;
        let dt_dz_s = -positive(a / h)?;
        Ok(FlrwPoint {
            a,
            redshift,
            hubble_per_s: h,
            n_h_cm3: positive(self.n_h0_cm3 * inv_a3)?,
            n_he_cm3: product(self.n_he0_cm3, inv_a3)?,
            tcmb_k: positive(c.tcmb0_k * inv_a)?,
            dt_dln_a_s,
            dt_dz_s,
            geometry: GeometrySnapshot::new([a; 3], [h; 3])?,
        })
    }

    pub fn at_redshift(&self, z: f64) -> Result<FlrwPoint, ForwardError> {
        if !z.is_finite() || z <= -1.0 {
            return Err(invalid());
        }
        // Exact representable endpoint identities take precedence over a
        // second transcendental round trip, which can move ln(a) a few ulps
        // beyond its declared bound. No tolerance band or physical clipping:
        // all other inputs pass through the ordinary ln(a) domain checks.
        let early = self.at_ln_a(self.config.ln_a_min)?;
        let late = self.at_ln_a(self.config.ln_a_max)?;
        if z == early.redshift {
            return Ok(early);
        }
        if z == late.redshift {
            return Ok(late);
        }
        self.at_ln_a(-z.ln_1p())
    }
}
