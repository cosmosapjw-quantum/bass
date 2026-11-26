"""Further bounded squeeze in the weak temporal skew plane."""
import numpy as np,json
from scipy.linalg import schur
from pathlib import Path
import concurrent.futures as cf
from joint import run_case,control
D=Path(__file__).resolve().parent
def run():
 z=json.loads((D/'JOINT.json').read_text());M=np.array(z['M']);A=control('whole');base=np.linalg.norm(A@M@A.T);_,V=schur(M,output='real');meta={};cases=[]
 for s in [-2,-3,-4,-5,-6,-7,-8]:
  G=V@np.diag(np.exp([s,-s,0,0]))@V.T;C=A@G;C/=np.linalg.norm(C);w=np.linalg.norm(C@M@C.T)/base;k='deep'+str(-s)
  meta[k]=dict(s=s,wedge_ratio=float(w),admitted=bool(w>=.8))
  if w>=.8:cases.append((k,C))
 with cf.ThreadPoolExecutor(max_workers=3) as p:rows=list(p.map(lambda t:run_case(*t,768,8192),cases))
 ref=z['rows'][1];gen=z['rows'][0]
 for q in rows:q.update(meta[q['label']]);q['score']=max(q['B2']/gen['B2'],q['B3']/gen['B3'])
 best=min(rows,key=lambda q:q['score']);C=np.array(best['control'])
 refine=[run_case('deep_best',C,384,8192),run_case('deep_bestfine',C,768,16384)]
 out=dict(candidates=meta,rows=rows,best=best,refinement=refine,cubic_ratio=float(best['B3']/ref['B3']),scope='bounded weak-plane symplectic squeeze, fixed Frobenius norm and >=0.8 wedge; no global optimum, tiny B2 near numerical floor')
 (D/'DEEP_SQUEEZE.json').write_text(json.dumps(out,indent=2)+'\n');print([(q['label'],q['wedge_ratio'],q['B2'],q['B3']) for q in rows],best['label'],[(q['B2'],q['B3']) for q in refine],flush=True)
if __name__=='__main__':run()
