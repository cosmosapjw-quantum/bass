#!/usr/bin/env python3
"""Independent stdlib hostile audit of the BASS source-locked native output."""
import argparse,csv,gzip,json,math,copy
from pathlib import Path
D=Path(__file__).resolve().parent
P=D.parent/"bass_rei_f08_s0_continuous_native_20261102/results/SOURCE_LOCKED_REI_S0_CONTINUOUS_NATIVE_HHE_TRAJECTORY.csv.gz"
DT=625000000.0;EB=13.7
def ensure(x,msg):
 if not x:raise ValueError(msg)
def rows(p):
 with p.open(newline="") as f:return list(csv.DictReader(f))
def audit(dir,mutated=None):
 data=json.loads((dir/"RESULT.json").read_text())
 source=rows(dir/"CHARACTERISTIC_INTERVAL_TRAJECTORY.csv")
 if mutated is not None:
  source=copy.deepcopy(source)
  mutated(source)
 with gzip.open(P,"rt") as f:
  reference={(r["branch"],r["step"]):r for r in csv.DictReader(f) if r["model"]=="CHARACTERISTIC"}
 ensure(data["source_pair_sha256"]=="0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8","SOURCE_ID")
 accepted=[r for r in source if r["status"]=="PASS"]
 for g in ("S0_BI","S0_FLRW"):
  sub=[r for r in source if r["branch"]==g]
  ensure(len(sub)==data["results"][0 if g=="S0_BI" else 1]["requested"],"STEPS_COUNT")
  ensure(all(r["status"]=="PASS" for r in sub),"ROOT_BLOCKED")
  hmax=1.01e-14 if g=="S0_BI" else 1e-14
  for i,r in enumerate(sub,1):
   ensure(int(r["step"])==i and float(r["t_s"])==i*DT,"CLOCK")
   q=float(r["root_q"]);ensure(0<=q<1.,"ROOT_Q")
   n=float(r["N_photons_per_H"])
   ensure(float(r["N_box_lo"])<=n<=float(r["N_box_hi"]),"TOTAL_N_BOX")
   floor=EB*math.exp(-hmax*i*DT)
   ensure(abs(float(r["physical_min_energy_ev"])-floor)<3e-12,"SUPPORT_FLOOR")
   ensure(float(r["represented_min_energy_ev"])>=floor-3e-12,"PHYSICAL_SUPPORT")
   ensure(float(r["below_physical_support_N_per_H"])==0.,"FORBIDDEN_PHOTON_MASS")
   ensure(abs(float(r["point_number_residual"]))<2e-12,"NUMBER_LEDGER")
   ensure(abs(float(r["point_energy_residual_ev_per_H"]))<6e-12,"ENERGY_LEDGER")
   for x in ("xHII","xHeII","xHeIII"):ensure(0<=float(r[x])<=1,"SPECIES")
   ensure(float(r["xHeII"])+float(r["xHeIII"])<=1,"HELIUM")
   ensure(35000<float(r["T_K"])<60000,"THERMAL_DOMAIN")
   old=reference[(g,str(i))]
   for key,alias,limit in [("xHII","xHII",2e-12),("xHeII","xHeII",2e-12),
                           ("xHeIII","xHeIII",2e-12),("T_K","T_K",5e-8),
                           ("N_photons_per_H","N_photons_per_H",2e-12)]:
    ensure(abs(float(r[key])-float(old[alias]))<limit,"ORIGINAL_PR328_POINT_PARITY_"+key)
 with gzip.open(dir/"CHARACTERISTIC_PACKET_SAMPLES.csv.gz","rt") as f:
  packet=list(csv.DictReader(f))
 ensure(len(packet)>0,"NO_PHYSICAL_PACKET_RECORDS")
 for r in packet:
  n=float(r["N_per_H"]);e=float(r["E_ev"])
  ensure(float(r["N_interval_lo"])<=n<=float(r["N_interval_hi"]),"PACKET_N_ROOT")
  ensure(float(r["E_analytic_lo"])<=e<=float(r["E_analytic_hi"]),"PACKET_E_SUPPORT")
  ensure(0<=float(r["birth_time_s"])<=int(r["step"])*DT,"BIRTH_TIME_CAUSAL")
  q=[float(r[f"q_{d}"]) for d in "xyz"]
  ensure(abs(sum(x*x for x in q)-1)<1e-12,"ORIGINAL_Q_UNIT")
  ensure(e>=EB*math.exp(-(1.01e-14 if r["branch"]=="S0_BI" else 1e-14)*int(r["step"])*DT)-3e-12,"PACKET_PHYSICAL_FLOOR")
 return {"status":"SCOPED_PASS","gas_and_photon_consecutive_steps":len(accepted),
         "packet_witnesses":len(packet),"geometry_count":2,
         "max_root_q":max(float(r["root_q"]) for r in accepted),
         "max_gas_width":max(float(r["gas_width_max"]) for r in accepted),
         "max_number_box_width":max(float(r["N_box_hi"])-float(r["N_box_lo"]) for r in accepted),
         "max_abs_point_energy_residual":max(abs(float(r["point_energy_residual_ev_per_H"])) for r in accepted),
         "global_energy_q_photoionization_interval":"NOT_CERTIFIED",
         "original_owner_full_14_interval_ledgers":"NOT_RUN",
         "owner_admission":"HOLD"}
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--dir",type=Path,required=True)
 ap.add_argument("--negative",action="store_true")
 a=ap.parse_args()
 out=audit(a.dir)
 if a.negative:
  negative=[("FORGED_SUPPORT",lambda x:x[0].__setitem__("below_physical_support_N_per_H","0.02")),
   ("FORGED_HII",lambda x:x[0].__setitem__("xHII","1.2")),
   ("FORGED_E",lambda x:x[0].__setitem__("point_energy_residual_ev_per_H","0.01")),
   ("FORGED_BOX",lambda x:x[0].__setitem__("N_box_lo","999.0"))]
  for name,fn in negative:
   try:audit(a.dir,fn)
   except ValueError:pass
   else:raise ValueError(name+"_WAS_ACCEPTED")
  out["negative_cases_rejected"]=len(negative)
 print(json.dumps(out,indent=2,sort_keys=True))
 (a.dir/"AUDIT.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
main()
