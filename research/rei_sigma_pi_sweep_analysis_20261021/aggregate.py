#!/usr/bin/env python3
"""Portable saved-result aggregation; supplied plan owns the candidate set."""
from __future__ import annotations
import argparse
import copy
import csv
import json
import math
from pathlib import Path
import sys

LANE = Path(__file__).resolve().parent
ACCEL = LANE.parent / 'rei_sigma_pi_acceleration_20261021'
if str(ACCEL) not in sys.path:
    sys.path.insert(0, str(ACCEL))
import work_plan as wp
from diagnostics import row_diagnostics, matched_controls

GATES = {'number_5e-12', 'energy_5e-11', 'gamma_monopole_3e-9', 'nu_monopole_3e-9',
         'initial_mapping_3e-13', 'positive_matter_P2', 'positive_radiation_P2', 'finite_success_json'}
LIMITS = {'photochemical_number_abs_max': 5e-12, 'photochemical_energy_eV_H_abs_max': 5e-11,
          'gamma_number_monopole_abs_max': 3e-9, 'nu_number_monopole_abs_max': 3e-9}
META = ('science_id', 'science_context_id', 'source_id', 'backend', 'toolchain_id', 'toolchain_json',
        'nsteps', 'cohort_id', 'origin', 'history_available')


class InputIntegrityError(ValueError):
    pass


class PhysicsError(ValueError):
    pass


def require(condition, message, *, physics=False):
    if not condition:
        raise (PhysicsError if physics else InputIntegrityError)(message)


def load(path):
    return json.loads(Path(path).read_text())


def finite_tree(value):
    if isinstance(value, float):
        require(math.isfinite(value), 'NONFINITE_SCIENTIFIC_VALUE')
    elif isinstance(value, dict):
        for item in value.values(): finite_tree(item)
    elif isinstance(value, list):
        for item in value: finite_tree(item)


def read_plan(plan_path, baseline=wp.BASELINE):
    plan = load(plan_path)
    registry = wp.load_completed_registry(baseline)
    require(plan.get('schema') == 'rei.split.pending_work_plan.v1', 'PLAN_SCHEMA')
    require(plan['science_context'] == registry['context'] and plan['science_context_id'] == registry['context_id']
            and plan['evidence_sources'] == registry['evidence_sources'], 'PLAN_SCIENCE_CONTEXT')
    require(plan['execution_id'] == wp.identity(plan['execution']), 'PLAN_EXECUTION_ID')
    require(plan['completed_count'] == len(plan['completed']) and plan['pending_count'] == len(plan['pending'])
            and plan['candidate_count'] == plan['completed_count']+plan['pending_count'], 'PLAN_COUNTS')
    known = {r['science_id']: r for r in registry['records'].values()}
    completed, pending = {}, {}
    for item in plan['completed']:
        original = known.get(item['science_id'])
        require(original is not None and item['evidence'] == original['evidence'], 'UNVERIFIED_COMPLETION')
        case = {**original['case'], 'case_id': item['case_id']}
        require(item['science_id'] not in completed, 'DUPLICATE_COMPLETION')
        completed[item['science_id']] = {**original, 'case': case}
    for item in plan['pending']:
        case, science, seed = item['case'], item['science'], item['seed']
        require(science['schema'] == 'rei.split.case_science.v1' and item['science_id'] == wp.identity(science), 'PENDING_SCIENCE_ID')
        require(science['context_id'] == registry['context_id'] and science['case'] == {k:v for k,v in case.items() if k != 'case_id'}, 'PENDING_CASE_BINDING')
        require(type(science['nsteps']) is int and 2 <= science['nsteps'] <= 1024 and science['compress'] is True and science['feedback'] is True, 'PENDING_STEPS_OR_POLICY')
        expected = {**registry['context']['parameter_defaults'], 'Sigma_initial': case[wp.MAGNITUDES[0]],
                    'orientation': case[wp.SIGNS[0]], 'massive_quadrupole': seed['alpha_m'],
                    'gamma_quadrupole': seed['alpha_r'], 'nu_quadrupole': seed['alpha_r']}
        require(science['parameters'] == expected and set(science['toolchain']) == {'python', 'numpy', 'scipy'}, 'PENDING_PARAMETERS_OR_TOOLCHAIN')
        require(-1 <= seed['alpha_m'] <= 2 and -1 <= seed['alpha_r'] <= 2, 'PENDING_SEED_POSITIVITY', physics=True)
        require(item['science_id'] not in pending and item['science_id'] not in completed, 'DUPLICATE_SCIENCE_ID')
        pending[item['science_id']] = item
    wp.validate_cases([r['case'] for r in [*completed.values(), *pending.values()]])
    finite_tree(plan)
    return plan, registry, completed, pending


