"""Render only this unit's saved manufactured results, never rerun science."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
u=Path(__file__).resolve().parents[1]
s=json.loads((u/'results/SYNTHETIC.json').read_text())
h=[r['dt'] for r in s['refinement']]
a=[r['state_error'] for r in s['refinement']]
b=[r['reward_error'] for r in s['refinement']]
fig,ax=plt.subplots(figsize=(7.2,4.8),layout='constrained')
ax.loglog(h,a,'o-',label='Population carrier')
ax.loglog(h,b,'s-',label='Accumulated rewards')
ax.loglog(h,[a[-1]*(v/h[-1])**4 for v in h],'--',label=r'$h^4$ guide, fine-grid anchor')
ax.set_xlabel('Global time step h [s]');ax.set_ylabel('Maximum absolute error [fixture units]')
ax.set_title('Manufactured variable-M model: reference convergence')
ax.grid(True,which='both',alpha=.25);ax.legend(fontsize=9)
fig.savefig(u/'figures/REFERENCE_CONVERGENCE.png',dpi=180);plt.close(fig)
m=s['mutations'];t=[v['cut_s'] for v in m]
fig,ax=plt.subplots(figsize=(7.2,4.8),layout='constrained')
for key,marker,label in [('QSS_reward_error','o','QSS population reset'),('clock_reset_reward_error','s','Reward clock reset'),('dropped_prefix_reward_error','^','Lost reward prefix'),('QSS_same_law_reward_bound','x','QSS reset analytic bound')]:
 ax.plot(t,[v[key] for v in m],marker+'-',label=label)
ax.set_xlabel('Restart cut [s]');ax.set_ylabel('Maximum reward discrepancy [fixture units]')
ax.set_title('Manufactured negative controls: memory is not disposable')
ax.set_ylim(bottom=0);ax.grid(True,alpha=.25);ax.legend(fontsize=9)
fig.savefig(u/'figures/RESET_REWARD_ERRORS.png',dpi=180);plt.close(fig)
print('Saved two new figures; no scientific driver called.')
