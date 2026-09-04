#!/usr/bin/env bash
# BASS_REC_SOURCE_R10_CERTIFIED_SCALAR_PROJECTION_PARITY_GREEN
#
# Execute the exact R10 source candidate in a detached worktree.  The gate
# preserves all 49 R5/R6/R7/R9 focused methods, checks two-process parity
# identities, generates residual/Gram/conditioning diagnostics, records fresh
# alternative-CAS availability, and leaves the caller checkout untouched.
#
# The script writes its own classification and always returns shell status 0.

set +e
set +u
set +o pipefail 2>/dev/null || true

PARENT='06693571d98013610bc01565a1f4988bdc673094'
SOURCE_COMMIT='308507f2289b4cd6aabf0d7762e6e12766feb627'
SOURCE_TREE='a27ff7c010b76cfc42ad0f2ac62049689cbb816a'
BRANCH='research/bass-rec-source-r10-certified-scalar-parity-green-20260904-r1'

SOURCE_AUTHORITY_BLOB='869677390004f68aef9f547e6556f5f1c15bd012'
SOURCE_ADAPTER_BLOB='8b00602fc76e1cd49ac5b43615c97a686b56f080'
SOURCE_PARITY_BLOB='a807191ff0baa6851ec7748826a7d4e34b400207'
R5_TEST_BLOB='db336d64633d8a9552bc3613c588a00f33404a4d'
R6_TEST_BLOB='49be9546c4655bc5ca330bc31ae2daf07578b74f'
R7_TEST_BLOB='d6fb316452a947d0f955dd4a115e8840688a2d02'
R9_TEST_BLOB='31e72e4075e973022650dd8f14cc8690c2c55673'

ROOT="${RECEIPT_ROOT:-$HOME/Dropbox/bianchi/_runtime_receipts}"
OUT="$ROOT/BASS_REC_SOURCE_R10_GREEN_$(date -u +%Y%m%dT%H%M%SZ)"
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
  stop_gate STOP_R10_FETCH_FAILURE \
    "fetch=$RC_FETCH publication=${PUBLICATION_HEAD:-MISSING}"
fi

git -C "$BASS" merge-base --is-ancestor "$SOURCE_COMMIT" "$PUBLICATION_HEAD" \
  >/dev/null 2>&1
[ "$?" -eq 0 ] || stop_gate STOP_R10_SOURCE_NOT_PUBLICATION_ANCESTOR \
  "$PUBLICATION_HEAD"

TMP="$(mktemp -d /tmp/bass-r10-green.XXXXXX 2>/dev/null)"
[ -d "$TMP" ] || stop_gate STOP_TEMP_DIRECTORY_FAILURE "$TMP"
WT="$TMP/worktree"

cleanup() {
  git -C "$BASS" worktree remove --force "$WT" >/dev/null 2>&1 || true
  case "$TMP" in
    /tmp/bass-r10-green.*) rm -rf -- "$TMP" >/dev/null 2>&1 || true ;;
  esac
}
trap cleanup EXIT HUP INT TERM

git -C "$BASS" worktree add --detach "$WT" "$SOURCE_COMMIT" \
  >"$OUT/worktree.log" 2>&1
RC_WT=$?
[ "$RC_WT" -eq 0 ] || stop_gate STOP_R10_WORKTREE_FAILURE "$RC_WT"

ACTUAL_COMMIT="$(git -C "$WT" rev-parse HEAD 2>/dev/null)"
ACTUAL_TREE="$(git -C "$WT" rev-parse HEAD^{tree} 2>/dev/null)"
AUTH_BLOB="$(git -C "$WT" hash-object bianchi/source_authority.py 2>/dev/null)"
ADAPTER_BLOB="$(git -C "$WT" hash-object bianchi/source_adapters.py 2>/dev/null)"
PARITY_BLOB="$(git -C "$WT" hash-object bianchi/source_parity.py 2>/dev/null)"
T5="$(git -C "$WT" hash-object tests/research/test_bass_rec_source_protocol_red.py 2>/dev/null)"
T6="$(git -C "$WT" hash-object tests/research/test_bass_rec_source_protocol_r6_red.py 2>/dev/null)"
T7="$(git -C "$WT" hash-object tests/research/test_bass_rec_source_r7_dual_adapter_red.py 2>/dev/null)"
T9="$(git -C "$WT" hash-object tests/research/test_bass_rec_source_r9_parity_red.py 2>/dev/null)"

