"""Build native-input fixtures and *predicted* source-only moment expectations.

Actual BASS FD96 backgrounds plus explicit manufactured angular controls.
No row generated here is a native SourceLedger measurement.
"""
from __future__ import annotations
from dataclasses import replace
from functools import lru_cache
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import time
import numpy as np

from source_oracle import Case,REI_SHA,AREF,XMAX,verify_source_files
from deposition import simulate,midpoint_cases,gauss2_cases,continuum_reference
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'reference'))
from kinetic_tangent import EinsteinTangent
KINETIC_SHA='153e0a3ff4546adceaa56ed74149ccefc8ade4b72265064139d72e76a28967e7'

def jwrite(path,data):Path(path).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def original_geometry(name):
    if digest(HERE/'reference/kinetic_tangent.py')!=KINETIC_SHA:raise ValueError('BASS_BACKGROUND_SOURCE_HASH')
    if name=='COLD':model=EinsteinTangent(mass=30.,fraction=0.,A=0.,Sigma_ref=0.,orientation=1)
    elif name=='MASSIVE_PLUS':model=EinsteinTangent(mass=3.,fraction=.1,A=.5,Sigma_ref=0.,orientation=1)
    elif name=='MASSIVE_MINUS':model=EinsteinTangent(mass=3.,fraction=.1,A=-.5,Sigma_ref=0.,orientation=1)
    else:raise ValueError('GEOMETRY_NAME')
    sol=model.solution(rtol=2e-12,atol=2e-14,n=33)
    if not sol.success:raise RuntimeError('BASS_IVP')
    @lru_cache(maxsize=8192)
    def geometry(x):
        y=sol.sol(x);_,H,_,_=model.field(x,y[0],y[1])
        return float(y[0]),H,float(model.href*y[1])
    return geometry,{'name':name,'model':'PR164 original source-only BASS FD96 EinsteinTangent',
        'original_module_sha256':KINETIC_SHA,'mass_over_Tref':model.fd.mass,
        'mass_fraction':model.fraction,'A':model.A,'IVP_nfev':int(sol.nfev)}

def encode_case(cases,end):
    if not cases:raise ValueError('EMPTY_PROTOCOL')
    c=cases[0];c.validate()
    lines=[f'CASE {c.id} {c.nh0:.17g} {c.fesc:.17g} {c.nseg} {c.nmu} {c.nenergy} {c.qmin:.17g} {c.qmax:.17g}']
    for v in cases:
        v.validate()
        lines.append('BIRTH '+' '.join(format(x,'.17g') for x in (v.x,v.b,v.H,v.s,v.dt)))
    lines.append('END '+' '.join(format(x,'.17g') for x in end))
    return '\n'.join(lines)+'\n'

