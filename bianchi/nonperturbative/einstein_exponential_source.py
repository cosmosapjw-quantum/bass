"""CE1-E: nonpolynomial initial angular density and rigorous pressure quadrature bound.

Admitted physical model: positive G(q)*exp(lambda*q_z^2), not a Taylor
truncation; lambda>=0, reflection-even massless collisionless diagonal Bianchi I,
all-direction expanding, Lambda=0.  E0 is the amplitude, NOT the actual initial
energy after exponential dressing.  Stored numerical ray masses are the *actual*
binary64 outputs of the parent quadrature, multiplied by a binary64 exponential.

The certificate compares the exact continuum source to the exact-real function
defined by the stored binary64 masses, rays and coefficient data.  Polynomial
moment mismatch is computed with exact fractions; all bounds involving positive
ranges, transcendental functions and divisions use outward MPFR192 intervals.
This is not a formal verification of Python/MPFR or decimal acquisition.
"""
from __future__ import annotations
from fractions import Fraction
from functools import lru_cache
from math import comb, factorial
import numpy as np

from .einstein_error_budget import PolynomialRadiation, _real, _oracle
from .einstein_input_enclosure import _polynomial_exact_min
from .einstein_interval import (Interval, _iv_fraction, _spherical_monomial,
                                _poly_source_coeffs, propagate_interval)


def _r(x):
    return Fraction.from_float(float(x))


def _maxabs(a):
    return max(abs(a.lower),abs(a.upper))


def _positive_geometric_box(lower,upper):
    lo=np.asarray(lower,float);hi=np.asarray(upper,float)
    if lo.shape!=(3,) or hi.shape!=(3,) or not np.isfinite(lo).all() or not np.isfinite(hi).all():
        raise ValueError('Finite three-dimensional log-scale box required')
    if np.any(lo<0) or np.any(lo>hi):
        raise ValueError('Require nonnegative ordered expanding log-scale box')
    return lo,hi


class ExponentialRadiation:
    """Entire positive nonpolynomial angular source; not a finite-l hierarchy.

    F0(q)=E_amplitude/(4*pi) G(q) exp(lambda*q_z^2), lambda>=0.
    The baseline stored masses preserve existing GL/phi weights exactly.
    """
    def __init__(self,energy=.9,coefficients=(.6,.25,.2),lambda_exp=.2,
                 ntheta=8,nphi=None,*,backend=None):
        _oracle(backend)
        lam=float(lambda_exp)
        if not np.isfinite(lam) or not 0<=lam<=1.0:
            raise ValueError('Nonnegative finite exponent strength <=1 required')
        base=PolynomialRadiation(energy,coefficients,ntheta,nphi,backend='python_oracle')
        if _polynomial_exact_min(*map(_r,base.coefficients))<=0:
            raise ValueError('Strictly positive reference angular polynomial required')
        exponent=np.exp(lam*base.n[:,2]**2)
        mass=base.mass*exponent
        if not np.isfinite(mass).all() or np.any(mass<=0):
            raise ValueError('Positive finite stored angular masses required')
        self.base=base;self.amplitude=base.energy0;self.coefficients=base.coefficients
        self.lambda_exp=lam;self.n=base.n;self.ntheta=base.ntheta
        self.nphi=base.nphi;self.weights=base.weights;self.mass=mass.copy()
        self.mass.setflags(write=False)
        self.energy0=self.moments(np.zeros(3))[0]

    def moments(self,ell):
        e=_real(ell,(3,));b=np.exp(-2*e);r=np.sqrt((self.n*self.n)@b)
        v=np.exp(-e.sum());return float(v*(self.mass@r)),v*b*np.einsum('j,ji->i',self.mass/r,self.n*self.n)

    def rhs(self,t,y):
        y=_real(y,(6,));h=y[3:]
        return np.r_[h,-h.sum()*h+self.moments(y[:3])[1]]

    def initial_state(self,shear=(.2,-.13,-.07)):
        s=_real(shear,(3,));scale=max(np.finfo(float).tiny,float(np.max(abs(s))))
        if abs(s.sum())>2e-12*scale:
            raise ValueError('Exactly constrained trace-free shear to within storage precision required')
        h=np.sqrt((self.energy0+0.5*np.dot(s,s))/3)+s
        if np.any(h<0):raise ValueError('All directional expansions must be nonnegative')
        return np.r_[np.zeros(3),h]


