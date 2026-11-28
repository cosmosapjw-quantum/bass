"""C4F robust empirical multi-matrix wedge and independent native 16384-step test."""
from pathlib import Path
import sys,json,numpy as np,hashlib,subprocess,concurrent.futures as cf,time
from scipy.optimize import least_squares
D=Path(__file__).resolve().parent;P=D.parent;E=P/'r118c4e_precision_refit'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
p=E/'bass.py';src=p.read_text();g={'__file__':str(p),'__name__':'prior'};exec(compile(src,str(p),'exec'),g)
H,Q,Cbase,P1,P3,vec,target,norm,budget=[g[k] for k in ['H','Q','Cbase','P1','P3','vec','target','norm','budget']]
z=np.load(E/'CONTROLS.npz');x0=(z['A_new']@np.linalg.inv(Q.T)).copy();ma=z['M192'];mb=z['M256'];mm=(ma+mb)/2;dm=(ma-mb)/2
assert np.array_equal(Q,z['Q']) and np.array_equal(z['target'],target) and np.array_equal(np.load(E/'basis_192.npz')['C'],Cbase)
def W(x,m):
 x=x.reshape(5,7).astype(np.longdouble);return vec(x@m@x.T)
def J(x,m):
 x=x.reshape(5,7).astype(np.longdouble);return np.array([vec(v@m@x.T+x@m@v.T) for v in np.eye(35,dtype=np.longdouble).reshape(35,5,7)]).T
def stat(x,m):
 w=W(x,m);return dict(spin3=float(np.linalg.norm(P3@w)/norm),spin1=float(np.linalg.norm(P1@w-target)/norm))
def budget_rel(x):return float((np.sum((x.reshape(5,7)@Q.T)**2)-budget)/budget)
def control(x):return (x.reshape(5,7).astype(np.longdouble)@Cbase).astype(float)
def feasible(x):
 return abs(budget_rel(x))<1e-7 and max(stat(x,m)['spin1'] for m in [ma,mb])<1e-5 and max(np.linalg.norm(control(x),axis=0))*.04<.099
def fit():
 # Both mean and difference are well-resolved independently in the extended-precision temporal coordinates.
 a=x0.ravel();rows=[];candidates={'C4E':a.copy()}
 for wt in [0.,1.,10.,100.,1000.,10000.]:
  def f(x):return np.r_[np.array((W(x,mm)-target)/norm,float),wt*np.array(P3@W(x,dm)/norm,float),budget_rel(x),1e-7*(x-a)/np.linalg.norm(a)]
  def jac(x):return np.vstack([np.array(J(x,mm)/norm,float),wt*np.array(P3@J(x,dm)/norm,float),2*(x.reshape(5,7)@Q.T@Q).ravel()/budget,1e-7*np.eye(35)/np.linalg.norm(a)])
  # Rank-aware small Newton steps; retain both objective and feasibility.
  x=a.copy();hist=[]
  for i in range(24):
   r=f(x);j=jac(x);u,s,v=np.linalg.svd(j,full_matrices=False);ok=s>max(s[0]*1e-14,1e-11);dx=-(v[ok].T@((u[:,ok].T@r)/s[ok]));e=float(np.linalg.norm(r));hist.append(dict(i=i,residual=e,rank=int(sum(ok)),step=float(np.linalg.norm(dx))))
   if np.linalg.norm(dx)<1e-15*np.linalg.norm(a):break
   cap=.003*np.linalg.norm(a)
   if np.linalg.norm(dx)>cap:dx*=cap/np.linalg.norm(dx)
   if np.linalg.norm(x-a)>0.03*np.linalg.norm(a):break
   for step in [1,.5,.25,.125,.0625,.03125,.015625]:
    if np.linalg.norm(f(x+step*dx))<e:x+=step*dx;break
   else:break
  label=f'joint_{wt:g}';candidates[label]=x;rows.append(dict(label=label,weight=wt,iterations=hist))
 data={k:dict(train=[stat(x,m) for m in [ma,mb]],budget_relative=abs(budget_rel(x)),displacement_relative=float(np.linalg.norm(x-a)/np.linalg.norm(a)),peak=float(max(np.linalg.norm(control(x),axis=0))),feasible=bool(feasible(x))) for k,x in candidates.items()}
 selected=min([k for k,x in candidates.items() if feasible(x)],key=lambda k:max(v['spin3'] for v in data[k]['train']))
 best=candidates[selected];assert feasible(best)
 np.savez_compressed(D/'TRAIN_CONTROLS.npz',labels=np.array(list(candidates)),coordinates=np.array(list(candidates.values())).reshape(-1,5,7),selected=np.array(selected),control_old=z['control_new'],control_new=control(best),target=target,Q=Q)
 write('TRAIN_SELECTION.json',dict(selected=selected,records=data,iterations=rows,prior_controls_sha=sha(E/'CONTROLS.npz'),training_only=True,scope='finite empirical M192, M256; convex combinations bounded, no extrapolation or global optimum'))
 print('train',selected,data,flush=True)
