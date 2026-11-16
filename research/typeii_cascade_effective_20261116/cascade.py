"""Finite source-conditioned H cascade and conservative stationary reduction.
Six unaligned hydrogen nl levels plus an ion tracer at prescribed proper ne.
All rates use proper seconds. No native HYREC effective coefficient replacement.
"""
from pathlib import Path
from functools import lru_cache
import sys,math,json,hashlib
import numpy as np
import sympy as sp
from scipy.constants import epsilon_0
from scipy.integrate import quad
from scipy.special import eval_genlaguerre
from numpy.polynomial.legendre import leggauss
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'research/typeii_boundfree_balance_20261116'))
import boundfree as bf
H,C,KB,EV,ME=bf.H,bf.C,bf.KB,bf.EV,bf.ME
HBAR=H/(2*np.pi);EC=1.602176634e-19
A0=4*np.pi*epsilon_0*HBAR**2/(ME*EC**2)
STATES=((1,0),(2,0),(2,1),(3,0),(3,1),(3,2))
RETAINED=np.array([0,1,2,6]);FAST=np.array([3,4,5])
ENERGY=np.array([-bf.level(k)['chi'] for k in STATES]+[0.])

def check(ok,msg):
 if not bool(ok):raise RuntimeError(msg)

def validate(Tn,beta,eta=0):
 if not np.isfinite([Tn,beta,eta]).all() or not 300<=Tn<=10000 or abs(beta)>.2 or eta<0:raise ValueError('domain: 300..10000 K, |beta|<=.2, eta>=0')

def validate_line(upper,lower):
 if upper not in STATES or lower not in STATES or abs(upper[1]-lower[1])!=1 or upper[0]<=lower[0]:raise ValueError('not an admitted downward E1 line')

@lru_cache(maxsize=20)
def radial_exact(upper,lower):
 validate_line(upper,lower);x=sp.Symbol('x',positive=True)
 def poly(n,l):
  n=sp.Integer(n)
  return (2/n)**sp.Rational(3,2)*sp.sqrt(sp.factorial(n-l-1)/(2*n*sp.factorial(n+l)))*(2*x/n)**l*sp.assoc_laguerre(n-l-1,2*l+1,2*x/n)
 a=sp.Rational(1,upper[0])+sp.Rational(1,lower[0]);p=sp.Poly(sp.expand(x**3*poly(*upper)*poly(*lower)),x)
 val=sum(coeff*sp.factorial(power[0])/a**(power[0]+1) for power,coeff in p.terms())
 return float(val)

def radial_numeric(upper,lower):
 validate_line(upper,lower)
 def R(n,l,x):
  return (2/n)**1.5*math.sqrt(math.factorial(n-l-1)/(2*n*math.factorial(n+l)))*np.exp(-x/n)*(2*x/n)**l*eval_genlaguerre(n-l-1,2*l+1,2*x/n)
 return quad(lambda x:x**3*R(*upper,x)*R(*lower,x),0,np.inf,epsabs=1e-12,epsrel=2e-13)[0]

@lru_cache(maxsize=20)
def einstein_A(upper,lower):
 validate_line(upper,lower)
 gap=bf.level(lower)['chi']-bf.level(upper)['chi'];omega=gap/HBAR
 angular=max(upper[1],lower[1])/(2*upper[1]+1)
 return EC**2*omega**3/(3*np.pi*epsilon_0*HBAR*C**3)*angular*(A0*radial_exact(upper,lower))**2

def lines():
 return [(u,l) for u in STATES for l in STATES if u[0]>l[0] and abs(u[1]-l[1])==1]

def line_rates(upper,lower,Tn,beta,eta=0):
 validate(Tn,beta,eta);a=einstein_A(upper,lower)
 e=bf.level(lower)['chi']-bf.level(upper)['chi'];occ=float(np.exp(bf.log_nbar(e,Tn,beta,eta)))
 ratio=bf.level(upper)['g']/bf.level(lower)['g']
 return {'upper':upper,'lower':lower,'down':a*(1+occ),'up':ratio*a*occ,'vacuum_A':a,'gap_J':e,'photon_count':1}

def moments(E,Tn,beta,eta=0,order=32):
 mu,w=leggauss(order);g=1/np.sqrt(1-beta*beta)
 ex=np.asarray(E)[...,None]/(KB*Tn)*g*(1+beta*mu)+eta
 f=np.exp(-ex)/(-np.expm1(-ex));p2=(3*mu**2-1)/2
 return f@(w/2),f@(w*p2/2)

