//! B1 · Fermi-Dirac 적분 (질량 중성미자의 ρ, p).
//!
//! Python `matter.neutrino` 미러 (무차원, 종별 온도 단위, y = m/T):
//!     ρ(y) = ∫₀^∞ x² √(x²+y²) f(x) dx
//!     p(y) = (1/3) ∫₀^∞ x⁴/√(x²+y²) f(x) dx        f(x) = 1/(eˣ+1)
//!
//! 적분법: **Gauss-Legendre** (구간분할).  피적분함수는 e^{-x} 감쇠의 매끄러운 함수라
//! GL 이 평가횟수당 정확도가 압도적이다 — 합성 심프슨은 h⁴ 오차라 N=4000 에서도
//! ~3e-9 에 그치는 반면, GL-64 두 구간(총 128 평가)으로 ~1e-15 에 도달한다.
//! 노드는 Newton 반복으로 1회 생성 후 캐시한다 (해석 적분값으로 검증).
//! X_MAX=60 에서 f ~ e^{-60} ≈ 1e-26 이라 절단오차는 무시된다.

use std::sync::OnceLock;

/// 적분 상한.  f(x) ~ e^{-x} 이므로 60 이면 절단 잔차 ~1e-26.
const X_MAX: f64 = 60.0;
/// 구간 경계 — 피적분함수가 x≲10 에 몰려 있어 앞구간을 촘촘히 본다.
const X_SPLIT: f64 = 12.0;
/// 구간당 Gauss-Legendre 차수.
const GL_N: usize = 64;

#[inline]
fn fermi_dirac(x: f64) -> f64 {
    // x 가 크면 exp 오버플로 방지 (Python 의 min(x,700) 과 동일 취지)
    1.0 / (x.min(700.0).exp() + 1.0)
}

/// [-1,1] 위 Gauss-Legendre 노드·가중치 (Newton 반복, Legendre 점화식).
pub fn gauss_legendre_nodes(n: usize) -> (Vec<f64>, Vec<f64>) {
    let mut x = vec![0.0; n];
    let mut w = vec![0.0; n];
    let m = (n + 1) / 2;
    for i in 0..m {
        // Chebyshev 초기추정 후 Newton
        let mut z = (std::f64::consts::PI * (i as f64 + 0.75) / (n as f64 + 0.5)).cos();
        let mut pp = 0.0;
        for _ in 0..100 {
            let (mut p0, mut p1) = (1.0f64, 0.0f64);
            for j in 0..n {
                let p2 = p1;
                p1 = p0;
                let jj = j as f64;
                p0 = ((2.0 * jj + 1.0) * z * p1 - jj * p2) / (jj + 1.0);
            }
            pp = n as f64 * (z * p0 - p1) / (z * z - 1.0);
            let dz = p0 / pp;
            z -= dz;
            if dz.abs() < 1e-15 {
                break;
            }
        }
        x[i] = -z;
        x[n - 1 - i] = z;
        let wi = 2.0 / ((1.0 - z * z) * pp * pp);
        w[i] = wi;
        w[n - 1 - i] = wi;
    }
    (x, w)
}

fn gl_cached() -> &'static (Vec<f64>, Vec<f64>) {
    static GL: OnceLock<(Vec<f64>, Vec<f64>)> = OnceLock::new();
    GL.get_or_init(|| gauss_legendre_nodes(GL_N))
}

/// [a,b] 에서 Gauss-Legendre 적분.
#[inline]
fn gl_interval<F: Fn(f64) -> f64>(g: &F, a: f64, b: f64) -> f64 {
    let (xs, ws) = gl_cached();
    let c = 0.5 * (b - a);
    let d = 0.5 * (b + a);
    let mut s = 0.0;
    for k in 0..GL_N {
        s += ws[k] * g(c * xs[k] + d);
    }
    s * c
}

/// ∫₀^{X_MAX} g dx  — [0,X_SPLIT] + [X_SPLIT,X_MAX] 두 구간.
#[inline]
fn integrate<F: Fn(f64) -> f64>(g: F) -> f64 {
    gl_interval(&g, 0.0, X_SPLIT) + gl_interval(&g, X_SPLIT, X_MAX)
}

/// ρ 적분:  ∫ x² √(x²+y²) f dx   (무차원)
pub fn rho_integral(y: f64) -> f64 {
    let y2 = y * y;
    integrate(|x| x * x * (x * x + y2).sqrt() * fermi_dirac(x))
}

/// p 적분:  (1/3) ∫ x⁴/√(x²+y²) f dx   (무차원)
pub fn p_integral(y: f64) -> f64 {
    let y2 = y * y;
    integrate(|x| {
        let r = (x * x + y2).sqrt();
        if r == 0.0 {
            0.0
        } else {
            x * x * x * x / (3.0 * r) * fermi_dirac(x)
        }
    })
}

/// 수밀도 적분:  ∫ x² f dx  (무질량 기준값 3ζ(3)/2 형)
pub fn n_integral() -> f64 {
    integrate(|x| x * x * fermi_dirac(x))
}

/// 등방 배경의 (ρ, p, w) — Python `neutrino_rho_p` 미러.
///
/// `a` 는 스케일인자(오늘=1), `y0 = m/T_ν0`.  T_ν ∝ 1/a 이므로 y = y0·a,
/// ρ ∝ a⁻⁴ ∫(y).  반환은 오늘의 무질량 ρ 적분값 대비 무차원.
pub fn neutrino_rho_p(a: f64, y0: f64, n_species: f64) -> (f64, f64, f64) {
    let y = y0 * a;
    let a4 = a * a * a * a;
    let rho = n_species * rho_integral(y) / a4;
    let p = n_species * p_integral(y) / a4;
    let w = if rho != 0.0 { p / rho } else { 0.0 };
    (rho, p, w)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn massless_limit_w_is_one_third() {
        let (rho, p, w) = neutrino_rho_p(1.0, 0.0, 1.0);
        assert!(rho > 0.0 && p > 0.0);
        assert!((w - 1.0 / 3.0).abs() < 1e-10, "w={w}");
    }

    #[test]
    fn nonrelativistic_limit_w_to_zero() {
        // y = m/T = 50 이면 비상대론적: w → 0
        let (_, _, w) = neutrino_rho_p(1.0, 50.0, 1.0);
        assert!(w < 0.02, "w={w}");
    }

    #[test]
    fn massless_rho_matches_analytic() {
        // ∫ x²·x·f dx = ∫ x³/(eˣ+1) dx = 7π⁴/120
        let exact = 7.0 * std::f64::consts::PI.powi(4) / 120.0;
        assert!((rho_integral(0.0) - exact).abs() / exact < 1e-12);
    }

    #[test]
    fn n_integral_matches_analytic() {
        // ∫ x²/(eˣ+1) dx = (3/2) ζ(3) = 1.803085…
        let exact = 1.5 * 1.202_056_903_159_594;
        assert!((n_integral() - exact).abs() / exact < 1e-12);
    }
}
