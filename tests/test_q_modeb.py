"""
Mode B **정식 결합** 게이트 (80차) — 완전 f 를 QState 에.

  · ★★ Mode A ≡ Mode B (인수분해 초기자료에서 Ω·Π 일치) — 축약 항등
        ln Ĝ_i = 4 lnμ_i + ln Jr_i 의 실측
  · ★ Bianchi I 에서 Mode B 자유흐름이 **정확히 항등** (Mode A 의 4 dlnμ 항은
        반경적분의 부산물이었다는 증명)
  · ★ 충돌이 반경 슬라이스마다 **같은 연산** (에너지-교환 정리)
  · ★★ Mode B 만 주는 것: **분광 관측량** (비섭동 y-왜곡) — Ĝ 는 1모멘트라 불가
  · Rust ln_ghat ≡ Python 참조
  · 결정성
"""
import numpy as np
import pytest

RC = pytest.importorskip("bianchi_rustcore")
if not hasattr(RC, "qe_evolve"):
    pytest.skip("Mode B 미빌드", allow_module_level=True)

from bianchi.q import comoving as CM  # noqa: E402
from bianchi.q import coupled as Q  # noqa: E402
from bianchi.q import fast as F  # noqa: E402
from bianchi.q import modeb as B  # noqa: E402
from bianchi.q import sphere as S  # noqa: E402

SG = np.diag([0.2, -0.1, -0.1])


def test_mode_b_reduces_to_mode_a_for_factorized_data():
    """★★ 축약 항등: 같은 물리를 두 표현이 같은 값으로 준다."""
    sph = S.sphere(16, 32)
    N = np.diag([0.3, -0.2, 0.1])
    b = B.planck_state(sph, n_p=64, Sigma=SG, N=N)
    a = Q.QState(sph, SG, N, np.zeros(3), lG=b.ln_ghat())
    _, ea, mua, lwa = a.geometry()
    ra, _, pa = CM.moments_log(lwa, a.lG, ea)
    rb, _, pb = b.moments()
    assert abs(ra - rb) <= 1e-12 * max(1.0, abs(ra))
    assert float(np.abs(pa - pb).max()) <= 1e-12
    # 진화 후에도
    F.evolve(a, -0.002, 300)
    b2 = B.planck_state(sph, n_p=64, Sigma=SG, N=N)
    B.evolve(b2, -0.002, 300)
    oa, ob = a.aux()["Omega"], B.diagnostics(b2)["Omega"]
    assert abs(oa - ob) / oa <= 1e-9, (oa, ob)


def test_rust_ln_ghat_matches_python_reference():
    """Rust `QState::ln_ghat` ≡ Python 참조 축약."""
    sph = S.sphere(12, 24)
    b = B.planck_state(sph, n_p=48, Sigma=SG, N=np.diag([0.3, 0.3, 0.3]))
    a = Q.QState(sph, SG, np.diag([0.3, 0.3, 0.3]), np.zeros(3), lG=b.ln_ghat())
    # Rust 진단이 같은 Ω 를 준다 ⇒ 내부 축약이 참조와 일치
    da = F.diagnostics(a)
    db = B.diagnostics(b)
    assert abs(da["Omega"] - db["Omega"]) <= 1e-12 * max(1.0, da["Omega"])
    assert abs(da["q"] - db["q"]) <= 1e-12


def test_mode_b_free_stream_is_exactly_identity_for_bianchi_I():
    """★ 공변 프레임에서 f 는 자유흐름 하에 **정확히 불변** (곡률 0)."""
    sph = S.sphere(16, 32)
    b = B.planck_state(sph, n_p=48, Sigma=SG, N=np.zeros((3, 3)))
    before = b.lnf.copy()
    B.evolve(b, -0.002, 400, nu=0.0)
    assert float(np.abs(b.lnf - before).max()) <= 1e-13
    # 그런데 Ω 는 움직인다 (기하가 μ 를 통해 나른다)
    assert abs(B.diagnostics(b)["Omega"]) > 0.0


