#!/usr/bin/env python3
"""Fail-closed structural validator for the RF-02C V2 execution contract."""
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path

ALLOWED={'state','parameter','const_f64_bits','add','sub','mul','neg'}

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def die(msg:str): raise SystemExit('FAIL: '+msg)
def walk_expr(node,seen):
    if not isinstance(node,dict) or node.get('op') not in ALLOWED: die(f'invalid expression node: {node}')
    op=node['op']; seen.add(op)
    if op=='state':
        if not isinstance(node.get('index'),int) or node['index']<0: die('bad state index')
        return 3
    if op in {'parameter','const_f64_bits'}: return 0
    if op=='neg': return walk_expr(node.get('arg'),seen)
    a=walk_expr(node.get('lhs'),seen); b=walk_expr(node.get('rhs'),seen)
    return a+b if op=='mul' else max(a,b)
def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--contract',type=Path,required=True); ap.add_argument('--v1',type=Path,required=True); ap.add_argument('--output',type=Path,required=True)
    ns=ap.parse_args(); d=json.loads(ns.contract.read_text()); v1=json.loads(ns.v1.read_text())
    if d.get('schema')!='bass-rf02c-execution-semantics/v2': die('wrong schema')
    if d['supersedes']['contract_id']!=v1['contract_id'] or d['supersedes']['sha256']!=sha(ns.v1): die('v1 identity mismatch')
    if d['base']['required_preimplementation_parent_head']!='11c6c7ad58257575cf3ccca482ec6f52c37a0d85': die('wrong parent head')
    lang=d['event_expression_language'];
    registry_bytes=json.dumps(lang['builtin_registry'],sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')
    if hashlib.sha256(registry_bytes).hexdigest()!=lang.get('registry_sha256'): die('event registry hash mismatch')
    if set(lang['closed_ops'])!=ALLOWED: die('closed op set mismatch')
    forbidden=' '.join(lang['forbidden']).lower()
    for token in ('callback','closure','function pointer','arbitrary user event'):
        if token not in forbidden: die(f'missing forbidden token {token}')
    ids=[]; maxdeg=0; seen=set()
    for chart,events in lang['builtin_registry'].items():
        for e in events:
            ids.append((chart,e['id'])); deg=walk_expr(e['expr'],seen); maxdeg=max(maxdeg,deg)
            if deg>lang['degree_ceiling']: die(f'degree ceiling exceeded: {chart} {e["id"]} {deg}')
            if e['id']=='type_ix_recollapse':
                if not (e['segment_terminal'] and not e['trajectory_terminal'] and e['transition_id']=='type_ix_expanding_to_contracting' and e['one_shot_after_transition']): die('recollapse terminal/transition fields incomplete')
    if sum(1 for _,i in ids if i=='type_ix_recollapse')!=1: die('recollapse registry multiplicity')
    dense=d['event_dense_carrier']['dyadic_certification']
    if dense['max_depth']!=24 or dense['accept_subsegment']!='D_y <= 0.25 and every armed D_g <= 0.25': die('carrier certificate drift')
    if 'EVENT_CARRIER_NONFINITE' not in dense.get('nonfinite_rule','') or 'NONADVANCING_ACCEPTED_STEP' not in dense.get('nonadvancing_step',''): die('carrier exceptional cases undefined')
    root=' '.join(d['root_isolation']['algorithm']).lower()
    for token in ('square-free','sturm','tangential','continuum_zero','event_root_representation_failure'):
        if token not in root and token not in json.dumps(d['root_isolation']).lower(): die(f'missing root mechanism {token}')
    dom=d['domain_semantics']
    if 'g_raw=0' not in dom['events'] or 'g_cert>=0' not in dom['projection']: die('raw/certificate split absent')
    if 'first certified carrier subsegment' not in dom.get('epsilon_initial',''): die('epsilon_initial undefined')
    if d['restart']['zero_neighborhood']!='abs(g_raw(y)) <= stored epsilon_g': die('latch zero band drift')
    if 'exact isolation' not in d['restart'].get('evaluation_frequency','') or len(d['restart'].get('within_step_rearm',[]))<5: die('within-step latch rearm undefined')
    order=d['transitions']['atomic_recollapse_order']
    joined=' '.join(order).lower()
    for token in ('root sample exactly once','event record','transition record','without appending a restart-initial sample','completed_at_transition'):
        if token not in joined: die(f'incomplete recollapse order: {token}')
    hist=d['history']
    if hist.get('byte_identity_encoding',{}).get('registry_hash')!='event_expression_language.registry_sha256': die('byte identity encoding incomplete')
    for field in ('segments','samples','events','transitions','initial_phase','final_phase'):
        if field not in hist['top_level_fields']: die(f'history field missing: {field}')
    # Execute the independent exact root oracle from the same directory.
    oracle=ns.contract.parents[2]/'tools/audit/rf02c_event_root_oracle_v2.py'
    if not oracle.is_file():
        # local staging layout
        oracle=Path(__file__).with_name('rf02c_event_root_oracle_v2.py')
    run=subprocess.run(['python',str(oracle),'--self-test'],capture_output=True,text=True)
    if run.returncode: die('root oracle failed: '+run.stdout+run.stderr)
    oreport=json.loads(run.stdout)
    if oreport.get('status')!='PASS': die('root oracle status not PASS')
    report={'schema':'bass-rf02c-semantics-v2-validation/v1','status':'PASS','contract_sha256':sha(ns.contract),'v1_sha256':sha(ns.v1),'builtin_event_count':len(ids),'max_compiled_degree':maxdeg,'expression_ops_observed':sorted(seen),'root_oracle_cases':sorted(oreport['cases'])}
    text=json.dumps(report,indent=2,sort_keys=True)+'\n'; print(text,end=''); ns.output.parent.mkdir(parents=True,exist_ok=True); ns.output.write_text(text)
    return 0
if __name__=='__main__': raise SystemExit(main())
