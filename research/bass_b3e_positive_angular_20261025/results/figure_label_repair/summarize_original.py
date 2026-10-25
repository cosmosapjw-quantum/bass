"""Serialize all raw rows and actual diagnostic figure; no scientific rerun."""
import csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'
r=json.loads((OUT/'POSITIVE_ANGULAR_SWEEP.json').read_text());rows=r['rows']
allrows=[];cost=[]
for row in rows:
    e=row['errors'];b=row.get('source_aware',{}).get('selected',{});old=row.get('baseline',{}).get('selected',{})
    flat=dict(label=row['label'],scope=row['scope'],K=b.get('K'),points=b.get('points',row.get('points')),baseline_K=old.get('K'),baseline_points=old.get('points'),
        bound_relative=b.get('bound_relative',row.get('bound_relative')),**e,all_gates_pass=all(row['gates'].values()),
        old_Q14_tensor_error=row.get('old_errors_unchanged',{}).get('Q14',{}).get('tensor'),old_Q26_tensor_error=row.get('old_errors_unchanged',{}).get('Q26',{}).get('tensor'),
        failed_gates=';'.join(k for k,v in row['gates'].items() if not v))
    for key,value in row.get('invariants',{}).items():flat['invariant_'+key]=value
    for key,value in row.get('covariance',{}).items():
        if isinstance(value,(float,int,bool)):flat['covariance_'+key]=value
    allrows.append(flat)
    for strategy in ['source_aware','baseline']:
        if strategy in row:
            for candidate in row[strategy]['history']:cost.append(dict(label=row['label'],scope=row['scope'],strategy=strategy,selected=candidate['K']==row[strategy]['selected']['K'],**candidate))
def writecsv(path,data):
    fields=list(dict.fromkeys(key for row in data for key in row))
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(data)
writecsv(OUT/'ALL_ROWS.csv',allrows);writecsv(OUT/'SELECTOR_COST.csv',cost)
plt.rcParams.update({'font.size':9});fig,axes=plt.subplots(3,1,figsize=(13,12),gridspec_kw={'height_ratios':[1.25,1,.9]},layout='constrained')
x=np.arange(len(rows));labels=[v['label'].replace('B3d_','').replace('_eta',' e=') for v in rows]
# True zeros remain exact in JSON/CSV. Log display only masks them at 1e-18.
floor=1e-18
for field,label,style in [('frobenius_relative','Actual full tensor Frobenius','o-'),('max_component_relative','Actual max component','x--'),('ideal_bound_over_reference','Ideal truncation bound / reference F','s-')]:
    vals=np.array([v['errors'][field] for v in rows]);axes[0].plot(x,np.maximum(vals,floor),style,label=label,markersize=4)
    zero=np.where(vals==0)[0]
    if len(zero):axes[0].scatter(zero,np.full(len(zero),floor),marker='v',s=50,label=f'{label}: exact zero (display floor)')
axes[0].axhline(2e-8,color='red',ls=':',label='Unchanged total target 2e-8');axes[0].set_yscale('log');axes[0].set_ylabel('Error / reference energy F');axes[0].legend(ncol=2,fontsize=8)
axes[0].set_title('B3e positive angular control: 19 mapped endpoints, 2 orientation checks, 1 positive mixture')
main=rows[:19];xx=np.arange(19);src=[v['source_aware']['selected']['points'] for v in main];base=[v['baseline']['selected']['points'] for v in main]
axes[1].bar(xx-.18,src,width=.36,label='Source-aware sufficient selector');axes[1].bar(xx+.18,base,width=.36,label='Stated worst-direction baseline');axes[1].set_ylabel('Positive rays');axes[1].legend()
checkrows=rows[14:];cx=np.arange(len(checkrows));res=[]
for v in checkrows:
    inv=[value for key,value in v.get('invariants',{}).items() if not key.startswith('minimum_')]
    inv+=[v.get('packet_tensor_residual',0.),v.get('number_residual',0.),v.get('covariance',{}).get('co_rotated_tensor_residual',0.)]
    res.append(max(inv or [0.]))
axes[2].plot(cx,np.maximum(res,floor),'o',label='Largest direct/packet/covariance invariant residual');axes[2].axhline(512*np.finfo(float).eps,color='red',ls=':',label='512 eps allowance');axes[2].set_yscale('log');axes[2].set_ylabel('Scaled invariant residual');axes[2].set_xticks(cx,[v['label'] for v in checkrows],rotation=25,ha='right');axes[2].legend(fontsize=8)
for ax in axes[:2]:ax.set_xticks(x if ax is axes[0] else xx,labels if ax is axes[0] else labels[:19],rotation=65,ha='right');ax.grid(axis='y',alpha=.25)
fig.supxlabel('Endpoint labels are manufactured/reused mapped cohorts; these are not time samples. Log display floor 1e-18 only; raw zeros retained.')
fig.savefig(OUT/'POSITIVE_ANGULAR_SUMMARY.png',dpi=160);plt.close(fig)
summary=dict(status=r['status'],row_count=len(rows),main_endpoint_count=19,orientation_check_count=2,mixture_count=1,failed_gates=r['failed_gates'],
    preserved_old_failures_count=r['old_failures_count'],max_actual_frobenius=max(v['errors']['frobenius_relative'] for v in rows),max_actual_component=max(v['errors']['max_component_relative'] for v in rows),
    main_source_aware_points=src,main_baseline_points=base,main_point_saving=[b-a for a,b in zip(src,base)],
    figure_zero_display_floor=floor,zero_policy='Raw exact zero retained in JSON/CSV; log display only uses floor and explicit zero markers.',
    qualification=r['qualification'])
(OUT/'NUMERICAL_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
