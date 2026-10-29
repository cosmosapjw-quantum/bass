from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
p=Path(__file__).resolve().parent
rows=json.loads((p/'CE1J_SWEEP.json').read_text())
x=[r['refinement'] for r in rows]
fig,ax=plt.subplots(figsize=(7.3,4.6))
for key,label,mark in [('ce1g_h','CE1-G','o'),('ce1h_h','CE1-H','s'),('ce1i_h','CE1-I','^'),('ce1j_h','CE1-J','D')]:
 ax.plot(x,[r[key] for r in rows],marker=mark,markersize=5,label=label)
ax.axhline(1e-5,color='0.35',linestyle=':',linewidth=1.2,label='Frozen target 1e-5')
ax.set(xscale='log',yscale='log',xlabel='Angular subdivision factor',ylabel='Upper bound on max |Delta h|',title='Same frozen input: certified total error vs refinement')
ax.set_xticks(x,[str(z) for z in x]);ax.legend(frameon=False);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(p/'CE1J_REFINEMENT.png',dpi=180);plt.close(fig)
r=json.loads((p/'CE1J_REF16_REUSE_SHA.json').read_text())
fig,ax=plt.subplots(figsize=(7.3,4.3))
xx=[z['tleft'] for z in r['panels']]
ax.plot(xx,[r['original_global_source_upper']]*4,marker='o',label='CE1-F/G global eta')
ax.plot(xx,[z['adopted_source_cap'] for z in r['panels']],marker='s',label='CE1-J panel-local eta')
ax.set(xlabel='Panel left time u',ylabel='Certified pressure discrepancy upper',title='CE1-J contraction from exact isotropic scale covariance')
ax.set_ylim(bottom=0);ax.legend(frameon=False);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(p/'CE1J_SOURCE_CAP.png',dpi=180);plt.close(fig)
