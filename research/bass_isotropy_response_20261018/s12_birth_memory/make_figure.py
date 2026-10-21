#!/usr/bin/env python3
"""Plot already stored S12 evidence only; no solver or benchmark calls."""
from pathlib import Path
import json,csv,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

UNIT=Path(__file__).resolve().parent
EV=UNIT/'evidence'
def read(relative):return json.loads((EV/relative).read_bytes())
core=read('core_run01/PERFORMANCE.json')
parallel=read('case_parallel_run02/bench/RETURN.json')
fd=read('history_run02/FD_RICHARDSON.json')
omissions=read('history_run02/OMISSION_CONTROLS.json')
support=read('support_run01/result/RETURN_SUPPORT_PREFLIGHT.json')
out=EV/'figure';out.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':12,'axes.labelsize':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
fig,axs=plt.subplots(2,2,figsize=(12.8,9.2))
fig.subplots_adjust(left=.085,right=.965,bottom=.14,top=.84,hspace=.51,wspace=.30)
fig.suptitle('BASS S12 | birth memory and fixed-workload optimization',x=.085,y=.965,ha='left',fontsize=19,fontweight='bold')
fig.text(.085,.918,'Rust f4cd0d53  /  verifier 4e3615dd  /  stored-support observer be773dbf',fontsize=10,color='#4d5969')
fig.text(.085,.887,'Sandbox measurements and reused native evidence. NCP64 execution: NOT RUN.',fontsize=11,color='#9a382f')
rows=[]
def add(panel,series,x,value):rows.append(dict(panel=panel,series=series,x=repr(x),value=repr(value)))
def speed_panel(ax,title,ratios,median,q1,q3):
    x=np.arange(1,len(ratios)+1)
    ax.axhspan(q1,q3,color='#dbe7f3',label='Observed IQR')
    ax.axhline(1,color='#737d89',ls='--',lw=1)
    ax.axhline(median,color='#205b8e',lw=1.5,label=f'Paired median {median:.3f}×')
    ax.plot(x,ratios,'o-',color='#205b8e',ms=6,lw=1.1)
    ax.set(title=title,xlabel='Measured pair (warmups excluded)',ylabel='Paired speedup',xticks=x)
    ax.set_ylim(.97,max(ratios)*1.17)
    ax.grid(axis='y',alpha=.18);ax.legend(frameon=False,fontsize=8.5,loc='upper right')
cr=[p['speedup'] for p in core['all_pairs'] if not p['warmup']]
speed_panel(axs[0,0],'A  Fused augmented callbacks: 24 points / 48 rays',cr,core['paired_speedup_median'],core['paired_speedup_q25'],core['paired_speedup_q75'])
for i,r in enumerate(cr,1):add('A','paired_kernel_speedup',i,r)
pa=[p['speedup'] for p in parallel['pairs'] if not p['warmup']]
speed_panel(axs[0,1],'B  Four whole cases: serial / two workers',pa,parallel['speedup_median'],parallel['speedup_q25'],parallel['speedup_q75'])
for i,r in enumerate(pa,1):add('B','paired_batch_speedup',i,r)
ax=axs[1,0]
values=[fd['fine_Richardson_max_absolute']]+[c['omitted_vs_Richardson_max_absolute'] for c in omissions]
names=['Full tangent','Omit birth memory',r'Omit $\mu_b$',r'Omit $\alpha_b$']
ax.bar(np.arange(4),values,color=['#205b8e','#ad4e3d','#ca7950','#d4a06b'],width=.62)
ax.axhline(1e-8,color='#667481',ls='--',lw=1)
ax.text(3.4,1.5e-8,'Full-tangent gate',ha='right',fontsize=8,color='#667481')
for i,v in enumerate(values):ax.text(i,v*1.7,f'{v:.2e}',ha='center',fontsize=8.5);add('C',names[i],i,v)
ax.set_yscale('log');ax.set_ylim(1e-12,1e-2);ax.set_xticks(np.arange(4),names,rotation=12,ha='right')
ax.set(title='C  Short history: memory terms are identifiable',ylabel='Max absolute difference from fine Richardson')
ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
ax=axs[1,1]
birth=[c['birth'] for c in support['certificates']];Z=[c['z_max']['display_float'] for c in support['certificates']]
ax.axhspan(0,.6,color='#f7e0da',zorder=0)
ax.axhline(.6,color='#a33e32',ls='--',lw=1.3,label=r'Necessary $Z\geq 3/5$')
ax.plot(birth,Z,'o-',color='#205b8e',ms=4,label=r'Stored native $Z=\max\mu_i^2$')
ax.scatter(birth[13:],Z[13:],s=36,color='#aa3f32',zorder=4)
ax.scatter([11],[Z[11]],s=65,facecolors='none',edgecolors='#b47a24',linewidths=1.8,zorder=5)
ax.annotate('First impossible birth: 13',xy=(13,Z[13]),xytext=(6.2,.552),fontsize=9,color='#9a382f',arrowprops=dict(arrowstyle='->',color='#9a382f'))
ax.set(title='D  Original fixed n64 support: a later obstruction',xlabel='Birth index (zero based)',ylabel=r'$Z=\max_i\mu_i^2$',xticks=[0,3,6,9,11,13,15],ylim=(.54,.79))
ax.grid(axis='y',alpha=.18);ax.legend(frameon=False,fontsize=8.5,loc='upper right')
for j,z in zip(birth,Z):add('D','stored_native_Z',j,z)
fig.text(.085,.065,'A: 7 paired samples, 2 warmups. B: 3 paired samples, 1 warmup; process/file costs included.',fontsize=9,color='#4d5969')
fig.text(.085,.043,'IQR is not a confidence interval. C: omission controls retain failed physics gates. D: exact gate = 3/10¹⁵; no native replay.',fontsize=9,color='#4d5969')
fig.text(.085,.021,'No continuum, native full spectral-history, actual MD14/shared-Q, or full-EoR completion is inferred.',fontsize=9,color='#4d5969')
for suffix in ['png','pdf','svg']:fig.savefig(out/('S12_RESULTS.'+suffix),dpi=180)
plt.close(fig)
with (out/'S12_PLOT_DATA.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=['panel','series','x','value']);w.writeheader();w.writerows(rows)
paths=[EV/'core_run01/PERFORMANCE.json',EV/'case_parallel_run02/bench/RETURN.json',EV/'history_run02/FD_RICHARDSON.json',EV/'history_run02/OMISSION_CONTROLS.json',EV/'support_run01/result/RETURN_SUPPORT_PREFLIGHT.json']
meta={'schema':'BASS_S12_STORED_EVIDENCE_FIGURE_V1','inputs':[{'path':str(p.relative_to(UNIT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],'artifacts':[{'path':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.iterdir()) if p.is_file() and p.name != 'FIGURE_MANIFEST.json'],'rows':len(rows),'new_science_or_benchmark_calls':0,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(out/'FIGURE_MANIFEST.json').write_text(json.dumps(meta,indent=2)+'\n')
print(json.dumps({'rows':len(rows),'outputs':[r['path'] for r in meta['artifacts']]}))
