"""CE1-A: collisionless diagonal massless Einstein--Vlasov Python oracle.

Signature(-+++), normal proper time t, u=t/Tstar, a_i(0)=1.
ell=ln a, h=Tstar H, E=(8*pi*G*Tstar**2/c**2)*rho_energy.
P uses the same normalization. Lambda=0. No constraint projection.
Positive coordinate-reflection-invariant initial angular energy is retained in
full; this is not a fluid or finite-multipole closure. Native defaults unchanged.
"""
from __future__ import annotations
from itertools import product
import numpy as np
from scipy.integrate import solve_ivp
from scipy.spatial import cKDTree

def _oracle(backend):
    if backend != 'python_oracle':
        raise ValueError("CE1-A requires explicit backend='python_oracle'; no native fallback")

def _real(x,name):
    if np.iscomplexobj(x):
        raise ValueError(name+' must be real')
    a=np.asarray(x,dtype=float)
    if not np.isfinite(a).all():
        raise ValueError(name+' must be finite')
    return a

class AngularRadiation:
    """Initial angular energy density, not radiance.

    Conventional bolometric radiance must first be divided by c and multiplied
    by 8*pi*G*Tstar**2/c**2. Weights are raw solid angle; no normalization occurs.
    Reflection invariance is sufficient, not necessary, for a diagonal model.
    """
    def __init__(self,n,weights,intensity):
        n=_real(n,'n');w=_real(weights,'weights');I=_real(intensity,'intensity')
        if n.ndim!=2 or n.shape[1]!=3 or w.shape!=(len(n),) or I.shape!=w.shape:
            raise ValueError('incompatible ray/weight/intensity shapes')
        if len(n)<1 or np.max(abs(np.linalg.norm(n,axis=1)-1))>2e-11:
            raise ValueError('unit ray directions required')
        if np.any(w<=0) or np.any(I<0):
            raise ValueError('positive angular weights and nonnegative energy required')
        tree=cKDTree(n);W=w*I;scale=max(1.,float(np.max(W)))
        if len(n)>1 and tree.query(n,k=2)[0][:,1].min()<1e-13:
            raise ValueError('duplicate directions are unsupported')
        for signs in product((-1.,1.),repeat=3):
            distance,idx=tree.query(n*np.array(signs))
            if np.max(distance)>2e-11 or np.max(abs(W[idx]-W))>2e-11*scale:
                raise ValueError('coordinate-reflection-invariant discrete energy measure required')
        self.n=n.copy();self.weights=w.copy();self.intensity=I.copy()
        self.energy_weights=W.copy();self.energy0=float(W.sum())
        for a in (self.n,self.weights,self.intensity,self.energy_weights):
            a.setflags(write=False)

    def _kinematics(self,ell):
        ell=_real(ell,'ell')
        if ell.shape!=(3,):
            raise ValueError('ell has three components')
        with np.errstate(over='raise',under='ignore',invalid='raise'):
            p=self.n*np.exp(-ell)[None,:]
            r=np.linalg.norm(p,axis=1)
            iv=np.exp(-ell.sum())
        if np.any(r<=0) or not np.isfinite(r).all() or not np.isfinite(iv) or iv<=0:
            raise FloatingPointError('scale factors outside supported float64 range')
        return p,r,iv

    def moments(self,ell):
        p,r,iv=self._kinematics(ell)
        E=iv*np.dot(self.energy_weights,r)
        P=iv*np.einsum('q,qi->i',self.energy_weights/r,p*p)
        return float(E),P

    def tensor(self,ell):
        p,r,iv=self._kinematics(ell)
        E=iv*np.dot(self.energy_weights,r)
        T=iv*np.einsum('q,qi,qj->ij',self.energy_weights/r,p,p)
        flux=iv*np.einsum('q,qi->i',self.energy_weights,p)
        return float(E),np.diag(T).copy(),flux,T

    def jacobian(self,ell):
        p,r,iv=self._kinematics(ell)
        E,P=self.moments(ell)
        R=iv*np.einsum('q,qi,qj->ij',self.energy_weights/r**3,p*p,p*p)
        return -(E+P), -P[:,None]-2*np.diag(P)+R

