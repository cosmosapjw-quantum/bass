"""G1B-only tests. Do not replay G1A's existing campaign or tests."""
import numpy as np
import pytest
from scipy.integrate import quad
import smooth as sm
from vendor import kinetic as kn


def test_stable_occupation_and_infrared_measure():
    q=np.array([1e-12,.1,1.,40.,1000.])
    assert np.all(np.isfinite(sm.radial_density(q,'FD')))
    assert np.all(np.isfinite(sm.radial_density(q,'Planck')))
    assert abs(sm.radial_density(q[:1],'Planck')[0]/q[0]-1)<2e-12
    assert sm.radial_density(np.array([0.]),'Planck')[0]==0
    assert sm.occupation(np.array([1000.]),'FD')[0]==0  # representational underflow
    from vendor import freestream as old
    assert old.f_fermi_dirac(np.array([1000.]))[0]>0 # old finite-node source kept distinct


def test_fixed_continuum_normalization_not_per_grid():
    for kind,m in [('FD',0.),('FD',3.),('FD',30.),('Planck',0.)]:
        z=sm.normalizer(kind,m)
        ref=quad(lambda q:q*q*np.hypot(m,q)*np.exp(-q)/(1+np.exp(-q) if kind=='FD' else -np.expm1(-q)),0,np.inf,epsabs=1e-11,epsrel=2e-13)[0]
        assert abs(z-ref)/ref<5e-13
        q,dq=sm.radial_rule(16)
        assert abs(np.sum(dq*sm.radial_density(q,kind)*np.hypot(m,q))/z-1)<5e-13
    coarse=sm.packets('FD',3.,4,8)
    rho=kn.moments(*coarse)[0]
    assert abs(rho-1)>1e-9 # coarse quadrature error must remain visible


def test_angular_positive_normalized_rule_and_quadrupole():
    n,w=sm.angular_rule(10)
    assert np.all(w>0) and abs(w.sum()-4*np.pi)<1e-13
    np.testing.assert_allclose(np.einsum('q,qa,qb->ab',w,n,n),4*np.pi*np.eye(3)/3,atol=2e-14,rtol=0)
    A=sm.default_anisotropy()
    g=sm.angular_factor(n,A)
    assert min(g)>0 and abs(w@g/(4*np.pi)-1)<2e-14


def test_radial_tails_against_independent_infinite_integrals():
    for kind in ['FD','Planck']:
        for Q in [4.,12.,24.,48.]:
            for p in [2,3]:
                f=lambda q:q**p*np.exp(-q)/(1+np.exp(-q) if kind=='FD' else -np.expm1(-q))
                exact=quad(f,Q,np.inf,epsabs=1e-30,epsrel=2e-12)[0]
                bound=sm.radial_tail(p,Q,kind)
                assert exact<=bound*(1+2e-13)
                assert exact>0 and bound/exact<1.02
    assert sm.energy_tail_bound('FD',3.,48.,np.exp(2.4),np.exp(5.6))<1e-12


def test_massless_number_and_tensor_reduction_after_deformation_boost():
    A=sm.default_anisotropy()
    for kind in ['FD','Planck']:
        full=sm.packets(kind,0.,16,14,A=A)
        reduced=sm.photon_packets(kind,14,A=A)
        for x in [full,reduced]:
            assert np.all(x[1]>0)
        def transform(data):
            k,w,m=data;D=np.diag(np.exp([.3,-.7,.2]))
            k=k@D.T;w=w*np.linalg.det(D)
            n=k/np.linalg.norm(k,axis=1)[:,None];w=w*np.exp(.12*n[:,0]-.08*n[:,1])
            k,w=kn.boost(k,w,m,[.21,-.12,.09])
            e=np.linalg.norm(k,axis=1)
            return kn.tensor(k,w,m), np.r_[w.sum(),np.sum(w[:,None]*k/e[:,None],axis=0)]
        T,N=transform(full);Tr,Nr=transform(reduced)
        assert np.max(np.abs(T-Tr))/T[0,0]<5e-12
        assert np.max(np.abs(N-Nr))/N[0]<5e-12


def test_energy_only_compression_changes_number_and_higher_moments():
    k,w,m=sm.photon_packets('Planck',10)
    e=np.linalg.norm(k,axis=1);rho=np.sum(w*e);N=w.sum()
    wrongN=rho # qrep=1 matches energy only
    assert abs(wrongN/N-1)>1
    I2,I3,I4=sm.radial_moments('Planck')
    # Matched N and energy is NOT a full spectral replacement.
    assert abs(I3*I3/(I2*I4)-1)>.1


def test_massless_flow_homogeneity_new_reduction_contract():
    k=np.array([[.4,-.2,.8],[.7,.6,-.1]])
    s=np.array([[.1,.04,.03],[.04,-.06,-.02],[.03,-.02,-.04]])
    n=np.array([[.4,.02,.01],[.02,-.3,.05],[.01,.05,.8]])
    args=(.6,s,n,np.array([.2,-.1,.05]),np.array([.1,.2,-.3]))
    d,l=kn.flow(k,np.zeros(2),*args)
    for q in [.001,.2,4.,50.]:
        dq,lq=kn.flow(q*k,np.zeros(2),*args)
        np.testing.assert_allclose(dq/q,d,rtol=2e-13,atol=1e-13)
        np.testing.assert_allclose(lq,l,rtol=2e-13,atol=1e-13)


def test_input_guards():
    for call in [lambda:sm.packets('Planck',3.,8,8),lambda:sm.packets('FD',1.,8,8),lambda:sm.radial_rule(0),lambda:sm.angular_rule(3),lambda:sm.packets('FD',3.,8,8,A=np.diag([-2.,1.,1.])),lambda:sm.radial_tail(2,-1,'FD'),lambda:sm.occupation([1+1j],'FD')]:
        with pytest.raises(ValueError):call()
