#!/usr/bin/env bash
# BASS_REC_SOURCE_R8_LOCAL_EXACT_GREEN_REPLAY
#
# Runs the bounded R8 source-adapter candidate in a detached worktree. The
# caller checkout is never switched or modified. The script records its own
# classification and exits zero after preserving all evidence.

set +e
set +u
set +o pipefail 2>/dev/null || true

BRANCH='research/bass-rec-source-r8-dual-adapter-green-20260904-r1'
SOURCE_COMMIT='ed630f3b8b02531af0f392b722e6636c14a41864'
SOURCE_TREE='a5617a552bb2f6e65b78979bedde23543b9f9506'
SOURCE_AUTHORITY_BLOB='869677390004f68aef9f547e6556f5f1c15bd012'
SOURCE_ADAPTER_BLOB='8b00602fc76e1cd49ac5b43615c97a686b56f080'
R5_TEST_BLOB='db336d64633d8a9552bc3613c588a00f33404a4d'
R6_TEST_BLOB='49be9546c4655bc5ca330bc31ae2daf07578b74f'
R7_TEST_BLOB='d6fb316452a947d0f955dd4a115e8840688a2d02'

ROOT="${RECEIPT_ROOT:-$HOME/Dropbox/bianchi/_runtime_receipts}"
OUT="$ROOT/BASS_REC_SOURCE_R8_GREEN_$(date -u +%Y%m%dT%H%M%SZ)"
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
  stop_gate STOP_R8_FETCH_FAILURE 'publication branch unavailable'
fi

git -C "$BASS" merge-base --is-ancestor "$SOURCE_COMMIT" "$PUB" \
  >/dev/null 2>&1
if [ "$?" -ne 0 ]; then
  stop_gate STOP_R8_SOURCE_NOT_PUBLICATION_ANCESTOR "$PUB"
fi

TMP="$(mktemp -d /tmp/bass-r8-green.XXXXXX 2>/dev/null)"
[ -d "$TMP" ] || stop_gate STOP_R8_TEMP_DIRECTORY_FAILURE "$TMP"
WT="$TMP/worktree"

cleanup() {
  git -C "$BASS" worktree remove --force "$WT" >/dev/null 2>&1 || true
  case "$TMP" in
    /tmp/bass-r8-green.*) rm -rf -- "$TMP" >/dev/null 2>&1 || true ;;
  esac
}
trap cleanup EXIT HUP INT TERM

git -C "$BASS" worktree add --detach "$WT" "$SOURCE_COMMIT" \
  >"$OUT/worktree.log" 2>&1
RC_WT=$?
[ "$RC_WT" -eq 0 ] || stop_gate STOP_R8_WORKTREE_FAILURE "$RC_WT"

TREE="$(git -C "$WT" rev-parse HEAD^{tree} 2>/dev/null)"
AUTH_BLOB="$(git -C "$WT" hash-object bianchi/source_authority.py 2>/dev/null)"
ADAPTER_BLOB="$(git -C "$WT" hash-object bianchi/source_adapters.py 2>/dev/null)"
T5="$(git -C "$WT" hash-object tests/research/test_bass_rec_source_protocol_red.py 2>/dev/null)"
T6="$(git -C "$WT" hash-object tests/research/test_bass_rec_source_protocol_r6_red.py 2>/dev/null)"
T7="$(git -C "$WT" hash-object tests/research/test_bass_rec_source_r7_dual_adapter_red.py 2>/dev/null)"

if [ "$TREE" != "$SOURCE_TREE" ] || \
   [ "$AUTH_BLOB" != "$SOURCE_AUTHORITY_BLOB" ] || \
   [ "$ADAPTER_BLOB" != "$SOURCE_ADAPTER_BLOB" ] || \
   [ "$T5" != "$R5_TEST_BLOB" ] || \
   [ "$T6" != "$R6_TEST_BLOB" ] || \
   [ "$T7" != "$R7_TEST_BLOB" ]; then
  stop_gate STOP_R8_EXACT_IDENTITY_MISMATCH \
    "$TREE $AUTH_BLOB $ADAPTER_BLOB $T5 $T6 $T7"
fi

(
  cd "$WT" || exit 97
  PYTHONPATH="$WT" "$PY" -m py_compile \
    bianchi/source_authority.py \
    bianchi/source_adapters.py \
    tests/research/test_bass_rec_source_protocol_red.py \
    tests/research/test_bass_rec_source_protocol_r6_red.py \
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
    result.testsRun == 33
    and not result.failures
    and not result.errors
    and not result.skipped
)
print(json.dumps(summary, indent=2, sort_keys=True))
print(stream.getvalue(), file=sys.stderr)
raise SystemExit(0 if summary['pass'] else 1)
PY
) >"$OUT/focused_result.json" 2>"$OUT/focused_verbose.log"
RC_FOCUSED=$?