def read_manifest(path, plan_path, plan, pending):
    manifest = load(path)
    binding = manifest['science_binding']
    require(manifest['schema'] == 'rei.shared_case_science.v1', 'MANIFEST_SCHEMA')
    require(manifest['completion_reuse'] == {'completed': plan['completed_count'], 'pending': len(pending),
                                           'source_plan_sha256': wp.file_hash(plan_path)}, 'MANIFEST_PLAN_BINDING')
    require(binding['input'] == wp.identity({'context': plan['science_context_id'], 'cases': sorted(pending)}), 'MANIFEST_INPUT_BINDING')
    require(binding['toolchain'] == wp.identity(manifest['toolchain']), 'MANIFEST_TOOLCHAIN_BINDING')
    require(manifest['split_pilot']['case_count'] == len(pending), 'MANIFEST_PENDING_COUNT')
    for record in pending.values():
        require(record['science']['toolchain'] == manifest['toolchain'] and record['science']['nsteps'] == manifest['split_pilot']['nsteps'], 'MANIFEST_RECORDED_TOOLCHAIN_OR_STEPS')
    require(isinstance(binding['source'], str) and len(binding['source']) == 64, 'MANIFEST_SOURCE_ID')
    return manifest


def numeric(row, key):
    value = row[key]
    require(type(value) in (int, float) and math.isfinite(value), 'MALFORMED_SCIENTIFIC_ROW: '+key)
    return value


def validate_case(result, record, source_identity):
    split, _ = wp.modules()
    finite_tree(result)
    owner = result['owner_result']
    require(result['case'] == record['case'] and result['seed'] == record['seed'], 'CASE_OR_SEED_MISMATCH')
    require(owner['schema'] == 'rei.c15.active_source_shear_stress_coupling.v1'
            and owner['config'] == record['science']['parameters'] and owner['source_identity'] == source_identity, 'OWNER_SOURCE_OR_CONFIG')
    require(set(result['gates']) == GATES and all(v is True for v in result['gates'].values()), 'ORIGINAL_PHYSICS_GATE_FAILED', physics=True)
    nsteps = record['science']['nsteps']
    require(owner['nsteps'] == nsteps and len(owner['history']) == nsteps, 'OWNER_STEP_COUNT')
    require(result['initial']['a'] == .1999 and owner['history'][-1]['a'] == .2 and owner['final'] == owner['history'][-1], 'OWNER_INTERVAL_OR_FINAL')
    rows = [result['initial'], *owner['history']]
    require(all(a['a'] < b['a'] for a, b in zip(rows, rows[1:])), 'HISTORY_TIME_ORDER')
    for row in rows:
        for name in ('a', 'H', 'Tgas_K', 'x_HII', 'x_HeII', 'nerr', 'eerr', 'gamma_number_N0', 'nu_number_N0',
                     'signed_Sigma', 'signed_Pi_m', 'signed_Pi_r', 'signed_Pi_total'):
            numeric(row, name)
        require(row['H'] > 0 and 10000 <= row['Tgas_K'] <= 24000 and 0 <= row['x_HII'] <= 1 and 0 <= row['x_HeII'] <= 1, 'CASE_PHYSICAL_DOMAIN', physics=True)
    # Existing pure initial mapping function, with unchanged 3e-13 criterion.
    try:
        checks = split.initial_checks(record['case'], result['initial'])
    except RuntimeError as error:
        raise PhysicsError(str(error)) from error
    require(result['numeric_checks'] == checks, 'INITIAL_MAPPING_REDUCTION')
    errors = {'photochemical_number_abs_max': max(row['nerr'] for row in owner['history']),
              'photochemical_energy_eV_H_abs_max': max(row['eerr'] for row in owner['history']),
              'gamma_number_monopole_abs_max': max(abs(row['gamma_number_N0']-1) for row in owner['history']),
              'nu_number_monopole_abs_max': max(abs(row['nu_number_N0']-1) for row in owner['history'])}
    require(owner['errors'] == errors, 'ERROR_REDUCTION_MISMATCH')
    require(all(0 <= errors[k] <= limit for k, limit in LIMITS.items()), 'ORIGINAL_ERROR_LIMIT_FAILED', physics=True)
    require(-1 <= record['seed']['alpha_m'] <= 2 and -1 <= record['seed']['alpha_r'] <= 2, 'ORIGINAL_POSITIVITY_FAILED', physics=True)
    calibration = result['calibration']
    require(all(type(v) in (int, float) and math.isfinite(v) and v > 0 for v in calibration.values()), 'INVALID_CALIBRATION')
    return rows


