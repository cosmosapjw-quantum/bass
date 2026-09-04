#!/usr/bin/env bash
# BASS_REC_SOURCE_R9_LOCAL_EXPECTED_RED_REPLAY
#
# Verifies the exact test-only R9 source commit in a detached worktree.
# R5/R6/R7 must remain green. R9 is accepted only when the future parity
# module is absent and the new suite produces exactly 14 assertion failures,
# 0 errors, 0 skips, and 2 passing controls.
#
# The caller checkout is never switched or modified. The runner always exits
# with shell status zero after writing its own machine-readable classification.

set +e
set +u
set +o pipefail 2>/dev/null || true

PARENT='5a7084e9f8fb4ac702ae1301d18cc91ea8e7ca06'
SOURCE_COMMIT='50652295bb4ed3514cad7f9a392b27a1ab866093'
SOURCE_TREE='890b96be954962e9c300e14165d8a593c9e4104d'
BRANCH='research/bass-rec-source-r9-grid-pstf-parity-red-20260904-r1'

SOURCE_AUTHORITY_BLOB='869677390004f68aef9f547e6556f5f1c15bd012'
SOURCE_ADAPTER_BLOB='8b00602fc76e1cd49ac5b43615c97a686b56f080'
R5_TEST_BLOB='db336d64633d8a9552bc3613c588a00f33404a4d'
R6_TEST_BLOB='49be9546c4655bc5ca330bc31ae2daf07578b74f'
R7_TEST_BLOB='d6fb316452a947d0f955dd4a115e8840688a2d02'
R9_TEST_BLOB='31e72e4075e973022650dd8f14cc8690c2c55673'

ROOT="${RECEIPT_ROOT:-$HOME/Dropbox/bianchi/_runtime_receipts}"
OUT="$ROOT/BASS_REC_SOURCE_R9_RED_$(date -u +%Y%m%dT%H%M%SZ)"
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

find_bass() {
  for candidate in \
    "${BASS_REPO:-}" \
    "$HOME/Dropbox/bianchi/bass" \
    "$HOME/Dropbox/bass" \
    "$HOME/bass"
  do
    [ -n "$candidate" ] || continue
    top="$(git -C "$candidate" rev-parse --show-toplevel 2>/dev/null)"
    [ -n "$top" ] || continue
    origin="$(git -C "$top" config --get remote.origin.url 2>/dev/null)"
    case "$origin" in
      *cosmosapjw-quantum/bass|*cosmosapjw-quantum/bass.git)
        printf '%s\n' "$top"
        return 0
        ;;
    esac
  done
  return 1
}

BASS="$(find_bass)"
[ -n "$BASS" ] || stop_gate STOP_BASS_REPOSITORY_NOT_FOUND \
  'Set BASS_REPO=/absolute/path/to/bass and rerun.'

PY="${PYTHON:-$(command -v python3.12 2>/dev/null)}"
[ -x "$PY" ] || PY="$(command -v python 2>/dev/null)"
[ -x "$PY" ] || stop_gate STOP_PYTHON_NOT_FOUND 'Python is required.'
PYVER="$($PY -c 'import sys; print(".".join(map(str,sys.version_info[:3])))' 2>/dev/null)"

git -C "$BASS" fetch --no-tags origin \
  "$BRANCH:refs/remotes/origin/$BRANCH" >"$OUT/fetch.log" 2>&1
RC_FETCH=$?
PUBLICATION_HEAD="$(git -C "$BASS" rev-parse "refs/remotes/origin/$BRANCH" 2>/dev/null)"
if [ "$RC_FETCH" -ne 0 ] || [ -z "$PUBLICATION_HEAD" ]; then
  stop_gate STOP_R9_FETCH_FAILURE \
    "fetch=$RC_FETCH publication=${PUBLICATION_HEAD:-MISSING}"
fi

git -C "$BASS" merge-base --is-ancestor "$SOURCE_COMMIT" "$PUBLICATION_HEAD" \
  >/dev/null 2>&1
[ "$?" -eq 0 ] || stop_gate STOP_R9_SOURCE_NOT_PUBLICATION_ANCESTOR \
  "$PUBLICATION_HEAD"

TMP="$(mktemp -d /tmp/bass-r9-red.XXXXXX 2>/dev/null)"
[ -d "$TMP" ] || stop_gate STOP_TEMP_DIRECTORY_FAILURE "$TMP"
WT="$TMP/worktree"

