"""Direct source quadrature and positive frequency endpoint lift."""
import argparse, pathlib, sys, json, math, hashlib, time, concurrent.futures
import numpy as np
from scipy.special import eval_legendre
P=pathlib.Path
p=argparse.ArgumentParser();p.add_argument('--rec',type=P,required=True);p.add_argument('--out',type=P,required=True);p.add_argument('--workers',type=int,default=4)
args=p.parse_args();rec=args.rec.resolve();root=args.out.resolve();root.mkdir(parents=True,exist_ok=False)
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
def lifted(nt,ns,mu,w,i,j,same):
    # Row = i, column = j. Caller supplies ordered frequencies.
    l,r=net.state_intervals[i];a,b=net.state_intervals[j]
    xt=(nt-PCC.nu_abs)/PCC.dnu;xs=(ns-PCC.nu_abs)/PCC.dnu
    t=(xt-l)/(r-l);s=(xs-a)/(b-a)
    assert np.min(t)>=-1e-10 and np.max(t)<=1+1e-10 and np.min(s)>=-1e-10 and np.max(s)<=1+1e-10
    # No clipping: quadrature nodes must lie in the open interval.
    assert np.min(t)>=0 and np.max(t)<=1 and np.min(s)>=0 and np.max(s)<=1
    d=density(nt,ns,mu)*w
    if same:
        # Comonotone coupling: no artificial intra-cell frequency jump
        # when physical incident and outgoing frequencies coincide.
        hats=[1-np.maximum(t,s),np.maximum(s-t,0),np.maximum(t-s,0),np.minimum(t,s)]
    else:hats=[(1-t)*(1-s),(1-t)*s,t*(1-s),t*s]
    axes=tuple(range(1,d.ndim))
    q=np.stack([np.sum(d*h,axis=axes) for h in hats],axis=-1)
    raw=np.stack([np.sum(d,axis=axes),np.sum(d*xt,axis=axes),np.sum(d*xs,axis=axes),np.sum(d*(xt-xs),axis=axes)],axis=-1)
    return q,raw
def eval_block(mu,nodes,i,j,reverse):
    nt,ns,w=nodes;qs=[];rs=[]
    for k in range(0,len(mu),8):
        m=mu[k:k+8,None]
        # density must be evaluated in owner ordering, then transpose
        # endpoint hats for exterior pairs; use frequency reversal
        # only for coordinate labelling, not for changing integrand.
        if reverse:
            q,r=lifted(nt[None,:],ns[None,:],m,w,j,i,False)
            q=q[:,[0,2,1,3]];r=r[:,[0,2,1,3]];r[:,3]*=-1
        else:q,r=lifted(nt[None,:],ns[None,:],m,w,i,j,False)
        qs.append(q);rs.append(r)
    return np.concatenate(qs),np.concatenate(rs)
def job(ij):
    i,j=ij;start=time.monotonic()
    if i==j:
        par=SC.PRODUCTION_LANE;mu,w=angular(par)
        u,wu=SC._u_rule(i,par['nu'],par['nu_pole']);y,wy=PCC.leggauss(par['ny'])
        a,b=net.state_intervals[i];half=np.minimum(u-a,b-u)[None,:,None];qs=[];rs=[]
        for k in range(0,len(mu),8):
            m=mu[k:k+8,None,None];s=np.sqrt((1-m)/2);ym=np.minimum(par['ymax'],half/s)
            v=s*ym*y[None,None,:];nt=PCC.nu_abs+PCC.dnu*(u[None,:,None]+v);ns=PCC.nu_abs+PCC.dnu*(u[None,:,None]-v)
            ww=2*s*wu[None,:,None]*ym*wy[None,None,:]
            q,r=lifted(nt,ns,m,ww,i,i,True);qs.append(q);rs.append(r)
        q=np.concatenate(qs);raw=np.concatenate(rs)
    else:
        core=j<17;par=PCC.PRODUCTION_LANE if core else EX.LANES['production']
        mu,w=angular(par);a,b=(net.state_intervals[i],net.state_intervals[j]) if core else (net.state_intervals[j],net.state_intervals[i])
        use=np.arange(len(mu))<par['ob']
        if not core:use|=EX._crosses_resonance_mean(tuple(a),tuple(b))|((mu>.995)&EX._touching_intervals(tuple(a),tuple(b)))
        q=np.zeros((len(mu),4));raw=q.copy()
        if np.any(use):q[use],raw[use]=eval_block(mu[use],uv_nodes(a,b,par,.05 if core else .08),i,j,not core)
        if np.any(~use):q[~use],raw[~use]=eval_block(mu[~use],tensor_nodes(a,b,par['nf']),i,j,not core)
    scale=factor*.75*(1+mu**2);q*=scale[:,None];raw*=scale[:,None]
    x=net.state_intervals[i];y=net.state_intervals[j]
    xt=np.array([x[0],x[0],x[1],x[1]]);xs=np.array([y[0],y[1],y[0],y[1]])
    # Exact at each source quadrature node after frequency integration.
    e=np.stack([q.sum(axis=1),q@xt,q@xs,q@(xt-xs)],axis=1)
    norm=np.maximum(raw[:,0],1e-300)
    err=float(np.max(abs(e-raw)/norm[:,None]))
    # Same-cell reversal at fixed angle; symmetrize unordered cross
    # channels only after verifying native reciprocity.
    symmetry=0.
    if i==j:
        symmetry=float(np.sum(w*abs(q[:,1]-q[:,2]))/max(np.sum(w*(q[:,1]+q[:,2])),1e-300))
        q[:,1]=q[:,2]=(q[:,1]+q[:,2])/2
    assert np.all(np.isfinite(q)) and np.min(q)>=0 and err<2e-11
    mom=np.array([np.sum(w*q.sum(axis=1)*eval_legendre(l,mu)) for l in range(25)])
    if i==j:
        mom=np.array([np.sum(w*q.sum(axis=1)*(eval_legendre(l,mu)-1))/net.equilibrium_weight[i] for l in range(25)])
        ref=net.same_cell_rates[:,i];norm0=abs(ref[1])
    else:ref=net.pair_moments[:,i,j];norm0=ref[0]
    rec=dict(i=i,j=j,marginal_error=err,raw_symmetry=symmetry,release_error=float(np.max(abs(mom-ref))/norm0),source_integral=(w@raw).tolist(),lifted_integral=(w@q).tolist(),wall_s=time.monotonic()-start)
    sort=np.argsort(mu)
    return rec,mu[sort],w[sort],q[sort],raw[sort]
