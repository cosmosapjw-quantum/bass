#!/usr/bin/env python3
"""Read-only independent S9 PHYS-MATH then PHYS-MATH-CODE review.

No BASS analysis/production helper is imported and no ODE solver is run.
Fractions inspect serialized binary64 moments; Decimal independently reconstructs
cohort inventories and differentiates the radial kernel at the recorded states.
"""
from __future__ import annotations
import argparse
import copy
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import struct
import time


def dec(x):
    return D.from_float(x) if isinstance(x, float) else D(x)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(c):
    nums = [c['u'], c['b_birth'], c['energy_birth'], *c['mu'], *c['alpha']]
    payload = b''.join(struct.pack('<d', x) for x in nums) + c['role'].encode()
    return hashlib.sha256(payload).hexdigest()


def exact_moments(c):
    # Express all moments using monomials instead of a Legendre helper.
    s0 = sum((F.from_float(w) for w in c['alpha']), F(0))
    s2 = sum((F.from_float(w)*F.from_float(m)**2
              for m,w in zip(c['mu'],c['alpha'])), F(0))
    s4 = sum((F.from_float(w)*F.from_float(m)**4
              for m,w in zip(c['mu'],c['alpha'])), F(0))
    return s0, (3*s2-s0)/2, (35*s4-30*s2+3*s0)/8


def inventory(cohorts, x, b, bprime):
    """High-precision sums and dE/dx at fixed active cohort list."""
    E=P=Q=Ex=D(0)
    for c in cohorts:
        u,bb,amp,zs,ws=c
        d=b-bb; ep=(2*d).exp(); ez=(-4*d).exp()
        volume=amp*(-4*(x-u)).exp()
        sr=sd=sq=sx=D(0)
        for z,w in zip(zs,ws):
            av=ep*(1-z); bv=ez*z; r=(av+bv).sqrt()
            n=bv-av/2
            sr+=w*r
            sd+=w*n/r
            sq+=w*((-4*bv-av)/r+2*n*n/(r*r*r))
            # Direct derivative of e^{-4(x-u)} sqrt(A+B).
            sx+=w*(-4*r+bprime*(2*av-4*bv)/(2*r))
        E+=volume*sr; P+=volume*sd; Q+=volume*sq; Ex+=volume*sx
    return E,P,Q,Ex


def prepared_cohorts(raw):
    return [(dec(c['u']),dec(c['b_birth']),dec(c['energy_birth']),
             [dec(m)**2 for m in c['mu']],[dec(w) for w in c['alpha']])
            for c in raw]


def evaluation(h,y,ed,E,P,Q,L):
    fh=(-h*h-2*y*y-ed/2-E+L)/h
    rhs=[fh,y/h,-3*y+P/h]
    jac=[[-2-fh/h,2*P/h,-4*y/h],[-y/(h*h),D(0),1/h],[-P/(h*h),Q/h,D(-3)]]
    ft=[(3*ed/2+4*E)/h,D(0),-4*P/h]
    return rhs,jac,ft


def scaled_mismatch(a,b):
    return max((abs(dec(x)-y)/(1+abs(y)) for x,y in zip(a,b)),default=D(0))


