"""Conditional collisionless secondary radiation moments on actual live history.
Reconstruct stage birth totals from the original isotropic reservoir updates.
Signed CMB correction is a perturbation, never a separate positive distribution.
"""
import numpy as np,json,hashlib
from pathlib import Path
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent;p=Path('/home/cosmosapjw/Downloads/bass_r118c2x_refined/history.csv')
r=np.genfromtxt(p,names=True,delimiter=',')
F=np.stack([r[f'F{i}{j}'] for i in range(3) for j in range(3)],axis=1).reshape(-1,3,3)
a=r['a'];am=np.sqrt(a[1:]*a[:-1]);fm=(F[1:]+F[:-1])/2;fm/=np.cbrt(np.linalg.det(fm))[:,None,None]
# C2W bridge used isotropic redshift plus midpoint source.
source=np.stack([(r[k][1:]-a[:-1]/a[1:]*r[k][:-1])/(am/a[1:]) for k in ('escape','cmb')],axis=1)
assert min(source[:,0])>=-1e-20
rows=[]
for nt,np0 in ((8,16),(16,32),(32,64)):
 x,w=leggauss(nt);ph=2*np.pi*np.arange(np0)/np0;mu,t=np.meshgrid(x,ph,indexing='ij')
 n=np.stack([np.sqrt(1-mu*mu)*np.cos(t),np.sqrt(1-mu*mu)*np.sin(t),mu],axis=-1).reshape(-1,3);ww=np.repeat(w/2/np0,np0)
 inv=np.linalg.inv(F[-1]).T
 U=np.zeros(2);P=np.zeros((2,3,3));flux=np.zeros((2,3))
 for j in range(len(am)):
    mat=am[j]/a[-1]*inv@fm[j].T
    v=n@mat.T;e=np.linalg.norm(v,axis=1)
    uj=ww@e;pj=np.einsum('a,ai,aj->ij',ww/e,v,v)
    U+=source[j]*uj;P+=source[j,:,None,None]*pj;flux+=source[j,:,None]*(ww@v)
 iso=np.array([r[k][-1] for k in ('escape','cmb')]);pi=P-U[:,None,None]*np.eye(3)/3
 assert np.max(abs(np.trace(P,axis1=1,axis2=2)-U))<1e-12*max(abs(U))
 row=dict(nmu=nt,nphi=np0,U=U.tolist(),isotropic=iso.tolist(),relative_U=((U-iso)/np.maximum(abs(iso),1e-300)).tolist(),pressure=P.tolist(),pi_norm=np.linalg.norm(pi,axis=(1,2)).tolist(),flux=flux.tolist(),total_pi_norm=float(np.linalg.norm(pi.sum(axis=0))))
 rows.append(row);print(row,flush=True)
out=dict(status='SCOPED_SECONDARY_COLLISIONLESS_MOMENT_ORACLE',source_sha=hashlib.sha256(p.read_bytes()).hexdigest(),rows=rows,scope='actual live geometry and reconstructed stage birth energy; midpoint F interpolated, no absorption or scattering, signed CMB perturbation not physical distribution, no feedback rerun')
(D/'SECONDARY.json').write_text(json.dumps(out,indent=2)+'\n')
