"""Finite-band photon transport with exact source phase measure.
Explicit model: dilute, factorized angle-averaged frequency diffusion +
unpolarized elastic dipole redistribution; NOT full correlated R_II.
"""
from pathlib import Path
import sys,math
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.linalg import eigh
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'research/typeii_lyman_transfer_20261116'))
import line_transfer as lt
H,C,KB,MH,NU0,ALYA=lt.H,lt.C,lt.KB,lt.MH,lt.NU0,lt.ALYA

def check(ok,msg):
 if not bool(ok):raise RuntimeError(msg)

def sphere_rule(nmu,nphi):
 if not isinstance(nmu,int) or not isinstance(nphi,int) or nmu<2 or nphi<4:raise ValueError('positive resolved angular quadrature')
 mu,w=leggauss(nmu);phi=2*np.pi*(np.arange(nphi)+.5)/nphi
 n=np.stack(np.broadcast_arrays(np.sqrt(1-mu[:,None]**2)*np.cos(phi),np.sqrt(1-mu[:,None]**2)*np.sin(phi),mu[:,None]),axis=-1).reshape(-1,3)
 return n,np.repeat(w,nphi)*2*np.pi/nphi

def atom_directions(n,beta):
 n=np.asarray(n,float)
 if n.ndim!=2 or n.shape[1]!=3 or not np.isfinite(n).all() or np.max(abs(np.linalg.norm(n,axis=1)-1))>5e-10 or not np.isfinite(beta) or abs(beta)>=1:raise ValueError('unit directions and subluminal tilt required')
 G=1/np.sqrt(1-beta*beta);q=1-beta*n[:,1];D=G*q
 a=n/D[:,None];a[:,1]=(n[:,1]-beta)/q
 return a,D

def mode_capacity(edges):
 e=np.asarray(edges,float)
 if e.ndim!=1 or len(e)<3 or not np.isfinite(e).all() or min(e)<=0 or min(np.diff(e))<=0:raise ValueError('positive increasing frequency edges')
 return 2/(3*C**3)*np.diff(e)*(e[1:]**2+e[:-1]*e[1:]+e[:-1]**2)

def capacities(edges,wn,D,V):
 g=mode_capacity(edges);w=np.asarray(wn,float);D=np.asarray(D,float)
 if w.ndim!=1 or w.shape!=D.shape or not np.isfinite(np.r_[w,D,V]).all() or min(w)<=0 or min(D)<=0 or V<=0:raise ValueError('positive geometric weights, Doppler, volume')
 return V*w[:,None]/D[:,None]**3*g[None,:]

def pair_flux(fi,fj,delta):
 if not np.isfinite([fi,fj,delta]).all() or min(fi,fj)<0 or abs(delta)>100:raise ValueError('finite dilute or Bose occupations and energy difference')
 return fi*(1+fj)-np.exp(delta)*fj*(1+fi)

def bernoulli(x):
 a=np.asarray(x,float);out=np.empty_like(a);small=abs(a)<1e-5
 out[small]=1-a[small]/2+a[small]**2/12-a[small]**4/720
 out[~small]=a[~small]/np.expm1(a[~small]);return out

def angular_generator(ne,wa,D):
 n=np.asarray(ne,float);w=np.asarray(wa,float);D=np.asarray(D,float)
 if n.ndim!=2 or n.shape[1]!=3 or w.shape!=(len(n),) or D.shape!=w.shape or not np.isfinite(np.r_[n.ravel(),w,D]).all() or min(w)<=0 or min(D)<=0 or max(abs(np.linalg.norm(n,axis=1)-1))>5e-10:raise ValueError('invalid angular generator inputs')
 K=3/(16*np.pi)*(1+(n@n.T)**2)
 Q=w[:,None]*D[None,:]*K;np.fill_diagonal(Q,0.);np.fill_diagonal(Q,-Q.sum(axis=0))
 pi=w/D;pi/=sum(pi)
 return Q,pi

def angular_evolve(Q,pi,N,optical_times,return_audit=False):
 Q=np.asarray(Q,float);p=np.asarray(pi,float);x=np.asarray(N,float);s=np.asarray(optical_times,float)
 if x.ndim!=2 or x.shape[0]!=len(p) or s.shape!=(x.shape[1],) or Q.shape!=(len(p),len(p)) or not np.isfinite(np.r_[Q.ravel(),p,x.ravel(),s]).all() or min(p)<=0 or x.min()<0 or min(s)<0:raise ValueError('invalid angular state/time')
 root=np.sqrt(p);S=Q*root[None,:]/root[:,None]
 check(np.max(abs(S-S.T))<3e-12,'angular reciprocity')
 lam,U=eigh((S+S.T)/2)
 check(abs(lam[-1])<2e-12 and lam[-2]<0,'connected angular equilibrium mode')
 # Analytic stationary mode avoids exponentially amplifying its roundoff eigenvalue.
 U=U[:,:-1];lam=lam[:-1];total=x.sum(axis=0)
 out=p[:,None]*total+root[:,None]*(U@(np.exp(lam[:,None]*s[None,:])*(U.T@(x/root[:,None]))))
 out[:,s==0]=x[:,s==0]
 tolerance=2e-13*np.maximum(total,1e-300)
 check(np.all(out.min(axis=0)>=-tolerance),'angular semigroup positivity defect')
 cleanup=float(-np.minimum(out,0).sum());out=np.maximum(out,0.)
 mass=out.sum(axis=0);mask=total>0
 check(np.all(abs(mass-total)<=3e-12*np.maximum(total,1e-300)),'angular semigroup count defect')
 out[:,mask]*=(total[mask]/mass[mask])[None,:]
 audit={'roundoff_clipped_mass':cleanup,'preprojection_number_gap':float(max(abs(mass-total)))}
 return (out,audit) if return_audit else out

