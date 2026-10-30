#!/usr/bin/env python3
"""CE1-AC original source exact continuum l=4 time-jet rank certificate.

All moments and all operations use integer outward fixed-point interval arithmetic.
No GL/ray discretization or numerical IVP path enters the rank proof.
"""
from __future__ import annotations
import argparse, functools, hashlib, itertools, json, math, sys
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'original_source'
sys.path.insert(0,str(SRC))
from cellwise_gl_rust import MU,PHI,CELL_E,SHEAR,frozen_source_identity
SOURCE_EXPECT='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'

SCALE=10**80

def ceildiv(a,b):return -((-a)//b)
@dataclass(frozen=True)
class I:
    l:int
    h:int
    def __post_init__(self):
        if self.l>self.h:raise ValueError('reversed interval')
    @classmethod
    def rat(cls, r):
        r=F(r)
        return cls((r.numerator*SCALE)//r.denominator,ceildiv(r.numerator*SCALE,r.denominator))
    @classmethod
    def z(cls):return cls(0,0)
    def __add__(self,other):
        b=iv(other);return I(self.l+b.l,self.h+b.h)
    __radd__=__add__
    def __neg__(self):return I(-self.h,-self.l)
    def __sub__(self,other):return self+-iv(other)
    def __rsub__(self,other):return iv(other)-self
    def __mul__(self,other):
        b=iv(other); v=[self.l*b.l,self.l*b.h,self.h*b.l,self.h*b.h]
        return I(min(v)//SCALE,ceildiv(max(v),SCALE))
    __rmul__=__mul__
    def reciprocal(self):
        if self.l<=0<=self.h:raise ZeroDivisionError('interval contains zero')
        # For fixed-point B, 1/(B/SCALE) * SCALE = SCALE^2/B
        return I(SCALE*SCALE//self.h,ceildiv(SCALE*SCALE,self.l))
    def __truediv__(self,other):return self*iv(other).reciprocal()
    def sqrt(self):
        if self.l<0:raise ValueError('negative sqrt')
        low=math.isqrt(self.l*SCALE)
        up=math.isqrt(self.h*SCALE)
        if up*up<self.h*SCALE:up+=1
        return I(low,up)
    def pair(self):return [format(self.l/SCALE,'.17g'),format(self.h/SCALE,'.17g')]
    def exact_text(self):return [str(self.l)+'e-80',str(self.h)+'e-80']
    def decimal(self, digits=60):
        from decimal import Decimal,localcontext
        with localcontext() as c:
            c.prec=digits
            return [str(Decimal(self.l)/Decimal(SCALE)),str(Decimal(self.h)/Decimal(SCALE))]
    def width(self):return self.h-self.l

def iv(a):return a if isinstance(a,I) else I.rat(a)
ZERO=I.z();ONE=I.rat(1)

def alternating_arctan_bounds(x:F,N:int):
    # x>0 rational; alternating, monotonically decreasing terms.
    S=F(0)
    for k in range(N):S+=(-1)**k*x**(2*k+1)/F(2*k+1)
    r=(-1)**N*x**(2*N+1)/F(2*N+1)
    return min(S,S+r),max(S,S+r)

def pi_machin():
    p=alternating_arctan_bounds(F(1,5),85)
    q=alternating_arctan_bounds(F(1,239),40)
    low=16*p[0]-4*q[1];high=16*p[1]-4*q[0]
    return I(low.numerator*SCALE//low.denominator, ceildiv(high.numerator*SCALE,high.denominator))
PI=pi_machin()
SQ2=I.rat(2).sqrt()

def sin_symbol(k,t):
    # sin(k*pi*t) at t in {0,1/4,3/4,1} = a+b sqrt(2)
    z=k*t*4
    if z.denominator!=1:raise ValueError((k,t,z))
    table={0:(0,0),1:(0,F(1,2)),2:(1,0),3:(0,F(1,2)),4:(0,0),5:(0,F(-1,2)),6:(-1,0),7:(0,F(-1,2))}
    return table[int(z)%8]

@functools.lru_cache(None)
def phi_average_symbol(a,b,lo,hi):
    n=a+b;A={}
    for p in range(2*a+1):
        for q in range(2*b+1):
            k=n-p-q
            A[k]=A.get(k,F(0))+F((-1)**(b+q)*math.comb(2*a,p)*math.comb(2*b,q),4**n)
    assert all(A[k]==A.get(-k,F(0)) for k in A)
    a0=A.get(0,F(0)); r=F(0);s=F(0)
    for k in range(1,n+1):
        u=sin_symbol(k,hi);v=sin_symbol(k,lo)
        fac=2*A.get(k,F(0))/F(k)/(hi-lo)
        r+=fac*(u[0]-v[0]);s+=fac*(u[1]-v[1])
    return a0,r,s

@functools.lru_cache(None)
def mu_average(a,b,c,lo,hi):
    power=a+b
    out=F(0)
    for j in range(power+1):
        k=2*(c+j)+1
        out+=(-1)**j*math.comb(power,j)*(hi**k-lo**k)/k/(hi-lo)
    return out

@functools.lru_cache(None)
def moment_symbol(a,b,c):
    # Returned triple A, D, G such that integral = A + (D+G sqrt(2))/pi.
    A=D=G=F(0)
    for j in range(2):
        for k in range(3):
            mu0=F.from_float(float(MU[j]));mu1=F.from_float(float(MU[j+1]))
            t0=F.from_float(float(PHI[k]));t1=F.from_float(float(PHI[k+1]))
            factor=F.from_float(float(CELL_E[j,k]))*mu_average(a,b,c,mu0,mu1)
            v=phi_average_symbol(a,b,t0,t1)
            A+=factor*v[0];D+=factor*v[1];G+=factor*v[2]
    return A,D,G

MOMENT_KEYS=[]
@functools.lru_cache(None)
def moment(a,b,c):
    MOMENT_KEYS.append((a,b,c))
    A,D,G=moment_symbol(a,b,c)
    return iv(A)+(iv(D)+iv(G)*SQ2)/PI

# Sparse polynomials in original initial unit direction squared, x+y+z=1.
class Poly:
    def __init__(self,values=None):
        self.coeff={k:iv(v) for k,v in (values or {}).items() if iv(v).l or iv(v).h}
    @classmethod
    def const(cls,v):return cls({(0,0,0):v})
    @classmethod
    def coordinate(cls,j):
        power=[0,0,0];power[j]=1
        return cls({tuple(power):1})
    def __add__(self,b):
        b=pol(b);keys=set(self.coeff)|set(b.coeff)
        return Poly({k:self.coeff.get(k,ZERO)+b.coeff.get(k,ZERO) for k in keys})
    __radd__=__add__
    def __neg__(self):return Poly({k:-v for k,v in self.coeff.items()})
    def __sub__(self,b):return self+-pol(b)
    def __rsub__(self,b):return pol(b)-self
    def __mul__(self,b):
        b=pol(b);acc={}
        for a,x in self.coeff.items():
            for c,y in b.coeff.items():
                k=tuple(a[i]+c[i] for i in range(3))
                acc[k]=acc.get(k,ZERO)+x*y
        return Poly(acc)
    __rmul__=__mul__
    def integrate(self):return sum((v*moment(*k) for k,v in self.coeff.items()),ZERO)
    def degree(self):return max((sum(k) for k in self.coeff),default=0)
    def monomials(self):return len(self.coeff)

def pol(x):return x if isinstance(x,Poly) else Poly.const(x)

def det3(M):
    p=ZERO
    for perm in itertools.permutations(range(3)):
        n=sum(perm[i]>perm[j] for i in range(3) for j in range(i+1,3))
        term=M[0][perm[0]]*M[1][perm[1]]*M[2][perm[2]]
        p=p+(-term if n%2 else term)
    return p

def certify():
    source=frozen_source_identity()
    assert source==SOURCE_EXPECT
    X=[Poly.coordinate(i) for i in range(3)];x,y,z=X
    mass0=moment(0,0,0)
    pressure=[moment(*(1 if j==i else 0 for j in range(3))) for i in range(3)]
    s=[iv(F.from_float(float(v))) for v in SHEAR]
    assert sum((F.from_float(float(v)) for v in SHEAR),F(0))==0
    H0=((mass0+sum((v*v for v in s),ZERO)/iv(2))/iv(3)).sqrt()
    h=[H0+v for v in s]
    theta=sum(h,ZERO)
    a=[-theta*h[i]+pressure[i] for i in range(3)]
    B=sum((X[i]*h[i] for i in range(3)),Poly())
    C=sum((X[i]*h[i]*h[i] for i in range(3)),Poly())
    D=sum((X[i]*a[i] for i in range(3)),Poly())
    Bdot=2*(B*B-C)+D
    xp=[2*X[i]*(B-h[i]) for i in range(3)]
    xpp=[4*X[i]*(B-h[i])*(B-h[i])+2*X[i]*(Bdot-a[i]) for i in range(3)]
    dx,dy,dz=xp;ddx,ddy,ddz=xpp
    w1=-B
    w2=2*C-B*B-D
    T=[35*z*z-30*z+3,(x-y)*(7*z-1),x*x-6*x*y+y*y]
    Tp=[(70*z-30)*dz,(dx-dy)*(7*z-1)+7*(x-y)*dz,(2*x-6*y)*dx+(2*y-6*x)*dy]
    Tpp=[(70*z-30)*ddz+70*dz*dz,(ddx-ddy)*(7*z-1)+14*(dx-dy)*dz+7*(x-y)*ddz,(2*x-6*y)*ddx+(2*y-6*x)*ddy+2*dx*dx-12*dx*dy+2*dy*dy]
    m0=mass0;m0p=w1.integrate();m0pp=w2.integrate()
    mat=[[],[],[]]
    polys=[]
    for k in range(3):
        c0=T[k].integrate();c1=(Tp[k]+T[k]*w1).integrate();c2=(Tpp[k]+2*Tp[k]*w1+T[k]*w2).integrate()
        f0=c0/m0;f1=(c1-f0*m0p)/m0;f2=(c2-f0*m0pp-2*f1*m0p)/m0
        for j,v in enumerate([f0,f1,f2]):mat[j].append(v)
        polys.append({'T_degree':T[k].degree(),'Tprime_degree':Tp[k].degree(),'Tsecond_degree':Tpp[k].degree(),
                      'T2_monomials':Tpp[k].monomials()})
    determinant=det3(mat)
    out={'schema':'bass.ce1ac.original_exact_continuum_l4_jet_interval.v1',
         'statement':'nonzero det of three initial-time jets of unnormalized harmonic polynomials / energy; positive harmonic normalizations preserve rank',
         'source_sha256':source,'model':'massless collisionless diagonal Bianchi I, Lambda=0, (-,+,+,+), u=t/Tstar in [0,0.08]',
         'convention':'Exact binary64 source cell energies and shear treated as exact dyadics, continuous spherical angular integrals, positivity and reflections preserved',
         'interval_arithmetic':'integer fixed-point outward with unit=1e-80; pi Machin alternating rational, sqrt2 and H0 integer isqrt',
         'moment_field':'A+(D+G sqrt2)/pi; all moments derived from exact cell angular measure without quadrature',
         'moments_evaluated':moment.cache_info().currsize,'moment_max_degree':max(map(sum,MOMENT_KEYS)),
         'pi_interval':PI.decimal(),'sqrt2_interval':SQ2.decimal(),
         'E0_interval':mass0.decimal(), 'P0_intervals':[v.decimal(40) for v in pressure],
         'initial_h0_interval':[v.decimal() for v in h], 'initial_hprime_interval':[v.decimal() for v in a],
         'normalized_polynomial_jet_rows':[[v.decimal(55) for v in row] for row in mat],
         'interval_det_of_unscaled_l4_jet':determinant.decimal(65),'interval_determinant_width_scaled_integer':str(determinant.width()),
         'strict_positive_determinant':determinant.l>0,
         'interval_det_dyadic_lower_as_integer_times_1e_minus_80':str(determinant.l),
         'physical_claim_if_strict':'The exact original-continuum normalized l4 3-vector has three independent C^2 time components near u=0, hence continuous-time deterministic l4 Gram kernel rank 3; not a 41-sample lambda3 numeric certificate',
         'degree_diagnostics':polys,
         'DAG_upper':'9/15','CE1':'PARTIAL','production_ready':False,'merge_ready':False,'auto_next':False}
    assert determinant.l>0, ('no positive determinant',determinant.decimal())
    dest=ROOT/'data'/'ORIGINAL_CONTINUUM_L4_JET_INTERVAL.json'
    dest.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print('STRICT continuum positive det unscaled initial jet:',determinant.decimal(52),'moment count',out['moments_evaluated'],flush=True)
    return out
if __name__=='__main__':certify()
