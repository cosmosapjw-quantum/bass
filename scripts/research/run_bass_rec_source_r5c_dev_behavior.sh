#!/usr/bin/env bash
# R5C development-behavior gate for the BASS REC source protocol.
#
# This runner uses the explicit RF-00 development override only for the native
# differential integration tests.  A PASS is behavior-only evidence and never
# establishes production provenance.  The trusted-payload registry is neither
# read-modified-written nor patched by this script.
#
# Safe shell contract:
# - may be launched from rec_bianchi or any other directory;
# - never switches the caller checkout;
# - uses detached temporary worktrees and an isolated Python 3.12 venv;
# - does not use `set -e`;
# - records a machine-readable classification and exits zero.
#
# Optional overrides:
#   BASS_REPO=/absolute/path/to/bass
#   R5B_RECEIPT_DIR=/absolute/path/to/BASS_REC_SOURCE_R5B_<stamp>
#   PYTHON_BOOTSTRAP=/absolute/path/to/python3.12
#   RECEIPT_ROOT=/absolute/path
#   KEEP_SANDBOX=1

set +e
set +u
set +o pipefail 2>/dev/null || true

BASE_COMMIT='d81ad12f795b6ac6d57293502e75426ed1dbbb1a'
CANDIDATE_COMMIT='fc4d21b92a1abd1e9b35178f7d666831fc5c827d'
CANDIDATE_BRANCH='research/bass-rec-source-r5-protocol-green-20260903-r1'
EXPECTED_WHEEL_SHA256='bf5a59534ffc9d6f9c3410aa19319f18a4a8a7a9761bcd61c5da8c8627ddf609'
GOLDEN_PAYLOAD_SHA256='ca3807fa4ef49b5292bd65fd80b6fe9947c1cef7f835979122bff572900eb906'
OVERRIDE='BASS_ALLOW_UNVERIFIED_NATIVE_DEV'

STAMP="$(date -u +%Y%m%dT%H%M%SZ 2>/dev/null)"
[ -n "$STAMP" ] || STAMP='UNKNOWN_TIME'
RECEIPT_ROOT="${RECEIPT_ROOT:-$HOME/Dropbox/bianchi/_runtime_receipts}"
OUT="$RECEIPT_ROOT/BASS_REC_SOURCE_R5C_$STAMP"
mkdir -p "$OUT" 2>/dev/null
if [ ! -d "$OUT" ]; then
  printf 'classification=STOP_RECEIPT_DIRECTORY_UNAVAILABLE\n'
  exit 0
fi
MASTER="$OUT/master.log"
: >"$MASTER"
say() { printf '\n===== %s =====\n' "$*" | tee -a "$MASTER"; }
kv() { printf '%s=%s\n' "$1" "$2" | tee -a "$MASTER"; }
stop() { kv classification "$1"; kv detail "$2"; kv receipt_dir "$OUT"; exit 0; }

is_bass_repo() {
  C="$1"
  [ -n "$C" ] || return 1
  TOP="$(git -C "$C" rev-parse --show-toplevel 2>/dev/null)"
  [ -n "$TOP" ] || return 1
  ORIGIN="$(git -C "$TOP" config --get remote.origin.url 2>/dev/null)"
  case "$ORIGIN" in
    *cosmosapjw-quantum/bass|*cosmosapjw-quantum/bass.git)
      printf '%s\n' "$TOP"; return 0;;
  esac
  return 1
}

say 'CALLER CONTEXT'
kv caller_pwd "$PWD"
kv caller_head "$(git rev-parse HEAD 2>/dev/null || printf NOT_A_GIT_REPOSITORY)"
kv caller_origin "$(git config --get remote.origin.url 2>/dev/null || printf UNAVAILABLE)"

say 'LOCATE BASS'
BASS=''
if [ -n "${BASS_REPO:-}" ]; then BASS="$(is_bass_repo "$BASS_REPO")"; fi
if [ -z "$BASS" ]; then
  for C in "$HOME/Dropbox/bianchi/bass" "$HOME/Dropbox/bass" "$HOME/bass"; do
    BASS="$(is_bass_repo "$C")"; [ -n "$BASS" ] && break
  done
