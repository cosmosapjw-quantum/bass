"""KM2M: first polarized Thomson frequency gain on real BASS KM2L ballistic Lyalpha rays.

New first-collision collision *source*, not evolved post-scatter radiation.
Source-locked original tilted P8 rank-two projector and bulk Doppler map.
No extra Einstein or chemistry stress, and no repeated scattering.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.special import ndtr

from research.dual_lane_km2l_20261031.thomson_lya import (
    case_science, original_source_guards,
)
from research.dual_lane_km2k_20261031.escaping_lya import HIST_EDGES
from research.dual_lane_km2j_20261031.coupled_chem_p8 import CoupledChemicalP8
from tilted_collision import TiltedThomson, radiation_tensor

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
KM2L_HEAD = "8a1e09f6176166595b33810d3ce0c1f18afb245f"
KM2L_BLOB = "34933d752ae1888ac4eead17fb7d579a584add88"
OBS_EPOCHS = (8,16,24,32,40)
EDGES = HIST_EDGES.copy()
NBINS = len(EDGES)-1
STEP = float(EDGES[1]-EDGES[0])
MID = 0.5*(EDGES[1:]+EDGES[:-1])


def blob_sha(path):
    b = Path(path).read_bytes()
    return hashlib.sha1(f"blob {len(b)}\0".encode()+b).hexdigest()


def source_guards():
    sources = original_source_guards()
    path = ROOT / "research/dual_lane_km2l_20261031/thomson_lya.py"
    sha = blob_sha(path)
    if sha != KM2L_BLOB:
        raise ValueError(f"IMMUTABLE_KM2L_SOURCE_CHANGED {sha}")
    sources[str(path.relative_to(ROOT))] = sha
    return sources


def electron_frame_gaussian_histogram(amp_normal, centers_normal,
                                       widths, D, *, edges=EDGES):
    """Exact narrow Maxwell-Gaussian CDF bin integrals of normal -> rest E^4.

    Photon bin energy is I_nu*nu dlnnu, so electron-rest
    total packet energy transforms by D^4 and y_rest=y_normal+ln D.
    The Gaussian wings are retained with a 5-bin local CDF stencil
    that is error-checked against the exact total packet energy.
    """
    amp_normal = np.asarray(amp_normal,float)
    centers_normal = np.asarray(centers_normal,float)
    widths = np.asarray(widths,float)
    D = np.asarray(D,float)
    if amp_normal.shape != centers_normal.shape or amp_normal.ndim != 2:
        raise ValueError("spectral packet shapes mismatch")
    count,N = amp_normal.shape
    nb=len(edges)-1
    if widths.shape != (count,) or D.shape != (N,):
        raise ValueError("spectral widths and rays mismatch")
    if min(widths)<=0 or min(D)<=0 or min(amp_normal.flat)<0:
        raise ValueError("nonphysical first-scatter source")
    step=float(edges[1]-edges[0])
    if not np.allclose(np.diff(edges),step,atol=1e-14,rtol=1e-13):
        raise ValueError("frequency grid not uniformly source-resolved")
    centers = centers_normal + np.log(D)[None,:]
    sig = np.broadcast_to(widths[:,None],centers.shape)
    if np.any(centers<edges[0]+12*sig) or np.any(centers>edges[-1]-12*sig):
        raise ValueError("electron frame frequency grid truncates real packets")
    norm = amp_normal * D[None,:]**4
    floor=np.floor((centers-edges[0])/step).astype(int)
    id_ray=np.broadcast_to(np.arange(N,dtype=int)[None,:],centers.shape)
    accum=np.zeros(N*nb,float)
    # Normal physical Maxwell width (~1e-5) is far narrower than 1200-bin
    # source window (8.333e-4). Exact CDF, not a fitted delta source.
    for jump in (-2,-1,0,1,2):
        k=floor+jump
        mask=(k>=0)&(k<nb)
        ix=k[mask]
        prob=ndtr((edges[ix+1]-centers[mask])/sig[mask])-ndtr(
             (edges[ix]-centers[mask])/sig[mask])
        if np.any(prob<-1e-14):
            raise ArithmeticError("negative physical Gaussian measure")
        accum += np.bincount((id_ray[mask]*nb+ix).astype(int),
                            weights=norm[mask]*prob,minlength=N*nb)
    out=accum.reshape(N,nb)
    err=abs(out.sum()/norm.sum()-1.)
    if err>5e-12:
        raise ArithmeticError(f"rest Doppler line energy missing {err}")
    return out,float(err)


def normal_frequency_spectrum(gain_rate_by_ray_e, D, weights):
    """Source-conservative cold-electron bulk-Doppler remap y_n=y_e-lnDout.

    Splits electron-bin point samples between adjacent normal-bin centres:
    exact zero/first frequency-bin moments on its adopted discrete grid.
    """
    x=np.asarray(gain_rate_by_ray_e,float)
    D=np.asarray(D,float)
    w=np.asarray(weights,float)
    N,nb=x.shape
    if nb!=NBINS or D.shape!=(N,) or w.shape!=(N,):
        raise ValueError("gain frequency remap shape mismatch")
    y=MID[None,:]-np.log(D)[:,None]
    coordinate=(y-(MID[0]))/STEP
    lo=np.floor(coordinate).astype(int)
    frac=coordinate-lo
    if lo.min()<0 or lo.max()+1>=nb:
        raise ValueError("bulk Doppler remap escapes physical frequency window")
    weighted=x*w[:,None]
    flattened=np.arange(N*nb)
    out=np.bincount(lo.ravel(),weights=(weighted*(1-frac)).ravel(),minlength=nb)
    out+=np.bincount((lo+1).ravel(),weights=(weighted*frac).ravel(),minlength=nb)
    err=abs(out.sum()/weighted.sum()-1.)
    if err>5e-13:
        raise ArithmeticError("normal spectral remap lost source energy")
    return out,float(err)


def scattering_gain_snapshot(model,sol,packet,opacity,k,*,save_source=None):
    """One actual time/angle/frequency resolved polarized P8 first-gain source."""
    if k not in OBS_EPOCHS:
        raise ValueError("snapshots must use source-owned real KM2K epochs")
    u=k*model.end/40.
    d=model.fields(u,sol.sol(u),False)
    N=model.N
    op=TiltedThomson(d["n"],d["w"],d["beta"])
    if abs(d["nu"]-d["nH"]*d["x"]*6.6524587051e-29*
           299792458.0*model.parent.Tstar_seconds)>1e-10:
        raise ArithmeticError("physical Thomson dimensional rate mismatch")
    timeorder=8
    cut=k*timeorder
    attenuation=np.maximum(0.,opacity["tau_edges"][k][None,:]-
                              opacity["tau_nodes"][:cut])
    drift=packet["Rend"][k][None,:]-packet["Rnode"][:cut]
    if np.min(drift)<-2e-12:
        raise ArithmeticError("redshift frequency characteristic inconsistent")
    lab_packet=packet["source_packets"][:cut]*np.exp(-4*drift-attenuation)
    mu=packet["center_D"][:cut]-drift
    therm=packet["doppler_sigma"][:cut]
    if np.min(lab_packet)<=0:
        raise ArithmeticError("zero or negative ballistic source packet")
    hist_e,packet_gap=electron_frame_gaussian_histogram(
         lab_packet,mu,therm,op.D)
    # Original electron-frame P8 source with polarized projector.
    # Since original tagged radiation is unpolarized, J_e=.5 I_e Pe.
    M_e=0.5*np.einsum("n,nb,nij->bij",op.we,hist_e,op.Pe)
    M_total=M_e.sum(axis=0)
    if np.max(abs(M_total-M_total.T))>1e-13:
        raise ArithmeticError("electron source coherency not symmetric")
    # Positive original incident coherent spectrum gives PSD 3x3 source.
    if np.min(np.linalg.eigvalsh(M_total))<-1e-13*max(1.,np.trace(M_total)):
        raise ArithmeticError("negative electron-frame Thomson polarization source")
    c=3./(8.*math.pi)
    trace_gain_e=c*np.einsum("nij,bij->nb",op.Pe,M_e)
    # Actual Doppler-transformed normal gain rate from source-locked P8:
    # nu_rest*D * D^-4 * J_gain,e = nu_rest D^-3 J_gain,e.
    gain_normal_by_ray_bin = d["nu"]*op.D[:,None]**(-3)*trace_gain_e
    loss_normal_by_ray=d["nu"]*op.D*lab_packet.sum(axis=0)
    gain_normal_by_ray=gain_normal_by_ray_bin.sum(axis=1)
    # Compare against the ACTUAL original source P8 gain, not a scalar model.
    projection=np.eye(3)[None,:,:]-np.einsum("ni,nj->nij",op.n,op.n)
    J0_n=0.5*lab_packet.sum(axis=0)[:,None,None]*projection
    actual_gain_n=op.gain(J0_n)
    original_normal_gain=d["nu"]*op.D*np.trace(actual_gain_n,axis1=1,axis2=2)
    parity=np.max(abs(gain_normal_by_ray-original_normal_gain)) / max(
          abs(original_normal_gain).max(),1e-300)
    if parity>=3e-10:
        raise ArithmeticError(f"frequency-integrated first P8 gain parity {parity}")
    # Electron-rest bolometric energy must be conserved in Thomson limit,
    # separately from normal-frame electron bulk-work exchange.
    incident_e=float(np.dot(op.we,hist_e.sum(axis=1)))
    produced_e=float(np.dot(op.we,trace_gain_e.sum(axis=1)))
    rest_gap=abs(produced_e/incident_e-1.)
    if rest_gap>=5e-6:
        raise ArithmeticError(f"rest Thomson electron energy source gap {rest_gap}")
    energy_loss=float(np.dot(op.w,loss_normal_by_ray))
    energy_gain=float(np.dot(op.w,gain_normal_by_ray))
    moment_loss=np.einsum("n,ni->i",op.w*loss_normal_by_ray,op.n)
    moment_gain=np.einsum("n,ni->i",op.w*gain_normal_by_ray,op.n)
    if energy_gain<=0 or energy_loss<=0:
        raise ArithmeticError("nonphysical negative first-gain source")
    # Build the integrated real symmetric polarization tensor in rest frame.
    J_e_bol=c*np.einsum("nik,kl,nlj->nij",op.Pe,M_total,op.Pe)
    tr=np.trace(J_e_bol,axis1=1,axis2=2)
    tr2=np.einsum("nij,nji->n",J_e_bol,J_e_bol)
    pi=np.sqrt(np.maximum(0.,2*tr2-tr**2))/np.maximum(tr,1e-300)
    if np.max(pi)>1+1e-9:
        raise ArithmeticError("unphysical first-Thomson polarization degree")
    weight=op.we*tr
    mean_pi=float(np.dot(weight,pi)/sum(weight))
    rms_pi=float(np.sqrt(np.dot(weight,pi**2)/sum(weight)))
    max_pi=float(pi.max())
    electron_edges_spectrum=d["nu"]*np.einsum("n,nb->b",op.we,trace_gain_e)
    normal_bins,bingap=normal_frequency_spectrum(gain_normal_by_ray_bin,
                                                  op.D,op.w)
    centroid_e=float(np.dot(electron_edges_spectrum,MID)/
                     electron_edges_spectrum.sum())
    centroid_n=float(np.dot(normal_bins,MID)/normal_bins.sum())
    # Source is a differential-in-time injection: not evolved J1 yet.
    first_rate_reference=float(energy_loss)
    input_q=np.r_[energy_loss,moment_loss]
    output_q=np.r_[energy_gain,moment_gain]
    result={
      "u":float(u),"n_theta":int(model.ntheta),"rays":int(N),
      "source_balanced_original_KM2J":True,
      "incoming_ballistic_tagged_rho":float(np.dot(op.w,lab_packet.sum(axis=0))),
      "incoming_first_event_energy_rate":energy_loss,
      "normal_first_gain_energy_rate":energy_gain,
      "normal_first_gain_fourmom":output_q.tolist(),
      "normal_ballistic_loss_fourmom":input_q.tolist(),
      "normal_net_scatter_fourmom":(output_q-input_q).tolist(),
      "normal_gain_over_loss":energy_gain/energy_loss,
      "electron_rest_source_gain_relative_error":float(rest_gap),
      "P8_gain_bolometric_parity_relative_error":float(parity),
      "electron_rest_input_energy":incident_e,
      "electron_rest_output_energy":produced_e,
      "frequency_packet_CDF_error":float(packet_gap),
      "normal_frequency_remap_energy_error":float(bingap),
      "electron_rest_scattered_logfrequency_centroid":centroid_e,
      "normal_scattered_logfrequency_centroid":centroid_n,
      "linear_polarization_mean":mean_pi,
      "linear_polarization_rms":rms_pi,
      "linear_polarization_max":max_pi,
      "incoming_electron_frame_spectrum":(d["nu"]*
          np.einsum("n,nb->b",op.we,hist_e)).tolist(),
      "gained_electron_frame_spectrum":electron_edges_spectrum.tolist(),
      "gained_normal_frame_spectrum":normal_bins.tolist(),
      "normal_gain_angle_energy":gain_normal_by_ray.tolist(),
      "normal_loss_angle_energy":loss_normal_by_ray.tolist(),
      "normal_gain_linear_polarization_fraction":pi.tolist(),
    }
    if save_source is not None:
        dest=Path(save_source)
        dest.parent.mkdir(parents=True,exist_ok=True)
        np.savez_compressed(dest,
            M_e_frequency=M_e,
            n_normal=op.n,w_normal=op.w,
            n_electron=op.ne,w_electron=op.we,
            S=op.S,D=op.D,Pe=op.Pe,
            source_nu_rest=np.array([d["nu"]]),
            incoming_ballistic_per_ray=lab_packet.sum(axis=0),
            incoming_rest_frequency_bin=hist_e,
            first_gain_e_frequency_trace=trace_gain_e,
            first_gain_normal_frequency= gain_normal_by_ray_bin,
            first_gain_normal_bolometric_tensor=
                 d["nu"]*op.D[:,None,None]*actual_gain_n,
            original_normal_frequency_edges=EDGES,
            electron_frequency_source=M_e)
        result["factorized_source_file"]=dest.name
        result["factorized_source_sha256"]=hashlib.sha256(dest.read_bytes()).hexdigest()
    else:
        result["factorized_source_file"]=None
        result["factorized_source_sha256"]=None
    return result


def run_science(output,orders=(12,16)):
    sources=source_guards()
    path=Path(output)
    path.parent.mkdir(parents=True,exist_ok=True)
    all_cases={}
    for n in orders:
        # Restores the same actual original Einstein-P8-Peebles IVP and
        # its KM2L zero-scatter trajectories and physical first-event source.
        reference=case_science(n,path.parent,order=8,end=.25)
        parent=CoupledChemicalP8(ntheta=n,end=.25,chem_energy=True)
        solution=parent.solve(rtol=1e-11,atol=1.5e-13)
        files=[path.parent/reference["KM2K_original_packets_file"],
               path.parent/reference["thomson_opacity_file"]]
        with np.load(files[0],allow_pickle=False) as z:
            physical={k:z[k].copy() for k in z.files}
        with np.load(files[1],allow_pickle=False) as z:
            optical={k:z[k].copy() for k in z.files}
        measurements=[]
        for k in OBS_EPOCHS:
            out=path.parent/f"KM2M_GAIN_FACTOR_GL{n}_STEP{k}.npz" if k==40 else None
            rec=scattering_gain_snapshot(parent,solution,physical,optical,k,
                                          save_source=out)
            first=reference["scenarios"]["shear_thomson"]["epochs"][k]["first_collision_energy_rate"]
            ratio=abs(rec["incoming_first_event_energy_rate"]/first-1.)
            if ratio>4e-10:
                raise ArithmeticError("original KM2L true first-event collision source mismatch "+str(ratio))
            rec["original_KM2L_first_rate_relative_error"]=ratio
            measurements.append(rec)
        final=measurements[-1]
        all_cases[f"GL{n}"]={
            "n_theta":int(n),
            "actual_original_joint_IVP_reintegrations":3,
            "source_KM2L_initial_J_sha256":reference["inherited_initial_J_SHA256"],
            "original_joint_IVP_RHS_evals":reference["joint_original_parent_rhs_calls"]+
                                           [int(solution.nfev)],
            "source_KM2L_packet_sha256":reference["KM2K_original_packets_sha256"],
            "source_KM2L_opacity_sha256":reference["thomson_opacity_sha256"],
            "parent_Einstein_conservation":reference["reintegrated_KM2J_conservation"],
            "measurements":measurements,
        }
        print("KM2M_POLARIZED_THOMSON_FIRST_GAIN",n,
              "in",final["incoming_first_event_energy_rate"],
              "gain",final["normal_first_gain_energy_rate"],
              "rest_gap",final["electron_rest_source_gain_relative_error"],
              "mean_linear_polarization",final["linear_polarization_mean"],
              "centroid_n",final["normal_scattered_logfrequency_centroid"],
              "P8_parity",final["P8_gain_bolometric_parity_relative_error"],flush=True)
    ans={
        "schema":"bass.km2m.first_polarized_thomson_frequency_source.v1",
        "immutable_parent_PR":294,
        "immutable_parent_HEAD":KM2L_HEAD,
        "source_blobs":sources,
        "metric":"(-,+,+,+)",
        "physics":"actual original Einstein/P8/Peebles/KM2L ballistic Lyalpha first scattering P8 rank-2 polarized gain source with electron-frame elastic frequency and relativistic bulk-Doppler angular remapping",
        "scope":"INSTANTANEOUS_FIRST_COLLISION_GAIN_SOURCE_NOT_PROPAGATED_SCATTERED_RADIATION",
        "frequencies_per_snapshot":NBINS,
        "original_physical_scatter_epochs_per_grid":len(OBS_EPOCHS),
        "snapshots":all_cases,
        "frequency_bin_edges":EDGES.tolist(),
        "upper_dag":"9/15","upper_edges":21,"KM2":"PARTIAL",
        "new_completed_upper_nodes":0,
        "KM2M_scoped_status":"PENDING_CI",
        "production_ready":False,"merge_ready":False,"auto_next":False,
        "native_subagent":"NOT_RUN","distinct_author_R6_C9":"NOT_RUN",
        "not_implemented":[
            "time propagation of first-scattered radiation",
            "second and higher Thomson scattering events",
            "frequency transfer with electron thermal Compton effect",
            "resonant Lyalpha atomic recoil redistribution or 2p populations",
            "backreaction of tagged source on Einstein or chemistry",
            "observational cosmological CMB spectrum",
            "angular continuum certificate"
        ]}
    path.write_text(json.dumps(ans,sort_keys=True,indent=2,allow_nan=False)+"\n")
    return ans


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--orders",default="12,16")
    args=p.parse_args()
    run_science(args.output,tuple(map(int,args.orders.split(","))))
