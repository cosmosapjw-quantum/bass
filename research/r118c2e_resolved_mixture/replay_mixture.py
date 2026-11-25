"""Run actual accepted BASS background and native cold temperature replay."""
import argparse,pathlib,subprocess,json,time,hashlib,concurrent.futures,os,math
import numpy as np
from scipy.constants import h,k
P=pathlib.Path
p=argparse.ArgumentParser();p.add_argument('--binary',type=P,required=True);p.add_argument('--old',type=P,required=True);p.add_argument('--hydrogen',type=P,required=True);p.add_argument('--out',type=P,required=True);p.add_argument('--workers',type=int,default=3);p.add_argument('--only',default='')
a=p.parse_args();root=a.out.resolve();root.mkdir(exist_ok=False,parents=True)
exe=a.binary.resolve();sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest()
prior=json.loads((a.old/'RESULTS.json').read_text());old=next(q for q in prior['cases'] if q['case']=='early_cold_f2048')
opt=dict(zip(old['command'][1::2],old['command'][2::2]))
assert opt['--family']=='I' and opt['--frequency-collision']=='dual'
for k0 in list(opt):
 if k0.startswith('--frequency-') or k0.startswith('--spectral-') or k0.startswith('--los-'):opt.pop(k0)
# Near 3000 K reference: use actual H-window table, start at T=3000 e^eta.
dt=.025;T=3000*math.exp(dt);data=np.loadtxt(a.hydrogen,skiprows=4)
# columns eta, x_hi, x_heii, x_heiii, w_k, n_H, H, T_r
e0=math.log(data[0,7]/T);time_grid=np.r_[e0,data[(data[:,0]>e0)&(data[:,0]<e0+dt),0],e0+dt]
interp=lambda col,e:np.interp(e,data[:,0],data[:,col])
xe=1-interp(1,time_grid);table=root/'near_ionization.tsv';np.savetxt(table,np.c_[time_grid-e0,xe],header='eta xe_per_H',comments='',fmt='%.17g')
# Set exact endpoint to avoid tiny interpolation-bound errors.
v=np.loadtxt(table,skiprows=1);v[-1,0]=dt;np.savetxt(table,v,header='eta xe_per_H',comments='',fmt='%.17g')
nH=float(np.exp(np.interp(e0,data[:,0],np.log(data[:,5]))));H=float(np.exp(np.interp(e0,data[:,0],np.log(data[:,6]))))
f0=.7096320726663242;lam0=5.611003179596944e-10
rr=(1-f0-lam0)*math.exp(-4*e0);mm=f0*math.exp(-3*e0);ll=lam0
near=dict(opt);near.update({'--duration':str(dt),'--dust-fraction':str(mm/(mm+rr+ll)),'--omega-lambda':str(ll/(mm+rr+ll)),'--shear':'0.01','--dust-beta':'0.0001,0.00003,0','--ionization':str(table),'--n-h-emit-m3':str(nH),'--h-emit-s':str(H)})
cases=[]
def add(name,base,bins,extent,nt,np_,temp):
 cases.append(dict(case=name,base=base,bins=bins,extent=extent,nt=nt,np=np_,T_emit=temp))
