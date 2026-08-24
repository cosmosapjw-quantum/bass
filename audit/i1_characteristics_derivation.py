"""
I1-계획 · class A 특성곡선의 선유도 (64차) — K4 (type V) 두-경로 방법론의 일반화.

규약: [e_b, e_c] = C^a_{bc} e_a,  class A: C^a_{bc} = ε_{bcd} n^{da}, n 대각.
정리 (T1): dp_a/dλ = C^c_{ba} p_c p^b — 하지수 (ba); (ab) 는 부호 반대 (적발용).
(T2): dp̂_a/dt = −(H+σ_aa)p̂_a + (1/Ê)((N·p̂)×p̂)_a, N_a = n_a a_a/(a_ba_c).
(T3): |p̂| N-정확불변.  (T4): l≤1 모멘트 정확 0, l=2 (12)율 = (4π/5)u₃(N₂−N₁).
전부 sympy 게이트 + Wolfram 이중엔진 (64차) 완료.
사용:  python -m audit.i1_characteristics_derivation
"""
from __future__ import annotations

import sympy as sp


def _eps():
    e = {}
    for a, b, c, s in [(0, 1, 2, 1), (1, 2, 0, 1), (2, 0, 1, 1),
                       (0, 2, 1, -1), (2, 1, 0, -1), (1, 0, 2, -1)]:
        e[(a, b, c)] = s
    return e


def route_a(p_lo, p_up, C):
    return [sum(C.get((c, b, a), 0) * p_lo[c] * p_up[b]
                for b in range(3) for c in range(3)) for a in range(3)]


def route_a_wrong_order(p_lo, p_up, C):
    return [sum(C.get((c, a, b), 0) * p_lo[c] * p_up[b]
                for b in range(3) for c in range(3)) for a in range(3)]


def class_a_C(n1, n2, n3):
    eps = _eps()
    n = [n1, n2, n3]
    C = {}
    for (b, c, d), s in eps.items():
        C[(d, b, c)] = C.get((d, b, c), 0) + s * n[d]
    return C


def type_ii_symbolic():
    t, x, y, z, lam, n1 = sp.symbols("t x y z lambda n1", real=True)
    a1, a2, a3 = [sp.Function(f"a{k}", positive=True)(t) for k in (1, 2, 3)]
    X = [t, x, y, z]
    dX = [sp.Symbol(f"d{s}", real=True) for s in ("t", "x", "y", "z")]
    g = sp.zeros(4, 4)
    g[0, 0] = -1
    g[1, 1] = a1**2
    g[2, 2] = a2**2
    g[1, 3] = g[3, 1] = -a1**2 * n1 * y
    g[3, 3] = a3**2 + a1**2 * n1**2 * y**2
    p_co = [sum(g[m, nn] * dX[nn] for nn in range(4)) for m in range(4)]
    dp_co = [sp.Rational(1, 2) * sum(sp.diff(g[al, be], X[m])
                                     * dX[al] * dX[be]
                                     for al in range(4) for be in range(4))
             for m in range(4)]
    p_inv = [p_co[1], p_co[2], p_co[3] + n1 * y * p_co[1]]
    dp_inv = [dp_co[1], dp_co[2],
              dp_co[3] + n1 * dX[2] * p_co[1] + n1 * y * dp_co[1]]
    p_up = [p_inv[0] / a1**2, p_inv[1] / a2**2, p_inv[2] / a3**2]
    C = class_a_C(n1, 0, 0)
    good = route_a(p_inv, p_up, C)
    bad = route_a_wrong_order(p_inv, p_up, C)
    return ([sp.simplify(dp_inv[a] - good[a]) for a in range(3)],
            [sp.simplify(dp_inv[a] - bad[a]) for a in range(3)])


def _su2_forms(th, ph, ps):
    return [
        [sp.cos(ps), sp.sin(ps) * sp.sin(th), 0],
        [sp.sin(ps), -sp.cos(ps) * sp.sin(th), 0],
        [0, sp.cos(th), 1],
    ]


