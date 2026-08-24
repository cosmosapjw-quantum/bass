//! H3-Rust · Thomson 충돌항 — 무충돌 계층을 진짜 Boltzmann 계층으로.
//!
//! Python 오라클: `bianchi.matter.collision`.
//!
//! ★ **두 경로를 Rust 쪽에서도 분리해 구현**한다 (H4 와 나누는 방식이 다르다):
//!   - 경로 A (`eigenvalue_numeric`): Thomson 위상함수 K̃(μ)=(3/8)(1+μ²) 를 Gauss-Legendre
//!     격자에서 **직접 적분**해 λ_l 을 측정.  다극 대수를 쓰지 않는다.
//!   - 경로 B (`eigenvalue`): Legendre 전개 1+μ² = 4/3 + (2/3)P₂ 에서
//!     λ_l = 4π k_l/(2l+1) 을 **해석적으로** 준다.  적분을 하지 않는다.
//!
//! ★ 정직한 한계: `quad.rs` 정확 구적 오라클은 충돌항을 **검증할 수 없다** — 충돌이
//!   자유흐름 특성곡선(불변기저 p_i = const)을 깨뜨려 구적의 정확성 근거가 사라진다.
//!   그래서 두 경로가 λ₂ = 1/10 (감쇠 **9/10**) 을 독립 재생산하는 것이 유일한 교차검증이다.
//!
//! 물리: 비편광 Thomson 산란은 전자 정지틀에서 탄성이라 광자 **에너지를 바꾸지 않고**
//!   각분포만 등방화한다 ⇒ 충돌항은 (l,i) 중 **l 에만** 의존한다.
//!
//! ```text
//! C[J^(i)_{A_l}] = -(n_e σ_T)(1 - λ_l) J^(i)_{A_l}
//! λ_0 = 1 (수 보존), λ_1 = 0, λ_2 = 1/10 (감쇠 9/10), λ_{l≥3} = 0
//! ```

use crate::kinetic::hierarchy::{rhs_one, State};
use crate::kinetic::pstf;
use crate::thermo::fd::gauss_legendre_nodes;

/// 경로 A 기본 절점수 (Python `thomson_eigenvalue_numeric` 의 n_nodes 기본값과 동일).
pub const N_NODES_DEFAULT: usize = 200;

/// Legendre P_l(x) — 3항 점화 (l+1)P_{l+1} = (2l+1)x P_l − l P_{l−1}.
///
/// ★ 왜 점화인가: 경로 A 는 "다극 대수를 쓰지 않는다"는 것이 요점이므로 λ_l 을
///   해석 상수로 하드코딩하지 않고 위상함수와 P_l 의 적분으로 **측정**해야 한다.
#[inline]
pub fn legendre(l: usize, x: f64) -> f64 {
    if l == 0 {
        return 1.0;
    }
    if l == 1 {
        return x;
    }
    let mut pm = 1.0;
    let mut p = x;
    for k in 1..l {
        let kf = k as f64;
        let nxt = ((2.0 * kf + 1.0) * x * p - kf * pm) / (kf + 1.0);
        pm = p;
        p = nxt;
    }
    p
}

// ════════════════════════════════════════════ 경로 A — 수치 위상함수
/// λ_l = ∫_{-1}^{1} dμ K̃(μ) P_l(μ),  K̃(μ) = (3/8)(1+μ²).  ∫K̃ dμ = 1 (수 보존).
pub fn eigenvalue_numeric(l: usize, n_nodes: usize) -> f64 {
    let (x, w) = gauss_legendre_nodes(n_nodes);
    let mut acc = 0.0;
    for k in 0..n_nodes {
        let mu = x[k];
        acc += w[k] * (3.0 / 8.0) * (1.0 + mu * mu) * legendre(l, mu);
    }
    acc
}

/// 감쇠계수 (1 − λ_l) — 경로 A.
pub fn damping_numeric(l: usize, n_nodes: usize) -> f64 {
    1.0 - eigenvalue_numeric(l, n_nodes)
}

// ════════════════════════════════════════════ 경로 B — 해석 다극
/// λ_l = 4π k_l/(2l+1).  K(μ) = (3/16π)(1+μ²) = (1/4π)[P₀ + ½P₂] ⇒ k₀=1/4π, k₂=1/8π.
#[inline]
pub fn eigenvalue(l: usize) -> f64 {
    match l {
        0 => 1.0,
        2 => 0.1,
        _ => 0.0,
    }
}

/// 감쇠계수 (1 − λ_l) — 경로 B.  l=0: 0, l=2: **9/10**, 나머지: 1.
#[inline]
pub fn damping(l: usize) -> f64 {
    1.0 - eigenvalue(l)
}

