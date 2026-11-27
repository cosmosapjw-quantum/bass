"""C4A fixed wedge, budget and transfer/sensitivity diagnostics; native finite test."""
from pathlib import Path
import numpy as np,json,hashlib,subprocess,sys,time,concurrent.futures as cf
from scipy.linalg import schur,null_space
from scipy.optimize import least_squares
from itertools import combinations,permutations
D=Path(__file__).resolve().parent;P=D.parent;Y=P/'r118c3z_spin_projector_mc';X=P/'r118c3x_native_coefficients';L=P/'r118c3l_reachable_sky';U=P/'r118c3u_exact_wedge';S=P/'r118c3s_radial_envelope';R=D.parents[1]
def write(n,x):(D/n).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pairs=np.array(list(combinations(range(5),2)));ii,jj=pairs.T
def vec(W):return W[ii,jj]
def skew(v):
 W=np.zeros((5,5));W[ii,jj]=v;W[jj,ii]=-v;return W
B=np.zeros((5,3,3));B[0]=np.diag([1,-1,0])/np.sqrt(2);B[1]=np.diag([-1,-1,2])/np.sqrt(6)
for k,(i,j) in enumerate([(0,1),(0,2),(1,2)],2):B[k,i,j]=B[k,j,i]=1/np.sqrt(2)
C=np.stack([(B[i]@B[j]-B[j]@B[i])[[0,0,1],[1,2,2]] for i,j in pairs],axis=1);P1=C.T@np.linalg.solve(C@C.T,C);P3=np.eye(10)-P1
P3L=P3.astype(np.longdouble);P1L=P1.astype(np.longdouble)
def blocks(M):
 T,U=schur(np.array(M,float),output='real');b=[];i=0
 while i<len(M)-1:
  if T[i+1,i]!=0.:
   b.append((i,float(T[i,i+1])));i+=2
  else:i+=1
 b=sorted(b,key=lambda r:-abs(r[1]));return U,b
def wedge(A,M):
 A=A.astype(np.longdouble);M=M.astype(np.longdouble);return vec(A@M@A.T)
def jac(A,M):
 return np.column_stack([vec(E@M@A.T+A@M@E.T) for E in np.eye(A.size).reshape(A.size,*A.shape)])
