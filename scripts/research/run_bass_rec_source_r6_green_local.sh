#!/usr/bin/env bash
# BASS_REC_SOURCE_R6_GREEN_LOCAL_EXACT_REPLAY
#
# Run from any directory.  This script never switches or modifies the caller's
# checkout.  It fetches the publication branch, verifies that the exact source
# candidate is an ancestor, creates a detached worktree at that immutable source
# commit, executes the focused suites and adversarial probes, generates a
# standard-library SVG, and writes durable receipts.
#
# Optional overrides:
#   BASS_REPO=/absolute/path/to/bass
#   PYTHON=/absolute/path/to/python3.12
#   RECEIPT_ROOT=/absolute/path/to/receipt/root

set +e
set +u
set +o pipefail 2>/dev/null || true

BRANCH='research/bass-rec-source-r6-hardening-green-20260904-r1'
SOURCE_COMMIT='92d67dc79cf645947beb93ac01a9505ee277dabd'
SOURCE_TREE='65cb63e6d08e80e9a8f38f83e3a536cb0a00a693'
SOURCE_BLOB='869677390004f68aef9f547e6556f5f1c15bd012'
R5_TEST_BLOB='db336d64633d8a9552bc3613c588a00f33404a4d'
R6_TEST_BLOB='49be9546c4655bc5ca330bc31ae2daf07578b74f'

ROOT="${RECEIPT_ROOT:-$HOME/Dropbox/bianchi/_runtime_receipts}"
OUT="$ROOT/BASS_REC_SOURCE_R6_GREEN_$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$OUT" 2>/dev/null
if [ ! -d "$OUT" ]; then
  printf 'classification=STOP_RECEIPT_DIRECTORY_UNAVAILABLE\n'
  exit 0
fi

say() { printf '\n===== %s =====\n' "$*" | tee -a "$OUT/master.log"; }
kv() { printf '%s=%s\n' "$1" "$2" | tee -a "$OUT/master.log"; }

is_bass_repo() {
  CANDIDATE="$1"
  [ -n "$CANDIDATE" ] || return 1
  TOP="$(git -C "$CANDIDATE" rev-parse --show-toplevel 2>/dev/null)"
  [ -n "$TOP" ] || return 1
  ORIGIN="$(git -C "$TOP" config --get remote.origin.url 2>/dev/null)"
  case "$ORIGIN" in
    *cosmosapjw-quantum/bass|*cosmosapjw-quantum/bass.git)
      printf '%s\n' "$TOP"
      return 0
      ;;
    *) return 1 ;;
  esac
}

say 'CALLER CONTEXT'
kv caller_pwd "$PWD"
kv caller_head "$(git rev-parse HEAD 2>/dev/null || printf NOT_GIT)"
kv caller_origin "$(git config --get remote.origin.url 2>/dev/null || printf UNAVAILABLE)"

say 'LOCATE BASS'
BASS=''
if [ -n "${BASS_REPO:-}" ]; then
  BASS="$(is_bass_repo "$BASS_REPO")"
fi
if [ -z "$BASS" ]; then
  for C in "$HOME/Dropbox/bianchi/bass" "$HOME/Dropbox/bass" "$HOME/bass"; do
    BASS="$(is_bass_repo "$C")"
    [ -n "$BASS" ] && break
  done
fi
if [ -z "$BASS" ]; then
  printf 'classification=STOP_BASS_REPOSITORY_NOT_FOUND\n' | tee "$OUT/summary.txt"
  exit 0
fi
kv bass_repo "$BASS"
kv bass_origin "$(git -C "$BASS" config --get remote.origin.url 2>/dev/null)"

say 'SELECT PYTHON 3.12'
PY="${PYTHON:-$(command -v python3.12 2>/dev/null)}"
[ -x "$PY" ] || PY="$(command -v python 2>/dev/null)"
if [ ! -x "$PY" ]; then
  printf 'classification=STOP_PYTHON_NOT_FOUND\n' | tee "$OUT/summary.txt"
  exit 0