fi
[ -n "$BASS" ] || stop STOP_BASS_REPOSITORY_NOT_FOUND 'Set BASS_REPO explicitly.'
kv bass_repo "$BASS"
kv bass_origin "$(git -C "$BASS" config --get remote.origin.url 2>/dev/null)"

say 'LOCATE EXACT R5B WHEEL'
R5B="${R5B_RECEIPT_DIR:-$HOME/Dropbox/bianchi/_runtime_receipts/BASS_REC_SOURCE_R5B_20260903T140455Z}"
mapfile -t WHEELS < <(find "$R5B/wheel" -maxdepth 1 -type f -name 'bianchi_rustcore-0.1.0-*.whl' -print 2>/dev/null)
[ "${#WHEELS[@]}" -eq 1 ] || stop STOP_R5B_WHEEL_NOT_UNIQUE "count=${#WHEELS[@]} root=$R5B/wheel"
WHEEL="${WHEELS[0]}"
WHEEL_SHA="$(sha256sum "$WHEEL" 2>/dev/null | awk '{print $1}')"
kv wheel "$WHEEL"
kv wheel_sha256 "$WHEEL_SHA"
[ "$WHEEL_SHA" = "$EXPECTED_WHEEL_SHA256" ] || stop STOP_R5B_WHEEL_IDENTITY_MISMATCH "$WHEEL_SHA"

say 'SELECT PYTHON 3.12'
PY_BOOT="${PYTHON_BOOTSTRAP:-$(command -v python3.12 2>/dev/null)}"
[ -x "$PY_BOOT" ] || stop STOP_PYTHON_3_12_NOT_FOUND 'Set PYTHON_BOOTSTRAP.'
PYVER="$("$PY_BOOT" -c 'import sys; print(".".join(map(str,sys.version_info[:3])))' 2>/dev/null)"
kv python_bootstrap "$PY_BOOT"
kv python_version "$PYVER"
case "$PYVER" in 3.12.*) ;; *) stop STOP_WRONG_PYTHON_VERSION "$PYVER";; esac

say 'FETCH AND VERIFY SOURCE IDENTITIES'
git -C "$BASS" fetch --no-tags origin "$CANDIDATE_BRANCH:refs/remotes/origin/$CANDIDATE_BRANCH" >"$OUT/fetch.log" 2>&1
RC_FETCH=$?
REMOTE_HEAD="$(git -C "$BASS" rev-parse "refs/remotes/origin/$CANDIDATE_BRANCH" 2>/dev/null)"
kv fetch_rc "$RC_FETCH"
kv remote_head "${REMOTE_HEAD:-UNAVAILABLE}"
[ "$REMOTE_HEAD" = "$CANDIDATE_COMMIT" ] || stop STOP_REMOTE_HEAD_MOVED_OR_FETCH_FAILED "${REMOTE_HEAD:-UNAVAILABLE}"
for SHA in "$BASE_COMMIT" "$CANDIDATE_COMMIT"; do
  git -C "$BASS" cat-file -e "$SHA^{commit}" 2>/dev/null || stop STOP_COMMIT_UNAVAILABLE "$SHA"
done
git -C "$BASS" diff --name-only "$BASE_COMMIT" "$CANDIDATE_COMMIT" >"$OUT/changed_paths.txt" 2>&1
[ "$(cat "$OUT/changed_paths.txt" 2>/dev/null)" = 'bianchi/source_authority.py' ] || stop STOP_UNEXPECTED_CANDIDATE_DIFF "$OUT/changed_paths.txt"

