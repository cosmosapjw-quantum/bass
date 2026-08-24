"""
K5b · **type V 결합 진화** — 운동론이 기하를 실제로 움직인다.

K5a 가 계량 `ds² = −dt² + a₁²dx² + e^{2Ax}(a₂²dy² + a₃²dz²)` 에서 확정한 것 (인용 없음):

    Friedmann :  3H² = ρ + σ² + 3A²/a₁²                        (G_{0̂0̂} = ρ)
    Codazzi   :  3σ₁·A/a₁ = −q₁                                 (G_{0̂1̂} = −q₁)
    공간      :  G_{îî} = A²/a₁² − u_j − u_k − h_jh_k = p + π_ii  (i,j,k 순환)
                 u_i ≡ ä_i/a_i,  h_i ≡ ȧ_i/a_i
    ★ 비대각 성분 G_{0̂2̂}=G_{0̂3̂}=G_{1̂2̂}=G_{1̂3̂}=G_{2̂3̂} 은 **항등적으로 0**
      → 대각 계량이 유지되려면 물질도 q₂=q₃=π_{i≠j}=0 이어야 하고, type V 자유흐름은
        p₂→−p₂, p₃→−p₃ 반사대칭을 각각 보존하므로 **자동으로 만족**한다.

★ 세 방향의 공간식에 모두 **같은** A²/a₁² 가 붙는다 (1 축이 특별한데도).  이건
  가정이 아니라 K5a 의 기호 계산에서 읽은 값이고, `accelerations` 는 그 식을
  **왕복**으로 재검증한다 (`audit.k5_type_v_einstein.spatial_einstein_numeric`).

★ 운동론은 **순방향**으로 바꾼다.  K4b 는 매 시각 t=0 까지 역추적했는데 (O(nsteps²)),
  결합 진화에서는 감당이 안 된다.  Liouville 로 노드와 무게를 함께 굴리면 O(nsteps):

      ṗ_i = 특성곡선 (K4a),        d ln W/dt = −2A p¹/E

  둘째 항의 유래: 불변기저 측도가 보존되지 않고 ∂ṗ_i/∂p_i = −2A p¹/E 다 (K4b 에서
  측정).  ★ 이 규칙을 **가정하지 않고** 역추적 판과 대조해 확인한다
  (`forward_vs_backward` → 1.7e−13; 규칙을 빼면 3.4e−03, 배율 2e+10).

★ 반증된 첫 설계 (기록): 처음에는 W 에 측도 d³P = d³p/V 를 통째로 넣어
  d ln W/dt = −2Ap¹/E − **3H** 로 굴렸다.  그런데 A = 0 대조군이 0 이 아니라
  1.7e−09 를 냈다 — 전량이 지수함수 e^{−3Ht} 의 RK4 오차였다
  (예측 n·z⁵/120 = 1.73e−09, 측정 1.732e−09, `volume_factor_is_the_error_floor`).
  V 는 어차피 a_i 에서 정확히 나오므로 **W 는 공변무게 f·d³p 만 나르고** 모멘트를
  잴 때 V=∏a_i 로 나눈다.  그러면 A=0 대조군이 **비트-정확 0.0** 이 된다.
"""
from __future__ import annotations

import numpy as np

from bianchi.matter import type_v as TV

try:                                        # R1 · Rust 가속 (없으면 numpy 폴백)
    import bianchi_rustcore as _RC
except Exception:                           # pragma: no cover
    _RC = None


def rust_available():
    """R1 가속 경로가 살아 있는가 (없으면 numpy 오라클로 그대로 돈다)."""
    return _RC is not None


# ═══════════════════════════════════════ 1. 순방향 운동론 (Liouville)
def initial_nodes(mass, f0=None):
    """t = 0 의 노드 p_i 와 **공변무게** W = f₀·d³p (V 는 나르지 않는다).

    격자는 K4b 와 같은 것을 쓴다 — 두 판을 비교할 때 격자 차이가 섞이지 않도록.
    """
    from bianchi.matter import freestream as fs
    Q, DQ, NH, WA = fs._Q, fs._DQ, fs._NHAT, fs._WANG
    P = (Q[:, None, None] * NH[None, :, :]).reshape(-1, 3)
    g0 = (lambda pp: fs.f_fermi_dirac(np.linalg.norm(pp, axis=-1))) if f0 is None else f0
    fv = np.asarray(g0(P), float)
    W = ((DQ[:, None] * Q[:, None] ** 2) * WA[None, :]).reshape(-1) * fv
    return P, W


def kinetic_rhs(P, W, a_vec, mass, A, measure=True):
    """(Ṗ, Ẇ) — 특성곡선 + Liouville 측도 무게.

    `measure=False` 는 **대조군**이다 (야코비안을 버린 판).  이걸로 재면
    `forward_vs_backward` 가 3.4e−03 로 무너진다 — 규칙이 장식이 아님을 고정한다.
    """
    dP = TV.characteristic_rhs_vec(P, a_vec, mass, A)
    if not measure:
        return dP, np.zeros_like(W)
    PU = P / np.asarray(a_vec, float) ** 2
    E = np.sqrt(mass ** 2 + np.einsum("ni,ni->n", P, PU))
    return dP, W * (-2.0 * A * PU[:, 0] / E)


