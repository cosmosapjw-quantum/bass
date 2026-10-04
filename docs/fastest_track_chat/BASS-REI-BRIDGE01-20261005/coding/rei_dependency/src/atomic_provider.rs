//! Scoped reference values from Grackle 3.4.1 and Verner et al. (1996).
//!
//! Grackle source: commit af7939494ce65007887ada7b98d1813df6843346,
//! `rate_functions.c`; copyright Enzo/Grackle development team. Its license
//! is retained in the handoff's `common/external_reference/grackle_3_4_1/LICENSE`.
//! These raw values are not a
//! physical-source admission or a thermal closure.

use crate::ForwardError;

const TINY: f64 = 1e-20;
const TEVK: f64 = 11605.0;
const KBOLTZ: f64 = 1.3806504e-16;
const LN_DHUGE: f64 = 69.07755278982137; // ln(1e30)
const COMMIT: &str = "af7939494ce65007887ada7b98d1813df6843346";

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RecombinationCase {
    A,
    B,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CoefficientUnits {
    Cm3PerSecond,
    ErgCm3PerSecond,
    ErgCm6PerSecond,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct RawCoefficient {
    pub value: f64,
    pub unit: CoefficientUnits,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RawProcess {
    K1,
    K2,
    K3,
    K4,
    K5,
    K6,
    CeHI,
    CeHeI,
    CeHeII,
    CiHeIS,
    CiHI,
    CiHeI,
    CiHeII,
    ReHII,
    ReHeII1,
    ReHeII2,
    ReHeIII,
    Brem,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Absorber {
    HI,
    HeI,
    HeII,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SourceFrame {
    GasRest,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ObservableKind {
    ThermalRate,
    CoolingCoefficient,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct TemperatureDomain {
    pub minimum_k: f64,
    pub maximum_k: f64,
    pub physical_support_resolved: bool,
}

#[derive(Debug, Clone, Copy)]
pub struct RawRecord {
    pub source_function: &'static str,
    pub source_commit: &'static str,
    pub consumer_admission: bool,
    pub density_prefactor: &'static str,
    /// HI, HII, HeI, HeII, HeIII, electron.
    pub species_change: [i8; 6],
    pub frame: SourceFrame,
    pub frame_description: &'static str,
    pub distribution: &'static str,
    pub domain: TemperatureDomain,
    pub reference_domain: &'static str,
    pub observable_kind: ObservableKind,
    pub observable: &'static str,
    pub provenance: &'static str,
}

#[derive(Debug, Clone, Copy, Default)]
pub struct AtomicProvider;

impl AtomicProvider {
    /// Returns a raw reference-value provider; no physical consumer is admitted.
    pub fn reference() -> Self {
        Self
    }

    pub fn record(&self, process: RawProcess) -> RawRecord {
        use RawProcess::*;
        let (source_function, density_prefactor, species_change) = match process {
            K1 => ("k1_rate", "n_e*n_HI", [-1, 1, 0, 0, 0, 1]),
            K2 => ("k2_rate", "n_e*n_HII", [1, -1, 0, 0, 0, -1]),
            K3 => ("k3_rate", "n_e*n_HeI", [0, 0, -1, 1, 0, 1]),
            K4 => ("k4_rate", "n_e*n_HeII", [0, 0, 1, -1, 0, -1]),
            K5 => ("k5_rate", "n_e*n_HeII", [0, 0, 0, -1, 1, 1]),
            K6 => ("k6_rate", "n_e*n_HeIII", [0, 0, 0, 1, -1, -1]),
            CeHI => ("ceHI_rate", "n_e*n_HI", [0; 6]),
            CeHeI => ("ceHeI_rate", "n_e^2*n_HeII", [0; 6]),
            CeHeII => ("ceHeII_rate", "n_e*n_HeII", [0; 6]),
            CiHeIS => ("ciHeIS_rate", "n_e^2*n_HeII", [0; 6]),
            CiHI => ("ciHI_rate", "n_e*n_HI", [0; 6]),
            CiHeI => ("ciHeI_rate", "n_e*n_HeI", [0; 6]),
            CiHeII => ("ciHeII_rate", "n_e*n_HeII", [0; 6]),
            ReHII => ("reHII_rate", "n_e*n_HII", [0; 6]),
            ReHeII1 => ("reHeII1_rate", "n_e*n_HeII", [0; 6]),
            ReHeII2 => ("reHeII2_rate", "n_e*n_HeII", [0; 6]),
            ReHeIII => ("reHeIII_rate", "n_e*n_HeIII", [0; 6]),
            Brem => ("brem_rate", "n_e*(n_HII+n_HeII+4*n_HeIII)", [0; 6]),
        };
        RawRecord {
            source_function,
            source_commit: COMMIT,
            consumer_admission: false,
            density_prefactor,
            species_change,
            frame: SourceFrame::GasRest,
            frame_description: "gas-rest thermal coefficient with proper gas density",
            distribution: "Grackle original temperature fit; enabled cooling flags",
            domain: TemperatureDomain {
                minimum_k: 100.0,
                maximum_k: 1e9,
                physical_support_resolved: false,
            },
            reference_domain: "finite 100 <= T/K <= 1e9; implementation guard only",
            observable_kind: match process {
                K1 | K2 | K3 | K4 | K5 | K6 => ObservableKind::ThermalRate,
                _ => ObservableKind::CoolingCoefficient,
            },
            observable: "raw source coefficient, not modeled cooling",
            provenance: "Grackle 3.4.1 exact isolated rate bodies at units=1",
        }
    }

    // Preserve the original C source literals, including excess decimal digits.
    #[allow(clippy::excessive_precision)]
    pub fn raw_coefficient(
        &self,
        process: RawProcess,
        t: f64,
        case: RecombinationCase,
    ) -> Result<RawCoefficient, ForwardError> {
        if !t.is_finite() || !(100.0..=1e9).contains(&t) {
            return Err(ForwardError::InvalidInput("RAW_TEMPERATURE_DOMAIN"));
        }
        use RawProcess::*;
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
        let k4 = || {
            if case == RecombinationCase::B {
                1.26e-14 * (5.7067e5 / t).powf(0.75)
            } else if te > 0.8 {
                1.54e-9 * (1.0 + 0.3 / (8.099328789667 / te).exp())
                    / ((40.49664394833662 / te).exp() * te.powf(1.5))
                    + 3.92e-13 / te.powf(0.6353)
            } else {
                3.92e-13 / te.powf(0.6353)
            }
        };
        let v = match process {
            K1 => k1(),
            K2 => {
                if case == RecombinationCase::B {
                    if t < 1e9 {
                        4.881357e-6 * t.powf(-1.5) * (1.0 + 1.14813e2 * t.powf(-0.407)).powf(-2.242)
                    } else {
                        TINY
                    }
                } else if t > 5500.0 {
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
                    k4()
                }
            }
            K3 => k3(),
            K4 => k4(),
            K5 => k5(),
            K6 => {
                if case == RecombinationCase::B {
                    if t < 1e9 {
                        7.8155e-5 * t.powf(-1.5) * (1.0 + 2.0189e2 * t.powf(-0.407)).powf(-2.242)
                    } else {
                        TINY
                    }
                } else {
                    3.36e-10 / t.sqrt() / (t / 1e3).powf(0.2) / (1.0 + (t / 1e6).powf(0.7))
                }
            }
            CeHI => 7.5e-19 * (-(118348.0 / t).min(LN_DHUGE)).exp() / (1.0 + (t / 1e5).sqrt()),
            CeHeI => {
                9.1e-27 * (-(13179.0 / t).min(LN_DHUGE)).exp() * t.powf(-0.1687)
                    / (1.0 + (t / 1e5).sqrt())
            }
            CeHeII => {
                5.54e-17 * (-(473638.0 / t).min(LN_DHUGE)).exp() * t.powf(-0.3970)
                    / (1.0 + (t / 1e5).sqrt())
            }
            CiHeIS => {
                5.01e-27 * t.powf(-0.1687) / (1.0 + (t / 1e5).sqrt())
                    * (-(55338.0 / t).min(LN_DHUGE)).exp()
            }
            CiHI => 2.18e-11 * k1(),
            CiHeI => 3.94e-11 * k3(),
            CiHeII => 8.72e-11 * k5(),
            ReHII => {
                let lambda = 2.0 * 157807.0 / t;
                if case == RecombinationCase::B {
                    3.435e-30 * t * lambda.powf(1.970)
                        / (1.0 + (lambda / 2.25).powf(0.376)).powf(3.720)
                } else {
                    1.778e-29 * t * lambda.powf(1.965)
                        / (1.0 + (lambda / 0.541).powf(0.502)).powf(2.697)
                }
            }
            ReHeII1 => {
                let lambda = 2.0 * 285335.0 / t;
                if case == RecombinationCase::B {
                    1.26e-14 * KBOLTZ * t * lambda.powf(0.75)
                } else {
                    3e-14 * KBOLTZ * t * lambda.powf(0.654)
                }
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
                if case == RecombinationCase::B {
                    8.0 * 3.435e-30 * t * lambda.powf(1.970)
                        / (1.0 + (lambda / 2.25).powf(0.376)).powf(3.720)
                } else {
                    8.0 * 1.778e-29 * t * lambda.powf(1.965)
                        / (1.0 + (lambda / 0.541).powf(0.502)).powf(2.697)
                }
            }
            Brem => 1.43e-27 * t.sqrt() * (1.1 + 0.34 * (-(5.5 - t.log10()).powi(2) / 3.0).exp()),
        };
        if !v.is_finite() || v < 0.0 {
            return Err(ForwardError::InvalidInput("RAW_COEFFICIENT_INVALID"));
        }
        let unit = match process {
            K1 | K2 | K3 | K4 | K5 | K6 => CoefficientUnits::Cm3PerSecond,
            CeHeI | CiHeIS => CoefficientUnits::ErgCm6PerSecond,
            _ => CoefficientUnits::ErgCm3PerSecond,
        };
        Ok(RawCoefficient { value: v, unit })
    }

    /// Verner ground-state outer-shell fit. Fit thresholds differ from binding energies.
    pub fn cross_section(&self, absorber: Absorber, energy_ev: f64) -> Result<f64, ForwardError> {
        if !energy_ev.is_finite() || energy_ev < 0.0 {
            return Err(ForwardError::InvalidInput("PHOTON_ENERGY_INVALID"));
        }
        if energy_ev > 50000.0 {
            return Err(ForwardError::InvalidInput("VERNER_ENERGY_DOMAIN"));
        }
        let (eth, e0, sigma0, ya, p, yw, y0, y1) = match absorber {
            Absorber::HI => (13.60, 0.4298, 5.475e4, 32.88, 2.963, 0.0, 0.0, 0.0),
            Absorber::HeI => (24.59, 13.61, 949.2, 1.469, 3.188, 2.039, 0.4434, 2.136),
            Absorber::HeII => (54.42, 1.720, 1.369e4, 32.88, 2.963, 0.0, 0.0, 0.0),
        };
        if energy_ev < eth {
            return Ok(0.0);
        }
        let x = energy_ev / e0 - y0;
        let y = (x * x + y1 * y1).sqrt();
        let sigma = sigma0
            * ((x - 1.0).powi(2) + yw * yw)
            * y.powf(p / 2.0 - 5.5)
            * (1.0 + (y / ya).sqrt()).powf(-p)
            * 1e-18;
        if !sigma.is_finite() || sigma < 0.0 {
            return Err(ForwardError::InvalidInput("VERNER_RESULT_INVALID"));
        }
        Ok(sigma)
    }
}
