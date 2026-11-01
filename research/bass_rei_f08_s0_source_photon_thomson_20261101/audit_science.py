#!/usr/bin/env python3
"""Read-only same-author adversarial cross-check for BASS REI-F08 S0.
No equivalence to original discretized photon solver is certified.
"""
from pathlib import Path
import csv,gzip,hashlib,json,math,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from s0_source_photon_thomson import source_histories,C,SIG_T,BIRTH_EV,SHA,digest,ROOT

def audit():
    r=json.loads((ROOT/"results/RESULT.json").read_text())
    hs=source_histories()
    if r["source_sha256"] != SHA:raise AssertionError("source provenance mismatch")
    path=ROOT/"results"/r["sky_filename"]
    if digest(path)!=r["sky_sha256"]:raise AssertionError("published sky SHA drift")
    with gzip.open(path,"rt",newline="") as f: rows=list(csv.DictReader(f))
    if len(rows)!=4096 or r["sky_rows"]!=4096:raise AssertionError("4096 ray claim")
    per=[]
    max_relative_energy_gain_error=0.
    global_max_flrw=0.
    by={(e["branch"],e["observer_time_s"]):e for e in r["epochs"]}
    for (lab,t),e in by.items():
        h=hs[lab]
        g=[q for q in rows if (q["branch"],float(q["epoch_s"]))==(lab,t)]
        if len(g)!=512:raise AssertionError("expected 512 sky directions per original epoch")
        if not (0.0 < e["model_survivor_n_per_H"] < 0.1+1e-13):raise AssertionError("nonphysical photon count")
        if not (0.0 <= e["model_photons_below_10eV_per_H"] < 1e-15):raise AssertionError("physical redshift below 10 eV")
        if not (float(e["original_lower_guard_n_per_H"])>0):raise AssertionError("unexpected missing original guard")
        if not (e["original_lower_guard_n_per_H"]/e["original_survivor_n_per_H"] >0):raise AssertionError("guard count wrong")
        src_energy=e["pre_first_scatter_unscattered_u_ev_per_H"]
        ne=h.linear(h.ne,t)
        scatter_rate=C*SIG_T*ne
        integrated_I=0.; pmax=0.; pmean=0.
        for q in g:
            I,Q,U,P=(float(q[k]) for k in (
                "out_gain_I_ev_per_H_s_sr","out_gain_Q_ev_per_H_s_sr",
                "out_gain_U_ev_per_H_s_sr","out_gain_P_over_I"))
            if not all(map(math.isfinite,(I,Q,U,P))) or I<0 or P<0 or P>1:
                raise AssertionError("invalid polarized intensity")
            if not math.isclose(math.hypot(Q,U),I*P,rel_tol=3e-12,abs_tol=2e-34):
                raise AssertionError("Stokes polarization fraction inconsistent")
            integrated_I+=I*4*math.pi/len(g)
            pmax=max(pmax,P)
            pmean+=P/len(g)
        relative=integrated_I/(src_energy*scatter_rate)-1
        max_relative_energy_gain_error=max(max_relative_energy_gain_error,abs(relative))
        if abs(relative)>1e-6:raise AssertionError("Thomson gain angular-integral/energy constraint")
        if lab=="S0_FLRW":
            global_max_flrw=max(global_max_flrw,pmax)
            if pmax>2e-11:raise AssertionError("FLRW generated false polarization")
        else:
            if pmax<1e-6:raise AssertionError("Bianchi original prescribed shear produced zero polarization")
        per.append({"branch":lab,"observer_t_s":t,"total_outgoing_gain_ev_per_H_s":integrated_I,
             "source_gain_energy_ev_per_H_s":src_energy*scatter_rate,
             "sky_gain_relative_conservation_residual":relative,
             "mean_P_over_I":pmean,"max_P_over_I":pmax,
             "source_owner_vs_independent_photon_n_relative":e["model_minus_original_n_rel"],
             "source_owner_below_10eV_guard_n_per_H":e["original_lower_guard_n_per_H"],
             "mathematical_source_support_min_eV":e["exact_null_minimum_E_ev"]})
    # Mathematical source-bound theorem, no observational or numerical-model acceptance.
    min_ev=BIRTH_EV*math.exp(-max(max(h.H) for h in hs.values())*1e13)
    if min_ev<=10 or global_max_flrw>=2e-11:raise AssertionError("analytic exact-redshift bound/control failed")
    out={
        "schema":"BASS_REI_S0_INDEPENDENT_IMPLEMENTATION_AUDIT_V1",
        "scope":"same_author_read_only_finite_model_crosscheck_not_independent_referee",
        "science_status":"SOURCE_CONDITIONAL_HOLD_NO_DAG_PROMOTION",
        "source_sha":SHA,
        "source_original_F08":"HOLD",
        "model_source_energy_min_eV":min_ev,
        "guard_conflict":"original discrete below-10eV guard violates exact source characteristic support; error mechanism unresolved",
        "full_equivalence_to_original_photon_discrete_transfer":False,
        "sky_sha256":r["sky_sha256"],"sky_rows":4096,
        "max_sky_integrated_Thomson_gain_relative_residual":max_relative_energy_gain_error,
        "max_FLRW_P_over_I":global_max_flrw,
        "records":per,
        "REI_CENTRAL":"28/88_REPORTED_DELTA_0",
        "BASS_UPPER":"9/15_SCOPED_SOURCE_MAPPED_NO_NEW_FULL",
        "verdict":"PASS_FROZEN_CONDITIONAL_MODEL; UNRESOLVED_ORIGINAL_PHOTON_OWNER_EQUIVALENCE"
    }
    (ROOT/"results/INDEPENDENT_AUDIT.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"verdict":out["verdict"],"max_conservation_residual":max_relative_energy_gain_error,
         "FLRW_max_P_over_I":global_max_flrw,"records":len(per)},sort_keys=True))
if __name__=="__main__":audit()
