#!/usr/bin/env python3
"""Native lane selection, keeping shared planner/worker/executor policies."""
from __future__ import annotations
import argparse
from functools import partial
import json
from pathlib import Path
import sys

LANE = Path(__file__).resolve().parent
ACCEL = LANE.parent / 'rei_sigma_pi_acceleration_20261021'
if str(ACCEL) not in sys.path:
    sys.path.insert(0, str(ACCEL))
import batch_worker as worker
import work_plan as wp
from build_native import DEFAULT_BUILD, inspect_build

NAME = 'reflected-native-neumaier-v1'


def backend_spec(build_dir=DEFAULT_BUILD):
    # Inspect the binding, but do not load the shared library during preparation.
    library, receipt_path, receipt = inspect_build(build_dir)
    from native_context import PreparedContext
    files = tuple(LANE / p for p in ('native_context.py', 'native_worker.py', 'moments.cpp',
                                     'build_native.py', 'FROZEN_CONTRACT.md')) + (receipt_path, library)
    identity = {'schema': receipt['schema'], 'source_sha256': receipt['source_sha256'],
                'compiler': receipt['compiler'], 'compiler_version': receipt['compiler_version'],
                'flags': receipt['flags'], 'library_sha256': receipt['library_sha256'],
                'platform': receipt['platform'], 'machine': receipt['machine']}
    return worker.BackendSpec(NAME, partial(PreparedContext, build_dir=Path(build_dir)), files,
                              Path(__file__).resolve(), identity,
                              ('--build-dir', str(Path(build_dir).resolve())))


def prepare(plan_path, out, case_store, group_size='auto', build_dir=DEFAULT_BUILD):
    # The standard pending-zero branch validates inputs and publishes its receipt
    # before a native build is inspected, imported, loaded, or requested.
    plan = json.loads(Path(plan_path).read_text())
    if plan.get('pending_count') == 0 and not plan.get('pending'):
        return worker.prepare(plan_path, out, case_store, group_size)
    return worker.prepare(plan_path, out, case_store, group_size,
                          backend=backend_spec(build_dir))


def run_group(input_path, output_path, build_dir=DEFAULT_BUILD, **kwargs):
    return worker.run_group(input_path, output_path, backend=backend_spec(build_dir), **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    plan = sub.add_parser('plan')
    plan.add_argument('--cases', type=Path)
    plan.add_argument('--nsteps', type=int, default=64)
    plan.add_argument('--group-size', type=int, default=3)
    plan.add_argument('--profile', choices=('sandbox', 'ncp'), default='ncp')
    plan.add_argument('--out', required=True, type=Path)
    prepare_parser = sub.add_parser('prepare')
    for name in ('plan', 'out', 'case-store'):
        prepare_parser.add_argument('--' + name, required=True, type=Path)
    prepare_parser.add_argument('--group-size', default='auto')
    prepare_parser.add_argument('--build-dir', type=Path, default=DEFAULT_BUILD)
    run = sub.add_parser('run-group')
    run.add_argument('--input', required=True, type=Path)
    run.add_argument('--output', required=True, type=Path)
    run.add_argument('--build-dir', type=Path, default=DEFAULT_BUILD)
    args = parser.parse_args()
    if args.command == 'plan':
        result = wp.build_plan(cases=args.cases, nsteps=args.nsteps, group_size=args.group_size,
                               profile=args.profile, backend=NAME)
        worker.write_json(args.out, result)
        result = {key: result[key] for key in ('status', 'candidate_count', 'completed_count', 'pending_count', 'launched_jobs')}
    elif args.command == 'prepare':
        result = prepare(args.plan, args.out, args.case_store, args.group_size, args.build_dir)
    else:
        data = run_group(args.input, args.output, args.build_dir)
        result = {'status': data['status'], 'cases': len(data['cases']),
                  'reused': sum(record['reused'] for record in data['case_cache'])}
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
