"""Isotropic continuum vs refined positive hat source actions.
Nonlinear equilibrium projection uses exact hat-average BE inverse.
Only an action closure audit; no claim of an exact pair integrator."""
import argparse,pathlib,json,hashlib,numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.constants import h,k as k_B
P=pathlib.Path
p=argparse.ArgumentParser();p.add_argument('--source',type=P,required=True);p.add_argument('--out',type=P,required=True);a=p.parse_args();a.out.mkdir(exist_ok=False)
src=json.loads((a.source/'SOURCE_RESULTS.json').read_text());names=[v['name'] for v in src['direct']]
sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest()
from hat_thermal import project,inverse_be
def eval_action(Q,x,f,alpha,z0):
    N=f.shape[-1];out=np.zeros(N);gross=np.zeros(N)
    for (i,j),K in Q:
        flow=K[:,:,None]*(1+f[i,:,None,:])*(1+f[j,None,:,:])*(alpha[j,None,:,:]-alpha[i,:,None,:])/z0
        e=flow*(x[i,:,None]-x[j,None,:])[:,:,None]
        factor=.5 if i==j else 1.
        out+=factor*e.sum(axis=(0,1));gross+=factor*abs(e).sum(axis=(0,1))
    return out,gross
results=[]
for n in (1,2,4,8):
    with np.load(a.source/f'REFINE_{n}.npz') as data:S={key:data[key] for key in data.files}
    x,xx,zr,W,g,z=project(S['bounds'],n,float(S['nu0']),float(S['dnu']),float(S['z0']))
    zz=float(S['z0']);A=np.stack([np.ones_like(xx)*.3,1e-17*(1+.15*np.tanh(xx/3)),.3*(1+.15*np.tanh(xx/3)),.3*(1+.25*np.exp(-.5*((xx-1.2)/.22)**2)),1e-17*(1+.3*np.tanh(xx/.25)),.3*(1+1e-9*np.tanh(xx/3))],axis=-1)
    u=A*zr[:,:,None];f=np.einsum('inq,iqc->inc',W,u/(1-u))
    old=f/(1+f)/z[:,:,None];new=inverse_be(f,zr,W,z)
    Q=[]
    for j,(i,k) in enumerate(S['pairs']):
        sl=slice(S['offset'][j],S['offset'][j+1]);K=np.einsum('a,aij->ij',S['weight'][sl],S['density'][sl])
        Q.append(((i,k),K))
    oldq,oldgross=eval_action(Q,x,f,old,zz);newq,newgross=eval_action(Q,x,f,new,zz)
    # physical number density from phase weights; angle measure normalized.
    total=8*np.pi*float(S['nu0'])**2*float(S['dnu'])/299792458.**3*np.einsum('in,inc->c',g,f)
    rows=[]
    for j,ref in enumerate(src['direct']):
        q=ref['signal']
        rows.append(dict(name=ref['name'],direct=q,old=float(oldq[j]),aware=float(newq[j]),old_error=abs(oldq[j]-q)/abs(q) if q!=0 else None,aware_error=abs(newq[j]-q)/abs(q) if q!=0 else None,old_per_photon_s=float(abs(oldq[j]-q)/total[j]),aware_per_photon_s=float(abs(newq[j]-q)/total[j])))
    print(n,[(q['name'],q['old_error'],q['aware_error'],q['aware_per_photon_s']) for q in rows],flush=True)
    results.append(dict(subcells=n,nodes=35*(n+1),cases=rows,source_sha256=sha(a.source/f'REFINE_{n}.npz'),thermal_activity_deviation=float(np.max(abs(new[:,:,0]-.3)))))
(a.out/'CLOSURE_RESULTS.json').write_text(json.dumps(results,indent=2,allow_nan=False)+'\n')
