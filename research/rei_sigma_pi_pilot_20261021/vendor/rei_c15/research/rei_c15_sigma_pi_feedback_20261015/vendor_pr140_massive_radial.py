"""PR137 gamma/nu+Thomson Einstein coupled to original BASS160 finite-mass Vlasov.

- Exact BASS-source 96-point FD radial quadrature, axisymmetric positive W.
- l=0,2, velocity indices i=0..imax are integrated as actual ODE states.
- Higher index and l=4 missing boundary moments come from the exact
  collisionless momentum characteristic, NOT zero/i-geometric closures.
- The Hamiltonian and Einstein shear default to ACTUALLY EVOLVED
  J0(0),J2(0); the exact Vlasov moments are an independent numerical
  oracle. An optional exact-Vlasov owner is retained as a control.
- Original Omega_m dust reduced by fm; massive fraction restricted to
  nonbaryonic budget. Gamma/nu remains PR137's separate energy/number
  unpolarized Thomson source with optional frozen real H/He n_e(a).
- Neither full polarized Thomson nor photoionization backreaction admitted.
All physical time, mass, H and pressure are source-normalized, metric -+++.
"""
from __future__ import annotations
import math
import time
from dataclasses import dataclass
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp
from species_hierarchy import SpeciesHierarchy

SQRT3=math.sqrt(3)
BASS160_SHA="1857567475b1c8586298f868e5420aae7a72e8e1ba69cce6a5b21bfca4fdd790"


def P2(x): return (3*x-1)/2
def P4(x): return (35*x*x-30*x+3)/8


@dataclass(frozen=True)
class RadialTowers:
    """Normalized J^i_0, axial J^i_2 and J^i_4, per initial massive energy."""
    j0:np.ndarray
    j2:np.ndarray
    j4:np.ndarray


class MassiveRadialGrid:
    def __init__(self,mass=30.,nr=96,nmu=32):
        if not (math.isfinite(mass) and 3<=mass<=1e5):
            raise ValueError("BASS source mass/Tref not in [3,1e5]")
        if not (isinstance(nr,int) and 16<=nr<=256 and
                isinstance(nmu,int) and nmu%2==0 and 8<=nmu<=256):
            raise ValueError("positive bounded Gauss radial/angle nodes")
        z,w=leggauss(nr)
        self.q=3*(1+z)/(1-z)
        self.rw=(6*w/(1-z)**2)*self.q**2/(1+np.exp(np.minimum(self.q,700)))
        self.mass=float(mass)
        self.mu,self.wmu=leggauss(nmu)
        self.wmu*=.5
        self.mu2=self.mu**2
        self.p2=P2(self.mu2)
        self.norm=float(np.dot(self.rw,np.hypot(self.mass,self.q)))
        if self.norm<=0:raise ArithmeticError("massive reference normalization")

    def moments(self,x,b,A=0.,imax=4):
        if not (math.isfinite(x) and math.isfinite(b) and
                0<=x<=4 and abs(b)<=1 and math.isfinite(A)
                and -1<=A<=2 and isinstance(imax,int) and 2<=imax<=7):
            raise ValueError("massive radial input outside bounded source")
        r=math.exp(-x)
        eq=math.exp(2*b);ez=math.exp(-4*b)
        R2=eq*(1-self.mu2)+ez*self.mu2
        p2=(r*self.q[:,None])**2*R2[None,:]
        E=np.sqrt(self.mass**2+p2)
        vv=p2/E**2
        mu2phys=ez*self.mu2/R2
        W=self.wmu*(1+A*self.p2)
        base=r**3/self.norm*self.rw[:,None]*W[None,:]*E
        j0=np.empty(imax+1);j2=np.empty(imax+1);j4=np.empty(imax+1)
        vpow=np.ones_like(E)
        q2=P2(mu2phys)[None,:];q4=P4(mu2phys)[None,:]
        for i in range(imax+1):
            j0[i]=np.sum(base*vpow)
            vpow*=vv
            j2[i]=np.sum(base*vpow*q2)
            j4[i]=np.sum(base*vpow*vv*q4)
        return RadialTowers(j0,j2,j4)

    def batch(self,xs,bs,A=0.,imax=2,chunk=16):
        xs=np.asarray(xs,float);bs=np.asarray(bs,float)
        if (xs.ndim!=1 or bs.shape!=xs.shape or xs.size<1 or
            not isinstance(chunk,int) or not 1<=chunk<=2048):
            raise ValueError("source chunk domain")
        dest=np.empty((xs.size,3,imax+1))
        for start in range(0,len(xs),chunk):
            stop=min(len(xs),start+chunk)
            r=np.exp(-xs[start:stop])[:,None,None]
            eq=np.exp(2*bs[start:stop])[:,None,None]
            ez=np.exp(-4*bs[start:stop])[:,None,None]
            R2=eq*(1-self.mu2)+ez*self.mu2
            mom2=(r*self.q[None,:,None])**2*R2
            E=np.sqrt(self.mass**2+mom2)
            v2=mom2/E**2
            mu_phys2=ez*self.mu2/R2
            W=self.wmu*(1+A*self.p2)
            base=r**3/self.norm*self.rw[None,:,None]*W[None,None,:]*E
            q2=P2(mu_phys2);q4=P4(mu_phys2)
            pow_v=np.ones_like(E)
            for i in range(imax+1):
                dest[start:stop,0,i]=(base*pow_v).sum(axis=(1,2))
                pow_v*=v2
                dest[start:stop,1,i]=(base*pow_v*q2).sum(axis=(1,2))
                dest[start:stop,2,i]=(base*pow_v*v2*q4).sum(axis=(1,2))
        return dest


