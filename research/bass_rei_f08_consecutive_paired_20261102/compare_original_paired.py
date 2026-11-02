#!/usr/bin/env python3
"""Cross-host semantic native paired-runtime parity, NEVER an original gate change.

Proves both trajectories individually satisfy source and native interval gate
audits, then compares scientifically meaningful physical observables. Ignore
byte-only changes and low-level floating-point diagnostic residual identity.
"""
import argparse
import csv
from pathlib import Path
import math
import sys
from audit_original_paired import AuditError, require, verify


SCIENTIFIC_FIELDS = (
    "photon_n", "photon_box_lo", "photon_box_hi", "spurious_support_n",
    "spurious_support_frac", "spurious_support_box_lo", "physical_energy_lower_ev",
    "gas_xhii", "gas_xheii", "gas_xheiii", "gas_w_ev_h", "gas_t_kelvin",
    "source_n", "absorbed_n", "redshift_work_ev", "thermal_work_ev",
)


def read(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def compare(ref, cold, refw, coldw):
    evidence_ref = verify(ref, refw)
    evidence_cold = verify(cold, coldw)
    require(evidence_ref["stage_count"] == evidence_cold["stage_count"] == 320, "REFERENCE_STAGE_COUNT")
    maxima = {name: 0.0 for name in SCIENTIFIC_FIELDS}
    for i, (a, b) in enumerate(zip(ref, cold)):
        for field in ("geometry", "step", "status", "error"):
            require(a[field] == b[field], "CROSS_HOST_DISCRETE_IDENTITY_" + field)
        for field in SCIENTIFIC_FIELDS:
            x = float(a[field])
            y = float(b[field])
            delta = abs(x-y)
            maxima[field] = max(maxima[field], delta)
            # This measures cross-host semantic parity ONLY; original native
            # gates and physical-support FAIL are enforced separately by verify.
            # Bound is orders smaller than forbidden 0.0177/H mass; not a
            # replacement of original 2e-4/2e-3/1e-12 source gates.
            require(math.isclose(x, y, rel_tol=2e-9, abs_tol=1e-12),
                    f"CROSS_HOST_PHYSICAL_PARITY_{field}_row{i+1}")
    for geom in ("S0_BI", "S0_FLRW"):
        a = evidence_ref["per_geometry"][geom]
        b = evidence_cold["per_geometry"][geom]
        require(a["physical_birth_support"] == b["physical_birth_support"] == "FAIL", "NEGATIVE_PHYSICS_NOT_REPRODUCED")
        require(a["numerical_stage_gates"] == b["numerical_stage_gates"] == "PASS", "ORIGINAL_NUMERIC_GATE_NOT_REPRODUCED")
        require(a["step160_forbidden_photon_interval_lower_per_h"] > 0
                and b["step160_forbidden_photon_interval_lower_per_h"] > 0,
                "POSITIVE_FORBIDDEN_MASS_NOT_REPRODUCED")
    return maxima


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reference", type=Path, required=True)
    ap.add_argument("--replay", type=Path, required=True)
    ap.add_argument("--reference-native", type=Path)
    ap.add_argument("--replay-native", type=Path)
    ap.add_argument("--negative-test", action="store_true")
    a = ap.parse_args()
    ref = read(a.reference)
    cold = read(a.replay)
    refw = a.reference_native or a.reference.parent / "native_endpoints"
    coldw = a.replay_native or a.replay.parent
    results = compare(ref, cold, refw, coldw)
    if a.negative_test:
        import copy
        tampered = copy.deepcopy(cold)
        tampered[0]["gas_t_kelvin"] = str(float(tampered[0]["gas_t_kelvin"]) + 100.0)
        try:
            compare(ref, tampered, refw, coldw)
        except AuditError:
            print("NEGATIVE_CROSS_HOST_PHYSICAL_TAMPER_REJECTED")
        else:
            raise AuditError("FORGED_CROSS_HOST_TEMPERATURE_ACCEPTED")
    print("CROSS_HOST_SEMANTIC_NATIVE_PASS_SOURCE_SUPPORT_FAIL_STILL_REPRODUCED")
    print("MAX_ABSOLUTE_CROSS_HOST_DISCREPANCIES", sorted(results.items()))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (AuditError, OSError, KeyError, ValueError) as exc:
        print("CROSS_HOST_AUDIT_FAIL " + str(exc))
        sys.exit(1)
