"""
R4 - (a) contracted Bianchi identity  nabla^a G_ab = 0  in the rotating ON frame
     (b) explicit constraint-propagation matrix for  C_0 = G_00 - T_00 ,
                                                     C_i = G_0i - T_0i
"""
import sympy as sp, itertools, json
from einstein_frame import einstein, jacobi_subs, eps, eta, I3, I4, t

m = einstein(with_rotation=True)
H, n, a, s, R, G4, Gam = m['H'], m['n'], m['a'], m['s'], m['R'], m['G4'], m['G']
js = jacobi_subs(m)
js2 = {sp.Derivative(k.expr, t, 2): sp.diff(v, t) for k, v in js.items()}


def full_subs(x):
    x = sp.expand(sp.diff(x, t)) if False else x
    for _ in range(3):
        x = sp.expand(x.subs(js2, simultaneous=True).subs(js, simultaneous=True).doit())
    return sp.expand(x)


def div(E):
    """nabla^a E_ab , E symmetric 4x4 in the ON frame; e_alpha(component) = 0."""
    out = []
    for b in I4:
        tot = sp.Integer(0)
        for c in I4:
            inner = (sp.diff(E[c, b], t) if c == 0 else sp.Integer(0))
            inner -= sum(Gam[d][c][c] * E[d, b] for d in I4)      # -Gamma^d_{ac} E_db  (a=c)
            inner -= sum(Gam[d][b][c] * E[c, d] for d in I4)
            tot += eta[c, c] * inner
        out.append(sp.expand(tot))
    return out


# ---------- (a) Bianchi identity ------------------------------------------------
D = [full_subs(x) for x in div(G4)]
bianchi = [sp.simplify(x) for x in D]
out = {'bianchi_identity_components': [str(x) for x in bianchi],
       'bianchi_identity_vanishes': all(x == 0 for x in bianchi)}

# ---------- (b) constraint propagation -----------------------------------------
C0 = sp.Function('C0')(t)
Ci = sp.Matrix(3, 1, lambda i, j: sp.Function(f'C{i+1}')(t))
E = sp.zeros(4, 4)
E[0, 0] = C0
for i in I3:
    E[0, i + 1] = Ci[i]; E[i + 1, 0] = Ci[i]
DE = [sp.expand(x) for x in div(E)]
unk = [sp.Derivative(C0, t)] + [sp.Derivative(Ci[i], t) for i in I3]
sol = sp.solve([sp.Eq(x, 0) for x in DE], unk, dict=True)[0]
rhs = [sp.expand(sol[u]) for u in unk]
Cvec = [C0] + [Ci[i] for i in I3]
M = sp.zeros(4, 4)
lin = True
for r in range(4):
    e = rhs[r]
    for c in range(4):
        M[r, c] = sp.simplify(sp.diff(e, Cvec[c]))
    lin = lin and sp.simplify(e - sum(M[r, c] * Cvec[c] for c in range(4))) == 0
out['constraint_propagation_is_linear_homogeneous'] = bool(lin)
out['propagation_matrix_M'] = sp.pretty(sp.simplify(M))
out['M_depends_on_R'] = any(sp.simplify(sp.diff(M[i, j], R[k])) != 0
                            for i in I4 for j in I4 for k in I3)

print(json.dumps(out, indent=2))
json.dump(out, open('r4_bianchi_constraints.json', 'w'), indent=2)
print(sp.pretty(sp.simplify(M)))
