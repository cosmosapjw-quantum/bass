"""Positive source quadrature, NOT inversion/clipping of signed moments.
Uses the actual pinned REC full conditional COM-KHW integrand.
Frequency nodes reproduce source production rule (core/exterior separate).
Same-cell uses full direct regularized integrand, not inherited control variate.
"""
import argparse, pathlib, sys, json, math, hashlib, time, concurrent.futures
import numpy as np
from scipy.special import eval_legendre
P=pathlib.Path
p=argparse.ArgumentParser();p.add_argument('--rec',type=P,required=True);p.add_argument('--out',type=P,required=True);p.add_argument('--workers',type=int,default=4);p.add_argument('--only',default='');p.add_argument('--lane',choices=['production','reference','refined'],default='production')
args=p.parse_args();rec=args.rec.resolve();root=args.out.resolve();root.mkdir(parents=True,exist_ok=False)
if args.lane=='refined' and args.only!='same':raise ValueError('refined lane is same-cell only')
sys.path.insert(0,str(rec/'src'))
from full_bianchi_hyrec.recoil import pair_cell_conductance as PCC, exterior_interface as EX, same_cell_regular as SC
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import CollisionNetwork
owner=rec/'data/full_scalar_com_khw_v050.npz';net=CollisionNetwork.from_npz(owner)
factor=8*np.pi*PCC.dnu/PCC.c**3
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def angular(par):
 z,w=PCC.leggauss(par['ob']);c=.5*np.sqrt(.005)*(z+1);cw=.5*np.sqrt(.005)*w
 z,w=PCC.leggauss(par['om']);mu=.5*(.999+.99)*z+.5*(.999-.99);mw=.25*(.999+.99)*w
 z,w=PCC.leggauss(par['of']);t=.5*np.sqrt(.001)*(z+1);tw=.5*np.sqrt(.001)*w
 a=np.r_[-1+2*c*c,mu,1-t*t];b=np.r_[2*c*cw,mw,t*tw];return a,b
def uv_nodes(a,b,par,half):
 at,bt=a;as_,bs=b;lo=(at+as_)/2;hi=(bt+bs)/2;delta=PCC.gamma/PCC.dnu
 breaks=[lo,hi,(at+bs)/2,(bt+as_)/2]
 if lo<0<hi:breaks += [max(lo,-half),0,min(hi,half)]
 breaks=sorted(set(round(float(v),15) for v in breaks if lo-1e-14<=v<=hi+1e-14))
 U=[];W=[]
 for l,r in zip(breaks,breaks[1:]):
  if r-l<1e-14:continue
  if lo<0<hi and abs(l)<=half+1e-14 and abs(r)<=half+1e-14:
   z,w=PCC.leggauss(par['nl']);l1=np.arctan(l/delta);r1=np.arctan(r/delta);t=(l1+r1)/2+(r1-l1)*z/2
   u=delta*np.tan(t);ww=(r1-l1)*w/2*delta/np.cos(t)**2
  else:z,w=PCC.leggauss(par['nb']);u=(l+r)/2+(r-l)*z/2;ww=(r-l)*w/2
  U.extend(u);W.extend(ww)
 u=np.array(U)[:,None];w=np.array(W)[:,None];vmin=np.maximum(at-u,u-bs);vmax=np.minimum(bt-u,u-as_)
 z,wv=PCC.leggauss(par['nv']);v=(vmin+vmax)/2+(vmax-vmin)*z/2
 ww=2*w*(vmax-vmin)/2*wv
 assert np.all(ww>=0)
 return (PCC.nu_abs+PCC.dnu*(u+v)).ravel(),(PCC.nu_abs+PCC.dnu*(u-v)).ravel(),ww.ravel()
def tensor_nodes(a,b,n):
 z,w=PCC.leggauss(n)
 def get(a):return PCC.nu_abs+PCC.dnu*((a[0]+a[1])/2+(a[1]-a[0])*z/2),(a[1]-a[0])*w/2
 nt,wt=get(a);ns,ws=get(b);return np.broadcast_to(nt[:,None],(n,n)).ravel(),np.broadcast_to(ns[None,:],(n,n)).ravel(),(wt[:,None]*ws[None,:]).ravel()
def density(nt,ns,mu):
 # Source owner uses its exact positive conditional squared amplitude.
 v=PCC.const_exact*np.exp(-PCC.beta*PCC.h*ns+PCC.logSmj(ns,nt,mu))*ns*nt*PCC.exact_amp2(ns,nt,mu,amplitude_lane='full')
 if np.any(~np.isfinite(v)) or np.any(v<0):raise ValueError('source integrand not positive finite')
 return v
def batch_eval(mu,nodes):
 nt,ns,w=nodes;res=[]
 for start in range(0,len(mu),8):
  m=mu[start:start+8,None];v=density(nt[None,:],ns[None,:],m)
  res.extend(v@w)
 return np.asarray(res)
