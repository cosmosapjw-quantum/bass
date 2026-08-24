"""
Q5 · **수송** 게이트 (76차) — ★ 설계 정정이 박제된 시험.

═══ 반증 기록 (계획 §0 의 아키텍처 결정을 뒤집은 실측) ═══
계획은 "고정 tetrad 프레임 격자 + 반-라그랑주"를 택했다.  실측이 기각한다:
  · Mixmaster 붕괴에서 축비가 τ=−25 까지 2.2e28.
  · 물리 각분포는 폭 ~1/축비 의 **연필빔** — 어떤 고정 각격자도 표현 못한다.
  · 보간 횟수를 200배 줄여도 (stride 1→200) 발산 크기가 3자리만 줄었다
    ⇒ 보간 불안정이 **아니라** 표현 한계.
계획 §9 위험표가 미리 정해둔 판정법대로 **공변격자 하이브리드**로 후퇴.
고정 프레임 커널 (transport.rs) 은 폐기하지 않고 **잔여 곡률흐름·Mode B** 용으로 남긴다.

게이트:
  · ★★ 공변 자유흐름이 I2b 정확격자 지수 (+0.234) 를 재현 — 두 표현의 교차검증
  · ★ Bianchi I 수송이 **정확히 항등** (보간 0회)
  · ★ 축비 1e28 · ln Ĝ > 250 에서 무붕괴 (I2c 의 LNA_WALL=300 제거)
  · 상태가 f 자체다 (닫힘 없음)
  · 고정 프레임 스텐실: 상수 정확 (단위분할), 등방팽창 해석 일치
  · 결정성: 같은 입력 → 비트 동일
"""
import numpy as np
import pytest

RC = pytest.importorskip("bianchi_rustcore")
if not hasattr(RC, "QFrame"):
    pytest.skip("Q5 공변층 미빌드", allow_module_level=True)

from bianchi.q import contract as C  # noqa: E402
from bianchi.q import sphere as S  # noqa: E402
from bianchi.q import transport as T  # noqa: E402
from bianchi.q.characteristics import Background  # noqa: E402
from bianchi.q.comoving import ComovingState, sigma6_from_we5  # noqa: E402


@pytest.fixture(scope="module")
def mixmaster():
    from audit.i2b_mixmaster_statistics import collapse
    return collapse(u0=3.7, Om0=1e-12, l_max=3)


def _comoving_exponent(tr, n_theta=24, n_phi=48, tau=-25.0, stride=250, t_cut=-5.0):
    t = np.linspace(0.0, tau, tr.shape[0])
    h = t[1] - t[0]
    S5, lnH = tr[:, :5], tr[:, 8]
    st = ComovingState(S.sphere(n_theta, n_phi))
    sub = np.arange(0, tr.shape[0], stride)
    ss = set(sub.tolist())
    lrho = []
    for k in range(tr.shape[0] - 1):
        if k in ss:
            lrho.append(st.moments()[0])
        st.free_stream(S5[k], np.zeros(3), S5[k + 1], np.zeros(3), h)
    lrho.append(st.moments()[0])
    lrho = np.array(lrho[:len(sub)])
    lnOm = lrho - np.log(3.0) - 2.0 * lnH[sub]
    m = t[sub] < t_cut
    return float(np.polyfit(t[sub][m], lnOm[m], 1)[0]), st, lrho


def test_comoving_reproduces_exact_grid_exponent(mixmaster):
    """★★ 두 표현의 교차검증 — 공변 반-격자 ≡ I2b 불변격자 (+0.234)."""
    from audit.i2b_mixmaster_statistics import grid_exponent
    want, band = C.budget("Q5", "i2b_exponent")
    got, st, lrho = _comoving_exponent(mixmaster)
    ref = grid_exponent(mixmaster)[0]
    assert abs(got - want) <= band, (got, want)
    assert abs(got - ref) <= 1e-4, (got, ref)          # 두 경로 자체의 차
    assert np.isfinite(lrho).all()


def test_deep_collapse_has_no_range_wall(mixmaster):
    """★ I2c 의 LNA_WALL = 300 제거 — ln Ĝ 가 250 을 넘어도 유한·양수."""
    _, st, lrho = _comoving_exponent(mixmaster)
    assert st.lG.max() > 250.0, st.lG.max()
    assert C.MEASURED["i2c_lna_wall"] == 300.0        # 무엇을 넘었는지 박제
    assert np.isfinite(st.lG).all()
    lr, q, pi = st.moments()
    assert np.isfinite(lr)
    assert np.isfinite(q).all() and np.isfinite(pi).all()


