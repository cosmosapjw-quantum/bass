"""Independent, read-only review of completed arrays; no solver import/call."""
from pathlib import Path
import ast
import hashlib
import json
from datetime import datetime, timezone
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
BASE = 'ee7e9ae76c852079ce86cdd5165624ab2b7fc7a9c672016501ed5da5fb4341d3'
GROUPS = [(0,), (1, 2), (3, 4), (5, 6), (7, 8, 9), (10, 11, 12), (13, 14, 15, 16), (17, 18, 19, 20)]
GATES = {'full_interval_and_samples', 'initial_physical_axes', 'finite', 'population_positivity',
         'isotope_scaled_conservation', 'baryon_conservation', 'nonnegative_electrons', 'number_monopoles',
         'monotone_optical_depth', 'einstein_constraint', 'tensor_sum', 'finite_angular_positivity', 'trace_energy_small'}

def read(name): return json.loads((ROOT/name).read_text())
def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical(value): return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
def identity(base, config): return hashlib.sha256(canonical({'base': base, 'config': config})).hexdigest()
def arrays(path):
    with np.load(path, allow_pickle=False) as data: return {k: data[k] for k in data.files}
def load(directory, config, base, compact=True):
    result = json.loads((directory/'RESULT.json').read_text())
    marker = json.loads((directory/'COMPLETE.json').read_text())
    assert result['status'] == 'COMPLETE' and result['config'] == config
    assert set(result['gates']) == GATES and all(v is True for v in result['gates'].values())
    assert marker['identity'] == result['scientific_identity_sha256'] == identity(base, config)
    assert marker['result_sha256'] == digest(directory/'RESULT.json')
    for output in (marker['outputs']['trajectory.npz'], result['outputs']['trajectory.npz']):
        assert output['sha256'] == digest(directory/'trajectory.npz')
        assert output['bytes'] == (directory/'trajectory.npz').stat().st_size
    data = arrays(directory/'trajectory.npz')
    assert data['raw_state'].shape == (193, 62) and data['Y'].shape == (193, 21)
    assert data['signed_observables'].shape == (193, 6)
    if compact:
        assert result['schema'] == 'rec.rei.hheli.compact33.v1'
        assert data['compact_raw_state33'].shape == (193, 33)
        assert np.array_equal(data['signed_observables_half_contraction'], data['signed_observables']/np.sqrt(2))
    else:
        assert result['schema'] == 'rec.rei.hheli.coupled62.v1' and 'compact_raw_state33' not in data
    assert np.array_equal(data['x'], np.linspace(0, np.log(7.), 193))
    assert np.array_equal(data['z'], 21*np.exp(-data['x'])-1)
    assert all(np.isfinite(v).all() for v in data.values() if np.issubdtype(v.dtype, np.number))
    assert np.array_equal(data['Y'], data['scaled_populations']*data['isotope_scales'])
    assert np.array_equal(data['observables_norm'], abs(data['signed_observables']))
    return data, result, dict(case_id=config['case_id'], scientific_identity_sha256=marker['identity'],
                             result_sha256=digest(directory/'RESULT.json'),
                             complete_sha256=digest(directory/'COMPLETE.json'),
                             trajectory_sha256=digest(directory/'trajectory.npz'))

frozen = read('results/pilot_v2/FROZEN.json')
assert frozen['base_identity'] == BASE
assert hashlib.sha256(canonical(frozen['files'])).hexdigest() == BASE
assert len(frozen['files']) == 39
for path, expected in frozen['files'].items(): assert digest(ROOT/path) == expected, path
manifest = read('data/CAMPAIGN.json')
configs = [{**row['config'], 'case_id': row['case_id']} for row in manifest['cases']]
assert configs == frozen['configs'] and len(configs) == 127
assert {c['case_id'] for c in configs} == {p.name for p in (ROOT/'results/pilot_v2/cases').iterdir() if p.is_dir()}
plot = read('evidence/PLOT_VERIFICATION.json')
parents = {p['case_id']: p for p in plot['parent_case_hashes']}
source = arrays(ROOT/'results/analysis/all_histories_plot_source.npz')
positions = {str(cid): i for i, cid in enumerate(source['case_ids'])}
assert set(positions) == set(parents) == {c['case_id'] for c in configs}
data_by_id, result_by_id = {}, {}
stats = dict(min_Y=float('inf'), negative_Y_count=0, max_baryon_error=0., max_electron_relative_error=0.,
             max_tensor_sum_error=0., max_radiation_sum_error=0., min_angular_weight=float('inf'),
             min_tau_step=float('inf'), max_isotope_scaled_conservation_error=0.)
