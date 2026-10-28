"""CE1-B tests: analytic truncation and full-panel residual bounds, not sample certificates."""
import math
import numpy as np
import pytest
from scipy.integrate import solve_ivp
from bianchi.nonperturbative.einstein_error_budget import (
    PolynomialRadiation, HermitePath, rk4_path, audit_path,
    pressure_jets, source_bound_box, residual_panel, propagate,
)

KW={'backend':'python_oracle'}

def test_explicit_backend_and_continuum_positivity():
    with pytest.raises(ValueError): PolynomialRadiation()
    with pytest.raises(ValueError): PolynomialRadiation(coefficients=(3.,0.,0.),**KW)
    with pytest.raises(ValueError): PolynomialRadiation(energy=-1,**KW)
    with pytest.raises(ValueError): PolynomialRadiation(ntheta=3,**KW)
    with pytest.raises(ValueError): PolynomialRadiation(nphi=9,**KW)

def test_initial_pressure_and_raw_mass():
    s=PolynomialRadiation(**KW)
    e,p=s.moments(np.zeros(3))
    assert abs(e-.9)<2e-14
    assert np.max(abs(p-s.initial_pressure))<2e-14
    assert abs(s.weights.sum()-4*np.pi)<2e-14
    assert s.polynomial_degree==4

def test_isotropic_geometry_exact_quadrature_bound():
    s=PolynomialRadiation(ntheta=4,**KW)
    for a in (0.,.3,1.):
        b=source_bound_box(s,np.full(3,a),np.full(3,a))
        assert b['q']==0 and np.max(b['pressure_bound'])==0
        assert np.max(abs(s.moments(np.full(3,a))[1]-s.initial_pressure*np.exp(-4*a)))<2e-14

def test_pressure_quadrature_bound_not_grid_difference():
    coarse=PolynomialRadiation(ntheta=6,**KW)
    fine=PolynomialRadiation(ntheta=48,**KW)
    for ell in ([.4,.1,.2],[.8,.2,.5],[1.,.9,.8]):
        bound=source_bound_box(coarse,np.array(ell),np.array(ell))
        err=abs(coarse.moments(ell)[1]-fine.moments(ell)[1])
        assert np.all(err<=np.array(bound['pressure_bound'])+2e-12)
    assert bound['K']==2

def test_source_box_covers_interior_and_refines():
    lo=np.array([.1,.02,.04]);hi=np.array([.4,.25,.3])
    s=PolynomialRadiation(ntheta=8,**KW);f=PolynomialRadiation(ntheta=40,**KW)
    bound=np.array(source_bound_box(s,lo,hi)['pressure_bound'])
    for ell in np.random.default_rng(351).uniform(lo,hi,(15,3)):
        assert np.all(abs(s.moments(ell)[1]-f.moments(ell)[1])<=bound+2e-12)
    assert max(source_bound_box(PolynomialRadiation(ntheta=16,**KW),lo,hi)['pressure_bound'])<max(bound)
    with pytest.raises(ValueError): source_bound_box(s,hi,lo)

def test_pressure_taylor_coefficients_exact_isotropic_path():
    s=PolynomialRadiation(**KW);c=.7;v=.2
    L=np.array([[v,v,v],[c,c,c],[0,0,0],[0,0,0.]])
    jets=pressure_jets(s,L)
    for k in range(4):
        expected=s.initial_pressure*np.exp(-4*v)*(-4*c)**k/math.factorial(k)
        assert np.max(abs(jets[k]-expected))<3e-13

def test_hermite_reconstructs_knots_and_derivatives():
    s=PolynomialRadiation(**KW);p=rk4_path(s,s.initial_state(),.4,8,**KW)
    for i,t in enumerate(p.times):
        assert np.max(abs(p.at(t)-p.states[i]))<2e-15
        assert np.max(abs(p.at(t,derivative=1)-p.slopes[i]))<2e-13
    with pytest.raises(ValueError):p.at(-.1)
    with pytest.raises(ValueError):p.at(.5)

