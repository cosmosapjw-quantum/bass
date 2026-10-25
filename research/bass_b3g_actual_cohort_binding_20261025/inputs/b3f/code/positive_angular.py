"""Frozen B3e positive mapped-cohort selector. No integration history or repair."""
from pathlib import Path
import math
import sys
import numpy as np
from numpy.polynomial.legendre import leggauss
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'vendor/rec_line_source/code'))
from vendor import core,kinetic
import line_source
EPS=np.finfo(float).eps
ROUND=512*EPS
TARGET=2e-8
ANGULAR=1e-8
FLOAT_ALLOWANCE=2e-12
CARD=line_source.CARDS['H_LYA_EFFECTIVE_2P']
SCALE=core.FixedScale(1.)
EB=CARD.energy_J
OZ=np.array([[3/5,-4/5,0],[4/5,3/5,0],[0,0,1.]])
OX=np.array([[1.,0,0],[0,5/13,-12/13],[0,12/13,5/13]])
OY=np.array([[3/5,0,4/5],[0,1.,0],[-4/5,0,3/5]])

class BoundNotMet(ValueError):
    def __init__(self,history):
        super().__init__('BOUND_NOT_MET: frozen K cap exhausted');self.history=history

def real_array(x,shape,label):
    a=np.asarray(x)
    if np.iscomplexobj(a) or a.dtype.kind not in 'fiu' or a.shape!=shape or not np.all(np.isfinite(a)):
        raise ValueError(label+' requires finite real '+str(shape))
    return a.astype(float,copy=False)

def density(x):
    a=real_array(x,(),'density');v=float(a)
    if v<0:raise ValueError('negative birth density')
    return v

def validate(S,R):
    S=real_array(S,(3,3),'S');R=real_array(R,(3,3),'R')
    if np.max(np.abs(S-S.T))>ROUND:raise ValueError('S must be symmetric')
    if abs(np.trace(S))>ROUND:raise ValueError('S must be STF')
    if np.linalg.eigvalsh(S)[0]<-1:raise ValueError('negative continuous source q')
    singular=np.linalg.svd(R,compute_uv=False);b=float(singular[0]);a=float(singular[-1])
    if a<=0 or np.linalg.det(R)<=0:raise ValueError('R must be invertible with positive determinant')
    if b>1+ROUND or b/a>2+ROUND:raise ValueError('bounded outgoing/condition domain exceeded')
    return S,R,a,b

def geometry(S,R):
    S,R,a,b=validate(S,R);s=(a*a+b*b)/2;delta=(b*b-a*a)/(b*b+a*a)
    H=np.eye(3)/3+2*S/15;M=R@H@R.T;m2=float(np.trace(M))
    return dict(a=a,b=b,s=s,delta=delta,H=H,M=M,m2=m2,
                F_lower=(m2+a*b)/(a+b),F_upper=math.sqrt(m2))

def bound(S,R,K):
    if not isinstance(K,(int,np.integer)) or K<0:raise ValueError('nonnegative integer K required')
    g=geometry(S,R);coefficient=1.
    for j in range(1,K+2):coefficient*=(-.5-j+1)/j
    tm=abs(coefficient)*g['delta']**(K+1)/(1-g['delta']);tp=tm/(2*K+1)
    beta=2*tm/math.sqrt(g['s']);bf=2*math.sqrt(g['s'])*tp
    bp=beta*float(np.linalg.norm(g['M'],'fro'));bt=math.hypot(bf,bp)
    old=math.sqrt(bf*bf+3*(beta*g['b']**2)**2)/g['a']
    return dict(K=int(K),Nmu=K+3,Nphi=2*(K+3),points=2*(K+3)**2,
                tminus=tm,tplus=tp,beta=beta,B_F=bf,B_P_F=bp,B_T=bt,
                bound_relative=bt/g['F_lower'],baseline_relative=old,
                F_lower=g['F_lower'],F_upper=g['F_upper'],a=g['a'],b=g['b'],s=g['s'],delta=g['delta'])

