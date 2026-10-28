"""CE1-B: exact-arithmetic source/defect bounds with explicit floating-point limits.

Restricted to positive reflection-even polynomial initial angular energy and the
all-expanding, diagonal, collisionless massless Bianchi-I channel, Lambda=0.
Units: u=t/Tstar, ell=log a, h=Tstar H, E,P=8piG*Tstar^2/c^2 times
energy density/pressure. These are not radiance inputs. No physical multipole
closure, raw-weight renormalization, constraint projection or clipping is used.

The inequalities are analytic in exact arithmetic. Their float64 evaluations
are NOT outward-rounded interval certificates. A sampled fine-grid difference
is never used to define a quadrature bound or a between-sample residual bound.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import comb, factorial
import numpy as np
from numpy.polynomial.legendre import leggauss


def _oracle(backend):
    if backend != 'python_oracle':
        raise ValueError("Explicit backend='python_oracle' required; no native fallback")


def _real(x, shape=None):
    if np.iscomplexobj(x):
        raise ValueError('Real inputs required')
    a=np.asarray(x,dtype=float)
    if not np.isfinite(a).all() or (shape is not None and a.shape!=shape):
        raise ValueError('Finite inputs with the contracted shape required')
    return a


def _integer(x, minimum=1):
    if isinstance(x,(bool,np.bool_)) or not isinstance(x,(int,np.integer)) or x<minimum:
        raise ValueError('Integer count outside the supported range')
    return int(x)


class PolynomialRadiation:
    """Explicit degree4 continuum model, not an inferred sampled distribution.

    F0=energy/(4pi)*(1+c2*P2(qz)+ct*(qx^2-qy^2)+c4*P4(qz)).
    Positivity is checked on the entire sphere by a quadratic minimum in qz^2.
    Integer quadrature counts identify the ideal exact-arithmetic GL/phi rule.
    Numerical node/weight rounding is outside the analytic error certificate.
    """
    polynomial_degree=4

    def __init__(self,energy=.9,coefficients=(.6,.25,.2),ntheta=12,nphi=None,*,backend=None):
        _oracle(backend)
        E=float(energy);c=_real(coefficients,(3,))
        nt=_integer(ntheta,4);np_=_integer(2*nt if nphi is None else nphi,8)
        if np_%2 or not np.isfinite(E) or E<0:
            raise ValueError('Even azimuth count and nonnegative finite energy required')
        # Minimum over azimuth at fixed z^2; then minimize this quadratic on [0,1].
        a=35*c[2]/8;b=1.5*c[0]-30*c[2]/8+abs(c[1])
        d=1-c[0]/2+3*c[2]/8-abs(c[1])
        vals=[d,a+b+d]
        if a>0 and 0 < -b/(2*a) < 1:
            v=-b/(2*a);vals.append(a*v*v+b*v+d)
        if min(vals)<0:
            raise ValueError('Initial angular polynomial is negative somewhere on the sphere')
        mu,w=leggauss(nt);phi=2*np.pi*np.arange(np_)/np_
        z=np.repeat(mu,np_);ph=np.tile(phi,nt);s=np.sqrt(1-z*z)
        n=np.column_stack([s*np.cos(ph),s*np.sin(ph),z])
        weights=np.repeat(w,np_)*2*np.pi/np_
        F=E/(4*np.pi)*(1+c[0]*(3*z*z-1)/2+c[1]*(n[:,0]**2-n[:,1]**2)
                         +c[2]*(35*z**4-30*z*z+3)/8)
        self.energy0=E;self.coefficients=c.copy();self.ntheta=nt;self.nphi=np_
        self.n=n;self.weights=weights;self.density=F;self.mass=weights*F
        self.sampled_energy0=float(self.mass.sum());self.positivity_min=float(min(vals))
        self.initial_pressure=E*np.array([1/3-c[0]/15+2*c[1]/15,
                                         1/3-c[0]/15-2*c[1]/15,1/3+2*c[0]/15])
        self.exact_degree=min(2*nt-1,np_-1)
        self.K=(self.exact_degree-self.polynomial_degree-2)//2
        if self.K<0:raise ValueError('Quadrature cannot integrate the leading pressure polynomial')
        for v in (self.n,self.weights,self.density,self.mass,self.coefficients,self.initial_pressure):
            v.setflags(write=False)

    def moments(self,ell):
        ell=_real(ell,(3,))
        with np.errstate(over='raise',under='raise',invalid='raise',divide='raise'):
            b=np.exp(-2*ell);r=np.sqrt((self.n*self.n)@b);iv=np.exp(-sum(ell))
            E=iv*(self.mass@r)
            P=iv*b*np.einsum('q,qi->i',self.mass/r,self.n*self.n)
        return float(E),P

    def rhs(self,t,y):
        y=_real(y,(6,));h=y[3:]
        return np.r_[h,-h.sum()*h+self.moments(y[:3])[1]]

    def initial_state(self,shear=(.2,-.13,-.07)):
        s=_real(shear,(3,));scale=max(np.finfo(float).tiny,float(max(abs(s))))
        if abs(sum(s))>2e-12*scale:raise ValueError('Trace-free shear required, no silent projection')
        h=np.sqrt((self.energy0+.5*(s@s))/3)+s
        if np.any(h<0):raise ValueError('Error budget requires every initial expansion rate nonnegative')
        return np.r_[np.zeros(3),h]


def source_bound_box(source,lower,upper):
    """Uniform ideal-rule pressure error on a complete log-scale box.

    A degree-(d+2+2K) polynomial is integrated exactly. The two positive
    remainder functionals each have mass initial_pressure[i]. This is not a
    bound on an arbitrary callable or on floating-point node/weight errors.
    """
    lo=_real(lower,(3,));hi=_real(upper,(3,))
    if np.any(lo>hi):raise ValueError('Ordered log-scale bounds required')
    spread=float(max(hi)-min(lo));q=float(np.tanh(spread))
    if q>=1:raise ValueError('Angular contrast too large for this binomial bound')
    K=source.K;c=comb(2*(K+1),K+1)/4.**(K+1)
    tail=c*q**(K+1)/(1-q)
    m_lower=.5*(np.exp(-2*max(hi))+np.exp(-2*min(hi)))
    pref=np.exp(-2*lo-sum(lo))/np.sqrt(m_lower)
    eta=2*source.initial_pressure*pref*tail
    if not np.isfinite(eta).all():raise FloatingPointError('Source bound overflow')
    return {'pressure_bound':eta.tolist(),'K':K,'q':q,'tail_bound':float(tail),
            'exact_degree':source.exact_degree,'floating_point_certificate':False}


def _conv(a,b,order=3):
    out=np.zeros_like(a)
    for k in range(order+1):
        for j in range(k+1):out[k]+=a[j]*b[k-j]
    return out


def _expjet(a):
    out=np.zeros_like(a);out[0]=np.exp(a[0])
    for k in range(1,4):
        for j in range(1,k+1):out[k]+=j*a[j]*out[k-j]/k
    return out


def pressure_jets(source,ell_taylor):
    """P_Q(ell(t)) coefficients through degree3 (derivative divided by k!)."""
    ell=_real(ell_taylor,(4,3));b=_expjet(-2*ell)
    Z=b@(source.n*source.n).T
    v=Z/Z[0];v[0]=0
    v2=_conv(v,v);v3=_conv(v2,v)
    root=np.zeros_like(v);root[0]=1
    root+=-.5*v+.375*v2-.3125*v3
    root/=np.sqrt(Z[0])
    numerator=_expjet(-ell.sum(axis=1)[:,None]-2*ell)
    out=np.empty((4,3))
    for i in range(3):
        prod=_conv(numerator[:,i,None]*np.ones_like(root),root)
        out[:,i]=prod@(source.mass*source.n[:,i]**2)
    return out


def _bernstein(coeff):
    c=np.asarray(coeff);degree=len(c)-1;out=np.zeros_like(c)
    for i in range(degree+1):
        for j in range(i+1):out[i]+=comb(i,j)/comb(degree,j)*c[j]
    return out


def _derivative(coeff,order=1):
    c=np.asarray(coeff)
    for _ in range(order):
        c=np.arange(1,len(c))[:,None]*c[1:]
    return c


@dataclass
class HermitePath:
    times: np.ndarray
    states: np.ndarray
    slopes: np.ndarray

    def __post_init__(self):
        self.times=_real(self.times).copy();self.states=_real(self.states).copy()
        self.slopes=_real(self.slopes).copy()
        if (self.times.ndim!=1 or len(self.times)<2 or self.times[0]!=0 or
                np.any(np.diff(self.times)<=0) or self.states.shape!=(len(self.times),6)
                or self.slopes.shape!=self.states.shape):
            raise ValueError('Increasing times from zero and six-dimensional states/slopes required')
        self.coefficients=[]
        for j,dt in enumerate(np.diff(self.times)):
            y,z=self.states[j:j+2];f,g=self.slopes[j:j+2]
            self.coefficients.append(np.array([y,dt*f,3*(z-y)-dt*(2*f+g),
                                               2*(y-z)+dt*(f+g)]))
        self.coefficients=np.array(self.coefficients)

    def at(self,t,derivative=0):
        t=float(t)
        if not np.isfinite(t) or t<0 or t>self.times[-1]:raise ValueError('Time outside path')
        i=min(np.searchsorted(self.times,t,side='right')-1,len(self.times)-2)
        h=self.times[i+1]-self.times[i];v=(t-self.times[i])/h;c=self.coefficients[i]
        if derivative not in (0,1,2,3):raise ValueError('Derivative must be 0,1,2 or3')
        if derivative:c=_derivative(c,derivative)/h**derivative
        return np.polynomial.polynomial.polyval(v,c)

    def panel_bounds(self,i):
        B=_bernstein(self.coefficients[i])
        return B.min(axis=0),B.max(axis=0)


def rk4_path(source,state,end,steps,*,backend=None):
    _oracle(backend);steps=_integer(steps);y=_real(state,(6,)).copy();T=float(end)
    if not np.isfinite(T) or T<=0:raise ValueError('Positive finite end time required')
    E=source.moments(y[:3])[0];h=y[3:]
    C=h[0]*h[1]+h[0]*h[2]+h[1]*h[2]-E
    if max(abs(y[:3]))>2e-14 or np.any(h<0) or abs(C)>2e-11*max(E,max(h*h),np.finfo(float).tiny):
        raise ValueError('Constraint-admissible expanding initial geometry with a_i=1 required')
    ts=np.linspace(0,T,steps+1);states=[y.copy()];slopes=[source.rhs(0,y)]
    for j in range(steps):
        t=ts[j];dt=ts[j+1]-t;k1=slopes[-1]
        k2=source.rhs(t+dt/2,y+dt*k1/2);k3=source.rhs(t+dt/2,y+dt*k2/2)
        k4=source.rhs(t+dt,y+dt*k3)
        y=y+dt*(k1+2*k2+2*k3+k4)/6
        if not np.isfinite(y).all():raise FloatingPointError('RK4 state is not finite')
        states.append(y.copy());slopes.append(source.rhs(ts[j+1],y))
    return HermitePath(ts,np.array(states),np.array(slopes))


def _p4_bound(E,H1,H2,H3):
    # Product rule for exp(-sum ell-2ell_i) * (sum q_j^2 exp(-2ell_j))^-1/2.
    m1=2*H1;m2=2*H2+4*H1**2;m3=2*H3+12*H1*H2+8*H1**3
    m4=16*H1*H3+12*H2**2+48*H1**2*H2+16*H1**4
    b1=.5*m1;b2=.5*m2+.75*m1**2
    b3=.5*m3+2.25*m1*m2+1.875*m1**3
    b4=.5*m4+3*m1*m3+2.25*m2**2+11.25*m1*m1*m2+6.5625*m1**4
    a1=5*H1;a2=5*H2+25*H1**2
    a3=5*H3+75*H1*H2+125*H1**3
    a4=100*H1*H3+75*H2**2+750*H1**2*H2+625*H1**4
    return E*(a4+4*a3*b1+6*a2*b2+4*a1*b3+b4)


def residual_panel(source,path,i,subcells=8):
    """Upper bounds over the whole panel, conditional on exact arithmetic.

    Residual Taylor coefficients through cubic order are evaluated at subcell
    centers; an analytic fourth-derivative remainder bounds all omitted terms.
    A grid of residual values alone is never reported as a supremum.
    """
    subcells=_integer(subcells);dt=path.times[i+1]-path.times[i]
    C=path.coefficients[i];lo,hi=path.panel_bounds(i)
    if np.any(lo<0):raise ValueError('Whole Hermite path must have ell_i,h_i>=0')
    deriv_caps=[]
    for k in (1,2,3):
        B=_bernstein(_derivative(C,k))/dt**k
        deriv_caps.append(np.max(abs(B),axis=0))
    H=[max(a[:3]) for a in deriv_caps];G=[max(a[3:]) for a in deriv_caps]
    R4=_p4_bound(source.sampled_energy0,*H)+24*G[2]*G[0]+18*G[1]**2
    delta_l=0.;delta_h=0.;radius=dt/(2*subcells)
    for j in range(subcells):
        v=(j+.5)/subcells
        T=np.zeros((4,6))
        for k in range(4):
            c=C if k==0 else _derivative(C,k)
            T[k]=np.polynomial.polynomial.polyval(v,c)/dt**k/factorial(k)
        rate=np.zeros((4,6));rate[:3]=np.arange(1,4)[:,None]*T[1:]
        r_l=rate[:,:3]-T[:,3:]
        theta=T[:,3:].sum(axis=1)
        product=np.array([sum(theta[j]*T[k-j,3:] for j in range(k+1)) for k in range(4)])
        r_h=rate[:,3:]+product-pressure_jets(source,T[:,:3])
        powers=radius**np.arange(4)
        delta_l=max(delta_l,float(np.max(powers@abs(r_l))))
        delta_h=max(delta_h,float(np.max(powers@abs(r_h))+R4*radius**4/24))
    return {'ell_defect':delta_l,'h_defect':delta_h,'fourth_derivative_bound':float(R4),
            'subcells':subcells,'remainder_method':'analytic_fourth_derivative_not_sample_max',
            'path_lower':lo.tolist(),'path_upper':hi.tolist()}


def propagate(previous,dt,energy,ell_forcing,h_forcing):
    p=_real(previous,(2,));v=_real([dt,energy,ell_forcing,h_forcing])
    if np.any(p<0) or np.any(v<0):raise ValueError('Nonnegative comparison inputs required')
    t,E,a,b=v;x,y=p
    if E==0:return np.array([x+t*y+a*t+.5*b*t*t,y+b*t])
    k=2*np.sqrt(E);z=k*t
    if z>700:raise OverflowError('Comparison envelope overflow')
    sh=np.sinh(z);ch=np.cosh(z);cm=2*np.sinh(z/2)**2
    return np.array([ch*x+sh*y/k+a*sh/k+b*cm/k**2,
                     k*sh*x+ch*y+a*cm+b*sh/k])


def audit_path(source,path,subcells=8):
    """Separate source and time contributions to a geometry error envelope.

    Compares the stated Hermite path to the continuum polynomial-source solution
    with the same initial state. Assumes that initial data are constraint-
    admissible and in the expanding octant; checks those conditions explicitly.
    No bound is claimed on unrecorded interpolation schemes or floating rounding.
    """
    if not isinstance(source,PolynomialRadiation) or not isinstance(path,HermitePath):
        raise TypeError('Explicit polynomial source and HermitePath required')
    y0=path.states[0];h0=y0[3:]
    C=h0[0]*h0[1]+h0[0]*h0[2]+h0[1]*h0[2]-source.energy0
    if max(abs(y0[:3]))>2e-14 or np.any(h0<0) or abs(C)>2e-11*max(source.energy0,max(h0*h0),np.finfo(float).tiny):
        raise ValueError('Continuum-constraint-admissible initial state required')
    angular=np.zeros(2);time=np.zeros(2);rows=[]
    for i,dt in enumerate(np.diff(path.times)):
        defect=residual_panel(source,path,i,subcells)
        lo=np.array(defect['path_lower'][:3]);hi=np.array(defect['path_upper'][:3])
        bound=source_bound_box(source,lo,hi);eta=max(bound['pressure_bound'])
        angular=propagate(angular,dt,source.energy0,0.,eta)
        time=propagate(time,dt,source.energy0,defect['ell_defect'],defect['h_defect'])
        rows.append({'start':float(path.times[i]),'end':float(path.times[i+1]),
                     **defect,**bound,'source_envelope':angular.tolist(),
                     'time_envelope':time.tolist(),'total_envelope':(angular+time).tolist()})
    return {'status':'ANALYTIC_BOUND_FLOAT_EVALUATED','floating_point_certificate':False,
            'scope':'known polynomial continuum source; cubic reconstructed path; all-expanding channel',
            'final_source':angular.tolist(),'final_time':time.tolist(),
            'final_total':(angular+time).tolist(),'rows':rows}
