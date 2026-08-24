#!/usr/bin/env python3
"""Exact SymPy witness for the rank-one projector/left/Kato algebra.

This witness is intentionally independent of floating-point carrier details.
It proves the finite-dimensional algebra used by BASS-8B.2B.3 for an exact,
nontrivial two-dimensional family with independently varying right and left
null data.
"""
from __future__ import annotations

import json
import sympy as sp


def zero_matrix_q(value: sp.Matrix) -> bool:
    return all(sp.factor(item) == 0 for item in value)


def main() -> None:
    t, u, td, ud, lam, lamd = sp.symbols(
        "t u td ud lambda lambda_dot", finite=True
    )
    den = 1 + u * t
    r = sp.Matrix([1, t])
    rdot = sp.Matrix([0, td])
    a = sp.Matrix([[1, u]]) / den
    adot = (
        sp.Matrix([[0, ud]]) / den
        - sp.Matrix([[1, u]]) * (ud * t + u * td) / den**2
    )

    P = sp.simplify(r * a)
    Pdot = sp.simplify(rdot * a + r * adot)
    I = sp.eye(2)
    C = sp.simplify(-lam * (I - P))
    Cdot = sp.simplify(-lamd * (I - P) + lam * Pdot)
    K = sp.simplify(Pdot * P - P * Pdot)

    residuals = {
        "normalization": sp.factor((a * r)[0] - 1),
        "normalization_tangent": sp.factor((adot * r + a * rdot)[0]),
        "right_null": sp.simplify(C * r),
        "left_null": sp.simplify(a * C),
        "projector_idempotence": sp.simplify(P * P - P),
        "projector_tangent": sp.simplify(P * Pdot + Pdot * P - Pdot),
        "projector_offdiagonal": sp.simplify(P * Pdot * P),
        "generator_projector_left": sp.simplify(C * P),
        "generator_projector_right": sp.simplify(P * C),
        "differentiated_right_null": sp.simplify(Cdot * r + C * rdot),
        "differentiated_left_null": sp.simplify(adot * C + a * Cdot),
        "kato_commutator": sp.simplify(K * P - P * K - Pdot),
        "kato_pp_block": sp.simplify(P * K * P),
        "kato_qq_block": sp.simplify((I - P) * K * (I - P)),
    }

    scalar_keys = {"normalization", "normalization_tangent"}
    checks = {}
    encoded = {}
    for key, value in residuals.items():
        if key in scalar_keys:
            checks[key] = sp.factor(value) == 0
            encoded[key] = str(sp.factor(value))
        else:
            checks[key] = zero_matrix_q(value)
            encoded[key] = [[str(sp.factor(x)) for x in row] for row in value.tolist()]

    checks["global_scalar_projector_independence"] = not P.has(lam, lamd)
    checks["global_scalar_projector_tangent_independence"] = not Pdot.has(lam, lamd)

    wrong_k = -K
    wrong = sp.simplify(wrong_k * P - P * wrong_k - Pdot)
    wrong_nonzero = not zero_matrix_q(wrong)
    checks["wrong_kato_sign_rejected"] = wrong_nonzero
    encoded["wrong_kato_sign_residual"] = [
        [str(sp.factor(x)) for x in row] for row in wrong.tolist()
    ]

    status = "PASS_EXACT_PROJECTOR_LEFT_KATO_SYMPY" if all(checks.values()) else "FAIL"
    payload = {
        "schema": "bass8b2b3-exact-projector-left-kato-sympy-v1",
        "status": status,
        "checks": checks,
        "residuals": encoded,
        "symbols": ["t", "u", "td", "ud", "lambda", "lambda_dot"],
        "assumption": "1 + u*t != 0 and lambda != 0 for collision-selected rank-one projector",
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    if status != "PASS_EXACT_PROJECTOR_LEFT_KATO_SYMPY":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
