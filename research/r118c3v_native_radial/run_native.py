"""Run actual native finite-amplitude independent radial owner, scoped CPU cases."""
from pathlib import Path
import numpy as np,json,subprocess,sys,time,concurrent.futures
D=Path(__file__).resolve().parent;P=D.parent/'r118c3u_exact_wedge'
BIN=Path.home()/'worktrees/bass-r109-native-20261124/_rustcore/target/release/examples/c3v_radial'
def run(j):
 tag,eps,nt,nr,nm=j;name=f'{tag}_{eps:g}_{nt}_{nr}_{nm}';C=np.load(D.parent/'r118c3t_radial_null'/'best_4096.npz' if tag=='pred' else P/f'{tag}_selected_4096.npz')['control'];np.savetxt(D/(name+'.ctrl'),np.r_[[.001,.006,.05],(eps*C.T).ravel()][None],fmt='%.17e')
 t=time.monotonic()
 with (D/(name+'.csv')).open('w') as o,(D/(name+'.geom')).open('w') as e:
  p=subprocess.run([str(BIN),str(D.parent/'r118c3l_reachable_sky/clock.csv'),str(D/(name+'.ctrl')),str(nt),str(nr),str(nm)],stdout=o,stderr=e)
 print(name,p.returncode,time.monotonic()-t,flush=True)
 if p.returncode:raise RuntimeError(name)
 return name
def main():
 nt=int(sys.argv[1]);nr=int(sys.argv[2]);nm=int(sys.argv[3]);tags=sys.argv[4].split(',');eps=float(sys.argv[5])
 jobs=[(t,s*eps,nt,nr,nm) for t in tags for s in [-1,1]]+([('base',0.,nt,nr,nm)] if not (D/f'base_0_{nt}_{nr}_{nm}.csv').exists() else [])
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,jobs))
if __name__=='__main__':main()