def test_mode_b_collision_is_radial_slice_uniform():
    """★ 에너지-교환 정리의 Mode B 실측: 슬라이스 간 오프셋이 보존된다."""
    sph = S.sphere(12, 24)
    e, _ = S.nodes(sph)
    n_p = 6
    b = B.ModeBState(sph, n_p=n_p, lnq_min=-3.0, lnq_max=3.0, Sigma=SG)
    ang = 0.7 * e[:, 2]
    off = np.array([0.0, 1.3, -2.1, 0.5, 3.0, -0.4])
    b.lnf = (ang[:, None] + off[None, :]).ravel()
    B.evolve(b, -1e-9, 1, nu=1.7e9)
    F2 = b.lnf.reshape(-1, n_p)
    for j in range(1, n_p):
        d = F2[:, j] - F2[:, 0]
        # 81차: 충돌이 공통 물리격자로 두 번 시프트하므로 경계 확장 오차가 남는다
        # (M = I 라 δ = 0 이고 시프트 자체는 항등이지만, 꼬리 확장이 유한 정밀).
        assert float(np.abs(d - (off[j] - off[0])).max()) <= 1e-8, j


def test_mode_b_gives_spectral_observable_mode_a_cannot():
    """★★ Mode B 의 존재 이유: **비섭동 y-왜곡**.

    Mode A 는 에너지 1모멘트라 y 를 정의조차 못한다."""
    sph = S.sphere(24, 48)
    dT = 0.2
    c = B.planck_state(sph, n_p=300, lnq_min=-7.0, lnq_max=4.5,
                       T_of=lambda x: 1.0 + dT * x[2])
    B.evolve(c, -1e-9, 1, nu=5e10)                 # 완전 등방화
    y, Teff = B.y_parameter(c)
    expect = 0.5 * dT ** 2 / 3.0                   # ½⟨(ΔT/T)²⟩, ⟨cos²⟩=1/3
    assert y > 0
    assert abs(y / expect - 1.0) <= 0.10, (y, expect)
    assert 0.9 < Teff < 1.1
    # Mode A 상태에는 스펙트럼 축이 아예 없다
    a = Q.QState(sph, SG, np.zeros((3, 3)), np.zeros(3), lG=c.ln_ghat())
    assert a.lG.size == int(sph.n)
    assert c.lnf.size == int(sph.n) * 300


def test_mode_b_spectrum_accessor():
    sph = S.sphere(12, 24)
    b = B.planck_state(sph, n_p=128, lnq_min=-6.0, lnq_max=4.0)
    q, fb = b.q(), b.spectrum()
    ref = 1.0 / np.expm1(q)
    assert float(np.abs(fb - ref).max()) <= 1e-12   # 등방 초기자료


def test_mode_b_is_deterministic():
    sph = S.sphere(12, 24)
    outs = []
    for _ in range(2):
        b = B.planck_state(sph, n_p=48, Sigma=SG, N=np.diag([0.3, -0.2, 0.1]))
        B.evolve(b, -0.002, 150, nu=1.0)
        outs.append(b.pack().copy())
    assert np.array_equal(outs[0], outs[1])


def test_mode_b_residual_runs_for_curved_types():
    """곡률이 있으면 잔여 이류가 실제로 작동 (Q5b Mode B 경로)."""
    sph = S.sphere(12, 24)
    b = B.planck_state(sph, n_p=48, Sigma=SG, N=np.diag([0.0, 0.3, -0.3]),
                       A=np.array([0.2, 0.0, 0.0]))
    before = b.lnf.copy()
    B.evolve(b, -0.002, 200, nu=0.0)
    assert float(np.abs(b.lnf - before).max()) > 1e-8
    assert np.isfinite(b.lnf).all()


def test_frontend_selects_mode_b_and_prints_it():
    """★ Q15 계약: Model(Grid(n_p=...)) 이 Mode B 를 고르고 summary 가 인쇄한다."""
    from bianchi.q.model import Collision, Grid, Model, run
    m = Model(type="II", grid=Grid(12, 24, n_p=48), tau_span=(0.0, -0.3),
              nsteps=100, collision=Collision.thomson(nu=2.0))
    assert m.grid.mode() == "B"
    s = m.summary()
    assert "Mode B" in s and "분광" in s
    st, traj, hits = run(m)
    assert st.lnf.size == 12 * 24 * 48
    assert np.isfinite(st.lnf).all()
    a = Model(type="II", grid=Grid(12, 24), tau_span=(0.0, -0.3), nsteps=100)
    assert a.grid.mode() == "A"
    sa, _, _ = run(a)
    assert sa.lG.size == 12 * 24
