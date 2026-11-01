#!/usr/bin/env python3
"""C9 RHS-free saved-source hostile referee. No producer import, normal/-O fail identical."""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
CSV=HERE/"PHOTON_RAYS_401X26.csv"
DATA=HERE/"PHOTON_RAYS_RESULT.json"
CONV=HERE/"C8_CONVERGENCE.json"
OWNER=HERE/"ELECTRON_OWNER_PARITY.json"

def need(condition, message):
    if not bool(condition): raise ValueError(message)

def read():
    report=json.loads(DATA.read_text())
    conv=json.loads(CONV.read_text())
    owner=json.loads(OWNER.read_text())
    with CSV.open(newline="") as stream:
        reader=csv.DictReader(stream)
        rows=list(reader)
    return report,conv,owner,rows

def assess(report,conv,owner,rows):
    need(report["source_main"]=="9c6506e4e2087129a8b674ff10438e5db1a55c9d","SOURCE_ID")
    need(report["source_locked_original_9"]==9 and report["source_locked_extra_original"]==6,"SOURCE_PROVENANCE")
    need(len(rows)==10426,"ROW_COUNT")
    need(owner["owner_electron_transform_evaluations"]==10426 and owner["maximum_source_D_minus_analytic_Gamma_q"]<3e-14,"ELECTRON_OWNER_PARITY")
    need(report["rust_source_oracle_evaluations"]==10426 and report["rust_source_max_abs_gap"]<2e-12,"RUST_SOURCE_PARITY")
    need(conv["maximum_Radau_vs_DOP853_endpoint_abs_gap"]<3e-9 and all(x>3.3 for x in conv["RK4_observed_orders"][:3]),"CONVERGENCE")
    def vec(key):
        return np.array([float(row[key]) for row in rows],float).reshape((26,401))
    tau=vec("tau_H")
    ids=np.array([int(row["ray_id"]) for row in rows]).reshape((26,401))
    need(np.array_equal(ids,np.arange(26)[:,None]*np.ones((1,401),dtype=int)),"RAY_IDS")
    need(np.max(abs(tau-tau[0][None,:]))<1e-15 and abs(tau[0,-1]-0.2)<1e-15,"SOURCE_TIME")
    dn=np.stack([vec(k) for k in ("n_x","n_y","n_z")],axis=-1)
    norms=np.linalg.norm(dn,axis=-1)
    logE=vec("ln_E_normal");logI=vec("ln_I_normal");logEe=vec("ln_E_electron")
    unit=vec("optical_depth_unit_proper_rate")
    proxy=vec("optical_depth_proxy_if_proper")
    qonly=vec("optical_depth_q_only_wrong")
    need(np.isfinite(dn).all() and np.isfinite(logE).all() and np.isfinite(unit).all(),"FINITE_STATES")
    dnorm=float(np.max(abs(norms-1.0)))
    bol=float(np.max(abs(logI-4*logE)))
    need(dnorm<2e-10,"PHOTON_UNIT_SPHERE")
    need(bol<2e-10,"BOLOMETRIC_FOURTH_POWER")
    v0=.05;v1=.046733834290499716
    # The original Type II v(t) is NOT linearly interpolated: use exact original 401 source states,
    # and pin their sha in a separate original-main file instead of relying on producer metadata.
    fixture=json.loads((HERE.parents[1]/"compiler/validation/typeii_fixture_canonical.json").read_text())
    v=np.array([float(s["state"][4]) for s in fixture["trajectory"]["samples"]],float)
    need(len(v)==401 and v[0]==v0 and v[-1]==v1,"OWNER_V_HISTORY")
    doppler=(1-v[None,:]*dn[:,:,1])/np.sqrt(1-v[None,:]*v[None,:])
    electron=float(np.max(abs(logEe-logE-np.log(doppler))))
    need(electron<2e-9,"ELECTRON_FRAME_ENERGY_CHAIN")
    increments=np.diff(unit,axis=1)
    need(np.min(increments)>-1e-13,"NEGATIVE_OPTICAL_DEPTH_INCREMENT")
    need(np.min(np.diff(proxy,axis=1))>-1e-10,"NEGATIVE_PROXY_DEPTH_INCREMENT")
    # independent composite trapezoid for proper-electron unit opacity, does not call producer.
    trap=np.sum((doppler[:,:-1]+doppler[:,1:])*(tau[:,1:]-tau[:,:-1])*0.5,axis=1)
    trap_gap=float(np.max(abs(trap-unit[:,-1])))
    need(trap_gap<2e-8,"INTEGRATED_RATE_IDENTITY")
    need(float(np.max(abs(unit[:,-1]-qonly[:,-1])))>1e-4,"MISSING_GAMMA_NEGATIVE")
    need(report["negative_wrong_curvature_sign_endpoint_direction_gap"]>1e-3,"MISSING_CURVATURE_NEGATIVE")
    return {"source_rows":len(rows),"unit_sphere_defect":dnorm,"bolometric_log_defect":bol,
            "electron_rest_frame_log_chain_defect":electron,
            "trapezoidal_unit_optical_depth_max_gap":trap_gap,
            "minimum_depth_increment":float(increments.min()),
            "min_final_depth":float(unit[:,-1].min()),
            "max_final_depth":float(unit[:,-1].max()),
            "max_missed_gamma_depth":float(np.max(abs(unit[:,-1]-qonly[:,-1])))}

rep,conv,owner,rows=read()
summary=assess(rep,conv,owner,rows)
controls={}
from copy import deepcopy
def expected_rejection(name, mutate):
    r=deepcopy(rep);c=deepcopy(conv);o=deepcopy(owner)
    dataset=deepcopy(rows)
    mutate(r,c,o,dataset)
    try: assess(r,c,o,dataset)
    except ValueError as exc: controls[name]=str(exc)
    else: raise RuntimeError(f"HOSTILE_TAMPER_ACCEPTED: {name}")

expected_rejection("modified_source_claim",lambda r,c,o,rows:r.update(source_main="fake"))
expected_rejection("bolometric_power_mismatch",
                   lambda r,c,o,rows:rows[1000].update(ln_I_normal=str(float(rows[1000]["ln_I_normal"])+0.01)))
expected_rejection("negative_optical_depth",
                   lambda r,c,o,rows:rows[250].update(optical_depth_unit_proper_rate="-1.0"))
expected_rejection("missing_source_rows",
                   lambda r,c,o,rows:rows.pop())
expected_rejection("artificial_radau_convergence",
                   lambda r,c,o,rows:c.update(maximum_Radau_vs_DOP853_endpoint_abs_gap=1.0))
if len(controls)!=5:raise RuntimeError("MISSING_HOSTILE_CONTROLS")
out={
    "schema":"bass.typeii.RHS_free_saved_data_referee.v1",
    "test":summary,
    "negative_controls":controls,
    "output_csv_sha256":hashlib.sha256(CSV.read_bytes()).hexdigest(),
    "verdict":"PASS_SCOPED_SAME_AUTHOR_SAVED_EVIDENCE_REFEREE",
    "blind_distinct_author":"NOT_RUN",
    "scope":"Source-conditioned normal photon rays; no real electron n_e(t), no full radiation transport",
}
(HERE/"C9_REFEREE.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,sort_keys=True,indent=2))
