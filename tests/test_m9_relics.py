"""PR-37 열적 잔존물 동결 테스트."""
import numpy as np
import pytest

from bianchi.thermo import relics as rel


def test_wimp_miracle():
    """σv ~ 1 pb -> Ω h² ~ 0.1 (WIMP miracle), x_f ~ 20-25."""
    r = rel.freeze_out(1.0 * rel.GEV2_PER_PB, m_GeV=100.0, g_star=90.0)
    assert 0.05 < r["Omega_h2"] < 0.15
    assert 18 < r["x_f"] < 28


def test_inverse_cross_section_scaling():
    """Ω h² ∝ 1/⟨σv⟩ (더 큰 소멸단면적 -> 더 적은 잔존)."""
    o1 = rel.freeze_out(1.0 * rel.GEV2_PER_PB, 100.0)["Omega_h2"]
    o3 = rel.freeze_out(3.0 * rel.GEV2_PER_PB, 100.0)["Omega_h2"]
    assert o3 < o1
    assert abs(o1 / o3 / 3.0 - 1) < 0.15          # 대략 3배 (x_f 보정 내)


def test_anisotropic_expansion_increases_relic():
    """★ Bianchi 고유: 이방 팽창(shear boost) -> 더 이른 동결 -> 잔존 증가.
    Σ→0 (boost=1) 에서 표준 FLRW 값 복원."""
    o_flrw = rel.freeze_out(1.0 * rel.GEV2_PER_PB, 100.0, shear_boost=1.0)["Omega_h2"]
    o_aniso = rel.freeze_out(1.0 * rel.GEV2_PER_PB, 100.0, shear_boost=1.5)["Omega_h2"]
    assert o_aniso > o_flrw
    # boost=1 이 FLRW 기준
    assert 0.05 < o_flrw < 0.15


def test_freeze_out_x_earlier_with_boost():
    """shear boost -> 더 빠른 팽창 -> 더 이른 동결 (작은 x_f = 높은 T)."""
    xf1 = rel.freeze_out_x(1.0 * rel.GEV2_PER_PB, 100.0, shear_boost=1.0)
    xf2 = rel.freeze_out_x(1.0 * rel.GEV2_PER_PB, 100.0, shear_boost=2.0)
    assert xf2 < xf1


def test_standard_wimp_helper():
    """standard_wimp_omega 헬퍼가 pb 입력으로 Ω h² ~ 0.1."""
    o = rel.standard_wimp_omega(sigma_v_pb=1.0, m_GeV=100.0)
    assert 0.05 < o < 0.15


# ══════════════════════════════ v3.0 (A2) 완전 Boltzmann 동결
def test_boltzmann_matches_analytic():
    """완전 Boltzmann ODE 가 해석식과 일치 (WIMP miracle 재현)."""
    sv = 1.0 * rel.GEV2_PER_PB
    b = rel.freeze_out_boltzmann(sv)
    a = rel.freeze_out(sv)
    assert b["success"]
    assert abs(b["Omega_h2"] - a["Omega_h2"]) / a["Omega_h2"] < 0.05
    assert 0.05 < b["Omega_h2"] < 0.15          # WIMP miracle: ~0.1 (1 pb)


def test_boltzmann_radau_bdf_agree():
    """Radau 와 BDF 가 같은 답 (적분기 무관)."""
    sv = 1.0 * rel.GEV2_PER_PB
    r = rel.freeze_out_boltzmann(sv, method="Radau")
    b = rel.freeze_out_boltzmann(sv, method="BDF")
    assert abs(r["Omega_h2"] - b["Omega_h2"]) / r["Omega_h2"] < 1e-4


def test_lsoda_fails_stiff_radau_succeeds():
    """A2 근거 박제: 같은 문제에서 LSODA 는 실패하고 Radau 는 성공한다.

    이전 판이 해석식으로 후퇴한 이유가 '강성이라 불가능'이 아니라
    **적분기 선택 실수**였음을 시험으로 고정한다.
    """
    d = rel.lsoda_fails_on_stiff_freezeout(1.0 * rel.GEV2_PER_PB)
    assert not d["lsoda_ok"], "LSODA 가 성공하면 이 전제를 재검토할 것"
    assert d["radau_ok"]


def test_boltzmann_inverse_cross_section_scaling():
    """Ω h² ∝ 1/⟨σv⟩ (선두차수)."""
    import numpy as np
    vals = {}
    for pb in (0.1, 1.0, 10.0):
        vals[pb] = rel.freeze_out_boltzmann(pb * rel.GEV2_PER_PB)["Omega_h2"]
    # Ωh²·⟨σv⟩ 가 로그 보정 수준(±25%) 내에서 일정
    prods = [vals[pb] * pb for pb in vals]
    assert max(prods) / min(prods) < 1.3, prods
    assert vals[0.1] > vals[1.0] > vals[10.0]


def test_boltzmann_shear_boost_increases_relic():
    """이방 팽창(boost>1) → 더 이른 동결 → 잔존 증가 (Bianchi 고유 효과)."""
    sv = 1.0 * rel.GEV2_PER_PB
    base = rel.freeze_out_boltzmann(sv, shear_boost=1.0)["Omega_h2"]
    boosted = rel.freeze_out_boltzmann(sv, shear_boost=2.0)["Omega_h2"]
    assert boosted > base


# ══════════════════════════════ v3.0 (B3) 자기일관 g_* + 이방 스캔
def test_selfconsistent_gstar_converges():
    """x_f ↔ g_*(T_f) 반복이 수렴하고, 하드코딩 90 과 다른 값을 준다."""
    r = rel.freeze_out_selfconsistent(1.0 * rel.GEV2_PER_PB)
    assert r["converged"], r
    assert r["n_iter_used"] < 15
    # 100 GeV WIMP → T_f ≈ 4.5 GeV, g_*(4.5 GeV) ≈ 85 (구표라면 106.75 라 우겼을 구간)
    assert 3.0 < r["T_f_GeV"] < 6.0
    assert 80.0 < r["g_star_eff"] < 90.0
    assert abs(r["g_star_eff"] - 90.0) > 1.0            # 하드코딩과 실제로 다름


def test_selfconsistent_still_wimp_miracle():
    """자기일관 보정 후에도 WIMP miracle 범위 유지."""
    r = rel.freeze_out_selfconsistent(1.0 * rel.GEV2_PER_PB)
    assert 0.05 < r["Omega_h2"] < 0.15


def test_anisotropy_scan_monotone():
    """이방 boost 증가 → 잔존량 단조 증가 (Bianchi 고유 효과)."""
    s = rel.anisotropy_scan(1.0 * rel.GEV2_PER_PB, [1.0, 1.25, 1.5, 2.0])
    om = s["Omega_h2"]
    assert all(om[i] < om[i + 1] for i in range(len(om) - 1)), om
    assert s["boosts"].shape == om.shape
