#!/usr/bin/env python3
"""Retarded exactly-once Thomson-scattered S0 ionizing photons through REI F08.

This is an independently reconstructed source-prescription matched continuum
Boltzmann first-scatter solution on frozen F08 H/He matter histories.
It is not a replay of the original discrete F08 photon source operator, and
not an observed CMB or an Einstein-self-consistent solution.
"""
from __future__ import annotations
import argparse, csv, gzip, hashlib, io, json, math, sys
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/"bass_rei_f08_s0_source_photon_thomson_20261101"
sys.path.insert(0,str(PARENT))
from s0_source_photon_thomson import (
    source_histories,gauss_birth_direction_grid,direction_grid,redshift,
    threshold_age,split_threshold_births,tau_hi,THRESHOLD,BIRTH_EV,
    SOURCE_RATE,INITIAL_COUNT,SIG_T,C,END,SHA,ATOMIC_OWNER,digest
)
PREF=3/(16*math.pi)
GRID_STEP=6.25e8
STAGES=(0.5,1.0)
BRANCHES=("S0_BI","S0_FLRW")
MODEL="BASS_REI_F08_S0_RETARDED_EXACTLY_ONE_POLARIZED_THOMSON_V1"

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):
            h.update(b)
    return h.hexdigest()

def sig_hi_vec(e):
    e=np.asarray(e,dtype=np.float64)
    if np.any(~np.isfinite(e)) or np.any((e<0)|(e>50000)):
        raise ValueError("Verner original provider energy domain")
    out=np.zeros_like(e)
    ok=e>=THRESHOLD
    x=e[ok]/.4298
    out[ok]=5.475e4*(x-1)**2*x**(2.963/2-5.5)*(
        1+np.sqrt(x/32.88))**(-2.963)*1e-18
    return out

def original_linear_grid(values, t):
    """Only original immutable F08 uniform proper-clock samples; vectorized."""
    t=np.asarray(t,dtype=np.float64)
    if np.any((t<0)|(t>END)) or not np.all(np.isfinite(t)):
        raise ValueError("F08 physical clock outside original sample support")
    v=np.asarray(values,dtype=np.float64)
    idx=np.minimum((t/GRID_STEP).astype(np.int64),15999)
    frac=np.clip((t-idx*GRID_STEP)/GRID_STEP,0.0,1.0)
    return v[idx]*(1-frac)+v[idx+1]*frac

def incoming_photon_packets(history, scatter_t, births, inmu, inphi, simpson):
    """Number weights at time s for each source birth and physical birth angle."""
    if not 0<scatter_t<=END:raise ValueError("scatter time outside original F08")
    tr=history.tau_electron(scatter_t)
    source=[(0.0,INITIAL_COUNT,"initial")]
    source += [((k+.5)*scatter_t/births,SOURCE_RATE*scatter_t/births,"continuous")
               for k in range(births)]
    en=[]; weight=[]; nsc=[]; birth_t=[]
    for _,_,n,mu,phi,wa in gauss_birth_direction_grid(inmu,inphi):
        max_age=threshold_age(history.H,n)
        for _,(t_b,source_n,kind) in split_threshold_births(source,scatter_t,max_age):
            dt=scatter_t-t_b
            R,ns=redshift(history.H,n,dt)
            t_hi=tau_hi(history,t_b,scatter_t,n,max_age,simpson)
            t_t=tr-history.tau_electron(t_b)
            if t_t<-1e-17 or t_hi<0:raise ValueError("negative incoming absorption")
            w=source_n*wa*math.exp(-t_hi-t_t)
            if not (0<w<=INITIAL_COUNT+SOURCE_RATE*scatter_t):
                raise ValueError("unphysical initial S0 photon weight")
            en.append(BIRTH_EV*R)
            weight.append(w)
            nsc.append(ns)
            birth_t.append(t_b)
    e=np.asarray(en); w=np.asarray(weight); ns=np.asarray(nsc)
    t=np.asarray(birth_t)
    if not (len(e)==len(w)==len(t)==len(ns)>0):
        raise ValueError("original source birth data incomplete")
    if np.min(e)<BIRTH_EV*math.exp(-max(history.H)*scatter_t)-1e-12:
        raise ValueError("original S0 characteristic violated source support")
    return e,w,ns,t

