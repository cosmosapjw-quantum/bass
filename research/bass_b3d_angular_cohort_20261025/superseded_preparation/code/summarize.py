"""Mechanical frozen-gate report, CSVs and research figure from new raw runs."""
from pathlib import Path
import csv,json,math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import emission_split as es
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'results'
read=lambda name:json.loads((R/name).read_text())
runs=[read(f'coupled_{n}.json') for n in [16,32,64,128]]
tight=read('tight_128.json');controls=read('prescribed_controls.json')
diffs=[]
for a,b in zip(runs[:-1],runs[1:]):
    d=es.distance(a['final'],b['final']);d['maximum']=max(d.values())
    diffs.append(dict(coarse=a['steps'],fine=b['steps'],**d))
orders={key:es.order(diffs[-2][key],diffs[-1][key]) for key in ['geometry','x','photon_number','photon_tensor']}
tightdist=es.distance(runs[-1]['final'],tight['final']);tightdist['maximum']=max(tightdist.values())
allrows=[row for run in runs+[tight] for row in run['history']]
maxima={k:max(row[k] for row in allrows) for k in ['constraint','atom_count_error','excitation_photon_count_error','energy_work_error']}
minm=min(row['m_min'] for row in allrows)
minw=min(row['packet_weight_min'] for row in allrows if row['packet_weight_min'] is not None)
mindepth=min(tx['path_depth_ratio'] for run in runs+[tight] for tx in run['transactions'])
control_report={}
for scheme in ['lie','strang']:
    sr=[r for r in controls['runs'] if r['scheme']==scheme]
    control_report[scheme]=dict(errors=[dict(steps=r['steps'],**r['oracle_error']) for r in sr],
        orders={key:es.order(sr[-2]['oracle_error'][key],sr[-1]['oracle_error'][key]) for key in ['geometry','x','photon_number','photon_tensor']})
resolved=[orders[key]['value'] for key in ['x','photon_number','photon_tensor'] if orders[key]['value'] is not None]
# Every resolved source/radiation component must meet the frozen asymptotic band.
order_pass=bool(resolved) and all(1.8<=p<=2.2 for p in resolved)
gates=dict(final64_128=diffs[-1]['maximum']<=2e-8,constraint=maxima['constraint']<=2e-8,
    atom_count=maxima['atom_count_error']<=5e-12,
    excitation_photon_count=maxima['excitation_photon_count_error']<=5e-12,
    energy_work=maxima['energy_work_error']<=2e-10,tight_A=tightdist['maximum']<=2e-10,
    coupled_second_order=order_pass,strict_directional_support=minm>0,strict_packet_positivity=minw>0,whole_path_thick=mindepth>=es.fx.owner.THICK_THRESHOLD)
report=dict(workflow_version='1.0.0',admission='PENDING_INDEPENDENT_ASTRA_REVIEW',
    selfconsistent_trajectories=5,prescribed_trajectories=6,new_total_trajectories=11,
    refinement=diffs,orders=orders,tight_A_distance=tightdist,maxima=maxima,
    minimum_directional_expansion=minm,analytic_support_lower_bound=.6/(1.02**3),
    minimum_positive_packet_weight=minw,minimum_source_path_depth_ratio=mindepth,oracle=controls['oracle'],prescribed_controls=control_report,gates=gates,
    all_frozen_gates_pass=all(gates.values()),
    denominators=dict(geometry='initial h0=1',x='fine x',photon_number='fine n_gamma',photon_tensor='fine rho_gamma',
        constraint='unchanged core.relative_constraint',atom_count='N0',excitation_photon_count='N0*x0',energy_work='u0=initial excitation'),
    initial_constants=dict(N0=es.N0,x0=es.X0,H0_s_inv=es.H0,L_m=es.SCALE.length_m,alphaL=es.SCALE.density_factor,
        energy_J=es.CARD.energy_J,wavelength_m=es.CARD.wavelength_m,M0_kg=es.M0,u0=es.U0),
    unresolved_obligations=['finite absorption','full REC35x26 bootstrap','broad B3c domains','B4 restart','B5 domain validation'],overall_BASS_physical_completion=None)
(R/'SUMMARY.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
with (R/'refinement.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(diffs[0]));writer.writeheader();writer.writerows(diffs)
fields=['steps','tau','stage','h','alpha','x','N','n_gamma','rho_exc','rho_rest','rho_gamma','constraint','atom_count_error','excitation_photon_count_error','energy_work_error','W_over_u0','m_min','packet_energy_max','packet_weight_min','packets']
with (R/'trajectories.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
    for run in runs:
        for row in run['history']:writer.writerow({k:run['steps'] if k=='steps' else row[k] for k in fields})
with (R/'prescribed_errors.csv').open('w',newline='') as f:
    fields2=['scheme','steps','geometry','x','photon_number','photon_tensor'];w=csv.DictWriter(f,fieldnames=fields2);w.writeheader()
    for run in controls['runs']:w.writerow(dict(scheme=run['scheme'],steps=run['steps'],**run['oracle_error']))
fig,axs=plt.subplots(2,2,figsize=(10.5,7.5),constrained_layout=True)
ax=axs[0,0]
for key,label in [('x','excited fraction'),('photon_number','photon number'),('photon_tensor','photon tensor')]:ax.loglog([d['coarse'] for d in diffs],[d[key] for d in diffs],'o-',label=label)
ax.axhline(2e-8,color='0.5',ls='--',label='64/128 gate');ax.set(xlabel='Coarse outer steps',ylabel='Successive final difference',title='Self-consistent Strang refinement');ax.legend(fontsize=8)
ax=axs[0,1]
for scheme,marker in [('lie','o'),('strang','s')]:
    sr=control_report[scheme]['errors'];ax.loglog([v['steps'] for v in sr],[v['photon_tensor'] for v in sr],marker+'-',label=scheme.title())
ax.set(xlabel='Outer steps',ylabel='Tensor error / oracle photon energy',title='Independent prescribed-geometry oracle');ax.legend()
rows=runs[-1]['history'];t=np.array([r['tau'] for r in rows])
ax=axs[1,0]
for key,label in [('excitation_photon_count_error','excitation + photon count'),('energy_work_error','excitation + radiation work')]:
    vals=np.array([r[key] for r in rows]);ax.plot(t,vals,label=label)
ax.set(xlabel='Dimensionless proper time',ylabel='Normalized absolute residual',title='128-step ledgers (exact zeros retained)');ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0));ax.legend(fontsize=8)
ax=axs[1,1]
for i in range(3):ax.plot(t,[r['h']+r['sigma'][i] for r in rows],label=f'h + sigma_{i+1}')
ax.plot(t,.6/(1+t)**3,'k--',label='Analytic minimum bound')
ax.set(xlabel='Dimensionless proper time',ylabel='Directional expansion',title='Redward-support diagnostic');ax.legend(fontsize=8)
fig.suptitle('BASS B3c1: cold emission + diagonal Bianchi I, fixed 14-ray model',fontsize=13)
fig.savefig(R/'refinement_ledgers_support.png',dpi=180);plt.close(fig)
print(json.dumps({'gates':gates,'maxima':maxima,'orders':orders,'tight_A':tightdist,'all_frozen_gates_pass':all(gates.values())}))
