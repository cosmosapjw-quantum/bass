//! J3 · 계수공간 계층 커널 — tilted 좌변 격자 + 질량블록 + untilted RHS 격자.
//!
//! 좌표-동일 (R5b): 블록표는 `coeff_tables.rs` (Python 산출 캐리) — 재유도 0.
//! 수식은 `bianchi.matter.tilted_coeff.equation_lhs_coeff` /
//! `hierarchy_coeff.hierarchy_rhs_coeff` 의 **항별 동일** 미러.
//!
//! 격자 팩킹: l-major, (l,i) 블록 연속 —
//!   off(l,i) = Σ_{l'<l}(2l'+1)·(i_pad+1) + i·(2l+1),  l ≤ l_pad, i ≤ i_pad.
//! 좌변 격자는 이웃 (l+2, i+2) 를 요구하므로 호출자가 l_pad=l_max+2,
//! i_pad=i_max+2 로 패딩한다 (dense 계약 "이웃 필수, 절단은 호출자" 동일).
//!
//! 비트-정확은 **주장하지 않는다** — R5b 46차 교훈: 축약 합 순서가 경계.
//! 게이트는 Python 두-경로 대조 (tests/test_j3_coeff_kernel.py).

use super::coeff_tables as t;

// ─────────────────────────────── 표 접근
/// (data, n_out, n_in, k) — op 블록의 l 절편.
pub(crate) fn block(op: &str, l: usize) -> (&'static [f64], usize, usize, usize) {
    let (min_l, max_l, off, data, l_in, k): (usize, usize, &[usize], &[f64], usize, usize) =
        match op {
            "outer" => (t::OUTER_MIN_L, t::OUTER_MAX_L, &t::OUTER_OFF, &t::OUTER_DATA, l - 2, 5),
            "c1" => (t::C1_MIN_L, t::C1_MAX_L, &t::C1_OFF, &t::C1_DATA, l, 5),
            "c2" => (t::C2_MIN_L, t::C2_MAX_L, &t::C2_OFF, &t::C2_DATA, l + 2, 5),
            "ov" => (t::OV_MIN_L, t::OV_MAX_L, &t::OV_OFF, &t::OV_DATA, l - 1, 3),
            "cv" => (t::CV_MIN_L, t::CV_MAX_L, &t::CV_OFF, &t::CV_DATA, l + 1, 3),
            "rot" => (t::ROT_MIN_L, t::ROT_MAX_L, &t::ROT_OFF, &t::ROT_DATA, l, 3),
            _ => panic!("unknown block op {op}"),
        };
    assert!(
        (min_l..=max_l).contains(&l),
        "block {op}: l={l} outside table range {min_l}..={max_l}"
    );
    let idx = l - min_l;
    (&data[off[idx]..off[idx + 1]], 2 * l + 1, 2 * l_in + 1, k)
}

/// out[p] = Σ_{m,kk} G[p,m,kk]·c[m]·s[kk]  (pstf_coeff.apply_block 미러).
pub(crate) fn apply(op: &str, l: usize, c: &[f64], s: &[f64]) -> Vec<f64> {
    let (g, n_out, n_in, k) = block(op, l);
    assert_eq!(c.len(), n_in, "apply {op} l={l}: input length");
    assert_eq!(s.len(), k, "apply {op} l={l}: slot length");
    let mut out = vec![0.0; n_out];
    for p in 0..n_out {
        let mut acc = 0.0;
        for m in 0..n_in {
            let base = p * n_in * k + m * k;
            let mut inner = 0.0;
            for (kk, sv) in s.iter().enumerate() {
                inner += g[base + kk] * sv;
            }
            acc += inner * c[m];
        }
        out[p] = acc;
    }
    out
}

// ─────────────────────────────── J2c 닫힌 기하 3항 (적합계수는 Python 이 나름)
/// perp_dot X-부: c_pd[0]·I + Σ_k c_pd[1+k]·c1_k + l·Σ_a c_pd[6+a]·B_a.
fn perp_p_apply(l: usize, c_pd: &[f64], x: &[f64]) -> Vec<f64> {
    let mut y: Vec<f64> = x.iter().map(|v| c_pd[0] * v).collect();
    if l >= 1 {
        for (yi, ci) in y.iter_mut().zip(apply("c1", l, x, &c_pd[1..6])) {
            *yi += ci;
        }
        let lr = l as f64;
        for (yi, ri) in y.iter_mut().zip(apply("rot", l, x, &c_pd[6..9])) {
            *yi += lr * ri;
        }
    }
    y
}

