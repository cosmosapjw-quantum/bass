#!/usr/bin/env python3
"""One fixed S12 core/CAS-to-code check and paired benchmark, no old campaign."""
from __future__ import annotations
import argparse
from copy import deepcopy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import time
import numpy as np
import reference as ref
from process_control import run_owned, atomic_json


def sha(data):return hashlib.sha256(data).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_json(path,value)


def invoke(binary, mode, data, out, tag, records, repeat=0):
    args = [str(binary), '--mode', mode]
    if repeat:args += ['--repeat', str(repeat)]
    env = os.environ.copy()
    env.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', RAYON_NUM_THREADS='1')
    (out/(tag+'.stdin')).write_bytes(data)
    record=run_owned(args,env=env,stdin_bytes=data,
        stdout_path=out/(tag+'.stdout'),stderr_path=out/(tag+'.stderr'),
        receipt_path=out/(tag+'.process.json'),timeout_s=180,
        as_bytes=2*1024**3,file_bytes=64*1024**2)
    record.update(tag=tag,binary_sha256=sha(binary.read_bytes()))
    records.append(record)
    save(out/'EXECUTIONS.json',records)
    stdout=(out/(tag+'.stdout')).read_bytes() if (out/(tag+'.stdout')).exists() else b''
    stderr=(out/(tag+'.stderr')).read_bytes() if (out/(tag+'.stderr')).exists() else b''
    return record['exit_code'], stdout, stderr


def parse_output(data, mode, expected_count):
    lines=data.decode().splitlines()
    if lines[0] != 'BASS_S12_CORE_OUTPUT_V1':raise ValueError('CORE_OUTPUT_SCHEMA')
    if lines[1] != 'MODE '+mode or not lines[2].startswith('ROWS '):raise ValueError('CORE_HEADER')
    n=int(lines[2].split()[1]);rows=[];p=3
    if n != expected_count:raise ValueError('CORE_ROW_COUNT')
    for i in range(n):
        if lines[p] != f'ROW {i}':raise ValueError('CORE_ROW_ORDER')
        p+=1;row={}
        for name,count in [('RHS',6),('JVP',6),('PT',6),('JAC',36),('MOMENTS',10)]:
            parts=lines[p].split();p+=1
            if parts[0]!=name or len(parts)!=count+1:raise ValueError('CORE_FIELD_SHAPE')
            values=np.asarray([float(x) for x in parts[1:]])
            if not np.isfinite(values).all():raise ValueError('CORE_FIELD_NONFINITE')
            row[name]=values.reshape(6,6) if name=='JAC' else values
        rows.append(row)
    if p != len(lines):raise ValueError('CORE_TRAILING_OUTPUT')
    return rows