@lru_cache(maxsize=None)
def _moment_monomial(alpha):
    return _spherical_monomial(*alpha)


def _spherical_poly_moment(base,lambda_binary,i,exponents,exp_order):
    """Exact mean of G q_i^2 q^(2exponents) sum(lambda*qz^2)^n/n!."""
    coeffs=_poly_source_coeffs(base)
    result=Fraction()
    for k in range(exp_order+1):
        lam_factor=lambda_binary**k/factorial(k)
        for deg,coef in coeffs.items():
            powers=[exponents[j]+deg[j]+int(i==j)+k*int(j==2) for j in range(3)]
            result+=coef*lam_factor*_moment_monomial(tuple(powers))
    return _r(base.energy0)*result


def _spherical_energy_poly(base,lam,order):
    coef=_poly_source_coeffs(base);out=Fraction()
    for n in range(order+1):
        factor=lam**n/factorial(n)
        for deg,g in coef.items():
            out+=g*factor*_moment_monomial((deg[0],deg[1],deg[2]+n))
    return _r(base.energy0)*out


@lru_cache(maxsize=512)
def _polynomial_data(masses_tuple,ray_tuple,base_energy,coeffs,lambda_float,geom_order,exp_order):
    """Exact rational polynomial moments of ideal sphere minus stored binary rule.

    Inputs are tuples of binary float objects (only existing stored data).
    The result is cached across different geometry boxes and validation points.
    """
    class Plain:
        energy0=base_energy
        coefficients=np.array(coeffs)
    base=Plain()
    lam=_r(lambda_float)
    n=len(masses_tuple)
    rays=[[ _r(q)**2 for q in row] for row in ray_tuple]
    masses=[_r(w) for w in masses_tuple]
    rpow=[[[Fraction(1)]*(geom_order+1) for _ in range(3)] for _ in range(n)]
    exp_poly=[]
    for j in range(n):
        for i in range(3):
            for k in range(1,geom_order+1):rpow[j][i][k]=rpow[j][i][k-1]*rays[j][i]
        zz=rays[j][2];term=Fraction(1);T=term
        for k in range(1,exp_order+1):
            term*=lam*zz/k;T+=term
        exp_poly.append(T)
    mismatches={};continuum_zero=[];discrete_zero=[]
    for i in range(3):
        for a in range(geom_order+1):
            for b in range(geom_order-a+1):
                for c in range(geom_order-a-b+1):
                    p=(a,b,c)
                    cont=_spherical_poly_moment(base,lam,i,p,exp_order)
                    disc=sum((masses[j]*exp_poly[j]*rays[j][i]*rpow[j][0][a]
                              *rpow[j][1][b]*rpow[j][2][c] for j in range(n)),Fraction())
                    mismatches[i,a,b,c]=cont-disc
                    if a==b==c==0:
                        continuum_zero.append(cont);discrete_zero.append(disc)
    return {'mismatch':mismatches,'cont0':continuum_zero,'disc0':discrete_zero,
            'exp_poly':exp_poly,'rays_squared':rays,'mass_binary':masses}


def _coeff_data(source,geom_order,exp_order):
    return _polynomial_data(tuple(float(x) for x in source.base.mass),
                            tuple(tuple(float(q) for q in row) for row in source.n),
                            float(source.base.energy0),tuple(map(float,source.coefficients)),
                            float(source.lambda_exp),int(geom_order),int(exp_order))


