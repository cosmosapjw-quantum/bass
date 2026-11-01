#!/usr/bin/env python3
"""CE1AS: one genuinely independent isotropic Einstein--Vlasov FLRW reference.

The isotropic massless collisionless distribution is a DIFFERENT angular source
than the original reflection-even anisotropic six-cell distribution. We match
its physical initial energy monopole, not its pressure tensor or the mean
expansion rate. BASS original six-cell input and CE1AR fixed-z Bianchi
observables are immutable scientific witnesses, never recomputed or overwritten.

Conventions: (-,+,+,+), Lambda=0, 8pi G=1, u=t/Tstar,
H dimensionless, D_A/(c*Tstar) dimensionless, massless p=rho/3.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp, quad

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
INPUT=ROOT/'ancestor'/'CE1AP_DIRECTIONAL_GEODESIC.csv'
BEAMS=ROOT/'ancestor'/'CE1AR_FIXED_Z_BEAMS.csv'
OUTPUT=ROOT/'data'
ORIGINAL_SIX_CELL_SHA='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
PARENT_PR=306
PARENT_HEAD='edfed2152c8fc28a6c96fc59341c4d10538c2937'
CE1AP_SHA='98bd1ed2909abfc5e47da12003354d6a3c75bee8ef0ecc13144b1a4c110a1207'
CE1AR_BEAMS_SHA='e1540cdff5384a96d67b579d125a785105b6fb995dcc3bc8d92744e1bfe780ac'
SHELLS=(.005,.01,.015,.020,.025,.030)
ORDERS=(8,16,24)
EPS=(-.035,0.,.035)
UO=.08

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
    with Path(p).open(newline='') as f:return list(csv.DictReader(f))
def csvout(path,header,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='') as f:
        w=csv.writer(f);w.writerow(header);w.writerows(data)

def original_constraint(ancestor=INPUT, *,strict=True):
    """Infer original three axis expansion rates FROM frozen original ray drift.
    E0=h1*h2+h1*h3+h2*h3 (Bianchi I Hamiltonian constraint)."""
    if strict and sha(ancestor)!=CE1AP_SHA:raise ArithmeticError('original six-cell CE1AP input SHA mismatch')
    raw=read(ancestor)
    if len(raw)!=16842:raise ArithmeticError('CE1AP original 16842 records missing')
    first={}
    for r in raw:
        if r['dir'] not in ('x','y','z') or float(r['u'])!=0.:continue
        gl=int(r['GL']);eps=float(r['eps']);axis=r['dir']
        if gl not in ORDERS or eps not in (-.035,.035):raise ArithmeticError('original axis label mismatch')
        key=(gl,eps)
        if axis in first.setdefault(key,{}):raise ArithmeticError('duplicated initial original axis')
        first[key][axis]=(-float(r['drift_base']),-float(r['drift_base'])-float(r['delta_drift']))
    if len(first)!=6 or any(set(x)!=set('xyz') for x in first.values()):
        raise ArithmeticError('original six-cell initial axis data incomplete')
    initial=[]
    for (gl,eps),axes in sorted(first.items()):
        for finite in (False,True):
            H=np.array([axes[a][int(finite)] for a in 'xyz'],float)
            rho=float(H[0]*H[1]+H[0]*H[2]+H[1]*H[2])
            initial.append({'GL':gl,'eps':eps if finite else 0.,'H':H.tolist(),'rho':rho})
    energies=np.asarray([x['rho'] for x in initial]);rho0=float(np.mean(energies))
    if rho0<=0 or np.max(abs(energies-rho0))>5e-12:raise ArithmeticError('six-cell initial energy/source mismatch')
    return rho0,initial,float(np.max(abs(energies-rho0)))

def flrw_ivp(rho0,uo=UO,method='DOP853'):
    """Genuinely integrate Einstein+isotropic massless Vlasov conservation.
    3H^2=rho, rho'=-4H*rho, a'=aH. Initial a=1, rho=rho0."""
    if rho0<=0 or uo<=0:raise ValueError('nonpositive initial energy or horizon')
    H0=math.sqrt(rho0/3.)
    def rhs(u,x):
        a,rho=x
        if a<=0 or rho<=0:raise ArithmeticError('unphysical FLRW radiation state')
        h=math.sqrt(rho/3.)
        return [a*h,-4*h*rho]
    times=np.linspace(0,uo,401)
    sol=solve_ivp(rhs,(0.,uo),(1.,rho0),t_eval=times,dense_output=True,
        method=method,rtol=8e-13,atol=2e-14)
    if not sol.success:raise ArithmeticError(sol.message)
    a,rho=sol.y
    h=np.sqrt(rho/3.)
    expected=np.sqrt(1+2*H0*times)
    err=float(np.max(np.abs(a/expected-1)))
    err_rho=float(np.max(np.abs(rho*a**4/rho0-1)))
    err_constraint=float(np.max(np.abs(3*h*h-rho)))
    if max(err,err_rho,err_constraint)>1.5e-11:raise ArithmeticError('independent Friedmann IVP failed exact radiation oracle')
    history=np.column_stack([times,a,rho,h,rho/3,rho*a**4,3*h*h-rho])
    return {'H0':H0,'H_observer':H0/(1+2*H0*uo),'sol':sol,'history':history,
            'max_scale_relative':err,'max_rhoa4_relative':err_rho,'max_friedmann_absolute':err_constraint}

def shell(rho0,ivp,z,uo=UO):
    H0=ivp['H0'];ao=math.sqrt(1+2*H0*uo)
    if not 0<z<ao-1:raise ValueError('shell outside independent physical FLRW source epoch')
    ae=ao/(1+z)
    ue=(ae*ae-1)/(2*H0)
    if ue<0 or ue>=uo:raise ArithmeticError('invalid source shell')
    da_analytic= z/(ivp['H_observer']*(1+z)**2)
    # Independent numerical solution + light integral, not the closed-form identity.
    state_e=ivp['sol'].sol(ue);state_o=ivp['sol'].sol(uo)
    ae_num=float(state_e[0]);ao_num=float(state_o[0]);
    chi,chierr=quad(lambda u: 1/float(ivp['sol'].sol(u)[0]),ue,uo,
                    epsabs=2e-13,epsrel=2e-13)
    da_num=ae_num*chi
    root_err=abs(ao_num/ae_num-(1+z))
    if abs(da_num-da_analytic)>2e-11 or root_err>2e-11:raise ArithmeticError('FLRW IVP ray mismatch')
    return {'z':z,'u_emit':ue,'D_A':da_analytic,'D_A_integrated':da_num,
            'ray_abs_gap':abs(da_num-da_analytic),'redshift_abs_gap':root_err,
            'a_emit':ae,'a_obs':ao}

def run(ancestor=INPUT,beams=BEAMS,out=OUTPUT,*,strict=True,
        ce1ap_metadata=None,ce1ar_metadata=None):
    ancestor=Path(ancestor);beams=Path(beams);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    if strict:
        if sha(beams)!=CE1AR_BEAMS_SHA:raise ArithmeticError('CE1AR original fixed-z beam SHA mismatch')
    else:
        # New GitHub CI runs the ORIGINAL PR301/306 source owners, so generated
        # CSV bytes can differ across Python/BLAS. Never accept unbound CSVs.
        if ce1ap_metadata is None or ce1ar_metadata is None:
            raise ArithmeticError('CI-replayed inputs require BOTH original-owner metadata ledgers')
        pm=json.loads(Path(ce1ap_metadata).read_text())
        bm=json.loads(Path(ce1ar_metadata).read_text())
        if (pm.get('source_sha256')!=ORIGINAL_SIX_CELL_SHA or pm.get('new_IVPs')!=9 or
            pm.get('parent_head')!='d94843f2b63638d36244d951eccdbb81f3a64357' or
            bm.get('source_sha256')!=ORIGINAL_SIX_CELL_SHA or
            bm.get('parent_ce1aq_head')!='bbebf7f0cdc3e23eec422f67118e8d402afb106c' or
            bm.get('reused_owner_IVPs')!=9 or bm.get('real_beam_rows')!=5562):
            raise ArithmeticError('remote GitHub physical source owner/parent not accepted')
    rho0,initial,source_gap=original_constraint(ancestor,strict=strict)
    h0=math.sqrt(rho0/3.)
    ivp=flrw_ivp(rho0)
    shells={z:shell(rho0,ivp,z) for z in SHELLS}
    source_h=np.array(next(x['H'] for x in initial if x['GL']==24 and x['eps']==0.))
    mean_h=float(np.mean(source_h))
    shear_source=3*mean_h**2-rho0
    if shear_source<=0:raise ArithmeticError('baseline original has no positive shear; audit source provenance')
    if abs(shear_source-sum((source_h-mean_h)**2)/2)>1e-11:raise ArithmeticError('Bianchi shear constraint error')
    csvout(out/'CE1AS_FLRW_HISTORY.csv',
           ['u','a_flrw','rho_flrw','H_flrw','p_flrw','radiation_rhoa4','friedmann_residual'],ivp['history'])
    csvout(out/'CE1AS_FLRW_SHELLS.csv',
           ['z','u_emit','D_A_FLRW','D_A_ODE_light','D_A_absolute_gap','redshift_abs_gap','a_emit','a_obs'],
           [[s[k] for k in ('z','u_emit','D_A','D_A_integrated','ray_abs_gap','redshift_abs_gap','a_emit','a_obs')] for s in shells.values()])
    old=read(beams)
    if len(old)!=5562:raise ArithmeticError('CE1AR beam count changed')
    grouped=defaultdict(list)
    output=[]
    seen=set()
    hdr=['GL','eps','z','direction','nx','ny','nz','D_A_Bianchi','D_A_FLRW_E0_matched',
         'fractional_DA_difference','D_A_equal_volume_proxy','proxy_fractional_error_to_FLRW',
         'Bianchi_fractional_to_old_proxy','model_source_multipoles_identical',
         'comparison_kind']
    for r in old:
        gl=int(r['GL']);eps=float(r['eps']);z=float(r.get('z_target',r.get('z')));direction=r['direction']
        if gl not in ORDERS or eps not in EPS or z not in SHELLS:
            raise ArithmeticError('unexpected source grid or shell')
        key=(gl,eps,z,direction)
        if key in seen:raise ArithmeticError('duplicate input sky ray')
        seen.add(key)
        DA=float(r.get('D_A_over_cTstar',r.get('D_A')));f=shells[z]['D_A'];proxy=float(r.get('equal_volume_isotropic_D_A',r.get('isotropic_proxy_D_A')))
        if not(DA>0 and f>0 and proxy>0):raise ArithmeticError('negative sample beam')
        ratio=DA/f-1;pr=proxy/f-1
        original=float(r.get('fractional_anisotropy_vs_isotropic_proxy',r.get('anisotropy')))
        if abs((DA/proxy-1)-original)>2e-13:raise ArithmeticError('original Bianchi proxy identity broken')
        output.append([gl,eps,z,direction,r['nx'],r['ny'],r['nz'],DA,f,ratio,proxy,pr,
                       original,False,'ENERGY_MONOPOLE_MATCHED_ISOTROPIZED_COLLISIONLESS_VLASOV'])
        grouped[(gl,eps,z)].append((direction,ratio,pr,DA))
    if len(seen)!=5562:raise ArithmeticError('not all original rays transported into comparator')
    # Three frozen physical anchor observables, from the original independent
    # CE1AR owner at GL24/eps0/z=.02. Guard cross-codepath scientific parity.
    anchor={'x':.028044169626674734,'y':.048605391588600874,'z':.04260215256293194}
    for row in output:
        if row[0]==24 and row[1]==0. and row[2]==.02 and row[3] in anchor:
            if abs(row[7]-anchor[row[3]])>2e-11:
                raise ArithmeticError('source-owner original Bianchi fixed-z anchor mismatch')
    csvout(out/'CE1AS_BIANCHI_VS_FLRW.csv',hdr,output)
    sumrows=[]
    axes_for_graph=[]
    for (gl,eps,z),grp in sorted(grouped.items()):
        if len(grp)!=103:raise ArithmeticError('direction sampling changed')
        axes={d:y for d,y,_,_ in grp if d in ('x','y','z')}
        if set(axes)!=set('xyz'):raise ArithmeticError('axes unavailable')
        fib=[y for d,y,_,_ in grp if d.startswith('fib')]
        if len(fib)!=96:raise ArithmeticError('sky fibonacci sample count changed')
        allvals=np.array([q[1] for q in grp]);vals=np.array(fib)
        proxies=np.array([q[2] for q in grp])
        sumrows.append([gl,eps,z,len(grp),axes['x'],axes['y'],axes['z'],
                      axes['x']-axes['z'],float(np.min(vals)),float(np.max(vals)),
                      float(np.mean(vals)),float(np.sqrt(np.mean(vals*vals))),
                      float(np.mean(proxies)),float(np.max(abs(proxies)))])
        if gl==24 and eps==0:axes_for_graph.append((z,axes))
    csvout(out/'CE1AS_SHELL_SOURCE_SKY_SUMMARY.csv',
           ['GL','eps','z','direction_count','delta_x','delta_y','delta_z','axis_x_minus_z',
            'fib96_min','fib96_max','fib96_sample_mean','fib96_sample_rms',
            'old_proxy_fractional_bias_mean','old_proxy_max_abs_bias'],sumrows)
    if len(sumrows)!=54:raise ArithmeticError('summary incomplete')
    report={
      'schema':'bass.ce1as.energy_matched_independent_flrw_radiation.v1',
      'date_kst':'2026-11-01','parent_PR':PARENT_PR,'parent_HEAD':PARENT_HEAD,
      'source_sixcell_sha256':ORIGINAL_SIX_CELL_SHA,
      'original_ce1ap_csv_sha256':sha(ancestor),'parent_ce1ar_beams_sha256':sha(beams),
      'input_identity_mode':'BYTE_LOCKED_S2' if strict else 'REPLAYED_SAME_OWNER_SEMANTIC_CI',
      'model':'FLAT_FLRW_ISOTROPIC_MASSLESS_COLLISIONLESS_VLASOV_RADIATION',
      'source_identity':'MATCHED_INITIAL_ENERGY_MONOPOLE_ONLY_NOT_FULL_SIXCELL_ANGULAR_SOURCE',
      'model_closure':'P=rho/3; Einstein 3H^2=rho; rho_prime=-4Hrho; a_prime=Ha',
      'signature':'(-,+,+,+)','normalization':'8piG=1, dimensionless u=t/Tstar',
      'distance_unit':'c*Tstar','observer_u':UO,'initial_h_bianchi_GL24':source_h.tolist(),
      'initial_Hbar_Bianchi':mean_h,'initial_shear_constraint':shear_source,
      'initial_rho_Bianchi':rho0,'flrw_initial_H':h0,'flrw_observer_H':ivp['H_observer'],
      'initial_constraint_source_gap':source_gap,'initial_6cell_model_checks':len(initial),
      'new_physically_distinct_FLRW_Einstein_Vlasov_IVPs':1,
      'new_original_sixcell_Bianchi_IVPs':0,'reused_original_Bianchi_IVPs':9,
      'flrw_history_rows':len(ivp['history']), 'flrw_spectral_shell_rows':6,
      'reused_bianchi_original_fixed_z_rows':5562,
      'new_Bianchi_vs_FLRW_comparison_rows':len(output),
      'new_sky_summary_rows':len(sumrows),
      'flrw_ivp_max_scale_relative':ivp['max_scale_relative'],
      'flrw_ivp_max_rhoa4_relative':ivp['max_rhoa4_relative'],
      'flrw_ivp_max_friedmann_abs':ivp['max_friedmann_absolute'],
      'flrw_max_DA_analytical_vs_IVP_ray_abs':max(s['ray_abs_gap'] for s in shells.values()),
      'flrw_max_redshift_abs':max(s['redshift_abs_gap'] for s in shells.values()),
      'source_cell_fully_preserved':True,'reference_fully_same_phase_space_source':False,
      'physically_measured_cosmological_data':False,
      'BASS_upper_scoped_source_mapped':'9/15','new_completed_upper_physics_nodes':0,
      'CE1':'PARTIAL','OB1':'PARTIAL','merge_ready':False,'production_ready':False,'auto_next':False,
      'axis_GL24_epsilon0':axes_for_graph
    }
    (out/'CE1AS_RESULTS.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print('CE1AS_REAL_FLRW_IVP','rho0',rho0,'H0',h0,'Hobs',ivp['H_observer'],
          'original_Bianchi_Hbar0',mean_h,'initial_sigma_constraint',shear_source,
          'FLRW_ray_gap',report['flrw_max_DA_analytical_vs_IVP_ray_abs'],flush=True)
    print('CE1AS_NEW_OBSERVABLES','flrw_history',report['flrw_history_rows'],
          'shells',report['flrw_spectral_shell_rows'],'Bianchi_FLRW_rows',len(output),
          'sky_summary',len(sumrows),flush=True)
    for z,ax in axes_for_graph:print('GL24_FIXED_Z',z,'FLRW_DA',shells[z]['D_A'],
                'axis_frac_delta',ax,flush=True)
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--ancestor',type=Path,default=INPUT)
    p.add_argument('--beams',type=Path,default=BEAMS);p.add_argument('--out',type=Path,default=OUTPUT)
    p.add_argument('--ci-replayed-source',action='store_true')
    p.add_argument('--ce1ap-metadata',type=Path)
    p.add_argument('--ce1ar-metadata',type=Path)
    args=p.parse_args()
    run(args.ancestor,args.beams,args.out,strict=not args.ci_replayed_source,
        ce1ap_metadata=args.ce1ap_metadata,ce1ar_metadata=args.ce1ar_metadata)
