#!/usr/bin/env python3
"""Independent data-level H/He science readback; never edits original REI source."""
import csv,gzip,hashlib,io,json,math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SRC=ROOT/"original_rei_rust"
INPUT=ROOT/"inputs"
RESULT=ROOT/"results"
PARENT=ROOT.parent/"bass_rei_f08_s0_source_photon_thomson_20261101"
PR321=ROOT.parent/"bass_rei_f08_s0_remap_support_20261101"
HI_CHI=13.598434599702
FHE=.083
EV_K=8.617333262145e-5
LIGHT_CM_S=29979245800.0
TICKS=(0,800,1600,6400,15999)
BKG=("S0_BI","S0_FLRW")
SCHEMA="BASS_REI_S0_ORIGINAL_RUST_HHE_COUPLED_STAGE_FEEDBACK_V1"

def digest(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()

def load_originals():
 all_files=0
 for line in (SRC/"original_source_sha256.txt").read_text().splitlines():
  sha,p=line.split(maxsplit=1)
  if digest(SRC/p)!=sha:
   raise AssertionError("REI original Rust source byte identity changed "+p)
  all_files+=1
 assert all_files==51
 assert digest(SRC/"src/coupled_primary.rs")=="915d0a898100a54d04a525227e7fbeb870e321fcc14aaa91afd61352b6d4cf4b"
 assert digest(SRC/"src/atomic_provider.rs")=="b0b572d3940a7a1f740e09d5f43c60236ec61511e8bdbcc68e60395ec7e107d3"
 for folder,lock,n in ((PARENT/"source_inputs","ORIGIN_SHA256SUMS.txt",12),
                       (PR321/"source_inputs","LOCKED_CHECKPOINT_SHA256SUMS.txt",4)):
  lines=(folder/lock).read_text().splitlines()
  assert len(lines)==n
  for l in lines:
   v,p=l.split(maxsplit=1)
   assert digest(folder/p)==v,(folder,p)
 return all_files

def read_rows(path):
 with Path(path).open("rt",newline="") as f:return list(csv.DictReader(f))

def source_reference():
 data={}
 for label in BKG:
  with gzip.open(PARENT/"source_inputs"/(label+".csv.gz"),"rt",newline="") as f:
   rows=list(csv.DictReader(f))
  assert len(rows)==16000
  data[label]=rows
 return data

def get_case_packets():
 metadata=json.loads((INPUT/"STAGE_INPUT_PROVENANCE.json").read_text())
 assert metadata["source_parent_head"]=="c0e965ba21892346feef9ecb2389932c34f3fc82"
 assert metadata["stage_input_sha256"]==digest(INPUT/"native_stage_cases.txt")
 in_cases={}
 with (INPUT/"native_stage_cases.txt").open() as f:
  for ln in f:
   line=ln.strip()
   if not line or line.startswith("#"):continue
   p=line.split("|")
   if p[0]=="S":
    assert len(p)==15
    key=p[1]
    assert key not in in_cases
    in_cases[key]={"branch":p[2],"model":p[3],"tick":int(p[4]),
                   "t_s":float(p[5]),"dt_s":float(p[6]),
                   "nh":float(p[7]),"fHe":float(p[8]),"Hmean":float(p[9]),
                   "fractions":[float(x) for x in p[10:13]],
                   "w":float(p[13]),"escape":float(p[14]),
                   "packets":[]}
   elif p[0]=="P":
    assert len(p)==3
    in_cases[key]["packets"].append((float(p[1]),float(p[2])))
   else:raise AssertionError("Unrecognized source record "+line[:15])
 assert len(in_cases)==len(metadata["cases"])==20
 for case in metadata["cases"]:
  it=in_cases[case["id"]]
  assert it["branch"]==case["branch"] and it["model"]==case["model"]
  assert it["tick"]==case["tick"]
  assert len(it["packets"])==case["source_packet_count"]
  N=math.fsum(n for e,n in it["packets"])
  U=math.fsum(e*n for e,n in it["packets"])
  assert math.isclose(N,case["input_total_N_per_H"],rel_tol=1e-12,abs_tol=1e-15)
  assert math.isclose(U,case["input_total_U_eV_per_H"],rel_tol=1e-12,abs_tol=1e-14)
 return metadata,in_cases

def response(data,models,owner):
 return None

def audit():
 locks=load_originals()
 meta,in_cases=get_case_packets()
 native=read_rows(RESULT/"native_stage.csv")
 original=source_reference()
 cases={r["id"]:r for r in native}
 assert len(native)==len(cases)==20
 model_source={}
 max_hii=0.
 max_energy=0.
 max_number=0.
 max_same_parent=0.
 for key,r in cases.items():
  q=in_cases[key]
  tick=q["tick"]
  label=q["branch"]
  assert r["model"]==q["model"] and r["branch"]==label
  assert int(r["tick"])==tick and tick in TICKS
  packet=q["packets"]
  n0=math.fsum(n for e,n in packet)
  u0=math.fsum(e*n for e,n in packet)
  assert math.isclose(n0,float(r["N_before_per_H"]),rel_tol=6e-13,abs_tol=3e-14),(key,"n0")
  assert math.isclose(u0,float(r["U_before_eV_per_H"]),rel_tol=6e-13,abs_tol=3e-13),(key,"u0")
  assert int(r["packets"])==len(packet)
  assert 0<float(r["stage_residual"])<1e-14
  assert 0<float(r["T_after_K"])<110000.
  assert 0. <=float(r["xHeII_after"])+float(r["xHeIII_after"])<=1.+1e-12
  gamma_direct=LIGHT_CM_S*q["nh"]*math.fsum(
     n*verner_hi(e) for e,n in packet)
  assert math.isclose(gamma_direct,float(r["HI_gamma_in_s_inv"]),rel_tol=5e-12,abs_tol=1e-24),(key,"Gamma")
  N_out=float(r["N_after_per_H"])
  event=sum(float(r[z]) for z in ("HI_abs_per_H","HeI_abs_per_H","HeII_abs_per_H"))
  n_res=N_out+event-n0
  hei=float(r["dxHII"])-float(r["HI_abs_per_H"])-float(r["HI_collision_per_H"])+float(r["HI_recombination_per_H"])
  max_hii=max(max_hii,abs(hei))
  max_number=max(max_number,abs(n_res),abs(float(r["photon_count_residual"])))
  max_energy=max(max_energy,abs(float(r["energy_residual_ev_per_H"])))
  assert abs(hei)<5e-14 and abs(n_res)<2e-13
  assert abs(float(r["energy_residual_ev_per_H"]))<8e-13
  assert float(r["HI_abs_per_H"])>=0 and float(r["excess_photoheat_events_eV_per_H"])>=0
  Tgas=float(r["T_before_K"])
  T_calc=2*q["w"]/(3*EV_K*(1+q["fHe"]+q["fractions"][0]+q["fHe"]*(q["fractions"][1]+2*q["fractions"][2])))
  assert abs(T_calc-Tgas)<2e-7
  if tick>0:
   hist=original[label][tick-1]
   for value,field in zip(q["fractions"],("x_HII","x_HeII","x_HeIII")):
    assert value==float(hist[field]),(key,field)
   assert q["w"]==float(hist["w_ev_per_h"])
   assert q["escape"]==float(hist["escape_ev_per_h"])
   assert abs(Tgas-float(hist["temperature_K"]))<2e-7
  else:
   assert q["fractions"]==[.9,.3,.6]
   assert abs(Tgas-5e4)<2e-7
  bound=13.7*math.exp(-max(([1.01e-14,9.9e-15,1e-14] if label=="S0_BI" else [1e-14]*3))*((tick+1)*6.25e8))
  if q["model"]=="CHARACTERISTIC":
   assert float(r["below_physical_support_N_per_H"])<1e-18
   assert min(e for e,n in packet)>=bound-2e-12
  model_source[key]=q
  assert math.isfinite(float(r["dw_ev_per_H"]))
 pairs=[]
 for lab in BKG:
  for tick in TICKS:
   a=cases[f"{lab}_T{tick}_CHARACTERISTIC"]
   b=cases[f"{lab}_T{tick}_ORIGINAL_HAT_FROZEN_HI"]
   qa=model_source[a["id"]]
   qb=model_source[b["id"]]
   for k in ("fractions","w","escape","nh","fHe","dt_s","t_s"):
    assert qa[k]==qb[k],(lab,tick,k)
   gamma_a=float(a["HI_gamma_in_s_inv"]);gamma_b=float(b["HI_gamma_in_s_inv"])
   w_char=float(a["w_after_ev_per_H"]);w_hat=float(b["w_after_ev_per_H"])
   pc=1+FHE+float(a["xHII_after"])+FHE*(float(a["xHeII_after"])+2*float(a["xHeIII_after"]))
   ph=1+FHE+float(b["xHII_after"])+FHE*(float(b["xHeII_after"])+2*float(b["xHeIII_after"]))
   dT_energy=2*(w_char-w_hat)/(3*EV_K*pc)
   dT_particles=2*w_hat*(1/pc-1/ph)/(3*EV_K)
   dT_native=float(a["T_after_K"])-float(b["T_after_K"])
   assert abs((dT_energy+dT_particles)-dT_native)<4e-8,("NATIVE_HHE_EOS_DECOMPOSITION",lab,tick)
   obj={
    "branch":lab,"original_parent_tick":tick,"parent_t_s":qa["t_s"],
    "native_one_step_dt_s":qa["dt_s"],"original_parent_nh_cm3":qa["nh"],
    "parent_xHII":qa["fractions"][0],"parent_xHeII":qa["fractions"][1],
    "parent_xHeIII":qa["fractions"][2],
    "original_parent_T_K":float(a["T_before_K"]),
    "native_characteristic_packets":int(a["packets"]),
    "native_original_hat_packets":int(b["packets"]),
    "characteristic_input_gamma_HI_s_inv":gamma_a,
    "fixed_hat_input_gamma_HI_s_inv":gamma_b,
    "gamma_characteristic_over_hat_minus1":gamma_a/gamma_b-1,
    "HII_after_characteristic":float(a["xHII_after"]),
    "HII_after_fixed_hat":float(b["xHII_after"]),
    "delta_HII_native_coupled":float(a["xHII_after"])-float(b["xHII_after"]),
    "delta_HeII_native_coupled":float(a["xHeII_after"])-float(b["xHeII_after"]),
    "delta_HeIII_native_coupled":float(a["xHeIII_after"])-float(b["xHeIII_after"]),
    "native_characteristic_T_after_K":float(a["T_after_K"]),
    "native_fixed_hat_T_after_K":float(b["T_after_K"]),
    "delta_T_after_K":dT_native,
    "delta_T_kinetic_energy_term_K":dT_energy,
    "delta_T_particle_number_term_K":dT_particles,
    "delta_particle_count_per_H":pc-ph,
    "delta_kinetic_energy_ev_per_H":float(a["w_after_ev_per_H"])-float(b["w_after_ev_per_H"]),
    "delta_HI_photoevents_per_H":float(a["HI_abs_per_H"])-float(b["HI_abs_per_H"]),
    "delta_photoelectron_heat_ev_per_H":float(a["excess_photoheat_events_eV_per_H"])-float(b["excess_photoheat_events_eV_per_H"]),
    "delta_total_output_photons_per_H":float(a["N_after_per_H"])-float(b["N_after_per_H"]),
    "characteristic_below_exact_source_support_N_per_H":float(a["below_physical_support_N_per_H"]),
    "fixed_hat_below_exact_source_support_N_per_H":float(b["below_physical_support_N_per_H"]),
    "native_characteristic_residual":float(a["stage_residual"]),
    "native_fixed_hat_residual":float(b["stage_residual"]),
    "original_F08_next_xHII":float(original[lab][tick]["x_HII"]),
    "source_comment":"ONE_NATIVE_RUST_COUPLED_HHE_STAGE_AFTER_FROZEN_PRIOR_HISTORY"
   }
   pairs.append(obj)
 assert len(pairs)==10
 assert next(x for x in pairs if x["branch"]=="S0_BI" and x["original_parent_tick"]==800)["delta_HII_native_coupled"]>5e-6
 assert next(x for x in pairs if x["branch"]=="S0_BI" and x["original_parent_tick"]==1600)["delta_HII_native_coupled"]<0
 conv=[]
 hp=RESULT/"native_high_stage.csv"
 if hp.exists():
  high=read_rows(hp)
  highmap={(x["branch"],int(x["tick"]),x["model"]):x for x in high}
  assert len(highmap)==12
  for p in pairs:
   key=(p["branch"],p["original_parent_tick"])
   if (key[0],key[1],"CHARACTERISTIC") not in highmap:continue
   item=highmap[(key[0],key[1],"CHARACTERISTIC")]
   a=cases[f"{key[0]}_T{key[1]}_CHARACTERISTIC"]
   w=highmap[(key[0],key[1],"ORIGINAL_HAT_FROZEN_HI")]
   delta_high=float(item["xHII_after"])-float(w["xHII_after"])
   conv.append({"branch":key[0],"parent_tick":key[1],
     "baseline_birth_gl":128,"baseline_HI_simpson":24,
     "high_birth_gl":512,"high_HI_simpson":48,
     "baseline_gamma_s_inv":float(a["HI_gamma_in_s_inv"]),
     "high_gamma_s_inv":float(item["HI_gamma_in_s_inv"]),
     "gamma_relative_baseline_vs_high":float(a["HI_gamma_in_s_inv"])/float(item["HI_gamma_in_s_inv"])-1,
     "baseline_delta_HII":p["delta_HII_native_coupled"],
     "high_delta_HII":delta_high,
     "delta_HII_high_minus_baseline":delta_high-p["delta_HII_native_coupled"],
     "baseline_delta_T_K":p["delta_T_after_K"],
     "high_delta_T_K":float(item["T_after_K"])-float(w["T_after_K"]),
     "native_high_residual":float(item["stage_residual"])})
 assert len(conv)==6
 (RESULT/"SOURCE_QUADRATURE_SENSITIVITY.json").write_text(json.dumps({"source_models":2,"scoped_numerical_only":True,"rows":conv},indent=2,sort_keys=True)+"\n")
 out=RESULT/"F08_S0_ORIGINAL_RUST_HHE_COUPLED_FEEDBACK.csv.gz"
 with out.open("wb") as f:
  with gzip.GzipFile(fileobj=f,filename="",mtime=0,mode="wb",compresslevel=6) as g:
   with io.TextIOWrapper(g,encoding="utf-8",newline="") as text:
    writer=csv.DictWriter(text,fieldnames=list(pairs[0]))
    writer.writeheader();writer.writerows(pairs)
 report={
  "schema":SCHEMA,"source_parent_sha":"c0e965ba21892346feef9ecb2389932c34f3fc82",
  "original_Rust_sha51":"PASS","original_F08_source_sha12":"PASS","original_photon_checkpoint_sha4":"PASS",
  "original_native_Rust_coupled_HHe_function":"primary_stage_step_conservative",
  "original_native_Rust_control":{"max_iterations":200,"residual_tolerance":1e-15},
  "stage_input_sha256":meta["stage_input_sha256"],"stage_input_file":meta["stage_input_file"],
  "original_compiled_Rust_wrapper":"BASS_ONLY_NO_ORIGINAL_SOURCE_MUTATION",
  "native_coupled_case_count":len(native),"paired_physics_rows":len(pairs),
  "baseline_source_packets":sum(len(q["packets"]) for q in in_cases.values()),
  "independent_count_hii_and_energy_max":{"HII_identity":max_hii,"photon_count":max_number,"total_energy":max_energy},
  "physical_response_file":out.name,"physical_response_sha256":digest(out),
  "native_stage_csv_sha256":digest(RESULT/"native_stage.csv"),
  "source_sensitivity_count":len(conv),
  "source_condition":"F08_S0_13.7EV_PREVIOUS_FROZEN_HHE_CURRENT_NATIVE_COUPLED_STEP",
  "state_claim":"NATIVE_OLD_RUST_HHE_COUPLED_ONE_STEP_EACH_PARENT_NOT_FULL_NEW_CONTINUOUS_IVP",
  "native_code_status":"ORIGINAL_SOURCE_BYTE_LOCKED_51_PLUS_SCOPED_WRAPPER",
  "original_F05_tick161":"NOT_ACCEPTED","original_F08_admission":"HOLD",
  "original_F09":"BLOCKED_PROVIDER_DOMAIN",
  "REI_CENTRAL":"28/88_REPORTED","REI_WORKING":"33/88_REPORTED_NONADDITIVE",
  "REI_FAST":"4/7_REPORTED","BASS_UPPER":"9/15_SCOPED_SOURCE_MAPPED",
  "canonical_delta":0,"full_bass_upper_delta":0,"production":"HOLD",
  "source_results":pairs
 }
 (RESULT/"RESULT.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 print("NATIVE_HHE_STAGE_HOSTILE_AUDIT_PASS",json.dumps({"native":len(native),"paired_rows":len(pairs),
  "source_packets":report["baseline_source_packets"],"max_residuals":report["independent_count_hii_and_energy_max"],
  "response_sha256":report["physical_response_sha256"],"sensitivity":len(conv)},sort_keys=True))
 return report

def verner_hi(E):
 if E<0 or E>50000 or not math.isfinite(E):raise ValueError("source cross section domain")
 if E<13.60:return 0.
 x=E/.4298
 return 5.475e4*(x-1)**2*x**(2.963/2-5.5)*(1+math.sqrt(x/32.88))**(-2.963)*1e-18
if __name__=="__main__":audit()