say 'CREATE DETACHED WORKTREES AND ISOLATED VENV'
SANDBOX="$(mktemp -d /tmp/bass-rec-r5c.XXXXXX 2>/dev/null)"
[ -d "$SANDBOX" ] || stop STOP_TEMP_DIRECTORY_FAILURE 'mktemp failed'
WT_BASE="$SANDBOX/base"
WT_CAND="$SANDBOX/candidate"
VENV="$SANDBOX/venv"
cleanup() {
  if [ "${KEEP_SANDBOX:-0}" != '1' ]; then
    git -C "$BASS" worktree remove --force "$WT_BASE" >/dev/null 2>&1 || true
    git -C "$BASS" worktree remove --force "$WT_CAND" >/dev/null 2>&1 || true
    case "$SANDBOX" in /tmp/bass-rec-r5c.*) rm -rf -- "$SANDBOX" >/dev/null 2>&1 || true;; esac
  else
    kv sandbox_preserved "$SANDBOX"
  fi
}
trap cleanup EXIT HUP INT TERM
git -C "$BASS" worktree add --detach "$WT_BASE" "$BASE_COMMIT" >"$OUT/worktree_base.log" 2>&1; RC_WT_BASE=$?
git -C "$BASS" worktree add --detach "$WT_CAND" "$CANDIDATE_COMMIT" >"$OUT/worktree_candidate.log" 2>&1; RC_WT_CAND=$?
"$PY_BOOT" -m venv "$VENV" >"$OUT/venv.log" 2>&1; RC_VENV=$?
kv worktree_base_rc "$RC_WT_BASE"
kv worktree_candidate_rc "$RC_WT_CAND"
kv venv_rc "$RC_VENV"
[ "$RC_WT_BASE" -eq 0 ] && [ "$RC_WT_CAND" -eq 0 ] && [ "$RC_VENV" -eq 0 ] || stop STOP_ISOLATION_CREATION_FAILED "base=$RC_WT_BASE candidate=$RC_WT_CAND venv=$RC_VENV"
PY="$VENV/bin/python"

say 'INSTALL LOCK, LOCAL WHEEL, AND CANDIDATE PACKAGE'
"$PY" -m pip install --disable-pip-version-check -r "$WT_CAND/requirements.lock" >"$OUT/pip_lock.log" 2>&1; RC_LOCK=$?
"$PY" -m pip install --disable-pip-version-check --no-deps "$WHEEL" >"$OUT/pip_wheel.log" 2>&1; RC_WHEEL=$?
( cd "$WT_CAND" && "$PY" -m pip install --disable-pip-version-check --no-deps . ) >"$OUT/pip_project.log" 2>&1; RC_PROJECT=$?
kv lock_install_rc "$RC_LOCK"
kv wheel_install_rc "$RC_WHEEL"
kv project_install_rc "$RC_PROJECT"
[ "$RC_LOCK" -eq 0 ] && [ "$RC_WHEEL" -eq 0 ] && [ "$RC_PROJECT" -eq 0 ] || stop STOP_INSTALL_FAILED "lock=$RC_LOCK wheel=$RC_WHEEL project=$RC_PROJECT"

say 'DEFAULT FAIL-CLOSED CONTROL'
( cd "$WT_CAND" && env -u "$OVERRIDE" PYTHONPATH="$WT_CAND" "$PY" - <<'PY'
from bianchi import backend
from bianchi.backend_policy import UnverifiedNativePayloadError
try:
    backend.thomson_stiffness(1.0, 0.01)
except UnverifiedNativePayloadError as exc:
    print('EXPECTED_UNVERIFIED_NATIVE_PAYLOAD_ERROR')
    print(exc)
else:
    raise SystemExit('untrusted wheel dispatched without explicit override')
PY
) >"$OUT/default_fail_closed.log" 2>&1
RC_FAIL_CLOSED=$?
kv default_fail_closed_rc "$RC_FAIL_CLOSED"

say 'POLICY AND PACKAGING WITHOUT OVERRIDE'
( cd "$WT_CAND" && env -u "$OVERRIDE" PYTHONPATH="$WT_CAND" "$PY" -m pytest -q tests/test_backend_policy.py tests/test_backend_packaging.py --junitxml="$OUT/policy_packaging.xml" ) >"$OUT/policy_packaging.log" 2>&1
RC_POLICY=$?
kv policy_packaging_rc "$RC_POLICY"

