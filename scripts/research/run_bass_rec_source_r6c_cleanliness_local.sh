#!/usr/bin/env bash
# BASS_REC_SOURCE_R6C_CLEANLINESS_ONLY_DIFFERENTIAL_REPLAY
#
# Close the sole remaining R6B gate without weakening cleanliness semantics.
# The preceding R6B run built the root Python package inside each detached Git
# worktree and therefore left the same untracked packaging artifact, build/,
# on both sides. This runner exports each exact Git tree into a non-Git staging
# directory and performs the package build/install there. The source worktrees
# are used only for identity checks and tests and must remain completely clean.
#
# The caller checkout is never switched or modified. The runner records its own
# classification and always exits with shell status zero.
#
# Optional overrides:
#   BASS_REPO=/absolute/path/to/bass
#   PYTHON_BOOTSTRAP=/absolute/path/to/python3.12
#   RECEIPT_ROOT=/absolute/path/to/receipt/root

set +e
set +u
set +o pipefail 2>/dev/null || true

RED_PARENT='0a4875e5c18419a672c164eb5c849f3f4ab01571'
GREEN_SOURCE='92d67dc79cf645947beb93ac01a9505ee277dabd'
BRANCH='research/bass-rec-source-r6-hardening-green-20260904-r1'

GREEN_TREE='65cb63e6d08e80e9a8f38f83e3a536cb0a00a693'
GREEN_SOURCE_BLOB='869677390004f68aef9f547e6556f5f1c15bd012'
R5_TEST_BLOB='db336d64633d8a9552bc3613c588a00f33404a4d'
R6_TEST_BLOB='49be9546c4655bc5ca330bc31ae2daf07578b74f'

NATIVE_WHEEL_SHA256='bf5a59534ffc9d6f9c3410aa19319f18a4a8a7a9761bcd61c5da8c8627ddf609'
SOURCE_PAYLOAD_SHA256='7f0db7e1cf7423ff6751a21ab4002ef8f13d89f788a8a746b26992abecf791e8'
INTEGRATED_BINDING_SHA256='54762aa915b3fa0da847676a3d4491b8f7f2f358e48dd275fffee84ba6496093'

ROOT="${RECEIPT_ROOT:-$HOME/Dropbox/bianchi/_runtime_receipts}"
OUT="$ROOT/BASS_REC_SOURCE_R6C_$(date -u +%Y%m%dT%H%M%SZ)"
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

PYBOOT="${PYTHON_BOOTSTRAP:-$(command -v python3.12 2>/dev/null)}"
[ -x "$PYBOOT" ] || PYBOOT="$(command -v python 2>/dev/null)"
[ -x "$PYBOOT" ] || stop_gate STOP_PYTHON_NOT_FOUND 'Python 3.12 is required'

PYVER="$($PYBOOT -c 'import sys; print(".".join(map(str,sys.version_info[:3])))' 2>/dev/null)"
case "$PYVER" in
  3.12.*) ;;
  *) stop_gate STOP_WRONG_PYTHON_VERSION "$PYVER" ;;
esac

git -C "$BASS" fetch --no-tags origin \
  "$BRANCH:refs/remotes/origin/$BRANCH" >"$OUT/fetch.log" 2>&1
RC_FETCH=$?
PUBLICATION_HEAD="$(
  git -C "$BASS" rev-parse "refs/remotes/origin/$BRANCH" 2>/dev/null
)"
if [ "$RC_FETCH" -ne 0 ] || [ -z "$PUBLICATION_HEAD" ]; then
  stop_gate STOP_FETCH_FAILURE 'publication branch unavailable'
fi

git -C "$BASS" merge-base --is-ancestor \
  "$GREEN_SOURCE" "$PUBLICATION_HEAD" >/dev/null 2>&1
[ "$?" -eq 0 ] || \
  stop_gate STOP_GREEN_NOT_PUBLICATION_ANCESTOR "$PUBLICATION_HEAD"

NATIVE_WHEEL="$(
  find "$ROOT" -type f -name 'bianchi_rustcore-0.1.0-*.whl' -print 2>/dev/null |
  while IFS= read -r candidate; do
    digest="$(sha256sum "$candidate" 2>/dev/null | awk '{print $1}')"
    if [ "$digest" = "$NATIVE_WHEEL_SHA256" ]; then
      printf '%s\n' "$candidate"
      break
    fi
  done
)"
[ -f "$NATIVE_WHEEL" ] || \
  stop_gate STOP_GOLDEN_NATIVE_WHEEL_NOT_FOUND "$NATIVE_WHEEL_SHA256"

