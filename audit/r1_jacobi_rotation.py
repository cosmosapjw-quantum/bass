"""
R1 - derive n_ab, a_a evolution (with frame rotation) from the 4d Jacobi identity
     and pin the rotation-vector sign dictionary  R_gen  vs  R_comm.

Frame:  e_0 = n (unit normal, geodesic, vorticity-free),  e_alpha spatial orthonormal,
        allowed to rotate:            [e_0, e_a] = -Theta^b_a e_b ,
        Theta^b_a = H d^b_a + sigma^b_a + Omega^b_a ,   Omega_ab = -Omega_ba ,
        Omega^b_a = eps_{b a g} Rgen^g          <-- "generator" convention
        (equivalently  Omega_ab = +eps_abc Rcomm^c  with  Rgen = -Rcomm)
        [e_a, e_b] = C^c_ab e_c ,  C^c_ab = eps_abd n^{dc} + a_a d^c_b - a_b d^c_a
"""
import sympy as sp
from sympy import Rational as Q
import itertools, json

I3 = range(3)
eps = sp.MutableDenseNDimArray.zeros(3, 3, 3)
for i, j, k in itertools.product(I3, I3, I3):
    eps[i, j, k] = sp.Integer(((i - j) * (j - k) * (k - i)) // 2)
d = sp.eye(3)
t = sp.Symbol('t')

H = sp.Function('H')(t)
n = sp.Matrix(3, 3, lambda i, j: sp.Function(f'n{min(i,j)}{max(i,j)}')(t))
s = sp.Matrix(3, 3, lambda i, j: sp.Function(f's{min(i,j)}{max(i,j)}')(t))  # shear, will impose trace 0
a = sp.Matrix(3, 1, lambda i, j: sp.Function(f'a{i}')(t))
Rg = sp.Matrix(3, 1, lambda i, j: sp.Function(f'R{i}')(t))                  # Rgen

Om = sp.Matrix(3, 3, lambda i, j: sum(eps[i, j, g] * Rg[g] for g in I3))    # Omega^i_j = eps_{i j g} Rgen^g
Th = H * d + s + Om

# structure constants of the full 4d frame:  C[c][a][b],  indices 0..3 (0 = e_0)
C = [[[sp.Integer(0)] * 4 for _ in range(4)] for _ in range(4)]
for al in I3:
    for be in I3:
        C[0][al + 1][be + 1] = sp.Integer(0)                     # hypersurface orthogonal
        for ga in I3:
            C[ga + 1][al + 1][be + 1] = (sum(eps[al, be, dd] * n[dd, ga] for dd in I3)
                                         + a[al] * d[ga, be] - a[be] * d[ga, al])
for al in I3:
    for be in I3:
        C[be + 1][0][al + 1] = -Th[be, al]
        C[be + 1][al + 1][0] = +Th[be, al]

# Jacobi identity, spatial derivatives of homogeneous quantities vanish
def jac(x, y, z):
    """sum over cyclic (x,y,z) of  e_x(C^d_yz) + C^d_xe C^e_yz  -> vector in d"""
    res = []
    for dd in range(4):
        tot = sp.Integer(0)
        for (p, q, r) in ((x, y, z), (y, z, x), (z, x, y)):
            if p == 0:
                tot += sp.diff(C[dd][q][r], t)                   # e_0 = d/dt
            tot += sum(C[dd][p][e] * C[e][q][r] for e in range(4))
        res.append(sp.simplify(tot))
    return res

subs0 = {}                                                        # impose tr sigma = 0
subs0[s[2, 2]] = -s[0, 0] - s[1, 1]

rows = {}
for al, be in ((0, 1), (0, 2), (1, 2), (0, 0), (1, 1), (2, 2)):
    rows[(al, be)] = [sp.expand(x.subs(subs0).doit()) for x in jac(0, al + 1, be + 1)]

# ---- solve for ndot, adot ------------------------------------------------------
unk = [sp.diff(n[i, j], t) for i, j in ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))] \
      + [sp.diff(a[i], t) for i in I3]
eqs = [e for v in rows.values() for e in v]
sol = sp.solve(eqs, unk, dict=True)
assert sol, "Jacobi system not solvable"
sol = sol[0]

ndot = sp.Matrix(3, 3, lambda i, j: sp.expand(sol[sp.diff(n[min(i,j), max(i,j)], t)]))
adot = sp.Matrix(3, 1, lambda i, j: sp.expand(sol[sp.diff(a[i], t)]))