/// 경로 선택자 — 차등테스트에서 두 경로가 같은 충돌항을 주는지 확인하기 위해 노출.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Route {
    /// 경로 B (해석 다극).
    Analytic,
    /// 경로 A (수치 위상함수 적분).
    Numeric,
}

#[inline]
pub fn damping_route(l: usize, route: Route) -> f64 {
    match route {
        Route::Analytic => damping(l),
        Route::Numeric => damping_numeric(l, N_NODES_DEFAULT),
    }
}

// ════════════════════════════════════════════ 계층에 충돌항 붙이기
/// C[J^(i)_{A_l}] = −(n_e σ_T)(1 − λ_l) J^(i)_{A_l}.  i(속도가중)에 **무관** (탄성).
pub fn collision_term(s: &State, l: usize, i: i32, n_e_sigma_t: f64, route: Route) -> Vec<f64> {
    let d = pstf::dim(l);
    let c = -n_e_sigma_t * damping_route(l, route);
    let j = &s.j[l][i as usize];
    (0..d).map(|k| c * j[k]).collect()
}

/// 무충돌 RHS + Thomson 충돌항.  n_e_sigma_t = 0 이면 H1/H2 와 **비트 단위로** 일치.
pub fn rhs_one_collisional(
    s: &State,
    h: f64,
    sigma: &[f64; 9],
    l: usize,
    i: i32,
    n_e_sigma_t: f64,
    route: Route,
) -> Vec<f64> {
    let mut out = rhs_one(s, h, sigma, l, i);
    if n_e_sigma_t == 0.0 {
        return out;
    }
    let c = -n_e_sigma_t * damping_route(l, route);
    let j = &s.j[l][i as usize];
    for k in 0..out.len() {
        out[k] += c * j[k];
    }
    out
}

/// 격자 전체 충돌 RHS (닫힘 적용).  Rayon 으로 (l,i) 병렬.
pub fn rhs_state_collisional(
    s: &State,
    h: f64,
    sigma: &[f64; 9],
    n_e_sigma_t: f64,
    route: Route,
) -> Vec<Vec<Vec<f64>>> {
    use rayon::prelude::*;
    let mut sc = s.clone();
    sc.close_i();
    (0..=s.l_max)
        .into_par_iter()
        .map(|l| {
            (0..=s.i_max)
                .map(|i| rhs_one_collisional(&sc, h, sigma, l, i as i32, n_e_sigma_t, route))
                .collect()
        })
        .collect()
}

/// 충돌 계층 RK4 적분.  반환 (t, ρ, p, π_ab) 이력 — 무충돌 `hierarchy::integrate` 와 같은 형태.
///
/// ★ 강성(stiffness) 주의: n_e σ_T ≫ H 이면 l≥1 이 1/(n_eσ_T) 시간척도로 감쇠하므로
///   RK4 안정영역은 dt ≲ 2.8/(n_eσ_T) 다.  `stiffness_ratio` 로 진단값을 반환한다.
#[allow(clippy::too_many_arguments)]
pub fn integrate_collisional(
    a0: &[f64; 3],
    mass: f64,
    h: f64,
    sigma_diag: &[f64; 3],
    n_e_sigma_t: f64,
    t_end: f64,
    nsteps: usize,
    l_max: usize,
    i_max: usize,
    dipole_eps: f64,
    route: Route,
) -> (Vec<f64>, Vec<f64>, Vec<f64>, Vec<[f64; 9]>) {
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
    let mut s = State::from_quadrature(a0, mass, l_max, i_max, dipole_eps, 2);
    let dt = t_end / nsteps as f64;
    let (mut ts, mut rhos, mut ps, mut pis) = (vec![], vec![], vec![], vec![]);

    let axpy = |base: &State, d: &Vec<Vec<Vec<f64>>>, c: f64| -> State {
        let mut o = base.clone();
        for l in 0..=base.l_max {
            for i in 0..=base.i_max {
                for k in 0..o.j[l][i].len() {
                    o.j[l][i][k] = base.j[l][i][k] + c * d[l][i][k];
                }
            }
        }
        o
    };

    for step in 0..=nsteps {
        ts.push(step as f64 * dt);
        rhos.push(s.j[0][0][0]);
        ps.push(s.j[0][1][0] / 3.0);
        let mut pi = [0.0f64; 9];
        if l_max >= 2 {
            pi.copy_from_slice(&s.j[2][0]);
        }
        pis.push(pi);
        if step == nsteps {
            break;
        }
        let k1 = rhs_state_collisional(&s, h, &sigma, n_e_sigma_t, route);
        let k2 = rhs_state_collisional(&axpy(&s, &k1, 0.5 * dt), h, &sigma, n_e_sigma_t, route);
        let k3 = rhs_state_collisional(&axpy(&s, &k2, 0.5 * dt), h, &sigma, n_e_sigma_t, route);
        let k4 = rhs_state_collisional(&axpy(&s, &k3, dt), h, &sigma, n_e_sigma_t, route);
        for l in 0..=l_max {
            for i in 0..=i_max {
                for k in 0..s.j[l][i].len() {
                    s.j[l][i][k] += dt / 6.0
                        * (k1[l][i][k] + 2.0 * k2[l][i][k] + 2.0 * k3[l][i][k] + k4[l][i][k]);
                }
            }
        }
    }
    (ts, rhos, ps, pis)
}

