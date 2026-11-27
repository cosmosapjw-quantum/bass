"""C4B independently refined physical temporal matrices and finite-mesh transfer."""
from pathlib import Path
import sys,json,numpy as np,hashlib,concurrent.futures as cf,time
D=Path(__file__).resolve().parent;P=D.parent;S=P/'r118c3s_radial_envelope';A4=P/'r118c4a_robust_wedge'
sys.path.insert(0,str(S));from envelope import solve
ns={'__file__':str(A4/'bass.py'),'__name__':'prior'};exec(compile((A4/'bass.py').read_text(),ns['__file__'],'exec'),ns)
wedge,jac,P1,P3=map(ns.get,['wedge','jac','P1','P3']);P1=P1.astype(np.longdouble);P3=P3.astype(np.longdouble)
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(nr,nt):
 t=time.monotonic();r=solve(2,nr,nt);r['seconds']=time.monotonic()-t;write(f'M_{nr}_{nt}.json',r);print('matrix',nr,nt,r['whitened_sv'],flush=True)
def analysis():
 prior=json.loads((S/'RADIAL_FINE.json').read_text());H=np.array(prior['H']);M=np.array(prior['M'])
 z=np.load(A4/'CONTROLS.npz');A0=z['A'][list(z['labels']).index('baseline')];target=P1@wedge(A0,M);norm=float(np.linalg.norm(target));budget=float(np.sum(A0*A0))
 rows=[prior]+[json.loads((D/f'M_{nr}_{nt}.json').read_text()) for nr,nt in [(192,1536),(256,1536),(256,3072)] if (D/f'M_{nr}_{nt}.json').exists()]
 assert len(rows)>=2
 mats=[];labels=[]
 for r in rows:
  Q=H@np.linalg.inv(np.array(r['H']));N=Q@np.array(r['M'])@Q.T;N=(N-N.T)/2;mats.append(N);labels.append(f"{r['nr']}_{r['nt']}")
 candidates={k:a for k,a in zip(z['labels'].tolist(),z['A']) if k in ['baseline','local_newton','canon_192_768_01','canon_192_768_10']}
 # Fit only first new same-radial temporal matrix. Finest is held out, if available.
 N=mats[1];A=candidates['local_newton'].copy();history=[]
 def res(A):return np.r_[np.asarray((wedge(A,N)-target)/norm,float),(np.sum(A*A)-budget)/budget]
 for i in range(16):
  r=res(A);J=np.vstack([jac(A,N)/norm,2*A.ravel()/budget]);u,s,v=np.linalg.svd(J,full_matrices=False);ok=s>max(1e-12,s[0]*1e-13);dA=-(v[ok].T@((u[:,ok].T@r)/s[ok])).reshape(A.shape)
  e=np.linalg.norm(r);history.append(dict(i=i,residual=float(e),rank=int(ok.sum()),step=float(np.linalg.norm(dA))))
  if e<1e-10:break
  if np.linalg.norm(dA)>.02*np.linalg.norm(A):dA*=.02*np.linalg.norm(A)/np.linalg.norm(dA)
  for f in [1,.5,.25,.125,.0625]:
   B=A+f*dA
   if np.linalg.norm(res(B))<e:A=B;break
  else:break
 candidates['refit_intermediate']=A
 # Audit fixed-C transfer identity and Frobenius bound in extended precision.
 def frob(v):return float(np.linalg.norm(v))
 stats={}
 for k,A in candidates.items():
  rr=[];w0=wedge(A,M)
  for j,N in enumerate(mats):
   w=wedge(A,N);dx=w-w0;dm=N-M;rhs=wedge(A,dm);err=frob(dx-rhs);bound=np.linalg.norm(A,2)**2*np.linalg.norm(dm,'fro')
   rr.append(dict(matrix=labels[j],spin3_rel=frob(P3@w)/norm,spin1_target_rel=frob(P1@w-target)/norm,transfer_abs=frob(dx),transfer_identity_error=err,Frobenius_bound=float(bound),bound_holds=bool(frob(dx)*np.sqrt(2)<=bound+1e-15)))
  assert all(x['bound_holds'] for x in rr)
  stats[k]=dict(budget_rel=float(abs(np.sum(A*A)-budget)/budget),matrix_tests=rr,sensitivity=float(np.linalg.norm(np.asarray(P3,float)@jac(A,mats[-1]),2)*np.linalg.norm(A)/norm))
 diff=[]
 for j in range(1,len(mats)):
  prev=mats[j-1];N=mats[j];sp=np.linalg.svd(N,compute_uv=False)
  diff.append(dict(from_case=labels[j-1],to_case=labels[j],relative_matrix=float(np.linalg.norm(N-prev)/np.linalg.norm(N)),small_sv=sp[2:4].tolist(),small_sv_relative=float(abs(sp[2]-np.linalg.svd(prev,compute_uv=False)[2])/sp[2])))
 out=dict(labels=labels,delta_matrix=diff,target_norm=norm,budget=budget,refit_history=history,stats=stats,source_sha={str(p.relative_to(P)):sha(p) for p in [S/'envelope.py',S/'RADIAL_FINE.json',A4/'CONTROLS.npz']},scope='actual frozen-clock radial/time refinement; refit only intermediate; heldout finest, not native nonlinear cancellation proof')
 np.savez_compressed(D/'REFINED_CONTROLS.npz',labels=np.array(list(candidates)),A=np.array(list(candidates.values())),H=H)
 write('REFINEMENT.json',out);print(json.dumps(out),flush=True)
if __name__=='__main__':
 if sys.argv[1]=='matrix':run(int(sys.argv[2]),int(sys.argv[3]))
 else:analysis()

