"""New smooth-source curved controls, using unchanged G1A dynamics.

Each call saves before the next starts. Reuse requires identical source/config
hashes and raw-file hash, never a name-only or transcript-only completion claim.
"""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
import argparse, hashlib, json, time, traceback
import numpy as np
from scipy.integrate import solve_ivp
import smooth
from symmetric_bridge import SymmetricPackets
from vendor import kinetic as kn, core as bg
ROOT=Path(__file__).resolve().parent
GATE=2e-8
SCHEDULE=[(4,6,False),(8,6,False),(12,6,False),(8,10,False),
          (8,14,False),(8,20,False),(8,14,True),(12,20,False)]

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def dump(path,obj):Path(path).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def source_lock():
    return {name:sha(ROOT/name) for name in ('smooth.py','NORMALIZERS.json','vendor/core.py','vendor/kinetic.py','symmetric_bridge.py','run_curved.py')}

def make_case(family,order,nmu):
    if family=='V':n=np.zeros((3,3));a=np.array([.25,0.,0.]);s=np.diag([0.,.22,-.22])
    elif family=='VIII':n=np.diag([-.9,.7,1.1]);a=np.zeros(3);s=np.diag([.24,-.09,-.15])
    else:raise ValueError('only frozen V and VIII controls are selected')
    km,wm,mm=smooth.packets('FD',3.,order,nmu,amplitude=1.8,A=smooth.default_anisotropy())
    kr,wr,mr=smooth.photon_packets('Planck',nmu,amplitude=.9)
    k=np.vstack((km,kr));w=np.r_[wm,wr];mass=np.r_[mm,mr]
    sector=np.r_[np.zeros(len(wm),dtype=int),np.ones(len(wr),dtype=int)]
    model=SymmetricPackets(mass,sector,cosmological_constant=.15)
    rho,flux,_=model.moment_blocks(k,w)
    r3,_=bg.curvature(n,a)
    h=np.sqrt((rho.sum()+model.lam+np.sum(s*s)/2-r3/2)/3)
    continuum_h=np.sqrt((2.7+model.lam+np.sum(s*s)/2-r3/2)/3)
    z=model.initial(h,s,n,a,k,w)
    if np.max(np.abs(bg.constraints(z[:model.nb],model.lam)))>2e-13:
        raise ArithmeticError('initial discrete Einstein constraints are not closed')
    return model,z,dict(family=family,order=int(order),nmu=int(nmu),packets=len(w),
                       massive_packets=len(wm),photon_packets=len(wr),initial_rho_m=float(rho[0]),
                       initial_rho_r=float(rho[1]),initial_h=float(h),continuum_initial_h=float(continuum_h),
                       h0_discrete_shift=float(h-continuum_h),initial_flux=flux.tolist(),
                       photon_reduction='exact_N_and_T_radial',amplitudes=[1.8,.9],lambda_value=.15)

def check_envelope(z):
    s=bg.stf(z[1:6]);vals=np.array([abs(z[0]),np.linalg.norm(s,ord=2),np.linalg.norm(z[12:15])])
    if not np.all(np.isfinite(vals)) or np.any(vals>np.array([2.,1.,.5])):
        raise ValueError(f'fixed geometry envelope exceeded: {vals}')
    return vals

def diagnostics(model,z):
    y,k,w=model.decode(z);rho,f,src=model.moment_blocks(k,w)
    actual=bg.State(y.h,y.sigma,y.n,y.a,y.alpha,rho,f).pack()
    mismatch=float(np.max(np.abs(z[:24]-actual)/(1+np.maximum(np.abs(z[:24]),np.abs(actual)))))
    blocks=[]
    for i in range(2):
        sel=model.sectors==i;ki,wi,mi=k[sel],w[sel],model.mass[sel]
        E=np.hypot(mi,np.linalg.norm(ki,axis=1))
        # 14 fields per sector: rho, flux3, p, pi5, N, number-current3.
        blocks.append(np.r_[rho[i],f[i],src.pressure[i],bg.five(src.pi[i]),
                            wi.sum(),np.einsum('q,qi->i',wi/E,ki)])
    return dict(observable=np.r_[z[:24],*blocks],mismatch=mismatch,
                core_constraint=float(bg.relative_constraint(z[:24],model.lam)),
                kinetic_constraint=float(bg.relative_constraint(actual,model.lam)),
                minimum_weight=float(w.min()))

def compare_observables(a,b):
    if a.shape!=b.shape or not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
        raise ValueError('matched finite history arrays required')
    return float(np.max(np.abs(a-b)/(1+np.maximum(np.abs(a),np.abs(b)))))

