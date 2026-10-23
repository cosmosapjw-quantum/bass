"""Plot saved G1A evidence only. No IVPs or scientific test replay."""
from pathlib import Path
import csv, hashlib, json
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'evidence/controls_001'
FIG = ROOT / 'figures'

def save(fig, name, columns):
    fig.tight_layout()
    fig.savefig(FIG / (name + '.png'), dpi=180)
    fig.savefig(FIG / (name + '.svg'))
    with (FIG / (name + '.csv')).open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(columns.keys())
        writer.writerows(zip(*columns.values()))
    plt.show()
    plt.close(fig)

def main():
    FIG.mkdir(exist_ok=True)
    names = ['closure_mismatch', 'separate_stress', 'collisionless_turnaround']
    if any((FIG / (n + '.png')).exists() for n in names):
        raise FileExistsError('Refuse to overwrite existing rendered evidence')
    good = np.load(RAW / 'V.npz')
    bad = np.load(RAW / 'V_wrong_weight.npz')
    t = good['tau']
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    curves = [(bad['ledger'], 'Mutant: kinetic/ledger mismatch', '-'),
              (bad['kinetic_constraint'], 'Mutant: kinetic constraint', '--'),
              (bad['core_constraint'], 'Mutant: core constraint', ':'),
              (good['kinetic_constraint'], 'Correct: kinetic constraint', '-.')]
    for values, label, ls in curves:
        ax.semilogy(t, np.ma.masked_less_equal(values, 0), ls, label=label, linewidth=1.7)
    ax.axhline(2e-8, linestyle='--', linewidth=1, label='Frozen acceptance gate')
    ax.set(xlabel=r'Fixed-scale proper time $\tau=ct/L_*$', ylabel='Scaled residual (dimensionless)',
           title='Bianchi V: a constraint-only check misses the weight error')
    ax.legend(fontsize=9, loc='center right')
    ax.grid(True, which='major', alpha=.25)
    save(fig, names[0], dict(tau=t, wrong_moment_mismatch=bad['ledger'],
         wrong_kinetic_constraint=bad['kinetic_constraint'], wrong_core_constraint=bad['core_constraint'],
         correct_kinetic_constraint=good['kinetic_constraint']))

    d = np.load(RAW / 'VIII.npz')
    pm, pr = d['pi'][:, 0, 0, 1], d['pi'][:, 1, 0, 1]
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    for values, label, ls in [(pm, 'Massive sector', '-'), (pr, 'Massless sector', '--'),
                              (pm+pr, 'Tensor sum', '-.')]:
        ax.plot(d['tau'], values, ls, label=label, linewidth=1.8)
    ax.set(xlabel=r'Fixed-scale proper time $\tau=ct/L_*$',
           ylabel=r'Signed $\widehat{\pi}_{xy}=\kappa L_*^2\pi^{\rm phys}_{xy}$',
           title='Bianchi VIII: off-diagonal stress from two kinetic sectors')
    ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
    ax.legend(fontsize=10)
    ax.grid(True, alpha=.25)
    save(fig, names[1], dict(tau=d['tau'], massive_pi_xy=pm, massless_pi_xy=pr, total_pi_xy=pm+pr))

    d = np.load(RAW / 'IX_turnaround.npz')
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    ax.plot(d['tau'], d['state'][0], linewidth=1.8, label='Collisionless massive + massless mixture')
    ax.axhline(0, linestyle=':', linewidth=1.2, label='Maximum expansion: h = 0')
    ax.set(xlabel=r'Fixed-scale proper time $\tau=ct/L_*$',
           ylabel=r'$h=L_*H_{\rm phys}/c$',
           title='Closed Bianchi IX control: expansion through contraction')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=.25)
    save(fig, names[2], dict(tau=d['tau'], h=d['state'][0],
         kinetic_constraint=d['kinetic_constraint'], moment_mismatch=d['ledger']))
    receipt = {p.name: dict(bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest())
               for p in FIG.iterdir() if p.suffix in ('.png', '.svg', '.csv')}
    (FIG / 'MANIFEST.json').write_text(json.dumps(receipt, indent=2)+'\n')

if __name__ == '__main__':
    main()
