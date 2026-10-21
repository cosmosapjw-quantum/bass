#!/usr/bin/env python3
"""Independent standard-library observer of raw S9 native receipts.

Exact polynomial sums are recomputed with Fraction from the serialized binary64
nodes and weights. This observer never adjusts input, weights or tolerances.
"""
from __future__ import annotations
from fractions import Fraction
import cmath
import hashlib
import json
import math
import struct

MOMENT_GATE=Fraction(3,10**15)

def cohort_digest(cohort):
    h=hashlib.sha256()
    for number in [cohort['u'],cohort['b_birth'],cohort['energy_birth'],*cohort['mu'],*cohort['alpha']]:
        h.update(struct.pack('<d',number))
    h.update(cohort['role'].encode())
    return h.hexdigest()

def exact(cohort):
    norm=m2=m4=Fraction(0)
    for mu,alpha in zip(cohort['mu'],cohort['alpha']):
        m=Fraction.from_float(mu); a=Fraction.from_float(alpha); z=m*m
        norm+=a; m2+=a*(3*z-1)/2; m4+=a*(35*z*z-30*z+3)/8
    return norm,m2,m4

def complex_energy_identity(receipt):
    """Independent complex-step total energy vs native real E and Pi."""
    error=0.0; eps=1e-25
    for row in receipt['observations']:
        x=row['x']; h,b,y=row['state']; bp=y/h
        xc=x+1j*eps; bc=b+1j*eps*bp
        terms=[]
        for cohort in receipt['final_cohorts']:
            if cohort['u']>x: continue
            d=bc-cohort['b_birth']
            radial=sum(w*cmath.sqrt(cmath.exp(2*d)*(1-m*m)+cmath.exp(-4*d)*m*m)
                       for m,w in zip(cohort['mu'],cohort['alpha']))
            terms.append(cohort['energy_birth']*cmath.exp(-4*(xc-cohort['u']))*radial)
        derivative=sum(terms).imag/eps
        scale=row['e_radiation']
        if scale>0:
            error=max(error,abs(derivative+4*scale+2*bp*row['pi'])/scale)
    return error

