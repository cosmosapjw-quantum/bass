from __future__ import annotations

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


def _fixture(l_max: int = 2) -> tuple[float, ...]:
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


def _compare_kwargs(
    *,
    coefficients: tuple[float, ...] | None = None,
    l_max: int = 2,
    time_basis: SourceTimeBasis = SourceTimeBasis.PHYSICAL_TIME,
    **overrides: object,
) -> dict[str, object]:
    values: dict[str, object] = {
        "source": _bundle(),
        "coefficients": _fixture(l_max) if coefficients is None else coefficients,
        "l_out": l_max,
        "l_work": l_max,
        "state_parent_sha256": _SHA_PARENT,
        "grid_representation_sha256": _SHA_GRID,
        "pstf_representation_sha256": _SHA_PSTF,
        "time_basis": time_basis,
        "atol": 2.0e-13,
        "rtol": 2.0e-13,
    }
    values.update(overrides)
    return values


class TestR10AAuthorityHardeningExpectedRed(unittest.TestCase):
    def test_01_contract_is_factory_only_and_cannot_be_forged(self):
        with self.assertRaises(TypeError):
            parity.SourceParityContract(
                contract_schema="forged",
                convention=(
                    parity.RealSphericalHarmonicConvention
                    .ORTHONORMAL_DOMEGA_CONDON_SHORTLEY
                ),
                l_out=0,
                l_work=0,
                compared_coefficients=1,
                projection_contract_sha256="0" * 64,
                state_parent_sha256="a" * 64,
                grid_representation_sha256="1" * 64,
                pstf_representation_sha256="2" * 64,
                source_payload_sha256="3" * 64,
                atol_hex=0.0.hex(),
                rtol_hex=0.0.hex(),
                contract_sha256="4" * 64,
            )

    def test_02_report_is_factory_only_and_cannot_be_forged(self):
        baseline = parity.compare_constant_pair_grid_and_pstf(
            **_compare_kwargs()
        )
        with self.assertRaises(TypeError):
            parity.SourceParityReport(
                report_schema="forged",
                contract=baseline.contract,
                time_basis=baseline.time_basis,
                rate_divisor_hex=baseline.rate_divisor_hex,
                compared_coefficients=baseline.compared_coefficients,
                grid_projected=baseline.grid_projected,
                pstf_values=baseline.pstf_values,
                residuals=baseline.residuals,
                max_abs_residual=0.0,
                max_rel_residual=0.0,
                pass_parity=True,
                grid_receipt=baseline.grid_receipt,
                pstf_receipt=baseline.pstf_receipt,
                report_sha256="f" * 64,
            )

    def test_03_mutated_quadrature_weights_are_rejected_at_use_time(self):
        quadrature = parity.build_gauss_legendre_uniform_phi_quadrature(
            l_work=2
        )
        mutated = tuple(
            -abs(value) if index == 0 else value
            for index, value in enumerate(quadrature.mu_weights)
        )
        object.__setattr__(quadrature, "mu_weights", mutated)
        samples = parity.synthesize_real_spherical_harmonics(
            _fixture(),
            l_max=2,
            quadrature=quadrature,
        )
        with self.assertRaises(parity.SourceParityError):
            parity.project_real_spherical_harmonics(
                samples,
                l_max=2,
                quadrature=quadrature,
            )

    def test_04_stale_quadrature_identity_is_rejected_after_node_mutation(self):
        quadrature = parity.build_gauss_legendre_uniform_phi_quadrature(
            l_work=2
        )
        original_identity = quadrature.projection_contract_sha256
        changed_mu = list(quadrature.mu)
        changed_mu[0] = 0.5 * changed_mu[0]
        object.__setattr__(quadrature, "mu", tuple(changed_mu))
        self.assertEqual(
            quadrature.projection_contract_sha256,
            original_identity,
        )
        with self.assertRaises(parity.SourceParityError):
            parity.synthesize_real_spherical_harmonics(
                _fixture(),
                l_max=2,
                quadrature=quadrature,
            )

    def test_05_projection_contract_binds_basis_realization(self):
        quadrature = parity.build_gauss_legendre_uniform_phi_quadrature(
            l_work=2
        )
        realization = getattr(
            quadrature,
            "basis_realization_sha256",
            None,
        )
        self.assertIsInstance(realization, str)
        self.assertRegex(realization, r"\A[0-9a-f]{64}\Z")

    def test_06_projection_contract_exposes_sample_layout(self):
        quadrature = parity.build_gauss_legendre_uniform_phi_quadrature(
            l_work=2
        )
        self.assertEqual(
            getattr(quadrature, "sample_layout", None),
            "mu_major_phi_minor",
        )

    def test_07_contract_identity_changes_with_time_basis_and_divisor(self):
        physical = parity.compare_constant_pair_grid_and_pstf(
            **_compare_kwargs()
        )
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

    def test_08_contract_identity_changes_with_unit_field_realization(self):
        baseline = parity.compare_constant_pair_grid_and_pstf(
            **_compare_kwargs()
        )
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

    def test_09_report_states_sampled_not_continuous_positivity_scope(self):
        coefficients = (
            0.008,
            0.0,
            0.0,
            0.0,
            -0.005,
            0.0,
            0.0,
            0.0,
            0.0,
        )
        quadrature = parity.build_gauss_legendre_uniform_phi_quadrature(
            l_work=2
        )
        samples = parity.synthesize_real_spherical_harmonics(
            coefficients,
            l_max=2,
            quadrature=quadrature,
        )
        y00 = 1.0 / math.sqrt(4.0 * math.pi)
        y20_at_mu_099 = math.sqrt(5.0 / (16.0 * math.pi)) * (
            3.0 * 0.99**2 - 1.0
        )
        off_node_value = coefficients[0] * y00 + coefficients[4] * y20_at_mu_099
        self.assertGreater(min(samples), 9.0e-4)
        self.assertLess(off_node_value, -7.0e-4)

        report = parity.compare_constant_pair_grid_and_pstf(
            **_compare_kwargs(
                coefficients=coefficients,
                l_max=2,
                quadrature=quadrature,
            )
        )
        self.assertEqual(
            getattr(report, "positivity_scope", None),
            "quadrature_nodes_only",
        )
        self.assertFalse(
            getattr(report, "continuous_positivity_certified", True)
        )

    def test_10_report_exposes_acceptance_scaled_residual(self):
        report = parity.compare_constant_pair_grid_and_pstf(
            **_compare_kwargs()
        )
        scaled = getattr(report, "max_scaled_residual", None)
        self.assertIsNotNone(scaled)
        self.assertLessEqual(scaled, 1.0)


