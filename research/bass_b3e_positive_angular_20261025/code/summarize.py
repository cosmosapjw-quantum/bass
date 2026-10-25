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
# Presentation-only C9-V1/V2 repair: all numeric serialization above/below is unchanged.
plt.rcParams.update({'font.size':8,'axes.labelsize':8,'xtick.labelsize':7,
    'ytick.labelsize':7,'legend.fontsize':7.5,'axes.titlesize':9})
floor=1e-18
eta_labels=['0','1/128','1/64','1/32','1/16','1/4','1']
labels=['A'+v for v in eta_labels]+['I'+v for v in eta_labels]+['G1','G2','G3','G4','G5','G1r','G3r','M']
main=rows[:19];src=[v['source_aware']['selected']['points'] for v in main];base=[v['baseline']['selected']['points'] for v in main]
checkrows=rows[14:];res=[]
for v in checkrows:
    inv=[value for key,value in v.get('invariants',{}).items() if not key.startswith('minimum_')]
    inv+=[v.get('packet_tensor_residual',0.),v.get('number_residual',0.),v.get('covariance',{}).get('co_rotated_tensor_residual',0.)]
    res.append(max(inv or [0.]))
figure_metadata=[]
def external_legend(ax,ncol=2,fontsize=7.5):
    return ax.legend(loc='lower left',bbox_to_anchor=(0,1.015),borderaxespad=0,
        ncol=ncol,fontsize=fontsize,frameon=False,columnspacing=1.0,handlelength=2.1)
def error_panel(ax,indices,narrow=False):
    idx=np.array(indices);x=np.arange(len(idx));zero_label_used=False
    for field,label,style in [('frobenius_relative','Frobenius error','o-'),('max_component_relative','Max component error','x--'),('ideal_bound_over_reference','Ideal bound / reference F','s-')]:
        vals=np.array([rows[i]['errors'][field] for i in idx]);ax.plot(x,np.maximum(vals,floor),style,label=label,markersize=3,linewidth=1)
        zero=np.where(vals==0)[0]
        if len(zero):
            ax.scatter(zero,np.full(len(zero),floor),marker='v',s=24,zorder=5,color='#2ca02c',label='Exact zero: display floor' if not zero_label_used else None);zero_label_used=True
    ax.axhline(2e-8,color='#bc2222',ls=':',label='Total target 2e-8',linewidth=1)
    ax.set_yscale('log');ax.set_ylim(4e-19,1e-7);ax.set_ylabel('Error / reference F')
    ax.set_xticks(x,[labels[i] for i in idx],rotation=60 if narrow else 55,ha='right',rotation_mode='anchor')
    ax.grid(axis='y',alpha=.22);ax.set_axisbelow(True);external_legend(ax,1 if narrow else 2,7 if narrow else 7.5)
def cost_panel(ax,horizontal=False):
    xx=np.arange(19)
    if horizontal:
        ax.barh(xx-.18,src,height=.36,label='Source-aware selector');ax.barh(xx+.18,base,height=.36,label='Worst-direction baseline')
        ax.set_yticks(xx,labels[:19]);ax.invert_yaxis();ax.set_xlabel('Positive rays');ax.grid(axis='x',alpha=.22)
    else:
        ax.bar(xx-.18,src,width=.36,label='Source-aware selector');ax.bar(xx+.18,base,width=.36,label='Worst-direction baseline')
        ax.set_xticks(xx,labels[:19],rotation=55,ha='right',rotation_mode='anchor');ax.set_ylabel('Positive rays');ax.grid(axis='y',alpha=.22)
    ax.set_axisbelow(True);external_legend(ax,1 if horizontal else 2,7 if horizontal else 7.5)
def residual_panel(ax,narrow=False):
    xx=np.arange(len(checkrows));ax.plot(xx,np.maximum(res,floor),'o',markersize=3,label='Largest invariant residual')
    ax.axhline(512*np.finfo(float).eps,color='#bc2222',ls=':',linewidth=1,label='512 eps allowance')
    ax.set_yscale('log');ax.set_ylabel('Scaled invariant residual');ax.set_xticks(xx,labels[14:],rotation=45 if narrow else 0,ha='right' if narrow else 'center')
    ax.grid(axis='y',alpha=.22);ax.set_axisbelow(True);external_legend(ax,1 if narrow else 2,7 if narrow else 7.5)
def save_figure(fig,name,width,height,role):
    fig.savefig(OUT/name,dpi=300)
    text_sizes=[float(item.get_fontsize()) for item in fig.findobj(matplotlib.text.Text) if item.get_visible() and item.get_text()]
    figure_metadata.append(dict(path=name,native_width_mm=width,native_height_mm=height,dpi=300,
        minimum_visible_text_pt=min(text_sizes),role=role,legend_placement='Outside data axes',zero_policy='Raw exact zeros unchanged; downward triangle at display floor 1e-18'))
    plt.close(fig)
