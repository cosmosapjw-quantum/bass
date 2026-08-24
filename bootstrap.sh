#!/usr/bin/env bash
# 세션 컨테이너 회수 후 **한 번에** 환경을 복원한다.
#
# 배경: 이 프로젝트는 클라우드 세션에서 개발되는데 컨테이너가 비활성 후 회수되면
# 작업트리·설치 의존성·빌드 산출물이 모두 사라진다 (2026-07-30 에 두 번 발생).
# 매번 손으로 재설치하면 5분 + 실수 여지가 생기므로 절차를 고정한다.
#
# 사용법:
#     tar -xzf bianchi-*.tar.gz && cd restore && bash bootstrap.sh
#     bash bootstrap.sh --fast      # Rust 재빌드 건너뛰기 (Python 시험만)
#
# 확인 대상: pytest 1682 passed, cargo test 122 passed (doctest 0).

set -euo pipefail
cd "$(dirname "$0")"
FAST=0
[[ "${1:-}" == "--fast" ]] && FAST=1

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

say "1/5  Python 의존성"
pip install -q --break-system-packages -r requirements.lock 2>&1 | tail -1 || \
  pip install -q -r requirements.lock 2>&1 | tail -1
# ★ requirements.lock 에 없지만 필요한 것들:
#   maturin  = Rust 확장 빌드 (개발 전용이라 lock 에 넣지 않았다)
pip install -q maturin 2>&1 | tail -1

say "2/5  audit 패키지 마커"
# ★ tests/test_h5_tilted_signs.py 가 `audit.h5_tilted_conservation` 을 임포트한다.
touch audit/__init__.py

if [[ $FAST -eq 0 ]]; then
  say "3/5  Rust 코어 빌드 (약 2분)"
  ( cd _rustcore && cargo test --release 2>&1 | tail -3 )
  ( cd _rustcore && maturin build --release 2>&1 | tail -2 )
  pip install -q --force-reinstall --no-deps _rustcore/target/wheels/*.whl 2>&1 | tail -1
else
  say "3/5  Rust 빌드 건너뜀 (--fast)"
fi

say "4/5  임포트 점검"
python - <<'PY'
import importlib, sys
mods = ["numpy", "scipy", "sympy", "jax", "bianchi", "bianchi.matter.hierarchy",
        "bianchi.matter.collision", "bianchi.matter.viscous_derived",
        "bianchi.matter.tilted", "bianchi.matter.tilted_moments",
        "bianchi.matter.tilted_terms", "bianchi.backend"]
for m in mods:
    importlib.import_module(m)
    print(f"  ok  {m}")
try:
    import bianchi_rustcore
    print("  ok  bianchi_rustcore (Rust 가속 경로 활성)")
except ImportError:
    print("  !!  bianchi_rustcore 없음 → Python 폴백으로만 동작 "
          "(차등테스트는 skip 된다)", file=sys.stderr)
PY

say "5/5  회귀 시험"
# test_m11_{rays,cmb} 는 장시간 실행이라 기본 제외 (기존 관례와 동일)
python -m pytest tests/ -q --ignore=tests/test_m11_rays.py --ignore=tests/test_m11_cmb.py \
  2>&1 | tail -3

say "완료 — 기대값: pytest 1682 passed / cargo test 122 passed"

