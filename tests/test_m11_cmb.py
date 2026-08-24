"""PR-46 CMB 이방 패턴 테스트."""
import numpy as np
import pytest

from bianchi.observables import cmb_pattern as cmb


def test_bianchi_I_pure_quadrupole():
    """Bianchi I (대각 shear) 는 순수 사중극 CMB 패턴을 만든다."""
    model = dict(H0=1.0, Sigma0=[0.2, -0.1, -0.1], Omega0=0.9, gamma=1.0, nhat=[0, 0, 1])
    t0 = 2 / 3
    pat = cmb.temperature_pattern_diag_bianchi(model, t0, 0.6 * t0,
                                               n_theta=10, n_phi=16, nsteps=400)
    qd = cmb.quadrupole_dominance(pat)
    assert qd["quadrupole_fraction"] > 0.98        # C_2 지배
    assert qd["C"][2] > 100 * (qd["C"][1] + 1e-12)  # C_1 << C_2
    assert qd["C"][2] > 100 * (qd["C"][3] + 1e-12)  # C_3 << C_2


def test_isotropic_no_pattern():
    """등방 배경 (Σ=0) 에서 ΔT/T = 0."""
    t0 = 2 / 3
    pat = cmb.temperature_pattern_diag_bianchi(
        dict(H0=1.0, Sigma0=[0, 0, 0], Omega0=1.0, gamma=1.0, nhat=[0, 0, 1]),
        t0, 0.6 * t0, n_theta=8, n_phi=12, nsteps=300)
    assert np.abs(pat["dT_over_T"]).max() < 1e-12


def test_pattern_amplitude_scales_with_shear():
    """패턴 진폭이 shear 크기에 따라 증가."""
    t0 = 2 / 3
    amps = []
    for amp in (0.1, 0.2):
        model = dict(H0=1.0, Sigma0=[2 * amp, -amp, -amp], Omega0=0.9,
                     gamma=1.0, nhat=[0, 0, 1])
        pat = cmb.temperature_pattern_diag_bianchi(model, t0, 0.5 * t0,
                                                   n_theta=8, n_phi=12, nsteps=300)
        amps.append(np.abs(pat["dT_over_T"]).max())
    assert amps[1] > amps[0]                        # 더 큰 shear -> 더 큰 패턴


def test_planck_limit_reference():
    """Planck VII_h vorticity 제한 참조값이 노출됨."""
    r = cmb.shear_from_planck_limit()
    assert r["vorticity_over_H"] == 7.6e-10
