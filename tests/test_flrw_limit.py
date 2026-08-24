"""
PR-49 · FLRW 극한 회귀 (Σ, N, A → 0) 대 CLASS/CAMB 기준값.

Bianchi 해가 등방 극한에서 표준 ΛCDM 로 환원됨을 **관측 파생량 수준**에서 검증한다.
기준값은 Planck 2018 (TT,TE,EE+lowE+lensing) / CAMB.  두 갈래:

  (A) 배경·열·거리 파생량이 ΛCDM 값과 일치 (D_M, 나이, r_drag, z_*, Ω_νh², g_*, θ_*).
  (B) 이방 고유 신호(shear·vorticity·다극)가 Σ=v=0 에서 정확히 소멸.

★ 정직성: 음향지평 물리적분(sound_horizon)은 반해석적 ~2% 오차가 있어(반복 확인)
  Aubourg2015 보정식(sound_horizon_fit, CAMB 0.1%)을 정밀 오라클로 병기한다.
  θ_* 는 물리적분 기준이라 ~2% 편차를 상속 — 완전 정밀은 Boltzmann(CLASS/CAMB) 필요.
"""
import numpy as np
from scipy.integrate import quad
import pytest

from bianchi.observables import distances as D
from bianchi.observables import sn
from bianchi.physical import units as U
from bianchi.physical import congruence as cg
from bianchi.thermo import dof, recombination as rec, temperature as temp
from bianchi.matter import neutrino as nu
from bianchi.analysis import no_hair as nh

# ---- Planck 2018 / CAMB 기준값 ----
H0, OM, OR = 67.36, 0.3153, 9.24e-5
OB_H2, OM_H2 = 0.02237, 0.1430
Z_STAR = 1089.80                    # 최종산란 (visibility)
DM_STAR_CAMB = 13869.6              # 공변 D_M(z*) [Mpc]
R_DRAG_PLANCK = 147.09              # [Mpc]
AGE_PLANCK = 13.797                 # [Gyr]
ACOUSTIC_100THETA = 1.04109        # 100 θ_*


# ═══════════════════════════════ (A) 배경·거리
def test_distance_to_last_scattering():
    """D_M(z*) = 13869.6 Mpc (CAMB) 를 0.3% 내로."""
    DM = D.comoving_distance(Z_STAR, H0=H0, Om=OM, Or=OR)
    assert abs(DM - DM_STAR_CAMB) / DM_STAR_CAMB < 3e-3


def test_cosmic_age():
    """우주 나이 t0 = 13.797 Gyr 를 0.5% 내로."""
    integ, _ = quad(lambda z: 1.0 / ((1 + z) * D.flrw_hubble(z, H0, OM, OR)),
                    0, np.inf, limit=400)
    age = integ * U.MPC_KM / U.GYR_S
    assert abs(age - AGE_PLANCK) / AGE_PLANCK < 5e-3


def test_sound_horizon_calibrated():
    """r_drag (Aubourg2015 보정식) = 147.09 Mpc 를 0.2% 내로 (CAMB급 오라클)."""
    rs = D.sound_horizon_fit(Om_h2=OM_H2, Ob_h2=OB_H2, Onu_h2=6.4e-4)
    assert abs(rs - R_DRAG_PLANCK) / R_DRAG_PLANCK < 2e-3


def test_sound_horizon_integral_selfconsistent():
    """물리적분 r_drag (자기일관 z_drag + 복사기 해석 꼬리) — 1% 내.

    ★ v3.0 (A3): 이전 판은 z_max=1e5 절단으로 꼬리 2.7 Mpc(≈2%)를 빠뜨렸고,
      E-H z_drag(≈1021)가 그 결손을 **우연히 벌충**해 0.5% 처럼 보였다.
      꼬리를 더하고 z_drag 을 τ=1 자기일관 값으로 바꾼 뒤 실제로 1% 내가 된다.
    """
    rs_int = D.sound_horizon(H0=H0, Om=OM, Ob_h2=OB_H2, Or=OR)
    assert abs(rs_int - R_DRAG_PLANCK) / R_DRAG_PLANCK < 1e-2


def test_sound_horizon_tail_is_significant():
    """복사기 꼬리가 무시할 수 없음을 박제 (A3 회귀 가드)."""
    with_tail = D.sound_horizon(z_drag=Z_STAR, H0=H0, Om=OM, Ob_h2=OB_H2, Or=OR)
    truncated = D.sound_horizon(z_drag=Z_STAR, H0=H0, Om=OM, Ob_h2=OB_H2, Or=OR,
                                include_tail=False)
    assert with_tail - truncated > 2.0                    # ≈2.7 Mpc
    assert abs(with_tail - 144.43) / 144.43 < 5e-3        # 꼬리 포함 시 0.5% 내
    assert abs(truncated - 144.43) / 144.43 > 1e-2        # 절단 시 1% 이상 어긋남


