"""Independent BASS native replay of exact REI stage contributions and quadratic table interpolation."""
from pathlib import Path
import numpy as np,json,hashlib,gzip,subprocess,time,os
D=Path(__file__).resolve().parent;H=Path.home();E=H/'worktrees/rei-htt-thomson-20261124/research/r118c4n_dg_jvp';K=E.parent/'r118c4m_coupled_stage';SH=H/'r118c4n_rei_shadow'
def sha(b):return hashlib.sha256(b).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2,allow_nan=False)+'\n')
def main():
 b=SH/'bridge/target/release/c4n_bass';bid=json.loads((E/'BUILD_ID.json').read_text());assert sha(b.read_bytes())==bid['bins']['c4n_bass']
 assert sha((D/'native.rs').read_bytes())==bid['changes']['bridge/src/bin/c4n_bass.rs']['sha'];(D/'c4n_bass.gz').write_bytes(gzip.compress(b.read_bytes(),mtime=0))
 jobs=[];refs={}
 for tag in ['base','H-0.01','H+0.01','H-0.003','H+0.003']:
  p=E/(tag+'_stage.csv');q=D/(tag+'_stage.csv');q.write_bytes(p.read_bytes());refs[tag]=np.loadtxt(q,delimiter=',',dtype=np.longdouble);jobs.append((tag,q))
 z=refs['base'];m=refs['H-0.01'];p=refs['H+0.01'];h=np.longdouble('.01')
 assert np.array_equal(z[:,[0,10]],m[:,[0,10]]) and np.array_equal(z[:,[0,10]],p[:,[0,10]])
 d1=(p-m)/(2*h);d2=((p-z)+(m-z))/(2*h*h);rows=[];runs=[]
 for ep in [-.003,.003,-.001,.001]:
  t=z+np.longdouble(str(ep))*d1+np.longdouble(str(ep))**2*d2;tag=f'table{ep:+g}';q=D/(tag+'_stage.csv');np.savetxt(q,t,delimiter=',',fmt='%.17e');jobs.append((tag,q))
 for tag,p in jobs:
  t=time.monotonic();cmd=[str(b),str(p)]
  with (D/(tag+'.csv')).open('w') as f,(D/(tag+'.log')).open('w') as g:r=subprocess.run(cmd,stdout=f,stderr=g,timeout=100)
  assert r.returncode==0,tag;runs.append(dict(tag=tag,exit=r.returncode,seconds=time.monotonic()-t,source_sha=sha(p.read_bytes())))
  print(tag,'completed',flush=True)
 def load(tag):return np.genfromtxt(D/(tag+'.csv'),names=True,delimiter=',')
 for tag in refs:
  a=load(tag);g=np.genfromtxt(K/(tag+'_history.csv'),names=True,delimiter=',');m=np.genfromtxt(K/(tag+'_matter.csv'),names=True,delimiter=',')
  fields=['a','h','S0','S1','S2','S3','S4','gauss'];diff={k:float(np.max(abs(a[k]-g[k]))) for k in fields}
  fg=max(float(np.max(abs(a[k]-m[k]))) for k in [f'F{i}{j}' for i in range(3) for j in range(3)])
  w=np.loadtxt(E/(tag+'_work.csv'),delimiter=',');rows.append(dict(tag=tag,geometry_gap=diff,coframe_gap=fg,work_density_max_abs=float(max(abs(w[:,1]-w[:,2]))),work_density_max=float(max(abs(w[:,2])))))
  assert max(diff.values())<1e-12 and fg<1e-12
 held=[]
 for ep in [-.003,.003]:
  t=f'table{ep:+g}';tag=f'H{ep:+g}';a=load(t);b0=load(tag);ref=refs[tag];tab=np.loadtxt(D/(t+'_stage.csv'),delimiter=',',dtype=np.longdouble)
  amp=np.maximum(np.max(abs(ref-z),axis=0),np.longdouble('1e-300'));gap=np.max(abs(tab-ref),axis=0)
  fields=['h','S0','S4','I2','E2','B3'];fd={k:float(a[k][-1]-b0[k][-1]) for k in fields}
  held.append(dict(p=ep,stage_absolute_gap=gap.astype(float).tolist(),stage_response_relative=(gap/amp).astype(float).tolist(),terminal_native_gap=fd,terminal_actual_response={k:float(b0[k][-1]-load('base')[k][-1]) for k in fields}))
 coeff=[]
 for eps in [.003,.001]:
  a,b0,c=load(f'table{eps:+g}'),load(f'table{-eps:+g}'),load('base');row={'h':eps}
  for k in ['h','S0','S4','I2','E2','B3']:
   # coefficients of norms, not harmonic vector jets; tiny second differences reported even if cancellation-limited.
   row[k]=[float((np.longdouble(a[k][-1])-b0[k][-1])/(2*eps)),float(((np.longdouble(a[k][-1])-c[k][-1])+(np.longdouble(b0[k][-1])-c[k][-1]))/(2*eps*eps))]
  coeff.append(row)
 np.savez_compressed(D/'TABLE_JET.npz',base=z,first=d1,second=d2)
 write('TABLE_REPLAY.json',dict(runs=runs,replays=rows,heldout=held,output_secant_coefficients=coeff,source_build_sha=sha((E/'BUILD_ID.json').read_bytes()),scope='actual REI native stage material owner captured, independent native SDIRK BASS replay. Quadratic interpolation of prescribed material tables trained on H ±0.01, held-out actual ±0.003; output coefficients finite secants of norms, not direct analytic C4M Taylor2 nor live chemical JVP.'))
def lie():
 b=SH/'bridge/target/release/c4n_bass';tm=time.monotonic()
 with (D/'LIE.csv').open('w') as f,(D/'lie_native.log').open('w') as g:r=subprocess.run([str(b),'lie'],stdout=f,stderr=g,timeout=150)
 assert r.returncode==0
 a=np.genfromtxt(D/'LIE.csv',names=True,delimiter=',',dtype=None,encoding='utf8');assert len(a)==36
 rows=[]
 for fam in sorted(set(a['family'])):
  z=a[a['family']==fam];rr=dict(family=fam,initial_codazzi=float(z['initial_codazzi'][0]),max_codazzi=z['max_codazzi'].tolist(),max_gauss=z['max_gauss'].tolist(),max_jacobi=z['max_jacobi'].tolist(),B3=z['B3'].tolist(),E2=z['E2'].tolist(),h=z['h'].tolist(),S_norm=z['S_norm'].tolist())
  for k in ['B3','E2','h','S_norm']:
   v=z[k];rr[k+'_ratio']=float(abs(v[1]-v[0])/max(abs(v[2]-v[1]),1e-300))
  rows.append(rr)
 write('LIE_NONLINEAR.json',dict(rows=rows,seconds=time.monotonic()-tm,scope='actual native Lie streaming coupled to Raychaudhuri and physical radiation energy/pressure/flux, congruence N/A, midpoint evolution to du=0.2. Initial class-B Codazzi defect retained (not full Einstein solution); class-A diagonal cases constraint audit; finite lmax6.'))
 print(rows,flush=True)
if __name__=='__main__':{'replay':main,'lie':lie}[os.sys.argv[1]]()
