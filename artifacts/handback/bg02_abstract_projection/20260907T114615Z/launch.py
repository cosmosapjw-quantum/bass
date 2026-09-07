from pathlib import Path
import datetime, hashlib, json, os, shutil, subprocess, sys, time

run = Path(__file__).resolve().parent
ctx = json.loads((run / 'context.json').read_text())
label = sys.argv[1]
out = run / 'execution' / label
out.mkdir(parents=True, exist_ok=False)
code = Path(ctx['code_directory'])
deps = json.loads((run / 'identity/dependencies.json').read_text())
files = [Path(d['path']) for d in deps] + [code / name for name in
    ['AbstractProjection.wl', 'projection_tests.wl', 'run_projection.wls']]
def hashes():
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
def save(name, value):
    (out / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
previous = list((run / 'execution').glob('*/process.json'))
assert len(previous) < 20
assert sum(json.loads(p.read_text())['elapsed_seconds'] for p in previous) < 3360
script = Path(sys.argv[2]) if len(sys.argv) > 2 else code / 'run_projection.wls'
argv = ['timeout', '--signal=TERM', '--kill-after=10s', '240s', ctx['wolframscript'],
        '-local', ctx['kernel'], '-file', str(script)]
env = os.environ.copy()
env['BASS_REPO'] = ctx['BASS_REPO']
before = hashes()
save('source-before.json', before)
shutil.copytree(code, out / 'code')
if script.parent != code:
    shutil.copy2(script, out / 'diagnostic-script.wls')
start = datetime.datetime.now(datetime.timezone.utc).isoformat()
save('ATTEMPT_STARTED.json', {'label': label, 'started_at_utc': start, 'argv': argv,
     'BASS_REPO': ctx['BASS_REPO'], 'script_sha256': hashlib.sha256(script.read_bytes()).hexdigest()})
t0 = time.monotonic()
with (out / 'stdout.log').open('wb') as stdout, (out / 'stderr.log').open('wb') as stderr:
    process = subprocess.run(argv, cwd=out, env=env, stdout=stdout, stderr=stderr)
elapsed = time.monotonic() - t0
after = hashes()
save('source-after.json', after)
result = {'label': label, 'started_at_utc': start,
          'ended_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'elapsed_seconds': elapsed, 'exit_code': process.returncode,
          'source_unchanged': before == after, 'argv': argv}
save('process.json', result)
text = (out / 'stdout.log').read_text(errors='replace')
if 'AP_FINAL_BEGIN\n' in text and '\nAP_FINAL_END' in text:
    payload = text.split('AP_FINAL_BEGIN\n', 1)[1].split('\nAP_FINAL_END', 1)[0]
    try:
        final = json.loads(payload)
        save('ap-final.json', final)
        result['status'] = final.get('status')
        result['rows'] = len(final.get('rows', []))
    except json.JSONDecodeError as exc:
        save('final-parse-error.json', {'error': str(exc), 'payload': payload})
print(json.dumps(result, indent=2))
