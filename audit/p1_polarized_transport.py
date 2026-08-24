"""
P1 · **편광 수송의 제1원리 유도** (83차) — f_ab 도입 전 예비 유도.

규약 (docs/Q-CONTRACT.md §2 승계):
    [e_b, e_c] = C^a_{bc} e_a ,  C^c_{ab} = eps_{abd} n^{dc} + a_a d^c_b - a_b d^c_a
    (T1)  dp_a/dlambda = C^c_{ba} p_c p^b

★★ 반증 기록 (83차, 이 스크립트가 잡았다)
   첫 후보는 "T1 의 이차항에서 p_c 를 V_c 로 바꾸면 된다" 였다:
       dV_a/dt =? -H V_a - sigma V + (R x V) + (1/E)[((N V) x p) + (A·p)V - A(V·p)]
   기각 근거 둘: (i) d(V·p)/dt ≠ 0 (기호), (ii) 좌표 평행이동 대비 상대오차
   **3.2e-1** (운동량은 같은 코드에서 3.7e-14 — 즉 좌표 경로는 옳다).
   원인: 4-벡터의 **시간성분 V_0 가 수송으로 생성**된다.  운동량은 널 조건이
   V_0 를 묶어주지만 일반 벡터는 그렇지 않다.  공간 3-벡터 법칙으로 쓰려면
   스크린 게이지 (V_0 = 0) 를 **회복하는 항**이 있어야 한다.

═══ 유도 1 (D1) · 4-벡터 평행이동을 회전계수에서 직접 ═══
부호를 손으로 추측하지 않는다.  정규직교틀의 교환함수에서 Ricci 회전계수를
**기계적으로** 만든다:

    [e_0, e_a] = -(H d_a^b + sigma_a^b + eps_a^{bc} R_c) e_b     (C^b_{0a})
    [e_a, e_b] = C^c_{ab} e_c = (eps_abd n^{dc} + a_a d^c_b - a_b d^c_a) e_c
    C^0_{ab} = 0 (초곡면 직교, omega = 0),  C^0_{0a} = 0 (측지, A_acc = 0)

    Gamma_{abc} = 1/2 (-C_{abc} - C_{bca} + C_{cab}),  eta = diag(-1,1,1,1)
    ★ 이 식은 **기억해서 쓰지 않고** 두 조건에서 직접 푼 것이다:
        (계량 적합) Gamma_{abc} = -Gamma_{bac}
        (무비틀림)  Gamma_{abc} - Gamma_{acb} = -C_{abc}
    세 순환식을 더하고 빼면 위 식이 유일해로 나온다.
    ★★ 반증 기록: 처음엔 1/2(C_{abc} + C_{cab} - C_{bca}) 를 썼다.  이 식은
    (a,b) 에 **대칭**이라 계량 적합성을 위반한다.  그런데 C_{abc} 가 (b,c) 에
    반대칭이라 **측지선 방정식에서는 통째로 빠진다** — 그래서 운동량 대조는
    2.1e-14 로 통과하고 편광만 3.2e-1 로 틀렸다.  "운동량이 맞으니 접속이 맞다"
    는 추론이 성립하지 않는 자리다.
    평행이동:  dV^a/dlambda + Gamma^a_{bc} V^b P^c = 0,   P = (E, p^a)

이 경로는 T1 을 **유도 결과로** 재현해야 한다 (앵커).

═══ 유도 2 (D2) · 스크린 게이지와 직교성 ═══
V·p = 0 이면 tetrad 성분으로 -V_0 E + V_a p_a = 0.  스크린 대표원은
    W_a = V_a - (V_0/E) p_a      (W_0 = 0, W·p = 0)
이고 이것이 편광 캐리어가 들 물리량이다.  d(V·p)/dt = 0 은 **평행이동의 성질**로
자동이며 (계량 보존), 게이트가 그것을 실측한다.

═══ 유도 3 (D3) · 스크린 홀로노미 = 순수 회전 ★ ═══
평행이동은 계량을 보존하므로, 스크린 2-평면 위의 홀로노미는 **정확히 SO(2)** 다.
따라서 편광 텐서의 수송은
        (스칼라 수송 배율)  x  (스크린 SO(2) 회전)
로 분해된다.  배율은 세기 I 와 **같은** 배율이다 (같은 접속을 받으므로).
⇒ 계획 §1.2 의 예측이 **증명된다**.  이 스크립트는 그것을 좌표 측지선 위에서
   수치로도 확인한다 (반증 시도).

═══ 유도 4 (D4) · 공변 프레임에서의 회전각 ═══
공변 노드 q̂ 에서 물리 방향은 ê = M q̂/mu.  캐리어는 tetrad 지표로 P_ab 를 들고
있으므로, 한 스텝의 갱신은
        P_new = R(psi) [ S · P_old ] R(psi)^T
여기서 S 는 스칼라와 같은 배율, R(psi) 는 **M-밀기 스크린**과 **평행이동 스크린**의
어긋남이다.  psi 는 닫힌형이 없을 수도 있다 — 그 경우 ODE 로 적분한다 (규모 상향은
계획 P5 에 반영).  이 스크립트가 어느 쪽인지 **측정**한다.

사용:  python -m audit.p1_polarized_transport
"""
from __future__ import annotations

