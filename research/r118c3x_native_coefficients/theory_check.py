import numpy as np,json
from pathlib import Path
D=Path(__file__).resolve().parent
def run():
 rng=np.random.default_rng(31);x=np.array([.02,.04,.06])**2;scale=max(x);A=np.vander(x/scale,3,increasing=True)
 p=(rng.normal(size=(3,7))+1j*rng.normal(size=(3,7)))*np.array([1e-8,1e-7,1e-6])[:,None]
 Y=A@(p*np.array([1,scale,scale**2])[:,None]);q=np.linalg.solve(A,Y)/np.array([1,scale,scale**2])[:,None]
 err=np.linalg.norm(q-p,axis=1)/np.linalg.norm(p,axis=1);assert max(err)<1e-7
 lin=np.linalg.solve(np.vander(x[:2],2,increasing=True),Y[:2]);want=np.array([p[0]-x[0]*x[1]*p[2],p[1]+(x[0]+x[1])*p[2]])
 assert np.max(abs(lin-want))<1e-18
 out=dict(condition=float(np.linalg.cond(A)),relative=err.tolist(),linear_bias_abs=float(np.max(abs(lin-want))),scope='manufactured complex polynomial extraction; no physical coefficient claim')
 (D/'R7.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':run()
