import numpy as np,json
from pathlib import Path
D=Path(__file__).resolve().parent;G=np.array(json.loads((D.parent/'r118c3c_memory_kernel/WEDGE.json').read_text())['gram']);P=2*G
rng=np.random.default_rng(20261126);rows=[]
for r in (2,3,4,5):
 v=[]
 for k in range(1000):
    u,_=np.linalg.qr(rng.normal(size=(5,r)));x=rng.normal(size=(r,r));w=u@(x-x.T)@u.T;ww=w[np.triu_indices(5,1)]
    v.append(float(np.linalg.norm(P@ww)/np.linalg.norm(ww)))
 rows.append(dict(dimension=r,min=min(v),max=max(v),samples=len(v)))
assert min(x['min'] for x in rows[:2])>=1/np.sqrt(5)-1e-12
print(rows);(D/'RANK_PROBE.json').write_text(json.dumps(rows,indent=2)+'\n')
