"""Publish self-consistent Bianchi-I initial stress histories as typed scientific data.

These are NOT prevalidated AX08 H/He histories. All cosmic radiation Omega_r
is treated as collisionless massless component from zbar=20; initial κ is a
positive quadrupole, independently specified from source-locked initial q.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from pathlib import Path
import numpy as np
import einstein_vlasov as ev
from vector_batch import CASES

G_SI=6.67430e-11
C_SI=299792458.0
FIELDS=["q_ref","kappa","initial_pi_over_epsrad_ref","row","ln_a_over_aref",
        "a","zbar","elapsed_proper_s","b","s_per_s","s_over_href",
        "h_per_s","s_over_h","h_perp_per_s","h_parallel_per_s",
        "a_perp","a_parallel","radiation_M","radiation_P",
        "rho_rad_J_m3","pi_s_J_m3","pi_x_J_m3","pi_y_J_m3","pi_z_J_m3",
        "radiation_density_over_crit0","pi_s_over_crit0",
        "Hamiltonian_rel_residual"]

def generate(directory:Path,n=501):
    if directory.exists():raise FileExistsError("immutable output directory already exists")
    directory.mkdir(parents=True,exist_ok=True)
    allrows=[]
    summary=[]
    for q,k in CASES:
        model=ev.KineticStressBackground(ev.Initial(q,k))
        field=model.table(n)
        crit=3*model.h0**2*C_SI**2/(8*math.pi*G_SI)
        H2model=(model.h0**2)*(model.om/field["a"]**3+
           model.ol+model.orad/field["a"]**4*field["radiation_monopole_M"])+field["s_per_s"]**2
        resid=H2model/field["h_per_s"]**2-1
        if np.max(abs(resid))>2e-13:
            raise ArithmeticError("Hamiltonian constraint failed in source table")
        for j in range(n):
            f={name:float(np.asarray(arr).item() if np.asarray(arr).ndim==0 else np.asarray(arr)[j]) for name,arr in field.items() if name!="pi_ab_over_crit_today"}
            rho=crit*f["radiation_density_over_crit_today"]
            pi=crit*f["pi_energy_over_crit_today"]
            row={"q_ref":q,"kappa":k,"initial_pi_over_epsrad_ref":k/15,
                 "row":j,"ln_a_over_aref":f["x"],
                 "a":f["a"],"zbar":f["zbar"],"elapsed_proper_s":f["elapsed_proper_s"],
                 "b":f["b"],"s_per_s":f["s_per_s"],"s_over_href":f["s_over_href"],
                 "h_per_s":f["h_per_s"],"s_over_h":f["s_per_s"]/f["h_per_s"],
                 "h_perp_per_s":f["h_perp_per_s"],"h_parallel_per_s":f["h_parallel_per_s"],
                 "a_perp":f["a_perp"],"a_parallel":f["a_parallel"],
                 "radiation_M":f["radiation_monopole_M"],"radiation_P":f["radiation_P"],
                 "rho_rad_J_m3":rho,"pi_s_J_m3":pi,
                 "pi_x_J_m3":-pi,"pi_y_J_m3":-pi,"pi_z_J_m3":2*pi,
                 "radiation_density_over_crit0":f["radiation_density_over_crit_today"],
                 "pi_s_over_crit0":f["pi_energy_over_crit_today"],
                 "Hamiltonian_rel_residual":float(resid[j])}
            allrows.append(row)
        p=allrows[-1]
        summary.append({"q_ref":q,"kappa":k,"initial_pi_over_epsrad_ref":k/15,
                        "b_end":p["b"],"s_over_h_end":p["s_over_h"],
                        "pi_over_rho_end":p["pi_s_J_m3"]/p["rho_rad_J_m3"],
                        "radiation_M_end":p["radiation_M"]})
    path=directory/"AXBI_INITIAL_STRESS_BACKGROUND.csv"
    with path.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS,lineterminator="\n")
        writer.writeheader();writer.writerows(allrows)
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    manifest={"schema":"rei.axbi.initial_stress_kinetic_background.v1",
      "original_SOURCE_LOCK_SHA256":ev.LOCK_SHA,
      "q_cases":[q for q,k in CASES],"kappa_cases":[k for q,k in CASES],
      "original_cosmology":ev._read_lock()["cosmology"],
      "reference_range":{"a0":1/21,"aend":.2,"mean_redshift_start":20,
        "mean_redshift_end":4,"clock":"SI proper seconds elapsed since mean zbar20"},
      "model":"positive collisionless massless radiation W(mu_ref)=1+kappa P2(mu_ref), independent initial shear q and angular stress κ, no emission/absorption/Thomson",
      "anisotropic_pressure_PSTF":{"components":"diag(-pi_s,-pi_s,2pi_s)","physical_units":"J/m^3",
        "initial_pi_s_over_rho_rad_ref":"kappa/15",
        "kinetic_exact_energy_consistency":"dM/db=-6 P"},
      "initial_stress_free_rei_original_status":"PREVIOUSLY_PRESCRIBED_STRESS_FREE_ONLY; NOT_OVERRIDDEN",
      "n_cases":len(CASES),"rows_per_case":n,"total_rows":len(allrows),
      "columns":FIELDS,"csv_sha256":digest,
      "source_rei_native_science_driver_connected":False,
      "ionizing_CMB_radiation_stress_self_consistent":False,
      "comparison":"original source Omega_r cosmological number remains, but all effective Omega_r assumed free-streaming after z20; phenomenological model scope conditional",
      "summary":summary}
    (directory/"AXBI_INITIAL_STRESS_MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps({"output":str(path),"sha256":digest,"rows":len(allrows),
      "first_nonzero_pi_endpoint":summary[1],"max_constraint":max(abs(x["Hamiltonian_rel_residual"]) for x in allrows)},indent=2))
    return manifest
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--directory",type=Path,required=True);p.add_argument("--rows",type=int,default=501)
    arg=p.parse_args();generate(arg.directory,arg.rows)
