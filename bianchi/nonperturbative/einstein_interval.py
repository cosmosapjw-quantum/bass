"""CE1-C directed-rounded scalar MPFR intervals for Bianchi-I budget primitives.

No heuristic epsilon padding. All input float objects are exact binary numbers.
MPFR operations use RNDD/RNDU. Requires libmpfr.so.6 explicitly; never
falls back silently to mpmath or binary64. Does not enclose the rounding
inside the PREVIOUS float64 RK4/GL source or Hermite path generator.
"""
from __future__ import annotations
import ctypes as C
import math
from math import comb
import numpy as np

class _S(C.Structure):
    _fields_=[('_mpfr_prec',C.c_long),('_mpfr_sign',C.c_int),('_mpfr_exp',C.c_long),('_mpfr_d',C.c_void_p)]
try:
    _lib=C.CDLL('libmpfr.so.6')
except OSError as exc:
    raise ImportError('CE1-C interval extension requires GNU MPFR6, no float fallback') from exc
_P=C.POINTER(_S)
for name,args in {
    'mpfr_init2':[_P,C.c_long],'mpfr_clear':[_P],
    'mpfr_set_d':[_P,C.c_double,C.c_int],
    'mpfr_set_si':[_P,C.c_long,C.c_int],
    'mpfr_set_str':[_P,C.c_char_p,C.c_int,C.c_int],
    'mpfr_set':[_P,_P,C.c_int],
    'mpfr_get_d':[_P,C.c_int], 'mpfr_cmp':[_P,_P],
    'mpfr_add':[_P,_P,_P,C.c_int],
    'mpfr_sub':[_P,_P,_P,C.c_int],
    'mpfr_mul':[_P,_P,_P,C.c_int],
    'mpfr_div':[_P,_P,_P,C.c_int],
    'mpfr_exp':[_P,_P,C.c_int],
    'mpfr_sqrt':[_P,_P,C.c_int],
    'mpfr_tanh':[_P,_P,C.c_int],
    'mpfr_sinh':[_P,_P,C.c_int],
    'mpfr_cosh':[_P,_P,C.c_int],
    'mpfr_neg':[_P,_P,C.c_int]
}.items():
    f=getattr(_lib,name);f.argtypes=args
    f.restype=C.c_double if name=='mpfr_get_d' else C.c_int
D=3;U=2;N=0;BITS=192

class _F:
    __slots__=('v',)
    def __init__(self):
        self.v=_S();_lib.mpfr_init2(C.byref(self.v),BITS)
    def __del__(self, _clear=_lib.mpfr_clear, _byref=C.byref):
        if hasattr(self,'v'):_clear(_byref(self.v))
    def ptr(self):return C.byref(self.v)

