#!/usr/bin/env python3
"""Audit and plot the completed compact33 campaign, without solving any ODE.

All plotted coordinates are saved epochs. Straight connecting segments and
samplewise case envelopes add no new solved epochs. No clipping, smoothing,
renormalization, synthetic trajectories, or positivity floors are applied.
"""
from __future__ import annotations
import argparse
import csv
import gzip
import hashlib
import json
import os
from pathlib import Path
import sys
import traceback
from datetime import datetime, timezone

os.environ.setdefault('MPLCONFIGDIR', '/tmp/rei_hheli_compact_pilot_matplotlib')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import SymLogNorm
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
GROUPS = {'n': (0,), 'H1': (1, 2), 'D': (3, 4), 'T': (5, 6),
          'He3': (7, 8, 9), 'He4': (10, 11, 12),
          'Li6': (13, 14, 15, 16), 'Li7': (17, 18, 19, 20)}
OBS = ('S_F', 'P_m_F', 'P_r_F', 'P_total_F', 'P_gamma_F', 'P_nu_F')
HALF = ('S_half', 'P_m_half', 'P_r_half', 'P_total_half', 'P_gamma_half', 'P_nu_half')
PALETTE = ('#225ea8', '#d77d15', '#7a5195', '#277a73', '#ba527a')
SCOPE = 'Retained LRS H–Li model; prescribed T(z) and external isotropic UV; test-fluid baryons.'
PLOT_CHECKS = []


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load_case(directory, expected_config=None, require_compact=False):
    """Read actual completion, retained owner gates, and hash-bound raw data."""
    result_path, complete_path = directory/'RESULT.json', directory/'COMPLETE.json'
    result, complete = json.loads(result_path.read_text()), json.loads(complete_path.read_text())
    need(result['status'] == 'COMPLETE', f'{directory.name}: status is not COMPLETE')
    need(bool(result['gates']) and all(v is True for v in result['gates'].values()),
         f'{directory.name}: a retained owner gate failed')
    need(complete['identity'] == result['scientific_identity_sha256'], f'{directory.name}: completion identity mismatch')
    need(complete['result_sha256'] == digest(result_path), f'{directory.name}: RESULT hash mismatch')
    trajectory = directory/'trajectory.npz'
    for record in (result['outputs']['trajectory.npz'], complete['outputs']['trajectory.npz']):
        need(record['sha256'] == digest(trajectory) and record['bytes'] == trajectory.stat().st_size,
             f'{directory.name}: trajectory hash or size mismatch')
    if expected_config is not None:
        for key, value in expected_config.items():
            need(result['config'].get(key) == value, f'{directory.name}: config mismatch for {key}')
    with np.load(trajectory, allow_pickle=False) as raw:
        data = {name: raw[name].copy() for name in raw.files}
    x, z = data['x'], data['z']
    need(x.shape == z.shape == (193,), f'{directory.name}: missing 193 epochs')
    need(np.array_equal(x, np.linspace(0, np.log(7.), 193)), f'{directory.name}: x grid differs from frozen grid')
    need(np.array_equal(z, 21*np.exp(-x)-1), f'{directory.name}: z/x mismatch')
    need(np.all(np.diff(x) > 0) and np.all(np.diff(z) < 0), f'{directory.name}: nonmonotone x/z')
    need(abs(z[0]-20) < 1e-13 and abs(z[-1]-2) < 1e-13, f'{directory.name}: wrong redshift interval')
    for name in ('Y', 'scaled_populations'):
        need(data[name].shape == (193, 21), f'{directory.name}: wrong {name} shape')
    need(data['signed_observables'].shape == (193, 6), f'{directory.name}: wrong observables shape')
    need(data['raw_state'].shape == (193, 62), f'{directory.name}: missing full62 lifted output')
    for key, values in data.items():
        if np.issubdtype(values.dtype, np.number):
            need(np.isfinite(values).all(), f'{directory.name}: nonfinite {key}')
    need(np.allclose(data['Y'], data['scaled_populations']*data['isotope_scales'], rtol=0, atol=0),
         f'{directory.name}: Y/scaled population mismatch')
    need(np.array_equal(data['observables_norm'], abs(data['signed_observables'])), f'{directory.name}: norm mismatch')
    if require_compact:
        need(data['compact_raw_state33'].shape == (193, 33), f'{directory.name}: missing compact coordinates')
        need(np.array_equal(data['signed_observables_full_frobenius'], data['signed_observables']),
             f'{directory.name}: full convention mismatch')
        need(np.array_equal(data['signed_observables_half_contraction'], data['signed_observables']/np.sqrt(2.)),
             f'{directory.name}: half convention mismatch')
    data['_result'] = result
    data['_parent'] = dict(case_id=directory.name, scientific_identity_sha256=result['scientific_identity_sha256'],
                           trajectory_sha256=digest(trajectory), result_sha256=digest(result_path),
                           complete_sha256=digest(complete_path))
    return data


