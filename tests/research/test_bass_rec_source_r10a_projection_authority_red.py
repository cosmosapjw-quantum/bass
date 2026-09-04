from __future__ import annotations

from dataclasses import fields
from fractions import Fraction
import math
import unittest

from bianchi.source_adapters import SourceTimeBasis
from bianchi.source_authority import SourceAuthorityBundle, SourceFrequencyKind
import bianchi.source_parity as parity


_SHA_PARENT = "a" * 64
_SHA_GRID = "1" * 64
_SHA_PSTF = "2" * 64


def _bundle(*, eta: float = 3.0, kappa: float = 2.0) -> SourceAuthorityBundle:
    return SourceAuthorityBundle.constant_pair(
        eta_s_inv=eta,
        kappa_s_inv=kappa,
        frame="hydrogen_orthonormal",
        channel="total_occupation",
        source_sha256="0" * 64,
        frequency_kind=SourceFrequencyKind.POINTWISE_SPECTRAL,
    )


def _coefficients(l_max: int = 2) -> tuple[float, ...]:
    values = [1.5 * math.sqrt(4.0 * math.pi)]
    for ell in range(1, l_max + 1):
        values.append(((-1.0) ** ell) * (ell + 1.0) / 500.0)
        for order in range(1, ell + 1):
            values.append(
                ((-1.0) ** (ell + order))
                * (ell + 2.0 * order + 1.0)
                / 5000.0
            )
            values.append(
                ((-1.0) ** order)
                * (2.0 * ell + order + 1.0)
                / 7000.0
            )
    if len(values) != (l_max + 1) ** 2:
        raise AssertionError("fixture coefficient count is inconsistent")
    return tuple(values)


def _compare_kwargs(*, l_max: int = 2, **overrides: object) -> dict[str, object]:
    values: dict[str, object] = {
        "source": _bundle(),
        "coefficients": _coefficients(l_max),
        "l_out": l_max,
        "l_work": l_max,
        "state_parent_sha256": _SHA_PARENT,
        "grid_representation_sha256": _SHA_GRID,
        "pstf_representation_sha256": _SHA_PSTF,
        "time_basis": SourceTimeBasis.PHYSICAL_TIME,
        "atol": 2.0e-13,
        "rtol": 2.0e-13,
    }
    values.update(overrides)
    return values


class TestR10AProjectionAuthorityExpectedRed(unittest.TestCase):
    def test_01_stale_projection_hash_is_rejected_at_use(self):
        rule = parity.build_gauss_legendre_uniform_phi_quadrature(l_work=2)
        object.__setattr__(rule, "projection_contract_sha256", "f" * 64)
        with self.assertRaises(parity.SourceParityError):
            parity.synthesize_real_spherical_harmonics(
                _coefficients(2), l_max=2, quadrature=rule
            )

    def test_02_same_length_weight_tampering_is_rejected_at_use(self):
        rule = parity.build_gauss_legendre_uniform_phi_quadrature(l_work=2)
        weights = list(rule.mu_weights)
        weights[0] *= 1.01
        object.__setattr__(rule, "mu_weights", tuple(weights))
        with self.assertRaises(parity.SourceParityError):
            parity.project_real_spherical_harmonics(
                (1.0,) * (rule.n_mu * rule.n_phi),
                l_max=2,
                quadrature=rule,
            )

    def test_03_basis_realization_mutation_invalidates_projection(self):
        rule = parity.build_gauss_legendre_uniform_phi_quadrature(l_work=1)
        original = parity._real_harmonic

        def sign_mutated(mode, mu, phi):
            return -original(mode, mu, phi)

        parity._real_harmonic = sign_mutated
        try:
            with self.assertRaises(parity.SourceParityError):
                parity.synthesize_real_spherical_harmonics(
                    _coefficients(1), l_max=1, quadrature=rule
                )
        finally:
            parity._real_harmonic = original

    def test_04_sample_layout_is_explicit(self):
        rule = parity.build_gauss_legendre_uniform_phi_quadrature(l_work=2)
        self.assertEqual(
            getattr(rule, "sample_layout", None),
            "mu_major_phi_minor",
        )

    def test_05_semantic_and_realization_identities_are_separate(self):
        rule = parity.build_gauss_legendre_uniform_phi_quadrature(l_work=2)
        spec = getattr(rule, "projection_spec_sha256", None)
        realization = getattr(rule, "projection_realization_sha256", None)
        self.assertRegex(spec or "", r"\A[0-9a-f]{64}\Z")
        self.assertRegex(realization or "", r"\A[0-9a-f]{64}\Z")
        self.assertNotEqual(spec, realization)

    def test_06_basis_matrix_identity_is_explicit(self):
        rule = parity.build_gauss_legendre_uniform_phi_quadrature(l_work=2)
        identity = getattr(rule, "basis_matrix_sha256", None)
        self.assertRegex(identity or "", r"\A[0-9a-f]{64}\Z")

    def test_07_actual_unit_field_changes_contract_identity(self):
        baseline = parity.compare_constant_pair_grid_and_pstf(**_compare_kwargs())
        wrong_unit = list(parity.unit_field_coefficients(2))
        wrong_unit[0] = 1.0
        mutated = parity.compare_constant_pair_grid_and_pstf(
            **_compare_kwargs(
                unit_field_coefficients=tuple(wrong_unit),
                require_pass=False,
            )
        )
        self.assertNotEqual(
            baseline.contract.contract_sha256,
            mutated.contract.contract_sha256,
        )

    def test_08_time_basis_and_divisor_change_contract_identity(self):
        physical = parity.compare_constant_pair_grid_and_pstf(**_compare_kwargs())
        q_time = parity.compare_constant_pair_grid_and_pstf(
            **_compare_kwargs(
                time_basis=SourceTimeBasis.Q_TIME,
                H_s_inv=4.0,
            )
        )
        self.assertNotEqual(
            physical.contract.contract_sha256,
            q_time.contract.contract_sha256,
        )

    def test_09_contract_constructor_is_factory_only(self):
        contract = parity.compare_constant_pair_grid_and_pstf(
            **_compare_kwargs()
        ).contract
        kwargs = {
            field.name: getattr(contract, field.name)
            for field in fields(parity.SourceParityContract)
        }
        with self.assertRaises(TypeError):
            parity.SourceParityContract(**kwargs)

    def test_10_report_constructor_is_factory_only(self):
        report = parity.compare_constant_pair_grid_and_pstf(**_compare_kwargs())
        kwargs = {
            field.name: getattr(report, field.name)
            for field in fields(parity.SourceParityReport)
        }
        with self.assertRaises(TypeError):
            parity.SourceParityReport(**kwargs)

    def test_11_scaled_tolerance_utilization_is_reported(self):
        report = parity.compare_constant_pair_grid_and_pstf(**_compare_kwargs())
        utilization = getattr(report, "max_tolerance_utilization", None)
        self.assertIsInstance(utilization, float)
        self.assertGreaterEqual(utilization, 0.0)
        self.assertLessEqual(utilization, 1.0)

    def test_12_continuous_positivity_is_not_overclaimed(self):
        report = parity.compare_constant_pair_grid_and_pstf(**_compare_kwargs())
        self.assertIs(
            getattr(report, "continuous_positivity_certified", None),
            False,
        )

    def test_13_rank_above_executed_certificate_fails_closed(self):
        with self.assertRaises(parity.SourceParityError):
            parity.build_gauss_legendre_uniform_phi_quadrature(l_work=9)


