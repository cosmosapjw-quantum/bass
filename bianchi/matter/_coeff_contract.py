"""Dependency-light interface shared by Python coefficient builders and Rust."""
from __future__ import annotations

import numpy as np


class ClosedGeoBlocksContract:
    """Marker base for verified closed geometry blocks passed to Rust."""


def omega_vector(matrix) -> np.ndarray:
    """Return w for the existing antisymmetric convention W = +epsilon.w."""

    W = np.asarray(matrix, dtype=float)
    return -0.5 * np.array(
        [W[2, 1] - W[1, 2], W[0, 2] - W[2, 0], W[1, 0] - W[0, 1]]
    )
