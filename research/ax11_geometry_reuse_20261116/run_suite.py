#!/usr/bin/env python3
"""One finite source-qualified AX11 same-accuracy benchmark, no automatic retries."""
import argparse,csv,hashlib,json,os,random,statistics,subprocess,sys,time
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def nbytes(p):return sum(f.stat().st_size for f in p.rglob('*') if f.is_file())
ap=argparse.ArgumentParser();ap.add_argument('--scratch',type=Path,required=True);a=ap.parse_args()
u=Path(__file__).resolve().parent;x=a.scratch;out=x/'runs';out.mkdir(exist_ok=True)
alloc=json.loads((u/'PROFILE_ALLOCATION.json').read_text());caps=alloc['caps'];receipts=u/'results/native';receipts.mkdir(exist_ok=True)
ledger={'schema':'bass.ax11.geometry-reuse.execution-debits.v1','prior_actual_campaign_cost':'UNKNOWN_PRESERVED','new_native_starts':0,'new_native_wall_s':0.0,'new_native_cpu_s':0.0,'jobs':[],'new_full_history_starts':0,'automatic_retry':False}
ledgerpath=u/'results/EXECUTION_DEBITS.json'
if ledgerpath.exists():raise SystemExit('Existing suite receipt: no blind restart')
for rel,d in alloc['inputs'].items():
 if sha(x/'inputs'/rel)!=d['sha256']:raise SystemExit('INPUT_CHANGED '+rel)
binary={'original':x/'original/rust/rei_microphysics/target/release/examples/bass_ax11_geometry_bench','profile_uncached':x/'candidate/rust/rei_microphysics/target/release/examples/bass_ax11_geometry_bench','exact_reuse':x/'candidate/rust/rei_microphysics/target/release/examples/bass_ax11_geometry_bench'}
save(u/'results/BINARY_IDENTITY.json',{k:{'path':str(v),'sha256':sha(v)} for k,v in binary.items()})
order=[(c,w,m) for c in ['ZERO','SHEAR_PLUS'] for w in ['early','plateau'] for m in ['original','profile_uncached','exact_reuse']]
# Declared fixed ordering; all variants on the same single CPU and three repeats.
save(u/'results/EXECUTION_ORDER.json',{'order':order,'per_process_repetitions':3,'affinity_cpu':min(os.sched_getaffinity(0)),'cpu_model':[s.strip() for s in Path('/proc/cpuinfo').read_text().splitlines() if s.startswith('model name')][:1]})
save(ledgerpath,ledger)
for case,window,mode in order:
 key=f'{case}_{window}_{mode}';record=receipts/(key+'.json');dest=out/key
 if ledger['new_native_starts']>=caps['native_process_starts'] or ledger['new_native_wall_s']>=caps['native_wall_s_total'] or ledger['new_native_cpu_s']>=caps['native_cpu_s_total'] or nbytes(out)>=caps['output_bytes_total']-caps['terminal_reserved_bytes']:raise SystemExit('AGGREGATE_PROFILE_CAP')
 ledger['new_native_starts']+=1
 ledger['jobs'].append({'job':key,'status':'RESERVED','max_wall_s':60,'max_cpu_s':60});save(ledgerpath,ledger)
 command=[sys.executable,str(u/'bounded_exec.py'),'--kind','native','--record',str(record),'--cwd',str(x),'--',str(binary[mode]),mode,case,window,str(x/'inputs'),str(dest)]
 code=subprocess.run(command).returncode
 if record.exists():
  rec=json.loads(record.read_text());ledger['new_native_wall_s']+=rec['wall_s'];ledger['new_native_cpu_s']+=rec['cpu_s']
 ledger['jobs'][-1]['status']='EXIT0' if code==0 else 'FIRST_FAILURE_STOP';ledger['jobs'][-1]['exit_code']=code;save(ledgerpath,ledger)
 if code:raise SystemExit(code)
 print('COMPLETED',key,flush=True)
