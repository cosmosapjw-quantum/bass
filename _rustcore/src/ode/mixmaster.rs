//! R4 · **Mixmaster 튐 수열 커널** — 세 벽을 **한 번의 적분**으로.
//!
//! D1b 의 Python/diffrax 판은 튐 하나마다 세 벽에 각각 이벤트를 걸어 `span` 만큼
//! 적분하고, 근을 찾으면 상태를 되감아 다시 시작했다.  튐 4번에 12번의 긴 적분이라
//! 회귀시험이 19 → 26 분으로 늘었다.  여기서는 **한 번 굴리면서** 세 사건함수를
//! 동시에 감시한다 — 되감기도, 중복 적분도 없다.
//!
//! 사건함수 (τ̃ = −τ, 특이점 방향):
//! ```text
//! g_i(τ̃) = −d ln N_i/dτ = (4Σ₊ − q,  −q − 2Σ₊ − 2√3Σ₋,  −q − 2Σ₊ + 2√3Σ₋)
//! ```
//! 튐 = **자라던 벽이 꺾이는 순간** = g_i 가 **+ → −** 로 지나는 점 (N_i 극대).
//! 스텝 끝에서 부호변화를 보고 그 스텝 안에서 이분법으로 근을 조인다 (스텝이 작아
//! 재적분이 싸다).  가장 이른 근이 그 튐이다.
//!
//! ★ u 는 튐 지점이 아니라 **튐 사이에서 max_i|N_i| 가 최소인 스텝**에서 읽는다
//!   (그 순간이 가장 Kasner 답다).  Python 판과 같은 규칙이라 값이 비교 가능하다.
//!
//! ★ 적분기는 Dormand-Prince 5(4) 적응 스텝이다.  Python 판은 diffrax Kvaerno5 라
//!   **같은 답을 낼 이유가 없다** — 그래서 값 자체를 차등시험으로 대조한다
//!   (u 는 씨앗이 정하는 양이라 적분기에 둔감하다: D1b §4 에서 rtol 1e−12 vs 1e−10
//!   이 9자리까지 같음을 이미 쟀다).

use crate::ode::charts::{aux_a, deceleration, rhs, s_minus, s_plus, Chart, K_COEFF_WE, SQRT3};

/// 튐 하나의 기록.
#[derive(Clone, Copy, Debug)]
pub struct Bounce {
    pub tau: f64,
    pub wall: usize,
    pub u: f64,
    pub tau_epoch: f64,
    pub max_n: f64,
    pub omega: f64,
}

/// Kasner 매개변수 u = p_max/p_mid,  p_i = (1 + Σ_i)/3.
pub fn kasner_u(sp: f64, sm: f64) -> f64 {
    let s = [-2.0 * sp, sp + SQRT3 * sm, sp - SQRT3 * sm];
    let mut p = [(1.0 + s[0]) / 3.0, (1.0 + s[1]) / 3.0, (1.0 + s[2]) / 3.0];
    p.sort_by(|a, b| a.partial_cmp(b).unwrap());
    if p[1].abs() < 1e-300 {
        f64::INFINITY
    } else {
        p[2] / p[1]
    }
}

/// τ̃ 기준 벽 성장률의 **음수** — 사건함수 g_i (부호가 + 이면 벽이 자라는 중).
#[inline]
pub fn event_fns(y: &[f64; 5], gamma: f64) -> [f64; 3] {
    let (_s2, _k, _om, q) = aux_a(y, gamma);
    let (sp, sm) = (y[0], y[1]);
    [
        -(q - 4.0 * sp),
        -(q + 2.0 * sp + 2.0 * SQRT3 * sm),
        -(q + 2.0 * sp - 2.0 * SQRT3 * sm),
    ]
}

#[inline]
fn f_past(chart: &Chart, y: &[f64; 5], out: &mut [f64; 5]) {
    rhs(chart, &y[..], &mut out[..]);
    for v in out.iter_mut() {
        *v = -*v; // τ̃ = −τ
    }
}