def moments_from_nodes(P, W, a_vec, mass, l_max=2, i_max=1):
    """노드·공변무게에서 J^(i)_{A_l} — 측도 d³P = d³p/V 의 **V 는 여기서** 나눈다."""
    from bianchi.matter.hierarchy import pstf
    a = np.asarray(a_vec, float)
    w = np.asarray(W, float) / float(np.prod(a))
    Pi = np.asarray(P, float) / a
    lam2 = np.einsum("ni,ni->n", Pi, Pi)
    lam = np.sqrt(lam2)
    E = np.sqrt(mass ** 2 + lam2)
    e = Pi / np.maximum(lam, 1e-300)[:, None]
    out = {}
    for l in range(l_max + 1):
        for i in range(i_max + 1):
            integ = w * E * (lam / np.maximum(E, 1e-300)) ** (l + 2 * i)
            if l == 0:
                out[(l, i)] = float(integ.sum())
                continue
            letters = "ijklmn"[:l]
            subs = ",".join(f"n{c}" for c in letters)
            out[(l, i)] = pstf(np.einsum(f"n,{subs}->{letters}", integ, *([e] * l)))
    return out


def flux_rate_from_nodes(P, W, a_vec, mass, A):
    """★★ q̇₁ 을 **노드에서 정확히** — 유한차분 없이.

        q₁ = (a₁V)⁻¹ Σ W p₁        (측도 d³P = d³p/V, ê₁ = (p₁/a₁)/λ)

    Liouville 규칙 Ẇ = −2A(p¹/E)W 와 특성곡선 ṗ₁ = (A/E)(p₂p²+p₃p³) 을 넣으면

        q̇₁ = −(h₁+3H)q₁ + (A/(a₁V)) Σ W λ²(1 − 3ê₁²)/E

    이고, ∫f(λ²/E) = 3p, ∫f(λ²/E)ê₁² = π₁₁ + p 라 뒷항이 −3(A/a₁)π₁₁ 로 줄어든다.
    ★ 이 함수는 **줄이기 전** 형태를 그대로 계산한다 — 줄인 법칙과 대조하기 위해.
    """
    a = np.asarray(a_vec, float)
    V = float(np.prod(a))
    Pi = np.asarray(P, float) / a
    lam2 = np.einsum("ni,ni->n", Pi, Pi)
    E = np.sqrt(mass ** 2 + lam2)
    e1sq = np.where(lam2 > 0, Pi[:, 0] ** 2 / np.maximum(lam2, 1e-300), 0.0)
    src = float(np.sum(W * lam2 * (1.0 - 3.0 * e1sq) / E)) * float(A) / (a[0] * V)
    q1 = float(np.sum(W * np.asarray(P, float)[:, 0])) / (a[0] * V)
    return q1, src


def _push_nodes(P, W, bg_a, mass, A, t, nsteps, measure=True, rate=None,
                backend=None):
    """t 까지 RK4 로 (P, W) 를 민다.  `bg_a(u)` 는 시각 u 의 a_i.

    ★ R2: `rate` (지수 성장률) 를 주면 배경이 해석적이라 Rust 커널로 갈 수 있다.
    """
    if backend != "python" and rate is not None and _RC is not None:
        Pn, Wn = _RC.tv_push_nodes(
            np.ascontiguousarray(np.asarray(P, float)),
            np.ascontiguousarray(np.asarray(W, float)),
            np.asarray(bg_a(0.0), float), np.asarray(rate, float), float(mass),
            float(A), float(t), int(nsteps), bool(measure))
        return np.asarray(Pn), np.asarray(Wn)
    dt = t / nsteps
    for k in range(nsteps):
        s = k * dt

        def f(Pv, Wv, u):
            return kinetic_rhs(Pv, Wv, bg_a(u), mass, A, measure)

        k1P, k1W = f(P, W, s)
        k2P, k2W = f(P + .5 * dt * k1P, W + .5 * dt * k1W, s + .5 * dt)
        k3P, k3W = f(P + .5 * dt * k2P, W + .5 * dt * k2W, s + .5 * dt)
        k4P, k4W = f(P + dt * k3P, W + dt * k3W, s + dt)
        P = P + dt / 6 * (k1P + 2 * k2P + 2 * k3P + k4P)
        W = W + dt / 6 * (k1W + 2 * k2W + 2 * k3W + k4W)
    return P, W


