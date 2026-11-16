#!/usr/bin/env python3
"""Original TypeII source-state level rates and a closed finite reaction test.
No native HYREC effective-rate substitution and no new cosmological xe history.
"""
import csv,json,subprocess
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.integrate import solve_ivp
from boundfree import *
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
PARENT='ad4bda34a833d215aa49037d7cb4d609e5cee04b'
SELECTED=[(1,0),(2,0),(2,1),(3,0),(3,1),(3,2)]

def source_fields():
    fp=REPO/'research/typeii_spectral_collisions_20261116/SPECTRAL_COMPTON_FIELDS.csv'
    hp=REPO/'research/typeii_clock_interface_20261115/outputs/FULL_r2_both.dat'
    ident={}
    for f in (fp,hp):
        rel=str(f.relative_to(REPO))
        expect=subprocess.check_output(['git','rev-parse',PARENT+':'+rel],cwd=REPO,text=True).strip()
        got=subprocess.check_output(['git','hash-object',str(f)],text=True).strip()
        check(got==expect,'immutable parent changed: '+rel);ident[rel]=got
    fields=np.genfromtxt(fp,delimiter=',',names=True)
    hist=np.loadtxt(hp);check(hist.shape==(8000,3),'parent native history shape')
    Tm=PchipInterpolator(np.log1p(hist[::-1,0]),hist[::-1,2],extrapolate=False)(np.log1p(fields['z_mean']))
    xe=PchipInterpolator(np.log1p(hist[::-1,0]),hist[::-1,1],extrapolate=False)(np.log1p(fields['z_mean']))
    check(len(fields)==358 and np.isfinite(Tm).all(),'source field contract')
    return fields,Tm,xe,ident

def close_network(Tn,Tm,beta,nH,label):
    """Isolated 2s/2p + ion/e closed chemistry in a fixed prescribed bath.
    Not a cosmological population truncation claimed to approximate HYREC.
    Dimensionless time u=t_proper*max(photo rates); an analytic positive
    stationary solution and dissipation identity are independent checks.
    """
    rr=[rates(Tn,Tm,beta,k,order=6) for k in [(2,0),(2,1)]]
    B=np.array([r['photo_s'] for r in rr]);AA=nH*np.array([r['alpha_m3_s'] for r in rr]);scale=float(max(B))
    b=B/scale;a=AA/scale
    total=float(np.sum(AA/B));xeq=2/(1+np.sqrt(1+4*total));yeq=AA/B*xeq**2
    def fun(t,y):
        x=1-float(np.sum(y));return a*x*x-b*y
    def jac(t,y):
        x=1-float(np.sum(y));return -2*x*a[:,None]*np.ones((1,2))-np.diag(b)
    initial=np.array([.25,.15]);end=80/float(min(b));u=np.unique(np.r_[0.,np.geomspace(1e-6,end,360)])
    solutions={}
    for method in ('Radau','BDF'):
        sol=solve_ivp(fun,(0.,end),initial,t_eval=u,method=method,jac=jac,rtol=2e-10,atol=1e-24,max_step=.35)
        check(sol.success,'isolated network solve '+label+method)
        y=sol.y.T;x=1-y.sum(axis=1)
        check(min(x)>0 and min(y.flat)>0 and max(x)<=1,'population positivity')
        last=float(max(abs(y[-1]/yeq-1)))
        check(last<3e-6,'stationary population not reached')
        solutions[method]=(y,x,last)
    y,x,last=solutions['Radau'];alt,xalt,_=solutions['BDF']
    gap=float(np.max(abs(y-alt)));check(gap<2e-8,'independent network solver disagreement')
    # Relative-entropy Lyapunov of this reversible fixed-rate mass-action
    # network; NOT a thermodynamic free energy of the anisotropic bath.
    F=2*(x*np.log(x/xeq)-x+xeq)+np.sum(y*np.log(y/yeq)-y+yeq,axis=1)
    forward=y*b[None,:];reverse=x[:,None]**2*a[None,:]
    diss=-np.sum((forward-reverse)*np.log(forward/reverse),axis=1)
    check(np.max(diss)<1e-12,'reversible mass-action dissipation sign')
    check(np.max(np.diff(F))<1e-10,'relative entropy not decreasing')
    dyi=np.array([fun(float(tt),yy) for tt,yy in zip(u,y)])
    dx=-dyi.sum(axis=1)
    chain=np.sum(np.log(y/yeq)*dyi,axis=1)+2*np.log(x/xeq)*dx
    dgap=float(np.max(abs(chain-diss)));check(dgap<1e-11,'Lyapunov chain-rule identity')
    ratio=float(yeq[1]/yeq[0])
    out={'label':label,'Tn_K':Tn,'Tm_K':Tm,'beta':beta,'fixed_nH_m3':nH,
         'proper_time_unit_s':1/scale,'initial_bound_fractions':initial.tolist(),
         'equilibrium_bound_fractions':yeq.tolist(),'equilibrium_continuum_fraction':xeq,
         'stationary_2p_over_2s':ratio,'final_relative_stationary_error':last,
         'Radau_BDF_max_abs_fraction_gap':gap,'max_positive_entropy_increment':float(max(0.,max(np.diff(F)))),
         'max_entropy_chainrule_gap':dgap,'nucleus_residual':float(max(abs(x+y.sum(axis=1)-1))),
         'interpretation':'isolated 2s/2p continuum mass-action validation; no cosmological xe prediction'}
    return out,np.column_stack((u,u/scale,y,x,F,diss))