def select(S,R,maxK=64,baseline=False):
    if not isinstance(maxK,int) or not 0<=maxK<=64:raise ValueError('maxK outside [0,64]')
    history=[];key='baseline_relative' if baseline else 'bound_relative'
    for K in range(maxK+1):
        row=bound(S,R,K);history.append(row)
        if row[key]<=ANGULAR:return dict(selected=row,history=history,strategy='worst_direction' if baseline else 'source_aware')
    raise BoundNotMet(history)

def sphere_rule(N):
    if not isinstance(N,int) or N<3:raise ValueError('Nmu integer >=3 required')
    mu,w=leggauss(N);phi=np.arange(2*N)*math.pi/N
    mm,pp=np.meshgrid(mu,phi,indexing='ij');rr=np.sqrt(1-mm*mm)
    rays=np.stack((rr*np.cos(pp),rr*np.sin(pp),mm),axis=-1).reshape(-1,3)
    weights=np.broadcast_to(w[:,None]/(4*N),(N,2*N)).reshape(-1).copy()
    return rays,weights

def moments(S,R,n,A):
    S,R,_,_=validate(S,R);n=real_array(n,(len(n),3),'rays');A=real_array(A,(len(n),),'weights')
    if np.any(A<0) or np.max(np.abs(np.sum(n*n,axis=1)-1))>ROUND:raise ValueError('positive sphere rule required')
    q=np.einsum('ni,ij,nj->n',n,np.eye(3)+S,n)
    if np.any(q<0):raise ValueError('negative sampled q; no clipping')
    v=n@R.T;r=np.linalg.norm(v,axis=1);measure=A*q
    F=float(np.sum(measure*r));P=np.einsum('n,ni,nj->ij',measure/r,v,v)
    flux=np.einsum('n,ni->i',measure,v);T=np.zeros((4,4));T[0,0]=F;T[1:,1:]=P;T[0,1:]=flux;T[1:,0]=flux
    M=np.einsum('n,ni,nj->ij',measure,v,v)
    return dict(F=F,P=P,pi=P-np.eye(3)*F/3,flux=flux,T=T,M_quadrature=M,
                normalization=float(np.sum(measure)),minimum_q=float(np.min(q)),minimum_A=float(np.min(A)),
                sphere_residual=float(np.max(np.abs(np.sum(n*n,axis=1)-1))))

def packets(S,R,n,A,nb=1.):
    nb=density(nb);S,R,_,_=validate(S,R)
    # Evaluate the same admitted rays without changing or clipping q.
    direct=moments(S,R,n,A);q=np.einsum('ni,ij,nj->n',n,np.eye(3)+S,n)
    k=n@R.T;w=SCALE.density_factor*EB*nb*np.linalg.det(R)*A*q
    return k,w,np.zeros(len(A)),direct

def mixture_relative(coefficients,bounds,denominators):
    c=real_array(coefficients,(len(coefficients),),'coefficients')
    if np.any(c<0):raise ValueError('negative mixture coefficient')
    den=float(np.dot(c,denominators))
    if den<=0:raise ValueError('all-zero mixture relative error undefined')
    return float(np.dot(c,bounds))/den

def fixtures():
    R=OZ@np.diag([.45,.60,.90])@OX.T
    return [('G1',OY@np.diag([.30,-.10,-.20])@OY.T,R),('G2',np.zeros((3,3)),R),
        ('G3',OZ@np.diag([.90,-.35,-.55])@OZ.T,OX@np.diag([.50,.75,.90])@OY.T),
        ('G4',np.diag([-1.,.4,.6]),np.diag([.45,.60,.90])),
        ('G5',np.diag([-1.,.4,.6]),.7*np.eye(3))]

def serial(x):
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    if isinstance(x,dict):return {k:serial(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [serial(v) for v in x]
    return x
