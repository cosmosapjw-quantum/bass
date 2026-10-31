#!/usr/bin/env python3
"""CE1AP remote: original six-cell Einstein-Vlasov + exact Bianchi I photon redshift."""
from __future__ import annotations
import csv,hashlib,json,math,sys
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;RESEARCH=ROOT.parent
sys.path.insert(0,str(RESEARCH/'ce1ai_20261031'/'source'))
import ce1ai_source_response as src
LOCK='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
PARENT='d94843f2b63638d36244d951eccdbb81f3a64357'
ORDERS=(8,16,24);EPS=(-.035,.035);N=401;U=.08
DIR={'x':(1.,0.,0.),'y':(0.,1.,0.),'z':(0.,0.,1.),
'xy':(2**-.5,2**-.5,0.),'xz':(2**-.5,0.,2**-.5),
'yz':(0.,2**-.5,2**-.5),'xyz':(3**-.5,)*3}
F_DIR=['GL','eps','u','dir','ln_R_base','delta_ln_R','source_secant','tangent_delta_ln_R',
 'secant_tangent_gap','drift_base','delta_drift','tangent_drift','drift_secant_tangent_gap',
 'E_ratio_base','E_ratio_finite']
F_TAN=['GL','u','dell1','dell2','dell3','dh1','dh2','dh3','dconstraint','ray_count']
F_SKY=['GL','eps','u','RMS_delta_ln_R_7dirs','max_abs_delta_ln_R_7dirs',
 'rms_tangent_ln_R_7dirs','redshift_x','redshift_y','redshift_z','volume_delta_ln_a',
 'A_early_expected_scale']
def A_exact():
 s=[F.from_float(float(v)) for v in src.SHEAR]
 tab={'xxx':-3,'xxy':1,'xxz':2,'xyy':1,'xyz':-2,'xzz':0,'yyy':-3,'yyz':2,'yzz':0,'zzz':0}
 C=[sum((s[j]*s[k]*tab[''.join(sorted('xyz'[v] for v in (i,j,k))) ]
          for j in range(3) for k in range(3)),F(0)) for i in range(3)]
 if sum(C)!=0:raise RuntimeError('traceless sixth moment violated')
 return [float(z)*(-27/(1421*math.pi)) for z in C]
def geo(ell,h,dl,dh,n):
 n2=np.asarray(n)**2;w=n2*np.exp(-2*np.asarray(ell));w/=sum(w)
 baseline=.5*math.log(float(n2@np.exp(-2*np.asarray(ell))))
 tangent=-float(w@dl);drift=-float(w@h)
 tdrift=-float(w@dh)+2*float(w@(h*dl)-(w@h)*(w@dl))
 return baseline,tangent,drift,tdrift
def finite(ell,h,ep,he,n):
 n2=np.asarray(n)**2;w=n2*np.exp(-2*np.asarray(ell));w/=sum(w)
 de=np.asarray(ep)-ell
 diff=.5*math.log1p(float(w@np.expm1(-2*de)))
 wp=w*np.exp(-2*de);wp/=sum(wp)
 return diff,-float(wp@he-w@h)
def write(path,fields,rows):
 with path.open('w',newline='') as f:
  w=csv.writer(f);w.writerow(fields);w.writerows(rows)
