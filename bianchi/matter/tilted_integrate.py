"""
H5-e3 · tilted 계층의 **시간적분** — M(v)·J̇ = F 를 닫고 RK4 로 굴린다.

법선합동 판(`hierarchy.integrate_hierarchy`)과 두 가지가 다르다:
  1. RHS 가 명시적이지 않다 — 매 스텝 M(v)·J̇ = F 를 **풀어야** 한다 (PSTF 좌표).
  2. 닫힘이 하나 더 필요하다 — tilted 에는 (div-con) 의 **l+1 결합**이 있어서
     l_max 절단이 J^(i)_{A_{l_max+1}} 과 그 J̇ 를 요구한다.

★ 닫힘의 근거를 **가정하지 않고 측정했다** (PLAN-H5d 위험표 항목):

  · `close_i` 의 근거(무질량 i-무관성)가 **boost 후에도 성립**한다:
        m=0 에서 |J′^(i)|/|J′^(0)| = 1.0000 (i=1,2,3, l=0/2/3 전부)
        m=0.5 → 0.967, 0.938, 0.912 ;  m=2 → 0.698, 0.531, 0.423  (기하급수 감쇠)
    ⇒ H2 의 기하외삽을 그대로 쓴다.

  · **l+1 절단오차는 기존 σ 의 l+2 절단보다 약 3배 크다** (측정):
        l=2:  l+1 절단 2.10e−4  vs  l+2(σ) 절단 7.32e−5
        l=3:  l+1 절단 1.64e−4  vs  l+2(σ) 절단 4.50e−5
    ⇒ 같은 정확도를 원하면 tilted 는 l_max 를 조금 더 올려야 한다.  조용히 쓰지 않고
      `truncation_error()` 로 노출한다.

★ 격자 밖 J̇ 의 처리: H5-e2 에서 확인했듯 격자 밖 J̇ 를 **0 으로 버리면** 잔차가
  1.5e−10 → 5.5e−2 로 8자리 나빠진다.  적분에서는 바깥 J̇ 를 알 수 없으므로 0 절단이
  불가피하고, 그 대가가 위 절단오차다 — **이것이 절단오차의 정체**다.

★★ L3 정정 (2026-07-31): "불가피" 가 아니었다.  **J 를 닫으면서 J̇ 만 버린 것이
  결함**이었다 — 닫힘이 J 와 J̇ 사이에서 어긋나 있었다.  같은 비 r 로 J̇ 도 닫으면
  (`jdot_closure=True`, 기본값) 그 오차 채널이 사라진다:

      무질량:  ρ 5.26e−4 → 7.76e−8  (6800배),  q 3.0e−4 → 2.3e−6,  π 8.6e−4 → 1.5e−5
               ★ 값이 `integrate_degenerate` (1차원 환원) 와 **1.8e−18 절대**로 같다
                 — 1차원 환원은 이 J̇ 닫힘의 r=1 특수경우였다.
                 (39차 이전에는 마지막 비트까지 같았다.  `hierarchy.pstf` 를 고정
                  행렬로 굳히면서 대칭화 합의 순서가 바뀌어 동률이 깨졌다 — 이분법으로
                  원인을 확정했고, 물리는 배정밀도 eps 의 1/100 안에서 그대로다.)
      유질량 (i_max=3, ratio 닫힘 병용):
               m=0.5  1.86e−5 → 8.4e−7 (22배)
               m=1    1.18e−5 → 2.6e−6 (4.6배)
               m=2    6.8e−7 → 3.9e−6  (★ 나빠짐 — 기존 값이 부호상쇄로 우연히 좋았다)
               m=4    3.2e−6 → 1.8e−6 (1.8배)

  ⇒ **J 닫힘만 정확하게 만드는 것은 소용없다** (정확 구적을 넣어도 궤적은 그대로).
    한계는 J 값이 아니라 J̇ 였다.  `jdot_closure=False` 로 옛 거동을 재현할 수 있고,
    H5-e3 의 기전 시험들이 그 대조군을 쓴다.
"""
from __future__ import annotations

import numpy as np

