"""Astra approved binary64-input Decimal60 oracle; V1 evidence is immutable."""
import argparse
from decimal import Decimal
import io
import json
from pathlib import Path
import resource
import subprocess
import time
import zipfile

import readback as v1

ROOT = Path(__file__).resolve().parent


def binary64_rows(data, expected=16384):
    # Retain the original intake requirements, then use the native parsed values.
    raw = v1.parse_cells(data, expected)
    rows = [[Decimal.from_float(float(x)) for x in row] for row in raw]
    for i, row in enumerate(rows):
        if any(not x.is_finite() for x in row):
            raise ValueError('BINARY64_NONFINITE')
        if row[1] <= row[0] or row[4] < 0 or row[5] < 0:
            raise ValueError('BINARY64_CLOCK_OR_DENSITY')
        if i and rows[i-1][1] != row[0]:
            raise ValueError('BINARY64_DISCONTINUITY')
    return rows


def verify_preserved_source(base):
    diff = (ROOT/'evidence/repair_build/receiver_source.diff').read_text()
    source = ''.join(line[1:]+'\n' for line in diff.splitlines()
                     if line.startswith('+') and not line.startswith('+++'))
    actual = (base/'_rustcore/examples/rei_pr104_cell_receiver.rs').read_bytes()
    assert actual == source.encode(), 'RECEIVER_SOURCE_IDENTITY'
    for line in (ROOT/'evidence/build/cargo_inputs.sha256').read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        assert v1.sha((base/name).read_bytes()) == digest, 'CARGO_INPUT_IDENTITY'
    return v1.sha(actual)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    result = {'contract': 'BINARY64_ORACLE_CLOSEOUT_V2', 'status': 'RUNNING',
              'science_solver_calls': 0, 'rust_rebuilds': 0, 'repair_count': 0,
              'receiver_calls_new': 0, 'receiver_launches_cumulative': 1,
              'v1_status': 'HOLD_ORACLE_CONTRACT', 'cases': {}}
    def save():
        (args.output/'EXECUTION.json').write_text(json.dumps(result, indent=2)+'\n')
    save()
    try:
        archive = Path(v1.CONTRACT['archive']).read_bytes()
        assert v1.sha(archive) == v1.CONTRACT['archive_sha256'], 'ARCHIVE_HASH'
        z = zipfile.ZipFile(io.BytesIO(archive))
        payloads = {}
        for name, digest in v1.CONTRACT['members'].items():
            data = z.read('research/broad_history_20261010/'+name)
            assert v1.sha(data) == digest, name
            payloads[name] = data
        result['archive_sha256'] = v1.sha(archive)
        result['receiver_source_sha256'] = verify_preserved_source(ROOT.parents[1])
        binary_sha = v1.sha(args.binary.read_bytes())
        expected_binary = (ROOT/'evidence/repair_build/executable.sha256').read_text().split()[0]
        old = json.loads((ROOT/'evidence/repair/EXECUTION.json').read_text())
        assert binary_sha == expected_binary == old['binary_sha256'], 'BINARY_IDENTITY'
        assert old['cases']['flrw']['exit'] == 0, 'PRESERVED_FLRW_EXIT'
        result['binary_sha256'] = binary_sha
        rows = {}
        for case in ('flrw', 'rp01'):
            rows[case] = binary64_rows(payloads[f'evidence/RUN002/{case}_BASS_CELLS.csv'])
            v1.reference(rows[case])
            result['cases'][case] = {'producer_preflight': 'PASS'}
        result['both_preflight'] = 'PASS'
        save()
        flrw = (ROOT/'evidence/repair/flrw.stdout.log').read_bytes()
        result['cases']['flrw'].update({'execution': 'REUSED_WITHOUT_RERUN',
            'stdout_sha256': v1.sha(flrw), 'receipt': old['cases']['flrw'],
            'validation': v1.check_native(flrw.decode(), rows['flrw'])})
        save()
        command = [str(args.binary.resolve())]
        start = time.monotonic()
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        result['receiver_calls_new'] = 1
        result['receiver_launches_cumulative'] = 2
        result['cases']['rp01']['command'] = command
        save()
        p = subprocess.run(command, input=payloads['evidence/RUN002/rp01_BASS_CELLS.csv'],
                           capture_output=True, timeout=120)
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        (args.output/'rp01.stdout.log').write_bytes(p.stdout)
        (args.output/'rp01.stderr.log').write_bytes(p.stderr)
        result['cases']['rp01'].update({'exit': p.returncode, 'wall_s': time.monotonic()-start,
            'child_user_cpu_s': after.ru_utime-before.ru_utime,
            'child_system_cpu_s': after.ru_stime-before.ru_stime,
            'child_maxrss_kib': after.ru_maxrss, 'stdout_sha256': v1.sha(p.stdout),
            'stderr_sha256': v1.sha(p.stderr)})
        save()
        assert p.returncode == 0, 'NATIVE_EXIT'
        result['cases']['rp01']['validation'] = v1.check_native(p.stdout.decode(), rows['rp01'])
        result['status'] = 'PASS_SCOPED'
        save()
        (args.output/'VALIDATION.json').write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps(result, indent=2))
    except Exception as error:
        result['status'] = 'HOLD'
        result['failure'] = {'type': type(error).__name__, 'message': str(error)}
        save()
        (args.output/'FAILURE.json').write_text(json.dumps(result, indent=2)+'\n')
        raise


if __name__ == '__main__':
    main()
