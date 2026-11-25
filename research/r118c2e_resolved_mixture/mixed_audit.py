"""Frozen scalar energy action on evolved BASS temperature mixtures.
Same source angular collocation for continuum polynomial and refined
frequency lifts. No claim of a continuous angular quadrature limit."""
import argparse,pathlib,json,hashlib,numpy as np,time
from scipy.constants import h,k as k_B,c
from numpy.polynomial.legendre import leggauss,legvander
from hat_thermal import project,inverse_be
P=pathlib.Path
p=argparse.ArgumentParser();p.add_argument('--source',type=P,required=True);p.add_argument('--replay',type=P,required=True);p.add_argument('--out',type=P,required=True);p.add_argument('--only',default='');p.add_argument('--ratio-audit',type=float);args=p.parse_args()
root=args.out.resolve();root.mkdir(exist_ok=False)
def load(p):
 with np.load(p,allow_pickle=False) as s:return {key:s[key] for key in s.files}
S={n:load(args.source/f'REFINE_{n}.npz') for n in (1,2,4,8)}
P0=load(args.source/'CONTINUUM_POLY.npz');base=S[1];bounds=base['bounds'];nu0=float(base['nu0']);dnu=float(base['dnu']);z0=float(base['z0'])
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def scale(K,w):
    z=K@w
    if np.any(z<=0):raise ValueError('zero parent angular support')
    d=1/np.sqrt(z)
    for it in range(500):
        r=d*(K@(w*d));err=np.max(abs(r-1))
        if err<3e-13:return d[:,None]*d[None,:],float(err)
        d/=np.sqrt(r)
    y=np.log(d)
    for _ in range(100):
        d=np.exp(y);r=d*(K@(w*d));err=np.max(abs(r-1))
        if err<3e-13:return d[:,None]*d[None,:],float(err)
        J=np.eye(len(w))+K*(w*d)[None,:]/(K@(w*d))[:,None]
        dy=np.linalg.lstsq(J,-np.log(r),rcond=1e-14)[0]
        for a in 2.**(-np.arange(20)):
            yy=y+a*dy
            if np.max(abs(yy))>300:continue
            dd=np.exp(yy);rr=dd*(K@(w*dd))
            if np.all(rr>0) and np.max(abs(np.log(rr)))<np.max(abs(np.log(r))):y=yy;break
        else:break
    raise ValueError(('parent row balance nonconverged',err))
def interp(mu,arr,dot):
    # Shared nonnegative linear angular interpolation coefficients. Energy
    # moments can be signed; do not clip them. All source arrays use the
    # identical brackets.
    idx=np.searchsorted(mu,dot,side='right')-1;idx=np.clip(idx,0,len(mu)-2)
    t=np.clip((dot-mu[idx])/(mu[idx+1]-mu[idx]),0,1)
    tail=(None,)*(arr.ndim-1)
    return (1-t)[(...,)+tail]*arr[idx]+t[(...,)+tail]*arr[idx+1]
def plan(d,w):
    dot=np.clip(d@d.T,-1,1);dot=(dot+dot.T)/2;np.fill_diagonal(dot,1.)
    ww=w[:,None]*w[None,:];rows=[]
    for k,(i,j) in enumerate(base['pairs']):
        sl=slice(base['offset'][k],base['offset'][k+1]);mu=base['mu'][sl];aw=base['weight'][sl];q=base['density'][sl].sum(axis=(1,2))
        if i!=j:
            I=float(aw@q);K=interp(mu,q,dot)/I
            norm,err=scale(K,w);mul=ww*norm;reg=False
        else:
            # Same-cell regularized angular transport; no identical-angle
            # transfer. Apply exactly the same normalization to raw source
            # energy moments and frequency-lifted energy action.
            qr=(1-mu)*q;K=interp(mu,qr,dot);np.fill_diagonal(K,0.)
            norm=float(aw@qr)/np.sum(ww*K)
            mul=np.divide(ww*norm,1-dot,out=np.zeros_like(ww),where=(1-dot)>1e-14);reg=True;err=0.
        rows.append((i,j,sl,mu,mul,reg,err))
    return dot,rows
