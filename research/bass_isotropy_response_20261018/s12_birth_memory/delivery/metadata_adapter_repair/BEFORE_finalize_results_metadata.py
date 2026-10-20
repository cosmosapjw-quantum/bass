#!/usr/bin/env python3
"""Read stored S12 receipts and write delivery metadata; no scientific execution."""
from pathlib import Path
import argparse, copy, datetime, hashlib, json, shutil

BASE = Path(__file__).resolve().parents[1]
REPO = BASE/'bass_work'
LANE = REPO/'research/bass_isotropy_response_20261018'
UNIT = LANE/'s12_birth_memory'
SCI = 'f4cd0d53760783e6a58c3b0a98c64311ca489d28'
SCI_TREE = 'a9048818707ef3f446528631c3b5d6c8171116cc'
VAL = '4e3615dd75ff1a1efc2792edb3ba5b702a8a9b06'
C8 = '8247645d04695bdbfa48eb2fe74757dacf7d2636'
SUPPORT = 'be773dbf36bbe74b42e89e51c61dcd56ef2e6687'
OWNER = '0e25846433170d0f420c4cda44a0bedbf02cd177'
STAGES = ['stage1','stage2','stage2_repair','stage3_inputs','stage3_support','stage4_c8_source']

def read(path):
    return json.loads(Path(path).read_bytes())

def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')

def identity(path):
    path=Path(path); raw=path.read_bytes()
    return {'path':str(path.relative_to(LANE)), 'bytes':len(raw), 'sha256':hashlib.sha256(raw).hexdigest()}

def copy_tree(source, target):
    source=Path(source);target=Path(target)
    for f in source.rglob('*'):
        if f.is_file() and '__pycache__' not in f.parts and f.suffix!='.pyc':
            d=target/f.relative_to(source);d.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(f,d);assert f.read_bytes()==d.read_bytes()