def run():
 f=json.loads((S/'RADIAL_FINE.json').read_text());H=np.array(f['H']);M=np.array(f['M']);z=np.load(U/'best_selected_4096.npz');A0=z['A'];assert np.array_equal(A0@H,z['control'])
 budget=np.sum(A0*A0);w=wedge(A0,M);tar=P1L@w;norm=float(np.linalg.norm(tar));T=skew(np.array(tar,float));V,wb=blocks(T);wb=wb[:2];assert len(wb)==2
 rows=[f]+[r for r in json.loads((S/'R7.json').read_text())['rows'] if r['nw']==2]
 mats=[];labels=[]
 for r in rows:
  Hj=np.array(r['H']);Q=H@np.linalg.inv(Hj);m=Q@np.array(r['M'])@Q.T;m=(m-m.T)/2;mats.append(m);labels.append(f"{r['nr']}_{r['nt']}")
 def stats(A):
  W=wedge(A,M);s=np.linalg.svd(P3@jac(A,M),compute_uv=False);C0=A@H
  peak=max(np.linalg.norm(C0[:,1+2*j:3+2*j],axis=0).max() for j in range(3))
  return dict(budget_rel=float(abs(np.sum(A*A)-budget)/budget),target_spin1_rel=float(np.linalg.norm(P1L@W-tar)/norm),spin3_rel=float(np.linalg.norm(P3L@W)/norm),sensitivity=float(s[0]*np.linalg.norm(A)/norm),sensitivity_small=float(s[6]*np.linalg.norm(A)/norm),peak_control=float(peak),initial_shear_control=float(np.linalg.norm(C0[:,0])),transfer={l:{'spin3_relative_to_target':float(np.linalg.norm(P3L@wedge(A,m))/norm),'spin1_relative_to_target':float(np.linalg.norm(P1L@wedge(A,m)-tar)/norm)} for l,m in zip(labels,mats)})
 cand={'baseline':A0};records={}
 # Canonical balanced 2-plane congruence, exact kernel fill.
 for mi,MM in enumerate(mats):
  Q,mb=blocks(MM);mb=mb[:2]
  if len(mb)!=2:continue
  null=null_space(MM,rcond=1e-19)
  # Choose smallest singular direction (odd-dimensional exact kernel; numeric residual retained).
  _,_,vv=np.linalg.svd(MM);k=vv[-1];k-=Q[:,[mb[0][0],mb[0][0]+1,mb[1][0],mb[1][0]+1]]@(Q[:,[mb[0][0],mb[0][0]+1,mb[1][0],mb[1][0]+1]].T@k);k/=np.linalg.norm(k)
  for perm in permutations(range(2)):
   label=f'canon_{labels[mi]}_{perm[0]}{perm[1]}';A=np.zeros_like(A0)
   for j,idx in enumerate(perm):
    a,m=mb[idx];b,ww=wb[j];d=np.sqrt(abs(ww/m));A+=V[:,b:b+2]@np.diag([np.sign(ww/m)*d,d])@Q[:,a:a+2].T
   req=float(np.sum(A*A))
   if req>budget*(1+1e-10):
    records[label]=dict(infeasible_budget_ratio=req/budget);continue
   if req<budget:
    u=A0@k
    if np.linalg.norm(u)<1e-14:u=V[:,wb[0][0]]
    A+=np.sqrt(max(0,budget-req))*np.outer(u/np.linalg.norm(u),k)
   cand[label]=A;records[label]=dict(required_budget_fraction=req/budget,kernel_residual=float(np.linalg.norm(MM@k)))
 # Local high-precision constrained Newton: solve 10 wedge coordinates and budget, with trust radius and line search.
 # Minimize residual to exact W1 at reference, preserve baseline local branch.
 A=A0.copy();hist=[]
 for step in range(12):
  residual=np.r_[np.array((wedge(A,M)-tar)/norm,float),(np.sum(A*A)-budget)/budget]
  J=np.vstack([jac(A,M)/norm,2*A.ravel()/budget]);u,s,v=np.linalg.svd(J,full_matrices=False)
  good=s>max(s[0]*1e-13,1e-12);dA=-(v[good].T@((u[:,good].T@residual)/s[good])).reshape(A.shape)
  n=np.linalg.norm(residual);hist.append(dict(step=step,residual=float(n),rank=int(good.sum()),step_norm=float(np.linalg.norm(dA))))
  if n<1e-10:break
  if np.linalg.norm(dA)>.05*np.linalg.norm(A):dA*=.05*np.linalg.norm(A)/np.linalg.norm(dA)
  def res(B):return np.linalg.norm(np.r_[np.array((wedge(B,M)-tar)/norm,float),(np.sum(B*B)-budget)/budget])
  for f0 in [1.,.5,.25,.125,.0625,.03125]:
   Q=A+f0*dA
   if res(Q)<n:A=Q;break
  else:break
 cand['local_newton']=A;records['local_newton']=dict(iterations=hist)
 # Additional robust least-squares across measured M; fine W1 and fixed budget maintained at 1e-5 gates.
 # Solve using truncated SVD / scaled residual, small-step regularization. Keep candidates even if rejected.
 for weight in [.01,.1,1.]:
  A0c=cand['local_newton'];x0=A0c.ravel()
  def residual(x):
   A=x.reshape(A0.shape);fine=np.array((wedge(A,M)-tar)/norm,float);other=[weight*np.array(P3L@wedge(A,m)/norm,float) for m in mats[1:]]
   return np.r_[fine,(np.sum(A*A)-budget)/budget,*other,1e-3*(x-x0)/np.linalg.norm(A0)]
  def deriv(x):
   A=x.reshape(A0.shape);return np.vstack([jac(A,M)/norm,2*A.ravel()/budget,*[weight*P3@jac(A,m)/norm for m in mats[1:]],1e-3*np.eye(A.size)/np.linalg.norm(A0)])
  z=least_squares(residual,x0,jac=deriv,max_nfev=250,ftol=1e-11,xtol=1e-12,gtol=1e-10,x_scale='jac')
  label=f'robust_{weight:g}';cand[label]=z.x.reshape(A0.shape);records[label]=dict(nfev=int(z.nfev),status=int(z.status),cost=float(z.cost),displacement=float(np.linalg.norm(z.x-x0)))
 for k,A in cand.items():records.setdefault(k,{}).update(stats(A))
 eligible=[k for k in cand if records[k]['budget_rel']<1e-7 and records[k]['target_spin1_rel']<1e-5 and records[k]['peak_control']*.04<.099 and records[k]['initial_shear_control']*.04<.099]
 assert 'baseline' in eligible
 def score(k):
  r=records[k];return max(r['spin3_rel'],max(a['spin3_relative_to_target'] for a in r['transfer'].values()))+1e-8*r['sensitivity']
 best=min(eligible,key=score);best_fine=min(eligible,key=lambda k:records[k]['spin3_rel'])
 # use best fine if robust winner is baseline, but do not claim robust win.
 chosen=best if best!='baseline' else best_fine
 np.savez_compressed(D/'CONTROLS.npz',labels=np.array(list(cand)),A=np.array(list(cand.values())),H=H,target=np.array(tar,float),selected=cand[chosen]@H,chosen=chosen)
 out=dict(target_norm=norm,budget=float(budget),temporal_cases=labels,records=records,eligible=eligible,robust_winner=best,fine_winner=best_fine,native_selected=chosen,robust_score={k:score(k) for k in eligible},scope='finite actual matrices; canonical and local constrained candidates only, physical native verification separate; not global optimum')
 write('ROBUST.json',out);print({k:dict(spin3=records[k].get('spin3_rel'),sensitivity=records[k].get('sensitivity'),budget=records[k].get('budget_rel'),target=records[k].get('target_spin1_rel')) for k in records},'selected',chosen,flush=True)
