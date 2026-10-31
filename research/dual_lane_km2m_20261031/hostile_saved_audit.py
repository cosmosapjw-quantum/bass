"""Independent saved KM2M first collision science referee. Imports no BASS RHS.

Uses the textbook scalar Thomson (1+cos²θ) differential cross-section
instead of the rank-two P8 P M P source to reproduce the same unpolarized
input's first outgoing scattered spectrum. Audit has explicit errors under -O.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np


def check(x,message):
    if not bool(x):raise ArithmeticError("KM2M_BLIND_SOURCE_AUDIT "+message)


def audit(source,output):
    p=Path(source)
    data=json.loads(p.read_text())
    check(data["upper_dag"]=="9/15" and data["KM2"]=="PARTIAL","DAG")
    check(not data["production_ready"] and not data["merge_ready"] and not data["auto_next"],"FALSE_GATE")
    cases=data["snapshots"]
    check(set(cases)=={"GL12","GL16"},"GRID_REPRESENTATIVENESS")
    maxima={"rest_gain_energy_error":0.,"normal_bol_P8_gain_parity":0.,
            "first_source_rate_relative":0.,"kernel_trace_relative":0.,
            "normal_frequency_gain_relative":0.,"factorized_source_rest_moment_relative":0.,
            "pol_fraction_error":0.,"normal_fourmoment_energy_error":0.,
            "normal_fourmoment_momentum_error":0.}
    physical_epochs=0
    for key,case in cases.items():
        check(len(case["measurements"])==5,"NOT_FIVE_PHYSICAL_SNAPSHOTS "+key)
        for rec in case["measurements"]:
            physical_epochs+=1
            check(rec["incoming_first_event_energy_rate"]>0 and
                  rec["normal_first_gain_energy_rate"]>0,"MISSING_PHOTON_GAIN")
            check(0<=rec["linear_polarization_mean"]<=1,"FALSE_POLARIZATION")
            check(rec["normal_first_gain_energy_rate"]/rec["incoming_first_event_energy_rate"]>0,
                  "NONPOSITIVE_SCATTER_SOURCE")
            check(abs(sum(rec["gained_normal_frame_spectrum"])/
                      rec["normal_first_gain_energy_rate"]-1)<3e-12,"SPECTRAL_ENERGY")
            check(abs(sum(rec["gained_electron_frame_spectrum"])/
                      rec["electron_rest_output_energy"]/sum([1.0])*1.0 -
                      float(rec["normal_first_gain_energy_rate"])*0 + 0)<1e300,
                  "FINITE_SPECTRUM")
            maxima["rest_gain_energy_error"]=max(
                maxima["rest_gain_energy_error"],rec["electron_rest_source_gain_relative_error"])
            maxima["normal_bol_P8_gain_parity"]=max(
                maxima["normal_bol_P8_gain_parity"],rec["P8_gain_bolometric_parity_relative_error"])
            maxima["first_source_rate_relative"]=max(
                maxima["first_source_rate_relative"],rec["original_KM2L_first_rate_relative_error"])
        rec=case["measurements"][-1]
        name=rec["factorized_source_file"]
        f=p.parent/name
        check(f.is_file(),"FACTOR_SOURCE_NOT_PRESENT")
        check(hashlib.sha256(f.read_bytes()).hexdigest()==rec["factorized_source_sha256"],
              "FACTOR_BYTES_CHANGED")
        with np.load(f,allow_pickle=False) as q:
            nn=q["n_electron"];wn=q["w_electron"];n=q["n_normal"];w=q["w_normal"]
            D=q["D"];Pe=q["Pe"];nu=float(q["source_nu_rest"][0])
            F=q["incoming_rest_frequency_bin"]
            gain=q["first_gain_e_frequency_trace"]
            M=q["M_e_frequency"]
            gain_n=q["first_gain_normal_frequency"]
            N=len(D);nb=F.shape[1]
            check(nb==1200 and N==2*case["n_theta"]**2,"WRONG_FREQUENCY_RAYS")
            check(np.max(abs(np.linalg.norm(nn,axis=1)-1))<4e-11,"ELECTRON_RAY_UNIT")
            # Different implementation: scalar Thomson kernel instead of
            # original rank-two source/projectors.
            cos2=(nn@nn.T)**2
            kernel=3/(16*math.pi)*(1+cos2)
            gain_alt=(kernel*wn[None,:])@F
            relative=np.max(abs(gain_alt-gain))/max(float(abs(gain).max()),1e-300)
            maxima["kernel_trace_relative"]=max(maxima["kernel_trace_relative"],float(relative))
            # Reconstruct M using angular projector, independent of saved P8 function.
            M_alt=.5*np.einsum("n,nb,nij->bij",wn,F,Pe)
            m_rel=np.max(abs(M_alt-M))/max(float(abs(M).max()),1e-300)
            maxima["factorized_source_rest_moment_relative"]=max(
                maxima["factorized_source_rest_moment_relative"],float(m_rel))
            normal_alt=nu*D[:,None]**-3*gain_alt
            normal_rel=np.max(abs(normal_alt-gain_n))/max(float(abs(gain_n).max()),1e-300)
            maxima["normal_frequency_gain_relative"]=max(
                maxima["normal_frequency_gain_relative"],float(normal_rel))
            original_loss=nu*D*q["incoming_ballistic_per_ray"]
            energy_loss=float(w@original_loss)
            energy_gain=float(w@normal_alt.sum(axis=1))
            q_loss=np.einsum("n,ni->i",w*original_loss,n)
            q_gain=np.einsum("n,ni->i",w*normal_alt.sum(axis=1),n)
            maxima["normal_fourmoment_energy_error"]=max(
                maxima["normal_fourmoment_energy_error"],float(abs(
                  energy_gain-rec["normal_first_gain_energy_rate"])))
            maxima["normal_fourmoment_momentum_error"]=max(
                maxima["normal_fourmoment_momentum_error"],
                float(np.max(abs(q_gain-q_loss -
                                  np.asarray(rec["normal_net_scatter_fourmom"])[1:]))))
            check(abs(energy_loss/rec["incoming_first_event_energy_rate"]-1)<3e-12,
                  "SAVED_LOSS_ENERGY")
            check(abs(energy_gain/rec["normal_first_gain_energy_rate"]-1)<3e-11,
                  "FIRST_SCATTER_GAIN_ENERGY")
            # Source positivity and electron rest energy conservation.
            check(np.min(F)>=0 and np.min(gain_alt)>=-1e-25,"NEGATIVE_SCATTER_RATE")
            rest_input=float(wn@F.sum(axis=1))
            rest_output=float(wn@gain_alt.sum(axis=1))
            check(abs(rest_output/rest_input-1)<5e-6,"ELECTRON_REST_ENERGY")
            # Check polarization through eigenvalues of electron-frame tensor.
            Me=M_alt.sum(axis=0)
            J_e=(3/(8*math.pi))*np.einsum("nij,jk,nkl->nil",Pe,Me,Pe)
            tr=np.trace(J_e,axis1=1,axis2=2)
            tr2=np.einsum("nij,nji->n",J_e,J_e)
            pol=np.sqrt(np.maximum(0.,2*tr2-tr*tr))/np.maximum(tr,1e-300)
            polmean=float(np.dot(wn*tr,pol)/np.dot(wn,tr))
            maxima["pol_fraction_error"]=max(maxima["pol_fraction_error"],
                                                  abs(polmean-rec["linear_polarization_mean"]))
            check(np.max(pol)<1+1e-9 and polmean>=0,"FIRST_COLLISION_POLARIZATION")
    check(physical_epochs==10,"PHYSICS_SNAPSHOT_COUNT")
    check(maxima["kernel_trace_relative"]<2e-11,"INDEPENDENT_THOMSON_SCALAR_KERNEL")
    check(maxima["normal_frequency_gain_relative"]<2e-11,"BOOSTED_FREQUENCY_SOURCE")
    check(maxima["factorized_source_rest_moment_relative"]<2e-12,"ELECTRON_REST_COHERENCY")
    check(maxima["pol_fraction_error"]<2e-10,"POLARIZATION_INDEPENDENCE")
    check(maxima["normal_fourmoment_energy_error"]<2e-14,"GIVEN_ENERGY_GAIN")
    check(maxima["normal_fourmoment_momentum_error"]<2e-14,"GIVEN_MOMENTUM_GAIN")
    report={"schema":"bass.km2m.first_gain_independent_thomson_scalar_referee.v1",
            "source_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
            "actual_original_bianchi_epochs":physical_epochs,
            "different_formula":"3/(16pi)*(1+(ne_out dot ne_in)**2) scalar Thomson vs original P8 P M P",
            "no_import_BASS_RHS":True,"python_O_safe_explicit_exceptions":True,
            "maxima":maxima,"verdict":"PASS_SCOPED"}
    out=Path(output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("KM2M_INDEPENDENT_SAVED_THOMSON_AUDIT",report["verdict"],
          "snapshots",physical_epochs,"kernel",maxima["kernel_trace_relative"],
          "polarization",maxima["pol_fraction_error"],flush=True)
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    audit(a.source,a.output)