fi
PYVER="$($PY -c 'import sys; print(".".join(map(str,sys.version_info[:3])))' 2>/dev/null)"
kv python "$PY"
kv python_version "$PYVER"
case "$PYVER" in
  3.12.*) ;;
  *)
    printf 'classification=STOP_WRONG_PYTHON_VERSION\nactual=%s\n' "$PYVER" \
      | tee "$OUT/summary.txt"
    exit 0
    ;;
esac

say 'FETCH PUBLICATION BRANCH'
git -C "$BASS" fetch --no-tags origin \
  "$BRANCH:refs/remotes/origin/$BRANCH" >"$OUT/fetch.log" 2>&1
RC_FETCH=$?
REMOTE_HEAD="$(git -C "$BASS" rev-parse "refs/remotes/origin/$BRANCH" 2>/dev/null)"
kv fetch_rc "$RC_FETCH"
kv remote_head "${REMOTE_HEAD:-UNAVAILABLE}"
if [ "$RC_FETCH" -ne 0 ] || [ -z "$REMOTE_HEAD" ]; then
  printf 'classification=STOP_FETCH_FAILURE\n' | tee "$OUT/summary.txt"
  exit 0
fi
if ! git -C "$BASS" cat-file -e "$SOURCE_COMMIT^{commit}" 2>/dev/null; then
  printf 'classification=STOP_SOURCE_COMMIT_UNAVAILABLE\n' | tee "$OUT/summary.txt"
  exit 0
fi
git -C "$BASS" merge-base --is-ancestor "$SOURCE_COMMIT" "$REMOTE_HEAD"
RC_ANCESTOR=$?
kv source_commit_is_ancestor "$([ "$RC_ANCESTOR" -eq 0 ] && echo true || echo false)"
if [ "$RC_ANCESTOR" -ne 0 ]; then
  printf 'classification=STOP_SOURCE_NOT_ANCESTOR_OF_PUBLICATION_HEAD\n' \
    | tee "$OUT/summary.txt"
  exit 0
fi

say 'CREATE DETACHED SOURCE WORKTREE'
TMP="$(mktemp -d /tmp/bass-rec-r6-green.XXXXXX 2>/dev/null)"
WT="$TMP/worktree"
cleanup() {
  git -C "$BASS" worktree remove --force "$WT" >/dev/null 2>&1 || true
  case "$TMP" in
    /tmp/bass-rec-r6-green.*) rm -rf -- "$TMP" >/dev/null 2>&1 || true ;;
  esac
}
trap cleanup EXIT HUP INT TERM

git -C "$BASS" worktree add --detach "$WT" "$SOURCE_COMMIT" \
  >"$OUT/worktree.log" 2>&1
RC_WT=$?
if [ "$RC_WT" -ne 0 ]; then
  printf 'classification=STOP_WORKTREE_FAILURE\n' | tee "$OUT/summary.txt"
  exit 0
fi

HEAD_ACTUAL="$(git -C "$WT" rev-parse HEAD 2>/dev/null)"
TREE_ACTUAL="$(git -C "$WT" rev-parse HEAD^{tree} 2>/dev/null)"
SOURCE_ACTUAL="$(git -C "$WT" hash-object bianchi/source_authority.py 2>/dev/null)"
R5_ACTUAL="$(git -C "$WT" hash-object tests/research/test_bass_rec_source_protocol_red.py 2>/dev/null)"
R6_ACTUAL="$(git -C "$WT" hash-object tests/research/test_bass_rec_source_protocol_r6_red.py 2>/dev/null)"

kv source_commit "$HEAD_ACTUAL"
kv source_tree "$TREE_ACTUAL"
kv source_blob "$SOURCE_ACTUAL"
kv r5_test_blob "$R5_ACTUAL"
kv r6_test_blob "$R6_ACTUAL"

if [ "$HEAD_ACTUAL" != "$SOURCE_COMMIT" ] || \
   [ "$TREE_ACTUAL" != "$SOURCE_TREE" ] || \
   [ "$SOURCE_ACTUAL" != "$SOURCE_BLOB" ] || \
   [ "$R5_ACTUAL" != "$R5_TEST_BLOB" ] || \
   [ "$R6_ACTUAL" != "$R6_TEST_BLOB" ]; then
  printf 'classification=STOP_EXACT_IDENTITY_MISMATCH\n' | tee "$OUT/summary.txt"
  exit 0
