#!/usr/bin/env python3
import json,math
import numpy as np
from scipy.linalg import expm
from redistribution import *
from source_geometry import source,Angles,flow_fields

def main():
 s=source();fx=s.fixture;times=np.array([r['tau'] for r in fx]);actual=s.bg.sol(times)[:5].T;ref=np.array([r['state'] for r in fx]);gap=float(np.max(abs(actual-ref)));check(gap<1e-10,'original 401 state overlap')
 moment=[];measureerr=0.;wrongmeasure=[]
 for nm,np0 in [(4,8),(8,16),(16,32),(32,64),(48,96)]:
  a=Angles(0,s.end,nm,np0);end=a.at(s.end);mom=[]
  for t in np.linspace(0,s.end,31):
   x=a.at(t);invariant=x['V']*np.exp(3*x['logEn']+x['logJ']);measureerr=max(measureerr,float(max(abs(invariant-1))))
   mom.append(abs(sum(x['wn'])/(4*np.pi)-1))
  E=math.exp(3*s.end)*np.dot(end['wn'],np.exp(4*end['logEn']))/(4*np.pi)
  false=math.exp(3*s.end)*np.dot(a.w0,np.exp(3*end['logEn']))/(4*np.pi)
  moment.append({'angles':nm*np0,'max_sky_area_relative_gap':float(max(mom)),'final_comoving_photon_energy_ratio':float(E)})
  wrongmeasure.append(float(false-1))
 check(measureerr<2e-11 and moment[-1]['max_sky_area_relative_gap']<2e-8,'phase measure/sky convergence')
 # Independent surface Jacobian from four perturbed neighboring characteristics.
 n0,_=sphere_rule(3,4);bases=[];pert=[];eps=2e-5
 for n in n0[:5]:
  e=np.cross(n,[0.,0.,1.]);e/=np.linalg.norm(e);f=np.cross(n,e);bases.append((n,e,f))
  for v in (e,-e,f,-f):
   q=n+eps*v;pert.append(q/np.linalg.norm(q))
 center=Angles(0,.8,initial=n0[:5]);neighbor=Angles(0,.8,initial=np.array(pert));ng=neighbor.at(.8)['n'].reshape(5,4,3)
 numerical=np.linalg.norm(np.cross((ng[:,0]-ng[:,1])/(2*eps),(ng[:,2]-ng[:,3])/(2*eps)),axis=1)
 exact=np.exp(center.at(.8)['logJ']);jacgap=float(max(abs(numerical/exact-1)));check(jacgap<3e-8,'surface Jacobian finite difference')
 # Normal-frame energy obeys d(Vu)/dtau=-Vu -V sigma:P, independently of the measure identity.
 a=Angles(0,s.end,8,16);energygap=0.
 def energy(t):
  x=a.at(t);return x['V']*np.dot(x['wn'],np.exp(4*x['logEn']))/(4*np.pi)
 for t in (.2,.7,1.2):
  hh=1e-5;fd=(energy(t-2*hh)-8*energy(t-hh)+8*energy(t+hh)-energy(t+2*hh))/(12*hh)
  x=a.at(t);_,S=flow_fields(x['state'],x['n']);expected=-x['V']*np.dot(x['wn'],(1+S)*np.exp(4*x['logEn']))/(4*np.pi)
  energygap=max(energygap,float(abs(fd-expected)/max(abs(expected),1e-30)))
 check(energygap<2e-8,'collisionless stress-energy moment')
 # Frequency operator convergence independently against dense expm.
 e=np.linspace(NU0*.999,NU0*1.001,25);rr=np.ones(24);rf=np.ones(25)
 m=frequency_model(e,3000.,rr,rf,.02,1.,absorbing=True);Q=np.diag(-m['loss'])+np.diag(m['up'],-1)+np.diag(m['down'],1)
 p=np.exp(-((np.arange(24)-11.5)/3)**2);p/=sum(p);tex=5.;exact=expm(tex*Q)@p;errs=[];energyres=0.;numberres=0.
 for steps in (20,40,80,160):
  x=p.copy();loss=0.
  for k in range(steps):
   z=frequency_step(m,x,tex/steps);x=z['N'];loss+=z['red']+z['blue']+z['death'];energyres=max(energyres,abs(z['energy_residual_J'])/(H*NU0));numberres=max(numberres,abs(z['number_residual']))
  errs.append({'steps':steps,'max_state_gap':float(max(abs(x-exact))),'number_budget_gap':float(abs(sum(x)+loss-1))})
 check(all(errs[i+1]['max_state_gap']<errs[i]['max_state_gap'] for i in range(3)),'implicit step independent convergence')
 # Full Bose adjacent-pair free-energy decay, distinct from dilute tagged evolution.
 rng=np.random.default_rng(902);entropymax=-1e99;beerr=0.
 for i in range(80):
  fi,fj=np.exp(rng.uniform(-4,2,2));de=float(rng.uniform(.001,2));F=pair_flux(fi,fj,de)
  mu=math.log(fj/(1+fj))-math.log(fi/(1+fi))+de
  entropymax=max(entropymax,F*mu)
  x=float(rng.uniform(.1,20));eta=.3;f=1/np.expm1(x+eta);g=1/np.expm1(x+eta+de)
  beerr=max(beerr,abs(pair_flux(f,g,de))/max(f*(1+g),1e-300))
 check(entropymax<=1e-14 and beerr<2e-13,'Bose pair entropy/equilibrium')
 # Angular semigroup vs independent dense exponential and normal-energy exchange.
 n,w=sphere_rule(4,8);na,D=atom_directions(n,.05);A,pi=angular_generator(na,w/D**2,D);p=np.exp(4*n[:,0]);p/=sum(p)
 got=angular_evolve(A,pi,p[:,None],np.array([1.3]))[:,0];want=expm(1.3*A)@p;angerr=float(max(abs(got-want)));check(angerr<2e-13,'angle expm comparison')
 result={'original_401_state_gap':gap,'phase_invariant_max_abs':measureerr,'sky_quadrature':moment,'wrong_frozen_sky_weight_photon_defect':wrongmeasure,'surface_Jacobian_independent_relative_gap':jacgap,'normal_energy_stress_relative_gap':energygap,'frequency_step_expm_convergence':errs,'frequency_single_step_number_residual':numberres,'frequency_energy_relative_residual':energyres,'Bose_pair_max_equilibrium_relative_gap':beerr,'Bose_pair_free_energy_max_derivative':entropymax,'angular_semigroup_expm_abs_gap':angerr,'parent_Git_blobs':s.locks,'scope':'exact homogeneous source Liouville measure; specified factorized FP+dipole collision closure'}
 (HERE/'PHASE_AND_KERNEL_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
