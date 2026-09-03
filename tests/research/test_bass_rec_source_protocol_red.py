from __future__ import annotations

import math
import re
import unittest

# EXPECTED RED at the pinned parent:
# ModuleNotFoundError: No module named 'bianchi.source_authority'
from bianchi.source_authority import (  # type: ignore[import-not-found]
    SourceAuthorityBundle,
    SourceFrequencyKind,
    SourceRepresentationError,
    SourceStateKind,
    require_source_representation_compatibility,
    required_work_rank,
    validate_work_rank,
)


_SHA256 = re.compile(r"[0-9a-f]{64}")


class TestBassRecSourceProtocolRed(unittest.TestCase):
    def make_bundle(self):
        return SourceAuthorityBundle.constant_pair(
            eta_s_inv=3.0,
            kappa_s_inv=2.0,
            frame="hydrogen_orthonormal",
            channel="total_occupation",
            source_sha256="0" * 64,
            frequency_kind=SourceFrequencyKind.POINTWISE_SPECTRAL,
        )

    def test_positive_pair_is_primary_and_net_affine_rate_is_signed(self):
        bundle = self.make_bundle()
        self.assertEqual(bundle.eta_s_inv, 3.0)
        self.assertEqual(bundle.kappa_s_inv, 2.0)
        self.assertEqual(bundle.chi_affine_s_inv, -1.0)
        self.assertRegex(bundle.payload_sha256, _SHA256)

    def test_physical_time_to_q_time_conversion_is_explicit_and_exact(self):
        bundle = self.make_bundle()
        eta_tau, kappa_tau = bundle.rates_per_tau(H_s_inv=4.0)
        self.assertEqual(eta_tau, 0.75)
        self.assertEqual(kappa_tau, 0.5)
        self.assertEqual(kappa_tau - eta_tau, bundle.chi_affine_s_inv / 4.0)
        for invalid in (0.0, -1.0, math.inf, math.nan):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    bundle.rates_per_tau(H_s_inv=invalid)

    def test_constant_pair_pointwise_action_keeps_stimulated_emission(self):
        bundle = self.make_bundle()
        f = 5.0
        expected = bundle.eta_s_inv * (1.0 + f) - bundle.kappa_s_inv * f
        self.assertEqual(bundle.pointwise_action(f), expected)
        self.assertEqual(expected, 8.0)
        with self.assertRaises(ValueError):
            bundle.pointwise_action(-1.0)

    def test_negative_or_nonfinite_primary_rates_are_rejected(self):
        kwargs = dict(
            frame="hydrogen_orthonormal",
            channel="total_occupation",
            source_sha256="0" * 64,
            frequency_kind=SourceFrequencyKind.POINTWISE_SPECTRAL,
        )
        for eta, kappa in ((-1.0, 0.0), (0.0, -1.0), (math.nan, 1.0), (1.0, math.inf)):
            with self.subTest(eta=eta, kappa=kappa):
                with self.assertRaises(ValueError):
                    SourceAuthorityBundle.constant_pair(
                        eta_s_inv=eta,
                        kappa_s_inv=kappa,
                        **kwargs,
                    )

    def test_source_payload_requires_canonical_sha256_and_named_frame_channel(self):
        with self.assertRaises(ValueError):
            SourceAuthorityBundle.constant_pair(
                eta_s_inv=1.0,
                kappa_s_inv=1.0,
                frame="",
                channel="total_occupation",
                source_sha256="0" * 64,
                frequency_kind=SourceFrequencyKind.POINTWISE_SPECTRAL,
            )
        with self.assertRaises(ValueError):
            SourceAuthorityBundle.constant_pair(
                eta_s_inv=1.0,
                kappa_s_inv=1.0,
                frame="hydrogen_orthonormal",
                channel="",
                source_sha256="0" * 64,
                frequency_kind=SourceFrequencyKind.POINTWISE_SPECTRAL,
            )
        with self.assertRaises(ValueError):
            SourceAuthorityBundle.constant_pair(
                eta_s_inv=1.0,
                kappa_s_inv=1.0,
                frame="hydrogen_orthonormal",
                channel="total_occupation",
                source_sha256="not-a-sha256",
                frequency_kind=SourceFrequencyKind.POINTWISE_SPECTRAL,
            )

    def test_state_representations_are_distinct_typed_objects(self):
        values = {member.value for member in SourceStateKind}
        self.assertEqual(
            values,
            {
                "full_spectral_grid",
                "radial_integrated_angular_grid",
                "finite_spectral_pstf",
                "finite_integrated_j_hierarchy",
            },
        )

    def test_pointwise_spectral_source_is_rejected_for_integrated_states(self):
        for state_kind in (
            SourceStateKind.RADIAL_INTEGRATED_ANGULAR_GRID,
            SourceStateKind.FINITE_INTEGRATED_J_HIERARCHY,
        ):
            with self.subTest(state_kind=state_kind):
                with self.assertRaises(SourceRepresentationError):
                    require_source_representation_compatibility(
                        SourceFrequencyKind.POINTWISE_SPECTRAL,
                        state_kind,
                    )

    def test_pointwise_spectral_source_is_admitted_for_full_grid_and_spectral_pstf(self):
        for state_kind in (
            SourceStateKind.FULL_SPECTRAL_GRID,
            SourceStateKind.FINITE_SPECTRAL_PSTF,
        ):
            with self.subTest(state_kind=state_kind):
                self.assertIsNone(
                    require_source_representation_compatibility(
                        SourceFrequencyKind.POINTWISE_SPECTRAL,
                        state_kind,
                    )
                )

    def test_frequency_kinds_remain_distinct_typed_objects_across_protocol_versions(self):
        values = {member.value for member in SourceFrequencyKind}
        self.assertEqual(
            values,
            {
                "pointwise_spectral",
                "source_integrated_witness",
            },
        )
        self.assertIsNot(
            SourceFrequencyKind.POINTWISE_SPECTRAL,
            SourceFrequencyKind.SOURCE_INTEGRATED_WITNESS,
        )

    def test_work_rank_guard_blocks_same_cutoff_aliasing(self):
        self.assertEqual(required_work_rank(l_out=2, l_source=2), 4)
        self.assertEqual(validate_work_rank(l_work=4, l_out=2, l_source=2), 4)
        with self.assertRaisesRegex(ValueError, r"L_work=2.*L_out=2.*L_source=2"):
            validate_work_rank(l_work=2, l_out=2, l_source=2)
        self.assertEqual(required_work_rank(l_out=7, l_source=0), 7)

    def test_rank_inputs_reject_bools_nonintegers_and_negative_values(self):
        for args in (
            (True, 1),
            (1.5, 1),
            (-1, 1),
            (1, -1),
        ):
            with self.subTest(args=args):
                with self.assertRaises((TypeError, ValueError)):
                    required_work_rank(l_out=args[0], l_source=args[1])


if __name__ == "__main__":
    unittest.main(verbosity=2)