if [ "$ACTUAL_COMMIT" != "$SOURCE_COMMIT" ] || \
   [ "$ACTUAL_TREE" != "$SOURCE_TREE" ] || \
   [ "$AUTH_BLOB" != "$SOURCE_AUTHORITY_BLOB" ] || \
   [ "$ADAPTER_BLOB" != "$SOURCE_ADAPTER_BLOB" ] || \
   [ "$PARITY_BLOB" != "$SOURCE_PARITY_BLOB" ] || \
   [ "$T5" != "$R5_TEST_BLOB" ] || \
   [ "$T6" != "$R6_TEST_BLOB" ] || \
   [ "$T7" != "$R7_TEST_BLOB" ] || \
   [ "$T9" != "$R9_TEST_BLOB" ]; then
  stop_gate STOP_R10_EXACT_IDENTITY_MISMATCH \
    "$ACTUAL_COMMIT $ACTUAL_TREE $AUTH_BLOB $ADAPTER_BLOB $PARITY_BLOB $T5 $T6 $T7 $T9"
fi

git -C "$WT" diff --name-status "$PARENT" "$SOURCE_COMMIT" \
  >"$OUT/source_diff_name_status.txt" 2>&1
if [ "$(wc -l <"$OUT/source_diff_name_status.txt" | tr -d ' ')" != 1 ] || \
   ! grep -Fqx $'A\tbianchi/source_parity.py' "$OUT/source_diff_name_status.txt"; then
  stop_gate STOP_R10_UNBOUNDED_PRODUCTION_DIFF \
    "$(tr '\n' ';' <"$OUT/source_diff_name_status.txt")"
fi

(
  cd "$WT" || exit 97
  PYTHONPATH="$WT" "$PY" -m py_compile \
    bianchi/source_authority.py \
    bianchi/source_adapters.py \
    bianchi/source_parity.py \
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
) >"$OUT/focused_result.json" 2>"$OUT/focused_verbose.log"
RC_FOCUSED=$?