def heldout():
 b=np.load(D/'TRAIN_CONTROLS.npz');x=b['coordinates'][list(b['labels']).index(str(b['selected']))];ctrl=b['control_new'];old=b['control_old']
 # 320 radial independent, both temporal and actual physical coordinates. Time refinement also held out.
 def run(q):
  label,C,sub=q;M,r=g['ns']['integrate_general']('mld',320,sub,C);r.update(label=label);np.savez_compressed(D/(label+'.npz'),M=M,C=C);write(label+'.json',r);print(label,r,flush=True);return M
 with cf.ThreadPoolExecutor(max_workers=3) as ex:res=list(ex.map(run,[('basis320',Cbase,16),('old320',old,16),('new320',ctrl,16)]))
 m,wo,wn=res;J0,W0,ident=g['ns']['harmonic']();pred=W(x,m);rows={}
 for k,w in [('old',vec(wo)),('new',vec(wn)),('predicted_new',pred)]:
  rows[k]=dict(spin3=float(np.linalg.norm(P3@w)/norm),spin1=float(np.linalg.norm(P1@w-target)/norm),B2_norm=float(np.linalg.norm(W0.astype(np.clongdouble)@w)))
 rows['direct_vs_prediction']=float(np.linalg.norm(vec(wn)-pred)/norm)
 out=dict(selected=str(b['selected']),radial=320,early_subdivisions=16,rows=rows,harmonic=ident,scope='independent actual physical DP5 propagation and untrained radial basis, same exact clock mesh')
 write('HELDOUT.json',out);print(out,flush=True)
def native():
 b=np.load(D/'TRAIN_CONTROLS.npz');binary=D.parents[1]/'_rustcore/target/release/examples/c3x_radial';want=json.loads((P/'r118c3x_native_coefficients/ops/BUILD_ID.json').read_text())['binary']['sha256'];assert sha(binary)==want
 clock=P/'r118c3l_reachable_sky/clock.csv';cases=[('zero',0.)]+[(k,e) for k in ['old','new'] for e in [-.01,.01,-.02,.02,-.04,.04]]
 def job(q):
  k,e=q;tag=f'{k}_{e:g}_16384';ctrl=b['control_old' if k=='old' else 'control_new'];np.savetxt(D/(tag+'.ctrl'),np.r_[[.001,.006,.05],(e*ctrl.T).ravel()][None],fmt='%.17e');t=time.monotonic()
  with (D/(tag+'.csv')).open('w') as f,(D/(tag+'.geom')).open('w') as z:r=subprocess.run([str(binary),str(clock),str(D/(tag+'.ctrl')),'16384','192','8','8'],stdout=f,stderr=z,timeout=280)
  assert r.returncode==0 and 'max_gauss=' in (D/(tag+'.geom')).read_text(),tag
  print('native',tag,flush=True);return dict(tag=tag,exit=r.returncode,seconds=time.monotonic()-t)
 with cf.ThreadPoolExecutor(max_workers=7) as ex:rows=list(ex.map(job,cases))
 def read(k,e):
  a=np.genfromtxt(D/f'{k}_{e:g}_16384.csv',names=True,delimiter=',');m=(a['epoch']==1)&(a['ell']==3);assert sum(m)==7;return a['Bre'][m]+1j*a['Bim'][m]
 zero=read('zero',0.);r=np.array([.01,.02,.04])**2;V=np.vander(r,3,increasing=True);out={}
 for k in ['old','new']:
  Y=np.array([(read(k,e)+read(k,-e)-2*zero)/(2*e*e) for e in [.01,.02,.04]]);f=np.linalg.solve(V,Y);two=(4*Y[0]-Y[1])/3
  out[k]=dict(B2=float(np.linalg.norm(f[0])),B4=float(np.linalg.norm(f[1])),B6=float(np.linalg.norm(f[2])),two_vs_three=float(np.linalg.norm(f[0]-two)),B2_re=f[0].real.tolist(),B2_im=f[0].imag.tolist())
 prior=json.loads((E/'NATIVE_REFINED.json').read_text())['results']['new'];dif=float(np.linalg.norm(np.array(out['old']['B2_re'])+1j*np.array(out['old']['B2_im'])-np.array(prior['B2_re'])-1j*np.array(prior['B2_im'])))
 write('NATIVE_16384.json',dict(rows=rows,binary_sha=want,clock_sha=sha(clock),results=out,prior_8192_new=prior,old_vs_8192_vector_abs=dif,scope='matched old/new 16384-step native, same 192 radial/angular/lmax8, three amplitudes; no exact quadratic coefficient'))
 print('NATIVE',out,'refinement',dif,flush=True)
if __name__=='__main__':{'fit':fit,'heldout':heldout,'native':native}[sys.argv[1]]()
