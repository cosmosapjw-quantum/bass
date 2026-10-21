#!/usr/bin/env python3
"""Plot stored aggregate samples, separating numerical cohorts explicitly."""
from __future__ import annotations
import os
for _key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
             'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'BLIS_NUM_THREADS'):
    os.environ[_key] = '1'
if hasattr(os, 'sched_getaffinity'):
    os.sched_setaffinity(0, sorted(os.sched_getaffinity(0))[:2])
import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, TwoSlopeNorm
import numpy as np

META = ('case_id', 'science_id', 'science_context_id', 'source_id', 'backend',
        'toolchain_id', 'nsteps', 'cohort_id', 'origin', 'history_available')
COLORS = ('#426d9a', '#87713c', '#208476', '#b45b76', '#8057a3', '#497344', '#a56b35')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_csv(path):
    with path.open(newline='') as handle:
        return list(csv.DictReader(handle))


def number(row, field):
    value = row.get(field, '')
    if value == '':
        return None
    value = float(value)
    if not math.isfinite(value):
        raise ValueError('NONFINITE_PLOT_INPUT: '+field)
    return value


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')


def point(table, index, row, figure, panel, series, xfield, yfield, x=None):
    y = number(row, yfield)
    xx = number(row, xfield) if x is None else x
    return {**{key: row.get(key, '') for key in META},
            'source_table': table, 'source_row': index, 'figure': figure,
            'panel': panel, 'series': series, 'x_field': xfield,
            'x_source_value': number(row, xfield), 'x_plot': xx,
            'y_field': yfield, 'y_source_value': y, 'y_plot': y,
            'point_status': 'PLOTTED' if y is not None else 'UNAVAILABLE',
            'source_diagnostic_status': row.get('diag_cancellation_status',
                                      row.get('final_diag_cancellation_status', '')),
            'source_control_status': row.get('control_status', '')}


def decorate(ax):
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(True, color='#e2e6eb', linewidth=.7)
    ax.set_axisbelow(True)


def caption(cohort, row, count, history):
    return (f"{count} cases · {int(row['nsteps'])} steps · {row['backend']} · "
            f"{row['origin']}\nsource {row['source_id'][:12]} · cohort {cohort[:12]} · "
            + (f'{history} actual saved samples' if history else '\nendpoints only; intermediate history not loaded in this projection'))


def finish(fig, out, stem, title, subtitle, footer):
    fig.suptitle(title, x=.055, y=.985, ha='left', fontsize=16, fontweight='bold', color='#253449')
    fig.text(.055, .932, subtitle, ha='left', va='top', fontsize=9, color='#526174', linespacing=1.5)
    fig.text(.055, .016, footer, ha='left', fontsize=8, color='#526174')
    fig.subplots_adjust(left=.075, right=.95, bottom=.15, top=.80, hspace=.58, wspace=.40)
    paths = []
    for extension in ('png', 'pdf'):
        path = out/(stem+'.'+extension)
        fig.savefig(path, dpi=180, facecolor='white')
        paths.append(path)
    plt.close(fig)
    return paths