class Interval:
    """Finite closed MPFR interval, with outward operations and conversions."""
    __slots__=('a','b')
    def __init__(self,x):
        self.a=_F();self.b=_F()
        if isinstance(x,Interval):
            self._set(self.a,x.a,N);self._set(self.b,x.b,N)
        elif isinstance(x,(int,np.integer)) and not isinstance(x,(bool,np.bool_)):
            if not -(2**63)<=int(x)<2**63: raise ValueError('Integer out of supported signed-long range')
            _lib.mpfr_set_si(self.a.ptr(),int(x),D)
            _lib.mpfr_set_si(self.b.ptr(),int(x),U)
        else:
            x=float(x)
            if not math.isfinite(x):raise ValueError('Nonfinite interval input')
            _lib.mpfr_set_d(self.a.ptr(),x,D);_lib.mpfr_set_d(self.b.ptr(),x,U)
    @classmethod
    def decimal(cls,string):
        z=cls._empty()
        bs=str(string).encode('ascii')
        if _lib.mpfr_set_str(z.a.ptr(),bs,10,D) or _lib.mpfr_set_str(z.b.ptr(),bs,10,U):
            raise ValueError('Invalid exact decimal interval input')
        return z
    @classmethod
    def _empty(cls):
        z=cls.__new__(cls);z.a=_F();z.b=_F();return z
    @staticmethod
    def _set(dst,src,rounding):_lib.mpfr_set(dst.ptr(),src.ptr(),rounding)
    @property
    def lower(self):return _lib.mpfr_get_d(self.a.ptr(),D)
    @property
    def upper(self):return _lib.mpfr_get_d(self.b.ptr(),U)
    def contains(self,value):
        v=Interval(value)
        return _lib.mpfr_cmp(self.a.ptr(),v.a.ptr())<=0 and _lib.mpfr_cmp(self.b.ptr(),v.b.ptr())>=0
    def is_nonnegative(self):return _lib.mpfr_cmp(self.a.ptr(),Interval(0).a.ptr())>=0
    def _arith(self,other,op):
        y=as_iv(other);z=Interval._empty()
        f=getattr(_lib,'mpfr_'+op)
        if op=='add':
            f(z.a.ptr(),self.a.ptr(),y.a.ptr(),D);f(z.b.ptr(),self.b.ptr(),y.b.ptr(),U)
        elif op=='sub':
            f(z.a.ptr(),self.a.ptr(),y.b.ptr(),D);f(z.b.ptr(),self.b.ptr(),y.a.ptr(),U)
        elif op in ('mul','div'):
            if op=='div' and y.lower<=0<=y.upper:
                raise ZeroDivisionError('Divisor interval contains zero')
            lows=[];highs=[]
            for a in (self.a,self.b):
                for b in (y.a,y.b):
                    l=_F();h=_F();f(l.ptr(),a.ptr(),b.ptr(),D);f(h.ptr(),a.ptr(),b.ptr(),U)
                    lows.append(l);highs.append(h)
            lo=lows[0];hi=highs[0]
            for v in lows[1:]:
                if _lib.mpfr_cmp(v.ptr(),lo.ptr())<0:lo=v
            for v in highs[1:]:
                if _lib.mpfr_cmp(v.ptr(),hi.ptr())>0:hi=v
            self._set(z.a,lo,N);self._set(z.b,hi,N)
        return z
    def __add__(self,b):return self._arith(b,'add')
    def __radd__(self,b):return as_iv(b).__add__(self)
    def __sub__(self,b):return self._arith(b,'sub')
    def __rsub__(self,b):return as_iv(b).__sub__(self)
    def __mul__(self,b):return self._arith(b,'mul')
    def __rmul__(self,b):return as_iv(b).__mul__(self)
    def __truediv__(self,b):return self._arith(b,'div')
    def __rtruediv__(self,b):return as_iv(b).__truediv__(self)
    def __neg__(self):
        z=self._empty();_lib.mpfr_neg(z.a.ptr(),self.b.ptr(),D);_lib.mpfr_neg(z.b.ptr(),self.a.ptr(),U);return z
    def __pow__(self,n):
        if not isinstance(n,int) or n<0:raise ValueError('Only nonnegative integer powers')
        p=Interval(1);x=self
        while n:
            if n&1:p=p*x
            x=x*x;n//=2
        return p
    def _mono(self,name):
        z=self._empty();f=getattr(_lib,'mpfr_'+name)
        if name=='sqrt' and self.lower<0:raise ValueError('Negative sqrt input interval')
        f(z.a.ptr(),self.a.ptr(),D);f(z.b.ptr(),self.b.ptr(),U);return z
    def exp(self):return self._mono('exp')
    def sqrt(self):return self._mono('sqrt')
    def tanh(self):return self._mono('tanh')
    def sinh(self):return self._mono('sinh')
    def cosh(self):
        # cosh not monotone on real line. This budget uses nonnegative arguments.
        if self.lower<0:raise ValueError('cosh expects nonnegative interval here')
        return self._mono('cosh')
    def __repr__(self):return f'Interval([{self.lower:.17g},{self.upper:.17g}])'

def as_iv(x):return x if isinstance(x,Interval) else Interval(x)

def pressure_bound_interval(source,lo,hi):
    """MPFR-outward evaluation of CE1-B's *analytic* ideal-GL source bound.

    Inputs are exact binary64 coefficients and box endpoints. This is NOT yet a
    certified bound on numpy/BLAS evaluation of numerical quadrature weights.
    """
    lo=np.asarray(lo,float);hi=np.asarray(hi,float)
    if lo.shape!=(3,) or hi.shape!=(3,) or not np.isfinite(lo).all() or not np.isfinite(hi).all() or np.any(lo>hi):
        raise ValueError('Finite ordered three-dimensional log-scale box required')
    spread=Interval(float(max(hi)))-Interval(float(min(lo)))
    q=spread.tanh()
    # Treat coefficients as exact binary numbers. Reconstruct exact initial pressure
    # from angular polynomial, avoiding the parent roundoff of stored initial_pressure.
    E=Interval(source.energy0);c2,ct,_=[Interval(float(z)) for z in source.coefficients]
    press=[E*(Interval(1)/3-c2/15+2*ct/15),
           E*(Interval(1)/3-c2/15-2*ct/15),
           E*(Interval(1)/3+2*c2/15)]
    k=source.K+1;coef=Interval(comb(2*k,k))/Interval(4)**k
    tail=coef*q**k/(Interval(1)-q)
    m=( (-2*Interval(float(max(hi)))).exp()+(-2*Interval(float(min(hi)))).exp())/2
    v=Interval(0)
    for a in lo:v=v+Interval(float(a))
    result=[]
    for i in range(3):
        pref=(-2*Interval(float(lo[i]))-v).exp()/m.sqrt()
        bound=2*press[i]*pref*tail
        if bound.lower<0:raise ValueError('Unphysical negative bound')
        result.append(bound)
    return {'bounds':[a.upper for a in result],
            'bounds_lower':[a.lower for a in result], 'q_interval':[q.lower,q.upper],
            'rounding_method':'MPFR_DIRECTED','precision_bits':BITS,
            'input_semantics':'exact binary floating-point values',
            'scope':'analytic ideal-Gauss source truncation; excludes floating GL weight evaluation'}

