#!/usr/bin/env python3
"""Source-bound Verner cross sections and electron-frame collision diagnostics."""
from pathlib import Path
import json,ctypes,subprocess,hashlib,csv
import numpy as np
from scipy.interpolate import PchipInterpolator
import spectral as s
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PAR=ROOT/'research/typeii_clock_interface_20261115'
def check(c,msg):
 if not bool(c):raise RuntimeError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lab_photo(species,T,b,ne=96,nmu=80):
 """Independent normal-frame isotropic integral with atom proper-time flux D.
 E_e=D E_n, D=Gamma(1-beta mu_n); no electron-angle Jacobian is reused.
 """
 g=1/np.sqrt(1-b*b);mu,wm=s.gauss(nmu);t,w=s.laguerre(ne)
 D=g*(1-b*mu);dm=g*(1+abs(b));kt=s.KB*T/s.EV;chi=s.PARAMS[species]['threshold_eV']
 En=chi/D[None,:]+kt*t[:,None]
 Ee=D[None,:]*En
 scaled=np.exp(-chi/(kt*D)+chi/(kt*dm))[None,:]/(-np.expm1(-En/kt))
 values=En*En*D[None,:]*s.cross_section(species,Ee)*scaled
 val=float(w@(values@(wm/2)))
 return np.log(8*np.pi*s.EV**3/(s.HPLANCK**3*s.C**2)*kt)+np.log(val)-chi/(kt*dm)
