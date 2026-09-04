#!/usr/bin/env bash
# BASS_REC_SOURCE_R8B_TRUSTED_NATIVE_PARENT_CANDIDATE_NONREGRESSION
#
# Compare the exact R7 parent and R8 production source under the same admitted
# RF-00 native payload, with the development override absent. Root-package
# builds occur only in non-Git staging directories; detached source worktrees
# are reserved for identity checks and tests and must remain clean.
#
# The caller checkout is never switched or modified. The script records a
# machine-readable classification and always exits with shell status zero.

set +e
set +u
set +o pipefail 2>/dev/null || true
unset BASS_ALLOW_UNVERIFIED_NATIVE_DEV

PARENT='4431edef61351bfba49a5781db3005d4a0308d05'
PARENT_TREE='28fb517990b9f7935b30f3fd8a4aa0f182c907f3'
CANDIDATE='ed630f3b8b02531af0f392b722e6636c14a41864'
CANDIDATE_TREE='a5617a552bb2f6e65b78979bedde23543b9f9506'
BRANCH='research/bass-rec-source-r8-dual-adapter-green-20260904-r1'

SOURCE_AUTHORITY_BLOB='869677390004f68aef9f547e6556f5f1c15bd012'
SOURCE_ADAPTER_BLOB='8b00602fc76e1cd49ac5b43615c97a686b56f080'
R5_TEST_BLOB='db336d64633d8a9552bc3613c588a00f33404a4d'
R6_TEST_BLOB='49be9546c4655bc5ca330bc31ae2daf07578b74f'
R7_TEST_BLOB='d6fb316452a947d0f955dd4a115e8840688a2d02'

TRUSTED_BRANCH='agent/architecture/rf04-scalar-raw-20260829-fhxMnS'
TRUSTED_COMMIT='50b6e9f7a6741b7fd25b0421d2a674b9eb92cdda'
TRUSTED_WHEEL_PATH='artifacts/rust_first_runtime/rf04/scalar_raw/native_delta/rf02c-wheel/bianchi_rustcore-0.1.0-cp312-cp312-manylinux_2_34_x86_64.whl'
TRUSTED_RESTORE_PATH='artifacts/rust_first_runtime/rf04/scalar_raw/native_delta/RF02C_NATIVE_RESTORE.json'
TRUSTED_WHEEL_SHA='99bd0596642dd31ca82080fb24306cd9bf3f6dd1ad3f68a1380f77378e266302'
TRUSTED_SO_SHA='5d5b8197518d8637b14e0c78b871802ed64f6506c7a95128f31bd52044a98633'

SOURCE_PAYLOAD_SHA='7f0db7e1cf7423ff6751a21ab4002ef8f13d89f788a8a746b26992abecf791e8'
INTEGRATED_BINDING_SHA='54762aa915b3fa0da847676a3d4491b8f7f2f358e48dd275fffee84ba6496093'
GRID_OUTPUT_SHA='cb11368e2f440ad244c6b486fa07831ab5aa9d2f31628f54047fb92ade5c77f7'
PSTF_OUTPUT_SHA='7bdffbae76a7da1ab94241d13ae6149403e187d0011dd7cb5ef700028c88f28a'
CHANGED_PROJECTION_SHA='b85309a770f17ea90e83299b09945692796529410fdb3f1a7463289d17aa1229'
EXPECTED_BACKEND_TESTS=54
EXPECTED_FOCUSED_TESTS=33

STAMP="$(date -u +%Y%m%dT%H%M%SZ 2>/dev/null)"
[ -n "$STAMP" ] || STAMP='UNKNOWN_TIME'
ROOT="${RECEIPT_ROOT:-$HOME/Dropbox/bianchi/_runtime_receipts}"
OUT="$ROOT/BASS_REC_SOURCE_R8B_$STAMP"
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
BASS_ORIGIN="$(git -C "$BASS" config --get remote.origin.url 2>/dev/null)"

PYBOOT="${PYTHON_BOOTSTRAP:-$(command -v python3.12 2>/dev/null)}"
[ -x "$PYBOOT" ] || PYBOOT="$(command -v python 2>/dev/null)"
[ -x "$PYBOOT" ] || stop_gate STOP_PYTHON_NOT_FOUND 'Python 3.12 is required.'
PYVER="$($PYBOOT -c 'import sys; print(".".join(map(str,sys.version_info[:3])))' 2>/dev/null)"
case "$PYVER" in
  3.12.*) ;;
  *) stop_gate STOP_PYTHON_3_12_REQUIRED "$PYVER" ;;
esac

git -C "$BASS" fetch --no-tags origin \
  "$BRANCH:refs/remotes/origin/$BRANCH" \
  "$TRUSTED_BRANCH:refs/remotes/origin/$TRUSTED_BRANCH" \
  >"$OUT/fetch.log" 2>&1
