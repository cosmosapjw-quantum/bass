"""Build reciprocal positive angular graph of the lifted frequency modes."""
import argparse,pathlib,sys,json,hashlib,time,numpy as np
from scipy.integrate import lebedev_rule
from scipy.special import eval_legendre
P=pathlib.Path
p=argparse.ArgumentParser();p.add_argument('--lift',type=P,required=True);p.add_argument('--out',type=P,required=True);p.add_argument('--orders',nargs='+',type=int,default=[7,11,17]);p.add_argument('--mixed-dir',type=P);args=p.parse_args()
root=args.out.resolve();root.mkdir(exist_ok=False);src=np.load(args.lift,allow_pickle=False)
sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest()
def symmetric_scale(K,w,allow_global=False):
    z=K@w
    if np.any(z<=0):raise ValueError('zero row')
    d=1/np.sqrt(z)
    for it in range(1000):
        row=d*(K@(w*d));err=float(np.max(abs(row-1)))
        if err<3e-13:return K*d[:,None]*d[None,:],err,it+1,False
        if not np.all(np.isfinite(row)) or np.any(row<=0):raise ValueError('invalid scaling')
        d/=np.sqrt(row)
    # Newton for log row sums. Near-bipartite support can make the
    # Jacobian singular, so least-squares and line search are explicit.
    y=np.log(d)
    for it in range(100):
        d=np.exp(y);row=d*(K@(w*d));r=np.log(row);err=float(np.max(abs(row-1)))
        if err<3e-13:return K*d[:,None]*d[None,:],err,1000+it,False
        A=np.eye(len(w))+K*(w*d)[None,:]/(K@(w*d))[:,None]
        dy=np.linalg.lstsq(A,-r,rcond=1e-14)[0]
        ok=False
        for a in 2.**(-np.arange(20)):
            yy=y+a*dy
            if np.max(abs(yy))>300:continue
            dd=np.exp(yy);rr=dd*(K@(w*dd))
            if np.all(rr>0) and np.max(abs(np.log(rr)))<np.max(abs(r)):y=yy;ok=True;break
        if not ok:break
    if not allow_global:raise ValueError(('nonconverged',err))
    # Only exploratory non-Lebedev ray grid: scalar total monopole
    # normalization, NOT an angular row-preserving release.
    K=K/(w@(K@w));return K,float(np.max(abs(K@w-1))),1100,True
