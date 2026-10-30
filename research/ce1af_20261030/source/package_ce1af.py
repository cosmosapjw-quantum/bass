#!/usr/bin/env python3
"""Generate CE1-AF typed, source-inclusive archives and bounded stage evidence.

ZIP integrity is not a claim of theorem truth. Restores verifiable source content.
"""
from pathlib import Path
import hashlib,json,zipfile,io
ROOT=Path(__file__).resolve().parents[1]
STAGES=ROOT/'stages';STAGES.mkdir(exist_ok=True)

stage={
'R1':('Physical problem and source contract',['PROVENANCE.json','DAG_DELTA.json']),
'R2':('Original literature and predecessor reuse',['THEORY_KO.md','PROVENANCE.json']),
'R3':('Definition, signs, dimensionless units and exact claim boundary',['THEORY_KO.md','BLIND_REFEREE_KO.md']),
'R4':('Constructed shear work and quadrupole-to-fourth-moment alternative',['THEORY_KO.md']),
'R5':('Exact energy/pressure hierarchy, shear transfer and rational W0 proof',['THEORY_KO.md','source/certify_initial_shear_work.py','data/CE1AF_EXACT_INITIAL_SHEAR_WORK.json']),
'R6':('Same-context hostile audit; distinct-author NOT_RUN',['BLIND_REFEREE_KO.md']),
'R7':('Actually computed 1604 new physical time records',['data/CE1AF_SHEAR_QUADRUPOLE_RESULTS.json']),
'R8':('Bounded scientific claim gate',['REPORT_KO.md','DAG_DELTA.json']),
'R9':('Mathematical theory to exact runnable science mapping',['THEORY_KO.md','REPRODUCE.md']),
'R10':('Backup and next-thread handoff; no auto-successor',['PROVENANCE.json','DAG_DELTA.json']),
'C1':('Frozen source identity and target baseline',['PROVENANCE.json']),
'C2':('Source ODE to E/P/R/alpha2 and data columns',['source/shear_work_physics.py']),
'C3':('Actual positive source quadrature, integrated work and independent checks',['source/shear_work_physics.py','REPRODUCE.md']),
'C4':('Bounded 4×401 physics GL and non-mutating implementation',['REPRODUCE.md','DAG_DELTA.json']),
'C5':('Runnable six-cell Einstein-Vlasov, exact initial moment and physical figure generators',['source/shear_work_physics.py','source/certify_initial_shear_work.py','source/plot_ce1af.py']),
'C6':('Executed tests and compileall source checks',['source/test_ce1af.py','REPORT_KO.md']),
'C7':('Model provenance and physical equations closure',['data/CE1AF_SHEAR_QUADRUPOLE_RESULTS.json','data/CE1AF_EXACT_INITIAL_SHEAR_WORK.json']),
'C8':('GL16/64 comparison and numerical-vs-certified distinction',['REPORT_KO.md','BLIND_REFEREE_KO.md']),
'C9':('Same-context hostile implementation check; distinct-author NOT_RUN',['BLIND_REFEREE_KO.md','source/test_ce1af.py']),
'C10':('Publication readiness hold, local archives and actual resume',['PROVENANCE.json','REPRODUCE.md','DAG_DELTA.json']),
}

def digest(buf):return hashlib.sha256(buf).hexdigest()

def pack(path, paths, extra=None):
    members={f'ce1af_20261030/{q}':(ROOT/q).read_bytes() for q in paths}
    if extra:
        for k,v in extra.items():members[k]=v.encode() if isinstance(v,str) else v
    manifest={'schema':'bass.ce1af.source_inclusive_SHA256.v1','members':{k:digest(v) for k,v in sorted(members.items())}}
    members['CE1AF_ZIP_MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for k in sorted(members):z.writestr(k,members[k])
    return {'archive':path.name,'size':path.stat().st_size,'sha256':digest(path.read_bytes()),'payload_members':len(members)-1}

def build():
    row=[]
    for st,(goal,ref) in stage.items():
        state={'stage':st,'bounded_objective':goal,'upper_DAG':'9/15','upper_edges':21,'CE1':'PARTIAL',
               'original_R_C':'18/20','new_upper_completed_nodes':0,'genuine_independent_author':'NOT_RUN',
               'scientific_status':'SCOPED_SAME_CONTEXT_CHECKED' if st in ('R6','C9') else 'BOUNDED_PHASE_DELIVERED',
               'refs':ref}
        (STAGES/f'CE1AF_{st}.json').write_text(json.dumps(state,indent=2,ensure_ascii=False)+'\n')
        row.append(state)
    (ROOT/'STAGE_LEDGER.json').write_text(json.dumps({'stages':row,'upper_DAG':'9/15','CE1':'PARTIAL','actual_new_upper_nodes':0,'original_scoped_R_C':'18/20'},indent=2,ensure_ascii=False)+'\n')
    receipts=[]
    for st,(goal,refs) in stage.items():
        r=pack(STAGES/f'CE1AF_STAGE_{st}_20261030.zip',refs+[f'stages/CE1AF_{st}.json','STAGE_LEDGER.json'])
        receipts.append(r)
        print('STAGE',st,'9/15',r['size'],r['payload_members'],flush=True)
    s0=['THEORY_KO.md','BLIND_REFEREE_KO.md','REPRODUCE.md','PROVENANCE.json','DAG_DELTA.json','STAGE_LEDGER.json',
        'source/certify_initial_shear_work.py','data/CE1AF_EXACT_INITIAL_SHEAR_WORK.json']
    s1=['data/CE1AF_SHEAR_QUADRUPOLE_RESULTS.json','data/CE1AF_EXACT_INITIAL_SHEAR_WORK.json','data/CE1AF_PHYSICAL_TIMELINE.csv','data/CE1AF_PHYSICAL_TIMELINE.csv.gz',
        'figures/CE1AF_GL64_SHEAR_RADIATION_WORK.png','figures/CE1AF_GL64_VOLUME_COMPENSATED_ENERGY.png','figures/CE1AF_GL64_C2_VS_C4_REAL_PHYSICS.png',
        'REPORT_KO.md','DAG_DELTA.json','REPRODUCE.md']
    original=['input/cellwise_gl_rust.py','input/GL6_DOP853_coupled_41epochs.csv','input/GL8_DOP853_coupled_41epochs.csv','input/CE1AE_PARENT_C4_DENSE.csv.gz']
    code=['source/shear_work_physics.py','source/certify_initial_shear_work.py','source/test_ce1af.py','source/plot_ce1af.py','source/package_ce1af.py']
    docs=['THEORY_KO.md','REPORT_KO.md','BLIND_REFEREE_KO.md','REPRODUCE.md','PROVENANCE.json','DAG_DELTA.json','STAGE_LEDGER.json','.github/workflows/ce1af-physical-shear-quadrupole.yml']
    for name,paths in [('BASS_CE1AF_S0_THEORY_20261030.zip',s0),('BASS_CE1AF_S1_NEW_PHYSICAL_DATA_20261030.zip',s1),('BASS_CE1AF_SOURCE_INCLUSIVE_FULL_20261030.zip',sorted(set(original+code+docs+s1+s0)))]:
        receipts.append(pack(STAGES/name,paths))
    (ROOT/'PACKAGE_RECEIPTS_LOCAL.json').write_text(json.dumps(receipts,indent=2)+'\n')
    for r in receipts[-3:]:print('ARCHIVE',r['archive'],r['size'],r['sha256'],r['payload_members'])
    return receipts
if __name__=='__main__':build()
