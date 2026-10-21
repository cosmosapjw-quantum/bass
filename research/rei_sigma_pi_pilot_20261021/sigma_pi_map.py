"""Unit-explicit, source-independent C15 initial invariant adapter.

This module changes no owner physics. kappa_time is 8*pi*G/c**2, not
C15's KAPPA=8*pi*G/(3*c**2). All pressures/energy densities are J/m^3.
"""
from __future__ import annotations

import math


def invariants(*, s: float, H: float, delta_pressure: float,
               kappa_time: float) -> dict[str, float | int | str]:
    values = (s, H, delta_pressure, kappa_time)
    if not all(math.isfinite(x) for x in values) or H <= 0 or kappa_time <= 0:
        raise ValueError("finite expanding state and positive kappa_time required")
    sigma = math.sqrt(3) * abs(s) / H
    pi = kappa_time * abs(delta_pressure) / (math.sqrt(3) * H * H)
    return {
        "norm_convention": "half_contraction",
        "Sigma_half": sigma, "Pi_half": pi,
        "Sigma_frobenius": math.sqrt(2) * sigma,
        "Pi_frobenius": math.sqrt(2) * pi,
        "shear_sign": (1 if s > 0 else -1 if s < 0 else 0),
        "stress_sign": (1 if delta_pressure > 0 else -1 if delta_pressure < 0 else 0),
        "shear_work_J_m3_s": 2 * s * delta_pressure,
    }


def initial_seed(*, Sigma_half: float, Pi_half: float,
                 shear_sign: int, stress_sign: int,
                 H_base: float, stress_per_alpha: float,
                 kappa_time: float) -> dict[str, float | int | str]:
    """Map (Sigma,Pi) to a common positive P2 initial seed.

    stress_per_alpha is W=(rho_gamma+rho_nu+rho_m_ref*J01)/5, evaluated
    from the actual fixed source at b=x=0 with all included stress terms on.
    The caller must verify the achieved invariants using owner initial().
    No requested coordinate or negative angular weight is clipped.
    """
    values = (Sigma_half, Pi_half, H_base, stress_per_alpha, kappa_time)
    if not all(math.isfinite(x) for x in values):
        raise ValueError("finite input required")
    if not 0 <= Sigma_half < math.sqrt(3) or Pi_half < 0:
        raise ValueError("initial invariant domain")
    if H_base <= 0 or stress_per_alpha <= 0 or kappa_time <= 0:
        raise ValueError("positive source calibration required")
    if shear_sign not in (-1, 0, 1) or stress_sign not in (-1, 0, 1):
        raise ValueError("sign must be -1, 0, or 1")
    if (Sigma_half == 0) != (shear_sign == 0):
        raise ValueError("zero shear requires and only permits zero orientation")
    if (Pi_half == 0) != (stress_sign == 0):
        raise ValueError("zero stress requires and only permits zero orientation")
    H = H_base / math.sqrt(1 - Sigma_half * Sigma_half / 3)
    s = shear_sign * Sigma_half * H / math.sqrt(3)
    D = stress_sign * math.sqrt(3) * H * H * Pi_half / kappa_time
    alpha = D / stress_per_alpha
    if not -1 <= alpha <= 2:
        raise ValueError("requested Pi outside positive common-P2 family")
    cap = kappa_time * stress_per_alpha / (math.sqrt(3) * H * H)
    return {"H_initial_per_s": H, "s_initial_per_s": s,
            "delta_pressure_initial_Pa": D, "common_P2_alpha": alpha,
            "Pi_half_negative_cap": cap, "Pi_half_positive_cap": 2 * cap,
            **invariants(s=s, H=H, delta_pressure=D, kappa_time=kappa_time)}
