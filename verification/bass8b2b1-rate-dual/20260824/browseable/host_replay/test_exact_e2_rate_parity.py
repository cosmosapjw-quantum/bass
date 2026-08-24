"""Exact-host parity between BASS-8B.2B.1 and the frozen E2 owner."""
from __future__ import annotations

from pathlib import Path
import os

import numpy as np
import pytest

from pure_python_e2_loader import load_exact_e2_owner

_E2_MODULE_ROOT = os.environ.get("BASS_E2_MODULE_ROOT")
if not _E2_MODULE_ROOT:
    raise RuntimeError("BASS_E2_MODULE_ROOT is required for exact E2 host parity")
_EF, _ER, E2_LOADER_RECEIPT = load_exact_e2_owner(Path(_E2_MODULE_ROOT))
E2_C_LIGHT_M_S = _EF.C_LIGHT_M_S
ColdElectronTestField = _EF.ColdElectronTestField
ElectronCollisionContext = _ER.ElectronCollisionContext
E2_SIGMA_T_M2 = _ER.SIGMA_T_M2
from direction_dependent_rate_dual import (
    C_LIGHT_M_S,
    SIGMA_T_M2,
    NormalHubbleRateJet,
    RateDualAuthority,
    bind_direction_dependent_rate_dual,
)
from electron_state_binding import (
    CollisionOff,
    DerivativeSide,
    ElectronBindingCertificate,
    ElectronStateJet,
    HashRef,
    IndependentElectronState,
)
from generic_vector_paired_carrier import lebedev26

H1 = "1" * 64
H2 = "2" * 64
H3 = "3" * 64
H4 = "4" * 64


def candidate_binding(density: float, beta: np.ndarray) -> ElectronBindingCertificate:
    if density == 0.0:
        return ElectronBindingCertificate(
            state=CollisionOff("exact-vacuum", H1),
            jet=None,
            coordinate_sha256=H3,
            binding_sha256=H4,
            metadata={"direction_dependent_rate_bound": False},
        )
    state = IndependentElectronState(
        proper_density_m3=float(density),
        beta_normal=tuple(float(x) for x in beta),
        schedule_payload_sha256=H1,
        source=HashRef("e2-parity-electron", H2),
    )
    jet = ElectronStateJet(
        tau=0.25,
        proper_density_m3=float(density),
        beta_normal=tuple(float(x) for x in beta),
        dproper_density_dtau=0.0,
        dbeta_normal_dtau=(0.0, 0.0, 0.0),
        segment_index=0,
        derivative_side=DerivativeSide.INTERIOR,
        closure=state.closure,
        schedule_payload_sha256=H1,
    )
    return ElectronBindingCertificate(
        state=state,
        jet=jet,
        coordinate_sha256=H3,
        binding_sha256=H4,
        metadata={"direction_dependent_rate_bound": False},
    )


def candidate_rate(density: float, beta: np.ndarray, H: float):
    e_rest, w_rest = lebedev26()
    return bind_direction_dependent_rate_dual(
        candidate_binding(density, beta),
        NormalHubbleRateJet(
            tau=0.25,
            H_normal_s=H,
            dH_normal_s_dtau=0.0,
            derivative_side=DerivativeSide.INTERIOR,
            coordinate_sha256=H3,
            provenance=HashRef("e2-parity-H", H2),
        ),
        e_rest=e_rest,
        w_rest=w_rest,
        authority=RateDualAuthority.frozen_project_authority(),
    )


def test_project_constants_are_identical_to_frozen_e2_owner():
    assert C_LIGHT_M_S == E2_C_LIGHT_M_S == 299_792_458.0
    assert SIGMA_T_M2 == E2_SIGMA_T_M2


def test_zero_tilt_rate_matches_frozen_e2_owner():
    density, H = 7.0, 2.1e-18
    beta = np.zeros(3)
    candidate = candidate_rate(density, beta, H)
    actual = ElectronCollisionContext(
        ColdElectronTestField.independent(density, beta)
    ).rate_per_normal_hubble_time(candidate.e_normal, H)
    np.testing.assert_allclose(candidate.nu_tau, actual, rtol=0.0, atol=0.0)


def test_generic_vector_rate_matches_frozen_e2_owner_randomized():
    rng = np.random.default_rng(20260824)
    for _ in range(128):
        direction = rng.normal(size=3)
        direction /= np.linalg.norm(direction)
        beta = float(rng.uniform(0.0, 0.75)) * direction
        density = float(10.0 ** rng.uniform(-3.0, 5.0))
        H = float(10.0 ** rng.uniform(-20.0, -16.0))
        candidate = candidate_rate(density, beta, H)
        context = ElectronCollisionContext(
            ColdElectronTestField.independent(density, beta)
        )
        actual_hubble = context.rate_per_normal_hubble_time(candidate.e_normal, H)
        actual_second = context.rate_per_normal_time_s(candidate.e_normal)
        np.testing.assert_allclose(candidate.nu_tau, actual_hubble, rtol=3e-15, atol=0.0)
        np.testing.assert_allclose(candidate.nu_tau * H, actual_second, rtol=3e-15, atol=0.0)
        np.testing.assert_allclose(
            candidate.nu_tau,
            candidate.global_generator_scale * candidate.direction_factor,
            rtol=3e-15,
            atol=0.0,
        )


def test_exact_vacuum_rate_agrees_but_candidate_quotients_velocity():
    H = 2.1e-18
    beta_representative = np.array([0.2, -0.1, 0.05])
    candidate = candidate_rate(0.0, beta_representative, H)
    e_rest, _ = lebedev26()
    actual = ElectronCollisionContext(
        ColdElectronTestField.independent(0.0, beta_representative)
    ).rate_per_normal_hubble_time(e_rest, H)
    assert candidate.beta is None
    assert np.array_equal(candidate.nu_tau, actual)
    assert candidate.authority_metadata()["collision_off_velocity_quotient"] is True


def test_actual_e2_owner_rejects_nonunit_normal_directions():
    context = ElectronCollisionContext(
        ColdElectronTestField.independent(1.0, (0.1, 0.0, 0.0))
    )
    with pytest.raises(ValueError, match="unit vectors"):
        context.rate_per_normal_hubble_time(np.array([[2.0, 0.0, 0.0]]), 2.0e-18)
