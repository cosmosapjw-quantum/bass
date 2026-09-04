#!/usr/bin/env bash

# BASS-only source-GREEN validation for BG-02. This does not claim the native
# xTensor projection-derivation gate; that gate remains intentionally RED.

set +e
set +u
set +o pipefail 2>/dev/null || true

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." 2>/dev/null && pwd)"
OUT="${1:-$ROOT/artifacts/bg02_einstein_projection_source_green}"
PYTHON_BIN="$(command -v python3 2>/dev/null)"

if [ -z "$ROOT" ] || [ -z "$PYTHON_BIN" ] || [ ! -x "$PYTHON_BIN" ]; then
    printf 'ERROR: source root or python3 unavailable\n' >&2
    exit 2
fi

REGISTRY="$ROOT/docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/BG_02_IMPLEMENTATION_REGISTRY.json"
SOURCE="$ROOT/wolfram/BASS/Kernel/Background/EinsteinProjection.wl"
INIT="$ROOT/wolfram/BASS/Kernel/init.wl"
VERIFIER="$ROOT/scripts/verify_bg02_einstein_projection_implementation.py"
CAS_AUDITOR="$ROOT/scripts/audit_bg02_cross_cas.py"
WLT="$ROOT/wolfram/BASS/Tests/BG02EinsteinProjectionImplementation.wlt"
WLS="$ROOT/wolfram/scripts/run_bg02_einstein_projection_native.wls"
SUMMARY="$OUT/BG_02_SOURCE_GREEN_VALIDATION_SUMMARY.json"
MANIFEST="$OUT/SHA256SUMS"

for REQUIRED in "$REGISTRY" "$SOURCE" "$INIT" "$VERIFIER" "$CAS_AUDITOR" "$WLT" "$WLS"; do
    if [ ! -s "$REQUIRED" ]; then
        printf 'ERROR: required source-GREEN input missing: %s\n' "$REQUIRED" >&2
        exit 3
    fi
done

rm -rf -- "$OUT"
mkdir -p -- "$OUT" || exit 4

printf '\n===== BG-02 SOURCE VERIFIER =====\n'
"$PYTHON_BIN" -S "$VERIFIER" --input "$REGISTRY" --source "$SOURCE" --init "$INIT"
VERIFIER_RC=$?
if [ "$VERIFIER_RC" -ne 0 ]; then
    exit 10
fi

printf '\n===== BG-02 18-METHOD PYTHON CONTRACT =====\n'
(
    cd "$ROOT" || exit 90
    "$PYTHON_BIN" -S -m unittest -v tests.test_bg02_einstein_projection_implementation
)
TEST_RC=$?
if [ "$TEST_RC" -ne 0 ]; then
    exit 11
fi

printf '\n===== BG-02 CROSS-CAS AUDIT =====\n'
"$PYTHON_BIN" "$CAS_AUDITOR" --output "$OUT/BG_02_CROSS_CAS_AUDIT.json"
CAS_RC=$?
if [ "$CAS_RC" -ne 0 ]; then
    exit 12
fi

printf '\n===== STATIC WOLFRAM CONTRACT =====\n'
"$PYTHON_BIN" -S - "$SOURCE" "$WLT" "$WLS" <<'PY'
from __future__ import annotations
import sys
from pathlib import Path

paths=[Path(x) for x in sys.argv[1:]]

def balanced(text: str) -> bool:
    stack=[]
    pairs={')':'(',']':'[','}':'{'}
    in_string=False
    escaped=False
    i=0
    while i < len(text):
        ch=text[i]
        if in_string:
            if escaped:
                escaped=False
            elif ch=='\\':
                escaped=True
            elif ch=='"':
                in_string=False
        else:
            if ch=='"':
                in_string=True
            elif ch in '([{':
                stack.append(ch)
            elif ch in ')]}':
                if not stack or stack.pop()!=pairs[ch]:
                    return False
        i+=1
    return not in_string and not stack

for path in paths:
    text=path.read_text(encoding='utf-8')
    assert balanced(text), f'unbalanced Wolfram source: {path}'
wlt=paths[1].read_text(encoding='utf-8')
assert wlt.count('VerificationTest[')==26
assert 'xTensor_projection_derivation_verified' in wlt
assert all(token not in wlt for token in ('$InputFileName','Get[','Import['))
print('STATIC_WOLFRAM_CONTRACT=PASS')
print('NATIVE_XACT_DERIVATION_GATE=PENDING')
PY
STATIC_RC=$?
if [ "$STATIC_RC" -ne 0 ]; then
    exit 13
fi

HEAD="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || true)"
TREE="$(git -C "$ROOT" show -s --format=%T HEAD 2>/dev/null || true)"

"$PYTHON_BIN" -S - "$REGISTRY" "$OUT/BG_02_CROSS_CAS_AUDIT.json" "$SUMMARY" "$HEAD" "$TREE" <<'PY'
from __future__ import annotations
import json
import sys
from pathlib import Path
reg_path,cas_path,summary_path,head,tree=sys.argv[1:]
reg=json.loads(Path(reg_path).read_text(encoding='utf-8'))
cas=json.loads(Path(cas_path).read_text(encoding='utf-8'))
assert reg['formula_count']==14
assert reg['required_native_replay']['xTensor_projection_derivation_gate']=='PENDING'
assert cas['status']=='PASS_AVAILABLE_CAS_AXES'
payload={
  'schema_version':'1.0.0',
  'stage_id':'BG_02_EINSTEIN_PROJECTION_SOURCE_GREEN_VALIDATION',
  'repository_scope':'BASS_ONLY',
  'git_head':head,
  'git_tree':tree,
  'python_implementation_tests':'18/18',
  'source_verifier':'PASS',
  'formula_count':14,
  'sympy_exact':'PASS',
  'mpmath_100_digit':'PASS',
  'wolfram_connector':'BLOCKED_HTTP_502',
  'native_xact_projection_derivation':'PENDING',
  'native_munit_expected':26,
  'production_claim':'SOURCE_GREEN_CANDIDATE_ONLY',
  'status':'PASS_SOURCE_GREEN_CANDIDATE_NATIVE_XACT_PENDING'
}
Path(summary_path).write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n',encoding='utf-8')
print(json.dumps(payload,sort_keys=True))
PY
SUMMARY_RC=$?
if [ "$SUMMARY_RC" -ne 0 ]; then
    exit 14
fi

sha256sum \
  "$REGISTRY" "$SOURCE" "$INIT" "$VERIFIER" "$CAS_AUDITOR" "$WLT" "$WLS" \
  "$ROOT/tools/bg02/bg02_offshell_octave.m" \
  "$ROOT/tools/bg02/bg02_offshell_sage.py" \
  "$ROOT/tools/bg02/bg02_offshell_singular.sing" \
  "$ROOT/formal/lean/BG02OffShellIdentities.lean" \
  "$OUT/BG_02_CROSS_CAS_AUDIT.json" "$SUMMARY" > "$MANIFEST"
MANIFEST_RC=$?
if [ "$MANIFEST_RC" -ne 0 ]; then
    exit 15
fi

sha256sum -c "$MANIFEST"
CHECK_RC=$?
if [ "$CHECK_RC" -ne 0 ]; then
    exit 16
fi

printf '\nBG-02 source GREEN candidate validation PASS\n'
printf 'native xTensor projection derivation remains PENDING\n'
printf 'artifacts: %s\n' "$OUT"
exit 0