def main():
    fields,Tm,xe,ident=source_fields();records=[];selected_probes=[];interpolation=[];quadrature_errors=[]
    ix={z:int(np.argmin(abs(fields['z_mean']-z))) for z in (1700.,1500.,1392.,1100.,1000.,800.,300.)}
    for i,f in enumerate(fields):
        tn=float(f['Tn_K']);tm=float(Tm[i]);beta=float(f['beta'])
        for key in SELECTED:
            r=rates(tn,tm,beta,key);base=rates(tn,tm,0.,key)
            energy=rates(float(f['energy_scalar_T_K']),tm,0.,key)
            row={'tau_H':float(f['tau_H']),'z_mean':float(f['z_mean']),'n':key[0],'l':key[1],
                 'Tn_K':tn,'Tm_parent_K':tm,'beta':beta,
                 'photo_rate_s':r['photo_s'],'log_photo_rate_s':r['log_photo'],
                 'capture_alpha_m3_s':r['alpha_m3_s'],'log_capture_alpha':r['log_alpha'],
                 'stimulated_capture_fraction':r['stimulated_fraction'],
                 'stationary_over_Tm_Saha':float(np.exp(r['log_departure_from_Tm_Saha'])),
                 'log_stationary_ratio_m3':r['log_stationary_ratio_m3'],
                 'photo_boost_over_normal':float(np.exp(r['log_photo']-base['log_photo'])),
                 'capture_boost_over_normal':float(np.exp(r['log_alpha']-base['log_alpha'])),
                 'photo_boost_over_energy_scalar':float(np.exp(r['log_photo']-energy['log_photo'])),
                 'capture_boost_over_energy_scalar':float(np.exp(r['log_alpha']-energy['log_alpha'])),
                 'mean_photo_excess_eV':r['photo_excess_J']/EV,
                 'mean_captured_kinetic_eV':r['capture_kinetic_J']/EV,
                 'Kmax_over_kT_hot':r['support_over_kT_hot']}
            records.append(row)
            if i in ix.values():
                r8=rates(tn,tm,beta,key,order=12);lin=rates(tn,tm,beta,key,method='linear')
                quadrature_errors.append(max(abs(np.expm1(r8['log_alpha']-r['log_alpha'])),abs(np.expm1(r8['log_photo']-r['log_photo']))))
                interpolation.append({'z':row['z_mean'],'level':list(key),
                  'alpha_linear_vs_pchip_relative':float(np.expm1(lin['log_alpha']-r['log_alpha'])),
                  'photo_linear_vs_pchip_relative':float(np.expm1(lin['log_photo']-r['log_photo']))})
                selected_probes.append(row)
    check(max(quadrature_errors)<3e-8,'actual source kernel quadrature')
    with (HERE/'LEVEL_BOUND_FREE_SOURCE.csv').open('w',newline='') as out:
        w=csv.DictWriter(out,fieldnames=list(records[0]),lineterminator='\n');w.writeheader();w.writerows(records)
    high=[]
    for z in (1700.,1100.,300.):
        i=ix[z];f=fields[i]
        for key in LEVELS:
            r=rates(float(f['Tn_K']),float(Tm[i]),float(f['beta']),key)
            high.append({'z_mean':z,'n':key[0],'l':key[1],'alpha_finite_m3_s':r['alpha_m3_s'],'photo_finite_s':r['photo_s'],
                'stimulated_fraction':r['stimulated_fraction'],'support_over_kT_hot':r['support_over_kT_hot'],
                'stationary_over_Tm_Saha':float(np.exp(r['log_departure_from_Tm_Saha']))})
    with (HERE/'ALL_LEVEL_FINITE_BAND_PROBES.csv').open('w',newline='') as out:
        w=csv.DictWriter(out,fieldnames=list(high[0]),lineterminator='\n');w.writeheader();w.writerows(high)
    # Use source density at z1100 for the isolated kinetic test, not an invented
    # cosmological ionization history. The test itself omits 1s/bound-bound levels.
    i=ix[1100.];f=fields[i];tn=float(f['Tn_K']);b=float(f['beta'])
    nh0=11.223846333047e-6*.0224*(1-.245)*1e6
    nh=nh0*(1+f['z_mean'])**3*float(fields['Gamma'][0])/float(f['Gamma'])
    network=[]
    for label,tt,bb in [('Planck_common_T',tn,0.),('boost_common_T',tn,b),('boost_parent_Tm',float(Tm[i]),b)]:
        result,data=close_network(tn,tt,bb,float(nh),label);network.append(result)
        np.savetxt(HERE/('NETWORK_'+label+'.csv'),data,delimiter=',',header='scaled_proper_time,proper_seconds,x_2s,x_2p,x_continuum,relative_entropy,entropy_derivative',comments='',fmt='%.17g')
    check(abs(network[0]['stationary_2p_over_2s']/3-1)<2e-11,'network Planck statistical weights')
    probes_by_z={str(z):[x for x in selected_probes if abs(x['z_mean']-z)<1e-8] for z in ix}
    result={'source_parent':PARENT,'input_Git_blobs':ident,'source_time_points':len(fields),'low_level_rate_rows':len(records),
            'all_level_finite_band_probe_rows':len(high),'levels_primary':[list(k) for k in SELECTED],
            'max_segment8_12_rate_relative_gap':float(max(quadrature_errors)),
            'max_loglinear_vs_logPCHIP_rate_relative_difference':float(max(max(abs(x['alpha_linear_vs_pchip_relative']),abs(x['photo_linear_vs_pchip_relative'])) for x in interpolation)),
            'minimum_primary_Kmax_over_kT_hot':float(min(x['Kmax_over_kT_hot'] for x in records)),
            'state_probes':probes_by_z,'interpolation_diagnostics':interpolation,
            'isolated_population_networks':network,
            'interpretation':'state-resolved source-dependent rates and isolated reversible population validation, finite energy support',
            'new_native_HYREC_population_run':False,'new_cosmological_xe_or_tau_history':False,
            'tail_statement':'no source data outside the tabulated support; endpoint/tail scale is diagnostic, not a rigorous missing-tail bound'}
    (HERE/'SOURCE_AND_NETWORK_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
    print('SOURCE_COUNTS',len(fields),len(records),len(high),flush=True)
    print('MAX_QUAD_GAP',result['max_segment8_12_rate_relative_gap'],flush=True)
    print('MAX_INTERPOLATION_DIFFERENCE',result['max_loglinear_vs_logPCHIP_rate_relative_difference'],flush=True)
    print('MIN_SUPPORT',result['minimum_primary_Kmax_over_kT_hot'],flush=True)
    for key in ('1700.0','1100.0','300.0'):
        print('PROBES',key,json.dumps(probes_by_z[key]),flush=True)
    print('NETWORKS',json.dumps(network),flush=True)
if __name__=='__main__':main()
