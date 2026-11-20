#!/usr/bin/env python3
"""Leading-recoil Hummer shift compared to parent and finite source outcomes.

Keep recoil shift, raw classical RII0, and arbitrarily thermally symmetrized
finite operators separate. None of these is full quantum recoil redistribution.
"""
from pathlib import Path
import json,hashlib
import numpy as np
import hummer_rii as h
import rii_transport as op
import outer_hummer as outer
from rii_transport import src
HERE=Path(__file__).resolve().parent
def check(c,msg):
 if not bool(c):raise RuntimeError(msg)
def main():
 T=3000.745332620248;nl=253341572.44286457
 recoil=src.H*src.NU0/(src.MH*src.C**2*np.sqrt(2*src.KB*T/(src.MH*src.C**2)))
 e=np.linspace(-120,120,97)
 diffs=[]
 for x in (2.,8.,20.,40.,80.):
  for mu in (-1.,0.,.5):
   a=h.leading_recoil_bins(x,mu,.001,e,recoil)
   b=src.conditional_bins(x,mu,.001,e,recoil)
   diffs.append({'x_in':x,'cos_theta':mu,'max_abs':float(max(abs(a-b))),
                 'L1':float(sum(abs(a-b)))})
 maxgap=max(v['max_abs'] for v in diffs)
 check(maxgap<3e-10,'analytic leading recoil not matched to independent Maxwell source')
 raw0=op.matrix_kernel(X=40.,T=T,nl=nl,thermo_sym=False,leading_recoil=False)
 rawr=op.matrix_kernel(X=40.,T=T,nl=nl,thermo_sym=False,leading_recoil=True)
 symr=op.matrix_kernel(X=40.,T=T,nl=nl,thermo_sym=True,leading_recoil=True)
 check(rawr['wien_detailed_balance_defect']>1e-5 and symr['wien_detailed_balance_defect']<1e-12,
       'raw recoil not physically exact or thermal pair sym missing')
 cases={}
 for name,kw in [
   ('LEADING_RECOIL_RAW_X40_512',dict(X=40.,steps=512,thermo_sym=False,leading_recoil=True)),
   ('LEADING_RECOIL_SYM_X40_512',dict(X=40.,steps=512,thermo_sym=True,leading_recoil=True)),
   ('LEADING_RECOIL_RAW_X40_256',dict(X=40.,steps=256,thermo_sym=False,leading_recoil=True)),
 ]:
  val=outer.evolve(save=name,**kw)
  check(abs(sum(val[k] for k in ('survival','red_outer_exit','blue_outer_exit','tagged_ionized'))-1)<5e-7,
        'actual source recoil normal-count failure')
  cases[name]=val
  print('RECOIL_SOURCE',name,{k:val[k] for k in ('survival','red_outer_exit','tagged_ionized','gross_outer_to_inner_reentries')},flush=True)
 old=json.loads((HERE/'HUMMER_SOURCE_WING_CASES.json').read_text())['results']
 compare={
  'leading_recoil_raw_minus_no_recoil_raw_tagged_ionized':
   cases['LEADING_RECOIL_RAW_X40_512']['tagged_ionized']-old['H40_RAW_512']['tagged_ionized'],
  'leading_recoil_sym_minus_norecoil_sym_tagged_ionized':
   cases['LEADING_RECOIL_SYM_X40_512']['tagged_ionized']-old['H40_512']['tagged_ionized'],
  'leading_recoil_sym_minus_leading_recoil_raw_tagged_ionized':
   cases['LEADING_RECOIL_SYM_X40_512']['tagged_ionized']-cases['LEADING_RECOIL_RAW_X40_512']['tagged_ionized'],
  'leading_raw_256_vs512_time_step_ionization_difference':
   cases['LEADING_RECOIL_RAW_X40_512']['tagged_ionized']-cases['LEADING_RECOIL_RAW_X40_256']['tagged_ionized']
 }
 report={
  'schema':'bass.typeii.classical_RII0_leading_recoil_shift_hostile.v1',
  'recoil_width_shift':recoil,
  'analytic_shift_vs_parent_direct_recoil_max_conditional_gap':maxgap,
  'original_recoil_shift_conditions':diffs,
  'static_raw_Wien_defect_no_recoil':raw0['wien_detailed_balance_defect'],
  'static_raw_Wien_defect_with_recoil_shift':rawr['wien_detailed_balance_defect'],
  'static_symmetrized_Wien_defect_with_recoil_shift':symr['wien_detailed_balance_defect'],
  'physical_claim_limit':'first-order shift only, no full microscopic recoil operator or exact quantum detailed balance',
  'source_cases':cases,'paired':compare
 }
 (HERE/'LEADING_RECOIL_AND_THERMAL_SENSITIVITY.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 print('RECOIL_PAIRED',json.dumps(compare,sort_keys=True))
if __name__=='__main__':main()