def history_figure(cases, histories, cohort, out, title, points):
    stem = 'actual_samples_'+cohort[:12]
    fig, axes = plt.subplots(2, 3, figsize=(13, 8.3))
    ids = [row['case_id'] for _, row in cases]
    lookup = {cid: i for i, cid in enumerate(ids)}
    fields = [('signed_Pi_m', 'Matter stress', r'signed $\Pi_m$'),
              ('signed_Pi_r', 'Radiation stress', r'signed $\Pi_r$'),
              ('signed_Pi_total', 'Total stress', r'signed $\Pi_{\rm total}$'),
              ('signed_Sigma', 'Shear', r'signed $\Sigma$')]
    lines = []
    for ax, (field, label, ylabel) in zip(axes.flat, fields):
        for cid in ids:
            records = sorted(((i, r) for i, r in histories if r['case_id'] == cid),
                             key=lambda item: int(item[1]['step']))
            current = [point('history.csv', i, r, stem, field, cid, 'a', field) for i, r in records]
            points.extend(current)
            if any(p['y_plot'] is None for p in current):
                raise ValueError('MISSING_SAVED_HISTORY_FIELD: '+field)
            line, = ax.plot([p['x_plot'] for p in current], [p['y_plot'] for p in current],
                           '-o', color=COLORS[lookup[cid] % len(COLORS)], lw=1.4, ms=4, label=cid)
            if field == 'signed_Pi_m':
                lines.append(line)
        ax.set_title(label, loc='left', fontsize=11, fontweight='bold')
        ax.set_xlabel('scale factor a')
        ax.set_ylabel(ylabel)
        ax.ticklabel_format(axis='x', style='plain', useOffset=False)
        ax.tick_params(axis='x', labelrotation=20)
        ax.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2), useOffset=False)
        decorate(ax)
    ax = axes[1, 1]
    missing_controls = []
    for index, row in cases:
        current = point('cases.csv', index, row, stem, 'matched_control_response', row['case_id'],
                        'signed_Sigma_requested', 'control_subtracted_final_signed_Sigma', x=lookup[row['case_id']])
        points.append(current)
        if current['y_plot'] is None:
            missing_controls.append(row['case_id'])
            continue
        ax.scatter(current['x_plot'], current['y_plot'], color=COLORS[lookup[row['case_id']] % len(COLORS)], s=38)
    ax.set_xticks(range(len(ids)), [cid.replace('native_check_', 'N') for cid in ids], rotation=20)
    ax.set_title('Matched-control final shear', loc='left', fontsize=11, fontweight='bold')
    ax.set_ylabel(r'$\Sigma_f-\Sigma_{f,\mathrm{control}}$')
    ax.set_xlabel('case (same cohort control)')
    ax.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2), useOffset=False)
    if missing_controls:
        ax.text(.02, .98, f'{len(missing_controls)} controls unavailable', transform=ax.transAxes, va='top', fontsize=8)
    decorate(ax)
    ax = axes[1, 2]
    selected = [r['case_id'] for _, r in cases
                if number(r, 'signed_Pi_m_requested') * number(r, 'signed_Pi_r_requested') < 0]
    for cid in selected:
        records = sorted(((i, r) for i, r in histories if r['case_id'] == cid), key=lambda item: int(item[1]['step']))
        current = [point('history.csv', i, r, stem, 'cancellation_release', cid, 'a', 'diag_residual_fraction') for i, r in records]
        points.extend(current)
        available = [p for p in current if p['y_plot'] is not None]
        ax.plot([p['x_plot'] for p in available], [p['y_plot'] for p in available], '-o',
                color=COLORS[lookup[cid] % len(COLORS)], lw=1.6, ms=5)
    ax.set_title('Opposite-stress residual fraction', loc='left', fontsize=11, fontweight='bold')
    ax.set_ylabel(r'$q=|\Pi_m+\Pi_r|/(|\Pi_m|+|\Pi_r|)$')
    ax.set_xlabel('scale factor a')
    ax.ticklabel_format(axis='x', style='plain', useOffset=False)
    ax.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2), useOffset=False)
    ax.tick_params(axis='x', labelrotation=20)
    if not selected:
        ax.text(.5, .5, 'No opposite-stress cases', ha='center', transform=ax.transAxes)
    decorate(ax)
    fig.legend(lines, ids, loc='lower center', bbox_to_anchor=(.5, .061), ncol=min(5, len(ids)), frameon=False, fontsize=8)
    paths = finish(fig, out, stem, title or 'Stored NCP samples: signed stress and shear',
        caption(cohort, cases[0][1], len(cases), len(histories)),
        'Half-contraction convention. Lines join actual samples; markers show every saved point. No interpolation or solver rerun.')
    return {'figure': stem, 'kind': 'actual_sample_history', 'cohort_id': cohort,
            'case_count': len(cases), 'history_rows': len(histories),
            'opposite_stress_cases': selected, 'missing_control_cases': missing_controls,
            'files': [p.name for p in paths]}


