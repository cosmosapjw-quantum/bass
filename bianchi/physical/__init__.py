"""물리량 재구성 패키지 (Hubble 정규화 해 -> 관측 가능량).

기존 단일 모듈(physical.py)의 API 는 _legacy 에서 그대로 re-export 하여 하위호환.
신규 (v2.0):
  chart            τ <-> (H, t, ℓ) 왕복, IX D-차트 경로, 차원 복원  (PR-28)
  frame_transport  삼각대 전송 dP/dτ=(I+Σ+Ω)P, a_i(τ)              (PR-29)
  units, initial   CODATA 상수, Ω_i0, 오늘->과거 역적분 빌더        (PR-31)
  congruence       유체 합동 vorticity/가속도, CMB 쌍극             (PR-42)
"""
from bianchi.physical._legacy import (  # noqa: F401
    integrate_H, cosmic_time, mean_scale_factor, directional_scale_factors,
    shear_scalar, dimensionful, lorentz_factor, bbn_expansion_anisotropy,
    observables,
)
