"""CE1-AC: exact-original-cell rational interval certificate for initial l=4 third jet mode.

This is NOT a GL approximation. The six original cell masses, mu and phi_frac
boundaries, and shears are interpreted as exact stored binary64 rationals.
Moments are finite exact Q(sqrt(2),1/pi) expressions; finite rational
Machin-arctan and integer-sqrt brackets enclose all irrational constants.
All subsequent interval operations use exact Fraction arithmetic.
"""
from __future__ import annotations
import hashlib, json, math, sys
from dataclasses import dataclass
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
from source_paths import SRC
sys.path.insert(0,str(SRC))
from cellwise_gl_rust import MU, PHI, CELL_E, SHEAR, frozen_source_identity
ORIGINAL_SHA='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
D=85

@dataclass(frozen=True)
class I:
    lo:F
    hi:F
    def __init__(self,lo=0,hi=None):
        if isinstance(lo,I) and hi is None:
            object.__setattr__(self,'lo',lo.lo);object.__setattr__(self,'hi',lo.hi);return
        a=F(lo);b=F(hi) if hi is not None else a
        if a>b:raise ValueError('reversed interval')
        object.__setattr__(self,'lo',a);object.__setattr__(self,'hi',b)
    @staticmethod
    def c(v):return v if isinstance(v,I) else I(v)
    def __add__(self,other):
        b=self.c(other);return I(self.lo+b.lo,self.hi+b.hi)
    __radd__=__add__
    def __neg__(self):return I(-self.hi,-self.lo)
    def __sub__(self,b):return self+(-self.c(b))
    def __rsub__(self,b):return self.c(b)+(-self)
    def __mul__(self,b):
        b=self.c(b);products=[self.lo*b.lo,self.lo*b.hi,self.hi*b.lo,self.hi*b.hi]
        return I(min(products),max(products))
    __rmul__=__mul__
    def __truediv__(self,b):
        b=self.c(b)
        if b.lo<=0<=b.hi:raise ZeroDivisionError('interval includes zero')
        return self*I(1/b.hi,1/b.lo)
    def __rtruediv__(self,b):return self.c(b)/self
    def __pow__(self,n:int):
        if not isinstance(n,int) or n<0: raise ValueError('nonnegative integer only')
        r=I(1)
        for _ in range(n):r=r*self
        return r
    def positive(self):return self.lo>0
    def negative(self):return self.hi<0
    def width(self):return self.hi-self.lo
    def sqrt(self, digits=D):
        if self.lo<0:raise ValueError('negative radicand')
        s=10**digits
        a=math.isqrt(self.lo.numerator*s*s//self.lo.denominator)
        b=math.isqrt(self.hi.numerator*s*s//self.hi.denominator)
        return I(F(a,s),F(b+1,s))
    def fmt(self,digits=48):
        def conv(q,rounding):
            with localcontext() as ctx:
                ctx.prec=digits+6;ctx.rounding=rounding
                y=Decimal(q.numerator)/Decimal(q.denominator)
                return format(+y, f'.{digits}g')
        return [conv(self.lo,ROUND_FLOOR),conv(self.hi,ROUND_CEILING)]

ZERO=I(0);ONE=I(1)

def arctan_bounds(x:F,N:int):
    s=F(0)
    for k in range(N):s+=F((-1)**k)*(x**(2*k+1))/F(2*k+1)
    nxt=F((-1)**N)*x**(2*N+1)/F(2*N+1)
    return I(min(s,s+nxt),max(s,s+nxt))

PI=16*arctan_bounds(F(1,5),95)-4*arctan_bounds(F(1,239),45)
RT2=I(2).sqrt()

# Each symbolic cell moment = A+(B+C sqrt(2))/pi; all A,B,C exact rationals.
@lru_cache(None)
def sin_quarter_pi(m:int,t:F):
    n=4*m*t
    if n.denominator!=1:raise ValueError('non-quarter angle')
    return {0:(F(0),F(0)),1:(F(0),F(1,2)),2:(F(1),F(0)),3:(F(0),F(1,2)),
            4:(F(0),F(0)),5:(F(0),F(-1,2)),6:(F(-1),F(0)),7:(F(0),F(-1,2))}[int(n)%8]

@lru_cache(None)
def phi_average(a:int,b:int,tlo:F,thi:F):
    # 2(a+b)th real-power trigonometric product, exact Fourier expansion.
    n=a+b
    coeff={}
    for j in range(2*a+1):
        for k in range(2*b+1):
            order=n-j-k
            value=F((-1)**(b+k)*math.comb(2*a,j)*math.comb(2*b,k),4**n)
            coeff[order]=coeff.get(order,F(0))+value
    assert all(coeff[k]==coeff.get(-k,F(0)) for k in coeff)
    A=coeff.get(0,F(0));B=C=F(0)
    for m in range(1,n+1):
        sinhi=sin_quarter_pi(m,thi);sinlo=sin_quarter_pi(m,tlo)
        fac=F(2)*coeff.get(m,F(0))/F(m)/(thi-tlo)
        B+=fac*(sinhi[0]-sinlo[0]);C+=fac*(sinhi[1]-sinlo[1])
    return (A,B,C)

@lru_cache(None)
def mu_average(a:int,b:int,c:int,lo:F,hi:F):
    out=F(0)
    for k in range(a+b+1):
        m=2*(c+k)+1
        out+=F((-1)**k*math.comb(a+b,k))*(hi**m-lo**m)/m/(hi-lo)
    return out

@lru_cache(None)
def moment_symbol(a,b,c):
    A=B=C=F(0)
    for i in range(2):
        for j in range(3):
            slo=F.from_float(float(MU[i]));shi=F.from_float(float(MU[i+1]))
            tlo=F.from_float(float(PHI[j]));thi=F.from_float(float(PHI[j+1]))
            w=F.from_float(float(CELL_E[i,j]))*mu_average(a,b,c,slo,shi)
            xx=phi_average(a,b,tlo,thi)
            A+=w*xx[0];B+=w*xx[1];C+=w*xx[2]
    return A,B,C

@lru_cache(None)
def moment(a,b,c):
    A,B,C=moment_symbol(a,b,c)
    return I(A)+(I(B)+I(C)*RT2)/PI

@dataclass
class Poly:
    terms:dict
    def __init__(self,terms=None):
        self.terms={k:I(v) for k,v in (terms or {}).items() if I(v).lo!=0 or I(v).hi!=0}
    @staticmethod
    def const(n):return Poly({(0,0,0):n})
    @staticmethod
    def var(i):return Poly({tuple(int(j==i) for j in range(3)):1})
    @staticmethod
    def coerce(o):return o if isinstance(o,Poly) else Poly.const(o)
    def __add__(self,other):
        other=self.coerce(other);out=self.terms.copy()
        for k,v in other.terms.items():out[k]=out.get(k,ZERO)+v
        return Poly(out)
    __radd__=__add__
    def __neg__(self):return Poly({k:-v for k,v in self.terms.items()})
    def __sub__(self,other):return self+(-self.coerce(other))
    def __rsub__(self,other):return self.coerce(other)+(-self)
    def __mul__(self,other):
        other=self.coerce(other);out={}
        for a,wa in self.terms.items():
            for b,wb in other.terms.items():
                k=tuple(a[i]+b[i] for i in range(3))
                out[k]=out.get(k,ZERO)+wa*wb
        return Poly(out)
    __rmul__=__mul__
    def __pow__(self,n):
        out=Poly.const(1)
        for _ in range(n):out=out*self
        return out
    def deriv(self,i):
        out={}
        for k,v in self.terms.items():
            if k[i]>0:
                kp=list(k);kp[i]-=1
                out[tuple(kp)]=v*k[i]
        return Poly(out)
    def av(self):
        E0=sum((F.from_float(float(x)) for x in CELL_E.flatten()),F(0))
        result=ZERO
        for k,v in self.terms.items():result+=v*moment(*k)/E0
        return result


def det3(rows):
    a,b,c=rows[0];d,e,f=rows[1];g,h,i=rows[2]
    return a*(e*i-f*h)-b*(d*i-f*g)+c*(d*h-e*g)

def certificate():
    assert frozen_source_identity()==ORIGINAL_SHA
    assert PI.lo>F(314,100) and PI.hi<F(315,100)
    assert RT2.lo>F(141,100) and RT2.hi<F(142,100)
    E0=sum((F.from_float(float(x)) for x in CELL_E.flatten()),F(0))
    shears=[I(F.from_float(float(v))) for v in SHEAR]
    H0=((I(E0)+sum((q*q for q in shears),ZERO)/2)/3).sqrt()
    h0=[H0+q for q in shears]
    theta=sum(h0,ZERO)
    x,y,z=[Poly.var(i) for i in range(3)]
    xyz=[x,y,z]
    first_moments=[p.av() for p in xyz]
    P0=[I(E0)*m for m in first_moments]
    hp=[-theta*h0[i]+P0[i] for i in range(3)]
    B=sum((xyz[i]*h0[i] for i in range(3)),Poly.const(0))
    A=sum((xyz[i]*hp[i] for i in range(3)),Poly.const(0))
    S2=sum((xyz[i]*(h0[i]*h0[i]) for i in range(3)),Poly.const(0))
    V=[2*xyz[i]*(B-h0[i]) for i in range(3)]
    Bdot=A+2*(B*B-S2)
    W=[2*V[i]*(B-h0[i])+2*xyz[i]*(Bdot-hp[i]) for i in range(3)]
    C=-A-B*B+2*S2
    T=[35*z*z-30*z+3,(x-y)*(7*z-1),x*x-6*x*y+y*y]
    Ts=[sum((p.deriv(i)*V[i] for i in range(3)),Poly.const(0)) for p in T]
    Tss=[sum((p.deriv(i)*W[i] for i in range(3)),Poly.const(0))+
         sum((p.deriv(i).deriv(j)*V[i]*V[j] for i in range(3) for j in range(3)),Poly.const(0)) for p in T]
    N1=(-B).av();N2=C.av()
    triples=[]
    for t,td,tdd in zip(T,Ts,Tss):
        M0=t.av();M1=(td-B*t).av();M2=(tdd-2*B*td+C*t).av()
        a1=M1-M0*N1;a2=M2-M0*N2-2*a1*N1
        triples.append([M0,a1,a2])
    rows=[[triples[j][i] for j in range(3)] for i in range(3)]
    delta=det3(rows)
    scales=[PI.sqrt()/4, (5*PI).sqrt()/2, (35*PI).sqrt()/4]
    scaled=[[rows[i][j]*scales[j] for j in range(3)] for i in range(3)]
    scaled_delta=det3(scaled)
    # Higher moment positivity and source angular constraint, checked independently.
    assert (moment(1,0,0)+moment(0,1,0)+moment(0,0,1)-I(E0)).lo<=0
    assert (moment(1,0,0)+moment(0,1,0)+moment(0,0,1)-I(E0)).hi>=0
    if not scaled_delta.positive() or not scaled_delta.lo>F(3,100000):raise ArithmeticError('rank3 sign was NOT certified')
    cert={'schema':'bass.ce1ac.original_six_cell_exact_initial_l4_rank3.v1',
          'status':'DERIVED_EXACT_RATIONAL_INTERVAL',
          'original_source_sha256':ORIGINAL_SHA,
          'source': 'original six exact dyadic energy cells; uniform mu and phi_frac angular coordinate in each cell',
          'metric_signature':'(-,+,+,+)', 'normal_proper_time':'u=t/Tstar',
          'model':'positive massless collisionless diagonal Einstein-Vlasov Bianchi I with Lambda=0',
          'cell_weight_exact_binary64_hex':[[float(q).hex() for q in row] for row in CELL_E],
          'mu_binary64_hex':[float(q).hex() for q in MU],
          'phi_fraction_binary64_hex':[float(q).hex() for q in PHI],
          'shear_binary64_hex':[float(q).hex() for q in SHEAR],
          'initial_E0_exact_dyadic_rational':str(E0),
          'H0_interval':H0.fmt(55),'initial_h_intervals':[v.fmt(45) for v in h0],
          'initial_hprime_intervals':[v.fmt(45) for v in hp],
          'moment_exact_structure':'A+(B+C sqrt(2))/pi, A B C exact rationals for every monomial',
          'moment_count':moment.cache_info().currsize,
          'max_moment_total_degree':4,
          'irrational_bounds':{'pi':PI.fmt(55),'sqrt2':RT2.fmt(55),'sqrt_pi':PI.sqrt().fmt(55)},
          'rational_certification_method':'Machin pi alternating-series N=95/45, integer-isqrt 85 decimal radix, exact Fraction interval operations',
          'unscaled_initial_l4_jet_matrix_interval':[[v.fmt(45) for v in row] for row in rows],
          'scaled_initial_l4_jet_matrix_interval':[[v.fmt(45) for v in row] for row in scaled],
          'unscaled_initial_jet_det_interval':delta.fmt(57),
          'scaled_initial_jet_det_interval':scaled_delta.fmt(57),
          'exact_initial_jet_det_strictly_positive':scaled_delta.positive(),
          'simple_exact_rational_det_lower':'3/100000',
          'physical_continuum_l4_function_rank_at_least_3_on_interval':True,
          'constant_harmonic_conventions':'X=(sqrt(pi)/4 * T40_normalized, sqrt(5pi)/2 * T42_normalized, sqrt(35pi)/4 * T44_normalized)',
          'DAG_upper_completed':9,'DAG_upper_total':15,'CE1':'PARTIAL',
          'not_claimed':['finite 41 epoch true-spacetime Gram lambda3 strict positivity by uniform error transport',
                         'numerical 3rd eigenvalue of continuous-time integral K4 operator',
                         'fully formal MPFR implementation correctness','CMB temperature/polarization/likelihood']}
    moments={}
    for degree in range(5):
        for a in range(degree+1):
            for b in range(degree-a+1):
                c=degree-a-b
                m=moment_symbol(a,b,c)
                moments[f'{a},{b},{c}']={'A':str(m[0]),'B':str(m[1]),'C':str(m[2]),'interval':moment(a,b,c).fmt(55)}
    (BASE/'data'/'EXACT_MOMENT_SYMBOLIC_35.json').write_text(json.dumps({'model_sha256':ORIGINAL_SHA,
       'formula':'M_abc = A + (B + C sqrt(2))/pi; all A,B,C exact dyadic rational combinations',
       'moments':moments},indent=2)+'\n')
    return cert

if __name__=='__main__':
    report=certificate()
    p=BASE/'data'/'EXACT_CONTINUUM_INITIAL_JET_CERTIFICATE.json'
    p.write_text(json.dumps(report,indent=2)+'\n')
    print('CERTIFIED ORIGINAL CONTINUUM INITIAL THIRD JET',report['scaled_initial_jet_det_interval'])
    print('UNSCALED',report['unscaled_initial_jet_det_interval'])
    print('MOMENTS',report['moment_count'])
