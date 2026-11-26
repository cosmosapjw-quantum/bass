"""Independent cross-grid and native-comparison audit."""
import numpy as np,json
from pathlib import Path
from scipy.interpolate import CubicSpline
D=Path(__file__).resolve().parent
def run():
 rows={}
 for k in ['generic','whole','best']:
  a,b=[np.load(D/f'{k}_{n}.npz') for n in [1024,2048]]
  g=CubicSpline(a['t'],a['S'],axis=0)(b['t'])
  norms=lambda x:np.sqrt(np.trapezoid(np.sum(x*x,axis=2),b['t'],axis=0))
  srel=(norms(g-b['S'])/norms(b['S'])).tolist()
  v=a['B'][:,9:16];w=b['B'][:,9:16]
  bc=[float(np.linalg.norm(v[j]-w[j])/max(np.linalg.norm(w[j]),1e-300)) for j in [2,3]]
  # At second order target is close to floating-point cancellation floor.
  b2abs=float(np.linalg.norm(v[1]-w[1]))
  q=json.loads((D/f'{k}_2048.json').read_text())
  assert max(srel)<1e-6 and max(bc)<1e-5 and q['native_S3_rel']<1e-3
  rows[k]=dict(S_relative=srel,B3_B4_relative=bc,B2_abs_change=b2abs,crossover=float(np.linalg.norm(w[2])/np.linalg.norm(w[3])),native_S3_rel=q['native_S3_rel'])
 o=dict(rows=rows,scope='two independent radial/angular/time resolutions; no relative precision claim for near-zero B2; B4 partial closure')
 (D/'AUDIT.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
if __name__=='__main__':run()