run_parity_audit() {
  target="$1"
  (
    cd "$WT" || exit 97
    PYTHONPATH="$WT" "$PY" - <<'PY'
import json
import math

from bianchi.source_adapters import SourceTimeBasis
from bianchi.source_authority import SourceAuthorityBundle, SourceFrequencyKind
from bianchi.source_parity import (
    build_gauss_legendre_uniform_phi_quadrature,
    compare_constant_pair_grid_and_pstf,
    project_real_spherical_harmonics,
    synthesize_real_spherical_harmonics,
)

PARENT = 'a' * 64
GRID = '1' * 64
PSTF = '2' * 64


def bundle(eta=3.0, kappa=2.0):
    return SourceAuthorityBundle.constant_pair(
        eta_s_inv=eta,
        kappa_s_inv=kappa,
        frame='hydrogen_orthonormal',
        channel='total_occupation',
        source_sha256='0' * 64,
        frequency_kind=SourceFrequencyKind.POINTWISE_SPECTRAL,
    )


def fixture(l_max):
    values = [1.5 * math.sqrt(4.0 * math.pi)]
    for ell in range(1, l_max + 1):
        values.append(((-1.0) ** ell) * (ell + 1.0) / 500.0)
        for m in range(1, ell + 1):
            values.append(((-1.0) ** (ell + m)) * (ell + 2.0 * m + 1.0) / 5000.0)
            values.append(((-1.0) ** m) * (2.0 * ell + m + 1.0) / 7000.0)
    return tuple(values)


def inverse(matrix):
    n = len(matrix)
    augmented = [
        list(row) + [1.0 if i == j else 0.0 for j in range(n)]
        for i, row in enumerate(matrix)
    ]
    for column in range(n):
        pivot = max(range(column, n), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) < 1.0e-15:
            raise ArithmeticError('Gram matrix is singular')
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        augmented[column] = [value / divisor for value in augmented[column]]
        for row in range(n):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor != 0.0:
                augmented[row] = [
                    left - factor * right
                    for left, right in zip(augmented[row], augmented[column], strict=True)
                ]
    return [row[n:] for row in augmented]


def norm_inf(matrix):
    return max(sum(abs(value) for value in row) for row in matrix)


def gram_diagnostics(l_max, quadrature):
    count = (l_max + 1) ** 2
    columns = []
    for column in range(count):
        unit = [0.0] * count
        unit[column] = 1.0
        samples = synthesize_real_spherical_harmonics(
            tuple(unit), l_max=l_max, quadrature=quadrature
        )
        columns.append(
            project_real_spherical_harmonics(
                samples, l_max=l_max, quadrature=quadrature
            )
        )
    gram = [
        [columns[column][row] for column in range(count)]
        for row in range(count)
    ]
    defect = max(
        abs(gram[row][column] - (1.0 if row == column else 0.0))
        for row in range(count)
        for column in range(count)
    )
    condition = norm_inf(gram) * norm_inf(inverse(gram))
    return defect, condition

records = {}
all_pass = True
for l_max in (0, 1, 2, 3, 4, 6, 8):
    quadrature = build_gauss_legendre_uniform_phi_quadrature(l_work=l_max)
    report = compare_constant_pair_grid_and_pstf(
        bundle(),
        fixture(l_max),
        l_out=l_max,
        l_work=l_max,
        state_parent_sha256=PARENT,
        grid_representation_sha256=GRID,
        pstf_representation_sha256=PSTF,
        time_basis=SourceTimeBasis.PHYSICAL_TIME,
        atol=2.0e-13,
        rtol=2.0e-13,
    )
    gram_defect, gram_condition = gram_diagnostics(l_max, quadrature)
    record = {
        'compared_coefficients': report.compared_coefficients,
        'gram_condition_inf': gram_condition,
        'gram_max_abs_defect': gram_defect,
        'max_abs_residual': report.max_abs_residual,
        'max_rel_residual': report.max_rel_residual,
        'n_mu': quadrature.n_mu,
        'n_phi': quadrature.n_phi,
        'pass_parity': report.pass_parity,
        'projection_contract_sha256': quadrature.projection_contract_sha256,
        'report_sha256': report.report_sha256,
    }
    records[str(l_max)] = record
    all_pass = (
        all_pass
        and report.pass_parity
        and report.max_abs_residual <= 2.0e-13
        and gram_defect <= 2.0e-13
        and gram_condition <= 2.0
    )

payload = {
    'all_pass': all_pass,
    'basis': 'real orthonormal Condon-Shortley harmonics on dOmega',
    'records': records,
    'schema_version': '1.0.0',
    'source': 'constant photon/boson pair',
}
print(json.dumps(payload, indent=2, sort_keys=True))
raise SystemExit(0 if all_pass else 1)
PY
  ) >"$target" 2>"${target%.json}.err"
}

run_parity_audit "$OUT/parity_run_1.json"
RC_PARITY_1=$?
run_parity_audit "$OUT/parity_run_2.json"
RC_PARITY_2=$?
cmp -s "$OUT/parity_run_1.json" "$OUT/parity_run_2.json"
RC_PARITY_CMP=$?
DETERMINISTIC=false
[ "$RC_PARITY_1" -eq 0 ] && [ "$RC_PARITY_2" -eq 0 ] && \
  [ "$RC_PARITY_CMP" -eq 0 ] && DETERMINISTIC=true

