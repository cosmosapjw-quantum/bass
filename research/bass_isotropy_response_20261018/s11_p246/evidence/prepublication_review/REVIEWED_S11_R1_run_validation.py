"""Run only the registered S11 new-projector controls, never an old history.

An existing output directory is rejected. Raw command/stdin/stdout/stderr and all
failed controls remain in that run directory. Pass a published source commit.
"""
from __future__ import annotations
import argparse
import dataclasses
from decimal import Decimal as D, localcontext
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone

from projector import (ProjectionError, array_digest, decimal_continuum_response,
                       decimal_ray_response, exact_certificate, legendre,
                       project_birth, response_taylor, support_feasibility)


def dump(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False)+"\n")


def invoke(command, *, stdin=None, timeout=120):
    t = time.monotonic()
    rec = {"command": list(map(str, command)), "stdin": stdin, "timeout_seconds":timeout}
    def as_text(value):
        return value.decode(errors="replace") if isinstance(value,bytes) else (value or "")
    try:
        result = subprocess.run(command, input=stdin, text=True, capture_output=True, timeout=timeout)
        rec.update(stdout=result.stdout, stderr=result.stderr, exit_code=result.returncode,
                   execution_status="COMPLETED")
    except subprocess.TimeoutExpired as error:
        rec.update(stdout=as_text(error.stdout), stderr=as_text(error.stderr), exit_code=None,
                   execution_status="TIMEOUT")
    except OSError as error:
        rec.update(stdout="", stderr=str(error), exit_code=None, execution_status="LAUNCH_FAILED")
    rec["elapsed_seconds"] = time.monotonic()-t
    return rec


def payload(order, mu, prior):
    return f"{order} {len(mu)}\n"+"\n".join(f"{m:.17e} {w:.17e}" for m, w in zip(mu, prior))+"\n"


