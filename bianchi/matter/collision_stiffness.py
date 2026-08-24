"""
V2e · **강성(stiffness) 스캔** — 문헌의 `τ̇ δη ≪ 1` 을 우리 수치로 재현한다.

★ 왜 필요한가: Pontzen & Challinor (2007) 는 Bianchi VII_h + Thomson 을 풀 때 매 스텝
  `δη ≪ 1`, `σ δη ≪ 1`, **`τ̇ δη ≪ 1`** 을 강제한다.  세 번째가 Thomson 불투명도에
  대한 강성 제약인데, "≪ 1" 이 실제로 얼마인지는 논문이 숫자로 주지 않는다.
  우리는 **재서** 쓴다 — 그리고 넘었을 때 **조용히 틀리지 않고 경고**하게 만든다.

★ 문제의 구조: 충돌항이 붙은 사중극 방정식은
        π̇ = −Γ π + S,      Γ = 4H + d₂ · τ̇        (d₂ = 유효 사중극 감쇠)
  이고 τ̇ ≫ H 이면 Γ ≈ d₂τ̇ 로 **강성**이 된다.  명시적 RK4 의 안정영역은 실축에서
  |Γ δt| < R 이고 R 은 고전적으로 2.7853 (RK4 의 실축 안정한계) 이다.
  ⇒ **δt_crit = R / Γ** 를 예측하고, 그것을 **측정으로 확인**한다.

★ 정직한 구분 — 두 가지 실패가 있다:
  1. **불안정(instability)**: |Γδt| > R 에서 해가 발산한다.  파국적이라 눈에 띈다.
  2. **정확도 손실**: 안정하더라도 |Γδt| ~ 1 이면 준정적 극한을 제대로 못 따라간다.
     이쪽이 위험하다 — **조용히 틀린다**.  둘 다 측정한다.

★ 대안: 강결합에서는 **준정적 해** π ≈ S/Γ 가 δt 와 무관하게 정확해진다.
  언제 그쪽으로 넘어가야 하는지의 기준도 측정으로 제시한다.
"""
from __future__ import annotations

import warnings

import numpy as np

RK4_REAL_STABILITY_LIMIT = 2.7852935634669  # z = Γδt, RK4 실축 안정한계 (고전값)


# ═══════════════════════════════════════ 1. 모형 문제 (해석해가 있다)
def exact_solution(y0, S, Gamma, t):
    """π̇ = −Γπ + S 의 정확해 (Γ, S 상수).  준정적값은 S/Γ."""
    return S / Gamma + (y0 - S / Gamma) * np.exp(-Gamma * t)


def rk4_solution(y0, S, Gamma, t_end, nsteps):
    """명시적 RK4 — 강성에서 무엇이 일어나는지 보려고 일부러 명시적으로 푼다."""
    dt = t_end / nsteps
    y = float(y0)

    def rhs(v):
        return -Gamma * v + S

    for _ in range(nsteps):
        k1 = rhs(y)
        k2 = rhs(y + 0.5 * dt * k1)
        k3 = rhs(y + 0.5 * dt * k2)
        k4 = rhs(y + dt * k3)
        y = y + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        if not np.isfinite(y) or abs(y) > 1e100:
            return np.inf
    return y


def amplification_factor(z):
    """RK4 의 증폭인자 |R(z)|, z = −Γδt (실축).  |R| > 1 이면 불안정."""
    z = np.asarray(z, float)
    return np.abs(1.0 + z + z ** 2 / 2.0 + z ** 3 / 6.0 + z ** 4 / 24.0)


# ═══════════════════════════════════════ 2. ★ 안정한계를 측정한다
def measured_stability_limit(tol=1e-12, lo=1.0, hi=4.0):
    """★ |R(−z)| = 1 이 되는 z 를 이분법으로 **찾는다** (2.7853 을 인용하지 않는다)."""
    a, b = lo, hi
    for _ in range(200):
        m = 0.5 * (a + b)
        if amplification_factor(-m) > 1.0:
            b = m
        else:
            a = m
        if b - a < tol:
            break
    return 0.5 * (a + b)


