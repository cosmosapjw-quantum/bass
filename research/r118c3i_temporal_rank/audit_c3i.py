"""Skew Pfaffian audit with extended precision on stored binary64 matrices."""
import json,numpy as np
from decimal import Decimal,localcontext
from pathlib import Path
D=Path(__file__).resolve().parent
def main():
 a=json.loads((D/'REFINEMENT.json').read_text());rows={}
 for name in ['base','fine_base']:
  M=np.array(a[name]['M']);sv=np.linalg.svd(M,compute_uv=False)
  assert np.array_equal(M,-M.T)
  with localcontext() as c:
   c.prec=80;v=lambda i,j:Decimal.from_float(float(M[i,j]))
   pf=v(0,1)*v(2,3)-v(0,2)*v(1,3)+v(0,3)*v(1,2)
  ratio=float(abs(pf))/sv[0]**2
  rows[name]=dict(pfaffian=str(pf),ratio_from_pfaffian=ratio,svd_ratio=float(sv[2]/sv[0]),relative_difference=float(abs(ratio/(sv[2]/sv[0])-1)))
  assert rows[name]['relative_difference']<1e-4
 out=dict(rows=rows,weyl_ratio=a['weyl_ratio_to_small_singular'],scope='arithmetic check on computed binary64 M, not certified continuous rank; Weyl bound fails to resolve small singular value')
 (D/'AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':main()