/// RK4 안정성 진단:  (n_eσ_T·dt·(1−λ₂), 안정 여부).  2.785 는 RK4 실축 안정한계.
pub fn stiffness_ratio(n_e_sigma_t: f64, dt: f64) -> (f64, bool) {
    let r = n_e_sigma_t * dt * damping(2);
    (r, r < 2.785)
}

// ════════════════════════════════════════════ 유도: Thomson 점성
/// 긴밀결합 극한의 광자 전단점성.  반환 (η, τ_π, 감쇠율, η·n_eσ_T/ρ).
///
/// ```text
/// 1/τ_π = 4H + (1−λ₂) n_e σ_T,      2η/τ_π = (8/15)ρ  ⇒  η = (4/15)ρ τ_π
/// n_eσ_T ≫ H:  9/10 포함 → η = (8/27)ρ/(n_eσ_T),   미포함 → (4/15)ρ/(n_eσ_T)
/// ```
/// ★ 정직한 주석: 문헌 통용값은 (4/15)ρ/(n_eσ_T) 이고 우리 계층에 Thomson 사중극
///   9/10 을 넣으면 (8/27) 이다.  비가 정확히 10/9 — **차이의 전부가 9/10 인자**다.
///   어느 쪽이 맞다고 단정하지 않고 플래그로 노출한다 (문헌 관례가 갈리는 지점).
pub fn thomson_viscosity(
    rho: f64,
    n_e_sigma_t: f64,
    h: f64,
    include_thomson_9_10: bool,
) -> (f64, f64, f64, f64) {
    let d = 4.0 * h
        + (if include_thomson_9_10 {
            damping(2)
        } else {
            1.0
        }) * n_e_sigma_t;
    let tau_pi = 1.0 / d;
    let eta = (4.0 / 15.0) * rho * tau_pi;
    (eta, tau_pi, d, eta * n_e_sigma_t / rho)
}

// ════════════════════════════════════════════ 물리 게이트
/// 긴밀결합 극한에서 π_ab 준정적값/ρ (완전유체화).  반환 (π_qs/ρ, 감쇠율, 소스/ρ).
pub fn tight_coupling_residual(
    mass: f64,
    a_vec: &[f64; 3],
    h: f64,
    sigma_diag: &[f64; 3],
    n_e_sigma_t: f64,
    l_max: usize,
    i_max: usize,
) -> (f64, f64, f64) {
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
    let mut s = State::from_quadrature(a_vec, mass, l_max, i_max, 0.0, 2);
    let rho = s.j[0][0][0];
    // π=0 에서 소스만 본다 (l≥1 을 모두 0 으로).
    for l in 1..=l_max {
        for i in 0..s.j[l].len() {
            s.j[l][i] = vec![0.0; pstf::dim(l)];
        }
    }
    let src = rhs_one(&s, h, &sigma, 2, 0);
    let d = 4.0 * h + damping(2) * n_e_sigma_t;
    let worst = src.iter().fold(0.0f64, |a, b| a.max(b.abs()));
    (worst / d / rho, d, worst / rho)
}