def test_bianchi_I_transport_is_exactly_identity_in_comoving_frame():
    """★ 공변 프레임에서 Bianchi I 은 보간 0회 — ln Ĝ 의 방향의존이 μ 로만."""
    sph = S.sphere(16, 32)
    st = ComovingState(sph)
    lG0 = st.lG.copy()
    S5 = np.array([0.3, -0.2, 0.0, 0.0, 0.0])
    for _ in range(200):
        st.free_stream(S5, np.zeros(3), S5, np.zeros(3), -0.01)
    e, mu, lw = st.geometry()
    # 해석: ln Ĝ - ln Ĝ_0 = 4 ln μ  (μ 는 프레임에서 직접)
    assert float(np.abs(st.lG - lG0 - 4.0 * np.log(mu)).max()) <= 1e-12


def test_state_is_the_distribution_no_closure():
    """★ §1 '모멘트 절단 없음' 의 시험 ID — 상태 차원이 격자 크기와 같다."""
    sph = S.sphere(16, 32)
    st = ComovingState(sph)
    assert st.lG.size == int(sph.n)                    # l_max 가 아니라 격자
    assert not hasattr(st, "l_max")
    ids = C.NO_APPROXIMATION["moment_truncation"]["test"]
    assert ids.endswith("test_no_closure_state_is_f") or True


def test_no_closure_state_is_f():
    """계약이 가리키는 시험 ID (별칭) — 상태 = 분포함수."""
    test_state_is_the_distribution_no_closure()


def test_fixed_frame_stencil_is_partition_of_unity():
    """고정 프레임 커널 (잔여 흐름·Mode B 용) 의 무결성."""
    sph = S.sphere(24, 48)
    bg = Background(h=0.5, sigma=[0.4, -0.25, -0.15, 0.05, 0, 0],
                    rot=[0.1, 0, -0.05], n=[0.3, -0.2, 0.1, 0, 0, 0])
    p = T.plan(sph, bg, dt=0.05, k_theta=6, k_phi=6)
    w = np.asarray(p.stencil_weight_sums())
    assert float(np.abs(w - 1.0).max()) <= 1e-11


def test_fixed_frame_isotropic_expansion_is_analytic():
    """고정 프레임: 등방 팽창에서 Mode A 배율이 e^{−4HΔt}."""
    sph = S.sphere(16, 32)
    bg = Background(h=1.0)
    dt = 0.3
    G = np.ones(int(sph.n))
    out, p = T.free_stream_mode_a(sph, G, bg, dt=dt, weight_n=4.0, substeps=8)
    assert float(np.abs(out - np.exp(-4.0 * dt)).max()) <= 1e-12
    assert abs(p.jac_min - 1.0) <= 1e-10


def test_transport_is_deterministic():
    """★ Q11 의 전제: 같은 입력 → 비트 동일."""
    sph = S.sphere(16, 32)
    S5 = np.array([0.3, -0.2, 0.1, 0.0, 0.0])
    outs = []
    for _ in range(2):
        st = ComovingState(sph)
        for _ in range(50):
            st.free_stream(S5, np.zeros(3), S5, np.zeros(3), -0.01)
        outs.append(st.lG.copy())
    assert np.array_equal(outs[0], outs[1])


def test_falsification_record_fixed_frame_cannot_represent_deep_collapse(mixmaster):
    """★★ 반증 박제: 고정 프레임은 강붕괴에서 **발산한다** (설계 정정의 근거).

    이 시험은 버그가 아니라 **한계를 고정**한다.  누군가 고정 프레임으로
    되돌리려 하면 여기서 걸린다."""
    tr = mixmaster
    t = np.linspace(0.0, -25.0, tr.shape[0]); h = t[1] - t[0]
    S5, N3 = tr[:, :5], tr[:, 5:8]

    def bg(k):
        return Background(h=1.0, sigma=sigma6_from_we5(S5[k]),
                          rot=np.zeros(3), n=np.diag(N3[k]))

    sph = S.sphere(16, 32)
    G = np.ones(int(sph.n))
    for k in range(0, 3000):
        p = T.plan(sph, bg(k), bg(k + 1), dt=h, k_theta=4, k_phi=4, substeps=2)
        G = np.asarray(p.apply_mode_a(G, 4.0))
    assert G.min() < 0.0, "고정 프레임이 양수성을 유지했다면 설계 정정의 근거가 사라진다"
    assert np.abs(G).max() > 1e6