def metadata(record, plan, source, backend, toolchain, origin, history_available):
    steps = record['science']['nsteps']
    cohort = {'source': source, 'backend': backend, 'toolchain': toolchain, 'nsteps': steps,
              'science_context_id': plan['science_context_id'], 'a_start': .1999, 'a_end': .2}
    return {**record['case'], 'science_id': record['science_id'], 'science_context_id': plan['science_context_id'],
            'source_id': source, 'backend': backend, 'toolchain_id': wp.identity(toolchain),
            'toolchain_json': wp.canonical(toolchain).decode(), 'nsteps': steps, 'cohort_id': wp.identity(cohort),
            'origin': origin, 'history_available': history_available}


def csv_value(value):
    if value in ('True', 'False'): return value == 'True'
    try:
        number = float(value)
        require(math.isfinite(number), 'NONFINITE_ARCHIVED_FIELD')
        return number
    except ValueError:
        if value.lower() in ('nan', 'inf', '-inf', 'infinity', '-infinity'):
            raise InputIntegrityError('NONFINITE_ARCHIVED_FIELD')
        return value


def write_csv(path, rows, default_fields):
    fields = list(dict.fromkeys([*default_fields, *(k for row in rows for k in row)]))
    with Path(path).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def aggregate(plan_path, out, *, manifest_path=None, scopes=(), results=(), baseline=wp.BASELINE):
    plan_path, out, baseline = Path(plan_path), Path(out), Path(baseline)
    plan, registry, completed, pending = read_plan(plan_path, baseline)
    split, _ = wp.modules()
    manifest = read_manifest(manifest_path, plan_path, plan, pending) if manifest_path else None
    require(not (scopes or results) or manifest is not None, 'PENDING_RESULTS_REQUIRE_MANIFEST')
    routes, paths = [], []
    for scope in scopes:
        for path in split.prior.result_paths_from_scope(scope):
            paths.append(path)
            routes.append({'path': str(path.resolve()), 'route': 'executor_success_receipt', 'scope': str(Path(scope).resolve())})
    for path in results:
        paths.append(Path(path))
        routes.append({'path': str(Path(path).resolve()), 'route': 'explicit_result_import'})
    successful, duplicates, origins = {}, [], {}
    pending_labels = {r['case']['case_id']: sid for sid, r in pending.items()}
    source_identity = split.prior.load_owner().source_identity()
    for path in paths:
        group = load(path)
        require(group.get('schema') == 'rei.sigma_pi_split.group_result.v1' and group.get('status') == 'SUCCEEDED', 'GROUP_SCHEMA_OR_STATUS')
        require(group['science_binding'] == manifest['science_binding'] and group['owner_ref'] == split.OWNER_REF, 'GROUP_SCIENCE_BINDING')
        require(group['nsteps'] == manifest['split_pilot']['nsteps'], 'GROUP_NSTEPS')
        for scientific in group['cases']:
            label = scientific['case']['case_id']
            require(label in pending_labels, 'UNEXPECTED_CASE: '+label)
            sid = pending_labels[label]
            validate_case(scientific, pending[sid], source_identity)
            if sid in successful:
                require(wp.canonical(successful[sid]) == wp.canonical(scientific), 'CONFLICTING_SCIENTIFIC_DUPLICATE: '+label)
                duplicates.append({'science_id': sid, 'first': origins[sid], 'duplicate': str(path.resolve())})
            else:
                successful[sid] = scientific
                origins[sid] = str(path.resolve())
    endpoints, histories, diagnostic_rows = [], [], []
    def diagnose(row, meta, label, kappa=None):
        diag, arithmetic = row_diagnostics(row, kappa)
        require(diag['diag_arithmetic_pass'], 'COMPONENT_SCALED_ARITHMETIC_FAILED: '+meta['case_id']+'/'+str(label), physics=True)
        diagnostic_rows.append({'case_id': meta['case_id'], 'science_id': meta['science_id'],
                                'sample': label, 'diagnostics': diag, 'arithmetic': arithmetic})
        return diag
    with (baseline / wp.CASES).open(newline='') as stream:
        archived = {row['case_id']: row for row in csv.DictReader(stream)}
    for sid, record in completed.items():
        row = {k: csv_value(v) for k,v in archived[record['evidence']['csv_case_id']].items()}
        row.update(record['case'])
        meta = metadata(record, plan, wp.SOURCE_SHA, 'archived-owner-c15', record['science']['toolchain'], 'reused_completed', False)
        row.update(meta)
        for prefix in ('initial', 'final'):
            sample = {k[len(prefix)+1:]:v for k,v in row.items() if k.startswith(prefix+'_')}
            diag = diagnose(sample, meta, prefix)
            row.update({prefix+'_'+k:v for k,v in diag.items()})
        endpoints.append(row)
    for sid, scientific in successful.items():
        record = pending[sid]
        meta = metadata(record, plan, manifest['science_binding']['source'], plan['execution']['backend'],
                        manifest['toolchain'], 'successful_pending', True)
        row = {**meta, 'alpha_m': record['seed']['alpha_m'], 'alpha_r': record['seed']['alpha_r'],
               **scientific['numeric_checks'], **scientific['owner_result']['errors']}
        rows = [scientific['initial'], *scientific['owner_result']['history']]
        for step, sample in enumerate(rows):
            diag = diagnose(sample, meta, step, scientific['calibration']['kappa_time'])
            histories.append({**meta, 'step': step, **split.prior.scalar_row(sample), **diag})
            if step == 0:
                row.update({'initial_'+k:v for k,v in {**split.prior.scalar_row(sample), **diag}.items()})
            if step == record['science']['nsteps']:
                row.update({'final_'+k:v for k,v in {**split.prior.scalar_row(sample), **diag}.items()})
        endpoints.append(row)
    endpoints.sort(key=lambda r:r['case_id'])
    histories.sort(key=lambda r:(r['case_id'], r['step']))
    matched_controls(endpoints)
    missing = [{'science_id': sid, 'case_id': r['case']['case_id']} for sid,r in pending.items() if sid not in successful]
    cohorts = {}
    for row in endpoints:
        cohorts.setdefault(row['cohort_id'], {key:row[key] for key in ('origin','source_id','backend','toolchain_id','toolchain_json','nsteps','history_available')})
    summary = {'schema': 'rei.sweep_analysis.summary.v1', 'status': 'PARTIAL' if missing else 'COMPLETE',
               'admission': 'PENDING_INDEPENDENT_REVIEW', 'expected_count': plan['candidate_count'],
               'reused_completed_count': len(completed), 'successful_pending_count': len(successful),
               'missing_pending_count': len(missing), 'case_count': len(endpoints), 'history_rows': len(histories),
               'missing_pending': missing, 'cohorts': cohorts, 'scientific_duplicate_count': len(duplicates),
               'science_context_id': plan['science_context_id'], 'arithmetic_checks_pass': True}
    provenance = {'schema': 'rei.sweep_analysis.provenance.v1', 'plan': {'path': str(plan_path.resolve()), 'sha256': wp.file_hash(plan_path)},
                  'manifest': {'path': str(Path(manifest_path).resolve()), 'sha256': wp.file_hash(manifest_path)} if manifest_path else None,
                  'results': [{**route, 'sha256': wp.file_hash(route['path'])} for route in routes],
                  'duplicates': duplicates, 'archived_baseline': {'path': str((baseline/wp.CASES).resolve()), 'sha256': wp.file_hash(baseline/wp.CASES)},
                  'source_identity': source_identity, 'analyst_runtime_is_not_a_result_validation_gate': True}
    out.mkdir(parents=True, exist_ok=True)
    write_csv(out/'cases.csv', endpoints, ['case_id', *META])
    write_csv(out/'history.csv', histories, ['case_id', *META, 'step', 'a', 'signed_Sigma', 'signed_Pi_m', 'signed_Pi_r', 'signed_Pi_total'])
    for name, value in (('summary.json',summary),('provenance.json',provenance),('diagnostics.json',diagnostic_rows)):
        (out/name).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')
    (out/'diagnosis.json').unlink(missing_ok=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', required=True, type=Path)
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--scope', action='append', type=Path, default=[])
    parser.add_argument('--result', action='append', type=Path, default=[])
    parser.add_argument('--baseline', type=Path, default=wp.BASELINE)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    try:
        summary = aggregate(args.plan, args.out, manifest_path=args.manifest, scopes=args.scope, results=args.result, baseline=args.baseline)
    except (ValueError, KeyError, TypeError, OSError) as error:
        args.out.mkdir(parents=True, exist_ok=True)
        diagnosis = {'status': 'INPUT_REJECTED', 'category': type(error).__name__, 'message': str(error)}
        (args.out/'diagnosis.json').write_text(json.dumps(diagnosis, indent=2)+'\n')
        print(json.dumps(diagnosis), file=sys.stderr)
        return 2
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