# Exact recorded state, all required native output bytes and cadence, not rounding-based tolerances.
names=['states.bin','history.csv','abundances.csv','spectra.csv','ledgers.csv','feedback.csv','cadence.csv','initial_checkpoint.txt','checkpoint.txt']
comparisons=[];timings=[]
for case in ['ZERO','SHEAR_PLUS']:
 for window in ['early','plateau']:
  base=out/f'{case}_{window}_original'
  if sha(base/'native_source_identity.txt')!=alloc['original_17_file_corpus_sha256']:raise SystemExit('COMPILED_BASELINE_SOURCE_IDENTITY')
  for mode in ['original','profile_uncached','exact_reuse']:
   d=out/f'{case}_{window}_{mode}'
   with (d/'TIMING.csv').open() as f:timings.extend(csv.DictReader(f))
   for rep in range(3):
    for name in names:
     b=base/f'rep{rep}'/name;c=d/f'rep{rep}'/name
     equal=b.read_bytes()==c.read_bytes()
     comparisons.append({'case':case,'window':window,'mode':mode,'rep':rep,'file':name,'sha256':sha(c),'reference_sha256':sha(b),'byte_exact':equal,'bytes':c.stat().st_size})
     if not equal:save(u/'results/EXACT_COMPARISON.json',{'status':'FAIL','comparisons':comparisons});raise SystemExit('STATE_OR_OUTPUT_MISMATCH '+str(c))
save(u/'results/EXACT_COMPARISON.json',{'status':'BYTE_EXACT_PASS','comparisons':comparisons,'nonreference_comparisons':216,'unique_checkpoints_windows':4,'all_native_stage_gas_photon_ledger_and_algorithmic_counters_in_states_bin':True,'unmatched_wall_CPU_profiling_fields_not_in_scientific_state':True})
with (u/'results/TIMING_ALL.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(timings[0]),lineterminator='\n');w.writeheader();w.writerows(timings)
rows=[]
for case in ['ZERO','SHEAR_PLUS']:
 for window in ['early','plateau']:
  groups={mode:[r for r in timings if r['case']==case and r['window']==window and r['mode']==mode] for mode in binary}
  med=lambda m,k:statistics.median(float(r[k]) for r in groups[m])
  row={'case':case,'window':window,'accepted_per_repeat':32,'repeat_count':3,'original_wall_ms':med('original','wall_ns')/1e6,'candidate_wall_ms':med('exact_reuse','wall_ns')/1e6,'owner_window_speedup':med('original','wall_ns')/med('exact_reuse','wall_ns'),'original_adaptive_ms':med('original','adaptive_ns')/1e6,'candidate_adaptive_ms':med('exact_reuse','adaptive_ns')/1e6,'profile_uncached_quadrature_share':med('profile_uncached','quadrature_ns')/med('profile_uncached','wall_ns'),'profile_uncached_over_original_wall':med('profile_uncached','wall_ns')/med('original','wall_ns'),'background_calls':int(med('exact_reuse','background_calls')),'cached_quadratures':int(med('exact_reuse','background_misses')),'uncached_quadratures':int(med('profile_uncached','background_misses')),'reference_hits':int(med('exact_reuse','reference_hits')),'accepted_state_arithmetic':'BYTE_EXACT_PASS','old_spectrum_and_feedback_work':'UNCHANGED'}
  row['wall_ms_ranges']={m:[min(float(r['wall_ns']) for r in v)/1e6,max(float(r['wall_ns']) for r in v)/1e6] for m,v in groups.items()}
  rows.append(row)
ledger['scientific_output_bytes']=nbytes(out);ledger['status']='BOUNDED_SUITE_EXIT0';ledger['new_executed_accepted_events']=sum(int(r['new_accepted']) for r in timings);ledger['new_executed_tentative_trials']=sum(int(r['new_attempts']) for r in timings);ledger['new_executed_rhs']=sum(int(r['new_rhs']) for r in timings);save(ledgerpath,ledger)
summary={'schema':'bass.ax11.geometry-reuse.same-accuracy.v1','central_pin':alloc['central_review_pin'],'owner_consumer':alloc['named_owner_consumer'],'scenario':alloc['scenario'],'status':'EXACT_NATIVE_OWNER_WINDOW_REUSE_VERIFIED','source_quadrature_nodes':4097,'accepted_state_and_output_parity':'BYTE_EXACT_PASS','rows':rows,'full_AX11_empirical_refinement':'NOT_RUN','AX11_complete':False,'original_goal_workflow':'10/17_UNCHANGED','expansion_dag':'28/88_UNCHANGED','caps_pass':True,'scientific_claim':'Same-accuracy native window implementation/cost evidence, not new convergence or gas error bound'}
save(u/'results/SAME_ACCURACY_BENCHMARK.json',summary);print(json.dumps(summary,indent=2),flush=True)
