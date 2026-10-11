#!/usr/bin/env python3
"""Frozen warm P01 finite-history receiver validation; no REI solver calls."""
import argparse
import base64
from datetime import datetime, timezone
from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess
import sys
import time

import numpy as np

INTERVAL_REL = "research/p01_certified_warm_exec01_20261010/output/production_interval.json"
DATASET_REL = "research/p01_certified_warm_exec01_20261010/output/production_dataset.npz"
PROVIDER_REL = "research/physical_provider_20261010/CONTRACT.json"
BACKGROUND_REL = "research/physical_provider_20261010/background.py"
HASHES = {
    INTERVAL_REL: "d0745653fa463b05a47f352063e57661d97385561174c749424a7ec1907c1520",
    DATASET_REL: "77a144347d8f85c91320c7acc694e770544ff61f79bc418cebe3f8f13403483a",
    PROVIDER_REL: "2f5f118b856a47fa339a510a58e7221e7d7ab3ea3a38625d2c61e9b93380ed6d",
    BACKGROUND_REL: "b80f1d2ca8b4ab251d93447ff746428e6230130bee9b87500b7960bbc3a0076d",
}
RATE_REL = Decimal.from_float(1.4210854715202004e-14)
DEPTH_REL = Decimal.from_float(5.684341886080802e-14)
ABS = Decimal.from_float(1.4210854715202004e-14)
D = Decimal.from_float


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fail(message, out, details=None):
    payload = {"status": "FAIL_FIRST", "first_failure": message, "details": details}
    (out / "FIRST_FAILURE.json").write_text(json.dumps(payload, indent=2) + "\n")
    raise RuntimeError(message)


def near(name, actual, expected, relative, absolute=Decimal(0)):
    a, e = D(actual), expected
    difference = abs(a - e)
    bound = absolute + relative * abs(e)
    if difference > bound:
        raise ValueError(f"{name}: observed {a} expected {e}, difference {difference} > {bound}")
    return float(difference / (abs(e) if e != 0 else Decimal(1)))


def fmt(x):
    return format(float(x), ".17g")


def native_input(rows, tail):
    lines = ["TAIL\t" + fmt(tail), "N\t" + str(len(rows))]
    lines += ["\t".join(fmt(v) for v in row) for row in rows]
    return ("\n".join(lines) + "\n").encode()