#: 안정성 판정에 필요한 최대 스텝수 (|R^n| ≤ 1 ⇔ |R| ≤ 1 이라 n 은 자유롭다).
NS_CAP = 64


def critical_step_scan(tau_dots=(1.0, 10.0, 100.0, 1e3, 1e4), H=1.0, d2=0.9,
                       n_steps_target=60, n_probe=64):
    """★ τ̇ 를 올리며 **명시적 RK4 가 깨지는 δt** 를 실제 적분으로 찾는다.

    반환 [(τ̇, Γ, 측정 δt_crit, Γ·δt_crit)] — 마지막 열이 **τ̇ 에 무관한 상수**여야
    한다 (= 안정한계).  이것이 문헌의 `τ̇ δη ≪ 1` 을 숫자로 바꾼 형태다.

    ★ 적분구간을 Γ 에 맞춰 잡는다 (`t_end ≈ n_steps_target · R/Γ`).  처음에 t_end=1
      고정으로 짰더니 작은 τ̇ 에서 스텝이 한두 번뿐이라 불안정이 드러날 시간이 없었고
      Γδt_crit 가 10.0, 6.5 로 나왔다 — **측정이 아니라 이산화 잔재**였다.

    ★ R3 (성능): 이등분 초반에는 δt 가 1e−6 수준이라 `t_end/δt` 가 2.4e+07 스텝이
      됐다 — 이 한 시험이 전체 회귀의 103 초를 먹고 있었다.  S = 0 이면 해가 정확히
      `y_n = R(−Γδt)^n y₀` 이라 **|y_n| ≤ |y₀| ⇔ |R| ≤ 1** 이고 n 은 판정에 전혀
      영향이 없다.  그래서 스텝수를 `NS_CAP` 으로 자른다 (측정값은 그대로다).
    """
    out = []
    for td in tau_dots:
        G = 4.0 * H + d2 * td
        n = int(n_steps_target)
        t_end = n * RK4_REAL_STABILITY_LIMIT / G
        # ★ 판정 기준: **소스를 끄고** (S=0) 증폭이 1 을 넘는 지점.
        #   y_end = R^n y0 이므로 |y_end| = |y0| 이 곧 |R| = 1 이다 — 임계값이
        #   "허용 성장률" 같은 임의 문턱에 의존하지 않는다.
        #   ★ 처음에 |y| < 1e3 을 기준으로 썼더니 60 스텝에 걸친 1000배 성장을
        #     허용해 |R| = 10^{3/60} = 1.122 지점을 재고 있었다 (Γδt = 2.8813).
        lo, hi = 1e-12, 10.0 / G
        for _ in range(n_probe):
            mid = np.sqrt(lo * hi)
            ns = min(max(1, int(round(t_end / mid))), NS_CAP)
            y = rk4_solution(1.0, 0.0, G, ns * mid, ns)
            if np.isfinite(y) and abs(y) <= 1.0:
                lo = mid
            else:
                hi = mid
            if hi / lo < 1.0 + 1e-12:
                break
        dt_c = np.sqrt(lo * hi)
        out.append((float(td), float(G), float(dt_c), float(G * dt_c)))
    return out


def explicit_step_cost(tau_over_H=(1e0, 1e2, 1e4, 1e6), H=1.0, d2=0.75, T=1.0,
                       safety=0.5):
    """★ **전환의 진짜 이유는 정확도가 아니라 비용**이다 — 필요한 스텝수를 센다.

    안정성만으로 δt ≤ safety·R/Γ 이 강제되므로, 고정 물리구간 T 를 풀려면
    스텝수가 Γ 에 **비례**해 늘어난다.  τ̇/H = 10⁶ 이면 T = 1/H 에 27만 스텝이다.
    반환 [(τ̇/H, Γ, δt_max, 필요 스텝수)].
    """
    out = []
    for r in tau_over_H:
        td = r * H
        G = 4.0 * H + d2 * td
        dt = safety * RK4_REAL_STABILITY_LIMIT / G
        out.append((float(r), float(G), float(dt), int(np.ceil(T / dt))))
    return out


