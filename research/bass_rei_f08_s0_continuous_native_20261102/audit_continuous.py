#!/usr/bin/env python3
"""Independent, Python-stdlib-only original-source coupled-evolution data audit."""
import csv,gzip,hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/"bass_rei_f08_s0_source_photon_thomson_20261101"/"source_inputs"
PARENT=ROOT.parent/"bass_rei_f08_native_hhe_firststage_20261101"/"original_rei_rust"
CHECKPOINT=ROOT.parent/"bass_rei_f08_s0_remap_support_20261101"/"source_inputs"
EV_K=1.380649e-16/1.602176634e-12
CHI=(13.598434599702,24.587389011,54.41776)
HE=.083
DT=625000000.
RATE=5e-15

def sha(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()

def rows(path):
 with gzip.open(path,"rt",newline="") as f:return list(csv.DictReader(f))

def load_original(label):
 return rows(SOURCE/(label+".csv.gz"))

def original_source_locks():
 numbers=[]
 for folder,filename,expected in (
  (SOURCE,"ORIGIN_SHA256SUMS.txt",12),
  (PARENT,"original_source_sha256.txt",51),
  (CHECKPOINT,"LOCKED_CHECKPOINT_SHA256SUMS.txt",4)):
  result=(folder/filename).read_text().splitlines()
  assert len(result)==expected
  for line in result:
   h,n=line.split(maxsplit=1)
   assert sha(folder/n)==h,(filename,n)
  numbers.append(expected)
 return numbers

def gas_total(r):
 x,y,z=(float(r[p]) for p in ("xHII","xHeII","xHeIII"))
 return float(r["w_ev_per_H"])+CHI[0]*x+HE*(CHI[1]*y+(CHI[1]+CHI[2])*z)+float(r["escape_ev_per_H"])

def audit(result_dir=ROOT/"results",check_prefix=True):
 result_dir=Path(result_dir)
 source_counts=original_source_locks()
 m=json.loads((result_dir/"RESULT.json").read_text())
 assert m["original_rei_F08_pair"]=="0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8"
 assert m["parent_head"]=="4984b42a9ed4025e4b3f20a3a61355a448e522ab"
 assert not m["owner_full_F08_RK_MPRK_interval_root"]=="PASS"
 trajectories=rows(result_dir/m["trajectory_file"])
 paired=rows(result_dir/m["comparison_file"])
 N=m["steps_per_model"]
 assert len(trajectories)==4*N and len(paired)==2*N
 assert len({(r["branch"],r["model"],r["step"]) for r in trajectories})==4*N
 assert len({(r["branch"],r["step"]) for r in paired})==2*N
 owner={lab:load_original(lab) for lab in ("S0_BI","S0_FLRW")}
 original_npart=1+HE+.9+HE*(.3+2*.6)
 w0=1.5*EV_K*50000*original_npart
 init_gas=w0+CHI[0]*.9+HE*(CHI[1]*.3+(CHI[1]+CHI[2])*.6)
 total_initial=init_gas+.05*13.7
 bounds={"native_root":0.,"global_number":0.,"global_energy_ev_H":0.,"HII_event":0.,"temp_K":0.,"original_reference":0.}
 pref={}
 for lab in owner:
  for model in ("CHARACTERISTIC","ORIGINAL_HAT"):
   collection=sorted((r for r in trajectories if r["branch"]==lab and r["model"]==model),key=lambda r:int(r["step"]))
   assert len(collection)==N
   previous=.9
   for i,r in enumerate(collection):
    step=i+1;t=step*DT
    assert int(r["step"])==step and float(r["proper_t_s"])==t
    xf=float(r["xHII"]);x2=float(r["xHeII"]);x3=float(r["xHeIII"])
    assert 0<xf<1 and 0<x2<1 and 0<x3<1 and x2+x3<1
    T=float(r["T_K"]);w=float(r["w_ev_per_H"])
    assert 30000<=T<=110000 and w>0
    T_re=2*w/(3*EV_K*(1+HE+xf+HE*(x2+2*x3)))
    bounds["temp_K"]=max(bounds["temp_K"],abs(T-T_re))
    src=float(r["source_cumulative_per_H"])
    Nobs=float(r["N_photons_per_H"])
    absorbed=float(r["HI_He_photo_absorbed_cumulative_per_H"])
    assert abs(src-RATE*t)<1e-14
    nerr=.05+src-Nobs-absorbed
    bounds["global_number"]=max(bounds["global_number"],abs(nerr),
             abs(float(r["cumulative_photon_count_residual_per_H"])))
    eend=gas_total(r)+float(r["U_photons_ev_per_H"])
    eerr=total_initial+13.7*src-float(r["redshift_work_ev_per_H"])-float(r["thermal_expansion_work_ev_per_H"])-eend
    bounds["global_energy_ev_H"]=max(bounds["global_energy_ev_H"],abs(eerr),
         abs(float(r["cumulative_total_energy_residual_ev_per_H"])))
    hii=xf-previous-float(r["stage_HI_photo_per_H"])-float(r["stage_HI_collision_per_H"])+float(r["stage_HI_recombination_per_H"])
    bounds["HII_event"]=max(bounds["HII_event"],abs(hii))
    previous=xf
    bounds["native_root"]=max(bounds["native_root"],float(r["stage_native_residual"]))
    assert int(r["stage_native_root_iterations"])<=200
    assert Nobs>=0 and absorbed>=0 and float(r["stage_photoelectron_heat_ev_per_H"])>=0
    floor=13.7*math.exp(-max((1.01e-14,9.9e-15,1e-14) if lab=="S0_BI" else (1e-14,)*3)*t)
    assert abs(float(r["exact_photon_energy_floor_ev"])-floor)<2e-13
    if model=="CHARACTERISTIC":
     assert float(r["below_exact_support_N_per_H"])<=1e-18
    else:
     if step>=1:assert float(r["below_exact_support_N_per_H"])>0
    for field,sourcefield in (
       ("original_F08_xHII","x_HII"),("original_F08_T_K","temperature_K"),
       ("original_F08_photon_n_per_H","photon_n"),
       ("original_F08_photon_energy_ev_per_H","photon_u_ev_per_h")):
     assert math.isclose(float(r[field]),float(owner[lab][i][sourcefield]),rel_tol=2e-15,abs_tol=5e-15)
    bounds["original_reference"]=max(bounds["original_reference"],abs(float(r["xHII"])-float(r["original_F08_xHII"])))
   pref[(lab,model)]=collection
 assert bounds["global_number"]<1e-12,bounds
 assert bounds["global_energy_ev_H"]<6e-12,bounds
 assert bounds["HII_event"]<5e-13,bounds
 assert bounds["native_root"]<=1e-15,bounds
 assert bounds["temp_K"]<2e-7,bounds
 for r in paired:
  a=pref[r["branch"],"CHARACTERISTIC"][int(r["step"])-1]
  b=pref[r["branch"],"ORIGINAL_HAT"][int(r["step"])-1]
  for key,field in (
    ("delta_xHII","xHII"),("delta_T_K","T_K"),
    ("delta_xHeII","xHeII"),("delta_xHeIII","xHeIII"),
    ("delta_photon_n_per_H","N_photons_per_H"),
    ("delta_gas_w_ev_per_H","w_ev_per_H"),
    ("delta_ionizing_events_step_per_H","stage_HI_photo_per_H")):
   assert math.isclose(float(r[key]),float(a[field])-float(b[field]),rel_tol=1e-12,abs_tol=1e-14),(key,r["branch"],r["step"])
 prefix_summary={"ran":False,"rows":0}
 prefix=ROOT/"results_prefix64"/"RESULT.json"
 if check_prefix and prefix.is_file() and N>=64:
  small=json.loads(prefix.read_text())
  ap=rows(prefix.parent/small["trajectory_file"])
  grouped={(r["branch"],r["model"],r["step"]):r for r in trajectories if int(r["step"])<=64}
  assert len(ap)==256
  for r in ap:
   matched=grouped[r["branch"],r["model"],r["step"]]
   for k in r:
    if k in ("branch","model","step"):assert r[k]==matched[k]
    else:
     x,y=float(r[k]),float(matched[k])
     if "residual" in k:
      assert abs(x)<1e-12 and abs(y)<1e-12
     else:assert math.isclose(x,y,rel_tol=2e-12,abs_tol=2e-14),(k,x,y)
  prefix_summary={"ran":True,"rows":len(ap),"status":"PREFIX64_NUMERIC_PARITY_PASS"}
 result={"schema":"BASS_REI_F08_CONTINUOUS_NATIVE_HHE_ADVERSARIAL_READBACK_V1",
 "claimed_science":"REAL_CONTINUOUS_SOURCE_PRESCRIPTION_MATCHED_COUPLED_HHE_NOT_ORIGINAL_INTERVAL_OWNER",
 "test_status":"PASS_SCOPED",
 "original_sha_counts":source_counts,
 "physics_rows":len(trajectories),"paired_rows":len(paired),
 "max_residual":bounds,"prefix":prefix_summary,
 "original_owner":"F08_HOLD","REI_CENTRAL":"28/88_REPORTED",
 "BASS_UPPER":"9/15_SCOPED_SOURCE_MAPPED","canonical_delta":0,
 "specific_research_limit":"SOURCE_PRESCRIPTION_AND_NATIVE_STAGE_EQUAL_NOT_ORIGINAL_INTERVAL_BUNDLES",
 "native_subagent":"NOT_RUN",
 "blind_referee_other_author":"NOT_RUN"}
 (result_dir/"AUDIT.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
 print("CONTINUOUS_NATIVE_S0_STDLIB_HOSTILE_AUDIT_PASS",json.dumps(result,sort_keys=True))
 return result
if __name__=="__main__":
 import argparse
 ap=argparse.ArgumentParser()
 ap.add_argument("--out",type=Path,default=ROOT/"results")
 ap.add_argument("--no-prefix",action="store_true")
 a=ap.parse_args()
 audit(a.out,not a.no_prefix)
