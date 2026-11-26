"""Native early-to-late sky probes, matched early Frobenius controls."""
import json,sys,subprocess,numpy as np,concurrent.futures as cf
from pathlib import Path
D=Path(__file__).resolve().parent;ROOT=D.parents[1]
sys.path.insert(0,str(D.parent/'r118c3l_reachable_sky'))
from reach import EARLY,CLOCK
BIN=ROOT/'_rustcore/target/release/examples/r118c3l_early_sky'
def prepare():
 e=np.genfromtxt(EARLY,names=True,delimiter=',');l=np.genfromtxt(CLOCK,names=True,delimiter=',');cut=np.log(1/21/e['a'][0])
 assert abs(e['u'][-1]-cut)<1e-12
 np.savetxt(D/'clock.csv',np.c_[np.r_[e['u'],cut+l['u'][1:]],np.r_[e['ne_m3'],l['ne_m3'][1:]]],delimiter=',',header='u,ne_m3',comments='',fmt='%.17e')
 q=json.loads((D/'R7.json').read_text())[-1];rng=np.random.default_rng(123)
 for key,A in [('late',np.array(q['late']['control'])),('whole',np.array(q['whole']['control'])),('generic',rng.normal(size=(5,4)))]:
  A=A/np.linalg.norm(A)
  for sign in [1,-1]:
   a=np.r_[[.001,.006,.05],(sign*.0025*A.T).ravel()]
   np.savetxt(D/f'{key}_{sign}.ctrl',a[None,:],fmt='%.17e')
def run(n):
 def f(t):
  key,sign=t;label=f'{key}_{n}_{sign}'
  with (D/(label+'.csv')).open('w') as o,(D/(label+'.geom')).open('w') as e:
   p=subprocess.run([str(BIN),str(D/'clock.csv'),str(D/f'{key}_{sign}.ctrl'),str(n),'7'],stdout=o,stderr=e)
  print(label,p.returncode,flush=True);return p.returncode
 with cf.ThreadPoolExecutor(max_workers=2) as p:r=list(p.map(f,[(k,s) for k in ['late','whole','generic'] for s in [1,-1]]))
 if any(r):raise SystemExit(1)
def analyze(n):
 rows={};eps=.0025
 for k in ['late','whole','generic']:
  a,b=[np.genfromtxt(D/f'{k}_{n}_{s}.csv',names=True,delimiter=',') for s in [1,-1]]
  out={}
  for ep in [0,1]:
   f=(a['epoch']==ep)&(a['ell']==3)
   p=a['Bre'][f]+1j*a['Bim'][f];q=b['Bre'][f]+1j*b['Bim'][f]
   out[str(ep)]=dict(even=float(np.linalg.norm(p+q)/(2*eps**2)),odd=float(np.linalg.norm(p-q)/(2*eps**3)))
  gg=[]
  for s in [1,-1]:
   z=(D/f'{k}_{n}_{s}.geom').read_text().splitlines()
   assert z[-1].startswith('min_screen=')
   v=np.genfromtxt(z[:-1],names=True,delimiter=',')
   gg.append(dict(max_gauss=float(max(abs(v['gauss']))),min_screen=float(z[-1].split('=')[1]),a=v['a'].tolist()))
  rows[k]=dict(B3=out,geometry=gg)
 (D/f'NATIVE{n}.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows,flush=True)
if __name__=='__main__':
 prepare();n=int(sys.argv[1]);run(n);analyze(n)
