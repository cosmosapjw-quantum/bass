#!/usr/bin/env python3
"""CE1AI: five-direction source-cell mass-transfer response of original Einstein--Vlasov Bianchi I.

All source families are explicitly separate conditional initial data. Original six-cell
source is immutable and is never silently replaced. Normal-frame bolometric angular
power is *not* CMB temperature/polarization or an observational likelihood.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math, sys
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp, cumulative_simpson

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
RESEARCH=ROOT.parent
sys.path.insert(0,str(RESEARCH/'ce1af_20261030'/'input'))
sys.path.insert(0,str(RESEARCH/'ce1ah_20261031'/'source'))
from cellwise_gl_rust import make_cell_rays, frozen_source_identity, MU, PHI, CELL_E, SHEAR
import ce1ah_tangent as ancestor

ORIGINAL_SOURCE_SHA='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
IMMUTABLE_PARENT_HEAD='c7660436f233bfe94d954146017059fd79385dd5'
PARENT_PR=287
U=0.08
# Exact reference cell: equatorial (mu <1/2), middle azimuth cell.
REFERENCE=(0,1)
TARGETS={'EQ_X':(0,0),'EQ_Y':(0,2),'POL_X':(1,0),'POL_MID':(1,1),'POL_Y':(1,2)}
BASE_NAMES=tuple(TARGETS)
NAMES=BASE_NAMES+('DARK_L2L4',)
MASS_DIRECTIONS=np.zeros((len(NAMES),2,3),dtype=float)
for idx,name in enumerate(BASE_NAMES):
  MASS_DIRECTIONS[idx,REFERENCE[0],REFERENCE[1]]=-1.
  r,c=TARGETS[name];MASS_DIRECTIONS[idx,r,c]=1.
# Exact integer continuum null for energy and real l=2,4 initial harmonics.
# <(1-mu^2)^2> = 203/240 for equatorial mu cell, 53/240 for polar cell.
DARK_INTEGER=np.array([[53,-106,53],[-203,406,-203]],dtype=int)
MASS_DIRECTIONS[-1,:,:]=DARK_INTEGER/406.

BASE_FIELDS=['GL','u','E','H','W','q','C2','C4','F','constraint']
TAN_FIELDS=['GL','u','mode','dell1','dell2','dell3','dh1','dh2','dh3',
            'dE','dP1','dP2','dP3','dH','dW','dq','dC2','dC4',
            'dalpha20','dalpha22','dalpha40','dalpha42','dalpha44','dF','dconstraint','dlogbalance']
FD_FIELDS=['GL','u','mode','eps','sign','E','W','q','C2','C4','constraint']
SPEC_FIELDS=['GL','u','s1','s2','s3','s4','s5','condition_number','max_constraint_tangent']


def validate_immutable():
  got=frozen_source_identity()
  if got!=ORIGINAL_SOURCE_SHA:raise RuntimeError('Original six-cell SHA256 drift')
  if np.any(CELL_E<=0) or MASS_DIRECTIONS.shape!=(6,2,3):raise RuntimeError('Invalid source')
  if not np.all(MASS_DIRECTIONS.sum(axis=(1,2))==0):raise RuntimeError('Source-mass directions must preserve total E0')
  if np.linalg.matrix_rank(MASS_DIRECTIONS[:5].reshape(5,6))!=5:raise RuntimeError('Five base source-mass modes not independent')
  if not np.array_equal(DARK_INTEGER.sum(axis=1),[0,0]):raise RuntimeError('Dark source row sums')
  return got


def ray_source_basis(gl,base_mass):
  # Direct derivative of exactly the original six-cell positive GL angular measure,
  # not its replacement or a synthetic wave function.
  origins=np.repeat(np.arange(6),gl*gl)
  epercell=np.asarray(CELL_E,dtype=float).ravel()[origins]
  if len(origins)!=len(base_mass):raise RuntimeError('Original cell ray indexing drift')
  dm=MASS_DIRECTIONS.reshape(len(NAMES),6)[:,origins]*(base_mass[None,:]/epercell[None,:])
  if max(abs(float(x)) for x in dm.sum(axis=1))>3e-13:
    raise RuntimeError('GL direction source total E not preserved')
  return dm


def positive_reweighted_mass(gl,base_mass,mode,eps):
  validate_immutable()
  if mode not in NAMES:raise KeyError(mode)
  if not math.isfinite(eps) or abs(eps)>=0.04:raise ValueError('Finite source mass shift must be <0.04')
  i=NAMES.index(mode)
  new=base_mass+eps*ray_source_basis(gl,base_mass)[i]
  if not np.all(new>0):raise ValueError('Negative source angular mass')
  return new


def source_integrals(ray2,delta_mass,ell,x=None,rad=None):
  # Return V integrals against one or all source directions. Exact source derivative
  # in each cell amplitude, evaluated with the original positive angular measure.
  q=ray2*np.exp(-2*np.asarray(ell)[None,:])
  if rad is None:rad=np.sqrt(q.sum(axis=1))
  if x is None:x=q/(rad[:,None]**2)
  domega=delta_mass*(rad*np.exp(-sum(ell)))[None,:]
  de=np.sum(domega,axis=1)
  dp=domega@x
  return de,dp,domega


def real_even_harmonics(x):
  xx,yy,zz=x.T
  d=xx-yy
  c20=math.sqrt(5/(16*math.pi));c22=math.sqrt(15/(32*math.pi))
  c40=3/(16*math.sqrt(math.pi));c42=3/8*math.sqrt(5/(2*math.pi));c44=3/16*math.sqrt(35/(2*math.pi))
  return np.array([c20*(3*zz-1),c22*d,c40*(35*zz*zz-30*zz+3),
       c42*(7*zz-1)*d,c44*(xx*xx-6*xx*yy+yy*yy)])


def initial_condition(ray2,mass):
  if np.any(mass<=0):raise ValueError('Physical source must be positive')
  E,_,_,_,_=ancestor.moment(ray2,mass,np.zeros(3))
  H=math.sqrt((E+0.5*float(SHEAR@SHEAR))/3)
  return np.r_[np.zeros(3),H+SHEAR]


def tangent_initial(ray2,mass,delta_mass):
  y=initial_condition(ray2,mass)
  de0,_,_=source_integrals(ray2,delta_mass,np.zeros(3))
  dH0=de0/(6*np.mean(y[3:]))
  # Exact first variation of 3H^2=E+1/2|sigma|^2, with d sigma=0.
  out=np.zeros((len(delta_mass),6))
  out[:,3:]=dH0[:,None]
  return out


def rhs_base(ray2,mass,y):
  _,P,*_=ancestor.moment(ray2,mass,y[:3])
  h=y[3:];return np.r_[h,-sum(h)*h+P]


def rhs_joint(ray2,mass,dm,z):
  y=z[:6];ell=y[:3];h=y[3:];th=float(sum(h))
  E,P,R,x,omega=ancestor.moment(ray2,mass,ell)
  jp=ancestor.pressure_jacobian(P,R)
  de_src,dp_src,_=source_integrals(ray2,dm,ell,x=x)
  tans=z[6:].reshape(len(dm),6)
  dl=tans[:,:3];dh=tans[:,3:]
  ddp=dl@jp.T+dp_src
  ddh=-th*dh-(dh.sum(axis=1)[:,None]*h[None,:])+ddp
  return np.r_[h,-th*h+P,np.c_[dh,ddh].ravel()]


def nonlinear_observables(ray2,mass,y):
  # For FD calculations, compute only observable values (not the expensive Jacobian).
  E,P,x,omega=ancestor.moment(ray2,mass,y[:3],with_r=False)
  f=real_even_harmonics(x)
  alpha=(4*math.pi/E)*(f@omega)
  C2=(alpha[0]**2+2*alpha[1]**2)/5
  C4=(alpha[2]**2+2*alpha[3]**2+2*alpha[4]**2)/9
  h=y[3:];H=float(np.mean(h));sig=h-H
  W=float(sig@(P-E/3));q=W/E
  constraint=float(h[0]*h[1]+h[0]*h[2]+h[1]*h[2]-E)
  return [E,W,q,C2,C4,constraint]


def produce(gl=8,epochs=401,eps=1e-4,finite=True):
  validate_immutable()
  if epochs<41 or (epochs-1)%40!=0:raise ValueError('Use a 41 epoch inclusive grid multiple')
  rays,mass=make_cell_rays(gl);ray2=rays*rays
  dm=ray_source_basis(gl,mass)
  y0=initial_condition(ray2,mass)
  first=np.r_[y0,tangent_initial(ray2,mass,dm).ravel()]
  times=np.linspace(0,U,epochs)
  result=solve_ivp(lambda t,z:rhs_joint(ray2,mass,dm,z),(0,U),first,method='DOP853',
                   rtol=3e-12,atol=3e-14,t_eval=times)
  if not result.success:raise RuntimeError(result.message)
  states=result.y.T
  # Distinct fully nonlinear + and - perturbed Einstein-Vlasov IVPs, NOT linear surrogates.
  # DARK_L2L4 is a sixth (linearly dependent) direction, explicitly testing
  # whether Einstein--Vlasov transport exposes initially invisible l>=6 shape.
  finite_paths={}
  if finite:
    for k,name in enumerate(NAMES):
      for sign in (-1,1):
        mm=positive_reweighted_mass(gl,mass,name,sign*eps)
        yy=initial_condition(ray2,mm)
        sol=solve_ivp(lambda t,y:rhs_base(ray2,mm,y),(0,U),yy,
                      method='DOP853',rtol=3e-12,atol=3e-14,t_eval=times)
        if not sol.success:raise RuntimeError('Finite nonlinear IVP: '+sol.message)
        finite_paths[name,sign]=(mm,sol.y.T)
  base=[]; tangent=[];finite_rows=[];spectra=[]
  init_E=float(ancestor.moment(ray2,mass,[0.,0.,0.])[0])
  source_E0,_dp0,_=source_integrals(ray2,dm,np.zeros(3))
  all_dq={name:[] for name in NAMES}
  tangent_dconstraint=[];ranked=[]
  for t,z in zip(times,states):
    y=z[:6];ell=y[:3];h=y[3:]
    ob=ancestor.basic_observables(ray2,mass,y)
    E,P,R,x,omega=ob['E'],ob['P'],ob['R'],ob['x'],ob['omega']
    rad=np.sqrt((ray2*np.exp(-2*ell)).sum(axis=1))
    srcE,srcP,srcOmega=source_integrals(ray2,dm,ell,x=x,rad=rad)
    harm=real_even_harmonics(x)
    alpha,jac,C2,C4=ob['alpha'],ob['jac'],ob['C2'],ob['C4']
    F=E*math.exp(4*sum(ell)/3)/init_E
    base.append([gl,t,E,ob['H'],ob['W'],ob['q'],C2,C4,F,ob['C']])
    a_response=np.empty((5,5))
    gradE= -E-P
    jp=ancestor.pressure_jacobian(P,R)
    for k,name in enumerate(NAMES):
      tan=z[6+6*k:12+6*k];dl=tan[:3];dh=tan[3:]
      dE=float(gradE@dl+srcE[k])
      dP=jp@dl+srcP[k]
      dH=float(np.mean(dh));dsig=dh-dH
      dW=float(dsig@ob['Pi']+ob['sig']@(dP-dE/3))
      dq=float((dW-ob['q']*dE)/E)
      dalpha_src=4*math.pi/E*(harm@srcOmega[k])-alpha*(srcE[k]/E)
      dalpha=jac@dl+dalpha_src
      if k<5:a_response[:,k]=dalpha
      dC2=float((2*alpha[0]*dalpha[0]+4*alpha[1]*dalpha[1])/5)
      dC4=float((2*alpha[2]*dalpha[2]+4*alpha[3]*dalpha[3]+4*alpha[4]*dalpha[4])/9)
      dF=float(F*(dE/E-source_E0[k]/init_E+4*sum(dl)/3))
      dcon=float((sum(h)-h)@dh-dE)
      tangent.append([gl,t,name,*dl,*dh,dE,*dP,dH,dW,dq,dC2,dC4,*dalpha,dF,dcon,0.])
      all_dq[name].append(dq);tangent_dconstraint.append(dcon)
    svals=np.linalg.svd(a_response,compute_uv=False)
    ranked.append(svals[-1])
    spectra.append([gl,t,*svals,float(svals[0]/svals[-1]) if svals[-1]>0 else math.inf,
                    max(abs(tangent[-1-j][TAN_FIELDS.index('dconstraint')]) for j in range(len(NAMES)))])
    if finite_paths:
      for (name,sign),(mm,st) in finite_paths.items():
        # Index resolved by deterministic inclusive grid, not by cumulative integration.
        idx=int(round(t*(epochs-1)/U))
        vals=nonlinear_observables(ray2,mm,st[idx]);finite_rows.append([gl,t,name,eps,sign,*vals])
  qintegrals={name:np.r_[0.,cumulative_simpson(np.array(dq),x=times)] for name,dq in all_dq.items()}
  dlogmax=0.
  tidx={name:i for i,name in enumerate(TAN_FIELDS)}
  for row in tangent:
    i=int(round(row[1]*(epochs-1)/U));name=row[2]
    dlog=float(row[tidx['dF']]/base[i][8]+qintegrals[name][i]);row[tidx['dlogbalance']]=dlog
    dlogmax=max(dlogmax,abs(dlog))
  fderr={}
  if finite_paths:
    for name in NAMES:
      sampled=[v for v in tangent if v[2]==name]
      for obs,field in [('E','dE'),('W','dW'),('q','dq'),('C2','dC2'),('C4','dC4')]:
        col=FD_FIELDS.index(obs);ri=tidx[field]
        fp=np.array([r[col] for r in finite_rows if r[2]==name and r[4]==1])
        fm=np.array([r[col] for r in finite_rows if r[2]==name and r[4]==-1])
        truth=np.array([r[ri] for r in sampled])
        fderr[f'{name}.{obs}']=float(np.max(np.abs((fp-fm)/(2*eps)-truth)))
  origdiff=None
  if gl in (6,8) and epochs==401:
    with (RESEARCH/'ce1af_20261030'/'input'/f'GL{gl}_DOP853_coupled_41epochs.csv').open(newline='') as f:
      rows=list(csv.DictReader(f))
    old=np.array([[float(row[f'ell{k}']) for k in range(1,4)]+[float(row[f'h{k}']) for k in range(1,4)] for row in rows])
    origdiff=float(np.max(np.abs(states[::10,:6]-old)))
  sv0=spectra[0][2:7];svend=spectra[-1][2:7]
  response_end={name:{field:float([r for r in tangent if r[2]==name][-1][tidx[field]])
                  for field in ('dE','dW','dq','dC2','dC4','dF','dconstraint','dlogbalance')}
                for name in NAMES}
  report=dict(GL=gl,rays=len(mass),epochs=epochs,nfev=result.nfev,
      baseline_constraint_max=float(max(abs(v[-1]) for v in base)),
      tangent_constraint_max=float(max(abs(x) for x in tangent_dconstraint)),
      max_abs_linearized_log_work_identity=dlogmax,
      original_41sample_max_state_difference=origdiff,
      initial_dE0=source_E0.tolist(),
      final_baseline=dict(E=base[-1][2],W=base[-1][4],C2=base[-1][6],C4=base[-1][7],F=base[-1][8]),
      initial_source_harmonic_singular_values=list(map(float,sv0)),
      final_source_harmonic_singular_values=list(map(float,svend)),
      initial_source_harmonic_condition=float(spectra[0][-2]),
      final_source_harmonic_condition=float(spectra[-1][-2]),
      min_sampled_source_harmonic_singular_value=float(min(ranked)),
      endpoint_response=response_end,finite_difference_max_errors=fderr,
      finite_eps=eps,baseline_rows=len(base),tangent_rows=len(tangent),finite_rows=len(finite_rows))
  return base,tangent,finite_rows,spectra,report


def write_csv(path,fields,rows):
  with path.open('w',newline='') as f:
    w=csv.writer(f);w.writerow(fields);w.writerows(rows)


def main():
  ap=argparse.ArgumentParser()
  ap.add_argument('--orders',default='6,8,16')
  ap.add_argument('--epochs',type=int,default=401)
  ap.add_argument('--eps',type=float,default=1e-4)
  ap.add_argument('--output',default=str(ROOT/'data'))
  opt=ap.parse_args();dest=Path(opt.output);dest.mkdir(parents=True,exist_ok=True)
  accum=[[],[],[],[]];reports={}
  for gl in map(int,opt.orders.split(',')):
    sets=produce(gl,opt.epochs,opt.eps,finite=gl in (6,8))
    for allrows,rows in zip(accum,sets[:4]):allrows.extend(rows)
    reports[str(gl)]=sets[4]
    print('GL',gl,'rays',sets[4]['rays'],'base/tangent/finite/spectra',*[len(v) for v in sets[:4]],
       'constraint/tangent',sets[4]['baseline_constraint_max'],sets[4]['tangent_constraint_max'],
       'finite_difference_error',max(sets[4]['finite_difference_max_errors'].values(),default=None),flush=True)
  specs=[('CE1AI_BASELINE_PHYSICAL.csv',BASE_FIELDS,accum[0]),
         ('CE1AI_SOURCE_TANGENT_PHYSICAL.csv',TAN_FIELDS,accum[1]),
         ('CE1AI_FINITE_FAMILY_PHYSICAL.csv',FD_FIELDS,accum[2]),
         ('CE1AI_HARMONIC_RESPONSE_SINGULAR_VALUES.csv',SPEC_FIELDS,accum[3])]
  for name,fields,rows in specs:write_csv(dest/name,fields,rows)
  output={
    'schema':'bass.ce1ai.original_sixcell_constrained_source_mass_transfer.v1',
    'unit':'CE1AI_PHYSICAL_RESPONSE_TO_SOURCE_CELL_MASS_REWEIGHTING_20261031',
    'parent_pr':PARENT_PR,'immutable_parent_head':IMMUTABLE_PARENT_HEAD,
    'original_source_sha256':validate_immutable(),
    'original_baseline_immutable':True,
    'physical_family':'five-dimensional total-energy-conserving positive six-cell mass-transfer at fixed original initial shear',
    'source_reference_cell':'EQ_MID (mu in [0,1/2], azimuth fraction in [1/4,3/4])',
    'source_transfer_modes':{name:MASS_DIRECTIONS[i].tolist() for i,name in enumerate(NAMES)},
    'dark_source_exact_integer_direction':DARK_INTEGER.tolist(),
    'dark_direction_definition':'DARK_INTEGER/406, exactly null for E and initial l=2,l=4 angular coefficients of the continuous original six-cell geometry, before dynamics',
    'time_u':[0.,U], 'metric':'(-,+,+,+)', 'Lambda':0,
    'units':'original Einstein-scale dimensionless E,P and transfer eps (same units as cell energy); physical proper u=t/Tstar',
    'angular_approximation':'positive GL n^2 per source cell, not exact angular continuum quadrature enclosure',
    'finite_step':opt.eps,
    'counts':{'baseline':len(accum[0]),'linear_response':len(accum[1]),'nonlinear_family':len(accum[2]),'singular_spectrum':len(accum[3])},
    'GL':reports,
    'DAG':{'upper':'9/15','edges':21,'CE1':'PARTIAL','scoped_R_C':'18/20','new_upper_nodes':0},
    'claims':{'normal_frame_fractional_sky':True,'actual_CMB_likelihood':False,'rigorous_angular_continuum_numerical_error':False,'distinct_author_R6_C9':False},
    'production_ready':False,'merge_ready':False,'auto_next':False
  }
  (dest/'CE1AI_PHYSICAL_RESPONSE_RESULTS.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
  print('CE1AI_COUNTS',output['counts']);return output

if __name__=='__main__':main()
