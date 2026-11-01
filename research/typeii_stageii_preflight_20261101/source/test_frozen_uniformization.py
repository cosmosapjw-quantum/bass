"""Scoped production-path tests, not canonical Stage II admission tests."""
import hashlib,json
from pathlib import Path
import numpy as np
import pytest
from frozen_uniformization import sixaxis,lebedev26,paired,collision,require_markov,uniform,run

def test_source_git_blobs_are_immutable():
    root=Path(__file__).resolve().parents[3]
    data=json.loads((root/"research/typeii_stageii_preflight_20261101/SOURCE_BINDINGS.json").read_text())
    for path,expected in data["source_blobs"].items():
        b=(root/path).read_bytes()
        found=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
        assert found==expected,(path,found,expected)

def test_original_Rust_sixaxis_output_parity():
    actual=run()["fixed_grid"]
    assert actual["original_Rust_fixture_max_gap"]<5e-13

def test_frozen_fixed_normal_v01_fails():
    n,w=sixaxis();C,r,a,_=collision(n,w,.1)
    assert np.max(abs(C@r))>1e-3
    with pytest.raises(ValueError):require_markov(C,r,a)

@pytest.mark.parametrize("v",[0.,.02,.05,.10,.20])
def test_paired_sixaxis_valid_scalar_reference(v):
    er,wr=sixaxis();en,wn=paired(er,wr,v)
    C,r,a,_=collision(en,wn,v)
    lam,B,M,pi=require_markov(C,r,a)
    assert min(np.min(r),np.min(a),np.min(M))>=0
    assert np.max(abs(M.sum(1)-1))<1e-12
    assert np.max(abs(pi@M-pi))<1e-12

def test_lebedev26_real_source_cases():
    cases=run()
    assert cases["matched_paired_scalar_cases"]==10
    assert all(c["max_expm_gap"]<3e-12 for c in cases["rows"])

def test_witness_is_not_production_gate():
    o=run()
    assert o["stageII"].endswith("NOT_ESTABLISHED")
    assert not o["production_ready"]
    assert o["join_J1"]=="0/2_PASS"

def test_false_signed_generator_fails_closed():
    en,wn=sixaxis();C,r,a,_=collision(en,wn,0)
    C[0,1]=-0.5
    with pytest.raises(ValueError):require_markov(C,r,a)

def test_false_equilibrium_fails_closed():
    en,wn=sixaxis();C,r,a,_=collision(en,wn,0)
    with pytest.raises(ValueError):require_markov(C,np.arange(1.,7.),a)