def exact_line(ax, x, y, **kwargs):
    line, = ax.plot(x, y, **kwargs)
    need(np.array_equal(line.get_xdata(), x) and np.array_equal(line.get_ydata(), y, equal_nan=True),
         'render line does not match saved source data')
    PLOT_CHECKS.append(dict(samples=len(x), exact_x=True, exact_y=True))
    return line


def time_axis(ax):
    ax.set_xlim(20, 2)
    ax.set_xticks([20, 16, 12, 8, 4, 2])
    ax.set_xlabel('Redshift z (time increases →)')
    ax.grid(True, alpha=.16, linewidth=.65)
    ax.axhline(0, color='#555555', linewidth=.65, zorder=0)


def save_figure(fig, name, output, note):
    fig.text(.5, .012, SCOPE + '\n' + note, ha='center', va='bottom', fontsize=9)
    fig.savefig(output/(name+'.png'), dpi=190, bbox_inches='tight', facecolor='white')
    fig.savefig(output/(name+'.pdf'), bbox_inches='tight', facecolor='white',
                metadata={'Title': name, 'Subject': SCOPE + ' ' + note})
    plt.close(fig)


def write_table(path, header, rows):
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'wt', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerows(rows)


def make_time_figure(cases, figdir):
    fig, axes = plt.subplots(2, 2, figsize=(13.4, 9.6))
    quantities = (r'$\Sigma_F=|\sqrt{6}s/H|$', r'$\Pi_{m,F}=|\sqrt{6}\kappa_t p_m/H^2|$',
                  r'$\Pi_{r,F}=|\sqrt{6}\kappa_t(p_\gamma+p_\nu)/H^2|$',
                  r'$\Pi_{\mathrm{total},F}=|P_{m,F}+P_{r,F}|$')
    representative = ['s00_m02_r02', 's00_m04_r04', 's00_m00_r00',
                      's01_m04_r04', 's02_m04_r04', 's03_m04_r04', 's04_m04_r04']
    colors = ['#222222', '#225ea8', '#7a5195', '#277a73', '#ba527a', '#d77d15', '#a64422']
    styles = ['--', '-', ':', '-.', '--', ':', '-']
    labels = []
    for cid in representative:
        cfg = cases[cid]['_result']['config']
        labels.append(f'{cid}: ({cfg["Sigma_F"]:g}, {cfg["P_m_initial_target"]:g}, {cfg["P_r_initial_target"]:g})')
    for k, ax in enumerate(axes.flat):
        for cid, d in cases.items():
            exact_line(ax, d['z'], np.abs(d['signed_observables'][:, k]),
                       color='#aab4bf', alpha=.28, linewidth=.65, zorder=1)
        for cid, color, style in zip(representative, colors, styles):
            d = cases[cid]
            exact_line(ax, d['z'], abs(d['signed_observables'][:, k]), color=color,
                       linestyle=style, linewidth=1.6, marker='.', markevery=12, markersize=3, zorder=3)
        ax.set_yscale('symlog', linthresh=1e-7, linscale=.7)
        ax.set_ylabel(quantities[k] + ' [dimensionless]')
        time_axis(ax)
    handles = [Line2D([0], [0], color='#aab4bf', lw=1, label='All 127 actual trajectories (grey)')]
    handles += [Line2D([0], [0], color=c, ls=s, lw=1.6, label=label)
                for c, s, label in zip(colors, styles, labels)]
    fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(.5, .94), ncol=2,
               title='Selected case IDs and initial (ΣF, Pm,F, Pr,F); radiation = photon + neutrino', fontsize=8.5)
    fig.suptitle('Shear and independently seeded matter / radiation stress: z = 20 → 2', fontsize=15, y=.985)
    fig.subplots_adjust(top=.76, bottom=.13, left=.09, right=.98, hspace=.28, wspace=.24)
    save_figure(fig, 'time_evolution_sigma_pi', figdir,
                'Full Frobenius norms; half-contraction = full / √2. Symlog linear region |y| ≤ 10⁻⁷ retains actual zeros; no floor.')


