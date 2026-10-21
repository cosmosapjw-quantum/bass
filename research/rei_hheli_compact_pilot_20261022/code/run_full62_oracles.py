#!/usr/bin/env python3
"""Two prescribed full62 comparison cases; sequential, never runs compact cases."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
for variable in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[variable]='1'
sys.path.insert(0,str(ROOT/'vendor/rec_hheli/code'))
# Pin runner import to this lane; donor path is retained for unchanged coupled.
sys.path.insert(0,str(ROOT/'code'))
from run_pilot import freeze,canonical,resource_budget,execute_one,atomic_json,owner
# Output compatibility only; all vendored dynamics, gates and source bytes stay original.
import coupled
from compact_run import atomic_json as scalar_metadata_atomic_json
coupled.atomic_json=scalar_metadata_atomic_json

CASES=('s04_m04_r04','cancel_positive_matter')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true')
    parser.add_argument('--output',type=Path,default=ROOT/'results/full62_oracles')
    args=parser.parse_args()
    frozen=freeze(ROOT,ROOT/'data/CAMPAIGN.json')
    compact_base=frozen['base_identity']
    frozen['base_identity']=hashlib.sha256(canonical({'compact_source_base':compact_base,'implementation':'unchanged_donor_full62'})).hexdigest()
    configs=[next(c for c in frozen['configs'] if c['case_id']==name) for name in CASES]
    resources=resource_budget([ROOT/'results/.reservations'],requested='1',cap=1)
    summary={'mode':'execute' if args.execute else 'plan','cases':list(CASES),'implementation':'unchanged_donor_full62',
             'compact_source_base':compact_base,'full62_base':frozen['base_identity'],'resources':resources}
    if not args.execute:
        print(json.dumps(summary,indent=2));return 0
    args.output.mkdir(parents=True,exist_ok=True)
    if not resources['workers']:
        summary['status']='resource_deferred';atomic_json(args.output/'RESOURCE_DEFERRED.json',summary)
        print(json.dumps(summary,indent=2));return 3
    # Original completion/claim logic preserves all prior cases without retry.
    summary['records']=[execute_one(str(ROOT),str(args.output),frozen,c,module='coupled') for c in configs]
    summary['status']='COMPLETE' if all(r['status'] in ('completed','complete_reused') for r in summary['records']) else 'PRESERVED_FAILURE'
    atomic_json(args.output/('ORACLE_RUN_'+owner()['token']+'.json'),summary)
    print(json.dumps(summary,indent=2));return 0 if summary['status']=='COMPLETE' else 2

if __name__=='__main__':raise SystemExit(main())
