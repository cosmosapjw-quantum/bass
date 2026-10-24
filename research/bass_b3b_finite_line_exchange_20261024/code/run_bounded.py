"""Execute one scientific command with an enforced 30s subprocess ceiling.

Every attempted command retains argv/cwd/stdout/stderr/exit/wall/CPU. Cumulative
implementation science wall is bounded at 60s; historical budgets stay null.
"""
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/'results'
LEDGER=RESULTS/'EXECUTION_LEDGER.json'


def main():
    argv=sys.argv[1:]
    if not argv:raise SystemExit('supply executable and arguments')
    RESULTS.mkdir(exist_ok=True)
    data=json.loads(LEDGER.read_text()) if LEDGER.exists() else dict(
        unit='BASS_B3B_FINITE_LINE_EXCHANGE_20261024', implementation_wall_ceiling_s=60.,
        per_process_wall_ceiling_s=30., remaining_campaign_wall_seconds=None,
        remaining_campaign_cpu_seconds=None,budget_reset=False,
        old_B3a_wall_seconds=6.3684287650103215,old_B3a_cpu_seconds=6.359076642999999,
        historical_partial_wall_subtotal_s=34.1262904040002,
        orchestration_backup_wall_seconds=None,commands=[])
    spent=sum(row['wall_seconds'] for row in data['commands'])
    allowance=min(30.,60.-spent)
    if allowance<=0:raise SystemExit('implementation science allocation exhausted')
    index=len(data['commands'])+1
    outpath=RESULTS/f'COMMAND_{index:02d}.stdout.txt'
    errpath=RESULTS/f'COMMAND_{index:02d}.stderr.txt'
    before=resource.getrusage(resource.RUSAGE_CHILDREN)
    start=time.perf_counter();timed_out=False
    env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',
             MPLBACKEND='Agg',MPLCONFIGDIR='/tmp/bass_b3b_matplotlib',PYTHONDONTWRITEBYTECODE='1')
    with outpath.open('w') as stdout,errpath.open('w') as stderr:
        process=subprocess.Popen(argv,cwd=ROOT,stdout=stdout,stderr=stderr,env=env)
        try:exit_code=process.wait(timeout=allowance)
        except subprocess.TimeoutExpired:
            timed_out=True;process.kill();process.wait();exit_code=124
    wall=time.perf_counter()-start;after=resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu=(after.ru_utime+after.ru_stime)-(before.ru_utime+before.ru_stime)
    row=dict(command_index=index,argv=argv,cwd=str(ROOT),exit_code=exit_code,
             timed_out=timed_out,timeout_seconds=allowance,wall_seconds=wall,cpu_seconds=cpu,
             stdout=str(outpath.relative_to(ROOT)),stderr=str(errpath.relative_to(ROOT)))
    data['commands'].append(row)
    data['implementation_science_wall_seconds']=spent+wall
    data['implementation_science_cpu_seconds']=sum(x['cpu_seconds'] for x in data['commands'])
    LEDGER.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(row,indent=2))
    print(outpath.read_text());print(errpath.read_text(),file=sys.stderr)
    return exit_code


if __name__=='__main__':raise SystemExit(main())