def job(ij):
 i,j=ij;t=time.monotonic()
 if i==j:
  par=SC.PRODUCTION_LANE if args.lane=='production' else SC.REFERENCE_LANE if args.lane=='reference' else dict(ob=36,om=320,of=80,nu=64,nu_pole=160,ny=72,ymax=12.)
  mu,w=angular(par);u,wu=SC._u_rule(i,par['nu'],par['nu_pole']);y,wy=PCC.leggauss(par['ny'])
  vals=[];a,b=net.state_intervals[i];half=np.minimum(u-a,b-u)[None,:,None]
  for start in range(0,len(mu),8):
   m=mu[start:start+8,None,None];s=np.sqrt((1-m)/2);ym=np.minimum(par['ymax'],half/s)
   v=s*ym*y[None,None,:];nt=PCC.nu_abs+PCC.dnu*(u[None,:,None]+v);ns=PCC.nu_abs+PCC.dnu*(u[None,:,None]-v)
   ww=2*s*wu[None,:,None]*ym*wy[None,None,:]
   vals.extend(np.sum(density(nt,ns,m)*ww,axis=(1,2)))
  # Retain regularized transport measure r=(1-mu)*K/pi, rates s^-1.
  k=factor*np.asarray(vals)*.75*(1+mu**2)/net.equilibrium_weight[i]
  q=(1-mu)*k
  ref=net.same_cell_rates[:,i]
  mom=np.array([np.sum(w*k*(eval_legendre(l,mu)-1)) for l in range(25)])
  typ='same_regularized'
 else:
  core=j<17
  par=(PCC.PRODUCTION_LANE if args.lane=='production' else PCC.REFERENCE_LANE) if core else EX.LANES[args.lane]
  mu,w=angular(par)
  a,b=(net.state_intervals[i],net.state_intervals[j]) if core else (net.state_intervals[j],net.state_intervals[i])
  use_uv=np.arange(len(mu))<par['ob']
  if not core:
   use_uv |= EX._crosses_resonance_mean(tuple(a),tuple(b)) | ((mu>.995)&EX._touching_intervals(tuple(a),tuple(b)))
  v=np.zeros_like(mu)
  if np.any(use_uv):v[use_uv]=batch_eval(mu[use_uv],uv_nodes(a,b,par,.05 if core else .08))
  if np.any(~use_uv):v[~use_uv]=batch_eval(mu[~use_uv],tensor_nodes(a,b,par['nf']))
  q=factor*v*.75*(1+mu**2)
  ref=net.pair_moments[:,i,j]
  mom=np.array([np.sum(w*q*eval_legendre(l,mu)) for l in range(25)])
  typ='pair'
 sort=np.argsort(mu);mu=mu[sort];w=w[sort];q=q[sort]
 if np.any(~np.isfinite(q)) or np.any(q<0):raise ValueError((i,j,'invalid source measure'))
 scale=max(abs(ref[0]) if i!=j else abs(ref[1]),1e-300)
 result=dict(i=i,j=j,kind=typ,measure_integral=float(w@q),reference_scale=float(scale),source_moment_error=float(np.max(abs(mom-ref))/scale),source_moment_error_l0_l4=float(np.max(abs(mom[:5]-ref[:5]))/scale),reference_moments=ref.tolist(),direct_moments=mom.tolist(),wall_s=time.monotonic()-t)
 # All physical values in this record remain unscaled source results.
 return result,mu,w,q
jobs=[(i,j) for i in range(17) for j in range(i+1,35) if net.pair_moments[0,i,j]>0]+[(i,i) for i in range(17)]
if args.only=='test':jobs=[(7,10),(8,8),(8,29),(8,34),(0,16)]
if args.only=='same':jobs=[(i,i) for i in range(17)]
t=time.monotonic();result=[];rows=[]
with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
 fs={pool.submit(job,ij):ij for ij in jobs}
 for f in concurrent.futures.as_completed(fs):
  try:
   r,mu,w,q=f.result();result.append(r);rows.append((r['i'],r['j'],mu,w,q))
   if len(result)%20==0 or args.only:print(len(result),r['i'],r['j'],r['source_moment_error'],'elapsed',round(time.monotonic()-t,2),flush=True)
  except Exception as e:
   print('FAIL',fs[f],repr(e),flush=True);raise
result.sort(key=lambda r:(r['i'],r['j']));rows.sort(key=lambda r:r[:2])
# Flat offsets; each measure is a separately typed positive quadrature.
offset=np.r_[0,np.cumsum([len(x[2]) for x in rows])]
np.savez_compressed(root/'SOURCE_MEASURE.npz',pairs=np.array([x[:2] for x in rows]),offset=offset,mu=np.concatenate([x[2] for x in rows]),weight=np.concatenate([x[3] for x in rows]),density=np.concatenate([x[4] for x in rows]),state_labels=net.state_labels,mode_measure=net.mode_measure,equilibrium_weight=net.equilibrium_weight,momentum_scale=net.momentum_scale)
summary=dict(schema='r118c2c.source-measure/1',source=str(owner),source_sha256=sha(owner),lane=args.lane,elapsed_s=time.monotonic()-t,measure_sha256=sha(root/'SOURCE_MEASURE.npz'),pairs=result)
(root/'SOURCE_RESULTS.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
print('COMPLETE',len(result),'max moment error',max(r['source_moment_error'] for r in result),flush=True)
