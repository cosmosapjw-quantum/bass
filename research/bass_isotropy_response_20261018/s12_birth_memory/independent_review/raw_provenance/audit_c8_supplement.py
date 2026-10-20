"""Read only the already completed C8/native/Dropbox evidence; no child work."""
import datetime as dt
import hashlib
import io
import json
from pathlib import Path
import zipfile

ROOT = Path('/workspace/scratch/14e1021f8231')
UNIT = ROOT/'bass_work/research/bass_isotropy_response_20261018/s12_birth_memory'
OUT = ROOT/'bass_s12_intake/c9_c8_supplement_run01'
OUT.mkdir(exist_ok=False)
identities = {}
checks = []

def read(path, *, size=None, sha=None, blob=None):
    path = Path(path)
    data = path.read_bytes()
    got = hashlib.sha256(data).hexdigest()
    git = hashlib.sha1(b'blob '+str(len(data)).encode()+bytes([0])+data).hexdigest()
    if size is not None: assert len(data) == size, str(path)
    if sha is not None: assert got == sha, str(path)
    if blob is not None: assert git == blob, str(path)
    identities[str(path.relative_to(ROOT))] = {'bytes':len(data),'sha256':got,'git_blob':git}
    return data

def load(path, **kw):
    return json.loads(read(path, **kw))

def check(name, **details):
    checks.append({'name':name,'pass':True,**details})

record = {'schema':'BASS_S12_C9_C8_RAW_PROVENANCE_SUPPLEMENT_V1',
    'started_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
    'scope':'Supplement to the immutable 23-group raw audit; this does not rerun any test, compiler, history or cloud transfer.',
    'new_compiler_processes':0,'new_science_processes':0,'new_cloud_requests':0,
    'independent_functional_retest_claim':False,
    'reviewer_note':'Reviewer authored C8 and infrastructure; this is provenance/readback review, not an independent functional implementation test.'}
