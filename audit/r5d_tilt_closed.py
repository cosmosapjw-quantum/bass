"""
Closed form of the tilt equation, derived from the relativistic Euler equation
and verified against the brute-force 4x4 solve of  nabla^a T_ab = 0.

  u^b nabla_b u^i :   vdot^i + (Gammadot/Gamma) v^i + (H d^i_j + sigma^i_j) v^j
                      + Omega^i_j v^j + P^i = -((g-1)/g)(rhodot/rho) v^i ,
  P^i = ^3Gamma^i_{jk} v^j v^k  (spatial connection contracted twice with v)
"""
import numpy as np, json, sympy as sp
from core import connection3, EPS, stf, sym

# ---- identify P^i = ^3Gamma^i_jk v^j v^k in closed form -----------------------
rng = np.random.default_rng(99)


def P_of(N, A, v):
    G = connection3(N, A)                      # G[c,a,b] = Gamma^c_{ab}
    return np.einsum('ijk,j,k->i', G, v, v)


cands = {
    'A V2': lambda N, A, v: A * float(v @ v),
    '(A.v) v': lambda N, A, v: float(A @ v) * v,
    'eps(v, N v)': lambda N, A, v: np.einsum('ijk,j,k->i', EPS, v, N @ v),
    'N.v': lambda N, A, v: N @ v,
    '(vNv) v': lambda N, A, v: float(v @ (N @ v)) * v,
    'A': lambda N, A, v: A,
    'trN v': lambda N, A, v: np.trace(N) * v,
}
rows, rhs = [], []
for _ in range(300):
    N = sym(rng.normal(size=(3, 3)))
    w, V = np.linalg.eigh(N); k = int(np.argmin(abs(w))); w[k] = 0.0
    N = V @ np.diag(w) @ V.T; A = float(rng.normal()) * V[:, k]
    v = rng.normal(size=3)
    y = P_of(N, A, v); cols = [f(N, A, v) for f in cands.values()]
    for i in range(3):
        rows.append([c[i] for c in cols]); rhs.append(y[i])
coef, *_ = np.linalg.lstsq(np.array(rows), np.array(rhs), rcond=None)
res = float(abs(np.array(rows) @ coef - np.array(rhs)).max())
out = {'P_i_coeffs': {k: float(np.round(c, 12)) for k, c in zip(cands, coef)},
       'P_i_maxres': res}

# ---- full closed form vs brute force ------------------------------------------
import r5c_tilt_fit as bf                       # reuses fA, fb, draw, flat

worst_v, worst_r = 0.0, 0.0
for _ in range(250):
    st = bf.draw(); Hv, gv, rv, N, A, S, Rv, vv = st
    x = bf.flat(*st)
    sol = np.linalg.solve(np.array(bf.fA(*x), float), np.array(bf.fb(*x), float).ravel())
    rdot, vdot = sol[0], sol[1:]

    V2 = float(vv @ vv); Gm2 = 1.0 / (1.0 - V2)
    Gp = 1 + (gv - 1) * V2; Gm = 1 - (gv - 1) * V2
    Om_ = -np.einsum('abc,c->ab', EPS, Rv)          # Omega^i_j = -eps_ijk R^k ... test both
    P = P_of(N, A, vv)
    # energy equation:  Gamma rhodot + gamma rho theta_u = 0  ->  rhodot/rho
    # closed form for vdot:
    #   vdot = -[ (Gammadot/Gamma) + ((g-1)/g)(rhodot/rho) ] v - H v - S.v - Om.v - P
    Gdot_over_G = Gm2 * float(vv @ vdot)
    pred = -(Gdot_over_G + (gv - 1) / gv * rdot / rv) * vv \
           - Hv * vv - (S @ vv) - (Om_ @ vv) - P
    worst_v = max(worst_v, float(np.abs(pred - vdot).max()))
out['euler_closed_form_maxres'] = worst_v

# ---- now eliminate Gammadot and rhodot -> explicit v_a' ------------------------
# energy:  Gamma rhodot + gamma rho theta_u = 0 ,   theta_u = nabla_a u^a
# Instead of theta_u we use the brute-force rhodot to *derive* the scalar T:
#   contract the closed form with v  ->  scalar equation for (v.vdot)
worst_T = 0.0
recs = []
for _ in range(400):
    st = bf.draw(); Hv, gv, rv, N, A, S, Rv, vv = st
    x = bf.flat(*st)
    sol = np.linalg.solve(np.array(bf.fA(*x), float), np.array(bf.fb(*x), float).ravel())
    rdot, vdot = sol[0], sol[1:]
    V2 = float(vv @ vv); Gm = 1 - (gv - 1) * V2
    Sig = S / Hv; Aa = A / Hv; Nn = N / Hv; Rr = Rv / Hv
    Sv = float(vv @ (Sig @ vv)); Adv = float(Aa @ vv)
    Om_ = -np.einsum('abc,c->ab', EPS, Rr)
    P = P_of(Nn, Aa, vv)
    T = (((3 * gv - 4) - 2 * (gv - 1) * Adv) * (1 - V2) + (2 - gv) * Sv) / Gm
    pred = T * vv - (Sig @ vv) - (Om_ @ vv) - P
    recs.append(float(np.abs(pred - vdot / Hv).max()))
out['explicit_v_prime_maxres'] = float(max(recs))

print(json.dumps(out, indent=2))
json.dump(out, open('r5d_tilt_closed.json', 'w'), indent=2)