def forward_vs_backward(mass=0.6, t=0.35, A=0.7, nsteps=200, l_max=2, i_max=1,
                        measure=True, ref_steps=256, backend=None):
    """★★ 순방향 Liouville 이 K4b 의 **역추적**과 같은 모멘트를 주는가.

    측도 규칙 `d ln W/dt = −2Ap¹/E` 를 **가정하지 않고 대조로 확인**한다.
    두 판은 격자마저 다르다 (역추적은 시각 t 의 고정 구면격자, 순방향은 t=0 격자를
    실어 나른 찌그러진 격자) — 그래서 이 일치는 구적·측도·특성곡선을 한 번에 잡는다.

    반환 max|Δ|/ρ.
    """
    bg = TV.Background(A=A)
    ref = TV.moments_type_V(bg, mass, t, l_max, i_max, nsteps=ref_steps)
    P, W = initial_nodes(mass)
    P, W = _push_nodes(P, W, bg.a, mass, A, t, nsteps, measure,
                       rate=bg.H + bg.sig, backend=backend)
    got = moments_from_nodes(P, W, bg.a(t), mass, l_max, i_max)
    rho = float(ref[(0, 0)])
    return max(float(np.abs(np.atleast_1d(np.asarray(got[k], float)).ravel()
                            - np.atleast_1d(np.asarray(ref[k], float)).ravel()
                            ).max() / rho) for k in ref)


def measure_rule_is_needed(**kw):
    """★ 규칙 있음/없음 — (있음, 없음, 배율)."""
    good = forward_vs_backward(measure=True, **kw)
    bad = forward_vs_backward(measure=False, **kw)
    return dict(with_rule=good, without_rule=bad,
                ratio=bad / max(good, 1e-300))


def volume_factor_is_the_error_floor(mass=0.6, t=0.35, H=1.0, nsteps=50):
    """★ **반증 기록**: W 에 1/V 까지 실어 −3H 를 RK4 로 굴리면 A=0 에서도 0 이 아니다.

    측정과 예측을 함께 낸다.  RK4 의 지수함수 상대오차는 스텝당 z⁵/120 (z = 3H·dt)
    이고 n 스텝 누적이면 n·z⁵/120 다.
    """
    bg = TV.Background(A=0.0, H=H)
    ref = TV.moments_type_V(bg, mass, t, 0, 0, nsteps=8)
    P, W = initial_nodes(mass)
    W = W / float(np.prod(bg.a(0.0)))
    dt = t / nsteps

    def rhs(Pv, Wv):                       # 옛 판: −2Ap¹/E − 3H (A=0 이라 −3H 만)
        return np.zeros_like(Pv), -3.0 * H * Wv

    for _ in range(nsteps):
        k1P, k1W = rhs(P, W)
        k2P, k2W = rhs(P + .5 * dt * k1P, W + .5 * dt * k1W)
        k3P, k3W = rhs(P + .5 * dt * k2P, W + .5 * dt * k2W)
        k4P, k4W = rhs(P + dt * k3P, W + dt * k3W)
        P = P + dt / 6 * (k1P + 2 * k2P + 2 * k3P + k4P)
        W = W + dt / 6 * (k1W + 2 * k2W + 2 * k3W + k4W)
    # 옛 판은 W 가 이미 1/V 를 안고 있으므로 V 를 다시 나누면 안 된다
    a = bg.a(t)
    old = moments_from_nodes(P, W * float(np.prod(a)), a, mass, 0, 0)
    z = 3.0 * H * dt
    return dict(old_scheme=abs(old[(0, 0)] / ref[(0, 0)] - 1.0),
                predicted=nsteps * z ** 5 / 120.0,
                new_scheme=forward_vs_backward(mass=mass, t=t, A=0.0,
                                               nsteps=nsteps, l_max=0, i_max=0,
                                               ref_steps=8))


# ═══════════════════════════════════════ 2. 기하 — K5a 의 공간 Einstein 식
def accelerations(a_vec, da_vec, A, p, pi):
    """ä_i/a_i 를 K5a 의 공간 Einstein 식에서 푼다 (3×3 선형계).

        G_{îî} = A²/a₁² − u_j − u_k − h_jh_k = p + π_ii    (i,j,k 순환)

    행렬 [[0,1,1],[1,0,1],[1,1,0]] 의 역: u_i = ½Σr − r_i.
    ★ 세 방향 모두 계수가 A²/a₁² 로 **같다** — K5a 의 기호 계산에서 읽은 것.
    """
    a = np.asarray(a_vec, float)
    h = np.asarray(da_vec, float) / a
    c = float(A) ** 2 / a[0] ** 2
    pid = np.diag(np.asarray(pi, float))
    rhs = np.array([c - h[1] * h[2] - p - pid[0],
                    c - h[0] * h[2] - p - pid[1],
                    c - h[0] * h[1] - p - pid[2]])   # = u_j + u_k
    S = float(rhs.sum()) / 2.0                        # u₁+u₂+u₃
    return np.array([S - rhs[0], S - rhs[1], S - rhs[2]])


