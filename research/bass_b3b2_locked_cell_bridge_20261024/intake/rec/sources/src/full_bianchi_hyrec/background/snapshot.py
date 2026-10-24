"""Stable chart-independent background interface.

All geometric rates are physical (s^-1), not Hubble-normalized.  The
local atomic/collision kernel consumes this interface and therefore does
not import primitive chart state classes.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace as dataclass_replace
from types import MappingProxyType
from typing import Mapping

import numpy as np


def _array(value, shape, name):
    array = np.asarray(value, dtype=float)
    if array.shape != shape:
        raise ValueError(f"{name} must have shape {shape}")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must be finite")
    return array.copy()


@dataclass(frozen=True)
class BackgroundSnapshot:
    tau: float
    cosmic_time_s: float
    H_s_inv: float
    q: float
    sigma_s_inv: np.ndarray
    N_s_inv: np.ndarray
    A_s_inv: np.ndarray
    frame_rotation_s_inv: np.ndarray
    beta_H: np.ndarray
    D0_beta_H_s_inv: np.ndarray
    chart_id: str
    bianchi_type: str
    normalization: str = "physical"
    branch_flags: Mapping[str, bool] = field(default_factory=dict)
    constraint_residuals: Mapping[str, float] = field(default_factory=dict)
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self):
        for scalar_name in ("tau", "cosmic_time_s", "H_s_inv", "q"):
            value = float(getattr(self, scalar_name))
            if not np.isfinite(value):
                raise ValueError(f"{scalar_name} must be finite")
            object.__setattr__(self, scalar_name, value)
        if self.H_s_inv <= 0.0:
            raise ValueError("H_s_inv must be positive")

        sigma = _array(self.sigma_s_inv, (3, 3), "sigma_s_inv")
        N = _array(self.N_s_inv, (3, 3), "N_s_inv")
        A = _array(self.A_s_inv, (3,), "A_s_inv")
        rotation = _array(
            self.frame_rotation_s_inv,
            (3,),
            "frame_rotation_s_inv",
        )
        beta = _array(self.beta_H, (3,), "beta_H")
        dbeta = _array(
            self.D0_beta_H_s_inv,
            (3,),
            "D0_beta_H_s_inv",
        )

        scale = max(self.H_s_inv, np.max(np.abs(sigma)), 1.0)
        if np.max(np.abs(sigma - sigma.T)) > 2e-12 * scale:
            raise ValueError("sigma_s_inv must be symmetric")
        if abs(np.trace(sigma)) > 2e-12 * scale:
            raise ValueError("sigma_s_inv must be trace-free")
        if np.max(np.abs(N - N.T)) > 2e-12 * max(np.max(np.abs(N)), 1.0):
            raise ValueError("N_s_inv must be symmetric")
        if float(beta @ beta) >= 1.0:
            raise ValueError("|beta_H| must be strictly less than 1")
        if not self.chart_id or not self.bianchi_type:
            raise ValueError("chart_id and bianchi_type must be nonempty")
        if self.normalization != "physical":
            raise ValueError("normalization must be 'physical'")

        for name, array in (
            ("sigma_s_inv", sigma),
            ("N_s_inv", N),
            ("A_s_inv", A),
            ("frame_rotation_s_inv", rotation),
            ("beta_H", beta),
            ("D0_beta_H_s_inv", dbeta),
        ):
            array.setflags(write=False)
            object.__setattr__(self, name, array)

        object.__setattr__(
            self,
            "branch_flags",
            MappingProxyType({str(k): bool(v) for k, v in self.branch_flags.items()}),
        )
        object.__setattr__(
            self,
            "constraint_residuals",
            MappingProxyType(
                {str(k): float(v) for k, v in self.constraint_residuals.items()}
            ),
        )
        provenance = {str(k): str(v) for k, v in self.provenance.items()}
        if any(not key or not value for key, value in provenance.items()):
            raise ValueError("provenance keys and values must be nonempty")
        object.__setattr__(self, "provenance", MappingProxyType(provenance))

    def replace(self, **changes) -> "BackgroundSnapshot":
        return dataclass_replace(self, **changes)
