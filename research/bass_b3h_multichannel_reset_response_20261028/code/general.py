"""Exact-rational same-law integrated signed-output enclosures.

The caller supplies whole-suffix physical/source validity; this module never
turns a supplied bound into a physical certificate or executes a native IVP.
"""
from fractions import Fraction as F
from itertools import product
import math


def source_number(x):
    if isinstance(x,bool) or x is None:raise ValueError('finite numeric literal required')
    if isinstance(x,float):
        if not math.isfinite(x):raise ValueError('finite binary64 required')
        return F.from_float(x)
    try:return F(x)
    except (ValueError,TypeError,ZeroDivisionError) as e:raise ValueError('finite rational required') from e


def q(x):
    if isinstance(x,(float,bool)) or x is None:raise ValueError('explicit rational required')
    return source_number(x)


def rows(value):
    if len(value)!=3 or any(len(r)!=2 for r in value):raise ValueError('three two-entry rows required')
    return tuple(tuple(q(x) for x in r) for r in value)


def combine(values):
    out=[[F(0),F(0)] for _ in range(3)]
    for value in values:
        for k,r in enumerate(rows(value)):
            for j in range(2):out[k][j]+=r[j]
    return tuple(map(tuple,out))


def energy_rows(ell0,ell1,e0,e1,n0,ev):
    if len(ell0)!=2 or len(ell1)!=2:raise ValueError('two interface coefficients required')
    e0,e1,n0,ev=map(q,(e0,e1,n0,ev))
    return (tuple(n0*ev*e0*q(x) for x in ell0),tuple(n0*ev*e1*q(x) for x in ell1),(F(0),F(0)))


class Context:
    def __init__(self,*,B,X,Dlo,Dhi,gamma,alphaM,LM,theta,Tlo,Rb,Rhi,alphaR,LR):
        if len(B)!=2 or any(len(r)!=2 for r in B) or len(X)!=2 or any(len(r)!=2 for r in X):raise ValueError('2x2 matrix and initial box required')
        self.B=tuple(tuple(q(x) for x in r) for r in B);self.X=tuple(tuple(q(x) for x in r) for r in X)
        a,b=self.B[0];c,d=self.B[1];self.beta=min(a+c,b+d);det=a*d-b*c
        if a<=0 or d<=0 or b>0 or c>0 or self.beta<=0 or det<=0:raise ValueError('inverse-positive column-contracting B required')
        self.inv=((d/det,-b/det),(-c/det,a/det))
        self.Dlo,self.Dhi,self.gamma,self.alphaM,self.LM,self.Tlo,self.Rb,self.Rhi,self.alphaR,self.LR=map(q,(Dlo,Dhi,gamma,alphaM,LM,Tlo,Rb,Rhi,alphaR,LR))
        if len(theta)!=2:raise ValueError('anchor interval required')
        self.theta=tuple(map(q,theta))
        if (min(self.Dlo,self.alphaM,self.LM,self.Rb,self.Rhi,self.alphaR,self.LR)<0 or self.Dlo>self.Dhi or self.gamma<=0 or self.Tlo<=0 or not 0<=self.theta[0]<=self.theta[1]<=1 or self.Rb>self.Rhi or any(lo>hi for lo,hi in self.X)):
            raise ValueError('ordered nonnegative source bounds required')
        self.tb=sum(self.theta)/2;self.te=(self.theta[1]-self.theta[0])/2
        self.Z=sum(max(abs(lo),abs(hi)) for lo,hi in self.X)
        self.phi=min(self.Dhi,1/self.beta);self.psi=min(self.Dhi*self.Dhi/2,1/(self.beta*self.beta))
        self.tail_factor=(1+self.beta*self.Dlo/8)**(-8)
        self.defect_mass=self.alphaM*self.phi+self.LM*self.psi


def response(c:Context,value):
    r0,r1,rr=rows(value);dr=tuple(b-a for a,b in zip(r0,r1))
    rb=tuple(a+c.tb*d+c.Rb*r for a,d,r in zip(r0,dr,rr))
    w=tuple(sum(rb[i]*c.inv[i][j] for i in range(2)) for j in range(2))
    center=tuple(sum((min if k==0 else max)(a*lo,a*hi) for a,(lo,hi) in zip(w,c.X)) for k in range(2))
    corners=[tuple(a+t*d+R*r for a,d,r in zip(r0,dr,rr)) for t,R in product((F(0),F(1)),(F(0),c.Rhi))]
    rmax=max(abs(v) for row in corners for v in row)
    alphar=c.te*max(map(abs,dr))+c.alphaR*max(map(abs,rr))
    Lr=max(map(abs,dr))/c.Tlo+c.LR*max(map(abs,rr))
    em=c.Z*rmax/c.gamma*c.defect_mass
    er=c.Z*(alphar*c.phi+Lr*c.psi)
    tail=max(map(abs,w))*c.Z*c.tail_factor
    radius=em+er+tail;gross=rmax*c.Dhi*c.Z
    lo=max(center[0]-radius,-gross);hi=min(center[1]+radius,gross)
    rpos=all(v>=0 for row in corners for v in row);rneg=all(v<=0 for row in corners for v in row)
    xpos=all(a>=0 for a,b in c.X);xneg=all(b<=0 for a,b in c.X)
    if (rpos and xpos) or (rneg and xneg):lo=max(lo,F(0))
    if (rpos and xneg) or (rneg and xpos):hi=min(hi,F(0))
    if lo>hi:raise ValueError('inconsistent enclosures')
    return dict(w=w,rb=rb,rmax=rmax,center_box=center,operator_error=em,row_error=er,tail=tail,radius=radius,interval=(lo,hi))
