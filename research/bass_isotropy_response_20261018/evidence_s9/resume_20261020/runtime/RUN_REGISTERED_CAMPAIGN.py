#!/usr/bin/env python3
"""Bounded current-environment execution of the already registered S9 matrix.

This observer enforces the existing memory/wall/disk ceilings on this task's
process tree and records source identity. It does not change the matrix,
accuracy gates, model, solver configuration, or existing evidence.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time
from datetime import datetime, timezone


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def descendants_rss(root_pid):
    parents, rss = {}, {}
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():
            continue
        try:
            row = dict(line.split(':', 1) for line in (p / 'status').read_text().splitlines() if ':' in line)
            pid = int(p.name)
            parents[pid] = int(row['PPid'])
            rss[pid] = int(row.get('VmRSS', '0 kB').split()[0]) * 1024
        except (OSError, KeyError, ValueError):
            continue
    selected = {root_pid}
    while True:
        more = {pid for pid, parent in parents.items() if parent in selected}
        if more <= selected:
            break
        selected |= more
    return sum(rss.get(pid, 0) for pid in selected), len(selected)


def directory_bytes(paths):
    total = 0
    for path in paths:
        for p in path.rglob('*'):
            try:
                if p.is_file() and not p.is_symlink():
                    total += p.stat().st_size
            except FileNotFoundError:
                continue
    return total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lane', type=Path, required=True)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--preparation-receipt', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--resource-root', type=Path, action='append', default=[])
    args = parser.parse_args()
    lane = args.lane.resolve()
    output = args.output_dir.resolve()
    if output.exists():
        raise ValueError('Output directory already exists; preserve previous results.')
    output.mkdir(parents=True)
    prereg_path = lane / 's9_vigilode/PREREGISTRATION.json'
    prereg = json.loads(prereg_path.read_text())
    identity = {p: digest(lane / 's9_vigilode' / p)
                for p in {**prereg['source_sha256'], **prereg['input_sha256']}}
    owner = lane / 'balance_p24.rs'
    identity['../balance_p24.rs'] = digest(owner)
    cmd = ['python3', str(lane / 's9_vigilode/campaign.py'),
           '--binary', str(args.binary.resolve()),
           '--preparation-receipt', str(args.preparation_receipt.resolve()),
           '--publication-receipt', str(lane / 'evidence_s9/SOURCE_PUBLICATION_GATE.json'),
           '--output-dir', str(output)]
    env = os.environ.copy()
    env.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1',
               NUMEXPR_NUM_THREADS='1', RAYON_NUM_THREADS='1', PYTHONUNBUFFERED='1')
    record = {'schema': 'BASS_S9_CURRENT_EXECUTION_V1',
              'started_utc': datetime.now(timezone.utc).isoformat(),
              'command': cmd, 'cwd': str(lane),
              'preregistration_sha256': digest(prereg_path),
              'publication_gate_sha256': digest(lane / 'evidence_s9/SOURCE_PUBLICATION_GATE.json'),
              'preparation_receipt_sha256': digest(args.preparation_receipt),
              'binary_sha256': digest(args.binary),
              'source_inputs_before': identity, 'limits': prereg['limits'],
              'extra_whole_matrix_wall_limit_seconds': 1800,
              'old_scientific_campaigns_rerun': 0}
    start = time.monotonic()
    peak_rss = peak_processes = 0
    stop_reason = None
    try:
        disk = directory_bytes(args.resource_root)
        if disk >= prereg['limits']['disk_bytes']:
            raise RuntimeError('Task disk ceiling already exceeded before launch.')
        record['task_disk_bytes_before'] = disk
        with (output / 'CAMPAIGN_PROCESS.log').open('x') as log:
            child = subprocess.Popen(cmd, cwd=lane, env=env, stdout=log,
                                     stderr=subprocess.STDOUT, start_new_session=True)
            while child.poll() is None:
                rss, count = descendants_rss(child.pid)
                peak_rss, peak_processes = max(peak_rss, rss), max(peak_processes, count)
                if rss > prereg['limits']['ram_bytes']:
                    stop_reason = 'ram_limit'
                if time.monotonic() - start > 1800:
                    stop_reason = 'matrix_wall_limit'
                if stop_reason:
                    os.killpg(child.pid, signal.SIGTERM)
                    try:
                        child.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        os.killpg(child.pid, signal.SIGKILL)
                    break
                time.sleep(0.2)
            record['exit_code'] = child.wait()
    finally:
        record.update(elapsed_seconds=time.monotonic()-start,
                      peak_process_tree_rss_bytes=peak_rss,
                      peak_process_tree_count=peak_processes,
                      stop_reason=stop_reason,
                      completed_utc=datetime.now(timezone.utc).isoformat())
        record['source_inputs_after'] = {p: digest(lane / 's9_vigilode' / p) for p in identity}
        record['source_inputs_unchanged'] = record['source_inputs_after'] == identity
        record['task_disk_bytes_after'] = directory_bytes(args.resource_root)
        record['disk_gate'] = record['task_disk_bytes_after'] <= prereg['limits']['disk_bytes']
        record['status'] = 'completed' if record.get('exit_code') == 0 and stop_reason is None else 'failed'
        (output / 'CURRENT_EXECUTION.json').write_text(json.dumps(record, indent=2)+'\n')
        print(json.dumps({k: record[k] for k in ['status', 'elapsed_seconds', 'peak_process_tree_rss_bytes',
                                               'source_inputs_unchanged', 'disk_gate']}), flush=True)


if __name__ == '__main__':
    main()
