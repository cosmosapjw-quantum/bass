#!/usr/bin/env python3
"""Compare the actual S9 Rust adapter callbacks with independent num-dual AD.

No ODE history is integrated. All five fixture banks are immutable manufactured
data. The two final banks form one donor-transfer event at the same state.
The output directory must be new, so old evidence cannot be overwritten.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import resource
import subprocess
import time

GATE = 5e-13
STATES = [[0.42,-0.5,-0.08],[0.9,0.0,0.0],[1.4,0.34,0.09],[2.1,0.9,-0.13]]
TIMES = [0.45,0.9,1.2]
DIRECTIONS = [[1.0,0.0,0.0],[0.0,1.0,0.0],[0.0,0.0,1.0],
              [0.31,-0.73,1.2],[-2.0,0.09,-0.4]]


def cohort(u, b, energy, role='manufactured_new_isotropic_P24'):
    half = math.sqrt(0.5)
    return dict(u=u, b_birth=b, energy_birth=energy, role=role,
                mu=[-1.0,-half,0.0,half,1.0],
                alpha=[1/30,4/15,2/5,4/15,1/30])


def fixtures():
    old = cohort(0.0,-0.2,0.2,'existing_physical_anisotropic_stock')
    old['alpha'] = [a*(1+0.4*(3*m*m-1)/2) for a,m in zip(old['alpha'],old['mu'])]
    base = dict(donor0=0.7, decay_lambda=0.7, exposure=0.0,
                cosmological_constant=0.1, cohorts=[])
    stock = copy.deepcopy(base); stock.update(exposure=0.17, cohorts=[old])
    multi = copy.deepcopy(base)
    multi.update(exposure=0.41, cohorts=[old,cohort(0.15,0.13,0.012),cohort(0.3,-0.31,0.02)])
    queries = [dict(x=x,state=state,direction=direction)
               for x in TIMES for state in STATES for direction in DIRECTIONS]
    result = [(name,dict(bank=bank,queries=queries))
              for name,bank in [('dust',base),('physical_stock',stock),('multiple_cohorts',multi)]]
    before = copy.deepcopy(multi)
    after = copy.deepcopy(before)
    x, state, du = 0.61, STATES[2], 0.05
    w = before['donor0']*math.exp(-3*x-before['decay_lambda']*before['exposure'])\
        * -math.expm1(-before['decay_lambda']*du)
    after['exposure'] += du
    after['cohorts'].append(cohort(x,state[1],w))
    event_queries = [dict(x=x,state=state,direction=d) for d in DIRECTIONS]
    result += [('event_before',dict(bank=before,queries=event_queries)),
               ('event_after',dict(bank=after,queries=event_queries))]
    assert after['cohorts'][:-1] == before['cohorts']
    return result, w


def scaled_error(actual, reference):
    if len(actual) != 3 or len(reference) != 3:
        raise ValueError('CALLBACK_VECTOR_SHAPE')
    if not all(math.isfinite(v) for v in [*actual,*reference]):
        return math.inf
    return max(abs(a-r)/(1+abs(r)) for a,r in zip(actual,reference))


def file_receipt(path):
    data = path.read_bytes()
    return dict(path=path.name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())


def run_command(command, log_path):
    start = time.monotonic()
    run = subprocess.run(command,capture_output=True,text=True,timeout=1800)
    log_path.write_text(run.stdout+run.stderr)
    receipt = dict(command=list(map(str,command)),exit=run.returncode,
                   wall_seconds=time.monotonic()-start,
                   child_max_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                   log=file_receipt(log_path))
    if run.returncode:
        raise RuntimeError(json.dumps(receipt))
    return receipt


def execute(adapter, oracle, out):
    out.mkdir(parents=True,exist_ok=False)
    cases, event_w = fixtures()
    oracle_lines, index, commands = [], [], []
    for label, fixture in cases:
        path = out/f'{label}.input.json'
        path.write_text(json.dumps(fixture,indent=2,allow_nan=False)+'\n')
        bank = fixture['bank']
        amplitude = bank['donor0']*math.exp(-bank['decay_lambda']*bank['exposure'])
        for j, query in enumerate(fixture['queries']):
            case_id = f'{label}_{j:03d}'
            time_seed = [-1.3,0.0,0.71][j%3]
            scalars = [query['x'],*query['state'],amplitude,bank['cosmological_constant'],
                       time_seed,*query['direction']]
            oracle_lines.append('CASE '+case_id+' '+' '.join(format(v,'.17g') for v in scalars))
            for c in bank['cohorts']:
                oracle_lines.append('COHORT '+' '.join(format(c[k],'.17g')
                                    for k in ['u','b_birth','energy_birth']))
                oracle_lines.extend(f'RAY {m:.17g} {a:.17g}' for m,a in zip(c['mu'],c['alpha']))
                oracle_lines.append('END_COHORT')
            oracle_lines.append('END_CASE')
            index.append(dict(id=case_id,bank=label,row=j,time_seed=time_seed))
    oracle_input = out/'oracle.input.txt'
    oracle_input.write_text('\n'.join(oracle_lines)+'\n')
    (out/'fixture_index.json').write_text(json.dumps(index,indent=2)+'\n')
    prereg = dict(schema='BASS_S9_CALLBACK_AD_PREREG_V1',comparison_gate=GATE,
                 criterion='max_i abs(actual_i-reference_i)/(1+abs(reference_i))',
                 query_vectors=len(index),distinct_bank_state_points=38,
                 fixed_banks=5,new_ode_histories=0,event_transfer_energy=event_w,
                 controls=['omit explicit partial_t','reuse pre-birth partial_t after birth'],
                 adapter_binary=file_receipt(adapter),oracle_binary=file_receipt(oracle),
                 input_files=[file_receipt(p) for p in sorted(out.glob('*.input.*'))])
    (out/'PREREG.json').write_text(json.dumps(prereg,indent=2)+'\n')
    for label, _ in cases:
        commands.append(run_command([str(adapter),'callbacks',str(out/f'{label}.input.json'),
                                    str(out/f'{label}.actual.json')],out/f'{label}.command.log'))
    oracle_output = out/'oracle.actual.jsonl'
    commands.append(run_command([str(oracle),'--oracle',str(oracle_input),str(oracle_output)],
                                out/'oracle.command.log'))
    expected = {row['id']:row for row in map(json.loads,oracle_output.read_text().splitlines())}
    if len(expected) != len(index): raise ValueError('ORACLE_ROW_COUNT')
    actual = {}
    for label, fixture in cases:
        document = json.loads((out/f'{label}.actual.json').read_text())
        if document['bank'] != fixture['bank']: raise ValueError('ACTUAL_BANK_CHANGED')
        if len(document['rows']) != len(fixture['queries']): raise ValueError('ACTUAL_ROW_COUNT')
        actual[label] = document['rows']
    rows = []
    worst = dict(rhs=0.0,jvp=0.0,partial_t=0.0,augmented_composition=0.0)
    for item in index:
        ref = expected[item['id']]
        row = actual[item['bank']][item['row']]
        ev = row['evaluation']
        errors = dict(rhs=scaled_error(ev['rhs'],ref['rhs']),
                      jvp=scaled_error(row['jvp'],ref['jvp']),
                      partial_t=scaled_error(ev['partial_t'],ref['partial_t']),
                      augmented_composition=scaled_error(
                          [j+item['time_seed']*t for j,t in zip(row['jvp'],ev['partial_t'])],
                          ref['total_direction']))
        for name,value in errors.items(): worst[name] = max(worst[name],value)
        rows.append(dict(id=item['id'],errors=errors,pass_gate=all(e<=GATE for e in errors.values())))
    controls = []
    for label in ['dust','physical_stock','multiple_cohorts']:
        mismatch = scaled_error([0.0]*3,expected[f'{label}_000']['partial_t'])
        controls.append(dict(kind='omitted_partial_t',bank=label,scaled_mismatch=mismatch,
                             rejected=mismatch>GATE))
    stale = actual['event_before'][0]['evaluation']['partial_t']
    post = expected['event_after_000']['partial_t']
    mismatch = scaled_error(stale,post)
    controls.append(dict(kind='stale_pre_birth_partial_t',scaled_mismatch=mismatch,
                         rejected=mismatch>GATE))
    summary = dict(schema='BASS_S9_ACTUAL_CALLBACK_NUM_DUAL_RESULT_V1',
                   status='PASS' if all(r['pass_gate'] for r in rows) and all(c['rejected'] for c in controls) else 'FAIL',
                   comparison_gate=GATE,query_vectors=len(index),distinct_bank_state_points=38,
                   fixed_banks=5,new_ode_histories=0,max_scaled_errors=worst,
                   controls=controls,commands=commands,
                   scope='Actual production FrozenBank eval/jvp against independent dual primal; augmented Jv+Ft composition, not a separate SmallProblem callback execution.',
                   event_transfer_energy=event_w,
                   artifacts=[file_receipt(p) for p in sorted(out.iterdir()) if p.is_file()])
    (out/'COMPARISONS.json').write_text(json.dumps(rows,indent=2)+'\n')
    (out/'RESULT.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adapter',type=Path,required=True)
    parser.add_argument('--oracle',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    args = parser.parse_args()
    try:
        summary = execute(args.adapter.resolve(),args.oracle.resolve(),args.output_dir.resolve())
    except Exception as error:
        if args.output_dir.is_dir():
            (args.output_dir/'FAILURE.json').write_text(json.dumps(dict(status='FAIL',
                kind='callback_comparison_setup_or_execution',error=repr(error)),indent=2)+'\n')
        raise
    print(json.dumps({k:summary[k] for k in ['status','query_vectors','distinct_bank_state_points',
                                          'max_scaled_errors','controls']},indent=2))
    raise SystemExit(0 if summary['status']=='PASS' else 1)


if __name__ == '__main__':
    main()
