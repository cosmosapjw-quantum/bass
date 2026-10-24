"""One prescribed photon cohort: normalized birth-label angular integrals.

No IVP, source transaction, event rate, or REC angular inventory is used.
"""
import math
import numpy as np
from numpy.polynomial.legendre import leggauss
import finite_exchange as fx
from vendor import core, kinetic

EPS=np.finfo(np.float64).eps
ROUND=512*EPS
RESOLUTION=4096*EPS
A=.4
B=np.diag([.3,-.1,-.2])
ETAS=[0.,1/128,1/64,1/32,1/16,1/4,1.]
SOURCES={'ANISO':B/2,'ISO':np.zeros((3,3))}
O=np.array([[.6,-.8,0],[.8,.6,0],[0,0,1.]])
CARD=fx.owner.CARDS['H_LYA_EFFECTIVE_2P']
SCALE=core.FixedScale(1.)
NB=1.
D=math.exp(-3*A)
PSTAR=CARD.energy_J/core.C_SI
RHOSTAR=SCALE.density_factor*CARD.energy_J*NB*D*math.exp(-A)

def real_matrix(value,name):
    if np.iscomplexobj(value):raise ValueError(name+' must be real')
    out=np.asarray(value,dtype=np.float64)
    if out.shape!=(3,3) or not np.all(np.isfinite(out)):raise ValueError(name+' must be finite 3x3')
    if np.max(np.abs(out-out.T))>ROUND*max(1.,float(np.max(np.abs(out)))):raise ValueError(name+' must be symmetric')
    return out

def validate(S,C):
    S=real_matrix(S,'S');C=real_matrix(C,'C')
    if abs(np.trace(S))>ROUND*max(1.,float(np.max(np.abs(S)))):raise ValueError('S must be STF')
    if 1+np.linalg.eigvalsh(S)[0]<=0:raise ValueError('q must be strictly positive on the sphere')
    if np.linalg.eigvalsh(C)[0]<=0:raise ValueError('transport eigenvalues must be positive')
    return S,C

def transport(eta):
    if not np.isreal(eta) or not np.isfinite(eta) or not 0<=eta<=1:raise ValueError('eta outside frozen [0,1]')
    return np.diag(np.exp(-eta*np.diag(B)))

def rule26():
    n=[];w=[]
    for i in range(3):
        for s in [-1.,1.]:
            v=np.zeros(3);v[i]=s;n.append(v);w.append(1/21)
    for i,j in [(0,1),(0,2),(1,2)]:
        for s in [-1.,1.]:
            for t in [-1.,1.]:
                v=np.zeros(3);v[i]=s/math.sqrt(2);v[j]=t/math.sqrt(2);n.append(v);w.append(4/105)
    for x in [-1.,1.]:
        for y in [-1.,1.]:
            for z in [-1.,1.]:n.append(np.array([x,y,z])/math.sqrt(3));w.append(9/280)
    return np.array(n),np.array(w)

def rule(name):
    if name=='Q14':return fx.cubature14()
    if name=='Q26':return rule26()
    raise ValueError(name)

def sphere_rule(nmu):
    mu,wm=leggauss(nmu);phi=np.arange(2*nmu)*(2*math.pi/(2*nmu))
    mm,pp=np.meshgrid(mu,phi,indexing='ij');rr=np.sqrt(1-mm*mm)
    n=np.stack((rr*np.cos(pp),rr*np.sin(pp),mm),axis=-1).reshape(-1,3)
    w=np.broadcast_to(wm[:,None]/(4*nmu),(nmu,2*nmu)).ravel().copy()
    return n,w

def moments(S,C,n,w):
    S,C=validate(S,C)
    q=1+np.einsum('ni,ij,nj->n',n,S,n)
    v=n@C.T;e=np.linalg.norm(v,axis=1);measure=w*q
    F=float(np.sum(measure*e));P=np.einsum('n,ni,nj->ij',measure/e,v,v)
    flux=np.einsum('n,ni->i',measure,v)
    pi=P-np.eye(3)*(F/3)
    T=np.zeros((4,4));T[0,0]=F;T[0,1:]=flux;T[1:,0]=flux;T[1:,1:]=P
    return dict(F=F,P=P.tolist(),pi=pi.tolist(),flux=flux.tolist(),T=T.tolist())

