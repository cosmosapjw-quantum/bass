"""CE1-F: rigorous mean-square-ray quadrature for positive angular-cell radiation.

Each *physical* angular cell has exact rational total energy and constant density
in (mu=|q_z|, t=2/pi atan(|q_y/q_x|)) on the first octant, reflected in all eight
coordinate octants. Cell jumps are part of the model. Refinement divides these
original cells and their exact energy, changing the quadrature only.

Only the diagonal, reflection-even, massless collisionless Einstein-Vlasov source
is modeled. Numerical rays have barycentric x_i=E_C[q_i²], not midpoint angles.
MPFR192 directed bounds enclose continuum-vs-exact-real stored binary quadrature;
float64 ODE evaluator/integrator roundoff is NOT included in the geometry bound.
"""
from __future__ import annotations
import ctypes
from fractions import Fraction
import math
import numpy as np
from .einstein_interval import Interval, _iv_fraction, propagate_interval
from . import einstein_interval as ei

# MPFR directed trig on rational first-octant angular boundaries.
ei._lib.mpfr_const_pi.argtypes = [ei._P, ctypes.c_int]
ei._lib.mpfr_const_pi.restype = ctypes.c_int
ei._lib.mpfr_sin.argtypes = [ei._P, ei._P, ctypes.c_int]
ei._lib.mpfr_sin.restype = ctypes.c_int
ei._lib.mpfr_cos.argtypes = [ei._P, ei._P, ctypes.c_int]
ei._lib.mpfr_cos.restype = ctypes.c_int
_PI = Interval._empty()
ei._lib.mpfr_const_pi(_PI.a.ptr(),ei.D)
ei._lib.mpfr_const_pi(_PI.b.ptr(),ei.U)


def _fraction(v):
    if not isinstance(v,str):
        raise ValueError('Exact decimal strings required for angular boundaries and energies')
    try:return Fraction(v)
    except (ValueError,ZeroDivisionError) as exc:raise ValueError('Invalid exact rational decimal') from exc


def _maxabs(v):return max(abs(v.lower),abs(v.upper))


def _clamp_known_unit(x):
    """Intersect outward interval with analytically proved physical range [0,1]."""
    a=max(0.,x.lower);b=min(1.,x.upper)
    if a>b:raise ArithmeticError('Physical trigonometric unit interval was lost')
    return Interval.between(a,b)


def _trig_pi(t,fn):
    """Directed sin(pi*t) or cos(pi*t) at exact rational t in [0,1]."""
    if t<0 or t>1:raise ValueError('First-octant angle endpoint out of range')
    if fn=='sin':
        if t==0 or t==1:return Interval(0)
        if t==Fraction(1,2):return Interval(1)
    else:
        if t==0:return Interval(1)
        if t==1:return Interval(-1)
        if t==Fraction(1,2):return Interval(0)
    rad=_PI*_iv_fraction(t)
    out=Interval._empty();call=getattr(ei._lib,'mpfr_'+fn)
    monotone_up=(fn=='sin' and t<Fraction(1,2))
    if monotone_up:
        call(out.a.ptr(),rad.a.ptr(),ei.D);call(out.b.ptr(),rad.b.ptr(),ei.U)
    else:
        call(out.a.ptr(),rad.b.ptr(),ei.D);call(out.b.ptr(),rad.a.ptr(),ei.U)
    return out


def _cos_sq(t):return _clamp_known_unit((Interval(1)+_trig_pi(t,'cos'))/2)


def _sin_sq(t):return _clamp_known_unit((Interval(1)-_trig_pi(t,'cos'))/2)


