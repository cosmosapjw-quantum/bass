"""
F2 · **정확해 매트릭스** — 차트 상태벡터로 내린 닫힌형 참조값 레지스트리.

모든 수치는 `audit/f2_exact_derivation.py` 의 sympy 유도 + Wolfram 독립 재유도
(54차, 두 경로 완전 합치)에서 왔다 — 문헌 암기 인용이 아니다.  기존
`audit/d_tilted_II.py` 의 CS(II) 하드코드는 이 유도로 **독립 확인**되었다.

평형점 (자기유사 정확해):
    class_a : Kasner 원 𝒦, 평탄 FLRW F, Collins–Stewart CS(II),
              Jacobs 원판 (γ=2 전용 — q≡2 라 Σ-원판 전체가 평형)
    class_b : Milne (Ã=1), Collins VI_h (κ<0 유체), plane wave 족
              — ★ 완전족: Δ=0, Σ̃=Ñ=−Σ₊(1+Σ₊), Ã=(1+Σ₊)²,
                N₊² = (1+Σ₊)[κ(1+Σ₊)−3Σ₊], Ω=0 자동, Σ₊∈(−1,0]
                (Σ₊=−1 은 Ã=0 — class A 경계라 제외).
                N₊=0 가지는 κ=3Σ₊/(1+Σ₊)≤0 뿐 — **VII_h 는 N₊≠0 필수**.

동적 닫힌형 (제1적분):
    진공 type II (Taub): L=(2−Σ₊)/Σ₋ 정확 보존 (Taub 점 (2,0) 직선 궤도);
                         LRS 는 Φ(Σ₊)−τ 보존, Φ=−ln(1−Σ₊)/4+ln(1+Σ₊)/12+ln(2−Σ₊)/6
    진공 type V: Σ̃(τ) = Σ̃₀/(Σ̃₀+(1−Σ̃₀)e^{4τ})  (로지스틱; Milne 로 수렴)

범위 밖 (F2b 로 명시 이월): Taub–NUT IX 동적 닫힌형 (type_ix_d 차트),
예외형 VI*_-1/9 의 Wainwright(γ=10/9)/Collinson–French 해.
"""
from __future__ import annotations

import numpy as np

GAMMA_RANGE_FLUID = (2.0 / 3.0, 2.0)   # CS(II)/Collins 유체해의 존재 구간


def _check_gamma(gamma):
    lo, hi = GAMMA_RANGE_FLUID
    if not lo < gamma < hi:
        raise ValueError(f"γ = {gamma} 는 유체 평형해 존재 구간 (2/3, 2) 밖")


# ---------------------------------------------------------------- class_a
def kasner(theta):
    """Kasner 원 𝒦: Σ₊²+Σ₋²=1, N=0, Ω=0 (진공, q=2). 각 θ 로 파라미터화."""
    return np.array([np.cos(theta), np.sin(theta), 0.0, 0.0, 0.0])


def flrw_flat():
    """평탄 FLRW F: Σ=N=0, Ω=1."""
    return np.zeros(5)


def collins_stewart_II(gamma):
    """CS(II): Σ₊=(3γ−2)/8, N₁²=9(2−γ)(3γ−2)/16, Ω=(18−3γ)/16."""
    _check_gamma(gamma)
    sp = (3.0 * gamma - 2.0) / 8.0
    n1 = np.sqrt(9.0 * (2.0 - gamma) * (3.0 * gamma - 2.0) / 16.0)
    return np.array([sp, 0.0, n1, 0.0, 0.0])


def jacobs(sigma_p, sigma_m):
    """Jacobs 원판 (γ=2 전용): N=0 이면 q≡2 → Σ-원판 내부 전체가 평형."""
    if sigma_p**2 + sigma_m**2 >= 1.0:
        raise ValueError("Jacobs 원판은 Σ² < 1 내부")
    return np.array([sigma_p, sigma_m, 0.0, 0.0, 0.0])


def taub_II_vacuum(sigma_p, sigma_m=0.0):
    """진공 type II 궤도 위 점: N₁ = √(12(1−Σ²)) 로 Ω=0 강제."""
    s2 = sigma_p**2 + sigma_m**2
    if not s2 < 1.0:
        raise ValueError("진공 type II 는 Σ² < 1 (N₁² = 12(1−Σ²) > 0)")
    return np.array([sigma_p, sigma_m, np.sqrt(12.0 * (1.0 - s2)), 0.0, 0.0])


def taub_line_integral(y):
    """L = (2−Σ₊)/Σ₋ — 진공 type II 에서 정확 보존 (dL/dτ = 0 기호 확인)."""
    y = np.asarray(y, float)
    return (2.0 - y[..., 0]) / y[..., 1]


