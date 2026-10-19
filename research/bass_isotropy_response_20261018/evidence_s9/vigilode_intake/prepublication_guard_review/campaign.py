#!/usr/bin/env python3
"""Execute the prepublished S9 matrix with per-case immutable raw receipts.

This script requires the root's concrete source/publication/dual-readback receipt.
It never retries a failed angular support with different tolerance or resolution.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time
from analyze import assess,cohort_digest
HERE=Path(__file__).resolve().parent

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+"\n")

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binary',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--publication-receipt',type=Path,required=True)
    p.add_argument('--preparation-receipt',type=Path,required=True)
    args=p.parse_args()
    prereg_path=HERE/'PREREGISTRATION.json'; prereg=json.loads(prereg_path.read_text())
    auth=json.loads(args.publication_receipt.read_text())
    if (auth.get('schema')!='BASS_S9_CAMPAIGN_AUTH_V1' or len(auth.get('source_commit',''))!=40
        or auth.get('preregistration_sha256')!=sha(prereg_path)
        or not all(auth.get(k) is True for k in ['source_publication_readback','dropbox_readback','drive_readback'])):
        raise ValueError('SOURCE_PUBLICATION_AND_DUAL_READBACK_REQUIRED')
    for relative,digest in prereg['input_sha256'].items():
        if sha(HERE/relative)!=digest: raise ValueError('FROZEN_INPUT_CHANGED: '+relative)
    for relative,digest in prereg['source_sha256'].items():
        if sha(HERE/relative)!=digest: raise ValueError('FROZEN_SOURCE_CHANGED: '+relative)
    prepared=json.loads(args.preparation_receipt.read_text())
    if prepared.get('status')!='prepared' or prepared.get('binary',{}).get('sha256')!=sha(args.binary):
        raise ValueError('PREPARED_BINARY_IDENTITY_MISMATCH')
    if (prepared.get('vigilode_source')!=prereg['vigilode_source']
        or prepared.get('balance_owner_sha256')!=prereg['unchanged_balance_owner_sha256']
        or not any(row['exit_code']==0 and any(word in row['command'] for word in ['build','test'])
                   for row in prepared.get('commands',[]))):
        raise ValueError('PREPARED_BUILD_SOURCE_IDENTITY_MISMATCH')
    for relative,digest in prepared['client_source_sha256'].items():
        if sha(HERE/relative)!=digest: raise ValueError('PREPARED_CLIENT_SOURCE_MISMATCH: '+relative)
    out=args.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    if (out/'CAMPAIGN_RETURN.json').exists(): raise ValueError('CAMPAIGN_OUTPUT_ALREADY_EXISTS')
    base=json.loads((HERE/'inputs/base.json').read_text())
    reference=json.loads((HERE/'reference/S8_PRIMAL.json').read_text())
    summary={'schema':'BASS_S9_CAMPAIGN_V1','source_publication':auth,
        'preregistration_sha256':sha(prereg_path),'binary_sha256':sha(args.binary),
        'preparation_receipt_sha256':sha(args.preparation_receipt),
        'limits':prereg['limits'],'cases':[],'state':'running','not_admitted':prereg['not_admitted']}
    save(out/'CAMPAIGN_RETURN.json',summary)
    env=os.environ.copy(); env.update({'RAYON_NUM_THREADS':'1','OMP_NUM_THREADS':'1'})
    for case in prereg['cases']:
        data=copy.deepcopy(base); data['solver'].update(case['solver'])
        if case['model']=='analytic_FLRW':
            c=data['config']; c.update({'k':0,'y0':0.0,'decay_lambda':0.0,'old_isotropic':0.2,'old_anisotropic':0.0})
            stock=copy.deepcopy(data['initial_cohorts'][0]); stock['energy_birth']=0.2
            data['initial_cohorts']=[stock]; data['expected_old_digests']=[cohort_digest(stock)]
            data['provenance']['control']='Synthetic analytic FLRW data; independent initial stock, no existing stock mutation'
        folder=out/case['name']; folder.mkdir()
        save(folder/'INPUT.json',data)
        cmd=[str(args.binary.resolve()),'run',str(folder/'INPUT.json'),str(folder/'RAW.json')]
        start=time.time()
        with (folder/'console.log').open('w') as log:
            child=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            try: code=child.wait(timeout=prereg['limits']['job_seconds'])
            except subprocess.TimeoutExpired:
                os.killpg(child.pid,signal.SIGTERM)
                try: child.wait(timeout=5)
                except subprocess.TimeoutExpired: os.killpg(child.pid,signal.SIGKILL);child.wait()
                code=124
        process={'command':cmd,'exit_code':code,'elapsed_seconds':time.time()-start,
                 'input_sha256':sha(folder/'INPUT.json'),'log_sha256':sha(folder/'console.log')}
        raw=folder/'RAW.json'
        if raw.exists():
            process['raw_sha256']=sha(raw)
            result=assess(json.loads(raw.read_text()),reference,prereg,case)
            if code!=0 and result['completed']:
                result.update({'completed':False,'status':'process_return_inconsistency'})
        else:
            result={'case':case['name'],'status':'failed','completed':False,
                    'failure':{'kind':'job_timeout' if code==124 else 'process_failure_without_receipt','exit_code':code}}
        save(folder/'PROCESS.json',process); save(folder/'ASSESSMENT.json',result)
        summary['cases'].append({'case':case,'process':process,'assessment':result})
        save(out/'CAMPAIGN_RETURN.json',summary)
        print(json.dumps({'case':case['name'],'status':result['status'],'failure':result.get('failure'),
                          'all_quality_gates':result.get('all_quality_gates')}),flush=True)
    summary['state']='completed_matrix'
    summary['completed_histories']=sum(row['assessment']['completed'] for row in summary['cases'])
    summary['failed_histories']=len(summary['cases'])-summary['completed_histories']
    fine=[row for row in summary['cases'] if row['case']['claim_role']=='primary_fine']
    summary['fine_preregistered_gate_pass']=all(row['assessment'].get('all_quality_gates') is True for row in fine)
    controls=[row for row in summary['cases'] if row['case']['claim_role']=='analytic_control']
    summary['analytic_control_gate_pass']=all(row['assessment'].get('all_quality_gates') is True for row in controls)
    summary['claim']='Bounded manufactured-history client only; failures remain explicit; no production expansion'
    save(out/'CAMPAIGN_RETURN.json',summary)

if __name__=='__main__': main()
