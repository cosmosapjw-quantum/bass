//! Separate phenomenological low-temperature Grackle subset; no FT03 admission.
//!
//! Selected Case-A functions from Grackle 3.4.1, commit
//! af7939494ce65007887ada7b98d1813df6843346, rate_functions.c.
//! Copyright Enzo/Grackle development team; retained license and independent
//! literal-C reference are in tests/data/igm_grackle/. No call to the raw
//! provider is made, and its 100 K guard remains unchanged.
use crate::ForwardError;
#[derive(Clone, Copy, Debug, Default)]
pub struct IgmRateDiagnostics {
    /// Full coefficient of each floor-selected CI channel, not an excess correction.
    pub ci_floor_cm3_s: [f64; 3],
    /// Full coefficient of each cap-active CE channel; units follow ce_erg.
    pub ce_cap_erg: [f64; 3],
    pub dr_excluded_erg_cm3_s: f64,
    pub dr_low_branch: bool,
}
#[derive(Clone, Copy, Debug, Default)]
pub struct IgmRates {
    pub ci_cm3_s: [f64; 3],
    pub rr_cm3_s: [f64; 3],
    pub dr_cm3_s: f64,
    /// HI, metastable HeI, HeII: erg cm3/s, erg cm6/s, erg cm3/s.
    /// Density products: ne*nHI, ne^2*nHeII, ne*nHeII respectively.
    pub ce_erg: [f64; 3],
    pub rr_cooling_erg_cm3_s: [f64; 3],
    pub dr_cooling_erg_cm3_s: f64,
    pub dr_raw_cooling_erg_cm3_s: f64,
    pub freefree_erg_cm3_s: f64,
    pub diagnostics: IgmRateDiagnostics,
}

