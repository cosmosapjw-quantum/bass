#!/usr/bin/env bash
# BASS_REC_SOURCE_R7_LOCAL_EXPECTED_RED_REPLAY
#
# Runs the test-only R7 contract in a detached worktree. It accepts only the
# exact fingerprint 12 run / 10 assertion failures / 0 errors / 2 controls,
# while the R5+R6 survivor suites remain green. The caller checkout is never
# switched or modified. The script records its own classification and exits 0.

set +e
set +u
set +o pipefail 2>/dev/null || true

BRANCH='research/bass-rec-source-r7-dual-adapter-red-20260904-r1'
EXPECTED_PARENT='6ffbcceb660896f29d569533f0349c8ebaafbbe1'
EXPECTED_SOURCE_BLOB='869677390004f68aef9f547e6556f5f1c15bd012'
EXPECTED_R5_BLOB='db336d64633d8a9552bc3613c588a00f33404a4d'
EXPECTED_R6_BLOB='49be9546c4655bc5ca330bc31ae2daf07578b74f'
EXPECTED_R7_BLOB='d6fb316452a947d0f955dd4a115e8840688a2d02'

ROOT="${RECEIPT_ROOT:-$HOME/Dropbox/bianchi/_runtime_receipts}"
OUT="$ROOT/BASS_REC_SOURCE_R7_RED_$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$OUT" 2>/dev/null

stop_gate() {
  printf 'classification=%s\ndetail=%s\nreceipt_dir=%s\n' \
    "$1" "$2" "$OUT" | tee "$OUT/summary.txt"
  exit 0
}

[ -d "$OUT" ] || {
  printf 'classification=STOP_RECEIPT_DIRECTORY_UNAVAILABLE\n'
  exit 0
}

BASS="${BASS_REPO:-$HOME/Dropbox/bianchi/bass}"
ORIGIN="$(git -C "$BASS" config --get remote.origin.url 2>/dev/null)"
case "$ORIGIN" in
  *cosmosapjw-quantum/bass|*cosmosapjw-quantum/bass.git) ;;
  *) stop_gate STOP_WRONG_OR_MISSING_BASS_REPOSITORY "$ORIGIN" ;;
esac

PY="${PYTHON:-$(command -v python3.12 2>/dev/null)}"
[ -x "$PY" ] || PY="$(command -v python 2>/dev/null)"
[ -x "$PY" ] || stop_gate STOP_PYTHON_NOT_FOUND 'Python 3.12 is required'

PYVER="$($PY -c 'import sys; print(".".join(map(str, sys.version_info[:3])))' 2>/dev/null)"
case "$PYVER" in
  3.12.*) ;;
  *) stop_gate STOP_WRONG_PYTHON_VERSION "$PYVER" ;;
esac

git -C "$BASS" fetch --no-tags origin \
  "$BRANCH:refs/remotes/origin/$BRANCH" >"$OUT/fetch.log" 2>&1
RC_FETCH=$?
PUB="$(git -C "$BASS" rev-parse "refs/remotes/origin/$BRANCH" 2>/dev/null)"

if [ "$RC_FETCH" -ne 0 ] || [ -z "$PUB" ]; then
  stop_gate STOP_R7_FETCH_FAILURE "publication branch unavailable"
fi

git -C "$BASS" merge-base --is-ancestor "$EXPECTED_PARENT" "$PUB" \
  >/dev/null 2>&1
if [ "$?" -ne 0 ]; then
  stop_gate STOP_R7_PARENT_ANCESTRY "$PUB"
fi

TMP="$(mktemp -d /tmp/bass-r7-red.XXXXXX 2>/dev/null)"
[ -d "$TMP" ] || stop_gate STOP_R7_TEMP_DIRECTORY_FAILURE "$TMP"
WT="$TMP/worktree"

cleanup() {
  git -C "$BASS" worktree remove --force "$WT" >/dev/null 2>&1 || true
  case "$TMP" in
    /tmp/bass-r7-red.*) rm -rf -- "$TMP" >/dev/null 2>&1 || true ;;
  esac
}
trap cleanup EXIT HUP INT TERM

git -C "$BASS" worktree add --detach "$WT" "$PUB" \
  >"$OUT/worktree.log" 2>&1
RC_WT=$?
[ "$RC_WT" -eq 0 ] || stop_gate STOP_R7_WORKTREE_FAILURE "$RC_WT"

SOURCE_BLOB="$(git -C "$WT" hash-object bianchi/source_authority.py 2>/dev/null)"
R5_BLOB="$(git -C "$WT" hash-object tests/research/test_bass_rec_source_protocol_red.py 2>/dev/null)"
R6_BLOB="$(git -C "$WT" hash-object tests/research/test_bass_rec_source_protocol_r6_red.py 2>/dev/null)"
R7_BLOB="$(git -C "$WT" hash-object tests/research/test_bass_rec_source_r7_dual_adapter_red.py 2>/dev/null)"

