"""Exact original BASS directional flow and quadrature Jacobians.
Sources remain external prescribed matter history, not solved photon feedback.
"""
import ast,json,math,subprocess
from functools import lru_cache
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator
from redistribution import ROOT,HERE,check,sphere_rule,atom_directions,lt
PARENT='0577ef0a40cf10130a5933eb52c7230d4de1f11b'

def flow_fields(state,n):
 sp,sm,s13,N1,b=state;sr=np.sqrt(3)
 S=np.array([[-2*sp,0,sr*s13],[0,sp+sr*sm,0],[sr*s13,0,sp-sr*sm]])
 Sn=n@S.T;snn=np.sum(n*Sn,axis=1)
 dn=-Sn+snn[:,None]*n
 dn[:,0]+=sr*s13*n[:,2]
 dn[:,2]-=sr*s13*n[:,0]
 dn[:,1]-=N1*n[:,0]*n[:,2]
 dn[:,2]+=N1*n[:,0]*n[:,1]
 return dn,snn

class Source:
 def __init__(self):
  paths=['compiler/validation/generate_typeii_fixture.py','compiler/validation/typeii_fixture_canonical.json','research/typeii_cascade_effective_20261116/SOURCE_TRACE_STATIONARY.csv','research/typeii_lyman_transfer_20261116/RESONANCE_FATES.csv','research/typeii_native_hyrec_expansion_20261102/R3_TYPEII_HUBBLE_GRID.json']
  self.locks={}
  for path in paths:
   want=subprocess.check_output(['git','rev-parse',PARENT+':'+path],cwd=ROOT,text=True).strip()
   actual=subprocess.check_output(['git','hash-object',path],cwd=ROOT,text=True).strip();check(want==actual,'immutable parent source drift '+path);self.locks[path]=want
  ns={'math':math};source=ROOT/paths[0];node=[v for v in ast.parse(source.read_text()).body if isinstance(v,ast.FunctionDef) and v.name=='typeii_rhs']
  check(len(node)==1,'original RHS definition');exec(compile(ast.Module(body=node,type_ignores=[]),str(source),'exec'),ns);self.rhs=ns['typeii_rhs']
  self.fixture=json.loads((ROOT/paths[1]).read_text())['trajectory']['samples'];x0=np.asarray(self.fixture[0]['state'],float);self.G0=1/np.sqrt(1-x0[4]**2)
  self.tr=np.genfromtxt(ROOT/paths[2],delimiter=',',names=True);t=self.tr['tau_H'];self.end=float(t[-1])
  self.H0=json.loads((ROOT/paths[4]).read_text())['H_anchor_source_FLRW_s_inverse']
  def rhs(t,y):
   dx=np.array(self.rhs(list(y[:5]),1.3));q=dx[3]/y[3]+4*y[0];return np.r_[dx,-1-q]
  self.bg=solve_ivp(rhs,(0.,self.end),np.r_[x0,np.log(self.H0)],method='DOP853',rtol=2e-12,atol=1e-13,max_step=.003,dense_output=True)
  check(self.bg.success,'original TypeII background integration')
  self.tm=PchipInterpolator(t,np.log(self.tr['Tm_K']),extrapolate=False);self.pl=PchipInterpolator(t,np.log(self.tr['p1s']),extrapolate=False)
  f=np.genfromtxt(ROOT/paths[3],delimiter=',',names=True);tf=np.log(1701/(1+f['z_mean']))
  check(max(abs(tf-t))<4e-14,'tagged fate/parent time agreement')
  self.pd=PchipInterpolator(t,np.log(f['p_ionization']),extrapolate=False)
  self.nh0=11.223846333047e-6*.0224*(1-.245)*1e6
 def state(self,t):
  if not np.isfinite(t) or t<0 or t>self.end+1e-13:raise ValueError('time outside source support')
  y=self.bg.sol(t);return y[:5],float(np.exp(y[5]))
 def matter(self,t):
  st,hn=self.state(t);G=1/np.sqrt(1-st[4]**2)
  nh=self.nh0*1701**3*np.exp(-3*t)*self.G0/G
  return {'T':float(np.exp(self.tm(t))),'nl':float(nh*np.exp(self.pl(t))),'pd':float(np.exp(self.pd(t))),'Hn':hn,'beta':float(st[4]),'nHrest':float(nh)}

@lru_cache(maxsize=1)
def source():return Source()

class Angles:
 def __init__(self,t0,t1,nmu=4,nphi=8,initial=None):
  self.src=source();self.t0=float(t0);self.t1=float(t1)
  if not 0<=t0<t1<=self.src.end+1e-13:raise ValueError('invalid angular propagation interval')
  if initial is None:self.n0,self.w0=sphere_rule(nmu,nphi)
  else:
   self.n0=np.asarray(initial,float);self.w0=np.ones(len(self.n0))
   atom_directions(self.n0,0.)
  _,self.D0=atom_directions(self.n0,self.src.state(t0)[0][4])
  def rhs(t,y):
   x=y.reshape(-1,5);st,hn=self.src.state(t);dn,snn=flow_fields(st,x[:,:3]);return np.column_stack((dn,-1-snn,3*snn)).ravel()
  y0=np.column_stack((self.n0,np.zeros((len(self.n0),2)))).ravel()
  self.sol=solve_ivp(rhs,(t0,t1),y0,method='DOP853',rtol=2e-12,atol=5e-14,max_step=.003,dense_output=True)
  check(self.sol.success,'source angular characteristics')
 def at(self,t):
  if t<self.t0-1e-13 or t>self.t1+1e-13:raise ValueError('angular interpolation outside support')
  r=self.sol.sol(t).reshape(-1,5);n=r[:,:3];st,hn=self.src.state(t);a,D=atom_directions(n,st[4]);wn=self.w0*np.exp(r[:,4]);wa=wn/D**2
  d=lt.drift(st,self.src.rhs(list(st),1.3),n)
  return {'n':n,'na':a,'D':D,'wn':wn,'wa':wa,'logEn':r[:,3],'logJ':r[:,4],'V':float(np.exp(3*(t-self.t0))),'kappa':d['kappa'],'Hn':hn,'state':st}
