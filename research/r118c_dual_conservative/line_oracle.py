"""Independent continuum and nodal characteristic line oracles plus
continuous-time semidiscrete reversible redistribution oracle (DOP853).
No Rust implementation or old moment reconstruction reused.
"""
import pathlib,sys,json,math
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.special import ndtr,expit
from scipy.integrate import solve_ivp
root=pathlib.Path(sys.argv[1]);cases=json.loads((root/'RESULTS.json').read_text())['cases']
N3=2.4041138063191885;N4=np.pi**4/15
gx,gw=leggauss(32);tx,tw=leggauss(32)
def load(p):return np.genfromtxt(p,names=True,delimiter='\t')
def hats(u,split=()):
 # independently integrate number measure with positive linear-energy hats
 us=[];ws=[];ls=[];rs=[]
 for j,(a,b) in enumerate(zip(u,u[1:])):
  edges=[a]+[z for z in split if a<z<b]+[b]
  for l,r in zip(edges,edges[1:]):
   v=(l+r)/2+(r-l)*gx/2;w=(r-l)*gw/2*np.exp(3*v)
   s=np.expm1(v-a)/np.expm1(b-a)
   us.extend(v);ws.extend(w);ls.extend([j]*len(v));rs.extend(s)
 return np.array(us),np.array(ws),np.array(ls),np.array(rs)
def project(n,w,left,s,nf):
 return np.bincount(left,weights=w*(1-s)*n,minlength=nf)+np.bincount(left+1,weights=w*s*n,minlength=nf)
records=[]
for c in cases:
 name=c['case']
 if not name.startswith(('monotone_f','turn_f','turn_t','narrow_f')):continue
 assert c['status']=='PASS_SCOPED'
 p=root/name;ray=load(p/'frequency_rays.tsv');raw=load(p/'frequency_nodes.tsv').reshape(len(ray),-1)
 u=raw['u'][0];nf=len(u)
 center,sigma,strength,S=map(float,c['command'][c['command'].index('--frequency-line')+1].split(','))
 vel=load(p/'frequency_line_velocity.tsv');end=float(c['last']['eta'])
 # For the stationary narrow-line benchmark split each continuum integral
 # around the two analytic cumulative optical-depth transitions.
 split=sorted({center+j*sigma for j in range(-12,13)}|{center+end+j*sigma for j in range(-12,13)}) if np.max(np.abs(vel['beta_z']))==0 else ()
 uu,ww,ll,ss=hats(u,split)
 init=1/np.expm1(np.exp(uu));initial=project(init,ww,ll,ss,nf);weights=project(np.ones_like(uu),ww,ll,ss,nf)
 t=[];dt=[];bs=[]
 for l,r,bl,br in zip(vel['eta'][:-1],vel['eta'][1:],vel['beta_z'][:-1],vel['beta_z'][1:]):
  t.append((l+r)/2+(r-l)*tx/2);dt.append((r-l)*tw/2);bs.append((bl+br)/2+(br-bl)*tx/2)
 t=np.concatenate(t);dt=np.concatenate(dt);bs=np.concatenate(bs)
 def tau(y,mu):
  if np.max(np.abs(bs))==0:return strength*(ndtr((y-center)/sigma)-ndtr((y-end-center)/sigma))
  D=(1-mu*bs)/np.sqrt(1-bs**2);shift=-t+np.log(D)
  val=np.empty(len(y))
  for l in range(0,len(y),2048):
   z=(y[l:l+2048,None]+shift[None,:]-center)/sigma
   val[l:l+2048]=strength/(sigma*np.sqrt(2*np.pi))*(np.exp(-z*z/2)@(dt*D))
  return val
 e_node=e_cont=signal=0.;number_node=number_cont=number_act=0.;energy_node=energy_cont=energy_act=0.
 for i,mu in enumerate(ray['e_z']):
  tau_n=tau(u,mu);tau_c=tau(uu,mu)
  nodal=S*weights+(initial-S*weights)*np.exp(-tau_n)
  continuum=project(S+(init-S)*np.exp(-tau_c),ww,ll,ss,nf)
  actual=raw['n_xx'][i]+raw['n_yy'][i]+raw['n_zz'][i]
  w=ray['weight'][i]/(4*np.pi)
  e_node+=w*np.sum(np.abs(actual-nodal));e_cont+=w*np.sum(np.abs(actual-continuum))
  signal+=w*np.sum(np.abs(continuum-initial))
  number_node+=w*nodal.sum()/N3;number_cont+=w*continuum.sum()/N3;number_act+=w*actual.sum()/N3
  energy_node+=w*(nodal@np.exp(u))/N4;energy_cont+=w*(continuum@np.exp(u))/N4;energy_act+=w*(actual@np.exp(u))/N4
 v=dict(case=name,nodes=nf,relative_nodal_L1=e_node/signal,relative_continuum_hat_L1=e_cont/signal,continuum_number_error=abs(number_cont-number_act),nodal_number_error=abs(number_node-number_act),continuum_energy_error=abs(energy_cont-energy_act),actual_number=number_act,exact_continuum_number=number_cont,exact_nodal_number=number_node)
 records.append(v);print(name,v['relative_nodal_L1'],v['relative_continuum_hat_L1'],v['continuum_number_error'],flush=True)
# Compare exact semidiscrete nonautonomous evolution of the full tridiagonal
# chain to Rust's Strang pair sweeps, using FLRW rest geometry, no line sink.
red=[]
for c in cases:
 name=c['case']
 if not name.startswith('redist_t') or name.startswith('redist_turn'):continue
 assert c['status']=='PASS_SCOPED'
 p=root/name;raw=load(p/'frequency_nodes.tsv');ray=load(p/'frequency_rays.tsv')
 raw=raw.reshape(len(ray),-1);u=raw['u'][0];x=np.exp(u);nf=len(u)
 uu,ww,ll,ss=hats(u)
 initial=project(1/np.expm1(np.exp(uu)),ww,ll,ss,nf);w=project(np.ones_like(uu),ww,ll,ss,nf)
 diff,theta=c['red'];center,width,*_=map(float,c['command'][c['command'].index('--frequency-line')+1].split(','))
 def rhs(t,n):
  lp=np.log(w)-x*np.exp(-t)/theta
  rate=2*diff*np.exp(-.5*((.5*(u[:-1]+u[1:])-t-center)/width)**2)/np.diff(u)**2
  to_r=rate*expit(lp[1:]-lp[:-1]);to_l=rate*expit(lp[:-1]-lp[1:])
  flux=to_r*n[:-1]-to_l*n[1:]
  return np.r_[-flux,0.]+np.r_[0.,flux]
 exact=solve_ivp(rhs,(0,float(c['last']['eta'])),initial,method='DOP853',rtol=2e-12,atol=1e-14).y[:,-1]
 assert abs(exact.sum()-initial.sum())<2e-12
 act=raw['n_xx'][0]+raw['n_yy'][0]+raw['n_zz'][0]
 err=np.sum(abs(act-exact))/np.sum(abs(exact-initial))
 val=dict(case=name,nodes=nf,relative_l1_signal=float(err),energy_error=float(abs((act-exact)@x)/N4),oracle_energy_transfer=float((exact-initial)@x/N4))
 red.append(val);print(val,flush=True)
(root/'LINE_REDIST_ORACLE.json').write_text(json.dumps(dict(line=records,redistribution=red),indent=2)+'\n')
