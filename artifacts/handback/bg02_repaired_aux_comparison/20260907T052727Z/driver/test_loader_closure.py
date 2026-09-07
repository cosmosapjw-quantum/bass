from pathlib import Path
import hashlib,json,re,sys,unittest
r=Path(__file__).resolve().parent.parent
revision=sys.argv.pop(1)
class FrozenDriverClosureTests(unittest.TestCase):
 def test_exact_original_assertions_inputs_and_exit_semantics_preserved(self):
  original=(r/'driver/original/BASS_AUX13_AUX14_V1.wls').read_text()
  actual=(r/'driver'/revision/'BASS_AUX13_AUX14_V1.wls').read_text()
  prefix=' rel = {"Authority/BG02Convention.wl",\n   "Geometry/StructureConstants.wl",'
  self.assertEqual(actual.replace(prefix,' rel = {"Geometry/StructureConstants.wl",',1),original)
  ids=re.findall(r'TestID->"([^"]+)"',actual)
  self.assertEqual(ids,json.loads((r/'historical/execution/aux-final-original.json').read_text())['required_ids'])
 def test_required_candidate_loader_dependency_is_present_before_consumers(self):
  actual=(r/'driver'/revision/'BASS_AUX13_AUX14_V1.wls').read_text()
  rel=re.search(r' rel = \{(.*?)\};',actual,re.S).group(1)
  paths=re.findall(r'"([^"]+)"',rel)
  self.assertIn('Authority/BG02Convention.wl',paths)
  self.assertLess(paths.index('Authority/BG02Convention.wl'),paths.index('Geometry/ONFConnectionCurvature.wl'))
  for p in paths:self.assertTrue((r/'source/wolfram/BASS/Kernel'/p).is_file())
  registry=r/'source/docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/BG_02_CONVENTION_V2.json'
  self.assertEqual(hashlib.sha256(registry.read_bytes()).hexdigest(),'60dd32c8185d37850a6f0878ba7c461644f332b96f6fcf92ec12823cfd487868')
if __name__=='__main__':unittest.main()