// Dormand-Prince 5(4) 계수.
const A21: f64 = 1.0 / 5.0;
const A31: f64 = 3.0 / 40.0;
const A32: f64 = 9.0 / 40.0;
const A41: f64 = 44.0 / 45.0;
const A42: f64 = -56.0 / 15.0;
const A43: f64 = 32.0 / 9.0;
const A51: f64 = 19372.0 / 6561.0;
const A52: f64 = -25360.0 / 2187.0;
const A53: f64 = 64448.0 / 6561.0;
const A54: f64 = -212.0 / 729.0;
const A61: f64 = 9017.0 / 3168.0;
const A62: f64 = -355.0 / 33.0;
const A63: f64 = 46732.0 / 5247.0;
const A64: f64 = 49.0 / 176.0;
const A65: f64 = -5103.0 / 18656.0;
const B1: f64 = 35.0 / 384.0;
const B3: f64 = 500.0 / 1113.0;
const B4: f64 = 125.0 / 192.0;
const B5: f64 = -2187.0 / 6784.0;
const B6: f64 = 11.0 / 84.0;
const E1: f64 = 71.0 / 57600.0;
const E3: f64 = -71.0 / 16695.0;
const E4: f64 = 71.0 / 1920.0;
const E5: f64 = -17253.0 / 339200.0;
const E6: f64 = 22.0 / 525.0;
const E7: f64 = -1.0 / 40.0;

/// 한 스텝 (DP54) — (y_next, 오차추정, k1 재사용용 k7).  RHS 는 클로저 (D3: 로그판 공유).
fn dp54_step<F: Fn(&[f64; 5], &mut [f64; 5])>(
    f_past: &F,
    y: &[f64; 5],
    h: f64,
    k1: &[f64; 5],
) -> ([f64; 5], f64, [f64; 5]) {
    let mut t = [0.0f64; 5];
    let mut k2 = [0.0f64; 5];
    let mut k3 = [0.0f64; 5];
    let mut k4 = [0.0f64; 5];
    let mut k5 = [0.0f64; 5];
    let mut k6 = [0.0f64; 5];
    let mut k7 = [0.0f64; 5];
    for i in 0..5 {
        t[i] = y[i] + h * A21 * k1[i];
    }
    f_past(&t, &mut k2);
    for i in 0..5 {
        t[i] = y[i] + h * (A31 * k1[i] + A32 * k2[i]);
    }
    f_past(&t, &mut k3);
    for i in 0..5 {
        t[i] = y[i] + h * (A41 * k1[i] + A42 * k2[i] + A43 * k3[i]);
    }
    f_past(&t, &mut k4);
    for i in 0..5 {
        t[i] = y[i] + h * (A51 * k1[i] + A52 * k2[i] + A53 * k3[i] + A54 * k4[i]);
    }
    f_past(&t, &mut k5);
    for i in 0..5 {
        t[i] = y[i] + h * (A61 * k1[i] + A62 * k2[i] + A63 * k3[i] + A64 * k4[i] + A65 * k5[i]);
    }
    f_past(&t, &mut k6);
    let mut yn = [0.0f64; 5];
    for i in 0..5 {
        yn[i] = y[i] + h * (B1 * k1[i] + B3 * k3[i] + B4 * k4[i] + B5 * k5[i] + B6 * k6[i]);
    }
    f_past(&yn, &mut k7); // FSAL
    let mut err = 0.0f64;
    for i in 0..5 {
        let e = h * (E1 * k1[i] + E3 * k3[i] + E4 * k4[i] + E5 * k5[i] + E6 * k6[i] + E7 * k7[i]);
        err = err.max(e.abs());
    }
    (yn, err, k7)
}

/// 스텝 시작점에서 `s`(0..1) 만큼 간 상태 — 사건 이분법에 쓴다 (작은 스텝이라 싸다).
fn state_at<F: Fn(&[f64; 5], &mut [f64; 5])>(
    f_past: &F,
    y: &[f64; 5],
    h: f64,
    s: f64,
    k1: &[f64; 5],
) -> [f64; 5] {
    dp54_step(f_past, y, h * s, k1).0
}

