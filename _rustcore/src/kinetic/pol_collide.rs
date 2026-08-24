//! P-C · **편광 정확 충돌 지수** (84차) — rank-9 3항.
//!
//! 유도: docs/P-DERIVATION.md D5.  기저-없는 에르미트 3-텐서 J_ab(ê) 위에서
//!     (K J)_ab(ê') = (3/8pi) Int dOmega Pi_ac(ê') J_cd(ê) Pi_db(ê')
//! 투영자가 ê' 에만 의존하므로 ê 적분이 M = Int J dOmega (9 성분) 로 축약된다
//! ⇒ K 는 **정확히 rank 9**, l-분해 불필요.
//!     Kcal[M] = (7/10)M + (1/10)tr(M)delta (대칭),  (1/2)A (반대칭)
//!     고유값 (1, 7/10, 1/2)
//!     exp(xC)J = e^{-x}J + (3/8pi)Pi(ê)[sum_l ((e^{-x(1-l)}-e^{-x})/l) P_l M]Pi(ê)
//!
//! 저장: J[i*9 + k], k = (S11,S22,S33,S12,S13,S23, A23,A31,A12).

const PI: f64 = std::f64::consts::PI;

/// 고유값 — **하드코딩이 아니라 구적 재계산과 상시 대조**되는 상수 (계약 P0).
pub const EIG: [f64; 3] = [1.0, 0.7, 0.5]; // (trace, stf, anti)

#[inline]
fn unpack(v: &[f64]) -> [[f64; 3]; 3] {
    [
        [v[0], v[3] + v[8], v[4] - v[7]],
        [v[3] - v[8], v[1], v[5] + v[6]],
        [v[4] + v[7], v[5] - v[6], v[2]],
    ]
}

#[inline]
fn pack_into(m: &[[f64; 3]; 3], o: &mut [f64]) {
    o[0] = m[0][0];
    o[1] = m[1][1];
    o[2] = m[2][2];
    o[3] = 0.5 * (m[0][1] + m[1][0]);
    o[4] = 0.5 * (m[0][2] + m[2][0]);
    o[5] = 0.5 * (m[1][2] + m[2][1]);
    o[6] = 0.5 * (m[1][2] - m[2][1]);
    o[7] = 0.5 * (m[2][0] - m[0][2]);
    o[8] = 0.5 * (m[0][1] - m[1][0]);
}

/// exp(x C) J — 정확 3항.  ehat: 3M, j: 9M, w: M.
/// 3항 계수 c_l(x) = (e^{-x(1-l)} - e^{-x})/l = e^{-x} expm1(x l)/l.
/// 85차: x*l <~ 1 에서 파국적 상쇄를 피한다.  Python `_three_term_coeff` 와 동일 분기.
#[inline]
fn three_term_coeff(x: f64, lam: f64) -> f64 {
    if x * lam < 1.0 {
        (-x).exp() * (x * lam).exp_m1() / lam
    } else {
        ((-x * (1.0 - lam)).exp() - (-x).exp()) / lam
    }
}