def outgoing_characteristic(history, observed_dir, t_sc, t_obs):
    """Physical propagation direction at scatter, redshift and sky Jacobian."""
    if t_obs<t_sc or not (0<=t_sc<=t_obs<=END):
        raise ValueError("invalid outgoing chronology")
    H=np.asarray(history.H);no=np.asarray(observed_dir,dtype=float)
    D=t_obs-t_sc
    g=np.sqrt(np.sum(no*no*np.exp(2*H*D)))
    ns=no*np.exp(H*D)/g
    R=1/g
    jac=R**3*math.exp(np.sum(H)*D)
    if not math.isclose(np.sum(ns*ns),1,rel_tol=1e-13) or R>1+1e-12:
        raise ValueError("outgoing null energy/direction normalization")
    return ns,R,jac

def parallel_rotation(history, scatter_dir, delta, simpson=8):
    """Bianchi I screen angle chi=int mu*dphi, exact sphere connection."""
    H=np.asarray(history.H); ns=np.asarray(scatter_dir)
    if delta<=0:return 0.
    if simpson%2 or simpson<2:raise ValueError("screen Simpson must be even")
    step=delta/simpson
    total=0.
    for j in range(simpson+1):
        age=j*step
        q=ns*np.exp(-H*age);q=q/np.linalg.norm(q)
        xy=q[0]*q[0]+q[1]*q[1]
        phi_dot=(H[0]-H[1])*q[0]*q[1]/xy if xy>1e-26 else 0.
        total+=(1 if j in (0,simpson) else 4 if j%2 else 2)*q[2]*phi_dot
    return total*step/3

def post_hi_optical_depth(history, energy_sc, scatter_dir, scatter_t, obs_t, simpson=8):
    """Exact Bianchi frequency with source-matched nHI, vectorized threshold split."""
    energy=np.asarray(energy_sc,dtype=np.float64)
    H=np.asarray(history.H,dtype=float);n=np.asarray(scatter_dir)
    delta=obs_t-scatter_t
    if delta<0 or not 0<=scatter_t<=obs_t<=END:
        raise ValueError("outgoing source time mismatch")
    ans=np.zeros_like(energy)
    if delta==0:return ans
    mask=energy>=THRESHOLD
    if not np.any(mask):return ans
    en=energy[mask]
    def red(age):
        z=(n[None,:]**2)*np.exp(-2*age[:,None]*H[None,:])
        return np.sqrt(np.sum(z,axis=1))
    # Cut frequency at the TRUE HI fit threshold, rather than Simpson across a jump.
    dlo=np.zeros_like(en);dhi=np.full_like(en,delta)
    if np.all(en*red(np.full_like(en,delta))>=THRESHOLD):
        cut=dhi
    else:
        for _ in range(36):
            mid=(dlo+dhi)/2
            still=en*red(mid)>THRESHOLD
            dlo=np.where(still,mid,dlo)
            dhi=np.where(still,dhi,mid)
        cut=np.where(en*red(np.full_like(en,delta))>=THRESHOLD,delta,(dlo+dhi)/2)
    accum=np.zeros_like(en)
    for k in range(simpson+1):
        age=cut*(k/simpson)
        obsenergy=en*red(age)
        # Values at discontinuous end-cuts are taken on the ionizing side.
        if k==simpson:
            obsenergy=np.where(cut<delta,np.maximum(obsenergy,THRESHOLD),obsenergy)
        density=original_linear_grid(history.nhi,scatter_t+age)
        coeff=(1 if k==0 or k==simpson else 4 if k%2 else 2)
        accum+=coeff*density*sig_hi_vec(obsenergy)
    ans[mask]=C*cut*accum/(3*simpson)
    if np.any(ans<0) or np.any(~np.isfinite(ans)):
        raise ValueError("invalid outgoing neutral-H absorption")
    return ans

