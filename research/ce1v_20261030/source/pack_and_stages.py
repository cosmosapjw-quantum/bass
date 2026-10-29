#!/usr/bin/env python3
"""CE1-V durable bounded checkpoint factory. Does not perform provider uploads."""
import hashlib,json,zipfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STAMP=(2026,10,30,8,0,0)

def digest(b):return hashlib.sha256(b).hexdigest()
def zipit(path,files,meta=True):
    files=sorted(set(files))
    manifest={'schema':'bass.ce1v.payload_sha256.v1','members':{}}
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
        for p in files:
            p=Path(p)
            if not p.is_file():raise FileNotFoundError(p)
            rel=p.relative_to(ROOT).as_posix()
            b=p.read_bytes();manifest['members'][rel]=digest(b)
            zi=zipfile.ZipInfo(rel,STAMP);zi.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(zi,b,compress_type=zipfile.ZIP_DEFLATED,compresslevel=7)
        if meta:
            zi=zipfile.ZipInfo('MANIFEST_SHA256.json',STAMP);zi.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(zi,json.dumps(manifest,indent=2,sort_keys=True).encode()+b'\n',compress_type=zipfile.ZIP_DEFLATED,compresslevel=7)
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        obj=json.loads(z.read('MANIFEST_SHA256.json'))
        assert len(obj['members'])==len(files)
        assert all(digest(z.read(n))==s for n,s in obj['members'].items())
    return {'name':path.name,'bytes':path.stat().st_size,'sha256':digest(path.read_bytes()),'members':len(files)+1,'payload_sha_verified':len(files)}

def stages():
    desc={
      'R1':('completed_scoped','frozen source/observable target and original DAG authority',['THEORY_R_KO.md','inputs/SOURCE_CONTRACT.json']),
      'R2':('completed_scoped','read original CE1-U coupled histories, cited Bianchi I and harmonic source literature',['THEORY_R_KO.md','inputs/SOURCE_CONTRACT.json']),
      'R3':('completed_scoped','distinguished deterministic cross-power and stochastic covariance; fixed tetrad',['THEORY_R_KO.md']),
      'R4':('completed_scoped','constructed K2, K4, fractional contrast and rotational xi definition',['THEORY_R_KO.md']),
      'R5':('completed_scoped','proved Gram PSD/diagonal, Cauchy, symmetry, parity ranks and time derivative',['THEORY_R_KO.md','evidence/WOLFRAM_CHECK.json']),
      'R6':('NOT_RUN_DISTINCT_AUTHOR','native independent author verification not available; same-context checks are not independent',['THEORY_R_KO.md']),
      'R7':('completed_scoped','CAS Gram identity and independent SciPy original six-cell projection',['evidence/WOLFRAM_CHECK.json','evidence/pytest.log']),
      'R8':('completed_scoped','bounded interpreted result not CMB/ensemble/sky interval proof',['THEORY_R_KO.md','REPORT_KO.md']),
      'R9':('completed_scoped','matched kinetic moments, harmonics, derivative formulas and code',['THEORY_R_KO.md','source/build_crosstime.py']),
      'R10':('completed_scoped','scientific report and resume handoff',['REPORT_KO.md','REPRODUCE.md']),
      'C1':('completed_scoped','exact parent coupled binary64 CSV identities',['inputs/SOURCE_CONTRACT.json','source/build_crosstime.py']),
      'C2':('completed_scoped','map physical E/Eprime, a_lm and da_lm into code',['source/build_crosstime.py']),
      'C3':('completed_scoped','41x41 Gram kernel, 181-angle gamma Legendre projection',['source/build_crosstime.py']),
      'C4':('completed_scoped','bounded two channels and input/result SHA checkpoints',['source/build_crosstime.py','REPRODUCE.md']),
      'C5':('completed_scoped','3362 actual source-locked time-pair rows and 608522 angle samples',['data/GL6_two_time_1681.csv','data/GL8_two_time_1681.csv','data/RESULTS.json']),
      'C6':('completed_scoped','18 implemented and executed scoped tests; compileall',['evidence/pytest.log','tests/test_two_time_physics.py']),
      'C7':('completed_scoped','independent original six-cell SciPy harmonics, E/P quadrupole, parity and positivity',['tests/test_two_time_physics.py','data/RESULTS.json']),
      'C8':('completed_scoped','GL6 vs GL8 empirical angular accuracy, 5-point time derivative, kernel PSD',['data/RESULTS.json','tests/test_two_time_physics.py']),
      'C9':('NOT_RUN_DISTINCT_AUTHOR','native independent reviewer unavailable, no invented receipt',['evidence/pytest.log']),
      'C10':('completed_scoped','reproduction archive and publication handoff (receipt separate)',['REPORT_KO.md','REPRODUCE.md'])}
    root=ROOT/'stage_checkpoints';root.mkdir(exist_ok=True)
    all_=[]
    for phase in ('R','C'):
        for i in range(1,11):
            sid=f'{phase}{i}';status,description,evidence=desc[sid]
            state={'schema':'bass.ce1v.stage.v1','stage':sid,'status':status,'description':description,
                   'evidence_files':evidence,'upper_dag_completed':9,'upper_dag_total':15,'upper_edges':21,
                   'ce1':'PARTIAL','parent_pr':264,'parent_head':'15bb9fd015570c1562a4a7b9102f25a8481796f5',
                   'source_identity':'022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035',
                   'backup_note':'Local stage ZIP in packages; consult independent provider acknowledgements in DELIVERY_RECEIPTS.json, not this source-stage claim',
                   'publication_note':'Stage JSON committed to child Draft when remote receipt verified'}
            (root/f'{sid}.json').write_text(json.dumps(state,indent=2,ensure_ascii=False)+'\n')
            all_.append(state)
    ledger={'schema':'bass.ce1v.stage_ledger.v1','date':'2026-10-30','upper_dag':'9/15',
            'upper_edges':21,'ce1':'PARTIAL','scoped_completed':18,'scoped_total':20,
            'R6':'NOT_RUN_DISTINCT_AUTHOR','C9':'NOT_RUN_DISTINCT_AUTHOR','native_subagent':'NOT_EXPOSED',
            'production_ready':False,'merge_ready':False,'auto_next':False,'stages':all_}
    (ROOT/'STAGE_LEDGER.json').write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n')
    (ROOT/'DAG_DELTA.json').write_text(json.dumps({'schema':'bass.ce1v.dag_delta.v1',
       'source_upper_dag':'9/15','current_upper_dag':'9/15','upper_edges':21,'ce1':'PARTIAL',
       'new_physical_data':'3362 GL6/GL8 proper-time pair rows; 608522 l<=4 rotational angle samples',
       'new_observable':'deterministic energy sky two-time K_l and fractional SO3-averaged xi_l<=4',
       'new_top_level_node_closed':False,
       'scoped_completed':'18/20','R6':'NOT_RUN_DISTINCT_AUTHOR','C9':'NOT_RUN_DISTINCT_AUTHOR',
       'production_ready':False,'merge_ready':False,'auto_next':False},indent=2)+'\n')
    return all_

