"""C9 read-only evidence audit. No production scientific executable is called."""
import datetime as dt
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import statistics
import struct
import zipfile

BASE=Path('/workspace/scratch/14e1021f8231')
REPO=BASE/'bass_work'
UNIT=REPO/'research/bass_isotropy_response_20261018/s12_birth_memory'
OUT=BASE/'bass_s12_intake/c9_raw_provenance_run02'
OUT.mkdir(exist_ok=False)
checks=[];evidence={}; details={}
def raw(p):
    p=Path(p);p=p if p.is_absolute() else BASE/p
    b=p.read_bytes();evidence[str(p.relative_to(BASE))]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()};return b
def load(p):return json.loads(raw(p))
def sha(p):return hashlib.sha256(raw(p)).hexdigest()
def check(name,value,**data):checks.append({'name':name,'pass':bool(value),**data})
def hashes(root,rows):
    errors=[]
    for row in rows:
        b=raw(root/row['path']);size=row.get('bytes',row.get('size'))
        if len(b)!=size or hashlib.sha256(b).hexdigest()!=row['sha256']:errors.append(row['path'])
        if 'git_blob' in row and hashlib.sha1(b'blob '+str(len(b)).encode()+bytes([0])+b).hexdigest()!=row['git_blob']:errors.append(row['path']+':git')
    return errors
def process(record):
    bad=[]
    for label in ['stdout','stderr','stdin']:
        if record.get(label+'_path') is not None and record.get(label+'_sha256') is not None:
            if sha(record[label+'_path'])!=record[label+'_sha256']:bad.append(label)
    if record.get('elapsed_s',0)>1800 or record.get('timeout_s',1800)>1800:bad.append('time_cap')
    return bad