for config in configs:
    cid = config['case_id']
    data, result, parent = load(ROOT/'results/pilot_v2/cases'/cid, config, BASE)
    assert parent == parents[cid]
    data_by_id[cid], result_by_id[cid] = data, result
    i = positions[cid]
    for aggregate, raw in [('Y', 'Y'), ('signed_full_frobenius', 'signed_observables'),
                           ('signed_half_contraction', 'signed_observables_half_contraction'),
                           ('norm_full_frobenius', 'observables_norm'), ('diagnostics', 'diagnostics')]:
        assert np.array_equal(source[aggregate][i], data[raw]), (cid, aggregate)
    assert np.array_equal(source['norm_half_contraction'][i], abs(data['signed_observables'])/np.sqrt(2))
    assert np.array_equal(source['x'], data['x']) and np.array_equal(source['z'], data['z'])
    assert np.array_equal(source['species_names'], data['species_names'])
    assert np.count_nonzero(data['Y'][:, [0, 5, 6]]) == 0
    stats['min_Y'] = min(stats['min_Y'], float(data['Y'].min()))
    stats['negative_Y_count'] += int(np.count_nonzero(data['Y'] < 0))
    stats['max_baryon_error'] = max(stats['max_baryon_error'], float(abs(data['Y']@data['A']-1).max()))
    for indices in GROUPS:
        nominal = data['initial_Y'][list(indices)].sum()
        residual = float(abs(data['Y'][:, indices].sum(axis=1)-nominal).max()/data['isotope_scales'][indices[0]])
        stats['max_isotope_scaled_conservation_error'] = max(stats['max_isotope_scaled_conservation_error'], residual)
        if nominal > 0:
            assert np.array_equal(source['charge_fractions'][i][:, indices], data['Y'][:, indices]/nominal)
        else:
            assert np.isnan(source['charge_fractions'][i][:, indices]).all()
    diag = dict(zip(data['diagnostic_names'], data['diagnostics'].T))
    ne = diag['nb_m3']*(data['Y']@data['q'])
    stats['max_electron_relative_error'] = max(stats['max_electron_relative_error'], float((abs(ne-diag['ne_m3'])/ne).max()))
    obs = data['signed_observables']
    stats['max_tensor_sum_error'] = max(stats['max_tensor_sum_error'], float(abs(obs[:, 3]-obs[:, 1]-obs[:, 2]).max()))
    stats['max_radiation_sum_error'] = max(stats['max_radiation_sum_error'], float(abs(obs[:, 2]-obs[:, 4]-obs[:, 5]).max()))
    stats['min_angular_weight'] = min(stats['min_angular_weight'], *(float(diag[k].min()) for k in diag if k.startswith('min_')))
    stats['min_tau_step'] = min(stats['min_tau_step'], float(np.diff(data['raw_state'][:, 61]).min()))
assert stats['min_Y'] == 0 and stats['negative_Y_count'] == 0
assert stats['max_baryon_error'] < 2e-8 and stats['max_isotope_scaled_conservation_error'] < 2e-7
assert stats['max_electron_relative_error'] < 1e-12 and stats['max_tensor_sum_error'] < 2e-16
assert stats['min_angular_weight'] > -2e-7 and stats['min_tau_step'] >= -2e-10

fullbase = hashlib.sha256(canonical({'compact_source_base': BASE, 'implementation': 'unchanged_donor_full62'})).hexdigest()
paired = []
for cid in ['s04_m04_r04', 'cancel_positive_matter']:
    config = next(c for c in configs if c['case_id'] == cid)
    compact = data_by_id[cid]
    full, _, parent = load(ROOT/'results/full62_oracles/cases'/cid, config, fullbase, False)
    for key in ['x', 'z', 'initial_Y', 'isotope_scales', 'species_names', 'A', 'q']:
        assert np.array_equal(compact[key], full[key])
    inventories = np.zeros(21)
    for indices in GROUPS: inventories[list(indices)] = compact['initial_Y'][list(indices)].sum()
    good = inventories > 0
    row = dict(case_id=cid,
               signed_max_absolute=float(abs(compact['signed_observables']-full['signed_observables']).max()),
               charge_fraction_max_absolute=float(abs((compact['Y'][:, good]-full['Y'][:, good])/inventories[good]).max()),
               tau_max_absolute=float(abs(compact['raw_state'][:, 61]-full['raw_state'][:, 61]).max()),
               full62_parent=parent)
    assert row['signed_max_absolute'] <= 3e-7 and row['charge_fraction_max_absolute'] <= 3e-5 and row['tau_max_absolute'] <= 3e-7
    assert np.count_nonzero(full['Y'][:, ~good]) == 0
    paired.append(row)

