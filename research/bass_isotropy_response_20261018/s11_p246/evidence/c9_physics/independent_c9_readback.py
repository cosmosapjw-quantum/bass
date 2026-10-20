"""Independent C9 readback of finalized S11 outputs; no solver is imported.

Uses Rodrigues polynomials, exact support-factor expectations, Legendre D0..D4
identities, and adaptive positive composite Simpson integration. The only new
scalar angular reference points are d=-.6,-.3,0,.3,.6; absolute diagnostic5e-13.
The original normalization/P2/P4 gate3e-15 is retained and P6 uses that same gate.
All files supplied as main-run evidence are read-only. Output must be a new dir.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import platform
import resource
import struct
import sys
import time
import traceback


MOMENT_GATE = Q(3, 10**15)
SCALAR_GATE = Decimal("5e-13")
REFERENCE_POINTS = ("-0.6", "-0.3", "0", "0.3", "0.6")
EXPECTED_CASES = ("dyadic_uniform", "dyadic_biased_prior", "P24_only_support",
                  "b9_n64", "b9_n128", "b9_n256", "b6_n64")
EXPECTED_INFEASIBLE = {"P24_only_support_P6", "b9_n64_P6"}
EVIDENCE_FILES = ("RETURN.json", "SOURCE_MANIFEST.json", "FIXED_INPUTS.json",
                  "PROJECTIONS.json", "TAYLOR_COEFFICIENTS.json",
                  "REFERENCE_VALUES.json", "ANGULAR_RESPONSES.json",
                  "DOMAIN_CONTROLS.json", "CERTIFICATE_DOMAIN_CONTROLS.json",
                  "EXECUTIONS.json")


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False,
                               allow_nan=False)+"\n")


def file_record(path):
    data = path.read_bytes()
    return {"path": str(path), "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest()}


def bit_digest(values):
    return hashlib.sha256(b"".join(struct.pack("<d", float(v))
                                   for v in values)).hexdigest()


@lru_cache(None)
def rodrigues_terms(ell):
    # Differentiate (x*x-1)^ell exactly, then divide by 2^ell ell!.
    return tuple((ell-2*k,
                  Q((-1)**k * math.factorial(2*ell-2*k),
                    2**ell * math.factorial(k) * math.factorial(ell-k)
                    * math.factorial(ell-2*k)))
                 for k in range(ell//2+1))


def p_exact(mu, ell):
    return sum((c*mu**power for power, c in rodrigues_terms(ell)), Q(0))


def exact_moments(mu, weights):
    m, w = list(map(Q, mu)), list(map(Q, weights))
    return {ell: sum((a*p_exact(x, ell) for x, a in zip(m, w)), Q(0))
            for ell in range(0, 13, 2)}


def independent_certificate(mu, weights, order):
    shape = (type(order) is int and order in (4, 6)
             and len(mu) == len(weights) and 2 <= len(mu) <= 4096)
    finite = all(math.isfinite(x) for x in [*mu, *weights])
    if not shape or not finite:
        return {"pass": False, "shape": shape, "finite": finite}, None
    moments = exact_moments(mu, weights)
    residuals = {0: moments[0]-1,
                 **{ell: moments[ell] for ell in range(2, order+1, 2)}}
    domain = all(abs(x) <= 1 for x in mu)
    order_ok = all(a < b for a, b in zip(mu, mu[1:]))
    positive = all(w > 0 for w in weights)
    parity = (all(x == -y for x, y in zip(mu, reversed(mu)))
              and weights == list(reversed(weights)))
    passed = (domain and order_ok and positive and parity
              and all(abs(v) <= MOMENT_GATE for v in residuals.values()))
    return {"pass": passed, "gate_exact": str(MOMENT_GATE),
            "domain": domain, "strict_order": order_ok,
            "strict_positive": positive, "reflection_exact": parity,
            "minimum_weight": min(weights),
            "residuals_exact": {str(k): str(v) for k, v in residuals.items()},
            "max_abs_residual_exact": str(max(map(abs, residuals.values()))),
            "mu_sha256": bit_digest(mu), "weight_sha256": bit_digest(weights)}, moments


def factor_expectation(roots):
    """Multiply support factors, then integrate z^k using 1/(2k+1).

    Does not call or copy the projector's closed quadratic/cubic slack formula.
    """
    coefficients = [Q(1)]
    for root in roots:
        new = [Q(0)]*(len(coefficients)+1)
        for i, value in enumerate(coefficients):
            new[i] -= root*value
            new[i+1] += value
        coefficients = new
    return sum((a/Q(2*k+1) for k, a in enumerate(coefficients)), Q(0))


def independent_support(mu, order):
    z = sorted({Q(x)**2 for x in mu})
    n, degree = len(z), order//2
    if n <= degree:
        # This branch is not used by the registered 14 projection pairs.
        # The exact dyadic monic-factor obstruction excludes this rank.
        vanishing_mean = factor_expectation(z)
        return {"status": "INFEASIBLE_AFFINE_SUPPORT" if vanishing_mean else
                "UNRESOLVED_AFFINE_COMPATIBILITY", "distinct_z": n,
                "vanishing_factor_expectation_exact": str(vanishing_mean)}
    roots_and_signs = []
    if order == 4:
        roots_and_signs += [("lower", [i, i+1], 1) for i in range(n-1)]
        roots_and_signs.append(("upper", [0, n-1], -1))
    else:
        roots_and_signs += [("lower", [0, i, i+1], 1) for i in range(1, n-1)]
        roots_and_signs += [("upper", [i, i+1, n-1], -1) for i in range(n-2)]
    records = []
    for kind, indices, sign in roots_and_signs:
        slack = sign*factor_expectation([z[i] for i in indices])
        records.append({"kind": kind, "indices": indices,
                        "slack_exact": str(slack)})
    minimum = min(Q(r["slack_exact"]) for r in records)
    status = ("STRICT_INTERIOR" if minimum > 0 else
              "BOUNDARY_ONLY" if minimum == 0 else "INFEASIBLE_SUPPORT")
    return {"status": status, "distinct_z": n,
            "minimum_slack_exact": str(minimum), "facets": records}


# Independent exact Legendre derivative identities. D3/D4 and the normalized
# high-order coefficients are verified by the retained 25-check math unit;
# D0=P2, D1=-1/2-6z+9z^2/2 and D2=-1/2+63z/2-135z^2/2+81z^3/2
# follow directly from differentiating R^2. Row n means d^n D/dd^n at d=0.
DERIVATIVES = (
    (Q(0), Q(1)),
    (-Q(8, 5), -Q(10, 7), Q(36, 35)),
    (Q(16, 7), Q(12, 7), -Q(216, 77), Q(216, 77)),
    (-Q(96, 35), Q(200, 77), -Q(43632, 5005), -Q(864, 77), Q(1728, 143)),
    (-Q(320, 77), Q(4528, 143), Q(10080, 143), -Q(116640, 1309),
     -Q(172800, 2717), Q(3265920, 46189)),
)
ISOTROPIC_COEFFICIENTS = (Q(0), -Q(8, 5), Q(8, 7), Q(368, 175), -Q(248, 77))


def independent_taylor(moments):
    g = [sum((c*moments[2*k] for k, c in enumerate(row)), Q(0))
         / math.factorial(n) for n, row in enumerate(DERIVATIVES)]
    f = [moments[0]]+[-2*g[n]/(n+1) for n in range(4)]
    result = []
    for n in range(5):
        result.append((g[n]-sum((f[k]*result[n-k] for k in range(1, n+1)), Q(0)))/f[0])
    return result


def simpson_at(d, n):
    """Positive composite Simpson weights; standard binary64 scalar arithmetic."""
    ep, ea = math.exp(2*d), math.exp(-4*d)
    f_terms, g_terms = [], []
    for i in range(n+1):
        mu = i/n  # dyadic since every grid size is a power of two
        z = mu*mu
        a, b = ep*(1-z), ea*z
        r = math.sqrt(a+b)
        weight = 1 if i in (0, n) else (4 if i % 2 else 2)
        f_terms.append(weight*r)
        g_terms.append(weight*(b-a/2)/r)
    f, g = math.fsum(f_terms)/(3*n), math.fsum(g_terms)/(3*n)
    return {"F": f, "G": g, "A": g/f}


def simpson_truncation_bounds(d, n):
    """Analytic fourth-derivative bound evaluated in binary64.

    These are truncation-bound estimates, not outward-rounded floating interval
    certificates. Final scalar comparisons remain diagnostics at5e-13.
    """
    ep, ea = math.exp(2*d), math.exp(-4*d)
    q_min, b = min(ep, ea), abs(ea-ep)
    f4 = (3*b*b*q_min**(-1.5)+18*b**3*q_min**(-2.5)
          +15*b**4*q_min**(-3.5))
    inv2 = b*q_min**(-1.5)+3*b*b*q_min**(-2.5)
    inv3 = 9*b*b*q_min**(-2.5)+15*b**3*q_min**(-3.5)
    inv4 = (9*b*b*q_min**(-2.5)+90*b**3*q_min**(-3.5)
            +105*b**4*q_min**(-4.5))
    c = ea+ep/2
    numerator_max = max(ep/2, ea)
    g4 = numerator_max*inv4+8*c*inv3+12*c*inv2
    f_error, g_error = f4/(180*n**4), g4/(180*n**4)
    # The exact continuum obeys F>=sqrt(q_min), |G/F|<=1.
    a_error = (f_error+g_error)/(math.sqrt(q_min)-f_error)
    return {"F": f_error, "G": g_error, "A": a_error}


def adaptive_scalar_reference(d_text):
    d = float(d_text)
    records, previous = [], None
    for power in range(8, 19):
        n = 2**power
        values, bounds = simpson_at(d, n), simpson_truncation_bounds(d, n)
        change = (None if previous is None else
                  max(abs(values[k]-previous[k]) for k in ("F", "G", "A")))
        records.append({"N": n, "values": values,
                        "analytic_truncation_bound_estimates": bounds,
                        "maximum_change_from_previous_grid": change})
        if (previous is not None and change <= float(SCALAR_GATE)/20
                and max(bounds.values()) <= float(SCALAR_GATE)/20):
            return {"d": d_text, "converged": True, "values": values,
                    "refinement_records": records}
        previous = values
    return {"d": d_text, "converged": False, "values": records[-1]["values"],
            "refinement_records": records}


def scalar_ray_response(mu, weights, d_text):
    d = float(d_text)
    ep, ea = math.exp(2*d), math.exp(-4*d)
    fs, gs = [], []
    for x, w in zip(mu, weights):
        z = x*x
        a, b = ep*(1-z), ea*z
        r = math.sqrt(a+b)
        fs.append(w*r)
        gs.append(w*(b-a/2)/r)
    f, g = math.fsum(fs), math.fsum(gs)
    return g/f


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    if len(args.source_commit) != 40 or any(c not in "0123456789abcdef" for c in args.source_commit):
        parser.error("source commit must be a full lowercase SHA")
    args.output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    checks = []

    def check(identity, passed, **evidence):
        checks.append({"id": identity, "pass": bool(passed), **evidence})

    own_record = file_record(Path(__file__).resolve())
    try:
        records = [file_record(args.evidence/name) for name in EVIDENCE_FILES]
        write_json(args.output/"READBACK_INPUT_MANIFEST.json", records)
        data = {name: json.loads((args.evidence/name).read_text()) for name in EVIDENCE_FILES}
        main_result = data["RETURN.json"]
        check("main_result_is_completed_PASS_SCOPED", main_result["status"] == "PASS_SCOPED")
        check("main_check_aggregate_identity", main_result["check_count"] == main_result["pass_count"]
              == len(main_result["checks"]) == 101
              and all(c["pass"] is True for c in main_result["checks"])
              and not main_result["failures"])
        check("expected_main_source_commit", main_result["source_commit"] == args.source_commit
              == data["SOURCE_MANIFEST.json"]["source_commit"])
        check("main_source_manifest_identity", main_result["source_manifest_sha256"]
              == file_record(args.evidence/"SOURCE_MANIFEST.json")["sha256"])
        check("main_published_source_binding", data["SOURCE_MANIFEST.json"].get("published_binding_matches") is True)
        cases = {c["id"]: c for c in data["FIXED_INPUTS.json"]}
        expected_ids = {f"{name}_P{order}" for name in EXPECTED_CASES for order in (4, 6)}
        rows = data["PROJECTIONS.json"]
        check("fixed_case_identity", set(cases) == set(EXPECTED_CASES) and len(cases) == 7)
        check("projection_pair_identity", len(rows) == 14 and {r["id"] for r in rows} == expected_ids)
        raw_executions = data["EXECUTIONS.json"]
        pair_executions = {r["id"]: r for r in raw_executions if r.get("id") in expected_ids}
        check("raw_execution_cardinality", len(raw_executions) == 26
              and set(pair_executions) == expected_ids
              and sum(str(r.get("id", "")).startswith("domain_") for r in raw_executions) == 10)
        support_records, certificate_records, taylor_records = [], [], []
        projected_moments = {}
        for row in rows:
            identity, order = row["id"], row["order"]
            case = cases[row["case"]]
            mu, prior = case["mu"], case["prior"]
            check(identity+"_input_bits", row["input_mu_sha256"] == bit_digest(mu)
                  and row["input_prior_sha256"] == bit_digest(prior))
            execution = pair_executions[identity]
            check(identity+"_raw_exit_identity", execution["execution_status"] == "COMPLETED"
                  and execution["exit_code"] == (3 if identity in EXPECTED_INFEASIBLE else 0)
                  and not execution["stderr"]
                  and json.loads(execution["stdout"]) == row["rust"])
            support = independent_support(mu, order)
            expected_status = "INFEASIBLE_SUPPORT" if identity in EXPECTED_INFEASIBLE else "STRICT_INTERIOR"
            check(identity+"_independent_support", support["status"] == expected_status
                  == row["support"]["status"])
            if "minimum_slack_exact" in support:
                check(identity+"_support_minimum_exact", Q(support["minimum_slack_exact"])
                      == Q(row["support"]["minimum_slack"]["exact"]))
            support_records.append({"id": identity, **support})
            if identity in EXPECTED_INFEASIBLE:
                check(identity+"_negative_admission", row["python"]["status"] == "INFEASIBLE_SUPPORT"
                      and row["rust"]["status"] == "INFEASIBLE_SUPPORT")
                continue
            check(identity+"_paired_success", row["python"]["status"] == "PROJECTED"
                  and row["rust"]["status"] == "PROJECTED_NEEDS_EXACT_CERTIFICATE")
            for engine in ("python", "rust"):
                weights = row[engine].get("weights", [])
                cert, moments = independent_certificate(mu, weights, order)
                check(identity+"_"+engine+"_independent_exact_gate", cert["pass"])
                certificate_records.append({"id": identity, "engine": engine, **cert})
                stored = (row["python"]["certificate"] if engine == "python"
                          else row.get("rust_exact_certificate", {}))
                norm_match = (cert["pass"] and Q(stored["normalization"]["exact"])
                              == Q(cert["residuals_exact"]["0"]))
                moment_match = (cert["pass"] and all(Q(stored["moments"][str(ell)]["exact"])
                                == moments[ell] for ell in range(2, order+1, 2)))
                check(identity+"_"+engine+"_stored_certificate_identity", norm_match and moment_match
                      and stored.get("mu_sha256") == cert["mu_sha256"]
                      and stored.get("weight_sha256") == cert["weight_sha256"])
                if engine == "python" and cert["pass"]:
                    projected_moments[identity] = moments
        write_json(args.output/"EXACT_SUPPORT_READBACK.json", support_records)
        write_json(args.output/"EXACT_WEIGHT_READBACK.json", certificate_records)

        taylor_rows = data["TAYLOR_COEFFICIENTS.json"]
        check("taylor_row_identity", len(taylor_rows) == 12
              and {r["id"] for r in taylor_rows} == expected_ids-EXPECTED_INFEASIBLE)
        for row in taylor_rows:
            moments = projected_moments[row["id"]]
            coefficients = independent_taylor(moments)
            check(row["id"]+"_Rodrigues_moment_readback", all(
                Q(row["moments"][str(ell)]["exact"]) == moments[ell]
                for ell in range(2, 13, 2)))
            check(row["id"]+"_Legendre_derivative_Taylor_readback",
                  coefficients == list(map(Q, row["actual_response_coefficients"]))
                  and [c-i for c, i in zip(coefficients, ISOTROPIC_COEFFICIENTS)]
                  == list(map(Q, row["bias_coefficients"])))
            taylor_records.append({"id": row["id"],
                                   "independent_coefficients_exact": list(map(str, coefficients))})
        write_json(args.output/"EXACT_TAYLOR_READBACK.json", taylor_records)

        references = {Decimal(k): v for k, v in data["REFERENCE_VALUES.json"].items()}
        scalar_records = []
        with localcontext() as context:
            context.prec = 80
            for d_text in REFERENCE_POINTS:
                scalar = adaptive_scalar_reference(d_text)
                check("Simpson_refinement_"+d_text, scalar["converged"])
                observed = references[Decimal(d_text)]
                comparisons = {}
                for key in ("F", "G", "A"):
                    difference = abs(Decimal.from_float(scalar["values"][key])-Decimal(observed[key]))
                    check("continuum_"+key+"_"+d_text, difference <= SCALAR_GATE,
                          absolute_difference=str(difference), gate=str(SCALAR_GATE))
                    comparisons[key] = {"stored": observed[key], "absolute_difference": str(difference)}
                scalar_records.append({**scalar, "comparisons": comparisons})
                write_json(args.output/"SCALAR_CONTINUUM_READBACK.json", scalar_records)
            responses = data["ANGULAR_RESPONSES.json"]
            response_map = {(r["id"], Decimal(r["d"])): r for r in responses}
            check("response_row_cardinality", len(responses) == 660 and len(response_map) == 660)
            ray_records = []
            for row in rows:
                if row["id"] in EXPECTED_INFEASIBLE:
                    continue
                case, weights = cases[row["case"]], row["python"]["weights"]
                for d_text in REFERENCE_POINTS:
                    stored = response_map[(row["id"], Decimal(d_text))]
                    calculated = scalar_ray_response(case["mu"], weights, d_text)
                    difference = abs(Decimal.from_float(calculated)-Decimal(stored["A"]))
                    check(row["id"]+"_ray_readback_"+d_text, difference <= SCALAR_GATE,
                          absolute_difference=str(difference), gate=str(SCALAR_GATE))
                    ray_records.append({"id": row["id"], "d": d_text,
                                        "independent_binary64_A": calculated,
                                        "stored_A": stored["A"],
                                        "absolute_difference": str(difference)})
            write_json(args.output/"SCALAR_RAY_READBACK.json", ray_records)
        check("domain_control_cardinality", len(data["DOMAIN_CONTROLS.json"]) == 10
              and len(data["CERTIFICATE_DOMAIN_CONTROLS.json"]) == 5)
        check("main_evidence_bytes_unchanged", records == [file_record(args.evidence/name) for name in EVIDENCE_FILES])
        check("review_source_bytes_unchanged", own_record == file_record(Path(__file__).resolve()))
        failed = [c for c in checks if not c["pass"]]
        result = {"schema": "BASS_S11_INDEPENDENT_C9_READBACK_V1",
                  "status": "PASS_SCOPED" if not failed else "FAIL",
                  "main_source_commit": args.source_commit, "review_source": own_record,
                  "command": [sys.executable, *sys.argv],
                  "completed_at_utc": datetime.now(timezone.utc).isoformat(),
                  "python": sys.version, "platform": platform.platform(),
                  "elapsed_seconds": time.monotonic()-started,
                  "process_max_RSS_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  "check_count": len(checks), "pass_count": len(checks)-len(failed),
                  "checks": checks, "failures": failed,
                  "projection_pairs": len(rows), "positive_weight_certificates": len(certificate_records),
                  "Taylor_rows": len(taylor_records), "continuum_points": len(scalar_records),
                  "finite_ray_readbacks": len(ray_records),
                  "new_solver_executions": 0, "old_campaign_replays": 0,
                  "old_native_history_replays": 0, "optimization_cycles": 0, "NCP_runs": 0,
                  "scope": "Read-only independent exact moment/support/Taylor and five-point scalar angular diagnostics; no ODE, spectral deposition, reactive history or production admission."}
        write_json(args.output/"RETURN.json", result)
        print(json.dumps({k: result[k] for k in ("status", "check_count", "pass_count",
              "projection_pairs", "positive_weight_certificates", "Taylor_rows", "continuum_points",
              "finite_ray_readbacks", "elapsed_seconds", "failures")}))
        return 0 if not failed else 1
    except Exception as error:
        failure = {"schema": "BASS_S11_INDEPENDENT_C9_READBACK_V1", "status": "EXECUTION_EXCEPTION",
                   "main_source_commit": args.source_commit, "review_source": own_record,
                   "exception_type": type(error).__name__, "exception": str(error),
                   "traceback": traceback.format_exc(), "checks_completed_before_exception": checks,
                   "elapsed_seconds": time.monotonic()-started, "new_solver_executions": 0,
                   "old_campaign_replays": 0, "old_native_history_replays": 0,
                   "optimization_cycles": 0, "NCP_runs": 0}
        write_json(args.output/"FAILURE.json", failure)
        write_json(args.output/"RETURN.json", failure)
        print(json.dumps({"status": failure["status"], "exception": failure["exception"]}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
