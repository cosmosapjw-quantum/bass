from __future__ import annotations

import importlib
import math
import unittest
from fractions import Fraction

from bianchi.source_authority import (
    SourceAuthorityBundle,
    SourceFrequencyKind,
    SourceStateKind,
)


_SHA_A = "a" * 64
_SHA_B = "b" * 64
_SHA_C = "c" * 64

# Exact low-order Legendre polynomials in ascending monomial order.
_P = (
    (Fraction(1),),
    (Fraction(0), Fraction(1)),
    (Fraction(-1, 2), Fraction(0), Fraction(3, 2)),
    (Fraction(0), Fraction(-3, 2), Fraction(0), Fraction(5, 2)),
)


def _poly_add(a, b):
    n = max(len(a), len(b))
    out = [Fraction(0)] * n
    for i, value in enumerate(a):
        out[i] += value
    for i, value in enumerate(b):
        out[i] += value
    return tuple(out)


def _poly_scale(a, scalar):
    return tuple(Fraction(scalar) * value for value in a)


def _poly_mul(a, b):
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return tuple(out)


def _poly_integral_minus_one_to_one(a):
    total = Fraction(0)
    for power, value in enumerate(a):
        if power % 2 == 0:
            total += value * Fraction(2, power + 1)
    return total


def _legendre_reconstruct(coefficients):
    poly = (Fraction(0),)
    for coefficient, basis in zip(coefficients, _P, strict=True):
        poly = _poly_add(poly, _poly_scale(basis, coefficient))
    return poly


def _legendre_project(poly):
    coefficients = []
    for ell, basis in enumerate(_P):
        inner = _poly_integral_minus_one_to_one(_poly_mul(poly, basis))
        coefficients.append(Fraction(2 * ell + 1, 2) * inner)
    return tuple(coefficients)


def _legendre_value(ell, x):
    if ell == 0:
        return 1.0
    if ell == 1:
        return x
    if ell == 2:
        return 0.5 * (3.0 * x * x - 1.0)
    if ell == 3:
        return 0.5 * (5.0 * x * x * x - 3.0 * x)
    raise ValueError(ell)


def _gauss_legendre_four():
    root = math.sqrt(6.0 / 5.0)
    x_inner = math.sqrt((3.0 - 2.0 * root) / 7.0)
    x_outer = math.sqrt((3.0 + 2.0 * root) / 7.0)
    w_inner = (18.0 + math.sqrt(30.0)) / 36.0
    w_outer = (18.0 - math.sqrt(30.0)) / 36.0
    return (
        (-x_outer, w_outer),
        (-x_inner, w_inner),
        (x_inner, w_inner),
        (x_outer, w_outer),
    )


def _project_samples(samples, ell_max=3):
    out = []
    for ell in range(ell_max + 1):
        integral = sum(
            weight * value * _legendre_value(ell, mu)
            for (mu, weight), value in zip(
                _gauss_legendre_four(), samples, strict=True
            )
        )
        out.append((2 * ell + 1) * integral / 2.0)
    return tuple(out)


def _bundle():
    return SourceAuthorityBundle.constant_pair(
        eta_s_inv=3.0,
        kappa_s_inv=2.0,
        frame="hydrogen_orthonormal",
        channel="total_occupation",
        source_sha256="0" * 64,
        frequency_kind=SourceFrequencyKind.POINTWISE_SPECTRAL,
    )


class _R7Mixin:
    def adapter(self):
        try:
            return importlib.import_module("bianchi.source_adapters")
        except ModuleNotFoundError as exc:
            self.fail(
                "R7 expected RED: missing future receiving module "
                "'bianchi.source_adapters'"
            )
            raise AssertionError from exc

    def grid_kwargs(self, module, **overrides):
        values = dict(
            state_parent_sha256=_SHA_A,
            representation_sha256=_SHA_B,
            projection_contract_sha256=_SHA_C,
            time_basis=module.SourceTimeBasis.PHYSICAL_TIME,
        )
        values.update(overrides)
        return values


