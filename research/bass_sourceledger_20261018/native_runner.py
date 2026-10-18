"""Pin, stage, compile and observe the *original* REI source-only ledger.

No rewrite of native physics, owner checkout changes, blanket-zero-test PASS,
network inside the runner, external Rust dependencies, or production restart.
Use an existing Git object database containing the pinned native commit.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import shutil
import signal
import platform
import resource
import subprocess
import time

from source_oracle import REI_SHA, PINS, SOURCE_ID, verify_source_files
HERE=Path(__file__).resolve().parent
NATIVE_CRATE='rust/rei_microphysics'
PROBE_NAME='bass_sourceledger_probe'
SCHEMA='bass.sourceledger.native.v1'
COMPLETE='bass.sourceledger.complete.v1'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write_json(path, data):
    Path(path).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
def strict_json(text):
    def bad(value):raise ValueError('NONFINITE_JSON:'+value)
    def object_pairs(pairs):
        obj={}
        for key,val in pairs:
            if key in obj:raise ValueError('DUPLICATE_JSON_KEY:'+key)
            obj[key]=val
        return obj
    return json.loads(text,parse_constant=bad,object_pairs_hook=object_pairs)

def validate_native(text, expected, owner_sha, probe_sha):
    """Protocol/content checks. A synthetic invocation is not native evidence."""
    lines=[line for line in text.splitlines() if line.strip()]
    if not expected or not lines:raise ValueError('EMPTY_NATIVE_DATA')
    try:rows=[strict_json(line) for line in lines]
    except (json.JSONDecodeError,TypeError) as e:raise ValueError('NATIVE_JSON') from e
    last=rows[-1]
    if last.get('schema')!=COMPLETE or type(last.get('count')) is not int or last['count']!=len(expected):
        raise ValueError('NATIVE_COMPLETION_COUNT')
    if len(rows)!=len(expected)+1:raise ValueError('NATIVE_ROW_COUNT')
    ids=[];defects=[]
    for row in rows:
        if row.get('owner_sha')!=owner_sha or row.get('probe_sha')!=probe_sha:
            raise ValueError('NATIVE_SOURCE_IDENTITY')
    for row in rows[:-1]:
        ident=row.get('id')
        if ident not in expected or ident in ids:raise ValueError('NATIVE_CASE_ID')
        ids.append(ident)
        e=expected[ident]
        if row.get('schema')!=SCHEMA or row.get('source_id')!=SOURCE_ID:raise ValueError('NATIVE_SCHEMA_SOURCE')
        if type(row.get('births')) is not int or row['births']!=e['births']:raise ValueError('BIRTH_COUNT')
        fields=('inventory_n','inventory_u','delta','dipole','ledger_n','ledger_u','work',
                'number_residual','energy_residual','proper_nh','min_number','pperp','ppar')
        for name in fields:
            if type(row.get(name)) not in (float,int) or not math.isfinite(row[name]):raise ValueError('NATIVE_FINITE:'+name)
        for name in ('inventory_n','inventory_u','ledger_n','ledger_u','proper_nh','min_number','pperp','ppar'):
            if row[name]<0:raise ValueError('NATIVE_POSITIVITY:'+name)
        nscale=max(abs(e['ledger_n']),1e-30);uscale=max(abs(e['ledger_u']),1e-30)
        errors={}
        # These are new, explicit source-only cross-language parity targets,
        # not a relaxation of any native chemistry or owner tolerance.
        for name in ('inventory_n','inventory_u','delta','dipole','ledger_n','ledger_u','work','proper_nh'):
            scale=nscale if name.endswith('_n') else (max(abs(e[name]),1e-30) if name=='proper_nh' else uscale)
            rel=abs(row[name]-e[name])/scale
            if rel>5e-11:raise ValueError('NATIVE_PARITY:'+ident+':'+name)
            errors[name]=rel
        if abs(row['number_residual'])/nscale>1e-11 or abs(row['energy_residual'])/uscale>1e-11:
            raise ValueError('NATIVE_LEDGER')
        if abs(row['inventory_n']-row['ledger_n']-row['number_residual'])/nscale>2e-14:
            raise ValueError('NATIVE_NUMBER_RESIDUAL_INCONSISTENT')
        if abs(row['inventory_u']+row['work']-row['ledger_u']-row['energy_residual'])/uscale>2e-14:
            raise ValueError('NATIVE_ENERGY_RESIDUAL_INCONSISTENT')
        for field,scale in [('ray_number',nscale),('ray_energy_ref',max(sum(e['ray_energy_ref']),1e-30))]:
            values=row.get(field)
            if not isinstance(values,list) or len(values)!=len(e[field]):raise ValueError('NATIVE_RAY_SHAPE')
            if any(type(v) not in (int,float) or not math.isfinite(v) or v<0 for v in values):raise ValueError('NATIVE_RAY_DOMAIN')
            err=sum(abs(a-b) for a,b in zip(values,e[field]))/scale
            if err>5e-11:raise ValueError('NATIVE_RAY_PARITY')
            errors[field+'_l1']=err
        defects.append({'id':ident,'normalized_differences':errors})
    return {'schema':'bass.sourceledger.validation.v1','cases':len(ids),'rows':len(rows)-1,
            'scope':'SOURCE_ONLY_NATIVE_VS_MATCHED_DISCRETE_ORACLE',
            'targets':{'cross_language_relative':5e-11,'ledger_relative':1e-11,
                       'normalization':'number by emitted photons/H; energy,stress,work by emitted eV/H; floor1e-30'},
            'defects':defects}

def git_bytes(repo, *args):
    c=subprocess.run(['git','-C',str(repo),*args],capture_output=True,check=False,timeout=90)
    if c.returncode:raise RuntimeError('PINNED_GIT_READ_FAILED:'+c.stderr.decode(errors='replace'))
    return c.stdout

def stage_owner(repo:Path,destination:Path,commit=REI_SHA,pins=PINS):
    """Copy committed blobs only; never use dirty working-tree source files.

    The bounded literal include closure fixes old include_str! staging failures.
    Non-literal include macros and Git symlinks fail closed for manual review.
    """
    if not re.fullmatch(r'[0-9a-f]{40}',commit):raise ValueError('COMMIT_IDENTITY')
    if destination.exists():raise FileExistsError(destination)
    git_bytes(repo,'cat-file','-e',commit+'^{commit}')
    tree=git_bytes(repo,'ls-tree','-r','-z',commit,'--',NATIVE_CRATE)
    files={}
    for item in tree.split(b'\0'):
        if not item:continue
        meta,path=item.split(b'\t',1);mode,kind,_=meta.split()
        if kind!=b'blob' or mode not in (b'100644',b'100755'):raise ValueError('NATIVE_TREE_MODE')
        files[path.decode('utf-8')]=None
    if NATIVE_CRATE+'/Cargo.toml' not in files:raise ValueError('MISSING_NATIVE_CRATE')
    includes=re.compile(r'\binclude(?:_str|_bytes)?!\s*\(\s*"([^"\n]+)"\s*\)',re.MULTILINE)
    any_include=re.compile(r'\binclude(?:_str|_bytes)?!\s*\(')
    pending=list(files);size=0
    while pending:
        path=pending.pop()
        raw=git_bytes(repo,'show',commit+':'+path);size+=len(raw)
        if size>64*1024*1024 or len(files)>5000:raise ValueError('SOURCE_STAGE_BUDGET')
        files[path]=raw
        if path.endswith('.rs'):
            text=raw.decode('utf-8')
            matches=list(includes.finditer(text))
            if len(matches)!=len(any_include.findall(text)):raise ValueError('NONLITERAL_INCLUDE:'+path)
            for m in matches:
                relative=m.group(1)
                if PurePosixPath(relative).is_absolute() or '\\' in relative:raise ValueError('INCLUDE_PATH')
                target=posixpath.normpath(posixpath.join(posixpath.dirname(path),relative))
                if target=='..' or target.startswith('../'):raise ValueError('INCLUDE_ESCAPES_REPO')
                if target not in files:files[target]=None;pending.append(target)
    for name,digest in pins.items():
        raw=files.get(NATIVE_CRATE+'/src/'+name)
        if raw is None or hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('PINNED_NATIVE_SOURCE:'+name)
    destination.mkdir(parents=True)
    for path,raw in files.items():
        p=destination/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    receipt={'owner_commit':commit,'source_files':len(files),'source_bytes':size,
             'original_pins':pins,'files':{p:hashlib.sha256(v).hexdigest() for p,v in sorted(files.items())}}
    return receipt

def compiler_executable(stdout,allowed_root:Path):
    found=[]
    for line in stdout.splitlines():
        if not line.strip():continue
        try:r=strict_json(line)
        except (ValueError,TypeError):continue
        if r.get('reason')=='compiler-artifact' and r.get('target',{}).get('name')==PROBE_NAME and 'bin' in r.get('target',{}).get('kind',[]) and r.get('executable'):
            found.append(Path(r['executable']).resolve())
    found=list(dict.fromkeys(found))
    if len(found)!=1:raise ValueError('NO_UNIQUE_NATIVE_EXECUTABLE')
    exe=found[0]
    if not exe.is_relative_to(allowed_root.resolve()) or not exe.is_file() or not os.access(exe,os.X_OK):
        raise ValueError('INVALID_NATIVE_EXECUTABLE')
    return exe

def run(repo,fixtures,out,cargo=None,jobs=2,timeout=1800):
    if out.exists():raise FileExistsError(out)
    if not 1<=jobs<=4 or not 10<=timeout<=1800:raise ValueError('EXECUTION_BUDGET')
    out.mkdir(parents=True)
    status={'schema':'bass.sourceledger.execution.v1','started_utc':datetime.now(timezone.utc).isoformat(),
            'status':'RUNNING','native_admission':'NOT_RUN','commands':[],'owner':REI_SHA,
            'host':platform.node(),'logical_cpus':os.cpu_count(),'python':platform.python_version(),
            'limits':{'cargo_jobs':jobs,'total_wall_s':timeout,'native_source_threads':1,'source_stage_bytes':64*1024*1024}}
    resultpath=out/'RETURN_TO_CHATGPT.json'
    env=os.environ.copy()
    env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',RAYON_NUM_THREADS='1',CARGO_BUILD_JOBS=str(jobs))
    started=time.monotonic()
    def command(label,argv):
        remaining=timeout-(time.monotonic()-started)
        if remaining<=0:raise TimeoutError('TOTAL_WALL_BUDGET')
        t=time.monotonic()
        with (out/(label+'.stdout')).open('w') as stdout,(out/(label+'.stderr')).open('w') as stderr:
            process=subprocess.Popen(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,start_new_session=True)
            try:
                process.wait(timeout=remaining)
                r=process
            except subprocess.TimeoutExpired:
                # Only the process group created by this runner is terminated.
                os.killpg(process.pid,signal.SIGKILL);process.wait()
                status['commands'].append({'label':label,'argv':list(map(str,argv)),'exit_code':'TIMEOUT','wall_s':time.monotonic()-t})
                raise
        record={'label':label,'argv':list(map(str,argv)),'exit_code':r.returncode,'wall_s':time.monotonic()-t}
        status['commands'].append(record);write_json(resultpath,status)
        return r.returncode
    try:
        verify_source_files()
        fixtures=Path(fixtures).resolve()
        manifest=strict_json((fixtures/'FIXTURE_MANIFEST.json').read_text())
        for name,digest in manifest['files'].items():
            if '/' in name or '\\' in name or sha(fixtures/name)!=digest:raise ValueError('FIXTURE_HASH:'+name)
        expected=strict_json((fixtures/'EXPECTED.json').read_text())
        status['fixture_manifest_sha256']=sha(fixtures/'FIXTURE_MANIFEST.json')
        status['stage']=stage_owner(Path(repo).resolve(),out/'owner')
        shutil.copytree(HERE/'native_probe',out/'probe')
        status['probe_sha256']=sha(out/'probe/src/main.rs')
        env.update(BASS_REI_SHA=REI_SHA,BASS_PROBE_SHA=status['probe_sha256'],CARGO_TARGET_DIR=str((out/'target').resolve()))
        cargo=cargo or shutil.which('cargo')
        if not cargo:
            candidate=Path.home()/'.cargo/bin/cargo'
            if candidate.is_file():cargo=str(candidate)
        if not cargo:raise FileNotFoundError('CARGO_NOT_AVAILABLE')
        # Preserve rustup's cargo symlink name: argv[0] selects the tool.
        cargo=str(Path(cargo).expanduser().absolute()) if '/' in cargo else cargo
        if command('toolchain',[cargo,'--version']):raise RuntimeError('CARGO_VERSION')
        man=out/'probe/Cargo.toml'
        if command('lock',[cargo,'generate-lockfile','--offline','--manifest-path',man]):raise RuntimeError('CARGO_LOCK_FAILED')
        if command('build',[cargo,'build','--offline','--locked','--release','--manifest-path',man,'--message-format=json']):raise RuntimeError('NATIVE_BUILD_FAILED')
        executable=compiler_executable((out/'build.stdout').read_text(),out/'target')
        status['binary_sha256']=sha(executable)
        if command('measure',[executable,fixtures/'INPUT.tsv',out/'NATIVE.jsonl']):raise RuntimeError('NATIVE_MEASUREMENT_FAILED')
        status['validation']=validate_native((out/'NATIVE.jsonl').read_text(),expected,REI_SHA,status['probe_sha256'])
        status['negative_controls']=[]
        for name in manifest['negative_inputs']:
            produced=out/(name+'.jsonl')
            code=command(name,[executable,fixtures/name,produced])
            if code!=3 or produced.exists():raise RuntimeError('NEGATIVE_CONTROL_NOT_REJECTED:'+name)
            status['negative_controls'].append({'name':name,'exit_code':code,'no_output':True})
        status['status']='PASS_SCOPED_SOURCE_LEDGER'
        status['native_admission']='MEASURED_PINNED_NATIVE_SOURCE_ONLY'
        status['not_admitted']=['continuum quadrature accuracy','HHe/opacity','source-age reactive history','new checkpoint','Q^a/EoR']
    except Exception as exc:
        status['status']='BLOCKED_OR_FAILED';status['error']=f'{type(exc).__name__}: {exc}'
        status['wall_s']=time.monotonic()-started;write_json(resultpath,status)
        raise
    status['wall_s']=time.monotonic()-started
    status['children_peak_rss_kib_linux']=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    write_json(resultpath,status)
    return status

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--rei-repo',type=Path,required=True)
    ap.add_argument('--fixtures',type=Path,default=HERE/'fixtures')
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--cargo')
    ap.add_argument('--jobs',type=int,default=2)
    ap.add_argument('--wall-seconds',type=int,default=1800)
    a=ap.parse_args()
    r=run(a.rei_repo,a.fixtures,a.out.resolve(),a.cargo,a.jobs,a.wall_seconds)
    print(json.dumps({'status':r['status'],'cases':r['validation']['cases'],'native_admission':r['native_admission']},indent=2))