def make_ion_figure(cases, figdir):
    ids = list(cases)
    ref = cases['s00_m02_r02']
    ratios = {name: float(ref['initial_Y'][list(indices)].sum()/ref['initial_Y'][[1, 2]].sum())
              for name, indices in GROUPS.items()}
    fig, axes = plt.subplots(2, 4, figsize=(16.5, 9.2))
    roman = ('I', 'II', 'III', 'IV')
    for ax, (name, indices) in zip(axes.flat, GROUPS.items()):
        inventory = ref['initial_Y'][list(indices)].sum()
        for charge, index in enumerate(indices):
            if inventory > 0:
                samples = np.stack([cases[cid]['Y'][:, index] / inventory for cid in ids])
                y = ref['Y'][:, index] / inventory
            else:
                samples = np.stack([cases[cid]['Y'][:, index] for cid in ids])
                y = ref['Y'][:, index]
            lo, hi = np.min(samples, axis=0), np.max(samples, axis=0)
            ax.fill_between(ref['z'], lo, hi, color=PALETTE[charge], alpha=.15, linewidth=0)
            exact_line(ax, ref['z'], y, color=PALETTE[charge], linestyle=('-', '--', '-.', ':')[charge],
                       linewidth=1.5, marker='.', markevery=12, markersize=2.5,
                       label=('n' if name == 'n' else roman[charge]))
        ax.set_title(f'{name}: initial number / H1 = {ratios[name]:.5g}', fontsize=10.5)
        ax.set_yscale('symlog', linthresh=1e-9, linscale=.65)
        ax.set_ylabel('Charge fraction Y / isotope inventory' if inventory > 0 else 'Abundance Y = n(species) / n(baryon)')
        if inventory == 0:
            ax.text(.5, .55, 'Zero initial inventory\nAll charge states remain exactly zero\nFraction Y / inventory is undefined',
                    transform=ax.transAxes, ha='center', va='center', fontsize=9,
                    bbox=dict(facecolor='white', edgecolor='none', alpha=.85))
            ax.set_ylim(-1.2e-9, 1.2e-9)
        time_axis(ax)
        ax.legend(loc='lower left' if inventory > 0 else 'upper right', ncol=min(4, len(indices)), fontsize=8)
    fig.suptitle('All 21 isotope / ion states through reionization', fontsize=16, y=.985)
    fig.text(.5, .94, 'Lines: zero-shear, zero-seed control s00_m02_r02. Shading: samplewise min–max across 127 cases (scenario range).',
             ha='center', fontsize=10)
    fig.subplots_adjust(top=.87, bottom=.15, left=.065, right=.985, hspace=.39, wspace=.33)
    save_figure(fig, 'isotope_ion_fractions', figdir,
                'Shared electronic rates impose equal H1/D, He3/He4 and Li6/Li7 fractions. Symlog |f| ≤ 10⁻⁹ is linear; raw signs retained.')


