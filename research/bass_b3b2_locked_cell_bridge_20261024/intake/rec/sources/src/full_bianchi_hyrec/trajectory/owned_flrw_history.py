"""Single-owner q=0 history with once-only prefix validation.

This is the original retarded two-neighbor interpolation, not a new transport
closure. Arrays copied at construction cannot be changed through the caller's
input arrays. Only validated whole columns may be appended. Read-only views
are for trusted observers, not a security boundary against deliberate access
to NumPy .base. This object is single-threaded and strictly FLRW.
"""
from __future__ import annotations

import math
import numpy as np

from full_bianchi_hyrec.trajectory.causal_virtual_redshift import (
    SOURCE_DLNA, SOURCE_N_VIRTUAL, _source_edges,
)


class OwnedFLRWHistory:
    """Keep prefix ownership instead of rescanning it at every atomic call."""

    def __init__(self, *, energies_eV, z_start: float, dlna: float,
                 virtual, average, lyman, capacity: int):
        if not (math.isfinite(z_start) and z_start >= 0.
                and math.isfinite(dlna) and 0. < dlna <= SOURCE_DLNA):
            raise ValueError("OWNED_HISTORY_CLOCK")
        if isinstance(capacity, bool) or not isinstance(capacity, (int, np.integer)):
            raise ValueError("OWNED_HISTORY_CAPACITY")
        v, a, ly = (np.array(x, dtype=np.float64, copy=True, order="F")
                    for x in (virtual, average, lyman))
        if v.ndim != 2 or v.shape[0] != SOURCE_N_VIRTUAL:
            raise ValueError("OWNED_HISTORY_PREFIX_SHAPE")
        n = v.shape[1]
        if n < 2 or a.shape != v.shape or ly.shape != (3, n) or capacity < n:
            raise ValueError("OWNED_HISTORY_PREFIX_SHAPE")
        if not all(np.all(np.isfinite(x)) for x in (v, a, ly)):
            raise ValueError("OWNED_HISTORY_PREFIX_NONFINITE")
        self._src, targets, sources = _source_edges(np.asarray(energies_eV))
        self._lookback = np.log(sources / targets)
        self._eta0 = -math.log1p(z_start)
        self._z_start = float(z_start)
        self._h = float(dlna)
        self._n = n
        self._capacity = int(capacity)
        self._v = np.full((SOURCE_N_VIRTUAL, capacity), np.nan, order="F")
        self._a = np.full_like(self._v, np.nan)
        self._ly = np.full((3, capacity), np.nan, order="F")
        self._v[:, :n], self._a[:, :n], self._ly[:, :n] = v, a, ly
        self._groups = (
            (np.flatnonzero(self._src < SOURCE_N_VIRTUAL), self._v, 0),
            (np.flatnonzero(self._src >= SOURCE_N_VIRTUAL), self._ly, SOURCE_N_VIRTUAL),
        )

    @property
    def accepted_columns(self) -> int:
        return self._n

    def readonly_views(self):
        """Trusted observational access, without a growing-prefix copy."""
        result = []
        for array in (self._v, self._a, self._ly):
            view = array[:, :self._n].view()
            view.setflags(write=False)
            result.append(view)
        return tuple(result)

    def incoming(self, z_face: float):
        """Return original q=0 virtual/line incoming values as 1-D arrays."""
        if not (math.isfinite(z_face) and self._z_start >= z_face >= 0.):
            raise ValueError("OWNED_HISTORY_FACE_REDSHIFT")
        j = self._n
        eta_face = -math.log1p(z_face)
        expected_eta = self._eta0 + j * self._h
        eps_clock = 16. * np.finfo(np.float64).eps * max(1., abs(expected_eta))
        if abs(eta_face - expected_eta) > eps_clock:
            raise ValueError("OWNED_HISTORY_FACE_CLOCK_MISMATCH")
        eta_emit = eta_face - self._lookback
        active = eta_emit >= self._eta0
        if np.any(eta_emit[active] >= self._eta0 + self._h * (j-1)):
            raise ArithmeticError("OWNED_HISTORY_FUTURE_READ")
        ix = np.maximum((eta_emit - self._eta0) / self._h, 0.)
        ix = np.minimum(ix, np.nextafter(float(j-1), -math.inf))
        k = np.minimum(np.floor(ix).astype(np.intp), j-2)
        w = ix - k
        if np.any(k[active] < 0) or np.any(k[active] + 1 > j-1):
            raise ArithmeticError("OWNED_HISTORY_INDEX")
        incoming = np.empty(SOURCE_N_VIRTUAL + 2, dtype=np.float64)
        for columns, history, offset in self._groups:
            rows = self._src[columns] - offset
            left = ((1. - w[columns]) * history[rows, k[columns]]
                    + w[columns] * history[rows, k[columns] + 1])
            # Preserve the original isotropic angular arithmetic association.
            incoming[columns] = np.where(active[columns], left * 1. + left * 0., 0.)
        if not np.all(np.isfinite(incoming)):
            raise ArithmeticError("OWNED_HISTORY_GATHER_NONFINITE")
        return incoming[:SOURCE_N_VIRTUAL], incoming[SOURCE_N_VIRTUAL:]

    def append(self, *, expected_index: int, virtual, average, lyman) -> None:
        """Validate all candidate fields before committing any of the column."""
        if expected_index != self._n or self._n >= self._capacity:
            raise ValueError("OWNED_HISTORY_APPEND_INDEX_OR_CAPACITY")
        candidates = tuple(np.array(x, dtype=np.float64, copy=True)
                           for x in (virtual, average, lyman))
        for value, shape in zip(candidates, ((SOURCE_N_VIRTUAL,), (SOURCE_N_VIRTUAL,), (3,))):
            if value.shape != shape or not np.all(np.isfinite(value)):
                raise ValueError("OWNED_HISTORY_APPEND_SHAPE_OR_NONFINITE")
        self._v[:, self._n], self._a[:, self._n], self._ly[:, self._n] = candidates
        self._n += 1