#[derive(Clone, Copy)]
enum Process {
    K1,
    K2,
    K3,
    K5,
    K6,
    CeHI,
    CeHeI,
    CeHeII,
    ReHII,
    ReHeII1,
    ReHeII2,
    ReHeIII,
    Brem,
}
// Exact Grackle defaults, deliberately distinct from EOS CODATA kB.
const TINY: f64 = 1e-20;
const TEVK: f64 = 11605.0;
const KBOLTZ: f64 = 1.3806504e-16;
const LN_DHUGE: f64 = 69.07755278982137;
/// Operational package domain, not empirical support. No clamping of T.
/// Source literals: Grackle af7939494ce65007887ada7b98d1813df6843346.
/// CI floors and CE exponent caps are retained; DR cooling is disabled where
/// k4's DR reaction is disabled. Its excluded source residual remains visible.
pub fn igm_rates(t: f64) -> Result<IgmRates, ForwardError> {
    if !t.is_finite() || !(1.0..=1e6).contains(&t) {
        return Err(ForwardError::InvalidInput("IGM_TEMPERATURE_DOMAIN"));
    }
    use Process::*;
    let c = |p| source_coefficient(p, t);
    let ci = [c(K1)?, c(K3)?, c(K5)?];
    let te = t / TEVK;
    let low = te <= 0.8;
    let (rr_he, dr) = he_recombination(t);
    let ce = [c(CeHI)?, c(CeHeI)?, c(CeHeII)?];
    let dr_raw = c(ReHeII2)?;
    Ok(IgmRates {
        ci_cm3_s: ci,
        rr_cm3_s: [c(K2)?, rr_he, c(K6)?],
        dr_cm3_s: dr,
        ce_erg: ce,
        rr_cooling_erg_cm3_s: [c(ReHII)?, c(ReHeII1)?, c(ReHeIII)?],
        dr_cooling_erg_cm3_s: if low { 0.0 } else { dr_raw },
        dr_raw_cooling_erg_cm3_s: dr_raw,
        freefree_erg_cm3_s: c(Brem)?,
        diagnostics: IgmRateDiagnostics {
            ci_floor_cm3_s: std::array::from_fn(|i| if low && ci[i] == TINY { ci[i] } else { 0.0 }),
            ce_cap_erg: std::array::from_fn(|i| {
                if [118348.0, 13179.0, 473638.0][i] / t > LN_DHUGE {
                    ce[i]
                } else {
                    0.0
                }
            }),
            dr_excluded_erg_cm3_s: if low { dr_raw } else { 0.0 },
            dr_low_branch: low,
        },
    })
}
// Preserve the original C source literals, including excess decimal digits.
#[allow(clippy::excessive_precision)]
fn source_coefficient(process: Process, t: f64) -> Result<f64, ForwardError> {
    if !t.is_finite() || !(1.0..=1e6).contains(&t) {
        return Err(ForwardError::InvalidInput("IGM_TEMPERATURE_DOMAIN"));
    }
    use Process::*;
    let te = t / TEVK;
    let l = te.ln();
    let k1 = || {
        let v = (-32.71396786375 + 13.53655609057 * l - 5.739328757388 * l.powi(2)
            + 1.563154982022 * l.powi(3)
            - 0.2877056004391 * l.powi(4)
            + 0.03482559773736999 * l.powi(5)
            - 0.00263197617559 * l.powi(6)
            + 0.0001119543953861 * l.powi(7)
            - 2.039149852002e-6 * l.powi(8))
        .exp();
        if te <= 0.8 {
            v.max(TINY)
        } else {
            v
        }
    };
    let k3 = || {
        if te > 0.8 {
            (-44.09864886561001 + 23.91596563469 * l - 10.75323019821 * l.powi(2)
                + 3.058038757198 * l.powi(3)
                - 0.5685118909884001 * l.powi(4)
                + 0.06795391233790001 * l.powi(5)
                - 0.005009056101857001 * l.powi(6)
                + 0.0002067236157507 * l.powi(7)
                - 3.649161410833e-6 * l.powi(8))
            .exp()
        } else {
            TINY
        }
    };
    let k5 = || {
        if te > 0.8 {
            (-68.71040990212001 + 43.93347632635 * l - 18.48066993568 * l.powi(2)
                + 4.701626486759002 * l.powi(3)
                - 0.7692466334492 * l.powi(4)
                + 0.08113042097303 * l.powi(5)
                - 0.005324020628287001 * l.powi(6)
                + 0.0001975705312221 * l.powi(7)
                - 3.165581065665e-6 * l.powi(8))
            .exp()
        } else {
            TINY
        }
    };
    let v = match process {
        K1 => k1(),
        K2 => {
            if t > 5500.0 {
                (-28.61303380689232
                    - 0.7241125657826851 * l
                    - 0.02026044731984691 * l.powi(2)
                    - 0.002380861877349834 * l.powi(3)
                    - 0.0003212605213188796 * l.powi(4)
                    - 0.00001421502914054107 * l.powi(5)
                    + 4.989108920299513e-6 * l.powi(6)
                    + 5.755614137575758e-7 * l.powi(7)
                    - 1.856767039775261e-8 * l.powi(8)
                    - 3.071135243196595e-9 * l.powi(9))
                .exp()
            } else {
                he_recombination(t).0
            }
        }
        K3 => k3(),
        K5 => k5(),
        K6 => 3.36e-10 / t.sqrt() / (t / 1e3).powf(0.2) / (1.0 + (t / 1e6).powf(0.7)),
        CeHI => 7.5e-19 * (-(118348.0 / t).min(LN_DHUGE)).exp() / (1.0 + (t / 1e5).sqrt()),
        CeHeI => {
            9.1e-27 * (-(13179.0 / t).min(LN_DHUGE)).exp() * t.powf(-0.1687)
                / (1.0 + (t / 1e5).sqrt())
        }
        CeHeII => {
            5.54e-17 * (-(473638.0 / t).min(LN_DHUGE)).exp() * t.powf(-0.3970)
                / (1.0 + (t / 1e5).sqrt())
        }
        ReHII => {
            let lambda = 2.0 * 157807.0 / t;

            1.778e-29 * t * lambda.powf(1.965) / (1.0 + (lambda / 0.541).powf(0.502)).powf(2.697)
        }
        ReHeII1 => {
            let lambda = 2.0 * 285335.0 / t;

            3e-14 * KBOLTZ * t * lambda.powf(0.654)
        }
        ReHeII2 => {
            1.24e-13
                * t.powf(-1.5)
                * (-(470000.0 / t).min(LN_DHUGE)).exp()
                * (1.0 + 0.3 * (-(94000.0 / t).min(LN_DHUGE)).exp())
        }
        ReHeIII => {
            let lambda = 2.0 * 631515.0 / t;
            // Preserve original raw 8*T term; no kinetic-moment substitution.

            8.0 * 1.778e-29 * t * lambda.powf(1.965)
                / (1.0 + (lambda / 0.541).powf(0.502)).powf(2.697)
        }
        Brem => 1.43e-27 * t.sqrt() * (1.1 + 0.34 * (-(5.5 - t.log10()).powi(2) / 3.0).exp()),
    };
    if !v.is_finite() || v < 0.0 {
        return Err(ForwardError::InvalidInput("IGM_COEFFICIENT_INVALID"));
    }
    Ok(v)
}

// The two k4 summands, evaluated separately to avoid cancellation in tiny DR.
fn he_recombination(t: f64) -> (f64, f64) {
    let te = t / TEVK;
    let rr = 3.92e-13 / te.powf(0.6353);
    let dr = if te <= 0.8 {
        0.0
    } else {
        1.54e-9 * (1.0 + 0.3 / (8.099328789667 / te).exp())
            / ((40.49664394833662 / te).exp() * te.powf(1.5))
    };
    (rr, dr)
}
