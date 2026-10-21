"""Bianchi-I Einstein + collisionless radiation/matter anisotropic-stress pilot.

Source-intent:
 - Primary amplitude: Sigma = sqrt(sigma_ab sigma^ab/2)/H = sqrt(3)|s|/H.
 - Separate orientation epsilon = sign(s). Sigma alone does NOT specify axis
   orientation. Historical REI q_ref is allowed ONLY at provenance adapter.
 - Radiation: initially isotropic massless effective Omega_r, Liouville
   transported exactly by three conserved Bianchi-I spatial momenta; angular
   Gauss-Legendre quadrature resolves its pressure tensor, not a guessed
   quadrupole ansatz.
 - Matter: trace-preserving collisionless nonrelativistic H+He+e thermal
   pressure tensor, plus a separately diagnosed isotropized-gas comparator.
 - Geometry: integrate the *Einstein-sourced* shear equation and Hamiltonian
   constraint under homogeneous stress-conserving closure, not the previous
   stress-free prescribed model.
 - No stellar ionizing emissivity, chemical reactions, gas collisions,
   baryon radiation drag, atomic polarization or native REI production solve.
   This is a scientifically scoped homogeneous pilot, NOT a completion claim.

Metric signature (-,+,+,+):
 ds²=-c²dt²+a(t)²[e^{-2b}(dx²+dy²)+e^{4b}dz²],
 Hperp=H-s, Hparallel=H+2s, s=db/dt.
 pi_i^j=diag(-Pi/3,-Pi/3,+2Pi/3), Pi=Pparallel-Pperp.
 Einstein:
 H²= (8 pi G/(3 c²)) * (epsilon_mrest+u_m+epsilon_r+epsilon_L) + s²;
 ds/dt+3Hs= (8 pi G/(3 c²)) * (Pi_rad+Pi_m).
 Conservation exactly:
 depsilon_r/dt+4H epsilon_r+2s Pi_rad=0;
 du_m/dt+5H u_m+2s Pi_m=0.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

C_SI=299792458.0
G_SI=6.67430e-11
K_B_SI=1.380649e-23
M_P_SI=1.67262192369e-27
MPC_SI=3.0856775814913673e22
SQRT3=math.sqrt(3.0)
KAPPA=8.0*math.pi*G_SI/(3.0*C_SI*C_SI)


def sigma_from_signed_axis(s:float,h:float)->tuple[float,int]:
    """Convert shear eigenvalues (-s,-s,2s) to magnitude and axis branch."""
    if not (math.isfinite(s) and math.isfinite(h) and h>0):
        raise ValueError("positive H and finite axis shear required")
    return SQRT3*abs(s)/h, (1 if s>0 else -1 if s<0 else 0)


def historical_axis_ratio_to_sigma(axis_ratio:float)->tuple[float,int]:
    """Boundary adapter ONLY for immutable stress-free REI source q_ref=s/H_FLRW.

    The conversion is exact when H²=H_FLRW²+s² and the gas kinetic energy
    contribution to the constraint is omitted, as in the frozen REI model.
    New experiments should specify Sigma and orientation instead.
    """
    if not math.isfinite(axis_ratio):
        raise ValueError("nonfinite historical source amplitude")
    sigma=SQRT3*abs(axis_ratio)/math.hypot(1.,axis_ratio)
    return sigma,(1 if axis_ratio>0 else -1 if axis_ratio<0 else 0)


@dataclass(frozen=True)
class SigmaPiScenario:
    h0_km_s_mpc:float
    omega_m:float
    omega_r:float
    omega_lambda:float
    omega_b_h2:float
    helium_Y:float
    tcmb0_K:float
    z_ref:float
    z_end:float
    x_e_ref:float
    gas_T_ref_K:float
    source_scenario_sha256:str
    gas_owner:str
    _derived:dict=field(init=False,repr=False,compare=False)

    def __post_init__(self):
        p=(self.h0_km_s_mpc,self.omega_m,self.omega_r,
           self.omega_lambda,self.omega_b_h2,self.helium_Y,
           self.tcmb0_K,self.z_ref,self.z_end,self.gas_T_ref_K)
        if not all(math.isfinite(v) for v in p):
            raise ValueError("all physical reference quantities must be finite")
        if (self.h0_km_s_mpc<=0 or self.omega_m<=0 or self.omega_r<0 or
            self.omega_lambda<0 or self.omega_b_h2<=0 or
            not (0<self.helium_Y<1) or self.tcmb0_K<=0 or
            not(0<=self.z_end<self.z_ref) or not (0<=self.x_e_ref<=1)
            or self.gas_T_ref_K<=0):
            raise ValueError("unphysical cosmological or gas source configuration")
        if abs(self.omega_m+self.omega_r+self.omega_lambda-1)>1e-12:
            raise ValueError("source reference is spatially flat by scope")
        h0=self.h0_km_s_mpc*1000/MPC_SI
        a_ref=1/(1+self.z_ref)
        Href=h0*math.sqrt(self.omega_m/a_ref**3+
                        self.omega_r/a_ref**4+self.omega_lambda)
        rho_crit=3*h0*h0/(8*math.pi*G_SI)
        omega_b=self.omega_b_h2/(self.h0_km_s_mpc/100)**2
        nH0=(1-self.helium_Y)*omega_b*rho_crit/M_P_SI
        fHe=self.helium_Y/(4*(1-self.helium_Y))
        nPart=nH0*a_ref**-3*(1+fHe+self.x_e_ref)
        P0=nPart*K_B_SI*self.gas_T_ref_K
        E_R0=(3*C_SI*C_SI*h0*h0/(8*math.pi*G_SI)) *self.omega_r*a_ref**-4
        object.__setattr__(self,"_derived",dict(h0=h0,a_ref=a_ref,
          Href=Href, fHe=fHe,nH0=nH0,p0=P0,eps_r0=E_R0))

    @classmethod
    def from_locked_json(cls,path:str|Path, *,gas_case="baseline",
                         donor_path:str|Path|None=None):
        raw=Path(path).read_bytes()
        d=json.loads(raw)
        if d.get("schema")!="rei.axbi.scenario_lock.v1":
            raise ValueError("REI scenario physics identity not recognized")
        c=d["cosmology"];init=d["gas_initial"];iv=d["interval"]
        if c["omega_b_formula"]!="0.0224/(0.674^2)" or c["h0_km_s_mpc"]!=67.4:
            raise ValueError("baryon density owner changed; explicit adapter revision required")
        gasx=float(init["x_HII"])
        gasT=float(c["tcmb0_k"])*(1+float(iv["zbar_start"]))**2/(150*(.0224/.023)**.4)
        source="frozen_REI_approximate_conditional_IC"
        if gas_case=="donor":
            if donor_path is None:
                raise ValueError("need authentic source-pinned REC donor")
            donor=json.loads(Path(donor_path).read_text())
            if (donor.get("schema")!="rei.conditional.primordial_donor_candidate.v1"
                or donor.get("source_rei_scenario_sha256")!=hashlib.sha256(raw).hexdigest()
                or donor.get("activation")!="DISABLED_REQUIRES_SEPARATE_REI_SENSITIVITY_CAMPAIGN"):
                raise ValueError("REC donor must stay source-bound and disabled")
            candidate=donor["candidate_initial_gas"]
            if candidate["x_HeII"]!=0 or candidate["x_HeIII"]!=0:
                raise ValueError("donor He neutral projection required")
            gasx=float(candidate["x_HII"])
            gasT=float(candidate["Tgas_K"])
            source="native_HyRec2012_FULL_q0_conditional_helium_neutral_projection"
        elif gas_case!="baseline":
            raise ValueError("unknown gas reference")
        return cls(h0_km_s_mpc=float(c["h0_km_s_mpc"]),
            omega_m=float(c["omega_m"]),omega_r=float(c["omega_r"]),
            omega_lambda=1-float(c["omega_m"])-float(c["omega_r"]),
            omega_b_h2=.0224,helium_Y=float(c["helium_mass_fraction"]),
            tcmb0_K=float(c["tcmb0_k"]),z_ref=float(iv["zbar_start"]),
            z_end=float(iv["zbar_end"]),x_e_ref=gasx,gas_T_ref_K=gasT,
            source_scenario_sha256=hashlib.sha256(raw).hexdigest(),
            gas_owner=source)

    @property
    def a_ref(self):return self._derived["a_ref"]
    @property
    def h_flrw_ref(self):return self._derived["Href"]
    @property
    def gas_pressure_ref(self):return self._derived["p0"]
    @property
    def radiation_energy_ref(self):return self._derived["eps_r0"]


class RadiationKillingGL:
    """Exact angle-resolved collisionless initially isotropic radiation.

    Initial reference directions mu0 have uniform energy density. Characteristic
    redshift factor R = sqrt(exp(2b)(1-mu0²)+exp(-4b) mu0²).
    Since the physical phase-space volume scales a^-3 and energy scales a^-1 R,
    epsilon_rad / epsilon_rad_iso = <R>_mu0.
    Pressure Ppara=epsilon_iso <exp(-4b) mu0²/R>,
    Pperp=epsilon_iso <exp(2b)(1-mu0²)/(2R)>.
    The quadrupole is Pi_rad=Ppara-Pperp.
    """
    def __init__(self,n_mu:int=64):
        if not isinstance(n_mu,int) or n_mu<8 or n_mu%2 or n_mu>512:
            raise ValueError("even Gauss-Legendre order 8..512")
        x,w=np.polynomial.legendre.leggauss(n_mu)
        self.mu2=x[n_mu//2:]**2
        self.w=w[n_mu//2:]
        if abs(float(np.sum(self.w))-1.)>1e-14:
            raise ArithmeticError("failed positive normalized GL half-sphere")

    def factors(self,b:float):
        if not math.isfinite(b) or abs(b)>30:
            raise ValueError("bounded log axial anisotropy required")
        if b==0.0:
            return 1.0, 0.0, 0.0, (1/3,1/3)
        p=math.exp(2*b);z=math.exp(-4*b)
        R=np.sqrt(p*(1-self.mu2)+z*self.mu2)
        monopole=math.fsum((self.w*R).tolist())
        delta=math.fsum((self.w*(R-1.)).tolist())
        ppara=math.fsum((self.w*z*self.mu2/R).tolist())
        pperp=.5*math.fsum((self.w*p*(1-self.mu2)/R).tolist())
        # Independent trace closure should not be repaired by normalization.
        if abs(ppara+2*pperp-monopole)>4e-14*max(monopole,1):
            raise ArithmeticError("radiation pressure trace inconsistency")
        return monopole, ppara-pperp, delta, (ppara,pperp)

    def factors_batch(self,b):
        """Memory-bounded direct positive-half angular NumPy vectorization."""
        x=np.asarray(b,dtype=float)
        if x.ndim!=1 or np.any(~np.isfinite(x)) or np.any(np.abs(x)>30):
            raise ValueError("finite 1d log-axis batches only")
        result=np.empty((len(x),3),dtype=float)
        for start in range(0,len(x),1024):
            sub=x[start:start+1024,None]
            p=np.exp(2*sub);z=np.exp(-4*sub)
            r=np.sqrt(p*(1-self.mu2)+z*self.mu2)
            result[start:start+1024,0]=r@self.w
            result[start:start+1024,1]=(
                (z*self.mu2/r-.5*p*(1-self.mu2)/r)@self.w)
            result[start:start+1024,2]=(r-1.)@self.w
        return result


@dataclass(frozen=True)
class SigmaPiState:
    eta:float
    b:float
    shear_s_inv:float
    H_s_inv:float
    Sigma:float
    orientation:int
    rad_energy_J_m3:float
    rad_Pi_J_m3:float
    matter_kin_energy_J_m3:float
    matter_Pi_J_m3:float
    matter_pbar_J_m3:float
    constraint_h2_s_inv2:float

    def __post_init__(self):
        if not 0<=self.Sigma<math.sqrt(3)+1e-11 or self.orientation not in (-1,0,1):
            raise ValueError("invalid normalized shear and branch")


class SigmaPiDynamics:
    def __init__(self,model:SigmaPiScenario, *,sigma_ref:float,
                 orientation:int, closure:str="collisionless_matter",
                 geometry:str="einstein_stress",n_mu:int=64):
        if not math.isfinite(sigma_ref) or not (0<=sigma_ref<math.sqrt(3)):
            raise ValueError("Sigma requires 0<=Sigma<sqrt(3)")
        if orientation not in (-1,0,1) or (sigma_ref==0)!=(orientation==0):
            raise ValueError("Sigma magnitude and orientation must agree")
        if closure not in ("collisionless_matter","isotropized_matter"):
            raise ValueError("invalid matter stress closure")
        if geometry not in ("einstein_stress","prescribed_source"):
            raise ValueError("geometry mode not implemented")
        self.model=model
        self.sigma_ref=sigma_ref
        self.orientation=orientation
        self.closure=closure
        self.geometry=geometry
        self.angular=RadiationKillingGL(n_mu)
        self.H_ref=model.h_flrw_ref
        p0=model.gas_pressure_ref
        base_ratio=(self.H_flrw(model.a_ref)/self.H_ref)**2+(
            KAPPA*(1.5*p0)/self.H_ref**2)
        magnitude=sigma_ref/math.sqrt(3-sigma_ref**2)*math.sqrt(base_ratio)
        self.initial_shear_dimless=orientation*magnitude

    def H_flrw(self,a):
        p=self.model
        d=p._derived
        return d["h0"]*math.sqrt(p.omega_m*a**-3+
                 p.omega_r*a**-4+p.omega_lambda)

    def matter(self,eta,b):
        p0=self.model.gas_pressure_ref*math.exp(-5*eta)
        if self.closure=="collisionless_matter":
            pperp=p0*math.exp(2*b)
            ppara=p0*math.exp(-4*b)
        else:
            pperp=ppara=p0
        return .5*(2*pperp+ppara),ppara-pperp,(2*pperp+ppara)/3

    def moments(self,eta,b):
        p=self.model
        eps0=p.radiation_energy_ref*math.exp(-4*eta)
        A,pi,delta,press=self.angular.factors(b)
        return eps0*A,eps0*pi,eps0*delta,press

    def inspect(self,eta,b,shear_dimensionless):
        p=self.model
        a=p.a_ref*math.exp(eta)
        epsrad,pir,rad_diff,_=self.moments(eta,b)
        um,pim,pbar=self.matter(eta,b)
        if self.geometry=="prescribed_source":
            # Source's frozen stress-free perfect fluid metric H²=Hfl²+s²;
            # radiation/matter pi remain diagnostics but do not source Einstein.
            H2=self.H_flrw(a)**2+(shear_dimensionless*self.H_ref)**2
        else:
            H2=(self.H_flrw(a)**2+(shear_dimensionless*self.H_ref)**2+
                KAPPA*(rad_diff+um))
        if not math.isfinite(H2) or H2<=0:
            raise FloatingPointError("Einstein constraint not positive")
        H=math.sqrt(H2)
        s=shear_dimensionless*self.H_ref
        sigma,orientation=sigma_from_signed_axis(s,H)
        return SigmaPiState(
            eta=eta,b=b,shear_s_inv=s,H_s_inv=H,
            Sigma=sigma,orientation=orientation,
            rad_energy_J_m3=epsrad,rad_Pi_J_m3=pir,
            matter_kin_energy_J_m3=um,matter_Pi_J_m3=pim,
            matter_pbar_J_m3=pbar,constraint_h2_s_inv2=H2
        )

    def rhs(self,eta,y):
        if len(y) not in (2,3):
            raise ValueError("expected b, shear and optional proper clock")
        b,s_scaled=y[:2]
        state=self.inspect(eta,b,s_scaled)
        db=s_scaled*self.H_ref/state.H_s_inv
        drive=(state.rad_Pi_J_m3+state.matter_Pi_J_m3
               if self.geometry=="einstein_stress" else 0.)
        ds=-3*s_scaled+KAPPA*drive/(self.H_ref*state.H_s_inv)
        if len(y)==3:
            return np.array([db,ds,1.0/state.H_s_inv],dtype=float)
        return np.array([db,ds],dtype=float)

    def evolution(self,*,rtol=2e-10,atol=1e-12,max_step=.015):
        p=self.model
        eta_end=math.log((1+p.z_ref)/(1+p.z_end))
        # Proper time is an actual ODE state, not the difference of two
        # enormous accumulated timestamps (the native AX03 C9 finding).
        sol=solve_ivp(self.rhs,(0.,eta_end),
             (0.,self.initial_shear_dimless,0.),method="DOP853",
             rtol=rtol,atol=np.array([atol,atol,1.0]),max_step=max_step,
             first_step=min(max_step,5e-4),dense_output=True)
        if not sol.success:
            raise RuntimeError(f"Einstein ODE failed: {sol.message}")
        return sol

    def sampled(self,sol,count:int=121):
        if count<3:raise ValueError("sample >= 3 points")
        eta=np.linspace(0,sol.t[-1],count)
        state=sol.sol(eta)
        result=[]
        for t,b,u,proper_t in zip(eta,state[0],state[1],state[2]):
            s=self.inspect(float(t),float(b),float(u))
            d=dict(eta=s.eta,elapsed_proper_t_s=float(proper_t),
                   zbar=(1+self.model.z_ref)*math.exp(-s.eta)-1,
                   Sigma=s.Sigma,orientation=s.orientation,b=s.b,
                   s_per_s=s.shear_s_inv,H_per_s=s.H_s_inv,
                   Pi_rad_J_m3=s.rad_Pi_J_m3,
                   Pi_matter_J_m3=s.matter_Pi_J_m3,
                   epsilon_rad_J_m3=s.rad_energy_J_m3,
                   u_matter_kin_J_m3=s.matter_kin_energy_J_m3,
                   constraint_H2_per_s2=s.constraint_h2_s_inv2)
            result.append(d)
        return result

    def raychaudhuri_relative_residual(self,eta,b,s_scaled,step=1e-5):
        """Independent mean Einstein evolution from constraint differentiation.

        With rest dust epsilon_rest, radiation epsilon_r and nonrel kinetic
        u_m (pbar_m=2u_m/3), the exact flat LRS evolution is

          dot(H) = -(3/2) kappa epsilon_rest - 2 kappa epsilon_r
                   -(5/2) kappa u_m - 3 s^2.

        We calculate dot(H)=H*dH/d(ln a) from a symmetric path-direction
        finite difference. No actual native REI hydro/chemistry is involved.
        """
        if self.geometry!="einstein_stress":
            raise ValueError("Raychaudhuri consistency applies to sourced Einstein")
        if not math.isfinite(step) or step<=0 or step>=.001:
            raise ValueError("required positive local differentiation interval")
        first=self.inspect(eta,b,s_scaled)
        db,ds=self.rhs(eta,(b,s_scaled))
        hp=self.inspect(eta+step,b+step*db,s_scaled+step*ds).H_s_inv
        hm=self.inspect(eta-step,b-step*db,s_scaled-step*ds).H_s_inv
        numerical=first.H_s_inv*(hp-hm)/(2*step)
        a=self.model.a_ref*math.exp(eta)
        rest_term=1.5*self.model._derived["h0"]**2*self.model.omega_m*a**-3
        expected=(-rest_term-2*KAPPA*first.rad_energy_J_m3
                  -2.5*KAPPA*first.matter_kin_energy_J_m3
                  -3*first.shear_s_inv**2)
        return abs(numerical-expected)/max(abs(expected),1e-200)

    def stress_conservation_identites(self,eta,b,db=1e-5):
        """Independently verify exact Liouville dE/db = -2(Ppara-Pperp)."""
        Er,Pr,_,_=self.moments(eta,b)
        Em,Pm,_=self.matter(eta,b)
        ep=self.moments(eta,b+db)[0]
        en=self.moments(eta,b-db)[0]
        mp=self.matter(eta,b+db)[0]
        mn=self.matter(eta,b-db)[0]
        scale_rad=max(abs(Pr)*2,Er,1e-120)
        scale_m=max(abs(Pm)*2,Em,1e-120)
        return dict(
            radiation_relative=abs((ep-en)/(2*db)+2*Pr)/scale_rad,
            matter_relative=abs((mp-mn)/(2*db)+2*Pm)/scale_m)
