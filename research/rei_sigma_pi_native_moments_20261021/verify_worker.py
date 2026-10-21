#!/usr/bin/env python3
"""One extra real two-step case, then a fresh launched job reusing its checkpoint."""
from __future__ import annotations
import json
from pathlib import Path
import sys

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))
import native_worker as native
import batch_worker as worker
import work_plan as wp


def main():
    root = LANE / 'evidence' / 'worker'
    root.mkdir(parents=True, exist_ok=True)
    cases = json.loads((LANE / 'evidence' / 'CUSTOM_CASES.json').read_text())[:1]
    plan = wp.build_plan(cases=cases, nsteps=2, group_size=1, profile='ncp', backend=native.NAME)
    worker.write_json(root / 'plan.json', plan)
    prepared = native.prepare(root / 'plan.json', root / 'prepared', root / 'case_store', 1)
    worker.write_json(root / 'prepare_receipt.json', prepared)
    input_path = next((root / 'prepared' / 'inputs').glob('*.json'))
    try:
        worker.run_group(input_path, root / 'wrong_backend.json')
    except ValueError as error:
        if str(error) != 'NUMERIC_BACKEND_SELECTION_MISMATCH':
            raise
        mismatch = str(error)
    else:
        raise AssertionError('WRONG_NUMERIC_BACKEND_ACCEPTED')
    _, executor = wp.modules()
    first = executor.run(root / 'prepared' / 'manifest.json', root / 'scope_first', profile='ncp',
                         max_workers=2, resource_wait_s=30, poll_s=.1, reserve_mb=256)
    worker.write_json(root / 'execution_first.json', first)
    if first['status'] != 'COMPLETE':
        raise AssertionError('FIRST_EXECUTOR_INCOMPLETE')
    result_path = next((root / 'scope_first' / 'jobs').rglob('result.json'))
    original = json.loads(result_path.read_text())
    if original['case_cache'][0]['reused']:
        raise AssertionError('FIRST_EXECUTION_UNEXPECTED_REUSE')
    receipt_path = next((root / 'case_store').rglob('receipt.json'))
    before = receipt_path.read_bytes()
    # A distinct executor scope actually starts a new worker process; the case
    # namespace must reuse its stored case rather than invoke the solver again.
    second = executor.run(root / 'prepared' / 'manifest.json', root / 'scope_second', profile='ncp',
                          max_workers=2, resource_wait_s=30, poll_s=.1, reserve_mb=256)
    worker.write_json(root / 'execution_second.json', second)
    if second['status'] != 'COMPLETE':
        raise AssertionError('SECOND_EXECUTOR_INCOMPLETE')
    result_path = next((root / 'scope_second' / 'jobs').rglob('result.json'))
    reused = json.loads(result_path.read_text())
    if (not reused['case_cache'][0]['reused'] or before != receipt_path.read_bytes()
            or original['cases'] != reused['cases']):
        raise AssertionError('SECOND_WORKER_FAILED_EXACT_REUSE')
    summary = {'status': 'PASS', 'numeric_backend_rejection': mismatch,
               'worker_solves': 1, 'worker_reuses': 1, 'max_workers': 2,
               'thread_env': executor.THREAD_ENV, 'source_id': original['science_binding']['source'],
               'science_id': original['case_cache'][0]['science_id'],
               'first_cache': original['case_cache'], 'second_cache': reused['case_cache'],
               'stored_receipt_unchanged': True, 'stored_results_equal': True}
    worker.write_json(root / 'WORKER_CHECKS.json', summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
