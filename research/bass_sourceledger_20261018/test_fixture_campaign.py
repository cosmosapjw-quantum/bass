"""Published generated fixtures, references and finite-time convergence gates."""
from pathlib import Path
import hashlib,json,unittest
from dataclasses import replace
from generate_fixtures import original_geometry
from deposition import continuum_reference
from source_oracle import Case
ROOT=Path(__file__).resolve().parent
class FixtureCampaignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f=ROOT/'fixtures';cls.a=json.loads((cls.f/'ANALYSIS.json').read_text())
    def test_all_exact_file_hashes_and_real_case_records(self):
        m=json.loads((self.f/'FIXTURE_MANIFEST.json').read_text())
        for name,h in m['files'].items():
            self.assertEqual(hashlib.sha256((self.f/name).read_bytes()).hexdigest(),h)
        text=(self.f/'INPUT.tsv').read_text().splitlines()
        self.assertEqual(sum(z.startswith('CASE ') for z in text),58)
        self.assertEqual(sum(z.startswith('BIRTH ') for z in text),1090)
        self.assertEqual(sum(z.startswith('END ') for z in text),58)
        self.assertEqual(m['native_status'],'NOT_RUN')
    def test_actual_background_sampled_source_time_order(self):
        for row in self.a['time_refinement']:
            limits=(3.8,4.2) if row['method']=='midpoint' else (14.,18.)
            for r in row['successive_abs_error_ratios']:
                self.assertGreater(r,limits[0]);self.assertLess(r,limits[1])
        self.assertLess(self.a['max_number_ledger_normalized'],2e-14)
        self.assertLess(self.a['max_energy_ledger_normalized'],2e-14)
    def test_birth_isotropy_discrete_bias_and_angular_resolution(self):
        rows=[r for r in self.a['results'] if r['kind']=='angular' and r['b']!=0]
        for b in (-.2,.2):
            d={r['nmu']:abs(r['P2_per_U']) for r in rows if r['b']==b}
            self.assertGreater(d[8],1e-3);self.assertLess(d[32],1e-12)
    def test_continuum_reference_resolution_independent(self):
        g,_=original_geometry('MASSIVE_PLUS');b,H,s=g(.2)
        c=Case('REFERENCE',.2,b,H,s,1.,qmin=1.)
        a=continuum_reference(c,g,.2,.8,96,96);b=continuum_reference(c,g,.2,.8,192,192)
        for name in ('inventory_n','inventory_u','delta','work'):
            self.assertLess(abs(a[name]-b[name])/b['ledger_u'],5e-12)
if __name__=='__main__':unittest.main(verbosity=2)
