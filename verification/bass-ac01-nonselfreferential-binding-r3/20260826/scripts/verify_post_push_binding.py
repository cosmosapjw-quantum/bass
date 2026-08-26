#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path

def run(repo,*args):
    return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()

def sha256_bytes(data: bytes)->str:
    return hashlib.sha256(data).hexdigest()

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument('--repo',required=True)
    p.add_argument('--binding',required=True)
    p.add_argument('--implementation-branch',required=True)
    p.add_argument('--attestation-branch',required=True)
    a=p.parse_args()
    repo=Path(a.repo)
    b=json.loads(Path(a.binding).read_text())
    assert b['schema']=='bass-post-push-binding-v1'
    subject=b['subject_sha']
    impl_remote=run(repo,'ls-remote','--heads','origin',a.implementation_branch).split()[0]
    attest_remote=run(repo,'ls-remote','--heads','origin',a.attestation_branch).split()[0]
    assert impl_remote==subject
    run(repo,'fetch','--no-tags','origin',subject,attest_remote)
    assert run(repo,'rev-parse',f'{attest_remote}^')==subject
    assert run(repo,'rev-parse',f'{subject}^')==b['subject_parent']
    assert run(repo,'show','-s','--format=%T',subject)==b['subject_tree']
    assert run(repo,'show','-s','--format=%B',subject).strip()==b['subject_commit_message']
    paths=run(repo,'diff-tree','--no-commit-id','--name-only','-r',attest_remote).splitlines()
    assert paths==['verification/bass-ac-01/20260826/POST_PUSH_BINDING.json']
    receipt=run(repo,'show',f"{subject}:{b['receipt_path']}").encode()
    diff=run(repo,'show',f"{subject}:{b['diff_firewall_path']}").encode()
    assert run(repo,'rev-parse',f"{subject}:{b['receipt_path']}")==b['receipt_blob_sha']
    assert run(repo,'rev-parse',f"{subject}:{b['diff_firewall_path']}")==b['diff_firewall_blob_sha']
    assert sha256_bytes(receipt)==b['receipt_sha256']
    assert sha256_bytes(diff)==b['diff_firewall_sha256']
    parsed=json.loads(receipt)
    assert 'final_sha' not in parsed
    assert b['verdict']=='BOUND_FOR_FRESH_REVIEW'
    print('PASS_POST_PUSH_BINDING')
    print('IMPLEMENTATION_SHA='+subject)
    print('ATTESTATION_SHA='+attest_remote)
    return 0
if __name__=='__main__': raise SystemExit(main())
