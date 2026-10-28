"""One bounded subprocess and raw receipt for the selected tau scientific unit."""
import os,time,resource,subprocess,json,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def limit():
 resource.setrlimit(resource.RLIMIT_CPU,(20,21))
 resource.setrlimit(resource.RLIMIT_AS,(512*1024*1024,512*1024*1024))

def main():
 if sys.argv[1:]!=['--once']:raise SystemExit('single scoped --once required')
 cmd=[sys.executable,'-I','-S',str(P/'code/run_once.py')]
 env=dict(os.environ);env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
 t=time.monotonic();before=resource.getrusage(resource.RUSAGE_CHILDREN)
 try:
  c=subprocess.run(cmd,capture_output=True,text=True,timeout=30,preexec_fn=limit,env=env)
  code=c.returncode;stdout=c.stdout;stderr=c.stderr;timed_out=False
 except subprocess.TimeoutExpired as e:
  code=124;timed_out=True;stdout=(e.stdout or b'').decode() if isinstance(e.stdout,bytes) else (e.stdout or '');stderr=(e.stderr or b'').decode() if isinstance(e.stderr,bytes) else (e.stderr or '')
 after=resource.getrusage(resource.RUSAGE_CHILDREN);wall=time.monotonic()-t
 cpu=(after.ru_utime+after.ru_stime)-(before.ru_utime+before.ru_stime)
 (P/'evidence/RUN.stdout').write_text(stdout)
 (P/'evidence/RUN.stderr').write_text(stderr)
 receipt={'exit':code,'timeout':timed_out,'command':cmd,'child_CPU_s':cpu,'child_wall_s':wall,'child_CPU_cap_s':20,
  'child_wall_cap_s':30,'memory_cap_MiB':512,'threads':1,'old_campaigns':0,'native_ODE':0,
  'wrapper_CPU_s':'NOT_MEASURED','old_budgets':'CLOSED_NOT_TRANSFERRED','network_preparation_model_cost':'UNKNOWN_NOT_ZERO'}
 (P/'evidence/RUN_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps(receipt,indent=2));print(stdout[-1600:])
 if code!=0:print(stderr[-1600:],file=sys.stderr);raise SystemExit(code)
if __name__=='__main__':main()
