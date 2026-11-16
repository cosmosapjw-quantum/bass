#!/usr/bin/env python3
"""Time-dependent finite-band tagged-photon source experiments.
Counts live on the normal hypersurface with moving angular characteristics.
Factorized FP-frequency plus elastic Rayleigh angular redistribution is an
explicit approximation, not a complete correlated R_II transport kernel.
"""
import json,csv,time
from pathlib import Path
import numpy as np
from redistribution import *

def evolve(z0=1100.,X=20.,cells=160,steps=192,nmu=4,nphi=8,duration=.01,frozen=False,frequency=True,angular=True,destruction=True,save=None):
 if not np.isfinite([z0,X,duration]).all() or not 300<z0<=1700 or duration<=0 or not isinstance(steps,int) or steps<4:raise ValueError('invalid source evolution specification')
 t0=np.log(1701/(1+z0));geom=Geometry(t0,t0+duration,nmu,nphi);s0=geom.at(t0);grid=fixed_grid(s0['Tm'],X,cells)
 nu=grid['nu'];nedges=grid['nu_edges'];x=grid['x'];width=grid['width'];m=len(nu);na=geom.nang
 # Initial isotropic atom-frame occupation shape, evaluated on the normal slice.
 # A tagged Gaussian of width3 Doppler units, centered at+3, is not a full line-emission law.
 initial_shape=np.exp(-.5*((x-3.)/3.)**2)
 N=s0['capacity_angle'][:,None]*grid['cap'][None,:]*initial_shape[None,:];N/=N.sum()
 Ninitial=N.copy();E0n=nu[None,:]/NU0/s0['D'][:,None];Einit=float(np.sum(E0n*N))
 total_red=total_blue=total_kill=0.;Eout=Ekill=geo_work=angular_work=freq_work=rest_heat=0.
 times=t0+np.r_[0.,np.geomspace(1e-10,duration,steps)];trace=[];maxcount=maxenergy=maxframe=maxangle=0.;minN=1.
 for ii,(left,right) in enumerate(zip(times[:-1],times[1:])):
  dt=right-left;mid=(left+right)/2
  sm=s0 if frozen else geom.at(mid);sl=s0 if frozen else geom.at(left);sr=s0 if frozen else geom.at(right)
  D=sm['D'];hn=sm['H'];K=sm['kappa'];Tm=sm['Tm'];nl=sm['nl'];pd=sm['pion'];check(min(K)>0,'nonmonotonic source outside current upwind scope')
  En=nu[None,:]/NU0/D[:,None];Enl=nu[None,:]/NU0/sl['D'][:,None];Enr=nu[None,:]/NU0/sr['D'][:,None]
  geo_work+=float(np.sum((En-Enl)*N));maxangle=max(maxangle,sm['angular_weight_defect'])
  rs,killrest=medium_rates(nu,Tm,nl,pd)
  if angular:
   Q,pi=angular_generator(sm['na'],sm['we'],D)
   before=N.copy();N=angular_step(N,Q,pi,.5*dt*rs/hn);change=N-before
   ew=float(np.sum(En*change));py=float(np.sum(En*sm['n'][:,1,None]*change));rest=float(np.sum(nu[None,:]/NU0*change));G=1/np.sqrt(1-sm['state'][4]**2)
   maxframe=max(maxframe,abs(G*(ew-sm['state'][4]*py)-rest));angular_work+=ew
  if frequency:up0,down0=frequency_rates(grid,Tm,nl,pd,True)
  else:up0,down0=np.zeros(m),np.zeros(m)
  factor=D[:,None]/hn
  up=factor*up0[None,:];downfp=factor*down0[None,:]
  downadv=K[:,None]*nedges[:-1][None,:]/width[None,:]
  down=downfp+downadv;kill=factor*killrest[None,:] if destruction else np.zeros_like(up)
  after=backward_birth_death(N,up,down,kill,dt)
  # All losses are integrated with the same implicit state as the finite-volume update.
  red=dt*down[:,0]*after[:,0];blue=dt*up[:,-1]*after[:,-1];lost=dt*kill*after
  total_red+=float(sum(red));total_blue+=float(sum(blue));total_kill+=float(np.sum(lost))
  Eout+=float(np.sum(red*nedges[0]/NU0/D+blue*nedges[-1]/NU0/D));Ekill+=float(np.sum(En*lost))
  # Independent flux energy ledger, including detuning at the finite boundaries.
  Jfp=dt*(np.asarray(up[:,:-1],np.longdouble)*after[:,:-1]-np.asarray(downfp[:,1:],np.longdouble)*after[:,1:])
  dnu=np.diff(nu)/NU0
  delta_atom=float(np.sum(Jfp*dnu[None,:]));delta_normal=float(np.sum(Jfp*dnu[None,:]/D[:,None]))
  rfp=dt*downfp[:,0]*after[:,0];bfp=dt*up[:,-1]*after[:,-1]
  delta_atom+=float(np.sum(rfp*(nedges[0]-nu[0])/NU0+bfp*(nedges[-1]-nu[-1])/NU0))
  delta_normal+=float(np.sum((rfp*(nedges[0]-nu[0])+bfp*(nedges[-1]-nu[-1]))/NU0/D))
  freq_work+=delta_normal;rest_heat-=delta_atom
  adv_internal=float(np.sum(dt*downadv[:,1:]*after[:,1:]*(nu[:-1]-nu[1:])[None,:]/NU0/D[:,None]))
  adv_boundary=float(np.sum(dt*downadv[:,0]*after[:,0]*(nedges[0]-nu[0])/NU0/D))
  geo_work+=adv_internal+adv_boundary
  N=after
  if angular:
   before=N.copy();N=angular_step(N,Q,pi,.5*dt*rs/hn);change=N-before
   ew=float(np.sum(En*change));py=float(np.sum(En*sm['n'][:,1,None]*change));rest=float(np.sum(nu[None,:]/NU0*change));G=1/np.sqrt(1-sm['state'][4]**2)
   maxframe=max(maxframe,abs(G*(ew-sm['state'][4]*py)-rest));angular_work+=ew
  geo_work+=float(np.sum((Enr-En)*N));minN=min(minN,float(N.min()))
  count=float(N.sum()+total_red+total_blue+total_kill-1)
  energy=float(np.sum(Enr*N)+Eout+Ekill-Einit-geo_work-angular_work-freq_work)
  maxcount=max(maxcount,abs(count));maxenergy=max(maxenergy,abs(energy))
  trace.append([right-t0,1701*np.exp(-right)-1,float(N.sum()),total_red,total_blue,total_kill,float(np.sum(x[None,:]*N)),rest_heat,geo_work,angular_work,freq_work,count,energy])
 check(maxcount<3e-9 and minN>-1e-13,'tagged photon count/positivity failure')
 check(maxenergy<2e-8 and maxframe<1e-12,'independent energy or four-force ledger')
 result={'z_initial':float(z0),'z_final':float(1701*np.exp(-(t0+duration))-1),'duration_tauH':float(duration),'band_halfwidth_initial_Doppler':float(X),'frequency_cells':cells,'time_steps':steps,'angular_nodes':na,'angular_orders':[nmu,nphi],
 'time_varying_source':not frozen,'frequency_redistribution':frequency,'angular_redistribution':angular,'tagged_ionization':destruction,
 'survival':float(N.sum()),'red_band_exit':total_red,'blue_band_exit':total_blue,'tagged_ionized':total_kill,
 'max_count_ledger_defect':maxcount,'max_normal_energy_ledger_defect_in_initial_line_energy':maxenergy,'max_collision_fourforce_defect':maxframe,'min_cell_count':minN,
 'max_atom_angular_quadrature_defect':maxangle,'atom_rest_frequency_heat_per_initial_line_energy':rest_heat,'normal_angular_bulk_photon_energy_change':angular_work,'normal_frequency_photon_energy_change':freq_work,'normal_geometric_work':geo_work,
 'initial_atom_temperature_K':s0['Tm'],'initial_neutral_lower_m3':s0['nl'],'initial_tagged_pion':s0['pion'],
 'initial_condition':'unit-normalized tagged Gaussian atom-frame occupation, center+3,width3 Doppler; isotropic rest occupation represented on normal slice',
 'boundary':'absorbing frequency-diffusion exits and red advection outflow; no photon inflow; finite exits not global escape',
 'collision_scope':'dilute leading FP frequency + elastic Rayleigh angle factorization; no full joint redistribution, atom/thermal feedback or polarization'}
 if save:
  with (HERE/(save+'_TRACE.csv')).open('w',newline='') as f:
   w=csv.writer(f,lineterminator='\n');w.writerow(['delta_tauH','z_mean','survival','red_band_exit','blue_band_exit','tagged_ionized','unnormalized_mean_Doppler_x','atom_rest_frequency_heat_E0','geometric_work_E0','angular_bulk_change_E0','frequency_change_normal_E0','count_residual','energy_residual_E0']);w.writerows(trace)
  np.save(HERE/(save+'_FINAL_COUNTS.npy'),N)
  (HERE/(save+'_RESULT.json')).write_text(json.dumps(result,indent=2)+'\n')
 return result

