"""Independent saved-data audit, deliberately NO import of BASS RHS.

Exceptions, never assert, to execute identically under `python` and `python -O`.
Verifies physical proper-time chemistry rates, 4-force Minkowski norm,
chemical mass/emission algebra and scoped Einstein numerical constraints.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path

# Independently restated SI constants and original class fit (not importing BASS).
E=1.602176634e-19
KB=1.380649e-23
H_PLANCK=6.62607015e-34
M_E=9.1093837139e-31
C=299792458.
SIGMA_T=6.6524587051e-29
TSTAR=218601.80677272403*365.25*86400.

def ensure(condition,message):
    if not condition:raise ArithmeticError("HOSTILE_KM2J_AUDIT "+message)

def alpha(T):
    f=T/1.e4
    return 4.309e-19*f**(-.6166)/(1+.6703*f**.53)

def audit(source,output):
    raw=Path(source).read_bytes()
    d=json.loads(raw)
    ensure(d["upper_dag"]=="9/15" and d["new_upper_nodes"]==0,"DAG")
    ensure(not d["merge_ready"] and not d["production_ready"] and not d["auto_next"],"FALSE_PASS")
    maxima={"rest_chem_rate_relative":0.,"mass_fraction_error":0.,
            "grey_energy_source_abs":0.,"thomson_rate_relative":0.,
            "fourforce_rest_norm_abs":0.,"fourforce_time_component_abs":0.,
            "chemical_quadrature_relative":0., "constraint_max":0.}
    nrows=0;nsource=0
    ensure(set(d["cases"])=={"GL12","GL16"},"ANGULAR_GRIDS")
    for label,case in d["cases"].items():
        ensure(set(case["cases"])=={"full","opacity_only"},"CONTROL_MISSING "+label)
        ensure(case["parent_original_Einstein_IVP_nfev"]>10,"PARENT_IVP_NOT_RUN "+label)
        a=case["cases"]["full"]
        b=case["cases"]["opacity_only"]
        ensure(abs(case["comparison"]["full_minus_opacity_only_photon_rho"])>1e-12,"NO_BINDING_PHOTON_RESPONSE")
        ensure(case["comparison"]["full_minus_parent_shear_matrix_frob"]>1e-8,"NO_NEW_GR_SHEAR_RESPONSE")
        for mode,case2 in case["cases"].items():
            epochs=case2["epochs"]
            ensure(len(epochs)==41,"NO_REACTION_TRAJECTORY")
            x0=epochs[0]["x_e"]
            eta=case2["mass_eta"]
            for v in epochs:
                nrows+=1
                x=v["x_e"];gamma=v["gamma_b"];Tm=v["T_m_K"];Tg=v["T_gamma_K"];nH=v["nH_m3"]
                ensure(0<x<1 and Tm>0 and Tg>0 and nH>0 and gamma>=1,"UNPHYSICAL_STATE")
                beta=alpha(Tg)*(2*math.pi*M_E*KB*Tg/H_PLANCK**2)**1.5*math.exp(-3.4*E/(KB*Tg))
                La=v["lambda_lya_s"]
                escape=(La+8.2245809)/(La+8.2245809+beta)
                ion=beta*(1-x)*math.exp(-10.2*E/(KB*Tg))
                rate=TSTAR*escape*(ion-alpha(Tm)*nH*x*x)/gamma
                maxima["rest_chem_rate_relative"]=max(maxima["rest_chem_rate_relative"],
                    abs(rate-v["xprime_u"])/max(1e-12,abs(rate)))
                expected_nu=nH*x*SIGMA_T*C*TSTAR
                maxima["thomson_rate_relative"]=max(maxima["thomson_rate_relative"],
                    abs(expected_nu/v["nu_live"]-1))
                mass=1+eta*(x-x0) if mode=="full" else 1.
                maxima["mass_fraction_error"]=max(maxima["mass_fraction_error"],
                    abs(mass-v["chemical_mass_ratio"]))
                greysrc=-(v["rho_baryon"]*eta*v["xprime_u"])/(mass*gamma) if mode=="full" else 0.
                maxima["grey_energy_source_abs"]=max(maxima["grey_energy_source_abs"],
                    abs(greysrc-v["chemical_rest_emission_per_u"]))
                maxima["constraint_max"]=max(maxima["constraint_max"],
                   v["hamiltonian_normalized"],v["momentum_constraint_normalized"])
            for z in case2["source_snapshots"]:
                nsource+=1
                s=z["chemical_rest_emission_per_u"];gamma=z["gamma_b"];F=z["chem_force"]
                maxima["fourforce_time_component_abs"]=max(maxima["fourforce_time_component_abs"],abs(F[0]-s*gamma))
                norm=F[0]**2-sum(v*v for v in F[1:])
                maxima["fourforce_rest_norm_abs"]=max(maxima["fourforce_rest_norm_abs"],abs(norm-s*s))
                maxima["chemical_quadrature_relative"]=max(maxima["chemical_quadrature_relative"],
                    z["chemical_force_moment_relative"])
                ensure(z["chemical_force_moment_relative"]<2e-12,"DISCRETE_CHEM_FORCE_FAIL")
            cons=case2["conservation"]
            ensure(cons["max_Hamiltonian_norm"]<5e-8,"HAMILTONIAN")
            ensure(cons["max_momentum_norm"]<5e-8,"MOMENTUM")
            ensure(cons["hamiltonian_propagation_error"]<5e-8,"HAMILTONIAN_PROPAGATION")
            ensure(cons["momentum_integrated_error"]<5e-8,"MOMENTUM_PROPAGATION")
    ensure(nrows==164 and nsource==12,"SOURCE_EPOCH_COUNTS")
    ensure(maxima["rest_chem_rate_relative"]<1e-11,"INDEPENDENT_PEEBLES_RATE")
    ensure(maxima["thomson_rate_relative"]<1e-12,"DIMENSIONAL_THOMSON_OPACITY")
    ensure(maxima["mass_fraction_error"]<1e-12,"CHEMICAL_MASS_DEFECT")
    ensure(maxima["grey_energy_source_abs"]<1e-15,"GREY_ENERGY_MATCH")
    ensure(maxima["fourforce_time_component_abs"]<1e-15,"CHEMICAL_ENERGY_FOURFORCE")
    ensure(maxima["fourforce_rest_norm_abs"]<1e-15,"CHEMICAL_MOMENTUM_FOURFORCE")
    ensure(abs(d["cases"]["GL12"]["comparison"]["chem_xe_end"]
         -d["cases"]["GL16"]["comparison"]["chem_xe_end"])<1e-5,"ANGULAR_SCOPED_XE_CONVERGENCE")
    receipt={"schema":"bass.km2j.saved_science_independent_arithmetic.v1",
             "source_sha256":hashlib.sha256(raw).hexdigest(),
             "no_import_of_BASS_RHS":True,"test_style":"raise ArithmeticError, survives python -O",
             "reaction_rows":nrows,"source_snapshots":nsource,"maxima":maxima,
             "verdict":"PASS_SCOPED"}
    out=Path(output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print("KM2J_HOSTILE_SAVED_AUDIT",receipt["verdict"],"rows",nrows,
          "rest_rate_rel",maxima["rest_chem_rate_relative"],
          "fourforce_rest_norm_abs",maxima["fourforce_rest_norm_abs"],flush=True)
    return receipt

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args();audit(a.source,a.output)