def run(args, here, output):
    started = time.monotonic()
    checks, executions, projections = [], [], []

    def check(name, condition, **evidence):
        checks.append({"id": name, "pass": bool(condition), **evidence})

    def record_execution(call):
        executions.append(call)
        dump(output/"EXECUTIONS.json", executions)

    manifest = []
    for path in sorted(here.rglob("*")):
        if path.is_file() and "evidence" not in path.parts and "__pycache__" not in path.parts and path.suffix in (".py", ".rs", ".json"):
            b = path.read_bytes()
            manifest.append({"path": str(path.relative_to(here)), "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()})
    binding_bytes = args.published_file_manifest.read_bytes()
    binding = json.loads(binding_bytes)
    expected = {f["path"]:f for f in binding["files"]}
    matches = binding["source_commit"] == args.source_commit and set(expected) == {f["path"] for f in manifest}
    for f in manifest:
        remote = expected.get(f["path"],{})
        b = (here/f["path"]).read_bytes()
        blob = hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
        matches = matches and remote.get("sha256") == f["sha256"] and remote.get("bytes") == f["bytes"] and remote.get("git_blob") == blob
    dump(output/"SOURCE_MANIFEST.json", {"source_commit": args.source_commit,
         "published_binding_sha256":hashlib.sha256(binding_bytes).hexdigest(), "files": manifest,
         "published_binding_matches":bool(matches)})
    check("published_source_binding", matches)
    if not matches:
        dump(output/"RETURN.json", {"status":"SOURCE_BINDING_FAILED", "checks":checks,
                                   "source_commit":args.source_commit})
        return 1
    compiler = invoke([args.rustc, "-vV"])
    record_execution(compiler)
    dump(output/"COMPILER.json", compiler)
    binary = output/"p246_projector"
    build = invoke([args.rustc, "--edition=2021", "-O", "-D", "warnings", str(here/"rust/cli.rs"), "-o", str(binary)])
    record_execution(build)
    dump(output/"BUILD.json", build)
    if compiler["exit_code"] != 0 or build["exit_code"] != 0:
        dump(output/"RETURN.json", {"status": "BUILD_FAILED", "executions": executions,
                                   "source_commit":args.source_commit})
        return 1
    binary_sha = hashlib.sha256(binary.read_bytes()).hexdigest()
    fixed = [
        {"id": "dyadic_uniform", "mu": [-1., -.75, -.5, 0., .5, .75, 1.], "prior": [1.]*7},
        {"id": "dyadic_biased_prior", "mu": [-1., -.75, -.5, 0., .5, .75, 1.], "prior": [1., 2., 3., 4., 3., 2., 1.]},
        {"id": "P24_only_support", "mu": [-1., -.5, -.25, 0., .25, .5, 1.], "prior": [1.]*7},
    ]
    for name in ("b9_n64", "b9_n128", "b9_n256", "b6_n64"):
        item = json.loads((here/"inputs"/(name+"_birth11_input.json")).read_text())
        fixed.append({"id": name, "mu": item["mu"], "prior": item["prior"],
                      "source_input": name+"_birth11_input.json"})
    dump(output/"FIXED_INPUTS.json", fixed)
    for case in fixed:
        mu, prior, case_id = case["mu"], case["prior"], case["id"]
        original_mu, original_prior = array_digest(mu), array_digest(prior)
        for order in (4, 6):
            identity = f"{case_id}_P{order}"
            support = support_feasibility(mu, order)
            expected_support = ("INFEASIBLE_SUPPORT" if order == 6 and case_id in ("P24_only_support", "b9_n64")
                                else "STRICT_INTERIOR")
            check(identity+"_registered_support", support["status"] == expected_support,
                  expected=expected_support, actual=support["status"])
            row = {"id": identity, "case": case_id, "order": order, "support": support,
                   "registered_support": expected_support,
                   "input_mu_sha256": original_mu, "input_prior_sha256": original_prior}
            try:
                py = project_birth(mu, prior, order=order, declared_isotropic_birth=True)
                row["python"] = {"status": "PROJECTED", **dataclasses.asdict(py)}
            except ProjectionError as error:
                row["python"] = {"status": error.status, "details": error.details}
            call = invoke([str(binary), "--isotropic-birth"], stdin=payload(order, mu, prior))
            record_execution({"id": identity, **call})
            try:
                decoded = json.loads(call["stdout"])
                row["rust"] = decoded if isinstance(decoded, dict) else {"status":"MALFORMED_OUTPUT", "raw":call}
            except json.JSONDecodeError:
                row["rust"] = {"status": "MALFORMED_OUTPUT", "raw": call}
            is_feasible = expected_support == "STRICT_INTERIOR"
            if not is_feasible:
                check(identity+"_expected_infeasibility", row["python"]["status"] == expected_support and call["exit_code"] == 3 and not call["stderr"] and row["rust"].get("status") == expected_support, exact_status=support["status"])
            else:
                success = (row["python"]["status"] == "PROJECTED" and call["exit_code"] == 0
                           and not call["stderr"] and row["rust"].get("status") == "PROJECTED_NEEDS_EXACT_CERTIFICATE"
                           and row["rust"].get("order") == order
                           and "weights" in row["rust"])
                check(identity+"_executed", success)
                if success:
                    rust_weights = row["rust"]["weights"]
                    try:
                        row["rust_exact_certificate"] = exact_certificate(mu, rust_weights, order)
                    except ProjectionError as error:
                        row["rust_exact_certificate"] = {"status": error.status,
                                                         "max_abs_residual": None, "details":error.details}
                    diff = max(abs(a-b) for a, b in zip(py.weights, rust_weights))
                    row["cross_weight_max_abs"] = diff
                    check(identity+"_exact_gate", row["rust_exact_certificate"]["status"] == "PASS_SCOPED" and py.certificate["status"] == "PASS_SCOPED", max_rust_residual=row["rust_exact_certificate"]["max_abs_residual"])
                    check(identity+"_cross_implementation", diff <= 1e-12, max_abs=diff)
            check(identity+"_input_identity", array_digest(mu) == original_mu and array_digest(prior) == original_prior)
            projections.append(row)
            dump(output/"PROJECTIONS.json", projections)
    base = fixed[0]
    invalid = [
        ("not_isotropic", base["mu"], base["prior"], 6, False),
        ("asymmetric_mu", [-1., -.75, -.5, .01, .5, .75, 1.], base["prior"], 6, True),
        ("asymmetric_prior", base["mu"], [1., 1., 1., 1., 1., 1., 2.], 6, True),
        ("zero_prior", base["mu"], [1., 1., 1., 0., 1., 1., 1.], 6, True),
        ("negative_prior", base["mu"], [1., 1., 1., -1., 1., 1., 1.], 6, True),
        ("nonfinite", [-1., -.75, -.5, float("nan"), .5, .75, 1.], base["prior"], 6, True),
        ("out_of_range", [-1.1, -.75, -.5, 0., .5, .75, 1.1], base["prior"], 6, True),
        ("duplicate_mu", [-1., -.5, -.5, 0., .5, .5, 1.], base["prior"], 6, True),
        ("rank_deficient", [-.5, .5], [1., 1.], 6, True),
        ("invalid_order", base["mu"], base["prior"], 0, True),
    ]
    domain = []
    expected_python_rejections = {
        "not_isotropic":"NOT_ISOTROPIC_BIRTH", "asymmetric_mu":"REFLECTION_SOURCE_REQUIRED",
        "asymmetric_prior":"REFLECTION_PRIOR_REQUIRED", "zero_prior":"PRIOR_POSITIVITY_DOMAIN",
        "negative_prior":"PRIOR_POSITIVITY_DOMAIN", "nonfinite":"ANGULAR_INPUT_DOMAIN",
        "out_of_range":"ANGULAR_INPUT_DOMAIN", "duplicate_mu":"ANGULAR_ORDER_DOMAIN",
        "rank_deficient":"INFEASIBLE_AFFINE_SUPPORT", "invalid_order":"ORDER_DOMAIN",
    }
    for name, mu, prior, order, declared in invalid:
        try:
            project_birth(mu, prior, order=order, declared_isotropic_birth=declared)
            py_status = "UNEXPECTED_ACCEPTANCE"
        except ProjectionError as error:
            py_status = error.status
        call = invoke([str(binary)]+(["--isotropic-birth"] if declared else []), stdin=payload(order, mu, prior))
        record_execution({"id": "domain_"+name, **call})
        expected_exit, expected_status = ((2,"NOT_ISOTROPIC_BIRTH") if not declared else
            ((3,"FEASIBILITY_UNRESOLVED") if name == "rank_deficient" else (3,"INVALID_INPUT")))
        try:
            decoded = json.loads(call["stdout"])
            rust_status = decoded.get("status") if isinstance(decoded,dict) else "MALFORMED_OUTPUT"
        except json.JSONDecodeError:
            rust_status = "MALFORMED_OUTPUT"
        domain.append({"id": name, "python_status": py_status, "rust": call,
                       "expected_python_status":expected_python_rejections[name],
                       "expected_rust_status":expected_status, "expected_rust_exit":expected_exit})
        check("domain_"+name, py_status == expected_python_rejections[name]
              and call["exit_code"] == expected_exit and rust_status == expected_status and not call["stderr"])
    dump(output/"DOMAIN_CONTROLS.json", domain)

    try:
        project_birth(base["mu"], base["prior"], declared_isotropic_birth="false")
        declaration_status = "UNEXPECTED_ACCEPTANCE"
    except ProjectionError as error:
        declaration_status = error.status
    check("python_boolean_declaration_required", declaration_status == "NOT_ISOTROPIC_BIRTH", observed=declaration_status)

    # The standalone certificate is a separate trust boundary: a solver-success
    # label cannot bypass its domain checks. These are reviewer counterexamples.
    outside_beta = [Q(8797,23625), Q(388,3675), Q(2404,4725), Q(244,18375)]
    outside_weights = [float(outside_beta[3]/2),float(outside_beta[2]/2),float(outside_beta[1]/2),float(outside_beta[0]),float(outside_beta[1]/2),float(outside_beta[2]/2),float(outside_beta[3]/2)]
    certificate_controls = [
        ("certificate_invalid_order", base["mu"], [1/7]*7, 0, "ORDER_DOMAIN"),
        ("certificate_fractional_order", base["mu"], [1/7]*7, 6.0, "ORDER_DOMAIN"),
        ("certificate_outside_exact_moments", [-1.25,-.75,-.5,0.,.5,.75,1.25], outside_weights, 6, "ANGULAR_INPUT_DOMAIN"),
        ("certificate_duplicate_mu", [-1.,-.5,-.5,0.,.5,.5,1.], [1/7]*7, 6, "ANGULAR_ORDER_DOMAIN"),
        ("certificate_nonfinite_weight", base["mu"], [1.,1.,1.,float("inf"),1.,1.,1.], 6, "CERTIFICATE_NONFINITE"),
    ]
    certificate_results = []
    for name, mu, weights, order, expected in certificate_controls:
        try:
            certificate = exact_certificate(mu, weights, order)
            status = "UNEXPECTED_CERTIFICATE_RETURN"
        except ProjectionError as error:
            status = error.status
        certificate_results.append({"id":name,"status":status,"expected_status":expected})
        check(name, status == expected)
    dump(output/"CERTIFICATE_DOMAIN_CONTROLS.json", certificate_results)

    # Exact ideal quadrature is an independent control, not generated by either solver.
    beta = [Q(286,945), Q(32,105), Q(2048,6615), Q(61,735)]
    ideal = [float(beta[3]/2),float(beta[2]/2),float(beta[1]/2),float(beta[0]),float(beta[1]/2),float(beta[2]/2),float(beta[3]/2)]
    for row in projections:
        if row["case"].startswith("dyadic_") and row["order"] == 6 and row["python"]["status"] == "PROJECTED":
            check(row["id"]+"_rational_control", max(abs(x-y) for x,y in zip(row["python"]["weights"], ideal)) < 1e-16)

    strains = [str(D(k)/40) for k in range(-24,25)]
    small = ["0.001", "0.0005", "0.00025", "-0.001", "-0.0005", "-0.00025"]
    references = {d: decimal_continuum_response(d) for d in strains+small}
    responses, coefficients, asymptotics = [], [], []
    iso = [Q(0), -Q(8,5), Q(8,7), Q(368,175), -Q(248,77)]
    by_case = {c["id"]: c for c in fixed}
    with localcontext() as ctx:
        ctx.prec = 80
        for row in projections:
            if row["python"]["status"] != "PROJECTED":
                continue
            mu = by_case[row["case"]]["mu"]
            weights = row["python"]["weights"]
            coeff = response_taylor(mu, weights)
            difference = [a-b for a,b in zip(coeff,iso)]
            dd = [D(x.numerator)/D(x.denominator) for x in difference]
            moments = {str(l): sum((Q(w)*legendre(Q(m), l) for m,w in zip(mu,weights)),Q(0)) for l in (2,4,6,8,10,12)}
            coefficients.append({"id":row["id"],"actual_response_coefficients":[str(x) for x in coeff],"bias_coefficients":[str(x) for x in difference],"moments":{k:{"exact":str(v),"value":float(v)} for k,v in moments.items()}})
            leading = 2 if row["order"] == 4 else 3
            for d in strains+small:
                response = decimal_ray_response(mu, weights, d)
                ref = references[d]
                error = D(response["A"])-D(ref["A"])
                responses.append({"id":row["id"],"d":d,"A":response["A"],"A_iso":ref["A"],"signed_error":str(error)})
                if row["case"] == "dyadic_uniform" and d in small[:3]:
                    delta = D(d)
                    corrected = error-sum(dd[k]*delta**k for k in range(leading))
                    ratio = corrected/delta**leading
                    rel = abs((ratio-dd[leading])/dd[leading])
                    asymptotics.append({"id":row["id"],"d":d,"leading_power":leading,"measured_coefficient":str(ratio),"exact_stored_coefficient":str(dd[leading]),"relative_error":str(rel)})
                    check(row["id"]+"_leading_"+d, rel <= D(".02"), relative_error=float(rel))
                    if row["order"] == 6:
                        fourth = (corrected-dd[3]*delta**3)/delta**4
                        rel4 = abs((fourth-dd[4])/dd[4])
                        asymptotics.append({"id":row["id"]+"_quartic","d":d,"leading_power":4,"measured_coefficient":str(fourth),"exact_stored_coefficient":str(dd[4]),"relative_error":str(rel4)})
                        check(row["id"]+"_quartic_"+d, rel4 <= D(".02"), relative_error=float(rel4))
            if row["order"] == 6:
                expected3 = Q(288,143)*moments["8"]
                expected4 = -Q(7200,2717)*moments["8"]+Q(136080,46189)*moments["10"]
                check(row["id"]+"_P8_P10_coefficients", abs(difference[3]-expected3) < Q(1,10**12) and abs(difference[4]-expected4) < Q(1,10**12), delta3=float(difference[3]-expected3), delta4=float(difference[4]-expected4))
    dump(output/"ANGULAR_RESPONSES.json", responses)
    dump(output/"TAYLOR_COEFFICIENTS.json", coefficients)
    dump(output/"SMALL_STRAIN_CHECKS.json", asymptotics)
    dump(output/"REFERENCE_VALUES.json", references)
    dump(output/"EXECUTIONS.json", executions)
    after = all(hashlib.sha256((here/f["path"]).read_bytes()).hexdigest() == f["sha256"] for f in manifest)
    check("source_unchanged_during_validation", after)
    failed = [c for c in checks if not c["pass"]]
    result = {"schema":"BASS_S11_VALIDATION_RETURN_V1","status":"PASS_SCOPED" if not failed else "FAIL", "source_commit":args.source_commit,"source_manifest_sha256":hashlib.sha256((output/"SOURCE_MANIFEST.json").read_bytes()).hexdigest(),"binary_sha256":binary_sha,"completed_at_utc":datetime.now(timezone.utc).isoformat(),"platform":platform.platform(),"python":sys.version,"elapsed_seconds":time.monotonic()-started,"max_individual_child_RSS_KiB":resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,"RSS_scope":"RUSAGE_CHILDREN cumulative maximum individual child, including compile; not simultaneous process-tree peak", "checks":checks,"check_count":len(checks),"pass_count":len(checks)-len(failed),"failures":failed,"projection_inputs":len(projections),"domain_controls":len(domain),"response_points":len(responses),"old_campaign_replays":0,"old_native_history_replays":0,"optimization_cycles":0,"NCP_runs":0,"scope":"new isolated birth projector and factorized collisionless angular response; no spectral deposition or native history integration"}
    dump(output/"RETURN.json", result)
    print(json.dumps({k:result[k] for k in ("status","check_count","pass_count","projection_inputs","domain_controls","response_points","elapsed_seconds","failures")},ensure_ascii=False))
    return 0 if not failed else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rustc", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--published-file-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if len(args.source_commit) != 40 or any(c not in "0123456789abcdef" for c in args.source_commit):
        parser.error("source commit must be a full lowercase SHA")
    here, output = Path(__file__).resolve().parent, args.output.resolve()
    # Refuse to touch any previous output. Exception receipts belong only to a
    # directory created by this process, never to a reused or completed run.
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    try:
        return run(args, here, output)
    except Exception as error:
        failure = {"status":"INPUT_MISSING" if isinstance(error,FileNotFoundError) else "EXECUTION_EXCEPTION",
                   "source_commit":args.source_commit,"exception_type":type(error).__name__,
                   "exception":str(error),"traceback":traceback.format_exc(),
                   "elapsed_seconds":time.monotonic()-started,"old_campaign_replays":0,
                   "old_native_history_replays":0,"optimization_cycles":0,"NCP_runs":0}
        dump(output/"FAILURE.json",failure)
        dump(output/"RETURN.json",failure)
        print(json.dumps(failure,ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
