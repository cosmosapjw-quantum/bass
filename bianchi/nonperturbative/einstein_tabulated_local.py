"""CE1-I: time-panel-local sharp pressure Jacobian for a fixed Bianchi-I table.

Entirely opt-in, exact-binary-input MPFR192 a posteriori comparison. Reuses the
CE1-H/CE1-G recorded path certificate and its fourth-order residual majorants.
No change to the source, RK4 path, cutoff or original acceptance target.
"""
from __future__ import annotations

import math

import numpy as np

from .einstein_error_budget import HermitePath, rk4_path
from .einstein_interval import (
    Interval, _bernstein_box_binary, _iv_fraction, propagate_interval,
)
from .einstein_tabulated_source import TabulatedRadiation, _q, _real
from .einstein_tabulated_sharp import (
    initial_continuum_pressure_cap, _initial_constraint_mismatch,
)
from .einstein_tabulated_time import certify_tabulated_computed_path


def _exact_expansion_initial(source: TabulatedRadiation, shear) -> tuple[list[Interval], Interval]:
    """Outward exact-binary initial h_i and theta0 for continuum cell energy."""
    s = _real(shear, (3,))
    # CE1-F exact initial constraint contracts s_z = -(s_x+s_y).
    sx, sy = _iv_fraction(_q(s[0])), _iv_fraction(_q(s[1]))
    si = [sx, sy, -(sx + sy)]
    E0 = _iv_fraction(source.continuum_energy)
    hbar = ((E0 + sum((v*v for v in si), Interval(0))/2)/3).sqrt()
    h0 = [hbar + v for v in si]
    theta0 = 3 * hbar
    if any(h.lower <= 0 for h in h0) or theta0.lower <= 0:
        raise ValueError('Strict all-direction-expanding continuum initial data required')
    return h0, theta0


def _local_pressure_caps(
    source: TabulatedRadiation, path: HermitePath, shear, pmax0: float
) -> list[dict]:
    """For every full Hermite panel, certify a shared positive lower log-scale.

    theta'=-theta**2+E<=E0-theta**2, theta0**2>=E0 yields theta<=theta0.
    Exact ell_i(u)>=h_i0*(1-exp(-theta0*u))/theta0. The full-panel
    Bernstein hull bounds the separate stored-binary Hermite curve.
    """
    h0, theta0 = _exact_expansion_initial(source, shear)
    theta_up = Interval(theta0.upper)
    rows = []
    for j in range(len(path.times)-1):
        lo, hi = _bernstein_box_binary(path, j)
        if min(lo) < 0:
            raise ValueError('Stored Hermite path exits expanding octant')
        uleft = Interval(float(path.times[j]))
        integral = (Interval(1) - (-theta_up * uleft).exp()) / theta_up
        exact_lower = [(h * integral).lower for h in h0]
        # Both terms are outward LOWER bounds. Positive-octant certification
        # permits the 0 floor, including the original panel at u=0.
        common_lower = max(0.0, min(*exact_lower, *lo[:3]))
        if not math.isfinite(common_lower):
            raise ValueError('Nonfinite lower geometry bound')
        pcap = (Interval(float(pmax0)) * (-4*Interval(common_lower)).exp()).upper
        pcap = min(float(pmax0), pcap)
        rows.append({
            'panel': j,
            'u_left': float(path.times[j]),
            'u_right': float(path.times[j+1]),
            'exact_lower_at_left': exact_lower,
            'stored_bernstein_lower': lo[:3],
            'shared_logscale_lower': common_lower,
            'pressure_cap_upper': pcap,
            'lipschitz_upper': (4*Interval(pcap)).upper,
            'ratio_to_initial_cap': (Interval(pcap)/Interval(float(pmax0))).upper,
        })
    return rows