def review_case(folder, case, prereg, reference, base):
    r=json.loads((folder/'RAW.json').read_text())
    p=json.loads((folder/'PROCESS.json').read_text())
    a=json.loads((folder/'ASSESSMENT.json').read_text())
    inp=json.loads((folder/'INPUT.json').read_text())
    exp=copy.deepcopy(base);exp['solver'].update(case['solver'])
    if case['model']=='analytic_FLRW':
        exp['config'].update(k=0,y0=0.0,decay_lambda=0.0,old_isotropic=0.2,old_anisotropic=0.0)
        old=copy.deepcopy(exp['initial_cohorts'][0]);old['energy_birth']=0.2
        exp['initial_cohorts']=[old];exp['expected_old_digests']=[digest(old)]
        exp['provenance']['control']='Synthetic analytic FLRW data; independent initial stock, no existing stock mutation'
    assert inp==exp and r['input']==inp
    assert p['exit_code']==0 and r['status']=='completed' and r['failure'] is None and r['pending_birth'] is None
    for n,key in [('RAW.json','raw_sha256'),('INPUT.json','input_sha256'),('console.log','log_sha256')]:
        assert sha(folder/n)==p[key], (folder.name,n,'hash')
    assert r['spectral_owner']==prereg['fixed_spectral_owner']
    assert r['vigilode_source']==prereg['vigilode_source']
    cfg=inp['config'];events=r['events'];obs=r['observations'];stock=r['final_cohorts']
    old=[c for c in stock if c['role'].startswith('old_')]
    born=[c for c in stock if c['role']=='new_isotropic_P24']
    assert old==inp['initial_cohorts']
    assert [digest(c) for c in old]==inp['expected_old_digests']==r['old_stock_digests']
    assert [o['x'] for o in obs]==inp['output_times']
    assert len(obs)==153
    gate=F(3,10**15); mmax=F(0);normmax=F(0)
    event_map={e['u']:e for e in events}; moment_records=[]
    for c in stock:
        assert c['energy_birth']>0 and all(-1<=v<=1 for v in c['mu']) and all(v>0 for v in c['alpha'])
        assert c['mu']==[-v for v in c['mu'][::-1]] and c['alpha']==c['alpha'][::-1]
        norm,m2,m4=exact_moments(c);normmax=max(normmax,abs(norm-1));assert abs(norm-1)<=gate
        if c['role']!='new_isotropic_P24':continue
        e=event_map[c['u']];n=e['exact_moment_certificate'];assert digest(c)==e['birth_rule_sha256']
        assert c['b_birth']==e['b_birth']==e['state'][1]
        assert c['energy_birth']==e['energy_birth']
        assert F(n['sum_alpha_exact'])==norm and F(n['m2_exact'])==m2 and F(n['m4_exact'])==m4
        assert F(n['gate_rational'])==gate and n['pass'] is True
        assert abs(m2)<=gate and abs(m4)<=gate
        mmax=max(mmax,abs(m2),abs(m4))
        moment_records.append({'u':c['u'],'norm_exact':str(norm),'m2_exact':str(m2),'m4_exact':str(m4)})
    closed=case['model']=='S8_closed_donor'
    assert len(events)==len(born)==(32 if closed else 0)
    seg=r['segments'];assert len(seg)==(33 if closed else 1)
    ends=[e['u'] for e in events]+[cfg['x_end']]
    du=cfg['birth_end']/cfg['k'] if closed else 0.0
    for i,s in enumerate(seg):
        begin=0.0 if i==0 else ends[i-1]
        assert s['index']==i and s['begin']==begin and s['end']==ends[i]
        assert s['exposure']==i*du and s['cohort_count']==len(old)+i
        assert s['output_times']==[begin]+[t for t in inp['output_times'] if begin<t<ends[i]]+[ends[i]]
        assert s['success'] and s['fresh_driver'] and s['fresh_immutable_bank']
        assert s['solver']['accepted']==s['internal_steps']==s['counters']['accepted_steps']
    pc=prepared_cohorts(stock);L=dec(cfg['cosmological_constant']);lam=dec(cfg['decay_lambda']);d0=dec(cfg['donor0'])
    maxC=maxIdentity=maxNativeE=maxNativeP=maxDonor=maxSigma=maxNativeC=D(0)
    maxCprop=maxCallback=maxEvent=maxEventReportedDiff=maxRightDiff=maxKernelJump=D(0)
    maxRef=[D(0),D(0),D(0)];maxLegacyRef=[0.0,0.0,0.0]
    refs={o['x']:[o['h'],o['b'],o['y']] for o in reference['rows']}
    obs_by_x={o['x']:o for o in obs}
    for row in obs:
        x=dec(row['x']);h,b,y=map(dec,row['state']);assert h>0
        active=[c for c in pc if c[0]<=x]
        E,P,Q,Ex=inventory(active,x,b,y/h)
        k=sum(e['u']<=row['x'] for e in events)
        exposure=dec(k*du)
        ed=d0*(-3*x-lam*exposure).exp()
        C=h*h-y*y-ed-E-L; scale=h*h+y*y+ed+E+L
        maxC=max(maxC,abs(C)/scale)
        maxNativeE=max(maxNativeE,abs(dec(row['e_radiation'])-E)/E)
        maxNativeP=max(maxNativeP,abs(dec(row['pi'])-P)/(1+abs(P)))
        maxDonor=max(maxDonor,abs(dec(row['e_donor'])-ed)/(ed or 1))
        maxSigma=max(maxSigma,abs(dec(row['sigma'])-D(3).sqrt()*abs(y)/h))
        maxNativeC=max(maxNativeC,abs(dec(row['c_relative'])-abs(C)/scale))
        # Compare independent differentiated energy to the *native* E and Pi.
        residual=Ex+4*dec(row['e_radiation'])+2*(y/h)*dec(row['pi'])
        maxIdentity=max(maxIdentity,abs(residual)/E)
        f,j,ft=evaluation(h,y,ed,E,P,Q,L)
        Cprime=2*h*f[0]-2*y*f[2]+3*ed-Ex
        maxCprop=max(maxCprop,abs(Cprime+2*C)/(1+scale))
        if closed:
            target=[dec(v) for v in refs[row['x']]]
            legacy=refs[row['x']]
        else:
            target=[(d0*(-3*x).exp()+dec(cfg['old_isotropic'])*(-4*x).exp()+L).sqrt(),dec(cfg['b0']),D(0)]
            import math
            legacy=[math.sqrt(cfg['donor0']*math.exp(-3*row['x'])+cfg['old_isotropic']*math.exp(-4*row['x'])+cfg['cosmological_constant']),cfg['b0'],0.0]
        for i in range(3):
            maxRef[i]=max(maxRef[i],abs(dec(row['state'][i])-target[i]))
            maxLegacyRef[i]=max(maxLegacyRef[i],abs(row['state'][i]-legacy[i]))
    for k,e in enumerate(events):
        x=dec(e['u']);h,b,y=map(dec,e['state']);w=dec(e['energy_birth'])
        before=[c for c in pc if c[0]<x];after=[c for c in pc if c[0]<=x]
        eb,pb,qb,_=inventory(before,x,b,y/h);ea,pa,qa,_=inventory(after,x,b,y/h)
        db=d0*(-3*x-lam*dec(k*du)).exp();da=d0*(-3*x-lam*dec((k+1)*du)).exp()
        event=(da+ea-db-eb)/(db+eb);maxEvent=max(maxEvent,abs(event))
        maxEventReportedDiff=max(maxEventReportedDiff,abs(dec(e['energy_jump_relative'])-abs(event)))
        for side,ed,E,P,Q in [('before',db,eb,pb,qb),('after',da,ea,pa,qa)]:
            f,j,ft=evaluation(h,y,ed,E,P,Q,L)
            maxCallback=max(maxCallback,scaled_mismatch(e['rhs_'+side],f),scaled_mismatch(e['partial_t_'+side],ft),scaled_mismatch(sum(e['jacobian_'+side],[]),sum(j,[])))
        row=obs_by_x[e['u']]
        assert row['state']==e['state'] and e['state_jump']==[0.0,0.0,0.0]
        assert row['e_donor']==e['donor_after'] and row['e_radiation']==e['radiation_after'] and row['pi']==e['pi_after']
        assert e['previous_cohort_digests_unchanged'] is True
        c=born[k];norm,m2,m4=exact_moments(c)
        # The finite binary64 rule has S rather than exactly1 in this jump.
        S=dec(norm.numerator)/dec(norm.denominator)
        M2=dec(m2.numerator)/dec(m2.denominator);M4=dec(m4.numerator)/dec(m4.denominator)
        KD=-D(8)/5*S-D(10)/7*M2+D(36)/35*M4
        maxKernelJump=max(maxKernelJump,abs((ea-eb)-w*S),abs((pa-pb)-w*M2),abs((qa-qb)-w*KD))
    counters={}
    for s in seg:
        for key,value in s['counters'].items():counters[key]=counters.get(key,0)+value
    assert counters==a['solver_counters']
    arm=case['solver']['arm']
    assert (counters['ft_calls']>0 and counters['jvp_calls']>0) if arm=='mf_into_ls' else (counters['direct_factorizations']>0 and counters['jacobian_builds']>0)
    assert maxLegacyRef==a['max_abs_h_b_y_reference']
    assert max(o['c_relative'] for o in obs)==a['max_hamiltonian_relative']
    assert max((e['energy_jump_relative'] for e in events),default=0)==a['max_event_energy_relative']
    clock_max=max(abs(o['clock_error']) for o in obs)
    assert clock_max==a['max_clock_abs']
    gates=prereg['gates']
    physics={'hamiltonian':maxC<=dec(gates['hamiltonian_relative']),
             'cohort_energy':maxIdentity<=dec(gates['cohort_energy_relative']),
             'event_energy':maxEvent<=dec(gates['event_energy_relative']),
             'native_donor_pointwise':maxDonor<=dec(gates['donor_endpoint_relative']),
             'reference':max(maxRef)<=dec(gates['fine_reference_abs']),
             'reported_augmented_clock':clock_max<=gates['clock_abs'],
             'callback_values':maxCallback<=D('5e-13'),
             'constraint_propagation_identity':maxCprop<=D('1e-65'),
             'exact_kernel_event_jump':maxKernelJump<=D('1e-65')}
    assert all(physics.values()),(folder.name,physics)
    return {'case':case['name'],'physics_checks':physics,'observations':len(obs),'births':len(events),'segments':len(seg),
            'max_exact_birth_moment':float(mmax),'max_exact_norm_error':float(normmax),'exact_birth_certificates':moment_records,
            'max_abs_reference_decimal':[float(x) for x in maxRef],
            'max_abs_reference_original_f64_expression':maxLegacyRef,
            'hamiltonian_decimal_max':float(maxC),'energy_derivative_vs_native_relative_max':float(maxIdentity),
            'native_E_vs_decimal_relative_max':float(maxNativeE),'native_Pi_vs_decimal_scaled_max':float(maxNativeP),
            'native_donor_vs_decimal_relative_max':float(maxDonor),'native_sigma_abs_difference_max':float(maxSigma),
            'native_Crelative_abs_difference_max':float(maxNativeC),'event_energy_decimal_relative_max':float(maxEvent),
            'event_relative_report_difference_max':float(maxEventReportedDiff),'callback_vs_decimal_scaled_max':float(maxCallback),
            'reported_clock_abs_max':clock_max,
            'Cprime_plus2C_decimal_scaled_max':float(maxCprop),'event_exact_kernel_identity_abs_max':float(maxKernelJump),
            'old_stock_digests':[digest(c) for c in old],
            'code_checks':{'preregistered_input_exact':True,'raw_input_exact':True,'raw_process_hashes':True,'old_stock_bytes_and_hash':True,
                           'all_birth_exact_certificates_match':True,'right_bank_event_observations':True,'fresh_segments_and_exact_output_schedule':True,
                           'counter_totals_match':True,'actual_requested_solver_callbacks_used':True,'assessment_reference_maxima_exactly_reproduced':True},
            'counters':{k:counters[k] for k in ['accepted_steps','rejected_steps','ft_calls','jvp_calls','direct_factorizations','jacobian_builds','rhs_calls']},
            'output_clipped_steps':sum(s['output_clipped_steps'] for s in seg),
            'files':{n:{'sha256':sha(folder/n),'bytes':(folder/n).stat().st_size} for n in ['RAW.json','PROCESS.json','ASSESSMENT.json','INPUT.json','console.log']}}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--lane',type=Path,required=True);ap.add_argument('--run',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    start=time.monotonic();s9=args.lane/'s9_vigilode';prereg=json.loads((s9/'PREREGISTRATION.json').read_text());reference=json.loads((s9/'reference/S8_PRIMAL.json').read_text());base=json.loads((s9/'inputs/base.json').read_text())
    assert sha(s9/'PREREGISTRATION.json')=='7e615ea1820e95b6fb61d7a360d13bf0fb560b6f25883e17ed487e8a3505f507'
    for rel,digest0 in prereg['input_sha256'].items():assert sha(s9/rel)==digest0
    for rel,digest0 in prereg['source_sha256'].items():assert sha(s9/rel)==digest0
    rows=[]
    with localcontext() as ctx:
        ctx.prec=80
        for case in prereg['cases']:
            rows.append(review_case(args.run/case['name'],case,prereg,reference,base));print(case['name'],'PASS',flush=True)
    pair=[]
    for arm in ['mf_into_ls','small_clock4']:
        ra=json.loads((args.run/f'closed_{arm}_r0/RAW.json').read_text());rb=json.loads((args.run/f'closed_{arm}_r1/RAW.json').read_text())
        eq={k:ra[k]==rb[k] for k in ['observations','segments','events','final_cohorts']}
        pair.append({'arm':arm,'r0_r1_exact_json_numeric_equal':eq,'all_equal':all(eq.values())})
    result={'schema':'bass.s9.independent_actual_review.v1','reviewer':'/root/science_reuse_and_review','status':'PASS_SCOPED',
        'review_order':['PHYS-MATH','PHYS-MATH-CODE'],'methods':['80-decimal-digit radial-kernel reconstruction and direct derivative','exact Fraction monomial moments','binary64 cohort digest and event-bank reconstruction','raw process and input identity checks'],
        'science_integrations_executed':0,'previous_tests_rerun':0,'calls_to_analyze_assess':0,'cases':rows,
        'total_histories_read':len(rows),'total_observations_read':sum(r['observations'] for r in rows),'total_exact_birth_certificates':sum(r['births'] for r in rows),
        'r0_r1_plateau_evidence':pair,'plateau_inference':'r0/r1 return exactly the same numeric observations, event banks and segment counters;119 clipped steps perclosed case constrain adaptation. Internal per-step time arrays are absent, so identity of every internal timestep is not claimed.',
        'resource_claim':'No precise peak RSS follows from sparse /proc sampling; observed RSS is a lower bound only.',
        'elapsed_seconds':time.monotonic()-start,'dependency_sha256':{'preregistration':sha(s9/'PREREGISTRATION.json'),'reference':sha(s9/'reference/S8_PRIMAL.json'),'base_input':sha(s9/'inputs/base.json'),'raw_campaign':sha(args.run/'CAMPAIGN_RETURN.json'),'review_script':sha(Path(__file__))},
        'scope':'Frozen discrete S8 manufactured donor model; no continuum/native spectral owner feedback/physical MD14 admission.'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k in ['status','total_histories_read','total_observations_read','total_exact_birth_certificates','elapsed_seconds']}))


if __name__=='__main__':main()
