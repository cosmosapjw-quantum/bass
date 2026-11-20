#!/usr/bin/env python3
"""Time-dependent tagged photons: correlated finite scattering + outer-band reentry.

The exact Type-II source normal phase-space flow and field inputs are owned by
PR341. This local experiment uses the coherent Maxwell/Lorentz (Hummer-like)
finite angle-frequency kernel, explicitly thermally symmetrized, not exact RII.
Photon counts are on the normal slice; no full cosmic atom/radiation feedback.
"""
import csv,json,math
from pathlib import Path
import numpy as np
from scipy.sparse import csc_matrix,eye
from scipy.sparse.linalg import spsolve
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"typeii_correlated_outer_20261119"))
from correlated import *
from rii_transport import matrix_kernel,scattering_tails

HERE=Path(__file__).resolve().parent
def source_geometry(z0,duration,ang=6):
 if not 300<z0<=1700 or not np.isfinite(duration) or duration<=0:raise ValueError('valid mean-redshift start and duration')
 t0=np.log(1701/(1+z0))
 bg=prev.background()
 if not t0+duration<bg['end']:raise ValueError('source time outside original Hubble background')
 if ang==6:na,wa=sphere6()
 elif ang==14:na,wa=sphere14()
 else:raise ValueError('unsupported source angular grid')
 b=float(bg['sol'](t0)[4])
 nn,D=prev.to_normal(na,b)
 geom=prev.Geometry(t0,t0+duration,normal_initial=nn,weights=wa*D**2)
 return geom,t0

def prior_scattering_tails(g):
 """Raw coherent-atom scattering to x outside the *outer* simulated band.

 Conditional finite-bands are not normalized to1: the omitted tails are
 genuine terminal outgoing channels, unlike the internal ±20 core crossing.
 """
 x=g['x'];edges=g['edges'];na=g['na'];wa=g['wa'];T=g['T']
 dn=NU0*np.sqrt(2*KB*T/(MH*C*C));a=A/(4*np.pi*dn)
 recoil=H*NU0/(MH*C*C*np.sqrt(2*KB*T/(MH*C*C)))
 M=len(x);N=len(wa)
 red=np.zeros((N,M));blue=np.zeros((N,M));maxnorm=0
 for aj in range(N):
  for ai in range(N):
   mu=float(np.round(na[ai]@na[aj],12))
   ang=wa[ai]*.75*(1+mu**2)
   for k,xin in enumerate(x):
    b=conditional_bins(float(xin),mu,float(a),
       np.array([-1.e5,edges[0],edges[-1],1.e5]),recoil=float(recoil))
    red[aj,k]+=ang*b[0]
    blue[aj,k]+=ang*b[-1]
 for j in range(N):
  for k in range(M):
   if red[j,k]<-1e-10 or blue[j,k]<-1e-10 or red[j,k]+blue[j,k]>1+1e-7:raise RuntimeError('unphysical scattered outer losses')
 return red.reshape(-1),blue.reshape(-1)

