#!/usr/bin/env python3
"""BASS KM2 source-owned Thomson visibility on frozen KM2N/KM2L rays.

Only the causal survival-weighted hazard kernel, not a source-weighted CMB
last-scattering probability, and not a merger with CE1AS or REI H/He.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.interpolate import PchipInterpolator

ROOT=Path(__file__).resolve().parent
MANIFEST=ROOT/'SOURCE_MANIFEST.json'
SOURCE=ROOT/'source_inputs'
END_U=0.25
GRID=(12,16)
TIME=41
ORDER=8


def fail_if(condition, label):
    if bool(condition): raise ArithmeticError(label)


def source_arrays(gl:int,source=SOURCE,manifest=MANIFEST):
    if gl not in GRID: raise ValueError('source grid not original GL12 or GL16')
    m=json.loads(Path(manifest).read_text())
    fail_if(m.get('parent_head')!='4137f942d2a95999f4e6627b71042e98f7afc1b7','KM2N parent identity mismatch')
    data={}
    for tag,basename in [('ledger',f'KM2N_FIRST_SOURCE_LEDGER_GL{gl}.npz'),('opacity',f'KM2L_THOMSON_OPTICAL_GL{gl}_GLT8.npz')]:
        p=Path(source)/basename
        sha=hashlib.sha256(p.read_bytes()).hexdigest()
        fail_if(sha!=m['files'][basename],'immutable KM2N/KM2L source SHA changed: '+basename)
        with np.load(p,allow_pickle=False) as z:
            data[tag]={k:z[k].copy() for k in z.files}
    a,b=data['ledger'],data['opacity']
    n=2*gl*gl
    shapes={'time':(41,),'nu':(41,),'D':(41,n),'w':(41,n),'mu':(41,n),'tau':(41,n),'n':(41,n,3)}
    for k,shape in shapes.items(): fail_if(a[k].shape!=shape,'original ledger shape drift: '+k)
    for k,shape in {'hazard_nodes':(320,n),'hazard_edges':(41,n),'tau_nodes':(320,n),'tau_edges':(41,n)}.items():
        fail_if(b[k].shape!=shape,'original rate shape drift: '+k)
    for arr in (a['time'],a['nu'],a['D'],a['w'],a['mu'],a['tau'],a['n'],b['hazard_nodes'],b['hazard_edges'],b['tau_nodes'],b['tau_edges']):
        fail_if(not np.all(np.isfinite(arr)),'non-finite source')
    fail_if(max(abs(a['time']-np.linspace(0,END_U,TIME)))>2e-14,'wrong normal time')
    fail_if(np.any(a['w']<=0) or np.min(a['nu'])<=0 or np.min(a['D'])<=0,'non-positive physical source')
    fail_if(np.max(abs(np.linalg.norm(a['n'][-1],axis=1)-1))>2e-12,'bad photon normal direction')
    fail_if(np.max(abs(a['w'][-1].sum()-4*math.pi))>1e-7,'incomplete angular quadrature')
    fail_if(np.max(abs(b['tau_edges']-a['tau']))>1e-13,'two independent source optical histories differ')
    fail_if(np.max(abs(b['hazard_edges']-a['nu'][:,None]*a['D']))>2e-11,'original Thomson nu*D != hazard')
    fail_if(np.min(np.diff(a['tau'],axis=0))<=0,'source optical depth not monotone')
    fail_if(np.max(np.diff(a['mu'],axis=0))>2e-12,'source photon redshift not monotone')
    return a,b


def integrate_visibility_arrays(hazard, tau_sample, tau_edge, d_u_weight):
    """Independent GL integrals of direction-wise survival-weighted hazard.

    The supplied arrays are already source time-node sampled. This function
    intentionally takes independent hazard and tau to detect owner mismatch.
    """
    T=np.asarray(tau_edge,dtype=float)
    h=np.asarray(hazard,dtype=float)
    tt=np.asarray(tau_sample,dtype=float)
    weights=np.asarray(d_u_weight,dtype=float)
    fail_if(h.shape!=tt.shape or h.ndim!=2 or weights.shape!=(len(h),),'bad visibility input shapes')
    fail_if(np.any(h<0) or not np.all(np.isfinite(h)),'bad collision hazard')
    fail_if(np.any(tt>T[None,:]+1e-10) or np.any(tt<0),'invalid source causal optical time')
    g=h*np.exp(tt-T[None,:])
    I=np.einsum('k,kj->j',weights,g)
    expected=-np.expm1(-T)
    mismatch=float(np.max(np.abs(I-expected)))
    if mismatch>2e-10:
        raise ArithmeticError(f'visibility source inconsistency: {mismatch:.15g}')
    return g,I,expected,mismatch


def run_grid(gl:int,source=SOURCE,manifest=MANIFEST):
    ledger,original=source_arrays(gl,source,manifest)
    u=ledger['time'];tau=original['tau_edges'];last=tau[-1]
    rates=original['hazard_nodes'];tau_q=original['tau_nodes'];ray=len(last)
    gn,gw=leggauss(ORDER);width=END_U/(TIME-1)
    t_nodes=np.repeat(u[:-1],ORDER)+np.tile((gn+1)*width/2,TIME-1)
    du_weights=np.tile(gw*width/2,TIME-1)
    tau_reconstructed=np.cumsum(np.einsum('m,kmj->kj',gw*width/2,rates.reshape(TIME-1,ORDER,ray)),axis=0)
    tau_reconstructed=np.vstack([np.zeros(ray),tau_reconstructed])
    tau_error=float(np.max(abs(tau_reconstructed-tau)))
    fail_if(tau_error>3e-12,'same-source opacity integral mismatches tau edges')
    g,I,expected,gap=integrate_visibility_arrays(rates,tau_q,last,du_weights)
    p=expected
    mean=np.einsum('k,kj->j',du_weights*t_nodes,g)/p
    second=np.einsum('k,kj->j',du_weights*t_nodes**2,g)/p
    sigma=np.sqrt(np.maximum(0.,second-mean*mean))
    qs={}
    # Continuous interpolation of actually sampled original physical optical time;
    # PCHIP is monotonic, not a continuum ODE error certificate.
    for quantile in (.1,.5,.9):
        target=last+np.log(np.exp(-last)+quantile*(-np.expm1(-last)))
        uq=np.empty(ray)
        for j in range(ray):
            tq=np.r_[0.,tau_q[:,j],last[j]]
            tt=np.r_[0.,t_nodes,END_U]
            fail_if(np.any(np.diff(tq)<=0),'nonmonotone original tau quadrature')
            uq[j]=float(PchipInterpolator(tq,tt)(target[j]))
        qs[quantile]=uq
    z50=np.empty(ray)
    for j in range(ray):
        energy50=float(PchipInterpolator(u,ledger['mu'][:,j])(qs[.5][j]))
        z50[j]=energy50/ledger['mu'][-1,j]-1.
    fail_if(np.min(z50)<0 or np.any(np.diff(np.array([qs[z] for z in (.1,.5,.9)]),axis=0)<0),'physical redshift or quantile ordering failed')
    w=ledger['w'][-1];n=ledger['n'][-1];w4=w/w.sum() # normalize finite GL solid angle to exact unit mass
    av=lambda x:float(np.dot(w4,x))
    high=1-np.exp(-(last-tau[32]))
    # Probability of an event in the final [u=0.2,u=0.25] interval, conditioned on >=1.
    late=high/p
    def angular_moments(obs):
        c=np.asarray(obs)-av(obs)
        dip=np.einsum('r,ri->i',w4*c,n)
        q=np.einsum('r,ri,rj->ij',w4*c,n,n)-np.eye(3)*(np.dot(w4,c)/3.)
        q=(q+q.T)/2.
        return {'dipole':dip.tolist(),'quadrupole':q.tolist(),'quadrupole_frobenius':float(np.linalg.norm(q))}
    # Raw ray-averaged unweighted tau is deliberately not angular-sky average.
    Xdip=np.column_stack([np.ones(ray),n]);coef=np.linalg.lstsq(Xdip*np.sqrt(w4[:,None]),last*np.sqrt(w4),rcond=None)[0]
    sigma_tau=float(np.sqrt(np.dot(w4,(last-av(last))**2)))
    dipole_fit_fraction=float(np.sqrt(np.dot(w4,(last-Xdip@coef)**2))/sigma_tau)
    summary={
        'grid':f'GL{gl}', 'original_ray_count':ray,'original_time_edges':TIME,
        'original_rate_quadrature_nodes':len(t_nodes),'observer_u':END_U,
        'weighted_tau_mean':av(last),'unweighted_tau_mean':float(np.mean(last)),
        'tau_ray_range':[float(np.min(last)),float(np.max(last))],
        'mean_at_least_one_collision_probability':av(p),
        'conditional_last_event_mean_u':av(mean),'conditional_last_event_std_u_mean':av(sigma),
        'median_time_sky_mean':av(qs[.5]),
        'median_time_range':[float(np.min(qs[.5])),float(np.max(qs[.5]))],
        'median_event_to_observer_redshift_mean':av(z50),
        'median_event_to_observer_redshift_range':[float(np.min(z50)),float(np.max(z50))],
        'probability_last_event_in_final_0p05_conditional':av(late),
        'source_opacity_integral_maxabs_error':tau_error,
        'survival_visibility_GL_quadrature_maxabs_residual':gap,
        'time_GL_normalized_event_mean_error':float(np.max(abs(I/p-1))),
        'event_time_angular_moments':angular_moments(mean),
        'opacity_angular_moments':angular_moments(last),
        'tau_dipole_fit_unexplained_rms_fraction':dipole_fit_fraction,
        'median_redshift_angular_moments':angular_moments(z50),
        'new_owner_Einstein_IVPs':0,'reused_owner_einstein_p8_peebles_source':True,
        'not_full_photon_CMB_visibility':True,
    }
    ray_fields=['grid','ray','nobs_x','nobs_y','nobs_z','w_obs_solid_angle','tau_total','p_ge1','last_event_mean_u','last_event_std_u','last_event_q10_u','last_event_q50_u','last_event_q90_u','event_q50_redshift','p_last_event_u_ge_0p2']
    rays=[(f'GL{gl}',j,*n[j].tolist(),w[j],last[j],p[j],mean[j],sigma[j],qs[.1][j],qs[.5][j],qs[.9][j],z50[j],late[j]) for j in range(ray)]
    profile_fields=['grid','u','weighted_mean_hazard','weighted_mean_tau_remaining','weighted_mean_visibility_du','weighted_mean_visibility_conditional_du']
    g_edges=original['hazard_edges']*np.exp(tau-last[None,:]);muhaz=np.einsum('j,tj->t',w4,original['hazard_edges']);meantau=np.einsum('j,tj->t',w4,last[None,:]-tau)
    prof=[(f'GL{gl}',float(u[k]),float(muhaz[k]),float(meantau[k]),float(w4@g_edges[k]),float(w4@(g_edges[k]/p))) for k in range(TIME)]
    arrays={'u_quadrature':t_nodes,'du_weight':du_weights,'visibility_probability_per_u':g,'tau_remaining_quadrature':last[None,:]-tau_q,'p_event':p,'last_event_mean_u':mean,'last_event_median_u':qs[.5],'median_scatter_redshift':z50,'n_observer':n,'sky_quadrature_w':w}
    return summary,ray_fields,rays,profile_fields,prof,arrays


def write_csv(path,fields,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='') as f:
        wr=csv.writer(f);wr.writerow(fields);wr.writerows(rows)


def run(output=ROOT/'results'):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    records=[];profiles=[];cases={}
    for gl in GRID:
        summary,rf,rr,pf,pr,arrays=run_grid(gl)
        records.extend(rr);profiles.extend(pr);cases[f'GL{gl}']=summary
        np.savez_compressed(out/f'KM2_VISIBILITY_GL{gl}.npz',**arrays)
        print('ORIGINAL_BASS_VISIBILITY',gl,'rays',len(rr),'tau',summary['weighted_tau_mean'],
              'mean_u',summary['conditional_last_event_mean_u'],'median_z',summary['median_event_to_observer_redshift_mean'],flush=True)
    write_csv(out/'KM2_ORIGINAL_SKY_VISIBILITY_RAYS.csv',rf,records)
    write_csv(out/'KM2_ORIGINAL_SKY_VISIBILITY_TIME.csv',pf,profiles)
    report={'schema':'bass.km2.source_owned_thomson_visibility.v1','asof_kst':'2026-11-01',
      'parent_pr':297,'parent_head':'4137f942d2a95999f4e6627b71042e98f7afc1b7',
      'read_only_science_reference':'BASS PR307 CE1AS separate massless collisionless six-cell owner, no electron opacity',
      'original_source':json.loads(MANIFEST.read_text()),
      'physics':'original KM2J-N Einstein-P8-Peebles baryon-proper chemistry with normal-clock source and tilted ray hazard nu*D, no new Einstein IVPs',
      'definition':'g(u,n|uobs)=h(u,n)*exp[-tau(uobs,n)+tau(u,n)], h=nH*x_e*sigmaT*c*Tstar*D. Conditional last-event probability only for a photon existing at u=0; not complete source-weighted last scattering or observed CMB visibility.',
      'cases':cases,'physical_ray_observable_rows':len(records),'time_profile_rows':len(profiles),
      'new_owner_einstein_ivps':0,'BASS_upper':'9/15 SCOPED_OR_SOURCE_MAPPED','new_completed_upper_nodes':0,'KM2':'PARTIAL','OB1':'PARTIAL_NOT_SOURCE_MATCHED_TO_CE1AS','production_ready':False,'merge_ready':False,'auto_next':False,
      'unresolved':['same-source CE1AS D_A vs KM2 electron history (different Einstein owner)', 'full source-weighted multiorder photon last scattering','actual CMB visibility/likelihood','angular/time continuum bound','thermal first law / Lyalpha resonant recoil']}
    (out/'KM2_VISIBILITY_RESULTS.json').write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'results');a=p.parse_args();run(a.output)