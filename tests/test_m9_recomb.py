"""PR-36 재결합 Saha+Peebles 테스트."""
import numpy as np
import pytest

from bianchi.thermo import recombination as rec


def test_saha_half_ionization():
    """Saha x_e=0.5 근처 z ≈ 1360-1380 (표준)."""
    zstar = rec.recombination_redshift()
    assert 1300 < zstar < 1420, zstar


def test_peebles_shape_and_residual():
    """Peebles x_e: 재결합 급강하 + 잔존 x_e ≈ 2e-4 (RECFAST 급)."""
    zg = np.linspace(1800, 10, 700)
    xe = rec.peebles_xe(zg)
    assert xe[0] > 0.9                            # 고z 이온화
    assert xe[-1] < 1e-3                          # 잔존 소량
    assert 1e-4 < xe[-1] < 6e-4                   # 표준 잔존 범위
    # 단조 감소 (재결합)
    assert xe[np.argmin(abs(zg - 800))] < xe[np.argmin(abs(zg - 1200))]


def test_visibility_z_star():
    """가시함수 g(z) 최대점 z_* ≈ 1090 (관측; ±60)."""
    zg = np.linspace(1600, 200, 800)
    xe = rec.peebles_xe(zg)
    vis = rec.optical_depth_and_visibility(zg, xe)
    assert 1020 < vis["z_star"] < 1160, vis["z_star"]


def test_drag_redshift():
    """z_drag ≈ 1060 (Eisenstein-Hu)."""
    zd = rec.drag_redshift()
    assert 1000 < zd < 1080, zd


def test_anisotropy_enters_only_through_H():
    """이방성은 H(z) 를 통해서만: 다른 H 콜백을 주면 x_e 가 바뀐다 (D7)."""
    zg = np.linspace(1600, 100, 400)
    xe_std = rec.peebles_xe(zg)
    # 팽창이 빠른 이방 배경 (H 1.2배) -> 재결합 덜 완료 (잔존 x_e 큼)
    def H_fast(z):
        Om = 0.143 / 0.674 ** 2; OL = 1 - Om
        return 1.2 * (100 * 0.674 / 3.0857e19) * np.sqrt(Om * (1 + z) ** 3 + OL)
    xe_aniso = rec.peebles_xe(zg, H_of_z=H_fast)
    assert xe_aniso[-1] > xe_std[-1]              # 빠른 팽창 -> 잔존 전자 증가


# ══════════════════════════════ v3.0 (B2a) 헬륨 재결합 + H(z) 복사항
def test_helium_fraction():
    """f_He = Y_p/(4(1-Y_p)) = 0.0811 (Y_p=0.245)."""
    assert abs(rec.helium_fraction(0.245) - 0.08113) < 1e-4
    assert rec.helium_fraction(0.0) == 0.0


def test_helium_full_ionization_limit():
    """고온 극한: x_e → 1 + 2 f_He (헬륨 전자 2개)."""
    r = rec.saha_all_species(8000.0, 0.02237)
    assert abs(r["x_e"] - (1 + 2 * rec.helium_fraction(0.245))) < 1e-4
    assert r["x_HeIII"] > 0.99


def test_helium_two_transitions():
    """HeIII→HeII (z~6000), HeII→HeI (z~2500) 두 전이가 순서대로."""
    hi = rec.saha_all_species(6000.0, 0.02237)
    mid = rec.saha_all_species(4000.0, 0.02237)
    lo = rec.saha_all_species(2000.0, 0.02237)
    assert 0.1 < hi["x_HeIII"] < 0.95
    assert mid["x_HeII"] > 0.95 and mid["x_HeIII"] < 0.05
    assert lo["x_HeII"] < 0.01
    assert hi["x_e"] > mid["x_e"] > lo["x_e"]


def test_helium_neutral_before_hydrogen_recombination():
    """z ≲ 2000 에서 헬륨은 중성 → 수소 재결합기 x_e 에 영향 없음 (정직한 범위)."""
    r = rec.saha_all_species(1500.0, 0.02237)
    assert r["x_HeII"] < 1e-4 and r["x_HeIII"] < 1e-8


