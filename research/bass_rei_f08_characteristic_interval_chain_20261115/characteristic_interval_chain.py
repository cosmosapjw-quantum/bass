#!/usr/bin/env python3
"""Original S0 source-born characteristic transport + native gas/photon-number box chain.

Energy box is an analytically guaranteed H_min/H_max range computed by original
Rust Interval arithmetic. Energy uncertainty is NOT passed into native gas root.
"""
import argparse,csv,gzip,json,math,subprocess,sys,hashlib
from pathlib import Path
U=Path(__file__).resolve().parent
sys.path.insert(0,str(U.parent/"bass_rei_f08_s0_continuous_native_20261102"))
import continuous_s0 as C
from spectral_support import original_checkpoint
from s0_source_photon_thomson import source_histories
DT=C.DT
POINTS={1,2,4,8,16,32,64,96,128,160}
FIELDS=["branch","step","status","error","t_s","packet_count","xHII","xHeII","xHeIII","T_K",
"gas_width_max","root_q","root_residual","N_photons_per_H","N_box_lo","N_box_hi",
"photon_U_ev_per_H","physical_min_energy_ev","represented_min_energy_ev",
"below_physical_support_N_per_H","source_N_per_H","absorbed_N_per_H",
"redshift_work_ev_per_H","thermal_work_ev_per_H","point_number_residual",
"point_energy_residual_ev_per_H","photoHI","photoHeI","photoHeII"]
PFIELDS=["branch","step","packet","direction","q_x","q_y","q_z","birth_time_s",
          "E_ev","E_analytic_lo","E_analytic_hi","N_per_H","N_interval_lo","N_interval_hi"]
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def native(exe,inp,out,pre,parents,ages,gas,gbox,H,nh,t0):
 assert len(pre)==len(parents)==len(ages)
 with inp.open("w") as f:
  f.write("S|"+"|".join(format(x,".17e") for x in
   (nh,C.FHE,sum(H)/3,DT,*gas["x"],gas["w"],gas["escape"],t0))+"\n")
  f.write("H|"+format(min(H),".17e")+"|"+format(max(H),".17e")+"\n")
  for b in gbox:f.write("G|"+format(b[0],".17e")+"|"+format(b[1],".17e")+"\n")
  for (_,e,n),b,age in zip(pre,parents,ages):
   assert b[0]>=0 and b[0]<=n<=b[1] and n>0 and age>=0
   f.write("P|"+"|".join(format(x,".17e") for x in (age,e,n,*b))+"\n")
 p=subprocess.run([str(exe),str(inp),str(out)],capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stderr[-600:])
 with out.open() as f:
  head=f.readline().strip().split("|")
  if len(head)!=18 or head[0]!="S":raise ValueError("BAD_NATIVE_STAGE_HEADER")
  v=[float(x) for x in head[1:]]
  gb=[f.readline().strip().split("|") for _ in range(4)]
  packets=[f.readline().strip().split("|") for _ in pre]
  if f.readline():raise ValueError("UNEXPECTED_NATIVE_TRAILER")
 if any(x[0]!="G" or len(x)!=3 for x in gb):raise ValueError("BAD_GAS_BOX")
 if any(x[0]!="P" or len(x)!=6 for x in packets):raise ValueError("BAD_PACKET_BOX")
 gasbox=[tuple(map(float,x[1:])) for x in gb]
 photonbox=[tuple(map(float,x[2:4])) for x in packets]
 energybox=[tuple(map(float,x[4:6])) for x in packets]
 num=[float(x[1]) for x in packets]
 fractions=tuple(v[:3]);w,escape,temp,n,iterations,residual,thermal,absorbed,hi,hei,heii,q,gw,pw=v[3:]
 if not all(a<=b<=c for (a,c),b in zip(gasbox,[*fractions,w])):raise ValueError("GAS_ROOT_EXCLUDES_POINT")
 if not all(a<=b<=c for (a,c),b in zip(photonbox,num)):raise ValueError("PHOTON_ROOT_EXCLUDES_POINT")
 if not all(a<=b<=c for (a,c),(_,b,_) in zip(energybox,pre)):raise ValueError("ENERGY_OUTSIDE_PHYSICAL_BOUNDS")
 if not (0<=q<1 and residual<=1e-15 and iterations<=200):raise ValueError("ROOT_GATE")
 if abs((hi+hei+heii)-absorbed)>1e-12:raise ValueError("PHOTO_EVENTS_LEDGER")
 if not math.isclose(C.temperature(fractions,w),temp,rel_tol=1e-12):raise ValueError("THERMAL_CONVERSION")
 return {"gas":{"x":fractions,"w":w,"escape":escape},"temperature":temp,"photonbox":photonbox,
    "energybox":energybox,"gasbox":gasbox,"num":num,"q":q,"residual":residual,
    "thermal":thermal,"absorbed":absorbed,"photo":[hi,hei,heii],"gaswidth":gw}
