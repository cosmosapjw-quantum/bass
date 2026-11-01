#!/usr/bin/env python3
"""Source-bound CE1AR fixed-observed-redshift Sachs atlas, GitHub CI implementation.

Reuses original CE1AP 9 Einstein-Vlasov solutions reconstructed by ancestor CI.
No independent Einstein rerun here; no opacity, likelihood, or FLRW-owner claim.
"""
import csv,json,math,sys
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.integrate import simpson
from scipy.optimize import brentq
HERE=Path(__file__).resolve().parent
RESEARCH=HERE.parents[1]
sys.path.insert(0,str(RESEARCH/'ce1aq_20261101'/'source'))
import ce1aq_remote as parent
GLS=(8,16,24); EPS=(-.035,0.,.035); ZS=(.005,.01,.015,.02,.025,.03); UO=.08
SOURCE='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
FULL=['GL','eps','z','direction','nx','ny','nz','u_em','D_A','D_A_saunders','gap','isotropic_proxy_D_A','anisotropy','redshift_gap']
RESP=['GL','z','direction','nx','ny','nz','u_minus','u_base','u_plus','D_A_minus','D_A_base','D_A_plus','source_secant','direct_fixed_time','clock_term','implicit_sum','implicit_gap']

def nn(x):
 a=np.asarray(x,float);return a/np.linalg.norm(a)

def rad(L,u,n):
 f=L(u)-L(UO);return .5*math.log(float((n*n)@np.exp(-2*f)))

def emitter(L,z,n):
 target=math.log1p(z)
 if rad(L,0,n)<target:raise ArithmeticError('out-of-horizon redshift')
 ue=brentq(lambda u:rad(L,u,n)-target,0,UO,xtol=5e-15,rtol=9e-16)
 gap=abs(math.expm1(rad(L,ue,n))-z)
 if gap>5e-13:raise ArithmeticError('redshift root failure')
 return ue,gap

def screen(L,ue,n):
 t=np.linspace(ue,UO,257);a=np.exp(L(t)-L(UO));v=1/a**2
 E=np.sqrt(np.einsum('i,ti->t',n*n,v))
 J=np.diag(simpson(v/E[:,None],x=t,axis=0))
 w=n[None,:]*v
 J-=simpson(np.einsum('ti,tj->tij',w,w)/E[:,None,None]**3,x=t,axis=0)
 pole=np.array([0.,0.,1.]) if abs(n[2])<.9 else np.array([0.,1.,0.])
 b1=np.cross(pole,n);b1/=np.linalg.norm(b1); b=np.column_stack((b1,np.cross(n,b1)))
 s=n/a[0]/E[0];B=a[0,:,None]*(J@b);P=np.eye(3)-np.outer(s,s)
 gram=B.T@P@B;ev=np.linalg.eigvalsh(gram)
 if ev[0]<=0:raise ArithmeticError('invalid beam')
 da=float(np.sqrt(np.sqrt(ev[0]*ev[1])))
 av=np.cbrt(np.prod(a,axis=1));I=simpson(a*a/(av[:,None]**6*E[:,None]**3),x=t,axis=0)
 d=n[0]**2*I[1]*I[2]+n[1]**2*I[0]*I[2]+n[2]**2*I[0]*I[1]
 sau=float(av[0]*math.sqrt(float(av[0]*E[0]*d)))
 return da,sau,float((da-sau)/sau)

def isotropic(L,z):
 lv=lambda u:float(np.mean(L(u)))
 ue=brentq(lambda u:lv(UO)-lv(u)-math.log1p(z),0,UO,xtol=5e-15,rtol=9e-16)
 t=np.linspace(ue,UO,257);a=np.exp(np.mean(L(t),axis=1)-lv(UO))
 return float(a[0]*simpson(1/a,x=t))

def export(path,header,rows):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('w',newline='') as f:
  w=csv.writer(f);w.writerow(header);w.writerows(rows)

