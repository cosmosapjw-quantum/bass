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

/// 상태벡터 최대 길이 (class_b_tilted 의 11) — 버퍼 크기.
pub const MAX_STATES: usize = 11;
/// tilt 유체의 0 나눗셈 가드 (`bianchi.matter.fluid.GUARD_EPS` 와 동일).
pub const GUARD_EPS: f64 = 1e-12;
/// Existing public routing boundary for the degenerate class-B `kappa = -9` chart.
pub const KAPPA_EXCEPTIONAL: f64 = -9.0;
pub const KAPPA_EXCEPTIONAL_TOL: f64 = 1e-9;

#[inline]
fn safe(x: f64) -> f64 {
    if x.abs() < GUARD_EPS {
        if x >= 0.0 {
            GUARD_EPS
        } else {
            -GUARD_EPS
        }
    } else {
        x
    }
}

/// 차트 종류 (파라미터 포함).
#[derive(Clone, Copy, Debug)]
pub enum Chart {
    /// Class A 비틸트 (γ)
    ClassA { gamma: f64 },
    /// Class B 비틸트 (γ, κ=1/h)
    ClassB { gamma: f64, kappa: f64 },
    /// C2 · Tilted class B (Hervik 게이지, 11 상태) — `charts.class_b_tilted` 미러
    ClassBTilted { gamma: f64 },
    /// F3 · Tilted class A (n-대각 게이지, 11 상태) — `charts.class_a_tilted` 미러
    ClassATilted { gamma: f64 },
    /// C2 · 예외형 VI*_{−1/9} (HHW 게이지, 6 상태) — `charts.exceptional` 미러
    Exceptional { gamma: f64 },
    /// C2 · IX D-정규화 (Heinzle-Uggla, 7 상태) — `charts.type_ix_d` 미러.
    /// `future` 는 부호 반전 (`rhs_future`: 재붕괴 추적 방향).
    TypeIXD { gamma: f64, future: bool },
}

impl Chart {
    /// tilt 차트의 (γ, V²) — 편타(whiplash) 문턱 감시용.  비틸트는 None.
    pub fn tilt_gamma_v2(&self, y: &[f64]) -> Option<(f64, f64)> {
        match *self {
            Chart::ClassBTilted { gamma } | Chart::ClassATilted { gamma } => {
                Some((gamma, y[8] * y[8] + y[9] * y[9] + y[10] * y[10]))
            }
            _ => None,
        }
    }

    /// F3 · class A tilted 의 LRS 게이지 근접도 max|W_ij| (그 외 None).
    /// N_i→N_j (Σ_ij≠0) 에서 발산 — 문턱 초과는 게이지 붕괴 신호.
    pub fn lrs_gauge_w_max(&self, y: &[f64]) -> Option<f64> {
        match *self {
            Chart::ClassATilted { .. } => {
                let w12 = SQRT3 * y[2] * (y[5] + y[6]) / safe(y[5] - y[6]);
                let w13 = SQRT3 * y[3] * (y[5] + y[7]) / safe(y[5] - y[7]);
                let w23 = SQRT3 * y[4] * (y[6] + y[7]) / safe(y[6] - y[7]);
                Some(w12.abs().max(w13.abs()).max(w23.abs()))
            }
            _ => None,
        }
    }