// ═══════════════════════════════════ D3 · 로그-벽 표현 (혼합정밀: 특이점 근방)
//
// D1b 의 반증 기록이 확정한 한계: "혼돈 증폭이 아니라 **벽의 언더플로**" — 선형 N_i 는
// 에라마다 기하급수로 죽어 배정밀도 바닥(~1e−308, 실측 잔재는 1e−13 부터 병리)을
// 만난다.  벽만 w_i = ln|N_i| 로 옮기면 (Σ 는 f64 그대로 — **혼합 표현**):
//     dw_i/dτ = (d ln N_i/dτ)          ← 곱셈 구조가 정확히 덧셈이 된다
//     N_i = s_i·e^{w_i}                ← 곡률·전단원천에서만 되돌린다
// w 의 표현범위는 ±1.8e308 — 벽이 e^{-5000} 까지 죽어도 자취를 잃지 않고 되돌아온다.
// e^{w} 가 0 으로 언더플로해도 (w < −745) 곡률 기여가 참값 e^{-745} 이하이므로
// 배정밀도에서 **정확히 옳다**.  부호 s_i 는 상수다 (N_i = 0 보존 ⇒ 부호 불변).

/// 로그 상태의 보조량 — n_i = s_i e^{w_i} 로 되돌려 기존 닫힌형을 그대로 쓴다.
#[inline]
fn aux_log(y: &[f64; 5], signs: &[f64; 3], gamma: f64) -> (f64, f64, f64, f64) {
    let (sp, sm) = (y[0], y[1]);
    let n1 = signs[0] * y[2].exp();
    let n2 = signs[1] * y[3].exp();
    let n3 = signs[2] * y[4].exp();
    let sigma2 = sp * sp + sm * sm;
    let k = K_COEFF_WE * (n1 * n1 + n2 * n2 + n3 * n3 - 2.0 * (n1 * n2 + n2 * n3 + n3 * n1));
    let omega = 1.0 - sigma2 - k;
    let q = deceleration(sigma2, omega, gamma);
    (n1, n2, n3, q)
}

/// 로그-벽 RHS (τ̃ = −τ, 특이점 방향).
#[inline]
fn f_past_log(y: &[f64; 5], signs: &[f64; 3], gamma: f64, out: &mut [f64; 5]) {
    let (sp, sm) = (y[0], y[1]);
    let (n1, n2, n3, q) = aux_log(y, signs, gamma);
    out[0] = -(-(2.0 - q) * sp - s_plus(n1, n2, n3));
    out[1] = -(-(2.0 - q) * sm - s_minus(n1, n2, n3));
    out[2] = -(q - 4.0 * sp);
    out[3] = -(q + 2.0 * sp + 2.0 * SQRT3 * sm);
    out[4] = -(q + 2.0 * sp - 2.0 * SQRT3 * sm);
}

