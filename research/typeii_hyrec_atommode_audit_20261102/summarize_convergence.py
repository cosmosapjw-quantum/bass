#!/usr/bin/env python3
"""Separate empirical atomic-step, model, quadrature and physical-closure errors."""
import json,math
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent
r=json.loads((P/'MODE_COMPARISON_RESULTS.json').read_text())
cs={(x['a'],x['reference']):x for x in r['comparisons']}
conv={}
for bg in ('FLRW','TypeII'):
    a=np.loadtxt(P/'outputs'/('FULL_r1_'+bg+'.dat'))
    b=np.loadtxt(P/'outputs'/('FULL_r2_'+bg+'.dat'))
    c=np.loadtxt(P/'outputs'/('FULL_r4_'+bg+'.dat'))
    w=(a[:,0]>=300)&(a[:,0]<=1700)
    d1=abs(a[:,1]-b[:,1]);d2=abs(b[:,1]-c[:,1])
    clean=w&(a[:,0]<=1500)
    at=6900
    conv[bg]={'global_step1_half_max_abs':float(max(d1[w])),
              'global_half_quarter_max_abs':float(max(d2[w])),
              'global_max_norm_monotone':bool(max(d2[w])<max(d1[w])),
              'z300_1500_step1_half_max_abs':float(max(d1[clean])),
              'z300_1500_half_quarter_max_abs':float(max(d2[clean])),
              'at_z1100_delta1':float(d1[at]),'at_z1100_delta2':float(d2[at]),
              'at_z1100_observed_order':math.log(d1[at]/d2[at],2),
              'interpretation':'Empirical successive-difference diagnostics, not a rigorous error bound; switch locations can dominate the global norm.'}
q=r['optical_depths'];f=q['FULL_r4_TypeII'];d={}
for name in ('SWIFT_r1_TypeII','SWIFT_matched_TypeII','EMLA2s2p_r1_TypeII','FULL_r1_TypeII','FULL_r2_TypeII'):
    delta=np.array(q[name]['all_rays'])-np.array(f['all_rays'])
    d[name]={'minus_FULL_r4_plus':q[name]['plus']-f['plus'],'minus_FULL_r4_minus':q[name]['minus']-f['minus'],
             'max_all_rays_abs':float(max(abs(delta))),'max_all_rays_relative':float(max(abs(delta)/np.array(f['all_rays'])))}
match=cs['SWIFT_matched_TypeII','FULL_r4_TypeII']
flrw=cs['SWIFT_matched_FLRW','FULL_r4_FLRW']
result={'full_step_diagnostics':conv,'optical_depth_differences':d,
        'same_atomic_step_model_discrepancy_TypeII':match,
        'same_atomic_step_model_discrepancy_FLRW':flrw,
        'max_relative_discrepancy_amplification_TypeII_over_FLRW':match['max_rel_xe']/flrw['max_rel_xe'],
        'quadrature_abs_error_diagnostic':r['max_gauss8_16_gap'],
        'proper_clock_correction_scale_max_Gamma_minus1':r['clock_and_thermal_closure']['max_Gamma_minus_one'],
        'not_admitted':['global Richardson extrapolation across phase switches','arbitrary-H precision guarantee','covariant tilted-atom accuracy','removal of the retained SWIFT refinement failure']}
(P/'CONVERGENCE_AND_ERROR_BUDGET.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