def run():
 if parent.SOURCE!=SOURCE:raise ArithmeticError('upstream immutable source changed')
 hist,t=parent.metric();directions=parent.directions()
 if len(hist)!=9 or len(directions)!=103 or len(t)!=401:raise ArithmeticError('owner source missing')
 out=HERE.parent/'data';out.mkdir(parents=True,exist_ok=True)
 beams=[];respond=[];stats={}
 for gl in GLS:
  series={ep:PchipInterpolator(t,hist[(gl,ep)],axis=0,extrapolate=False) for ep in EPS}
  iso={(ep,z):isotropic(series[ep],z) for ep in EPS for z in ZS}
  root_max=gap_max=implicit_max=0.
  for z in ZS:
   for key,vec in directions:
    n=nn(vec);d={}
    for ep in EPS:
     L=series[ep];ue,res=emitter(L,z,n);da,sau,gap=screen(L,ue,n)
     anis=da/iso[(ep,z)]-1
     beams.append([gl,ep,z,key,*n,ue,da,sau,gap,iso[(ep,z)],anis,res]);d[ep]=(ue,da,anis)
     root_max=max(root_max,res);gap_max=max(gap_max,abs(gap))
    minus,base,plus=[d[ep] for ep in EPS]
    finite=(plus[1]-minus[1])/.07
    ub=base[0];fixed=(screen(series[.035],ub,n)[0]-screen(series[-.035],ub,n)[0])/.07
    derivative=((rad(series[.035],ub,n)-rad(series[-.035],ub,n))/.07)
    h=series[0.].derivative()(ub)
    f=series[0.](ub)-series[0.](UO);weights=n*n*np.exp(-2*f);weights/=weights.sum()
    slope=-float(weights@h)
    if slope>=0:raise ArithmeticError('non-monotonic expansion')
    du=-derivative/slope
    step=min(2e-4,ub/4,(UO-ub)/4)
    optical_slope=(screen(series[0.],ub+step,n)[0]-screen(series[0.],ub-step,n)[0])/(2*step)
    clock=optical_slope*du;total=fixed+clock
    implicit_max=max(implicit_max,abs(total-finite))
    respond.append([gl,z,key,*n,minus[0],base[0],plus[0],minus[1],base[1],plus[1],finite,fixed,clock,total,total-finite])
  stats[str(gl)]={'ray_rows':len(EPS)*len(ZS)*len(directions), 'response_rows':len(ZS)*len(directions),
     'max_redshift_gap':root_max,'max_jacobi_saunders_gap':gap_max,'max_implicit_absolute_gap':implicit_max}
  print('CE1AR_REAL_PHYSICS',gl,stats[str(gl)],flush=True)
 if len(beams)!=5562 or len(respond)!=1854:raise ArithmeticError('atlas incomplete')
 export(out/'CE1AR_FIXED_Z_REMOTE_BEAMS.csv',FULL,beams)
 export(out/'CE1AR_FIXED_Z_REMOTE_RESPONSE.csv',RESP,respond)
 info={'schema':'bass.ce1ar.original_source_fixed_z_remote.v1','parent_ce1aq_head':'bbebf7f0cdc3e23eec422f67118e8d402afb106c',
  'source_sha256':SOURCE,'original_owner':'CE1AP original nine six-cell Einstein-Vlasov IVPs',
  'new_Einstein_IVPs':0,'reused_owner_IVPs':9,'real_beam_rows':len(beams),'source_response_rows':len(respond),
  'z_shells':ZS,'direction_count':len(directions),'GL':stats,'upper_BASS':'9/15 scoped source-mapped',
  'CE1':'PARTIAL','OB1_full_accepted':False,'new_upper_nodes':0,'production':False,'merge':False,'auto_next':False,
  'isotropic_control':'equal-volume kinematic proxy NOT independently solved FLRW',
  'real_observation_likelihood':False,'matched_REI_owner':False}
 (out/'CE1AR_REMOTE_RESULTS.json').write_text(json.dumps(info,indent=2,allow_nan=False)+'\n')
 return info
if __name__=='__main__':run()