RC_FETCH=$?
PUBLICATION_HEAD="$(git -C "$BASS" rev-parse "refs/remotes/origin/$BRANCH" 2>/dev/null)"
TRUSTED_HEAD="$(git -C "$BASS" rev-parse "refs/remotes/origin/$TRUSTED_BRANCH" 2>/dev/null)"
if [ "$RC_FETCH" -ne 0 ] || [ -z "$PUBLICATION_HEAD" ] || \
   [ "$TRUSTED_HEAD" != "$TRUSTED_COMMIT" ]; then
  stop_gate STOP_REMOTE_IDENTITY_MISMATCH \
    "fetch=$RC_FETCH publication=${PUBLICATION_HEAD:-MISSING} trusted=${TRUSTED_HEAD:-MISSING}"
fi

git -C "$BASS" merge-base --is-ancestor "$CANDIDATE" "$PUBLICATION_HEAD" \
  >/dev/null 2>&1
[ "$?" -eq 0 ] || stop_gate STOP_R8_SOURCE_NOT_PUBLICATION_ANCESTOR "$PUBLICATION_HEAD"

TMP="$(mktemp -d /tmp/bass-r8b.XXXXXX 2>/dev/null)"
[ -d "$TMP" ] || stop_gate STOP_TEMP_DIRECTORY_FAILURE "$TMP"
WORKTREE_PARENT="$TMP/worktree-parent"
WORKTREE_CANDIDATE="$TMP/worktree-candidate"
STAGE_PARENT="$TMP/stage-parent"
STAGE_CANDIDATE="$TMP/stage-candidate"
VENV_PARENT="$TMP/venv-parent"
VENV_CANDIDATE="$TMP/venv-candidate"

cleanup() {
  git -C "$BASS" worktree remove --force "$WORKTREE_PARENT" >/dev/null 2>&1 || true
  git -C "$BASS" worktree remove --force "$WORKTREE_CANDIDATE" >/dev/null 2>&1 || true
  case "$TMP" in
    /tmp/bass-r8b.*) rm -rf -- "$TMP" >/dev/null 2>&1 || true ;;
  esac
}
trap cleanup EXIT HUP INT TERM

git -C "$BASS" worktree add --detach "$WORKTREE_PARENT" "$PARENT" \
  >"$OUT/worktree_parent.log" 2>&1
RC_WT_PARENT=$?
git -C "$BASS" worktree add --detach "$WORKTREE_CANDIDATE" "$CANDIDATE" \
  >"$OUT/worktree_candidate.log" 2>&1
RC_WT_CANDIDATE=$?
if [ "$RC_WT_PARENT" -ne 0 ] || [ "$RC_WT_CANDIDATE" -ne 0 ]; then
  stop_gate STOP_WORKTREE_FAILURE \
    "parent=$RC_WT_PARENT candidate=$RC_WT_CANDIDATE"
fi

ACTUAL_PARENT_TREE="$(git -C "$WORKTREE_PARENT" rev-parse HEAD^{tree} 2>/dev/null)"
ACTUAL_CANDIDATE_TREE="$(git -C "$WORKTREE_CANDIDATE" rev-parse HEAD^{tree} 2>/dev/null)"
PARENT_AUTH_BLOB="$(git -C "$WORKTREE_PARENT" hash-object bianchi/source_authority.py 2>/dev/null)"
CANDIDATE_AUTH_BLOB="$(git -C "$WORKTREE_CANDIDATE" hash-object bianchi/source_authority.py 2>/dev/null)"
CANDIDATE_ADAPTER_BLOB="$(git -C "$WORKTREE_CANDIDATE" hash-object bianchi/source_adapters.py 2>/dev/null)"
T5="$(git -C "$WORKTREE_CANDIDATE" hash-object tests/research/test_bass_rec_source_protocol_red.py 2>/dev/null)"
T6="$(git -C "$WORKTREE_CANDIDATE" hash-object tests/research/test_bass_rec_source_protocol_r6_red.py 2>/dev/null)"
T7="$(git -C "$WORKTREE_CANDIDATE" hash-object tests/research/test_bass_rec_source_r7_dual_adapter_red.py 2>/dev/null)"