(
  cd "$WT" || exit 97
  PYTHONPATH="$WT" "$PY" - <<'PY'
import json
import math

from bianchi.source_adapters import SourceTimeBasis
from bianchi.source_authority import SourceAuthorityBundle, SourceFrequencyKind
import bianchi.source_parity as parity


def source(eta=3.0, kappa=2.0):
    return SourceAuthorityBundle.constant_pair(
        eta_s_inv=eta,
        kappa_s_inv=kappa,
        frame='hydrogen_orthonormal',
        channel='total_occupation',
        source_sha256='0' * 64,
        frequency_kind=SourceFrequencyKind.POINTWISE_SPECTRAL,
    )


def fixture(l_max=6):
    values = [1.5 * math.sqrt(4.0 * math.pi)]
    for ell in range(1, l_max + 1):
        values.append(((-1.0) ** ell) * (ell + 1.0) / 500.0)
        for m in range(1, ell + 1):
            values.append(((-1.0) ** (ell + m)) * (ell + 2.0 * m + 1.0) / 5000.0)
            values.append(((-1.0) ** m) * (2.0 * ell + m + 1.0) / 7000.0)
    return tuple(values)

common = dict(
    source=source(),
    coefficients=fixture(),
    l_out=6,
    l_work=6,
    state_parent_sha256='a' * 64,
    grid_representation_sha256='1' * 64,
    pstf_representation_sha256='2' * 64,
    time_basis=SourceTimeBasis.PHYSICAL_TIME,
    atol=2.0e-13,
    rtol=2.0e-13,
)
baseline = parity.compare_constant_pair_grid_and_pstf(**common)
wrong_unit = list(parity.unit_field_coefficients(6))
wrong_unit[0] = 1.0
mutated = parity.compare_constant_pair_grid_and_pstf(
    **common,
    unit_field_coefficients=tuple(wrong_unit),
    require_pass=False,
)

checks = {
    'baseline_pass': baseline.pass_parity,
    'normalization_mutation_detected': not mutated.pass_parity,
    'normalization_mutation_hash_sensitive': baseline.report_sha256 != mutated.report_sha256,
    'source_off_exact': all(
        value == 0.0
        for value in parity.compare_constant_pair_grid_and_pstf(
            **{**common, 'source': source(0.0, 0.0)}
        ).pstf_values
    ),
}

for name, kwargs in {
    'underresolved_mu_rejected': dict(l_work=6, n_mu=6, n_phi=13),
    'underresolved_phi_rejected': dict(l_work=6, n_mu=7, n_phi=12),
}.items():
    try:
        parity.SphereQuadrature.create(**kwargs)
    except parity.SourceParityError:
        checks[name] = True
    else:
        checks[name] = False

quadrature = parity.build_gauss_legendre_uniform_phi_quadrature(l_work=6)
try:
    parity.compare_constant_pair_grid_and_pstf(
        **common,
        quadrature=quadrature,
        projection_contract_sha256='d' * 64,
    )
except parity.SourceParityError:
    checks['projection_identity_mismatch_rejected'] = True
else:
    checks['projection_identity_mismatch_rejected'] = False

checks['all_pass'] = all(checks.values())
print(json.dumps(checks, indent=2, sort_keys=True))
raise SystemExit(0 if checks['all_pass'] else 1)
PY
) >"$OUT/adversarial_probe.json" 2>"$OUT/adversarial_probe.err"
RC_ADVERSARIAL=$?