fi

say 'PY_COMPILE'
(
  cd "$WT" || exit 97
  PYTHONPATH="$WT" "$PY" -m py_compile bianchi/source_authority.py
) >"$OUT/py_compile.log" 2>&1
RC_COMPILE=$?
kv compile_rc "$RC_COMPILE"

run_suite() {
  MODULE_NAME="$1"
  EXPECTED_COUNT="$2"
  JSON_PATH="$3"
  VERBOSE_PATH="$4"
  (
    cd "$WT" || exit 97
    PYTHONPATH="$WT" "$PY" - "$MODULE_NAME" "$EXPECTED_COUNT" <<'PY'
import io
import json
import sys
import unittest

name = sys.argv[1]
expected = int(sys.argv[2])
stream = io.StringIO()
suite = unittest.defaultTestLoader.loadTestsFromName(name)
result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
summary = {
    "suite": name,
    "tests_run": result.testsRun,
    "failures": [case.id() for case, _ in result.failures],
    "errors": [case.id() for case, _ in result.errors],
    "skipped": [case.id() for case, _ in result.skipped],
}
summary["pass"] = (
    result.testsRun == expected
    and not result.failures
    and not result.errors
    and not result.skipped
)
print(json.dumps(summary, indent=2, sort_keys=True))
print(stream.getvalue(), file=sys.stderr)
raise SystemExit(0 if summary["pass"] else 1)
PY
  ) >"$JSON_PATH" 2>"$VERBOSE_PATH"
  return $?
}

say 'R5 STABLE SURVIVORS'
run_suite \
  tests.research.test_bass_rec_source_protocol_red \
  11 "$OUT/r5_result.json" "$OUT/r5_verbose.log"
RC_R5=$?
kv r5_survivor_rc "$RC_R5"

say 'R6 AUTHORITY HARDENING'
run_suite \
  tests.research.test_bass_rec_source_protocol_r6_red \
  10 "$OUT/r6_result.json" "$OUT/r6_verbose.log"
RC_R6=$?
kv r6_hardening_rc "$RC_R6"

say 'TWO-PROCESS SOURCE AND BINDING HASHES'
: >"$OUT/source_hashes.txt"
: >"$OUT/binding_hashes.txt"
for N in 1 2; do
  (
    cd "$WT" || exit 97
    PYTHONPATH="$WT" "$PY" - <<'PY'
from bianchi.source_authority import SourceAuthorityBundle, SourceFrequencyKind
b = SourceAuthorityBundle.constant_pair(
    eta_s_inv=3.0,
    kappa_s_inv=2.0,
    frame="hydrogen_orthonormal",
    channel="total_occupation",
    source_sha256="0"*64,
    frequency_kind=SourceFrequencyKind.POINTWISE_SPECTRAL,
)
print(b.payload_sha256)
PY
  ) >>"$OUT/source_hashes.txt" 2>>"$OUT/hash_errors.log"
  (
    cd "$WT" || exit 97
    PYTHONPATH="$WT" "$PY" - <<'PY'
from bianchi.source_authority import IntegratedMomentMapBinding, SourceStateKind
b = IntegratedMomentMapBinding.create(
    target_state_kind=SourceStateKind.RADIAL_INTEGRATED_ANGULAR_GRID,
    moment_map_sha256="1"*64,
    radial_weight_family_sha256="2"*64,
    source_sha256="3"*64,
)
print(b.binding_sha256)
PY
  ) >>"$OUT/binding_hashes.txt" 2>>"$OUT/hash_errors.log"
done
SOURCE_H1="$(sed -n '1p' "$OUT/source_hashes.txt")"
SOURCE_H2="$(sed -n '2p' "$OUT/source_hashes.txt")"
BIND_H1="$(sed -n '1p' "$OUT/binding_hashes.txt")"
BIND_H2="$(sed -n '2p' "$OUT/binding_hashes.txt")"
HASH_RE='^[0-9a-f]{64}$'
HASH_OK=0
if [[ "$SOURCE_H1" =~ $HASH_RE ]] && [ "$SOURCE_H1" = "$SOURCE_H2" ] && \
   [[ "$BIND_H1" =~ $HASH_RE ]] && [ "$BIND_H1" = "$BIND_H2" ]; then
  HASH_OK=1
