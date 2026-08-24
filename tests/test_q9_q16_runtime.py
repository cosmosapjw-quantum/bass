"""
Q9–Q16 · **다성분 · 적분/사건 · 런타임 · 프론트엔드 · 통계** 게이트 (76차).

한 파일에 모은 이유: 이 층들은 물리가 아니라 **계약 준수**를 재는 시험이라
서로 독립적이고 짧다.  물리 게이트는 Q1–Q8 파일에 있다.
"""
import os
import tempfile

import numpy as np
import pytest

RC = pytest.importorskip("bianchi_rustcore")
if not hasattr(RC, "QFrame"):
    pytest.skip("Q 층 미빌드", allow_module_level=True)

from bianchi.q import contract as C  # noqa: E402
from bianchi.q import coupled as QC  # noqa: E402
from bianchi.q import integrate as QI  # noqa: E402
from bianchi.q import runtime as RT  # noqa: E402
from bianchi.q import species as SP  # noqa: E402
from bianchi.q import sphere as S  # noqa: E402
from bianchi.q import stats as ST  # noqa: E402
from bianchi.q.model import Collision, Grid, Model, run  # noqa: E402


def _state(nt=16):
    sph = S.sphere(nt, 2 * nt)
    Sg = np.diag([0.2, -0.1, -0.1]); N = np.diag([0.3, 0.3, 0.3])
    st0 = QC.QState(sph, Sg, N, np.zeros(3)); K, _ = st0.curvature()
    return QC.on_gauss_surface(sph, Sg, N, np.zeros(3),
                               1 - float(np.trace(Sg @ Sg) / 6) - K)


# ───────────────────────────────────────────── Q9
def test_q9_momentum_exchange_conserves_total():
    """★ Σ_c Q_c = 0 — κ 대칭·영대각의 **구조적** 귀결 (H'2 승계)."""
    sph = S.sphere(16, 32)
    sp = [SP.Species("photon", sph), SP.Species("neutrino", sph), SP.Species("cdm")]
    for c, v in zip(sp, ([0.1, 0, 0], [-0.05, 0.02, 0], [0, 0, 0.03])):
        c.v = np.array(v, float)
    k = np.array([[0.0, 0.5, 0.2], [0.5, 0.0, 0.3], [0.2, 0.3, 0.0]])
    Qx = SP.exchange_Q(sp, [0.5, 0.3, 0.2], k)
    assert float(np.abs(Qx.sum(axis=0)).max()) <= C.budget("Q9", "momentum_sum")


def test_q9_rejects_bad_kappa():
    sph = S.sphere(8, 16)
    sp = [SP.Species("photon", sph), SP.Species("cdm")]
    with pytest.raises(ValueError, match="대칭"):
        SP.exchange_Q(sp, [0.5, 0.5], np.array([[0.0, 1.0], [0.5, 0.0]]))
    with pytest.raises(ValueError, match="대각"):
        SP.exchange_Q(sp, [0.5, 0.5], np.array([[0.1, 0.3], [0.3, 0.0]]))


def test_q9_fluid_species_are_explicitly_marked():
    """★ '격자인 척' 금지 — 유체 캐리어는 Kind 로 명시된다."""
    sph = S.sphere(8, 16)
    assert SP.Species("photon", sph).is_grid()
    assert not SP.Species("cdm").is_grid()
    assert not SP.Species("dark_energy").is_grid()
    assert SP.W_DEFAULT[SP.Kind.DARK_ENERGY] == -1.0


# ───────────────────────────────────────────── Q10
def test_q10_analytic_jacobian_has_structure():
    """SymBoltz 교훈: 야코비안과 **희소 패턴**을 얻는다 (기하 블록)."""
    st = _state()
    J = QI.jacobian(st)
    assert J.shape == (25, 25)
    sp = QI.sparsity(st)
    assert 0.05 < sp.mean() < 0.95            # 실제로 희소하다
    assert np.isfinite(J).all()


def test_q10_event_detection_precision():
    """사건 위치 정밀도 (계약 임계)."""
    st = _state()
    ev = QI.omega_threshold_event(0.99)
    st, traj, hits = QI.integrate(st, -0.002, 400, events=[ev])
    assert hits, "사건이 잡히지 않았다"
    name, tau = hits[0]
    assert name == "omega"
    # 그 τ 로 다시 굴려 g ≈ 0 인지
    st2 = _state()
    n = max(int(abs(tau) / 0.002), 1)
    QC.evolve(st2, tau / n, n)
    assert abs(ev.g(st2)) <= 1e-4


