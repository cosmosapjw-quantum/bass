"""Identify every Einstein-tensor block by least-squares against a tensor basis."""
import sympy as sp, numpy as np, itertools, json
from einstein_frame import einstein, eps, I3, t
from core import stf, sym, ricci3, S3_explicit, R3_explicit, EPS, ID

m = einstein(with_rotation=True)
H, n, a, s, R, Ein = m['H'], m['n'], m['a'], m['s'], m['R'], m['G4']
sdot = sp.Matrix(3, 3, lambda i, j: sp.diff(s[i, j], t))
Hdot = sp.diff(H, t)

plain = {}
names = []
for x in [H] + [n[0, 0], n[0, 1], n[0, 2], n[1, 1], n[1, 2], n[2, 2]] + \
         [a[0], a[1], a[2]] + [s[0, 0], s[0, 1], s[0, 2], s[1, 1], s[1, 2]] + \
         [R[0], R[1], R[2]]:
    y = sp.Symbol(str(x.func)); plain[x] = y
for x, nm in ((Hdot, 'Hd'), (sdot[0, 0], 'sd00'), (sdot[0, 1], 'sd01'),
              (sdot[0, 2], 'sd02'), (sdot[1, 1], 'sd11'), (sdot[1, 2], 'sd12')):
    plain[x] = sp.Symbol(nm)

SY = [plain[H], plain[Hdot]] + [plain[n[0, 0]], plain[n[0, 1]], plain[n[0, 2]],
      plain[n[1, 1]], plain[n[1, 2]], plain[n[2, 2]]] + [plain[a[i]] for i in I3] + \
     [plain[s[0, 0]], plain[s[0, 1]], plain[s[0, 2]], plain[s[1, 1]], plain[s[1, 2]]] + \
     [plain[sdot[0, 0]], plain[sdot[0, 1]], plain[sdot[0, 2]], plain[sdot[1, 1]],
      plain[sdot[1, 2]]] + [plain[R[i]] for i in I3]
EinP = [[sp.expand(sp.expand(Ein[i, j]).doit()).subs(plain, simultaneous=True)
         for j in range(4)] for i in range(4)]
f = sp.lambdify(SY, EinP, 'numpy')


def pack(Hv, Hdv, N, A, S, Sd, Rv):
    return [Hv, Hdv, N[0, 0], N[0, 1], N[0, 2], N[1, 1], N[1, 2], N[2, 2],
            A[0], A[1], A[2], S[0, 0], S[0, 1], S[0, 2], S[1, 1], S[1, 2],
            Sd[0, 0], Sd[0, 1], Sd[0, 2], Sd[1, 1], Sd[1, 2], Rv[0], Rv[1], Rv[2]]


rng = np.random.default_rng(31337)


def sample():
    N = sym(rng.normal(size=(3, 3)))
    A = rng.normal(size=3)
    S = stf(rng.normal(size=(3, 3)))
    Sd = stf(rng.normal(size=(3, 3)))
    return rng.normal(), rng.normal(), N, A, S, Sd, rng.normal(size=3)


def fit(target, basis, nsamp=250, shape='scalar'):
    rows, rhs = [], []
    for _ in range(nsamp):
        st = sample()
        G = np.array(f(*pack(*st)), dtype=float)
        y = target(G, *st); cols = [b(*st) for b in basis]
        if shape == 'scalar':
            rows.append([float(c) for c in cols]); rhs.append(float(y))
        elif shape == 'vec':
            for i in range(3):
                rows.append([c[i] for c in cols]); rhs.append(y[i])
        else:
            for i in range(3):
                for j in range(i, 3):
                    rows.append([c[i, j] for c in cols]); rhs.append(y[i, j])
    Mx = np.array(rows); yv = np.array(rhs)
    coef, *_ = np.linalg.lstsq(Mx, yv, rcond=None)
    return coef, float(abs(Mx @ coef - yv).max())


out = {}

# ---------------- G_00 -------------------------------------------------------
b00 = [lambda Hv, Hd, N, A, S, Sd, Rv: Hv ** 2,
       lambda Hv, Hd, N, A, S, Sd, Rv: 0.5 * np.sum(S * S),
       lambda Hv, Hd, N, A, S, Sd, Rv: R3_explicit(N, A)]
c, e = fit(lambda G, *st: G[0, 0], b00)
out['G00'] = dict(coeffs=dict(zip(['H^2', 'sigma^2', '^3R'], np.round(c, 12).tolist())), maxres=e)

# ---------------- G_0i -------------------------------------------------------
b0i = [lambda Hv, Hd, N, A, S, Sd, Rv: S @ A,
       lambda Hv, Hd, N, A, S, Sd, Rv: np.einsum('ibc,bd,cd->i', EPS, S, N),
       lambda Hv, Hd, N, A, S, Sd, Rv: np.einsum('ibc,b,c->i', EPS, Rv, A),
       lambda Hv, Hd, N, A, S, Sd, Rv: N @ A]
c, e = fit(lambda G, *st: G[0, 1:], b0i, shape='vec')
out['G0i'] = dict(coeffs=dict(zip(['sigma.a', 'eps_ibc sigma^b_d n^cd', 'eps R a', 'n.a'],
                                  np.round(c, 12).tolist())), maxres=e)

# ---------------- trace of G_ij ---------------------------------------------
btr = [lambda Hv, Hd, N, A, S, Sd, Rv: Hd,
       lambda Hv, Hd, N, A, S, Sd, Rv: Hv ** 2,
       lambda Hv, Hd, N, A, S, Sd, Rv: 0.5 * np.sum(S * S),
       lambda Hv, Hd, N, A, S, Sd, Rv: R3_explicit(N, A)]
c, e = fit(lambda G, *st: np.trace(G[1:, 1:]), btr)
out['tr_Gij'] = dict(coeffs=dict(zip(['Hdot', 'H^2', 'sigma^2', '^3R'],
                                     np.round(c, 12).tolist())), maxres=e)

# ---------------- trace-free G_ij -------------------------------------------
bij = [lambda Hv, Hd, N, A, S, Sd, Rv: Sd,
       lambda Hv, Hd, N, A, S, Sd, Rv: Hv * S,
       lambda Hv, Hd, N, A, S, Sd, Rv: S3_explicit(N, A),
       lambda Hv, Hd, N, A, S, Sd, Rv: stf(np.einsum('cda,c,bd->ab', EPS, Rv, S)),
       lambda Hv, Hd, N, A, S, Sd, Rv: stf(np.outer(A, A)),
       lambda Hv, Hd, N, A, S, Sd, Rv: stf(np.einsum('cda,c,bd->ab', EPS, A, N))]
c, e = fit(lambda G, *st: stf(G[1:, 1:]), bij, shape='mat')
out['Gij_tracefree'] = dict(coeffs=dict(zip(
    ['sigmadot', 'H sigma', '^3S', 'eps_{cd<a}R^c sigma_b>^d', 'A_<aA_b>',
     'eps_{cd<a}A^c N_b>^d'], np.round(c, 12).tolist())), maxres=e)

print(json.dumps(out, indent=2))
json.dump(out, open('fit_einstein.json', 'w'), indent=2)