TMP="$(mktemp -d /tmp/bass-r6c.XXXXXX 2>/dev/null)"
[ -d "$TMP" ] || stop_gate STOP_TEMP_DIRECTORY_FAILURE "$TMP"

WORKTREE_RED="$TMP/worktree-red"
WORKTREE_GREEN="$TMP/worktree-green"
STAGE_RED="$TMP/stage-red"
STAGE_GREEN="$TMP/stage-green"
VENV_RED="$TMP/venv-red"
VENV_GREEN="$TMP/venv-green"

cleanup() {
  git -C "$BASS" worktree remove --force "$WORKTREE_RED" \
    >/dev/null 2>&1 || true
  git -C "$BASS" worktree remove --force "$WORKTREE_GREEN" \
    >/dev/null 2>&1 || true
  case "$TMP" in
    /tmp/bass-r6c.*) rm -rf -- "$TMP" >/dev/null 2>&1 || true ;;
  esac
}
trap cleanup EXIT HUP INT TERM

git -C "$BASS" worktree add --detach "$WORKTREE_RED" "$RED_PARENT" \
  >"$OUT/worktree_red.log" 2>&1
RC_WORKTREE_RED=$?

git -C "$BASS" worktree add --detach "$WORKTREE_GREEN" "$GREEN_SOURCE" \
  >"$OUT/worktree_green.log" 2>&1
RC_WORKTREE_GREEN=$?

if [ "$RC_WORKTREE_RED" -ne 0 ] || [ "$RC_WORKTREE_GREEN" -ne 0 ]; then
  stop_gate STOP_WORKTREE_FAILURE \
    "red=$RC_WORKTREE_RED green=$RC_WORKTREE_GREEN"
fi

ACTUAL_GREEN_TREE="$(
  git -C "$WORKTREE_GREEN" rev-parse HEAD^{tree} 2>/dev/null
)"
ACTUAL_GREEN_BLOB="$(
  git -C "$WORKTREE_GREEN" hash-object bianchi/source_authority.py 2>/dev/null
)"
ACTUAL_R5_TEST_BLOB="$(
  git -C "$WORKTREE_GREEN" \
    hash-object tests/research/test_bass_rec_source_protocol_red.py 2>/dev/null
)"
ACTUAL_R6_TEST_BLOB="$(
  git -C "$WORKTREE_GREEN" \
    hash-object tests/research/test_bass_rec_source_protocol_r6_red.py 2>/dev/null
)"

if [ "$ACTUAL_GREEN_TREE" != "$GREEN_TREE" ] || \
   [ "$ACTUAL_GREEN_BLOB" != "$GREEN_SOURCE_BLOB" ] || \
   [ "$ACTUAL_R5_TEST_BLOB" != "$R5_TEST_BLOB" ] || \
   [ "$ACTUAL_R6_TEST_BLOB" != "$R6_TEST_BLOB" ]; then
  stop_gate STOP_GREEN_IDENTITY_MISMATCH \
    "$ACTUAL_GREEN_TREE $ACTUAL_GREEN_BLOB $ACTUAL_R5_TEST_BLOB $ACTUAL_R6_TEST_BLOB"
fi

RED_RUST_TREE="$(
  git -C "$WORKTREE_RED" rev-parse HEAD:_rustcore 2>/dev/null
)"
GREEN_RUST_TREE="$(
  git -C "$WORKTREE_GREEN" rev-parse HEAD:_rustcore 2>/dev/null
)"
RED_LOCK_BLOB="$(
  git -C "$WORKTREE_RED" rev-parse HEAD:requirements.lock 2>/dev/null
)"
GREEN_LOCK_BLOB="$(
  git -C "$WORKTREE_GREEN" rev-parse HEAD:requirements.lock 2>/dev/null
)"
RED_PROJECT_BLOB="$(
  git -C "$WORKTREE_RED" rev-parse HEAD:pyproject.toml 2>/dev/null
)"
GREEN_PROJECT_BLOB="$(
  git -C "$WORKTREE_GREEN" rev-parse HEAD:pyproject.toml 2>/dev/null
)"

if [ "$RED_RUST_TREE" != "$GREEN_RUST_TREE" ] || \
   [ "$RED_LOCK_BLOB" != "$GREEN_LOCK_BLOB" ] || \
   [ "$RED_PROJECT_BLOB" != "$GREEN_PROJECT_BLOB" ]; then
  stop_gate STOP_DIFFERENTIAL_ENVIRONMENT_INPUT_DRIFT \
    'native tree, requirements.lock, or pyproject.toml differs'