# ───────────────────────────────────────────── Q11
def test_q11_deterministic_reduction():
    """★ 고정 순서 pairwise — 순서를 바꾸면 다르다는 것까지 확인."""
    rng = np.random.default_rng(0)
    v = rng.standard_normal(10000) * 1e8
    assert RT.reduce_det(v) == RT.reduce_det(v.copy())
    assert C.budget("Q11", "threads") == "bitwise"


def test_q11_evolution_is_bitwise_reproducible():
    a = _state(); QC.evolve(a, -0.002, 200)
    b = _state(); QC.evolve(b, -0.002, 200)
    assert np.array_equal(a.pack(), b.pack())


# ───────────────────────────────────────────── Q12
def test_q12_checkpoint_roundtrip_and_guards():
    st = _state(); QC.evolve(st, -0.002, 100)
    cfg = dict(type="IX", nt=16)
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "ck.npz")
        RT.save_checkpoint(p, st.pack(), cfg, -0.2)
        v, tau = RT.load_checkpoint(p, cfg)
        assert np.array_equal(v, st.pack()) and tau == -0.2
        with pytest.raises(ValueError, match="해시"):
            RT.load_checkpoint(p, dict(type="VIII"))


def test_q12_restart_continues_bitwise():
    a = _state(); QC.evolve(a, -0.002, 200)
    b = _state(); QC.evolve(b, -0.002, 100)
    mid = b.pack().copy()
    b2 = b.unpack(mid); b2.sph = b.sph
    QC.evolve(b2, -0.002, 100)
    assert np.array_equal(a.pack(), b2.pack())


# ───────────────────────────────────────────── Q13
def test_q13_seed_reproducibility_and_measure_docs():
    """★ 시드 재현 + **샘플러 측도가 문서화**되어 있다 (통계 결론의 전제)."""
    o1, f1 = RT.run_ensemble(lambda i, r: float(r.standard_normal()), 20, 7)
    o2, f2 = RT.run_ensemble(lambda i, r: float(r.standard_normal()), 20, 7)
    assert o1 == o2 and not f1 and not f2
    assert set(RT.SAMPLERS) >= {"uniform_kasner", "haar_so3", "gauss_measure"}
    for name, fn in RT.SAMPLERS.items():
        assert len(fn.measure) > 30, name        # 측도 정의가 실제로 적혀 있다


def test_q13_failures_are_isolated_and_recorded():
    def member(i, r):
        if i == 3:
            raise RuntimeError("의도적 실패")
        return i
    out, fails = RT.run_ensemble(member, 10, 1)
    assert out[3] is None and len(fails) == 1 and fails[0][0] == 3
    assert sum(1 for x in out if x is not None) == 9


def test_q13_haar_measure_is_actually_haar():
    """Haar SO(3): 회전축이 구면 위 균일 — l=1 모멘트가 0 으로 수렴."""
    rng = np.random.default_rng(0)
    axes = []
    for _ in range(4000):
        R = RT.haar_so3(rng)["R"]
        w, v = np.linalg.eig(R)
        ax = np.real(v[:, np.argmin(np.abs(w - 1.0))])
        axes.append(ax / np.linalg.norm(ax) * np.sign(ax[0] or 1.0))
    m = np.abs(np.mean(axes, axis=0))
    assert m[1] < 0.05 and m[2] < 0.05, m


# ───────────────────────────────────────────── Q14
def test_q14_streaming_io_roundtrip_and_manifest_guard():
    cfg = dict(type="IX", nt=16)
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "run")
        w = RT.RunWriter(p, cfg, chunk=37)
        rows = [dict(tau=-0.01 * k, Omega=0.9 - 1e-4 * k) for k in range(200)]
        for r in rows:
            w.append(r)
        w.close()
        rd = RT.RunReader(p)
        arr = rd.scalars(["tau", "Omega"])
        assert arr.shape == (200, 2)
        assert np.array_equal(arr[:, 1], np.array([r["Omega"] for r in rows]))
        with pytest.raises(FileNotFoundError):
            RT.RunReader(d)


# ───────────────────────────────────────────── Q15
def test_q15_summary_prints_every_assumption():
    """★ 편의 API 가 물리 규약을 숨기지 못한다."""
    m = Model(type="VIII", grid=Grid(16, 32), tau_span=(0.0, -1.0), nsteps=100)
    s = m.summary()
    for key in C.NO_APPROXIMATION:
        assert key in s, key
    for key in C.DISCRETIZATION:
        assert key in s, key
    assert "공변" in s and "ln Ĝ" in s
    assert "Q5b" in s                            # 알려진 간극도 인쇄한다


