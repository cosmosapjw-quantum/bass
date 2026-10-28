"""CE1-G: scoped MPFR whole-panel time+source enclosure for CE1-F tabulated Bianchi-I.

This certifies the exact-real continuum Einstein--Vlasov ODE against the
*recorded binary64 RK4 knot state* using the stored binary Hermite coefficients.
It is not a formally verified Python/MPFR program and is not a native solver.
No source renormalization, constraint projection, or hidden numerical fallback.
"""
from __future__ import annotations

import math
from fractions import Fraction

import numpy as np

from .einstein_error_budget import HermitePath, rk4_path, _real
from .einstein_interval import (
    Interval, _maxabs, _bernstein_box_binary, _hermite_binary_eval,
    residual_taylor_mpfr, propagate_interval,
)
from .einstein_tabulated_source import (
    TabulatedRadiation, certified_tabulated_geometry,
    certified_tabulated_pressure,
)


def _panel_endpoint_jump(path: HermitePath, i: int) -> tuple[float, float]:
    """Exact binary cubic at v=1 versus next stored binary knot.

    This matters: rounded Hermite coefficients need not interpolate the
    recorded next state *exactly as real numbers*. A proof for the piecewise
    exact-binary polynomials must carry every such jump, including at t=end.
    """
    y_end, _ = _hermite_binary_eval(path, i, Interval(1))
    jumps = [_maxabs(y_end[k] - Interval(float(path.states[i + 1, k])))
             for k in range(6)]
    return max(jumps[:3]), max(jumps[3:])


