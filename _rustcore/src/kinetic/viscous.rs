//! H4-Rust · imperfect fluid **유도** — Eckart/Israel-Stewart 가 계층 절단의 귀결.
//!
//! Python 오라클: `bianchi.matter.viscous_derived`.
//!
//! ★ 두 경로를 Rust 쪽에서도 **분리**해 구현하고 교차검증한다:
//!   - **경로 A (freestream 구적)**: `quad::moments` 의 유한차분으로 dπ_ab/dt 를 얻는다.
//!     계층 수식을 **전혀 쓰지 않는다**.
//!   - **경로 B (PSTF 계층)**: `hierarchy::rhs_one` 의 l=2,i=0 방정식을 평가한다.
//!     `route_b_damping_handset` 은 구적을 **전혀 쓰지 않는다** (상태 손세팅).
//!
//! 유도값 (무질량 무충돌):
//! ```text
//! σ=0 →  π̇_ab = −4H π_ab            ⇒  1/τ_π = 4H
//! π=0 →  π̇_ab = −(8/15) ρ σ_ab       ⇒  2η/τ_π = (8/15)ρ
//! ⇒  τ_π = 1/(4H),   η = ρ/(15H)          (자유 파라미터 없음)
//! ```
//! ★ σ=0 이면 (A),(B),(C) 항군이 모두 σ 에 비례하므로 l=2 방정식이 **절단 없이** 닫힌다.
//! ★ 유질량은 J^(1)_ab ≠ π_ab 이므로 감쇠가 빨라지고 **성분마다 다르다** (τ_π 가 스칼라
//!   아님).  평균과 이방성을 함께 반환한다 — 정직한 한계 노출.

use crate::kinetic::hierarchy::{rhs_one, State};
use crate::kinetic::pstf;
use crate::kinetic::quad;

/// 무질량 무충돌 유도값 — 두 경로가 모두 재생산해야 한다.
#[cfg(test)]
pub const MASSLESS_DAMPING_RATE: f64 = 4.0; // 1/τ_π  (H 단위)
#[cfg(test)]
pub const MASSLESS_SOURCE_COEFF: f64 = -8.0 / 15.0; // dπ/dt = coeff·ρσ

/// 감쇠 측정 결과 — (성분별, 평균, 이방성).
#[derive(Clone, Copy, Debug)]
pub struct Damping {
    pub per_component: [f64; 3],
    pub mean: f64,
    pub anisotropy: f64,
}

impl Damping {
    fn from(rate: [f64; 3]) -> Self {
        let mean = (rate[0] + rate[1] + rate[2]) / 3.0;
        let mx = rate.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
        let mn = rate.iter().cloned().fold(f64::INFINITY, f64::min);
        Damping {
            per_component: rate,
            mean,
            anisotropy: mx - mn,
        }
    }
}

// ════════════════════════════════════════════ 경로 A — freestream (정확 구적)
/// σ=0 등방팽창에서 (dπ_ab/dt)/π_ab 를 **정확 구적의 중앙차분**으로 측정.
/// 계층 수식을 쓰지 않는다.  σ=0 이므로 ȧ_i = H a_i (모든 축이 같은 비율).
pub fn route_a_damping(mass: f64, a_vec: &[f64; 3], h: f64, dt: f64) -> Damping {
    let ap = [
        a_vec[0] * (1.0 + h * dt),
        a_vec[1] * (1.0 + h * dt),
        a_vec[2] * (1.0 + h * dt),
    ];
    let am = [
        a_vec[0] * (1.0 - h * dt),
        a_vec[1] * (1.0 - h * dt),
        a_vec[2] * (1.0 - h * dt),
    ];
    let pi_p = quad::moments(&ap, mass).2;
    let pi_m = quad::moments(&am, mass).2;
    let pi_0 = quad::moments(a_vec, mass).2;
    let mut rate = [0.0f64; 3];
    for k in 0..3 {
        let d = (pi_p[k * 3 + k] - pi_m[k * 3 + k]) / (2.0 * dt);
        rate[k] = d / pi_0[k * 3 + k];
    }
    Damping::from(rate)
}

/// π≈0 에서 σ 를 켤 때의 급작응답 계수 (dπ/dt = coeff·ρσ) — 정확 구적.
/// Python `freestream.sudden_response_coefficient`: 부피보존 변형 δ(ln a) = (2δ, −δ, −δ).
pub fn route_a_source(mass: f64, delta: f64) -> f64 {
    let lna = [2.0 * delta, -delta, -delta];
    let a = [lna[0].exp(), lna[1].exp(), lna[2].exp()];
    let (rho, _, pi) = quad::moments(&a, mass);
    pi[0] / (rho * lna[0])
}

