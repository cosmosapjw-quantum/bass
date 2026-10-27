"""Frozen command runner; STARTED survives interruption; no automatic retry."""
from pathlib import Path
import datetime,hashlib,importlib.metadata,json,os,resource,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
COMMANDS={'tests':[sys.executable,'-m','unittest','discover','-s','tests','-v'],'consume':[sys.executable,'code/consume.py'],'plot':[sys.executable,'code/plot.py']}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 wrapper_start=resource.getrusage(resource.RUSAGE_SELF);stage=sys.argv[1];cmd=COMMANDS[stage]
 frozen=json.loads((ROOT/'provenance/EXECUTION_FREEZE.json').read_text())
 if frozen['commands']!=COMMANDS:raise RuntimeError('command identity mismatch')
 for row in frozen['files']:
  if sha(ROOT/row['path'])!=row['sha256']:raise RuntimeError('frozen source identity mismatch '+row['path'])
 inputs=ROOT/'provenance/SELECTED_INPUTS.json'
 if sha(inputs)!=frozen['input_manifest_sha256']:raise RuntimeError('input manifest identity mismatch')
 for row in json.loads(inputs.read_text())['files']:
  if sha(Path(row['path']))!=row['sha256']:raise RuntimeError('input identity mismatch '+row['path'])
 path=ROOT/'results/EXECUTION_LEDGER.json'
 ledger=json.loads(path.read_text()) if path.exists() else dict(prior_known_cpu=3.7263,prior_known_wall=3.739223223001318,historical_remaining_cpu=None,historical_remaining_wall=None,historical_budget_reset=False,prior_ledgers=['../bass_b3g_actual_cohort_binding_20261025/results/EXECUTION_LEDGER.json','../bass_b3g_actual_cohort_binding_20261025/provenance/HISTORICAL_B3F_EXECUTION_LEDGER.json'],attempts=[],allocation_cpu=20,allocation_wall=60,metadata_io_cost='UNKNOWN_EXCLUDED',requested_model='gpt6.1sol',observed_model=None)
 if any(x.get('state')!='COMPLETED' for x in ledger['attempts']):raise RuntimeError('incomplete attempt has unknown debit; rerun blocked')
 if any(x['stage']==stage for x in ledger['attempts']):raise RuntimeError('no automatic retry')
 if [x['stage'] for x in ledger['attempts']]!=list(COMMANDS)[:list(COMMANDS).index(stage)]:raise RuntimeError('frozen stage order')
 if any(x['returncode']!=0 for x in ledger['attempts']):raise RuntimeError('prior failure requires root repair authorization')
 cpu=sum(x['cpu'] for x in ledger['attempts']);wall=sum(x['wall'] for x in ledger['attempts'])
 if cpu>=20 or wall>=60:raise RuntimeError('budget exhausted')
 attempt=dict(stage=stage,state='STARTED',command=cmd,cwd=str(ROOT),started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),code_freeze_sha256=sha(ROOT/'provenance/EXECUTION_FREEZE.json'),input_manifest_sha256=sha(inputs),cpu=None,wall=None,returncode=None,unknown_debit_blocks_rerun=True,versions={name:importlib.metadata.version(name) for name in ['numpy','scipy','matplotlib']},python=sys.version)
 ledger['attempts'].append(attempt);path.write_text(json.dumps(ledger,indent=2)+'\n')
 def limits():resource.setrlimit(resource.RLIMIT_CPU,(max(1,int(min(10,20-cpu))),max(1,int(min(10,20-cpu)))))
 before=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.monotonic()
 with (ROOT/f'results/{stage}.stdout').open('wb') as out,(ROOT/f'results/{stage}.stderr').open('wb') as err:
  try:r=subprocess.run(cmd,cwd=ROOT,stdout=out,stderr=err,timeout=min(20,60-wall),preexec_fn=limits,env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'});rc=r.returncode
  except subprocess.TimeoutExpired:rc=124
 after=resource.getrusage(resource.RUSAGE_CHILDREN);wrapper_end=resource.getrusage(resource.RUSAGE_SELF)
 attempt.update(state='COMPLETED',cpu=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,wall=time.monotonic()-start,returncode=rc,wrapper_cpu_measured=wrapper_end.ru_utime+wrapper_end.ru_stime-wrapper_start.ru_utime-wrapper_start.ru_stime)
 path.write_text(json.dumps(ledger,indent=2)+'\n');sys.exit(rc)
if __name__=='__main__':main()