(
  cd "$WT" || exit 97
  PYTHONPATH="$WT" "$PY" - "$TMP" <<'PY'
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

scratch = Path(sys.argv[1])
status = {'schema_version': '1.0.0', 'tools': {}}
mandatory_pass = True

try:
    import sympy as sp
    eta, kappa, occupation, hubble, light_speed = sp.symbols(
        'eta kappa occupation hubble light_speed', nonzero=True
    )
    action = eta * (1 + occupation) - kappa * occupation
    affine = eta - (kappa - eta) * occupation
    residuals = {
        'affine': sp.simplify(action - affine),
        'q_time': sp.simplify(action / hubble - affine / hubble),
        'ray_length': sp.simplify(action / light_speed - affine / light_speed),
    }
    passed = all(value == 0 for value in residuals.values())
    status['tools']['sympy'] = {
        'available': True,
        'version': sp.__version__,
        'pass': passed,
        'residuals': {key: str(value) for key, value in residuals.items()},
    }
    mandatory_pass = mandatory_pass and passed
except Exception as exc:
    status['tools']['sympy'] = {
        'available': False,
        'detail': f'{type(exc).__name__}: {exc}',
        'inherited_r9_fallback_receipt': True,
    }

try:
    import mpmath as mp
    mp.mp.dps = 80
    nodes, weights = mp.gauss_quadrature(7, 'legendre')
    errors = []
    for degree in range(13):
        observed = mp.fsum(weights[index] * nodes[index] ** degree for index in range(7))
        expected = mp.mpf(0) if degree % 2 else mp.mpf(2) / (degree + 1)
        errors.append(abs(observed - expected))
    maximum = max(errors)
    passed = maximum < mp.mpf('1e-70')
    status['tools']['mpmath'] = {
        'available': True,
        'version': mp.__version__,
        'pass': passed,
        'max_abs_error': mp.nstr(maximum, 25),
        'precision_dps': 80,
    }
    mandatory_pass = mandatory_pass and passed
except Exception as exc:
    status['tools']['mpmath'] = {
        'available': False,
        'detail': f'{type(exc).__name__}: {exc}',
        'inherited_r9_fallback_receipt': True,
    }

optional_commands = {
    'gnu_octave': ['octave-cli', '--quiet', '--eval', "e=3;k=2;f=5;r=e*(1+f)-k*f-(e-(k-e)*f);printf('R10_OCTAVE_RESIDUAL=%.17g\\n',r);if(r!=0),exit(2);end;"],
    'sagemath': ['sage', '-python', '-c', "from sage.all import QQ;e,k,f=QQ(3),QQ(2),QQ(5);r=e*(1+f)-k*f-(e-(k-e)*f);print('R10_SAGE_RESIDUAL='+str(r));raise SystemExit(0 if r==0 else 2)"],
}
for name, command in optional_commands.items():
    executable = shutil.which(command[0])
    if executable is None:
        status['tools'][name] = {'available': False, 'status': 'SKIP_TOOL_UNAVAILABLE'}
        continue
    command[0] = executable
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=20, check=False)
        status['tools'][name] = {
            'available': True,
            'returncode': result.returncode,
            'stdout': result.stdout[-2000:],
            'stderr': result.stderr[-2000:],
            'pass': result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        status['tools'][name] = {'available': True, 'status': 'TIMEOUT_20S', 'pass': False}

singular = shutil.which('Singular')
if singular is None:
    status['tools']['singular'] = {'available': False, 'status': 'SKIP_TOOL_UNAVAILABLE'}
else:
    program = 'ring r=0,(e,k,f),dp; poly p=e*(1+f)-k*f-(e-(k-e)*f); print(p); quit;\n'
    try:
        result = subprocess.run(
            [singular, '--no-rc', '--quiet'], input=program,
            capture_output=True, text=True, timeout=20, check=False,
        )
        status['tools']['singular'] = {
            'available': True,
            'returncode': result.returncode,
            'stdout': result.stdout[-2000:],
            'stderr': result.stderr[-2000:],
            'pass': result.returncode == 0 and result.stdout.strip().endswith('0'),
        }
    except subprocess.TimeoutExpired:
        status['tools']['singular'] = {'available': True, 'status': 'TIMEOUT_20S', 'pass': False}

lean = shutil.which('lean')
lake = shutil.which('lake')
if lean is None and lake is None:
    status['tools']['lean_mathlib'] = {'available': False, 'status': 'SKIP_TOOL_UNAVAILABLE'}
else:
    proof = scratch / 'R10Affine.lean'
    proof.write_text(
        'import Mathlib\n\nexample (eta kappa f : ℝ) : eta * (1 + f) - kappa * f = eta - (kappa - eta) * f := by ring\n',
        encoding='utf-8',
    )
    command = [lean, str(proof)] if lean is not None else [lake, 'env', 'lean', str(proof)]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30, check=False)
        status['tools']['lean_mathlib'] = {
            'available': True,
            'returncode': result.returncode,
            'stdout': result.stdout[-2000:],
            'stderr': result.stderr[-2000:],
            'pass': result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        status['tools']['lean_mathlib'] = {'available': True, 'status': 'TIMEOUT_30S', 'pass': False}

status['mandatory_pass'] = mandatory_pass
print(json.dumps(status, indent=2, sort_keys=True))
raise SystemExit(0 if mandatory_pass else 1)
PY
) >"$OUT/formal_tool_status.json" 2>"$OUT/formal_tool_status.err"
RC_FORMAL=$?