if [ "$ACTUAL_PARENT_TREE" != "$PARENT_TREE" ] || \
   [ "$ACTUAL_CANDIDATE_TREE" != "$CANDIDATE_TREE" ] || \
   [ "$PARENT_AUTH_BLOB" != "$SOURCE_AUTHORITY_BLOB" ] || \
   [ "$CANDIDATE_AUTH_BLOB" != "$SOURCE_AUTHORITY_BLOB" ] || \
   [ "$CANDIDATE_ADAPTER_BLOB" != "$SOURCE_ADAPTER_BLOB" ] || \
   [ "$T5" != "$R5_TEST_BLOB" ] || \
   [ "$T6" != "$R6_TEST_BLOB" ] || \
   [ "$T7" != "$R7_TEST_BLOB" ]; then
  stop_gate STOP_EXACT_SOURCE_IDENTITY_MISMATCH \
    "$ACTUAL_PARENT_TREE $ACTUAL_CANDIDATE_TREE $PARENT_AUTH_BLOB $CANDIDATE_AUTH_BLOB $CANDIDATE_ADAPTER_BLOB $T5 $T6 $T7"
fi

if git -C "$WORKTREE_PARENT" cat-file -e "$PARENT:bianchi/source_adapters.py" 2>/dev/null; then
  stop_gate STOP_PARENT_ALREADY_CONTAINS_R8_ADAPTER "$PARENT"
fi

git -C "$BASS" diff --name-status "$PARENT" "$CANDIDATE" \
  >"$OUT/source_diff_name_status.txt" 2>&1
DIFF_LINES="$(wc -l <"$OUT/source_diff_name_status.txt" 2>/dev/null | tr -d ' ')"
if [ "$DIFF_LINES" != 1 ] || \
   ! grep -Fqx $'A\tbianchi/source_adapters.py' "$OUT/source_diff_name_status.txt"; then
  stop_gate STOP_R8_UNBOUNDED_SOURCE_DIFF \
    "expected only A bianchi/source_adapters.py; observed $(tr '\n' ';' <"$OUT/source_diff_name_status.txt")"
fi

PARENT_RUST_TREE="$(git -C "$WORKTREE_PARENT" rev-parse HEAD:_rustcore 2>/dev/null)"
CANDIDATE_RUST_TREE="$(git -C "$WORKTREE_CANDIDATE" rev-parse HEAD:_rustcore 2>/dev/null)"
PARENT_LOCK_BLOB="$(git -C "$WORKTREE_PARENT" rev-parse HEAD:requirements.lock 2>/dev/null)"
CANDIDATE_LOCK_BLOB="$(git -C "$WORKTREE_CANDIDATE" rev-parse HEAD:requirements.lock 2>/dev/null)"
PARENT_PROJECT_BLOB="$(git -C "$WORKTREE_PARENT" rev-parse HEAD:pyproject.toml 2>/dev/null)"
CANDIDATE_PROJECT_BLOB="$(git -C "$WORKTREE_CANDIDATE" rev-parse HEAD:pyproject.toml 2>/dev/null)"
if [ "$PARENT_RUST_TREE" != "$CANDIDATE_RUST_TREE" ] || \
   [ "$PARENT_LOCK_BLOB" != "$CANDIDATE_LOCK_BLOB" ] || \
   [ "$PARENT_PROJECT_BLOB" != "$CANDIDATE_PROJECT_BLOB" ]; then
  stop_gate STOP_DIFFERENTIAL_ENVIRONMENT_INPUT_DRIFT \
    'native tree, requirements.lock, or pyproject.toml differs'
fi

mkdir -p "$STAGE_PARENT" "$STAGE_CANDIDATE"
git -C "$BASS" archive --format=tar --output="$TMP/parent.tar" "$PARENT" \
  >"$OUT/archive_parent.log" 2>&1
RC_ARCHIVE_PARENT=$?
git -C "$BASS" archive --format=tar --output="$TMP/candidate.tar" "$CANDIDATE" \
  >"$OUT/archive_candidate.log" 2>&1
RC_ARCHIVE_CANDIDATE=$?
tar -xf "$TMP/parent.tar" -C "$STAGE_PARENT" >"$OUT/extract_parent.log" 2>&1
RC_EXTRACT_PARENT=$?
tar -xf "$TMP/candidate.tar" -C "$STAGE_CANDIDATE" >"$OUT/extract_candidate.log" 2>&1
RC_EXTRACT_CANDIDATE=$?
if [ "$RC_ARCHIVE_PARENT" -ne 0 ] || [ "$RC_ARCHIVE_CANDIDATE" -ne 0 ] || \
   [ "$RC_EXTRACT_PARENT" -ne 0 ] || [ "$RC_EXTRACT_CANDIDATE" -ne 0 ]; then
  stop_gate STOP_STAGING_ARCHIVE_FAILURE \
    "archive_parent=$RC_ARCHIVE_PARENT archive_candidate=$RC_ARCHIVE_CANDIDATE extract_parent=$RC_EXTRACT_PARENT extract_candidate=$RC_EXTRACT_CANDIDATE"
fi