try:
    stage=BASE/'bass_delivery_s12/stage2'
    git=load(stage/'GIT_READBACK.json');build=load('runtime_s12/BUILD_RECEIPT.json')
    check('f4_published_source_and_build_binding',git['git_readback_pass'] and git['source_commit']==build['source_commit']=='f4cd0d53760783e6a58c3b0a98c64311ca489d28'
          and sha(stage/'GIT_READBACK.json')==build['binding_sha256'] and not hashes(stage/'source_snapshot',git['files']),published_files=len(git['files']))
    check('actual_build_and_two_binary_identities',build['status']=='COMPILED_SOURCE_BOUND' and len(build['commands'])==1
          and build['commands'][0]['exit_code']==0 and not process(build['commands'][0])
          and all(sha(row['path'])==row['sha256'] for row in build['binaries'].values()),binaries=build['binaries'])
    check('compiled_client_and_projector_bytes',all(sha(BASE/'runtime_s12/client/s12_birth_memory'/name)==digest for name,digest in build['runtime_client_files'].items())
          and sha(BASE/'runtime_s12/client/s11_p246/rust/projector.rs')==build['projector_sha256'],compiled_client_files=len(build['runtime_client_files']))
    vigilode=load(REPO/'research/bass_isotropy_response_20261018/s9_vigilode/VIGILODE_SOURCE.json')
    check('fixed_vigilode_owner_copy',vigilode['source_commit']==build['upstream']['commit']=='a21d573980f66fe02891bd216153443b5352f921'
          and len(vigilode['files'])==178 and not hashes(BASE/'runtime_s12/vigilode',vigilode['files']),files=178)
    science=load(UNIT/'ncp/SCIENCE_BINDING.json')
    check('narrow_immutable_science_binding',science['source_commit']==build['source_commit'] and len(science['files'])==15
          and not hashes(REPO,science['files']),note='Mutable DAG and later documentation are not compared against the old scientific source.')

    core=load('runtime_s12/core_f4cd0d53_run01/RETURN.json');core_dir=BASE/'runtime_s12/core_f4cd0d53_run01'
    check('core_scoped_269_count_and_binary',core['status']=='PASS_SCOPED' and core['check_count']==core['passed']==len(core['checks'])==269
          and all(c['pass'] for c in core['checks']) and core['binary_sha256']==build['binaries']['s12-core']['sha256']
          and core['source_commit']==build['source_commit'] and not core['NCP_executed'] and core['completed_campaign_replays']==0)
    core_process_errors={p['tag']:process(p) for p in core['processes'] if process(p)}
    check('core_all28_process_raw_logs',len(core['processes'])==28 and not core_process_errors,errors=core_process_errors,
          actual_exit_counts={str(code):sum(p['exit_code']==code for p in core['processes']) for code in sorted({p['exit_code'] for p in core['processes']})})
    fixed=load(core_dir/'FIXED_INPUT.json')
    check('core_24_fixed_queries',len(fixed['queries'])==24,cohorts=len(fixed['bank']['cohorts']))
    perf=load(core_dir/'PERFORMANCE.json');ratios=[];perf_ok=True
    for p in perf['all_pairs']:
        for arm in ['baseline','fused']:
            timing=load(core_dir/(f"bench_{p['pair']:02d}_{arm}.stderr"))
            perf_ok &= timing==p[arm] and timing['queries']==24 and timing['repeat']==2000 and timing['timed_evaluations']==48000
        ratio=p['baseline']['elapsed_ns']/p['fused']['elapsed_ns'];perf_ok &= ratio==p['speedup']
        if not p['warmup']:ratios.append(ratio)
    check('core_fixed_workload_paired_timing_from_raw',perf_ok and len(ratios)==perf['paired_samples']==7 and perf['warmup_pairs']==2
          and statistics.median(ratios)==perf['paired_speedup_median'],median=perf['paired_speedup_median'],q25=perf['paired_speedup_q25'],q75=perf['paired_speedup_q75'],scope=perf['scope'])

    history_dir=BASE/'runtime_s12/history_r2_run02';hm=load(history_dir/'ARTIFACT_MANIFEST.json');summary=load(history_dir/'SUMMARY.json')
    declared={r['path'] for r in hm['files']};actual={p.relative_to(history_dir).as_posix() for p in history_dir.rglob('*') if p.is_file()}
    check('history_complete125_raw_manifest',len(declared)==125 and actual==declared|{'ARTIFACT_MANIFEST.json'} and not hashes(history_dir,hm['files']),manifest_self_excluded=True)
    executions=load(history_dir/'EXECUTIONS.json');reused=[p for p in executions if p['kind']=='REUSED'];new=[p for p in executions if p['kind']!='REUSED']
    check('history_72checks_5reuse_11new',summary['checks_passed']==summary['checks_total']==72 and all(c['pass'] for c in load(history_dir/'CHECKS.json'))
          and len(reused)==summary['reused_completed_histories']==5 and len(new)==summary['new_process_attempts']==11
          and len(executions)==summary['process_records']==16 and summary['source_commit']==build['source_commit']
          and summary['binary_sha256']==build['binaries']['s12-history']['sha256']
          and summary['validation_source_commit']=='4e3615dd75ff1a1efc2792edb3ba5b702a8a9b06',scope=summary['scope'])
    reuse_ok=True
    for r in reused:
        reuse_ok &= r['execution_performed'] is False and r['current_assessor_full_pass'] and not process(r['original_execution'])
        reuse_ok &= sha(Path(r['origin_run'])/'ARTIFACT_MANIFEST.json')==r['origin_manifest_sha256']
        for row in r['copied_files']:
            reuse_ok &= sha(Path(r['origin_run'])/row['origin'])==row['source_sha256']==row['copied_sha256']==sha(history_dir/row['copy'])
    check('history_exact_reused_prefix_no_rerun',reuse_ok and load(history_dir/'REUSED_PREFIX.json')['fallback_rerun_allowed'] is False)
    check('history_11new_raw_process_receipts',all(p['exit_code']==0 and p['status']=='EXITED' and not process(p) for p in new),
          kinds={kind:sum(p['kind']==kind for p in new) for kind in sorted({p['kind'] for p in new})})
    ident=load(history_dir/'RUN_IDENTITY.json')
    check('history_validator_source_and_binary_roles',all(sha(UNIT/name)==digest for name,digest in ident['source_file_sha256'].items())
          and sha(ident['binary_path'])==ident['binary_sha256'] and ident['source_commit']==build['source_commit'],
          Rust_source_commit=ident['source_commit'],validator_source_commit=ident['validation_source_commit'])
    fd=load(history_dir/'FD_RICHARDSON.json');targets=fd['output_times'];raw_derivatives=[]
    for step,tag in zip(fd['steps'],['1p0em04','5p0em05','2p5em05']):
        arms=[]
        for suffix in ['plus','minus']:
            h=load(history_dir/(f'fd_{tag}_{suffix}.stdout'));indexed={r['x']:r['state'][:3] for r in h['observations']};arms.append([indexed[t] for t in targets])
        raw_derivatives.append([[(a-b)/(2*step) for a,b in zip(plus,minus)] for plus,minus in zip(*arms)])
    rich=[[ (4*f-c)/3 for f,c in zip(fine,coarse)] for fine,coarse in zip(raw_derivatives[2],raw_derivatives[1])]
    maxerr=max(abs(a-b) for r,t in zip(rich,fd['full_tangent']) for a,b in zip(r,t))
    check('paired_FD_and_Richardson_rederived_from_stored_outputs',raw_derivatives==fd['raw_centered_derivatives'] and rich==fd['fine_Richardson'] and maxerr==fd['fine_Richardson_max_absolute'],
          max_absolute=maxerr,ODE_or_history_reexecution=0)
    controls=load(history_dir/'OMISSION_CONTROLS.json')
    check('omission_failures_not_scientific_passes',len(controls)==3 and all(c['identified'] and not c['full_scientific_pass'] and not c['internal_numerical_gates_pass'] and c['omitted_vs_Richardson_max_absolute']>c['required_strict_lower_bound'] for c in controls),
          controls=[{k:c[k] for k in ['control','omitted_vs_Richardson_max_absolute','required_strict_lower_bound']} for c in controls])
    checkpoint=load(history_dir/'primary_final.checkpoint.json');checkpoint_id=load(history_dir/'FINAL_CHECKPOINT_IDENTITY.json')
    restored=load(history_dir/'final_checkpoint_resume.stdout');original=load(history_dir/'p24_y0_full.stdout')
    check('final_checkpoint_binding_exact_only',sha(history_dir/'primary_final.checkpoint.json')==checkpoint_id['checkpoint_sha256']
          and checkpoint['payload_sha256']==checkpoint_id['payload_sha256'] and checkpoint['payload']['binding']==checkpoint_id['binding']
          and restored['binding']==original['binding'] and checkpoint_id['next_segment']==5 and checkpoint_id['pending_event'] is None,
          scope='Final checkpoint serialization/restore only; no interrupted-mid-history resume claim.')

    parallel_dir=BASE/'runtime_s12/case_parallel_094971e5_run02/bench';parallel=load(parallel_dir/'RETURN.json');pb=load(parallel_dir.parent/'BINDING.json')
    case_manifest_path=UNIT/'ncp/inputs/core_packs/CASES.json';cases=load(case_manifest_path)
    parallel_ok=True;identity={};case_processes=0
    for pair in parallel['pairs']:
        for arm in ['serial','parallel']:
            for index in range(4):
                p=parallel_dir/f"pair{pair['pair']:02d}_{arm}"/f'case{index:02d}';rec=load(p/'PROCESS.json');data=raw(p/'stdout.txt')
                inp=raw(p/'input.txt');case_processes+=1
                parallel_ok &= rec['status']=='EXITED' and rec['exit_code']==0 and rec['stdout_sha256']==hashlib.sha256(data).hexdigest()
                parallel_ok &= rec['stderr_sha256']==sha(p/'stderr.json') and rec['input_sha256']==hashlib.sha256(inp).hexdigest()==cases['cases'][index]['sha256']
                parallel_ok &= rec['binary_sha256']==parallel['binary_sha256']==build['binaries']['s12-core']['sha256']
                parallel_ok &= identity.setdefault(index,data)==data
    check('C7_32_case_children_full_scientific_byte_identity',parallel_ok and case_processes==32 and parallel['profile']=='sandbox' and parallel['requested_workers']==2
          and parallel['cases']==4 and parallel['repeat']==128 and parallel['measured_pairs']==3 and parallel['warmup_pairs']==1
          and parallel['source_commit']==build['source_commit'] and sha(case_manifest_path)==parallel['cases_manifest_sha256']==pb['case_manifest_sha256'],
          median=parallel['speedup_median'],q25=parallel['speedup_q25'],q75=parallel['speedup_q75'],scope=parallel['scope'])

    support=load('runtime_s12/support_be773dbf_run01/result/RETURN_SUPPORT_PREFLIGHT.json');facets_ok=True;facet_count=0
    for cert in support['certificates']:
        mus=[struct.unpack('>d',bytes.fromhex(v))[0] for v in cert['mu_bits']];z=sorted(set(F.from_float(mu)**2 for mu in mus))
        facets_ok &= F(cert['z_min']['exact'])==z[0] and F(cert['z_max']['exact'])==z[-1] and len(z)==cert['distinct_z']
        for fac in cert['facets']+[cert['simple_zmax_certificate']]:
            a,b,c=map(F,fac['polynomial']);A=a+b/3+c/5;B=2*b/3+4*c/7;C=8*c/35
            upper=A+F(support['gate_exact'])*(abs(A)+abs(B)+abs(C));facet_count+=1
            facets_ok &= all(a+b*v+c*v*v>=0 for v in z) and A==F(fac['target_slack']['exact']) and upper==F(fac['maximum_under_existing_gates']['exact'])
            facets_ok &= (upper<0)==fac['infeasible_at_existing_gates']
    check('stored_support_exact_rational_certificates',facets_ok and len(support['certificates'])==16 and support['first_infeasible_at_existing_gate']==13,
          births=16,facets_checked=facet_count,first_infeasible_birth=13,original_owner=support['owner_commit'],
          scope='Fixed archived binary64 support and unchanged norm/P2/P4 gates only; no projector, native history, or continuum claim.')
    check('support_source_and_nonexecution_claims',not hashes(REPO,support['source_binding']['files'])
          and all(support[key]==0 for key in ['geometry_calls','compiler_calls','projector_calls','ODE_calls','native_history_calls','old_campaign_calls'])
          and not any(support[key] for key in ['native_history_completion_inferred','continuum_or_full_spectral_claim','old_physical_weights_mutated','new_projected_weights_produced']))

    infra1=load('runtime_s12/infrastructure_f4cd0d53/run01/RETURN_INFRASTRUCTURE.json');infra2=load('runtime_s12/infrastructure_4e3615dd/run02/RETURN_INFRASTRUCTURE.json')
    check('infrastructure_original_failure_and_R2_success_separate',infra1['tests_run']==14 and infra1['failures']==2 and infra1['status']=='FAIL_OR_INCOMPLETE'
          and infra2['tests_run']==14 and infra2['failures']==0 and infra2['status']=='PASS_14_INFRA_CONTROLS' and infra2['source_bytes_unchanged_after'],
          review_independence='Infrastructure authored/executed by this auditor; this check is provenance reconciliation, not a new independent functional test.')
    native=[]
    for name in ['f4cd0d53_r1','f4cd0d53_r2','4e3615dd_r3','be773dbf_r4']:
        n=load(BASE/'bass_s12_intake/native_compile'/name/'RETURN_NATIVE_FOLLOWUP.json');native.append({'attempt':name,'status':n['status'],'failure':n.get('failure'), 'command_count':len(n.get('commands',[])), 'source_commit':n['source_commit']})
    check('native_failed_preflight_compile_attempts_preserved',all(n['status']=='FAILED' for n in native),attempts=native,
          note='No native full history success inferred; root may publish a later distinct compile-only repair receipt.')

    backups=[];backup_ok=True
    for name in ['stage1','stage2','stage2_repair','stage3_inputs','stage3_support']:
        stage=BASE/'bass_delivery_s12'/name;p=load(stage/'PACKAGE_RECEIPT.json');r=load(stage/'DROPBOX_FULL_READBACK.json');remote=raw(stage/'DROPBOX_REMOTE_BYTES.zip')
        backup_ok &= len(remote)==p['bytes']==r['bytes'] and hashlib.sha256(remote).hexdigest()==p['sha256']==r['sha256']
        archive=p.get('archive',p.get('local_path'));archive_name=p.get('name',p.get('filename'))
        remote_id=r.get('file_id') or r.get('remote_id') or r.get('remote',{}).get('id')
        backup_ok &= sha(archive)==p['sha256'] and ('PASS' in r['status']) and bool(remote_id)
        with zipfile.ZipFile(stage/'DROPBOX_REMOTE_BYTES.zip') as z:
            m=json.loads(z.read('MANIFEST.json'));backup_ok &= z.testzip() is None and len(m['files'])==p['payload_count']
        backups.append({'stage':name,'archive':archive_name,'bytes':p['bytes'],'sha256':p['sha256'],'payload_count':p['payload_count'],'Dropbox_ID':remote_id,'remote_readback_receipt_sha256':sha(stage/'DROPBOX_FULL_READBACK.json'),'Drive':'NO_NEW_CONFIRMED_S12_COPY'})
    check('five_new_Dropbox_archives_reconcile_full_readback_receipts',backup_ok and len(backups)==5,archives=backups,
          total_archive_bytes=sum(p['bytes'] for p in backups),payloads_with_duplicates=sum(p['payload_count'] for p in backups),
          fresh_remote_GETs_during_this_audit=0,old_S10_9ZIP_completion_reused=True,new_Drive_completion_claim=False)
