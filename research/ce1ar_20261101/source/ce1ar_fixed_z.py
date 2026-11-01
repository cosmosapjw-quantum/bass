#!/usr/bin/env python3
"""BASS CE1AR: source-owned fixed-observed-redshift Bianchi-I Sachs distances.

No new Einstein IVPs and no cross-owner metric substitution. Input is the frozen
CE1AP six-cell geodesic history (401 u points, nine original physical models).
All calculated D_A values are in original c*Tstar units, observer-normal sky.
The isotropized equal-volume curve is a KINEMATIC comparator, not an FLRW IVP.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.integrate import simpson
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq

SOURCE_SHA = '022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
PARENT_CE1AQ = 'bbebf7f0cdc3e23eec422f67118e8d402afb106c'
PARENT_CE1AP = 'baef3a4b5a556703f2e2feb93b57da6b364d29fd'
CE1AP_SOURCE_PARENT = 'd94843f2b63638d36244d951eccdbb81f3a64357'
S2_ANCESTOR_INPUT_SHA = '98bd1ed2909abfc5e47da12003354d6a3c75bee8ef0ecc13144b1a4c110a1207'
ORDERS = (8, 16, 24)
EPS = (-.035, 0., .035)
SHELLS = (.005, .010, .015, .020, .025, .030)
OBS_U = .08

FIELDS = (
 'GL','eps','z_target','direction','nx','ny','nz','u_emit','u_observer',
 'reconstructed_z','redshift_abs_residual','D_A_over_cTstar',
 'D_A_saunders_over_cTstar','D_A_jacobi_saunders_rel_gap',
 'beam_s1','beam_s2','beam_ellipticity','screen_det',
 'equal_volume_isotropic_D_A','fractional_anisotropy_vs_isotropic_proxy',
 'input_model','source_sha256')
RESP = (
 'GL','z_target','direction','nx','ny','nz','u_emit_minus','u_emit_base',
 'u_emit_plus','u_emit_plus_minus_base','D_A_minus','D_A_base','D_A_plus',
 'delta_D_A_plus','central_secant_D_A_at_fixed_z',
 'direct_D_A_secant_at_fixed_emission_clock','emitter_clock_response_term',
 'implicit_total_source_response','implicit_minus_actual_abs_gap',
 'fractional_source_response_at_fixed_z',
 'anisotropy_minus','anisotropy_base','anisotropy_plus')


def sha256(path):
 return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def directions():
 out=[('x',(1.,0.,0.)),('y',(0.,1.,0.)),('z',(0.,0.,1.)),
      ('xy',(2**-.5,2**-.5,0.)),('xz',(2**-.5,0.,2**-.5)),
      ('yz',(0.,2**-.5,2**-.5)),('xyz',(3**-.5,)*3)]
 golden=(1+math.sqrt(5))/2
 for k in range(96):
  v=1-2*(k+.5)/96; phi=2*math.pi*(k/golden % 1)
  s=math.sqrt(1-v*v)
  out.append((f'fib{k:02d}',(s*math.cos(phi),s*math.sin(phi),v)))
 return out


@dataclass(frozen=True)
class Geometry:
 u: np.ndarray
 ell: np.ndarray
 h: np.ndarray
 gl: int
 eps: float

 def __post_init__(self):
  if self.ell.shape != (401,3) or self.h.shape != (401,3) or self.u.shape != (401,):
   raise ValueError('wrong source owner state shape')
  if np.min(self.h)<=0 or not np.all(np.isfinite(self.ell)):
   raise ValueError('nonexpanding or invalid frozen source state')

 @property
 def L(self):
  return PchipInterpolator(self.u,self.ell,axis=0,extrapolate=False)
 @property
 def H(self):
  return PchipInterpolator(self.u,self.h,axis=0,extrapolate=False)


def load_original(input_csv, metadata, *, strict_sha=False):
 input_csv=Path(input_csv)
 raw_hash=sha256(input_csv)
 if strict_sha and raw_hash!=S2_ANCESTOR_INPUT_SHA:
  raise ArithmeticError('immutable original CE1AP S2 input SHA mismatch')
 if metadata is None:raise ValueError('source metadata is mandatory')
 meta=json.loads(Path(metadata).read_text())
 if meta.get('source_sha256')!=SOURCE_SHA:
  raise ArithmeticError('original six-cell physical source SHA mismatch')
 if meta.get('schema','').startswith('bass.ce1aq.original_ancestor_bound'):
  if meta.get('parent_head')!=PARENT_CE1AP or meta.get('original_ce1ap_geodesic_csv_sha256')!=raw_hash:
   raise ArithmeticError('original CE1AQ ancestor receipt mismatch')
 else:
  if meta.get('parent_head')!=CE1AP_SOURCE_PARENT or meta.get('new_IVPs')!=9:
   raise ArithmeticError('original CE1AP science-owner metadata mismatch')
 with input_csv.open(newline='') as handle: rows=list(csv.DictReader(handle))
 if len(rows)!=16842:raise ArithmeticError(f'bad original parent rows {len(rows)}')
 grouped={}
 for row in rows:
  if row['dir'] not in ('x','y','z'):continue
  key=(int(row['GL']),float(row['eps']),row['dir'])
  grouped.setdefault(key,[]).append(row)
 hist={}
 uref=None
 for gl in ORDERS:
  for eps in EPS:
   key_eps=eps if eps!=0 else EPS[0]
   def column(direction,name,offset):
    rr=sorted(grouped[(gl,key_eps,direction)],key=lambda v:float(v['u']))
    if len(rr)!=401:raise ArithmeticError('wrong owner ray clock density')
    return np.asarray([float(x[name])+offset*float(x.get('delta_'+name,0)) for x in rr]),np.asarray([float(x['u']) for x in rr])
   axes_ell=[]; axes_h=[]
   for direction in 'xyz':
    rr=sorted(grouped[(gl,key_eps,direction)],key=lambda v:float(v['u']))
    if len(rr)!=401:raise ArithmeticError('wrong axis rows')
    u=np.asarray([float(x['u']) for x in rr])
    axes_ell.append(np.asarray([-float(x['ln_R_base']) - (float(x['delta_ln_R']) if eps else 0) for x in rr]))
    axes_h.append(np.asarray([-float(x['drift_base']) - (float(x['delta_drift']) if eps else 0) for x in rr]))
    if uref is None:uref=u
    if np.max(np.abs(u-uref))>1e-14:raise ArithmeticError('source clock inconsistency')
   ell=np.column_stack(axes_ell);h=np.column_stack(axes_h)
   if np.max(np.abs(ell[0]))>1e-14 or np.max(np.abs(u-np.linspace(0,OBS_U,401)))>1e-14:
    raise ArithmeticError('invalid parent observer clock or initial scale factor')
   hist[(gl,eps)]=Geometry(u,ell,h,gl,eps)
 return hist,{'input_sha256':raw_hash,'parent_source_sha256':SOURCE_SHA,
               'local_S2_byte_exact':raw_hash==S2_ANCESTOR_INPUT_SHA,
               'metadata_schema':meta.get('schema'),'reused_original_IVPs':9}


def normalize(n):
 n=np.asarray(n,dtype=float)
 return n/np.linalg.norm(n)


def basis(n):
 n=normalize(n)
 pole=np.array([0.,0.,1.]) if abs(n[2])<.9 else np.array([0.,1.,0.])
 b1=np.cross(pole,n); b1/=np.linalg.norm(b1)
 return np.column_stack((b1,np.cross(n,b1)))


def log_redshift(model,u_emit,n):
 n=normalize(n)
 f=model.L(u_emit)-model.ell[-1]
 return .5*math.log(float(np.dot(n*n,np.exp(-2*f))))


def solve_emitter(model,z,n):
 if z<=0:raise ValueError('positive observed redshift required')
 target=math.log1p(z)
 if log_redshift(model,model.u[0],n)<target:
  raise ValueError('redshift outside owner physical horizon, no extrapolation')
 emitter=brentq(lambda ue:log_redshift(model,ue,n)-target,
   float(model.u[0]),float(model.u[-1]),xtol=5e-15,rtol=9e-16)
 residual=abs(math.expm1(log_redshift(model,emitter,n))-z)
 if residual>5e-13:raise ArithmeticError('fixed-observed-redshift root residual')
 return float(emitter),float(residual)


def optical_at_emitter(model,u_emit,n, *, panels=257):
 if panels<65 or panels%2!=1:raise ValueError('odd Simpson panel sample count >= 65 required')
 n=normalize(n)
 t=np.linspace(u_emit,float(model.u[-1]),panels)
 a=np.exp(model.L(t)-model.ell[-1]); a2=a*a; inva2=1/a2
 E=np.sqrt(np.einsum('i,ti->t',n*n,inva2))
 invE=inva2/E[:,None]
 J=np.diag(simpson(invE,x=t,axis=0))
 v=n[None,:]*inva2
 J-=simpson(np.einsum('ti,tj->tij',v,v)/E[:,None,None]**3,x=t,axis=0)
 s=n/a[0]/E[0]
 B=a[0,:,None]*(J@basis(n))
 gram=B.T@(np.eye(3)-np.outer(s,s))@B
 eigen=np.linalg.eigvalsh((gram+gram.T)/2)
 if eigen[0]<=0:raise ArithmeticError('nonpositive sampled beam determinant')
 s1,s2=np.sqrt(eigen)
 DA=math.sqrt(float(s1*s2))
 eta=float((s2-s1)/(s1+s2))
 av=np.cbrt(np.prod(a,axis=1))
 Ii=simpson(a2/(av[:,None]**6 * E[:,None]**3),x=t,axis=0)
 delta=n[0]**2*Ii[1]*Ii[2]+n[1]**2*Ii[0]*Ii[2]+n[2]**2*Ii[0]*Ii[1]
 sau=float(av[0]*math.sqrt(float(av[0]*E[0]*delta)))
 if not (DA>0 and sau>0 and 0<=eta<1):raise ArithmeticError('invalid physical distance or ellipticity')
 return {'redshift':float(E[0]-1),'DA':DA,'saunders':sau,'gap':float((DA-sau)/sau),
   's1':float(s1),'s2':float(s2),'ellipticity':eta,'det':float(np.linalg.det(gram))}


def isotropic_equal_volume_proxy(model,z,*,panels=257):
 """Directional null: same a_volume(u) but a_i->a_volume; NOT an FLRW Einstein owner."""
 lv=PchipInterpolator(model.u,np.mean(model.ell,axis=1),extrapolate=False)
 end=float(lv(model.u[-1]))
 target=math.log1p(z)
 if end-float(lv(model.u[0]))<target:raise ValueError('no isotropic proxy root')
 ue=brentq(lambda u:end-float(lv(u))-target,0,float(model.u[-1]),xtol=5e-15,rtol=9e-16)
 t=np.linspace(ue,float(model.u[-1]),panels)
 normalized=np.exp(lv(t)-end)
 DA=float(normalized[0]*simpson(1/normalized,x=t))
 return DA


def implicit_response(minus,base,plus,n,z, *,panels=257):
 ue0,_=solve_emitter(base,z,n)
 ue_minus,_=solve_emitter(minus,z,n)
 ue_plus,_=solve_emitter(plus,z,n)
 F_plus=log_redshift(plus,ue0,n)
 F_minus=log_redshift(minus,ue0,n)
 f_deps=(F_plus-F_minus)/(.07)
 ell0=base.L(ue0)-base.ell[-1]
 weights=n*n*np.exp(-2*ell0);weights/=weights.sum()
 f_due=-float(weights@base.H(ue0))
 if f_due>=0:raise ArithmeticError('nonmonotone source geometry')
 du_deps=-f_deps/f_due
 pp=optical_at_emitter(plus,ue0,n,panels=panels)['DA']
 mm=optical_at_emitter(minus,ue0,n,panels=panels)['DA']
 direct=(pp-mm)/.07
 delta=min(2e-4,ue0/4,(OBS_U-ue0)/4)
 dp=optical_at_emitter(base,ue0+delta,n,panels=panels)['DA']
 dm=optical_at_emitter(base,ue0-delta,n,panels=panels)['DA']
 dDA_du=(dp-dm)/(2*delta)
 clock=dDA_du*du_deps
 return {'direct':float(direct),'clock':float(clock),'prediction':float(direct+clock),
   'ue_base':ue0,'ue_minus':ue_minus,'ue_plus':ue_plus,'dueps':du_deps}


def write_csv(path,headers,rows):
 with Path(path).open('w',newline='',encoding='utf-8') as handle:
  w=csv.writer(handle);w.writerow(headers);w.writerows(rows)


def execute(input_csv,meta,output,*,strict_sha=False,panels=257):
 output=Path(output);output.mkdir(parents=True,exist_ok=True)
 geom,provenance=load_original(input_csv,meta,strict_sha=strict_sha)
 sky=directions()
 full=[];resp=[];stats={}
 for gl in ORDERS:
  maxgap=0.;maxroot=0.;maximplicit=0.;minDA=math.inf
  iso={(ep,z):isotropic_equal_volume_proxy(geom[(gl,ep)],z,panels=panels) for ep in EPS for z in SHELLS}
  for z in SHELLS:
   for label,arr in sky:
    n=normalize(arr);state={}
    for ep in EPS:
     model=geom[(gl,ep)];ue,r=solve_emitter(model,z,n)
     cur=optical_at_emitter(model,ue,n,panels=panels)
     v_iso=iso[(ep,z)]
     anis=cur['DA']/v_iso-1
     full.append([gl,ep,z,label,*n,ue,OBS_U,cur['redshift'],r,cur['DA'],cur['saunders'],cur['gap'],
                  cur['s1'],cur['s2'],cur['ellipticity'],cur['det'],v_iso,anis,
                  'original CE1AP nine self-consistent Bianchi I IVPs',SOURCE_SHA])
     state[ep]=(ue,cur,anis)
     maxgap=max(maxgap,abs(cur['gap']));maxroot=max(maxroot,r);minDA=min(minDA,cur['DA'])
    minus,baseline,plus=[state[ep] for ep in EPS]
    sec=(plus[1]['DA']-minus[1]['DA'])/.07
    imp=implicit_response(geom[(gl,-.035)],geom[(gl,0.)],geom[(gl,.035)],n,z,panels=panels)
    diff=imp['prediction']-sec
    maximplicit=max(maximplicit,abs(diff))
    resp.append([gl,z,label,*n,minus[0],baseline[0],plus[0],plus[0]-baseline[0],
      minus[1]['DA'],baseline[1]['DA'],plus[1]['DA'],plus[1]['DA']-baseline[1]['DA'],sec,
      imp['direct'],imp['clock'],imp['prediction'],diff,sec/baseline[1]['DA'],
      minus[2],baseline[2],plus[2]])
  stats[str(gl)]={'new_fixed_z_ray_records':len(SHELLS)*len(sky)*len(EPS),
    'new_fixed_z_response_records':len(SHELLS)*len(sky),
    'max_jacobi_saunders_relative_gap':maxgap,
    'max_fixed_z_root_absolute_error':maxroot,
    'max_implicit_response_absolute_gap':maximplicit,'minimum_sampled_DA':minDA}
  print('CE1AR_SCIENCE',gl,stats[str(gl)],flush=True)
 if len(full)!=5562 or len(resp)!=1854:raise ArithmeticError('incomplete original source-owned atlas')
 write_csv(output/'CE1AR_FIXED_Z_BEAMS.csv',FIELDS,full)
 write_csv(output/'CE1AR_FIXED_Z_RESPONSE.csv',RESP,resp)
 report={'schema':'bass.ce1ar.fixed_observed_redshift_sachs.v1',
 'source_SHA256':SOURCE_SHA,'original_parent_CE1AP_PR':301,'original_parent_CE1AP_HEAD':PARENT_CE1AP,
 'parent_PR':302,'immutable_parent_HEAD':PARENT_CE1AQ,
 'original_model':'massless collisionless reflection-even six-cell diagonal Bianchi I Einstein Vlasov',
 'source_provenance':provenance,'signature':'(-,+,+,+)','Einstein_normalization':'8piG=1 dimensionless',
 'observer_u':OBS_U,'redshift_shells':list(SHELLS),'sky_directions':len(sky),
 'new_Einstein_IVPs':0,'reused_original_Einstein_IVPs':9,
 'new_original_physical_beam_rows':len(full),'new_physical_source_response_rows':len(resp),
 'new_fixed_z_observable_records':len(full)+len(resp),
 'isotropic_comparator':'same-volume kinematic proxy, NOT separately solved FLRW Einstein Vlasov',
 'input_oracle':'independent original CE1AQ fixed-u Jacobi/Saunders and CE1AP metric; no new owner',
 'polarized_Thomson':False,'matched_REI_IGM_source':False,'Planck_or_measured_sky_likelihood':False,
 'OB1_full_accepted':False,'CE1':'PARTIAL','KM2':'PARTIAL','upper_BASS':'9/15 scoped source-mapped',
 'new_upper_completed':0,'production_ready':False,'merge_ready':False,'auto_next':False,
 'quadrature_samples':panels,'GL':stats}
 (output/'CE1AR_RESULTS.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
 return report


def cli():
 p=argparse.ArgumentParser()
 p.add_argument('--input',type=Path,required=True)
 p.add_argument('--metadata',type=Path,required=True)
 p.add_argument('--out',type=Path,required=True)
 p.add_argument('--strict-sha',action='store_true')
 p.add_argument('--panels',type=int,default=257)
 a=p.parse_args()
 execute(a.input,a.metadata,a.out,strict_sha=a.strict_sha,panels=a.panels)

if __name__=='__main__':cli()