def make_cancellation_figure(cases, figdir, out):
    fig, axes = plt.subplots(3, 2, figsize=(13.8, 11))
    control = cases['s00_m02_r02']
    rows = []
    source = {}
    for col, cid in enumerate(('cancel_positive_matter', 'cancel_negative_matter')):
        d = cases[cid]
        obs = d['signed_observables']
        denom = abs(obs[:, 1]) + abs(obs[:, 2])
        ratio = np.full(len(denom), np.nan)
        np.divide(abs(obs[:, 3]), denom, out=ratio, where=denom > 0)
        delta = obs[:, 0] - control['signed_observables'][:, 0]
        source[cid+'_signed_full'] = obs
        source[cid+'_delta_signed_S_F'] = delta
        source[cid+'_cancellation_ratio'] = ratio
        source[cid+'_ratio_denominator'] = denom
        cfg = d['_result']['config']
        axes[0, col].set_title(f'{cid}\nInitial (Pm,F, Pr,F) = ({cfg["P_m_initial_target"]:g}, {cfg["P_r_initial_target"]:g})', fontsize=11)
        for index, label, color, style in ((1, 'Signed Pm,F', PALETTE[0], '-'),
                                          (2, 'Signed Pr,F', PALETTE[1], '--'),
                                          (3, 'Signed Ptotal,F', PALETTE[2], '-.')):
            exact_line(axes[0, col], d['z'], obs[:, index], label=label, color=color, linestyle=style, linewidth=1.6)
        for y, label, color, style in ((obs[:, 0], 'Raw signed SF', PALETTE[0], '-'),
                                      (control['signed_observables'][:, 0], 'Raw zero-seed control SF', '#555555', ':'),
                                      (delta, 'ΔSF = case − matched control', PALETTE[1], '--')):
            exact_line(axes[1, col], d['z'], y, label=label, color=color, linestyle=style, linewidth=1.6)
        exact_line(axes[2, col], d['z'], ratio, color=PALETTE[2], linewidth=1.6,
                   label=r'$q=|P_m+P_r|/(|P_m|+|P_r|)$')
        for row in (0, 1):
            axes[row, col].set_yscale('symlog', linthresh=1e-7, linscale=.7)
            axes[row, col].set_ylabel('Signed full-Frobenius coordinate')
        axes[2, col].set_ylabel('Cancellation ratio q [dimensionless]')
        axes[2, col].set_ylim(-.025, 1.025)
        for row in range(3):
            time_axis(axes[row, col])
            axes[row, col].legend(fontsize=8.5, loc='best')
        for i in range(len(d['z'])):
            rows.append([cid, i, d['x'][i], d['z'][i], *obs[i, :4],
                         control['signed_observables'][i, 0], delta[i], denom[i],
                         ratio[i] if denom[i] > 0 else '', bool(denom[i] > 0)])
    source.update(z=control['z'], x=control['x'], control_signed_full=control['signed_observables'])
    np.savez_compressed(out/'cancellation_plot_source.npz', **source)
    write_table(out/'cancellation_plot_source.csv', ['case_id', 'sample', 'x', 'z', *OBS[:4],
                'control_S_F', 'delta_S_F', 'q_denominator', 'q', 'q_defined'], rows)
    fig.suptitle('Initially cancelling stress components: actual evolution and matched zero-stress control', fontsize=14, y=.985)
    fig.subplots_adjust(top=.90, bottom=.115, left=.09, right=.98, hspace=.35, wspace=.25)
    save_figure(fig, 'cancellation_time_evolution', figdir,
                'Signed values, not norms. Zero-seed control roundoff is retained. q is undefined where its denominator is zero; no replacement.')