def pair_average(E1,E2,Tn,beta,eta=0,direct=False,order=32):
 validate(Tn,beta,eta)
 if min(E1,E2)<=0 or not np.isfinite([E1,E2]).all():raise ValueError('positive pair energies required')
 if not direct:
  a0,a2=moments(E1,Tn,beta,eta,order);b0,b2=moments(E2,Tn,beta,eta,order)
  return float(a0*b0+.5*a2*b2)
 mu,w=leggauss(order);g=1/np.sqrt(1-beta*beta)
 def f(E):
  ex=E/(KB*Tn)*g*(1+beta*mu)+eta;return np.exp(-ex)/(-np.expm1(-ex))
 # Exact azimuth average of 3/4(1+cos(theta12)^2), independently of multipoles.
 z=mu[:,None]*mu[None,:];b=(1-mu[:,None]**2)*(1-mu[None,:]**2)
 W=.75*(1+z*z+.5*b)
 return float((f(E1)*w/2)@W@(f(E2)*w/2))

@lru_cache(maxsize=2)
def two_photon_table(which='hires'):
 if which not in ('standard','hires'):raise ValueError('unknown two-photon source table')
 name='two_photon_tables'+('_hires' if which=='hires' else '')+'.dat'
 lock=json.loads((HERE/'sources/PROVENANCE.json').read_text())['HYREC_source_files']
 p=HERE/'sources'/name;check(hashlib.sha256(p.read_bytes()).hexdigest()==lock[name],'two-photon source drift')
 data=np.loadtxt(p);num=408 if which=='hires' else 140
 data=data[:num];y=data[:,0]/10.198714553953742;w=data[:,2]
 check(np.all((y>.5)&(y<1)) and np.all(w>=0),'invalid source 2gamma sharing')
 w=8.2206*w/np.sum(w)
 return y,w

def two_photon(Tn,beta,eta=0,table='hires',order=32,vacuum=False):
 validate(Tn,beta,eta);gap=bf.level((1,0))['chi']-bf.level((2,0))['chi'];y,w=two_photon_table(table)
 if vacuum:return {'upper':(2,0),'lower':(1,0),'down':float(sum(w)),'up':0.,'gap_J':gap,'photon_count':2}
 a0,a2=moments(gap*y,Tn,beta,eta,order);b0,b2=moments(gap*(1-y),Tn,beta,eta,order)
 pair=a0*b0+.5*a2*b2
 down=float(np.sum(w*(1+a0+b0+pair)));up=float(np.sum(w*pair))
 return {'upper':(2,0),'lower':(1,0),'down':down,'up':up,'gap_J':gap,'photon_count':2,'table':table,
         'wrong_independent_angles_up':float(np.sum(w*a0*b0)),
         'stimulated_enhancement':down/8.2206-1}

def network(Tn,Tm,beta,ne,eta=0,table='hires',bf_records=None):
 bf.validate(Tn,Tm,beta,eta)
 if not np.isfinite(ne) or ne<=0:raise ValueError('proper reservoir ne must be positive')
 br=[bf.rates(Tn,Tm,beta,k,eta=eta) for k in STATES] if bf_records is None else bf_records
 check(len(br)==6,'six microscopic bound-free channels required')
 Q=np.zeros((7,7));channels=[]
 def edge(dest,source,rate):
  check(np.isfinite(rate) and rate>=0,'invalid transition rate');Q[dest,source]+=rate
 for i,r in enumerate(br):
  edge(6,i,r['photo_s']);edge(i,6,ne*r['alpha_m3_s'])
 for u,l in lines():
  r=line_rates(u,l,Tn,beta,eta);channels.append(r)
 channels.append(two_photon(Tn,beta,eta,table))
 for r in channels:
  u=STATES.index(r['upper']);l=STATES.index(r['lower']);edge(l,u,r['down']);edge(u,l,r['up'])
 np.fill_diagonal(Q,-np.sum(Q,axis=0))
 logw=np.array([math.log(ne)+bf.log_saha(Tm,k) for k in STATES]+[0.]);w=np.exp(logw-max(logw));w/=sum(w)
 return {'Q':Q,'boundfree':br,'channels':channels,'ne':ne,'Tn':Tn,'Tm':Tm,'beta':beta,'eta':eta,'reference_weights':w,'energy':ENERGY.copy()}

