"""
H3 · Thomson 충돌항 — 무충돌(Vlasov) 계층을 **진짜 Boltzmann** 계층으로.

Lewis-Challinor 논문은 암흑물질(무충돌)을 다루며 "In the case of collisional matter the
right hand side would contain a collision term" 이라고만 적는다.  여기서 그 충돌항을
Thomson 산란에 대해 구성한다.

★ **중요한 한계 (정직하게)**: `freestream.py` 의 정확 구적 오라클은 **충돌항을 검증할 수
  없다** — 충돌이 자유흐름 특성곡선(불변기저 p_i = const)을 깨뜨려 구적의 정확성 근거가
  사라지기 때문이다.  그래서 H3 의 두 경로는 H4 와 다른 방식으로 나눈다:

    **경로 A (수치 위상함수)**: Thomson 미분단면적 K(μ) ∝ (1+μ²) 을 각격자에서 직접
       적분해 다극 고윳값 λ_l 을 **측정**한다.  다극 대수를 쓰지 않는다.
    **경로 B (해석 다극)**: Legendre 전개 1+μ² = 4/3 + (2/3)P₂ 에서
       λ_l = 4π k_l/(2l+1) 을 해석적으로 준다.  적분을 하지 않는다.

  두 경로가 λ₂ = 1/10 (즉 감쇠 **9/10**) 을 독립적으로 재생산한다.

물리:  비편광 Thomson 산란은 탄성(전자 정지틀)이라 **광자 에너지를 바꾸지 않고 각분포만
  등방화**한다.  따라서 충돌항은 (l, i) 중 **l 에만** 의존한다:

      C[J^(i)_{A_l}] = -(n_e σ_T) (1 - λ_l) J^(i)_{A_l}

      λ_0 = 1     → 감쇠 0      (광자 수 보존)
      λ_1 = 0     → 감쇠 1      (쌍극; 실제로는 바리온 속도로 완화 → `dipole_source`)
      λ_2 = 1/10  → 감쇠 **9/10**
      λ_l = 0     → 감쇠 1      (l ≥ 3)
"""
from __future__ import annotations

import numpy as np
from numpy.polynomial.legendre import leggauss, legval

from bianchi.matter import hierarchy as H


# ════════════════════════════════════════════ 경로 A — 수치 위상함수
def thomson_eigenvalue_numeric(l, n_nodes=200):
    """λ_l 을 Thomson 위상함수의 **각적분**으로 측정 (다극 대수 미사용).

        λ_l = ∫_{-1}^{1} dμ K̃(μ) P_l(μ),      K̃(μ) = (3/8)(1+μ²)
      (dΩ' = 2π dμ 를 위상함수 정규화에 흡수한 형태; ∫K̃ dμ = 1.)
    """
    x, w = leggauss(int(n_nodes))
    c = np.zeros(l + 1)
    c[l] = 1.0
    p_l = legval(x, c)
    kernel = (3.0 / 8.0) * (1.0 + x ** 2)
    return float(np.sum(w * kernel * p_l))


def thomson_damping_numeric(l, n_nodes=200):
    """감쇠 계수 (1 - λ_l) — 경로 A."""
    return 1.0 - thomson_eigenvalue_numeric(l, n_nodes)


# ════════════════════════════════════════════ 경로 B — 해석 다극
def thomson_eigenvalue(l):
    """λ_l = 4π k_l/(2l+1) — 해석값 (적분 미사용).

    K(μ) = (3/16π)(1+μ²) = (1/4π)[P₀ + ½P₂]  ⇒  k₀ = 1/4π, k₂ = 1/8π, 나머지 0.
    """
    if l == 0:
        return 1.0
    if l == 2:
        return 0.1
    return 0.0


def thomson_damping(l):
    """감쇠 계수 (1 - λ_l) — 경로 B.  l=0: 0,  l=2: **9/10**,  나머지: 1."""
    return 1.0 - thomson_eigenvalue(l)


