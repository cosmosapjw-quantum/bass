#!/usr/bin/env python3
"""Actual continuous REI-F08 S0 source-born photons + unchanged native Rust H/He stages.

Two complete cumulative radiation+H/He IVPs (Bianchi I and FLRW) on exactly
original S0 proper clock: characteristic birth-energy / original fixed-hat
control. Research-scoped, prescribed metric, H/He original microphysics.
No authoritative original paired-interval acceptance or F05/F09 production.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,io,json,math,subprocess,sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
UP=ROOT.parent
PR321=UP/"bass_rei_f08_s0_remap_support_20261101"
PR317=UP/"bass_rei_f08_s0_source_photon_thomson_20261101"
sys.path.insert(0,str(PR321))
from spectral_support import original_checkpoint,remap_once,original_redshift_g,original_birth_weights
sys.path.insert(0,str(PR317))
from s0_source_photon_thomson import source_histories,C,INITIAL_COUNT,SOURCE_RATE,BIRTH_EV,sigma_hi

DT=6.25e8
FHE=.083
KB=1.380649e-16/1.602176634e-12
CHI=(13.598434599702,24.587389011,54.41776)
SCHEMA="BASS_REI_F08_S0_CONTINUOUS_SOURCE_NATIVE_HHE_V1"
CHECKPOINTS=(1,2,4,8,16,32,64,96,128,160)
SOURCE_REI_F08_PAIR="0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8"
BASE_HEAD="4984b42a9ed4025e4b3f20a3a61355a448e522ab"

def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()

def matter_energy(x,w,escape,fhe=FHE):
 return w+CHI[0]*x[0]+fhe*(CHI[1]*x[1]+(CHI[1]+CHI[2])*x[2])+escape

def temperature(x,w):
 particles=1+FHE+x[0]+FHE*(x[1]+2*x[2])
 return 2*w/(3*KB*particles)

def init_gas():
 x=(.9,.3,.6)
 return {"x":x,"w":1.5*KB*5e4*(1+FHE+x[0]+FHE*(x[1]+2*x[2])),"escape":0.}

def source_packets(kind, q, grid, h):
 if kind=="CHARACTERISTIC":
  return [(i,BIRTH_EV,INITIAL_COUNT/len(q)) for i in range(len(q))]
 if kind=="ORIGINAL_HAT":
  n=np.zeros((len(q),len(grid)))
  n[:,12]=INITIAL_COUNT/len(q)
  return (n,np.zeros(len(q)),np.zeros(len(q)))
 raise ValueError("invalid model")

def pre_transport(kind, store, h, q, Egrid, tick):
 H=h.H
 t0=tick*DT;t1=(tick+1)*DT
 g0=original_redshift_g(q,H,t0);g1=original_redshift_g(q,H,t1)
 ratio=g1/g0
 src=SOURCE_RATE*DT
 weights=original_birth_weights(q,H,t1,g1)
 if not math.isclose(float(np.sum(weights)),1,rel_tol=2e-15):
  raise ValueError("source angle normalization")
 if kind=="CHARACTERISTIC":
  old=store
  U0=math.fsum(en*n for _,en,n in old)
  items=[(d,en*ratio[d],num) for d,en,num in old]
  Ured=math.fsum(en*n for _,en,n in items)
  items.extend((d,BIRTH_EV,float(src*weights[d])) for d in range(len(q)))
  if any(en<BIRTH_EV*math.exp(-max(H)*t1)-1.5e-12 for _,en,_ in items):
   raise ValueError("source support violation")
  return items,{"old_n":math.fsum(x[2] for x in old),
      "old_u":U0,"pre_u":Ured,"redshift":U0-Ured,
      "source_n":src,"source_u":src*BIRTH_EV,"new_n":math.fsum(x[2] for x in items)}
 else:
  n,gn,gu=store
  old_n=float(np.sum(n)+np.sum(gn))
  old_u=float(np.sum(n*Egrid[None,:])+np.sum(gu))
  n,gn,gu,remap_err=remap_once(n,gn,gu,ratio,Egrid)
  remapped_n=float(np.sum(n)+np.sum(gn))
  red_u=float(np.sum(n*Egrid[None,:])+np.sum(gu))
  if abs(old_n-remapped_n)>8e-14 or remap_err>3e-13:
   raise ValueError("original fixed hat source-number/energy remap error")
  n[:,12]+=src*weights
  items=[]
  for d in range(len(q)):
   for k,e in enumerate(Egrid):
    if n[d,k]>0:items.append((("G",d,k),float(e),float(n[d,k])))
   if gn[d]>0:
    e=gu[d]/gn[d]
    if not 0<e<10:raise ValueError("nonphysical original guard")
    items.append((("B",d,-1),float(e),float(gn[d])))
  return items,{"old_n":old_n,"old_u":old_u,"pre_u":red_u,"redshift":old_u-red_u,
      "source_n":src,"source_u":src*BIRTH_EV,
      "new_n":math.fsum(x[2] for x in items),"n":n,"gn":gn,"gu":gu}

def native_one(exe,inp,out,stage,items):
 nh=stage["nh"];gas=stage["gas"];mean=stage["Hmean"];t0=stage["t0"]
 with inp.open("w") as f:
  f.write("S|"+"|".join(format(v,".17g") for v in
      (nh,FHE,mean,DT,*gas["x"],gas["w"],gas["escape"],t0))+"\n")
  for _,energy,number in items:
   if not (number>0 and math.isfinite(energy*number)):
    raise ValueError("invalid input native source packet")
   f.write("P|"+format(energy,".17g")+"|"+format(number,".17g")+"\n")
 p=subprocess.run([str(exe),str(inp),str(out)],capture_output=True,text=True)
 if p.returncode:
  raise RuntimeError("native Rust stage "+p.stderr[-2000:])
 with out.open() as f:
  s=f.readline().strip().split("|")
  if s[0]!="S" or len(s)!=21:raise ValueError("native output stage schema")
  values=list(map(float,s[1:]))
  packet_nums=[]
  for line in f:
   a=line.strip().split("|")
   if a[0]!="P" or len(a)!=2:raise ValueError("native surviving packet schema")
   packet_nums.append(float(a[1]))
 if len(packet_nums)!=len(items):raise ValueError("original native photon index mismatch")
 # stage outputs 20 numbers: state x3,w,escape,temp,n1,iterations,residual,
 # photonres,energyres, photo(HI,HeI,HeII),heat,thermalwork, collisionHI,recombHI,comp,absorbedN
 x=tuple(values[:3]);w,escape,temp,n1=values[3:7]
 iterations=int(values[7]);residual=values[8]
 number_res,energy_res=values[9:11]
 photo=(values[11],values[12],values[13])
 heat,thermal,coll,recomb,comp,abs_events=values[14:20]
 if iterations>200 or residual>1e-15 or residual<0:raise ValueError("native original stage tolerance violation")
 if abs(number_res)>8e-13 or abs(energy_res)>8e-13:raise ValueError("native ledger failure")
 if abs(sum(photo)-abs_events)>6e-13:raise ValueError("original photoevent mismatch")
 if abs((x[0]-gas["x"][0])-photo[0]-coll+recomb)>6e-13:raise ValueError("original HII event identity")
 if not(0<=x[0]<=1 and 0<=x[1]<=1 and 0<=x[2]<=1 and x[1]+x[2]<=1):
  raise ValueError("native helium bound")
 if not math.isclose(temperature(x,w),temp,rel_tol=1e-12):raise ValueError("thermal gas temperature")
 if not all(n>=0 for n in packet_nums):raise ValueError("native photon underflow")
 return {"gas":{"x":x,"w":w,"escape":escape},"temp":temp,"n1":n1,
         "iterations":iterations,"residual":residual,"number_res":number_res,
         "energy_res":energy_res,"photo":photo,"heat":heat,"thermal":thermal,
         "collisionHI":coll,"recombHI":recomb,"comp":comp,
         "abs_events":abs_events,"survived":packet_nums}

def transfer_after(kind,pre,result,items,Egrid):
 if kind=="CHARACTERISTIC":
  return [(key,E,N) for (key,E,_),N in zip(items,result["survived"]) if N>0]
 n=np.zeros_like(pre["n"]);gn=np.zeros_like(pre["gn"]);gu=np.zeros_like(pre["gu"])
 for (key,E,_),N in zip(items,result["survived"]):
  if key[0]=="G":
   _,d,k=key;n[d,k]=N
  else:
   _,d,_=key;gn[d]=N;gu[d]=N*E
 return n,gn,gu

def write_gzip(path,rows):
 with path.open("wb") as file:
  with gzip.GzipFile(fileobj=file,mode="wb",filename="",mtime=0,compresslevel=6) as gz:
   with io.TextIOWrapper(gz,newline="",encoding="utf8") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]))
    w.writeheader();w.writerows(rows)
 return sha(path)

def evolve(label,kind,steps,exe,inputs,ref):
 h=ref["h"]
 q=ref["owner"]["qhat"]
 Egrid=ref["owner"]["energies"]
 store=source_packets(kind,q,Egrid,h)
 gas=init_gas()
 total_abs=0.;total_thermal=0.;total_red=0.;total_source=INITIAL_COUNT*0
 initial_total=matter_energy(gas["x"],gas["w"],gas["escape"])+INITIAL_COUNT*BIRTH_EV
 rows=[]
 for i in range(steps):
  pre_items,transport=pre_transport(kind,store,h,q,Egrid,i)
  t=(i+1)*DT
  nh=1e-4*math.exp(-sum(h.H)*t)
  result=native_one(exe,inputs/"s0_in.txt",inputs/"s0_out.txt",
      {"nh":nh,"gas":gas,"Hmean":sum(h.H)/3,"t0":i*DT},pre_items)
  gas=result["gas"]
  store=transfer_after(kind,transport,result,pre_items,Egrid)
  total_abs+=result["abs_events"]
  total_red+=transport["redshift"]
  total_thermal+=result["thermal"]
  total_source+=transport["source_n"]
  n_after=math.fsum(p[2] for p in store) if kind=="CHARACTERISTIC" else float(np.sum(store[0])+np.sum(store[1]))
  u_after=math.fsum(p[1]*p[2] for p in store) if kind=="CHARACTERISTIC" else float(np.sum(store[0]*Egrid[None,:])+np.sum(store[2]))
  count_res=INITIAL_COUNT+total_source-total_abs-n_after
  U_now=matter_energy(gas["x"],gas["w"],gas["escape"])+u_after
  energy_res=initial_total+total_source*BIRTH_EV-total_red-total_thermal-U_now
  floor=BIRTH_EV*math.exp(-max(h.H)*t)
  under=math.fsum(n for _,E,n in store if E<floor-2e-12) if kind=="CHARACTERISTIC" else float(np.sum(store[0][:,Egrid<floor])+np.sum(store[1]))
  xh,h2,h3=gas["x"]
  src=h.original[i]
  r={
   "branch":label,"model":kind,"step":i+1,"proper_t_s":t,"source_packets":len(pre_items),
   "xHII":xh,"xHeII":h2,"xHeIII":h3,"T_K":temperature(gas["x"],gas["w"]),"w_ev_per_H":gas["w"],
   "escape_ev_per_H":gas["escape"],"N_photons_per_H":n_after,"U_photons_ev_per_H":u_after,
   "source_cumulative_per_H":total_source,"HI_He_photo_absorbed_cumulative_per_H":total_abs,
   "redshift_work_ev_per_H":total_red,"thermal_expansion_work_ev_per_H":total_thermal,
   "stage_HI_photo_per_H":result["photo"][0],"stage_HeI_photo_per_H":result["photo"][1],
   "stage_HeII_photo_per_H":result["photo"][2],
   "stage_photoelectron_heat_ev_per_H":result["heat"],
   "stage_HI_collision_per_H":result["collisionHI"],
   "stage_HI_recombination_per_H":result["recombHI"],
   "stage_native_root_iterations":result["iterations"],
   "stage_native_residual":result["residual"],"stage_energy_residual_ev_per_H":result["energy_res"],
   "stage_photon_count_residual_per_H":result["number_res"],
   "cumulative_photon_count_residual_per_H":count_res,
   "cumulative_total_energy_residual_ev_per_H":energy_res,
   "exact_photon_energy_floor_ev":floor,"below_exact_support_N_per_H":under,
   "original_F08_xHII":float(src["x_HII"]),
   "original_F08_T_K":float(src["temperature_K"]),
   "original_F08_photon_n_per_H":float(src["photon_n"]),
   "original_F08_photon_energy_ev_per_H":float(src["photon_u_ev_per_h"]),
   "original_F08_absorbed_n_per_H":float(src["absorbed_n"]),
   "original_F08_gamma_HI_s_inv":float(src["gamma_HI_per_s"]),
  }
  if (abs(count_res)>2e-12 or abs(energy_res)>6e-12 or
      under>1e-18 and kind=="CHARACTERISTIC"):
   raise ValueError(f"GLOBAL_SOURCE_LEDGER_FAIL: {label} {kind} {i+1} {count_res} {energy_res} {under}")
  if i in (0,3,7,15,31,63,95,127,159):
   print("NATIVE_S0_CONTINUOUS",label,kind,i+1,
     "xHII",format(xh,".14g"),"T",format(r["T_K"],".14g"),
     "N",format(n_after,".14g"),"dHx_original",format(xh-r["original_F08_xHII"],".7g"),flush=True)
  rows.append(r)
 return rows

def solve(steps,out,rust_exe):
 if steps<2 or steps>160 or not Path(rust_exe).exists():
  raise ValueError("scoped S0 research original interval 2..160 or compiled native executable missing")
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 h=source_histories()
 refs={b:{"h":h[b],"owner":original_checkpoint(b)} for b in ("S0_BI","S0_FLRW")}
 rows=[]
 for b in ("S0_BI","S0_FLRW"):
  for mode in ("CHARACTERISTIC","ORIGINAL_HAT"):
   rows+=evolve(b,mode,steps,rust_exe,out,refs[b])
 summaries=[]
 keys={(x["branch"],x["step"]) for x in rows}
 for b,t in sorted(keys):
  cases={x["model"]:x for x in rows if x["branch"]==b and x["step"]==t}
  x,y=cases["CHARACTERISTIC"],cases["ORIGINAL_HAT"]
  summaries.append({"branch":b,"step":t,"t_proper_s":x["proper_t_s"],
   "delta_xHII":x["xHII"]-y["xHII"],"delta_xHeII":x["xHeII"]-y["xHeII"],
   "delta_xHeIII":x["xHeIII"]-y["xHeIII"],"delta_T_K":x["T_K"]-y["T_K"],
   "delta_gas_w_ev_per_H":x["w_ev_per_H"]-y["w_ev_per_H"],
   "delta_photon_n_per_H":x["N_photons_per_H"]-y["N_photons_per_H"],
   "delta_thermal_work_ev_per_H":x["thermal_expansion_work_ev_per_H"]-y["thermal_expansion_work_ev_per_H"],
   "delta_ionizing_events_step_per_H":x["stage_HI_photo_per_H"]-y["stage_HI_photo_per_H"],
   "original_source_xHII":x["original_F08_xHII"],
   "characteristic_vs_original_xHII":x["xHII"]-x["original_F08_xHII"],
   "fixed_hat_vs_original_xHII":y["xHII"]-x["original_F08_xHII"],
   "characteristic_vs_original_T_K":x["T_K"]-x["original_F08_T_K"],
   "fixed_hat_vs_original_T_K":y["T_K"]-x["original_F08_T_K"]
  })
 a=out/"SOURCE_LOCKED_REI_S0_CONTINUOUS_NATIVE_HHE_TRAJECTORY.csv.gz"
 z=out/"CHARACTERISTIC_VS_HAT_CONTINUOUS_MATERIAL_RESPONSE.csv.gz"
 ah=write_gzip(a,rows);zh=write_gzip(z,summaries)
 manifest={"schema":SCHEMA,"parent_bass_pr":326,"parent_head":BASE_HEAD,
 "original_rei_F08_pair":SOURCE_REI_F08_PAIR,
 "source_hhe":"ORIGINAL_F08_S0_ONLY_INITIAL_STATE_THEN_SELF_EVOLVED_NATIVE_RUST",
 "source_photon":"13.7eV_ORIGINAL_S0_INITIAL_AND_PER_STEP_EMISSION",
 "physics":"EXACT_BIANCHI_CHARACTERISTIC_VS_ORIGINAL_HAT_WITH_REI_NATIVE_COUPLED_PRIMARY_AT_EACH_STEP",
 "sky_directed_128_q":True,"original_reference_hhe_material_after_first_step":False,
 "steps_per_model":steps,"actual_original_native_gas_chemistry_steps":len(rows),
 "physical_trajectory_rows":len(rows),"physical_comparison_rows":len(summaries),
 "trajectory_file":a.name,"comparison_file":z.name,
 "trajectory_sha256":ah,"comparison_sha256":zh,
 "max_absolute_global_count_residual":max(abs(r["cumulative_photon_count_residual_per_H"]) for r in rows),
 "max_absolute_global_total_energy_residual_ev_per_H":max(abs(r["cumulative_total_energy_residual_ev_per_H"]) for r in rows),
 "max_original_native_stage_root_residual":max(r["stage_native_residual"] for r in rows),
 "milestones":[r for r in summaries if r["step"] in (1,8,16,32,64,96,128,160)],
 "owner_full_F08_RK_MPRK_interval_root":"NOT_REPLAYED",
 "source_original_51_rust_sha256":"REQUIRE_EXACT",
 "BASS_UPPER":"9/15_SCOPED_SOURCE_MAPPED",
 "REI_CENTRAL":"28/88_REPORTED","REI_WORKING":"33/88_REPORTED_NONADDITIVE",
 "REI_FAST":"4/7_REPORTED",
 "new_canonical_nodes":0,"new_complete_BASS_upper_nodes":0,
 "original_F08_scientific_admission":"HOLD","production":"HOLD","merge":False,
 "scope":"EXPLORATORY_INDEPENDENT_CONTINUOUS_REI_RUST_STAGES_PRESCRIBED_BIANCHI_S0_NO_SOURCE_OWNER_MERGE"
 }
 (out/"RESULT.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
 print("CONTINUOUS_NATIVE_F08_OUTPUT",json.dumps({
 "step_count":steps,"physical_rows":len(rows),"paired_rows":len(summaries),
 "global_n_max":manifest["max_absolute_global_count_residual"],
 "global_E_max":manifest["max_absolute_global_total_energy_residual_ev_per_H"],
 "trajectory_sha256":ah,"final_BI":next((r for r in summaries if r["branch"]=="S0_BI" and r["step"]==steps),None)
 },sort_keys=True))
 return manifest
if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--steps",type=int,default=64)
 ap.add_argument("--out",type=Path,default=ROOT/"results")
 ap.add_argument("--rust",type=Path,required=True)
 a=ap.parse_args()
 solve(a.steps,a.out,a.rust)
