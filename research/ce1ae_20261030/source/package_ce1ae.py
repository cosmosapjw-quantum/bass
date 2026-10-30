#!/usr/bin/env python3
"""One bounded CE1-AE source-inclusive evidence package with per-stage snapshots."""
from __future__ import annotations
import hashlib,json,zipfile
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'stages';OUT.mkdir(exist_ok=True)
SRC='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
PARENT='f80f03d33a8b98cd49dfb9cda85ae316d868cdf6'
DESCRIPTION={
'R1':'Freeze original six-cell Einstein-Vlasov and bounded CE1-AE objective, top DAG 9/15',
'R2':'Read pinned source, exact CE1AD sampled Gram theorem and primary Heinzle Uggla / Barzegar Fajman Heissel',
'R3':'Trace unweighted dimensionless proper-time kernel vs 41-sampled and CMB distinctions',
'R4':'Construct choices: matrix integral quantitative bound using per-interval errors versus certified global Lipschitz from positivity; select robust positive route',
'R5':'Derive simplex harmonic bound and one-sided Lipschitz finite-sample-to-operator theorem',
'R6':'Same-context hostile check of covariance, coefficient, time extension, and finite quadrature scope (not distinct author)',
'R7':'Execute exact rational witness and actual 6D Einstein-Vlasov dense physical histories GL6/8/16/64',
'R8':'Admit conditional physical >1e-23, distinguish numerical ~1e-13 and observed CMB',
'R9':'Record source-to-physics kernel finite-rank operator map and exact computational contract',
'R10':'Checkpoint proven claim, source hashes, actual new physics and bounded successor without upper DAG promotion',
'C1':'Pin original GH PR281, six positive cell SHA, horizon .08, h goal and parent 41-time spectral theorem',
'C2':'Bind original ray source -> 6D ODE -> sky X -> integral kernel -> numeric Gram and C4 energy',
'C3':'Derive Simpson positive weighted physical integral, 4pt Hermite independent reference, dyadic SPD witness',
'C4':'Choose GL6/8/16/64 401 source time samples, GL6/8 1601 comparisons; isolate original input',
'C5':'Implement runnable physics, conditional continuum certificate, exact dyadic surrogate, plots',
'C6':'Execute physical finite run, compileall and 16 scoped pytest tests',
'C7':'Check Hamiltonian, radiation trace, source positivity, normalized versus raw C4, original 41 replay',
'C8':'Compare GL16 vs GL64 and GL6/8 401 versus 1601 and independent 41 Hermite integral',
'C9':'Self-hostile review, reject interpreting Simpson numerical eigenvalue as rigorous true-operator bound',
'C10':'Source-inclusive zip, CI contract, dual backup, frozen parent and next-scoped handoff'}
FILES=[p for p in BASE.rglob('*') if p.is_file() and not any(x in p.parts for x in ('__pycache__','.pytest_cache','stages','backup')) and not p.name.startswith('.github_placeholder')]
FILES=[p for p in FILES if not p.name.endswith('.pyc')]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def package(filename,paths):
    manifest={str(p.relative_to(BASE)):sha(p) for p in sorted(paths)}
    dst=OUT/filename
    with zipfile.ZipFile(dst,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
        for p in sorted(paths):z.write(p,'ce1ae_20261030/'+str(p.relative_to(BASE)))
        z.writestr('ce1ae_20261030/MANIFEST_SHA256.json',json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    with zipfile.ZipFile(dst) as z:
        assert z.testzip() is None
        for k,h in manifest.items():assert hashlib.sha256(z.read('ce1ae_20261030/'+k)).hexdigest()==h
    return {'file':dst.name,'bytes':dst.stat().st_size,'sha256':sha(dst),'members':len(manifest)}

def main():
    stage=[]
    for i,(name,desc) in enumerate(DESCRIPTION.items()):
        record={'stage':name,'sequence':i+1,'description':desc,'status':'COMPLETED_SCOPED_LOCAL',
          'completed_upper_DAG':'9/15','upper_DAG_edges':21,'CE1':'PARTIAL',
          'original_scoped_R_C':'18/20', 'new_completed_upper_nodes':0,
          'parent_pr':281,'parent_head_sha':PARENT,'source_sha256':SRC,
          'scientific_claim':'CONDITIONAL_True_continuous_integral_lambda3_GT_1e-23',
          'numerical_claim':'GL6/8/16/64 dense time original Einstein-Vlasov 1604 records, continuum integrated G spectrum NUMERICAL_ONLY',
          'proof_source':'THEORY_KO.md','actual_tests':'16 PASS local',
          'R6_C9_distinct_author':'NOT_RUN', 'native_subagent':'NOT_RUN',
          'backup_provider_ack':'NOT_RECORDED_IN_STAGE_SNAPSHOT',
          'production_ready':False,'merge_ready':False,'auto_next':False}
        p=OUT/f'CE1AE_STAGE_{name}.json';p.write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n')
        if name.startswith('R'):
            incl=[BASE/'THEORY_KO.md',p]
            if name=='R6':incl.append(BASE/'BLIND_REFEREE_KO.md')
            if name in ('R5','R7'):incl.append(BASE/'data'/'CONTINUOUS_TIME_STRICT_GAP_WITNESS.json')
        else:
            incl=[BASE/'REPRODUCE.md',p]
            if name in ('C5','C6'):incl.append(BASE/'source'/'continuous_kernel_physics.py')
            if name=='C7':incl.append(BASE/'data'/'CONTINUOUS_TIME_INTEGRATED_PHYSICS.json')
        stage.append(package(f'CE1AE_STAGE_{name}_20261030.zip',incl))
    # Recalculate all source paths now including stage json (zips excluded).
    fs=[p for p in BASE.rglob('*') if p.is_file() and not any(x in p.parts for x in ('__pycache__','.pytest_cache','backup')) and p.suffix not in ('.zip','.pyc') and p.name!='.github_placeholder']
    theory=[p for p in fs if p.name in ('THEORY_KO.md','BLIND_REFEREE_KO.md','CONTINUOUS_TIME_STRICT_GAP_WITNESS.json','CE1AD_SAMPLED_SPECTRAL_GATE.json','cellwise_gl_rust.py','REPRODUCE.md') or '/stages/CE1AE_STAGE_R' in str(p)]
    science=[p for p in fs if p.name not in ('THEORY_KO.md','BLIND_REFEREE_KO.md') and ('/stages/CE1AE_STAGE_C' in str(p) or '/source/' in str(p) or '/data/' in str(p) or '/figures/' in str(p) or '/input/' in str(p))]
    full=[p for p in fs if '/stages/' not in str(p)]
    full += [p for p in fs if '/stages/' in str(p)]
    pack=[package('BASS_CE1AE_S0_THEORY_20261030.zip',theory),package('BASS_CE1AE_S1_NEW_PHYSICS_20261030.zip',science),package('BASS_CE1AE_SOURCE_INCLUSIVE_FULL_20261030.zip',full)]
    receipt={'stage_archives':stage,'s0_s1_full':pack,'upper_DAG':'9/15','CE1':'PARTIAL','authoritative_GitHub_latest_from_parent':PARENT,
             'provider_backup_status':'NOT_YET_UPLOADED; local source-inclusive payloads generated and checked',
             'parent_certified_41_sample_lambda3_gt':'3e-12','new_conditional_continuous_lambda3_gt':'1e-23'}
    (BASE/'PACKAGE_RECEIPTS_LOCAL.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('stage zipped',len(stage),'S0/S1/FULL',json.dumps(pack));return receipt
if __name__=='__main__':main()