def propagate_interval(previous,dt,energy,ell_force,h_force):
    p=[as_iv(z) for z in previous]
    h=as_iv(dt);E=as_iv(energy);a=as_iv(ell_force);b=as_iv(h_force)
    if any(z.lower<0 for z in [*p,h,E,a,b]):raise ValueError('Nonnegative comparison inputs required')
    if E.lower<=0:raise ValueError('Strictly positive E required in this channel')
    k=2*E.sqrt();z=k*h
    s=z.sinh();c=z.cosh();cm=2*(z/2).sinh()**2
    return [c*p[0]+s*p[1]/k+a*s/k+b*cm/k**2,
            k*s*p[0]+c*p[1]+a*cm+b*s/k]

@classmethod
def _interval_between(cls,lower,upper):
    a=cls(lower);b=cls(upper)
    if a.lower>b.upper:raise ValueError('Ordered interval endpoints required')
    z=cls._empty();cls._set(z.a,a.a,D);cls._set(z.b,b.b,U)
    return z
Interval.between=_interval_between

def _maxabs(z):
    return max(abs(z.lower),abs(z.upper))

def _bernstein_box_binary(path,i):
    """Outward Bernstein hull of the exact real cubic with stored binary coefficients."""
    coeff=[[Interval(float(v)) for v in row] for row in path.coefficients[i]]
    B=[[coeff[0][k],
        coeff[0][k]+coeff[1][k]/3,
        coeff[0][k]+2*coeff[1][k]/3+coeff[2][k]/3,
        coeff[0][k]+coeff[1][k]+coeff[2][k]+coeff[3][k]] for k in range(6)]
    return [min(v.lower for v in axis) for axis in B], [max(v.upper for v in axis) for axis in B]

def _source_stored_binary(source,ell):
    """Enclose real quadrature formula using exactly the stored float rays/masses.

    It does not itself enclose the unknown *ideal* GL nodes or the continuum sphere.
    """
    b=[(-2*as_iv(v)).exp() for v in ell]
    volume=(-(ell[0]+ell[1]+ell[2])).exp()
    sums=[Interval(0) for _ in range(3)]
    for w,n in zip(source.mass,source.n):
        n2=[Interval(float(v))*Interval(float(v)) for v in n]
        r2=sum((b[i]*n2[i] for i in range(3)),Interval(0))
        r=r2.sqrt(); ww=Interval(float(w))/r
        for i in range(3):sums[i]=sums[i]+ww*b[i]*n2[i]
    return [volume*z for z in sums]

def _hermite_binary_eval(path,i,v):
    """Exact stored binary cubic and its coordinate-time derivative, enclosed."""
    rows=path.coefficients[i]
    h=Interval(float(path.times[i+1]))-Interval(float(path.times[i]))
    if h.lower<=0:raise ValueError('Nonpositive time panel')
    values=[];derivs=[]
    for k in range(6):
        c=[Interval(float(rows[j,k])) for j in range(4)]
        values.append(c[0]+v*(c[1]+v*(c[2]+v*c[3])))
        derivs.append((c[1]+v*(2*c[2]+v*3*c[3]))/h)
    return values,derivs

def residual_binary_interval(source,path,i,subcells=4):
    """All-time semidiscrete ODE defect, including interval arithmetic rounding.

    This uses natural interval evaluation on each CLOSED time subcell; it is
    rigorous for the exact real cubic through the stored binary Hermite
    coefficients and the exact real source formula over the STORED binary
    ray/weight/intensity data. It may be very conservative (dependency).
    """
    if not isinstance(subcells,int) or subcells<1 or subcells>256:
        raise ValueError('subcells must be 1..256')
    lo,hi=_bernstein_box_binary(path,i)
    if any(x<0 for x in lo):raise ValueError('Entire Hermite path must stay in expanding octant')
    dh=0.;dl=0.
    for j in range(subcells):
        v=exact_time_subcell(j,subcells)
        y,yp=_hermite_binary_eval(path,i,v)
        P=_source_stored_binary(source,y[:3])
        theta=y[3]+y[4]+y[5]
        for k in range(3):
            dl=max(dl,_maxabs(yp[k]-y[k+3]))
            dh=max(dh,_maxabs(yp[k+3]+theta*y[k+3]-P[k]))
    return {'ell_defect':dl,'h_defect':dh,'subcells':subcells,
            'path_lower':lo,'path_upper':hi,
            'status':'MPFR_OUTWARD_SEMIDISCRETE_RESIDUAL',
            'source_scope':'stored binary nodes/weights/intensities, not exact ideal GL'}

