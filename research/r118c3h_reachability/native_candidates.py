"""Generate bounded native candidates and analyze actual histories."""
from reachability import *
def controls():
 d=json.loads((D/'PROXY.json').read_text());M=np.array(d['matrix']);A=np.array(d['candidate'])
 Q=np.linalg.svd(initial_span(1.,0,1/(3*np.sqrt(2)),0),full_matrices=False)[0]
 P,pairs=projector();i,j=pairs.T
 B=np.array([Q[i,k]*Q[j,l]-Q[i,l]*Q[j,k] for k,l in combinations(range(4),2)]).T
 _,_,V=np.linalg.svd(P@B,full_matrices=False);target=skew(V[-1],4)
 def blocks(K):
  T,U=schur(K,output='real');idx=sorted([0,2],key=lambda k:-abs(T[k,k+1]))
  U=U[:,[j for k in idx for j in [k,k+1]]];T=U.T@K@U
  return U,np.array([T[0,1],T[2,3]])
 U,m=blocks(M);V,t=blocks(target);Z=Q@V@np.diag(np.ravel(np.c_[np.sign(t/m),np.ones(2)]))@U.T
 z=vector(Z@M@Z.T);rho=np.linalg.norm(P@z)/np.linalg.norm(z);pred=np.sqrt(max(0,1-(2*abs(m[0])+abs(m[1]))**2/(5*np.sum(m*m))))
 assert abs(rho-pred)<1e-8
 out={'orthogonal_fraction':float(rho),'predicted_fraction':float(pred),'orthogonal_wedge':float(np.linalg.norm(z)),'orthogonal':Z.tolist(),'congruence':A.tolist()}
 (D/'CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n')
 for lab,Z in [('orthogonal',Z),('congruence',A)]:
  for amp in [.025,.0125]:
   name=lab+str(int(amp*10000))
   np.savetxt(D/(name+'.controls'),amp*Z.T,fmt='%.17e')
 return out
def analyze(label,amp):
 p=D/(label+'.geom');lines=p.read_text().splitlines();assert lines[-1].startswith('gauss=')
 g=np.genfromtxt(lines[:-1],names=True,delimiter=',');S=np.stack([g[f'S{i}'] for i in range(5)],axis=1)/amp
 clock=np.genfromtxt(D.parent/'r118c2r_multispecies/rei_q256.csv',names=True,delimiter=',');P,_=projector()
 W=memory(g['u'],S,g['h'],clock);v=vector(W)
 y=np.genfromtxt(D/(label+'.csv'),names=True,delimiter=',');m=y['ell']==3
 out=dict(label=label,amplitude=amp,fraction=float(np.linalg.norm(P@v)/np.linalg.norm(v)),normalized_wedge=float(np.linalg.norm(v)),physical_wedge=float(amp**2*np.linalg.norm(v)),native_B3=float(np.linalg.norm(y['re'][m]+1j*y['im'][m])),gauss=float(lines[-1].split('=')[1]),geometry_sha=sha(p))
 (D/(label+'.json')).write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':
 if len(sys.argv)==1:print(controls())
 else:analyze(sys.argv[1],float(sys.argv[2]))
