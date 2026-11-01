"""Display the genuine 12 source-owned VI0 constrained fluid evolutions, not a surrogate."""
import csv
from collections import defaultdict
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
with (ROOT/'data/VI0_DYNAMIC_PHYSICAL_HISTORIES.csv').open() as f:
    rows=list(csv.DictReader(f))
groups=defaultdict(list)
for row in rows:groups[int(row['case'])].append(row)
fig,ax=plt.subplots(figsize=(8,4.5))
seen=set()
for i,rr in sorted(groups.items()):
    gamma=float(rr[0]['gamma']);label=f'$\\gamma={gamma:.3g}$'
    ax.plot([float(r['u']) for r in rr], [float(r['Omega']) for r in rr],
            label=label if label not in seen else None,linewidth=1.1)
    seen.add(label)
ax.set_xlabel('Hubble-normalized time $u$ (BASS prime time)')
ax.set_ylabel('Normal-frame fluid $\\Omega(u)$')
ax.set_title('12 original BASS tilted VI$_0$ Einstein--perfect-fluid IVPs')
ax.legend(loc='best',fontsize=8)
fig.tight_layout()
for ext in ('png','svg'):
    fig.savefig(ROOT/f'VI0_DYNAMICS_SCIENTIFIC_FIGURE.{ext}',dpi=160)
plt.close(fig)
