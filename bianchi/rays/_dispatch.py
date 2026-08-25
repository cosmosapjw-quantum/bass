"""
R1 광선 디스패치 — `bianchi.backend` 로 통합됨 (하위호환 재노출).

신규 코드는 `from bianchi import backend` 를 쓸 것.  이 모듈은 R0/R1 단계의 API 를
유지하기 위한 얇은 별칭이다.
"""
from __future__ import annotations

from bianchi.backend import (  # noqa: F401
    available, name as backend, info,
    ray_final_z_batch, optical_batch,
)
