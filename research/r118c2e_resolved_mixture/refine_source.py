"""Compile refined positive hat event measure from the actual REC owner quadrature.
For each parent pair retain angular samples, refined frequency transitions,
and polynomial event energy moments for an independent continuum action.
"""
import argparse,pathlib,sys,json,math,hashlib,time,concurrent.futures
import numpy as np
from scipy.special import eval_legendre
P=pathlib.Path
p=argparse.ArgumentParser();p.add_argument('--rec',type=P,required=True);p.add_argument('--out',type=P,required=True);p.add_argument('--workers',type=int,default=4);p.add_argument('--levels',nargs='+',type=int,default=[1,2,4,8]);args=p.parse_args()
rec=args.rec.resolve();root=args.out.resolve();root.mkdir(exist_ok=False,parents=True)
sys.path.insert(0,str(rec/'src'))
from full_bianchi_hyrec.recoil import pair_cell_conductance as PCC, exterior_interface as EX, same_cell_regular as SC
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import CollisionNetwork
net=CollisionNetwork.from_npz(rec/'data/full_scalar_com_khw_v050.npz')
factor=8*np.pi*PCC.dnu/PCC.c**3
sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest()
levels=args.levels
assert levels==[1,2,4,8]
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
from numpy.polynomial.legendre import legvander
from numpy.polynomial.legendre import leggauss
# Direct continuum action reference spectra, copied semantically from C2D
# (thermal, smooth dilute/Bose, narrow Bose, steep dilute). One additional
# near-thermal finite-occupation perturbation.
names=['thermal','smooth_dilute','smooth_bose','narrow_bose','steep_dilute','near_thermal']
z0=np.exp(-PCC.beta*PCC.h*PCC.nu_abs)
def activity(x,nu):
    aa=np.stack([np.ones_like(x)*.3,1e-17*(1+.15*np.tanh(x/3)),.3*(1+.15*np.tanh(x/3)),.3*(1+.25*np.exp(-.5*((x-1.2)/.22)**2)),1e-17*(1+.3*np.tanh(x/.25)),.3*(1+1e-9*np.tanh(x/3))],axis=-1)
    z=np.exp(-PCC.beta*PCC.h*nu)
    q=aa*z[...,None]/z0
    return aa/z0,q/(1-q)
def block(nt,ns,mu,w,i,j):
    # Broadcast owner integrand first, preserve exact source ordering.
    D=density(nt,ns,mu)*w
    shape=D.shape;batch=shape[0]
    xt=np.broadcast_to((nt-PCC.nu_abs)/PCC.dnu,shape).reshape(batch,-1)
    xs=np.broadcast_to((ns-PCC.nu_abs)/PCC.dnu,shape).reshape(batch,-1)
    nt=np.broadcast_to(nt,shape).reshape(batch,-1);ns=np.broadcast_to(ns,shape).reshape(batch,-1)
    D=D.reshape(batch,-1)
    l,r=net.state_intervals[i];a,b=net.state_intervals[j]
    t=(xt-l)/(r-l);s=(xs-a)/(b-a)
    assert min(t.min(),s.min())>=0 and max(t.max(),s.max())<=1
    out={}
    for n in levels:
        N=n+1
        it=np.minimum((n*t).astype(int),n-1);js=np.minimum((n*s).astype(int),n-1)
        u=n*t-it;v=n*s-js
        if i==j:
            hats=[1-np.maximum(u,v),np.maximum(v-u,0),np.maximum(u-v,0),np.minimum(u,v)]
        else:hats=[(1-u)*(1-v),(1-u)*v,u*(1-v),u*v]
        index=(np.arange(batch)[:,None]*N*N+it*N+js).ravel()
        Q=np.zeros(batch*N*N)
        for off,h in zip([0,1,N,N+1],hats):
            Q+=np.bincount(index+off,weights=(D*h).ravel(),minlength=len(Q))
        out[n]=Q.reshape(batch,N,N)
    # Frequency-resolved energy transfer for arbitrary smooth anisotropic
    # occupation represented in local Legendre polynomials degree <= 4.
    # P_m(t) P_n(s) times (x_t-x_s) on the exact source quadrature.
    pt=legvander(2*t-1,4);ps=legvander(2*s-1,4)
    K=np.einsum('bqm,bq,bqn->bmn',pt,D*(xt-xs),ps,optimize=True)
    aa,fa=activity(xt,nt);bb,fb=activity(xs,ns)
    flux=D[...,None]*(1+fa)*(1+fb)*(bb-aa)*(xt-xs)[...,None]
    direct=np.sum(flux,axis=1);gross=np.sum(abs(flux),axis=1)
    raw=np.stack([D.sum(axis=1),np.sum(D*xt,axis=1),np.sum(D*xs,axis=1)],axis=1)
    return out,K,direct,gross,raw
def batch_eval(mu,nodes,i,j):
    nt,ns,w=nodes;parts=[]
    for k in range(0,len(mu),8):
        parts.append(block(nt[None,:],ns[None,:],mu[k:k+8,None],w,i,j))
    return ({n:np.concatenate([x[0][n] for x in parts]) for n in levels},*[np.concatenate([x[j] for x in parts]) for j in range(1,5)])