try:
    basepath=ROOT/'bass_s12_intake/c9_raw_provenance_run02/RAW_PROVENANCE_AUDIT.json'
    base=load(basepath, size=137765, sha='adcacee8db0339aded5f7394a5de627c641cdfc5cebf730b7eedfe24a23591e1')
    assert base['passed']==base['check_count']==23 and base['status']=='PASS_SCOPED_RAW_PROVENANCE'
    check('prior_23_group_report_preserved', prior_report=str(basepath.relative_to(ROOT)), first_reader_failure_also_preserved=True)

    source='8247645d04695bdbfa48eb2fe74757dacf7d2636'
    native=ROOT/'bass_s12_intake/native_compile'
    guarddir=native/'8247645d_guard_r1'
    guard=load(guarddir/'RETURN_NATIVE_FOLLOWUP.json')
    gi=load(native/'8247645d_guard_r1.INDEX.json')
    assert guard['status']=='BLOCKED_KNOWN_FIXED_SUPPORT_INFEASIBLE' and guard['source_commit']==source
    assert guard['commands']==guard['downloads']==[] and guard['native_histories_attempted']==guard['native_histories_executed']==0
    assert guard['fixed_support_guard']['first_infeasible_birth']==13 and guard['fixed_support_guard']['native_history_execution_allowed'] is False
    assert guard['fixed_support_guard']['gate_exact']=='3/1000000000000000'
    for f in gi['files']: read(guarddir/f['path'], size=f['bytes'], sha=f['sha256'])
    certificate=load(UNIT/'evidence/support_run01/result/RETURN_SUPPORT_PREFLIGHT.json',sha=guard['fixed_support_guard']['certificate_sha256'])
    check('native_actual_default_guard_before_any_children', wrapper_exit_code=guard['wrapper_exit_code'], native_histories=0,
          commands=0,downloads=0,first_infeasible_birth=13,certificate_sha256=guard['fixed_support_guard']['certificate_sha256'])

    compile_dir=native/'8247645d_r5'
    compiled=load(compile_dir/'RETURN_NATIVE_FOLLOWUP.json')
    index=load(native/'8247645d_r5.INDEX.json')
    assert compiled['source_commit']==source and compiled['status']=='COMPILED_NOT_EXECUTED'
    assert compiled['wrapper_exit_code']==0 and compiled['native_histories_attempted']==compiled['native_histories_executed']==0
    assert compiled['downloads']==[] and compiled['completed_old_cases_replayed']==0 and len(compiled['commands'])==3
    actual={str(p.relative_to(compile_dir)) for p in compile_dir.rglob('*') if p.is_file()}
    assert actual=={f['path'] for f in index['files']}
    for f in index['files']: read(compile_dir/f['path'],size=f['bytes'],sha=f['sha256'])
    for c in compiled['commands']:
        assert c['status']=='PASS' and c['exit_code']==0
        for stream in ('stdout','stderr'):
            read(compile_dir/c[stream],size=c[stream+'_bytes'],sha=c[stream+'_sha256'])
    assert [c['label'] for c in compiled['commands']]==['compiler_version','compile_pinned_owner','compile_s12_followup']
    assert 'link-arg=-Wl,--threads=1' in compiled['commands'][-1]['argv']
    for name,digest in compiled['compiled_sha256'].items(): read(compile_dir/'build'/name,sha=digest)
    for row in compiled['source_binding']['files']:
        read(UNIT/'native_followup'/row['path'],size=row['bytes'],sha=row['sha256'],blob=row['git_blob'])
    read(UNIT/'native_followup/SOURCE_MANIFEST.json',sha=compiled['source_binding']['manifest_sha256'])
    owner=load(UNIT/'native_followup/native_owner_manifest.json',sha='2cd4d9fdfc49c499f1c99c9373680d7056a4223b0107b10e39d7472756bc8cb2')
    assert owner['commit']=='0e25846433170d0f420c4cda44a0bedbf02cd177' and len(owner['files'])==57
    for row in owner['files']:
        read(native/'4e3615dd_r3/owner_source'/row['path'],size=row['size'],sha=row['sha256'],blob=row['sha'])
    assert sum(row['size'] for row in owner['files'])==614313
    assert compiled['owner_verification_before']==compiled['owner_verification_after']
    check('native_actual_compile_only_raw_bound', source_commit=source,raw_index_files=len(index['files']),raw_index_bytes=index['bytes'],
          compiler_commands=3,native_histories=0,owner_files=57,owner_bytes=614313,
          elapsed_s=compiled['elapsed_seconds'],binary_sha256=compiled['compiled_sha256']['native_followup'],
          child_AS_bytes=compiled['resources_before']['child_address_space_cap_bytes'],peak_child_RSS_KiB=compiled['children_peak_rss_kib_linux'],
          prior_four_failed_attempts_preserved=True,physical_history_success_claim=False)

    c8=ROOT/'runtime_s12/c8_verify_8247645d_run01'
    control=ROOT/'runtime_s12/c8_verify_8247645d_run01_control'
    result=load(c8/'RETURN_C8_VERIFICATION.json',size=7895,sha='6d4308868553ad5fb89bd9be4d23f0c2ad092aafca77d939928741783bd42065')
    outer=load(control/'PROCESS.json')
    assert result['status']=='PASS_BOUNDED_C8_CONTROLS' and result['delivery_source_commit']==source and result['passed']==result['check_count']==19
    assert outer['status']=='EXITED' and outer['exit_code']==0 and outer['limits']['address_space_bytes']==2<<30 and outer['timeout_s']==120
    assert result['actual_process_count']==3 and [x['exit_code'] for x in result['actual_process_records']]==[0,0,2]
    for proc in [outer]+result['actual_process_records']:
        for stream in ('stdout','stderr'): read(proc[stream+'_path'],sha=proc[stream+'_sha256'])
    for directory in (c8,control):
        for f in directory.rglob('*'):
            if f.is_file(): read(f)
    assert all(result[k]==0 for k in ('NCP_executions','builds','scientific_histories','old_campaign_replays','network_requests'))
    assert result['production_positive_full_CLI_claim'] is False and result['synthetic_capacity_is_not_hardware_evidence'] is True
    assert result['checks'][-1]['verified_files']==109
    check('C8_bounded_verification_actual_raws', passed=19,total=19,source_commit=source,actual_child_processes=3,
          actual_child_roles=['rustc version','cargo version','forbidden sandbox profile CLI'],source_union_files=109,
          AS_bytes=2<<30,outer_elapsed_s=outer['elapsed_s'],build_history_network_NCP=0,synthetic64CPU128GiB_is_not_hardware_claim=True,
          full_positive_CLI_resume_executed=False)

    stage=ROOT/'bass_delivery_s12/stage4_c8_source'
    cloud=load(stage/'DROPBOX_FULL_READBACK.json',size=17616,sha='e8a100e4b42b97affa8ed86da7c2707e89aea8f203c2449357f75a73dd0cb604')
    assert cloud['source_commit']==source and cloud['payload_count']==50 and cloud['payload_bytes']==1652768
    archive=read(stage/'DROPBOX_REMOTE_BYTES.zip',size=432014,sha='d97b57d760664e1214ce5556b7802982e0e10c80603b28b8839e7ddcdbc28d67')
    assert read(cloud['archive'])==archive
    provider=hashlib.sha256(b''.join(hashlib.sha256(archive[i:i+4194304]).digest() for i in range(0,len(archive),4194304))).hexdigest()
    assert provider==cloud['provider_content_hash']==cloud['remote']['content_hash']
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        assert z.testzip() is None and len(z.namelist())==52
        manifest=load(stage/'MANIFEST.json');git=load(stage/'GIT_READBACK.json')
        assert z.read('MANIFEST.json')==(stage/'MANIFEST.json').read_bytes() and z.read('GIT_READBACK.json')==(stage/'GIT_READBACK.json').read_bytes()
        assert set(z.namelist())=={f['path'] for f in manifest['files']}|{'MANIFEST.json','GIT_READBACK.json'}
        gitrows={f['path']:f for f in git['files']}
        for f in manifest['files']:
            data=z.read(f['path']);blob=hashlib.sha1(b'blob '+str(len(data)).encode()+bytes([0])+data).hexdigest()
            assert len(data)==f['bytes'] and hashlib.sha256(data).hexdigest()==f['sha256'] and blob==f['git_blob']==gitrows[f['path']]['git_blob']
    assert cloud['drive']['new_stage_write_calls']==0 and cloud['drive']['status']=='PENDING_UNCONFIRMED'
    check('sixth_Dropbox_archive_cached_full_byte_proof',remote_id=cloud['remote_id'],bytes=cloud['bytes'],sha256=cloud['sha256'],
          payloads=50,total_S12_ZIPs=6,total_S12_ZIP_bytes=1316030,total_payloads_with_duplicates=297,
          remote_GETs_during_this_review=0,prior_actual_full_GET=1,Drive_new_stage_writes=0,Drive_full_readback_claim=False)
    record['status']='PASS_SCOPED_SUPPLEMENT'
except BaseException as error:
    record.update(status='FAILED_READ_ONLY_REVIEW',error={'type':type(error).__name__,'message':str(error)})
record.update(finished_utc=dt.datetime.now(dt.timezone.utc).isoformat(),passed=len(checks),check_count=len(checks),checks=checks,
              actual_file_identities=identities,actual_unique_files_read=len(identities),
              unresolved=['Actual NCP run/quota','Positive full C8 CLI and production resume execution','Actual MD14 normalization and native Einstein/shear shared-Q closure','Evolving reactive full finite-bin physical spectral history'])
payload=(json.dumps(record,indent=2,ensure_ascii=False)+'\n').encode()
(OUT/'C9_C8_SUPPLEMENT.json').write_bytes(payload)
print(json.dumps({k:v for k,v in record.items() if k not in ('actual_file_identities','checks')},indent=2))
print('receipt_bytes',len(payload),'sha256',hashlib.sha256(payload).hexdigest())
raise SystemExit(0 if record['status']=='PASS_SCOPED_SUPPLEMENT' else 2)
