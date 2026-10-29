"""CE1-H: pressure-moment sharpened nonlinear error envelope for CE1-G.

The new theorem replaces CE1-G's 4*Emax pressure Lipschitz coefficient by
4*max_i P_i^continuum(0), for nonnegative angular energy and ell_i>=0.
All MPFR intervals retain exact stored binary input semantics. It is not a
formal proof of the Python/MPFR implementation or a production backend.
"""
from __future__ import annotations

from .einstein_interval import Interval, _iv_fraction, _maxabs, propagate_interval
from .einstein_tabulated_source import TabulatedRadiation, _q, _real
from .einstein_tabulated_time import certify_tabulated_computed_path
from .einstein_error_budget import HermitePath, rk4_path


def initial_continuum_pressure_cap(source: TabulatedRadiation) -> dict:
    """Enclose exact continuum P_i(ell=0) from the original physical cells.

    The physical angular density is constant on each original first-octant
    solid-angle cell. Exact initial pressure is sum E_cell * mean(n_i^2).
    The cell means are outward MPFR192 intervals computed using rational cell
    edges and directed sinpi/cospi. No float64 moment evaluation is reused.
    """
    if not isinstance(source, TabulatedRadiation):
        raise TypeError('CE1-F TabulatedRadiation required')
    pressures = [Interval(0) for _ in range(3)]
    for cell in source.cells:
        # This exact-real identity is a property of unit sphere directions.
        means_sum = sum(cell.means, Interval(0))
        if not means_sum.contains(1):
            raise ArithmeticError('Initial cell means fail unit-sphere sum identity')
        w = _iv_fraction(cell.energy)
        if w.lower < 0:
            raise ValueError('Nonnegative cell energies required')
        for i in range(3):
            pressures[i] = pressures[i] + w * cell.means[i]
    total = sum(pressures, Interval(0))
    E = _iv_fraction(source.continuum_energy)
    if total.lower > E.lower or total.upper < E.upper:
        raise ArithmeticError('Directional pressures do not enclose exact continuum E0')
    cap = max(x.upper for x in pressures)
    return {
        'status': 'SCOPED_EXACT_CONTINUUM_INITIAL_PRESSURE',
        'method': 'MPFR192_EXACT_CELL_MEANS',
        'pressure_intervals': [(x.lower, x.upper) for x in pressures],
        'pressure_max_upper': cap,
        'energy_continuum_upper': E.upper,
        'lipschitz_upper': 4 * cap,
        'exact_continuum_sum_identity': True,
        'input_semantics': 'exact stored binary original cell edges and energies',
        'formal_machine_verified': False,
    }



def _initial_constraint_mismatch(source, path, shear):
    """Direct exact-binary Hamiltonian root, no duplicate source quadrature."""
    s = _real(shear, (3,))
    sx, sy = _iv_fraction(_q(s[0])), _iv_fraction(_q(s[1]))
    sh = [sx, sy, -(sx + sy)]
    E = _iv_fraction(source.continuum_energy)
    hbar = ((E + sum((z*z for z in sh), Interval(0))/2)/3).sqrt()
    return max(_maxabs((hbar + sh[i]) - Interval(float(path.states[0, 3+i])))
               for i in range(3))