def frequency_model(edges,T,rate_cent,rate_face,pdestroy,clock=1.,absorbing=True,recoil=True):
 e=np.asarray(edges,float);g=mode_capacity(e);nu=(e[:-1]+e[1:])/2
 rc=np.asarray(rate_cent,float);rf=np.asarray(rate_face,float)
 if rc.shape!=g.shape or rf.shape!=e.shape or not np.isfinite(np.r_[T,rc,rf,pdestroy,clock]).all() or T<=0 or min(rc)<0 or min(rf)<0 or not 0<=pdestroy<=1 or clock<=0:raise ValueError('bad redistribution rates or state')
 dnu=NU0*np.sqrt(2*KB*T/(MH*C*C));diff=.5*dnu*dnu*(1-pdestroy)*rf
 W=2*e**2/C**3
 delta=H*np.diff(nu)/(KB*T) if recoil else np.zeros(len(nu)-1)
 a=clock*W[1:-1]*diff[1:-1]/np.diff(nu)*bernoulli(delta)
 up=a/g[:-1];down=a*np.exp(delta)/g[1:]
 red=blue=0.
 if absorbing:
  dl=H*(nu[0]-e[0])/(KB*T) if recoil else 0.
  dr=H*(e[-1]-nu[-1])/(KB*T) if recoil else 0.
  red=float(clock*W[0]*diff[0]/(nu[0]-e[0])*bernoulli(np.array(dl))*np.exp(dl)/g[0])
  blue=float(clock*W[-1]*diff[-1]/(e[-1]-nu[-1])*bernoulli(np.array(dr))/g[-1])
 kill=clock*pdestroy*rc
 loss=kill.copy();loss[:-1]+=up;loss[1:]+=down;loss[0]+=red;loss[-1]+=blue
 pi=g*np.exp(-H*(nu-nu[len(nu)//2])/(KB*T)) if recoil else g.copy()
 return {'up':up,'down':down,'loss':loss,'kill':kill,'red':red,'blue':blue,'nu':nu,'edges':e,'g':g,'pi':pi}

def frequency_step(m,N,dt):
 x=np.asarray(N,float);a=np.asarray(m['up'],np.longdouble);b=np.asarray(m['down'],np.longdouble)
 if x.shape!=m['loss'].shape or not np.isfinite(np.r_[x,dt]).all() or min(x)<0 or dt<0:raise ValueError('positive frequency populations and time')
 if dt==0:return {'N':x.copy(),'red':0.,'blue':0.,'death':0.,'heat_J':0.,'number_residual':0.,'energy_residual_J':0.}
 t=np.longdouble(dt);diag=1+t*np.asarray(m['loss'],np.longdouble);lo=-t*a;hi=-t*b
 rhs=x.astype(np.longdouble).copy();diag=diag.copy()
 for i in range(1,len(x)):
  v=lo[i-1]/diag[i-1];diag[i]-=v*hi[i-1];rhs[i]-=v*rhs[i-1]
 check(np.min(diag)>0,'implicit M-matrix pivot')
 y=np.empty_like(rhs);y[-1]=rhs[-1]/diag[-1]
 for i in range(len(x)-2,-1,-1):y[i]=(rhs[i]-hi[i]*y[i+1])/diag[i]
 check(np.min(y)>=0 and np.isfinite(y).all(),'implicit frequency positivity')
 red=t*m['red']*y[0];blue=t*m['blue']*y[-1];deathbins=t*np.asarray(m['kill'],np.longdouble)*y;death=deathbins.sum()
 flux=t*(a*y[:-1]-b*y[1:]);E=np.asarray(H*m['nu'],np.longdouble);El=np.longdouble(H*m['edges'][0]);Er=np.longdouble(H*m['edges'][-1])
 heat=-(np.diff(E)@flux+(El-E[0])*red+(Er-E[-1])*blue)
 energy=E@y+El*red+Er*blue+E@deathbins+heat-E@x.astype(np.longdouble)
 count=y.sum()+red+blue+death-x.sum(dtype=np.longdouble)
 return {'N':np.array(y,float),'red':float(red),'blue':float(blue),'death':float(death),'death_energy_J':float(E@deathbins),'heat_J':float(heat),'number_residual':float(count),'energy_residual_J':float(energy)}

def remap_details(N,edges,scale):
 x=np.asarray(N,float);e=np.asarray(edges,float);s=np.asarray(scale,float);mode_capacity(e)
 if x.ndim!=2 or x.shape[1]!=len(e)-1 or s.shape!=(x.shape[0],) or not np.isfinite(np.r_[x.ravel(),s]).all() or x.min()<0 or min(s)<=0:raise ValueError('invalid characteristic remap')
 out=np.empty_like(x);red=np.zeros(len(x));blue=np.zeros(len(x))
 for j in range(len(x)):
  c=np.r_[0.,np.cumsum(x[j])];mapped=np.interp(e/s[j],e,c,left=0.,right=c[-1])
  out[j]=np.diff(mapped);red[j]=mapped[0];blue[j]=c[-1]-mapped[-1]
 return out,red,blue

def redshift_remap(N,edges,scale):
 x,r,b=remap_details(N,edges,scale);return x,float(sum(r)),float(sum(b))