except Exception as error:
    checks.append({'name':'AUDIT_COMPLETED_WITHOUT_UNHANDLED_READ_OR_FORMAT_FAILURE','pass':False,'error':{'type':type(error).__name__,'message':str(error)}})

record={'schema':'BASS_S12_C9_RAW_PROVENANCE_AUDIT_V1','reviewed_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
        'status':'PASS_SCOPED_RAW_PROVENANCE' if all(c['pass'] for c in checks) else 'FAIL_OR_INCOMPLETE_REVIEW',
        'passed':sum(c['pass'] for c in checks),'check_count':len(checks),'checks':checks,
        'read_only_scope':'Hash/JSON/ZIP and exact algebra on stored results only. No solver, projector, ODE, benchmark, build, historical campaign or NCP execution.',
        'new_scientific_processes':0,'new_cloud_mutations':0,'new_remote_GETs':0,
        'pending_not_approved':['C8 new bounded verification remains unexecuted until publication.','Actual NCP64/128 execution remains NOT_RUN.','Actual MD14 native Einstein/shear shared-Q and evolving reactive full finite-bin physical history remain unclosed.','Fixed b9_n64 all16-birth positive P24 history is blocked by archived support infeasibility from birth13.'],
        'input_file_count':len(evidence),'input_files':evidence,
        'audit_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'prior_audit_reader_failure_preserved':{'receipt':'bass_s12_intake/c9_raw_provenance/RAW_PROVENANCE_AUDIT.json','sha256':'ac11c31583943f9f6f6d2670ca0db65e77a0e32ce64b86d73ed0953fdc894b5b','failure':'Reader expected uniform archive/file_id fields; C1 uses local_path/remote_id, C2 uses remote.id. Adapter repair only, no evidence/source mutation or science rerun.'}}
(OUT/'RAW_PROVENANCE_AUDIT.json').write_text(json.dumps(record,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
print(json.dumps({k:record[k] for k in ['status','passed','check_count','input_file_count']},indent=2))
print(json.dumps([c for c in checks if not c['pass']],ensure_ascii=False,indent=2))
