"""
Full 4d orthonormal-frame Einstein tensor for a spatially homogeneous model,
derived from the structure constants alone (no coordinates, no metric ansatz).

e_0 = unit normal (geodesic, hypersurface orthogonal),  e_alpha spatial ON triad
  [e_0, e_a] = -Theta^b_a e_b ,  Theta = H delta + sigma + Omega ,  Omega^b_a = eps_{bag} R^g
  [e_a, e_b] = eps_{abd} n^{dc} e_c + a_a e_b - a_b e_a
Units 8 pi G = c = 1, signature (-,+,+,+).
"""
import sympy as sp
import itertools

I3 = range(3)
I4 = range(4)
eta = sp.diag(-1, 1, 1, 1)
eps = sp.MutableDenseNDimArray.zeros(3, 3, 3)
for i, j, k in itertools.product(I3, I3, I3):
    eps[i, j, k] = sp.Integer(((i - j) * (j - k) * (k - i)) // 2)
t = sp.Symbol('t')


def build(with_rotation=True):
    H = sp.Function('H')(t)
    n = sp.Matrix(3, 3, lambda i, j: sp.Function(f'n{min(i,j)}{max(i,j)}')(t))
    a = sp.Matrix(3, 1, lambda i, j: sp.Function(f'a{i}')(t))
    sfun = [[sp.Function('s00')(t), sp.Function('s01')(t), sp.Function('s02')(t)],
            [sp.Function('s01')(t), sp.Function('s11')(t), sp.Function('s12')(t)],
            [sp.Function('s02')(t), sp.Function('s12')(t), None]]
    sfun[2][2] = -sfun[0][0] - sfun[1][1]
    s = sp.Matrix(3, 3, lambda i, j: sfun[i][j])
    R = sp.Matrix(3, 1, lambda i, j: sp.Function(f'R{i}')(t) if with_rotation else sp.Integer(0))
    Om = sp.Matrix(3, 3, lambda i, j: sum(eps[i, j, g] * R[g] for g in I3))
    Th = H * sp.eye(3) + s + Om

    C = [[[sp.Integer(0)] * 4 for _ in I4] for _ in I4]           # C[c][a][b]
    for al, be in itertools.product(I3, I3):
        for ga in I3:
            C[ga + 1][al + 1][be + 1] = (sum(eps[al, be, dd] * n[dd, ga] for dd in I3)
                                         + a[al] * sp.eye(3)[ga, be] - a[be] * sp.eye(3)[ga, al])
        C[be + 1][0][al + 1] = -Th[be, al]
        C[be + 1][al + 1][0] = +Th[be, al]
    return dict(H=H, n=n, a=a, s=s, R=R, C=C)


def connection(C):
    """solve for Gamma^a_{bc}  (nabla_c e_b = Gamma^a_{bc} e_a)."""
    G = [[[sp.Symbol(f'G_{a}_{b}_{c}') for c in I4] for b in I4] for a in I4]
    eqs = []
    for a, b, c in itertools.product(I4, I4, I4):
        # torsion free:  Gamma^a_{cb} - Gamma^a_{bc} = C^a_{bc}
        eqs.append(sp.Eq(G[a][c][b] - G[a][b][c], C[a][b][c]))
        # metric compatibility:  Gamma_{abc} = -Gamma_{bac}
        eqs.append(sp.Eq(eta[a, a] * G[a][b][c] + eta[b, b] * G[b][a][c], 0))
    unk = [G[a][b][c] for a, b, c in itertools.product(I4, I4, I4)]
    sol = sp.solve(eqs, unk, dict=True)[0]
    return [[[sp.expand(sol.get(G[a][b][c], G[a][b][c])) for c in I4] for b in I4] for a in I4]


def jacobi_subs(m):
    """ndot, adot forced by the 4d Jacobi identity (derived & verified in r1_*.py)."""
    H, n, a, s, R = m['H'], m['n'], m['a'], m['s'], m['R']
    ndot = sp.Matrix(3, 3, lambda i, j: sp.expand(
        -H * n[i, j]
        + sum(n[i, c] * s[j, c] + n[j, c] * s[i, c] for c in I3)
        + sum(eps[c, dd, i] * n[j, c] * R[dd] + eps[c, dd, j] * n[i, c] * R[dd]
              for c in I3 for dd in I3)))
    adot = sp.Matrix(3, 1, lambda i, j: sp.expand(
        -H * a[i] - sum(s[i, b] * a[b] for b in I3)
        + sum(eps[i, b, c] * a[b] * R[c] for b in I3 for c in I3)))
    sub = {}
    for i, j in ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)):
        sub[sp.Derivative(n[i, j], t)] = ndot[i, j]
    for i in I3:
        sub[sp.Derivative(a[i], t)] = adot[i]
    return sub