def evolve(label,steps,exe,dest,writer,pwriter):
 h=source_histories()[label];source=original_checkpoint(label)
 q=source["qhat"];H=h.H
 store=C.source_packets("CHARACTERISTIC",q,source["energies"],h)
 births=[0.0]*len(store)
 nboxes=[(n,n) for _,_,n in store]
 gas=C.init_gas();gbox=[(x,x) for x in (*gas["x"],gas["w"])]
 initial=C.matter_energy(gas["x"],gas["w"],gas["escape"])+C.INITIAL_COUNT*C.BIRTH_EV
 cumabs=cumsrc=cumred=cumtherm=0.0
 count=0;failure=None
 for i in range(steps):
  t=(i+1)*DT
  pre,transport=C.pre_transport("CHARACTERISTIC",store,h,q,source["energies"],i)
  ages=[t-tb for tb in births]+[0.0]*len(q)
  assert len(pre)==len(ages)==len(nboxes)+len(q)
  birthboxes=[(max(0.0,math.nextafter(n,-math.inf)),math.nextafter(n,math.inf))
               for _,_,n in pre[len(nboxes):]]
  try:
   out=native(exe,dest/"stage_in.txt",dest/"stage_out.txt",pre,nboxes+birthboxes,
              ages,gas,gbox,H,1e-4*math.exp(-sum(H)*t),i*DT)
  except (RuntimeError,ValueError,AssertionError) as ex:
   failure={"step":i+1,"kind":"NATIVE_INTERVAL_PROPAGATION","error":str(ex)}
   writer.writerow({"branch":label,"step":i+1,"status":"BLOCKED","error":str(ex)})
   print("BLOCKED",label,i+1,str(ex),flush=True)
   break
  gas=out["gas"];gbox=out["gasbox"]
  store=[(d,e,n) for (d,e,_),n in zip(pre,out["num"])]
  births=[t-a for a in ages]
  nboxes=out["photonbox"]
  if any(n<=0 and b[1]>0 for (_,_,n),b in zip(store,nboxes)):
   failure={"step":i+1,"kind":"ZERO_POINT_NONZERO_BOX"};break
  if any(n<=0 for _,_,n in store):
   filtered=[(p,b,tb) for p,b,tb in zip(store,nboxes,births) if p[2]>0]
   store=[p for p,_,_ in filtered];nboxes=[b for _,b,_ in filtered]
   births=[tb for _,_,tb in filtered]
  cumabs+=out["absorbed"];cumsrc+=transport["source_n"]
  cumred+=transport["redshift"];cumtherm+=out["thermal"]
  N=math.fsum(n for _,_,n in store);E=math.fsum(e*n for _,e,n in store)
  nr=C.INITIAL_COUNT+cumsrc-cumabs-N
  er=initial+cumsrc*C.BIRTH_EV-cumred-cumtherm-C.matter_energy(gas["x"],gas["w"],gas["escape"])-E
  floor=C.BIRTH_EV*math.exp(-max(H)*t)
  below=math.fsum(n for _,e,n in store if e<floor-3e-12)
  if abs(nr)>2e-12 or abs(er)>6e-12 or below>0:
   raise ValueError(f"PHYSICAL_LEDGER_OR_SUPPORT_FAIL {label} step{i+1} {nr} {er} {below}")
  if not all(0<=x<=1 for x in gas["x"]) or gas["x"][1]+gas["x"][2]>1:raise ValueError("GAS_DOMAIN")
  # Wide upper/lower independent envelope for diagnostics, not a proved exact
  # sum of box endpoints: original root packet enclosures remain authoritative.
  nl=math.nextafter(math.fsum(b[0] for b in nboxes),-math.inf)
  nu=math.nextafter(math.fsum(b[1] for b in nboxes),math.inf)
  if not (nl<=N<=nu):raise ValueError("TOTAL_NUMBER_BOX_MISSES_POINT")
  writer.writerow(dict(branch=label,step=i+1,status="PASS",error="NONE",t_s=t,
    packet_count=len(store),xHII=gas["x"][0],xHeII=gas["x"][1],xHeIII=gas["x"][2],
    T_K=out["temperature"],gas_width_max=out["gaswidth"],root_q=out["q"],
    root_residual=out["residual"],N_photons_per_H=N,N_box_lo=nl,N_box_hi=nu,
    photon_U_ev_per_H=E,physical_min_energy_ev=floor,
    represented_min_energy_ev=min(e for _,e,_ in store),
    below_physical_support_N_per_H=below,
    source_N_per_H=cumsrc,absorbed_N_per_H=cumabs,
    redshift_work_ev_per_H=cumred,thermal_work_ev_per_H=cumtherm,
    point_number_residual=nr,point_energy_residual_ev_per_H=er,
    photoHI=out["photo"][0],photoHeI=out["photo"][1],photoHeII=out["photo"][2]))
  count+=1
  if i+1 in POINTS:
   for j,((d,e,n),b,tb) in enumerate(zip(store,nboxes,births)):
    lo,hi=out["energybox"][j]
    pwriter.writerow(dict(branch=label,step=i+1,packet=j,direction=int(d),
      q_x=float(q[d][0]),q_y=float(q[d][1]),q_z=float(q[d][2]),
      birth_time_s=tb,E_ev=e,E_analytic_lo=lo,E_analytic_hi=hi,
      N_per_H=n,N_interval_lo=b[0],N_interval_hi=b[1]))
   print("ORIGINAL_ROOT_INTERVAL",label,"step",i+1,"rootq",format(out["q"],".4e"),
      "HII",format(gas["x"][0],".12g"),"T",format(out["temperature"],".12g"),
      "N",format(N,".12g"),"N_width",format(nu-nl,".4e"),
      "support_under",format(below,".3e"),flush=True)
 return dict(branch=label,complete=count,requested=steps,
             status="SCOPED_COMPLETE" if count==steps else "BLOCKED",failure=failure)
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--steps",type=int,default=8)
 ap.add_argument("--rust-exe",type=Path,required=True)
 ap.add_argument("--out",type=Path,required=True)
 a=ap.parse_args()
 if not 1<=a.steps<=160:ap.error("require 1..160")
 a.out.mkdir(parents=True,exist_ok=True)
 t=a.out/"CHARACTERISTIC_INTERVAL_TRAJECTORY.csv"
 p=a.out/"CHARACTERISTIC_PACKET_SAMPLES.csv.gz"
 with t.open("w",newline="") as f,gzip.open(p,"wt",newline="") as g:
  w=csv.DictWriter(f,fieldnames=FIELDS,lineterminator="\n");w.writeheader()
  z=csv.DictWriter(g,fieldnames=PFIELDS);z.writeheader()
  results=[evolve(x,a.steps,a.rust_exe,a.out,w,z) for x in ("S0_BI","S0_FLRW")]
 def sha(x):return hashlib.sha256(x.read_bytes()).hexdigest()
 record={"unit":"BASS_F08_CHAR_SUPPORT_ORIGINAL_ROOT_GAS_AND_NUMBER_CHAIN",
  "source_pair_sha256":C.SOURCE_REI_F08_PAIR,
  "original_root_sha256":"915d0a898100a54d04a525227e7fbeb870e321fcc14aaa91afd61352b6d4cf4b",
  "energy_birth_ev":C.BIRTH_EV,"dt_s":DT,"results":results,
  "gas_photon_number_boxes":"ORIGINAL_ROOT_CHAINED",
  "energy_bounds":"ANALYTIC_HMIN_HMAX_ORIGINAL_RUST_INTERVAL",
  "energy_uncertainty_IN_ROOT":"NOT_PROPAGATED",
  "angular_q_uncertainty_IN_ROOT":"NOT_PROPAGATED",
  "original_14_ledgers":"NOT_RUN","owner_admission":"HOLD",
  "trajectory_sha256":sha(t),"packet_samples_sha256":sha(p)}
 (a.out/"RESULT.json").write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
 print("RESULT",json.dumps(record,sort_keys=True),flush=True)
main()
