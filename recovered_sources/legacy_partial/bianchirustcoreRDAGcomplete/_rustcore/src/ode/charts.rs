//! R2 · 차트별 배경 RHS (Wainwright-Ellis 팽창 정규화) — Python `bianchi.charts` 미러.
//!
//! Class A  (`charts.class_a`):  상태 (Σ₊, Σ₋, N₁, N₂, N₃),  Ω 는 Gauss 로 소거.
//!   ★ N_i' = (…)·N_i 의 **곱셈 구조** 덕에 N_i = 0 과 부호가 부동소수점에서도 정확히
//!     보존된다 → 유형 안전성이 구조적으로 보장 (Python 주석과 동일한 성질을 Rust 에서도).
//! Class B  (`charts.class_b`):  상태 (Σ₊, Σ̃, Δ, Ã, N₊),  파라미터 κ = 1/h.
//!   유도 확정 계수 (b3,c2,c) = (-4,2,6);  b3=-4 는 Codazzi 구속면 위에서만 성립.

pub const SQRT3: f64 = 1.732_050_807_568_877_2;
pub const K_COEFF_WE: f64 = 1.0 / 12.0;
pub const S_COEFF_WE: f64 = 1.0 / 6.0;

/// 차트 종류 (파라미터 포함).
#[derive(Clone, Copy, Debug)]
pub enum Chart {
    /// Class A 비틸트 (γ)
    ClassA { gamma: f64 },
    /// Class B 비틸트 (γ, κ=1/h)
    ClassB { gamma: f64, kappa: f64 },
}

impl Chart {
    pub fn nstates(&self) -> usize {
        5
    }
}

/// 감속 파라미터 q = 2Σ² + ½(3γ-2)Ω  (비틸트; `charts.base.deceleration`).
#[inline]
pub fn deceleration(sigma2: f64, omega: f64, gamma: f64) -> f64 {
    2.0 * sigma2 + 0.5 * (3.0 * gamma - 2.0) * omega
}

// ───────────────────────────────── Class A
#[inline]
pub fn curvature_k_a(n1: f64, n2: f64, n3: f64) -> f64 {
    K_COEFF_WE * (n1 * n1 + n2 * n2 + n3 * n3 - 2.0 * (n1 * n2 + n2 * n3 + n3 * n1))
}

#[inline]
pub fn s_plus(n1: f64, n2: f64, n3: f64) -> f64 {
    S_COEFF_WE * ((n2 - n3) * (n2 - n3) - n1 * (2.0 * n1 - n2 - n3))
}

#[inline]
pub fn s_minus(n1: f64, n2: f64, n3: f64) -> f64 {
    (n3 - n2) * (n1 - n2 - n3) / (2.0 * SQRT3)
}

/// Class A 보조량 (Σ², K, Ω, q).
#[inline]
pub fn aux_a(y: &[f64], gamma: f64) -> (f64, f64, f64, f64) {
    let (sp, sm, n1, n2, n3) = (y[0], y[1], y[2], y[3], y[4]);
    let sigma2 = sp * sp + sm * sm;
    let k = curvature_k_a(n1, n2, n3);
    let omega = 1.0 - sigma2 - k;
    let q = deceleration(sigma2, omega, gamma);
    (sigma2, k, omega, q)
}

// ───────────────────────────────── Class B
#[inline]
pub fn n_tilde(np: f64, at: f64, kappa: f64) -> f64 {
    (np * np - kappa * at) / 3.0
}

/// Class B 보조량 (Ñ, Σ², K, Ω, q).
#[inline]
pub fn aux_b(y: &[f64], gamma: f64, kappa: f64) -> (f64, f64, f64, f64, f64) {
    let (sp, st, at, np) = (y[0], y[1], y[3], y[4]);
    let nt = n_tilde(np, at, kappa);
    let sigma2 = sp * sp + st;
    let k = nt + at;
    let omega = 1.0 - sigma2 - k;
    let q = deceleration(sigma2, omega, gamma);
    (nt, sigma2, k, omega, q)
}