# ═══════════════════════════════════════ 3. ★ 조용한 정확도 손실
#
# ★ 처음에 **상수 소스**로 이 절을 짰다가 퇴화된 시험을 만들었다: S 가 상수면
#   RK4 는 (안정하기만 하면) z 에 무관하게 정확한 준정적값 S/Γ 에 그대로 앉는다
#   (측정: Γ=1e3, z=0.01…1 에서 상대오차 1e−14…0).  "정확도 손실이 없다" 가 아니라
#   **시험이 아무것도 재지 않았던 것**이다.
#   실제 물리에서는 소스(전단·팽창)가 시간에 따라 변한다.  그래서 진동 소스로 바꾼다 —
#   Bianchi VII₀ 의 진동을 생각하면 이쪽이 오히려 현실적인 설정이다.
def exact_forced(Gamma, S0, eps, omega, t, y0=0.0):
    """π̇ = −Γπ + S₀(1 + ε sin ωt) 의 정확해.

        π = S₀/Γ (1 − e^{−Γt}) + y₀e^{−Γt}
            + S₀ε [Γ sin ωt − ω cos ωt + ω e^{−Γt}] / (Γ² + ω²)
    """
    e = np.exp(-Gamma * t)
    return (S0 / Gamma * (1 - e) + y0 * e
            + S0 * eps * (Gamma * np.sin(omega * t) - omega * np.cos(omega * t)
                          + omega * e) / (Gamma ** 2 + omega ** 2))


def rk4_forced(Gamma, S0, eps, omega, t_end, nsteps, y0=0.0):
    """진동 소스에서의 명시적 RK4."""
    dt = t_end / nsteps
    y = float(y0)

    def rhs(t, v):
        return -Gamma * v + S0 * (1.0 + eps * np.sin(omega * t))

    for k in range(nsteps):
        t = k * dt
        k1 = rhs(t, y)
        k2 = rhs(t + 0.5 * dt, y + 0.5 * dt * k1)
        k3 = rhs(t + 0.5 * dt, y + 0.5 * dt * k2)
        k4 = rhs(t + dt, y + dt * k3)
        y = y + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        if not np.isfinite(y) or abs(y) > 1e100:
            return np.inf
    return y


def accuracy_vs_z(zs=(0.01, 0.03, 0.1, 0.3, 1.0, 2.0, 2.7), Gamma=1e3, S0=1.0,
                  eps=0.5, omega=None, t_end=None):
    """★ **안정하더라도** |Γδt| 가 크면 조용히 부정확해진다 — 진동 소스에서 측정.

    기본 설정은 ω = Γ/10 (소스가 감쇠보다 느리게 진동), t_end = 3주기.
    반환 [(z, 상대오차)].
    """
    omega = 0.1 * Gamma if omega is None else float(omega)
    t_end = 3.0 * 2 * np.pi / omega if t_end is None else float(t_end)
    ex = exact_forced(Gamma, S0, eps, omega, t_end)
    out = []
    for z in zs:
        dt = z / Gamma
        ns = max(1, int(np.ceil(t_end / dt)))
        y = rk4_forced(Gamma, S0, eps, omega, t_end, ns)
        out.append((float(z), float(abs(y - ex) / abs(ex))))
    return out


def quasi_static_error(Gamma, S0=1.0, eps=0.5, omega=None, t_end=None):
    """준정적 근사 π ≈ S(t)/Γ 의 오차 — Γ ≫ ω 이면 **δt 와 무관하게** 정확해진다.

    (정확해의 진동 성분이 S₀ε[Γ sin − ω cos]/(Γ²+ω²) → S₀ε sin/Γ 로 가기 때문.)
    """
    omega = 0.1 * Gamma if omega is None else float(omega)
    t_end = 3.0 * 2 * np.pi / omega if t_end is None else float(t_end)
    ex = exact_forced(Gamma, S0, eps, omega, t_end)
    qs = S0 * (1.0 + eps * np.sin(omega * t_end)) / Gamma
    return float(abs(qs - ex) / abs(ex))