def constraints(a_vec, da_vec, A, rho, q):
    """★ Friedmann·Codazzi 잔차 — K3 스타일 **상시 감시자**.

        F = 3H² − ρ − σ² − 3A²/a₁²
        C = 3σ₁·A/a₁ + q₁            (G_{0̂1̂} = 3σ₁A/a₁ = −q₁)
    """
    a = np.asarray(a_vec, float)
    h = np.asarray(da_vec, float) / a
    H = float(h.mean())
    sig = h - H
    s2 = 0.5 * float(sig @ sig)
    F = 3 * H ** 2 - rho - s2 - 3 * float(A) ** 2 / a[0] ** 2
    C = 3 * sig[0] * float(A) / a[0] + float(np.asarray(q, float)[0])
    return dict(friedmann=F, codazzi=C, H=H, sigma=sig)


def initial_expansion(a0, A, rho0, shear=0.0, sigma1=0.0, hsign=1.0):
    """★★ **정합 초기자료** — 두 구속을 t=0 에서 동시에 만족시킨다.

    등방 f₀ 면 t=0 에 q = 0 이므로 **Codazzi 가 σ₁ = 0 을 강제**한다.
    남는 자유도는 횡전단 σ = (0, s, −s) 이고 (무대각합), H 는 Friedmann 이 정한다:

        3H² = ρ + σ² + 3A²/a₁²,   σ² = ½(0 + s² + s²) = s²

    `sigma1 ≠ 0` 은 **대조군**이다 — 일부러 구속을 깨서 게이트에 이빨이 있는지 본다.
    ★ Friedmann 은 H² 만 정하므로 `hsign=-1` 이면 **수축** 해가 된다 (D2 에서 쓴다).
    """
    a = np.asarray(a0, float)
    s = float(shear)
    sig = np.array([float(sigma1), s, -s - float(sigma1)])
    sig = sig - sig.mean()                                  # 무대각합 보정
    s2 = 0.5 * float(sig @ sig)
    H = float(hsign) * float(
        np.sqrt(max((rho0 + s2 + 3 * float(A) ** 2 / a[0] ** 2) / 3.0, 0.0)))
    return (H + sig) * a, H, sig


# ═══════════════════════════════════════ 3. ★★ 결합 진화
def ansatz_residual(P, W, a_vec, mass):
    """★★ K5c · **대각 ansatz 가 허용되는 물질인가** — 비대각 성분을 잰다.

    K5c 가 계량에서 확정했듯 G_{0̂2̂}=G_{0̂3̂}=G_{1̂2̂}=G_{1̂3̂}=G_{2̂3̂} 는 **항등적으로 0**
    이다.  따라서 물질도 q₂=q₃=0, π_{i≠j}=0 이어야 Einstein 방정식이 무모순이다.
    type V 자유흐름은 p₂→−p₂, p₃→−p₃ 반사대칭을 각각 보존하므로 등방 f₀ 면 자동인데,
    **f₀ 가 그 대칭을 깨면 조용히 틀린 답이 나온다**.  그래서 재고 막는다.
    """
    mo = moments_from_nodes(P, W, a_vec, mass, 2, 0)
    rho = float(mo[(0, 0)])
    q = np.asarray(mo[(1, 0)], float)
    pi = np.asarray(mo[(2, 0)], float)
    off = pi - np.diag(np.diag(pi))
    return dict(q_transverse=float(np.abs(q[1:]).max() / rho),
                pi_offdiag=float(np.abs(off).max() / rho),
                worst=float(max(np.abs(q[1:]).max(), np.abs(off).max()) / rho))


