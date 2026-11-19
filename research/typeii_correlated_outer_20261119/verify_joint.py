#!/usr/bin/env python3
"""An independent source-conditional joint-kernel scientific test."""
import json,hashlib
from pathlib import Path
import numpy as np
from correlated import *
def test():
 T=3000.;x=2.;dn=NU0*np.sqrt(2*KB*T/(MH*C*C))
 a=A/(4*np.pi*dn); recoil=H*NU0/(MH*C*C*np.sqrt(2*KB*T/(MH*C*C)))
 edges=np.linspace(-25,25,201);centers=(edges[:-1]+edges[1:])/2
 moments={}
 for mu in (1.,0.,-1.):
  p=conditional_bins(x,mu,a,edges,recoil)
  check(np.isfinite(p).all() and p.min()>=0 and 0.999<sum(p)<=1.00001,"conditional positivity/normalization")
  moments[str(mu)]={'mean':float(centers@p/sum(p)),
                   'std':float(np.sqrt(max(0.,(centers*centers)@p/sum(p)-(centers@p/sum(p))**2))),
                   'resolved_mass':float(sum(p))}
 check(moments['1.0']['mean']>moments['0.0']['mean']+1.8,'angle-frequency correlation 1 vs0')
 check(moments['0.0']['mean']>moments['-1.0']['mean']+1.8,'angle-frequency correlation 0 vs-1')
 g=matrix_kernel(X=40,angle_order=6,T=T)
 q=g['Q'];pi=g['pi'];cap=g['cap']
 check(q.shape[0]==q.shape[1],'joint generator matrix square')
 check(max(abs(q.sum(axis=0)))<1e-3,'absolute generator column closure') # rates can exceed1e9, check scaled separately
 check(g['column_defect']<1e-14,'relative generator column closure')
 check(np.min(q-np.diag(np.diag(q)))>=-1e-15,'positive rates')
 check(g['wien_detailed_balance_defect']<1e-13,'Wien pair flux balance')
 check(g['factorization_gap']>0.01,'genuine angle-frequency correlation')
 # The finite static sphere has exactly paired Bose-stimulated thermal fluxes:
 energy=(NU0+dn*g['x'])
 eta=.7
 f=1/np.expm1(eta+H*(energy-NU0)/(KB*T))
 N=cap*f.reshape((1,-1)).repeat(len(g['wa']),axis=0).reshape(-1) if False else cap*np.tile(f,len(g['wa']))
 flux=q*(N[None,:]*(1+(N/cap)[:,None]))
 # opposite direction contribution from its partner
 adj=flux-flux.T
 defect=float(np.max(abs(adj))/max(np.max(flux),1e-300))
 check(defect<2e-12,'stimulated Bose equilibrium: '+str(defect))
 # Independent nonlinear evolution for positive source counts, conservative
 # generator's equilibrium state is stationary at the thermal ratio.
 stationary=np.max(abs(q@pi))/max(1.,np.max(abs(q)*pi[None,:]))
 check(stationary<1e-12,'thermal stationary source: '+str(stationary))
 # Extrapolating identity to complete redistribution is forbidden.
 src=Path(__file__).resolve().parent
 result={
 'conditional_kernel':'coherent atom frame Maxwell + Lorentz absorption with leading recoil, finite angular quadrature and pairwise thermal symmetrization',
 'full_Hummer_RII_or_polarization':'NOT_IMPLEMENTED',
 'source_temperature_K':T,'natural_width_a':float(a),'recoil_eta':float(recoil),
 'x_in':x,'conditional_by_mu':moments,'matrix_shape':list(q.shape),
 'column_defect_relative':g['column_defect'],'Wien_balance_rel_defect':g['wien_detailed_balance_defect'],
 'stimulated_BE_pair_defect':defect,'stationary_eigenvector_rel_defect':float(stationary),
 'factorized_joint_raw_L1_gap':g['factorization_gap'],
 'core_to_outer_scattering_rate_s':g['core_outward_rate'],
 'outer_to_core_scattering_rate_s':g['core_return_rate'],
 'original_PARENT_SHA':'55aa1a61ac66019f0901dd2cb02ddfdcbb5fca9c',
 'result':'KINEMATIC_CORRELATION_AND_FINITE_STATIC_THERMAL_KERNEL_NUMERICALLY_CHECKED'}
 (src/'JOINT_KERNEL_RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':test()