STAGED_ADAPTER_BLOB="$(git -C "$BASS" hash-object "$STAGE_CANDIDATE/bianchi/source_adapters.py" 2>/dev/null)"
[ "$STAGED_ADAPTER_BLOB" = "$SOURCE_ADAPTER_BLOB" ] || \
  stop_gate STOP_STAGED_ADAPTER_IDENTITY_MISMATCH "$STAGED_ADAPTER_BLOB"

WHEEL="$OUT/bianchi_rustcore-0.1.0-cp312-cp312-manylinux_2_34_x86_64.whl"
git -C "$BASS" show "$TRUSTED_COMMIT:$TRUSTED_WHEEL_PATH" \
  >"$WHEEL" 2>"$OUT/extract_wheel.log"
RC_WHEEL_EXTRACT=$?
git -C "$BASS" show "$TRUSTED_COMMIT:$TRUSTED_RESTORE_PATH" \
  >"$OUT/RF02C_NATIVE_RESTORE.json" 2>"$OUT/extract_restore.log"
RC_RESTORE_EXTRACT=$?
WHEEL_SHA="$(sha256sum "$WHEEL" 2>/dev/null | awk '{print $1}')"
if [ "$RC_WHEEL_EXTRACT" -ne 0 ] || [ "$RC_RESTORE_EXTRACT" -ne 0 ] || \
   [ "$WHEEL_SHA" != "$TRUSTED_WHEEL_SHA" ]; then
  stop_gate STOP_TRUSTED_WHEEL_RECOVERY_FAILURE \
    "wheel=$RC_WHEEL_EXTRACT restore=$RC_RESTORE_EXTRACT sha=${WHEEL_SHA:-MISSING}"
fi

prepare_environment() {
  worktree="$1"
  stage="$2"
  venv="$3"
  tag="$4"

  "$PYBOOT" -m venv "$venv" >"$OUT/${tag}_venv.log" 2>&1 || return 31
  "$venv/bin/python" -m pip install --disable-pip-version-check \
    -r "$worktree/requirements.lock" >"$OUT/${tag}_requirements.log" 2>&1 || return 32
  "$venv/bin/python" -m pip install --disable-pip-version-check \
    --no-index --no-deps --force-reinstall "$WHEEL" \
    >"$OUT/${tag}_wheel_install.log" 2>&1 || return 33
  "$venv/bin/python" -m pip install --disable-pip-version-check \
    'setuptools==68.1.2' 'wheel==0.42.0' \
    >"$OUT/${tag}_build_system.log" 2>&1 || return 34
  (
    cd "$stage" || exit 97
    env -u BASS_ALLOW_UNVERIFIED_NATIVE_DEV \
      "$venv/bin/python" -m pip install --disable-pip-version-check \
      --no-deps --no-build-isolation .
  ) >"$OUT/${tag}_project_from_stage.log" 2>&1 || return 35

  (
    cd "$worktree" || exit 97
    env -u BASS_ALLOW_UNVERIFIED_NATIVE_DEV PYTHONPATH="$worktree" \
      "$venv/bin/python" - <<'PY'
from __future__ import annotations
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import bianchi
from bianchi import backend_policy
import bianchi_rustcore
import jax
root = Path(bianchi_rustcore.__file__).resolve().parent
extensions = sorted(root.glob('*.so'))
if len(extensions) != 1:
    raise SystemExit(f'expected exactly one native extension, found {extensions}')
load = backend_policy.load_native()
if not load.available or load.module is None:
    raise SystemExit(f'native load unavailable: {load!r}')
so = extensions[0]
print(json.dumps({
    'bianchi_source': str(Path(bianchi.__file__).resolve()),
    'native_distribution_version': metadata.version('bianchi-rustcore'),
    'root_distribution_version': metadata.version('bianchi-solver'),
    'jax_version': jax.__version__,
    'shared_object': str(so),
    'shared_object_sha256': hashlib.sha256(so.read_bytes()).hexdigest(),
    'native_load_available': load.available,
    'development_override_present': 'BASS_ALLOW_UNVERIFIED_NATIVE_DEV' in os.environ,
}, indent=2, sort_keys=True))
PY
  ) >"$OUT/${tag}_native_identity.json" 2>"$OUT/${tag}_native_identity.err" || return 36
  return 0
}

prepare_environment "$WORKTREE_PARENT" "$STAGE_PARENT" "$VENV_PARENT" parent
RC_ENV_PARENT=$?
prepare_environment "$WORKTREE_CANDIDATE" "$STAGE_CANDIDATE" "$VENV_CANDIDATE" candidate
RC_ENV_CANDIDATE=$?
if [ "$RC_ENV_PARENT" -ne 0 ] || [ "$RC_ENV_CANDIDATE" -ne 0 ]; then
  stop_gate STOP_ENVIRONMENT_INSTALL_OR_NATIVE_LOAD_FAILURE \
    "parent=$RC_ENV_PARENT candidate=$RC_ENV_CANDIDATE"
