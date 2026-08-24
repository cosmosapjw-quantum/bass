from __future__ import annotations

import importlib

import numpy as np
import pytest

from electron_state_binding import (
    DerivativeSide,
    ElectronBindingCertificate,
    ElectronStateJet,
    HashRef,
    IndependentElectronState,
    CollisionOff,
)
from generic_vector_paired_carrier import lebedev26, rotation_matrix, rotate_state

rate_dual = importlib.import_module("direction_dependent_rate_dual")

H1 = "1" * 64
H2 = "2" * 64
H3 = "3" * 64
H4 = "4" * 64


def electron_binding(
    *,
    tau: float = 0.3,
    density: float = 7.0,
    beta=(0.0, 0.0, 0.0),
    ddensity: float = 0.0,
    dbeta=(0.0, 0.0, 0.0),
    side: DerivativeSide = DerivativeSide.INTERIOR,
) -> ElectronBindingCertificate:
    state = IndependentElectronState(
        proper_density_m3=density,
        beta_normal=tuple(beta),
        schedule_payload_sha256=H1,
        source=HashRef("electron-schedule", H2),
    )
    jet = ElectronStateJet(
        tau=tau,
        proper_density_m3=density,
        beta_normal=tuple(beta),
        dproper_density_dtau=ddensity,
        dbeta_normal_dtau=tuple(dbeta),
        segment_index=0,
        derivative_side=side,
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


def test_rate_dual_binding_api_exists():
    assert hasattr(rate_dual, "bind_direction_dependent_rate_dual")


def test_zero_tilt_returns_rest_grid_and_e2_rate():
    e_rest, w_rest = lebedev26()
    H = 2.0e-18
    hubble = rate_dual.NormalHubbleRateJet(
        tau=0.3,
        H_normal_s=H,
        dH_normal_s_dtau=0.0,
        derivative_side=DerivativeSide.INTERIOR,
        coordinate_sha256=H3,
        provenance=HashRef("normal-H", H2),
    )
    authority = rate_dual.RateDualAuthority.frozen_project_authority()
    out = rate_dual.bind_direction_dependent_rate_dual(
        electron_binding(density=7.0),
        hubble,
        e_rest=e_rest,
        w_rest=w_rest,
        authority=authority,
    )

    alpha = 7.0 * rate_dual.SIGMA_T_M2 * rate_dual.C_LIGHT_M_S / H
    assert out.gamma == pytest.approx(1.0)
    assert np.array_equal(out.e_normal, e_rest)
    assert np.array_equal(out.w_normal, w_rest)
    assert np.array_equal(out.doppler, np.ones(len(e_rest)))
    assert np.array_equal(out.direction_factor, np.ones(len(e_rest)))
    assert np.allclose(out.nu_tau, alpha)
    assert out.global_generator_scale == pytest.approx(alpha)


def test_generic_rate_matches_e2_direction_factorization():
    e_rest, w_rest = lebedev26()
    beta = np.array([0.17, -0.09, 0.11])
    beta *= 0.23 / np.linalg.norm(beta)
    H = 3.0e-18
    out = rate_dual.bind_direction_dependent_rate_dual(
        electron_binding(density=5.0, beta=beta),
        rate_dual.NormalHubbleRateJet(
            tau=0.3,
            H_normal_s=H,
            dH_normal_s_dtau=0.0,
            derivative_side=DerivativeSide.INTERIOR,
            coordinate_sha256=H3,
            provenance=HashRef("normal-H", H2),
        ),
        e_rest=e_rest,
        w_rest=w_rest,
        authority=rate_dual.RateDualAuthority.frozen_project_authority(),
    )
    gamma = 1.0 / np.sqrt(1.0 - beta @ beta)
    q = 1.0 - out.e_normal @ beta
    alpha = 5.0 * rate_dual.SIGMA_T_M2 * rate_dual.C_LIGHT_M_S / H
    assert out.gamma == pytest.approx(gamma)
    assert np.max(np.abs(out.direction_factor - q)) < 2e-15
    assert np.max(np.abs(out.doppler - gamma * q)) < 2e-15
    assert np.max(np.abs(out.nu_tau - alpha * gamma * q)) < 2e-15 * max(1.0, alpha)
    assert out.global_generator_scale == pytest.approx(alpha * gamma)


def test_full_generator_left_dual_and_projector_scalar_cancellation():
    e_rest, w_rest = lebedev26()
    beta = np.array([0.12, -0.16, 0.07])
    beta *= 0.27 / np.linalg.norm(beta)
    common = dict(
        e_rest=e_rest,
        w_rest=w_rest,
        authority=rate_dual.RateDualAuthority.frozen_project_authority(),
    )
    out = rate_dual.bind_direction_dependent_rate_dual(
        electron_binding(density=4.0, beta=beta),
        rate_dual.NormalHubbleRateJet(
            tau=0.3,
            H_normal_s=2.5e-18,
            dH_normal_s_dtau=0.0,
            derivative_side=DerivativeSide.INTERIOR,
            coordinate_sha256=H3,
            provenance=HashRef("normal-H", H2),
        ),
        **common,
    )
    rescaled = rate_dual.bind_direction_dependent_rate_dual(
        electron_binding(density=40.0, beta=beta),
        rate_dual.NormalHubbleRateJet(
            tau=0.3,
            H_normal_s=8.0e-18,
            dH_normal_s_dtau=0.0,
            derivative_side=DerivativeSide.INTERIOR,
            coordinate_sha256=H3,
            provenance=HashRef("normal-H", H2),
        ),
        **common,
    )
    rng = np.random.default_rng(15)
    y = rng.normal(size=9 * len(e_rest))
    cy = out.apply_full_generator(y)
    assert abs(out.left_functional(cy)) < 3e-13 * max(1.0, np.linalg.norm(cy))
    py = out.project(y)
    assert np.max(np.abs(out.project(py) - py)) < 3e-13
    assert out.global_generator_scale != pytest.approx(rescaled.global_generator_scale)
    assert np.max(np.abs(out.project(y) - rescaled.project(y))) < 3e-13


def test_rate_jet_includes_paired_node_motion_and_matches_finite_difference():
    e_rest, w_rest = lebedev26()
    tau = 0.37
    density = 5.0
    ddensity = 0.4
    beta = np.array([0.11, -0.08, 0.05])
    dbeta = np.array([0.013, -0.017, 0.009])
    H = 2.7e-18
    dH = -0.12e-18
    auth = rate_dual.RateDualAuthority.frozen_project_authority()

    def evaluate(t: float):
        dt = t - tau
        return rate_dual.bind_direction_dependent_rate_dual(
            electron_binding(
                tau=t,
                density=density + ddensity * dt,
                beta=beta + dbeta * dt,
                ddensity=ddensity,
                dbeta=dbeta,
            ),
            rate_dual.NormalHubbleRateJet(
                tau=t,
                H_normal_s=H + dH * dt,
                dH_normal_s_dtau=dH,
                derivative_side=DerivativeSide.INTERIOR,
                coordinate_sha256=H3,
                provenance=HashRef("normal-H", H2),
            ),
            e_rest=e_rest,
            w_rest=w_rest,
            authority=auth,
        )

    out = evaluate(tau)
    h = 2.0e-6
    plus = evaluate(tau + h)
    minus = evaluate(tau - h)
    de_fd = (plus.e_normal - minus.e_normal) / (2.0 * h)
    dq_fd = (plus.direction_factor - minus.direction_factor) / (2.0 * h)
    dD_fd = (plus.doppler - minus.doppler) / (2.0 * h)
    dnu_fd = (plus.nu_tau - minus.nu_tau) / (2.0 * h)

    assert np.max(np.abs(out.de_normal_dtau - de_fd)) < 2e-9
    assert np.max(np.abs(out.ddirection_factor_dtau - dq_fd)) < 2e-10
    assert np.max(np.abs(out.ddoppler_dtau - dD_fd)) < 2e-10
    assert np.max(np.abs(out.dnu_tau_dtau - dnu_fd)) < 2e-10

    gamma = out.gamma
    dgamma = gamma**3 * float(beta @ dbeta)
    D_rest_formula = 1.0 / (gamma * (1.0 + e_rest @ beta))
    dD_rest_formula = -D_rest_formula * (
        dgamma / gamma + (e_rest @ dbeta) / (1.0 + e_rest @ beta)
    )
    assert np.max(np.abs(out.doppler - D_rest_formula)) < 2e-15
    assert np.max(np.abs(out.ddoppler_dtau - dD_rest_formula)) < 2e-14
    assert np.max(
        np.abs(
            out.ddoppler_dtau
            - (
                out.dgamma_dtau * out.direction_factor
                + out.gamma * out.ddirection_factor_dtau
            )
        )
    ) < 2e-14
    expected_log_rate = (
        ddensity / density - dH / H + out.ddoppler_dtau / out.doppler
    )
    assert np.max(
        np.abs(out.dnu_tau_dtau / out.nu_tau - expected_log_rate)
    ) < 2e-13



def test_knot_side_and_coordinate_authorities_must_match():
    e_rest, w_rest = lebedev26()
    binding = electron_binding(side=DerivativeSide.LEFT)
    auth = rate_dual.RateDualAuthority.frozen_project_authority()
    with pytest.raises(ValueError, match="same derivative side"):
        rate_dual.bind_direction_dependent_rate_dual(
            binding,
            rate_dual.NormalHubbleRateJet(
                tau=0.3,
                H_normal_s=2.0e-18,
                dH_normal_s_dtau=0.0,
                derivative_side=DerivativeSide.RIGHT,
                coordinate_sha256=H3,
                provenance=HashRef("normal-H", H2),
            ),
            e_rest=e_rest,
            w_rest=w_rest,
            authority=auth,
        )
    with pytest.raises(ValueError, match="coordinate authority"):
        rate_dual.bind_direction_dependent_rate_dual(
            binding,
            rate_dual.NormalHubbleRateJet(
                tau=0.3,
                H_normal_s=2.0e-18,
                dH_normal_s_dtau=0.0,
                derivative_side=DerivativeSide.LEFT,
                coordinate_sha256="9" * 64,
                provenance=HashRef("normal-H", H2),
            ),
            e_rest=e_rest,
            w_rest=w_rest,
            authority=auth,
        )


def test_local_observer_boost_cannot_own_electron_collision_rate():
    frozen = rate_dual.RateDualAuthority.frozen_project_authority()
    with pytest.raises(ValueError, match="electron_from_normal"):
        rate_dual.RateDualAuthority(
            e2_rate_owner_sha256=frozen.e2_rate_owner_sha256,
            electron_state_jet_source_sha256=frozen.electron_state_jet_source_sha256,
            carrier_source_sha256=frozen.carrier_source_sha256,
            sigma_t_m2=frozen.sigma_t_m2,
            c_m_s=frozen.c_m_s,
            frame_map="local_observer_output_boost",
            time_variable=frozen.time_variable,
        )


def test_exact_vacuum_is_collision_off_and_has_no_projector():
    e_rest, w_rest = lebedev26()
    state = CollisionOff("exact-vacuum", H1)
    binding = ElectronBindingCertificate(
        state=state,
        jet=None,
        coordinate_sha256=H3,
        binding_sha256=H4,
        metadata={"direction_dependent_rate_bound": False},
    )
    out = rate_dual.bind_direction_dependent_rate_dual(
        binding,
        rate_dual.NormalHubbleRateJet(
            tau=0.3,
            H_normal_s=2.0e-18,
            dH_normal_s_dtau=0.0,
            derivative_side=DerivativeSide.INTERIOR,
            coordinate_sha256=H3,
            provenance=HashRef("normal-H", H2),
        ),
        e_rest=e_rest,
        w_rest=w_rest,
        authority=rate_dual.RateDualAuthority.frozen_project_authority(),
    )
    assert out.collision_off is True
    assert out.beta is None
    assert np.array_equal(out.nu_tau, np.zeros(len(e_rest)))
    y = np.ones(9 * len(e_rest))
    assert np.array_equal(out.apply_full_generator(y), np.zeros_like(y))
    with pytest.raises(rate_dual.VacuumProjectorUndefinedError):
        out.project(y)



def test_hostile_rate_and_left_mutations_are_detected():
    e_rest, w_rest = lebedev26()
    beta = np.array([0.19, -0.08, 0.04])
    beta *= 0.31 / np.linalg.norm(beta)
    out = rate_dual.bind_direction_dependent_rate_dual(
        electron_binding(density=6.0, beta=beta),
        rate_dual.NormalHubbleRateJet(
            tau=0.3,
            H_normal_s=2.4e-18,
            dH_normal_s_dtau=0.0,
            derivative_side=DerivativeSide.INTERIOR,
            coordinate_sha256=H3,
            provenance=HashRef("normal-H", H2),
        ),
        e_rest=e_rest,
        w_rest=w_rest,
        authority=rate_dual.RateDualAuthority.frozen_project_authority(),
    )
    mutations = out.rate_mutations()
    assert np.max(np.abs(mutations["omit_gamma"] - out.nu_tau)) > 1e-5
    assert np.max(np.abs(mutations["omit_direction_factor"] - out.nu_tau)) > 1e-5
    assert np.max(np.abs(mutations["double_doppler"] - out.nu_tau)) > 1e-5

    rng = np.random.default_rng(23)
    y = rng.normal(size=9 * len(e_rest))
    correct = out.apply_full_generator(y)
    assert abs(out.left_functional(correct)) < 3e-13 * max(1.0, np.linalg.norm(correct))
    assert abs(out.left_without_direction_factor(correct)) > 1e-6
    omit_q = out.apply_mutated_generator(y, "omit_direction_factor")
    double_d = out.apply_mutated_generator(y, "double_doppler")
    assert abs(out.left_functional(omit_q)) > 1e-6
    assert abs(out.left_functional(double_d)) > 1e-6


def test_so3_covariance_of_rate_jet_generator_and_dual():
    e_rest, w_rest = lebedev26()
    beta = np.array([0.12, -0.07, 0.18])
    dbeta = np.array([0.011, 0.006, -0.013])
    R = rotation_matrix(np.array([0.3, -0.5, 0.8]), 0.73)
    auth = rate_dual.RateDualAuthority.frozen_project_authority()

    def build(e0, b, db):
        return rate_dual.bind_direction_dependent_rate_dual(
            electron_binding(beta=b, dbeta=db, ddensity=0.2),
            rate_dual.NormalHubbleRateJet(
                tau=0.3,
                H_normal_s=2.2e-18,
                dH_normal_s_dtau=-0.04e-18,
                derivative_side=DerivativeSide.INTERIOR,
                coordinate_sha256=H3,
                provenance=HashRef("normal-H", H2),
            ),
            e_rest=e0,
            w_rest=w_rest,
            authority=auth,
        )

    base = build(e_rest, beta, dbeta)
    rotated = build(e_rest @ R.T, R @ beta, R @ dbeta)
    assert np.max(np.abs(rotated.e_normal - base.e_normal @ R.T)) < 3e-13
    assert np.max(np.abs(rotated.de_normal_dtau - base.de_normal_dtau @ R.T)) < 3e-13
    assert np.max(np.abs(rotated.doppler - base.doppler)) < 3e-14
    assert np.max(np.abs(rotated.ddoppler_dtau - base.ddoppler_dtau)) < 3e-14
    assert np.max(np.abs(rotated.nu_tau - base.nu_tau)) < 3e-14
    assert np.max(np.abs(rotated.dnu_tau_dtau - base.dnu_tau_dtau)) < 3e-14

    rng = np.random.default_rng(51)
    y = rng.normal(size=9 * len(e_rest))
    yr = rotate_state(y, R)
    lhs = rotated.apply_full_generator(yr)
    rhs = rotate_state(base.apply_full_generator(y), R)
    assert np.max(np.abs(lhs - rhs)) < 3e-12 * max(1.0, np.max(np.abs(rhs)))
    assert rotated.left_functional(yr) == pytest.approx(base.left_functional(y), abs=3e-13)


def test_typeii_axis_lane_is_only_generic_vector_restriction():
    e_rest, w_rest = lebedev26()
    v, vdot = 0.21, -0.017
    beta = np.array([0.0, v, 0.0])
    dbeta = np.array([0.0, vdot, 0.0])
    out = rate_dual.bind_direction_dependent_rate_dual(
        electron_binding(beta=beta, dbeta=dbeta),
        rate_dual.NormalHubbleRateJet(
            tau=0.3,
            H_normal_s=2.0e-18,
            dH_normal_s_dtau=0.0,
            derivative_side=DerivativeSide.INTERIOR,
            coordinate_sha256=H3,
            provenance=HashRef("normal-H", H2),
        ),
        e_rest=e_rest,
        w_rest=w_rest,
        authority=rate_dual.RateDualAuthority.frozen_project_authority(),
    )
    gamma = 1.0 / np.sqrt(1.0 - v * v)
    dgamma = gamma**3 * v * vdot
    assert np.max(np.abs(out.direction_factor - (1.0 - v * out.e_normal[:, 1]))) < 2e-15
    assert out.gamma == pytest.approx(gamma)
    assert out.dgamma_dtau == pytest.approx(dgamma)
    assert np.max(
        np.abs(
            out.ddirection_factor_dtau
            + vdot * out.e_normal[:, 1]
            + v * out.de_normal_dtau[:, 1]
        )
    ) < 2e-14


def test_frozen_owner_hashes_and_state_jet_consistency_are_fail_closed():
    e_rest, w_rest = lebedev26()
    frozen = rate_dual.RateDualAuthority.frozen_project_authority()
    wrong = rate_dual.RateDualAuthority(
        e2_rate_owner_sha256="8" * 64,
        electron_state_jet_source_sha256=frozen.electron_state_jet_source_sha256,
        carrier_source_sha256=frozen.carrier_source_sha256,
        sigma_t_m2=frozen.sigma_t_m2,
        c_m_s=frozen.c_m_s,
    )
    hubble = rate_dual.NormalHubbleRateJet(
        tau=0.3,
        H_normal_s=2.0e-18,
        dH_normal_s_dtau=0.0,
        derivative_side=DerivativeSide.INTERIOR,
        coordinate_sha256=H3,
        provenance=HashRef("normal-H", H2),
    )
    with pytest.raises(ValueError, match="frozen project owner"):
        rate_dual.bind_direction_dependent_rate_dual(
            electron_binding(), hubble, e_rest=e_rest, w_rest=w_rest, authority=wrong
        )

    inconsistent = electron_binding(density=7.0)
    object.__setattr__(inconsistent.state, "proper_density_m3", 8.0)
    with pytest.raises(ValueError, match="state/jet density mismatch"):
        rate_dual.bind_direction_dependent_rate_dual(
            inconsistent, hubble, e_rest=e_rest, w_rest=w_rest, authority=frozen
        )


def test_metadata_keeps_rows_and_runtime_unpromoted():
    e_rest, w_rest = lebedev26()
    out = rate_dual.bind_direction_dependent_rate_dual(
        electron_binding(beta=(0.1, 0.02, -0.03)),
        rate_dual.NormalHubbleRateJet(
            tau=0.3,
            H_normal_s=2.0e-18,
            dH_normal_s_dtau=0.0,
            derivative_side=DerivativeSide.INTERIOR,
            coordinate_sha256=H3,
            provenance=HashRef("normal-H", H2),
        ),
        e_rest=e_rest,
        w_rest=w_rest,
        authority=rate_dual.RateDualAuthority.frozen_project_authority(),
    )
    meta = out.authority_metadata()
    assert meta["direction_dependent_rate_dual_bound"] is True
    assert meta["moving_bundle_differential_bound"] is False
    assert meta["projector_left_full_audit_bound"] is False
    assert meta["authority_row_promoted"] is False
    assert meta["production_runtime_wired"] is False


def test_rate_bound_left_dual_is_derived_from_shape_dual_nodewise():
    e_rest, w_rest = lebedev26()
    out = rate_dual.bind_direction_dependent_rate_dual(
        electron_binding(density=5.5, beta=(0.17, -0.06, 0.09)),
        rate_dual.NormalHubbleRateJet(
            tau=0.3,
            H_normal_s=2.3e-18,
            dH_normal_s_dtau=0.0,
            derivative_side=DerivativeSide.INTERIOR,
            coordinate_sha256=H3,
            provenance=HashRef("normal-H", H2),
        ),
        e_rest=e_rest,
        w_rest=w_rest,
        authority=rate_dual.RateDualAuthority.frozen_project_authority(),
    )
    # The no-rate transformed shape has left weights w*q^2.  Multiplication
    # by nu=alpha*gamma*q maps the full left dual to shape_left/nu.  The
    # residual global 1/(alpha*gamma) is irrelevant to the normalized P.
    assert np.max(
        np.abs(
            out.shape_left_node_weights / out.nu_tau
            - out.full_left_node_weights / out.global_generator_scale
        )
    ) < 2e-14
    assert np.max(
        np.abs(
            out.full_left_node_weights
            - out.w_normal * out.direction_factor / (4.0 * np.pi)
        )
    ) < 2e-15


def test_bound_authority_arrays_are_immutable_and_detached_from_inputs():
    e_rest, w_rest = lebedev26()
    beta = np.array([0.13, -0.04, 0.08])
    dbeta = np.array([0.01, 0.002, -0.004])
    out = rate_dual.bind_direction_dependent_rate_dual(
        electron_binding(beta=beta, dbeta=dbeta),
        rate_dual.NormalHubbleRateJet(
            tau=0.3,
            H_normal_s=2.0e-18,
            dH_normal_s_dtau=0.0,
            derivative_side=DerivativeSide.INTERIOR,
            coordinate_sha256=H3,
            provenance=HashRef("normal-H", H2),
        ),
        e_rest=e_rest,
        w_rest=w_rest,
        authority=rate_dual.RateDualAuthority.frozen_project_authority(),
    )
    frozen_names = (
        "e_normal",
        "de_normal_dtau",
        "w_normal",
        "beta",
        "dbeta_dtau",
        "doppler",
        "ddoppler_dtau",
        "direction_factor",
        "ddirection_factor_dtau",
        "nu_tau",
        "dnu_tau_dtau",
        "shape_left_node_weights",
        "full_left_node_weights",
    )
    assert all(not getattr(out, name).flags.writeable for name in frozen_names)
    beta[:] = 0.0
    dbeta[:] = 0.0
    assert np.linalg.norm(out.beta) > 0.0
    with pytest.raises(ValueError):
        out.nu_tau[0] = 0.0


def test_rate_dual_receipt_retains_replayable_input_provenance():
    e_rest, w_rest = lebedev26()
    out = rate_dual.bind_direction_dependent_rate_dual(
        electron_binding(density=4.2, beta=(0.08, -0.03, 0.05), ddensity=0.11),
        rate_dual.NormalHubbleRateJet(
            tau=0.3,
            H_normal_s=2.4e-18,
            dH_normal_s_dtau=-0.07e-18,
            derivative_side=DerivativeSide.INTERIOR,
            coordinate_sha256=H3,
            provenance=HashRef("normal-H", H2),
        ),
        e_rest=e_rest,
        w_rest=w_rest,
        authority=rate_dual.RateDualAuthority.frozen_project_authority(),
    )
    meta = out.authority_metadata()
    assert meta["coordinate_sha256"] == H3
    assert meta["electron_binding_sha256"] == H4
    assert meta["electron_schedule_payload_sha256"] == H1
    assert meta["electron_closure"] == "independent-electron-test-field"
    assert meta["hubble_provenance"] == {
        "source_id": "normal-H",
        "source_sha256": H2,
    }
    assert meta["derivative_side"] == "interior"
    assert out.proper_density_m3 == pytest.approx(4.2)
    assert out.dproper_density_dtau == pytest.approx(0.11)
    assert out.H_normal_s == pytest.approx(2.4e-18)
    assert out.dH_normal_s_dtau == pytest.approx(-0.07e-18)


def test_collision_off_receipt_retains_vacuum_reason_and_unpromoted_boundaries():
    e_rest, w_rest = lebedev26()
    state = CollisionOff("exact-vacuum", H1)
    binding = ElectronBindingCertificate(
        state=state,
        jet=None,
        coordinate_sha256=H3,
        binding_sha256=H4,
        metadata={"direction_dependent_rate_bound": False},
    )
    out = rate_dual.bind_direction_dependent_rate_dual(
        binding,
        rate_dual.NormalHubbleRateJet(
            tau=0.3,
            H_normal_s=2.0e-18,
            dH_normal_s_dtau=0.0,
            derivative_side=DerivativeSide.INTERIOR,
            coordinate_sha256=H3,
            provenance=HashRef("normal-H", H2),
        ),
        e_rest=e_rest,
        w_rest=w_rest,
        authority=rate_dual.RateDualAuthority.frozen_project_authority(),
    )
    meta = out.authority_metadata()
    assert out.tau == pytest.approx(0.3)
    assert out.derivative_side is DerivativeSide.INTERIOR
    assert meta["collision_off_reason"] == "exact-vacuum"
    assert meta["coordinate_sha256"] == H3
    assert meta["electron_binding_sha256"] == H4
    assert meta["hubble_provenance"]["source_sha256"] == H2
    assert meta["authority_row_promoted"] is False
    assert meta["production_runtime_wired"] is False
