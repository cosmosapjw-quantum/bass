#!/usr/bin/env python3
"""Plot immutable S7 run01 measurements; no solver or quadrature is called.

First extraction: --coupled-run DIR --native-analysis FILE
Standalone reproduction: --data PLOT_DATA_RUN01.json
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile

os.environ['MPLBACKEND'] = 'Agg'
os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir())/'bass-s7-mpl-cache'))
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, FuncFormatter, LogLocator
import numpy as np

HERE = Path(__file__).resolve().parent
COLORS = {'prior': '#667085', 'P2': '#0072B2', 'P24': '#009E73'}
MARKERS = {'prior': 'o', 'P2': 's', 'P24': '^'}
LABELS = {'prior': 'prior', 'P2': 'P2', 'P24': 'P2/P4'}
BAD = '#b2182b'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path, sources):
    raw = path.read_bytes()
    sources.append({'path': str(path.resolve()), 'bytes': len(raw),
                    'sha256': hashlib.sha256(raw).hexdigest()})
    return json.loads(raw)


def extract(coupled, native):
    sources = []
    ret = read(coupled/'RETURN_S7_COUPLED.json', sources)
    comp = read(coupled/'ANGULAR_COMPARISONS.json', sources)
    linear = read(coupled/'RADIATION_LINEAR_BENCHMARK.json', sources)
    native_result = read(native, sources)
    cases = {c['id']: c for c in ret['cases']}
    coupled_rows = []
    for row in comp:
        case = cases[row['id']]
        cfg = case['config']
        failed_gates = [k for k, passed in case['gate_results'].items() if not passed]
        coupled_rows.append({'id': row['id'], 'b0': cfg['b0'], 'n': cfg['n'],
                             'mode': cfg['mode'], 'error': row['max_abs_difference']['y'],
                             'reference': row['reference'], 'status': 'MEASURED',
                             'failed_gates': failed_gates})
    for row in ret['failures']:
        cfg = row['config']
        coupled_rows.append({'id': row['id'], 'b0': cfg['b0'], 'n': cfg['n'],
                             'mode': cfg['mode'], 'error': None, 'status': 'INFEASIBLE',
                             'failure': row['error'], 'birth_u': row['u']})
    native_rows = []
    for row in native_result['metrics']:
        if row['block'] != 'angular':
            continue
        mode = 'P24' if row['mode'] == 'P2P4' else row['mode']
        failed_gates = [f['gate'] for f in native_result['gate_failures'] if f['case_id'] == row['case_id']]
        native_rows.append({'id': row['case_id'], 'b0': row['b0'], 'n': row['n_mu'],
                            'mode': mode, 'error': abs(row['angular_a_error']),
                            'signed_error': row['angular_a_error'], 'status': 'MEASURED',
                            'failed_gates': failed_gates})
    for row in native_result['support_or_numerical_failures']:
        if not row['case_id'].startswith('angular_'):
            continue
        mode = 'P24' if row['mode'] == 'P2P4' else row['mode']
        native_rows.append({'id': row['case_id'], 'b0': row['b0'], 'n': row['n_mu'],
                            'mode': mode, 'error': None, 'status': 'INFEASIBLE',
                            'failure': row['failure'], 'birth_u': row['failed_u']})
    assert len(coupled_rows) == 27 and len(native_rows) == 27
    assert sum(r['status'] == 'INFEASIBLE' for r in coupled_rows) == 8
    assert sum(r['status'] == 'INFEASIBLE' for r in native_rows) == 9
    assert all(np.isfinite(r['error']) and r['error'] > 0
               for r in coupled_rows+native_rows if r['status'] == 'MEASURED')
    plotted_coupled = {r['id'] for r in coupled_rows}
    plotted_native = {r['id'] for r in native_rows}
    output = {'schema': 'bass.s7.original_run01.figure_data.v1', 'sources': sources,
              'data_status': 'Original recorded run01 outcomes; later exact-moment diagnosis does not overwrite them.',
              'linear_benchmark': linear, 'coupled_angular': coupled_rows, 'native_angular': native_rows,
              'coupled_return_status': ret['status'], 'native_return_status': native_result['status'],
              'counts': {'coupled_attempted': ret['cases_attempted'], 'coupled_measured': ret['cases_completed'],
                         'coupled_angular_measured': 19, 'coupled_angular_infeasible': 8,
                         'native_attempted': native_result['rows'], 'native_measured': native_result['measured'],
                         'native_angular_measured': 18, 'native_angular_infeasible': 9},
              'not_shown_cases': {
                  'coupled_reference_cases': [c['id'] for c in ret['cases'] if c['id'] not in plotted_coupled],
                  'native_nonangular_cases': [m['case_id'] for m in native_result['metrics'] if m['case_id'] not in plotted_native],
                  'native_offpanel_gate_failures': [f for f in native_result['gate_failures'] if f['case_id'] not in plotted_native],
                  'other_benchmarks': ['ISOTROPIC_DONOR_BENCHMARK.json', 'BIRTH_REFINEMENT.json'],
                  'reason': 'Panels isolate the coupled linear limit and angular refinement. Separate birth, spectral-panel, bin and slab tests are not overlaid on angular axes.'}}
    # A report writer in another process must not mutate a source during plotting.
    assert all(sha(Path(s['path'])) == s['sha256'] for s in sources)
    return output


def style():
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9.2,
                         'axes.labelsize': 9.2, 'axes.titlesize': 10,
                         'xtick.labelsize': 8.2, 'ytick.labelsize': 8.2,
                         'legend.fontsize': 8.2, 'axes.linewidth': .7,
                         'lines.linewidth': 1.35, 'svg.fonttype': 'none',
                         'svg.hashsalt': 'bass-s7-run01', 'savefig.facecolor': 'white'})


def benchmark(fig, spec, data, single=False, inset_spec=None):
    ax = fig.add_subplot(spec)
    row = data['linear_benchmark']['rows'][0]
    eps = row['epsilon']
    t = row['trajectory']
    x = np.array([r['x'] for r in t])
    for key, color, label in [('q', '#7b3294', r'$q=s/H$'), ('A', '#D55E00', r'$\mathcal{A}=\Delta P/U$')]:
        ax.plot(x, [r[key]/eps for r in t], color=color, label=label)
        ax.plot(x, [r['linear_'+key]/eps for r in t], color=color, linestyle='--', linewidth=1.1)
    ax.axhline(0, color='#d0d5dd', linewidth=.7, zorder=0)
    ax.set(xlabel=r'$x=\ln(a/a_{\rm ref})$', ylabel=r'Amplitude / $\epsilon$', xlim=(0, 2))
    ax.grid(axis='x', color='#eaecf0', linewidth=.7)
    ax.set_title('Coupled radiation:\nnonlinear and linear limit' if single
                 else 'A  Coupled radiation: nonlinear and linear limit',
                 loc='left', fontweight='bold', fontsize=10 if single else 10,
                 pad=10 if single else 12)
    if single:
        ax.set_xticks([0, .5, 1, 1.5, 2], labels=['0', '0.5', '1', '1.5', '2'])
        ax.set_ylabel(r'$q/\epsilon,\;\mathcal{A}/\epsilon$')
    handles = [Line2D([], [], color='#7b3294', label=r'$q$'),
               Line2D([], [], color='#D55E00', label=r'$\mathcal{A}$'),
               Line2D([], [], color='#344054', linestyle='-', label='nonlinear'),
               Line2D([], [], color='#344054', linestyle='--', label='linear')]
    ax.legend(handles=handles, loc='upper right' if single else 'lower left', frameon=False, ncol=2 if single else 4,
              columnspacing=1.0, handlelength=1.8)
    ax.text(.015, .90, r'$\epsilon=0.01$', transform=ax.transAxes, fontsize=9)
    inset = (fig.add_subplot(inset_spec) if inset_spec is not None
             else ax.inset_axes([.67, .64, .31, .29]))
    rows = data['linear_benchmark']['rows']
    eps = np.array([r['epsilon'] for r in rows])
    errors = np.array([r['max_absolute_error'] for r in rows])
    inset.loglog(eps, errors, 'o', color='#111827', markersize=3.8)
    inset.loglog(eps, errors[0]*(eps/eps[0])**2, color='#98a2b3', linestyle='--', linewidth=1)
    inset.set_xlim(.0021, .0118)
    inset.set_ylim(1.7e-6, 6e-5)
    inset.set_xticks([.0025, .005, .01], labels=['2.5', '5', '10'])
    inset.xaxis.set_minor_locator(FixedLocator([]))
    inset.set_yticks([3e-6, 3e-5], labels=[r'$3\,10^{-6}$', r'$3\,10^{-5}$'])
    inset.yaxis.set_minor_locator(FixedLocator([]))
    inset.tick_params(labelsize=7.2, pad=2)
    inset.set_xlabel(r'$\epsilon\;(10^{-3})$', fontsize=7.8, labelpad=1)
    if single:
        inset.set_ylabel('Max absolute error', fontsize=8.2)
    inset.set_title(r'Error; $O(\epsilon^2)$' if single else r'Max error; $O(\epsilon^2)$ guide',
                    fontsize=7.8, pad=3)
    ratios = data['linear_benchmark']['error_ratios']
    text_ax = inset if single else ax
    text_ax.text(.985, -.50 if single else -.27,
                 f'Error ratios: {ratios[0]:.4f}, {ratios[1]:.4f}',
                 transform=text_ax.transAxes, ha='right', fontsize=8, color='#344054')
    return [ax, inset]


def angular_group(fig, spec, data, kind, vertical=False):
    rows = data[kind+'_angular']
    offsets = sorted({r['b0'] for r in rows})
    if vertical:
        grids = spec.subgridspec(3, 1, hspace=.55)
    else:
        grids = spec.subgridspec(1, 3, wspace=.20)
    axes = []
    for column, b0 in enumerate(offsets):
        sub = grids[column].subgridspec(2, 1, height_ratios=[.105, 1], hspace=.055)
        support = fig.add_subplot(sub[0])
        ax = fig.add_subplot(sub[1], sharex=support)
        support.set_xscale('log', base=2)
        support.set_xlim(6.6, 39)
        support.set_ylim(0, 1)
        support.set_yticks([])
        support.tick_params(axis='x', which='both', bottom=False, labelbottom=False)
        for spine in support.spines.values():
            spine.set_visible(False)
        support.set_facecolor('#f2f4f7')
        support.set_title(rf'Fixed-grid offset $b_0={b0:g}$', fontsize=9.2, pad=9)
        if column == 0 or vertical:
            support.text(-.025, .5, 'support', transform=support.transAxes, ha='right', va='center', fontsize=7.1, color='#667085')
        ax.set_xscale('log', base=2)
        ax.set_yscale('log')
        ax.set_xlim(6.6, 39)
        ax.set_xticks([8, 16, 32], labels=['8', '16', '32'])
        ax.xaxis.set_minor_locator(FixedLocator([]))
        ax.grid(which='major', axis='y', color='#eaecf0', linewidth=.6)
        ax.set_xlabel(r'Angular rays $n_\mu$', fontsize=9)
        if kind == 'coupled':
            ax.set_ylim(1e-13, 2e-2)
            ax.set_yticks([1e-12, 1e-9, 1e-6, 1e-3])
        else:
            ax.set_ylim(5e-17, 1)
            ax.set_yticks([1e-15, 1e-10, 1e-5, 1])
            ax.axhline(1e-6, color=BAD, linewidth=.9, linestyle=(0, (3, 3)), zorder=0)
        ax.yaxis.set_minor_locator(FixedLocator([]))
        if column or not vertical:
            if column and not vertical:
                ax.tick_params(labelleft=False)
        if column == 0 or vertical:
            ax.set_ylabel(r'$\max_x|y-y_{\rm GL128}|$' if kind == 'coupled'
                          else r'$|\mathcal{A}-\mathcal{A}_{\rm iso}|$', fontsize=9)
        subset = {(r['n'], r['mode']): r for r in rows if r['b0'] == b0}
        for mode in ('prior', 'P2', 'P24'):
            ns, vals = [], []
            for n in (8, 16, 32):
                rec = subset[n, mode]
                ns.append(n)
                vals.append(rec['error'] if rec['status'] == 'MEASURED' else np.nan)
                if rec['status'] == 'INFEASIBLE':
                    shift = {'prior': -.085, 'P2': -.055, 'P24': .055}[mode]
                    support.plot(n*2**shift, .5, marker='x', markersize=5.4,
                                 markeredgewidth=1.35, color=COLORS[mode], linestyle='none')
                elif rec['failed_gates']:
                    ax.plot(n, rec['error'], marker='o', markersize=8.3, markerfacecolor='none',
                            markeredgecolor=BAD, markeredgewidth=1.3, linestyle='none', zorder=6)
            ax.plot(ns, vals, marker=MARKERS[mode], color=COLORS[mode], label=LABELS[mode],
                    markersize=4.5, linewidth=1.25, zorder=3)
        if kind == 'native' and b0 == .6:
            target = subset[32, 'P24']
            ax.annotate('9.9453e-4\nFAIL vs 1e-6', xy=(32, target['error']), xytext=(8.7, 1e-8),
                        color=BAD, fontsize=8, ha='left', va='center',
                        arrowprops={'arrowstyle': '-', 'color': BAD, 'linewidth': .8})
            ax.text(7.0, 2e-6, '1e-6 target', color=BAD, fontsize=7.3)
        axes.extend([support, ax])
    return axes


def constraint_legend(fig, y=.94):
    handles = [Line2D([], [], color=COLORS[m], marker=MARKERS[m], markersize=4.5,
                      label=LABELS[m]) for m in ('prior', 'P2', 'P24')]
    handles += [Line2D([], [], color='#344054', marker='x', linestyle='none', markersize=5,
                       label='support failure (top strip)'),
                Line2D([], [], color=BAD, marker='o', markerfacecolor='none', linestyle='none',
                       markersize=7, label='recorded gate FAIL')]
    fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(.53, y),
               ncol=3, frameon=False, columnspacing=1.5, handlelength=1.8)


def save(fig, stem, output):
    paths = []
    for extension in ('svg', 'png'):
        path = output/(stem+'.'+extension)
        options = {'metadata': {'Date': None}} if extension == 'svg' else {'dpi': 220}
        fig.savefig(path, **options)
        paths.append(path)
    plt.close(fig)
    return paths


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=Path)
    parser.add_argument('--coupled-run', type=Path)
    parser.add_argument('--native-analysis', type=Path)
    parser.add_argument('--out', type=Path, default=HERE)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    if args.data:
        data = json.loads(args.data.read_text())
        data_path = args.data
    else:
        if not args.coupled_run or not args.native_analysis:
            parser.error('supply --data or both original input paths')
        data = extract(args.coupled_run, args.native_analysis)
        data_path = args.out/'PLOT_DATA_RUN01.json'
        data_path.write_text(json.dumps(data, indent=2)+'\n')
    style()
    outputs = []
    fig = plt.figure(figsize=(7.2, 11.3))
    fig.subplots_adjust(left=.105, right=.98, bottom=.055, top=.867)
    grid = fig.add_gridspec(3, 1, height_ratios=[1, 1.0, 1.0], hspace=.64)
    benchmark(fig, grid[0], data)
    angular_group(fig, grid[1], data, 'coupled')
    angular_group(fig, grid[2], data, 'native')
    fig.suptitle('BASS S7: original run01 results', x=.105, y=.985, ha='left', fontsize=14, fontweight='bold')
    fig.text(.105, .956, 'Coupled gravity and native transport are separate tests; failures are retained.', fontsize=9.1)
    constraint_legend(fig, .946)
    boxes = [grid[i].get_position(fig) for i in range(3)]
    fig.text(.105, boxes[1].y1+.065, 'B  Coupled donor model: angular error', fontweight='bold', fontsize=10.5)
    fig.text(.105, boxes[1].y1+.045, 'Same 64 births; reference: source-frame GL128. 19 measured + 8 support failures.', fontsize=8.5)
    fig.text(.105, boxes[2].y1+.065, 'C  Native prescribed history: angular error', fontweight='bold', fontsize=10.5)
    fig.text(.105, boxes[2].y1+.045, 'Same 16 births; continuum angular reference. 18 measured + 9 support failures.', fontsize=8.5)
    fig.text(.105, .013, r'$b_0$ labels the fixed-grid reference offset, not physical shear. '
             'Red circles preserve original run01 gate failures.', fontsize=8.2)
    outputs += save(fig, 'S7_SUMMARY_RUN01', args.out)

    # Separate 90 mm panels keep text readable without shrinking the summary.
    fig = plt.figure(figsize=(3.54, 4.85))
    fig.subplots_adjust(left=.235, right=.95, bottom=.155, top=.86)
    single_grid = fig.add_gridspec(2, 1, height_ratios=[1.7, 1], hspace=.65)
    benchmark(fig, single_grid[0], data, single=True, inset_spec=single_grid[1])
    outputs += save(fig, 'S7_RADIATION_LINEAR_SINGLE_COLUMN', args.out)
    for kind in ('coupled', 'native'):
        fig = plt.figure(figsize=(3.54, 7.8))
        fig.subplots_adjust(left=.21, right=.97, bottom=.090, top=.845)
        angular_group(fig, fig.add_gridspec(1, 1)[0], data, kind, vertical=True)
        title = 'Coupled angular refinement' if kind == 'coupled' else 'Native angular refinement'
        fig.suptitle(title+'\nOriginal run01', x=.09, y=.982, ha='left', fontsize=10, fontweight='bold')
        handles = [Line2D([], [], color=COLORS[m], marker=MARKERS[m], markersize=4, label=LABELS[m])
                   for m in ('prior', 'P2', 'P24')]
        fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(.56, .935), frameon=False,
                   ncol=3, handlelength=1.2, columnspacing=.8)
        fig.text(.09, .900, 'Top-strip x: infeasible support', fontsize=8)
        fig.text(.09, .882, 'Red circle: recorded gate FAIL', fontsize=8)
        fig.text(.09, .018, r'$b_0$: fixed-grid offset, not physical shear.', fontsize=8)
        outputs += save(fig, 'S7_'+kind.upper()+'_ANGULAR_SINGLE_COLUMN', args.out)

    provenance = {'schema': 'bass.s7.figure_provenance.v1', 'utc': datetime.now(timezone.utc).isoformat(),
                  'status': 'RENDERED_AWAITING_VISUAL_QA', 'source_script_sha256': sha(Path(__file__)),
                  'plot_data': {'path': data_path.name, 'bytes': data_path.stat().st_size, 'sha256': sha(data_path)},
                  'original_sources': data['sources'], 'counts': data['counts'],
                  'outputs': [{'path': p.name, 'bytes': p.stat().st_size, 'sha256': sha(p)} for p in outputs],
                  'not_shown_cases': data['not_shown_cases'],
                  'matplotlib': matplotlib.__version__, 'numpy': np.__version__,
                  'transformations': ['Read-only extraction of reported numerical results; no kernel/projection/ODE/native run.',
                                      'Panel A q and A divided by their initial perturbation epsilon; inset uses reported max errors and an epsilon^2 guide anchored at epsilon=0.01.',
                                      'Panel B uses reported max_x abs(y-y_reference), y=s/H*, for each complete history, including flagged histories.',
                                      'Panel C takes absolute value of the reported native angular A error at the same birth times.',
                                      'Infeasible support crosses use an independent top strip, never an invented numerical error.',
                                      'Original run01 gate-failed points remain circled; later exact-moment diagnosis does not relabel them.'],
                  'interpretive_limits': ['The two angular panels have different observables, source models and geometry histories.',
                                          'b0 controls the fixed coordinate-grid offset; it is not s/H or Sigma.',
                                          'Native per-H transport and final opacity slab are not native coupled Einstein or a reactive EoR history.',
                                          'The 1e-6 line is the recorded large-b native angular target; other modes are shown for comparison.'],
                  'reproduce': 'python3 sourceplot.py --data PLOT_DATA_RUN01.json --out /new/figure-output'}
    (args.out/'FIGURE_PROVENANCE.json').write_text(json.dumps(provenance, indent=2)+'\n')
    print(json.dumps({'outputs': len(outputs), 'plot_data_sha256': sha(data_path), 'counts': data['counts']}, indent=2))


if __name__ == '__main__':
    main()