from bianchi.backend_policy import BackendPolicy, select_backend
from bianchi.matter import tilted_closure as TC
from bianchi.matter import tilted_equation as TE
from bianchi.matter import tilted_mass as TMass
from bianchi.matter import tilted_moments as TM
from bianchi.matter import tilted_rust as TR
from bianchi.matter import tilted_terms as TT
from bianchi.matter.hierarchy import close_i, pstf


# ═══════════════════════════════════════ 배경 처방
class Background:
    """a(t), v(t) 를 처방한다.

    ★ a(t) 는 **법선** 합동의 (H_n, σ_n) 이 정한다: ȧ_i = (H_n + σ_n,i) a_i.
      v(t) 는 자유롭다 — 어떤 tilted 합동이든 식 (12) 는 성립하므로, 시험에서는
      임의의 매끄러운 v(t) 를 써도 정당하다 (오라클도 같은 v(t) 로 계산한다).
    """

    def __init__(self, a0=(1.0, 0.9, 1.2), H=1.0, sigma_diag=(0.06, -0.02, -0.04),
                 v0=(0.08, -0.05, 0.12), dv=(0.0, 0.0, 0.0)):
        self.a0 = np.asarray(a0, float)
        self.H = float(H)
        self.sig = np.asarray(sigma_diag, float)
        self.v0 = np.asarray(v0, float)
        self.dv = np.asarray(dv, float)

    def a(self, t):
        return self.a0 * np.exp((self.H + self.sig) * t)

    def da(self, t):
        return (self.H + self.sig) * self.a(t)

    def v(self, t):
        return self.v0 + self.dv * t

    def geometry(self, t):
        return TT.geometry(self.a(t), self.da(t), self.v(t), self.dv)


# ═══════════════════════════════════════ 닫힘
def closure(J, l_max, i_max, mode="ratio", n_star=None):
    """격자를 방정식이 요구하는 이웃까지 채운다.

    · i 위쪽: 기하외삽.  `mode="frozen"` 은 기존 `hierarchy.close_i` (비를 얼림),
      `mode="ratio"` 는 L3 의 **(1−r) 기하외삽** (`tilted_closure`).
      유질량에서 후자가 낫다 (닫힘 예측오차 3–8배, 궤적오차는 `mode_comparison` 참조).
      무질량에서는 둘이 **정확히 같다** (r ≡ 1).
    · l 위쪽: **0 절단** (l_max+1, l_max+2).  대가는 측정된 절단오차.
    """
    if n_star is not None:                       # ★ L1: 삼각 절단 (원논문 체계)
        out = dict(J)
        for l in range(l_max + 3):
            for i in range(-1, i_max + 3):
                if (l, i) in out and l + 2 * i <= n_star:
                    continue
                out[(l, i)] = 0.0 if l == 0 else np.zeros((3,) * l)
        return out
    out = dict(J)
    if mode == "frozen":
        for l in range(l_max + 1):
            close_i(out, l, i_max)
    else:
        for l in range(l_max + 1):
            TC.close_i(out, l, i_max, mode)
    for l in (l_max + 1, l_max + 2):
        for i in range(-1, i_max + 3):
            out[(l, i)] = np.zeros((3,) * l)
    return out


def initial_state(bg, mass, l_max, i_max, t=0.0, backend=None):
    """t=0 의 정확 구적 초기조건 (tilted 사틀 성분)."""
    a, v = bg.a(t), bg.v(t)
    return {(l, i): np.atleast_1d(np.asarray(
        TM.J_moment_tilted(a, v, mass, l, i, backend=backend), float)
    ).reshape((3,) * l)
        for l in range(l_max + 1) for i in range(-1, i_max + 1)}


