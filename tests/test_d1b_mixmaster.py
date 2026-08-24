"""
D1b · **Mixmaster 연속 튐** — u 수열이 BKL 사상을 따르는가.

D1 은 Bianchi II 로 **한 번의 튐**을 오라클 삼아 Kasner 사상을 측정했다.  여기서는
벽이 셋인 IX/VIII 에서 **연속으로** 튀는 것을 잡는다.

★ 방향이 D1 과 반대다.  Mixmaster 의 튐은 **특이점 쪽**(τ 감소)에서 일어난다.
  부호 실수를 피하려고 τ̃ = −τ 로 뒤집은 RHS 를 써서 D1 의 사건 정의를 그대로 쓴다.
  특이점 쪽으로는 **Σ₊ > 1/2 인 벽**이 자란다 (D1 의 정반대) — D1 이 잰 것이 BKL 의
  **역**이었던 것과 앞뒤가 맞는다.

★ u 는 **튐 지점에서 읽으면 안 된다** (그 순간 벽이 최대라 Kasner 원에서 멀다).
  튐 사이에서 max_i N_i 가 최소인 곳에서 읽는다.

★ 이 파일이 고정하는 측정 (u₀ = 3.7, 씨앗 1e−3, IX):
```
  #   τ̃_bounce  벽    u(에라)      BKL 예측     |차|      maxN
  0     6.5017  N1   3.7000004                          1.0e−03
  1    18.2832  N2   2.7000019   2.7000004  1.44e−06   1.5e−04
  2    30.8984  N1   1.7000019   1.7000019  2.31e−08   4.0e−06
  3    49.2605  N2   1.4285676   1.4285676  7.98e−12   8.3e−11
```
  **두 가지가 다 나온다**: u−1 감소 세 번, 그리고 u<2 에서 1/(u−1) 재주입
  (1/(1.7−1) = 1.4285714).  에라 구조도 확인 — u₀=5.4 에서 5.4→4.4→3.4→2.4→1.4.

★ **반증된 기대**: "혼돈이라 튐마다 오차가 커진다" 고 적고 쟀는데 **정반대**였다.
  오차가 1.4e−06 → 2.3e−08 → 8.0e−12 로 **줄어든다** — 비활성 벽이 에라마다
  기하급수로 죽어 구간이 점점 더 Kasner 다워지기 때문이다.  이 구간의 한계는
  혼돈 증폭이 아니라 **벽의 언더플로** (maxN 1e−03 → 8.3e−11 → 배정밀도 바닥).

★ 씨앗 교환관계: 10배 줄이면 첫 오차가 ~100배 준다 (1.4e−04 → 1.4e−06).  대신 튐
  하나에 드는 τ̃ 가 길어져 같은 span 으로는 튐을 덜 잡는다.

★ 오차는 **적분 tolerance 가 아니라 씨앗**이 정한다: rtol 을 1e−12 → 1e−10 으로
  풀어도 u 가 9자리까지 그대로다 (3.700000440 / 2.700001876 / 1.700001899 /
  1.428567554).  조이는 쪽으로는 얻을 게 없다는 뜻이다.
"""
import numpy as np
import pytest

from bianchi.analysis import kasner as K
from bianchi.analysis import mixmaster as M


# ═══════════════════════════════ 1. 방향과 사건 정의
def test_the_growing_wall_flips_toward_the_singularity():
    """★★ 특이점 쪽으로는 **Σ₊ > 1/2** 인 벽이 자란다 (D1 의 정반대)."""
    y0, args = M.mixmaster_ic(3.7, 1e-3)
    fwd = K.wall_rates(y0, args["gamma"])
    past = M.past_wall_rates(y0, args["gamma"])
    assert np.allclose(past, -fwd), (fwd, past)
    assert float(y0.Sigma_p) > 0.5
    assert past[0] > 0.0 > fwd[0]


def test_initial_data_is_on_the_vacuum_surface():
    """★ D1 의 반증 기록 (a) — 벽을 켜면 Σ²=1 은 Ω=0 이 아니다."""
    from bianchi.charts import class_a as ca
    y0, args = M.mixmaster_ic(3.7, 1e-3)
    assert abs(float(ca.aux(y0, args["gamma"])["Omega"])) < 1e-14