def scalar_hierarchy_rhs(j0,j2,j4,H,s,imax):
    """Exact LRS tensor contraction of original BASS Lewis–Challinor Eq12.

    Tensor J^i_(ab)=j2[i]*diag(-1/3,-1/3,2/3); J^i_(abcd)
    =j4[i]*STF(z_a z_b z_c z_d). Wolfram exact tensor contraction
    STF(z^4):sigma -> (36/35)*s*STF(z^2).
    No finite velocity-index truncation: upper indices are source exact.
    """
    if (len(j0)<imax+3 or len(j2)<imax+2 or len(j4)<imax+1
        or not np.isfinite(H) or not np.isfinite(s)):
        raise ValueError("incomplete BASS J_i or clock hierarchy")
    d0=np.empty(imax+1);d2=np.empty(imax+1)
    for i in range(imax+1):
        a2_prev=j2[i-1] if i else 0.
        a4_prev=j4[i-1] if i else 0.
        d0[i]=(-H*((3+2*i)*j0[i]+(1-2*i)*j0[i+1])
               +2*s*(-2*i*a2_prev+(2*i-1)*j2[i]))
        d2[i]=(
            -H*((5+2*i)*j2[i]+(-1-2*i)*j2[i+1])
            -(2/7)*s*((7+4*i)*j2[i]-(2+4*i)*j2[i+1])
            +(36/35)*s*(-2*i*a4_prev+(1+2*i)*j4[i])
            +(2/5)*s*((1+2*i)*j0[i+2]-(5+2*i)*j0[i+1])
        )
    return d0,d2