def evolve(z0=1100.,X=40.,duration=.00015,steps=64,
           factorized=False,frozen=False,angular_order=6,save=None,thermo_sym=True,
           include_outer_scattering=True):
 if not isinstance(steps,int) or steps<8 or X not in (20.,40.,80.,120.,160.,240.,320.,480.):
  raise ValueError('finite source intervals, integer time grid and bounded outer support')
 geom,t0=source_geometry(z0,duration,ang=angular_order)
 s0=geom.at(t0)
 g=matrix_kernel(z=z0,X=X,T=s0['Tm'],nl=s0['nl'],
                 angle_order=angular_order,factorized=factorized,thermo_sym=thermo_sym)
 nf=len(g['x']);na=len(g['wa']);N=na*nf
 x=g['x'];nu=NU0+NU0*np.sqrt(2*KB*s0['Tm']/(MH*C*C))*x
 edges_nu=NU0+NU0*np.sqrt(2*KB*s0['Tm']/(MH*C*C))*g['edges']
 width=np.diff(edges_nu)
 # Red/blue outermost probabilities from scattering, without artificial
 # normalization of the truncated coherent redistribution function.
 t_red,t_blue=scattering_tails(g)
 # Finite photonic tagged initial condition, source normal-count capacity.
 shape=np.exp(-.5*((x-3)/3)**2)
 init=(s0['capacity_angle'][:,None]*
       (width*nu**2)[None,:]*shape[None,:]).reshape(-1)
 if not np.isfinite(init).all() or min(init)<0:raise RuntimeError('invalid source tagged distribution')
 init/=sum(init)
 n=np.r_[init,np.zeros(3)]
 core=np.tile(abs(x)<=20,na)
 outsrc=~core
 I=eye(N+3,format='csc')
 tedges=np.linspace(t0,t0+duration,steps+1)
 maxcount=0.;mincount=float(min(n));gross_core_out=gross_core_return=0.
 energy_resid=0.;scat_norm=0.;red_flux_advection=0.
 source_drift=0.;frame_geom_shift=0.;maxangle=0.
 traces=[]
 for k in range(steps):
  left,right=tedges[k:k+2];mid=(left+right)/2;dt=right-left
  s=s0 if frozen else geom.at(mid)
  smL=s0 if frozen else geom.at(left)
  smR=s0 if frozen else geom.at(right)
  D=s['D'];K=s['kappa'];Hn=s['H']
  if np.min(K)<=0:raise RuntimeError('nonmonotonic source photon drift')
  # Source-dependent opacity/clock, while the *shape* of the idealized
  # joint redistribution kernel is frozen at T(z0); this is a model error.
  rate,_=prev.medium_rates(nu,s['Tm'],s['nl'],0.)
  source_scale=(rate/g['rate'])[None,:]*(D/Hn)[:,None]
  scale=(source_scale*(1-s['pion'])).reshape(-1)
  scat=g['Q']*scale[None,:]
  Q=np.zeros((N+3,N+3))
  Q[:N,:N]=scat
  # Physically absolute source absorption into ionizing tagged fates.
  kill=(source_scale*s['pion']*g['rate'][None,:]).reshape(-1)
  # Out-of-grid coherent scattering: red and blue terminal channels.
  red=(source_scale*(1-s['pion'])*g['rate'][None,:]).reshape(-1)*t_red
  blue=(source_scale*(1-s['pion'])*g['rate'][None,:]).reshape(-1)*t_blue
  Q[N,:N]=red
  Q[N+1,:N]=blue
  Q[N+2,:N]=kill
  Q[np.arange(N),np.arange(N)]-=red+blue+kill
  # Directional drift from actual BASS source kappa, including its Doppler
  # derivative, without dropping the photon-path normal clock.
  adv=np.zeros(N)
  for j in range(na):
   for q in range(nf):
    idx=j*nf+q
    # center flux of a first-order positive frequency finite volume.
    val=K[j]*edges_nu[q]/width[q]
    if val<0:raise RuntimeError('nonpositive redshift rate')
    adv[idx]=val
    Q[idx,idx]-=val
    if q>0:Q[idx-1,idx]+=val
    else:Q[N,idx]+=val
  # Interface diagnostic: crossings of ±20 Doppler widths in either
  # direction. A photon can cross more than once, so these are GROSS counts.
  src_core=n[:N][core]
  # Backward implicit positive M-matrix under genuine source stiffness.
  after=spsolve(I-csc_matrix(Q*dt),n)
  if not np.isfinite(after).all() or min(after)<-3e-10:
   raise RuntimeError('positive finite source solve failed')
  after=np.maximum(after,0)
  maxcount=max(maxcount,abs(float(sum(after)-1)))
  mincount=min(mincount,float(min(after)))
  if maxcount>3e-7:raise RuntimeError('source photon+termination ledger defect')
  gross_core_out+=dt*np.sum(Q[:N,:N][np.ix_(outsrc,core)]@after[:N][core])
  gross_core_return+=dt*np.sum(Q[:N,:N][np.ix_(core,outsrc)]@after[:N][outsrc])
  # Fixed-source normal energy ledger; collision + advection must account
  # for same finite generator. Source D variation is a separate geometric term.
  Em=(nu[None,:]/NU0/D[:,None]).reshape(-1)
  change=after[:N]-n[:N]
  modeled=dt*np.dot(Em,Q[:N,:N]@after[:N])
  energy_resid=max(energy_resid,abs(float(Em@change-modeled)))
  scat_norm+=float(dt*np.abs(scat@after[:N]).sum())
  red_flux_advection+=float(dt*np.dot(adv,np.r_[after[:N]])/max(N,1))
  frame_geom_shift+=float(np.dot((nu[None,:]/NU0/smR['D'][:,None]-nu[None,:]/NU0/smL['D'][:,None]).reshape(-1),after[:N]))
  maxangle=max(maxangle,float(s['angular_weight_defect']))
  n=after
  traces.append((right-t0,1701*np.exp(-right)-1,float(sum(n[:N])),float(n[N]),float(n[N+1]),float(n[N+2]),float(gross_core_out),float(gross_core_return),float(sum(n)-1)))
 res={'HUMMER_RII0_SOURCE_KERNEL':True,'thermal_pair_symmetrization':thermo_sym,
 'model':'finite-band correlated Maxwell-Lorentz dipole kernel, leading recoil, pairwise Wien symmetrization',
 'initial_z_mean':float(z0),'final_z_mean':float(1701*np.exp(-(t0+duration))-1),
 'duration_tauH':float(duration),'steps':steps,'outer_half_width_Doppler':X,
 'inner_half_width_Doppler':20.,'factorized_control':factorized,
 'frozen_source':frozen,'angle_count':na,'frequency_bins':nf,
 'survival':float(sum(n[:N])),'red_outer_exit':float(n[N]),'blue_outer_exit':float(n[N+1]),
 'tagged_ionized':float(n[N+2]),
 'gross_inner_to_outer_crossings':float(gross_core_out),
 'gross_outer_to_inner_reentries':float(gross_core_return),
 'max_number_ledger_defect':maxcount,'min_cell_count':mincount,
 'max_frozen_midpoint_energy_generator_ledger_defect':float(energy_resid),
 'integrated_absolute_scattering_redistribution':float(scat_norm),
 'geometric_D_frame_change_per_initial_line_energy':float(frame_geom_shift),
 'angular_source_measure_defect':maxangle,
 'joint_kernel_L1_vs_factorized':float(g['factorization_gap']),
 'kernel_natural_width_a':g['kernel_meta']['a'],
 'kernel_recoil_eta':g['kernel_meta']['recoil'],
 'boundary':'physical outer support terminal; inner ±20 interface crossings and returns recorded; terminal probabilities not global escape',
 'source':'original five-state BASS TypeII normal geometry; fixed parent nHrest/Tm/pion, no photon feedback',
 'approximations':'coherent Maxwell/Lorentz joint kernel with pairwise thermal symmetrization, frozen shape at start; time-dependent source opacity, D/H and frequency drift; no exact RII or polarization'
 }
 if save:
  (HERE/(save+'_RESULT.json')).write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
  with (HERE/(save+'_TRACE.csv')).open('w',newline='') as f:
   wr=csv.writer(f,lineterminator='\n')
   wr.writerow(['delta_tauH','z_mean','survival','red_outer_exit','blue_outer_exit','tagged_ionized','gross_core_out','gross_core_return','number_ledger'])
   wr.writerows(traces)
 return res

def campaign():
 cases=[
 ('core_20',dict(X=20.,steps=64)),
 ('outer_40',dict(X=40.,steps=64)),
 ('outer_80',dict(X=80.,steps=64)),
 ('outer_40_factorized',dict(X=40.,steps=64,factorized=True)),
 ('outer_40_frozen',dict(X=40.,steps=64,frozen=True)),
 ('outer_40_time128',dict(X=40.,steps=128)),
 ]
 results=[]
 for name,kwargs in cases:
  p=evolve(**kwargs,save='OUTER_'+name);p['case']=name;results.append(p)
  (HERE/'OUTER_MATCHING_RESULTS.json').write_text(json.dumps({'cases':results,'status':'source conditional finite joint kernel experiment, not global escape'},indent=2)+'\n')
  print('OUTER_CASE',name,json.dumps({k:p[k] for k in ('survival','red_outer_exit','blue_outer_exit','tagged_ionized','gross_inner_to_outer_crossings','gross_outer_to_inner_reentries','max_number_ledger_defect')}),flush=True)
if __name__=='__main__':campaign()