# ---- compare with the closed forms we will publish -----------------------------
# claim:  ndot^{ab} = -H n^{ab} + 2 n^{c(a} sigma^{b)}_c  + 2 eps^{cd(a} n^{b)}_c Rgen_d
#         adot_a    = -H a_a     -   sigma_a^b a_b        +   eps_{abc} a^b Rgen^c
n2 = sp.Matrix(3, 3, lambda i, j: sum(n[i, c] * s[j, c] + n[j, c] * s[i, c] for c in I3) / 2 * 2)
rot_n = sp.Matrix(3, 3, lambda i, j: sum(eps[c, dd, i] * n[j, c] * Rg[dd]
                                         + eps[c, dd, j] * n[i, c] * Rg[dd] for c in I3 for dd in I3))
claim_ndot = sp.expand((-H * n + n2 + rot_n).subs(subs0))
claim_adot = sp.expand((-H * a - (s * a) + sp.Matrix(3, 1, lambda i, j:
                        sum(eps[i, b, c] * a[b] * Rg[c] for b in I3 for c in I3))).subs(subs0))

dn = sp.simplify(ndot - claim_ndot)
da = sp.simplify(adot - claim_adot)

out = {'ndot_matches_claim': dn == sp.zeros(3, 3),
       'adot_matches_claim': da == sp.zeros(3, 1)}
if not out['ndot_matches_claim']:
    out['ndot_residual'] = str(dn)
if not out['adot_matches_claim']:
    out['adot_residual'] = str(da)

# ---- spatial Jacobi identity  =>  n^{ab} a_b = 0 -------------------------------
spatial = []
for al, be, ga in ((0, 1, 2),):
    spatial = [sp.expand(x.subs(subs0)) for x in jac(al + 1, be + 1, ga + 1)]
out['spatial_jacobi'] = [sp.srepr(x)[:0] or str(sp.simplify(x)) for x in spatial]

# ---- does  n^{ab} a_b = 0  propagate along the derived flow? -------------------
Jc = n * a
Jdot = sp.expand(ndot * a + n * adot)
gens = sorted({g for g in ([H] + list(n) + list(a) + list(s) + list(Rg)) if g != s[2, 2]},
              key=lambda z: str(z))
coeffs = sp.symbols('m0 m1 m2')
M = sp.zeros(3, 3); ok = True
for i in I3:
    poly = sp.Poly(sp.expand(Jdot[i] - sum(coeffs[j] * Jc[j] for j in I3)), *gens)
    solc = sp.solve(poly.coeffs(), coeffs, dict=True)
    if solc:
        for j in I3:
            M[i, j] = solc[0].get(coeffs[j], coeffs[j])
    else:
        ok = False
out['jacobi_constraint_propagates_linearly'] = bool(ok)
out['jacobi_propagation_matrix'] = str(M)

# numeric fallback: evaluate Jdot on random states that satisfy n a = 0
import numpy as np
fJ = sp.lambdify(gens, [sp.expand(Jdot[i]) for i in I3], 'numpy')
rng = np.random.default_rng(7)
worst = 0.0
for _ in range(300):
    Nm = rng.normal(size=(3, 3)); Nm = .5 * (Nm + Nm.T)
    w, V = np.linalg.eigh(Nm); k = int(np.argmin(abs(w))); w[k] = 0.0
    Nm = V @ np.diag(w) @ V.T; Av = rng.normal() * V[:, k]
    Sm = rng.normal(size=(3, 3)); Sm = .5 * (Sm + Sm.T); Sm -= np.trace(Sm) * np.eye(3) / 3
    Rv = rng.normal(size=3); Hv = rng.normal()
    vals = {'H(t)': Hv}
    env = {}
    for g in gens:
        nm = str(g)
        if nm.startswith('H'):
            env[g] = Hv
        elif nm.startswith('n'):
            env[g] = Nm[int(nm[1]), int(nm[2])]
        elif nm.startswith('s'):
            env[g] = Sm[int(nm[1]), int(nm[2])]
        elif nm.startswith('a'):
            env[g] = Av[int(nm[1])]
        elif nm.startswith('R'):
            env[g] = Rv[int(nm[1])]
    res = fJ(*[env[g] for g in gens])
    worst = max(worst, float(np.abs(np.array(res, dtype=float)).max()))
out['jacobi_constraint_numeric_Jdot_on_surface'] = worst

print(json.dumps(out, indent=2, default=str))
json.dump(out, open('r1_jacobi_rotation.json', 'w'), indent=2, default=str)

with open('r1_equations.txt', 'w') as f:
    f.write("ndot =\n" + sp.pretty(ndot) + "\n\nadot =\n" + sp.pretty(adot) + "\n")