def endpoint_figure(cases, cohort, out, signed_sigma, title, points):
    selected = [(i, row) for i, row in cases if number(row, 'signed_Sigma_requested') == signed_sigma]
    stem = 'endpoint_slice_'+cohort[:12]
    fig, axes = plt.subplots(2, 2, figsize=(11, 9))
    fields = [('final_signed_Sigma', 'Final signed shear', r'$\Sigma_f$'),
              ('final_signed_Pi_total', 'Final signed total stress', r'$\Pi_{\mathrm{total},f}$'),
              ('final_diag_residual_fraction', 'Final residual fraction', r'$q_f$'),
              ('final_diag_normalized_work_total', 'Final normalized total shear work', r'$2\Sigma_f\Pi_{\mathrm{total},f}$')]
    for ax, (field, label, colorlabel) in zip(axes.flat, fields):
        current = []
        for index, row in selected:
            p = point('cases.csv', index, row, stem, field, field,
                      'signed_Pi_m_requested', field)
            p.update({'coordinate_y_field': 'signed_Pi_r_requested',
                      'coordinate_y_value': number(row, 'signed_Pi_r_requested')})
            points.append(p)
            if p['y_plot'] is not None:
                current.append(p)
        if current:
            values = np.array([p['y_plot'] for p in current])
            if field == 'final_diag_residual_fraction':
                norm, cmap = Normalize(0, 1), 'viridis'
            else:
                extent = float(np.max(np.abs(values))) or 1.
                norm, cmap = TwoSlopeNorm(vmin=-extent, vcenter=0., vmax=extent), 'RdBu_r'
            artist = ax.scatter([p['x_plot'] for p in current], [p['coordinate_y_value'] for p in current],
                                c=values, cmap=cmap, norm=norm, s=43, edgecolors='white', linewidths=.35)
            bar = fig.colorbar(artist, ax=ax, fraction=.05, pad=.025)
            bar.set_label(colorlabel, fontsize=9)
            bar.ax.tick_params(labelsize=8)
            if field == 'final_diag_residual_fraction':
                # Emphasize the requested-zero coordinate without changing or
                # interpreting its retained raw numerical diagnostic.
                nominal_zero = [p for p in current if p['x_plot'] == 0.
                                and p['coordinate_y_value'] == 0.]
                if nominal_zero:
                    ax.scatter([0.]*len(nominal_zero), [0.]*len(nominal_zero),
                               s=93, facecolors='none', edgecolors='#253449',
                               linewidths=1.2, zorder=5)
        else:
            ax.text(.5, .5, 'No available exact-slice points', ha='center', transform=ax.transAxes)
        ax.set_title(label, loc='left', fontsize=11, fontweight='bold')
        ax.set_xlabel(r'requested signed $\Pi_m$')
        ax.set_ylabel(r'requested signed $\Pi_r$')
        ax.ticklabel_format(axis='both', style='sci', scilimits=(-2, 2), useOffset=False)
        ax.set_aspect('equal', adjustable='box')
        decorate(ax)
    fig.text(.055, .064,
             'Ring at requested (0, 0): nominal-zero stress; q reflects raw floating-point residuals, with no physical cancellation interpretation.',
             ha='left', fontsize=8, color='#526174')
    paths = finish(fig, out, stem, title or 'Archived endpoints: exact signed-shear slice',
        caption(cohort, cases[0][1], len(cases), 0)+f'\nexact requested signed Sigma = {signed_sigma:g}; {len(selected)} actual coordinates',
        'Half-contraction convention. Each marker is one stored endpoint. Colors show saved values; no interpolation, absent-cell fill, or history reconstruction.')
    return {'figure': stem, 'kind': 'exact_endpoint_slice', 'cohort_id': cohort,
            'source_case_count': len(cases), 'selected_case_count': len(selected),
            'exact_signed_sigma': signed_sigma, 'history_rows': 0,
            'nominal_zero_interpretation': 'Raw numerical residual ratio; no physical cancellation interpretation',
            'files': [p.name for p in paths]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aggregate', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--signed-sigma', type=float, default=0.)
    parser.add_argument('--title')
    args = parser.parse_args()
    if not math.isfinite(args.signed_sigma):
        raise ValueError('NONFINITE_EXACT_SIGNED_SIGMA')
    args.out.mkdir(parents=True, exist_ok=True)
    summary = json.loads((args.aggregate/'summary.json').read_text())
    tables = {name: read_csv(args.aggregate/name) for name in ('cases.csv', 'history.csv')}
    cases, histories = tables['cases.csv'], tables['history.csv']
    points, figures = [], []
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                         'axes.labelcolor': '#334155', 'axes.edgecolor': '#acb5c1',
                         'text.color': '#253449', 'xtick.color': '#526174', 'ytick.color': '#526174'})
    for cohort in sorted({r['cohort_id'] for r in cases}):
        subset = [(i, row) for i, row in enumerate(cases) if row['cohort_id'] == cohort]
        hsubset = [(i, row) for i, row in enumerate(histories) if row['cohort_id'] == cohort]
        if hsubset:
            figures.append(history_figure(subset, hsubset, cohort, args.out, args.title, points))
        else:
            figures.append(endpoint_figure(subset, cohort, args.out, args.signed_sigma, args.title, points))
    # Focused value check against the original CSV row and field, with exact
    # floating equality; missing values stay null/empty and are not fabricated.
    for p in points:
        source = tables[p['source_table']][p['source_row']]
        if number(source, p['y_field']) != p['y_source_value'] or p['y_plot'] != p['y_source_value']:
            raise AssertionError('POINT_TABLE_Y_MISMATCH')
        if number(source, p['x_field']) != p['x_source_value']:
            raise AssertionError('POINT_TABLE_X_MISMATCH')
        if 'coordinate_y_field' in p and number(source, p['coordinate_y_field']) != p['coordinate_y_value']:
            raise AssertionError('POINT_TABLE_COORDINATE_MISMATCH')
    fields = list(dict.fromkeys(key for row in points for key in row))
    with (args.out/'source_points.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(points)
    inputs = {name: {'path': str((args.aggregate/name).resolve()), 'sha256': sha(args.aggregate/name)}
              for name in ('summary.json', 'cases.csv', 'history.csv', 'provenance.json')}
    report = {'status': 'PENDING_INDEPENDENT_REVIEW', 'point_table_equality': 'PASS',
        'argv': sys.argv, 'input_counts': {'cases': len(cases), 'history_rows': len(histories)},
        'aggregate_counts': {key: summary.get(key) for key in ('expected_count', 'reused_completed_count',
                            'successful_pending_count', 'missing_pending_count', 'history_rows')},
        'inputs': inputs, 'figures': figures, 'source_points': len(points),
        'plotted_points_by_panel': dict(Counter(p['figure']+'/'+p['panel'] for p in points if p['point_status'] == 'PLOTTED')),
        'undefined_points': sum(p['point_status'] != 'PLOTTED' for p in points),
        'cohorts': summary['cohorts'], 'source_points_sha256': sha(args.out/'source_points.csv'),
        'plotter_sha256': sha(__file__), 'requested_execution_model': 'gpt-6.1-sol',
        'observed_runtime_model': None, 'solver_calls': 0, 'native_builds': 0, 'benchmarks': 0,
        'outputs': {file: sha(args.out/file) for figure in figures for file in figure['files']}}
    write_json(args.out/'plot_provenance.json', report)
    print(json.dumps(report, sort_keys=True, allow_nan=False))


if __name__ == '__main__':
    main()