class MassiveRadialSpecies(SpeciesHierarchy):
    """Couple physical nonbaryonic BASS160 J0/J2 to PR137 gamma/nu Einstein.

    No phenomenological matter viscosity and NO thermal u double count.
    The extra l=0,2 i-towers are real time-evolved numerical states,
    but higher exact Vlasov moments close their source equations.
    """

    def __init__(self,source,Tcmb0_K,ellmax=8,*,Sigma_ref=0.,
                 orientation=0,kappa_gamma=.2,kappa_nu=.2,
                 ne_source=None,mass_fraction=.1,massive_A=.5,
                 mass_over_T_ref=30.,imax=2,nr=96,nmu=32,
                 omega_b=.049309230511847414,gravity_owner="hierarchy"):
        if not (math.isfinite(mass_fraction) and 0<=mass_fraction<1):
            raise ValueError("nonbaryonic source fraction")
        if (not math.isfinite(omega_b) or omega_b<=0 or
            source.omega_m*mass_fraction>source.omega_m-omega_b+1e-14):
            raise ValueError("massive fraction overlaps baryonic Omega_m")
        if not (math.isfinite(massive_A) and -1<=massive_A<=2):
            raise ValueError("massive positive W(mu) source")
        if not (isinstance(imax,int) and 0<=imax<=4):
            raise ValueError("bounded i index [0,4]")
        if gravity_owner not in ("hierarchy","exact_vlasov"):
            raise ValueError("gravity owner must be hierarchy or exact_vlasov")
        self.gravity_owner=gravity_owner
        self.fmass=float(mass_fraction)
        self.Amass=float(massive_A)
        self.imax=imax
        self.massive=MassiveRadialGrid(mass_over_T_ref,nr,nmu)
        super().__init__(source,Tcmb0_K,ellmax,
            Sigma_ref=Sigma_ref,orientation=orientation,
            kappa_gamma=kappa_gamma,kappa_nu=kappa_nu,
            ne_source=ne_source,matter_nu_viscosity=0.)
        self.main_size=4+4*self.n
        self.fmass_norm=source.omega_m*self.fmass/source.aref**3
        self.dust_omega=source.omega_m*(1-self.fmass)
        self.n_rhs=0

    def initial_state(self):
        base=super().initial_state()
        j=self.massive.moments(0.,0.,self.Amass,max(2,self.imax+2))
        return np.r_[base,j.j0[:self.imax+1],j.j2[:self.imax+1]]

    def fields(self,x,y):
        base=super().fields(x,y[:self.main_size])
        j=self.massive.moments(float(x),float(y[1]),self.Amass,
                               max(2,self.imax+2))
        a=base["a"];s=base["s"]
        dust=self.dust_omega/a**3
        offset=self.main_size
        N=self.imax+1
        # The finite hierarchy is a physically active Einstein source,
        # unlike a read-only passive regressor. The upper moments remain
        # actual source-bound Vlasov closure data.
        if self.gravity_owner=="hierarchy":
            J00=float(y[offset])
            J20=float(y[offset+N])
            J01=float(y[offset+1]) if self.imax>=1 else float(j.j0[1])
        else:
            J00=float(j.j0[0])
            J20=float(j.j2[0])
            J01=float(j.j0[1])
        if not all(math.isfinite(z) for z in (J00,J20,J01)) or J00<=0:
            raise FloatingPointError("nonpositive integrated massive energy")
        if J01<0 or abs(J20)>J01*(1+3e-8):
            raise FloatingPointError("massive PSTF pressure outside positive momentum cone")
        kinetic=self.fmass_norm*J00
        H2=self.source.h0**2*(dust+kinetic+
               base["rad_energy_norm"]+self.source.omega_lambda)+s*s
        if not math.isfinite(H2) or H2<=0:
            raise FloatingPointError("nonpositive Einstein Hamiltonian")
        H=math.sqrt(H2)
        pim=self.fmass_norm*J20/3
        base.update({
            "H":H,"Sigma":SQRT3*abs(s)/H,
            "dust_energy_norm":dust,"massive_energy_norm":kinetic,
            "massive_mean_pressure_norm":self.fmass_norm*J01/3,
            "gravity_owner":self.gravity_owner,
            "massive_energy_exact_minus_hierarchy_norm":
                self.fmass_norm*(j.j0[0]-J00),
            "massive_pi_exact_minus_hierarchy_norm":
                self.fmass_norm*(j.j2[0]-J20)/3,
            "Pi_matter_norm":pim,
            "Pi_matter_J_m3":self.source.rhocrit_j_m3*pim,
            "exact_radial_towers":j,
            "Hamiltonian_norm":H2,
        })
        return base

    def rhs(self,x,y):
        self.n_rhs+=1
        w=self.fields(x,y)
        H=w["H"];s=w["s"];v=s/H;gamma=w["GammaT"]/H
        eg,ng,en,nn=(w["E_gamma"],w["N_gamma"],w["E_nu"],w["N_nu"])
        d_eg=v*(self.energy_matrix@eg)-gamma*self.thomson*eg
        d_ng=v*(self.number_matrix@ng)-gamma*self.thomson*ng
        d_en=v*(self.energy_matrix@en)
        d_nn=v*(self.number_matrix@nn)
        source_pi=w["Pi_radiation_norm"]+w["Pi_matter_norm"]
        dv=-3*y[2]+3*self.source.h0**2/(self.source.href*H)*source_pi

        N=self.imax+1;offset=self.main_size
        jexact=w["exact_radial_towers"]
        j0=jexact.j0.copy();j2=jexact.j2.copy()
        j0[:N]=y[offset:offset+N]
        j2[:N]=y[offset+N:offset+2*N]
        dj0,dj2=scalar_hierarchy_rhs(j0,j2,jexact.j4,H,s,self.imax)

        return np.r_[self.source.href/H,v,dv,0.,
                     d_eg,d_ng,d_en,d_nn,dj0/H,dj2/H]

    def integrate(self,n=301,rtol=5e-11,atol=1e-13):
        t=time.perf_counter()
        sol=solve_ivp(self.rhs,(0,self.source.xmax),self.initial_state(),
            t_eval=np.linspace(0,self.source.xmax,n),
            method="DOP853",rtol=rtol,atol=atol)
        wall=time.perf_counter()-t
        if not sol.success:
            raise RuntimeError("SOURCE_MASSIVE_HIERARCHY_ODE_FAILURE")
        samples=[self.fields(float(x),sol.y[:,i]) for i,x in enumerate(sol.t)]
        if any(abs(w["N_gamma"][0]-1)>5e-11 or
               abs(w["N_nu"][0]-1)>5e-11 for w in samples):
            raise RuntimeError("number conservation failure")
        return sol,samples,wall
