#!/usr/bin/env python3
"""Read fixed S9 source/receipts; write C2 static cost evidence only.

No solver/kernel invocation, compilation, network, source modification or timing
benchmark. Counts named static_* are source-level work, not measured CPU events.
"""
from __future__ import annotations

import collections
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import tomllib

ROOT = Path('/workspace/scratch/a1783628e7a7')
LANE = ROOT / 'bass/research/bass_isotropy_response_20261018'
CLIENT = LANE / 's9_vigilode'
RUN = LANE / 'evidence_s9/run_20261020_r1'
RUNTIME = ROOT / 'runtime_s9_20261020'
OUT = ROOT / 'intake/optimization/c2'
SKILL = Path('/root/.codex/plugins/cache/created-by-me-remote/physmath-research-loop/1.3.0/skills/physmath-research-loop')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def fingerprint(path):
    data = path.read_bytes()
    try:
        label = str(path.relative_to(ROOT))
    except ValueError:
        label = str(path)
    return {'path': label, 'bytes': len(data), 'sha256': sha(data),
            'git_blob_sha': hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()}

def readj(path):
    return json.loads(path.read_text())

def writej(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')

OUT.mkdir(parents=True, exist_ok=True)
created = datetime.datetime.now(datetime.timezone.utc).isoformat()
prereg = readj(CLIENT/'PREREGISTRATION.json')
preparation = readj(ROOT/'intake/runtime/PREPARATION_RETURN.json')
execution = readj(RUN/'CURRENT_EXECUTION.json')
source_fingerprints = []
checks = []
for relative, expected in {**prereg['source_sha256'], **prereg['input_sha256']}.items():
    p = CLIENT/relative
    f = fingerprint(p)
    f.update({'role': 'preregistered_s9_source_or_input', 'expected_sha256': expected,
              'matches_preregistration': f['sha256'] == expected})
    source_fingerprints.append(f)
    checks.append(f['matches_preregistration'])
balance = fingerprint(LANE/'balance_p24.rs')
balance.update({'role': 'unchanged_p24_owner', 'expected_sha256': prereg['unchanged_balance_owner_sha256'],
                'matches_preregistration': balance['sha256'] == prereg['unchanged_balance_owner_sha256']})
source_fingerprints.append(balance)
checks.append(balance['matches_preregistration'])

upstream_paths = ['Cargo.toml','crates/rodas5p-core/Cargo.toml',
                  'crates/rodas5p-integrators/Cargo.toml',
                  'crates/rodas5p-integrators/src/problem.rs',
                  'crates/rodas5p-integrators/src/rodas5p_fast_small.rs',
                  'crates/rodas5p-integrators/src/rodas5p_matrix_free_fast.rs']
upstream_manifest = {f['path']: f for f in readj(CLIENT/'VIGILODE_SOURCE.json')['files']}
for relative in upstream_paths:
    f = fingerprint(RUNTIME/'vigilode_source'/relative)
    expected = upstream_manifest[relative]
    f.update({'role': 'inspected_pinned_upstream', 'upstream_path': relative,
              'expected_sha256': expected['sha256'], 'expected_git_blob_sha': expected['git_blob'],
              'matches_pin': (f['sha256'] == expected['sha256'] and
                              f['git_blob_sha'] == expected['git_blob'] and f['bytes'] == expected['size'])})
    source_fingerprints.append(f)
    checks.append(f['matches_pin'])

skill_context = []
for relative in ['SKILL.md','STAGE_SELECTION.md','references/POLICY_INTEGRATION.md',
                 'references/CODING_LOOP.md','references/SUBAGENT_MODE.md']:
    f = fingerprint(SKILL/relative)
    f['selected_section'] = 'C2 execution-grade completion contract' if relative.endswith('CODING_LOOP.md') else 'full document'
    skill_context.append(f)

evidence_fingerprints = []
rows = []
counter_sum = collections.Counter()
for raw_path in sorted(RUN.glob('*/RAW.json')):
    raw = readj(raw_path)
    inp = readj(raw_path.with_name('INPUT.json'))
    process = readj(raw_path.with_name('PROCESS.json'))
    raw_fp, inp_fp = fingerprint(raw_path), fingerprint(raw_path.with_name('INPUT.json'))
    verified = (raw_fp['sha256'] == process['raw_sha256'] and raw_fp['bytes'] == process['raw_bytes']
                and inp_fp['sha256'] == process['input_sha256'] and inp == raw['input'])
    checks.append(verified)
    evidence_fingerprints.extend([raw_fp, inp_fp, fingerprint(raw_path.with_name('PROCESS.json'))])
    assert raw['status'] == 'completed' and verified
    final_cohorts = raw['final_cohorts']
    n0 = len(inp['initial_cohorts'])
    n_births = len(raw['events'])
    solver_evals = node_visits = cohort_visits = vec_requests = payload_bytes = exp_calls = 0
    admin_evals = admin_nodes = admin_cohorts = admin_vecs = admin_payload = admin_exp = 0
    counters = collections.Counter()
    segments = []
    def cost(cohort_count, count):
        nodes = sum(len(c['mu']) for c in final_cohorts[:cohort_count])
        return {'evals': count, 'nodes': count*nodes, 'cohorts': count*cohort_count,
                'vecs': count*(cohort_count+1), 'payload': count*24*(nodes+cohort_count),
                'exp': count*(3*cohort_count+1)}
    initial = cost(n0, 1)
    admin_evals += initial['evals']; admin_nodes += initial['nodes']; admin_cohorts += initial['cohorts']
    admin_vecs += initial['vecs']; admin_payload += initial['payload']; admin_exp += initial['exp']
    for s in raw['segments']:
        c = s['counters']; counters.update(c)
        count = sum(c.get(k, 0) for k in ['rhs_calls','ft_calls','jvp_calls','jacobian_builds'])
        m = cost(s['cohort_count'], count)
        solver_evals += m['evals']; node_visits += m['nodes']; cohort_visits += m['cohorts']
        vec_requests += m['vecs']; payload_bytes += m['payload']; exp_calls += m['exp']
        # All successful scheduled observations except each segment's first,
        # plus before, after, and right-bank replacement for every birth.
        a = cost(s['cohort_count'], len(s['output_times'])-1 + int(s['index'] < n_births))
        if s['index'] < n_births:
            b = cost(s['cohort_count']+1, 2)
            a = {k: a[k]+b[k] for k in a}
        admin_evals += a['evals']; admin_nodes += a['nodes']; admin_cohorts += a['cohorts']
        admin_vecs += a['vecs']; admin_payload += a['payload']; admin_exp += a['exp']
        segments.append({'index':s['index'], 'cohort_count':s['cohort_count'],
                         'angular_nodes':sum(len(z['mu']) for z in final_cohorts[:s['cohort_count']]),
                         'callback_evals':count,'accepted':c['accepted_steps'],
                         'rhs':c['rhs_calls'],'ft':c['ft_calls'],'jvp':c['jvp_calls'],
                         'jacobian':c['jacobian_builds'], 'admin_evals':a['evals']})
    es = [e['projection']['evaluations'] for e in raw['events']]
    exact_sizes = {}
    for key in ['sum_alpha_exact','m2_exact','m4_exact']:
        vals = [e['exact_moment_certificate'][key] for e in raw['events']]
        nums=[]; dens=[]
        for v in vals:
            chunks=v.split('/'); nums.append(abs(int(chunks[0])).bit_length()); dens.append(int(chunks[1] if len(chunks)>1 else '1').bit_length())
        exact_sizes[key]={'max_numerator_bits':max(nums,default=0),'max_denominator_bits':max(dens,default=0)}
    vector_clone_nodes = (3*sum(len(c['mu']) for c in inp['initial_cohorts'])
        +sum(sum(len(c['mu']) for c in final_cohorts[:s['cohort_count']]) for s in raw['segments'])
        +sum(sum(len(c['mu']) for c in final_cohorts[:n0+j+1]) for j in range(n_births)))
    row={'case':raw_path.parent.name,'arm':inp['solver']['arm'],'rtol':inp['solver']['rtol'],
         'receipt_status':raw['status'],'input_and_raw_match_process_receipt':verified,
         'initial_cohorts':n0,'initial_nodes':[len(c['mu']) for c in inp['initial_cohorts']],
         'births':n_births,'birth_nodes':inp['config']['n'],'segments_count':len(segments),
         'observations':len(raw['observations']), 'counters':dict(counters),
         'static_solver_eval_calls':solver_evals,'static_admin_eval_calls':admin_evals,
         'static_total_eval_calls':solver_evals+admin_evals,
         'static_solver_node_visits_sqrt':node_visits,'static_total_node_visits_sqrt':node_visits+admin_nodes,
         'static_solver_cohort_visits':cohort_visits,'static_total_cohort_visits':cohort_visits+admin_cohorts,
         'static_solver_exp_calls':exp_calls,'static_total_exp_calls':exp_calls+admin_exp,
         'static_solver_vec_requests':vec_requests,'static_total_vec_requests':vec_requests+admin_vecs,
         'static_solver_vec_payload_bytes_requested':payload_bytes,
         'static_total_vec_payload_bytes_requested':payload_bytes+admin_payload,
         'projection_distribution_evaluations':sum(es),'projection_min_per_birth':min(es,default=0),
         'projection_max_per_birth':max(es,default=0),
         'static_projection_node_exp_calls':sum(es)*inp['config']['n'],
         'static_projection_evaluated_vec_requests':2*sum(es),
         'static_exact_certificate_calls':n_births,
         'static_exact_from_float_calls':2*n_births*inp['config']['n'],
         'exact_certificate_output_integer_sizes':exact_sizes,
         'static_birth_support_calls':2*n_births,
         'static_birth_support_exp_expressions':2*n_births*3*inp['config']['n'],
         'static_cohort_clone_angular_nodes':vector_clone_nodes,
         'static_cohort_clone_mu_alpha_bytes':vector_clone_nodes*16,
         'output_clipped_steps':sum(s['output_clipped_steps'] for s in raw['segments']),
         'raw_output_bytes':raw_fp['bytes'],'segments':segments,
         'timing_interpretation':'Original debug-profile timing is deliberately not used to estimate or claim a speedup.'}
    rows.append(row); counter_sum.update(counters)

lock=tomllib.loads((CLIENT/'Cargo.lock').read_text())
packages = {(p['name'], p['version']):p for p in lock['package']}
names = {'pulp','rayon','rayon-core','crossbeam-deque','crossbeam-epoch','crossbeam-utils','faer',
         'faer-traits','gemm','gemm-common','private-gemm-x86','nano-gemm','bytemuck','raw-cpuid',
         'cpufeatures','num_cpus','num-bigint','num-rational','num-traits'}
build_features={}
for p in sorted((RUNTIME/'build/target/debug/.fingerprint').glob('*/lib-*.json')):
    d=readj(p); name=p.stem[4:].replace('_','-')
    if name in names or name == 'num-cpus':
        build_features.setdefault(name,[]).append({'features':json.loads(d.get('features','[]')),
                                                  'evidence':fingerprint(p)})
inventory=[]
for p in sorted((RUNTIME/'vendor').glob('*/Cargo.toml')):
    t=tomllib.loads(p.read_text()); q=t.get('package',{})
    if q.get('name') not in names: continue
    lock_entry=packages[(q['name'],q['version'])]
    licenses=[fingerprint(v) for v in sorted(p.parent.iterdir()) if v.is_file() and
              any(s in v.name.lower() for s in ['license','copying'])]
    inventory.append({'name':q['name'],'version':q['version'],'license_declared':q.get('license'),
                      'license_file_declared':q.get('license-file'),'license_notice_files':licenses,
                      'repository':q.get('repository'),'cargo_manifest':fingerprint(p),
                      'cargo_lock_checksum':lock_entry.get('checksum'),
                      'cargo_lock_dependencies':lock_entry.get('dependencies',[]),
                      'compiled_feature_evidence':build_features.get(q['name'].replace('_','-'),[]),
                      'declared_features':t.get('features',{})})

cpu_text=Path('/proc/cpuinfo').read_text(); processors=cpu_text.strip().split('\n\n')
cpu_records=[{l.split(':',1)[0].strip():l.split(':',1)[1].strip() for l in record.splitlines() if ':' in l}
             for record in processors]
flags=[set(x.get('flags','').split()) for x in cpu_records]
common_flags=sorted(set.intersection(*flags)) if flags else []
cg={n:Path('/sys/fs/cgroup'/Path(n)).read_text().strip() for n in
    ['cpu.max','memory.max','memory.current','memory.peak','cpuset.cpus.effective']}
stat={}
for line in Path('/sys/fs/cgroup/memory.stat').read_text().splitlines():
    key,value=line.split()
    if key in {'anon','file','kernel','slab','inactive_file','active_file','shmem'}:stat[key]=int(value)
machine={'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'machine':platform.machine(),'cpu_models':sorted({x.get('model name','') for x in cpu_records}),
         'logical_visible':os.cpu_count(),'affinity_cpu_count':len(os.sched_getaffinity(0)),
         'common_exposed_cpu_flags':common_flags,'cgroup':cg,'memory_stat_selected_bytes':stat,
         'cpu_quota_effective_cores':int(cg['cpu.max'].split()[0])/int(cg['cpu.max'].split()[1]),
         'memory_limit_bytes':int(cg['memory.max']),
         'interpretation':'Exposed virtual CPU flags and shared cgroup counters only; no vector instruction, clock or throughput benchmark; current/peak memory are not task RSS.'}

core_source_still_matches=all(fingerprint(ROOT/f['path'])['sha256']==f['sha256'] for f in source_fingerprints)
checks.append(core_source_still_matches)
aggregate={k:sum(r[k] for r in rows) for k in ['static_solver_eval_calls','static_admin_eval_calls',
           'static_total_eval_calls','static_total_node_visits_sqrt','static_total_cohort_visits',
           'static_total_exp_calls','static_total_vec_requests','static_total_vec_payload_bytes_requested',
           'projection_distribution_evaluations','static_projection_node_exp_calls',
           'static_projection_evaluated_vec_requests','static_exact_certificate_calls',
           'static_exact_from_float_calls','static_birth_support_calls','raw_output_bytes']}
result={'schema':'BASS_S10_C2_CODE_COST_MAP_V1','created_utc':created,
        'status':'C2_STATIC_MAPPING_COMPLETE','selected_stage':'C2',
        'skill_context_used':{'version':'1.3.0','paths':skill_context,
            'applied_contract':'Source/authority first; formulas, normalization, time variables, IC/BC, closure and exact function/data correspondence; distinguish measured counters from static work and future speed tests.',
            'native_child_task':'/root/s9_runtime_prepare','parent':'/root','no_recursive_review':True},
        'scope':{'source_modified':False,'compiles':0,'scientific_histories_executed':0,
                 'benchmarks_executed':0,'external_writes':0,'external_reads':0,
                 'only_outputs_under':'intake/optimization/c2'},
        'identity':{'BASS_scientific_source':'4b30957cb008aad8019bb1a673937fc67bd017e8',
            'BASS_actual_results_commit':'a40311796f9aac5ea5e0e58c630bee2a78443353',
            'vigilode_source':prereg['vigilode_source'],'spectral_owner':prereg['fixed_spectral_owner'],
            'typed_checks':'BYTE identity for locked source/input/receipt hashes; STRUCTURAL mapping and counter-derived static work; no new NUMERICAL or SCIENTIFIC_EQUIVALENCE claim',
            'source_input_receipt_checks_pass':all(checks),'source_unchanged_during_inspection':core_source_still_matches,
            'preregistration':fingerprint(CLIENT/'PREREGISTRATION.json'),
            'original_execution':fingerprint(RUN/'CURRENT_EXECUTION.json'),
            'preparation':fingerprint(ROOT/'intake/runtime/PREPARATION_RETURN.json')},
        'formulas':{'time':'x = ln(a/a_ref); y = s/H_star; h = H/H_star; no physical dimensional unit conversion performed by this adapter',
            'cohort':'d=b-b_birth, a=exp(2d)*(1-mu^2), c=exp(-4d)*mu^2, R=sqrt(a+c), N=c-a/2, D=N/R, D_b=(-4c-a)/R+2N^2/R^3; [E,Pi,Pi_b]=energy_birth*exp(-4*(x-u))*sum(alpha*[R,D,D_b])',
            'donor':'E_d=donor0*exp(-3*x-lambda*exposure); exposure frozen in each segment',
            'rhs':'[(-h*h-2*y*y-E_d/2-E+Lambda)/h, y/h, -3*y+Pi/h]',
            'IC':'h0=sqrt(y0*y0+donor0+old_isotropic+old_anisotropic+Lambda); b0,y0 from input',
            'event':'u_j=(j+1/2)*birth_end/k; w=E_d_before*(-expm1(-lambda*du)); fixed state, append positive P24-certified new cohort, exposure=(j+1)*du, new bank/driver',
            'objective':'new-birth KL projection alpha_i proportional q_i*exp(lambda2*P2(mu_i)+lambda4*P4(mu_i)); sum alpha=1, sum alpha P2=sum alpha P4=0 to unchanged gates'},
        'static_cost_model':{'C':'current cohort count','N':'sum of stored angular nodes over current cohorts',
            'eval':'O(N+C); 3*C+1 exp expressions; N sqrt expressions; C+1 explicit Vec constructions, requested numeric payload 24*(N+C) bytes; not simultaneous live bytes or measured allocator calls',
            'eval_transient_live_payload_upper_shape':'24*(C+max cohort node count), excluding allocator capacity rounding/metadata, stack and output structs',
            'callbacks':'All RHS, analytic Ft, JVP and Small Jacobian callbacks call the same full eval once; JVP then performs a 3x3 matrix-vector operation.',
            'admin':'initial observe + each successful segment scheduled output after initial + before/after birth eval + right-bank observation replacement; total observations+3*births',
            'projection':'E evaluated distributions => 2*E explicit Vec constructions and n*E exp expressions; fixed overhead geometry/q/p2/p4/logq separate; not Newton iteration count',
            'compiler_caveat':'Compiler may hoist expressions/elide allocations; only allocation/instruction instrumentation can establish actual runtime events.'},
        'cases':rows,'aggregate_static_work':aggregate,'aggregate_original_counters':dict(counter_sum),
        'reusable_packages':inventory,'cpu_capabilities':machine,
        'fixed_gates':prereg['gates'],'fixed_angular_policy':prereg['angular_policy'],
        'open_measurements':['release-profile allocation counts/bytes and peak RSS by phase',
            'kernel/JVP cache hit-miss and state-bank identity trace',
            'projection versus exact-rational versus ODE versus JSON wall/CPU breakdown',
            'matched-accuracy scalar vs SIMD and deterministic thread-count sensitivity',
            'warmup/repeated independent timing, dispersion, cgroup CPU throttling and memory accounting'],
        'no_speedup_claim':True}
writej('SOURCE_FINGERPRINTS.json',{'schema':'BASS_S10_C2_SOURCE_FINGERPRINTS_V1','created_utc':created,
       'sources':source_fingerprints,'raw_evidence':evidence_fingerprints,
       'skill_context_used':skill_context,'all_checked_identities_match':all(checks)})
writej('CPU_CAPABILITIES.json',machine)
writej('REUSABLE_PACKAGE_INVENTORY.json',{'schema':'BASS_S10_C2_PACKAGE_INVENTORY_V1','packages':inventory,
       'scope':'Locally pinned Cargo.toml/license text and existing build feature evidence, not a new dependency resolution or legal opinion.'})
writej('CODE_COST_MAP.json',result)
print(json.dumps({'status':result['status'],'source_identity_match':all(checks),
                 'cases':[{'case':r['case'],'evals':r['static_total_eval_calls'],
                    'nodes':r['static_total_node_visits_sqrt'],'vecs':r['static_total_vec_requests'],
                    'payload':r['static_total_vec_payload_bytes_requested'],
                    'projection':r['projection_distribution_evaluations']} for r in rows],
                 'aggregate':aggregate},ensure_ascii=False,indent=2))
