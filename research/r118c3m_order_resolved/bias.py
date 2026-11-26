"""Early-generated template amplitude bias, with beam and nuisance marginalization."""
import numpy as np,json
from pathlib import Path
from numpy.polynomial.legendre import leggauss
from scipy.special import sph_harm_y
D=Path(__file__).resolve().parent;P=D.parent/'r118c3l_reachable_sky'
def run():
 a,b=[np.genfromtxt(P/f'generic_8192_{s}.csv',names=True,delimiter=',') for s in [1,-1]]
 eps=.0025;rows={}
 for cut in [0,20,40,70]:
  for beam in [0,20]:
   zz,ww=leggauss(80);z0=np.sin(np.deg2rad(cut));X=[];Z=[];W=[]
   sigma=np.deg2rad(beam)/np.sqrt(8*np.log(2))
   for lo,hi in [(-1,-z0),(z0,1)]:
    mu=(lo+hi)/2+(hi-lo)/2*zz;ph=np.arange(160)*np.pi/80;th,phi=np.meshgrid(np.arccos(mu),ph,indexing='ij');v=np.zeros((th.size,2));nuis=[]
    for l in [3,5,7]:
     sel=(a['epoch']==1)&(a['ell']==l);A=a['Bre'][sel]+1j*a['Bim'][sel];B=b['Bre'][sel]+1j*b['Bim'][sel]
     Y=np.stack([sph_harm_y(l,m,th,phi).ravel() for m in range(-l,l+1)],axis=1)
     v+=np.exp(-l*(l+1)*sigma*sigma/2)*(Y@np.stack([(A+B)/(2*eps**2),(A-B)/(2*eps**3)],axis=1)).real
    for l in range(3):
     for m in range(l+1):
      y=sph_harm_y(l,m,th,phi).ravel();nuis.append(y.real)
      if m:nuis.append(y.imag)
    wt=np.repeat(ww*(hi-lo)/2,160)*np.pi/80/(1+4*(.5+.5*np.cos(phi.ravel()))**2)
    X.append(v);Z.append(np.stack(nuis,axis=1));W.append(wt)
   w=np.sqrt(np.concatenate(W));X=np.concatenate(X)*w[:,None];Z=np.concatenate(Z)*w[:,None]
   Q,_=np.linalg.qr(Z);R=X-Q@(Q.T@X);F=R.T@R;N=np.sqrt(F.diagonal());G=F/np.outer(N,N)
   bias=eps*F[0,1]/F[0,0];data=R@np.array([eps**2,eps**3])
   fit=R[:,0]@data/F[0,0];assert abs(fit/eps**2-1-bias)<1e-12
   # Scale-independent standard-error inflation relative to unmasked reference with same beam.
   rows[f'{cut}_{beam}']=dict(fractional_bias=float(bias),cosine=float(G[0,1]),condition=float(np.linalg.cond(G)),sigma_unit=np.sqrt(np.diag(np.linalg.inv(F))).tolist())
 for name,r in rows.items():
  beam=name.split('_')[1];r['sigma_inflation']=(np.array(r['sigma_unit'])/rows[f'0_{beam}']['sigma_unit']).tolist()
 (D/'BIAS.json').write_text(json.dumps(dict(rows=rows,scope='early generated native generic sky, l3/5/7, synthetic mask/beam/noise, nuisance l<=2; unit white noise precision, not observed covariance'),indent=2)+'\n');print(rows)
if __name__=='__main__':run()
