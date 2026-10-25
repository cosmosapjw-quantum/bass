"""Adapted B3d additive receipts; actual child CPU/wall and immutable input hashes."""
from pathlib import Path
import datetime,hashlib,importlib.metadata,json,math,os,platform,resource,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];RESULTS=ROOT/'results';RESULTS.mkdir(exist_ok=True)
ledger_path=RESULTS/'EXECUTION_LEDGER.json'
ledger=json.loads(ledger_path.read_text()) if ledger_path.exists() else dict(allocation_wall_s=60.,allocation_cpu_s=40.,
    scientific_guard_wall_s=120.,scientific_guard_cpu_s=60.,historical_remaining_wall_s=None,historical_remaining_cpu_s=None,budget_reset=False,
    prior_B3d_subtotal=dict(wall_s=8.752321051000724,cpu_s=8.78189),prior_turn_subtotal=dict(wall_s=8.835034051000724,cpu_s=8.864051),
    historical_partial_subtotal_wall_s=34.1262904040002,model_identity=dict(requested='LOWER_TIER_CODING_EXECUTOR',observed=None,observation_status='NO_MODEL_IDENTITY_TOOL_PROVIDED'),runs=[])
wall=sum(r['wall_s'] for r in ledger['runs']);cpu=sum(r['cpu_s'] for r in ledger['runs'])
cpu_limit=min(20,math.floor(40-cpu))
if wall>=60 or cpu_limit<1:raise RuntimeError('implementation scientific allocation exhausted')
argv=[sys.executable,*sys.argv[1:]]
idx=len(ledger['runs'])+1;prefix=RESULTS/f'attempt_{idx:02}'
env=os.environ.copy()
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:env[key]='1'
env['MPLCONFIGDIR']='/tmp/b3e_mplconfig'
wall_limit=min(30.,60-wall)
def limit():resource.setrlimit(resource.RLIMIT_CPU,(cpu_limit,cpu_limit))
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
receipt=dict(argv=argv,cwd=str(ROOT),start_utc=start,status='STARTED',wall_limit_s=wall_limit,cpu_limit_s=cpu_limit,
    stdout=str(prefix.with_suffix('.stdout').relative_to(ROOT)),stderr=str(prefix.with_suffix('.stderr').relative_to(ROOT)),
    environment={k:env[k] for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','MPLCONFIGDIR']},
    packages=dict(python=platform.python_version(),**{p:importlib.metadata.version(p) for p in ['numpy','scipy','matplotlib']}),
    runtime_identity=dict(executable=sys.executable,platform=platform.platform(),machine=platform.machine(),model_observed=None),
    code_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for d in ['code','tests','vendor'] for p in (ROOT/d).rglob('*.py')},
    input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'FROZEN_CONTRACT.md',ROOT/'CONTRACT_ADDENDUM.md',ROOT/'provenance/SOURCE_COPIES.json',ROOT/'provenance/reused_data/B3D_COHORT_SWEEP.json',ROOT/'theory/INDEPENDENT_SOURCE_AWARE_BOUND.md']})
prefix.with_suffix('.start.json').write_text(json.dumps(receipt,indent=2)+'\n')
t0=time.monotonic();r0=resource.getrusage(resource.RUSAGE_CHILDREN)
try:
    proc=subprocess.run(argv,cwd=ROOT,env=env,capture_output=True,timeout=wall_limit,preexec_fn=limit)
    stdout,stderr,code=proc.stdout,proc.stderr,proc.returncode
except subprocess.TimeoutExpired as e:
    stdout,stderr,code=e.stdout or b'',e.stderr or b'',-999
elapsed=time.monotonic()-t0;r1=resource.getrusage(resource.RUSAGE_CHILDREN)
prefix.with_suffix('.stdout').write_bytes(stdout);prefix.with_suffix('.stderr').write_bytes(stderr)
receipt.update(end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='COMPLETED' if code==0 else 'FAILED',
    exit_code=code,wall_s=elapsed,cpu_s=(r1.ru_utime+r1.ru_stime-r0.ru_utime-r0.ru_stime))
ledger['runs'].append(receipt);ledger['total_wall_s']=wall+elapsed;ledger['total_cpu_s']=cpu+receipt['cpu_s']
ledger_path.write_text(json.dumps(ledger,indent=2)+'\n')
print(json.dumps(dict(argv=argv,status=receipt['status'],exit_code=code,wall_s=elapsed,cpu_s=receipt['cpu_s'],cumulative_wall_s=ledger['total_wall_s'],cumulative_cpu_s=ledger['total_cpu_s'])))
sys.exit(0 if code==0 else 1)
