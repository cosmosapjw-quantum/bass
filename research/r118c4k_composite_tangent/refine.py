"""Same native composite tangent, two additional time grids and fixed radial quadrature."""
from pathlib import Path
import os,subprocess,json,hashlib,time,numpy as np,concurrent.futures as cf
D=Path(__file__).resolve().parent;H=Path.home();P=D.parent;B=H/'r118c4k_bass_shadow/_rustcore/target/release/examples/c3x_radial'
assert hashlib.sha256(B.read_bytes()).hexdigest()==json.loads((D/'BUILD_ID.json').read_text())['binary_sha']
env=os.environ.copy();env['C4K_TANGENT']='1';clk=P/'r118c3l_reachable_sky/clock.csv';ctrl=D/'p0.ctrl'
def run(n):
 t=time.monotonic();tag=f'n{n}';cmd=[str(B),str(clk),str(ctrl),str(n),'192','8','8']
 with (D/(tag+'.csv')).open('w') as f,(D/(tag+'.geom')).open('w') as g:r=subprocess.run(cmd,env=env,stdout=f,stderr=g,timeout=300)
 assert r.returncode==0;print(n,r.returncode,time.monotonic()-t,flush=True);return dict(steps=n,exit=r.returncode,seconds=time.monotonic()-t,cmd=cmd)
with cf.ThreadPoolExecutor(max_workers=2) as ex:runs=list(ex.map(run,[2048,8192]))
data={}
for n,tag in [(2048,'n2048'),(4096,'p0'),(8192,'n8192')]:
 raw=(D/(tag+'.geom')).read_text()
 sky=np.array([list(map(float,l.split(',')[1:])) for l in raw.splitlines() if l.startswith('C4K_SKY,')]);geom=np.array([list(map(float,l.split(',')[1:])) for l in raw.splitlines() if l.startswith('C4K_GEOM,')])
 assert geom.shape==(2,19) and len(sky)==162
 data[n]=(sky,geom)
rows=[]
for ep in [0,1]:
 m=(data[4096][0][:,0]==ep)&(data[4096][0][:,1]>0)
 r=dict(epoch=ep,gauss_tangent=[float(data[n][1][ep,2]) for n in [2048,4096,8192]],det_tangent=[float(data[n][1][ep,3]) for n in [2048,4096,8192]],lnH=[float(data[n][1][ep,1]) for n in [2048,4096,8192]])
 for j,k in enumerate(['I','E','B']):
  x=[data[n][0][m,3+2*j]+1j*data[n][0][m,4+2*j] for n in [2048,4096,8192]]
  e0=float(np.linalg.norm(x[0]-x[1]));e1=float(np.linalg.norm(x[1]-x[2]));r[k]=dict(difference=[e0,e1],ratio=e0/max(e1,1e-300),fine_norm=float(np.linalg.norm(x[2])))
 rows.append(r);print(r,flush=True)
(D/'REFINED_COMPOSITE.json').write_text(json.dumps(dict(runs=runs,rows=rows,scope='matched native 2048/4096/8192 early steps plus quarter-count late; identical radial quadrature and control; finite step sensitivity convergence, not continuum proof'),indent=2)+'\n')
