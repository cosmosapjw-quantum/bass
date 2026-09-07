#!/usr/bin/env python3
"""Run one recorded revision of the exact research SC suite; retain nonzero exits."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,shlex,subprocess,time
parser=argparse.ArgumentParser();parser.add_argument('revision');arg=parser.parse_args()
assert arg.revision in ['original']+['repair'+str(i) for i in range(1,8)]
r=Path(__file__).resolve().parent;intake=json.loads((r/'intake.json').read_text());source=Path(intake['BASS_REPO']);code=Path(intake['code_root'])
out=r/'execution'/arg.revision;out.mkdir(parents=True,exist_ok=True)
def now():return datetime.now(timezone.utc).isoformat()
def save(name,value):(out/name).write_text(json.dumps(value,indent=2)+'\n')
expected=json.loads((r/'identity/dependencies-before.json').read_text());names=list(json.loads((r/'identity/original-code.json').read_text()))
def hashes():return {**{p:hashlib.sha256((source/p).read_bytes()).hexdigest() for p in expected},**{n:hashlib.sha256((code/n).read_bytes()).hexdigest() for n in names}}
before=hashes()
assert all(before[p]==e['sha256'] for p,e in expected.items())
exes=json.loads((r/'identity/executables.json').read_text())
for e in exes.values():assert hashlib.sha256(Path(e['resolved_path']).read_bytes()).hexdigest()==e['sha256']
prior=list((r/'execution').glob('*/ATTEMPT_STARTED.json'));assert len(prior)<8
argv=[exes['timeout']['resolved_path'],'--signal=TERM','--kill-after=10s','150s',exes['wolframscript']['path'],'-local',exes['kernel']['resolved_path'],'-file',str(code/'run_state_constraints.wls')]
record={'task':'BG02_STATE_TO_CONSTRAINT_MAP_VALIDATION_V1','revision':arg.revision,'attempt':len(prior)+1,'start_utc':now(),'argv':argv,'cwd':str(out),'environment_overrides':{'BASS_REPO':str(source)},'inner_timeout_seconds':120,'outer_timeout_seconds':150,'kill_after_seconds':10,'code_identity':{n:before[n] for n in names},'launcher_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
with (out/'ATTEMPT_STARTED.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
save('source-before.json',before)
(out/'process-limits.txt').write_text(Path('/proc/self/limits').read_text())
g=Path('/sys/fs/cgroup')/Path('/proc/self/cgroup').read_text().split('0::',1)[1].strip().lstrip('/');caps=[]
while True:
 caps.append({'path':str(g),'limits':{n:(g/n).read_text().strip() for n in ['memory.max','memory.high','cpu.max','pids.max'] if (g/n).exists()}})
 if g==Path('/sys/fs/cgroup'):break
 g=g.parent
save('resource-caps.json',caps)
(out/'command.txt').write_text('env '+shlex.quote('BASS_REPO='+str(source))+' '+shlex.join(argv)+' >stdout.log 2>stderr.log\n')
env=os.environ.copy();env['BASS_REPO']=str(source);start=time.monotonic();exitcode=None;error=None
try:
 with (out/'stdout.log').open('xb') as so,(out/'stderr.log').open('xb') as se:
  p=subprocess.Popen(argv,cwd=out,env=env,stdin=subprocess.DEVNULL,stdout=so,stderr=se)
  save('process-start.json',{'pid':p.pid,'utc':now()});exitcode=p.wait()
except OSError as e:error=repr(e)
finally:
 after=hashes();save('source-after.json',after)
 record.update({'end_utc':now(),'elapsed_seconds':time.monotonic()-start,'process_exit':exitcode,'launch_error':error,'timeout':exitcode==124,'source_unchanged':before==after,'exit_semantics':'GNU timeout status; child status when not timed out.'});save('process.json',record)
(out/'process_exit.txt').write_text(str(exitcode)+'\n')
stdout=(out/'stdout.log').read_text();lines=stdout.splitlines();starts=[i for i,x in enumerate(lines) if x=='SC_FINAL_BEGIN'];ends=[i for i,x in enumerate(lines) if x=='SC_FINAL_END']
final=None;parse_error=None
if len(starts)==len(ends)==1 and starts[0]<ends[0]:
 try:final=json.loads('\n'.join(lines[starts[0]+1:ends[0]]));save('sc-final.json',final)
 except ValueError as e:parse_error=repr(e)
else:parse_error='SC final markers missing/duplicate/unordered'
events=[x for x in lines if x.startswith('SC_TEST_EVENT ')]
(out/'test-events.log').write_text('\n'.join(events)+('\n' if events else ''))
save('extraction.json',{'final_json_observed':final is not None,'parse_error':parse_error,'test_event_count':len(events)})
print(json.dumps({'revision':arg.revision,'process_exit':exitcode,'elapsed_seconds':record['elapsed_seconds'],'final_status':None if final is None else final.get('status'),'events':len(events),'source_unchanged':before==after}))
