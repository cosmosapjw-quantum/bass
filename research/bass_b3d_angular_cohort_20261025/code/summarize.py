"""Mechanical frozen-gate assembly and original-data figure; no new sweep."""
from pathlib import Path
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import angular_cohort as ac
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'results'

def main():
    raw=json.loads((R/'COHORT_SWEEP.json').read_text());tests=json.loads((R/'TEST_RESULTS.json').read_text())
    rows=raw['fixtures'];order_rows=[];leading_checks=[];benchmark=[]
    for label in ac.SOURCES:
        small=[r for r in rows if r['source']==label and 0<r['eta']<=1/16]
        for name in ['Q14','Q26']:
            for a,b in zip(small[:-1],small[1:]):
                order_rows.append(dict(source=label,rule=name,eta_small=a['eta'],eta_large=b['eta'],
                    **{field:ac.observed_order(a['rules'][name]['errors'][field],b['rules'][name]['errors'][field]) for field in ['energy','pressure','pi','tensor']}))
        entry=small[0]['rules']['Q14']
        leading_checks.append(dict(source=label,eta=small[0]['eta'],energy_relative_difference=entry['leading_energy_relative_difference'],pressure_relative_difference=entry['leading_pressure_relative_difference']))
    for row in rows:
        for name,entry in row['rules'].items():benchmark.append(dict(source=row['source'],eta=row['eta'],rule=name,**entry['errors'],passes_2e_8=entry['errors']['tensor']<=2e-8))
    max_ref=max(max(r['reference32_64'].values()) for r in rows)
    max_oct=max(max(r['octant_full_error'].values()) for r in rows if 'octant_full_error' in r)
    max_axial=max(raw['axial']['errors']['64'].values())
    bounds=[(r['ideal_node_truncation'],r['reference']['64']['F']) for r in rows]+[(raw['axial']['ideal_node_truncation'],raw['axial']['oracle']['F'])]
    max_bound=max(max(b['energy_absolute'],b['pressure_component_absolute']) for b,F in bounds)
    max_bound_norm=max(max(b['energy_absolute'],b['pressure_component_absolute'])/F for b,F in bounds)
    packet_fields=['tensor_error','rho_error','flux_error','pressure_error','pi_error','number_relative_error']
    max_packet=max(e['packet'][k] for r in rows for e in r['rules'].values() for k in packet_fields)
    max_cov=max(e['co_rotation_error'] for r in raw['rotation'] for e in r['rules'].values())
    max_ref_cov=max(r['reference_covariance_error'] for r in raw['rotation'])
    max_trace=max(abs(np.trace(e['moments']['P'])-e['moments']['F'])/e['moments']['F'] for r in rows for e in r['rules'].values())
    order_gates={}
    bands={'ANISO':{'energy':(1.8,2.2),'pressure':(.8,1.2)},'ISO':{'energy':(2.8,3.2),'pressure':(1.8,2.2)}}
    selected_triplets={}
    for label in ac.SOURCES:
        for field in ['energy','pressure']:
            candidates=[o for o in order_rows if o['source']==label and o['rule']=='Q14']
            triplet=next(([a,b] for a,b in zip(candidates[:-1],candidates[1:]) if a[field]['value'] is not None and b[field]['value'] is not None),None)
            key=label+'_'+field;lo,hi=bands[label][field]
            order_gates[key]=triplet is not None and all(lo<=o[field]['value']<=hi for o in triplet)
            selected_triplets[key]=triplet
    minq=min(r['minimum_birth_q'] for r in rows);minexp=min(r['minimum_directional_log_expansion'] for r in rows)
    gates=dict(scoped_tests=tests['status']=='PASS_SCOPED_TESTS',reference32_64=max_ref<=2e-12,
        octant_reference=max_oct<=2e-12,analytic_axial=max_axial<=2e-12,
        ideal_node_truncation=max_bound<=2e-12 and max_bound_norm<=2e-12,
        actual_packet_mapping=max_packet<=ac.ROUND,trace_identity=max_trace<=ac.ROUND,
        co_rotation=max_cov<=ac.ROUND,reference_rotation=max_ref_cov<=2e-12,
        leading_Q14_coefficients=all(max(r['energy_relative_difference'],r['pressure_relative_difference'])<=.05 for r in leading_checks),
        positive_birth_q=minq>0,redward_log_expansion=minexp>0,
        **{'order_'+k:v for k,v in order_gates.items()})
    summary=dict(workflow_version='1.0.0',admission='PENDING_INDEPENDENT_ASTRA_REVIEW',new_IVPs=0,
        old_campaign_replay=0,source_transactions=0,cohort_fixtures=len(rows),rotation_fixtures=len(raw['rotation']),
        gates=gates,all_frozen_gates_pass=all(gates.values()),orders=order_rows,finest_resolved_Q14_triplets=selected_triplets,
        leading_Q14_checks=leading_checks,angular_2e_8_benchmark=benchmark,
        maximum_reference32_64=max_ref,maximum_octant_full=max_oct,maximum_axial_oracle=max_axial,
        maximum_ideal_node_bound_absolute=max_bound,maximum_ideal_node_bound_normalized=max_bound_norm,
        maximum_actual_packet_error=max_packet,maximum_trace_error=max_trace,maximum_co_rotation_error=max_cov,
        minimum_birth_q=minq,minimum_directional_log_expansion=minexp,
        normalization=raw['normalization'],denominators='All angular errors use positive continuum F; packet errors use direct-rule F; number error uses n_b*D',
        q26_identity='Canonical positive degree-7 candidate; actual REC26 inventory NOT_USED',
        truncation_qualification='Ideal-node analytic truncation bound only; floating-node/summation error is not interval certified',
        physical_claim='Selected one-cohort angular domain only; no temporal or full REC closure claim',overall_BASS_physical_completion=None,
        unresolved=['native finite absorption','calibrated REC coupling','B4 restart','B5 general-domain validation'])
    (R/'SUMMARY.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    with (R/'angular_errors.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(benchmark[0]));w.writeheader();w.writerows(benchmark)
    with (R/'leading_ratios.csv').open('w',newline='') as f:
        fields=['source','eta','rule','energy_ratio','pressure_ratio','energy_status','pressure_status'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in rows:
            if r['eta']>0:
                for name,e in r['rules'].items():w.writerow(dict(source=r['source'],eta=r['eta'],rule=name,energy_ratio=e['leading_energy_ratio'],pressure_ratio=e['leading_pressure_ratio'],energy_status=e['leading_energy_status'],pressure_status=e['leading_pressure_status']))
    fig,axs=plt.subplots(2,2,figsize=(11,8),constrained_layout=True)
    colors={'ANISO':'#225ea8','ISO':'#d95f0e'};zero_masks=0
    for ax,field,title in [(axs[0,0],'energy','Energy angular error'),(axs[0,1],'pressure','Pressure angular error')]:
        for label in ac.SOURCES:
            rr=[r for r in rows if r['source']==label]
            for name,style in [('Q14','o-'),('Q26','s--')]:
                xx=np.array([r['eta'] for r in rr]);yy=np.array([r['rules'][name]['errors'][field] for r in rr]);mask=(xx>0)&(yy>0);zero_masks+=int(np.count_nonzero(~mask))
                ax.loglog(xx[mask],yy[mask],style,color=colors[label],label=label+' '+name,markersize=4)
        ax.axhline(2e-8,color='.4',ls=':',label='2e-8 comparison');ax.set(xlabel='Anisotropic redshift parameter eta',ylabel='Absolute error / continuum energy',title=title);ax.legend(fontsize=8)
    ax=axs[1,0]
    for label in ac.SOURCES:
        rr=[r for r in rows if r['source']==label and 0<r['eta']<=1/16]
        for field,style in [('energy','o-'),('pressure','s--')]:ax.semilogx([r['eta'] for r in rr],[r['rules']['Q14']['leading_'+field+'_ratio'] for r in rr],style,color=colors[label],label=label+' '+field,markersize=4)
    ax.axhline(1.,color='.4',ls=':');ax.set(xlabel='eta',ylabel='Saved signed error / exact leading term',title='Q14 exact leading-error ratios');ax.legend(fontsize=8)
    ax=axs[1,1];labels=[];aligned=[];rotated=[]
    for r in raw['rotation']:
        for name,e in r['rules'].items():labels.append(r['source']+'\n'+name);aligned.append(e['aligned_errors']['tensor']);rotated.append(e['fixed_grid_errors']['tensor'])
    xx=np.arange(len(labels));ax.bar(xx-.18,aligned,.36,label='Aligned physical pair');ax.bar(xx+.18,rotated,.36,label='Rotated pair, fixed rays');ax.set_yscale('log');ax.set_xticks(xx,labels);ax.set(ylabel='Tensor error / continuum energy',title='Fixed-grid orientation sensitivity at eta=1');ax.legend(fontsize=8)
    fig.suptitle('BASS B3d: one cohort, continuum angular reference and positive 14/26-ray rules',fontsize=12)
    fig.text(.5,.001,f'Log curves mask eta=0 or true zero entries ({zero_masks} curve entries); scientific JSON/CSV retain exact values. Q26 is a candidate, not actual REC26.',ha='center',fontsize=8)
    fig.savefig(R/'angular_cohort_errors.png',dpi=180,bbox_inches='tight');plt.close(fig)
    print(json.dumps(dict(gates=gates,all_frozen_gates_pass=all(gates.values()),leading_Q14_checks=leading_checks,new_IVPs=0)))

if __name__=='__main__':main()