/// div 계열 X-부 합성: Σ_a c[a]·op_a + l·Σ_{x,a} c[3+3x+a]·B_x∘op_a.
fn div_p_apply(op: &str, l: usize, c12: &[f64], x: &[f64]) -> Vec<f64> {
    let n_out = 2 * l + 1;
    // t_a = op[:,:,a] @ x  (a = 정준 l=1 슬롯)
    let mut ta = Vec::with_capacity(3);
    for a in 0..3 {
        let mut e = [0.0; 3];
        e[a] = 1.0;
        ta.push(apply(op, l, x, &e));
    }
    let mut y = vec![0.0; n_out];
    for a in 0..3 {
        for p in 0..n_out {
            y[p] += c12[a] * ta[a][p];
        }
    }
    if l >= 1 {
        let lr = l as f64;
        for xa in 0..3 {
            // s_x = Σ_a c[3+3x+a]·t_a,  y += l·B_x @ s_x
            let mut sx = vec![0.0; n_out];
            for a in 0..3 {
                let cc = c12[3 + 3 * xa + a];
                for p in 0..n_out {
                    sx[p] += cc * ta[a][p];
                }
            }
            let mut e = [0.0; 3];
            e[xa] = 1.0;
            for (yi, ri) in y.iter_mut().zip(apply("rot", l, &sx, &e)) {
                *yi += lr * ri;
            }
        }
    }
    y
}

// ─────────────────────────────── 격자 오프셋
pub fn grid_len(l_pad: usize, i_pad: usize) -> usize {
    (0..=l_pad).map(|l| (2 * l + 1) * (i_pad + 1)).sum()
}

fn off(l: usize, i: usize, i_pad: usize) -> usize {
    let mut o = 0;
    for lp in 0..l {
        o += (2 * lp + 1) * (i_pad + 1);
    }
    o + i * (2 * l + 1)
}

fn slot<'a>(g: &'a [f64], l: usize, i: usize, i_pad: usize) -> &'a [f64] {
    let o = off(l, i, i_pad);
    &g[o..o + 2 * l + 1]
}

fn axpy(y: &mut [f64], a: f64, x: &[f64]) {
    for (yi, xi) in y.iter_mut().zip(x) {
        *yi += a * xi;
    }
}

