#!/usr/bin/env python3
"""One new source-bound history, raw receipt, then independent admission gates."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

UNIT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(UNIT))
from process_control import run_owned, atomic_json
from assess_history import assess


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binary',type=Path,required=True)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--source-commit',required=True)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    # Attempt directories are assigned by runner.py; refuse a prior raw result.
    if (out/'history.stdout').exists() or (out/'ASSESSMENT.json').exists():
        raise ValueError('HISTORY_JOB_ATTEMPT_ALREADY_USED')
    data=args.input.read_bytes();inp=json.loads(data)
    if inp.get('provenance',{}).get('completed_campaign_replay') is not False:
        raise ValueError('COMPLETED_CAMPAIGN_REPLAY_NOT_ALLOWED')
    digest=hashlib.sha256(data).hexdigest();binary=args.binary.resolve()
    (out/'INPUT.json').write_bytes(data)
    env=os.environ.copy()
    env.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',RAYON_NUM_THREADS='1')
    execution=run_owned([str(binary),'--source-commit',args.source_commit,'--input-sha256',digest,
        '--checkpoint',str(out/'BOUNDARY_CHECKPOINT.json')],stdin_bytes=data,env=env,
        stdout_path=out/'history.stdout',stderr_path=out/'history.stderr',
        receipt_path=out/'PROCESS.json',timeout_s=1700,as_bytes=2*1024**3,file_bytes=64*1024**2)
    result={'schema':'BASS_S12_HISTORY_JOB_V1','status':'FAIL','execution':execution,
        'source_commit':args.source_commit,'input_sha256':digest,
        'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest()}
    try:
        raw=json.loads((out/'history.stdout').read_bytes())
        atomic_json(out/'HISTORY.json',raw)
        evaluation=assess(inp,raw,input_sha256=digest,source_commit=args.source_commit,
            binary_sha256=result['binary_sha256'])
        atomic_json(out/'ASSESSMENT.json',evaluation)
        result['assessment']=evaluation
        # Omission controls are admissible only as complete, structural controls.
        admitted=(evaluation['full_scientific_pass'] if inp['control']=='full'
            else evaluation['execution_completed'] and evaluation['structural_pass'])
        if execution['status']=='EXITED' and execution['exit_code']==0 and admitted:
            result['status']='PASS_FULL' if inp['control']=='full' else 'PASS_CONTROL_RECORD'
    except Exception as e:
        result['error']={'type':type(e).__name__,'message':str(e)}
    atomic_json(out/'RETURN.json',result)
    print(json.dumps({'status':result['status'],'receipt':str(out/'RETURN.json')}))
    return 0 if result['status'].startswith('PASS_') else 1


if __name__=='__main__':raise SystemExit(main())
