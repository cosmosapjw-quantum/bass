"""Direct exact fixed-W/G sphere search on actual high-order radial jets."""
import sys,json,numpy as np
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
D=Path(__file__).resolve().parent;P=D.parent/'r118c3s_radial_envelope';Q=D.parent/'r118c3t_radial_null'
sys.path.insert(0,str(P));from radial_jets import solve,window
from sphere import start,change,check,H,G,M
def obj(v,ep=.01):
 return float(max(np.linalg.norm(np.array([(s*ep)**k for k in range(1,6)])@v) for s in [-1,1]))
def run(job):
 tag,label,A,nt=job;C=A@H;u,s,q,b=solve(C,nt,192,6 if nt<=1024 else 8)
 v=b[:,9:16];z=dict(tag=tag,label=label,nt=nt,**check(start(tag),A),objective=obj(v),B3=np.linalg.norm(v,axis=1).tolist())
 np.savez_compressed(D/f'{tag}_{label}_{nt}.npz',t=u,S=s,monopole=q,B=b,control=C,A=A);print(z,flush=True);return z
def main():
 jobs=[]
 for tag in ['base','best']:
  A=start(tag);jobs.append((tag,'ref',A,1024))
  # Finite, physically nontrivial directions; within each stratum W exactly fixed.
  for j,k,t in [(0,0,-.35),(0,0,.35),(0,1,-.35),(0,1,.35),(1,0,-.5),(1,0,.5)]:
   jobs.append((tag,f'j{j}k{k}t{t:g}',change(A,j,k,t),1024))
 with ProcessPoolExecutor(max_workers=2) as p:rows=list(p.map(run,jobs))
 # select best actual candidate per fixed-W stratum and independently refine.
 fine=[]
 for tag in ['base','best']:
  ref=next(x for x in rows if x['tag']==tag and x['label']=='ref');r=min((x for x in rows if x['tag']==tag),key=lambda x:x['objective'])
  A=np.load(D/f"{tag}_{r['label']}_1024.npz")['A'];fine.extend([(tag,'selected',A,2048),(tag,'selected',A,4096)])
 with ProcessPoolExecutor(max_workers=2) as p:rr=list(p.map(run,fine))
 out={}
 for tag in ['base','best']:
  a,b=[x for x in rr if x['tag']==tag];ref=np.load(Q/('base_4096.npz' if tag=='base' else 'best_4096.npz'))['B'][:,9:16]
  x,y=[np.load(D/f'{tag}_selected_{nt}.npz')['B'][:,9:16] for nt in [2048,4096]]
  err=[float(np.linalg.norm(x[k]-y[k])/max(np.linalg.norm(y[k]),1e-300)) for k in [2,3,4]]
  z=np.load(D/f'{tag}_selected_4096.npz');C=z['control'];yp=np.linspace(0,60,1001);V=np.array([window(yp),1-window(yp)]);peak=max(np.linalg.norm(C[:,1+2*j:3+2*j]@V,axis=0).max() for j in range(3))
  out[tag]=dict(**b,reference_objective=obj(ref),objective_ratio=b['objective']/obj(ref),quartic_ratio=b['B3'][3]/np.linalg.norm(ref[3]),fine_relative=err,peak_stf=float(peak),B2=float(np.linalg.norm(y[1])))
 assert all(v['wedge_relative']<1e-5 and v['metric_relative']<1e-12 for v in rows+rr)
 o=dict(coarse=rows,fine=rr,selected=out,scope='finite sphere search within each exact numerical W and G stratum; no global minimum, no exact nonlinear null')
 (D/'SEARCH.json').write_text(json.dumps(o,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':main()
