#!/usr/bin/env python3
"""CE1AQ source-frozen Einstein–Vlasov Bianchi I optical Jacobi and Saunders atlas.
NO new Einstein IVPs. Uses original parent PR301 source-locked CE1AP physical rays.
"""
from __future__ import annotations
import csv, math, json, sys
from pathlib import Path
import numpy as np
from scipy.integrate import simpson
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
RESEARCH=ROOT.parent
SOURCE='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
IMMUTABLE_PARENT='baef3a4b5a556703f2e2feb93b57da6b364d29fd'
CE1AP_PARENT='d94843f2b63638d36244d951eccdbb81f3a64357'
ORDERS=(8,16,24);EP=(-.035,0.,.035)
EM=(0,40,80,120,160,200,240,320)
HEADER=['GL','eps','u_emit','u_obs','direction','nx','ny','nz','redshift_1plusz',
  'D_A_over_cTstar','D_A_saunders_over_cTstar','D_A_Jacobi_relative_gap',
  'beam_s1_over_cTstar','beam_s2_over_cTstar','beam_ellipticity','screen_det']
RESP=['GL','u_emit','direction','nx','ny','nz','D_A_minus','D_A_base','D_A_plus',
  'dD_A_plus','dD_A_minus','central_secant_D_A','dD_A_relative_secant',
  'ellipticity_minus','ellipticity_base','ellipticity_plus','central_secant_ellipticity',
  'redshift_minus','redshift_base','redshift_plus']
def directions():
  out=[('x',(1.,0.,0.)),('y',(0.,1.,0.)),('z',(0.,0.,1.)),
   ('xy',(2**-.5,2**-.5,0.)),('xz',(2**-.5,0.,2**-.5)),
   ('yz',(0.,2**-.5,2**-.5)),('xyz',(3**-.5,)*3)]
  phi=(1+math.sqrt(5))/2
  for i in range(96):
    z=1-2*(i+.5)/96; t=2*math.pi*(i/phi%1);r=math.sqrt(1-z*z)
    out.append((f'fib{i:02d}',(r*math.cos(t),r*math.sin(t),z)))
  return out
def metric():
  inp=RESEARCH/'ce1ap_20261031'/'data'/'CE1AP_DIRECTIONAL_GEODESIC.csv'
  meta=RESEARCH/'ce1ap_20261031'/'data'/'CE1AP_REMOTE_RESULTS.json'
  a=json.loads(meta.read_text())
  if a.get('source_sha256')!=SOURCE or a.get('parent_head')!=CE1AP_PARENT or a.get('new_IVPs')!=9:
    raise RuntimeError('Original CE1AP six-cell source and parent identity mismatch')
  with inp.open(newline='') as f:rows=list(csv.DictReader(f))
  if len(rows)!=16842: raise RuntimeError('Original source rays missing')
  out={}
  for gl in ORDERS:
    for ep in EP:
      data=[r for r in rows if int(r['GL'])==gl and float(r['eps'])==(ep if ep else -.035)]
      axes=[]
      for name in 'xyz':
        q=sorted([r for r in data if r['dir']==name],key=lambda r:float(r['u']))
        if len(q)!=401:raise RuntimeError('Incorrect original ray clock')
        axes.append(q)
      t=np.array([float(q['u']) for q in axes[0]])
      if np.max(np.abs(t-np.linspace(0,.08,401)))>1e-14:raise RuntimeError('Original ray clock drift')
      ell=np.array([[-float(v['ln_R_base'])-(0 if not ep else float(v['delta_ln_R'])) for v in q] for q in axes]).T
      if not np.isfinite(ell).all() or np.max(np.abs(ell[0]))>1e-14: raise RuntimeError('Invalid original metric')
      out[(gl,ep)]=ell
  return out,t