def evolve_coupled(a0=(1.0, 0.95, 1.05), A=0.7, mass=0.6, t_end=0.3, nsteps=120,
                   f0=None, shear=0.03, sigma1=0.0, l_max=2, i_max=1, da0=None,
                   check_ansatz=1e-10, hsign=1.0, project=False, backend=None):
    """★★ **운동론이 기하를 움직인다** — (a_i, ȧ_i, P, W) 를 한 상태로 굴린다.

    매 스텝 두 구속 잔차를 기록한다 (K3 스타일 상시 감시).  구속은 진화식에
    **넣지 않는다** — 넣으면 게이트가 자기 자신을 검사하게 된다.

    ★ R1: `backend=None` 이면 Rust 커널이 있으면 쓰고 없으면 numpy 로 돈다.
      `backend="python"` 은 **오라클 경로**를 강제한다 (차등테스트가 쓴다).

    ★ K5c: t=0 에서 `ansatz_residual` 을 검사하고 임계를 넘으면 **거부**한다.
      대각 계량은 대각 물질만 담을 수 있는데, 검사가 없으면 비대각 성분을 조용히
      버리고 틀린 답을 낸다.  `check_ansatz=None` 이면 검사를 끈다 (대조군용).
    """
    a = np.asarray(a0, float).copy()
    P, W = initial_nodes(mass, f0)
    if check_ansatz is not None:
        r = ansatz_residual(P, W, a, mass)
        if r["worst"] > check_ansatz:
            raise ValueError(
                f"대각 ansatz 를 깨는 f₀ 다 — 비대각 물질 {r['worst']:.3e} "
                f"(q⊥ {r['q_transverse']:.3e}, π_offdiag {r['pi_offdiag']:.3e}). "
                "대각 계량으로는 담을 수 없다 (K5c).")
    rho0 = float(moments_from_nodes(P, W, a, mass, 0, 0)[(0, 0)])
    da = np.asarray(da0, float).copy() if da0 is not None \
        else initial_expansion(a, A, rho0, shear, sigma1, hsign)[0]
    if backend != "python" and _RC is not None and (l_max, i_max) == (2, 1):
        return _RC.tv_evolve(np.ascontiguousarray(P), np.ascontiguousarray(W),
                             a, da, float(mass), float(A), float(t_end),
                             int(nsteps), bool(project))
    dt = t_end / nsteps
    rec = {k: [] for k in ("t", "a", "h", "sigma1", "rho", "q1", "pi",
                           "friedmann", "codazzi", "offdiag", "Hdot_spatial",
                           "Hdot_ray", "qdot_node", "qdot_law", "qdot_naive")}

    def rhs(av, dav, Pv, Wv):
        mo = moments_from_nodes(Pv, Wv, av, mass, l_max, i_max)
        p = float(mo[(0, 1)]) / 3.0
        pi = np.asarray(mo[(2, 0)], float)
        acc = accelerations(av, dav, A, p, pi) * av
        dP, dW = kinetic_rhs(Pv, Wv, av, mass, A)
        return dav, acc, dP, dW

    for k in range(nsteps + 1):
        mo = moments_from_nodes(P, W, a, mass, l_max, i_max)
        q = np.asarray(mo[(1, 0)], float)
        pit = np.asarray(mo[(2, 0)], float)
        rho = float(mo[(0, 0)])
        pr = float(mo[(0, 1)]) / 3.0
        cs = constraints(a, da, A, rho, q)
        h = da / a
        u = accelerations(a, da, A, pr, pit)
        s2 = 0.5 * float(cs["sigma"] @ cs["sigma"])
        rec["t"].append(k * dt)
        rec["a"].append(a.copy())
        rec["h"].append(h.copy())
        rec["sigma1"].append(float(cs["sigma"][0]))
        rec["rho"].append(rho)
        rec["q1"].append(float(q[0]))
        rec["pi"].append(np.diag(pit).copy())
        rec["friedmann"].append(cs["friedmann"])
        rec["codazzi"].append(cs["codazzi"])
        rec["offdiag"].append(max(float(np.abs(q[1:]).max()),
                                  float(np.abs(pit - np.diag(np.diag(pit))).max()))
                              / rho)
        rec["Hdot_spatial"].append(float(u.mean() - (h ** 2).mean()))
        rec["Hdot_ray"].append(-cs["H"] ** 2 - 2.0 / 3.0 * s2
                               - (rho + 3.0 * pr) / 6.0)
        # ★ D2b · 운동량 보존을 **노드에서 정확히** 재고 줄인 법칙과 나란히 기록
        qn, src = flux_rate_from_nodes(P, W, a, mass, A)
        Hc = float(cs["H"])
        rec["qdot_node"].append(-(h[0] + 3.0 * Hc) * qn + src)
        rec["qdot_law"].append(-(4.0 * Hc + cs["sigma"][0]) * qn
                               - 3.0 * float(A) / a[0] * float(pit[0, 0]))
        rec["qdot_naive"].append(-(4.0 * Hc + cs["sigma"][0]) * qn)
        if k == nsteps:
            break
        s1 = rhs(a, da, P, W)
        s2 = rhs(a + .5 * dt * s1[0], da + .5 * dt * s1[1],
                 P + .5 * dt * s1[2], W + .5 * dt * s1[3])
        s3 = rhs(a + .5 * dt * s2[0], da + .5 * dt * s2[1],
                 P + .5 * dt * s2[2], W + .5 * dt * s2[3])
        s4 = rhs(a + dt * s3[0], da + dt * s3[1], P + dt * s3[2], W + dt * s3[3])
        a = a + dt / 6 * (s1[0] + 2 * s2[0] + 2 * s3[0] + s4[0])
        da = da + dt / 6 * (s1[1] + 2 * s2[1] + 2 * s3[1] + s4[1])
        P = P + dt / 6 * (s1[2] + 2 * s2[2] + 2 * s3[2] + s4[2])
        W = W + dt / 6 * (s1[3] + 2 * s2[3] + 2 * s3[3] + s4[3])
        if project:                      # ★ D2 · 매 스텝 구속 다양체로 되돌린다
            from bianchi.matter import type_v_constraints as D2
            mn = moments_from_nodes(P, W, a, mass, 1, 0)
            da = D2.project(a, da, A, float(mn[(0, 0)]),
                            float(np.asarray(mn[(1, 0)], float)[0]))
    return {k: np.array(v) for k, v in rec.items()}


