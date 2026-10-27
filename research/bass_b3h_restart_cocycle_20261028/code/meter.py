"""Run one bounded new child and preserve failure-inclusive costs."""
import json, math, os, resource, subprocess, sys, time
from pathlib import Path
U=Path(__file__).resolve().parents[1]
ledger=U/'results/EXECUTION_LEDGER.jsonl'
name=sys.argv[1]; cmd=sys.argv[2:]
old=[json.loads(x) for x in ledger.read_text().splitlines()] if ledger.exists() else []
cpu=sum(x['child_cpu_s'] for x in old); wall=sum(x['wall_s'] for x in old)
if cpu>=120 or wall>=300: raise SystemExit('ALLOCATION_EXHAUSTED')
def limit():
 resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
 c=max(1,math.ceil(120-cpu)); resource.setrlimit(resource.RLIMIT_CPU,(c,c))
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
b=resource.getrusage(resource.RUSAGE_CHILDREN); t=time.monotonic(); w=time.process_time()
try:
 with (U/'results'/f'{name}.stdout').open('w') as out,(U/'results'/f'{name}.stderr').open('w') as err:
  r=subprocess.run(cmd,cwd=U,env=env,stdout=out,stderr=err,timeout=min(40,300-wall),preexec_fn=limit)
  rc=r.returncode
except subprocess.TimeoutExpired: rc=124
a=resource.getrusage(resource.RUSAGE_CHILDREN)
row={'name':name,'command':cmd,'exit_code':rc,'child_cpu_s':a.ru_utime+a.ru_stime-b.ru_utime-b.ru_stime,'wall_s':time.monotonic()-t,'wrapper_cpu_s':time.process_time()-w,'max_RSS_KiB':a.ru_maxrss,'threads':1,'native_old_replays':0}
with ledger.open('a') as f:f.write(json.dumps(row)+'\n')
print(json.dumps(row)); print((U/'results'/f'{name}.stdout').read_text()[-4500:]); print((U/'results'/f'{name}.stderr').read_text()[-3000:])
sys.exit(rc)
