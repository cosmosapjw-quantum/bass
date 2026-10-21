#!/usr/bin/env python3
"""Prepared S8 result plots; NOT EXECUTED when written before the campaign.

This file reads recorded results only. It imports no BASS solver/projector,
performs no quadrature or integration, and never changes science or DAG files.
The parent must notify that actual S8 results are ready before first execution.

First extraction (all arguments are explicit):
  python sourceplot_s8.py --tangent-run DIR --native-run DIR \
    --tangent-prereg FILE --native-prereg FILE --out NEW_DIRECTORY
For the separately published serializer resume, also provide:
  --tangent-resume DIR --tangent-resume-prereg FILE
Standalone reproduction from an archived extraction:
  python sourceplot_s8.py --data PLOT_DATA_S8.json --out NEW_DIRECTORY

One semantic/visual pass follows actual output, policy 08 then policy 07.
The numerical cross-check here re-reads existing finite differences; it is not
a new scientific case, a new tolerance, or a replacement execution verdict.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile

os.environ['MPLBACKEND'] = 'Agg'
os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir())/'bass-s8-mpl-cache'))
for _name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_name] = '1'

PREPARED_PLAN = {
    'status_when_written': 'PREPARED_NOT_EXECUTED',
    'panels': [
        'Tangent: three central-FD step sizes, b/y/joint(h,b,y) errors; Richardson value separate.',
        'Tangent: full versus three omission columns, y error against finest actual nonlinear FD.',
        'Native: fixed-grid b0=.6, all prior/P2/P24 at reused32 and new64/128/256.',
        'Native: fixed-grid b0=.9, same axes/gates; missing support shown separately from error.',
    ],
    'sizes': 'One180mm overview plus four individual90mm panels, each SVG and PNG.',
    'failure_semantics': 'Retain every measured target/gate failure and every support/numerical missing row; no invented error for an unavailable case.',
    'history_semantics': 'Open markers are reused S7 n32 at internal3e-15; filled markers are new S8 n>=64 at internal1e-15. Exact admission remains3/10^15.',
    'scope': 'Manufactured closed-model tangent and prescribed native new-photon angular accuracy are separate experiments.',
    'not_admitted': ['production', 'full EoR', 'native Einstein closure', 'full reactive history'],
}
COLORS = {'prior': '#667085', 'P2': '#0072B2', 'P2P4': '#009E73'}
MARKERS = {'prior': 'o', 'P2': 's', 'P2P4': '^'}
LABELS = {'prior': 'prior', 'P2': 'P2', 'P2P4': 'P2/P4'}
BAD = '#b2182b'
MAIN_QUANTITIES = ('h', 'b', 'y')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bind_native_raw(path, expected_sha, sources):
    """Accept raw or its lossless gzip archive; bind physical and decoded bytes."""
    path = Path(path)
    actual = path if path.exists() else Path(str(path)+'.gz')
    raw = actual.read_bytes()
    decoded = gzip.decompress(raw) if actual.suffix == '.gz' else raw
    decoded_sha = hashlib.sha256(decoded).hexdigest()
    require(decoded_sha == expected_sha, 'native decoded raw SHA')
    sources.append({'path': str(actual.resolve()), 'bytes': len(raw),
                    'sha256': hashlib.sha256(raw).hexdigest(),
                    'decoded_canonical_path': str(path.resolve()),
                    'decoded_bytes': len(decoded), 'decoded_sha256': decoded_sha})


def require(ok, reason):
    if not ok:
        raise ValueError('S8_FIGURE_EVIDENCE_IDENTITY: '+reason)


def read(path, sources, required=True):
    path = Path(path)
    if not path.exists() and not required:
        return None
    raw = path.read_bytes()
    sources.append({'path': str(path.resolve()), 'bytes': len(raw),
                    'sha256': hashlib.sha256(raw).hexdigest()})
    def reject(value):
        raise ValueError('S8_FIGURE_NONFINITE_JSON: '+value)
    return json.loads(raw, parse_constant=reject)


def finite(value):
    if isinstance(value, float):
        require(math.isfinite(value), 'nonfinite numeric value')
    elif isinstance(value, dict):
        for v in value.values():
            finite(v)
    elif isinstance(value, list):
        for v in value:
            finite(v)


def check_fd_from_saved_histories(tangent_run, plan, analytic, assessment, sources):
    """Pure-Python arithmetic on existing JSON; no model or ODE is evaluated."""
    rows = analytic['trajectory']
    window = [i for i, row in enumerate(rows) if row['x'] >= plan['primary']['comparison_x_start']]
    require(bool(window), 'empty tangent comparison interval')
    series = assessment['series']
    eps_values = plan['primary']['epsilon_values']
    require(len(series) == len(eps_values) == 3, 'three preregistered FD steps required')
    recomputed, derivatives = [], []
    for index, eps in enumerate(eps_values):
        pair = [read(tangent_run/f'FD_EPS{index}_{suffix}.json', sources)
                for suffix in ('MINUS', 'PLUS')]
        minus, plus = [p['primal_diagnostics']['trajectory'] for p in pair]
        require(len(minus) == len(plus) == len(rows), 'FD trajectory count')
        require(all(a['x'] == b['x'] == c['x'] for a, b, c in zip(rows, minus, plus)),
                'FD comparison must use the same x')
        require(all(p['epsilon'] == eps for p in pair), 'FD source epsilon')
        require(pair[0]['config']['y0'] == plan['primary']['config']['y0']-eps and
                pair[1]['config']['y0'] == plan['primary']['config']['y0']+eps,
                'symmetric y0 perturbation')
        diff = [{q: (p[q]-m[q])/(2*eps) for q in MAIN_QUANTITIES}
                for m, p in zip(minus, plus)]
        error = {q: max(abs(diff[i][q]-rows[i]['tangent']['full'][q]) for i in window)
                 for q in MAIN_QUANTITIES}
        require(series[index]['epsilon'] == eps, 'assessment epsilon')
        require(all(error[q] == series[index]['max_abs_error_after_x_start'][q]
                    for q in MAIN_QUANTITIES), 'reported FD errors versus saved nonlinear histories')
        require(max(error.values()) == series[index]['h_b_y_joint_max_abs_error'],
                'joint error is max over h,b,y')
        require(all(series[index]['central_derivative'][i][q] == diff[i][q]
                    for i in range(len(rows)) for q in MAIN_QUANTITIES),
                'reported FD derivatives versus saved nonlinear histories')
        derivatives.append(diff)
        recomputed.append({'epsilon': eps, 'max_abs_error': error})
    richardson = {q: max(abs((4*derivatives[-1][i][q]-derivatives[-2][i][q])/3
                             -rows[i]['tangent']['full'][q]) for i in window)
                  for q in MAIN_QUANTITIES}
    require(all(richardson[q] == assessment['fine_richardson_max_abs_error_after_x_start'][q]
                for q in MAIN_QUANTITIES), 'Richardson errors')
    controls = []
    full_y = recomputed[-1]['max_abs_error']['y']
    threshold = max(plan['gates']['negative_control_y_min_abs'],
                    plan['gates']['negative_control_over_full_error_min']*full_y)
    for control in assessment['negative_controls']:
        mode = control['mode']
        error = max(abs(rows[i]['tangent'][mode]['y']-derivatives[-1][i]['y']) for i in window)
        require(error == control['max_abs_y_error_after_x_start'], 'omission control reported error')
        require(control['rejected_by_preregistered_criterion'] == (error >= threshold),
                'omission criterion versus plotted threshold')
        controls.append({'mode': mode, 'error': error, 'threshold': threshold})
    return {'status': 'PASS_EXACT_REPLAY_OF_RECORDED_FLOAT_ARITHMETIC',
            'new_scientific_cases': 0, 'quantities': list(MAIN_QUANTITIES),
            'recomputed_errors': recomputed, 'richardson': richardson, 'controls': controls}


def native_rows(analysis, baseline, plan):
    expected = {r['case_id']: r for r in plan['matrix']}
    measured = {r['case_id']: r for r in analysis['metrics']}
    missing = {r['case_id']: r for r in analysis['support_or_numerical_failures']}
    require(not set(measured) & set(missing), 'native measured and missing rows overlap')
    require(set(measured) | set(missing) == set(expected), 'all18 new native cases must be represented')
    require(len(expected) == analysis['rows'] == 18 and len(measured) == analysis['measured'],
            'native case counts')
    threshold = plan['gates']['angular_accuracy_absolute']
    out = []
    for case_id, cfg in expected.items():
        row = measured.get(case_id, missing.get(case_id))
        require(all(row[k] == cfg[k] for k in ('n_mu', 'b0', 'mode')), 'native axes changed')
        failed = [f['gate'] for f in analysis['gate_failures'] if f['case_id'] == case_id]
        target = None
        if case_id in measured:
            target = abs(row['angular_a_error']) <= threshold
            require(row['accuracy_target_met'] == target, 'native target flag versus error')
        out.append({'id': case_id, 'n': cfg['n_mu'], 'b0': cfg['b0'], 'mode': cfg['mode'],
                    'origin': 'S8_new', 'status': 'MEASURED' if case_id in measured else row['status'],
                    'error': abs(row['angular_a_error']) if case_id in measured else None,
                    'signed_error': row.get('angular_a_error'), 'target_met': target,
                    'failed_gates': failed, 'failure': row.get('failure'),
                    'failed_birth': row.get('failed_birth'), 'failed_u': row.get('failed_u')})
    historical = []
    if baseline is not None:
        require(baseline['reused_sha256'] == plan['reuse_from']['files_sha256'], 'S7 baseline identities')
        base_ids = {r['case_id'] for r in baseline['rows']}
        metrics = {r['case_id']: r for r in baseline['metrics']}
        failures = {r['case_id']: r for r in baseline['failures']}
        require(len(base_ids) == 6 and set(metrics) | set(failures) == base_ids,
                'all6 reused native32 cases must be represented')
        require(baseline['native_reexecution'] is False and baseline['historical_inner_tolerance'] == 3e-15,
                'historical baseline must be reused without execution')
        for case_id in sorted(base_ids):
            row = metrics.get(case_id, failures.get(case_id))
            require(row['n_mu'] == 32 and row['b0'] in (.6, .9), 'historical native axes')
            historical.append({'id': case_id, 'n': 32, 'b0': row['b0'], 'mode': row['mode'],
                               'origin': 'S7_reused', 'status': 'MEASURED' if case_id in metrics else row['status'],
                               'error': abs(row['angular_a_error']) if case_id in metrics else None,
                               'signed_error': row.get('angular_a_error'),
                               'target_met': abs(row['angular_a_error']) <= threshold if case_id in metrics else None,
                               'failed_gates': [], 'failure': row.get('failure'),
                               'failed_birth': row.get('failed_birth'), 'failed_u': row.get('failed_u')})
    return historical+out


def extract(args):
    sources = []
    tp = read(args.tangent_prereg, sources)
    np = read(args.native_prereg, sources)
    nr = read(args.native_run/'RETURN_NATIVE_ANGULAR_REFINEMENT.json', sources)
    recovery = None
    if args.tangent_resume:
        rp = read(args.tangent_resume_prereg, sources)
        tr = read(args.tangent_resume/'RETURN_S8_TANGENT_R2.json', sources)
        require(tr['publication']['preregistration_sha256'] == sha(args.tangent_resume_prereg), 'tangent resume preregistration SHA')
        require(tr['source_sha256'] == rp['source_sha256'], 'tangent resume source identity')
        require(rp['original_source_sha256'] == tp['source_sha256'], 'original tangent source preserved')
        require(rp['original_preregistration_sha256'] == sha(args.tangent_prereg), 'original tangent preregistration preserved')
        require(tr['reused_history_sha256'] == rp['reused_history_sha256'], 'resume history manifest')
        require(tr['integration_accounting']['historical_reruns'] == 0, 'resume must not rerun original histories')
        require(tr['integration_accounting']['original_completed'] == 7 and
                tr['integration_accounting']['new_integrations_attempted'] <= 1,
                'resume integration accounting')
        for name, digest in rp['reused_history_sha256'].items():
            require(sha(args.tangent_run/name) == digest, 'original history SHA: '+name)
        lane = args.tangent_prereg.resolve().parent.parent
        for name, digest in rp['reused_receipt_sha256'].items():
            path = lane/name
            require(sha(path) == digest, 'original receipt SHA: '+name)
            sources.append({'path': str(path.resolve()), 'bytes': path.stat().st_size, 'sha256': digest})
        recovery = {'original_failure': tr['original_failure_retained'],
                    'original_execution_commit': tr['original_execution_commit'],
                    'resume_publication': tr['publication'],
                    'integration_accounting': tr['integration_accounting'],
                    'meaning': 'Original7 integrations reused; serializer repair and originally unrun gauge only.'}
        assessment_dir = args.tangent_resume
    else:
        tr = read(args.tangent_run/'RETURN_S8_TANGENT.json', sources)
        require(tr['preregistration']['preregistration_sha256'] == sha(args.tangent_prereg), 'tangent preregistration SHA')
        require(tr['source_sha256'] == tp['source_sha256'], 'tangent source identity')
        assessment_dir = args.tangent_run
    require(nr['preregistration_sha256'] == sha(args.native_prereg), 'native preregistration SHA')
    require(nr['pinned_sha256'] == np['pinned_sha256'], 'native source identity')
    analytic = read(args.tangent_run/'ANALYTIC_TANGENT.json', sources, required=False)
    assessment = read(assessment_dir/'FINITE_DIFFERENCE_ASSESSMENT.json', sources, required=False)
    gauge = read(assessment_dir/'SOURCE_FRAME_GAUGE.json', sources, required=False)
    analysis = read(args.native_run/'ANALYSIS.json', sources, required=False)
    baseline = read(args.native_run/'REUSED_S7_BASELINE.json', sources, required=False)
    audit = {'tangent': 'UNAVAILABLE_UNTIL_COMPLETE_RECORDED_ASSESSMENT',
             'native': 'UNAVAILABLE_UNTIL_COMPLETE_RECORDED_ANALYSIS'}
    if assessment is not None:
        require(analytic is not None, 'FD assessment without analytic source')
        audit['tangent'] = check_fd_from_saved_histories(args.tangent_run, tp, analytic, assessment, sources)
    rows = []
    if analysis is not None:
        require(nr['analysis_sha256'] == sha(args.native_run/'ANALYSIS.json'), 'native analysis SHA')
        bind_native_raw(args.native_run/'NATIVE_ANGULAR_REFINEMENT.jsonl', nr['raw_sha256'], sources)
        rows = native_rows(analysis, baseline, np)
        audit['native'] = {'status': 'PASS_BYTE_BINDING_AND_CASE_COVERAGE',
                           'new_rows': 18, 'historical_rows': sum(r['origin'] == 'S7_reused' for r in rows)}
    out = {'schema': 'bass.s8.actual_result_figure_data.v1', 'sources': sources,
           'created_utc': datetime.now(timezone.utc).isoformat(), 'plan': PREPARED_PLAN,
           'data_status': 'Original actual S8 execution receipts and separately identified reused S7 native32 evidence.',
           'tangent_status': tr['status'], 'native_status': nr['status'],
           'tangent_receipt': tr, 'native_receipt': nr,
           'tangent_recovery': recovery,
           'tangent_preregistration': tp, 'native_preregistration': np,
           'tangent_assessment': assessment, 'native_rows': rows,
           'native_analysis_summary': ({k: v for k, v in analysis.items() if k != 'metrics'}
                                       if analysis is not None else None),
           'semantic_data_audit': audit,
           'not_plotted': {
               'tangent': 'Full trajectories, E/Pi/Sigma ancillary FD errors, per-cohort and event diagnostics are retained in source files. Main comparison plots use b/y/joint(h,b,y) and the three preregistered omission controls.',
               'native': 'All18 new and all available6 historical cases are represented. Native photon/energy ledger, old-state digests, birth moments and kernel/continuity diagnostics remain separately gated in source files.',
               'gauge': ({'status': 'RECORDED', 'max_h_y_abs': gauge['gauge_max_h_y_abs'],
                          'max_b_minus_one_abs': gauge['gauge_max_b_minus_one_abs']}
                         if gauge is not None else {'status': 'UNAVAILABLE'}),
           }}
    finite(out)
    return out


def style():
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                         'axes.labelsize': 9, 'axes.titlesize': 10,
                         'xtick.labelsize': 8, 'ytick.labelsize': 8,
                         'legend.fontsize': 8, 'axes.linewidth': .7,
                         'lines.linewidth': 1.25, 'svg.fonttype': 'none',
                         'svg.hashsalt': 'bass-s8-original-results',
                         'savefig.facecolor': 'white'})


def unavailable(ax, title, reason):
    ax.set_axis_off()
    ax.set_title(title, loc='left', fontweight='bold')
    ax.text(.5, .55, 'No completed recorded assessment', transform=ax.transAxes,
            ha='center', va='center', fontsize=10, color=BAD)
    ax.text(.5, .37, reason, transform=ax.transAxes, ha='center', va='center',
            fontsize=8, wrap=True)


def error_floor(values):
    positive = [v for v in values if v > 0]
    return max(1e-18, min(positive)*.3) if positive else 1e-18


def convergence(ax, data, label='A'):
    import matplotlib.lines as lines
    from matplotlib.ticker import FixedLocator
    a = data['tangent_assessment']
    title = f'{label}  Central-difference convergence'
    if a is None:
        return unavailable(ax, title, 'See the retained tangent execution failure.')
    series = a['series']
    eps = [r['epsilon'] for r in series]
    values = {'b': [r['max_abs_error_after_x_start']['b'] for r in series],
              'y': [r['max_abs_error_after_x_start']['y'] for r in series],
              'joint': [r['h_b_y_joint_max_abs_error'] for r in series]}
    floor = error_floor([v for vs in values.values() for v in vs])
    for key, color, marker, size, name in [('joint', '#344054', 'o', 7, 'joint (h,b,y)'),
                                         ('b', '#7b3294', 's', 4, 'b'),
                                         ('y', '#D55E00', '^', 4, 'y')]:
        ax.plot(eps, [v if v > 0 else floor for v in values[key]], color=color,
                marker=marker, markersize=size, markerfacecolor='none' if key == 'joint' else color,
                label=name)
        ratios = a['order2_ratios']['h_b_y_joint' if key == 'joint' else key]
        lo, hi = data['tangent_preregistration']['gates']['central_difference_order2_ratios']
        if not all(v is not None and lo <= v <= hi for v in ratios):
            ax.plot(eps, [v if v > 0 else floor for v in values[key]], 'o', markersize=9,
                    markerfacecolor='none', markeredgecolor=BAD, linestyle='none')
    guide = values['joint'][0]*.35
    if guide > 0:
        ax.plot(eps, [guide*(e/eps[0])**2 for e in eps], '--', color='#98a2b3', label=r'$\epsilon^2$ guide')
    ax.set(xscale='log', yscale='log', xlabel=r'Nonlinear FD step $\epsilon$',
           ylabel=r'Max $|D_\epsilon-\partial_{y_0}|$',
           xlim=(min(eps)/1.3, max(eps)*1.3))
    ax.set_xticks(sorted(eps), labels=[f'{e:g}' for e in sorted(eps)])
    ax.xaxis.set_minor_locator(FixedLocator([]))
    ax.yaxis.set_minor_locator(FixedLocator([]))
    ax.grid(axis='y', color='#eaecf0', linewidth=.6)
    ax.set_title(title, loc='left', fontweight='bold', pad=10)
    ax.legend(frameon=False, loc='upper left', handlelength=1.5, ncol=2)
    r = max(a['fine_richardson_max_abs_error_after_x_start'][q] for q in MAIN_QUANTITIES)
    gate = data['tangent_preregistration']['gates']['fine_richardson_h_b_y_max_abs']
    ax.text(.98, .035, f'Richardson: {r:.2e}\ngate {gate:.0e}; '+('PASS' if r <= gate else 'FAIL'),
            transform=ax.transAxes, ha='right', va='bottom', fontsize=8,
            color='#344054' if r <= gate else BAD)


def controls(ax, data, label='B'):
    from matplotlib.ticker import FixedLocator
    a = data['tangent_assessment']
    title = f'{label}  Birth sensitivity terms'
    if a is None:
        return unavailable(ax, title, 'No omission-control comparison is invented.')
    full = a['series'][-1]['max_abs_error_after_x_start']['y']
    names = ['full', 'omit_birth_memory', 'omit_mu_b', 'omit_alpha_b']
    by_mode = {r['mode']: r for r in a['negative_controls']}
    values = [full]+[by_mode[m]['max_abs_y_error_after_x_start'] for m in names[1:]]
    gates = data['tangent_preregistration']['gates']
    threshold = max(gates['negative_control_y_min_abs'], gates['negative_control_over_full_error_min']*full)
    floor = error_floor(values+[threshold])
    shown = [v if v > 0 else floor for v in values]
    bars = ax.bar(range(4), shown, width=.56, color=['#344054', '#E69F00', '#D55E00', '#CC79A7'])
    ax.set_yscale('log')
    ax.axhline(threshold, color='#667085', linestyle='--', linewidth=1)
    for i, (bar, value) in enumerate(zip(bars, values)):
        ax.text(i, shown[i]*1.2, f'{value:.1e}', ha='center', va='bottom', fontsize=8)
        if i and not by_mode[names[i]]['rejected_by_preregistered_criterion']:
            ax.plot(i, shown[i], 'o', markersize=10, markerfacecolor='none',
                    markeredgecolor=BAD, markeredgewidth=1.4)
    ax.set_xticks(range(4), labels=['full', 'omit birth\nmemory', r'omit $\mu_b$', r'omit $\alpha_b$'])
    ax.yaxis.set_minor_locator(FixedLocator([]))
    ax.set_ylim(floor*.6, max(shown+[threshold])*12)
    ax.set_ylabel(r'Max $y$ error to finest nonlinear FD')
    ax.set_title(title, loc='left', fontweight='bold', pad=10)
    passed = sum(r['rejected_by_preregistered_criterion'] for r in a['negative_controls'])
    ax.text(.98, .97, f'{passed}/3 controls rejected\nthreshold {threshold:.1e}',
            transform=ax.transAxes, ha='right', va='top', fontsize=8,
            color='#344054' if passed == 3 else BAD)
    ax.grid(axis='y', color='#eaecf0', linewidth=.6)
    ax.set_axisbelow(True)


def native_panel(ax, data, b0, label):
    from matplotlib.lines import Line2D
    from matplotlib.ticker import FixedLocator
    title = rf'{label}  Native fixed-grid offset $b_0={b0:g}$'
    rows = [r for r in data['native_rows'] if r['b0'] == b0]
    if not rows:
        return unavailable(ax, title, 'No completed native angular analysis was recorded.')
    fig = ax.figure
    spec = ax.get_subplotspec()
    ax.remove()
    sub = spec.subgridspec(2, 1, height_ratios=[.10, 1], hspace=.025)
    status_ax = fig.add_subplot(sub[0])
    ax = fig.add_subplot(sub[1])
    status_ax.set(xscale='log', xlim=(25, 320), ylim=(0, 1))
    status_ax.set_yticks([])
    status_ax.tick_params(axis='x', which='both', bottom=False, labelbottom=False)
    status_ax.set_facecolor('#f2f4f7')
    for spine in status_ax.spines.values():
        spine.set_visible(False)
    status_ax.set_title(title, loc='left', fontweight='bold', pad=8)
    status_ax.text(-.025, .5, 'missing', transform=status_ax.transAxes,
                   ha='right', va='center', fontsize=7, color='#667085')
    threshold = data['native_preregistration']['gates']['angular_accuracy_absolute']
    positive = [r['error'] for r in data['native_rows'] if r['error'] is not None and r['error'] > 0]
    floor = error_floor(positive+[threshold])
    ceiling = max(positive+[threshold])*3
    ax.set(xscale='log', yscale='log', xlim=(25, 320), ylim=(floor*.6, ceiling),
           xlabel=r'Angular rays $n_\mu$', ylabel=r'$|\mathcal{A}_{\rm new}-\mathcal{A}_{\rm ref}|$')
    ax.set_xticks([32, 64, 128, 256], labels=['32', '64', '128', '256'])
    ax.xaxis.set_minor_locator(FixedLocator([]))
    ax.yaxis.set_minor_locator(FixedLocator([]))
    ax.axhline(threshold, color=BAD, linestyle=(0, (4, 3)), linewidth=1)
    by = {(r['n'], r['mode']): r for r in rows}
    for mode in ('prior', 'P2', 'P2P4'):
        ns, vals = [], []
        for n in (32, 64, 128, 256):
            row = by.get((n, mode))
            ns.append(n)
            vals.append(row['error'] if row is not None and row['error'] is not None and row['error'] > 0 else math.nan)
            if row is None:
                continue
            if row['status'] != 'MEASURED':
                shift = {'prior': -.10, 'P2': -.07, 'P2P4': .07}[mode]
                marker = 'x' if row['status'] == 'FEASIBILITY_FAILURE' else '+'
                status_ax.plot(n*2**shift, .5, marker=marker, color=COLORS[mode], markersize=7,
                               markeredgewidth=1.3, linestyle='none')
                continue
            value = row['error'] if row['error'] > 0 else floor
            marker = MARKERS[mode] if row['error'] > 0 else 'v'
            ax.plot(n, value, marker=marker, color=COLORS[mode], markersize=5.2,
                    markerfacecolor='white' if row['origin'] == 'S7_reused' else COLORS[mode],
                    markeredgewidth=1.1, linestyle='none', zorder=4)
            if not row['target_met'] or row['failed_gates']:
                ax.plot(n, value, 'o', markerfacecolor='none', markeredgecolor=BAD,
                        markersize=9, markeredgewidth=1.25, linestyle='none', zorder=5)
        # Only new orders share the same internal stopping margin. Historical32
        # is an open reference marker, not an uninterrupted refinement segment.
        ax.plot(ns[1:], vals[1:], color=COLORS[mode], linewidth=1.15, zorder=2)
    ax.grid(axis='y', color='#eaecf0', linewidth=.6)
    handles = [Line2D([], [], color=COLORS[m], marker=MARKERS[m], markersize=4,
                      label=LABELS[m]) for m in ('prior', 'P2', 'P2P4')]
    ax.legend(handles=handles, frameon=False, loc='upper right', ncol=3,
              handlelength=1.1, columnspacing=.9)
    ax.text(.98, .15, r'target $10^{-6}$', transform=ax.transAxes,
            ha='right', fontsize=8, color=BAD)


def save(fig, out, stem, outputs):
    import matplotlib.pyplot as plt
    for ext in ('svg', 'png'):
        p = out/(stem+'.'+ext)
        fig.savefig(p, dpi=300, metadata={'Date': None} if ext == 'svg' else None)
        outputs.append({'path': str(p.resolve()), 'bytes': p.stat().st_size, 'sha256': sha(p)})
    plt.close(fig)


def render(data, out):
    import matplotlib.pyplot as plt
    style()
    outputs = []
    width = 180/25.4
    fig, axes = plt.subplots(2, 2, figsize=(width, 7.4), layout='constrained')
    convergence(axes[0, 0], data)
    controls(axes[0, 1], data)
    native_panel(axes[1, 0], data, .6, 'C')
    native_panel(axes[1, 1], data, .9, 'D')
    fig.suptitle('S8: full tangent and native angular refinement', fontsize=12, fontweight='bold')
    save(fig, out, 'S8_SUMMARY_180mm', outputs)
    panels = [('TANGENT_CONVERGENCE', lambda ax: convergence(ax, data)),
              ('TANGENT_CONTROLS', lambda ax: controls(ax, data)),
              ('NATIVE_B06', lambda ax: native_panel(ax, data, .6, 'C')),
              ('NATIVE_B09', lambda ax: native_panel(ax, data, .9, 'D'))]
    for name, draw in panels:
        fig, ax = plt.subplots(figsize=(90/25.4, 3.45), layout='constrained')
        draw(ax)
        save(fig, out, 'S8_'+name+'_90mm', outputs)
    return outputs


def caption(data):
    recovery_note = ('The original tangent run01 process exit1 from numpy.bool serialization is retained. '
                     'Its7 completed integrations are reused by SHA; the separately published resume converts one boolean '
                     'and performs only the originally unrun gauge integration. The displayed tangent status belongs '
                     'to that separately recorded recovery, not to a relabeled original process.\n'
                     if data.get('tangent_recovery') else '')
    return f'''# S8 actual-output figure caption and scope

**Recorded statuses:** tangent `{data['tangent_status']}`; native `{data['native_status']}`.
These execution statuses are retained verbatim. The plotting step does not override any scientific gate.

{recovery_note}

**A — Central-difference convergence.** Three actual symmetric nonlinear perturbation pairs are compared with the full analytic derivative with respect to initial signed shear y0 at fixed x and Hstar. The plotted errors are maxima for x>=0.2. Joint means max over h,b,y. The epsilon-squared curve is an offset order guide, not a fitted result. Richardson accuracy is reported separately from central-difference accuracy. A red outline marks a recorded failure of an applicable order check.

**B — Birth sensitivity terms.** The full column and each of the three incomplete diagnostic columns are compared with the finest actual nonlinear finite difference for y. The dashed threshold is the maximum of the preregistered absolute discrimination threshold and100 times the full-column FD error. A control below that threshold was not successfully discriminated; it remains a failed test. The signed alpha_b is a derivative, not a negative physical weight.

**C–D — Native angular refinement.** Every measured prior/P2/P24 point at b0=.6/.9 is shown. The horizontal red line is the unchanged1e-6 target for the new-photon observable A_new=DeltaP_new/U_new. A red outline marks a target miss or a recorded new-row integrity failure. The overall finest-order target applies to n256; lower-order misses remain visible. The same vertical range is used in both panels. A support failure is marked x in the separate upper status strip, and a numerical failure is marked +; neither is assigned a numerical angular error.

Open n32 markers are the byte-bound historical S7 execution reused without rerunning it. Filled n64/128/256 markers are the new S8 execution. Historical internal projection stopping tolerance was3e-15 and new orders use1e-15; the exact stored-binary64 moment admission remains3/10^15 throughout. This numerical margin distinction is not an angular-resolution change. Lines connect only the new orders, which share the same margin and the same spectral/birth-time/bin settings.

b0 is a fixed-coordinate-grid offset and conditioning parameter; beta=.2 fixes the prescribed native shear history. It must not be read as a coordinate-invariant physical shear comparison. The native plot isolates new photons, so old n32 stock cannot dilute its accuracy measure. Old stock, spectral-owner identity and native photon/energy ledger checks are separately retained in the source files.

If an observed floating difference is exactly zero, a downward marker at the display floor denotes that recorded zero; it does not prove mathematically exact continuum agreement. No missing or failed case is assigned a fabricated error. Data absent because execution stopped are labeled unavailable.

These panels do not admit production/full EoR, native Einstein/MD14 energy closure, evolving reactive history, continuum spectral accuracy, or continuum angular accuracy merely from moment matching. The manufactured closed-model tangent and prescribed native experiment are distinct leaves. Raw/preregistration/analysis/receipt identities and all not-plotted diagnostics are listed in PLOT_DATA_S8.json and FIGURE_PROVENANCE.json.

Visual audit remains a separate actual-image pass: policy08 hostile/semantic audit, then policy07 residual/legibility pass at180mm overview and90mm individual panels.
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path)
    parser.add_argument('--tangent-run', type=Path)
    parser.add_argument('--native-run', type=Path)
    parser.add_argument('--tangent-prereg', type=Path)
    parser.add_argument('--tangent-resume', type=Path)
    parser.add_argument('--tangent-resume-prereg', type=Path)
    parser.add_argument('--native-prereg', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if bool(args.tangent_resume) != bool(args.tangent_resume_prereg):
        parser.error('--tangent-resume and --tangent-resume-prereg must be provided together')
    if args.data:
        reproduction = []
        data = read(args.data, reproduction)
        require(data['schema'] == 'bass.s8.actual_result_figure_data.v1', 'standalone figure data schema')
    else:
        if not all((args.tangent_run, args.native_run, args.tangent_prereg, args.native_prereg)):
            parser.error('all four actual-result input paths are required without --data')
        data = extract(args)
        reproduction = []
    finite(data)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    data_path = out/'PLOT_DATA_S8.json'
    data_path.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False)+'\n')
    outputs = render(data, out)
    caption_path = out/'FIGURE_CAPTION.md'
    caption_path.write_text(caption(data))
    if not args.data:
        require(all(sha(s['path']) == s['sha256'] for s in data['sources']), 'source changed during plotting')
    import matplotlib
    record = {'schema': 'bass.s8.figure_provenance.v1',
              'status': 'ACTUAL_DATA_RENDERED_PENDING_SINGLE_VISUAL_AUDIT',
              'created_utc': datetime.now(timezone.utc).isoformat(),
              'sourceplot': {'path': str(Path(__file__).resolve()), 'sha256': sha(__file__)},
              'data_sha256': sha(data_path), 'caption_sha256': sha(caption_path),
              'sources': data['sources'], 'reproduction_input': reproduction,
              'semantic_data_audit': data['semantic_data_audit'], 'outputs': outputs,
              'python': sys.version, 'matplotlib': matplotlib.__version__,
              'new_scientific_cases': 0, 'S7_rerun': False,
              'visual_audit': 'Not yet performed: policy08 then07, one finite pass.',
              'source_files_mutated': False, 'plan': PREPARED_PLAN}
    p = out/'FIGURE_PROVENANCE.json'
    p.write_text(json.dumps(record, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'status': record['status'], 'out': str(out), 'figures': len(outputs),
                      'provenance_sha256': sha(p), 'new_scientific_cases': 0}))


if __name__ == '__main__':
    main()
