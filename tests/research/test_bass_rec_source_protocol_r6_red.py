from __future__ import annotations

import math
import re
import unittest

import bianchi.source_authority as source_authority


_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


class TestBassRecSourceProtocolR6Red(unittest.TestCase):
    """Hardening requirements that the exact R5 candidate does not yet satisfy."""

    def make_pair(
        self,
        *,
        eta_s_inv: float = 3.0,
        kappa_s_inv: float = 2.0,
        frequency_kind=None,
    ):
        if frequency_kind is None:
            frequency_kind = source_authority.SourceFrequencyKind.POINTWISE_SPECTRAL
        return source_authority.SourceAuthorityBundle.constant_pair(
            eta_s_inv=eta_s_inv,
            kappa_s_inv=kappa_s_inv,
            frame="hydrogen_orthonormal",
            channel="total_occupation",
            source_sha256="0" * 64,
            frequency_kind=frequency_kind,
        )

    def test_direct_dataclass_constructor_cannot_bypass_validation_or_hash(self):
        with self.assertRaises(TypeError):
            source_authority.SourceAuthorityBundle(
                eta_s_inv=-1.0,
                kappa_s_inv=math.nan,
                frame=" ",
                channel=" ",
                source_sha256="not-a-sha256",
                frequency_kind="pointwise_spectral",
                payload_sha256="f" * 64,
            )

    def test_signed_zero_has_one_physical_and_payload_identity(self):
        plus = self.make_pair(eta_s_inv=0.0, kappa_s_inv=0.0)
        minus = self.make_pair(eta_s_inv=-0.0, kappa_s_inv=-0.0)
        self.assertEqual(minus.eta_s_inv, 0.0)
        self.assertEqual(minus.kappa_s_inv, 0.0)
        self.assertEqual(math.copysign(1.0, minus.eta_s_inv), 1.0)
        self.assertEqual(math.copysign(1.0, minus.kappa_s_inv), 1.0)
        self.assertEqual(plus.payload_sha256, minus.payload_sha256)

    def test_constant_pair_is_explicitly_photon_boson_and_schema_v2(self):
        self.assertTrue(hasattr(source_authority, "SourceSpecies"))
        self.assertTrue(hasattr(source_authority, "SourceStatistics"))
        bundle = self.make_pair()
        self.assertIs(bundle.species, source_authority.SourceSpecies.PHOTON)
        self.assertIs(bundle.statistics, source_authority.SourceStatistics.BOSON)
        self.assertEqual(bundle.payload_schema, "bass.source_authority.constant_pair.v2")
        self.assertRegex(bundle.payload_sha256, _SHA256)

    def test_constant_pair_cannot_masquerade_as_integrated_witness(self):
        with self.assertRaises(source_authority.SourceRepresentationError):
            self.make_pair(
                frequency_kind=(
                    source_authority.SourceFrequencyKind.SOURCE_INTEGRATED_WITNESS
                )
            )

    def test_integrated_source_is_rejected_without_a_moment_map_binding(self):
        with self.assertRaises(source_authority.SourceRepresentationError):
            source_authority.require_source_representation_compatibility(
                source_authority.SourceFrequencyKind.SOURCE_INTEGRATED_WITNESS,
                source_authority.SourceStateKind.RADIAL_INTEGRATED_ANGULAR_GRID,
            )

    def test_integrated_moment_map_binding_is_typed_hashed_and_target_specific(self):
        self.assertTrue(hasattr(source_authority, "IntegratedMomentMapBinding"))
        binding_type = source_authority.IntegratedMomentMapBinding
        binding = binding_type.create(
            target_state_kind=(
                source_authority.SourceStateKind.RADIAL_INTEGRATED_ANGULAR_GRID
            ),
            moment_map_sha256="1" * 64,
            radial_weight_family_sha256="2" * 64,
            source_sha256="3" * 64,
        )
        self.assertRegex(binding.binding_sha256, _SHA256)
        self.assertIsNone(
            source_authority.require_source_representation_compatibility(
                source_authority.SourceFrequencyKind.SOURCE_INTEGRATED_WITNESS,
                source_authority.SourceStateKind.RADIAL_INTEGRATED_ANGULAR_GRID,
                integrated_binding=binding,
            )
        )
        with self.assertRaises(source_authority.SourceRepresentationError):
            source_authority.require_source_representation_compatibility(
                source_authority.SourceFrequencyKind.SOURCE_INTEGRATED_WITNESS,
                source_authority.SourceStateKind.FINITE_INTEGRATED_J_HIERARCHY,
                integrated_binding=binding,
            )

    def test_pointwise_action_fails_closed_on_binary64_overflow(self):
        self.assertTrue(hasattr(source_authority, "SourceArithmeticError"))
        bundle = self.make_pair(eta_s_inv=1.0e308, kappa_s_inv=0.0)
        with self.assertRaises(source_authority.SourceArithmeticError):
            bundle.pointwise_action(1.0e308)

    def test_q_time_conversion_fails_closed_on_binary64_overflow(self):
        self.assertTrue(hasattr(source_authority, "SourceArithmeticError"))
        bundle = self.make_pair(eta_s_inv=1.0e308, kappa_s_inv=0.0)
        with self.assertRaises(source_authority.SourceArithmeticError):
            bundle.rates_per_tau(H_s_inv=1.0e-308)

    def test_existing_source_off_and_negative_chi_controls_survive(self):
        source_off = self.make_pair(eta_s_inv=0.0, kappa_s_inv=0.0)
        self.assertEqual(source_off.pointwise_action(10.0), 0.0)
        stimulated = self.make_pair(eta_s_inv=3.0, kappa_s_inv=2.0)
        self.assertEqual(stimulated.chi_affine_s_inv, -1.0)
        self.assertEqual(stimulated.pointwise_action(5.0), 8.0)

    def test_expanding_q_time_domain_remains_explicit(self):
        bundle = self.make_pair()
        for invalid in (0.0, -1.0, math.inf, math.nan):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    bundle.rates_per_tau(H_s_inv=invalid)


if __name__ == "__main__":
    unittest.main(verbosity=2)