def launch(binary, out, name, payload):
    input_file = out / f"INPUT_{name}.tsv"
    input_file.write_bytes(payload)
    command = ["timeout", "--signal=TERM", "--kill-after=5s", "10s", str(binary)]
    start = datetime.now(timezone.utc).isoformat()
    clock = time.monotonic()
    proc = subprocess.run(command, input=payload, capture_output=True)
    record = {
        "command": command, "start_utc": start, "wall_s": time.monotonic() - clock,
        "stdin_path": str(input_file), "stdin_sha256": sha(payload),
        "exit_code": proc.returncode,
        "stdout_b64": base64.b64encode(proc.stdout).decode(),
        "stderr_b64": base64.b64encode(proc.stderr).decode(),
        "stdout_utf8": proc.stdout.decode("utf-8", "replace"),
        "stderr_utf8": proc.stderr.decode("utf-8", "replace"),
    }
    (out / f"RAW_{name}.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


def parse_native(stdout, rows):
    edge, cell = {}, {}
    for line in stdout.splitlines():
        fields = line.split("\t")
        if len(fields) == 12 and fields[0] == "E":
            i = int(fields[1])
            if i in edge:
                raise ValueError(f"duplicate edge {i}")
            edge[i] = [float(s) for s in fields[2:]]
        elif len(fields) == 4 and fields[0] == "C":
            i = int(fields[1])
            if i in cell:
                raise ValueError(f"duplicate cell {i}")
            cell[i] = [float(s) for s in fields[2:]]
        else:
            raise ValueError(f"invalid output line: {line[:100]}")
    if sorted(edge) != list(range(17)) or sorted(cell) != list(range(16)):
        raise ValueError(f"incomplete output: {len(edge)} edges, {len(cell)} cells")
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            if edge[i][j] != val or struct.pack(">d", edge[i][j]) != struct.pack(">d", val):
                raise ValueError(f"input echo changed at epoch {i} field {j}")
    return edge, cell


def reference(rows, tail):
    with localcontext() as ctx:
        ctx.prec = 80
        constant = D(299792458.0) * D(6.6524587e-29)
        ne = [D(r[1])*D(r[3]) + D(r[2])*(D(r[4])+D(2)*D(r[5])) for r in rows]
        rate = [n*constant for n in ne]
        avg = [(rate[i]+rate[i+1])/D(2) for i in range(16)]
        depth = [avg[i]*D(rows[i+1][0]-rows[i][0]) for i in range(16)]
        tau = [Decimal(0)]*17
        tau[-1] = D(tail)
        for i in range(15,-1,-1):
            tau[i] = tau[i+1]+depth[i]
        survival = [(-t).exp() for t in tau]
        mass = [survival[i+1]*(D(1)-(-depth[i]).exp()) for i in range(16)]
        return ne, rate, avg, tau, survival, mass


def validate(edge, cell, rows, tail, archived_ne):
    ne, rate, avg, tau, survival, mass = reference(rows, tail)
    max_rate_rel = Decimal(0)
    max_depth_rel = Decimal(0)
    max_survival_abs = Decimal(0)
    for i in range(17):
        e = edge[i]
        for name, observed, expected in [
            ("ne", e[6], ne[i]), ("q", e[7], rate[i])
        ]:
            delta = near(f"{name}[{i}]", observed, expected, RATE_REL)
            max_rate_rel = max(max_rate_rel, D(delta))
        near(f"archived_ne[{i}]", e[6], D(archived_ne[i]), RATE_REL)
        delta = near(f"tau[{i}]", e[8], tau[i], DEPTH_REL)
        max_depth_rel = max(max_depth_rel, D(delta))
        diff = abs(D(e[9])-survival[i])
        if diff > ABS:
            raise ValueError(f"survival[{i}] difference {diff} > {ABS}")
        max_survival_abs = max(max_survival_abs, diff)
        if not all(math.isfinite(v) for v in e) or e[8] < 0 or e[9] < 0:
            raise ValueError(f"nonphysical edge {i}")
    for i in range(16):
        delta = near(f"average_rate[{i}]", cell[i][0], avg[i], RATE_REL)
        max_rate_rel = max(max_rate_rel, D(delta))
        delta = near(f"cell_mass[{i}]", cell[i][1], mass[i], DEPTH_REL)
        max_depth_rel = max(max_depth_rel, D(delta))
        if cell[i][1] < 0 or edge[i][8] < edge[i+1][8]:
            raise ValueError(f"nonmonotone/negative cell {i}")
    if struct.pack(">d", edge[16][8]) != struct.pack(">d", tail):
        raise ValueError("right edge tau differs from supplied tail")
    balance = abs(D(edge[0][9]) + sum(D(cell[i][1]) for i in range(16)) - (-D(tail)).exp())
    if balance > ABS:
        raise ValueError(f"mass balance difference {balance} > {ABS}")
    return {
        "max_ne_q_avg_relative_error": str(max_rate_rel),
        "max_tau_and_mass_relative_error": str(max_depth_rel),
        "max_survival_absolute_error": str(max_survival_abs),
        "mass_balance_absolute_error": str(balance),
        "tau_start": edge[0][8], "tau_end": edge[16][8],
        "survival_start": edge[0][9], "mass_sum": sum(cell[i][1] for i in range(16)),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source-root", required=True, type=Path)
    p.add_argument("--binary", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    start = datetime.now(timezone.utc).isoformat()
    try:
        for rel, expected in HASHES.items():
            actual = sha((args.source_root / rel).read_bytes())
            if actual != expected:
                fail("IMMUTABLE_INPUT_SHA_MISMATCH:" + rel, out, {"expected": expected, "actual": actual})
        history = json.loads((args.source_root / INTERVAL_REL).read_text())["history"]
        with np.load(args.source_root / DATASET_REL, allow_pickle=False) as npz:
            times = np.array(npz["times_s"], copy=True)
            states = np.array(npz["states"][:3], copy=True)
        if len(history) != 17 or times.shape != (17,) or states.shape != (3,17):
            fail("HISTORY_SHAPE", out)
        rows, archived_ne = [], []
        fields = ["xHII", "xHeII", "xHeIII"]
        parity = {"times": 0, "ionic": 0}
        for i, h in enumerate(history):
            t = float(h["time_s"])
            if struct.pack(">d", t) != struct.pack(">d", float(times[i])):
                fail(f"TIME_PARITY_EPOCH_{i}", out)
            parity["times"] += 1
            ion = [float(h[k]) for k in fields]
            for j, x in enumerate(ion):
                if struct.pack(">d", x) != struct.pack(">d", float(states[j,i])):
                    fail(f"STATE_PARITY_EPOCH_{i}_ROW_{j}", out)
                parity["ionic"] += 1
            if not (math.isfinite(t) and 0 <= t <= 1e11 and (i == 0 or t > rows[-1][0])
                    and math.isfinite(h["T_K"]) and 30000 <= h["T_K"] <= 110000
                    and math.isfinite(h["z"]) and 1+h["z"] > 0
                    and math.isfinite(h["nH_cm3"]) and h["nH_cm3"] > 0
                    and math.isfinite(h["ne_cm3"]) and h["ne_cm3"] > 0
                    and all(math.isfinite(x) and x >= 0 for x in ion)
                    and ion[0] <= 1 and ion[1]+ion[2] <= 1):
                fail(f"INPUT_DOMAIN_EPOCH_{i}", out)
            nhcm = float(h["nH_cm3"])
            nhecm = nhcm * 0.24/(4.0*0.76)
            rows.append([t, nhcm*1e6, nhecm*1e6, *ion])
            archived_ne.append(float(h["ne_cm3"])*1e6)
        if rows[0][0] != 0.0 or rows[-1][0] != 1e11:
            fail("FROZEN_TIME_ENDPOINTS", out)
        if any(rows[i+1][0]-rows[i][0] != 6.25e9 for i in range(16)):
            fail("FROZEN_TIME_SPACING", out)
        volume = [h["nH_cm3"]/(1.0+h["z"])**3 for h in history]
        geometry_relative = max(abs(v/volume[0]-1.0) for v in volume)
        if geometry_relative > 1e-11:
            fail("GEOMETRY_NORMALIZATION", out, geometry_relative)
        (out/"INPUT_IDENTITY.json").write_text(json.dumps({
            "hashes_verified": HASHES, "npz_json_bit_parity": parity,
            "nH_volume_label_relative_max": geometry_relative,
            "row_count": len(rows), "first_time_s": rows[0][0], "last_time_s": rows[-1][0]
        }, indent=2) + "\n")
        baseline = launch(args.binary, out, "baseline", native_input(rows, 0.0))
        if baseline["exit_code"] != 0:
            fail("BASELINE_RECEIVER_EXIT", out, baseline)
        edge0, cell0 = parse_native(baseline["stdout_utf8"], rows)
        check0 = validate(edge0, cell0, rows, 0.0, archived_ne)
        tail = launch(args.binary, out, "tail025", native_input(rows, 0.25))
        if tail["exit_code"] != 0:
            fail("TAIL025_RECEIVER_EXIT", out, tail)
        edge1, cell1 = parse_native(tail["stdout_utf8"], rows)
        check1 = validate(edge1, cell1, rows, 0.25, archived_ne)
        factor = math.exp(-0.25)
        for i in range(17):
            near(f"tail_shift[{i}]", edge1[i][8]-edge0[i][8], D(0.25), DEPTH_REL)
            if abs(edge1[i][9]-edge0[i][9]*factor) > float(ABS):
                fail(f"TAIL_SURVIVAL_SCALE_{i}", out)
        for i in range(16):
            near(f"tail_mass_scale[{i}]", cell1[i][1], D(cell0[i][1])*D(factor), DEPTH_REL)
        negatives = {}
        cases = {
            "missing_epoch": native_input(rows[:-1], 0.0),
            "invalid_fraction": native_input([[*r] if i else [r[0],r[1],r[2],1.1,r[4],r[5]] for i,r in enumerate(rows)],0.0),
            "negative_tail": native_input(rows,-0.1),
        }
        for name, payload in cases.items():
            result = launch(args.binary, out, name, payload)
            negatives[name] = {"exit_code": result["exit_code"], "stderr_utf8": result["stderr_utf8"]}
            if result["exit_code"] == 0:
                fail(f"NEGATIVE_NOT_REJECTED_{name}", out, result)
        validation = {
            "schema": "warm.p01.bass.history.exec28.validation.v1",
            "status": "FACTUAL_TARGETED_PASS_PENDING_INDEPENDENT_ASTRA",
            "start_utc": start, "completion_utc": datetime.now(timezone.utc).isoformat(),
            "input_identity": str(out/"INPUT_IDENTITY.json"),
            "baseline": check0, "tail025": check1,
            "positive_substantive_runs": 2, "negative_receiver_runs": 3,
            "negative_cases": negatives,
            "chemistry_solver_runs": 0, "REI_native_launches": 0, "network_calls": 0,
            "claim_ceiling": "Finite sampled warm P01 BASS production visibility component only; no full BASS crate, PR135 legacy adapter, full observer tail, chemistry convergence or global scientific admission."
        }
        (out/"VALIDATION.json").write_text(json.dumps(validation, indent=2) + "\n")
        print(json.dumps({"status": validation["status"], "validation": str(out/"VALIDATION.json"),
                          "parity": parity, "baseline_tau": check0["tau_start"],
                          "tail025_tau": check1["tau_start"]}, sort_keys=True))
    except Exception as e:
        if not (out/"FIRST_FAILURE.json").exists():
            (out/"FIRST_FAILURE.json").write_text(json.dumps({
                "status": "FAIL_FIRST", "first_failure": type(e).__name__ + ": " + str(e)
            }, indent=2) + "\n")
        print(str(e), file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
