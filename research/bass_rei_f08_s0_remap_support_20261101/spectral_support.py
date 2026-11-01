#!/usr/bin/env python3
"""Actual REI F08 S0 original spectral remap, source-support/HI physics audit.

Pure passive and frozen-material photon-only isolation; does not re-solve REI H/He.
Reads untouched original F08 V1 checkpoint and its original 8x16 angular/17-node energy grid.
"""
from __future__ import annotations
import csv,gzip,hashlib,io,json,math,struct,sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent/"bass_rei_f08_s0_source_photon_thomson_20261101"
sys.path.insert(0,str(PARENT))
from s0_source_photon_thomson import source_histories,sigma_hi,C,BIRTH_EV,SOURCE_RATE,INITIAL_COUNT,END

RAW=ROOT/"source_inputs"
CHECKPOINT_SHA={
"S0_BI-checkpoint.dat":"d7b717aab4f98b48d687d1b814dd48b767f088af7296ce61876dd7b526f3d6e1",
"S0_BI-header.jsonl":"a2a8bdd963febd1667d61e49ae027c02a2260208bbd9061c25117f1fdbe59082",
"S0_FLRW-checkpoint.dat":"5e80b15409f36ccd4e0f0aeab61ba0c4bcf0e53af579ea854cc0883660ffc174",
"S0_FLRW-header.jsonl":"7746d4f6e19ce59cdc3f0c8da300f6b5f12aa3b1c7e06d85cfc27ed89cff33db",
}
DT=6.25e8
NSTEP=16000
THRESHOLD=13.60
SIM_MODES=("PASSIVE_REMAP_ONLY","FROZEN_HI_IMPLICIT_ABSORPTION")
LABELS=("S0_BI","S0_FLRW")
N_SAMPLES=(1,10,100,400,800,1600,3200,4800,6400,8000,9600,11200,12800,14400,16000)

