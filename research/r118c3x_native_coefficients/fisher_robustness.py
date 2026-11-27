"""Beam/window/noise robustness of leakage-constrained discrete estimator.
Synthetic covariance only; exact same coordinate pixel integration as C3W.
"""
import numpy as np,json,sys
from pathlib import Path
D=Path(__file__).resolve().parent
src=D.parent/'r118c3u_exact_wedge/pixel_integrated.py'
s=src.read_text().replace('range(2,15)','range(2,23)')
ns={'__file__':str(src),'__name__':'heldout_source'};exec(s,ns)
grid,avg,lift,realbasis=[ns[k] for k in ['grid','avg','lift','realbasis']]
P=D.parent/'r118c3l_reachable_sky'
def run():
 a,b=[np.genfromtxt(P/f'generic_8192_{s}.csv',names=True,delimiter=',') for s in [1,-1]];eps=.0025;B=np.zeros((525,2),complex)
 for l in [3,5,7]:
  def get(r):z=(r['epoch']==1)&(r['ell']==l);return r['Bre'][z]+1j*r['Bim'][z]
  u,v=get(a),get(b);B[l*l-4:(l+1)**2-4]=np.stack([(u+v)/(2*eps**2),(u-v)/(2*eps**3)],axis=1)
 phi=2*np.pi*(np.arange(48)+.5)/48;rows={};ell=np.concatenate([np.full(2*l+1,l) for l in range(2,23)])
 nm=256;cut=20;lo,hi=grid(nm,cut);mu,ph=np.meshgrid((lo+hi)/2,phi,indexing='ij');wt=np.repeat((hi-lo)*2*np.pi/48,48);q=np.sqrt(np.r_[wt,wt]);real=lambda A:np.r_[A.real,A.imag]
 rawp={}
 for width in [5,10,20]:
  aa,bb=avg(lo,hi,cut,width,8);rawp[width]=real(realbasis(lift(bb,9,phi),9,-1j))*q[:,None]
 Y=lift(aa,22,phi);E0=real(realbasis(Y,22,-1))*q[:,None]
 for widths in [(5,10,20),(10,20)]:
  for contrast in [0.,2.,8.]:
   noise=np.sqrt(1+contrast*(.5+.5*np.cos(ph.ravel()))**2+.5*(contrast>0)*(mu.ravel()>0));n=np.r_[noise,noise]
   Q,s,_=np.linalg.svd(np.concatenate([rawp[w] for w in widths],axis=1)*n[:,None],full_matrices=False);Q=Q[:,s>s[0]*1e-6]
   C=Q.T@(E0/n[:,None])
   U,sv,_=np.linalg.svd(C[:,ell<=18],full_matrices=True);sv=np.r_[sv,np.zeros(U.shape[0]-len(sv))]
   A=U[:,sv<=1e-3];leak=float(np.linalg.norm(A.T@C[:,ell>18],2));train=float(np.linalg.norm(A.T@C[:,ell<=18],2))
   for beam in [1.,5.,10.]:
    sig=np.deg2rad(beam)/np.sqrt(8*np.log(2));beamf=np.exp(-ell*(ell+1)*sig**2/2)
    X=real(-1j*Y@(B*beamf[:,None]))*(q/n)[:,None];raw=np.sum(X*X,axis=0);Z=A.T@(Q.T@X);C1=A.T@C
    for amp in [0.,100.,1e5]:
     cl=amp*(2/ell)**2*beamf**2;cov=np.eye(A.shape[1])+(C1*cl)@C1.T
     F=Z.T@np.linalg.solve(cov,Z);assert np.linalg.eigvalsh(F).min()>0
     diag=np.diag(F);marg=1/np.diag(np.linalg.inv(F));key=f'{widths}_{contrast:g}_{beam:g}_{amp:g}'
     rows[key]=dict(widths=list(widths),contrast=contrast,beam_deg=beam,amplitude=amp,rank=A.shape[1],train=train,heldout=leak,Fisher_diag_retention=(diag/raw).tolist(),marginal_retention=(marg/raw).tolist(),corr=float(F[0,1]/np.sqrt(F[0,0]*F[1,1])),weighted_E_cov_norm=float(np.linalg.norm(cov-np.eye(len(cov)),2)))
   print(widths,contrast,'rank',A.shape[1],'train',train,'holdout',leak,flush=True)
 out=dict(rows=rows,scope='256 mu/48 phi coordinate pixels 20deg cut, E ell<=18 train and19..22 heldout; synthetic Cl=amplitude*(2/l)^2 and beam, synthetic noise; diagonal and marginalized Fisher normalized to cut-sky noise-only template norm. No observed likelihood.')
 (D/'FISHER_ROBUSTNESS.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':run()
