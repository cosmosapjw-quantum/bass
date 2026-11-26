"""Actual early-to-late shear and separate cubic integration."""
import numpy as np,json,sys,subprocess,concurrent.futures as cf
from pathlib import Path
D=Path(__file__).resolve().parent;ROOT=D.parents[1];OLD=D.parent/'r118c3l_reachable_sky';BIN=ROOT/'_rustcore/target/release/examples'
from symmetry import rotation
def run(n,eps,keys):
 def job(t):
  name,sign=t;lab=f'{name}_{n}_{eps:g}_{sign}';orig=np.loadtxt(OLD/f'{"whole" if name=="rot" else name if name!="zero" else "whole"}_1.ctrl')
  a=orig.copy();a[3:]=a[3:]/.0025*eps*sign
  if name=='rot':a[3:]=(rotation(np.pi/3)@a[3:].reshape(4,5).T).T.ravel()
  if name=='zero':a[3:]=0
  p=D/(lab+'.ctrl');np.savetxt(p,a[None,:],fmt='%.17e')
  with (D/(lab+'.csv')).open('w') as f,(D/(lab+'.geom')).open('w') as g:
   z=subprocess.run([str(BIN/'r118c3m_shear'),str(OLD/'clock.csv'),str(p),str(n),'7'],stdout=f,stderr=g)
  print(lab,z.returncode,flush=True);return z.returncode
 jobs=[(k,s) for k in keys for s in ([0] if k=='zero' else [-1,1])]
 with cf.ThreadPoolExecutor(max_workers=3) as p:r=list(p.map(job,jobs))
 if any(r):raise SystemExit(1)
def geom(l):
 s=(D/(l+'.geom')).read_text().splitlines();assert s[-1].startswith('min_screen=')
 return np.genfromtxt(s[:-1],names=True,delimiter=',')
def prepare(n,eps,key):
 a,b=[geom(f'{key}_{n}_{eps:g}_{s}') for s in [1,-1]]
 zero=geom(f'zero_{n}_0.01_0');assert np.array_equal(a['u'],b['u']) and np.array_equal(a['u'],zero['u'])
 S=lambda a:np.stack([a[f'S{i}'] for i in range(5)],axis=1)
 s1=(S(a)-S(b))/(2*eps);s2=(S(a)+S(b)-2*S(zero))/(2*eps**2)
 p=D/f'{key}_{n}_{eps:g}_orders_input.csv'
 np.savetxt(p,np.c_[a['u'],zero['h'],s1,s2],delimiter=',',header='u,h,S10,S11,S12,S13,S14,S20,S21,S22,S23,S24',comments='',fmt='%.17e')
 return p
def extract(n,eps,key):
 p=prepare(n,eps,key);l=f'{key}_{n}_{eps:g}_orders'
 with (D/(l+'.csv')).open('w') as f:
  z=subprocess.run([str(BIN/'r118c3m_orders'),str(p),str(OLD/'clock.csv'),str(n*2)],stdout=f)
 assert z.returncode==0
 a=np.genfromtxt(D/(l+'.csv'),names=True,delimiter=',')
 get=lambda j: a['re'][(a['order']==j)&(a['ell']==3)]+1j*a['im'][(a['order']==j)&(a['ell']==3)]
 b,c,d=get(2),get(3),get(5)
 # actual finite amplitude
 zz=[]
 for s in [1,-1]:
  g=np.genfromtxt(D/f'{key}_{n}_{eps:g}_{s}.csv',names=True,delimiter=',');m=(g['epoch']==1)&(g['ell']==3);zz.append(g['Bre'][m]+1j*g['Bim'][m])
 native=(zz[0]-zz[1])/(2*eps**3)
 out=dict(n=n,eps=eps,key=key,quadratic=float(np.linalg.norm(b)),cubic_linear=float(np.linalg.norm(c)),cubic_geometry=float(np.linalg.norm(d)),cubic_total=float(np.linalg.norm(c+d)),native_odd=float(np.linalg.norm(native)),native_diff=float(np.linalg.norm(native-c-d)),cubic_vector=np.c_[(c+d).real,(c+d).imag].tolist())
 print(out,flush=True);return out
if __name__=='__main__':
 n=int(sys.argv[1]);eps=float(sys.argv[2]);keys=sys.argv[3].split(',');run(n,eps,keys)
 rows=[extract(n,eps,k) for k in keys if k!='zero']
 (D/f'ORDERS_{n}_{eps:g}.json').write_text(json.dumps(rows,indent=2)+'\n')
