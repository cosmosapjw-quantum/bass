"""Direct continuum Bose energy integral at the owner frequency quadrature.
Compare to lifted graph with *projected* positive node masses.
Uses same source quadrature; this checks representation closure, not source novelty.
"""
import argparse,pathlib,sys,json,math,hashlib,time,concurrent.futures
import numpy as np
from numpy.polynomial.legendre import leggauss
P=pathlib.Path
p=argparse.ArgumentParser();p.add_argument('--rec',type=P,required=True);p.add_argument('--lift',type=P,required=True);p.add_argument('--graph',type=P,required=True);p.add_argument('--out',type=P,required=True);p.add_argument('--workers',type=int,default=4)
args=p.parse_args();rec=args.rec.resolve();root=args.out.resolve();root.mkdir(exist_ok=False)
sys.path.insert(0,str(rec/'src'))
from full_bianchi_hyrec.recoil import pair_cell_conductance as PCC,exterior_interface as EX,same_cell_regular as SC
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import CollisionNetwork
net=CollisionNetwork.from_npz(rec/'data/full_scalar_com_khw_v050.npz');factor=8*np.pi*PCC.dnu/PCC.c**3
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
# Smooth and sharper spectra. These tests are isotropic; direct angular
# integrals eliminate angular quadrature as a source of energy error.
names=['thermal','smooth_dilute','smooth_bose','narrow_bose','steep_dilute']
def activity(x,nu):
    z=np.exp(-PCC.beta*PCC.h*nu)
    z0=np.exp(-PCC.beta*PCC.h*PCC.nu_abs)
    # scale alpha by z0 for well-conditioned activity differences.
    aa=np.stack([np.ones_like(x)*.3,1e-17*(1+.15*np.tanh(x/3)),.3*(1+.15*np.tanh(x/3)),.3*(1+.25*np.exp(-.5*((x-1.2)/.22)**2)),1e-17*(1+.3*np.tanh(x/.25))],axis=-1)
    q=aa*z[...,None]/z0
    f=q/(1-q)
    return aa/z0,f
def evaluate(nt,ns,mu,w):
    xt=(nt-PCC.nu_abs)/PCC.dnu;xs=(ns-PCC.nu_abs)/PCC.dnu
    at,ft=activity(xt,nt);a_s,fs=activity(xs,ns)
    q=density(nt,ns,mu)*w
    event=q[...,None]*(1+ft)*(1+fs)*(a_s-at)*(xt-xs)[...,None]
    axes=tuple(range(1,event.ndim-1))
    return np.sum(event,axis=axes),np.sum(abs(event),axis=axes)
def batch(mu,nodes,rev):
    nt,ns,w=nodes;v=[];a=[]
    for k in range(0,len(mu),8):
        z,q=evaluate(nt[None,:],ns[None,:],mu[k:k+8,None],w)
        v.append(z);a.append(q)
    # Reversal swaps both activity difference and frequency difference,
    # so energy transfer is invariant.
    return np.concatenate(v),np.concatenate(a)
def job(ij):
    i,j=ij
    if i==j:
        par=SC.PRODUCTION_LANE;mu,w=angular(par)
        u,wu=SC._u_rule(i,par['nu'],par['nu_pole']);y,wy=PCC.leggauss(par['ny'])
        a,b=net.state_intervals[i];half=np.minimum(u-a,b-u)[None,:,None];vals=[];gross=[]
        for k in range(0,len(mu),8):
            m=mu[k:k+8,None,None];s=np.sqrt((1-m)/2);ym=np.minimum(par['ymax'],half/s)
            v=s*ym*y[None,None,:];nt=PCC.nu_abs+PCC.dnu*(u[None,:,None]+v);ns=PCC.nu_abs+PCC.dnu*(u[None,:,None]-v)
            ww=2*s*wu[None,:,None]*ym*wy[None,None,:]
            q,r=evaluate(nt,ns,m,ww);vals.append(q);gross.append(r)
        val=.5*np.concatenate(vals);ab=.5*np.concatenate(gross)
    else:
        core=j<17;par=PCC.PRODUCTION_LANE if core else EX.LANES['production'];mu,w=angular(par)
        a,b=(net.state_intervals[i],net.state_intervals[j]) if core else (net.state_intervals[j],net.state_intervals[i])
        use=np.arange(len(mu))<par['ob']
        if not core:use|=EX._crosses_resonance_mean(tuple(a),tuple(b))|((mu>.995)&EX._touching_intervals(tuple(a),tuple(b)))
        val=np.zeros((len(mu),len(names)));ab=val.copy()
        if np.any(use):val[use],ab[use]=batch(mu[use],uv_nodes(a,b,par,.05 if core else .08),not core)
        if np.any(~use):val[~use],ab[~use]=batch(mu[~use],tensor_nodes(a,b,par['nf']),not core)
    weight=factor*.75*(1+mu**2)*w
    return (i,j,weight@val,weight@ab)
