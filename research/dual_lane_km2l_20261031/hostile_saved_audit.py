"""KM2L independent saved-data hostile audit; never imports BASS RHS.

Analytically reconstructs the Thomson survival probability, 240 nonzero
frequency-resolved epochs, first-collision event moments, 30 spectra and
independent constant-medium Green function. Exception checks survive -O.
"""
from __future__ import annotations

import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from scipy.special import ndtr
from numpy.polynomial.legendre import leggauss


def ensure(ok,issue):
    if not bool(ok):
        raise ArithmeticError("KM2L_INDEPENDENT_PHYSICS_FAIL " + issue)


def audit(source,output):
    p=Path(source)
    evidence=json.loads(p.read_text())
    ensure(evidence["upper_dag"]=="9/15" and evidence["new_completed_upper_nodes"]==0,"DAG")
    ensure(not evidence["production_ready"] and not evidence["merge_ready"],"FALSE_PRODUCTION")
    ensure(set(evidence["cases"])=={"GL12","GL16"},"GRID")
    maxima={"optical_integral_abs":0.,"green_energy_relative":0.,
            "centroid_abs":0.,"redwing_abs":0.,"first_scatter_rate_abs":0.,
            "first_scatter_momentum_abs":0.,"survival_ratio_abs":0.,
            "spectral_hist_relative":0.,"parent_zero_scatter_relative":0.}
    epochs=0;events=0;histograms=0
    for name,case in evidence["cases"].items():
        root=p.parent
        packet=root/case["KM2K_original_packets_file"]
        opacity=root/case["thomson_opacity_file"]
        ensure(packet.is_file() and opacity.is_file(),"MISSING_SOURCE "+name)
        ensure(hashlib.sha256(packet.read_bytes()).hexdigest()==case["KM2K_original_packets_sha256"],
               "SOURCE_KM2K_SHA "+name)
        ensure(hashlib.sha256(opacity.read_bytes()).hexdigest()==case["thomson_opacity_sha256"],
               "SOURCE_OPACITY_SHA "+name)
        with np.load(packet,allow_pickle=False) as z, np.load(opacity,allow_pickle=False) as opt:
            event=z["source_packets"];logD=z["center_D"];sig=z["doppler_sigma"]
            R=z["Rnode"];RH=z["Rnode_H"];RE=z["Rend"];REH=z["Rend_H"]
            raydirs=z["directions_epoch"];weights=z["weights_epoch"]
            fullrho=z["full_photon_rho"];rays=event.shape[1]
            tau=opt["tau_nodes"];tauE=opt["tau_edges"];haz=opt["hazard_nodes"]
            hazE=opt["hazard_edges"]
            order=len(haz)//40
            ensure(event.shape==(40*order,rays),"SOURCE_PACKET_SHAPE "+name)
            ensure(np.min(event)>0 and np.min(haz)>0 and np.min(hazE)>0,"NO_PHYSICAL_SOURCE "+name)
            ensure(np.min(np.diff(tauE,axis=0))>0,"NEGATIVE_TAU "+name)
            nodes,glw=leggauss(order)
            delta_u=.25/40
            for j in range(40):
                integral=delta_u/2*(glw@haz[j*order:(j+1)*order])
                gap=np.max(abs(tauE[j+1]-tauE[j]-integral))
                maxima["optical_integral_abs"]=max(maxima["optical_integral_abs"],float(gap))
            events+=len(haz)
            for mode in ("shear_thomson","shear_free","Honly_thomson"):
                data=case["scenarios"][mode]
                ensure(len(data["epochs"])==41 and len(data["spectra"])==5,"HIST_OR_EPOCH "+name)
                for k in range(1,41):
                    epochs+=1
                    cut=k*order
                    if mode=="Honly_thomson":
                        delt=REH[k]-RH[:cut,None]
                    else:
                        delt=RE[k][None,:]-R[:cut]
                    ensure(np.min(delt)>=-2e-12,"NEGATIVE_GEODESIC_REDSHIFT "+name)
                    optical=np.maximum(0.,tauE[k][None,:]-tau[:cut])
                    survive=np.ones_like(optical) if mode=="shear_free" else np.exp(-optical)
                    pkg=event[:cut]*np.exp(-4*delt)*survive
                    cent=logD[:cut]-delt
                    weighted=pkg*weights[k][None,:]
                    rho=float(weighted.sum())
                    yy=float(np.sum(weighted*cent)/rho)
                    var=float(np.sum(weighted*(cent**2+sig[:cut,None]**2))/rho-yy**2)
                    red=float(np.sum(weighted*ndtr((-.01-cent)/sig[:cut,None]))/rho)
                    red=min(1.,max(0.,red))
                    r_energy=pkg.sum(axis=0)
                    event_by_ray=hazE[k]*r_energy if mode!="shear_free" else np.zeros_like(r_energy)
                    first_rate=float(weights[k]@event_by_ray)
                    first_q=np.einsum("i,ij->j",weights[k]*event_by_ray,raydirs[k])
                    baseline=float(np.sum(event[:cut]*np.exp(-4*delt)*weights[k][None,:]))
                    frac=rho/baseline
                    rec=data["epochs"][k]
                    maxima["green_energy_relative"]=max(maxima["green_energy_relative"],
                        abs(rho/rec["rho"]-1))
                    maxima["centroid_abs"]=max(maxima["centroid_abs"],abs(yy-rec["mean_log_nu"]))
                    maxima["redwing_abs"]=max(maxima["redwing_abs"],abs(red-rec["redwing_fraction"]))
                    maxima["first_scatter_rate_abs"]=max(maxima["first_scatter_rate_abs"],
                        abs(first_rate-rec["first_collision_energy_rate"]))
                    maxima["first_scatter_momentum_abs"]=max(maxima["first_scatter_momentum_abs"],
                        float(np.max(abs(first_q-np.asarray(rec["first_collision_momentum_rate"])))) )
                    maxima["survival_ratio_abs"]=max(maxima["survival_ratio_abs"],
                        abs(frac-rec["mean_packet_survival"]))
                    ensure(0<rho<fullrho[k],"NOT_A_SUBSET_OF_EXISTING_P8 "+name)
                    ensure(var>=-1e-13,"NEGATIVE_FREQUENCY_VARIANCE "+name)
                    ensure(frac<=1+1e-12,"NEGATIVE_THOMSON_LOSS "+name)
                for s in data["spectra"]:
                    histograms+=1
                    x=np.asarray(s["spectrum_energy_bins"])
                    ensure(len(x)==1200 and np.min(x)>=0,"BAD_SPECTRAL_HIST "+name)
                    maxima["spectral_hist_relative"]=max(
                        maxima["spectral_hist_relative"],float(abs(x.sum()/s["rho"]-1)))
            free=case["scenarios"]["shear_free"]["epochs"][-1]
            atten=case["scenarios"]["shear_thomson"]["epochs"][-1]
            ensure(atten["rho"]<free["rho"],"THOMSON_HAS_NO_ATTENUATION "+name)
            ensure(atten["first_collision_energy_rate"]>0,"NO_FIRST_SCATTER "+name)
    ensure(epochs==240 and events==640 and histograms==30,"CARDINALITY")
    ensure(maxima["optical_integral_abs"]<2e-12,"THOMSON_TAU_ODE")
    ensure(maxima["green_energy_relative"]<3e-12,"GREEN_ENERGY")
    ensure(maxima["centroid_abs"]<3e-12,"FREQUENCY_CENTROID")
    ensure(maxima["redwing_abs"]<2e-12,"FREQUENCY_CDF")
    ensure(maxima["first_scatter_rate_abs"]<2e-12,"FIRST_COLLISION_RATE")
    ensure(maxima["first_scatter_momentum_abs"]<2e-12,"FIRST_COLLISION_DIRECTION")
    ensure(maxima["survival_ratio_abs"]<3e-12,"THOMSON_SURVIVAL_PROB")
    ensure(maxima["spectral_hist_relative"]<2e-10,"SPECTRUM_HIST_NORMALIZATION")
    # Independent positive analytic constant-medium check, not imported original RHS.
    x,w=leggauss(64)
    h=.37;rate=8.6;j0=2.4;t=.25
    ts=t*(x+1)/2
    measured=np.dot(w*t/2,j0*np.exp(-(4*h+rate)*(t-ts)))
    expected=j0*(-math.expm1(-(4*h+rate)*t))/(4*h+rate)
    ensure(abs(measured/expected-1)<2e-14,"CONSTANT_THOMSON_GREEN")
    output=Path(output);output.parent.mkdir(exist_ok=True,parents=True)
    receipt={"schema":"bass.km2l.independent_saved_ballistic_scattering.v1",
             "source_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
             "no_BASS_RHS_import":True,"python_O_safe":True,
             "nonzero_physics_epochs":epochs,"source_hazard_events":events,
             "frequency_snapshots":histograms,"maxima":maxima,
             "verdict":"PASS_SCOPED"}
    output.write_text(json.dumps(receipt,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("KM2L_HOSTILE_SAVED_AUDIT",receipt["verdict"],
          "epochs",epochs,"events",events,
          "max_tau_integral_abs",maxima["optical_integral_abs"],flush=True)
    return receipt


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--source",type=Path,required=True)
    a.add_argument("--output",type=Path,required=True)
    z=a.parse_args();audit(z.source,z.output)
