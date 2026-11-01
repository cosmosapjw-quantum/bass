"""Bounded independent host checks on ORIGINAL source-owned Type-II replay."""
import json,sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import replay_from_original_fixture as m

def test_git_blob_authority():
    assert m.source_lock()==5

def test_original_401_fixture_and_trajectory_rhs():
    s=m.Owner()
    assert len(s.samples)==401
    assert abs(s.samples[0]["state"][4]-.05)<1e-15
    assert abs(s.samples[-1]["state"][4]-.046733834290499696)<3e-14
    assert np.max(np.abs(m.bg_rhs(np.array(s.samples[0]["state"]))-
      np.array(s.samples[0]["rhs"])))<5e-14
    errors=[np.max(abs(m.bg_rhs(np.array(a["state"]))-np.array(a["rhs"]))) for a in s.samples]
    assert max(errors)<1e-11
    for tau,target in [(0,240.13336620482818),(.1,100.08485094440381),(.2,13.322173705416928)]:
        assert abs(s.rate(tau)/target-1)<1e-13

def test_original_rust_sixaxis_collision_fixture():
    e,w=m.grid("axis6");C,*_=m.cp(e,w,.1,"fixed")
    y=np.array([1.,.7,1.2,.9,.6,1.4])
    expected=np.array([-.077556362500000239,.22097348749999984,.25408950617283943,-.25930785123966976,.3561345749999999,-.4399450250000001])
    assert np.max(abs(C@y-expected))<3e-13

def test_paired_grid_truly_source_admissible_and_fixed6_false():
    for name in ("axis6","lebedev26"):
        e,w=m.grid(name)
        for v in (0,.05,.1,.2):
            C,P,_,_,r,a=m.cp(e,w,v,"paired")
            off=C.copy();np.fill_diagonal(off,0.)
            assert np.min(off)>-1e-13
            assert np.max(abs(C@r))<5e-13
            assert np.max(abs(a@C))<5e-13
            assert np.max(abs(P@P-P))<1e-12
    e,w=m.grid("axis6");C,P,_,_,r,a=m.cp(e,w,.1,"fixed")
    assert np.max(abs(C@r))>.01

def test_original_oblique_kato_intertwines():
    e,w=m.grid("lebedev26");v=.061;dv=.031
    for mode in ("fixed","paired"):
        C,P,*_=m.cp(e,w,v,mode)
        Pd=m.pv(e,w,v,mode)
        h=1e-6
        center=(m.cp(e,w,v+h,mode)[1]-m.cp(e,w,v-h,mode)[1])/(2*h)
        assert np.max(abs(center-Pd))<2e-8
        K=dv*(Pd@P-P@Pd)
        assert np.max(abs(K@P-P@K-dv*Pd))<1e-12

def test_saved_aem2_exact_source_scoped_order():
    x=json.loads((HERE.parent/"ci_generated/ORIGINAL_TYPEII_AEM2_REPLAY.json").read_text())
    assert len(x["records"])==96 and x["original_source_hash_count"]==5
    y=json.loads((HERE.parent/"LOCAL_REFERENCE_SCIENCE.json").read_text())["baseline"]
    o=next(z for z in x["records"] if z["grid"]=="lebedev26" and z["mode"]=="paired" and z["alpha"]==100000 and z["N"]==32 and z["method"]=="old")
    k=next(z for z in x["records"] if z["grid"]=="lebedev26" and z["mode"]=="paired" and z["alpha"]==100000 and z["N"]==32 and z["method"]=="kato")
    assert abs(o["local_order"]-y["old_order"])<.04
    assert abs(k["local_order"]-y["kato_order"])<.04
    assert abs(o["relative_error"]-y["old_error"])<5e-7
    assert abs(k["relative_error"]-y["kato_error"])<5e-7
    assert o["endpoint_defect"]/k["endpoint_defect"]>100
    assert x["stageII"]=="11/11_HISTORICAL_NOT_CANONICAL"
    assert x["production_ready"] is False
