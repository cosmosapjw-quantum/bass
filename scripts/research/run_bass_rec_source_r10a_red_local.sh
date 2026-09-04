#!/usr/bin/env bash
# BASS_REC_SOURCE_R10A_PROJECTION_AUTHORITY_HARDENING_TDD_RED
#
# Execute the test-only R10A authority-hardening contract in a detached
# worktree.  The expected result is exactly 13 future-behaviour assertion
# failures, three passing controls, no errors/skips, and all 49 inherited
# R5/R6/R7/R9 tests still GREEN.
#
# The script writes its own classification and always returns shell status 0.

set +e
set +u
set +o pipefail 2>/dev/null || true

PARENT='662f682654f80281a4afd56a28be1ff0d535e2ac'
SOURCE_COMMIT='931ce2d4cd499bc388027c36a68c4b72b6c65d6e'
SOURCE_TREE='3889efcd37f6a30c2e2222856e17e8452c4a52b3'
BRANCH='research/bass-rec-source-r10a-projection-authority-hardening-red-20260904-r1'

SOURCE_AUTHORITY_BLOB='869677390004f68aef9f547e6556f5f1c15bd012'
SOURCE_ADAPTER_BLOB='8b00602fc76e1cd49ac5b43615c97a686b56f080'
SOURCE_PARITY_BLOB='a807191ff0baa6851ec7748826a7d4e34b400207'
R5_TEST_BLOB='db336d64633d8a9552bc3613c588a00f33404a4d'
R6_TEST_BLOB='49be9546c4655bc5ca330bc31ae2daf07578b74f'
R7_TEST_BLOB='d6fb316452a947d0f955dd4a115e8840688a2d02'
R9_TEST_BLOB='31e72e4075e973022650dd8f14cc8690c2c55673'
R10A_TEST_BLOB='de2f341ce04b4b061efbdab360525ef87996701d'

ROOT="${RECEIPT_ROOT:-$HOME/Dropbox/bianchi/_runtime_receipts}"
OUT="$ROOT/BASS_REC_SOURCE_R10A_RED_$(date -u +%Y%m%dT%H%M%SZ)"
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
  stop_gate STOP_R10A_FETCH_FAILURE \
    "fetch=$RC_FETCH publication=${PUBLICATION_HEAD:-MISSING}"
fi

git -C "$BASS" merge-base --is-ancestor "$SOURCE_COMMIT" "$PUBLICATION_HEAD" \
  >/dev/null 2>&1
[ "$?" -eq 0 ] || stop_gate STOP_R10A_SOURCE_NOT_PUBLICATION_ANCESTOR \
  "$PUBLICATION_HEAD"

TMP="$(mktemp -d /tmp/bass-r10a-red.XXXXXX 2>/dev/null)"
[ -d "$TMP" ] || stop_gate STOP_TEMP_DIRECTORY_FAILURE "$TMP"
WT="$TMP/worktree"

cleanup() {
  git -C "$BASS" worktree remove --force "$WT" >/dev/null 2>&1 || true
  case "$TMP" in
    /tmp/bass-r10a-red.*) rm -rf -- "$TMP" >/dev/null 2>&1 || true ;;
  esac
}
trap cleanup EXIT HUP INT TERM

git -C "$BASS" worktree add --detach "$WT" "$SOURCE_COMMIT" \
  >"$OUT/worktree.log" 2>&1
RC_WT=$?
[ "$RC_WT" -eq 0 ] || stop_gate STOP_R10A_WORKTREE_FAILURE "$RC_WT"

ACTUAL_COMMIT="$(git -C "$WT" rev-parse HEAD 2>/dev/null)"
ACTUAL_TREE="$(git -C "$WT" rev-parse HEAD^{tree} 2>/dev/null)"
AUTH_BLOB="$(git -C "$WT" hash-object bianchi/source_authority.py 2>/dev/null)"
ADAPTER_BLOB="$(git -C "$WT" hash-object bianchi/source_adapters.py 2>/dev/null)"
PARITY_BLOB="$(git -C "$WT" hash-object bianchi/source_parity.py 2>/dev/null)"
T5="$(git -C "$WT" hash-object tests/research/test_bass_rec_source_protocol_red.py 2>/dev/null)"
T6="$(git -C "$WT" hash-object tests/research/test_bass_rec_source_protocol_r6_red.py 2>/dev/null)"
T7="$(git -C "$WT" hash-object tests/research/test_bass_rec_source_r7_dual_adapter_red.py 2>/dev/null)"
T9="$(git -C "$WT" hash-object tests/research/test_bass_rec_source_r9_parity_red.py 2>/dev/null)"
T10A="$(git -C "$WT" hash-object tests/research/test_bass_rec_source_r10a_projection_authority_red.py 2>/dev/null)"

