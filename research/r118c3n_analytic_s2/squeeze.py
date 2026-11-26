"""Bounded symplectic squeeze scan, retain nonzero wedge amplitude at fixed control norm."""
import numpy as np,json
from scipy.linalg import schur
from pathlib import Path
import concurrent.futures as cf
from joint import run_case,control
D=Path(__file__).resolve().parent
def run():
 z=json.loads((D/'JOINT.json').read_text());M=np.array(z['M']);A=control('whole');base=np.linalg.norm(A@M@A.T)
 U,V=schur(M,output='real');cases=[];meta={}
 for s,t in [(-.5,0),(.5,0),(0,-.5),(0,.5),(-.5,.5),(.5,-.5),(.5,.5),(-.5,-.5),(-1,0),(0,1)]:
  G=V@np.diag(np.exp([s,-s,t,-t]))@V.T;C=A@G;C/=np.linalg.norm(C)
  w=np.linalg.norm(C@M@C.T)/base;key=f'sq{len(meta)}'
  meta[key]=dict(s=s,t=t,wedge_ratio=float(w),admitted=bool(w>=.8),norm=float(np.linalg.norm(C)))
  if w>=.8:cases.append((key,C))
 with cf.ThreadPoolExecutor(max_workers=3) as p:rows=list(p.map(lambda t:run_case(*t,768,8192),cases))
 ref=z['rows'][1];g=z['rows'][0]
 for q in rows:q.update(meta[q['label']]);q['score']=max(q['B2']/g['B2'],q['B3']/g['B3'])
 best=min([dict(ref,score=max(ref['B2']/g['B2'],ref['B3']/g['B3']))]+rows,key=lambda q:q['score'])
 out=dict(candidates=meta,rows=rows,best=best,relative_cubic=float(best['B3']/ref['B3']),scope='finite skew-preserving squeezes followed by norm normalization; wedge amplitude >=80% of reference (chosen exploratory threshold), no global optimizer')
 (D/'SQUEEZE.json').write_text(json.dumps(out,indent=2)+'\n');print([(q['label'],q['wedge_ratio'],q['B3'],q['score']) for q in rows],best['label'],out['relative_cubic'])
if __name__=='__main__':run()