def main():
 locks=json.loads((HERE/'SOURCES.json').read_text())
 for r in locks['photo_cross_sections']:check(sha(HERE/'sources'/r['file'])==r['sha256'],'Verner source drift')
 # Original author's single-precision Fortran as an independent implementation.
 lib=HERE/'native_run/libphfit2.so'
 p=subprocess.run(['gfortran','-shared','-fPIC','-O2','-std=legacy',str(HERE/'sources/phfit2.f'),'-o',str(lib)],capture_output=True,text=True,timeout=60)
 (HERE/'FORTRAN_BUILD.log').write_text(p.stdout+p.stderr);check(p.returncode==0,'original Verner Fortran failed')
 fn=ctypes.CDLL(str(lib)).phfit2_
 fn.argtypes=[ctypes.POINTER(ctypes.c_int)]*3+[ctypes.POINTER(ctypes.c_float)]*2
 fchecks=[]
 for name,r in s.PARAMS.items():
  for factor in (1.0001,1.1,2.,10.,100.,500.):
   e=ctypes.c_float(r['threshold_eV']*factor);out=ctypes.c_float(0)
   Z,N,sh=ctypes.c_int(r['Z']),ctypes.c_int(r['N']),ctypes.c_int(1)
   fn(ctypes.byref(Z),ctypes.byref(N),ctypes.byref(sh),ctypes.byref(e),ctypes.byref(out))
   py=float(s.cross_section(name,e.value));ref=out.value*1e-22
   rel=abs(py/ref-1);check(rel<8e-6,'Fortran-Python fit disagreement')
   fchecks.append({'species':name,'E_eV':e.value,'python_m2':py,'Fortran_m2':ref,'relative_gap':rel})
 # Parent source velocities and beta'=d beta/d tau_H: exact recorded source table.
 clk=np.loadtxt(PAR/'CLOCK_GRID.dat');source=json.loads((PAR/'SOURCE_FIELDS.json').read_text())
 check(sha(PAR/'CLOCK_GRID.dat')==source['clock_grid_sha256'],'parent clock source changed')
 check(clk.shape==(2248,2),'parent clock grid shape')
 z=np.arange(2248)*8000/2248;rows=[];rad=np.column_stack((np.ones(2248),np.ones(2248),np.zeros(2248),np.ones(2248),np.zeros(2248)))
 mu_gap=0.;photo_gap=0.;frame_gap=0.;examples=[]
 beta_curve=PchipInterpolator(z,clk[:,0]);beta_prime=PchipInterpolator(z,clk[:,1])
 for k in np.where(z<1700)[0]:
  b,bp=clk[k];r=s.compton(float(b));db=1e-5
  rp=s.compton(float(b+db));rm=s.compton(float(b-db))
  logder=(np.log(rp['Tc_ratio'])-np.log(rm['Tc_ratio']))/(2*db)*bp
  isoder=(np.log(rp['monopole_squared_Tc_ratio'])-np.log(rm['monopole_squared_Tc_ratio']))/(2*db)*bp
  rad[k]=[r['energy_ratio'],r['Tc_ratio'],logder,r['monopole_squared_Tc_ratio'],isoder]
  if z[k]<300:continue
  T=2.7255*(1+z[k]);te=T*r['energy_ratio']**.25
  for name in s.PARAMS:
   a=s.photo_rate(name,T,b);zero=s.photo_rate(name,T,0.);energy=s.photo_rate(name,te,0.)
   rows.append([z[k],b,T,name,a['rate_s'],a['log_rate_s'],a['heating_W'],a['mean_excess_eV'],
                np.exp(a['log_rate_s']-zero['log_rate_s']),np.exp(a['log_rate_s']-energy['log_rate_s'])])
 for zz in (1700.,1500.,1392.,1242.,1100.,1000.,800.,500.,300.):
  b=float(beta_curve(zz));T=2.7255*(1+zz);r=s.compton(b);fine=s.compton(b,96,256)
  mu_gap=max(mu_gap,abs(r['Tc_ratio']/fine['Tc_ratio']-1))
  sample={'z_mean':zz,'beta':b,'Tn_K':T,'energy_ratio':r['energy_ratio'],'TC_K':T*r['Tc_ratio'],
          'T_energy_K':T*r['energy_ratio']**.25,'TC_wrong_monopole_K':T*r['monopole_squared_Tc_ratio'],'species':{}}
  for name in s.PARAMS:
   a=s.photo_rate(name,T,b);f=s.photo_rate(name,T,b,128,96);base=s.photo_rate(name,T,0.)
   en=s.photo_rate(name,T*r['energy_ratio']**.25,0.)
   photo_gap=max(photo_gap,abs(np.expm1(a['log_rate_s']-f['log_rate_s'])))
   lab=lab_photo(name,T,b);frame_gap=max(frame_gap,abs(np.expm1(lab-a['log_rate_s'])))
   sample['species'][name]={'rate_per_atom_s':a['rate_s'],'log_rate_s':a['log_rate_s'],'heating_per_atom_W':a['heating_W'],
     'mean_excess_eV':a['mean_excess_eV'],'ratio_to_normal_blackbody':float(np.exp(a['log_rate_s']-base['log_rate_s'])),
     'ratio_to_energy_matched_blackbody':float(np.exp(a['log_rate_s']-en['log_rate_s']))}
  examples.append(sample)
 check(mu_gap<2e-11 and photo_gap<1e-8 and frame_gap<1e-8,'spectral convergence/frame invariance failure')
 cold=[]
 for b in (0.,.05,.2):
  for x in (.2,1.,6.):
   m=s.multipoles(np.array([x]),b,64)[0];lead=m[0]+s.induced(m)
   a=s.direct_pair(x,b,24,48,recoil_eta=1e-4);q=s.direct_pair(x,b,24,48,recoil_eta=1e-6)
   err=abs(q/lead-1);check(err<3e-5 and abs(q-lead)<abs(a-lead),'exact recoil limit mismatch')
   cold.append({'beta':b,'x':x,'leading':float(lead),'exact_KN_eta_1e6':q,'relative_gap':err})
 np.savetxt(HERE/'COMPTON_GRID.dat',rad,fmt='%.17e',header='U_ratio TC_ratio dlogTCratio_dtau TC_monopole_ratio dlogTCmonopole_dtau; fixed parent 2248 z-grid')
 with (HERE/'PHOTOIONIZATION_SOURCE_GRID.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['z_mean','beta','Tn_K','species','rate_s','log_rate_s','heating_W','mean_excess_eV','ratio_to_normal','ratio_to_energy_scalar']);w.writerows(rows)
 info={'parent_sha':'7ad4e4b1cf841e0a974715bcece739ec06b38014','source_beta_grid_sha256':sha(PAR/'CLOCK_GRID.dat'),
       'cross_sections':'Verner1996 ground-state fits, direct ionizing continuum, NOT HYREC effective n2 photoionization',
       'Fortran_comparisons':fchecks,'Fortran_max_relative_gap':max(x['relative_gap'] for x in fchecks),
       'compton_angular_energy_refinement_max_relative':mu_gap,'photo_quadrature_max_relative':photo_gap,
       'photo_independent_normal_frame_integral_max_relative':frame_gap,'cold_exact_KN_recoil_controls':cold,
       'TC_small_beta_coefficient':'2*pi^2/9-7/6','source_samples':examples,'photo_grid_records':len(rows),
       'compton_grid_sha256':sha(HERE/'COMPTON_GRID.dat'),'Compton_approximation':'leading E/mec2 and kT/mec2, exact bulk-boosted prescribed photon spectrum; stimulation retained',
       'underflow_policy':'rate_s may underflow for negligible far-Wien tails; log_rate_s and ratios remain separately evaluated',
       'native_atom_photoionization_coupled':False}
 (HERE/'SPECTRAL_RESULTS.json').write_text(json.dumps(info,indent=2)+'\n')
 (HERE/'SYMBOLIC_CHECKS.json').write_text(json.dumps({'actual_Wolfram_call':True,'kernel_Legendre_residual':0,'kernel_normalization':1,'Planck_energy_balance_residual':0,'Tc_smallbeta_coefficient':'-7/6+2 Pi^2/9','coefficient_value':1.0265787557976352,'scope':'algebraic checks, not distinct-author review'},indent=2)+'\n')
 print('SPECTRAL_CHECKS',json.dumps({k:info[k] for k in ('Fortran_max_relative_gap','compton_angular_energy_refinement_max_relative','photo_quadrature_max_relative','photo_independent_normal_frame_integral_max_relative','photo_grid_records')}),flush=True)
 for x in examples:print('SOURCE_SAMPLE',json.dumps(x),flush=True)
if __name__=='__main__':main()