for bins in [128,256,512,1024,2048]:add(f'early_t{bins}',opt,bins,1.,4,8,2.7255*2801)
add('early_wide',opt,1024,2.,4,8,2.7255*2801)
for bins in [128,256,512,1024]:add(f'near_t{bins}',near,bins,.25,4,8,T)
add('near_wide',near,1024,.5,4,8,T)
# Isotropic exact thermal anchor with the same ionization history.
flrw=dict(near);flrw.update({'--family':'FLRW','--shear':'0','--dust-beta':'0,0,0'})
add('near_flrw',flrw,128,.25,4,8,T)
# Angular resolution lane at matched temperature resolution.
add('near_ang72',near,512,.25,6,12,T)
# Narrow support convergence, after wide-grid near-null diagnosis.
for bins in (128,256,512,1024):add(f'near_local_{bins}',near,bins,.01,4,8,T)
add('near_local_ang72',near,512,.01,6,12,T)
def run(q):
 name=q['case'];dest=root/name;t=time.monotonic();o=dict(q['base'])
 o.update({'--out':str(dest),'--temperature-mixture':str(q['bins']),'--temperature-log-extent':str(q['extent']),'--temperature-nmu':str(q['nt']),'--temperature-nphi':str(q['np'])})
 cmd=[str(exe)]+[str(v) for kv in o.items() for v in kv]
 r={k:v for k,v in q.items() if k!='base'};r.update(command=cmd)
 try:
  proc=subprocess.run(cmd,text=True,capture_output=True,timeout=480,env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',RAYON_NUM_THREADS='1'))
  if proc.returncode:raise RuntimeError(proc.stderr[-1800:])
  meta=dict(x.split('=',1) for x in (dest/'run.txt').read_text().splitlines() if '=' in x)
  for key in list(meta):
   try:meta[key]=float(meta[key])
   except ValueError:pass
  rays=np.genfromtxt(dest/'temperature_rays.tsv',names=True,delimiter='\t')
  z=np.genfromtxt(dest/'temperature_nodes.tsv',names=True,delimiter='\t')
  na=len(rays);L=z['log_temperature'].reshape(na,-1);w=z['weight'].reshape(na,-1)
  assert np.all(np.isfinite(L)) and np.min(w)>=-1e-14
  # Evaluate true local line samples and color slope from the measure.
  nu=2.466e15
  yy=h*nu/(k*q['T_emit'])*np.exp(-L);f=1/np.expm1(yy)
  occupation=np.sum(w*f,axis=1);slope=-np.sum(w*yy*f*(1+f),axis=1)/occupation
  out=dict(b3_gap=float(np.max(abs(rays['b3']/rays['ref_b3']-1))),b4_gap=float(np.max(abs(rays['b4']/rays['ref_b4']-1))),m0_gap=float(np.max(abs(w.sum(axis=1)-rays['ref_m0']))),min_weight=float(w.min()),occupation_min=float(occupation.min()),occupation_max=float(occupation.max()),slope_min=float(slope.min()),slope_max=float(slope.max()),angular_weight_sum=float(rays['angular_weight'].sum()/(4*np.pi)),eta=float(q['base']['--duration']))
  assert out['b3_gap']<2e-7 and out['b4_gap']<2e-7,(name,out)
  assert meta['temperature_number_defect']<2e-12 and meta['temperature_material_energy_defect']<2e-12
  r.update(status='PASS_SCOPED',metrics=out,run={k:v for k,v in meta.items() if k.startswith('temperature_')},hashes={p.name:sha(p) for p in dest.iterdir() if p.is_file()},wall_s=time.monotonic()-t)
 except Exception as e:r.update(status='FAIL_CHECK',error=repr(e),wall_s=time.monotonic()-t)
 print(name,r['status'],r.get('error',''),r.get('metrics',''),flush=True)
 return r
selected=[q for q in cases if (not q['case'].startswith('near_local') if a.only=='base' else q['case'].startswith(a.only))]
with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:results=list(pool.map(run,selected))
r=dict(binary_sha256=sha(exe),prior_results_sha256=sha(a.old/'RESULTS.json'),hydrogen_sha256=sha(a.hydrogen),near_table_sha256=sha(table),near_T_emit=T,near_T_reference_final=T*math.exp(-dt),near_nH_emit=nH,near_H_emit=H,near_x_hi_final=float(interp(1,e0+dt)),near_nHI_final_m3=float(interp(1,e0+dt)*nH*math.exp(-3*dt)),cases=results)
(root/'REPLAY_RESULTS.json').write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
print('done',len(results),flush=True)
