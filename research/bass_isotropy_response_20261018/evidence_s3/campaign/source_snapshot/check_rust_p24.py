#!/usr/bin/env python3
"""Run prepared finite-support inputs once and verify both implementations."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess
import time
import numpy as np
from angular_p24 import ALGORITHM_ID,legendre24


def main():
    p=argparse.ArgumentParser()
    for name in ['probe','input','expected','out']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);here=Path(__file__).resolve().parent
    expected=json.loads(a.expected.read_text());cases=expected['cases']
    assert expected['schema']==ALGORITHM_ID
    path=a.out/'RUST_P24.csv';cmd=[str(a.probe.resolve()),str(a.input.resolve()),str(path.resolve())]
    t=time.monotonic();process=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
    (a.out/'RUST_P24.log').write_text('$ '+' '.join(cmd)+'\n'+process.stdout+process.stderr+f'\nEXIT_CODE={process.returncode}\n')
    assert process.returncode==0,process.stderr
    lines=path.read_text().splitlines()
    assert lines[0]==f'{ALGORITHM_ID} {len(cases)}' and lines[-1]==f'END {len(cases)}'
    parsed=list(csv.reader(lines[1:-1]));assert len(parsed)==len(cases)
    rows=[];ids=set()
    for got,ref in zip(parsed,cases):
        n=ref['n_mu'];assert got[0]==ref['id'] and int(got[1])==n and len(got)==7+n
        assert got[0] not in ids;ids.add(got[0])
        weights=np.array([float(v) for v in got[7:]]);mu=np.array(ref['mu'])
        p2,p4=legendre24(mu);r=np.array([math.fsum(weights*v) for v in [p2,p4]])
        reported=np.array([float(got[4]),float(got[5])]);delta=max(abs(weights-np.array(ref['weights'])))
        assert np.isfinite(weights).all() and np.all(weights>0)
        assert max(abs(reported))<=3e-15 and max(abs(r))<=3e-15
        assert abs(math.fsum(weights)-1)<=5e-16
        assert max(abs(weights-weights[::-1]))<=5e-14
        assert delta<2e-14
        rows.append({'id':ref['id'],'max_weight_difference':float(delta),
                     'reported_residuals':reported.tolist(),'independently_computed_residuals':r.tolist(),
                     'min_weight':float(weights.min())})
    result={'schema':'bass.s3.rust_python_parity.v1','status':'PASS_SCOPED_43_SAME_INPUTS' if len(rows)==43 else 'PASS_SCOPED',
        'command':cmd,'exit_code':process.returncode,'wall_seconds':time.monotonic()-t,'cases':len(rows),
        'source_sha256':hashlib.sha256((here/'balance_p24.rs').read_bytes()).hexdigest(),
        'binary_sha256':hashlib.sha256(a.probe.read_bytes()).hexdigest(),
        'input_sha256':hashlib.sha256(a.input.read_bytes()).hexdigest(),
        'expected_sha256':hashlib.sha256(a.expected.read_bytes()).hexdigest(),
        'output_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'max_weight_difference':max(r['max_weight_difference'] for r in rows),
        'max_Rust_moment_residual':max(max(abs(v) for v in r['reported_residuals']) for r in rows),
        'moment_atol':3e-15,'cross_implementation_weight_budget':2e-14,
        'continuum_angular_admission':False,'rows':rows}
    (a.out/'RETURN_RUST_PARITY.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))


if __name__=='__main__':main()