def screen(scatter_dir):
    x,y,z=map(float,scatter_dir)
    phi=math.atan2(y,x)
    sin=math.hypot(x,y)
    return np.array((z*math.cos(phi),z*math.sin(phi),-sin)), np.array((-math.sin(phi),math.cos(phi),0.))

def scatter_contribution(history, packets, scatter_t, obs_t, obsdir,
                         hi_post_simpson=8, rotate=True):
    E,ww,ni,birth=packets
    ns,R,jac=outgoing_characteristic(history,obsdir,scatter_t,obs_t)
    e_theta,e_phi=screen(ns)
    dot=ni@ns;d1=ni@e_theta;d2=ni@e_phi
    tau_hi_out=post_hi_optical_depth(history,E,ns,scatter_t,obs_t,hi_post_simpson)
    dtau=history.tau_electron(obs_t)-history.tau_electron(scatter_t)
    if dtau<-1e-16:raise ValueError("Thomson postscatter history nonmonotonic")
    probability=ww*np.exp(-tau_hi_out-dtau)
    electron=C*SIG_T*history.linear(history.ne,scatter_t)
    factor=PREF*electron*jac
    weighted=probability*E*R
    k_I=1+dot*dot
    I=factor*np.dot(weighted,k_I)
    Q=-factor*np.dot(weighted,d1*d1-d2*d2)
    U=-2*factor*np.dot(weighted,d1*d2)
    photon_number=factor*np.dot(probability,k_I)
    emission_time=factor*np.dot(weighted*k_I,birth)
    if rotate:
        chi=parallel_rotation(history,ns,obs_t-scatter_t)
        # A parallel screen frame in Bianchi I, spin-two law.
        spin=complex(Q,U)*complex(math.cos(-2*chi),math.sin(-2*chi))
        Q,U=spin.real,spin.imag
    if I<0 or photon_number<0 or math.hypot(Q,U)>I*(1+1e-12):
        raise ValueError("unphysical polarized scattering density matrix")
    return I,Q,U,photon_number,emission_time,dtau,float(np.max(tau_hi_out))

def gauss_scatter_times(obs_time,panels):
    x,w=np.polynomial.legendre.leggauss(panels)
    return [(obs_time*(xi+1)/2,obs_time*wi/2) for xi,wi in zip(x,w)]

