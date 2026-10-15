"""Export source-frozen two-species kinetic π_ab and Sigma histories for REI intake.

NO native REI owner file changes. This exports a physically sourced background
table, not a coupled H/He ionization history or arbitrary viscous closure.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,sys,time
from pathlib import Path
import numpy as np
from sigma_matter import InitialStress,EinsteinVlasovSigmaMatter,sigma_from_legacy_q,LOCK_SHA

HERE=Path(__file__).resolve().parent
FIELD=["case_id","row","Sigma_ref","shear_orientation","radiation_fraction",
    "radiation_A","massive_matter_fraction","massive_matter_A","mass_over_Tref",
    "ln_a_over_aref","a","zbar","proper_elapsed_s","b","s_per_s","H_mean_per_s",
    "H_FLRW_ref_per_s","signed_s_over_H","Sigma","a_perp","a_parallel",
    "H_perp_per_s","H_parallel_per_s","shear2_per_s2",
    "radiation_kinetic_energy_J_m3","radiation_pressure_perp_J_m3",
    "radiation_pressure_parallel_J_m3","Pi_r_J_m3","pi_r_perp_J_m3","pi_r_parallel_J_m3",
    "matter_kinetic_energy_J_m3","matter_pressure_perp_J_m3",
    "matter_pressure_parallel_J_m3","Pi_m_J_m3","pi_m_perp_J_m3","pi_m_parallel_J_m3",
    "Pi_total_J_m3","n_H_cm3","n_He_cm3","Tbar_CMB_K",
    "dt_dln_a_s","db_dln_a","ds_dln_a_per_s","dH_dln_a_per_s","constraint_rel"]

def cases():
    s5=sigma_from_legacy_q(.005)
    s10=sigma_from_legacy_q(.01)
    c=[
      ("BASE_ZERO",InitialStress(0.)),
      ("SHEAR_PLUS_SIGMA",InitialStress(s10,1)),
      ("SHEAR_MINUS_SIGMA",InitialStress(s10,-1)),
      ("RADIATION_ONLY_SEED",InitialStress(0.,1,.5,.2)),
      ("MASSIVE_MATTER_ONLY_SEED",InitialStress(0.,1,0,0,.1,.5,30)),
      ("RADIATION_AND_MATTER_SEED",InitialStress(0.,1,.5,.2,.1,.5,30)),
      ("RADIATION_MINUS_MATTER_PLUS",InitialStress(0.,1,.5,-.2,.1,.5,30)),
      ("SHEAR_PLUS_RAD_PLUS",InitialStress(s10,1,.5,.2)),
      ("SHEAR_PLUS_MATTER_PLUS",InitialStress(s10,1,0,0,.1,.5,30)),
      ("SHEAR_PLUS_BOTH_PLUS",InitialStress(s10,1,.5,.2,.1,.5,30)),
      ("SHEAR_PLUS_BOTH_MINUS",InitialStress(s10,1,.5,-.2,.1,-.5,30)),
      ("SHEAR_MINUS_BOTH_PLUS",InitialStress(s10,-1,.5,.2,.1,.5,30)),
      ("SHEAR_HALF_PLUS_BOTH",InitialStress(s5,1,.5,.2,.1,.5,30)),
      ("SHEAR_PLUS_COLD_MATTER",InitialStress(s10,1,0,0,.1,.5,1000))
    ]
    return c

def write_csv(path,rows):
    if path.exists():raise FileExistsError(path)
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELD,lineterminator="\n")
        w.writeheader();w.writerows(rows)

def export(path:Path,n=501):
    if path.exists():raise FileExistsError(path)
    if not isinstance(n,int) or not 3<=n<=32769:raise ValueError("bounded table")
    path.mkdir(parents=True)
    cases_def=cases()
    rows=[]
    summary=[]
    for label,initial in cases_def:
        model=EinsteinVlasovSigmaMatter(initial,angular_n=32)
        table=model.table(n)
        first=model.initial_tensors()
        p=model.at_a(model.aend)
        for i in range(n):
            r={k:float(np.asarray(v)[i]) for k,v in table.items()}
            data={"case_id":label,"row":i,"Sigma_ref":initial.Sigma_ref,
                "shear_orientation":initial.shear_orientation,
                "radiation_fraction":initial.radiation_fraction,"radiation_A":initial.radiation_A,
                "massive_matter_fraction":initial.massive_matter_fraction,
                "massive_matter_A":initial.massive_matter_A,"mass_over_Tref":initial.mass_over_Tref,
                "ln_a_over_aref":r["x"]}
            data.update({k:r[k] for k in FIELD if k in r})
            rows.append({k:data[k] for k in FIELD})
        summary.append({"case_id":label,"initial":initial.__dict__,
            "initial_radiation_Pi_J_m3":first["initial_radiation_Pi_J_m3"],
            "initial_matter_Pi_J_m3":first["initial_matter_Pi_J_m3"],
            "Sigma_end":p["Sigma"],"b_end":p["b"],
            "signed_s_over_H_end":p["signed_s_over_H"],
            "t_end_s":p["proper_elapsed_s"],
            "Pi_r_end_J_m3":p["Pi_r_J_m3"],
            "Pi_m_end_J_m3":p["Pi_m_J_m3"],
            "ODE_nfev":model.nfev})
    history=path/"AX03_SIGMA_MASSIVE_HISTORIES.csv"
    write_csv(history,rows)
    contract={"schema":"bass.rei.axbi.sigma_matter_initial_pi.v1",
      "source_family_sha256":LOCK_SHA,
      "source_massive_quadrature":"original BASS bianchi/matter/freestream.py cached Q,DQ,FD momentum quadrature; angular GL32",
      "original_reference_literature":"Lewis and Challinor 2002 astro-ph/0203507 J^(i) moment hierarchy",
      "model":"self-consistent Bianchi-I collisionless massless radiation plus source-energy normalized MASSIVE matter subset of Omega_m",
      "important_scientific_scope":"not physical ionizing chemistry, collisionful Thomson transfer, observed CMB anisotropy, coupled baryon anisotropic viscosity",
      "units":{"Sigma":"sqrt(sigma_ab*sigma^ab/2)/H>=0","shear_orientation":"initial sign(s)",
        "signed_s_over_H":"signed LRS shear s/H distinct from Sigma/sqrt(3)",
        "Pi_r_J_m3":"radiation LRS Pi, diag(-Pi,-Pi,2Pi)",
        "Pi_m_J_m3":"massive collisionless LRS Pi, diag(-Pi,-Pi,2Pi)",
        "H_mean_per_s":"s^-1","proper_elapsed_s":"elapsed SI seconds since mean zbar=20",
        "n_H_cm3":"background baryon H nuclei untouched",
        "Tbar_CMB_K":"T0/a isotropic reference, not directional CMB temperature"},
      "initial_parameters":{
        "Sigma_ref":"non-negative scalar", "shear_orientation":"signed +/-1",
        "radiation_fraction":"fraction of ORIGINAL Omega_r transferred from perfect to massless Vlasov",
        "massive_matter_fraction":"fraction of ORIGINAL Omega_m, <=nonbaryonic budget, transferred to massive Vlasov",
        "radiation_A":"positive initial Wrad=1+Ar P2, Ar in [-1,2]",
        "massive_matter_A":"positive initial Wmatter=1+Am P2, Am in [-1,2]",
        "mass_over_Tref":"thermal comoving momentum to mass ratio input, not measured DM mass"},
      "energy_bookkeeping":"Omega_m and Omega_r each split into perfect vs kinetic fractions at a_ref; a0 energy constraint unchanged",
      "source_solver_sha256":hashlib.sha256((HERE/"sigma_matter.py").read_bytes()).hexdigest(),
      "history_sha256":hashlib.sha256(history.read_bytes()).hexdigest(),
      "n_cases":len(cases_def),"n_per_case":n,"history_rows":len(rows),
      "cases":summary,"native_REI_science_admission":"NOT_ISSUED"}
    meta=path/"AX03_SIGMA_MATTER_CONTRACT.json"
    meta.write_text(json.dumps(contract,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"path":str(path),"cases":len(cases_def),"rows":len(rows),"table_sha256":contract["history_sha256"]},indent=2))
    return contract

if __name__=="__main__":
    pa=argparse.ArgumentParser()
    pa.add_argument("--out-dir",type=Path,required=True)
    pa.add_argument("--nodes",type=int,default=501)
    args=pa.parse_args()
    export(args.out_dir,args.nodes)