def native():
 q=np.load(D/'CONTROLS.npz');tag=str(q['chosen']);control=q['selected'];binary=R/'_rustcore/target/release/examples/c3x_radial';assert sha(binary)==json.loads((X/'ops/BUILD_ID.json').read_text())['binary']['sha256']
 def job(e):
  n=4096;nm=f'candidate_{e:g}_{n}';np.savetxt(D/(nm+'.ctrl'),np.r_[[.001,.006,.05],(e*control.T).ravel()][None],fmt='%.17e');t=time.monotonic()
  with (D/(nm+'.csv')).open('w') as f,(D/(nm+'.geom')).open('w') as g:z=subprocess.run([str(binary),str(L/'clock.csv'),str(D/(nm+'.ctrl')),str(n),'192','8','8'],stdout=f,stderr=g,timeout=200)
  assert z.returncode==0 and 'max_gauss=' in (D/(nm+'.geom')).read_text(),nm
  return dict(e=e,exit=z.returncode,seconds=time.monotonic()-t)
 with cf.ThreadPoolExecutor(max_workers=2) as ex:rows=list(ex.map(job,[-.02,.02,-.04,.04]))
 def read(path):
  a=np.genfromtxt(path,names=True,delimiter=',');assert len(a)==162
  m=(a['epoch']==1)&np.isin(a['ell'],[3,5,7]);return a['Bre'][m]+1j*a['Bim'][m]
 z=read(P/'r118c3y_signed_coefficients/base_0_4096_192_8.csv') if (P/'r118c3y_signed_coefficients/base_0_4096_192_8.csv').exists() else read(P/'r118c3w_harmonic_collision/base_0_4096_192_8.csv')
 vals={}
 for t in ['candidate','baseline']:
  A=[];O=[]
  for e in [.02,.04]:
   if t=='candidate':p,m=[read(D/f'candidate_{v:g}_4096.csv') for v in [e,-e]]
   else:
    def prior(v):
     for root in [X,P/'r118c3w_harmonic_collision',P/'r118c3y_signed_coefficients']:
      f=root/f'best_{v:g}_4096_192_8.csv'
      if f.exists():return read(f)
     raise FileNotFoundError(str(v))
    p,m=prior(e),prior(-e)
   A.append((p+m-2*z)/(2*e**2));O.append((p-m)/(2*e))
  B2=(4*A[0]-A[1])/3;B4=(A[1]-A[0])/(.04**2-.02**2)
  vals[t]=dict(even_norm=[float(np.linalg.norm(x[:7])) for x in A],odd_norm=[float(np.linalg.norm(x[:7])) for x in O],B2_two_amplitude=float(np.linalg.norm(B2[:7])),B4_two_amplitude=float(np.linalg.norm(B4[:7])))
 write('NATIVE.json',dict(rows=rows,selected=tag,binary_sha=sha(binary),results=vals,scope='two amplitudes; B2 estimate contaminated by B6 and higher; same prior zero at nt4096, fixed radial/angular/lmax8'))
 print(vals,flush=True)
if __name__=='__main__':{'robust':run,'native':native}[sys.argv[1]]()

