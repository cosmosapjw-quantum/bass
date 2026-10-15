from __future__ import annotations
import csv,hashlib,json,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from export_native_geometry import export
from source_table import BackgroundTable

class GeometryExportTests(unittest.TestCase):
  def test_eight_cases_native_background_contract(self):
    inputdir=ROOT/"source_pr164"
    with tempfile.TemporaryDirectory() as tmp:
      p=pathlib.Path(tmp)/"out"
      result=export(inputdir/"PRODUCER_RECEIPT.json",inputdir/"PROPOSED_REI_BACKGROUND.csv",p)
      self.assertEqual(result["rows"],968)
      self.assertEqual(result["native_cargo_build"],"NOT_RUN_IN_CHATGPT_SESSION")
      self.assertLess(result["max_producer_integrated_clock_relative"],5e-10)
      h=hashlib.sha256((p/"NATIVE_GEOMETRY.csv").read_bytes()).hexdigest()
      self.assertEqual(h,result["geometry_csv_sha256"])
      receipt=json.loads((p/"NATIVE_GEOMETRY_RECEIPT.json").read_text())
      self.assertEqual(h,receipt["geometry_csv_sha256"])
      with (p/"NATIVE_GEOMETRY.csv").open() as f:rows=list(csv.DictReader(f))
      self.assertEqual(len(rows),968)
      self.assertEqual(len({r["case"] for r in rows}),8)
      self.assertTrue(all(float(r["h_per_s"])>0 for r in rows))
      self.assertTrue(all(float(r["time_s"])>=0 for r in rows))
      self.assertLess(float(rows[-1]["sigma_signed"]),0)
      self.assertGreater(float(rows[-1]["Sigma"]),0)
      with self.assertRaises(FileExistsError):export(inputdir/"PRODUCER_RECEIPT.json",inputdir/"PROPOSED_REI_BACKGROUND.csv",p)

if __name__=="__main__": unittest.main(verbosity=2)