fi

git -C "$WORKTREE_GREEN" diff --name-status \
  "$RED_PARENT" "$GREEN_SOURCE" >"$OUT/source_diff_name_status.txt" 2>&1

mkdir -p "$STAGE_RED" "$STAGE_GREEN"

git -C "$BASS" archive --format=tar \
  --output="$TMP/red.tar" "$RED_PARENT" >"$OUT/archive_red.log" 2>&1
RC_ARCHIVE_RED=$?

git -C "$BASS" archive --format=tar \
  --output="$TMP/green.tar" "$GREEN_SOURCE" >"$OUT/archive_green.log" 2>&1
RC_ARCHIVE_GREEN=$?

tar -xf "$TMP/red.tar" -C "$STAGE_RED" >"$OUT/extract_red.log" 2>&1
RC_EXTRACT_RED=$?

tar -xf "$TMP/green.tar" -C "$STAGE_GREEN" >"$OUT/extract_green.log" 2>&1
RC_EXTRACT_GREEN=$?

if [ "$RC_ARCHIVE_RED" -ne 0 ] || [ "$RC_ARCHIVE_GREEN" -ne 0 ] || \
   [ "$RC_EXTRACT_RED" -ne 0 ] || [ "$RC_EXTRACT_GREEN" -ne 0 ]; then
  stop_gate STOP_STAGING_ARCHIVE_FAILURE \
    "archive_red=$RC_ARCHIVE_RED archive_green=$RC_ARCHIVE_GREEN extract_red=$RC_EXTRACT_RED extract_green=$RC_EXTRACT_GREEN"
fi

STAGED_GREEN_BLOB="$(
  git -C "$BASS" hash-object "$STAGE_GREEN/bianchi/source_authority.py" 2>/dev/null
)"
[ "$STAGED_GREEN_BLOB" = "$GREEN_SOURCE_BLOB" ] || \
  stop_gate STOP_STAGED_SOURCE_IDENTITY_MISMATCH "$STAGED_GREEN_BLOB"

prepare_environment() {
  worktree="$1"
  stage="$2"
  venv="$3"
  tag="$4"

  "$PYBOOT" -m venv "$venv" >"$OUT/${tag}_venv.log" 2>&1 || return 31

  "$venv/bin/python" -m pip install --disable-pip-version-check \
    -r "$worktree/requirements.lock" >"$OUT/${tag}_requirements.log" 2>&1 || \
    return 32

  (
    cd "$stage" || exit 97
    "$venv/bin/python" -m pip install --disable-pip-version-check \
      --constraint requirements.lock "$NATIVE_WHEEL" .
  ) >"$OUT/${tag}_project_from_stage.log" 2>&1 || return 33

  (
    cd "$worktree" || exit 97
    PYTHONPATH="$worktree" "$venv/bin/python" - <<'PY'
from importlib import metadata
import bianchi
import bianchi_rustcore
import jax
print("bianchi-solver", metadata.version("bianchi-solver"))
print("bianchi-rustcore", metadata.version("bianchi-rustcore"))
print("jax", jax.__version__)
print("bianchi-source", bianchi.__file__)
print("native-source", bianchi_rustcore.__file__)
PY
  ) >"$OUT/${tag}_imports.log" 2>&1 || return 34

  return 0
}

prepare_environment \
  "$WORKTREE_RED" "$STAGE_RED" "$VENV_RED" red
RC_ENV_RED=$?

prepare_environment \
  "$WORKTREE_GREEN" "$STAGE_GREEN" "$VENV_GREEN" green
RC_ENV_GREEN=$?

if [ "$RC_ENV_RED" -ne 0 ] || [ "$RC_ENV_GREEN" -ne 0 ]; then
  stop_gate STOP_ENVIRONMENT_INSTALL_FAILURE \
    "red=$RC_ENV_RED green=$RC_ENV_GREEN"
fi

export BASS_ALLOW_UNVERIFIED_NATIVE_DEV=1
export RAYON_NUM_THREADS=1
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1

run_backend_cone() {
  worktree="$1"
  python="$2"
  tag="$3"

  (
    cd "$worktree" || exit 97
    PYTHONPATH="$worktree" "$python" -m pytest -q \
      tests/test_backend_policy.py \
      tests/test_backend_integration.py \
      tests/test_backend_packaging.py
  ) >"$OUT/${tag}_backend.log" 2>&1

  rc=$?

  grep -E '^FAILED |^ERROR ' "$OUT/${tag}_backend.log" | \
    sed -E 's/ - .*//' | \
    sort -u >"$OUT/${tag}_failures.txt" 2>/dev/null || true

  return "$rc"
}