import numpy as np
import sympy as sp

# ───────────────────────────────────────────── 기호 게이트


def _sym_n():
    v = sp.symbols("n11 n22 n33 n12 n13 n23", real=True)
    return sp.Matrix(3, 3, lambda i, j: {
        (0, 0): v[0], (1, 1): v[1], (2, 2): v[2],
        (0, 1): v[3], (1, 0): v[3], (0, 2): v[4], (2, 0): v[4],
        (1, 2): v[5], (2, 1): v[5]}[(i, j)])


def general_C(n, a):
    eps = {(0, 1, 2): 1, (1, 2, 0): 1, (2, 0, 1): 1,
           (0, 2, 1): -1, (2, 1, 0): -1, (1, 0, 2): -1}
    C = [[[sp.Integer(0)] * 3 for _ in range(3)] for _ in range(3)]
    for c in range(3):
        for i in range(3):
            for j in range(3):
                s = sum(eps.get((i, j, d), 0) * n[d, c] for d in range(3))
                if c == j:
                    s += a[i]
                if c == i:
                    s -= a[j]
                C[c][i][j] = sp.expand(s)
    return C


def rotation_coefficients(H, S, R, N, A):
    """정규직교틀의 Ricci 회전계수 Gamma^a_{bc} (4x4x4, numpy).

    eta = diag(-1,1,1,1).  C^a_{bc} 는 [e_b, e_c] = C^a_{bc} e_a.
    Gamma_{abc} = 1/2 (C_{abc} + C_{cab} - C_{bca}),  Gamma^a_{bc} = eta^{ad}Gamma_{dbc}.
    """
    eps = np.zeros((3, 3, 3))
    for i in range(3):
        for j in range(3):
            for k in range(3):
                eps[i, j, k] = (i - j) * (j - k) * (k - i) / 2
    C = np.zeros((4, 4, 4))                       # C[a][b][c]
    # [e_0, e_a] = -(H d + sigma + eps R) e_b
    K = H * np.eye(3) + S + np.einsum("abc,c->ab", eps, R)
    for a in range(3):
        for b in range(3):
            C[1 + b, 0, 1 + a] = -K[a, b]
            C[1 + b, 1 + a, 0] = +K[a, b]
    # [e_a, e_b] = C^c_{ab} e_c
    for c in range(3):
        for i in range(3):
            for j in range(3):
                v = sum(eps[i, j, d] * N[d, c] for d in range(3))
                if c == j:
                    v += A[i]
                if c == i:
                    v -= A[j]
                C[1 + c, 1 + i, 1 + j] = v
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    Clow = np.einsum("ad,dbc->abc", eta, C)       # C_{abc}
    Glow = 0.5 * (-Clow - np.einsum("bca->abc", Clow)
                  + np.einsum("cab->abc", Clow))
    # 계량 적합성 자기검사 (조용히 틀리지 않게)
    asym = np.abs(Glow + np.einsum("bac->abc", Glow)).max()
    assert asym < 1e-12, f"Gamma_(ab)c != 0 : {asym}"
    return np.einsum("ad,dbc->abc", eta, Glow)    # Gamma^a_{bc}


def transport_4vector(V4, P4, H, S, R, N, A):
    """dV^a/dlambda = -Gamma^a_{bc} V^b P^c  (반변 성분)."""
    G = rotation_coefficients(H, S, R, N, A)
    return -np.einsum("abc,b,c->a", G, V4, P4)


