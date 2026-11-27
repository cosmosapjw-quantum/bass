"""Audit exact W and budget on all actual saved jet controls."""
import json,numpy as np
from pathlib import Path
from sphere import start,check,G,H
D=Path(__file__).resolve().parent
def run():
 files=sorted(D.glob('*.npz'));assert len(files)==18
 rows={}
 for f in files:
  z=np.load(f);tag=f.name.split('_')[0];a=z['A'];C=z['control'];q=check(start(tag),a);assert q['wedge_relative']<1e-5 and q['metric_relative']<1e-12
  assert abs(np.trace(C@G@C.T)-q['budget'])<1e-12
  assert np.isfinite(z['B']).all()
  rows[f.stem]=q
 p=json.loads((D/'SEARCH.json').read_text());s=json.loads((D/'PIXEL_INTEGRATED.json').read_text())
 for tag,r in p['selected'].items():assert max(r['fine_relative'])<1e-5
 z=json.loads((D/'R7.json').read_text());assert len([q for r in z['rows'] for q in r['samples']])==30
 out=dict(actual_jet_cases=len(files),max_wedge_relative=max(q['wedge_relative'] for q in rows.values()),max_budget_relative=max(q['metric_relative'] for q in rows.values()),selected=p['selected'],pixel_examples={k:v for k,v in s['rows'].items() if k in ['64_20_6_1e-06','128_20_6_1e-06','128_20_12_1e-06','256_20_6_1e-06']},scope='saved-array exact numerical wedge/metric and refinement audit; no global minimum or observed likelihood')
 (D/'AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':run()
