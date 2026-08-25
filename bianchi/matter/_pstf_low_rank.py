"""Dependency-light canonical low-rank PSTF bases used by native wrappers."""
from __future__ import annotations

import numpy as np


_U1 = np.array(
    [
        [0.0, 0.0, 1.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ],
    dtype=float,
)
_U2 = np.array(
    [
        [0.0, 0.0, -0.408248290463863, 0.0, 0.7071067811865476],
        [0.7071067811865476, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.7071067811865476, 0.0],
        [0.7071067811865476, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, -0.408248290463863, 0.0, -0.7071067811865476],
        [0.0, 0.7071067811865476, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.7071067811865476, 0.0],
        [0.0, 0.7071067811865476, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.816496580927726, 0.0, 0.0],
    ],
    dtype=float,
)
_U1.setflags(write=False)
_U2.setflags(write=False)


def u_basis(rank: int) -> np.ndarray:
    """Return the existing canonical rank-1 or rank-2 basis bytes."""

    if rank == 1:
        return _U1
    if rank == 2:
        return _U2
    raise ValueError("dependency-light PSTF basis supports rank 1 or 2")


def to_coefficients(values, rank: int) -> np.ndarray:
    """Project rank-1/2 Cartesian values onto the existing canonical basis."""

    return u_basis(rank).T @ np.asarray(values, dtype=float).ravel()


def vec_to_c3(values) -> np.ndarray:
    """Convert a Cartesian vector to the canonical rank-1 coefficients."""

    return to_coefficients(values, 1)


def sigma_to_c5(values) -> np.ndarray:
    """Convert a symmetric trace-free matrix to canonical rank-2 coefficients."""

    return to_coefficients(values, 2)