# ════════════════════════════════════════════ 계층에 충돌항 붙이기
# ★ V2b 에서 **측정**한 광자–바리온 항력 계수 (가정하지 않았다).
#   등방 광자 + 작은 전자속도 v_e 에서  q̇_a = +n_eσ_T · c · ρ · v_{e,a}  의 c 를
#   전자 정지틀 boost 로 조립한 충돌항에서 직접 뽑았다:
#       |v_e| = 1e−4 → c = 1.333333354,   3e−3 → 1.333351   (편차 ∝ v_e²)
#   ⇒ c = 4/3 + O(v²).  `collision_moving.dipole_source_coefficient()` 참조.
DIPOLE_DRAG_COEFF = 4.0 / 3.0


def dipole_source(rho, v_e, n_e_sigma_T):
    """★ V2b — l=1 의 **바리온 속도 원천** (H3 docstring 이 약속만 하고 없던 것).

        q̇_a|_충돌 = −n_eσ_T [ q_a − (4/3) ρ v_{e,a} ]

    즉 쌍극은 0 이 아니라 **전자 속도로 완화**한다.  이 함수는 그 원천 부분만 준다.
    계수 4/3 은 `collision_moving` 에서 측정한 값이다 (문헌 인용이 아니다).
    """
    return n_e_sigma_T * DIPOLE_DRAG_COEFF * float(rho) * np.asarray(v_e, float)


def collision_term(J, l, i, n_e_sigma_T, route="analytic", v_e=None, rho=None):
    """C[J^(i)_{A_l}] = -(n_e σ_T)(1 - λ_l) J^(i)_{A_l}  (+ l=1 의 바리온 원천).

    ★ 탄성 산란이라 i(속도가중)에 의존하지 않는다 — 에너지를 바꾸지 않기 때문.
      (V2a 에서 **측정으로 확인**: m=1, l=2 에서 i=0..3 모두 감쇠비 0.1000000000.)

    ★ `v_e` 를 주면 l=1 에 `dipole_source` 를 더한다.  v_e=None 이면 옛 거동 그대로.
    """
    damp = (thomson_damping(l) if route == "analytic"
            else thomson_damping_numeric(l))
    out = -n_e_sigma_T * damp * np.asarray(J[(l, i)], float)
    if v_e is not None and l == 1:
        r = float(J[(0, 0)]) if rho is None else float(rho)
        out = out + dipole_source(r, v_e, n_e_sigma_T)
    return out


def hierarchy_rhs_collisional(J, H_hubble, sigma, l, i, n_e_sigma_T,
                              route="analytic", signs=None):
    """무충돌 RHS + Thomson 충돌항.  n_e_sigma_T=0 이면 H1/H2 와 정확히 일치."""
    free = np.asarray(H.hierarchy_rhs(J, H_hubble, sigma, l, i, signs), float)
    if n_e_sigma_T == 0.0:
        return free
    return free + collision_term(J, l, i, n_e_sigma_T, route)


# ════════════════════════════════════════════ 유도: Thomson 점성
POLARISED_QUADRUPOLE_DAMPING = 0.75      # ★ V2 에서 **측정**한 값 (3/4). 아래 참조.


