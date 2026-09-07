#!/usr/bin/env python3
"""Bounded candidate AUX launcher; scientific source and frozen assertions untouched."""
from pathlib import Path
from datetime import datetime, timezone
import argparse,hashlib,json,os,shlex,subprocess,time
p=argparse.ArgumentParser();p.add_argument('revision',choices=['original','repair1','repair2']);a=p.parse_args()
r=Path(__file__).resolve().parent
out=r/'execution'/a.revision;out.mkdir(parents=True,exist_ok=True)
def now():return datetime.now(timezone.utc).isoformat()
def save(name,v):(out/name).write_text(json.dumps(v,indent=2)+'\n')
entries=json.loads((r/'identity/source-before.json').read_text())
for e in entries:assert hashlib.sha256((r/'source'/e['path']).read_bytes()).hexdigest()==e['sha256']
exes=json.loads((r/'identity/executables.json').read_text())
for e in exes.values():assert hashlib.sha256(Path(e['resolved_path']).read_bytes()).hexdigest()==e['sha256']
driver=r/'driver'/a.revision/'BASS_AUX13_AUX14_V1.wls'
argv=[exes['timeout']['resolved_path'],'--signal=TERM','--kill-after=10s','150s',exes['wolframscript']['path'],'-local',exes['kernel']['resolved_path'],'-file',str(driver)]
env=os.environ.copy();env['BASS_REPO']=str(r/'source')
record={'task':'BG02_REPAIRED_CANDIDATE_AUX13_AUX14_COMPARISON','revision':a.revision,'start_utc':now(),'argv':argv,'cwd':str(out),'environment_overrides':{'BASS_REPO':env['BASS_REPO']},'inner_timeout_seconds':120,'outer_timeout_seconds':150,'kill_after_seconds':10,'driver_sha256':hashlib.sha256(driver.read_bytes()).hexdigest(),'launcher_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'resource_policy':'Inherit actual process and ancestor cgroup limits; do not install or alter permanent resource settings.'}
with (out/'ATTEMPT_STARTED.json').open('x') as f:
 json.dump(record,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
(out/'command.txt').write_text('env '+shlex.quote('BASS_REPO='+env['BASS_REPO'])+' '+shlex.join(argv)+' >stdout.log 2>stderr.log\n')
(out/'inherited-process-limits.txt').write_text(Path('/proc/self/limits').read_text())
(out/'inherited-cgroup.txt').write_text(Path('/proc/self/cgroup').read_text())
start=time.monotonic()
with (out/'stdout.log').open('xb') as so,(out/'stderr.log').open('xb') as se:
 child=subprocess.Popen(argv,cwd=out,env=env,stdin=subprocess.DEVNULL,stdout=so,stderr=se)
 save('process-start.json',{'pid':child.pid,'observed_utc':now()})
 code=child.wait()
record.update({'process_exit':code,'elapsed_seconds':time.monotonic()-start,'end_utc':now(),'timeout':code==124,'termination_signal':-code if code<0 else None,'exit_semantics':'GNU timeout status; child exit when not timed out.'})
save('process.json',record);(out/'process_exit.txt').write_text(str(code)+'\n')
stdout=(out/'stdout.log').read_text();begin='AUX_FINAL_BEGIN\n';end='\nAUX_FINAL_END'
if stdout.count(begin)==1 and stdout.count(end)==1:
 final=json.loads(stdout.split(begin,1)[1].split(end,1)[0]);save('aux-final.json',final)
else:final={'status':'FINAL_JSON_MISSING_OR_AMBIGUOUS'}
print(json.dumps({'revision':a.revision,'process_exit':code,'elapsed_seconds':record['elapsed_seconds'],'final_status':final['status'],'test_events':stdout.count('AUX_TEST_EVENT ')}))