    pub fn nstates(&self) -> usize {
        match *self {
            Chart::ClassA { .. } | Chart::ClassB { .. } => 5,
            Chart::ClassBTilted { .. } | Chart::ClassATilted { .. } => 11,
            Chart::Exceptional { .. } => 6,
            Chart::TypeIXD { .. } => 7,
        }
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

// ───────────────────────────────── C2 · Tilted class B (Hervik)
/// (Σ², K, Ω, V², G₊, G₋, q, Sv², A·v₁) — Ω 는 Gauss 로 소거 (Python 기본 경로와 동일).
#[allow(clippy::type_complexity)]
#[inline]
pub fn aux_bt(y: &[f64], gamma: f64) -> (f64, f64, f64, f64, f64, f64, f64, f64, f64) {
    let (sp, sm, s12, s13, s23) = (y[0], y[1], y[2], y[3], y[4]);
    let (n, _lam, a) = (y[5], y[6], y[7]);
    let (v1, v2, v3) = (y[8], y[9], y[10]);
    let sigma2 = sp * sp + sm * sm + s12 * s12 + s13 * s13 + s23 * s23;
    let k = n * n + a * a;
    let omega = 1.0 - sigma2 - k;
    let v2s = v1 * v1 + v2 * v2 + v3 * v3;
    let gp = safe(1.0 + (gamma - 1.0) * v2s);
    let gm = safe(1.0 - (gamma - 1.0) * v2s);
    let q = 2.0 * sigma2 + 0.5 * ((3.0 * gamma - 2.0) + (2.0 - gamma) * v2s) * omega / gp;
    // Sᵥ² = vᵀΣv  (전단행렬: 대각 (−2Σ₊, Σ₊+√3Σ₋, Σ₊−√3Σ₋), 비대각 √3·Σ_ij)
    let sv2 = -2.0 * sp * v1 * v1
        + (sp + SQRT3 * sm) * v2 * v2
        + (sp - SQRT3 * sm) * v3 * v3
        + 2.0 * SQRT3 * (s12 * v1 * v2 + s13 * v1 * v3 + s23 * v2 * v3);
    let adv = a * v1;
    (sigma2, k, omega, v2s, gp, gm, q, sv2, adv)
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
        Chart::ClassBTilted { gamma } => {
            let (_s2, _k, om, v2s, gp, gm, q, sv2, adv) = aux_bt(y, gamma);
            let (sp, sm, s12, s13, s23) = (y[0], y[1], y[2], y[3], y[4]);
            let (n, lam, a) = (y[5], y[6], y[7]);
            let (v1, v2, v3) = (y[8], y[9], y[10]);
            let r3 = SQRT3;
            let g = gamma;
            let t =
                (((3.0 * g - 4.0) - 2.0 * (g - 1.0) * adv) * (1.0 - v2s) + (2.0 - g) * sv2) / gm;
            // ★ 3(S12²+S13²) 는 프레임 회전항 (게이지 유지가 회전 3개를 전부 소모)
            out[0] = (q - 2.0) * sp + 3.0 * (s12 * s12 + s13 * s13) - 2.0 * n * n
                + (g * om / (2.0 * gp)) * (-2.0 * v1 * v1 + v2 * v2 + v3 * v3);
            out[1] = (q - 2.0 - 2.0 * r3 * s23 * lam) * sm
                + r3 * (s12 * s12 - s13 * s13)
                + 2.0 * a * n
                + (r3 * g * om / (2.0 * gp)) * (v2 * v2 - v3 * v3);
            out[2] = (q - 2.0 - 3.0 * sp - r3 * sm) * s12 - r3 * (s23 + sm * lam) * s13
                + (r3 * g * om / gp) * v1 * v2;
            out[3] = (q - 2.0 - 3.0 * sp + r3 * sm) * s13 - r3 * (s23 - sm * lam) * s12
                + (r3 * g * om / gp) * v1 * v3;
            out[4] = (q - 2.0) * s23 - 2.0 * r3 * n * n * lam
                + 2.0 * r3 * lam * sm * sm
                + 2.0 * r3 * s12 * s13
                + (r3 * g * om / gp) * v2 * v3;
            out[5] = (q + 2.0 * sp + 2.0 * r3 * s23 * lam) * n;
            out[6] = 2.0 * r3 * s23 * (1.0 - lam * lam);
            out[7] = (q + 2.0 * sp) * a;
            out[8] = (t + 2.0 * sp) * v1
                - 2.0 * r3 * s13 * v3
                - 2.0 * r3 * s12 * v2
                - a * (v2 * v2 + v3 * v3)
                - r3 * n * (v2 * v2 - v3 * v3);
            out[9] = (t - sp - r3 * sm) * v2 - r3 * (s23 + sm * lam) * v3
                + r3 * lam * n * v1 * v3
                + (a + r3 * n) * v1 * v2;
            out[10] = (t - sp + r3 * sm) * v3 - r3 * (s23 - sm * lam) * v2 - r3 * lam * n * v1 * v2
                + (a - r3 * n) * v1 * v3;
        }
        Chart::ClassATilted { gamma } => {
            // F3: `charts.class_a_tilted.rhs` (경로 1) 성분별 미러 — 두 경로
            //   합성검증(≤4.4e−16)을 통과한 산술을 그대로 옮긴다.
            let g = gamma;
            let (sp, sm, s12, s13, s23) = (y[0], y[1], y[2], y[3], y[4]);
            let (n1, n2, n3) = (y[5], y[6], y[7]);
            let (v1, v2, v3) = (y[8], y[9], y[10]);
            let r3 = SQRT3;
            let s2t = sp * sp + sm * sm + s12 * s12 + s13 * s13 + s23 * s23;
            let k = (n1 * n1 + n2 * n2 + n3 * n3 - 2.0 * (n1 * n2 + n2 * n3 + n3 * n1)) / 12.0;
            let om = 1.0 - s2t - k;
            let v2s = v1 * v1 + v2 * v2 + v3 * v3;
            let gp = safe(1.0 + (g - 1.0) * v2s);
            let gm = safe(1.0 - (g - 1.0) * v2s);
            let q = 2.0 * s2t + 0.5 * ((3.0 * g - 2.0) + (2.0 - g) * v2s) * om / gp;
            let (s1, s2c, s3c) = (-2.0 * sp, sp + r3 * sm, sp - r3 * sm);
            let (s12m, s13m, s23m) = (r3 * s12, r3 * s13, r3 * s23);
            let sv2 = s1 * v1 * v1
                + s2c * v2 * v2
                + s3c * v3 * v3
                + 2.0 * (s12m * v1 * v2 + s13m * v1 * v3 + s23m * v2 * v3);
            // 게이지 회전 (n-대각 유지; 0/0 불변부분공간은 분자 0)
            let w12 = s12m * (n1 + n2) / safe(n1 - n2);
            let w13 = s13m * (n1 + n3) / safe(n1 - n3);
            let w23 = s23m * (n2 + n3) / safe(n2 - n3);
            // ³S (대각)
            let tn = n1 + n2 + n3;
            let b1 = 2.0 * n1 * n1 - tn * n1;
            let b2 = 2.0 * n2 * n2 - tn * n2;
            let b3 = 2.0 * n3 * n3 - tn * n3;
            let bm = (b1 + b2 + b3) / 3.0;
            let (s3_1, s3_2, s3_3) = (b1 - bm, b2 - bm, b3 - bm);
            // Π
            let c_pi = 3.0 * g * om / gp;
            let pi11 = c_pi * (v1 * v1 - v2s / 3.0);
            let pi22 = c_pi * (v2 * v2 - v2s / 3.0);
            let pi33 = c_pi * (v3 * v3 - v2s / 3.0);
            let pi12 = c_pi * v1 * v2;
            let pi13 = c_pi * v1 * v3;
            let pi23 = c_pi * v2 * v3;
            // [W,Σ]
            let c11 = 2.0 * (w12 * s12m + w13 * s13m);
            let c22 = 2.0 * (-w12 * s12m + w23 * s23m);
            let c33 = 2.0 * (-w13 * s13m - w23 * s23m);
            let c12 = w12 * (s2c - s1) + w13 * s23m + w23 * s13m;
            let c13 = w13 * (s3c - s1) + w12 * s23m - w23 * s12m;
            let c23 = w23 * (s3c - s2c) - w12 * s13m - w13 * s12m;
            let d11 = -(2.0 - q) * s1 - s3_1 + pi11 + c11;
            let d22 = -(2.0 - q) * s2c - s3_2 + pi22 + c22;
            let d33 = -(2.0 - q) * s3c - s3_3 + pi33 + c33;
            let d12 = -(2.0 - q) * s12m + pi12 + c12;
            let d13 = -(2.0 - q) * s13m + pi13 + c13;
            let d23 = -(2.0 - q) * s23m + pi23 + c23;
            // v' = T v − Σv + W v − v×(Nv)
            let t = ((3.0 * g - 4.0) * (1.0 - v2s) + (2.0 - g) * sv2) / gm;
            let sv_1 = s1 * v1 + s12m * v2 + s13m * v3;
            let sv_2 = s12m * v1 + s2c * v2 + s23m * v3;
            let sv_3 = s13m * v1 + s23m * v2 + s3c * v3;
            let wv1 = w12 * v2 + w13 * v3;
            let wv2 = -w12 * v1 + w23 * v3;
            let wv3 = -w13 * v1 - w23 * v2;
            let p1 = v2 * (n3 * v3) - v3 * (n2 * v2);
            let p2 = v3 * (n1 * v1) - v1 * (n3 * v3);
            let p3 = v1 * (n2 * v2) - v2 * (n1 * v1);
            out[0] = -d11 / 2.0;
            out[1] = (d22 - d33) / (2.0 * r3);
            out[2] = d12 / r3;
            out[3] = d13 / r3;
            out[4] = d23 / r3;
            // 곱셈 구조 — N_i = 0/부호가 tilt 에서도 정확 보존
            out[5] = (q + 2.0 * s1) * n1;
            out[6] = (q + 2.0 * s2c) * n2;
            out[7] = (q + 2.0 * s3c) * n3;
            out[8] = t * v1 - sv_1 + wv1 - p1;
            out[9] = t * v2 - sv_2 + wv2 - p2;
            out[10] = t * v3 - sv_3 + wv3 - p3;
        }
        Chart::Exceptional { gamma } => {
            let (sp, sm, s2, sx, nm, a) = (y[0], y[1], y[2], y[3], y[4], y[5]);
            let sigma2 = sp * sp + sm * sm + s2 * s2 + sx * sx;
            let k = nm * nm + 4.0 * a * a; // 4 는 게이지 n23=3A 산물
            let omega = 1.0 - sigma2 - k;
            let q = deceleration(sigma2, omega, gamma);
            out[0] = (q - 2.0) * sp + 3.0 * s2 * s2 - 2.0 * nm * nm - 6.0 * a * a;
            out[1] = (q - 2.0) * sm - SQRT3 * s2 * s2 + 2.0 * SQRT3 * sx * sx
                - 2.0 * SQRT3 * nm * nm
                + 2.0 * SQRT3 * a * a;
            out[2] = (q - 3.0 * sp + SQRT3 * sm - 2.0) * s2;
            out[3] = (q - 2.0 * SQRT3 * sm - 2.0) * sx - 8.0 * nm * a;
            out[4] = (q + 2.0 * sp + 2.0 * SQRT3 * sm) * nm + 6.0 * sx * a;
            out[5] = (q + 2.0 * sp) * a;
        }
        Chart::TypeIXD { gamma, future } => {
            let h = y[0];
            let sv = [y[1], y[2], y[3]];
            let nv = [y[4], y[5], y[6]];
            let sigma2 = (sv[0] * sv[0] + sv[1] * sv[1] + sv[2] * sv[2]) / 6.0;
            let omega = 1.0 - sigma2 - (nv[0] * nv[0] + nv[1] * nv[1] + nv[2] * nv[2]) / 12.0;
            let q = deceleration(sigma2, omega, gamma);
            let f = (nv[0] * nv[1] * sv[2] + nv[0] * sv[1] * nv[2] + sv[0] * nv[1] * nv[2]) / 6.0;
            let s3 = [
                (nv[0] * (2.0 * nv[0] - nv[1] - nv[2]) - (nv[1] - nv[2]) * (nv[1] - nv[2])) / 3.0,
                (nv[1] * (2.0 * nv[1] - nv[2] - nv[0]) - (nv[2] - nv[0]) * (nv[2] - nv[0])) / 3.0,
                (nv[2] * (2.0 * nv[2] - nv[0] - nv[1]) - (nv[0] - nv[1]) * (nv[0] - nv[1])) / 3.0,
            ];
            let mut ds = [0.0f64; 3];
            for i in 0..3 {
                ds[i] = sv[i] * ((2.0 - q) * h - f) + s3[i];
            }
            let mean = (ds[0] + ds[1] + ds[2]) / 3.0;
            let sgn = if future { -1.0 } else { 1.0 };
            out[0] = sgn * (q * (1.0 - h * h) - f * h);
            for i in 0..3 {
                out[1 + i] = sgn * (ds[i] - mean); // trace-free 유지
                out[4 + i] = sgn * (-nv[i] * (q * h + 2.0 * sv[i] + f));
            }
        }
    }
}

/// Ω (물리 영역 진단·구속 감시용).
pub fn omega(chart: &Chart, y: &[f64]) -> f64 {
    match *chart {
        Chart::ClassA { gamma } => aux_a(y, gamma).2,
        Chart::ClassB { gamma, kappa } => aux_b(y, gamma, kappa).3,
        Chart::ClassBTilted { gamma } => aux_bt(y, gamma).2,
        Chart::ClassATilted { .. } => {
            let s2t = y[0] * y[0] + y[1] * y[1] + y[2] * y[2] + y[3] * y[3] + y[4] * y[4];
            let (n1, n2, n3) = (y[5], y[6], y[7]);
            1.0 - s2t - (n1 * n1 + n2 * n2 + n3 * n3 - 2.0 * (n1 * n2 + n2 * n3 + n3 * n1)) / 12.0
        }
        Chart::Exceptional { .. } => {
            let (sp, sm, s2, sx, nm, a) = (y[0], y[1], y[2], y[3], y[4], y[5]);
            1.0 - (sp * sp + sm * sm + s2 * s2 + sx * sx) - (nm * nm + 4.0 * a * a)
        }
        Chart::TypeIXD { .. } => {
            let sigma2 = (y[1] * y[1] + y[2] * y[2] + y[3] * y[3]) / 6.0;
            1.0 - sigma2 - (y[4] * y[4] + y[5] * y[5] + y[6] * y[6]) / 12.0
        }
    }
}

/// 차트별 **대표 구속** (Class A 는 0).
///   Class B: Codazzi C = Σ̃Ñ − Δ² − Σ₊²Ã
///   ClassBTilted: C₂ = 2Σ₊A + 2Σ₋N + γΩv₁/G₊  (Hervik Codazzi 첫 성분)
///   Exceptional:  g = (Σ₊+√3Σ₋)A − Σ_x N₋      (Codazzi C¹ = −6g)
///   TypeIXD:      정의식 G = H² + (N₁N₂+N₁N₃+N₂N₃)/6 − 1
pub fn codazzi(chart: &Chart, y: &[f64]) -> f64 {
    match *chart {
        Chart::ClassA { .. } => 0.0,
        Chart::ClassB { kappa, .. } => {
            let (sp, st, de, at, np) = (y[0], y[1], y[2], y[3], y[4]);
            st * n_tilde(np, at, kappa) - de * de - sp * sp * at
        }
        Chart::ClassBTilted { gamma } => {
            let (_s2, _k, om, _v2, gp, _gm, _q, _sv2, _adv) = aux_bt(y, gamma);
            2.0 * y[0] * y[7] + 2.0 * y[1] * y[5] + gamma * om * y[8] / gp
        }
        Chart::ClassATilted { gamma } => {
            // max_a |C_a| — C¹ 단일 성분은 v₂/v₃ 부분공간 위반에 맹목이었다
            // (리뷰 MINOR 4).  C_a = (εNΣ)_a − 3γΩv_a/G₊  (A=0, N 대각):
            //   C¹ = √3Σ₂₃(N₂−N₃) − q₁,  C² = √3Σ₁₃(N₃−N₁) − q₂,
            //   C³ = √3Σ₁₂(N₁−N₂) − q₃
            let om = omega(chart, y);
            let v2s = y[8] * y[8] + y[9] * y[9] + y[10] * y[10];
            let gp = safe(1.0 + (gamma - 1.0) * v2s);
            let cq = 3.0 * gamma * om / gp;
            let c1 = SQRT3 * y[4] * (y[6] - y[7]) - cq * y[8];
            let c2 = SQRT3 * y[3] * (y[7] - y[5]) - cq * y[9];
            let c3 = SQRT3 * y[2] * (y[5] - y[6]) - cq * y[10];
            c1.abs().max(c2.abs()).max(c3.abs())
        }
        Chart::Exceptional { .. } => (y[0] + SQRT3 * y[1]) * y[5] - y[3] * y[4],
        Chart::TypeIXD { .. } => {
            y[0] * y[0] + (y[4] * y[5] + y[4] * y[6] + y[5] * y[6]) / 6.0 - 1.0
        }
    }
}

/// RF-02B production scalar-chart inventory.
///
/// Tilted charts are deliberately excluded here: their matter closure is owned by RF-03.
/// The general 14/18-state tensor charts remain independent Python formula oracles.
pub fn scalar_state_names(chart: &Chart) -> Option<&'static [&'static str]> {
    match *chart {
        Chart::ClassA { .. } => Some(&["Sigma_p", "Sigma_m", "N1", "N2", "N3"]),
        Chart::ClassB { .. } => Some(&["Sigma_p", "Sigma_tilde", "Delta", "A_tilde", "N_p"]),
        Chart::Exceptional { .. } => {
            Some(&["Sigma_p", "Sigma_m", "Sigma_2", "Sigma_x", "N_m", "A"])
        }
        Chart::TypeIXD { .. } => Some(&["H", "S1", "S2", "S3", "N1", "N2", "N3"]),
        Chart::ClassATilted { .. } | Chart::ClassBTilted { .. } => None,
    }
}