def execute():
 if src.validate_immutable()!=LOCK:raise RuntimeError('source identity drift')
 out=ROOT/'data';out.mkdir(parents=True,exist_ok=True)
 ts=np.linspace(0,U,N);drows=[];trows=[];srows=[];summ={}
 A=A_exact()
 for gl in ORDERS:
  rays,m=src.make_cell_rays(gl);r2=rays*rays;dm=src.ray_source_basis(gl,m)[-1]
  if abs(float(sum(dm)))>2e-13 or max(abs(dm@r2))>3e-12:raise RuntimeError('initial source not hidden')
  y0=src.initial_condition(r2,m);z0=np.r_[y0,src.tangent_initial(r2,m,dm[None,:])[0]]
  sol=solve_ivp(lambda t,z:src.rhs_joint(r2,m,dm[None,:],z),(0,U),z0,
    t_eval=ts,method='DOP853',rtol=3e-12,atol=3e-14)
  if not sol.success:raise RuntimeError(sol.message)
  paths={}
  for eps in EPS:
   mm=src.positive_reweighted_mass(gl,m,'DARK_L2L4',eps)
   f=solve_ivp(lambda t,y:src.rhs_base(r2,mm,y),(0,U),src.initial_condition(r2,mm),
     t_eval=ts,method='DOP853',rtol=3e-12,atol=3e-14)
   if not f.success:raise RuntimeError(f.message)
   paths[eps]=(mm,f.y.T)
  bc=dc=fc=0.
  for i,t in enumerate(ts):
   z=sol.y[:,i];ell=z[:3];h=z[3:6];dl=z[6:9];dh=z[9:12]
   E,P,x,om=src.ancestor.moment(r2,m,ell,with_r=False)
   dE=float((-E-P)@dl+(dm/m*om).sum())
   cons=float(h[0]*h[1]+h[0]*h[2]+h[1]*h[2]-E)
   dcons=float((sum(h)-h)@dh-dE)
   bc=max(bc,abs(cons));dc=max(dc,abs(dcons))
   trows.append([gl,float(t),*dl,*dh,dcons,len(m)])
   for eps,(mm,yy) in paths.items():
    yf=yy[i];ef,pf,*_=src.ancestor.moment(r2,mm,yf[:3],with_r=False)
    cc=float(yf[3]*yf[4]+yf[3]*yf[5]+yf[4]*yf[5]-ef);fc=max(fc,abs(cc))
    dlvalues=[];tanvalues=[]
    for k,n in DIR.items():
     baseline,tan,dr,tdr=geo(ell,h,dl,dh,np.asarray(n))
     delta,ddr=finite(ell,h,yf[:3],yf[3:],n)
     drows.append([gl,eps,float(t),k,baseline,delta,delta/eps,tan,delta/eps-tan,
       dr,ddr,tdr,ddr/eps-tdr,math.exp(baseline),math.exp(baseline+delta)])
     dlvalues.append(delta);tanvalues.append(tan)
    srows.append([gl,eps,float(t),float(np.sqrt(np.mean(np.square(dlvalues)))),
     max(abs(z) for z in dlvalues),float(np.sqrt(np.mean(np.square(tanvalues)))),
     *dlvalues[:3],float(sum(yf[:3])-sum(ell)),float(t**4*np.linalg.norm(A)/8)])
  summ[str(gl)]={'new_IVPs':3,'rays':len(m),'max_constraint':bc,'max_tangent_constraint':dc,
    'max_finite_constraint':fc,'end_tangent_dell':list(map(float,sol.y[6:9,-1]))}
  print('CE1AP_REMOTE',gl,'rays',len(m),'constraint',bc,'tangent',dc,'finite',fc,flush=True)
 write(out/'CE1AP_DIRECTIONAL_GEODESIC.csv',F_DIR,drows)
 write(out/'CE1AP_EINSTEIN_TANGENT_METRIC.csv',F_TAN,trows)
 write(out/'CE1AP_DIRECTIONAL_SKY_RMS.csv',F_SKY,srows)
 res={'schema':'bass.ce1ap.original_source_remote.v1','source_sha256':LOCK,'parent_head':PARENT,
  'source_model':'original massless collisionless six-cell diagonal Bianchi I','signature':'(-,+,+,+)',
  'Einstein_normalization':'8piG=1 dimensionless','orders':ORDERS,'eps':EPS,'epochs':N,
  'new_IVPs':9,'tangent_IVPs':3,'finite_IVPs':6,'directional_rows':len(drows),
  'tangent_rows':len(trows),'directional_RMS_rows':len(srows),'A_exact_from_dyadic_source':A,
  'GL':summ,'upper_DAG':'9/15','new_upper_nodes':0,'full_continuum_weyl_sign':False,
  'CMB_likelihood':False,'production':False,'merge':False,'auto_next':False}
 (out/'CE1AP_REMOTE_RESULTS.json').write_text(json.dumps(res,indent=2,allow_nan=False)+'\n')
 return res
if __name__=='__main__':execute()