# ═══════════════════════════════ 2. ★★ u 수열이 BKL 사상을 따른다
def test_the_u_sequence_follows_the_bkl_map():
    """★★ **D1b 의 핵심** — 연속 튐의 u 가 BKL 사상을 따라간다."""
    r = M.u_sequence(n_bounce=4)
    assert len(r["u"]) >= 4, r["u"]
    assert max(r["err"]) < 1e-4, r["err"]
    assert abs(r["u"][0] - 3.7) < 1e-5, r["u"]


def test_both_branches_appear_in_one_sequence():
    """★★ 감소(u−1) 세 번과 **재주입** 1/(u−1) 이 한 수열에 다 나온다."""
    r = M.u_sequence(n_bounce=4)
    u = r["u"]
    for a, b in zip(u[:3], u[1:3]):
        assert abs(b - (a - 1.0)) < 1e-4, u          # u ≥ 2 가지
    assert abs(u[3] - 1.0 / (u[2] - 1.0)) < 1e-4, u  # 1 < u < 2 가지
    assert 1.0 < u[3] < 2.0, u


def test_u_is_read_between_bounces_not_at_the_bounce():
    """★ 기록 지점의 벽이 작다 (가장 Kasner 다운 순간) — 그래서 u 가 의미 있다."""
    r = M.u_sequence(n_bounce=4)
    for row in r["rows"]:
        assert row[4] < 1e-2, row                    # maxN at epoch
        assert abs(row[5]) < 1e-10, row              # Ω (진공 유지)


def test_era_structure_is_a_run_of_unit_decrements():
    """★ u₀ = 5.4 는 5.4 → 4.4 → 3.4 → 2.4 → 1.4 — 한 에라가 통째로 나온다."""
    rows = M.era_structure(u0=5.4, n_bounce=3)
    assert len(rows) >= 2, rows
    for a, b, kind in rows:
        assert kind == "감소", rows
        assert abs(b - (a - 1.0)) < 1e-4, rows


# ═══════════════════════════════ 3. ★★ 무엇이 한계인가 (반증 기록)
def test_the_error_shrinks_along_the_sequence_not_grows():
    """★★ **반증된 기대** — 혼돈 증폭이 아니라 오차가 **줄어든다**.

    비활성 벽이 에라마다 기하급수로 죽어 구간이 더 Kasner 다워지기 때문이다.
    """
    r = M.resolvable_bounces(n_bounce=4)
    e = r["err"]
    assert len(e) >= 3, e
    for a, b in zip(e, e[1:]):
        assert b < a, e
    assert r["good"] == len(e), r


def test_the_walls_underflow_geometrically():
    """★ 한계의 정체 — 에라마다 maxN 이 1e−03 → 1.5e−04 → 4e−06 → 8e−11 로 죽는다."""
    r = M.u_sequence(n_bounce=4)
    mx = [row[4] for row in r["rows"]]
    for a, b in zip(mx, mx[1:]):
        assert b < a, mx
    assert mx[-1] < 1e-9, mx


def test_smaller_seed_buys_accuracy():
    """★ 씨앗 10배 감소 → 첫 오차 ~100배 감소 (교환관계는 튐 수)."""
    rows = M.seed_dependence(seeds=(1e-2, 1e-3), n_bounce=2)
    (s1, e1, _, n1), (s2, e2, _, n2) = rows
    assert s1 > s2 and e1 > e2, rows
    assert e1 / e2 > 10.0, rows


# ═══════════════════════════════ 4. 대조군
def test_type_VIII_bounces_too():
    """★ VIII (n = +,+,−) 도 같은 사상을 따른다 — IX 만의 성질이 아니다."""
    r = M.type_VIII_also_bounces(n_bounce=2)
    assert len(r["u"]) >= 2, r["u"]
    assert max(r["err"]) < 1e-4, r["err"]


def test_type_II_bounces_exactly_once():
    """★★ 벽이 하나면 튐도 한 번 — D1 의 오라클과 앞뒤가 맞는다."""
    assert M.type_II_bounces_once() == 1


def test_type_I_never_bounces():
    """★ 벽이 없으면 튐이 0 번."""
    assert M.type_I_never_bounces() == 0
