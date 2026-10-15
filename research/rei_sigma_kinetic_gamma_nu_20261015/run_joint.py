"""Actual source-pinned 8-case Einstein+gamma/nu+massive background campaign.

Publishes typed csv for downstream rei_bianchi; donor is a verified one-way
original q=0 real HHe ne source. No raw/private source history is republished.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,sys,time
from pathlib import Path
import numpy as np
from joint_kinetic import (
 KineticGammaNuMassive,source_lock,verify_original_sources,
 actual_AX08_electron_donor,PARENT_REI_HEAD,PARENT_BASS_HEAD)

HERE=Path(__file__).resolve().parent
HEADERS=("case","x","a","zbar","proper_elapsed_s","b","s_per_s","H_mean_per_s",
        "Sigma","orientation","pi_gamma_J_m3","pi_nu_J_m3","pi_massive_J_m3",
        "pi_total_J_m3","radiation_rho_J_m3","massive_rho_J_m3",
        "H_perp_per_s","H_parallel_per_s","a_perp","a_parallel",
        "gamma_energy_J0","gamma_energy_J2","nu_energy_J0","nu_energy_J2",
        "gamma_number_N0","nu_number_N0","GammaT_per_s","n_e_cm3",
        "massive_pbar_J_m3","Raychaudhuri_dHdx_per_s")

def cases():
    q=.01
    sigma=math.sqrt(3)*q/math.hypot(1.,q)
    args=dict(kappa_gamma=.2,kappa_nu=.2,massive_fraction=.1,massive_A=.5,
              m_over_Tref=30.,ellmax=8)
    return [
      ("FLRW_CONTROL",dict(Sigma_ref=0.,orientation=0,kappa_gamma=0.,
                            kappa_nu=0.,massive_fraction=0.,massive_A=0.)),
      ("RADIATION_ONLY",dict(Sigma_ref=0.,orientation=0,kappa_gamma=.2,
                             kappa_nu=.2,massive_fraction=0.,massive_A=0.)),
      ("MASSIVE_ONLY",dict(Sigma_ref=0.,orientation=0,kappa_gamma=0.,
                            kappa_nu=0.,massive_fraction=.1,massive_A=.5)),
      ("BOTH_PRIMORDIAL",dict(args,Sigma_ref=0.,orientation=0)),
      ("BOTH_THOMSON_AX08",dict(args,Sigma_ref=0.,orientation=0,real_donor=True)),
      ("SIGNED_PLUS",dict(args,Sigma_ref=sigma,orientation=1)),
      ("SIGNED_MINUS",dict(args,Sigma_ref=sigma,orientation=-1)),
      ("GAMMA_ONLY_THOMSON",dict(args,Sigma_ref=0.,orientation=0,kappa_nu=0.,real_donor=True))
    ]

def execute(outdir:Path,n=401,*,stable_massive_pi:bool=False):
    outdir=outdir.resolve()
    if outdir.exists():raise FileExistsError(outdir)
    outdir.mkdir(parents=True)
    frozen=verify_original_sources();src=source_lock()
    donor,dmeta=actual_AX08_electron_donor(Path("/home/cosmosapjw/Dropbox/bianchi/rei_bianchi"))
    settings=cases()
    entries=[];arr=[]
    for name,params in settings:
        params=params.copy()
        with_donor=params.pop("real_donor",False)
        model=KineticGammaNuMassive(src,ne_source=donor if with_donor else None,
                                  stable_massive_pi=stable_massive_pi,**params)
        p,fields,wall=model.integrate(n=n,rtol=2e-12,atol=8e-14)
        state_radiation0=model.initial_tensors()
        stage=[]
        maximum_residual=0
        for i,(x,f) in enumerate(zip(p.t,fields)):
            yp=p.y[:,i]
            check=model.constraint_and_work(float(x),yp)
            maximum_residual=max(maximum_residual,
               abs(check['gamma_monopole_work_residual']),
               abs(check['nu_monopole_work_residual']),
               abs(check['shear_Einstein_rhs_residual']))
            s=f["s"];a=f["a"];b=f["b"]
            row=dict(case=name,x=float(x),a=float(a),zbar=float(1/a-1),
               proper_elapsed_s=float(yp[0]/src.href),b=float(b),
               s_per_s=float(s),H_mean_per_s=float(f["H"]),Sigma=float(f["Sigma"]),
               orientation=int(np.sign(s)),
               pi_gamma_J_m3=float(f["pi_gamma_norm"]*src.rhocrit_j_m3),
               pi_nu_J_m3=float(f["pi_nu_norm"]*src.rhocrit_j_m3),
               pi_massive_J_m3=float(f["pi_massive_norm"]*src.rhocrit_j_m3),
               pi_total_J_m3=float(f["pi_radiation_J_m3"]+f["pi_massive_J_m3"]),
               radiation_rho_J_m3=float(f["rho_r_J_m3"]),
               massive_rho_J_m3=float(f["rho_m_J_m3"]),
               H_perp_per_s=float(f["H"]-s),H_parallel_per_s=float(f["H"]+2*s),
               a_perp=float(a*math.exp(-b)),a_parallel=float(a*math.exp(2*b)),
               gamma_energy_J0=float(f["E_gamma"][0]),
               gamma_energy_J2=float(f["E_gamma"][2]),
               nu_energy_J0=float(f["E_nu"][0]),
               nu_energy_J2=float(f["E_nu"][2]),
               gamma_number_N0=float(f["N_gamma"][0]),
               nu_number_N0=float(f["N_nu"][0]),
               GammaT_per_s=float(f["GammaT"]),
               n_e_cm3=float(f["electron_density_cm3"]),
               massive_pbar_J_m3=float(f["pbar_massive_norm"]*src.rhocrit_j_m3),
               Raychaudhuri_dHdx_per_s=float(f["meanH_prime_x"]))
            stage.append(row)
        arr.extend(stage)
        last=stage[-1]
        entries.append({"case":name,"settings":params,"actual_one_way_HHe_donor":with_donor,
            "DOP853_wall_s":wall,"nfev":p.nfev,
            "Sigma_end":last["Sigma"],"b_end":last["b"],"proper_t_end_s":last["proper_elapsed_s"],
            "J2_gamma_end":last["gamma_energy_J2"],"J2_nu_end":last["nu_energy_J2"],
            "Pi_massive_end_J_m3":last["pi_massive_J_m3"],
            "max_algebraic_moment_work_residual":maximum_residual,
            "initial_Pi":state_radiation0,
            "minimum_angular_brightness_sampled":min(model.minimum_angular_brightness(
                  p.y[:,i]) for i in (0,n//4,n//2,3*n//4,n-1))})
        print("CASE",name,"Sigma",last["Sigma"],"b",last["b"],
              "gamma2",last["gamma_energy_J2"],"Pi_m",last["pi_massive_J_m3"],
              "wall",round(wall,4),flush=True)
    csv_path=outdir/"REI_GAMMANU_MASSIVE_BACKGROUND.csv"
    with csv_path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=HEADERS,lineterminator="\n")
        w.writeheader()
        for row in arr:w.writerow(row)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    receipt={"schema":"bass.rei.axbi.massive_gamma_nu_einstein_background.v1",
      "source_model":"frozen AX03 + independently sourced BASS FD96 massive and REI gamma+masslessnu Boltzmann",
      "massive_pi_evaluation":("stable_inverse_energy" if stable_massive_pi else
                               "legacy_pressure_subtraction"),
      "source_parent_BASS_head":PARENT_BASS_HEAD,"source_parent_REI_head":PARENT_REI_HEAD,
      "AX03_family_source_sha256":"46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0",
      "source_q_ref_is_only_legacy_parity_adapter":True,
      "Sigma_definition":"sqrt(3)*abs(s)/H with separate shear_orientation",
      "initial_Pi_tensor_convention":"diag(-Pi,-Pi,2Pi); Pi=physical (P_parallel-P_perp)/3 in J/m3",
      "initial_radiation_distribution":"nonnegative W_gamma=1+kappa_gamma P2 and W_nu=1+kappa_nu P2",
      "initial_massive":"BASS original FD96 radial source positive W_m=1+A_m P2",
      "massive_fraction_budget":"part of original nonbaryonic Omega_m, not additive to Omega_m",
      "actual_one_way_AX08_electron_donor":dmeta,
      "source_Tcmb0_K":frozen["cosmology"]["Tcmb0_K"],
      "n_cases":len(settings),"samples_per_case":n,"n_rows":len(arr),
      "time_range":"source physical proper seconds from zbar20 to zbar4",
      "source_Rust_production_driver":"NOT_MODIFIED",
      "actual_native_HHe_coupled_dynamics":"NOT_RUN",
      "full_polarized_photon_Thomson":"NOT_IMPLEMENTED",
      "electron_backreaction_to_HHe_chemistry":"NOT_INCLUDED",
      "complete_radial_hierarchy_time_evolution":"MASSIVE_COLLISIONLESS_EXACT_KILLING_REFERENCE_ONLY",
      "scientific_admission":"BACKGROUND_RESEARCH_ONLY",
      "case_receipts":entries,"csv_sha256":sha(csv_path)}
    (outdir/"RESULTS.json").write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    return receipt

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--out",type=Path,required=True)
    a.add_argument("--points",type=int,default=401)
    a.add_argument("--stable-massive-pi",action="store_true",
                   help="Opt-in cancellation-resistant FD96 anisotropic stress")
    args=a.parse_args()
    execute(args.out,args.points,stable_massive_pi=args.stable_massive_pi)
