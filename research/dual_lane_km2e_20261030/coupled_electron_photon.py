"""KM-2E: first reciprocal cold-electron / original polarized photon momentum response.

Prescribed noncommuting Bianchi I geometry only; photons retain full original
KM2A/P8 normal-carrier transport with raw angular weights and instantaneous
finite-beta Thomson collisions. Electron specific spatial four-momentum and
normal-frame number conservation evolve from opposite covariant Thomson force.
No electron thermal pressure or self-consistent Einstein geometry.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/"research/dual_lane_km2c_20261028"
PREV=ROOT/"research/dual_lane_km2d_20261030"
sys.path[:0]=[str(OLD/"vendor"),str(OLD/"code")]
from curved_tilt import FieldProfile, make_fixture, linear_collision, P8
from tilted_collision import TiltedThomson, _velocity, radiation_tensor, expected_fourforce

PARENT_HEAD="8993bdf97c5aca2961a7d2e1df08bd4119899670"
PARENT_KM2D_BLOB="b599d3842e843d8de1de1499b73e6849374bf8f8"
KM2C_BLOB="05aade3aab7e9a32c11608882c943e4d3cb6f379"
KM2A_BLOB="92660768f4719d78261fed1cb44f186d2821629d"
KM1_BLOB="9d500e36fefaa4ddc22300a2f03d9eb9cfe98403"
SOURCE_BLOBS={
    PREV/"accelerating_tilt.py":PARENT_KM2D_BLOB,
    OLD/"code/curved_tilt.py":KM2C_BLOB,
    OLD/"vendor/tilted_collision.py":KM2A_BLOB,
    OLD/"vendor/source_memory.py":KM1_BLOB,
}


def git_blob(path:Path)->str:
    raw=path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii")+raw).hexdigest()


def source_guards()->dict:
    out={}
    for path,expected in SOURCE_BLOBS.items():
        digest=git_blob(path)
        if digest!=expected:
            raise ValueError(f"Original photon and geometry source SHA changed: {path}")
        out[str(path.relative_to(ROOT))]=digest
    return out


class CoupledColdElectronPhoton:
    """Full photon carrier + homogeneous cold electron fluid, prescribed geometry.

    Inertia ratio fixes R_e0 / rho_gamma0 as a dimensionless toy physical
    parameter. The original ν0=n_rest0 σ_T c T_star is fixed separately by
    normal time and radiation-energy normalization, not observationally fitted.
    """
    def __init__(self,n=8,end=.25,nu0=1.3,inertia_ratio=.75,
                 beta0=(.3,-.4,.2),geometry="main"):
        source_guards()
        self.n=int(n);self.end=float(end)
        self.nu0=float(nu0);self.inertia_ratio=float(inertia_ratio)
        self.beta0=np.asarray(beta0,float)
        if (self.n<4 or self.n>24 or not 0<self.end<=.6
            or not np.isfinite([self.nu0,self.inertia_ratio]).all()
            or self.nu0<0 or self.inertia_ratio<=0):
            raise ValueError("Finite physical opacity, inertia and bounded grid/time required")
        self.beta0,self.gamma0=_velocity(self.beta0)
        self.geo,self.J0=make_fixture(self.n,FieldProfile(geometry,self.nu0),
                                      self.beta0,self.end)
        self.shape=self.J0.shape
        self.N=len(self.J0)
        initial=self.geo.at(0)
        self.initial_T=radiation_tensor(initial["e"],initial["w"],self.J0)
        self.rho_g0=float(self.initial_T[0,0])
        if self.rho_g0<=0:raise ValueError("Positive original physical photon energy required")
        self.R_e0=self.inertia_ratio*self.rho_g0
        self.M0=self.R_e0/self.gamma0 # m_e c² * initial normal-frame particle density
        self.p0=self.gamma0*self.beta0
        self.Z=np.zeros((3,3));self.zero=np.zeros(3)

    def parse(self,y,mode):
        y=np.asarray(y,float)
        if y.shape!=(self.J0.size+4,) or not np.isfinite(y).all():
            raise ValueError("Full coupled photon+electron state has wrong shape")
        J=y[:self.J0.size].reshape(self.shape)
        vector=y[self.J0.size:self.J0.size+3]
        zeta=float(y[-1])
        if zeta<=0:raise ValueError("Electron normal-slice number density is not positive")
        if mode=="p":
            p=vector
            gamma=math.sqrt(1+float(p@p))
            beta=p/gamma
        elif mode=="beta":
            beta,gamma=_velocity(vector)
            p=gamma*beta
        else:
            raise ValueError("Only p and beta physical parameterizations supported")
        return J,np.asarray(p,float),np.asarray(beta,float),gamma,zeta

    def init(self,mode):
        if mode not in ("p","beta"):
            raise ValueError("Unknown matter variable")
        return np.r_[self.J0.ravel(), self.p0 if mode=="p" else self.beta0,1.]

    def at(self,t,J,beta,gamma,zeta):
        a=self.geo.at(t)
        H,sigma=self.geo.profile.fields(t)
        B=H*np.eye(3)+sigma
        nu=self.nu0*zeta*self.gamma0/gamma
        if not np.isfinite(nu) or nu<0:
            raise ValueError("Nonphysical electron rest density or Thomson rate")
        op=TiltedThomson(a["e"],a["w"],beta)
        s=np.einsum("ni,ij,nj->n",a["e"],sigma,a["e"])
        streaming=-4*(H+s)[:,None,None]*J+P8.tensor_rate(
            J,a["e"],H,sigma,self.zero,self.Z,self.zero)
        coll=linear_collision(op,J,nu)
        T=radiation_tensor(a["e"],a["w"],J)
        # Independent covariant force expression, with exact U.F=0.
        cov=expected_fourforce(T,beta,nu)
        intensity=np.trace(coll,axis1=1,axis2=2)
        raw=np.r_[np.dot(a["w"],intensity),
                   np.einsum("n,n,ni->i",a["w"],intensity,a["e"])]
        return {"geo":a,"H":H,"sigma":sigma,"B":B,"nu":nu,"op":op,
                "T":T,"covariant_force":cov,"raw_P8_force":raw,
                "streaming":streaming,"collision":coll,"rhs_J":streaming+coll}

    def rhs(self,t,y,*,mode="p",feedback=True):
        J,p,beta,gamma,zeta=self.parse(y,mode)
        d=self.at(t,J,beta,gamma,zeta)
        force=d["covariant_force"][1:]
        H=d["H"];B=d["B"]
        # Matter momentum Q_e=M0*zeta*p; Q_e'=-[4H I+sigma]Q_e-F_gamma.
        pdot=-B@p-(float(bool(feedback))*force)/(self.M0*zeta)
        zdot=-3*H*zeta
        if mode=="p":
            matter_rhs=pdot
        else:
            # Independent beta evolution from the mass shell, not p' in beta vars.
            R=self.M0*zeta*gamma
            projection=np.eye(3)-np.outer(beta,beta)
            matter_rhs=-projection@(B@beta+float(bool(feedback))*force/R)
        return np.r_[d["rhs_J"].ravel(),matter_rhs,zdot]

    def integrate(self,*,mode="p",feedback=True,rtol=2e-11,atol=2e-13):
        res=solve_ivp(lambda u,y:self.rhs(u,y,mode=mode,feedback=feedback),
                      (0,self.end),self.init(mode),method="DOP853",
                      rtol=rtol,atol=atol,dense_output=True)
        if not res.success:raise RuntimeError(res.message)
        return res

    def measure(self,t,history,mode="p"):
        J,p,beta,gamma,zeta=self.parse(history.sol(float(t)),mode)
        d=self.at(float(t),J,beta,gamma,zeta)
        T=d["T"];rho_g=float(T[0,0]);q_g=T[0,1:]
        P_g=T[1:,1:]
        R=self.M0*zeta*gamma
        Q=self.M0*zeta*p
        Pe=R*np.outer(beta,beta)
        E=rho_g+R
        Qall=q_g+Q
        Pall=P_g+Pe
        W_E=-3*d["H"]*E-np.einsum("ij,ij->",d["B"],Pall)
        W_Q=-(4*d["H"]*np.eye(3)+d["sigma"])@Qall
        gap=d["raw_P8_force"]-d["covariant_force"]
        nu=d["nu"]
        return {
            "u":float(t),"p":p.tolist(),"beta":beta.tolist(),"gamma":gamma,
            "zeta_lab_number_ratio":zeta,
            "rest_density_ratio":zeta*self.gamma0/gamma,
            "nu_rest_Tstar":nu,
            "rho_gamma":rho_g,"q_gamma":q_g.tolist(),
            "P_gamma":P_g.tolist(),
            "rho_electron_normal":float(R),
            "q_electron_normal":Q.tolist(),
            "P_electron":Pe.tolist(),
            "rho_total":float(E),"q_total":Qall.tolist(),
            "P_total":Pall.tolist(),
            "original_source_electron_M":d["op"].source(J).tolist(),
            "photon_raw_P8_force":d["raw_P8_force"].tolist(),
            "covariant_photon_force":d["covariant_force"].tolist(),
            "discrete_force_gap":gap.tolist(),
            "geometry_energy_rate":float(W_E),
            "geometry_momentum_rate":W_Q.tolist(),
            "total_energy_rate_including_force_gap":float(W_E+gap[0]),
            "total_momentum_rate_including_force_gap":(W_Q+gap[1:]).tolist(),
            "normal_screen_leak":float(max(
                np.max(abs(np.einsum("nij,nj->ni",J,d["geo"]["e"]))),
                np.max(abs(np.einsum("nji,nj->ni",J,d["geo"]["e"]))))),
            "velocity_subluminal":bool(beta@beta<1),
            "physical_mass_shell_residual":float(abs(gamma*gamma-1-p@p)),
            "covariant_force_orthogonality_residual":float(
                abs(d["covariant_force"][0]-beta@d["covariant_force"][1:])),
            "raw_force_relative_difference":float(
                np.max(abs(gap))/max(1.,nu*abs(rho_g)))
        }

    def time_balance(self,history,*,mode="p",time_nodes=24):
        x,w=leggauss(time_nodes)
        ts=self.end*(x+1)/2;tw=self.end*w/2
        rows=[self.measure(float(t),history,mode) for t in ts]
        first=self.measure(0.,history,mode)
        last=self.measure(self.end,history,mode)
        change_E=last["rho_total"]-first["rho_total"]
        change_Q=np.asarray(last["q_total"])-np.asarray(first["q_total"])
        WE=float(np.dot(tw,[r["total_energy_rate_including_force_gap"] for r in rows]))
        WQ=np.einsum("n,ni->i",tw,
                     np.asarray([r["total_momentum_rate_including_force_gap"] for r in rows]))
        GE=float(np.dot(tw,[r["geometry_energy_rate"] for r in rows]))
        GQ=np.einsum("n,ni->i",tw,np.asarray([r["geometry_momentum_rate"] for r in rows]))
        Fgap0=float(np.dot(tw,[r["discrete_force_gap"][0] for r in rows]))
        Fgapq=np.einsum("n,ni->i",tw,np.asarray([r["discrete_force_gap"][1:] for r in rows]))
        return {
            "time_nodes":time_nodes,
            "E_initial":first["rho_total"],"E_final":last["rho_total"],
            "E_observed_delta":change_E,"Q_initial":first["q_total"],
            "Q_final":last["q_total"],"Q_observed_delta":change_Q.tolist(),
            "E_geometry_integral":GE,"E_raw_force_gap_integral":Fgap0,
            "E_predicted_delta":WE,"E_closure_abs":abs(change_E-WE),
            "Q_geometry_integral":GQ.tolist(),"Q_raw_force_gap_integral":Fgapq.tolist(),
            "Q_predicted_delta":WQ.tolist(),"Q_closure_max_abs":float(np.max(abs(change_Q-WQ))),
            "max_raw_force_gap_relative":max(r["raw_force_relative_difference"] for r in rows),
            "max_mass_shell_residual":max(r["physical_mass_shell_residual"] for r in rows),
            "max_covariant_force_orthogonality_residual":
                max(r["covariant_force_orthogonality_residual"] for r in rows),
            "max_screen_leak":max(r["normal_screen_leak"] for r in rows),
            "time_rows":rows,
        }


def actual_science(output:Path,*,quick=False):
    sources=source_guards()
    grid=(8,) if quick else (8,12)
    T=.25
    times=(0.,.0625,.125,.1875,.25)
    cases={}
    for n in grid:
        m=CoupledColdElectronPhoton(n=n,end=T,nu0=1.3,inertia_ratio=.75)
        psol=m.integrate(mode="p")
        bsol=m.integrate(mode="beta")
        unreacted=m.integrate(mode="p",feedback=False)
        data=[];max_j=0;max_beta=0;max_z=0
        for t in times:
            a=m.measure(t,psol,"p")
            beta_repr=m.measure(t,bsol,"beta")
            Jp,p,_,_,z=m.parse(psol.sol(t),"p")
            Jb,_,_,_,zb=m.parse(bsol.sol(t),"beta")
            dj=float(np.max(abs(Jp-Jb)))
            db=float(np.max(abs(np.asarray(a["beta"])-np.asarray(beta_repr["beta"]))))
            dz=abs(z-zb)
            max_j=max(max_j,dj);max_beta=max(max_beta,db);max_z=max(max_z,dz)
            data.append(a)
        work=m.time_balance(psol,mode="p")
        endpoint=data[-1]
        control=m.measure(T,unreacted)
        delta_beta=np.asarray(endpoint["beta"])-np.asarray(control["beta"])
        endpoint_delta=float(np.linalg.norm(delta_beta))
        if (not np.isfinite([max_j,max_beta,max_z,endpoint_delta]).all()
            or work["E_closure_abs"]>=2e-8 or work["Q_closure_max_abs"]>=2e-8
            or max_j>=1e-8 or max_beta>=1e-8 or max_z>=1e-10
            or work["max_covariant_force_orthogonality_residual"]>=1e-10
            or work["max_screen_leak"]>=2e-9):
            raise ArithmeticError("Selfconsistent cold matter/radiation physical gate failed")
        if endpoint_delta<=1e-5:
            raise ArithmeticError("Electron selfconsistent recoil not distinguishable from no-feedback control")
        cases[str(n)]={
            "angular_ntheta":n,"angular_nphi":2*n,"total_raw_rays":m.N,
            "electron_to_photon_initial_energy_ratio":m.inertia_ratio,
            "initial_matter_inertia_m_times_nlab":m.M0,
            "photon_initial":m.rho_g0,
            "p_vs_beta_same_physical_solutions":{
                "max_J_abs":max_j,"max_beta_abs":max_beta,"max_zeta_abs":max_z},
            "feedback_enabled_vs_nonconservative_control_beta_final_norm":endpoint_delta,
            "feedback_enabled_vs_nonconservative_control_beta_delta":delta_beta.tolist(),
            "no_feedback_beta_final":control["beta"],"normal_time_work":work,
            "physical_5epoch_records":data,
            "IVP_direct_photons_and_electron_p":True,
            "IVP_independent_electron_beta_representation":True,
            "distinct_model_independent_author":"NOT_RUN",
        }
        print("KM2E_RECIPROCAL_PHYSICS",n,
              "electron_beta_recoil",f"{endpoint_delta:.12g}",
              "Eclosure",f"{work['E_closure_abs']:.12g}",
              "Qclosure",f"{work['Q_closure_max_abs']:.12g}",
              "p_beta_diff",f"{max_beta:.9g}",flush=True)
    # Flat spacetime, initially isotropic electron distribution from original
    # KM2 fixture, no gravitational work: observe actual total 4-momentum drift.
    flat=CoupledColdElectronPhoton(n=12,end=.15,nu0=1.3,inertia_ratio=.75,
                                    geometry="flat")
    flat_sol=flat.integrate(mode="p")
    a=flat.measure(0.,flat_sol)
    b=flat.measure(.15,flat_sol)
    flat_delta_E=abs(b["rho_total"]-a["rho_total"])
    flat_delta_Q=float(np.max(abs(np.asarray(b["q_total"])-np.asarray(a["q_total"]))))
    if flat_delta_E>=2e-8 or flat_delta_Q>=2e-8:
        raise ArithmeticError("Flat Bianchi-limit total stress-energy cancellation failed")
    # Explicit collision-off control must preserve normal-slice electron number
    # dilution and geodesic specific momentum.
    vac=CoupledColdElectronPhoton(n=8,end=.15,nu0=0.,inertia_ratio=.75)
    vacsol=vac.integrate(mode="p")
    vm=vac.measure(.15,vacsol)
    if (abs(vm["rest_density_ratio"]*vm["gamma"]/
            (vm["zeta_lab_number_ratio"]*vac.gamma0)-1)>2e-14
        or np.max(np.abs(np.asarray(vm["photon_raw_P8_force"])))>1e-14):
        raise ArithmeticError("Vacuum number / collision invariant failed")
    result={
        "schema":"bass.km2e.cold_electron_photon_backreaction.v1",
        "date":"2026-10-30","parent_pr":274,"parent_head":PARENT_HEAD,
        "source_git_blobs":sources,
        "model":"homogeneous cold electron pressureless matter + original fully polarized photon angular carrier with reciprocal Thomson force; prescribed noncommuting Bianchi I",
        "signature":"(-,+,+,+)","units":"u=t/T_star; beta=v/c; ν0=n_rest0 σ_T c T_star",
        "electron_momentum":"p=gamma*beta; p'=-[H I + sigma]p -F_gamma_spatial/(M0*zeta)",
        "electron_number":"zeta'=-3H zeta; n_rest/n_rest0=zeta*gamma0/gamma",
        "electron_density":"R_e=M0*zeta*gamma, Q_e=M0*zeta*p",
        "Thomson_rate":"nu(u)=nu0*zeta*gamma0/gamma",
        "rho_e0_to_rho_gamma0":.75,"u_end":T,
        "normal_photon_carrier":"full per-ray original P8 Hermitian S+iA, no moment closure",
        "cases":cases,
        "flat_spacetime_total_E_abs_delta":flat_delta_E,
        "flat_spacetime_total_Q_max_abs_delta":flat_delta_Q,
        "vacuum_final":vm,
        "upper_dag":"9/15","km2":"PARTIAL","new_upper_completed":0,
        "Einstein_feedback":"NOT_RUN","electron_temperature_or_pressure":"NOT_RUN",
        "spectral_domain":"NOT_CERTIFIED","production_ready":False,
        "merge_ready":False,"auto_next":False,
        "native_subagent":"NOT_RUN","distinct_author_R6_C9":"NOT_RUN",
        "numerical_continuum_angular_certificate":"NOT_RUN",
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("KM2E_PHYSICAL_SCIENCE_CLOSED",output,flush=True)
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--quick",action="store_true")
    v=p.parse_args()
    actual_science(v.output,quick=v.quick)