/// exp(x C) J — 정확 3항.  **계약**: x >= 0 (음수는 조용히 항등으로 떨어뜨리지 않는다).
pub fn collide(ehat: &[f64], w: &[f64], j: &[f64], x: f64) -> Vec<f64> {
    let n = w.len();
    debug_assert!(x >= 0.0, "nu*dt < 0 금지 (조용한 폴백 금지)");
    if !(x > 0.0) {
        return j.to_vec();
    }
    // 1. M = sum w J   (9 성분 축약)
    let mut mv = [0.0f64; 9];
    for i in 0..n {
        for k in 0..9 {
            mv[k] += w[i] * j[i * 9 + k];
        }
    }
    let m = unpack(&mv);
    // 2. 고유공간 분해 (trace / stf / anti)
    let tr = (m[0][0] + m[1][1] + m[2][2]) / 3.0;
    let mut parts = [[[0.0f64; 3]; 3]; 3];
    for a in 0..3 {
        for b in 0..3 {
            let s = 0.5 * (m[a][b] + m[b][a]);
            let anti = 0.5 * (m[a][b] - m[b][a]);
            parts[0][a][b] = if a == b { tr } else { 0.0 };
            parts[1][a][b] = s - parts[0][a][b];
            parts[2][a][b] = anti;
        }
    }
    // 3. 3항 계수
    let em = (-x).exp();
    let mut acc = [[0.0f64; 3]; 3];
    for (p, lam) in EIG.iter().enumerate() {
        let c = three_term_coeff(x, *lam);
        for a in 0..3 {
            for b in 0..3 {
                acc[a][b] += c * parts[p][a][b];
            }
        }
    }
    // 4. 적용:  e^{-x}J + (3/8pi) Pi acc Pi
    let mut out = vec![0.0; n * 9];
    let c38 = 3.0 / (8.0 * PI);
    for i in 0..n {
        let e = [ehat[3 * i], ehat[3 * i + 1], ehat[3 * i + 2]];
        // Pi acc Pi  = acc - e(e·acc) - (acc·e)e + e (e·acc·e) e
        let mut ae = [0.0f64; 3];
        let mut ea = [0.0f64; 3];
        for a in 0..3 {
            for b in 0..3 {
                ae[a] += acc[a][b] * e[b];
                ea[a] += e[b] * acc[b][a];
            }
        }
        let eae = ae[0] * e[0] + ae[1] * e[1] + ae[2] * e[2];
        let mut pap = [[0.0f64; 3]; 3];
        for a in 0..3 {
            for b in 0..3 {
                pap[a][b] = acc[a][b] - e[a] * ea[b] - ae[a] * e[b] + e[a] * e[b] * eae;
            }
        }
        let mut tmp = [0.0f64; 9];
        pack_into(&pap, &mut tmp);
        for k in 0..9 {
            out[i * 9 + k] = em * j[i * 9 + k] + c38 * tmp[k];
        }
    }
    out
}

