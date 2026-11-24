//! Full-sky deterministic T/E/B analysis of a positively weighted observer quadrature.
//!
//! Directions point from the observer towards the sky. Q+iU is specified in
//! the right-handed (e_theta,e_phi) arrival-sky screen (at poles use phi=0).
//! A caller with photon propagation n must first express the data at s=-n:
//! e_theta is unchanged and e_phi is reversed, hence U changes sign.
//! Samples and their dOmega weights already belong to the observer frame.
//! Raw positive solid angles are used without a sum-to-4pi renormalization.
//!
//! With _sY_lm=(-1)^s sqrt((2l+1)/(4pi)) d^l_{m,-s} exp(im phi), define
//! a_± = integral[(Q±iU) conj(_±2Y)] dOmega. HEALPix/COSMO (Zaldarriaga &
//! Seljak 1997) gives E=−(a_++a_-)/2 and B=i(a_+−a_-)/2. Dossier II's
//! positive definitions have E_D=−E and B_D=−B with the same sky and dyad.
//! Each block has the supplied T, Q/U field units; the caller names these.

use std::f64::consts::{LN_2, PI};

#[derive(Clone, Copy, Debug)]
pub struct SkySample {
    pub direction: [f64; 3],
    pub weight: f64,
    pub t: f64,
    pub q: f64,
    pub u: f64,
}

#[derive(Clone, Copy, Debug)]
pub struct Mode {
    pub ell: usize,
    pub m: i32,
    /// T, E, B, each stored as [real, imaginary].
    pub alm: [[f64; 2]; 3],
}

#[derive(Clone, Copy)]
struct Step {
    factor: f64,
    offset: f64,
    previous: f64,
}

struct Column {
    first: usize,
    log_seed_factor: f64,
    cos_power: i32,
    sin_power: i32,
    sign: f64,
    steps: Vec<Step>,
}

fn parity(i: i32) -> f64 {
    if i % 2 == 0 {
        1.0
    } else {
        -1.0
    }
}

impl Column {
    // Start with the single nonzero factorial term at j=max(m,|n|), avoiding
    // the cancellation of an alternating factorial sum at every degree.
    fn new(m: i32, n: i32, lmax: usize, log_fact: &[f64]) -> Option<Self> {
        let j = m.max(n.abs());
        if j as usize > lmax {
            return None;
        }
        let k = (n - m).max(0);
        let lf = |i: i32| log_fact[i as usize];
        let log_seed_factor = 0.5 * (lf(j + n) + lf(j - n) + lf(j + m) + lf(j - m))
            - lf(j + n - k)
            - lf(k)
            - lf(j - m - k)
            - lf(k - n + m);
        let mut steps = Vec::with_capacity(lmax - j as usize);
        let m2 = (m as f64).powi(2);
        let n2 = (n as f64).powi(2);
        for ell in j as usize..lmax {
            let l = ell as f64;
            let lp = l + 1.0;
            let factor = lp * (2.0 * l + 1.0) / ((lp * lp - m2) * (lp * lp - n2)).sqrt();
            let offset = if ell == 0 {
                0.0
            } else {
                m as f64 * n as f64 / (l * lp)
            };
            let previous = if ell == 0 {
                0.0
            } else {
                factor * ((l * l - m2) * (l * l - n2)).sqrt() / (l * (2.0 * l + 1.0))
            };
            steps.push(Step {
                factor,
                offset,
                previous,
            });
        }
        Some(Self {
            first: j as usize,
            log_seed_factor,
            cos_power: 2 * j - 2 * k + n - m,
            sin_power: 2 * k - n + m,
            sign: parity(k - m + n),
            steps,
        })
    }

