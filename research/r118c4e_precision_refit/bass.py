"""C4E exact C4D DP5 source reused for general control-basis wedge; high precision refit and native verification."""
from pathlib import Path
import numpy as np,sys,json,hashlib,subprocess,concurrent.futures as cf,time
from scipy.linalg import schur
from itertools import combinations
D=Path(__file__).resolve().parent;P=D.parent;R=D.parents[1];C4=P/'r118c4d_precision_jet';A4=P/'r118c4a_robust_wedge';B=P/'r118c4b_temporal_mask';C3=P/'r118c4c_conditioned_transfer';S=P/'r118c3s_radial_envelope';X=P/'r118c3x_native_coefficients';L=P/'r118c3l_reachable_sky'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
src=(C4/'bass.py').read_text()
ns={'__file__':str(C4/'bass.py'),'__name__':'c4d_owner'};exec(compile(src,str(C4/'bass.py'),'exec'),ns)
H=ns['H'];A=ns['A'];P1=ns['P1'];P3=ns['P3'];wedge=ns['wedge'];vec=ns['vec'];Z=ns['Z']
old=json.loads((B/'M_256_3072.json').read_text());T=H@np.linalg.inv(np.array(old['H']));M0=T@np.array(old['M'])@T.T;_,Q=schur((M0-M0.T)/2,output='real')
# Use exact inverse of numerically orthogonal Q for the physical-coordinate map, not assume exact orthogonality.
Qinv=np.linalg.inv(Q);Cbase=Q.T.astype(np.longdouble)@H.astype(np.longdouble);Aq=A@np.linalg.inv(Q.T)
target=P1@wedge(Z['A'][list(Z['labels']).index('baseline')],np.array(json.loads((S/'RADIAL_FINE.json').read_text())['M']));norm=float(np.linalg.norm(target));budget=float(np.sum(A*A))
# Generate only a general-n wedge integrator from C4D; same clocks, DP5 coefficients and radial physics.
body=src[src.index('def integrate('):src.index('\ndef jet(')]
def rep(a,b):
 global body
 assert body.count(a)==1,(a,body.count(a));body=body.replace(a,b)
rep('def integrate(kind,nr,sub):','def integrate_general(kind,nr,sub,Cmat):')
rep('J,W,ident=harmonic();Jr=np.concatenate([J.real,J.imag],axis=1).astype(dtype)','n=len(Cmat);ii,jj=np.array(list(combinations(range(n),2))).T;nw=len(ii)')
rep('C=control.T.astype(dtype)','C=Cmat.T.astype(dtype)')
rep('src=C[1:].reshape(3,2,5)','src=C[1:].reshape(3,2,n)')
rep('s,b,I,P=z[:20].reshape(4,5);ww=z[20:30];bb=z[30:]','s,b,I,P=z[:4*n].reshape(4,n);ww=z[4*n:]')
rep("  bs=np.einsum('kij,i,j->k',Jr[0],s,I)+np.einsum('kij,i,j->k',Jr[1],s,P)\n","")
rep(',bs-k*bb]',']')
rep('z=np.zeros(44,dtype=dtype);z[:5]=C[0]','z=np.zeros(4*n+nw,dtype=dtype);z[:n]=C[0]')
body=body[:body.index(' w0=z[20:30]')]+""" M=np.zeros((n,n),dtype=dtype);M[ii,jj]=z[4*n:];M[jj,ii]=-z[4*n:]
 return M,dict(n=n,nr=nr,sub=sub,steps=nstep,mesh_sha=mesh_sha,mantissa=np.finfo(dtype).nmant,seconds=time.monotonic()-start)
"""
ns['combinations']=combinations;exec(compile(body,'C4D_general_wedge','exec'),ns)
def calc(tag,nr,C):
 M,r=ns['integrate_general']('mld',nr,16,C);r['tag']=tag;r['source_sha256']=sha(C4/'bass.py');r['sv']=np.linalg.svd(M.astype(float),compute_uv=False).tolist();np.savez_compressed(D/(tag+'.npz'),M=M,C=C,Q=Q);write(tag+'.json',r);print(tag,r,flush=True);return M