def generate(out):
    out=Path(out)
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True)
    started=time.perf_counter();verify_source_files()
    stream='BASS_SOURCELEDGER_INPUT_V1\n';expected={};summary=[];geometry_records=[]
    def add(cases,end,kind):
        nonlocal stream
        ident=cases[0].id
        if ident in expected:raise ValueError('DUPLICATE_FIXTURE')
        stream+=encode_case(cases,end)
        e=simulate(cases,end[0],end[1]);e['fixture_kind']=kind
        e['end_x']=end[0];e['end_b']=end[1];expected[ident]=e
        return e
    # Angular controls are not presented as native source histories.
    for b in (-.2,0.,.2):
        for nmu in (8,16,32):
            c=Case(f'POINT_{"M" if b<0 else "P"}{abs(b):.1f}_A{nmu}',.3,b,1e-16,0.,1e12,
                   nseg=8,nmu=nmu,nenergy=64,qmin=1.,qmax=512.)
            e=add([c],(.3,b,1e-16,0.),'MANUFACTURED_CONSTANT_B_POINT')
            summary.append({'kind':'angular','id':c.id,'b':b,'nmu':nmu,'P2_per_U':e['delta']/e['inventory_u'],
                            'continuum_P2_per_U':0.})
    z=Case('ZERO_DT',.3,0.,1e-16,0.,0.,nseg=8,nmu=8,nenergy=64,qmin=1.)
    add([z],(.3,0.,1e-16,0.),'ZERO_DURATION_CONTRACT')
    x0,x1=.2,.8
    for name in ('COLD','MASSIVE_PLUS','MASSIVE_MINUS'):
        geometry,record=original_geometry(name);geometry_records.append(record)
        b,H,s=geometry(x0)
        template=Case(name,x0,b,H,s,1.,nseg=8,nmu=16,nenergy=64,qmin=1.,qmax=512.)
        ref=continuum_reference(template,geometry,x0,x1,ntime=96,nangle=96)
        for method,rule in (('midpoint',midpoint_cases),('gl2',gauss2_cases)):
            for steps in (4,8,16,32):
                for nmu in (8,32):
                    c=replace(template,id=f'{name}_{method}_N{steps}_A{nmu}',nmu=nmu)
                    births=rule(c,geometry,x0,x1,steps)
                    b1,H1,s1=geometry(x1);e=add(births,(x1,b1,H1,s1),'ORIGINAL_BASS_FINITE_INTERVAL')
                    scale=max(ref['ledger_u'],1e-30)
                    summary.append({'kind':'temporal','id':c.id,'geometry':name,'method':method,'steps':steps,'nmu':nmu,
                        'U_relative_error_continuum':(e['inventory_u']-ref['inventory_u'])/ref['inventory_u'],
                        'N_relative_error_continuum':(e['inventory_n']-ref['inventory_n'])/ref['inventory_n'],
                        'Delta_difference_per_emitted_U':(e['delta']-ref['delta'])/scale,
                        'source_only_ledger_N_normalized':e['number_residual']/max(e['ledger_n'],1e-30),
                        'source_only_ledger_U_normalized':e['energy_residual']/max(e['ledger_u'],1e-30),
                        'continuum':ref})
    (out/'INPUT.tsv').write_text(stream)
    jwrite(out/'EXPECTED.json',expected)
    ratios=[]
    for name in ('COLD','MASSIVE_PLUS','MASSIVE_MINUS'):
        for method in ('midpoint','gl2'):
            rows=[r for r in summary if r.get('geometry')==name and r['nmu']==32 and r['method']==method]
            errors=[r['U_relative_error_continuum'] for r in rows]
            ratios.append({'geometry':name,'method':method,'steps':[4,8,16,32],'signed_U_errors':errors,
                           'successive_abs_error_ratios':[abs(errors[i]/errors[i+1]) for i in range(3)]})
    controls={
      'NEGATIVE_DT.tsv':'BASS_SOURCELEDGER_INPUT_V1\nCASE BAD 1.9e-7 .2 8 8 64 1 512\nBIRTH .3 0 1e-16 0 -1\nEND .4 0 1e-16 0\n',
      'NEGATIVE_SUPPORT.tsv':'BASS_SOURCELEDGER_INPUT_V1\nCASE BAD 1.9e-7 .2 8 8 64 90 512\nBIRTH .3 0 1e-16 0 1e12\nEND .4 0 1e-16 0\n',
      'EMPTY.tsv':'BASS_SOURCELEDGER_INPUT_V1\n',
      'MISSING_END.tsv':'BASS_SOURCELEDGER_INPUT_V1\nCASE BAD 1.9e-7 .2 8 8 64 1 512\nBIRTH .3 0 1e-16 0 1e12\n',
      'REVERSE_TIME.tsv':'BASS_SOURCELEDGER_INPUT_V1\nCASE BAD 1.9e-7 .2 8 8 64 1 512\nBIRTH .4 0 1e-16 0 1e12\nEND .3 0 1e-16 0\n',
    }
    for name,text in controls.items():(out/name).write_text(text)
    jwrite(out/'ANALYSIS.json',{'schema':'bass.sourceledger.sourceonly.campaign.v1','native_status':'NOT_RUN',
       'cases':len(expected),'birth_records':sum(v['births'] for v in expected.values()),
       'geometry_sources':geometry_records,'results':summary,'time_refinement':ratios,
       'derivation':'stages/S2_THEORY.md','scope':'Predicted native discrete SourceLedger; continuum quadrature independent; no native Rust output',
       'max_number_ledger_normalized':max(abs(r.get('source_only_ledger_N_normalized',0.)) for r in summary),
       'max_energy_ledger_normalized':max(abs(r.get('source_only_ledger_U_normalized',0.)) for r in summary)})
    jwrite(out/'FIXTURE_MANIFEST.json',{'schema':'bass.sourceledger.fixtures.v1','owner_sha':REI_SHA,
       'native_status':'NOT_RUN','cases':len(expected),'negative_inputs':list(controls),
       'files':{p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file()}})
    record={'cases':len(expected),'birth_records':sum(v['births'] for v in expected.values()),
       'time_refinement':ratios,'wall_s':time.perf_counter()-started,'native':'NOT_RUN'}
    print(json.dumps(record,indent=2));return record
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();generate(a.out)
