"""Signed native coefficient extraction; never fit norms.
C3W exact binary reused, l=3 magnetic complex vector. Coefficients index perturbation order.
"""
import numpy as np,json,re
from pathlib import Path
D=Path(__file__).resolve().parent;W=D.parent/'r118c3w_harmonic_collision'
def path(tag,ep,nt,nr=192,nm=8,l=8):
 f=f'{tag}_{ep:g}_{nt}_{nr}_{nm}'+('' if l==8 else f'_l{l}')
 for p in [D,W]:
  q=p/(f+'.csv');g=p/(f+'.geom')
  if q.is_file() and g.is_file() and 'max_gauss=' in g.read_text():
   return q,g
 raise FileNotFoundError(f)
def load(tag,ep,nt,nr=192,nm=8,l=8):
 q,g=path(tag,ep,nt,nr,nm,l);x=np.genfromtxt(q,names=True,delimiter=',');assert len(x)==2*(l+1)**2
 m=(x['epoch']==1)&(x['ell']==3);assert np.sum(m)==7 and np.isfinite(x.view(float)).all()
 return x['Bre'][m]+1j*x['Bim'][m]
def pair(tag,e,n,nr=192,nm=8,l=8):
 # Existing zero control at the same time resolution; if unavailable,
 # use exact-isotropy B=0, record the known prior numerical floor separately.
 p=load(tag,e,n,nr,nm,l);m=load(tag,-e,n,nr,nm,l)
 try:z=load('base',0.,n,nr,nm,l)
 except FileNotFoundError:z=np.zeros_like(p)
 return np.stack([((p+m)/2-z)/e**2,(p-m)/2/e**3])
def fit(tag,n,es,degree):
 y=np.array([pair(tag,e,n) for e in es]);s=max(es)**2;x=np.array(es)**2/s
 A=np.vander(x,degree+1,increasing=True);b=np.linalg.lstsq(A,y.reshape(len(es),-1),rcond=None)[0].reshape(degree+1,2,7)/s**np.arange(degree+1)[:,None,None]
 return b,float(np.linalg.cond(A))
def metrics(b,J):
 # complex vector coefficient order2,3,4,5. B2 cancellation absolute.
 a=np.array([b[0,0],b[0,1],b[1,0],b[1,1]])
 norm=np.linalg.norm(a,axis=1);err=np.linalg.norm(a-J,axis=1);jn=np.linalg.norm(J,axis=1)
 return dict(norm=norm.tolist(),abs_error=err.tolist(),relative_3_to_5=(err[1:]/jn[1:]).tolist())
def run():
 out={};allcoef={}
 for tag in ['pred','best']:
  J=np.load(D.parent/'r118c3t_radial_null'/'best_4096.npz' if tag=='pred' else D.parent/'r118c3u_exact_wedge'/'best_selected_4096.npz')['B'][1:5,9:16]
  rows={};co={}
  for nt in [2048,4096,8192]:
   try:b,cond=fit(tag,nt,[.02,.04,.06],2)
   except FileNotFoundError:continue
   lin,_=fit(tag,nt,[.02,.04],1);rows[str(nt)]=dict(**metrics(b,J),condition=cond,linear_quadratic_difference=metrics(lin,np.array([b[0,0],b[0,1],b[1,0],b[1,1]])),higher_norm=np.linalg.norm(b[2],axis=1).tolist());co[nt]=b
   if nt==4096:
    held={}
    for ep in [.01,.03]:
     try:y=pair(tag,ep,nt)
     except FileNotFoundError:continue
     pred=sum(b[k]*ep**(2*k) for k in range(3));held[str(ep)]=(np.linalg.norm(y-pred,axis=1)/np.linalg.norm(y,axis=1)).tolist()
    rows[str(nt)]['heldout_relative']=held
    try:f,_=fit(tag,nt,[.01,.02,.03,.04,.06],3);rows[str(nt)]['cubic_fit']=metrics(f,J);allcoef[tag+'_cubic4096']=f
    except FileNotFoundError:pass
   allcoef[f'{tag}_{nt}']=b
  for n in [2048,4096]:
   if n in co and 2*n in co:
    b=(4*co[2*n]-co[n])/3;rows[f'Richardson_{n}_{2*n}']=metrics(b,J);allcoef[f'{tag}_rich{n}']=b
  if all(n in co for n in [2048,4096,8192]):
   a0=co[2048]-co[4096];a1=co[4096]-co[8192]
   rows['time_ratio']=(np.linalg.norm(a0[:2],axis=2)/np.maximum(np.linalg.norm(a1[:2],axis=2),1e-300)).tolist()
  out[tag]=rows
 tests={}
 for nr,nm,l in [(256,8,8),(192,12,8),(192,8,10)]:
  try:a=pair('best',.04,4096,nr,nm,l);b=pair('best',.04,4096)
  except FileNotFoundError:continue
  tests[f'{nr}_{nm}_{l}']=(np.linalg.norm(a-b,axis=1)/np.linalg.norm(b,axis=1)).tolist()
 np.savez_compressed(D/'COEFFICIENTS.npz',**allcoef)
 result=dict(fits=out,independent_axes=tests,scope='signed complex native B_ell3 amplitude fit through perturbation orders 6/7, scaled Vandermonde, time Richardson diagnostic, prior C3W exact binary except lmax10 shadow. Zero missing at 8192 and lmax/radial/angular tests replaced by analytic zero; prior floor1.27e-34 not bound for all runs.')
 (D/'COEFFICIENTS.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':run()