// ─────────────────────────────── tilted 좌변 격자 (equation_lhs_coeff 미러)
/// signs 순서: [A, B, C, D, E, Omega, divcon, divfree].
#[allow(clippy::too_many_arguments)]
pub fn lhs_grid(
    j: &[f64], dj: &[f64], l_max: usize, i_max: usize, h: f64, s5: &[f64],
    w: &[f64], u3: &[f64], gamma: f64, v3: &[f64], c_pd: &[f64], c_dc: &[f64],
    c_df: &[f64], signs: &[f64],
) -> Vec<f64> {
    assert!(
        l_max <= t::L_KERNEL_MAX,
        "coeff 커널 벽: l_max ≤ {} (c2 표 l_in=l+2 ≤ 12)",
        t::L_KERNEL_MAX
    );
    let (l_pad, i_pad) = (l_max + 2, i_max + 2);
    assert_eq!(j.len(), grid_len(l_pad, i_pad), "j grid length");
    assert_eq!(dj.len(), grid_len(l_pad, i_pad), "dj grid length");
    let (s_a, s_b, s_c, s_d, s_e, s_om, s_dc, s_df) = (
        signs[0], signs[1], signs[2], signs[3], signs[4], signs[5], signs[6], signs[7],
    );
    let mut out = vec![0.0; grid_len(l_max, i_max)];
    let mut o = 0;
    for l in 0..=l_max {
        let n_l = 2 * l + 1;
        for i in 0..=i_max {
            let n = (l + 2 * i) as f64;
            let lr = l as f64;
            let y = &mut out[o..o + n_l];
            // ⊥J̇: P@J + γ·dJ
            axpy(y, 1.0, &perp_p_apply(l, c_pd, slot(j, l, i, i_pad)));
            axpy(y, gamma, slot(dj, l, i, i_pad));
            // H 항
            axpy(y, h * (3.0 + n), slot(j, l, i, i_pad));
            axpy(y, h * (1.0 - n), slot(j, l, i + 1, i_pad));
            // div-con: s_dc·(Pc@J(l+1,i) + γ·cv(dJ(l+1,i), v3))
            axpy(y, s_dc, &div_p_apply("cv", l, c_dc, slot(j, l + 1, i, i_pad)));
            axpy(y, s_dc * gamma, &apply("cv", l, slot(dj, l + 1, i, i_pad), v3));
            if l >= 1 {
                let cf = lr / (2.0 * lr + 1.0);
                // div-free: s_df·(−cf)·(Pf@J(l−1,i+1) + γ·ov(dJ(l−1,i+1), v3))
                axpy(y, s_df * (-cf),
                     &div_p_apply("ov", l, c_df, slot(j, l - 1, i + 1, i_pad)));
                axpy(y, s_df * (-cf) * gamma,
                     &apply("ov", l, slot(dj, l - 1, i + 1, i_pad), v3));
                // Ω: s_om·(−l)·rot(J(l,i), w)   (w = 카르테시안!)
                axpy(y, s_om * (-lr), &apply("rot", l, slot(j, l, i, i_pad), w));
                // D: s_d·cd·[(l+n+1)·ov(J(l−1,i),u3) + (2−n)·ov(J(l−1,i+1),u3)]
                let cd = lr / (2.0 * lr + 1.0);
                axpy(y, s_d * cd * (lr + n + 1.0),
                     &apply("ov", l, slot(j, l - 1, i, i_pad), u3));
                axpy(y, s_d * cd * (2.0 - n),
                     &apply("ov", l, slot(j, l - 1, i + 1, i_pad), u3));
            }
            // E: s_e·[(n−2)·cv(J(l+1,i),u3) + (l−n)·cv(J(l+1,i−1),u3)]
            axpy(y, s_e * (n - 2.0), &apply("cv", l, slot(j, l + 1, i, i_pad), u3));
            if lr - n != 0.0 {
                axpy(y, s_e * (lr - n),
                     &apply("cv", l, slot(j, l + 1, i - 1, i_pad), u3));
            }
            if l >= 1 {
                // A: s_a·ca·[(2n+3)·c1(J(l,i),s5) + (2−2n)·c1(J(l,i+1),s5)]
                let ca = lr / (2.0 * lr + 3.0);
                axpy(y, s_a * ca * (2.0 * n + 3.0),
                     &apply("c1", l, slot(j, l, i, i_pad), s5));
                axpy(y, s_a * ca * (2.0 - 2.0 * n),
                     &apply("c1", l, slot(j, l, i + 1, i_pad), s5));
            }
            // B: s_b·[(n−1)·c2(J(l+2,i),s5) + (l−n)·c2(J(l+2,i−1),s5)]
            axpy(y, s_b * (n - 1.0), &apply("c2", l, slot(j, l + 2, i, i_pad), s5));
            if lr - n != 0.0 {
                axpy(y, s_b * (lr - n),
                     &apply("c2", l, slot(j, l + 2, i - 1, i_pad), s5));
            }
            if l >= 2 {
                // C: s_c·cc·[(n−1)·outer(J(l−2,i+2),s5) − (l+n+1)·outer(J(l−2,i+1),s5)]
                let cc = lr * (lr - 1.0) / (4.0 * lr * lr - 1.0);
                axpy(y, s_c * cc * (n - 1.0),
                     &apply("outer", l, slot(j, l - 2, i + 2, i_pad), s5));
                axpy(y, s_c * cc * (-(lr + n + 1.0)),
                     &apply("outer", l, slot(j, l - 2, i + 1, i_pad), s5));
            }
            o += n_l;
        }
    }
    out
}

// ─────────────────────────────── 질량블록 (mass_blocks_canonical 미러)
/// 반환: (diag(γI), up, down) — down 은 l=0 에서 빈 벡터.
pub fn mass_blocks(
    l: usize, gamma: f64, v3: &[f64], s_dc: f64, s_df: f64,
) -> (Vec<f64>, Vec<f64>, Vec<f64>) {
    let n = 2 * l + 1;
    let mut diag = vec![0.0; n * n];
    for p in 0..n {
        diag[p * n + p] = gamma;
    }
    // up[p,q] = s_dc·γ·Σ_a cv[p,q,a]·v3[a]
    let (g, n_out, n_in, k) = block("cv", l);
    let mut up = vec![0.0; n_out * n_in];
    for p in 0..n_out {
        for q in 0..n_in {
            let base = p * n_in * k + q * k;
            let mut acc = 0.0;
            for (a, va) in v3.iter().enumerate() {
                acc += g[base + a] * va;
            }
            up[p * n_in + q] = s_dc * gamma * acc;
        }
    }
    let down = if l >= 1 {
        let (g, n_out, n_in, k) = block("ov", l);
        let coef = s_df * (-(l as f64) / (2.0 * l as f64 + 1.0)) * gamma;
        let mut d = vec![0.0; n_out * n_in];
        for p in 0..n_out {
            for q in 0..n_in {
                let base = p * n_in * k + q * k;
                let mut acc = 0.0;
                for (a, va) in v3.iter().enumerate() {
                    acc += g[base + a] * va;
                }
                d[p * n_in + q] = coef * acc;
            }
        }
        d
    } else {
        Vec::new()
    };
    (diag, up, down)
}