def run_one(family,order,nmu,tight,target):
    target=Path(target);target.mkdir(parents=True,exist_ok=True)
    name=f'{family}_r{order}_a{nmu}'+('_tight' if tight else '')
    receipt=target/(name+'.json');raw=target/(name+'.npz')
    config=dict(family=family,order=order,nmu=nmu,tight=bool(tight),tau=[0.,.8],epochs=33,
                method='DOP853',rtol=2e-12 if tight else 2e-10,atol=2e-14 if tight else 2e-12,max_step=.04)
    lock=source_lock()
    if receipt.exists():
        r=json.loads(receipt.read_text())
        if r.get('config')!=config or r.get('source')!=lock or not raw.exists() or sha(raw)!=r.get('raw_sha256'):
            raise RuntimeError(f'changed existing evidence: {name}')
        print(json.dumps({'case':name,'execution':'reused_saved','status':r['status']}),flush=True)
        return r
    if raw.exists() or (target/(name+'.failure.json')).exists():
        raise FileExistsError(f'preserve earlier raw/failure before any explicit continuation: {name}')
    start=time.perf_counter();model,z0,info=make_case(family,order,nmu)
    maxima=np.zeros(3)
    def fun(t,z):
        nonlocal maxima
        maxima=np.maximum(maxima,check_envelope(z))
        return model.rhs(t,z)
    try:
        sol=solve_ivp(fun,(0.,.8),z0,t_eval=np.linspace(0,.8,33),method='DOP853',
                      rtol=config['rtol'],atol=config['atol'],max_step=.04)
        if not sol.success or sol.y.shape[1]!=33:raise RuntimeError(sol.message)
        ds=[diagnostics(model,z) for z in sol.y.T]
        obs=np.array([d['observable'] for d in ds])
        values={key:np.array([d[key] for d in ds]) for key in ('mismatch','core_constraint','kinetic_constraint','minimum_weight')}
        np.savez_compressed(raw,tau=sol.t,state=sol.y,observable=obs,mass=model.mass,sectors=model.sectors,**values)
        r=dict(case=name,config=config,source=lock,initial=info,nfev=sol.nfev,
               elapsed_s=time.perf_counter()-start,max_sampled_RHS_envelope=maxima.tolist(),
               maxima={key:float(values[key].max()) for key in ('mismatch','core_constraint','kinetic_constraint')},
               minimum_weight=float(values['minimum_weight'].min()),raw_sha256=sha(raw),raw_bytes=raw.stat().st_size,
               full_state_size=len(z0),status='PASS_SCOPED')
        if max(r['maxima'].values())>=GATE:r['status']='FAIL_LEDGER_OR_CONSTRAINT'
        dump(receipt,r);print(json.dumps(r),flush=True)
        return r
    except Exception as exc:
        dump(target/(name+'.failure.json'),dict(case=name,config=config,source=lock,
             exception=repr(exc),traceback=traceback.format_exc(),elapsed_s=time.perf_counter()-start))
        raise

def summarize(target):
    target=Path(target);rows=[];comparisons=[]
    for family in ('V','VIII'):
        loaded={}
        for order,ang,tight in SCHEDULE:
            name=f'{family}_r{order}_a{ang}'+('_tight' if tight else '')
            r=json.loads((target/(name+'.json')).read_text());raw=target/(name+'.npz')
            if sha(raw)!=r['raw_sha256']:raise RuntimeError('raw hash mismatch')
            with np.load(raw) as f:loaded[(order,ang,tight)]=f['observable'].copy()
            rows.append(r)
        for label,left,right in (
          ('radial_coarse',(4,6,False),(12,6,False)),
          ('radial_selected',(8,6,False),(12,6,False)),
          ('angular_coarse',(8,6,False),(8,20,False)),
          ('angular_middle',(8,10,False),(8,20,False)),
          ('angular_selected',(8,14,False),(8,20,False)),
          ('time_selected',(8,14,False),(8,14,True)),
          ('radial_fine_angle',(8,20,False),(12,20,False)),
          ('combined',(8,14,False),(12,20,False))):
            err=compare_observables(loaded[left],loaded[right])
            comparisons.append(dict(family=family,axis=label,left=list(left),right=list(right),error=err,
                required=label not in ('radial_coarse','angular_coarse','angular_middle'),accepted=err<GATE))
    result=dict(status='PASS_SCOPED' if all(r['status']=='PASS_SCOPED' for r in rows) and
                all(c['accepted'] for c in comparisons if c['required']) else 'FAIL_REFINEMENT',
                new_IVPs=len(rows),old_campaign_replays=0,epochs_per_history=33,comparisons=comparisons,
                maxima={key:max(r['maxima'][key] for r in rows) for key in ('core_constraint','kinetic_constraint','mismatch')},
                max_initial_h_shift=max(abs(r['initial']['h0_discrete_shift']) for r in rows),
                max_RHS_envelope=np.max([r['max_sampled_RHS_envelope'] for r in rows],axis=0).tolist(),
                measured_elapsed_s=sum(r['elapsed_s'] for r in rows),
                norm='max across saved times and 52 fields: abs(a-b)/(1+max(abs(a),abs(b)))',
                claim='finite two-family, bounded-time grid comparison; no global coupled tail certificate')
    dump(target/'RESULTS.json',result);print(json.dumps(result,indent=2),flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--family',choices=['V','VIII','all'],default='all')
    p.add_argument('--output',default=str(ROOT/'evidence/curved_002'));p.add_argument('--summarize-only',action='store_true')
    args=p.parse_args()
    if not args.summarize_only:
        for family in ('V','VIII') if args.family=='all' else (args.family,):
            for order,nmu,tight in SCHEDULE:run_one(family,order,nmu,tight,args.output)
    if args.family=='all' or args.summarize_only:
        r=summarize(args.output);raise SystemExit(0 if r['status']=='PASS_SCOPED' else 1)