def _forms_exact_point(forms, subs_pt, seed):
    t = sp.symbols("t", real=True)
    th, ph, ps = sp.symbols("theta phi psi", real=True)
    a = [sp.Function(f"a{k}", positive=True)(t) for k in (1, 2, 3)]
    q = [th, ph, ps]
    W = sp.Matrix(forms(th, ph, ps))
    E = W.inv()
    C = {}
    for b in range(3):
        for c in range(3):
            if b == c:
                continue
            comm = [sum(E[m, b] * sp.diff(E[k, c], q[m])
                        - E[m, c] * sp.diff(E[k, b], q[m])
                        for m in range(3)) for k in range(3)]
            coef = W * sp.Matrix(comm)
            for aa in range(3):
                v = sp.simplify(coef[aa])
                if v != 0:
                    C[(aa, b, c)] = v
    g3 = sum((a[k]**2 * W.row(k).T * W.row(k) for k in range(3)),
             sp.zeros(3, 3))
    import random
    rng = random.Random(seed)

    def r():
        return sp.Rational(rng.randint(-4, 4), rng.randint(2, 5))

    sub = dict(subs_pt)
    sub.update({a[0]: sp.Rational(3, 2), a[1]: sp.Rational(5, 4),
                a[2]: sp.Rational(7, 6)})
    dq = [r(), r(), r()]
    p_co = [sum(g3[m, nn] * dq[nn] for nn in range(3)) for m in range(3)]
    dp_co = [sp.Rational(1, 2) * sum(sp.diff(g3[al, be], q[m]) * dq[al] * dq[be]
                                     for al in range(3) for be in range(3))
             for m in range(3)]
    p_inv = [sum(p_co[m] * E[m, aa] for m in range(3)) for aa in range(3)]
    dE = [[sum(sp.diff(E[m, aa], q[k]) * dq[k] for k in range(3))
           for aa in range(3)] for m in range(3)]
    dp_inv = [sum(dp_co[m] * E[m, aa] + p_co[m] * dE[m][aa] for m in range(3))
              for aa in range(3)]
    p_up = [p_inv[aa] / a[aa]**2 for aa in range(3)]
    good = route_a(p_inv, p_up, C)
    resid = [sp.simplify((dp_inv[aa] - good[aa]).subs(sub)) for aa in range(3)]
    return resid, C, sub


def type_ix_exact_point(seed=0):
    th, ph, ps = sp.symbols("theta phi psi", real=True)
    pt = {th: sp.Rational(1, 3), ph: sp.Rational(2, 5), ps: sp.Rational(1, 7)}
    resid, C, sub = _forms_exact_point(_su2_forms, pt, seed)
    Cnum = {k: sp.simplify(v.subs(sub)) for k, v in C.items()}
    return resid, Cnum


def orthonormal_form_symbolic():
    t = sp.symbols("t", real=True)
    n1, n2, n3, m = sp.symbols("n1 n2 n3 m", real=True, positive=True)
    a = [sp.Function(f"a{k}", positive=True)(t) for k in (1, 2, 3)]
    ph = list(sp.symbols("ph1 ph2 ph3", real=True))
    n = [n1, n2, n3]
    p_lo = [a[k] * ph[k] for k in range(3)]
    p_up = [p_lo[k] / a[k]**2 for k in range(3)]
    C = class_a_C(n1, n2, n3)
    dp = route_a(p_lo, p_up, C)
    E_hat = sp.sqrt(m**2 + sum(x**2 for x in ph))
    H = sp.Function("H", real=True)(t)
    sig = [sp.Function(f"s{k}", real=True)(t) for k in (1, 2, 3)]
    adot_over_a = [H + sig[k] for k in range(3)]
    dphat = [sp.simplify(dp[k] / (a[k] * E_hat)
                         - adot_over_a[k] * ph[k]) for k in range(3)]
    N = [n[0] * a[0] / (a[1] * a[2]), n[1] * a[1] / (a[2] * a[0]),
         n[2] * a[2] / (a[0] * a[1])]
    u = [N[k] * ph[k] for k in range(3)]
    cross = [u[1]*ph[2] - u[2]*ph[1], u[2]*ph[0] - u[0]*ph[2],
             u[0]*ph[1] - u[1]*ph[0]]
    claim = [-adot_over_a[k] * ph[k] + cross[k] / E_hat for k in range(3)]
    resid = [sp.simplify(dphat[k] - claim[k]) for k in range(3)]
    mag = sp.simplify(sum(ph[k] * cross[k] for k in range(3)))
    return resid, mag


