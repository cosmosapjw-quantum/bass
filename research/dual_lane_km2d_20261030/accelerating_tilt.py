"""KM2-D: prescribed accelerating electron four-velocity and exact causal source memory.

Inherits original KM2-C Bianchi-I normal-frame geometry, Thomson map,
and independent full-carrier direct / unknown-source Volterra algorithms.
Only beta(t) and its explicit frame-acceleration work are new.
"""
from __future__ import annotations

import argparse
from collections import OrderedDict
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from numpy.polynomial.legendre import leggauss

ROOT = Path(__file__).resolve().parents[2]
VENDOR = ROOT/"research/dual_lane_km2c_20261028/vendor"
CODE = ROOT/"research/dual_lane_km2c_20261028/code"
sys.path[:0] = [str(VENDOR),str(CODE)]
from curved_tilt import (FieldProfile, make_fixture, CurvedMemory, DirectHistory,
                         VolterraHistory, linear_collision)
from tilted_collision import TiltedThomson, _velocity, radiation_tensor, expected_fourforce
from source_memory import ALPHA

ORIGINAL_KM2C_SHA="05aade3aab7e9a32c11608882c943e4d3cb6f379"
ORIGINAL_COLLISION_SHA="92660768f4719d78261fed1cb44f186d2821629d"
ORIGINAL_GEOMETRY_SHA="9d500e36fefaa4ddc22300a2f03d9eb9cfe98403"
PARENT_CE1AA_HEAD="48e6c979c49a49ff6854a9555fe97a9690d86d16"
ORIGINAL_TOP_DAG="9/15"


def git_blob(path:Path):
    b=path.read_bytes()
    return hashlib.sha1(f"blob {len(b)}\0".encode("ascii")+b).hexdigest()


def check_origins():
    checks={
        str(CODE/"curved_tilt.py"):ORIGINAL_KM2C_SHA,
        str(VENDOR/"tilted_collision.py"):ORIGINAL_COLLISION_SHA,
        str(VENDOR/"source_memory.py"):ORIGINAL_GEOMETRY_SHA,
    }
    if any(git_blob(Path(p))!=sha for p,sha in checks.items()):
        raise ValueError("Unchanged KM2C/KM2A physical source Git blob identity required")
    return checks


@dataclass(frozen=True)
class ElectronVelocity:
    """Affine externally prescribed beta(u), beta'=d(v/c)/du, with entire support timelike."""
    beta0: tuple[float,float,float]
    slope: tuple[float,float,float]
    end: float

    def __post_init__(self):
        x=np.asarray(self.beta0,dtype=float);a=np.asarray(self.slope,dtype=float)
        if x.shape!=(3,) or a.shape!=(3,) or not (np.isfinite(x).all()
                and np.isfinite(a).all() and np.isfinite(self.end) and 0<self.end<=.6):
            raise ValueError("Finite prescribed dimensionless beta and positive u support required")
        # The timelike velocity ball is convex, so checking affine endpoints
        # guarantees |beta(u)|<1 everywhere in the chosen interval.
        for v in (x,x+self.end*a):
            _velocity(v)
        object.__setattr__(self,"beta0",tuple(map(float,x)))
        object.__setattr__(self,"slope",tuple(map(float,a)))

    def beta(self,t):
        t=float(t)
        if not np.isfinite(t) or not 0<=t<=self.end:
            raise ValueError("Velocity clock outside prescribed support")
        return np.asarray(self.beta0)+t*np.asarray(self.slope)

    def derivative(self,t):
        self.beta(t)
        return np.asarray(self.slope)

    def gamma(self,t):
        return _velocity(self.beta(t))[1]


class MovingMemory(CurvedMemory):
    """Original KM2C normal screen and causal solver with instantaneous beta(u).

    No beta-prime term in X'= -nu D X+G M, since X lives in the normal
    transported screen rather than in the changing electron rest screen.
    """
    def __init__(self,geometry,J0,velocity:ElectronVelocity,nu0,**kwargs):
        if geometry.end>velocity.end:
            raise ValueError("Electron law must cover full geometric source support")
        self.velocity=velocity
        super().__init__(geometry,J0,velocity.beta(0.0),nu0,**kwargs)

    def at(self,t):
        t=self.time(t)
        if t in self._cache:
            self._cache.move_to_end(t)
            return self._cache[t]
        a=self.geo.at(t)
        beta=self.velocity.beta(t)
        op=TiltedThomson(a["e"],a["w"],beta)
        F=np.einsum("nij,nja->nia",op.S,a["screen"])
        # Same KM2C/source-memory formula and exact fixed angular measure.
        L=(a["v"]*op.D**2)[:,None,None]*np.einsum(
            "nia,njb->nijab",F,F).reshape(self.geo.n,9,4)
        G=(ALPHA*self.nu0/(a["mu"]**4*op.D**3))[:,None,None]*np.einsum(
            "nia,njb->nabij",F,F).reshape(self.geo.n,4,9)
        z={**a,"op":op,"F":F,"D":op.D,"beta_u":beta.copy(),
           "d":self.nu0*op.D,"L":L,"G":G}
        self._cache[t]=z
        if len(self._cache)>128:
            self._cache.popitem(last=False)
        return z