class TestR7DualAdapterExpectedRed(_R7Mixin, unittest.TestCase):
    def test_01_future_module_exports_typed_contract(self):
        module = self.adapter()
        required = {
            "SourceTimeBasis",
            "SourceAdapterError",
            "SourceApplicationReceipt",
            "SourceApplicationResult",
            "apply_constant_pair_to_full_spectral_grid",
            "apply_constant_pair_to_spectral_pstf",
            "require_dual_adapter_target",
        }
        self.assertTrue(required.issubset(set(dir(module))))

    def test_02_full_spectral_grid_uses_exact_bosonic_source(self):
        module = self.adapter()
        result = module.apply_constant_pair_to_full_spectral_grid(
            _bundle(),
            (0.0, 1.0, 5.0),
            **self.grid_kwargs(module),
        )
        self.assertEqual(result.values, (3.0, 4.0, 8.0))
        self.assertEqual(
            result.receipt.state_kind,
            SourceStateKind.FULL_SPECTRAL_GRID,
        )
        self.assertEqual(
            result.receipt.source_payload_sha256,
            _bundle().payload_sha256,
        )

    def test_03_spectral_pstf_uses_explicit_unit_field_coefficients(self):
        module = self.adapter()
        coefficients = (0.9, 0.2, -0.1, 0.05)
        unit = (1.0, 0.0, 0.0, 0.0)
        result = module.apply_constant_pair_to_spectral_pstf(
            _bundle(),
            coefficients,
            unit_field_coefficients=unit,
            l_out=3,
            l_work=3,
            **self.grid_kwargs(module),
        )
        self.assertEqual(
            result.receipt.state_kind,
            SourceStateKind.FINITE_SPECTRAL_PSTF,
        )
        for actual, expected in zip(
            result.values,
            (3.9, 0.2, -0.1, 0.05),
            strict=True,
        ):
            self.assertAlmostEqual(actual, expected, places=15)

    def test_04_grid_projection_commutes_with_constant_pair_pstf_action(self):
        module = self.adapter()
        coefficients = (0.9, 0.2, -0.1, 0.05)
        unit = (1.0, 0.0, 0.0, 0.0)

        samples = tuple(
            sum(
                coefficient * _legendre_value(ell, mu)
                for ell, coefficient in enumerate(coefficients)
            )
            for mu, _ in _gauss_legendre_four()
        )
        grid = module.apply_constant_pair_to_full_spectral_grid(
            _bundle(),
            samples,
            **self.grid_kwargs(module),
        )
        projected_grid_source = _project_samples(grid.values)

        pstf = module.apply_constant_pair_to_spectral_pstf(
            _bundle(),
            coefficients,
            unit_field_coefficients=unit,
            l_out=3,
            l_work=3,
            **self.grid_kwargs(module),
        )
        for actual, expected in zip(
            projected_grid_source,
            pstf.values,
            strict=True,
        ):
            self.assertAlmostEqual(actual, expected, places=13)

    def test_05_receipts_bind_same_source_parent_and_projection_contract(self):
        module = self.adapter()
        grid = module.apply_constant_pair_to_full_spectral_grid(
            _bundle(),
            (0.0, 1.0),
            **self.grid_kwargs(
                module,
                representation_sha256="1" * 64,
            ),
        )
        pstf = module.apply_constant_pair_to_spectral_pstf(
            _bundle(),
            (1.0, 0.1),
            unit_field_coefficients=(1.0, 0.0),
            l_out=1,
            l_work=1,
            **self.grid_kwargs(
                module,
                representation_sha256="2" * 64,
            ),
        )
        self.assertEqual(
            grid.receipt.source_payload_sha256,
            pstf.receipt.source_payload_sha256,
        )
        self.assertEqual(
            grid.receipt.state_parent_sha256,
            pstf.receipt.state_parent_sha256,
        )
        self.assertEqual(
            grid.receipt.projection_contract_sha256,
            pstf.receipt.projection_contract_sha256,
        )
        self.assertNotEqual(
            grid.receipt.representation_sha256,
            pstf.receipt.representation_sha256,
        )

    def test_06_q_time_action_divides_physical_rates_exactly_once(self):
        module = self.adapter()
        result = module.apply_constant_pair_to_full_spectral_grid(
            _bundle(),
            (5.0,),
            **self.grid_kwargs(
                module,
                time_basis=module.SourceTimeBasis.Q_TIME,
                H_s_inv=4.0,
            ),
        )
        self.assertEqual(result.values, (2.0,))
        self.assertEqual(
            result.receipt.time_basis,
            module.SourceTimeBasis.Q_TIME,
        )

    def test_07_ray_length_action_retains_explicit_speed_of_light(self):
        module = self.adapter()
        result = module.apply_constant_pair_to_full_spectral_grid(
            _bundle(),
            (5.0,),
            **self.grid_kwargs(
                module,
                time_basis=module.SourceTimeBasis.RAY_LENGTH,
                c_m_s=2.0,
            ),
        )
        self.assertEqual(result.values, (4.0,))
        self.assertEqual(
            result.receipt.time_basis,
            module.SourceTimeBasis.RAY_LENGTH,
        )

    def test_08_rank_and_integrated_state_firewalls_are_fail_closed(self):
        module = self.adapter()
        for state_kind in (
            SourceStateKind.RADIAL_INTEGRATED_ANGULAR_GRID,
            SourceStateKind.FINITE_INTEGRATED_J_HIERARCHY,
        ):
            with self.subTest(state_kind=state_kind):
                with self.assertRaises(module.SourceAdapterError):
                    module.require_dual_adapter_target(state_kind)

        with self.assertRaises(module.SourceAdapterError):
            module.apply_constant_pair_to_spectral_pstf(
                _bundle(),
                (1.0, 0.1, 0.01),
                unit_field_coefficients=(1.0, 0.0, 0.0),
                l_out=2,
                l_work=1,
                **self.grid_kwargs(module),
            )

    def test_09_missing_or_ambiguous_identity_and_time_inputs_are_rejected(self):
        module = self.adapter()
        with self.assertRaises(module.SourceAdapterError):
            module.apply_constant_pair_to_full_spectral_grid(
                _bundle(),
                (1.0,),
                state_parent_sha256="",
                representation_sha256=_SHA_B,
                projection_contract_sha256=_SHA_C,
                time_basis=module.SourceTimeBasis.PHYSICAL_TIME,
            )
        with self.assertRaises(module.SourceAdapterError):
            module.apply_constant_pair_to_full_spectral_grid(
                _bundle(),
                (1.0,),
                **self.grid_kwargs(
                    module,
                    time_basis=module.SourceTimeBasis.Q_TIME,
                ),
            )
        with self.assertRaises(module.SourceAdapterError):
            module.apply_constant_pair_to_full_spectral_grid(
                _bundle(),
                (1.0,),
                **self.grid_kwargs(
                    module,
                    time_basis=module.SourceTimeBasis.PHYSICAL_TIME,
                    H_s_inv=1.0,
                ),
            )

    def test_10_receipt_output_identity_is_deterministic_and_input_sensitive(self):
        module = self.adapter()
        kwargs = self.grid_kwargs(module)
        first = module.apply_constant_pair_to_full_spectral_grid(
            _bundle(),
            (0.0, 1.0, 5.0),
            **kwargs,
        )
        second = module.apply_constant_pair_to_full_spectral_grid(
            _bundle(),
            (0.0, 1.0, 5.0),
            **kwargs,
        )
        changed = module.apply_constant_pair_to_full_spectral_grid(
            _bundle(),
            (0.0, 1.0, 5.0),
            **self.grid_kwargs(
                module,
                projection_contract_sha256="d" * 64,
            ),
        )
        self.assertEqual(
            first.receipt.output_sha256,
            second.receipt.output_sha256,
        )
        self.assertNotEqual(
            first.receipt.output_sha256,
            changed.receipt.output_sha256,
        )


class TestR7SurvivorControls(unittest.TestCase):
    def test_11_r6_source_authority_survives_unchanged(self):
        bundle = _bundle()
        self.assertEqual(bundle.chi_affine_s_inv, -1.0)
        self.assertEqual(bundle.pointwise_action(5.0), 8.0)
        self.assertEqual(bundle.rates_per_tau(H_s_inv=4.0), (0.75, 0.5))

    def test_12_exact_legendre_projection_control(self):
        coefficients = (
            Fraction(9, 10),
            Fraction(1, 5),
            Fraction(-1, 10),
            Fraction(1, 20),
        )
        polynomial = _legendre_reconstruct(coefficients)
        self.assertEqual(_legendre_project(polynomial), coefficients)


if __name__ == "__main__":
    unittest.main(verbosity=2)
