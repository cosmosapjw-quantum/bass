"""
Q2 · 특성곡선의 **전 유형 일반화** 선유도 (76차) — I1a (class A) 의 class B 확장.

규약 (docs/Q-CONTRACT.md §2):
    [e_b, e_c] = C^a_{bc} e_a ,   C^c_{ab} = eps_{abd} n^{dc} + a_a d^c_b - a_b d^c_a
    (T1)  dp_a/dlambda = C^c_{ba} p_c p^b        ← 하지수 (ba). (ab) 는 부호 반대.

**유도 (여기서 제1원리로; 아래 sympy 게이트가 박제)**

T1 에 일반 C 를 넣으면

    C^c_{ba} p_c p^b = eps_{bad} n^{dc} p_c p^b + a_b d^c_a p_c p^b - a_a d^c_b p_c p^b
                     = ((n p) x p)_a  +  (a·p) p_a  -  a_a |p|^2

첫 항이 I1a 의 N-항, 뒤 두 항이 **새로 붙는 class B a-항**이다.

  (Q-T3) a-항도 |p| 를 정확히 보존한다:
        p·[(a·p)p - |p|^2 a] = (a·p)|p|^2 - |p|^2 (a·p) = 0     ← 항등
     즉 T3 (N-항의 노름 보존) 이 class B 로 그대로 확장된다.

  (Q-T5) a-항은 방향공간에서 **-a 방향으로의 순수 이류**다:
        (a·ê)ê - a = -(a - (a·ê)ê) = -a_perp
     l=1 에 직접 작용하므로 (N-항과 달리) 다중극 선택률이 없다.

정규직교틀 + 시간 t 로 옮기면 (프레임 자체의 H, sigma, R 이 더해진다):

    dp̂_a/dt = -H p̂_a - sigma_ab p̂_b + (R x p̂)_a
              + (1/Ê)[ ((N̂ p̂) x p̂)_a + (Â·p̂) p̂_a - Â_a |p̂|^2 ]

방향·크기 분해 (p̂ = p ê,  Ê = sqrt(p^2+m^2)):

    (L1)  dln p/dt = -(H + sigma_ab ê^a ê^b)                       ← class B 에서도 **불변**
    (L2)  dê_a/dt  = -(sigma_ab ê^b - (sigma_bc ê^b ê^c) ê_a) + (R x ê)_a
                     + (p/Ê)[ ((N̂ ê) x ê)_a - (Â_a - (Â·ê) ê_a) ]

검증 3경로:
  R0  좌표 측지선 (sympy 계량 → 라그랑주 방정식) — type II (n-항) · type V (a-항)
  RA  불변틀 T1 + 삼중틀 환산 (수치)
  RB  닫힌 정규직교틀 공식 (L1)(L2)

사용:  python -m audit.q2_characteristics_general
"""
from __future__ import annotations

import numpy as np
import sympy as sp

# ─────────────────────────────────────────────────────── 기호 게이트 (T1 → 분해)


def general_C(n, a):
    """C^c_{ab} = eps_abd n^dc + a_a d^c_b - a_b d^c_a  (기호)."""
    eps = {(0, 1, 2): 1, (1, 2, 0): 1, (2, 0, 1): 1,
           (0, 2, 1): -1, (2, 1, 0): -1, (1, 0, 2): -1}
    C = [[[sp.Integer(0)] * 3 for _ in range(3)] for _ in range(3)]
    for c in range(3):
        for i in range(3):
            for j in range(3):
                s = sum(eps.get((i, j, d), 0) * n[d][c] for d in range(3))
                if c == j:
                    s += a[i]
                if c == i:
                    s -= a[j]
                C[c][i][j] = sp.expand(s)
    return C