def constraint_drift(**kw):
    """★★ **K3 스타일 게이트**: 구속이 진화 내내 유지되는가 (ρ 로 무차원화)."""
    r = evolve_coupled(**kw)
    rho = r["rho"]
    return dict(friedmann=float(np.abs(r["friedmann"] / rho).max()),
                codazzi=float(np.abs(r["codazzi"] / rho).max()),
                q1_final=float(r["q1"][-1]),
                sigma1_final=float(r["sigma1"][-1]),
                rho_ratio=float(rho[-1] / rho[0]),
                H_final=float(r["h"][-1].mean()))


def codazzi_tracking(**kw):
    """★★ **K5b 의 물리 결론**: 자유흐름이 q₁ 을 만들면 기하의 σ₁ 이 **따라간다**.

    t=0 에서 σ₁ = 0, q₁ = 0 으로 출발했는데, 진화 중 두 값이 Codazzi
    `3σ₁A/a₁ = −q₁` 를 계속 만족하는지 시각별로 낸다 (예측 σ₁ vs 실제 σ₁).
    """
    r = evolve_coupled(**kw)
    A = kw.get("A", 0.7)
    a1 = r["a"][:, 0]
    pred = -r["q1"] * a1 / (3.0 * A) if A else np.zeros_like(a1)
    return dict(t=r["t"], q1=r["q1"], sigma1=r["sigma1"], sigma1_pred=pred,
                rel=float(np.abs(pred[1:] - r["sigma1"][1:]).max()
                          / max(np.abs(r["sigma1"]).max(), 1e-300)))


def type_I_limit(**kw):
    """★ 대조군: A = 0 이면 Bianchi I.

    ★ **반증된 기대** (기록): 처음에는 "A=0 이면 q₁ 도 σ₁ 도 0" 이라고 적었는데
      틀렸다.  q₁ 은 정확히 0 (1.9e−15) 이지만 **σ₁ 은 2.1e−03 까지 자란다**.
      이유가 분명하다 — A=0 에서 Codazzi 는 `3σ₁·0/a₁ + q₁ = q₁ = 0` 으로 **퇴화**해
      σ₁ 을 전혀 구속하지 않는다.  σ₁ 은 대신 비등방 압력 π₁₁ 이 전단 진화식으로
      끌고 간다 (K1 과 같은 물리).  ⇒ 여기서 검사할 것은 σ₁=0 이 아니라 **K1 과의
      궤적 일치**다 (`bianchi_I_cross_check`).
    """
    kw.setdefault("A", 0.0)
    r = evolve_coupled(**kw)
    return dict(friedmann=float(np.abs(r["friedmann"] / r["rho"]).max()),
                q1_max=float(np.abs(r["q1"]).max()),
                sigma1_max=float(np.abs(r["sigma1"]).max()))


def bianchi_I_cross_check(a0=(1.0, 0.95, 1.05), mass=0.6, shear=0.03,
                          t_end=0.3, nsteps=120):
    """★★ A = 0 에서 **K1 의 독립 적분기**와 궤적이 같은가.

    두 경로가 공유하는 것이 거의 없다:
      K1  — H 를 Friedmann **구속에서 풀고**, σ̇ = −3Hσ + π (1계), 물질은 Bianchi I
            닫힌형 구적 (적색이동 p_i = const)
      K5b — ä_i 를 **공간 Einstein 식**에서 풀고 (2계), Friedmann 은 아예 안 쓰며,
            물질은 특성곡선으로 실어 나른 노드
    """
    from bianchi.matter import kinetic_einstein as KE
    sig0 = np.array([0.0, shear, -shear])
    ref = KE.integrate_reference(a0, sig0, mass, t_end, nsteps=nsteps)
    got = evolve_coupled(a0=a0, A=0.0, mass=mass, t_end=t_end, nsteps=nsteps,
                         shear=shear)
    ra = np.asarray(ref["a"])
    return dict(a=float(np.abs(got["a"] - ra).max() / np.abs(ra).max()),
                sigma=float(np.abs(got["sigma1"]
                                   - np.asarray(ref["sigma"])[:, 0]).max()))


def broken_initial_data(**kw):
    """★ 대조군: σ₁ ≠ 0 으로 출발하면 Codazzi 가 t=0 부터 깨지고 **회복되지 않는다**."""
    kw.setdefault("sigma1", 0.05)
    return constraint_drift(**kw)