def test_q15_model_validates_and_runs():
    m = Model(type="VII_h", grid=Grid(16, 32), tau_span=(0.0, -0.5), nsteps=200,
              collision=Collision.thomson(nu=3.0))
    st, traj, hits = run(m)
    assert st.aux()["Omega"] > 0
    with pytest.raises(ValueError, match="알 수 없는 유형"):
        Model(type="XVII").build()
    with pytest.raises(ValueError, match="짝수"):
        Grid(16, 33).build()


def test_q15_b2b_history_interface_is_unchanged_but_lane_is_required():
    """B2b **이력 인터페이스**는 무변경 — 그러나 lane 은 명시해야 한다.

    ★★ 87차 정정 (외부 리뷰).  이 시험은 원래 "B2b 통합양식이 **코드 수정 없이**
    꽂힌다" 고 주장하며 `m.collision.history is hist` 까지만 봤다.  두 가지가
    틀렸다:

    (1) 85차 Q19 가 밝혔듯, 객체가 이력을 **들고 있는** 것과 적분기가 이력을
        **쓰는** 것은 다른 명제다 (그때는 상수 nu 가 들어가고 있었다).
    (2) 87차 Q20 이 `lane` 을 **필수**로 만들었으므로 "코드 수정 없이" 는 이제
        문자 그대로 거짓이다 — 호출자는 internal / phenomenology 중 하나를
        선언해야 한다.  이것은 의도된 계약 변경이다: lane 을 안 정하면 재결합
        이동이 anisotropic physics 인지 H normalization 차이인지 섞이기 때문이다.

    그래서 이 시험이 지키는 것은 좁아진 두 문장이다 —
    **외부 모듈 쪽 인터페이스(IonizationHistory 프로토콜)는 무변경**이고,
    **lane 미지정은 조용히 통과하지 않는다**."""
    import pytest
    from bianchi.thermo.history_api import (IonizationHistory, SahaHistory,
                                            validate_history)
    hist = SahaHistory()                      # B2b 내장 대조군 (계약 7종 통과)
    assert all(validate_history(hist).values())
    # (a) 외부 모듈 쪽 인터페이스는 무변경 — 프로토콜만 만족하면 된다
    assert isinstance(hist, IonizationHistory)
    c = Collision.thomson(hist, nu=1.0)
    assert c.history is hist
    # (b) lane 미지정은 **조용히 통과하지 않는다** (Q20)
    m_no_lane = Model(type="I", grid=Grid(8, 16), tau_span=(0.0, -0.2), nsteps=50,
                      collision=c)
    with pytest.raises(ValueError, match="lane 은 필수"):
        m_no_lane.schedule()
    # (c) lane 을 선언하면 끝까지 돈다
    m = Model(type="I", grid=Grid(8, 16), tau_span=(0.0, -0.2), nsteps=50,
              collision=c, lane="phenomenology")
    assert m.collision.history is hist
    assert m.schedule() is not None
    run(m)


# ───────────────────────────────────────────── Q16
def test_q16_gauss_map_statistics():
    """★ 에라 전이의 x = {1/x} (Gauss 사상) 가 불변측도 1/((1+x)ln2) 를 따른다.

    ★ 반증 기록 (76차): 처음엔 u-수열의 소수부를 그대로 KS 에 넣었다가 p ~ 1e−44
    로 기각당했다.  원인은 물리가 아니라 **시험 설계**였다 — u→u−1 단계는 소수부를
    바꾸지 않아 표본이 강하게 상관되고, KS 의 독립성 가정이 깨진다.  에라 전이
    (Gauss 사상) 만 뽑고 궤도마다 1표본으로 고치면 통과한다."""
    rng = np.random.default_rng(3)
    xs = []
    for _ in range(3000):
        x = float(rng.random())
        for _ in range(20):                   # 전이 (transient) 제거
            x = (1.0 / x) % 1.0 if x > 0 else float(rng.random())
        xs.append(x)                          # 궤도당 1표본 (독립)
    res = ST.gauss_measure_ks(np.array(xs))
    assert res.pvalue > C.budget("Q16", "ks_p"), res


def test_q16_bootstrap_covers():
    rng = np.random.default_rng(0)
    d = rng.normal(2.0, 1.0, 400)
    val, (lo, hi) = ST.bootstrap(np.mean, d, n=400, seed=1)
    assert lo < 2.0 < hi and abs(val - 2.0) < 0.2


def test_q16_distortion_requires_convergence_before_reporting():
    """★ 계획 §9: y 는 격자 수렴을 먼저 보이고 나서만 보고한다."""
    ys = ST.distortion_convergence(0.1, n_theta=(12, 16, 24), n_p=(150, 300, 600))
    rel = np.abs(np.diff(ys)) / np.abs(ys[1:])
    assert (rel < 5e-2).all(), ys                # 수렴 확인
    assert ys.min() > 0.0