cleanup() {
  git -C "$BASS" worktree remove --force "$WT" >/dev/null 2>&1 || true
  case "$TMP" in
    /tmp/bass-r9-red.*) rm -rf -- "$TMP" >/dev/null 2>&1 || true ;;
  esac
}
trap cleanup EXIT HUP INT TERM

git -C "$BASS" worktree add --detach "$WT" "$SOURCE_COMMIT" \
  >"$OUT/worktree.log" 2>&1
RC_WT=$?
[ "$RC_WT" -eq 0 ] || stop_gate STOP_R9_WORKTREE_FAILURE "$RC_WT"

ACTUAL_COMMIT="$(git -C "$WT" rev-parse HEAD 2>/dev/null)"
ACTUAL_TREE="$(git -C "$WT" rev-parse HEAD^{tree} 2>/dev/null)"
AUTH_BLOB="$(git -C "$WT" hash-object bianchi/source_authority.py 2>/dev/null)"
ADAPTER_BLOB="$(git -C "$WT" hash-object bianchi/source_adapters.py 2>/dev/null)"
T5="$(git -C "$WT" hash-object tests/research/test_bass_rec_source_protocol_red.py 2>/dev/null)"
T6="$(git -C "$WT" hash-object tests/research/test_bass_rec_source_protocol_r6_red.py 2>/dev/null)"
T7="$(git -C "$WT" hash-object tests/research/test_bass_rec_source_r7_dual_adapter_red.py 2>/dev/null)"
T9="$(git -C "$WT" hash-object tests/research/test_bass_rec_source_r9_parity_red.py 2>/dev/null)"

if [ "$ACTUAL_COMMIT" != "$SOURCE_COMMIT" ] || \
   [ "$ACTUAL_TREE" != "$SOURCE_TREE" ] || \
   [ "$AUTH_BLOB" != "$SOURCE_AUTHORITY_BLOB" ] || \
   [ "$ADAPTER_BLOB" != "$SOURCE_ADAPTER_BLOB" ] || \
   [ "$T5" != "$R5_TEST_BLOB" ] || \
   [ "$T6" != "$R6_TEST_BLOB" ] || \
   [ "$T7" != "$R7_TEST_BLOB" ] || \
   [ "$T9" != "$R9_TEST_BLOB" ]; then
  stop_gate STOP_R9_EXACT_IDENTITY_MISMATCH \
    "$ACTUAL_COMMIT $ACTUAL_TREE $AUTH_BLOB $ADAPTER_BLOB $T5 $T6 $T7 $T9"
fi

git -C "$WT" diff --name-status "$PARENT" "$SOURCE_COMMIT" \
  >"$OUT/source_diff_name_status.txt" 2>&1
if [ "$(wc -l <"$OUT/source_diff_name_status.txt" | tr -d ' ')" != 1 ] || \
   ! grep -Fqx $'A\ttests/research/test_bass_rec_source_r9_parity_red.py' \
      "$OUT/source_diff_name_status.txt"; then
  stop_gate STOP_R9_UNBOUNDED_TEST_SOURCE_DIFF \
    "$(tr '\n' ';' <"$OUT/source_diff_name_status.txt")"
fi

PARITY_MODULE_ABSENT=false
if ! git -C "$WT" cat-file -e "$SOURCE_COMMIT:bianchi/source_parity.py" \
  2>/dev/null; then
  PARITY_MODULE_ABSENT=true
fi

(
  cd "$WT" || exit 97
  PYTHONPATH="$WT" "$PY" -m py_compile \
    bianchi/source_authority.py \
    bianchi/source_adapters.py \
    tests/research/test_bass_rec_source_r9_parity_red.py
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
    'tests.research.test_bass_rec_source_r7_dual_adapter_red',
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
    result.testsRun == 33 and not result.failures
    and not result.errors and not result.skipped
)
print(json.dumps(summary, indent=2, sort_keys=True))
print(stream.getvalue(), file=sys.stderr)
raise SystemExit(0 if summary['pass'] else 1)
PY
) >"$OUT/survivor_result.json" 2>"$OUT/survivor_verbose.log"
RC_SURVIVORS=$?

