"""
H4 · imperfect fluid 를 **유도**한다 — Eckart / Israel-Stewart 가 계층 절단의 귀결임을 보인다.

`matter/viscous.py` 는 π_ab = -2η σ_ab (Eckart) 와 τ_π π̇ + π = -2η σ (IS) 를 **가정**하고
η, ζ, τ_π 를 자유 파라미터로 받는다.  여기서는 Lewis-Challinor 계층(식 12)의 l=2 방정식에서
이들을 **유도**해 자유 파라미터를 없앤다.

★ 두 경로를 **분리해서** 측정하고 교차검증한다 (한쪽 실수를 다른 쪽이 잡는다):

  **경로 A — freestream (정확 구적)**:  분포함수 모멘트를 직접 구적하고 유한차분으로
     dπ_ab/dt 를 얻는다.  계층 수식을 **전혀 쓰지 않는다**.
  **경로 B — PSTF 계층**:  식 (12) 의 l=2, i=0 방정식 계수를 직접 읽는다.
     구적을 **전혀 쓰지 않는다** (상태를 손으로 세팅).

유도 결과 (무질량 무충돌):

    σ=0 에서   π̇_ab = -4H π_ab                        ⇒  1/τ_π = 4H
    π=0 에서   π̇_ab = -(8/15) ρ σ_ab                   ⇒  2η/τ_π = (8/15)ρ
    ⇒  **τ_π = 1/(4H)**,   **η = ρ/(15H)**

  Eckart 극한(π̇→0)도 같은 η 를 준다:  0 = -4Hπ - (8/15)ρσ ⇒ π = -(2/15)ρσ/H = -2ησ ✓

★ σ=0 이면 l=2 방정식이 **절단 없이 정확히 닫힌다** — (A),(B),(C) 항이 모두 σ 에 비례하므로.
  무질량은 추가로 J^(1)_ab = π_ab (i-무관) 이라 π̇ = -H[5π - π] = -4Hπ 가 **정확**하다.
  두 경로가 무질량에서 -4.000000 으로 일치하는 이유다.

★ 유질량은 J^(1)_ab ≠ π_ab 이므로 감쇠율이 커지고 **성분마다 다르다** (τ_π 가 스칼라가
  아니게 된다).  측정: 1/τ_π = 4.044H (m=1), 4.345H (m=4).  평균과 이방성을 함께 보고한다.
"""
from __future__ import annotations

import numpy as np

from bianchi.matter import freestream as fs
from bianchi.matter import hierarchy as H

#: 무질량 무충돌의 유도값 (아래 두 경로가 모두 재생산해야 한다).
MASSLESS_DAMPING_RATE = 4.0          # 1/τ_π in units of H
MASSLESS_SOURCE_COEFF = -8.0 / 15.0  # dπ/dt = coeff · ρ σ


# ════════════════════════════════════════════ 경로 A — freestream (정확 구적)
def route_a_damping(mass=0.0, a_vec=(1.0, 0.85, 1.18), H_hubble=1.0, dt=1e-5):
    """σ=0 등방팽창에서 dπ_ab/dt / π_ab 를 **정확 구적의 유한차분**으로 측정.

    계층 수식을 쓰지 않는다.  반환 dict(rate_per_component, rate_mean, anisotropy).
    a_vec 이 비등방이면 π_ab ≠ 0 이고, σ=0 이므로 ȧ_i = H a_i (모두 같은 비율).
    """
    a = np.asarray(a_vec, float)
    ap = a * (1.0 + H_hubble * dt)
    am = a * (1.0 - H_hubble * dt)
    pi_p = fs.moments(ap, mass)[2]
    pi_m = fs.moments(am, mass)[2]
    pi_0 = fs.moments(a, mass)[2]
    dpi = (pi_p - pi_m) / (2.0 * dt)
    rate = np.array([dpi[k, k] / pi_0[k, k] for k in range(3)])
    return dict(rate_per_component=rate, rate_mean=float(rate.mean()),
                anisotropy=float(rate.max() - rate.min()))