class TestR10ASurvivorControls(unittest.TestCase):
    def test_11_r10_baseline_parity_survives(self):
        report = parity.compare_constant_pair_grid_and_pstf(
            **_compare_kwargs(l_max=4)
        )
        self.assertTrue(report.pass_parity)
        self.assertLessEqual(report.max_abs_residual, 2.0e-13)

    def test_12_unit_field_and_low_order_harmonics_match_analytic_values(self):
        quadrature = parity.build_gauss_legendre_uniform_phi_quadrature(
            l_work=1
        )
        unit_samples = parity.synthesize_real_spherical_harmonics(
            parity.unit_field_coefficients(1),
            l_max=1,
            quadrature=quadrature,
        )
        self.assertTrue(
            all(abs(value - 1.0) <= 2.0e-15 for value in unit_samples)
        )

        y10_coefficients = (0.0, 1.0, 0.0, 0.0)
        y10_samples = parity.synthesize_real_spherical_harmonics(
            y10_coefficients,
            l_max=1,
            quadrature=quadrature,
        )
        expected_by_mu = tuple(
            math.sqrt(3.0 / (4.0 * math.pi)) * mu
            for mu in quadrature.mu
            for _ in quadrature.phi
        )
        for actual, expected in zip(
            y10_samples,
            expected_by_mu,
            strict=True,
        ):
            self.assertAlmostEqual(actual, expected, delta=2.0e-15)

    def test_13_source_off_remains_exact(self):
        report = parity.compare_constant_pair_grid_and_pstf(
            **_compare_kwargs(
                source=_bundle(eta=0.0, kappa=0.0),
            )
        )
        self.assertTrue(report.pass_parity)
        self.assertTrue(all(value == 0.0 for value in report.grid_projected))
        self.assertTrue(all(value == 0.0 for value in report.pstf_values))


if __name__ == "__main__":
    unittest.main()
