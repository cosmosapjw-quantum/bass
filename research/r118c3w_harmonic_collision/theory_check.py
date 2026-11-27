import numpy as np,json
from scipy.linalg import expm
from pathlib import Path
D=Path(__file__).resolve().parent
def run():
 d=np.sqrt(8/3);C=np.array([[-.9,.4/d],[.15*d,-.4]])
 rows=[]
 for t in [0,1e-12,1e-8,.001,.1,1,10,100]:
  M=np.exp(-t)*np.eye(2)+np.exp(-.3*t)*(-np.expm1(-.7*t))*(C+np.eye(2))/.7
  err=np.linalg.norm(M-expm(t*C));assert err<1e-14
  rows.append(dict(tau=t,error=float(err)))
 # Native sparse generator parity leakage for Bianchi I: actual exported entries.
 a=np.genfromtxt(D.parent/'r118c3o_analytic_s3/generator.csv',names=True,delimiter=',');M=81
 # form real-complex I/E/B basis transform and check I/E even ell, B odd ell.
 n=3*M;U=np.zeros((n,n),complex);V=U.copy();U[:M,:M]=V[:M,:M]=np.eye(M)
 I=np.eye(M);U[M:2*M,M:2*M]=-I;U[M:2*M,2*M:]=-1j*I;U[2*M:,M:2*M]=-I;U[2*M:,2*M:]=1j*I
 V[M:2*M,M:2*M]=V[M:2*M,2*M:]=-.5*I;V[2*M:,M:2*M]=.5j*I;V[2*M:,2*M:]=-.5j*I
 ell=np.floor(np.sqrt(np.arange(M))).astype(int);ok=np.r_[ell%2==0,(ell%2==0)&(ell>=2),(ell%2==1)&(ell>=2)]
 err=[]
 for k in range(5):
  q=a[a['axis']==k];A=np.zeros((n,n),complex);A[q['row'].astype(int),q['col'].astype(int)]=q['re']+1j*q['im'];T=V@A@U;err.append(float(np.linalg.norm(T[np.ix_(~ok,ok)])/np.linalg.norm(T[np.ix_(ok,ok)])))
 out=dict(semigroup=rows,parity_relative=err,scope='analytic collision and actual exported native Bianchi I streaming generator, no time trajectory')
 assert max(err)<1e-12
 (D/'R7.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':run()