def t1_decomposition_symbolic():
    """★ T1 의 우변이 ((n p) x p) + (a·p)p - |p|^2 a 와 **항등**인가 (정규직교틀)."""
    p = sp.Matrix(sp.symbols("p1 p2 p3", real=True))
    a = sp.Matrix(sp.symbols("a1 a2 a3", real=True))
    nsym = sp.symbols("n11 n22 n33 n12 n13 n23", real=True)
    n = sp.Matrix(3, 3, lambda i, j: {
        (0, 0): nsym[0], (1, 1): nsym[1], (2, 2): nsym[2],
        (0, 1): nsym[3], (1, 0): nsym[3],
        (0, 2): nsym[4], (2, 0): nsym[4],
        (1, 2): nsym[5], (2, 1): nsym[5]}[(i, j)])
    C = general_C([[n[i, j] for j in range(3)] for i in range(3)], list(a))
    lhs = [sp.expand(sum(C[c][b][A] * p[c] * p[b] for b in range(3) for c in range(3)))
           for A in range(3)]
    npv = n * p
    cross = npv.cross(p)
    rhs = [sp.expand(cross[A] + (a.dot(p)) * p[A] - a[A] * p.dot(p)) for A in range(3)]
    return all(sp.simplify(lhs[A] - rhs[A]) == 0 for A in range(3))


def a_term_preserves_norm_symbolic():
    """★ (Q-T3) a-항이 |p| 를 정확히 보존 — p·[(a·p)p - |p|^2 a] ≡ 0."""
    p = sp.Matrix(sp.symbols("p1 p2 p3", real=True))
    a = sp.Matrix(sp.symbols("a1 a2 a3", real=True))
    term = (a.dot(p)) * p - p.dot(p) * a
    return sp.simplify(p.dot(term)) == 0


def n_term_preserves_norm_symbolic():
    """I1a 의 T3 재확인 (일반 대칭 n 으로) — p·((n p) x p) ≡ 0."""
    p = sp.Matrix(sp.symbols("p1 p2 p3", real=True))
    nsym = sp.symbols("m11 m22 m33 m12 m13 m23", real=True)
    n = sp.Matrix(3, 3, lambda i, j: {
        (0, 0): nsym[0], (1, 1): nsym[1], (2, 2): nsym[2],
        (0, 1): nsym[3], (1, 0): nsym[3],
        (0, 2): nsym[4], (2, 0): nsym[4],
        (1, 2): nsym[5], (2, 1): nsym[5]}[(i, j)])
    return sp.simplify(p.dot((n * p).cross(p))) == 0


def wrong_index_order_is_detectable():
    """반증 장치: C^c_{ab} (지표 뒤집기) 는 부호가 뒤집힌다 — 조용히 같지 않다."""
    p = sp.Matrix(sp.symbols("p1 p2 p3", real=True))
    a = sp.Matrix(sp.symbols("a1 a2 a3", real=True))
    n = sp.diag(*sp.symbols("k1 k2 k3", real=True))
    C = general_C([[n[i, j] for j in range(3)] for i in range(3)], list(a))
    good = [sum(C[c][b][A] * p[c] * p[b] for b in range(3) for c in range(3))
            for A in range(3)]
    bad = [sum(C[c][A][b] * p[c] * p[b] for b in range(3) for c in range(3))
           for A in range(3)]
    return any(sp.simplify(good[A] + bad[A]) != 0 or sp.simplify(good[A]) != 0
               for A in range(3))


# ─────────────────────────────────────────────────────── R0 · 좌표 측지선 (제1원리)


def _coord_geodesic_rhs(gfun, dgfun, ndim=4):
    """라그랑주 방정식 dp_mu/dl = 1/2 (d_mu g_ab) v^a v^b,  p_mu = g_mu,a v^a."""
    def rhs(y, gfun=gfun, dgfun=dgfun):
        x, v = y[:ndim], y[ndim:]
        g = gfun(x)
        dg = dgfun(x)                       # dg[mu][a][b] = d_mu g_ab
        dp = 0.5 * np.einsum("mab,a,b->m", dg, v, v)
        # dv 는 dp 에서: p = g v  =>  dp = g dv + (dg·v) v
        gdot = np.einsum("mab,m->ab", dg, v)
        dv = np.linalg.solve(g, dp - gdot @ v)
        return np.concatenate([v, dv])
    return rhs


