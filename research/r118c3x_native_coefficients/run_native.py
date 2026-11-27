"""Actual C3W harmonic collision binary with explicit amplitude/time/radial/angular axes."""
from pathlib import Path
import numpy as np,json,subprocess,time,concurrent.futures,hashlib,sys
D=Path(__file__).resolve().parent;P=D.parent/'r118c3u_exact_wedge';W=D.parent/'r118c3w_harmonic_collision'
BIN=Path.home()/'worktrees/bass-r109-native-20261124/_rustcore/target/release/examples/c3w_radial'
def run(j):
 tag,ep,nt,nr,nm=j;name=f'{tag}_{ep:g}_{nt}_{nr}_{nm}'
 C=np.load(D.parent/'r118c3t_radial_null'/'best_4096.npz' if tag=='pred' else P/f'{tag}_selected_4096.npz')['control']
 np.savetxt(D/(name+'.ctrl'),np.r_[[.001,.006,.05],(ep*C.T).ravel()][None],fmt='%.17e')
 t=time.monotonic()
 with (D/(name+'.csv')).open('w') as o,(D/(name+'.geom')).open('w') as e:
  p=subprocess.run([str(BIN),str(D.parent/'r118c3l_reachable_sky/clock.csv'),str(D/(name+'.ctrl')),str(nt),str(nr),str(nm)],stdout=o,stderr=e)
 print(name,p.returncode,time.monotonic()-t,flush=True)
 if p.returncode:raise RuntimeError(name)
 return name
def main():
 ident=json.loads((W/'ops/BUILD_ID.json').read_text());assert hashlib.sha256(BIN.read_bytes()).hexdigest()==ident['binary']['sha256']
 jobs=[]
 for tag in ['pred','best']:
  for ep,nt in [(.02,2048),(.06,2048),(.06,4096),(.01,4096),(.03,4096)]:
   for s in [-1,1]:jobs.append((tag,s*ep,nt,192,8))
 for nr,nm in [(256,8),(192,12)]:
  for ep in [-.04,.04]:jobs.append(('best',ep,4096,nr,nm))
 for ep in [.02,.04,.06]:
  for s in [-1,1]:jobs.append(('best',s*ep,8192,192,8))
 jobs=[j for j in jobs if not (D/f'{j[0]}_{j[1]:g}_{j[2]}_{j[3]}_{j[4]}.csv').exists()]
 (D/'RUN_CONTRACT.json').write_text(json.dumps(dict(binary=ident['binary'],jobs=jobs,prior_scope=str(W),scope='native C3W exactly unchanged binary, fixed lmax8'),indent=2)+'\n')
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,jobs))
if __name__=='__main__':main()