def thomson_viscosity(rho, n_e_sigma_T, H_hubble=0.0, include_thomson_9_10=True,
                      polarised=False):
    """긴밀결합(tight-coupling) 극한의 광자 전단점성 η — H4 의 매칭을 그대로 쓴다.

        l=2 감쇠율 = 4H + (유효감쇠) n_e σ_T          (팽창 + 충돌)
        1/τ_π = 그 값,   2η/τ_π = (8/15)ρ   ⇒   η = (4/15) ρ τ_π

    ★★ **V2 에서 닫힘 (2026-07-31)** — 예전 이 자리에 "문헌 관례가 갈린다" 고
      적어 두었던 `8/27 vs 4/15` 미결이 측정으로 해결됐다.  세 값의 정체는 이렇다:

        유효감쇠 1      → η = **4/15**  = 0.2667   각구조를 아예 무시한 값
        유효감쇠 9/10   → η = **8/27**  = 0.2963   **비편광** 계층의 자기정합 값
        유효감쇠 3/4    → η = **16/45** = 0.3556   **편광 포함 — 물리적으로 옳은 값**

      3/4 는 `collision_oracle.effective_quadrupole_damping()` 이 각격자에서 잰
      값이다: 편광을 합산하지 않은 Thomson 연산자의 l=2 축소 블록이
      [[1/10, √6/10], [√6/10, 3/5]] 로 나오고, 소스가 강도 채널에만 들어가는
      준정적 균형을 풀면 유효감쇠 = 3/4 가 나온다 (기계정밀도).
      비 (9/10)/(3/4) = **6/5** 는 Hu 의 강의노트 "polarization increases the
      viscosity of the fluid by a factor of 6/5" 와 일치한다.

    ⇒ 새 코드는 `polarised=True` 를 쓸 것.  옛 플래그는 **재현용**으로 남긴다.
    """
    if polarised:
        d2 = POLARISED_QUADRUPOLE_DAMPING
    else:
        d2 = thomson_damping(2) if include_thomson_9_10 else 1.0
    damp = 4.0 * H_hubble + d2 * n_e_sigma_T
    tau_pi = 1.0 / damp
    eta = (4.0 / 15.0) * rho * tau_pi
    return dict(eta=eta, tau_pi=tau_pi, damping_rate=damp,
                eta_times_nesigT_over_rho=eta * n_e_sigma_T / rho,
                include_thomson_9_10=include_thomson_9_10, polarised=polarised,
                quadrupole_damping=d2)


# ════════════════════════════════════════════ 물리 게이트
def tight_coupling_residual(mass=0.0, a_vec=(1.0, 0.85, 1.18), H_hubble=1.0,
                           sigma_diag=(0.05, -0.02, -0.03), n_e_sigma_T=1e4,
                           l_max=4, i_max=2):
    """긴밀결합 극한에서 π_ab 의 준정적값이 0 으로 간다 (완전유체화).

        준정적: 0 = -(damp)π - (8/15)ρσ  ⇒  π ~ (8/15)ρσ/damp → 0  as n_eσ_T → ∞
    반환 dict(pi_quasi_static_over_rho, scales_as_inverse_rate).
    """
    a = np.asarray(a_vec, float)
    sig = np.diag(np.asarray(sigma_diag, float))
    rho = H.J_moment(a, mass, 0, 0)
    J = {(l, i): H.J_moment(a, mass, l, i)
         for l in range(l_max + 1) for i in range(i_max + 3)}
    for l in range(1, l_max + 1):
        for i in range(i_max + 3):
            J[(l, i)] = np.zeros((3,) * l)               # π=0 에서 소스만 본다
    src = np.asarray(hierarchy_rhs_collisional(J, H_hubble, sig, 2, 0, 0.0), float)
    damp = 4.0 * H_hubble + thomson_damping(2) * n_e_sigma_T
    pi_qs = src / damp
    return dict(pi_quasi_static_over_rho=float(np.abs(pi_qs).max() / rho),
                damping_rate=damp, source_over_rho=float(np.abs(src).max() / rho))


def photon_number_is_conserved(J, l_max=4, i_max=2, n_e_sigma_T=1.0):
    """Thomson 은 광자 수를 보존한다 ⇒ l=0 충돌항이 정확히 0."""
    c = collision_term(J, 0, 0, n_e_sigma_T)
    return float(np.abs(np.atleast_1d(c)).max())


def free_streaming_limit_residual(mass=0.0, a_vec=(1.0, 0.85, 1.18), H_hubble=1.0,
                                  sigma_diag=(0.05, -0.02, -0.03)):
    """n_e σ_T = 0 이면 무충돌 RHS 와 **정확히** 같아야 한다."""
    a = np.asarray(a_vec, float)
    sig = np.diag(np.asarray(sigma_diag, float))
    J = {(l, i): H.J_moment(a, mass, l, i) for l in (0, 2, 4) for i in (0, 1, 2, 3)}
    worst = 0.0
    for l in (0, 2):
        free = np.asarray(H.hierarchy_rhs(J, H_hubble, sig, l, 0), float)
        coll = np.asarray(hierarchy_rhs_collisional(J, H_hubble, sig, l, 0, 0.0), float)
        worst = max(worst, float(np.abs(free - coll).max()))
    return worst
