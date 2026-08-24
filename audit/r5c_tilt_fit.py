"""
Exact tilted gamma-law fluid EOM by coefficient identification.

The 4d conservation law  nabla^a T_ab = 0  is LINEAR in (rho_dot, v_dot_a).
We build that 4x4 system symbolically once, evaluate it at random numeric
geometries, solve, and then identify  G_- * v_a'  and  G_+ * Omega'  against a
tensor basis by least squares.  Coefficients come out as exact integers/halves.
"""
import sympy as sp, numpy as np, itertools, json
from einstein_frame import einstein, jacobi_subs, eps, eta, I3, I4, t
from core import EPS, stf, sym

m = einstein(with_rotation=True)
H, n, a, s, R, Gam = m['H'], m['n'], m['a'], m['s'], m['R'], m['G']
js = jacobi_subs(m)
g4 = sp.diag(-1, 1, 1, 1)

gam = sp.Symbol('gamma', positive=True)
rf = sp.Function('rho')(t)
v = sp.Matrix(3, 1, lambda i, j: sp.Function(f'v{i}')(t))
V2 = sum(v[i] ** 2 for i in I3)
ul = sp.Matrix(4, 1, [-1, v[0], v[1], v[2]])
T = sp.Matrix(4, 4, lambda i, j: sp.expand(
    gam * rf * ul[i] * ul[j] / (1 - V2) + (gam - 1) * rf * g4[i, j]))


def div_T(T):
    o = []
    for b in I4:
        tot = sp.Integer(0)
        for c in I4:
            inner = (sp.diff(T[c, b], t) if c == 0 else sp.Integer(0))
            inner -= sum(Gam[d][c][c] * T[d, b] for d in I4)
            inner -= sum(Gam[d][b][c] * T[c, d] for d in I4)
            tot += eta[c, c] * inner
        o.append(tot)
    return o


D = [x.subs(js, simultaneous=True) for x in div_T(T)]
rd, vd = sp.symbols('rd'), sp.symbols('vd0 vd1 vd2')
repl = {sp.Derivative(rf, t): rd}
for i in I3:
    repl[sp.Derivative(v[i], t)] = vd[i]
D = [sp.expand(sp.together(x).subs(repl, simultaneous=True)) for x in D]

SY = [H, gam, rf] + [n[0, 0], n[0, 1], n[0, 2], n[1, 1], n[1, 2], n[2, 2]] \
     + [a[0], a[1], a[2]] + [s[0, 0], s[0, 1], s[0, 2], s[1, 1], s[1, 2]] \
     + [R[0], R[1], R[2]] + [v[0], v[1], v[2]]
plain = {x: sp.Symbol('p%d' % i) for i, x in enumerate(SY)}
Dp = [sp.expand(x.subs(plain, simultaneous=True)) for x in D]
unk = [rd] + list(vd)
Amat, bvec = sp.linear_eq_to_matrix(Dp, unk)
fA = sp.lambdify(list(plain.values()), Amat, 'numpy')
fb = sp.lambdify(list(plain.values()), bvec, 'numpy')

rng = np.random.default_rng(4242)


def draw():
    Hv = float(rng.uniform(0.5, 2.0)); gv = float(rng.uniform(0.3, 1.9))
    rv = float(rng.uniform(0.2, 2.0))
    N = sym(rng.normal(size=(3, 3)))
    w, V = np.linalg.eigh(N); k = int(np.argmin(abs(w))); w[k] = 0.0
    N = V @ np.diag(w) @ V.T; A = float(rng.normal()) * V[:, k]
    S = stf(rng.normal(size=(3, 3))); Rv = rng.normal(size=3)
    vv = rng.normal(size=3); vv *= rng.uniform(0.05, 0.9) / np.linalg.norm(vv)
    return Hv, gv, rv, N, A, S, Rv, vv


def flat(Hv, gv, rv, N, A, S, Rv, vv):
    return [Hv, gv, rv, N[0, 0], N[0, 1], N[0, 2], N[1, 1], N[1, 2], N[2, 2],
            A[0], A[1], A[2], S[0, 0], S[0, 1], S[0, 2], S[1, 1], S[1, 2],
            Rv[0], Rv[1], Rv[2], vv[0], vv[1], vv[2]]