// ─────────────────────────────── untilted RHS 격자 (hierarchy_rhs_coeff 미러)
/// signs 순서: [A, B, C].
pub fn rhs_grid(
    j: &[f64], l_max: usize, i_max: usize, h: f64, s5: &[f64], signs: &[f64],
) -> Vec<f64> {
    assert!(l_max <= t::L_KERNEL_MAX, "coeff 커널 벽: l_max ≤ {}", t::L_KERNEL_MAX);
    let (l_pad, i_pad) = (l_max + 2, i_max + 2);
    assert_eq!(j.len(), grid_len(l_pad, i_pad), "j grid length");
    let (s_a, s_b, s_c) = (signs[0], signs[1], signs[2]);
    let mut out = vec![0.0; grid_len(l_max, i_max)];
    let mut o = 0;
    for l in 0..=l_max {
        let n_l = 2 * l + 1;
        for i in 0..=i_max {
            let n = (l + 2 * i) as f64;
            let lr = l as f64;
            let y = &mut out[o..o + n_l];
            axpy(y, -h * (3.0 + n), slot(j, l, i, i_pad));
            axpy(y, -h * (1.0 - n), slot(j, l, i + 1, i_pad));
            if l >= 1 {
                let ca = lr / (2.0 * lr + 3.0);
                axpy(y, -s_a * ca * (2.0 * n + 3.0),
                     &apply("c1", l, slot(j, l, i, i_pad), s5));
                axpy(y, -s_a * ca * (2.0 - 2.0 * n),
                     &apply("c1", l, slot(j, l, i + 1, i_pad), s5));
            }
            axpy(y, -s_b * (n - 1.0), &apply("c2", l, slot(j, l + 2, i, i_pad), s5));
            if lr - n != 0.0 {
                axpy(y, -s_b * (lr - n),
                     &apply("c2", l, slot(j, l + 2, i - 1, i_pad), s5));
            }
            if l >= 2 {
                let cc = lr * (lr - 1.0) / (4.0 * lr * lr - 1.0);
                axpy(y, -s_c * cc * (n - 1.0),
                     &apply("outer", l, slot(j, l - 2, i + 2, i_pad), s5));
                axpy(y, -s_c * cc * (-(lr + n + 1.0)),
                     &apply("outer", l, slot(j, l - 2, i + 1, i_pad), s5));
            }
            o += n_l;
        }
    }
    out
}

// ═══════════════════════════════ cargo 단위시험
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn table_offsets_are_consistent() {
        for l in 2..=12 {
            let (g, n_out, n_in, k) = block("outer", l);
            assert_eq!(g.len(), n_out * n_in * k);
        }
        for l in 0..=10 {
            let (g, n_out, n_in, k) = block("c2", l);
            assert_eq!(g.len(), n_out * n_in * k);
        }
        for l in 1..=12 {
            for op in ["c1", "ov", "rot"] {
                let (g, n_out, n_in, k) = block(op, l);
                assert_eq!(g.len(), n_out * n_in * k, "{op} l={l}");
            }
        }
    }

    #[test]
    #[should_panic(expected = "outside table range")]
    fn c2_wall_at_l11() {
        block("c2", 11);
    }

    #[test]
    fn apply_matches_manual_sum() {
        let (g, n_out, n_in, k) = block("c1", 2);
        let c: Vec<f64> = (0..n_in).map(|m| 0.3 + 0.1 * m as f64).collect();
        let s: Vec<f64> = (0..k).map(|kk| 1.0 - 0.2 * kk as f64).collect();
        let got = apply("c1", 2, &c, &s);
        for p in 0..n_out {
            let mut want = 0.0;
            for m in 0..n_in {
                for kk in 0..k {
                    want += g[p * n_in * k + m * k + kk] * c[m] * s[kk];
                }
            }
            assert!((got[p] - want).abs() <= 1e-15 * want.abs().max(1.0));
        }
    }

    #[test]
    fn mass_down_empty_at_l0() {
        let v3 = [0.1, -0.2, 0.05];
        let (diag, up, down) = mass_blocks(0, 1.1, &v3, 1.0, -1.0);
        assert_eq!(diag, vec![1.1]);
        assert_eq!(up.len(), 3);
        assert!(down.is_empty());
    }

    #[test]
    fn grid_len_matches_offsets() {
        let (l_pad, i_pad) = (5, 3);
        assert_eq!(off(l_pad, i_pad, i_pad) + 2 * l_pad + 1,
                   grid_len(l_pad, i_pad));
    }
}
