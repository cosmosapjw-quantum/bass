"""
J3 · **계수공간 계층의 Rust 커널** — 좌표-동일 캐리 + 1호출 격자 (61차).

측정:
  · tilted 좌변 전 격자: Rust ≡ Python(equation_lhs_coeff, gm=ClosedGeoBlocks)
    — l≤6 (GeoMats 창 내) + l=10 (창 밖, 닫힌형 전용) 두 geo.
  · 질량블록: Rust ≡ mass_blocks_for — l=0(down=None)..6.  실측 **비트-정확**
    (성분당 곱 1회, 합 순서 동일) — 단 게이트는 0 아닌 1e−15 (R5b: 비트-정확
    주장은 경계를 재야 하므로 억제).
  · untilted RHS 격자: Rust ≡ hierarchy_rhs_coeff.
  · 벽: l_max=11 명시 거부 (c2 표 l_in ≤ 12 유도) — Python·Rust 양쪽.
  · 무언 폴백 금지: rustcore 부재 시 RuntimeError (R5b 회귀시험 교훈).
"""
import numpy as np
import pytest

from bianchi.matter import coeff_kernel as CK
from bianchi.matter import pstf_coeff as PC
from bianchi.matter import tilted_coeff as TC
from bianchi.matter import tilted_terms as TT
from bianchi.matter.hierarchy_coeff import hierarchy_rhs_coeff
from bianchi.matter.tilted_coeff import equation_lhs_coeff

pytest.importorskip("bianchi_rustcore")


@pytest.fixture(scope="module")
def geo():
    return TT.geometry(np.array([1.0, 1.1, 0.9]), np.array([0.3, 0.2, 0.4]),
                       np.array([0.12, -0.05, 0.08]),
                       np.array([0.02, 0.01, -0.03]))


@pytest.fixture(scope="module")
def geo2():
    return TT.geometry(np.array([0.8, 1.3, 1.05]), np.array([-0.1, 0.25, 0.15]),
                       np.array([-0.06, 0.11, 0.04]),
                       np.array([0.01, -0.02, 0.02]))


def _grids(l_max, i_max, seed):
    rng = np.random.default_rng(seed)
    Jc = {(l, i): rng.standard_normal(2*l + 1)
          for l in range(l_max + 3) for i in range(i_max + 3)}
    dJc = {(l, i): rng.standard_normal(2*l + 1)
           for l in range(l_max + 3) for i in range(i_max + 3)}
    return Jc, dJc


def test_lhs_grid_parity_within_geomats_window(geo, geo2):
    """★★ J3 의 심판 1: 좌변 전 격자 Rust ≡ Python — 두 geo, l≤6."""
    for k, gg in enumerate((geo, geo2)):
        cg = TC.ClosedGeoBlocks(gg)
        Jc, dJc = _grids(6, 2, seed=30 + k)
        got = CK.lhs_grid(Jc, dJc, gg, cg, 6, 2)
        worst = 0.0
        for l in range(7):
            for i in range(3):
                want = equation_lhs_coeff(Jc, dJc, gg, l, i, gm=cg)
                worst = max(worst, float(np.abs(got[(l, i)] - want).max()))
        assert worst <= 5e-14, worst


def test_lhs_grid_parity_beyond_window_l10(geo):
    """★★ J3 의 심판 2: GeoMats 창 밖 l=10 — 닫힌형 전용 영역의 두-경로."""
    cg = TC.ClosedGeoBlocks(geo)
    Jc, dJc = _grids(10, 2, seed=41)
    got = CK.lhs_grid(Jc, dJc, geo, cg, 10, 2)
    worst = 0.0
    for l in range(11):
        for i in range(3):
            want = equation_lhs_coeff(Jc, dJc, geo, l, i, gm=cg)
            worst = max(worst, float(np.abs(got[(l, i)] - want).max()))
    assert worst <= 1e-13, worst
    assert got[(10, 1)].shape == (21,)