/// ★★ 튐 수열의 공용 코어 — RHS·사건함수·"가장 Kasner 다운 순간" 척도를 클로저로 받는다.
///
/// `wallness(y)` 는 벽 크기의 단조 대리량 (선형: max|N_i|, 로그: max w_i — exp 는
/// 단조라 argmin 이 같다).  `report_n(y)` 은 Bounce.max_n 에 넣을 값.
#[allow(clippy::too_many_arguments)]
fn bounce_core<F, G, W, R, O>(
    f_past: F,
    events: G,
    wallness: W,
    report_n: R,
    omega_of: O,
    y0: &[f64; 5],
    n_bounce: usize,
    tau_max: f64,
    rtol: f64,
    atol: f64,
    h0: f64,
    h_max: f64,
) -> Vec<Bounce>
where
    F: Fn(&[f64; 5], &mut [f64; 5]),
    G: Fn(&[f64; 5]) -> [f64; 3],
    W: Fn(&[f64; 5]) -> f64,
    R: Fn(&[f64; 5]) -> f64,
    O: Fn(&[f64; 5]) -> f64,
{
    let mut y = *y0;
    let mut t = 0.0f64;
    let mut h = h0;
    let mut out: Vec<Bounce> = Vec::new();
    let mut g = events(&y);
    // 에라 추적 (직전 튐 이후 벽 대리량이 최소인 지점)
    let mut best_n = f64::INFINITY;
    let mut best = (0.0f64, 0.0f64, 0.0f64, 0.0f64, 0.0f64); // (τ, Σ₊, Σ₋, 보고값, Ω)
    let mut k1 = [0.0f64; 5];
    f_past(&y, &mut k1);

    let mut m = wallness(&y);
    if m < best_n {
        best_n = m;
        best = (t, y[0], y[1], report_n(&y), omega_of(&y));
    }

    let mut nsteps = 0usize;
    while t < tau_max && out.len() < n_bounce && nsteps < 4_000_000 {
        nsteps += 1;
        if t + h > tau_max {
            h = tau_max - t;
        }
        let (yn, err, k7) = dp54_step(&f_past, &y, h, &k1);
        let sc = atol + rtol * y.iter().fold(0.0f64, |a, v| a.max(v.abs()));
        if !err.is_finite() || err > sc {
            h *= (0.9 * (sc / err.max(1e-300)).powf(0.2)).clamp(0.2, 1.0);
            if h < 1e-13 {
                break;
            }
            continue;
        }
        let gn = events(&yn);
        // ★ 사건: g_i 가 + → − (자라던 벽이 꺾인다).  가장 이른 근을 고른다.
        let mut hit: Option<(f64, usize)> = None;
        for i in 0..3 {
            if g[i] > 0.0 && gn[i] <= 0.0 {
                let (mut lo, mut hi) = (0.0f64, 1.0f64);
                for _ in 0..80 {
                    let mid = 0.5 * (lo + hi);
                    let ym = state_at(&f_past, &y, h, mid, &k1);
                    if events(&ym)[i] > 0.0 {
                        lo = mid;
                    } else {
                        hi = mid;
                    }
                    if hi - lo < 1e-15 {
                        break;
                    }
                }
                let s = 0.5 * (lo + hi);
                if hit.is_none() || s < hit.unwrap().0 {
                    hit = Some((s, i));
                }
            }
        }
        if let Some((s, i)) = hit {
            out.push(Bounce {
                tau: t + h * s,
                wall: i,
                u: kasner_u(best.1, best.2),
                tau_epoch: best.0,
                max_n: best.3,
                omega: best.4,
            });
            best_n = f64::INFINITY; // 다음 에라 추적 시작
        }
        // 스텝 확정
        t += h;
        y = yn;
        k1 = k7;
        g = gn;
        m = wallness(&y);
        if m < best_n {
            best_n = m;
            best = (t, y[0], y[1], report_n(&y), omega_of(&y));
        }
        h = (h * (0.9 * (sc / err.max(1e-300)).powf(0.2)).clamp(1.0, 5.0)).min(h_max);
    }
    out
}

/// ★★ 튐 수열 (선형 N 표현 — R4 원판).
#[allow(clippy::too_many_arguments)]
pub fn bounce_sequence(
    y0: &[f64; 5],
    gamma: f64,
    n_bounce: usize,
    tau_max: f64,
    rtol: f64,
    atol: f64,
    h0: f64,
) -> Vec<Bounce> {
    let chart = Chart::ClassA { gamma };
    bounce_core(
        move |y: &[f64; 5], out: &mut [f64; 5]| f_past(&chart, y, out),
        move |y: &[f64; 5]| event_fns(y, gamma),
        |y: &[f64; 5]| y[2].abs().max(y[3].abs()).max(y[4].abs()),
        |y: &[f64; 5]| y[2].abs().max(y[3].abs()).max(y[4].abs()),
        move |y: &[f64; 5]| aux_a(&y[..], gamma).2,
        y0,
        n_bounce,
        tau_max,
        rtol,
        atol,
        h0,
        f64::INFINITY,
    )
}