fi

PARENT_SO_SHA="$(sed -n 's/.*"shared_object_sha256": "\([0-9a-f]*\)".*/\1/p' "$OUT/parent_native_identity.json" | head -n 1)"
CANDIDATE_SO_SHA="$(sed -n 's/.*"shared_object_sha256": "\([0-9a-f]*\)".*/\1/p' "$OUT/candidate_native_identity.json" | head -n 1)"
if [ "$PARENT_SO_SHA" != "$TRUSTED_SO_SHA" ] || \
   [ "$CANDIDATE_SO_SHA" != "$TRUSTED_SO_SHA" ] || \
   grep -Fq '"development_override_present": true' "$OUT/parent_native_identity.json" || \
   grep -Fq '"development_override_present": true' "$OUT/candidate_native_identity.json"; then
  stop_gate FAIL_R8B_TRUSTED_NATIVE_IDENTITY \
    "parent_so=$PARENT_SO_SHA candidate_so=$CANDIDATE_SO_SHA"
fi

export RAYON_NUM_THREADS=1
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1

run_backend_cone() {
  worktree="$1"
  python="$2"
  tag="$3"
  (
    cd "$worktree" || exit 97
    env -u BASS_ALLOW_UNVERIFIED_NATIVE_DEV PYTHONPATH="$worktree" \
      "$python" -m pytest -q \
      tests/test_backend_policy.py \
      tests/test_backend_integration.py \
      tests/test_backend_packaging.py
  ) >"$OUT/${tag}_backend.log" 2>&1
  rc=$?
  grep -E '^FAILED |^ERROR ' "$OUT/${tag}_backend.log" | \
    sed -E 's/ - .*//' | sort -u >"$OUT/${tag}_failures.txt" 2>/dev/null || true
  return "$rc"
}

run_backend_cone "$WORKTREE_PARENT" "$VENV_PARENT/bin/python" parent
RC_BACKEND_PARENT=$?
run_backend_cone "$WORKTREE_CANDIDATE" "$VENV_CANDIDATE/bin/python" candidate
RC_BACKEND_CANDIDATE=$?
diff -u "$OUT/parent_failures.txt" "$OUT/candidate_failures.txt" \
  >"$OUT/backend_failure_diff.txt" 2>&1
RC_BACKEND_FAILURE_DIFF=$?
PARENT_BACKEND_TESTS="$(sed -n 's/^\([0-9][0-9]*\) passed.*/\1/p' "$OUT/parent_backend.log" | tail -n 1)"
CANDIDATE_BACKEND_TESTS="$(sed -n 's/^\([0-9][0-9]*\) passed.*/\1/p' "$OUT/candidate_backend.log" | tail -n 1)"
BACKEND_COUNTS_OK=false
if [ "$PARENT_BACKEND_TESTS" = "$EXPECTED_BACKEND_TESTS" ] && \
   [ "$CANDIDATE_BACKEND_TESTS" = "$EXPECTED_BACKEND_TESTS" ]; then
  BACKEND_COUNTS_OK=true
fi

(
  cd "$WORKTREE_CANDIDATE" || exit 97
  env -u BASS_ALLOW_UNVERIFIED_NATIVE_DEV PYTHONPATH="$WORKTREE_CANDIDATE" \
    "$VENV_CANDIDATE/bin/python" - <<'PY'
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
    result.testsRun == 33 and not result.failures and
    not result.errors and not result.skipped
)
print(json.dumps(summary, indent=2, sort_keys=True))
print(stream.getvalue(), file=sys.stderr)
raise SystemExit(0 if summary['pass'] else 1)
PY
) >"$OUT/candidate_focused_result.json" 2>"$OUT/candidate_focused_verbose.log"
RC_FOCUSED=$?