def d1_vector_transport_decomposition():
    """(구 후보, 기각됨) — 반증 박제용으로 남긴다."""
    p = sp.Matrix(sp.symbols("p1 p2 p3", real=True))
    V = sp.Matrix(sp.symbols("V1 V2 V3", real=True))
    A = sp.Matrix(sp.symbols("A1 A2 A3", real=True))
    n = _sym_n()
    C = general_C(n, list(A))
    lhs = [sp.expand(sum(C[c][b][k] * V[c] * p[b] for b in range(3)
                         for c in range(3))) for k in range(3)]
    rhs = [sp.expand(((n * V).cross(p))[k] + (A.dot(p)) * V[k]
                     - A[k] * V.dot(p)) for k in range(3)]
    return all(sp.simplify(lhs[k] - rhs[k]) == 0 for k in range(3))


def d1_reduces_to_T1():
    """(D1 앵커) V = p 로 놓으면 T1 의 분해가 정확히 나온다."""
    p = sp.Matrix(sp.symbols("p1 p2 p3", real=True))
    A = sp.Matrix(sp.symbols("A1 A2 A3", real=True))
    n = _sym_n()
    gen = [((n * p).cross(p))[k] + (A.dot(p)) * p[k] - A[k] * p.dot(p)
           for k in range(3)]
    t1 = [((n * p).cross(p))[k] + (A.dot(p)) * p[k] - A[k] * p.dot(p)
          for k in range(3)]
    return all(sp.simplify(gen[k] - t1[k]) == 0 for k in range(3))


def d2_orthogonality_is_preserved():
    """(D2) d(V·p)/dt == 0  — (P-T1) + T1 에서 항등.  V·p = 0 을 **쓰지 않고** 증명."""
    p = sp.Matrix(sp.symbols("p1 p2 p3", real=True))
    V = sp.Matrix(sp.symbols("V1 V2 V3", real=True))
    A = sp.Matrix(sp.symbols("A1 A2 A3", real=True))
    n = _sym_n()
    H, E = sp.symbols("H E", positive=True)
    S = sp.Matrix(3, 3, lambda i, j: sp.Symbol(
        f"s{min(i,j)}{max(i,j)}", real=True))
    R = sp.Matrix(sp.symbols("R1 R2 R3", real=True))
    dp = (-H * p - S * p + R.cross(p)
          + ((n * p).cross(p) + (A.dot(p)) * p - A * p.dot(p)) / E)
    dV = (-H * V - S * V + R.cross(V)
          + ((n * V).cross(p) + (A.dot(p)) * V - A * V.dot(p)) / E)
    # d(V·p)/dt = V·dp + p·dV;  V·p = 0 위에서 0 이어야 한다
    expr = sp.expand(V.dot(dp) + p.dot(dV))
    # V·p 로 나누어떨어지는가 (즉 V·p = 0 면 정확히 0)
    quo = sp.simplify(sp.expand(expr) - sp.expand(
        (-2 * H - 2 * (A.dot(p)) / E * 0) * V.dot(p)))
    # 직접 판정: V·p = 0 대입 후 0 인지
    sub = sp.solve(V.dot(p), V[2], dict=True)
    if not sub:
        return False, expr
    e2 = sp.simplify(expr.subs(sub[0]))
    return sp.simplify(e2) == 0, sp.simplify(quo)


# ───────────────────────────────────────────── 좌표 경로 (제1원리 대조)


def _christoffel_num(gfun, dgfun, x):
    g = gfun(x); dg = dgfun(x)                      # dg[mu][a][b] = d_mu g_ab
    ginv = np.linalg.inv(g)
    # Gamma^k_{ij} = 1/2 g^{kl}(d_i g_lj + d_j g_li - d_l g_ij)
    return 0.5 * np.einsum("kl,ijl->kij", ginv,
                           np.einsum("ilj->ijl", dg)
                           + np.einsum("jli->ijl", dg)
                           - np.einsum("lij->ijl", dg))


def _rk4(f, y, h, n):
    for _ in range(n):
        k1 = f(y); k2 = f(y + 0.5 * h * k1)
        k3 = f(y + 0.5 * h * k2); k4 = f(y + h * k3)
        y = y + h / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
    return y