def einstein(with_rotation=True):
    m = build(with_rotation)
    C, G = m['C'], connection(m['C'])

    def de(idx, expr):
        return sp.diff(expr, t) if idx == 0 else sp.Integer(0)

    Riem = [[[[sp.Integer(0)] * 4 for _ in I4] for _ in I4] for _ in I4]
    for a, b, c, dd in itertools.product(I4, I4, I4, I4):
        Riem[a][b][c][dd] = sp.expand(
            de(c, G[a][b][dd]) - de(dd, G[a][b][c])
            + sum(G[a][e][c] * G[e][b][dd] - G[a][e][dd] * G[e][b][c] for e in I4)
            - sum(G[a][b][e] * C[e][c][dd] for e in I4))
    Ric = sp.Matrix(4, 4, lambda b, dd: sp.expand(sum(Riem[a][b][a][dd] for a in I4)))
    Rs = sp.expand(sum(eta[i, i] * Ric[i, i] for i in I4))
    Ein = sp.Matrix(4, 4, lambda i, j: sp.expand(Ric[i, j] - Rs * eta[i, j] / 2))
    js = jacobi_subs(m)
    Ein = sp.Matrix(4, 4, lambda i, j: sp.expand(Ein[i, j].subs(js, simultaneous=True)))
    Ric = sp.Matrix(4, 4, lambda i, j: sp.expand(Ric[i, j].subs(js, simultaneous=True)))
    Riem = [[[[sp.expand(Riem[a][b][c][dd].subs(js, simultaneous=True))
                for dd in I4] for c in I4] for b in I4] for a in I4]
    m.update(G=G, Ric=Ric, Rscalar=sp.expand(Rs.subs(js, simultaneous=True)),
             G4=Ein, jacobi=js, Riem=Riem)
    return m


if __name__ == '__main__':
    # v1.3 (audit F4): the old self-check block carried stale, WRONG reference
    # formulas (G00 with -R3/2, Codazzi with the opposite eps order, shear eq
    # with v1.0 rotation bookkeeping) and shipped their nonzero residuals to
    # einstein_frame.json without any gate.  Replaced by numeric evaluation
    # against the coefficient-identified blocks of fit_einstein.py:
    #   G00        = 3H^2 - (1/2) sigma_ab sigma^ab + (1/2) ^3R
    #   G0i        = -3 sigma_i^b a_b + eps_ibc sigma^b_d n^cd
    #   tr G_ij    = -6 Hdot - 9H^2 - (3/2) sigma_ab sigma^ab - (1/2) ^3R
    #   G_<ij>     = sigmadot + 3H sigma + ^3S + 2 eps_{cd<a} R^c sigma_b>^d
    # (all in ENGINE R = R_gen = -R_comm).
    import json
    import numpy as np
    from core import EPS, stf, sym, ricci3, S3_explicit, R3_explicit

    m = einstein(with_rotation=True)
    H_, n_, a_, s_, R_, Ein = m['H'], m['n'], m['a'], m['s'], m['R'], m['G4']
    Hd_ = sp.Derivative(H_, t)
    sd_ = [sp.Derivative(s_[i, j], t) for i, j in
           ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2))]
    SY = [H_] + [n_[0, 0], n_[0, 1], n_[0, 2], n_[1, 1], n_[1, 2], n_[2, 2]] \
         + [a_[0], a_[1], a_[2]] \
         + [s_[0, 0], s_[0, 1], s_[0, 2], s_[1, 1], s_[1, 2]] \
         + [R_[0], R_[1], R_[2]] + [Hd_] + sd_
    pl = {x: sp.Symbol('w%d' % i) for i, x in enumerate(SY)}
    fE = sp.lambdify(list(pl.values()),
                     [[sp.expand(Ein[i, j]).subs(pl, simultaneous=True)
                       for j in range(4)] for i in range(4)], 'numpy')
    rng = np.random.default_rng(20260729)
    res = dict(G00=0.0, G0i=0.0, trGij=0.0, Gij_tf=0.0)
    for _ in range(200):
        N = sym(rng.normal(size=(3, 3)))
        w, V = np.linalg.eigh(N); k = int(np.argmin(abs(w))); w[k] = 0.0
        N = V @ np.diag(w) @ V.T
        A = float(rng.normal()) * V[:, k]
        S = stf(rng.normal(size=(3, 3))); Sd = stf(rng.normal(size=(3, 3)))
        Rv = rng.normal(size=3)
        Hv = float(rng.uniform(0.5, 2.0)); Hdv = float(rng.normal())
        args = ([Hv, N[0, 0], N[0, 1], N[0, 2], N[1, 1], N[1, 2], N[2, 2],
                 A[0], A[1], A[2], S[0, 0], S[0, 1], S[0, 2], S[1, 1], S[1, 2],
                 Rv[0], Rv[1], Rv[2], Hdv,
                 Sd[0, 0], Sd[0, 1], Sd[0, 2], Sd[1, 1], Sd[1, 2]])
        G = np.array(fE(*args), float)
        sig2 = 0.5 * float(np.sum(S * S))
        R3 = R3_explicit(N, A)
        res['G00'] = max(res['G00'], abs(G[0, 0] - (3 * Hv ** 2 - sig2 + R3 / 2)))
        ref0i = -3.0 * (S @ A) + np.einsum('ibc,bd,cd->i', EPS, S, N)
        res['G0i'] = max(res['G0i'], float(np.abs(G[0, 1:] - ref0i).max()))
        res['trGij'] = max(res['trGij'], abs(np.trace(G[1:, 1:])
                           - (-6 * Hdv - 9 * Hv ** 2 - 3 * sig2 - R3 / 2)))
        rot = 2.0 * stf(np.einsum('cda,c,bd->ab', EPS, Rv, S))
        ref_tf = Sd + 3 * Hv * S + S3_explicit(N, A) + rot
        res['Gij_tf'] = max(res['Gij_tf'],
                            float(np.abs(stf(G[1:, 1:]) - ref_tf).max()))
    print(json.dumps(res, indent=2))
    json.dump(res, open('einstein_frame.json', 'w'), indent=2)