def dipole_curvature_coupling():
    th, ph_ = sp.symbols("theta phi", real=True)
    N1, N2, N3, u1, u2, u3 = sp.symbols("N1 N2 N3 u1 u2 u3", real=True)
    e = [sp.sin(th) * sp.cos(ph_), sp.sin(th) * sp.sin(ph_), sp.cos(th)]
    N = [N1, N2, N3]
    u = [u1, u2, u3]
    f = 1 + 3 * sum(u[k] * e[k] for k in range(3))
    w = [N[k] * e[k] for k in range(3)]
    edot = [w[1]*e[2] - w[2]*e[1], w[2]*e[0] - w[0]*e[2],
            w[0]*e[1] - w[1]*e[0]]
    integ = [sp.integrate(sp.integrate(
        (edot[k] * f) * sp.sin(th), (th, 0, sp.pi)), (ph_, 0, 2*sp.pi))
        for k in range(3)]
    return [sp.simplify(x * sp.Rational(3, 4) / sp.pi) for x in integ]


def quadrupole_curvature_coupling():
    th, ph_ = sp.symbols("theta phi", real=True)
    N1, N2, N3, u1, u2, u3 = sp.symbols("N1 N2 N3 u1 u2 u3", real=True)
    e = [sp.sin(th) * sp.cos(ph_), sp.sin(th) * sp.sin(ph_), sp.cos(th)]
    f = 1 + 3 * (u1*e[0] + u2*e[1] + u3*e[2])
    w = [N1*e[0], N2*e[1], N3*e[2]]
    ed = [w[1]*e[2] - w[2]*e[1], w[2]*e[0] - w[0]*e[2], w[0]*e[1] - w[1]*e[0]]
    q12 = sp.integrate(sp.integrate(
        (ed[0]*e[1] + e[0]*ed[1]) * f * sp.sin(th), (th, 0, sp.pi)),
        (ph_, 0, 2*sp.pi))
    return sp.simplify(q12 - 4*sp.pi*u3*(N2 - N1)/5)


def frame_covariance_exact_points(n_seeds=5):
    import random
    resids = []
    for seed in range(n_seeds):
        rng = random.Random(100 + seed)

        def r():
            return sp.Rational(rng.randint(-5, 5), rng.randint(1, 4))

        A = sp.Matrix(3, 3, lambda i, j: r())
        while A.det() == 0:
            A[0, 0] += 1
        Ad = sp.Matrix(3, 3, lambda i, j: r())
        C = {}
        for a in range(3):
            for b in range(3):
                for c in range(3):
                    if b != c:
                        C[(a, b, c)] = r()
        p = sp.Matrix([r(), r(), r()])
        m2 = sp.Rational(rng.randint(0, 4), 1)
        Ainv = A.inv()
        ginv = A.T * A
        E = sp.sqrt(m2 + (p.T * ginv * p)[0])
        gp = ginv * p
        dp = sp.Matrix([sum(C.get((k, j, i), 0) * p[k] * gp[j]
                            for j in range(3) for k in range(3)) / E
                        for i in range(3)])
        lhs = Ad * p + A * dp
        ph = A * p
        chat = {}
        for cc in range(3):
            for bb in range(3):
                for aa in range(3):
                    v = sum(A[bb, j] * A[aa, i] * C.get((k, j, i), 0)
                            * Ainv[k, cc]
                            for i in range(3) for j in range(3)
                            for k in range(3))
                    if v != 0:
                        chat[(cc, bb, aa)] = v
        rhs = Ad * Ainv * ph + sp.Matrix(
            [sum(chat.get((cc, bb, aa), 0) * ph[cc] * ph[bb]
                 for bb in range(3) for cc in range(3)) / E
             for aa in range(3)])
        resids.append([sp.simplify(x) for x in (lhs - rhs)])
    return resids