/// n_e σ_T = 0 이면 무충돌 RHS 와 **정확히** 같아야 한다 (H1/H2 회귀 보호).
pub fn free_streaming_limit_residual(
    mass: f64,
    a_vec: &[f64; 3],
    h: f64,
    sigma_diag: &[f64; 3],
) -> f64 {
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
    let s = State::from_quadrature(a_vec, mass, 4, 2, 0.0, 2);
    let mut worst = 0.0f64;
    for l in [0usize, 2] {
        let free = rhs_one(&s, h, &sigma, l, 0);
        let coll = rhs_one_collisional(&s, h, &sigma, l, 0, 0.0, Route::Analytic);
        for k in 0..free.len() {
            worst = worst.max((free[k] - coll[k]).abs());
        }
    }
    worst
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn route_a_reproduces_analytic_eigenvalues() {
        // ★ 핵심 교차검증: 수치 위상함수 적분 vs 해석 다극.
        for l in 0..7 {
            let a = eigenvalue_numeric(l, N_NODES_DEFAULT);
            let b = eigenvalue(l);
            assert!((a - b).abs() < 1e-12, "l={l} {a:e} vs {b:e}");
        }
    }

    #[test]
    fn route_a_l2_damping_is_nine_tenths() {
        assert!((damping_numeric(2, N_NODES_DEFAULT) - 0.9).abs() < 1e-12);
    }

    #[test]
    fn phase_function_is_normalised() {
        assert!((eigenvalue_numeric(0, N_NODES_DEFAULT) - 1.0).abs() < 1e-12);
    }

    #[test]
    fn legendre_matches_known_values() {
        assert!((legendre(2, 0.5) - (1.5 * 0.25 - 0.5)).abs() < 1e-15);
        assert!((legendre(3, 0.3) - (2.5 * 0.027 - 1.5 * 0.3)).abs() < 1e-15);
        for l in 1..8 {
            assert!((legendre(l, 1.0) - 1.0).abs() < 1e-13, "P_{l}(1)");
        }
    }

    #[test]
    fn photon_number_conserved() {
        let s = State::from_quadrature(&[1.0, 0.85, 1.18], 0.0, 4, 2, 0.0, 2);
        let c = collision_term(&s, 0, 0, 3.0, Route::Analytic);
        assert!(c[0].abs() == 0.0, "l=0 충돌항 {}", c[0]);
    }

    #[test]
    fn free_streaming_limit_is_exact() {
        let r = free_streaming_limit_residual(0.0, &[1.0, 0.85, 1.18], 1.0, &[0.05, -0.02, -0.03]);
        assert!(r == 0.0, "residual {r:e}");
    }

    #[test]
    fn viscosity_is_eight_over_twentyseven_with_910() {
        let (_, _, _, r) = thomson_viscosity(1.0, 1e4, 0.0, true);
        assert!((r - 8.0 / 27.0).abs() < 1e-12, "{r}");
        let (_, _, _, r0) = thomson_viscosity(1.0, 1e4, 0.0, false);
        assert!((r0 - 4.0 / 15.0).abs() < 1e-12, "{r0}");
        assert!((r / r0 - 10.0 / 9.0).abs() < 1e-12);
    }

    #[test]
    fn tight_coupling_scales_as_inverse_rate() {
        let a = [1.0, 0.85, 1.18];
        let sg = [0.05, -0.02, -0.03];
        let lo = tight_coupling_residual(0.0, &a, 1.0, &sg, 1e3, 4, 2).0;
        let hi = tight_coupling_residual(0.0, &a, 1.0, &sg, 1e4, 4, 2).0;
        assert!((8.0..12.0).contains(&(lo / hi)), "ratio {}", lo / hi);
    }

    #[test]
    fn collision_damps_l2_by_nine_tenths() {
        let s = State::from_quadrature(&[1.0, 0.85, 1.18], 0.0, 4, 2, 0.0, 2);
        let c = collision_term(&s, 2, 0, 2.0, Route::Analytic);
        for k in 0..9 {
            assert!((c[k] + 2.0 * 0.9 * s.j[2][0][k]).abs() < 1e-15);
        }
    }

    #[test]
    fn collisional_integration_drives_pi_down() {
        // 충돌이 켜지면 π 가 무충돌보다 작아진다 (부호·크기 감각 확인).
        let a0 = [1.0, 0.85, 1.18];
        let sg = [0.05, -0.02, -0.03];
        let (_, _, _, pi_free) = integrate_collisional(
            &a0,
            0.0,
            1.0,
            &sg,
            0.0,
            0.2,
            200,
            4,
            2,
            0.0,
            Route::Analytic,
        );
        let (_, _, _, pi_coll) = integrate_collisional(
            &a0,
            0.0,
            1.0,
            &sg,
            5.0,
            0.2,
            200,
            4,
            2,
            0.0,
            Route::Analytic,
        );
        let w_free = pi_free
            .last()
            .unwrap()
            .iter()
            .fold(0.0f64, |a, b| a.max(b.abs()));
        let w_coll = pi_coll
            .last()
            .unwrap()
            .iter()
            .fold(0.0f64, |a, b| a.max(b.abs()));
        assert!(w_coll < w_free, "coll {w_coll:e} !< free {w_free:e}");
    }

    #[test]
    fn stiffness_flag_trips() {
        assert!(stiffness_ratio(1.0, 0.01).1);
        assert!(!stiffness_ratio(1e4, 0.01).1);
    }
}
