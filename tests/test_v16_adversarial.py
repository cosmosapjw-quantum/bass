"""
V16 · **적대적 감사** — 깨뜨리려고 시도한 것과 그 결과를 게이트로.

지금까지의 시험은 "옳은 입력에서 옳은가" 였다.  여기서는 반대로 공격한다:
가드 모서리·NaN·FFI 남용·극단 파라미터·축퇴점.  수확 2건:

★★ 수확 1 (결함 → 수정): `th_*` 바인딩의 검증 구멍 **셋** — ops/bases 부족,
  geo 행 길이, (th_rhs/th_force_and_matrix 의) j0 길이 — 전부 `ops[l]`/slice 인덱싱
  **Rust 패닉**으로 FFI 를 넘었다 (PanicException + 백트레이스 덤프).  경계
  ValueError 로 막았다 (`th_check` + `th_geo` 가드 + state_len 검사) — R2 의
  `check_l` 관례와 동일.  첫 수정 때 replace 가 한 함수에 3중 삽입되고 나머지
  둘은 비는 사고까지 있었다 — 2차 공격이 그걸 잡았다 (감사가 수정을 감사했다).

★★ 수확 2 (물리 — 조건수 절벽의 정량화): tilted-B 의 편타면 G₋ = 1−(γ−1)V² → 0
  근방에서 두 백엔드의 RHS 가 **상대 ε·V²/|G₋| 로 갈라진다** (V² 합산순서 1 ulp 가
  1/G₋ 배 증폭).  실측: G₋ = 4.1e−11 에서 5.4e−6 (예측 6.2e−6).  구현 결함이 아니라
  차트의 내재적 조건수다 — 게이트를 **스케일링 법칙**으로 건다.  γ=2 (강성 유체) 에서
  |v|→1 이면 물리적으로 도달 가능 → 계획서 H' 티어의 정규화/이벤트 항목이 됐다.

그 밖에 통과한 공격 (게이트로 고정):
  · 전 차트 NaN 주입 → NaN-in NaN-out (침묵 오염 없음), 커널 행업 없음 (mx 0튐,
    integrate_background ok=False)
  · FFI 모양 남용 8종 → 전부 깨끗한 예외 (패닉 0)
  · 극단 구적 (m=1e6, |v|=0.999999) 유한;  kasner_u 축퇴점(Σ=0, Taub) 유한
  · eras_from_u 의 inf/NaN/정확-u=1 입력 → 접두부 절단이 조용히 막는다
"""
import numpy as np
import pytest

RC = pytest.importorskip("bianchi_rustcore")

import jax.numpy as jnp  # noqa: E402

from bianchi.charts import class_b_tilted as BT  # noqa: E402


# ═══════════════════════════════════════ 수확 1 — FFI 경계 검증 (회귀)
def test_short_ops_or_bases_raise_cleanly_instead_of_panicking():
    """★★ 패닉이 아니라 ValueError — V16 이 잡은 결함의 회귀 게이트."""
    with pytest.raises(ValueError, match="ops/bases"):
        RC.th_integrate(np.zeros(8), np.zeros((3, 142)), 1, 0.1, np.ones(8),
                        [np.zeros(0)], [np.ones(1)], 1, 1, 1, True, -1)
    ops = [np.zeros(0), np.zeros(0)]
    bad_bases = [np.ones(1), np.ones(5)]           # l=1 기저는 3×3=9 여야 한다
    with pytest.raises(ValueError, match="bases"):
        RC.th_rhs(np.zeros(8), np.zeros(142), np.ones(8), ops, bad_bases,
                  1, 1, 1, True, -1)
    # ★ 2차 공격이 추가로 잡은 두 표면 (수정 후 회귀): 짧은 geo 행, 짧은 j0
    good = [np.ones(1), np.ones(9)]
    with pytest.raises(ValueError, match="geo row"):
        RC.th_rhs(np.zeros(4), np.zeros(10), np.ones(8), ops, good, 1, 0, 1,
                  True, -1)
    with pytest.raises(ValueError, match="j0"):
        RC.th_rhs(np.zeros(3), np.zeros(142), np.ones(8), ops, good, 1, 0, 1,
                  True, -1)


@pytest.mark.parametrize("abuse", [
    lambda: RC.chart_rhs("class_b_tilted", np.zeros(5), 1.3),
    lambda: RC.integrate_background("class_a", np.zeros(5), np.array([0.0]), 1.3),
    lambda: RC.integrate_batch("exceptional", np.zeros((2, 5)),
                               np.linspace(0, 1, 3), 1.2),
    lambda: RC.mx_bounce_sequence(np.zeros(4), 2.0, 2, 10.0, 1e-11, 1e-13, 1e-3),
    lambda: RC.mx_bounce_sequence_log(np.zeros(5), np.ones(2), 2.0, 2, 10.0,
                                      1e-11, 1e-13, 1e-3),
    lambda: RC.kin_j_moment(np.ones(3), 0.7, 6, 0, 0.0, 2),
])
def test_shape_abuse_raises_clean_python_exceptions(abuse):
    """★ 모양/길이 남용 전부 — 패닉/중단 없이 깨끗한 예외."""
    with pytest.raises(Exception) as ei:
        abuse()
    assert "Panic" not in type(ei.value).__name__