def job(ij):
    i,j=ij
    if i==j:
        par=SC.PRODUCTION_LANE;mu,w=angular(par)
        u,wu=SC._u_rule(i,par['nu'],par['nu_pole']);y,wy=PCC.leggauss(par['ny']);a,b=net.state_intervals[i]
        half=np.minimum(u-a,b-u)[None,:,None];parts=[]
        for k in range(0,len(mu),8):
            m=mu[k:k+8,None,None];s=np.sqrt((1-m)/2);ym=np.minimum(par['ymax'],half/s)
            v=s*ym*y[None,None,:];nt=PCC.nu_abs+PCC.dnu*(u[None,:,None]+v);ns=PCC.nu_abs+PCC.dnu*(u[None,:,None]-v)
            ww=2*s*wu[None,:,None]*ym*wy[None,None,:]
            parts.append(block(nt,ns,m,ww,i,i))
        Q={n:np.concatenate([x[0][n] for x in parts]) for n in levels}
        K,direct,gross,raw=[np.concatenate([x[j] for x in parts]) for j in range(1,5)]
    else:
        core=j<17;par=PCC.PRODUCTION_LANE if core else EX.LANES['production'];mu,w=angular(par)
        I,J=(i,j) if core else (j,i);a,b=net.state_intervals[I],net.state_intervals[J]
        use=np.arange(len(mu))<par['ob']
        if not core:use|=EX._crosses_resonance_mean(tuple(a),tuple(b))|((mu>.995)&EX._touching_intervals(tuple(a),tuple(b)))
        Q={n:np.zeros((len(mu),n+1,n+1)) for n in levels};K=np.zeros((len(mu),5,5));direct=np.zeros((len(mu),len(names)));gross=direct.copy();raw=np.zeros((len(mu),3))
        for mask,nodes in [(use,uv_nodes(a,b,par,.05 if core else .08)),(~use,tensor_nodes(a,b,par['nf']))]:
            if not np.any(mask):continue
            q,k,v,g,r=batch_eval(mu[mask],nodes,I,J)
            for n in levels:Q[n][mask]=q[n] if core else q[n].transpose(0,2,1)
            K[mask]=k if core else -k.transpose(0,2,1)
            direct[mask]=v;gross[mask]=g;raw[mask]=r if core else r[:,[0,2,1]]
    scale=factor*.75*(1+mu**2);K*=scale[:,None,None];direct*=scale[:,None];gross*=scale[:,None];raw*=scale[:,None]
    sym=0.;err=0.
    for n in levels:
        q=Q[n]*scale[:,None,None]
        if i==j:
            sym=max(sym,float(np.sum(w[:,None,None]*abs(q-q.transpose(0,2,1)))/max(np.sum(w[:,None,None]*q),1e-300)))
            q=(q+q.transpose(0,2,1))/2
        x=np.linspace(*net.state_intervals[i],n+1);y=np.linspace(*net.state_intervals[j],n+1)
        marg=np.stack([q.sum(axis=(1,2)),np.einsum('aij,i->a',q,x),np.einsum('aij,j->a',q,y)],axis=1)
        err=max(err,float(np.max(abs(marg-raw)/np.maximum(raw[:,0,None],1e-300))))
        assert np.min(q)>=0 and np.all(np.isfinite(q));Q[n]=q
    if i==j:
        K=(K-K.transpose(0,2,1))/2
        direct*=.5;gross*=.5
    order=np.argsort(mu)
    return (i,j,mu[order],w[order],{n:Q[n][order] for n in levels},K[order],w@direct,w@gross,err,sym)
jobs=[(i,j) for i in range(17) for j in range(i+1,35) if net.pair_moments[0,i,j]>0]+[(i,i) for i in range(17)]
rows=[];start=time.monotonic()
# Save per-pair data as individual compressed arrays to cap live memory;
# final concatenated arrays only for bounded levels.
with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
    for v in pool.map(job,jobs):
        rows.append(v)
        if len(rows)%50==0:print('pairs',len(rows),'elapsed',time.monotonic()-start,flush=True)
rows.sort(key=lambda x:x[:2]);off=np.r_[0,np.cumsum([len(q[2]) for q in rows])]
base=dict(pairs=np.array([v[:2] for v in rows]),offset=off,mu=np.concatenate([v[2] for v in rows]),weight=np.concatenate([v[3] for v in rows]),bounds=net.state_intervals,nu0=PCC.nu_abs,dnu=PCC.dnu,z0=z0)
for n in levels:
    Q=np.concatenate([v[4][n] for v in rows]);np.savez_compressed(root/f'REFINE_{n}.npz',**base,density=Q)
np.savez_compressed(root/'CONTINUUM_POLY.npz',**base,energy_moments=np.concatenate([v[5] for v in rows]))
direct=np.sum([q[6] for q in rows],axis=0);gross=np.sum([q[7] for q in rows],axis=0)
r=dict(pairs=len(rows),samples=int(off[-1]),levels=levels,max_marginal=max(q[8] for q in rows),max_same_sym=max(q[9] for q in rows),direct=[dict(name=n,signal=float(x),gross=float(y)) for n,x,y in zip(names,direct,gross)],elapsed=time.monotonic()-start,hashes={p.name:sha(p) for p in root.glob('*.npz')})
(root/'SOURCE_RESULTS.json').write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');print(r,flush=True)