def _cell_means_ranges(mu0,mu1,t0,t1):
    """Directed barycentric q_i² and positive coordinate ranges on first octant."""
    if not (0<=mu0<mu1<=1 and 0<=t0<t1<=1):raise ValueError('Nondegenerate angular cell required')
    mz=_iv_fraction((mu0**2+mu0*mu1+mu1**2)/3)
    c=(Interval(1)/2 + (_trig_pi(t1,'sin')-_trig_pi(t0,'sin'))/(2*_PI*_iv_fraction(t1-t0)))
    c=_clamp_known_unit(c)
    transverse=Interval(1)-mz
    mean=[_clamp_known_unit(transverse*c),_clamp_known_unit(transverse*(Interval(1)-c)),mz]
    ranges=[
        (_clamp_known_unit((_iv_fraction(1-mu1**2)*_cos_sq(t1))),
         _clamp_known_unit((_iv_fraction(1-mu0**2)*_cos_sq(t0)))),
        (_clamp_known_unit((_iv_fraction(1-mu1**2)*_sin_sq(t0))),
         _clamp_known_unit((_iv_fraction(1-mu0**2)*_sin_sq(t1)))),
        (_iv_fraction(mu0**2),_iv_fraction(mu1**2)),
    ]
    # Each tuple stores low and upper bounding intervals rather than point estimates.
    lower=[v[0].lower for v in ranges];upper=[v[1].upper for v in ranges]
    if any(a<0 or b>1 or a>b for a,b in zip(lower,upper)):
        raise ArithmeticError('Failed positive cell direction range')
    return mean,lower,upper


class TabulatedRadiation:
    """Positive exact-decimal angular cell energies with implicit octant reflection."""
    physical_representation='EIGHT_REFLECTED_PIECEWISE_CONSTANT_CELLS'
    def __init__(self,edges_mu,edges_az,energies,refinement=1,*,backend=None,**unexpected):
        if backend!='python_oracle':raise ValueError("Explicit backend='python_oracle' required")
        if unexpected:raise ValueError('Unsupported tabular input: '+','.join(unexpected))
        em=tuple(map(_fraction,edges_mu));et=tuple(map(_fraction,edges_az))
        if len(em)<2 or len(et)<2 or em[0]!=0 or em[-1]!=1 or et[0]!=0 or et[-1]!=1:
            raise ValueError('Finite first-octant partitions must span [0,1]')
        if any(b<=a for e in (em,et) for a,b in zip(e[:-1],e[1:])):
            raise ValueError('Strictly ordered first-octant edges required')
        if not isinstance(refinement,int) or isinstance(refinement,bool) or not 1<=refinement<=8:
            raise ValueError('refinement must be an integer 1..8')
        if len(energies)!=len(em)-1 or any(len(row)!=len(et)-1 for row in energies):
            raise ValueError('Angular cell energy shape must match partitions')
        W=[[ _fraction(str(x)) if isinstance(x,str) else _fraction(x) for x in row] for row in energies]
        if any(x<0 for row in W for x in row):raise ValueError('Nonnegative cell energies required')
        total=sum((v for row in W for v in row),Fraction())
        if total<=0:raise ValueError('Positive total cell energy required')
        self.exact_energy=total
        self.original_cells=tuple(((em[i],em[i+1]),(et[j],et[j+1]),W[i][j])
                                  for i in range(len(em)-1) for j in range(len(et)-1))
        self.cells=[];self._cell_data=[];masses=[];rays=[]
        for (a,b),(c,d),w in self.original_cells:
            for i in range(refinement):
                ai=a+(b-a)*Fraction(i,refinement)
                bi=a+(b-a)*Fraction(i+1,refinement)
                for j in range(refinement):
                    cj=c+(d-c)*Fraction(j,refinement)
                    dj=c+(d-c)*Fraction(j+1,refinement)
                    wc=w/Fraction(refinement**2)
                    self.cells.append(((ai,bi),(cj,dj),wc))
                    if wc==0:continue
                    mean,lower,upper=_cell_means_ranges(ai,bi,cj,dj)
                    middle=[(v.lower+v.upper)/2 for v in mean]
                    if any(v<=0 or v>1 for v in middle):
                        raise ValueError('Cell barycenter has nonpositive direction component')
                    n=np.sqrt(np.asarray(middle,dtype=float))
                    mass=float(wc)
                    if not np.isfinite(n).all() or not math.isfinite(mass) or mass<=0:
                        raise ValueError('Nonfinite stored cell mass or ray')
                    self._cell_data.append({'energy':wc,'means':mean,'lower':lower,
                                            'upper':upper,'stored_mass':mass,'ray':n})
                    masses.append(mass);rays.append(n)
        if len(masses)>20000:raise ValueError('Too many positive refined cells')
        self.mass=np.array(masses,float);self.n=np.array(rays,float)
        self.mass.setflags(write=False);self.n.setflags(write=False)
        self.refinement=refinement
        self.ntheta=len(em)-1;self.nphi=len(et)-1
        self.energy0=self.moments(np.zeros(3))[0]

    def moments(self,ell):
        e=np.asarray(ell,float)
        if e.shape!=(3,) or not np.isfinite(e).all():raise ValueError('Finite 3-log scale vector required')
        b=np.exp(-2*e)
        rad=np.sqrt((self.n*self.n)@b)
        if np.any(rad<=0):raise ValueError('Nonpositive stored ray energy')
        vol=np.exp(-e.sum())
        return float(vol*np.dot(self.mass,rad)),vol*b*np.einsum('j,ji->i',self.mass/rad,self.n*self.n)

    def rhs(self,u,y):
        v=np.asarray(y,float)
        if v.shape!=(6,) or not np.isfinite(v).all():raise ValueError('Finite 6-state required')
        h=v[3:]
        return np.r_[h,-h.sum()*h+self.moments(v[:3])[1]]

    def initial_state(self,shear=(.2,-.13,-.07)):
        s=np.asarray(shear,float)
        if s.shape!=(3,) or not np.isfinite(s).all() or abs(s.sum())>2e-12*max(float(np.max(abs(s))),np.finfo(float).tiny):
            raise ValueError('Trace-free shear input required')
        h=np.sqrt((self.energy0+.5*np.dot(s,s))/3)+s
        if np.any(h<0):raise ValueError('Initial directional expansions must be nonnegative')
        return np.r_[np.zeros(3),h]


