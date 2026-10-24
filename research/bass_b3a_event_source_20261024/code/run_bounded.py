"""Measure each new validation process including failures. Upper limits only."""
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'
OUT.mkdir(exist_ok=True)
RECEIPT=OUT/'VALIDATION_RECEIPT.json'
receipt=json.loads(RECEIPT.read_text()) if RECEIPT.exists() else {
 'unit':'BASS_B3A_REC_EVENT_ADAPTER_20261024','imported_preparatory_unit':'BASS_B3A_EVENT_SOURCE_20261024',
 'historical_remaining_wall_s':None,'historical_remaining_cpu_s':None,'budget_reset':False,
 'new_local_combined_wall_upper_limit_s':60.,'per_scientific_subprocess_upper_limit_s':30.,
 'requested_model':'gpt-6.1-sol','observed_runtime_model':'not inferable from tool/process evidence',
 'actual_executor':'delegated agent b3a_implementation via functions.exec exec_command; python3 subprocesses',
 'records':[]}
commands={'repair_targeted':[sys.executable,'-m','unittest','discover','-s','tests','-p','test_repairs.py','-v'],
          'tests':[sys.executable,'-m','unittest','discover','-s','tests','-p','test_*.py','-v'],
          'reference_plot':[sys.executable,'code/reference_runner.py']}
key=sys.argv[1]
used=sum(r['wall_s'] for r in receipt['records'])
remaining=60.-used
if remaining <= 0:raise SystemExit('New scoped validation wall ceiling exhausted')
cmd=commands[key]
env=os.environ.copy();env['MPLCONFIGDIR']='/tmp/bass_b3a_rec_event_adapter_mpl';env['OPENBLAS_NUM_THREADS']='1';env['OMP_NUM_THREADS']='1'
before=resource.getrusage(resource.RUSAGE_CHILDREN)
t0=time.perf_counter();timeout=False
try:
 result=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True,timeout=min(30.,remaining))
 code=result.returncode;stdout=result.stdout;stderr=result.stderr
except subprocess.TimeoutExpired as exc:
 timeout=True;code=124
 stdout=exc.stdout or '';stderr=exc.stderr or ''
 if isinstance(stdout,bytes):stdout=stdout.decode(errors='replace')
 if isinstance(stderr,bytes):stderr=stderr.decode(errors='replace')
wall=time.perf_counter()-t0
after=resource.getrusage(resource.RUSAGE_CHILDREN)
index=len(receipt['records'])+1
log=f'{index:02d}_{key}.log'
(OUT/log).write_text('STDOUT\n'+stdout+'\nSTDERR\n'+stderr)
record={'argv':cmd,'cwd':str(ROOT),'env_overrides':{k:env[k] for k in ['MPLCONFIGDIR','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS']},
 'exit_code':code,'timeout':timeout,'wall_s':wall,'user_cpu_s':after.ru_utime-before.ru_utime,
 'system_cpu_s':after.ru_stime-before.ru_stime,'cpu_s':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
 'stdout':stdout,'stderr':stderr,'raw_log':log,'process_identity':{'executable':sys.executable,'harness_pid':os.getpid()},
 'classification':'new source-bound adapter validation; no IVP, no historical replay'}
receipt['records'].append(record)
receipt['new_validation_wall_s']=sum(r['wall_s'] for r in receipt['records'])
receipt['new_validation_cpu_s']=sum(r['cpu_s'] for r in receipt['records'])
receipt['within_new_wall_ceiling']=receipt['new_validation_wall_s']<=60.
RECEIPT.write_text(json.dumps(receipt,indent=2)+'\n')
print(stdout,end='');print(stderr,end='',file=sys.stderr)
print(json.dumps({k:record[k] for k in ['exit_code','wall_s','user_cpu_s','system_cpu_s','cpu_s','raw_log']}))
raise SystemExit(code)
