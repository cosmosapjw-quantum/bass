//! Spin-weighted spherical-harmonic transforms (s = 0, +2, -2) on Gauss-Legendre
//! x uniform-phi rings (`SphereGrid` order: ring-major, phi_k = 2 pi k / n_phi).
//!
//! Convention (Goldberg; identical to `sky_spectrum`):
//! _sY_lm(theta, phi) = (-1)^s sqrt((2l+1)/(4 pi)) d^l_{m,-s}(theta) e^{i m phi},
//! so _sY_{l,-m} = (-1)^{s+m} conj(_{-s}Y_lm). Coefficients are stored for all
//! signed m with the flat index l(l+1)+m. A real scalar field has
//! a_{l,-m} = (-1)^m conj(a_lm); for P_+-2 = Q +- iU, a^-2_{l,-m} = (-1)^m conj(a^+2_lm).
//! With a^+-2 = -(E +- iB) the analysis reproduces `sky_spectrum::analyze_rings`.
//!
//! Analysis is exact for fields band-limited to lmax when n_theta >= lmax + 1
//! and n_phi >= 2 lmax + 1. The directions are those of the field's own sphere;
//! the Lie hierarchy uses photon propagation directions with the (e_theta, e_phi)
//! dyad of the propagation direction.
use crate::kinetic::sky_spectrum::normalized_wigner_d_table;
use crate::kinetic::sphere::SphereGrid;
use nalgebra::Complex;

pub type C64 = Complex<f64>;

/// Flat coefficient index of (l, m), -l <= m <= l.
#[inline]
pub fn index(l: usize, m: i64) -> usize {
    ((l * l + l) as i64 + m) as usize
}

/// Number of coefficients with l <= lmax.
#[inline]
pub fn modes(lmax: usize) -> usize {
    (lmax + 1) * (lmax + 1)
}

#[inline]
fn tri(l: usize, m: usize) -> usize {
    l * (l + 1) / 2 + m
}

fn slot(s: i64) -> usize {
    match s {
        0 => 0,
        2 => 1,
        -2 => 2,
        _ => panic!("spin_sht supports s = 0, +2, -2 only"),
    }
}

pub struct SpinSht {
    pub lmax: usize,
    pub grid: SphereGrid,
    tri_len: usize,
    /// lambda[slot(s)][ring * tri_len + tri(l, m)] = _sLambda_lm(theta_ring) for m >= 0.
    lambda: [Vec<f64>; 3],
    /// exp(i 2 pi j / n_phi) for j < n_phi.
    roots: Vec<C64>,
}

impl SpinSht {
    pub fn new(lmax: usize, n_theta: usize, n_phi: usize) -> Result<Self, String> {
        if n_theta < lmax + 1 || n_phi < 2 * lmax + 1 {
            return Err(format!(
                "spin transform needs n_theta >= lmax+1 and n_phi >= 2 lmax+1 (lmax {lmax}, grid {n_theta}x{n_phi})"
            ));
        }
        let grid = SphereGrid::new(n_theta, n_phi);
        let tri_len = (lmax + 1) * (lmax + 2) / 2;
        let lambda = [0i64, 2, -2].map(|s| {
            let mut table = Vec::with_capacity(n_theta * tri_len);
            for &z in &grid.ct {
                // (-1)^s = +1 for the even spins supported here.
                table.extend(normalized_wigner_d_table(z, -(s as i32), lmax));
            }
            table
        });
        let roots = (0..n_phi)
            .map(|j| {
                let angle = 2.0 * std::f64::consts::PI * j as f64 / n_phi as f64;
                C64::new(angle.cos(), angle.sin())
            })
            .collect();
        Ok(Self {
            lmax,
            grid,
            tri_len,
            lambda,
            roots,
        })
    }

    pub fn len(&self) -> usize {
        self.grid.len()
    }
    pub fn is_empty(&self) -> bool {
        self.grid.is_empty()
    }

    /// _sLambda_lm(theta_ring) for any signed m.
    #[inline]
    fn lam(&self, s: i64, ring: usize, l: usize, m: i64) -> f64 {
        if m >= 0 {
            self.lambda[slot(s)][ring * self.tri_len + tri(l, m as usize)]
        } else {
            let sign = if (m + s).rem_euclid(2) == 0 {
                1.0
            } else {
                -1.0
            };
            sign * self.lambda[slot(-s)][ring * self.tri_len + tri(l, (-m) as usize)]
        }
    }

    #[inline]
    fn root(&self, m: i64, k: usize) -> C64 {
        let n = self.grid.n_phi as i64;
        self.roots[(m * k as i64).rem_euclid(n) as usize]
    }

