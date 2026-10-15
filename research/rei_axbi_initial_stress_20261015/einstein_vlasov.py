"""Source-locked, self-consistent LRS Einstein–massless-Vlasov background.

This is a *new conditional model lane*, not the original stress-free AX03
scientific source; original cosmological H0, Omegas, proper-time interval and
five signed shear initial conditions are read from the byte-locked original.

At a_ref initial positive massless angular distribution
  W(mu0) = 1 + kappa * P2(mu0),  |kappa|<=0.5.
The independent initial stress is pi_s_ref/epsilon_rad_ref = kappa/15.
No source-driven ionizing photon spectrum or Thomson collision is included.

Initially labelled reference momentum has conserved spatial Killing components.
With b=ln(a_parallel/a)/2:
 R^2 = exp(2b)(1-u^2) + exp(-4b)u^2,
 mu_late = exp(-2b)u/R,
 M(b,kappa)=<W R>, P(b,kappa)=<W R P2(mu_late)>/3.
Here <...>=(1/2)integral_-1^1 (... )du.

Exact source energy conservation M_b=-6P, so rho_rad=
rho_crit0*Omega_r*a^-4*M and pi_s= rho_rad_ref(a_ref/a)^4*P
are both used in Einstein H constraint and s equation.

Use dimensionless S=s/H_ref, E=H/H_ref, tau=H_ref*(t-t_ref),
x=ln(a/a_ref). H_ref=original FLRW H(a_ref), s_ref=q_ref H_ref.
d[tau,b,S]/dx=[1/E,S/E,-3S+(3 H0^2/Href^2)Omega_r*a^-4 P/E].
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import hashlib,math,sys
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp

HERE=Path(__file__).resolve().parent
SOURCE_CANDIDATES=(HERE.parent/"rei_axbi_background_supplier_20261015",
                   HERE.parent/"background_suppliers/bass_20261015")
PARENT=next((p for p in SOURCE_CANDIDATES if (p/"axbi_provider.py").is_file()),None)
if PARENT is None:raise FileNotFoundError("Original AX03 source-locked supplier must be adjacent")
sys.path.insert(0,str(PARENT))
from axbi_provider import Background,Family,_read_lock,LOCK_SHA

@lru_cache(maxsize=8)
def gauss64(order=64):
    if not isinstance(order,int) or isinstance(order,bool) or order not in (16,32,64,96,128):
        raise ValueError("supported angular resolution 16,32,64,96,128")
    u,w=leggauss(order)
    u.flags.writeable=False
    w.flags.writeable=False
    return u,w/2

def p2(mu):
    return .5*(3*np.asarray(mu)**2-1)

def moments(b,kappa,*,order=64):
    b=np.asarray(b,dtype=float)
    kappa=np.asarray(kappa,dtype=float)
    if not np.isfinite(b).all() or not np.isfinite(kappa).all() or np.any(abs(kappa)>.5):
        raise ValueError("source positivity |kappa|<=0.5 and finite b")
    b,kappa=np.broadcast_arrays(b,kappa)
    # Exact isotropic FLRW equilibrium; prevent O(1e-16) quadrature noise
    # from spuriously sourcing shear in the zero-shear zero-stress control.
    if b.ndim==0 and b==0.0 and kappa==0.0:
        return (1.0,0.0)
    u,w=gauss64(order)
    # relative momentum energy stable in the explored small-b domain,
    # input b outside envelope triggers no silent source extrapolation.
    if np.any(abs(b)>.25):raise ValueError("conditional small-Bianchi anisotropy |b|<=.25")
    ee=np.exp(2*b[...,None])
    zz=np.exp(-4*b[...,None])
    rr=np.sqrt(ee*(1-u*u)+zz*u*u)
    mu2=zz*u*u/(rr*rr)
    W=1+kappa[...,None]*p2(u)
    mass=np.sum(w*W*rr,axis=-1)
    pp=np.sum(w*W*rr*(1.5*mu2-.5),axis=-1)/3.
    exact_flrw=(b==0.0)&(kappa==0.0)
    mass=np.where(exact_flrw,1.0,mass)
    pp=np.where(exact_flrw,0.0,pp)
    if np.any(mass<=0) or not np.isfinite([np.min(mass),np.max(mass),np.min(pp),np.max(pp)]).all():
        raise ArithmeticError("invalid positive radiation moments")
    return (float(mass),float(pp)) if mass.ndim==0 else (mass,pp)

@dataclass(frozen=True)
class Initial:
    q_ref:float
    kappa:float
    def __post_init__(self):
        lock=_read_lock()
        if not math.isfinite(self.q_ref) or self.q_ref not in lock["q_ref_family"]:
            raise ValueError("not a frozen signed shear q")
        if not math.isfinite(self.kappa) or abs(self.kappa)>.5:
            raise ValueError("initial massless radiation quadrupole must yield positive W")
    @property
    def initial_pi_over_rad_energy(self):
        return self.kappa/15

class KineticStressBackground:
    def __init__(self,initial:Initial,*,order=64,rtol=3e-12,atol=2e-14):
        self.initial=initial;self.order=order
        source=_read_lock()
        c=source["cosmology"];clock=source["clock"]
        self.source_lock_sha256=LOCK_SHA
        self.aref=clock["a_ref"];self.aend=clock["a_end"]
        self.xmax=math.log(self.aend/self.aref)
        self.h0=float(c["H0_per_s"])
        self.om=float(c["Omega_m"])
        self.orad=float(c["Omega_r"])
        self.ol=float(c["Omega_lambda"])
        self.href=self.h0*math.sqrt(self.om/self.aref**3+self.orad/self.aref**4+self.ol)
        self.f0=(self.h0/self.href)**2
        if not(1e-15<=rtol<=1e-8 and 1e-16<=atol<=1e-8):
            raise ValueError("strict positive ODE tolerances")
        def rhs(x,Y):
            b,S=Y[1],Y[2]
            m,p=moments(b,initial.kappa,order=self.order)
            a=self.aref*math.exp(x)
            E2=self.f0*(self.om/a**3+self.ol+self.orad/a**4*m)+S*S
            if E2<=0:raise ArithmeticError("Einstein Hamiltonian positivity")
            E=math.sqrt(E2)
            source_strength=3*self.f0*self.orad/a**4*p
            return [1/E,S/E,-3*S+source_strength/E]
        self.solution=solve_ivp(rhs,(0.,self.xmax),
           (0.,0.,initial.q_ref),method="DOP853",dense_output=True,
           rtol=rtol,atol=atol)
        if not self.solution.success:raise ArithmeticError(self.solution.message)
    def fields(self,x):
        x=np.asarray(x,dtype=float)
        if not np.isfinite(x).all() or np.any(x<0) or np.any(x>self.xmax):
            raise ValueError("source x domain")
        Y=self.solution.sol(x)
        tau,b,S=Y
        a=self.aref*np.exp(x)
        m,p=moments(b,self.initial.kappa,order=self.order)
        E2=self.f0*(self.om/a**3+self.ol+self.orad/a**4*m)+S*S
        E=np.sqrt(E2);H=self.href*E;shear=self.href*S
        epsrad_to_crit=self.orad/a**4*m
        pi_to_rad= p/m
        delta_rad_rho=self.orad/a**4*(m-1)
        z=1/a-1
        result=dict(x=x,a=a,zbar=z,elapsed_proper_s=tau/self.href,
          b=b,s_over_href=S,s_per_s=shear,
          h_per_s=H,href_flrw_per_s=self.href,
          h2_FLRW_reference_per_s2=(self.h0**2)*(self.om/a**3+self.ol+self.orad/a**4),
          h_perp_per_s=H-shear,h_parallel_per_s=H+2*shear,
          a_perp=a*np.exp(-b),a_parallel=a*np.exp(2*b),
          radiation_monopole_M=m,radiation_P=p,
          radiation_density_over_crit_today=epsrad_to_crit,
          radiation_delta_over_crit_today=delta_rad_rho,
          pi_over_rad_energy=pi_to_rad,
          pi_energy_over_crit_today=self.orad/a**4*p,
          pi_ab_over_crit_today=np.stack([-self.orad/a**4*p,-self.orad/a**4*p,
                                          2*self.orad/a**4*p],axis=-1),
          d_tau_dx=1/E,db_dx=S/E,
          dS_dx=-3*S+3*self.f0*self.orad/a**4*p/E)
        if x.ndim==0:
            return {k:float(np.asarray(v)) if k!="pi_ab_over_crit_today"
                 else [float(y) for y in v] for k,v in result.items()}
        return result
    def table(self,n=501):
        if not isinstance(n,int) or isinstance(n,bool) or n<3 or n>50000:
            raise ValueError("positive bounded rows")
        return self.fields(np.linspace(0,self.xmax,n))
    def at_a(self,a):
        a=float(a)
        if not math.isfinite(a) or not self.aref<=a<=self.aend:
            raise ValueError("source scale domain")
        if a==self.aref:x=0.
        elif a==self.aend:x=self.xmax
        else:x=math.log(a/self.aref)
        return self.fields(x)

def pilot():
    combos=[(0,0),(0,.2),(0,-.2),(.005,0),(-.005,0),(.005,.2),(.005,-.2),(.01,.2),(-.01,.2),(.01,0)]
    out=[]
    for q,k in combos:
        s=KineticStressBackground(Initial(q,k))
        p=s.at_a(s.aend)
        old=Background(Family(q)).at_a(s.aend)
        out.append(dict(q_ref=q,kappa=k,pi_ref_over_epsrad=k/15,
                        b_end=p["b"],s_over_H_end=p["s_per_s"]/p["h_per_s"],
                        t_elapsed_s=p["elapsed_proper_s"],
                        b_difference_from_stressfree_original=p["b"]-old["b"],
                        t_difference_from_stressfree_original=p["elapsed_proper_s"]-old["proper_elapsed_s"],
                        radiation_M_end=p["radiation_monopole_M"],
                        pi_over_rad_energy_end=p["pi_over_rad_energy"]))
    return {"schema":"bass.rei.axbi.initial_quad_stress_background.v1","lock_sha256":LOCK_SHA,"cases":out}
if __name__=="__main__":
    import argparse,json
    p=argparse.ArgumentParser();p.add_argument("--output",type=Path)
    a=p.parse_args()
    j=pilot()
    if a.output:
        if a.output.exists():raise FileExistsError(a.output)
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(j,indent=2)+"\n")
    print(json.dumps(j,indent=2))