def octant_reference(S,C,n=32):
    # Only diagonal inputs admit the eight identical reflected octants.
    S,C=validate(S,C)
    if np.any(S-np.diag(np.diag(S))) or np.any(C-np.diag(np.diag(C))):raise ValueError('octant reference requires diagonal S,C')
    x,w=leggauss(n);mu=(x+1)/2;phi=(x+1)*math.pi/4
    mm,pp=np.meshgrid(mu,phi,indexing='ij');rr=np.sqrt(1-mm*mm)
    base=np.stack((rr*np.cos(pp),rr*np.sin(pp),mm),axis=-1).reshape(-1,3)
    weights=np.outer(w,w).ravel()/4
    signs=np.array([[x,y,z] for x in [-1,1] for y in [-1,1] for z in [-1,1]])
    return moments(S,C,(base[:,None,:]*signs).reshape(-1,3),np.repeat(weights/8,8))

def errors(X,Y):
    den=Y['F']
    out={'energy':abs(X['F']-Y['F'])/den}
    for field,label in [('P','pressure'),('pi','pi'),('T','tensor')]:out[label]=float(np.max(np.abs(np.array(X[field])-Y[field])))/den
    return out

def tensor_difference(X,Y):
    return float(np.max(np.abs(np.array(X)-Y)))

def packet_check(S,C,name):
    n,w=rule(name);q=1+np.einsum('ni,ij,nj->n',n,S,n)
    birth_w=SCALE.density_factor*CARD.energy_J*NB*w*q
    R=math.exp(-A)*C;k=n@R.T;weights=D*birth_w
    T=kinetic.tensor(k,weights,np.zeros(len(w)))/RHOSTAR
    rho,flux,p,pi=kinetic.moments(k,weights,np.zeros(len(w)))
    direct=moments(S,C,n,w);den=direct['F']
    number=float(np.sum(weights)/(SCALE.density_factor*CARD.energy_J))
    return dict(tensor_error=tensor_difference(T,direct['T'])/den,
        rho_error=abs(rho/RHOSTAR-direct['F'])/den,
        flux_error=float(np.max(np.abs(flux/RHOSTAR-direct['flux'])))/den,
        pressure_error=abs(p/RHOSTAR-direct['F']/3)/den,
        pi_error=tensor_difference(pi/RHOSTAR,direct['pi'])/den,
        number_density_m3=number,number_relative_error=abs(number/(NB*D)-1),
        minimum_weight=float(np.min(weights)),maximum_energy_over_birth=float(np.max(np.linalg.norm(k,axis=1))))

def binomial_tail(p,delta,K=40):
    coefficient=1.
    for j in range(1,K+2):coefficient*= (p-j+1)/j
    return abs(coefficient)*delta**(K+1)/(1-delta)

def truncation_bound(C):
    ev=np.linalg.eigvalsh(C);lo=float(ev[0]);hi=float(ev[-1]);a0=(hi*hi+lo*lo)/2
    delta=(hi*hi-lo*lo)/(hi*hi+lo*lo)
    return dict(K=40,polynomial_degree=84,a0=a0,delta=delta,
        energy_absolute=2*math.sqrt(a0)*binomial_tail(.5,delta),
        pressure_component_absolute=2*hi*hi/math.sqrt(a0)*binomial_tail(-.5,delta),
        qualification='IDEAL_NODE_TRUNCATION_ONLY; floating nodes and summation not interval-certified')

def axial_oracle():
    u=math.exp(-3/20);v=math.exp(3/10);d=v*v-u*u
    term=u*u/math.sqrt(d)*math.asinh(math.sqrt(d)/u)
    F=(v+term)/2;pz=v*v/(2*d)*(v-term);P=np.diag([(F-pz)/2,(F-pz)/2,pz])
    T=np.zeros((4,4));T[0,0]=F;T[1:,1:]=P
    return dict(F=F,P=P.tolist(),pi=(P-np.eye(3)*F/3).tolist(),flux=[0.,0.,0.],T=T.tolist())

def leading(label,name):
    if name=='Q14':
        e,p,power_e,power_p=(-9/35000,np.diag([13.,-11.,-2.])/10500,2,1) if label=='ANISO' else (-9/17500,np.diag([13.,-11.,-2.])/3500,3,2)
    else:
        e,p,power_e,power_p=(-7/100000,np.diag([9.,-3.,-6.])/20000,3,2) if label=='ANISO' else (-7/40000,np.diag([3.,-1.,-2.])/2000,4,3)
    return dict(energy_coefficient=e,pressure_coefficient=p.tolist(),energy_power=power_e,pressure_power=power_p)

def observed_order(small,large):
    if min(small,large)<=RESOLUTION:return dict(value=None,status='ROUNDING_UNRESOLVED')
    return dict(value=math.log2(large/small),status='RESOLVED')
