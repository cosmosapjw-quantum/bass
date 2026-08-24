"""PR-38 자유흐름(Vlasov) 종족 테스트 — D12 오라클 이식."""
import numpy as np
import pytest

from bianchi.matter import freestream as fs


def test_isotropic_no_anisotropic_stress():
    """등방 (a1=a2=a3) 에서 π_ab = 0."""
    _, _, pi = fs.moments([1.0, 1.0, 1.0], mass=0.0)
    assert np.abs(pi).max() < 1e-11


def test_massless_equation_of_state():
    """무질량 w = 1/3, ρ ∝ ℓ⁻⁴ (부피 2배 -> ρ 1/16)."""
    r0, p0, _ = fs.moments([1, 1, 1], 0.0)
    assert abs(p0 / r0 - 1 / 3) < 1e-6
    r1, _, _ = fs.moments([2, 2, 2], 0.0)          # ℓ 2배
    assert abs(np.log(r1 / r0) / np.log(0.5) - 4.0) < 1e-6


def test_nonrelativistic_scaling():
    """비상대론 (m>>T): ρ ∝ ℓ⁻³, w ≈ 0."""
    r0, p0, _ = fs.moments([1, 1, 1], mass=50.0)
    r1, _, _ = fs.moments([2, 2, 2], mass=50.0)
    assert abs(np.log(r1 / r0) / np.log(0.5) - 3.0) < 0.01
    assert p0 / r0 < 1e-2


def test_pi_is_tracefree():
    _, _, pi = fs.moments([1.3, 0.9, 0.85], 0.0)
    assert abs(np.trace(pi)) < 1e-11


def test_emt_conservation():
    """ρ̇ + 3H(ρ+p) + σ_ab π^ab = 0 (무질량/질량)."""
    f = fs.FreeStreamingSpecies(mass=0.0, a_vec=[1.1, 0.95, 0.92])
    r = fs.emt_conservation_residual(f, H=1.0, sigma_diag=[0.15, -0.05, -0.10])
    assert abs(r) < 1e-8
    f2 = fs.FreeStreamingSpecies(mass=3.0, a_vec=[1.1, 0.95, 0.92])
    r2 = fs.emt_conservation_residual(f2, H=1.0, sigma_diag=[0.15, -0.05, -0.10])
    assert abs(r2) < 1e-8


def test_sudden_response_minus_8_15():
    """급작응답 계수 -> -8/15 (Misner 점성; f0 형상 무관)."""
    c = fs.sudden_response_coefficient(delta=0.002, mass=0.0, f0=fs.f_fermi_dirac)
    assert abs(c + 8.0 / 15.0) < 5e-3
    # 형상 무관: 가우시안 f0 도 같은 극한
    cg = fs.sudden_response_coefficient(delta=0.002, mass=0.0,
                                        f0=lambda q: np.exp(-q ** 2 / 2))
    assert abs(cg + 8.0 / 15.0) < 5e-3
    # 질량 기체는 0 으로 소멸
    cm = fs.sudden_response_coefficient(delta=0.004, mass=60.0)
    assert abs(cm) < 1e-2


def test_shear_damping_misner():
    """자유흐름 π_ab 가 shear 를 감쇠시킨다 (부호 확인)."""
    # π_11 부호: a1 큰 방향(팽창)에서 π_11 < 0 -> shear 를 되돌린다
    _, _, pi = fs.moments([1.2, 0.92, 0.9], 0.0)
    assert pi[0, 0] < 0                             # 팽창 축의 anisotropic stress 복원력