def assess(receipt,reference,prereg,case):
    result={'case':case['name'],'status':receipt.get('status','unparseable'),
            'failure':receipt.get('failure'),'completed':receipt.get('status')=='completed'}
    observations=receipt.get('observations',[])
    if not result['completed']:
        result.update({'admitted_births':len(receipt.get('events',[])),
                       'completed_segments':len(receipt.get('segments',[])),
                       'remaining_obligations':['complete requested history after a separately frozen repair or support decision'],
                       'quality_gates':None})
        return result
    input=receipt['input']; config=input['config']; gates=prereg['gates']
    if case['model']=='S8_closed_donor':
        expected={row['x']:[row['h'],row['b'],row['y']] for row in reference['rows']}
    else:
        expected={x:[math.sqrt(config['donor0']*math.exp(-3*x)+config['old_isotropic']*math.exp(-4*x)+config['cosmological_constant']),config['b0'],0.0]
                  for x in input['output_times']}
    observed={row['x']:row for row in observations}
    output_exact=list(observed)==input['output_times'] and len(observations)==len(input['output_times'])
    common=sorted(set(expected)&set(observed))
    errors=[max((abs(observed[x]['state'][i]-expected[x][i]) for x in common),default=math.inf) for i in range(3)]
    hamiltonian=max((r['c_relative'] for r in observations),default=math.inf)
    clock=max((abs(r['clock_error']) for r in observations),default=math.inf)
    energy_identity=complex_energy_identity(receipt)
    all_stock=receipt['final_cohorts']
    positive=all(c['energy_birth']>0 and all(w>0 and math.isfinite(w) for w in c['alpha']) for c in all_stock)
    reflection=all(c['mu']==[-v for v in c['mu'][::-1]] and c['alpha']==c['alpha'][::-1] for c in all_stock)
    norm=True; moment=True; exact_agreement=True; certificates=[]
    birth_cohorts=[c for c in all_stock if c['role']=='new_isotropic_P24']
    event_map={row['u']:row for row in receipt['events']}
    for c in all_stock:
        n,m2,m4=exact(c); norm &= abs(n-1)<=MOMENT_GATE
        if c['role']!='new_isotropic_P24': continue
        passed=max(abs(m2),abs(m4))<=MOMENT_GATE; moment &= passed
        native=event_map[c['u']]['exact_moment_certificate']
        agree=(Fraction(native['sum_alpha_exact'])==n and Fraction(native['m2_exact'])==m2 and Fraction(native['m4_exact'])==m4)
        exact_agreement &= agree
        certificates.append({'u':c['u'],'pass':passed,'native_exact_agreement':agree,
            'm2':float(m2),'m4':float(m4),'m2_exact':str(m2),'m4_exact':str(m4)})
    old=[c for c in all_stock if c['role'].startswith('old_')]
    old_ok=[cohort_digest(c) for c in old]==input['expected_old_digests']
    born_ok=all(cohort_digest(c)==event_map[c['u']]['birth_rule_sha256'] for c in birth_cohorts)
    old_bits=(old==input['initial_cohorts'])
    event=max((e['energy_jump_relative'] for e in receipt['events']),default=0.0)
    positive_h=all(r['state'][0]>0 and all(math.isfinite(v) for v in r['state']) for r in observations)
    donor_expected=config['donor0']*math.exp(-3*config['x_end']-config['decay_lambda']*config['birth_end'])
    if not receipt['events']: donor_expected=config['donor0']*math.exp(-3*config['x_end'])
    donor_error=abs(observations[-1]['e_donor']-donor_expected)/(donor_expected or 1.0)
    rhs_jumps=[abs(e['rhs_after'][0]-e['rhs_before'][0]) for e in receipt['events']]
    solver_counters={}
    for segment in receipt['segments']:
        for key,value in segment['counters'].items():
            if isinstance(value,(int,float)): solver_counters[key]=solver_counters.get(key,0)+value
    q={'output_exact':output_exact,'finite_positive_background':positive_h,
       'hamiltonian':hamiltonian<=gates['hamiltonian_relative'],
       'cohort_energy_identity':energy_identity<=gates['cohort_energy_relative'],
       'event_energy':event<=gates['event_energy_relative'],
       'donor_endpoint':donor_error<=gates['donor_endpoint_relative'],
       'positive_stock':positive,'reflection_exact':reflection,'normalization_exact':norm,
       'new_birth_moments_exact':moment,'independent_exact_observer_agreement':exact_agreement,
       'old_stock_hash_and_raw_bits':old_ok and old_bits,'previous_birth_hashes':born_ok,
       'clock_augmentation':clock<=gates['clock_abs'],
       'fine_reference_abs':max(errors)<=gates['fine_reference_abs']}
    if case['model']=='S8_closed_donor':
        q['fresh_event_workspaces']=len(receipt['segments'])==config['k']+1 and all(s['fresh_driver'] and s['fresh_immutable_bank'] for s in receipt['segments'])
        q['nonzero_event_rhs_jump']=len(rhs_jumps)==config['k'] and min(rhs_jumps)>0.0
    if case['solver']['arm']=='mf_into_ls':
        q['actual_analytic_jvp_and_ft_work']=solver_counters.get('jvp_calls',0)>0 and solver_counters.get('ft_calls',0)>0
    else:
        q['actual_small_direct_work']=solver_counters.get('direct_factorizations',0)>0 and solver_counters.get('jacobian_builds',0)>0
    result.update({'quality_gates':q,'all_quality_gates':all(q.values()),
        'max_abs_h_b_y_reference':errors,'max_hamiltonian_relative':hamiltonian,
        'max_native_cohort_energy_identity_relative':energy_identity,
        'max_event_energy_relative':event,'donor_endpoint_relative':donor_error,
        'max_clock_abs':clock,'birth_certificates':certificates,'old_stock_digests':[cohort_digest(c) for c in old],
        'admitted_births':len(birth_cohorts),'segments':len(receipt['segments']),
        'solver_counters':solver_counters,'elapsed_seconds_diagnostic_only':receipt['elapsed_seconds'],
        'reference_scope':'Stored S8 numerical primal or analytic FLRW formula; no continuum-angular or finite-bin certificate'})
    return result