"$PY" - "$OUT/parity_run_1.json" "$OUT/r10_plot_data.json" "$OUT/r10_projection_audit.svg" <<'PY'
import html
import json
import math
import sys
from pathlib import Path

source = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
records = source['records']
plot = {
    'classification': 'R10_PRE_ADMISSION_DIAGNOSTIC',
    'ranks': [int(rank) for rank in records],
    'max_abs_residual': [records[rank]['max_abs_residual'] for rank in records],
    'gram_max_abs_defect': [records[rank]['gram_max_abs_defect'] for rank in records],
    'gram_condition_inf': [records[rank]['gram_condition_inf'] for rank in records],
    'tolerance': 2.0e-13,
}
Path(sys.argv[2]).write_text(json.dumps(plot, indent=2, sort_keys=True) + '\n', encoding='utf-8')

width, height = 820, 500
left, right, top, bottom = 75, 25, 45, 65
plot_width = width - left - right
plot_height = height - top - bottom
ranks = plot['ranks']
positive = [
    max(value, 1.0e-18)
    for value in plot['max_abs_residual'] + plot['gram_max_abs_defect']
]
y_min, y_max = 1.0e-18, 1.0e-11

def x(rank):
    return left + plot_width * rank / max(ranks[-1], 1)

def y(value):
    clipped = min(max(value, y_min), y_max)
    return top + plot_height * (math.log10(y_max) - math.log10(clipped)) / (math.log10(y_max) - math.log10(y_min))

def points(values):
    return ' '.join(f'{x(rank):.3f},{y(max(value, y_min)):.3f}' for rank, value in zip(ranks, values, strict=True))

svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
    '<rect width="100%" height="100%" fill="white"/>',
    '<text x="75" y="25" font-size="17" font-weight="bold">R10 finite-rank projection diagnostics</text>',
]
for exponent in range(-18, -10):
    value = 10.0 ** exponent
    yy = y(value)
    svg.append(f'<line x1="{left}" y1="{yy:.3f}" x2="{width-right}" y2="{yy:.3f}" stroke="#dddddd"/>')
    svg.append(f'<text x="8" y="{yy+4:.3f}" font-size="11">1e{exponent}</text>')
for rank in ranks:
    xx = x(rank)
    svg.append(f'<line x1="{xx:.3f}" y1="{top}" x2="{xx:.3f}" y2="{height-bottom}" stroke="#eeeeee"/>')
    svg.append(f'<text x="{xx-4:.3f}" y="{height-bottom+20}" font-size="11">{rank}</text>')
svg.extend([
    f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="black"/>',
    f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="black"/>',
    f'<polyline fill="none" stroke="#1f77b4" stroke-width="2" points="{points(plot["max_abs_residual"])}"/>',
    f'<polyline fill="none" stroke="#d62728" stroke-width="2" points="{points(plot["gram_max_abs_defect"])}"/>',
    f'<line x1="{left}" y1="{y(plot["tolerance"]):.3f}" x2="{width-right}" y2="{y(plot["tolerance"]):.3f}" stroke="#333333" stroke-dasharray="6 4"/>',
    f'<text x="{left+10}" y="{y(plot["tolerance"])-6:.3f}" font-size="11">parity tolerance 2e-13</text>',
    '<line x1="535" y1="24" x2="565" y2="24" stroke="#1f77b4" stroke-width="2"/>',
    '<text x="572" y="28" font-size="11">source parity residual</text>',
    '<line x1="535" y1="42" x2="565" y2="42" stroke="#d62728" stroke-width="2"/>',
    '<text x="572" y="46" font-size="11">Gram defect</text>',
    f'<text x="{width/2-35}" y="{height-20}" font-size="13">maximum harmonic rank L</text>',
    '<text x="17" y="300" font-size="13" transform="rotate(-90 17 300)">absolute residual / defect</text>',
    '<text x="75" y="480" font-size="11">Condition numbers are stored in r10_plot_data.json; this SVG is a numerical contract diagnostic, not a physical observable.</text>',
    '</svg>',
])
Path(sys.argv[3]).write_text('\n'.join(svg) + '\n', encoding='utf-8')
PY
RC_PLOT=$?

