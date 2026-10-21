#!/usr/bin/env python3
"""C9: inspect saved evidence only. No subprocess, network, solver or benchmark.

Uses no S9/S10 analyzer import. Scientific receipt hashes are reconstructed by
retaining the original Rust JSON number lexemes, avoiding Python/Ryu formatting
differences. Physics is checked algebraically on saved observations/cohorts.
"""
from pathlib import Path
from collections import defaultdict
from fractions import Fraction
import cmath
import datetime
import hashlib
import json
import math
import re
import struct
import tomllib

ROOT = Path('/workspace/scratch/a1783628e7a7')
LANE = ROOT/'bass/research/bass_isotropy_response_20261018'
EX = ROOT/'intake/optimization/execution_r1'
MEAS = EX/'measurements'
OUT = ROOT/'intake/optimization/c9_review_r1'
MODES = ['baseline','stream','prepared','cache','simd','simd_cache']
CASES = ['closed_mf_into_ls_r2','closed_small_clock4_r2',
         'flrw_mf_into_ls_fine','flrw_small_clock4_fine']
SOURCE = 'd5a173644f5c7c0dbe9eb8757dfc4ccad6c4f4c8'
TREE = '95785be65c196c68d61b79dafb32f4cedfd7702d'
OWNER = '0e25846433170d0f420c4cda44a0bedbf02cd177'
VIGILODE = 'a21d573980f66fe02891bd216153443b5352f921'
INPUTS_READ = {}
CHECKS = []

