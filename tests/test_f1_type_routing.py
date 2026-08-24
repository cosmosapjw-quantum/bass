"""
F1 · **11개 Bianchi 유형(+III 별칭)의 명시 라우팅** — 분류→차트→적분→서명 왕복 게이트.

측정 (이 증분):
  · 12개 이름 전부 왕복 통과 — class_a(6) / class_b(κ=0,−1,±4)(5) / exceptional(1),
    적분 2.0τ (Rust BDF) 내내 서명 보존.
  · ★ 유형 V 의 함정 **실측**: {N₊=0, Δ≠0} 이면 N₊′ = (q+2Σ₊)N₊ + 6Δ 의 6Δ 항이
    N₊ 를 재생성한다 (0 → 1.6e−1 in 2τ) — V 가 IV 로 표류.  진화의 불변 부분공간은
    {N₊=Δ=0} (그 위에서 정확히 0, 곱셈 구조).
  · ★ 반증 기록 (scientific-diff-reviewer, 53차): 자유 지정 Δ 템플릿은 Codazzi 를
    O(10⁻⁴⁻⁵) 로 이탈했었다 (V: C=−3.6e−5, VI_h: +4.4e−4).  V 는 Codazzi 가
    Σ₊=0 **까지** 강제 (C = −Δ²−Σ₊²Ã).  수정: type_V_state / on_codazzi_surface
    로 구속면 위 생성, |C| ≤ 1e−12 게이트.  또 tilted κ 는 Rust 가 무시하는
    no-op 인자였고 (메타데이터로 강등), tilted 서명의 y[2]/y[5] 는 Σ₁₂/N 오독
    (미구현으로 봉인).
  · ★ 중복조사 기록: 처음 `bianchi/types.py` 를 새로 쓰려다 GateGuard 훅의
    중복조사에서 `bianchi/algebra.py` 의 기존 분류기(PR-04)가 걸렸다 — routing 은
    algebra 를 조합만 한다.  도구 규율(v5.1 §11.6)이 실제로 중복을 막은 사례.
"""
import numpy as np
import pytest

RC = pytest.importorskip("bianchi_rustcore")

from bianchi import algebra as AL  # noqa: E402
from bianchi import routing as R  # noqa: E402


@pytest.mark.parametrize("name", R.ALL_NAMES)
def test_roundtrip_preserves_the_type(name):
    """★★ 분류 → 라우팅 → Rust 적분(2τ) → 서명이 전 구간 그 유형이다."""
    r = R.roundtrip(name, t_end=2.0)
    assert r["ok"], name
    assert r["classified"] == name
    assert set(r["signatures"]) == {name}, (name, set(r["signatures"]))


@pytest.mark.parametrize("name", ["V", "IV", "III", "VI_h", "VII_h"])
def test_class_b_templates_sit_on_the_codazzi_surface(name):
    """★★ 리뷰 MAJOR 1 의 게이트: 템플릿 |C| ≤ 1e−12 (자유 Δ 는 O(1e−4) 였다)."""
    y, r = R.ic_template(AL.classify(*AL.CANONICAL[name]))
    om, con = R._aux_of("class_b", y, 1.3, r["params"]["kappa"])
    assert om > 0.0
    assert abs(con) <= R.CODAZZI_TOL, (name, con)
    if name == "V":
        assert y[0] == 0.0 and y[2] == 0.0 and y[4] == 0.0   # Σ₊=Δ=N₊=0 강제


def test_type_v_needs_the_full_invariant_subspace():
    """★★ 함정 실측 — Δ≠0 이면 6Δ 항이 N₊ 를 재생성해 V → IV 로 표류한다."""
    ts = np.linspace(0.0, 2.0, 5)
    bad = np.array([0.06, 0.07, 0.5e-2, 1e-2, 0.0])          # N₊=0, Δ≠0
    ys, ok = RC.integrate_background("class_b", bad, ts, 1.3, 0.0)
    assert ok
    assert abs(ys[-1][4]) > 0.1                              # N₊ 재생성 (실측 0.16)
    assert R.signature_of_state("class_b", ys[-1], 0.0) == "IV"
    good = np.array([0.06, 0.07, 0.0, 1e-2, 0.0])            # 진화 불변 부분공간
    ys2, _ = RC.integrate_background("class_b", good, ts, 1.3, 0.0)
    assert np.abs(ys2[:, 4]).max() == 0.0                    # 정확히 0
    assert np.abs(ys2[:, 2]).max() == 0.0