class TestR10ASurvivorControls(unittest.TestCase):
    def test_14_current_l2_parity_survives(self):
        report = parity.compare_constant_pair_grid_and_pstf(**_compare_kwargs())
        self.assertTrue(report.pass_parity)
        self.assertLessEqual(report.max_abs_residual, 2.0e-13)

    def test_15_low_modes_match_independent_analytic_formulas(self):
        rule = parity.build_gauss_legendre_uniform_phi_quadrature(l_work=1)
        basis_vectors = (
            (1.0, 0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0, 0.0),
            (0.0, 0.0, 1.0, 0.0),
            (0.0, 0.0, 0.0, 1.0),
        )
        samples = tuple(
            parity.synthesize_real_spherical_harmonics(
                vector, l_max=1, quadrature=rule
            )
            for vector in basis_vectors
        )
        index = 0
        for mu in rule.mu:
            sin_theta = math.sqrt(max(0.0, 1.0 - mu * mu))
            for phi in rule.phi:
                expected = (
                    1.0 / math.sqrt(4.0 * math.pi),
                    math.sqrt(3.0 / (4.0 * math.pi)) * mu,
                    -math.sqrt(3.0 / (4.0 * math.pi))
                    * sin_theta
                    * math.cos(phi),
                    -math.sqrt(3.0 / (4.0 * math.pi))
                    * sin_theta
                    * math.sin(phi),
                )
                for actual_values, target in zip(samples, expected, strict=True):
                    self.assertAlmostEqual(
                        actual_values[index], target, delta=2.0e-15
                    )
                index += 1

    def test_16_exact_affine_projection_linearity_survives(self):
        eta = Fraction(3)
        kappa = Fraction(2)
        chi = kappa - eta
        weights = (Fraction(2, 7), Fraction(-3, 11), Fraction(5, 13))
        unit = (Fraction(1), Fraction(0), Fraction(0))
        field = (Fraction(9, 10), Fraction(1, 5), Fraction(-1, 10))
        projected_source = sum(
            weight * (eta * one - chi * value)
            for weight, one, value in zip(weights, unit, field, strict=True)
        )
        separated = (
            eta
            * sum(
                weight * one
                for weight, one in zip(weights, unit, strict=True)
            )
            - chi
            * sum(
                weight * value
                for weight, value in zip(weights, field, strict=True)
            )
        )
        self.assertEqual(projected_source, separated)


if __name__ == "__main__":
    unittest.main()
