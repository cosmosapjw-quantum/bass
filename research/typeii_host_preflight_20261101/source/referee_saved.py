"""Blind-ish saved-data chart verifier: NO import from source model or generated RHS.

Explicit raise, remains active under `python -O`. Checks physics and provenance scope;
not an independently authored reviewer, not production validation.
"""
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path
SQ3=math.sqrt(3.)

def inspect(csv_path:Path,results_path:Path):
    rows=list(csv.DictReader(csv_path.open(newline='')))
    info=json.loads(results_path.read_text())
    if len(rows)!=401 or info['physical_rows']!=401:raise RuntimeError('PHYSICAL_401_ROWS_MISSING')
    if info['production_ready'] or info['real_rustcore_compiled']:
        raise RuntimeError('UNAUTHORIZED_PRODUCTION_CLAIM')
    if info['original_main']!='9c6506e4e2087129a8b674ff10438e5db1a55c9d':
        raise RuntimeError('SOURCE_WRONG_HEAD')
    maxerr=0.;minderiv=math.inf
    for i,line in enumerate(rows):
        if int(line['index'])!=i:raise RuntimeError('ORDER_BAD')
        sp,sm,n,v=[float(line[k]) for k in ('SigmaPlus','SigmaMinus','N1','v2')]
        sig=float(line['stored_Sigma13']);om=float(line['stored_Omega'])
        g=1.3; gp=1+(g-1)*v*v
        budget=1-sp*sp-sm*sm-n*n/12
        beta=3*g*g*v*v/(n*n*gp*gp)
        eq=om+beta*om*om-budget
        cod=-SQ3*n*sig-3*g*om*v/gp
        gauss=om-(budget-sig*sig)
        der=-SQ3*n*(1+2*beta*om)
        record_der=float(line['constraint_minor'])
        err=max(abs(eq),abs(cod),abs(gauss),abs(der-record_der),
                abs(sig-float(line['chart_Sigma13'])),abs(om-float(line['chart_Omega'])))
        maxerr=max(maxerr,err);minderiv=min(minderiv,abs(der))
        if err>1e-11:raise RuntimeError(f'SOURCE_PHYSICS_FALSE_AT_ROW:{i}, err={err}')
        if not (der<0 and n>0 and budget>0 and abs(v)<1):
            raise RuntimeError(f'INVALID_BRANCH_AT_ROW:{i}')
    if minderiv<1e-4:raise RuntimeError('UNSAFE_IMPLICIT_FUNCTION_RANK')
    return {'rows':401,'max_absolute_constraint_gap':maxerr,'min_abs_jacobian':minderiv,
            'provenance':info['source']['status'],'optimized_safe':True,'production_ready':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True)
    x=p.parse_args()
    print(json.dumps(inspect(x.data/'TYPEII_401_PHYSICAL_CHART.csv',
                             x.data/'TYPEII_HOST_CHART_RESULTS.json'),indent=2))