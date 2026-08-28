"""Native-only RF-03 adapter for the explicit gamma-law tilted perfect fluid.

The historical functions in :mod:`bianchi.matter.fluid` remain the explicit
validation oracle.  This production adapter never dispatches to them.
"""
from __future__ import annotations

import numpy as np

from bianchi.backend_policy import BackendPolicy, select_backend


MODEL_ID = "explicit_gamma_law_tilted_perfect_fluid_v1"


class RF03ModelSelectionError(ValueError):
    """Caller omitted or changed the sole authorized production model ID."""


def _require_model_id(model_id):
    if model_id != MODEL_ID or not isinstance(model_id, str):
        raise RF03ModelSelectionError(
            f"model_id must be supplied exactly as {MODEL_ID!r}"
        )


def _native(route_id: str, development_override: bool):
    selected = select_backend(
        route_id,
        policy=BackendPolicy.RUST_REQUIRED,
        development_override=development_override,
    )
    assert selected.native_module is not None
    return selected.native_module


def _vector(value, size: int):
    array = np.ascontiguousarray(value, dtype=np.float64)
    if array.shape != (size,):
        raise ValueError(f"expected shape ({size},), got {array.shape}")
    return array


def _matrix(value):
    array = np.ascontiguousarray(value, dtype=np.float64)
    if array.shape != (3, 3):
        raise ValueError(f"expected shape (3, 3), got {array.shape}")
    return array


def force(
    *,
    model_id,
    gamma,
    state,
    Sigma,
    N,
    A,
    R,
    q,
    T_gamma=None,
    development_override=False,
):
    """Return ``[dOmega,dv1,dv2,dv3]`` from the native production route."""
    _require_model_id(model_id)
    native = _native("matter.gamma_law.force", development_override)
    return np.asarray(
        native.rf03_matter_force(
            model_id,
            gamma,
            _vector(state, 4),
            _matrix(Sigma),
            _matrix(N),
            _vector(A, 3),
            _vector(R, 3),
            q,
            T_gamma,
        ),
        dtype=np.float64,
    )


def force_jvp(
    *,
    model_id,
    gamma,
    state,
    direction,
    Sigma,
    N,
    A,
    R,
    q,
    T_gamma=None,
    development_override=False,
):
    """Return the native force and its analytic state-direction JVP."""
    _require_model_id(model_id)
    native = _native("matter.gamma_law.force_jvp", development_override)
    primal, tangent = native.rf03_matter_force_jvp(
        model_id,
        gamma,
        _vector(state, 4),
        _vector(direction, 4),
        _matrix(Sigma),
        _matrix(N),
        _vector(A, 3),
        _vector(R, 3),
        q,
        T_gamma,
    )
    return np.asarray(primal, dtype=np.float64), np.asarray(tangent, dtype=np.float64)


def integrate(
    *,
    model_id,
    gamma,
    state,
    Sigma,
    N,
    A,
    R,
    q,
    t_end,
    nsteps,
    T_gamma=None,
    development_override=False,
):
    """Run one deterministic fixed-context native RK4 trajectory."""
    _require_model_id(model_id)
    native = _native("matter.gamma_law.integrate", development_override)
    result = native.rf03_matter_integrate(
        model_id,
        gamma,
        _vector(state, 4),
        _matrix(Sigma),
        _matrix(N),
        _vector(A, 3),
        _vector(R, 3),
        q,
        t_end,
        nsteps,
        T_gamma,
    )
    result = dict(result)
    result["times"] = np.asarray(result["times"], dtype=np.float64)
    result["states"] = np.asarray(result["states"], dtype=np.float64)
    return result


def integrate_history(
    *,
    model_id,
    gamma,
    state,
    times,
    Sigma,
    N,
    A,
    R,
    q,
    T_gamma=None,
    development_override=False,
):
    """Integrate against a precomputed native RF-02C context history.

    All context samples cross the boundary once; no Python callback is made
    inside the native RK4 loop.
    """
    _require_model_id(model_id)
    native = _native("matter.gamma_law.integrate_history", development_override)
    times = np.ascontiguousarray(times, dtype=np.float64)
    Sigma = np.ascontiguousarray(Sigma, dtype=np.float64)
    N = np.ascontiguousarray(N, dtype=np.float64)
    A = np.ascontiguousarray(A, dtype=np.float64)
    R = np.ascontiguousarray(R, dtype=np.float64)
    q = np.ascontiguousarray(q, dtype=np.float64)
    if T_gamma is not None:
        T_gamma = np.ascontiguousarray(T_gamma, dtype=np.float64)
    result = native.rf03_matter_integrate_history(
        model_id,
        gamma,
        _vector(state, 4),
        times,
        Sigma,
        N,
        A,
        R,
        q,
        T_gamma,
    )
    result = dict(result)
    result["times"] = np.asarray(result["times"], dtype=np.float64)
    result["states"] = np.asarray(result["states"], dtype=np.float64)
    return result
