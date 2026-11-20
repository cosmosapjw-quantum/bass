#!/usr/bin/env python3
"""Source-matched BASS Type II photon wings under classical Hummer RII0.

Recoil-free, explicitly thermal-symmetrized finite RII0 is compared with raw
RII0 and old parent leading-recoil surrogate. No global escape is asserted.
"""
import json,time,hashlib,subprocess
from pathlib import Path
import numpy as np
import outer_hummer as o

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PARENT="b23e75dcd2e8145cb161339bf08b6e1f522626f5"
def check(cond,msg):
 if not bool(cond):raise RuntimeError(msg)
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args],text=True).strip()
def check_source():
 for file in ('research/typeii_correlated_outer_20261119/outer_transport.py',
   'research/typeii_correlated_outer_20261119/correlated.py',
   'research/typeii_redistribution_phase_20261116/redistribution.py',
   'research/typeii_cascade_effective_20261116/SOURCE_TRACE_STATIONARY.csv'):
  check(git('hash-object',file)==git('rev-parse',PARENT+':'+file),'parent source drift '+file)
 return True
def main():
 check_source()
 cases=[
 ('H40_128',40.,128,False,False,True),
 ('H40_256',40.,256,False,False,True),
 ('H40_512',40.,512,False,False,True),
 ('H80_256',80.,256,False,False,True),
 ('H80_512',80.,512,False,False,True),
 ('H160_256',160.,256,False,False,True),
 ('H160_512',160.,512,False,False,True),
 ('H240_512',240.,512,False,False,True),
 ('H320_512',320.,512,False,False,True),
 ('H40_FACT_512',40.,512,True,False,True),
 ('H40_RAW_512',40.,512,False,False,False),
 ('H40_FROZEN_512',40.,512,False,True,True)
 ]
 data={'schema':'bass.typeii.hummerRII0.source.scattering_outer.v1',
       'source_parent':PARENT,'parent_locked':True,
       'kernel':'exact classical Hummer II no recoil; thermal sym separate explicit model',
       'source':'Original TypeII H/D/J/kappa/nH/Tm/pion from parent, fixed trace',
       'results':{}}
 dest=HERE/'HUMMER_SOURCE_WING_CASES.json'
 for name,X,n,fac,frozen,thermo in cases:
  begin=time.monotonic()
  res=o.evolve(X=X,steps=n,factorized=fac,frozen=frozen,thermo_sym=thermo,save='HUMMER_'+name)
  check(res['HUMMER_RII0_SOURCE_KERNEL'] is True,'wrong kernel path '+name)
  check(res['frequency_bins']>0 and res['max_number_ledger_defect']<5e-7 and res['max_frozen_midpoint_energy_generator_ledger_defect']<3e-8,'energy or number loss '+name)
  check(abs(sum(res[k] for k in ('survival','red_outer_exit','blue_outer_exit','tagged_ionized'))-1)<5e-7,
        'conserved finite tagged fates '+name)
  res['case']=name;res['runtime_s']=time.monotonic()-begin
  data['results'][name]=res
  dest.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
  print('HUMMER_SOURCE_CASE',name,json.dumps({k:res[k] for k in ('survival','red_outer_exit','blue_outer_exit','tagged_ionized','gross_outer_to_inner_reentries','max_number_ledger_defect','runtime_s')}),flush=True)
if __name__=='__main__':main()