def make_sweep_figure(cases, axes_def, figdir, out):
    fig, axes = plt.subplots(2, 5, figsize=(17.5, 8))
    fig.subplots_adjust(top=.85, bottom=.16, left=.055, right=.88, wspace=.33, hspace=.37)
    sources, rows = {}, []
    delta, stress = np.empty((5, 5, 5)), np.empty((5, 5, 5))
    for si in range(5):
        control = cases[f's{si:02d}_m02_r02']['signed_observables'][-1, 0]
        for mi in range(5):
            for ri in range(5):
                cid = f's{si:02d}_m{mi:02d}_r{ri:02d}'
                obs = cases[cid]['signed_observables'][-1]
                delta[si, mi, ri], stress[si, mi, ri] = obs[0]-control, obs[3]
                rows.append([cid, axes_def['Sigma_F'][si], axes_def['P_m'][mi], axes_def['P_r'][ri],
                             obs[0], control, obs[0]-control, obs[1], obs[2], obs[3]])
    for row, cube in enumerate((delta, stress)):
        limit = float(np.max(abs(cube)))
        need(limit > 0, 'endpoint matrix has no dynamic range; requires alternate scale')
        norm = SymLogNorm(linthresh=max(limit*1e-3, 1e-12), vmin=-limit, vmax=limit, base=10)
        for si in range(5):
            ax = axes[row, si]
            rr, mm = np.meshgrid(axes_def['P_r'], axes_def['P_m'])
            # Discrete square marks: only actual 5×5 requested points, no contour or interpolation.
            artist = ax.scatter(rr.ravel(), mm.ravel(), c=cube[si].ravel(), cmap='RdBu_r', norm=norm,
                                marker='s', s=260, linewidths=.55, edgecolors='#555555')
            need(np.array_equal(np.asarray(artist.get_array()), cube[si].ravel()), 'sweep colors/source mismatch')
            need(np.array_equal(np.asarray(artist.get_offsets()), np.c_[rr.ravel(), mm.ravel()]), 'sweep axes/source mismatch')
            PLOT_CHECKS.append(dict(discrete_points=25, exact_color_values=True, exact_offsets=True))
            if row == 0:
                ax.set_title(f'Initial ΣF = {axes_def["Sigma_F"][si]:g}', fontsize=11)
            ax.set_xticks(axes_def['P_r'], [f'{v*1e3:g}' for v in axes_def['P_r']], fontsize=9)
            ax.set_yticks(axes_def['P_m'], [f'{v*1e3:g}' for v in axes_def['P_m']], fontsize=9)
            ax.set_xlim(-.0015, .0015)
            ax.set_ylim(-.0007, .0012)
            ax.set_xlabel('Initial signed Pr,F [×10⁻³]')
            ax.set_ylabel('Initial signed Pm,F [×10⁻³]')
            ax.grid(alpha=.12)
        row_position = axes[row, 0].get_position()
        cax = fig.add_axes([.91, row_position.y0, .012, row_position.height])
        ticks = np.array([-limit, -limit/10, -limit/100, 0., limit/100, limit/10, limit])
        colorbar = fig.colorbar(artist, cax=cax, ticks=ticks)
        colorbar.ax.set_yticklabels(['0' if v == 0 else f'{v:.1e}' for v in ticks])
        colorbar.ax.tick_params(labelsize=8.5)
        colorbar.set_label('Δ signed SF(z=2)' if row == 0 else 'Signed Ptotal,F(z=2)', fontsize=10)
    sources.update(endpoint_delta_S_F=delta, endpoint_P_total_F=stress,
                   initial_Sigma_F=axes_def['Sigma_F'], initial_P_m_F=axes_def['P_m'], initial_P_r_F=axes_def['P_r'])
    np.savez_compressed(out/'parameter_sweep_plot_source.npz', **sources)
    write_table(out/'parameter_sweep_plot_source.csv', ['case_id', 'initial_Sigma_F', 'initial_P_m_F', 'initial_P_r_F',
                'endpoint_S_F', 'matched_zero_stress_endpoint_S_F', 'endpoint_delta_S_F', 'endpoint_P_m_F',
                'endpoint_P_r_F', 'endpoint_P_total_F'], rows)
    fig.suptitle('Independent initial stress sweep at five shear seeds: discrete endpoints at z = 2', fontsize=15, y=.99)
    fig.text(.5, .94, 'Top: signed shear difference from the same-ΣF, Pm,F = Pr,F = 0 control. Bottom: signed total stress.',
             ha='center', fontsize=10)
    save_figure(fig, 'parameter_sweep_slices', figdir,
                '125 actual grid cases; squares are discrete samples. Shared diverging symlog color scale within each row; no interpolated contours.')


