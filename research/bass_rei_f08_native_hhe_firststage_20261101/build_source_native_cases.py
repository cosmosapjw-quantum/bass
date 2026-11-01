#!/usr/bin/env python3
"""Source-authentic REI F08 S0 photon inputs for untouched native Rust coupled H/He.

Compare original fixed-node hat and exact-energy birth-characteristics at a common
original F08 H/He parent snapshot, both entered into the same actual Rust solver.
Photon histories to the parent are FROZEN H I conditional, not self-consistent IVP.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent/"bass_rei_f08_s0_source_photon_thomson_20261101"
PR321=ROOT.parent/"bass_rei_f08_s0_remap_support_20261101"
PR323=ROOT.parent/"bass_rei_f08_s0_characteristic_photoheating_20261101"
sys.path.insert(0,str(PR323))
from source_exact_photoheat import verner,kgrav,interpolate_original,ION
sys.path.insert(0,str(PR321))
from spectral_support import original_checkpoint,remap_once,original_redshift_g,original_birth_weights
sys.path.insert(0,str(PARENT))
from s0_source_photon_thomson import source_histories,BIRTH_EV,SOURCE_RATE,INITIAL_COUNT,C
DT=6.25e8
KBEV=8.617333262145e-5
TICKS=(0,800,1600,6400,15999)
BIRTH_GL=128
HI_SIMPSON=24
VERSION="BASS_REI_F08_NATIVE_STAGE_SOURCE_PACKETS_V1"
def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for x in iter(lambda:f.read(1<<20),b""):h.update(x)
 return h.hexdigest()
def hsource(history,tick):
 if tick==0:
  fractions=[.9,.3,.6]
  w=1.5*KBEV*5e4*(1+0.083+.9+0.083*(.3+2*.6))
  escape=0.
 else:
  row=history.original[tick-1]
  fractions=[float(row[k]) for k in ("x_HII","x_HeII","x_HeIII")]
  w=float(row["w_ev_per_h"]);escape=float(row["escape_ev_per_h"])
  npart=1+0.083+fractions[0]+0.083*(fractions[1]+2*fractions[2])
  wcheck=1.5*KBEV*float(row["temperature_K"])*npart
  if not math.isclose(w,wcheck,rel_tol=1e-12,abs_tol=1e-12):
   raise ValueError("original F08 thermal energy and temperature not source-equal")
 return fractions,w,escape

def exact_birth_weights(q,h,t):
 t=np.asarray(t,dtype=float)
 gb=kgrav(q,h,np.asarray(t).reshape((-1,1)))
 a=np.exp(-np.sum(h)*t.reshape((-1,1)))/gb**3
 return a/a.sum(axis=1,keepdims=True)

def exact_pre_packets(history,q,t_s,n_birth=BIRTH_GL,simpson=HI_SIMPSON):
 if t_s==0:
  born=np.array([0.])
  sw=np.array([INITIAL_COUNT])
 else:
  xs,ws=np.polynomial.legendre.leggauss(n_birth)
  born=np.concatenate(([0.],t_s*(xs+1)/2))
  sw=np.concatenate(([INITIAL_COUNT],ws*(SOURCE_RATE*t_s/2)))
 if len(born)!=len(sw):
  raise ValueError("source birth support")
 q=np.asarray(q,dtype=float);h=np.asarray(history.H,dtype=float)
 weights=exact_birth_weights(q,h,born)
 emitted=sw[:,None]*weights
 gb=kgrav(q,h,born.reshape((-1,1)))
 gs=kgrav(q,h,np.array([[t_s]]))
 E=BIRTH_EV*gs/gb
 low=born[:,None].repeat(q.shape[0],axis=1)
 high=np.full_like(low,t_s)
 below=E<13.60
 for _ in range(38):
  mid=(low+high)/2
  energy=BIRTH_EV*kgrav(q,h,mid)/gb
  still=energy>=13.60
  low=np.where(still,mid,low)
  high=np.where(still,high,mid)
 cut=np.where(below,(low+high)/2,t_s)
 duration=cut-born[:,None]
 if np.min(duration)<-1e-5:
  raise ValueError("source photon birth future time")
 survive=emitted.copy()
 for j in range(simpson):
  x=born[:,None]+duration*j/simpson
  y=born[:,None]+duration*(j+.5)/simpson
  z=born[:,None]+duration*(j+1)/simpson
  Ea=BIRTH_EV*kgrav(q,h,x)/gb
  Em=BIRTH_EV*kgrav(q,h,y)/gb
  Eb=BIRTH_EV*kgrav(q,h,z)/gb
  if j==simpson-1:
   Eb=np.where(below,np.maximum(Eb,13.60),Eb)
  ra=C*interpolate_original(history.nhi,x)*verner(Ea)
  rm=C*interpolate_original(history.nhi,y)*verner(Em)
  rb=C*interpolate_original(history.nhi,z)*verner(Eb)
  tau=duration/simpson*(ra+4*rm+rb)/6
  if np.any(tau<0) or np.any(~np.isfinite(tau)):
   raise ValueError("invalid HI source opacity")
  survive*=np.exp(-tau)
 if np.any(survive<=0) or np.min(E)<BIRTH_EV*math.exp(-max(h)*t_s)-1e-12:
  raise ValueError("exact photon source support")
 return born,survive,E,gb

def characteristic_input(history,q,tick,nb=BIRTH_GL,simpson=HI_SIMPSON):
 ts=tick*DT;t1=(tick+1)*DT
 born,survive,Eparent,gb=exact_pre_packets(history,q,ts,nb,simpson)
 # No H I photoabsorption during THIS new native coupled substep.
 g1=kgrav(np.asarray(q),np.asarray(history.H),np.array([[t1]]))
 E1=BIRTH_EV*g1/gb
 ne=SOURCE_RATE*DT
 w1=exact_birth_weights(np.asarray(q),np.asarray(history.H),np.array([t1]))[0]
 packets=[(float(e),float(n)) for e,n in zip(E1.ravel(),survive.ravel()) if n>0]
 packets += [(BIRTH_EV,float(w)) for w in (ne*w1) if w>0]
 parentN=float(survive.sum())
 parentU=float((survive*Eparent).sum())
 inpN=sum(n for e,n in packets)
 inpU=sum(e*n for e,n in packets)
 if not math.isclose(inpN,parentN+ne,rel_tol=3e-13,abs_tol=1e-14):
  raise ValueError("characteristic source input photon loss")
 if min(e for e,n in packets)<BIRTH_EV*math.exp(-max(history.H)*t1)-1e-11:
  raise ValueError("source energy support violated")
 return packets,{"parent_photons_per_H":parentN,"parent_energy_eV_per_H":parentU,
  "stage_input_n_per_H":inpN,"stage_input_u_eV_per_H":inpU,
  "exact_floor_eV":BIRTH_EV*math.exp(-max(history.H)*t1)}

def fixed_inputs(history,owner,ticks=TICKS):
 E=np.asarray(owner["energies"])
 q=np.asarray(owner["qhat"])
 h=np.asarray(history.H)
 n=np.zeros((128,17));n[:,12]=INITIAL_COUNT/128
 gn=np.zeros(128);gu=np.zeros(128)
 prev=original_redshift_g(q,h,0.)
 sigma=verner(E)
 out={}
 for i in range(1,max(ticks)+2):
  t=i*DT;gt=original_redshift_g(q,h,t)
  n,gn,gu,_=remap_once(n,gn,gu,gt/prev,E)
  weights=original_birth_weights(q,h,t,gt)
  n[:,12]+=SOURCE_RATE*DT*weights
  if (i-1) in ticks:
   groups=[(float(e),float(v)) for e,v in zip(E,n.sum(axis=0)) if v>0]
   guard=float(gn.sum())
   if guard:
    mean=float(gu.sum())/guard
    if not (0<mean<10):raise ValueError("original below-10 guard identity")
    groups.append((mean,guard))
   pN=sum(v for e,v in groups);pU=sum(e*v for e,v in groups)
   out[i-1]=(groups,{"stage_input_n_per_H":pN,
                     "stage_input_u_eV_per_H":pU,
                     "fixed_guard_photons_per_H":guard})
  if i<=max(ticks):
   attenuation=1/(1+C*DT*history.nhi[i]*sigma)
   n*=attenuation[None,:]
  prev=gt
 return out

def run(path,ticks=TICKS,nb=BIRTH_GL,simpson=HI_SIMPSON):
 hs=source_histories()
 output=Path(path);output.parent.mkdir(parents=True,exist_ok=True)
 registry=[]
 with output.open("w") as f:
  f.write("# "+VERSION+"\n")
  f.write("# Source: BASS #323 SHA c0e965ba21892346feef9ecb2389932c34f3fc82; original REI-F08 source-pair 0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8\n")
  for lab in ("S0_BI","S0_FLRW"):
   h=hs[lab];orig=original_checkpoint(lab)
   fixed=fixed_inputs(h,orig,ticks)
   for tick in ticks:
    frac,w,escape=hsource(h,tick)
    t=tick*DT;t1=(tick+1)*DT
    nh=1e-4*math.exp(-sum(h.H)*t1)
    e,exmeta=characteristic_input(h,orig["qhat"],tick,nb,simpson)
    fx,fxmeta=fixed[tick]
    for mode,packets,met in (("CHARACTERISTIC",e,exmeta),("ORIGINAL_HAT_FROZEN_HI",fx,fxmeta)):
     id=f"{lab}_T{tick}_{mode}"
     x=["S",id,lab,mode,str(tick),format(t,".17g"),
        format(DT,".17g"),format(nh,".17g"),format(.083,".17g"),
        format(sum(h.H)/3,".17g"),*[format(v,".17g") for v in frac],
        format(w,".17g"),format(escape,".17g")]
     assert len(x)==15
     f.write("|".join(x)+"\n")
     for energy,number in packets:
      if energy<=0 or number<=0 or not math.isfinite(energy*number):
       raise ValueError("invalid stage physical photon packets")
      f.write("P|%.17g|%.17g\n"%(energy,number))
     registry.append({"id":id,"branch":lab,"tick":tick,"t_parent_s":t,"stage_end_s":t1,
        "model":mode,"source_packet_count":len(packets),
        "input_total_N_per_H":sum(n for en,n in packets),
        "input_total_U_eV_per_H":sum(en*n for en,n in packets),
        "original_HHe_fractions":frac,"original_material_w_eV_per_H":w,
        "original_material_escape_eV_per_H":escape,
        "source_meta":met})
 return {"schema":VERSION,"source_parent_head":"c0e965ba21892346feef9ecb2389932c34f3fc82",
   "original_microphysics_rust_sha256":"915d0a898100a54d04a525227e7fbeb870e321fcc14aaa91afd61352b6d4cf4b",
   "original_V1_F08_source_pair":"0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8",
   "same_matter_parent_each_model":True,"birth_gauss_nodes":nb,"pre_absorption_panels":simpson,
   "original_ticks":list(ticks),"cases":registry,"stage_input_file":output.name,
   "stage_input_sha256":sha(output)}

if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--out",type=Path,default=ROOT/"inputs/native_stage_cases.txt")
 ap.add_argument("--ticks",default=",".join(map(str,TICKS)))
 ap.add_argument("--birth",type=int,default=BIRTH_GL)
 ap.add_argument("--simpson",type=int,default=HI_SIMPSON)
 args=ap.parse_args()
 ticks=tuple(sorted({int(x) for x in args.ticks.split(",") if x}))
 if not ticks or min(ticks)<0 or max(ticks)>=16000:
  raise ValueError("original F08 source clock support")
 ans=run(args.out,ticks,args.birth,args.simpson)
 (args.out.parent/"STAGE_INPUT_PROVENANCE.json").write_text(json.dumps(ans,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"stage_case_count":len(ans["cases"]),
    "ticks":list(ticks),"total_source_packets":sum(x["source_packet_count"] for x in ans["cases"]),
    "stage_input_sha256":ans["stage_input_sha256"]},sort_keys=True))
