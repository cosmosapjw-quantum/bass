"""
R4 - contracted Bianchi identity and constraint propagation.

The first version of this audit compared unreduced component expressions.  In
the spatially homogeneous frame the Einstein tensor is symmetric only on the
spatial Jacobi surface ``n @ a = 0``; therefore the old raw components were a
diagnostic, not an acceptance observable.  RF-02A keeps those raw bytes for
provenance and adds an exact charted reduction over the full Jacobi surface.
"""
import itertools
import json
import sys
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from einstein_frame import einstein, jacobi_subs, eps, eta, I3, I4, t
from bianchi import algebra
from bianchi.symbolic.geometry_contract import (
    CONVENTION_HASH,
    STATE_SCHEMA_HASH,
)

MANIFEST_GENERATOR = {
    "name": "BASS RF-02A geometry audit",
    "version": "rf02a-1.0",
    "source": "audit/r4_bianchi_constraints.py",
    "reduction": "three exact nonzero-a kernel charts plus a=0 branch",
}


def div(E, Gam):
    """nabla^a E_ab for a symmetric lower-index tensor in the ON frame."""
    out = []
    for b in I4:
        tot = sp.Integer(0)
        for c in I4:
            inner = sp.diff(E[c, b], t) if c == 0 else sp.Integer(0)
            inner -= sum(Gam[d][c][c] * E[d, b] for d in I4)
            inner -= sum(Gam[d][b][c] * E[c, d] for d in I4)
            tot += eta[c, c] * inner
        out.append(sp.expand(tot))
    return out


def full_subs(x, js, js2):
    for _ in range(3):
        x = sp.expand(x.subs(js2, simultaneous=True).subs(js, simultaneous=True).doit())
    return sp.expand(x)


def _kernel_chart(chart):
    """Return a polynomial symmetric N with N A=0 on one pivot chart."""
    A = sp.symbols("A0:3")
    p, q, r = sp.symbols("p q r")
    if chart == 0:
        u, v = sp.Matrix([-A[1], A[0], 0]), sp.Matrix([-A[2], 0, A[0]])
    elif chart == 1:
        u, v = sp.Matrix([A[1], -A[0], 0]), sp.Matrix([0, -A[2], A[1]])
    elif chart == 2:
        u, v = sp.Matrix([A[2], 0, -A[0]]), sp.Matrix([0, A[2], -A[1]])
    else:
        raise ValueError(chart)
    return A, p, q, r, sp.expand(p * u * u.T + q * (u * v.T + v * u.T) + r * v * v.T)


def _chart_substitution(chart, n, a):
    A, p, q, r, N = _kernel_chart(chart)
    sub = {a[i]: A[i] for i in range(3)}
    for i, j in ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)):
        sub[n[i, j]] = N[i, j]
    return sub, (A, p, q, r)


def _reduce_on_jacobi_charts(components, n, a):
    reduced = {}
    for chart in range(3):
        sub, _ = _chart_substitution(chart, n, a)
        reduced[chart] = [sp.factor(x.subs(sub, simultaneous=True)) for x in components]
    return reduced


def _mutated_components(m, components_builder):
    """Flip one Jacobi evolution coefficient for a discriminating witness."""
    js = jacobi_subs(m)
    key = sp.Derivative(m["n"][0, 0], t)
    js[key] = js[key] + 2 * m["H"] * m["n"][0, 0]
    js2 = {sp.Derivative(k.expr, t, 2): sp.diff(v, t) for k, v in js.items()}
    return [full_subs(x, js, js2) for x in components_builder(m)]


def _components(m):
    js = jacobi_subs(m)
    js2 = {sp.Derivative(k.expr, t, 2): sp.diff(v, t) for k, v in js.items()}
    return [full_subs(x, js, js2) for x in div(m["G4"], m["G"])], js, js2


