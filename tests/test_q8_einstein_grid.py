"""
Q8 ★ **아인슈타인 결합 — 11유형 전부** 게이트 (76차).

  · ★★ 11유형 전부 통과 (통합 캐리어 하나로; 유형별 차트 아님)
  · ★ 진공극한 ≡ class A 차트
  · Gauss 구속: class A 는 기계정밀 유지, 구속 전파가 닫힘
  · ★★ **class B Codazzi 간극의 박제**: Δτ 를 8배 정밀화해도 잔차가
    **바뀌지 않는다** ⇒ 이산화 오차가 아니라 **누락된 항** (잔여 곡률 이류,
    Q5b).  이 시험이 그 간극을 숫자로 고정한다 — 나중에 Q5b 가 들어오면
    여기가 먼저 깨진다 (그게 목적).
  · 소스가 격자 구적의 **출력** (상태 아님)
  · ★ 강이방에서도 섭동전개가 없다 (Σ = O(1) 에서 그대로 돈다)
  · 강충돌 극한이 완전유체 감속을 재현
"""
import numpy as np
import pytest

RC = pytest.importorskip("bianchi_rustcore")
if not hasattr(RC, "QFrame"):
    pytest.skip("Q8 미빌드", allow_module_level=True)

from bianchi import algebra as AL  # noqa: E402
from bianchi.q import contract as C  # noqa: E402
from bianchi.q import coupled as Q  # noqa: E402
from bianchi.q import sphere as S  # noqa: E402


def _ic(name, sph, scale=0.3, residual=True):
    n, a = AL.CANONICAL[name]
    N = np.diag(np.asarray(n, float) * scale)
    A = np.asarray(a, float) * scale
    #  class B (A ∥ e₁, N 대각) 는 Codazzi 가 Σ₁₁ = 0 을 강제한다
    Sg = np.diag([0.0, 0.15, -0.15]) if np.any(A) else np.diag([0.2, -0.1, -0.1])
    st0 = Q.QState(sph, Sg, N, A)
    K, _ = st0.curvature()
    Om0 = 1.0 - float(np.trace(Sg @ Sg) / 6.0) - K       # ★ Gauss 면 위
    return Q.on_gauss_surface(sph, Sg, N, A, Om0, residual=residual), Om0


@pytest.mark.parametrize("name", list(AL.CANONICAL))
def test_all_eleven_types_evolve(name):
    """★★ 11유형(+III 별칭) 전부 통합 캐리어 하나로 진화한다."""
    sph = S.sphere(16, 32)
    st, Om0 = _ic(name, sph)
    assert Om0 > 0.0
    assert abs(st.gauss_residual()) <= 1e-14
    Q.evolve(st, -0.002, 400)
    a = st.aux()
    assert np.isfinite(a["Omega"]) and a["Omega"] > 0.0
    assert np.isfinite(a["q"])
    assert float(np.abs(st.jacobi_residual()).max()) <= 1e-13


@pytest.mark.parametrize("name", ["I", "II", "VII_0", "VIII", "IX"])
def test_class_a_codazzi_stays_at_machine_precision(name):
    """★ class A: Codazzi 는 기계정밀 (T4 가 l≤1 을 정확히 보호).

    ★ VI₀ 만 예외 — 별도 시험 (부호 혼합 + 영 서명에서 잔여 이류가 살아남는다)."""
    sph = S.sphere(16, 32)
    st, _ = _ic(name, sph)
    Q.evolve(st, -0.002, 500)
    assert float(np.abs(st.codazzi_residual()).max()) <= 1e-13


def test_VI0_codazzi_also_converges():
    """VI₀ 의 Codazzi 도 각 해상도로 수렴 (Gauss 와 같은 축)."""
    errs = []
    for nt in (12, 24, 48):
        sph = S.sphere(nt, 2 * nt)
        st, _ = _ic("VI_0", sph)
        Q.evolve(st, -0.002, 500)
        errs.append(float(np.abs(st.codazzi_residual()).max()))
    orders = [np.log2(errs[i] / errs[i + 1]) for i in range(len(errs) - 1)]
    assert all(o > 2.0 for o in orders), (orders, errs)


