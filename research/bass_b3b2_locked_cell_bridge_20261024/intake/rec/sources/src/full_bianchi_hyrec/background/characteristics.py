"""Normal-frame and exact finite-tilt hydrogen-frame characteristics."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .snapshot import BackgroundSnapshot


def _unit(value):
    vector = np.asarray(value, dtype=float)
    if vector.shape != (3,) or not np.all(np.isfinite(vector)):
        raise ValueError("direction must be a finite vector of shape (3,)")
    norm = float(np.linalg.norm(vector))
    if norm == 0.0:
        raise ValueError("direction must be nonzero")
    return vector / norm


@dataclass(frozen=True)
class FrameCharacteristic:
    direction_normal: np.ndarray
    R_normal_s_inv: float
    D0_direction_normal_s_inv: np.ndarray


@dataclass(frozen=True)
class HydrogenFrameCharacteristic:
    direction_normal: np.ndarray
    direction_hydrogen: np.ndarray
    doppler_factor: float
    R_normal_s_inv: float
    R_hydrogen_s_inv: float
    D0_direction_normal_s_inv: np.ndarray
    D0_direction_hydrogen_s_inv: np.ndarray
    D0_log_doppler_s_inv: float


def _spatial_connection_double(N, A, direction):
    n = direction
    return (
        A
        - float(A @ n) * n
        + np.cross(n, N @ n)
    )


def normal_frame_characteristic(
    snapshot: BackgroundSnapshot,
    direction,
) -> FrameCharacteristic:
    n = _unit(direction)
    sigma_n = snapshot.sigma_s_inv @ n
    n_sigma_n = float(n @ sigma_n)
    spatial = _spatial_connection_double(
        snapshot.N_s_inv,
        snapshot.A_s_inv,
        n,
    )
    dn = (
        -(sigma_n - n_sigma_n * n)
        + np.cross(snapshot.frame_rotation_s_inv, n)
        - (spatial - float(n @ spatial) * n)
    )
    R_normal = -(snapshot.H_s_inv + n_sigma_n)
    return FrameCharacteristic(
        direction_normal=n,
        R_normal_s_inv=float(R_normal),
        D0_direction_normal_s_inv=dn,
    )


def doppler_factor(beta, direction) -> float:
    beta = np.asarray(beta, dtype=float)
    n = _unit(direction)
    beta2 = float(beta @ beta)
    if beta.shape != (3,) or beta2 >= 1.0:
        raise ValueError("beta must have shape (3,) and norm below one")
    gamma = 1.0 / np.sqrt(1.0 - beta2)
    return float(gamma * (1.0 - beta @ n))


def aberrate_direction(beta, direction):
    beta = np.asarray(beta, dtype=float)
    n = _unit(direction)
    beta2 = float(beta @ beta)
    if beta.shape != (3,) or beta2 >= 1.0:
        raise ValueError("beta must have shape (3,) and norm below one")
    if beta2 < 1e-28:
        return n.copy()
    gamma = 1.0 / np.sqrt(1.0 - beta2)
    bn = float(beta @ n)
    D = gamma * (1.0 - bn)
    result = (
        n
        + (((gamma - 1.0) * bn / beta2) - gamma) * beta
    ) / D
    return _unit(result)


def _aberration_derivative(beta, dbeta, n, dn):
    beta2 = float(beta @ beta)
    if beta2 < 1e-20:
        # First-order aberration n_H=n-beta+(beta.n)n.
        return dn - dbeta + float(dbeta @ n) * n

    gamma = 1.0 / np.sqrt(1.0 - beta2)
    bdot = float(beta @ dbeta)
    dgamma = gamma**3 * bdot
    bn = float(beta @ n)
    dbn = float(dbeta @ n + beta @ dn)
    dbeta2 = 2.0 * bdot

    coefficient = (gamma - 1.0) * bn / beta2 - gamma
    dcoefficient = (
        dgamma * bn / beta2
        + (gamma - 1.0) * dbn / beta2
        - (gamma - 1.0) * bn * dbeta2 / beta2**2
        - dgamma
    )
    numerator = n + coefficient * beta
    dnumerator = dn + dcoefficient * beta + coefficient * dbeta
    D = gamma * (1.0 - bn)
    dD = dgamma * (1.0 - bn) - gamma * dbn
    derivative = (dnumerator * D - numerator * dD) / D**2
    direction_h = numerator / D
    # Remove round-off radial leakage without altering the analytic tangent.
    derivative -= float(direction_h @ derivative) * direction_h
    return derivative


def hydrogen_frame_characteristic(
    snapshot: BackgroundSnapshot,
    normal: FrameCharacteristic,
) -> HydrogenFrameCharacteristic:
    beta = snapshot.beta_H
    dbeta = snapshot.D0_beta_H_s_inv
    n = normal.direction_normal
    dn = normal.D0_direction_normal_s_inv
    beta2 = float(beta @ beta)
    gamma = 1.0 / np.sqrt(1.0 - beta2)
    bn = float(beta @ n)
    denominator = 1.0 - bn
    D = gamma * denominator
    dlogD = (
        gamma**2 * float(beta @ dbeta)
        - float(dbeta @ n + beta @ dn) / denominator
    )
    direction_h = aberrate_direction(beta, n)
    dn_h = _aberration_derivative(beta, dbeta, n, dn)
    return HydrogenFrameCharacteristic(
        direction_normal=n,
        direction_hydrogen=direction_h,
        doppler_factor=float(D),
        R_normal_s_inv=normal.R_normal_s_inv,
        R_hydrogen_s_inv=float(normal.R_normal_s_inv + dlogD),
        D0_direction_normal_s_inv=dn,
        D0_direction_hydrogen_s_inv=dn_h,
        D0_log_doppler_s_inv=float(dlogD),
    )


def doppler_coordinate_speed(
    R_hydrogen_s_inv,
    x_boundary,
    *,
    nu_abs_Hz,
    Doppler_width_Hz,
    D0_nu_abs_Hz_s=0.0,
    D0_log_Doppler_width_s_inv=0.0,
    D0_x_boundary_s_inv=0.0,
):
    if Doppler_width_Hz <= 0.0 or nu_abs_Hz <= 0.0:
        raise ValueError("nu_abs_Hz and Doppler_width_Hz must be positive")
    x = np.asarray(x_boundary, dtype=float)
    frequency = nu_abs_Hz + x * Doppler_width_Hz
    return (
        (frequency * np.asarray(R_hydrogen_s_inv) - D0_nu_abs_Hz_s)
        / Doppler_width_Hz
        - x * D0_log_Doppler_width_s_inv
        - D0_x_boundary_s_inv
    )


# Convenient reference used by tests and external symbolic adapters.
hydrogen_frame_characteristic.doppler_factor = doppler_factor
