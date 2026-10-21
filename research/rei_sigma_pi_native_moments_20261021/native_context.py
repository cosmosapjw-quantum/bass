"""Explicit reflected native evaluator composed with ACCEL01's exact-bit cache."""
from __future__ import annotations
import copy
import ctypes
from functools import lru_cache
import math
from pathlib import Path
import struct
import sys

LANE = Path(__file__).resolve().parent
ACCEL = LANE.parent / 'rei_sigma_pi_acceleration_20261021'
if str(ACCEL) not in sys.path:
    sys.path.insert(0, str(ACCEL))
import cached_context as cached
from build_native import DEFAULT_BUILD, inspect_build


def freeze(array):
    return cached._immutable_exact(array)


def fold_model(model):
    """Reject wrong shape/parity before creating independent immutable inputs."""
    import numpy as np
    grid = model.massive
    arrays = ((grid.mu, (32,)), (grid.mu2, (32,)), (grid.p2, (32,)),
              (grid.wmu, (32,)), (model.massive_q2, (96, 1)),
              (model.massive_weight, (96, 32)))
    for array, shape in arrays:
        if (array.dtype != np.dtype('float64') or array.shape != shape or
                not array.flags.c_contiguous or not np.isfinite(array).all()):
            raise ValueError('NATIVE_REQUIRES_FINITE_ORIGINAL_96X32_C_BINARY64_LAYOUT')
    mu, u, p2, wmu = grid.mu, grid.mu2, grid.p2, grid.wmu
    q2, weights = model.massive_q2, model.massive_weight
    if (not math.isfinite(grid.mass) or grid.mass <= 0 or np.any(u < 0) or np.any(u > 1)
            or np.any(q2 < 0) or np.any(weights < 0) or np.any(wmu < 0)):
        raise ValueError('NATIVE_INPUT_DOMAIN')
    if (not np.array_equal(mu, -mu[::-1]) or not np.array_equal(u, u[::-1])
            or not np.array_equal(p2, p2[::-1]) or not np.array_equal(wmu, wmu[::-1])
            or not np.array_equal(weights, weights[:, ::-1])
            or not np.array_equal(u, mu*mu) or not np.array_equal(p2, .5*(3*u-1))):
        raise ValueError('NATIVE_REFLECTION_PARITY_REQUIRED_NO_FALLBACK')
    # Copy all angular data per model; cache source bindings cannot be mutated
    # through a different case's shared grid shell.
    model.massive = copy.copy(grid)
    for name in ('mu', 'mu2', 'p2', 'wmu'):
        setattr(model.massive, name, freeze(getattr(grid, name)))
    model.massive_q2 = freeze(q2)
    model.massive_weight = freeze(weights)
    folded = np.ascontiguousarray(weights[:, :16] + weights[:, ::-1][:, :16])
    return freeze(q2[:, 0].copy()), freeze(u[:16].copy()), freeze(folded)


class NativeLibrary:
    def __init__(self, build_dir=DEFAULT_BUILD):
        self.path, self.receipt_path, self.receipt = inspect_build(build_dir)
        self.library = ctypes.CDLL(str(self.path))
        self.function = self.library.rei_moments_v1
        pointer = ctypes.POINTER(ctypes.c_double)
        self.function.argtypes = [pointer, pointer, pointer, ctypes.c_double,
                                  ctypes.c_double, ctypes.c_double, pointer]
        self.function.restype = ctypes.c_int

    def evaluate(self, folded, mass, x, b):
        pointer = ctypes.POINTER(ctypes.c_double)
        output = (ctypes.c_double * 3)()
        status = self.function(*(a.ctypes.data_as(pointer) for a in folded), mass, x, b, output)
        if status:
            raise FloatingPointError('NATIVE_KERNEL_STATUS_' + str(status))
        return tuple(output)


class _NativeMiss:
    def massive_source_3moments(self, x, b):
        # Called only after the unchanged exact-cache domain and binding checks.
        return self._native_library.evaluate(self._native_folded, self.massive.mass, x, b)


class _NativeGuard:
    def _check_moment_binding(self):
        super()._check_moment_binding()
        if (self._native_folded is not self._native_binding[0]
                or self._native_library is not self._native_binding[1]
                or any(a.flags.writeable for a in self._native_folded)
                or tuple(cached._array_binding(a) for a in self._native_folded) != self._native_binding[2]
                or any(getattr(self.massive, name) is not original for name, original in
                       zip(('mu', 'p2', 'wmu'), self._native_binding[3]))
                or any(a.flags.writeable for a in self._native_binding[3])
                or tuple(cached._array_binding(a) for a in self._native_binding[3]) != self._native_binding[4]):
            raise ValueError('NATIVE_KERNEL_BINDING_CHANGED_CREATE_FRESH_MODEL')


@lru_cache(maxsize=1)
def _model_class():
    owner = cached.split.prior.load_owner()
    # Cache -> native miss -> owner. No inherited owner dynamics are changed.
    return type('NativeCachedEinsteinBoltzmann',
                (_NativeGuard, cached._ExactMomentCache, _NativeMiss, owner.EinsteinBoltzmann), {})


class PreparedContext(cached.split.PreparedContext):
    def __init__(self, cache_size=128, build_dir=DEFAULT_BUILD):
        super().__init__()
        if isinstance(cache_size, bool) or not isinstance(cache_size, int) or not 1 <= cache_size <= 4096:
            raise ValueError('EXACT_CACHE_CAPACITY_1_TO_4096_REQUIRED')
        self.cache_size = cache_size
        self.native_library = NativeLibrary(build_dir)
        self.models_created = 0
        self.last_model = None

    def model(self, params):
        source = super().model(params)
        model = object.__new__(_model_class())
        model.__dict__.update(source.__dict__)
        model._native_folded = fold_model(model)
        model._native_library = self.native_library
        model._bind_moment_cache(self.cache_size)
        model._native_binding = (model._native_folded, model._native_library,
                                 tuple(cached._array_binding(a) for a in model._native_folded),
                                 tuple(getattr(model.massive, name) for name in ('mu', 'p2', 'wmu')),
                                 tuple(cached._array_binding(getattr(model.massive, name)) for name in ('mu', 'p2', 'wmu')))
        self.models_created += 1
        self.last_model = model
        return model
