"""Additive raw execution receipts; one thread; hard per-process limits."""
from pathlib import Path
import datetime,hashlib,importlib.metadata,json,math,os,platform,resource,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];RESULTS=ROOT/'results'
ledger_path=RESULTS/'EXECUTION_LEDGER.json'
ledger=json.loads(ledger_path.read_text()) if ledger_path.exists() else {'allocation_wall_s':60.,'allocation_cpu_s':40.,'budget_reset':False,'runs':[]}
wall=sum(r['wall_s'] for r in ledger['runs']);cpu=sum(r['cpu_s'] for r in ledger['runs'])
cpu_limit=min(20,math.floor(40-cpu))
if wall>=60 or cpu_limit<1:raise RuntimeError('implementation scientific allocation exhausted')
argv=[sys.executable,*sys.argv[1:]]
idx=len(ledger['runs'])+1;prefix=RESULTS/f'attempt_{idx:02}'
env=os.environ.copy()
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:env[key]='1'
env['MPLCONFIGDIR']='/tmp/b3c1_mplconfig'
wall_limit=min(30.,60-wall)
def limit():resource.setrlimit(resource.RLIMIT_CPU,(cpu_limit,cpu_limit))
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
receipt=dict(argv=argv,cwd=str(ROOT),start_utc=start,status='STARTED',
    wall_limit_s=wall_limit,cpu_limit_s=cpu_limit,
    stdout=str(prefix.with_suffix('.stdout').relative_to(ROOT)),stderr=str(prefix.with_suffix('.stderr').relative_to(ROOT)),
    environment={k:env[k] for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','MPLCONFIGDIR']},
    packages=dict(python=platform.python_version(),**{p:importlib.metadata.version(p) for p in ['numpy','scipy','matplotlib']},mpmath='PACKAGE_MISSING_NOT_REQUIRED'),
    code_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for d in ['code','tests','vendor'] for p in (ROOT/d).rglob('*.py')})
prefix.with_suffix('.start.json').write_text(json.dumps(receipt,indent=2)+'\n')
t0=time.monotonic();r0=resource.getrusage(resource.RUSAGE_CHILDREN)
try:
    proc=subprocess.run(argv,cwd=ROOT,env=env,capture_output=True,timeout=wall_limit,preexec_fn=limit)
    stdout,stderr,code=proc.stdout,proc.stderr,proc.returncode
except subprocess.TimeoutExpired as e:
    stdout,stderr,code=e.stdout or b'',e.stderr or b'',-999
elapsed=time.monotonic()-t0;r1=resource.getrusage(resource.RUSAGE_CHILDREN)
prefix.with_suffix('.stdout').write_bytes(stdout);prefix.with_suffix('.stderr').write_bytes(stderr)
receipt.update(end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='COMPLETED',
    exit_code=code,wall_s=elapsed,cpu_s=(r1.ru_utime+r1.ru_stime-r0.ru_utime-r0.ru_stime))
ledger['runs'].append(receipt);ledger['total_wall_s']=wall+elapsed;ledger['total_cpu_s']=cpu+receipt['cpu_s']
ledger_path.write_text(json.dumps(ledger,indent=2)+'\n')
print(json.dumps(receipt));sys.exit(0 if code==0 else 1)