def moving_balance(m:MovingMemory,t,J):
    """Direct moment derivative vs exact geometric + prescribed beta'-work.

    F and the normal stress are independently constructed from the full
    normal carrier. Discrete-quadrature collision-invariant defect is
    reported separately; no renormalization or false exact-invariant claim.
    """
    z=m.at(t);e=z["e"];w=z["w"];op=z["op"]
    beta=m.velocity.beta(t);dbeta=m.velocity.derivative(t)
    gamma=m.velocity.gamma(t);gamma_p=gamma**3*float(beta@dbeta)
    H,sigma=m.geo.profile.fields(t)
    T=radiation_tensor(e,w,J)
    rho=float(T[0,0]);q=T[0,1:]
    pi=T[1:,1:]-rho*np.eye(3)/3
    coll=linear_collision(op,J,m.nu0)
    Icoll=np.trace(coll,axis1=1,axis2=2)
    f=np.r_[float(w@Icoll),np.einsum("n,n,ni->i",w,Icoll,e)]
    target=expected_fourforce(T,beta,m.nu0)
    flux_defect=gamma*(f[0]-float(beta@f[1:]))
    I=np.trace(J,axis1=1,axis2=2)
    s=np.einsum("ni,ij,nj->n",e,sigma,e)
    edot=-e@sigma.T+s[:,None]*e
    rho_prime=float(w@((-4*H-s)*I+Icoll))
    q_prime=np.einsum("n,n,ni->i",w,(-4*H-s)*I+Icoll,e)
    q_prime+=np.einsum("n,n,ni->i",w,I,edot)
    C=gamma*(rho-float(beta@q))
    geometric=(-4*H*C-gamma*np.sum(sigma*pi)
               +gamma*float(beta@(sigma@q)))
    acceleration=(gamma_p*(rho-float(beta@q))-gamma*float(dbeta@q))
    full=geometric+acceleration
    direct_product=(gamma_p*(rho-float(beta@q))
                    +gamma*(rho_prime-float(dbeta@q)-float(beta@q_prime)))
    scale=max(1.,abs(C),abs(full),abs(f[0]),np.linalg.norm(f[1:]))
    return {
        "u":float(t),"beta":beta.tolist(),"beta_prime":dbeta.tolist(),
        "gamma":float(gamma),"gamma_prime":float(gamma_p),
        "rho":rho,"q":q.tolist(),"C":float(C),
        "geometric_work_rate":float(geometric),
        "acceleration_work_rate":float(acceleration),
        "work_rate_without_discrete_collision":float(full),
        "discrete_collision_C_rate":float(flux_defect),
        "full_C_derivative_from_normal_moments":float(direct_product),
        "identity_residual_relative":float(abs(direct_product-full-flux_defect)/scale),
        "fourforce_relative":float(np.max(abs(f-target))/scale),
        "collision_elasticity_relative":float(abs(f[0]-beta@f[1:])/scale),
        "rho_prime_normal":rho_prime,"q_prime_normal":q_prime.tolist(),
        "stress_anisotropic_trace":float(np.trace(pi)),
    }


def make_moving(n:int=8,T:float=.25,nu0:float=1.3,
                beta0=(.30,-.40,.20),slope=(.20,-.10,.12),coefficients=None,
                kind="main"):
    vel=ElectronVelocity(tuple(beta0),tuple(slope),T)
    geo,J0=make_fixture(n,FieldProfile(kind,nu0),vel.beta(0),T,coefficients)
    return MovingMemory(geo,J0,vel,nu0)


def independent_work_integral(m,d,T,order=24):
    """Independent GL time quadrature of physical geometry and acceleration work."""
    x,w=leggauss(order)
    ts=T*(x+1)/2
    ww=T*w/2
    rows=[moving_balance(m,float(t),d.carrier(float(t))) for t in ts]
    geom=float(np.dot(ww,[r["geometric_work_rate"] for r in rows]))
    accel=float(np.dot(ww,[r["acceleration_work_rate"] for r in rows]))
    collision=float(np.dot(ww,[r["discrete_collision_C_rate"] for r in rows]))
    c0=moving_balance(m,0.,d.carrier(0.))["C"]
    cT=moving_balance(m,T,d.carrier(T))["C"]
    observed=cT-c0
    return {
        "C_initial":c0,"C_final":cT,"C_change_actual_direct":observed,
        "integrated_geometric_work":geom,"integrated_acceleration_work":accel,
        "integrated_discrete_collision_defect":collision,
        "integrated_predicted_change":geom+accel+collision,
        "work_closure_absolute":abs(observed-geom-accel-collision),
        "would_omit_acceleration_work_error":abs(observed-geom-collision),
        "max_instantaneous_force_relative":max(r["fourforce_relative"] for r in rows),
        "max_instantaneous_elasticity_relative":max(r["collision_elasticity_relative"] for r in rows),
        "max_product_rule_residual_relative":max(r["identity_residual_relative"] for r in rows),
        "GL_time_nodes":order,
        "GL_independent_work_rows":rows,
    }


