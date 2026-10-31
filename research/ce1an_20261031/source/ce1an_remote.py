#!/usr/bin/env python3
"""CE1AN: source-locked, actual finite-amplitude original six-cell Einstein--Vlasov IVPs.
Original parent CE1AL PR296; no thermal, Thomson, CMB or production model.
"""
from __future__ import annotations
import csv, json, math, sys
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
RESEARCH=ROOT.parent
sys.path.insert(0,str(RESEARCH/'ce1ai_20261031'/'source'))
sys.path.insert(0,str(RESEARCH/'ce1al_20261031'/'source'))
import ce1ai_source_response as src
import ce1al_curvature_remote as curv

SOURCE='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
PARENT='cdd77fbbd4c9e29c202927e4fac6a6d2a4cd7d0a'
ORDERS=(8,16,24)
EPS=(.01,.025,.035)
U=.08
N=401

FIELDS=('GL','eps','u','E','P1','P2','P3','h1','h2','h3','ell1','ell2','ell3','W','q',
  'WeylSq','RicciSq','Kretschmann','Electric1','Electric2','Electric3','F','integral_q',
  'logbalance','constraint','Weyl_identity_gap','mass_min')
TAN=('GL','u','dWeylSq','dRicciSq','dKretschmann','dE','dP1','dP2','dP3','dconstraint')
SEC=('GL','amplitude','u','dWeylSq_secant','dRicciSq_secant','dKretschmann_secant',
 'dWeylSq_tangent','dRicciSq_tangent','dKretschmann_tangent','nonlinear_secant_gap_WeylSq','nonlinear_secant_gap_RicciSq')

def source_check():
 if src.validate_immutable()!=SOURCE or curv.certificate()['source_sha256']!=SOURCE:
  raise RuntimeError('Original immutable source SHA drift')
 return SOURCE

def moments(r2,m,ell):
 E,P,x,omega=src.ancestor.moment(r2,m,ell,with_r=False)
 return E,P

def work(h,E,P):
 return float((h-np.mean(h))@(P-E/3.))

def joint_rhs(t,y,r2,m):
 h=y[3:6]
 E,P=moments(r2,m,y[:3])
 w=work(h,E,P)
 return np.r_[src.rhs_base(r2,m,y[:6]),w/E]

def record(gl,e,t,y,r2,m,Einit):
 ell=y[:3];h=y[3:6]
 E,P=moments(r2,m,ell)
 electric,c2,K,ric,ratio,identity,trace=curv.curv(h,P,E)
 H=float(np.mean(h));W=work(h,E,P)
 q=W/E;F=E*math.exp(4*sum(ell)/3)/Einit
 con=float(h[0]*h[1]+h[0]*h[2]+h[1]*h[2]-E)
 return [gl,e,float(t),E,*P,*h,*ell,W,q,c2,ric,K,*electric,F,float(y[6]),
  math.log(F)+float(y[6]),con,identity,float(np.min(m))]

def tangent_obs(z,r2,m,dm):
 ell=z[:3];h=z[3:6];dl=z[6:9];dh=z[9:12]
 E,P,R,x,omega=src.ancestor.moment(r2,m,ell)
 ds,dp,_=src.source_integrals(r2,dm[None,:],ell,x=x)
 dE=float((-E-P)@dl+ds[0])
 dP=src.ancestor.pressure_jacobian(P,R)@dl+dp[0]
 _,dc2,dk,dr,_,did,dtrace=curv.dcurv(h,P,E,dh,dP,dE)
 return [float(dc2),float(dr),float(dk),dE,*map(float,dP),
  float((sum(h)-h)@dh-dE)]

