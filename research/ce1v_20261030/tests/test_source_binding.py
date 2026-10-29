"""CE1-V negative contract tests for the dual-exact-rational/MPFR source link."""
from __future__ import annotations
from fractions import Fraction
import copy

import pytest

from research.ce1u_20261030.certified_gl_source import sample_gl_source
from research.ce1v_20261030.cross_certify import load_donor, evidence_lock

@pytest.mark.parametrize("n", (6,8))
def test_original_binary_gl_source_match_and_rational_is_stronger(n):
    src=sample_gl_source(n)
    proof=load_donor(n)
    exact=evidence_lock(n,src,proof)
    assert isinstance(exact,Fraction) and exact>0
    assert exact < Fraction(1,10**8)

@pytest.mark.parametrize("n", (6,8))
def test_reject_modified_actual_gl_mass_or_ray(n):
    src=sample_gl_source(n)
    cert=load_donor(n)
    src.mass=src.mass.copy()
    src.mass[0]*=1.01
    with pytest.raises(ValueError,match="stored binary source"):
        evidence_lock(n,src,cert)
    src=sample_gl_source(n)
    src.n=src.n.copy()
    src.n[0,0]*=.99
    with pytest.raises(ValueError,match="stored binary source"):
        evidence_lock(n,src,cert)

@pytest.mark.parametrize("n", (6,8))
def test_reject_claimed_physical_source_or_box_change(n):
    src=sample_gl_source(n)
    proof=load_donor(n)
    tamper=copy.deepcopy(proof)
    tamper["source_sha256"]="0"*64
    with pytest.raises(ValueError,match="physical continuum"):
        evidence_lock(n,src,tamper)
    tamper=copy.deepcopy(proof)
    tamper["box"]["ell_i_max"]="1/100"
    with pytest.raises(ValueError,match="geometry domain"):
        evidence_lock(n,src,tamper)

def test_donor_order_rejects_unstudied_gl4():
    with pytest.raises(ValueError,match="6 or 8"):
        load_donor(4)
