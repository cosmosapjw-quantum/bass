from __future__ import annotations

import importlib
import math
import unittest
from fractions import Fraction

from bianchi.source_adapters import (
    SourceTimeBasis,
    apply_constant_pair_to_full_spectral_grid,
    apply_constant_pair_to_spectral_pstf,
)
from bianchi.source_authority import SourceAuthorityBundle, SourceFrequencyKind


_SHA_PARENT = "a" * 64
_SHA_GRID = "1" * 64
_SHA_PSTF = "2" * 64
_SHA_PROJECTION = "c" * 64


def _bundle(*, eta: float = 3.0, kappa: float = 2.0) -> SourceAuthorityBundle:
    return SourceAuthorityBundle.constant_pair(
        eta_s_inv=eta,
        kappa_s_inv=kappa,
        frame="hydrogen_orthonormal",
        channel="total_occupation",
        source_sha256="0" * 64,
        frequency_kind=SourceFrequencyKind.POINTWISE_SPECTRAL,
    )


def _r8_common(*, representation: str, projection: str = _SHA_PROJECTION):
    return dict(
        state_parent_sha256=_SHA_PARENT,
        representation_sha256=representation,
        projection_contract_sha256=projection,
        time_basis=SourceTimeBasis.PHYSICAL_TIME,
    )


def _fixture_coefficients(l_max: int = 6) -> tuple[float, ...]:
    """Positive nonaxisymmetric real-harmonic fixture in canonical order."""

    values: list[float] = [1.5 * math.sqrt(4.0 * math.pi)]
    for ell in range(1, l_max + 1):
        values.append(((-1.0) ** ell) * (ell + 1.0) / 500.0)
        for m in range(1, ell + 1):
            values.append(
                ((-1.0) ** (ell + m)) * (ell + 2.0 * m + 1.0) / 5000.0
            )
            values.append(((-1.0) ** m) * (2.0 * ell + m + 1.0) / 7000.0)
    if len(values) != (l_max + 1) ** 2:
        raise AssertionError("fixture coefficient count is inconsistent")
    return tuple(values)


class _R9Mixin:
    def parity(self):
        try:
            return importlib.import_module("bianchi.source_parity")
        except ModuleNotFoundError as exc:
            self.fail(
                "R9 expected RED: missing future finite-rank parity module "
                "'bianchi.source_parity'"
            )
            raise AssertionError from exc

    def compare_kwargs(self, module, *, time_basis=None, **overrides):
        values = dict(
            source=_bundle(),
            coefficients=_fixture_coefficients(),
            l_out=6,
            l_work=6,
            state_parent_sha256=_SHA_PARENT,
            grid_representation_sha256=_SHA_GRID,
            pstf_representation_sha256=_SHA_PSTF,
            time_basis=(
                module.SourceTimeBasis.PHYSICAL_TIME
                if time_basis is None
                else time_basis
            ),
            atol=2.0e-13,
            rtol=2.0e-13,
        )
        values.update(overrides)
        return values


