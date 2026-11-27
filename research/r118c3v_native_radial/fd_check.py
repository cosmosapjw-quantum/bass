"""Independent finite FD stress and positive profile quadrature checks."""
import numpy as np,json
from pathlib import Path
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent;P=D.parent/'r118c3u_exact_wedge'
def window(y):return 1/(1+np.exp(np.clip(-.5*((y-8)/1.4)**2+.5*((y-.7)/1.4)**2,-700,700)))
B=np.zeros((5,3,3));B[0]=np.diag([1,-1,0])/np.sqrt(2);B[1]=np.diag([-1,-1,2])/np.sqrt(6)
for k,(i,j) in enumerate([(0,1),(0,2),(1,2)],2):B[k,i,j]=B[k,j,i]=1/np.sqrt(2)
def stress(C,a,ep,nr,nm):
 y,w=leggauss(nr);y=30*(y+1);w*=30
 mu,g=leggauss(nm);m,ph=np.meshgrid(mu,np.arange(2*nm)*np.pi/nm,indexing='ij');n=np.stack([np.sqrt(1-m*m)*np.cos(ph),np.sqrt(1-m*m)*np.sin(ph),m],axis=-1).reshape(-1,3);g=np.repeat(g/(4*nm),2*nm)
 j=np.einsum('ka,kij->aij',C,B)[1:].reshape(3,2,3,3);v=np.einsum('ni,msij,nj->msn',n,j,n);j=v[:,1,:,None]+(v[:,0]-v[:,1])[:,:,None]*window(y)
 f=1/(1+np.exp(y*np.exp(-ep*j)));E=np.hypot(y,a*np.array([.001,.006,.05])[:,None,None]/.00016763891604963858)
 P=sum((n.T*(g*((f[i]/E[i])@(w*y**4))))@n for i in range(3));rho=np.sum((f*E)@(w*y*y)@g)
 assert f.min()>0 and f.max()<1
 return rho,P
def run():
 rows=[]
 for tag in ['base','best']:
  C=np.load(P/f'{tag}_selected_4096.npz')['control']
  for a in [1/1601,.02,.2]:
   r,p=stress(C,a,.04,192,12)
   for nr,nm in [(48,8),(96,8),(192,8)]:
    q,Q=stress(C,a,.04,nr,nm);rows.append(dict(tag=tag,a=a,nr=nr,nmu=nm,rho_rel=float(abs(q-r)/r),P_rel=float(np.linalg.norm(Q-p)/np.linalg.norm(p))))
 out=dict(rows=rows,scope='direct finite FD quadrature at identity coframe; not native time evolution')
 (D/'R7.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':run()
