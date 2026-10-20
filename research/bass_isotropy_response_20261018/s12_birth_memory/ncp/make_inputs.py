#!/usr/bin/env python3
"""Materialize fixed NEW inputs in the sandbox; NCP consumes static JSON/text.

No solver, campaign, benchmark, or projector is called. Whole-core packs reuse
the already verified fixture byte-for-byte except the registered x offsets.
Extended histories retain fixed donor/event and old-stock contracts.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import reference as ref
from process_control import atomic_json


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fixture',type=Path,required=True);p.add_argument('--fixture-sha256',required=True)
    p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    raw=args.fixture.read_bytes()
    if sha(raw)!=args.fixture_sha256:raise ValueError('VERIFIED_CORE_FIXTURE_SHA')
    fixture=json.loads(raw);bank,queries=fixture['bank'],fixture['queries']
    if len(queries)!=24 or len(bank['cohorts'])!=2 or sum(len(c['mu']) for c in bank['cohorts'])!=48:
        raise ValueError('FIXED_CORE_WORKLOAD_SHAPE')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);packs=[]
    (out/'core_packs').mkdir()
    for i in range(64):
        q=deepcopy(queries)
        for row in q:row['x']+=i*1e-4
        data=ref.core_protocol(bank,q).encode();path=out/'core_packs'/f'pack{i:02d}.txt';path.write_bytes(data)
        packs.append({'path':path.name,'sha256':sha(data),'bytes':len(data),'x_offset':i*1e-4})
    atomic_json(out/'core_packs/CASES.json',{'schema':'BASS_S12_FIXED_CORE_PACKS_V1',
        'fixture_sha256':args.fixture_sha256,'cases':packs,'scientific_generation_calls':0,
        'physical_bank_changed':False,'ray_cohort_reduction_order_changed':False})
    histories={
        'p24_y0_full':ref.history_input(extended=True),
        'gl_y0_full':ref.history_input(rule='source_frame_GL',extended=True),
        'gl_b0_gauge':ref.history_input(rule='source_frame_GL',parameter='b0',extended=True),
        'p24_y0_mf6':ref.history_input(arm='mf_into_ls6',extended=True),
        'p24_y0_baseline':ref.history_input(mode='baseline',extended=True)}
    primary=histories['p24_y0_full']
    fd=[]
    for h in [1e-4,5e-5,2.5e-5]:
        ids=[]
        for sign,label in [(1,'plus'),(-1,'minus')]:
            inp=deepcopy(primary);inp['config']['y0']+=sign*h
            name='fd_'+format(h,'.1e').replace('.','p').replace('-','m')+'_'+label
            histories[name]=inp;ids.append(name)
        fd.append({'step':h,'plus':ids[0],'minus':ids[1]})
    for control in ['omit_birth_memory','omit_mu_b','omit_alpha_b']:
        histories[control]=ref.history_input(control=control,extended=True)
    rows=[]
    for name,inp in histories.items():
        path=out/'histories'/(name+'.json');atomic_json(path,inp);data=path.read_bytes()
        rows.append({'id':name,'path':str(path.relative_to(out)),'bytes':len(data),'sha256':sha(data),
            'control':inp['control'],'parameter':inp['parameter'],'birth_rule':inp['birth_rule'],
            'solver_arm':inp['solver']['arm']})
    atomic_json(out/'HISTORIES.json',{'schema':'BASS_S12_EXTENDED_FIXED_HISTORIES_V1','cases':rows,'fd_pairs':fd,
        'primary':'p24_y0_full','fixed_config':primary['config'],'output_times':primary['output_times'],
        'completed_campaign_replays':0,'solver_calls_during_generation':0,'old_stock_changes':0,
        'native_case_separate':'b9_n64_P2P4; original incomplete case only; no completed17-case replay'})
    atomic_json(out/'GENERATION.json',{'schema':'BASS_S12_FIXED_INPUT_GENERATION_V1',
        'core_fixture_sha256':args.fixture_sha256,'core_packs':64,'new_extended_histories':len(rows),
        'solver_calls':0,'projector_calls':0,'benchmark_calls':0,'old_stock_reweighted':False,
        'generator_source_sha256':sha(Path(__file__).read_bytes()),
        'reference_source_sha256':sha((Path(__file__).resolve().parents[1]/'reference.py').read_bytes())})
    print(json.dumps({'core_packs':64,'new_extended_histories':len(rows),'solver_calls':0}))


if __name__=='__main__':main()