def constraint(state,energy):
    z=_real(state,'state')
    if z.shape!=(6,):
        raise ValueError('state has six components')
    h=z[3:]
    return float(h[0]*h[1]+h[0]*h[2]+h[1]*h[2]-energy)

def initial_state(radiation,shear):
    s=_real(shear,'shear')
    if s.shape!=(3,) or abs(s.sum())>2e-13*max(1.,np.max(abs(s))):
        raise ValueError('three explicitly trace-free shear components required')
    H=np.sqrt((radiation.energy0+.5*np.dot(s,s))/3)
    return np.r_[np.zeros(3),H+s]

def _inputs(radiation,state,end,allow_constraint_defect=False):
    z=_real(state,'state').copy();end=float(end)
    if z.shape!=(6,) or np.max(abs(z[:3]))>2e-13:
        raise ValueError('six-component initial state with a_i(0)=1 required')
    if not np.isfinite(end) or end<=0:
        raise ValueError('positive finite end time required')
    if not allow_constraint_defect and abs(constraint(z,radiation.energy0))>2e-11*max(1.,radiation.energy0,np.max(abs(z[3:]))**2):
        raise ValueError('initial Hamiltonian constraint is not satisfied')
    return z,end

def _time(u,end):
    u=float(u)
    if not np.isfinite(u) or u<0 or u>end+1e-13*max(1,end):
        raise ValueError('time outside integrated interval')
    return min(u,end)

class CoupledHistory:
    """Full initial distribution as an exact finite-ray metric functional.

    pressure_bias is diagnostic source injection, not a physical matter model.
    Initial constraints are checked, never reimposed during evolution.
    """
    def __init__(self,radiation,state,end,*,backend=None,rtol=2e-11,atol=2e-13,
                 allow_constraint_defect=False,pressure_bias=None):
        _oracle(backend)
        z,self.end=_inputs(radiation,state,end,allow_constraint_defect)
        self.radiation=radiation;self.initial=z.copy();self.pressure_bias=pressure_bias
        def rhs(u,y):
            _,P=radiation.moments(y[:3]);h=y[3:]
            if pressure_bias is not None:
                eta=_real(pressure_bias(u,y.copy()),'pressure bias')
                if eta.shape!=(3,):raise ValueError('pressure bias must have three entries')
                P=P+eta
            return np.r_[h,-h.sum()*h+P]
        self.rhs=rhs
        self.solution=solve_ivp(rhs,(0,self.end),z,method='DOP853',rtol=rtol,atol=atol,dense_output=True)
        if not self.solution.success:raise RuntimeError(self.solution.message)

    def at(self,u):
        return self.solution.sol(_time(u,self.end)).copy()

    def stress_at(self,u):
        return self.radiation.tensor(self.at(u)[:3])

