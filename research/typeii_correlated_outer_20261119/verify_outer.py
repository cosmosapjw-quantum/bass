#!/usr/bin/env python3
"""Independent time discretization and one bounded same-author hostile review.

Numeric identities verified on actual immutable BASS source and exact current
native Python artifacts, with failure kinds separated from physical assumptions.
"""
import json,hashlib,subprocess,math
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse.linalg import expm_multiply,spsolve
from scipy.sparse import csc_matrix,eye
from correlated import *
from outer_transport import scattering_tails
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PARENT="55aa1a61ac66019f0901dd2cb02ddfdcbb5fca9c"
def check(cond,msg):
 if not bool(cond):raise RuntimeError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args],text=True).strip()
def verify():
 base=json.loads((HERE/'OUTER_MATCHING_RESULTS.json').read_text())
 fine=json.loads((HERE/'OUTER_REFINEMENT.json').read_text())
 match=json.loads((HERE/'MATCHED_BAND_REFINEMENT.json').read_text())
 cases={c['case']:c for c in base['cases']}
 check(len(cases)==6 and len(fine)==4 and len(match)==2,'source 12-case coverage not restored')
 original=json.loads((ROOT/'research/typeii_host_preflight_20261101/SOURCE_LOCK.json').read_text())['original_git_blobs_sha1']
 for name,want in original.items():check(git('hash-object',name)==want,'original BASS protected Git blob drift '+name)
 for path in ['research/typeii_redistribution_phase_20261116/redistribution.py',
              'research/typeii_redistribution_phase_20261116/packet_campaign.py',
              'research/typeii_cascade_effective_20261116/SOURCE_TRACE_STATIONARY.csv']:
  check(git('hash-object',path)==git('rev-parse',PARENT+':'+path),'parent source drift '+path)
 # Static source kernel: two independent integration algorithms.
 g=matrix_kernel(X=40.,angle_order=6,T=3000.,nl=2.5e8)
 q=g['Q'];na=len(g['wa']);nf=len(g['x'])
 y=(g['wa'][:,None]*g['cap'].reshape(na,nf)/g['wa'][:,None]*
     np.exp(-.5*((g['x'][None,:]-3)/3)**2)).reshape(-1)
 y=y/y.sum()
 exact=expm_multiply(csc_matrix(q*.5),y)
 bdf=solve_ivp(lambda t,x:q@x,(0,.5),y,method='BDF',jac=csc_matrix(q),
               atol=1e-13,rtol=2e-11)
 check(bdf.success,'independent unsplit static BDF failed')
 gap=float(max(abs(exact-bdf.y[:,-1])))
 check(gap<2e-9,'source static BDF vs Krylov exponential mismatch '+str(gap))
 check(abs(exact.sum()-1)<3e-13 and min(exact)>-1e-13,
       'static photon number and positivity')
 err=[]
 for steps in (4,8,16,32,64):
  z=y.copy();dt=.5/steps;Aimp=eye(len(y),format='csc')-csc_matrix(q*dt)
  for _ in range(steps):z=spsolve(Aimp,z)
  err.append(float(np.max(abs(z-exact))))
 check(all(err[i+1]<err[i] for i in range(len(err)-1)),
       'first order implicit static convergence nonmonotone')
 # Raw coherent conditional transitions + explicit outside-tail probability:
 r,_=raw_kernel(g['x'],g['edges'],g['T'],g['na'],g['wa'])
 domain=r.sum(axis=(0,1))
 tr,tb=scattering_tails(g)
 conditional_gap=float(np.max(abs(domain.reshape(-1)+tr+tb-1)))
 check(conditional_gap<3e-4,'raw kernel plus true outer tails not normalized '+str(conditional_gap))
 # Explicit same mesh/time comparison; do not compare across discretizations.
 for k in ('outer_40_time256','outer_40_time512','outer_40_frozen_time512','outer_40_factorized_time512'):
  check(abs(sum(fine[k][f] for f in ('survival','red_outer_exit','blue_outer_exit','tagged_ionized'))-1)<5e-7,
        'tagged outcome ledger '+k)
 for k in ('core20_time512','outer80_time512'):
  check(abs(sum(match[k][f] for f in ('survival','red_outer_exit','blue_outer_exit','tagged_ionized'))-1)<5e-7,
        'matched boundary outcome ledger '+k)
 a=[cases['outer_40_time128']['tagged_ionized'],fine['outer_40_time256']['tagged_ionized'],fine['outer_40_time512']['tagged_ionized']]
 time_decrease=[abs(cases['outer_40']['tagged_ionized']-a[0]),abs(a[0]-a[1]),abs(a[1]-a[2])]
 check(time_decrease[1]<time_decrease[0] and time_decrease[2]<time_decrease[1],
       'time discretization did not converge in observed source')
 # Paired comparisons at exact matching resolution.
 end=fine['outer_40_time512']
 fact=fine['outer_40_factorized_time512']
 frozen=fine['outer_40_frozen_time512']
 core=match['core20_time512'];wide=match['outer80_time512']
 paired={
  'joint_minus_factorized_ionized':end['tagged_ionized']-fact['tagged_ionized'],
  'evolving_minus_frozen_ionized':end['tagged_ionized']-frozen['tagged_ionized'],
  'wide_minus_40_ionized':wide['tagged_ionized']-end['tagged_ionized'],
  'core20_minus_outer40_red_exit':core['red_outer_exit']-end['red_outer_exit'],
  'core20_minus_outer40_blue_exit':core['blue_outer_exit']-end['blue_outer_exit'],
 }
 # The strong source-opacity regime can suppress final observable correlation
 # despite a large single-scattering raw joint-vs-factorized L1 gap.
 check(g['factorization_gap']>.05 and abs(paired['joint_minus_factorized_ionized'])<1e-4,
       'physical local covariance vs saturated terminal comparison inconsistent')
 check(end['gross_outer_to_inner_reentries']>1 and end['gross_inner_to_outer_crossings']>1,
       'outer reentry physically absent')
 # One bounded self-hostile suite: wrong external/core normalization,
 # unphysical inputs, false local-to-global admission and missing source frames.
 invalid={}
 cases_bad=[
  ('negative_lorentz',lambda:conditional_bins(1.,0.,-.2,np.array([-1.,0.,1.]))),
  ('outside_mu',lambda:conditional_bins(1.,1.2,.01,np.array([-1.,0.,1.]))),
  ('nonmonotonic_bin_edges',lambda:conditional_bins(1.,0.,.01,np.array([-1.,1.,0.]))),
  ('negative_source_density',lambda:matrix_kernel(X=40.,nl=-1)),
  ('invalid_source_angle',lambda:matrix_kernel(angle_order=7)),
  ('unsupported_outer_band',lambda:matrix_kernel(X=240.)),
 ]
 for tag,fn in cases_bad:
  try:fn()
  except (ValueError,RuntimeError):invalid[tag]='REJECTED'
  else:raise RuntimeError('bad source input accepted '+tag)
 wrong_core_absorption=end['gross_outer_to_inner_reentries'] if core['gross_outer_to_inner_reentries']==0 else 0
 check(wrong_core_absorption>0.5,'false no-reentry comparison was not detected')
 # No global-escape or exact kernel assertions should be added.
 out={
  'source_parent':PARENT,'original_BASS_source_blobs':len(original),
  'static_number_exact_Krylov_and_BDF_max_abs_gap':gap,
  'static_backward_Euler_4_8_16_32_64_max_abs_errors':err,
  'original_raw_conditional_inside_plus_tails_max_abs_defect':conditional_gap,
  'static_correlated_Bose_Wien_defect':g['wien_detailed_balance_defect'],
  'joint_raw_vs_factorized_L1':g['factorization_gap'],
  'time_step_64_to128_128to256_256to512_ionization_gaps':time_decrease,
  'same_grid_paired_differences':paired,
  'matched_outer40':{k:end[k] for k in ('survival','red_outer_exit','blue_outer_exit','tagged_ionized','gross_inner_to_outer_crossings','gross_outer_to_inner_reentries')},
  'matched_outer80':{k:wide[k] for k in ('survival','red_outer_exit','blue_outer_exit','tagged_ionized','gross_outer_to_inner_reentries')},
  'matched_core20':{k:core[k] for k in ('survival','red_outer_exit','blue_outer_exit','tagged_ionized')},
  'wrong_absorb_core_omits_gross_returns':wrong_core_absorption,
  'malformed_inputs':invalid,
  'hostile_physical_limits':['factorized versus joint source raw conditional differs but final tagged ionization is saturated',
   'finite-band terminal state is not global escape',
   'correlated kernel symmetrized to enforce thermodynamic balance, not exact microscopic RII',
   'redistribution spectrum/angle shape frozen at source start',
   'sources population and H are prescribed, no Einstein-atom-photon backreaction',
   'independent source numerical BDF tests frozen generator, not full evolving nonlinear transport'],
  'reviewer':'same author hostile and independent numerical algorithm, no distinct-author blind referee'
 }
 (HERE/'FINAL_VERIFICATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':verify()