fi
kv source_hash_1 "${SOURCE_H1:-MISSING}"
kv source_hash_2 "${SOURCE_H2:-MISSING}"
kv binding_hash_1 "${BIND_H1:-MISSING}"
kv binding_hash_2 "${BIND_H2:-MISSING}"
kv deterministic_hashes "$([ "$HASH_OK" -eq 1 ] && echo true || echo false)"

say 'ADVERSARIAL AUTHORITY PROBES AND PLOT DATA'
(
  cd "$WT" || exit 97
  PYTHONPATH="$WT" "$PY" - "$OUT" <<'PY'
from __future__ import annotations

import html
import json
import math
from pathlib import Path
import sys

from bianchi.source_authority import (
    IntegratedMomentMapBinding,
    SourceArithmeticError,
    SourceAuthorityBundle,
    SourceFrequencyKind,
    SourceRepresentationError,
    SourceSpecies,
    SourceStateKind,
    SourceStatistics,
    require_source_representation_compatibility,
)

out = Path(sys.argv[1])
checks: dict[str, bool] = {}

try:
    SourceAuthorityBundle(
        eta_s_inv=-1.0,
        kappa_s_inv=math.nan,
        frame=" ",
        channel=" ",
        source_sha256="not-a-sha256",
        frequency_kind="pointwise_spectral",
        payload_sha256="f"*64,
    )
except TypeError:
    checks["direct_constructor_blocked"] = True
else:
    checks["direct_constructor_blocked"] = False

plus = SourceAuthorityBundle.constant_pair(
    eta_s_inv=0.0,
    kappa_s_inv=0.0,
    frame="hydrogen_orthonormal",
    channel="total_occupation",
    source_sha256="0"*64,
    frequency_kind=SourceFrequencyKind.POINTWISE_SPECTRAL,
)
minus = SourceAuthorityBundle.constant_pair(
    eta_s_inv=-0.0,
    kappa_s_inv=-0.0,
    frame="hydrogen_orthonormal",
    channel="total_occupation",
    source_sha256="0"*64,
    frequency_kind=SourceFrequencyKind.POINTWISE_SPECTRAL,
)
checks["signed_zero_canonical"] = (
    math.copysign(1.0, minus.eta_s_inv) == 1.0
    and math.copysign(1.0, minus.kappa_s_inv) == 1.0
    and plus.payload_sha256 == minus.payload_sha256
)

sample = SourceAuthorityBundle.constant_pair(
    eta_s_inv=3.0,
    kappa_s_inv=2.0,
    frame="hydrogen_orthonormal",
    channel="total_occupation",
    source_sha256="0"*64,
    frequency_kind=SourceFrequencyKind.POINTWISE_SPECTRAL,
)
checks["species_statistics_schema"] = (
    sample.species is SourceSpecies.PHOTON
    and sample.statistics is SourceStatistics.BOSON
    and sample.payload_schema == "bass.source_authority.constant_pair.v2"
)

try:
    SourceAuthorityBundle.constant_pair(
        eta_s_inv=1.0,
        kappa_s_inv=1.0,
        frame="hydrogen_orthonormal",
        channel="total_occupation",
        source_sha256="0"*64,
        frequency_kind=SourceFrequencyKind.SOURCE_INTEGRATED_WITNESS,
    )
except SourceRepresentationError:
    checks["constant_pair_cannot_be_integrated"] = True
else:
    checks["constant_pair_cannot_be_integrated"] = False

try:
    require_source_representation_compatibility(
        SourceFrequencyKind.SOURCE_INTEGRATED_WITNESS,
        SourceStateKind.RADIAL_INTEGRATED_ANGULAR_GRID,
    )
except SourceRepresentationError:
    checks["unbound_integrated_rejected"] = True
else:
    checks["unbound_integrated_rejected"] = False

binding = IntegratedMomentMapBinding.create(
    target_state_kind=SourceStateKind.RADIAL_INTEGRATED_ANGULAR_GRID,
    moment_map_sha256="1"*64,
    radial_weight_family_sha256="2"*64,
    source_sha256="3"*64,
)
require_source_representation_compatibility(
    SourceFrequencyKind.SOURCE_INTEGRATED_WITNESS,
    SourceStateKind.RADIAL_INTEGRATED_ANGULAR_GRID,
    integrated_binding=binding,
)
try:
    require_source_representation_compatibility(
        SourceFrequencyKind.SOURCE_INTEGRATED_WITNESS,
        SourceStateKind.FINITE_INTEGRATED_J_HIERARCHY,
        integrated_binding=binding,
    )
except SourceRepresentationError:
    checks["binding_is_target_specific"] = True
else:
    checks["binding_is_target_specific"] = False

huge = SourceAuthorityBundle.constant_pair(
    eta_s_inv=1.0e308,
    kappa_s_inv=0.0,
    frame="hydrogen_orthonormal",
    channel="total_occupation",
    source_sha256="0"*64,
    frequency_kind=SourceFrequencyKind.POINTWISE_SPECTRAL,
)
try:
    huge.pointwise_action(1.0e308)
except SourceArithmeticError:
    checks["pointwise_overflow_rejected"] = True
else:
    checks["pointwise_overflow_rejected"] = False
try:
    huge.rates_per_tau(H_s_inv=1.0e-308)
except SourceArithmeticError:
    checks["q_time_overflow_rejected"] = True
else:
    checks["q_time_overflow_rejected"] = False

# Generate deterministic source-branch data and a dependency-free SVG.  This
# is a protocol-mathematics diagnostic, not solver or observational evidence.
fixtures = [
    ("absorptive", 1.0, 3.0, ""),
    ("chi_zero", 2.0, 2.0, "6,4"),
    ("stimulated_growth", 3.0, 2.0, "2,4"),
]
xs = [i / 20.0 for i in range(101)]
curves = []
for name, eta, kappa, dash in fixtures:
    bundle = SourceAuthorityBundle.constant_pair(
        eta_s_inv=eta,
        kappa_s_inv=kappa,
        frame="hydrogen_orthonormal",
        channel="total_occupation",
        source_sha256="0"*64,
        frequency_kind=SourceFrequencyKind.POINTWISE_SPECTRAL,
    )
    ys = [bundle.pointwise_action(x) for x in xs]
    curves.append({
        "name": name,
        "eta_s_inv": eta,
        "kappa_s_inv": kappa,
        "chi_affine_s_inv": bundle.chi_affine_s_inv,
        "dash": dash,
        "x": xs,
        "source": ys,
        "omitted_stimulated_emission_residual": [eta*x for x in xs],
    })

checks["source_off_control"] = plus.pointwise_action(10.0) == 0.0
checks["negative_chi_control"] = sample.pointwise_action(5.0) == 8.0
checks["branch_endpoints"] = (
    curves[0]["source"][-1] == -9.0
    and curves[1]["source"][-1] == 2.0
    and curves[2]["source"][-1] == 8.0
)

plot_data = {
    "schema": "bass.source_authority.r6.branch_plot.v1",
    "claim": "protocol mathematics only",
    "curves": curves,
    "checks": checks,
}
(out / "source_branch_audit.json").write_text(
    json.dumps(plot_data, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

width, height = 820, 500
left, right, top, bottom = 80, 30, 45, 70
xmin, xmax = 0.0, 5.0
ymin, ymax = -10.0, 9.0

def sx(x: float) -> float:
    return left + (x-xmin)/(xmax-xmin)*(width-left-right)

def sy(y: float) -> float:
    return top + (ymax-y)/(ymax-ymin)*(height-top-bottom)

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
    '<rect width="100%" height="100%" fill="white"/>',
    f'<line x1="{left}" y1="{sy(0)}" x2="{width-right}" y2="{sy(0)}" stroke="#777" stroke-width="1"/>',
    f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="black" stroke-width="1.5"/>',
    f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="black" stroke-width="1.5"/>',
    f'<text x="{width/2}" y="{height-22}" text-anchor="middle" font-size="16">occupation f</text>',
    f'<text x="20" y="{height/2}" transform="rotate(-90 20 {height/2})" text-anchor="middle" font-size="16">source C[f] (s^-1)</text>',
    f'<text x="{width/2}" y="24" text-anchor="middle" font-size="17">R6 photon/boson affine-source branches</text>',
]
for x in range(6):
    parts.append(f'<text x="{sx(float(x))}" y="{height-bottom+25}" text-anchor="middle" font-size="13">{x}</text>')
for y in (-10,-5,0,5):
    parts.append(f'<text x="{left-12}" y="{sy(float(y))+4}" text-anchor="end" font-size="13">{y}</text>')
for idx, curve in enumerate(curves):
    points = " ".join(
        f"{sx(x):.2f},{sy(y):.2f}" for x, y in zip(curve["x"], curve["source"])
    )
    dash = f' stroke-dasharray="{curve["dash"]}"' if curve["dash"] else ""
    parts.append(f'<polyline points="{points}" fill="none" stroke="black" stroke-width="2.2"{dash}/>')
    legend_y = 55 + 24*idx
    parts.append(f'<line x1="570" y1="{legend_y}" x2="610" y2="{legend_y}" stroke="black" stroke-width="2.2"{dash}/>')
    label = html.escape(f'{curve["name"]}: eta={curve["eta_s_inv"]:g}, kappa={curve["kappa_s_inv"]:g}')
    parts.append(f'<text x="620" y="{legend_y+5}" font-size="13">{label}</text>')
parts.append('</svg>')
(out / "source_branch_audit.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")

summary = {
    "all_checks_pass": all(checks.values()),
    "checks": checks,
    "source_payload_sha256": sample.payload_sha256,
    "binding_sha256": binding.binding_sha256,
}
(out / "adversarial_probe.json").write_text(
    json.dumps(summary, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(json.dumps(summary, indent=2, sort_keys=True))
raise SystemExit(0 if summary["all_checks_pass"] else 1)
PY
) >"$OUT/adversarial_probe_stdout.json" 2>"$OUT/adversarial_probe_stderr.log"
RC_PROBE=$?
kv adversarial_probe_rc "$RC_PROBE"

say 'POST-RUN CLEANLINESS'
git -C "$WT" status --porcelain >"$OUT/git_status_after.txt" 2>&1
if [ -s "$OUT/git_status_after.txt" ]; then
  RC_CLEAN=1
else
  RC_CLEAN=0
fi
kv clean_worktree "$([ "$RC_CLEAN" -eq 0 ] && echo true || echo false)"

say 'CLASSIFICATION'
CLASS='FAIL_R6_GREEN_LOCAL_EXACT_REPLAY'
if [ "$RC_COMPILE" -eq 0 ] && [ "$RC_R5" -eq 0 ] && [ "$RC_R6" -eq 0 ] && \
   [ "$HASH_OK" -eq 1 ] && [ "$RC_PROBE" -eq 0 ] && [ "$RC_CLEAN" -eq 0 ]; then
  CLASS='PASS_BASS_REC_SOURCE_R6_AUTHORITY_HARDENING_GREEN'
fi

cat >"$OUT/summary.txt" <<EOF
classification=$CLASS
publication_head=$REMOTE_HEAD
source_commit=$HEAD_ACTUAL
source_tree=$TREE_ACTUAL
source_blob=$SOURCE_ACTUAL
r5_test_blob=$R5_ACTUAL
r6_test_blob=$R6_ACTUAL
compile_rc=$RC_COMPILE
r5_survivor_rc=$RC_R5
r6_hardening_rc=$RC_R6
deterministic_hashes=$([ "$HASH_OK" -eq 1 ] && echo true || echo false)
source_payload_sha256=$SOURCE_H1
integrated_binding_sha256=$BIND_H1
adversarial_probe_rc=$RC_PROBE
clean_worktree=$([ "$RC_CLEAN" -eq 0 ] && echo true || echo false)
receipt_dir=$OUT
EOF
cat "$OUT/summary.txt"
sha256sum "$OUT"/* >"$OUT/SHA256SUMS" 2>/dev/null || true

# Never terminate a failure-sensitive interactive shell.
exit 0
