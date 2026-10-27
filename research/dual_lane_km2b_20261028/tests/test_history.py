"""Bounded KM2B acceptance; no historical campaign is invoked."""
import sys
from pathlib import Path
import numpy as np
import pytest
from scipy.integrate import quad
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'code'),str(R/'vendor')]
from tilted_collision import TiltedThomson,boost_map
import polarized_dictionary as PD
import polarization as P8
from tilted_history import TiltedDirect,TiltedVolterra,exponential_weights,conserved,stationary_carrier


def fixture(beta=(.3,-.4,.2),n=6,tail=False):
    g=PD.Grid(n,2*n)
    B,nlab,invD=boost_map(g.n,-np.asarray(beta,float))
    coeff={('I',0,0):2*np.sqrt(4*np.pi),('I',1,1):.12,
           ('I',2,-1):.08,('E',2,0):.09,('B',3,1):.06,('V',1,-1):.07}
    if tail:coeff={('I',3,0):.1}
    Je=PD.synthesize(g,coeff)
    J=invD[:,None,None]**4*np.einsum('nik,nkl,njl->nij',B,Je,B)
    op=TiltedThomson(nlab,g.w/invD**2,beta)
    return op,J,g


def test_exponential_weights_are_integrals():
    z=np.array([0.,1e-12,1e-5,.7,3.,100.])
    poly=[lambda x:1-3*x+2*x*x,lambda x:4*x-4*x*x,lambda x:-x+2*x*x]
    for r in [.173,.5,1.]:
        W=exponential_weights(z,r)
        assert W.shape==(len(z),3)
        for i,zz in enumerate(z):
            for j in range(3):
                expected=quad(lambda x:zz*np.exp(-zz*(r-x))*poly[j](x),0,r,epsabs=1e-13)[0]
                assert abs(W[i,j]-expected)<3e-13
        assert np.max(abs(W.sum(axis=1)+np.expm1(-z*r)))<2e-14


def test_rest_frame_exact_semigroup():
    op,J,g=fixture((0,0,0)); nu=1.3; T=.6
    v=TiltedVolterra(op,J,nu,T,64)
    expected=P8.collide(g.n,g.w,J,nu*T)
    assert np.max(abs(v.carrier(T)-expected))<3e-9


def test_vacuum_exact_and_no_extrapolation():
    op,J,_=fixture();v=TiltedVolterra(op,J,0.,.7,4)
    for t in [0.,.13,.7]:assert np.array_equal(v.carrier(t),J)
    for t in [-1e-5,.7001,np.nan]:
        with pytest.raises(ValueError):v.carrier(t)
    with pytest.raises(ValueError):TiltedVolterra(op,J,-1,.7,4)
    with pytest.raises(ValueError):TiltedVolterra(op,J,1,.7,0)


def test_boosted_equilibrium_is_stationary():
    op,J,_=fixture((.6,0,0));eq=stationary_carrier(op,J)
    v=TiltedVolterra(op,eq,1.1,1.,16)
    assert np.max(abs(v.carrier(1)-eq))/np.max(abs(eq))<2e-11


def test_independent_volterra_never_calls_direct(monkeypatch):
    op,J,_=fixture()
    def forbidden(*a,**k):raise AssertionError('direct source or normal RHS was used')
    monkeypatch.setattr(TiltedDirect,'__init__',forbidden)
    monkeypatch.setattr(op,'rhs',forbidden)
    v=TiltedVolterra(op,J,1.3,.6,12)
    assert np.isfinite(v.moment(.6)).all()


def test_temporal_refinement_and_invariant():
    op,J,_=fixture();T=.8;d=TiltedDirect(op,J,1.3,T)
    v1=TiltedVolterra(op,J,1.3,T,8);v2=TiltedVolterra(op,J,1.3,T,16)
    e1=np.max(abs(v1.moment(T)-d.moment(T)));e2=np.max(abs(v2.moment(T)-d.moment(T)))
    assert e1>10*e2 and e2<3e-8
    v3=TiltedVolterra(op,J,1.3,T,64)
    I0=conserved(op,J)
    assert max(abs(conserved(op,v3.carrier(t))-I0)/abs(I0) for t in np.linspace(0,T,7))<3e-9


def test_initial_gain_null_tail_is_kept():
    op,J,_=fixture((0,0,.6),8,True)
    assert np.linalg.norm(op.source(J))<2e-12
    d=TiltedDirect(op,J,1.3,.7);v=TiltedVolterra(op,J,1.3,.7,64)
    assert np.linalg.norm(d.moment(.7))>1e-3
    assert np.max(abs(v.moment(.7)-d.moment(.7)))<3e-9
    empty=TiltedVolterra(op,np.zeros_like(J),1.3,.7,8)
    assert np.array_equal(empty.moment(.7),np.zeros((3,3)))


def test_causal_identical_prefix():
    op,J,_=fixture()
    a=TiltedVolterra(op,J,1.3,.4,8);b=TiltedVolterra(op,J,1.3,.8,16)
    assert np.array_equal(a.carrier(.4),b.carrier(.4))


def test_full_history_sum_matches_recurrence():
    op,J,_=fixture();v=TiltedVolterra(op,J,1.3,.6,8)
    assert np.max(abs(v.history_integral(.6)-v.moment(.6)))<2e-11


def test_dense_screen_exponential_reference():
    from dense_reference import DenseScreenExponential
    op,J,_=fixture((.6,0,0),4)
    dense=DenseScreenExponential(op,J,1.3)
    d=TiltedDirect(op,J,1.3,.7);v=TiltedVolterra(op,J,1.3,.7,64)
    scale=max(1.,np.max(abs(J)))
    assert np.max(abs(dense.carrier(.7)-d.carrier(.7)))/scale<3e-10
    assert np.max(abs(dense.carrier(.7)-v.carrier(.7)))/scale<3e-9
    assert dense.weighted_symmetry_residual<2e-11


def test_screen_positivity_for_bounded_fixture():
    op,J,_=fixture((.6,0,0),8);v=TiltedVolterra(op,J,1.3,1.,64)
    from covariant_oracle import screen
    E=screen(op.n)
    for t in [0.,.2,.7,1.]:
        H=PD.hermitian(v.carrier(t));X=np.einsum('nia,nij,njb->nab',E,H,E)
        assert np.linalg.eigvalsh(X).min()>0


def test_malformed_carrier_rejected():
    op,J,_=fixture()
    with pytest.raises(ValueError):TiltedVolterra(op,np.ones_like(J),1.,1.,4)
    with pytest.raises(ValueError):TiltedDirect(op,J,1.,np.inf)
