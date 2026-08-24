"""
K4 · **type V 자유흐름 특성곡선** — tilt 결합의 선행조건.

★ 왜 필요한가 (K2b 의 no-go):
  Codazzi 구속 `C^a = 3A_bΣ^{ab} + ε^{abc}N_{bd}Σ_c{}^d − q^a = 0` 이 Bianchi I 에서
  q = 0 을 강제한다.  대각 N·Σ 이면 class A 전체가 그렇다.  tilt 를 담으려면
  **A ≠ 0 (class B, 최소 type V)** 이어야 하고, 동시에 **Σ ≠ 0** 이어야 한다
  (등방 type V 는 용량이 다시 0 이다).

★ 그런데 type V 에서는 **불변기저 운동량이 보존되지 않는다** — type I 정확 구적의
  근거(p_i = const)가 사라진다.  구조상수 C²₁₂ = C³₁₃ = A 때문에

      ṗ₁ = (A/E)(p₂p² + p₃p³),   ṗ₂ = −(A/E)p¹p₂,   ṗ₃ = −(A/E)p¹p₃
      p^i = p_i/a_i²,   E = √(m² + Σ p_i p^i)

  로 결합한다.  ⇒ 자유흐름 해를 **특성곡선 적분**으로 다시 구해야 한다.

★ 정직한 한계 (미리 적어 둔다): 이 오라클은 type I 처럼 닫힌형이 아니다.
  일반 a_i(t) 에서는 닫힌 해가 없다 (축대칭에서도 a₁²/b² 가 시간의존이라 안 닫힌다).
  정확도가 **ODE 솔버에 걸린다** — `solver_accuracy()` 로 그 한계를 측정해 노출한다.

★ 검증은 언제나처럼 두 경로 + 보존량:
  경로 A — 구조상수 공식 (`characteristic_rhs`)
  경로 B — 명시적 계량에서 **기호 측지선** (`symbolic_rhs`), 좌표 → 불변기저 변환
  보존량 게이트 4종 — §3 참조.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from bianchi.backend_policy import BackendPolicy, select_backend

# ═══════════════════════════════════════ 1. 경로 A — 구조상수
def characteristic_rhs(p, a_vec, mass, A):
    """ṗ_i (불변기저 공변성분), type V 구조상수 C²₁₂ = C³₁₃ = A.

    ★ 부호는 유도를 믿지 않고 `symbolic_rhs` 와 대조해 확정한다 (경로 B).
    """
    p = np.asarray(p, float)
    a = np.asarray(a_vec, float)
    pu = p / a ** 2                                   # p^i
    E = np.sqrt(mass ** 2 + float(p @ pu))
    return np.array([A * (p[1] * pu[1] + p[2] * pu[2]),
                     -A * pu[0] * p[1],
                     -A * pu[0] * p[2]]) / E


def energy(p, a_vec, mass):
    p = np.asarray(p, float)
    a = np.asarray(a_vec, float)
    return float(np.sqrt(mass ** 2 + float(p @ (p / a ** 2))))


# ═══════════════════════════════════════ 2. 경로 B — 기호 측지선 (독립)
@lru_cache(maxsize=4)
def _symbolic_geodesic():
    """계량 ds² = −dt² + a₁²dx² + e^{2Ax}(a₂²dy² + a₃²dz²) 에서 측지선을 **기호로**.

        dp_μ/dλ = ½ ∂_μ g_{αβ} p^α p^β

    y, z 는 순환좌표라 p_y, p_z 가 보존된다 (Killing).  p_x 만 소스가 있다.
    반환 lambdify 된 dp_x/dλ (좌표 성분).
    """
    import sympy as sp
    t, x, A = sp.symbols("t x A", real=True)
    a1, a2, a3 = sp.symbols("a1 a2 a3", positive=True)
    px, py, pz, pt = sp.symbols("p_x p_y p_z p_t", real=True)
    g = sp.diag(-1, a1 ** 2, sp.exp(2 * A * x) * a2 ** 2, sp.exp(2 * A * x) * a3 ** 2)
    ginv = g.inv()
    pl = sp.Matrix([pt, px, py, pz])
    pu = ginv * pl
    # dp_x/dλ = ½ ∂_x g_{αβ} p^α p^β
    dgx = sp.diff(g, x)
    expr = sp.simplify(sum(dgx[i, i] * pu[i] ** 2 for i in range(4)) / 2)
    return sp.lambdify((A, x, a1, a2, a3, px, py, pz, pt), expr, "numpy"), expr


def symbolic_rhs(p, a_vec, mass, A, x=0.0):
    """★ 경로 B — 기호 측지선에서 얻은 ṗ_i (불변기저).

    좌표 ↔ 불변기저:  p₁ = p_x,  p₂ = e^{−Ax}p_y,  p₃ = e^{−Ax}p_z.
    ⇒ ṗ₁ = dp_x/dλ / E,   ṗ₂ = −A(dx/dt)p₂,  dx/dt = p^x/E = p₁/(a₁²E).
    """
    fn, _ = _symbolic_geodesic()
    p = np.asarray(p, float)
    a = np.asarray(a_vec, float)
    E = energy(p, a, mass)
    py, pz = np.exp(A * x) * p[1], np.exp(A * x) * p[2]
    dpx = float(fn(A, x, a[0], a[1], a[2], p[0], py, pz, -E))
    dxdt = p[0] / (a[0] ** 2 * E)
    return np.array([dpx / E, -A * dxdt * p[1], -A * dxdt * p[2]])


def route_residual(p=(0.7, -0.4, 0.55), a_vec=(1.0, 0.85, 1.18), mass=0.6, A=0.7,
                   x=0.0):
    """★★ 두 경로 대조 — 구조상수 조립 vs 기호 측지선."""
    ra = characteristic_rhs(p, a_vec, mass, A)
    rb = symbolic_rhs(p, a_vec, mass, A, x)
    sc = max(np.abs(ra).max(), 1e-300)
    return dict(route_a=ra, route_b=rb, residual=float(np.abs(ra - rb).max() / sc))


# ═══════════════════════════════════════ 3. 특성곡선 적분
class Background:
    """type V 배경 — a_i(t) = a_i(0)exp((H+σ_i)t),  A = const."""

    def __init__(self, a0=(1.0, 0.85, 1.18), H=1.0, sigma_diag=(0.06, -0.02, -0.04),
                 A=0.7):
        self.a0 = np.asarray(a0, float)
        self.H = float(H)
        self.sig = np.asarray(sigma_diag, float)
        self.A = float(A)

    def a(self, t):
        return self.a0 * np.exp((self.H + self.sig) * t)


def evolve(p0, bg, mass, t_end, nsteps=200, track_x=False, x0=0.0):
    """RK4 로 특성곡선을 적분한다.  `track_x` 면 좌표 x 도 함께 (Killing 게이트용).

    ★ dx/dt = p^x/E = p₁/(a₁²E).
    """
    p = np.asarray(p0, float).copy()
    x = float(x0)
    dt = t_end / nsteps

    def f(pv, xv, t):
        a = bg.a(t)
        dp = characteristic_rhs(pv, a, mass, bg.A)
        dx = pv[0] / (a[0] ** 2 * energy(pv, a, mass))
        return dp, dx

    for k in range(nsteps):
        t = k * dt
        k1p, k1x = f(p, x, t)
        k2p, k2x = f(p + 0.5 * dt * k1p, x + 0.5 * dt * k1x, t + 0.5 * dt)
        k3p, k3x = f(p + 0.5 * dt * k2p, x + 0.5 * dt * k2x, t + 0.5 * dt)
        k4p, k4x = f(p + dt * k3p, x + dt * k3x, t + dt)
        p = p + dt / 6.0 * (k1p + 2 * k2p + 2 * k3p + k4p)
        x = x + dt / 6.0 * (k1x + 2 * k2x + 2 * k3x + k4x)
    return (p, x) if track_x else p


# ═══════════════════════════════════════ 4. ★ 보존량 게이트
def type_I_reduction_residual(p0=(0.7, -0.4, 0.55), mass=0.6, t_end=0.5, nsteps=50):
    """★ A → 0 이면 p_i 가 **정확히 상수** (type I 로 환원) — 비트 수준."""
    bg = Background(A=0.0)
    p = evolve(p0, bg, mass, t_end, nsteps)
    return float(np.abs(p - np.asarray(p0, float)).max())


def p2_over_p3_residual(p0=(0.7, -0.4, 0.55), mass=0.6, A=0.7, t_end=0.5, nsteps=200):
    """★ ṗ₂/p₂ = ṗ₃/p₃ 이므로 **p₂/p₃ 가 보존**된다 (구조에서 곧바로 나온다)."""
    bg = Background(A=A)
    p = evolve(p0, bg, mass, t_end, nsteps)
    r0 = p0[1] / p0[2]
    return float(abs(p[1] / p[2] - r0) / abs(r0))


def isotropic_invariant_residual(p0=(0.7, -0.4, 0.55), mass=0.6, A=0.7, t_end=0.5,
                                 nsteps=200):
    """★★ **등방 a_i 에서 Σp_i² 가 보존**된다 (이방이면 안 된다).

    d(Σp_i²)/dt = 2(A/E)p₁[p₂²(1/a₂²−1/a₁²) + p₃²(1/a₃²−1/a₁²)] 이므로
    a₁=a₂=a₃ 에서만 0 이다.  즉 open FRW 극한에서 |p| = const, λ = |p|/a ∝ 1/a
    라는 잘 아는 사실 — 이것이 특성곡선 방정식의 **독립 검산**이다.
    """
    bg = Background(a0=(1.0, 1.0, 1.0), sigma_diag=(0.0, 0.0, 0.0), A=A)
    p = evolve(p0, bg, mass, t_end, nsteps)
    n0 = float(np.asarray(p0, float) @ np.asarray(p0, float))
    return float(abs(float(p @ p) - n0) / n0)


def anisotropic_invariant_is_broken(p0=(0.7, -0.4, 0.55), mass=0.6, A=0.7,
                                    t_end=0.5, nsteps=200):
    """★ 대조군: 이방이면 Σp_i² 가 **깨져야** 한다 (위 게이트가 죽지 않았음을 보인다)."""
    bg = Background(A=A)
    p = evolve(p0, bg, mass, t_end, nsteps)
    n0 = float(np.asarray(p0, float) @ np.asarray(p0, float))
    return float(abs(float(p @ p) - n0) / n0)


def killing_momentum_residual(p0=(0.7, -0.4, 0.55), mass=0.6, A=0.7, t_end=0.5,
                              nsteps=400):
    """★★ **독립 게이트**: 좌표 그림의 Killing 운동량 p_y = e^{Ax}p₂, p_z = e^{Ax}p₃
    가 보존된다 (y, z 가 순환좌표).

    불변기저 ODE 를 전혀 안 쓰는 사실이라, 이것이 맞으면 특성곡선이 옳다.
    """
    bg = Background(A=A)
    p, x = evolve(p0, bg, mass, t_end, nsteps, track_x=True)
    py0, pz0 = p0[1], p0[2]                            # x(0) = 0
    py, pz = np.exp(A * x) * p[1], np.exp(A * x) * p[2]
    return dict(py=float(abs(py - py0) / abs(py0)),
                pz=float(abs(pz - pz0) / abs(pz0)), x_final=float(x))


def solver_accuracy(p0=(0.7, -0.4, 0.55), mass=0.6, A=0.7, t_end=0.5,
                    steps=(25, 50, 100, 200, 400)):
    """★ **정직한 한계 노출**: 이 오라클의 정확도는 ODE 솔버가 정한다.

    스텝 수를 올리며 Killing 보존 잔차를 재서 수렴차수를 보고한다 (RK4 → 4차 기대).
    """
    out = []
    for n in steps:
        r = killing_momentum_residual(p0, mass, A, t_end, n)
        out.append((int(n), max(r["py"], r["pz"])))
    return out


# ═══════════════════════════════════════ 5. K4b — 모멘트 구적 (역방향 특성곡선)
#
# ★ 측도의 함정 (측정으로 확인): 불변기저 측도 d³p 는 **보존되지 않는다**.
#       ∂ṗ_i/∂p_i = −2A p¹/E ≠ 0
#   (좌표 측도 d³p_coord 는 보존되고 d³p_inv = e^{−2Ax}d³p_coord 이라 정합한다.)
#   ⇒ 순방향으로 입자를 밀며 야코비안을 따라다니면 오차가 쌓인다.
#
# ★ 그래서 **역방향 특성곡선**을 쓴다: 시각 t 의 구적 격자점마다 t=0 으로 거슬러
#   올라가 f₀ 를 읽는다.  f 가 특성곡선을 따라 상수이므로 야코비안이 **전혀 필요 없다**.
#   격자는 t 에서 고정이고, 측도는 type I 과 같은 d³P = d³p/V 를 그대로 쓴다.
def characteristic_rhs_vec(P, a_vec, mass, A):
    """`characteristic_rhs` 의 벡터판 — P shape (N, 3)."""
    P = np.asarray(P, float)
    a = np.asarray(a_vec, float)
    PU = P / a ** 2
    E = np.sqrt(mass ** 2 + np.einsum("ni,ni->n", P, PU))
    out = np.empty_like(P)
    out[:, 0] = A * (P[:, 1] * PU[:, 1] + P[:, 2] * PU[:, 2])
    out[:, 1] = -A * PU[:, 0] * P[:, 1]
    out[:, 2] = -A * PU[:, 0] * P[:, 2]
    return out / E[:, None]


def back_trace(P_t, bg, mass, t, nsteps=64, backend=None):
    """시각 t 의 운동량 P_t 를 t=0 까지 **거슬러** 적분한다 (RK4, 음의 스텝).

    ★ R2: 배경이 처방형 `Background` 면 Rust 커널로 간다 (`backend="python"` 으로 강제).
      두 경로는 차등테스트로 대조한다 — 포트는 빠르게만 할 뿐 정확해지지 않는다.
    """
    policy = BackendPolicy.PYTHON_ORACLE if backend == "python" else backend
    selected = select_backend(
        "type_v.back_trace",
        policy=policy,
        builtin_background=type(bg) is Background,
    )
    if selected.uses_rust:
        rc = selected.native_module
        assert rc is not None
        return np.asarray(rc.tv_back_trace(
            np.ascontiguousarray(np.asarray(P_t, float)), bg.a0,
            bg.H + bg.sig, float(mass), float(bg.A), float(t), int(nsteps)))
    P = np.asarray(P_t, float).copy()
    dt = -t / nsteps
    for k in range(nsteps):
        s = t + k * dt

        def f(Q, u):
            return characteristic_rhs_vec(Q, bg.a(u), mass, bg.A)

        k1 = f(P, s)
        k2 = f(P + 0.5 * dt * k1, s + 0.5 * dt)
        k3 = f(P + 0.5 * dt * k2, s + 0.5 * dt)
        k4 = f(P + dt * k3, s + dt)
        P = P + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
    return P


def moments_type_V(bg, mass, t, l_max=2, i_max=1, f0=None, nsteps=64):
    """★★ type V 자유흐름 모멘트 J^(i)_{A_l}(t) — 역방향 특성곡선 구적.

    측도는 type I 과 동일: d³P = d³p/V,  P^î = p_i/a_i (정규직교 성분).
    `f0` 는 t=0 의 불변기저 분포 f₀(p_i) — 기본값은 |p| 의 페르미-디랙.
    """
    from bianchi.matter import freestream as fs
    a = bg.a(t)
    V = float(np.prod(a))
    Q, DQ, NH, WA = fs._Q, fs._DQ, fs._NHAT, fs._WANG
    # 시각 t 의 격자: 불변기저 공변성분 p_i = q n̂_i (구면 격자를 p-공간에 그대로)
    P = (Q[:, None, None] * NH[None, :, :]).reshape(-1, 3)
    P0 = back_trace(P, bg, mass, t, nsteps)            # ← t=0 의 값
    g0 = (lambda pp: fs.f_fermi_dirac(np.linalg.norm(pp, axis=-1))) if f0 is None else f0
    fv = np.asarray(g0(P0), float).reshape(len(Q), -1)

    Pi = P.reshape(len(Q), -1, 3) / a                  # 정규직교 P^î = p_i/a_i
    lam2 = np.einsum("rai,rai->ra", Pi, Pi)
    lam = np.sqrt(lam2)
    E = np.sqrt(mass ** 2 + lam2)
    e = Pi / np.maximum(lam, 1e-300)[..., None]
    w = (DQ[:, None] * Q[:, None] ** 2) * WA[None, :] * fv / V
    out = {}
    from bianchi.matter.hierarchy import pstf
    for l in range(l_max + 1):
        for i in range(i_max + 1):
            integ = w * E * (lam / np.maximum(E, 1e-300)) ** (l + 2 * i)
            if l == 0:
                out[(l, i)] = float(integ.sum())
                continue
            letters = "ijklmn"[:l]
            subs = ",".join(f"ra{c}" for c in letters)
            T = np.einsum(f"ra,{subs}->{letters}", integ, *([e] * l))
            out[(l, i)] = pstf(T)
    return out


def type_I_moment_residual(mass=0.6, t=0.35, l_max=2, i_max=1, nsteps=64):
    """★★ A → 0 에서 type V 모멘트가 **type I 정확 구적과 일치**해야 한다.

    역방향 특성곡선·격자·측도가 모두 옳은지 한 번에 보는 게이트.
    """
    from bianchi.matter import hierarchy as H
    bg = Background(A=0.0)
    a = bg.a(t)
    got = moments_type_V(bg, mass, t, l_max, i_max, nsteps=nsteps)
    rho = H.J_moment(a, mass, 0, 0)
    worst = 0.0
    for (l, i), v in got.items():
        ex = np.atleast_1d(np.asarray(H.J_moment(a, mass, l, i), float))
        worst = max(worst, float(np.abs(np.atleast_1d(np.asarray(v, float)).ravel()
                                        - ex.ravel()).max() / rho))
    return worst


def moment_convergence(mass=0.6, t=0.35, A=0.7, steps=(8, 16, 32, 64, 128)):
    """★ 역추적 스텝 수에 대한 모멘트 수렴 — 오라클의 실제 정확도를 노출한다."""
    bg = Background(A=A)
    ref = moments_type_V(bg, mass, t, 2, 1, nsteps=512)
    rho = float(ref[(0, 0)])
    out = []
    for n in steps:
        g = moments_type_V(bg, mass, t, 2, 1, nsteps=n)
        worst = max(float(np.abs(np.atleast_1d(np.asarray(g[k], float)).ravel()
                                 - np.atleast_1d(np.asarray(ref[k], float)).ravel()
                                 ).max() / rho) for k in ref)
        out.append((int(n), worst))
    return out


def isotropic_redshift_residual(mass=0.0, t=0.4, A=0.7, nsteps=64):
    """★ 등방 type V (= open FRW) 에서 무질량 ρ ∝ a⁻⁴ 인지 — 물리 게이트.

    (Σp² 가 보존되므로 λ = |p|/a ∝ 1/a, 따라서 ρ ∝ a⁻⁴.)
    """
    bg = Background(a0=(1.0, 1.0, 1.0), sigma_diag=(0.0, 0.0, 0.0), A=A)
    r0 = moments_type_V(bg, mass, 0.0, 0, 0, nsteps=nsteps)[(0, 0)]
    rt = moments_type_V(bg, mass, t, 0, 0, nsteps=nsteps)[(0, 0)]
    scale = float(bg.a(t)[0] / bg.a(0.0)[0])
    return float(abs(rt / r0 * scale ** 4 - 1.0))


# ═══════════════════════════════════════ 6. K4c — type V **boosted** 모멘트
#
# H5-d 가 type I 에 한 것과 구조는 같다.  다른 것은 딱 하나:
#   · 같은 것 — boost 대수는 순수 대수 (`tilted_moments.boost_momentum` 재사용),
#              측도도 d³P′ = (E′/E)d³P 그대로.
#   · 다른 것 — 격자에서 f 값을 얻는 방법.  type I 은 f₀(q) 를 바로 읽지만
#              type V 는 **역방향 특성곡선**으로 t=0 까지 거슬러야 한다 (`back_trace`).
def moments_type_V_tilted(bg, mass, t, v, l_max=2, i_max=1, f0=None, nsteps=64):
    """★★ tilt 를 켠 type V 모멘트 J′^(i)_{A_l}(t).

    v = 0 이면 `moments_type_V` 와 **비트-정확** 같아야 한다 (피적분함수가 문자 그대로 동일).
    """
    from bianchi.matter import freestream as fs
    from bianchi.matter import tilted_moments as TM
    from bianchi.matter.hierarchy import pstf
    a = bg.a(t)
    V = float(np.prod(a))
    Q, DQ, NH, WA = fs._Q, fs._DQ, fs._NHAT, fs._WANG
    P_inv = (Q[:, None, None] * NH[None, :, :]).reshape(-1, 3)   # 불변기저 p_i (t)
    P0 = back_trace(P_inv, bg, mass, t, nsteps)
    g0 = (lambda pp: fs.f_fermi_dirac(np.linalg.norm(pp, axis=-1))) if f0 is None else f0
    fv = np.asarray(g0(P0), float).reshape(len(Q), -1)

    P = P_inv.reshape(len(Q), -1, 3) / a                        # 법선틀 정규직교 P^î
    P2 = np.einsum("rai,rai->ra", P, P)
    E = np.sqrt(mass ** 2 + P2)
    Ep, _, lamp, ep = TM.boost_momentum(P, E, v)
    # ★ 측도: d³P′ = (E′/E)d³P (로런츠 불변 d³P/E) — type I 과 동일
    w = (DQ[:, None] * Q[:, None] ** 2) * WA[None, :] * fv / V * (Ep / E)
    out = {}
    for l in range(l_max + 1):
        for i in range(i_max + 1):
            integ = w * Ep * (lamp / np.maximum(Ep, 1e-300)) ** (l + 2 * i)
            if l == 0:
                out[(l, i)] = float(integ.sum())
                continue
            letters = "ijklmn"[:l]
            subs = ",".join(f"ra{c}" for c in letters)
            out[(l, i)] = pstf(np.einsum(f"ra,{subs}->{letters}", integ, *([ep] * l)))
    return out


def tilted_v_zero_residual(mass=0.6, t=0.35, A=0.7, l_max=2, i_max=1, nsteps=64):
    """★ v = 0 에서 `moments_type_V` 와 **비트-정확** 일치 (E′=E, P′=P)."""
    bg = Background(A=A)
    a = moments_type_V(bg, mass, t, l_max, i_max, nsteps=nsteps)
    b = moments_type_V_tilted(bg, mass, t, np.zeros(3), l_max, i_max, nsteps=nsteps)
    return max(float(np.abs(np.atleast_1d(np.asarray(a[k], float)).ravel()
                            - np.atleast_1d(np.asarray(b[k], float)).ravel()).max())
               for k in a)


def project_stress_with_flux(rho, p, q, pi, v):
    """법선틀 (ρ, q^i, p, π^{ij}) 로 T^{μν} 를 세우고 tilted 사틀로 사영한다.

    ★ `tilted_moments.project_stress_to_tilted` 를 재사용할 수 **없다** — 그쪽은
      `T[0,i] = 0` (법선틀 q = 0) 을 가정한다.  type I 등방 f₀ 에서는 홀수 l 이
      항등적으로 0 이라 옳았지만, **type V 는 자유흐름만으로 q ≠ 0 을 만든다**
      (특성곡선이 p₁ 방향의 홀짝 대칭을 깬다 — K2b 가 "담을 수 있다" 고 한 그 자리).
      처음에 그 함수를 그대로 썼다가 프레임 게이트가 1e−3 에서 멈췄고,
      `normal_q_is_zero = 6.3e−3` 이 원인을 가리켰다.
    """
    from bianchi.matter import tilted_moments as TM
    pi = np.asarray(pi, float)
    q = np.asarray(q, float)
    T = np.zeros((4, 4))
    T[0, 0] = rho
    T[0, 1:] = q
    T[1:, 0] = q
    T[1:, 1:] = p * np.eye(3) + pi
    _, udn, _, edn = TM._tetrad_flat(v)
    rho_p = float(udn @ T @ udn)
    q_p = -np.einsum("m,mn,an->a", udn, T, edn)
    S = np.einsum("am,mn,bn->ab", edn, T, edn)
    return rho_p, np.trace(S) / 3.0, q_p, S - np.trace(S) * np.eye(3) / 3.0


def frame_independence_residual_type_V(mass=0.6, t=0.35, A=0.7,
                                       v=(0.15, -0.1, 0.2), nsteps=64):
    """★★ **가장 결정적인 게이트** — T^{μν} 프레임 무관성 (계층을 전혀 안 쓴다).

    법선틀 구적의 (ρ, q, p, π) 로 T^{μν} 를 세우고 tilted 사틀로 사영한 값이,
    **boosted 구적이 직접 준** (ρ′, q′, π′) 와 같아야 한다.
    여기서 어긋나면 특성곡선·측도·boost 중 하나가 틀린 것이다.
    """
    bg = Background(A=A)
    n = moments_type_V(bg, mass, t, 2, 1, nsteps=nsteps)
    rho, p = float(n[(0, 0)]), float(n[(0, 1)]) / 3.0
    pi = np.asarray(n[(2, 0)], float)
    q0 = np.asarray(n[(1, 0)], float)
    rho_t, p_t, q_t, pi_t = project_stress_with_flux(rho, p, q0, pi, v)
    b = moments_type_V_tilted(bg, mass, t, v, 2, 1, nsteps=nsteps)
    rho_q = float(b[(0, 0)])
    p_q = float(b[(0, 1)]) / 3.0
    q_q = np.asarray(b[(1, 0)], float)
    pi_q = np.asarray(b[(2, 0)], float)
    return dict(rho=abs(rho_t - rho_q) / rho, p=abs(p_t - p_q) / rho,
                q=float(np.abs(q_t - q_q).max()) / rho,
                pi=float(np.abs(pi_t - pi_q).max()) / rho,
                normal_flux=float(np.abs(q0).max()) / rho)


def spontaneous_flux(masses=(0.0, 0.6, 2.0), As=(0.0, 0.2, 0.4, 0.7), t=0.35,
                     nsteps=64):
    """★★ **type V 자유흐름은 법선틀 열유속 q 를 스스로 만든다** — K2b 가 연 자리.

    등방 f₀(|p|) 로 출발해도 특성곡선이 p₁ 의 홀짝 대칭을 깬다.
    반환 [(m, A, |q|/ρ)].  A=0 이면 정확히 0 이어야 한다 (type I).
    """
    out = []
    for m in masses:
        for A in As:
            bg = Background(A=A)
            n = moments_type_V(bg, m, t, 1, 0, nsteps=nsteps)
            rho = float(n[(0, 0)])
            q = np.abs(np.asarray(n[(1, 0)], float)).max()
            out.append((float(m), float(A), float(q / rho)))
    return out


def type_I_boosted_residual(mass=0.6, t=0.35, v=(0.15, -0.1, 0.2), nsteps=64):
    """★★ A → 0 에서 **H5-d 의 type I boosted 구적**과 일치 — 두 오라클이 만난다."""
    from bianchi.matter import tilted_moments as TM
    bg = Background(A=0.0)
    a = bg.a(t)
    got = moments_type_V_tilted(bg, mass, t, v, 2, 1, nsteps=nsteps)
    rho = TM.J_moment_tilted(a, v, mass, 0, 0)
    worst = 0.0
    for (l, i), val in got.items():
        ex = np.atleast_1d(np.asarray(TM.J_moment_tilted(a, v, mass, l, i), float))
        worst = max(worst, float(np.abs(np.atleast_1d(np.asarray(val, float)).ravel()
                                        - ex.ravel()).max() / rho))
    return worst


def self_consistent_a_physical(mass=0.6, t=0.35, A=0.7,
                               sigma_diag=(0.06, -0.02, -0.04), nsteps=64):
    """★★ K5a 로 확정한 **물리 단위** Codazzi 로 자기정합성을 잰다.

        q_a = 3 a_b σ^{ab}        (K5a 에서 계량으로 확인, 잔차 정확히 0)
        우리 계량 e^{+2Ax} 의 Ellis-MacCallum 구조상수는  a₁ = **−A/a₁(t)**
        (교환자 [e₁,e₂] = −(A/a₁)e₂ 를 직접 계산해 확정 — 부호가 논쟁거리였다)

    ⇒ 대각 σ 에서  q₁ = 3σ₁·a₁ = −3σ₁A/a₁(t).
    자유흐름이 만든 q₁ 을 넣고 **필요한 a₁** 을 역산해, 배경이 실제로 준 값과 비교한다.
    규격화(H, 3H² …) 를 전혀 거치지 않으므로 애매함이 없다.

    ★ K4c 의 `self_consistent_A` 는 확장정규화 판이라 규격화 인자가 불확실했다.
      이 함수가 그것을 **물리 단위로** 대체한다.
    """
    bg = Background(sigma_diag=sigma_diag, A=A)
    n = moments_type_V(bg, mass, t, 1, 0, nsteps=nsteps)
    rho = float(n[(0, 0)])
    q = np.asarray(n[(1, 0)], float)
    a = bg.a(t)
    sig = np.asarray(sigma_diag, float)
    a1_actual = -float(A) / float(a[0])                 # 배경이 실제로 준 a₁
    a1_needed = float(q[0]) / (3.0 * sig[0])            # q₁ 을 담으려면 필요한 a₁
    return dict(q_over_rho=float(np.abs(q).max() / rho), q1=float(q[0]),
                a1_actual=a1_actual, a1_needed=a1_needed,
                ratio=a1_needed / a1_actual,
                transverse=float(max(abs(q[1]), abs(q[2])) / rho))


def flux_vanishes_at_t_zero(mass=0.6, A=0.7, nsteps=8):
    """★ t = 0 에서는 등방 f₀ 라 q = 0 — 유속이 **자유흐름으로 생긴다**는 확인."""
    bg = Background(A=A)
    n = moments_type_V(bg, mass, 0.0, 1, 0, nsteps=nsteps)
    return float(np.abs(np.asarray(n[(1, 0)], float)).max() / float(n[(0, 0)]))


def flux_growth(mass=0.6, A=0.7, times=(0.0, 0.1, 0.2, 0.35, 0.5), nsteps=64):
    """★ |q|/ρ 의 시간 성장 — 자유흐름이 유속을 만드는 속도."""
    out = []
    for t in times:
        bg = Background(A=A)
        n = moments_type_V(bg, mass, t, 1, 0, nsteps=max(nsteps, 8))
        out.append((float(t), float(np.abs(np.asarray(n[(1, 0)], float)).max()
                                    / float(n[(0, 0)]))))
    return out


def solve_self_consistent_shear(mass=0.6, t=0.35, A=0.7, lo=-0.030, hi=-0.002,
                                nsteps=64, iters=40):
    """★★ **구성적 결과**: 운동량 구속을 정확히 만족하는 σ₁ 을 찾는다.

        조건:  q₁(σ, A, t)  =  3 σ₁ · a₁,      a₁ = −A/a₁(t)   (K5a 로 확정)

    자유흐름이 만드는 q 는 σ 에도 의존하므로 이것은 **고정점 문제**다.
    σ₁ 을 이분법으로 풀어 잔차를 보고한다 (나머지 두 성분은 −σ₁/2 로 무대각합 유지).

    ★ 정직한 범위: 이것은 **운동량 구속만** 만족시킨 구성이다.  Friedmann 구속과
      진화방정식까지 함께 푸는 것은 K5 결합계의 몫이다.
    """
    def resid(s1):
        sg = (s1, -s1 / 2.0, -s1 / 2.0)
        bg = Background(sigma_diag=sg, A=A)
        n = moments_type_V(bg, mass, t, 1, 0, nsteps=nsteps)
        q1 = float(np.asarray(n[(1, 0)], float)[0])
        a1 = -float(A) / float(bg.a(t)[0])
        return q1 - 3.0 * s1 * a1, q1, a1, float(n[(0, 0)])

    flo, *_ = resid(lo)
    fhi, *_ = resid(hi)
    if flo * fhi > 0:
        return dict(found=False, f_lo=flo, f_hi=fhi, lo=lo, hi=hi)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        fm, *_ = resid(mid)
        if flo * fm <= 0:
            hi, fhi = mid, fm
        else:
            lo, flo = mid, fm
    s1 = 0.5 * (lo + hi)
    f, q1, a1, rho = resid(s1)
    return dict(found=True, sigma1=s1, q1=q1, a1=a1, rho=rho,
                residual=abs(f) / rho, ratio=(q1 / (3 * s1)) / a1)
