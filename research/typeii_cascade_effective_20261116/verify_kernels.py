#!/usr/bin/env python3
import json,hashlib
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
import cascade as m
p=Path(__file__).resolve().parent
radial=[];line_data=[]
for u,l in m.lines():
 a=m.radial_exact(u,l);b=m.radial_numeric(u,l);err=abs(a/b-1)
 m.check(err<1e-11,'radial integral verification')
 radial.append({'upper':u,'lower':l,'analytic_a0':a,'independent_quad_a0':b,'relative_gap':err})
 line_data.append({'upper':u,'lower':l,'A_s_inv':m.einstein_A(u,l),'gap_eV':(m.bf.level(l)['chi']-m.bf.level(u)['chi'])/m.EV})
# NIST isotope values are a scale comparison; infinite-mass/rounding differences
# are not adjusted away. These reference numbers were directly retrieved from NIST.
nist=[]
for u,l,ref in [((2,1),(1,0),6.26485e8),((3,1),(1,0),1.6725e8)]:
 diff=m.einstein_A(u,l)/ref-1;m.check(abs(diff)<1e-3,'NIST line scale disagreement')
 nist.append({'upper':u,'lower':l,'NIST_s_inv':ref,'infinite_mass_model_relative_difference':diff,
              'url':'https://physics.nist.gov/PhysRefData/Handbook/Tables/hydrogentable3.htm'})
thermal=[];frame=[];table_res=[];stat=[]
mu,w=leggauss(64)
for T in (300.,3000.,8000.):
 for u,l in m.lines():
  rr=m.line_rates(u,l,T,0);expect=np.log(m.bf.level(u)['g']/m.bf.level(l)['g'])-rr['gap_J']/(m.KB*T)
  thermal.append(abs(np.log(rr['up']/rr['down'])-expect))
  beta=.05;g=1/np.sqrt(1-beta*beta);D=g*(1-beta*mu);ex=rr['gap_J']/(D*m.KB*T)
  normal=np.sum(w/2*np.exp(-ex)/(-np.expm1(-ex))/D**2)
  electron=np.exp(m.bf.log_nbar(rr['gap_J'],T,beta));frame.append(float(abs(normal/electron-1)))
 for b in (0.,.05,.2):
  a=m.two_photon(T,b,table='standard');h=m.two_photon(T,b,table='hires')
  table_res.append({'T':T,'beta':b,'standard_down':a['down'],'hires_down':h['down'],
                    'relative_down_difference':a['down']/h['down']-1,'relative_up_difference':a['up']/h['up']-1})
  if b==0:thermal.append(abs(np.log(h['up']/h['down'])+h['gap_J']/(m.KB*T)))
 net=m.network(T,T,0,1e8);s=m.stationary(net['Q'],net['reference_weights']);e=m.eliminate(net['Q'])
 q=m.stationary(e['S'],net['reference_weights'][m.RETAINED]);v=m.lift(e,q);v/=sum(v)
 stat.append({'T':T,'full_vs_Saha':float(max(abs(s/net['reference_weights']-1))),
              'reconstructed_vs_full':float(max(abs(v/s-1))),
              'exit_probability_defect':float(max(abs(e['P'].sum(axis=0)-1)))})
m.check(max(thermal)<1e-10 and max(frame)<1e-10,'E1/2gamma thermal/frame')
m.check(max(x['full_vs_Saha'] for x in stat)<1e-9 and max(x['reconstructed_vs_full'] for x in stat)<1e-9,'thermal full/reduced populations')
# Literal photon-pair azimuth quadrature, not the analytic azimuth expression.
pair=[]
mu,w=leggauss(24);phi=2*np.pi*(np.arange(48)+.5)/48
cost=mu[:,None,None]*mu[None,:,None]+np.sqrt(1-mu[:,None,None]**2)*np.sqrt(1-mu[None,:,None]**2)*np.cos(phi)[None,None,:]
W=.75*(1+cost*cost)
for E1,E2,T,b in [(.1,.2,3000,.05),(5.,5.2,4636.,.05),(.01,10.,8000.,.2)]:
 g=1/np.sqrt(1-b*b)
 def occ(e):
  ex=e*m.EV/(m.KB*T)*g*(1+b*mu);return np.exp(-ex)/(-np.expm1(-ex))
 a=occ(E1)*w/2;bb=occ(E2)*w/2
 direct=float(np.sum(W*a[:,None,None]*bb[None,:,None])/len(phi))
 moment=m.pair_average(E1*m.EV,E2*m.EV,T,b)
 err=abs(direct/moment-1);m.check(err<3e-12,'literal pair-angle quadrature')
 pair.append({'E1_eV':E1,'E2_eV':E2,'T':T,'beta':b,'relative_gap':err})
# The chemical affinity of a loop with net two photons is 2eta, not zero.
cycles=[]
for eta in (0.,.1,.5):
 a=m.cycle_affinity(3000,0,eta);m.check(abs(a-2*eta)<1e-11,'chemical cycle identity')
 cycles.append({'eta':eta,'cycle_log_affinity':a,'expected':2*eta})
out={'E1_radial_checks':radial,'E1_lines':line_data,'NIST_scale_checks':nist,
     'max_thermal_log_ratio_residual':float(max(thermal)),'max_E1_frame_relative_gap':max(frame),
     'standard_hires_two_photon_comparison':table_res,'thermal_stationary_checks':stat,
     'literal_pair_angle_checks':pair,'BE_chemical_cycles':cycles,
     'two_photon_frequency_rescale_parent_over_HYREC':m.two_photon(3000,0)['gap_J']/(10.198714553953742*m.EV),
     'normalization':'original half-spectrum sum8.2206; no factor2; parent binding gaps mapped without modifying source bytes'}
(p/'KERNEL_VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
