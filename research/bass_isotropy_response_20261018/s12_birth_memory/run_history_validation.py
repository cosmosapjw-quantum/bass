#!/usr/bin/env python3
"""One preregistered NEW S12 history validation; no completed campaign replay.

All children use process_control.run_owned. The standalone assessor observes
receipts without running an integrator. This runner separately performs the
registered FD, independent reference, driver, fused-mode and omission checks.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import traceback

import numpy as np

import assess_history as observer
from process_control import atomic_json, run_owned
import reference as ref

HERE = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n').encode()


def selected_states(rows, times):
    by_time = {}
    for row in rows:
        if row['x'] in by_time:
            raise ValueError('DUPLICATE_OBSERVATION_TIME')
        by_time[row['x']] = row['state']
    values = np.asarray([by_time[x] for x in times], dtype=float)
    if values.shape != (len(times), 6) or not np.isfinite(values).all():
        raise ValueError('SELECTED_STATE_DOMAIN')
    return values


def scaled(actual, expected):
    a, b = np.asarray(actual, dtype=float), np.asarray(expected, dtype=float)
    if a.shape != b.shape or not a.size or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError('COMPARISON_FINITE_SHAPE')
    den = 1+np.maximum(np.abs(a), np.abs(b))
    if not np.isfinite(den).all() or np.min(den) <= 0:
        raise ValueError('COMPARISON_DENOMINATOR')
    return float(np.max(np.abs(a-b)/den))


def python_child(path):
    """Executed only in its separately limited child process."""
    inp = json.loads(Path(path).read_bytes())
    result = ref.python_history(inp)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, allow_nan=False)+'\n')
    sys.stdout.flush()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binary', type=Path, required=True)
    p.add_argument('--source-commit', required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    binary, out = a.binary.resolve(), a.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    records, checks, assessments = [], [], {}
    receipts, inputs, input_bytes = {}, {}, {}
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    error = None;binary_hash = None
    atomic_json(out/'EXECUTIONS.json', records)
    atomic_json(out/'CHECKS.json', checks)

    def check(name, passed, **details):
        checks.append({'name': name, 'pass': bool(passed), **observer.clean(details)})
        atomic_json(out/'CHECKS.json', checks)

    def execute(tag, kind, argv, data, *, input_file_hash=None, timeout_s=1800):
        stdin = b'' if data is None else data
        (out/(tag+'.stdin')).write_bytes(stdin)
        record = {'tag': tag, 'kind': kind, 'source_commit': a.source_commit,
                  'status': 'LAUNCH_PENDING', 'argv': list(map(str, argv)),
                  'stdin_path': str(out/(tag+'.stdin')),
                  'stdin_sha256': sha(stdin), 'reference_input_file_sha256': input_file_hash}
        index = len(records);records.append(record)
        atomic_json(out/'EXECUTIONS.json', records)
        env = os.environ.copy()
        env.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1',
                   RAYON_NUM_THREADS='1', NUMEXPR_NUM_THREADS='1')
        actual = run_owned(argv, stdout_path=out/(tag+'.stdout'), stderr_path=out/(tag+'.stderr'),
            receipt_path=out/(tag+'.process.json'), timeout_s=timeout_s, stdin_bytes=data,
            cwd=HERE, env=env, as_bytes=2*1024**3, file_bytes=256*1024**2)
        record.update(actual)
        record['tag'] = tag;record['kind'] = kind;record['source_commit'] = a.source_commit
        record['executable_sha256'] = sha(Path(argv[0]).read_bytes()) if Path(argv[0]).is_file() else None
        records[index] = record
        atomic_json(out/'EXECUTIONS.json', records)
        check(tag+'_process', actual['status'] == 'EXITED' and actual['exit_code'] == 0,
              process_status=actual['status'], exit_code=actual['exit_code'])
        raw = (out/(tag+'.stdout')).read_bytes() if (out/(tag+'.stdout')).exists() else b''
        stderr = (out/(tag+'.stderr')).read_bytes() if (out/(tag+'.stderr')).exists() else b''
        if actual['status'] != 'EXITED' or actual['exit_code'] != 0:
            raise RuntimeError(tag+':PROCESS_'+actual['status']+':'+str(actual['exit_code']))
        return raw, stderr

    def history(tag, inp, *, checkpoint=None, resume=None):
        if sha(binary.read_bytes()) != binary_hash:
            raise RuntimeError('BINARY_CHANGED_BETWEEN_CALLS')
        data = encoded(inp);inputs[tag] = inp;input_bytes[tag] = data
        (out/(tag+'.input.json')).write_bytes(data)
        argv = [binary, '--source-commit', a.source_commit, '--input-sha256', sha(data)]
        if checkpoint is not None:
            argv += ['--checkpoint', checkpoint]
        if resume is not None:
            argv += ['--resume', resume]
        raw, stderr = execute(tag, 'rust_history_final_resume' if resume else 'rust_history',
                              argv, data)
        receipt = json.loads(raw)
        process_status = json.loads(stderr)
        check(tag+'_structured_process_status',
              process_status.get('schema') == 'BASS_S12_PROCESS_STATUS_V1'
              and process_status.get('status') == 'completed'
              and process_status.get('binding') == receipt.get('binding')
              and process_status.get('segments') == len(receipt.get('segments', []))
              and process_status.get('admitted_births') == len(receipt.get('events', []))
              and process_status.get('observations') == len(receipt.get('observations', [])))
        assessment = observer.assess(inp, receipt, input_sha256=sha(data),
                                    source_commit=a.source_commit, binary_sha256=binary_hash)
        assessment.update(input_file_sha256=sha(data), receipt_file_sha256=sha(raw),
                          process_receipt_sha256=sha((out/(tag+'.process.json')).read_bytes()))
        atomic_json(out/(tag+'.assessment.json'), assessment)
        assessments[tag] = assessment;receipts[tag] = receipt
        if inp['control'] == 'full':
            check(tag+'_internal_scientific_gates', assessment['full_scientific_pass'],
                  internal_checks_passed=assessment['checks_passed'], total=assessment['checks_total'],
                  status=assessment['status'])
        else:
            check(tag+'_control_structural_validity',
                  assessment['execution_completed'] and assessment['structural_pass']
                  and assessment['status'] == 'OMISSION_CONTROL_OBSERVED'
                  and assessment['full_scientific_pass'] is False,
                  numerical_gates_pass=assessment['numerical_gates_pass'],
                  expected_not_full_pass=True)
        return receipt, assessment

    try:
        if len(a.source_commit) != 40 or any(c not in '0123456789abcdef' for c in a.source_commit):
            raise ValueError('SOURCE_COMMIT_FORMAT')
        binary_hash = sha(binary.read_bytes())
        prereg = json.loads((HERE/'PREREGISTRATION.json').read_bytes())
        tracked = ['run_history_validation.py', 'assess_history.py', 'reference.py',
                   'process_control.py', 'PREREGISTRATION.json', 'CONTRACT.json',
                   'src/core.rs', 'src/birth.rs', 'src/history.rs', 'src/main.rs', 'Cargo.toml', 'Cargo.lock']
        identity = {'schema': 'BASS_S12_HISTORY_VALIDATION_IDENTITY_V1',
            'source_commit': a.source_commit, 'binary_path': str(binary),
            'binary_sha256': binary_hash, 'python_executable': sys.executable,
            'python_executable_sha256': sha(Path(sys.executable).read_bytes()),
            'source_file_sha256': {path: sha((HERE/path).read_bytes()) for path in tracked},
            'preregistration_recorded_before_execution': prereg['recorded_before_scientific_execution'],
            'started_utc': started, 'old_campaign_calls': 0}
        atomic_json(out/'RUN_IDENTITY.json', identity)
        primary_input = ref.history_input()
        check('fixed_preregistered_config', primary_input['config'] == prereg['histories']['config'])
        check('fixed_preregistered_solver', primary_input['solver']['arm'] == prereg['histories']['primary_driver']
              and primary_input['solver']['rtol'] == prereg['histories']['rtol']
              and primary_input['solver']['atol'] == prereg['histories']['atol']
              and primary_input['solver']['max_step'] == prereg['histories']['max_step'])
        final_checkpoint = out/'primary_final.checkpoint.json'
        primary, primary_assessment = history('p24_y0_full', primary_input, checkpoint=final_checkpoint)
        if not primary_assessment['full_scientific_pass']:
            raise RuntimeError('PRIMARY_INTERNAL_GATES_FAILED')
        gl, _ = history('gl_y0_full', ref.history_input(rule='source_frame_GL'))
        gauge, _ = history('gl_b0_gauge', ref.history_input(rule='source_frame_GL', parameter='b0'))
        mf, _ = history('p24_y0_mf6', ref.history_input(arm='mf_into_ls6'))
        baseline, baseline_assessment = history('p24_y0_baseline', ref.history_input(mode='baseline'))
        times = primary_input['output_times']
        full = selected_states(primary['observations'], times)
        mf_values = selected_states(mf['observations'], times)
        baseline_values = selected_states(baseline['observations'], times)
        driver_gate = prereg['histories']['MF6_clock7_state6_scaled_gate']
        fused_gate = prereg['histories']['baseline_fused_history_state6_scaled_gate']
        driver_error = scaled(mf_values, full);fused_error = scaled(baseline_values, full)
        check('MF6_clock7_state6', driver_error <= driver_gate, scaled_error=driver_error, gate=driver_gate)
        check('baseline_fused_history_state6', fused_error <= fused_gate,
              scaled_error=fused_error, gate=fused_gate,
              state6_binary64_equal=np.array_equal(baseline_values, full))
        primary_gates = {v['name']: v['pass'] for v in primary_assessment['checks'] if v['category'] == 'numerical'}
        baseline_gates = {v['name']: v['pass'] for v in baseline_assessment['checks'] if v['category'] == 'numerical'}
        check('baseline_fused_scientific_gate_identity', primary_gates == baseline_gates
              and all(primary_gates.values()))

        # One independent DOP853 history. The child has the same fixed input bytes.
        py_tag = 'python_p24_reference'
        raw, _ = execute(py_tag, 'independent_python_reference',
                         [sys.executable, Path(__file__).resolve(), '--python-reference-child',
                          out/'p24_y0_full.input.json'], None,
                         input_file_hash=sha(input_bytes['p24_y0_full']))
        py = json.loads(raw);atomic_json(out/'PYTHON_REFERENCE.json', py)
        check('independent_reference_identity', py.get('schema') == 'BASS_S12_NEW_PYTHON_REFERENCE_V1'
              and py.get('method') == 'DOP853' and py.get('old_S8_campaign_invoked') is False
              and py.get('nfev', 0) > 0)
        check('independent_reference_fixed_events',
              [e['x'] for e in py['events']] == [e['u'] for e in primary['events']])
        py_values = selected_states(py['state_rows'], times)
        python_error = scaled(full, py_values)
        python_gate = prereg['histories']['Python_Rust_state6_scaled_gate']
        check('independent_python_Rust_state6', python_error <= python_gate,
              scaled_error=python_error, gate=python_gate)
        atomic_json(out/'CROSS_IMPLEMENTATION.json', {'output_times': times,
            'Rust_state6': full.tolist(), 'Python_state6': py_values.tolist(),
            'MF6_state6': mf_values.tolist(), 'baseline_state6': baseline_values.tolist(),
            'Python_Rust_scaled': python_error, 'MF6_clock7_scaled': driver_error,
            'baseline_fused_scaled': fused_error})

        # Six preregistered new perturbation runs; fixed old physical stock,
        # fixed donor law, event coordinates, angular rule and solver settings.
        steps = [1e-4, 5e-5, 2.5e-5]
        estimates = []
        for h in steps:
            pair = []
            for sign, label in [(1, 'plus'), (-1, 'minus')]:
                inp = deepcopy(primary_input);inp['config']['y0'] += sign*h
                tag = 'fd_'+format(h, '.1e').replace('.', 'p').replace('-', 'm')+'_'+label
                result, _ = history(tag, inp)
                pair.append(selected_states(result['observations'], times)[:, :3])
                comparison = deepcopy(inp);comparison['config']['y0'] = primary_input['config']['y0']
                check(tag+'_fixed_all_other_data', comparison == primary_input
                      and inp['expected_old_digests'] == primary_input['expected_old_digests'])
            denominator = 2*h
            check('FD_'+str(h)+'_positive_denominator', math.isfinite(denominator) and denominator > 0,
                  denominator=denominator)
            estimate = (pair[0]-pair[1])/denominator
            if not np.isfinite(estimate).all():
                raise ValueError('FD_NONFINITE')
            estimates.append(estimate)
        coarse_richardson = (4*estimates[1]-estimates[0])/3
        fine_richardson = (4*estimates[2]-estimates[1])/3
        tangent = full[:, 3:]
        richardson_error = float(np.max(np.abs(tangent-fine_richardson)))
        raw_scaled_error = scaled(tangent, estimates[2])
        richardson_gate = prereg['histories']['Richardson_h_b_y_max_absolute_gate']
        raw_gate = prereg['histories']['raw_fine_FD_scaled_gate']
        check('fine_Richardson_absolute_h_b_y', richardson_error <= richardson_gate,
              max_absolute_error=richardson_error, gate=richardson_gate)
        check('raw_fine_FD_scaled_h_b_y', raw_scaled_error <= raw_gate,
              max_scaled_error=raw_scaled_error, gate=raw_gate)
        fd_result = {'steps': steps, 'output_times': times, 'full_tangent': tangent.tolist(),
            'raw_centered_derivatives': [v.tolist() for v in estimates],
            'coarse_Richardson': coarse_richardson.tolist(), 'fine_Richardson': fine_richardson.tolist(),
            'fine_Richardson_error': (tangent-fine_richardson).tolist(),
            'fine_Richardson_max_absolute': richardson_error,
            'raw_fine_max_scaled': raw_scaled_error,
            'coarse_to_fine_Richardson_difference_max_absolute':
                float(np.max(np.abs(coarse_richardson-fine_richardson))),
            'old_completed_S8_Richardson_campaign_replayed': False}
        atomic_json(out/'FD_RICHARDSON.json', fd_result)

        controls = []
        for control in prereg['histories']['negative_controls']:
            inp = ref.history_input(control=control)
            result, assessment = history(control, inp)
            omitted = selected_states(result['observations'], times)[:, 3:]
            omission_error = float(np.max(np.abs(omitted-tangent)))
            omission_reference_error = float(np.max(np.abs(omitted-fine_richardson)))
            threshold = 10*richardson_error
            identified = math.isfinite(omission_error) and math.isfinite(threshold) and omission_error > threshold
            check(control+'_identified_against_full_error', identified,
                  full_vs_omitted_max_absolute=omission_error,
                  omitted_vs_Richardson_max_absolute=omission_reference_error,
                  full_vs_Richardson_max_absolute=richardson_error,
                  required_strict_lower_bound=threshold)
            controls.append({'control': control, 'identified': identified,
                'full_vs_omitted_max_absolute': omission_error,
                'omitted_vs_Richardson_max_absolute': omission_reference_error,
                'required_strict_lower_bound': threshold,
                'internal_numerical_gates_pass': assessment['numerical_gates_pass'],
                'full_scientific_pass': assessment['full_scientific_pass'],
                'tangent': omitted.tolist(),
                'failed_numerical_checks': [v for v in assessment['checks']
                                            if v['category'] == 'numerical' and not v['pass']]})
        atomic_json(out/'OMISSION_CONTROLS.json', controls)

        # Exact final-boundary restore only. This does not test interruption or
        # claim to have resumed a partly executed integration.
        checkpoint_before = final_checkpoint.read_bytes()
        checkpoint = json.loads(checkpoint_before)
        atomic_json(out/'FINAL_CHECKPOINT_IDENTITY.json', {
            'scope': 'final checkpoint serialization and same-source/input/binary restore only',
            'checkpoint_sha256': sha(checkpoint_before),
            'payload_sha256': checkpoint['payload_sha256'],
            'binding': checkpoint['payload']['binding'],
            'next_segment': checkpoint['payload']['next_segment'],
            'pending_event': checkpoint['payload']['pending_event']})
        check('final_checkpoint_boundary', checkpoint['payload']['pending_event'] is None
              and checkpoint['payload']['next_segment'] == len(primary['segments'])
              and checkpoint['payload']['begin'] == primary_input['config']['x_end']
              and checkpoint['payload']['receipt']['status'] == 'completed')
        resumed, resumed_assessment = history('final_checkpoint_resume', primary_input, resume=final_checkpoint)
        fields = ['binding', 'input', 'observations', 'events', 'segments', 'final_cohorts', 'old_stock_digests']
        check('final_checkpoint_scientific_bytes_restore',
              all(resumed[field] == primary[field] for field in fields)
              and resumed.get('resumed') is True
              and resumed['resume_boundary']['next_segment'] == len(primary['segments'])
              and resumed_assessment['full_scientific_pass'],
              scope='final completed-boundary restore; no intermediate-resume claim')
        check('final_checkpoint_file_unchanged', final_checkpoint.read_bytes() == checkpoint_before,
              sha256_before=sha(checkpoint_before), sha256_after=sha(final_checkpoint.read_bytes()))
        check('fixed_execution_cardinality',
              sum(r['kind'] == 'rust_history' for r in records) == 14
              and sum(r['kind'] == 'rust_history_final_resume' for r in records) == 1
              and sum(r['kind'] == 'independent_python_reference' for r in records) == 1,
              history_calls=sum(r['kind'] == 'rust_history' for r in records),
              final_resume_calls=sum(r['kind'] == 'rust_history_final_resume' for r in records),
              independent_reference_calls=sum(r['kind'] == 'independent_python_reference' for r in records))
    except Exception as exc:
        error = {'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()}
        atomic_json(out/'FAILURE.json', error)
        check('runner_completed_without_exception', False, **error)
    finally:
        summary = {'schema': 'BASS_S12_HISTORY_VALIDATION_V1',
            'status': 'PASS_SCOPED' if error is None and checks and all(v['pass'] for v in checks) else 'FAIL',
            'source_commit': a.source_commit, 'binary_sha256': binary_hash,
            'started_utc': started, 'ended_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
            'checks_passed': sum(v['pass'] for v in checks), 'checks_total': len(checks),
            'process_records': len(records), 'error': error, 'old_campaign_calls': 0,
            'scope': 'New short manufactured histories and exact final-checkpoint restore only; no native full spectral or actual NCP64 completion',
            'assessment_statuses': {tag: {'status': value['status'],
                'full_scientific_pass': value['full_scientific_pass'],
                'numerical_gates_pass': value['numerical_gates_pass']} for tag, value in assessments.items()}}
        atomic_json(out/'SUMMARY.json', summary)
        files = [{'path': str(path.relative_to(out)), 'bytes': path.stat().st_size,
                  'sha256': sha(path.read_bytes())} for path in sorted(out.rglob('*')) if path.is_file()
                 and path.name != 'ARTIFACT_MANIFEST.json']
        atomic_json(out/'ARTIFACT_MANIFEST.json', {'schema': 'BASS_S12_HISTORY_ARTIFACTS_V1',
            'source_commit': a.source_commit, 'manifest_excludes_itself': True, 'files': files})
        print(json.dumps({k: summary[k] for k in ['status', 'checks_passed', 'checks_total', 'process_records']},
                         allow_nan=False))
    return 0 if summary['status'] == 'PASS_SCOPED' else 1


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--python-reference-child':
        python_child(sys.argv[2])
    else:
        raise SystemExit(main())

