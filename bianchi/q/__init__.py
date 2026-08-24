"""
Q 티어 — 절단 없는 비섭동 완전 볼츠만 백엔드 (Rust 코어 / Python 프론트엔드).

계획서: PLAN-Q-nonperturbative-backend.md
계약  : docs/Q-CONTRACT.md  ·  기계가독 사본 `bianchi.q.contract`

규율 한 줄: **Python 은 설정·조립·분석만, 스텝 루프는 Rust.**
"""
from __future__ import annotations

from bianchi.q import contract  # noqa: F401

__all__ = ["contract"]