# ═══════════════════════════════════════ RHS (질량행렬 해)
def rhs(J, bg, t, l_max, i_max, signs=None, mode="ratio", jdot_closure=True,
        n_star=None, backend=None):
    """J̇ = M⁻¹F — 매 스텝 PSTF 좌표에서 선형해.

    `jdot_closure=True` 면 (div-free) 가 요구하는 **격자 밖 J̇** 을 버리지 않고
    J 닫힘과 같은 비로 닫는다 (`tilted_closure.jdot_ratio`).  L3 의 핵심 개선.
    """
    geo = bg.geometry(t)
    Jc = closure(J, l_max, i_max, mode, n_star)
    zero = {k: np.zeros(np.asarray(Jc[k]).shape) for k in Jc}
    F = {(l, i): -np.asarray(
        TE.equation_lhs(Jc, zero, geo, l, i, signs, backend=backend), float
    )
         for l in range(l_max + 1) for i in range(i_max + 1)}
    ir = (TC.jdot_ratio(Jc, l_max, i_max, mode)
          if (jdot_closure and n_star is None) else None)
    return TMass.solve(F, geo, l_max, i_max, signs, ir, n_star)


def rust_available(mode="ratio", jdot_closure=True, n_star=None):
    """★ R5b: Rust 계층 커널이 **이 설정에서** 쓸 수 있는가.

    ★ 처음에는 기본 경로만 포트했다가 계수를 세어 보고 뒤집었다: tilted 시험 1260
      적분스텝 중 기본 경로는 **310 스텝(25%)** 뿐이고 나머지는 전부 대조군이었다.
      대조군을 Python 에 남기면 벽시계가 그대로여서 `tilted_closure.MODES` 전부와
      J̇ 닫힘 on/off, 삼각절단까지 옮겼다.
    """
    return bool(TR.available(mode))


def integrate(bg, mass, t_end, nsteps=40, l_max=3, i_max=1, signs=None,
              mode="ratio", jdot_closure=True, n_star=None, backend=None):
    """RK4 적분 → dict(t, J[(l,i)] 이력).

    ★ i = −1 성분은 상태가 아니다 (방정식이 i=0 에서 J^(−1) 을 참조하지 않는다:
      계수 (l−n) = −2i 가 0 이므로).  닫힘이 매 스텝 다시 채운다.

    ★ R5b: 기본 경로면 Rust 커널이 루프 전체를 돌린다.  `backend="python"` 이
      오라클로 남아 있다 (차등시험이 이걸 쓴다).
    """
    policy = BackendPolicy.PYTHON_ORACLE if backend == "python" else backend
    selected = select_backend("tilted.integrate", policy=policy, mode=mode)
    child_backend = (BackendPolicy.RUST_REQUIRED if selected.uses_rust
                     else BackendPolicy.PYTHON_ORACLE)
    keys, _, _ = TMass.layout(l_max, i_max, n_star)
    J = {k: v for k, v in initial_state(
        bg, mass, l_max, i_max, backend=child_backend
    ).items()
         if k in keys}
    dt = t_end / nsteps
    if selected.uses_rust:
        ts, js = TR.integrate(bg, J, t_end, nsteps, l_max, i_max, signs, mode,
                              jdot_closure, n_star, set(keys),
                              _native_module=selected.native_module)
        return {"t": ts, "J": js}
    hist = {"t": [0.0], "J": [dict(J)]}

    def axpy(base, d, c):
        return {k: base[k] + c * np.asarray(d[k], float) for k in keys}

    for step in range(nsteps):
        t = step * dt
        jc = jdot_closure
        k1 = rhs(J, bg, t, l_max, i_max, signs, mode, jc, n_star,
                 backend=child_backend)
        k2 = rhs(axpy(J, k1, 0.5 * dt), bg, t + 0.5 * dt, l_max, i_max,
                 signs, mode, jc, n_star, backend=child_backend)
        k3 = rhs(axpy(J, k2, 0.5 * dt), bg, t + 0.5 * dt, l_max, i_max,
                 signs, mode, jc, n_star, backend=child_backend)
        k4 = rhs(axpy(J, k3, dt), bg, t + dt, l_max, i_max,
                 signs, mode, jc, n_star, backend=child_backend)
        J = {k: J[k] + dt / 6.0 * (np.asarray(k1[k], float)
                                   + 2 * np.asarray(k2[k], float)
                                   + 2 * np.asarray(k3[k], float)
                                   + np.asarray(k4[k], float)) for k in keys}
        hist["t"].append(t + dt)
        hist["J"].append(dict(J))
    return hist


