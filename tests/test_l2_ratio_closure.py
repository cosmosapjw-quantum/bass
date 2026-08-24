"""
L2 · **비율 닫힘** — 원논문의 물리적 r 처방을 데이터 구동 `close_i` 와 겨룬다.

문헌:  초기 r ≈ (3w)^{1/2},  후기 r ≈ 5w,  그리고 이 조건이
      "frame-invariant to the order of our velocity-weight truncation".
L1 에서 프레임 효과가 **tilt 오염도**로 드러남을 확인했으므로 그 단서를 여기서 잰다.

★ 이 파일이 고정하는 측정:
  1. r₀ = 3w 는 **정의상 항등식** (J^(1) ≡ 3p) — 잴 것이 없다.  l ≥ 1 만 의미 있다.
  2. l=2 의 비가 상대론 영역에서 **√(3w) 와 4자리 일치** (w=0.3226 에서 상대오차 4e−5).
  3. 5w 는 **l=1 에서만** 맞는다 (논문이 J_a 로 쓴 그대로) — 낮은 w 에서 상대오차가
     0.157 까지 내려가며 계속 개선.  반면 l≥2 에서는 낮은 w 에서 상대오차 > 1 로 발산.
  4. ★★ r 은 **l 에 의존**한다 (r_l = ⟨v^{l+2}⟩/⟨v^l⟩): w=0.005 에서 r₃/r₁ = 2.54.
     단일 r 처방은 그 자체로 근사다 — 이것이 `phys_5w` 가 적분기에서 나쁜 이유.
  5. ★ **정직한 부정 결과**: 물리 처방이 적분기에서 데이터 구동 닫힘을 **못 이긴다**.
     "frame-invariant" 단서도 tilt 오염도 감소로 나타나지 않는다.
"""
import numpy as np
import pytest

from bianchi.matter import tilted_closure as TC


# ═══════════════════════════════ 1. 항등식과 정의
def test_l0_ratio_is_an_identity_not_a_measurement():
    """★ r₀ = J^(1)/J^(0) = 3p/ρ = 3w — **정의상** 그렇다 (측정이 아니다).

    처음에 이걸 '5w 와 0.6 배로 일치' 라고 읽을 뻔했다.  0.6 = 3/5 는
    3w/5w 일 뿐 물리가 아니다.
    """
    from bianchi.matter import hierarchy as H
    a = (1.0, 0.85, 1.18)
    for m in (0.0, 1.0, 5.0):
        rho = H.J_moment(a, m, 0, 0)
        j1 = H.J_moment(a, m, 0, 1)
        w = j1 / (3.0 * rho)
        assert abs(j1 / rho - 3.0 * w) < 1e-14


def test_physical_ratio_reduces_to_massless_degeneracy():
    """★ 무질량 w = 1/3 에서 √(3w) = 1 — 우리가 정확히 아는 축퇴와 맞는다.

    반면 5w = 5/3 이라 **어긋난다** — 왜 phys_5w 가 상대론 영역에서 나쁜지의 근거.
    """
    assert abs(TC.physical_ratio(1 / 3, "phys_sqrt") - 1.0) < 1e-15
    assert abs(TC.physical_ratio(1 / 3, "phys_interp") - 1.0) < 1e-15
    assert abs(TC.physical_ratio(1 / 3, "phys_5w") - 5 / 3) < 1e-15


def test_interpolation_has_the_right_two_limits():
    """보간이 3w→1 에서 1, 3w→0 에서 5w 로 간다 (문헌의 두 극한)."""
    assert abs(TC.physical_ratio(1 / 3, "phys_interp") - 1.0) < 1e-12
    w = 1e-4
    assert abs(TC.physical_ratio(w, "phys_interp") / (5 * w) - 1.0) < 0.05


def test_unknown_physical_mode_raises():
    with pytest.raises(ValueError):
        TC.physical_ratio(0.1, "phys_7w")


# ═══════════════════════════════ 2. ★ 문헌 공식의 검증 범위
def test_sqrt_3w_is_excellent_for_l2_in_the_relativistic_regime():
    """★★ w = 0.3226 에서 r₂ 와 √(3w) 의 상대오차가 **4e−5** — 문헌 확인."""
    rows = TC.exact_ratio_vs_w(masses=(0.5,), l=2)
    _, w, r, s3w, _, _ = rows[0]
    assert abs(r / s3w - 1.0) < 1e-4, rows


def test_alpha_moves_from_one_half_toward_one():
    """★ 유효 지수 α (r = (3w)^α) 가 0.50 → 0.82 로 간다 — 문헌 보간 방향과 일치.

    (다만 우리 질량 범위에서 1 에 닿지는 않는다 — 정직하게 기록.)
    """
    rows = TC.exact_ratio_vs_w(masses=(0.5, 5.0, 60.0), l=2)
    al = [r[5] for r in rows]
    assert abs(al[0] - 0.5) < 0.01, rows
    assert al[0] < al[1] < al[2], rows
    assert al[2] < 1.0, rows


def test_five_w_works_only_for_l_equals_one():
    """★★ 5w 는 **l=1 에서만** 맞는다 (논문이 J_a 로 쓴 그대로).

    낮은 w 에서 l=1 상대오차는 0.157 까지 내려가지만, l=2 는 1.02 로 **발산**한다.
    """
    r1 = TC.formula_crossover(1)["rows"][-1]      # 가장 낮은 w
    r2 = TC.formula_crossover(2)["rows"][-1]
    assert r1[2] < 0.25, r1                        # l=1: 5w 상대오차 작다
    assert r2[2] > 0.9, r2                         # l=2: 5w 상대오차 크다