class DirectHistory:
    """Independent Cartesian P8 radiation+Einstein IVP, no reduced-source call.

    Evolves directions, angular Jacobian and physical 3x3 bolometric carrier.
    Initial unpolarized radiation is the admitted test channel. P8 handles both
    tensor indices. No state normalization or clipping is performed.
    """
    def __init__(self,radiation,state,end,*,backend=None,rtol=2e-11,atol=2e-13):
        _oracle(backend)
        from bianchi.q import polarization as P8
        z,self.end=_inputs(radiation,state,end)
        self.radiation=radiation;self.nray=len(radiation.n)
        n=radiation.n
        proj=np.eye(3)-np.einsum('qi,qj->qij',n,n)
        J=.5*radiation.intensity[:,None,None]*proj
        y0=np.r_[z,n.ravel(),np.zeros(self.nray),J.ravel()]
        zero=np.zeros(3);Z=np.zeros((3,3))
        def unpack(y):
            N=self.nray
            return y[:6],y[6:6+3*N].reshape(N,3),y[6+3*N:6+4*N],y[6+4*N:].reshape(N,3,3)
        self._unpack=unpack
        def rhs(u,y):
            state,n,lw,J=unpack(y);h=state[3:];H=h.mean();S=np.diag(h-H)
            w=radiation.weights*np.exp(lw)
            I=np.trace(J,axis1=1,axis2=2)
            pressure=np.einsum('q,q,qi->i',w,I,n*n)
            nrate=P8.direction_rate(n,H,S,zero,Z,zero)
            s=np.einsum('qi,ij,qj->q',n,S,n)
            Jrate=-4*(H+s)[:,None,None]*J+P8.tensor_rate(J,n,H,S,zero,Z,zero)
            return np.r_[h,-h.sum()*h+pressure,nrate.ravel(),3*s,Jrate.ravel()]
        self.solution=solve_ivp(rhs,(0,self.end),y0,method='DOP853',rtol=rtol,atol=atol,dense_output=True)
        if not self.solution.success:raise RuntimeError(self.solution.message)

    def at(self,u):
        state,n,lw,J=self._unpack(self.solution.sol(_time(u,self.end)))
        w=self.radiation.weights*np.exp(lw)
        I=np.trace(J,axis1=1,axis2=2)
        E=float(w@I);T=np.einsum('q,q,qi,qj->ij',w,I,n,n)
        return {'state':state.copy(),'directions':n,'jacobian':np.exp(lw),'carrier':J,
                'energy':E,'pressure':np.diag(T).copy(),'stress':T,
                'flux':np.einsum('q,q,qi->i',w,I,n),'constraint':constraint(state,E)}

def source_error_bound(u,source_sup,Emax,B,initial_error=0.0):
    """Nonlinear Gronwall bound on z=(ell,h) in the stated expanding region.

    Requires E<=Emax and |h_i|<=B on the comparison segment. For positive
    collisionless data with h_i(0)>=0: B=max(max h_i(0),sqrt(E0)) is invariant.
    source_sup may be a certified source bound or total variation of two positive
    angular measures. A measured quadrature gap is NOT automatically certified.
    """
    vals=_real([u,source_sup,Emax,B,initial_error],'bound parameters')
    if np.any(vals<0):raise ValueError('nonnegative bound parameters required')
    u,eta,Emax,B,e0=vals
    L=max(1.,4*Emax+6*B)
    if L*u>700:raise OverflowError('bound exceeds supported exponential range')
    return float(np.exp(L*u)*e0+eta*np.expm1(L*u)/L)


def source_error_envelope(u,source_sup,Emax,ell_initial_error=0.,h_initial_error=0.):
    """Sharper nonlinear comparison bound in the directional expanding octant.

    For all h_i>=0, mu_inf(d[-theta*h]/dh)=max_i(h_i-theta)<=0.
    Hence e_ell'<=e_h, e_h'<=4Emax*e_ell+source_sup in Dini sense.
    Returns separate bounds for logarithmic scales and directional expansion.
    It does not certify the input source_sup; TV of two initial positive energy
    measures is one admissible bound. No small-anisotropy expansion is used.
    """
    v=_real([u,source_sup,Emax,ell_initial_error,h_initial_error],'bound parameters')
    if np.any(v<0):raise ValueError('nonnegative bound parameters required')
    t,eta,E,e0,h0=v
    if E==0:return np.array([e0+h0*t+.5*eta*t*t,h0+eta*t])
    k=2*np.sqrt(E);x=k*t
    if x>700:raise OverflowError('bound exceeds supported exponential range')
    sh=np.sinh(x);ch=np.cosh(x);cm1=2*np.sinh(x/2)**2
    return np.array([e0*ch+h0*sh/k+eta*cm1/k**2,
                     k*e0*sh+h0*ch+eta*sh/k])