def _radius_norm(source,dat):
    norm=[sum(x,Fraction()) for x in dat['rays_squared']]
    return min(norm),max(norm)


def _positive_remainders(source,order):
    lam=Interval(source.lambda_exp)
    return lam.exp()*lam**(order+1)/factorial(order+1)


def _pressure_fixed_order(source,lower,upper,*,exp_order=8,geom_order=5):
    """MPFR-outward uniform pressure difference: continuum minus stored rule.

    Source model is the *nontruncated* positive exponential. The two polynomial
    expansions are proof devices only. No assumption of ideal GL exactness for
    the stored binary weights or non-unit ray norms is made.
    """
    if not isinstance(source,ExponentialRadiation):raise TypeError('Expected ExponentialRadiation')
    lo,hi=_positive_geometric_box(lower,upper)
    if not isinstance(exp_order,int) or exp_order<0 or exp_order>16 or not isinstance(geom_order,int) or geom_order<0 or geom_order>9:
        raise ValueError('Exponential/geometric truncation order outside supported range')
    dat=_coeff_data(source,geom_order,exp_order)
    norm_min,norm_max=_radius_norm(source,dat)
    bmin=(-2*Interval(float(max(hi)))).exp()
    bmax=(-2*Interval(float(min(lo)))).exp()
    m=(bmin+bmax)/2
    if m.lower<=0:raise ValueError('Nonpositive midpoint of energy-square range')
    tmin=bmin/m;tmax=bmax/m
    qnormlo=_iv_fraction(norm_min);qnormhi=_iv_fraction(norm_max)
    zr=Interval(1)-Interval.between((tmin*qnormlo).lower,(tmax*qnormhi).upper)
    rho=Interval(max(_maxabs(Interval(1)-tmin),_maxabs(Interval(1)-tmax),_maxabs(zr)))
    if rho.upper>=1:raise ValueError('Geometric binomial series is not uniformly convergent')
    tail=(_iv_fraction(Fraction(comb(2*(geom_order+1),geom_order+1),4**(geom_order+1)))
          *rho**(geom_order+1)/(Interval(1)-rho))
    coeffs=[sum((Fraction(comb(2*k,k),4**k)*(-1)**j*comb(k,j) for k in range(j,geom_order+1)),Fraction())
            for j in range(geom_order+1)]
    # Componentwise upper |b_i/(V sqrt(m))| and positive ratios.
    v_inv=(-sum((Interval(float(z)) for z in lo),Interval(0))).exp()
    pref=[(-2*Interval(float(lo[i]))).exp()*v_inv/m.sqrt() for i in range(3)]
    ratio=[(-2*Interval(float(lo[i]))).exp()/m for i in range(3)]
    lamtail=_positive_remainders(source,exp_order)
    ncap=_iv_fraction(norm_max).sqrt()
    discrepancies=sum((abs(_r(w)-mass*TN) for w,mass,TN in zip(source.mass,dat['mass_binary'],dat['exp_poly'])),Fraction())
    # Exact stored sample exponential/product rounding and omitted exp tail.
    sample_b=(ncap*_iv_fraction(discrepancies)).upper
    bound=[];parts=[]
    for i in range(3):
        mismatch=Interval(0)
        for j in range(geom_order+1):
            dj=abs(coeffs[j]);
            if not dj:continue
            for a in range(j+1):
                for b in range(j-a+1):
                    c=j-a-b
                    d=abs(dat['mismatch'][i,a,b,c])
                    if not d:continue
                    factor=_iv_fraction(dj*d*Fraction(factorial(j),factorial(a)*factorial(b)*factorial(c)))
                    mismatch=mismatch+factor*ratio[0]**a*ratio[1]**b*ratio[2]**c
        poly=(pref[i]*mismatch)
        geom=pref[i]*tail*_iv_fraction(dat['cont0'][i]+dat['disc0'][i])
        expo=Interval(source.amplitude)*lamtail+Interval(sample_b)
        total=poly+geom+expo
        bound.append(total.upper)
        parts.append({'polynomial_mismatch':poly.upper,'geometry_tail':geom.upper,
                      'exponential_continuum_tail_and_stored_sample_residual':expo.upper})
    return {'status':'MPFR_OUTWARD_NONPOLYNOMIAL_PRESSURE_BOUND',
            'continuum_source_enclosure':True,
            'pressure_upper':bound,'bound_max':max(bound),
            'parts':parts,'rho_upper':rho.upper,
            'exp_order':exp_order,'geom_order':geom_order,
            'lambda':source.lambda_exp,
            'mass_semantics':'exact recorded binary64 masses and rays compared against exact continuum G*exp',
            'physical_model_truncated':False,'production_ready':False}