/// Ordered live equality-constraint names used by the RF-02B pointwise projector.
pub fn scalar_constraint_names(chart: &Chart) -> Option<&'static [&'static str]> {
    match *chart {
        Chart::ClassA { .. } => Some(&[]),
        Chart::ClassB { .. } => Some(&["codazzi"]),
        Chart::Exceptional { .. } => Some(&["g"]),
        Chart::TypeIXD { .. } => Some(&["definition", "trace"]),
        Chart::ClassATilted { .. } | Chart::ClassBTilted { .. } => None,
    }
}

#[inline]
fn check_scalar_buffers(
    chart: &Chart,
    y: &[f64],
    other: Option<&[f64]>,
    out_len: usize,
) -> Result<usize, &'static str> {
    let names = scalar_state_names(chart).ok_or("chart is outside RF-02B scalar closure")?;
    let n = names.len();
    if y.len() != n || other.is_some_and(|v| v.len() != n) || out_len < n {
        return Err("scalar chart buffer length mismatch");
    }
    if !y.iter().all(|x| x.is_finite()) || other.is_some_and(|v| !v.iter().all(|x| x.is_finite())) {
        return Err("scalar chart buffers must be finite");
    }
    Ok(n)
}

/// Exact algebraic directional derivative `J_rhs(y) * v` for the RF-02B scalar closure.
///
/// This is separate from [`jac_mul`], which remains the RF-02C-owned solver finite-
/// difference callback.  Moving the BDF solver to this operator requires RF-02C event,
/// restart, and convergence proof and is intentionally not done here.
pub fn exact_jvp(chart: &Chart, y: &[f64], v: &[f64], out: &mut [f64]) -> Result<(), &'static str> {
    let n = check_scalar_buffers(chart, y, Some(v), out.len())?;
    if v.iter().all(|x| *x == 0.0) {
        out[..n].fill(0.0);
        return Ok(());
    }
    match *chart {
        Chart::ClassA { gamma } => {
            let (sp, sm, n1, n2, n3) = (y[0], y[1], y[2], y[3], y[4]);
            let (dsp, dsm, dn1, dn2, dn3) = (v[0], v[1], v[2], v[3], v[4]);
            let sigma2 = sp * sp + sm * sm;
            let dsigma2 = 2.0 * (sp * dsp + sm * dsm);
            let k = curvature_k_a(n1, n2, n3);
            let dk = K_COEFF_WE
                * (2.0 * (n1 * dn1 + n2 * dn2 + n3 * dn3)
                    - 2.0 * (dn1 * n2 + n1 * dn2 + dn2 * n3 + n2 * dn3 + dn3 * n1 + n3 * dn1));
            let om = 1.0 - sigma2 - k;
            let dom = -dsigma2 - dk;
            let matter = 0.5 * (3.0 * gamma - 2.0);
            let q = 2.0 * sigma2 + matter * om;
            let dq = 2.0 * dsigma2 + matter * dom;
            let dsp_curv = S_COEFF_WE
                * (2.0 * (n2 - n3) * (dn2 - dn3)
                    - dn1 * (2.0 * n1 - n2 - n3)
                    - n1 * (2.0 * dn1 - dn2 - dn3));
            let dsm_curv =
                ((dn3 - dn2) * (n1 - n2 - n3) + (n3 - n2) * (dn1 - dn2 - dn3)) / (2.0 * SQRT3);
            out[0] = dq * sp + (q - 2.0) * dsp - dsp_curv;
            out[1] = dq * sm + (q - 2.0) * dsm - dsm_curv;
            out[2] = (dq - 4.0 * dsp) * n1 + (q - 4.0 * sp) * dn1;
            out[3] =
                (dq + 2.0 * dsp + 2.0 * SQRT3 * dsm) * n2 + (q + 2.0 * sp + 2.0 * SQRT3 * sm) * dn2;
            out[4] =
                (dq + 2.0 * dsp - 2.0 * SQRT3 * dsm) * n3 + (q + 2.0 * sp - 2.0 * SQRT3 * sm) * dn3;
        }
        Chart::ClassB { gamma, kappa } => {
            let (sp, st, de, at, np) = (y[0], y[1], y[2], y[3], y[4]);
            let (dsp, dst, dde, dat, dnp) = (v[0], v[1], v[2], v[3], v[4]);
            let nt = n_tilde(np, at, kappa);
            let dnt = (2.0 * np * dnp - kappa * dat) / 3.0;
            let sigma2 = sp * sp + st;
            let dsigma2 = 2.0 * sp * dsp + dst;
            let om = 1.0 - sigma2 - nt - at;
            let dom = -dsigma2 - dnt - dat;
            let matter = 0.5 * (3.0 * gamma - 2.0);
            let q = 2.0 * sigma2 + matter * om;
            let dq = 2.0 * dsigma2 + matter * dom;
            out[0] = dq * sp + (q - 2.0) * dsp - 2.0 * dnt;
            out[1] = 2.0 * (dq * st + (q - 2.0) * dst)
                - 4.0 * (dsp * at + sp * dat)
                - 4.0 * (dde * np + de * dnp);
            out[2] = 2.0 * ((dq + dsp) * de + (q + sp - 1.0) * dde)
                + 2.0 * ((dst - dnt) * np + (st - nt) * dnp);
            out[3] = 2.0 * ((dq + 2.0 * dsp) * at + (q + 2.0 * sp) * dat);
            out[4] = (dq + 2.0 * dsp) * np + (q + 2.0 * sp) * dnp + 6.0 * dde;
        }
        Chart::Exceptional { gamma } => {
            let (sp, sm, s2, sx, nm, a) = (y[0], y[1], y[2], y[3], y[4], y[5]);
            let (dsp, dsm, ds2, dsx, dnm, da) = (v[0], v[1], v[2], v[3], v[4], v[5]);
            let sigma2 = sp * sp + sm * sm + s2 * s2 + sx * sx;
            let dsigma2 = 2.0 * (sp * dsp + sm * dsm + s2 * ds2 + sx * dsx);
            let k = nm * nm + 4.0 * a * a;
            let dk = 2.0 * nm * dnm + 8.0 * a * da;
            let om = 1.0 - sigma2 - k;
            let dom = -dsigma2 - dk;
            let matter = 0.5 * (3.0 * gamma - 2.0);
            let q = 2.0 * sigma2 + matter * om;
            let dq = 2.0 * dsigma2 + matter * dom;
            out[0] = dq * sp + (q - 2.0) * dsp + 6.0 * s2 * ds2 - 4.0 * nm * dnm - 12.0 * a * da;
            out[1] = dq * sm + (q - 2.0) * dsm - 2.0 * SQRT3 * s2 * ds2 + 4.0 * SQRT3 * sx * dsx
                - 4.0 * SQRT3 * nm * dnm
                + 4.0 * SQRT3 * a * da;
            out[2] = (dq - 3.0 * dsp + SQRT3 * dsm) * s2 + (q - 3.0 * sp + SQRT3 * sm - 2.0) * ds2;
            out[3] = (dq - 2.0 * SQRT3 * dsm) * sx + (q - 2.0 * SQRT3 * sm - 2.0) * dsx
                - 8.0 * (dnm * a + nm * da);
            out[4] = (dq + 2.0 * dsp + 2.0 * SQRT3 * dsm) * nm
                + (q + 2.0 * sp + 2.0 * SQRT3 * sm) * dnm
                + 6.0 * (dsx * a + sx * da);
            out[5] = (dq + 2.0 * dsp) * a + (q + 2.0 * sp) * da;
        }
        Chart::TypeIXD { gamma, future } => {
            let h = y[0];
            let dh = v[0];
            let s = [y[1], y[2], y[3]];
            let ds = [v[1], v[2], v[3]];
            let nn = [y[4], y[5], y[6]];
            let dn = [v[4], v[5], v[6]];
            let sigma2 = (s[0] * s[0] + s[1] * s[1] + s[2] * s[2]) / 6.0;
            let dsigma2 = (s[0] * ds[0] + s[1] * ds[1] + s[2] * ds[2]) / 3.0;
            let n2 = nn[0] * nn[0] + nn[1] * nn[1] + nn[2] * nn[2];
            let dn2 = 2.0 * (nn[0] * dn[0] + nn[1] * dn[1] + nn[2] * dn[2]);
            let om = 1.0 - sigma2 - n2 / 12.0;
            let dom = -dsigma2 - dn2 / 12.0;
            let matter = 0.5 * (3.0 * gamma - 2.0);
            let q = 2.0 * sigma2 + matter * om;
            let dq = 2.0 * dsigma2 + matter * dom;
            let f = (nn[0] * nn[1] * s[2] + nn[0] * s[1] * nn[2] + s[0] * nn[1] * nn[2]) / 6.0;
            let df = (dn[0] * nn[1] * s[2]
                + nn[0] * dn[1] * s[2]
                + nn[0] * nn[1] * ds[2]
                + dn[0] * s[1] * nn[2]
                + nn[0] * ds[1] * nn[2]
                + nn[0] * s[1] * dn[2]
                + ds[0] * nn[1] * nn[2]
                + s[0] * dn[1] * nn[2]
                + s[0] * nn[1] * dn[2])
                / 6.0;
            let ds3 = [
                (dn[0] * (2.0 * nn[0] - nn[1] - nn[2]) + nn[0] * (2.0 * dn[0] - dn[1] - dn[2])
                    - 2.0 * (nn[1] - nn[2]) * (dn[1] - dn[2]))
                    / 3.0,
                (dn[1] * (2.0 * nn[1] - nn[2] - nn[0]) + nn[1] * (2.0 * dn[1] - dn[2] - dn[0])
                    - 2.0 * (nn[2] - nn[0]) * (dn[2] - dn[0]))
                    / 3.0,
                (dn[2] * (2.0 * nn[2] - nn[0] - nn[1]) + nn[2] * (2.0 * dn[2] - dn[0] - dn[1])
                    - 2.0 * (nn[0] - nn[1]) * (dn[0] - dn[1]))
                    / 3.0,
            ];
            let mut d_raw = [0.0; 3];
            for i in 0..3 {
                let factor = (2.0 - q) * h - f;
                let dfactor = -dq * h + (2.0 - q) * dh - df;
                d_raw[i] = ds[i] * factor + s[i] * dfactor + ds3[i];
            }
            let mean = (d_raw[0] + d_raw[1] + d_raw[2]) / 3.0;
            let sign = if future { -1.0 } else { 1.0 };
            out[0] = sign * (dq * (1.0 - h * h) - 2.0 * q * h * dh - df * h - f * dh);
            for i in 0..3 {
                out[1 + i] = sign * (d_raw[i] - mean);
                let factor = q * h + 2.0 * s[i] + f;
                let dfactor = dq * h + q * dh + 2.0 * ds[i] + df;
                out[4 + i] = sign * (-dn[i] * factor - nn[i] * dfactor);
            }
        }
        Chart::ClassATilted { .. } | Chart::ClassBTilted { .. } => {
            return Err("chart is outside RF-02B scalar closure");
        }
    }
    Ok(())
}

