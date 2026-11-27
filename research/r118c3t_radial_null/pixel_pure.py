"""Pixel midpoint quadrature and finite E calibration for joint pure-B probes.
Actual native B templates, synthetic beam/noise, held-out E11..14.
"""
import numpy as np,json,sys
from pathlib import Path
D=Path(__file__).resolve().parent;P=D.parent/'r118c3l_reachable_sky'
p=D.parent/'r118c3q_controls/pure_window.py';s=p.read_text().replace('range(2,11)','range(2,15)').replace('if l<=7:','if l<=9:')
ns={'__file__':str(p),'__name__':'expanded'};exec(s,ns);fields=ns['fields']
def span(A,tol=1e-10):
 Q,s,_=np.linalg.svd(A,full_matrices=False);k=s>s[0]*tol
 return Q[:,k],s[k]
def run():
 a,b=[np.genfromtxt(P/f'generic_8192_{s}.csv',names=True,delimiter=',') for s in [1,-1]];eps=.0025;B=np.zeros((221,2),complex);sig=np.deg2rad(5)/np.sqrt(8*np.log(2))
 for l in [3,5,7]:
  def get(r):
   z=(r['epoch']==1)&(r['ell']==l);return r['Bre'][z]+1j*r['Bim'][z]
  c,d=get(a),get(b);B[l*l-4:(l+1)**2-4]=np.exp(-l*(l+1)*sig**2/2)*np.stack([(c+d)/(2*eps**2),(c-d)/(2*eps**3)],axis=1)
 rows={}
 for nm in [64,128,256]:
  m=-1+(np.arange(nm)+.5)*2/nm;ph=2*np.pi*(np.arange(48)+.5)/48
  for cut in [20,40]:
   c=np.sin(np.deg2rad(cut));mu,phi=np.meshgrid(m[abs(m)>=c],ph,indexing='ij');mu,phi=mu.ravel(),phi.ravel();wt=np.full(len(mu),4*np.pi/(nm*48))
   noise=np.sqrt(1+2*(.5+.5*np.cos(phi))**2+.5*(mu>0));q=np.sqrt(np.r_[wt,wt]);n=np.r_[noise,noise];real=lambda A:np.r_[A.real,A.imag]
   probes=[]
   for width in [5,10,20]:
    s=np.sin(np.deg2rad(cut+width));t=np.clip((abs(mu)-c)/(s-c),0,1);W=t*t*(3-2*t);W1=np.where(t<1,6*t*(1-t)*np.sign(mu)/(s-c),0.);W2=np.where(t<1,6*(1-2*t)/(s-c)**2,0.)
    Y,Z,O,Pb=fields(mu,phi,W,W1,W2);probes.append(real(Pb)*(q*n)[:,None])
   X=real(-1j*Y@B)*(q/n)[:,None];E=real(Z)*(q/n)[:,None];raw=np.sum(X*X,axis=0);qe,_=span(E[:,:117])
   for lmax in [7,9]:
    A=np.concatenate([v[:,:(lmax+1)**2-4] for v in probes],axis=1)
    Q,s=span(A);raw_train=float(np.linalg.norm(Q.T@E[:,:117],2));raw_hold=float(np.linalg.norm(Q.T@E[:,117:],2));ret=np.sum((Q.T@X)**2,axis=0)/raw
    # Orthogonalize with finite pixelized E training band only. Heldout test
    # checks whether correction of known modes generalizes.
    R,ss=span(A-qe@(qe.T@A));train=float(np.linalg.norm(R.T@E[:,:117],2));hold=float(np.linalg.norm(R.T@E[:,117:],2));ret2=np.sum((R.T@X)**2,axis=0)/raw
    rows[f'{nm}_{cut}_{lmax}']=dict(rank=Q.shape[1],singular_ratio=float(s[-1]/s[0]),retain=ret.tolist(),raw_train=raw_train,raw_holdout=raw_hold,calibrated_retain=ret2.tolist(),calibrated_train=train,calibrated_holdout=hold)
    print(nm,cut,lmax,rows[f'{nm}_{cut}_{lmax}'],flush=True)
 o=dict(rows=rows,scope='uniform mu/phi midpoint pixels; synthetic 5deg beam/nonuniform noise, E<=10 calibrated, held-out E11..14; not Planck HEALPix likelihood')
 (D/'PIXEL_PURE.json').write_text(json.dumps(o,indent=2)+'\n')
if __name__=='__main__':run()
