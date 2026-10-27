"""Selected-unit guard; append-only events, independent known/unknown history."""
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
COMMANDS={'tests':[sys.executable,'-m','unittest','discover','-s','tests','-v'],
          'tests_env_repair':[sys.executable,'-m','unittest','discover','-s','tests','-v'],
          'consume':[sys.executable,'code/consume.py'], 'plot':[sys.executable,'code/plot.py']}


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def append(path,event):
    with path.open('a') as f:
        f.write(json.dumps(event,allow_nan=False)+'\n'); f.flush(); os.fsync(f.fileno())


def main():
    wrapper_before=resource.getrusage(resource.RUSAGE_SELF)
    stage=sys.argv[1]
    if stage not in COMMANDS: raise ValueError('unknown selected stage')
    freeze_path=ROOT/'inputs/EXECUTION_FREEZE.json'
    frozen=json.loads(freeze_path.read_text())
    if frozen['commands'] != COMMANDS: raise ValueError('command identity mismatch')
    for row in frozen['files']:
        if sha(ROOT/row['path'])!=row['sha256']: raise ValueError('frozen byte identity mismatch: '+row['path'])
    for row in frozen['source_files']:
        if sha(Path(row['path']))!=row['sha256']: raise ValueError('source byte identity mismatch: '+row['path'])
    ledger_path=ROOT/'results/EXECUTION_LEDGER.jsonl'
    events=[json.loads(x) for x in ledger_path.read_text().splitlines()] if ledger_path.exists() else []
    started=[x for x in events if x['event']=='STARTED']; completed=[x for x in events if x['event']=='COMPLETED']
    if len(started)!=len(completed): raise RuntimeError('unknown incomplete debit; retry blocked')
    if any(x['stage']==stage for x in started): raise RuntimeError('no automatic retry')
    repair=json.loads((ROOT/'inputs/ENVIRONMENT_REPAIR.json').read_text())
    prior_exact_package_failure=(len(completed)>=1 and completed[0]['stage']=='tests' and completed[0]['returncode']==1
        and completed[0]['freeze_sha256']==repair['prior_failed_freeze_sha256']
        and sha(ROOT/'results/tests_PACKAGE_MISSING.stderr')==repair['prior_failed_stderr_sha256']
        and repair['exception'] in (ROOT/'results/tests_PACKAGE_MISSING.stderr').read_text())
    failed=[x for x in completed if x['returncode']!=0]
    if failed and not (prior_exact_package_failure and len(failed)==1 and failed[0] is completed[0]):
        raise RuntimeError('failure not the one authorized PACKAGE_MISSING repair')
    if stage=='tests_env_repair' and not (prior_exact_package_failure and len(completed)==1):
        raise RuntimeError('environment repair stage requires exact first PACKAGE_MISSING attempt')
    if stage in ['consume','plot'] and not any(x['stage']=='tests_env_repair' and x['returncode']==0 for x in completed):
        raise RuntimeError('environment repair tests have not passed')
    if [x['stage'] for x in completed]!=list(COMMANDS)[:list(COMMANDS).index(stage)]: raise RuntimeError('stage order mismatch')
    cpu=sum(x['child_cpu_s'] for x in completed); wall=sum(x['child_wall_s'] for x in completed)
    allowance_cpu=math.floor(min(5.,10.-cpu)); allowance_wall=min(10.,30.-wall)
    if allowance_cpu<1 or allowance_wall<=0: raise RuntimeError('new selected-unit guard exhausted')
    common=dict(stage=stage,command=COMMANDS[stage],freeze_sha256=sha(freeze_path),
       requested_implementation_model='gpt-6.1-sol',observed_runtime_model=None,
       historical_prior_known_child_cpu_s=10.904214,historical_prior_known_child_wall_s=10.985060912003973,
       historical_midpoint_wrapper_cpu_s=0.130123,historical_other_overhead_s=None,
       historical_remaining_cpu_s=None,historical_remaining_wall_s=None,historical_budget_reset=False,
       new_selected_unit_limits=dict(aggregate_child_cpu_s=10,aggregate_child_wall_s=30,each_child_cpu_s=5,each_child_wall_s=10),
       current_child_allowance=dict(cpu_s=allowance_cpu,wall_s=allowance_wall),
       environment_repair=repair,preserved_failed_attempt_superseded_only_by='tests_env_repair PASS')
    append(ledger_path,dict(**common,event='STARTED',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=sys.version))
    def limit(): resource.setrlimit(resource.RLIMIT_CPU,(allowance_cpu,allowance_cpu))
    before=resource.getrusage(resource.RUSAGE_CHILDREN); start=time.monotonic()
    with (ROOT/f'results/{stage}.stdout').open('wb') as out,(ROOT/f'results/{stage}.stderr').open('wb') as err:
        try:
            child=subprocess.run(COMMANDS[stage],cwd=ROOT,stdout=out,stderr=err,timeout=allowance_wall,preexec_fn=limit,
                env={**os.environ,'PYTHONPATH':repair['dependency_location'],'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1','MPLCONFIGDIR':str(ROOT/'results/mplconfig')})
            rc=child.returncode
        except subprocess.TimeoutExpired: rc=124
    after=resource.getrusage(resource.RUSAGE_CHILDREN); wrapper_after=resource.getrusage(resource.RUSAGE_SELF)
    child_cpu=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime
    child_wall=time.monotonic()-start
    append(ledger_path,dict(**common,event='COMPLETED',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
       child_cpu_s=child_cpu,child_wall_s=child_wall,returncode=rc,
       cumulative_child_cpu_s=cpu+child_cpu,cumulative_child_wall_s=wall+child_wall,
       wrapper_cpu_s=wrapper_after.ru_utime+wrapper_after.ru_stime-wrapper_before.ru_utime-wrapper_before.ru_stime))
    sys.exit(rc)


if __name__=='__main__': main()
