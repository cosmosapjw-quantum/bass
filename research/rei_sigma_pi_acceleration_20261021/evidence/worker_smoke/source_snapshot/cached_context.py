"""Exact per-model reuse of the pinned C15 finite-mass moment evaluator.

The owner function, its reduction order and all evolution methods are inherited
unchanged. Only a repeated binary64 (x, b) request within one immutable kernel
binding reuses its original three Python floats. This is not an interpolation.
"""
from __future__ import annotations

from collections import OrderedDict
import copy
from functools import lru_cache
import math
from pathlib import Path
import struct
import sys

BASELINE = Path(__file__).resolve().parents[1] / 'rei_sigma_pi_pilot_20261021'
sys.path.insert(0, str(BASELINE))
import split_sweep as split


def _immutable_exact(array):
    """Keep C-order binary64 values in a truly immutable bytes-backed view."""
    import numpy as np
    if array.dtype != np.dtype('float64') or not array.flags.c_contiguous:
        raise ValueError('EXACT_CACHE_REQUIRES_ORIGINAL_C_BINARY64_LAYOUT')
    return np.frombuffer(array.tobytes(order='C'), dtype=array.dtype).reshape(array.shape)


def _array_binding(array):
    # Read-only data still permits NumPy dtype/shape/stride metadata assignment.
    return (array.dtype.str, array.shape, array.strides,
            bool(array.flags.c_contiguous))


class _ExactMomentCache:
    def _bind_moment_cache(self, maxsize):
        if isinstance(maxsize, bool) or not isinstance(maxsize, int) or not 1 <= maxsize <= 4096:
            raise ValueError('EXACT_CACHE_CAPACITY_1_TO_4096_REQUIRED')
        if self.fast_massive is not True:
            raise ValueError('EXACT_CACHE_REQUIRES_PINNED_FAST_MASSIVE_PATH')
        # Per-case shell prevents another case changing this grid object's fields.
        # Immutable backing also prevents setflags(write=True) on cache inputs.
        self.massive = copy.copy(self.massive)
        self.massive.mu2 = _immutable_exact(self.massive.mu2)
        self.massive_q2 = _immutable_exact(self.massive_q2)
        self.massive_weight = _immutable_exact(self.massive_weight)
        self._moment_binding = (
            self.massive, self.massive.mu2, self.massive_q2, self.massive_weight,
            struct.pack('>d', self.massive.mass), self.params,
            tuple(_array_binding(a) for a in
                  (self.massive.mu2, self.massive_q2, self.massive_weight)),
        )
        self._moment_cache = OrderedDict()
        self._moment_capacity = maxsize
        self._moment_hits = self._moment_misses = self._moment_evictions = 0

    def _check_moment_binding(self):
        grid, mu2, q2, weights, mass_bits, params, layouts = self._moment_binding
        if (self.massive is not grid or self.massive.mu2 is not mu2
                or self.massive_q2 is not q2 or self.massive_weight is not weights
                or struct.pack('>d', self.massive.mass) != mass_bits
                or self.params is not params or self.fast_massive is not True
                or any(a.flags.writeable for a in (mu2, q2, weights))
                or tuple(_array_binding(a) for a in (mu2, q2, weights)) != layouts):
            raise ValueError('EXACT_CACHE_KERNEL_BINDING_CHANGED_CREATE_FRESH_MODEL')

    def massive_source_3moments(self, x, b):
        self._check_moment_binding()
        # Match the owner's domain before a lookup, including nonfinite rejection.
        if not (math.isfinite(x) and 0 <= x <= 4 and math.isfinite(b) and abs(b) <= 1):
            raise ValueError('BASS_MASSIVE_SOURCE_DOMAIN')
        key = struct.pack('>dd', x, b)  # signed zero and adjacent floats remain distinct
        if key in self._moment_cache:
            value = self._moment_cache.pop(key)
            self._moment_cache[key] = value
            self._moment_hits += 1
            return value
        # This dispatch executes the original pinned owner body, unchanged.
        value = super().massive_source_3moments(x, b)
        if len(value) != 3 or not all(math.isfinite(v) for v in value):
            raise FloatingPointError('EXACT_CACHE_NONFINITE_OWNER_RESULT')
        self._moment_misses += 1
        self._moment_cache[key] = value
        if len(self._moment_cache) > self._moment_capacity:
            self._moment_cache.popitem(last=False)
            self._moment_evictions += 1
        return value

    def moment_cache_info(self):
        return dict(hits=self._moment_hits, misses=self._moment_misses,
                    evictions=self._moment_evictions, entries=len(self._moment_cache),
                    capacity=self._moment_capacity,
                    key='exact IEEE754 binary64 x,b bits; fixed per-model kernel binding')


@lru_cache(maxsize=1)
def _model_class():
    owner = split.prior.load_owner()  # validates immutable source before import
    return type('ExactCachedEinsteinBoltzmann', (_ExactMomentCache, owner.EinsteinBoltzmann), {})


class PreparedContext(split.PreparedContext):
    """One immutable preparation per batch; fresh state/cache for every case."""
    def __init__(self, cache_size=128):
        super().__init__()
        if isinstance(cache_size, bool) or not isinstance(cache_size, int) or not 1 <= cache_size <= 4096:
            raise ValueError('EXACT_CACHE_CAPACITY_1_TO_4096_REQUIRED')
        self.cache_size = cache_size
        self.models_created = 0
        self.last_model = None

    def model(self, params):
        source_model = super().model(params)
        model = object.__new__(_model_class())
        model.__dict__.update(source_model.__dict__)
        model._bind_moment_cache(self.cache_size)
        self.models_created += 1
        self.last_model = model
        return model
