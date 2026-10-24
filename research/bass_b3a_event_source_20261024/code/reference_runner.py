"""Produce one current local reference and NEW A/B diagnostic; no history replay."""
import csv
from dataclasses import asdict
import json
from pathlib import Path
import numpy as np
from event_measure import ab_fixture,moments,exact_axis_pi_xx,Identity
from rec_adapter import native_scalar_state,event_bundle,owner,angular,OWNER

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT/'results'
RESULTS.mkdir(exist_ok=True)
identity = Identity(OWNER,'stored_scalar_epoch_z1099.9986525171403','rest','proper_time_dt_dV_invariant',
                    'STORED_NATIVE_SCALAR_EXTRACT + CONSTRUCTED_ROTATED_S_FIXTURE')
S = owner.shear_fixtures()['rotated']
state,restored = native_scalar_state(S)
bundle = event_bundle(state,identity)
net = bundle.net_moments()
direct = owner.exchange_source(state,n_mu=12,n_phi=20)
down,up = moments(bundle.down),moments(bundle.up)
gross_energy = down.cQ_J_m3_s[0]+up.cQ_J_m3_s[0]
reference = {
    'unit':'BASS_B3A_REC_EVENT_ADAPTER_20261024',
    'classification':'detached full-Planck/stimulated reference from native scalar inputs; constructed angular S; NOT native LINE02/history parity',
    'identity':asdict(identity),'native_reconstruction':restored,'S_fixture':S,
    'n_l_m3':state.n_l_m3,'n_u_m3':state.n_u_m3,'H_s_inv':state.H_s_inv,'f_plus':state.f_plus,
    'card':asdict(state.card),'quadrature':{'n_mu':12,'n_phi':20,'full_event_nodes':len(bundle.down.energy_J),'sign_count':8,'weights_renormalized':False},
    'native_reference':{
        'owner_api':'line_source.exchange_source(mode=quadrature via owner implementation)',
        'gross_down_m3_s':down.number_rate_m3_s,'gross_up_m3_s':up.number_rate_m3_s,
        'net_R_m3_s':net.number_rate_m3_s,'net_cQ_J_m3_s':net.cQ_J_m3_s,'K_J_m3_s':net.K_J_m3_s,
        'PiRate_J_m3_s':net.PiRate_J_m3_s,'owner_energy_J_m3_s':direct['du_radiation_J_m3_s'],
        'energy_discrepancy_over_gross':abs(net.cQ_J_m3_s[0]-direct['du_radiation_J_m3_s'])/gross_energy,
        'PiRate_discrepancy_over_gross':float(np.max(np.abs(net.PiRate_J_m3_s-direct['energy_PSTF_J_m3_s'])))/gross_energy,
        'thermal_source_J_m3_s':0.,'atomic_internal_energy_J_m3_s':-net.cQ_J_m3_s[0],
        'ionization_yield':0.,'free_electron_yield':0.,'new_native_solver_calls':0},
    'constructed_fixtures':[],'claim_limit':'same-grid donor parity is not angular continuum convergence; synthetic callback is not real photon stock certification',
}
for label in ['emission','absorption','LTE']:
    s = owner.state_at_depth('H_LYA_EFFECTIVE_2P',label,3.7,S)
    b = event_bundle(s,Identity(OWNER,'constructed_'+label,'rest',identity.clock,'CONSTRUCTED_'+label))
    d,u = moments(b.down),moments(b.up)
    ref = owner.exchange_source(s,n_mu=12,n_phi=20)
    m = b.net_moments()
    scale = d.cQ_J_m3_s[0]+u.cQ_J_m3_s[0]
    reference['constructed_fixtures'].append({'label':label,'gross_down_m3_s':d.number_rate_m3_s,'gross_up_m3_s':u.number_rate_m3_s,
         'net_energy_J_m3_s':m.cQ_J_m3_s[0],'owner_net_energy_J_m3_s':ref['du_radiation_J_m3_s'],
         'energy_discrepancy_over_gross':abs(m.cQ_J_m3_s[0]-ref['du_radiation_J_m3_s'])/scale,
         'net_over_gross':m.cQ_J_m3_s[0]/scale})
