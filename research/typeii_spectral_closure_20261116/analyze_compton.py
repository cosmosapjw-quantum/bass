#!/usr/bin/env python3
"""Compare actual FULL Compton interventions at fixed parent source geometry."""
from pathlib import Path
import json,csv,ast,math,subprocess
import numpy as np
from scipy.integrate import solve_ivp,simpson
from scipy.interpolate import PchipInterpolator,CubicHermiteSpline
from numpy.polynomial.legendre import leggauss
from native_compton import HERE,ROOT,PAR,OUT,owner,check,sha
PARENT_SHA='7ad4e4b1cf841e0a974715bcece739ec06b38014'
def main():
 r=json.loads((HERE/'NATIVE_RUNS.json').read_text());check(len(r['runs'])==8 and all(x['exit']==0 for x in r['runs']),'native campaign incomplete')
 data={}
 for run in r['runs']:
  f=HERE/run['path'];check(sha(f)==run['sha256'],'native output changed');data[run['refinement'],run['lane']]=np.loadtxt(f)
 for ref in (1,2):check(sha(OUT/f'FULL_r{ref}_zero.dat')==sha(PAR/f'outputs/FULL_r{ref}_both.dat'),'parent zero parity')
 z=data[2,'zero'][:,0];w=(z>=300)&(z<=1700);comparisons={};probes=[]
 for ref in (1,2):
  base=data[ref,'zero']
  for lane in ('moments','energy_scalar','monopole'):
   a=data[ref,lane];dx=a[:,1]-base[:,1];dt=a[:,2]-base[:,2];j=np.where(w)[0][np.argmax(abs(dx[w]))];k=np.where(w)[0][np.argmax(abs(dt[w]))]
   comparisons[f'r{ref}_{lane}']={'max_abs_xe_delta':float(max(abs(dx[w]))),'z_max_abs_xe':float(z[j]),
    'max_relative_xe_delta':float(max(abs(dx[w]/base[w,1]))),'max_abs_Tm_delta_K':float(max(abs(dt[w]))),'z_max_Tm':float(z[k]),
    'xe1100':float(a[6900,1]),'Tm1100_K':float(a[6900,2]),'Tm300_K':float(a[7700,2])}
 for zz in (1700,1500,1392,1242,1100,1000,800,500,300):
  k=8000-zz;probes.append({'z_mean':zz,**{f'{q}_{lane}':float(data[2,lane][k,col]) for lane in ('zero','moments','energy_scalar','monopole') for q,col in [('xe',1),('Tm_K',2)]}})
 delta1=data[1,'moments'][:,1]-data[1,'zero'][:,1];delta2=data[2,'moments'][:,1]-data[2,'zero'][:,1]
 conv={'max_abs_moments_base_half_xe':float(max(abs(data[1,'moments'][w,1]-data[2,'moments'][w,1]))),
       'max_abs_intervention_effect_base_half_drift':float(max(abs(delta1[w]-delta2[w]))),
       'intervention_drift_z1100':float(abs(delta1[6900]-delta2[6900]))}
 contrasts={}
 for lane in ('energy_scalar','monopole'):
  dx=data[2,'moments'][:,1]-data[2,lane][:,1]
  contrasts[lane]={'max_abs_xe_gap':float(max(abs(dx[w]))),'max_relative_xe_gap':float(max(abs(dx[w]/data[2,'moments'][w,1]))),
                   'max_abs_Tm_gap_K':float(max(abs(data[2,'moments'][w,2]-data[2,lane][w,2])))}
 # Parent photon characteristics remain immutable, with original source time convention.
 rf=owner.P0/'EXTENDED_TYPEII_HYREC2_RAY_26.csv';rel=str(rf.relative_to(ROOT))
 expected=subprocess.check_output(['git','rev-parse',PARENT_SHA+':'+rel],cwd=ROOT,text=True).strip()
 check(subprocess.check_output(['git','hash-object',str(rf)],text=True).strip()==expected,'source photon blob changed')
 ray=np.genfromtxt(rf,delimiter=',',names=True).reshape(26,1167);t=ray['tau_H'][0];zn=ray['z_mean_not_observed'][0]
 src=ROOT/'compiler/validation/generate_typeii_fixture.py';fn=[n for n in ast.parse(src.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='typeii_rhs'];check(len(fn)==1,'source rhs ambiguous')
 env={'math':math};exec(compile(ast.Module(body=fn,type_ignores=[]),str(src),'exec'),env);rhs=env['typeii_rhs']
 fx=json.loads((ROOT/'compiler/validation/typeii_fixture_canonical.json').read_text())['trajectory']['samples'];x0=np.array(fx[0]['state'])
 bg=solve_ivp(lambda u,x:rhs(list(x),1.3),(0.,float(t[-1])),x0,method='DOP853',rtol=2e-12,atol=1e-13,max_step=.004,dense_output=True);check(bg.success,'source background failed')
 sp,sm,s13,N1,v=bg.sol(t);nx,ny,nz=ray['n_x'],ray['n_y'],ray['n_z']
 snn=-2*sp*nx*nx+(sp+np.sqrt(3)*sm)*ny*ny+(sp-np.sqrt(3)*sm)*nz*nz+2*np.sqrt(3)*s13*nx*nz
 NY=CubicHermiteSpline(t,ny,(snn-sp-np.sqrt(3)*sm)*ny-N1*nx*nz,axis=1)
 H0=json.loads((owner.P1/'R3_TYPEII_HUBBLE_GRID.json').read_text())['H_anchor_source_FLRW_s_inverse'];hh=ray['H_s_inv'][0];HL=PchipInterpolator(t,np.log(hh*H0/hh[0]))
 N0=11.223846333047e-6*.0224*(1-.245)*1701**3/np.sqrt(1-x0[4]**2);sc=6.6524587e-25*29979245800.
 ip=int(np.argmin(np.max(abs(np.column_stack((nx[:,0],ny[:,0],nz[:,0]))-[0,1,0]),axis=1)));im=int(np.argmin(np.max(abs(np.column_stack((nx[:,0],ny[:,0],nz[:,0]))-[0,-1,0]),axis=1)))
 geometry=[]
 for order in (8,16):
  a,wg=leggauss(order);dt=np.diff(t);qt=(t[:-1,None]+dt[:,None]*(a+1)/2).ravel();qw=(dt[:,None]*wg/2).ravel();vv=bg.sol(qt)[4]
  W=sc*N0*np.exp(-3*qt)/np.exp(HL(qt));Q=1-vv[None,:]*NY(qt);geometry.append((qt,qw,W,Q))
 depths={};gaps={}
 for (ref,lane),a in data.items():
  xe=PchipInterpolator(np.log1p(a[::-1,0]),a[::-1,1]);values=[]
  for qt,qw,W,Q in geometry:values.append(np.sum(Q*(qw*W*xe(np.log1p(1701*np.exp(-qt)-1)))[None,:],axis=1))
  d=values[1];key=f'r{ref}_{lane}';gaps[key]=float(max(abs(values[1]-values[0])));depths[key]={'plus':float(d[ip]),'minus':float(d[im]),'asymmetry':float((d[im]-d[ip])/(d[im]+d[ip])),'rays':d.tolist()}
 check(max(gaps.values())<5e-8,'photon quadrature not converged')
 parent_depth=json.loads((PAR/'NATIVE_RESULTS.json').read_text())['common_geometry_optical_depths']['r2_both']
 parity=max(abs(depths['r2_zero'][k]-parent_depth[k]) for k in ('plus','minus'));check(parity<2e-8,'source opacity normalization drift')
 a=data[2,'moments'];xe=PchipInterpolator(np.log1p(a[::-1,0]),a[::-1,1]);W=sc*N0*np.exp(-3*t)/np.exp(HL(t));Q=1-v[None,:]*ny
 sg=float(max(abs(simpson(Q*(W*xe(np.log1p(zn)))[None,:],x=t,axis=1)-np.array(depths['r2_moments']['rays']))));check(sg<3e-7,'independent Simpson mismatch')
 result={'parent_sha':PARENT_SHA,'native_histories':8,'identity_adapter':'BYTE_EXACT_TO_PR334_BOTH_AT_BOTH_STEPS',
         'comparisons_to_zero_spectral_adapter':comparisons,'direct_approximation_contrasts':contrasts,'convergence':conv,'probes':probes,
         'common_geometry_optical_depths':depths,'max_Gauss8_16_gap':max(gaps.values()),'independent_Simpson_gap':sg,'parent_opacity_gap':parity,
         'scope':'Compton heat energy moment only; native effective photoionization and photon line-transfer bath unchanged; no ground-state rates substituted',
         'phase_switch':'fixed native lag to refer to Compton target; DLNT_MAX unchanged; initial mismatch failure retained'}
 (HERE/'NATIVE_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
 with (HERE/'ATOMIC_PROBES.csv').open('w',newline='') as f:
  wr=csv.DictWriter(f,fieldnames=list(probes[0]),lineterminator='\n');wr.writeheader();wr.writerows(probes)
 with (HERE/'THOMSON_ENDPOINTS.csv').open('w',newline='') as f:
  wr=csv.writer(f,lineterminator='\n');wr.writerow(['lane','ray','tau_to_mean_z300'])
  for name,r in depths.items():
   for j,val in enumerate(r['rays']):wr.writerow([name,j,format(val,'.17g')])
 print('HALFSTEP_COMPARISONS',json.dumps({k:v for k,v in comparisons.items() if k.startswith('r2')}),flush=True)
 print('CONTRASTS',json.dumps(contrasts),'CONVERGENCE',json.dumps(conv),flush=True)
 print('PHOTONS',json.dumps({k:{s:x for s,x in r.items() if s!='rays'} for k,r in depths.items() if k.startswith('r2')}),flush=True)
 print('GAPS',max(gaps.values()),sg,parity,flush=True)
if __name__=='__main__':main()