if [ "$ACTUAL_COMMIT" != "$SOURCE_COMMIT" ] || \
   [ "$ACTUAL_TREE" != "$SOURCE_TREE" ] || \
   [ "$AUTH_BLOB" != "$SOURCE_AUTHORITY_BLOB" ] || \
   [ "$ADAPTER_BLOB" != "$SOURCE_ADAPTER_BLOB" ] || \
   [ "$PARITY_BLOB" != "$SOURCE_PARITY_BLOB" ] || \
   [ "$T5" != "$R5_TEST_BLOB" ] || \
   [ "$T6" != "$R6_TEST_BLOB" ] || \
   [ "$T7" != "$R7_TEST_BLOB" ] || \
   [ "$T9" != "$R9_TEST_BLOB" ] || \
   [ "$T10A" != "$R10A_TEST_BLOB" ]; then
  stop_gate STOP_R10A_EXACT_IDENTITY_MISMATCH \
    "$ACTUAL_COMMIT $ACTUAL_TREE $AUTH_BLOB $ADAPTER_BLOB $PARITY_BLOB $T5 $T6 $T7 $T9 $T10A"
fi

git -C "$WT" diff --name-status "$PARENT" "$SOURCE_COMMIT" \
  >"$OUT/source_diff_name_status.txt" 2>&1
if [ "$(wc -l <"$OUT/source_diff_name_status.txt" | tr -d ' ')" != 1 ] || \
   ! grep -Fqx $'A\ttests/research/test_bass_rec_source_r10a_projection_authority_red.py' \
     "$OUT/source_diff_name_status.txt"; then
  stop_gate STOP_R10A_NOT_TEST_ONLY \
    "$(tr '\n' ';' <"$OUT/source_diff_name_status.txt")"
fi

(
  cd "$WT" || exit 97
  PYTHONPATH="$WT" "$PY" -m py_compile \
    bianchi/source_authority.py \
    bianchi/source_adapters.py \
    bianchi/source_parity.py \
    tests/research/test_bass_rec_source_r10a_projection_authority_red.py
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
    'tests.research.test_bass_rec_source_r9_parity_red',
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
    result.testsRun == 49 and not result.failures
    and not result.errors and not result.skipped
)
print(json.dumps(summary, indent=2, sort_keys=True))
print(stream.getvalue(), file=sys.stderr)
raise SystemExit(0 if summary['pass'] else 1)
PY
) >"$OUT/survivor_result.json" 2>"$OUT/survivor_verbose.log"
RC_SURVIVOR=$?

