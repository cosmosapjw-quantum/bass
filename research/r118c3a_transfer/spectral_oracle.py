"""Independent physical-emission-angle grey free-free spectrum and absorption diagnostic."""
import sys,hashlib,json
from pathlib import Path
import numpy as np
from scipy.linalg import expm
from scipy.special import digamma
from scipy.integrate import quad
from scipy.constants import h,c,e,k
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent;H=Path('/home/cosmosapjw/Downloads')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
edges=np.array([0.,1e-6,1e-5,1e-4,3e-4,1e-3,3e-3,1e-2,3e-2,.1,.3,1.,np.inf]);kb=k/e
def mat(v):
 x,y,z,p,q=v;rr=1/np.sqrt(2);t=1/np.sqrt(6)
 return np.array([[rr*x-t*y,rr*z,rr*p],[rr*z,-rr*x-t*y,rr*q],[rr*p,rr*q,2*t*y]])
def load(name):
 root=H/('bass_r118c3a_'+name);r=np.genfromtxt(root/'history.csv',names=True,delimiter=',');s=np.genfromtxt(root/'secondary_spectrum.csv',names=True,delimiter=',')
 assert len(r)==len(s) and np.array_equal(r['a'],s['a'])
 return root,r,s
def analyze(name,parts):
 roots=[];hs=[];ss=[]
 for j,n in enumerate(parts):
    root,r,s=load(n);roots.append(root);hs.append(r if j==0 else r[1:]);ss.append(s if j==0 else s[1:])
 r=np.concatenate(hs);s=np.concatenate(ss)
 a=r['a'];du=np.log(a[1:]/a[:-1]);am=a[:-1]*np.exp(du/2)
 F=np.stack([r[f'F{i}{j}'] for i in range(3) for j in range(3)],axis=1).reshape(-1,3,3);S=np.stack([r[f'S{i}'] for i in range(5)],axis=1)
 fm=np.array([expm(mat(v)*t/2)@f for v,t,f in zip(S,du,F)])
 birth=np.diff(s['FF_birth']);tm=np.diff(s['FF_T_moment'])/birth;assert min(birth)>0 and min(tm)>0
 U=np.array([s[f'bin{i}'][-1] for i in range(12)]);rows=[]
 for nt,np0 in ((8,16),(16,32)):
    mu,w=leggauss(nt);phi=2*np.pi*np.arange(np0)/np0;M,P=np.meshgrid(mu,phi,indexing='ij')
    n=np.stack([np.sqrt(1-M*M)*np.cos(P),np.sqrt(1-M*M)*np.sin(P),M],axis=-1).reshape(-1,3);ww=np.repeat(w/2/np0,np0)
    bins=np.zeros(12);inv=np.linalg.inv(F[-1]).T
    for b,t,aa,f in zip(birth,tm,am,fm):
        # Each physical birth-frame unit direction gives reference q-vector.
        q=n@f*(aa/a[0]);qn=np.linalg.norm(q,axis=1)
        # final / birth photon energy ratio, from same canonical covector.
        scale=np.linalg.norm(q@inv.T,axis=1)*a[0]/a[-1]
        ex=edges[None,:]/(qn[:,None]*kb*t)
        fr=np.exp(-ex[:,:-1])*(-np.expm1(-(ex[:,1:]-ex[:,:-1])))
        bins+=b*np.sum((ww*scale)[:,None]*fr,axis=0)
    er=float(np.sum(abs(bins-U))/U.sum());rows.append(dict(nmu=nt,nphi=np0,bins=bins.tolist(),total_relative=float(abs(bins.sum()/U.sum()-1)),bin_l1=er))
    assert er<1e-8
 # Grey Kirchhoff absorption in an isotropic blackbody, not fed back.
 tc=2.7255/am;ratio=tc/tm;absorb=ratio*(digamma(1+ratio)+np.euler_gamma)
 for q in (.1,1.,10.):
    v=quad(lambda x:(-np.expm1(-q*x))*np.exp(-x)/(-np.expm1(-x)),0,100,epsabs=1e-11)[0]*q
    assert abs(v-q*(digamma(1+q)+np.euler_gamma))<1e-10
 # isotropic redshift factor for this conditional CMB comparison.
 red=am/a[-1]
 net=float(np.sum(birth*(1-absorb)*red));ab=float(np.sum(birth*absorb*red));em=float(np.sum(birth*red))
 # Optical depth at fixed dimensionless CMB frequency; H density from BB_U,
 # which is independently defined by Planck energy density / nH.
 arad=8*np.pi**5*k**4/(15*h**3*c**3);nh=arad*tc**4/e/((s['BB_U'][:-1]+s['BB_U'][1:])/2)
 tau={}
 for xg in (.01,.1,1.,10.):
    E=xg*kb*tc
    phase=8*np.pi*(E*e/(h*c))**3
    tau[str(xg)]=float(np.sum(nh*birth/(kb*tm)*(-np.expm1(-E/(kb*tm)))/phase))
 out=dict(name=name,inputs={str(p/f):sha(p/f) for p in roots for f in ('history.csv','secondary_spectrum.csv')},bins=U.tolist(),rows=rows,gray_absorption=dict(emission_redshifted=em,absorption_redshifted=ab,net_redshifted=net,absorption_over_emission=ab/em,initial_absorption_ratio=float(absorb[0]),terminal_absorption_ratio=float(absorb[-1]),tau=tau,scope='isotropic Planck bath; gray Gaunt; conditional, not gas feedback or observed net spectrum'))
 print(name,'bins',rows[-1]['bin_l1'],'absorption',out['gray_absorption'],flush=True)
 return out
def Y(x):
 ex=np.exp(-x);return x*ex/(-np.expm1(-x))**2*(x*(1+ex)/(1-ex)-4)
mom2=quad(lambda x:x*x*Y(x),1e-10,100,epsabs=1e-11)[0]
mom3=quad(lambda x:x**3*Y(x),1e-10,100,epsabs=1e-10)[0]
assert abs(mom2)<1e-8 and abs(mom3/(np.pi**4/15)-4)<1e-10
parts=sys.argv[1:] or ['long']
out=dict(status='SCOPED_GRAY_FF_AND_Y_MOMENTS',short=analyze('short',['short']),long=analyze('long',parts),Y_number=mom2,Y_energy=mom3,Y_energy_over_planck=mom3/(np.pi**4/15))
(D/'SPECTRAL_ORACLE.json').write_text(json.dumps(out,indent=2)+'\n')
