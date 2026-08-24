"""Adjudicate the D19 E=0-limit mismatch: what rotation term does the ENGINE's
Faraday/Ampere actually produce, in engine-R (generator) and comm-R terms?"""
import sympy as sp, numpy as np, itertools, json
from einstein_frame import einstein, jacobi_subs, eps, eta, I3, I4, t
from core import EPS, stf, sym

m = einstein(with_rotation=True)
H, n, a, s, R, Gam = m['H'], m['n'], m['a'], m['s'], m['R'], m['G']
js = jacobi_subs(m)
Ee = sp.Matrix(3, 1, lambda i, j: sp.Function(f'E{i}')(t))
Bb = sp.Matrix(3, 1, lambda i, j: sp.Function(f'B{i}')(t))
F = sp.zeros(4, 4)
for i in I3:
    F[0, i + 1] = -Ee[i]; F[i + 1, 0] = Ee[i]
for i, j in itertools.product(I3, I3):
    F[i + 1, j + 1] = sum(eps[i, j, k] * Bb[k] for k in I3)
Fup = sp.Matrix(4, 4, lambda i, j: sp.expand(
    sum(eta[i, p] * eta[j, q] * F[p, q] for p in I4 for q in I4)))

def div_up(T):
    o = []
    for b in I4:
        tot = sp.Integer(0)
        for c in I4:
            tot += (sp.diff(T[c, b], t) if c == 0 else 0)
            tot += sum(Gam[c][d][c] * T[d, b] for d in I4)
            tot += sum(Gam[b][d][c] * T[c, d] for d in I4)
        o.append(sp.expand(tot))
    return o

def cov_d(Tl, aa, bb, cc):
    val = sp.diff(Tl[bb, cc], t) if aa == 0 else sp.Integer(0)
    val -= sum(Gam[d][bb][aa] * Tl[d, cc] for d in I4)
    val -= sum(Gam[d][cc][aa] * Tl[bb, d] for d in I4)
    return sp.expand(val)

amp = [x.subs(js, simultaneous=True) for x in div_up(Fup)]
bF = {}
for k3 in itertools.combinations(range(4), 3):
    aa, bb, cc = k3
    bF[k3] = sp.expand(cov_d(F, aa, bb, cc) + cov_d(F, bb, cc, aa)
                       + cov_d(F, cc, aa, bb)).subs(js, simultaneous=True)
Edot = [sp.Derivative(Ee[i], t) for i in I3]
Bdot = [sp.Derivative(Bb[i], t) for i in I3]
sol_E = sp.solve([sp.Eq(x, 0) for x in amp[1:]], Edot, dict=True)[0]
sol_B = sp.solve([sp.Eq(x, 0) for x in [bF[k] for k in bF if 0 in k]],
                 Bdot, dict=True)[0]

# numeric: isolate the R-dependence (n=a=s=0, H=0)
SY = [H] + [n[0,0],n[0,1],n[0,2],n[1,1],n[1,2],n[2,2]] + [a[0],a[1],a[2]] \
     + [s[0,0],s[0,1],s[0,2],s[1,1],s[1,2]] + [R[0],R[1],R[2]] \
     + [Ee[0],Ee[1],Ee[2],Bb[0],Bb[1],Bb[2]]
pl = {x: sp.Symbol('z%d' % i) for i, x in enumerate(SY)}
fB = sp.lambdify(list(pl.values()), [sp.expand(sol_B[d]).subs(pl, simultaneous=True) for d in Bdot], 'numpy')
fE = sp.lambdify(list(pl.values()), [sp.expand(sol_E[d]).subs(pl, simultaneous=True) for d in Edot], 'numpy')
rng = np.random.default_rng(7)
res = {'B_plus': 0., 'B_minus': 0., 'E_plus': 0., 'E_minus': 0.}
for _ in range(50):
    Rv = rng.normal(size=3); Ev = rng.normal(size=3); Bv = rng.normal(size=3)
    args = [0.]*15 + list(Rv) + list(Ev) + list(Bv)
    dB = np.array(fB(*args), float); dE = np.array(fE(*args), float)
    # engine R = R_gen.  Candidates in engine-R components:
    RxB = np.cross(Rv, Bv); RxE = np.cross(Rv, Ev)
    res['B_plus'] = max(res['B_plus'], float(np.abs(dB - RxB).max()))
    res['B_minus'] = max(res['B_minus'], float(np.abs(dB + RxB).max()))
    res['E_plus'] = max(res['E_plus'], float(np.abs(dE - RxE).max()))
    res['E_minus'] = max(res['E_minus'], float(np.abs(dE + RxE).max()))
print(json.dumps(res, indent=1))
json.dump(res, open('adjudicate_d19.json', 'w'), indent=1)