for run_index in 1 2; do
  (
    cd "$WORKTREE_CANDIDATE" || exit 97
    env -u BASS_ALLOW_UNVERIFIED_NATIVE_DEV PYTHONPATH="$WORKTREE_CANDIDATE" \
      "$VENV_CANDIDATE/bin/python" - <<'PY'
import json
from bianchi.source_adapters import (
    SourceTimeBasis,
    apply_constant_pair_to_full_spectral_grid,
    apply_constant_pair_to_spectral_pstf,
)
from bianchi.source_authority import (
    IntegratedMomentMapBinding,
    SourceAuthorityBundle,
    SourceFrequencyKind,
    SourceStateKind,
)
source = SourceAuthorityBundle.constant_pair(
    eta_s_inv=3.0,
    kappa_s_inv=2.0,
    frame='hydrogen_orthonormal',
    channel='total_occupation',
    source_sha256='0' * 64,
    frequency_kind=SourceFrequencyKind.POINTWISE_SPECTRAL,
)
binding = IntegratedMomentMapBinding.create(
    target_state_kind=SourceStateKind.RADIAL_INTEGRATED_ANGULAR_GRID,
    moment_map_sha256='1' * 64,
    radial_weight_family_sha256='2' * 64,
    source_sha256='3' * 64,
)
common = dict(
    state_parent_sha256='a' * 64,
    projection_contract_sha256='c' * 64,
    time_basis=SourceTimeBasis.PHYSICAL_TIME,
)
grid = apply_constant_pair_to_full_spectral_grid(
    source, (0.0, 1.0, 5.0), representation_sha256='1' * 64, **common
)
pstf = apply_constant_pair_to_spectral_pstf(
    source,
    (0.9, 0.2, -0.1, 0.05),
    unit_field_coefficients=(1.0, 0.0, 0.0, 0.0),
    l_out=3,
    l_work=3,
    representation_sha256='2' * 64,
    **common,
)
changed = apply_constant_pair_to_full_spectral_grid(
    source,
    (0.0, 1.0, 5.0),
    state_parent_sha256='a' * 64,
    representation_sha256='1' * 64,
    projection_contract_sha256='d' * 64,
    time_basis=SourceTimeBasis.PHYSICAL_TIME,
)
print(json.dumps({
    'source_payload_sha256': source.payload_sha256,
    'integrated_binding_sha256': binding.binding_sha256,
    'grid_output_sha256': grid.receipt.output_sha256,
    'pstf_output_sha256': pstf.receipt.output_sha256,
    'changed_projection_output_sha256': changed.receipt.output_sha256,
    'grid_values': grid.values,
    'pstf_values': pstf.values,
}, sort_keys=True))
PY
  ) >"$OUT/hash_run_${run_index}.json" 2>"$OUT/hash_run_${run_index}.err"
done

HASH_DETERMINISTIC=false
cmp -s "$OUT/hash_run_1.json" "$OUT/hash_run_2.json" && HASH_DETERMINISTIC=true
"$PYBOOT" - "$OUT/hash_run_1.json" \
  "$SOURCE_PAYLOAD_SHA" "$INTEGRATED_BINDING_SHA" \
  "$GRID_OUTPUT_SHA" "$PSTF_OUTPUT_SHA" "$CHANGED_PROJECTION_SHA" \
  >"$OUT/hash_check.json" <<'PY'
import json
import sys
from pathlib import Path
payload = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
expected_source, expected_binding, expected_grid, expected_pstf, expected_changed = sys.argv[2:]
checks = {
    'source_payload_exact': payload['source_payload_sha256'] == expected_source,
    'integrated_binding_exact': payload['integrated_binding_sha256'] == expected_binding,
    'grid_output_exact': payload['grid_output_sha256'] == expected_grid,
    'pstf_output_exact': payload['pstf_output_sha256'] == expected_pstf,
    'projection_mutation_exact': payload['changed_projection_output_sha256'] == expected_changed,
    'projection_mutation_sensitive': payload['changed_projection_output_sha256'] != payload['grid_output_sha256'],
    'grid_values_exact': payload['grid_values'] == [3.0, 4.0, 8.0],
    'pstf_values_exact': payload['pstf_values'] == [3.9, 0.2, -0.1, 0.05],
}
checks['pass'] = all(checks.values())
print(json.dumps(checks, indent=2, sort_keys=True))
raise SystemExit(0 if checks['pass'] else 1)
PY
RC_HASH_CHECK=$?
HASHES_PASS=false
if [ "$HASH_DETERMINISTIC" = true ] && [ "$RC_HASH_CHECK" -eq 0 ]; then
  HASHES_PASS=true
fi

cat "$OUT/parent_backend.log" "$OUT/candidate_backend.log" \
    "$OUT/parent_native_identity.err" "$OUT/candidate_native_identity.err" \
  | grep -nE 'UnverifiedNativePayloadError|UNVERIFIED_DEVELOPMENT_NATIVE_PAYLOAD|UnverifiedNativeDevelopmentWarning' \
  >"$OUT/forbidden_provenance_diagnostics.txt" 2>/dev/null || true
FORBIDDEN_PROVENANCE_LINES="$(wc -l <"$OUT/forbidden_provenance_diagnostics.txt" 2>/dev/null | tr -d ' ')"
[ -n "$FORBIDDEN_PROVENANCE_LINES" ] || FORBIDDEN_PROVENANCE_LINES=0

git -C "$WORKTREE_PARENT" status --porcelain=v1 --untracked-files=all \
  >"$OUT/parent_status.txt"