def data(path):
    path = Path(path)
    b = path.read_bytes()
    INPUTS_READ[str(path.relative_to(ROOT))] = {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
    return b

def load(path):
    return json.loads(data(path))

def rows(path):
    return [json.loads(line) for line in data(path).splitlines() if line.strip()]

def check(name, ok, details=None):
    CHECKS.append({'check':name,'pass':bool(ok),'details':details})

def bits(v):
    if isinstance(v,float):
        return ('f64',struct.pack('<d',v).hex())
    if isinstance(v,dict):
        return tuple((k,bits(v[k])) for k in sorted(v))
    if isinstance(v,list):
        return tuple(bits(x) for x in v)
    return (type(v).__name__,v)

def science_object(r):
    return {k:v for k,v in r.items() if k!='elapsed_seconds'}

class NumericLexeme:
    def __init__(self,s): self.s=s

def canonical_lexemes(v):
    if isinstance(v,NumericLexeme): return v.s
    if isinstance(v,dict):
        return '{'+','.join(json.dumps(k,ensure_ascii=False)+':'+canonical_lexemes(v[k]) for k in sorted(v))+'}'
    if isinstance(v,list): return '['+','.join(canonical_lexemes(x) for x in v)+']'
    return json.dumps(v,ensure_ascii=False,separators=(',',':'))

def scientific_digest(path):
    v=json.loads(data(path),parse_int=NumericLexeme,parse_float=NumericLexeme)
    del v['elapsed_seconds']
    return hashlib.sha256(canonical_lexemes(v).encode()).hexdigest()

def quantile(values,p):
    a=sorted(values); h=(len(a)-1)*p; lo=math.floor(h); hi=math.ceil(h)
    if lo==hi: return a[lo]
    return a[lo]*(hi-h)+a[hi]*(h-lo)

def summary(values):
    return {'n':len(values),'median':quantile(values,.5),'q1':quantile(values,.25),
            'q3':quantile(values,.75),'iqr':quantile(values,.75)-quantile(values,.25),
            'min':min(values),'max':max(values),'values':values}

def stat_equal(a,b):
    # This is a comparison of independently rounded summary arithmetic only,
    # never a relaxation of the strict scientific-output/experiment gates.
    if isinstance(a,float) and isinstance(b,(int,float)):
        return abs(a-b)<=4*max(math.ulp(a),math.ulp(float(b)))
    if isinstance(a,list): return len(a)==len(b) and all(stat_equal(x,y) for x,y in zip(a,b))
    if isinstance(a,dict): return all(k in b and stat_equal(v,b[k]) for k,v in a.items())
    return a==b

def pairs(records,keynames):
    grouped=defaultdict(lambda:defaultdict(list))
    for r in records:
        grouped[tuple(r[k] for k in keynames)][r['round']].append(r)
    output=[]
    for key,rounds in sorted(grouped.items()):
        good=set(rounds)==set(range(7))
        base=[]; cand=[]
        for round in range(7):
            rr=rounds[round]; candidate=key[-1]
            ci=(MODES.index(candidate)-1-round)%5
            order=['baseline',candidate] if (ci+round)%2==0 else [candidate,'baseline']
            good &= len(rr)==2 and [r['mode'] for r in rr]==order
            good &= all(r['order']==order and math.isfinite(r['seconds']) and r['seconds']>0 for r in rr)
            bymode={r['mode']:r for r in rr}
            base.append(bymode['baseline']['seconds']); cand.append(bymode[candidate]['seconds'])
        check('seven_adjacent_pairs:'+repr(key),good)
        row=dict(zip(keynames,key))
        row.update(baseline_seconds=summary(base),candidate_seconds=summary(cand),
                   paired_speedup=summary([a/b for a,b in zip(base,cand)]))
        output.append(row)
    return output

def cohort_digest(c):
    h=hashlib.sha256()
    for v in [c['u'],c['b_birth'],c['energy_birth'],*c['mu'],*c['alpha']]: h.update(struct.pack('<d',v))
    h.update(c['role'].encode())
    return h.hexdigest()

def exact_moments(c):
    weighted=[(Fraction(m)**2,Fraction(a)) for m,a in zip(c['mu'],c['alpha'])]
    return (sum((w for z,w in weighted),Fraction()),
            sum((w*(3*z-1)/2 for z,w in weighted),Fraction()),
            sum((w*(35*z*z-30*z+3)/8 for z,w in weighted),Fraction()))

def real_moments(c,x,b):
    d=b-c['b_birth']; p=math.exp(2*d); q=math.exp(-4*d)
    energy=[]; stress=[]
    for mu,w in zip(c['mu'],c['alpha']):
        a=p*(1-mu*mu); z=q*mu*mu; rr=math.sqrt(a+z)
        energy.append(w*rr); stress.append(w*(z-a/2)/rr)
    prefactor=c['energy_birth']*math.exp(-4*(x-c['u']))
    return prefactor*math.fsum(energy),prefactor*math.fsum(stress)

def complex_energy_derivative(cohorts,x,b,bprime):
    # Recompute a directional derivative of the closed form, never integrate.
    epsilon=1e-25
    xc=complex(x,epsilon); bc=complex(b,epsilon*bprime); terms=[]
    for c in cohorts:
        if c['u']>x: continue
        d=bc-c['b_birth']; p=cmath.exp(2*d); q=cmath.exp(-4*d)
        rays=[w*cmath.sqrt(p*(1-m*m)+q*m*m) for m,w in zip(c['mu'],c['alpha'])]
        radial=complex(math.fsum(v.real for v in rays),math.fsum(v.imag for v in rays))
        terms.append(c['energy_birth']*cmath.exp(-4*(xc-c['u']))*radial)
    return math.fsum(t.imag for t in terms)/epsilon

def physics(case,r,reference,prereg):
    cfg=r['input']['config']; obs=r['observations']; stock=r['final_cohorts']; events=r['events']; seg=r['segments']
    eventmap={e['u']:e for e in events}; closed=case.startswith('closed')
    gate=Fraction(3,10**15); old=r['input']['initial_cohorts']; nold=len(old)
    certificates=[]; allnorm=True; allmoment=True; allcert=True
    positive=True; reflection=True
    for c in stock:
        positive &= math.isfinite(c['energy_birth']) and c['energy_birth']>0 and all(math.isfinite(w) and w>0 for w in c['alpha'])
        reflection &= c['mu']==[-m for m in reversed(c['mu'])] and c['alpha']==list(reversed(c['alpha']))
        norm,m2,m4=exact_moments(c); allnorm &= abs(norm-1)<=gate
        if c['role']=='new_isotropic_P24':
            cert=eventmap[c['u']]['exact_moment_certificate']; good=max(abs(m2),abs(m4))<=gate
            agree=(norm==Fraction(cert['sum_alpha_exact']) and m2==Fraction(cert['m2_exact']) and m4==Fraction(cert['m4_exact']))
            allmoment &= good; allcert &= agree and cert['pass'] and Fraction(cert['gate_rational'])==gate
            certificates.append({'u':c['u'],'moment_pass':good,'native_exact_agreement':agree,
                                 'normalization_residual':str(norm-1),'m2':str(m2),'m4':str(m4)})
    oldmatch=bits(stock[:nold])==bits(old)
    oldhash=[cohort_digest(c) for c in stock[:nold]]
    oldmatch &= oldhash==r['input']['expected_old_digests']==r['old_stock_digests']
    bornhash=all(cohort_digest(c)==eventmap[c['u']]['birth_rule_sha256'] for c in stock[nold:])
    max_constraint=0.; max_constraint_field=0.; max_e_observer=0.; max_pi_observer=0.; max_energy=0.; max_sigma=0.
    reference_errors=[0.,0.,0.]; output_map={o['x']:o for o in obs}
    right_bank=True; state_jump=True; birthmatch=True
    ref_by_x={v['x']:[v['h'],v['b'],v['y']] for v in reference['rows']}
    for o in obs:
        x=o['x']; h,b,y=o['state']; e=o['e_radiation']; donor=o['e_donor']
        residual=h*h-y*y-donor-e-cfg['cosmological_constant']
        scale=h*h+y*y+donor+e+cfg['cosmological_constant']
        relative=abs(residual)/scale
        max_constraint=max(max_constraint,relative)
        max_constraint_field=max(max_constraint_field,abs(relative-o['c_relative']),abs(residual-o['c']))
        m=[real_moments(c,x,b) for c in stock if c['u']<=x]
        er=math.fsum(v[0] for v in m); pi=math.fsum(v[1] for v in m)
        max_e_observer=max(max_e_observer,abs(er-e)/e)
        max_pi_observer=max(max_pi_observer,abs(pi-o['pi']))
        max_sigma=max(max_sigma,abs(math.sqrt(3)*abs(y)/h-o['sigma']))
        derivative=complex_energy_derivative(stock,x,b,y/h)
        max_energy=max(max_energy,abs(derivative+4*e+2*(y/h)*o['pi'])/e)
        target=ref_by_x[x] if closed else [math.sqrt(cfg['donor0']*math.exp(-3*x)+cfg['old_isotropic']*math.exp(-4*x)+cfg['cosmological_constant']),cfg['b0'],0.]
        reference_errors=[max(m,abs(a-z)) for m,a,z in zip(reference_errors,o['state'],target)]
    event_rel=0.; event_field_error=0.
    for e,c in zip(events,stock[nold:]):
        jump=e['donor_after']+e['radiation_after']-e['donor_before']-e['radiation_before']
        relative=abs(jump)/(e['donor_before']+e['radiation_before'])
        event_rel=max(event_rel,relative); event_field_error=max(event_field_error,abs(jump-e['energy_jump']),abs(relative-e['energy_jump_relative']))
        o=output_map[e['u']]
        right_bank &= bits(o['state'])==bits(e['state']) and bits(o['e_donor'])==bits(e['donor_after']) and bits(o['e_radiation'])==bits(e['radiation_after']) and bits(o['pi'])==bits(e['pi_after'])
        state_jump &= all(v==0 for v in e['state_jump'])
        birthmatch &= bits([c['u'],c['b_birth'],c['energy_birth']])==bits([e['u'],e['state'][1],e['energy_birth']])
        birthmatch &= e['previous_cohort_digests_unchanged']
    exposure=cfg['birth_end'] if events else 0.
    donor_expected=cfg['donor0']*math.exp(-3*cfg['x_end']-cfg['decay_lambda']*exposure)
    donor_error=abs(obs[-1]['e_donor']-donor_expected)/(donor_expected or 1.)
    counters=defaultdict(int)
    for s in seg:
        for k,v in s['counters'].items(): counters[k]+=v
    g=prereg['gates']
    qualities={
        'output_exact':bits([o['x'] for o in obs])==bits(r['input']['output_times']) and len(obs)==153,
        'finite_positive_background':all(o['state'][0]>0 and all(math.isfinite(v) for v in o['state']) for o in obs),
        'hamiltonian':max_constraint<=g['hamiltonian_relative'],
        'cohort_energy_identity':max_energy<=g['cohort_energy_relative'],
        'event_energy':event_rel<=g['event_energy_relative'],
        'donor_endpoint':donor_error<=g['donor_endpoint_relative'],
        'positive_stock':positive,'reflection_exact':reflection,'normalization_exact':allnorm,
        'new_birth_moments_exact':allmoment,'independent_exact_observer_agreement':allcert,
        'old_stock_hash_and_raw_bits':oldmatch,'previous_birth_hashes':bornhash,
        'clock_augmentation':max(abs(o['clock_error']) for o in obs)<=g['clock_abs'],
        'fine_reference_abs':max(reference_errors)<=g['fine_reference_abs'],
    }
    if closed:
        qualities['fresh_event_workspaces']=len(seg)==cfg['k']+1 and all(s['fresh_driver'] and s['fresh_immutable_bank'] for s in seg)
        qualities['nonzero_event_rhs_jump']=len(events)==cfg['k'] and all(e['rhs_after'][0]!=e['rhs_before'][0] for e in events)
    if 'mf_into_ls' in case:
        qualities['actual_analytic_jvp_and_ft_work']=counters['jvp_calls']>0 and counters['ft_calls']>0
    else:
        qualities['actual_small_direct_work']=counters['direct_factorizations']>0 and counters['jacobian_builds']>0
    check('science_gates:'+case,all(qualities.values()),qualities)
    check('stronger_observer_event_consistency:'+case,
          max_constraint_field==0 and event_field_error==0 and max_sigma==0 and max_e_observer<1e-14 and max_pi_observer<1e-14 and right_bank and state_jump and birthmatch)
    return {'case':case,'quality_gates':qualities,'birth_certificates':certificates,
            'counts':{'observations':len(obs),'births':len(events),'segments':len(seg)},
            'max_hamiltonian_relative':max_constraint,'max_cohort_energy_relative_independent_fsum':max_energy,
            'max_event_energy_relative':event_rel,'donor_endpoint_relative':donor_error,
            'max_clock_abs':max(abs(o['clock_error']) for o in obs),'max_abs_h_b_y_reference':reference_errors,
            'max_independent_real_E_relative':max_e_observer,'max_independent_real_Pi_abs':max_pi_observer,
            'constraint_field_exact':max_constraint_field==0,'event_field_exact':event_field_error==0,
            'right_bank_outputs':right_bank,'continuous_state':state_jump,'birth_state_energy_binding':birthmatch,
            'old_stock_digests':oldhash,'solver_counters':dict(counters)}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    protocol=load(LANE/'evidence_s10/c4/BENCHMARK_PROTOCOL.json')
    manifest=load(LANE/'s10_optimization/SOURCE_MANIFEST.json')
    manifest_hash=hashlib.sha256(data(LANE/'s10_optimization/SOURCE_MANIFEST.json')).hexdigest()
    freeze=[]
    for f in manifest['files']:
        b=data(ROOT/'bass'/f['path'])
        ok=len(b)==f['bytes'] and hashlib.sha256(b).hexdigest()==f['sha256'] and hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==f['git_blob_sha']
        freeze.append({'path':f['path'],'match':ok})
    check('all_frozen_source_input_bytes_and_git_blobs',all(x['match'] for x in freeze),{'files':len(freeze)})
    check('fixed_owner_and_solver_source',manifest['fixed_spectral_owner']==OWNER and manifest['vigilode_source']==VIGILODE)
    prereg=load(LANE/'s9_vigilode/PREREGISTRATION.json')
    check('original_S9_13_sources_unchanged',all(hashlib.sha256(data(LANE/'s9_vigilode'/p)).hexdigest()==h for p,h in prereg['source_sha256'].items()),{'files':len(prereg['source_sha256'])})
    runtime=ROOT/'runtime_s9_20261020/build/client'
    runtime_rows=[]
    for directory in ['s10_optimization','s9_vigilode']:
        for p in sorted((LANE/directory/'src').rglob('*.rs')):
            rel=p.relative_to(LANE); q=runtime/rel
            runtime_rows.append({'path':str(rel),'same_bytes':data(p)==data(q)})
        for f in ['Cargo.toml','Cargo.lock']:
            p=LANE/directory/f; q=runtime/directory/f
            runtime_rows.append({'path':str(p.relative_to(LANE)),'same_bytes':data(p)==data(q)})
    runtime_rows.append({'path':'balance_p24.rs','same_bytes':data(LANE/'balance_p24.rs')==data(runtime/'balance_p24.rs')})
    check('compiled_runtime_source_matches_frozen_repo',all(x['same_bytes'] for x in runtime_rows),runtime_rows)
    oldlock=tomllib.loads(data(LANE/'s9_vigilode/Cargo.lock').decode())['package']
    newlock=tomllib.loads(data(LANE/'s10_optimization/Cargo.lock').decode())['package']
    packagekey=lambda p:(p['name'],p['version'],p.get('source'))
    newpackages={packagekey(p):p for p in newlock}
    check('old_locked_packages_unchanged',all(p==newpackages[packagekey(p)] for p in oldlock),{'old':len(oldlock),'new':len(newlock)})
    git=load(ROOT/'intake/publication/S10_C3_C5_GIT_READBACK.json')
    check('recorded_git_source_readback',git['commit']==SOURCE and git['tree']==TREE and git['ref_readback']['matched'] and git['tree_readback']['complete'] and not git['tree_readback']['truncated'])
    processes=[]
    for phase in ['build','tests','micro','history','parallel','allocation_build','allocations']:
        p=load(EX/(phase+'_r1_PROCESS.json'))
        ok=p['exit_code']==0 and p['attempt']=='r1' and p['status']=='completed' and p['published_source_commit']==SOURCE and p['published_source_tree']==TREE and p['source_manifest_sha256']==manifest_hash
        ok &= p['git_readback_sha256']==hashlib.sha256(data(ROOT/'intake/publication/S10_C3_C5_GIT_READBACK.json')).hexdigest()
        ok &= hashlib.sha256(data(Path(p['log']['path']))).hexdigest()==p['log']['sha256']
        if 'binary' in p: ok &= hashlib.sha256(data(Path(p['binary']['path']))).hexdigest()==p['binary']['sha256']
        check('process_binding:'+phase,ok)
        processes.append(p)
    timingphases=[p for p in processes if p['phase'] in ['micro','history','parallel']]
    buildphases=[p for p in processes if p['phase'] in ['build','tests','allocation_build']]
    dt=datetime.datetime.fromisoformat
    overlaps=[(a['phase'],b['phase']) for a in timingphases for b in buildphases if max(dt(a['started_at_utc']),dt(b['started_at_utc']))<min(dt(a['finished_at_utc']),dt(b['finished_at_utc']))]
    check('no_recorded_build_overlaps_timing',not overlaps,overlaps)
    testlog=data(EX/'tests_r1.log').decode()
    check('targeted_tests_recorded_11_pass',bool(re.search(r'test result: ok\. 11 passed; 0 failed;',testlog)))
    disasm=data(EX/'AVX2_TERMS_DISASSEMBLY.txt').decode()
    simdinspect=load(EX/'SIMD_BINARY_INSPECTION.json')
    check('saved_SIMD_symbol_packed_sqrt_div_no_fma',bool(re.search(r'\bvsqrtpd\b',disasm)) and bool(re.search(r'\bvdivpd\b',disasm)) and not re.search(r'\bv(?:fmadd|fmsub|fnmadd|fnmsub)\w*\b',disasm) and simdinspect['binary_sha256']==hashlib.sha256(data(EX/'s10-benchmark-timing.bin')).hexdigest())

    microall=rows(MEAS/'MICRO_SAMPLES.jsonl'); micro=[v for v in microall if v['kind']=='micro']; diagnostics=[v for v in microall if v['kind']=='diagnostic']
    historyall=rows(MEAS/'HISTORY_SAMPLES.jsonl'); history=[v for v in historyall if v['kind']=='history']; warmup=[v for v in historyall if v['kind']=='warmup_proof']
    parallelall=rows(MEAS/'PARALLEL_SAMPLES.jsonl'); parallel=[v for v in parallelall if v['kind']=='parallel']; parwarm=[v for v in parallelall if v['kind']=='parallel_warmup']
    prep=rows(MEAS/'PREPARE_SAMPLES.jsonl'); proof=load(MEAS/'MICRO_PROOF.json'); alloc=load(MEAS/'ALLOCATION_PROBE.json')['rows']
    counts={'micro_timed':len(micro),'micro_proof':len(proof),'micro_diagnostic':len(diagnostics),'history_timed':len(history),'history_warmup_proof':len(warmup),'parallel_timed_batches':len(parallel),'parallel_warmup_batches':len(parwarm),'prepare_timed':len(prep),'allocation_rows':len(alloc)}
    check('fixed_preregistered_counts',counts=={'micro_timed':1260,'micro_proof':108,'micro_diagnostic':108,'history_timed':280,'history_warmup_proof':24,'parallel_timed_batches':42,'parallel_warmup_batches':6,'prepare_timed':378,'allocation_rows':108},counts)
    expected_micro=[]
    for n in [16,64,256]:
        for k in [2,16,64]:
            for tr in ['changing','jvp_reuse']:
                for r in range(7):
                    for ci in range(5):
                        cand=MODES[1+(ci+r)%5]; order=['baseline',cand] if (ci+r)%2==0 else [cand,'baseline']
                        expected_micro.extend((n,k,tr,cand,r,m) for m in order)
    check('micro_entire_pair_order',[(v['n'],v['cohorts'],v['trace'],v['candidate'],v['round'],v['mode']) for v in micro]==expected_micro)
    check('fixed_micro_call_counts',all(v['calls']==max(64,min(8192,1048576//(v['n']*v['cohorts']))) for v in micro))
    groups=defaultdict(list)
    for p in proof: groups[p['n'],p['cohorts'],p['trace']].append(p)
    check('micro_proof_all_modes_bits',len(groups)==18 and all(len(p)==6 and {v['mode'] for v in p}==set(MODES) and all(v['exact'] and v['queries']==64 for v in p) and len({v['output_bits_sha256'] for v in p})==1 for p in groups.values()))
    check('SIMD_actually_selected_in_proof',all(p['backend']==('Avx2' if p['mode'] in ['simd','simd_cache'] else 'Scalar') for p in proof))
    expected_hist=[]
    for case in CASES:
        expected_hist.extend(('warmup_proof',case,None,None,m) for m in MODES)
        for r in range(7):
            for ci in range(5):
                cand=MODES[1+(ci+r)%5]; order=['baseline',cand] if (ci+r)%2==0 else [cand,'baseline']
                expected_hist.extend(('history',case,cand,r,m) for m in order)
    check('history_entire_pair_and_warmup_order',[(v['kind'],v['case'],v.get('candidate'),v.get('round'),v['mode']) for v in historyall]==expected_hist)
    expected_prep=[(n,k,r,MODES[(o+r)%6]) for n in [16,64,256] for k in [2,16,64] for r in range(7) for o in range(6)]
    check('preparation_entire_order',[(v['n'],v['cohorts'],v['round'],v['mode']) for v in prep]==expected_prep and all(not v['drop_included'] and not v['input_bank_clone_included'] for v in prep))
    expected_parallel=[]
    for w in [1,2,4]:
        expected_parallel.extend(('parallel_warmup',w,None,m) for m in ['baseline','simd_cache'])
        for r in range(7): expected_parallel.extend(('parallel',w,r,m) for m in (['baseline','simd_cache'] if r%2==0 else ['simd_cache','baseline']))
    check('parallel_entire_pair_and_warmup_order',[(v['kind'],v['workers'],v.get('round'),v['mode']) for v in parallelall]==expected_parallel)

    expected_hash={}; representative=[]; stored_comparison=[]; baseline_raw={}
    for case in CASES:
        baseline=load(MEAS/(case+'_baseline.json')); baseline_raw[case]=baseline
        original=load(LANE/'evidence_s9/run_20261020_r1'/case/'RAW.json')
        stored=bits(science_object(baseline))==bits(science_object(original))
        stored_comparison.append({'case':case,'full_non_timing_f64_bits_equal':stored})
        for mode in MODES:
            p=MEAS/(case+'_'+mode+'.json'); actual=load(p); digest=scientific_digest(p)
            same=bits(science_object(actual))==bits(science_object(baseline))
            if mode=='baseline': expected_hash[case]=digest
            loghash=[w['scientific_sha256'] for w in warmup if w['case']==case and w['mode']==mode]
            ok=same and actual['status']=='completed' and actual['failure'] is None and digest==expected_hash[case] and loghash==[digest]
            representative.append({'case':case,'mode':mode,'full_non_timing_f64_bits_equal':same,'reconstructed_scientific_sha256':digest,'matches_runtime_digest':loghash==[digest],'pass':ok})
    check('all_24_representative_scientific_hashes_independently_reconstructed',all(r['pass'] for r in representative))
    check('all_four_release_baselines_equal_stored_S9_except_timer',all(r['full_non_timing_f64_bits_equal'] for r in stored_comparison))
    check('all_280_timed_history_digests_status',all(r['scientific_sha256']==expected_hash[r['case']] and r['exact'] and r['status']=='completed' for r in history))
    check('all_42_parallel_batches_output_order_and_digest',all(r['hashes']==[expected_hash[c] for c in CASES] and r['exact'] and r['all_completed'] and r['jobs']==4 and r['pool_construction_included'] for r in parallel))
    check('parallel_warmup_logged_completion',all(r['exact'] and r['jobs']==4 for r in parwarm))
    expectedfile=load(MEAS/'EXPECTED_HISTORY_HASHES.json')
    check('expected_hash_file',expectedfile=={'cases':CASES,'hashes':[expected_hash[c] for c in CASES]})

    micro_stats=pairs(micro,['n','cohorts','trace','candidate']); history_stats=pairs(history,['case','candidate'])
    parallel_stats=[]
    for workers in [1,2,4]:
        for mode in ['baseline','simd_cache']:
            vals=[r['seconds'] for r in sorted((r for r in parallel if r['workers']==workers and r['mode']==mode),key=lambda r:r['round'])]
            parallel_stats.append({'workers':workers,'mode':mode,'batch_seconds':summary(vals),'histories_per_second':summary([4/t for t in vals])})
    prep_stats=[]
    for n in [16,64,256]:
        for k in [2,16,64]:
            for mode in MODES:
                vals=[v['seconds'] for v in prep if (v['n'],v['cohorts'],v['mode'])==(n,k,mode)]
                prep_stats.append({'n':n,'cohorts':k,'mode':mode,'seconds':summary(vals)})
    assessment=load(ROOT/'intake/optimization/analysis_r1/S10_ASSESSMENT.json')
    for name,computed,key in [('micro',micro_stats,['n','cohorts','trace','candidate']),('history',history_stats,['case','candidate']),('parallel',parallel_stats,['workers','mode']),('preparation',prep_stats,['n','cohorts','mode'])]:
        expected={tuple(r[k] for k in key):r for r in assessment[name]}
        check('independent_all_statistics:'+name,len(expected)==len(computed) and all(stat_equal(r,expected[tuple(r[k] for k in key)]) for r in computed),{'groups':len(computed),'summary_rounding_comparison':'at most four ulps; scientific equality remains bit exact'})
    diag_ok=True
    for r in diagnostics:
        cached=r['mode'] in ['cache','simd_cache']; c=r['counters']
        expected=4 if cached and r['trace']=='jvp_reuse' else 64
        diag_ok &= c['enabled'] and r['calls']==64 and c['kernel_evaluations']==expected
        diag_ok &= c['jvp_cache_hits']==(60 if cached and r['trace']=='jvp_reuse' else 0)
        diag_ok &= c['rhs_cache_hits']==0 and c['jvp_rhs_transfers']==0
    check('diagnostic_work_counts_from_fixed_trace',diag_ok)
    alloc_ok=all(r['evaluation_calls']==64 and r['bank_clone_excluded_from_setup'] and r['not_live_or_peak_bytes'] for r in alloc)
    alloc_ok &= all(r['allocation_or_reallocation_calls']==(64*(r['cohorts']+1) if r['mode']=='baseline' else 0) for r in alloc)
    check('allocation_counts_and_compiled_out_timing_scope',alloc_ok)

    reference=load(LANE/'s9_vigilode/reference/S8_PRIMAL.json')
    sciences=[physics(c,baseline_raw[c],reference,prereg) for c in CASES]
    check('independent_science_68_decisions',sum(len(s['quality_gates']) for s in sciences)==68 and all(all(s['quality_gates'].values()) for s in sciences))
    outputs={'schema':'BASS_S10_C9_INDEPENDENT_RAW_RECOMPUTATION_V1','reviewer':'/root/science_reuse_and_review',
             'status':'PASS_SCOPED' if all(c['pass'] for c in CHECKS) else 'REVIEW_FINDING',
             'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'source_commit':SOURCE,'source_tree':TREE,'source_manifest_sha256':manifest_hash,
             'raw_counts':counts,'source_files':freeze,'runtime_sources':runtime_rows,
             'independent_checks':CHECKS,'failed_checks':[c for c in CHECKS if not c['pass']],
             'representative_receipts':representative,'stored_S9_comparison':stored_comparison,
             'micro_statistics':micro_stats,'history_statistics':history_stats,
             'parallel_statistics':parallel_stats,'preparation_statistics':prep_stats,
             'physics':sciences,'science_gate_count':sum(len(s['quality_gates']) for s in sciences),
             'unique_birth_certificates_recomputed':sum(len(s['birth_certificates']) for s in sciences),
             'observations_recomputed':sum(s['counts']['observations'] for s in sciences),
             'review_execution':{'ODE_or_benchmark_calls':0,'compiles':0,'source_mutations':0,'network_requests':0,
               'calculation':'Pure saved-data hashing, seven-sample statistics, exact rational polynomial sums, algebraic observer and complex-step directional derivative.'},
             'limitation':'Current four stored S9 inputs, current CPU/backend and registered grid. IQR is not a confidence interval; no universal floating-equivalence or portable-speed claim.',
             'files_read':INPUTS_READ}
    path=OUT/'INDEPENDENT_RECOMPUTATION.json'; path.write_text(json.dumps(outputs,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':outputs['status'],'checks':len(CHECKS),'failed_checks':outputs['failed_checks'],
                      'science_gate_count':outputs['science_gate_count'],'birth_certificates':outputs['unique_birth_certificates_recomputed'],
                      'observations':outputs['observations_recomputed'],'output':str(path)},ensure_ascii=False))

if __name__=='__main__': main()
