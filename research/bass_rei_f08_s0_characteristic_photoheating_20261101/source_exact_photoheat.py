#!/usr/bin/env python3
"""One REI original S0 characteristic-photon photoionization/photoheating study.

S0 born 13.7 eV, q direction owned by REI F08, original H/He gas clock
held frozen; compare exact packet redshift to original fixed-grid hat remap.
All photon numbers/energies per original comoving H nucleus. Not a new H/He IVP.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,io,json,math,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent/"bass_rei_f08_s0_source_photon_thomson_20261101"
PR321=ROOT.parent/"bass_rei_f08_s0_remap_support_20261101"
sys.path.insert(0,str(PR321))
from spectral_support import original_checkpoint,remap_once,original_redshift_g,original_birth_weights,DT,NSTEP
sys.path.insert(0,str(PARENT))
from s0_source_photon_thomson import (
    source_histories,sigma_hi,C,BIRTH_EV,SOURCE_RATE,INITIAL_COUNT,END,SHA as F08_SOURCE_SHA
)
SOURCE_PR321="178d93c380a0e868a22869c3160d81c0aa643098"
ION=13.598434599702    # actual REI PrimaryStage HI chemical binding eV
FIT_CUTOFF=13.60       # original Verner96 atomic-owner lower energy
STEPS=(1,10,100,400,800,1600,3200,4800,6400,8000,9600,11200,12800,14400,16000)
COLUMNS=("branch","source_original_tick","proper_time_s","direction_id",
         "q_x","q_y","q_z","characteristic_surviving_per_H",
         "characteristic_ionizing_per_H","characteristic_energy_eV_per_H",
         "characteristic_photo_rate_per_H_s","characteristic_heat_rate_eV_per_H_s",
         "characteristic_cumulative_absorbed_per_H",
         "characteristic_cumulative_photoheat_eV_per_H",
         "characteristic_cumulative_absorbed_energy_eV_per_H")
MODEL="BASS_REI_F08_S0_MONOENERGETIC_CHARACTERISTIC_PHOTOIONIZATION_HEATING_V1"

def checksum(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def verner(E):
    E=np.asarray(E,dtype=np.float64)
    if np.any(~np.isfinite(E)) or np.any(E<0) or np.any(E>5e4):
        raise ValueError("original Verner H I energy domain")
    v=np.zeros_like(E)
    sel=E>=FIT_CUTOFF
    x=E[sel]/.4298
    v[sel]=5.475e4*(x-1)**2*x**(2.963/2-5.5)*(1+np.sqrt(x/32.88))**(-2.963)*1e-18
    return v

def interpolate_original(a,t):
    t=np.asarray(t,dtype=np.float64)
    if np.any((t<0)|(t>END)) or np.any(~np.isfinite(t)):
        raise ValueError("invalid original proper time")
    j=np.minimum((t/DT).astype(np.int64),NSTEP-1)
    u=np.clip((t-j*DT)/DT,0,1)
    vals=np.asarray(a,dtype=np.float64)
    return vals[j]*(1-u)+vals[j+1]*u

def kgrav(q,H,t):
    """g(q,t)=sqrt(sum q_i² exp(-2 H_i t)): shape t[:,None], q[None,:]."""
    t=np.asarray(t,dtype=np.float64)
    q=np.asarray(q,dtype=np.float64)
    hh=np.asarray(H,dtype=np.float64)
    return np.sqrt(np.sum(q[None,:,:]**2*np.exp(-2*t[...,None]*hh[None,None,:]),axis=-1))

def characteristic_snapshot(history,sourceq,t,births=128,simpson=24,include_rays=True):
    """Positive passive photon transport on exact source energies with frozen nHI(t)."""
    if not 0<t<=END or births<8 or simpson<4 or simpson%2:
        raise ValueError("source photon quadrature domain")
    q=np.asarray(sourceq,dtype=float)
    if q.shape!=(128,3) or not np.allclose(np.sum(q*q,axis=1),1,atol=1e-12):
        raise ValueError("original source q directions")
    H=np.asarray(history.H,dtype=float)
    # Original S0 isotropic initial impulse + proper-time continuous birth measure.
    x,wx=np.polynomial.legendre.leggauss(births)
    born=np.concatenate(([0.],t*(x+1)/2))
    srcw=np.concatenate(([INITIAL_COUNT],wx*(SOURCE_RATE*t/2)))
    tb=born[:,None]
    gb=kgrav(q,H,tb)
    gt=kgrav(q,H,np.array([[t]]))
    E=BIRTH_EV*gt/gb
    # REI's original angular source distribution at each original birth clock:
    # q_i are spatial Killing labels; physical isotropic birth requires vol/g^3.
    unnormalized=np.exp(-float(H.sum())*tb)/gb**3
    birth_direction=unnormalized/unnormalized.sum(axis=1,keepdims=True)
    emitted=srcw[:,None]*birth_direction
    if not math.isclose(float(emitted.sum()),INITIAL_COUNT+SOURCE_RATE*t,rel_tol=2e-14):
        raise ValueError("original source birth measure")
    # Bianchi energy decreases monotonically for these original H_i>0.
    lo=np.broadcast_to(tb,E.shape).copy()
    hi=np.full(E.shape,t)
    crossed=E<FIT_CUTOFF
    for _ in range(38):
        mid=(lo+hi)/2
        Em=BIRTH_EV*kgrav(q,H,mid)/gb
        still=Em>=FIT_CUTOFF
        lo=np.where(still,mid,lo)
        hi=np.where(still,hi,mid)
    cut=np.where(crossed,(lo+hi)/2,t)
    duration=cut-tb
    if np.any(duration<0):
        raise ValueError("negative causal photoionization time")
    survivors=emitted.copy()
    absorbed=np.zeros_like(survivors)
    energy_abs=np.zeros_like(survivors)
    excess_heat=np.zeros_like(survivors)
    redshift_eligible=emitted>0
    for j in range(simpson):
        aa=tb+duration*j/simpson
        mm=tb+duration*(j+.5)/simpson
        bb=tb+duration*(j+1)/simpson
        Ea=BIRTH_EV*kgrav(q,H,aa)/gb
        Em=BIRTH_EV*kgrav(q,H,mm)/gb
        Eb=BIRTH_EV*kgrav(q,H,bb)/gb
        # Avoid a +/-few ULP endpoint discontinuity at exact Verner threshold.
        if j==simpson-1:
            Eb=np.where(crossed,np.maximum(Eb,FIT_CUTOFF),Eb)
        ka=C*interpolate_original(history.nhi,aa)*verner(Ea)
        km=C*interpolate_original(history.nhi,mm)*verner(Em)
        kb=C*interpolate_original(history.nhi,bb)*verner(Eb)
        dt=duration/simpson
        d_tau=dt*(ka+4*km+kb)/6
        if np.any(d_tau<0) or np.any(~np.isfinite(d_tau)):
            raise ValueError("negative/nonfinite photoabsorption optical depth")
        dabs=survivors*(-np.expm1(-d_tau))
        absorbed+=dabs
        energy_abs+=dabs*Em
        excess_heat+=dabs*np.maximum(Em-ION,0)
        survivors-=dabs
    total=survivors+absorbed
    if np.max(abs(total-emitted))>1.2e-16:
        raise ValueError("characteristic local source-photon count ledger")
    per_dir_N=survivors.sum(axis=0)
    ionizing=np.where(E>=FIT_CUTOFF,survivors,0.)
    per_dir_ion=ionizing.sum(axis=0)
    per_dir_U=(survivors*E).sum(axis=0)
    sig=verner(E)
    # Γ_HI per neutral atom and proper photon absorption rate per ORIGINAL H nucleus.
    per_dir_gamma_weight=(survivors*sig).sum(axis=0)
    per_dir_A=C*history.linear(history.nhi,t)*per_dir_gamma_weight
    per_dir_H=C*history.linear(history.nhi,t)*np.sum(survivors*sig*np.maximum(E-ION,0),axis=0)
    ray_abs=absorbed.sum(axis=0)
    ray_H=excess_heat.sum(axis=0)
    ray_Eabs=energy_abs.sum(axis=0)
    emitted_U=BIRTH_EV*emitted.sum()
    survived_U=per_dir_U.sum()
    absorbed_U=ray_Eabs.sum()
    redshift_U=emitted_U-survived_U-absorbed_U
    if redshift_U<-8e-8:
        raise ValueError("unphysical source redshift energy work")
    if np.min(E)<BIRTH_EV*math.exp(-max(H)*t)-1e-11:
        raise ValueError("exact photon energy below source support")
    if np.max(E)>BIRTH_EV+1e-12:
        raise ValueError("original S0 emitted energy exceeded")
    ans={
        "source_birth_n_per_H":float(emitted.sum()),
        "remaining_photon_n_per_H":float(per_dir_N.sum()),
        "ionizing_photon_n_per_H":float(per_dir_ion.sum()),
        "photon_energy_eV_per_H":float(survived_U),
        "HI_photo_gamma_per_neutral_H_s":float(C*history.linear(history.nh,t)*per_dir_gamma_weight.sum()),
        "HI_photo_rate_per_original_H_s":float(per_dir_A.sum()),
        "HI_photoheating_rate_eV_per_original_H_s":float(per_dir_H.sum()),
        "HI_cumulative_absorbed_photons_per_H":float(ray_abs.sum()),
        "HI_cumulative_absorbed_energy_eV_per_H":float(absorbed_U),
        "HI_cumulative_excess_photoheat_eV_per_H":float(ray_H.sum()),
        "cosmological_redshift_work_eV_per_H":float(redshift_U),
        "photon_number_ledger_abs_residual":float(abs(emitted.sum()-per_dir_N.sum()-ray_abs.sum())),
        "photon_energy_ledger_abs_residual_eV_per_H":float(abs(emitted_U-survived_U-absorbed_U-redshift_U)),
        "physical_source_lower_energy_eV":BIRTH_EV*math.exp(-max(H)*t),
        "actual_survivor_energy_min_eV":float(E[survivors>0].min()),
        "source_hit_Verner_subthreshold_count":int(np.count_nonzero((E<FIT_CUTOFF)&(survivors>0))),
        "num_packets":int(E.size),
    }
    if not include_rays:return ans,()
    rows=[]
    for j,d in enumerate(q):
        rows.append({"branch":history.label,"source_original_tick":round(t/DT),"proper_time_s":t,
          "direction_id":j,"q_x":float(d[0]),"q_y":float(d[1]),"q_z":float(d[2]),
          "characteristic_surviving_per_H":float(per_dir_N[j]),
          "characteristic_ionizing_per_H":float(per_dir_ion[j]),
          "characteristic_energy_eV_per_H":float(per_dir_U[j]),
          "characteristic_photo_rate_per_H_s":float(per_dir_A[j]),
          "characteristic_heat_rate_eV_per_H_s":float(per_dir_H[j]),
          "characteristic_cumulative_absorbed_per_H":float(ray_abs[j]),
          "characteristic_cumulative_photoheat_eV_per_H":float(ray_H[j]),
          "characteristic_cumulative_absorbed_energy_eV_per_H":float(ray_Eabs[j])})
    return ans,rows

def frozen_hat_history(history,checkpoint):
    """Replay prior PR321 verified original fixed-node hat + frozen H I source."""
    E=np.array(checkpoint["energies"])
    q=np.asarray(checkpoint["qhat"])
    nd,ne=checkpoint["original"].shape
    photons=np.zeros((nd,ne))
    photons[:,12]=INITIAL_COUNT/nd
    gn=np.zeros(nd);gu=np.zeros(nd)
    sigma=verner(E)
    prev=original_redshift_g(q,history.H,0)
    absorbedN=absorbedU=photo_heat=0.
    redshift_work=0.
    result={}
    for i in range(1,NSTEP+1):
        t=i*DT
        oldU=float(np.sum(photons*E)+np.sum(gu))
        gt=original_redshift_g(q,history.H,t)
        photons,gn,gu,_=remap_once(photons,gn,gu,gt/prev,E)
        redshift_work+=oldU-(float(np.sum(photons*E)+np.sum(gu)))
        srcw=original_birth_weights(q,history.H,t,gt)
        photons[:,12]+=SOURCE_RATE*DT*srcw
        original_cumsum=(C*DT*history.nhi[i])*sigma
        prev_photons=photons.copy()
        photons/=1+original_cumsum[None,:]
        delta=prev_photons-photons
        absorbedN+=float(np.sum(delta))
        absorbedU+=float(np.sum(delta*E))
        photo_heat+=float(np.sum(delta*np.maximum(E-ION,0)))
        prev=gt
        if i in STEPS:
            num=float(np.sum(photons)+np.sum(gn))
            weight=np.sum(photons,axis=0)
            photo_gamma=float(C*history.nh[i]*np.dot(weight,sigma))
            heat_rate=float(C*history.nhi[i]*np.dot(weight,sigma*np.maximum(E-ION,0)))
            result[i]={
                "fixed_hat_surviving_n_per_H":num,
                "fixed_hat_ionizing_n_per_H":float(np.sum(weight[E>=FIT_CUTOFF])),
                "fixed_hat_photon_energy_eV_per_H":float(np.dot(weight,E)+np.sum(gu)),
                "fixed_hat_gamma_HI_per_neutral_s":photo_gamma,
                "fixed_hat_photo_rate_per_H_s":float(C*history.nhi[i]*np.dot(weight,sigma)),
                "fixed_hat_photoheat_rate_eV_per_H_s":heat_rate,
                "fixed_hat_cumulative_absorbed_per_H":absorbedN,
                "fixed_hat_cumulative_absorbed_energy_eV_per_H":absorbedU,
                "fixed_hat_cumulative_excess_photoheat_eV_per_H":photo_heat,
                "fixed_hat_cosmological_redshift_work_eV_per_H":redshift_work,
            }
    return result

def csvgzip(path,rows):
    assert rows
    with path.open("wb") as f:
        with gzip.GzipFile(fileobj=f,filename="",mtime=0,mode="wb",compresslevel=6) as g:
            with io.TextIOWrapper(g,encoding="utf8",newline="") as txt:
                w=csv.DictWriter(txt,fieldnames=list(rows[0]))
                w.writeheader();w.writerows(rows)
    return checksum(path)

def calculate(out,births=128,simpson=24):
    if births<8 or simpson<4 or simpson%2:
        raise ValueError("quad")
    hist=source_histories()
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    summaries=[];rays=[]
    for label in ("S0_BI","S0_FLRW"):
        h=hist[label];owner=original_checkpoint(label)
        fixed=frozen_hat_history(h,owner)
        for step in STEPS:
            t=h.times[step]
            exact,dirrows=characteristic_snapshot(h,owner["qhat"],t,births,simpson,True)
            obs=h.original[step-1]
            fr=fixed[step]
            merged={"branch":label,"original_tick":step,"proper_time_s":t,
                "quadrature_birth_nodes":births,"quadrature_absorption_simpson_panels":simpson,
                **exact,**fr,
                "original_F08_owner_gamma_HI_per_neutral_s":float(obs["gamma_HI_per_s"]),
                "original_F08_owner_photon_n_per_H":float(obs["photon_n"]),
                "original_F08_owner_photon_energy_eV_per_H":float(obs["photon_u_ev_per_h"]),
                "original_F08_owner_absorbed_n_per_H":float(obs["absorbed_n"]),
                "original_F08_owner_temperature_K":float(obs["temperature_K"]),
                "original_F08_owner_x_HII":float(obs["x_HII"]),
                "exact_over_original_gamma_HI_minus1":exact["HI_photo_gamma_per_neutral_H_s"]/float(obs["gamma_HI_per_s"])-1,
                "fixed_over_original_gamma_HI_minus1":fr["fixed_hat_gamma_HI_per_neutral_s"]/float(obs["gamma_HI_per_s"])-1,
                "exact_over_fixed_photoheat_rate_minus1":(exact["HI_photoheating_rate_eV_per_original_H_s"]/fr["fixed_hat_photoheat_rate_eV_per_H_s"]-1)
                      if fr["fixed_hat_photoheat_rate_eV_per_H_s"]>0 else None,
                "exact_minus_fixed_absorbed_per_H":exact["HI_cumulative_absorbed_photons_per_H"]-fr["fixed_hat_cumulative_absorbed_per_H"],
                "exact_minus_fixed_excess_photoheat_eV_per_H":exact["HI_cumulative_excess_photoheat_eV_per_H"]-fr["fixed_hat_cumulative_excess_photoheat_eV_per_H"],
            }
            summaries.append(merged);rays.extend(dirrows)
    outsum=out/"F08_S0_SOURCE_EXACT_CHARACTERISTIC_PHOTOION_HEAT_HISTORY.csv.gz"
    outrays=out/"F08_S0_SOURCE_EXACT_CHARACTERISTIC_ANGLE_EVENTS.csv.gz"
    sumsha=csvgzip(outsum,summaries);raysha=csvgzip(outrays,rays)
    report={
      "schema":MODEL,"unit":"ONE_SOURCE_OWNER_F08_PHOTON_REPRESENTATION_TO_HI_IONIZATION_HEAT_PHYSICS",
      "source_parent_PR":321,"source_parent_head":SOURCE_PR321,
      "original_REI_F08_PR":349,"original_source_s0_SHA256":F08_SOURCE_SHA,
      "original_checkpoint_hashes":"PARENT_PR321_BYTE_EXACT_4_INPUTS",
      "physical_assumptions":"original_HHe_matter_time_frozen_no_reionization_IVP_no_selfconsistent_backreaction",
      "source_birth":"REI_S0_13.7EV_INITIAL_AND_CONTINUOUS_ORIGINAL_DISCRETE_Q_BIRTH_ISOTROPY",
      "photo_provider":"ORIGINAL_VERNER96_HI_PER_ATOM_13.60EV_CUTOFF",
      "photo_heat_ionization_energy_eV":ION,
      "units":{"rate":"per_original_H_per_second","gamma":"per_neutral_H_per_second",
               "photoheat":"eV_per_original_H_per_second","cumulative_heat":"eV_per_original_H",
               "photon_number":"per_original_comoving_H"},
      "quadrature":{"births_Gauss_Legendre":births,"absorption_Simpson_panels":simpson},
      "epochs":len(summaries),"angle_rows":len(rays),
      "summary_sha256":sumsha,"angle_sha256":raysha,
      "summary_file":outsum.name,"angle_file":outrays.name,
      "original_discrete_photon_IVP_replayed":False,
      "original_hhe_chemistry_thermodynamics_IVP_replayed":False,
      "physical_admission":"SOURCE_CONDITIONAL_EXPLORATORY_HOLD",
      "REI_CENTRAL":"28/88_REPORTED","REI_WORKING":"33/88_REPORTED_NONADDITIVE",
      "BASS_UPPER":"9/15_SCOPED_SOURCE_MAPPED",
      "new_canonical_nodes":0,"new_upper_physical_complete":0,"production":"HOLD",
      "summary_preview":[x for x in summaries if x["original_tick"] in (800,1600,6400,16000)]
    }
    (out/"RESULT.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("SOURCE_EXACT_PHYSICAL_HEAT_RESULTS",json.dumps({
        "rows":len(summaries),"angle_rows":len(rays),"summary_sha256":sumsha,
        "angle_sha256":raysha,"final":report["summary_preview"][-2:]},sort_keys=True))
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=ROOT/"results")
    p.add_argument("--births",type=int,default=128)
    p.add_argument("--simpson",type=int,default=24)
    a=p.parse_args()
    calculate(a.out,a.births,a.simpson)
