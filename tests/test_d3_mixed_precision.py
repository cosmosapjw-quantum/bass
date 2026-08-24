"""
D3 · **혼합정밀 (특이점 근방)** — 표현이 죽는 곳을 재고, 표현 혼합으로 고친다.

D1b 가 확정한 한계("혼돈 증폭이 아니라 벽의 언더플로")를 직접 공격한 증분.
고침은 정밀도 상향이 아니라 **표현 혼합**: Σ± 는 f64 그대로, 벽만 w = ln|N| —
곱셈 구조 dN/dτ = rate·N 이 덧셈 dw/dτ = rate 가 되어 물리가 근사 없이 옮겨진다
(항등 실측 8.9e−16).

★★ 측정이 뒤집은 것 둘:
  1. 선형 벽의 실효 바닥은 표현(−708)이 아니라 **atol** 이다 — 골이 1e−13(=atol)에
     핀되어 회복 τ 가 인위 단축, **가짜로 이른 튐**이 생긴다 (372 vs 참 520).
     u 는 사상 강건성 때문에 6e−6 으로 계속 맞아 **u 만 보면 못 잡는다** — τ 간격의
     기하급수성이 판별량이다.
  2. "로그벽이면 D1c 앙상블이 깊어진다" 는 기대는 **반증**됐다 — 에라가 오히려
     890 < 1130 으로 준다.  선형의 atol-핀이 깊은 에라를 인위적으로 싸게 만들어
     수확을 부풀렸던 것.  λ·KS 는 오차 내 일치 — D1c 의 **통계 결론은 강건**하고,
     τ 에 기대는 양만 선형에서 못 믿는다.

★★ 로그가 드러낸 다음 한계는 물리다: 골 깊이 |w| 가 에라마다 기하급수(비 1.6~3.2,
  Δτ 비와 1% 이내로 같음 — 회복 τ ∝ |w| 의 실측)로 자라 **튐 수 ~ O(ln τ_budget)**.
  어떤 표현도 못 고친다.

★ f32 결정표 (E1 GPU): 그림자 지평 f32 ≈ 8 에라 / f64 ≈ 16.5 (예측 ln(1/ε)/λ =
  6.7/15.2), u 판독은 f32 로 δu ≲ 1e−4 (u ≤ 50) 허용, 구속감시 Ω 는 상쇄바닥
  1.2e−7 로 **불가**.
"""
from functools import lru_cache

import numpy as np
import pytest

from bianchi.analysis import gauss_map as G
from bianchi.analysis import mixmaster as MX
from bianchi.analysis import precision as P

pytestmark = pytest.mark.skipif(not MX.rust_available(),
                                reason="bianchi_rustcore 없음 (D3 는 Rust 커널 대상)")


@lru_cache(maxsize=1)
def _depth():
    return P.depth_comparison()


@lru_cache(maxsize=1)
def _rows():
    y0, args = MX.mixmaster_ic(2.0 + 2.0 ** -0.5, 1e-3, "IX")
    lin = MX.bounce_sequence(y0, args, n_bounce=12, tau_max=8000.0)
    log = MX.bounce_sequence(y0, args, n_bounce=12, tau_max=8000.0, walls="log")
    return lin, log


# ═══════════════════════════════════════ 표현의 정확성
def test_log_rhs_is_an_exact_reexpression():
    """★★ dw/dτ = Ṅ/N 항등 — 로그 커널의 물리가 선형과 **같다** (표현만 다르다)."""
    assert P.log_rhs_identity() < 1e-13


def test_log_and_linear_agree_in_the_overlap():
    """★ 겹치는 구간의 u 가 1e−4 이내 (실측 6.2e−6) — R4 의 오라클 사슬을 상속."""
    assert _depth()["overlap_du"] < 1e-4


def test_log_walls_reach_depths_linear_cannot_represent():
    """★★ 로그판 최저 골 w = −2197 < 선형 표현한계 −708 — 증분의 존재 이유."""
    d = _depth()
    assert d["deepest"] < 3.0 * P.LINEAR_FLOOR
    assert d["linear_can_represent"] is False


# ═══════════════════════════════════════ ★★ 선형의 실효 바닥은 atol 이다
def test_linear_troughs_pin_at_the_atol_floor():
    """★★ 선형 골이 표현 바닥(1e−308)이 아니라 **atol(1e−13)** 에 핀된다.

    처음 가설은 "선형은 denormal 바닥에서 죽는다" 였다 — 실측은 그보다 훨씬 먼저,
    오차제어가 벽을 놓는 지점이었다.  가설을 측정으로 고친 자리.
    """
    lin, log = _rows()
    late = [r[4] for r in lin[3:]]
    assert late, "선형 튐이 너무 적다"
    assert all(1e-14 < m < 1e-11 for m in late), late      # atol=1e-13 띠
    # 같은 구간에서 참 골(로그)은 atol 로그값(≈ −30)보다 자릿수로 깊다
    assert min(r[4] for r in log) < 10.0 * np.log(1e-13)


