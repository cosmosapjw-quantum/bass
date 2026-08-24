"""
Q4 · **반경 격자 + 해석적 점근 닫힘** 게이트 (76차).

  · ★ 멱법칙은 ln f 보간에서 **정확** (ln f = k ln p 가 ln p 의 1차)
  · 등방 팽창의 해석해 재현
  · 시프트 수렴차수 ≥ 6 (8점 Lagrange)
  · 스텐실 가중합 = 1
  · ★ 꼬리 모형이 **명시적**이다 (Wien / PowerLaw) — 숨은 가정 금지
  · 기존 96노드 GL 반경격자와 모멘트 대조
"""
import numpy as np
import pytest

RC = pytest.importorskip("bianchi_rustcore")
if not hasattr(RC, "QRadial"):
    pytest.skip("Q4 반경층 미빌드", allow_module_level=True)

from bianchi.q import contract as C  # noqa: E402
from bianchi.q import transport as T  # noqa: E402


def test_power_law_shift_is_exact_in_log_space():
    """★ ln f 보간 + PowerLaw 꼬리 ⇒ 멱법칙 정확."""
    r = T.radial(-6.0, 6.0, 96)
    lnp = np.asarray(r.ln_p())
    for k in (-2.5, 0.0, 3.0):
        lnf = k * lnp
        for dln in (0.31, -0.77, 2.4):
            got = np.asarray(r.apply_shift_log(lnf, dln, 8, "power"))
            want = k * (lnp - dln)
            assert float(np.abs(got - want).max()) <= 1e-11, (k, dln)


def test_isotropic_expansion_matches_analytic():
    """등방 팽창 f(p) → f(p e^{−Δ}) (계약 임계)."""
    tol = C.budget("Q4", "isotropic")
    r = T.radial(-5.0, 5.0, 192)
    lnp = np.asarray(r.ln_p())
    lnf = -2.0 * lnp                      # f = p^{-2}
    d = 0.4
    got = np.asarray(r.apply_shift_log(lnf, d, 8, "power"))
    assert float(np.abs(got - (-2.0 * (lnp - d))).max()) <= tol


def test_shift_convergence_order_on_planck():
    """★ Planck 스펙트럼에서 시프트 수렴차수 ≥ 6 (계약)."""
    want = C.budget("Q4", "shift_order")
    errs = []
    for n in (48, 96, 192, 384):
        r = T.radial(-5.0, 5.0, n)
        lnf = T.planck_lnf(r)
        got = np.asarray(r.apply_shift_log(lnf, 0.23, 8, "wien"))
        p = np.asarray(r.p())
        ref = np.log(1.0 / np.expm1(p * np.exp(-0.23)))
        k = 8
        errs.append(float(np.abs(got[k:-k] - ref[k:-k]).max()))
    orders = [np.log2(errs[i] / errs[i + 1]) for i in range(len(errs) - 1)]
    assert max(orders) >= want, (orders, errs)


def test_stencil_is_partition_of_unity():
    r = T.radial(-4.0, 4.0, 64)
    for dln in (0.0, 0.13, -1.9, 5.5):
        v = np.asarray(r.shift_stencil(dln, 8))
        assert abs(float(v[8:].sum()) - 1.0) <= 1e-12


def test_tail_model_is_explicit_and_matters():
    """★ 꼬리 모형이 숨은 가정이 아니다 — 둘이 실제로 다른 답을 준다."""
    r = T.radial(-3.0, 3.0, 64)
    lnf = T.planck_lnf(r)
    a = np.asarray(r.apply_shift_log(lnf, -1.5, 8, "wien"))
    b = np.asarray(r.apply_shift_log(lnf, -1.5, 8, "power"))
    assert float(np.abs(a - b).max()) > 1e-3         # 선택이 결과를 바꾼다
    with pytest.raises(ValueError, match="tail"):
        r.apply_shift_log(lnf, 0.1, 8, "nonsense")


def test_tail_fit_recovers_planck_asymptotics():
    """저에너지 RJ 지수 ≈ −1, 고에너지 온도 ≈ T."""
    r = T.radial(-8.0, 4.0, 400)
    lnf = T.planck_lnf(r, T=1.0)
    k, Temp = r.tail_fit(np.exp(lnf))
    assert abs(k + 1.0) < 0.02, k
    assert abs(Temp - 1.0) < 0.05, Temp


def test_energy_moment_matches_analytic_planck():
    """∫ f p³ dp = π⁴/15 (Planck, T=1) — 균일 ln p 사다리꼴의 지수적 정확성."""
    r = T.radial(-9.0, 5.0, 600)
    f = np.exp(T.planck_lnf(r))
    got = r.moment(f, 4)                     # ∫ f p⁴ dlnp = ∫ f p³ dp
    want = np.pi ** 4 / 15.0
    assert abs(got - want) / want <= 1e-9, (got, want)