# ═══════════════════════════════════════ 게이트·진단
def trajectory_error(bg, mass, t_end=0.2, nsteps=40, l_max=3, i_max=1,
                     mode="ratio", jdot_closure=True, n_star=None, backend=None):
    """★ 궤적을 **정확 구적**과 대조 — H2 가 법선합동에 쓴 것과 같은 종단 게이트.

    반환 dict(rho, q, pi) — 각각 |적분 − 정확|/ρ′(T).
    """
    policy = BackendPolicy.PYTHON_ORACLE if backend == "python" else backend
    selected = select_backend("tilted.trajectory_error", policy=policy, mode=mode)
    child_backend = (BackendPolicy.RUST_REQUIRED if selected.uses_rust
                     else BackendPolicy.PYTHON_ORACLE)
    hist = integrate(bg, mass, t_end, nsteps, l_max, i_max, mode=mode,
                     jdot_closure=jdot_closure, n_star=n_star,
                     backend=child_backend)
    T = hist["t"][-1]
    J = hist["J"][-1]
    aT, vT = bg.a(T), bg.v(T)
    rho_e = TM.J_moment_tilted(aT, vT, mass, 0, 0, backend=child_backend)
    out = {}
    for name, (l, i) in (("rho", (0, 0)), ("q", (1, 0)), ("pi", (2, 0))):
        if l > l_max:
            continue
        ex = np.atleast_1d(np.asarray(
            TM.J_moment_tilted(aT, vT, mass, l, i, backend=child_backend), float
        ))
        got = np.atleast_1d(np.asarray(J[(l, i)], float)).ravel()
        out[name] = float(np.abs(got - ex.ravel()).max() / rho_e)
    return out


def truncation_error(mass=0.0, a_vec=(1.0, 0.9, 1.2), da_vec=(0.35, 0.28, 0.42),
                     v=(0.08, -0.05, 0.12), dv=(0.015, 0.01, -0.02), l=2, dt=1e-5):
    """★ tilted 의 **l+1 절단오차**를 기존 σ 의 l+2 절단과 나란히 보고한다.

    반환 dict(exact, trunc_l_plus_1, trunc_l_plus_2_sigma, ratio).
    조용히 쓰지 않기 위한 진단 — 측정: l+1 이 l+2(σ) 보다 약 3배 크다.
    """
    from audit import h5d_tilted_residual as R
    geo = TT.geometry(a_vec, da_vec, v, dv)
    J = R.moment_grid(a_vec, v, mass)
    dJ = R.moment_grid_dot(a_vec, da_vec, v, dv, mass, dt)
    rho = float(J[(0, 0)])

    def worst(Jx, dJx):
        return float(np.abs(np.atleast_1d(np.asarray(
            TE.equation_lhs(Jx, dJx, geo, l, 0), float))).max() / rho)

    ex = worst(J, dJ)
    J1, d1 = dict(J), dict(dJ)
    J1[(l + 1, 0)] = np.zeros((3,) * (l + 1))
    d1[(l + 1, 0)] = np.zeros((3,) * (l + 1))
    t1 = worst(J1, d1)
    J2 = dict(J)
    J2[(l + 2, 0)] = np.zeros((3,) * (l + 2))
    J2[(l + 2, -1)] = np.zeros((3,) * (l + 2))
    t2 = worst(J2, dJ)
    return dict(exact=ex, trunc_l_plus_1=t1, trunc_l_plus_2_sigma=t2,
                ratio=t1 / max(t2, 1e-300))


def i_independence_ratios(mass, a_vec=(1.0, 0.9, 1.2), v=(0.08, -0.05, 0.12),
                          l=0, i_max=3):
    """★ `close_i` 의 근거 확인: |J′^(i)|/|J′^(0)| (무질량이면 1, 유질량이면 감쇠)."""
    base = np.atleast_1d(np.asarray(TM.J_moment_tilted(a_vec, v, mass, l, 0), float))
    s = max(np.abs(base).max(), 1e-300)
    return [float(np.abs(np.atleast_1d(np.asarray(
        TM.J_moment_tilted(a_vec, v, mass, l, i), float))).max() / s)
        for i in range(1, i_max + 1)]


