#!/usr/bin/env bash
# Q18 · 회귀 · 성능 CI (76차).
#   황금 케이스 비트 회귀 + 성능 기준선 + 시험 시간 예산.
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD"

echo "=== cargo test ==="
( cd _rustcore && cargo test --lib -q ) 2>&1 | tail -3

echo "=== Q 층 게이트 ==="
python -m pytest tests/test_q*.py -q --timeout=1200 2>&1 | tail -3

echo "=== 황금 케이스 (비트 회귀) ==="
python -m pytest tests/test_q18_golden.py -q 2>&1 | tail -3

echo "=== 오차예산 재생성 ==="
python scripts/q17_convergence.py > /dev/null && echo "docs/Q-ERROR-BUDGET.md 갱신"

echo "=== 전체 스위트 ==="
python -m pytest -q -x --timeout=2400 2>&1 | tail -3
