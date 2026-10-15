"""Emit physically typed, REI-AX03-source-bound background & photon tables.

Purely external component to the current live Rust solver (no owner modification).
Background proper-time clock never passes ln(a) as elapsed SI seconds.
"""
from __future__ import annotations
import argparse,csv,json,hashlib,platform
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator

from axbi_provider import Background,Family,_read_lock,LOCK_SHA,photon_pullback

TAGS=["PhysicalDensityFixed","SameHDiagnostic"]
Q=[0.,.005,-.005,.01,-.01]
BG_COLS=["family","q_ref","row","ln_a_over_aref","a","zbar",
         "proper_elapsed_s","b","H_flrw_per_s","H_mean_per_s",
         "shear_s_per_s","sigma_s_over_H","sigma_tensor_squared_per_s2",
         "H_perp_per_s","H_parallel_per_s","a_perp","a_parallel",
         "n_H_cm3","n_He_cm3","Tbar_CMB_K","dt_dln_a_s","db_dln_a",
         "dproper_t_dz_s","volume_a_perp2_a_parallel"]
PH_COLS=["family","q_ref","row","zbar","proper_elapsed_s",
         "mu_face","energy_early_over_face","mu_early",
         "jacobian_dOmega_early_over_face","number_volume_invariant",
         "geometry_volume_factor"]

def write(rows,path,fields):
    if path.exists():raise FileExistsError(path)
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

def generate(outroot:Path,n=501):
    lock=_read_lock()
    if outroot.exists():raise FileExistsError("create-only destination")
    outroot.mkdir(parents=True)
    bg_rows=[]
    photon_rows=[]
    scenarios=[(q,"PhysicalDensityFixed") for q in Q]+[(.01,"SameHDiagnostic")]
    for q,family in scenarios:
        obj=Background(Family(q,family))
        data=obj.table(n)
        earliest=obj.at_a(obj.aref)
        latest=obj.at_a(obj.aend)
        for i in range(n):
            row={k:float(np.asarray(v)[i]) for k,v in data.items()}
            if i==0:
                row["a"]=obj.aref;row["zbar"]=20.;row["proper_elapsed_s"]=0.;row["b"]=0.
            if i==n-1:
                row["a"]=obj.aend;row["zbar"]=4.
            row.update({"family":family,"q_ref":q,"row":i})
            bg_rows.append({k:row[k] for k in BG_COLS})
            if i%2==0 or i==n-1:
                earlier=obj.at_x(float(data["ln_a_over_aref"][i]))
                for mu in (-1.,-.6,0.,.6,1.):
                    qmap=photon_pullback(earlier,latest,mu)
                    v={"family":family,"q_ref":q,"row":i,
                       "zbar":row["zbar"],"proper_elapsed_s":row["proper_elapsed_s"],
                       "mu_face":mu}
                    v.update({k:float(np.asarray(z)) for k,z in qmap.items()})
                    photon_rows.append({k:v[k] for k in PH_COLS})
    table=outroot/"AX03_BACKGROUND.csv"
    photon=outroot/"AX03_PHOTON_KILLING.csv"
    write(bg_rows,table,BG_COLS)
    write(photon_rows,photon,PH_COLS)
    metadata={"schema":"bass.rei.axbi.table_consumer_contract.v1",
      "source_background_family_sha256":LOCK_SHA,
      "source_lock":lock,
      "model":"original REI AX03 StressFree prescribed Bianchi I; geometry-only physical density fixed plus SAME_H counterfactual",
      "native_Rust_integration_status":"NOT_APPLIED_OWNER_REPO_READ_ONLY",
      "n_cases":len(scenarios),"sample_count_per_case":n,
      "rows_background":len(bg_rows),"rows_photon":len(photon_rows),
      "boundary":{"a_ref":lock["clock"]["a_ref"],"a_end":lock["clock"]["a_end"],
                  "proper_t_ref_s":0,"redshift_mean_ref":20.,"redshift_mean_end":4.},
      "units":{"proper_elapsed_s":"SI elapsed proper seconds from zbar20, not absolute age",
             "H_flrw_per_s":"SI s^-1","H_mean_per_s":"SI s^-1","shear_s_per_s":"SI s^-1",
             "a":"dimensionless mean scale factor","zbar":"1/a-1 mean redshift",
             "n_H_cm3":"physical H nuclei per cm^3, frozen baryon mass approximation",
             "n_He_cm3":"physical He nuclei per cm^3, frozen baryon mass approximation",
             "Tbar_CMB_K":"isotropic reference T0/a only; NOT exact direction-dependent CMB color temperature",
             "b":"dimensionless axes convention","mu_face":"orthonormal longitudinal direction cosine at late endpoint",
             "energy_early_over_face":"dimensionless Killing photon frequency ratio",
             "jacobian_dOmega_early_over_face":"dimensionless solid-angle Jacobian"},
      "scientific_locks":{"same_h":"counterfactual only","reference_CMB_feedback":"NOT_INCLUDED",
       "ionizing_radiation_backreaction":"NOT_INCLUDED",
       "full_ionization_history":"NOT_ATTEMPTED","native_axbi_science_admission":"NOT_ISSUED",
       "ordinary_z_isotropic_assumption":"zbar is mean-scale chart not a unique photon observed redshift"},
      "fields_background":BG_COLS,"fields_photon":PH_COLS,
      "file_sha256":{table.name:hashlib.sha256(table.read_bytes()).hexdigest(),
                     photon.name:hashlib.sha256(photon.read_bytes()).hexdigest()},
      "data_identity":"full CSV content sha256; decimal binary64 serialization; not equivalent to original Rust Simpson binary64 bit identity"}
    (outroot/"AX03_SUPPLIER_CONTRACT.json").write_text(json.dumps(metadata,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"path":str(outroot),"n_cases":len(scenarios),"background_rows":len(bg_rows),
      "photon_rows":len(photon_rows),"background_sha256":metadata["file_sha256"][table.name],
      "photon_sha256":metadata["file_sha256"][photon.name]},indent=2))
    return metadata

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--rows",type=int,default=501)
    a=parser.parse_args()
    generate(a.output_dir,a.rows)
