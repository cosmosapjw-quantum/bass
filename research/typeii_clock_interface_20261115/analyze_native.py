#!/usr/bin/env python3
"""Matched-source atomic histories and common geometric Thomson observables."""
from pathlib import Path
import ast,math,json,csv,subprocess
import numpy as np
from scipy.integrate import solve_ivp,simpson
from scipy.interpolate import PchipInterpolator,CubicHermiteSpline
from numpy.polynomial.legendre import leggauss
from native_experiment import HERE,ROOT,PAR,owner,check,sha

def main():
 records=json.loads((HERE/'NATIVE_RUNS.json').read_text())['runs'];check(len(records)==12 and all(r['exit']==0 for r in records),'native campaign incomplete')
 data={}
 for r in records:
  f=HERE/r['path'];check(sha(f)==r['sha256'],'native data hash changed');data[(r['refinement'],r['lane'])]=np.loadtxt(f)
 z=data[2,'legacy'][:,0];mask=(z>=300)&(z<=1700);rows=[];comparison={}
 for ref in (1,2):
  old=data[ref,'legacy']
  for lane in ('reaction','thermal','both','zero','global'):
   a=data[ref,lane];dx=a[:,1]-old[:,1];dt=a[:,2]-old[:,2];i=np.where(mask)[0][np.argmax(abs(dx[mask]))]
   comparison[f'r{ref}_{lane}']={'max_abs_xe_delta':float(max(abs(dx[mask]))),'z_of_max_xe_delta':float(z[i]),'max_relative_xe_delta':float(max(abs(dx[mask]/old[mask,1]))),'max_abs_Tm_delta_K':float(max(abs(dt[mask]))),'xe_at1100':float(a[6900,1]),'Tm_at300_K':float(a[7700,2]),'Tm_delta_at300_K':float(dt[7700])}
 for zz in (1700,1500,1392,1200,1100,1000,800,300):
  k=8000-zz;rows.append({'z':zz,**{f'xe_{lane}':float(data[2,lane][k,1]) for lane in ('legacy','reaction','thermal','both','global')}})
 same_input_delta1=data[1,'both'][:,1]-data[1,'legacy'][:,1];same_input_delta2=data[2,'both'][:,1]-data[2,'legacy'][:,1]
 convergence={'max_abs_both_base_vs_half_xe':float(max(abs(data[1,'both'][mask,1]-data[2,'both'][mask,1]))),'max_abs_clock_effect_change_base_to_half':float(max(abs(same_input_delta1[mask]-same_input_delta2[mask]))),'clock_effect_change_at1100':float(abs(same_input_delta1[6900]-same_input_delta2[6900]))}
 # Actual common parent geometry. Wrong global-H atom intervention does not
 # change the photon H or baryon current in this observable comparison.
 rf=owner.P0/'EXTENDED_TYPEII_HYREC2_RAY_26.csv';rel=str(rf.relative_to(ROOT));expected=subprocess.check_output(['git','rev-parse','27a3c7cfb57e145ed35526d4613de2e9d613d4ea:'+rel],cwd=ROOT,text=True).strip()
 check(subprocess.check_output(['git','hash-object',str(rf)],text=True).strip()==expected,'parent ray identity')
 ray=np.genfromtxt(rf,delimiter=',',names=True).reshape(26,1167);t=ray['tau_H'][0];zn=ray['z_mean_not_observed'][0]
 src=ROOT/'compiler/validation/generate_typeii_fixture.py';fn=[a for a in ast.parse(src.read_text()).body if isinstance(a,ast.FunctionDef) and a.name=='typeii_rhs'];ns={'math':math};exec(compile(ast.Module(body=fn,type_ignores=[]),str(src),'exec'),ns);rhs=ns['typeii_rhs']
 fixture=json.loads((ROOT/'compiler/validation/typeii_fixture_canonical.json').read_text())['trajectory']['samples'];x0=np.asarray(fixture[0]['state'])
 bg=solve_ivp(lambda t,x:rhs(list(x),1.3),(0,float(t[-1])),x0,method='DOP853',rtol=2e-12,atol=1e-13,max_step=.004,dense_output=True);check(bg.success,'geometry integration')
 X=bg.sol(t).T;sp,sm,s13,N1,v=X.T;nx,ny,nz=ray['n_x'],ray['n_y'],ray['n_z']
 snn=-2*sp*nx*nx+(sp+np.sqrt(3)*sm)*ny*ny+(sp-np.sqrt(3)*sm)*nz*nz+2*np.sqrt(3)*s13*nx*nz
 Y=CubicHermiteSpline(t,ny,(snn-sp-np.sqrt(3)*sm)*ny-N1*nx*nz,axis=1)
 H0=json.loads((owner.P1/'R3_TYPEII_HUBBLE_GRID.json').read_text())['H_anchor_source_FLRW_s_inverse'];hh=ray['H_s_inv'][0];HL=PchipInterpolator(t,np.log(hh*H0/hh[0]))
 N0=11.223846333047e-6*.0224*(1-.245)*1701**3/np.sqrt(1-x0[4]**2);sc=6.6524587e-25*29979245800.
 ip=int(np.argmin(np.max(abs(np.column_stack((nx[:,0],ny[:,0],nz[:,0]))-[0,1,0]),axis=1)));im=int(np.argmin(np.max(abs(np.column_stack((nx[:,0],ny[:,0],nz[:,0]))-[0,-1,0]),axis=1)))
 geometry=[]
 for order in (8,16):
  q,w=leggauss(order);width=np.diff(t);tt=(t[:-1,None]+width[:,None]*(q+1)/2).ravel();weights=(width[:,None]*w/2).ravel();vv=bg.sol(tt)[4];W=sc*N0*np.exp(-3*tt)/np.exp(HL(tt));Q=1-vv[None,:]*Y(tt);geometry.append((tt,weights,W,Q))
 depths={};qgap={}
 for (ref,lane),a in data.items():
  xe=PchipInterpolator(np.log1p(a[::-1,0]),a[::-1,1],extrapolate=False);vals=[]
  for tt,weights,W,Q in geometry:vals.append(np.sum(Q*(weights*W*xe(np.log1p(1701*np.exp(-tt)-1)))[None,:],axis=1))
  val=vals[1];key=f'r{ref}_{lane}';qgap[key]=float(max(abs(vals[1]-vals[0])));depths[key]={'plus':float(val[ip]),'minus':float(val[im]),'asymmetry':float((val[im]-val[ip])/(val[im]+val[ip])),'rays':val.tolist()}
 check(max(qgap.values())<5e-8,'photon quadrature refinement')
 parent=json.loads((PAR/'MODE_COMPARISON_RESULTS.json').read_text())['optical_depths']['FULL_r2_TypeII']
 parity=max(abs(depths['r2_legacy']['plus']-parent['plus']),abs(depths['r2_legacy']['minus']-parent['minus']));check(parity<2e-8,'opacity normalization changed')
 # Independent Simpson check on the original source-node rates.
 a=data[2,'both'];xe=PchipInterpolator(np.log1p(a[::-1,0]),a[::-1,1]);q=1-v[None,:]*ny;wn=sc*N0*np.exp(-3*t)/np.exp(HL(t));rate=q*(wn*xe(np.log1p(zn)))[None,:]
 independent=simpson(rate,x=t,axis=1);simpson_gap=float(max(abs(independent-np.array(depths['r2_both']['rays']))));check(simpson_gap<3e-7,'independent photon integration')
 gap_global=float(max(abs(data[2,'both'][mask,1]-data[2,'global'][mask,1])));check(gap_global>1e-7,'distinct clocks not distinguishable from global H test')
 result={'parent_sha':'27a3c7cfb57e145ed35526d4613de2e9d613d4ea','native_histories_successful':12,'native_zero_clock_identity':'BYTE_EXACT_BOTH_REFINEMENTS','comparison_to_legacy':comparison,'probes':rows,'convergence':convergence,'native_both_vs_naive_globalH_max_abs_xe':gap_global,'common_geometry_optical_depths':depths,'max_Gauss8_16_gap':max(qgap.values()),'independent_Simpson_gap':simpson_gap,'parent_opacity_gap':parity,'scope':'actual conditional native FULL clock/thermal interventions; exact boosted radiation interface remains separately implemented, not coupled into atomic rate tables'}
 (HERE/'NATIVE_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
 with (HERE/'ATOMIC_PROBES.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
 with (HERE/'THOMSON_ENDPOINTS.csv').open('w',newline='') as f:
  w=csv.writer(f,lineterminator='\n');w.writerow(['model','ray_id','optical_depth'])
  for k,x in depths.items():
   for j,value in enumerate(x['rays']):w.writerow([k,j,format(value,'.17g')])
 print('COMPARISON',json.dumps({k:x for k,x in comparison.items() if k.startswith('r2')}))
 print('CONVERGENCE',convergence,'GLOBAL_VS_BOTH',gap_global)
 print('PHOTONS',json.dumps({k:{kk:vv for kk,vv in x.items() if kk!='rays'} for k,x in depths.items() if k.startswith('r2')}))
 print('GAPS',max(qgap.values()),simpson_gap,parity)
if __name__=='__main__':main()