    fn evaluate(&self, z: f64, logs: [f64; 2], mut accept: impl FnMut(usize, f64)) {
        let mut log_seed = self.log_seed_factor;
        if self.cos_power != 0 {
            log_seed += f64::from(self.cos_power) * logs[0];
        }
        if self.sin_power != 0 {
            log_seed += f64::from(self.sin_power) * logs[1];
        }
        if !log_seed.is_finite() {
            return;
        } // identically zero at this pole
          // Track a shared binary exponent so a tiny sectoral seed can grow
          // into a representable mode at higher degrees near a polar cap.
        let binary = log_seed / LN_2;
        let mut exponent = binary.floor() as i32;
        let mut previous = 0.0;
        let mut current = self.sign * (binary - f64::from(exponent)).exp2();
        let unscale = |v: f64, e: i32| {
            if e < -1074 {
                (v * 2.0f64.powi(-512)) * 2.0f64.powi((e + 512).max(-1075))
            } else {
                v * 2.0f64.powi(e)
            }
        };
        accept(self.first, unscale(current, exponent));
        for (i, step) in self.steps.iter().enumerate() {
            let next = step.factor * (z - step.offset) * current - step.previous * previous;
            previous = current;
            current = next;
            if current.abs().max(previous.abs()) > 1e100 {
                previous *= 2.0f64.powi(-256);
                current *= 2.0f64.powi(-256);
                exponent += 256;
            }
            accept(self.first + i + 1, unscale(current, exponent));
        }
    }
}

/// Return all signed m in increasing (ell,m) order. The mode's flat index is
/// ell*(ell+1)+m. The quadrature estimates inner products, including any
/// residual sampling/alias error of the supplied directions and weights.
pub fn analyze(sky: &[SkySample], lmax: usize) -> Result<Vec<Mode>, String> {
    if sky.is_empty() {
        return Err("empty sky".to_owned());
    }
    if lmax > (i32::MAX / 4) as usize {
        return Err("multipole index out of range".to_owned());
    }
    let n_modes = (lmax + 1).checked_pow(2).ok_or("mode count overflow")?;
    let mut modes = Vec::new();
    modes
        .try_reserve_exact(n_modes)
        .map_err(|e| e.to_string())?;
    for l in 0..=lmax {
        for m in -(l as i32)..=l as i32 {
            modes.push(Mode {
                ell: l,
                m,
                alm: [[0.0; 2]; 3],
            });
        }
    }
    let norm: Vec<f64> = (0..=lmax)
        .map(|l| (((2 * l + 1) as f64) / (4.0 * PI)).sqrt())
        .collect();
    let mut log_fact = vec![0.0; 2 * lmax + 1];
    for i in 1..log_fact.len() {
        log_fact[i] = log_fact[i - 1] + (i as f64).ln();
    }
    let columns: Vec<_> = (0..=lmax)
        .map(|m| [0, -2, 2].map(|n| Column::new(m as i32, n, lmax, &log_fact)))
        .collect();
    for sample in sky {
        let [x, y, z] = sample.direction;
        let radius = x.hypot(y);
        let len = radius.hypot(z);
        if !len.is_finite()
            || (len - 1.0).abs() > 1e-9
            || !sample.weight.is_finite()
            || sample.weight <= 0.0
            || ![sample.t, sample.q, sample.u].iter().all(|v| v.is_finite())
        {
            return Err(
                "expected unit direction, positive solid angle, and finite T/Q/U".to_owned(),
            );
        }
        let (cp, sp) = if radius == 0.0 {
            (1.0, 0.0)
        } else {
            (x / radius, y / radius)
        };
        let z = z / len;
        let (ch, sh) = if z >= 0.0 {
            let ch = ((1.0 + z) / 2.0).sqrt();
            (ch, radius / (2.0 * len * ch))
        } else {
            let sh = ((1.0 - z) / 2.0).sqrt();
            (radius / (2.0 * len * sh), sh)
        };
        let logs = [ch.ln(), sh.ln()];
        let (mut re, mut im) = (1.0, 0.0);
        for (m, columns_m) in columns.iter().enumerate() {
            for (field, column) in columns_m.iter().enumerate() {
                let Some(column) = column else {
                    continue;
                };
                let (real, imag) = match field {
                    0 => (re * sample.t, im * sample.t),
                    1 => (re * sample.q - im * sample.u, im * sample.q + re * sample.u),
                    _ => (re * sample.q + im * sample.u, im * sample.q - re * sample.u),
                };
                column.evaluate(z, logs, |l, d| {
                    let fac = sample.weight * norm[l] * d;
                    let a = &mut modes[l * (l + 1) + m].alm;
                    if field == 0 {
                        a[0][0] += fac * real;
                        a[0][1] += fac * imag;
                    } else {
                        let half = 0.5 * fac;
                        a[1][0] -= half * real;
                        a[1][1] -= half * imag;
                        let sign = if field == 1 { 1.0 } else { -1.0 };
                        a[2][0] -= sign * half * imag;
                        a[2][1] += sign * half * real;
                    }
                });
            }
            (re, im) = (re * cp + im * sp, im * cp - re * sp);
        }
    }
    for l in 0..=lmax {
        let center = l * (l + 1);
        for v in &mut modes[center].alm {
            v[1] = 0.0;
        }
        for m in 1..=l {
            let sign = parity(m as i32);
            modes[center - m].alm = modes[center + m].alm.map(|[r, i]| [sign * r, -sign * i]);
        }
    }
    if modes
        .iter()
        .any(|mode| !mode.alm.iter().flatten().all(|v| v.is_finite()))
    {
        return Err("nonfinite harmonic coefficient".to_owned());
    }
    Ok(modes)
}

