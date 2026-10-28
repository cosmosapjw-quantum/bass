"""BF3-E independent source-memory tests on the actual package namespace."""
import numpy as np
import pytest
from scipy.linalg import expm
from scipy.integrate import quad_vec
from bianchi.nonperturbative.lapse_field import (
    FieldGrid, LapseField, PeriodicLapse, smooth_initial, stationary, from_stokes,
)
from bianchi.nonperturbative.lapse_memory import LapseMemory, exponential_weights


def setup(nx=9,nmu=6,eps=.35,nu=1.1):
    g=FieldGrid(nx,nmu,8); met=PeriodicLapse(eps)
    y=smooth_initial(g.x[:,None,None],g.mu[None,:,None],g.phi[None,None,:])
    op=LapseMemory(g,met,nu,backend='python_oracle')
    return g,met,y,op


def test_explicit_backend_and_invalid_parameters():
    g=FieldGrid(5,4,8)
    with pytest.raises(ValueError):LapseMemory(g,PeriodicLapse(.2),1.)
    with pytest.raises(ValueError):LapseMemory(g,PeriodicLapse(.2),-1.,backend='python_oracle')
    op=LapseMemory(g,PeriodicLapse(.2),1.,backend='python_oracle')
    for t,p in [(-1,4),(.1,0),(.1,True),(.1,1.5)]:
        with pytest.raises(ValueError):op.solve(stationary(g),t,p)
    with pytest.raises(ValueError):op.solve(stationary(g).astype(complex),.1,4)


def test_stream_loss_gain_matches_parent_rhs_without_using_it_in_solver():
    g,met,y,op=setup(); ref=LapseField(g,met,1.1,backend='python_oracle')
    rhs=op.apply_phase(op.A,y)+op.inject(op.scaled_source(y))
    assert np.max(abs(rhs-ref.rhs(0,y)))<2e-11
    assert np.max(abs(op.source(y)-ref.source(y)))<2e-11


def test_kernel_equals_explicit_stream_gain_projection():
    g,met,y,op=setup(5,4)
    rng=np.random.default_rng(20261028);M=rng.normal(size=(g.nx,3,3))
    for tau in (0.,.13):
        direct=op.source(op.apply_phase(expm(tau*op.A),op.inject(M*op.N[:,None,None]**4)))
        actual=(op.kernel(tau)@M.ravel()).reshape(g.nx,3,3)
        assert np.max(abs(direct-actual))<2e-11


def test_exact_polynomial_exponential_weights_including_singular_A():
    A=np.array([[0.,.3],[0.,-.7]]);h=.2;r=.63
    U,W=exponential_weights(A,h,r)
    L=[lambda v:1-3*v+2*v*v,lambda v:4*v-4*v*v,lambda v:2*v*v-v]
    for j in range(3):
        target=quad_vec(lambda v:h*expm(h*A*(r-v))*L[j](v),0,r,epsabs=1e-13)[0]
        assert np.max(abs(W[j]-target))<2e-12
    assert np.max(abs(U-expm(A*h*r)))<2e-12


def test_stationary_and_exact_vacuum():
    g,met,y,op=setup(nu=lambda x:1+.2*np.sin(x))
    z=stationary(g);a=op.solve(z,.2,4);v=op.solve(z*0,.2,4)
    assert np.max(abs(a.at(.2)-z))<4e-10
    assert np.max(abs(v.at(.2)))==0


def test_constant_lapse_polarized_clock():
    g=FieldGrid(5,6,8);met=PeriodicLapse(0.)
    # A constant nonunit lapse is a separate coefficient provider.
    class Constant:
        cbar=1.
        def N(self,x):return np.ones_like(x)*np.exp(.4)
        def dN(self,x):return np.zeros_like(x)
    met=Constant();nu=.7;I=2+.3*(3*g.mu**2-1)/2
    y=np.broadcast_to(from_stokes(I[None,:,None],0,0,0),g.shape).copy()
    op=LapseMemory(g,met,nu,backend='python_oracle');ref=LapseField(g,met,nu,backend='python_oracle')
    actual=op.solve(y,.4,32).at(.4);exact=ref.collision(y,.4)
    assert np.max(abs(actual-exact))<3e-8
    wrong=LapseField(g,met,nu/np.exp(.4),backend='python_oracle').collision(y,.4)
    assert np.max(abs(actual-wrong))>1e-3


def test_independence_from_radiation_rhs_and_history(monkeypatch):
    g,met,y,op=setup(5,4)
    def forbidden(*a,**k):raise AssertionError('radiation oracle was called')
    for name in ('rhs','direct','split','gain','collision_rhs'):
        monkeypatch.setattr(LapseField,name,forbidden)
    out=op.solve(y,.1,4).at(.1)
    assert np.isfinite(out).all()


def test_temporal_refinement_against_direct():
    g,met,y,op=setup(7,6);ref=LapseField(g,met,1.1,backend='python_oracle').direct(y,.3,rtol=3e-13,atol=3e-15).at(.3)
    errors=[]
    for n in (4,8,16):errors.append(np.max(abs(op.source(op.solve(y,.3,n).at(.3))-op.source(ref))))
    assert min(np.log2(np.array(errors[:-1])/errors[1:]))>3.3
    assert errors[-1]<3e-8


def test_global_retarded_reconstruction_and_offgrid():
    g,met,y,op=setup(5,4);h=op.solve(y,.2,4)
    for t in (.073,.2):
        assert np.max(abs(h.global_reconstruction(t)-h.at(t)))<2e-11
        assert np.max(abs(h.initial(t)+h.gain_history(t)-h.at(t)))<2e-11
    with pytest.raises(ValueError):h.at(.21)


def test_causal_prefix_and_input_unchanged():
    g,met,y,op=setup(5,4);saved=y.copy()
    a=op.solve(y,.2,4);b=op.solve(y,.3,6)
    assert np.max(abs(a.at(.2)-b.at(.2)))<2e-11
    assert np.array_equal(saved,y)


def test_source_null_initial_tail_returns():
    g,met,y,op=setup(7,6)
    P4=(35*g.mu**4-30*g.mu**2+3)/8
    tail=np.broadcast_to(from_stokes(.1*np.cos(g.x)[:,None,None]*P4[None,:,None],0,0,0),g.shape).copy()
    assert np.max(abs(op.source(tail)))<2e-11
    h=op.solve(tail,.25,12,signed=True)
    assert np.max(abs(h.moment(.25)))>1e-5
    assert np.max(abs(h.initial(.25)))>1e-3


def test_retarded_kernel_nonlocal_and_no_jacobian_renormalization():
    g,met,y,op=setup(7,6)
    K0=op.kernel(0).reshape(g.nx,9,g.nx,9)
    K1=op.kernel(.13).reshape(g.nx,9,g.nx,9)
    mask=~np.eye(g.nx,dtype=bool)
    assert np.max(abs(K0.transpose(0,2,1,3)[mask]))<2e-11
    assert np.max(abs(K1.transpose(0,2,1,3)[mask]))>1e-4
    assert np.array_equal(op.grid.w,g.w)


def test_zero_scattering_is_exact_semidiscrete_free_flow():
    g,met,y,op=setup(7,6,nu=0.)
    out=op.solve(y,.2,4).at(.2)
    assert np.max(abs(out-op.apply_phase(expm(.2*op.A),y)))<2e-11
