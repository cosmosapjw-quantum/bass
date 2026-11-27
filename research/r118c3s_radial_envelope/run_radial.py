"""Actual nonlinear radial Taylor coefficients under the fixed physical budget."""
import sys,json,numpy as np
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
D=Path(__file__).resolve().parent
from radial_jets import solve,window
def run(t):
 name,C,nt=t;u,s,m,b=solve(C,nt,48 if nt<=1024 else 96,6 if nt<=1024 else 8)
 np.savez_compressed(D/f'{name}_{nt}.npz',t=u,S=s,monopole=m,B=b,control=C)
 z=b[:,9:16];obj=max(np.linalg.norm(np.array([(sg*.01)**k for k in range(1,6)])@z) for sg in [-1,1])
 return dict(name=name,nt=nt,B3=np.linalg.norm(z,axis=1).tolist(),objective=float(obj))
def main():
 a=json.loads((D/'R7.json').read_text())['rows'];r=[x for x in a if x['nw']==2 and x['nr']==96][0];C=np.array(r['control'])
 c=np.load(D.parent/'r118c3r_fixed_wedge/best_fine.npz')['control'];base=np.c_[c[:,0],np.repeat(c[:,1:],2,axis=1)]
 G=np.array(r['G']);assert abs(np.trace(base@G@base.T)-r['budget'])<1e-10
 # same metric budget, distinct W amplitude. Constant profiles exactly embed prior control.
 jobs=[(n,A,t) for n,A in [('embedded',base),('radial2',C)] for t in [1024,2048]]
 with ProcessPoolExecutor(max_workers=2) as p:rows=list(p.map(run,jobs))
 for q in rows:print(q,flush=True)
 old=np.load(D.parent/'r118c3r_fixed_wedge/best_fine.npz')['B']
 new=np.load(D/'embedded_2048.npz')['B']
 # Check high-order coefficients relative, B2 close to cancellation floor.
 err=[float(np.linalg.norm(new[k,9:16]-old[k,9:16])/np.linalg.norm(old[k,9:16])) for k in [2,3,4]]
 o=dict(rows=rows,embedded_reproduction=err,scope='two-window direct order4 geometry and order5 magnetic jet; fixed chosen FD number metric, W changes; no native radial solver')
 (D/'RADIAL_JETS.json').write_text(json.dumps(o,indent=2)+'\n')
if __name__=='__main__':main()