def constraint_propagation(sigma1=0.05, **kw):
    """★★ 깨진 구속이 **어떻게** 번지는지 — Codazzi 위반이 Friedmann 을 민다.

    Bianchi 항등식 ∇_μG^{μν}=0 과 ∇_μT^{μν}=0 을 함께 쓰면 두 잔차는 **자기들끼리
    닫힌 선형계**를 이룬다.  그래서 C ≠ 0 이면 F 가 0 에서 출발해도 자란다.
    측정: C/ρ ≈ 1.4e−03 (거의 일정) 이 F/ρ 를 0 → 5.2e−04 로 **단조**하게 끌어올린다.
    """
    r = evolve_coupled(sigma1=sigma1, **kw)
    F = r["friedmann"] / r["rho"]
    C = r["codazzi"] / r["rho"]
    return dict(t=r["t"], F=F, C=C, F0=float(F[0]), F_end=float(F[-1]),
                C_mean=float(np.abs(C).mean()),
                monotone=bool(np.all(np.diff(np.abs(F)) > -1e-14)))


# ═══════════════════════════════════════ 4. K5c · ansatz 의 유효 범위
def offdiagonal_matter(**kw):
    """★★ K5c — 진화 내내 비대각 물질이 **0 으로 남는가** (대각 계량이 성립하는가)."""
    r = evolve_coupled(**kw)
    return dict(worst=float(np.abs(r["offdiag"]).max()),
                at_end=float(r["offdiag"][-1]))


def dipole_f0(eps=0.3, axis=1):
    """★ 대조군용 f₀ — `axis` 방향 쌍극자 (반사대칭 p_axis→−p_axis 를 깬다)."""
    from bianchi.matter import freestream as fs

    def f(P):
        P = np.asarray(P, float)
        n = np.linalg.norm(P, axis=-1)
        return fs.f_fermi_dirac(n) * (1.0 + eps * P[:, axis] / np.maximum(n, 1e-300))
    return f


def quadrupole_f0(eps=0.3, i=0, j=1):
    """★ 대조군용 f₀ — (i,j) 사중극자 (π_ij ≠ 0 을 직접 만든다)."""
    from bianchi.matter import freestream as fs

    def f(P):
        P = np.asarray(P, float)
        n2 = np.maximum(np.einsum("ni,ni->n", P, P), 1e-300)
        return fs.f_fermi_dirac(np.sqrt(n2)) * (1.0 + 3.0 * eps * P[:, i] * P[:, j] / n2)
    return f


def ansatz_admissibility(mass=0.6, a0=(1.0, 0.95, 1.05)):
    """★★ **정직한 한계** — 어떤 f₀ 가 대각 계량에 담기는가.

    K5c 가 계량에서 확정한 대로 비대각 Einstein 성분이 항등적으로 0 이므로,
    q₂=q₃=π_{i≠j}=0 을 어기는 f₀ 는 이 풀개로 풀 수 없다.  숫자로 못 박는다.
    """
    rows = []
    for name, f in (("등방", None),
                    ("쌍극자 p₂", dipole_f0(axis=1)),
                    ("쌍극자 p₁", dipole_f0(axis=0)),
                    ("사중극자 p₁p₂", quadrupole_f0(i=0, j=1)),
                    ("사중극자 p₂p₃", quadrupole_f0(i=1, j=2))):
        P, W = initial_nodes(mass, f)
        r = ansatz_residual(P, W, np.asarray(a0, float), mass)
        rows.append((name, r["q_transverse"], r["pi_offdiag"]))
    return rows


def solver_rejects_inadmissible_f0(**kw):
    """★ 검사가 실제로 막는가 — (등방 통과 여부, 사중극자 거부 여부)."""
    ok = True
    try:
        evolve_coupled(nsteps=1, t_end=1e-4, **kw)
    except ValueError:
        ok = False
    rejected = False
    try:
        evolve_coupled(nsteps=1, t_end=1e-4, f0=quadrupole_f0(i=0, j=1), **kw)
    except ValueError:
        rejected = True
    return dict(isotropic_ok=ok, quadrupole_rejected=rejected)


def raychaudhuri_gap(**kw):
    """★★ K5c — Ḣ 를 **두 경로**로 재고, 차이가 정확히 −F/6 인지 본다.

      (A) 공간 Einstein 식에서:  Ḣ = ⟨u_i⟩ − ⟨h_i²⟩       (Friedmann 미사용)
      (B) Raychaudhuri:          Ḣ = −H² − ⅔σ² − (ρ+3p)/6

    대수적으로 (A) − (B) = −F/6 이 **항등식**이다 (F 는 Friedmann 잔차).
    두 구속 진단자를 정확히 묶는 식이라, 우연한 일치로는 못 맞춘다.
    """
    r = evolve_coupled(**kw)
    gap = r["Hdot_spatial"] - r["Hdot_ray"]
    pred = -r["friedmann"] / 6.0
    sc = max(float(np.abs(r["Hdot_ray"]).max()), 1e-300)
    return dict(residual=float(np.abs(gap - pred).max() / sc),
                gap_max=float(np.abs(gap).max()),
                pred_max=float(np.abs(pred).max()))