def route_a_source(mass=0.0, delta=0.002):
    """π≈0 에서 σ 를 켤 때의 급작응답 계수 (dπ/dt = coeff·ρσ) — 정확 구적.

    `freestream.sudden_response_coefficient` 를 그대로 쓴다 (구적·차분 수준 정확도).
    """
    return float(fs.sudden_response_coefficient(delta=delta, mass=mass))


# ════════════════════════════════════════════ 경로 B — PSTF 계층
def route_b_damping(mass=0.0, a_vec=(1.0, 0.85, 1.18), H_hubble=1.0):
    """σ=0 에서 l=2 방정식의 감쇠율을 읽는다 — **방정식만** 평가 (미분 없음).

    ★ σ=0 이면 (A),(B),(C) 세 σ-결합 항군이 모두 사라져 l=2 방정식이 **절단 없이**
          π̇_ab = -H[5 π_ab - J^(1)_ab]
      로 정확히 닫힌다.  따라서 이 경로는 임의 질량에서 유효하다.
    ★ a_vec 은 **비등방**이어야 한다 (등방이면 π_ab ≡ 0 이라 감쇠율이 0/0).
      경로 A 와 같은 a_vec 을 써서 같은 물리 상태에서 비교한다.
    """
    a = np.asarray(a_vec, float)
    if abs(a[0] - a[1]) < 1e-12 and abs(a[1] - a[2]) < 1e-12:
        raise ValueError("a_vec 이 등방이면 π_ab ≡ 0 이라 감쇠율을 정의할 수 없다")
    J = {(l, i): H.J_moment(a, mass, l, i)
         for l in (0, 2, 4) for i in (0, 1, 2, 3)}
    pi0 = np.asarray(J[(2, 0)], float)
    dpi = np.asarray(H.hierarchy_rhs(J, H_hubble, np.zeros((3, 3)), 2, 0), float)
    rate = np.array([dpi[k, k] / pi0[k, k] for k in range(3)])
    return dict(rate_per_component=rate, rate_mean=float(rate.mean()),
                anisotropy=float(rate.max() - rate.min()))


def route_b_damping_handset(H_hubble=1.0, pi_diag=(0.1, -0.04, -0.06)):
    """무질량 전용 — J^(i)_ab 를 **손으로** 세팅해 구적을 전혀 쓰지 않는 가장 순수한 경로 B.

    무질량은 J^(i) 가 i-무관이므로 J^(i)_ab = π_ab 로 둘 수 있다 ⇒ π̇ = -H[5π - π] = -4Hπ.
    """
    pi0 = np.diag(np.asarray(pi_diag, float))
    pi0 = pi0 - np.trace(pi0) * np.eye(3) / 3.0
    J = {}
    for l in (0, 2, 4):
        for i in (0, 1, 2, 3):
            J[(l, i)] = 1.0 if l == 0 else np.zeros((3,) * l)
    for i in (0, 1, 2, 3):
        J[(2, i)] = pi0.copy()
    dpi = np.asarray(H.hierarchy_rhs(J, H_hubble, np.zeros((3, 3)), 2, 0), float)
    rate = np.array([dpi[k, k] / pi0[k, k] for k in range(3)])
    return dict(rate_per_component=rate, rate_mean=float(rate.mean()))


def route_b_source(mass=0.0, a_vec=(1.0, 1.0, 1.0), H_hubble=1.0,
                   sigma_diag=(0.05, -0.02, -0.03)):
    """π=0, σ≠0 상태에서 l=2 방정식의 σ-소스 계수 (dπ/dt / (ρσ)) — 계층만 사용."""
    a = np.asarray(a_vec, float)
    sig_d = np.asarray(sigma_diag, float)
    sigma = np.diag(sig_d)
    rho = H.J_moment(a, mass, 0, 0)
    J = {}
    for l in (0, 2, 4):
        for i in (0, 1, 2, 3):
            J[(l, i)] = H.J_moment(a, mass, l, i) if l == 0 else np.zeros((3,) * l)
    src = np.asarray(H.hierarchy_rhs(J, H_hubble, sigma, 2, 0), float)
    coef = np.array([src[k, k] / sig_d[k] for k in range(3)]) / rho
    return float(coef.mean())