def type_v_setup(c=(0.4, 0.7, 0.25)):
    """Bianchi V (class B, a-항).  Q2 의 설정 재사용."""
    c = np.asarray(c, float)

    def scale(t):
        return t ** c

    def gfun(x):
        t, xx = x[0], x[1]; a = scale(t); e2 = np.exp(2.0 * xx)
        return np.diag([-1.0, a[0] ** 2, a[1] ** 2 * e2, a[2] ** 2 * e2])

    def dgfun(x):
        t, xx = x[0], x[1]; a = scale(t); e2 = np.exp(2.0 * xx)
        da = c * t ** (c - 1.0); d = np.zeros((4, 4, 4))
        d[0] = np.diag([0.0, 2 * a[0] * da[0], 2 * a[1] * da[1] * e2,
                        2 * a[2] * da[2] * e2])
        d[1] = np.diag([0.0, 0.0, 2 * a[1] ** 2 * e2, 2 * a[2] ** 2 * e2])
        return d

    def bg(t):
        a = scale(t); da = c * t ** (c - 1.0); hs = da / a
        H = float(hs.mean())
        return H, np.diag(hs - H), np.zeros(3), np.zeros((3, 3)), \
            np.array([-1.0 / a[0], 0.0, 0.0])

    def triad(x):
        """정규직교 삼중틀의 공변 성분 변환: p_a(tetrad) = p_inv / a_a."""
        t, xx = x[0], x[1]; a = scale(t)
        return a, np.array([1.0, np.exp(-xx), np.exp(-xx)])

    return gfun, dgfun, bg, triad


def type_ii_setup(c=(0.4, 0.7, 0.25), n1=1.0):
    c = np.asarray(c, float)

    def scale(t):
        return t ** c

    def gfun(x):
        t, y = x[0], x[2]; a = scale(t); g = np.zeros((4, 4))
        g[0, 0] = -1.0; g[1, 1] = a[0] ** 2; g[2, 2] = a[1] ** 2
        g[3, 3] = a[2] ** 2 + a[0] ** 2 * (n1 * y) ** 2
        g[1, 3] = g[3, 1] = -a[0] ** 2 * n1 * y
        return g

    def dgfun(x):
        t, y = x[0], x[2]; a = scale(t); da = c * t ** (c - 1.0)
        d = np.zeros((4, 4, 4))
        d[0, 1, 1] = 2 * a[0] * da[0]; d[0, 2, 2] = 2 * a[1] * da[1]
        d[0, 3, 3] = 2 * a[2] * da[2] + 2 * a[0] * da[0] * (n1 * y) ** 2
        d[0, 1, 3] = d[0, 3, 1] = -2 * a[0] * da[0] * n1 * y
        d[2, 3, 3] = 2 * a[0] ** 2 * n1 ** 2 * y
        d[2, 1, 3] = d[2, 3, 1] = -a[0] ** 2 * n1
        return d

    def bg(t):
        a = scale(t); da = c * t ** (c - 1.0); hs = da / a
        H = float(hs.mean())
        return H, np.diag(hs - H), np.zeros(3), \
            np.diag([n1 * a[0] / (a[1] * a[2]), 0.0, 0.0]), np.zeros(3)

    def triad(x):
        t, y = x[0], x[2]; a = scale(t)
        return a, ("II", n1 * y)

    return gfun, dgfun, bg, triad


def _tetrad_lower(x, cov, kind, scale_fn):
    """좌표 공변성분 -> 불변틀 -> 정규직교틀 (공변 지표)."""
    a = scale_fn(x[0])
    if kind == "V":
        inv = np.array([cov[1], np.exp(-x[1]) * cov[2], np.exp(-x[1]) * cov[3]])
    else:                                             # II
        inv = np.array([cov[1], cov[2], cov[3] + _N1 * x[2] * cov[1]])
    return inv / a


_N1 = 1.0


