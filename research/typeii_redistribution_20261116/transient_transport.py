"""Evolving finite-band dilute tagged photons in original TypeII phase space.
Factorized angular-averaged frequency diffusion + elastic dipole redistribution.
Local source and backgrounds remain prescribed. No global escape/CMB claim.
"""
import csv,json,time
from pathlib import Path
import numpy as np
from scipy.special import wofz
from redistribution import *
from source_geometry import source,Angles

def resonance_rates(nu,T,nl):
 dn=NU0*np.sqrt(2*KB*T/(MH*C*C));a=ALYA/(4*np.pi*dn)
 profile=np.real(wofz((np.asarray(nu)-NU0)/dn+1j*a))/(np.sqrt(np.pi)*dn)
 # Declared narrow-line resonance event rate; true ionization is separately pd.
 return 3*ALYA*C**3*nl/(8*np.pi*NU0**2)*profile

def simulate(label,z0=1100.,width=20.,cells=80,nmu=4,nphi=8,steps=160,duration=.003,frozen_matter=False,recoil=True,frequency=True,angular=True,destruction=True):
 if not 320<=z0<=1700 or not 8<=width<=100 or cells<16 or steps<16 or not 0<duration<=.02:raise ValueError('bounded source packet/grid domain')
 src=source();t0=float(np.log(1701/(1+z0)));t1=t0+duration
 if t1>src.end:raise ValueError('end outside parent input')
 geom=Angles(t0,t1,nmu,nphi);mat0=src.matter(t0)
 eps=np.sqrt(2*KB*mat0['T']/(MH*C*C));dn=NU0*eps
 check(width*eps<.05,'source finite band outside narrow-line support')
 edges=NU0+dn*np.linspace(-width,width,cells+1);nu=(edges[:-1]+edges[1:])/2
 x=(nu-NU0)/dn;g0=geom.at(t0);M0=capacities(edges,g0['wn'],g0['D'],g0['V'])
 # Smooth injected spectrum (sigma=3 initial Doppler widths), atom-isotropic f.
 N=M0*np.exp(-.5*(x/3)**2)[None,:];N/=N.sum()
 initial_occ=float((N/M0).max());check(initial_occ<1e-8,'tagged occupation not dilute')
 epoch=np.r_[0.,np.geomspace(1e-13,duration,steps)]+t0
 tally={'red_drift':0.,'red_diffusion':0.,'blue_diffusion':0.,'blue_drift':0.,'ionized':0.,'escape_energy_J':0.,'ionized_energy_J':0.,'frequency_exchange_normal_J':0.,'angular_exchange_normal_J':0.,'geometry_work_J':0.,'angular_roundoff_clipped_mass':0.}
 E=lambda y,g:float(np.sum(y*(H*nu[None,:]/g['D'][:,None])))
 Ein=E(N,g0);tr=[];maxnum=maxenergy=maxstep=maxsky=0.;maxocc=initial_occ;residence=0.
 def geo_update(y,a,b):
  if a==b:return y
  ga,gb,gm=geom.at(a),geom.at(b),geom.at((a+b)/2)
  scale=np.exp(gb['logEn']-ga['logEn'])*gb['D']/ga['D']
  out,red,blue=remap_details(y,edges,scale)
  lossE=float(np.dot(red,H*edges[0]/gm['D'])+np.dot(blue,H*edges[-1]/gm['D']))
  tally['red_drift']+=float(sum(red));tally['blue_drift']+=float(sum(blue));tally['escape_energy_J']+=lossE
  tally['geometry_work_J']+=E(out,gb)+lossE-E(y,ga)
  return out
 for k,(a,b) in enumerate(zip(epoch[:-1],epoch[1:])):
  dt=b-a;mid=(a+b)/2;before=float(N.sum());N=geo_update(N,a,mid);gm=geom.at(mid)
  matter=mat0 if frozen_matter else src.matter(mid)
  rate=resonance_rates(nu,matter['T'],matter['nl']);rates_e=resonance_rates(edges,matter['T'],matter['nl'])
  pd=matter['pd'] if destruction else 0.
  Q,pi=angular_generator(gm['na'],gm['wa'],gm['D'])
  if angular:
   eprev=E(N,gm);N,audit=angular_evolve(Q,pi,N,.5*dt*(1-pd)*rate/gm['Hn'],True)
   tally['angular_exchange_normal_J']+=eprev-E(N,gm);tally['angular_roundoff_clipped_mass']+=audit['roundoff_clipped_mass']
  fm=frequency_model(edges,matter['T'],rate,rates_e,pd,1.,absorbing=True,recoil=recoil)
  if not frequency:
   fm['up']*=0;fm['down']*=0;fm['red']=0.;fm['blue']=0.;fm['loss']=fm['kill'].copy()
  for j in range(len(N)):
   out=frequency_step(fm,N[j],dt*gm['D'][j]/gm['Hn']);N[j]=out['N']
   tally['red_diffusion']+=out['red'];tally['blue_diffusion']+=out['blue'];tally['ionized']+=out['death']
   tally['escape_energy_J']+=(H*edges[0]*out['red']+H*edges[-1]*out['blue'])/gm['D'][j]
   tally['ionized_energy_J']+=out['death_energy_J']/gm['D'][j]
   tally['frequency_exchange_normal_J']+=out['heat_J']/gm['D'][j]
   maxstep=max(maxstep,abs(out['number_residual']));maxenergy=max(maxenergy,abs(out['energy_residual_J'])/Ein)
  if angular:
   eprev=E(N,gm);N,audit=angular_evolve(Q,pi,N,.5*dt*(1-pd)*rate/gm['Hn'],True)
   tally['angular_exchange_normal_J']+=eprev-E(N,gm);tally['angular_roundoff_clipped_mass']+=audit['roundoff_clipped_mass']
  N=geo_update(N,mid,b);gb=geom.at(b);alive=float(N.sum())
  outs=tally['red_drift']+tally['blue_drift']+tally['red_diffusion']+tally['blue_diffusion']
  defect=alive+outs+tally['ionized']-1;maxnum=max(maxnum,abs(defect))
  M=capacities(edges,gb['wn'],gb['D'],gb['V']);maxocc=max(maxocc,float((N/M).max()))
  maxsky=max(maxsky,abs(sum(gb['wn'])/(4*np.pi)-1),abs(sum(gb['wa'])/(4*np.pi)-1))
  residence+=.5*(before+alive)*dt
  energydef=E(N,gb)+tally['escape_energy_J']+tally['ionized_energy_J']+tally['frequency_exchange_normal_J']+tally['angular_exchange_normal_J']-tally['geometry_work_J']-Ein
  maxenergy=max(maxenergy,abs(energydef)/Ein)
  tr.append([b-t0,1701*np.exp(-b)-1,alive,tally['red_drift'],tally['red_diffusion'],tally['blue_diffusion'],tally['ionized'],defect,energydef/Ein])
 check(N.min()>=0 and maxnum<2e-8 and maxenergy<5e-8,'tagged packet count/energy audit')
 check(maxocc<1e-8,'tagged packet leaves admitted dilute limit')
 material_end=src.matter(t1)
 result={'label':label,'z_initial':z0,'z_final':1701*np.exp(-t1)-1,'halfwidth_initial_Doppler':width,'frequency_cells':cells,'angular_directions':nmu*nphi,'time_steps':steps,'duration_tauH':duration,'frozen_matter':frozen_matter,'recoil':recoil,'frequency_diffusion':frequency,'angular_redistribution':angular,'true_ionization':destruction,'surviving':float(N.sum()),**tally,'max_number_budget_abs_gap':maxnum,'max_normal_radiation_energy_ledger_relative_gap':maxenergy,'max_frequency_step_number_gap':maxstep,'max_occupation_one_initial_photon_per_m3':maxocc,'max_sky_area_quadrature_gap':maxsky,'mean_censored_residence_tauH':residence,'matter_initial':mat0,'matter_final_actual':material_end,'physical_scope':'finite absorbing band, prescribed population/thermal histories, factorized leading FP+dipole closure; exits are not global escape'}
 output=HERE/'outputs';output.mkdir(exist_ok=True)
 with (output/(label+'.csv')).open('w',newline='') as f:
  w=csv.writer(f,lineterminator='\n');w.writerow(['elapsed_tauH','z_mean','surviving','red_stream','red_diffusion','blue_diffusion','ionized','number_residual','normal_energy_relative_residual']);w.writerows(tr)
 np.save(output/(label+'_final_N.npy'),N,allow_pickle=False)
 (output/(label+'.json')).write_text(json.dumps(result,indent=2)+'\n')
 return result

if __name__=='__main__':
 r=simulate('pilot',cells=80,nmu=3,nphi=4,steps=100)
 print(json.dumps(r,indent=2))
