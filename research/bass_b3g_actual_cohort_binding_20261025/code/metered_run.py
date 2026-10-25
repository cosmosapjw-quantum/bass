"""One frozen test/consumer/plot sequence, additive budgets, no automatic replay."""
from pathlib import Path
import datetime
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import resource
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/'results'


def save(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def main():
    frozen=json.loads((ROOT/'provenance/FROZEN_COMMANDS.json').read_text())
    command=sys.argv[1:]
    RESULTS.mkdir(exist_ok=True)
    path=RESULTS/'EXECUTION_LEDGER.json'
    ledger=json.loads(path.read_text()) if path.exists() else dict(
        schema='B3G_ADDITIVE_EXECUTION_LEDGER_V1',allocation_wall_s=60.,allocation_cpu_s=40.,
        cumulative_guard_wall_s=120.,cumulative_guard_cpu_s=60.,per_child_wall_s=30.,per_child_cpu_s=20.,
        historical_remaining_wall_s=None,historical_remaining_cpu_s=None,budget_reset=False,
        historical_debits_preserved_in=['provenance/HISTORICAL_B3F_EXECUTION_LEDGER.json','inputs/b3c/RESOURCE_LEDGER.json'],
        historical_failures_and_unknown_no_ack='UNCHANGED_OWNER_RECEIPTS_NOT_RETRIED',
        model_identity=dict(requested='gpt-6.1-sol',observed=None,observation_status='NO_MODEL_IDENTITY_TOOL_PROVIDED'),
        runs=[])
    runs=ledger['runs']
    if any(r['status']!='COMPLETED' for r in runs):raise RuntimeError('prior failed/unacknowledged attempt: root adjudication required, no automatic replay')
    if len(runs)>=len(frozen['commands']) or command!=frozen['commands'][len(runs)]:raise RuntimeError('command/order differs from frozen one-test/one-consumer/one-plot sequence')
    for rel,sha in frozen['code_sha256'].items():
        if hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()!=sha:raise RuntimeError('frozen code byte mismatch: '+rel)
    wall=sum(r['wall_s'] for r in runs);cpu=sum(r['cpu_s'] for r in runs)
    wall_limit=min(30.,60.-wall,120.-wall);cpu_limit=min(20,math.floor(40.-cpu),math.floor(60.-cpu))
    if wall_limit<=0 or cpu_limit<1:raise RuntimeError('cumulative task allocation exhausted')
    env=os.environ.copy()
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:env[key]='1'
    env['MPLCONFIGDIR']='/tmp/b3g_mplconfig'
    idx=len(runs)+1;prefix=RESULTS/f'attempt_{idx:02}'
    receipt=dict(argv=[sys.executable,*command],cwd=str(ROOT),status='STARTED',
        start_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),wall_limit_s=wall_limit,cpu_limit_s=cpu_limit,
        stdout=prefix.with_suffix('.stdout').name,stderr=prefix.with_suffix('.stderr').name,
        code_sha256=frozen['code_sha256'],
        input_manifest_sha256=hashlib.sha256((ROOT/'inputs/MANIFEST.json').read_bytes()).hexdigest(),
        dependency_versions=dict(python=platform.python_version(),**{p:importlib.metadata.version(p) for p in ['numpy','scipy','matplotlib']}),
        runtime_identity=dict(executable=sys.executable,platform=platform.platform(),machine=platform.machine(),model_observed=None))
    runs.append(receipt);save(path,ledger);save(prefix.with_suffix('.start.json'),receipt)
    def limit():resource.setrlimit(resource.RLIMIT_CPU,(cpu_limit,cpu_limit))
    t0=time.monotonic();r0=resource.getrusage(resource.RUSAGE_CHILDREN)
    try:
        proc=subprocess.run(receipt['argv'],cwd=ROOT,env=env,capture_output=True,timeout=wall_limit,preexec_fn=limit)
        stdout,stderr,code=proc.stdout,proc.stderr,proc.returncode
    except subprocess.TimeoutExpired as exc:
        stdout,stderr,code=exc.stdout or b'',exc.stderr or b'',-999
    elapsed=time.monotonic()-t0;r1=resource.getrusage(resource.RUSAGE_CHILDREN)
    prefix.with_suffix('.stdout').write_bytes(stdout);prefix.with_suffix('.stderr').write_bytes(stderr)
    child_cpu=r1.ru_utime+r1.ru_stime-r0.ru_utime-r0.ru_stime
    receipt.update(status='COMPLETED' if code==0 else 'FAILED',exit_code=code,wall_s=elapsed,cpu_s=child_cpu,
        end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    ledger.update(total_wall_s=wall+elapsed,total_cpu_s=cpu+child_cpu)
    save(path,ledger)
    print(json.dumps(dict(status=receipt['status'],exit_code=code,wall_s=elapsed,cpu_s=child_cpu,
        cumulative_wall_s=ledger['total_wall_s'],cumulative_cpu_s=ledger['total_cpu_s'])))
    sys.exit(0 if code==0 else 1)


if __name__=='__main__':main()
