#!/usr/bin/env python3
"""Source-bound spectral rates and a passive fixed-xe thermal response.
No HYREC population/effective-rate replacement. The photoionization histories
are single-target ground-state diagnostics. Thermal comparison uses identical
parent xe, geometry and initial Tm; no new optical depth or xe result is claimed.
"""
import ast,csv,hashlib,json,math,subprocess
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator
from collisions import *
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PARENT='7ad4e4b1cf841e0a974715bcece739ec06b38014'
CLOCK=ROOT/'research/typeii_clock_interface_20261115'
HX=ROOT/'research/typeii_native_hyrec_expansion_20261102'

def check(ok,msg):
 if not bool(ok):raise RuntimeError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def source():
 paths=[ROOT/'compiler/validation/generate_typeii_fixture.py',ROOT/'compiler/validation/typeii_fixture_canonical.json',CLOCK/'outputs/FULL_r2_both.dat',HX/'R3_TYPEII_HUBBLE_GRID.json']
 identity={}
 for p in paths:
  rel=str(p.relative_to(ROOT))
  expected=subprocess.check_output(['git','rev-parse',PARENT+':'+rel],cwd=ROOT,text=True).strip()
  got=subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
  check(got==expected,'immutable parent file changed: '+rel);identity[rel]=got
 fn=[n for n in ast.parse(paths[0].read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='typeii_rhs']
 check(len(fn)==1,'source rhs ownership');ns={'math':math}
 exec(compile(ast.Module(body=fn,type_ignores=[]),str(paths[0]),'exec'),ns);rhs=ns['typeii_rhs']
 fixture=json.loads(paths[1].read_text())['trajectory']['samples'];initial=np.array(fixture[0]['state'])
 Hend=json.loads(paths[3].read_text())['H_anchor_source_FLRW_s_inverse']
 tmax=math.log(1701/301)
 def eq(t,y):
  der=np.asarray(rhs(list(y[:5]),1.3),float);q=der[3]/y[3]+4*y[0]
  return np.r_[der,-1-q]
 sol=solve_ivp(eq,(0.,tmax),np.r_[initial,np.log(Hend)],method='DOP853',rtol=2e-12,atol=1e-13,max_step=.004,dense_output=True)
 check(sol.success,'TypeII source integration')
 parent=np.loadtxt(paths[2]);check(parent.shape==(8000,3),'parent native history shape')
 xe=PchipInterpolator(np.log1p(parent[::-1,0]),parent[::-1,1],extrapolate=False)
 tm=PchipInterpolator(np.log1p(parent[::-1,0]),parent[::-1,2],extrapolate=False)
 def fields(t):
  tt=np.asarray(t,float)
  check(np.isfinite(tt).all() and np.min(tt)>=0 and np.max(tt)<=tmax,'source time domain')
  y=sol.sol(tt);v=y[4];g=1/np.sqrt(1-v*v)
  if tt.ndim==0:vp=rhs(list(y[:5]),1.3)[4]
  else:vp=np.array([rhs(list(s),1.3)[4] for s in y[:5].T])
  L=v*vp/(1-v*v);z=1701*np.exp(-tt)-1
  return z,2.7255*(1+z),v,g,L,np.exp(y[5]),xe(np.log1p(z)),tm(np.log1p(z))
 return fields,tmax,identity

def main():
 fields,tmax,ident=source()
 zprobe=np.array([1700.,1500.,1392.,1242.,1100.,1000.,800.,500.,300.])
 tprobe=np.log(1701/(1+zprobe));tprobe[-1]=tmax
 times=np.unique(np.r_[np.linspace(0,tmax,351),tprobe]);z,T,b,G,L,hh,xe,tparent=fields(times)
 cm=[compton_moments(float(v)) for v in b]
 U=np.array([r['energy_ratio'] for r in cm]);tc=np.array([r['Tc_over_Tn'] for r in cm]);ts=np.array([r['Tc_spontaneous_over_Tn'] for r in cm]);tw=np.array([r['Tc_wrong_monopole_over_Tn'] for r in cm])
 photo=[];probes=[]
 for k in range(len(times)):
  one={'tau_H':float(times[k]),'z_mean':float(z[k]),'Tn_K':float(T[k]),'beta':float(b[k]),'Gamma':float(G[k]),'A':float(2+2*L[k]/3),'energy_ratio':float(U[k]),'Tc_over_Tn':float(tc[k]),'Tc_K':float(tc[k]*T[k]),'energy_matched_T_K':float(U[k]**.25*T[k]),'no_induced_Tc_K':float(ts[k]*T[k]),'wrong_monopole_Tc_K':float(tw[k]*T[k]),'parent_xe':float(xe[k]),'parent_Tm_K':float(tparent[k])}
  for species in SPECIES:
   full=photo_rate(float(T[k]),float(b[k]),species)
   base=photo_rate(float(T[k]),0.,species)
   energy=photo_rate(float(T[k]*U[k]**.25),0.,species)
   row={'species':species,'z_mean':float(z[k]),'beta':float(b[k]),'log_rate_s':full['log_rate_s'],'rate_s':full['rate_s'],'mean_excess_eV':full['mean_excess_eV'],'log_heat_W_per_target':full['log_photoheat_W'],'boost_over_normal_rate':float(np.exp(full['log_rate_s']-base['log_rate_s'])),'boost_over_energy_scalar_rate':float(np.exp(full['log_rate_s']-energy['log_rate_s']))}
   photo.append(row)
   if np.min(abs(times[k]-tprobe))<1e-12:one[species]=row
  if np.min(abs(times[k]-tprobe))<1e-12:probes.append(one)
 spectral=np.column_stack((times,z,T,b,G,L,U,tc,T*U**.25,T*ts,T*tw))
 np.savetxt(HERE/'SPECTRAL_COMPTON_FIELDS.csv',spectral,delimiter=',',header='tau_H,z_mean,Tn_K,beta,Gamma,L,energy_ratio,Tc_over_Tn,energy_scalar_T_K,spontaneous_only_Tc_K,wrong_monopole_Tc_K',comments='',fmt='%.17g')
 with (HERE/'GROUND_PHOTOIONIZATION.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(photo[0]),lineterminator='\n');w.writeheader();w.writerows(photo)
 # Passive thermal comparison. Same source xe, H, fluid expansion, initial Tm.
 # Deliberately retain the parent's fixed-composition temperature convention.
 fHe=.245/(1-.245)/3.97153
 if not np.isfinite(fHe):raise RuntimeError('bad helium convention')
 Ufn=PchipInterpolator(times,U);Tcfn=PchipInterpolator(times,tc);Tsfn=PchipInterpolator(times,ts);Twfn=PchipInterpolator(times,tw)
 lanes=('scalar','energy_matched','spectral','no_induced','monopole_induced')
 initial=float(fields(0.)[-1])
 def equations(t,y,lane):
  zz,tn,v,g,ll,h,xx,_=fields(float(t))
  # Parent source coefficient in s^-1/K^4; normalize all lanes identically.
  K0=4.91466895548409e-22*tn**4*xx/(1+xx+fHe)
  boost=float(Ufn(t));gain=1. if lane=='scalar' else boost
  drive=tn if lane=='scalar' else tn*(boost**.25 if lane=='energy_matched' else float(Tcfn(t) if lane=='spectral' else Tsfn(t) if lane=='no_induced' else Twfn(t)))
  return [-(2+2*ll/3)*y[0]+K0*gain/(g*h)*(drive-y[0])]
 results={};checks={}
 for lane in lanes:
  a=solve_ivp(lambda t,y:equations(t,y,lane),(0,tmax),[initial],method='Radau',t_eval=times,rtol=3e-10,atol=1e-7,max_step=.006)
  check(a.success and np.isfinite(a.y).all() and min(a.y[0])>0,'passive thermal integration '+lane)
  results[lane]=a.y[0]
 # Independent stiff solver, tighter tolerance for the physically admitted lanes.
 for lane in ('scalar','spectral','energy_matched'):
  alt=solve_ivp(lambda t,y:equations(t,y,lane),(0,tmax),[initial],method='BDF',t_eval=times,rtol=3e-11,atol=2e-8,max_step=.003)
  check(alt.success,'independent thermal BDF failure')
  gap=float(max(abs(alt.y[0]-results[lane])))
  check(gap<3e-4,'independent thermal comparison > declared .0003K target')
  checks[lane]=gap
 np.savetxt(HERE/'PASSIVE_FIXED_XE_TEMPERATURE.csv',np.column_stack([times,z,tparent]+[results[k] for k in lanes]),delimiter=',',header='tau_H,z_mean,parent_native_Tm_K,'+','.join('T_'+k+'_K' for k in lanes),comments='',fmt='%.17g')
 impacts={}
 for lane in lanes:
  delta=results[lane]-results['scalar'];i=int(np.argmax(abs(delta)))
  impacts[lane]={'Tm_at300_K':float(results[lane][-1]),'delta_at300_K':float(delta[-1]),'max_abs_delta_K':float(max(abs(delta))),'z_at_max':float(z[i])}
 # Frame and quadrature spot checks on the actual source probes, not invented beta.
 frames=[];quadrature=[]
 for t in tprobe:
  zz,tn,bb,*_=fields(float(t))
  for species in SPECIES:
   a=photo_rate(float(tn),float(bb),species,order=48);bref=photo_rate(float(tn),float(bb),species,order=96)
   n=photo_rate_normal(float(tn),float(bb),species,order=64)
   quadrature.append(float(abs(np.expm1(a['log_rate_s']-bref['log_rate_s']))))
   frames.append(float(abs(np.expm1(n['log_rate_s']-bref['log_rate_s']))))
 check(max(frames)<2e-7 and max(quadrature)<2e-7,'actual source photo frame/convergence failure')
 out={'parent_sha':PARENT,'input_Git_blobs':ident,'source_time_samples':len(times),'photo_rate_rows':len(photo),'source_z_domain':[300,1700],'source_probes':probes,
      'max_Tc_over_energy_scalar_difference_K':float(max(abs(T*tc-T*U**.25))),
      'max_relative_Tc_shift':float(max(tc-1)),
      'max_monopole_induced_temperature_error_K':float(max(abs(T*tw-T*tc))),
      'max_photo_frame_relative_gap':max(frames),'max_photo_order48_96_relative_gap':max(quadrature),
      'passive_thermal_initial_K':initial,'passive_thermal_lanes':impacts,'independent_Radau_BDF_max_gaps_K':checks,
      'passive_radiation_vs_energy_matched_endpoint_K':float(results['spectral'][-1]-results['energy_matched'][-1]),
      'parent_scalar_temperature_nonidentity_K':float(max(abs(results['scalar']-tparent))),
      'small_parameters':{'max_kBTn_over_mec2':float(max(KB*T/(ME*C*C))),'max_betav':float(max(abs(b)))},
      'claims':{'spectral_photoionization':'proper single-target ground-state rate with original Verner fit','Compton':'leading nonrelativistic unpolarized energy moment including induced angular coupling','thermal':'passive fixed-parent-xe ODE, same finite-z initial condition, fixed-composition convention','native_HYREC_population_feedback':False,'new_xe_or_optical_depth_prediction':False,'global_Bianchi_radiation_evolution':False,'momentum_backreaction':False}}
 (HERE/'SPECTRAL_SOURCE_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
 print('SPECTRAL_PROBES',json.dumps(probes,indent=2),flush=True)
 print('PASSIVE_THERMAL',json.dumps(impacts),flush=True)
 print('INDEPENDENT_THERMAL',checks,flush=True)
 print('GAPS',out['max_photo_frame_relative_gap'],out['max_photo_order48_96_relative_gap'],flush=True)
if __name__=='__main__':main()
