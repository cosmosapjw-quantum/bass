#!/usr/bin/env python3
"""CE1AL independently constructed remote original Einstein--Vlasov Weyl curvature replay.

Source owned: original BASS IEEE754 six cells, no changes to ancestor. The
dark mass reweighting is a derivative family, not thermal CMB observations.
"""
from __future__ import annotations
import csv,json,math,sys
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
RESEARCH=ROOT.parent
sys.path.insert(0,str(RESEARCH/'ce1ai_20261031'/'source'))
import ce1ai_source_response as src
SOURCE_SHA='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
WINDOWS={'short_curvature':.01,'original_horizon':.08}
BASE_COLS=['GL','window','u','E','H','W','P1','P2','P3','h1','h2','h3','ell1','ell2','ell3','ElectricWeyl1','ElectricWeyl2','ElectricWeyl3','WeylSq','Kretschmann','RicciSq','WeylSq_over_E2','curvature_identity_residual','weyl_trace','einstein_constraint','dE','dP1','dP2','dP3','dh1','dh2','dh3','dell1','dell2','dell3','dElectricWeyl1','dElectricWeyl2','dElectricWeyl3','dWeylSq','dKretschmann','dRicciSq','dWeylSq_over_E2','dcurvature_identity_residual','dweyl_trace','dtangent_constraint','jet_dElectricWeyl1','jet_dElectricWeyl2','jet_dElectricWeyl3','jet_dWeylSq']
FIN_COLS=['GL','window','u','eps','sign','E','H','W','P1','P2','P3','h1','h2','h3','ell1','ell2','ell3','ElectricWeyl1','ElectricWeyl2','ElectricWeyl3','WeylSq','Kretschmann','RicciSq','WeylSq_over_E2','curvature_identity_residual','einstein_constraint']
class I:
 def __init__(self,lo,hi=None):
  self.lo=F(lo);self.hi=F(hi if hi is not None else lo)
  if self.lo>self.hi:raise ArithmeticError('empty bound')
 def __add__(self,x):
  x=_I(x);return I(self.lo+x.lo,self.hi+x.hi)
 __radd__=__add__
 def __neg__(self):return I(-self.hi,-self.lo)
 def __sub__(self,x):return self+-_I(x)
 def __rsub__(self,x):return _I(x)+-self
 def __mul__(self,x):
  x=_I(x);v=[a*b for a in (self.lo,self.hi) for b in (x.lo,x.hi)];return I(min(v),max(v))
 __rmul__=__mul__
 def __truediv__(self,x):
  x=_I(x)
  if x.lo<=0<=x.hi:raise ZeroDivisionError('interval zero')
  return self*I(1/x.hi,1/x.lo)
def _I(x):return x if isinstance(x,I) else I(x)
def certificate():
 if src.validate_immutable()!=SOURCE_SHA:raise RuntimeError('original six-cell mismatch')
 cell=[[F.from_float(float(v)) for v in row] for row in src.CELL_E]
 sigma=[F.from_float(float(v)) for v in src.SHEAR]
 E=sum((v for row in cell for v in row),F(0))
 Pz=sum((sum(row)*u for row,u in zip(cell,[F(1,12),F(7,12)])),F(0))
 b=(E-Pz)/2
 aa=sum(((r[0]-r[2])*v for r,v in zip(cell,[F(11,12),F(5,12)])),F(0))
 if aa-F(1,15)!=F(41,4323455642275676160):raise ArithmeticError('dyadic angular coefficient')
 pi=I(F(3141,1000),F(3142,1000));rt=I(F(1414,1000),F(1415,1000))
 press=[b+aa*(rt/pi),b-aa*(rt/pi),I(Pz)]
 Hsq=(E+sum((s*s for s in sigma),F(0))/2)/3
 H=I(F(557,1000),F(558,1000))
 if not H.lo**2<Hsq<H.hi**2:raise ArithmeticError('H0 enclosure')
 h=[H+s for s in sigma];theta=3*H
 ew=[theta*h[i]-h[i]*h[i]-(press[i]+E)/2 for i in range(3)]
 signs={'xxx':-3,'xxy':1,'xxz':2,'xyy':1,'xyz':-2,'xzz':0,'yyy':-3,'yyz':2,'yzz':0,'zzz':0}
 q=F(-27,1421)
 T=[[[q*signs[''.join(sorted('xyz'[i]+'xyz'[j]+'xyz'[k]))] for k in range(3)] for j in range(3)] for i in range(3)]
 for j in range(3):
  for k in range(3):
   if sum(T[i][j][k] for i in range(3))!=0:raise ArithmeticError('sixth tensor trace')
 A=[sum((sigma[j]*sigma[k]*T[i][j][k] for j in range(3) for k in range(3)),F(0)) for i in range(3)]
 if sum(A)!=0:raise ArithmeticError('A trace')
 dot=sum((ew[i]*(I(A[i])/pi) for i in range(3)),I(0))
 coeff=-12*dot
 if not (dot.lo>0 and coeff.hi<0):raise ArithmeticError('exact strict Weyl sign')
 r={'source_sha256':SOURCE_SHA,'kappa_rational_interval':[str(coeff.lo),str(coeff.hi)],
    'kappa_floats':[float(coeff.lo),float(coeff.hi)],'A_over_pi':[str(x) for x in A],
    'exact_initial_source_P_z':str(Pz),'exact_initial_h2':str(Hsq),
    'strict_claim':'delta WeylSq=kappa*u^2+O(u^3), kappa<0 for original continuum six cells',
    'full_horizon_sign':'NOT_CERTIFIED_CONTINUUM',
    'upper_DAG':'9/15','CE1':'PARTIAL','production_ready':False}
 return r

