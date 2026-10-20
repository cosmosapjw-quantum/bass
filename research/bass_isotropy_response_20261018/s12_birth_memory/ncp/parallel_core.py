#!/usr/bin/env python3
"""Case-parallel frozen S12 core batches; each child's reductions stay serial.

Run this wrapper as an owned group through runner.py/process_control.py. Core
children share that group, use no shell/preexec/daemon, and create no children.
All raw process inputs/outputs survive. This measures whole-batch wall time,
including process and file costs, separately from the inner core timing.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
import threading
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from process_control import atomic_json


def sha(data):return hashlib.sha256(data).hexdigest()


def validate_scientific_output(raw):
    lines=raw.decode().splitlines()
    if lines[:3]!=['BASS_S12_CORE_OUTPUT_V1','MODE fused','ROWS 24']:raise ValueError('SCIENCE_HEADER')
    cursor=3
    for i in range(24):
        if cursor>=len(lines) or lines[cursor]!=f'ROW {i}':raise ValueError('SCIENCE_ROW_ORDER')
        cursor+=1
        for name,count in [('RHS',6),('JVP',6),('PT',6),('JAC',36),('MOMENTS',10)]:
            if cursor>=len(lines):raise ValueError('SCIENCE_TRUNCATION')
            fields=lines[cursor].split();cursor+=1
            if fields[0]!=name or len(fields)!=count+1:raise ValueError('SCIENCE_FIELD_SHAPE')
            if not all(math.isfinite(float(v)) for v in fields[1:]):raise ValueError('SCIENCE_NONFINITE')
    if cursor!=len(lines):raise ValueError('SCIENCE_TRAILING_OUTPUT')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binary',type=Path,required=True);p.add_argument('--cases',type=Path,required=True)
    p.add_argument('--source-commit',required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--workers',type=int,required=True)
    p.add_argument('--profile',choices=['sandbox','ncp'],required=True)
    args=p.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    profile={'sandbox':(4,128,1,3,16),'ncp':(64,1024,2,7,64)}[args.profile]
    count,repeat,warmups,samples,limit=profile
    if not 1<=args.workers<=min(limit,len(os.sched_getaffinity(0))):raise ValueError('WORKER_AFFINITY_CAP')
    if args.profile=='sandbox' and args.workers!=2:raise ValueError('PREREGISTERED_SANDBOX_WIDTH_TWO')
    manifest=json.loads(args.cases.read_bytes());data=[]
    for row in manifest['cases'][:count]:
        relative=Path(row['path'])
        if relative.is_absolute() or '..' in relative.parts:raise ValueError('CASE_PATH')
        raw=(args.cases.parent/relative).read_bytes()
        if sha(raw)!=row['sha256']:raise ValueError('CASE_SHA256')
        data.append(raw)
    if len(data)!=count:raise ValueError('CASE_CARDINALITY')
    binary=args.binary.resolve();binary_digest=sha(binary.read_bytes())
    env=os.environ.copy();env.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',RAYON_NUM_THREADS='1')
    expected={};pairs=[];error=None;started=dt.datetime.now(dt.timezone.utc).isoformat()
    lock=threading.Lock();active=0;peak=0
    def one(item):
        nonlocal active,peak
        tag,i=item;directory=out/tag/f'case{i:02d}';directory.mkdir(parents=True,exist_ok=False)
        (directory/'input.txt').write_bytes(data[i]);t=time.monotonic()
        record={'case':i,'input_sha256':sha(data[i]),'binary_sha256':binary_digest,
            'argv':[str(binary),'--mode','fused','--repeat',str(repeat)],'status':'STARTING'}
        atomic_json(directory/'PROCESS.json',record)
        with lock:active+=1;peak=max(peak,active)
        try:
            with (directory/'stdout.txt').open('wb') as stdout,(directory/'stderr.json').open('wb') as stderr:
                process=subprocess.run(record['argv'],input=data[i],stdout=stdout,stderr=stderr,
                    env=env,timeout=120,start_new_session=False)
            record.update(exit_code=process.returncode,status='EXITED')
            if process.returncode:raise RuntimeError('CORE_CHILD_FAILED')
            raw=(directory/'stdout.txt').read_bytes();timing=json.loads((directory/'stderr.json').read_bytes())
            validate_scientific_output(raw)
            if timing['repeat']!=repeat or timing['timed_evaluations']!=repeat*24:raise ValueError('TIMED_WORKLOAD')
            record.update(stdout_sha256=sha(raw),stderr_sha256=sha((directory/'stderr.json').read_bytes()),inner_timing=timing)
            return i,raw,record
        except Exception as exc:
            record.update(status='FAILED',error={'type':type(exc).__name__,'message':str(exc)})
            raise
        finally:
            with lock:active-=1
            record['elapsed_s']=time.monotonic()-t;atomic_json(directory/'PROCESS.json',record)
    try:
        for pair in range(warmups+samples):
            order=['serial','parallel'] if pair%2==0 else ['parallel','serial']
            row={'pair':pair,'warmup':pair<warmups,'order':order}
            for arm in order:
                peak=0;t=time.monotonic();tag=f'pair{pair:02d}_{arm}'
                tasks=[(tag,i) for i in range(count)]
                if arm=='serial':result=[one(item) for item in tasks]
                else:
                    with ThreadPoolExecutor(max_workers=args.workers) as pool:result=list(pool.map(one,tasks))
                elapsed=time.monotonic()-t
                for i,raw,execution in result:
                    if i not in expected:expected[i]=raw
                    elif raw!=expected[i]:raise ValueError('SERIAL_PARALLEL_SCIENTIFIC_BYTES_CHANGED')
                row[arm]={'wall_s':elapsed,'workers':1 if arm=='serial' else args.workers,
                    'observed_peak_case_workers':peak,'scientific_identity_count':len(result)}
            row['speedup']=row['serial']['wall_s']/row['parallel']['wall_s'];pairs.append(row)
            atomic_json(out/'PAIRS.json',pairs)
        if sha(binary.read_bytes())!=binary_digest:raise ValueError('BINARY_CHANGED')
    except Exception as exc:error={'type':type(exc).__name__,'message':str(exc)}
    ratios=[x['speedup'] for x in pairs if not x['warmup']]
    ordered=sorted(ratios)
    def percentile(q):
        index=(len(ordered)-1)*q;lo=int(index);hi=min(lo+1,len(ordered)-1)
        return ordered[lo]*(1-(index-lo))+ordered[hi]*(index-lo)
    result={'schema':'BASS_S12_CASE_PARALLEL_V1','status':'PASS_EXECUTION_IDENTITY' if error is None else 'FAIL',
        'source_commit':args.source_commit,'binary_sha256':binary_digest,'cases_manifest_sha256':sha(args.cases.read_bytes()),
        'profile':args.profile,'requested_workers':args.workers,'cases':count,'repeat':repeat,
        'warmup_pairs':warmups,'measured_pairs':len(ratios),'pairs':pairs,
        'speedup_median':statistics.median(ratios) if ratios else None,
        'speedup_q25':percentile(.25) if ratios else None,'speedup_q75':percentile(.75) if ratios else None,
        'scientific_identity':'Full stdout bytes across every serial/parallel timing repeat',
        'ray_cohort_reduction_order_changed':False,'completed_campaign_replays':0,
        'started_utc':started,'ended_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'error':error,
        'scope':'New fixed whole-core batches; not native spectral/history convergence; not a comparison with old NCP64 results'}
    atomic_json(out/'RETURN.json',result)
    print(json.dumps({k:result[k] for k in ['status','cases','requested_workers','speedup_median','error']}))
    return 0 if error is None else 1


if __name__=='__main__':raise SystemExit(main())
