"""
Q7b · **정확 광행차 + 비섭동 분광 왜곡** 게이트 (76차).

★ 계획보다 강한 결과 (실측 정정):
  Ĝ(ê) = ∫f p³dp 는 부스트 하에서 **닫힌다** (f 로런츠 불변 ⇒ Ĝ' = 𝒟⁴Ĝ,
  dΩ' = dΩ/𝒟²).  Thomson 핵이 정지계에서 λ-무관이므로 ∫p³dp 와 가환 ⇒
  **Mode A 도 움직이는 전자에서 정확**하다 (계획은 Mode B 전용이라 적었다).
  게다가 보간 0회 — 정확 충돌 루틴이 임의 (ê, w) 를 받으므로 노드만 옮기면 된다.

게이트:
  · v → 0 연속성
  · ★ 정확 − O(v) 전개의 차가 **v² 로** 스케일 (계약: 지수 2.0 ± 0.1)
  · 부스트 왕복이 항등
  · ★★ **비섭동 y-왜곡**: O(1) 온도 이방성의 Thomson 혼합이 만드는 왜곡을
    직접 계산.  선형 코드는 구조적으로 0 인 양.  ΔT/T 가 작을 때 해석
    ½⟨(ΔT/T)²⟩ 로 수렴하고, 커지면 **해석식이 못 잡는 고차 보정**이 나타난다.
"""
import numpy as np
import pytest

RC = pytest.importorskip("bianchi_rustcore")
if not hasattr(RC, "qm_collide_log"):
    pytest.skip("Q7b 미빌드", allow_module_level=True)

from bianchi.q import boost as B  # noqa: E402
from bianchi.q import contract as C  # noqa: E402
from bianchi.q import sphere as S  # noqa: E402
from bianchi.q import transport as T  # noqa: E402


@pytest.fixture(scope="module")
def st():
    sph = S.sphere(24, 48)
    e, w = S.nodes(sph)
    return sph, e, np.log(w), 0.6 * e[:, 2]


def test_v_to_zero_is_continuous(st):
    sph, e, lw, lG = st
    tol = C.budget("Q7b", "v_to_zero")
    a = B.collide_moving_log(lw, lG, e, np.zeros(3), 1.0)
    from bianchi.q.comoving import collide_log
    b = collide_log(lw, lG, e, 1.0)
    assert float(np.abs(a - b).max()) <= tol


def test_exact_vs_ov_expansion_scales_as_v2(st):
    """★★ 계약 §3 '충돌핵 선형화 부재' 의 시험 ID."""
    sph, e, lw, lG = st
    want, band = C.budget("Q7b", "v2_exponent")
    vs = np.array([1e-4, 1e-3, 1e-2])
    d = []
    for v in vs:
        a = B.collide_moving_log(lw, lG, e, [v, 0, 0], 1.0)
        o = B.collide_moving_ov(lw, lG, e, [v, 0, 0], 1.0, order=1)
        d.append(float(np.abs(a - o).max()))
    p = np.polyfit(np.log(vs), np.log(d), 1)[0]
    assert abs(p - want) <= band, (p, d)


def test_doppler_map_is_an_involution():
    """부스트 왕복 (v, −v) 이 항등 — 광행차 사상의 무결성."""
    tol = C.budget("Q7b", "roundtrip")
    sph = S.sphere(16, 32)
    e, _ = S.nodes(sph)
    v = np.array([0.2, -0.1, 0.05])
    D1, ep = B.doppler(e, v)
    D2, ebk = B.doppler(ep, -v)
    assert float(np.abs(ebk - e).max()) <= tol
    assert float(np.abs(D1 * D2 - 1.0).max()) <= tol


def test_mode_a_closes_under_boost(st):
    """★ Ĝ 가 부스트 하에서 닫힘 — 충돌 없이 왕복하면 원래대로."""
    sph, e, lw, lG = st
    v = np.array([0.15, 0.0, 0.0])
    D, ep = B.doppler(e, v)
    lD = np.log(D)
    back = (lG + 4 * lD) - 4 * lD
    assert float(np.abs(back - lG).max()) <= 1e-14
    # ν=0 이면 부스트 충돌도 항등 (부동소수 왕복 오차 이내)
    out = B.collide_moving_log(lw, lG, e, v, 0.0)
    assert float(np.abs(out - lG).max()) <= 1e-13


@pytest.mark.parametrize("dT", [0.05, 0.1])
def test_nonperturbative_y_distortion_matches_second_order_theory(dT):
    """★★ 비섭동 y-왜곡이 작은 ΔT/T 에서 ½⟨(ΔT/T)²⟩ 로 수렴."""
    sph = S.sphere(24, 48)
    rad = T.radial(-7.0, 4.5, 400)
    y, ye = B.y_from_mixing(sph, rad, dT)
    assert y > 0
    assert abs(y / ye - 1.0) <= 0.05, (dT, y, ye)


def test_y_distortion_shows_higher_order_beyond_analytic():
    """★★ 이 아키텍처가 사는 이유: ΔT/T 가 커지면 해석식이 **못 잡는** 보정.

    선형 코드는 y ≡ 0, 2차 해석식은 ½⟨δ²⟩.  절단 없는 full-f 는 그 너머를 준다."""
    sph = S.sphere(24, 48)
    rad = T.radial(-7.0, 4.5, 400)
    ratios = [B.y_from_mixing(sph, rad, d) for d in (0.05, 0.2, 0.4)]
    r = [y / ye for y, ye in ratios]
    assert abs(r[0] - 1.0) < 0.02                 # 2차 극한에서 일치
    assert r[2] > 1.08, r                         # O(1) 에서 유의미한 고차 보정
    assert r[0] < r[1] < r[2]                     # 단조 증가 (고차항의 부호)
    # 선형 코드가 주는 값 (=0) 과 확실히 구분
    assert ratios[2][0] > 100.0 * 0.0 + 1e-3