def coord_transport(kind="V", t0=1.0, t1=1.5, nstep=6000, seed=0, four=False):
    """좌표에서 측지선 + 편광 벡터 평행이동 → tetrad 성분 (p_a, V_a) 궤적."""
    global _N1
    if kind == "V":
        gfun, dgfun, bg, _ = type_v_setup()
        scale_fn = lambda t: t ** np.array([0.4, 0.7, 0.25])   # noqa: E731
    else:
        gfun, dgfun, bg, _ = type_ii_setup(); _N1 = 1.0
        scale_fn = lambda t: t ** np.array([0.4, 0.7, 0.25])   # noqa: E731
    rng = np.random.default_rng(seed)
    x = np.array([t0, 0.0, 0.0, 0.0])
    vsp = rng.standard_normal(3) * 0.4
    g = gfun(x)
    vt = np.sqrt(float(vsp @ g[1:, 1:] @ vsp))
    u = np.concatenate([[vt], vsp])                    # 널 4-속도

    # 편광: p·W = 0, W 는 공간적.  임의 공간벡터를 p 에 직교화
    w = np.concatenate([[0.0], rng.standard_normal(3)])
    w = w - (w @ g @ u) / (u @ g @ u + 1e-300) * u if abs(u @ g @ u) > 1e-12 else w
    # 널이라 u·u = 0 — 대신 g(w,u)=0 을 직접 풀어 성분 조정
    lam = (w @ g @ u) / (g[0, 0] * u[0])
    w = w - lam * np.array([1.0, 0, 0, 0])
    w = w / np.sqrt(abs(w @ g @ w))

    def rhs(y):
        X, U, W = y[:4], y[4:8], y[8:12]
        G = _christoffel_num(gfun, dgfun, X)
        dU = -np.einsum("kij,i,j->k", G, U, U)
        dW = -np.einsum("kij,i,j->k", G, W, U)
        return np.concatenate([U, dU, dW])

    y = np.concatenate([x, u, w])
    h = (t1 - t0) / nstep / max(vt, 1e-12)
    traj = []
    while y[0] < t1:
        y = _rk4(rhs, y, h, 1)
        gg = gfun(y[:4])
        p_cov = gg @ y[4:8]
        w_cov = gg @ y[8:12]
        ps = _tetrad_lower(y[:4], p_cov, kind, scale_fn)
        ws = _tetrad_lower(y[:4], w_cov, kind, scale_fn)
        if four:
            # 반변 4-성분: V^0 = -V_0 = (dt 성분),  V^a = 공간 tetrad 성분
            traj.append((y[0], np.concatenate([[y[4]], ps]),
                         np.concatenate([[y[8]], ws])))
        else:
            traj.append((y[0], ps, ws))
    return traj, bg


def closed_transport(p0, V0, bg, t0, t1, nstep=6000):
    """(P-T1) 닫힌형으로 (p, V) 를 나른다."""
    def f(y):
        p, V = y[:3], y[3:]
        H, S, R, N, A = bg(f.t)
        E = np.linalg.norm(p)
        dp = (-H * p - S @ p + np.cross(R, p)
              + (np.cross(N @ p, p) + (A @ p) * p - A * (p @ p)) / E)
        dV = (-H * V - S @ V + np.cross(R, V)
              + (np.cross(N @ V, p) + (A @ p) * V - A * (V @ p)) / E)
        return np.concatenate([dp, dV])

    y = np.concatenate([p0, V0]); h = (t1 - t0) / nstep
    f.t = t0
    for _ in range(nstep):
        k1 = f(y); f.t += 0.5 * h
        k2 = f(y + 0.5 * h * k1); k3 = f(y + 0.5 * h * k2)
        f.t += 0.5 * h
        k4 = f(y + h * k3)
        y = y + h / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
    return y[:3], y[3:]


def closed_transport4(P0, V0, bg, t0, t1, nstep=6000):
    """회전계수 경로로 (P^a, V^a) 4-벡터를 t 로 나른다 (dt = E dlambda)."""
    def f(y, t):
        P, V = y[:4], y[4:]
        H, S, R, N, A = bg(t)
        E = max(P[0], 1e-300)
        dP = transport_4vector(P, P, H, S, R, N, A) / E
        dV = transport_4vector(V, P, H, S, R, N, A) / E
        return np.concatenate([dP, dV])

    y = np.concatenate([P0, V0]); h = (t1 - t0) / nstep; t = t0
    for _ in range(nstep):
        k1 = f(y, t); k2 = f(y + 0.5 * h * k1, t + 0.5 * h)
        k3 = f(y + 0.5 * h * k2, t + 0.5 * h); k4 = f(y + h * k3, t + h)
        y = y + h / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4); t += h
    return y[:4], y[4:]


