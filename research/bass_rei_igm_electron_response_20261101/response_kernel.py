#!/usr/bin/env python3
"""Original BASS Einstein–P8–Peebles response to conditional electron-history changes.

Fixed original BASS geometry/matter/electron source. Does NOT install REI H/He
numerical history, predict CMB likelihood, or authorize a canonical DAG node.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,io,json
from pathlib import Path
import numpy as np
OUTER='45733f4ca2c0250cc94d934e0c58c7dbb0f6220350b2a303e25e55f77c787ffe'
INNER='8dd9258a3a50b6d0140c9305040c978f5a0790d907a8927769d3d27b5c63ab0d'
NESTED='tmp/km2n_ci/KM2N_S2_COMPLETE_SOURCE_SCIENCE.zip'
SOURCE_ROOT='research/dual_lane_km2n_20261031/results/'
OWNER='4137f942d2a95999f4e6627b71042e98f7afc1b7'
PANELS=40; GL=8; END=.25
def sha(b): return hashlib.sha256(b).hexdigest()
def source(zippath):
    b=Path(zippath).read_bytes()
    if sha(b)!=OUTER:raise ValueError('original outer SHA changed')
    with __import__('zipfile').ZipFile(io.BytesIO(b)) as z:
        if z.testzip():raise ValueError('outer CRC')
        inner=z.read(NESTED)
    if sha(inner)!=INNER:raise ValueError('original inner SHA changed')
    z=__import__('zipfile').ZipFile(io.BytesIO(inner))
    if z.testzip():raise ValueError('inner CRC')
    manifest=json.loads(z.read('MANIFEST.json'))
    if manifest['git_source_HEAD']!=OWNER or len(manifest['members'])!=50:raise ValueError('original physics identity')
    for name,receipt in manifest['members'].items():
        buf=z.read(name)
        if sha(buf)!=receipt['sha256'] or len(buf)!=receipt['bytes']:raise ValueError('forged source: '+name)
    return z
def npz(z,name):
    with np.load(io.BytesIO(z.read(SOURCE_ROOT+name)),allow_pickle=False) as a:
        return {k:a[k].copy() for k in a.files}
def compute(z,grid,dest):
    op=npz(z,f'KM2L_THOMSON_OPTICAL_GL{grid}_GLT8.npz')
    sc=npz(z,f'KM2N_FIRST_SOURCE_LEDGER_GL{grid}.npz')
    rays={12:288,16:512}[grid]
    h=op['hazard_nodes'].reshape(PANELS,GL,rays)
    node_tau=op['tau_nodes'].reshape(PANELS,GL,rays)
    edge=op['tau_edges']
    if edge.shape!=(PANELS+1,rays) or h.shape!=(PANELS,GL,rays):raise ValueError('original shape')
    if np.max(abs(edge-sc['tau']))!=0.:raise ValueError('original optical clock differs')
    if np.any(h<=0) or np.any(np.diff(edge,axis=0)<=0):raise ValueError('source cone')
    x,w=np.polynomial.legendre.leggauss(GL)
    dt=END/PANELS
    t=np.linspace(0,END,PANELS+1)[:-1,None]+dt*(x+1)/2
    weight=w*dt/2
    future=edge[-1][None,None,:]-node_tau
    survival=np.exp(-future)
    visibility=h*survival
    W=visibility*weight[None,:,None]
    dTau=np.diff(edge,axis=0)
    err_tau=float(np.max(abs(np.sum(h*weight[None,:,None],axis=1)-dTau)))
    P=-np.expm1(-edge[-1])
    err_P=float(np.max(abs(np.sum(W,axis=(0,1))-P)))
    if err_tau>2e-12 or err_P>3e-12:raise ValueError('original source integral identity')
    mean=(W*t[:,:,None]).sum((0,1))/P
    dProb=np.empty((PANELS,rays));dMean=np.empty_like(dProb)
    err_dP=0.
    for p in range(PANELS):
        priorW=W[:p].sum((0,1))
        priorTW=(W[:p]*t[:p,:,None]).sum((0,1))
        rem=edge[p+1][None,:]-node_tau[p]
        dp0=(W[p]*(1-rem)).sum(0)-dTau[p]*priorW
        dp1=(W[p]*t[p,:,None]*(1-rem)).sum(0)-dTau[p]*priorTW
        dp=np.exp(-edge[-1])*dTau[p]
        err_dP=max(err_dP,float(np.max(abs(dp-dp0))))
        dProb[p]=dp
        dMean[p]=(dp1-mean*dp)/P
    if err_dP>4e-12:raise ValueError('causal response normalization failure')
    def changed_mean(p,eps):
        excess=future.copy()
        excess[:p,:,:]+=eps*dTau[p][None,None,:]
        excess[p,:,:]+=eps*(edge[p+1][None,:]-node_tau[p])
        gg=h*np.exp(-excess)
        gg[p]*=(1+eps)
        return (gg*weight[None,:,None]*t[:,:,None]).sum((0,1))/-np.expm1(-(edge[-1]+eps*dTau[p]))
    errFD=0.
    for p in [0,3,9,19,29,39]:
        v=(changed_mean(p,3e-4)-changed_mean(p,-3e-4))/6e-4
        errFD=max(errFD,float(np.max(abs(v-dMean[p]))))
    if errFD>4e-9:raise ValueError('real-source finite electron response mismatch')
    def uniform(eps):
        gg=(1+eps)*h*np.exp(-(1+eps)*future)
        pp=-np.expm1(-(1+eps)*edge[-1])
        return (gg*weight[None,:,None]*t[:,:,None]).sum((0,1))/pp
    err_uniform=float(np.max(abs((uniform(1e-4)-uniform(-1e-4))/2e-4-dMean.sum(0))))
    if err_uniform>5e-9:raise ValueError('uniform electron linear response mismatch')
    sky=sc['w'][-1]/sum(sc['w'][-1])
    out=Path(dest)
    rayfile=out/f'GL{grid}_ELECTRON_PANEL_RESPONSE.csv.gz'
    with gzip.open(rayfile,'wt',encoding='utf8',newline='') as f:
        wr=csv.writer(f);wr.writerow(('panel','ray','u0','u1','tau_panel','dP','dMean_u','original_P','original_mean_u'))
        for p in range(PANELS):
            for i in range(rays):
                wr.writerow((p,i,f'{p*dt:.17g}',f'{(p+1)*dt:.17g}',*[f'{v:.17g}' for v in (dTau[p,i],dProb[p,i],dMean[p,i],P[i],mean[i])]))
    nodesfile=out/f'GL{grid}_ORIGINAL_RAY_VISIBILITY_NODES.csv.gz'
    with gzip.open(nodesfile,'wt',encoding='utf8',newline='') as f:
        wr=csv.writer(f);wr.writerow(('panel','gauss','ray','u','hazard','survival','visibility'))
        for p in range(PANELS):
            for k in range(GL):
                for i in range(rays):
                    wr.writerow((p,k,i,f'{t[p,k]:.17g}',*[f'{v:.17g}' for v in (h[p,k,i],survival[p,k,i],visibility[p,k,i])]))
    report={'grid':grid,'rays':rays,'new_response_rows':PANELS*rays,'original_visibility_nodes':PANELS*GL*rays,
            'tau_mean_sky':float(np.dot(sky,edge[-1])),'P_at_least_one_sky':float(np.dot(sky,P)),
            'conditional_last_scatter_mean_u_sky':float(np.dot(sky,mean)),
            'd_mean_u_d_uniform_electron_density_sky':float(np.dot(sky,dMean.sum(0))),
            'd_mean_u_d_earliest_panel_sky':float(np.dot(sky,dMean[0])),
            'd_mean_u_d_latest_panel_sky':float(np.dot(sky,dMean[-1])),
            'panel_sign_changes':[(p,float(np.dot(sky,dMean[p]))) for p in range(PANELS)],
            'max_tau_original_gauss_error':err_tau,'max_probability_original_gauss_error':err_P,
            'max_response_probability_identity_error':err_dP,
            'max_panel_actual_source_fd_error':errFD,'max_uniform_actual_source_fd_error':err_uniform,
            'original_new_IVPs':0,'REI_HHe_source_injected':False,
            'published_files':{p.name:sha(p.read_bytes()) for p in (rayfile,nodesfile)}}
    print('BASS_REI_SOURCE_VISIBILITY',json.dumps(report,sort_keys=True),flush=True)
    return report
def run(sourcezip,output):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    z=source(sourcezip)
    result={str(g):compute(z,g,out) for g in (12,16)}
    main={'science_unit':'BASS_KM2_REI_IGM_CAUSAL_VISIBILITY_ELECTRON_FRECHET',
      'original_BASS_owner':OWNER,'original_source_outer_SHA256':OUTER,
      'BASS_upper_DAG':'9/15_SCOPED','REI_central_DAG':'28/88_REPORTED','canonical_delta':0,
      'REI_F05_first_canonical_interval':'BLOCKED_AT_TICK_160_OF_131072',
      'source_matched_with_REI_F05':False,'new_model_response_rows':32000,'original_ray_visibility_nodes':256000,
      'grids':result,'production':'HOLD','merge':'HOLD','original_ivps_new':0}
    (out/'BASS_REI_CAUSAL_ELECTRON_RESPONSE.json').write_text(json.dumps(main,sort_keys=True,indent=2)+'\n')
    return main
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--source',required=True);a.add_argument('--output',required=True)
    p=a.parse_args();run(p.source,p.output)