(
  cd "$WT" || exit 97
  PYTHONPATH="$WT" "$PY" - <<'PY'
import io
import json
import sys
import unittest
name = 'tests.research.test_bass_rec_source_r9_parity_red'
stream = io.StringIO()
suite = unittest.defaultTestLoader.loadTestsFromName(name)
result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
failures = sorted(case.id() for case, _ in result.failures)
errors = sorted(case.id() for case, _ in result.errors)
skipped = sorted(case.id() for case, _ in result.skipped)
controls = result.testsRun - len(failures) - len(errors) - len(skipped)
summary = {
    'suite': name,
    'tests_run': result.testsRun,
    'failures': failures,
    'errors': errors,
    'skipped': skipped,
    'passing_controls': controls,
    'expected': {
        'tests_run': 16,
        'failures': 14,
        'errors': 0,
        'skipped': 0,
        'passing_controls': 2,
    },
}
summary['pass_expected_red'] = (
    result.testsRun == 16 and len(failures) == 14
    and not errors and not skipped and controls == 2
)
print(json.dumps(summary, indent=2, sort_keys=True))
print(stream.getvalue(), file=sys.stderr)
raise SystemExit(0 if summary['pass_expected_red'] else 1)
PY
) >"$OUT/r9_result.json" 2>"$OUT/r9_verbose.log"
RC_R9_EXPECTED=$?

git -C "$WT" status --porcelain=v1 --untracked-files=all \
  >"$OUT/git_status_after.txt"
CLEAN=false
[ ! -s "$OUT/git_status_after.txt" ] && CLEAN=true

CLASSIFICATION='FAIL_R9_EXPECTED_RED_FINGERPRINT'
if [ "$RC_COMPILE" -eq 0 ] && \
   [ "$RC_SURVIVORS" -eq 0 ] && \
   [ "$RC_R9_EXPECTED" -eq 0 ] && \
   [ "$PARITY_MODULE_ABSENT" = true ] && \
   [ "$CLEAN" = true ]; then
  CLASSIFICATION='PASS_EXPECTED_R9_FINITE_RANK_GRID_PSTF_PARITY_RED'
fi

cat >"$OUT/summary.txt" <<EOF
classification=$CLASSIFICATION
publication_head=$PUBLICATION_HEAD
parent=$PARENT
source_commit=$ACTUAL_COMMIT
source_tree=$ACTUAL_TREE
source_authority_blob=$AUTH_BLOB
source_adapter_blob=$ADAPTER_BLOB
r5_test_blob=$T5
r6_test_blob=$T6
r7_test_blob=$T7
r9_test_blob=$T9
python=$PYVER
compile_rc=$RC_COMPILE
survivor_33_rc=$RC_SURVIVORS
r9_expected_red_rc=$RC_R9_EXPECTED
parity_module_absent=$PARITY_MODULE_ABSENT
clean_worktree=$CLEAN
receipt_dir=$OUT
EOF
cat "$OUT/summary.txt"

cat >"$OUT/R9_EXPECTED_RED_RECEIPT.json" <<EOF
{
  "schema_version": "1.0.0",
  "stage_id": "BASS_REC_SOURCE_R9_FINITE_RANK_GRID_PSTF_PARITY_RED",
  "classification": "$CLASSIFICATION",
  "publication_head": "$PUBLICATION_HEAD",
  "source_commit": "$ACTUAL_COMMIT",
  "source_tree": "$ACTUAL_TREE",
  "compile_rc": $RC_COMPILE,
  "survivor_33_rc": $RC_SURVIVORS,
  "r9_expected_red_rc": $RC_R9_EXPECTED,
  "parity_module_absent": $PARITY_MODULE_ABSENT,
  "clean_worktree": $CLEAN,
  "expected_fingerprint": {
    "tests_run": 16,
    "assertion_failures": 14,
    "errors": 0,
    "skipped": 0,
    "passing_controls": 2
  },
  "claim_boundary": {
    "finite_rank_nonaxisymmetric_parity": false,
    "anisotropic_source_product": false,
    "physical_rec_source_wiring": false,
    "integrated_state_closure": false,
    "polarized_source_parity": false,
    "physical_face": false,
    "provider_export": false
  }
}
EOF

sha256sum "$OUT"/* >"$OUT/SHA256SUMS" 2>/dev/null || true
printf '\nCaller checkout was not switched or modified.\n'
exit 0