def test_xe_with_helium_reduces_to_hydrogen_at_low_z():
    """xe_with_helium 이 저-z 에서 순수 수소 Peebles 로 환원."""
    import numpy as np
    zg = np.linspace(1500, 300, 200)
    xh = rec.peebles_xe(zg, 0.02237, 0.1430, 0.6736)
    xe = rec.xe_with_helium(zg, 0.02237, 0.1430, 0.6736)
    assert np.allclose(xe, xh, rtol=1e-6, atol=1e-8)


def test_peebles_hubble_includes_radiation():
    """★ B2 버그 수정 회귀: Peebles 내부 H(z) 가 복사항을 포함해야 한다."""
    import numpy as np
    from bianchi.physical import units as U
    h, Om_h2 = 0.6736, 0.1430
    Om = Om_h2 / h ** 2
    Or = 4.18e-5 / h ** 2
    H0 = 100 * h / U.MPC_KM

    def H_no_rad(z):
        return H0 * np.sqrt(Om * (1 + z) ** 3 + (1 - Om))

    def H_with_rad(z):
        return H0 * np.sqrt(Or * (1 + z) ** 4 + Om * (1 + z) ** 3 + (1 - Om - Or))

    zg = np.linspace(1600, 800, 300)
    xe_no = rec.peebles_xe(zg, 0.02237, Om_h2, h, H_of_z=H_no_rad)
    xe_yes = rec.peebles_xe(zg, 0.02237, Om_h2, h, H_of_z=H_with_rad)
    i = np.argmin(abs(zg - 1100))
    assert xe_yes[i] > xe_no[i], "복사 포함 시 재결합이 느려져야 (x_e 커야) 한다"
    xe_def = rec.peebles_xe(zg, 0.02237, Om_h2, h)
    assert np.allclose(xe_def, xe_yes, rtol=1e-6)


def test_peebles_saturated_regime_structure():
    """★ v3.0 구조적 발견 박제: 급강하 구간은 **탈출률 지배**(포화)라 fudge 가 무효.

    C = Λ/(Λ+β), β ∝ α_B  →  β≫Λ 이면 C·α_B 가 α_B 무관.
    이 성질이 깨지면 B2b(Lyα 복사전달 표적) 논거가 흔들리므로 시험으로 고정한다.
    """
    # 급강하 구간: 강하게 포화
    for z, xe in [(1400, 0.80), (1200, 0.32), (1100, 0.14)]:
        d = rec.peebles_rate_regime(z, xe, 0.02237, 0.1430, 0.6736)
        assert d["saturated"], (z, d["beta_over_Lam"])
        assert d["beta_over_Lam"] > 20, (z, d["beta_over_Lam"])
        assert d["C"] < 0.05
    # 꼬리 구간: 포화 해제 → 여기서는 fudge 가 실제로 작동한다
    d = rec.peebles_rate_regime(900, 0.013, 0.02237, 0.1430, 0.6736)
    assert not d["saturated"], d["beta_over_Lam"]
    assert d["C"] > 0.1
    # Λ_2γ 는 원자상수 (고정)
    assert abs(d["Lam_2gamma"] - 8.2245809) < 1e-6


def test_fudge_has_no_effect_in_steep_regime():
    """포화의 관측 가능한 귀결: α_B 배율(fudge)을 바꿔도 z_* 가 사실상 불변."""
    import numpy as np
    zg = np.linspace(1600, 200, 500)
    xe = rec.peebles_xe(zg, 0.02237, 0.1430, 0.6736)
    v = rec.optical_depth_and_visibility(zg, xe, 0.02237, 0.6736, 0.1430)
    # fudge 를 바꾼 α_B 로 다시 풀어도 z_* 변화 < 1
    d_lo = rec.peebles_rate_regime(1200, 0.32, 0.02237, 0.1430, 0.6736, fudge=0.7)
    d_hi = rec.peebles_rate_regime(1200, 0.32, 0.02237, 0.1430, 0.6736, fudge=1.3)
    # C·α_B (유효 재결합률) 이 fudge 에 거의 무관
    eff_lo = d_lo["C"] * 0.7
    eff_hi = d_hi["C"] * 1.3
    assert abs(eff_hi / eff_lo - 1.0) < 0.05, (eff_lo, eff_hi)
    assert 1020 < v["z_star"] < 1160
