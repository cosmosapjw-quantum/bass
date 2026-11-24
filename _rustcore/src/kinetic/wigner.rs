//! Wigner 3j symbols and the spin-weighted Gaunt kernels of the Lie hierarchy.
//!
//! The 3j symbol uses the Racah single-sum formula with log-factorials. The
//! kernels are Dossier II ii:gaunt_prefactor, ii:gaunt_gradient and
//! ii:gaunt_rotation for the multiplication G^h, the gradient K_grad^h and the
//! rotated gradient K_J^h of a degree-L scalar potential acting on a spin-h
//! field (Goldberg/HEALPix spin harmonics, the convention of `sky_spectrum`).
//! With one small L <= 2 the Racah sum has at most 2L+1 terms, so the
//! log-space evaluation is accurate to a few ulps for l up to several hundred.

/// ln(k!) for 0 <= k < len.
#[derive(Clone, Debug)]
pub struct LogFactorial(Vec<f64>);

impl LogFactorial {
    pub fn new(len: usize) -> Self {
        let mut v = vec![0.0; len.max(2)];
        for i in 1..v.len() {
            v[i] = v[i - 1] + (i as f64).ln();
        }
        Self(v)
    }
    #[inline]
    fn get(&self, k: i64) -> f64 {
        self.0[k as usize]
    }
    pub fn len(&self) -> usize {
        self.0.len()
    }
    pub fn is_empty(&self) -> bool {
        self.0.is_empty()
    }
}

/// (j1 j2 j3; m1 m2 m3) for integer arguments; zero outside the selection rules.
/// The table must hold arguments up to j1 + j2 + j3 + 1.
pub fn wigner3j(lf: &LogFactorial, j: [i64; 3], m: [i64; 3]) -> f64 {
    let [j1, j2, j3] = j;
    let [m1, m2, m3] = m;
    if m1 + m2 + m3 != 0
        || j1 < 0
        || j2 < 0
        || j3 < 0
        || j3 < (j1 - j2).abs()
        || j3 > j1 + j2
        || m1.abs() > j1
        || m2.abs() > j2
        || m3.abs() > j3
    {
        return 0.0;
    }
    assert!(
        ((j1 + j2 + j3 + 1) as usize) < lf.len(),
        "log-factorial table too short for 3j arguments"
    );
    let tri = 0.5
        * (lf.get(j1 + j2 - j3) + lf.get(j1 - j2 + j3) + lf.get(-j1 + j2 + j3)
            - lf.get(j1 + j2 + j3 + 1));
    let norm = 0.5
        * (lf.get(j1 + m1)
            + lf.get(j1 - m1)
            + lf.get(j2 + m2)
            + lf.get(j2 - m2)
            + lf.get(j3 + m3)
            + lf.get(j3 - m3));
    let kmin = 0.max(j2 - j3 - m1).max(j1 - j3 + m2);
    let kmax = (j1 + j2 - j3).min(j1 - m1).min(j2 + m2);
    let mut sum = 0.0;
    for k in kmin..=kmax {
        let den = lf.get(k)
            + lf.get(j3 - j2 + k + m1)
            + lf.get(j3 - j1 + k - m2)
            + lf.get(j1 + j2 - j3 - k)
            + lf.get(j1 - k - m1)
            + lf.get(j2 - k + m2);
        let term = (tri + norm - den).exp();
        sum += if k % 2 == 0 { term } else { -term };
    }
    if (j1 - j2 - m3).rem_euclid(2) == 0 {
        sum
    } else {
        -sum
    }
}

/// Kernel values of one (l m; L M; l' m') triple for spin h, with m' = m - M.
/// `kj` is the real factor of K_J = -i kj.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct GauntTriple {
    pub g: f64,
    pub kgrad: f64,
    pub kj: f64,
}

