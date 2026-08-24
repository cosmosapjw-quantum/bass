//! R5a · **일반 rank tilted 텐서 커널** — `bianchi.matter.tilted_terms` 의 포트.
//!
//! 프로파일 (tilted 적분 4.55 s, l_max=3, i_max=3, 20 스텝):
//! ```text
//! tensordot          52480 회  1.49 s (누적)   ← to_coord / covariant_derivative
//! equation_lhs                 2.46 s (누적)
//! covariant_derivative          0.58 s
//! ```
//! 작은 배열에 대한 numpy 호출이 수만 번이라 **호출 오버헤드가 지배**한다.  여기서는
//! 그 층(⊥Ẋ, D_B X, D^aJ_{aA_l}, D_{⟨a_l}J_{A_{l−1}⟩})을 통째로 Rust 로 옮긴다.
//!
//! ★ 지표 규약 (Python 에서 **실측**해 맞춘 것):
//! ```text
//! eup, edn, deup : (3, 4)   [A][μ]
//! Γ              : (4,4,4)  Γ[μ][λ][ρ]
//! to_coord   : 축 0(A) 를 소비하고 μ 를 **뒤에** 붙인다 (r 번 반복 → 순서 보존)
//! to_tetrad  : 축 0(μ) 를 edn 의 **두 번째** 지표와 축약하고 A 를 뒤에 붙인다
//! spatial_derivative 반환 축은 (B, A₁…A_r)  ← 문서 그대로, 실측 확인
//! div_contracted 는 그 (B, A₁) 을 축약한다
//! ```
//! ★ PSTF 는 여기서 하지 않는다 — Python 의 고정 연산자(R3)가 이미 행렬곱 한 번이라
//!   되돌려 주고 거기서 적용하는 편이 포트 표면을 줄인다.

/// tilted 기하 묶음 (Python `tilted._geometry` 의 필요한 부분만).
#[derive(Clone, Debug)]
pub struct Geo {
    pub eup: [f64; 12],  // [A*4 + μ]
    pub edn: [f64; 12],  // [A*4 + μ]
    pub deup: [f64; 12], // [A*4 + μ]
    pub hmix: [f64; 16], // [μ*4 + ν]
    pub uup: [f64; 4],
    pub gam: [f64; 64], // Γ[μ*16 + λ*4 + ρ]
}

/// 축 0 을 소비하고 새 지표를 **뒤에** 붙이는 축약 (numpy `tensordot(x, m, ([0],[k]))`).
///
/// `transposed=false` → `m[a*n + c]`,  `true` → `m[c*m_rows + a]`.
fn tdot0(x: &[f64], m_rows: usize, mat: &[f64], n: usize, transposed: bool) -> Vec<f64> {
    let rr = x.len() / m_rows;
    let mut out = vec![0.0f64; rr * n];
    for a in 0..m_rows {
        for j in 0..rr {
            let v = x[a * rr + j];
            if v == 0.0 {
                continue;
            }
            for c in 0..n {
                let w = if transposed {
                    mat[c * m_rows + a]
                } else {
                    mat[a * n + c]
                };
                out[j * n + c] += v * w;
            }
        }
    }
    out
}

/// X_{A₁…A_r} (사틀, 3^r) → X^{μ₁…μ_r} (좌표, 4^r).
pub fn to_coord(x: &[f64], r: usize, eup: &[f64; 12]) -> Vec<f64> {
    let mut out = x.to_vec();
    for _ in 0..r {
        out = tdot0(&out, 3, eup, 4, false);
    }
    out
}

/// X^{μ₁…μ_r} → X_{A₁…A_r}  (앞쪽 `n_ax` 개 축만).
pub fn to_tetrad(x: &[f64], n_ax: usize, edn: &[f64; 12]) -> Vec<f64> {
    let mut out = x.to_vec();
    for _ in 0..n_ax {
        out = tdot0(&out, 4, edn, 3, true);
    }
    out
}

/// ∂_t X^{μ…} = Σ(dX_A/dt)E…E + Σ X_A ∂_t(E…E)  — 둘째 항이 **사틀 회전항**.
pub fn coord_time_derivative(
    x: &[f64],
    dx: &[f64],
    r: usize,
    eup: &[f64; 12],
    deup: &[f64; 12],
) -> Vec<f64> {
    let mut out = to_coord(dx, r, eup);
    for k in 0..r {
        let mut cur = x.to_vec();
        for j in 0..r {
            let basis = if j == k { deup } else { eup };
            cur = tdot0(&cur, 3, basis, 4, false);
        }
        for (o, c) in out.iter_mut().zip(cur.iter()) {
            *o += *c;
        }
    }
    out
}

/// ∇_λ X^{μ₁…μ_r} — 반환 축 (λ, μ₁…μ_r), 4^{r+1}.  공간균질이라 ∂_i 항이 없다.
pub fn covariant_derivative(xc: &[f64], dxc: &[f64], r: usize, gam: &[f64; 64]) -> Vec<f64> {
    let n = 4usize.pow(r as u32);
    let mut out = vec![0.0f64; 4 * n];
    out[..n].copy_from_slice(dxc); // λ = 0 성분에 ∂_t
    let mut idx = vec![0usize; r];
    for flat in 0..n {
        // flat → 다중지표
        let mut t = flat;
        for idx_k in idx.iter_mut().rev() {
            *idx_k = t % 4;
            t /= 4;
        }
        for lam in 0..4 {
            let mut acc = 0.0f64;
            for (k, &mu_k) in idx.iter().enumerate().take(r) {
                let stride = 4usize.pow((r - 1 - k) as u32);
                let base = flat - mu_k * stride;
                for rho in 0..4 {
                    let g = gam[mu_k * 16 + lam * 4 + rho];
                    if g != 0.0 {
                        acc += g * xc[base + rho * stride];
                    }
                }
            }
            out[lam * n + flat] += acc;
        }
    }
    out
}

