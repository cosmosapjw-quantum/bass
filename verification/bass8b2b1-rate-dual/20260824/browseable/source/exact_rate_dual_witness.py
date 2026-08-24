"""Exact symbolic witness for BASS-8B.2B.1 rate/dual binding.

This script is an audit artifact.  It proves four bounded algebraic claims:

1. a direction-dependent positive multiplier preserves the right kernel but
   transforms the left kernel;
2. a global nonzero scalar multiplier cancels from the normalized rank-one
   projector;
3. the paired inverse-aberration Doppler derivative is consistent in both the
   moving-normal-node and fixed-rest-node descriptions;
4. the Hubble-time rate logarithmic derivative has the declared split.
"""
from __future__ import annotations

import json
from pathlib import Path

import sympy as sp


def exact_witness() -> dict[str, object]:
    q1, q2, lam = sp.symbols("q1 q2 lam", nonzero=True)
    C0 = sp.Matrix([[-1, 1], [1, -1]])
    Mq = sp.diag(q1, q2)
    Cq = Mq * C0
    Cfull = lam * Cq
    r = sp.Matrix([1, 1])
    a0 = sp.Matrix([1, 1])
    aq = sp.Matrix([1 / q1, 1 / q2])

    Pq = sp.simplify(r * aq.T / (aq.dot(r)))
    Pscaled = sp.simplify(r * (aq / lam).T / ((aq / lam).dot(r)))
    Pwrong = sp.simplify(r * a0.T / (a0.dot(r)))

    b2, bdb, s, ds = sp.symbols("b2 bdb s ds")
    gamma = 1 / sp.sqrt(1 - b2)
    gamma_dot = gamma**3 * bdb
    q = (1 - b2) / (1 + s)
    q_dot = sp.diff(q, b2) * (2 * bdb) + sp.diff(q, s) * ds
    D = sp.simplify(gamma * q)
    D_rest = sp.sqrt(1 - b2) / (1 + s)
    D_dot_from_moving = sp.simplify(gamma_dot * q + gamma * q_dot)
    D_dot_from_rest = sp.simplify(
        sp.diff(D_rest, b2) * (2 * bdb) + sp.diff(D_rest, s) * ds
    )

    n, nd, H, Hd, k = sp.symbols("n nd H Hd k", nonzero=True)
    alpha = n * k / H
    alpha_dot = sp.simplify(alpha * (nd / n - Hd / H))
    nu = sp.simplify(alpha * D)
    nu_dot = sp.simplify(alpha_dot * D + alpha * D_dot_from_rest)
    rate_log_residual = sp.simplify(
        nu_dot / nu - (nd / n - Hd / H + D_dot_from_rest / D)
    )

    unchanged_left_residual = sp.simplify((a0.T * Cq))
    transformed_left_residual = sp.simplify((aq.T * Cq))
    transformed_full_left_residual = sp.simplify(((aq / lam).T * Cfull))

    results = {
        "right_kernel_residual": [sp.sstr(x) for x in Cq * r],
        "transformed_left_residual": [sp.sstr(x) for x in transformed_left_residual],
        "transformed_full_left_residual": [
            sp.sstr(x) for x in transformed_full_left_residual
        ],
        "unchanged_left_residual": [sp.sstr(x) for x in unchanged_left_residual],
        "projector_idempotence_residual": [
            [sp.sstr(sp.simplify(x)) for x in row]
            for row in (Pq * Pq - Pq).tolist()
        ],
        "global_scalar_projector_residual": [
            [sp.sstr(sp.simplify(x)) for x in row]
            for row in (Pscaled - Pq).tolist()
        ],
        "direction_dependent_projector_difference": [
            [sp.sstr(sp.factor(x)) for x in row]
            for row in (Pq - Pwrong).tolist()
        ],
        "paired_doppler_identity_residual": sp.sstr(sp.simplify(D - D_rest)),
        "paired_doppler_derivative_residual": sp.sstr(
            sp.simplify(D_dot_from_moving - D_dot_from_rest)
        ),
        "rate_log_derivative_residual": sp.sstr(rate_log_residual),
        "status": "PASS_EXACT_RATE_DUAL_WITNESS",
    }

    assert Cq * r == sp.zeros(2, 1)
    assert transformed_left_residual == sp.zeros(1, 2)
    assert transformed_full_left_residual == sp.zeros(1, 2)
    assert unchanged_left_residual != sp.zeros(1, 2)
    assert sp.simplify(Pq * Pq - Pq) == sp.zeros(2)
    assert sp.simplify(Pscaled - Pq) == sp.zeros(2)
    assert sp.simplify(Pq - Pwrong) != sp.zeros(2)
    assert sp.simplify(D - D_rest) == 0
    assert sp.simplify(D_dot_from_moving - D_dot_from_rest) == 0
    assert rate_log_residual == 0
    return results


def main() -> None:
    results = exact_witness()
    out = Path(__file__).resolve().parents[1] / "audit" / "exact_rate_dual_witness.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
