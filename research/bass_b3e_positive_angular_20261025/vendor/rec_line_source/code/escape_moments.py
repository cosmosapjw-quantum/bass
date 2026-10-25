"""ANGULAR01 local escape moments; no cosmological evolution is performed.

The exact vendored PR114 donor supplies tau_directional and spike attenuation.
The definition beta=A/tau adds a uniform-source optical-depth average. It does
not turn the spike map into a complete emissivity or recombination model.
Q is an escape-probability PSTF moment, not a material/radiation stress.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
import importlib.util
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


AUTO_EPSILON = 1.0e-8
AUTO_THRESHOLD = math.log1p(1.0 / AUTO_EPSILON)
ROUND_BAND_FACTOR = 64.0
DONOR_SHA256 = "3d03c35299d529ecaac66f40f5fc78f14ec3099c057005762f112250ee19add9"
DONOR_PATH = Path(__file__).resolve().parents[1] / "vendor" / "hyrec_spike_transfer.py"
ASSUMPTIONS = (
    "local orthonormal frame; non-tilted homogeneous expanding flow; H>0",
    "symmetric traceless S=sigma/H; q(n)=1+n.S.n strictly positive",
    "fixed direction-independent optical-depth coefficient and isotropic source",
    "beta=A/tau additionally assumes a uniform-source optical-depth average",
    "Q is an escape moment, not material or radiation stress",
)
COUNTERS: Counter[str] = Counter()

_donor_spec = importlib.util.spec_from_file_location("angular01_pinned_hyrec_donor", DONOR_PATH)
if _donor_spec is None or _donor_spec.loader is None:
    raise ImportError(f"Cannot load pinned donor: {DONOR_PATH}")
_donor = importlib.util.module_from_spec(_donor_spec)
sys.modules[_donor_spec.name] = _donor
_donor_spec.loader.exec_module(_donor)
OriginalHyRecSpikeTransfer = _donor.OriginalHyRecSpikeTransfer


@dataclass(frozen=True)
class TensorInput:
    t: float
    tensor: np.ndarray
    eigenvalues: np.ndarray
    eigenvectors: np.ndarray
    qmin: float
    qmax: float
    tolerance: float
    correction_norm: float


@dataclass(frozen=True)
class MomentResult:
    mean: float
    pstf: np.ndarray
    method: str
    qmin: float
    qmax: float
    n_mu: int
    n_phi: int
    nodes: int
    correction_norm: float
    analytic_bounds: dict[str, Any]
    assumptions: tuple[str, ...] = ASSUMPTIONS


def _positive_scalar(value: Any, label: str) -> float:
    if np.ndim(value) != 0 or np.iscomplexobj(value):
        raise ValueError(f"{label} must be a real scalar")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{label} must be a finite positive scalar") from exc
    if not math.isfinite(result) or result <= 0.0:
        raise ValueError(f"{label} must be finite and positive")
    return result


def validate_inputs(t: float, S: np.ndarray) -> TensorInput:
    """Validate the frozen domain and report any roundoff-band projection."""
    depth = _positive_scalar(t, "t")
    if np.iscomplexobj(S):
        raise ValueError("S must be real")
    try:
        raw = np.asarray(S, dtype=float)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("S must be a finite real 3x3 tensor") from exc
    if raw.shape != (3, 3) or not np.all(np.isfinite(raw)):
        raise ValueError("S must be a finite real 3x3 tensor")
    scale = float(np.linalg.norm(raw, ord="fro"))
    if not math.isfinite(scale):
        raise ValueError("S has an unrepresentable tensor scale")
    tolerance = ROUND_BAND_FACTOR * np.finfo(float).eps * max(1.0, scale)
    if float(np.linalg.norm(raw - raw.T, ord="fro")) > tolerance:
        raise ValueError("S is not symmetric within the frozen roundoff band")
    if abs(float(np.trace(raw))) > tolerance:
        raise ValueError("S is not tracefree within the frozen roundoff band")
    tensor = 0.5 * (raw + raw.T)
    tensor = tensor - np.trace(tensor) * np.eye(3) / 3.0
    correction = float(np.linalg.norm(tensor - raw, ord="fro"))
    eigenvalues, eigenvectors = np.linalg.eigh(tensor)
    qmin = 1.0 + float(eigenvalues[0])
    qmax = 1.0 + float(eigenvalues[-1])
    if qmin <= tolerance:
        raise ValueError("qmin is nonpositive or within the frozen zero-speed band")
    COUNTERS["tensor_validations"] += 1
    return TensorInput(depth, tensor, eigenvalues, eigenvectors, qmin, qmax, tolerance, correction)


def beta_vector(t: float, q: Any) -> np.ndarray | float:
    """Stable algebraic vector implementation of donor attenuation divided by tau."""
    depth = _positive_scalar(t, "t")
    if np.iscomplexobj(q):
        raise ValueError("q must be real")
    rates = np.asarray(q, dtype=float)
    if not np.all(np.isfinite(rates)) or np.any(rates <= 0.0):
        raise ValueError("q must be finite and positive")
    with np.errstate(over="ignore", under="ignore", divide="ignore", invalid="ignore"):
        tau = depth / rates
        value = -np.expm1(-tau) / tau
        # These are rounded limiting representations, not a change in the t>0 domain.
        value = np.where(tau == 0.0, 1.0, value)
        value = np.where(np.isposinf(tau), rates / depth, value)
    return float(value) if value.ndim == 0 else value


def donor_beta_reference(t: float, q: float) -> float:
    """Actually invoke the unchanged scalar donor, only for new reference cases."""
    depth, rate = _positive_scalar(t, "t"), _positive_scalar(q, "q")
    donor = OriginalHyRecSpikeTransfer(tau_flrw=depth, f_equilibrium=1.0, H_s_inv=1.0)
    transfer = donor.transfer(f_in=0.0, minus_dlognu_dt_s_inv=rate)
    if not (math.isfinite(transfer.tau_directional) and transfer.tau_directional > 0.0):
        raise ValueError("Donor scalar reference requires representable positive tau")
    COUNTERS["donor_scalar_calls"] += 1
    return transfer.absorbed_fraction / transfer.tau_directional


def _representable_exponential(log_value: float) -> tuple[float | None, str]:
    if log_value > math.log(sys.float_info.max):
        return None, "OVERFLOW_USE_LOG"
    value = math.exp(log_value)
    if value == 0.0:
        return None, "UNDERFLOW_USE_LOG"
    return value, "FLOAT_APPROXIMATION"


def thick_bounds(t: float, qmax: float) -> dict[str, Any]:
    """Analytic truncation bounds; floating evaluation is not interval arithmetic."""
    depth, upper = _positive_scalar(t, "t"), _positive_scalar(qmax, "qmax")
    u = depth / upper
    log_abs_b = -u - math.log(depth)
    log_abs_q = log_abs_b + 0.5 * math.log(2.0 / 3.0)
    denominator = -math.expm1(-u)
    log_relative_b = -u - math.log(denominator) if denominator > 0.0 else math.inf
    log_relative_q = log_relative_b + 0.5 * math.log(2.0 / 3.0)
    result: dict[str, Any] = {
        "kind": "ANALYTIC_TRUNCATION_BOUND",
        "floating_evaluation": "NOT_INTERVAL_ARITHMETIC",
        "log_r": -u,
        "auto_epsilon": AUTO_EPSILON,
        "auto_threshold": AUTO_THRESHOLD,
        "auto_eligible": u >= AUTO_THRESHOLD,
    }
    for name, logarithm in (("absolute_B", log_abs_b), ("absolute_Q_F", log_abs_q),
                             ("relative_B", log_relative_b), ("relative_Q_F_over_B", log_relative_q)):
        value, representation = _representable_exponential(logarithm)
        result[name] = value
        result["log_" + name] = logarithm
        result[name + "_representation"] = representation
    return result


def jensen_gap_bound(data: TensorInput) -> dict[str, Any]:
    qstar = min(data.qmax, max(data.qmin, data.t / 3.0))
    log_m = math.log(data.t) - data.t / qstar - 3.0 * math.log(qstar)
    shear_scale = float(np.max(np.abs(data.tensor)))
    if shear_scale == 0.0:
        return {"bound": 0.0, "log_bound": None, "representation": "EXACT_ZERO_SHEAR",
                "qstar": qstar, "log_M": log_m}
    log_tr_s2 = 2.0 * math.log(shear_scale) + math.log(float(np.sum((data.tensor / shear_scale) ** 2)))
    log_bound = log_m + log_tr_s2 - math.log(15.0)
    bound, representation = _representable_exponential(log_bound)
    return {"bound": bound, "log_bound": log_bound, "representation": representation,
            "qstar": qstar, "log_M": log_m}


def _order(value: int, name: str) -> int:
    if isinstance(value, bool) or int(value) != value or int(value) < 2:
        raise ValueError(f"{name} must be an integer >=2")
    return int(value)


@lru_cache(maxsize=8)
def _unit_interval_gauss(n: int) -> tuple[np.ndarray, np.ndarray]:
    x, w = np.polynomial.legendre.leggauss(_order(n, "order"))
    return 0.5 * (x + 1.0), 0.5 * w


@lru_cache(maxsize=8)
def _principal_rule(n_mu: int, n_phi: int) -> tuple[np.ndarray, np.ndarray]:
    mu, w_mu = _unit_interval_gauss(n_mu)
    phi_unit, w_phi = _unit_interval_gauss(n_phi)
    phi = 0.5 * math.pi * phi_unit
    transverse = 1.0 - mu[:, None] ** 2
    n2 = np.stack((transverse * np.cos(phi)[None, :] ** 2,
                   transverse * np.sin(phi)[None, :] ** 2,
                   np.broadcast_to(mu[:, None] ** 2, (n_mu, n_phi))), axis=-1)
    # Eight reflection-related octants reduce the normalized 4pi average to this rule.
    return n2.reshape(-1, 3), np.outer(w_mu, w_phi).ravel()


def _result(data: TensorInput, mean: float, pstf: np.ndarray, method: str,
            n_mu: int, n_phi: int, nodes: int) -> MomentResult:
    return MomentResult(float(mean), np.asarray(pstf), method, data.qmin, data.qmax,
                        n_mu, n_phi, nodes, data.correction_norm,
                        thick_bounds(data.t, data.qmax))


def _thick(data: TensorInput) -> MomentResult:
    if data.t / data.qmax < AUTO_THRESHOLD:
        raise ValueError("Thick result does not satisfy the frozen analytic error gate")
    COUNTERS["analytic_thick_calls"] += 1
    return _result(data, 1.0 / data.t, (2.0 / 15.0) * data.tensor / data.t,
                   "analytic_thick", 0, 0, 0)


def thick_moments(t: float, S: np.ndarray) -> MomentResult:
    """Approximation only inside the frozen analytic error gate, with bounds."""
    return _thick(validate_inputs(t, S))


def angular_moments(t: float, S: np.ndarray, *, n_mu: int = 64, n_phi: int = 128,
                    mode: str = "auto") -> MomentResult:
    data = validate_inputs(t, S)
    if mode not in ("auto", "quadrature", "thick"):
        raise ValueError("mode must be auto, quadrature or thick")
    if mode == "thick" or (mode == "auto" and data.t / data.qmax >= AUTO_THRESHOLD):
        return _thick(data)
    n_mu, n_phi = _order(n_mu, "n_mu"), _order(n_phi, "n_phi")
    n2, weights = _principal_rule(n_mu, n_phi)
    q = 1.0 + n2 @ data.eigenvalues
    weighted_beta = weights * beta_vector(data.t, q)
    mean = float(np.sum(weighted_beta))
    principal_q = weighted_beta @ n2 - mean / 3.0
    tensor = (data.eigenvectors * principal_q[None, :]) @ data.eigenvectors.T
    COUNTERS["general_quadrature_calls"] += 1
    COUNTERS["general_quadrature_nodes"] += len(weights)
    return _result(data, mean, tensor, "general_eigenbasis_2d", n_mu, n_phi, len(weights))


def lrs_moments(t: float, s: float, *, axis: Any = (0.0, 0.0, 1.0),
                n_mu: int = 64) -> MomentResult:
    if np.ndim(s) != 0 or np.iscomplexobj(s) or not math.isfinite(float(s)):
        raise ValueError("s must be a finite real scalar")
    s = float(s)
    if not (-1.0 < s < 2.0):
        raise ValueError("LRS convention requires -1<s<2")
    if np.iscomplexobj(axis):
        raise ValueError("axis must be real")
    direction = np.asarray(axis, dtype=float)
    if direction.shape != (3,) or not np.all(np.isfinite(direction)):
        raise ValueError("axis must be a finite three-vector")
    length = float(np.linalg.norm(direction))
    if not math.isfinite(length) or length == 0.0:
        raise ValueError("axis must have a finite nonzero norm")
    direction = direction / length
    axis_projector = np.outer(direction, direction)
    data = validate_inputs(t, s * (1.5 * axis_projector - 0.5 * np.eye(3)))
    n_mu = _order(n_mu, "n_mu")
    mu, weights = _unit_interval_gauss(n_mu)
    q = 1.0 + s * (1.5 * mu * mu - 0.5)
    weighted_beta = weights * beta_vector(data.t, q)
    mean = float(np.sum(weighted_beta))
    q_axis = float(np.dot(weighted_beta, mu * mu - 1.0 / 3.0))
    tensor = 1.5 * q_axis * (axis_projector - np.eye(3) / 3.0)
    COUNTERS["lrs_quadrature_calls"] += 1
    COUNTERS["lrs_quadrature_nodes"] += len(weights)
    return _result(data, mean, tensor, "lrs_1d", n_mu, 1, len(weights))


def lab_frame_oracle(t: float, S: np.ndarray, *, n_mu: int = 128,
                     n_phi: int = 256) -> MomentResult:
    """Independent full-sphere discretization, with no principal-frame integration."""
    data = validate_inputs(t, S)
    n_mu, n_phi = _order(n_mu, "n_mu"), _order(n_phi, "n_phi")
    mu, w_mu = np.polynomial.legendre.leggauss(n_mu)
    phi = np.arange(n_phi) * (2.0 * math.pi / n_phi)
    rho = np.sqrt(1.0 - mu[:, None] ** 2)
    directions = np.stack((rho * np.cos(phi)[None, :], rho * np.sin(phi)[None, :],
                           np.broadcast_to(mu[:, None], (n_mu, n_phi))), axis=-1).reshape(-1, 3)
    weights = np.broadcast_to(w_mu[:, None] / (2.0 * n_phi), (n_mu, n_phi)).ravel()
    q = 1.0 + np.einsum("ni,ij,nj->n", directions, data.tensor, directions)
    weighted_beta = weights * beta_vector(data.t, q)
    mean = float(np.sum(weighted_beta))
    tensor = (directions.T * weighted_beta) @ directions - np.eye(3) * mean / 3.0
    COUNTERS["lab_oracle_calls"] += 1
    COUNTERS["lab_oracle_nodes"] += len(weights)
    return _result(data, mean, tensor, "lab_frame_full_sphere_oracle", n_mu, n_phi, len(weights))


def observed_difference(coarse: MomentResult, fine: MomentResult, normalization: float) -> dict[str, Any]:
    return {"kind": "FINITE_TWO_LEVEL_OBSERVATION_NOT_CERTIFIED",
            "scalar": abs(fine.mean - coarse.mean) / normalization,
            "tensor_F": float(np.linalg.norm(fine.pstf - coarse.pstf, ord="fro")) / normalization}
