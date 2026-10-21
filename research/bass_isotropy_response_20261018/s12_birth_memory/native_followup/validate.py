"""S12 single-case native observer; Python standard library only.

The numerical gates and physical observables are inherited from the pinned S8
observer. This module never calls a projector or evolves any photon state.
Returned Rust weights are provisional until this exact rational admission.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import struct


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("DUPLICATE_JSON_KEY:" + key)
        out[key] = value
    return out


def load_json(text):
    def invalid(value):
        raise ValueError("NONFINITE_JSON:" + value)
    return json.loads(text, object_pairs_hook=unique_object, parse_constant=invalid)


def require_finite(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("NONFINITE_VALUE")
    if isinstance(value, dict):
        for child in value.values():
            require_finite(child)
    elif isinstance(value, list):
        for child in value:
            require_finite(child)


def vector(value, size, label):
    if not isinstance(value, list) or len(value) != size:
        raise ValueError(label + ":SHAPE")
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in value):
        raise ValueError(label + ":DOMAIN")
    return value


def positive(value, label):
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or value <= 0):
        raise ValueError(label+":FINITE_POSITIVE_REQUIRED")
    return value


def nonnegative_residual(value, label):
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or value < 0):
        raise ValueError(label+":FINITE_NONNEGATIVE_RESIDUAL_REQUIRED")
    return value


def inventory(value, label):
    result = vector(value, 3, label)
    positive(result[0], label+":N")
    positive(result[1], label+":U")
    # Anisotropic stress is signed; only number and energy are denominators.
    return result


def max_abs_diff(a, b):
    if len(a) != len(b):
        raise ValueError("VECTOR_LENGTH")
    return max((abs(x - y) for x, y in zip(a, b)), default=0.0)


def kernel(d, mu):
    w = math.exp(2*d)*(1-mu*mu)
    v = math.exp(-4*d)*mu*mu
    r = math.sqrt(w+v)
    return r, (v-w/2)/r


def source_rate(u):
    """Pinned S8/S7 MD14 source-rate observer; no new normalization claim."""
    zp = 21*math.exp(-u)
    sfr = .015*zp**2.7/(1+(zp/2.9)**5.6)
    log_yield = 1/(.00038*.002**.227+.01858)-math.log10(2.55)
    return .2*10**log_yield*sfr/(3.085677581491367e24**3*1.88e-7)


def exact_moments(mu, weights):
    if len(mu) != len(weights):
        raise ValueError("EXACT_MOMENT_SHAPE")
    values = [Fraction(0), Fraction(0), Fraction(0)]
    for m, weight in zip(mu, weights):
        z = Fraction.from_float(float(m))**2
        w = Fraction.from_float(float(weight))
        values[0] += w
        values[1] += w*(3*z-1)/2
        values[2] += w*(35*z*z-30*z+3)/8
    return values


@lru_cache(maxsize=2)
def isotropic_gl(n):
    """Standalone GL128/256 reference using the Legendre recurrence.

    S8's two-order agreement remains a scoped angular control, not a full
    spectral convergence proof. No interpolation of native outputs is used.
    """
    if n not in (128, 256):
        raise ValueError("REFERENCE_ORDER")
    mu, weights = [0.0]*n, [0.0]*n
    for i in range(n//2):
        x = math.cos(math.pi*(i+.75)/(n+.5))
        for _ in range(48):
            pm, p = 1.0, x
            for k in range(2, n+1):
                pm, p = p, ((2*k-1)*x*p-(k-1)*pm)/k
            derivative = n*(x*p-pm)/(x*x-1)
            nxt = x-p/derivative
            if abs(nxt-x) <= 2*math.ulp(1.0):
                x = nxt
                break
            x = nxt
        else:
            raise ValueError("REFERENCE_GL_ROOT")
        pm, p = 1.0, x
        for k in range(2, n+1):
            pm, p = p, ((2*k-1)*x*p-(k-1)*pm)/k
        derivative = n*(x*p-pm)/(x*x-1)
        w = 1/((1-x*x)*derivative*derivative)
        if not 0 < x < 1 or not w > 0 or not math.isfinite(w):
            raise ValueError("REFERENCE_GL_DOMAIN")
        mu[i], mu[n-1-i] = -x, x
        weights[i] = weights[n-1-i] = w
    if abs(math.fsum(weights)-1) > 3e-14 or any(a >= b for a, b in zip(mu, mu[1:])):
        raise ValueError("REFERENCE_GL_NORMALIZATION_ORDER")
    return tuple(mu), tuple(weights)


def old_identity(row, required_sha):
    if row.get("old_n_mu") != 32 or row.get("old_cell_count") != 3072:
        raise ValueError("OLD_BLOCK_GRID_CHANGED")
    packed = []
    for label in ("before", "after"):
        arrays = [[0]*3072 for _ in range(4)]
        seen = set()
        for item in row["old_sparse_"+label]:
            if (not isinstance(item, list) or len(item) != 5 or type(item[0]) is not int
                    or not 0 <= item[0] < 3072 or item[0] in seen):
                raise ValueError("OLD_SPARSE_INPUT")
            seen.add(item[0])
            for j, word in enumerate(item[1:]):
                if not isinstance(word, str) or len(word) != 16 or any(c not in "0123456789abcdef" for c in word):
                    raise ValueError("OLD_BIT_PATTERN")
                arrays[j][item[0]] = int(word, 16)
        data = b"".join(struct.pack("<Q", word) for array in arrays for word in array)
        fnv = 0xcbf29ce484222325
        for byte in data:
            fnv = ((fnv ^ byte)*0x100000001b3) & ((1 << 64)-1)
        if f"{fnv:016x}" != row["old_digest_"+label+"_fnv1a64"]:
            raise ValueError("OLD_REPORTED_DIGEST")
        if hashlib.sha256(data).hexdigest() != required_sha:
            raise ValueError("OLD_DECLARED_FULL_INPUT_IDENTITY")
        packed.append(data)
    if packed[0] != packed[1]:
        raise ValueError("OLD_BLOCK_MUTATED")
    return required_sha


def validate(path, contract, original_failure, baseline):
    records = [load_json(line) for line in Path(path).read_text().splitlines() if line.strip()]
    require_finite(records)
    if len(records) != 2:
        raise ValueError("EXACTLY_ONE_ROW_AND_COMPLETION_REQUIRED")
    row, done = records
    if (done.get("schema") != "bass.native.followup.s12.complete.v1" or type(done.get("rows")) is not int
            or done["rows"] != 1 or done.get("owner_commit") != contract["owner_commit"]
            or done.get("source_id") != contract["source_id"]):
        raise ValueError("COMPLETION_IDENTITY")
    if row.get("schema") != "bass.native.followup.s12.row.v1":
        raise ValueError("ROW_SCHEMA")
    for key, expected in contract["case"].items():
        if row.get(key) != expected or isinstance(row.get(key), bool):
            raise ValueError("CASE_IDENTITY:" + key)
    if row.get("internal_moment_tolerance") != contract["internal_legacy_tolerance"]:
        raise ValueError("LEGACY_INTERNAL_TOLERANCE_CHANGED")
    if row.get("status") != "MEASURED":
        # Binary completion is not scientific success. Preserve any numerical
        # failure exactly, and let the wrapper exit nonzero after writing it.
        return {"schema": "BASS_S12_NATIVE_ANALYSIS_V1", "status": "FAILED_NATIVE_CASE",
                "integrity_gates_pass": False, "completed_native_histories": 0,
                "case_id": row.get("case_id"), "retained_failure_row": row,
                "angular_accuracy_target_met": None, "completed_old_cases_replayed": 0}
    if row.get("source_id") != contract["source_id"] or len(row.get("births", [])) != 16:
        raise ValueError("SOURCE_OR_BIRTH_COUNT")
    for key in ("max_increment_ledger_n_relative", "max_increment_ledger_u_relative",
                "max_native_reported_ledger_relative", "max_cell_add_absolute", "max_cell_add_relative"):
        nonnegative_residual(row.get(key), key)
    for key in ("n_final", "u_final", "predicted_u"):
        positive(row.get(key), key)
    gates = contract["gates"]
    checks = []
    def check(ok, label, value=None):
        checks.append({"gate": label, "pass": bool(ok), "value": value})
    n = 64
    nu = vector(row["reference_nu"], n, "REFERENCE_NU")
    q = vector(row["reference_count_fraction"], n, "REFERENCE_Q")
    check(all(-1 < v < 1 for v in nu) and all(a < b for a, b in zip(nu, nu[1:])), "REFERENCE_DOMAIN_ORDER")
    check(min(q) > 0 and abs(math.fsum(q)-1) <= gates["reference_gl_normalization_absolute"], "REFERENCE_POSITIVE_NORMALIZATION")
    check(max_abs_diff(nu, [-v for v in nu[::-1]]) <= gates["reflection_absolute"]
          and max_abs_diff(q, q[::-1]) <= gates["reflection_absolute"], "REFERENCE_REFLECTION")
    check(max_abs_diff(nu, original_failure["reference_nu"]) <= gates["reference_gl_node_absolute"]
          and max_abs_diff(q, original_failure["reference_count_fraction"]) <= gates["reference_gl_weight_absolute"], "REUSED_ORIGINAL_REFERENCE_GRID")
    check(row.get("spectral_bits_identical") is True and row.get("source_rate_bits_identical") is True,
          "SPECTRAL_AND_RATE_BITS_UNCHANGED")
    check(row["spectral_digest_fnv1a64"] == baseline["selected_fields"]["spectral_digest_fnv1a64"], "REUSED_SPECTRAL_DIGEST")
    old_sha = old_identity(row, contract["old_stock_full_arrays_sha256"])
    check(row.get("survivors_bitwise_frozen") is True, "FROZEN_SURVIVOR_BLOCKS")
    gate = Fraction(contract["gate_rational"])
    pn, pu, pp, qu, qp = [], [], [], [], []
    continuum = {128: [[], []], 256: [[], []]}
    certificates, birth_digests = [], []
    for j, birth in enumerate(row["births"]):
        prefix = f"birth{j}:"
        dispatch = "legacy_P24" if j < 11 else "S11_P24"
        check(birth.get("projector") == dispatch, prefix+"PROJECTOR_DISPATCH")
        u = .8*(j+.5)/16
        b = .9+.2*u
        mu = vector(birth["mu"], n, prefix+"MU")
        prior = vector(birth["prior"], n, prefix+"PRIOR")
        alpha = vector(birth["alpha"], n, prefix+"ALPHA")
        ea = vector(birth["energy_alpha"], n, prefix+"ENERGY_ALPHA")
        na = vector(birth["photon_alpha"], n, prefix+"PHOTON_ALPHA")
        rb = [math.sqrt(math.exp(2*b)*(1-v*v)+math.exp(-4*b)*v*v) for v in nu]
        expected_mu = [math.exp(-2*b)*v/r for v, r in zip(nu, rb)]
        raw_prior = [weight/r**3 for weight, r in zip(q, rb)]
        mass = math.fsum(raw_prior)
        expected_prior = [v/mass for v in raw_prior]
        check(abs(birth["u"]-u) <= 2e-16 and abs(birth["b"]-b) <= 2e-16
              and abs(birth["z"]-(21*math.exp(-u)-1)) <= 5e-14
              and abs(birth["dt_s"]/(.8/16/1e-16)-1) <= gates["photon_source_relative"]
              and max_abs_diff(mu, expected_mu) <= gates["source_frame_mu_absolute"], prefix+"SOURCE_FRAME")
        check(max_abs_diff(prior, expected_prior) <= gates["native_prior_absolute"], prefix+"PRIOR_JACOBIAN")
        check(all(abs(v) <= 1 for v in mu) and all(a < b for a, b in zip(mu, mu[1:]))
              and min(prior) > 0 and min(alpha) > 0 and min(ea) > 0 and min(na) > 0, prefix+"POSITIVE_DOMAIN")
        check(max_abs_diff(mu, [-v for v in mu[::-1]]) <= gates["reflection_absolute"]
              and max_abs_diff(alpha, alpha[::-1]) <= gates["reflection_absolute"], prefix+"REFLECTION")
        norm, m2, m4 = exact_moments(mu, alpha)
        check(abs(norm-1) <= gate, prefix+"EXACT_NORMALIZATION", str(norm-1))
        check(abs(m2) <= gate and abs(m4) <= gate, prefix+"EXACT_P2_P4", [str(m2), str(m4)])
        certificates.append({"birth": j, "projector": dispatch, "sum_alpha_exact": str(norm),
                             "P2_exact": str(m2), "P4_exact": str(m4),
                             "photon_moments_diagnostic": [float(v) for v in exact_moments(mu, na)[1:]],
                             "energy_moments_diagnostic": [float(v) for v in exact_moments(mu, ea)[1:]]})
        if j == 11:
            check(max_abs_diff(mu, original_failure["support_mu"]) <= gates["source_frame_mu_absolute"], prefix+"ORIGINAL_FAILURE_SUPPORT")
        amount = source_rate(u)*.8/16/1e-16
        check(birth["n_birth"] > 0 and birth["u_birth"] > 0
              and abs(birth["source_amount"]/amount-1) <= gates["photon_source_relative"]
              and abs(birth["n_birth"]/amount-1) <= gates["photon_source_relative"], prefix+"OWNER_PHOTON_SOURCE")
        pairs = [kernel(.2*(1-u), v) for v in mu]
        amp = birth["u_birth"]*math.exp(u-1)
        pn.append(birth["n_birth"])
        pu.append(amp*math.fsum(a*r for a, (r, _) in zip(ea, pairs)))
        pp.append(amp*math.fsum(a*d for a, (_, d) in zip(ea, pairs)))
        qu.append(amp*math.fsum(a*r for a, (r, _) in zip(alpha, pairs)))
        qp.append(amp*math.fsum(a*d for a, (_, d) in zip(alpha, pairs)))
        for order in continuum:
            cmu, cw = isotropic_gl(order)
            cp = [kernel(.2*(1-u), v) for v in cmu]
            continuum[order][0].append(amp*math.fsum(w*r for w, (r, _) in zip(cw, cp)))
            continuum[order][1].append(amp*math.fsum(w*d for w, (_, d) in zip(cw, cp)))
        birth_digests.append(hashlib.sha256(b"".join(struct.pack("<d", v) for array in (mu, alpha) for v in array)).hexdigest())
    ns, us, ps = math.fsum(pn), math.fsum(pu), math.fsum(pp)
    positive(ns, "RECONSTRUCTED_N")
    positive(us, "RECONSTRUCTED_U")
    err = max(abs(row["n_final"]-ns)/ns, abs(row["u_final"]-us)/us, abs(row["stress_final"]-ps)/us,
              abs(row["predicted_u"]-us)/us, abs(row["predicted_stress"]-ps)/us)
    nonnegative_residual(err, "NATIVE_R_D_KERNEL")
    check(err <= gates["native_kernel_relative"], "NATIVE_R_D_KERNEL", err)
    old = inventory(row["old_values"], "OLD_VALUES")
    expected_old = inventory(baseline["selected_fields"]["old_values"], "REUSED_OLD_VALUES")
    old_error = max(abs(a-b)/scale for a, b, scale in zip(old, expected_old, [expected_old[0], expected_old[1], expected_old[1]]))
    nonnegative_residual(old_error, "REUSED_OLD32_OBSERVATION")
    check(old_error <= gates["native_ledger_relative"], "REUSED_OLD32_OBSERVATION", old_error)
    combined = inventory(row["combined_block_values"], "COMBINED")
    new = [row["n_final"], row["u_final"], row["stress_final"]]
    block_error = max(abs(a-b-c)/scale for a, b, c, scale in zip(combined, old, new, [combined[0], combined[1], combined[1]]))
    nonnegative_residual(block_error, "MULTIGRID_BLOCK_SUM")
    check(block_error <= gates["native_ledger_relative"], "MULTIGRID_BLOCK_SUM", block_error)
    ci = inventory(row["same_grid_control_initial"], "CONTROL_INITIAL")
    cf = inventory(row["same_grid_control_final"], "CONTROL_FINAL")
    control_error = max(abs(a-b-c)/scale for a, b, c, scale in zip(cf, ci, new, [cf[0], cf[1], cf[1]]))
    nonnegative_residual(control_error, "SAME_GRID_CONTROL_LEDGER")
    ledger_error = max(row["max_increment_ledger_n_relative"], row["max_increment_ledger_u_relative"],
                       row["max_native_reported_ledger_relative"], control_error)
    nonnegative_residual(ledger_error, "FINITE_BIN_TRANSFER_LEDGER")
    check(ledger_error <= gates["native_ledger_relative"], "FINITE_BIN_TRANSFER_LEDGER", ledger_error)
    check(row["max_cell_add_absolute"] == 0, "SAME_GRID_INCREMENT_PRESERVATION", row["max_cell_add_absolute"])
    cont = vector(row["energy_continuity_relative"], 2, "CONTINUITY")
    check(max(abs(v) for v in cont) <= gates["continuity_relative"], "PER_H_CONTINUITY", cont)
    refs = {n: [math.fsum(x) for x in pair] for n, pair in continuum.items()}
    for order, values in refs.items():
        positive(values[0], "CONTINUUM_REFERENCE_U:"+str(order))
    ref_error = max_abs_diff(refs[128], refs[256])/refs[256][0]
    nonnegative_residual(ref_error, "ANGULAR_REFERENCE_128_256")
    check(ref_error <= gates["continuum_reference_128_256_relative"], "ANGULAR_REFERENCE_128_256", ref_error)
    a_ref = refs[256][1]/refs[256][0]
    a_native = row["stress_final"]/row["u_final"]
    check(abs(row["a_response"]-a_native) <= gates["native_kernel_relative"], "NEW_ONLY_OBSERVABLE")
    angular_error = a_native-a_ref
    integrity = all(item["pass"] for item in checks)
    target = abs(angular_error) <= gates["angular_accuracy_absolute"]
    return {"schema": "BASS_S12_NATIVE_ANALYSIS_V1",
            "status": "PASS_SINGLE_NATIVE_HISTORY" if integrity else "FAILED_NATIVE_INTEGRITY",
            "integrity_gates_pass": integrity, "completed_native_histories": int(integrity),
            "case_id": row["case_id"], "checks": checks, "gate_failures": [x for x in checks if not x["pass"]],
            "exact_certificates": certificates, "birth_mu_alpha_sha256": birth_digests,
            "old_block_sha256": old_sha, "native_kernel_relative": err,
            "native_transfer_ledger_relative": ledger_error, "old32_reuse_relative": old_error,
            "block_sum_relative": block_error, "continuum_reference_relative": ref_error,
            "a_response": a_native, "continuum_a": a_ref, "angular_a_error": angular_error,
            "angular_accuracy_target_met": target, "angular_accuracy_is_separate_diagnostic": True,
            "discrete_alpha_a_error": math.fsum(qp)/math.fsum(qu)-a_ref,
            "native_minus_discrete_alpha_a": a_native-math.fsum(qp)/math.fsum(qu),
            "completed_old_cases_replayed": 0, "full_reactive_spectral_history_claim": False,
            "native_Einstein_shared_Q_claim": False, "finest_n256_admission_reissued": False}
