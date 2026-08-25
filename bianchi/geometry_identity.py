"""Lightweight RF-02A geometry convention identity.

This module intentionally imports no symbolic or numerical optional dependency so the
Rust-first frontend can bind the convention hash in a NumPy-only installation.
"""

from __future__ import annotations

import hashlib
import json


CONVENTION = {
    "version": "rf02a-geometry-convention-v1",
    "metric_signature": "(-,+,+,+)",
    "units": "8*pi*G=c=1",
    "structure_constants": (
        "C^c_ab = eps_abd n^dc + a_a delta^c_b - a_b delta^c_a"
    ),
    "epsilon_orientation": "eps_123=+1",
    "jacobi_constraint": "n^ab a_b=0",
    "rotation": "Omega^b_a=eps_bag R_gen^g; R_comm=-R_gen",
}

CONVENTION_HASH = hashlib.sha256(
    json.dumps(
        CONVENTION, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
).hexdigest()


__all__ = ["CONVENTION", "CONVENTION_HASH"]