jobs=[(i,j) for i in range(17) for j in range(i+1,35) if net.pair_moments[0,i,j]>0]+[(i,i) for i in range(17)]
rows=[];t=time.monotonic()
with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
    futures={pool.submit(job,ij):ij for ij in jobs}
    for f in concurrent.futures.as_completed(futures):
        try:rows.append(f.result())
        except Exception as e:print('FAILED',futures[f],repr(e),flush=True);raise
        if len(rows)%50==0:print(len(rows),'elapsed',time.monotonic()-t,flush=True)
rows.sort(key=lambda v:(v[0]['i'],v[0]['j']))
offset=np.r_[0,np.cumsum([len(v[1]) for v in rows])]
# Node phase volume and thermal measure: positive linear hats on
# actual source frequency intervals. Exact source g and pi recovered.
from numpy.polynomial.legendre import leggauss
z,w=leggauss(32);t=(1+z)/2;w=w/2
lo=net.state_intervals[:,0,None];hi=net.state_intervals[:,1,None]
nu=PCC.nu_abs+PCC.dnu*(lo+(hi-lo)*t)
vol=factor*(hi-lo)*nu**2*w
hat=np.stack([1-t,t],axis=1)
g=vol@hat;pi=(vol*np.exp(-PCC.beta*PCC.h*nu))@hat
pnode=PCC.h/PCC.c*(PCC.nu_abs+PCC.dnu*net.state_intervals)
errors=dict(g=float(np.max(abs(g.sum(axis=1)/net.mode_measure-1))),pi=float(np.max(abs(pi.sum(axis=1)/net.equilibrium_weight-1))),p=float(np.max(abs((g*pnode).sum(axis=1)/g.sum(axis=1)/net.momentum_scale-1))))
assert max(errors.values())<1e-12
np.savez_compressed(root/'LIFT.npz',pairs=np.array([[q[0]['i'],q[0]['j']] for q in rows]),offset=offset,mu=np.concatenate([q[1] for q in rows]),weight=np.concatenate([q[2] for q in rows]),density=np.concatenate([q[3] for q in rows]),raw=np.concatenate([q[4] for q in rows]),g=g,pi=pi,p=pnode,bounds=net.state_intervals,labels=net.state_labels,nu0=PCC.nu_abs,dnu=PCC.dnu)
result=dict(source_sha256=sha(owner),lift_sha256=sha(root/'LIFT.npz'),node_errors=errors,pairs=[v[0] for v in rows],elapsed=time.monotonic()-t)
(root/'LIFT_RESULTS.json').write_text(json.dumps(result,indent=2,allow_nan=False,default=lambda obj:obj.tolist())+'\n')
print('DONE',len(rows),'marginal',max(q[0]['marginal_error'] for q in rows),'symmetry',max(q[0]['raw_symmetry'] for q in rows),'node',errors,flush=True)