def audit_binary_path(source,path,subcells=4):
    """Certified rounded residual for semidiscrete model, ideal GL budget separate.

    Time defect is interval-certified *relative to exact stored discrete model*.
    Source ideal quadrature bound uses exact-rule analytic identity, outward MPFR
    numerical evaluation, but does NOT include finite GL node/weight rounding.
    Therefore total continuum geometry certificate is withheld.
    """
    from bianchi.nonperturbative.einstein_error_budget import PolynomialRadiation,HermitePath
    if not isinstance(source,PolynomialRadiation) or not isinstance(path,HermitePath):
        raise TypeError('PolynomialRadiation and HermitePath required')
    time=[Interval(0),Interval(0)];ideal=[Interval(0),Interval(0)];rows=[]
    for i in range(len(path.times)-1):
        d=residual_binary_interval(source,path,i,subcells)
        s=pressure_bound_interval(source,np.asarray(d['path_lower'][:3]),np.asarray(d['path_upper'][:3]))
        dt=Interval(float(path.times[i+1]))-Interval(float(path.times[i]))
        time=propagate_interval(time,dt,Interval(source.energy0),Interval(d['ell_defect']),Interval(d['h_defect']))
        ideal=propagate_interval(ideal,dt,Interval(source.energy0),Interval(0),Interval(max(s['bounds'])))
        rows.append({'panel':i,'time_end':float(path.times[i+1]),'defect':d,
                     'ideal_gauss_source_bound':s['bounds'],
                     'semidiscrete_time_envelope':[a.upper for a in time],
                     'ideal_source_envelope':[a.upper for a in ideal]})
    return {'status':'MPFR_SEMIDISCRETE_INTERVAL_VALIDATED',
            'semidiscrete_time_envelope':[a.upper for a in time],
            'ideal_source_envelope':[a.upper for a in ideal],
            'combined_conditional_upper':[time[i].upper+ideal[i].upper for i in range(2)],
            'combined_continuum_machine_certificate':False,
            'floating_point_path_treated_as_exact_binary_data':True,
            'quadrature_rounding_gap':'OPEN: ideal GL versus stored binary node/weight polynomial moments',
            'rows':rows}

def choose_scoped_budget(source_factory,angular_counts,step_counts,target,*,end=.25,subcells=4):
    """Target selection with typed assurance: semidiscrete yes/no, continuum withheld.

    Only requests combinations until FIRST conditional pass. This controller
    makes no claim of all-instrument certified continuum accuracy.
    """
    from bianchi.nonperturbative.einstein_error_budget import rk4_path
    target=float(target)
    if not math.isfinite(target) or target<=0:raise ValueError('Positive target required')
    attempts=[]
    for n in angular_counts:
        source=source_factory(ntheta=int(n))
        for steps in step_counts:
            path=rk4_path(source,source.initial_state(),end,int(steps),backend='python_oracle')
            result=audit_binary_path(source,path,subcells)
            t=result['semidiscrete_time_envelope'][1]
            ideal=result['ideal_source_envelope'][1]
            record={'ntheta':n,'steps':steps,'time_envelope':t,
                    'ideal_source_envelope':ideal,
                    'conditional_total':t+ideal,
                    'semidiscrete_time_target_met':t<=target,
                    'continuum_machine_admitted':False}
            attempts.append(record)
            if t+ideal<=target:
                return {'status':'CONDITIONAL_SELECTION_NOT_CONTINUUM_CERTIFIED',
                        'target':target,'selected':record,'attempts':attempts}
    return {'status':'NO_CANDIDATE_MET_CONDITIONAL_TARGET',
            'target':target,'selected':None,'attempts':attempts}

# Exact initial degree-four angular polynomial integration.  The normalization
# F0=E0/(4pi)*poly removes pi from all exact polynomial moments.
from fractions import Fraction
from functools import lru_cache
from math import factorial

def _r(v):return Fraction.from_float(float(v))

def exact_component_sum(values):
    """Enclose the exact sum of stored binary values, without float64 pre-summing."""
    return sum((Interval(float(v)) for v in values),Interval(0))


def exact_time_subcell(j,n):
    """Closed exact rational subcell, not binary-rounded j/n endpoints."""
    if not isinstance(j,int) or not isinstance(n,int) or n<1 or not 0<=j<n:
        raise ValueError('Expected integer 0<=j<n and n>=1')
    a=_iv_fraction(Fraction(j,n));b=_iv_fraction(Fraction(j+1,n))
    return Interval.between(a.lower,b.upper)


def _iv_fraction(v):
    v=Fraction(v);a=Interval._empty();b=Interval._empty()
    for dst,n in ((a.a,v.numerator),(a.b,v.numerator),(b.a,v.denominator),(b.b,v.denominator)):
        if _lib.mpfr_set_str(dst.ptr(),str(n).encode('ascii'),10,D if dst in (a.a,b.a) else U):
            raise ValueError('Could not parse rational interval')
    return a/b

@lru_cache(None)
def _spherical_monomial(a,b,c):
    """Exact spherical mean of qx^(2a) qy^(2b) qz^(2c)."""
    def odd(n):
        result=1
        for j in range(1,n+1,2):result*=j
        return result
    return Fraction(odd(2*a-1)*odd(2*b-1)*odd(2*c-1),odd(2*(a+b+c)+1))

def _poly_source_coeffs(source):
    c2,ct,c4=map(_r,source.coefficients)
    return { (0,0,0):1-c2/2+3*c4/8,
             (0,0,1):3*c2/2-30*c4/8,
             (0,0,2):35*c4/8,
             (1,0,0):ct,(0,1,0):-ct }

def _ideal_moment(source,i,a,b,c):
    base=[a,b,c];base[i]+=1
    v=Fraction(0)
    for degree,coeff in _poly_source_coeffs(source).items():
        v+=coeff*_spherical_monomial(*(base[j]+degree[j] for j in range(3)))
    return _r(source.energy0)*v