for N in 1 2; do
  (
    cd "$WT" || exit 97
    PYTHONPATH="$WT" "$PY" - <<'PY'
import json
from bianchi.source_adapters import (
    SourceTimeBasis,
    apply_constant_pair_to_full_spectral_grid,
    apply_constant_pair_to_spectral_pstf,
)
from bianchi.source_authority import SourceAuthorityBundle, SourceFrequencyKind

bundle = SourceAuthorityBundle.constant_pair(
    eta_s_inv=3.0,
    kappa_s_inv=2.0,
    frame='hydrogen_orthonormal',
    channel='total_occupation',
    source_sha256='0' * 64,
    frequency_kind=SourceFrequencyKind.POINTWISE_SPECTRAL,
)
common = dict(
    state_parent_sha256='a' * 64,
    projection_contract_sha256='c' * 64,
    time_basis=SourceTimeBasis.PHYSICAL_TIME,
)
grid = apply_constant_pair_to_full_spectral_grid(
    bundle,
    (0.0, 1.0, 5.0),
    representation_sha256='1' * 64,
    **common,
)
pstf = apply_constant_pair_to_spectral_pstf(
    bundle,
    (0.9, 0.2, -0.1, 0.05),
    unit_field_coefficients=(1.0, 0.0, 0.0, 0.0),
    l_out=3,
    l_work=3,
    representation_sha256='2' * 64,
    **common,
)
changed = apply_constant_pair_to_full_spectral_grid(
    bundle,
    (0.0, 1.0, 5.0),
    state_parent_sha256='a' * 64,
    representation_sha256='1' * 64,
    projection_contract_sha256='d' * 64,
    time_basis=SourceTimeBasis.PHYSICAL_TIME,
)
print(json.dumps({
    'grid_output_sha256': grid.receipt.output_sha256,
    'pstf_output_sha256': pstf.receipt.output_sha256,
    'changed_projection_output_sha256': changed.receipt.output_sha256,
    'grid_values': grid.values,
    'pstf_values': pstf.values,
}, sort_keys=True))
PY
  ) >"$OUT/hash_run_${N}.json" 2>"$OUT/hash_run_${N}.err"
done

HASH_DETERMINISTIC=false
HASH_SENSITIVE=false
if cmp -s "$OUT/hash_run_1.json" "$OUT/hash_run_2.json"; then
  HASH_DETERMINISTIC=true
fi

"$PY" - "$OUT/hash_run_1.json" >"$OUT/hash_check.json" <<'PY'
import json
import re
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
sha = re.compile(r'[0-9a-f]{64}\Z')
grid = payload['grid_output_sha256']
pstf = payload['pstf_output_sha256']
changed = payload['changed_projection_output_sha256']
result = {
    'all_hashes_canonical': all(sha.fullmatch(value) for value in (grid, pstf, changed)),
    'projection_contract_is_input_sensitive': grid != changed,
    'grid_values_exact': payload['grid_values'] == [3.0, 4.0, 8.0],
    'pstf_values_expected': payload['pstf_values'] == [3.9, 0.2, -0.1, 0.05],
}
result['pass'] = all(result.values())
print(json.dumps(result, indent=2, sort_keys=True))
raise SystemExit(0 if result['pass'] else 1)
PY
RC_HASH_CHECK=$?
if [ "$RC_HASH_CHECK" -eq 0 ]; then
  HASH_SENSITIVE=true
fi