def test_exceptional_kappa_is_refused_by_class_b_routing():
    """★ κ=−9 축퇴 가드 — class_b 로의 침묵 라우팅 금지."""
    fake = AL.BianchiType("VI_h", "B", -9.0, False, ((1, -1), 1))
    with pytest.raises(ValueError, match="축퇴"):
        R.chart_for(fake)
    with pytest.raises(ValueError, match="exceptional"):
        R.signature_of_state("class_b", np.zeros(5), kappa=-9.0)


def test_class_b_signature_guards_its_domain():
    """★ 리뷰 MAJOR 4: Ã≈0 은 class A 경계 — 'IV' 로 이름 붙이면 오류다."""
    on_boundary = np.array([0.06, 0.03, 0.0, 0.0, 0.1])      # Ã = 0
    with pytest.raises(ValueError, match="class A 경계"):
        R.signature_of_state("class_b", on_boundary, kappa=0.0)
    bad_ntilde = np.array([0.0, 0.03, 0.0, 1e-2, 0.0])       # Ñ = −κÃ/3 < 0
    with pytest.raises(ValueError, match="정의역"):
        R.signature_of_state("class_b", bad_ntilde, kappa=3.0)


def test_tilted_signature_is_sealed_not_wrong():
    """★ 리뷰 MAJOR 3: 11-상태의 y[2]/y[5] 는 Σ₁₂/N — class_b 오독 대신 봉인."""
    with pytest.raises(NotImplementedError, match="Σ₁₂/N"):
        R.signature_of_state("class_b_tilted", np.zeros(11), kappa=4.0)


def test_class_a_tilt_routing_opened_by_f3():
    """★ (53차: NotImplementedError("F3") 예약 → 55차 납품으로 해제 — 이력 보존.)
    ★ 리뷰 MAJOR 2: tilted κ 는 Rust ClassBTilted 가 무시하는 no-op 이었다 —
      params 에서 빼고 서명용 메타데이터로만 남긴다 (h 는 상태 λ 에 산다)."""
    r = R.chart_for("IX", tilt=True)                         # F3: 예약 해제
    assert r["chart"] == "class_a_tilted" and r["params"] == {}
    bt = AL.classify(*AL.CANONICAL["VII_h"])                 # κ = n₂n₃/A² = 4
    r = R.chart_for(bt, tilt=True)                           # class B tilt 는 열려 있다
    assert r["chart"] == "class_b_tilted"
    assert r["params"] == {}                                 # Rust 로 가는 κ 없음
    assert r["kappa_signature"] == 4.0


def test_ix_offers_the_recollapse_alternative():
    assert R.chart_for("IX")["alt"] == "type_ix_d"
    y = np.array([0.6, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0])
    assert R.signature_of_state("type_ix_d", y) == "IX"


def test_classification_rejects_jacobi_violation():
    """★ algebra 의 Jacobi 가드가 라우팅 앞단에서 살아 있다 (D2b 함정 재사용)."""
    with pytest.raises(ValueError, match="Jacobi"):
        AL.classify(np.array([1.0, 1.0, 1.0]), np.array([1.0, 0.0, 0.0]))


def test_templates_are_physical_for_all_types():
    """★ 모든 템플릿이 유한 + Ω > 0 (ic_template 내부 검사) — 왕복 게이트의 전제."""
    for name in R.ALL_NAMES:
        y, _ = R.ic_template(AL.classify(*AL.CANONICAL[name]))
        assert np.isfinite(y).all(), name