def certified_nonpolynomial_pressure(source,lower,upper,*,exp_order=8,geom_order=5):
    """Best of independently valid outward enclosures with k<=geom_order.

    Higher k is not always more accurate: signed high-degree polynomial
    mismatch may grow as a consequence of the exact stored GL sampling.
    Selecting the minimum of separately proved bounds is rigorous.
    """
    if not isinstance(geom_order,int) or geom_order<0 or geom_order>9:
        raise ValueError('Maximum geom_order outside supported range')
    candidates=[_pressure_fixed_order(source,lower,upper,exp_order=exp_order,geom_order=k)
                for k in range(geom_order+1)]
    chosen=min(candidates,key=lambda a:a['bound_max'])
    return {**chosen,'requested_max_geom_order':geom_order,
            'all_geom_order_bounds':[r['bound_max'] for r in candidates],
            'adaptive_order':'MINIMUM_OF_INDEPENDENT_VALID_BOUNDS'}


def certified_initial_energy(source,*,exp_order=8):
    """Rigorous initial E_continuum versus binary64 stored source.energy0."""
    if not isinstance(source,ExponentialRadiation):raise TypeError('Expected ExponentialRadiation')
    if not isinstance(exp_order,int) or exp_order<0 or exp_order>16:raise ValueError('Unsupported exp_order')
    dat=_coeff_data(source,0,exp_order)
    lam=_r(source.lambda_exp);E_cont=_spherical_energy_poly(source.base,lam,exp_order)
    E_Q_poly=sum((w*t for w,t in zip(dat['mass_binary'],dat['exp_poly'])),Fraction())
    const_mismatch=_iv_fraction(abs(E_cont-E_Q_poly))
    continuum_tail=Interval(source.amplitude)*_positive_remainders(source,exp_order)
    norm2=[sum(row,Fraction()) for row in dat['rays_squared']]
    normcap=_iv_fraction(max(norm2)).sqrt()
    samplediff=sum((abs(_r(w)-mass*TN) for w,mass,TN in zip(source.mass,dat['mass_binary'],dat['exp_poly'])),Fraction())
    sampletail=normcap*_iv_fraction(samplediff)
    # |sqrt(norm2)-1| <= |norm2-1| for norm2>=0.
    normterm=sum((dat['mass_binary'][i]*dat['exp_poly'][i]*abs(n2-1)
                  for i,n2 in enumerate(norm2)),Fraction())
    # Exact-real sampled mass*sqrt(norm2) minus binary64 sampled-energy result:
    exact_sum=sum((Interval(float(w))*_iv_fraction(n2).sqrt()
                   for w,n2 in zip(source.mass,norm2)),Interval(0))
    binary_energy_gap=_maxabs(exact_sum-Interval(source.energy0))
    total=const_mismatch+continuum_tail+sampletail+_iv_fraction(normterm)+Interval(binary_energy_gap)
    return {'status':'MPFR_OUTWARD_INITIAL_ENERGY_BOUND',
            'energy_error_upper':total.upper,
            'parts':{'polynomial_mass_mismatch':const_mismatch.upper,
                     'continuum_exp_remainder':continuum_tail.upper,
                     'stored_exponential_and_product_residual':sampletail.upper,
                     'stored_ray_norm_residual':_iv_fraction(normterm).upper,
                     'binary_energy_sum_roundoff':binary_energy_gap},
            'continuum_energy_lower':(Interval(source.energy0)-total).lower,
            'continuum_energy_upper':(Interval(source.energy0)+total).upper,
            'production_ready':False}