/// ★★ D3 · 튐 수열 (로그-벽 표현) — Bounce.max_n 은 **max w** (로그값) 다.
///
/// 언더플로가 없으므로 벽이 e^{-수천} 까지 죽어도 수열이 이어진다.  선형판과 겹치는
/// 구간에서는 u 가 일치해야 한다 (차등시험이 고정).
///
/// ★ **반증 기록 (h_max=1)**: 첫 판은 h 상한이 없어 3번째 튐 뒤 수열이 끊겼다.
///   순수 Kasner 구간에서 로그 RHS 는 **정확히 상수**라 DP54 오차가 0 — h 가
///   스텝마다 5배로 폭주해 거대 스텝 하나에 사건 쌍(+→−→+)이 통째로 들어가면
///   끝점 부호변화가 사라진다.  선형판은 지수적으로 변하는 N 이 오차제어로 h 를
///   묶어 **우연히** 안전했던 것 — 표현을 바꾸면 적분기의 보호막도 함께 사라진다.
#[allow(clippy::too_many_arguments)]
pub fn bounce_sequence_log(
    y0: &[f64; 5],
    signs: &[f64; 3],
    gamma: f64,
    n_bounce: usize,
    tau_max: f64,
    rtol: f64,
    atol: f64,
    h0: f64,
) -> Vec<Bounce> {
    let sg = *signs;
    bounce_core(
        move |y: &[f64; 5], out: &mut [f64; 5]| f_past_log(y, &sg, gamma, out),
        move |y: &[f64; 5]| {
            let (_n1, _n2, _n3, q) = aux_log(y, &sg, gamma);
            let (sp, sm) = (y[0], y[1]);
            [
                -(q - 4.0 * sp),
                -(q + 2.0 * sp + 2.0 * SQRT3 * sm),
                -(q + 2.0 * sp - 2.0 * SQRT3 * sm),
            ]
        },
        |y: &[f64; 5]| y[2].max(y[3]).max(y[4]), // max w (exp 는 단조)
        |y: &[f64; 5]| y[2].max(y[3]).max(y[4]),
        move |y: &[f64; 5]| {
            let (sp, sm) = (y[0], y[1]);
            let n1 = sg[0] * y[2].exp();
            let n2 = sg[1] * y[3].exp();
            let n3 = sg[2] * y[4].exp();
            let k =
                K_COEFF_WE * (n1 * n1 + n2 * n2 + n3 * n3 - 2.0 * (n1 * n2 + n2 * n3 + n3 * n1));
            1.0 - sp * sp - sm * sm - k
        },
        y0,
        n_bounce,
        tau_max,
        rtol,
        atol,
        h0,
        1.0,
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    fn kasner_state(u: f64, seed: [f64; 3]) -> [f64; 5] {
        // p (정렬) → Σ, 그리고 진공면(Ω=0)으로 사영
        let s = 1.0 + u + u * u;
        let p = [-u / s, (1.0 + u) / s, u * (1.0 + u) / s];
        let sig = [3.0 * p[0] - 1.0, 3.0 * p[1] - 1.0, 3.0 * p[2] - 1.0];
        let (mut sp, mut sm) = (-sig[0] / 2.0, (sig[1] - sig[2]) / (2.0 * SQRT3));
        let k = crate::ode::charts::curvature_k_a(seed[0], seed[1], seed[2]);
        let f = ((1.0 - k) / (sp * sp + sm * sm)).sqrt();
        sp *= f;
        sm *= f;
        [sp, sm, seed[0], seed[1], seed[2]]
    }

    #[test]
    fn kasner_u_round_trips() {
        for u in [1.3f64, 2.4, 3.7, 9.0] {
            let y = kasner_state(u, [0.0, 0.0, 0.0]);
            assert!((kasner_u(y[0], y[1]) - u).abs() < 1e-12, "{u}");
        }
    }

    #[test]
    fn no_wall_no_bounce() {
        let y = kasner_state(3.7, [0.0, 0.0, 0.0]);
        assert!(bounce_sequence(&y, 2.0, 4, 40.0, 1e-11, 1e-13, 1e-3).is_empty());
    }

    #[test]
    fn one_wall_bounces_once() {
        let y = kasner_state(3.7, [1e-3, 0.0, 0.0]);
        let b = bounce_sequence(&y, 2.0, 4, 40.0, 1e-11, 1e-13, 1e-3);
        assert_eq!(b.len(), 1, "{b:?}");
    }

    #[test]
    fn log_walls_agree_with_linear_where_both_are_valid() {
        // D3 · 같은 초기자료 (w = ln N), 겹치는 구간에서 u 가 일치해야 한다.
        // τ 는 적분기 민감량이라 1e-3, u 는 둔감량이라 1e-4 (D1b §4 의 위계 그대로).
        let y = kasner_state(3.7, [1e-3, 1e-3, 1e-3]);
        let b_lin = bounce_sequence(&y, 2.0, 4, 90.0, 1e-11, 1e-13, 1e-3);
        let ylog = [y[0], y[1], y[2].ln(), y[3].ln(), y[4].ln()];
        let b_log = bounce_sequence_log(&ylog, &[1.0, 1.0, 1.0], 2.0, 4, 90.0, 1e-11, 1e-13, 1e-3);
        assert!(
            b_log.len() >= b_lin.len(),
            "{} {}",
            b_log.len(),
            b_lin.len()
        );
        for (a, b) in b_lin.iter().zip(b_log.iter()) {
            assert!((a.u - b.u).abs() < 1e-4, "{} {}", a.u, b.u);
            assert!((a.tau - b.tau).abs() < 1e-3, "{} {}", a.tau, b.tau);
        }
    }

    #[test]
    fn log_walls_survive_far_past_the_underflow_floor() {
        // 무리수 궤도 (x = 1/√2, digit 주기 [1,2,2,…]) — 유리수 CF 종결 함정 회피
        // (첫 판은 u₀=2.7 을 썼다가 0.7 = 7/10 의 CF 가 **종결**해 u→1 메가에라에
        //  빠졌다 — D1c 에서 이미 밟은 함정을 여기서 또 밟을 뻔했다).
        // 측정: 8000τ 에 8튐, 골 깊이 w = −2197 — 선형 한계(ln 1e−308 ≈ −709)의 3배.
        // 튐이 더 안 나오는 건 결함이 아니라 **물리**다: 골이 에라마다 ×~3.2 로
        // 깊어져 회복 τ 가 기하급수로 늘어난다 (튐 수 ~ O(ln τ_budget)).
        let u0 = 2.0 + std::f64::consts::FRAC_1_SQRT_2;
        let y = kasner_state(u0, [1e-3, 1e-3, 1e-3]);
        let ylog = [y[0], y[1], y[2].ln(), y[3].ln(), y[4].ln()];
        let b = bounce_sequence_log(&ylog, &[1.0, 1.0, 1.0], 2.0, 10, 8000.0, 1e-11, 1e-13, 1e-3);
        assert!(b.len() >= 7, "{}", b.len());
        let deepest = b.iter().fold(0.0f64, |a, x| a.min(x.max_n));
        assert!(deepest < -700.0, "{deepest}");
        // 도입 두 에폭(2.7071, 1.7071) 뒤로는 주기점 {√2+1, √2} 근처에 끝까지 머문다
        for x in b.iter().skip(2) {
            assert!(
                (x.u - (1.0 + 2f64.sqrt())).abs() < 0.01 || (x.u - 2f64.sqrt()).abs() < 0.01,
                "{}",
                x.u
            );
        }
    }

    #[test]
    fn mixmaster_follows_the_bkl_map() {
        let y = kasner_state(3.7, [1e-3, 1e-3, 1e-3]);
        let b = bounce_sequence(&y, 2.0, 4, 90.0, 1e-11, 1e-13, 1e-3);
        assert!(b.len() >= 4, "{b:?}");
        let us: Vec<f64> = b.iter().map(|x| x.u).collect();
        for w in us.windows(2).take(2) {
            assert!((w[1] - (w[0] - 1.0)).abs() < 1e-4, "{us:?}");
        }
        // u < 2 에서 재주입 1/(u−1)
        let k = us.len() - 1;
        assert!((us[k] - 1.0 / (us[k - 1] - 1.0)).abs() < 1e-4, "{us:?}");
    }
}