git -C "$WORKTREE_CANDIDATE" status --porcelain=v1 --untracked-files=all \
  >"$OUT/candidate_status.txt"
CLEAN_WORKTREES=false
if [ ! -s "$OUT/parent_status.txt" ] && [ ! -s "$OUT/candidate_status.txt" ]; then
  CLEAN_WORKTREES=true
fi

CLASSIFICATION='FAIL_R8B_TRUSTED_NATIVE_DIFFERENTIAL'
if [ "$RC_BACKEND_PARENT" -eq 0 ] && \
   [ "$RC_BACKEND_CANDIDATE" -eq 0 ] && \
   [ "$RC_BACKEND_FAILURE_DIFF" -eq 0 ] && \
   [ "$BACKEND_COUNTS_OK" = true ] && \
   [ "$RC_FOCUSED" -eq 0 ] && \
   [ "$HASHES_PASS" = true ] && \
   [ "$FORBIDDEN_PROVENANCE_LINES" -eq 0 ] && \
   [ "$CLEAN_WORKTREES" = true ]; then
  CLASSIFICATION='PASS_BASS_REC_SOURCE_R8B_TRUSTED_NATIVE_PARENT_CANDIDATE_NONREGRESSION'
elif [ "$RC_BACKEND_PARENT" -eq 0 ] && [ "$RC_BACKEND_CANDIDATE" -ne 0 ]; then
  CLASSIFICATION='FAIL_R8_CANDIDATE_INDUCED_BACKEND_REGRESSION'
elif [ "$RC_BACKEND_PARENT" -ne 0 ] && [ "$RC_BACKEND_CANDIDATE" -ne 0 ] && \
     [ "$RC_BACKEND_FAILURE_DIFF" -eq 0 ]; then
  CLASSIFICATION='BLOCKED_INHERITED_PARENT_BACKEND_FAILURE'
elif [ "$RC_FOCUSED" -ne 0 ] || [ "$HASHES_PASS" != true ]; then
  CLASSIFICATION='FAIL_R8_FOCUSED_PROTOCOL_OR_HASH_IDENTITY'
elif [ "$FORBIDDEN_PROVENANCE_LINES" -ne 0 ]; then
  CLASSIFICATION='FAIL_R8B_UNTRUSTED_NATIVE_DIAGNOSTIC_OBSERVED'
elif [ "$CLEAN_WORKTREES" != true ]; then
  CLASSIFICATION='FAIL_R8B_SOURCE_WORKTREE_DIRTY_AFTER_STAGED_BUILD'
fi

cat >"$OUT/summary.txt" <<EOF
classification=$CLASSIFICATION
parent=$PARENT
candidate=$CANDIDATE
publication_head=$PUBLICATION_HEAD
parent_tree=$ACTUAL_PARENT_TREE
candidate_tree=$ACTUAL_CANDIDATE_TREE
source_authority_blob=$CANDIDATE_AUTH_BLOB
source_adapter_blob=$CANDIDATE_ADAPTER_BLOB
source_diff_only_adapter=true
trusted_commit=$TRUSTED_COMMIT
trusted_wheel_sha256=$WHEEL_SHA
parent_shared_object_sha256=$PARENT_SO_SHA
candidate_shared_object_sha256=$CANDIDATE_SO_SHA
python=$PYVER
parent_backend_rc=$RC_BACKEND_PARENT
candidate_backend_rc=$RC_BACKEND_CANDIDATE
parent_backend_tests=$PARENT_BACKEND_TESTS
candidate_backend_tests=$CANDIDATE_BACKEND_TESTS
failure_sets_identical=$([ "$RC_BACKEND_FAILURE_DIFF" -eq 0 ] && echo true || echo false)
candidate_focused_33_rc=$RC_FOCUSED
deterministic_golden_hashes=$HASHES_PASS
source_payload_sha256=$SOURCE_PAYLOAD_SHA
integrated_binding_sha256=$INTEGRATED_BINDING_SHA
grid_output_sha256=$GRID_OUTPUT_SHA
pstf_output_sha256=$PSTF_OUTPUT_SHA
changed_projection_output_sha256=$CHANGED_PROJECTION_SHA
forbidden_provenance_lines=$FORBIDDEN_PROVENANCE_LINES
development_override=unset
clean_worktrees=$CLEAN_WORKTREES
build_location=NON_GIT_STAGING_DIRECTORIES
receipt_dir=$OUT
EOF
cat "$OUT/summary.txt"