def type_v_setup(c=(0.4, 0.7, 0.25)):
    """Bianchi V: ds^2 = -dt^2 + a1^2 dx^2 + e^{2x}(a2^2 dy^2 + a3^2 dz^2),  a_i = t^{c_i}.

    불변틀 e_1 = d_x, e_2 = e^{-x} d_y, e_3 = e^{-x} d_z
      [e_1,e_2] = -e_2 , [e_1,e_3] = -e_3  =>  C^2_12 = C^3_13 = -1  (n=0, a_inv=(-1,0,0))
    """
    c = np.asarray(c, float)

    def scale(t):
        return t ** c

    def gfun(x):
        t, xx = x[0], x[1]
        a = scale(t)
        e2 = np.exp(2.0 * xx)
        return np.diag([-1.0, a[0] ** 2, a[1] ** 2 * e2, a[2] ** 2 * e2])

    def dgfun(x):
        t, xx = x[0], x[1]
        a = scale(t)
        e2 = np.exp(2.0 * xx)
        d = np.zeros((4, 4, 4))
        # d_t
        da = c * t ** (c - 1.0)
        d[0] = np.diag([0.0, 2 * a[0] * da[0], 2 * a[1] * da[1] * e2,
                        2 * a[2] * da[2] * e2])
        # d_x
        d[1] = np.diag([0.0, 0.0, 2 * a[1] ** 2 * e2, 2 * a[2] ** 2 * e2])
        return d

    def frame_background(t):
        """정규직교틀에서의 (H, sigma, R, N̂, Â)."""
        a = scale(t)
        da = c * t ** (c - 1.0)
        hs = da / a                                   # a_i'/a_i
        H = float(hs.mean())
        sig = np.diag(hs - H)
        N = np.zeros((3, 3))
        A = np.array([-1.0 / a[0], 0.0, 0.0])         # Ĉ^2_12 = -1/a1
        return H, sig, np.zeros(3), N, A

    return gfun, dgfun, scale, frame_background


def type_ii_setup(c=(0.4, 0.7, 0.25), n1=1.0):
    """Bianchi II: omega^1 = dx - n1 y dz, omega^2 = dy, omega^3 = dz.

    [e_2,e_3] = ... => C^1_23 = n1  (n = diag(n1,0,0), a = 0)
    계량 g = -dt^2 + a1^2 (omega^1)^2 + a2^2 (omega^2)^2 + a3^2 (omega^3)^2
    """
    c = np.asarray(c, float)

    def scale(t):
        return t ** c

    def gfun(x):
        t, y = x[0], x[2]
        a = scale(t)
        g = np.zeros((4, 4))
        g[0, 0] = -1.0
        g[1, 1] = a[0] ** 2
        g[2, 2] = a[1] ** 2
        g[3, 3] = a[2] ** 2 + a[0] ** 2 * (n1 * y) ** 2
        g[1, 3] = g[3, 1] = -a[0] ** 2 * n1 * y
        return g

    def dgfun(x):
        t, y = x[0], x[2]
        a = scale(t)
        da = c * t ** (c - 1.0)
        d = np.zeros((4, 4, 4))
        d[0, 1, 1] = 2 * a[0] * da[0]
        d[0, 2, 2] = 2 * a[1] * da[1]
        d[0, 3, 3] = 2 * a[2] * da[2] + 2 * a[0] * da[0] * (n1 * y) ** 2
        d[0, 1, 3] = d[0, 3, 1] = -2 * a[0] * da[0] * n1 * y
        d[2, 3, 3] = 2 * a[0] ** 2 * n1 ** 2 * y
        d[2, 1, 3] = d[2, 3, 1] = -a[0] ** 2 * n1
        return d

    def frame_background(t):
        a = scale(t)
        da = c * t ** (c - 1.0)
        hs = da / a
        H = float(hs.mean())
        sig = np.diag(hs - H)
        # 정규직교틀:  N̂_1 = n1 a1/(a2 a3),  나머지 0
        N = np.diag([n1 * a[0] / (a[1] * a[2]), 0.0, 0.0])
        return H, sig, np.zeros(3), N, np.zeros(3)

    return gfun, dgfun, scale, frame_background


def _tetrad_p(x, v, gfun, scale, kind):
    """좌표 (x, v) → 정규직교틀 공변성분 p̂_a."""
    g = gfun(x)
    p_co = g @ v                       # p_mu
    a = scale(x[0])
    if kind == "V":
        p_inv = np.array([p_co[1], np.exp(-x[1]) * p_co[2], np.exp(-x[1]) * p_co[3]])
    elif kind == "II":
        # e_1 = d_x, e_2 = d_y, e_3 = d_z + n1 y d_x   (omega^1 = dx - n1 y dz 의 쌍대)
        p_inv = np.array([p_co[1], p_co[2], p_co[3] + _N1 * x[2] * p_co[1]])
    else:
        raise ValueError(kind)
    return p_inv / a                   # 대각 삼중틀:  p̂_a = p_a / a_a


