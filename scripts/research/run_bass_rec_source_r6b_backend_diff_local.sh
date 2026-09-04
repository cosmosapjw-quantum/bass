#!/usr/bin/env bash
# BASS_REC_SOURCE_R6B_PARENT_CANDIDATE_BACKEND_DIFFERENTIAL
#
# Compare the coherent R6 RED parent and exact R6 GREEN source under the same
# locked Python stack and the same previously qualified source-built native
# wheel. The caller checkout is never switched or modified. The script records
# its own classification and always exits 0.
#
# Optional:
#   BASS_REPO=/absolute/path/to/bass
#   PYTHON_BOOTSTRAP=/absolute/path/to/python3.12
#   RECEIPT_ROOT=/absolute/path/to/receipt/root

set +e
set +u
set +o pipefail 2>/dev/null || true

BASE='0a4875e5c18419a672c164eb5c849f3f4ab01571'
GREEN='92d67dc79cf645947beb93ac01a9505ee277dabd'
BRANCH='research/bass-rec-source-r6-hardening-green-20260904-r1'
GREEN_TREE='65cb63e6d08e80e9a8f38f83e3a536cb0a00a693'
GREEN_BLOB='869677390004f68aef9f547e6556f5f1c15bd012'
R5_BLOB='db336d64633d8a9552bc3613c588a00f33404a4d'
R6_BLOB='49be9546c4655bc5ca330bc31ae2daf07578b74f'
WHEEL_GOLDEN='bf5a59534ffc9d6f9c3410aa19319f18a4a8a7a9761bcd61c5da8c8627ddf609'
SOURCE_GOLDEN='7f0db7e1cf7423ff6751a21ab4002ef8f13d89f788a8a746b26992abecf791e8'
BINDING_GOLDEN='54762aa915b3fa0da847676a3d4491b8f7f2f358e48dd275fffee84ba6496093'

ROOT="${RECEIPT_ROOT:-$HOME/Dropbox/bianchi/_runtime_receipts}"
OUT="$ROOT/BASS_REC_SOURCE_R6B_$(date -u +%Y%m%dT%H%M%SZ)"
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
case "$PYVER" in 3.12.*) ;; *) stop_gate STOP_WRONG_PYTHON_VERSION "$PYVER" ;; esac

git -C "$BASS" fetch --no-tags origin \
  "$BRANCH:refs/remotes/origin/$BRANCH" >"$OUT/fetch.log" 2>&1
RC_FETCH=$?
PUB="$(git -C "$BASS" rev-parse "refs/remotes/origin/$BRANCH" 2>/dev/null)"
if [ "$RC_FETCH" -ne 0 ] || [ -z "$PUB" ]; then
  stop_gate STOP_FETCH_FAILURE 'publication branch unavailable'
fi
git -C "$BASS" merge-base --is-ancestor "$GREEN" "$PUB" >/dev/null 2>&1
[ "$?" -eq 0 ] || stop_gate STOP_GREEN_NOT_PUBLICATION_ANCESTOR "$PUB"

WHEEL="$(find "$ROOT" -type f -name 'bianchi_rustcore-0.1.0-*.whl' -print 2>/dev/null | while IFS= read -r F; do S="$(sha256sum "$F" 2>/dev/null | awk '{print $1}')"; if [ "$S" = "$WHEEL_GOLDEN" ]; then printf '%s\n' "$F"; break; fi; done)"
[ -f "$WHEEL" ] || stop_gate STOP_GOLDEN_NATIVE_WHEEL_NOT_FOUND "$WHEEL_GOLDEN"

TMP="$(mktemp -d /tmp/bass-r6b.XXXXXX 2>/dev/null)"
[ -d "$TMP" ] || stop_gate STOP_TEMP_DIRECTORY_FAILURE "$TMP"
WB="$TMP/base"; WG="$TMP/green"; VB="$TMP/venv-base"; VG="$TMP/venv-green"
cleanup() {
  git -C "$BASS" worktree remove --force "$WB" >/dev/null 2>&1 || true
  git -C "$BASS" worktree remove --force "$WG" >/dev/null 2>&1 || true
  case "$TMP" in /tmp/bass-r6b.*) rm -rf -- "$TMP" >/dev/null 2>&1 || true ;; esac
}
trap cleanup EXIT HUP INT TERM

git -C "$BASS" worktree add --detach "$WB" "$BASE" >"$OUT/worktree_base.log" 2>&1
RC_WB=$?
git -C "$BASS" worktree add --detach "$WG" "$GREEN" >"$OUT/worktree_green.log" 2>&1
RC_WG=$?
if [ "$RC_WB" -ne 0 ] || [ "$RC_WG" -ne 0 ]; then
  stop_gate STOP_WORKTREE_FAILURE "base=$RC_WB green=$RC_WG"