# ---------------- basis for  G_- * v_a' / H   (Hubble-normalised) --------------
def basis_v(Hv, gv, rv, N, A, S, Rv, vv):
    V2_ = float(vv @ vv); Adv = float(A @ vv) / Hv; Sv = float(vv @ (S @ vv)) / Hv
    Sig = S / Hv; Nn = N / Hv; Aa = A / Hv; Rr = Rv / Hv
    W = -np.einsum('abc,c->ab', EPS, Rr)
    g = gv
    return {
        'v': vv, 'V2 v': V2_ * vv, '(A.v) v': Adv * vv, '(A.v)V2 v': Adv * V2_ * vv,
        'S v': Sv * vv, 'S V2 v': Sv * V2_ * vv,
        'g v': g * vv, 'g V2 v': g * V2_ * vv, 'g (A.v) v': g * Adv * vv,
        'g S v': g * Sv * vv, 'g^2 (A.v) v': g * g * Adv * vv,
        'Sig.v': Sig @ vv, 'g Sig.v': g * (Sig @ vv), 'V2 Sig.v': V2_ * (Sig @ vv),
        'g V2 Sig.v': g * V2_ * (Sig @ vv),
        'W.v': W @ vv, 'g W.v': g * (W @ vv),
        'A': Aa, 'V2 A': V2_ * Aa, 'g A': g * Aa, 'g V2 A': g * V2_ * Aa,
        'eps(v,A)': np.einsum('abc,b,c->a', EPS, vv, Aa),
        'eps(v,N.v)': np.einsum('abc,b,c->a', EPS, vv, Nn @ vv),
        'g eps(v,N.v)': g * np.einsum('abc,b,c->a', EPS, vv, Nn @ vv),
        '(vNv) v': float(vv @ (Nn @ vv)) * vv,
        'N.v': Nn @ vv, 'trN v': float(np.trace(Nn)) * vv,
    }


keys = list(basis_v(*draw()).keys())
rows, rhs = [], []
for _ in range(400):
    st = draw()
    Hv, gv, rv, N, A, S, Rv, vv = st
    x = flat(*st)
    sol = np.linalg.solve(np.array(fA(*x), float), np.array(fb(*x), float).ravel())
    vdot = sol[1:]
    V2_ = float(vv @ vv)
    Gm = 1.0 - (gv - 1.0) * V2_
    y = Gm * vdot / Hv                                     # G_- * v_a'
    B = basis_v(*st)
    for i in range(3):
        rows.append([B[k][i] for k in keys]); rhs.append(y[i])
Mx = np.array(rows); yv = np.array(rhs)
coef, res, rank, sv = np.linalg.lstsq(Mx, yv, rcond=None)
pred = Mx @ coef
out = {'v_prime_basis': {k: float(np.round(c, 10)) for k, c in zip(keys, coef)
                         if abs(c) > 1e-8},
       'v_prime_maxres': float(abs(pred - yv).max()),
       'v_prime_rank': int(rank), 'v_prime_nbasis': len(keys)}

# ---------------- Omega' check --------------------------------------------------
err = 0.0
for _ in range(300):
    st = draw(); Hv, gv, rv, N, A, S, Rv, vv = st
    x = flat(*st)
    sol = np.linalg.solve(np.array(fA(*x), float), np.array(fb(*x), float).ravel())
    rdot = sol[0]
    V2_ = float(vv @ vv); Gp = 1 + (gv - 1) * V2_; Gm = 1 - (gv - 1) * V2_
    Gam2 = 1.0 / (1.0 - V2_)
    rho_n = rv * Gam2 * Gp
    Om = rho_n / (3 * Hv ** 2)
    Sig = S / Hv; Aa = A / Hv
    Sig2 = np.trace(Sig @ Sig) / 6.0
    # q from Raychaudhuri with the tilted-fluid source
    p_n = (gv - 1) * rv + gv * rv * Gam2 * V2_ / 3.0
    q = (2 * np.trace((S / Hv) @ (S / Hv)) / 6.0 * 3 / 3) * 0 \
        + 2 * Sig2 + 0.5 * (rho_n + 3 * p_n) / (3 * Hv ** 2)
    Adv = float(Aa @ vv); Sv = float(vv @ (Sig @ vv))
    S_scaled = Sv / V2_ if V2_ > 0 else 0.0
    # d/dtau of Omega
    dGam2 = 2 * Gam2 ** 2 * float(vv @ sol[1:]) / Hv
    dGp = (gv - 1) * 2 * float(vv @ sol[1:]) / Hv
    dOm = (rdot / Hv * Gam2 * Gp + rv * dGam2 * Gp + rv * Gam2 * dGp) / (3 * Hv ** 2) \
        + 2 * (1 + q) * Om
    claim = (Om / Gp) * (2 * q - (3 * gv - 2) + 2 * gv * Adv
                         + (2 * q * (gv - 1) - (2 - gv)) * V2_ - gv * Sv)
    err = max(err, abs(dOm - claim) / max(1.0, abs(dOm)))
out['Omega_prime_published_relerr'] = err

print(json.dumps(out, indent=2))
json.dump(out, open('r5c_tilt_fit.json', 'w'), indent=2)
