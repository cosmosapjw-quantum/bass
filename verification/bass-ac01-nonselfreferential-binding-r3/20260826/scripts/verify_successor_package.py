#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path

def main(root: str)->int:
    p=Path(root)
    contract=json.loads((p/'WU-004-R3-NONSELFREFERENTIAL-BINDING.json').read_text())
    correction=json.loads((p/'SPEC_CORRECTION.json').read_text())
    pre=json.loads((p/'PRECOMMIT_RECEIPT.schema.json').read_text())
    post=json.loads((p/'POST_PUSH_BINDING.schema.json').read_text())
    assert contract['id']=='WU-004-R3'
    assert correction['severity']=='P0'
    assert 'final_sha' in pre['not']['anyOf'][0]['required']
    assert 'subject_sha' in post['required']
    assert contract['receipt_policy']['review_target_field']=='post_push_binding.subject_sha'
    assert contract['commit_policy']['implementation']['count_from_base']==1
    assert contract['commit_policy']['attestation']['changed_paths']==['verification/bass-ac-01/20260826/POST_PUSH_BINDING.json']
    manifest=(p/'MANIFEST.sha256').read_text().splitlines()
    declared=set()
    for line in manifest:
        if not line.strip(): continue
        h,name=line.split('  ',1)
        declared.add(name)
        assert hashlib.sha256((p/name).read_bytes()).hexdigest()==h,name
    actual={x.relative_to(p).as_posix() for x in p.rglob('*') if x.is_file() and x.name!='MANIFEST.sha256'}
    assert actual==declared, {'unmanifested':sorted(actual-declared),'missing':sorted(declared-actual)}
    assert not any('__pycache__' in x or x.endswith(('.pyc','.pyo')) for x in actual)
    print('PASS_AC01_NONSELFREFERENTIAL_BINDING_R3_PACKAGE')
    return 0
if __name__=='__main__': raise SystemExit(main(sys.argv[1] if len(sys.argv)>1 else '.'))
