"""CE1-I: time-local source Jacobian with exact-binary MPFR hulls."""

import numpy as np
import pytest
from scipy.integrate import solve_ivp
from numpy.polynomial.legendre import leggauss

from bianchi.nonperturbative.einstein_error_budget import rk4_path
from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation
from bianchi.nonperturbative.einstein_tabulated_local import (
    _exact_expansion_initial, _local_pressure_caps, certify_local_tabulated_path,
    run_local_tabulated_rk4,
)
from bianchi.nonperturbative.einstein_tabulated_sharp import (
    initial_continuum_pressure_cap,
)


def fixture(refinement=1):
    return TabulatedRadiation([0, .5, 1], [0, .25, .75, 1],
                              [[.1, .25, .05], [.2, .15, .15]],
                              refinement=refinement, backend='python_oracle')


def test_exact_initial_expansion_and_pressure_homothety():
    s = fixture()
    h, theta0 = _exact_expansion_initial(s, (.2, -.13, -.07))
    assert all(x.lower > 0 for x in h)
    assert theta0.lower > 0
    assert sum(x.lower for x in h) <= theta0.upper
    # Exact continuum pressure scaling is P(ell + m*1) = exp(-4*m) P(ell).
    # The stored ray source independently obeys this homothety as well.
    ell = np.array([.05, .04, .08]); m = .06
    p = s.moments(ell)[1]; q = s.moments(ell + m)[1]
    np.testing.assert_allclose(q, np.exp(-4*m)*p, rtol=8e-15, atol=1e-15)


def test_panel_lower_bound_is_positive_after_initial_panel():
    s = fixture()
    p = rk4_path(s, s.initial_state(), .08, 4, backend='python_oracle')
    pmax = initial_continuum_pressure_cap(s)['pressure_max_upper']
    rows = _local_pressure_caps(s,p,(.2,-.13,-.07),pmax)
    m = [x['shared_logscale_lower'] for x in rows]
    L = [x['lipschitz_upper'] for x in rows]
    assert len(rows) == 4 and m[0] == 0.
    assert all(x > 0 for x in m[1:])
    assert all(a < b for a,b in zip(L[1:],L[:-1]))
    assert all(l <= 4*pmax for l in L)
    for j,row in enumerate(rows):
        for t in np.linspace(p.times[j],p.times[j+1],11):
            assert min(p.at(t)[:3]) + 1e-14 >= row['shared_logscale_lower']


def test_local_repropagation_is_strictly_tighter_than_parent():
    s = fixture()
    out = run_local_tabulated_rk4(s, steps=4, backend='python_oracle')
    assert out['status'] == 'SCOPED_CE1I_TIME_LOCAL_PRESSURE_COMPARISON'
    assert out['local_total_ell_h_upper'][1] < out['ce1h_total_ell_h_upper'][1]
    assert out['ce1h_total_ell_h_upper'][1] < out['ce1g_total_ell_h_upper'][1]
    assert out['time_local_lipschitz_upper'][0] == out['initial_pressure_lipschitz_upper']
    assert out['target_met'] is False
    assert len(out['rows']) == 4 and out['production_ready'] is False
    assert out['source_pressure_upper'] > 0


def test_refinement_preserves_local_geometry_minima_and_target():
    a,b = (run_local_tabulated_rk4(fixture(k),steps=4,backend='python_oracle')
           for k in (1,2))
    assert a['time_local_min_logscale_lower'] == b['time_local_min_logscale_lower']
    assert b['local_total_ell_h_upper'][1] < a['local_total_ell_h_upper'][1]
    assert a['fixed_target_h']==b['fixed_target_h']==1e-5
    assert a['rays']==6 and b['rays']==24


def test_mutated_source_cannot_reuse_inherited_unsafe_cache():
    s=fixture()
    p=rk4_path(s,s.initial_state(),.08,2,backend='python_oracle')
    certify_local_tabulated_path(s,p)
    s.mass = s.mass.copy()*64.
    with pytest.raises(ValueError,match='Stale stored-ray'):
        certify_local_tabulated_path(s,p)


def test_hermite_start_identity_is_required_in_child():
    s=fixture()
    p=rk4_path(s,s.initial_state(),.08,2,backend='python_oracle')
    p.coefficients[0,0,3] += .01
    with pytest.raises(ValueError,match='Hermite origins'):
        certify_local_tabulated_path(s,p)


def test_explicit_python_oracle_and_invalid_types():
    s=fixture()
    with pytest.raises(ValueError,match='backend'):
        run_local_tabulated_rk4(s,steps=2)
    with pytest.raises(TypeError):
        certify_local_tabulated_path(object(),object())
    for steps in (0,True,257,1.1):
        with pytest.raises(ValueError):
            run_local_tabulated_rk4(s,steps=steps,backend='python_oracle')


def test_independent_original_cell_ode_does_not_falsify_local_enclosure():
    # Independent GL32 quadrature on ORIGINAL cells, not stored refined rays.
    s=fixture(1)
    out=run_local_tabulated_rk4(s,steps=4,backend='python_oracle')
    p=rk4_path(s,s.initial_state(),.08,4,backend='python_oracle')
    nodes,weights=leggauss(32)
    x_all,w_all=[],[]
    mu=[0,.5,1]; phi=[0,.25,.75,1]
    energy=[[.1,.25,.05],[.2,.15,.15]]
    for i in range(2):
        for j in range(3):
            z=mu[i]+(nodes+1)*(mu[i+1]-mu[i])/2
            ang=np.pi/2*(phi[j]+(nodes+1)*(phi[j+1]-phi[j])/2)
            Z,A=np.meshgrid(z,ang,indexing='ij')
            x_all.append(np.stack(((1-Z*Z)*np.cos(A)**2,
                                   (1-Z*Z)*np.sin(A)**2,Z*Z),-1).reshape(-1,3))
            w_all.append((energy[i][j]*np.outer(weights,weights)/4).ravel())
    x=np.concatenate(x_all);w=np.concatenate(w_all)
    def rhs(t,y):
        ell,h=y[:3],y[3:]
        b=np.exp(-2*ell)
        pressure=np.exp(-sum(ell))*b*np.einsum('q,qi->i',w/np.sqrt(x@b),x)
        return np.r_[h,-sum(h)*h+pressure]
    sol=solve_ivp(rhs,(0,.08),s.initial_state(),method='DOP853',
                  rtol=1e-12,atol=1e-14,dense_output=True)
    assert sol.success
    diff=max(abs(sol.y[3:,-1]-p.states[-1,3:]))
    assert 0 < diff < out['local_total_ell_h_upper'][1]
    for row in out['rows']:
        for t in np.linspace(row['u_left'],row['u_right'],6):
            assert min(sol.sol(t)[:3]) + 1e-12 >= row['shared_logscale_lower']
