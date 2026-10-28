"""Saved-result only: no owner/CMB RHS, quadrature or re-execution."""
from pathlib import Path
from fractions import Fraction as Q
import json,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parents[1]
r=json.loads((P/'evidence/PRIMARY.json').read_text());diag=r['diagnostic']
cols=r['structure']['geometry_columns']+r['structure']['charged_columns']
labels=['geo1','geo2','geo3','geo13','H+','He+','He++','Li+','Li++','Li+++']
values=[float(max(abs(Q(v[0])),abs(Q(v[1])))) for i in cols for v in [diag['row_box_exact'][i]]]
fig,ax=plt.subplots(figsize=(9.4,4.9))
ax.bar(range(len(cols)),values,width=.70)
ax.set_xticks(range(len(cols)),labels)
ax.set_yscale('log')
ax.set_xlabel('Reduced30 tau-row column (source coordinate)')
ax.set_ylabel('Supremum of declared row interval (synthetic units)')
ax.set_title('Source-derived 1x30 Thomson optical-depth Jacobian: 10 possible entries')
ax.grid(axis='y',alpha=.2)
fig.text(.02,.025,'K=1, nb/H synthetic diagnostic; NOT a physical opacity or corridor bound',fontsize=9)
fig.tight_layout(rect=(0,.08,1,1))
fig.savefig(P/'figures/TAU_ROW_COLUMN_ENVELOPES.png',dpi=150)
fig.savefig(P/'figures/TAU_ROW_COLUMN_ENVELOPES.svg')
plt.close(fig)
print(json.dumps({'figure':'figures/TAU_ROW_COLUMN_ENVELOPES.png','values':values,'nonzero_columns':cols,'source':'evidence/PRIMARY.json'},indent=2))