def digest(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for blob in iter(lambda:f.read(1<<20),b""):
            h.update(blob)
    return h.hexdigest()

def double(hexval):
    return struct.unpack(">d",bytes.fromhex(hexval))[0]

def original_checkpoint(label):
    for name,hashval in CHECKPOINT_SHA.items():
        if digest(RAW/name)!=hashval:
            raise ValueError("ORIGINAL_REI_V1_SOURCE_SHA_FAILURE: "+name)
    header=json.loads((RAW/(label+"-header.jsonl")).read_text())
    lines=(RAW/(label+"-checkpoint.dat")).read_text().splitlines()
    dims=lines[0].split()
    if len(dims)!=11 or dims[0]!="REI_F08_PAIRED_CHECKPOINT_V1":
        raise ValueError("wrong source-owner checkpoint version")
    m,nmu,nphi,accepted,rejected=map(int,dims[1:6])
    energies=np.array(header["energy_nodes"],dtype=np.float64)
    q=np.array(header["qhat"],dtype=np.float64)
    if (m,nmu,nphi,accepted,rejected)!=(4,8,16,NSTEP,0):
        raise ValueError("source-owner S0 accepted path changed")
    nd=nmu*nphi; ns=len(energies)
    if not(np.all(np.diff(energies)>0) and len(energies)==4*m+1 and q.shape==(nd,3)):
        raise ValueError("original source energy/angular bins mismatch")
    if not np.allclose(np.sum(q*q,axis=1),1,rtol=0,atol=1e-12):
        raise ValueError("original angular Killing rays nonunit")
    n=int(lines[4])
    if n!=nd*ns:raise ValueError("checkpoint original spectral size")
    packets=np.array([double(line.split()[0]) for line in lines[5:5+n]],dtype=float).reshape(nd,ns)
    guard_count=int(lines[5+n])
    if guard_count!=nd or len(lines)!=6+n+nd:
        raise ValueError("checkpoint original lower guard record")
    guard_n=np.array([double(line.split()[0]) for line in lines[6+n:]])
    guard_u=np.array([double(line.split()[1]) for line in lines[6+n:]])
    if np.any(packets<0) or np.any(guard_n<0) or np.any(guard_u<0):
        raise ValueError("original source output negative")
    return dict(label=label,energies=energies,qhat=q,original=packets,
       original_guard_n=guard_n,original_guard_u=guard_u,
       original_total_n=float(np.sum(packets)+np.sum(guard_n)),
       original_total_u=float(np.sum(packets*energies[None,:])+np.sum(guard_u)),
       m=m,nmu=nmu,nphi=nphi)

def exact_floor(t,h):
    return BIRTH_EV*math.exp(-max(h)*t)

def original_redshift_g(q,h,t):
    return np.sqrt(np.sum(q*q*np.exp(-2*np.asarray(h)[None,:]*t),axis=1))

def original_birth_weights(q,h,t,g):
    volume=math.exp(-sum(h)*t)
    a=volume/(g**3)
    return a/a.sum()

def remap_once(values,guardn,guardu,ratio,energies):
    """Exactly original hat(E_j*r,nodes,k) on original S0 step support."""
    nd,ns=values.shape
    if len(ratio)!=nd or len(energies)!=ns or not (np.all(ratio>0) and np.all(ratio<1)):
        raise ValueError("source redshift domain")
    shifted=energies[None,:]*ratio[:,None]
    if np.min(shifted[:,1:]-(energies[None,:-1]))<0:
        raise ValueError("original one-neighbor hat simplification not applicable")
    p_down=(energies[None,1:]-shifted[:,1:])/np.diff(energies)[None,:]
    if not np.all((p_down>=0)&(p_down<=1)):
        raise ValueError("original hat probability out of range")
    nxt=np.zeros_like(values)
    nxt[:,:-1]+=values[:,1:]*p_down
    nxt[:,1:]+=values[:,1:]*(1-p_down)
    gnew=guardn+values[:,0]
    unew=guardu*ratio+values[:,0]*shifted[:,0]
    before_n=np.sum(values)+np.sum(guardn)
    after_n=np.sum(nxt)+np.sum(gnew)
    before_u=float(np.sum(values*shifted)+np.sum(guardu*ratio))
    after_u=float(np.sum(nxt*energies[None,:])+np.sum(unew))
    return nxt,gnew,unew,max(abs(after_n-before_n),abs(after_u-before_u))

def support_statistics(packets,guard_n,guard_u,E,t,h):
    floor=exact_floor(t,h)
    under=E<floor
    false_count=float(np.sum(packets[:,under])+np.sum(guard_n))
    n_total=float(np.sum(packets)+np.sum(guard_n))
    under_hi=E<THRESHOLD
    return {
       "exact_min_eV":floor,
       "n_per_H":n_total,
       "energy_eV_per_H":float(np.sum(packets*E)+np.sum(guard_u)),
       "under_exact_min_n_per_H":false_count,
       "under_exact_min_fraction":false_count/n_total if n_total else float("nan"),
       "under_13_60ev_n_per_H":float(np.sum(packets[:,under_hi])+np.sum(guard_n)),
       "guard_n_per_H":float(np.sum(guard_n)),
       "guard_u_eV_per_H":float(np.sum(guard_u)),
    }

def run_mode(h, checkpoint,mode):
    E=checkpoint["energies"];q=checkpoint["qhat"]
    nd,ns=checkpoint["original"].shape
    n=np.zeros((nd,ns),dtype=float)
    n[:,3*checkpoint["m"]]=INITIAL_COUNT/nd
    guard_n=np.zeros(nd);guard_u=np.zeros(nd)
    sigma=np.array([sigma_hi(e) for e in E])
    prev_g=original_redshift_g(q,h.H,0)
    sourceN=INITIAL_COUNT;absorbedN=0.
    max_ledger=0.;max_remap_energy_residual=0.
    output=[]
    for step in range(1,NSTEP+1):
        t=step*DT
        g=original_redshift_g(q,h.H,t)
        r=g/prev_g
        n,guard_n,guard_u,err=remap_once(n,guard_n,guard_u,r,E)
        max_remap_energy_residual=max(max_remap_energy_residual,err)
        w=original_birth_weights(q,h.H,t,g)
        source_packet=SOURCE_RATE*DT
        n[:,3*checkpoint["m"]]+=source_packet*w
        sourceN+=source_packet
        if mode=="FROZEN_HI_IMPLICIT_ABSORPTION":
            nhit=h.nhi[step]
            sigma_eff=C*DT*nhit*sigma
            factor=1/(1+sigma_eff)
            before=n.copy()
            n*=factor[None,:]
            absorbedN+=float(np.sum(before-n))
        prev_g=g
        if step in N_SAMPLES:
            st=support_statistics(n,guard_n,guard_u,E,t,h.H)
            owner=h.original[step-1]
            output.append({
                "branch":h.label,"mode":mode,"tick":step,"t_proper_s":t,
                "owner_original_photons_per_H":float(owner["photon_n"]),
                "owner_original_gamma_HI_per_s":float(owner["gamma_HI_per_s"]),
                "owner_original_lower_guard_per_H":float(owner["lower_guard_n"]),
                "sim_integrated_source_per_H":sourceN,
                "sim_integrated_absorbed_per_H":absorbedN,
                **st
            })
        balance=sourceN-absorbedN-(float(np.sum(n))+float(np.sum(guard_n)))
        max_ledger=max(max_ledger,abs(balance))
    return n,guard_n,guard_u,output,{
        "mode":mode,"branch":h.label,"max_photon_count_ledger_abs":max_ledger,
        "max_redshift_number_energy_remap_residual_abs":max_remap_energy_residual,
        "frozen_sigma_photo_cm2":sigma.tolist(),
        "initial_photon_per_H":INITIAL_COUNT,
        "source_injection_per_H":SOURCE_RATE*END,
        "absorbed_per_H":absorbedN
    }

def gzwrite(path,rows):
    with path.open("wb") as b:
        with gzip.GzipFile(fileobj=b,mode="wb",filename="",mtime=0,compresslevel=6) as z:
            with io.TextIOWrapper(z,encoding="utf8",newline="") as txt:
                writer=csv.DictWriter(txt,fieldnames=tuple(rows[0]))
                writer.writeheader();writer.writerows(rows)
    return digest(path)

def build(out):
    histories=source_histories()
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    timeline=[];spectrum=[];angular=[];stats=[]
    for label in LABELS:
        h=histories[label]
        c=original_checkpoint(label)
        original_stats=support_statistics(c["original"],c["original_guard_n"],c["original_guard_u"],c["energies"],END,h.H)
        actual=h.original[-1]
        if abs(original_stats["n_per_H"]/float(actual["photon_n"])-1)>2e-13:
            raise ValueError("original checkpoint/source-owner photon quantity mismatch")
        for mode in SIM_MODES:
            photons,gn,gu,series,control=run_mode(h,c,mode)
            timeline.extend(series)
            stats.append(control)
            candidate=[{"mode":mode,"photons":photons,"guardn":gn,"guardu":gu}]
            if mode=="FROZEN_HI_IMPLICIT_ABSORPTION":
                candidate.append({"mode":"ORIGINAL_F08_SOURCE_CHECKPOINT","photons":c["original"],
                     "guardn":c["original_guard_n"],"guardu":c["original_guard_u"]})
            for cand in candidate:
                spectra=cand["photons"]; guard=cand["guardn"]; energy_guard=cand["guardu"]
                for k,ek in enumerate(c["energies"]):
                    mass=float(spectra[:,k].sum())
                    spectrum.append({"branch":label,"mode":cand["mode"],"E_node_ev":float(ek),
                        "energy_node_index":k,"photon_n_per_H":mass,
                        "photon_u_ev_per_H":mass*ek,
                        "below_exact_physical_support":bool(ek<exact_floor(END,h.H)),
                        "below_HI_fit_threshold":bool(ek<THRESHOLD)})
                for d,q in enumerate(c["qhat"]):
                    false_e=c["energies"]<exact_floor(END,h.H)
                    angular.append({"branch":label,"mode":cand["mode"],"direction_id":d,
                        "q_x":float(q[0]),"q_y":float(q[1]),"q_z":float(q[2]),
                        "retained_n_per_H":float(spectra[d].sum()+guard[d]),
                        "below_exact_floor_n_per_H":float(spectra[d,false_e].sum()+guard[d]),
                        "guard_n_per_H":float(guard[d]),
                        "guard_u_eV_per_H":float(energy_guard[d])})
                spectrum.append({"branch":label,"mode":cand["mode"],"E_node_ev":-1.0,
                        "energy_node_index":-1,"photon_n_per_H":float(guard.sum()),
                        "photon_u_ev_per_H":float(energy_guard.sum()),
                        "below_exact_physical_support":True,"below_HI_fit_threshold":True})
        first_idx=3*c["m"]
        g1=original_redshift_g(c["qhat"],h.H,DT)
        p=(c["energies"][first_idx]*(1-g1))/(c["energies"][first_idx]-c["energies"][first_idx-1])
        if not (np.min(p)>0 and np.max(p)<1):
            raise ValueError("analytic first redshift hat transfer impossible")
        stats.append({"branch":label,"type":"ACTUAL_SOURCE_FIRST_STEP_HAT_WITNESS",
            "first_step_exact_physical_floor":exact_floor(DT,h.H),
            "first_step_artificial_lower_node_eV":float(c["energies"][first_idx-1]),
            "first_step_artificial_mass_before_absorption_per_H":float(INITIAL_COUNT*np.mean(p)),
            "first_step_lower_node_fraction_min":float(np.min(p)),
            "first_step_lower_node_fraction_max":float(np.max(p)),
            "first_step_P0_energy_variance_max_ev2":float(np.max(
                (c["energies"][first_idx]*g1-c["energies"][first_idx-1]) *
                (c["energies"][first_idx]-c["energies"][first_idx]*g1)))})
        stats.append({"branch":label,"type":"ORIGINAL_PHYSICAL_S0_END_CHECKPOINT",
            "checkpoint_sha256":CHECKPOINT_SHA[label+"-checkpoint.dat"],
            "original_source_photon_U_eV_per_H":original_stats["energy_eV_per_H"],
            "original_source_photon_n_per_H":original_stats["n_per_H"],
            "original_below_exact_physical_support_n_per_H":original_stats["under_exact_min_n_per_H"],
            "original_below_exact_physical_support_fraction":original_stats["under_exact_min_fraction"],
            "original_lower_guard_n_per_H":original_stats["guard_n_per_H"],
            "exact_energy_floor_eV":original_stats["exact_min_eV"]})
    f1=out/"SOURCE_MATCHED_F08_S0_SPECTRAL_SUPPORT_TIMELINE.csv.gz"
    f2=out/"ORIGINAL_AND_REMAPPED_F08_S0_FINAL_SPECTRUM.csv.gz"
    f3=out/"ORIGINAL_AND_REMAPPED_F08_S0_ANGULAR_SUPPORT.csv.gz"
    h1,h2,h3=(gzwrite(a,b) for a,b in ((f1,timeline),(f2,spectrum),(f3,angular)))
    res={
      "schema":"BASS_REI_F08_ORIGINAL_HAT_S0_SPECTRAL_SUPPORT_CAUSAL_MECHANISM_V1",
      "model":"ORIGINAL_HAT_REMAP_SUBOPERATOR_WITH_SOURCE_S0_13.7EV_ZERO_COLLISION_AND_FROZEN_HI_CONTROLS",
      "original_F08_photo_owner_equivalence":"NOT_CLAIMED",
      "source_matter_and_time":"ORIGINAL_F08_16K_HHE_SAVED_HISTORY_BYTE_LOCKED",
      "source_original_checkpoint_sha256":CHECKPOINT_SHA,
      "source_old_original_atomic_owner":"PR317_IMMUTABLE_SHA",
      "original_source_rei_pr":349,
      "source_parent_bass_pr":317,
      "source_parent_bass_head":"18e6273f28ea67e472c919de86594f70fd1c81c9",
      "source_pair_sha256":"0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8",
      "support_lemma":"hat interpolation has positive lower neighbor weight if 0<E_j*r-E_(j-1)<E_j-E_(j-1), even if lower node is beneath exact physical minimum",
      "first_ever_epoch_physical_null_floor_eV":exact_floor(DT,histories["S0_BI"].H),
      "last_physical_null_floor_eV":exact_floor(END,histories["S0_BI"].H),
      "science_admission":"ACTUAL_ORIGINAL_REMAPPING_SUPPORT_MECHANISM_AND_SOURCE_CONDITIONAL_QUANTITATIVE_DIAGNOSTIC",
      "original_F08_admission":"HOLD","original_F05":"BLOCKED_TICK160/131072",
      "original_F09":"BLOCKED_ATOMIC_SOURCE_DOMAIN",
      "stat_records":stats,"time_rows":len(timeline),"spectrum_rows":len(spectrum),"angular_rows":len(angular),
      "time_sha256":h1,"spectrum_sha256":h2,"angular_sha256":h3,
      "time_file":f1.name,"spectrum_file":f2.name,"angular_file":f3.name,
      "physical_claim":"ORIGINAL_DISCRETE_S0_SUPPORT_INCOMPATIBLE_WITH_EXACT_MONOENERGETIC_CAUSAL_CHARACTERISTICS",
      "root_cause_scope":"HAT_LINEAR_ENERGY_REMAP_CAUSES_IMMEDIATE_LOWER_NODE_LEAKAGE_AND_CONSERVES_NUMBER_ENERGY_PER_STEP; FULL_ORIGINAL_6_PERCENT_DIFFERENCE_NOT_SOLVED",
      "original_solver_replayed":False,
      "einstein_coupled_admission":False,
      "REI_CENTRAL":"28/88_REPORTED","REI_WORKING":"33/88_REPORTED_NONADDITIVE",
      "BASS_UPPER":"9/15_SCOPED_SOURCE_MAPPED","canonical_delta":0,"full_bass_upper_delta":0,
      "production":"HOLD","merged":False
    }
    (out/"RESULT.json").write_text(json.dumps(res,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"row_counts":(len(timeline),len(spectrum),len(angular)),
     "original_BI_below_floor_frac":next(s["original_below_exact_physical_support_fraction"] for s in stats if s.get("type")=="ORIGINAL_PHYSICAL_S0_END_CHECKPOINT" and s["branch"]=="S0_BI"),
     "frozen_BI_end":next(x for x in timeline if x["branch"]=="S0_BI" and x["mode"]=="FROZEN_HI_IMPLICIT_ABSORPTION" and x["tick"]==16000),
     "passive_BI_end":next(x for x in timeline if x["branch"]=="S0_BI" and x["mode"]=="PASSIVE_REMAP_ONLY" and x["tick"]==16000)},sort_keys=True))
    return res

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=ROOT/"results")
    args=p.parse_args()
    build(args.out)