// ════════════════════════════════════════════ 경로 B — PSTF 계층
/// σ=0 에서 l=2 방정식의 감쇠율 — **방정식만** 평가 (미분 없음).
///
/// σ=0 이면 (A),(B),(C) 가 사라져 π̇_ab = −H[5π_ab − J^(1)_ab] 로 정확히 닫힌다.
/// a_vec 이 등방이면 π_ab ≡ 0 이라 0/0 → `None` (조용히 넘기지 않는다).
pub fn route_b_damping(mass: f64, a_vec: &[f64; 3], h: f64) -> Option<Damping> {
    if (a_vec[0] - a_vec[1]).abs() < 1e-12 && (a_vec[1] - a_vec[2]).abs() < 1e-12 {
        return None; // 등방 a_vec: π_ab ≡ 0 이라 감쇠율 정의 불가
    }
    let s = State::from_quadrature(a_vec, mass, 4, 2, 0.0, 2);
    let pi0 = s.j[2][0].clone();
    let dpi = rhs_one(&s, h, &[0.0; 9], 2, 0);
    let mut rate = [0.0f64; 3];
    for k in 0..3 {
        rate[k] = dpi[k * 3 + k] / pi0[k * 3 + k];
    }
    Some(Damping::from(rate))
}

/// 무질량 전용 — J^(i)_ab 를 **손으로** 세팅해 구적을 전혀 쓰지 않는 가장 순수한 경로 B.
/// 무질량은 J^(i) 가 i-무관이므로 J^(i)_ab = π_ab ⇒ π̇ = −H[5π − π] = −4Hπ 가 **정확**.
pub fn route_b_damping_handset(h: f64, pi_diag: &[f64; 3]) -> Damping {
    let tr = (pi_diag[0] + pi_diag[1] + pi_diag[2]) / 3.0;
    let pd = [pi_diag[0] - tr, pi_diag[1] - tr, pi_diag[2] - tr];
    let mut pi0 = [0.0f64; 9];
    for k in 0..3 {
        pi0[k * 3 + k] = pd[k];
    }
    let mut s = State::zeros(4, 2);
    for i in 0..s.j[0].len() {
        s.j[0][i] = vec![1.0];
    }
    for i in 0..s.j[2].len() {
        s.j[2][i] = pi0.to_vec();
    }
    let dpi = rhs_one(&s, h, &[0.0; 9], 2, 0);
    let mut rate = [0.0f64; 3];
    for k in 0..3 {
        rate[k] = dpi[k * 3 + k] / pi0[k * 3 + k];
    }
    Damping::from(rate)
}

/// π=0, σ≠0 상태에서 l=2 방정식의 σ-소스 계수 (dπ/dt / (ρσ)) — 계층만 사용.
pub fn route_b_source(mass: f64, a_vec: &[f64; 3], h: f64, sigma_diag: &[f64; 3]) -> f64 {
    let sigma = [
        sigma_diag[0],
        0.0,
        0.0,
        0.0,
        sigma_diag[1],
        0.0,
        0.0,
        0.0,
        sigma_diag[2],
    ];
    let mut s = State::from_quadrature(a_vec, mass, 4, 2, 0.0, 2);
    let rho = s.j[0][0][0];
    for l in 1..=s.l_max {
        for i in 0..s.j[l].len() {
            s.j[l][i] = vec![0.0; pstf::dim(l)];
        }
    }
    let src = rhs_one(&s, h, &sigma, 2, 0);
    let mut acc = 0.0;
    for k in 0..3 {
        acc += src[k * 3 + k] / sigma_diag[k];
    }
    acc / 3.0 / rho
}

// ════════════════════════════════════════════ 유도된 수송계수
#[derive(Clone, Copy, Debug)]
pub struct Transport {
    pub eta: f64,
    pub tau_pi: f64,
    pub rho: f64,
    pub damping_rate: f64,
    pub source_coeff: f64,
    pub eta_over_rho_h: f64,
}

/// (η, τ_π) 를 **유도** — 자유 파라미터 없음.
/// `hierarchy=true` → 경로 B, `false` → 경로 A.  무질량 기대: τ_π=1/(4H), η=ρ/(15H).
pub fn transport_coefficients(
    mass: f64,
    a_vec: &[f64; 3],
    h: f64,
    hierarchy_route: bool,
) -> Option<Transport> {
    let rho = quad::j_moment(a_vec, mass, 0, 0, 0.0, 2)[0];
    let (damp, src) = if hierarchy_route {
        (
            route_b_damping(mass, a_vec, h)?.mean,
            route_b_source(mass, &[1.0, 1.0, 1.0], h, &[0.05, -0.02, -0.03]),
        )
    } else {
        (
            route_a_damping(mass, a_vec, h, 1e-5).mean,
            route_a_source(mass, 0.002),
        )
    };
    let tau_pi = -1.0 / damp;
    let eta = -src * rho * tau_pi / 2.0;
    Some(Transport {
        eta,
        tau_pi,
        rho,
        damping_rate: damp,
        source_coeff: src,
        eta_over_rho_h: eta * h / rho,
    })
}