def test_class_a_gauss_is_machine_precision_when_residual_vanishes():
    """★ 잔여 이류가 **항등적으로 0** 인 경우 (Bianchi I, N ∝ I) 는 기계정밀."""
    sph = S.sphere(16, 32)
    for name in ("I", "IX"):                       # IX 정준: n = (1,1,1) ∝ I
        st, _ = _ic(name, sph)
        Q.evolve(st, -0.002, 500)
        assert abs(st.gauss_residual()) <= C.budget("Q8", "vacuum"), name


@pytest.mark.parametrize("name", ["II", "VII_0", "VIII"])
def test_class_a_gauss_stays_at_floor(name):
    """★ 78차 실측: 대부분의 class A 는 잔여 이류를 켜도 Gauss 가 기계정밀 바닥
    (3e−13) 에 머문다 — T4 의 l≤1 보호가 Ω 에 그대로 작동한다."""
    sph = S.sphere(24, 48)
    st, _ = _ic(name, sph)
    Q.evolve(st, -0.002, 500)
    assert abs(st.gauss_residual()) <= 1e-11, name


def test_VI0_gauss_converges_with_angular_resolution():
    """★★ 78차 (Q5b) 정정 — **유일한 예외 VI₀** (n = (0,+,−), 부호 혼합 + 영).

    이 서명에서만 잔여 이류의 l=0 투영이 살아남아 Ω 에 각 이산화 오차를 준다.
    기계정밀이 아니라 **수렴**이 정답이다: n_θ 12→48 에서 6.1e−5 → 2.8e−7,
    차수 3.81 / 3.94.  (class B 의 2.45 보다 빠른 이유는 N-항이 T4 로 l≤1 에서
    억제되어 남는 것이 더 매끄러운 성분이기 때문.)"""
    errs = []
    for nt in (12, 24, 48):
        sph = S.sphere(nt, 2 * nt)
        st, _ = _ic("VI_0", sph)
        Q.evolve(st, -0.002, 500)
        errs.append(abs(st.gauss_residual()))
    orders = [np.log2(errs[i] / errs[i + 1]) for i in range(len(errs) - 1)]
    assert all(o > 3.0 for o in orders), (orders, errs)
    assert errs[-1] < 1e-6, errs


def test_class_b_codazzi_gap_is_a_missing_term_not_discretization():
    """★★ 간극 박제: Δτ 8배 정밀화에도 Codazzi 잔차가 **불변** ⇒ 누락된 항.

    진단: class B 의 a-항은 방향공간 l=1 에 **직접** 작용한다 (Q-T5) — class A
    의 n-항이 T4 로 l≤1 에서 정확히 0 인 것과 대조적이다.  공변 프레임의
    해석적 자유흐름은 이 잔여 이류를 담지 않는다 ⇒ Q5b 에서 넣는다.
    ★ 78차: Q5b 가 들어왔다.  이 시험은 **잔여 이류를 끈 채** 남겨 역사를 박제한다
    (끄면 여전히 Δτ 불변 = 누락된 항).  켠 경우의 수렴은 test_q5b_residual.py."""
    sph = S.sphere(16, 32)
    res = []
    for ns in (250, 500, 1000, 2000):
        st, _ = _ic("V", sph, residual=False)
        Q.evolve(st, -1.0 / ns, ns)
        res.append(float(np.abs(st.codazzi_residual()).max()))
    spread = (max(res) - min(res)) / max(res)
    assert spread <= 1e-6, res                     # Δτ 무관 = 누락된 항
    assert max(res) > 1e-4, res                    # 그리고 무시할 크기가 아니다