def polynomial_inputs(logT,q,T):
    # Evaluate the actual Planck mixture at Gauss points, not from
    # broadband photon frequency masses. Fit degree 4 in parent detuning.
    z,w=leggauss(12);x=bounds.mean(axis=1)[:,None]+(bounds[:,1]-bounds[:,0])[:,None]*z/2
    def evalf(x):
        nu=nu0+dnu*x
        # a small number of frequencies per parent: direct Planck mixture.
        y=h*nu[:,:,None,None]/(k_B*T)*np.exp(-logT)[None,None,:,:]
        f=np.divide(1.,np.expm1(np.minimum(y,700.)),out=np.zeros_like(y),where=y<700.)
        return np.einsum('iqan,an->iqa',f,q)
    f=evalf(x);zr=np.exp(-h*(nu0+dnu*x)/(k_B*3000.))/z0
    b=f/zr[:,:,None];ref=float(np.mean(b/(1+f)))
    A=1+f;B=b-ref*A
    coeff=lambda v:np.einsum('qm,q,iqa->ima',legvander(z,4),w,v)*(np.arange(5)[None,:,None]+.5)
    ca=coeff(A);cb=coeff(B)
    # Independent 15-point test on the fitted polynomial.
    zz,_=leggauss(15);xx=bounds.mean(axis=1)[:,None]+(bounds[:,1]-bounds[:,0])[:,None]*zz/2
    vf=evalf(xx);vr=np.exp(-h*(nu0+dnu*xx)/(k_B*3000.))/z0
    vb=vf/vr[:,:,None]-ref*(1+vf)
    pred=np.einsum('qm,ima->iqa',legvander(zz,4),cb)
    err=float(np.max(abs(vb-pred))/max(np.max(abs(vf/vr[:,:,None])),1e-300))
    ap=np.einsum('qm,ima->iqa',legvander(zz,4),ca)
    errA=float(np.max(abs(ap-(1+vf))))
    # f is small for these physical Planck mixtures; for node projection
    # fit f rather than subtracting one from A.
    cf=coeff(f)
    pred_f=np.einsum('qm,ima->iqa',legvander(zz,4),cf)
    errf=float(np.max(abs(pred_f-vf))/max(np.max(vf),1e-300))
    return ca,cb,cf,ref,err,errA,errf
def eval_continuum(dot,rows,ca,cb):
    e=0.;gross=0.
    for i,j,sl,mu,mul,reg,err in rows:
        K=P0['energy_moments'][sl]
        if reg:K=K*(1-mu)[:,None,None]
        K=interp(mu,K,dot)*mul[:,:,None,None]
        # A_t B_s - B_t A_s; frequency and angular sums remain
        # nonseparable. Half for unordered same-parent events.
        v=np.einsum('abmn,ma,nb->ab',K,ca[i],cb[j],optimize=True)-np.einsum('abmn,ma,nb->ab',K,cb[i],ca[j],optimize=True)
        factor=.5 if i==j else 1.
        e+=factor*float(v.sum())/z0;gross+=factor*float(abs(v).sum())/z0
    return e,gross
