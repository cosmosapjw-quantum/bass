"""Native source seed cases with signed probes and matched controls."""
import numpy as np,json,subprocess,sys,concurrent.futures as cf
from pathlib import Path
D=Path(__file__).resolve().parent;ROOT=D.parents[1];CLOCK=ROOT/'research/r118c2r_multispecies/rei_q256.csv';BIN=ROOT/'_rustcore/target/release/examples/r118c3k_radiation'
def prep():
 d=json.loads((D/'R7.json').read_text())['rows'][-1];A=np.array(d['A']);assert A.shape==(5,6)
 rng=np.random.default_rng(20261126);G=rng.normal(size=(5,6));G/=np.linalg.norm(G,2)
 out={'target':A,'generic':G}
 for mode,k in [('I',4),('P',5)]:
  Z=np.zeros((5,6));Z[1,k]=1.;out[mode]=Z
 for name,z in out.items():
  for amp,n in [(.005,256),(.0025,512)]:
   for sign in [1,-1]:
    label=f'{name}_{n}_{sign}'
    np.savetxt(D/(label+'.ctrl'),np.r_[[.001,.006,.05],(sign*amp*z.T).ravel()][None,:],fmt='%.17e')
 return out
def run(labels):
 def f(l):
  n=int(l.split('_')[1])
  with (D/(l+'.csv')).open('w') as a,(D/(l+'.geom')).open('w') as b:
   p=subprocess.run([str(BIN),str(CLOCK),str(D/(l+'.ctrl')),str(n),'7'],stdout=a,stderr=b)
  print(l,p.returncode,flush=True);return p.returncode
 with cf.ThreadPoolExecutor(max_workers=2) as p:r=list(p.map(f,labels))
 if any(r):raise SystemExit(1)
def read(l):
 s=(D/(l+'.geom')).read_text().splitlines();assert s[-1].startswith('gauss=') and s[0].startswith('# initial_constraint=')
 return np.genfromtxt(s[1:-1],names=True,delimiter=','),float(s[-1].split('=')[1])
def vec(l):
 s=np.genfromtxt(D/(l+'.csv'),names=True,delimiter=',');z=s['ell']==3;return s['re'][z]+1j*s['im'][z]
def analyze(n):
 eps=.005 if n==256 else .0025
 v=np.load(D/'response_both.npz');u=v['u'];s=v['values'][0]
 res={}
 for name in ['I','P','target','generic']:
  l=f'{name}_{n}_1';r=f'{name}_{n}_-1';a,g=read(l);b,h=read(r);assert np.array_equal(a['u'],b['u'])
  A=np.loadtxt(D/(l+'.ctrl'))[3:].reshape(6,5).T/eps
  pred=np.stack([np.interp(a['u'],u,x) for x in A@s],axis=1)
  got=np.stack([(a[f'S{i}']-b[f'S{i}'])/(2*eps) for i in range(5)],axis=1)
  E=(vec(l)+vec(r))/(2*eps**2);O=(vec(l)-vec(r))/(2*eps**3)
  res[name]=dict(relative_S=float(np.linalg.norm(got-pred)/np.linalg.norm(pred)),even_B3=float(np.linalg.norm(E)),odd_B3=float(np.linalg.norm(O)),gauss=max(abs(g),abs(h)))
 (D/f'NATIVE{n}.json').write_text(json.dumps(res,indent=2)+'\n');print(res,flush=True)
if __name__=='__main__':
 prep();n=int(sys.argv[1]);run([f'{m}_{n}_{s}' for m in ['I','P','target','generic'] for s in [1,-1]]);analyze(n)