# Native two-column overview. Fixed axes reserve space for legends and label key.
fig=plt.figure(figsize=(180/25.4,260/25.4));axes=[fig.add_axes(rect) for rect in [(.16,.71,.82,.18),(.16,.415,.82,.17),(.16,.135,.82,.14)]]
error_panel(axes[0],range(22));cost_panel(axes[1]);residual_panel(axes[2])
for ax,title in zip(axes,['a  Angular error: 19 endpoints + 2 orientations + 1 mixture','b  Sufficient positive-rule cost: 19 main endpoints','c  Direct / packet / covariance checks']):ax.set_title(title,loc='left',pad=38)
fig.suptitle('B3e positive angular control',x=.16,y=.985,ha='left',fontsize=10)
fig.text(.16,.065,'Key: A = inherited ANISO; I = inherited ISO; suffix = exact eta.\nG1-G5 = manufactured endpoints; r = canonical rotated pair; M = G1-G4 mixture.',fontsize=7.5,ha='left',va='top')
fig.text(.16,.030,'Mapped endpoints are not time samples. Log display floor = 1e-18.\nRaw values, including exact zeros, are retained in JSON / CSV.',fontsize=7.5,ha='left',va='top')
save_figure(fig,'POSITIVE_ANGULAR_SUMMARY.png',180,260,'Native 180 mm overview')
# Independent single-column layouts: never downscale the dense overview to 90 mm.
for indices,name,title,scope in [(range(14),'POSITIVE_ANGULAR_ERROR_INHERITED_90MM.png','Inherited angular errors','A = ANISO; I = ISO; suffix = exact eta.'),(range(14,22),'POSITIVE_ANGULAR_ERROR_GENERAL_90MM.png','General endpoints and checks','G = manufactured endpoint; r = rotated pair.\nM = positive G1-G4 mixture.')]:
    fig=plt.figure(figsize=(90/25.4,110/25.4));ax=fig.add_axes((.20,.30,.77,.42));error_panel(ax,indices,narrow=True)
    fig.text(.20,.965,title,fontsize=8.5,ha='left',va='top');fig.text(.20,.12,scope,fontsize=7,ha='left',va='top')
    fig.text(.20,.055,'Exact zero: triangle at 1e-18 display floor.\nMapped endpoints; not time samples.',fontsize=7,ha='left',va='top');save_figure(fig,name,90,110,'Separate native 90 mm angular-error panel')
fig=plt.figure(figsize=(90/25.4,140/25.4));ax=fig.add_axes((.20,.17,.77,.66));cost_panel(ax,horizontal=True)
fig.text(.20,.965,'Positive-ray selector cost',fontsize=8.5,ha='left',va='top');fig.text(.20,.075,'A = ANISO; I = ISO; suffix = exact eta.\nG1-G5 = manufactured endpoints.\n19 main mapped endpoints; not time samples.',fontsize=7,ha='left',va='top');save_figure(fig,'POSITIVE_ANGULAR_COST_90MM.png',90,140,'Separate native 90 mm horizontal cost panel')
fig=plt.figure(figsize=(90/25.4,90/25.4));ax=fig.add_axes((.20,.29,.77,.43));residual_panel(ax,narrow=True)
fig.text(.20,.965,'Direct / packet / covariance checks',fontsize=8.5,ha='left',va='top');fig.text(.20,.115,'G = manufactured endpoint; r = rotated pair.\nM = positive G1-G4 mixture.',fontsize=7,ha='left',va='top');save_figure(fig,'POSITIVE_ANGULAR_INVARIANTS_90MM.png',90,90,'Separate native 90 mm invariant panel')
(OUT/'FIGURE_PRESENTATION_METADATA.json').write_text(json.dumps(dict(repair='C9-V1/V2 presentation only',minimum_native_font_requirement_pt=7,figures=figure_metadata),indent=2)+'\n')
summary=dict(status=r['status'],row_count=len(rows),main_endpoint_count=19,orientation_check_count=2,mixture_count=1,failed_gates=r['failed_gates'],
    preserved_old_failures_count=r['old_failures_count'],max_actual_frobenius=max(v['errors']['frobenius_relative'] for v in rows),max_actual_component=max(v['errors']['max_component_relative'] for v in rows),
    main_source_aware_points=src,main_baseline_points=base,main_point_saving=[b-a for a,b in zip(src,base)],
    figure_zero_display_floor=floor,zero_policy='Raw exact zero retained in JSON/CSV; log display only uses floor and explicit zero markers.',
    qualification=r['qualification'])
(OUT/'NUMERICAL_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