def fit():
 with cf.ThreadPoolExecutor(max_workers=2) as ex:
  ma,mb=list(ex.map(lambda nr:calc(f'basis_{nr}',nr,Cbase),[192,256]))
 T=ma;C=Aq.copy()
 def get(C,M):
  a=C.astype(np.longdouble);return vec(a@M@a.T)
 def f(C):return np.r_[np.array((get(C,T)-target)/norm,float),(np.sum((C@Q.T)**2)-budget)/budget]
 def deriv(C):
  v=[];a=C.astype(np.longdouble)
  for e in np.eye(C.size).reshape(C.size,*C.shape):
   b=e.astype(np.longdouble);v.append(np.r_[np.array(vec(b@T@a.T+a@T@b.T)/norm,float),2*np.sum((C@Q.T)*(e@Q.T))/budget])
  return np.array(v).T
 hist=[]
 for i in range(20):
  r=f(C);j=deriv(C);u,s,v=np.linalg.svd(j,full_matrices=False);ok=s>max(s[0]*1e-14,1e-12);dc=-(v[ok].T@((u[:,ok].T@r)/s[ok])).reshape(C.shape);e=np.linalg.norm(r);hist.append(dict(i=i,residual=float(e),rank=int(sum(ok)),step=float(np.linalg.norm(dc))))
  if e<1e-11:break
  if np.linalg.norm(dc)>.03*np.linalg.norm(C):dc*=.03*np.linalg.norm(C)/np.linalg.norm(dc)
  for a in [1.,.5,.25,.125,.0625,.03125]:
   if np.linalg.norm(f(C+a*dc))<e:C=C+a*dc;break
  else:break
 Anew=C@Q.T;ctrl=(C.astype(np.longdouble)@Cbase).astype(float)
 assert np.linalg.norm(ctrl-Anew@H)/np.linalg.norm(ctrl)<1e-12
 def stats(c):
  return [dict(spin3_relative=float(np.linalg.norm(P3@get(c,m))/norm),spin1_error=float(np.linalg.norm(P1@get(c,m)-target)/norm)) for m in [ma,mb]]
 oldstat=stats(Aq);newstat=stats(C);bud=abs(np.sum(Anew*Anew)-budget)/budget
 assert bud<1e-7 and newstat[0]['spin1_error']<1e-5
 assert max(np.linalg.norm(ctrl,axis=0))*.04<.099
 np.savez_compressed(D/'CONTROLS.npz',A_old=A,A_new=Anew,Q=Q,control_old=A@H,control_new=ctrl,target=target,M192=ma,M256=mb)
 write('REFIT.json',dict(history=hist,old=oldstat,new=newstat,budget_relative=float(bud),control_relative_change=float(np.linalg.norm(ctrl-A@H)/np.linalg.norm(A@H)),peak=float(max(np.linalg.norm(ctrl,axis=0))),fit_grid=192,heldout_grid=256,source_sha256=sha(C4/'bass.py'),scope='actual extended precision temporal basis, local minimum-norm fit; independent direct control propagation separate'))
 with cf.ThreadPoolExecutor(max_workers=2) as ex:
  ds=list(ex.map(lambda nr:calc(f'direct_refit_{nr}',nr,ctrl),[192,256]))
 J,W,ident=ns['harmonic']();rows=[]
 for nr,m,t in zip([192,256],ds,[ma,mb]):
  w=vec(m);pred=get(C,t)
  rows.append(dict(nr=nr,spin3_relative=float(np.linalg.norm(P3@w)/norm),spin1_error=float(np.linalg.norm(P1@w-target)/norm),direct_vs_congruence_relative=float(np.linalg.norm(w-pred)/norm),B2_norm=float(np.linalg.norm(W.astype(np.clongdouble)@w)),B2_pred_norm=float(np.linalg.norm(W.astype(np.clongdouble)@pred))))
 write('DIRECT_REFIT.json',dict(rows=rows,scope='independently integrated physical float64 control with extended precision DP5; not exact continuum',harmonic=ident));print('REFIT',newstat,rows,flush=True)
def native():
 z=np.load(D/'CONTROLS.npz');binary=R/'_rustcore/target/release/examples/c3x_radial';want=json.loads((X/'ops/BUILD_ID.json').read_text())['binary']['sha256'];assert sha(binary)==want
 cases=[('zero',0.)]+[(k,e) for k in ['old','new'] for e in [-.01,.01,-.02,.02,-.04,.04]]
 def job(q):
  name,e=q;tag=f'{name}_{e:g}_8192';control=z['control_old' if name=='old' else 'control_new'];np.savetxt(D/(tag+'.ctrl'),np.r_[[.001,.006,.05],(e*control.T).ravel()][None],fmt='%.17e');t=time.monotonic()
  with (D/(tag+'.csv')).open('w') as f,(D/(tag+'.geom')).open('w') as g:r=subprocess.run([str(binary),str(L/'clock.csv'),str(D/(tag+'.ctrl')),'8192','192','8','8'],stdout=f,stderr=g,timeout=180)
  assert r.returncode==0 and 'max_gauss=' in (D/(tag+'.geom')).read_text(),tag
  print('native',tag,'ok',flush=True);return dict(tag=tag,exit=r.returncode,seconds=time.monotonic()-t)
 with cf.ThreadPoolExecutor(max_workers=4) as ex:rows=list(ex.map(job,cases))
 def read(k,e):
  a=np.genfromtxt(D/f'{k}_{e:g}_8192.csv',names=True,delimiter=',');m=(a['epoch']==1)&(a['ell']==3);assert sum(m)==7;return a['Bre'][m]+1j*a['Bim'][m]
 zero=read('zero',0.);r=np.array([.01,.02,.04])**2;V=np.vander(r,3,increasing=True);out={}
 for name in ['old','new']:
  Y=np.array([(read(name,e)+read(name,-e)-2*zero)/(2*e*e) for e in [.01,.02,.04]]);fit=np.linalg.solve(V,Y);two=(4*Y[0]-Y[1])/3
  out[name]=dict(B2=float(np.linalg.norm(fit[0])),B4=float(np.linalg.norm(fit[1])),B6=float(np.linalg.norm(fit[2])),B2_re=fit[0].real.tolist(),B2_im=fit[0].imag.tolist(),two_vs_three=float(np.linalg.norm(fit[0]-two)),even_norm=np.linalg.norm(Y,axis=1).tolist())
 write('NATIVE_REFINED.json',dict(rows=rows,binary_sha256=want,results=out,prior_4096=json.loads((C3/'NATIVE.json').read_text())['results']['candidate'],scope='same 8192/192/8/8 native grid, fresh zero, three-amplitude B2 extraction; remainder and native floor persist'));print(out,flush=True)
if __name__=='__main__':{'fit':fit,'native':native}[sys.argv[1]]()