def class_a_cross_form_symbolic():
    eps = _eps()
    Nh = sp.Matrix(3, 3, lambda i, j: sp.Symbol(f"N{min(i,j)}{max(i,j)}",
                                                real=True))
    ph = sp.Matrix(sp.symbols("q1 q2 q3", real=True))
    quad = sp.zeros(3, 1)
    for aa in range(3):
        s = 0
        for bb in range(3):
            for cc in range(3):
                ch = sum(eps.get((bb, aa, d), 0) * Nh[d, cc] for d in range(3))
                s += ch * ph[cc] * ph[bb]
        quad[aa] = s
    Np = Nh * ph
    cross = sp.Matrix([Np[1]*ph[2] - Np[2]*ph[1],
                       Np[2]*ph[0] - Np[0]*ph[2],
                       Np[0]*ph[1] - Np[1]*ph[0]])
    return [sp.simplify(quad[k] - cross[k]) for k in range(3)]


def _sl2_forms(th, ph, ps):
    return [
        [sp.cos(ps), sp.sin(ps) * sp.sinh(th), 0],
        [sp.sin(ps), -sp.cos(ps) * sp.sinh(th), 0],
        [0, sp.cosh(th), 1],
    ]


def type_viii_exact_point(seed=1):
    th, ph, ps = sp.symbols("theta phi psi", real=True)
    pt = {th: sp.Rational(2, 7), ph: sp.Rational(1, 5), ps: sp.Rational(3, 8)}
    resid, C, sub = _forms_exact_point(_sl2_forms, pt, seed)
    signs = sorted(sp.sign(v.subs(sub)) for v in C.values())
    return resid, signs


def type_ii_general_metric_symbolic():
    t, x, y, z, n1 = sp.symbols("t x y z n1", real=True)
    G = sp.Matrix(3, 3, lambda i, j: sp.Function(
        f"g{min(i,j)}{max(i,j)}", real=True)(t))
    dX = [sp.Symbol(f"d{s}", real=True) for s in ("t", "x", "y", "z")]
    Wm = sp.Matrix([[1, 0, -n1 * y], [0, 1, 0], [0, 0, 1]])
    g3 = Wm.T * G * Wm
    X = [t, x, y, z]
    g = sp.zeros(4, 4)
    g[0, 0] = -1
    for i in range(3):
        for j in range(3):
            g[i + 1, j + 1] = g3[i, j]
    p_co = [sum(g[m, nn] * dX[nn] for nn in range(4)) for m in range(4)]
    dp_co = [sp.Rational(1, 2) * sum(sp.diff(g[al, be], X[m])
                                     * dX[al] * dX[be]
                                     for al in range(4) for be in range(4))
             for m in range(4)]
    p_inv = [p_co[1], p_co[2], p_co[3] + n1 * y * p_co[1]]
    dp_inv = [dp_co[1], dp_co[2],
              dp_co[3] + n1 * dX[2] * p_co[1] + n1 * y * dp_co[1]]
    Ginv = G.inv()
    p_up = [sum(Ginv[b, c] * p_inv[c] for c in range(3)) for b in range(3)]
    C = class_a_C(n1, 0, 0)
    good = route_a(p_inv, p_up, C)
    return [sp.simplify(dp_inv[a] - good[a]) for a in range(3)]
