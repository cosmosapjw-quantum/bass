"""Explicit Python-oracle interfaces for the integrated nonperturbative research.

Import is dependency-light. No production backend defaults are changed; numerical
calls require backend='python_oracle'. The underlying kernels retain their
published, bounded validity domains and are not a general Einstein solver.
"""
from __future__ import annotations
from importlib import import_module

_KERNELS = frozenset({
    'polarized_dictionary', 'source_memory', 'volterra_solver',
    'harmonic_streaming', 'direct_oracle', 'harmonic_history',
    'curvature_streaming', 'curvature_oracle', 'frozen_bianchi_ii',
    'expanding_bianchi_ii', 'classb_streaming', 'classb_oracle',
    'frozen_bianchi_v', 'expanding_bianchi_v', 'tilted_collision',
    'covariant_oracle', 'tilted_history', 'km2b_fixtures', 'matrix_oracle',
    'curved_tilt', 'spatial_projection', 'mean_collision',
    'spatial_transport', 'spatial_memory', 'lapse_transport',
    'independent_oracles',
})
__all__ = ['catalog', 'load_kernel', 'normal_time_collision_step']


def _oracle(backend, route):
    from bianchi.backend_policy import BackendPolicy, BackendPolicyError
    if backend != BackendPolicy.PYTHON_ORACLE:
        raise BackendPolicyError(route,
            "This scoped research route requires explicit backend='python_oracle'; "
            "a native implementation is not provided and no fallback is performed.")


def catalog() -> tuple[str, ...]:
    """Names of installed kernels; applicability is in the integration dossier."""
    return tuple(sorted(_KERNELS))


def load_kernel(name: str, *, backend=None):
    """Import a named kernel without mutating sys.path or global module aliases."""
    _oracle(backend, 'nonperturbative.load_kernel')
    if name not in _KERNELS:
        raise KeyError(f'Unknown nonperturbative kernel: {name!r}')
    return import_module(f'{__name__}._core.{name}')


def normal_time_collision_step(n, weights, carrier, *, dt_s, rest_rate_s,
                               beta, panels=32, backend=None):
    """Return a new physical carrier for a fixed-geometry collision-only step.

    dt_s is normal proper seconds. rest_rate_s=n_e* sigma_T c uses the electron
    proper density and excludes Doppler D. This adapter applies D exactly once.
    It never rescales angular weights, clips a state or mutates its input.
    """
    _oracle(backend, 'nonperturbative.normal_time_collision_step')
    from .polq_bridge import collision_step
    return collision_step(n, weights, carrier, dt_s=dt_s,
                          rest_rate_s=rest_rate_s, beta=beta, panels=panels)
