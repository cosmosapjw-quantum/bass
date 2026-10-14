"""R8 delivery read-only digest checks. Does not claim theorem truth or rerun any producer."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run():
 manifest=json.loads((ROOT/'MANIFEST.json').read_text())
 failures=[]
 for x in manifest['files']:
  p=ROOT/x['path']
  if not p.is_file():failures.append(x['path']+':MISSING');continue
  b=p.read_bytes()
  if len(b)!=x['size_bytes'] or hashlib.sha256(b).hexdigest()!=x['sha256']:failures.append(x['path']+':MISMATCH')
 json_result=json.loads((ROOT/'evidence/RESULT.json').read_text())
 xact=json.loads((ROOT/'evidence/xact_r8_fixed.json').read_text())
 if not xact['all_zero'] or any(v!='0' for v in xact['residuals'].values()):failures.append('XACT_7_NOT_ZERO')
 if json_result['decision']!='PROMOTE_FOR_FIXED_36RAY_MODEL_ONLY':failures.append('WRONG_DECISION')
 if float(json_result['total_error_display'])>=4.75e-7:failures.append('TOTAL_RADIUS')
 if not (float(json_result['conservative_stokes_min_eigen_lower_display'])>0.12548):failures.append('POLARIZATION')
 result={'read_only':True,'payload_count':len(manifest['files']),'actual_xAct_groups':len(xact['residuals']),'failures':failures,'pass':not failures}
 print(json.dumps(result,indent=2))
 return 0 if not failures else 1
if __name__=='__main__':raise SystemExit(run())
