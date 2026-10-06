"""Real NumPy-only history boundary checks, runnable without pytest/native/JAX.

Run: python -m unittest discover -s tests -p test_history_optional_boundary.py -v
No numerical backend is mocked. Each check runs in a fresh interpreter.
"""
from pathlib import Path
import subprocess
import sys
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[1]
GUARD = '''
import sys
OPTIONAL = {'jax', 'jaxlib', 'diffrax', 'equinox', 'optimistix', 'lineax',
            'scipy', 'sympy', 'mpmath'}
class RejectOptional:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.partition('.')[0] in OPTIONAL:
            raise ModuleNotFoundError('blocked optional dependency: ' + fullname,
                                      name=fullname.partition('.')[0])
sys.meta_path.insert(0, RejectOptional())
'''


class HistoryOptionalBoundaryTests(unittest.TestCase):
    def run_fresh(self, code):
        result = subprocess.run(
            [sys.executable, '-c', GUARD + textwrap.dedent(code)],
            cwd=ROOT, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_units_and_lazy_legacy_names(self):
        self.run_fresh('''
            import bianchi.physical as physical
            from bianchi.physical import units
            assert units.hubble_distance_mpc(100.0) == 2997.92458
            assert 'bianchi.physical._legacy' not in sys.modules
            expected = {'integrate_H', 'cosmic_time', 'mean_scale_factor',
                        'directional_scale_factors', 'shear_scalar', 'dimensionful',
                        'lorentz_factor', 'bbn_expansion_anisotropy', 'observables'}
            assert expected.issubset(dir(physical))
            try:
                physical.not_a_physical_export
            except AttributeError:
                pass
            else:
                raise AssertionError('unknown attribute should fail')
            assert not OPTIONAL.intersection(sys.modules)
        ''')

    def test_tabulated_history_rates_and_optical_depth(self):
        self.run_fresh('''
            import numpy as np
            from bianchi.thermo import history_api as H
            from bianchi.physical import units as U
            hist = H.TabulatedHistory([0., 1., 3.], [1., 1., 1.])
            assert H.validate_history(hist)['ok']
            assert hist.x_e(1.) == 1.
            assert hist.x_e(np.sqrt(2.) - 1.) == 1.
            assert H.n_H_cm3(0.) == 8.50e-6 * 0.0224
            assert H.n_H_cm3(1.) / H.n_H_cm3(0.) == 8.
            rate = H.thomson_rate(hist, 1., tau_units=False)
            expected = 6.6524587e-25 * (8.50e-6 * 0.0224 * 8.) * 2.99792458e10
            assert rate == expected
            z = np.array([0., 1., 3.])
            constant_h = lambda z: np.ones_like(z) * 1e-15
            np.testing.assert_allclose(H.thomson_rate(hist, z, H_of_z=constant_h),
                                       H.thomson_rate(hist, z, tau_units=False) / 1e-15,
                                       rtol=0., atol=0.)
            optical = H.optical_depth(hist, z, H_of_z=constant_h)
            assert optical['tau'][0] == 0.
            assert np.all(np.diff(optical['tau']) > 0.)
            assert np.isfinite(optical['g']).all()
            try:
                hist.x_e(4.)
            except ValueError:
                pass
            else:
                raise AssertionError('history must reject out-of-range input')
            assert not OPTIONAL.intersection(sys.modules)
        ''')

    def test_numpy_saha_and_rate_frontends(self):
        self.run_fresh('''
            import numpy as np
            from bianchi.thermo import recombination as R, history_api as H
            from bianchi.q import rate, electron_rate, electron_validity
            z = np.array([500., 1000., 1500.])
            xe = R.saha_xe(z)
            assert np.isfinite(xe).all() and np.all((xe >= 0.) & (xe <= 1.))
            hist = H.SahaHistory(z)
            np.testing.assert_array_equal(hist.x_e(z), xe)
            assert electron_rate.density_cm3_to_m3(2.) == 2e6
            assert electron_rate.density_m3_to_cm3(2e6) == 2.
            from bianchi.q.electron import ColdElectronTestField
            electron = ColdElectronTestField.comoving(2e6, [0., 0., 0.])
            context = electron_rate.ElectronCollisionContext(electron)
            rest_rate = context.rest_opacity_per_second()
            assert rest_rate == 2e6 * electron_rate.SIGMA_T_M2 * electron.c_m_s
            assert context.rate_per_normal_time_s([0., 0., 1.]) == rest_rate
            constant_hist = H.TabulatedHistory([0., 1., 3.], [1., 1., 1.])
            cosmo = rate.Cosmology(z0=1.)
            schedule = rate.RateSchedule(constant_hist, cosmo=cosmo,
                                         mode='lcdm', lane='phenomenology')
            assert schedule.nu(0.) == H.thomson_rate(constant_hist, 1.)
            schedule.validate_span(0.01, 2)
            assert not OPTIONAL.intersection(sys.modules)
        ''')

    def test_scipy_is_required_only_when_solver_is_called(self):
        self.run_fresh('''
            from bianchi.thermo import recombination as R
            from bianchi.optional_dependencies import OptionalDependencyError
            for operation in (
                lambda: R.recombination_redshift(),
                lambda: R.peebles_xe([1500., 1499.]),
                lambda: R.saha_all_species(2500.),
            ):
                try:
                    operation()
                except OptionalDependencyError as error:
                    assert error.dependency == 'scipy'
                    assert error.feature == R.__name__
                else:
                    raise AssertionError('actual solver must require SciPy')
        ''')

    def test_wildcard_import_preserves_historical_solver_aliases(self):
        self.run_fresh('''
            from bianchi.optional_dependencies import OptionalDependencyError
            try:
                exec('from bianchi.thermo.recombination import *', {})
            except OptionalDependencyError as error:
                assert error.dependency == 'scipy'
            else:
                raise AssertionError('wildcard import must not silently drop solver aliases')
        ''')

    def test_legacy_request_still_reports_optional_jax(self):
        self.run_fresh('''
            import bianchi.physical as physical
            from bianchi.optional_dependencies import OptionalDependencyError
            try:
                physical.integrate_H
            except OptionalDependencyError as error:
                assert error.dependency == 'jax'
            else:
                raise AssertionError('legacy oracle contract must be retained')
        ''')


if __name__ == '__main__':
    unittest.main()