def run(output:Path, *, quick=False):
    check_origins()
    T=.25
    m=make_moving(n=8,T=T)
    d=DirectHistory(m)
    panels=(8,16,32) if not quick else (8,16)
    times=(0.,.0625,.125,.1875,.25)
    cases={}
    for count in panels:
        v=VolterraHistory(m,count)
        physical=[]
        for t in times:
            D=d.carrier(t); V=v.carrier(t)
            Mb=d.moment(t);Mv=v.moment(t)
            b=moving_balance(m,t,D)
            physical.append({
                "u":t,
                "beta":b["beta"],
                "rho_direct":b["rho"],
                "q_direct":b["q"],
                "C_direct":b["C"],
                "M_direct_3x3":Mb.tolist(),
                "M_volterra_3x3":Mv.tolist(),
                "Mzz_direct":float(Mb[2,2]),
                "Mzz_volterra":float(Mv[2,2]),
                "Mxy_direct":float(Mb[0,1]),
                "Mxy_volterra":float(Mv[0,1]),
                "max_carrier_abs_error":float(np.max(abs(D-V))),
                "max_source_abs_error":float(np.max(abs(Mb-Mv))),
            })
        cases[str(count)]={
            "panels":count,
            "max_carrier_error":max(x["max_carrier_abs_error"] for x in physical),
            "max_source_error":max(x["max_source_abs_error"] for x in physical),
            "max_source_self_consistency_error":float(max(v.endpoint_defects)),
            "max_panel_condition":float(max(v.conditions)),
            "source_rows":physical,
        }
        print(f"KM2D_DIRECT_VOLTERRA_{count} source={cases[str(count)]['max_source_error']:.9g} carrier={cases[str(count)]['max_carrier_error']:.9g}",flush=True)
    # Independent angular control, separate from n=8 source/time refinement.
    hi=make_moving(n=12,T=T)
    direct_hi=DirectHistory(hi)
    work=independent_work_integral(hi,direct_hi,T,order=24)
    assert work["max_product_rule_residual_relative"]<2e-11
    if work["max_instantaneous_force_relative"]>=5e-9:
        raise ArithmeticError("High-resolution angular fourforce gate failed")
    if work["work_closure_absolute"]>=1e-7:
        raise ArithmeticError("Independent acceleration-work integral not closed")
    if abs(work["integrated_acceleration_work"])<=.0001:
        raise ArithmeticError("No physical acceleration work in chosen experiment")
    if work["would_omit_acceleration_work_error"]<=.0001:
        raise ArithmeticError("Fixed-beta work omission not falsified")
    # Initial octupole source-null: keep its true initial carrier at beta(0)=0.
    null=make_moving(n=10,T=.15,beta0=(0.,0.,0.),slope=(.20,-.10,.12),
                     coefficients={("I",3,0):.1})
    nv=VolterraHistory(null,16)
    null0=float(np.linalg.norm(null.initial_source(0)))
    nullT=float(np.linalg.norm(nv.moment(.15)))
    if null0>=2e-11 or nullT<=1e-5:
        raise ArithmeticError("Loss of physical initial source-null causal memory")
    if "32" in cases and cases["32"]["max_source_error"]>=3e-9:
        raise ArithmeticError("Unchanged high-accuracy KM2C source comparison gate failed")
    row={
        "schema":"bass.km2d.accelerating_tilt_original_source.v1",
        "date":"2026-10-30","physics":"prescribed noncommuting Bianchi I, time-varying electron tilt, cold elastic polarized Thomson, normal screen",
        "signature":"(-,+,+,+)","u_end":T,"Tstar_convention":"u=t/T_star; nu0 input means n_e_star*sigma_T*c*T_star",
        "beta0":[.30,-.40,.20],"beta_prime":[.20,-.10,.12],"nu0Tstar":1.3,
        "KM2C_original_blobs":check_origins(),
        "direct_IVP":"Original KM2C DirectHistory P8 normal-carrier with instantaneous variable beta operator",
        "volterra":"Original KM2C full-initial-carrier causal unknown-source collocation, no direct RHS access",
        "source_grid_n_theta":8,"work_grid_n_theta":12,
        "cases":cases,"independent_acceleration_work":work,
        "source_null_octupole":{"initial_source_norm":null0,"final_source_norm":nullT,
                                "whole_initial_carrier_retained":True},
        "upper_DAG":"9/15","KM2":"PARTIAL","new_upper_completed":0,
        "science_status":"PRESCRIBED_PROFILE_ONLY","thermal_spectral_validity":"NOT_CERTIFIED",
        "electron_Euler_or_continuity":"NOT_RUN","Einstein_feedback":"NOT_RUN",
        "production_ready":False,"merge_ready":False,"auto_next":False,
        "distinct_author_R6_C9":"NOT_RUN","native_subagent":"NOT_RUN",
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(row,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    print("KM2D_ACCELERATION_WORK",json.dumps(work,sort_keys=True),flush=True)
    print("KM2D_PHYSICAL_SCIENCE_SUCCESS",output,flush=True)
    return row


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--quick",action="store_true")
    v=ap.parse_args()
    run(v.output,quick=v.quick)