def test_crossover_is_not_monotone_for_l2():
    """★ **측정 도구를 한 번 틀렸던 기록**: l=2 의 승자가 단조가 아니다.

    처음에 절대오차 + 이분법으로 짰다가 첫 교차만 잡고 나머지를 놓쳤다.
    상대오차 + 스캔으로 바꾸니 l=1 은 전환 1회, l=2·3 은 **2회**로 드러난다.
    """
    assert TC.formula_crossover(1)["n_flips"] == 1
    assert TC.formula_crossover(2)["n_flips"] == 2
    assert TC.formula_crossover(3)["n_flips"] == 2


def test_ratio_is_genuinely_l_dependent():
    """★★ r_l = ⟨v^{l+2}⟩/⟨v^l⟩ 이라 l 마다 다르다 — **단일 r 처방의 한계**.

    측정: w=0.297 에서 r₃/r₁ = 1.05,  w=0.005 에서 **2.54**.
    비상대론으로 갈수록 단일 r 이 나빠진다.
    """
    rows = TC.ratio_is_l_dependent()
    assert rows[0][4] < 1.1, rows
    assert rows[-1][4] > 2.0, rows
    assert all(a[4] < b[4] for a, b in zip(rows, rows[1:])), rows


# ═══════════════════════════════ 3. ★ 동역학적 주장 (n_*=3 끌개)
def test_attractor_ratio_tracks_the_exact_ratio():
    """★ n_*=3 절단의 동역학적 비가 정확 구적의 비를 따라간다.

    ★ 우리 배경에는 k-모드가 없다 = **큰 스케일 극한 그 자체**라 논문의 조건이
      자동 충족된다.  측정 (m=1, t=0): r_dyn 0.9356 vs r_exact 0.9273.
    """
    rows = TC.attractor_ratio(mass=1.0, t_end=0.3, nsteps=30)
    t, rd, f5w, s3w, rex = rows[0]
    assert abs(rd / rex - 1.0) < 0.05, rows


def test_five_w_overestimates_the_attractor_in_the_relativistic_regime():
    """★ 우리 w 범위에서 5w 는 끌개를 과대평가하고 √(3w) 가 항상 더 가깝다.

    ★ 처음에 "1.5배 이상" 이라고 적었다가 t=0.28 에서 1.39 로 걸렸다.  과대평가
      배수는 **시간에 따라 줄어든다** (t_end=0.6, m=1 측정: 1.58 → 1.25) —
      w 가 떨어지며 5w 의 적용 영역에 가까워지기 때문이다.  주장을 측정에 맞춘다.
    """
    rows = TC.attractor_ratio(mass=1.0, t_end=0.3, nsteps=30)
    ratios = [f5w / rd for t, rd, f5w, s3w, rex in rows]
    assert min(ratios) > 1.2, rows
    assert ratios[0] > ratios[-1], rows                      # 시간에 따라 줄어든다
    for t, rd, f5w, s3w, rex in rows:
        assert abs(s3w / rd - 1.0) < abs(f5w / rd - 1.0), (t, rd, s3w, f5w)


# ═══════════════════════════════ 4. ★★ 정직한 부정 결과
def test_physical_closure_does_not_beat_the_data_driven_one():
    """★★ **문헌 처방이 적분기에서 이기지 못한다** (측정, m=1, l_max=i_max=3):

        모드          v=0        v=0.15      오염비
        frozen      2.19e−5    3.47e−5     +0.581
        ratio       1.89e−5    3.72e−5     +0.970
        phys_sqrt   1.88e−5    3.71e−5     +0.975
        phys_5w     3.79e−4    1.14e−3     +1.998

    phys_sqrt 는 ratio 와 사실상 동률이고, phys_5w 는 **20배 나쁘다**
    (단일 r 을 모든 l 에 적용하는데 5w 는 l=1 전용이기 때문).
    """
    rows = dict((md, (e0, ev)) for m, md, e0, ev, c in
                TC.closure_mode_comparison(masses=(1.0,),
                                           modes=("ratio", "phys_sqrt", "phys_5w")))
    assert rows["phys_sqrt"][0] < 1.2 * rows["ratio"][0], rows      # 동률 수준
    assert rows["phys_5w"][0] > 5.0 * rows["ratio"][0], rows        # 훨씬 나쁘다


def test_frame_invariance_claim_does_not_reduce_tilt_contamination():
    """★★ 문헌의 "frame-invariant" 단서가 **tilt 오염도 감소로 나타나지 않는다**.

    측정 (m=1): 오염비가 frozen +0.581 < phys_interp +0.876 < ratio +0.970
                ≈ phys_sqrt +0.975 < phys_5w +1.998.
    즉 데이터 구동 `frozen` 이 오히려 가장 프레임에 둔감하다 — **반증으로 기록**한다.
    (선형이론의 프레임 불변성이 우리 비선형 배경에서 자동으로 이득이 되지는 않는다.)
    """
    rows = dict((md, c) for m, md, e0, ev, c in
                TC.closure_mode_comparison(masses=(1.0,),
                                           modes=("frozen", "phys_sqrt", "phys_5w")))
    assert rows["frozen"] < rows["phys_sqrt"], rows
    assert rows["frozen"] < rows["phys_5w"], rows


def test_physical_modes_do_not_disturb_the_default_path():
    """★ 회귀: 기존 기본값(ratio)의 결과가 이번 변경으로 바뀌지 않았다."""
    from bianchi.matter import tilted_integrate as TI
    e = TI.trajectory_error(TI.Background(), 1.0, 0.2, 20, 3, 3)
    assert abs(e["rho"] - 2.5606e-06) < 1e-9, e
    assert abs(e["pi"] - 1.2648e-05) < 1e-8, e