def gauge_rescaling_invariance(lam=1.4, mass=0.6, t_end=0.2, nsteps=40,
                               a0=(1.0, 0.95, 1.05), A=0.7):
    """★★ K5c — x → λx 는 **게이지**다: (A, a₁, p₁) → (λA, λa₁, λp₁).

    물리량(정규직교틀 성분 ρ, H, σ, q^1̂, π)은 그대로여야 한다.  A 를 상수로
    고정한 것이 근사가 아니라 게이지 고정임을 **수치로** 확인한다.
    ★ 격자는 p′ 공간에 고정돼 있어 물리적으로 다른 점집합을 쓴다 — 그래서 일치는
      구적 정확도까지다 (기계정밀도가 아니다).
    """
    from bianchi.matter import freestream as fs
    base = evolve_coupled(a0=a0, A=A, mass=mass, t_end=t_end, nsteps=nsteps)
    sc = np.array([float(lam), 1.0, 1.0])

    def f0p(P):
        return fs.f_fermi_dirac(np.linalg.norm(np.asarray(P, float) / sc, axis=-1))

    scaled = evolve_coupled(a0=np.asarray(a0, float) * sc, A=lam * A, mass=mass,
                            t_end=t_end, nsteps=nsteps, f0=f0p)
    out = {}
    for k in ("rho", "q1", "sigma1"):
        d = np.abs(scaled[k] - base[k]).max() / np.abs(base["rho"]).max()
        out[k] = float(d)
    out["H"] = float(np.abs(scaled["h"].mean(axis=1) - base["h"].mean(axis=1)).max()
                     / np.abs(base["h"]).max())
    out["a_transverse"] = float(np.abs(scaled["a"][:, 1:] - base["a"][:, 1:]).max())
    out["a1_ratio"] = float(np.ptp(scaled["a"][:, 0] / base["a"][:, 0]))
    return out


def gauge_residual_is_quadrature(lam=2.5, nangs=(24, 32, 40), nsteps=20, t_end=0.2):
    """★ 게이지 잔차가 **각 구적 오차**임을 해상도로 확정한다.

    λ 가 크면 f₀′ 이 p′ 공간에서 납작해져 (종횡비 λ) 고정 각격자가 못 따라간다.
    NANG 을 올리면 6.1e−05 → 1.9e−06 → 5.6e−08 로 **스펙트럼 수렴**한다 — 즉
    물리적 불일치가 아니다.  (격자를 갈아끼우므로 느리다.)
    """
    from bianchi.matter import freestream as fs
    old = (fs._Q, fs._DQ, fs._NHAT, fs._WANG)
    rows = []
    try:
        for na in nangs:
            fs._Q, fs._DQ, fs._NHAT, fs._WANG = fs._build_grid(NANG=na)
            g = gauge_rescaling_invariance(lam=lam, nsteps=nsteps, t_end=t_end)
            rows.append((int(na), g["rho"], g["H"]))
    finally:
        fs._Q, fs._DQ, fs._NHAT, fs._WANG = old
    return rows


def report(**kw):
    print("=" * 74)
    print("K5b · type V 결합 진화 — 운동론이 기하를 움직인다")
    print("=" * 74)
    m = measure_rule_is_needed()
    print(f"\n[1] ★★ 측도 규칙 대조 (순방향 Liouville vs K4b 역추적)")
    print(f"    규칙 사용 : {m['with_rule']:.3e}")
    print(f"    규칙 제거 : {m['without_rule']:.3e}   (배율 {m['ratio']:.1e})")
    v = volume_factor_is_the_error_floor()
    print(f"\n[2] ★ 반증 기록 — 1/V 를 RK4 에 실었던 옛 판 (A=0)")
    print(f"    옛 판 오차 {v['old_scheme']:.3e}  vs 예측 n·z⁵/120 = {v['predicted']:.3e}")
    print(f"    새 판      {v['new_scheme']:.3e}   ← 비트-정확")
    d = constraint_drift(**kw)
    print(f"\n[3] ★★ 결합 진화 구속 표류")
    for k, val in d.items():
        print(f"    {k:14s} {val:.6e}" if isinstance(val, float) else f"    {k}: {val}")
    c = codazzi_tracking(**kw)
    print(f"\n[4] ★★ Codazzi 추적 — σ₁ 이 q₁ 을 따라가는가 (상대 {c['rel']:.2e})")
    for j in range(0, len(c["t"]), max(1, len(c["t"]) // 6)):
        print(f"    t={c['t'][j]:.3f}  q₁={c['q1'][j]:+.6e}  "
              f"σ₁={c['sigma1'][j]:+.6e}  예측={c['sigma1_pred'][j]:+.6e}")
    ti = type_I_limit(**kw)
    print(f"\n[5] ★ 대조군 A = 0 (Bianchi I)")
    print(f"    Friedmann {ti['friedmann']:.3e}   q₁ {ti['q1_max']:.3e}   "
          f"σ₁ {ti['sigma1_max']:.3e}")


if __name__ == "__main__":
    report()
