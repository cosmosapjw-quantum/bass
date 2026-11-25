"""Compare live source-born endpoint compression at fixed temporal and
source grids. Retain exact input support labels, not exact cohort weights."""
import argparse,hashlib,json,subprocess,math,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import cumulative_trapezoid
p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--donor',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--workers',type=int,default=3);a=p.parse_args()
root=a.out.resolve();root.mkdir(exist_ok=False);exe=a.binary.resolve()
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
d=json.loads(a.donor.read_text());q=d['initial'];bg=d['background'];fhe=bg['f_He']
assert q['z']==20 and q['x_HeII']==q['x_HeIII']==0
cases=[]
for shear in (0.,.01,-.01):
 for width in (None,.04,.01):
  cases.append((19.98,256,shear,8,8,width))
for n,w,sub in [(4096,.04,8),(8192,.04,8),(16384,.04,8),(8192,.02,8),(8192,.01,8),(8192,.02,16),(16384,.02,16),(16384,.01,16),(32768,.01,16)]:
 cases.append((4.,n,0.,sub,8,w))
def run(case):
 end,n,s,sub,mu,w=case
 name=f'z{end:g}_q{s:+g}_n{n}_s{sub}_w{w}'
 out=root/name;cmd=[str(exe),str(out),str(end),str(n),str(s),str(sub),str(mu),str(q['x_HII']),str(q['T_m_K'])]
 if w is not None:cmd.append(str(w))
 t=time.monotonic();r=subprocess.run(cmd,text=True,capture_output=True,timeout=210)
 row=dict(case=name,end=end,steps=n,shear=s,sub=sub,width=w,command=cmd,wall_s=time.monotonic()-t,returncode=r.returncode)
 if r.returncode:row.update(status='REJECTED',error=r.stderr);print(name,row['status'],r.stderr,flush=True);return row
 h=np.genfromtxt(out/'history.tsv',names=True,delimiter='\t');g=np.genfromtxt(out/'geometry.tsv',names=True,delimiter='\t');pk=np.genfromtxt(out/'packets.tsv',names=True,delimiter='\t')
 c=dict(l.split('=',1) for l in (out/'compression.txt').read_text().splitlines())
 assert len(h)==n+1 and np.all(np.diff(h['time_s'])>0)
 assert abs(h['eta'][-1]-math.log(21/(1+end)))<2e-15
 assert np.min(pk['energy_eV'])>=13.6 and np.min(pk['N_per_H'])>=0
 assert np.min(h['Tm_K'])>0 and np.all((h['x_HII']>=0)&(h['x_HII']<=1)&(h['x_HeII']>=0)&(h['x_HeIII']>=0)&(h['x_HeII']+h['x_HeIII']<=1))
 assert abs(h['nH_m3'][0]/q['n_H_m3']-1)<2e-14 and abs(h['Tm_K'][0]/q['T_m_K']-1)<2e-14
 eta=g['eta'];sig=g['Sigma_zz']/2;b=np.r_[0.,cumulative_trapezoid(sig,eta)]
 be=pk['birth_eta'];i=np.clip(np.searchsorted(eta,be,side='right')-1,0,len(eta)-2);dl=be-eta[i];slope=(sig[i+1]-sig[i])/(eta[i+1]-eta[i]);bb=b[i]+sig[i]*dl+.5*slope*dl*dl
 m=leggauss(mu)[0][pk['ray'].astype(int)]
 fac=lambda B:np.sqrt((1-m*m)*np.exp(2*B)+m*m*np.exp(-4*B))
 pred=pk['birth_energy_eV']*np.exp(-(eta[-1]-be))*fac(b[-1])/fac(bb)
 eerr=float(np.max(abs(pred/pk['energy_eV']-1)));assert eerr<5e-10
 tau=float(np.trapezoid(299792458.*6.6524587051e-29*h['nH_m3']*h['xe']/h['H_s'],h['eta']))
 nd=float(np.max(abs(h['number_defect'])/np.maximum(h['emitted_N'],1.)));ed=float(np.max(abs(h['energy_defect'])/np.maximum(h['emitted_U'],1.)))
 assert nd<1e-8 and ed<1e-8 and abs(tau/h['tau'][-1]-1)<2e-8
 if w is not None:assert int(c['peak_after'])<=2*mu*(sum(math.ceil(math.log(hi/lo)/w) for lo,hi in zip([13.6,24.59,54.42],[24.59,54.42,100]))+3) and float(c['max_U_relative'])<3e-14
 # PR171/PR173 inventory in eV/H; axisym ring-average, not individual x-direction ray.
 N=float(np.sum(pk['N_per_H']));U=float(np.dot(pk['N_per_H'],pk['energy_eV']));Delta=float(np.dot(pk['N_per_H']*pk['energy_eV'],(3*pk['mu_final']**2-1)/2))
 J1=float(np.dot(pk['N_per_H']*pk['energy_eV'],pk['mu_final']))
 Pperp=(U-Delta)/3;Ppar=(U+2*Delta)/3
 assert abs(U-h['U_eV'][-1])<2e-12*max(U,1e-30) and abs(N-h['N'][-1])<2e-12*max(N,1e-30)
 assert min(Pperp,Ppar)>=0 and abs(2*Pperp+Ppar-U)<2e-14*max(U,1e-30)
 rho=U*h['nH_m3'][-1]*1.602176634e-19
 native=dict(l.split('=',1) for l in (out/'uv_stress.txt').read_text().splitlines())
 scale=h['nH_m3'][-1]*1.602176634e-19
 for key,value in [('rho_J_m3',U),('flux_z_J_m3',J1),('P_parallel_J_m3',Ppar),('P_perp_J_m3',Pperp),('Delta_J_m3',Delta)]:
  assert abs(float(native[key])-scale*value)<2e-13*rho
 if c.get('isotropic_uv_reduced')=='true':assert abs(Delta/U)<2e-12
 if end==4.:assert c.get('isotropic_uv_reduced')=='true'
 crit=3*h['H_s'][-1]**2*299792458.**2/(8*math.pi*6.67430e-11)
 row.update(status='PASS_SCOPED',tau=tau,characteristic_error=eerr,number_defect=nd,energy_defect=ed,max_root=float(np.max(h['root_residual'])),compression=c,peak_packets=int(np.max(h['packets'])),terminal={k:float(h[k][-1]) for k in ('xe','x_HII','x_HeII','x_HeIII','Tm_K','N','U_eV','emitted_N','emitted_U','boundary_N','boundary_U','absorbed_N','redshift_work')},stress=dict(U=U,J1=J1,Delta=Delta,Pperp=Pperp,Ppar=Ppar,rho_J_m3=rho,Omega_UV=rho/crit,Pi_over_rho=Delta/U,native_SI={k:float(v) for k,v in native.items()}),hashes={f.name:sha(f) for f in out.iterdir() if f.is_file()})
 print(name,'PASS',tau,row['terminal']['Tm_K'],row['terminal']['x_HeIII'],row['peak_packets'],row['wall_s'],flush=True);return row
with ThreadPoolExecutor(max_workers=a.workers) as pool:r=list(pool.map(run,cases))
b={x['case']:x for x in r}
for x in r:
 if x['status']!='PASS_SCOPED':continue
 if x['end']>19 and x['width'] is not None:
  base=b[f"z{x['end']:g}_q{x['shear']:+g}_n{x['steps']}_s{x['sub']}_wNone"]
  x['uncompressed_delta']={k:x['terminal'][k]-base['terminal'][k] for k in x['terminal']}
  x['uncompressed_tau_relative']=abs(x['tau']/base['tau']-1)
  x['packet_reduction']=base['peak_packets']/x['peak_packets']
(root/'RESULTS.json').write_text(json.dumps(dict(scope='endpoint same-ray conservative quadrature short BASS geometry + long analytic FLRW',binary_sha256=sha(exe),donor_sha256=sha(a.donor),cases=r),indent=2,allow_nan=False)+'\n')