class TestR9FiniteRankParityExpectedRed(_R9Mixin, unittest.TestCase):
    def test_01_future_module_exports_typed_parity_contract(self):
        module = self.parity()
        required = {
            "RealSphericalHarmonicConvention",
            "SourceTimeBasis",
            "SphereQuadrature",
            "SourceParityContract",
            "SourceParityError",
            "SourceParityReport",
            "build_gauss_legendre_uniform_phi_quadrature",
            "canonical_real_harmonic_modes",
            "compare_constant_pair_grid_and_pstf",
            "project_real_spherical_harmonics",
            "synthesize_real_spherical_harmonics",
            "unit_field_coefficients",
        }
        self.assertTrue(required.issubset(set(dir(module))))

    def test_02_mode_order_and_unit_field_are_explicit(self):
        module = self.parity()
        modes = module.canonical_real_harmonic_modes(2)
        self.assertEqual(
            modes,
            (
                (0, 0, "m0"),
                (1, 0, "m0"),
                (1, 1, "cos"),
                (1, 1, "sin"),
                (2, 0, "m0"),
                (2, 1, "cos"),
                (2, 1, "sin"),
                (2, 2, "cos"),
                (2, 2, "sin"),
            ),
        )
        unit = module.unit_field_coefficients(2)
        self.assertEqual(len(unit), 9)
        self.assertAlmostEqual(unit[0], math.sqrt(4.0 * math.pi), places=15)
        self.assertTrue(all(value == 0.0 for value in unit[1:]))

    def test_03_quadrature_is_sufficient_and_hash_bound(self):
        module = self.parity()
        quadrature = module.build_gauss_legendre_uniform_phi_quadrature(l_work=6)
        self.assertEqual(quadrature.n_mu, 7)
        self.assertEqual(quadrature.n_phi, 13)
        self.assertEqual(len(quadrature.mu), 7)
        self.assertEqual(len(quadrature.phi), 13)
        self.assertRegex(
            quadrature.projection_contract_sha256,
            r"\A[0-9a-f]{64}\Z",
        )
        repeated = module.build_gauss_legendre_uniform_phi_quadrature(l_work=6)
        changed = module.build_gauss_legendre_uniform_phi_quadrature(l_work=7)
        self.assertEqual(
            repeated.projection_contract_sha256,
            quadrature.projection_contract_sha256,
        )
        self.assertNotEqual(
            changed.projection_contract_sha256,
            quadrature.projection_contract_sha256,
        )

    def test_04_nonaxisymmetric_synthesis_projection_round_trip(self):
        module = self.parity()
        quadrature = module.build_gauss_legendre_uniform_phi_quadrature(l_work=6)
        coefficients = _fixture_coefficients()
        samples = module.synthesize_real_spherical_harmonics(
            coefficients,
            l_max=6,
            quadrature=quadrature,
        )
        reconstructed = module.project_real_spherical_harmonics(
            samples,
            l_max=6,
            quadrature=quadrature,
        )
        self.assertEqual(len(samples), 7 * 13)
        self.assertGreater(min(samples), 0.0)
        for actual, expected in zip(reconstructed, coefficients, strict=True):
            self.assertAlmostEqual(actual, expected, delta=2.0e-13)

    def test_05_physical_time_parity_holds_across_finite_rank_sweep(self):
        module = self.parity()
        for l_max in (0, 1, 2, 3, 4, 6, 8):
            report = module.compare_constant_pair_grid_and_pstf(
                **self.compare_kwargs(
                    module,
                    coefficients=_fixture_coefficients(l_max),
                    l_out=l_max,
                    l_work=l_max,
                )
            )
            self.assertTrue(report.pass_parity)
            self.assertLessEqual(report.max_abs_residual, 2.0e-13)
            self.assertEqual(report.compared_coefficients, (l_max + 1) ** 2)
            self.assertEqual(
                report.time_basis,
                module.SourceTimeBasis.PHYSICAL_TIME,
            )
            self.assertEqual(
                report.grid_receipt.source_payload_sha256,
                report.pstf_receipt.source_payload_sha256,
            )
            self.assertEqual(
                report.grid_receipt.state_parent_sha256,
                report.pstf_receipt.state_parent_sha256,
            )
            self.assertNotEqual(
                report.grid_receipt.representation_sha256,
                report.pstf_receipt.representation_sha256,
            )

    def test_06_q_time_parity_divides_once(self):
        module = self.parity()
        report = module.compare_constant_pair_grid_and_pstf(
            **self.compare_kwargs(
                module,
                time_basis=module.SourceTimeBasis.Q_TIME,
                H_s_inv=4.0,
            )
        )
        self.assertTrue(report.pass_parity)
        self.assertEqual(report.time_basis, module.SourceTimeBasis.Q_TIME)
        self.assertEqual(report.rate_divisor_hex, float(4.0).hex())

    def test_07_ray_length_parity_keeps_explicit_c(self):
        module = self.parity()
        report = module.compare_constant_pair_grid_and_pstf(
            **self.compare_kwargs(
                module,
                time_basis=module.SourceTimeBasis.RAY_LENGTH,
                c_m_s=299_792_458.0,
            )
        )
        self.assertTrue(report.pass_parity)
        self.assertEqual(report.time_basis, module.SourceTimeBasis.RAY_LENGTH)
        self.assertEqual(
            report.rate_divisor_hex,
            float(299_792_458.0).hex(),
        )

    def test_08_source_off_is_exact_on_both_representations(self):
        module = self.parity()
        report = module.compare_constant_pair_grid_and_pstf(
            **self.compare_kwargs(
                module,
                source=_bundle(eta=0.0, kappa=0.0),
            )
        )
        self.assertTrue(report.pass_parity)
        self.assertTrue(all(value == 0.0 for value in report.grid_projected))
        self.assertTrue(all(value == 0.0 for value in report.pstf_values))

    def test_09_stimulated_growth_branch_is_nonvacuum_sensitive(self):
        module = self.parity()
        report = module.compare_constant_pair_grid_and_pstf(
            **self.compare_kwargs(module)
        )
        self.assertTrue(report.pass_parity)
        self.assertLess(_bundle().chi_affine_s_inv, 0.0)
        self.assertGreater(max(report.pstf_values), 3.0)

    def test_10_underresolved_mu_quadrature_fails_closed(self):
        module = self.parity()
        with self.assertRaises(module.SourceParityError):
            module.SphereQuadrature.create(l_work=6, n_mu=6, n_phi=13)

    def test_11_underresolved_phi_quadrature_fails_closed(self):
        module = self.parity()
        with self.assertRaises(module.SourceParityError):
            module.SphereQuadrature.create(l_work=6, n_mu=7, n_phi=12)

    def test_12_coefficient_layout_mismatch_fails_closed(self):
        module = self.parity()
        with self.assertRaises(module.SourceParityError):
            module.compare_constant_pair_grid_and_pstf(
                **self.compare_kwargs(
                    module,
                    coefficients=_fixture_coefficients()[:-1],
                )
            )

    def test_13_projection_contract_identity_mismatch_fails_closed(self):
        module = self.parity()
        quadrature = module.build_gauss_legendre_uniform_phi_quadrature(l_work=6)
        with self.assertRaises(module.SourceParityError):
            module.compare_constant_pair_grid_and_pstf(
                **self.compare_kwargs(
                    module,
                    projection_contract_sha256="d" * 64,
                    quadrature=quadrature,
                )
            )

    def test_14_normalization_and_sign_mutations_are_detected(self):
        module = self.parity()
        baseline = module.compare_constant_pair_grid_and_pstf(
            **self.compare_kwargs(module)
        )
        wrong_unit = list(module.unit_field_coefficients(6))
        wrong_unit[0] = 1.0
        normalization_mutation = module.compare_constant_pair_grid_and_pstf(
            **self.compare_kwargs(
                module,
                unit_field_coefficients=tuple(wrong_unit),
                require_pass=False,
            )
        )
        source = _bundle()
        coefficients = _fixture_coefficients()
        unit = module.unit_field_coefficients(6)
        sign_mutated_coefficients = tuple(
            source.eta_s_inv * one
            + source.chi_affine_s_inv * coefficient
            for one, coefficient in zip(unit, coefficients, strict=True)
        )
        sign_residual = max(
            abs(grid - mutated)
            for grid, mutated in zip(
                baseline.grid_projected,
                sign_mutated_coefficients,
                strict=True,
            )
        )
        self.assertTrue(baseline.pass_parity)
        self.assertFalse(normalization_mutation.pass_parity)
        self.assertGreater(sign_residual, 1.0)
        self.assertNotEqual(
            baseline.report_sha256,
            normalization_mutation.report_sha256,
        )


class TestR9SurvivorControls(unittest.TestCase):
    def test_15_exact_affine_projection_linearity_control(self):
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

    def test_16_r8_constant_pair_adapter_survives(self):
        grid = apply_constant_pair_to_full_spectral_grid(
            _bundle(),
            (0.0, 1.0, 5.0),
            **_r8_common(representation=_SHA_GRID),
        )
        pstf = apply_constant_pair_to_spectral_pstf(
            _bundle(),
            (0.9, 0.2, -0.1, 0.05),
            unit_field_coefficients=(1.0, 0.0, 0.0, 0.0),
            l_out=3,
            l_work=3,
            **_r8_common(representation=_SHA_PSTF),
        )
        self.assertEqual(grid.values, (3.0, 4.0, 8.0))
        for actual, expected in zip(
            pstf.values,
            (3.9, 0.2, -0.1, 0.05),
            strict=True,
        ):
            self.assertAlmostEqual(actual, expected, places=15)


if __name__ == "__main__":
    unittest.main()