cat >"$OUT/R8B_TRUSTED_NATIVE_DIFFERENTIAL_RECEIPT.json" <<EOF
{
  "schema_version": "1.0.0",
  "stage_id": "BASS_REC_SOURCE_R8B_TRUSTED_NATIVE_PARENT_CANDIDATE_NONREGRESSION",
  "classification": "$CLASSIFICATION",
  "parent": "$PARENT",
  "candidate": "$CANDIDATE",
  "publication_head": "$PUBLICATION_HEAD",
  "trusted_commit": "$TRUSTED_COMMIT",
  "trusted_wheel_sha256": "$WHEEL_SHA",
  "trusted_shared_object_sha256": "$TRUSTED_SO_SHA",
  "backend": {
    "parent_rc": $RC_BACKEND_PARENT,
    "candidate_rc": $RC_BACKEND_CANDIDATE,
    "parent_tests": ${PARENT_BACKEND_TESTS:-0},
    "candidate_tests": ${CANDIDATE_BACKEND_TESTS:-0},
    "failure_sets_identical": $([ "$RC_BACKEND_FAILURE_DIFF" -eq 0 ] && echo true || echo false)
  },
  "focused_33_rc": $RC_FOCUSED,
  "deterministic_golden_hashes": $HASHES_PASS,
  "forbidden_provenance_lines": $FORBIDDEN_PROVENANCE_LINES,
  "development_override": "unset",
  "clean_worktrees": $CLEAN_WORKTREES,
  "root_package_build_location": "non_git_staging_directories",
  "claim_boundary": {
    "trusted_native_adapter_nonregression": $([ "$CLASSIFICATION" = "PASS_BASS_REC_SOURCE_R8B_TRUSTED_NATIVE_PARENT_CANDIDATE_NONREGRESSION" ] && echo true || echo false),
    "general_grid_pstf_numerical_parity": false,
    "physical_rec_source_wiring": false,
    "anisotropic_or_nonlocal_source": false,
    "integrated_state_closure": false,
    "physical_directional_face": false,
    "provider_or_statistics_promotion": false,
    "pass_rec_physical_split": false,
    "pass_rf04": false
  }
}
EOF

cat >"$OUT/r8b_plot_data.json" <<EOF
{
  "classification": "$CLASSIFICATION",
  "backend_tests": {
    "parent": ${PARENT_BACKEND_TESTS:-0},
    "candidate": ${CANDIDATE_BACKEND_TESTS:-0}
  },
  "focused_tests": {
    "candidate": $EXPECTED_FOCUSED_TESTS
  },
  "failure_counts": {
    "parent_backend": $(wc -l <"$OUT/parent_failures.txt" 2>/dev/null | tr -d ' '),
    "candidate_backend": $(wc -l <"$OUT/candidate_failures.txt" 2>/dev/null | tr -d ' ')
  },
  "forbidden_provenance_lines": $FORBIDDEN_PROVENANCE_LINES,
  "clean_worktrees": $CLEAN_WORKTREES
}
EOF

"$PYBOOT" - "$OUT/r8b_plot_data.json" "$OUT/r8b_differential_audit.svg" <<'PY'
import json
import sys
from pathlib import Path
data = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
out = Path(sys.argv[2])
parent = int(data['backend_tests']['parent'])
candidate = int(data['backend_tests']['candidate'])
focused = int(data['focused_tests']['candidate'])
scale = 5
bars = [
    ('parent backend', parent, 55),
    ('candidate backend', candidate, 55),
    ('candidate focused', focused, 34),
]
rows = []
for i, (label, value, maximum) in enumerate(bars):
    y = 45 + i * 55
    width = 360 * value / maximum if maximum else 0
    rows.append(f'<text x="20" y="{y}" font-size="14">{label}</text>')
    rows.append(f'<rect x="170" y="{y-15}" width="360" height="20" fill="none" stroke="black"/>')
    rows.append(f'<rect x="170" y="{y-15}" width="{width:.2f}" height="20" fill="#777"/>')
    rows.append(f'<text x="540" y="{y}" font-size="14">{value}</text>')
status = data['classification']
footer = (
    f"forbidden provenance lines={data['forbidden_provenance_lines']}; "
    f"clean worktrees={str(data['clean_worktrees']).lower()}"
)
svg = '\n'.join([
    '<svg xmlns="http://www.w3.org/2000/svg" width="720" height="260" viewBox="0 0 720 260">',
    '<rect width="100%" height="100%" fill="white"/>',
    '<text x="20" y="22" font-size="16" font-weight="bold">R8B trusted-native differential audit</text>',
    *rows,
    f'<text x="20" y="220" font-size="12">{footer}</text>',
    f'<text x="20" y="242" font-size="11">{status}</text>',
    '</svg>',
])
out.write_text(svg + '\n', encoding='utf-8')
PY

sha256sum "$OUT"/* >"$OUT/SHA256SUMS" 2>/dev/null || true
printf '\nCaller checkout was not switched or modified.\n'
exit 0