def eval_refined(dot,rows,cf,ref,n):
    # hat-average f from the analytic local smooth spectrum polynomial.
    x,xx,zr,W,g,z=project(bounds,n,nu0,dnu,z0)
    p=2*(xx-bounds[:,0,None])/(bounds[:,1]-bounds[:,0])[:,None]-1
    f0=np.einsum('iqm,ima->iqa',legvander(p,4),cf)
    assert np.min(f0)>=0
    f=np.einsum('inq,iqa->ina',W,f0)
    alpha=inverse_be(f,zr,W,z)
    A=1+f;B=A*(alpha-ref);e=0.;gross=0.
    for i,j,sl,mu,mul,reg,err in rows:
        Q=S[n]['density'][sl]
        if reg:Q=Q*(1-mu)[:,None,None]
        K=interp(mu,Q,dot)*mul[:,:,None,None]
        # Store angle-major first for a bounded temporary. Integrate
        # source-lifted event energy, not difference of absolute energies.
        X=x[i,:,None]-x[j,None,:]
        f1=A[i].T[:,None,:,None]*B[j].T[None,:,None,:]
        f2=B[i].T[:,None,:,None]*A[j].T[None,:,None,:]
        v=K*(f1-f2)*X[None,None,:,:]
        factor=.5 if i==j else 1.
        e+=factor*float(v.sum())/z0;gross+=factor*float(abs(v).sum())/z0
    return e,gross
replay=json.loads((args.replay/'REPLAY_RESULTS.json').read_text());results=[];cache={}
for rr in replay['cases']:
    if rr['status']!='PASS_SCOPED' or not rr['case'].startswith(args.only):continue
    name=rr['case'];path=args.replay/name
    r=np.genfromtxt(path/'temperature_rays.tsv',names=True,delimiter='\t')
    z=np.genfromtxt(path/'temperature_nodes.tsv',names=True,delimiter='\t')
    na=len(r);d=np.c_[r['e_x'],r['e_y'],r['e_z']];w=r['angular_weight']/(4*np.pi);w/=w.sum()
    logT=z['log_temperature'].reshape(na,-1);q=z['weight'].reshape(na,-1)
    key=hashlib.sha256(d.tobytes()+w.tobytes()).hexdigest()
    if key not in cache:cache[key]=plan(d,w)
    dot,rows=cache[key]
    temps=[(name,rr['T_emit'])]
    if args.ratio_audit is not None:
        temps=[('ratio_hot',rr['T_emit']*args.ratio_audit),('ratio_cold',rr['T_emit']/args.ratio_audit)]
    elif name=='near_flrw':temps += [('flrw_hot_0p1pct',rr['T_emit']*1.001),('flrw_cold_0p1pct',rr['T_emit']*.999)]
    for label,T in temps:
        t=time.monotonic();ca,cb,cf,ref,err,errA,errf=polynomial_inputs(logT,q,T)
        e,gross=eval_continuum(dot,rows,ca,cb)
        row=dict(case=label,replay_case=name,T_emit=T,angles=na,poly_activity_relative_error=err,poly_A_absolute_error=errA,poly_f_relative_error=errf,continuum_x_per_s=e,continuum_energy_j_m3_s=e*h*dnu,continuum_gross_x_per_s=gross,max_parent_row_defect=max(x[-1] for x in rows),refinements=[])
        assert max(err,errA,errf)<2e-12,(label,err,errA,errf)
        if args.ratio_audit is None and name in ('early_t2048','near_t1024','near_ang72','near_flrw','near_local_1024','near_local_ang72'):
            # Angular convergence check for near_ang72 uses direct
            # continuum only; avoid allocating 72^2*81 per pair.
            if name not in ('near_ang72','near_local_ang72'):
                for n in (1,2,4,8):
                    en,gr=eval_refined(dot,rows,cf,ref,n)
                    row['refinements'].append(dict(subcells=n,x_per_s=en,energy_j_m3_s=en*h*dnu,gross_x_per_s=gr,relative_error=abs(en-e)/abs(e) if label!='near_flrw' and e!=0 else None))
        row['wall_s']=time.monotonic()-t
        print(label,'energy',e*h*dnu,'refinements',[(q['subcells'],q['energy_j_m3_s'],q['relative_error']) for q in row['refinements']],'poly error',errf,flush=True)
        results.append(row)
        (root/'MIXED_PARTIAL.json').write_text(json.dumps(results,indent=2,allow_nan=False)+'\n')
(root/'MIXED_RESULTS.json').write_text(json.dumps(results,indent=2,allow_nan=False)+'\n')
