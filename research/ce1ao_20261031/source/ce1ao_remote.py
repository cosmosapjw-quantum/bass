#!/usr/bin/env python3
"""CE1AO remote: original six-cell nonthermal bolometric l2/l4/l6/l8 sky.
Source and ancestry immutable; no new IVPs; not a Planck likelihood.
"""
import csv, json, math, sys
from pathlib import Path
import numpy as np
from scipy.special import lpmv
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
RESEARCH=ROOT.parent
sys.path.insert(0,str(RESEARCH/'ce1ai_20261031'/'source'))
import ce1ai_source_response as src
SOURCE="022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035"
PARENT="61257246883df00ff478aeb5e8317d46e25702ce"
ORDERS=(8,16,24)
EPS=(-.035,-.025,-.01,0.,.01,.025,.035)
FIELDS=["GL","eps","u","E_sky","dE_from_Einstein","P_gap",
"C2","C4","C6","C8","alpha20","alpha22","alpha40","alpha42","alpha44",
"alpha60","alpha62","alpha64","alpha66","alpha80","alpha82","alpha84","alpha86","alpha88","m4_cartesian_gap","m6_cartesian_gap"]
def spectral(r2,m,ell):
 q=r2*np.exp(-2*np.asarray(ell)[None,:]);r=np.sqrt(np.sum(q,axis=1))
 x=q/(r[:,None]**2);omega=m*r*np.exp(-sum(ell));E=float(sum(omega))
 P=omega@x
 z=np.sqrt(x[:,2]);c2=(x[:,0]-x[:,1])/(x[:,0]+x[:,1])
 cs={0:np.ones(len(z)),2:c2,4:2*c2*c2-1,6:4*c2**3-3*c2,8:2*(2*c2*c2-1)**2-1}
 A={};C={}
 for l in (2,4,6,8):
  for mm in range(0,l+1,2):
   n=math.sqrt((2*l+1)/(4*math.pi)*math.factorial(l-mm)/math.factorial(l+mm))
   A[(l,mm)]=4*math.pi/E*float(np.dot(omega,n*lpmv(mm,l,z)*cs[mm]))
  C[l]=(A[(l,0)]**2+2*sum(A[(l,k)]**2 for k in range(2,l+1,2)))/(2*l+1)
 cart4=(3/16*math.sqrt(35/(2*math.pi)))*(x[:,0]**2-6*x[:,0]*x[:,1]+x[:,1]**2)
 cart6=math.sqrt(13/(4*math.pi)*2/ math.factorial(10))*(945/2)*(11*x[:,2]-1)*(x[:,0]**2-6*x[:,0]*x[:,1]+x[:,1]**2)
 return E,P,A,C,A[(4,4)]-4*math.pi/E*float(omega@cart4),A[(6,4)]-4*math.pi/E*float(omega@cart6)
def run():
 if src.validate_immutable()!=SOURCE:raise RuntimeError('original source SHA drift')
 inp=RESEARCH/'ce1an_20261031'/'data'/'CE1AN_FINITE_SOURCE_PHYSICS.csv'
 with inp.open(newline='') as f:parent=list(csv.DictReader(f))
 if len(parent)!=8421:raise RuntimeError('missing original source-owned physical histories')
 out=ROOT/'data';out.mkdir(parents=True,exist_ok=True)
 results=[];summ={}
 prev=None
 for v in parent:
  gl=int(v['GL']);eps=float(v['eps']);t=float(v['u'])
  if gl!=prev:
   rays,m0=src.make_cell_rays(gl);r2=rays*rays
   dm=src.ray_source_basis(gl,m0)[-1]
   prev=gl
  m=m0+eps*dm
  if min(m)<=0:raise RuntimeError('invalid negative source family')
  ell=[float(v['ell'+str(i)]) for i in (1,2,3)]
  E,P,A,C,g4,g6=spectral(r2,m,ell)
  pg=float(max(abs(P-np.array([float(v['P'+str(j)]) for j in (1,2,3)]))))
  e_gap=E-float(v['E'])
  if max(pg,abs(e_gap),abs(g4),abs(g6))>1e-10:raise RuntimeError('physical harmonic mismatch')
  row=[gl,eps,t,E,e_gap,pg,*[C[l] for l in (2,4,6,8)],*[A[(l,k)] for l in (2,4,6,8) for k in range(0,l+1,2)],g4,g6]
  if len(row)!=len(FIELDS):raise RuntimeError('invalid field schema')
  results.append(row)
  key=str(gl);s=summ.setdefault(key,{'rows':0,'max_E_gap':0.,'max_P_gap':0.,'max_l6_cartesian_gap':0.,'initial':{},'horizon':{}})
  s['rows']+=1;s['max_E_gap']=max(s['max_E_gap'],abs(e_gap));s['max_P_gap']=max(s['max_P_gap'],pg)
  s['max_l6_cartesian_gap']=max(s['max_l6_cartesian_gap'],abs(g6))
  if t==0 or abs(t-.08)<1e-12:
   trg=s['initial' if t==0 else 'horizon']
   trg[str(eps)]={'C2':C[2],'C4':C[4],'C6':C[6],'C8':C[8],'alpha44':A[(4,4)],'alpha64':A[(6,4)]}
 with (out/'CE1AO_REMOTE_SKY.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(FIELDS);w.writerows(results)
 expected=-5.302758811735706
 for gl,s in summ.items():
  ini=s['initial']
  da=(ini['0.035']['alpha64']-ini['-0.035']['alpha64'])/.07
  if abs(da-expected)>3e-9:raise RuntimeError('exact initial source l6 slope error')
  if abs(ini['0.035']['C4']-ini['0.0']['C4'])>1e-9:raise RuntimeError('invalid initial dark C4')
 payload={'schema':'bass.ce1ao.remote_sky_replay.v1','source_sha256':SOURCE,'parent_head':PARENT,
  'new_sky_physical_rows':len(results),'reused_parent_IVPs':24,'new_ivps':0,
  'exact_initial_dalpha64':expected,'GL':summ,'upper_DAG':'9/15','new_upper_nodes':0,
  'CMB_likelihood':False,'continuum_horizon_weyl_sign_proved':False,
  'production':False,'merge':False,'auto_next':False}
 (out/'CE1AO_REMOTE_RESULTS.json').write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
 print('CE1AO_REMOTE_SUCCESS',len(results),'GL24_C6_initial',summ['24']['initial']['0.0']['C6'])
 return payload
if __name__=='__main__':run()