def taub_time_integral(sigma_p, tau):
    """Φ(Σ₊) − τ — LRS 진공 type II 에서 보존 (dΦ/dτ = 1 기호 확인)."""
    s = np.asarray(sigma_p, float)
    return (-np.log(1.0 - s) / 4.0 + np.log(1.0 + s) / 12.0
            + np.log(2.0 - s) / 6.0) - tau


# ---------------------------------------------------------------- class_b
def milne():
    """Milne (type V 진공 미래 끌개): Ã=1, 나머지 0, q=0. κ=0."""
    return np.array([0.0, 0.0, 0.0, 1.0, 0.0])


def collins_VIh(gamma, kappa):
    """Collins VI_h 유체해: Σ₊=−(3γ−2)/4, Σ̃=−3(3γ−2)²/(16κ),
       Ã=9(γ−2)(3γ−2)/(16κ)  — κ<0 에서만 Ã>0.

    ★ 존재조건 (리뷰 MAJOR 2): Ω = −3(γκ−3γ−2κ+2)/(4κ) > 0 은
      κ < −(3γ−2)/(2−γ) 와 동치 — 위반하면 RHS=0 인 고정점이긴 하나
      **음의 에너지밀도** (정확해 아님).  오라클 게이트(RHS=0)로는 안
      잡히므로 여기서 막는다 (κ=−4 는 γ≳1.44 부터 위반)."""
    _check_gamma(gamma)
    if not kappa < 0.0:
        raise ValueError("Collins VI_h 는 κ < 0 (VI_h) 에서만 Ã > 0")
    if not kappa < -(3.0 * gamma - 2.0) / (2.0 - gamma):
        raise ValueError(
            f"Ω ≤ 0: Collins VI_h 존재조건 κ < −(3γ−2)/(2−γ) "
            f"= {-(3.0*gamma-2.0)/(2.0-gamma):.3f} 위반 (κ = {kappa})")
    G = 3.0 * gamma - 2.0
    st = -3.0 * G * G / (16.0 * kappa)
    at = 9.0 * (gamma - 2.0) * G / (16.0 * kappa)
    return np.array([-G / 4.0, st, 0.0, at, 0.0])


def plane_wave(sigma_p, kappa):
    """진공 plane wave 족: Σ̃=Ñ=−Σ₊(1+Σ₊), Ã=(1+Σ₊)²,
       N₊²=(1+Σ₊)[κ(1+Σ₊)−3Σ₊].  정의역 Σ₊∈(−1,0] (Σ̃≥0), N₊²≥0.
       Σ₊=0 은 Milne.  ★ κ>0 (VII_h) 은 N₊≠0 로만 실현된다."""
    if not -1.0 < sigma_p <= 0.0:
        raise ValueError("plane wave 는 Σ₊ ∈ (−1, 0] (Σ̃ ≥ 0 정의역)")
    u = 1.0 + sigma_p
    np_sq = u * (kappa * u - 3.0 * sigma_p)
    if np_sq < 0.0:
        raise ValueError(f"N₊² = {np_sq:.3e} < 0 — 이 (Σ₊, κ) 에 plane wave 없음")
    return np.array([sigma_p, -sigma_p * u, 0.0, u * u, np.sqrt(np_sq)])


def typeV_vacuum(sigma_tilde):
    """진공 type V 궤도 위 점: (0, Σ̃, 0, 1−Σ̃, 0), κ=0."""
    if not 0.0 < sigma_tilde < 1.0:
        raise ValueError("진공 type V 는 Σ̃ ∈ (0,1)")
    return np.array([0.0, sigma_tilde, 0.0, 1.0 - sigma_tilde, 0.0])


def typeV_logistic(sigma_tilde0, tau):
    """진공 type V 닫힌형: Σ̃(τ) = Σ̃₀/(Σ̃₀+(1−Σ̃₀)e^{4τ})."""
    t = np.asarray(tau, float)
    return sigma_tilde0 / (sigma_tilde0 + (1.0 - sigma_tilde0) * np.exp(4.0 * t))


# ------------------------------------------------- F2b · 예외형 VI*_{-1/9}
# 유도: audit/f2b_exact_derivation.py (sympy) + Wolfram + γ=1.5 수치 전수 —
# 세 경로 합치.  상태 순서 (Σ₊, Σ₋, S₂, Sx, Nm, A).

def exc_vacuum_arc(sigma_p):
    """예외형 진공 호: A=Σ₊+1, Σ₋=√3(Σ₊+1), Nm=w, **Sx=−w** (상대부호 필수),
       w=√(−(Σ₊+1)(4Σ₊+3)), Ω=0 자동.  정의역 Σ₊∈(−1,−3/4]."""
    if not -1.0 < sigma_p <= -0.75:
        raise ValueError("예외형 진공 호는 Σ₊ ∈ (−1, −3/4]")
    u = sigma_p + 1.0
    w = np.sqrt(-u * (4.0 * sigma_p + 3.0))
    return np.array([sigma_p, np.sqrt(3.0) * u, 0.0, -w, w, u])


