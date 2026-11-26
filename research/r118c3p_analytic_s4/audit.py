"""Independent order coefficient comparison, preserve coarse and targeted fine evidence."""
import numpy as np,json
from pathlib import Path
from scipy.interpolate import CubicSpline
D=Path(__file__).resolve().parent
def run():
 o={}
 for k in ['generic','whole','best']:
  def comp(a,b):
   z,y=[np.load(D/f'{k}_{n}.npz') for n in [a,b]]
   t=y['t'];x=CubicSpline(z['t'],z['S'],axis=0)(t);norm=lambda x:np.sqrt(np.trapezoid(np.sum(x*x,axis=2),t,axis=0))
   S=norm(x-y['S'])/norm(y['S'])
   b3=[float(np.linalg.norm(z['B'][i,9:16]-y['B'][i,9:16])/np.linalg.norm(y['B'][i,9:16])) for i in [2,3,4]]
   b5=[float(np.linalg.norm(z['B'][i,25:36]-y['B'][i,25:36])/np.linalg.norm(y['B'][i,25:36])) for i in [3,4]]
   return dict(mesh=[a,b],S_rel=S.tolist(),B3_rel=b3,B5_rel=b5,pass_criterion=bool(max([*S,*b3,*b5])<1e-5))
  q=comp(1024,2048)
  if k=='best':q['refinement']=comp(2048,4096)
  q['native']=json.loads((D/f'{k}_2048.json').read_text())['native_S4_rel'];o[k]=q
 out=dict(rows=o,scope='predeclared 1e-5 cross-grid vector criterion, includes tiny B5 coefficient; failure retained; no exact coefficient limit')
 (D/'AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':run()
