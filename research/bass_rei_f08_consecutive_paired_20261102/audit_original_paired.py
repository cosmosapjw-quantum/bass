#!/usr/bin/env python3
"""Independent source-parameter physical-support and native interval witness audit.

Original Rust paired_runtime runs the physics. This auditor is standalone stdlib
code and does not claim interval certification of the continuum or 14 ledgers.
"""
import argparse
import copy
import csv
from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path


class AuditError(Exception):
    pass


def require(ok, code):
    if not ok:
        raise AuditError(code)


def finite(row, key):
    try:
        val = float(row[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise AuditError("FIELD_" + key) from exc
    require(math.isfinite(val), "NONFINITE_" + key)
    return val


def verify(rows, evidence_dir):
    require(len(rows) == 320, "ACTUAL_STAGE_COUNT")
    require(set(row["geometry"] for row in rows) == {"S0_BI", "S0_FLRW"}, "GEOMETRY_SET")
    results = {}
    for geom, hmax in (("S0_BI", 1.01e-14), ("S0_FLRW", 1.0e-14)):
        sub = [x for x in rows if x["geometry"] == geom]
        require(len(sub) == 160, "PER_GEOMETRY_STEP_COUNT")
        local = []
        widths = []
        ledgers = []
        nr = []
        er = []
        for expected, row in enumerate(sub, 1):
            require(int(row["step"]) == expected, "STEP_ORDER")
            require(row["status"] == "PASS" and row["error"] == "NONE", "NATIVE_STAGE_NOT_PASS")
            time_s = finite(row, "t_s")
            require(time_s == 625000000.0 * expected, "CLOCK_MISMATCH")
            l = finite(row, "local_bound")
            w = finite(row, "public_width")
            ledger = finite(row, "max_ledger")
            require(0.0 <= l < 2e-4, "ORIGINAL_LOCAL_GATE")
            require(0.0 <= w < 2e-3, "ORIGINAL_WIDTH_GATE")
            require(0.0 <= ledger <= 1e-12, "ORIGINAL_POINT_LEDGER_GATE")
            local.append(l)
            widths.append(w)
            ledgers.append(ledger)
            count = finite(row, "photon_n")
            lo = finite(row, "photon_box_lo")
            hi = finite(row, "photon_box_hi")
            require(0.0 < count and 0.0 <= lo <= count <= hi, "PHOTON_INTERVAL_CONTAINMENT")
            bad = finite(row, "spurious_support_n")
            bad_lo = finite(row, "spurious_support_box_lo")
            bad_frac = finite(row, "spurious_support_frac")
            require(0 <= bad_lo <= bad <= count, "PHYSICAL_SUPPORT_INTERVAL_COUNT")
            require(abs(bad_frac - bad / count) <= 1e-14, "SUPPORT_FRACTION_RECOMPUTE")
            # Independent decimal reference, using exact binary64 inputs from Rust.
            with localcontext() as ctx:
                ctx.prec = 70
                true_lower = Decimal.from_float(13.7) * (
                    -(Decimal.from_float(hmax) * Decimal.from_float(time_s))
                ).exp()
                reported_lower = Decimal.from_float(finite(row, "physical_energy_lower_ev"))
                require(reported_lower <= true_lower, "NONCONSERVATIVE_PHYSICAL_BOUND")
                require((true_lower - reported_lower) < Decimal("0.000000000001"), "PHYSICAL_BOUND_TOO_LOOSE")
            xhii = finite(row, "gas_xhii")
            heii = finite(row, "gas_xheii")
            heiii = finite(row, "gas_xheiii")
            require(0 <= xhii <= 1 and 0 <= heii <= 1 and 0 <= heiii <= 1 and heii + heiii <= 1, "GAS_SPECIES_DOMAIN")
            temp = finite(row, "gas_t_kelvin")
            require(35000 <= temp <= 60000, "TEMPERATURE_DOMAIN")
            require(finite(row, "gas_width_max") >= 0, "GAS_NEGATIVE_WIDTH")
            for fld in ["source_n", "absorbed_n", "redshift_work_ev", "thermal_work_ev"]:
                require(finite(row, fld) >= 0, "LEDGER_NONPOSITIVE_" + fld)
            nres = abs(finite(row, "photon_global_number_residual"))
            eres = abs(finite(row, "photon_global_energy_residual"))
            require(nres < 1e-12 and eres < 1e-12, "CUMULATIVE_POINT_LEDGER_FAIL")
            nr.append(nres)
            er.append(eres)
        end = sub[-1]
        # The scientific result is a FAIL in physical source support, not
        # something that should be swallowed by passing numerical gates.
        require(finite(end, "spurious_support_box_lo") > 0.0, "MISSING_CERTIFIED_SUPPORT_COUNTEREXAMPLE")
        results[geom] = {
            "actual_native_consecutive_stages": len(sub),
            "step160_support_fraction": finite(end, "spurious_support_frac"),
            "step160_spurious_photon_n_per_h": finite(end, "spurious_support_n"),
            "step160_forbidden_photon_interval_lower_per_h": finite(end, "spurious_support_box_lo"),
            "step160_physical_energy_lower_ev": finite(end, "physical_energy_lower_ev"),
            "step160_photon_number_per_h": finite(end, "photon_n"),
            "step160_gas_temperature_K": finite(end, "gas_t_kelvin"),
            "max_original_local_bound": max(local),
            "max_original_public_width": max(widths),
            "max_original_point_stage_ledger": max(ledgers),
            "max_cumulative_point_number_residual": max(nr),
            "max_cumulative_point_energy_residual": max(er),
            "numerical_stage_gates": "PASS",
            "physical_birth_support": "FAIL"
        }

    nfiles = 0
    root_maxq = 0.0
    for geom in ("S0_BI", "S0_FLRW"):
        for step in (1, 160):
            for endpoint in (0, 1, 2):
                p = evidence_dir / (f"{geom}_step{step:03}_native_endpoint{endpoint}.json")
                require(p.is_file(), "MISSING_NATIVE_WITNESS")
                data = json.loads(p.read_text())
                root_maxq = max(root_maxq, float(data["q"]))
                require(0 <= float(data["q"]) < 1, "KRAWCZYK_Q_GATE")
                require(len(data["old_gas"]) == len(data["parent_gas"]) == len(data["out_gas"]) == len(data["point_gas"]) == 4, "GAS_WITNESS_SHAPE")
                for old, parent, out, point in zip(data["old_gas"], data["parent_gas"], data["out_gas"], data["point_gas"]):
                    require(parent[0] <= old <= parent[1], "PARENT_GAS_NOT_CONTAINED")
                    require(out[0] <= point <= out[1], "ROOT_GAS_NOT_CONTAINED")
                require(len(data["point_photons"]) == len(data["out_photons"]) == len(data["parent_photons"]), "PHOTON_WITNESS_LENGTH")
                for point, interval in zip(data["point_photons"], data["out_photons"]):
                    require(interval[0] <= point <= interval[1], "ROOT_PHOTON_NOT_CONTAINED")
                nfiles += 1

    return {
        "science_unit": "BASS_F08_ORIGINAL_PAIRED_CONSECUTIVE_SUPPORT_20261102",
        "original_model": "S0_17_ENERGY_NODES_8x16_DIRECTIONS",
        "source_birth_energy_ev": 13.7,
        "source_dt_s": 625000000,
        "stage_count": 320,
        "native_endpoint_witness_files": nfiles,
        "maximum_original_native_root_witness_q": root_maxq,
        "source_pair_sha256": "0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8",
        "original_paired_runtime_sha256": "b6c1d2a07ab51ff02318139ae18387b77f61859c08037347f788524df770ebe7",
        "original_coupled_primary_sha256": "915d0a898100a54d04a525227e7fbeb870e321fcc14aaa91afd61352b6d4cf4b",
        "original_source_mutation": False,
        "per_geometry": results,
        "owner_original_F08_14_ledger": "NOT_RUN",
        "global_birth_q_energy_interval": "NOT_RUN",
        "source_physical_support": "FAIL",
        "original_F08_owner_admission": "HOLD",
        "central_REI_DAG": "28/88_REPORTED_UNCHANGED",
        "BASS_upper": "9/15_SCOPED_UNCHANGED",
        "native_subagents": "NOT_RUN",
        "distinct_author_blind_referee": "NOT_RUN"
    }


def hostile_tests(rows, evidence_dir):
    baseline = verify(rows, evidence_dir)
    require(baseline["stage_count"] == 320, "BASELINE_NOT_RECORDED")
    probes = [
        ("FORGED_GATE_PASS", "local_bound", "0.0003", 0),
        ("FORGED_SUPPORT_FRAC", "spurious_support_frac", "0.0", 159),
        ("FORGED_ZERO_PHOTON", "photon_n", "-1.0", 0),
        ("FORGED_BOX", "photon_box_lo", "0.5", 0),
        ("FORGED_ENERGY_BOUND", "physical_energy_lower_ev", "13.7", 159),
        ("FORGED_SUPPORT_INTERVAL", "spurious_support_box_lo", "0.0", 159)
    ]
    caught = []
    for name, field, value, i in probes:
        tampered = copy.deepcopy(rows)
        tampered[i][field] = value
        try:
            verify(tampered, evidence_dir)
        except AuditError as exc:
            caught.append({"case": name, "status": "REJECTED", "error_code": str(exc)})
        else:
            raise AuditError("FORGED_CASE_ACCEPTED_" + name)
    return caught


def main():
    pa = argparse.ArgumentParser()
    pa.add_argument("--csv", type=Path, required=True)
    pa.add_argument("--native-endpoints", type=Path)
    pa.add_argument("--output", type=Path)
    pa.add_argument("--negative-tests", action="store_true")
    args = pa.parse_args()
    path = args.csv
    witness = args.native_endpoints or path.parent / "native_endpoints"
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    summary = verify(rows, witness)
    summary["trajectory_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    summary["hostile_negative_tests"] = hostile_tests(rows, witness) if args.negative_tests else []
    output = json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output)
    print(output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, KeyError, json.JSONDecodeError, OSError) as exc:
        print("AUDIT_FAILED: " + str(exc), flush=True)
        raise SystemExit(1)