/// Eckart 준정적 극한 η (유도값): 0 = −4Hπ − (8/15)ρσ ⇒ π = −2ησ ⇒ η = ρ/(15H).
#[inline]
pub fn eckart_eta_from_hierarchy(rho: f64, h: f64) -> f64 {
    rho / (15.0 * h)
}

/// 무질량 무충돌 IS 완화시간 (유도값) τ_π = 1/(4H).
#[inline]
pub fn relaxation_time_massless(h: f64) -> f64 {
    1.0 / (4.0 * h)
}

/// ★ 두 경로 교차검증 — (감쇠 상대차, 소스 상대차, 일치 여부).
/// Python 측정: 감쇠 ~1e−9 (σ=0 에서 방정식이 정확), 소스 ~1.5e−3 (구적 급작응답 차분 한계).
pub fn cross_validate(
    mass: f64,
    a_vec: &[f64; 3],
    h: f64,
    tol_damp: f64,
    tol_src: f64,
) -> Option<(f64, f64, bool)> {
    let a_damp = route_a_damping(mass, a_vec, h, 1e-5).mean;
    let b_damp = route_b_damping(mass, a_vec, h)?.mean;
    let a_src = route_a_source(mass, 0.002);
    let b_src = route_b_source(mass, &[1.0, 1.0, 1.0], h, &[0.05, -0.02, -0.03]);
    let d_rel = (a_damp - b_damp).abs() / b_damp.abs();
    let s_rel = (a_src - b_src).abs() / b_src.abs();
    Some((d_rel, s_rel, d_rel < tol_damp && s_rel < tol_src))
}

#[cfg(test)]
mod tests {
    use super::*;

    const A: [f64; 3] = [1.0, 0.85, 1.18];

    #[test]
    fn route_a_massless_damping_is_minus_four() {
        let r = route_a_damping(0.0, &A, 1.0, 1e-5);
        assert!((r.mean + MASSLESS_DAMPING_RATE).abs() < 1e-6, "{r:?}");
        assert!(r.anisotropy < 1e-6, "{r:?}");
    }

    #[test]
    fn route_a_source_is_minus_eight_fifteenths() {
        let c = route_a_source(0.0, 0.002);
        assert!((c - MASSLESS_SOURCE_COEFF).abs() < 5e-3, "{c}");
    }

    #[test]
    fn route_b_handset_is_exactly_minus_four() {
        let r = route_b_damping_handset(1.0, &[0.1, -0.04, -0.06]);
        assert!((r.mean + MASSLESS_DAMPING_RATE).abs() < 1e-12, "{r:?}");
    }

    #[test]
    fn route_b_source_is_exactly_minus_eight_fifteenths() {
        let c = route_b_source(0.0, &[1.0, 1.0, 1.0], 1.0, &[0.05, -0.02, -0.03]);
        assert!((c - MASSLESS_SOURCE_COEFF).abs() < 1e-12, "{c}");
    }

    #[test]
    fn route_b_rejects_isotropic_a_vec() {
        assert!(route_b_damping(0.0, &[1.0, 1.0, 1.0], 1.0).is_none());
    }

    #[test]
    fn two_routes_agree() {
        for mass in [0.0, 0.5, 1.0, 4.0] {
            let (d, s, ok) = cross_validate(mass, &A, 1.0, 2e-3, 5e-3).unwrap();
            assert!(ok, "mass={mass} damp={d:e} src={s:e}");
            assert!(d < 1e-6, "mass={mass} damp rel {d:e}");
        }
    }

    #[test]
    fn derived_tau_pi_and_eta() {
        for hier in [true, false] {
            let t = transport_coefficients(0.0, &A, 1.0, hier).unwrap();
            assert!((t.tau_pi - 0.25).abs() < 1e-6, "{t:?}");
            assert!((t.eta_over_rho_h - 1.0 / 15.0).abs() < 5e-4, "{t:?}");
            assert!(t.eta > 0.0, "산일적이어야 한다 (2법칙)");
        }
    }

    #[test]
    fn mass_increases_damping() {
        let r0 = route_a_damping(0.0, &A, 1.0, 1e-5).mean;
        for mass in [0.5, 1.0, 4.0] {
            let rm = route_a_damping(mass, &A, 1.0, 1e-5).mean;
            assert!(rm < r0, "mass={mass} {rm} !< {r0}");
            assert!(rm.abs() > 4.0);
        }
    }

    #[test]
    fn massive_damping_is_anisotropic() {
        assert!(route_a_damping(4.0, &A, 1.0, 1e-5).anisotropy > 1e-3);
    }

    #[test]
    fn eckart_limit_matches() {
        let t = transport_coefficients(0.0, &A, 1.5, true).unwrap();
        let e = eckart_eta_from_hierarchy(t.rho, 1.5);
        assert!(((e - t.eta) / t.rho).abs() < 1e-6);
    }

    #[test]
    fn relaxation_time_helper() {
        assert!((relaxation_time_massless(2.0) - 0.125).abs() < 1e-15);
    }
}
