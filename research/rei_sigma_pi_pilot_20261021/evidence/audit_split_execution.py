"""Summarize existing split-sweep receipts and CSVs; never execute a solver."""
from collections import Counter
from datetime import datetime, timezone
import csv
import hashlib
import json
from pathlib import Path

LANE = Path(__file__).resolve().parents[1]
RUN = LANE / 'results/split729'
AGG = RUN / 'aggregate'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def span(values):
    vals = list(values)
    return {'min': min(vals), 'max': max(vals), 'span': max(vals)-min(vals)}


def main():
    summary = read(AGG/'summary.json')
    manifest = read(RUN/'inputs_manifest/manifest.json')
    issues = []
    bound = []
    for item in manifest['bound_files']:
        path = Path(item['path'])
        if not path.is_absolute():
            path = RUN/'inputs_manifest'/path
        actual = sha(path)
        bound.append({'path': str(path), 'sha256': actual, 'matches': actual == item['sha256']})
        if actual != item['sha256']:
            issues.append('bound:'+str(path))
    receipts = []
    gate_values = []
    raw_case_ids = []
    for path in sorted((RUN/'scope/jobs').rglob('receipt.json')):
        rec = read(path)
        for name, identity in rec.get('outputs', {}).items():
            out = path.parent/name
            if out.stat().st_size != identity['bytes'] or sha(out) != identity['sha256']:
                issues.append('output:'+str(out))
        obj = read(path.parent/'result.json')
        if obj['science_binding'] != summary['science_binding']:
            issues.append('science_binding:'+str(path))
        for case in obj['cases']:
            raw_case_ids.append(case['case']['case_id'])
            gate_values.extend(case['gates'].values())
        receipts.append(rec)
    with (AGG/'cases.csv').open(newline='') as stream:
        cases = list(csv.DictReader(stream))
    with (AGG/'history.csv').open(newline='') as stream:
        history_rows = sum(1 for _ in csv.DictReader(stream))
    f = lambda row, key: float(row[key])
    stats = {}
    for key in ('final_signed_Sigma','final_Sigma_half','final_signed_Pi_m',
                'final_signed_Pi_r','final_signed_Pi_total','final_Pi_m_half',
                'final_Pi_r_half','final_Pi_total_half','final_Tgas_K','final_x_HII'):
        stats[key] = span(f(row,key) for row in cases)
    changes = {key: span(f(r,'final_'+key)-f(r,'initial_'+key) for r in cases)
               for key in ('signed_Sigma','signed_Pi_m','signed_Pi_r','signed_Pi_total')}
    sigmas = sorted({f(r,'signed_Sigma_requested') for r in cases})
    thermo = {str(s): {k: span(f(r,k) for r in cases if f(r,'signed_Sigma_requested') == s)
                       for k in ('final_Tgas_K','final_x_HII')} for s in sigmas}
    cancel = [r for r in cases if f(r,'signed_Pi_m_requested')+f(r,'signed_Pi_r_requested') == 0]
    nonzero = [r for r in cancel if f(r,'signed_Pi_m_requested') != 0]
    zero_shear = [r for r in nonzero if f(r,'signed_Sigma_requested') == 0]
    keys = ('case_id','signed_Sigma_requested','signed_Pi_m_requested','signed_Pi_r_requested',
            'initial_signed_Sigma','initial_signed_Pi_m','initial_signed_Pi_r',
            'initial_signed_Pi_total','initial_Pi_component_norm_sum',
            'final_signed_Sigma','final_signed_Pi_m','final_signed_Pi_r','final_signed_Pi_total',
            'final_Pi_total_half','final_Tgas_K','final_x_HII')
    selected = [{k: r[k] if k=='case_id' else float(r[k]) for k in keys}
                for r in cases if f(r,'signed_Sigma_requested') == 0 and
                f(r,'signed_Pi_m_requested') in (0,-.0004,.0004) and
                f(r,'signed_Pi_r_requested') in (0,-.0004,.0004)]
    metric = {'schema':'rei.split.metrics.v1', 'scope':'descriptive existing finite pilot outputs; no convergence or performance inference',
              'case_count':len(cases),'history_rows':history_rows,'group_count':len(receipts),
              'stored_gate_count':len(gate_values),'stored_false_gates':sum(v is not True for v in gate_values),
              'ranges':stats,'changes_from_actual_initial':changes,'thermochemistry_by_initial_signed_Sigma':thermo,
              'nominal_cancellation': {'count':len(cancel),'nonzero_components':len(nonzero),
                  'nonzero_components_final_total':span(f(r,'final_Pi_total_half') for r in nonzero),
                  'zero_shear_nonzero_count':len(zero_shear),
                  'zero_shear_final_total':span(f(r,'final_Pi_total_half') for r in zero_shear),
                  'zero_shear_final_Sigma':span(f(r,'final_Sigma_half') for r in zero_shear)},
              'selected_zero_shear_cases':selected,
              'numeric_checks_max':{k:max(f(r,k) for r in cases) for k in ('Pi_m_initial_abs','Pi_r_initial_abs',
                  'signed_Pi_total_initial_abs','Sigma_initial_abs','photochemical_number_abs_max',
                  'photochemical_energy_eV_H_abs_max','gamma_number_monopole_abs_max','nu_number_monopole_abs_max')},
              'inputs':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in (AGG/'cases.csv',AGG/'history.csv',AGG/'summary.json')}}
    (AGG/'METRICS.json').write_text(json.dumps(metric,indent=2,sort_keys=True,allow_nan=False)+'\n')
    executions = []
    for directory in sorted((RUN/'scope/executions').iterdir()):
        policy = read(directory/'execution_policy.json')
        outcome = read(directory/'summary.json')
        obs = [json.loads(line) for line in (directory/'resource_observations.jsonl').read_text().splitlines()]
        executions.append({'directory':str(directory.relative_to(LANE)), 'status':outcome['status'],
            'job_status_counts':dict(Counter(j['status'] for j in outcome['jobs'])),
            'profile':policy['profile'],'profile_limits':policy['profile_limits'],
            'max_workers':policy['max_workers'],'nested_threads':policy['nested_threads'],
            'started_at':policy['started_at'],'finished_at':outcome['finished_at'],
            'maximum_observed_active_jobs':max(o['active_jobs'] for o in obs),
            'minimum_observed_filesystem_free_bytes':min(o['disk_observation']['filesystem_free_bytes'] for o in obs),
            'maximum_observed_scope_bytes':max(o['disk_observation']['scope_bytes'] for o in obs),
            'max_scope_bytes':policy['max_scope_bytes'],
            'observed_cpu_quota_cores':sorted({o['snapshot']['cpu_quota_cores'] for o in obs})})
    observation = {'schema':'rei.split.execution_observations.v1','created_at_utc':datetime.now(timezone.utc).isoformat(),
        'status':'PASS_EXISTING_OUTPUT_INTEGRITY' if not issues else 'FAIL', 'issues':issues,
        'science_execution_source':'82372ed8db68085868603d4267a630ed9cde6abb',
        'science_binding':summary['science_binding'], 'bound_files_count':len(bound),'bound_files':bound,
        'coverage':{'manifest_jobs':len(manifest['jobs']),'unique_receipts':len(receipts),
            'receipt_status_counts':dict(Counter(r['status'] for r in receipts)),
            'raw_cases':len(raw_case_ids),'unique_raw_cases':len(set(raw_case_ids)),
            'aggregate_cases':len(cases),'aggregate_history_rows':history_rows,
            'false_stored_gates':sum(v is not True for v in gate_values),'stored_gates':len(gate_values)},
        'executions':executions,'ncp_execution_this_turn':False,
        'performance':'No controlled timing benchmark, speedup or peak-memory claim; RSS samples can miss short workers.',
        'artifacts':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(AGG.iterdir()) if p.is_file()}}
    (LANE/'evidence/SPLIT_EXECUTION_OBSERVATIONS.json').write_text(json.dumps(observation,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':observation['status'],'coverage':observation['coverage'],
                     'bound_files':len(bound),'executions':executions,'metrics':metric['numeric_checks_max']}))


if __name__ == '__main__':
    main()
