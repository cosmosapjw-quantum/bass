//! Opt-in research discretization: fixed-frame, zero-tilt Thomson gain/loss.
//! No native-window conservation, stiff accuracy, or coupled-order guarantee.
//! All represented occupations are finite logs; no floor or normalization.
use super::radial::{self, RadialGrid, Tail};
use super::sphere::SphereGrid;
use nalgebra::{Matrix3, Vector3};

pub struct FrozenGain<'a> {
    sphere: &'a SphereGrid,
    radial: &'a RadialGrid,
    directions: Vec<Vector3<f64>>,
    delta: Vec<f64>,
    log_weights: Vec<f64>,
    order: usize,
    tail: Tail,
}

fn finite(x: f64, what: &str) -> Result<f64, String> {
    if x.is_finite() {
        Ok(x)
    } else {
        Err(format!("nonfinite {what}"))
    }
}

/// Finite-argument log-sum-exp, allowing -infinity only for zero coefficients.
fn logadd(a: f64, b: f64) -> Result<f64, String> {
    if a == f64::NEG_INFINITY {
        return finite(b, "log sum");
    }
    if b == f64::NEG_INFINITY {
        return finite(a, "log sum");
    }
    finite(a.max(b) + (-(a - b).abs()).exp().ln_1p(), "log sum")
}

impl<'a> FrozenGain<'a> {
    /// Right-handed frame; Frobenius condition estimate <= 1e8.
    /// Orders 2..=16 and representable, strictly uniform logarithmic grids only.
    pub fn new(
        s: &'a SphereGrid,
        r: &'a RadialGrid,
        frame: &[f64],
        order: usize,
        tail: Tail,
        kernel: &str,
        velocity: Option<&[f64]>,
    ) -> Result<Self, String> {
        if kernel != "thomson" {
            return Err("prototype supports Thomson only".into());
        }
        if let Some(v) = velocity {
            if v.len() != 3 || v.iter().any(|x| !x.is_finite() || *x != 0.) {
                return Err("prototype requires exactly zero tilt".into());
            }
        }
        if !(2..=16).contains(&order) || order > r.len() {
            return Err("interpolation order must be 2..=min(16, radial nodes)".into());
        }
        if r.len() < 2 || !r.dlnp.is_finite() || r.dlnp <= 0. {
            return Err("invalid radial grid".into());
        }
        for (j, &x) in r.ln_p.iter().enumerate() {
            if !x.is_finite() || !x.exp().is_finite() || x.exp() <= 0. {
                return Err("radial energies must be finite and positive".into());
            }
            if j > 0 {
                let d = x - r.ln_p[j - 1];
                if d <= 0.
                    || (d - r.dlnp).abs() > 64. * f64::EPSILON * (1. + x.abs() + r.dlnp.abs())
                    || x.exp() <= r.ln_p[j - 1].exp()
                {
                    return Err("radial grid must be uniformly increasing and representable".into());
                }
            }
        }
        if frame.len() != 9 || frame.iter().any(|x| !x.is_finite()) {
            return Err("frame must contain nine finite entries".into());
        }
        let m = Matrix3::from_row_slice(frame);
        let det = m.determinant();
        if !det.is_finite() || det <= 0. {
            return Err("frame must be nonsingular and right-handed".into());
        }
        let inv = m.try_inverse().ok_or("singular frame")?;
        let condition = m.norm() * inv.norm();
        if !condition.is_finite() || condition > 1e8 {
            return Err("frame condition estimate exceeds 1e8".into());
        }
        let n = s.w.len();
        if n == 0 || s.ehat.len() != 3 * n {
            return Err("invalid sphere dimensions".into());
        }
        let mut directions = Vec::with_capacity(n);
        let mut delta = Vec::with_capacity(n);
        let mut log_weights = Vec::with_capacity(n);
        for i in 0..n {
            let q = Vector3::from_row_slice(&s.ehat[3 * i..3 * i + 3]);
            if q.iter().any(|x| !x.is_finite())
                || (q.norm() - 1.).abs() > 1e-12
                || !s.w[i].is_finite()
                || s.w[i] <= 0.
            {
                return Err("invalid sphere directions or weights".into());
            }
            let p = m * q;
            let mu = p.norm();
            if !mu.is_finite() || mu <= 0. {
                return Err("invalid mapped direction".into());
            }
            let lw = finite(s.w[i].ln() + det.ln() - 3. * mu.ln(), "physical log weight")?;
            if !lw.exp().is_finite() || lw.exp() <= 0. {
                return Err("physical weights are not representable".into());
            }
            directions.push(p / mu);
            delta.push(mu.ln());
            log_weights.push(lw);
        }
        // Validate all offsets before zero-exposure identity, without interpolation.
        let max_delta = delta.iter().copied().fold(f64::NEG_INFINITY, f64::max)
            - delta.iter().copied().fold(f64::INFINITY, f64::min);
        let cells = max_delta / r.dlnp;
        if !cells.is_finite() || cells > i64::MAX as f64 / 4. || r.len() > i64::MAX as usize / 4 {
            return Err("unrepresentable pairwise stencil offset".into());
        }
        Ok(Self {
            sphere: s,
            radial: r,
            directions,
            delta,
            log_weights,
            order,
            tail,
        })
    }