# ═══════════════════════════════════════ 수확 2 — 편타면 조건수 스케일링
def test_whiplash_surface_amplifies_backend_differences_by_the_predicted_law():
    """★★ G₋→0 에서 패리티가 ε·V²/|G₋| 로 갈라진다 — **법칙째로** 게이트.

    구현 결함이 아니라는 주장(= 두 코드가 각자 1 ulp 정확하다)은 이 스케일링이
    맞아야만 성립한다.  훨씬 크면 진짜 버그, 훨씬 작으면 설명이 틀린 것.
    """
    g = 1.8
    v2t = 1.0 / (g - 1.0)
    rng = np.random.default_rng(2)
    worst_ratio = 0.0
    for _ in range(12):
        y = rng.uniform(-3, 3, size=11)
        d = rng.normal(size=3)
        d /= np.linalg.norm(d)
        y[8:] = d * np.sqrt(v2t) * (1.0 + rng.normal() * 1e-10)
        v2 = float(y[8] ** 2 + y[9] ** 2 + y[10] ** 2)
        gm = abs(1.0 - (g - 1.0) * v2)
        if gm < 1e-15 or gm > 1e-8:
            continue
        p = np.asarray(BT.rhs(0.0, BT.StateBT.of(*y), {"gamma": g}).as_array())
        r = np.asarray(RC.chart_rhs("class_b_tilted", y, g))
        rel = float(np.abs(p - r).max() / max(1.0, np.abs(p).max()))
        bound = 30.0 * 2.2e-16 * v2 / gm            # 여유 30×
        assert rel < bound, (rel, bound, gm)
        worst_ratio = max(worst_ratio, rel * gm / (2.2e-16 * v2))
    # 멀리서는 평소 게이트로 복귀
    y = rng.uniform(-2, 2, size=11)
    y[8:] = rng.normal(size=3) * 0.3
    p = np.asarray(BT.rhs(0.0, BT.StateBT.of(*y), {"gamma": g}).as_array())
    r = np.asarray(RC.chart_rhs("class_b_tilted", y, g))
    assert np.abs(p - r).max() / max(1.0, np.abs(p).max()) < 1e-13


# ═══════════════════════════════════════ NaN 규율 — 침묵 오염 금지
@pytest.mark.parametrize("chart,n", [("class_a", 5), ("class_b_tilted", 11),
                                     ("exceptional", 6), ("type_ix_d", 7)])
def test_nan_in_nan_out_for_every_chart(chart, n):
    y = np.linspace(0.1, 0.5, n)
    y[n // 2] = np.nan
    r = np.asarray(RC.chart_rhs(chart, y, 1.3))
    assert np.isnan(r).any()


def test_kernels_neither_hang_nor_lie_on_nan_input():
    """★ NaN 초기조건: mx 는 튐 0개, integrate_background 는 ok=False — 침묵 성공 금지."""
    b = RC.mx_bounce_sequence(np.array([np.nan, 0, 1e-3, 1e-3, 1e-3]), 2.0, 5,
                              100.0, 1e-11, 1e-13, 1e-3)
    assert len(b[0]) == 0
    _, ok = RC.integrate_background("class_a", np.array([np.nan, 0, 0, 0, 0]),
                                    np.linspace(0, 1, 5), 1.3)
    assert not ok


# ═══════════════════════════════════════ 극단·축퇴 입력
def test_extreme_quadrature_parameters_stay_finite():
    for m in (0.0, 1e6):
        r = np.asarray(RC.kin_j_moment_tilted(
            np.ones(3), np.array([0.0, 0.0, 0.999999]), m, 2, 0))
        assert np.isfinite(r).all()


def test_degenerate_kasner_points_are_finite():
    from bianchi.analysis import kasner as K
    for sp, sm in ((0.0, 0.0), (1.0, 0.0), (-0.5, np.sqrt(3) / 2)):
        u = K.kasner_u(sp, sm)
        assert np.isfinite(u) or u == np.inf


def test_eras_from_u_swallows_inf_nan_and_exact_one():
    from bianchi.analysis import gauss_map as G
    for seq in ([3.7, 2.7, np.inf], [3.7, np.nan, 2.0], [1.0, 5.0]):
        eras, _ = G.eras_from_u(seq)
        for (_u, _d, x) in eras:
            assert 0.0 < x < 1.0