def retarded_sky(history,obs_t,nt=12,births=32,inmu=8,inphi=16,
                 outmu=8,outphi=16,hi_simpson=8):
    if not 0<obs_t<=END or nt<4 or births<8:
        raise ValueError("invalid observer chronology or physical quadrature")
    outgoing=list(direction_grid(outmu,outphi))
    records=[{"branch":history.label,"observer_time_s":obs_t,
       "mu_index":i,"phi_index":j,"mu":mu,"phi_rad":phi,
       "nx_obs":n[0],"ny_obs":n[1],"nz_obs":n[2],
       "I1_ev_per_H_sr":0.,"Q1_ev_per_H_sr":0.,"U1_ev_per_H_sr":0.,
       "N1_photons_per_H_sr":0.,"emission_weighted_time_s":0.,
       "scatter_weighted_time_s":0.,"out_max_tau_HI":0.} for i,j,n,mu,phi in outgoing]
    chronology=[]
    for s,sw in gauss_scatter_times(obs_t,nt):
        packets=incoming_photon_packets(history,s,births,inmu,inphi,hi_simpson)
        cumI=0.;cumQ=0.;cumU=0.
        for idx,(i,j,n,mu,phi) in enumerate(outgoing):
            I,Q,U,N,et,t_th,max_tau=scatter_contribution(
                history,packets,s,obs_t,n,hi_simpson)
            r=records[idx]
            r["I1_ev_per_H_sr"]+=sw*I
            r["Q1_ev_per_H_sr"]+=sw*Q
            r["U1_ev_per_H_sr"]+=sw*U
            r["N1_photons_per_H_sr"]+=sw*N
            r["emission_weighted_time_s"]+=sw*et
            r["scatter_weighted_time_s"]+=sw*I*s
            r["out_max_tau_HI"]=max(r["out_max_tau_HI"],max_tau)
            cumI+=I
            cumQ+=Q
            cumU+=U
        chronology.append({"branch":history.label,"observer_time_s":obs_t,
              "scatter_time_s":s,"scatter_quadrature_weight_s":sw,
              "sky_mean_local_I_gain_ev_per_H_sr_s":cumI/len(outgoing),
              "sky_mean_local_Q_gain_ev_per_H_sr_s":cumQ/len(outgoing),
              "sky_mean_local_U_gain_ev_per_H_sr_s":cumU/len(outgoing),
              "input_packets":len(packets[0])})
    for r in records:
        I=r["I1_ev_per_H_sr"];Q=r["Q1_ev_per_H_sr"];U=r["U1_ev_per_H_sr"]
        if not 0<I or math.hypot(Q,U)>I*(1+1e-10):
            raise ValueError("observer first-scattered Stokes invalid")
        r["P1_over_I1"]=math.hypot(Q,U)/I
        r["mean_birth_time_s"]=r.pop("emission_weighted_time_s")/I
        r["mean_scatter_time_s"]=r.pop("scatter_weighted_time_s")/I
        r["mean_observed_photon_energy_ev"]=I/r["N1_photons_per_H_sr"]
    return records,chronology

def gzipcsv(path,records):
    with path.open("wb") as f:
        with gzip.GzipFile(fileobj=f,mode="wb",filename="",mtime=0,compresslevel=6) as z:
            with io.TextIOWrapper(z,encoding="utf8",newline="") as text:
                w=csv.DictWriter(text,fieldnames=list(records[0]))
                w.writeheader()
                for row in records:w.writerow(row)
    return sha(path)

