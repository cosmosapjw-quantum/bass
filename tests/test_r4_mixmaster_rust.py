"""
R4 · **Mixmaster 튐 수열을 Rust 로** — 그리고 그제서야 보이는 혼돈.

D1b 의 Python/diffrax 판은 튐 하나마다 세 벽에 각각 이벤트를 걸어 긴 구간을 적분하고
상태를 되감아 다시 시작했다 (튐 4번에 12번의 긴 적분, 회귀 19 → 26 분).  R4 는
**한 번 굴리면서** 세 사건함수를 동시에 감시한다 — 되감기도 중복 적분도 없다.

★ 측정:
```
u_sequence(n_bounce=4)   python 105.3 s → rust 0.0030 s      35109배
u 값 차                   0.0 / 5.5e−12 / 1.6e−12 / 8.2e−12
τ̃ 차                      4.5e−11 / 1.1e−09 / 2.6e−08 / 2.3e−05
```
적분기가 아예 다르다 (diffrax Kvaerno5 암묵 vs 직접 짠 Dormand-Prince 5(4) 명시).
그런데도 u 가 1e−12 로 맞는다 — D1b §4 가 "오차는 씨앗이 정한다" 고 잰 것과 일관된다.

★★ **Rust 가 생기고서야 잴 수 있게 된 것**: D1b 는 튐 4번에서 끊겨 "혼돈 증폭이
  아니라 오차가 줄어든다" 고 기록했다.  이제 10번까지 가니 **둘 다 맞다**:
```
 k   u(궤적)         이상 BKL        누적차     |d bkl/du| at k
 0   3.700000440    3.700000440    0.00e+00   1.00
 3   1.428567554    1.428570530    2.98e-06   5.44
 4   2.333354431    2.333338224    1.62e-05   1.00      ← 2.98e−06 × 5.44
 5   1.333354431    1.333338224    1.62e-05   9.00
 6   2.999810142    2.999955982    1.46e-04   1.00      ← 1.62e−05 × 9.00
 8   1.000189924    1.000044020    1.46e-04   2.77e+07  ← u → 1 (Taub)
 9   2584.0011      22716.9611     2.01e+04
```
  **국소** 사상오차는 벽이 죽으며 줄지만, **누적 표류**는 사상 미분의 곱으로 정확히
  자란다 (2.98e−06 × 5.44 = 1.62e−05, 1.62e−05 × 9.00 = 1.46e−04 — 자릿수가 아니라
  값이 맞는다).  추적이 깨지는 지점은 궤적이 u = 1 (Taub 점) 근처를 지나
  d(bkl)/du = 1/(u−1)² 가 2.8e+07 이 되는 곳이다.  그게 BKL 혼돈의 정체다.

★ 멀리 가니 하나 더 보였다: **γ=2 의 진공면 중립성은 Kasner 원 위에서만**이다.
  튐을 지날 때 q ≠ 2 라 그 구간에서 지수가 0 이 아니고, τ̃ ≈ 1242 까지 굴리면
  |Ω| 가 1e−16 → 4.0e−08 로 샌다 (Python 판의 τ̃ ≈ 49 에서는 안 보였다).
"""
import numpy as np
import pytest

from bianchi.analysis import kasner as K
from bianchi.analysis import mixmaster as M

pytestmark = pytest.mark.skipif(not M.rust_available(),
                                reason="bianchi_rustcore 없음 (Python 폴백만)")


# ═══════════════════════════════ 1. ★★ 두 적분기가 같은 답을 낸다
def test_rust_kernel_matches_the_diffrax_oracle():
    """★★ **차등시험** — 적분기가 다른데도 u 가 1e−10 안에서 같다.

    Python 판은 diffrax Kvaerno5(암묵), Rust 판은 Dormand-Prince 5(4)(명시)다.
    """
    ref = M.u_sequence(n_bounce=4, backend="python")
    got = M.u_sequence(n_bounce=4)
    assert len(got["u"]) >= len(ref["u"]), (ref["u"], got["u"])
    for a, b in zip(ref["u"], got["u"]):
        assert abs(a - b) < 1e-10, (a, b)
    for ra, rb in zip(ref["rows"], got["rows"]):
        assert abs(ra[0] - rb[0]) < 1e-3, (ra[0], rb[0])     # τ̃_bounce
        assert ra[1] == rb[1], (ra[1], rb[1])                # 어느 벽


def test_the_rust_path_is_the_default_and_the_oracle_is_still_reachable():
    """★ 포트가 오라클을 지우지 않았다 — `backend="python"` 이 살아 있다."""
    assert M.rust_available()
    r = M.bounce_sequence(*M.mixmaster_ic(3.7, 1e-3), n_bounce=1, span=20.0,
                          backend="python")
    assert len(r) == 1


