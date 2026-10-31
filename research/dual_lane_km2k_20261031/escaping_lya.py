"""KM2K: actual frequency-resolved escaped-Lyalpha photon characteristics.

Runs original KM2J Einstein + full polarized P8 + Peebles joint IVPs;
this is a *tagged* spectral decomposition of its EXISTING chemical grey source.
No duplicate T_munu, no new chemistry feedback, no resonant Fokker-Planck.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from research.dual_lane_km2j_20261031.coupled_chem_p8 import (
    CoupledChemicalP8, angular_grey_emission, guard_all, PARENT_HEAD,
)
from research.dual_lane_km2i_20261031.lya_peebles import (
    K_B,E_ALPHA_EV,CHI_H_EV,TWO_PHOTON,
)
from research.dual_lane_km2g_20261030.neutral_baryons import (
    M_E_KG,M_P_KG,C_M_S,
)
from research.dual_lane_km2k_20261031.frequency_core import (
    partial_gauss_integration, summarize_packets, gaussian_bin_histogram,
)
HERE=Path(__file__).resolve().parent
REPO_ROOT=HERE.parents[1]
KM2J_HEAD="63147c01f1b1fd3f0cf698c919db25d9bd2ef80b"
KM2J_CODE_BLOB="2bf86d6d48cd95177b55db12f78e89c69ddfd1dd"
N_WINDOWS=40
SPECTRUM_EPOCHS=(8,16,24,32,40)
HIST_EDGES=np.linspace(-.5,.5,1201)
MAX_SOURCE_MOMENT_GAP=2e-12


def gitblob(path):
    raw=Path(path).read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest()


def exact_parent_sources():
    r=guard_all()
    p=REPO_ROOT/"research/dual_lane_km2j_20261031/coupled_chem_p8.py"
    sh=gitblob(p)
    if sh!=KM2J_CODE_BLOB:
        raise ValueError(f"IMMUTABLE_KM2J_SOURCE_CHANGED {sh}")
    r[str(p.relative_to(REPO_ROOT))]=sh
    return r


def evaluate_grid(ntheta, *, order=8, end=.25,output_dir=None,
                  save_packets=True,make_hist=True):
    m=CoupledChemicalP8(ntheta=ntheta,end=end,chem_energy=True)
    sol=m.solve(rtol=1e-11,atol=1.5e-13)
    ray_count=m.N
    nodes,gweights,partial=partial_gauss_integration(order)
    endpts=np.linspace(0,end,N_WINDOWS+1)
    nt=N_WINDOWS*order
    Rnode=np.zeros((nt,ray_count))
    Rnode_H=np.zeros(nt)
    Rend=np.zeros((N_WINDOWS+1,ray_count))
    Rend_H=np.zeros(N_WINDOWS+1)
    src_packets=np.zeros((nt,ray_count))
    center_D=np.zeros((nt,ray_count))
    doppler_sigma=np.zeros(nt)
    line_fraction=np.zeros(nt)
    source_moment_error=np.zeros(nt)
    source_energy_rate=np.zeros(nt)
    source_expected_fourforce=np.zeros((nt,4))
    time_quadrature_weights=np.zeros(nt)
    sample_times=np.zeros(nt)
    emission_weight=np.zeros((nt,ray_count))
    emission_direction=np.zeros((nt,ray_count,3))
    directions_epoch=np.zeros((N_WINDOWS+1,ray_count,3))
    weights_epoch=np.zeros((N_WINDOWS+1,ray_count))
    full_photon_rho=np.zeros(N_WINDOWS+1)
    x_epoch=np.zeros(N_WINDOWS+1)
    H_epoch=np.zeros(N_WINDOWS+1)
    max_thomson_err=0.
    for k,u in enumerate(endpts):
        d=m.fields(float(u),sol.sol(float(u)),False)
        directions_epoch[k]=d["n"]
        weights_epoch[k]=d["w"]
        full_photon_rho[k]=d["rho_gamma"]
        x_epoch[k]=d["x"]
        H_epoch[k]=d["H"]
        if np.min(directions_epoch[k]@np.array([0.,0.,0.])+1.)<=0:
            raise ArithmeticError("invalid ray representation")
    for j in range(N_WINDOWS):
        width=endpts[j+1]-endpts[j]
        tvals=endpts[j]+width*(nodes+1)/2
        hh=np.zeros((order,ray_count))
        hh0=np.zeros(order)
        for k,t in enumerate(tvals):
            d=m.fields(float(t),sol.sol(float(t)),False)
            idx=j*order+k
            gamma=d["gamma"];beta=d["beta"]
            ray_n=d["n"];ww=d["w"]
            shearprojection=np.einsum("ni,ij,nj->n",ray_n,d["sigma"],ray_n)
            hh[k]=d["H"]+shearprojection;hh0[k]=d["H"]
            if np.min(hh[k])<=0:raise ArithmeticError("nonexpanding ray invalid post-Sobolev model")
            if d["xprime"]>=0 or d["chem_rest_source"]<=0:
                raise ValueError("net recombination and positive chemical emissivity required")
            linebranch=d["lambda_lya"]/(d["lambda_lya"]+TWO_PHOTON)
            f=(E_ALPHA_EV/CHI_H_EV)*linebranch
            if not 0<f<1:raise ArithmeticError("line energy partition out of range")
            src,force,gap,lo,hi=angular_grey_emission(ray_n,ww,beta,d["chem_rest_source"])
            jray=f*np.trace(src,axis1=1,axis2=2)
            if np.min(jray)<=0:raise ArithmeticError("negative tagged photon source")
            direct4=np.r_[float(ww@jray),np.einsum("n,ni->i",ww*jray,ray_n)]
            expected4=f*force
            gap4=np.max(np.abs(direct4-expected4))/max(abs(expected4).max(),1e-300)
            if gap4>MAX_SOURCE_MOMENT_GAP:raise ArithmeticError("escaping photon source fourmoment mismatch")
            D=1/(gamma*(1-ray_n@beta))
            if np.min(D)<=0:raise ArithmeticError("unphysical normal-to-baryon Doppler")
            sig=math.sqrt(K_B*d["Tm"]/((M_E_KG+M_P_KG)*C_M_S**2))
            line_fraction[idx]=f
            doppler_sigma[idx]=sig
            center_D[idx]=np.log(D)
            source_energy_rate[idx]=float(direct4[0])
            source_expected_fourforce[idx]=expected4
            time_quadrature_weights[idx]=width/2*gweights[k]
            source_moment_error[idx]=float(gap4)
            src_packets[idx]=jray*(width/2*gweights[k])
            sample_times[idx]=float(t)
            emission_weight[idx]=ww
            emission_direction[idx]=ray_n
        Rnode[j*order:(j+1)*order] = Rend[j][None,:]+(width/2)*(partial@hh)
        Rnode_H[j*order:(j+1)*order]=Rend_H[j]+(width/2)*(partial@hh0)
        Rend[j+1]=Rend[j]+(width/2)*(gweights@hh)
        Rend_H[j+1]=Rend_H[j]+(width/2)*float(gweights@hh0)
    # All actual physical trajectories are independently integrated at this level.
    data_modes={}
    for mode in ("shear","H_only"):
        res=[]
        spectral=[]
        for k,u in enumerate(endpts):
            if k==0:
                res.append({"u":0.,"rho":0.,"q":[0.,0.,0.],
                            "mean_log_nu":None,"std_log_nu":None,
                            "redwing_fraction":None,"quadrupole_frob":None,
                            "ratio_to_P8_rho":0.,"x_e":float(x_epoch[0]),
                            "H":float(H_epoch[0]),"line_ray_min":0.,"line_ray_max":0.})
                continue
            cut=k*order
            if mode=="shear":
                rnow=Rend[k]
                rsrc=Rnode[:cut]
            else:
                rnow=np.full(ray_count,Rend_H[k])
                rsrc=Rnode_H[:cut,None]
            delta=rnow[None,:]-rsrc
            if np.min(delta)<-1e-12:raise ArithmeticError("negative photon redshift advance")
            packet_energy=src_packets[:cut]*np.exp(-4*delta)
            means=center_D[:cut]-delta
            sig=doppler_sigma[:cut]
            stats=summarize_packets(means,sig,packet_energy,
                                    directions_epoch[k],weights_epoch[k])
            rays=stats.pop("ray_energy")
            stats.update({"u":float(u),"x_e":float(x_epoch[k]),"H":float(H_epoch[k]),
                          "ratio_to_P8_rho":stats["rho"]/float(full_photon_rho[k]),
                          "line_ray_min":float(rays.min()),"line_ray_max":float(rays.max())})
            if not 0<stats["rho"]<full_photon_rho[k]:
                raise ArithmeticError("tagged line photons exceed existing P8 field")
            res.append(stats)
            if make_hist and k in SPECTRUM_EPOCHS:
                hist,gap=gaussian_bin_histogram(means,sig,packet_energy,
                                               weights_epoch[k],HIST_EDGES)
                if gap>=2e-11:raise ArithmeticError("Gaussian spectrum dropped photon energy")
                spectral.append({"u":float(u),"mean_log_nu":stats["mean_log_nu"],
                                 "rho":stats["rho"],"histogram_loss_relative":gap,
                                 "spectrum_energy_bins":hist.tolist()})
        data_modes[mode]={"epochs":res,"spectra":spectral}
    comparison=[]
    for k in range(N_WINDOWS+1):
        a=data_modes["shear"]["epochs"][k];b=data_modes["H_only"]["epochs"][k]
        comparison.append({"u":a["u"],
            "rho_shear_minus_H_only":a["rho"]-b["rho"],
            "log_nu_centroid_shear_minus_H_only":None if k==0 else
                    a["mean_log_nu"]-b["mean_log_nu"],
            "redwing_fraction_shear_minus_H_only":None if k==0 else
                    a["redwing_fraction"]-b["redwing_fraction"]})
    conservation=m.conservation(sol,order=24)
    if conservation["max_Hamiltonian_norm"]>5e-8 or conservation["max_momentum_norm"]>5e-8:
        raise ArithmeticError("inherited coupled Einstein constraint fails")
    if conservation["hamiltonian_propagation_error"]>5e-8 or conservation["momentum_integrated_error"]>5e-8:
        raise ArithmeticError("inherited Einstein constraint propagation fails")
    if save_packets:
        p=Path(output_dir)/f"KM2K_PACKETS_GL{ntheta}_GLT{order}.npz"
        p.parent.mkdir(parents=True,exist_ok=True)
        np.savez_compressed(p,sample_times=sample_times,
            Rnode=Rnode,Rnode_H=Rnode_H,Rend=Rend,Rend_H=Rend_H,
            source_packets=src_packets,center_D=center_D,
            doppler_sigma=doppler_sigma,line_fraction=line_fraction,
            source_energy_rate=source_energy_rate,source_moment_error=source_moment_error,
            source_expected_fourforce=source_expected_fourforce,
            time_quadrature_weights=time_quadrature_weights,
            emission_weight=emission_weight,emission_direction=emission_direction,
            directions_epoch=directions_epoch,weights_epoch=weights_epoch,
            full_photon_rho=full_photon_rho,x_epoch=x_epoch,H_epoch=H_epoch)
        packet_name=p.name
        packet_sha=hashlib.sha256(p.read_bytes()).hexdigest()
    else:packet_name=None;packet_sha=None
    return {"ntheta":ntheta,"rays":ray_count,"time_order":order,
        "source_guard_count":len(m.initial_source),"parent_joint_ivp_nfev":int(sol.nfev),
        "parent_original_j_sha256":m.initial_j_sha,
        "initial_x_e":m.x0,"final_x_e":float(x_epoch[-1]),
        "eV_per_H_full_binding":CHI_H_EV*(m.x0-float(x_epoch[-1])),
        "line_energy_fraction_range":[float(line_fraction.min()),float(line_fraction.max())],
        "max_source_fourmoment_relative_gap":float(source_moment_error.max()),
        "max_expansion_through_frequency":float(Rend[-1].max()),
        "min_expansion_through_frequency":float(Rend[-1].min()),
        "characteristic_samples":int(nt),"source_subsets":{"shear":"tagged","H_only":"counterfactual"},
        "packet_npz":packet_name,"packet_npz_sha256":packet_sha,
        "conservation":conservation,"scenarios":data_modes,
        "comparison":comparison}


def run_science(out,orders=(12,16),time_order=8):
    parent=exact_parent_sources()
    dest=Path(out);dest.parent.mkdir(parents=True,exist_ok=True)
    data={}
    for n in orders:
        c=evaluate_grid(n,order=time_order,output_dir=dest.parent)
        data[f"GL{n}"]=c
        last=c["scenarios"]["shear"]["epochs"][-1]
        delta=c["comparison"][-1]
        print("KM2K_LYA_FREQUENCY_PHYSICS",n,"line_rho",last["rho"],
              "centroid",last["mean_log_nu"],
              "shear_centroid_delta",delta["log_nu_centroid_shear_minus_H_only"],
              "redwing",last["redwing_fraction"],
              "line_to_P8",last["ratio_to_P8_rho"],
              "new_orig_ivp_rhs",c["parent_joint_ivp_nfev"],flush=True)
    a,b=data["GL12"],data["GL16"]
    xerr=abs(a["final_x_e"]-b["final_x_e"])
    lerr=abs(a["scenarios"]["shear"]["epochs"][-1]["mean_log_nu"]-
             b["scenarios"]["shear"]["epochs"][-1]["mean_log_nu"])
    result={
      "schema":"bass.km2k.frequency_resolved_escaped_Lya_bianchi_tagged.v1",
      "base_pr":291,"immutable_parent_HEAD":KM2J_HEAD,"source_blobs":parent,
      "theory":"post-Sobolev escaped Lyalpha tagged scalar intensity, actual full Einstein-P8-Peebles geodesics; no resonant transfer",
      "positive_physical_source":"Peebles net chemical binding and 2p/2s effective branching; original grey emission source subset, NO second Einstein stress",
      "rest_frequency_lambda_m":121.567e-9,
      "Doppler_sigma_definition":"sqrt(kB*Tm/((mp+me)*c**2))",
      "time_transfer":"exact frequency characteristic Green integral with GL quadrature and Gaussian CDF binning",
      "transports_per_geometry":2,"new_solved_joint_Einstein_P8_chemistry_IVPs":len(orders),
      "data":data,"cross_grid":{"xe_abs_diff":xerr,"line_centroid_abs_diff":lerr},
      "hist_logfreq_edges":HIST_EDGES.tolist(),
      "upper_dag":"9/15","upper_edges":21,"km2":"PARTIAL",
      "new_completed_upper_nodes":0,"km2k_scoped":"EXPLORATORY_PENDING_CI",
      "production_ready":False,"merge_ready":False,"auto_next":False,
      "native_subagent":"NOT_RUN","distinct_author_R6_C9":"NOT_RUN",
      "not_implemented":["resonant Lya frequency diffusion","true line absorption and 2p population feedback",
         "atomic recoil","nonthermal photoionization feedback","thermal first-law closure",
         "selfconsistent frequency-polarized P8 gravitational backreaction",
         "observed cosmological parameters","continuum angular enclosure"],
    }
    dest.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--orders",default="12,16")
    p.add_argument("--time-order",default=8,type=int)
    a=p.parse_args()
    run_science(a.output,tuple(map(int,a.orders.split(","))),a.time_order)
