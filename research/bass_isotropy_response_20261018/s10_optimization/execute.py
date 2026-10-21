#!/usr/bin/env python3
"""Bounded S10 execution on the already verified S9 runtime; no downloads.

Source/inputs are verified against SOURCE_MANIFEST.json before each phase.
The Git readback must bind the manifest and all new crate source bytes. The
original S9 input/owner files retain their prior source identity independently.
Each phase is one explicit command with a new receipt; failed runs are retained.
"""
from __future__ import annotations
import argparse,hashlib,json,os,platform,resource,shutil,signal,subprocess,time
from datetime import datetime,timezone
from pathlib import Path

def digest(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def now():return datetime.now(timezone.utc).isoformat()
def main():
 p=argparse.ArgumentParser();p.add_argument('--runtime-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--git-readback',type=Path,required=True)
 p.add_argument('--phase',choices=['build','tests','micro','history','parallel','allocation_build','allocations'],required=True);p.add_argument('--attempt',default='r1');p.add_argument('--timeout',type=int,default=1800)
 p.add_argument('--build-receipt',type=Path);p.add_argument('--test-receipt',type=Path)
 a=p.parse_args();assert 1<=a.timeout<=1800
 source=Path(__file__).resolve().parent;lane=source.parent;repo=lane.parents[1];run=a.runtime_root.resolve();work=run/'build';dest=work/'client/s10_optimization';out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
 rp=out/(a.phase+'_'+a.attempt+'_PROCESS.json');assert not rp.exists(),'CREATE_ONLY_RECEIPT'
 prereg=source/'SOURCE_MANIFEST.json';m=json.loads(prereg.read_text());git=json.loads(a.git_readback.read_text());gmap={x['path']:x for x in git['files']}
 assert git['ref_readback']['matched'] and git['tree_readback']['complete'] and not git['tree_readback']['truncated']
 manifest_path=str(prereg.relative_to(repo));assert gmap[manifest_path]['git_blob_sha']==blob(prereg.read_bytes())
 for row in m['files']:
  data=(repo/row['path']).read_bytes();assert len(data)==row['bytes'] and digest(data)==row['sha256'],row['path']
  if '/s10_optimization/' in row['path']:
   assert gmap[row['path']]['git_blob_sha']==blob(data),row['path']
 # Runtime original source must remain the prior verified S9 client and owner.
 original=lane/'s9_vigilode';runtime_original=work/'client/s9_vigilode'
 for rel in ['src/lib.rs','src/main.rs','Cargo.toml','Cargo.lock']:
  assert (original/rel).read_bytes()==(runtime_original/rel).read_bytes(),rel
 assert (lane/'balance_p24.rs').read_bytes()==(work/'client/balance_p24.rs').read_bytes()
 if a.phase=='build':
  shutil.copytree(source,dest,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','target'))
  # The prior S9 preparation copied executable source only. Materialize this
  # unchanged include_str test fixture without editing any original repo file.
  fixture=runtime_original/'inputs/base.json';fixture.parent.mkdir(exist_ok=True)
  fixture_bytes=(original/'inputs/base.json').read_bytes()
  if fixture.exists():assert fixture.read_bytes()==fixture_bytes,'RUNTIME_FIXTURE_CONFLICT'
  else:fixture.write_bytes(fixture_bytes)
 else:
  for row in m['files']:
   prefix=str(source.relative_to(repo))+'/'
   if row['path'].startswith(prefix):
    f=dest/row['path'][len(prefix):];assert f.exists() and digest(f.read_bytes())==row['sha256'],str(f)
 rust=run/'rust/bin';cargo=rust/'cargo';binary=work/'target/release/s10-benchmark';saved=out/'s10-benchmark-timing.bin'
 if a.phase!='build':
  br=json.loads((a.build_receipt or out/'build_r1_PROCESS.json').read_text())
  assert br['status']=='completed' and br['source_manifest_sha256']==digest(prereg.read_bytes()),'BUILD_SOURCE_BINDING'
  assert saved.exists() and digest(saved.read_bytes())==br['timing_binary']['sha256'],'TIMING_BINARY_BUILD_BINDING'
 if a.phase in ['micro','history','parallel','allocation_build','allocations']:
  tr=json.loads((a.test_receipt or out/'tests_r1_PROCESS.json').read_text())
  assert tr['status']=='completed' and tr['source_manifest_sha256']==digest(prereg.read_bytes()),'C6_TEST_GATE'
 if a.phase=='allocations':
  ar=json.loads((out/'allocation_build_r1_PROCESS.json').read_text())
  assert ar['status']=='completed' and ar['source_manifest_sha256']==digest(prereg.read_bytes()),'ALLOCATION_BUILD_BINDING'
  assert digest(binary.read_bytes())==ar['allocation_binary']['sha256'],'ALLOCATION_BINARY_BINDING'
 env=os.environ.copy();env.update({'RUSTC':str(rust/'rustc'),'RUSTDOC':str(rust/'rustdoc'),'CARGO_HOME':str(work/'cargo_home'),'CARGO_TARGET_DIR':str(work/'target'),'CARGO_BUILD_JOBS':'2','CARGO_NET_OFFLINE':'true','RAYON_NUM_THREADS':'1','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'})
 env.pop('RUSTFLAGS',None);env.pop('CARGO_ENCODED_RUSTFLAGS',None)
 cargo_config=runtime_original/'.cargo/config.toml'
 cargo_prefix=[str(cargo),'--config',str(cargo_config)]
 if a.phase=='build':cmd=cargo_prefix+['build','--release','--offline','--locked','--bins']
 elif a.phase=='tests':cmd=cargo_prefix+['test','--release','--offline','--locked','--test','targeted','--','--test-threads=1']
 elif a.phase=='allocation_build':cmd=cargo_prefix+['build','--release','--offline','--locked','--features','allocation-probe','--bin','s10-benchmark']
 else:
  chosen=binary if a.phase=='allocations' else saved
  assert chosen.exists(),'BUILD_REQUIRED'
  cmd=[str(chosen),a.phase,str(lane/'evidence_s9/run_20261020_r1'),str(out/'measurements')]
 log=out/(a.phase+'_'+a.attempt+'.log')
 receipt={'schema':'BASS_S10_PROCESS_V1','phase':a.phase,'attempt':a.attempt,'started_at_utc':now(),'status':'running','command':cmd,'cwd':str(dest),'timeout_seconds':a.timeout,'published_source_commit':git['commit'],'published_source_tree':git['tree'],'source_manifest_sha256':digest(prereg.read_bytes()),'git_readback_sha256':digest(a.git_readback.read_bytes()),'environment_overrides':{k:env[k] for k in ['RUSTC','RUSTDOC','CARGO_HOME','CARGO_TARGET_DIR','CARGO_BUILD_JOBS','CARGO_NET_OFFLINE','RAYON_NUM_THREADS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']},'rustflags':'unset','limits':{'compile_jobs':2,'independent_history_workers':[1,2,4],'maximum_job_seconds':1800,'maximum_added_disk_bytes':4*1024**3,'actual_cgroup_cpu_quota':(Path('/sys/fs/cgroup/cpu.max').read_text().strip()),'actual_cgroup_memory_limit':(Path('/sys/fs/cgroup/memory.max').read_text().strip())}}
 if a.phase not in ['build','tests','allocation_build']:receipt['binary']={'path':cmd[0],'sha256':digest(Path(cmd[0]).read_bytes()),'bytes':Path(cmd[0]).stat().st_size}
 receipt['toolchain']={'rustc_verbose':subprocess.check_output([str(rust/'rustc'),'-Vv'],env=env,text=True).strip(),'cargo_version':subprocess.check_output([str(cargo),'--version'],env=env,text=True).strip(),'platform':platform.platform(),'offline_config_sha256':digest(cargo_config.read_bytes()),'reused_S9_preparation_receipt_sha256':digest((work/'PREPARATION_RETURN.json').read_bytes()),'original_S9_lock_sha256':digest((original/'Cargo.lock').read_bytes()),'new_lock_sha256':digest((source/'Cargo.lock').read_bytes())}
 save(rp,receipt);start=time.perf_counter()
 with log.open('wb') as f:
  proc=subprocess.Popen(cmd,cwd=dest,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  try:code=proc.wait(timeout=a.timeout);failure=None
  except subprocess.TimeoutExpired:
   failure='TIMEOUT';os.killpg(proc.pid,signal.SIGTERM)
   try:code=proc.wait(timeout=5)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);code=proc.wait()
 elapsed=time.perf_counter()-start
 receipt.update(status='completed' if code==0 else 'failed',exit_code=code,failure_kind=failure or (None if code==0 else 'COMMAND_NONZERO'),elapsed_seconds=elapsed,finished_at_utc=now(),log={'path':str(log),'sha256':digest(log.read_bytes()),'bytes':log.stat().st_size},child_maxrss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,child_maxrss_scope='Linux RUSAGE_CHILDREN maximum individual-child RSS, not simultaneous process-tree peak',cgroup_memory_current_bytes=int(Path('/sys/fs/cgroup/memory.current').read_text()))
 if code==0 and a.phase=='build':
  shutil.copy2(binary,saved);receipt['timing_binary']={'path':str(saved),'sha256':digest(saved.read_bytes()),'bytes':saved.stat().st_size,'allocation_probe_feature':False}
 if code==0 and a.phase=='allocation_build':receipt['allocation_binary']={'path':str(binary),'sha256':digest(binary.read_bytes()),'bytes':binary.stat().st_size,'allocation_probe_feature':True}
 receipt['runtime_total_bytes']=sum(x.stat().st_size for x in run.rglob('*') if x.is_file());receipt['disk_cap_pass_runtime_only']=receipt['runtime_total_bytes']<=4*1024**3
 save(rp,receipt);print(json.dumps(receipt,ensure_ascii=False));raise SystemExit(0 if code==0 else 1)
if __name__=='__main__':main()