    /// Field values sum_lm a_lm _sY_lm at every grid point (ring-major).
    pub fn synthesize(&self, s: i64, a: &[C64]) -> Vec<C64> {
        assert_eq!(a.len(), modes(self.lmax), "coefficient length");
        let lmin = s.unsigned_abs() as usize;
        let lmax = self.lmax as i64;
        let n_phi = self.grid.n_phi;
        let mut out = vec![C64::new(0.0, 0.0); self.len()];
        let mut column = vec![C64::new(0.0, 0.0); (2 * self.lmax + 1).max(1)];
        for ring in 0..self.grid.n_theta {
            for m in -lmax..=lmax {
                let mut f = C64::new(0.0, 0.0);
                for l in lmin.max(m.unsigned_abs() as usize)..=self.lmax {
                    f += a[index(l, m)] * self.lam(s, ring, l, m);
                }
                column[(m + lmax) as usize] = f;
            }
            for k in 0..n_phi {
                let mut v = C64::new(0.0, 0.0);
                for m in -lmax..=lmax {
                    v += column[(m + lmax) as usize] * self.root(m, k);
                }
                out[ring * n_phi + k] = v;
            }
        }
        out
    }

    /// Quadrature coefficients a_lm = sum_i w_i f_i conj(_sY_lm(e_i)).
    pub fn analyze(&self, s: i64, f: &[C64]) -> Vec<C64> {
        assert_eq!(f.len(), self.len(), "field length");
        let lmin = s.unsigned_abs() as usize;
        let lmax = self.lmax as i64;
        let n_phi = self.grid.n_phi;
        let mut a = vec![C64::new(0.0, 0.0); modes(self.lmax)];
        for ring in 0..self.grid.n_theta {
            let weight = self.grid.w[ring * n_phi];
            for m in -lmax..=lmax {
                let mut fourier = C64::new(0.0, 0.0);
                for k in 0..n_phi {
                    fourier += f[ring * n_phi + k] * self.root(-m, k);
                }
                fourier *= weight;
                for l in lmin.max(m.unsigned_abs() as usize)..=self.lmax {
                    a[index(l, m)] += fourier * self.lam(s, ring, l, m);
                }
            }
        }
        a
    }

    /// Real I, Q, U on the grid from (a^0, a^+2, a^-2), U in the (e_theta, e_phi) dyad.
    pub fn to_stokes(
        &self,
        a0: &[C64],
        plus: Option<(&[C64], &[C64])>,
    ) -> (Vec<f64>, Vec<f64>, Vec<f64>) {
        let i: Vec<f64> = self.synthesize(0, a0).iter().map(|v| v.re).collect();
        match plus {
            None => {
                let zero = vec![0.0; self.len()];
                (i, zero.clone(), zero)
            }
            Some((ap, am)) => {
                let p = self.synthesize(2, ap);
                let n = self.synthesize(-2, am);
                let q = p.iter().zip(&n).map(|(a, b)| 0.5 * (a.re + b.re)).collect();
                let u = p.iter().zip(&n).map(|(a, b)| 0.5 * (a.im - b.im)).collect();
                (i, q, u)
            }
        }
    }

    /// Coefficients (a^0, a^+2, a^-2) of real I, Q, U on the grid.
    pub fn from_stokes(&self, i: &[f64], q: &[f64], u: &[f64]) -> [Vec<C64>; 3] {
        let scalar: Vec<C64> = i.iter().map(|&x| C64::new(x, 0.0)).collect();
        let plus: Vec<C64> = q.iter().zip(u).map(|(&x, &y)| C64::new(x, y)).collect();
        let minus: Vec<C64> = q.iter().zip(u).map(|(&x, &y)| C64::new(x, -y)).collect();
        [
            self.analyze(0, &scalar),
            self.analyze(2, &plus),
            self.analyze(-2, &minus),
        ]
    }
}

/// sum_lm a_lm _sY_lm(e) at an arbitrary unit direction e (s = 0, +-2), with the
/// convention of the grid transforms. At the poles phi = 0.
pub fn evaluate_at(s: i64, a: &[C64], lmax: usize, e: [f64; 3]) -> C64 {
    assert_eq!(a.len(), modes(lmax), "coefficient length");
    let norm = (e[0] * e[0] + e[1] * e[1] + e[2] * e[2]).sqrt();
    let z = (e[2] / norm).clamp(-1.0, 1.0);
    let phi = if e[0] == 0.0 && e[1] == 0.0 {
        0.0
    } else {
        e[1].atan2(e[0])
    };
    let pos = normalized_wigner_d_table(z, -(s as i32), lmax);
    let neg = normalized_wigner_d_table(z, s as i32, lmax);
    let mut out = C64::new(0.0, 0.0);
    for l in (s.unsigned_abs() as usize)..=lmax {
        for m in -(l as i64)..=(l as i64) {
            let lam = if m >= 0 {
                pos[tri(l, m as usize)]
            } else {
                let sign = if (m + s).rem_euclid(2) == 0 {
                    1.0
                } else {
                    -1.0
                };
                sign * neg[tri(l, (-m) as usize)]
            };
            out += a[index(l, m)] * lam * C64::from_polar(1.0, m as f64 * phi);
        }
    }
    out
}