# ═══════════════════════════════════════ 무질량 1차원 환원 (문헌 근거)
#
# Lewis & Challinor (astro-ph/0203507) §"For massless particles":
#   "For massless particles E=λ and the velocity-weighted moments are identical,
#    J^(i)_{A_l} = J^(i')_{A_l}.  The momentum-integrated equations then reduce to
#    the usual one-dimensional Boltzmann hierarchy."
#
# ★ 왜 이게 중요한가 (측정으로 확인한 기전):
#   무질량 초기조건은 i-무관성을 4e−16 로 만족하지만, 2차원 격자를 **독립적으로**
#   적분하면 i_max 절단이 i 마다 다르게 되먹임되어 t=T 에서 그 축퇴가 5.5e−2 까지
#   깨진다 (궤적오차 1e−4 보다 크다).  즉 지배 오차의 정체는 "i-닫힘 부정확" 이 아니라
#   **정확한 축퇴를 수치적으로 깨뜨리는 것**이었다.
#   ⇒ 축퇴를 **강제**하면(1차원 환원) 그 오차 채널이 통째로 사라진다.
def rhs_degenerate(J1, bg, t, l_max, signs=None):
    """무질량 1차원 환원의 J̇ — 상태는 J_l ≡ J^(0)_{A_l} 뿐.

    방정식이 요구하는 모든 J^(i) 에 같은 J_l 을 공급한다 (무질량에서 **정확**).
    질량행렬 블록도 i 지표가 접힌다:
        M[l ← l]   = γ·P
        M[l ← l+1] = s_dc·γ·P∘(v 축약)
        M[l ← l−1] = s_df·(−l/(2l+1))·γ·P∘(·⊗v)
    """
    geo = bg.geometry(t)
    gam, v = TMass.gamma_and_v(geo)
    s = TMass.SIGNS if signs is None else signs
    # 모든 i 에 같은 값을 공급 (l+1, l+2 는 0 절단)
    Jfull = {}
    for l in range(l_max + 3):
        val = J1[l] if l <= l_max else np.zeros((3,) * l)
        for i in range(-1, l_max + 4):
            Jfull[(l, i)] = val
    zero = {k: np.zeros(np.asarray(Jfull[k]).shape) for k in Jfull}
    F = [-np.asarray(TE.equation_lhs(Jfull, zero, geo, l, 0, signs), float)
         for l in range(l_max + 1)]

    # 축소 질량행렬을 2l+1 PSTF 좌표에서 조립 (i 지표 접힘)
    off, n = [], 0
    for l in range(l_max + 1):
        off.append(n)
        n += 2 * l + 1

    def apply(x):
        blocks = [TMass.to_tensor(x[off[l]:off[l] + 2 * l + 1], l)
                  for l in range(l_max + 1)]
        out = np.zeros(n)
        for l in range(l_max + 1):
            acc = gam * np.asarray(blocks[l], float)
            if l + 1 <= l_max:
                acc = acc + s["divcon"] * gam * np.tensordot(
                    np.asarray(blocks[l + 1], float), v, axes=([0], [0]))
            if l >= 1:
                tt = np.multiply.outer(np.asarray(blocks[l - 1], float), v)
                acc = acc + s["divfree"] * (-l / (2.0 * l + 1.0)) * gam * \
                    (pstf(tt) if l >= 2 else tt)
            acc = pstf(acc) if l >= 2 else acc
            out[off[l]:off[l] + 2 * l + 1] = TMass.to_coef(acc, l)
        return out

    M = np.zeros((n, n))
    for c in range(n):
        e = np.zeros(n)
        e[c] = 1.0
        M[:, c] = apply(e)
    b = np.concatenate([TMass.to_coef(F[l], l) for l in range(l_max + 1)])
    x = np.linalg.solve(M, b)
    return [TMass.to_tensor(x[off[l]:off[l] + 2 * l + 1], l)
            for l in range(l_max + 1)]


