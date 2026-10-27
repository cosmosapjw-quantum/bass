"""Targeted new-unit controls; invoked once through metered.py."""
import copy
import json
import math
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from inverse import F,solve_ratio,reconstruct,load,ROOT,hx
import reference
from net import primitive,evaluate as net_evaluate
import mpmath as mp

def main():
    observed=[]
    def check(name,ok):
        observed.append(dict(name=name,pass_=bool(ok)))
        if not ok:raise AssertionError(name)
    for t in [.001,.1,1.,5.,30.]:
        got,br=solve_ratio(F(t));check('synthetic_monotone_inverse_'+str(t),abs(got-t)/t<2e-10 and br[0]<=got<=br[1])
    for r in [.5,1.,.4]:
        try:solve_ratio(r)
        except ValueError:check('invalid_ratio_refused_'+str(r),True)
        else:check('invalid_ratio_refused_'+str(r),False)
    tiny=1e-6;native=(.5-tiny/6)/(1-tiny/2)
    check('native_quadratic_formula_is_distinct_from_ideal',native!=F(tiny))
    p=load('NATIVE_VIRTUAL_TRIPLE_TRACE_5126_5127.json');ly=load('NATIVE_LYMAN_STORED_5126_5127.json')
    tr=next(t for t in p['traces'] if t['index']==5127 and t['bin']==273)
    q=copy.deepcopy(p);q.pop('validation_only_right_state');tr2=copy.deepcopy(tr);tr2.pop('right_snapshot_validation_only')
    a=reconstruct(q,ly,tr2);b=reference.reconstruct(q,ly,tr2)
    check('right_population_holdout_not_inverse_input',abs(a['x1s']/hx(p['validation_only_right_state']['x1s'])-1)<2e-10)
    check('independent_70digit_inverse',abs(a['tau']/float(b['tau'])-1)<2e-10)
    check('selected_nondiffusion_native_branch',not 100<=a['bin']<180 and a['tau']>1e-6)
    check('rounding_interval_labeled_assumption',a['rounding_model']['label']=='ASSUMED_32_BINARY64_ULPS_NOT_PHYSICAL_CERTIFICATE')
    vi=a['ys_virtual_assumed_interval'];prop=a['virtual_interval_propagation']
    check('trace_and_tau_interval_propagated_through_virtual_source',vi[0]<=a['ys_virtual']<=vi[1] and prop['feq'][0]<prop['feq'][1] and prop['D'][0]<prop['D'][1])
    expected_rel=max(abs(vi[0]-a['ys_virtual']),abs(vi[1]-a['ys_virtual']))/abs(a['ys_virtual'])
    check('virtual_qualification_uses_interval_width',a['virtual_rounding_model_relative_estimate']==expected_rel and a['virtual_well_conditioned_under_assumed_model']==(vi[0]>0 and expected_rel<=2e-10))
    with mp.workdps(70):
        ref=mp.quad(lambda u:mp.exp(4*u)*(2+3*u),[0,mp.mpf('.0000849')])
        val=primitive(0,.0000849,2,2+3*.0000849,4)
        check('stable_PL_exponential_primitive',abs(val/float(ref)-1)<2e-13)
    tube=load('FINITE_TUBE_INPUT_SLICE.json');old=load('PRIOR_INCOMING_TUBE_RESULT.json')
    net=net_evaluate(tube,ly,old)
    check('tensor_pressure_is_not_spatial_source_force',net['T_out0_J_m3'][1][1]>0 and net['common_volume_time_average_cQ_rad_J_m3_s'][1:]==[0.,0.,0.])
    check('retarded_internal_split_retained',len(net['segments'])==2 and 0<net['split_u'][1]<net['split_u'][-1])
    check('affine_clock_strict_past_margin',net['strict_past_margin']==old['native_clock']['lag_minus_native_cell_width'])
    bad=copy.deepcopy(tube);bad['selection']['cell_indices']=[5125,5127]
    try:net_evaluate(bad,ly,old)
    except ValueError:check('nonadjacent_native_interval_refused',True)
    else:check('nonadjacent_native_interval_refused',False)
    (ROOT/'results/CONTROLS.json').write_text(json.dumps(dict(status='PASS',controls=observed),indent=2))
    print(json.dumps(dict(status='PASS',count=len(observed))))
if __name__=='__main__':main()