def certified_tabulated_energy(source):
    """MPFR-outward exact continuum initial E compared to actual float64 E_Q(0)."""
    if not isinstance(source,TabulatedRadiation):raise TypeError('TabulatedRadiation required')
    E=_iv_fraction(source.exact_energy)
    exact_discrete=Interval(0)
    for data in source._cell_data:
        n2=sum((Fraction.from_float(float(z))**2 for z in data['ray']),Fraction())
        exact_discrete=exact_discrete+Interval(data['stored_mass'])*_iv_fraction(n2).sqrt()
    gap_a=_maxabs(E-exact_discrete)
    gap_b=_maxabs(exact_discrete-Interval(float(source.energy0)))
    total=Interval(gap_a)+Interval(gap_b)
    return {'status':'MPFR_TABULATED_INITIAL_ENERGY_ENCLOSURE',
            'continuum_energy_exact':str(source.exact_energy),
            'stored_binary_energy':float(source.energy0),
            'exact_real_discrete_difference_upper':gap_a,
            'floating_evaluator_difference_upper':gap_b,
            'energy_error_upper':total.upper,
            'float64_time_integrator_certified':False}


def certified_tabulated_pressure(source,lower,upper):
    """Uniform MPFR192 pressure discrepancy for nonnegative expanding log-scale box.

    Continuum cell center is exact E[x_i]; stored q=sqrt(center) is a rounded
    binary64 ray and stored mass is not normalized. The second-order bound is
    centered at *the mean on the simplex*, and vanishes at isotropic geometry.
    """
    if not isinstance(source,TabulatedRadiation):raise TypeError('TabulatedRadiation required')
    lo=np.asarray(lower,float);hi=np.asarray(upper,float)
    if lo.shape!=(3,) or hi.shape!=(3,) or not np.isfinite(lo).all() or not np.isfinite(hi).all() or np.any(lo<0) or np.any(hi<lo):
        raise ValueError('Nonnegative ordered finite log-scale box required')
    L=Interval(float(max(hi)))
    rmin=(-L).exp();d=Interval(1)-(-2*L).exp()
    ans=[Interval(0) for _ in range(3)]
    largest_cent=0.;largest_store=0.;largest_mass=0.
    for cell in source._cell_data:
        upper_cell=cell['upper'];lower_cell=cell['lower'];mean=cell['means']
        width=[Interval(float(upper_cell[i]))-Interval(float(lower_cell[i])) for i in range(3)]
        variance=sum((w*w/4 for w in width),Interval(0))
        Q=Interval(3)*d*d*variance/4
        nsq=[Fraction.from_float(float(x))**2 for x in cell['ray']]
        norm=sum(nsq,Fraction())
        if norm<=0:raise ValueError('Nonpositive stored ray squared norm')
        r0=rmin*_iv_fraction(min(Fraction(1),norm)).sqrt()
        eps=[_maxabs(_iv_fraction(nsq[i])-mean[i]) for i in range(3)]
        e1=sum((Interval(v) for v in eps),Interval(0))
        exactmass=_iv_fraction(cell['energy']);storedmass=Interval(cell['stored_mass'])
        massdiff=_maxabs(exactmass-storedmass)
        for i in range(3):
            v=width[i]*width[i]/4
            cent=v.__mul__(Q).sqrt()/(2*rmin**3)+Interval(3)*Interval(float(upper_cell[i]))*Q/(8*rmin**5)
            maxcomp=max(float(upper_cell[i]),float(nsq[i]))
            store=Interval(eps[i])/r0+Interval(maxcomp)*e1/(2*r0**3)
            mass=Interval(massdiff)*_iv_fraction(norm).sqrt()
            ans[i]=ans[i]+exactmass*(cent+store)+mass
            largest_cent=max(largest_cent,cent.upper)
            largest_store=max(largest_store,store.upper)
            largest_mass=max(largest_mass,mass.upper)
    return {'status':'MPFR_OUTWARD_TABULATED_SECOND_ORDER_PRESSURE',
            'method':'CENTERED_CELL_VARIANCE_PLUS_STORED_RAY',
            'pressure_upper':[v.upper for v in ans],
            'max_pressure_upper':max(v.upper for v in ans),
            'part_max':{'centered_covariance':largest_cent,
                        'stored_mean_ray':largest_store,'stored_mass':largest_mass},
            'cells_positive':len(source._cell_data),
            'model':'exact piecewise constant first-octant cell energy; eight reflections',
            'float64_rhs_rounding_included':False,
            'production_ready':False}


