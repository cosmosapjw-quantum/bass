#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 /path/to/extracted-E4-authority-root" >&2
  exit 2
fi

candidate_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
input_root="$(cd -- "$1" && pwd)"

find_authority_root() {
  local root="$1"
  local owner candidate
  while IFS= read -r owner; do
    case "$owner" in
      */source/bianchi/q/electron.py)
        candidate="${owner%/source/bianchi/q/electron.py}"
        [[ -f "$candidate/source/bianchi/q/electron_rate.py" ]] || continue
        [[ -f "$candidate/tests/test_electron_collision_rate.py" ]] || continue
        printf '%s\n' "$candidate"
        return 0
        ;;
      */bianchi/q/electron.py)
        candidate="${owner%/bianchi/q/electron.py}"
        [[ -f "$candidate/bianchi/q/electron_rate.py" ]] || continue
        [[ -f "$candidate/tests/test_electron_collision_rate.py" ]] || continue
        printf '%s\n' "$candidate"
        return 0
        ;;
    esac
  done < <(find "$root" -type f -path '*/bianchi/q/electron.py' -print | sort)
  return 1
}

authority_root="$(find_authority_root "$input_root")" || {
  echo "No complete E2 authority root found under $input_root" >&2
  exit 3
}

case "$authority_root" in
  */source)
    echo "unexpected authority root ending in /source" >&2
    exit 4
    ;;
esac

if [[ -f "$authority_root/source/bianchi/q/electron.py" ]]; then
  module_root="$authority_root/source"
else
  module_root="$authority_root"
fi
tests_root="$authority_root/tests"

expected_electron='f5fa2da696453ea0b11cfddeb7f824cd1bdb42596cd4e2947fb7841e1387aafe'
expected_rate='27fe46756023380078fc503e8fe2ea5e976504314e206f55613d06af61f4be1a'

printf '%s  %s\n' "$expected_electron" "$module_root/bianchi/q/electron.py" | sha256sum -c -
printf '%s  %s\n' "$expected_rate" "$module_root/bianchi/q/electron_rate.py" | sha256sum -c -

before="$(mktemp)"
after="$(mktemp)"
trap 'rm -f "$before" "$after"' EXIT
sha256sum \
  "$module_root/bianchi/q/electron.py" \
  "$module_root/bianchi/q/electron_rate.py" > "$before"

# Deliberately exclude module_root from PYTHONPATH.  Normal import would execute
# the legacy bianchi package initializer and force JAX.  The bounded parity
# test instead loads the exact E2 owner files through a fail-closed pure-Python
# namespace shim matching the E2 authority test's own no-optional-stack seam.
export PYTHONPATH="$candidate_root/host_replay:$candidate_root/source:$candidate_root/inputs/bass8b2a:$candidate_root/inputs/bass8b2b0${PYTHONPATH:+:$PYTHONPATH}"
export BASS_E2_MODULE_ROOT="$module_root"

python - <<'PY'
import importlib
import os
for name in ("numpy", "pytest"):
    importlib.import_module(name)
    print("IMPORT_OK", name)

from pure_python_e2_loader import load_exact_e2_owner

electron, rate, receipt = load_exact_e2_owner(os.environ["BASS_E2_MODULE_ROOT"])
assert electron.C_LIGHT_M_S == 299_792_458.0
assert rate.SIGMA_T_M2 == 6.6524587e-29
assert receipt["package_initializers_executed"] is False
assert receipt["optional_stack_imported"] is False
print("PURE_PYTHON_E2_OWNER_IMPORT_PASS")
PY

python -m pytest -q "$candidate_root/tests/test_direction_dependent_rate_dual.py"
python -m pytest -q "$candidate_root/host_replay/test_exact_e2_rate_parity.py"
# The frozen E2 test already contains its own focused no-optional-stack loader.
python -m pytest -q "$tests_root/test_electron_collision_rate.py"

sha256sum \
  "$module_root/bianchi/q/electron.py" \
  "$module_root/bianchi/q/electron_rate.py" > "$after"
cmp "$before" "$after"

echo 'BASS8B2B1_EXACT_E2_HOST_PARITY_PASS__PURE_PYTHON_FRONTEND'