def campaign():
 cases=[('base',dict()),('time_half_resolution',dict(steps=96)),('time_double_resolution',dict(steps=384)),('frequency_double',dict(cells=320,steps=384)),('angular_refined',dict(nmu=6,nphi=12,cells=320,steps=384)),('band40',dict(X=40,cells=640,steps=384)),('frozen',dict(cells=320,steps=384,frozen=True)),('no_frequency',dict(cells=320,steps=384,frequency=False)),('no_redistribution',dict(cells=320,steps=384,frequency=False,angular=False)),('no_destruction',dict(cells=320,steps=384,destruction=False))]
 results=[]
 for name,kw in cases:
  r=evolve(**kw,save='PACKET_'+name);r['case']=name;results.append(r)
  (HERE/'SOURCE_PACKET_RESULTS.json').write_text(json.dumps({'parent':PARENT,'cases':results,'source_scope':'prescribed parent TypeII background and fixed-ne tracer/fate histories; no new xe/tau prediction'},indent=2)+'\n')
  print('PACKET',name,json.dumps({k:r[k] for k in ('survival','red_band_exit','blue_band_exit','tagged_ionized','max_count_ledger_defect','max_normal_energy_ledger_defect_in_initial_line_energy')}),flush=True)
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--base-only',action='store_true');a=p.parse_args()
 if a.base_only:print(json.dumps(evolve(save='PACKET_base'),indent=2))
 else:campaign()
