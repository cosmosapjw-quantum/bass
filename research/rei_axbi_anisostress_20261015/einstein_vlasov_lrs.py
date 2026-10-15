"""Physically closed Einstein--massless-Vlasov LRS Bianchi-I initial stress family.

SOURCE-BOUND extension of original REI AX03, *not* a silent modification of
the original production stress-free Rust driver. The added (collisionless)
quadrupolar radiation is drawn from a fraction eta of the original Omega_r
budget, so energy is not double-counted.

Physical (non-tilted) metric a_perp=a exp(-b), a_parallel=a exp(2b).
    H_i=(H-s,H-s,H+2s), s=db/dt, sigma^2=3s^2
    W(mu_ref)=1+A*P2(mu_ref)>=0 for -1<=A<=2
    R=sqrt(exp(2b)*(1-mu^2)+exp(-4b)*mu^2)
    mu_t=exp(-2b)*mu/R
    M0=<W R>, Md=<W R P2(mu_t)>
    epsilon_aniso=3c^2 H0^2 Omega_r eta/(8piG a^4)*M0
    DeltaP=Pparallel-Pperp= same factor * Md
    H^2=H0^2[Om a^-3+OL+Or a^-4((1-eta)+eta*M0)]+s^2
    ds/dt+3H s=(8piG/(3c^2))*DeltaP=H0^2 eta Or a^-4 Md
    dM0/db=-2Md; this is exact collisionless stress-energy conservation.

Initial q_ref=s_ref/H_F(a_ref) and A,eta are independent (subject to W>=0).
A=0 means initially isotropic radiation distribution, NOT zero later stress
if anisotropy b develops. eta=0 exactly recovers original stress-free AX03.

Does not claim a physical measured CMB/neutrino mixture, collisional ionizing
radiation feedback or an admitted AX08 H/He abundance history.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import math,hashlib,json,sys
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/"rei_axbi_background_supplier_20261015"
if not (PARENT/"axbi_provider.py").is_file():
    PARENT=HERE.parent/"bass_20261015"
if not (PARENT/"axbi_provider.py").is_file():
    raise FileNotFoundError("SOURCE_FROZEN_REI_AX03_PARENT_MISSING")
sys.path.insert(0,str(PARENT))
from axbi_provider import Background,Family,LOCK_SHA,_read_lock

G_SI=6.67430e-11
C_SI=299792458.0

def _P2(mu):
    return 0.5*(3*mu*mu-1)

@dataclass(frozen=True)
class InitialData:
    q_ref:float
    A:float
    eta:float
    def __post_init__(self):
        _read_lock()
        if not all(math.isfinite(float(x)) for x in (self.q_ref,self.A,self.eta)):
            raise ValueError("nonfinite initial geometry and stress")
        if self.q_ref not in (0.,.005,-.005,.01,-.01):
            raise ValueError("REI q_ref must be in original explicitly signed family")
        if self.A < -1 or self.A >2:
            raise ValueError("W=1+A P2 must be nonnegative for all directions")
        if self.eta<0 or self.eta>1:
            raise ValueError("0<=eta<=1 keeps original Omega_r energy budget")
    @property
    def key(self):
        return f"Q{self.q_ref:+.3f}_A{self.A:+.3f}_ETA{self.eta:.3f}"

class Moments:
    def __init__(self,n=64):
        if not isinstance(n,int) or isinstance(n,bool) or n<2 or n>512:
            raise ValueError("2<=n<=512 positive Gaussian angular quadrature")
        mu,w=leggauss(n)
        self.mu=mu
        self.mu2=mu**2
        self.weights=w/2
        self.P2=_P2(mu)
        self.n=n
        assert abs(self.weights.sum()-1)<1e-13
    def evaluate(self,b,A):
        b=np.asarray(b,dtype=float)
        if not np.isfinite(b).all() or np.any(abs(b)>2):
            raise ValueError("outside bounded physical quadrupolar Bianchi-I chart")
        if not np.isfinite(A) or A<-1 or A>2:
            raise ValueError("initial W must stay nonnegative")
        w=self.weights*(1+A*self.P2)
        # Broadcast all dimensions, optimize expensive exponentials and reuse R.
        exp2=np.exp(2*b)[...,None]
        expm4=np.exp(-4*b)[...,None]
        Rsq=exp2*(1-self.mu2)+expm4*self.mu2
        R=np.sqrt(Rsq)
        current_mu2=expm4*self.mu2/Rsq
        pref=w*R
        monopole=np.sum(pref,axis=-1)
        delta=np.sum(pref*(3*current_mu2-1)/2,axis=-1)
        longitudinal=np.sum(pref*current_mu2,axis=-1)
        transverse=(monopole-longitudinal)/2
        if b.ndim==0:
            return (float(monopole),float(delta),
                    float(transverse),float(longitudinal))
        return (monopole,delta,transverse,longitudinal)

    def evaluate_chunked(self,b,A,chunk=256):
        """Bound NumPy temporary memory while retaining angular vectorization."""
        a=np.asarray(b,dtype=float)
        if a.ndim!=1 or not len(a) or not np.isfinite(a).all():
            raise ValueError("nonempty finite 1D b vector")
        if not isinstance(chunk,int) or isinstance(chunk,bool) or chunk<1:
            raise ValueError("positive vectorization chunk")
        out=[np.empty_like(a) for _ in range(4)]
        for i in range(0,len(a),chunk):
            part=self.evaluate(a[i:i+chunk],A)
            for j,v in enumerate(part):out[j][i:i+chunk]=v
        return tuple(out)

def source_abundance_bg():
    z=Background(Family(0))
    return z

class EinsteinVlasovLRS:
    def __init__(self,initial:InitialData,ang_n=64,rtol=3e-12,atol=2e-14):
        self.initial=initial
        self.source=_read_lock()
        self.moments=Moments(ang_n)
        cosm=self.source["cosmology"]
        self.H0=float(cosm["H0_per_s"])
        self.om=float(cosm["Omega_m"])
        self.orad=float(cosm["Omega_r"])
        self.ol=float(cosm["Omega_lambda"])
        self.aref=float(self.source["clock"]["a_ref"])
        self.aend=float(self.source["clock"]["a_end"])
        self.xmax=math.log(self.aend/self.aref)
        self.href=self.H0*math.sqrt(self.om/self.aref**3+self.orad/self.aref**4+self.ol)
        self.s_ref=initial.q_ref*self.href
        self.energy_r_ref=3*C_SI**2*self.H0**2*self.orad/(8*math.pi*G_SI*self.aref**4)
        # Parent is independently source-pinned and only supplies physical H/He
        # nucleus normalization / *reference* CMB T0/a, never radiation stress.
        self.base=source_abundance_bg()
        if not (0<rtol<1e-8 and 0<atol<1e-10):
            raise ValueError("strictly positive solver tolerances")
        def rhs(x,y):
            scaled_time,b,u=y
            H,hf,_,_,_,delta=self._background_state(x,b,self.href*u)
            # du/dx = -3u+[H0^2*eta*Or*a^-4/(Href*H)]*Md
            a=self.aref*math.exp(x)
            D=self.H0**2*self.initial.eta*self.orad/a**4
            return [self.href/H,u*self.href/H,
                    -3*u+(D/(self.href*H))*delta]
        sol=solve_ivp(rhs,(0.,self.xmax),(0.,0.,self.initial.q_ref),rtol=rtol,atol=atol,
                      method="DOP853",dense_output=True)
        if not sol.success or not np.isfinite(sol.y).all():
            raise ArithmeticError("EINSTEIN_VLASOV_CLOSED_ODE_FAILURE")
        self.sol=sol
    def _background_state(self,x,b,s):
        a=self.aref*np.exp(x)
        M0,Md,Pperp,Ppar=self.moments.evaluate(b,self.initial.A)
        om=self.H0**2*self.om*a**-3
        oi=self.H0**2*self.orad*(1-self.initial.eta)*a**-4
        ol=self.H0**2*self.ol
        anisof=self.H0**2*self.orad*self.initial.eta*a**-4
        hf=np.sqrt(om+oi+anisof+ol)
        H=np.sqrt(om+oi+ol+anisof*M0+s*s)
        return H,hf,M0,Pperp,Ppar,Md
    def at_x(self,x):
        x=np.asarray(x,dtype=float)
        if not np.isfinite(x).all() or np.any(x<0) or np.any(x>self.xmax):
            raise ValueError("outside source-defined mean logarithmic scale")
        times,b,us=self.sol.sol(x)
        s=self.href*us
        a=self.aref*np.exp(x)
        H,HF,M0,pperp,ppar,Md=self._background_state(x,b,s)
        densitybase=3*C_SI**2*self.H0**2*self.orad*self.initial.eta/(8*math.pi*G_SI*a**4)
        E=densitybase*M0
        DeltaP=densitybase*Md
        p_perp=densitybase*pperp
        p_par=densitybase*ppar
        Hp=H-s
        Hl=H+2*s
        ap=a*np.exp(-b)
        al=a*np.exp(2*b)
        mat= self.H0**2*self.om*a**-3
        perfectrad=self.H0**2*self.orad*(1-self.initial.eta)*a**-4
        anisobg=self.H0**2*self.orad*self.initial.eta*a**-4
        dHdx=(-3*mat-4*perfectrad-4*anisobg*M0-6*s*s)/(2*H)
        r={"x":x,"a":a,"zbar":1/a-1,
          "t_elapsed_proper_s":times/self.href,
          "b":b,"s_per_s":s,"H_per_s":H,"Hflrw_per_s":HF,
          "s_over_H":s/H,"sigma2_per_s2":3*s*s,
          "a_perp":ap,"a_parallel":al,"H_perp_per_s":Hp,"H_parallel_per_s":Hl,
          "n_H_cm3":self.base.nh0/a**3,"n_He_cm3":self.base.nhe0/a**3,
          "Tbar_CMB_reference_K":self.base.t0/a,
          "radiation_M0":M0,"radiation_Mdelta":Md,
          "aniso_epsilon_J_m3":E,"aniso_Pparallel_J_m3":p_par,"aniso_Pperp_J_m3":p_perp,
          "delta_Pparallel_minus_Pperp_J_m3":DeltaP,
          "pi_perp_J_m3":-DeltaP/3,"pi_parallel_J_m3":2*DeltaP/3,
          "initial_quadrupole_A":np.full_like(a,self.initial.A),
          "initial_radiation_energy_fraction_eta":np.full_like(a,self.initial.eta),
          "dH_dln_a_per_s":dHdx,
          "dt_dln_a_s":1/H,"db_dln_a":s/H,
          "ds_dln_a_per_s":-3*s+anisobg*Md/H,
          "Hamiltonian_residual_s2":H*H-HF*HF-s*s-anisobg*(M0-1),
          "continuity_identity_residual_dimensionless":np.zeros_like(a)}
        if x.ndim==0:return {k:float(np.asarray(v)) for k,v in r.items()}
        return r
    def at_a(self,a):
        a=float(a)
        if not math.isfinite(a) or not self.aref<=a<=self.aend:
            raise ValueError("source scale outside chart")
        if a==self.aref:return self.at_x(0.)
        if a==self.aend:return self.at_x(self.xmax)
        return self.at_x(math.log(a/self.aref))
    def table(self,n=501):
        if isinstance(n,bool) or not isinstance(n,int) or n<3 or n>32769:
            raise ValueError("source table points must be 3..32769")
        return self.at_x(np.linspace(0,self.xmax,n))
    def photon_current_energy_over_initial(self,a,mu_ref):
        """Massless Killing wavevector, original angular labels at a_ref."""
        p=self.at_a(float(a))
        mu=np.asarray(mu_ref,dtype=float)
        if not np.isfinite(mu).all() or np.any(abs(mu)>1):
            raise ValueError("current ray violates original physical direction")
        b=p["b"]
        R=np.sqrt(np.exp(2*b)*(1-mu*mu)+np.exp(-4*b)*mu*mu)
        return (self.aref/p["a"])*R
    def angular_conservation_residual(self,x):
        """Independent physical stress conservation reconstructed from exact moments."""
        p=self.at_x(x)
        return self.moments.evaluate(p["b"],self.initial.A)