/// Deterministic pseudo-random real fields (scalar + polarization) with l <= band,
/// satisfying the reality conditions above. Used by tests of the Lie hierarchy.
pub fn random_real_coefficients(lmax: usize, band: usize, seed: u64) -> [Vec<C64>; 3] {
    let mut state = seed;
    let mut next = || {
        state = state
            .wrapping_mul(6364136223846793005)
            .wrapping_add(1442695040888963407);
        ((state >> 11) as f64) / ((1u64 << 53) as f64) - 0.5
    };
    let n = modes(lmax);
    let mut a0 = vec![C64::new(0.0, 0.0); n];
    let mut ap = vec![C64::new(0.0, 0.0); n];
    let mut am = vec![C64::new(0.0, 0.0); n];
    for l in 0..=band.min(lmax) {
        for m in 0..=l as i64 {
            let sign = if m % 2 == 0 { 1.0 } else { -1.0 };
            let v = C64::new(next(), if m == 0 { 0.0 } else { next() });
            a0[index(l, m)] = v;
            a0[index(l, -m)] = v.conj() * sign;
            if l >= 2 {
                let p = C64::new(next(), next());
                let q = C64::new(next(), next());
                ap[index(l, m)] = p;
                am[index(l, -m)] = p.conj() * sign;
                if m > 0 {
                    ap[index(l, -m)] = q;
                    am[index(l, m)] = q.conj() * sign;
                }
            }
        }
    }
    [a0, ap, am]
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::kinetic::sky_spectrum::analyze_rings;
    use std::f64::consts::PI;

    #[test]
    fn round_trip_and_scalar_harmonic_convention() {
        let sht = SpinSht::new(9, 11, 21).unwrap();
        let [a0, ap, am] = random_real_coefficients(9, 9, 7);
        for (s, a) in [(0, &a0), (2, &ap), (-2, &am)] {
            let back = sht.analyze(s, &sht.synthesize(s, a));
            let err = back
                .iter()
                .zip(a.iter())
                .map(|(x, y)| (x - y).norm())
                .fold(0.0, f64::max);
            assert!(err < 2e-13, "spin {s}: {err:e}");
        }
        // Y_11 = -sqrt(3/8pi) sin(theta) e^{i phi}, Y_20 = sqrt(5/16pi)(3 cos^2 - 1).
        let mut unit = vec![C64::new(0.0, 0.0); modes(9)];
        unit[index(1, 1)] = C64::new(1.0, 0.0);
        unit[index(2, 0)] = C64::new(1.0, 0.0);
        let f = sht.synthesize(0, &unit);
        for (i, v) in f.iter().enumerate() {
            let e = &sht.grid.ehat[3 * i..3 * i + 3];
            let expect = C64::new(e[0], e[1]) * (-(3.0 / (8.0 * PI)).sqrt())
                + (5.0 / (16.0 * PI)).sqrt() * (3.0 * e[2] * e[2] - 1.0);
            assert!((v - expect).norm() < 1e-14);
        }
    }

    #[test]
    fn analysis_agrees_with_sky_spectrum_e_and_b() {
        let lmax = 8;
        let sht = SpinSht::new(lmax, 12, 24).unwrap();
        let [a0, ap, am] = random_real_coefficients(lmax, lmax, 11);
        let (i, q, u) = sht.to_stokes(&a0, Some((&ap, &am)));
        let ring_weight: Vec<f64> = (0..sht.grid.n_theta)
            .map(|r| sht.grid.w[r * sht.grid.n_phi])
            .collect();
        let modes =
            analyze_rings(&sht.grid.ct, &ring_weight, sht.grid.n_phi, &i, &q, &u, lmax).unwrap();
        for mode in modes {
            let k = index(mode.ell, mode.m as i64);
            let e = -(ap[k] + am[k]) * 0.5;
            let b = (ap[k] - am[k]) * C64::new(0.0, 0.5);
            for (got, want) in [(mode.alm[0], a0[k]), (mode.alm[1], e), (mode.alm[2], b)] {
                assert!(
                    (C64::new(got[0], got[1]) - want).norm() < 1e-13,
                    "l={} m={}",
                    mode.ell,
                    mode.m
                );
            }
        }
    }
}
