#!/usr/bin/env python3
"""Compare two retained compact trajectories with unchanged full62 oracles.

This reads existing raw data only. It does not run any solver or benchmark.
Acceptance thresholds are frozen absolute differences, including near zero.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import traceback
import numpy as np
from analyze_pilot import ROOT, OBS, GROUPS, digest, dump, load_case, need

CASES = ('s04_m04_r04', 'cancel_positive_matter')
LIMITS = dict(signed_observable_max_absolute=3e-7, scaled_ion_fraction_max_absolute=3e-5,
              tau_max_absolute=3e-7)


def maximum_difference(left, right, names=None):
    delta = abs(left-right)
    need(np.isfinite(delta).all(), 'nonfinite paired difference')
    location = np.unravel_index(np.argmax(delta), delta.shape)
    record = dict(max_absolute=float(delta[location]), sample=int(location[0]),
                  compact_value=float(left[location]), full62_value=float(right[location]))
    if len(location) > 1:
        record['column'] = int(location[1])
        if names is not None:
            record['column_name'] = str(names[location[1]])
        record['per_column_max_absolute'] = dict(zip(map(str, names), np.max(delta, axis=0).tolist()))
    return record


def verify(args):
    manifest = json.loads((ROOT/'data/CAMPAIGN.json').read_text())
    configs = {row['case_id']: row['config'] for row in manifest['cases']}
    rows = []
    parents = []
    for case_id in CASES:
        compact = load_case(args.compact/'cases'/case_id, configs[case_id], require_compact=True)
        full = load_case(args.full62/'cases'/case_id, configs[case_id])
        need(compact['_result']['schema'] == 'rec.rei.hheli.compact33.v1', f'{case_id}: compact result schema mismatch')
        need(full['_result']['schema'] == 'rec.rei.hheli.coupled62.v1', f'{case_id}: oracle is not the independent full62 schema')
        need('compact_raw_state33' not in full, f'{case_id}: oracle unexpectedly contains compact output')
        for key in ('x', 'z', 'initial_Y', 'isotope_scales', 'species_names', 'A', 'q'):
            need(np.array_equal(compact[key], full[key]), f'{case_id}: paired {key} mismatch')
        need(np.array_equal(compact['raw_state'][0], full['raw_state'][0]) or
             np.max(abs(compact['raw_state'][0]-full['raw_state'][0])) <= 8*np.finfo(float).eps,
             f'{case_id}: paired initial state mismatch beyond frozen roundoff allowance')
        # Ion fractions mean actual isotope charge fractions. Positive isotope
        # inventory is the denominator. Zero-inventory n/T populations are
        # checked separately; no undefined 0/0 and no relative-to-zero metric.
        inventories = np.zeros(21)
        for indices in GROUPS.values():
            inventories[list(indices)] = compact['initial_Y'][list(indices)].sum()
        populated = inventories > 0
        compact_fraction = compact['Y'][:, populated] / inventories[populated]
        full_fraction = full['Y'][:, populated] / inventories[populated]
        ion = maximum_difference(compact_fraction, full_fraction, compact['species_names'][populated])
        # Also retain donor scaled-population differences, including the chosen
        # numerical scale for zero inventories, for a stronger transparent check.
        scaled = maximum_difference(compact['scaled_populations'], full['scaled_populations'], compact['species_names'])
        signed = maximum_difference(compact['signed_observables'], full['signed_observables'], OBS)
        tau = maximum_difference(compact['raw_state'][:, 61], full['raw_state'][:, 61])
        zero_inventory = dict(compact_max_absolute=float(abs(compact['Y'][:, ~populated]).max()),
                              full62_max_absolute=float(abs(full['Y'][:, ~populated]).max()))
        checks = dict(signed_observable_max_absolute=signed['max_absolute'] <= LIMITS['signed_observable_max_absolute'],
                      scaled_ion_fraction_max_absolute=ion['max_absolute'] <= LIMITS['scaled_ion_fraction_max_absolute'],
                      donor_scaled_population_max_absolute=scaled['max_absolute'] <= LIMITS['scaled_ion_fraction_max_absolute'],
                      tau_max_absolute=tau['max_absolute'] <= LIMITS['tau_max_absolute'],
                      zero_inventory_exact_zero=all(v == 0 for v in zero_inventory.values()))
        rows.append(dict(case_id=case_id, status='PASS' if all(checks.values()) else 'FAIL', checks=checks,
                         samples=193, exact_x_z_pairing=True, signed_full_frobenius=signed,
                         isotope_charge_fractions=ion, donor_scaled_populations=scaled, optical_depth=tau,
                         zero_inventory_Y=zero_inventory))
        parents.append(dict(case_id=case_id, compact=compact['_parent'], full62=full['_parent']))
    status = 'PASS' if all(row['status'] == 'PASS' for row in rows) else 'FAIL'
    code_files = ['code/verify_paired.py', 'code/analyze_pilot.py', 'code/compact_system.py',
                  'code/compact_run.py', 'code/run_full62_oracles.py', 'vendor/rec_hheli/code/coupled.py']
    report = dict(schema='rei.hheli.compact33.paired-implementation.v1', status=status,
                  created_utc=datetime.now(timezone.utc).isoformat(), frozen_limits=LIMITS,
                  cases=rows, parent_case_hashes=parents,
                  code_hashes={name: digest(ROOT/name) for name in code_files},
                  oracle_implementation='unchanged vendor/rec_hheli/code/coupled.py full62 outputs',
                  metric_policy='Maximum pointwise absolute error; identical 193 saved x/z samples. No RMS or division by near-zero observables.',
                  ion_metric='Actual Y divided by fixed positive isotope inventory; n/T separately exact-zero checked. Donor scaled populations also reported.',
                  interpretation='Implementation equivalence at retained discretization and fixed T/UV model; not continuum convergence or performance benchmarking.')
    dump(ROOT/'evidence/PAIRED_COMPARISON.json', report)
    if status != 'PASS':
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        dump(ROOT/f'evidence/PAIRED_COMPARISON_FAILURE_{stamp}.json', report)
    print(json.dumps(report, indent=2))
    return 0 if status == 'PASS' else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compact', type=Path, default=ROOT/'results/pilot_v2')
    parser.add_argument('--full62', type=Path, default=ROOT/'results/full62_oracles')
    args = parser.parse_args()
    try:
        return verify(args)
    except Exception as error:
        report = dict(status='FAILED', error=str(error), traceback=traceback.format_exc(),
                      code_hashes={'code/verify_paired.py': digest(Path(__file__))},
                      created_utc=datetime.now(timezone.utc).isoformat())
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        dump(ROOT/f'evidence/PAIRED_COMPARISON_FAILURE_{stamp}.json', report)
        print(json.dumps(report, indent=2), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
