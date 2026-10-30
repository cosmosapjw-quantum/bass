"""Draw exact-continuum lower certificate against two historical GL64 anchor values.

The GL64 anchors are retrieved from frozen CE1AF PR284, not independently
recomputed here. They are numerical context, never the proof of strict sign.
"""
from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
with (ROOT/'data'/'CE1AG_RIGOROUS_LOWER_CURVE_401.csv').open() as f:
    rows=list(csv.DictReader(f))
u=[float(r['u']) for r in rows]
q=[float(r['q_lower']) for r in rows]
prior=[.0072784794777280325/.9,.0038525965338533238/.7584190590089559]
fig,ax=plt.subplots(figsize=(7.2,4.7))
ax.plot(u,q,label='continuum: exact-rational certified q lower envelope')
ax.scatter([0,.08],prior,marker='x',s=75,label='CE1AF GL64 anchors (numerical; not proof)')
ax.axhline(.0002,linestyle=':',label='claimed uniform strict bound 1/5000')
ax.set(xlabel='u = t / Tstar',ylabel='q(u) = W/E',title='BASS CE1AG | original six-cell continuum shear-work sign')
ax.set_xlim(0,.08);ax.set_ylim(bottom=0)
ax.grid(alpha=.25);ax.legend(fontsize=8)
fig.tight_layout()
out=ROOT/'data'/'CE1AG_CONTINUUM_SIGN_BOUND.png'
fig.savefig(out,dpi=170);print('PLOT_OK',out)
