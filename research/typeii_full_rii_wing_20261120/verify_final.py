#!/usr/bin/env python3
"""One bounded source-locked scientific and same-author hostile verification pass."""
import ast,csv,hashlib,json,subprocess
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import expm_multiply
import hummer_rii as hum
import rii_transport as kernel
import outer_hummer as evolve

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PARENT="b23e75dcd2e8145cb161339bf08b6e1f522626f5"
def check(v,msg):
 if not bool(v):raise RuntimeError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(["git","-C",str(ROOT),*args],text=True).strip()
def verify():
 b=json.loads((HERE/"HUMMER_RII_ORIGINAL_BENCHMARK.json").read_text())
 lead=json.loads((HERE/"LEADING_RECOIL_AND_THERMAL_SENSITIVITY.json").read_text())
 sources=json.loads((HERE/"HUMMER_SOURCE_WING_CASES.json").read_text())["results"]
 more=json.loads((HERE/"HUMMER_REFINEMENT_CASES.json").read_text())
 latest=json.loads((HERE/"ANGULAR_TIME_PAIRED.json").read_text())
 pair=json.loads((HERE/"Q3_SCIENCE_INTERPRETATION.json").read_text())
 check(len(b["original_conditioned_velocity_comparisons"])==15 and b["static_source_kernel_checks"]["closed_vs_integrated_max_abs15"]<3e-10,
       "Hummer direct integration cross-check incomplete")
 check(len(lead["original_recoil_shift_conditions"])==15 and lead["analytic_shift_vs_parent_direct_recoil_max_conditional_gap"]<3e-10,
       "leading recoil shifted law not verified")
 check(len(sources)==12 and len(more)==3,"source scenario coverage incomplete")
 for name,v in [*sources.items(),*more.items()]:
  check(v["max_number_ledger_defect"]<5e-7 and v["max_frozen_midpoint_energy_generator_ledger_defect"]<3e-8,
        "finite source conservation "+name)
  check(abs(sum(v[k] for k in ("survival","red_outer_exit","blue_outer_exit","tagged_ionized"))-1)<5e-7,
        "finite source photon outcomes not normalized "+name)
 check(abs(pair["outer_160_vs_320_tagged_ionization_diff"])<5e-9,
       "outer boundary not converged for this declared model")
 check(abs(pair["time_256_to_512_X160_tagged_ionization_diff"])>1e-5,
       "source time error artificially hidden")
 check(abs(latest["ang6_14_at512_ion"])>1e-4 and abs(latest["ang14_t256_to512_ion"])>1e-5,
       "sky quadrature and timestep sensitivity not detected")
 check(abs(pair["raw_no_recoil_minus_therm_sym_X40_tagged_ionization"])>.5,
       "large thermal closure sensitivity not detected")
 check(lead["static_raw_Wien_defect_with_recoil_shift"]>1e-5 and
       lead["static_symmetrized_Wien_defect_with_recoil_shift"]<1e-12,
       "missing recoil/thermal equilibration distinction")
 # Independent static finite-generator differential-equation solver
 T=3000.745332620248
 g=kernel.matrix_kernel(X=40.,T=T,nl=253341572.44286457)
 Q=g["Q"]
 y=g["pi"]*(1+.1*np.sin(np.arange(len(g["pi"]))))
 y/=sum(y)
 exact=expm_multiply(csc_matrix(.5*Q),y)
 ode=solve_ivp(lambda t,p:Q@p,(0.,.5),y,method="BDF",jac=csc_matrix(Q),atol=2e-13,rtol=2e-11)
 check(ode.success,"independent BDF source generator failure")
 independent=float(np.max(abs(exact-ode.y[:,-1])))
 check(independent<2e-9 and abs(sum(exact)-1)<2e-12 and min(exact)>-1e-12,
       "static exact Hummer source generator BDF/Krylov or positivity failure")
 # Source original materials exact Git bytes; no guessed live branch state.
 orig=json.loads((ROOT/"research/typeii_host_preflight_20261101/SOURCE_LOCK.json").read_text())["original_git_blobs_sha1"]
 for path,want in orig.items():check(git("hash-object",path)==want,"BASS original source changed "+path)
 for file in ("research/typeii_correlated_outer_20261119/outer_transport.py",
              "research/typeii_correlated_outer_20261119/correlated.py",
              "research/typeii_redistribution_phase_20261116/redistribution.py"):
  check(git("hash-object",file)==git("rev-parse",PARENT+":"+file),
        "immutable parent source mismatch "+file)
 # Wrong and malformed source negative controls: execution must reject, no tolerance-widening.
 bad=[
  ("nonfinite_frequency",lambda:hum.conditional_bins(float("nan"),0.,.001,[-1.,1.])),
  ("negative_absorption_damping",lambda:hum.conditional_bins(2.,0.,-.1,[-1.,1.])),
  ("zero_absorption_damping",lambda:hum.conditional_bins(2.,0.,0.,[-1.,1.])),
  ("unphysical_mu",lambda:hum.conditional_bins(2.,1.01,.001,[-1.,1.])),
  ("bad_frequency_edges",lambda:hum.conditional_bins(2.,0.,.001,[0.,-1.,1.])),
  ("singleton_frequency_edges",lambda:hum.conditional_bins(2.,0.,.001,[0.])),
  ("negative_recoil",lambda:hum.leading_recoil_bins(2.,0.,.001,[-1.,1.],-.1)),
  ("negative_joint_mu",lambda:hum.joint(2.,0.,-1.1,.001)),
  ("unsupported_outer_width",lambda:kernel.extended_edges(500.)),
  ("unsupported_sky",lambda:kernel.matrix_kernel(angle_order=8)),
  ("negative_hydrogen_density",lambda:kernel.matrix_kernel(nl=-1)),
  ("bad_evolving_timestep",lambda:evolve.evolve(X=40.,steps=7))
 ]
 rejected={}
 for name,fn in bad:
  try:fn()
  except (ValueError,RuntimeError,ZeroDivisionError,OverflowError) as exc:rejected[name]=type(exc).__name__
  else:raise RuntimeError("accepted invalid source input "+name)
 # Current science code must not lose validation if Python -O is enabled.
 for name in ("hummer_rii.py","rii_transport.py","outer_hummer.py","compare_hummer.py",
              "source_wing_campaign.py","source_refinement.py","verify_recoil.py","verify_final.py"):
  nodes=ast.walk(ast.parse((HERE/name).read_text()))
  check(not any(isinstance(x,ast.Assert) for x in nodes),"bypassable scientific assert "+name)
 # Host stage receipts existing Q1-Q3 at this time
 host=Path("/home/cosmosapjw/research_backups/bass_typeii_full_rii_wing_20261120")
 rows=list(csv.reader((host/"STAGE_RECEIPTS.tsv").open(),delimiter="\t"))
 check([x[0] for x in rows]==["Q1","Q2","Q3"],"current archive stages before Q4")
 import zipfile
 for stage,commit,want,fn in rows:
  check(sha(fn)==want,"host backup SHA failed "+stage)
  with zipfile.ZipFile(fn) as z:check(z.testzip() is None,"host backup CRC failed "+stage)
  check(git("cat-file","-t",commit)=="commit","host commit missing "+stage)
 result={
  "schema":"bass.typeii.hummer_RII0_source_wings_verification.v1",
  "parent":PARENT,"source_BASS_Git_blobs_exact":len(orig),
  "parent_original_physics_source_byte_exact":3,
  "theory_Hummer_RII0_conditional_15_source_max_abs":b["static_source_kernel_checks"]["closed_vs_integrated_max_abs15"],
  "leading_recoil_15_source_max_abs":lead["analytic_shift_vs_parent_direct_recoil_max_conditional_gap"],
  "independent_BDF_Krylov_static_state_max_abs":independent,
  "actual_matched_finite_source_cases":len(sources)+len(more)+1,
  "actual_leading_recoil_source_cases":len(lead["source_cases"]),
  "physical_outer_width_time_error":pair,
  "angular_time_matched_error":latest,
  "negative_source_inputs_rejected":rejected,
  "source_scientific_code_bypassable_asserts":0,
  "host_pre_final_stage_archives_SHA256_CRC":len(rows),
  "scope_verdict":"ANALYTICALLY_SOURCE_MATCHED_CLASSICAL_HUMMER_RII0_AND_BOUNDED_FINITE_WING_MODEL_NUMERICALLY_VERIFIED",
  "not_established":["exact full quantum recoiling Hummer RII under all conditions",
                     "microscopic detailed balance from frequency shift alone",
                     "self-consistent cosmological photon/atom/Einstein feedback",
                     "full angle convergence","continuum time high accuracy",
                     "global Lyalpha escape or observed z0 CMB visibility"],
  "reviewer":"one bounded same-author hostile pass, no actual distinct-author blind referee or native subagent"
 }
 (HERE/"FINAL_VERIFICATION.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print("SCIENCE_FINAL_CHECKS",json.dumps({k:result[k] for k in (
  "source_BASS_Git_blobs_exact","independent_BDF_Krylov_static_state_max_abs",
  "actual_matched_finite_source_cases","actual_leading_recoil_source_cases",
  "source_scientific_code_bypassable_asserts","host_pre_final_stage_archives_SHA256_CRC")}))
 print("NEGATIVE_SOURCE_INPUTS_REJECTED",len(rejected))
if __name__=="__main__":verify()
