"""CE1-I quantitative research plots from stored science evidence, no synthetic data."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

base=Path(__file__).resolve().parent
small=json.loads((base/'S1_RESULTS.json').read_text())['scoped_rows']
large=json.loads((base/'S2_REF16.json').read_text())
ref=np.asarray([x['refinement'] for x in small]+[16])
g=np.asarray([x['ce1g_total_h'] for x in small]+[large['ce1g_total_h']])
h=np.asarray([x['ce1h_total_h'] for x in small]+[large['ce1h_total_h']])
i=np.asarray([x['ce1i_total_h'] for x in small]+[large['ce1i_total_h']])
fig,ax=plt.subplots(figsize=(7.0,4.3))
for y,name,mark in [(g,'CE1-G (whole-panel)','o'),(h,'CE1-H (constant P cap)','s'),(i,'CE1-I (panel-local P cap)','^')]:
    ax.plot(ref,y,marker=mark,label=name)
ax.axhline(1e-5,linestyle='--',label=r'Fixed target $10^{-5}$')
ax.set_xscale('log',base=2);ax.set_yscale('log');ax.set_xticks(ref,labels=[str(k) for k in ref])
ax.set_xlabel('Angular refinement (subdivision per cell axis)')
ax.set_ylabel(r'Certified upper bound on $\max_i|\Delta h_i|$')
ax.set_title('Same-physics source + time + binary knot-jump bounds')
ax.grid(True,alpha=.22);ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(base/'CE1I_GEOMETRY_BOUNDS.png',dpi=175)
plt.close(fig)

fig,ax=plt.subplots(figsize=(6.8,4.1))
u=np.asarray([0,.02,.04,.06,.08]);L=np.asarray(large['L_panel'] + [large['L_panel'][-1]])
ax.step(u,L,where='post',label='CE1-I rigorous panel upper')
ax.plot(u[:-1],L[:-1],linestyle='None',marker='o')
ax.axhline(1.3,linestyle='--',label='CE1-H constant upper')
ax.set_xlim(-.002,.082);ax.set_ylim(1.14,1.33)
ax.set_xlabel(r'Normal proper dimensionless time $u=t/T_*$')
ax.set_ylabel(r'Pressure Jacobian $\|DP\|_{\infty}$ upper')
ax.set_title('Certified local pressure Lipschitz coefficients')
ax.grid(True,alpha=.22);ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(base/'CE1I_PANEL_LIPSCHITZ.png',dpi=175)
plt.close(fig)
print('PLOT_PASS')

# The three total-error curves almost coincide on a log scale. Distinguish
# coefficient improvement from a small but positive final-bound improvement.
fig,ax=plt.subplots(figsize=(6.8,4.0))
percent=100*(h-i)/h
ax.plot(ref,percent,marker='o',label='CE1-I gain over CE1-H')
ax.set_xscale('log',base=2);ax.set_xticks(ref,labels=[str(k) for k in ref])
ax.set_xlabel('Angular refinement')
ax.set_ylabel('Reduction of total certified h bound (%)')
ax.set_title('Small actual benefit of the sharper comparison')
ax.grid(True,alpha=.22)
fig.tight_layout()
fig.savefig(base/'CE1I_RELATIVE_GAIN.png',dpi=175)
plt.close(fig)
