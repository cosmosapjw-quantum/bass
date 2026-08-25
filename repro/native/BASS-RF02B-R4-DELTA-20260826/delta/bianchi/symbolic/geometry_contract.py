"""RF-02A geometry authority contract.

This module is deliberately a validation/identity layer.  The numerical
classification and curvature implementation remains in ``bianchi.algebra``
and the already-native ``bianchi.q.group`` route.  It records the convention
and state schema once, rejects unsupported domains explicitly, and never
selects a Python fallback for the native geometry routes.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

import numpy as np

from bianchi import algebra
from bianchi.geometry_identity import CONVENTION, CONVENTION_HASH


class GeometryContractError(ValueError):
    """Actionable failure at the RF-02A geometry boundary."""


STATE_SCHEMA = {
    "version": "rf02a-geometry-state-v1",
    "n_order": ["n11", "n22", "n33", "n12", "n13", "n23"],
    "a_order": ["a1", "a2", "a3"],
    "n_shape": [3, 3],
    "a_shape": [3],
    "n_symmetry": "n_ab=n_ba",
    "frame": "spatial orthonormal frame e_1,e_2,e_3",
    "time_gauge": "e_0=d/dt, spatially homogeneous derivatives vanish",
}

NATIVE_GEOMETRY_ROUTES = (
    "q.group.classify",
    "q.group.jacobi_residual",
    "q.group.structure_constants",
    "q.group.ricci3",
    "q.group.curvature",
    "q.group.kappa",
)


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("ascii")).hexdigest()


STATE_SCHEMA_HASH = _digest(STATE_SCHEMA)


def classify_route(route: str) -> str:
    """Return the only supported RF-02A route state, or fail closed."""

    if route in NATIVE_GEOMETRY_ROUTES:
        return "native_required"
    raise GeometryContractError(f"unsupported route: {route}")


def validate_geometry_state(
    n: Any,
    a: Any,
    *,
    type_name: str | None = None,
    tilted: bool = False,
) -> dict[str, Any]:
    """Validate one canonical ``(n, a)`` geometry state.

    This is intentionally a fail-closed boundary check.  It does not alter
    the algebra or introduce a second classifier; ``algebra.classify`` remains
    the Python oracle and the public compute route remains Rust-required.
    """

    if tilted:
        raise GeometryContractError(
            "RF-02A tilted geometry route is unsupported; use the RF-02B owner"
        )
    n_arr = np.asarray(n, dtype=float)
    a_arr = np.asarray(a, dtype=float)
    if n_arr.shape != (3, 3) or a_arr.shape != (3,):
        raise GeometryContractError(
            f"geometry state shape must be n=(3,3), a=(3,), got {n_arr.shape}, {a_arr.shape}"
        )
    if not (np.isfinite(n_arr).all() and np.isfinite(a_arr).all()):
        raise GeometryContractError("geometry state must be finite")
    if not np.array_equal(n_arr, n_arr.T):
        raise GeometryContractError("n must be symmetric in the RF-02A state schema")
    jacobi = n_arr @ a_arr
    if float(np.max(np.abs(jacobi))) > algebra.TOL:
        raise GeometryContractError(
            f"Jacobi constraint n^ab a_b=0 violated: max residual {float(np.max(np.abs(jacobi))):.6g}"
        )
    classified = algebra.classify(n_arr, a_arr)
    if type_name is not None:
        if type_name not in algebra.CANONICAL:
            raise GeometryContractError(f"unknown Bianchi type: {type_name}")
        if classified.name != type_name:
            raise GeometryContractError(
                f"Bianchi type mismatch: requested {type_name}, classified {classified.name}"
            )
    return {
        "type_name": classified.name,
        "group_class": classified.group_class,
        "kappa": classified.kappa,
        "exceptional": classified.exceptional,
        "convention_hash": CONVENTION_HASH,
        "state_schema_hash": STATE_SCHEMA_HASH,
    }


__all__ = [
    "CONVENTION",
    "CONVENTION_HASH",
    "STATE_SCHEMA",
    "STATE_SCHEMA_HASH",
    "NATIVE_GEOMETRY_ROUTES",
    "GeometryContractError",
    "classify_route",
    "validate_geometry_state",
]
