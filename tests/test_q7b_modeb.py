"""
Q7b × Mode B · **움직이는 전자 + 완전 f** (81차).

★★ 반증 기록 (이 증분이 발견한 것):
  80차의 Mode B 충돌은 **공변 q 슬라이스**에서 방향을 섞었다.  충돌 핵은
  **고정 물리 p 에서** 섞으므로 μ(q̂) 가 방향마다 다르면 틀린다.
  실측: 비등방 프레임 (μ 비 3.2) + Planck 스펙트럼에서 lnĜ 최대차 **1.97**.
  Q7b 를 붙이며 발각 — 부스트가 같은 종류의 재격자화를 요구하기 때문이다.
  정정: δ_i = ln(μ_i 𝒟_i) 로 **공통 정지계 운동량 격자**로 옮겨 3항을 적용하고
  되돌린다 (Q4 반경 스텐실 재사용).  정정 후 최대차 8.3e−7 (n_p=300).

게이트:
  · ★★ Mode A ≡ Mode B (충돌 포함), n_p 정밀화로 **수렴**
  · v → 0 연속성 (정확히 정지전자 경로)
  · ★ 부스트가 운동량 플럭스를 만든다 — v 에 **선형**, 정확−O(v) 차는 v²
  · Mode A 부스트 ≡ Mode B 부스트 (Ĝ 닫힘의 Mode B 확인)
  · |v| ≥ 1 명시 거부
"""
import numpy as np
import pytest

RC = pytest.importorskip("bianchi_rustcore")
if not hasattr(RC, "qe_evolve"):
    pytest.skip("미빌드", allow_module_level=True)

from bianchi.q import comoving as CM  # noqa: E402
from bianchi.q import coupled as Q  # noqa: E402
from bianchi.q import modeb as B  # noqa: E402
from bianchi.q import sphere as S  # noqa: E402

M_ANISO = np.array([[1.6, 0, 0], [0, 0.7, 0], [0, 0, 0.5]]).ravel()


def _pair(sph, n_p, M=M_ANISO):
    b = B.planck_state(sph, n_p=n_p, lnq_min=-8.0, lnq_max=5.0)
    b.M = np.asarray(M, float).copy()
    a = Q.QState(sph, np.zeros((3, 3)), np.zeros((3, 3)), np.zeros(3),
                 lG=b.ln_ghat(), M=np.asarray(M, float).copy())
    return a, b


def _collide_both(a, b, x):
    a.collide(x)
    B.evolve(b, -1e-12, 1, nu=x * 1e12)
    return float(np.abs(a.lG - b.ln_ghat()).max())


def test_mode_a_equals_mode_b_under_collision_with_anisotropic_frame():
    """★★ 정정의 본체 — 80차의 O(1) 불일치가 사라진다."""
    sph = S.sphere(16, 32)
    for x in (0.5, 2.0):
        a, b = _pair(sph, 300)
        assert _collide_both(a, b, x) <= 5e-5, x


def test_agreement_converges_with_radial_range_not_resolution():
    """★★ 남은 차의 정체를 **분리**한다: n_p (해상도) 가 아니라 **반경 범위**
    (정의역 절단) 다.  δ_i = ln μ_i 시프트가 격자 밖으로 질량을 밀어내고, 그
    바깥은 해석 꼬리 확장이 근사하기 때문이다.

    실측 (12×24): 범위 [-6,3] 2.9e−2 → [-8,5] 7.5e−5 (여기서 **정지**),
    n_p 100→400 도 7.53e−5 에서 꿈쩍 안 함.  남은 바닥은 **각 해상도** 축이다
    (12×24 → 16×32 에서 7.5e−5 → 8.3e−7).  세 축을 다 분리해 못박는다."""
    sph = S.sphere(12, 24)
    # (a) n_p 만 올리면 안 줄어든다 (해상도 축 아님)
    same = [_collide_both(*_pair(sph, n_p), 1.0) for n_p in (100, 400)]
    assert abs(same[0] - same[1]) / same[0] < 0.05, same
    # (b) 범위를 넓히면 줄어들다가 바닥에 닿는다 (정의역 절단 축)
    rng = []
    for lo, hi, npp in ((-6.0, 3.0, 150), (-8.0, 5.0, 200)):
        b = B.planck_state(sph, n_p=npp, lnq_min=lo, lnq_max=hi)
        b.M = M_ANISO.copy()
        a = Q.QState(sph, np.zeros((3, 3)), np.zeros((3, 3)), np.zeros(3),
                     lG=b.ln_ghat(), M=M_ANISO.copy())
        rng.append(_collide_both(a, b, 1.0))
    assert rng[0] > 100.0 * rng[1], rng
    # (c) 바닥은 **각 해상도** 축 — 각을 올리면 다시 내려간다
    ang = []
    for nt in (12, 16, 24):
        a2, b2 = _pair(S.sphere(nt, 2 * nt), 200)
        ang.append(_collide_both(a2, b2, 1.0))
    assert ang[0] > 10.0 * ang[-1], ang
    assert ang[-1] < 1e-5, ang