def analyze(args):
    manifest = json.loads(args.manifest.read_text())
    expected = {row['case_id']: row['config'] for row in manifest['cases']}
    need(len(expected) == len(manifest['cases']) == 127, 'campaign must have exactly 127 unique cases')
    need(len([k for k in expected if k.startswith('s')]) == 125, 'campaign must have 125 grid points')
    actual = {p.name for p in (args.input/'cases').iterdir() if p.is_dir()}
    need(actual == set(expected), f'case presence mismatch: missing={sorted(set(expected)-actual)}, extra={sorted(actual-set(expected))}')
    cases = {cid: load_case(args.input/'cases'/cid, cfg, require_compact=True) for cid, cfg in expected.items()}
    reference = next(iter(cases.values()))
    for cid, d in cases.items():
        for key in ('x', 'z', 'species_names', 'initial_Y', 'isotope_scales', 'A', 'q', 'diagnostic_names'):
            need(np.array_equal(d[key], reference[key]), f'{cid}: shared {key} mismatch')
    args.output.mkdir(parents=True, exist_ok=True)
    args.figures.mkdir(parents=True, exist_ok=True)
    ids = list(cases)
    observables = np.stack([cases[c]['signed_observables'] for c in ids])
    Y = np.stack([cases[c]['Y'] for c in ids])
    need(np.all(Y[:, :, [0, 5, 6]] == 0), 'zero-inventory n/T is not exactly zero; cannot use zero-state caption')
    inventory = np.array([reference['initial_Y'][list(indices)].sum() for indices in GROUPS.values()])
    charge_fractions = np.full_like(Y, np.nan)
    isotope_errors = {}
    for (name, indices), initial_inventory in zip(GROUPS.items(), inventory):
        if initial_inventory > 0:
            charge_fractions[:, :, list(indices)] = Y[:, :, list(indices)]/initial_inventory
        isotope_errors[name] = float(np.max(abs(Y[:, :, list(indices)].sum(axis=2)-initial_inventory))/reference['isotope_scales'][indices[0]])
    np.savez_compressed(args.output/'all_histories_plot_source.npz', case_ids=np.array(ids), x=reference['x'], z=reference['z'],
                        Y=Y, species_names=reference['species_names'],
                        signed_full_frobenius=observables, signed_half_contraction=observables/np.sqrt(2.),
                        norm_full_frobenius=abs(observables), norm_half_contraction=abs(observables)/np.sqrt(2.),
                        signed_full_names=np.array(OBS), signed_half_names=np.array(HALF),
                        charge_fractions=charge_fractions, isotope_inventory=inventory, isotope_group_names=np.array(list(GROUPS)),
                        diagnostic_names=reference['diagnostic_names'],
                        diagnostics=np.stack([cases[c]['diagnostics'] for c in ids]))
    dkeys = reference['diagnostic_names'].tolist()
    selected_diag = ['ne_m3', 'nb_m3', 'tau_T', 'T_K', 'uv_scale', 'gamma_T_per_H', 'trace_energy_fraction']
    header = ['case_id', 'sample', 'x', 'z'] + ['Y_'+str(n) for n in reference['species_names']] + list(OBS)+list(HALF)
    header += ['norm_'+n for n in OBS]+['norm_'+n for n in HALF]+selected_diag
    def record(cid, i):
        d = cases[cid]
        obs = d['signed_observables'][i]
        return [cid, i, d['x'][i], d['z'][i], *d['Y'][i], *obs, *(obs/np.sqrt(2.)), *abs(obs),
                *(abs(obs)/np.sqrt(2.)), *(d['diagnostics'][i, dkeys.index(name)] for name in selected_diag)]
    write_table(args.output/'all_histories.csv.gz', header, (record(cid, i) for cid in ids for i in range(193)))
    write_table(args.output/'endpoints.csv', header, (record(cid, 192) for cid in ids))
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.spines.top': False,
                         'axes.spines.right': False, 'pdf.fonttype': 42, 'savefig.facecolor': 'white'})
    make_time_figure(cases, args.figures)
    make_ion_figure(cases, args.figures)
    make_cancellation_figure(cases, args.figures, args.output)
    make_sweep_figure(cases, manifest['physical_axes'], args.figures, args.output)
    # Round-trip exported data values against raw trajectories, including exact zeros and negatives.
    with np.load(args.output/'all_histories_plot_source.npz') as saved:
        need(np.array_equal(saved['Y'], Y), 'plot-source Y roundtrip mismatch')
        need(np.array_equal(saved['signed_full_frobenius'], observables), 'plot-source observables mismatch')
        need(np.array_equal(saved['signed_half_contraction'], observables/np.sqrt(2.)), 'plot-source half convention mismatch')
    with gzip.open(args.output/'all_histories.csv.gz', 'rt', newline='') as stream:
        exported = csv.DictReader(stream)
        count = 0
        for cid in ids:
            for i in range(193):
                row = next(exported)
                need(row['case_id'] == cid and int(row['sample']) == i, 'CSV case/epoch alignment mismatch')
                need(float(row['x']) == cases[cid]['x'][i] and float(row['z']) == cases[cid]['z'][i], 'CSV x/z mismatch')
                for name, value in zip(header[4:], record(cid, i)[4:]):
                    need(float(row[name]) == value, f'CSV raw-value mismatch: {cid} {i} {name}')
                count += 1
        need(next(exported, None) is None, 'unexpected CSV rows')
    extrema = {name: dict(min=float(observables[:, :, k].min()), max=float(observables[:, :, k].max()),
                           norm_min=float(abs(observables[:, :, k]).min()), norm_max=float(abs(observables[:, :, k]).max()))
               for k, name in enumerate(OBS)}
    equality = {name: float(np.max(abs(charge_fractions[:, :, a]-charge_fractions[:, :, b])))
                for name, a, b in [('H1_D', 1, 3), ('He3_He4', 7, 10), ('Li6_Li7', 13, 17)]}
    cancellation_summary = {}
    control_s = cases['s00_m02_r02']['signed_observables'][:, 0]
    for cid in ('cancel_positive_matter', 'cancel_negative_matter'):
        obs = cases[cid]['signed_observables']
        denom = abs(obs[:, 1]) + abs(obs[:, 2])
        ratio = np.full(193, np.nan)
        np.divide(abs(obs[:, 3]), denom, out=ratio, where=denom > 0)
        cancellation_summary[cid] = dict(initial_signed_S_F=float(obs[0, 0]), final_signed_S_F=float(obs[-1, 0]),
            max_abs_signed_S_F=float(abs(obs[:, 0]).max()), final_delta_signed_S_F=float(obs[-1, 0]-control_s[-1]),
            initial_q=float(ratio[0]) if denom[0] > 0 else None, final_q=float(ratio[-1]) if denom[-1] > 0 else None,
            undefined_q_epochs=int(np.sum(denom == 0)), final_P_m_F=float(obs[-1, 1]), final_P_r_F=float(obs[-1, 2]),
            final_P_total_F=float(obs[-1, 3]))
    summary = dict(status='COMPLETE', schema='rei.hheli.compact33.plot-analysis.v1', cases=127,
                   grid_cases=125, explicit_cancellation_cases=2, samples_per_case=193, total_saved_epochs=count,
                   all_owner_gates_pass=True, hash_bound_completion_verified=True, monotone_redshift=True,
                   z_start=float(reference['z'][0]), z_end=float(reference['z'][-1]),
                   species_count=21, species_names=reference['species_names'].tolist(),
                   cancellation_cases=cancellation_summary, control_max_abs_signed_S_F=float(abs(control_s).max()),
                   extrema_full_signed_and_norm=extrema, min_raw_Y=float(Y.min()), negative_Y_count=int(np.sum(Y < 0)),
                   exact_zero_Y_count=int(np.sum(Y == 0)), isotope_scaled_conservation_errors=isotope_errors,
                   isotope_initial_number_to_H1={name: float(val/inventory[1]) for name, val in zip(GROUPS, inventory)},
                   equal_electronic_rate_fraction_max_differences=equality,
                   zero_inventory_species=['n', 'T'], zero_inventory_charge_fractions='undefined; stored NaN; plots use actual Y',
                   raw_n_and_T_exactly_zero=bool(np.all(Y[:, :, [0, 5, 6]] == 0)),
                   norm_convention='Full Frobenius: sqrt(6); half-contraction = full/sqrt(2); total signed sum before norm',
                   plotting_policy='193 actual samples per line, straight joins only, no smoothing/interpolation/clipping/floor/renormalization; samplewise case ranges are not confidence intervals',
                   plot_source_roundtrip_exact=True, csv_all_columns_roundtrip_exact=True,
                   artist_checks=PLOT_CHECKS, scientific_scope=SCOPE,
                   parent_case_hashes=[cases[c]['_parent'] for c in ids],
                   code_hashes={'code/analyze_pilot.py': digest(Path(__file__))}, manifest_sha256=digest(args.manifest))
    dump(args.output/'SUMMARY.json', summary)
    outputs = {str(p.relative_to(ROOT)): dict(bytes=p.stat().st_size, sha256=digest(p))
               for base in (args.output, args.figures) for p in sorted(base.iterdir()) if p.is_file()}
    dump(ROOT/'evidence/PLOT_VERIFICATION.json', dict(status='PASS', analysis_summary_sha256=digest(args.output/'SUMMARY.json'),
         csv_rows=count, exact_line_artists=len([x for x in PLOT_CHECKS if 'samples' in x]),
         exact_sweep_points=sum(x.get('discrete_points', 0) for x in PLOT_CHECKS),
         source_and_output_hashes=outputs, parent_case_hashes=summary['parent_case_hashes'],
         code_hashes=summary['code_hashes'], visual_inspection='PENDING; requires human or image inspection after rendering'))
    print(json.dumps({k: summary[k] for k in ('status', 'cases', 'total_saved_epochs', 'min_raw_Y', 'negative_Y_count', 'extrema_full_signed_and_norm')}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT/'results/pilot_v2')
    parser.add_argument('--manifest', type=Path, default=ROOT/'data/CAMPAIGN.json')
    parser.add_argument('--output', type=Path, default=ROOT/'results/analysis')
    parser.add_argument('--figures', type=Path, default=ROOT/'figures')
    args = parser.parse_args()
    try:
        analyze(args)
    except Exception as error:
        report = dict(status='FAILED', error=str(error), traceback=traceback.format_exc(),
                      code_hashes={'code/analyze_pilot.py': digest(Path(__file__))},
                      created_utc=datetime.now(timezone.utc).isoformat())
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        dump(ROOT/f'evidence/PLOT_FAILURE_{stamp}.json', report)
        print(json.dumps(report, indent=2), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
