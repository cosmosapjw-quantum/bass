"""BASS source-locked VI0 physical null-Liouville and moving-sky scalar Kato.

This is collisionless test-photon transport on genuine parent PR311 VI0 tilted
Einstein/fluid backgrounds. Source intensity I0=1 is an explicitly independent
non-gravitating tracer, not an inherited CMB/Peebles/CE1 radiation source.
No production/collision/P8 screen implementation or source mutation.
"""
from __future__ import annotations
import csv, hashlib, json, sys
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
PR311_SHA='8d15551c2e0127ede4344f0969f8b7e251a09e3e'
PR311_SOURCE_BLOB='aa3c7d5ba4e3aca62efe0c8651df73b5d29ea8f9'
MAIN_SHA='9c6506e4e2087129a8b674ff10438e5db1a55c9d'
U_END=.2
TIMES=np.linspace(0,U_END,41)
# Unmodified PR311 import; in source-inclusive standalone mode we use locked copy.
parentdir=HERE.parents[1]/'vi0_manifold_20261101'
if (parentdir/'vi0_dynamics.py').exists():
    sys.path.insert(0,str(parentdir))
    import vi0_dynamics as parent
else:
    sys.path.insert(0,str(HERE))
    import parent_vi0_dynamics_source_locked as parent

FIELDS=['grid','case','gamma','u','ray','nx','ny','nz','E_normal','weight_sky_fraction',
        'I_bolometric','S_shear','Omega_background','v1_baryon','v2_baryon','v3_baryon']
MOMENT=['grid','case','gamma','u','rho_tracer','I_quad_xx','I_quad_yy','I_quad_zz',
        'I_quad_xy','I_quad_xz','I_quad_yz','sky_weight_sum','max_norm_gap',
        'max_I_over_E4_gap','moment_balance_gap','mean_direction_cosine']