if [ "$SOURCE_BLOB" != "$EXPECTED_SOURCE_BLOB" ] || \
   [ "$R5_BLOB" != "$EXPECTED_R5_BLOB" ] || \
   [ "$R6_BLOB" != "$EXPECTED_R6_BLOB" ] || \
   [ "$R7_BLOB" != "$EXPECTED_R7_BLOB" ]; then
  stop_gate STOP_R7_EXACT_BLOB_IDENTITY \
    "$SOURCE_BLOB $R5_BLOB $R6_BLOB $R7_BLOB"
fi

if git -C "$WT" cat-file -e "$PUB:bianchi/source_adapters.py" 2>/dev/null; then
  stop_gate STOP_R7_PRODUCTION_ADAPTER_ALREADY_PRESENT "$PUB"
fi

(
  cd "$WT" || exit 97
  PYTHONPATH="$WT" "$PY" -m py_compile \
    bianchi/source_authority.py \
    tests/research/test_bass_rec_source_r7_dual_adapter_red.py
) >"$OUT/py_compile.log" 2>&1
RC_COMPILE=$?

(
  cd "$WT" || exit 97
  PYTHONPATH="$WT" "$PY" - <<'PY'
import io
import json
import sys
import unittest

names = [
    'tests.research.test_bass_rec_source_protocol_red',
    'tests.research.test_bass_rec_source_protocol_r6_red',
]
stream = io.StringIO()
suite = unittest.TestSuite(
    unittest.defaultTestLoader.loadTestsFromName(name) for name in names
)
result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
summary = {
    'suites': names,
    'tests_run': result.testsRun,
    'failures': [case.id() for case, _ in result.failures],
    'errors': [case.id() for case, _ in result.errors],
    'skipped': [case.id() for case, _ in result.skipped],
}
summary['pass'] = (
    result.testsRun == 21
    and not result.failures
    and not result.errors
    and not result.skipped
)
print(json.dumps(summary, indent=2, sort_keys=True))
print(stream.getvalue(), file=sys.stderr)
raise SystemExit(0 if summary['pass'] else 1)
PY
) >"$OUT/r5_r6_result.json" 2>"$OUT/r5_r6_verbose.log"
RC_SURVIVORS=$?

(
  cd "$WT" || exit 97
  PYTHONPATH="$WT" "$PY" - <<'PY'
import io
import json
import sys
import unittest

name = 'tests.research.test_bass_rec_source_r7_dual_adapter_red'
stream = io.StringIO()
suite = unittest.defaultTestLoader.loadTestsFromName(name)
result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
failed = sorted(case.id() for case, _ in result.failures)
errors = sorted(case.id() for case, _ in result.errors)
skipped = sorted(case.id() for case, _ in result.skipped)
passing = result.testsRun - len(failed) - len(errors) - len(skipped)
summary = {
    'suite': name,
    'tests_run': result.testsRun,
    'failures': failed,
    'errors': errors,
    'skipped': skipped,
    'passing_controls': passing,
    'expected': {
        'tests_run': 12,
        'assertion_failures': 10,
        'errors': 0,
        'skipped': 0,
        'passing_controls': 2,
    },
}
summary['pass_expected_red'] = (
    result.testsRun == 12
    and len(failed) == 10
    and not errors
    and not skipped
    and passing == 2
)
print(json.dumps(summary, indent=2, sort_keys=True))
print(stream.getvalue(), file=sys.stderr)
raise SystemExit(0 if summary['pass_expected_red'] else 1)
PY
) >"$OUT/r7_result.json" 2>"$OUT/r7_verbose.log"
RC_EXPECTED_RED=$?

git -C "$WT" status --porcelain >"$OUT/git_status_after.txt" 2>&1
if [ -s "$OUT/git_status_after.txt" ]; then
  CLEAN=false
else
  CLEAN=true
fi

CLASS='FAIL_R7_EXPECTED_RED_FINGERPRINT'
if [ "$RC_COMPILE" -eq 0 ] && \
   [ "$RC_SURVIVORS" -eq 0 ] && \
   [ "$RC_EXPECTED_RED" -eq 0 ] && \
   [ "$CLEAN" = true ]; then
  CLASS='PASS_EXPECTED_R7_FULL_GRID_SPECTRAL_PSTF_ADAPTER_RED'
fi

cat >"$OUT/summary.txt" <<EOF
classification=$CLASS
publication_head=$PUB
expected_parent=$EXPECTED_PARENT
source_blob=$SOURCE_BLOB
r5_test_blob=$R5_BLOB
r6_test_blob=$R6_BLOB
r7_test_blob=$R7_BLOB
python=$PYVER
compile_rc=$RC_COMPILE
r5_r6_survivor_rc=$RC_SURVIVORS
r7_expected_red_rc=$RC_EXPECTED_RED
production_adapter_absent=true
clean_worktree=$CLEAN
receipt_dir=$OUT
EOF

cat "$OUT/summary.txt"
sha256sum "$OUT"/* >"$OUT/SHA256SUMS" 2>/dev/null || true
printf '\nCaller checkout was not switched or modified.\n'
exit 0
