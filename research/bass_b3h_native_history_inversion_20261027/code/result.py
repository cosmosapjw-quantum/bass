"""One selected inverse/net result invocation; raw results saved before verdict."""
import json
import math
import sys
from inverse import ROOT,load,reconstruct,hx
import reference
import net

def rel(a,b):return abs(a-float(b))/abs(float(b))
def evaluate():
    p=load('NATIVE_VIRTUAL_TRIPLE_TRACE_5126_5127.json');ly=load('NATIVE_LYMAN_STORED_5126_5127.json')
    old=load('PRIOR_INCOMING_TUBE_RESULT.json');tube=load('FINITE_TUBE_INPUT_SLICE.json')
    rows=[];checks=[]
    for tr in p['traces']:
        row=reconstruct(p,ly,tr);ref=reference.reconstruct(p,ly,tr);row['reference70']=ref
        row['relative_primary_reference']={k:rel(row[k],ref[k]) for k in ['tau','x1s','Gamma','TR_eV','nH_cm3','H_s_inv','ys_beta','ys_gamma','ys_virtual','x2s','x2p']}
        checks.append(dict(name=f"inverse_reference_{tr['index']}_{tr['bin']}",value=row['relative_primary_reference']['tau'],limit=2e-10))
        if tr['index']==5127:
            known=p['validation_only_right_state'];val=tr['right_snapshot_validation_only']
            row['right_validation_residuals']={k:rel(row[k],hx(v)) for k,v in [('x1s',known['x1s']),('Gamma',val['Gamma']),('TR_eV',known['TR_eV_rescaled']),('nH_cm3',known['nH_cm3']),('H_s_inv',known['H_sInv'])]}
            for k,v in row['right_validation_residuals'].items():checks.append(dict(name=f'right_{k}_{tr["bin"]}',value=v,limit=2e-10 if k=='x1s' else 2e-13))
        row['ys_beta_gamma_relative']=rel(row['ys_beta'],row['ys_gamma'])
        row['ys_virtual_beta_relative']=rel(row['ys_virtual'],row['ys_beta'])
        checks.append(dict(name=f'ys_beta_gamma_{tr["index"]}_{tr["bin"]}',value=row['ys_beta_gamma_relative'],limit=2e-10))
        if row['virtual_well_conditioned_under_assumed_model']:checks.append(dict(name=f'ys_virtual_{tr["index"]}_{tr["bin"]}',value=row['ys_virtual_beta_relative'],limit=2e-10))
        if min(row['x1s'],row['x2s'],row['x2p'])<=0:raise ValueError('nonpositive reconstructed population')
        rows.append(row)
    primary=[next(r for r in rows if r['index']==k and r['bin']==273) for k in [5126,5127]]
    diagnostic=load('LYA_DIAGNOSTIC_NORMALIZATION.json')
    Aeff=(6.2649e8+2*6.2648e8)/3
    for r in primary:
        RLya=tube['native_cosmology']['LYA_FACT_cm3_inv']*r['H_s_inv']/r['nH_cm3']/r['x1s']
        r['Lyalpha_diagnostic']=dict(R_Lya_s_inv=RLya,A_effective_s_inv=Aeff,tau_Lya=Aeff/RLya,
          normalization=diagnostic,scope='preserved REC LINE01 diagnostic normalization; original Lyalpha still thick; not an inverse input or closure change')
    spread=[]
    for k,a in zip([5126,5127],primary):
        rr=[r for r in rows if r['index']==k]
        for r in rr:
            r['relative_x1s_vs_primary']=rel(r['x1s'],a['x1s'])
            checks.append(dict(name=f'crossbin_{k}_{r["bin"]}',value=r['relative_x1s_vs_primary'],limit=2e-10))
        spread.append(dict(index=k,x1s_min=min(r['x1s'] for r in rr),x1s_max=max(r['x1s'] for r in rr),max_relative_to_primary=max(r['relative_x1s_vs_primary'] for r in rr),averaged=False))
    finite=net.evaluate(tube,ly,old);refnet=reference.net(tube,ly,old);finite['reference70']=refnet
    finite['relative_primary_reference']={k:rel(finite[k],refnet[k]) for k in ['DeltaN0','DeltaU0']}
    for k,v in finite['relative_primary_reference'].items():checks.append(dict(name='net_'+k,value=v,limit=2e-11))
    for k in ['transport_residual_N','transport_residual_U']:checks.append(dict(name=k,value=abs(finite[k]),limit=2e-13))
    nref=old['nH_reference_m3'];EJ=old['representation']['E21_J']
    stocks=[dict(index=r['index'],N1s_per_V0_m3=nref*r['x1s'],N2s_per_V0_m3=nref*r['x2s'],N2p_per_V0_m3=nref*r['x2p'],
      U_excited_per_V0_J_m3=nref*EJ*(r['x2s']+r['x2p']),source_normalization_excess=r['source_normalization_excess']) for r in primary]
    ds=nref*(primary[1]['x2s']-primary[0]['x2s']);dp=nref*(primary[1]['x2p']-primary[0]['x2p']);D=finite['DeltaN0']
    storage=dict(nH_reference_m3=nref,endpoints=stocks,DeltaN2s_per_V0_m3=ds,DeltaN2p_per_V0_m3=dp,
      DeltaU_excited_per_V0_J_m3=EJ*(ds+dp),net_Lya_downward_events_per_V0_m3=D,
      required_finite_nonLya_complement_upper_per_V0_m3=dp+D,
      algebraic_QSS_channel_complement_upper_per_V0_m3=D,
      QSS_endpoint_storage_defect_upper_per_V0_m3=dp,
      algorithmic_parameter_refresh_upper_per_V0_m3=dp,
      direct_Lya_atomic_internal_energy_per_V0_J_m3=-EJ*D,
      required_nonLya_plus_refresh_internal_energy_per_V0_J_m3=EJ*(D+ds+dp),
      physical_nonLya_refill_energy_owner=None,
      QSS_complement_scope='Balance-inferred from native instantaneous algebraic row; individual nonLya operands not newly exported or integrated',
      refresh_scope='Endpoint algebraic refresh of effective-H inventories; not an observed physical refill',
      population_convention='native x1s=1-xHII; tiny excited fractions are not subtracted from ground fraction; xe=xHII holds only at the known selected snapshot',
      native_direct_pair_recoil_heat_ionization=[0.,0.,0.],B3i_RHS_invocations=0,physical_full_transaction_admitted=False)
    for c in checks:c['pass']=math.isfinite(c['value']) and c['value']<=c['limit']
    return dict(schema='BASS_NATIVE_HISTORY_INVERSION_NET_RESULT_V1',status='NUMERICAL_CHECKS_PASS' if all(c['pass'] for c in checks) else 'NUMERICAL_CHECK_FAILED_REQUIRES_ROOT',
      source=p['source_commit'],primary_bin=273,rows=rows,primary_endpoints=primary,crossbin_spread=spread,finite_photon=finite,
      QSS_storage=storage,acceptance_checks=checks,scientific_admission='PENDING_ROOT_INDEPENDENT_REVIEW',
      physical_radii={k:None for k in ['eS','en','eE','geometry','temporal','total']},
      original_central_DAG=dict(completed=27,total=88),requested_model='gpt-6.1-sol',observed_model=None,
      previous_512_maps_and_2_RHS_replayed=False,native_solver_invocations=0)

if __name__=='__main__':
    out=evaluate();(ROOT/'results/INVERSION_NET_RESULT.json').write_text(json.dumps(out,indent=2,allow_nan=False))
    print(json.dumps(dict(status=out['status'],checks=len(out['acceptance_checks']),failed=[x for x in out['acceptance_checks'] if not x['pass']],B3i_RHS_invocations=0)))
    sys.exit(0 if out['status']=='NUMERICAL_CHECKS_PASS' else 2)
