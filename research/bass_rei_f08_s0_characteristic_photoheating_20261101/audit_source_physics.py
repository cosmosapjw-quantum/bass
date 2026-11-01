#!/usr/bin/env python3
"""Same-author adversarial data-level audit of exact-source HI ionization and heat.
Reads actual physical tables as standard-library CSV, independent of NumPy model code.
"""
from pathlib import Path
import csv,gzip,hashlib,io,json,math
ROOT=Path(__file__).resolve().parent
RESULT=ROOT/"results"
ION=13.598434599702
BIRTH=13.7
SOURCE_RATE=5e-15
EPOCHS=15
EV_TO_ERG=1.602176634e-12

def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()
def read(p):
    with gzip.open(p,"rt",newline="") as f:return list(csv.DictReader(f))
def save(path,rows):
    with path.open("wb") as fp:
        with gzip.GzipFile(fileobj=fp,mode="wb",mtime=0,filename="") as f:
            with io.TextIOWrapper(f,encoding="utf-8",newline="") as t:
                writer=csv.DictWriter(t,fieldnames=list(rows[0]))
                writer.writeheader();writer.writerows(rows)
    return sha(path)

def audit(results_dir=RESULT):
    RESULT=Path(results_dir)
    r=json.loads((RESULT/"RESULT.json").read_text())
    table=RESULT/r["summary_file"]
    ang=RESULT/r["angle_file"]
    assert sha(table)==r["summary_sha256"] and sha(ang)==r["angle_sha256"]
    rows=read(table);rays=read(ang)
    assert len(rows)==r["epochs"]==2*EPOCHS
    assert len(rays)==r["angle_rows"]==2*EPOCHS*128
    groups={}
    for q in rays:
        key=(q["branch"],int(q["source_original_tick"]))
        groups.setdefault(key,[]).append(q)
        v=(float(q[x]) for x in ("characteristic_surviving_per_H",
                "characteristic_ionizing_per_H","characteristic_energy_eV_per_H",
                "characteristic_cumulative_absorbed_per_H",
                "characteristic_cumulative_photoheat_eV_per_H"))
        v=list(v)
        assert all(math.isfinite(x) for x in v) and min(v)>=0
        assert v[1]<=v[0]*(1+1e-12)
        assert v[4]<=(BIRTH-ION)*v[3]*(1+1e-9)+1e-18
        qn=tuple(float(q[x]) for x in ("q_x","q_y","q_z"))
        assert abs(sum(x*x for x in qn)-1)<1e-11
    assert len(groups)==30
    physical=[]
    errors={"count":0.,"energy":0.,"rate":0.,"ray_sum":0.,"binding":0.}
    originals=[]
    for x in rows:
        key=(x["branch"],int(x["original_tick"]))
        rr=groups[key]
        assert len(rr)==128
        t=float(x["proper_time_s"])
        assert abs(t-key[1]*6.25e8)<.01
        Nbirth=float(x["source_birth_n_per_H"])
        Nex=float(x["remaining_photon_n_per_H"])
        Aex=float(x["HI_cumulative_absorbed_photons_per_H"])
        Qex=float(x["HI_cumulative_excess_photoheat_eV_per_H"])
        Eabex=float(x["HI_cumulative_absorbed_energy_eV_per_H"])
        Eremain=float(x["photon_energy_eV_per_H"])
        Wred=float(x["cosmological_redshift_work_eV_per_H"])
        Nfix=float(x["fixed_hat_surviving_n_per_H"])
        Afix=float(x["fixed_hat_cumulative_absorbed_per_H"])
        Qfix=float(x["fixed_hat_cumulative_excess_photoheat_eV_per_H"])
        Eabfix=float(x["fixed_hat_cumulative_absorbed_energy_eV_per_H"])
        Gammaex=float(x["HI_photo_gamma_per_neutral_H_s"])
        Gammafix=float(x["fixed_hat_gamma_HI_per_neutral_s"])
        Gammaowner=float(x["original_F08_owner_gamma_HI_per_neutral_s"])
        abs_rate=float(x["HI_photo_rate_per_original_H_s"])
        xhi=1-float(x["original_F08_owner_x_HII"])
        assert 0<=xhi<=1
        errors["count"]=max(errors["count"],abs(Nbirth-Aex-Nex))
        errors["energy"]=max(errors["energy"],abs(BIRTH*Nbirth-Eremain-Eabex-Wred))
        errors["rate"]=max(errors["rate"],abs(abs_rate-xhi*Gammaex))
        errors["binding"]=max(errors["binding"],abs(Eabex-Qex-ION*Aex),
             abs(Eabfix-Qfix-ION*Afix))
        for rowcol,raycol in (
              ("remaining_photon_n_per_H","characteristic_surviving_per_H"),
              ("HI_cumulative_absorbed_photons_per_H","characteristic_cumulative_absorbed_per_H"),
              ("HI_cumulative_excess_photoheat_eV_per_H","characteristic_cumulative_photoheat_eV_per_H"),
              ("HI_photoheating_rate_eV_per_original_H_s","characteristic_heat_rate_eV_per_H_s"),
              ("photon_energy_eV_per_H","characteristic_energy_eV_per_H")):
            diff=abs(math.fsum(float(y[raycol]) for y in rr)-float(x[rowcol]))
            errors["ray_sum"]=max(errors["ray_sum"],diff)
        assert min(Nex,Aex,Qex,Eremain,Wred,Nfix,Afix,Qfix,Gammaex,Gammafix,Gammaowner)>=0
        assert math.isfinite(Gammaex/Gammaowner)
        binding_delta=ION*(Aex-Afix)
        heat_delta=Qex-Qfix
        ion_events_delta=Aex-Afix
        physical.append({
            "branch":key[0],"original_tick":key[1],"proper_time_s":t,
            "original_f08_gamma_HI_per_s":Gammaowner,
            "source_exact_gamma_HI_per_s":Gammaex,
            "fixed_hat_gamma_HI_per_s":Gammafix,
            "source_exact_over_owner_gamma_minus1":Gammaex/Gammaowner-1,
            "source_exact_over_fixed_gamma_minus1":Gammaex/Gammafix-1,
            "source_exact_cumulative_absorbed_photons_per_H":Aex,
            "fixed_hat_cumulative_absorbed_photons_per_H":Afix,
            "delta_physical_HI_ionizations_per_original_H":ion_events_delta,
            "delta_HI_chemical_binding_energy_eV_per_H":binding_delta,
            "delta_HI_chemical_binding_energy_erg_per_H":binding_delta*EV_TO_ERG,
            "source_exact_excess_photoheat_eV_per_H":Qex,
            "fixed_hat_excess_photoheat_eV_per_H":Qfix,
            "delta_excess_photoheat_eV_per_H":heat_delta,
            "delta_excess_photoheat_percent_of_fixed":100*heat_delta/Qfix,
            "total_source_conditional_photon_absorbed_energy_difference_eV_per_H":Eabex-Eabfix,
            "ionizing_photons_exact_per_H":float(x["ionizing_photon_n_per_H"]),
            "surviving_total_photons_exact_per_H":Nex,
            "source_exact_cosmological_redshift_work_eV_per_H":Wred,
            "original_f08_owner_photons_per_H":float(x["original_F08_owner_photon_n_per_H"]),
            "original_f08_owner_cumulative_absorbed_photons_per_H":float(x["original_F08_owner_absorbed_n_per_H"]),
            "scientific_owner_note":"FROZEN_REI_HHE_MATTER_NO_CHEMICAL_FEEDBACK"
        })
        originals.append({"branch":key[0],"tick":key[1],"owner_rel":Gammaex/Gammaowner-1})
    assert errors["count"]<5e-13,errors
    assert errors["energy"]<5e-13,errors
    assert errors["rate"]<1e-25,errors
    assert errors["binding"]<4e-13,errors
    assert errors["ray_sum"]<5e-13,errors
    result_path=RESULT/"F08_S0_HI_IONIZATION_BINDING_AND_HEAT_RESPONSE.csv.gz"
    result_sha=save(result_path,physical)
    report={"schema":"BASS_REI_F08_S0_HI_BINDING_HEAT_SAME_AUTHOR_ADVERSARIAL_AUDIT_V1",
      "verification":"PASS_SOURCE_CONDITIONAL_DATA_ONLY",
      "source_exact_owner":"S0_13.7eV_ORIGINAL_SOURCE_F08_FROZEN_HHE",
      "physical_model_error":"UNBOUNDED",
      "original_F08_photon_state_equivalence":"NOT_CERTIFIED",
      "original_HHe_solver_replayed":False,
      "records":{"physical_summary":len(rows),"source_q_angle":len(rays),
                 "binding_and_heat":len(physical)},
      "max_numerical_residuals":errors,
      "energy_response_sha256":result_sha,
      "energy_response_file":result_path.name,
      "physically_important_BI_tick16000":next(z for z in physical if z["branch"]=="S0_BI" and z["original_tick"]==16000),
      "no_native_subagent":True,"blind_referee_distinct_author":"NOT_RUN",
      "REI_canonical":"28/88_REPORTED","BASS_upper":"9/15_SCOPED_SOURCE_MAPPED",
      "canonical_delta":0,"production":"HOLD"}
    (RESULT/"AUDIT.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("SCIENCE_AUDIT_PASS",json.dumps({"rows":report["records"],"residuals":errors,"BI_final":report["physically_important_BI_tick16000"]},sort_keys=True))
    return report
if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=RESULT)
    audit(p.parse_args().out)
