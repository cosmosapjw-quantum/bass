"""Plot pinned completed endpoints; never integrates a trajectory."""
from pathlib import Path
import csv
import hashlib
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

import work_plan


def main():
    root = Path(__file__).resolve().parent
    registry = work_plan.load_completed_registry()
    source = work_plan.BASELINE / work_plan.CASES
    with source.open(newline='') as handle:
        rows = list(csv.DictReader(handle))
    selected = sorted((r for r in rows if float(r['signed_Sigma_requested']) == 0.
                       and float(r['signed_Pi_total_requested']) == 0.),
                      key=lambda r: float(r['signed_Pi_m_requested']))
    if len(selected) != 9:
        raise ValueError('PINNED_CANCELLATION_SLICE_REQUIRES_NINE_POINTS')
    points = [{'case_id': r['case_id'],
               'initial_signed_Pi_m': float(r['signed_Pi_m_requested']),
               'initial_signed_Pi_r': float(r['signed_Pi_r_requested']),
               'final_signed_Pi_total': float(r['final_signed_Pi_total']),
               'final_signed_Sigma': float(r['final_signed_Sigma'])} for r in selected]
    if not np.isfinite([[p[k] for k in p if k != 'case_id'] for p in points]).all():
        raise ValueError('NONFINITE_PLOT_INPUT')
    x = np.array([p['initial_signed_Pi_m'] for p in points]) * 1e4
    plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 5.0), layout='constrained')
    for ax, field, scale, label in [
        (axes[0], 'final_signed_Pi_total', 1e7, r'Final signed $\widetilde\Pi_{\rm tot,h}$  ($10^{-7}$)'),
        (axes[1], 'final_signed_Sigma', 1e11, r'Final signed $\widetilde\Sigma_h$  ($10^{-11}$)')]:
        y = np.array([p[field] for p in points]) * scale
        ax.scatter(x, y, s=49, color='#145c9e', edgecolor='white', linewidth=.7, zorder=4)
        ax.axhline(0, color='#999999', linewidth=.7)
        ax.axvline(0, color='#dddddd', linewidth=.7)
        ax.set_xlabel(r'Initial signed $\widetilde\Pi_{m,h}=-\widetilde\Pi_{r,h}$  ($10^{-4}$)')
        ax.set_ylabel(label)
        ax.set_xticks([-4, -2, -1, 0, 1, 2, 4])
        ax.grid(alpha=.18)
    axes[0].set_title('Stored total-stress response', loc='left')
    axes[1].set_title('Stored shear response', loc='left')
    fig.suptitle('Reuse of the completed cancellation slice\n'
                 r'Warm LRS Bianchi I: $a=0.1999\rightarrow0.2$, initial $\widetilde\Sigma_h=0$',
                 fontsize=15)
    fig.supxlabel('9 stored endpoints from split729; markers are actual samples, with no interpolation.\n'
                  'Source and output pins verified; no new trajectory integration for this figure.', fontsize=10)
    out = root / 'figures'
    out.mkdir(exist_ok=True)
    for suffix in ('png', 'pdf'):
        fig.savefig(out / f'REUSED_CANCELLATION.{suffix}', dpi=170)
    plt.close(fig)
    (out / 'REUSED_CANCELLATION.provenance.json').write_text(json.dumps({
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'source_url': registry['evidence_sources'][work_plan.CASES]['url'],
        'plot_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'points': points, 'points_count': 9, 'new_integrations': 0,
        'interpolation': False, 'smoothing': False,
        'scope': 'Signed half-contraction coordinates; original conditional finite warm pilot endpoints.'
    }, indent=2) + '\n')
    print(json.dumps({'status': 'STORED_DATA_PLOT_GENERATED', 'points': len(points), 'new_integrations': 0}))


if __name__ == '__main__':
    main()
