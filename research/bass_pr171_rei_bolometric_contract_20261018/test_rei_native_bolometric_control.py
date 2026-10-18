"""Independent numerical checks for the PR171 BASS--REI bolometric boundary."""
import unittest

from rei_native_bolometric_control import (
    NATIVE_SOURCE_COMMIT, NATIVE_SOURCE_SHA256, NATIVE_TRANSPORT_SHA256,
    angular_fractions, controls, mean_source_energy_ev, same_clock_bolometric_control,
    spectral_cells, transport_mean_energy_ev,
)


class NativeBolometricControlTests(unittest.TestCase):
    def test_immutable_native_identity_is_explicit(self):
        self.assertEqual(NATIVE_SOURCE_COMMIT, "0e25846433170d0f420c4cda44a0bedbf02cd177")
        self.assertEqual(len(NATIVE_SOURCE_SHA256), 64)
        self.assertEqual(len(NATIVE_TRANSPORT_SHA256), 64)

    def test_native_spectral_and_angular_normalization(self):
        cells = spectral_cells(16)
        self.assertEqual(len(cells), 48)
        self.assertAlmostEqual(sum(x[2] for x in cells), 1.0, places=14)
        self.assertTrue(all(x[0] < x[1] and x[2] > 0.0 and x[3] > 0.0 for x in cells))
        self.assertAlmostEqual(float(sum(angular_fractions(8))), 1.0, places=14)

    def test_same_clock_bolometric_identity_over_native_redshift_support(self):
        # These H values are explicit controls, not a claimed BASS trajectory.
        for zbar, h in ((4.0, 1.39e-17), (6.0, 2.24e-17), (10.0, 4.50e-17), (20.0, 1.14e-16)):
            row = same_clock_bolometric_control(zbar=zbar, h_per_s=h, n_h0_cm3=1.90e-7)
            self.assertGreater(row.j_proper_ev_cm3_s, 0.0)
            self.assertGreater(row.s_bass_ev_cm3_per_dln_a, 0.0)
            self.assertLessEqual(row.relative_bolometric_difference, 3e-16)
            self.assertAlmostEqual(row.spectral_fraction_sum, 1.0, places=14)
            self.assertAlmostEqual(row.angular_fraction_sum, 1.0, places=14)

    def test_per_h_to_proper_conversion_cannot_drop_the_a_cubed_factor(self):
        low = same_clock_bolometric_control(zbar=4.0, h_per_s=1.39e-17, n_h0_cm3=1.90e-7)
        high = same_clock_bolometric_control(zbar=20.0, h_per_s=1.14e-16, n_h0_cm3=1.90e-7)
        self.assertAlmostEqual(low.proper_n_h_cm3 / low.n_h0_cm3, 5.0**3, places=13)
        self.assertAlmostEqual(high.proper_n_h_cm3 / high.n_h0_cm3, 21.0**3, places=10)
        self.assertGreater(high.proper_photons_cm3_s, low.proper_photons_cm3_s)

    def test_transport_gl8_and_source_simpson_are_not_conflated(self):
        # The source's Simpson fractions and transport's GL8 cell moments are
        # separate native operators.  Equality of the unit conversion must use
        # the latter, while this nonzero difference prevents a false parity claim.
        simpson = mean_source_energy_ev()
        transport = transport_mean_energy_ev()
        self.assertGreater(abs(simpson - transport), 1e-11)
        self.assertLess(abs(simpson - transport) / transport, 1e-10)

    def test_serializable_control_does_not_expose_photo_rates(self):
        rows = controls(((6.0, 2.24e-17),), 1.90e-7)
        self.assertEqual(len(rows), 1)
        self.assertNotIn("photoionization_rate", rows[0])
        self.assertNotIn("photon_number_from_U_M", rows[0])

    def test_native_normal_domain_rejects_subnormal_comoving_hydrogen(self):
        with self.assertRaisesRegex(ValueError, "NATIVE_COMOVING_NH"):
            same_clock_bolometric_control(zbar=6.0, h_per_s=2.24e-17, n_h0_cm3=1e-320)

    def test_native_positive_domain_rejects_negative_h_and_hydrogen(self):
        with self.assertRaisesRegex(ValueError, "BASS_H_PER_S"):
            same_clock_bolometric_control(zbar=6.0, h_per_s=-2.24e-17, n_h0_cm3=1.90e-7)
        with self.assertRaisesRegex(ValueError, "NATIVE_COMOVING_NH"):
            same_clock_bolometric_control(zbar=6.0, h_per_s=2.24e-17, n_h0_cm3=-1.90e-7)

    def test_computed_native_domain_rejects_underflowing_escape_fraction(self):
        with self.assertRaisesRegex(ValueError, "NATIVE_ESCAPE_FRACTION"):
            same_clock_bolometric_control(
                zbar=6.0, h_per_s=2.24e-17, n_h0_cm3=1.90e-7, escape_fraction=1e-320
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
