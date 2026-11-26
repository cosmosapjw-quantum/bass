"""Additional amplitude refinement, independent from native time refinement."""
import json,subprocess,numpy as np,concurrent.futures as cf
from pathlib import Path
D=Path(__file__).resolve().parent
from native import BIN
def run():
 rows={}
 def job(t):
  key,sign=t;lab=f'{key}_half_{sign}';a=np.loadtxt(D/f'{key}_{sign}.ctrl');a[3:]*=.5
  p=D/(lab+'.ctrl');np.savetxt(p,a[None,:],fmt='%.17e')
  with (D/(lab+'.csv')).open('w') as f,(D/(lab+'.geom')).open('w') as g:
   r=subprocess.run([str(BIN),str(D/'clock.csv'),str(p),'4096','7'],stdout=f,stderr=g)
  print(lab,r.returncode,flush=True);return r.returncode
 with cf.ThreadPoolExecutor(max_workers=2) as ex:r=list(ex.map(job,[(k,s) for k in ['whole','generic'] for s in [1,-1]]))
 if any(r):raise SystemExit(1)
 eps=.00125
 for k in ['whole','generic']:
  a,b=[np.genfromtxt(D/f'{k}_half_{s}.csv',names=True,delimiter=',') for s in [1,-1]]
  m=(a['epoch']==1)&(a['ell']==3);p=a['Bre'][m]+1j*a['Bim'][m];q=b['Bre'][m]+1j*b['Bim'][m]
  rows[k]=dict(even=float(np.linalg.norm(p+q)/(2*eps**2)),odd=float(np.linalg.norm(p-q)/(2*eps**3)))
 (D/'AMP.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
if __name__=='__main__':run()
