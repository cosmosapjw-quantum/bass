#!/usr/bin/env python3
"""Read-only numerical/statistical assessment of frozen S10 raw outputs.

No integration, rerun, adaptive sampling or tolerance change. Original S9
observer is reused explicitly for release science gates; C9 supplies a separate
review and independent recomputation of statistics rather than trusting this file.
"""
import argparse,hashlib,importlib.util,json,math,statistics,struct
from pathlib import Path

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]
def quant(v,p):
 s=sorted(v);pos=(len(s)-1)*p;i=int(pos);f=pos-i
 return s[i]*(1-f)+s[min(i+1,len(s)-1)]*f
def stats(v):
 assert v and all(math.isfinite(x) and x>0 for x in v)
 return {'n':len(v),'median':statistics.median(v),'q1':quant(v,.25),'q3':quant(v,.75),'iqr':quant(v,.75)-quant(v,.25),'min':min(v),'max':max(v),'values':v}
def exact_object(v,top=True):
 if isinstance(v,float):return ('f64',struct.pack('>d',v).hex())
 if isinstance(v,dict):return tuple((k,exact_object(x,False)) for k,x in sorted(v.items()) if not (top and k=='elapsed_seconds'))
 if isinstance(v,list):return tuple(exact_object(x,False) for x in v)
 return (type(v).__name__,v)
def pairs(data,keys):
 cells={}
 for row in data:
  cell=tuple(row[k] for k in keys);rounds=cells.setdefault(cell,{})
  rd=rounds.setdefault(row['round'],{});assert row['mode'] not in rd
  rd[row['mode']]=row
 results=[]
 for key,rounds in sorted(cells.items()):
  assert set(rounds)==set(range(7));cand=key[-1];bs=[];cs=[];ratios=[]
  for r in range(7):
   pair=rounds[r];assert set(pair)=={'baseline',cand};b=pair['baseline']['seconds'];c=pair[cand]['seconds']
   bs.append(b);cs.append(c);ratios.append(b/c)
  results.append(dict(zip(keys,key))|{'baseline_seconds':stats(bs),'candidate_seconds':stats(cs),'paired_speedup':stats(ratios),'short_batch_warning':min(statistics.median(bs),statistics.median(cs))<.001})
 return results