/// 차트 RHS dy/dτ.  `out` 에 기록 (길이 5).
pub fn rhs(chart: &Chart, y: &[f64], out: &mut [f64]) {
    match *chart {
        Chart::ClassA { gamma } => {
            let (_s2, _k, _om, q) = aux_a(y, gamma);
            let (sp, sm, n1, n2, n3) = (y[0], y[1], y[2], y[3], y[4]);
            out[0] = -(2.0 - q) * sp - s_plus(n1, n2, n3);
            out[1] = -(2.0 - q) * sm - s_minus(n1, n2, n3);
            // 곱셈 구조 — N_i = 0 이 정확히 보존
            out[2] = (q - 4.0 * sp) * n1;
            out[3] = (q + 2.0 * sp + 2.0 * SQRT3 * sm) * n2;
            out[4] = (q + 2.0 * sp - 2.0 * SQRT3 * sm) * n3;
        }
        Chart::ClassB { gamma, kappa } => {
            let (nt, _s2, _k, _om, q) = aux_b(y, gamma, kappa);
            let (sp, st, de, at, np) = (y[0], y[1], y[2], y[3], y[4]);
            out[0] = (q - 2.0) * sp - 2.0 * nt;
            out[1] = 2.0 * (q - 2.0) * st - 4.0 * sp * at - 4.0 * de * np;
            out[2] = 2.0 * (q + sp - 1.0) * de + 2.0 * (st - nt) * np;
            out[3] = 2.0 * (q + 2.0 * sp) * at;
            out[4] = (q + 2.0 * sp) * np + 6.0 * de;
        }
    }
}

/// Ω (물리 영역 진단·구속 감시용).
pub fn omega(chart: &Chart, y: &[f64]) -> f64 {
    match *chart {
        Chart::ClassA { gamma } => aux_a(y, gamma).2,
        Chart::ClassB { gamma, kappa } => aux_b(y, gamma, kappa).3,
    }
}

/// Class B Codazzi 구속 C = Σ̃Ñ - Δ² - Σ₊²Ã  (Class A 는 0 반환).
pub fn codazzi(chart: &Chart, y: &[f64]) -> f64 {
    match *chart {
        Chart::ClassA { .. } => 0.0,
        Chart::ClassB { kappa, .. } => {
            let (sp, st, de, at, np) = (y[0], y[1], y[2], y[3], y[4]);
            st * n_tilde(np, at, kappa) - de * de - sp * sp * at
        }
    }
}

/// 야코비안-벡터 곱 J·v (중심차분).  BDF/ESDIRK 의 Newton 반복용.
/// FD 는 수렴률에만 영향을 주고 해의 정확도는 잔차가 결정하므로 안전하다.
pub fn jac_mul(chart: &Chart, y: &[f64], v: &[f64], out: &mut [f64]) {
    let n = y.len();
    let ynorm = y.iter().fold(0.0f64, |a, b| a.max(b.abs())).max(1.0);
    let vnorm = v.iter().fold(0.0f64, |a, b| a.max(b.abs()));
    if vnorm == 0.0 {
        out[..n].fill(0.0);
        return;
    }
    let eps = 1e-7 * ynorm / vnorm;
    let mut yp = [0.0f64; 5];
    let mut ym = [0.0f64; 5];
    for i in 0..n {
        yp[i] = y[i] + eps * v[i];
        ym[i] = y[i] - eps * v[i];
    }
    let mut fp = [0.0f64; 5];
    let mut fm = [0.0f64; 5];
    rhs(chart, &yp[..n], &mut fp[..n]);
    rhs(chart, &ym[..n], &mut fm[..n]);
    for i in 0..n {
        out[i] = (fp[i] - fm[i]) / (2.0 * eps);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn class_a_preserves_zero_n() {
        // N_i = 0 이면 N_i' = 0 (곱셈 구조) — Bianchi I 불변
        let c = Chart::ClassA { gamma: 4.0 / 3.0 };
        let y = [0.6, 0.3, 0.0, 0.0, 0.0];
        let mut out = [0.0; 5];
        rhs(&c, &y, &mut out);
        assert_eq!(out[2], 0.0);
        assert_eq!(out[3], 0.0);
        assert_eq!(out[4], 0.0);
    }

    #[test]
    fn kasner_circle_is_vacuum() {
        // Σ₊²+Σ₋²=1, N=0 → Ω=0 (진공 Kasner)
        let c = Chart::ClassA { gamma: 4.0 / 3.0 };
        let y = [0.6, 0.8, 0.0, 0.0, 0.0];
        assert!(omega(&c, &y).abs() < 1e-15);
    }

    #[test]
    fn jac_mul_matches_finite_difference() {
        let c = Chart::ClassA { gamma: 1.5 };
        let y = [0.3, -0.2, 0.5, 0.1, -0.4];
        let v = [1.0, 0.0, 0.0, 0.0, 0.0];
        let mut jv = [0.0; 5];
        jac_mul(&c, &y, &v, &mut jv);
        // ∂f/∂Σ₊ 를 성긴 차분으로 대조
        let h = 1e-6;
        let (mut yp, mut ym) = (y, y);
        yp[0] += h;
        ym[0] -= h;
        let (mut fp, mut fm) = ([0.0; 5], [0.0; 5]);
        rhs(&c, &yp, &mut fp);
        rhs(&c, &ym, &mut fm);
        for i in 0..5 {
            assert!((jv[i] - (fp[i] - fm[i]) / (2.0 * h)).abs() < 1e-5);
        }
    }
}
