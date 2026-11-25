"""Independent full angular x nodal-frequency generator, dense LU.
Pairwise direct barycentric energy deposition, no Rust low-rank gain or
fixed-point iteration. 18 rays x 17 nodes x 9 Cartesian components.
"""
import pathlib,sys,json
import numpy as np
import scipy.linalg as la
from numpy.polynomial.legendre import leggauss
root=pathlib.Path(sys.argv[1]);out=[]
b=np.array([.2,-.1,.05]);g=1/np.sqrt(1-b@b);k=g*g/(1+g);I=np.eye(3);G=3/(8*np.pi)
N3=2.4041138063191885
def load(p):return np.genfromtxt(p,names=True,delimiter='\t')
for scheme in ('backward-euler','sdirk2'):
 name='dense_projected_'+scheme;path=root/name
 ray=load(path/'frequency_rays.tsv');v=load(path/'frequency_nodes.tsv')
 nr=len(ray);nf=len(v)//nr;v=v.reshape(nr,nf);u=v['u'][0];x=np.exp(u)
 e=np.stack([ray['e_x'],ray['e_y'],ray['e_z']],axis=1);w=ray['weight']
 d=g*(1-e@b);ep=(e+(k*(e@b)-g)[:,None]*b)/d[:,None]
 J=I+(k*b+g*ep)[:,:,None]*b[None,None,:]
 inv=I+(k*(-b)+g*e)[:,:,None]*(-b)[None,None,:]
 P=I-ep[:,:,None]*ep[:,None,:];area=w/d**2
 A=G*np.einsum('i,ijk->jk',area,P);val,V=la.eigh(A);N=(V*val**-.5)@V.T
 # Initial hat weights independently evaluated with 32-point quadrature
 z,q=leggauss(32);m=np.zeros(nf)
 for j,(l,r) in enumerate(zip(u,u[1:])):
  y=(l+r)/2+(r-l)/2*z;wq=q*(r-l)/2*np.exp(3*y)/np.expm1(np.exp(y))
  f=(np.exp(y)-x[j])/(x[j+1]-x[j])
  m[j]+=wq@(1-f);m[j+1]+=wq@f
 scale=w/(4*np.pi*N3)
 f=scale[:,None,None,None]*.5*(I-e[:,:,None]*e[:,None,:])[:,None,:,:]*m[None,:,None,None]
 xx=d[:,None]*x[None,:];size=nr*nf*9
 L=np.zeros((size,size))
 for i in range(nr):
  for j in range(nr):
   K=inv[i]@P[i]@N@J[j];block=G*area[i]*d[j]*np.kron(K,K)
   for a,y in enumerate(xx[j]):
    # Direct compare in energy (Rust uses ordered logs + expm1).
    if y<xx[i,0] or y>xx[i,-1]:continue
    h=np.searchsorted(xx[i],y,side='right')-1
    if h==nf-1:dest=[(h,1.)]
    else:
     z=(y-xx[i,h])/(xx[i,h+1]-xx[i,h]);dest=[(h,1-z),(h+1,z)]
    p1=(j*nf+a)*9
    for destnode,ww in dest:
     p0=(i*nf+destnode)*9;L[p0:p0+9,p1:p1+9]+=ww*block
  for j in range(nf):
   p0=(i*nf+j)*9;L[p0:p0+9,p0:p0+9]-=d[i]*np.eye(9)
 h=.15 if scheme=='backward-euler' else (1-1/np.sqrt(2))*.15
 fac=la.lu_factor(np.eye(size)-h*L)
 f=f.ravel()
 for _ in range(2):
  y=la.lu_solve(fac,f)
  f=y if scheme=='backward-euler' else la.lu_solve(fac,f+(1+np.sqrt(2))*(y-f))
 f=f.reshape(nr,nf,3,3)/scale[:,None,None,None]
 names=['xx','yy','zz','xy','xz','yz'];ix=[(0,0),(1,1),(2,2),(0,1),(0,2),(1,2)]
 pred=np.stack([f[:,:,i,j] for i,j in ix],axis=-1)
 actual=np.stack([v['n_'+n] for n in names],axis=-1)
 err=float(np.max(np.abs(actual-pred)));rel=err/float(np.max(np.abs(pred)))
 assert rel<2e-11,(scheme,err,rel)
 a=dict(case=name,dense_unknowns=size,rays=nr,nodes=nf,max_abs=err,max_relative=rel)
 out.append(a);print(a,flush=True)
(root/'DENSE_ORACLE.json').write_text(json.dumps(out,indent=2)+'\n')