def _mismatch_coefficients(source,K):
    """Exact rationals: stored discrete polynomial angular moment minus continuum."""
    cache=getattr(source,"_ce1c_exact_mismatch_cache",None)
    if cache is not None and K in cache:return cache[K]
    data={};sq=[[ _r(v)**2 for v in n] for n in source.n]
    masses=list(map(_r,source.mass))
    for j in range(K+1):
        for a in range(j+1):
            for b in range(j-a+1):
                c=j-a-b
                # Squared amplitudes already include the correct direction factors.
                mon=[r[0]**a*r[1]**b*r[2]**c for r in sq]
                for i in range(3):
                    exact=sum((m*r[i]*v for m,r,v in zip(masses,sq,mon)),Fraction(0))
                    data[i,a,b,c]=exact-_ideal_moment(source,i,a,b,c)
    if cache is None:
        cache={};source._ce1c_exact_mismatch_cache=cache
    cache[K]=data
    return data

def _max_lower_upper(a,b):
    z=Interval._empty()
    Interval._set(z.a,a.a if a.lower>=b.lower else b.a,N)
    Interval._set(z.b,a.b if a.upper>=b.upper else b.b,N)
    return z

def source_full_rounding_bound(source,lo,hi,*,max_K=5):
    """Uniform ideal continuum versus exact-real *stored binary* discrete P.

    Split the binomial approximants into an exact rational coefficient mismatch
    (incorporating ALL rounded GL nodes, azimuth nodes, sampled density, weights)
    and rigorously enclosed continuum/stored positive remainders. Each MPFR
    elementary operation is rounded outward. No appeal to perfect float weights.
    Comparison is to the exact-real source function defined by stored binary
    inputs, not to the arbitrary BLAS evaluation order of its float64 RHS.
    """
    lo=np.asarray(lo,float);hi=np.asarray(hi,float)
    if lo.shape!=(3,) or hi.shape!=(3,) or not np.isfinite(lo).all() or not np.isfinite(hi).all() or np.any(lo>hi):
        raise ValueError('Finite ordered three-dimensional box required')
    K=min(int(source.K),int(max_K))
    if K<0:raise ValueError('Insufficient quadrature polynomial degree')
    mismatch=_mismatch_coefficients(source,K)
    blo=[(-2*Interval(float(z))).exp() for z in hi]
    bhi=[(-2*Interval(float(z))).exp() for z in lo]
    mlo=(((-2*Interval(float(max(hi)))).exp())+((-2*Interval(float(min(hi)))).exp()))/2
    mhi=(((-2*Interval(float(max(lo)))).exp())+((-2*Interval(float(min(lo)))).exp()))/2
    m=Interval.between(mlo.lower,mhi.upper)
    b=[Interval.between(blo[i].lower,bhi[i].upper) for i in range(3)]
    ratio=[v/m for v in b]
    summ=Interval.between(exact_component_sum(lo).lower,exact_component_sum(hi).upper)
    v_inv=(-summ).exp()
    q=(Interval(float(max(hi)))-Interval(float(min(lo)))).tanh()
    maxnorm=Fraction(0)
    for n in source.n:
        norm=sum((_r(z)**2 for z in n),Fraction(0))
        maxnorm=max(maxnorm,abs(norm-1))
    qextra=q+_iv_fraction(maxnorm)*max(r.upper for r in ratio)*Interval(1)
    if qextra.upper>=1:raise ValueError('Stored angular-radius series not convergent')
    ck=lambda k: Fraction(comb(2*k,k),4**k)
    # Ideal and stored n_i^2 moments (no scale factors), exact binary inputs.
    sum_mass=[sum((_r(w)*_r(n[i])**2 for w,n in zip(source.mass,source.n)),Fraction(0)) for i in range(3)]
    angular_b=[]
    for i in range(3):
        pref=b[i]*v_inv/m.sqrt()
        mismatch_bound=Interval(0)
        for j in range(K+1):
            dj=sum((ck(k)*(-1)**j*comb(k,j) for k in range(j,K+1)),Fraction(0))
            for a in range(j+1):
                for y in range(j-a+1):
                    c=j-a-y
                    multinomial=factorial(j)//(factorial(a)*factorial(y)*factorial(c))
                    delta=abs(mismatch[i,a,y,c])
                    if delta:
                        mismatch_bound=mismatch_bound+_iv_fraction(delta)*_iv_fraction(abs(dj))*multinomial*ratio[0]**a*ratio[1]**y*ratio[2]**c
        tail=(_iv_fraction(ck(K+1))*qextra**(K+1)/(Interval(1)-qextra))
        remainder=( _iv_fraction(_ideal_moment(source,i,0,0,0))+
                    _iv_fraction(sum_mass[i]))*tail
        upper=(pref*(mismatch_bound+remainder)).upper
        angular_b.append(upper)
    return {'bounds':angular_b,'K_used':K,'q_stored_upper':qextra.upper,
            'input_bits':'exact binary ray/weight/intensity and continuum polynomial coefficients',
            'proof':'exact spherical monomials; exact rational polynomial mismatch; MPFR-directed series tails',
            'floating_arithmetic':'interval MPFR; stored float64 source RHS is modeled as exact-real discrete rule',
            'continuum_source_enclosure':True}


