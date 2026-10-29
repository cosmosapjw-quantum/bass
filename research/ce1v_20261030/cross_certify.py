"""CE1-V source-faithful cross-branch GL exact-rational + MPFR192 Dini geometry.

Imports PR264 immutable exact-rational source certificate bytes, recertifies the
identical binary64 GL source and four RK4/Hermite panels under PR265, replaces
ONLY the nonnegative source forcing in the original positive MPFR propagator.
The initial/time/jump carriers are freshly obtained from PR265 and preserved.

This is a conditional composed pilot certificate, NOT a new formal verification
of the donor proof, not a production solver, and not a CMB sky certificate.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

import numpy as np

from bianchi.nonperturbative.einstein_interval import (
    Interval, _iv_fraction, propagate_interval,
)
from research.ce1u_20261030.certified_gl_source import (
    sample_gl_source, sha, SOURCE_SHA,
)
from research.ce1u_20261030.certify_gl_coupled import certify_gl_coupled

ROOT = Path(__file__).resolve().parent
DONOR_HEAD = "15bb9fd015570c1562a4a7b9102f25a8481796f5"
PARENT_HEAD = "bcbb2ba451b9026608525cce27e26cf1a1288161"
EXPECTED_DONOR_GIT_BLOBS = {
    6: "4a3442e72ccf41563464092079acf84483da9a0f",
    8: "7cc1f9331aa532d86a71f249a9be552367c90860",
}

def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def load_donor(n: int) -> dict:
    if n not in (6, 8):
        raise ValueError("GL order 6 or 8 only")
    path = ROOT / "donor" / f"GL{n}_source_exact_bound.json"
    raw = path.read_bytes()
    if git_blob_sha(raw) != EXPECTED_DONOR_GIT_BLOBS[n]:
        raise ValueError("Donor original exact-rational certificate bytes changed")
    return json.loads(raw)

def evidence_lock(n: int, source, cert: dict) -> Fraction:
    if n not in (6, 8):
        raise ValueError("Validated orders 6/8 only")
    c = cert
    if c.get("certificate") != "EXACT_RATIONAL_REAL_SOURCE_BOUND_NOT_FLOAT_RUNTIME_NOT_MPFR192":
        raise ValueError("Wrong donor proof type")
    if c.get("n") != n or c.get("rays") != 6*n*n or c.get("K") != 12:
        raise ValueError("Donor polynomial order/ray count mismatch")
    if c.get("box") != {
        "ell_i_min":"0", "ell_i_max":"2/25", "a_i_initial":"1", "u_final":"2/25"
    }:
        raise ValueError("Donor geometry domain mismatch")
    if c.get("q_exact") != "1/11" or c.get("b_reference_exact") != "23/25":
        raise ValueError("Donor analytic tail assumptions changed")
    if c.get("source_sha256") != SOURCE_SHA:
        raise ValueError("Changed physical continuum source")
    hashes = c.get("stored_gl_hashes", {})
    actual_n = sha(np.asarray(source.n,dtype="<f8").tobytes())
    actual_m = sha(np.asarray(source.mass,dtype="<f8").tobytes())
    if hashes.get("ray_sha256") != actual_n or hashes.get("mass_sha256") != actual_m:
        raise ValueError("Donor and active MPFR stored binary source differ")
    exact = Fraction(c["maximum_epsilon_source_exact"])
    if not 0 < exact < Fraction(1,10**8):
        raise ValueError("Donor pressure discrepancy outside expected scoped bound")
    # Preserve exact upper fraction, not the nearest-rounded float report.
    return exact

def run_one(n: int, *, subcells: int=1) -> dict:
    source = sample_gl_source(n)
    proof = load_donor(n)
    eta_exact = evidence_lock(n, source, proof)
    # Recompute the original four-panel CE1-U MPFR192 time defect, Hermite
    # binary knot jumps, input locking and initial Hamiltonian comparison.
    original = certify_gl_coupled(n, subcells=subcells)
    oldsrc = original["source"]
    if (oldsrc["stored_ray_sha256"] != proof["stored_gl_hashes"]["ray_sha256"]
        or oldsrc["stored_mass_sha256"] != proof["stored_gl_hashes"]["mass_sha256"]):
        raise ArithmeticError("Two live source calculators produced different binary inputs")
    if not (original["source"]["geometry_upper"] == 0.07 and
            float(Fraction(proof["box"]["ell_i_max"])) >= 0.07):
        raise ArithmeticError("Incompatible analytic source domains")
    # Source discrepancy is independent of initial and numerical time-error
    # carriers, so repropagate ONLY source forcing with the same L=4 Pcap=4.
    eta = _iv_fraction(eta_exact)
    if eta.upper > oldsrc["total_pressure_error_upper"]:
        raise ArithmeticError("Donor forcing not a source-bound improvement")
    src = [Interval(0), Interval(0)]
    for panel in original["rows"]:
        dt = Interval(float(panel["time_end"])) - Interval(float(panel["time_start"]))
        src = propagate_interval(src, dt, Interval(1), Interval(0), eta)
    # Parent values are already outward-rounded upper endpoints; wrapping as
    # exact binary64 retains the rigorous enclosure before another MPFR sum.
    hnew = (
        Interval(float(original["initial_h_upper"]))
        + Interval(float(original["time_jump_h_upper"]))
        + src[1]
    ).upper
    oldh = float(original["final_h_upper"])
    if not 0 < hnew <= oldh < 1e-5:
        raise ArithmeticError("Positive MPFR propagation or original fixed h target failed")
    return {
        "schema": "bass.ce1v.rational_to_mpfr_full_path.v1",
        "order": n, "rays": len(source.mass),
        "source_ray_sha256": oldsrc["stored_ray_sha256"],
        "source_mass_sha256": oldsrc["stored_mass_sha256"],
        "donor_pr": 264, "donor_head": DONOR_HEAD,
        "parent_pr": 265, "parent_head": PARENT_HEAD,
        "donor_exact_rational_source_upper": str(eta_exact),
        "donor_exact_rational_source_upper_float": float(eta.upper),
        "old_mpfr_ellipse_source_upper": oldsrc["total_pressure_error_upper"],
        "old_mpfr_h_upper": oldh,
        "new_initial_h_upper": original["initial_h_upper"],
        "new_time_jump_h_upper": original["time_jump_h_upper"],
        "new_source_h_upper": src[1].upper,
        "new_full_four_panel_h_upper": hnew,
        "fixed_geometry_h_target": 1e-5, "fixed_target_met": bool(hnew<1e-5),
        "scope": "identical binary GL source, exact rational donor forcing and reused/fresh CE1-U original MPFR192 RK4/Hermite 4-panel carriers",
        "production_ready": False, "merge_ready": False,
        "upper_dag": "9/15",
        "formal_all_program_proof": "NOT_RUN",
        "distinct_author_review": "NOT_RUN",
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",required=True)
    ap.add_argument("--subcells",type=int,default=1)
    args=ap.parse_args()
    if args.subcells not in (1,2):
        raise ValueError("Only original bounded subcells 1 or 2")
    out={"unit":"CE1V_DUAL_SOURCE_MPFR192", "cases":{}}
    for n in (6,8):
        r=run_one(n,subcells=args.subcells)
        out["cases"][str(n)]=r
        print(f"CE1V_GL{n}_DUAL_SOURCE_MPFR_TARGET_PASS "
              f"original={r['old_mpfr_h_upper']:.17g} "
              f"new={r['new_full_four_panel_h_upper']:.17g}",flush=True)
    dest=Path(args.output);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(out,indent=2,allow_nan=False)+"\n")
    return out

if __name__=="__main__":
    main()
