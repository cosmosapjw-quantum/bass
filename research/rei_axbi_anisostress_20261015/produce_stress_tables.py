"""Source-bounded initial (shear, anisotropic stress) background delivery table.

Byte-level frozen original AX03 source identity, no overwrite of original
rei_bianchi Rust background family, no full H/He histories, no unsupported
claim for actual CMB or ionizing-radiation anisotropic stress.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
import numpy as np
import einstein_vlasov_lrs as e

HERE=Path(__file__).resolve().parent
FIELDS=[
 "case_id","q_ref","A","eta","row","x","a","zbar","t_elapsed_proper_s",
 "b","s_per_s","H_per_s","Hflrw_per_s","s_over_H","sigma2_per_s2",
 "a_perp","a_parallel","H_perp_per_s","H_parallel_per_s",
 "n_H_cm3","n_He_cm3","Tbar_CMB_reference_K","radiation_M0",
 "radiation_Mdelta","aniso_epsilon_J_m3","aniso_Pparallel_J_m3",
 "aniso_Pperp_J_m3","delta_Pparallel_minus_Pperp_J_m3",
 "pi_perp_J_m3","pi_parallel_J_m3","dt_dln_a_s","db_dln_a",
 "ds_dln_a_per_s","dH_dln_a_per_s","Hamiltonian_residual_s2"]
PHOTON_FIELDS=["case_id","a","initial_mu","E_over_E_ref",
               "mu_current","jac_dOmega_current_over_initial"]
CASES=[
 (0,0,0),(.005,0,0),(-.005,0,0),(.01,0,0),(-.01,0,0),
 (0,0,1),(0,1,1),(0,-1,1),(.005,1,1),(.005,-1,1),
 (-.005,1,1),(-.005,-1,1),(.01,0,1),(.01,1,1),
 (.01,-1,1),(-.01,1,1),(.01,1,.2)]

def export(path:Path,n=501):
    if path.exists():raise FileExistsError("immutable export directory exists")
    if n<3:raise ValueError("at least 3")
    path.mkdir(parents=True)
    file=path/"AX03_INITIAL_PI_BACKGROUND.csv"
    photon=path/"AX03_INITIAL_PI_KILLING.csv"
    summary=[]
    with file.open("w",newline="") as o,photon.open("w",newline="") as po:
        w=csv.DictWriter(o,fieldnames=FIELDS,lineterminator="\n")
        p=csv.DictWriter(po,fieldnames=PHOTON_FIELDS,lineterminator="\n")
        w.writeheader();p.writeheader()
        for q,A,eta in CASES:
            bg=e.EinsteinVlasovLRS(e.InitialData(q,A,eta),ang_n=64)
            data=bg.table(n)
            case=bg.initial.key
            for i in range(n):
                r={"case_id":case,"q_ref":q,"A":A,"eta":eta,"row":i}
                for k,v in data.items():
                    if k in FIELDS:r[k]=float(np.asarray(v)[i])
                w.writerow({k:r[k] for k in FIELDS})
                if i%5==0 or i==n-1:
                    for mu in (-1.,-.6,0.,.6,1.):
                        bb=r["b"]
                        R=np.sqrt(np.exp(2*bb)*(1-mu*mu)+np.exp(-4*bb)*mu*mu)
                        # Source Killing covector: original input direction at a_ref.
                        mu_current=mu*np.exp(-2*bb)/R
                        R3=R**(-3)  # dOmega_current/dOmega_ref = dmu_current/dmu_ref
                        p.writerow({"case_id":case,"a":r["a"],"initial_mu":mu,
                          "E_over_E_ref":bg.aref/r["a"]*R,
                          "mu_current":mu_current,
                          "jac_dOmega_current_over_initial":R3})
            end=bg.at_a(bg.aend)
            start=bg.at_a(bg.aref)
            summary.append({"case_id":case,"q_ref":q,"A":A,"eta":eta,
                "initial_deltaP_over_original_epsilon_rad":eta*A/5,
                "initial_pi_parallel_J_m3":start["pi_parallel_J_m3"],
                "initial_pi_perp_J_m3":start["pi_perp_J_m3"],
                "end_elapsed_proper_s":end["t_elapsed_proper_s"],
                "end_b":end["b"],
                "end_s_over_H":end["s_over_H"],
                "end_pressure_anisotropy_J_m3":end["delta_Pparallel_minus_Pperp_J_m3"]})
    frozen=e._read_lock()
    metadata={
      "schema":"bass.rei.axbi.initial_shear_plus_pi.bg_supplier.v1",
      "original_AX03_lock_sha256":e.LOCK_SHA,
      "original_AX03_cosmology":frozen["cosmology"],
      "source_family":"ADD_COLLISIONLESS_AXISYMMETRIC_QUADRUPOLAR_PART_OF_ORIGINAL_OMEGA_R",
      "assumptions":{
          "metric":"diag(-c^2,a^2 exp(-2b),a^2 exp(-2b),a^2 exp(4b))",
          "shear":"diag(-s,-s,2s) in comoving orthonormal frame, s=db/dt",
          "pi_tensor":"diag(-DeltaP/3,-DeltaP/3,2DeltaP/3) SI J/m^3",
          "initial_W_mu":"1+A*(3 mu^2-1)/2, -1<=A<=2",
          "original_Omega_r_split":"perfect radiation Omega_r*(1-eta) + exactly collisionless Omega_r*eta",
          "stress_free_original_limit":"eta=0 with any allowed A; exact source AX03",
          "initial_stress_independently_chosen":"DeltaP_ref/epsilon_original_r_ref=eta*A/5",
          "collisionless_radiation_backreaction":"SELF_CONSISTENT_UNDER_THIS_INITIAL_DISTRIBUTION",
          "full_CMB_neutrino_and_ionizing_stress":"NOT_MODELLED_FULLY"},
      "scientific_admission":"BACKGROUND_ONLY_EXPLORATORY_NO_OBSERVED_EOR",
      "trajectory_rows":n*len(CASES),
      "ray_rows":(n//5+1)*len(CASES)*5,
      "case_count":len(CASES),
      "cases":summary,
      "units":{"t_elapsed_proper_s":"seconds elapsed since mean zbar20",
             "H_per_s":"s^-1","s_per_s":"s^-1",
             "aniso_epsilon_J_m3":"J/m^3",
             "pi_parallel_J_m3":"pressure anisotropic trace-free component in SI J/m^3",
             "a":"dimensionless mean scale factor",
             "zbar":"mean-scale chart, not directly observable photon redshift"},
      "SHA256":{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in (file,photon)}
    }
    metadata["ray_rows"]=sum(1 for _ in photon.open())-1
    meta=path/"AX03_INITIAL_PI_CONTRACT.json"
    meta.write_text(json.dumps(metadata,indent=2,ensure_ascii=False)+"\n")
    print("INITIAL_PI_SOURCE_TABLE",len(CASES),n,metadata["trajectory_rows"],metadata["ray_rows"])
    print("FROZEN_HASHES",metadata["SHA256"])
    return metadata
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out-dir",type=Path,required=True)
    p.add_argument("--rows",type=int,default=501)
    a=p.parse_args();export(a.out_dir,a.rows)
