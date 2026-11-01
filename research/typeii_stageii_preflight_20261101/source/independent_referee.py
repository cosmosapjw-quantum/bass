"""Independent static witness. Does NOT import source collision code. -O-safe."""
import json,sys
from pathlib import Path
from fractions import Fraction
import numpy as np

def verify(path):
    data=json.loads(Path(path).read_text())
    cases=data["rows"]
    if len(cases)!=10:raise RuntimeError("missing original model cases")
    dirs=np.array([[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]])
    K=np.array([[float(Fraction(1,8)*(1+int(dirs[i]@dirs[j])**2)) for j in range(6)] for i in range(6)])
    eig=np.sort(np.linalg.eigvalsh(K))
    if np.max(abs(eig-np.array([0,0,0,.25,.25,1])))>1e-13:
        raise RuntimeError("sixaxis exact positive collision spectrum mismatch")
    for c in cases:
        if c["max_null"]>2e-12 or c["max_left"]>2e-12:
            raise RuntimeError("false null/invariant admission")
        if c["max_markov_row"]>2e-12 or c["max_stationary"]>2e-12:
            raise RuntimeError("false Markov evidence")
        if c["max_expm_gap"]>3e-12 or c["poisson_tail"]>3e-13:
            raise RuntimeError("uniformization vs dense expm discrepancy")
    f=data["fixed_grid"]
    if f["fixed_normal_null_defect"]<=1e-3 or not f.get("correctly_rejected"):
        raise RuntimeError("fixed normal false pass")
    if f["original_Rust_fixture_max_gap"]>1e-12:
        raise RuntimeError("original Rust fixture parity failed")
    if data["production_ready"] or data["join_J1"]!="0/2_PASS":
        raise RuntimeError("unsupported production promotion")
    return {"status":"PASS_SCOPED_RHS_INDEPENDENT_SAME_AUTHOR","cases":len(cases),"sixaxis_K_eigenvalues":[float(x) for x in eig]}
if __name__=="__main__":
    print(json.dumps(verify(sys.argv[1]),sort_keys=True))
