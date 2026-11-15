"""Regression contracts for compile-time HYREC mode isolation and input ownership."""
import importlib.util, unittest, re
from pathlib import Path
class ModeContract(unittest.TestCase):
    def module(self):
        path=Path(__file__).with_name('native_modes.py')
        self.assertTrue(path.is_file(),'native_modes.py: reproducible mode-isolated builder is not implemented')
        spec=importlib.util.spec_from_file_location('native_modes',path)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
    def test_mode_invalid_fails(self):
        m=self.module()
        with self.assertRaises(ValueError):m.prepare('UNKNOWN',1)
    def test_full_compile_time_identity(self):
        m=self.module();b=m.prepare('FULL',1)
        self.assertRegex((b/'history.h').read_text(),r'#define MODEL\s+FULL\b')
        self.assertIn('1.25 * deriv - 0.25 *deriv_prev[1]',(b/'history.c').read_text())
    def test_common_grid_and_density_owners(self):
        m=self.module();b=m.prepare('SWIFT',1);s=(b/'history.c').read_text()
        self.assertEqual(s.count('bass_hydrogen_density(cosmo,'),12)
        self.assertEqual((b/'helium.c').read_text().count('bass_hydrogen_density('),4)
        self.assertIn('double Nz = 2248, dz = data->zmax/Nz;',s)
        self.assertIn('int Nz = 2248;',s)
    def test_timestep_refinement_only(self):
        m=self.module();b=m.prepare('FULL',2)
        h=(b/'hydrogen.h').read_text()
        self.assertAlmostEqual(float(re.search(r'^#define DLNA_HYREC\s+(\S+)',h,re.M)[1]),8.49e-5/2)
        for flag in ('EFFECT_A','EFFECT_B','EFFECT_C','EFFECT_D','DIFFUSION'):
            self.assertRegex(h,rf'#define {flag}\s+1\b')
    def test_original_sources_locked(self):
        m=self.module();self.assertEqual(m.verify_source(),16)
if __name__=='__main__':unittest.main(verbosity=2)
