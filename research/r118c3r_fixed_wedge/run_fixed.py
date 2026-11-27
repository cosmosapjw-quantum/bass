"""Actual fixed-W metric paths and quartic polynomial on one affine line."""
import sys,json,numpy as np
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
D=Path(__file__).resolve().parent;P=D.parent/'r118c3p_analytic_s4'
sys.path.insert(0,str(P));from jets4 import solve
from fixed import C0,check
def run(t):
 label,C,nt=t
 u,s,m,b=solve(C,nt,48 if nt<=1024 else 96,6 if nt<=1024 else 8)
 np.savez_compressed(D/f'{label}.npz',t=u,S=s,monopole=m,B=b,control=C)
 v=b[:,9:16];print(label,check(C),np.linalg.norm(v,axis=1).tolist(),flush=True)
 return v
def objective(v,e=.01):
 return float(max(np.linalg.norm(np.array([(sg*e)**k for k in range(1,6)])@v) for sg in [-1,1]))
def main():
 z=np.load(D/'CONTROLS.npz');labels=z['labels'];cs=z['controls'];jobs=[('base',C0,1024)]+[(str(k),c,1024) for k,c in zip(labels,cs)]
 # affine path on the actual nontrivial weak-plane endpoint. Its interior
 # is not constrained; use it only as a polynomial identity check.
 idx=int(np.argmax([check(c)['distance'] for c in cs]));d=cs[idx]-C0
 for t in [-1.,-.5,.5,.25]:jobs.append((f'poly_{t:g}',C0+t*d,1024))
 with ProcessPoolExecutor(max_workers=3) as pool:res=list(pool.map(run,jobs))
 base=res[0];rows={}
 for k,c,v in zip(labels,cs,res[1:1+len(cs)]):
  rows[str(k)]=dict(**check(c),B4_ratio=float(np.linalg.norm(v[3])/np.linalg.norm(base[3])),B4_vector_relative=float(np.linalg.norm(v[3]-base[3])/np.linalg.norm(base[3])),objective_ratio=objective(v)/objective(base),B3=float(np.linalg.norm(v[2])))
 nodes=np.array([-1,-.5,0,.5,1.]);v=np.array([res[-4][3],res[-3][3],base[3],res[-2][3],res[1+idx][3]])
 coef=np.linalg.solve(np.vander(nodes,5,increasing=True),v);pred=np.array([.25**k for k in range(5)])@coef;actual=res[-1][3]
 # Refine most improved control and baseline on identical grid.
 best=min(rows,key=lambda k:rows[k]['objective_ratio']);i=list(labels).index(best)
 with ProcessPoolExecutor(max_workers=2) as pool:fine=list(pool.map(run,[('base_fine',C0,2048),('best_fine',cs[i],2048)]))
 out=dict(rows=rows,polynomial=dict(path=str(labels[idx]),coefficient_norms=np.linalg.norm(coef,axis=1).tolist(),check_relative=float(np.linalg.norm(pred-actual)/np.linalg.norm(actual))),best=best,fine_objective_ratio=objective(fine[1])/objective(fine[0]),fine_B4_ratio=float(np.linalg.norm(fine[1][3])/np.linalg.norm(fine[0][3])),fine_change_relative=float(np.linalg.norm((fine[1]-fine[0])[3]-(res[1+i]-base)[3])/max(np.linalg.norm((fine[1]-fine[0])[3]),1e-300)),scope='finite fixed physical norm/W control paths; affine-line polynomial check diagnostic outside constraints. No global optimum or exact invariant.')
 (D/'RESULTS.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':main()