def certified_tabulated_geometry(source,*,end=.08,shear=(.2,-.13,-.07)):
    """Finite-time nonlinear source-to-geometry bound; ODE time error excluded."""
    if not isinstance(source,TabulatedRadiation):raise TypeError('TabulatedRadiation required')
    if not isinstance(end,(int,float)) or not math.isfinite(float(end)) or not 0<float(end)<=.2:
        raise ValueError('Pilot end time must lie in (0,.2]')
    s=np.asarray(shear,float)
    if s.shape!=(3,) or not np.isfinite(s).all() or abs(s.sum())>1e-14:
        raise ValueError('Trace-free initial shear required')
    E=certified_tabulated_energy(source)
    Econt=_iv_fraction(source.exact_energy)
    Eb=Interval(float(source.energy0))
    Emax=Interval(max(Econt.upper,Eb.upper))
    sx,sy=[Fraction.from_float(float(v)) for v in s[:2]]
    sref=[_iv_fraction(v) for v in (sx,sy,-sx-sy)]
    hbar=( (Econt+sum((q*q for q in sref),Interval(0))/2)/3).sqrt()
    exact_h=[hbar+si for si in sref]
    stored=source.initial_state(s)[3:]
    if any(z.lower<0 for z in exact_h) or any(z<0 for z in stored):
        raise ValueError('Both continuum and stored initial data must expand')
    d0=max(_maxabs(h-Interval(float(hb))) for h,hb in zip(exact_h,stored))
    T=Interval(float(end));bound=[]
    for h,hs in zip(exact_h,stored):
        largest=max(h.upper,float(hs));bound.append((Interval(largest)*T+Emax*T*T/2).upper)
    sourcebound=certified_tabulated_pressure(source,[0.,0.,0.],bound)
    propagated=propagate_interval([Interval(0),Interval(d0)],T,Emax,Interval(0),Interval(sourcebound['max_pressure_upper']))
    return {'status':'SCOPED_TABULATED_COUPLED_SOURCE_ENCLOSURE',
            'u_end':float(end),'initial_rate_upper':d0,
            'source_pressure_upper':sourcebound['max_pressure_upper'],
            'geometry_h_upper':propagated[1].upper,
            'geometry_ell_upper':propagated[0].upper,
            'geometry_box_upper':bound,'energy_certificate':E,
            'source_certificate':sourcebound,'time_integrator_error_included':False,
            'production_ready':False}