# ═══════════════════════════════ 2. ★★ 멀리 가야 보이는 것
def test_the_sequence_now_reaches_ten_bounces():
    """★★ D1b 는 튐 4번에서 끊겼다 — 이제 10번까지 간다 (τ̃ ≈ 1226)."""
    r = M.u_sequence(n_bounce=12, tau_max=3000.0)
    assert len(r["u"]) >= 10, r["u"]
    assert r["rows"][-1][0] > 500.0, r["rows"][-1]


def test_it_tracks_the_ideal_bkl_sequence_for_nine_bounces():
    """★★ 이상적 BKL 수열과 **9번** 같이 간다 (누적 표류 < 1e−3)."""
    t = M.bkl_tracking(n_bounce=12)
    assert t["tracked"] >= 8, (t["tracked"], t["drift"])
    assert t["drift"][0] == 0.0
    assert t["drift"][t["tracked"] - 1] < 1e-3, t["drift"]


def test_the_accumulated_drift_is_the_product_of_map_derivatives():
    """★★ **혼돈의 정체** — 누적 표류가 사상 미분의 곱으로 자란다.

    d(bkl)/du = 1 (u≥2 가지), 1/(u−1)² (1<u<2 가지).  표류가 그 배율로 커진다.
    """
    d = M.map_derivative_explains_the_blowup(n_bounce=12)
    drift, deriv = d["drift"], d["deriv"]
    checked = 0
    for k in range(1, min(len(drift) - 1, d["tracked"])):
        if drift[k] < 1e-12 or deriv[k] > 1e3:
            continue
        pred = drift[k] * deriv[k]
        if pred < 1e-12:
            continue
        assert 0.5 < drift[k + 1] / pred < 2.0, (k, drift, deriv)
        checked += 1
    assert checked >= 3, (checked, drift, deriv)


def test_the_blowup_happens_at_the_taub_point():
    """★★ 추적이 깨지는 곳은 u → 1 (Taub) 이고 거기서 사상 미분이 2.8e+07 이다."""
    d = M.map_derivative_explains_the_blowup(n_bounce=12)
    assert d["min_u"] < 1.001, d["min_u"]
    assert d["worst_deriv"] > 1e6, d["worst_deriv"]
    k = int(np.argmax(d["deriv"]))
    assert abs(d["u"][k] - 1.0) < 1e-3, (k, d["u"])


def test_both_bkl_branches_recur_many_times():
    """★ 긴 수열에서 감소·재주입이 여러 번 번갈아 나온다."""
    r = M.u_sequence(n_bounce=12, tau_max=3000.0)
    u = r["u"][:9]
    dec = sum(1 for a, b in zip(u, u[1:]) if a >= 2.0 and abs(b - (a - 1.0)) < 1e-3)
    rei = sum(1 for a, b in zip(u, u[1:])
              if a < 2.0 and abs(b - 1.0 / (a - 1.0)) < 1e-2)
    assert dec >= 3, (dec, u)
    assert rei >= 2, (rei, u)


# ═══════════════════════════════ 3. 대조군 (Rust 경로)
def test_no_wall_no_bounce_in_rust():
    """★ 벽이 없으면 튐이 0 번 (Rust 경로에서도)."""
    assert M.type_I_never_bounces() == 0


def test_one_wall_bounces_once_in_rust():
    """★ 벽이 하나면 튐도 한 번 — D1 의 오라클과 정합."""
    assert M.type_II_bounces_once() == 1


def test_vacuum_drifts_slowly_because_gamma_2_is_only_neutral_on_the_circle():
    """★ **긴 적분에서 드러난 것** — γ=2 의 중립성은 Kasner 원 위에서만이다.

    D1 §3 은 `Ω′ = [2q−(3γ−2)]Ω` 의 지수가 Kasner 원(q=2)에서 6−3γ 이고 γ=2 면 0 이라
    했다.  맞다 — 다만 **튐을 지날 때는 q ≠ 2** 라 그 구간에서만 지수가 0 이 아니다.
    τ̃ ≈ 1242 (튐 9번) 까지 굴리면 |Ω| 가 1e−16 에서 **4.0e−08** 로 천천히 샌다.
    Python 판(튐 4번, τ̃ ≈ 49)에서는 1e−10 이라 보이지 않던 양이다.
    """
    r = M.u_sequence(n_bounce=10, tau_max=3000.0)
    oms = [abs(row[5]) for row in r["rows"][:9]]
    assert max(oms) < 1e-6, oms                  # 여전히 물리적으로 무해
    assert oms[-1] > oms[0], oms                 # 그러나 **0 은 아니다**
    assert oms[0] < 1e-14, oms
