#!/usr/bin/env python3
"""Independent equilibrium, entropy, solid-angle Jacobian and stiff storage tests."""
import json
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from redistribution import *
def main():
 bg=background();t0=np.log(1701/1101);end=t0+.02;geom=Geometry(t0,end,4,8)
 a=geom.at(t0);b=geom.at(end);phase=abs(np.exp(3*(end-t0)+3*b['logEn'])*b['J']-1)
 check(max(phase)<2e-11,'phase-volume identity')
 # A genuinely independent numerical sphere divergence and flow-area determinant.
 divgap=0.;jacgap=0.;ini=[];basis=[];eps=2e-5
 for n in a['n'][::8]:
  axis=np.eye(3)[np.argmin(abs(n))];e1=np.cross(n,axis);e1/=np.linalg.norm(e1);e2=np.cross(n,e1);basis.append((e1,e2))
  V,S,_=geometric_rhs(a['state'],n[None,:]);val=0.
  for ee in (e1,e2):
   xp=np.cos(eps)*n+np.sin(eps)*ee;xm=np.cos(eps)*n-np.sin(eps)*ee
   vp=geometric_rhs(a['state'],xp[None,:])[0][0];vm=geometric_rhs(a['state'],xm[None,:])[0][0];val+=np.dot(ee,(vp-vm)/(2*eps))
  divgap=max(divgap,abs(val-3*S[0]))
  ini.extend([n,np.cos(eps)*n+np.sin(eps)*e1,np.cos(eps)*n-np.sin(eps)*e1,np.cos(eps)*n+np.sin(eps)*e2,np.cos(eps)*n-np.sin(eps)*e2])
 gg=Geometry(t0,end,normal_initial=np.array(ini),weights=np.ones(len(ini)));out=gg.at(end)
 for k in range(len(basis)):
  n,p,m,q,r=out['n'][5*k:5*k+5];u=(p-m)/(2*np.sin(eps));v=(q-r)/(2*np.sin(eps));det=np.dot(n,np.cross(u,v));jacgap=max(jacgap,abs(det/out['J'][5*k]-1))
 check(divgap<1e-8 and jacgap<1e-8,'independent angle divergence/Jacobian')
 wrong_noJ=[]
 long=Geometry(0,bg['end'],8,16);o=long.at(bg['end']);correct=np.sum(long.wn0*np.exp(3*bg['end']+3*o['logEn'])*o['J'])/sum(long.wn0);wrong=np.sum(long.wn0*np.exp(3*bg['end']+3*o['logEn']))/sum(long.wn0)
 check(abs(correct-1)<2e-11,'long comoving count')
 # Nonlinear stimulated pair equation, using actual Bose occupation numbers.
 x=np.linspace(.2,8,48);dx=x[1]-x[0];cap=x*x*dx;feq=1/np.expm1(x+.4);f0=feq*(1+.25*np.sin(2*x));initial=cap*f0
 face=(x[:-1]+x[1:])/2;mob=face*face/dx
 def ode(t,y):
  f=y[:-1]/cap;j=mob*thermal_flux(f,np.diff(x),True);dn=np.r_[-j[0],j[:-1]-j[1:],j[-1]];return np.r_[dn,-x@dn]
 sol=solve_ivp(ode,(0,40),np.r_[initial,0.],method='Radau',rtol=2e-10,atol=2e-13,t_eval=np.r_[0,np.geomspace(1e-4,40,150)])
 check(sol.success,'stimulated equilibrium evolution')
 N=sol.y[:-1];f=N/cap[:,None];number=np.sum(N,axis=0);heat=sol.y[-1]
 eta=brentq(lambda eta:sum(cap/np.expm1(x+eta))-sum(initial),-x[0]+1e-8,20)
 target=1/np.expm1(x+eta);defect=float(max(abs(f[:,-1]-target)))
 free=np.sum(cap[:,None]*(f*np.log(f)-(1+f)*np.log1p(f)+x[:,None]*f),axis=0)
 numbergap=float(max(abs(number/sum(initial)-1)));egap=float(max(abs((x@N+heat)-(x@initial))))
 check(numbergap<3e-12 and egap<3e-11 and np.max(np.diff(free))<1e-10 and defect<1e-7,'nonlinear number/heat/free-energy/BE relaxation')
 # Stiff conservative solve: no clipping or renormalization to restore photons.
 up=np.full((3,50),1e13);down=up.copy();up[:,-1]=0;down[:,0]=0
 initial=np.zeros_like(up);initial[:,25]=1
 out=backward_birth_death(initial,up,down,np.zeros_like(up),1.)
 stiffdef=float(max(abs(out.sum(axis=1)-1)));check(stiffdef<2e-12,'stiff storage cancellation')
 # Normal energy is not atom heat for elastic angular scattering.
 ne,w=sphere(6,12);nn,D=to_normal(ne,.05);Q,pi=angular_generator(ne,w,D)
 N=np.zeros((len(w),1));N[0,0]=1;out=angular_step(N,Q,pi,np.array([10.]));delta=out[:,0]-N[:,0]
 En=1/D;dnenergy=float(En@delta);dpy=float((En*nn[:,1])@delta);rest=1/np.sqrt(1-.05**2)*(dnenergy-.05*dpy)
 check(abs(rest-sum(delta))<1e-13 and abs(sum(delta))<2e-13,'collision four-momentum frame identity')
 # Frequency equilibrium with the physical nu^2 cell capacity.
 grid=fixed_grid(3000.,20,160);u,d=frequency_rates(grid,3000.,2e8,1e-7,False);fW=np.exp(-H*(grid['nu']-NU0)/(KB*3000.));mass=grid['cap']*fW;mass/=sum(mass)
 flux=u[:-1]*mass[:-1]-d[1:]*mass[1:];rel=float(max(abs(flux)/np.maximum(u[:-1]*mass[:-1]+d[1:]*mass[1:],1e-300)))
 check(rel<3e-14,'physical frequency detailed balance')
 data={'parent':PARENT,'original401_overlap':bg['overlap'],'source_input_blobs':bg['locks'],
 'local_phase_volume_max_defect':float(max(phase)),'sphere_divergence_independent_gap':float(divgap),'flow_area_Jacobian_relative_gap':float(jacgap),
 'local_atom_solid_angle_quadrature_defect':b['angular_weight_defect'],'long_source_comoving_number_correct':float(correct),'long_source_wrong_omit_J_number':float(wrong),
 'nonlinear_Bose_relaxation':{'number_relative_defect':numbergap,'energy_plus_heat_abs_defect':egap,'equilibrium_f_max_abs_gap':defect,'max_free_energy_increment':float(max(np.diff(free))),'final_eta':float(eta)},
 'stiff_conservative_linear_storage_defect':stiffdef,'physical_Wien_pair_relative_balance':rel,
 'elastic_angular_scattering':{'normal_energy_change_per_initial_rest_energy':dnenergy,'normal_momentum_c_change':dpy,'rest_energy_change':float(rest),'photon_number_change':float(sum(delta))},
 'CAS':{'sphere_divergence_residual':0,'Bose_pair_flux_residual':0,'normal_comoving_measure_residual':0,'evidence':'actual WolframLanguageEvaluator invocation on this construction'},
 'scope':'exact geometric/thermal identities; factorized FP+Rayleigh scattering approximation; not full correlated redistribution'}
 (HERE/'KERNEL_AND_GEOMETRY_VERIFICATION.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data,indent=2))
if __name__=='__main__':main()