def certify_tabulated_computed_path(
    source: TabulatedRadiation,
    path: HermitePath,
    *,
    end: float = .08,
    shear=(.2, -.13, -.07),
    subcells: int = 1,
) -> dict:
    """Outward a posteriori continuum ODE vs recorded RK4 knot geometry.

    The exact continuum initial measure is the positive CE1-F table. The
    reference shear uses exact stored binary sx,sy and sz=-(sx+sy). The
    recorded RK4/Hermite path and stored source ray/mass floats are interpreted
    as exact real binary input data. MPFR192 directed operations enclose the
    pressure source and all time-panel residuals. The analytic fourth-
    derivative majorant is inherited from CE1-C and applies to *positive*
    stored rays/masses on the expanding diagonal channel.

    The total is decomposed into (a) continuum initial constraint mismatch,
    (b) continuum-vs-stored source, (c) reconstructed time defect + every
    exact-binary Hermite knot jump. A conservative shared Emax propagates all
    three nonnegative errors with a positive 2x2 comparison system.
    """
    if not isinstance(source, TabulatedRadiation) or not isinstance(path, HermitePath):
        raise TypeError('CE1-F TabulatedRadiation and HermitePath required')
    T = float(end)
    if not math.isfinite(T) or not 0 < T <= .2:
        raise ValueError('Admitted time horizon must lie in (0,.2]')
    if isinstance(subcells, bool) or not isinstance(subcells, int) or not 1 <= subcells <= 32:
        raise ValueError('subcells must be integer in 1..32')
    if len(path.times) < 2 or path.times[0] != 0 or path.times[-1] != T:
        raise ValueError('Path must cover exact stored binary time interval [0,end]')
    if not np.array_equal(path.states[0], source.initial_state(shear)):
        raise ValueError('Path initial state differs from frozen source/shear fixture')
    if not np.all(np.isfinite(path.coefficients)):
        raise ValueError('Nonfinite binary Hermite coefficients')

    initial = certified_tabulated_geometry(source, end=T, shear=shear)
    Emax = Interval(float(initial['energy_max_upper']))
    if Emax.lower <= 0:
        raise ValueError('Positive energy bound required')
    global_box = list(initial['geometry_box_upper'])
    panel_hulls = []
    for i in range(len(path.times) - 1):
        lo, hi = _bernstein_box_binary(path, i)
        if min(lo) < 0:
            raise ValueError('Reconstructed Hermite path exits expanding octant')
        if not all(math.isfinite(v) for v in (*lo, *hi)):
            raise ValueError('Nonfinite Hermite path hull')
        for k in range(3):
            global_box[k] = max(global_box[k], hi[k])
        panel_hulls.append((lo, hi))
    if max(global_box) > 2:
        raise ValueError('Source box outside CE1-F certified range')
    source_cert = certified_tabulated_pressure(source, global_box)
    eta = Interval(float(source_cert['bound_max']))
    initial_error = [Interval(0), Interval(float(initial['initial_h_error_upper']))]
    source_error = [Interval(0), Interval(0)]
    time_error = [Interval(0), Interval(0)]
    rows = []
    max_jump_ell = max_jump_h = 0.
    for i in range(len(path.times) - 1):
        defect = residual_taylor_mpfr(source, path, i, subcells=subcells)
        dt = Interval(float(path.times[i + 1])) - Interval(float(path.times[i]))
        initial_error = propagate_interval(initial_error, dt, Emax, Interval(0), Interval(0))
        source_error = propagate_interval(source_error, dt, Emax, Interval(0), eta)
        time_error = propagate_interval(time_error, dt, Emax,
                                        Interval(float(defect['ell_defect'])),
                                        Interval(float(defect['h_defect'])))
        je, jh = _panel_endpoint_jump(path, i)
        max_jump_ell = max(max_jump_ell, je)
        max_jump_h = max(max_jump_h, jh)
        # Compare to the next stored knot, not the preceding polynomial limit.
        time_error = [time_error[0] + Interval(je), time_error[1] + Interval(jh)]
        rows.append({
            'panel': i,
            'u_right': float(path.times[i + 1]),
            'ell_defect_upper': defect['ell_defect'],
            'h_defect_upper': defect['h_defect'],
            'fourth_derivative_upper': defect['fourth_derivative_bound'],
            'knot_jump_ell_upper': je,
            'knot_jump_h_upper': jh,
            'initial_envelope': [x.upper for x in initial_error],
            'source_envelope': [x.upper for x in source_error],
            'time_and_jumps_envelope': [x.upper for x in time_error],
        })
    components = [initial_error, source_error, time_error]
    total = [sum((part[k] for part in components), Interval(0)).upper for k in range(2)]
    return {
        'status': 'SCOPED_MPFR_TABULATED_COMPUTED_PATH_ENCLOSURE',
        'continuum_vs_stored_rk4_knot': True,
        'u_end': T,
        'steps': len(path.times)-1,
        'subcells': subcells,
        'refinement': source.refinement,
        'rays': len(source.n),
        'source_pressure_upper': eta.upper,
        'geometry_box_upper': global_box,
        'Emax_upper': Emax.upper,
        'initial_ell_h_upper': [z.upper for z in initial_error],
        'source_ell_h_upper': [z.upper for z in source_error],
        'time_and_jump_ell_h_upper': [z.upper for z in time_error],
        'total_ell_h_upper': total,
        'max_knot_jump_ell_upper': max_jump_ell,
        'max_knot_jump_h_upper': max_jump_h,
        'rounding': 'MPFR192_RNDD_RNDU',
        'path_semantics': 'exact real piecewise cubic of stored binary coefficients, including all knot jumps',
        'source_semantics': 'exact stored binary ray/mass source vs exact binary physical cell table',
        'analytic_remainder': 'CE1-C positive-ray fourth derivative majorant',
        'full_machine_proof': False,
        'native_implementation': False,
        'production_ready': False,
        'rows': rows,
    }


def run_scoped_tabulated_rk4(
    source: TabulatedRadiation,
    *,
    steps: int,
    end: float = .08,
    shear=(.2, -.13, -.07),
    subcells: int = 1,
    backend=None,
) -> dict:
    """Generate one float64 RK4 path and certify its recorded binary output."""
    if backend != 'python_oracle':
        raise ValueError("Explicit backend='python_oracle' required")
    if isinstance(steps, bool) or not isinstance(steps, int) or not 1 <= steps <= 256:
        raise ValueError('Integer RK4 steps in 1..256 required')
    path = rk4_path(source, source.initial_state(shear), end, steps, backend=backend)
    return certify_tabulated_computed_path(source, path, end=end,
                                          shear=shear, subcells=subcells)