(
  cd "$WT" || exit 97
  PYTHONPATH="$WT" "$PY" - <<'PY'
import io
import json
import sys
import unittest

name = 'tests.research.test_bass_rec_source_r10a_projection_authority_red'
expected = {
    f'{name}.TestR10AProjectionAuthorityExpectedRed.test_01_stale_projection_hash_is_rejected_at_use',
    f'{name}.TestR10AProjectionAuthorityExpectedRed.test_02_same_length_weight_tampering_is_rejected_at_use',
    f'{name}.TestR10AProjectionAuthorityExpectedRed.test_03_basis_realization_mutation_invalidates_projection',
    f'{name}.TestR10AProjectionAuthorityExpectedRed.test_04_sample_layout_is_explicit',
    f'{name}.TestR10AProjectionAuthorityExpectedRed.test_05_semantic_and_realization_identities_are_separate',
    f'{name}.TestR10AProjectionAuthorityExpectedRed.test_06_basis_matrix_identity_is_explicit',
    f'{name}.TestR10AProjectionAuthorityExpectedRed.test_07_actual_unit_field_changes_contract_identity',
    f'{name}.TestR10AProjectionAuthorityExpectedRed.test_08_time_basis_and_divisor_change_contract_identity',
    f'{name}.TestR10AProjectionAuthorityExpectedRed.test_09_contract_constructor_is_factory_only',
    f'{name}.TestR10AProjectionAuthorityExpectedRed.test_10_report_constructor_is_factory_only',
    f'{name}.TestR10AProjectionAuthorityExpectedRed.test_11_scaled_tolerance_utilization_is_reported',
    f'{name}.TestR10AProjectionAuthorityExpectedRed.test_12_continuous_positivity_is_not_overclaimed',
    f'{name}.TestR10AProjectionAuthorityExpectedRed.test_13_rank_above_executed_certificate_fails_closed',
}
stream = io.StringIO()
suite = unittest.defaultTestLoader.loadTestsFromName(name)
result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
failures = {case.id() for case, _ in result.failures}
errors = {case.id() for case, _ in result.errors}
skipped = {case.id() for case, _ in result.skipped}
summary = {
    'suite': name,
    'tests_run': result.testsRun,
    'failures': sorted(failures),
    'errors': sorted(errors),
    'skipped': sorted(skipped),
    'expected_failures': sorted(expected),
    'passing_controls': result.testsRun - len(failures) - len(errors) - len(skipped),
}
summary['pass_expected_red'] = (
    result.testsRun == 16
    and failures == expected
    and not errors
    and not skipped
    and summary['passing_controls'] == 3
)
print(json.dumps(summary, indent=2, sort_keys=True))
print(stream.getvalue(), file=sys.stderr)
raise SystemExit(0 if summary['pass_expected_red'] else 1)
PY
) >"$OUT/r10a_expected_red_result.json" 2>"$OUT/r10a_expected_red_verbose.log"
RC_RED=$?

git -C "$WT" status --porcelain=v1 >"$OUT/git_status_after.txt" 2>&1
CLEAN=false
[ ! -s "$OUT/git_status_after.txt" ] && CLEAN=true

CLASSIFICATION='FAIL_R10A_EXPECTED_RED_GATE'
if [ "$RC_COMPILE" -eq 0 ] && \
   [ "$RC_SURVIVOR" -eq 0 ] && \
   [ "$RC_RED" -eq 0 ] && \
   [ "$CLEAN" = true ]; then
  CLASSIFICATION='PASS_EXPECTED_R10A_PROJECTION_AUTHORITY_HARDENING_RED'
fi

cat >"$OUT/R10A_EXPECTED_RED_RECEIPT.json" <<JSON
{
  "schema_version": "1.0.0",
  "stage_id": "BASS_REC_SOURCE_R10A_PROJECTION_AUTHORITY_HARDENING_TDD_RED",
  "classification": "$CLASSIFICATION",
  "publication_head": "$PUBLICATION_HEAD",
  "parent": "$PARENT",
  "source_commit": "$SOURCE_COMMIT",
  "source_tree": "$SOURCE_TREE",
  "source_parity_blob": "$PARITY_BLOB",
  "r10a_test_blob": "$T10A",
  "python": "$PYVER",
  "compile_rc": $RC_COMPILE,
  "survivor_49_rc": $RC_SURVIVOR,
  "r10a_expected_red_rc": $RC_RED,
  "expected_tests": 16,
  "expected_assertion_failures": 13,
  "expected_passing_controls": 3,
  "expected_errors": 0,
  "expected_skips": 0,
  "test_only_diff": true,
  "clean_worktree": $CLEAN
}
JSON

cat >"$OUT/summary.txt" <<TXT
classification=$CLASSIFICATION
publication_head=$PUBLICATION_HEAD
parent=$PARENT
source_commit=$SOURCE_COMMIT
source_tree=$SOURCE_TREE
source_authority_blob=$AUTH_BLOB
source_adapter_blob=$ADAPTER_BLOB
source_parity_blob=$PARITY_BLOB
r10a_test_blob=$T10A
python=$PYVER
compile_rc=$RC_COMPILE
survivor_49_rc=$RC_SURVIVOR
r10a_expected_red_rc=$RC_RED
expected_tests=16
expected_assertion_failures=13
expected_passing_controls=3
expected_errors=0
expected_skips=0
test_only_diff=true
clean_worktree=$CLEAN
receipt_dir=$OUT
TXT

find "$OUT" -maxdepth 1 -type f ! -name SHA256SUMS -print0 \
  | sort -z \
  | xargs -0 sha256sum >"$OUT/SHA256SUMS" 2>/dev/null || true
cat "$OUT/summary.txt"
printf '\nCaller checkout was not switched or modified.\n'
exit 0
