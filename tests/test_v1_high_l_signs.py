"""
V1 · **l ≥ 4 tilted 부호** — rank-6 PSTF 격자에서 식 (12) 를 절단 없이 심판.

H5-d 는 l ≤ 3 까지만 검증했다 ("l=4 는 rank-6 필요" 로 기록).  l=4 방정식은 (B) 항이
rank-6 PSTF 텐서 J^(i)_{A_6} 를 이중축약하므로, 격자를 l_max=6 정확구적으로 채우면
계수·부호만 순수하게 시험된다.

측정 (ρ 규격, dt=1e−5 중앙차분 한계 ~1e−10):
```
m=0.0: i=0 1.44e−11  i=1 1.40e−11        m=0.7: 5.46e−11 / 3.90e−11
m=3.0: 1.11e−11 / 6.07e−12
부호 반전 8종 전부: 잔차 ×2.1e5 ~ ×4.4e7   ← 대조군의 이빨
```
⇒ l≤3 이중 오라클로 확정한 부호·계수가 l=4 에서 **그대로** 성립한다.  l-의존 계수
  (l/(2l+1), l/(2l+3), l(l−1)/(4l²−1), (l−n)) 는 이제 네 값의 l 로 과결정.

★ l=5 는 범위 밖 (정직): l=7 격자 = rank-7 대칭화 5040 순열 × 2187² — 시간 단위
  비용인데, 계수는 이미 과결정이라 정보가 없다.
"""
import numpy as np
import pytest

from audit import v1_high_l_signs as V
from bianchi.matter import tilted as TL
from bianchi.matter.hierarchy import (L_MAX_SUPPORTED, is_pstf, n_independent,
                                      pstf_operator)

MASS = 0.7          # 격자 캐시(≈18 s 1회)를 전 시험이 공유하도록 한 질량만 쓴다


# ═══════════════════════════════════════ rank-6 PSTF 기반
def test_rank6_pstf_operator_properties():
    """★★ Q₆: 멱등(6e−16), rank = 2·6+1 = 13, 출력이 대칭·무대각합."""
    q = pstf_operator(6)
    assert q.shape == (729, 729)
    assert np.abs(q @ q - q).max() < 1e-13
    s = np.linalg.svd(q, compute_uv=False)
    assert int((s > 1e-9).sum()) == n_independent(6) == 13
    rng = np.random.default_rng(0)
    t = (q @ rng.normal(size=729)).reshape((3,) * 6)
    assert is_pstf(t, tol=1e-10)


def test_l_max_supported_covers_rank6():
    assert L_MAX_SUPPORTED >= 6


# ═══════════════════════════════════════ ★★ l=4 잔차 (오라클)
def test_equation12_holds_at_l4():
    """★★ **머리기사** — l=4 잔차가 FD 한계 (실측 5.5e−11 / 3.9e−11)."""
    assert V.residual_l4(MASS, 0) < 5e-10
    assert V.residual_l4(MASS, 1) < 5e-10


def test_massless_l4_residual_and_i_degeneracy():
    """★ 무질량: l=4 잔차 FD 한계 + J^(i)_{A_4} 의 i-무관성 (L-C 문장의 rank-4 판)."""
    assert V.residual_l4(0.0, 0) < 2e-10
    _, J, _, rho = V._grids(0.0, 1e-05, 6, 3)
    gap = np.abs(np.asarray(J[(4, 0)], float) - np.asarray(J[(4, 1)], float)).max()
    assert gap < 1e-12 * rho


@pytest.mark.parametrize("key,min_amp", [("C", 1e6), ("divfree", 1e6), ("B", 1e4)])
def test_sign_flips_blow_up_the_l4_residual(key, min_amp):
    """★★ 대조군의 이빨 — 부호군 하나를 뒤집으면 잔차가 자릿수로 뛴다.

    최소 증폭기 B(×2.1e5)와 최대 증폭기 C/divfree(×3e7)를 대표로 고정한다.
    """
    base = V.residual_l4(MASS, 0)
    s = dict(TL.SIGNS)
    s[key] = -s[key]
    flipped = V.residual_l4(MASS, 0, signs=s)
    assert flipped > min_amp * base, (key, base, flipped)


# ═══════════════════════════════════════ 적분기 접합 (l_max=4)
def test_the_integrator_runs_at_l_max_4_without_degrading():
    """★ R5b Rust 커널이 l_max=4 를 그대로 소화한다 — 궤적오차가 l_max=3 과 동급.

    (H5-e3 측정: l 절단은 이미 포화 — l_max 를 올려도 오차가 거의 안 변한다.
     여기서는 '나빠지지 않는다' 만 게이트한다.)
    """
    from bianchi.matter import tilted_integrate as TI
    bg = TI.Background()
    e4 = TI.trajectory_error(bg, MASS, 0.2, 10, l_max=4, i_max=1)
    e3 = TI.trajectory_error(bg, MASS, 0.2, 10, l_max=3, i_max=1)
    for k in ("rho", "q", "pi"):
        assert e4[k] < 2.0 * e3[k] + 1e-12, (k, e3[k], e4[k])
    # 두 백엔드 일치 (l_max=4 에서도 오라클이 살아 있다)
    p4 = TI.trajectory_error(bg, MASS, 0.2, 10, l_max=4, i_max=1,
                             backend="python")
    for k in ("rho", "q", "pi"):
        assert abs(e4[k] - p4[k]) <= 1e-12 * max(p4[k], 1e-300)
