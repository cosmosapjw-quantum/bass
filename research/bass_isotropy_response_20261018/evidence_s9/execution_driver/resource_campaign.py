#!/usr/bin/env python3
"""External resource/provenance wrapper for the already-frozen S9 campaign.

This file never edits model code, input, preregistration, tolerances or raw runs.
Scientific case timeout remains the frozen runner's 1800 seconds per case.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

RAM_CAP=16*1024**3
DISK_CAP=4*1024**3
SAMPLE_SECONDS=0.05

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    temporary.replace(path)

def disk_usage(roots):
    seen=set();allocated=logical=files=0
    for root in roots:
        for folder,dirs,names in os.walk(root,followlinks=False):
            dirs[:]=[name for name in dirs if not (Path(folder)/name).is_symlink()]
            for name in names:
                path=Path(folder)/name
                try: st=path.lstat()
                except FileNotFoundError: continue
                key=(st.st_dev,st.st_ino)
                if key in seen: continue
                seen.add(key);files+=1;logical+=st.st_size;allocated+=st.st_blocks*512
    return {'allocated_bytes':allocated,'logical_bytes':logical,'files':files,
            'method':'lstat st_blocks*512 and st_size; no symlink following; inode deduplication'}

def processes(root_pid):
    table={}
    for path in Path('/proc').glob('[0-9]*/status'):
        try:
            values={line.split(':',1)[0]:line.split(':',1)[1].strip() for line in path.read_text().splitlines() if ':' in line}
            pid=int(path.parent.name)
            table[pid]={'pid':pid,'ppid':int(values['PPid']),
                'rss_bytes':int(values.get('VmRSS','0 kB').split()[0])*1024,
                'hwm_bytes':int(values.get('VmHWM','0 kB').split()[0])*1024,
                'name':values.get('Name','unknown')}
        except (OSError,ValueError,KeyError): continue
    selected={root_pid};changed=True
    while changed:
        added={pid for pid,row in table.items() if row['ppid'] in selected}-selected
        changed=bool(added);selected.update(added)
    return [table[pid] for pid in sorted(selected) if pid in table]

def cgroup_value(name):
    try:
        value=(Path('/sys/fs/cgroup')/name).read_text().strip()
        return value if value=='max' else int(value)
    except (OSError,ValueError): return None

def terminate_tree(root_pid):
    rows=processes(root_pid)
    for row in reversed(rows):
        try: os.kill(row['pid'],signal.SIGTERM)
        except ProcessLookupError: pass
    return [row['pid'] for row in rows]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client-dir',type=Path,required=True)
    parser.add_argument('--binary',type=Path,required=True)
    parser.add_argument('--preparation-receipt',type=Path,required=True)
    parser.add_argument('--publication-receipt',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--budget-root',type=Path,action='append',required=True)
    args=parser.parse_args()
    client=args.client_dir.resolve();out=args.output_dir.resolve()
    out.mkdir(parents=True,exist_ok=True)
    if (out/'RESOURCE_RETURN.json').exists() or (out/'CAMPAIGN_RETURN.json').exists():
        raise ValueError('RESOURCE_OUTPUT_ALREADY_EXISTS; preserve and inspect earlier results')
    prereg=json.loads((client/'PREREGISTRATION.json').read_text())
    publication=json.loads(args.publication_receipt.read_text())
    if prereg['integration_count']!=8 or len(prereg['cases'])!=8:
        raise ValueError('EXPECTED_EXACTLY_EIGHT_FROZEN_CASES')
    if prereg['limits']['workers']!=1 or prereg['limits']['job_seconds']!=1800:
        raise ValueError('FROZEN_RESOURCE_CASE_LIMIT_MISMATCH')
    if (publication.get('preregistration_sha256')!=sha(client/'PREREGISTRATION.json')
        or not all(publication.get(key) is True for key in ['source_publication_readback','dropbox_readback','drive_readback'])):
        raise ValueError('ROOT_SOURCE_AND_DUAL_READBACK_GATE_REQUIRED')
    roots=[p.resolve() for p in args.budget_root]
    initial_disk=disk_usage(roots)
    command=[sys.executable,str(client/'campaign.py'),'--binary',str(args.binary.resolve()),
        '--preparation-receipt',str(args.preparation_receipt.resolve()),
        '--publication-receipt',str(args.publication_receipt.resolve()),'--output-dir',str(out)]
    record={'schema':'BASS_S9_RESOURCE_CAMPAIGN_V1','status':'launching','command':command,
        'source_commit':publication['source_commit'],'publication_receipt_sha256':sha(args.publication_receipt),
        'preregistration_sha256':sha(client/'PREREGISTRATION.json'),
        'binary_sha256':sha(args.binary),'preparation_receipt_sha256':sha(args.preparation_receipt),
        'wrapper_sha256':sha(__file__),'wrapper_path':str(Path(__file__).resolve()),
        'limits':{'scientific_workers':1,'additional_worker_cap':16,'ram_cap_bytes':RAM_CAP,
                  'disk_cap_bytes':DISK_CAP,'per_case_wall_seconds':1800},
        'memory_enforcement':{'inherited_RLIMIT_AS_per_process_bytes':RAM_CAP,
            'aggregate_campaign_descendants_RSS_monitor_bytes':RAM_CAP,
            'existing_shared_cgroup_memory_max_bytes':cgroup_value('memory.max'),
            'existing_shared_cgroup_unmodified':True,
            'cgroup_includes_other_owner_work':True},
        'environment':{'RAYON_NUM_THREADS':'1','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'},
        'budget_roots':list(map(str,roots)),'disk_before':initial_disk,
        'rss_sample_seconds':SAMPLE_SECONDS,'max_aggregate_RSS_bytes':0,'max_native_process_count':0,
        'sample_count':0,'case_resources':{},'resource_failure':None}
    save(out/'RESOURCE_LAUNCH.json',record)
    if initial_disk['allocated_bytes']>DISK_CAP:
        record.update({'status':'resource_preflight_failure','resource_failure':'disk_budget_before_execution'})
        save(out/'RESOURCE_RETURN.json',record);raise SystemExit(3)
    env=os.environ.copy();env.update(record['environment'])
    def inherited_limit():
        resource.setrlimit(resource.RLIMIT_AS,(RAM_CAP,RAM_CAP))
    start=time.monotonic();last_disk=start;last_checkpoint=start
    child=None
    try:
        with (out/'campaign_console.log').open('w') as log:
            child=subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT,
                                   start_new_session=True,preexec_fn=inherited_limit)
            record['campaign_pid']=child.pid
            while child.poll() is None:
                now=time.monotonic();rows=processes(child.pid)
                rss=sum(row['rss_bytes'] for row in rows)
                natives=[row for row in rows if row['name'].startswith('bass-s9')]
                record['max_aggregate_RSS_bytes']=max(record['max_aggregate_RSS_bytes'],rss)
                record['max_native_process_count']=max(record['max_native_process_count'],len(natives))
                record['sample_count']+=1
                active=[case['name'] for case in prereg['cases'] if (out/case['name']/'INPUT.json').exists()
                        and not (out/case['name']/'ASSESSMENT.json').exists()]
                for name in active:
                    sample=record['case_resources'].setdefault(name,{'samples':0,'peak_sampled_aggregate_RSS_bytes':0,
                        'peak_sampled_native_RSS_bytes':0,'peak_observed_native_HWM_bytes':0})
                    sample['samples']+=1
                    sample['peak_sampled_aggregate_RSS_bytes']=max(sample['peak_sampled_aggregate_RSS_bytes'],rss)
                    sample['peak_sampled_native_RSS_bytes']=max(sample['peak_sampled_native_RSS_bytes'],sum(r['rss_bytes'] for r in natives))
                    sample['peak_observed_native_HWM_bytes']=max(sample['peak_observed_native_HWM_bytes'],sum(r['hwm_bytes'] for r in natives))
                if rss>RAM_CAP: record['resource_failure']='aggregate_RSS_budget'
                if len(natives)>1: record['resource_failure']='scientific_worker_budget'
                if now-last_disk>=1.0:
                    current=disk_usage(roots);record['disk_latest']=current;last_disk=now
                    if current['allocated_bytes']>DISK_CAP: record['resource_failure']='disk_budget_during_execution'
                if now-start>8*1800+120: record['resource_failure']='matrix_wall_budget'
                if record['resource_failure']:
                    record['terminated_task_pids']=terminate_tree(child.pid)
                    try: child.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        for row in processes(child.pid):
                            try: os.kill(row['pid'],signal.SIGKILL)
                            except ProcessLookupError: pass
                        child.wait()
                    break
                if now-last_checkpoint>=1.0:
                    record['elapsed_seconds']=now-start;save(out/'RESOURCE_PROGRESS.json',record);last_checkpoint=now
                time.sleep(SAMPLE_SECONDS)
            record['campaign_exit_code']=child.wait()
    except Exception as error:
        record['resource_failure']={'kind':'wrapper_exception','error_type':type(error).__name__,'error':str(error)}
        if child is not None and child.poll() is None:
            record['terminated_task_pids']=terminate_tree(child.pid)
    finally:
        record['elapsed_seconds']=time.monotonic()-start
        record['disk_after']=disk_usage(roots)
        record['shared_cgroup_memory_current_after']=cgroup_value('memory.current')
        record['child_maxrss_kib_rusage']=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        for case in prereg['cases']:
            name=case['name'];folder=out/name
            sample=record['case_resources'].setdefault(name,{'samples':0,'sampled_peak_RSS_bytes':None,
                'sampling_note':'No live sample caught this case; do not read this as zero memory.'})
            process=folder/'PROCESS.json'
            if process.exists():
                sample['process_receipt_sha256']=sha(process)
                try:
                    value=json.loads(process.read_text());sample['exit_code']=value['exit_code'];sample['elapsed_seconds']=value['elapsed_seconds']
                except (OSError,ValueError,KeyError) as error: sample['process_readback_error']=str(error)
            else:
                sample['case_execution']='not_completed_or_not_attempted'
            assessment=folder/'ASSESSMENT.json'
            if assessment.exists(): sample['assessment_sha256']=sha(assessment)
            if folder.exists(): save(folder/'RESOURCE.json',sample)
        record['status']='completed_wrapper' if record.get('campaign_exit_code')==0 and not record['resource_failure'] else 'campaign_or_resource_failure'
        save(out/'RESOURCE_RETURN.json',record)
        print(json.dumps({'status':record['status'],'exit_code':record.get('campaign_exit_code'),
            'resource_failure':record['resource_failure'],'elapsed_seconds':record['elapsed_seconds'],
            'max_aggregate_RSS_bytes':record['max_aggregate_RSS_bytes'],'resource_receipt':str(out/'RESOURCE_RETURN.json')}),flush=True)
    raise SystemExit(0 if record['status']=='completed_wrapper' else 3)

if __name__=='__main__': main()