def test_linear_fabricates_early_bounces_beyond_its_floor():
    """★★ atol-핀 → 회복 τ 인위 단축 → **가짜로 이른 튐** (실측 372 vs 참 520).

    ★ 함정을 함께 못박는다: 그 구간에서도 u 는 1e−4 로 맞는다 — 사상 강건성이
      시간 조작을 가려 **u 만 보면 못 잡는다**.
    """
    lin, log = _rows()
    # ★ 문턱의 근거 (측정으로 고쳤다): max_n 열은 **가장 얕은** 벽의 w 라, 그것이
    #   atol 로그값(−30)을 갓 지난 구간(k=3,4: w=−101,−157)에서는 **튀는 벽** 자체는
    #   아직 핀 위에 있어 τ 왜곡이 없다 (실측 비 1.00).  얕은 벽조차 −240 아래면
    #   튀는 벽은 확실히 핀 아래다 — 그 구간(k≥5)에서 왜곡이 시작된다 (0.71→0.24).
    fabricated = [k for k in range(min(len(lin), len(log)))
                  if log[k][4] < 8.0 * np.log(1e-13)]
    assert fabricated, "참 골이 문턱 아래로 내려간 튐이 없다 — 시험 전제가 깨졌다"
    for k in fabricated:
        assert lin[k][0] < 0.85 * log[k][0], (k, lin[k][0], log[k][0])
        assert abs(lin[k][2] - log[k][2]) < 1e-3           # u 는 여전히 맞다 (함정)


def test_trough_growth_is_geometric_and_tau_tracks_w():
    """★★ 다음 한계는 물리 — |w_골| 기하급수, Δτ 비가 |w| 비를 1% 이내로 따른다."""
    t = P.trough_growth()
    assert len(t["ratios_w"]) >= 3
    assert t["ratios_w"][-2] > 1.5                          # 명백한 기하급수
    for rw, rt in zip(t["ratios_w"], t["ratios_tau"]):
        assert abs(rw - rt) / rw < 0.05, (rw, rt)           # 회복 τ ∝ |w|


# ═══════════════════════════════════════ f32 결정표 (E1)
def test_shadow_horizon_scales_with_precision():
    """★ 그림자 지평 n* ≈ ln(1/ε)/λ — f32 ≈ 8, f64 ≈ 16.5 에라, 비 ≈ 53/24 비트."""
    f32 = P.shadow_horizon(float(np.finfo(np.float32).eps), n_orbit=120)
    f64 = P.shadow_horizon(float(np.finfo(np.float64).eps), n_orbit=120)
    assert 6.0 < f32["mean"] < 10.0, f32
    assert 13.0 < f64["mean"] < 19.0, f64
    assert 1.7 < f64["mean"] / f32["mean"] < 2.4
    assert f32["mean"] > f32["predicted"] - 1.0             # 예측이 하한 노릇


def test_u_readout_tolerates_f32_but_omega_does_not():
    """★★ 혼합의 근거 — u 판독은 f32 허용(δu ≲ 1e−3), 구속감시 Ω 는 상쇄로 불가."""
    cond = P.u_conditioning()
    assert all(noise < 1e-3 for (_u, _g, noise) in cond)
    floor = P.omega_cancellation_floor()
    assert floor > 3e-8                                     # ≈ eps32 급 (실측 1.2e−7)
    assert floor > 30.0 * 1e-9                              # 1e−9 급 게이트 불가


# ═══════════════════════════════════════ D1c 와의 접합 (반증 기록)
def test_d1c_statistics_are_robust_across_wall_representations():
    """★★ **반증 기록** — "로그벽이면 앙상블이 깊어진다" 는 틀렸다 (890 < 1130 에라).

    선형의 atol-핀이 깊은 에라를 인위적으로 싸게 만들어 수확을 부풀렸던 것.
    그러나 u 기반 통계(λ, 밀도)는 오차 내 일치 — D1c 의 결론은 표현에 강건하다.
    """
    a = G.ode_ensemble()
    b = G.ode_ensemble(walls="log")
    assert len(b["x"]) < len(a["x"])                        # 부풀림의 증거
    la, sa = G.lyapunov_estimate(a["x"])
    lb, sb = G.lyapunov_estimate(b["x"])
    assert abs(la - lb) < 2.5 * float(np.hypot(sa, sb))
    for d in (a, b):
        ks = G.ks_to_gauss(d["x"])
        assert ks < 1.36 / np.sqrt(len(d["x"])) * 1.6, ks
    lam_th = G.LYAPUNOV
    assert abs(lb - lam_th) < 3.5 * sb                      # 로그판도 보편값과 맞다


# ═══════════════════════════════════════ 배선
def test_walls_log_requires_the_rust_kernel():
    y0, args = MX.mixmaster_ic(3.7, 1e-3, "IX")
    with pytest.raises(NotImplementedError):
        MX.bounce_sequence(y0, args, n_bounce=2, backend="python", walls="log")


def test_type_viii_signs_flow_through_the_log_kernel():
    """★ VIII (N₃ < 0) — 부호가 로그 표현을 지나 곡률·전단원천에 살아 닿는다."""
    y0, args = MX.mixmaster_ic(3.7, 1e-3, "VIII")
    rows = MX.bounce_sequence(y0, args, n_bounce=4, tau_max=200.0, walls="log")
    assert len(rows) >= 3
    us = [r[2] for r in rows]
    assert abs(us[1] - (us[0] - 1.0)) < 1e-3                # BKL 사상 첫걸음
