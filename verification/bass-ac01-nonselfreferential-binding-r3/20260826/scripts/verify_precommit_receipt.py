#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument('--contract',required=True)
    p.add_argument('--receipt',required=True)
    a=p.parse_args()
    contract=json.loads(Path(a.contract).read_text())
    receipt=json.loads(Path(a.receipt).read_text())
    assert contract['id']=='WU-004-R3'
    assert receipt['schema']=='bass-work-unit-precommit-evidence-v2'
    assert receipt['work_unit_id']=='WU-004-R3'
    assert receipt['base_sha']==contract['authority']['base']['sha']
    assert receipt['target_branch']==contract['authority']['implementation_branch']
    assert receipt['binding_mode']=='separate_post_push_attestation'
    assert 'final_sha' not in receipt
    assert 'attestation_commit_sha' not in receipt
    assert re.fullmatch(r'[0-9a-f]{64}',receipt['contract_sha256'])
    actual=hashlib.sha256(Path(a.contract).read_bytes()).hexdigest()
    assert receipt['contract_sha256']==actual
    for inv in contract['invariants']:
        assert receipt.get('invariants',{}).get(inv) in {'PASS','NOT_APPLICABLE'}
    assert receipt['verdict']=='PASS_PRECOMMIT'
    print('PASS_PRECOMMIT_RECEIPT')
    return 0
if __name__=='__main__': raise SystemExit(main())