def integrate_degenerate(bg, t_end, nsteps=20, l_max=3, signs=None):
    """무질량 1차원 환원의 RK4 적분 (질량 인자가 없다 — 무질량 전용)."""
    a, v = bg.a(0.0), bg.v(0.0)
    J = [np.atleast_1d(np.asarray(TM.J_moment_tilted(a, v, 0.0, l, 0), float)
                       ).reshape((3,) * l) for l in range(l_max + 1)]
    dt = t_end / nsteps
    for step in range(nsteps):
        t = step * dt
        k1 = rhs_degenerate(J, bg, t, l_max, signs)
        k2 = rhs_degenerate([J[l] + 0.5 * dt * k1[l] for l in range(l_max + 1)],
                            bg, t + 0.5 * dt, l_max, signs)
        k3 = rhs_degenerate([J[l] + 0.5 * dt * k2[l] for l in range(l_max + 1)],
                            bg, t + 0.5 * dt, l_max, signs)
        k4 = rhs_degenerate([J[l] + dt * k3[l] for l in range(l_max + 1)],
                            bg, t + dt, l_max, signs)
        J = [J[l] + dt / 6.0 * (k1[l] + 2 * k2[l] + 2 * k3[l] + k4[l])
             for l in range(l_max + 1)]
    return {"t": t_end, "J": J}


def degeneracy_violation(bg, t_end=0.2, nsteps=20, l_max=2, i_max=1,
                         mode="ratio", jdot_closure=True):
    """★ 2차원 적분이 무질량 축퇴 J^(i)=J^(0) 를 얼마나 깨뜨리는지 (기전 진단).

    ★ V3 (상시 감시자): 기본값(J̇ 닫힘)에서는 위반이 기계정밀도에 머문다.
      `jdot_closure=False` 로 옛 거동(2.2e−1 까지 깨짐)을 재현할 수 있다.
    """
    h = integrate(bg, 0.0, t_end, nsteps, l_max, i_max, mode=mode,
                  jdot_closure=jdot_closure)
    out = {}
    for tag, J in (("t0", h["J"][0]), ("tT", h["J"][-1])):
        w = 0.0
        for l in range(l_max + 1):
            b = np.atleast_1d(np.asarray(J[(l, 0)], float))
            sc = max(np.abs(b).max(), 1e-300)
            for i in range(1, i_max + 1):
                w = max(w, float(np.abs(np.atleast_1d(
                    np.asarray(J[(l, i)], float)) - b).max() / sc))
        out[tag] = w
    return out


def trajectory_error_degenerate(bg, t_end=0.2, nsteps=20, l_max=3):
    """1차원 환원 궤적을 정확 구적과 대조 (무질량)."""
    r = integrate_degenerate(bg, t_end, nsteps, l_max)
    aT, vT = bg.a(t_end), bg.v(t_end)
    rho_e = TM.J_moment_tilted(aT, vT, 0.0, 0, 0)
    out = {}
    for name, l in (("rho", 0), ("q", 1), ("pi", 2)):
        if l > l_max:
            continue
        ex = np.atleast_1d(np.asarray(TM.J_moment_tilted(aT, vT, 0.0, l, 0), float))
        out[name] = float(np.abs(np.atleast_1d(np.asarray(r["J"][l], float)).ravel()
                                 - ex.ravel()).max() / rho_e)
    return out


# ═══════════════════════════════════════ L3 진단: 닫힘 조합 비교
def mode_comparison(bg=None, masses=(0.0, 0.5, 1.0, 2.0, 4.0), t_end=0.2,
                    nsteps=20, l_max=3, i_max=3):
    """★ (J 닫힘 모드) × (J̇ 닫힘 on/off) 궤적오차 표.

    개선을 **주장하지 않고 표로 보인다** — 어디서 좋아지고 어디서 나빠지는지까지.
    """
    bg = Background() if bg is None else bg
    rows = []
    for m in masses:
        for mode in ("frozen", "ratio"):
            for jc in (False, True):
                rows.append((m, mode, jc,
                             trajectory_error(bg, m, t_end, nsteps, l_max, i_max,
                                              mode=mode, jdot_closure=jc)))
    return rows


