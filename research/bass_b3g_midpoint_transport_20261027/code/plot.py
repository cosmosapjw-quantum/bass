import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from reconstruct import ROOT
r=json.loads((ROOT/'results/MIDPOINT_ROWS.json').read_text())['rows'];s=json.loads((ROOT/'results/SUMMARY.json').read_text())['fixtures']
fig,axes=plt.subplots(1,2,figsize=(11,4),constrained_layout=True)
for label in ['ISO','ANISO']:
 x=[v for v in r if v['fixture']==label];axes[0].semilogy([v['analytic'][0] for v in x],label=label+' analytic alpha');axes[1].plot([v['eR'] for v in x],label=label+' operational eR')
for a in axes:a.set_xlabel('Saved birth index');a.legend();a.grid(alpha=.3)
axes[0].set_ylabel('Dimensionless radius');axes[1].set_ylabel('Map operator radius');fig.savefig(ROOT/'figures/MIDPOINT_MAP.png',dpi=160);plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(11,4),constrained_layout=True)
for i,v in enumerate(s):
 diff=np.asarray(v['signed_difference']);axes[0].plot(range(3),np.diag(diff[1:,1:])/v['saved'][0][0],marker='o',label=v['fixture']);axes[1].scatter(i,v['relative_difference'],label=v['fixture']+' observed');axes[1].scatter(i,v['relative_bound'],marker='_',s=150,label=v['fixture']+' bound')
axes[0].set_xticks([0,1,2],['xx','yy','zz']);axes[0].set_ylabel('Signed stress difference / saved photon energy');axes[1].set_yscale('log');axes[1].set_xticks([0,1],['ISO','ANISO']);axes[1].set_ylabel('Joint tensor difference / photon energy')
for a in axes:a.legend();a.grid(alpha=.3)
fig.savefig(ROOT/'figures/FINAL_STRESS.png',dpi=160)