def test_v_to_zero_is_exactly_the_static_path():
    sph = S.sphere(12, 24)
    b0 = B.planck_state(sph, n_p=120, lnq_min=-7.0, lnq_max=4.0)
    b0.M = M_ANISO.copy()
    b1 = B.planck_state(sph, n_p=120, lnq_min=-7.0, lnq_max=4.0)
    b1.M = M_ANISO.copy()
    b1.v_b = np.zeros(3)                       # 0 벡터는 None 으로 강등된다
    B.evolve(b0, -1e-12, 1, nu=1e12)
    B.evolve(b1, -1e-12, 1, nu=1e12)
    assert np.array_equal(b0.lnf, b1.lnf)


def _flux(b):
    """물리 프레임 운동량 플럭스 q_a/ρ (부스트가 만드는 l=1 성분)."""
    qhat, w_com = S.nodes(b.sph)
    fr = CM.frame_from(b.M)
    e, mu = CM.phys(fr, qhat)
    lw = CM.ln_phys_weights(fr, w_com, mu)
    return CM.moments_log(lw, b.ln_ghat(), e)[1]


@pytest.mark.parametrize("v", [1e-4, 1e-3, 1e-2])
def test_boost_generates_flux_linear_in_v(v):
    """★ 부스트가 운동량 플럭스를 만들고 그 크기가 v 에 선형."""
    sph = S.sphere(12, 24)
    b = B.planck_state(sph, n_p=200, lnq_min=-7.0, lnq_max=4.0)
    b.M = np.eye(3).ravel()                    # 등방 프레임에서 순수 부스트 효과
    b.v_b = np.array([v, 0.0, 0.0])
    f0 = _flux(b)
    B.evolve(b, -1e-12, 1, nu=1e12)
    f1 = _flux(b)
    d = abs(float(f1[0] - f0[0]))
    assert d > 0.1 * v, (v, d)                 # 실제로 생긴다
    assert d < 10.0 * v, (v, d)                # 그리고 O(v) 다


def test_flux_scaling_is_linear_in_v():
    sph = S.sphere(12, 24)
    ds = []
    for v in (1e-4, 1e-3, 1e-2):
        b = B.planck_state(sph, n_p=200, lnq_min=-7.0, lnq_max=4.0)
        b.M = np.eye(3).ravel()
        b.v_b = np.array([v, 0.0, 0.0])
        f0 = _flux(b)
        B.evolve(b, -1e-12, 1, nu=1e12)
        ds.append(abs(float(_flux(b)[0] - f0[0])))
    p = np.polyfit(np.log([1e-4, 1e-3, 1e-2]), np.log(ds), 1)[0]
    assert abs(p - 1.0) <= 0.1, (p, ds)


def test_mode_a_and_mode_b_agree_under_boost():
    """★ Ĝ 부스트 닫힘의 Mode B 확인 — 두 표현이 같은 답."""
    sph = S.sphere(12, 24)
    v = np.array([5e-3, 0.0, 0.0])
    b = B.planck_state(sph, n_p=400, lnq_min=-8.0, lnq_max=5.0)
    b.M = M_ANISO.copy(); b.v_b = v
    from bianchi.q.boost import collide_moving_log
    qhat, w_com = S.nodes(sph)
    fr = CM.frame_from(M_ANISO)
    e, mu = CM.phys(fr, qhat)
    lw = CM.ln_phys_weights(fr, w_com, mu)
    lg_a = collide_moving_log(lw, b.ln_ghat(), e, v, 1.0)
    B.evolve(b, -1e-12, 1, nu=1e12)
    assert float(np.abs(lg_a - b.ln_ghat()).max()) <= 1e-4


def test_superluminal_v_is_rejected():
    sph = S.sphere(8, 16)
    b = B.planck_state(sph, n_p=32)
    b.v_b = np.array([1.2, 0.0, 0.0])
    with pytest.raises(ValueError, match=r"\|v_b\| < 1"):
        B.evolve(b, -1e-3, 1, nu=1.0)