/// ★ Kcal 고유값을 구적으로 재계산 (하드코딩 금지 게이트의 Rust 판).
pub fn kcal_eigenvalues(ehat: &[f64], w: &[f64]) -> [f64; 3] {
    let n = w.len();
    let probes: [[[f64; 3]; 3]; 3] = [
        [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
        [[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, 0.0]],
        [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
    ];
    let mut out = [0.0; 3];
    for (p, m) in probes.iter().enumerate() {
        let mut acc = [[0.0f64; 3]; 3];
        for i in 0..n {
            let e = [ehat[3 * i], ehat[3 * i + 1], ehat[3 * i + 2]];
            let mut ae = [0.0f64; 3];
            let mut ea = [0.0f64; 3];
            for a in 0..3 {
                for b in 0..3 {
                    ae[a] += m[a][b] * e[b];
                    ea[a] += e[b] * m[b][a];
                }
            }
            let eae = ae[0] * e[0] + ae[1] * e[1] + ae[2] * e[2];
            for a in 0..3 {
                for b in 0..3 {
                    acc[a][b] += w[i] * (m[a][b] - e[a] * ea[b] - ae[a] * e[b] + e[a] * e[b] * eae);
                }
            }
        }
        let (ia, ib) = if p == 0 {
            (0, 0)
        } else {
            (0, if p == 1 { 0 } else { 1 })
        };
        out[p] = (3.0 / (8.0 * PI)) * acc[ia][ib] / m[ia][ib];
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::kinetic::sphere::SphereGrid;

    #[test]
    fn eigenvalues_recomputed() {
        let g = SphereGrid::new(24, 48);
        let k = kcal_eigenvalues(&g.ehat, &g.w);
        for p in 0..3 {
            assert!((k[p] - EIG[p]).abs() < 1e-12, "{k:?}");
        }
    }

    #[test]
    fn number_conserved_and_stiff_limit_finite() {
        let g = SphereGrid::new(16, 32);
        let n = g.len();
        let mut j = vec![0.0; n * 9];
        for i in 0..n {
            let e = [g.ehat[3 * i], g.ehat[3 * i + 1], g.ehat[3 * i + 2]];
            let ii = 1.0 + 0.5 * e[2] * e[2];
            // 무편광 J = (I/2)(delta - ee)
            let m = [
                [
                    0.5 * ii * (1.0 - e[0] * e[0]),
                    -0.5 * ii * e[0] * e[1],
                    -0.5 * ii * e[0] * e[2],
                ],
                [
                    -0.5 * ii * e[1] * e[0],
                    0.5 * ii * (1.0 - e[1] * e[1]),
                    -0.5 * ii * e[1] * e[2],
                ],
                [
                    -0.5 * ii * e[2] * e[0],
                    -0.5 * ii * e[2] * e[1],
                    0.5 * ii * (1.0 - e[2] * e[2]),
                ],
            ];
            pack_into(&m, &mut j[i * 9..i * 9 + 9]);
        }
        let num = |v: &[f64]| -> f64 {
            (0..n)
                .map(|i| g.w[i] * (v[i * 9] + v[i * 9 + 1] + v[i * 9 + 2]))
                .sum()
        };
        let n0 = num(&j);
        for x in [0.1f64, 3.0, 1e3, 1e6] {
            let o = collide(&g.ehat, &g.w, &j, x);
            assert!(o.iter().all(|v| v.is_finite()), "x={x}");
            assert!(((num(&o) - n0) / n0).abs() < 1e-13, "x={x}");
        }
    }
}

/// P9c · **Mode B 편광 충돌** — 운동량 격자 위의 rank-9 3항.
///
/// 저장: j[(i*n_p + jj)*9 + k]  (방향-주, 각 (방향, 운동량) 노드마다 9 성분).
/// Thomson 핵은 **에너지 교환이 없으므로** 반경 슬라이스마다 같은 연산자다
/// (스칼라판 `collide_exact_modeb` 와 같은 구조).  슬라이스별로 M 을 축약하고
/// 3항을 적용한다 — 비용 O(n_ang * n_p), 추가 메모리 O(n_ang * 9).
pub fn collide_modeb(ehat: &[f64], w: &[f64], j: &[f64], n_p: usize, x: f64) -> Vec<f64> {
    let n = w.len();
    debug_assert!(x >= 0.0, "nu*dt < 0 금지");
    if !(x > 0.0) {
        return j.to_vec();
    }
    let mut out = vec![0.0; n * n_p * 9];
    let mut slice = vec![0.0; n * 9];
    for jj in 0..n_p {
        for i in 0..n {
            let src = (i * n_p + jj) * 9;
            slice[i * 9..i * 9 + 9].copy_from_slice(&j[src..src + 9]);
        }
        let o = collide(ehat, w, &slice, x);
        for i in 0..n {
            let dst = (i * n_p + jj) * 9;
            out[dst..dst + 9].copy_from_slice(&o[i * 9..i * 9 + 9]);
        }
    }
    out
}

#[cfg(test)]
mod modeb_tests {
    use super::*;

    fn grid(nt: usize, np_: usize) -> (Vec<f64>, Vec<f64>) {
        let g = crate::kinetic::sphere::SphereGrid::new(nt, np_);
        (g.ehat.clone(), g.w.clone())
    }

    #[test]
    fn modeb_slices_match_mode_a() {
        // 각 반경 슬라이스가 Mode A 의 결과와 **정확히** 같아야 한다 (핵이 에너지 무관).
        let (e, w) = grid(8, 16);
        let n = w.len();
        let n_p = 5usize;
        let mut j = vec![0.0; n * n_p * 9];
        for i in 0..n {
            for jj in 0..n_p {
                for k in 0..9 {
                    j[(i * n_p + jj) * 9 + k] =
                        0.3 * ((i * 7 + jj * 3 + k) as f64).sin() + if k < 3 { 1.0 } else { 0.0 };
                }
            }
        }
        let x = 1.7;
        let got = collide_modeb(&e, &w, &j, n_p, x);
        for jj in 0..n_p {
            let mut sl = vec![0.0; n * 9];
            for i in 0..n {
                for k in 0..9 {
                    sl[i * 9 + k] = j[(i * n_p + jj) * 9 + k];
                }
            }
            let want = collide(&e, &w, &sl, x);
            for i in 0..n {
                for k in 0..9 {
                    let d = (got[(i * n_p + jj) * 9 + k] - want[i * 9 + k]).abs();
                    assert!(d < 1e-15, "jj={jj} i={i} k={k} d={d}");
                }
            }
        }
    }

    #[test]
    fn modeb_x_zero_is_identity() {
        let (e, w) = grid(6, 12);
        let n_p = 3usize;
        let j: Vec<f64> = (0..w.len() * n_p * 9).map(|t| (t as f64).cos()).collect();
        assert_eq!(collide_modeb(&e, &w, &j, n_p, 0.0), j);
    }
}
