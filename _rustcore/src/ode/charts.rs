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
}