def main():
 p=argparse.ArgumentParser();p.add_argument('--lane',type=Path,required=True);p.add_argument('--run',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True);m=a.run/'measurements'
 protocol=read(a.lane/'evidence_s10/c4/BENCHMARK_PROTOCOL.json');cases=[c['name'] for c in protocol['whole_history']['cases']];modes=protocol['modes']
 micro=rows(m/'MICRO_SAMPLES.jsonl');hist=rows(m/'HISTORY_SAMPLES.jsonl');par=rows(m/'PARALLEL_SAMPLES.jsonl');prep=rows(m/'PREPARE_SAMPLES.jsonl');alloc=read(m/'ALLOCATION_PROBE.json');proof=read(m/'MICRO_PROOF.json')
 mt=[x for x in micro if x['kind']=='micro'];ht=[x for x in hist if x['kind']=='history'];pt=[x for x in par if x['kind']=='parallel']
 assert len(mt)==1260 and len(ht)==280 and len(pt)==42 and len(prep)==378 and len(alloc['rows'])==108 and len(proof)==108
 assert all(x['exact'] for x in proof) and all(x['exact'] and x['status']=='completed' for x in ht) and all(x['exact'] and x['all_completed'] for x in pt)
 result={'schema':'BASS_S10_C7_C8_ASSESSMENT_V1','status':'PASS_SCOPED','raw_counts':{'micro_timed':len(mt),'micro_proof':len(proof),'micro_diagnostic':sum(x['kind']=='diagnostic' for x in micro),'history_timed':len(ht),'history_warmup_proof':sum(x['kind']=='warmup_proof' for x in hist),'parallel_timed_batches':len(pt),'parallel_warmup_batches':sum(x['kind']=='parallel_warmup' for x in par),'prepare_timed':len(prep),'allocation_rows':len(alloc['rows'])},'micro':pairs(mt,['n','cohorts','trace','candidate']),'history':pairs(ht,['case','candidate']),'parallel':[],'parallel_scaling':[],'preparation':[],'strict_raw_equivalence':[],'science':[],'stored_S9_comparison':[],'allocation_rows':alloc['rows'],'diagnostics':[x for x in micro if x['kind']=='diagnostic'],'limitations':['Seven fixed paired samples in a shared container, not population confidence or portable speedup.','Preparation includes evaluator construction only; caller bank clone/drop excluded.','Parallel includes local pool construction/teardown and four unequal jobs.','Allocation counts/requested bytes do not measure live bytes, peak RSS, or cost fraction.','Bit identity verified for stated inputs/CPU/compiler, not all finite-d continuum or all native finite-bin histories.','SHORT_BATCH is a descriptive median duration below 1 ms; no extra samples were collected.']}
 for workers in [1,2,4]:
  for mode in ['baseline','simd_cache']:
   rr=sorted([r for r in pt if r['workers']==workers and r['mode']==mode],key=lambda x:x['round']);assert [r['round'] for r in rr]==list(range(7))
   result['parallel'].append({'workers':workers,'mode':mode,'batch_seconds':stats([r['seconds'] for r in rr]),'histories_per_second':stats([4/r['seconds'] for r in rr])})
 for mode in ['baseline','simd_cache']:
  base={r['round']:r['seconds'] for r in pt if r['workers']==1 and r['mode']==mode}
  for workers in [2,4]:
   rr=sorted([r for r in pt if r['workers']==workers and r['mode']==mode],key=lambda x:x['round']);r=[base[x['round']]/x['seconds'] for x in rr]
   result['parallel_scaling'].append({'mode':mode,'workers':workers,'descriptive_round_index_scaling':stats(r),'efficiency':stats([x/workers for x in r]),'adjacent_pairing':False})
 for n in [16,64,256]:
  for k in [2,16,64]:
   for mode in modes:
    rr=[r['seconds'] for r in prep if r['n']==n and r['cohorts']==k and r['mode']==mode];assert len(rr)==7
    result['preparation'].append({'n':n,'cohorts':k,'mode':mode,'seconds':stats(rr),'timer_caution':True})
 spec=importlib.util.spec_from_file_location('bass_s9_observer',a.lane/'s9_vigilode/analyze.py');obs=importlib.util.module_from_spec(spec);spec.loader.exec_module(obs)
 prior=read(a.lane/'s9_vigilode/PREREGISTRATION.json');ref=read(a.lane/'s9_vigilode/reference/S8_PRIMAL.json');case_map={c['name']:c for c in prior['cases']}
 for case in cases:
  baseline=read(m/(case+'_baseline.json'));fixed=exact_object(baseline)
  for mode in modes:
   raw=read(m/(case+'_'+mode+'.json'));equal=exact_object(raw)==fixed
   result['strict_raw_equivalence'].append({'case':case,'mode':mode,'full_scientific_f64_bits_equal':equal,'raw_sha256':sha(m/(case+'_'+mode+'.json'))});assert equal
  assessment=obs.assess(baseline,ref,prior,case_map[case]);assert assessment['all_quality_gates'];result['science'].append(assessment)
  stored=read(a.lane/'evidence_s9/run_20261020_r1'/case/'RAW.json');old={r['x']:r for r in stored['observations']}
  errors=[max(abs(r['state'][i]-old[r['x']]['state'][i]) for r in baseline['observations']) for i in range(3)]
  result['stored_S9_comparison'].append({'case':case,'max_abs_state_difference':errors,'canonical_f64_full_receipt_equal':exact_object(stored)==fixed,'gate_scope':'new release compared to S8/analytic FLRW under original gates; debug/release bits not assumed'})
 result['science_gate_decisions']=sum(len(r['quality_gates']) for r in result['science'])
 result['science_gate_passes']=sum(sum(r['quality_gates'].values()) for r in result['science'])
 result['raw_source_manifest']=[{'path':str(p.relative_to(a.run)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(m.iterdir()) if p.is_file()]
 result['analysis_source_sha256']=sha(Path(__file__));result['protocol_sha256']=sha(a.lane/'evidence_s10/c4/BENCHMARK_PROTOCOL.json')
 (a.output/'S10_ASSESSMENT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
 overview={'status':result['status'],'counts':result['raw_counts'],'science_gates':[result['science_gate_passes'],result['science_gate_decisions']],'history_speedups':[{'case':r['case'],'candidate':r['candidate'],'median_ratio':r['paired_speedup']['median'],'q1':r['paired_speedup']['q1'],'q3':r['paired_speedup']['q3'],'baseline_ms':r['baseline_seconds']['median']*1000,'candidate_ms':r['candidate_seconds']['median']*1000} for r in result['history']],'parallel':[{'workers':r['workers'],'mode':r['mode'],'median_batch_ms':r['batch_seconds']['median']*1000,'median_histories_s':r['histories_per_second']['median']} for r in result['parallel']]}
 (a.output/'OVERVIEW.json').write_text(json.dumps(overview,ensure_ascii=False,indent=2)+'\n');print(json.dumps(overview,ensure_ascii=False))
if __name__=='__main__':main()