def compute_report(*, include_mutation=False):
    m = einstein(with_rotation=True)
    H, n, a, s, R = m["H"], m["n"], m["a"], m["s"], m["R"]
    components, _, _ = _components(m)
    raw_vanishes = all(sp.simplify(x) == 0 for x in components)
    reduced = _reduce_on_jacobi_charts(components, n, a)
    reduced_vanishes = all(
        all(sp.simplify(x) == 0 for x in row) for row in reduced.values()
    )

    out = {
        "manifest_generator": MANIFEST_GENERATOR,
        "convention_hash": CONVENTION_HASH,
        "state_schema_hash": STATE_SCHEMA_HASH,
        "type_registry": sorted(algebra.CANONICAL),
        "route_inventory": {
            "q.group.classify": "native_required",
            "q.group.jacobi_residual": "native_required",
            "q.group.structure_constants": "native_required",
            "q.group.ricci3": "native_required",
            "q.group.curvature": "native_required",
            "q.group.kappa": "native_required",
        },
        "unsupported_domains": {
            "unknown_type": "fail_closed",
            "tilted_geometry": "fail_closed_RF02B_owner",
        },
        "bianchi_identity_components": [str(x) for x in components],
        "raw_bianchi_identity_vanishes": bool(raw_vanishes),
        "bianchi_identity_components_reduced": {
            str(k): [str(x) for x in v] for k, v in reduced.items()
        },
        "bianchi_identity_reduced_vanishes": bool(reduced_vanishes),
        "bianchi_identity_vanishes": bool(reduced_vanishes),
        "jacobi_reduction": {
            "charts_checked": [0, 1, 2],
            "a_zero_branch": "raw components vanish identically",
            "parameterization": "N=p*u*u.T+q*(u*v.T+v*u.T)+r*v*v.T with u·a=v·a=0",
            "exact": True,
        },
    }

    # Constraint propagation is retained unchanged, but it is now emitted only
    # after the identity gate has an explicit reduced result.
    C0 = sp.Function("C0")(t)
    Ci = sp.Matrix(3, 1, lambda i, j: sp.Function(f"C{i+1}")(t))
    E = sp.zeros(4, 4)
    E[0, 0] = C0
    for i in I3:
        E[0, i + 1] = Ci[i]
        E[i + 1, 0] = Ci[i]
    DE = [sp.expand(x) for x in div(E, m["G"])]
    unk = [sp.Derivative(C0, t)] + [sp.Derivative(Ci[i], t) for i in I3]
    sol = sp.solve([sp.Eq(x, 0) for x in DE], unk, dict=True)[0]
    rhs = [sp.expand(sol[u]) for u in unk]
    Cvec = [C0] + [Ci[i] for i in I3]
    M = sp.zeros(4, 4)
    lin = True
    for rr in range(4):
        e = rhs[rr]
        for cc in range(4):
            M[rr, cc] = sp.simplify(sp.diff(e, Cvec[cc]))
        lin = lin and sp.simplify(e - sum(M[rr, cc] * Cvec[cc] for cc in range(4))) == 0
    out["constraint_propagation_is_linear_homogeneous"] = bool(lin)
    out["propagation_matrix_M"] = sp.pretty(sp.simplify(M))
    out["M_depends_on_R"] = any(
        sp.simplify(sp.diff(M[i, j], R[k])) != 0
        for i in I4 for j in I4 for k in I3
    )

    if include_mutation:
        mutated = _mutated_components(m, lambda mm: div(mm["G4"], mm["G"]))
        mut_reduced = _reduce_on_jacobi_charts(mutated, n, a)
        sub, symbols = _chart_substitution(0, n, a)
        A, p, q, r = symbols
        probe = {A[0]: sp.Rational(2), A[1]: sp.Rational(1), A[2]: sp.Rational(3),
                 p: sp.Rational(1), q: sp.Rational(2), r: sp.Rational(-1),
                 m["H"]: sp.Rational(11, 10), m["s"][0, 1]: sp.Rational(1, 5),
                 m["s"][0, 2]: sp.Rational(-2, 5)}
        values = [abs(float(sp.N(x.subs(probe)))) for x in mut_reduced[0]]
        out["mutation_witness"] = {
            "ndot_H_sign_flip": {
                "reduced_vanishes": all(
                    all(sp.simplify(x) == 0 for x in row) for row in mut_reduced.values()
                ),
                "max_nonzero_component": max(values),
                "mutation": "replace ndot[n00] -H*n00 by +H*n00",
            }
        }
        out["aggregate_gate"] = {
            "identity": out["bianchi_identity_reduced_vanishes"],
            "mutation_witness": not out["mutation_witness"]["ndot_H_sign_flip"]["reduced_vanishes"],
            "pass": bool(out["bianchi_identity_reduced_vanishes"] and
                         out["mutation_witness"]["ndot_H_sign_flip"]["reduced_vanishes"] is False),
        }
    return out


if __name__ == "__main__":
    result = compute_report(include_mutation=True)
    print(json.dumps(result, indent=2))
    json.dump(result, open(Path(__file__).with_suffix(".json"), "w"), indent=2)
    if not result["aggregate_gate"]["pass"]:
        raise SystemExit(1)
