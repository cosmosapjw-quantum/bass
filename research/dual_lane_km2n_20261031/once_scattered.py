"""KM2N exactly-one cold-Thomson-scattered Lyalpha spectral/polarized radiation.

Source-locked BASS KM2M gain and original Einstein-P8-Peebles trajectories.
Transport one-gain with survival after the collision; omit all higher gain.
NO feedback/reinsertion into Einstein or Peebles original grey photon field.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
from research.dual_lane_km2m_20261031.first_gain import (
    source_guards as km2m_source_guards,
    electron_frame_gaussian_histogram,
    scattering_gain_snapshot, EDGES, MID, NBINS, STEP,
)
from research.dual_lane_km2l_20261031.thomson_lya import case_science
from research.dual_lane_km2j_20261031.coupled_chem_p8 import CoupledChemicalP8
from tilted_collision import TiltedThomson

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PARENT_HEAD="2ff05b8416965af0adc7851a8aa60ec2e51b2fee"
KM2M_BLOB="28b0076e9688d60622ce9d8e547af2cccde43c47"
N_INTERVALS=40
OBS_EPOCHS=(8,16,24,32,40)
ALPHA=3/(8*math.pi)

def git_blob(path):
    b=Path(path).read_bytes()
    return hashlib.sha1(f"blob {len(b)}\0".encode()+b).hexdigest()

def source_guards():
    r=km2m_source_guards()
    path=ROOT/"research/dual_lane_km2m_20261031/first_gain.py"
    actual=git_blob(path)
    if actual!=KM2M_BLOB:
        raise ValueError("FROZEN_SOURCE_KM2M_CHANGED "+actual)
    r[str(path.relative_to(ROOT))]=actual
    return r


def analytic_one_scatter_pulse(h,nu,initial,u):
    if not (h>=0 and nu>=0 and initial>=0 and u>=0):
        raise ValueError("nonphysical analytic one scatter pulse")
    return initial*nu*u*math.exp(-(4*h+nu)*u)


def analytic_one_scatter_constant_emissivity(h,nu,j,u):
    if not (h>=0 and nu>=0 and j>=0 and u>=0):
        raise ValueError("nonphysical constant emitter")
    rate=4*h+nu
    if rate==0:return 0.
    return j*nu*(-math.expm1(-rate*u)-rate*u*math.exp(-rate*u))/rate**2


def remap_logfreq_source_tensor(rate,shift, *,bin_centers=MID):
    """Conservative non-negative source-bin remap for rank-2 2x2 tensors.

    `rate`: N, B, 2, 2 electron-rest source, physical bin integrals.
    `shift`: N, normal-observer frequency shift ln(nu_obs/nu_e).
    Output has same physical frequency bins, no negative fractions or clipped nonzero.
    """
    r=np.asarray(rate,float);s=np.asarray(shift,float)
    if r.ndim!=4 or r.shape[1:]!=(NBINS,2,2) or s.shape!=(len(r),):
        raise ValueError("spectral tensor remap shape")
    if not np.all(np.isfinite(r)) or not np.all(np.isfinite(s)):
        raise ValueError("nonfinite spectrum")
    n=len(r)
    if np.max(abs(r-r.swapaxes(2,3)))>1e-18*max(1.,float(np.max(abs(r)))):
        raise ValueError("polarized spectral tensor must be symmetric")
    coord=np.arange(NBINS,dtype=float)[None,:]+s[:,None]/STEP
    left=np.floor(coord).astype(int)
    f=coord-left
    nonzero=(r[:,:,0,0]+r[:,:,1,1])>0
    if np.any(nonzero & ((left<0)|(left+1>=NBINS))):
        raise ArithmeticError("nonzero physical scatter frequency support left validated band")
    pos=np.clip(left,0,NBINS-2)
    frac=np.where(nonzero,f,0.)
    base=(np.arange(n,dtype=int)[:,None]*NBINS + pos)
    y=np.empty_like(r)
    for a,b in [(0,0),(0,1),(1,0),(1,1)]:
        values=r[:,:,a,b]
        one=np.bincount(base.ravel(),weights=(values*(1-frac)).ravel(),minlength=n*NBINS)
        one+=np.bincount((base+1).ravel(),weights=(values*frac).ravel(),minlength=n*NBINS)
        y[:,:,a,b]=one.reshape(n,NBINS)
    scale=max(1e-300,float(np.sum(np.trace(r,axis1=-2,axis2=-1))))
    gap=abs(float(np.sum(np.trace(y,axis1=-2,axis2=-1)))-
            float(np.sum(np.trace(r,axis1=-2,axis2=-1))))/scale
    if gap>5e-12:raise ArithmeticError("one-scattered tensor frequency source not conserved")
    return y,gap


def source_endpoint(model,sol,pack,opt,j):
    """Produce original first gain source at real t_j from unscattered KM2L."""
    t=j*model.end/N_INTERVALS
    d=model.fields(float(t),sol.sol(float(t)),False)
    n=model.N
    op=TiltedThomson(d["n"],d["w"],d["beta"])
    if j==0:
        Me=np.zeros((NBINS,3,3));rate=0.;tau=opt["tau_edges"][0]
        hist_gap=0.;original_gap=0.
    else:
        cut=j*8
        adv=pack["Rend"][j][None,:]-pack["Rnode"][:cut]
        optical=opt["tau_edges"][j][None,:]-opt["tau_nodes"][:cut]
        if np.min(adv)<-2e-12 or np.min(optical)<-3e-12:
            raise ArithmeticError("invalid geodesic or optical-history characteristic")
        p=pack["source_packets"][:cut]*np.exp(-4*adv-np.maximum(0.,optical))
        mu=pack["center_D"][:cut]-adv
        hist,hist_gap=electron_frame_gaussian_histogram(p,mu,pack["doppler_sigma"][:cut],op.D)
        Me=.5*np.einsum("n,nb,nij->bij",op.we,hist,op.Pe)
        w=op.w;J0=.5*p.sum(axis=0)[:,None,None]*(
              np.eye(3)[None,:,:]-np.einsum("ni,nj->nij",op.n,op.n))
        p8_gain=op.gain(J0)
        rate=float(d["nu"]*np.dot(w*op.D,np.trace(p8_gain,axis1=1,axis2=2)))
        F=np.einsum("nij,nja->nia",op.S,d["E"])
        C=np.einsum("nia,bij,nja->nb",F,Me,F,optimize=True)
        rate2=float(np.dot(w,d["nu"]*op.D**(-3)*ALPHA*C.sum(axis=1)))
        original_gap=abs(rate2/rate-1.)
        if original_gap>4e-10:
            raise ArithmeticError("KM2M source gain rate disagrees with original P8")
    F=np.einsum("nij,nja->nia",op.S,d["E"])
    if np.max(abs(np.einsum("nia,nia->na",d["E"],d["n"][:, :, None])))>1e-8:
        raise ArithmeticError("unphysical photon normal screen")
    out={"time":float(t),"nu":float(d["nu"]),"Me":Me,
         "D":op.D,"F":F,"w":d["w"],"n":d["n"],
         "E":d["E"],"mu":d["mu"],
         "tau":opt["tau_edges"][j],"reference_gain_rate":float(rate),
         "rate_source_parity":float(original_gap),"cdf_error":float(hist_gap),
         "original_H":float(d["H"]),"original_xe":float(d["x"])}
    return out


def propagate_one_scatter(sources,k, *, save_field=None):
    """Composite-Simpson retarded first gain then exact Bianchi screen propagator.

    X1 is 2x2 screen coherency. Source at t_j built from original KM2L
    zero-scatter J0; after first collision, only opacity loss is allowed.
    """
    if k not in OBS_EPOCHS or len(sources)<k+1:
        raise ValueError("missing real coupled source epochs")
    obs=sources[k]
    N=len(obs["mu"]);u=obs["time"]
    h=u/k
    weights=np.array([1 if j in (0,k) else (4 if j%2 else 2)
                     for j in range(k+1)],float)*(h/3.)
    X=np.zeros((N,NBINS,2,2))
    source_energy_events=[]
    max_remap=0.
    for j in range(1,k+1):
        d=sources[j]
        age=np.maximum(0.,obs["tau"]-d["tau"])
        if np.min(obs["tau"]-d["tau"])<-2e-12:
            raise ArithmeticError("first-scattered photon attenuation is acausal")
        ratio=obs["mu"]/d["mu"]
        if np.any(ratio<=0) or np.max(ratio)>1+5e-12:
            raise ArithmeticError("original Bianchi first-scattered photon blueshift beyond source support")
        transfer=weights[j]*ratio**4*np.exp(-age)
        F=d["F"]
        # Exactly original P8 gain screen coherency, frequency resolved.
        J=np.einsum("nia,bij,njc->nbac",F,d["Me"],F,optimize=True)
        rate=(ALPHA*d["nu"]*d["D"]**(-3))
        J*= (rate*transfer)[:,None,None,None]
        shift=-np.log(d["D"])+np.log(ratio)
        remapped,gap=remap_logfreq_source_tensor(J,shift)
        max_remap=max(max_remap,gap)
        X+=remapped
        source_energy_events.append(float(d["reference_gain_rate"]))
    if not np.all(np.isfinite(X)):
        raise ArithmeticError("nonfinite time-propagated polarized spectrum")
    X=(X+X.swapaxes(2,3))/2
    B=X.sum(axis=1)
    eig=np.linalg.eigvalsh(B)
    if np.min(eig)<-1e-12*max(1e-20,float(np.max(abs(B)))):
        raise ArithmeticError("negative propagated first-scattered screen polarization")
    tr=np.trace(B,axis1=1,axis2=2)
    w=obs["w"]
    rho=float(w@tr)
    p2=np.einsum("nij,nji->n",B,B)
    pol=np.sqrt(np.maximum(0.,2*p2-tr*tr))/np.maximum(tr,1e-300)
    meanpol=float((w*tr)@pol/rho)
    rms=float(np.sqrt(np.dot(w*tr,pol**2)/rho))
    maximal=float(np.max(pol))
    if maximal>1+2e-9:raise ArithmeticError("unphysical once-scattered linear polarization")
    norm_spectrum=np.einsum("n,nb->b",w,np.trace(X,axis1=2,axis2=3))
    spec_gap=abs(norm_spectrum.sum()/rho-1.)
    if spec_gap>2e-11:raise ArithmeticError("one-scattered frequency/bolometric energy mismatch")
    cent=float(MID@norm_spectrum/rho)
    wid=float(np.sqrt(max(0.,(MID**2)@norm_spectrum/rho-cent**2)))
    q=np.einsum("n,ni->i",w*tr,obs["n"])
    pres=np.einsum("n,ni,nj->ij",w*tr,obs["n"],obs["n"])
    # Physical first-scatter polarization tensor in normal tetrad, final snapshot.
    if save_field:
        f=Path(save_field);f.parent.mkdir(parents=True,exist_ok=True)
        np.savez_compressed(f,screen_spectral_first_one=X,
              screen_bolometric_first_one=B,n=obs["n"],w=w,E=obs["E"],
              frequency_edges=EDGES,mu=obs["mu"],tau=obs["tau"])
        hash_file=hashlib.sha256(f.read_bytes()).hexdigest()
        filename=f.name
    else:
        filename=None;hash_file=None
    result={"u":float(u),"rho_exactly_one":rho,
            "q_exactly_one":q.tolist(),"pressure_exactly_one":pres.tolist(),
            "mean_linear_polarization":meanpol,"rms_linear_polarization":rms,
            "max_linear_polarization":maximal,
            "mean_logfreq":cent,"sigma_logfreq_bin":wid,
            "spectral_energy_bins":norm_spectrum.tolist(),
            "frequency_bolometric_relative_gap":float(spec_gap),
            "max_remap_relative_gap":float(max_remap),
            "source_rates_per_event_u":source_energy_events,
            "screen_eigen_min":float(np.min(eig)),
            "factorized_field_file":filename,"factorized_field_sha256":hash_file}
    return result


def run_science(output, grids=(12,16)):
    src=source_guards()
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    cases={}
    for theta in grids:
        source=case_science(theta,output.parent,order=8,end=.25)
        model=CoupledChemicalP8(ntheta=theta,end=.25,chem_energy=True)
        sol=model.solve(rtol=1e-11,atol=1.5e-13)
        with np.load(output.parent/source["KM2K_original_packets_file"],allow_pickle=False) as z:
            packet={k:z[k].copy() for k in z.files}
        with np.load(output.parent/source["thomson_opacity_file"],allow_pickle=False) as z:
            opacity={k:z[k].copy() for k in z.files}
        # independently re-integrate original source geometry for full screen transport.
        sources=[source_endpoint(model,sol,packet,opacity,j) for j in range(41)]
        ledger_path=output.parent/f"KM2N_FIRST_SOURCE_LEDGER_GL{theta}.npz"
        np.savez_compressed(ledger_path,
             time=np.array([z["time"] for z in sources]),
             Me=np.stack([z["Me"] for z in sources]),
             F=np.stack([z["F"] for z in sources]),
             D=np.stack([z["D"] for z in sources]),
             nu=np.array([z["nu"] for z in sources]),
             mu=np.stack([z["mu"] for z in sources]),
             tau=np.stack([z["tau"] for z in sources]),
             w=np.stack([z["w"] for z in sources]),
             n=np.stack([z["n"] for z in sources]),
             E=np.stack([z["E"] for z in sources]),
             source_gain_rate=np.array([z["reference_gain_rate"] for z in sources]))
        ledger_sha=hashlib.sha256(ledger_path.read_bytes()).hexdigest()
        out=[]
        for k in OBS_EPOCHS:
            dest=output.parent/f"KM2N_ONCE_POL_SCREEN_GL{theta}_U{k}.npz" if k==40 else None
            r=propagate_one_scatter(sources,k,save_field=dest)
            r["original_KM2L_ballistic_rho"]=source["scenarios"]["shear_thomson"]["epochs"][k]["rho"]
            r["original_KM2L_first_scatter_event_rate"]=source["scenarios"]["shear_thomson"]["epochs"][k]["first_collision_energy_rate"]
            r["new_once_scattered_to_ballistic_energy_ratio"]=r["rho_exactly_one"]/r["original_KM2L_ballistic_rho"]
            out.append(r)
        end=out[-1]
        print("KM2N_ORIGINAL_EXACT_ONE_SCATTER",theta,
              "rho1",end["rho_exactly_one"],"rho0",end["original_KM2L_ballistic_rho"],
              "ratio",end["new_once_scattered_to_ballistic_energy_ratio"],
              "linear_pol",end["mean_linear_polarization"],"centroid",end["mean_logfreq"],flush=True)
        C=model.conservation(sol,order=24)
        if max(C["max_Hamiltonian_norm"],C["max_momentum_norm"])>5e-8:
            raise ArithmeticError("original Einstein constraints not preserved")
        cases[f"GL{theta}"]={"grid":theta,"original_P8_ray_count":model.N,
             "fresh_original_joint_IVP_RHS":[*source["joint_original_parent_rhs_calls"],int(sol.nfev)],
             "source_original_gamma_xe_reintegrated":True,
             "max_source_p8_gain_parity_relative":max(z["rate_source_parity"] for z in sources),
             "max_source_frequency_cdf_gap":max(z["cdf_error"] for z in sources),
             "first_source_ledger_file":ledger_path.name,
             "first_source_ledger_sha256":ledger_sha,
             "original_Einstein_conservation":C,
             "snapshots":out}
    data={"schema":"bass.km2n.once_scattered_pol_spectral_retarded.v1",
          "immutable_parent_head":PARENT_HEAD,"immutable_parent_pr":295,
          "original_blobs":src,"metric":"(-,+,+,+)",
          "claim":"original coupled Einstein-P8-Peebles Bianchi I exact-one-cold-Thomson spectral and polarized field with post-first collision survival, composite Simpson 40 panels",
          "physical_time_nodes":5,"unique_original_angular_grids":len(grids),
          "frequency_bins_per_snapshot":NBINS,"physics_frequency_rows":len(grids)*5*NBINS,
          "cases":cases,"upper_dag":"9/15","upper_edges":21,
          "KM2":"PARTIAL","new_upper_completed":0,
          "KM2N_scoped":"PENDING_VERIFICATION", "production_ready":False,
          "merge_ready":False,"auto_next":False,"native_subagent":"NOT_RUN",
          "distinct_author_R6_C9":"NOT_RUN",
          "not_implemented":["second and higher Thomson scattering gain",
             "spectral tagged photons backreaction to original Einstein-P8 field",
             "resonant Lya Fokker-Planck and recoil",
             "thermal electron Compton redistribution","photoexcitation and first law closure",
             "angular continuum certified error","observational CMB spectrum"]}
    output.write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+"\n")
    return data

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--grids",default="12,16")
    a=p.parse_args();run_science(a.output,tuple(int(x) for x in a.grids.split(",")))
