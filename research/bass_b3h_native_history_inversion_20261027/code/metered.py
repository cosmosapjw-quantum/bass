"""Fresh current-unit child guard. No automatic retry and no old budget reset."""
from pathlib import Path
import datetime
import hashlib
import json
import math
import os
import resource
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
COMMANDS={'controls':[sys.executable,'tests/controls.py'], 'result':[sys.executable,'code/result.py'], 'plot':[sys.executable,'code/plot.py']}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def append(path,record):
    with path.open('a') as f:f.write(json.dumps(record,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())
def main():
    stage=sys.argv[1]
    if stage not in COMMANDS:raise ValueError('unknown stage')
    freeze=ROOT/'inputs/EXECUTION_FREEZE.json';f=json.loads(freeze.read_text())
    if f['status']!='READY_FOR_AUTHORIZED_BOUNDED_EXECUTION' or f['commands']!=COMMANDS:raise ValueError('execution freeze not ready or command identity differs')
    ack=json.loads((ROOT/'delivery/S0_ROOT_ACK.json').read_text())
    if not ack['root_authorized_execution'] or not ack['Drive_ACK'] or not ack['Dropbox_ACK']:raise ValueError('root S0 publication/double ACK is not confirmed')
    pre=json.loads((ROOT/f'provenance/PRE_NODE_{stage}.json').read_text())
    if pre['node']!=stage:raise ValueError('current-node live observation absent')
    for row in f['files']:
        if sha(ROOT/row['path'])!=row['sha256']:raise ValueError('frozen byte mismatch '+row['path'])
    path=ROOT/'results/EXECUTION_LEDGER.jsonl';ev=[json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []
    starts=[x for x in ev if x['event']=='STARTED'];done=[x for x in ev if x['event']=='COMPLETED']
    if len(starts)!=len(done) or any(x['returncode'] for x in done):raise ValueError('prior incomplete/failed debit: root interpretation required')
    if [x['stage'] for x in done]!=list(COMMANDS)[:list(COMMANDS).index(stage)]:raise ValueError('one invocation per stage, in order')
    cpu=sum(x['child_cpu_s'] for x in done);wall=sum(x['child_wall_s'] for x in done)
    ac=math.floor(30-cpu);aw=180-wall
    if ac<1 or aw<=0:raise ValueError('current-unit guard exhausted')
    common=dict(stage=stage,command=COMMANDS[stage],freeze_sha256=sha(freeze),requested_model='gpt-6.1-sol',observed_model=None,
      current_limits=dict(cpu_s=30,wall_s=180,target_memory_bytes=536870912,threads=1),
      historical_remaining_cpu_s=None,historical_remaining_wall_s=None,historical_budget_reset=False)
    append(path,dict(**common,event='STARTED',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=sys.version))
    def limits():
        resource.setrlimit(resource.RLIMIT_CPU,(ac,ac))
        resource.setrlimit(resource.RLIMIT_AS,(536870912,536870912))
    before=resource.getrusage(resource.RUSAGE_CHILDREN);wb=resource.getrusage(resource.RUSAGE_SELF);start=time.monotonic()
    with (ROOT/f'results/{stage}.stdout').open('wb') as out,(ROOT/f'results/{stage}.stderr').open('wb') as err:
        try:
            child=subprocess.run(COMMANDS[stage],cwd=ROOT,stdout=out,stderr=err,timeout=aw,preexec_fn=limits,
              env={**os.environ,'PYTHONPATH':f['dependency_path'],'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1','MPLCONFIGDIR':str(ROOT/'results/mplconfig')})
            rc=child.returncode
        except subprocess.TimeoutExpired:rc=124
    after=resource.getrusage(resource.RUSAGE_CHILDREN);wa=resource.getrusage(resource.RUSAGE_SELF)
    child_cpu=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime;child_wall=time.monotonic()-start
    append(path,dict(**common,event='COMPLETED',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),returncode=rc,
      child_cpu_s=child_cpu,child_wall_s=child_wall,cumulative_child_cpu_s=cpu+child_cpu,cumulative_child_wall_s=wall+child_wall,
      child_peak_RSS_kib=after.ru_maxrss,wrapper_cpu_s=wa.ru_utime+wa.ru_stime-wb.ru_utime-wb.ru_stime))
    sys.exit(rc)
if __name__=='__main__':main()