/// Ring version of [`analyze`] for iso-latitude grids with uniform azimuths
/// phi_k = 2 pi k / n_phi and one weight per ring (e.g. Gauss-Legendre x phi).
/// Fields are ring-major (index ring * n_phi + k). The same Wigner columns and
/// E/B combination are used; only the floating-point summation order differs,
/// and the cost is O(rings * n_phi * lmax + rings * lmax^2).
pub fn analyze_rings(
    cos_theta: &[f64],
    ring_weight: &[f64],
    n_phi: usize,
    t: &[f64],
    q: &[f64],
    u: &[f64],
    lmax: usize,
) -> Result<Vec<Mode>, String> {
    let rings = cos_theta.len();
    if rings == 0 || n_phi == 0 || ring_weight.len() != rings {
        return Err("ring grid needs matching nonempty rings and weights".to_owned());
    }
    let n = rings.checked_mul(n_phi).ok_or("ring grid size overflow")?;
    if t.len() != n || q.len() != n || u.len() != n {
        return Err("ring fields must have rings * n_phi entries".to_owned());
    }
    if lmax > (i32::MAX / 4) as usize {
        return Err("multipole index out of range".to_owned());
    }
    if n_phi < lmax.saturating_mul(2).saturating_add(1) {
        return Err("azimuthal ring grid is below Nyquist resolution for requested lmax".to_owned());
    }
    if !t.iter().chain(q).chain(u).all(|v| v.is_finite())
        || !ring_weight.iter().all(|w| w.is_finite() && *w > 0.0)
        || !cos_theta.iter().all(|z| z.is_finite() && z.abs() < 1.0)
    {
        return Err("expected finite fields, positive ring weights and |cos theta| < 1".to_owned());
    }
    let n_modes = (lmax + 1).checked_pow(2).ok_or("mode count overflow")?;
    let mut modes = Vec::new();
    modes
        .try_reserve_exact(n_modes)
        .map_err(|e| e.to_string())?;
    for l in 0..=lmax {
        for m in -(l as i32)..=l as i32 {
            modes.push(Mode {
                ell: l,
                m,
                alm: [[0.0; 2]; 3],
            });
        }
    }
    let norm: Vec<f64> = (0..=lmax)
        .map(|l| (((2 * l + 1) as f64) / (4.0 * PI)).sqrt())
        .collect();
    let mut log_fact = vec![0.0; 2 * lmax + 1];
    for i in 1..log_fact.len() {
        log_fact[i] = log_fact[i - 1] + (i as f64).ln();
    }
    let columns: Vec<_> = (0..=lmax)
        .map(|m| [0, -2, 2].map(|n| Column::new(m as i32, n, lmax, &log_fact)))
        .collect();
    // exp(-i m phi_k) from an exact table indexed by (m k) mod n_phi.
    let table: Vec<(f64, f64)> = (0..n_phi)
        .map(|k| {
            let angle = 2.0 * PI * k as f64 / n_phi as f64;
            (angle.cos(), -angle.sin())
        })
        .collect();
    for (ring, (&z, &weight)) in cos_theta.iter().zip(ring_weight).enumerate() {
        let radius = if z.abs() > 0.99999 {
            ((1.0 - z) * (1.0 + z)).max(0.0).sqrt()
        } else {
            (1.0 - z * z).max(0.0).sqrt()
        };
        let (ch, sh) = if z >= 0.0 {
            let ch = ((1.0 + z) / 2.0).sqrt();
            (ch, radius / (2.0 * ch))
        } else {
            let sh = ((1.0 - z) / 2.0).sqrt();
            (radius / (2.0 * sh), sh)
        };
        let logs = [ch.ln(), sh.ln()];
        let offset = ring * n_phi;
        for (m, columns_m) in columns.iter().enumerate() {
            // Fourier sums of T, Q+iU and Q-iU against exp(-i m phi).
            let mut f = [[0.0f64; 2]; 3];
            for k in 0..n_phi {
                let (re, im) = table[(m * k) % n_phi];
                let (tv, qv, uv) = (t[offset + k], q[offset + k], u[offset + k]);
                f[0][0] += re * tv;
                f[0][1] += im * tv;
                f[1][0] += re * qv - im * uv;
                f[1][1] += im * qv + re * uv;
                f[2][0] += re * qv + im * uv;
                f[2][1] += im * qv - re * uv;
            }
            for (field, column) in columns_m.iter().enumerate() {
                let Some(column) = column else {
                    continue;
                };
                let (real, imag) = (f[field][0], f[field][1]);
                column.evaluate(z, logs, |l, d| {
                    let fac = weight * norm[l] * d;
                    let a = &mut modes[l * (l + 1) + m].alm;
                    if field == 0 {
                        a[0][0] += fac * real;
                        a[0][1] += fac * imag;
                    } else {
                        let half = 0.5 * fac;
                        a[1][0] -= half * real;
                        a[1][1] -= half * imag;
                        let sign = if field == 1 { 1.0 } else { -1.0 };
                        a[2][0] -= sign * half * imag;
                        a[2][1] += sign * half * real;
                    }
                });
            }
        }
    }
    for l in 0..=lmax {
        let center = l * (l + 1);
        for v in &mut modes[center].alm {
            v[1] = 0.0;
        }
        for m in 1..=l {
            let sign = parity(m as i32);
            modes[center - m].alm = modes[center + m].alm.map(|[r, i]| [sign * r, -sign * i]);
        }
    }
    if modes
        .iter()
        .any(|mode| !mode.alm.iter().flatten().all(|v| v.is_finite()))
    {
        return Err("nonfinite harmonic coefficient".to_owned());
    }
    Ok(modes)
}

/// All nine products a_X(left) conj(a_Y(right)), including independent
/// imaginary parts for distinct fields and for off-diagonal mode pairs.
pub fn outer(left: &Mode, right: &Mode) -> [[[f64; 2]; 3]; 3] {
    left.alm
        .map(|[a, b]| right.alm.map(|[c, d]| [a * c + b * d, b * c - a * d]))
}

/// TT, TE, TB, EE, EB, BB, in that order. Real parts for the same mode
/// give the six deterministic C_lm^{XY}; sum all m and divide by 2l+1
/// for the angular average. An ensemble covariance requires an expectation.
pub fn products(left: &Mode, right: &Mode) -> [[f64; 2]; 6] {
    let p = outer(left, right);
    [p[0][0], p[0][1], p[0][2], p[1][1], p[1][2], p[2][2]]
}