def execute(output=ROOT/'data'):
 source_check()
 out=Path(output);out.mkdir(parents=True,exist_ok=True)
 grid=np.linspace(0,U,N)
 rows=[];tans=[];secs=[];summary={}
 for gl in ORDERS:
  rays,m=src.make_cell_rays(gl);r2=rays*rays
  dm=src.ray_source_basis(gl,m)[-1]
  Einit=float(np.sum(m))
  initial=np.r_[src.initial_condition(r2,m),0.]
  masses={0.:m}
  for a in EPS:
   for s in (-1,1):
    e=float(s*a);masses[e]=src.positive_reweighted_mass(gl,m,'DARK_L2L4',e)
    if not bool(np.all(masses[e]>0)): raise RuntimeError('nonpositive six-cell source')
  obs={}
  maxcon=maxid=maxwork=0.
  for e,me in masses.items():
   sol=solve_ivp(lambda t,y:joint_rhs(t,y,r2,me),(0,U),initial,t_eval=grid,
    method='DOP853',rtol=3e-12,atol=3e-14)
   if not sol.success:raise RuntimeError(sol.message)
   series=[record(gl,e,t,y,r2,me,Einit) for t,y in zip(grid,sol.y.T)]
   rows.extend(series);obs[e]=series
   maxcon=max(maxcon,max(abs(r[FIELDS.index('constraint')]) for r in series))
   maxid=max(maxid,max(abs(r[FIELDS.index('Weyl_identity_gap')]) for r in series))
   maxwork=max(maxwork,max(abs(r[FIELDS.index('logbalance')]) for r in series))
  z0=np.r_[src.initial_condition(r2,m),src.tangent_initial(r2,m,dm[None,:])[0]]
  sol=solve_ivp(lambda t,y:src.rhs_joint(r2,m,dm[None,:],y),(0,U),z0,
    t_eval=grid,method='DOP853',rtol=3e-12,atol=3e-14)
  if not sol.success: raise RuntimeError(sol.message)
  tv=[tangent_obs(z,r2,m,dm) for z in sol.y.T]
  tans.extend([[gl,float(t),*v] for t,v in zip(grid,tv)])
  cross={}
  for amp in EPS:
   maxdc=maxdr=0.;last=None;allnegative=True
   for i,t in enumerate(grid):
    plus=obs[amp][i];minus=obs[-amp][i]
    w2=FIELDS.index('WeylSq');rr=FIELDS.index('RicciSq');kk=FIELDS.index('Kretschmann')
    dc=(plus[w2]-minus[w2])/(2*amp)
    dr=(plus[rr]-minus[rr])/(2*amp)
    dk=(plus[kk]-minus[kk])/(2*amp)
    value=[gl,amp,float(t),dc,dr,dk,tv[i][0],tv[i][1],tv[i][2],
     dc-tv[i][0],dr-tv[i][1]]
    secs.append(value);last=value
    maxdc=max(maxdc,abs(value[-2]));maxdr=max(maxdr,abs(value[-1]))
    if i and not dc<0:allnegative=False
   cross[str(amp)]={'end_secant_weyl':last[3], 'end_secant_ricci':last[4],
    'max_abs_secant_minus_tangent_weyl':maxdc,'max_abs_secant_minus_tangent_ricci':maxdr,
    'all_400_positive_u_sampled_secants_negative':allnegative,
    'delta_weyl_eps_positive':obs[amp][-1][FIELDS.index('WeylSq')]-obs[0.][-1][FIELDS.index('WeylSq')],
    'delta_weyl_eps_negative':obs[-amp][-1][FIELDS.index('WeylSq')]-obs[0.][-1][FIELDS.index('WeylSq')]}
  summary[str(gl)]={'original_rays':len(m),'nonlinear_IVPs':len(masses),'tangent_IVPs':1,
   'max_constraint':maxcon,'max_Weyl_identity':maxid,'max_integrated_energy_work':maxwork,
   'end_dWeyl_tangent':tv[-1][0],'eps':cross}
  print('CE1AN_REMOTE',gl,'source IVPs',len(masses)+1,'max constraint',maxcon,
   'max first law',maxwork,'end tangent',tv[-1][0],flush=True)
 for name,header,data in [('CE1AN_FINITE_SOURCE_PHYSICS.csv',FIELDS,rows),
   ('CE1AN_TANGENT_PHYSICS.csv',TAN,tans),('CE1AN_SECANT_RESPONSE.csv',SEC,secs)]:
  with (out/name).open('w',newline='') as f:
   w=csv.writer(f);w.writerow(header);w.writerows(data)
 result={'schema':'bass.ce1an.original_source_remote.v1','source_sha256':SOURCE,'immutable_parent':PARENT,
  'model':'massless_collisionless_diagonal_Bianchi_I','metric':'(-,+,+,+)','lambda':0,
  'Einstein_units':'8piG=1 dimensionless','horizon':[0,U],
  'orders':list(ORDERS),'amplitudes':list(EPS),'epochs':N,
  'nonlinear_rows':len(rows),'nonzero_amp_rows':len(rows)-len(ORDERS)*N,
  'tangent_rows':len(tans),'secant_diagnostic_rows':len(secs),'new_IVPs':24,'results':summary,
  'CE1':'PARTIAL','upper_DAG':'9/15','upper_edges':21,'new_upper_completed_nodes':0,
  'full_continuum_sign_proof':False,'Planck_likelihood':False,'production':False,'merge':False,'auto_next':False}
 (out/'CE1AN_REMOTE_RESULTS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
 return result
if __name__=='__main__': execute()