fi

GT="$(git -C "$WG" rev-parse HEAD^{tree} 2>/dev/null)"
GB="$(git -C "$WG" hash-object bianchi/source_authority.py 2>/dev/null)"
T5="$(git -C "$WG" hash-object tests/research/test_bass_rec_source_protocol_red.py 2>/dev/null)"
T6="$(git -C "$WG" hash-object tests/research/test_bass_rec_source_protocol_r6_red.py 2>/dev/null)"
if [ "$GT" != "$GREEN_TREE" ] || [ "$GB" != "$GREEN_BLOB" ] || [ "$T5" != "$R5_BLOB" ] || [ "$T6" != "$R6_BLOB" ]; then
  stop_gate STOP_GREEN_IDENTITY_MISMATCH "$GT $GB $T5 $T6"
fi

BASE_RUST="$(git -C "$WB" rev-parse HEAD:_rustcore 2>/dev/null)"
GREEN_RUST="$(git -C "$WG" rev-parse HEAD:_rustcore 2>/dev/null)"
BASE_LOCK="$(git -C "$WB" rev-parse HEAD:requirements.lock 2>/dev/null)"
GREEN_LOCK="$(git -C "$WG" rev-parse HEAD:requirements.lock 2>/dev/null)"
BASE_PROJECT="$(git -C "$WB" rev-parse HEAD:pyproject.toml 2>/dev/null)"
GREEN_PROJECT="$(git -C "$WG" rev-parse HEAD:pyproject.toml 2>/dev/null)"
if [ "$BASE_RUST" != "$GREEN_RUST" ] || [ "$BASE_LOCK" != "$GREEN_LOCK" ] || [ "$BASE_PROJECT" != "$GREEN_PROJECT" ]; then
  stop_gate STOP_DIFFERENTIAL_ENVIRONMENT_INPUT_DRIFT 'native tree, requirements.lock, or pyproject.toml differs'
fi
git -C "$WG" diff --name-status "$BASE" "$GREEN" >"$OUT/source_diff_name_status.txt" 2>&1

prepare_env() {
  WT="$1"; VENV="$2"; TAG="$3"
  "$PYBOOT" -m venv "$VENV" >"$OUT/${TAG}_venv.log" 2>&1 || return 31
  "$VENV/bin/python" -m pip install --disable-pip-version-check -r "$WT/requirements.lock" >"$OUT/${TAG}_requirements.log" 2>&1 || return 32
  (cd "$WT" && "$VENV/bin/python" -m pip install --disable-pip-version-check --constraint requirements.lock "$WHEEL" .) >"$OUT/${TAG}_project.log" 2>&1 || return 33
  return 0
}
prepare_env "$WB" "$VB" base; RC_ENV_BASE=$?
prepare_env "$WG" "$VG" green; RC_ENV_GREEN=$?
if [ "$RC_ENV_BASE" -ne 0 ] || [ "$RC_ENV_GREEN" -ne 0 ]; then
  stop_gate STOP_ENVIRONMENT_INSTALL_FAILURE "base=$RC_ENV_BASE green=$RC_ENV_GREEN"
fi

export BASS_ALLOW_UNVERIFIED_NATIVE_DEV=1
export RAYON_NUM_THREADS=1
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1

run_backend_cone() {
  WT="$1"; PY="$2"; TAG="$3"
  (cd "$WT" && PYTHONPATH="$WT" "$PY" -m pytest -q tests/test_backend_policy.py tests/test_backend_integration.py tests/test_backend_packaging.py) >"$OUT/${TAG}_backend.log" 2>&1
  RC=$?
  grep -E '^FAILED |^ERROR ' "$OUT/${TAG}_backend.log" | sed -E 's/ - .*//' | sort -u >"$OUT/${TAG}_failures.txt" 2>/dev/null || true
  return "$RC"
}
run_backend_cone "$WB" "$VB/bin/python" base; RC_BASE=$?
run_backend_cone "$WG" "$VG/bin/python" green; RC_GREEN=$?
diff -u "$OUT/base_failures.txt" "$OUT/green_failures.txt" >"$OUT/failure_diff.txt" 2>&1
RC_DIFF=$?

(cd "$WG" && PYTHONPATH="$WG" "$VG/bin/python" -m unittest -q tests/research/test_bass_rec_source_protocol_red.py tests/research/test_bass_rec_source_protocol_r6_red.py) >"$OUT/green_focused.log" 2>&1
RC_FOCUSED=$?