def test_mass_blocks_parity(geo):
    """★ 질량블록 3종 — l=0 은 down=None 가지 포함."""
    for l in range(7):
        dg, up, dn = CK.mass_blocks(geo, l)
        d2, u2, n2 = TC.mass_blocks_for(geo, l)
        assert np.abs(dg - d2).max() <= 1e-15
        assert np.abs(up - u2).max() <= 1e-15
        if l == 0:
            assert dn is None and n2 is None
        else:
            assert np.abs(dn - n2).max() <= 1e-15


def test_rhs_grid_parity(geo):
    """★ untilted RHS 전 격자 — hierarchy_rhs_coeff 두-경로."""
    Jc, _ = _grids(6, 2, seed=52)
    s5 = PC.sigma_to_c5(geo["sigma"])
    got = CK.rhs_grid(Jc, 0.7, s5, 6, 2)
    worst = 0.0
    for l in range(7):
        for i in range(3):
            want = hierarchy_rhs_coeff(Jc, 0.7, s5, l, i)
            worst = max(worst, float(np.abs(got[(l, i)] - want).max()))
    assert worst <= 5e-14, worst


def test_kernel_wall_is_explicit(geo):
    """★ 벽: l_max=11 은 c2 표 (l_in=l+2≤12) 밖 — 명시 거부, KeyError 아님."""
    cg = TC.ClosedGeoBlocks(geo)
    Jc, dJc = _grids(11, 0, seed=60)
    with pytest.raises(ValueError, match="l_max"):
        CK.lhs_grid(Jc, dJc, geo, cg, 11, 0)
    with pytest.raises(ValueError, match="l_max"):
        CK.rhs_grid(Jc, 0.5, np.zeros(5), 11, 0)


def test_mass_wall_is_l11_not_l10(geo):
    """★ 리뷰 반영: cv 표는 l_out 인덱스 — 질량블록은 l=11 가능, l=12 거부.
    (첫 판 `l+1 > CV_MAX_L` 은 1 과잉제한 — l_in 혼동.)"""
    dg, up, dn = CK.mass_blocks(geo, 11)               # 좌변 벽(10) 밖에서도 가능
    assert dg.shape == (23, 23) and up.shape == (23, 25) and dn.shape == (23, 21)
    with pytest.raises(Exception, match="cv"):
        CK.mass_blocks(geo, 12)


def test_signs_passthrough(geo):
    """★ 부호 사전이 커널까지 관통 — divcon 뒤집으면 결과가 다르고,
    같은 뒤집힌 사전으로 Python 과 여전히 일치."""
    from bianchi.matter.tilted import SIGNS
    cg = TC.ClosedGeoBlocks(geo)
    Jc, dJc = _grids(4, 1, seed=71)
    flipped = dict(SIGNS)
    flipped["divcon"] = -flipped["divcon"]
    a = CK.lhs_grid(Jc, dJc, geo, cg, 4, 1)
    b = CK.lhs_grid(Jc, dJc, geo, cg, 4, 1, signs=flipped)
    assert np.abs(a[(2, 0)] - b[(2, 0)]).max() > 1e-6
    want = equation_lhs_coeff(Jc, dJc, geo, 2, 0, gm=cg, signs=flipped)
    assert np.abs(b[(2, 0)] - want).max() <= 5e-14


def test_stale_geo_rejected_at_ffi_boundary(geo2):
    """★ R5a 관통: ClosedGeoBlocks 의 스테일 가드가 FFI 진입 전에 발화."""
    gg = dict(geo2)
    gg["v"] = np.array(geo2["v"])
    cg = TC.ClosedGeoBlocks(gg)
    Jc, dJc = _grids(2, 1, seed=80)
    CK.lhs_grid(Jc, dJc, gg, cg, 2, 1)
    gg["v"] = np.array(gg["v"])                        # id 교체
    with pytest.raises(RuntimeError, match="R5a"):
        CK.lhs_grid(Jc, dJc, gg, cg, 2, 1)