run_backend_cone "$WORKTREE_RED" "$VENV_RED/bin/python" red
RC_BACKEND_RED=$?

run_backend_cone "$WORKTREE_GREEN" "$VENV_GREEN/bin/python" green
RC_BACKEND_GREEN=$?

diff -u "$OUT/red_failures.txt" "$OUT/green_failures.txt" \
  >"$OUT/failure_diff.txt" 2>&1
RC_FAILURE_DIFF=$?

(
  cd "$WORKTREE_GREEN" || exit 97
  PYTHONPATH="$WORKTREE_GREEN" "$VENV_GREEN/bin/python" \
    -m unittest -q \
    tests/research/test_bass_rec_source_protocol_red.py \
    tests/research/test_bass_rec_source_protocol_r6_red.py
) >"$OUT/green_focused.log" 2>&1
RC_FOCUSED=$?

: >"$OUT/source_hashes.txt"
: >"$OUT/binding_hashes.txt"

for run_index in 1 2; do
  (
    cd "$WORKTREE_GREEN" || exit 97
    PYTHONPATH="$WORKTREE_GREEN" "$VENV_GREEN/bin/python" - <<'PY'
from bianchi.source_authority import SourceAuthorityBundle, SourceFrequencyKind
bundle = SourceAuthorityBundle.constant_pair(
    eta_s_inv=3.0,
    kappa_s_inv=2.0,
    frame="hydrogen_orthonormal",
    channel="total_occupation",
    source_sha256="0" * 64,
    frequency_kind=SourceFrequencyKind.POINTWISE_SPECTRAL,
)
print(bundle.payload_sha256)
PY
  ) >>"$OUT/source_hashes.txt" 2>>"$OUT/hash_errors.log"

  (
    cd "$WORKTREE_GREEN" || exit 97
    PYTHONPATH="$WORKTREE_GREEN" "$VENV_GREEN/bin/python" - <<'PY'
from bianchi.source_authority import IntegratedMomentMapBinding, SourceStateKind
binding = IntegratedMomentMapBinding.create(
    target_state_kind=SourceStateKind.RADIAL_INTEGRATED_ANGULAR_GRID,
    moment_map_sha256="1" * 64,
    radial_weight_family_sha256="2" * 64,
    source_sha256="3" * 64,
)
print(binding.binding_sha256)
PY
  ) >>"$OUT/binding_hashes.txt" 2>>"$OUT/hash_errors.log"
done

SOURCE_HASH_1="$(sed -n '1p' "$OUT/source_hashes.txt")"
SOURCE_HASH_2="$(sed -n '2p' "$OUT/source_hashes.txt")"
BINDING_HASH_1="$(sed -n '1p' "$OUT/binding_hashes.txt")"
BINDING_HASH_2="$(sed -n '2p' "$OUT/binding_hashes.txt")"

HASHES_PASS=false
if [ "$SOURCE_HASH_1" = "$SOURCE_PAYLOAD_SHA256" ] && \
   [ "$SOURCE_HASH_2" = "$SOURCE_PAYLOAD_SHA256" ] && \
   [ "$BINDING_HASH_1" = "$INTEGRATED_BINDING_SHA256" ] && \
   [ "$BINDING_HASH_2" = "$INTEGRATED_BINDING_SHA256" ]; then
  HASHES_PASS=true
fi

git -C "$WORKTREE_RED" status --porcelain=v1 --untracked-files=all \
  >"$OUT/red_status.txt"
git -C "$WORKTREE_GREEN" status --porcelain=v1 --untracked-files=all \
  >"$OUT/green_status.txt"

CLEAN_WORKTREES=false
if [ ! -s "$OUT/red_status.txt" ] && [ ! -s "$OUT/green_status.txt" ]; then
  CLEAN_WORKTREES=true
fi

{
  printf 'RED staging artifacts:\n'
  find "$STAGE_RED" -maxdepth 3 \
    \( -type d -name build -o -type d -name '*.egg-info' \) \
    -print 2>/dev/null | sort
  printf '\nGREEN staging artifacts:\n'
  find "$STAGE_GREEN" -maxdepth 3 \
    \( -type d -name build -o -type d -name '*.egg-info' \) \
    -print 2>/dev/null | sort
} >"$OUT/staging_artifact_inventory.txt"