def jdot_closure_reproduces_1d_reduction(bg=None, t_end=0.2, nsteps=20, l_max=3,
                                         i_max=1):
    """★★ 무질량에서 J̇ 닫힘(r=1)이 **1차원 환원과 같은 답**임을 확인한다.

    두 경로는 코드가 전혀 다르다: 하나는 2차원 격자 + 닫힘, 다른 하나는 상태를
    J_l 하나로 접은 축소계.  일치는 "1차원 환원 = J̇ 닫힘의 r=1 특수경우" 를 뜻한다.
    """
    bg = Background() if bg is None else bg
    a = trajectory_error_degenerate(bg, t_end, nsteps, l_max)
    b = trajectory_error(bg, 0.0, t_end, nsteps, l_max, i_max, jdot_closure=True)
    return dict(reduction=a, jdot=b,
                gap=max(abs(a[k] - b[k]) / max(a[k], 1e-300) for k in a))


def oracle_closure_experiment(bg=None, mass=1.0, t_end=0.2, nsteps=10, l_max=2,
                              i_max=2):
    """★★ **반증 실험**: 격자 밖 J 를 *정확 구적*으로 채우면 궤적이 좋아지는가?

    반환 dict(baseline, exact_J, jdot) — 셋 다 같은 격자·같은 스텝.
    측정 결과는 "아니오" 다: `exact_J` 가 `baseline` 과 같은 자릿수에 머문다.
    좋아지는 것은 **J̇ 를 닫았을 때**(`jdot`)뿐이다.
    ⇒ 절단오차의 정체는 J 값이 아니라 **버려진 J̇** 이다.
    """
    bg = Background() if bg is None else bg
    keys, _, _ = TMass.layout(l_max, i_max)

    def run(kind):
        J = {k: v for k, v in initial_state(bg, mass, l_max, i_max).items()
             if k in keys}
        dt = t_end / nsteps

        def step_rhs(Jx, t):
            if kind != "exact_J":
                return rhs(Jx, bg, t, l_max, i_max, None, "frozen",
                           kind == "jdot")
            geo = bg.geometry(t)
            a, v = bg.a(t), bg.v(t)
            Jc = dict(Jx)
            for l in range(l_max + 3):
                for i in range(-1, i_max + 3):
                    if l <= l_max and i <= i_max and (l, i) in Jx:
                        continue
                    Jc[(l, i)] = np.atleast_1d(np.asarray(
                        TM.J_moment_tilted(a, v, mass, l, i), float)
                    ).reshape((3,) * l)
            zero = {k: np.zeros(np.asarray(Jc[k]).shape) for k in Jc}
            F = {(l, i): -np.asarray(TE.equation_lhs(Jc, zero, geo, l, i), float)
                 for l in range(l_max + 1) for i in range(i_max + 1)}
            return TMass.solve(F, geo, l_max, i_max)

        for s in range(nsteps):
            t = s * dt

            def ax(b, d, c):
                return {k: b[k] + c * np.asarray(d[k], float) for k in keys}

            k1 = step_rhs(J, t)
            k2 = step_rhs(ax(J, k1, 0.5 * dt), t + 0.5 * dt)
            k3 = step_rhs(ax(J, k2, 0.5 * dt), t + 0.5 * dt)
            k4 = step_rhs(ax(J, k3, dt), t + dt)
            J = {k: J[k] + dt / 6.0 * (np.asarray(k1[k], float)
                                       + 2 * np.asarray(k2[k], float)
                                       + 2 * np.asarray(k3[k], float)
                                       + np.asarray(k4[k], float)) for k in keys}
        aT, vT = bg.a(t_end), bg.v(t_end)
        rho = TM.J_moment_tilted(aT, vT, mass, 0, 0)
        out = {}
        for nm, (l, i) in (("rho", (0, 0)), ("q", (1, 0)), ("pi", (2, 0))):
            ex = np.atleast_1d(np.asarray(
                TM.J_moment_tilted(aT, vT, mass, l, i), float))
            out[nm] = float(np.abs(np.atleast_1d(np.asarray(J[(l, i)], float)
                                                 ).ravel() - ex.ravel()).max() / rho)
        return out

    return dict(baseline=run("baseline"), exact_J=run("exact_J"), jdot=run("jdot"))