def cloud_index(stages):
    rows=[]
    for stage in stages:
        root=BASE/'bass_delivery_s12'/stage
        receipt=root/'DROPBOX_FULL_READBACK.json'
        r=read(receipt)
        assert r['status'].startswith('PASS_FULL_REMOTE_BYTES')
        target=UNIT/'delivery'/stage;target.mkdir(parents=True,exist_ok=True)
        for name in ['DROPBOX_FULL_READBACK.json','GIT_READBACK.json','HEAD_READBACK.json','COMMENT_READBACK.json','PACKAGE_RECEIPT.json']:
            if (root/name).exists():shutil.copy2(root/name,target/name)
        rows.append({'stage':stage,'archive_name':r.get('archive_name',r.get('filename')),
            'bytes':r['bytes'],'sha256':r['sha256'],'dropbox_file_id':r.get('file_id',r.get('remote_id')),
            'publication_commit':r.get('source_commit',r.get('publication_commit')),
            'publication_tree':r.get('source_tree',r.get('publication_tree')),
            'payload_count':r['payload_count'],'zip_entries':r.get('zip_entries',r.get('archive_entry_count')),
            'Dropbox':'PASS_FULL_REMOTE_BYTES_SHA256_PROVIDERHASH_CRC_MANIFEST_GIT',
            'Drive':'PENDING_NOT_UPLOADED_NO_NEW_WRITE','readback':identity(target/'DROPBOX_FULL_READBACK.json')})
    return {'schema':'BASS_S12_CLOUD_CHECKPOINT_INDEX_V1','verified_stages':rows,
        'verified_zip_count':len(rows),'verified_total_bytes':sum(x['bytes']for x in rows),
        'verified_payload_count_including_duplicates':sum(x['payload_count']for x in rows),
        'Drive_status':'NEW_S11_S12_DELIVERY_PENDING_UNKNOWN_PREVIOUS_SERVER_OUTCOME',
        'Drive_new_writes_authorized_here':False,
        'completed_original_S10':'9ZIP4399983bytes383payload and finalJSON verified on both providers; unchanged',
        'final_containing_metadata_archive':'External postcommit final delivery JSON/comment owns its exact identity and finite readback; no self-referential hash'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--result-commit');p.add_argument('--result-tree');p.add_argument('--closeout',action='store_true');args=p.parse_args()
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    vroot=BASE/'runtime_s12/c8_verify_8247645d_run01'
    v=read(vroot/'RETURN_C8_VERIFICATION.json')
    assert v['status']=='PASS_BOUNDED_C8_CONTROLS' and v['passed']==v['check_count']
    copy_tree(vroot,UNIT/'evidence/c8_launcher_run01')
    for candidate in [BASE/'runtime_s12/c8_verify_8247645d_run01_receipts',BASE/'runtime_s12/c8_verify_8247645d_run01_outer',BASE/'runtime_s12/c8_verify_8247645d_run01_control']:
        if candidate.exists():copy_tree(candidate,UNIT/'evidence'/candidate.name)
    c=read(UNIT/'evidence/core_run01/RETURN.json'); h=read(UNIT/'evidence/history_run02/SUMMARY.json')
    f=read(UNIT/'evidence/history_run02/FD_RICHARDSON.json'); x=read(UNIT/'evidence/history_run02/CROSS_IMPLEMENTATION.json')
    perf=read(UNIT/'evidence/core_run01/PERFORMANCE.json'); par=read(UNIT/'evidence/case_parallel_run02/bench/RETURN.json')
    ag=read(UNIT/'evidence/c8_aggregate_run01/RETURN_VERIFY_AGGREGATE.json')
    native=read(UNIT/'evidence/native_compile/8247645d_r5/RETURN_NATIVE_FOLLOWUP.json')
    guard=read(UNIT/'evidence/native_compile/8247645d_guard_r1/RETURN_NATIVE_FOLLOWUP.json')
    assert c['passed']==269 and h['checks_passed']==72 and ag['checks_passed']==62
    assert native['status']=='COMPILED_NOT_EXECUTED' and guard['status']=='BLOCKED_KNOWN_FIXED_SUPPORT_INFEASIBLE'
    roles={'scientific_source':SCI,'scientific_tree':SCI_TREE,'verification_source':VAL,'static_input_publication':'094971e58d1dac98b8625f6178385d55cad73a81',
        'stored_support_observer_source':SUPPORT,'C8_delivery_source':C8,'C8_delivery_tree':'47d90048b2fe96f05a32711209b7d52bc2c7eee1','original_REI_owner':OWNER,
        'result_commit':args.result_commit or 'identified by external postcommit result receipt',
        'result_tree':args.result_tree or 'identified by external postcommit result receipt',
        'containing_metadata_commit':'actual Git HEAD and final PR174 postcommit comment; never equate to executed scientific source'}
    remaining=[
        {'id':'actual_MD14_and_native_shared_Q','status':'OPEN','scope':'Actual donor normalization, paired event physical input and native Einstein/shear shared-Q closure; PR175 components are reusable, not physical completion.'},
        {'id':'evolving_reactive_full_finite_bin_spectral_history','status':'OPEN'},
        {'id':'P6_and_broader_finite_d_angular_higher_moments','status':'S11_ALGORITHM_SCOPED_COMPLETE_BROADER_PHYSICS_OPEN','preserve':'P6 support infeasibility and registered49point1.54913989382294 worsening; no continuum guarantee.'},
        {'id':'new_Rust_full_birth_memory_parameter_tangent','status':'S12_SHORT_MANUFACTURED_PASS_SCOPED_EXTENDED_NCP_NOT_RUN','scope':'Fixed event coordinates and donor amplitudes; actual native/reactive, moving event and donor-normalization tangent remain outside approval.'},
        {'id':'S8_INNER_P2_PRECISION_LIMIT_and_fixed_native_history','status':'BIRTH11_POINTWISE_REPAIR_REUSED_FULL16BIRTH_BLOCKED_FROM_BIRTH13','scope':'Original failure preserved; exact unchanged-support impossibility at existing gates. New future-birth support needs a separate physical contract.'}]
    metrics={'core_checks':{'passed':c['passed'],'total':c['check_count']},'history_checks':{'passed':h['checks_passed'],'total':h['checks_total']},
        'history_recovery':{'reused':5,'new_R2_processes':11,'R2_logical_records':16,'total_distinct_Rust_history_processes':14,'Python_reference_processes':2,'final_restore_processes':1},
        'fine_Richardson_max_absolute':f['fine_Richardson_max_absolute'],'raw_fine_FD_scaled':f['raw_fine_max_scaled'],
        'Python_Rust_scaled':x['Python_Rust_scaled'],'MF6_clock7_scaled':x['MF6_clock7_scaled'],'baseline_fused_history_scaled':x['baseline_fused_scaled'],
        'fused_paired_speedup_median':perf['paired_speedup_median'],'fused_paired_speedup_IQR':[perf['paired_speedup_q25'],perf['paired_speedup_q75']],
        'case_parallel_paired_speedup_median':par['speedup_median'],'case_parallel_paired_speedup_IQR':[par['speedup_q25'],par['speedup_q75']],
        'case_parallel_scientific_byte_identity_outputs':32,'case_parallel_actual_workers':2,'case_parallel_actual_packs':4,
        'infrastructure_R2':'14/14 PASS; first12/14 retained','C8_launcher_controls':{'passed':v['passed'],'total':v['check_count'],'actual_child_processes':v['actual_process_count'],'scope':'Two version probes plus forbidden-profile Python invocation. Synthetic capacity fixtures are not hardware evidence.'},
        'C8_aggregate_controls':{'passed':ag['checks_passed'],'total':ag['checks_total'],'scope':'Stored SHORT data arithmetic/input controls only; full production receipt chain false.'},
        'native_compile_only':{'status':native['status'],'elapsed_seconds':native['elapsed_seconds'],'binary_sha256':native['compiled_sha256']['native_followup'],'native_histories':0},
        'native_guard':{'status':guard['status'],'exit_code':guard['wrapper_exit_code'],'commands':len(guard['commands']),'downloads':len(guard['downloads']),'native_histories':0}}
    review={'physics':'585/585 PASS_SCOPED','stored_support':'565/565 PASS_SCOPED','figure':'79/79 PASS_SCOPED','raw_provenance':'23/23 groups,664 file identities; pre-C8-execution cutoff','results_document':'31/31 initial document review; final status addendum separately read',
        'C8_static':'No blocking finding in final launcher and aggregate; not full NCP execution approval','do_not_sum_overlapping_check_counts':True,'independence':'Per-report author/reviewer boundaries retained. Root independently reviews p6 support observer/native guard; p6 reviews root Rust/figure; cloud provenance excludes own launcher approval.'}
    sources=[UNIT/'evidence/core_run01/RETURN.json',UNIT/'evidence/history_run02/SUMMARY.json',UNIT/'evidence/history_run02/FD_RICHARDSON.json',UNIT/'evidence/history_run02/CROSS_IMPLEMENTATION.json',UNIT/'evidence/history_run02/OMISSION_CONTROLS.json',UNIT/'evidence/core_run01/PERFORMANCE.json',UNIT/'evidence/case_parallel_run02/bench/RETURN.json',UNIT/'evidence/c8_launcher_run01/RETURN_C8_VERIFICATION.json',UNIT/'evidence/c8_aggregate_run01/RETURN_VERIFY_AGGREGATE.json',UNIT/'evidence/native_compile/8247645d_r5/RETURN_NATIVE_FOLLOWUP.json',UNIT/'evidence/native_compile/8247645d_guard_r1/RETURN_NATIVE_FOLLOWUP.json',UNIT/'evidence/support_run01/result/RETURN_SUPPORT_PREFLIGHT.json']
    ledger={'schema':'BASS_S12_RESULT_LEDGER_V1','written_utc':now,'status':'PASS_SCOPED_NEW_S12_RESEARCH_NCP_NOT_RUN_DRIVE_PENDING','source_roles':roles,'metrics':metrics,'independent_reviews':review,
        'fixed_support_result':{'birth0_to12':'STRICT_INTERIOR','birth13_to15':'OUTSIDE_AT_EXISTING_GATE','birth13_Z':0.5908471918238073,'necessary_Z':'3/5','gate_exact':'3/1000000000000000','weights_modified':False,'native_history_calls':0},
        'execution_bounds':{'sandbox_user_workers_max':16,'sandbox_user_ram_GiB_max':16,'observed_cpu_cap':8,'observed_ram_GiB_cap':8,'disk_GiB_max':4,'individual_job_seconds_max':1800,'actual_NCP_executions':0,'completed_campaign_replays':0,'automatic_next_unit_started':False},
        'NCP_prepared':{'fixed_jobs':17,'extended_histories':14,'fixed_case_packs':64,'fixed_input_files':81,'actual_status':'NOT_RUN_SERVICE_MONTHLY_QUOTA','hardware_currently_observed':False,'full_positive_launcher_and_production_ensemble_chain':'NOT_RUN'},
        'remaining_obligations':remaining,'evidence':[identity(p)for p in sources],
        'preserved_prior_results':['S9fixed8','S10targeted11/11 kernel108/108 RAW24/24 science68/68 C9155/155','closed2.973x FLRW4.115x fixedworkload only','closed-small uncertainty','changingn16/cohort2 0.9498173837599284 regression','S11P246 finite-grid worsening1.54913989382294'],
        'source_deposition_scope':'5.369926725506957e-12 remains limited source deposition; not full spectral-history convergence','production_or_full_EoR_or_merge':False}
    write(UNIT/'RESULT_LEDGER.json',ledger)
    stages=STAGES+(['stage5_results'] if args.closeout else [])
    ci=cloud_index(stages);write(UNIT/'delivery/CLOUD_CHECKPOINT_INDEX.json',ci)
    status='GIT_DROPBOX_PRIOR_STAGES_VERIFIED_FINAL_METADATA_READBACK_EXTERNAL_DRIVE_PENDING' if args.closeout else 'RESULTS_READY_FOR_PUBLICATION_C10_IN_PROGRESS'
    policy='S12 executed Rust source f4, verifier4e36, observerbe773 and delivery824 are separate identities. Result commit is identified by its postcommit receipt. The containing final metadata commit/tree and its finite last ZIP/JSON are identified by the external final PR174 comment and full readback; no self-reference. S10 dual-provider delivery remains complete. New Drive is pending; NCP is NOT_RUN.'
    for filename in ['DAG.json','RETURN_TO_CHATGPT.json','PUBLICATION_CLOSEOUT.json']:
        path=LANE/filename;j=read(path)
        historical_keys=['stage','publication','source_commit','source_tree','scientific_work','current_result_summary','current_physics_result_summary','current_delivery_index','active_metadata_publication_policy','next_first_action','remaining_obligations','NCP','limits','source_identity_policy','resume_head']
        if 'historical_S11_active_fields_before_S12' not in j:j['historical_S11_active_fields_before_S12']={k:copy.deepcopy(j[k])for k in historical_keys if k in j}
        j.update(date_utc=now,stage='S12_SCOPED_RESEARCH_COMPLETE_NCP_NOT_RUN_NEW_DRIVE_PENDING',active_unit='S12',current_result_summary='s12_birth_memory/RESULT_LEDGER.json',current_physics_result_summary='s12_birth_memory/RESULT_LEDGER.json',current_delivery_index='s12_birth_memory/delivery/CLOUD_CHECKPOINT_INDEX.json',active_metadata_publication_policy=policy,source_identity_policy=policy,remaining_obligations=remaining,
            NCP={'status':'NOT_RUN_SERVICE_MONTHLY_QUOTA','requested_cpu_cores':64,'requested_ram_GiB':128,'current_hardware_observed':False,'remote_process_calls':0,'retry_or_reconnect_after_explicit_quota_notice':False,'ready_jobs':17,'old_NCP_campaign':'2026-10-15 complete; not backlog'},
            current_S12_science=ledger,production_admission=False,auto_merge=False)
        j['limits']={'sandbox':{'additional_workers_max':16,'RAM_GiB_max':16,'actual_CPU_cap':8,'actual_RAM_GiB_cap':8},'NCP_requested':{'workers_max':64,'RAM_GiB_max':128,'respect_observed_resources_and_owner_load':True},'disk_GiB_max':4,'individual_job_seconds_max':1800}
        j['next_first_action']='Read actual Git HEAD/latest PR comments and exact Dropbox/Drive delivery records read-only. Reuse completed evidence. Do not request user chats, attachments, downloads or precommands. Do not replay old campaigns or fixed native16birth; continue only already authorized ready S12 NCP jobs if valid service access is independently available, otherwise preserve NOT_RUN and stop automatic new loops.'
        j['publication']={'status':status,'source_roles':roles,'prior_stage_Dropbox':ci['verified_zip_count'],'new_Drive':'PENDING_UNKNOWN_SERVER_OUTCOME_NO_MORE_WRITES','final_delivery_identity_owner':'Postcommit final PR174 comment and exact final JSON, external to containing commit'}
        if filename=='PUBLICATION_CLOSEOUT.json':j.update(source_commit=SCI,source_tree=SCI_TREE,scientific_work='New Rust full birth-memory short manufactured histories and fixed-workload optimization PASS_SCOPED; stored original native support proves later birth13 obstruction; no actual NCP/native reactive convergence approval.')
        if filename=='DAG.json':
            s=j['S12'];s.update(status='SCOPED_RESEARCH_COMPLETE_C10_DRIVE_PENDING_NCP_NOT_RUN',source_roles=roles,C8_observed=metrics['C8_launcher_controls'],C8_aggregate_observed=metrics['C8_aggregate_controls'],C9=review,C10=ci)
            s['stages'].update(C8='PREPARED_AND_BOUNDED_CONTROLS_PASS_ACTUAL_NCP_NOT_RUN',C9='PASS_SCOPED_INDEPENDENT_REVIEWS',C10=status)
            s['C8_prepared']['limited_verification']='PASS_BOUNDED_ONLY';s['C8_prepared']['full_positive_launch_chain']='NOT_RUN'
            s['C6_observed']['native_compile_attempts'].extend([])
            s['native_compile_final']=metrics['native_compile_only'];s['native_guard_final']=metrics['native_guard'];s['stage_delivery']['C8_SOURCE']={'publication':C8,'Dropbox':'s12_birth_memory/delivery/stage4_c8_source/DROPBOX_FULL_READBACK.json','Drive':'PENDING_NO_NEW_WRITE'}
            s['dropbox_delivery']=str(ci['verified_zip_count'])+'ZIP_FULL_BYTES_SHA_CRC_MANIFEST_GIT_PASS';j['resume_head']=args.result_commit or C8;j['resume_head_role']='Latest completed checkpoint known inside this metadata; actual containing HEAD is verified externally after commit.'
        write(path,j)
    write(UNIT/'delivery/C10_DECISION.json',{'schema':'BASS_S12_C10_DECISION_V1','utc':now,'source_roles':roles,'status':status,'Git':'source and result chain, final current ref readback after commit','Dropbox':ci,'Drive':'pending; no object ID or successful response for new delivery; do not retry or bypass','NCP':'NOT_RUN quota; do not claim current64/128 hardware','scientific_reruns_for_delivery':0,'final_policy':policy,'next_automatic_research_unit':False})
    print(json.dumps({'status':status,'core':c['passed'],'history':h['checks_passed'],'C8_launcher':v['passed'],'C8_aggregate':ag['checks_passed'],'Dropbox_zips':ci['verified_zip_count'],'Dropbox_bytes':ci['verified_total_bytes']}))

if __name__=='__main__':main()
