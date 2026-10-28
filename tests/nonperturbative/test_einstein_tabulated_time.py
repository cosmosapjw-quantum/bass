"""CE1-G: MPFR full-path tests against exact stored binary Hermite coefficients."""
from fractions import Fraction

import numpy as np
import pytest
from scipy.integrate import solve_ivp
from numpy.polynomial.legendre import leggauss

from bianchi.nonperturbative.einstein_error_budget import rk4_path
from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation
from bianchi.nonperturbative.einstein_tabulated_time import (
    _panel_endpoint_jump, certify_tabulated_computed_path, run_scoped_tabulated_rk4,
)
from bianchi.nonperturbative.einstein_interval import residual_taylor_mpfr


def model(refinement=1):
    return TabulatedRadiation([0, .5, 1], [0, .25, .75, 1],
                             [[.1, .25, .05], [.2, .15, .15]],
                             refinement=refinement, backend='python_oracle')


def test_explicit_backend_and_invalid_steps():
    s = model()
    with pytest.raises(ValueError, match='backend'):
        run_scoped_tabulated_rk4(s, steps=2)
    for n in (0, -1, True, 1.5, 257):
        with pytest.raises(ValueError):
            run_scoped_tabulated_rk4(s, steps=n, backend='python_oracle')


def test_computed_path_contract_and_error_decomposition():
    s = model()
    out = run_scoped_tabulated_rk4(s, steps=4, end=.08, subcells=1,
                                   backend='python_oracle')
    assert out['status'] == 'SCOPED_MPFR_TABULATED_COMPUTED_PATH_ENCLOSURE'
    assert out['continuum_vs_stored_rk4_knot']
    assert out['total_ell_h_upper'][1] > out['source_ell_h_upper'][1] > 0
    assert out['total_ell_h_upper'][1] > out['time_and_jump_ell_h_upper'][1] > 0
    assert out['total_ell_h_upper'][1] > out['initial_ell_h_upper'][1]
    assert out['source_pressure_upper'] > 0
    assert len(out['rows']) == 4
    assert all(x['h_defect_upper'] > 0 for x in out['rows'])
    assert out['rounding'] == 'MPFR192_RNDD_RNDU'
    assert out['full_machine_proof'] is False and out['production_ready'] is False


def test_exact_binary_hermite_endpoint_jumps_are_included():
    s = model()
    p = rk4_path(s, s.initial_state(), .08, 4, backend='python_oracle')
    out = certify_tabulated_computed_path(s, p, end=.08)
    for i, c in enumerate(p.coefficients):
        j = _panel_endpoint_jump(p, i)
        exact = [sum((Fraction.from_float(float(c[k, z])) for k in range(4)),
                     Fraction()) - Fraction.from_float(float(p.states[i+1, z]))
                 for z in range(6)]
        assert float(max(abs(z) for z in exact[:3])) <= j[0]
        assert float(max(abs(z) for z in exact[3:])) <= j[1]
    assert out['max_knot_jump_h_upper'] >= max(_panel_endpoint_jump(p, i)[1]
                                                  for i in range(4))


def test_knot_jump_mutation_not_silently_ignored():
    s = model()
    p = rk4_path(s, s.initial_state(), .08, 4, backend='python_oracle')
    original = _panel_endpoint_jump(p, 0)[1]
    p.coefficients[0, 3, 3] += 1e-5
    mutated = _panel_endpoint_jump(p, 0)[1]
    assert mutated > original + 5e-6
    result = certify_tabulated_computed_path(s, p, end=.08)
    assert result['max_knot_jump_h_upper'] >= mutated
    assert result['time_and_jump_ell_h_upper'][1] >= mutated


def test_reject_unrelated_initial_data_and_time_horizon():
    s = model()
    p = rk4_path(s, s.initial_state(), .08, 2, backend='python_oracle')
    with pytest.raises(ValueError, match='exact stored binary time'):
        certify_tabulated_computed_path(s, p, end=.09)
    p.states[0, 3] += .01
    with pytest.raises(ValueError, match='initial state'):
        certify_tabulated_computed_path(s, p, end=.08)


@pytest.mark.parametrize('T,subcells', [(0., 1), (.3, 1), (.08, 0), (.08, True), (.08, 33)])
def test_invalid_contract_inputs(T, subcells):
    s = model()
    p = rk4_path(s, s.initial_state(), .08, 2, backend='python_oracle')
    with pytest.raises(ValueError):
        certify_tabulated_computed_path(s, p, end=T, subcells=subcells)


