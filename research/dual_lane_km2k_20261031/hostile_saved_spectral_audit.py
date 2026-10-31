"""Independent source-saved KM2K frequency audit (NO BASS / no KM2K source imports).

Uses explicit raise exceptions, valid under python -O. Reconstructs all
164 epoch spectral moments and per-event 4-force from immutable raw NPZ.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from scipy.special import ndtr


def check(test,code):
    if not bool(test):raise ArithmeticError("KM2K_SAVED_REFEREE_FAIL "+code)


def audit(source,out):
    p=Path(source);root=p.parent
    d=json.loads(p.read_text())
    check(d["upper_dag"]=="9/15" and d["km2"]=="PARTIAL","DAG")
    check(not d["production_ready"] and not d["merge_ready"] and not d["auto_next"],"FALSE_PROMOTION")
    check(set(d["data"])=={"GL12","GL16"},"GRID")
    maxima={"event_fourmoment_rel":0.,"rho_relative":0.,"centroid_abs":0.,
            "variance_abs":0.,"redwing_abs":0.,"quadrupole_abs":0.,
            "green_drift_monotonic_abs":0.,"spectral_hist_mass_relative":0.}
    observed_epochs=0;observed_events=0;spectra=0
    for label,case in d["data"].items():
        raw=root/case["packet_npz"]
        check(raw.is_file(),"MISSING_PACKET "+label)
        check(hashlib.sha256(raw.read_bytes()).hexdigest()==case["packet_npz_sha256"],"PACKET_SHA "+label)
        with np.load(raw,allow_pickle=False) as z:
            t=z["sample_times"];e=z["source_packets"];D=z["center_D"]
            sigma=z["doppler_sigma"];R=z["Rnode"];Ri=z["Rnode_H"]
            Rends=z["Rend"];Riends=z["Rend_H"];ww=z["emission_weight"]
            nn=z["emission_direction"];dt=z["time_quadrature_weights"]
            goal4=z["source_expected_fourforce"];ff=z["line_fraction"]
            rww=z["weights_epoch"];rnn=z["directions_epoch"]
            nray=case["rays"];order=case["time_order"]
            check(len(t)==40*order and e.shape==(len(t),nray),"PACKETS "+label)
            check(np.all(e>0) and np.all(sigma>0) and np.all(dt>0),"NEGATIVE_SOURCE "+label)
            check(np.all(ff>0) and np.all(ff<1),"BAD_BRANCH "+label)
            check(np.all(np.diff(Rends,axis=0)>0),"NONPOSITIVE_EXPANSION "+label)
            check(np.all(np.diff(Riends)>0),"NONPOSITIVE_H "+label)
            check(np.all(np.abs(np.linalg.norm(nn,axis=2)-1)<3e-12),"BAD_ORIGINAL_RAYS "+label)
            j=e/dt[:,None]
            observed4=np.column_stack([np.sum(ww*j,axis=1),
                                        np.einsum("tn,tni->ti",ww*j,nn)])
            maxima["event_fourmoment_rel"]=max(maxima["event_fourmoment_rel"],
                 float(np.max(np.abs(observed4-goal4)/np.maximum(1e-14,np.abs(goal4[:,0:1])))))
            observed_events+=len(t)
            for mode in ("shear","H_only"):
                records=case["scenarios"][mode]["epochs"]
                snaps=case["scenarios"][mode]["spectra"]
                check(len(records)==41 and len(snaps)==5,"EPOCH_COUNT "+label)
                for k in range(1,41):
                    observed_epochs+=1
                    cut=k*order
                    rr=Rends[k][None,:] if mode=="shear" else Riends[k]
                    rt=R[:cut] if mode=="shear" else Ri[:cut,None]
                    adv=rr-rt
                    check(np.min(adv)>-1e-12,"NEGATIVE_REDSHIFT_ADVANCE "+label)
                    ek=e[:cut]*np.exp(-4*adv)
                    yc=D[:cut]-adv
                    wt=rww[k][None,:]*ek
                    total=float(wt.sum())
                    mean=float(np.sum(wt*yc)/total)
                    second=float(np.sum(wt*(yc*yc+sigma[:cut,None]**2))/total)
                    width=math.sqrt(max(0.,second-mean*mean))
                    red=float(np.sum(wt*ndtr((-.01-yc)/sigma[:cut,None]))/total)
                    ang=np.sum(ek,axis=0)*rww[k]
                    qt=np.einsum("n,ni,nj->ij",ang,rnn[k],rnn[k])/total-np.eye(3)/3
                    qcalc=np.einsum("n,ni->i",ang,rnn[k])
                    record=records[k]
                    maxima["rho_relative"]=max(maxima["rho_relative"],abs(total/record["rho"]-1))
                    maxima["centroid_abs"]=max(maxima["centroid_abs"],abs(mean-record["mean_log_nu"]))
                    maxima["variance_abs"]=max(maxima["variance_abs"],abs(width-record["std_log_nu"]))
                    maxima["redwing_abs"]=max(maxima["redwing_abs"],abs(red-record["redwing_fraction"]))
                    maxima["quadrupole_abs"]=max(maxima["quadrupole_abs"],
                             float(np.max(np.abs(qt-np.asarray(record["quadrupole"])))) )
                    check(np.max(abs(qcalc-np.asarray(record["q"])))<1e-12,"LINE_MOMENTUM "+label)
                    check(0<total<z["full_photon_rho"][k],"TAGGED_DUPLICATE_STRESS "+label)
                for s in snaps:
                    spectra+=1
                    check(len(s["spectrum_energy_bins"])==1200,"HIST_BINS "+label)
                    h=np.asarray(s["spectrum_energy_bins"])
                    check(np.min(h)>=0,"NEGATIVE_HIST "+label)
                    maxima["spectral_hist_mass_relative"]=max(maxima["spectral_hist_mass_relative"],
                             float(abs(h.sum()/s["rho"]-1)))
            cons=case["conservation"]
            check(cons["max_Hamiltonian_norm"]<5e-8 and cons["max_momentum_norm"]<5e-8,
                  "PARENT_EINSTEIN_CONSTRAINT "+label)
    check(observed_epochs==160 and spectra==20 and observed_events==640,"COUNT")
    check(maxima["event_fourmoment_rel"]<2e-12,"EVENT_FOURMOMENT")
    check(maxima["rho_relative"]<1e-12,"GREEN_ENERGY")
    check(maxima["centroid_abs"]<1e-12,"FREQUENCY_CENTROID")
    check(maxima["variance_abs"]<1e-11,"DOPPLER_VARIANCE")
    check(maxima["redwing_abs"]<1e-12,"REDWING_FRACTION")
    check(maxima["quadrupole_abs"]<1e-11,"ANGULAR_LINE_QUAD")
    check(maxima["spectral_hist_mass_relative"]<2e-10,"FREQUENCY_HISTOGRAM")
    # Independent time quadrature vs analytic characteristic for constant H.
    H=.37;q0=2.5;u=.21
    xx,ww=np.polynomial.legendre.leggauss(64)
    tt=u*(xx+1)/2
    numerical=float(np.dot(ww*u/2,q0*np.exp(-4*H*(u-tt))))
    analytic=q0*(-math.expm1(-4*H*u))/(4*H)
    check(abs(numerical/analytic-1)<2e-14,"INDEPENDENT_STATIC_GREEN")
    results={"schema":"bass.km2k.saved_data_referee.v1",
             "source_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
             "imported_BASS_RHS":False,"optimizations_safe":True,
             "physical_epoch_nonzero":observed_epochs,"spectra":spectra,
             "sampled_source_events":observed_events,"maxima":maxima,
             "verdict":"PASS_SCOPED"}
    q=Path(out);q.parent.mkdir(parents=True,exist_ok=True)
    q.write_text(json.dumps(results,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("KM2K_HOSTILE_SAVED_DATA_AUDIT",results["verdict"],
          "epochs",observed_epochs,"events",observed_events,
          "max_moment_error",maxima["event_fourmoment_rel"],flush=True)
    return results


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    audit(a.source,a.output)
