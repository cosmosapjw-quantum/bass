"""
J2c · **기하 3항의 닫힌 재구성 → l>6 tilted 완전 가동** (60차).

측정·반증 사슬:
  · perp X-부 = 순수 회전 (I·c1 계수 ~1e−17 — 사틀 회전항 수치 증명).
  · div X-부: 순수 cv/ov 스팬 **반증** (잔차 2.8e−2 — V₂-결합 실재);
    합성족 {cv, B∘cv} 로 정확 (7e−17).
  · ★ 단일-l 적합의 연장 실패 반증 (2.7e−2): 중복방향 최소노름이 원인 —
    **결합적합(l=2,3)** 이 연산자-일관 해를 고정, 보류 l=4,5,6 예측 ≤2.8e−16
    (l-균일 항등 증명; J1 dense-창 인식론과 동일).
  · Q-부 닫힌형: perp=γI, div_con=γCV_v, div_free=γOV_v (질량블록 일치).
  · R5a 가드: geo 배열 교체 시 명시 예외 (리뷰 MAJOR 반영).
"""
import numpy as np
import pytest

from bianchi.matter import pstf_coeff as PC
from bianchi.matter import tilted_coeff as TC
from bianchi.matter import tilted_terms as TT


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


def test_closed_blocks_predict_held_out_l(geo, geo2):
    """★★ J2c 의 심판: 적합창 (2,3) 밖 l=4..6 에서 닫힌 재구성 ≡ 직접 추출."""
    for gg in (geo, geo2):
        cg = TC.ClosedGeoBlocks(gg)
        gm = TC.GeoMats(gg)
        worst = 0.0
        for l in (4, 5):
            worst = max(worst, float(np.abs(cg.div_con(l)[0]
                                            - gm.div_con(l)[0]).max()))
        for l in (4, 5, 6):
            worst = max(worst, float(np.abs(cg.div_free(l)[0]
                                            - gm.div_free(l)[0]).max()))
            worst = max(worst, float(np.abs(cg.perp_dot(l)[0]
                                            - gm.perp_dot(l)[0]).max()))
        assert worst <= 5e-15, worst


def test_pure_vec_span_is_falsified(geo):
    """★ 반증 박제: div_con X-부는 cv(3) 만으로 안 닫힌다 (V₂-결합 실재)."""
    gm = TC.GeoMats(geo)
    P = gm.div_con(3)[0]
    A = np.stack([PC.contract_vec_block(3)[:, :, a].ravel()
                  for a in range(3)], axis=1)
    c, *_ = np.linalg.lstsq(A, P.ravel(), rcond=None)
    assert np.abs(A @ c - P.ravel()).max() > 1e-2


def test_single_l_fit_does_not_extend(geo):
    """★ 반증 박제: 단일-l(2) 적합은 l=4 로 연장 실패 (중복방향 최소노름)."""
    gm = TC.GeoMats(geo)
    fam2 = TC.ClosedGeoBlocks._cv_fams(2)
    A = np.stack([x.ravel() for x in fam2], axis=1)
    c, *_ = np.linalg.lstsq(A, gm.div_con(2)[0].ravel(), rcond=None)
    pred4 = sum(ci * f for ci, f in zip(c, TC.ClosedGeoBlocks._cv_fams(4)))
    assert np.abs(pred4 - gm.div_con(4)[0]).max() > 1e-3


def test_perp_x_part_is_pure_rotation(geo):
    """★ 사틀 회전항의 수치 증명: perp 계수의 I·c1 성분 ~0, B 성분만 생존."""
    cg = TC.ClosedGeoBlocks(geo)
    assert np.abs(cg.c_pd[:6]).max() <= 1e-14      # I(1) + c1(5)
    assert np.abs(cg.c_pd[6:]).max() > 1e-5        # B_a(3)


def test_closed_blocks_stale_geo_guard(geo2):
    """★ R5a 가드: geo 배열 교체 후 접근 시 명시 예외 (무언 스테일 금지)."""
    gg = dict(geo2)
    gg["v"] = np.array(geo2["v"])
    cg = TC.ClosedGeoBlocks(gg)
    cg.perp_dot(4)
    gg["v"] = np.array(gg["v"])                    # 제자리 교체 재현 (id 변경)
    with pytest.raises(RuntimeError, match="R5a"):
        cg.div_con(3)


def test_q_parts_are_closed_form(geo):
    """★ Q-부: perp=γI, div_con=γ·CV_v, div_free=γ·OV_v (임의 l 대조)."""
    cg = TC.ClosedGeoBlocks(geo)
    gm = TC.GeoMats(geo)
    for l in (3, 6):
        assert np.abs(cg.perp_dot(l)[1] - gm.perp_dot(l)[1]).max() <= 1e-14
        assert np.abs(cg.div_free(l)[1] - gm.div_free(l)[1]).max() <= 1e-14
    assert np.abs(cg.div_con(5)[1] - gm.div_con(5)[1]).max() <= 1e-14


def test_tilted_lhs_runs_at_l10_fully_closed(geo):
    """★★ 구조 전환 완결: l=10 tilted 좌변 전항 가동 (3^10 무생성) +
    l≤4 에서 닫힌-기하 조립 ≡ 추출-기하 조립 (경로 동등성)."""
    rng = np.random.default_rng(9)
    Jc = {(l, i): rng.standard_normal(2*l + 1)
          for l in range(13) for i in range(5)}
    dJc = {(l, i): rng.standard_normal(2*l + 1)
           for l in range(13) for i in range(5)}
    cg = TC.ClosedGeoBlocks(geo)
    out = TC.equation_lhs_coeff(Jc, dJc, geo, 10, 1, gm=cg)
    assert out.shape == (21,) and np.isfinite(out).all()
    gm = TC.GeoMats(geo)
    for l in (0, 2, 4):
        for i in (0, 1):
            a = TC.equation_lhs_coeff(Jc, dJc, geo, l, i, gm=cg)
            b = TC.equation_lhs_coeff(Jc, dJc, geo, l, i, gm=gm)
            assert np.abs(a - b).max() <= 5e-14, (l, i)