def test_hermite_interior_expanding_violation_rejected():
    s = model()
    p = rk4_path(s, s.initial_state(), .08, 2, backend='python_oracle')
    # A large negative quadratic coefficient creates a negative interior hull.
    p.coefficients[0, 2, 3] = -10.
    with pytest.raises(ValueError, match='expanding octant'):
        certify_tabulated_computed_path(s, p, end=.08)


def test_source_refinement_same_physics_and_total_bound_improves():
    a, b = model(1), model(2)
    assert a.continuum_energy == b.continuum_energy
    x = run_scoped_tabulated_rk4(a, steps=4, backend='python_oracle')
    y = run_scoped_tabulated_rk4(b, steps=4, backend='python_oracle')
    assert y['source_pressure_upper'] < x['source_pressure_upper'] / 3
    assert y['total_ell_h_upper'][1] < x['total_ell_h_upper'][1]
    assert abs(y['time_and_jump_ell_h_upper'][1] - x['time_and_jump_ell_h_upper'][1]) < 1e-7


def test_taylor_residual_contains_independent_float_heldout():
    s = model(2)
    p = rk4_path(s, s.initial_state(), .08, 4, backend='python_oracle')
    for i in (0, 1, 3):
        d = residual_taylor_mpfr(s, p, i, subcells=1)
        for t in np.linspace(p.times[i], p.times[i+1], 13):
            residual = p.at(t, derivative=1) - s.rhs(t, p.at(t))
            assert max(abs(residual[:3])) <= d['ell_defect']
            assert max(abs(residual[3:])) <= d['h_defect']


def _independent_original_cell_quadrature(order=32):
    mu = [0, .5, 1]
    ph = [0, .25, .75, 1]
    energy = [[.1, .25, .05], [.2, .15, .15]]
    nodes, weights = leggauss(order)
    x_all, w_all = [], []
    for i in range(2):
        for j in range(3):
            z = mu[i] + (nodes+1)*(mu[i+1]-mu[i])/2
            angle = np.pi/2*(ph[j]+(nodes+1)*(ph[j+1]-ph[j])/2)
            Z, A = np.meshgrid(z, angle, indexing='ij')
            x_all.append(np.stack(((1-Z*Z)*np.cos(A)**2,
                                   (1-Z*Z)*np.sin(A)**2, Z*Z),axis=-1).reshape(-1,3))
            w_all.append((energy[i][j]*np.outer(weights,weights)/4).ravel())
    x = np.concatenate(x_all);w = np.concatenate(w_all)
    def pressure(ell):
        b = np.exp(-2*np.asarray(ell))
        r = np.sqrt(x@b)
        return np.exp(-sum(ell))*b*np.einsum('q,qi->i',w/r,x)
    return pressure


def test_independent_original_cell_ivp_inside_total_bound():
    s = model(1)
    out = run_scoped_tabulated_rk4(s, steps=4, end=.08, backend='python_oracle')
    ref_pressure = _independent_original_cell_quadrature()
    def rhs(t,y):
        h = y[3:]
        return np.r_[h, -sum(h)*h + ref_pressure(y[:3])]
    sol = solve_ivp(rhs,(0,.08),s.initial_state(),method='DOP853',
                    rtol=1e-12,atol=1e-14)
    p = rk4_path(s,s.initial_state(),.08,4,backend='python_oracle')
    assert sol.success
    actual = max(abs(sol.y[3:,-1]-p.states[-1,3:]))
    assert 0 < actual < out['total_ell_h_upper'][1]


def test_reject_wrong_types_and_modified_source_data():
    s = model()
    p = rk4_path(s, s.initial_state(), .08, 2, backend='python_oracle')
    with pytest.raises(TypeError):
        certify_tabulated_computed_path(object(),p)
    with pytest.raises(TypeError):
        certify_tabulated_computed_path(s,object())
    original = certify_tabulated_computed_path(s,p)
    # The path is an arbitrary recorded approximant; altered stored masses are
    # admitted as changed source data only if the certificate pays for them.
    s.mass = s.mass.copy()*1.2
    changed = certify_tabulated_computed_path(s,p)
    assert changed['source_pressure_upper'] > original['source_pressure_upper']
    assert changed['time_and_jump_ell_h_upper'][1] > original['time_and_jump_ell_h_upper'][1]