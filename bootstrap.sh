#!/usr/bin/env bash
# 세션 컨테이너 회수 후 native-required 설치 단위를 복원한다.
#
# 배경: 이 프로젝트는 클라우드 세션에서 개발되는데 컨테이너가 비활성 후 회수되면
# 작업트리·설치 의존성·빌드 산출물이 모두 사라진다 (2026-07-30 에 두 번 발생).
# 매번 손으로 재설치하면 5분 + 실수 여지가 생기므로 절차를 고정한다.
#
# 사용법:
#     tar -xzf bianchi-*.tar.gz && cd restore && bash bootstrap.sh
# 이 파일은 복구 helper이며 회귀 test runner나 CI authority가 아니다.
#
set -euo pipefail
cd "$(dirname "$0")"

say() { printf '\n\033[1m== %s\033[0m\n' "$*"; }

# ═══ 스냅샷만 만들고 끝낸다 (컨테이너 회수가 잦아 절차에 넣었다)
#     bash bootstrap.sh --snapshot NAME   →  ../bianchi-NAME.tar.gz
# ★ 처음에 이 블록을 스크립트 **끝**에 뒀다가 회귀시험(13분)을 다 돌고서야 스냅샷이
#   나왔다.  "빨리 저장" 용도에 맞게 앞으로 옮기고 즉시 종료하게 고쳤다.
if [[ "${1:-}" == "--snapshot" ]]; then
  NAME="${2:-snapshot}"
  OUT="../bianchi-${NAME}.tar.gz"
  tar czf "$OUT" --exclude='_rustcore/target' --exclude='__pycache__' \
      --exclude='.git' --exclude='*.pyc' -C . .
  say "스냅샷: $(cd .. && pwd)/bianchi-${NAME}.tar.gz  ($(du -h "$OUT" | cut -f1))"
  exit 0
fi
if [[ $# -ne 0 ]]; then
  printf 'ERROR: unsupported bootstrap argument: %s (only --snapshot NAME is supported).\n' "$1" >&2
  exit 2
fi

if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  printf 'ERROR: bootstrap.sh requires an activated venv. Run: python3.12 -m venv .venv && source .venv/bin/activate\n' >&2
  exit 2
fi
if ! command -v rustc >/dev/null 2>&1; then
  printf 'ERROR: Rust 1.94.1 is required but rustc is not on PATH.\n' >&2
  exit 2
fi
if [[ "$(rustc --version)" != "rustc 1.94.1 "* ]]; then
  printf 'ERROR: Rust 1.94.1 is required; observed: %s\n' "$(rustc --version 2>&1)" >&2
  exit 2
fi

WHEEL_DIR="$(mktemp -d)"
trap 'rm -rf -- "$WHEEL_DIR"' EXIT

say "1/4  고정 native builder"
python -m pip install --disable-pip-version-check 'maturin==1.14.1'

say "2/4  lockfile 고정 native 휠"
( cd _rustcore && python -m maturin build --release --locked --out "$WHEEL_DIR" )
mapfile -t NATIVE_WHEELS < <(find "$WHEEL_DIR" -maxdepth 1 -type f \
  -name 'bianchi_rustcore-0.1.0-*.whl' -print)
if [[ ${#NATIVE_WHEELS[@]} -ne 1 ]]; then
  printf 'ERROR: expected exactly one bianchi-rustcore 0.1.0 wheel, found %d in %s\n' \
    "${#NATIVE_WHEELS[@]}" "$WHEEL_DIR" >&2
  exit 2
fi

say "3/4  단일 root resolver 설치"
python -m pip install --disable-pip-version-check --constraint requirements.lock \
  "${NATIVE_WHEELS[0]}" .

say "4/4  최소 native-required 임포트 점검"
python - <<'PY'
import importlib
from importlib import metadata
import sys

mods = ["numpy", "bianchi", "bianchi.backend_policy", "bianchi.matter.hierarchy",
        "bianchi.matter.collision", "bianchi.matter.viscous_derived",
        "bianchi.matter.tilted", "bianchi.matter.tilted_moments",
        "bianchi.matter.tilted_terms", "bianchi.backend", "bianchi_rustcore"]
for m in mods:
    importlib.import_module(m)
    print(f"  ok  {m}")
version = metadata.version("bianchi-rustcore")
if version != "0.1.0":
    raise RuntimeError(f"incompatible bianchi-rustcore distribution: {version}")
print(f"  ok  bianchi-rustcore {version} (native-required install)")
optional_roots = {
    "jax", "jaxlib", "diffrax", "equinox", "optimistix", "lineax",
    "scipy", "sympy", "mpmath",
}
loaded_optional = sorted(optional_roots.intersection(sys.modules))
if loaded_optional:
    raise RuntimeError(
        f"minimal native frontend imported optional dependencies: {loaded_optional}"
    )
print("  ok  optional Python oracle stack not imported")
PY

say "완료 — 검증은 RF-00 focused CI/evidence 명령을 별도로 사용"