def test_acoustic_scale():
    """100θ_* = r_s(z*)/D_M(z*) = 1.04109 (Planck) — **0.5% 내**.

    ★ v3.0 (A3): 절단 오차 수정 전에는 1.021 (-2%) 였다.
    """
    rs_star = D.sound_horizon(z_drag=Z_STAR, H0=H0, Om=OM, Ob_h2=OB_H2, Or=OR)
    DM = D.comoving_distance(Z_STAR, H0=H0, Om=OM, Or=OR)
    theta = 100.0 * rs_star / DM
    assert abs(theta - ACOUSTIC_100THETA) / ACOUSTIC_100THETA < 5e-3, theta


def test_drag_redshift_selfconsistent():
    """τ_drag=1 자기일관 z_drag 이 Planck 1059.94 근방 (±2%)."""
    zd = D.drag_redshift_tau(Ob_h2=OB_H2, H0=H0, Om=OM, Or=OR)
    assert abs(zd - 1059.94) / 1059.94 < 2e-2, zd


def test_bao_matches_boss():
    """BAO D_M/r_s, D_H/r_s 가 BOSS/eBOSS 유효값과 ~4% 내."""
    rs = D.sound_horizon_fit(Om_h2=OM_H2, Ob_h2=OB_H2)
    ref = {0.38: (10.27, 24.89), 0.51: (13.36, 22.33), 1.48: (30.21, 13.26)}
    for z, (dm_ref, dh_ref) in ref.items():
        b = D.bao_observables(z, r_s=rs, H0=H0, Om=OM)
        assert abs(b["DM_over_rs"] - dm_ref) / dm_ref < 4e-2, (z, b["DM_over_rs"])
        assert abs(b["DH_over_rs"] - dh_ref) / dh_ref < 4e-2, (z, b["DH_over_rs"])


# ═══════════════════════════════ (A) 열역사·중성미자
def test_neutrino_omega():
    """Ω_ν h²(Σm=0.06 eV) = 6.4e-4 (정확 FD 적분 = 근사식 <1%)."""
    assert abs(nu.omega_nu_h2(0.06) - 6.4e-4) < 5e-5


def test_gstar_limits():
    """g_*: 고온 106.75, 저온 (3.363, 3.909)."""
    assert abs(dof.g_star(1e4) - 106.75) < 1e-6          # 10 TeV 점근 (v3.0 A1)
    assert abs(dof.g_star(1e-5) - 3.36) < 0.01
    assert abs(dof.g_star_s(1e-5) - 3.91) < 0.01


def test_neutrino_temperature():
    """T_ν/T_γ = (4/11)^{1/3}."""
    assert abs(temp.neutrino_temperature(1.0) - (4 / 11) ** (1 / 3)) < 1e-6


def test_recombination_visibility_zstar():
    """관측 z_* (가시함수 최대) ≈ 1090 을 2% 내 + 잔존 x_e 급."""
    zg = np.linspace(1600, 200, 800)
    xe = rec.peebles_xe(zg, OB_H2, OM_H2, H0 / 100)
    vis = rec.optical_depth_and_visibility(zg, xe, OB_H2, H0 / 100, OM_H2)
    assert abs(vis["z_star"] - 1089.9) / 1089.9 < 2e-2
    assert 1e-4 < xe[-1] < 6e-4                       # 잔존 자유전자


# ═══════════════════════════════ (B) 이방 신호가 등방 극한에서 소멸
def test_shear_free_congruence_irrotational():
    """Σ, tilt = 0 → vorticity = 0, 팽창 θ_u = 3H."""
    H = 70.0; zero = np.zeros((3, 3)); z3 = np.zeros(3)
    k = cg.congruence_kinematics(H, zero, zero, z3, z3, z3, z3)
    assert np.abs(k["omega3"]).max() < 1e-13
    assert abs(k["theta"] - 3 * H) < 1e-9             # 등방: θ = 3H


def test_shear_free_no_directional_hubble():
    """Σ=0 → H_∥(n̂) = H (방향 무관)."""
    for n in ([1, 0, 0], [0, 1, 0], [1, 1, 1]):
        assert abs(D.directional_hubble(70.0, np.zeros((3, 3)), n) - 70.0) < 1e-9


def test_shear_free_bao_isotropic():
    """Σ=0 → 이방 BAO anisotropy = 0, AP 사중극 = 0."""
    assert D.anisotropic_bao(0.5, np.zeros((3, 3)))["anisotropy"] < 1e-12
    assert D.alcock_paczynski_quadrupole(0.5, np.zeros((3, 3))) < 1e-14


def test_shear_free_sn_no_multipoles():
    """Σ=0, v=0 → SN Hubble diagram 쌍극·사중극 = 0."""
    d = sn.decompose_dipole_quadrupole(0.1, np.zeros((3, 3)), v=None)
    assert d["C1"] < 1e-12 and d["C2"] < 1e-12


def test_no_hair_already_desitter():
    """Σ0→0 은 이미 de Sitter: Σ 가 0 근방 유지, H→√(Λ/3)."""
    r = nh.verify_no_hair(Lambda=1.0, Sigma0=1e-6, tau_max=6.0)
    assert r["Sigma_final"] < 1e-6
    assert abs(r["H_final"] - r["H_dS"]) < 1e-6
