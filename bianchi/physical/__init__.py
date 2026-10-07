"""물리량 재구성 패키지 (Hubble 정규화 해 -> 관측 가능량).

기존 단일 모듈(physical.py)의 API 는 _legacy 에서 그대로 re-export 하여 하위호환.
신규 (v2.0):
  chart            τ <-> (H, t, ℓ) 왕복, IX D-차트 경로, 차원 복원  (PR-28)
  frame_transport  삼각대 전송 dP/dτ=(I+Σ+Ω)P, a_i(τ)              (PR-29)
  units, initial   CODATA 상수, Ω_i0, 오늘->과거 역적분 빌더        (PR-31)
  congruence       유체 합동 vorticity/가속도, CMB 쌍극             (PR-42)
"""
from __future__ import annotations

import importlib as _importlib


__all__ = [
    "integrate_H", "cosmic_time", "mean_scale_factor", "directional_scale_factors",
    "shear_scalar", "dimensionful", "lorentz_factor", "bbn_expansion_anisotropy",
    "observables",
]


def __getattr__(name: str):
    """Load historical helpers only when requested, not for units/history imports."""
    if name not in __all__:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    legacy = _importlib.import_module(f"{__name__}._legacy")
    value = getattr(legacy, name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
