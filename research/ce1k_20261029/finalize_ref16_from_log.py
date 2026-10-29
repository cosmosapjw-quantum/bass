"""Reassemble completed fresh MPFR panel cap output after result-writer typo.
No new MPFR science run; previous source SHA and path SHA checked in captured log.
"""
from pathlib import Path
import zipfile, json, re
from bianchi.nonperturbative.einstein_interval import Interval
base=Path(__file__).parent
rows=[];source_id=path_id=None;box=None;ms=None
for line in (base/'REF16_SOURCE_ONLY.log').read_text().splitlines():
 if line.startswith('SHA_MATCH '):
  _,source_id,path_id=line.split()
 elif line.startswith('PROVEN_GEOMETRY '):
  parts=line.split(' LOWERS ')
  import ast
  box=ast.literal_eval(parts[0].split('PROVEN_GEOMETRY ')[1]);ms=ast.literal_eval(parts[1])
 elif line.startswith('PANEL '):
  _,j,raw,scaled,eta,src=line.split()
  rows.append({'j':int(j),'m':ms[int(j)] if ms else None,'raw_bound':float(raw),'scaled_bound':float(scaled),'adopted_eta':float(eta),'source_h_cumulative':float(src)})
assert len(rows)==4 and source_id and path_id and box is not None and len(ms)==4
z=zipfile.ZipFile('/mnt/data/BASS_CE1J_S2_FINAL_20261029_c25092d1.zip')
a=json.loads(z.read('research/ce1j_20261029/evidence/S2_REF16_PARTITIONED.json'))
assert source_id==a['source_id'] and path_id==a['path_id']
assert ms==a['m_panel']
assert rows[0]['adopted_eta']==3.569278983301304e-5
assert all(rows[j]['adopted_eta']<=rows[j-1]['adopted_eta'] for j in range(1,4))
initial=a['local']['initial_h'];time=a['local']['time_jump_h'];src=rows[-1]['source_h_cumulative']
h_total=sum((Interval(x) for x in (initial,time,src)),Interval(0)).upper
result={'schema':'bass.ce1k.current_run.ref16_source_only_reassembled.v1','source_id':source_id,'path_id':path_id,'geometry_box':box,'proven_panel_m':ms,'panels':rows,'fresh_MPFR_source_h_upper':src,'inherited_SHA_verified_initial_h_upper':initial,'inherited_SHA_verified_time_jump_h_upper':time,'ce1k_total_h_upper':h_total,'canonical_ce1i_total':a['local']['total_h'],'donor_ce1j_total':3.0184081966517434e-6,'target':1e-5,'target_met':h_total<1e-5,'full_panel_residual_this_run':'REUSED_SHA_VERIFIED_FROM_PR246','MPFR_source_caps_this_run':'FRESH','result_assembly':'REPLAY_FROM_CURRENT_TURN_CAPTURED_MPFR_LOG_AFTER_SCRIPT_WRITER_EXCEPTION','upper_dag':'9/15','production_ready':False,'distinct_author_R6_C9':'NOT_RUN'}
(base/'REF16_SOURCE_ONLY.json').write_text(json.dumps(result,indent=2))
print('PASS_REASSEMBLED',json.dumps({'h_total':h_total,'source':src,'initial':initial,'time':time,'target_met':h_total<1e-5}))