/// G^h, K_grad^h and K_J^h = -i kj of Dossier II for the triple
/// <_hY_lm | Y_LM (op) _hY_l'm'> with m' = m - M.
pub fn gaunt(
    lf: &LogFactorial,
    h: i64,
    l: i64,
    m: i64,
    big_l: i64,
    big_m: i64,
    lp: i64,
) -> GauntTriple {
    let mp = m - big_m;
    let zero = GauntTriple {
        g: 0.0,
        kgrad: 0.0,
        kj: 0.0,
    };
    if l < h.abs() || lp < h.abs() || mp.abs() > lp || m.abs() > l {
        return zero;
    }
    let phase = if (h + m).rem_euclid(2) == 0 {
        1.0
    } else {
        -1.0
    };
    let prefactor = phase
        * (((2 * l + 1) * (2 * big_l + 1) * (2 * lp + 1)) as f64 / (4.0 * std::f64::consts::PI))
            .sqrt()
        * wigner3j(lf, [l, big_l, lp], [-m, big_m, mp]);
    if prefactor == 0.0 {
        return zero;
    }
    let g = prefactor * wigner3j(lf, [l, big_l, lp], [h, 0, -h]);
    let kgrad = 0.5 * ((big_l * (big_l + 1) + lp * (lp + 1) - l * (l + 1)) as f64) * g;
    let up = (((lp + h) * (lp - h + 1)) as f64).max(0.0).sqrt();
    let down = (((lp - h) * (lp + h + 1)) as f64).max(0.0).sqrt();
    let bracket = up * wigner3j(lf, [l, big_l, lp], [h, -1, 1 - h])
        - down * wigner3j(lf, [l, big_l, lp], [h, 1, -1 - h]);
    let kj = 0.5 * ((big_l * (big_l + 1)) as f64).sqrt() * prefactor * bracket;
    GauntTriple { g, kgrad, kj }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn closed_form_3j_values_and_orthogonality() {
        let lf = LogFactorial::new(64);
        let close = |a: f64, b: f64| (a - b).abs() < 1e-15;
        assert!(close(
            wigner3j(&lf, [1, 1, 0], [0, 0, 0]),
            -1.0 / 3f64.sqrt()
        ));
        assert!(close(
            wigner3j(&lf, [2, 2, 0], [0, 0, 0]),
            1.0 / 5f64.sqrt()
        ));
        assert!(close(
            wigner3j(&lf, [1, 1, 2], [0, 0, 0]),
            (2.0 / 15.0f64).sqrt()
        ));
        assert!(close(
            wigner3j(&lf, [1, 1, 1], [1, -1, 0]),
            1.0 / 6f64.sqrt()
        ));
        assert_eq!(wigner3j(&lf, [1, 1, 1], [0, 0, 0]), 0.0);
        // sum_{m1,m2} (2 j3 + 1) (j1 j2 j3; m1 m2 m3)^2 = 1 for every admissible j3, m3.
        for (j1, j2) in [(7i64, 2i64), (12, 1), (20, 2), (5, 5)] {
            for j3 in (j1 - j2).abs()..=(j1 + j2) {
                for m3 in -j3..=j3 {
                    let mut s = 0.0;
                    for m1 in -j1..=j1 {
                        let m2 = -m1 - m3;
                        if m2.abs() <= j2 {
                            s += wigner3j(&lf, [j1, j2, j3], [m1, m2, m3]).powi(2);
                        }
                    }
                    assert!(
                        (s * (2 * j3 + 1) as f64 - 1.0).abs() < 2e-13,
                        "{j1} {j2} {j3} {m3} {s}"
                    );
                }
            }
        }
    }

    #[test]
    fn monopole_kernel_is_identity_over_sqrt_4pi_and_parity_holds() {
        let lf = LogFactorial::new(128);
        for h in [0i64, 2, -2] {
            for l in 2..12i64 {
                for m in -l..=l {
                    let k = gaunt(&lf, h, l, m, 0, 0, l);
                    assert!((k.g * (4.0 * std::f64::consts::PI).sqrt() - 1.0).abs() < 1e-13);
                    assert_eq!(k.kgrad, 0.0);
                    assert_eq!(k.kj, 0.0);
                }
            }
        }
        // ii:kernel_parity: G^{-h} = eta G^h, K_grad^{-h} = eta K_grad^h, K_J^{-h} = -eta K_J^h.
        for l in 2..9i64 {
            for big_l in 0..=2i64 {
                for lp in (l - big_l).max(2)..=(l + big_l) {
                    for m in -l..=l {
                        for big_m in -big_l..=big_l {
                            let eta = if (l + big_l + lp) % 2 == 0 { 1.0 } else { -1.0 };
                            let p = gaunt(&lf, 2, l, m, big_l, big_m, lp);
                            let q = gaunt(&lf, -2, l, m, big_l, big_m, lp);
                            assert!((q.g - eta * p.g).abs() < 1e-14);
                            assert!((q.kgrad - eta * p.kgrad).abs() < 1e-13);
                            assert!((q.kj + eta * p.kj).abs() < 1e-13);
                        }
                    }
                }
            }
        }
    }
}