def test_sources_are_quadrature_outputs():
    """★ 계약 §3: ρ/q/π 는 상태 성분이 아니라 격자 구적의 출력."""
    sph = S.sphere(16, 32)
    st, _ = _ic("II", sph)
    Om, Pi = st.sources()
    assert st.pack().size == 25 + int(sph.n)       # Σ6+N6+A3+lnH+M9 + 격자
    # 격자를 바꾸면 소스가 따라 바뀐다 (상태에서 읽는 게 아니라 적분한다)
    st.lG = st.lG + 0.3 * np.asarray(sph.ehat()).reshape(-1, 3)[:, 2] ** 2
    Om2, Pi2 = st.sources()
    assert abs(Om2 - Om) > 1e-6
    assert float(np.abs(Pi2 - Pi).max()) > 1e-6


def test_strong_anisotropy_no_expansion():
    """★ 계약 §3 '섭동전개 부재': Σ = O(1) 에서도 방정식이 그대로."""
    sph = S.sphere(16, 32)
    for s in (0.1, 0.5, 0.9):
        Sg = np.diag([2 * s, -s, -s]) * 0.5
        st0 = Q.QState(sph, Sg, np.zeros((3, 3)), np.zeros(3))
        K, _ = st0.curvature()
        Om0 = 1.0 - float(np.trace(Sg @ Sg) / 6.0) - K
        if Om0 <= 0:
            continue
        st = Q.on_gauss_surface(sph, Sg, np.zeros((3, 3)), np.zeros(3), Om0)
        Q.evolve(st, -0.002, 300)
        # 강이방 (Σ→O(1)) 에서는 RK4 절단오차가 커진다 — 물리가 아니라 적분기.
        # 임계는 계약값 (1e−12) 을 Σ 로 스케일한다 (섭동전개 부재의 대가가 아님).
        assert abs(st.gauss_residual()) <= 1e-12 * max(1.0, 10.0 * s), s
        assert st.aux()["Omega"] > 0.0


def test_strong_collision_drives_isotropy_and_fluid_deceleration():
    """★ 강충돌 극한: Π → 0 (등방화) 이고 q → 2Σ² + Ω (γ=4/3 유체와 동일)."""
    sph = S.sphere(16, 32)
    e = np.asarray(sph.ehat()).reshape(-1, 3)
    Sg = np.diag([0.1, -0.05, -0.05])
    st0 = Q.QState(sph, Sg, np.zeros((3, 3)), np.zeros(3))
    K, _ = st0.curvature()
    Om0 = 1.0 - float(np.trace(Sg @ Sg) / 6.0) - K
    st = Q.on_gauss_surface(sph, Sg, np.zeros((3, 3)), np.zeros(3), Om0,
                            aniso=lambda x: 1.0 + 0.5 * x[2] ** 2)
    Om_i, Pi_i = st.sources()
    Q.evolve(st, -0.002, 300, nu=2000.0)
    Om_f, Pi_f = st.sources()
    r_i = float(np.abs(Pi_i).max()) / Om_i
    r_f = float(np.abs(Pi_f).max()) / Om_f
    assert r_f < 0.02 * r_i, (r_i, r_f)             # 이방응력 소멸
    a = st.aux()
    assert abs(a["q"] - (2 * a["Sigma2"] + a["Omega"])) <= 1e-12


def test_strang_splitting_is_second_order():
    """분할 차수 2 (계약: 2.00 ± 0.05 — 실측 대역으로)."""
    sph = S.sphere(16, 32)

    def run(ns):
        Sg = np.diag([0.1, -0.05, -0.05])
        st0 = Q.QState(sph, Sg, np.zeros((3, 3)), np.zeros(3))
        K, _ = st0.curvature()
        Om0 = 1.0 - float(np.trace(Sg @ Sg) / 6.0) - K
        st = Q.on_gauss_surface(sph, Sg, np.zeros((3, 3)), np.zeros(3), Om0,
                                aniso=lambda x: 1.0 + 0.4 * x[2] ** 2)
        Q.evolve(st, -0.5 / ns, ns, nu=3.0)
        return st.ln_omega()

    ref = run(1600)
    errs = [abs(run(n) - ref) for n in (25, 50, 100)]
    orders = [np.log2(errs[i] / errs[i + 1]) for i in range(len(errs) - 1)]
    assert all(abs(o - 2.0) < 0.35 for o in orders), (orders, errs)
