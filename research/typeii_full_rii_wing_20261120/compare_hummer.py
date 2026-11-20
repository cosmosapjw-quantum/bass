#!/usr/bin/env python3
"""Original Hummer RII0 Voigt closed form vs independently integrated parent Maxwell."""
import json,hashlib,ast,subprocess
from pathlib import Path
import numpy as np
from scipy.integrate import quad
import hummer_rii as h
import rii_transport as rt
from rii_transport import src
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PARENT="b23e75dcd2e8145cb161339bf08b6e1f522626f5"
def check(c,m):
 if not bool(c):raise RuntimeError(m)
def git(*a):return subprocess.check_output(['git','-C',str(ROOT),*a],text=True).strip()
def source():
 for path in ('research/typeii_correlated_outer_20261119/correlated.py',
              'research/typeii_correlated_outer_20261119/outer_transport.py',
              'research/typeii_redistribution_phase_20261116/redistribution.py'):
  check(git('hash-object',path)==git('rev-parse',PARENT+':'+path),'parent source identity '+path)
 return True
def execute():
 source()
 compare=[]
 edges=np.linspace(-120,120,97)
 for x in (2.,8.,20.,40.,80.):
  for mu in (-1.,0.,.5):
   exact=h.conditional_bins(x,mu,.001,edges)
   direct=src.conditional_bins(x,mu,.001,edges,recoil=0.)
   compare.append({'incident_x':x,'cos_theta':mu,'exact_mass_in_band':float(sum(exact)),
       'direct_mass_in_band':float(sum(direct)),'max_abs_conditional_probability_gap':float(max(abs(exact-direct))),
       'L1_conditional_gap':float(sum(abs(exact-direct)))})
 mx=max(v['max_abs_conditional_probability_gap'] for v in compare)
 check(mx<3e-10,'closed Hummer vs Maxwell integral discrepancy')
 x=2.;damp=.001
 from scipy.integrate import quad
 m={}
 for mu in (-.5,0.,.5):
  marg=quad(lambda xp:h.joint(x,float(xp),mu,damp),-60,60,epsabs=1e-12,epsrel=4e-9)[0]
  m[str(mu)]={'integrated_joint':marg,'reference_Voigt_phi':float(h.phi(x,damp)),
                'relative_defect':float(marg/h.phi(x,damp)-1)}
 check(max(abs(v['relative_defect']) for v in m.values())<2e-4,'Hummer exact marginal failed')
 T=3000.745332620248;nl=253341572.44286457
 analytic=rt.matrix_kernel(X=40.,T=T,nl=nl,thermo_sym=True)
 original=src.matrix_kernel(X=40.,T=T,nl=nl)
 raw=rt.matrix_kernel(X=40.,T=T,nl=nl,thermo_sym=False)
 check(analytic['Q'].shape==original['Q'].shape,'source kernel matrix change')
 rel=float(np.max(abs(analytic['Q']-original['Q']))/max(1.,np.max(abs(original['Q']))))
 checks={
  'closed_vs_integrated_max_abs15':mx,'source_RII0_matrix_vs_parent_leading_recoil_max_relative_to_max_rate':rel,
  'source_hummer_raw_generator_Wien_balance_defect':float(raw['wien_detailed_balance_defect']),
  'source_hummer_thermally_pair_sym_generator_balance_defect':float(analytic['wien_detailed_balance_defect']),
  'source_hummer_thermo_sym_column_relative_defect':float(analytic['column_defect']),
  'joint_conditional_raw_L1_vs_factorized':float(analytic['factorization_gap']),
  'natural_damping_a':analytic['kernel_meta']['a'],
  'true_model':'original Hummer II atom-frame coherent radiative damping no recoil',
  'separate_thermodynamic_model':'arithmetic pairwise Wiener-flux sym, alters raw microscopic RII0',
  'absolute_recoil_corrected_full_RII':'NOT_ESTABLISHED'
 }
 check(checks['source_hummer_thermally_pair_sym_generator_balance_defect']<1e-12,
       'thermal correction static reciprocity')
 check(checks['source_hummer_thermo_sym_column_relative_defect']<1e-12,
       'thermal correction photon number')
 (HERE/'HUMMER_RII_ORIGINAL_BENCHMARK.json').write_text(json.dumps({
 'source_parent':PARENT,'source_verified':True,
 'original_conditioned_velocity_comparisons':compare,'Hummer_closed_Voigt_marginal_checks':m,
 'static_source_kernel_checks':checks,'source_object':'classical recoil-free RII0, not full quantum polarized redistribution'
 },indent=2,sort_keys=True)+'\n')
 print(json.dumps(checks,indent=2,sort_keys=True))
if __name__=='__main__':execute()