    fn validate_state(&self, logs: &[f64]) -> Result<(), String> {
        if self.sphere.len().checked_mul(self.radial.len()) != Some(logs.len())
            || logs.iter().any(|x| !x.is_finite())
        {
            return Err("log occupations must be finite with sphere x radial shape".into());
        }
        Ok(())
    }

    pub fn log_gain(&self, logs: &[f64]) -> Result<Vec<f64>, String> {
        self.validate_state(logs)?;
        let nr = self.radial.len();
        let na = self.sphere.len();
        let mut result = vec![f64::NEG_INFINITY; logs.len()];
        for i in 0..na {
            for b in 0..na {
                let row = &logs[b * nr..(b + 1) * nr];
                let shift = self.delta[b] - self.delta[i]; // old(x-shift): same physical energy
                let shifted = if shift == 0. {
                    row.to_vec()
                } else {
                    let stencil = radial::shift_stencil(self.radial, shift, self.order);
                    if stencil.1.iter().any(|x| !x.is_finite()) {
                        return Err("nonfinite stencil weight".into());
                    }
                    radial::apply_shift_log(self.radial, row, &stencil, self.tail)
                };
                let c = finite(self.directions[i].dot(&self.directions[b]), "kernel cosine")?;
                let lk = finite(
                    (3. / (16. * std::f64::consts::PI)).ln()
                        + (c * c).ln_1p()
                        + self.log_weights[b],
                    "weighted kernel",
                )?;
                for j in 0..nr {
                    let value = finite(shifted[j], "interpolated log occupation")?;
                    result[i * nr + j] =
                        logadd(result[i * nr + j], finite(lk + value, "gain summand")?)?;
                }
            }
        }
        Ok(result)
    }

    pub fn log_step(&self, logs: &[f64], exposure: f64) -> Result<Vec<f64>, String> {
        self.validate_state(logs)?;
        if !exposure.is_finite() || exposure < 0. {
            return Err("exposure must be finite and nonnegative".into());
        }
        if exposure == 0. {
            return Ok(logs.to_vec());
        }
        let gain = self.log_gain(logs)?;
        let half = 0.5 * exposure;
        let mix = |f: &[f64], g: &[f64], h: f64| -> Result<Vec<f64>, String> {
            let lg = (-(-h).exp_m1()).ln();
            f.iter()
                .zip(g)
                .map(|(&a, &b)| {
                    let loss = a - h;
                    // -infinity is valid only when the positive coefficient underflows.
                    if !loss.is_finite() {
                        return Err("nonfinite weighted native loss".into());
                    }
                    logadd(loss, b + lg)
                })
                .collect()
        };
        let midpoint = mix(logs, &gain, half)?;
        let middle_gain = self.log_gain(&midpoint)?; // immutable, fresh endpoint tails
        mix(logs, &middle_gain, exposure)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    const ID: [f64; 9] = [1., 0., 0., 0., 1., 0., 0., 0., 1.];
    #[test]
    fn zero_identity_owns_output() {
        let s = SphereGrid::new(4, 8);
        let r = RadialGrid::new(-3., 2., 16);
        let op = FrozenGain::new(&s, &r, &ID, 8, Tail::Wien, "thomson", None).unwrap();
        let f: Vec<_> = (0..s.len() * r.len())
            .map(|j| if j == 0 { -0. } else { j as f64 / 10. })
            .collect();
        let mut g = op.log_step(&f, 0.).unwrap();
        assert!(f.iter().zip(&g).all(|(a, b)| a.to_bits() == b.to_bits()));
        g[0] = 2.;
        assert_eq!(f[0].to_bits(), (-0.0f64).to_bits());
    }
    #[test]
    fn isotropic_identity_frame_gain() {
        let s = SphereGrid::new(4, 8);
        let r = RadialGrid::new(-3., 2., 16);
        let op = FrozenGain::new(&s, &r, &ID, 8, Tail::PowerLaw, "thomson", None).unwrap();
        let f = vec![-10000.; s.len() * r.len()];
        let g = op.log_gain(&f).unwrap();
        assert!(g.iter().all(|v| (v + 10000.).abs() < 1e-10));
    }
    #[test]
    fn rejects_nonuniform_grid() {
        let s = SphereGrid::new(4, 8);
        let mut r = RadialGrid::new(-3., 2., 16);
        r.ln_p[3] += 0.01;
        assert!(FrozenGain::new(&s, &r, &ID, 8, Tail::Wien, "thomson", None).is_err());
    }
    #[test]
    fn rejects_invalid_sphere_weight() {
        let mut s = SphereGrid::new(4, 8);
        s.w[0] = 0.;
        let r = RadialGrid::new(-3., 2., 16);
        assert!(FrozenGain::new(&s, &r, &ID, 8, Tail::Wien, "thomson", None).is_err());
    }
    #[test]
    fn rejects_nonfinite_interpolated_tail_without_repair() {
        let s = SphereGrid::new(4, 8);
        let r = RadialGrid::new(-3., 2., 16);
        let m = [2., 0., 0., 0., 1., 0., 0., 0., 1.];
        let op = FrozenGain::new(&s, &r, &m, 8, Tail::Wien, "thomson", None).unwrap();
        let mut f = vec![0.; s.len() * r.len()];
        f[14] = -f64::MAX;
        f[15] = f64::MAX;
        assert!(op.log_gain(&f).is_err());
    }
}
