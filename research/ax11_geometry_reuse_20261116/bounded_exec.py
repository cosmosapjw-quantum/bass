#!/usr/bin/env python3
"""Execute only a named finite original-source build/test/profile command."""
import argparse,subprocess,resource,time,json,os,hashlib
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--kind',choices=['build','test','native'],required=True);ap.add_argument('--record',type=Path,required=True);ap.add_argument('--cwd',type=Path,required=True);ap.add_argument('command',nargs=argparse.REMAINDER)
a=ap.parse_args();cmd=a.command
if cmd and cmd[0]=='--':cmd=cmd[1:]
if not cmd:ap.error('missing command')
if a.record.exists():raise SystemExit('No overwrite/retry of execution receipt')
seconds=90 if a.kind in ('build','test') else 60
mem=2147483648
# Fresh local allocation; historic cumulative costs are never overwritten.
def limits():
 if a.kind=='native':os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
 resource.setrlimit(resource.RLIMIT_CPU,(seconds,seconds))
 resource.setrlimit(resource.RLIMIT_AS,(mem,mem))
 resource.setrlimit(resource.RLIMIT_FSIZE,(32*1024*1024,32*1024*1024))
env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',RAYON_NUM_THREADS='1',CARGO_BUILD_JOBS='1')
a.record.parent.mkdir(parents=True,exist_ok=True)
prior=resource.getrusage(resource.RUSAGE_CHILDREN);t=time.perf_counter();error=None
with a.record.with_suffix('.stdout').open('w') as o,a.record.with_suffix('.stderr').open('w') as e:
 try:r=subprocess.run(cmd,cwd=a.cwd,env=env,stdout=o,stderr=e,timeout=seconds,preexec_fn=limits,start_new_session=True);code=r.returncode
 except subprocess.TimeoutExpired as ex:
  # subprocess.run kills its direct process; no persistent solver is launched by these commands.
  code=124;error=repr(ex)
after=resource.getrusage(resource.RUSAGE_CHILDREN)
z={'command':cmd,'cwd':str(a.cwd),'kind':a.kind,'exit_code':code,'wall_s':time.perf_counter()-t,'cpu_s':after.ru_utime+after.ru_stime-prior.ru_utime-prior.ru_stime,'maxrss_kib':after.ru_maxrss,'timeout_s':seconds,'error':error,'automatic_retry':False,'prior_campaign_actual_cost':'UNKNOWN_PRESERVED','affinity_cpu':min(os.sched_getaffinity(0)) if a.kind=='native' else None}
a.record.write_text(json.dumps(z,indent=2)+'\n');print(json.dumps(z),flush=True)
if code:raise SystemExit(code if code>0 else 1)