def audit_continuum_binary_path(source,path,subcells=4,max_K=5):
    """Complete a posteriori enclosure of exact continuum ODE vs stored path.

    1. Defect of exact stored binary Hermite cubic relative to *exact-real*
       stored discrete source is enclosed by MPFR intervals on all subcells.
    2. Uniform source discrepancy to continuum uses exact rational mismatch of
       rounded quadrature data and separately bounded positive series tails.
    3. Expanding comparison transports both with MPFR-directed functions.

    The resulting upper bounds include float64 path/weight/source-data effects
    AS THEY APPEAR IN THE RECORDED BINARY DATA. They do not yet include a
    certified bound on acquisition uncertainty in the intended decimal initial
    conditions or a formally machine-checked proof of this implementation.
    """
    from bianchi.nonperturbative.einstein_error_budget import PolynomialRadiation,HermitePath
    if not isinstance(source,PolynomialRadiation) or not isinstance(path,HermitePath):raise TypeError('Invalid inputs')
    t=[Interval(0),Interval(0)];a=[Interval(0),Interval(0)];rows=[]
    for i in range(len(path.times)-1):
        d=residual_binary_interval(source,path,i,subcells)
        src=source_full_rounding_bound(source,np.array(d['path_lower'][:3]),np.array(d['path_upper'][:3]),max_K=max_K)
        dt=Interval(float(path.times[i+1]))-Interval(float(path.times[i]))
        t=propagate_interval(t,dt,Interval(source.energy0),Interval(d['ell_defect']),Interval(d['h_defect']))
        a=propagate_interval(a,dt,Interval(source.energy0),Interval(0),Interval(max(src['bounds'])))
        rows.append({'i':i,'t_end':float(path.times[i+1]),'defect':d,
                     'continuum_source_bound':src['bounds'],
                     'time_envelope':[z.upper for z in t],
                     'source_envelope':[z.upper for z in a]})
    total=[(t[i]+a[i]).upper for i in range(2)]
    return {'status':'DIRECTED_ROUNDED_CONTINUUM_ODE_PATH_ENCLOSURE',
            'time_envelope':[z.upper for z in t],
            'source_envelope':[z.upper for z in a],
            'total_envelope':total,
            'input_semantics':'exact stored binary initial angular polynomial and Hermite path data',
            'model_scope':'finite positive degree-4 angular polynomial, expanding Bianchi I',
            'not_certified':'physical decimal data conversion, general sampled radiation, contracting sector, independent verified software',
            'rows':rows}

def _jet_product(x,y):
    return [sum((x[k-j]*y[j] for j in range(k+1)),Interval(0)) for k in range(4)]

def _jet_exp(a):
    out=[a[0].exp()]+[Interval(0) for _ in range(3)]
    for k in range(1,4):
        out[k]=sum((j*a[j]*out[k-j] for j in range(1,k+1)),Interval(0))/k
    return out

def _taylor_from_binary(path,i,center):
    """Taylor coefficients in coordinate u about a fractional panel center."""
    c=path.coefficients[i]
    h=Interval(float(path.times[i+1]))-Interval(float(path.times[i]))
    if h.lower<=0:raise ValueError('Nonpositive time panel')
    a=[[Interval(float(c[j,k])) for k in range(6)] for j in range(4)]
    return [[sum((comb(j,k)*a[j][r]*center**(j-k) for j in range(k,4)),Interval(0))/h**k
             for r in range(6)] for k in range(4)]

def _jet_source_discrete(source,T):
    """Outward pressure Taylor coefficients of the stored-quadrature source."""
    ell=[[T[k][i] for i in range(3)] for k in range(4)]
    exponent=[-sum((ell[k][i] for i in range(3)),Interval(0)) for k in range(4)]
    b=[_jet_exp([-2*ell[k][i] for k in range(4)]) for i in range(3)]
    out=[[Interval(0) for i in range(3)] for k in range(4)]
    numerator=[_jet_exp([exponent[k]-2*ell[k][i] for k in range(4)]) for i in range(3)]
    for w,n in zip(source.mass,source.n):
        square=[Interval(float(q))*Interval(float(q)) for q in n]
        Z=[sum((square[i]*b[i][k] for i in range(3)),Interval(0)) for k in range(4)]
        if Z[0].lower<=0:raise ValueError('Nonpositive ray energy square')
        ratio=[Interval(0)]+[Z[k]/Z[0] for k in range(1,4)]
        r2=_jet_product(ratio,ratio);r3=_jet_product(r2,ratio)
        root=[Interval(int(k==0))-ratio[k]/2+3*r2[k]/8-5*r3[k]/16 for k in range(4)]
        scale=Interval(float(w))/Z[0].sqrt()
        for i in range(3):
            p=_jet_product(numerator[i],root)
            for k in range(4):out[k][i]=out[k][i]+scale*square[i]*p[k]
    return out