# ════════════════════════════════════════════ 유도된 수송계수
def transport_coefficients(mass=0.0, a_vec=(1.0, 0.85, 1.18), H_hubble=1.0,
                           route="hierarchy"):
    """유도된 (η, τ_π) — 자유 파라미터 없음.

        1/τ_π = -(감쇠율),        2η/τ_π = -(소스계수)·ρ
      ⇒ η = -(소스계수)·ρ·τ_π/2

    route: 'hierarchy' (경로 B) 또는 'quadrature' (경로 A).
    무질량 기대값: τ_π = 1/(4H),  η = ρ/(15H).
    """
    rho = H.J_moment(np.asarray(a_vec, float), mass, 0, 0)
    if route == "hierarchy":
        damp = route_b_damping(mass, a_vec, H_hubble)["rate_mean"]
        src = route_b_source(mass, (1.0, 1.0, 1.0), H_hubble)
    elif route == "quadrature":
        damp = route_a_damping(mass, a_vec, H_hubble=H_hubble)["rate_mean"]
        src = route_a_source(mass)
    else:
        raise ValueError("route must be 'hierarchy' or 'quadrature'")
    tau_pi = -1.0 / damp
    eta = -src * rho * tau_pi / 2.0
    return dict(eta=eta, tau_pi=tau_pi, rho=rho, damping_rate=damp,
                source_coeff=src, eta_over_rho_H=eta * H_hubble / rho,
                route=route)


def eckart_eta_from_hierarchy(rho, H_hubble):
    """Eckart 준정적 극한의 η (유도값):  0 = -4Hπ - (8/15)ρσ ⇒ π = -2ησ ⇒ η = ρ/(15H)."""
    return rho / (15.0 * H_hubble)


def relaxation_time_massless(H_hubble):
    """무질량 무충돌 IS 완화시간 (유도값) τ_π = 1/(4H)."""
    return 1.0 / (4.0 * H_hubble)


def cross_validate(mass=0.0, H_hubble=1.0, tol_damp=2e-3, tol_src=5e-3):
    """★ 두 경로 교차검증 — 서로 다른 계산으로 같은 계수가 나오는지.

    반환 dict(route_a, route_b, damping_rel_diff, source_rel_diff, agree).
    """
    a_damp = route_a_damping(mass, H_hubble=H_hubble)["rate_mean"]
    b_damp = route_b_damping(mass, H_hubble=H_hubble)["rate_mean"]
    a_src = route_a_source(mass)
    b_src = route_b_source(mass, H_hubble=H_hubble)
    d_rel = abs(a_damp - b_damp) / abs(b_damp)
    s_rel = abs(a_src - b_src) / abs(b_src)
    return dict(route_a=dict(damping=a_damp, source=a_src),
                route_b=dict(damping=b_damp, source=b_src),
                damping_rel_diff=d_rel, source_rel_diff=s_rel,
                agree=bool(d_rel < tol_damp and s_rel < tol_src))


def entropy_production_is_positive(mass=0.0, H_hubble=1.0,
                                   sigma_diag=(0.05, -0.02, -0.03)):
    """열역학 2법칙 확인: 유도된 η > 0 이므로 T Ṡ = 2η σ² ≥ 0.

    `viscous.entropy_production_rate` 와 같은 형태이나 η 를 **유도값**으로 넣는다.
    """
    from bianchi.matter import viscous as vis
    tc = transport_coefficients(mass, H_hubble=H_hubble)
    sig = np.diag(np.asarray(sigma_diag, float))
    return dict(eta=tc["eta"],
                rate=vis.entropy_production_rate(sig / H_hubble, 3.0 * H_hubble,
                                                 tc["eta"], 0.0, H=H_hubble),
                positive=bool(tc["eta"] > 0))
