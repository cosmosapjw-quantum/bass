"""PR-34 질량 중성미자 + PR-35 암흑에너지 테스트."""
import numpy as np
import pytest

from bianchi.matter import neutrino as nu
from bianchi.matter import dark_energy as de


# ══════════════════════════════ PR-34 질량 중성미자
def test_massless_neutrino_scaling():
    """m→0: ρ ∝ a⁻⁴, w = 1/3."""
    n = nu.scaling_exponent(m_eV=1e-6, a1=1.0, a2=0.3)
    assert abs(n - 4.0) < 1e-3
    _, _, w = nu.neutrino_rho_p(1.0, m_eV=1e-6)
    assert abs(w - 1 / 3) < 1e-4


def test_massive_neutrino_nonrel_scaling():
    """m ≫ T: ρ ∝ a⁻³, w → 0 (오늘 매우 무거운 중성미자)."""
    # m = 1 eV, T_nu0 ≈ 1.68e-4 eV -> y0 ≈ 6000 (매우 비상대론)
    n = nu.scaling_exponent(m_eV=1.0, a1=1.0, a2=0.5)
    assert abs(n - 3.0) < 0.05
    _, _, w = nu.neutrino_rho_p(1.0, m_eV=1.0)
    assert w < 1e-3


def test_neutrino_omega_h2():
    """Σm=0.06 eV -> Ω_ν h² ≈ 6.4e-4."""
    assert abs(nu.omega_nu_h2(0.06) - 6.44e-4) < 1e-4


def test_neutrino_transition():
    """중간 질량에서 지수가 3과 4 사이 (상대론→비상대론 전이)."""
    n = nu.scaling_exponent(m_eV=1e-3, a1=1.0, a2=0.5)
    assert 3.0 < n < 4.0


# ══════════════════════════════ PR-35 암흑에너지
def test_lambda_constant_density():
    """Λ (w=-1): ρ_DE 상수."""
    a = np.array([0.1, 0.5, 1.0])
    assert np.allclose(de.rho_ratio_cpl(a, w0=-1.0, wa=0.0), 1.0)


def test_cpl_closed_form():
    """CPL 닫힌형이 수치 적분과 일치."""
    a_tab = np.linspace(0.01, 1.0, 200)
    w0, wa = -0.9, 0.3
    w_tab = de.w_cpl(a_tab, w0, wa)
    for a in (0.2, 0.5, 0.8):
        closed = de.rho_ratio_cpl(a, w0, wa)
        tabud = de.rho_ratio_tabulated(a, a_tab, w_tab)
        assert abs(closed / tabud - 1) < 1e-3


def test_cpl_w_of_a():
    """w(a=1)=w0, w(a=0)=w0+wa."""
    assert abs(de.w_cpl(1.0, -0.9, 0.3) - (-0.9)) < 1e-12
    assert abs(de.w_cpl(0.0, -0.9, 0.3) - (-0.6)) < 1e-12


def test_dark_energy_species():
    """DarkEnergy 성분: π=0, Λ 판정."""
    d = de.DarkEnergy(Omega0=0.7, w0=-1.0, wa=0.0)
    assert d.is_lambda()
    assert np.allclose(d.anisotropic_stress(), 0.0)
    d2 = de.DarkEnergy(Omega0=0.7, w0=-0.9, wa=0.2)
    assert not d2.is_lambda()