PLOT_PASS=false
"$PY" - "$OUT/r10_plot_data.json" <<'PY'
import json
import sys
from pathlib import Path
payload = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
passed = (
    max(payload['max_abs_residual']) <= payload['tolerance']
    and max(payload['gram_max_abs_defect']) <= payload['tolerance']
    and max(payload['gram_condition_inf']) <= 2.0
)
raise SystemExit(0 if passed else 1)
PY
RC_PLOT_AUDIT=$?
[ "$RC_PLOT" -eq 0 ] && [ "$RC_PLOT_AUDIT" -eq 0 ] && PLOT_PASS=true

git -C "$WT" status --porcelain=v1 --untracked-files=all >"$OUT/git_status_after.txt"
CLEAN=false
[ ! -s "$OUT/git_status_after.txt" ] && CLEAN=true

CLASSIFICATION='FAIL_R10_CERTIFIED_SCALAR_PROJECTION_PARITY_GREEN'
if [ "$RC_COMPILE" -eq 0 ] && \
   [ "$RC_FOCUSED" -eq 0 ] && \
   [ "$DETERMINISTIC" = true ] && \
   [ "$RC_ADVERSARIAL" -eq 0 ] && \
   [ "$RC_FORMAL" -eq 0 ] && \
   [ "$PLOT_PASS" = true ] && \
   [ "$CLEAN" = true ]; then
  CLASSIFICATION='PASS_BASS_REC_SOURCE_R10_CERTIFIED_SCALAR_PROJECTION_PARITY_GREEN'
fi

cat >"$OUT/summary.txt" <<EOF
classification=$CLASSIFICATION
publication_head=$PUBLICATION_HEAD
parent=$PARENT
source_commit=$ACTUAL_COMMIT
source_tree=$ACTUAL_TREE
source_authority_blob=$AUTH_BLOB
source_adapter_blob=$ADAPTER_BLOB
source_parity_blob=$PARITY_BLOB
r9_test_blob=$T9
python=$PYVER
compile_rc=$RC_COMPILE
focused_49_rc=$RC_FOCUSED
parity_run_1_rc=$RC_PARITY_1
parity_run_2_rc=$RC_PARITY_2
deterministic_parity_receipts=$DETERMINISTIC
adversarial_probe_rc=$RC_ADVERSARIAL
formal_fallback_rc=$RC_FORMAL
plot_generation_rc=$RC_PLOT
plot_audit_pass=$PLOT_PASS
clean_worktree=$CLEAN
receipt_dir=$OUT
EOF
cat "$OUT/summary.txt"

cat >"$OUT/R10_CERTIFIED_PARITY_RECEIPT.json" <<EOF
{
  "schema_version": "1.0.0",
  "stage_id": "BASS_REC_SOURCE_R10_CERTIFIED_SCALAR_PROJECTION_PARITY_GREEN",
  "classification": "$CLASSIFICATION",
  "publication_head": "$PUBLICATION_HEAD",
  "source_commit": "$ACTUAL_COMMIT",
  "source_tree": "$ACTUAL_TREE",
  "source_parity_blob": "$PARITY_BLOB",
  "compile_rc": $RC_COMPILE,
  "focused_49_rc": $RC_FOCUSED,
  "deterministic_parity_receipts": $DETERMINISTIC,
  "adversarial_probe_rc": $RC_ADVERSARIAL,
  "formal_fallback_rc": $RC_FORMAL,
  "plot_audit_pass": $PLOT_PASS,
  "clean_worktree": $CLEAN,
  "claim_boundary": {
    "finite_rank_scalar_constant_source_parity": $([ "$CLASSIFICATION" = 'PASS_BASS_REC_SOURCE_R10_CERTIFIED_SCALAR_PROJECTION_PARITY_GREEN' ] && echo true || echo false),
    "trusted_native_nonregression": false,
    "anisotropic_source_product": false,
    "polarized_source_parity": false,
    "transport_time_parity": false,
    "physical_rec_source_wiring": false,
    "integrated_state_closure": false,
    "physical_face": false,
    "provider_export": false
  }
}
EOF

sha256sum "$OUT"/* >"$OUT/SHA256SUMS" 2>/dev/null || true
printf '\nCaller checkout was not switched or modified.\n'
exit 0