cancel = arrays(ROOT/'results/analysis/cancellation_plot_source.npz')
control = data_by_id['s00_m02_r02']['signed_observables']
cancellation = []
for cid in ['cancel_positive_matter', 'cancel_negative_matter']:
    obs = data_by_id[cid]['signed_observables']
    denom = abs(obs[:, 1])+abs(obs[:, 2])
    q = abs(obs[:, 3])/denom
    assert np.array_equal(cancel[cid+'_signed_full'], obs)
    assert np.array_equal(cancel[cid+'_delta_signed_S_F'], obs[:, 0]-control[:, 0])
    assert np.array_equal(cancel[cid+'_cancellation_ratio'], q)
    cancellation.append(dict(case_id=cid, initial_q=float(q[0]), final_q=float(q[-1]),
                             final_signed_S_F=float(obs[-1, 0]), max_abs_S_F=float(abs(obs[:, 0]).max())))
sweep = arrays(ROOT/'results/analysis/parameter_sweep_plot_source.npz')
for si, s in enumerate(sweep['initial_Sigma_F']):
    for mi, m in enumerate(sweep['initial_P_m_F']):
        for ri, r in enumerate(sweep['initial_P_r_F']):
            cid = next(c['case_id'] for c in configs if c['case_id'].startswith('s') and c['Sigma_F'] == s and c['P_m_initial_target'] == m and c['P_r_initial_target'] == r)
            ctrl = data_by_id[f's{si:02d}_m02_r02']['signed_observables'][-1, 0]
            obs = data_by_id[cid]['signed_observables'][-1]
            assert sweep['endpoint_delta_S_F'][si, mi, ri] == obs[0]-ctrl
            assert sweep['endpoint_P_total_F'][si, mi, ri] == obs[3]
for path, expected in plot['source_and_output_hashes'].items():
    assert digest(ROOT/path) == expected['sha256'] and (ROOT/path).stat().st_size == expected['bytes'], path
for path, expected in plot['code_hashes'].items(): assert digest(ROOT/path) == expected
assert plot['analysis_summary_sha256'] == digest(ROOT/'results/analysis/SUMMARY.json')
assert plot['visual_inspection_evidence_sha256'] == digest(ROOT/'evidence/PLOT_VISUAL_INSPECTION.json')

def gate_ast(path):
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'gates' for t in node.targets):
            return ast.dump(node.value, include_attributes=False)
    raise AssertionError('Missing gate expression')
assert gate_ast(ROOT/'code/compact_run.py') == gate_ast(ROOT/'vendor/rec_hheli/code/coupled.py')
resume = read('evidence/FINAL_DEFAULT_RESUME.json')
assert resume['status'] == 'complete_reused' and resume['new_workers'] == 0 and resume['unsubmitted'] == 0
assert len(resume['records']) == 127
assert {row['case_id'] for row in resume['records']} == set(data_by_id)
for row in resume['records']:
    assert row['status'] == 'complete_reused' and row['identity'] == parents[row['case_id']]['scientific_identity_sha256']
resume_receipt = read('evidence/FINAL_RESUME_VERIFICATION.json')
assert resume_receipt['dispatcher_sha256'] == digest(ROOT/'code/run_pilot.py')
assert resume_receipt['source_base_identity'] == BASE and resume_receipt['new_integrations'] == 0
old_raw_count = len(list((ROOT/'results/pilot/cases').glob('*/trajectory.npz')))
assert old_raw_count == 127
report = dict(status='PASS', created_utc=datetime.now(timezone.utc).isoformat(), reviewer='/root/compact33_independent_review',
              method='Independent NumPy reads and SHA256 checks; no implementation analysis module imported, no ODE or benchmark run.',
              source_base=BASE, verified_source_files=39, compact_cases=127, compact_saved_epochs=24511,
              full62_cases=2, full62_saved_epochs=386, owner_gates_per_case=13, all_owner_gate_expressions_identical=True,
              aggregate_arrays_exact=True, discrete_sweep_endpoints_exact=250, plot_hash_entries_verified=len(plot['source_and_output_hashes']),
              raw_statistics=stats, paired=paired, cancellation=cancellation,
              zero_seed_control_max_abs_S_F=float(abs(control[:, 0]).max()),
              default_resume_complete_reused=127, default_resume_new_integrations=0, preserved_first_attempt_raw_count=old_raw_count,
              reviewer_script_sha256=digest(Path(__file__)))
(Path(__file__).parent/'FINAL_RAW_CHECK.json').write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False)+'\n')
print(json.dumps(report, indent=2, sort_keys=True))
