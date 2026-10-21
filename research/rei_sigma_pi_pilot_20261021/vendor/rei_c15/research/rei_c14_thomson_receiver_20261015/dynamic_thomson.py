#!/usr/bin/env python3
"""C14: C13 real MD14 source-driven H/He electrons -> original PR137 BASS LRS
Einstein-Boltzmann unpolarized photon Thomson hierarchy, gamma/nu independent.

One-way coupling on ONE common prescribed Bianchi-I background/clock.
No fake reuse of PR137 stationary C11 electron path, no native AX08 mutation.
Polarization E2 and baryon Thomson recoil are missing; background backreaction
is a separately measured source term, not time-integrated into Einstein.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
import math
import sys
from pathlib import Path
import numpy as np
from scipy.integrate import quad, solve_ivp
from scipy.interpolate import PchipInterpolator

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"research/rei_c13_live_source_20261015"))
from short_interval import (Scenario,NativeStellarSource,run as run_c13,
    Background,Family,THOMSON_CGS,C_CGS,ROOT as C13_ROOT)
from vendor_pr137_lrs_boltzmann import (legendre_matrix,thomson_coeffs,
    GAMMA_PER_NE, C_SI)

SOURCE_COMMIT="5d41df647c4fd624d8a1b574f67fdd0b82ff5102"
SOURCE_GIT_BLOB="e15e1875fba7fcc4a42e257e291c54d9b540a3f0"
SOURCE_REL="research/rei_bass_hierarchy_backreaction_20261015/lrs_boltzmann.py"
SIGMA_T_M2=THOMSON_CGS*1e-4
SIGMA_T_CGS=THOMSON_CGS
K_B_SI=1.380649e-23
HBAR_SI=1.054571817e-34
A_RAD=math.pi**2 * K_B_SI**4/(15*HBAR_SI**3*C_SI**3)
G_SI=6.67430e-11
EV_CM3_TO_J_M3=1.602176634e-13
KAPPA=8*math.pi*G_SI/(3*C_SI**2)


def validate_source_sha():
    p=HERE/"vendor_pr137_lrs_boltzmann.py"
    raw=p.read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if blob!=SOURCE_GIT_BLOB:
        raise ValueError("SOURCE_PR137_BLOB_IDENTITY_NOT_MATCHED")
    if abs(GAMMA_PER_NE-C_CGS*THOMSON_CGS)/GAMMA_PER_NE>1e-14:
        raise ValueError("THOMSON_CROSS_SECTION_MISMATCH")
    return {"PR137_git_commit":SOURCE_COMMIT,"PR137_path":SOURCE_REL,
            "PR137_git_blob":blob,"PR137_sha256":hashlib.sha256(raw).hexdigest()}


@dataclass
class ElectronSource:
    a:np.ndarray
    proper_ne_cm3:np.ndarray
    donor:dict
    interpolator:PchipInterpolator

    @classmethod
    def from_real_c13(cls,donor:dict,model:Scenario):
        if (not isinstance(donor,dict) or
            donor.get("source_scale_explicit_sensitivity")!=1. or
            donor.get("q") not in (-.01,-.005,0.,.005,.01)):
            raise ValueError("REI_NATIVE_MD14_SOURCE_REQUIRED")
        data=donor["history"]
        a=np.array([v["a"] for v in data],dtype=float)
        xe=np.array([v["x_e_perH"] for v in data],dtype=float)
        if not (len(a)>=16 and np.all(np.diff(a)>0)
                and np.isfinite(a).all() and np.isfinite(xe).all()
                and np.all(xe>0)):
            raise ValueError("ACTUAL_ELECTRON_HISTORY_DOMAIN")
        density=xe*model.nh/a**3
        return cls(a,density,donor,PchipInterpolator(np.log(a),density,
                          extrapolate=False))
    def ne(self,a):
        y=self.interpolator(np.log(a))
        if not np.isfinite(y).all() or np.any(y<0):
            raise ValueError("ELECTRON_SOURCE_EXTRAPOLATION")
        return y


@dataclass(frozen=True)
class PhysicalThomson:
    kappa_gamma:float
    kappa_nu:float
    L:int=8
    scattering:bool=True
    def __post_init__(self):
        if self.L not in (4,8,12,16) or not all(
            math.isfinite(v) and -1<=v<=2 for v in
            (self.kappa_gamma,self.kappa_nu)):
            raise ValueError("POSITIVE_INITIAL_P2_AND_LMAX_REQUIRED")


def omega_gamma_fraction(model:Scenario):
    t0=2.7255
    Ecrit=3*C_SI**2*(model.h0**2)/(8*math.pi*G_SI)
    Og=A_RAD*t0**4/Ecrit
    On=model.orad-Og
    if not (0<Og<model.orad and On>0):
        raise ValueError("PHOTON_VS_NEUTRINO_DENSITY_PARTITION")
    return {"Omega_gamma":Og,"Omega_nu":On,"Omega_gamma_fraction":Og/model.orad}


@lru_cache(maxsize=8)
def _cached_source_angular_operators(lmax:int):
    """Identical PR137 owner matrices, reused as immutable source by L."""
    A_E=legendre_matrix(lmax,power=4)
    A_N=legendre_matrix(lmax,power=3)
    damping=thomson_coeffs(lmax)
    for arr in (A_E,A_N,damping):
        arr.setflags(write=False)
    return A_E,A_N,damping


class OneWayThomson:
    """Unpolarized tensor intensity and count moments evolved on original q."""
    def __init__(self, electrons:ElectronSource, config:PhysicalThomson):
        self.donor=electrons
        self.config=config
        self.scenario=Scenario(ROOT)
        self.bg=Background(Family(electrons.donor["q"]))
        self.N=config.L+1
        self.A_E,self.A_N,self.D=_cached_source_angular_operators(config.L)
        if np.max(abs(self.A_N[0]))>1e-12:
            raise ValueError("PHOTON_NUMBER_SHEAR_ROW_NOT_ZERO")
        expected=np.zeros(self.N); expected[2]=-2
        if np.max(abs(self.A_E[0]-expected))>1e-12:
            raise ValueError("PHOTON_ENERGY_SHEAR_ROW_NOT_CONSERVATIVE")
        self.mix=omega_gamma_fraction(self.scenario)

    def initial(self):
        n=self.N
        y=np.zeros(4*n+1)
        for i,k in enumerate((self.config.kappa_gamma,
                               self.config.kappa_gamma,
                               self.config.kappa_nu,
                               self.config.kappa_nu)):
            y[i*n]=1.
            y[i*n+2]=k/5
        return y

    def rates(self,x):
        a=math.exp(x)
        H=float(self.bg.mean_hubble(a))
        shear=float(self.bg.shear(a))
        gamma=float(self.donor.ne(a))*GAMMA_PER_NE
        return H,shear,gamma

    def rhs(self,x,y):
        H,shear,gamma=self.rates(x)
        alpha=shear/H
        beta=gamma/H if self.config.scattering else 0.
        yy=y[:4*self.N].reshape(4,self.N)
        ans=np.empty_like(yy)
        ans[0]=alpha*(self.A_E@yy[0])-beta*self.D*yy[0]
        ans[1]=alpha*(self.A_N@yy[1])-beta*self.D*yy[1]
        ans[2]=alpha*(self.A_E@yy[2])
        ans[3]=alpha*(self.A_N@yy[3])
        out=np.r_[ans.ravel(),gamma/H]  # Tau diagnostic even when collisions OFF.
        return out

    def run(self,steps=97,rtol=2e-11,atol=1e-13):
        if steps<3 or steps>8193:
            raise ValueError("THOMSON_SAMPLE_WINDOW")
        amin,amax=self.donor.a[[0,-1]]
        grid=np.linspace(math.log(amin),math.log(amax),steps)
        initial=self.initial()
        sol=solve_ivp(self.rhs,(grid[0],grid[-1]),initial,
          method="DOP853",dense_output=False,t_eval=grid,rtol=rtol,atol=atol)
        if not sol.success or not np.all(np.isfinite(sol.y)):
            raise RuntimeError("THOMSON_HIERARCHY_EVOLUTION_FAILURE")
        rows=[]
        max_mono_E=0.
        max_mono_N=0.
        initial_e=float(initial[0])
        for i,x in enumerate(grid):
            yy=sol.y[:4*self.N,i].reshape(4,self.N)
            rhs=self.rhs(float(x),sol.y[:,i]).reshape(-1)
            H,s,gamma=self.rates(float(x))
            mx=self.mix
            a=math.exp(x)
            u0=A_RAD*2.7255**4/a**4
            # Physical pressure anisotropy Pi=P_parallel-P_perp=epsilon*J2.
            # PR137's RHS uses its internal driver Pi/3 and multiplies it
            # by 3*KAPPA; never confuse that intermediate with physical Pi.
            pi_gamma=u0*yy[0,2]
            pi_nu=u0*(mx["Omega_nu"]/mx["Omega_gamma"])*yy[2,2]
            max_mono_E=max(max_mono_E,abs(rhs[0]+2*s/H*yy[0,2]),
                          abs(rhs[2*self.N]+2*s/H*yy[2,2]))
            max_mono_N=max(max_mono_N,abs(rhs[self.N]),abs(rhs[3*self.N]))
            rows.append({"a":a,"zbar":1/a-1,"tau":float(sol.y[-1,i]),
                "electron_ne_cm3":float(self.donor.ne(a)),
                "gamma_per_s":gamma,"H_per_s":H,"s_over_H":s/H,
                "gamma_energy_J0":float(yy[0,0]),
                "gamma_energy_J2":float(yy[0,2]),
                "gamma_number_N0":float(yy[1,0]),
                "nu_energy_J0":float(yy[2,0]),
                "nu_energy_J2":float(yy[2,2]),
                "nu_number_N0":float(yy[3,0]),
                "Pi_gamma_physical_Pa":pi_gamma,
                "Pi_nu_physical_Pa":pi_nu,
                "PR137_normalized_shear_source_gamma_Pa":pi_gamma/3.,
                "PR137_normalized_shear_source_nu_Pa":pi_nu/3.,
                "shear_rhs_source_gamma_s2":KAPPA*pi_gamma,
                "shear_rhs_source_nu_s2":KAPPA*pi_nu})
        tau_integral=quad(lambda x: self.rates(x)[2]/self.rates(x)[0],
              grid[0],grid[-1],epsrel=3e-9,epsabs=1e-12,limit=250)[0]
        c13_tau=self.donor.donor["end"]["thomson_tau"]
        returned={
            "schema":"rei.c14.c13_native_electron_thomson_bass_PSTF.v1",
            "claim":"C13 positive time-varying H/He photo/Case-A real MD14 electrons -> PR137 actual unpolarized Thomson gamma/nu one-way LRS; not polarized full Boltzmann or Einstein feedback",
            "q":self.donor.donor["q"],"steps":steps,"L":self.config.L,
            "kappa_gamma":self.config.kappa_gamma,"kappa_nu":self.config.kappa_nu,
            "scattering":self.config.scattering,"source":validate_source_sha(),
            "Omega_photon_and_neutrino":self.mix,
            "c13_initial":self.donor.donor["history"][0],
            "c13_final":self.donor.donor["end"],
            "tau_C13_trapezoid":c13_tau,
            "tau_thomson_DOP853":rows[-1]["tau"],
            "tau_independent_quad":float(tau_integral),
            "tau_relative_disagreement_C13_vs_quad":abs(c13_tau-tau_integral)/tau_integral,
            "tau_relative_disagreement_solver_vs_quad":abs(rows[-1]["tau"]-tau_integral)/tau_integral,
            "max_unpolarized_energy_mono_RHS_residual":max_mono_E,
            "max_photon_and_neutrino_number_mono_RHS_residual":max_mono_N,
            "gamma_number_N0_max_drift":max(abs(r["gamma_number_N0"]-1) for r in rows),
            "nu_number_N0_max_drift":max(abs(r["nu_number_N0"]-1) for r in rows),
            "history":rows}
        if (returned["max_unpolarized_energy_mono_RHS_residual"]>3e-11 or
            returned["max_photon_and_neutrino_number_mono_RHS_residual"]>3e-11 or
            returned["gamma_number_N0_max_drift"]>3e-10 or
            returned["nu_number_N0_max_drift"]>3e-10):
            raise RuntimeError("THOMSON_SOURCE_CONSERVATION_FAILURE")
        return returned


def one_case(q=0.,steps_c13=128,steps_thomson=97,config=PhysicalThomson(.2,.2,L=8)):
    mod=Scenario(ROOT)
    src=NativeStellarSource.load(mod,
        ROOT/"research/rei_c13_live_source_20261015/NATIVE_SOURCE_8X8.csv")
    donor=run_c13(q,src,nstep=steps_c13,coalescence_budget=(1e-12,1e-11))
    history=ElectronSource.from_real_c13(donor,mod)
    return OneWayThomson(history,config).run(steps=steps_thomson)


def main():
    res=one_case()
    path=HERE/"TEST_ON_C13.json"
    path.write_text(json.dumps(res,indent=2)+"\n")
    print("SOURCE",res["q"],res["source"])
    print("THOMSON",res["tau_C13_trapezoid"],res["tau_thomson_DOP853"],
          res["tau_independent_quad"],res["tau_relative_disagreement_C13_vs_quad"])
    print("GAMMA J2",res["history"][0]["gamma_energy_J2"],res["history"][-1]["gamma_energy_J2"])
    print("NU J2",res["history"][0]["nu_energy_J2"],res["history"][-1]["nu_energy_J2"])
    print("LEDGER",res["gamma_number_N0_max_drift"],res["max_unpolarized_energy_mono_RHS_residual"])

if __name__=="__main__":main()
