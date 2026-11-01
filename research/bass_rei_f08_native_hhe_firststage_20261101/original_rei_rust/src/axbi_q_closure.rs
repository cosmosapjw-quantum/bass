//! Positive two-moment bounded-exponential photon spectrum reconstruction.
//! C6 scientific repair: split H/He photoelectric thresholds before integrating
//! opacity and gas heating. This is a closure, not the unique true spectrum.
use crate::{Absorber, AtomicProvider, ForwardError, HHeModel};

const X8: [f64; 8] = [
    -0.9602898564975363,
    -0.7966664774136267,
    -0.5255324099163290,
    -0.1834346424956498,
    0.1834346424956498,
    0.5255324099163290,
    0.7966664774136267,
    0.9602898564975363,
];
const W8: [f64; 8] = [
    0.1012285362903763,
    0.2223810344533745,
    0.3137066458778873,
    0.3626837833783619,
    0.3626837833783619,
    0.3137066458778873,
    0.2223810344533745,
    0.1012285362903763,
];
fn bad() -> ForwardError {
    ForwardError::InvalidInput("AXBI_Q_EXPONENTIAL_CLOSURE_DOMAIN")
}
fn valid(v: f64) -> bool {
    v.is_finite() && v >= 0.0
}
fn mean_x(beta: f64) -> f64 {
    let b = beta.abs();
    if b < 1e-3 {
        let b2 = beta * beta;
        beta * (1.0 / 3.0 - b2 / 45.0 + 2.0 * b2 * b2 / 945.0 - b2 * b2 * b2 / 4725.0)
    } else {
        beta.signum() * (1.0 + 2.0 / (2.0 * b).exp_m1() - 1.0 / b)
    }
}
fn variance_x(beta: f64) -> f64 {
    let b = beta.abs();
    if b < 1e-3 {
        let b2 = b * b;
        1.0 / 3.0 - b2 / 15.0 + 2.0 * b2 * b2 / 189.0
    } else if b > 30.0 {
        1.0 / (b * b)
    } else {
        1.0 / (b * b) - 1.0 / b.sinh().powi(2)
    }
}
#[derive(Clone, Copy, Debug)]
pub struct PositiveReconstruction {
    pub lower_ev: f64,
    pub upper_ev: f64,
    pub beta: f64,
    pub normalizer: f64,
}
impl PositiveReconstruction {
    pub fn mean_ev(&self) -> f64 {
        (self.lower_ev + self.upper_ev) * 0.5
            + (self.upper_ev - self.lower_ev) * 0.5 * mean_x(self.beta)
    }
}
pub fn positive_reconstruct(
    lo: f64,
    hi: f64,
    mean: f64,
) -> Result<PositiveReconstruction, ForwardError> {
    if !(lo.is_finite()
        && hi.is_finite()
        && mean.is_finite()
        && hi > lo
        && lo > 0.0
        && mean > lo
        && mean < hi)
    {
        return Err(bad());
    }
    let eta = (2.0 * mean - lo - hi) / (hi - lo);
    if eta.abs() >= 1.0 {
        return Err(bad());
    }
    let beta = if eta == 0.0 {
        0.0
    } else {
        let mut left = 0.0;
        let mut right = (2.0 / (1.0 - eta.abs())).max(2.0);
        if right > 25000.0 {
            return Err(bad());
        }
        let mut guess = if eta.abs() < 0.4 {
            3.0 * eta.abs()
        } else {
            1.0 / (1.0 - eta.abs())
        };
        guess = guess.clamp(left, right);
        for _ in 0..64 {
            let m = mean_x(guess);
            if m < eta.abs() {
                left = guess;
            } else {
                right = guess;
            }
            if (m - eta.abs()).abs() <= 2e-14 {
                break;
            }
            let deriv = variance_x(guess);
            let candidate = guess - (m - eta.abs()) / deriv;
            guess = if candidate.is_finite() && candidate > left && candidate < right {
                candidate
            } else {
                0.5 * (left + right)
            };
        }
        eta.signum() * guess
    };
    if (mean_x(beta) - eta).abs() > 2e-10 {
        return Err(bad());
    }
    let ab = beta.abs();
    let normalizer = if ab < 1e-5 {
        2.0 * (1.0 + beta * beta / 6.0 + beta.powi(4) / 120.0) * (-ab).exp()
    } else {
        -(-2.0 * ab).exp_m1() / ab
    };
    if !(normalizer.is_finite() && normalizer > 0.0) {
        return Err(bad());
    }
    Ok(PositiveReconstruction {
        lower_ev: lo,
        upper_ev: hi,
        beta,
        normalizer,
    })
}
#[derive(Clone, Copy, Debug, Default)]
pub struct PositiveBinAbsorption {
    pub surviving_photons_per_h: f64,
    pub surviving_energy_moment_ev_per_h: f64,
    pub absorbed_per_h: [f64; 3],
    pub binding_ev_per_h: f64,
    pub heat_ev_per_h: f64,
    pub quadrature_count_defect: f64,
    pub quadrature_mean_defect_ev: f64,
}
/// Frozen physical gas opacities, positive two-moment spectral shape in E_ref.
/// Threshold splitting occurs at each actual FIT threshold divided by R.
pub fn absorb_positive_bin(
    lo: f64,
    hi: f64,
    n: f64,
    uref: f64,
    r: f64,
    neutrals: [f64; 3],
    dt: f64,
) -> Result<PositiveBinAbsorption, ForwardError> {
    if !(valid(n)
        && n > 0.0
        && valid(uref)
        && r.is_finite()
        && r > 0.0
        && valid(dt)
        && neutrals.iter().all(|x| valid(*x)))
    {
        return Err(bad());
    }
    let mean = uref / n;
    let fit = positive_reconstruct(lo, hi, mean)?;
    let model = HHeModel::controlled_fixture();
    let provider = AtomicProvider::reference();
    let species = [Absorber::HI, Absorber::HeI, Absorber::HeII];
    let thresholds = [13.60, 24.59, 54.42];
    let mut points = [0.0; 5];
    points[0] = lo;
    let mut count = 1;
    for edge in thresholds {
        let cut = edge / r;
        if cut > lo && cut < hi {
            points[count] = cut;
            count += 1;
        }
    }
    points[count] = hi;
    count += 1;
    let mut out = PositiveBinAbsorption::default();
    let mid = (lo + hi) * 0.5;
    let half = (hi - lo) * 0.5;
    let mut total_weight = 0.0;
    let mut quadrature_uref = 0.0;
    let mut lost_n = 0.0;
    let mut lost_uref = 0.0;
    let steep = fit.beta.abs();
    for pair in points[..count].windows(2) {
        let (a, b) = (pair[0], pair[1]);
        // Keep each exponent change <=3 across a subpanel when beta is large.
        let panels = (((b - a) / (hi - lo) * steep / 3.0).ceil() as usize).max(1);
        if panels > 2048 {
            return Err(bad());
        }
        for panel in 0..panels {
            let l = a + (b - a) * (panel as f64) / (panels as f64);
            let h = a + (b - a) * ((panel + 1) as f64) / (panels as f64);
            let hm = (h - l) * 0.5;
            let center = (l + h) * 0.5;
            for idx in 0..8 {
                let eref = center + hm * X8[idx];
                let x = (eref - mid) / half;
                let fraction = (fit.beta * x - steep).exp() / fit.normalizer * W8[idx] * hm / half;
                let incoming = n * fraction;
                total_weight += fraction;
                quadrature_uref += fraction * eref;
                let e = eref * r;
                let mut rates = [0.0; 3];
                for j in 0..3 {
                    if neutrals[j] > 0.0 && e >= thresholds[j] {
                        rates[j] =
                            model.c_cm_s * neutrals[j] * provider.cross_section(species[j], e)?;
                    }
                }
                let lambda: f64 = rates.iter().sum();
                if lambda <= 0.0 {
                    continue;
                }
                let event = incoming * (-(-lambda * dt).exp_m1());
                lost_n += event;
                lost_uref += event * eref;
                for j in 0..3 {
                    let absorbed = event * rates[j] / lambda;
                    out.absorbed_per_h[j] += absorbed;
                    out.binding_ev_per_h += absorbed * model.threshold_ev[j];
                    out.heat_ev_per_h += absorbed * (e - model.threshold_ev[j]);
                }
            }
        }
    }
    out.quadrature_count_defect = total_weight - 1.0;
    out.quadrature_mean_defect_ev = quadrature_uref - mean;
    if total_weight.is_nan()
        || (total_weight - 1.0).abs() > 2e-9
        || (quadrature_uref - mean).abs() > 2e-9 * (hi - lo)
    {
        return Err(bad());
    }
    out.surviving_photons_per_h = n - lost_n;
    out.surviving_energy_moment_ev_per_h = uref - lost_uref;
    if !(valid(out.surviving_photons_per_h)
        && valid(out.surviving_energy_moment_ev_per_h)
        && out.surviving_energy_moment_ev_per_h <= hi * out.surviving_photons_per_h * (1.0 + 1e-9)
        && out.surviving_energy_moment_ev_per_h >= lo * out.surviving_photons_per_h * (1.0 - 1e-9))
    {
        return Err(bad());
    }
    Ok(out)
}
