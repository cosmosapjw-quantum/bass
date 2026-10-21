#!/usr/bin/env python3
"""Exercise the actual std-only P24 CLI, including create-only failure paths."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys


def main():
    here = Path(__file__).resolve().parent
    binary = here / 'rust_p24_probe'
    output = Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else here / 'rust_p24_cli_artifacts'
    output.mkdir(parents=True, exist_ok=False)
    schema = 'BASS_LRS_SOURCE_KL_P24_V1'
    half = math.sqrt(0.5)
    mu = [-1.0, -half, 0.0, half, 1.0]
    prior = [0.08, 0.19, 0.46, 0.19, 0.08]

    def case(name, directions, weights):
        return f'{name} {len(directions)}\n' + ''.join(
            f'{m:.17e} {w:.17e}\n' for m, w in zip(directions, weights))

    one = case('five', mu, prior)
    good_input = f'{schema} 1\n{one}'
    records = []

    def execute(name, content, target_name=None):
        source = output / f'{name}.txt'
        target = output / (target_name or f'{name}.csv')
        source.write_text(content)
        invocation = [str(binary), str(source), str(target)]
        r = subprocess.run(invocation, capture_output=True, text=True)
        (output / f'{name}.log').write_text(r.stdout + r.stderr)
        record = {'name': name, 'command': invocation, 'returncode': r.returncode,
                  'stdout': r.stdout, 'stderr': r.stderr,
                  'output_exists': target.exists(),
                  'input_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
        records.append(record)
        return r, target

    passed, target = execute('valid', good_input)
    assert passed.returncode == 0, passed.stderr
    lines = target.read_text().splitlines()
    assert lines[0] == schema + ' 1' and lines[-1] == 'END 1'
    row = lines[1].split(',')
    assert row[0] == 'five' and int(row[1]) == 5 and len(row) == 12
    residuals = [float(row[4]), float(row[5])]
    weights = [float(x) for x in row[7:]]
    assert all(abs(m) <= 3e-15 for m in residuals)
    assert all(w > 0.0 for w in weights)
    assert abs(math.fsum(weights) - 1.0) <= 3e-15
    expected = [1/30, 4/15, 2/5, 4/15, 1/30]
    assert max(abs(a-b) for a, b in zip(weights, expected)) < 8e-15
    original_digest = hashlib.sha256(target.read_bytes()).hexdigest()

    failed, same = execute('create_only', good_input, 'valid.csv')
    assert failed.returncode == 3 and same.exists()
    assert hashlib.sha256(same.read_bytes()).hexdigest() == original_digest
    records[-1]['existing_output_sha256_preserved'] = original_digest

    upper_mu = [-half, -0.5, 0.0, 0.5, half]
    rank1_mu = [-math.sqrt(0.6), 0.0, math.sqrt(0.6)]
    negatives = {
        'trailing': (good_input + 'EXTRA\n', 'TRAILING_INPUT'),
        'schema': (good_input.replace(schema, 'BASS_LRS_SOURCE_KL_P2_V1'), 'INPUT_SCHEMA'),
        'truncated': (' '.join(good_input.split()[:-1]), 'TRUNCATED'),
        'duplicate': (f'{schema} 2\n{one}{one}', 'CASE_ID'),
        'infeasible_second': (f'{schema} 2\n{one}' + case('upper', upper_mu, [1.0]*5),
                              'INFEASIBLE_P24_UPPER'),
        'rank1_compatible_unresolved': (f'{schema} 1\n' + case('rank1', rank1_mu,
                                     [5/18,4/9,5/18]), 'FEASIBILITY_UNRESOLVED_RANK1'),
    }
    for name, (content, failure) in negatives.items():
        result, rejected = execute(name, content)
        assert result.returncode == 3 and failure in result.stderr
        assert not rejected.exists(), f'Input failure created an output: {name}'

    result = {
        'status': 'PASS_SCOPED_RUST_P24_CLI',
        'source_sha256': hashlib.sha256((here.parent/'balance_p24.rs').read_bytes()).hexdigest(),
        'binary_sha256': hashlib.sha256(binary.read_bytes()).hexdigest(),
        'valid_output_sha256': original_digest,
        'csv_fields': ['id','nrays','lambda2','lambda4','residualP2','residualP4',
                       'evaluated_distributions','w0','...','w[n-1]'],
        'valid_cases': 1,
        'negative_controls': 7,
        'records': records,
    }
    (output/'RETURN.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'status': result['status'], 'valid_cases': 1,
                      'negative_controls': 7, 'output': str(output)}))


if __name__ == '__main__':
    main()
