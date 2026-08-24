"""Exact counterexample: a direction-dependent rate multiplier changes the left kernel."""
from __future__ import annotations

import json
from pathlib import Path

import sympy as sp

q1, q2 = sp.symbols("q1 q2", positive=True, nonzero=True)
C_hat = sp.Matrix([[-1, 1], [1, -1]])
Q = sp.diag(q1, q2)
C = Q * C_hat
r = sp.Matrix([1, 1])
a_hat = sp.Matrix([[1, 1]])
a = sp.Matrix([[1/q1, 1/q2]])
P_hat = r * a_hat / (a_hat * r)[0]
P = r * a / (a * r)[0]
wrong_left_residual = sp.simplify(a_hat * C)
right_residual = sp.simplify(C * r)
left_residual = sp.simplify(a * C)
projector_difference = sp.simplify(P - P_hat)

assert right_residual == sp.zeros(2, 1)
assert left_residual == sp.zeros(1, 2)
assert wrong_left_residual != sp.zeros(1, 2)
assert sp.simplify(P*P-P) == sp.zeros(2, 2)
assert projector_difference != sp.zeros(2, 2)

result = {
    "C_hat": str(C_hat),
    "Q": str(Q),
    "right_residual": str(right_residual),
    "correct_left": str(a),
    "correct_left_residual": str(left_residual),
    "unchanged_left_residual": str(wrong_left_residual),
    "projector_changes": True,
    "projector_difference": str(projector_difference),
    "conclusion": (
        "A positive diagonal direction-dependent multiplier preserves the right kernel "
        "but changes the paired left kernel and normalized rank-one projector."
    ),
}
Path(__file__).resolve().parents[1].joinpath("audit/exact_rate_multiplier_witness.json").write_text(
    json.dumps(result, indent=2) + "\n"
)
print("EXACT_RATE_MULTIPLIER_WITNESS_PASS")
