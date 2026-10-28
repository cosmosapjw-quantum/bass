"""CE1-A: new coupled-channel tests. No historical science campaigns."""
import numpy as np
import pytest
from bianchi.nonperturbative._core.polarized_dictionary import Grid
from bianchi.nonperturbative.einstein_vlasov import (
    AngularRadiation, CoupledHistory, DirectHistory, initial_state,
    constraint, source_error_bound
)

def radiation(n=8, amplitude=0.0):
    g=Grid(n,2*n)
    z=g.n[:,2]
    p4=(35*z**4-30*z*z+3)/8
    intensity=(1+amplitude*p4)/(4*np.pi)
    return g,AngularRadiation(g.n,g.w,intensity)

def test_initial_constraints_and_reflection():
    _,r=radiation(amplitude=.7)
    y=initial_state(r,[.16,-.04,-.12])
    assert abs(constraint(y,r.moments(y[:3])[0]))<2e-13
    E,P,q,T=r.tensor(np.array([.12,.22,.07]))
    assert np.max(abs(q))<2e-13
    assert np.max(abs(T-np.diag(P)))<2e-13
    assert abs(P.sum()-E)<2e-13

def test_moment_jacobian_and_energy_identity():
    _,r=radiation(amplitude=.7)
    ell=np.array([.1,.2,.3]);h=np.array([.6,.5,.4])
    E,P=r.moments(ell);de,dp=r.jacobian(ell)
    fd=np.column_stack([(r.moments(ell+1e-6*np.eye(3)[j])[1]-
                        r.moments(ell-1e-6*np.eye(3)[j])[1])/2e-6 for j in range(3)])
    assert np.max(abs(dp-fd))<3e-7
    assert np.max(abs(de+E+P))<2e-13
    assert np.max(abs(np.abs(dp).sum(axis=1)-4*P))<2e-13
    assert abs(de@h+h.sum()*E+h@P)<2e-13

def test_isotropic_radiation_exact_solution():
    _,r=radiation();y0=initial_state(r,[0,0,0])
    sol=CoupledHistory(r,y0,.4,backend='python_oracle')
    h0=y0[3]
    for u in [.1,.4]:
        y=sol.at(u);fac=1+2*h0*u
        assert np.max(abs(y[:3]-.5*np.log(fac)))<3e-9
        assert np.max(abs(y[3:]-h0/fac))<3e-9
        assert abs(r.moments(y[:3])[0]-1/fac**2)<3e-9

def test_kasner_vacuum_exact_solution():
    g=Grid(4,8);r=AngularRadiation(g.n,g.w,np.zeros(len(g.w)))
    p=np.array([-1,2,2])/3
    sol=CoupledHistory(r,np.r_[np.zeros(3),p],.3,backend='python_oracle')
    y=sol.at(.3)
    assert np.max(abs(y[:3]-p*np.log(1.3)))<3e-9
    assert np.max(abs(y[3:]-p/1.3))<3e-9

def test_p8_coupled_direct_matches_reduced():
    _,r=radiation(6,.5);y0=initial_state(r,[.16,-.04,-.12])
    a=CoupledHistory(r,y0,.3,backend='python_oracle')
    b=DirectHistory(r,y0,.3,backend='python_oracle')
    z=b.at(.3)
    assert np.max(abs(a.at(.3)-z['state']))<3e-9
    E,P=r.moments(a.at(.3)[:3])
    assert abs(z['energy']-E)<3e-9
    assert np.max(abs(z['pressure']-P))<3e-9
    assert abs(z['constraint'])<3e-9

def test_direct_does_not_call_reduced_source(monkeypatch):
    _,r=radiation(4,.2);y0=initial_state(r,[.08,-.02,-.06])
    def forbidden(*args,**kwargs):
        raise AssertionError('reduced source must not be called')
    monkeypatch.setattr(r,'moments',forbidden)
    out=DirectHistory(r,y0,.05,backend='python_oracle').at(.05)
    assert np.isfinite(out['energy'])

def test_constraint_propagates_without_projection():
    _,r=radiation(6,.6);y0=initial_state(r,[.1,.02,-.12])
    y0[3]+=.002
    c0=constraint(y0,r.moments(y0[:3])[0])
    s=CoupledHistory(r,y0,.25,backend='python_oracle',allow_constraint_defect=True)
    y=s.at(.25);c=constraint(y,r.moments(y[:3])[0])
    assert abs(c*np.exp(2*y[:3].sum())-c0)<3e-9
    assert abs(c)>1e-5

