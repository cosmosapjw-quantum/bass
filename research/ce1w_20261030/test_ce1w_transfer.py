from pathlib import Path
import sys, numpy as np, pytest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from research.ce1w_20261030 import ce1w_transfer as w
@pytest.mark.parametrize("n",[6,8])
def test_source_and_parent(n):
    q,m,d=w.read(n)
    assert len(q)==6*n*n and len(d["u"])==41
    for i in (0,20,40):
        ell=np.array([d[f"ell{j}"][i] for j in (1,2,3)])
        E,P,a,alpha,D=w.response(ell,q,m)
        assert abs(E-d["E"][i])<5e-13
        assert np.max(abs(D.sum(axis=1)))<8e-12
@pytest.mark.parametrize("n",[6,8])
def test_derivatives(n):
    q,m,d=w.read(n)
    ell=np.array([d[f"ell{j}"][20] for j in (1,2,3)])
    D=w.response(ell,q,m)[-1]
    for j in range(3):
        ep=ell.copy();em=ell.copy();h=3e-6
        ep[j]+=h;em[j]-=h
        finite=(w.response(ep,q,m)[-2]-w.response(em,q,m)[-2])/(2*h)
        assert np.max(abs(finite-D[:,j]))<5e-9
@pytest.mark.parametrize("n",[6,8])
def test_physical_two_time_kernel(n,tmp_path):
    r=w.build(n,tmp_path)
    for l in ("2","4"):
        z=np.load(tmp_path/f"GL{n}_K{l}_response.npz")
        K=z["K"];Du=z["Du"];Dv=z["Dv"]
        assert K.shape==(41,41)
        assert np.max(abs(K-K.T))<2e-13
        assert np.min(np.linalg.eigvalsh(K))>-2e-12
        assert np.max(abs(Du.sum(axis=2)))<5e-12
        assert np.max(abs(Du-Dv.transpose(1,0,2)))<2e-13
        assert abs(K[0,-1]-r[l]["K_0_end"])<1e-14