def crossover_scan(ratios=(0.3, 1.0, 3.0, 10.0, 30.0, 100.0), Gamma=1e3, z=1.0):
    """★ 언제 명시적 적분 대신 준정적으로 가야 하는가 — **Γ/ω** 로 스캔한다.

    반환 [(Γ/ω, RK4 오차(z 고정), 준정적 오차)].
    ★ 두 오차가 교차하는 지점이 전환 기준이다 (측정으로 제시).
    """
    out = []
    for r in ratios:
        om = Gamma / r
        t_end = 3.0 * 2 * np.pi / om
        ex = exact_forced(Gamma, 1.0, 0.5, om, t_end)
        dt = z / Gamma
        ns = max(1, int(np.ceil(t_end / dt)))
        y = rk4_forced(Gamma, 1.0, 0.5, om, t_end, ns)
        out.append((float(r), float(abs(y - ex) / abs(ex)),
                    quasi_static_error(Gamma, 1.0, 0.5, om, t_end)))
    return out


def constant_source_is_degenerate(Gamma=1e3, zs=(0.01, 0.3, 1.0), t_end=0.05):
    """★ 위 docstring 의 사건을 **시험으로 고정**: 상수 소스면 z 가 무의미하다.

    "발산하지 않았으니 정확하다" 는 판단이 왜 위험한지의 반례이자,
    내가 처음 만든 시험이 왜 아무것도 재지 못했는지의 기록.
    """
    ex = exact_solution(0.0, 1.0, Gamma, t_end)
    return [(float(z), float(abs(rk4_solution(0.0, 1.0, Gamma, t_end,
                                              max(1, int(np.ceil(t_end / (z / Gamma)))))
                                 - ex) / abs(ex))) for z in zs]


# ═══════════════════════════════════════ 4. 감시자 — 조용히 틀리지 않게
class StiffnessWarning(UserWarning):
    """명시적 적분이 Thomson 강성 한계를 넘었을 때."""


def check_step(dt, n_e_sigma_T, H_hubble=0.0, d2=None, safety=0.5, raise_error=False):
    """★ 스텝이 안전한지 **확인하고 경고**한다 (조용히 넘어가지 않는다).

    d2 기본값은 편광 포함 유효 사중극 감쇠 3/4 (V2 에서 측정).
    반환 dict(z, limit, safe).  `raise_error=True` 면 예외를 던진다.
    """
    from bianchi.matter.collision import POLARISED_QUADRUPOLE_DAMPING
    d2 = POLARISED_QUADRUPOLE_DAMPING if d2 is None else float(d2)
    G = 4.0 * float(H_hubble) + d2 * float(n_e_sigma_T)
    lim = RK4_REAL_STABILITY_LIMIT
    z = G * float(dt)
    safe = z <= safety * lim
    if not safe:
        msg = (f"Thomson 강성: Γδt = {z:.3g} > {safety}×{lim:.4g}. "
               f"명시적 RK4 가 부정확·불안정해진다 (δt ≤ {safety*lim/G:.3g} 권장, "
               f"또는 준정적/암묵적으로 전환).")
        if raise_error:
            raise RuntimeError(msg)
        warnings.warn(msg, StiffnessWarning, stacklevel=2)
    return dict(z=z, limit=lim, gamma=G, safe=bool(safe),
                recommended_dt=safety * lim / G)


def literature_constraint(n_e_sigma_T, H_hubble=0.0, d2=None):
    """문헌의 `τ̇ δη ≪ 1` 을 우리 수치로: **δη ≤ 1.39/Γ** (안전계수 0.5).

    d₂ = 3/4 이면 δη ≤ 1.86/τ̇ — 즉 문헌의 "≪ 1" 은 **τ̇δη ≲ 1.9** 를 뜻한다.
    """
    from bianchi.matter.collision import POLARISED_QUADRUPOLE_DAMPING
    d2 = POLARISED_QUADRUPOLE_DAMPING if d2 is None else float(d2)
    G = 4.0 * float(H_hubble) + d2 * float(n_e_sigma_T)
    dt = 0.5 * RK4_REAL_STABILITY_LIMIT / G
    return dict(gamma=G, dt_max=dt,
                tau_dot_times_dt=float(n_e_sigma_T) * dt, d2=d2)