def run():
    stages()
    P=ROOT/'packages';P.mkdir(exist_ok=True)
    all_=[]
    for phase in 'RC':
        for i in range(1,11):
            a=ROOT/'stage_checkpoints'/f'{phase}{i}.json'
            files=[a,ROOT/'inputs'/'SOURCE_CONTRACT.json',ROOT/'DAG_DELTA.json']
            item=zipit(P/f'CE1V_STAGE_{phase}{i}_20261030.zip',files)
            all_.append(item)
    (ROOT/'evidence'/'STAGE_PACKAGE_MANIFEST.json').write_text(json.dumps(all_,indent=2)+'\n')
    stage_R=list((ROOT/'stage_checkpoints').glob('R*.json'))
    stage_C=list((ROOT/'stage_checkpoints').glob('C*.json'))
    S0=[ROOT/x for x in ('THEORY_R_KO.md','inputs/SOURCE_CONTRACT.json','DAG_DELTA.json','evidence/WOLFRAM_CHECK.json')]+stage_R
    S1=[ROOT/x for x in ('THEORY_R_KO.md','REPORT_KO.md','REPRODUCE.md','DAG_DELTA.json','STAGE_LEDGER.json','inputs/SOURCE_CONTRACT.json',
        'inputs/GL6_coupled_41epochs.csv','inputs/GL8_coupled_41epochs.csv',
        'source/build_crosstime.py','source/plot_crosstime.py','tests/test_two_time_physics.py',
        'data/RESULTS.json','data/GL6_two_time_1681.csv','data/GL8_two_time_1681.csv',
        'data/GL6_two_time_rotation_average.npz','data/GL8_two_time_rotation_average.npz',
        'evidence/pytest.log','evidence/model_stdout.log','evidence/WOLFRAM_CHECK.json',
        'figures/GL8_r2_two_time.png','figures/GL8_r4_two_time.png','figures/GL8_fractional_sky_drift.png')]+stage_C
    r0=zipit(P/'BASS_CE1V_S0_THEORY_20261030.zip',S0)
    r1=zipit(P/'BASS_CE1V_S1_PHYSICS_20261030.zip',S1+[P/'BASS_CE1V_S0_THEORY_20261030.zip'])
    (ROOT/'evidence'/'MILESTONE_MANIFEST.json').write_text(json.dumps([r0,r1],indent=2)+'\n')
    return [r0,r1]
if __name__=='__main__':
    print(json.dumps(run(),indent=2))
