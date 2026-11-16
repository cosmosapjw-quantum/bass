#!/usr/bin/env python3
"""Original Fortran cross-section identity and independent spectral quadratures."""
import ctypes,hashlib,json,subprocess
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from scipy.special import logsumexp
from collisions import *
HERE=Path(__file__).resolve().parent

def check(ok,msg):
 if not bool(ok):raise RuntimeError(msg)
def sh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run():
 prov=json.loads((HERE/'sources/PROVENANCE.json').read_text())
 for r in prov:check(r['status']=='DOWNLOADED' and sh(HERE/'sources'/r['file'])==r['sha256'],'cross-section source drift')
 work=HERE/'native_run';work.mkdir(exist_ok=True)
 lib=work/'libphfit2.so'
 cmd=['gfortran','-O2','-std=legacy','-fPIC','-shared',str(HERE/'sources/phfit2.f'),'-o',str(lib)]
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=45)
 (HERE/'FORTRAN_BUILD.log').write_text(p.stdout+p.stderr);check(p.returncode==0,'original Fortran compilation failed')
 f=ctypes.CDLL(str(lib)).phfit2_;f.argtypes=[ctypes.POINTER(ctypes.c_int)]*3+[ctypes.POINTER(ctypes.c_float)]*2
 cases=[]
 for name,(Z,Ne) in SPECIES.items():
  for fac in (1.0001,1.01,1.1,1.5,2.,5.,10.,100.):
   E=ctypes.c_float(PARAMS[name][0]*fac);out=ctypes.c_float()
   iz,ie,ish=ctypes.c_int(Z),ctypes.c_int(Ne),ctypes.c_int(1)
   f(ctypes.byref(iz),ctypes.byref(ie),ctypes.byref(ish),ctypes.byref(E),ctypes.byref(out))
   want=float(out.value)*1e-22;ours=float(sigma_ev(E.value,name));gap=abs(ours/want-1)
   check(gap<2e-5,'source Fortran sigma parity failed '+name)
   cases.append({'species':name,'energy_eV_float32':E.value,'source_sigma_m2':want,'python_sigma_m2':ours,'relative_gap':gap})
 # Alternative adaptive energy integration and analytic angular occupation mean.
 # Same fit, but no directional/angular quadrature and no Gaussian energy summation.
 # Rescale by threshold occupation and sigma to avoid absolute-scale false convergence.
 photos=[]
 for T,b,name in [(3000.,.05,'HI'),(3000.,.05,'HeI'),(3000.,.05,'HeII'),(820.3755,.0275,'HI'),(820.3755,.0275,'HeII')]:
  g=1/np.sqrt(1-b*b);thot=T*np.sqrt((1+b)/(1-b));eth=PARAMS[name][0]*EV
  sig0=float(sigma_ev(PARAMS[name][0],name));shift=eth/(KB*thot)
  def scaled_avg(E):
   aa=g*E/(KB*T);amin=aa*(1-b);amax=aa*(1+b)
   # log(1-e^-a) difference divided by 2aa b, scaled for large threshold x.
   # For the current Wien tail, expm1 gives a stable factored expression.
   u=np.exp(-amin);v=np.exp(-amax)
   if amin>35:
    return np.exp(shift-amin)*(-np.expm1(-2*aa*b))/(2*aa*b)
   return (np.log1p(-v)-np.log1p(-u))*np.exp(shift)/(2*aa*b)
  def integrand(y):
   E=eth+KB*thot*y
   return (E/eth)**2*float(sigma_ev(E/EV,name))/sig0*scaled_avg(E)
  I,err=quad(integrand,0.,100.,epsabs=1e-12,epsrel=2e-11,limit=200)
  logR=np.log(8*np.pi/(H**3*C**2)*eth**2*sig0*KB*thot)+np.log(I)-shift
  ours=photo_rate(T,b,name,order=96)['log_rate_s'];gap=abs(np.expm1(ours-logR))
  check(gap<2e-7,'adaptive photo integral disagreement')
  photos.append({'T_K':T,'beta':b,'species':name,'relative_gap':gap,'adaptive_relative_estimate':err/I,'log_rate_s':ours})
 # Direct double angular kernel, separately integrated at multiple energies.
 pair=[]
 mu,w=gauss(32)
 for x in (.01,.1,1.,5.,20.):
  f,mu,w=occupation(np.array([x]),.05,angular_order=32)
  a=float(induced_multipoles(f,mu,w)[0]);b=induced_pair(f[0],mu,w)
  rel=abs(a/b-1);check(rel<3e-11,'angular bilinear mismatch');pair.append(rel)
 # Separate adaptive frequency quadrature for Compton (direct pair angular kernel).
 def fun(x,power,kind):
  f,mu,w=occupation(np.array([x]),.05,angular_order=24);n0=float(f[0]@w)
  q=n0 if kind=='energy' else n0+induced_pair(f[0],mu,w)
  return x**power*q
 U=quad(lambda x:fun(x,3,'energy'),0.,100.,epsabs=2e-10,epsrel=2e-11,limit=100)[0]
 J=quad(lambda x:fun(x,4,'recoil'),0.,100.,epsabs=2e-10,epsrel=2e-11,limit=100)[0]
 tc=J/(4*U);main=compton_moments(.05,order=40)
 check(abs(tc-main['Tc_over_Tn'])<3e-10,'adaptive Compton moment disagreement')
 result={'cross_section_source_files':len(prov),'original_Fortran_cases':len(cases),'max_Fortran_relative_gap':max(x['relative_gap'] for x in cases),'Fortran_cases':cases,'adaptive_photo_checks':photos,'angular_bilinear_max_relative_gap':max(pair),'adaptive_Compton_Tc_over_Tn':tc,'adaptive_Compton_absolute_gap':abs(tc-main['Tc_over_Tn']),'baseline_Planck':compton_moments(0.),'beta005':main,'units':'SI outputs; original source E[eV], sigma[Mb] converted by 1Mb=1e-22m^2','claim':'kernel/source/independent quadrature checks; no native atomic hierarchy coupling'}
 (HERE/'KERNEL_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ('Fortran_cases',)},indent=2))
if __name__=='__main__':run()
