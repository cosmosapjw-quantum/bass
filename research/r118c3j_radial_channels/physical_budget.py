"""Physical FD-weighted control budget rather than bare coefficient norm."""
import numpy as np,json
from pathlib import Path
from numpy.polynomial.legendre import leggauss
from scipy.linalg import block_diag
from radial import windows,solve
from optimize import construct,evaluate
D=Path(__file__).resolve().parent
def metric(nw,nr=256):
 y,w=leggauss(nr);y=30*(1+y);w=30*w;f=1/(1+np.exp(y));wt=w*y*y*f;wt/=wt.sum();V=windows(y,nw);G=(V*wt)@V.T/3
 return block_diag(np.ones((1,1)),G,G,G)
def check(a):
 M=np.array(a['M']);G=metric(a['nw']);e,U=np.linalg.eigh(G);assert min(e)>0
 H=(U/np.sqrt(e))@U.T;W=H@M@H;W=(W-W.T)/2;sv=np.linalg.svd(W,compute_uv=False);A,_=construct(W);A=A@H
 p=evaluate(M,A);norm=np.linalg.norm(A@((U*np.sqrt(e))@U.T),2);assert norm<=1+1e-9
 # Peak per-species tensor norm under unit whitened operator budget (not amplitude safety).
 y=np.linspace(0,60,4001);V=windows(y,a['nw']);peak=max(np.linalg.norm(A[:,1+i*a['nw']:1+(i+1)*a['nw']]@V,axis=0).max() for i in range(3))
 return dict(nw=a['nw'],metric_condition=float(e[-1]/e[0]),whitened_ratio=float(sv[2]/sv[0]),whitened_bound=float(np.sqrt(5)*sv[2]),constructed=p,physical_operator_norm=float(norm),pointwise_peak=float(peak),A=A.tolist())
def main():
 p=json.loads((D/'RADIAL.json').read_text())['cases'];rows=[check(a) for a in p[-3:]]
 for a in rows:print({k:v for k,v in a.items() if k!='A'})
 (D/'PHYSICAL_BUDGET.json').write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':main()