def certify_sharp_tabulated_path(
    source: TabulatedRadiation,
    path: HermitePath,
    *,
    end: float = .08,
    shear=(.2, -.13, -.07),
    subcells: int = 1,
) -> dict:
    """Sharpen CE1-G's exact continuum-vs-binary-Hermite path enclosure.

    This runs the parent CE1-G certificate first and reuses its *whole-panel*
    MPFR source and time defects and exact-binary knot jumps, not sampled
    residuals. Only the proven pressure Lipschitz coefficient changes.
    Emax remains the independent bound for exact expanding-solution geometry.
    """
    if not isinstance(source, TabulatedRadiation) or not isinstance(path, HermitePath):
        raise TypeError('CE1-F source and CE1-G HermitePath required')
    baseline = certify_tabulated_computed_path(
        source, path, end=end, shear=shear, subcells=subcells)
    p0 = initial_continuum_pressure_cap(source)
    Emax = float(baseline['Emax_upper'])
    # Both quantities separately bound max_i P_i^continuum(0): P_i(0)<=E_cont(0)<=Emax.
    # Taking their minimum is rigorous even if one MPFR upper rounds a ulp wider.
    pmax = min(p0['pressure_max_upper'], Emax)
    Ecomparison = Interval(pmax)  # propagate_interval uses k=2 sqrt(Ecomparison)
    eta = Interval(float(baseline['source_pressure_upper']))
    initial_error = [Interval(0), Interval(_initial_constraint_mismatch(source, path, shear))]
    source_error = [Interval(0), Interval(0)]
    time_error = [Interval(0), Interval(0)]
    rows = []
    for i, old in enumerate(baseline['rows']):
        dt = Interval(float(path.times[i + 1])) - Interval(float(path.times[i]))
        initial_error = propagate_interval(initial_error, dt, Ecomparison,
                                           Interval(0), Interval(0))
        source_error = propagate_interval(source_error, dt, Ecomparison,
                                          Interval(0), eta)
        time_error = propagate_interval(
            time_error, dt, Ecomparison,
            Interval(float(old['ell_defect_upper'])),
            Interval(float(old['h_defect_upper'])))
        # Outward MPFR jumps already computed from exact binary coefficients.
        time_error = [time_error[0] + Interval(float(old['knot_jump_ell_upper'])),
                      time_error[1] + Interval(float(old['knot_jump_h_upper']))]
        rows.append({
            'panel': i, 'u_right': float(path.times[i + 1]),
            'initial_envelope': [x.upper for x in initial_error],
            'source_envelope': [x.upper for x in source_error],
            'time_and_jumps_envelope': [x.upper for x in time_error],
        })
    components = [initial_error, source_error, time_error]
    total = [sum((part[k] for part in components), Interval(0)).upper for k in range(2)]
    # This must be at least as tight as the parent bound for identical data.
    if any(total[k] > baseline['total_ell_h_upper'][k] for k in range(2)):
        raise ArithmeticError('Sharp bound unexpectedly exceeds CE1-G bound')
    return {
        'status': 'SCOPED_CE1H_SHARP_PRESSURE_COMPARISON',
        'refinement': source.refinement, 'rays': len(source.n),
        'u_end': float(end), 'steps': len(path.times) - 1,
        'pressure_initial_certificate': p0,
        'pressure_lipschitz_upper': 4 * pmax,
        'Emax_upper': Emax,
        'comparison_pressure_cap': pmax,
        'comparison_coefficient_ratio': pmax / Emax,
        'ce1g_total_ell_h_upper': baseline['total_ell_h_upper'],
        'ce1g_source_ell_h_upper': baseline['source_ell_h_upper'],
        'sharp_initial_ell_h_upper': [x.upper for x in initial_error],
        'sharp_source_ell_h_upper': [x.upper for x in source_error],
        'sharp_time_and_jump_ell_h_upper': [x.upper for x in time_error],
        'sharp_total_ell_h_upper': total,
        'max_knot_jump_ell_upper': baseline['max_knot_jump_ell_upper'],
        'max_knot_jump_h_upper': baseline['max_knot_jump_h_upper'],
        'source_semantics': 'CE1-F exact continuum positive angular cells vs exact stored binary ray/mass source',
        'time_semantics': 'CE1-G exact stored binary Hermite full-panel residual and jumps',
        'new_proof': 'monotone pressure Jacobian; exact initial pressure Lipschitz 4 max_i P_i(0)',
        'rounding': 'MPFR192_RNDD_RNDU',
        'full_machine_proof': False, 'native_implementation': False,
        'production_ready': False, 'rows': rows,
    }


def run_sharp_tabulated_rk4(
    source: TabulatedRadiation,
    *,
    steps: int,
    end: float = .08,
    shear=(.2, -.13, -.07),
    subcells: int = 1,
    backend=None,
) -> dict:
    """Opt-in sharp certificate for the same recorded float64 RK4 path."""
    if backend != 'python_oracle':
        raise ValueError("Explicit backend='python_oracle' required")
    if isinstance(steps, bool) or not isinstance(steps, int) or not 1 <= steps <= 256:
        raise ValueError('Integer RK4 steps in 1..256 required')
    path = rk4_path(source, source.initial_state(shear), end, steps, backend=backend)
    return certify_sharp_tabulated_path(source, path, end=end,
                                       shear=shear, subcells=subcells)
