"""Source-locked convergence and kinetic conservation residuals, no false cert."""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import numpy as np
from sigma_matter import MassiveMoments,EinsteinVlasovSigmaMatter,sigma_from_legacy_q,InitialStress

def cases():
    s=sigma_from_legacy_q(.01)
    return [
     ("STRESS_MIX",InitialStress(s,1,.5,.2,.1,.5,30.)),
     ("PI_ONLY",InitialStress(0.,1,.5,.2,.1,.5,30.)),
     ("MASSIVE_ONLY",InitialStress(0.,1,0,0,.1,.5,30.)),
     ("COLD_LIMIT",InitialStress(s,1,0,0,.1,.5,1000.)),
    ]

def collect():
    out=[]
    for label,initial in cases():
        ref=EinsteinVlasovSigmaMatter(initial,angular_n=128,rtol=6e-14,atol=1e-15)
        truth=ref.at_x(ref.xmax)
        for n,rtol in [(16,3e-12),(32,3e-12),(64,3e-12),(128,6e-14)]:
            model=EinsteinVlasovSigmaMatter(initial,angular_n=n,rtol=rtol,atol=1e-15 if n==128 else 2e-14)
            sample=model.at_x(model.xmax)
            diffs={
               "b_absolute":abs(sample["b"]-truth["b"]),
               "Sigma_absolute":abs(sample["Sigma"]-truth["Sigma"]),
               "proper_time_relative":abs(sample["proper_elapsed_s"]/truth["proper_elapsed_s"]-1),
               "Pi_r_absolute_J_m3":abs(sample["Pi_r_J_m3"]-truth["Pi_r_J_m3"]),
               "Pi_m_absolute_J_m3":abs(sample["Pi_m_J_m3"]-truth["Pi_m_J_m3"]),
               "H_relative":abs(sample["H_mean_per_s"]/truth["H_mean_per_s"]-1)
            }
            out.append({"case":label,"Sigma_ref":initial.Sigma_ref,
               "radiation_A":initial.radiation_A,"massive_A":initial.massive_matter_A,
               "mass_over_Tref":initial.mass_over_Tref,"angular_n":n,"rtol":rtol,
               "ode_nfev":model.nfev,"diff":diffs})
    return {"schema":"bass.rei.axbi.massive_kinetic_numerical_convergence.v1",
       "reference":"DOP853 angular_GL128 rtol6e-14, same BASS FD momentum mesh, exact same source",
       "reference_type":"tighter sampled numerical reference, NOT continuum angle/radial source error certificate",
       "cases":out,
       "whole_kinetic_ODE_interval_certification":None,
       "original_BASS_radial_accuracy_certification":None}
if __name__=="__main__":
    pa=argparse.ArgumentParser();pa.add_argument("--out",type=Path,required=True)
    args=pa.parse_args()
    if args.out.exists():raise FileExistsError(args.out)
    data=collect()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(data,indent=2)+"\n")
    for a in data["cases"]:
        print(a["case"],a["angular_n"],a["diff"])