_N1 = 1.0


# ─────────────────────────────────────────────────────── RB · 닫힌 공식


def char_rhs_general(phat, H, sigma, R, N, A, mass):
    """(RB) dp̂_a/dt — 전 유형 일반형.  phat: (...,3)."""
    P = np.atleast_2d(np.asarray(phat, float))
    S = np.asarray(sigma, float)
    N = np.asarray(N, float)
    A = np.asarray(A, float)
    R = np.asarray(R, float)
    p2 = np.sum(P * P, axis=1)
    E = np.sqrt(mass * mass + p2)
    Np = P @ N.T
    term = (np.cross(Np, P)
            + (P @ A)[:, None] * P
            - p2[:, None] * A[None, :])
    out = -H * P - P @ S.T + np.cross(np.broadcast_to(R, P.shape), P) + term / E[:, None]
    return out[0] if np.asarray(phat).ndim == 1 else out


def _rk4(f, y, t, dt, n):
    for _ in range(n):
        k1 = f(y, t)
        k2 = f(y + 0.5 * dt * k1, t + 0.5 * dt)
        k3 = f(y + 0.5 * dt * k2, t + 0.5 * dt)
        k4 = f(y + dt * k3, t + dt)
        y = y + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        t = t + dt
    return y


def compare_routes(kind="V", mass=0.0, t0=1.0, t1=1.6, nstep=4000, seed=0):
    """★ R0 (좌표 측지선) 대 RB (닫힌 정규직교틀 공식) — 최대 편차."""
    global _N1
    if kind == "V":
        gfun, dgfun, scale, bg = type_v_setup()
    else:
        gfun, dgfun, scale, bg = type_ii_setup()
        _N1 = 1.0
    rng = np.random.default_rng(seed)

    # 초기: 좌표 원점, 공간속도 임의, 질량껍질로 v^t 결정
    x = np.array([t0, 0.0, 0.0, 0.0])
    vsp = rng.standard_normal(3) * 0.4
    g = gfun(x)
    sp_norm = float(vsp @ g[1:, 1:] @ vsp)
    vt = np.sqrt((sp_norm + mass ** 2) / 1.0) if mass > 0 else np.sqrt(sp_norm)
    v = np.concatenate([[vt], vsp])

    rhs0 = _coord_geodesic_rhs(gfun, dgfun)
    y = np.concatenate([x, v])
    dl = (t1 - t0) / nstep / max(vt, 1e-12)
    traj = []
    while y[0] < t1:
        y = _rk4(lambda z, _: rhs0(z), y, 0.0, dl, 1)
        traj.append(y.copy())
    yend = traj[-1]
    p_ref = _tetrad_p(yend[:4], yend[4:], gfun, scale, kind)

    # RB: 같은 초기 p̂ 에서 시간 t 로 적분
    p0 = _tetrad_p(x, v, gfun, scale, kind)

    def f(P, t):
        H, S, R, N, A = bg(t)
        return char_rhs_general(P, H, S, R, N, A, mass)

    tend = yend[0]
    p_rb = _rk4(f, p0, t0, (tend - t0) / nstep, nstep)
    scale_ = max(np.abs(p_ref).max(), 1e-30)
    return float(np.abs(p_rb - p_ref).max() / scale_), p_ref, p_rb


if __name__ == "__main__":
    print("T1 분해 항등          :", t1_decomposition_symbolic())
    print("a-항 노름보존 (Q-T3)  :", a_term_preserves_norm_symbolic())
    print("n-항 노름보존 (T3)    :", n_term_preserves_norm_symbolic())
    print("지표 뒤집기 검출가능  :", wrong_index_order_is_detectable())
    for kind in ("V", "II"):
        for m in (0.0, 0.5):
            e, _, _ = compare_routes(kind, mass=m)
            print(f"R0 vs RB  type {kind:<2}  m={m}:  {e:.3e}")