: >"$OUT/source_hashes.txt"; : >"$OUT/binding_hashes.txt"
for N in 1 2; do
  (cd "$WG" && PYTHONPATH="$WG" "$VG/bin/python" - <<'PY'
from bianchi.source_authority import SourceAuthorityBundle, SourceFrequencyKind
b=SourceAuthorityBundle.constant_pair(eta_s_inv=3.0,kappa_s_inv=2.0,frame="hydrogen_orthonormal",channel="total_occupation",source_sha256="0"*64,frequency_kind=SourceFrequencyKind.POINTWISE_SPECTRAL)
print(b.payload_sha256)
PY
  ) >>"$OUT/source_hashes.txt" 2>>"$OUT/hash_errors.log"
  (cd "$WG" && PYTHONPATH="$WG" "$VG/bin/python" - <<'PY'
from bianchi.source_authority import IntegratedMomentMapBinding, SourceStateKind
b=IntegratedMomentMapBinding.create(target_state_kind=SourceStateKind.RADIAL_INTEGRATED_ANGULAR_GRID,moment_map_sha256="1"*64,radial_weight_family_sha256="2"*64,source_sha256="3"*64)
print(b.binding_sha256)
PY
  ) >>"$OUT/binding_hashes.txt" 2>>"$OUT/hash_errors.log"
done
S1="$(sed -n '1p' "$OUT/source_hashes.txt")"; S2="$(sed -n '2p' "$OUT/source_hashes.txt")"
B1="$(sed -n '1p' "$OUT/binding_hashes.txt")"; B2="$(sed -n '2p' "$OUT/binding_hashes.txt")"
HASH_OK=false
if [ "$S1" = "$SOURCE_GOLDEN" ] && [ "$S2" = "$SOURCE_GOLDEN" ] && [ "$B1" = "$BINDING_GOLDEN" ] && [ "$B2" = "$BINDING_GOLDEN" ]; then HASH_OK=true; fi

git -C "$WB" status --porcelain >"$OUT/base_status.txt"
git -C "$WG" status --porcelain >"$OUT/green_status.txt"
CLEAN=false
if [ ! -s "$OUT/base_status.txt" ] && [ ! -s "$OUT/green_status.txt" ]; then CLEAN=true; fi

CLASS='UNRESOLVED_R6B_DIFFERENTIAL'
if [ "$RC_BASE" -eq 0 ] && [ "$RC_GREEN" -eq 0 ] && [ "$RC_FOCUSED" -eq 0 ] && [ "$HASH_OK" = true ] && [ "$CLEAN" = true ]; then
  CLASS='PASS_BASS_REC_SOURCE_R6B_NO_BACKEND_REGRESSION'
elif [ "$RC_BASE" -ne 0 ] && [ "$RC_GREEN" -ne 0 ] && [ "$RC_DIFF" -eq 0 ] && [ "$RC_FOCUSED" -eq 0 ] && [ "$HASH_OK" = true ]; then
  CLASS='PASS_R6B_CANDIDATE_NOT_CAUSAL_INHERITED_BACKEND_FAILURE'
elif [ "$RC_BASE" -eq 0 ] && [ "$RC_GREEN" -ne 0 ]; then
  CLASS='FAIL_R6_GREEN_CANDIDATE_INDUCED_BACKEND_REGRESSION'
elif [ "$RC_FOCUSED" -ne 0 ] || [ "$HASH_OK" != true ]; then
  CLASS='FAIL_R6_GREEN_PROTOCOL_OR_HASH'
fi

cat >"$OUT/summary.txt" <<EOF
classification=$CLASS
red_parent=$BASE
green_source=$GREEN
publication_head=$PUB
source_tree=$GT
source_blob=$GB
wheel_sha256=$WHEEL_GOLDEN
python=$PYVER
base_backend_rc=$RC_BASE
green_backend_rc=$RC_GREEN
failure_sets_identical=$([ "$RC_DIFF" -eq 0 ] && echo true || echo false)
green_focused_rc=$RC_FOCUSED
deterministic_golden_hashes=$HASH_OK
source_hash_1=$S1
source_hash_2=$S2
binding_hash_1=$B1
binding_hash_2=$B2
clean_worktrees=$CLEAN
receipt_dir=$OUT
EOF
cat "$OUT/summary.txt"
sha256sum "$OUT"/* >"$OUT/SHA256SUMS" 2>/dev/null || true
printf '\nCaller checkout was not switched or modified.\n'
exit 0
