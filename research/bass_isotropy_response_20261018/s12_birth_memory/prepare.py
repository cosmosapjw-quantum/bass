#!/usr/bin/env python3
"""Prepare/build only the published S12 client in an isolated runtime directory.

Every BASS/upstream file is hash bound before compilation.  No histories run.
Use the existing compiler; supplied --cargo/--rustc also support a private pinned
toolchain. No global package, repository, or server configuration is changed.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import time
import urllib.request
from process_control import run_owned

HERE = Path(__file__).resolve().parent
LANE = HERE.parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    path = Path(path);path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    os.replace(temporary, path)


def verify_upstream(root, row):
    relative = Path(row['path'])
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('UPSTREAM_UNSAFE_PATH')
    b = (root/relative).read_bytes()
    blob = hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
    if len(b) != row['size'] or hashlib.sha256(b).hexdigest() != row['sha256'] or blob != row['git_blob']:
        raise ValueError('UPSTREAM_SOURCE_MISMATCH:'+row['path'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work-dir', type=Path, required=True)
    parser.add_argument('--binding', type=Path, required=True)
    parser.add_argument('--source-commit', required=True)
    parser.add_argument('--vigilode-root', type=Path)
    parser.add_argument('--cargo', default=shutil.which('cargo') or 'cargo')
    parser.add_argument('--rustc', default=shutil.which('rustc') or 'rustc')
    parser.add_argument('--jobs', type=int, default=2)
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.jobs <= 16:
        parser.error('build jobs must be in1..16; independent NCP jobs may use more cores')
    work = args.work_dir.resolve();work.mkdir(parents=True, exist_ok=True)
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    record = {'schema': 'BASS_S12_BUILD_RECEIPT_V1', 'status': 'INCOMPLETE',
        'source_commit': args.source_commit, 'started_utc': started,
        'scientific_campaign_executed': False, 'commands': []}
    code = 0
    try:
        binding = json.loads(args.binding.read_bytes())
        if binding['source_commit'] != args.source_commit or not binding['git_readback_pass']:
            raise ValueError('SOURCE_BINDING_COMMIT_OR_READBACK')
        repo = HERE.parents[2]
        record['binding_sha256'] = sha(args.binding)
        record['source_files'] = {}
        for row in binding['files']:
            p = Path(row['path'])
            if p.is_absolute() or '..' in p.parts:
                raise ValueError('SOURCE_BINDING_PATH')
            b = (repo/p).read_bytes()
            if hashlib.sha256(b).hexdigest() != row['sha256']:
                raise ValueError('SOURCE_BINDING_BYTES:'+str(p))
            if hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest() != row['git_blob']:
                raise ValueError('SOURCE_BINDING_GIT_BLOB:'+str(p))
            record['source_files'][str(p)] = row['sha256']
        manifest_path = LANE/'s9_vigilode/VIGILODE_SOURCE.json'
        manifest = json.loads(manifest_path.read_bytes())
        if manifest['repo'] != 'cosmosapjw-quantum/vigilode' or manifest['source_commit'] != 'a21d573980f66fe02891bd216153443b5352f921':
            raise ValueError('UPSTREAM_OWNER')
        if sum(x['size'] for x in manifest['files']) > 6*1024**2:
            raise ValueError('UPSTREAM_SIZE_BUDGET')
        upstream = work/'vigilode'
        if args.vigilode_root:
            selected = args.vigilode_root.resolve()
            for row in manifest['files']:
                verify_upstream(selected, row)
            if selected != upstream:
                if upstream.is_symlink():raise ValueError('UPSTREAM_SYMLINK_NOT_BUNDLED')
                for row in manifest['files']:
                    destination=upstream/row['path']
                    if not destination.exists():
                        destination.parent.mkdir(parents=True,exist_ok=True)
                        shutil.copyfile(selected/row['path'],destination)
                    verify_upstream(upstream,row)
        else:
            def fetch(row):
                target = upstream/row['path']
                if not target.exists():
                    if args.offline:raise FileNotFoundError('OFFLINE_UPSTREAM_MISSING:'+row['path'])
                    url = 'https://raw.githubusercontent.com/'+manifest['repo']+'/'+manifest['source_commit']+'/'+row['path']
                    with urllib.request.urlopen(url, timeout=30) as response:
                        b = response.read(row['size']+1)
                    if len(b) != row['size']:raise ValueError('UPSTREAM_SIZE')
                    target.parent.mkdir(parents=True, exist_ok=True);target.write_bytes(b)
                verify_upstream(upstream, row)
            with ThreadPoolExecutor(max_workers=min(4, args.jobs)) as pool:
                list(pool.map(fetch, manifest['files']))
        record['upstream'] = {'commit': manifest['source_commit'], 'tree': manifest['source_tree'],
            'files': len(manifest['files']), 'bytes': sum(x['size'] for x in manifest['files']),
            'manifest_sha256': sha(manifest_path)}
        client = work/'client/s12_birth_memory';client.mkdir(parents=True, exist_ok=True)
        runtime_files = {}
        for path in [HERE/'Cargo.toml', HERE/'Cargo.lock', *sorted((HERE/'src').glob('*.rs'))]:
            relative = path.relative_to(HERE)
            target = client/relative;target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target);runtime_files[str(relative)] = sha(target)
        projector = LANE/'s11_p246/rust/projector.rs'
        target = work/'client/s11_p246/rust/projector.rs';target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(projector, target)
        record['projector_sha256'] = sha(projector)
        record['runtime_client_files'] = runtime_files
        env = os.environ.copy()
        env.update(RUSTC=str(Path(args.rustc).resolve()), CARGO_HOME=str(work/'cargo_home'),
            CARGO_TARGET_DIR=str(work/'target'), CARGO_BUILD_JOBS=str(args.jobs), CARGO_INCREMENTAL='0',
            RAYON_NUM_THREADS='1', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
        for label, executable in [('cargo', args.cargo), ('rustc', args.rustc)]:
            result = subprocess.run([executable, '--version'], env=env, capture_output=True, text=True, timeout=30)
            if result.returncode:raise ValueError('TOOLCHAIN_'+label+':'+result.stderr)
            record[label+'_version'] = result.stdout.strip()
        if 'rustc 1.94.1 ' not in record['rustc_version']:
            raise ValueError('PINNED_RUSTC_1_94_1_REQUIRED')
        if args.prepare_only:
            record['status'] = 'SOURCES_PREPARED_NOT_COMPILED'
        else:
            command = [args.cargo, 'build', '--locked', '--release', '--bins']
            if args.offline:command.append('--offline')
            execution=run_owned(command,cwd=client,env=env,
                stdout_path=work/'compile.stdout',stderr_path=work/'compile.stderr',
                receipt_path=work/'COMPILE_PROCESS.json',timeout_s=1750,
                as_bytes=6*1024**3,file_bytes=512*1024**2)
            code=execution['exit_code'];record['commands'].append(execution)
            if code:raise RuntimeError('COMPILE_FAILED')
            if any(sha(client/p) != h for p, h in runtime_files.items()):
                raise ValueError('RUNTIME_SOURCE_CHANGED_DURING_BUILD')
            if sha(target) != record['projector_sha256']:raise ValueError('PROJECTOR_CHANGED_DURING_BUILD')
            record['binaries'] = {name: {'path': str(work/'target/release'/name),
                'sha256': sha(work/'target/release'/name)} for name in ['s12-core', 's12-history']}
            record['status'] = 'COMPILED_SOURCE_BOUND'
    except Exception as e:
        code = code or 2
        record['status'] = 'FAILED'
        record['failure'] = {'type': type(e).__name__, 'message': str(e)}
    record['ended_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
    save(work/'BUILD_RECEIPT.json', record)
    print(json.dumps({'status': record['status'], 'exit_code': code, 'receipt': str(work/'BUILD_RECEIPT.json')}))
    raise SystemExit(code)


if __name__ == '__main__':main()