/// Ordered live equality-constraint vector for pointwise RF-02B operators.
pub fn constraint_values(chart: &Chart, y: &[f64], out: &mut [f64]) -> Result<usize, &'static str> {
    let n = check_scalar_buffers(chart, y, None, y.len())?;
    let m = scalar_constraint_names(chart)
        .expect("checked scalar chart")
        .len();
    if out.len() < m {
        return Err("constraint output buffer length mismatch");
    }
    match *chart {
        Chart::ClassA { .. } => {}
        Chart::ClassB { .. } | Chart::Exceptional { .. } => out[0] = codazzi(chart, y),
        Chart::TypeIXD { .. } => {
            out[0] = codazzi(chart, y);
            out[1] = y[1] + y[2] + y[3];
        }
        Chart::ClassATilted { .. } | Chart::ClassBTilted { .. } => unreachable!(),
    }
    debug_assert_eq!(n, y.len());
    Ok(m)
}

fn constraint_jacobian(
    chart: &Chart,
    y: &[f64],
    jac: &mut [[f64; MAX_STATES]; 2],
) -> Result<usize, &'static str> {
    check_scalar_buffers(chart, y, None, y.len())?;
    jac.fill([0.0; MAX_STATES]);
    match *chart {
        Chart::ClassA { .. } => Ok(0),
        Chart::ClassB { kappa, .. } => {
            let (sp, st, _de, at, np) = (y[0], y[1], y[2], y[3], y[4]);
            jac[0][0] = -2.0 * sp * at;
            jac[0][1] = n_tilde(np, at, kappa);
            jac[0][2] = -2.0 * y[2];
            jac[0][3] = -kappa * st / 3.0 - sp * sp;
            jac[0][4] = 2.0 * st * np / 3.0;
            Ok(1)
        }
        Chart::Exceptional { .. } => {
            let (sp, sm, _s2, sx, nm, a) = (y[0], y[1], y[2], y[3], y[4], y[5]);
            jac[0][0] = a;
            jac[0][1] = SQRT3 * a;
            jac[0][3] = -nm;
            jac[0][4] = -sx;
            jac[0][5] = sp + SQRT3 * sm;
            Ok(1)
        }
        Chart::TypeIXD { .. } => {
            let (h, n1, n2, n3) = (y[0], y[4], y[5], y[6]);
            jac[0][0] = 2.0 * h;
            jac[0][4] = (n2 + n3) / 6.0;
            jac[0][5] = (n1 + n3) / 6.0;
            jac[0][6] = (n1 + n2) / 6.0;
            jac[1][1] = 1.0;
            jac[1][2] = 1.0;
            jac[1][3] = 1.0;
            Ok(2)
        }
        Chart::ClassATilted { .. } | Chart::ClassBTilted { .. } => {
            Err("chart is outside RF-02B scalar closure")
        }
    }
}