def _bernstein_derivative_max(path,i,k):
    """Absolute bound of kth u derivative of 6 component cubic over panel."""
    c=path.coefficients[i];deg=3-k
    h=Interval(float(path.times[i+1]))-Interval(float(path.times[i]))
    caps=[]
    for j in range(6):
        power=[Interval(float(c[k+a,j]))*(factorial(k+a)//factorial(a))/h**k
               for a in range(deg+1)]
        ctrl=[]
        for a in range(deg+1):
            ctrl.append(sum((power[z]*Fraction(comb(a,z),comb(deg,z))
                             for z in range(a+1)),Interval(0)))
        caps.append(max(_maxabs(z) for z in ctrl))
    return [Interval(z) for z in caps]

def stored_ray_energy_majorant(source):
    """Fresh outward bound for CURRENT stored positive ray mass times max ray norm.

    Covers float64 summation of sampled_energy0 and |n| != 1 from generated
    binary angle directions without modifying the source or quadrature weights.
    """
    mass=exact_component_sum(source.mass)
    if mass.lower<0:raise ValueError('Nonnegative sampled ray masses required')
    norm=max(sum((_r(x)**2 for x in ray),Fraction()) for ray in source.n)
    cap=(mass*_iv_fraction(norm).sqrt()).upper
    return cap


def _p4_interval(source,H,G):
    # Parent CE1-B bound with each operation directed outward. H,G are
    # nonnegative envelopes on absolute derivatives of ell and h.
    E=Interval(stored_ray_energy_majorant(source)); H1,H2,H3=H;G1,G2,G3=G
    m1=2*H1;m2=2*H2+4*H1**2;m3=2*H3+12*H1*H2+8*H1**3
    m4=16*H1*H3+12*H2**2+48*H1**2*H2+16*H1**4
    b1=m1/2;b2=m2/2+3*m1**2/4
    b3=m3/2+9*m1*m2/4+15*m1**3/8
    b4=m4/2+3*m1*m3+9*m2**2/4+45*m1**2*m2/4+105*m1**4/16
    a1=5*H1;a2=5*H2+25*H1**2
    a3=5*H3+75*H1*H2+125*H1**3
    a4=100*H1*H3+75*H2**2+750*H1**2*H2+625*H1**4
    return E*(a4+4*a3*b1+6*a2*b2+4*a1*b3+b4)+24*G3*G1+18*G2**2

def residual_taylor_mpfr(source,path,i,subcells=4):
    """Whole-panel 3rd Taylor/4th remainder with directed-rounding MPFR.

    Assumes CE1-B's analytic fourth-derivative majorant, checked independently.
    Computes coefficient intervals of the reconstructed binary cubic and the
    exact-real discrete source of stored binary ray inputs. Unlike natural
    interval evaluation, dependencies cancel analytically through order three.
    """
    lo,hi=_bernstein_box_binary(path,i)
    if min(lo)<0:raise ValueError('Entire reconstructed path must be expanding')
    dt=Interval(float(path.times[i+1]))-Interval(float(path.times[i]))
    ds=[_bernstein_derivative_max(path,i,k) for k in (1,2,3)]
    H=[Interval(max(z.upper for z in v[:3])) for v in ds]
    G=[Interval(max(z.upper for z in v[3:])) for v in ds]
    R4=_p4_interval(source,H,G)
    radius=dt/(2*subcells)
    dl=Interval(0);dh=Interval(0)
    for j in range(subcells):
        T=_taylor_from_binary(path,i,Interval(2*j+1)/Interval(2*subcells))
        P=_jet_source_discrete(source,T)
        theta=[sum(T[k][i] for i in range(3,6)) for k in range(4)]
        defect_l=[];defect_h=[]
        for k in range(4):
            for i2 in range(3):
                lhs=(k+1)*T[k+1][i2] if k<3 else Interval(0)
                defect_l.append((k,i2,lhs-T[k][i2+3]))
                rhs=(k+1)*T[k+1][i2+3] if k<3 else Interval(0)
                defect_h.append((k,i2,rhs+sum((theta[q]*T[k-q][i2+3] for q in range(k+1)),Interval(0))-P[k][i2]))
        ql=Interval(0);qh=Interval(0)
        for k in range(4):
            ql=ql+Interval(max(_maxabs(z) for q,_,z in defect_l if q==k))*radius**k
            qh=qh+Interval(max(_maxabs(z) for q,_,z in defect_h if q==k))*radius**k
        qh=qh+R4*radius**4/24
        if ql.upper>dl.upper:dl=ql
        if qh.upper>dh.upper:dh=qh
    return {'ell_defect':dl.upper,'h_defect':dh.upper,
            'fourth_derivative_bound':R4.upper,
            'path_lower':lo,'path_upper':hi,
            'subcells':subcells,
            'status':'MPFR_OUTWARD_TAYLOR3_ANALYTIC4_REMAINDER'}

def audit_continuum_taylor(source,path,subcells=4,max_K=5,initial_h_error=0.0):
    """Rounding-enclosed full ODE-vs-binary-path result for scoped initial data."""
    t=[Interval(0),Interval(initial_h_error)];a=[Interval(0),Interval(0)];rows=[]
    for i in range(len(path.times)-1):
        d=residual_taylor_mpfr(source,path,i,subcells)
        s=source_full_rounding_bound(source,d['path_lower'][:3],d['path_upper'][:3],max_K=max_K)
        dt=Interval(float(path.times[i+1]))-Interval(float(path.times[i]))
        t=propagate_interval(t,dt,Interval(source.energy0),Interval(d['ell_defect']),Interval(d['h_defect']))
        a=propagate_interval(a,dt,Interval(source.energy0),Interval(0),Interval(max(s['bounds'])))
        rows.append({'i':i,'time_end':float(path.times[i+1]),'defect':d,
                     'continuum_source_upper':s['bounds'],
                     'time_envelope':[x.upper for x in t],
                     'source_envelope':[x.upper for x in a]})
    return {'status':'DIRECTED_ROUNDED_SCOPED_ODE_PATH_ENCLOSURE',
            'rounding_method':'GNU MPFR RNDD/RNDU,192bits',
            'time_envelope':[x.upper for x in t],
            'source_envelope':[x.upper for x in a],
            'total_envelope':[(t[i]+a[i]).upper for i in range(2)],
            'is_formal_verification_of_python_implementation':False,
            'initial_h_error_bound':initial_h_error,
            'input_scope':'exact stored binary initial polynomial and stored cubic path; expanding sector',
            'rows':rows}

def exact_polynomial_positivity(source):
    """Exact rational lower bound for F0/(E0/4pi), over the entire sphere."""
    c2,ct,c4=map(_r,source.coefficients)
    a=Fraction(35,8)*c4
    b=Fraction(3,2)*c2-Fraction(30,8)*c4+abs(ct)
    d=Fraction(1)-c2/2+3*c4/8-abs(ct)
    vals=[d,a+b+d]
    if a>0:
        v=-b/(2*a)
        if 0<v<1:vals.append(a*v*v+b*v+d)
    minimum=min(vals)
    return {'strictly_positive':minimum>0,'min_lower':_iv_fraction(minimum).lower,
            'exact_binary_coefficients':True}

def constraint_initial_h_error(source,path,reference_shear=(.2,-.13)):
    """Bound mismatch to exact Hamiltonian-admissible initial state.

    Reference chooses sx,sy as exact stored binary inputs and sz=-sx-sy
    exactly. The resulting h0 satisfies the exact continuum constraint,
    unlike the generally nonzero roundoff defect of float64 square roots.
    """
    E=Interval(source.energy0)
    sx,sy=[Interval(float(v)) for v in reference_shear]
    sh=[sx,sy,-(sx+sy)]
    hbar=((E+sum((v*v for v in sh),Interval(0))/2)/3).sqrt()
    err=max(_maxabs(Interval(float(path.states[0,3+i]))-(hbar+sh[i])) for i in range(3))
    return {'h_error_bound':err,'shear_trace_constraint':'exact',
            'reference_definition':'sx,sy are stored binaries; sz=-sx-sy; hbar from exact Hamiltonian root'}

def select_geometry_tolerance(source_factory,candidates,target_h,*,end=1.,subcells=4,max_K=5,
                              reference_shear=(.2,-.13)):
    """Stop on first outward interval enclosure meeting requested geometry rate.

    Work budget is explicit candidates [(ntheta,rk4_steps),...], no hidden
    tolerance or input change. The state/hull is exact reconstructed binary
    path versus the continuum ODE with exact constraint-compatible initial
    geometry specified by the first two shear components.
    """
    from bianchi.nonperturbative.einstein_error_budget import rk4_path
    target=Interval.decimal(str(target_h));out=[]
    if target.lower<=0:raise ValueError('Positive geometry tolerance required')
    for n,steps in candidates:
        s=source_factory(ntheta=int(n))
        if not exact_polynomial_positivity(s)['strictly_positive']:
            raise ValueError('Initial angular continuum polynomial is not positive')
        p=rk4_path(s,s.initial_state(),float(end),int(steps),backend='python_oracle')
        delta=constraint_initial_h_error(s,p,reference_shear)
        report=audit_continuum_taylor(s,p,subcells,max_K,delta['h_error_bound'])
        record={'ntheta':int(n),'nphi':s.nphi,'steps':int(steps),
                'rounding_enclosed_rate_upper':report['total_envelope'][1],
                'source_upper':report['source_envelope'][1],
                'time_and_initial_upper':report['time_envelope'][1],
                'initial_h_error_upper':delta['h_error_bound'],
                'meets_target':report['total_envelope'][1]<=target.lower,
                'scope':'continuum ODE vs recorded binary Hermite path, exact initial shear convention'}
        out.append(record)
        if record['meets_target']:
            return {'status':'SCOPED_MPFR_ENCLOSED_TOLERANCE_MET',
                    'target_h':str(target_h),'selected':record,'attempts':out,
                    'production_ready':False}
    return {'status':'NO_CANDIDATE_MEETS_INTERVAL_TARGET',
            'target_h':str(target_h),'selected':None,'attempts':out,
            'production_ready':False}
