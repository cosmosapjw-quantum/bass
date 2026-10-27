"""One metered invocation per separately authorized phase; no automatic replay.

The same ledger debits Phase A, a future root-frozen Phase B and saved-only plot.
Old closed allocations are not transferred or reopened. Preparation not metered
here remains unknown, not zero.
"""
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
COMMANDS={'phase_b':[sys.executable,'code/phase_b.py']}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def append(path,row):
    with path.open('a') as f:f.write(json.dumps(row,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())
def main():
    stage=sys.argv[1]
    if stage not in COMMANDS:raise ValueError('unfrozen phase; return to root')
    freeze_path=ROOT/'inputs/EXECUTION_FREEZE_PHASE_B.json';freeze=json.loads(freeze_path.read_text())
    if freeze['status']!='READY_FOR_AUTHORIZED_PHASE_B' or freeze['commands']!=COMMANDS:raise ValueError('execution freeze not ready')
    ack=json.loads((ROOT/'delivery/PHASE_B_ROOT_ACK.json').read_text())
    if not all(ack.get(k) for k in ['root_authorized_phase_b','actual_source_commit','Drive_ACK','Dropbox_ACK']):raise ValueError('actual S1A checkpoint/root Phase B signal required')
    pre=json.loads((ROOT/'provenance/PRE_NODE_phase_b.json').read_text())
    if pre['node']!=stage or not pre.get('actual_readback'):raise ValueError('actual current pre-node HEAD/AGENTS/parallel observation required')
    for row in freeze['files']:
        if sha(ROOT/row['path'])!=row['sha256']:raise ValueError('frozen byte mismatch '+row['path'])
    OUT=ROOT/'results';OUT.mkdir(exist_ok=True);ledger=OUT/'EXECUTION_LEDGER.jsonl'
    events=[json.loads(x) for x in ledger.read_text().splitlines()] if ledger.exists() else []
    started=[x for x in events if x['event']=='STARTED'];done=[x for x in events if x['event']=='COMPLETED']
    if len(started)!=len(done) or any(x['returncode'] for x in done):raise ValueError('incomplete/failed prior debit requires root interpretation')
    if any(x['stage']==stage for x in started):raise ValueError('one Phase B invocation only; replay requires separate root repair authorization')
    cpu=sum(x['child_cpu_s'] for x in done);wall=sum(x['child_wall_s'] for x in done)
    remain_cpu=math.floor(60-cpu);remain_wall=180-wall
    if remain_cpu<1 or remain_wall<=0:raise ValueError('new combined allocation exhausted')
    common=dict(stage=stage,command=COMMANDS[stage],freeze_sha256=sha(freeze_path),requested_model='gpt-6.1-sol',observed_runtime_model=None,
      aggregate_limits=dict(child_CPU_s=60,child_wall_s=180,memory_bytes=805306368,BLAS_OpenMP_threads=1),
      historical_remaining_cpu_s=None,historical_remaining_wall_s=None,old_allocation_reopened=False,
      environment={k:'1' for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','PYTHONDONTWRITEBYTECODE']})
    append(ledger,dict(**common,event='STARTED',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=sys.version))
    def limits():
        resource.setrlimit(resource.RLIMIT_CPU,(remain_cpu,remain_cpu));resource.setrlimit(resource.RLIMIT_AS,(805306368,805306368))
    before=resource.getrusage(resource.RUSAGE_CHILDREN);wb=resource.getrusage(resource.RUSAGE_SELF);start=time.monotonic()
    env={**os.environ,**common['environment'],'PYTHONPATH':freeze['dependency_path']}
    with (OUT/f'{stage}.stdout').open('wb') as stdout,(OUT/f'{stage}.stderr').open('wb') as stderr:
        try:
            child=subprocess.run(COMMANDS[stage],cwd=ROOT,stdout=stdout,stderr=stderr,env=env,timeout=remain_wall,preexec_fn=limits);rc=child.returncode
        except subprocess.TimeoutExpired:rc=124
    after=resource.getrusage(resource.RUSAGE_CHILDREN);wa=resource.getrusage(resource.RUSAGE_SELF)
    child_cpu=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime;child_wall=time.monotonic()-start
    append(ledger,dict(**common,event='COMPLETED',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),returncode=rc,
      child_cpu_s=child_cpu,child_wall_s=child_wall,cumulative_child_cpu_s=cpu+child_cpu,cumulative_child_wall_s=wall+child_wall,
      child_peak_RSS_KiB=after.ru_maxrss,wrapper_cpu_s=wa.ru_utime+wa.ru_stime-wb.ru_utime-wb.ru_stime,
      remaining_new_cpu_s=60-cpu-child_cpu,remaining_new_wall_s=180-wall-child_wall))
    sys.exit(rc)
if __name__=='__main__':main()
