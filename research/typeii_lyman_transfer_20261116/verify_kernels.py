#!/usr/bin/env python3
"""Independent stationary characteristics and closed atom/photon exchange tests."""
import json
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp,quad
from scipy.special import wofz
from line_transfer import *
HERE=Path(__file__).resolve().parent

def main():
 # Escape in cumulative-opacity coordinate, exact for any normalized shared profile.
 shared=[]
 for tau in (0.,1e-12,1e-6,.1,1.,100.,1e8):
  p=np.array([.03,.07,.2,.5,.2]);got=singleflight(p,tau*p)
  shared.append(abs(got-sobolev(tau))/sobolev(tau))
 check(max(shared)<3e-14,'CDF escape identity')
 # Native line profile is NOT renormalized to its finite support.
 masses=[]
 for X in (6.,20.,80.):
  g=line_grid(3000.,halfwidth=X,cells=int(16*X));m=quad(lambda x:np.real(wofz(x+1j*g['a']))/np.sqrt(np.pi),-X,X,epsabs=1e-11,epsrel=2e-12,points=[-3,0,3])[0]
  err=abs(g['band_mass']-m);check(err<3e-10,'profile cell vs adaptive integral')
  masses.append({'X':X,'mass':g['band_mass'],'adaptive_gap':err})
 # Exact steady characteristic against conservative photon-count upwind FV.
 # Manufactured frozen Hray sets the numerical experiment, not a cosmological run.
 conv=[]
 T=3000.;hr=1e-4;tau=30.;fs=1e-9
 delta=tau*8*np.pi*hr/(ALYA*(C/NU0)**3)
 nu=delta*fs;nl=(delta+nu)/GRATIO
 eps=np.sqrt(2*KB*T/(MH*C*C));dn=NU0*eps;a=ALYA/(4*np.pi*dn)
 def fun(x,y):
  vfreq=NU0+dn*x;profile=np.real(wofz(x+1j*a))/np.sqrt(np.pi)
  therm=np.exp((H*vfreq-E0)/(KB*T));absorb=ALYA*C**3*(GRATIO*nl*therm-nu)/(8*np.pi*hr*vfreq**3)*profile
  return [absorb*y[0]-profile]
 ref=solve_ivp(fun,(20.,-20.),[0.],method='Radau',rtol=3e-11,atol=1e-13,max_step=.07)
 check(ref.success,'independent characteristic solver');refout=float(ref.y[0,-1])
 for n in (100,200,400,800):
  g=line_grid(T,halfwidth=20,cells=n);s=frozen_steady(g,nl,nu,T,hr)
  got=s['red_out']/(ALYA*nu);gap=abs(got-refout)
  check(abs(s['number_residual'])/s['gross_number']<5e-14,'finite volume number ledger')
  check(abs(s['energy_residual'])/(E0*s['gross_number'])<5e-14,'finite volume energy/work ledger')
  conv.append({'cells':n,'out_per_spontaneous_full_rate':got,'independent_characteristic':refout,'abs_error':gap})
 check(conv[-1]['abs_error']<conv[0]['abs_error']/3 and conv[-1]['abs_error']<2e-5,'FV refinement target')
 # Closed two-level + finite line-photon population. Fixed Tm reservoir receives
 # detuning heat. Physical optical constants and nH; no expansion in this test.
 g=line_grid(T,halfwidth=8,cells=32);nl=1e8;ueq=GRATIO*nl*np.exp(-E0/(KB*T));nt=nl+ueq
 f0=planck(H*g['nu']/(KB*T));Nscale=g['capacity']*f0;uscale=ueq
 Escale=float(np.dot(H*g['nu'],Nscale));corr=np.exp((H*g['nu']-E0)/(KB*T));w=ALYA*g['p'];det=E0-H*g['nu']
 y0=np.r_[1.2,.9*np.ones(32),0.]
 def rhs(t,y):
  u=uscale*y[0];N=Nscale*y[1:-1];f=N/g['capacity'];l=nt-u
  F=w*(u*(1+f)-GRATIO*l*corr*f)
  return np.r_[-sum(F)/uscale,F/Nscale,np.dot(det,F)/Escale]
 def jac(t,y):
  u=uscale*y[0];f=Nscale*y[1:-1]/g['capacity'];l=nt-u
  fu=w*(1+f+GRATIO*corr*f);fn=w*(u-GRATIO*l*corr)/g['capacity']
  J=np.zeros((34,34));J[0,0]=-sum(fu);J[0,1:-1]=-fn*Nscale/uscale
  J[1:-1,0]=fu*uscale/Nscale;J[1:-1,1:-1]=np.diag(fn)
  J[-1,0]=np.dot(det,fu)*uscale/Escale;J[-1,1:-1]=det*fn*Nscale/Escale
  return J
 times=np.unique(np.r_[0.,np.geomspace(1e-11,10.,200)]);sol={}
 for method in ('Radau','BDF'):
  s=solve_ivp(rhs,(0.,10.),y0,method=method,t_eval=times,jac=jac,rtol=2e-10,atol=2e-12)
  check(s.success,'closed line atom+photon '+method);check(np.min(s.y[:-1])>0,'positive states')
  sol[method]=s.y
 out=sol['Radau'];u=uscale*out[0];N=Nscale[:,None]*out[1:-1];heat=Escale*out[-1]
 excit=u+N.sum(axis=0);et=E0*u+(H*g['nu'])@N+heat
 nerr=float(np.max(abs(excit/excit[0]-1)));eerr=float(np.max(abs(et/et[0]-1)))
 gap=float(np.max(abs(sol['Radau']-sol['BDF'])))
 check(nerr<2e-10 and eerr<2e-10 and gap<2e-7,'closed atom/photon independent integration')
 # Thermal correction must be tested channel by channel, not just total flux.
 thermal=collision(g,nl,ueq,f0,T,True);wrong=collision(g,nl,ueq,f0,T,False)
 check(thermal['balance_relative']<2e-12 and wrong['balance_relative']>1e-4,'thermal correction falsifier')
 result={'Sobolev_CDF_max_relative_gap':max(shared),'profile_mass_comparison':masses,
 'finite_volume_characteristic_convergence':conv,'closed_atom_photon':{'nH_m3':nt,'duration_s':10.,'excitation_number_max_relative_error':nerr,'total_energy_max_relative_error':eerr,'Radau_BDF_scaled_state_max_gap':gap,'physical_scope':'fixed-T two-level finite-line collision test; no cosmological populations'},
 'thermal_max_cell_balance_residual':thermal['balance_relative'],'identical_profiles_wrong_balance_residual':wrong['balance_relative'],
 'A_2p1s_s':ALYA,'line_gap_eV':E0/EV,'line_lambda_m':C/NU0}
 (HERE/'KERNEL_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
 np.savetxt(HERE/'CLOSED_ATOM_PHOTON_TRACE.csv',np.column_stack((times,u,N.sum(axis=0),heat,excit,et)),delimiter=',',header='proper_t_s,n_upper,photons_m3,heat_J_m3,excitation_m3,energy_J_m3',comments='')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