def eliminate(Q,retained=RETAINED):
 Q=np.asarray(Q,float);r=np.array(retained,int)
 if Q.ndim!=2 or Q.shape[0]!=Q.shape[1] or not np.isfinite(Q).all():raise ValueError('invalid generator')
 if len(set(r))!=len(r) or min(r)<0 or max(r)>=len(Q) or len(r)>=len(Q):raise ValueError('invalid retained indices')
 off=Q.copy();np.fill_diagonal(off,0)
 if np.min(off)<0 or np.any(np.diag(Q)>=0):raise ValueError('not a nonnegative transition generator')
 if np.any(abs(Q.sum(axis=0))>1e-12*np.sum(abs(Q),axis=0)):raise ValueError('generator does not conserve nuclei column by column')
 f=np.array([j for j in range(len(Q)) if j not in r]);rr=Q[np.ix_(r,r)];rf=Q[np.ix_(r,f)];fr=Q[np.ix_(f,r)];ff=Q[np.ix_(f,f)]
 N=np.linalg.solve(-ff,np.eye(len(f)));check(np.min(N)>=0,'non-transient eliminated block')
 L=N@fr;P=rf@N;raw=rr+rf@L
 S=raw.copy();np.fill_diagonal(S,0);check(np.min(S)>=0,'negative Schur offdiagonal');np.fill_diagonal(S,-S.sum(axis=0))
 Cstore=np.eye(len(r))+rf@N@N@fr
 return {'r':r,'f':f,'rr':rr,'rf':rf,'fr':fr,'ff':ff,'N':N,'L':L,'P':P,'S':S,'S_raw':raw,'storage':Cstore}

def lift(e,p):
 p=np.asarray(p);ans=np.zeros(len(e['r'])+len(e['f']),dtype=p.dtype);ans[e['r']]=p;ans[e['f']]=e['L']@p;return ans

def stationary(Q,weights):
 Q=np.asarray(Q);w=np.asarray(weights,float)
 if w.ndim!=1 or len(w)!=len(Q) or not np.isfinite(w).all() or np.any(w<=0):raise ValueError('positive finite conditioning weights needed')
 w=w/np.max(w);w=w/sum(w)
 q=Q*w[None,:]/w[:,None];a=int(np.argmax(w));other=np.array([i for i in range(len(w)) if i!=a])
 M=q[np.ix_(other,other)];rhs=-q[other,a];scale=np.max(abs(M),axis=1)
 x=np.ones(len(w));x[other]=np.linalg.solve(M/scale[:,None],rhs/scale)
 check(np.min(x)>0 and np.isfinite(x).all(),'stationary solution positivity')
 ans=w*x;return ans/sum(ans)

def energy(net,p):
 p=np.asarray(p,float)
 if p.shape!=(7,) or not np.isfinite(p).all() or min(p)<0:raise ValueError('nonnegative seven-state population needed')
 photon=kinetic=number=gross=0.
 for i,r in enumerate(net['boundfree']):
  fw=p[i]*r['photo_s'];rv=p[6]*net['ne']*r['alpha_m3_s'];chi=r['chi_J'];kp=r['photo_excess_J'];kr=r['capture_kinetic_J']
  photon+=-fw*(chi+kp)+rv*(chi+kr);kinetic+=fw*kp-rv*kr;number+=rv-fw
  gross+=fw*(chi+kp)+rv*(chi+kr)
 for r in net['channels']:
  u=STATES.index(r['upper']);l=STATES.index(r['lower']);down=p[u]*r['down'];up=p[l]*r['up'];F=down-up
  photon+=r['gap_J']*F;number+=r['photon_count']*F;gross+=r['gap_J']*(down+up)
 bound=float(ENERGY@(net['Q']@p));res=photon+kinetic+bound
 return {'photon_energy_J_s':float(photon),'electron_kinetic_J_s':float(kinetic),'bound_energy_J_s':bound,
         'photon_number_s':float(number),'gross_energy_J_s':float(gross),'residual_J_s':float(res),'relative_residual':float(abs(res)/max(gross,1e-300))}

def cycle_affinity(Tn,beta,eta=0):
 a=line_rates((3,1),(2,0),Tn,beta,eta);b=two_photon(Tn,beta,eta);c=line_rates((3,1),(1,0),Tn,beta,eta)
 return float(np.log(a['down'])-np.log(a['up'])+np.log(b['down'])-np.log(b['up'])+np.log(c['up'])-np.log(c['down']))
