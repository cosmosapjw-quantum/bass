import json
from pathlib import Path
from zipfile import ZipFile
import matplotlib.pyplot as plt
out=Path(__file__).parent
with ZipFile('/mnt/data/BASS_CE1K_FINAL_20261029.zip') as z: hist=json.loads(z.read('research/ce1k_20261029/SWEEP_IN_PROGRESS.json'))
now8=json.loads(Path('/mnt/data/BASS_CE1M_20261029/REF8_FRESH.json').read_text())
now16=json.loads((out/'CE1M_REF16_SOURCE_ONLY.json').read_text())
rows=hist['rows']
xs=[r['rays'] for r in rows]+[1536]
y1=[r['ce1i_total_h_upper'] for r in rows]+[now16['pr246_prior_local_total']]
y2=[r['total_h_upper'] for r in rows]+[now16['ce1k_total_h_upper']]
assert y2[3]==now8['total_h_upper']
fig,ax=plt.subplots(figsize=(9,5),layout='constrained')
ax.loglog(xs,y1,'o--',label='CE1-I global source (historical)')
ax.loglog(xs,y2,'s-',label='CE1-M panel-local source')
ax.axhline(1e-5,color='black',linestyle=':',label='Fixed 1e-5 threshold')
ax.axvspan(500,2500,alpha=.06)
ax.annotate('Fresh ref8: MET',(384,now8['total_h_upper']),xytext=(150,1.75e-5),arrowprops={'arrowstyle':'->'})
ax.annotate('Fresh source / inherited time at ref16',(1536,now16['ce1k_total_h_upper']),xytext=(280,3.5e-6),arrowprops={'arrowstyle':'->'})
ax.set(xlabel='Number of rays',ylabel='Certified upper bound on max |delta h_i|',title='CE1-M: same frozen Bianchi-I fixture and target')
ax.grid(True,which='both',alpha=.3)
ax.legend(fontsize=9)
fig.savefig(out/'REFINEMENT_SOURCE_COMPARISON.png',dpi=175)
plt.close(fig)
fig,ax=plt.subplots(figsize=(8,4.6),layout='constrained')
panels=now16['panels'];xs=[p['j']+1 for p in panels];vals=[p['adopted_eta'] for p in panels];unif=[vals[0]]*4
ax.plot(xs,unif,'o--',label='Old uniform source cap')
ax.plot(xs,vals,'s-',label='Fresh local MPFR192 source cap')
ax.set_xticks(xs)
ax.set(xlabel='RK4 panel index',ylabel='Max source discrepancy bound',title='CE1-M ref16: expanding-box contraction')
ax.grid(alpha=.3);ax.legend(fontsize=9)
fig.savefig(out/'SOURCE_CAP_REF16.png',dpi=175)
plt.close(fig)
print('Saved 2 plots',out)