def certified_coupled_geometry(source,*,end=.08,exp_order=8,geom_order=5,
                               shear=(.2,-.13,-.07)):
    """Conditional finite-time Bianchi-I continuum vs stored-source estimate.

    Uses all-expanding positive-source bounds, a computed geometric hull,
    pressure quadrature source bound and separate initial Hamiltonian error.
    Full radiation dynamics remains nonlinear. No discrete RK time error included.
    """
    if not isinstance(source,ExponentialRadiation):raise TypeError('Expected ExponentialRadiation')
    T=float(end)
    if not np.isfinite(T) or not 0<T<=0.2:raise ValueError('Pilot end time must be in (0,0.2]')
    s=np.asarray(shear,float)
    if s.shape!=(3,) or abs(s.sum())>1e-14:raise ValueError('Trace-free three shear components required')
    energy=certified_initial_energy(source,exp_order=exp_order)
    ebox=Interval.between(energy['continuum_energy_lower'],energy['continuum_energy_upper'])
    if ebox.lower<=0:raise ValueError('Positive continuum initial energy not certified')
    # The continuum constraint uses exact binary sx,sy and sz=-(sx+sy).
    # A separate stored float64 sz may differ by one ulp; the initial
    # geometric error interval includes that difference rather than clipping.
    sx=_r(s[0]);sy=_r(s[1]);si=[_iv_fraction(sx),_iv_fraction(sy),_iv_fraction(-(sx+sy))]
    hbar=((ebox+sum((q*q for q in si),Interval(0))/2)/3).sqrt()
    hcont=[hbar+q for q in si]
    stored=source.initial_state(s)[3:]
    d0=max(_maxabs(z-Interval(float(hi))) for z,hi in zip(hcont,stored))
    if any(x.lower<0 for x in hcont) or any(x<0 for x in stored):
        raise ValueError('Both continuum and discrete initial expansions must be nonnegative')
    Emax=max(energy['continuum_energy_upper'],source.energy0)
    # h_i'=-theta h_i+p_i <= E_initial, and ell_i'=h_i.
    box=[]
    for z,hstored in zip(hcont,stored):
        h0=max(z.upper,float(hstored)); hi=Interval(h0)*Interval(T)+Interval(Emax)*Interval(T)**2/2
        box.append(hi.upper)
    src=certified_nonpolynomial_pressure(source,[0.,0.,0.],box,exp_order=exp_order,geom_order=geom_order)
    prop=propagate_interval([Interval(0),Interval(d0)],Interval(T),Interval(Emax),Interval(0),Interval(src['bound_max']))
    return {'status':'SCOPED_NONPOLYNOMIAL_COUPLED_ENCLOSURE',
            'u_end':T,'geometry_h_upper':prop[1].upper,'geometry_ell_upper':prop[0].upper,
            'source_h_upper':propagate_interval([Interval(0),Interval(0)],Interval(T),Interval(Emax),Interval(0),Interval(src['bound_max']))[1].upper,
            'initial_rate_upper':d0,'initial_shear_reference':'EXACT_BINARY_SX_SY_TRACEFREE',
            'source_pressure_upper':src['bound_max'],
            'source_certificate':src,'energy_certificate':energy,'geometry_box_upper':box,
            'time_integration_error_included':False,
            'assurance':'exact-real stored-source versus continuum, not RK4 path error',
            'production_ready':False}