CLASSIFICATION='UNRESOLVED_R6C_CLEANLINESS_REPLAY'

if [ "$RC_BACKEND_RED" -eq 0 ] && \
   [ "$RC_BACKEND_GREEN" -eq 0 ] && \
   [ "$RC_FOCUSED" -eq 0 ] && \
   [ "$HASHES_PASS" = true ] && \
   [ "$CLEAN_WORKTREES" = true ]; then
  CLASSIFICATION='PASS_BASS_REC_SOURCE_R6C_CLEAN_BACKEND_NONREGRESSION'
elif [ "$RC_BACKEND_RED" -eq 0 ] && \
     [ "$RC_BACKEND_GREEN" -ne 0 ]; then
  CLASSIFICATION='FAIL_R6_GREEN_CANDIDATE_INDUCED_BACKEND_REGRESSION'
elif [ "$RC_BACKEND_RED" -ne 0 ] && \
     [ "$RC_BACKEND_GREEN" -ne 0 ] && \
     [ "$RC_FAILURE_DIFF" -eq 0 ]; then
  CLASSIFICATION='BLOCKED_INHERITED_BACKEND_FAILURE'
elif [ "$RC_FOCUSED" -ne 0 ] || [ "$HASHES_PASS" != true ]; then
  CLASSIFICATION='FAIL_R6_GREEN_PROTOCOL_OR_HASH'
elif [ "$CLEAN_WORKTREES" != true ]; then
  CLASSIFICATION='FAIL_R6C_SOURCE_WORKTREE_DIRTY_AFTER_STAGED_BUILD'
fi

cat >"$OUT/summary.txt" <<EOF
classification=$CLASSIFICATION
red_parent=$RED_PARENT
green_source=$GREEN_SOURCE
publication_head=$PUBLICATION_HEAD
green_tree=$ACTUAL_GREEN_TREE
green_source_blob=$ACTUAL_GREEN_BLOB
native_wheel_sha256=$NATIVE_WHEEL_SHA256
python=$PYVER
red_backend_rc=$RC_BACKEND_RED
green_backend_rc=$RC_BACKEND_GREEN
failure_sets_identical=$([ "$RC_FAILURE_DIFF" -eq 0 ] && echo true || echo false)
green_focused_rc=$RC_FOCUSED
deterministic_golden_hashes=$HASHES_PASS
source_hash_1=$SOURCE_HASH_1
source_hash_2=$SOURCE_HASH_2
binding_hash_1=$BINDING_HASH_1
binding_hash_2=$BINDING_HASH_2
clean_worktrees=$CLEAN_WORKTREES
build_location=NON_GIT_STAGING_DIRECTORIES
receipt_dir=$OUT
EOF

cat "$OUT/summary.txt"

cat >"$OUT/R6C_CLEANLINESS_REPLAY_RECEIPT.json" <<EOF
{
  "schema_version": "1.0.0",
  "stage": "BASS_REC_SOURCE_R6C_CLEANLINESS_ONLY_DIFFERENTIAL_REPLAY",
  "classification": "$CLASSIFICATION",
  "red_parent": "$RED_PARENT",
  "green_source": "$GREEN_SOURCE",
  "publication_head": "$PUBLICATION_HEAD",
  "native_wheel_sha256": "$NATIVE_WHEEL_SHA256",
  "red_backend_rc": $RC_BACKEND_RED,
  "green_backend_rc": $RC_BACKEND_GREEN,
  "failure_sets_identical": $([ "$RC_FAILURE_DIFF" -eq 0 ] && echo true || echo false),
  "green_focused_rc": $RC_FOCUSED,
  "deterministic_golden_hashes": $HASHES_PASS,
  "clean_worktrees": $CLEAN_WORKTREES,
  "root_package_build_location": "non_git_staging_directories",
  "claim_boundary": {
    "R6_behavior_level_nonregression": $([ "$CLASSIFICATION" = "PASS_BASS_REC_SOURCE_R6C_CLEAN_BACKEND_NONREGRESSION" ] && echo true || echo false),
    "trusted_native_payload": false,
    "physical_REC_source_integration": false,
    "grid_PSTF_adapter": false,
    "grid_PSTF_parity": false,
    "physical_face": false,
    "provider_export": false,
    "pass_RF04": false
  }
}
EOF

sha256sum "$OUT"/* >"$OUT/SHA256SUMS" 2>/dev/null || true

printf '\nCaller checkout was not switched or modified.\n'
exit 0
