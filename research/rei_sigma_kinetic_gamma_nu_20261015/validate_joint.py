"""Cross-source original BASS exact Vlasov and REI gamma/nu limits + refinement.

Finite comparison, not an interval true numerical global error certificate.
"""
from __future__ import annotations
import argparse,json,math,time
from pathlib import Path
import numpy as np
from joint_kinetic import KineticGammaNuMassive,source_lock,verify_original_sources
from species_hierarchy import SpeciesHierarchy
from sigma_matter import InitialStress,EinsteinVlasovSigmaMatter

def run():
    c=source_lock()
    oldm=[]
    for q in (0.,.01,-.01):
        sig=math.sqrt(3)*abs(q)/math.hypot(1,q);ori=0 if q==0 else int(np.sign(q))
        args=dict(Sigma_ref=sig,orientation=ori,kappa_gamma=.2,kappa_nu=.2,
                  massive_fraction=.1,massive_A=.5,ellmax=8,angular_n=32)
        new=KineticGammaNuMassive(c,**args)
        s,z,w=new.integrate(n=101,rtol=2e-12,atol=8e-14)
        original=EinsteinVlasovSigmaMatter(InitialStress(
           Sigma_ref=sig,shear_orientation=ori or 1,
           radiation_fraction=1.,radiation_A=.2,
           massive_matter_fraction=.1,massive_matter_A=.5,mass_over_Tref=30.))
        f=original.at_x(original.xmax)
        oldm.append({"q_legacy":q,"new_Sigma_end":z[-1]["Sigma"],
                     "BASS_original_Sigma_end":f["Sigma"],
                     "absolute_sigma_diff":abs(z[-1]["Sigma"]-f["Sigma"]),
                     "absolute_b_diff":abs(float(s.y[1,-1])-f["b"]),
                     "H_relative_diff":abs(z[-1]["H"]/f["H_mean_per_s"]-1),
                     "elapsed_time_relative_diff":abs((s.y[0,-1]/c.href)/f["proper_elapsed_s"]-1),
                     "source": "original BASS massive + full massless radiation Killing, REI truncated L8 gamma/nu (no Thomson)"})
    m=KineticGammaNuMassive(c,Sigma_ref=0,orientation=0,kappa_gamma=.2,kappa_nu=.2,massive_fraction=0.,ellmax=8)
    r=SpeciesHierarchy(c,2.7255,ellmax=8,Sigma_ref=0.,orientation=0,kappa_gamma=.2,kappa_nu=.2)
    sm,_,_=m.integrate(n=101,rtol=2e-12,atol=8e-14)
    sr,_,_=r.integrate(n=101,rtol=2e-12,atol=8e-14)
    parity={"state_max_absolute_diff":float(np.max(abs(sm.y-sr.y))),
            "origin_REI_gamma_nu_source":"PR137 exact copied source, matching numerical rtol and atol",
            "true_exact_physical_limiting_RHS":float(max(np.max(abs(m.rhs(float(x),sm.y[:,i])-r.rhs(float(x),sm.y[:,i])))
                for i,x in enumerate(sm.t)))}
    ref=[]
    settings=[(8,32,3e-11,3e-13),(8,32,2e-12,8e-14),
              (8,64,2e-12,8e-14),(12,64,2e-12,8e-14)]
    for L,ang,rtol,atol in settings:
        m=KineticGammaNuMassive(c,Sigma_ref=0,orientation=0,kappa_gamma=.2,kappa_nu=.2,
                massive_fraction=.1,massive_A=.5,m_over_Tref=30.,ellmax=L,angular_n=ang)
        p,rows,wall=m.integrate(n=151,rtol=rtol,atol=atol)
        ref.append({"ellmax":L,"massive_GL":ang,"rtol":rtol,"atol":atol,
                    "endpoint_Sigma":rows[-1]["Sigma"],"endpoint_b":float(p.y[1,-1]),
                    "endpoint_pi_m":rows[-1]["pi_massive_J_m3"],
                    "nfev":p.nfev,"wall_s":wall})
    high=ref[-1]
    for q in ref:
        q["abs_Sigma_diff_vs_high"]=abs(q["endpoint_Sigma"]-high["endpoint_Sigma"])
        q["abs_b_diff_vs_high"]=abs(q["endpoint_b"]-high["endpoint_b"])
    if max(x["absolute_sigma_diff"] for x in oldm)>1e-11:
        raise ArithmeticError("BASS_FULL_VLASOV_GAMMANU_NONTHOMSON_LIMIT_HOLD")
    if parity["state_max_absolute_diff"]>5e-12:
        raise ArithmeticError("REI_GAMMANU_ZERO_MASS_LIMIT_HOLD")
    return {"schema":"bass.rei.axbi.gamma_nu_massive_cross_source_refinement.v1",
      "source_original_REI_sha":"5d41df647c4fd624d8a1b574f67fdd0b82ff5102",
      "source_original_BASS_sha":"9e50f936f3289cb0c7c8127772cf9fb8d172d7a8",
      "BASS_full_massive_and_massless_radiation_source_parity":oldm,
      "REI_original_gamma_nu_without_mass_source_limit":parity,
      "refinement":ref,
      "claim":"source-bound finite result only, not rigorous full Einstein-Boltzmann coupled gas AX11 error budget",
      "fully_selfconsistent_HHe_chemistry":None}
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--out",type=Path,required=True)
    a=parser.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    j=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(j,indent=2)+"\n")
    print('BASS_full_source_parity',[(r["q_legacy"],r["absolute_sigma_diff"],r["absolute_b_diff"]) for r in j["BASS_full_massive_and_massless_radiation_source_parity"]],flush=True)
    print('REI_original_limit',j["REI_original_gamma_nu_without_mass_source_limit"],flush=True)
    print('Refinement',[(r["ellmax"],r["massive_GL"],r["rtol"],r["abs_Sigma_diff_vs_high"]) for r in j["refinement"]],flush=True)
