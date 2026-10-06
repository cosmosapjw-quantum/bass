"""Non-differentiable native Q diagnostics, also used by QState defaults.

The existing JAX conventions oracle remains unchanged. This module requires a
real, policy-accepted native extension; it never falls back to Python/JAX.
"""
from __future__ import annotations

import numpy as np

from bianchi.backend_policy import require_native


def codazzi_residual_native(Sigma, N, A, q_flux=None):
    """Return C_a = 3 A_b Sigma_ab + eps_abc N_bd Sigma_cd - q_a.

    Sigma and N must have shape (3, 3); A and optional q_flux shape (3,).
    Inputs must be finite. Symmetry/trace-freedom are physical caller contracts,
    not silently imposed by this diagnostic. This API is not JAX differentiable.
    """
    arrays = []
    for name, value, shape in (
        ("Sigma", Sigma, (3, 3)), ("N", N, (3, 3)), ("A", A, (3,)),
        ("q_flux", np.zeros(3) if q_flux is None else q_flux, (3,)),
    ):
        array = np.asarray(value, dtype=np.float64)
        if array.shape != shape:
            raise ValueError(f"{name} must have shape {shape}, got {array.shape}")
        if not np.isfinite(array).all():
            raise ValueError(f"{name} must contain only finite values")
        arrays.append(np.ascontiguousarray(array).ravel())
    rust = require_native("q.diagnostics.codazzi_residual_native")
    return np.asarray(rust.q_codazzi_residual(*arrays))