def optical(ell,t,n,j):
  n=np.array(n,dtype=float);n/=np.linalg.norm(n)
  a=np.exp(ell[j:]-ell[-1]);inv=1/a**2
  E=np.sqrt(np.sum(n[None,:]**2*inv,axis=1));time=t[j:]
  x=np.eye(3)[None,:,:]*(inv/E[:,None])[:,:,None]
  y=np.einsum('ti,tj->tij',n[None,:]*inv,n[None,:]*inv)/E[:,None,None]**3
  J=simpson(x-y,x=time,axis=0)
  pole=np.array([0.,0.,1.]) if abs(n[2])<.9 else np.array([0.,1.,0.])
  v=np.cross(pole,n);v/=np.linalg.norm(v);b=np.column_stack([v,np.cross(n,v)])
  s=n/a[0]/E[0];B=a[0,:,None]*(J@b)
  gram=B.T@(np.eye(3)-np.outer(s,s))@B
  eig=np.linalg.eigvalsh(gram)
  if eig[0]<=0:raise RuntimeError('Unphysical sampled beam')
  l1,l2=np.sqrt(eig[0]),np.sqrt(eig[1])
  DA=math.sqrt(l1*l2);dist=(l2-l1)/(l1+l2)
  av=np.cbrt(np.prod(a,axis=1))
  I=simpson(a**2/(av[:,None]**6*E[:,None]**3),x=time,axis=0)
  D=n[0]**2*I[1]*I[2]+n[1]**2*I[0]*I[2]+n[2]**2*I[0]*I[1]
  sau=av[0]*math.sqrt(av[0]*E[0]*D)
  return float(E[0]),DA,sau,(DA-sau)/sau,float(l1),float(l2),float(dist),float(np.linalg.det(gram))
def write(path,cols,rows):
  path.parent.mkdir(parents=True,exist_ok=True)
  with path.open('w',newline='') as f:
    w=csv.writer(f);w.writerow(cols);w.writerows(rows)
def run():
  hist,t=metric();full=[];resp=[];report={}
  for gl in ORDERS:
    gap=0.
    for j in EM:
      for name,n in directions():
        states={}
        for ep in EP:
          r=optical(hist[(gl,ep)],t,n,j);states[ep]=r
          gap=max(gap,abs(r[3]))
          full.append([gl,ep,float(t[j]),.08,name,*n,*r])
        m,b,p=[states[ep] for ep in EP]
        sec=(p[1]-m[1])/.07
        resp.append([gl,float(t[j]),name,*n,m[1],b[1],p[1],p[1]-b[1],
          m[1]-b[1],sec,sec/b[1],m[6],b[6],p[6],(p[6]-m[6])/.07,
          m[0],b[0],p[0]])
    report[str(gl)]={'rows':3*len(EM)*len(directions()),'max_Saunders_Jacobi_gap':gap}
    print('CE1AQ_REMOTE',gl,report[str(gl)],flush=True)
  if len(full)!=7416 or len(resp)!=2472:raise RuntimeError('Incomplete sourced optical sky')
  out=ROOT/'data'
  write(out/'CE1AQ_BEAM_PHYSICAL.csv',HEADER,full)
  write(out/'CE1AQ_SOURCE_BEAM_RESPONSE.csv',RESP,resp)
  report={'schema':'bass.ce1aq.remote_original_beam.v1','parent_head':IMMUTABLE_PARENT,
    'source_sha256':SOURCE,'new_Einstein_IVPs':0,'reused_parent_IVPs':9,
    'original_optical_rows':len(full),'new_source_response_rows':len(resp),
    'BASS_CE1_upper':'9/15','new_upper_nodes':0,
    'full_continuum_Weyl_sign':False,'Planck_CMB_likelihood':False,
    'production':False,'merge':False,'auto_next':False,'GL':report}
  (out/'CE1AQ_REMOTE_RESULTS.json').write_text(json.dumps(report,indent=2)+'\n')
  return report
if __name__=='__main__':run()
