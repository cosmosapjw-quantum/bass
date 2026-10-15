"""Source-locked missing free-streaming radiation stress feedback *diagnostic*.

This is a conditional radiation stress test, NOT coupled Einstein-Boltzmann,
not observed CMB anisotropy and not actual gas-ionizing radiation stress.
The full locked Omega_r fluid is treated as an initially isotropic freely
streamed effective radiation envelope from zbar=20 to4.
"""
from __future__ import annotations
import argparse,json,math,sys
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import cumulative_trapezoid

from axbi_provider import Background,Family,_read_lock

G_SI=6.67430e-11
C_SI=299792458.0
ROOT=Path(__file__).resolve().parent

def angular_moments(b,order=128):
    b=np.asarray(b,dtype=float)
    if not np.isfinite(b).all():raise ValueError("finite b")
    if not isinstance(order,int) or order<2:raise ValueError("order>=2")
    x,w=leggauss(order)
    mu=(x+1)/2;weight=w/2
    ep=np.exp(2*b[...,None])
    ez=np.exp(-4*b[...,None])
    R=np.sqrt((1-mu**2)*ep+mu**2*ez)
    mul=mu*np.sqrt(ez)/R
    monopole=np.sum(R*weight,axis=-1)
    quadrupole=np.sum(R*((3*mul**2-1)/2)*weight,axis=-1)
    return monopole,quadrupole

def sample(q,n=501):
    bgr=Background(Family(q))
    t=bgr.table(n)
    a=t["a"];b=t["b"];time=t["proper_elapsed_s"]
    spec=_read_lock()["cosmology"]
    rho0=3*bgr.h0*bgr.h0/(8*math.pi*G_SI)
    eps_ref=rho0*float(spec["Omega_r"])/bgr.aref**4*C_SI**2
    eps_iso=eps_ref*(bgr.aref/a)**4
    mon,quad=angular_moments(b,128)
    if q==0:
        mon[:]=1;quad[:]=0
    pr=eps_iso*quad
    extra=eps_iso*(mon-1)
    # Original Rust omitted_feedback with normalized pressure anisotropy
    # evaluates a^3*(8piG/3c²)*pressure and dt using trapezoids.
    k=8*math.pi*G_SI/(3*C_SI**2)
    I=cumulative_trapezoid(k*a**3*pr,time,initial=0)
    delta_s=I/a**3
    ratio=np.abs(delta_s)/t["H_mean_per_s"]
    extra_ratio=np.abs(extra)*k/t["H_flrw_per_s"]**2
    return {"q":q,"eps_reference_j_m3":eps_ref,
        "max_abs_stress_feedback_s_over_H":float(np.max(ratio)),
        "max_abs_free_stream_energy_correction_over_flrw_H2":float(np.max(extra_ratio)),
        "end_delta_s_per_s":float(delta_s[-1]),
        "end_pressure_j_m3":float(pr[-1]),
        "monopole_initial":float(mon[0]),
        "max_quadrupole":float(np.max(np.abs(quad))),
        "fraction_of_locked_q_shear_endpoint":float(abs(delta_s[-1]/t["shear_s_per_s"][-1])) if q else 0,
        "assumptions":"all effective Omega_r treated as initially isotropic free-streaming at z20; no ionizing radiation stress; trapezoid in elapsed proper seconds",
        "time_interval_s":[float(time[0]),float(time[-1])],
        "source_model":"actual AX03 physical_density_fixed Bianchi I with locked parameters",
        "not_certified":{"gas_ionizing_stress":None,"full_CMB_Boltzmann_stress":None,"shear_conservation_under_backreaction":None}}

def run():
    rows=[sample(q) for q in [0,.005,-.005,.01,-.01]]
    original=_read_lock()["feedback_scope"]
    return {"schema":"bass.rei.axbi.free_stream_effective_radiation_feedback_proxy.v1",
       "source_conventions":"isotropic effective Omega_r normalization, not a full exact photon stress history",
       "orig_diagnostic_ceiling_s_over_H":original["max_abs_delta_s_over_H_ceiling"],
       "orig_diagnostic_ceiling_energy":original["max_extra_energy_over_background_ceiling"],
       "rows":rows,
       "all_proxy_shear_below_1e_minus4":all(x["max_abs_stress_feedback_s_over_H"]<=original["max_abs_delta_s_over_H_ceiling"] for x in rows),
       "all_proxy_energy_below_1e_minus4":all(x["max_abs_free_stream_energy_correction_over_flrw_H2"]<=original["max_extra_energy_over_background_ceiling"] for x in rows),
       "actual_cosmological_atomic_reionization_admission":"NOT_ISSUED"}

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path,required=True)
    p=ap.parse_args()
    if p.output.exists():raise FileExistsError(p.output)
    d=run();p.output.parent.mkdir(parents=True,exist_ok=True)
    p.output.write_text(json.dumps(d,indent=2)+"\n")
    print(json.dumps(d,indent=2)[:3900])
