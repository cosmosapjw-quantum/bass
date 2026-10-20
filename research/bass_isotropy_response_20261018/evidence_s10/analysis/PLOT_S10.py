#!/usr/bin/env python3
"""Publication-sized figures from saved assessment only; never executes physics."""
import argparse,json,hashlib,math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--assessment',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=True)
 d=json.loads(a.assessment.read_text());plt.rcParams.update({'font.size':9,'axes.labelsize':9,'axes.titlesize':10,'figure.dpi':160,'savefig.dpi':220,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','font.family':'DejaVu Sans'})
 modes=['stream','prepared','cache','simd','simd_cache'];labels=['Stream','Prepared','Cache','SIMD','SIMD + cache'];grid=[(n,k) for n in [16,64,256] for k in [2,16,64]];files=[]
 def save(fig,name):
  for ext in ['png','svg']:
   p=a.output/(name+'.'+ext);fig.savefig(p,bbox_inches='tight');files.append({'path':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
  plt.close(fig)
 lookup={(r['trace'],r['n'],r['cohorts'],r['candidate']):r['paired_speedup']['median'] for r in d['micro']}
 matrices=[np.array([[lookup[(t,n,k,m)] for m in modes] for n,k in grid]) for t in ['changing','jvp_reuse']]
 logs=[np.log2(x) for x in matrices];vmin=min(-.25,min(float(x.min()) for x in logs));vmax=max(.25,max(float(x.max()) for x in logs));norm=TwoSlopeNorm(vmin=vmin,vcenter=0,vmax=vmax)
 fig,axes=plt.subplots(1,2,figsize=(8.5,5.0),layout='constrained',sharey=True)
 for ax,mat,lg,title in zip(axes,matrices,logs,['Changing-state evaluation','16 JVP directions per base point']):
  im=ax.imshow(lg,cmap='RdYlBu',norm=norm,aspect='auto');ax.set_title(title);ax.set_xticks(range(5),labels,rotation=35,ha='right');ax.set_yticks(range(9),[f'{n} / {k}' for n,k in grid])
  for i in range(9):
   for j in range(5):ax.text(j,i,f'{mat[i,j]:.2f}',ha='center',va='center',fontsize=8,color='white' if abs(lg[i,j])/max(abs(vmin),vmax)>.72 else 'black')
 axes[0].set_ylabel('Rays / cohorts');cb=fig.colorbar(im,ax=axes,shrink=.85);cb.set_label('log2 paired speedup (baseline / candidate)')
 fig.suptitle('Kernel speed: fixed workload, unchanged floating-point result',fontsize=11)
 save(fig,'01_kernel_speed')
 cases=['closed_mf_into_ls_r2','closed_small_clock4_r2','flrw_mf_into_ls_fine','flrw_small_clock4_fine'];case_labels=['Closed donor / MF','Closed donor / small','FLRW / MF','FLRW / small'];colors=['#4c78a8','#f58518','#54a24b','#b279a2','#e45756']
 fig,axes=plt.subplots(2,2,figsize=(8.5,5.8),layout='constrained')
 for ax,case,label in zip(axes.flat,cases,case_labels):
  rr=[next(r for r in d['history'] if r['case']==case and r['candidate']==m) for m in modes]
  for j,(r,c) in enumerate(zip(rr,colors)):
   s=r['paired_speedup'];ax.errorbar(s['median'],j,xerr=[[s['median']-s['q1']],[s['q3']-s['median']]],fmt='o',capsize=3,color=c)
  ax.axvline(1,color='0.35',linestyle='--',linewidth=1);ax.set_yticks(range(5),labels);ax.invert_yaxis();ax.set_title(label);ax.grid(axis='x',alpha=.2);ax.set_xlabel('Paired speedup (baseline / candidate)')
 fig.suptitle('Complete histories: median and IQR of seven adjacent pairs',fontsize=11)
 save(fig,'02_history_speed')
 fig,axes=plt.subplots(1,2,figsize=(8.5,3.5),layout='constrained')
 for mode,c,label in [('baseline','#4c78a8','Baseline'),('simd_cache','#e45756','SIMD + cache')]:
  rr=[next(r for r in d['parallel'] if r['workers']==w and r['mode']==mode) for w in [1,2,4]]
  for ax,key,scale in [(axes[0],'batch_seconds',1000),(axes[1],'histories_per_second',1)]:
   med=[r[key]['median']*scale for r in rr];lo=[(r[key]['median']-r[key]['q1'])*scale for r in rr];hi=[(r[key]['q3']-r[key]['median'])*scale for r in rr]
   ax.errorbar([1,2,4],med,yerr=[lo,hi],fmt='o-',capsize=4,color=c,label=label);ax.set_xticks([1,2,4]);ax.set_xlabel('Local Rayon workers');ax.grid(alpha=.2)
 axes[0].set_ylabel('Four-job batch latency (ms)');axes[1].set_ylabel('Histories / second');axes[0].legend(frameon=False);axes[0].set_ylim(bottom=0);axes[1].set_ylim(bottom=0)
 fig.suptitle('Independent histories: pool creation and four unequal jobs included',fontsize=11)
 save(fig,'03_parallel_throughput')
 manifest={'schema':'BASS_S10_FIGURE_MANIFEST_V1','assessment_path':str(a.assessment),'assessment_sha256':hashlib.sha256(a.assessment.read_bytes()).hexdigest(),'plot_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'files':files,'format':'Static scientific figures; PNG and editable SVG; figures sized 8.5 inches wide','captions':{'01_kernel_speed':'Each cell is the median of seven adjacent baseline/candidate time ratios, using the fixed C4 batch count. Same binary64 bits required. Colors are log2 ratios, values are direct ratios. Changing-state and JVP-reuse workloads are distinct.','02_history_speed':'Four fixed existing physical inputs. Points show median paired speedup; error bars are Q1-Q3, not confidence intervals. All 24 representative scientific receipts matched within release. Output, birth, certificate and driver counter fields retained.','03_parallel_throughput':'Each batch runs the four fixed workloads in input order. New pool creation is included in latency. Error bars are Q1-Q3 over seven fixed batches. Unequal task durations, pool overhead and shared-container noise limit scaling; no portable speedup claim.'},'scientific_runs_for_figures':0,'review_status':'AWAITING_VISUAL_INSPECTION'}
 (a.output/'FIGURE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'figures':len(files),'output':str(a.output)}))
if __name__=='__main__':main()