/// Fixed-contract Gauss-Newton point projection.
///
/// Only equality constraints are projected.  Physical-domain inequalities remain
/// diagnostics, exactly as in the Python authority.  No integration route invokes this
/// function implicitly.
pub fn project_constraints(
    chart: &Chart,
    y: &[f64],
    iters: usize,
    damping: f64,
    out: &mut [f64],
) -> Result<(), &'static str> {
    let n = check_scalar_buffers(chart, y, None, out.len())?;
    if !damping.is_finite() || damping < 0.0 {
        return Err("projection damping must be finite and non-negative");
    }
    out[..n].copy_from_slice(y);
    let mut c = [0.0; 2];
    let mut jac = [[0.0; MAX_STATES]; 2];
    for _ in 0..iters {
        let m = constraint_values(chart, &out[..n], &mut c)?;
        if m == 0 || c[..m].iter().all(|x| *x == 0.0) {
            break;
        }
        let jm = constraint_jacobian(chart, &out[..n], &mut jac)?;
        debug_assert_eq!(m, jm);
        let mut lambda = [0.0; 2];
        if m == 1 {
            let a00 = jac[0][..n].iter().map(|x| x * x).sum::<f64>() + damping;
            if !a00.is_finite() || a00 <= 0.0 {
                return Err("singular or non-finite projection system");
            }
            lambda[0] = c[0] / a00;
        } else {
            let a00 = jac[0][..n].iter().map(|x| x * x).sum::<f64>() + damping;
            let a11 = jac[1][..n].iter().map(|x| x * x).sum::<f64>() + damping;
            let a01 = jac[0][..n]
                .iter()
                .zip(&jac[1][..n])
                .map(|(a, b)| a * b)
                .sum::<f64>();
            let det = a00 * a11 - a01 * a01;
            if !det.is_finite() || det <= 0.0 {
                return Err("singular or non-finite projection system");
            }
            lambda[0] = (a11 * c[0] - a01 * c[1]) / det;
            lambda[1] = (-a01 * c[0] + a00 * c[1]) / det;
        }
        for j in 0..n {
            out[j] -= (0..m).map(|i| jac[i][j] * lambda[i]).sum::<f64>();
        }
        if !out[..n].iter().all(|x| x.is_finite()) {
            return Err("projection produced non-finite state");
        }
    }
    Ok(())
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
    let mut yp = [0.0f64; MAX_STATES];
    let mut ym = [0.0f64; MAX_STATES];
    for i in 0..n {
        yp[i] = y[i] + eps * v[i];
        ym[i] = y[i] - eps * v[i];
    }
    let mut fp = [0.0f64; MAX_STATES];
    let mut fm = [0.0f64; MAX_STATES];
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
    fn c2_charts_have_flrw_fixed_points() {
        // 등방 FLRW (Σ=N=A=v=0, Ω=1) 는 세 차트 모두에서 부동점 성분이 0 이어야 한다
        // (type_ix_d 는 H=1, 나머지 0).
        let mut out = [0.0f64; MAX_STATES];
        let bt = Chart::ClassBTilted { gamma: 4.0 / 3.0 };
        rhs(&bt, &[0.0; 11], &mut out[..11]);
        assert!(out[..11].iter().all(|v| v.abs() < 1e-15), "{out:?}");
        let ex = Chart::Exceptional { gamma: 4.0 / 3.0 };
        rhs(&ex, &[0.0; 6], &mut out[..6]);
        assert!(out[..6].iter().all(|v| v.abs() < 1e-15));
        let d = Chart::TypeIXD {
            gamma: 4.0 / 3.0,
            future: false,
        };
        let y = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0];
        rhs(&d, &y, &mut out[..7]);
        assert!(out[..7].iter().all(|v| v.abs() < 1e-14), "{out:?}");
    }

    #[test]
    fn exceptional_g_constraint_propagates_numerically() {
        // g' = 2(q+Σ₊−1)g — 무작위 상태(구속면 밖!)에서 FD 로 확인.
        let c = Chart::Exceptional { gamma: 1.2 };
        let y = [0.21, -0.13, 0.17, 0.09, 0.31, 0.11];
        let g0 = codazzi(&c, &y);
        let mut f = [0.0f64; 6];
        rhs(&c, &y, &mut f);
        let h = 1e-7;
        let mut yp = y;
        let mut ym = y;
        for i in 0..6 {
            yp[i] += h * f[i];
            ym[i] -= h * f[i];
        }
        let dg = (codazzi(&c, &yp) - codazzi(&c, &ym)) / (2.0 * h);
        let sigma2 = y[0] * y[0] + y[1] * y[1] + y[2] * y[2] + y[3] * y[3];
        let om = 1.0 - sigma2 - (y[4] * y[4] + 4.0 * y[5] * y[5]);
        let q = deceleration(sigma2, om, 1.2);
        assert!((dg - 2.0 * (q + y[0] - 1.0) * g0).abs() < 1e-6, "{dg} {g0}");
    }

    #[test]
    fn type_ix_d_future_is_the_exact_negation() {
        let p = Chart::TypeIXD {
            gamma: 1.0,
            future: false,
        };
        let f = Chart::TypeIXD {
            gamma: 1.0,
            future: true,
        };
        let y = [0.4, 0.1, -0.3, 0.2, 1.1, 0.9, 1.3];
        let mut a = [0.0f64; 7];
        let mut b = [0.0f64; 7];
        rhs(&p, &y, &mut a);
        rhs(&f, &y, &mut b);
        for i in 0..7 {
            assert_eq!(a[i], -b[i]);
        }
    }

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

    #[test]
    fn rf02b_scalar_schema_binds_every_packed_position() {
        let cases = [
            (
                Chart::ClassA { gamma: 1.3 },
                &["Sigma_p", "Sigma_m", "N1", "N2", "N3"][..],
            ),
            (
                Chart::ClassB {
                    gamma: 1.3,
                    kappa: -1.0,
                },
                &["Sigma_p", "Sigma_tilde", "Delta", "A_tilde", "N_p"][..],
            ),
            (
                Chart::Exceptional { gamma: 1.3 },
                &["Sigma_p", "Sigma_m", "Sigma_2", "Sigma_x", "N_m", "A"][..],
            ),
            (
                Chart::TypeIXD {
                    gamma: 1.3,
                    future: false,
                },
                &["H", "S1", "S2", "S3", "N1", "N2", "N3"][..],
            ),
        ];
        for (chart, expected) in cases {
            assert_eq!(scalar_state_names(&chart).unwrap(), expected);
        }
        assert!(scalar_state_names(&Chart::ClassATilted { gamma: 1.3 }).is_none());
        assert!(scalar_state_names(&Chart::ClassBTilted { gamma: 1.3 }).is_none());
    }

    #[test]
    fn rf02b_exact_jvp_is_linear_zero_exact_and_future_negated() {
        let past = Chart::TypeIXD {
            gamma: 1.2,
            future: false,
        };
        let future = Chart::TypeIXD {
            gamma: 1.2,
            future: true,
        };
        let y = [0.4, 0.1, -0.3, 0.2, 1.1, 0.9, 1.3];
        let v = [0.2, -0.1, 0.4, -0.3, 0.5, 0.7, -0.2];
        let mut a = [0.0; 7];
        let mut b = [0.0; 7];
        exact_jvp(&past, &y, &v, &mut a).unwrap();
        exact_jvp(&future, &y, &v, &mut b).unwrap();
        for i in 0..7 {
            assert_eq!(a[i], -b[i]);
        }

        let mut z = [1.0; 7];
        exact_jvp(&past, &y, &[0.0; 7], &mut z).unwrap();
        assert_eq!(z, [0.0; 7]);
    }

    #[test]
    fn rf02b_constraint_vectors_are_signed_and_complete() {
        let class_b = Chart::ClassB {
            gamma: 1.3,
            kappa: -1.0,
        };
        let yb = [0.2, 0.3, 0.07, 0.1, 0.4];
        let mut values = [0.0; MAX_STATES];
        let n = constraint_values(&class_b, &yb, &mut values).unwrap();
        assert_eq!(n, 1);
        assert_eq!(values[0], codazzi(&class_b, &yb));

        let ix = Chart::TypeIXD {
            gamma: 1.3,
            future: false,
        };
        let yi = [0.5, 0.2, 0.1, -0.25, 0.8, 0.9, 1.0];
        let n = constraint_values(&ix, &yi, &mut values).unwrap();
        assert_eq!(n, 2);
        assert_eq!(values[0], codazzi(&ix, &yi));
        assert_eq!(values[1], yi[1] + yi[2] + yi[3]);
    }

    #[test]
    fn rf02b_projection_is_noop_on_surface_and_repairs_off_surface() {
        let c = Chart::Exceptional { gamma: 1.3 };
        let good = [0.2, -0.1, 0.15, 0.02, 0.3, 0.02 * 0.3 / (0.2 - SQRT3 * 0.1)];
        let mut projected = [0.0; 6];
        project_constraints(&c, &good, 3, 1e-12, &mut projected).unwrap();
        assert_eq!(projected, good);

        let mut bad = good;
        bad[3] += 0.04;
        let before = codazzi(&c, &bad).abs();
        project_constraints(&c, &bad, 3, 1e-12, &mut projected).unwrap();
        let after = codazzi(&c, &projected).abs();
        assert!(after < 1e-12, "{before} -> {after}");
        assert!(after < before);
    }

    #[test]
    fn rf02b_exact_jvp_matches_independent_central_differences_on_scalar_corpus() {
        let cases: [(Chart, &[f64], &[f64]); 4] = [
            (
                Chart::ClassA { gamma: 1.3 },
                &[0.21, -0.17, 0.31, 0.13, -0.29],
                &[-0.31, -0.175, -0.04, 0.095, 0.23],
            ),
            (
                Chart::ClassB {
                    gamma: 1.25,
                    kappa: -1.0,
                },
                &[0.19, 0.24, 0.08, 0.11, 0.37],
                &[-0.31, -0.175, -0.04, 0.095, 0.23],
            ),
            (
                Chart::Exceptional { gamma: 1.2 },
                &[0.18, -0.09, 0.12, 0.05, 0.27, 0.08],
                &[-0.31, -0.202, -0.094, 0.014, 0.122, 0.23],
            ),
            (
                Chart::TypeIXD {
                    gamma: 1.1,
                    future: false,
                },
                &[0.43, 0.11, -0.27, 0.16, 0.91, 1.07, 0.83],
                &[-0.31, -0.22, -0.13, -0.04, 0.05, 0.14, 0.23],
            ),
        ];
        for (chart, y, v) in cases {
            let n = y.len();
            let mut exact = [0.0; MAX_STATES];
            exact_jvp(&chart, y, v, &mut exact[..n]).unwrap();
            let h = 1e-6;
            let mut yp = [0.0; MAX_STATES];
            let mut ym = [0.0; MAX_STATES];
            for i in 0..n {
                yp[i] = y[i] + h * v[i];
                ym[i] = y[i] - h * v[i];
            }
            let mut fp = [0.0; MAX_STATES];
            let mut fm = [0.0; MAX_STATES];
            rhs(&chart, &yp[..n], &mut fp[..n]);
            rhs(&chart, &ym[..n], &mut fm[..n]);
            for i in 0..n {
                let fd = (fp[i] - fm[i]) / (2.0 * h);
                assert!(
                    (exact[i] - fd).abs() < 2e-9,
                    "{chart:?} [{i}] {} {fd}",
                    exact[i]
                );
            }
        }
    }

    #[test]
    fn rf02b_off_surface_constraint_propagation_identities_hold() {
        let class_b = Chart::ClassB {
            gamma: 1.25,
            kappa: -1.0,
        };
        let yb = [0.19, 0.24, 0.08, 0.11, 0.37];
        let mut fb = [0.0; 5];
        rhs(&class_b, &yb, &mut fb);
        let mut jb = [[0.0; MAX_STATES]; 2];
        constraint_jacobian(&class_b, &yb, &mut jb).unwrap();
        let dc = jb[0][..5].iter().zip(fb).map(|(a, b)| a * b).sum::<f64>();
        let q = aux_b(&yb, 1.25, -1.0).4;
        assert!((dc - 4.0 * (q + yb[0] - 1.0) * codazzi(&class_b, &yb)).abs() < 2e-15);

        let ex = Chart::Exceptional { gamma: 1.2 };
        let ye = [0.18, -0.09, 0.12, 0.05, 0.27, 0.08];
        let mut fe = [0.0; 6];
        rhs(&ex, &ye, &mut fe);
        let mut je = [[0.0; MAX_STATES]; 2];
        constraint_jacobian(&ex, &ye, &mut je).unwrap();
        let dg = je[0][..6].iter().zip(fe).map(|(a, b)| a * b).sum::<f64>();
        let sigma2 = ye[0] * ye[0] + ye[1] * ye[1] + ye[2] * ye[2] + ye[3] * ye[3];
        let om = 1.0 - sigma2 - ye[4] * ye[4] - 4.0 * ye[5] * ye[5];
        let q = deceleration(sigma2, om, 1.2);
        assert!((dg - 2.0 * (q + ye[0] - 1.0) * codazzi(&ex, &ye)).abs() < 2e-15);

        let ix = Chart::TypeIXD {
            gamma: 1.1,
            future: false,
        };
        let check_definition_identity = |y: &[f64; 7]| {
            let mut f = [0.0; 7];
            rhs(&ix, y, &mut f);
            let mut jac = [[0.0; MAX_STATES]; 2];
            constraint_jacobian(&ix, y, &mut jac).unwrap();
            let dg = jac[0][..7].iter().zip(f).map(|(a, b)| a * b).sum::<f64>();
            let sigma2 = (y[1] * y[1] + y[2] * y[2] + y[3] * y[3]) / 6.0;
            let om = 1.0 - sigma2 - (y[4] * y[4] + y[5] * y[5] + y[6] * y[6]) / 12.0;
            let q = deceleration(sigma2, om, 1.1);
            let ff = (y[4] * y[5] * y[3] + y[4] * y[2] * y[6] + y[1] * y[5] * y[6]) / 6.0;
            dg + 2.0 * (q * y[0] + ff) * codazzi(&ix, y)
        };
        let trace_free = [0.43, 0.11, -0.27, 0.16, 0.91, 1.07, 0.83];
        assert!(check_definition_identity(&trace_free).abs() < 2e-15);
        let mut off_trace = trace_free;
        off_trace[3] += 0.02;
        assert!(check_definition_identity(&off_trace).abs() > 1e-8);
    }
}