rows=[]
for beta in np.linspace(0,.95,96):
    row={'beta_axis':float(beta)}
    for name in 'AB':
        numeric = moments(ab_fixture(name).boosted([beta,0,0],frame='axis_curve')).PiRate_J_m3_s[0,0]
        exact = exact_axis_pi_xx(name,beta)
        row.update({name+'_exact':exact,name+'_numeric':float(numeric),name+'_residual':float(numeric-exact)})
    row['delta_exact']=row['A_exact']-row['B_exact']
    row['delta_numeric']=row['A_numeric']-row['B_numeric']
    rows.append(row)
oblique = [moments(ab_fixture(name).boosted([.2,.4,.4],frame='oblique')) for name in 'AB']
oblique_delta = float(oblique[0].PiRate_J_m3_s[0,0]-oblique[1].PiRate_J_m3_s[0,0])
reference['AB']={'axis_three_fifths':{name:{'cQ':moments(ab_fixture(name).boosted([.6,0,0],frame='axis')).cQ_J_m3_s,
      'PiRate':moments(ab_fixture(name).boosted([.6,0,0],frame='axis')).PiRate_J_m3_s} for name in 'AB'},
      'oblique_beta':[.2,.4,.4],'oblique_delta_xx':oblique_delta,'oblique_exact_delta_xx':-286408/10384605,
      'max_axis_absolute_residual':max(abs(r[n+'_residual']) for r in rows for n in 'AB')}
reference['owner_call_counters']={'line_source':dict(owner.COUNTERS),'escape_moments':dict(angular.COUNTERS)}
def encode(x):
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    raise TypeError(type(x).__name__)
(RESULTS/'CURRENT_REFERENCE.json').write_text(json.dumps(reference,indent=2,default=encode,allow_nan=False)+'\n')
with (RESULTS/'AB_EXACT_BOOST.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,axes = plt.subplots(2,1,figsize=(8.4,7.2),sharex=True,gridspec_kw={'height_ratios':[3,1]})
x=np.array([r['beta_axis'] for r in rows])
for name,color in [('A','#1764ab'),('B','#ca6332')]:
    axes[0].plot(x,[r[name+'_exact'] for r in rows],color=color,label=f'{name}: exact axis PiRate xx')
    axes[0].plot(x[::6],[r[name+'_numeric'] for r in rows[::6]],'.',color=color,markersize=4)
    axes[1].plot(x,[r[name+'_residual'] for r in rows],color=color,label=f'{name} numeric - exact')
axes[0].plot(x,[r['delta_exact'] for r in rows],color='#29915c',label='A - B exact, axis boost')
axes[0].scatter([.6],[oblique_delta],marker='D',s=48,color='#8c39a4',zorder=5,label='Oblique A - B: beta=(.2,.4,.4)')
axes[0].axhline(0,color='black',linewidth=.7)
axes[0].set_ylabel('PiRate xx / (unit energy x event rate)')
axes[0].set_title('NEW detached event-adapter diagnostic: exact finite A/B measures')
axes[0].legend(loc='upper left',fontsize=8)
axes[0].grid(alpha=.2)
axes[1].axhline(0,color='black',linewidth=.7)
axes[1].set_ylim(-2e-15,2e-15)
axes[1].set_ylabel('Residual (linear)')
axes[1].set_xlabel('Axis beta, or |beta| for the distinguished oblique point')
axes[1].grid(alpha=.2)
axes[1].ticklabel_format(axis='y',style='sci',scilimits=(0,0))
fig.text(.5,.012,'Axes/cube gross events have identical rest moments; boosted PiRate differs. Zero is displayed on a linear scale.',ha='center',fontsize=8)
fig.tight_layout(rect=(0,.04,1,1));fig.savefig(RESULTS/'AB_EXACT_BOOST.png',dpi=150);plt.close(fig)
print(json.dumps({'native_energy_discrepancy_over_gross':reference['native_reference']['energy_discrepancy_over_gross'],
                  'native_PiRate_discrepancy_over_gross':reference['native_reference']['PiRate_discrepancy_over_gross'],
                  'max_AB_absolute_residual':reference['AB']['max_axis_absolute_residual'],'oblique_delta_xx':oblique_delta,
                  'owner_calls':reference['owner_call_counters'],'outputs':['CURRENT_REFERENCE.json','AB_EXACT_BOOST.csv','AB_EXACT_BOOST.png']},indent=2))