say 'BASE INTEGRATION WITH EXPLICIT DEVELOPMENT OVERRIDE'
( cd "$WT_BASE" && env "$OVERRIDE=1" PYTHONWARNINGS=always PYTHONPATH="$WT_BASE" "$PY" -m pytest -q tests/test_backend_integration.py --junitxml="$OUT/base_integration.xml" ) >"$OUT/base_integration.log" 2>&1
RC_BASE=$?
kv base_integration_rc "$RC_BASE"

say 'CANDIDATE INTEGRATION WITH EXPLICIT DEVELOPMENT OVERRIDE'
( cd "$WT_CAND" && env "$OVERRIDE=1" PYTHONWARNINGS=always PYTHONPATH="$WT_CAND" "$PY" -m pytest -q tests/test_backend_integration.py --junitxml="$OUT/candidate_integration.xml" ) >"$OUT/candidate_integration.log" 2>&1
RC_CAND=$?
kv candidate_integration_rc "$RC_CAND"

say 'FOCUSED SOURCE CONTRACT AND TWO-PROCESS HASH'
( cd "$WT_CAND" && PYTHONPATH="$WT_CAND" "$PY" -m unittest -v tests/research/test_bass_rec_source_protocol_red.py ) >"$OUT/focused.log" 2>&1
RC_FOCUSED=$?
: >"$OUT/payload_hashes.txt"
for RUN in 1 2; do
  ( cd "$WT_CAND" && PYTHONPATH="$WT_CAND" "$PY" - <<'PY'
from bianchi.source_authority import SourceAuthorityBundle, SourceFrequencyKind
b = SourceAuthorityBundle.constant_pair(
    eta_s_inv=3.0,
    kappa_s_inv=2.0,
    frame='hydrogen_orthonormal',
    channel='total_occupation',
    source_sha256='0'*64,
    frequency_kind=SourceFrequencyKind.POINTWISE_SPECTRAL,
)
print(b.payload_sha256)
PY
  ) >>"$OUT/payload_hashes.txt" 2>>"$OUT/payload_hash_errors.log"
done
RC_HASH=$?
H1="$(sed -n '1p' "$OUT/payload_hashes.txt" 2>/dev/null)"
H2="$(sed -n '2p' "$OUT/payload_hashes.txt" 2>/dev/null)"
HASH_PASS=0
[ "$H1" = "$GOLDEN_PAYLOAD_SHA256" ] && [ "$H2" = "$GOLDEN_PAYLOAD_SHA256" ] && HASH_PASS=1
kv focused_rc "$RC_FOCUSED"
kv hash_1 "${H1:-MISSING}"
kv hash_2 "${H2:-MISSING}"
kv hash_pass "$HASH_PASS"

say 'COMPARE TEST SUMMARIES AND WARNINGS'
export OUT
"$PY" - <<'PY' >"$OUT/junit_compare_stdout.log" 2>"$OUT/junit_compare_stderr.log"
import json, os, xml.etree.ElementTree as ET
from pathlib import Path
out = Path(os.environ['OUT'])
def read(name):
    root = ET.parse(out/name).getroot()
    suites = [root] if root.tag == 'testsuite' else list(root.findall('testsuite'))
    return {k: sum(int(s.attrib.get(k, '0')) for s in suites) for k in ('tests','failures','errors','skipped')}
payload = {'base': read('base_integration.xml'), 'candidate': read('candidate_integration.xml')}
payload['same_counts'] = payload['base'] == payload['candidate']
(out/'junit_comparison.json').write_text(json.dumps(payload, indent=2, sort_keys=True)+'\n')
PY
RC_COMPARE=$?
SAME_COUNTS="$("$PY" -c 'import json,sys; print(int(json.load(open(sys.argv[1]))["same_counts"]))' "$OUT/junit_comparison.json" 2>/dev/null)"
WARNINGS="$(grep -c 'UNVERIFIED_DEVELOPMENT_NATIVE_PAYLOAD' "$OUT/candidate_integration.log" 2>/dev/null)"
kv junit_compare_rc "$RC_COMPARE"
kv same_test_counts "${SAME_COUNTS:-0}"
kv development_override_warning_count "${WARNINGS:-0}"