def test_full_path_admission_not_only_endpoints():
    s=PolynomialRadiation(**KW);y0=s.initial_state();y1=y0.copy();y1[:3]=1.
    d=np.zeros((2,6));d[0,3:]=-20;d[1,3:]=20
    p=HermitePath(np.array([0.,1.]),np.array([y0,y1]),d)
    assert np.min(p.states[:,3:])>0
    assert np.min(p.at(.5)[3:])<0
    with pytest.raises(ValueError,match='Whole Hermite path'):
        audit_path(s,p)

def test_full_panel_residual_bound_covers_heldout_times():
    s=PolynomialRadiation(ntheta=8,**KW);p=rk4_path(s,s.initial_state(),.5,8,**KW)
    for i in (0,3,7):
        b=residual_panel(s,p,i,subcells=5)
        for t in np.linspace(p.times[i],p.times[i+1],31):
            r=p.at(t,derivative=1)-s.rhs(t,p.at(t))
            assert max(abs(r[:3]))<=b['ell_defect']+2e-12
            assert max(abs(r[3:]))<=b['h_defect']+2e-12
        assert b['remainder_method']=='analytic_fourth_derivative_not_sample_max'

def test_total_budget_covers_reference_and_splits():
    s=PolynomialRadiation(ntheta=10,**KW);y=s.initial_state()
    p=rk4_path(s,y,.5,16,**KW);a=audit_path(s,p,subcells=4)
    fine=PolynomialRadiation(ntheta=36,**KW)
    r=solve_ivp(fine.rhs,(0,.5),y,rtol=2e-12,atol=2e-14,dense_output=True,method='DOP853')
    diff=abs(p.at(.5)-r.sol(.5))
    assert max(diff[:3])<=a['final_total'][0]+2e-10
    assert max(diff[3:])<=a['final_total'][1]+2e-10
    assert np.max(abs(np.array(a['final_total'])-np.array(a['final_source'])-np.array(a['final_time'])))<2e-14
    assert a['floating_point_certificate'] is False

def test_residual_envelope_decreases_with_time_refinement():
    s=PolynomialRadiation(ntheta=16,**KW)
    a=audit_path(s,rk4_path(s,s.initial_state(),.4,8,**KW))
    b=audit_path(s,rk4_path(s,s.initial_state(),.4,16,**KW))
    assert b['final_time'][1]<a['final_time'][1]/4

def test_comparison_propagation_and_zero_energy_limit():
    assert np.allclose(propagate([0.,0.],1.,0.,.2,.3),[.35,.3],rtol=0,atol=2e-15)
    a=propagate([0.,0.],.3,.9,.02,.01)
    b=propagate(propagate([0.,0.],.15,.9,.02,.01),.15,.9,.02,.01)
    assert np.max(abs(a-b))<2e-15

def test_invalid_admission_no_clipping_or_constraint_projection():
    s=PolynomialRadiation(**KW);y=s.initial_state();original=y.copy()
    with pytest.raises(ValueError):rk4_path(s,y,1,0,**KW)
    with pytest.raises(ValueError):rk4_path(s,y,1,8)
    bad=y.copy();bad[3]+=.1
    with pytest.raises(ValueError):rk4_path(s,bad,1,8,**KW)
    assert np.array_equal(y,original)

def test_polynomial_quadrature_degree_and_zeros_do_not_certify_absent_tail():
    s=PolynomialRadiation(ntheta=4,**KW)
    assert s.K==0
    assert source_bound_box(s,np.array([.5,.1,.2]),np.array([.5,.1,.2]))['pressure_bound'][0]>0
    # P4 vanishes at polar GL4 nodes, but the known polynomial still has degree4.
    assert max(abs((35*s.n[:,2]**4-30*s.n[:,2]**2+3)/8))<1e-14
    assert s.polynomial_degree==4
