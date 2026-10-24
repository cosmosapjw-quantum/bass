"""One-thread, bounded scientific subprocess and append-only execution receipts."""
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts'
ledger_path = OUT / 'EXECUTION_LEDGER.json'
ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else []
if sum(x['wall_seconds'] for x in ledger) >= 90 or sum(x['cpu_seconds'] for x in ledger) >= 40:
    raise SystemExit('insufficient prospective aggregate wall/CPU budget')
argv = sys.argv[1:]
if not argv:
    raise SystemExit('provide executable and argv')
env = os.environ.copy()
env.update({k: '1' for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS')})
env['MPLBACKEND'] = 'Agg'
env['MPLCONFIGDIR'] = str(OUT / 'MPLCONFIG')
env['PYTHONPATH'] = str(ROOT) + os.pathsep + str(ROOT / 'code')
def limits():
    resource.setrlimit(resource.RLIMIT_CPU, (20, 20))
before = resource.getrusage(resource.RUSAGE_CHILDREN)
started = time.perf_counter()
try:
    result = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True, text=True, timeout=30, preexec_fn=limits)
    stdout, stderr, status = result.stdout, result.stderr, result.returncode
except subprocess.TimeoutExpired as exc:
    stdout, stderr, status = exc.stdout or '', exc.stderr or '', 124
    if isinstance(stdout, bytes): stdout = stdout.decode(errors='replace')
    if isinstance(stderr, bytes): stderr = stderr.decode(errors='replace')
elapsed = time.perf_counter() - started
after = resource.getrusage(resource.RUSAGE_CHILDREN)
index = len(ledger) + 1
stem = f'COMMAND_{index:02}'
(OUT / (stem + '.stdout.txt')).write_text(stdout)
(OUT / (stem + '.stderr.txt')).write_text(stderr)
hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
          for folder in ('code', 'tests', 'vendor', 'inputs') for p in sorted((ROOT / folder).rglob('*'))
          if p.is_file() and '__pycache__' not in p.parts}
row = dict(command_index=index, argv=argv, cwd=str(ROOT), exit_code=status,
           wall_seconds=elapsed, cpu_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
           started_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time()-elapsed)),
           stdout=stem+'.stdout.txt', stderr=stem+'.stderr.txt', hashes_sha256=hashes,
           environment={k: env[k] for k in env if k.endswith('NUM_THREADS') or k in ('MPLBACKEND','PYTHONPATH')},
           per_command_guard=dict(wall_seconds=30,cpu_seconds=20), new_ivp=0, old_campaign_replay=0)
ledger.append(row)
ledger_path.write_text(json.dumps(ledger, indent=2)+'\n')
print(json.dumps({k:row[k] for k in ('command_index','argv','exit_code','wall_seconds','cpu_seconds')}))
print(stdout, end='')
if stderr: print(stderr, file=sys.stderr, end='')
sys.exit(status)