def solve(out,nt=12,births=32,inmu=8,inphi=16,outmu=8,outphi=16,hi_simpson=8):
    histories=source_histories()
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    sky=[];chron=[]
    for label in BRANCHES:
        h=histories[label]
        for frac in STAGES:
            t=END*frac
            rows,ch=retarded_sky(h,t,nt,births,inmu,inphi,outmu,outphi,hi_simpson)
            sky+=rows;chron+=ch
    p=out/"RETARDED_ONCE_THOMSON_OBSERVER_STOKES.csv.gz"
    q=out/"RETARDED_ONCE_SCATTER_TIME_CHRONOLOGY.csv.gz"
    sh=gzipcsv(p,sky);qh=gzipcsv(q,chron)
    summaries=[]
    for label in BRANCHES:
        for frac in STAGES:
            rows=[r for r in sky if r["branch"]==label and r["observer_time_s"]==END*frac]
            summaries.append({"branch":label,"observer_time_s":END*frac,
                "mean_I1_ev_per_H_sr":math.fsum(r["I1_ev_per_H_sr"] for r in rows)/len(rows),
                "sky_integrated_N1_per_H":4*math.pi*math.fsum(r["N1_photons_per_H_sr"] for r in rows)/len(rows),
                "sky_integrated_U1_ev_per_H":4*math.pi*math.fsum(r["I1_ev_per_H_sr"] for r in rows)/len(rows),
                "mean_P1_over_I1":math.fsum(r["P1_over_I1"] for r in rows)/len(rows),
                "max_P1_over_I1":max(r["P1_over_I1"] for r in rows),
                "mean_scatter_time_s":sum(r["mean_scatter_time_s"]*r["I1_ev_per_H_sr"] for r in rows)/sum(r["I1_ev_per_H_sr"] for r in rows),
                "mean_birth_time_s":sum(r["mean_birth_time_s"]*r["I1_ev_per_H_sr"] for r in rows)/sum(r["I1_ev_per_H_sr"] for r in rows)})
    report={"schema":MODEL,"unit":"ONE_BOUNDED_REI_F08_S0_CAUSAL_EMISSION_TO_OBSERVER_PHYSICS",
        "status":"SOURCE_PRESCRIPTION_MATCHED_CONDITIONAL_NONAUTHORITATIVE",
        "source_f08_pair_id":"0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8",
        "parent_bass_pr":317,"parent_bass_head":"18e6273f28ea67e472c919de86594f70fd1c81c9",
        "source_original_F08_photon_state_equivalence":False,
        "input_f08_hhe_matter_history":"BYTE_EXACT_FROM_ORIGINAL_REI",
        "ionizing_photon_source":"13.7eV_INITIAL_AND_CONTINUOUS_ORIGINAL_S0",
        "source_I_incoming":"INCLUDES_HI_PHOTOABS_AND_ZERO_PREVIOUS_THOMSON",
        "outgoing_transport":"HI_PHOTOABS_UNTIL_13.60eV_PLUS_NO_FUTURE_THOMSON_PLUS_EXACT_BIANCHI_REDSHIFT_AND_SKY_JACOBIAN_PLUS_PARALLEL_SCREEN",
        "single_scatter_first_and_last_exact_one_only":True,
        "t0_epoch_is_not_modern_cosmic_z0":True,
        "spectral_photon_redistribution_from_original_discrete_owner":False,
        "einstein_constraint_on_original_metric":False,
        "source_hhe_spectra_model_error_bound":"NOT_ESTABLISHED",
        "code_trust":"NUMPY_BINARY64_GAUSS_SIMSPON_NO_INTERVAL_CLAIM",
        "units":{"I":"eV per original comoving hydrogen nucleus per steradian","N":"photons per original comoving hydrogen nucleus per steradian","physical_time":"s","polarization":"I,Q,U same units"},
        "quadrature":{"scatter_gl":nt,"continuous_birth_midpoint":births,"incident_GL_mu":inmu,"incident_phi":inphi,"observer_midpoint_mu":outmu,"observer_phi":outphi,"HI_split_Simpson":hi_simpson},
        "sky_rows":len(sky),"chronology_rows":len(chron),"sky_sha256":sh,"chronology_sha256":qh,
        "summary":summaries,
        "rei_central":"28/88_REPORTED","rei_working":"33/88_REPORTED_NONADDITIVE",
        "rei_physical_fast":"4/7_REPORTED","bass_upper":"9/15_SCOPED_SOURCE_MAPPED",
        "new_rei_canonical_nodes":0,"new_bass_full_nodes":0,
        "original_F05":"BLOCKED_TICK160/131072","original_F09":"BLOCKED_PROVIDER_DOMAIN",
        "original_F08":"HOLD","production":"HOLD","merge":False,"auto_next":False}
    (out/"RESULT.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("BASS_REI_RETARDED_FINAL",json.dumps({"sky_rows":len(sky),
       "chronology_rows":len(chron),"sha256":sh,"summary":summaries},sort_keys=True))
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--scatter",type=int,default=12)
    p.add_argument("--birth",type=int,default=32)
    p.add_argument("--inmu",type=int,default=8)
    p.add_argument("--inphi",type=int,default=16)
    p.add_argument("--outmu",type=int,default=8)
    p.add_argument("--outphi",type=int,default=16)
    p.add_argument("--simpson",type=int,default=8)
    a=p.parse_args()
    solve(a.out,a.scatter,a.birth,a.inmu,a.inphi,a.outmu,a.outphi,a.simpson)