def test_source_error_bound_for_two_positive_distributions():
    g,a=radiation(8,0.0);_,b=radiation(8,.1)
    y0=initial_state(a,[.16,-.04,-.12])
    sa=CoupledHistory(a,y0,.3,backend='python_oracle')
    sb=CoupledHistory(b,y0,.3,backend='python_oracle')
    tv=np.sum(abs(a.energy_weights-b.energy_weights))
    B=max(np.max(y0[3:]),np.sqrt(max(a.energy0,b.energy0)))
    assert np.max(abs(sa.at(.3)-sb.at(.3)))<=source_error_bound(.3,tv,1.,B)
    assert source_error_bound(0.,tv,1.,B)==0

def test_full_l4_tail_not_replaced_by_initial_stress():
    _,a=radiation(8,0);_,b=radiation(8,.6)
    assert np.max(abs(a.moments(np.zeros(3))[1]-b.moments(np.zeros(3))[1]))<2e-13
    y0=initial_state(a,[.16,-.04,-.12])
    aa=CoupledHistory(a,y0,.4,backend='python_oracle').at(.4)
    bb=CoupledHistory(b,y0,.4,backend='python_oracle').at(.4)
    assert np.max(abs(aa-bb))>1e-5

def test_invalid_and_asymmetric_input_rejected():
    g=Grid(4,8);I=np.ones(len(g.w))
    with pytest.raises(ValueError): AngularRadiation(g.n,g.w,-I)
    with pytest.raises(ValueError): AngularRadiation(g.n,g.w,I+.2*g.n[:,0])
    with pytest.raises(ValueError): AngularRadiation(g.n*1.01,g.w,I)
    with pytest.raises(ValueError): AngularRadiation(g.n,-g.w,I)
    r=AngularRadiation(g.n,g.w,I)
    with pytest.raises(ValueError): initial_state(r,[.1,.1,.1])

def test_explicit_backend_and_no_input_mutation():
    _,r=radiation(4,.1);y=initial_state(r,[0,0,0]);copy=y.copy()
    with pytest.raises(ValueError): CoupledHistory(r,y,.1)
    with pytest.raises(ValueError): DirectHistory(r,y,.1)
    CoupledHistory(r,y,.1,backend='python_oracle')
    assert np.array_equal(y,copy)

def test_prefix_and_out_of_domain_rejection():
    _,r=radiation(4,.2);y=initial_state(r,[.08,-.02,-.06])
    a=CoupledHistory(r,y,.1,backend='python_oracle')
    b=CoupledHistory(r,y,.2,backend='python_oracle')
    assert np.max(abs(a.at(.08)-b.at(.08)))<3e-9
    with pytest.raises(ValueError): a.at(-.01)
    with pytest.raises(ValueError): a.at(.2)

def test_initial_constraint_violation_rejected():
    _,r=radiation(4)
    with pytest.raises(ValueError):
        CoupledHistory(r,np.zeros(6),.1,backend='python_oracle')

def test_anisotropic_pressure_is_not_perfect_fluid():
    g=Grid(8,16);z=g.n[:,2]
    r=AngularRadiation(g.n,g.w,(1+.8*(3*z*z-1)/2)/(4*np.pi))
    E,P=r.moments(np.zeros(3))
    assert np.max(abs(P-E/3))>.05

def test_dissipative_comparison_envelope():
    from bianchi.nonperturbative.einstein_vlasov import source_error_envelope
    _,a=radiation(8,0);_,b=radiation(8,.1)
    y=initial_state(a,[.16,-.04,-.12])
    aa=CoupledHistory(a,y,.3,backend='python_oracle').at(.3)
    bb=CoupledHistory(b,y,.3,backend='python_oracle').at(.3)
    tv=np.sum(abs(a.energy_weights-b.energy_weights))
    bound=source_error_envelope(.3,tv,1.)
    assert np.max(abs(aa[:3]-bb[:3]))<=bound[0]
    assert np.max(abs(aa[3:]-bb[3:]))<=bound[1]
    assert max(bound)<source_error_bound(.3,tv,1.,1.)
    assert np.max(abs(source_error_envelope(.3,.2,0)-[.009,.06]))<1e-14