def graph(name,d,w,kind):
    t=time.monotonic();w=w/w.sum();a=len(w)
    assert np.all(w>0) and np.max(abs(np.linalg.norm(d,axis=1)-1))<1e-12
    dot=np.clip(d@d.T,-1,1);dot=(dot+dot.T)/2;np.fill_diagonal(dot,1.);ww=w[:,None]*w[None,:]
    X=src['bounds'].ravel();n=len(X);g=src['g'].ravel();pi=src['pi'].ravel();pm=src['p'].ravel()
    blocks=[];errs=[];rowerr=0.;itmax=0;max_detuning=0.;det_worst=0.;total_scale=0.;angular_err=0.;ang_scale=0.;fallback=0;fallback_weight=0.
    # A dilute test with linear angular activity A_i + B_i.e,
    # independent of endpoint. Raw continuum source angular integral
    # is compared separately against finite direction quadrature.
    centers=src['bounds'].mean(axis=1);A=1+.17*np.sin(centers/2.);B=np.stack([.08*np.cos(centers/3),.06*np.sin(centers/2),.09*np.ones_like(centers)],axis=1)
    act=A[:,None]+B@d.T
    raw_energy=0.;graph_energy=0.;raw_force=np.zeros(3);graph_force=np.zeros(3);energy_scale=0.;force_scale=0.
    b=float(src['dnu']/src['nu0'])
    for k,(i,j) in enumerate(src['pairs']):
        sl=slice(src['offset'][k],src['offset'][k+1]);mu=src['mu'][sl];aw=src['weight'][sl];Q=src['density'][sl];raw=src['raw'][sl]
        if i!=j:
            raw_energy+=np.sum(aw*raw[:,3])*(A[j]-A[i])
            energy_scale+=abs(np.sum(aw*raw[:,3])*(A[j]-A[i]))
            ps=raw[:,0]+b*raw[:,2];pt=raw[:,0]+b*raw[:,1]
            f=(np.sum(aw*(mu*pt-ps))*B[j]-np.sum(aw*(pt-mu*ps))*B[i])/3
        else:
            ps=raw[:,0]+b*raw[:,2];pt=raw[:,0]+b*raw[:,1]
            f=-np.sum(aw*(1-mu)*(pt+ps))*B[i]/6
        raw_force+=f;force_scale+=np.linalg.norm(f)
        pair_transfer=0.;pair_marg=0.;pair_moment=0.;pair_scale=0.
        for ii,jj in ((0,0),(0,1),(1,0),(1,1)):
            if i==j and ii>jj:continue
            I=2*i+ii;J=2*j+jj;q=Q[:,2*ii+jj]
            if I==J:
                qreg=(1-mu)*q;S=float(aw@qreg)
                if S<=0:continue
                K=np.interp(dot,mu,qreg)/S;np.fill_diagonal(K,0.)
                K/=np.sum(ww*K)
                K=np.divide(K,1-dot,out=np.zeros_like(K),where=1-dot>1e-14)
                W=S*ww*K
                ref=float(aw@(q*(mu-1)))/S
                err=abs(float(np.sum(W*(dot-1)))/S-ref)
            else:
                S=float(aw@q)
                if S<=0:continue
                K=np.interp(dot,mu,q)/S
                K,re,it,fb=symmetric_scale(K,w,kind!="lebedev");rowerr=max(rowerr,re);itmax=max(itmax,it);fallback+=int(fb);fallback_weight+=S*int(fb)
                W=S*ww*K
                err=abs(float(np.sum(W*dot))/S-float(aw@(q*mu))/S)
                if i!=j:
                    pair_transfer+=float(W.sum())*(X[I]-X[J]);pair_scale+=S*abs(X[I]-X[J])
                angular_err+=S*err;ang_scale+=S
            W=(W+W.T)/2
            assert np.all(np.isfinite(W)) and W.min()>=0
            blocks.append((int(I),int(J),W))
            # Independent state/event moment sum for linear dilute activity.
            flow=W*(act[j][None,:]-act[i][:,None])
            if I==J:flow=np.triu(flow,k=1)
            graph_energy+=float(flow.sum())*(X[I]-X[J])
            graph_force+=(1+b*X[I])*(flow.sum(axis=1)@d)-(1+b*X[J])*(flow.sum(axis=0)@d)
        if i!=j:
            target=float(aw@raw[:,3])
            err=abs(pair_transfer-target)/max(pair_scale,1e-300)
            max_detuning=max(max_detuning,err);det_worst+=abs(pair_transfer-target);total_scale+=pair_scale
    dest=root/f'graph_{name}.bin'
    with dest.open('wb') as f:
        f.write(b'RECPOS01');np.array([n,a,len(blocks)],dtype='<u4').tofile(f);np.asarray(np.c_[d,w],dtype='<f8').tofile(f);np.asarray(np.c_[g,pi,pm],dtype='<f8').tofile(f)
        for i,j,W in blocks:np.array([i,j],dtype='<u4').tofile(f);np.asarray(W,dtype='<f8',order='C').tofile(f)
    out=dict(name=name,angles=a,blocks=len(blocks),graph_sha256=sha(dest),row_error=rowerr,max_scaling_iterations=itmax,fallback_blocks=fallback,fallback_weight_fraction=fallback_weight/max(ang_scale,1e-300),maximum_pair_detuning_error=max_detuning,weighted_detuning_error=det_worst/total_scale,weighted_l1_error=angular_err/ang_scale,raw_dilute_detuning=raw_energy,graph_dilute_detuning=graph_energy,detuning_scaled_error=abs(graph_energy-raw_energy)/energy_scale,raw_dilute_force=raw_force.tolist(),graph_dilute_force=graph_force.tolist(),force_scaled_error=float(np.linalg.norm(graph_force-raw_force)/force_scale),wall_s=time.monotonic()-t,kind=kind)
    print(out,flush=True);return out
reports=[]
for order in args.orders:
    d,w=lebedev_rule(order);reports.append(graph('o'+str(order),d.T,w,'lebedev'))
if args.mixed_dir:
    r=np.genfromtxt(args.mixed_dir/'frequency_rays.tsv',names=True,delimiter='\t')
    q=np.genfromtxt(args.mixed_dir/'diagnostics.tsv',names=True,delimiter='\t')[-1]
    beta=np.array([q['host_beta_x'],q['host_beta_y'],q['host_beta_z']]);n=np.c_[r['e_x'],r['e_y'],r['e_z']];b2=beta@beta;gam=1/np.sqrt(1-b2);bn=n@beta
    D=gam*(1-bn);d=(n+(((gam-1)*bn/b2)-gam)[:,None]*beta)/D[:,None]
    w=r['weight']/(4*np.pi*D**2)
    print('mixed material angular weight sum',w.sum(),flush=True)
    q=graph('mixed',d,w,'accepted_BASS_rays_normalized_material_measure');q['material_weight_sum_before_normalization']=float(w.sum());reports.append(q)
(root/'GRAPH_RESULTS.json').write_text(json.dumps(reports,indent=2,allow_nan=False,default=lambda obj:obj.tolist())+'\n')