def git_blob(raw:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\x00'+raw).hexdigest()

def source_guard(checkout:Path|None=None):
    # This source may be scientifically executed only with exact PR311 source identity.
    p=(checkout/'research/vi0_manifold_20261101/vi0_dynamics.py') if checkout else Path(parent.__file__)
    if git_blob(p.read_bytes())!=PR311_SOURCE_BLOB:
        raise RuntimeError('VI0_PARENT_311_BYTE_IDENTITY_FAILURE '+git_blob(p.read_bytes()))
    if checkout:
        assert parent.original_source_guard(checkout)==7
    return {'parent_sha':PR311_SHA,'parent_source_git_blob':PR311_SOURCE_BLOB,'checked_7_original_main_blobs':bool(checkout)}

def grids():
    # Source's 6-axis exact rank witness, original TypeII Lebedev26, independent GL8x16.
    n=np.array([[1.,0,0],[-1.,0,0],[0,1.,0],[0,-1.,0],[0,0,1],[0,0,-1.]])
    result={'AXIS6':(n,np.ones(6)/6)}
    n26=[];w26=[]
    for i in range(3):
        for sign in [-1.,1.]:
            v=np.zeros(3);v[i]=sign;n26.append(v);w26.append(1/21)
    for zero in range(3):
        ij=[k for k in range(3) if k!=zero]
        for a in [-1.,1.]:
            for b in [-1.,1.]:
                v=np.zeros(3);v[ij[0]]=a/np.sqrt(2);v[ij[1]]=b/np.sqrt(2)
                n26.append(v);w26.append(4/105)
    for a in [-1.,1.]:
      for b in [-1.,1.]:
        for c in [-1.,1.]:
            n26.append(np.array([a,b,c])/np.sqrt(3));w26.append(9/280)
    result['LEBEDEV26']=(np.asarray(n26),np.asarray(w26))
    mu,ww=leggauss(8)
    xx=[];weights=[]
    for z,wz in zip(mu,ww):
        radial=np.sqrt(1-z*z)
        for k in range(16):
            phi=2*np.pi*k/16
            xx.append([radial*np.cos(phi),radial*np.sin(phi),z]);weights.append(wz/32)
    result['GL8x16']=(np.asarray(xx),np.asarray(weights))
    for key,(n,w) in result.items():
        if abs(w.sum()-1)>1e-14 or np.max(abs(np.linalg.norm(n,axis=1)-1))>1e-15 or np.any(w<=0):
            raise AssertionError('Original quadrature normalization failed '+key)
    return result

def null_connection_correction(n,N):
    """Intrinsic curvature-only null turn: -Gamma(n,n) = -n x (Nn)."""
    return -np.cross(n,n@N.T)

def koszul_connection(N):
    """Independent spatial anholonomy oracle, formula explicit from BASS algebra.
       C^k_ab = epsilon_abd N^dk; 2 Gamma^k_ab=C^k_ab-C^a_bk+C^b_ka.
    """
    C=np.einsum('abd,dk->kab',parent.EPS,N)
    G=np.empty((3,3,3))
    for k in range(3):
      for a in range(3):
        for b in range(3):
          G[k,a,b]=.5*(C[k,a,b]-C[a,b,k]+C[b,k,a])
    return G

def ray_flow(n,S,N,W, *,incorrect_curvature_sign=False,drop_curvature=False):
    """Forward null Liouville sky characteristics in original BASS frame."""
    s=np.einsum('na,ab,nb->n',n,S,n)
    turn=np.zeros_like(n) if drop_curvature else null_connection_correction(n,N)
    if incorrect_curvature_sign:turn=-turn
    nd=-n@S.T+s[:,None]*n+turn+n@W.T
    return nd,s

def sphere_divergence(n,S):
    """Exact S^2 Jacobian for scalar angular characteristic: 3 n^a Sigma_ab n^b."""
    return 3*np.einsum('na,ab,nb->n',n,S,n)

def analytic_bianchi_I(sig,n0,time):
    """Independent exact no-curvature, no-frame-rotation shear control.
    Sigma=diag(sig), constant trace-free. The Hubble normalized photon energy
    E(t)=e^-t (sum_i n0_i^2 e^(-2sig_i t))^1/2.
    """
    ex=n0*np.exp(-np.asarray(sig)*time)
    amp=np.linalg.norm(ex)
    return ex/amp, np.exp(-time)*amp

def launch_state(z0,n,w):
    return np.r_[z0,np.asarray(n).ravel(),np.zeros(len(w)),np.log(w),np.zeros(len(w))]

def split(y,nray):
    z=y[:7];n=y[7:7+3*nray].reshape(nray,3)
    lo=7+3*nray
    return z,n,y[lo:lo+nray],y[lo+nray:lo+2*nray],y[lo+2*nray:lo+3*nray]

def rhs(t,y,gamma,nray):
    z,n,logE,logw,logI=split(y,nray)
    dz=parent.reduced_rhs(t,z,gamma)
    omega,S,N,v=parent.checked_chart(z,gamma)
    W=parent.eigenframe_W(S,N)
    nd,s=ray_flow(n,S,N,W)
    return np.r_[dz,nd.ravel(),-1-s,3*s,-4*(1+s)]

def sky_moments(n,logE,logw,logI,S):
    E=np.exp(logE);w=np.exp(logw);I=np.exp(logI)
    s=np.einsum('na,ab,nb->n',n,S,n)
    rho=np.dot(w,I)
    P=np.einsum('n,na,nb->ab',w*I,n,n)
    # independently evaluate angular-radiation conservation in two equivalent forms
    drho_direct=np.dot(w*I,3*s-4*(1+s))
    drho_from_moment=-4*rho-np.sum(S*P)
    return {'rho':rho,'pressure':P,'weightsum':w.sum(),
        'max_norm':np.max(abs(np.linalg.norm(n,axis=1)-1)),
        'liouville_relative':np.max(abs(np.exp(logI-4*logE)-1)),
        'balance':abs(drho_direct-drho_from_moment),
        'dipole':np.sum((w*I)[:,None]*n,axis=0)/rho}

def initial_conditions():
    # Same deterministic generator, same order as frozen PR311 physical_histories().
    rng=np.random.default_rng(31120261101)
    for i in range(12):
        sp0,sm0=rng.uniform(-.11,.11,2)
        p,r=rng.uniform(.3,.62,2)
        v=rng.uniform(-.14,.14,3)
        gamma=(1.0,1.1,4/3,1.65)[i%4]
        yield i,float(gamma),np.r_[sp0,sm0,p,r,v]

def projector_chain(v,vd,n,nd,w,wd):
    """Full moving-grid oblique scalar projector derivative and Kato action.
    Angular cell weights are positive and may be time dependent. The common
    w normalization cancels from P, but physics sky moments require raw w.
    """
    v=np.asarray(v,float);vd=np.asarray(vd,float);n=np.asarray(n,float)
    nd=np.asarray(nd,float);w=np.asarray(w,float);wd=np.asarray(wd,float)
    vel2=v@v;qq=1-n@v
    if vel2>=1 or np.any(qq<=0) or np.any(w<=0):raise ValueError('unphysical source/scalar projector')
    sder=nd@v+n@vd
    r=(1-vel2)**2/qq**4;a=w*qq
    rd=r*(-4*(v@vd)/(1-vel2)+4*sder/qq)
    ad=wd*qq-w*sder
    den=a@r
    P=np.outer(r,a)/den
    Pd=(np.outer(rd,a)+np.outer(r,ad))/den-P*(ad@r+a@rd)/den
    K=Pd@P-P@Pd
    return P,Pd,K

def projector_on_rays(z,n,w,gamma):
    om,S,N,v=parent.checked_chart(z,gamma)
    _,_,_,dv,qdec,W,Pi,Q=parent.ambient_rhs(om,S,N,v,gamma)
    nd,s=ray_flow(n,S,N,W)
    P,Pd,K=projector_chain(v,dv,n,nd,w,3*s*w)
    P_g,PD_g,K_g=projector_chain(v,W@v,n,n@W.T,w,np.zeros_like(w))
    P_bad,PD_bad,_=projector_chain(v,W@v,n,np.zeros_like(n),w,np.zeros_like(w))
    P_wf,PD_wf,_=projector_chain(v,dv,n,nd,w,np.zeros_like(w))
    return dict(P=P,Pd=Pd,K=K,gauge_norm=float(np.max(abs(PD_g))),
        bad_gauge_norm=float(np.max(abs(PD_bad))),
        untransported_weight_norm=float(np.max(abs(Pd-PD_wf))),
        rank1_idempotence=float(np.max(abs(P@P-P))),
        kato_commutator=float(np.max(abs(K@P-P@K-Pd))),
        projector_pure_gauge_parity=float(np.max(abs(P-P_g))))

def integrate_one(case, gamma, z0, grid, n0,w0,*,t_eval=TIMES):
    y0=launch_state(z0,n0,w0)
    solution=solve_ivp(lambda t,y:rhs(t,y,gamma,len(w0)),(0,U_END),y0,
          t_eval=t_eval,method='DOP853',rtol=2e-11,atol=2e-13)
    if not solution.success:raise RuntimeError(solution.message)
    rayrows=[];momrows=[]
    for t,y in zip(solution.t,solution.y.T):
        z,n,logE,logw,logI=split(y,len(w0));om,S,N,v=parent.checked_chart(z,gamma)
        d=sky_moments(n,logE,logw,logI,S)
        s=np.einsum('na,ab,nb->n',n,S,n)
        for k in range(len(n)):
            rayrows.append([grid,case,gamma,float(t),k,*map(float,n[k]),
                 float(np.exp(logE[k])),float(np.exp(logw[k])),float(np.exp(logI[k])),
                 float(s[k]),float(om),*map(float,v)])
        P=d['pressure']
        momrows.append([grid,case,gamma,float(t),float(d['rho']),
             float(P[0,0]),float(P[1,1]),float(P[2,2]),float(P[0,1]),float(P[0,2]),float(P[1,2]),
             float(d['weightsum']),float(d['max_norm']),float(d['liouville_relative']),
             float(d['balance']),float(np.linalg.norm(d['dipole']))])
    return rayrows,momrows,solution

def write_csv(path,fields,rows):
    path.parent.mkdir(exist_ok=True,parents=True)
    with path.open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(fields);writer.writerows(rows)

def run(output=ROOT/'data', *,cases=12,grid_names=('AXIS6','LEBEDEV26','GL8x16')):
    source=source_guard()
    output=Path(output);output.mkdir(exist_ok=True,parents=True)
    available=grids();ra=[];mo=[];cases_info={};max_kato=0;max_gauge=0;max_kato_nonunitary=0
    for case,gamma,z0 in list(initial_conditions())[:cases]:
      for key in grid_names:
        n0,w0=available[key]
        rayrows,momrows,sol=integrate_one(case,gamma,z0,key,n0,w0)
        ra.extend(rayrows);mo.extend(momrows)
        # P, Pdot and K on the FULL native physical angular grid, including GL8x16.
        z,n,lE,lw,lI=split(sol.y[:,-1],len(w0));wf=np.exp(lw)
        ob=projector_on_rays(z,n,wf,gamma)
        max_kato=max(max_kato,ob['kato_commutator'],ob['rank1_idempotence'])
        max_gauge=max(max_gauge,ob['gauge_norm'],ob['projector_pure_gauge_parity'])
        max_kato_nonunitary=max(max_kato_nonunitary,float(np.max(abs(ob['K']+ob['K'].T))))
        d={name:float(max(abs(row[MOMENT.index(name)]) for row in momrows)) for name in ('max_norm_gap','max_I_over_E4_gap','moment_balance_gap')}
        cases_info[f'{key}:case{case}']={
            'original_gamma':gamma,'original_seed_7D':list(map(float,z0)),
            'new_collisionless_photon_ray_labels':len(w0),'time_rows':len(momrows),
            'max_checks':d,'endpoint_rho':float(momrows[-1][MOMENT.index('rho_tracer')]),
            'endpoint_skyweight_sum':float(momrows[-1][MOMENT.index('sky_weight_sum')]),
            'endpoint_rho_and_sky_P':{k:float(momrows[-1][MOMENT.index(k)]) for k in ('I_quad_xx','I_quad_yy','I_quad_zz','I_quad_xy','I_quad_xz','I_quad_yz')},
            'projector_physical_moving_grid':{k:v for k,v in ob.items() if isinstance(v,(int,float))}}
      print('VI0_PHYSICAL_NULL',case,'gamma',gamma, 'rows so far',len(ra),flush=True)
    write_csv(output/'VI0_NULL_RAY_PHYSICAL.csv',FIELDS,ra)
    write_csv(output/'VI0_NULL_MOMENT_HISTORY.csv',MOMENT,mo)
    # Real angular-resolution impact on same VI0 physical source and initial test photons.
    g23=[]
    for k in range(cases):
        d={g:cases_info[f'{g}:case{k}'] for g in grid_names}
        pair=d.get('GL8x16',{});ref=d.get('LEBEDEV26',{})
        if pair and ref:
            g23.append({'case':k,'gamma':pair['original_gamma'],
              'GL128_vs_leb26_endpoint_rho_abs':abs(pair['endpoint_rho']-ref['endpoint_rho']),
              'GL128_vs_axis6_endpoint_rho_abs':abs(pair['endpoint_rho']-d['AXIS6']['endpoint_rho']),
              'axis6_endpoint_weight_drift':abs(d['AXIS6']['endpoint_skyweight_sum']-1),
              'GL128_endpoint_weight_drift':abs(pair['endpoint_skyweight_sum']-1)})
    result={'schema':'bass.vi0.null_liouville_photon_canonical_source_scoped.v1',
      'source':source,'source_gamma_families':[1.,1.1,4/3,1.65],
      'background':'original PR311 twelve independently sourced exact VI0 tilted gamma-law fluid seed geometries; reintegrated unchanged',
      'photon_source':'initially isotropic bolometric I0=1 positive non-gravitating test photons, NO original electron/Thomson/CMB source',
      'theory':['null_direction=-Sigma.n+(n.Sigma.n)n-nx(Nn)+W.n',
                'Eprime_over_E=-1-n.Sigma.n','Iprime_over_I=-4(1+n.Sigma.n)',
                'dln_w=3 n.Sigma.n','rho_prime=-4rho-Sigma:Pphoton',
                'full_moving_grid_scalar_projector_Kato_commutator'],
      'reused_background_initial_value_problems':cases,'new_distinct_gravitating_einstein_ivps':0,
      'new_collisionless_ray_transport_runs':cases*len(grid_names),
      'ray_physical_rows':len(ra),'radiation_moment_rows':len(mo),
      'maximum_angular_unit_sphere_residual':max(x['max_checks']['max_norm_gap'] for x in cases_info.values()),
      'maximum_liouville_invariant_error':max(x['max_checks']['max_I_over_E4_gap'] for x in cases_info.values()),
      'maximum_discrete_moment_balance_gap':max(x['max_checks']['moment_balance_gap'] for x in cases_info.values()),
      'maximum_Kato_or_idempotent_error':max_kato,'maximum_pure_gauge_projector_error':max_gauge,
      'nonzero_oblique_Kato_symmetric_part_max':max_kato_nonunitary,
      'cross_grid_comparison':g23,'runs':cases_info,
      'upper_scoped_dag':'9/15','new_completed_upper_nodes':0,'original_G_DYN_MANIFOLD_VI0':'PARTIAL',
      'P_MIG_II_PREFLIGHT':'OPEN','JOIN_J1':'0/2_FULL_PASS_HOLD',
      'physical_N_screen_polarized':'NOT_RUN','real_source_collision':'NOT_RUN',
      'continuum_certificate':'NOT_RUN','native_subagent':'NOT_RUN',
      'production_ready':False,'merge_ready':False,'auto_next':False}
    (output/'VI0_NULL_RESULTS.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    print('SUMMARY',json.dumps({k:result[k] for k in ('new_collisionless_ray_transport_runs','ray_physical_rows','radiation_moment_rows','maximum_angular_unit_sphere_residual','maximum_liouville_invariant_error','maximum_discrete_moment_balance_gap','maximum_Kato_or_idempotent_error','maximum_pure_gauge_projector_error','nonzero_oblique_Kato_symmetric_part_max')}),flush=True)
    return result

if __name__=='__main__':run()
