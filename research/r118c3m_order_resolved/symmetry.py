"""SO(2) rotation of STF controls; analytic cubic extraction checks."""
import numpy as np,json
from pathlib import Path
D=Path(__file__).resolve().parent
B=np.zeros((5,3,3));B[0]=np.diag([1,-1,0])/np.sqrt(2);B[1]=np.diag([-1,-1,2])/np.sqrt(6)
for k,(i,j) in enumerate([(0,1),(0,2),(1,2)],2):B[k,i,j]=B[k,j,i]=1/np.sqrt(2)
def rotation(phi):
 c,s=np.cos(phi),np.sin(phi);R=np.array([[c,-s,0],[s,c,0],[0,0,1.]])
 return np.einsum('aij,ik,bkl,jl->ab',B,R,B,R)
def run():
 phi=np.pi/3;U=rotation(phi);assert np.linalg.norm(U.T@U-np.eye(5))<1e-14
 v=np.array([.3,.2,.5,-.1,.4]);z=U@v
 def h(v):
  a=v[0]-1j*v[2];b=-v[3]+1j*v[4];return np.array([a.conjugate(),-b.conjugate(),np.sqrt(2)*v[1],b,a])
 err=np.max(abs(h(z)-h(v)*np.exp(-1j*np.arange(-2,3)*phi)));assert err<1e-14
 a,b,c=1.,2.,3.;f=lambda e:a*e**3+b*e**5+c*e**7
 rows=[]
 for e in [.1,.05,.025]:
  odd=f(e)/e**3;rr=(4*f(e/2)/(e/2)**3-odd)/3
  rows.append([e,abs(odd-a),abs(rr-a)])
 (D/'R7.json').write_text(json.dumps(dict(rotation_error=float(err),richardson=rows),indent=2)+'\n');print(rows)
if __name__=='__main__':run()