def scaled(actual, expected):
    a,b=np.asarray(actual),np.asarray(expected)
    return float(np.max(np.abs(a-b)/(1+np.maximum(np.abs(a),np.abs(b)))))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--binary',type=Path,required=True)
    p.add_argument('--source-commit',required=True);p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();binary=args.binary.resolve();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    records=[];checks=[];started=dt.datetime.now(dt.timezone.utc).isoformat();error=None
    def check(name, passed, **details):checks.append({'name':name,'pass':bool(passed),**details})
    try:
        bank,queries,diag=ref.core_fixture();data=ref.core_protocol(bank,queries).encode()
        save(out/'FIXED_INPUT.json',{'bank':bank,'queries':queries,'new_birth_differential':diag})
        (out/'FIXED_INPUT.txt').write_bytes(data)
        rows={}
        for mode in ['baseline','fused']:
            code,raw,stderr=invoke(binary,mode,data,out,'diagnostic_'+mode,records)
            check(mode+'_exit',code==0,exit_code=code)
            if code:raise RuntimeError(mode+'_execution_failed:'+stderr.decode())
            rows[mode]=parse_output(raw,mode,len(queries))
        errors=[]
        for i,q in enumerate(queries):
            state=np.asarray(q['state']);x=q['x'];j,pt=ref.complex_derivatives(x,state,bank)
            rhs=ref.direct_rhs(x,state,bank);mom=ref.direct_moments(x,state[1],state[4],bank)
            expected={'RHS':rhs,'JAC':j,'JVP':j@q['direction'],'PT':pt,
                      'MOMENTS_selected':mom}
            record={'index':i,'strain':state[1]-0.65}
            for name in ['RHS','JAC','JVP','PT']:
                value=scaled(rows['fused'][i][name],expected[name]);record[name]=value
                check(f'complex_direct_{i}_{name}',value<=2e-11,scaled_error=value,gate=2e-11)
            value=scaled(rows['fused'][i]['MOMENTS'][[0,1,8,9,7]],mom)
            check(f'direct_moments_{i}',value<=2e-11,scaled_error=value,gate=2e-11)
            for name in ['RHS','JAC','JVP','PT','MOMENTS']:
                value=scaled(rows['baseline'][i][name],rows['fused'][i][name])
                check(f'baseline_fused_{i}_{name}',value<=2e-13,scaled_error=value,gate=2e-13)
            errors.append(record)
        save(out/'DERIVATIVE_ERRORS.json',errors)
        # Required GL gauge of simultaneously shifted current and all birth b.
        gauge=deepcopy(bank)
        for c in gauge['cohorts']:
            c['memory_theta']=1.;c['mu_theta']=[0.]*len(c['mu']);c['alpha_theta']=[0.]*len(c['mu'])
        qq=deepcopy(queries[:6])
        for q in qq:q['state'][3:]=[0.,1.,0.]
        code,raw,_=invoke(binary,'fused',ref.core_protocol(gauge,qq).encode(),out,'source_frame_gauge',records)
        check('gauge_exit',code==0)
        gr=parse_output(raw,'fused',len(qq))
        gv=max(float(np.max(np.abs(r['RHS'][3:]))) for r in gr)
        check('source_frame_gauge_rhs',gv<=1e-11,max_absolute=gv,gate=1e-11)
        # Explicit invalid-input checks protect physical versus signed weights.
        negatives=[]
        b=deepcopy(bank);b['cohorts'][0]['alpha'][0]=-0.1;negatives.append(('negative_weight',b,queries))
        b=deepcopy(bank);b['cohorts'][0]['alpha'][0]*=1.01;negatives.append(('physical_parity',b,queries))
        b=deepcopy(bank);b['cohorts'][1]['mu_theta'][0]+=0.001;negatives.append(('tangent_parity',b,queries))
        q=deepcopy(queries);q[0]['state'][0]=-1.;negatives.append(('negative_h',bank,q))
        q=deepcopy(queries);q[0]['x']=0.1;negatives.append(('future_cohort',bank,q))
        for name,b,q in negatives:
            code,_,stderr=invoke(binary,'fused',ref.core_protocol(b,q).encode(),out,'negative_'+name,records)
            check('reject_'+name,code!=0 and b'S12_ERROR' in stderr,exit_code=code,error=stderr.decode().strip())
        for name,invalid in [('nonfinite',data.replace(b'BANK 0.8',b'BANK nan',1)),('trailing',data+b'TRAILING\n')]:
            if name=='nonfinite':
                lines=data.decode().splitlines();parts=lines[1].split();parts[1]='nan';lines[1]=' '.join(parts);invalid=('\n'.join(lines)+'\n').encode()
            code,_,stderr=invoke(binary,'fused',invalid,out,'negative_'+name,records)
            check('reject_'+name,code!=0 and b'S12_ERROR' in stderr,exit_code=code,error=stderr.decode().strip())
        # Timing only proceeds after the actual scientific comparison gates.
        if not all(c['pass'] for c in checks):raise RuntimeError('SCIENTIFIC_GATE_FAILURE_BEFORE_BENCHMARK')
        timings=[]
        for pair in range(9):
            modes=['baseline','fused'] if pair%2==0 else ['fused','baseline']
            row={'pair':pair,'warmup':pair<2,'order':modes}
            for mode in modes:
                tag=f'bench_{pair:02d}_{mode}'
                code,raw,stderr=invoke(binary,mode,data,out,tag,records,repeat=2000)
                if code:raise RuntimeError('BENCHMARK_PROCESS_FAILED')
                observed=parse_output(raw,mode,len(queries))
                identity=all(np.array_equal(observed[i][field],rows[mode][i][field]) for i in range(24) for field in rows[mode][i])
                check(tag+'_scientific_identity',identity)
                timing=json.loads(stderr)
                if timing['timed_evaluations']!=48000 or timing['repeat']!=2000:raise ValueError('TIMED_WORKLOAD_SHAPE')
                row[mode]=timing
            row['speedup']=row['baseline']['elapsed_ns']/row['fused']['elapsed_ns'];timings.append(row)
        used=[r for r in timings if not r['warmup']];ratios=[r['speedup'] for r in used]
        timing_summary={'paired_samples':7,'warmup_pairs':2,'all_pairs':timings,
            'paired_speedup_median':float(np.median(ratios)),'paired_speedup_q25':float(np.percentile(ratios,25)),
            'paired_speedup_q75':float(np.percentile(ratios,75)),
            'baseline_median_s':float(np.median([r['baseline']['elapsed_ns'] for r in used]))/1e9,
            'fused_median_s':float(np.median([r['fused']['elapsed_ns'] for r in used]))/1e9,
            'scope':'New24point48ray full augmented callback workload, not S10 histories or NCP64 speedup'}
        save(out/'PERFORMANCE.json',timing_summary)
    except Exception as e:error={'type':type(e).__name__,'message':str(e)}
    result={'schema':'BASS_S12_CORE_VALIDATION_V1','source_commit':args.source_commit,
        'started_utc':started,'ended_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
        'binary_sha256':sha(binary.read_bytes()),'status':'PASS_SCOPED' if error is None and all(x['pass'] for x in checks) else 'FAIL',
        'check_count':len(checks),'passed':sum(x['pass'] for x in checks),'checks':checks,'error':error,
        'processes':records,'completed_campaign_replays':0,'NCP_executed':False}
    save(out/'RETURN.json',result)
    print(json.dumps({k:result[k] for k in ['status','check_count','passed','error']}),flush=True)
    raise SystemExit(0 if result['status']=='PASS_SCOPED' else 1)


if __name__=='__main__':main()
