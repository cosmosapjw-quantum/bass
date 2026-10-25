"""Render saved B3f evidence only; no quadrature or selector execution."""
from pathlib import Path
import csv
import json
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'

def main():
    raw=json.loads((OUT/'COHORT_INPUT_ERROR_SWEEP.json').read_text());rows=raw['rows'];pairs=[r for r in rows if r['scope']=='MANUFACTURED_FINITE_ENDPOINT']
    flat=[]
    for r in rows:
        co=r.get('pair',{}).get('composition',r.get('composition',{}));b=r.get('ball',{});err=r.get('errors',{})
        flat.append(dict(label=r['label'],scope=r['scope'],family=r.get('family',''),epsilon=r.get('epsilon',''),pair_U=r.get('pair',{}).get('U_pair',''),ball_U=b.get('U_ball',''),
                         ball_status=b.get('status',''),pair_status=co.get('status',''),ideal_total=co.get('ideal_total',''),operational_total=co.get('operational_total',''),Ltrue=co.get('Ltrue',''),
                         actual_pair_tensor=err.get('tensor_absolute',''),actual_combined_relative=err.get('combined_relative',r.get('actual_combined_relative','')),gates_pass=all(r['gates'].values())))
    with (OUT/'ALL_ROWS.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
    summary=dict(status=raw['status'],row_count=len(rows),pair_count=len(pairs),frame_count=sum(r['scope']=='SAVED_ENDPOINT_TWO_FRAME_COVARIANCE' for r in rows),mixture_count=sum(r['scope']=='POSITIVE_FOUR_COHORT_MIXTURE' for r in rows),
                 new_reference_pairs=raw['new_reference_pairs'],kinetic_mapping_checks=sum('kinetic' in r for r in pairs),failed_gates=raw['failed_gates'],controls=raw['controls'],
                 pair_certificate_counts={s:sum(r['pair']['composition']['status']==s for r in pairs) for s in sorted({r['pair']['composition']['status'] for r in pairs})},
                 ball_domain_counts={s:sum(r['ball']['status']==s for r in pairs) for s in sorted({r['ball']['status'] for r in pairs})},
                 max_reference64_96=max(r.get('reference64_96_relative',0) for r in pairs),max_actual_combined_relative=max(r['errors']['combined_relative'] for r in pairs),
                 exact_zero_identity_row=[r['label'] for r in pairs if r['family']=='P0'],scope=raw['scope'],qualifications=raw['qualifications'])
    (OUT/'NUMERICAL_SUMMARY.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    plt.rcParams.update({'font.size':8.,'axes.titlesize':8.5,'axes.labelsize':8.,'xtick.labelsize':7.5,'ytick.labelsize':7.5,'legend.fontsize':7.5,'savefig.dpi':200})
    labels={'P1':'Density','P2':'Map scaling','P3':'Source','P4':'Mixed','P5':'Source-zero'};colors=plt.cm.tab10(np.arange(5));families=list(labels)
    fig,axes=plt.subplots(1,2,figsize=(180/25.4,100/25.4));fig.subplots_adjust(left=.085,right=.98,bottom=.26,top=.78,wspace=.40)
    handles=[]
    for fam,color in zip(families,colors):
        rr=[r for r in pairs if r['family']==fam];x=[r['epsilon'] for r in rr]
        h,=axes[0].loglog(x,[r['pair']['tensor_bound']/r['Q0'][0][0] for r in rr],'-o',color=color,ms=3,label=labels[fam]);handles.append(h)
        axes[0].loglog(x,[r['errors']['tensor_absolute']/r['Q0'][0][0] for r in rr],':',color=color)
        axes[1].loglog(x,[r['pair']['composition']['operational_total'] for r in rr],'-o',color=color,ms=3)
    axes[1].axhline(raw['target'],color='black',ls='--',lw=.8)
    axes[0].set(title='(a) Finite pair error and bound',xlabel='Prescribed epsilon',ylabel='Tensor error / nominal energy')
    axes[1].set(title='(b) Angular + input budget',xlabel='Prescribed epsilon',ylabel='Operational relative bound')
    for ax in axes:ax.grid(True,which='both',alpha=.2)
    fig.legend(handles,[labels[x] for x in families],loc='upper center',ncol=3,frameon=False,bbox_to_anchor=(.5,.99))
    fig.text(.5,.105,'Panel (a): solid = bound; dotted = measured pair error.  Dashed in (b): target 2e-8.',ha='center',fontsize=7.5)
    fig.text(.5,.05,'P0 has exactly zero finite input error and is recorded in the tables; it is excluded from log axes.',ha='center',fontsize=7.5)
    fig.savefig(OUT/'FINITE_INPUT_OVERVIEW.png');plt.close(fig)
    fig,axes=plt.subplots(2,1,figsize=(90/25.4,145/25.4));fig.subplots_adjust(left=.21,right=.97,bottom=.15,top=.83,hspace=.70)
    eps=.01;rr=[next(r for r in pairs if r['family']==fam and r['epsilon']==eps) for fam in families];x=np.arange(5);bottom=np.zeros(5)
    for key,color,label in [('map','#4c78a8','Map'),('source','#f58518','Source'),('prefactor','#54a24b','Density and det R')]:
        values=np.array([r['pair']['prefactor_paths'][r['pair']['chosen_prefactor_path']][key]/r['Q0'][0][0] for r in rr]);axes[0].bar(x,values,bottom=bottom,color=color,label=label);bottom+=values
    axes[0].set_xticks(x,['P1','P2','P3','P4','P5']);axes[0].set(title='(a) Bound terms at epsilon = 0.01',ylabel='Energy bound / nominal energy');axes[0].legend(loc='lower center',bbox_to_anchor=(.5,1.12),ncol=2,frameon=False);axes[0].text(.5,-.30,'Zero terms: P1 map/source; P2 source; P3 map/prefactor.',transform=axes[0].transAxes,ha='center',fontsize=7.5,wrap=True)
    rr=[r for r in pairs if r['family']=='P2'];xx=[r['epsilon'] for r in rr];correct=[r['pair']['composition']['operational_total'] for r in rr];frozen=[(r['pair']['composition']['A0']+np.sqrt(2)*r['pair']['U_pair']+2e-12*r['pair']['composition']['B0'])/r['pair']['composition']['L0'] for r in rr]
    axes[1].loglog(xx,correct,'o-',ms=3,label='Corrected lower energy');axes[1].loglog(xx,frozen,'s--',ms=3,label='Frozen nominal denominator');axes[1].set(title='(b) P2 denominator dependence',xlabel='Prescribed epsilon',ylabel='Operational relative bound');axes[1].legend(loc='upper center',bbox_to_anchor=(.5,-.25),frameon=False)
    for ax in axes:ax.grid(True,alpha=.2,axis='y')
    fig.savefig(OUT/'FINITE_INPUT_TERMS.png');plt.close(fig)
    meta=dict(figures=[dict(path='FINITE_INPUT_OVERVIEW.png',width_mm=180,height_mm=100,panels=2),dict(path='FINITE_INPUT_TERMS.png',width_mm=90,height_mm=145,panels=2)],dpi=200,minimum_font_pt=7.5,legends='outside_axes_inside_native_figure',zeros='P0 explicitly annotated; zero stack contributions retained',source='COHORT_INPUT_ERROR_SWEEP.json')
    (OUT/'FIGURE_PRESENTATION_METADATA.json').write_text(json.dumps(meta,indent=2)+'\n')
    if len(flat)!=24 or summary['row_count']!=len(flat):raise ValueError('saved-output reconciliation count mismatch')
    print(json.dumps(dict(status=summary['status'],rows=len(flat),figures=len(meta['figures']))))
    return raw['status']!='COMPLETED'
if __name__=='__main__':sys.exit(main())
