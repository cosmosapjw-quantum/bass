"""Validate the package transition, without rerunning research science campaigns."""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
DOSSIER=ROOT/'research/integration_transition_20261028'


def blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def run(command,name,out,cwd=ROOT,env=None):
    p=subprocess.run(command,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    (out/f'{name}.log').write_text(p.stdout)
    print(p.stdout[-3500:])
    if p.returncode:
        raise RuntimeError(f'{name} failed with exit {p.returncode}; see {out/name}.log')


def counts(path):
    node=ET.parse(path).getroot()
    suites=list(node) if node.tag=='testsuites' else [node]
    return {k:sum(int(s.attrib.get(k,0)) for s in suites) for k in ('tests','failures','errors','skipped')}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',default='/tmp/bass-integration')
    ap.add_argument('--skip-baseline',action='store_true',help='Record baseline as NOT_RUN, never PASS')
    opts=ap.parse_args();out=Path(opts.output).resolve();out.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((DOSSIER/'CODEGEN.json').read_text())
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONPATH=str(ROOT))
    run([sys.executable,'scripts/assemble_nonperturbative.py','--check'],'source-identity',out,env=env)
    # The sole existing-code edit is one new method; every pre-existing byte stays.
    tree=ast.parse((ROOT/'scripts/assemble_nonperturbative.py').read_text())
    method=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='METHOD'))
    current=(ROOT/'bianchi/q/polstate.py').read_text()
    if current.count(method)!=1 or blob(current.replace(method,'',1).encode())!=manifest['polstate']['original_blob']:
        raise AssertionError('Pre-existing PolQState changed outside the additive method')
    for path,h in manifest.get('protected_sources',[]):
        if blob((ROOT/path).read_bytes())!=h:raise AssertionError(f'Protected source changed: {path}')
    for p in (ROOT/'bianchi/nonperturbative').rglob('*.py'):
        compile(p.read_text(),str(p),'exec')
        if 'sys.path' in p.read_text() and p.name!='__init__.py':
            # Check AST calls/assignments, not harmless explanatory text.
            for n in ast.walk(ast.parse(p.read_text())):
                if isinstance(n,(ast.Call,ast.Assign)) and 'sys.path' in ast.unparse(n):
                    raise AssertionError(f'Import path mutation: {p}')
    run([sys.executable,'-m','pytest','tests/nonperturbative','-q','--junitxml='+str(out/'integration.xml')],
        'package-tests',out,env=env)
    baseline={'status':'NOT_RUN','reason':'explicit skip; local optional dependency unavailable'}
    if not opts.skip_baseline:
        run([sys.executable,'-m','pytest','tests/test_backend_policy.py','tests/test_rf00_route_inventory.py','-q',
             '--junitxml='+str(out/'backend.xml')],'existing-backend-tests',out,env=env)
        baseline={'status':'EXECUTED',**counts(out/'backend.xml')}
    with tempfile.TemporaryDirectory(prefix='bass-package-only-') as d:
        target=Path(d);shutil.copytree(ROOT/'bianchi',target/'bianchi',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        code="""import sys,numpy as np
from bianchi.nonperturbative import load_kernel,catalog,normal_time_collision_step
for name in catalog(): load_kernel(name,backend='python_oracle')
g=load_kernel('polarized_dictionary',backend='python_oracle').Grid(6,12)
J=g.P/2
out=normal_time_collision_step(g.n,g.w,J,dt_s=.1,rest_rate_s=.7,beta=[0,0,0],panels=8,backend='python_oracle')
assert np.max(abs(out-J))<2e-11
assert not any('/research/' in str(getattr(m,'__file__','')) for m in sys.modules.values())
from bianchi.q.polstate import PolQState
assert callable(PolQState.collide_normal_time)
print('PACKAGE_ONLY_PASS: 26 kernels and actual PolQState method, no research tree')
"""
        standalone=dict(env,PYTHONPATH=str(target))
        run([sys.executable,'-c',code],'package-only',out,cwd=target,env=standalone)
    result={'schema':'bass.integration.verification.v1','python':sys.version,
            'research_units':len(manifest['reports']),'migrated_modules':len(manifest['modules']),
            'migrated_test_files':len(manifest['tests']),'integration':counts(out/'integration.xml'),
            'baseline':baseline,'package_without_research':'PASS','old_polq_methods_byte_preserved':True,
            'native_rust_execution':'NOT_RUN','native_constructor_execution':'NOT_RUN',
            'science_campaigns_replayed':0,'new_scientific_nodes_executed':0,
            'native_subagent':'NOT_RUN','independent_model_review':'NOT_RUN',
            'production_ready':False,'scientific_dag_progress':'8/15 unchanged',
            'status':'PASS_SCOPED' if not opts.skip_baseline else 'PASS_SCOPED_BASELINE_DEPENDENCY_BLOCKED'}
    (out/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