say 'POST-RUN CLEANLINESS'
git -C "$WT_BASE" status --porcelain >"$OUT/base_status.txt" 2>&1
git -C "$WT_CAND" status --porcelain >"$OUT/candidate_status.txt" 2>&1
RC_CLEAN=0
[ -s "$OUT/base_status.txt" ] && RC_CLEAN=1
[ -s "$OUT/candidate_status.txt" ] && RC_CLEAN=1
kv clean_worktrees "$([ "$RC_CLEAN" -eq 0 ] && printf true || printf false)"

say 'CLASSIFICATION'
CLASSIFICATION='FAIL_R5C_DEV_BEHAVIORAL_GATE'
if [ "$RC_FAIL_CLOSED" -eq 0 ] && [ "$RC_POLICY" -eq 0 ] && [ "$RC_BASE" -eq 0 ] && [ "$RC_CAND" -eq 0 ] && [ "${SAME_COUNTS:-0}" = '1' ] && [ "${WARNINGS:-0}" -gt 0 ] && [ "$RC_FOCUSED" -eq 0 ] && [ "$HASH_PASS" -eq 1 ] && [ "$RC_CLEAN" -eq 0 ]; then
  CLASSIFICATION='PASS_R5C_DEV_BEHAVIOR_ONLY_NO_PRODUCTION_PROVENANCE'
fi
kv classification "$CLASSIFICATION"
kv receipt_dir "$OUT"

export CLASSIFICATION BASE_COMMIT CANDIDATE_COMMIT WHEEL WHEEL_SHA RC_FAIL_CLOSED RC_POLICY RC_BASE RC_CAND RC_FOCUSED RC_CLEAN HASH_PASS H1 H2 GOLDEN_PAYLOAD_SHA256 SAME_COUNTS WARNINGS
"$PY" - <<'PY' >"$OUT/receipt_writer.log" 2>&1
import hashlib, json, os
from pathlib import Path
out=Path(os.environ['OUT'])
r={
 'schema_version':'1.0.0',
 'stage':'BASS_REC_SOURCE_R5C_DEV_BEHAVIORAL_BACKEND_GATE',
 'classification':os.environ['CLASSIFICATION'],
 'identity':{'base_commit':os.environ['BASE_COMMIT'],'candidate_commit':os.environ['CANDIDATE_COMMIT'],'local_wheel':os.environ['WHEEL'],'local_wheel_sha256':os.environ['WHEEL_SHA']},
 'return_codes':{'default_fail_closed':int(os.environ['RC_FAIL_CLOSED']),'policy_packaging':int(os.environ['RC_POLICY']),'base_integration_dev':int(os.environ['RC_BASE']),'candidate_integration_dev':int(os.environ['RC_CAND']),'focused':int(os.environ['RC_FOCUSED']),'cleanliness':int(os.environ['RC_CLEAN'])},
 'comparison':{'same_junit_counts':os.environ.get('SAME_COUNTS')=='1','development_override_warning_count':int(os.environ.get('WARNINGS','0'))},
 'payload_hash':{'run_1':os.environ.get('H1',''),'run_2':os.environ.get('H2',''),'golden':os.environ['GOLDEN_PAYLOAD_SHA256'],'pass':os.environ['HASH_PASS']=='1'},
 'claim_boundary':{'behavioral_regression_only':True,'production_native_provenance':False,'trusted_registry_modified':False,'source_integration':False,'grid_pstf_parity':False,'physical_face':False,'provider_export':False,'pass_rf04':False},
}
(out/'R5C_DEV_BEHAVIORAL_RECEIPT.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
lines=[]
for p in sorted(out.iterdir()):
    if p.is_file() and p.name!='SHA256SUMS': lines.append(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}')
(out/'SHA256SUMS').write_text('\n'.join(lines)+'\n')
PY

printf '\nCaller checkout unchanged. PASS is behavior-only, never production provenance.\n' | tee -a "$MASTER"
exit 0