(
  cd "$WT" || exit 97
  PYTHONPATH="$WT" "$PY" - <<'PY'
import json
from bianchi.source_adapters import (
    SourceAdapterError,
    SourceTimeBasis,
    apply_constant_pair_to_full_spectral_grid,
    apply_constant_pair_to_spectral_pstf,
    require_dual_adapter_target,
)
from bianchi.source_authority import (
    SourceAuthorityBundle,
    SourceFrequencyKind,
    SourceStateKind,
)

bundle = SourceAuthorityBundle.constant_pair(
    eta_s_inv=3.0,
    kappa_s_inv=2.0,
    frame='hydrogen_orthonormal',
    channel='total_occupation',
    source_sha256='0' * 64,
    frequency_kind=SourceFrequencyKind.POINTWISE_SPECTRAL,
)
base = dict(
    state_parent_sha256='a' * 64,
    representation_sha256='b' * 64,
    projection_contract_sha256='c' * 64,
)

checks = {}

def rejected(name, callable_):
    try:
        callable_()
    except SourceAdapterError:
        checks[name] = True
    else:
        checks[name] = False

for state in (
    SourceStateKind.RADIAL_INTEGRATED_ANGULAR_GRID,
    SourceStateKind.FINITE_INTEGRATED_J_HIERARCHY,
):
    rejected(f'integrated_state_{state.value}', lambda state=state: require_dual_adapter_target(state))

rejected(
    'negative_grid_occupation',
    lambda: apply_constant_pair_to_full_spectral_grid(
        bundle, (-1.0,), time_basis=SourceTimeBasis.PHYSICAL_TIME, **base
    ),
)
rejected(
    'missing_q_time_H',
    lambda: apply_constant_pair_to_full_spectral_grid(
        bundle, (1.0,), time_basis=SourceTimeBasis.Q_TIME, **base
    ),
)
rejected(
    'physical_time_with_H',
    lambda: apply_constant_pair_to_full_spectral_grid(
        bundle, (1.0,), time_basis=SourceTimeBasis.PHYSICAL_TIME,
        H_s_inv=1.0, **base
    ),
)
rejected(
    'ray_length_without_c',
    lambda: apply_constant_pair_to_full_spectral_grid(
        bundle, (1.0,), time_basis=SourceTimeBasis.RAY_LENGTH, **base
    ),
)
rejected(
    'rank_underallocation',
    lambda: apply_constant_pair_to_spectral_pstf(
        bundle, (1.0, 0.1, 0.01),
        unit_field_coefficients=(1.0, 0.0, 0.0),
        l_out=2, l_work=1,
        time_basis=SourceTimeBasis.PHYSICAL_TIME, **base
    ),
)
rejected(
    'coefficient_length_mismatch',
    lambda: apply_constant_pair_to_spectral_pstf(
        bundle, (1.0, 0.1), unit_field_coefficients=(1.0,),
        l_out=1, l_work=1,
        time_basis=SourceTimeBasis.PHYSICAL_TIME, **base
    ),
)
checks['q_time_exact_once'] = (
    apply_constant_pair_to_full_spectral_grid(
        bundle, (5.0,), time_basis=SourceTimeBasis.Q_TIME,
        H_s_inv=4.0, **base
    ).values == (2.0,)
)
checks['ray_length_explicit_c'] = (
    apply_constant_pair_to_full_spectral_grid(
        bundle, (5.0,), time_basis=SourceTimeBasis.RAY_LENGTH,
        c_m_s=2.0, **base
    ).values == (4.0,)
)
checks['pass'] = all(checks.values())
print(json.dumps(checks, indent=2, sort_keys=True))
raise SystemExit(0 if checks['pass'] else 1)
PY
) >"$OUT/adversarial_probe.json" 2>"$OUT/adversarial_probe.err"
RC_ADVERSARIAL=$?

git -C "$WT" status --porcelain >"$OUT/git_status_after.txt" 2>&1
if [ -s "$OUT/git_status_after.txt" ]; then
  CLEAN=false
else
  CLEAN=true
fi

CLASS='FAIL_BASS_REC_SOURCE_R8_DUAL_ADAPTER_GREEN'
if [ "$RC_COMPILE" -eq 0 ] && \
   [ "$RC_FOCUSED" -eq 0 ] && \
   [ "$HASH_DETERMINISTIC" = true ] && \
   [ "$HASH_SENSITIVE" = true ] && \
   [ "$RC_ADVERSARIAL" -eq 0 ] && \
   [ "$CLEAN" = true ]; then
  CLASS='PASS_BASS_REC_SOURCE_R8_CONSTANT_PAIR_DUAL_ADAPTER_GREEN'
fi

GRID_HASH="$($PY -c 'import json,sys; print(json.load(open(sys.argv[1]))["grid_output_sha256"])' "$OUT/hash_run_1.json" 2>/dev/null)"
PSTF_HASH="$($PY -c 'import json,sys; print(json.load(open(sys.argv[1]))["pstf_output_sha256"])' "$OUT/hash_run_1.json" 2>/dev/null)"

cat >"$OUT/summary.txt" <<EOF
classification=$CLASS
publication_head=$PUB
source_commit=$SOURCE_COMMIT
source_tree=$TREE
source_authority_blob=$AUTH_BLOB
source_adapter_blob=$ADAPTER_BLOB
r5_test_blob=$T5
r6_test_blob=$T6
r7_test_blob=$T7
python=$PYVER
compile_rc=$RC_COMPILE
focused_33_rc=$RC_FOCUSED
deterministic_output_hashes=$HASH_DETERMINISTIC
input_sensitive_output_hashes=$HASH_SENSITIVE
grid_output_sha256=$GRID_HASH
pstf_output_sha256=$PSTF_HASH
adversarial_probe_rc=$RC_ADVERSARIAL
clean_worktree=$CLEAN
receipt_dir=$OUT
EOF

cat "$OUT/summary.txt"
sha256sum "$OUT"/* >"$OUT/SHA256SUMS" 2>/dev/null || true
printf '\nCaller checkout was not switched or modified.\n'
exit 0
