"""Independent dense finite-volume angular-frequency matrix construction.
Union scheme oracle uses full 9*N angular matrix, not six-source reduction.
Projected scheme oracle builds full 9*N_angle*N_freq generator by pairwise
ray-bin intersections (not union sweep), then solves SDIRK/BE by dense LU.
"""
import sys,pathlib,json,math
import numpy as np
import scipy.linalg as la
from numpy.polynomial.legendre import leggauss
root=pathlib.Path(sys.argv[1]);results=[]
beta=np.array([.2,-.1,.05]);g=1/np.sqrt(1-beta@beta);k=g*g/(1+g);I=np.eye(3);gain=3/(8*np.pi)
gamma=1-1/np.sqrt(2)
def w3(a,b):return np.exp(3*a)*np.expm1(3*(b-a))/3
def load(p):return np.genfromtxt(p,names=True,delimiter='\t')
def tableau(fac,x,scheme):
 y=la.lu_solve(fac,x)
 return y if scheme=='backward-euler' else la.lu_solve(fac,x+(1+np.sqrt(2))*(y-x))
for method in ('union','projected'):
 for scheme in ('backward-euler','sdirk2'):
  name=f'dense_{method}_{scheme}';p=root/name;r=load(p/'frequency_rays.tsv')
  out=load(p/'frequency_cells.tsv');nr=len(r);nf=len(out)//nr;out=out.reshape(nr,nf)
  e=np.stack([r['e_x'],r['e_y'],r['e_z']],axis=1);w=r['weight']
  a=out['u_lo'][0];b=out['u_hi'][0];edges=np.r_[a,b[-1]]
  d=g*(1-e@beta);ep=(e+(k*(e@beta)-g)[:,None]*beta)/d[:,None]
  j=I+(k*beta+g*ep)[:,:,None]*beta[None,None,:]
  inv=I+(k*(-beta)+g*e)[:,:,None]*(-beta)[None,None,:]
  P=I-ep[:,:,None]*ep[:,None,:];wu=w/d**2
  A=gain*np.einsum('i,ijk->jk',wu,P);v,Q=la.eigh(A);N=(Q*v**-.5)@Q.T;gp=P@N
  gq,gwt=leggauss(32);u=(a[:,None]+b[:,None])/2+(b-a)[:,None]*gq/2
  init=np.sum((b-a)[:,None]*gwt/2*np.exp(3*u)/np.expm1(np.exp(u)),axis=1)/w3(a,b)
  f=0.5*(I-e[:,:,None]*e[:,None,:])[:,None,:,:]*init[None,:,None,None]
  material_edges=edges[None,:]+np.log(d)[:,None]
  h=.15 if scheme=='backward-euler' else gamma*.15
  if method=='projected':
   size=nr*nf*9;L=np.zeros((size,size))
   for i in range(nr):
    for jray in range(nr):
     K=inv[i]@gp[i]@j[jray];block=gain*wu[jray]*d[i]*np.kron(K,K)
     for ii in range(nf):
      l,rgt=material_edges[i,ii:ii+2]
      jj0=max(0,np.searchsorted(material_edges[jray],l,side='right')-1)
      for jj in range(jj0,nf):
       a0,a1=material_edges[jray,jj:jj+2]
       if a0>=rgt:break
       ll,rr=max(l,a0),min(rgt,a1)
       if rr<=ll:continue
       p0=(i*nf+ii)*9;p1=(jray*nf+jj)*9
       L[p0:p0+9,p1:p1+9]+=w3(ll,rr)/w3(l,rgt)*block
    for ii in range(nf):
     p0=(i*nf+ii)*9;L[p0:p0+9,p0:p0+9]-=d[i]*np.eye(9)
   fac=la.lu_factor(np.eye(size)-h*L)
   for _ in range(2):f=tableau(fac,f.ravel(),scheme).reshape(nr,nf,3,3)
  else:
   size=nr*9;L=np.zeros((size,size))
   for i in range(nr):
    for jray in range(nr):L[i*9:i*9+9,jray*9:jray*9+9]=gain*d[i]*wu[jray]*np.kron(gp[i],gp[i])
    L[i*9:i*9+9,i*9:i*9+9]-=d[i]*np.eye(9)
   fac=la.lu_factor(np.eye(size)-h*L);union=np.unique(material_edges.ravel());l=union[:-1];rr=union[1:]
   indices=np.stack([np.searchsorted(material_edges[i],l,side='right')-1 for i in range(nr)])
   for _ in range(2):
    rest=j[:,None]@f@np.swapaxes(j[:,None],-1,-2)
    inp=np.zeros((nr,len(l),3,3))
    for i in range(nr):
     idx=indices[i];ok=(idx>=0)&(idx<nf);inp[i,ok]=rest[i,idx[ok]]
    result=tableau(fac,inp.transpose(0,2,3,1).reshape(size,len(l)),scheme).reshape(nr,3,3,len(l)).transpose(0,3,1,2)
    result=inv[:,None]@result@np.swapaxes(inv[:,None],-1,-2)
    f=np.zeros_like(f)
    for i in range(nr):
     idx=indices[i];ok=(idx>=0)&(idx<nf);v=idx[ok]
     frac=w3(l[ok],rr[ok])/w3(material_edges[i,v],material_edges[i,v+1])
     np.add.at(f[i],v,frac[:,None,None]*result[i,ok])
  names=['xx','yy','zz','xy','xz','yz'];ix=[(0,0),(1,1),(2,2),(0,1),(0,2),(1,2)]
  actual=np.stack([out['f_'+n] for n in names],axis=-1)
  oracle=np.stack([f[:,:,i,jj] for i,jj in ix],axis=-1)
  err=float(np.max(np.abs(actual-oracle)));rel=err/float(np.max(np.abs(oracle)))
  assert rel<2e-11,(name,err,rel)
  row=dict(case=name,method=method,scheme=scheme,dense_unknowns=size,n_directions=nr,n_bins=nf,max_component_absolute_error=err,max_component_relative_global_scale=rel)
  results.append(row);print(row,flush=True)
(root/'DENSE_ORACLE.json').write_text(json.dumps(results,indent=2)+'\n')