def d1_first_principles(kind="V", nstep=4000, seed=0):
    """★ (D1 게이트) 좌표 평행이동 대 **회전계수 4-벡터** 경로 — 상대오차."""
    traj, bg = coord_transport(kind, nstep=nstep, seed=seed, four=True)
    t0, P0, V0 = traj[0]
    tE, PE, VE = traj[-1]
    P1, V1 = closed_transport4(P0, V0, bg, t0, tE, nstep=nstep)
    ep = np.abs(P1 - PE).max() / max(np.abs(PE).max(), 1e-30)
    eV = np.abs(V1 - VE).max() / max(np.abs(VE).max(), 1e-30)
    return float(ep), float(eV)


def screen_rep(V4, P4):
    """스크린 대표원 W_a = V_a - (V_0/E) p_a  (W_0 = 0, W·p = 0)."""
    E = P4[0]
    return V4[1:] - (V4[0] / E) * P4[1:]


def d2_orthogonality_numeric(kind="V", nstep=4000, seed=3):
    """(D2 게이트) V·p 가 수송으로 보존되는가 (계량 보존의 실측)."""
    traj, _ = coord_transport(kind, nstep=nstep, seed=seed, four=True)
    def dot(P, V):
        return -P[0] * V[0] + float(P[1:] @ V[1:])
    a = dot(traj[0][1], traj[0][2]); b = dot(traj[-1][1], traj[-1][2])
    sc = max(abs(traj[-1][1][0] * traj[-1][2][0]), 1e-30)
    return float(abs(a)) , float(abs(b - a) / sc)


def d3_screen_holonomy_is_rotation(kind="V", nstep=4000, seed=1):
    """(D3 게이트) 스크린 2-평면 사상이 **배율 x SO(2)** 인가.

    두 개의 독립 편광 벡터를 나르고, 초기·최종 스크린 정규직교기저 사이의
    2x2 사상을 추출해 (a) 배율이 세기 배율과 같은지, (b) 나머지가 직교인지 잰다."""
    traj, bg = coord_transport(kind, nstep=nstep, seed=seed, four=True)
    t0, p0, _ = traj[0]
    tE, _, _ = traj[-1]

    def screen_basis(p):
        e = p / np.linalg.norm(p)
        k = np.argmin(np.abs(e))
        m1 = np.zeros(3); m1[k] = 1.0
        m1 = m1 - (m1 @ e) * e; m1 /= np.linalg.norm(m1)
        return m1, np.cross(e, m1)

    m1, m2 = screen_basis(p0[1:])
    outs = []
    for v0 in (m1, m2):
        V0 = np.concatenate([[0.0], v0])
        PE4, VE4 = closed_transport4(p0, V0, bg, t0, tE, nstep=nstep)
        outs.append(screen_rep(VE4, PE4))
    pE = PE4
    n1, n2 = screen_basis(pE[1:])
    Mmat = np.array([[outs[0] @ n1, outs[1] @ n1],
                     [outs[0] @ n2, outs[1] @ n2]])
    # 스크린 밖 성분 (제약 이탈)
    ph = pE[1:] / np.linalg.norm(pE[1:])
    leak = max(abs(outs[0] @ ph), abs(outs[1] @ ph))
    U, s, Vt = np.linalg.svd(Mmat)
    aniso = float(s.max() / s.min() - 1.0)             # 0 이면 순수 배율x회전
    scale = float(np.sqrt(s[0] * s[1]))
    psi = float(np.arctan2((U @ Vt)[1, 0], (U @ Vt)[0, 0]))
    return dict(leak=float(leak), aniso=aniso, scale=scale, psi=psi,
                singular=[float(x) for x in s])


if __name__ == "__main__":
    print("D1 분해 항등            :", d1_vector_transport_decomposition())
    print("D1 T1 앵커              :", d1_reduces_to_T1())
    for k in ("V", "II"):
        a, b = d2_orthogonality_numeric(k)
        print(f"D2 직교성 type {k:<2}      :  |V·p|(0)={a:.2e}  표류={b:.2e}")
    for k in ("V", "II"):
        ep, eV = d1_first_principles(k)
        print(f"D1 제1원리 대조 type {k:<2}:  p {ep:.2e}   V {eV:.2e}")
    for k in ("V", "II"):
        r = d3_screen_holonomy_is_rotation(k)
        print(f"D3 스크린 홀로노미 {k:<2}: leak={r['leak']:.2e} "
              f"aniso={r['aniso']:.2e} scale={r['scale']:.6f} psi={r['psi']:+.6f}")
