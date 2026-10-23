import numpy as np
import pytest
from scipy.linalg import expm
from vendor import core as bg
import kinetic as kn

GATE=5e-12

def sample(seed=4,n=23):
    r=np.random.default_rng(seed);k=r.normal(size=(n,3));w=np.exp(r.normal(size=n));m=r.choice([0.,.3,3.],size=n)
    return k,w,m

def geometry(seed=6):
    r=np.random.default_rng(seed);s=r.normal(size=(3,3));s=(s+s.T)/12;s-=np.eye(3)*np.trace(s)/3
    n=r.normal(size=(3,3));n=(n+n.T)/3;a=r.normal(size=3)/8;rot=r.normal(size=3)/9
    return .6,s,n,a,rot

def scaled(a,b):return np.max(np.abs(a-b)/(1+np.maximum(np.abs(a),np.abs(b))))

def koszul(k,m,h,s,n,a,rot):
    eye=np.eye(3);C=np.zeros((3,3,3))
    for z in range(3):
        for i in range(3):
            for j in range(3):C[z,i,j]=np.cross(eye[i],eye[j])@n[:,z]+a[i]*eye[z,j]-a[j]*eye[z,i]
    con=np.empty_like(C)
    for z in range(3):
        for i in range(3):
            for j in range(3):con[z,i,j]=(C[z,i,j]-C[i,j,z]+C[j,z,i])/2
    e=np.sqrt(m*m+np.sum(k*k,axis=1))
    return -h*k-k@s.T+np.cross(rot,k)-np.einsum('zij,qi,qj->qz',con,k,k)/e[:,None]

def test_koszul_characteristic():
    for seed in range(8):
        k,w,m=sample(seed);h,s,n,a,rot=geometry(seed)
        dk,dlw=kn.flow(k,m,h,s,n,a,rot)
        assert scaled(dk,koszul(k,m,h,s,n,a,rot))<GATE
        e=np.sqrt(m*m+np.sum(k*k,axis=1))
        assert scaled(dlw,-3*h+2*(k@a)/e)<GATE

def test_moment_conservation():
    for seed in range(16):
        k,w,m=sample(seed);h,s,n,a,rot=geometry(seed)
        rho,f,p,pi=kn.moments(k,w,m)
        dk,dlw=kn.flow(k,m,h,s,n,a,rot);e=np.sqrt(m*m+np.sum(k*k,axis=1));de=np.sum(k*dk,axis=1)/e
        drho=np.sum(w*(dlw*e+de));df=np.sum(w[:,None]*(dlw[:,None]*k+dk),axis=0)
        wanted_r=-3*h*(rho+p)+2*a@f-np.sum(s*pi)
        wanted_f=-4*h*f-s@f+3*pi@a+bg.epsilon_product(n,pi)+np.cross(rot,f)
        assert scaled(drho,wanted_r)<GATE
        assert scaled(df,wanted_f)<GATE

def test_class_b_weight_mutation_detected():
    k=np.array([[1.,.2,-.3]]);w=np.array([.7]);m=np.array([2.]);h,s,n,a,rot=geometry()
    dk,rate=kn.flow(k,m,h,s,n,a,rot);rho,f,p,pi=kn.moments(k,w,m);e=np.sqrt(m*m+np.sum(k*k,axis=1))
    wrong=np.sum(w*(-3*h*e+np.sum(k*dk,axis=1)/e))
    correct=-3*h*(rho+p)+2*a@f-np.sum(s*pi)
    assert abs(wrong-correct)>1e-3
    assert abs((wrong-correct)+2*a@f)<1e-12

def test_lorentz_tensor_and_inverse():
    for speed in [0.,1e-8,.3,.8]:
        k,w,m=sample();beta=speed*np.array([2.,-1.,2.])/3
        kb,wb=kn.boost(k,w,m,beta);B=kn.boost_matrix(beta)
        assert scaled(kn.tensor(kb,wb,m),B@kn.tensor(k,w,m)@B.T)<2e-12
        kr,wr=kn.boost(kb,wb,m,-beta)
        assert scaled(kr,k)<2e-12 and scaled(wr,w)<2e-12
        if speed>.1:assert scaled(kn.tensor(kb,w,m),B@kn.tensor(k,w,m)@B.T)>1e-3

def test_rotation_covariance():
    k,w,m=sample();h,s,n,a,rot=geometry();O=expm(bg.cross(np.array([.3,-.1,.2])))
    d,l=kn.flow(k,m,h,s,n,a,rot);d2,l2=kn.flow(k@O.T,m,h,O@s@O.T,O@n@O.T,O@a,O@rot)
    assert scaled(d2,d@O.T)<GATE and scaled(l2,l)<GATE

def test_h_zero_and_contraction():
    k,w,m=sample();h,s,n,a,rot=geometry()
    for h in [-.7,0.,.7]:assert all(np.all(np.isfinite(x)) for x in kn.flow(k,m,h,s,n,a,rot))

def test_invalid_packets():
    k,w,m=sample()
    for bad in [np.full_like(w,-1.),np.full_like(w,np.nan)]:
        with pytest.raises(ValueError):kn.moments(k,bad,m)
    with pytest.raises(ValueError):kn.moments(np.zeros((1,3)),np.ones(1),np.zeros(1))
    with pytest.raises(ValueError):kn.boost(k,w,m,np.array([1.,0.,0.]))
    with pytest.raises(ValueError):kn.moments(k,w,-np.ones_like(m))

def test_same_node_donor_mapping():
    from vendor import freestream as fs
    for mass in [0.,3.,30.]:
        for alpha,beta in [(0.,np.zeros(3)),(.4,np.array([.17,-.05,-.12]))]:
            k,w,m=kn.fd_packets(fs,mass,alpha,beta)
            rho,f,p,pi=kn.moments(k,w,m)
            r0,p0,pi0=fs.moments(np.exp(alpha+beta),mass)
            norm=4*np.pi*np.sum(fs._DQ*fs._Q**2*fs.f_fermi_dirac(fs._Q)*np.hypot(mass,fs._Q))
            assert scaled(rho,r0/norm)<2e-12
            assert scaled(p,p0/norm)<2e-12
            assert scaled(pi,pi0/norm)<2e-12
            assert np.linalg.norm(f)<2e-12


def test_fd_owner_domain_guard():
    from vendor import freestream as fs
    for args in [(1.,0.,[0.,0.,0.]),(3.,-1.,[0.,0.,0.]),(3.,0.,[1.2,-.6,-.6])]:
        with pytest.raises(ValueError):kn.fd_packets(fs,*args)
    with pytest.raises(ValueError):kn.fd_packets(fs,3.,C=.5)
