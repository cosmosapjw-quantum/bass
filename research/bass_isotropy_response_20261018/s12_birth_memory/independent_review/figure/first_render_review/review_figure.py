#!/usr/bin/env python3
"""Independent check of already stored figure data; no scientific execution."""
from pathlib import Path
import csv
import datetime as dt
from fractions import Fraction
import hashlib
import json
import statistics

ROOT=Path('/workspace/scratch/14e1021f8231')
UNIT=ROOT/'bass_work/research/bass_isotropy_response_20261018/s12_birth_memory'
FIG=UNIT/'evidence/figure'
checks=[]
def check(name, passed, **detail):
    checks.append(dict(name=name,passed=bool(passed),**detail))
def read(name): return json.loads((UNIT/name).read_bytes())
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def quantile(a,q):
    a=sorted(a); at=(len(a)-1)*q; lo=int(at)
    return a[lo]+(at-lo)*(a[min(lo+1,len(a)-1)]-a[lo])
def maxdiff(a,b): return max(abs(x-y) for aa,bb in zip(a,b) for x,y in zip(aa,bb))

m=json.loads((FIG/'FIGURE_MANIFEST.json').read_bytes())
for row in m['inputs']:
    p=UNIT/row['path'];check('input_sha:'+row['path'],digest(p)==row['sha256'])
for row in m['artifacts']:
    p=FIG/row['path'];check('artifact_bytes:'+row['path'],p.stat().st_size==row['bytes']);check('artifact_sha:'+row['path'],digest(p)==row['sha256'])
check('manifest_excludes_self',all(r['path']!='FIGURE_MANIFEST.json' for r in m['artifacts']))
check('script_sha',digest(UNIT/'make_figure.py')==m['script_sha256'])
check('manifest_no_science',m['new_science_or_benchmark_calls']==0)
rows=list(csv.DictReader((FIG/'S12_PLOT_DATA.csv').open()))
check('30_rows',len(rows)==m['rows']==30)
core=read('evidence/core_run01/PERFORMANCE.json')
batch=read('evidence/case_parallel_run02/bench/RETURN.json')
fd=read('evidence/history_run02/FD_RICHARDSON.json')
om=read('evidence/history_run02/OMISSION_CONTROLS.json')
su=read('evidence/support_run01/result/RETURN_SUPPORT_PREFLIGHT.json')
a=[p for p in core['all_pairs'] if not p['warmup']]
b=[p for p in batch['pairs'] if not p['warmup']]
check('A_7_measured_2_warmup',len(a)==7 and sum(p['warmup'] for p in core['all_pairs'])==2)
check('B_3_measured_1_warmup',len(b)==3 and sum(p['warmup'] for p in batch['pairs'])==1)
for p in a:
    check('A_ratio:'+str(p['pair']),p['baseline']['elapsed_ns']/p['fused']['elapsed_ns']==p['speedup'])
for p in b:
    check('B_ratio:'+str(p['pair']),p['serial']['wall_s']/p['parallel']['wall_s']==p['speedup'])
for panel,values,data,prefix in [('A',[p['speedup'] for p in a],core,'paired_speedup_'),('B',[p['speedup'] for p in b],batch,'speedup_')]:
    check(panel+'_median',statistics.median(values)==data[prefix+'median'])
    for q,tail in [(.25,'q25'),(.75,'q75')]:
        check(panel+'_'+tail,quantile(values,q)==data[prefix+tail])
check('B_scope',batch['cases']==4 and batch['requested_workers']==2 and batch['profile']=='sandbox')
check('C_full_error_independent',maxdiff(fd['full_tangent'],fd['fine_Richardson'])==fd['fine_Richardson_max_absolute'])
for o in om:
    check('C_omitted_richardson:'+o['control'],maxdiff(o['tangent'],fd['fine_Richardson'])==o['omitted_vs_Richardson_max_absolute'])
    check('C_control_false:'+o['control'],o['full_scientific_pass'] is False and o['internal_numerical_gates_pass'] is False)
check('D_first_outside13',su['first_exact_target_outside']==13 and su['first_infeasible_at_existing_gate']==13)
check('D_fixed_case',su['fixed_configuration_verified']['case_id']=='b9_n64_prior' and su['fixed_configuration_verified']['n_mu']==64)
check('D_gate_exact',Fraction(su['gate_exact'])==Fraction(3,10**15))
check('D_no_native_replay',su['native_history_calls']==su['ODE_calls']==su['compiler_calls']==su['projector_calls']==su['old_campaign_calls']==0)
check('D_no_completion',su['native_history_completion_inferred'] is False and su['continuum_or_full_spectral_claim'] is False)
expected=[]
for panel,vals in [('A',[p['speedup'] for p in a]),('B',[p['speedup'] for p in b])]:
    expected.extend((panel,i,v) for i,v in enumerate(vals,1))
expected.extend(('C',i,v) for i,v in enumerate([fd['fine_Richardson_max_absolute']]+[o['omitted_vs_Richardson_max_absolute'] for o in om]))
expected.extend(('D',c['birth'],float(Fraction(c['z_max']['exact']))) for c in su['certificates'])
for idx,(row,(panel,x,value)) in enumerate(zip(rows,expected)):
    check('CSV_row_'+str(idx),row['panel']==panel and int(row['x'])==x and float(row['value'])==value)
check('D_simple_necessary_Z',all((Fraction(c['z_max']['exact']) < Fraction(3,5))==(c['birth']>=13) for c in su['certificates']))
report={'schema':'BASS_S12_INDEPENDENT_FIGURE_REVIEW_V1','utc':dt.datetime.now(dt.timezone.utc).isoformat(),'reviewer':'c9_review_finish; figure authored by root','status':'PASS_SCOPED' if all(c['passed'] for c in checks) else 'FAIL','passed':sum(c['passed'] for c in checks),'total':len(checks),'checks':checks,'source_sha256':digest(Path(__file__)),'figure_manifest_sha256':digest(FIG/'FIGURE_MANIFEST.json'),'visual_review':{'performed_with':'view_image of actual PNG','pass':True,'observations':['All titles, ticks, legends, and footnotes are readable without clipping or overlap.','NCP64 NOT RUN and exclusions are explicit.','Paired samples, observed IQR (not confidence interval), whole-batch timing scope and warmup counts are explicit.','Panel C uses omitted-vs-fine-Richardson differences, not the slightly different full-vs-omitted diagnostic.','Panel D shows the original fixed native support only; positive Z threshold is necessary, not a sufficiency claim.']},'limitations':['This data/visual review does not rerun a solver, benchmark, CAS, projector, support observer, or completed campaign.','Necessary Z threshold alone does not replace the separately reviewed full polygon certificate.','Existing first-render manifest is valid; make_figure.py must exclude the existing manifest on any later rerender to avoid a stale selfhash.'],'activity_counts':{'compiler_calls':0,'ODE_calls':0,'benchmark_calls':0,'projector_calls':0,'native_history_calls':0,'old_campaign_calls':0},'not_added_to_independent_physics_585_count':True}
(Path(__file__).parent/'FIGURE_REVIEW.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ('status','passed','total')}))
