import numpy as np,json,hashlib
from pathlib import Path
from scipy.integrate import solve_ivp
D=Path(__file__).resolve().parent;P=D.parent/'r118c3c_memory_kernel/WEDGE.json';G=np.array(json.loads(P.read_text())['gram']);P3=2*G
ne=np.genfromtxt(D.parent/'r118c2r_multispecies/rei_q256.csv',names=True,delimiter=',')
pairs=np.array([(i,j) for i in range(5) for j in range(i+1,5)]);ii,jj=pairs.T
rows=[]
for name,eps in [('m025',.025),('m05',.05),('angle08',.025),('angle15',.025),('m025fine',.025)]:
 p=D/(name+'.geom');lines=p.read_text().splitlines();r=np.genfromtxt(lines[:-1],delimiter=',',names=True);u=r['u'];S=np.stack([r[f'S{i}'] for i in range(5)],axis=1)/eps
 # Expected leading linear span of initial shear plus both species memory shapes.
 A=np.stack([S[0],np.array([0,1,0,0,0]),np.array([0,0,.6,.8,0])],axis=1);U,s,_=np.linalg.svd(A,full_matrices=False);U=U[:,s>1e-10];proj=U@U.T
 def solve(P):
    def rhs(t,y):
      ss=P@np.array([np.interp(t,u,S[:,j]) for j in range(5)])
      k=299792458*6.6524587051e-29/2.1842852410855023e-18*np.interp(t,ne['u'],ne['ne_m3'])/np.interp(t,u,r['h'])
      a,p,w=y[:5],y[5:10],y[10:]
      return np.r_[-4*ss-k*(.9*a+.4*p),-k*(.15*a+.4*p),ss[ii]*p[jj]-ss[jj]*p[ii]-k*w]
    z=solve_ivp(rhs,(u[0],u[-1]),np.zeros(20),method='DOP853',rtol=1e-11,atol=1e-18,max_step=(u[-1]-u[0])/1024);assert z.success;return z.y[10:,-1]
 w=solve(np.eye(5));v=solve(proj);ratio=np.linalg.norm(P3@w)/np.linalg.norm(w);ratio0=np.linalg.norm(P3@v)/np.linalg.norm(v)
 assert ratio0>=1/np.sqrt(5)-1e-8
 z=np.genfromtxt(D/(name+'.csv'),names=True,delimiter=',');m=z['ell']==3;norm=np.linalg.norm(z['re'][m]+1j*z['im'][m])
 coeff=16/np.sqrt(378)*np.linalg.norm(P3@w)
 row=dict(name=name,eps=eps,rank_span=U.shape[1],out_of_linear_span=float(np.linalg.norm(S-S@proj)/np.linalg.norm(S)),S_singular=np.linalg.svd(S,compute_uv=False).tolist(),wedge_norm=float(np.linalg.norm(w)),projected_fraction=float(ratio),projected_span_fraction=float(ratio0),quadratic_norm=coeff,native_B3=float(norm),relative_to_quadratic=float(norm/(eps**2*coeff)-1),gauss=float(lines[-1].split('=')[1]),geometry_sha=hashlib.sha256(p.read_bytes()).hexdigest())
 rows.append(row);print(row,flush=True)
(D/'PHYSICAL_WEDGE.json').write_text(json.dumps(dict(status='SCOPED_PHYSICAL_MULTI_STF_WEDGE',rows=rows),indent=2)+'\n')
