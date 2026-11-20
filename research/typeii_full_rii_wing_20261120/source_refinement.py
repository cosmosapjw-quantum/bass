#!/usr/bin/env python3
"""BASS TypeII source exact Hummer-RII0 finite wing time and angular refinement."""
import json,hashlib
from pathlib import Path
from outer_hummer import evolve
HERE=Path(__file__).resolve().parent
def check(c,m):
 if not bool(c):raise RuntimeError(m)
def main():
 base=json.loads((HERE/'HUMMER_SOURCE_WING_CASES.json').read_text())['results']
 for k in ('H160_512','H320_512','H40_256'):check(k in base,'missing baseline source '+k)
 records={}
 for name,kw in [
  ('H160_1024',dict(X=160.,steps=1024)),
  ('H320_1024',dict(X=320.,steps=1024)),
  ('H40_14ANG_256',dict(X=40.,steps=256,angular_order=14))
 ]:
  r=evolve(**kw,save='HUMMER_'+name)
  check(r['max_number_ledger_defect']<5e-7 and
      abs(sum(r[k] for k in ('survival','red_outer_exit','blue_outer_exit','tagged_ionized'))-1)<5e-7,
      'source count failure '+name)
  records[name]=r
  (HERE/'HUMMER_REFINEMENT_CASES.json').write_text(json.dumps(records,indent=2,sort_keys=True)+'\n')
  print('ADDITIONAL_SOURCE',name,
        {k:r[k] for k in ('survival','red_outer_exit','blue_outer_exit','tagged_ionized',
                         'max_number_ledger_defect','gross_outer_to_inner_reentries')},flush=True)
 paired={
  'X160_source_t512_to1024_ion':records['H160_1024']['tagged_ionized']-base['H160_512']['tagged_ionized'],
  'X320_source_t512_to1024_ion':records['H320_1024']['tagged_ionized']-base['H320_512']['tagged_ionized'],
  'X160_to320_t1024_ion':records['H320_1024']['tagged_ionized']-records['H160_1024']['tagged_ionized'],
  'X160_to320_t1024_survival':records['H320_1024']['survival']-records['H160_1024']['survival'],
  'X40_6to14_sky_t256_ion':records['H40_14ANG_256']['tagged_ionized']-base['H40_256']['tagged_ionized'],
  'X40_6to14_sky_t256_red_exit':records['H40_14ANG_256']['red_outer_exit']-base['H40_256']['red_outer_exit']
 }
 (HERE/'HUMMER_REFINEMENT_PAIRS.json').write_text(json.dumps(paired,indent=2,sort_keys=True)+'\n')
 print('PAIRED_REFINEMENT',json.dumps(paired,sort_keys=True),flush=True)
if __name__=='__main__':main()
