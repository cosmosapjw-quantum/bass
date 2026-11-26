"""Beam-weighted omitted cubic bias on pinned parity templates, synthetic covariance."""
import sys,json,numpy as np
from pathlib import Path
from scipy.special import sph_harm_y
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
P=D.parent/'r118c3i_temporal_rank'
def coeff(label,l):
 a=np.genfromtxt(P/(label+'.csv'),names=True,delimiter=',');z=a['ell']==l
 return a['re'][z]+1j*a['im'][z]
def run():
 eps=.003125;rows={}
 for cut in [0,20,40]:
  for beam_deg in [0,10,30]:
   z,w=leggauss(64);mu0=np.sin(np.deg2rad(cut));X=[];Z=[];W=[]
   sigma=np.deg2rad(beam_deg)/np.sqrt(8*np.log(2))
   for lo,hi in [(-1,-mu0),(mu0,1)]:
    mu=(lo+hi)/2+(hi-lo)/2*z;ph=np.arange(128)*np.pi/64;th,phi=np.meshgrid(np.arccos(mu),ph,indexing='ij')
    v=np.zeros((th.size,2));nuis=[]
    for l in [3,5,7]:
     Y=np.stack([sph_harm_y(l,m,th,phi).ravel() for m in range(-l,l+1)],axis=1)
     a=coeff('parity_1',l);b=coeff('parity_-1',l);e=(a+b)/(2*eps**2);o=(a-b)/(2*eps**3)
     v+=np.exp(-l*(l+1)*sigma*sigma/2)*(Y@np.stack([e,o],axis=1)).real
    for l in range(3):
     for m in range(l+1):
      y=sph_harm_y(l,m,th,phi).ravel();nuis.append(y.real)
      if m:nuis.append(y.imag)
    wt=np.repeat(w*(hi-lo)/2,128)*np.pi/64/(1+4*(.5+.5*np.cos(phi.ravel()))**2)
    X.append(v);Z.append(np.stack(nuis,axis=1));W.append(wt)
   x=np.concatenate(X)*np.sqrt(np.concatenate(W))[:,None];zz=np.concatenate(Z)*np.sqrt(np.concatenate(W))[:,None];Q,_=np.linalg.qr(zz);R=x-Q@(Q.T@x);F=R.T@R
   # Actual amplitudes for common eps: even eps², odd eps³. Omitted-variable fractional bias on even amplitude.
   pred=eps*F[0,1]/F[0,0];d=R@np.array([eps**2,eps**3]);fit=R[:,0]@d/F[0,0];assert abs(fit/eps**2-1-pred)<1e-12
   rows[f'{cut}_{beam_deg}']=dict(fractional_bias=float(pred),cosine=float(F[0,1]/np.sqrt(F[0,0]*F[1,1])),condition=float(np.linalg.cond(F/np.sqrt(np.outer(F.diagonal(),F.diagonal())))))
 (D/'BIAS.json').write_text(json.dumps(dict(rows=rows,scope='native multipole templates l3/5/7, synthetic beam, mask and diagonal noise, no measured likelihood'),indent=2)+'\n')
 print(rows)
if __name__=='__main__':run()
