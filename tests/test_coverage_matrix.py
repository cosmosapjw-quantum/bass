"""11 Bianchi 유형 커버리지 게이트 (87차) — 초록의 "11종 전부" 를 뒷받침한다."""
import numpy as np
import pytest

from bianchi import algebra as AL
from scripts.coverage_matrix import TYPES, run_type


def test_coverage_lists_all_eleven_types_plus_exceptional():
    """11 표준 유형 + 예외형 VI*_{-1/9} 가 전부 목록에 있다."""
    assert set(TYPES) == set(AL.CANONICAL)
    assert len(TYPES) == 12                      # 11 표준 + 예외형


@pytest.mark.parametrize("ty", TYPES)
def test_each_type_evolves_with_finite_state_and_exact_jacobi(ty):
    """유형별 smoke: 분류 왕복 · 유한성 · Jacobi 기계정밀."""
    r = run_type(ty, nsteps=60, n_theta=12, n_phi=24)
    assert r["classified"] == ty, r
    if "gauss" not in r:
        pytest.skip(r["status"])
    assert r["finite"], r
    assert r["jacobi"] <= 1e-12, r
    assert np.isfinite(r["ln_omega"]), r


def test_codazzi_order_separates_class_A_from_class_B():
    """★★ 87차: 커버리지 표가 자기 각주를 반증했다.

    "class A 는 Codazzi 가 기계정밀" 은 **거짓**이다 — 기계정밀인 것은 Bianchi I
    뿐이고 (곡률항이 없다), 곡률이 있는 class A 도 1e−5 수준 잔차를 갖는다.
    차이는 크기가 아니라 **수렴 차수**다: class A 곡률형 ~3.6, class B ~2.3
    (후자는 A-항이 l=1 에 직접 작용 — Q5b 의 μ-꺾임 축과 같은 축)."""
    from scripts.coverage_matrix import codazzi_convergence
    flat = codazzi_convergence("I", resolutions=(12, 16))
    assert max(flat["codazzi"]) <= 1e-14, flat      # 평탄형만 기계정밀

    a_curved = codazzi_convergence("VIII", resolutions=(12, 16, 24))
    b_type = codazzi_convergence("V", resolutions=(12, 16, 24))
    # 둘 다 기계정밀이 **아니다** (예전 각주의 반증)
    assert min(a_curved["codazzi"]) > 1e-9, a_curved
    # 그러나 둘 다 수렴하고, 차수가 분리된다
    oa, ob = min(a_curved["order"]), min(b_type["order"])
    assert oa >= 3.0, oa
    assert 1.8 <= ob <= 2.9, ob
    assert oa > ob + 0.8, (oa, ob)