fn nabla(x: &[f64], dx: &[f64], r: usize, geo: &Geo) -> Vec<f64> {
    let xc = to_coord(x, r, &geo.eup);
    let dxc = coord_time_derivative(x, dx, r, &geo.eup, &geo.deup);
    covariant_derivative(&xc, &dxc, r, &geo.gam)
}

/// ⊥Ẋ_{A₁…A_r} — 사영 시간미분의 사틀 성분 (회전항 포함).
pub fn perp_dot(x: &[f64], dx: &[f64], r: usize, geo: &Geo) -> Vec<f64> {
    let nab = nabla(x, dx, r, geo);
    let n = 4usize.pow(r as u32);
    let mut ux = vec![0.0f64; n];
    for lam in 0..4 {
        let u = geo.uup[lam];
        if u == 0.0 {
            continue;
        }
        for j in 0..n {
            ux[j] += u * nab[lam * n + j];
        }
    }
    // h^{μ_k}_{ν} 사영 — 축 k 마다 (numpy: moveaxis(tensordot(hmix, uX, ([1],[k])), 0, k))
    for _ in 0..r {
        ux = tdot0(&ux, 4, &geo.hmix, 4, true); // 축 0 소비, 새 지표를 뒤에 → r 번이면 순서 보존
    }
    to_tetrad(&ux, r, &geo.edn)
}

/// D_B X_{A₁…A_r} — 반환 축 (B, A₁…A_r), 3^{r+1}.
pub fn spatial_derivative(x: &[f64], dx: &[f64], r: usize, geo: &Geo) -> Vec<f64> {
    let nab = nabla(x, dx, r, geo);
    let n = 4usize.pow(r as u32);
    // T[μ…, B] = Σ_λ eup[B][λ] nab[λ, μ…]
    let mut t = vec![0.0f64; n * 3];
    for b in 0..3 {
        for lam in 0..4 {
            let e = geo.eup[b * 4 + lam];
            if e == 0.0 {
                continue;
            }
            for j in 0..n {
                t[j * 3 + b] += e * nab[lam * n + j];
            }
        }
    }
    to_tetrad(&t, r, &geo.edn) // r 번 돌면 (B, A₁…A_r)
}

/// D^a J_{a A_l} — rank r 입력 → rank r−1 (첫 두 축 축약).
pub fn div_contracted(x: &[f64], dx: &[f64], r: usize, geo: &Geo) -> Vec<f64> {
    let s = spatial_derivative(x, dx, r, geo); // (B, A₁…A_r)
    let rest = 3usize.pow((r - 1) as u32);
    let mut out = vec![0.0f64; rest];
    for b in 0..3 {
        let base = b * 3usize.pow(r as u32) + b * rest;
        for j in 0..rest {
            out[j] += s[base + j];
        }
    }
    out
}

/// D_{⟨a_l} J_{A_{l−1}⟩} 의 **PSTF 적용 전** 텐서 — 반환 축 (A₁…A_r, B).
pub fn div_free_raw(x: &[f64], dx: &[f64], r: usize, geo: &Geo) -> Vec<f64> {
    let s = spatial_derivative(x, dx, r, geo); // (B, A₁…A_r)
    let rest = 3usize.pow(r as u32);
    let mut out = vec![0.0f64; rest * 3];
    for b in 0..3 {
        for j in 0..rest {
            out[j * 3 + b] = s[b * rest + j];
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    fn toy_geo() -> Geo {
        let mut g = Geo {
            eup: [0.0; 12],
            edn: [0.0; 12],
            deup: [0.0; 12],
            hmix: [0.0; 16],
            uup: [1.0, 0.0, 0.0, 0.0],
            gam: [0.0; 64],
        };
        for a in 0..3 {
            g.eup[a * 4 + a + 1] = 1.0;
            g.edn[a * 4 + a + 1] = 1.0;
        }
        for m in 1..4 {
            g.hmix[m * 4 + m] = 1.0;
        }
        g
    }

    #[test]
    fn to_coord_then_to_tetrad_is_identity_for_an_orthonormal_frame() {
        let g = toy_geo();
        let x: Vec<f64> = (0..9).map(|i| i as f64 * 0.3 - 1.0).collect();
        let back = to_tetrad(&to_coord(&x, 2, &g.eup), 2, &g.edn);
        for (a, b) in x.iter().zip(back.iter()) {
            assert!((a - b).abs() < 1e-13, "{a} {b}");
        }
    }

    #[test]
    fn flat_geometry_gives_plain_time_derivative() {
        let g = toy_geo();
        let x: Vec<f64> = (0..3).map(|i| i as f64 + 1.0).collect();
        let dx = vec![0.5, -0.25, 2.0];
        let p = perp_dot(&x, &dx, 1, &g);
        for (a, b) in p.iter().zip(dx.iter()) {
            assert!((a - b).abs() < 1e-13, "{a} {b}");
        }
    }

    #[test]
    fn spatial_derivative_vanishes_in_a_static_orthonormal_frame() {
        let g = toy_geo();
        let x: Vec<f64> = (0..3).map(|i| i as f64 + 1.0).collect();
        let s = spatial_derivative(&x, &[0.0; 3], 1, &g);
        assert!(s.iter().all(|v| v.abs() < 1e-13), "{s:?}");
    }
}