def certify_local_tabulated_path(
    source: TabulatedRadiation,
    path: HermitePath,
    *,
    end: float = .08,
    shear=(.2, -.13, -.07),
    subcells: int = 1,
) -> dict:
    """MPFR whole-panel certificate using rigorously decreasing local pressure cap.

    Source/ODE/path physics is exactly the CE1-H physical fixture. The caller
    must not mistake conditional exact-binary program calculations for a formal
    verification of arbitrary float64 programs or observed skies.
    """
    if not isinstance(source, TabulatedRadiation) or not isinstance(path, HermitePath):
        raise TypeError('CE1-F TabulatedRadiation and HermitePath required')
    # PR244 check lives in the shared CE1-G parent certification; do not
    # duplicate the legacy guard. The current MPFR majorant is recomputed.
    # Exactly one costly parent whole-panel MPFR evaluation. Reuse its actual
    # unpropagated source forcing and residual/jump carriers. Neither pressure
    # nor time error is inverted from a secondary integrated envelope.
    baseline = certify_tabulated_computed_path(source, path, end=end,
                                              shear=shear, subcells=subcells)
    p0 = initial_continuum_pressure_cap(source)
    pmax0 = min(p0['pressure_max_upper'], baseline['Emax_upper'])
    caps = _local_pressure_caps(source, path, shear, pmax0)
    eta = Interval(float(baseline['source_pressure_upper']))
    delta0 = Interval(_initial_constraint_mismatch(source, path, shear))

    def propagate_with(pressure_caps):
        initial_error = [Interval(0), delta0]
        source_error = [Interval(0), Interval(0)]
        time_error = [Interval(0), Interval(0)]
        rows = []
        for j, (cap, defect) in enumerate(zip(pressure_caps, baseline['rows'])):
            dt = Interval(float(path.times[j+1])) - Interval(float(path.times[j]))
            local_energy = Interval(float(cap))
            initial_error = propagate_interval(initial_error, dt, local_energy,
                                               Interval(0), Interval(0))
            source_error = propagate_interval(source_error, dt, local_energy,
                                              Interval(0), eta)
            time_error = propagate_interval(time_error, dt, local_energy,
                                            Interval(float(defect['ell_defect_upper'])),
                                            Interval(float(defect['h_defect_upper'])))
            time_error = [
                time_error[0] + Interval(float(defect['knot_jump_ell_upper'])),
                time_error[1] + Interval(float(defect['knot_jump_h_upper'])),
            ]
            rows.append({
                'panel': j,
                'initial_envelope': [v.upper for v in initial_error],
                'source_envelope': [v.upper for v in source_error],
                'time_and_jump_envelope': [v.upper for v in time_error],
            })
        total = [sum((z[k] for z in (initial_error, source_error, time_error)),
                     Interval(0)).upper for k in (0, 1)]
        return total, rows, initial_error, source_error, time_error

    sharp, _, _, _, _ = propagate_with([pmax0 for _ in caps])
    total, panel_errors, initial, source_err, time_err = propagate_with(
        [row['pressure_cap_upper'] for row in caps])
    if any(total[k] > sharp[k] for k in range(2)):
        raise ArithmeticError('Local pressure bound exceeds CE1-H on identical inputs')
    rows = [{**cap, **r} for cap, r in zip(caps, panel_errors)]
    return {
        'status': 'SCOPED_CE1I_TIME_LOCAL_PRESSURE_COMPARISON',
        'refinement': source.refinement,
        'rays': len(source.n),
        'steps': len(path.times)-1,
        'u_end': float(end),
        'pressure_initial_max_upper': pmax0,
        'initial_pressure_lipschitz_upper': (4*Interval(pmax0)).upper,
        'time_local_pressure_caps': [row['pressure_cap_upper'] for row in rows],
        'time_local_lipschitz_upper': [row['lipschitz_upper'] for row in rows],
        'time_local_min_logscale_lower': [row['shared_logscale_lower'] for row in rows],
        'source_pressure_upper': baseline['source_pressure_upper'],
        'geometry_box_upper': baseline['geometry_box_upper'],
        'initial_ell_h_upper': [v.upper for v in initial],
        'source_ell_h_upper': [v.upper for v in source_err],
        'time_and_jump_ell_h_upper': [v.upper for v in time_err],
        'local_total_ell_h_upper': total,
        'ce1h_total_ell_h_upper': sharp,
        'ce1g_total_ell_h_upper': baseline['total_ell_h_upper'],
        'rounding': 'MPFR192_RNDD_RNDU_EXACT_BINARY_INPUT',
        'fixed_target_h': 1e-5,
        'target_met': total[1] < 1e-5,
        'full_machine_proof': False,
        'production_ready': False,
        'native_implementation': False,
        'rows': rows,
    }


def run_local_tabulated_rk4(
    source: TabulatedRadiation,
    *,
    steps: int,
    end: float = .08,
    shear=(.2, -.13, -.07),
    subcells: int = 1,
    backend=None,
) -> dict:
    """Opt-in source/time/local-coefficient certificate, never a native fallback."""
    if backend != 'python_oracle':
        raise ValueError("Explicit backend='python_oracle' required")
    if isinstance(steps, bool) or not isinstance(steps, int) or not 1 <= steps <= 256:
        raise ValueError('Integer RK4 steps in 1..256 required')
    path = rk4_path(source, source.initial_state(shear), end, steps, backend=backend)
    return certify_local_tabulated_path(source, path, end=end, shear=shear,
                                       subcells=subcells)