def curv(h,P,E):
 th=float(sum(h));rr=-th*h+P+h*h
 w=th*h-h*h-(P+E)/2
 k=float(4*(rr@rr+sum((h[i]*h[j])**2 for i in range(3) for j in range(i+1,3))))
 ric=float(E*E+P@P);w2=float(8*w@w)
 return w,w2,k,ric,w2/(E*E),k-2*ric-w2,float(sum(w))
def dcurv(h,P,E,dh,dP,dE):
 th=float(sum(h));dth=float(sum(dh));X=-th*h+P+h*h
 dX=-dth*h-th*dh+dP+2*h*dh
 w=th*h-h*h-(P+E)/2
 dw=dth*h+(th-2*h)*dh-(dP+dE)/2
 dk=float(8*(X@dX+sum(h[i]*h[j]*(dh[i]*h[j]+h[i]*dh[j]) for i in range(3) for j in range(i+1,3))))
 dric=float(2*(E*dE+P@dP));dc2=float(16*w@dw)
 dw2=float(8*w@w)
 return dw,dc2,dk,dric,dc2/E**2-2*dw2*dE/E**3,dk-2*dric-dc2,float(sum(dw))

def replay(epochs=401,eps=1e-3):
 c=certificate();out=ROOT/'data';out.mkdir(exist_ok=True,parents=True)
 allrows=[];allfinite=[];s={}
 for gl in (6,8,16):
  rays,mass=src.make_cell_rays(gl);r2=rays*rays;dm=src.ray_source_basis(gl,mass)[-1]
  base=src.initial_condition(r2,mass);tan=src.tangent_initial(r2,mass,dm[None,:])[0]
  s[str(gl)]={}
  for window,U in WINDOWS.items():
   ts=np.linspace(0,U,epochs)
   z=solve_ivp(lambda t,y:src.rhs_joint(r2,mass,dm[None,:],y),(0,U),np.r_[base,tan],
     method='DOP853',rtol=3e-12,atol=3e-14,t_eval=ts)
   if not z.success:raise RuntimeError(z.message)
   family={};mf={}
   for sign in (-1,1):
    mf[sign]=src.positive_reweighted_mass(gl,mass,'DARK_L2L4',sign*eps)
    y0=src.initial_condition(r2,mf[sign])
    sol=solve_ivp(lambda t,y:src.rhs_base(r2,mf[sign],y),(0,U),y0,
       method='DOP853',rtol=3e-12,atol=3e-14,t_eval=ts)
    if not sol.success:raise RuntimeError(sol.message)
    family[sign]=sol.y.T
   a=[];b=[];res=[]
   kappa=sum(float(c['A_over_pi'][j])/math.pi for j in range(3)) # only normalization check: sum A =0
   assert abs(kappa)<1e-15
   an=np.array([float(F(x))/math.pi for x in c['A_over_pi']])
   coeff= -.00216357980338848
   for ix,(u,v) in enumerate(zip(ts,z.y.T)):
    y=v[:6];ell=y[:3];h=y[3:];de=v[6:9];dh=v[9:]
    E,P,R,x,_=src.ancestor.moment(r2,mass,ell)
    ds,ps,_=src.source_integrals(r2,dm[None,:],ell,x=x)
    dE=float((-E-P)@de+ds[0]);dP=src.ancestor.pressure_jacobian(P,R)@de+ps[0]
    we,w2,kk,rr,ratio,identity,trace=curv(h,P,E)
    dw,dc2,dk,dric,dratio,dident,dtrace=dcurv(h,P,E,dh,dP,dE)
    W=float((h-h.mean())@(P-E/3));con=float(h[0]*h[1]+h[0]*h[2]+h[1]*h[2]-E)
    dcon=float((h.sum()-h)@dh-dE)
    row=[gl,window,float(u),E,float(h.mean()),W,*P,*h,*ell,*we,w2,kk,rr,ratio,identity,trace,con,
         dE,*dP,*dh,*de,*dw,dc2,dk,dric,dratio,dident,dtrace,dcon,*(-.75*an*u*u),coeff*u*u]
    if len(row)!=len(BASE_COLS):raise RuntimeError('invalid science CSV')
    a.append(row)
    for sign in (-1,1):
     yn=family[sign][ix];hn=yn[3:];ln=yn[:3]
     En,Pn,*_=src.ancestor.moment(r2,mf[sign],ln,with_r=False)
     en,w2n,kn,rn,ratio_n,ident_n,_=curv(hn,Pn,En)
     wn=float((hn-hn.mean())@(Pn-En/3));cn=float(hn[0]*hn[1]+hn[0]*hn[2]+hn[1]*hn[2]-En)
     b.append([gl,window,float(u),eps,sign,En,float(hn.mean()),wn,*Pn,*hn,*ln,*en,
                w2n,kn,rn,ratio_n,ident_n,cn])
   I2=BASE_COLS.index('dWeylSq');fi=FIN_COLS.index('WeylSq')
   errors=[]
   for j,v in enumerate(a):
    numer=(b[2*j+1][fi]-b[2*j][fi])/(2*eps)
    errors.append(abs(numer-v[I2]))
   report={'GL':gl,'window':window,'epochs':epochs,'physical_rows':len(a)+len(b),
      'end_WeylSq':a[-1][BASE_COLS.index('WeylSq')],
      'end_dWeylSq':a[-1][I2],
      'end_dK':a[-1][BASE_COLS.index('dKretschmann')],
      'end_dRicciSq':a[-1][BASE_COLS.index('dRicciSq')],
      'max_FD_error_WeylSq':max(errors),
      'max_constraint':max(abs(v[BASE_COLS.index('einstein_constraint')]) for v in a),
      'max_identity':max(abs(v[BASE_COLS.index('curvature_identity_residual')]) for v in a),
      'max_didentity':max(abs(v[BASE_COLS.index('dcurvature_identity_residual')]) for v in a)}
   s[str(gl)][window]=report
   allrows+=a;allfinite+=b
   print('CE1AL_REMOTE',gl,window,'W2diff',report['end_dWeylSq'],'FD',report['max_FD_error_WeylSq'],flush=True)
 for name,cols,rows in [('CE1AL_WEYL_CURVATURE_TANGENT.csv',BASE_COLS,allrows),('CE1AL_NONLINEAR_SOURCE_CURVATURE.csv',FIN_COLS,allfinite)]:
  with (out/name).open('w',newline='') as f:
   writer=csv.writer(f);writer.writerow(cols);writer.writerows(rows)
 result={'schema':'bass.ce1al.independent_remote_Weyl_curvature.v1','source_sha256':SOURCE_SHA,
    'parent_pr':292,'parent_head':'607aa819c7e3239c4c858884400333195587fd3d',
    'source_family':'original DARK_L2L4 derivative; source unchanged',
    'row_counts':{'tangent':len(allrows),'nonlinear':len(allfinite),'total':len(allrows)+len(allfinite)},
    'kappa_numeric':coeff,'rational_bounds':c['kappa_floats'],'results':s,'DAG':'9/15',
    'CE1':'PARTIAL','new_upper_nodes':0,'production_ready':False,'merge_ready':False}
 (out/'CE1AL_REMOTE_CURVATURE_RESULTS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
 (out/'CE1AL_EXACT_WEYL_REMOTE_CERT.json').write_text(json.dumps(c,indent=2,allow_nan=False)+'\n')
 return result
if __name__=='__main__':replay()