def exc_collins(gamma):
    """예외형 Collins (F2 Collins VI_h 의 κ=−9 축약과 정확 일치):
       Σ₊=−(3γ−2)/4, Σ₋=−Σ₊/√3, A²=−Σ₊(Σ₊+1)/3, Ω=(5−3γ)/3 — 존재 γ<5/3."""
    _check_gamma(gamma)
    if not gamma < 5.0 / 3.0:
        raise ValueError("예외형 Collins 존재조건 γ < 5/3 (Ω=(5−3γ)/3 > 0)")
    sp = -(3.0 * gamma - 2.0) / 4.0
    return np.array([sp, -sp / np.sqrt(3.0), 0.0, 0.0, 0.0,
                     np.sqrt(-sp * (sp + 1.0) / 3.0)])


def exc_s2_vacuum():
    """예외형 S₂-진공점 (γ-무관): Σ₊=−1/3, Σ₋=1/(3√3), S₂²=5/27, A²=1/6, Ω=0."""
    return np.array([-1.0 / 3.0, 1.0 / (3.0 * np.sqrt(3.0)),
                     np.sqrt(5.0 / 27.0), 0.0, 0.0, 1.0 / np.sqrt(6.0)])


def exc_wainwright(a_sq):
    """Wainwright γ=10/9 **평형점 선분**: S₂²=2A²−4/27, A²∈[2/27,1/6] —
       Collins(A²=2/27)와 S₂-진공점(A²=1/6)을 잇는다.  γ≠10/9 에서는
       강제식 (6A²−1)(9γ−10)=0 으로 A²=1/6 만 생존 (시험이 감시)."""
    if not 2.0 / 27.0 <= a_sq <= 1.0 / 6.0:
        raise ValueError("Wainwright 선분은 A² ∈ [2/27, 1/6]")
    return np.array([-1.0 / 3.0, 1.0 / (3.0 * np.sqrt(3.0)),
                     np.sqrt(2.0 * a_sq - 4.0 / 27.0), 0.0, 0.0,
                     np.sqrt(a_sq)])


# ------------------------------------------------- F2b · Taub (진공 LRS IX)
def taub_lrs_ix(sigma_p, u):
    """진공 LRS IX (Taub) 궤도 위 점 — class_a 상태 (Σ₋=0, N₂=N₃=n, N₁=un).
       진공 Gauss: n²·u(u−4)=12(1−Σ₊²) → u>4 가 IX 가지 (전부 양수 N).
       ★ u<0 은 공허가 아니라 **LRS VIII 가지** (N₁ 반대부호 — 범위 밖 명시),
       0≤u≤4 는 n²≤0 공허, u=4 는 축약식의 극."""
    if not (abs(sigma_p) < 1.0 and u > 4.0):
        raise ValueError("Taub LRS IX 는 |Σ₊|<1, u>4 (진공 Gauss + IX 부호)")
    n = np.sqrt(12.0 * (1.0 - sigma_p**2) / (u * (u - 4.0)))
    return np.array([sigma_p, 0.0, u * n, n, n])


def taub_reduced_rates(sigma_p, u):
    """Taub 축약계 (audit 검산 완료): (Σ₊', u') 닫힌형."""
    dsp = 2.0 * (1.0 - sigma_p**2) * (2.0 * (u - 1.0)
                                      - sigma_p * (u - 4.0)) / (u - 4.0)
    return dsp, -6.0 * sigma_p * u


#: 평형점 매트릭스 — 이름 → (차트, 생성자(γ), κ).  지속성 게이트 소비용.
EQUILIBRIA = {
    "kasner":          ("class_a", lambda gamma: kasner(0.7),            0.0),
    "flrw_flat":       ("class_a", lambda gamma: flrw_flat(),            0.0),
    "cs_II":           ("class_a", collins_stewart_II,                   0.0),
    "milne":           ("class_b", lambda gamma: milne(),                0.0),
    "collins_VIh":     ("class_b", lambda gamma: collins_VIh(gamma, -4.0), -4.0),
    "plane_wave_VIIh": ("class_b", lambda gamma: plane_wave(-0.4, 4.0),  4.0),
    "plane_wave_IV":   ("class_b", lambda gamma: plane_wave(-0.4, 0.0),  0.0),
    # F2b · 예외형 (κ=−9 는 차트에 내장 — kappa 인자 미사용)
    "exc_collins":     ("exceptional", exc_collins,                      0.0),
    "exc_s2_vacuum":   ("exceptional", lambda gamma: exc_s2_vacuum(),    0.0),
    "exc_vacuum_arc":  ("exceptional", lambda gamma: exc_vacuum_arc(-0.85), 0.0),
}