src=np.load(args.lift,allow_pickle=False)
with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as p:
    rows=list(p.map(job,[tuple(q) for q in src['pairs']]))
raw=np.sum([q[2] for q in rows],axis=0);gross=np.sum([q[3] for q in rows],axis=0)
# independent GL128 positive hat projection of each continuous f.
z,w=leggauss(128);t=(1+z)/2;w=w/2;lo=src['bounds'][:,0,None];hi=src['bounds'][:,1,None];x=lo+(hi-lo)*t
nu=PCC.nu_abs+PCC.dnu*x;v=factor*(hi-lo)*nu**2*w
_,f=activity(x,nu)
hat=np.stack([1-t,t],axis=1)
mass=np.einsum('ij,ja,ijk->iak',v,hat,f).reshape(70,len(names))
g=src['g'].ravel();pi=src['pi'].ravel();z=pi/g
fnode=mass/g[:,None];an=fnode/(z[:,None]*(1+fnode))
# Conductance integrals from the lifted source, no angular graph bias.
q_lift=np.zeros(len(names));qg=np.zeros(len(names));pair_diff=np.zeros(len(names))
for k,(i,j) in enumerate(src['pairs']):
    sl=slice(src['offset'][k],src['offset'][k+1])
    Q=src['weight'][sl]@src['density'][sl]
    for a,b in ((0,0),(0,1),(1,0),(1,1)):
        if i==j and a>=b:continue
        I=2*i+a;J=2*j+b
        q_lift+=Q[2*a+b]*(1+fnode[I])*(1+fnode[J])*(an[J]-an[I])*(src['bounds'].ravel()[I]-src['bounds'].ravel()[J])
# Native driver cases on actual graph are written to disk for comparison.
with args.graph.open('rb') as fp:
    assert fp.read(8)==b'RECPOS01';n,na,nb=np.fromfile(fp,dtype='<u4',count=3)
    d=np.fromfile(fp,dtype='<f8',count=4*na).reshape(na,4);mp=np.fromfile(fp,dtype='<f8',count=3*n).reshape(n,3)
    for _ in range(nb):
        I,J=np.fromfile(fp,dtype='<u4',count=2);W=np.fromfile(fp,dtype='<f8',count=na*na).reshape(na,na)
        qg+=W.sum()*(1+fnode[I])*(1+fnode[J])*(an[J]-an[I])*(src['bounds'].ravel()[I]-src['bounds'].ravel()[J])
for k,name in enumerate(names):
    f=np.repeat(fnode[:,k,None],na,axis=1)
    txt='rec_dual_source_case_v1\n0 0\n'+f"{float(src['nu0']):.17g} {float(src['dnu']):.17g}\n"
    txt+=' '.join(f'{x:.17g}' for x in src['bounds'].ravel())+'\n'+' '.join(['1']*na)+'\n'
    txt+=' '.join(f'{x:.17g}' for x in f.ravel())+'\n0\n'
    (root/(name+'.txt')).write_text(txt)
out=[]
for i,name in enumerate(names):
    out.append(dict(name=name,direct_x_per_s=float(raw[i]),direct_gross_x_per_s=float(gross[i]),lifted_x_per_s=float(q_lift[i]),graph_x_per_s=float(qg[i]),closure_relative_to_gross=float(abs(q_lift[i]-raw[i])/gross[i]) if gross[i]>0 else None,relative_to_direct_signal=float(abs(q_lift[i]-raw[i])/abs(raw[i])) if raw[i]!=0 else None,closure_x_error_per_photon_s=float(abs(q_lift[i]-raw[i])/mass[:,i].sum()),total_number_m3=float(mass[:,i].sum())))
(root/'CONTINUUM.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print(out,flush=True)
