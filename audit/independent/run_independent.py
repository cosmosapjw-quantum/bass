"""
Independent coordinate-basis verification runner (debt: structural resolution of the
self-consistency gates' common-mode blindness).

These five scripts import NOTHING from bianchi/ or audit/ -- they build a coordinate
realization of a type-VI_h algebra (exp(xM) co-frame), an arbitrary metric, and check
the disputed transport/Maxwell equations by JAX autodiff of the coordinate metric.  A
common-mode error in the orthonormal-frame engine (audit/einstein_frame.py) that fools
the self-consistency gates cannot fool these, because they never touch that engine.

    cd audit/independent && python run_independent.py   ->  independent_manifest.json

Exit 0 iff every part reports PASS.
"""
import json, os, re, subprocess, sys

PARTS = ["partA", "partB", "partC", "partD", "partE_rotated"]
HERE = os.path.dirname(os.path.abspath(__file__))

# what each part certifies (for the manifest) + the verdict-line regex
CERT = {
    "partA": "type-VI_h coordinate realization: structure constants re-read, Jacobi",
    "partB": "frame data (H, sigma, R, n-hat, a-hat) read off the metric",
    "partC": "CLAIM 1 geodesic transport (H/sigma/P-quadratic) vs exact coordinate geodesic",
    "partD": "CLAIM 2 Maxwell curl relative sign +eps (vs coordinate div F / dF)",
    "partE_rotated": "rotating-frame run: Maxwell R-terms + D13 Omega-sign discriminator",
}


def run(part):
    r = subprocess.run([sys.executable, f"{part}.py"], cwd=HERE,
                       capture_output=True, text=True,
                       env={**os.environ, "JAX_PLATFORMS": "cpu"})
    out = r.stdout + r.stderr
    m = re.search(r"PART [A-Z0-9_]*\s*VERDICT[^\n]*", out)
    verdict = m.group(0) if m else "(no verdict line)"
    passed = ("PASS" in verdict) or ("CONFIRMED" in verdict)
    # extract the tightest residual quoted, if any
    res = re.findall(r"(\d\.\d+e[+-]\d+)", out)
    return dict(part=part, certifies=CERT[part], passed=bool(passed),
                verdict=verdict.strip(), returncode=r.returncode,
                min_residual=min((float(x) for x in res), default=None),
                tail=out.strip().splitlines()[-3:])


def main():
    results = [run(p) for p in PARTS]
    n_fail = sum(not r["passed"] for r in results)
    manifest = dict(kind="independent_coordinate_basis_verification",
                    imports_bianchi_or_engine=False,
                    parts=results, n_failed=n_fail,
                    all_passed=(n_fail == 0))
    json.dump(manifest, open(os.path.join(HERE, "independent_manifest.json"), "w"),
              indent=2)
    for r in results:
        flag = "PASS" if r["passed"] else "FAIL"
        print(f"  [{flag}] {r['part']:14s} {r['verdict']}")
    print(f"\n{len(results) - n_fail}/{len(results)} independent parts passed")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
