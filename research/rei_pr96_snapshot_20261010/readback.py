"""Export pinned PR96 scalar snapshots and execute the actual BASS receiver."""
from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_hash(path, expected):
    actual = digest(path)
    if actual != expected:
        raise ValueError(f"IMMUTABLE_SOURCE_MISMATCH:{path}:{actual}")


def extract(source, contract):
    for name, expected in contract["source_files"].items():
        check_hash(source / name, expected)
    with np.load(source / "evidence/extended_dataset.npz", allow_pickle=False) as data:
        states, times = data["states"], data["times_s"]
    history = json.loads((source / "evidence/extended.json").read_text())["history"]
    if states.shape != (2913, 17) or times.shape != (17,) or len(history) != 17:
        raise ValueError("FROZEN_GRID_SHAPE")
    if not np.array_equal(times, np.linspace(0., 1e11, 17)):
        raise ValueError("FROZEN_EPOCH_GRID")
    rows, references = [], []
    for i, record in enumerate(history):
        x = states[:3, i]
        if record["time_s"] != times[i] or not np.array_equal(
            x, [record["xHII"], record["xHeII"], record["xHeIII"]]
        ):
            raise ValueError(f"DATASET_JSON_STATE_MISMATCH:{i}")
        nh = record["nH_cm3"]
        nhe = nh * .24 / (4. * .76)
        row = [float(times[i]), nh, nhe, *map(float, x)]
        if (not all(np.isfinite(row)) or nh < 0. or nhe < 0.
                or not 0. <= x[0] <= 1. or min(x[1:]) < 0. or sum(x[1:]) > 1.):
            raise ValueError(f"INVALID_SOURCE_SNAPSHOT:{i}")
        rows.append(row)
        # Independent arithmetic on the actual transmitted binary64 inputs.
        with localcontext() as ctx:
            ctx.prec = 60
            d = [Decimal.from_float(float(v)) for v in row]
            ne = Decimal(1000000) * (d[1]*d[3] + d[2]*(d[4]+2*d[5]))
            q = ne * Decimal("299792458") * Decimal("6.6524587e-29")
        references.append({"ne_m3_decimal": str(ne), "rate_s_inverse_decimal": str(q),
                           "archived_ne_m3": record["ne_cm3"] * 1e6})
    return rows, references


def compare(output, rows, refs, tolerance):
    values = np.asarray([[float(x) for x in line.split()] for line in output.splitlines()])
    if values.shape != (17, 5) or not np.isfinite(values).all():
        raise ValueError("RECEIVER_OUTPUT_SHAPE_OR_FINITE")
    if not np.array_equal(values[:, 0], np.asarray(rows)[:, 0]):
        raise ValueError("RECEIVER_TIME_READBACK")
    errors = {k: 0. for k in ("direct_ne", "legacy_ne", "archive_ne", "rate", "axis_rate")}
    result = []
    for v, ref in zip(values, refs):
        ne, rate = float(ref["ne_m3_decimal"]), float(ref["rate_s_inverse_decimal"])
        checks = {"direct_ne": abs(v[1]/ne-1), "legacy_ne": abs(v[2]/ne-1),
                  "archive_ne": abs(v[2]/ref["archived_ne_m3"]-1),
                  "rate": abs(v[3]/rate-1), "axis_rate": abs(v[4]/rate-1)}
        for key, error in checks.items():
            errors[key] = max(errors[key], float(error))
        result.append(dict(time_s=float(v[0]), direct_ne_m3=float(v[1]),
                           legacy_ne_m3=float(v[2]), transverse_rate_s_inverse=float(v[3]),
                           axial_rate_s_inverse=float(v[4]), **ref))
    if max(errors.values()) > tolerance or np.any(values[:, 1:] < 0.):
        raise ValueError(f"RECEIVER_PARITY:{errors}")
    return errors, result


def run(args):
    contract = json.loads((HERE / "CONTRACT.json").read_text())
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    execution = {"status": "STARTED", "commands": [], "python": sys.version,
                 "numpy": np.__version__, "platform": platform.platform(), "solver_calls": 0}

    def command(argv, name, stdin=None):
        start = time.monotonic()
        proc = subprocess.run(argv, input=stdin, text=True, capture_output=True,
                              cwd=REPO, timeout=contract["limits"]["command_wall_s"])
        (out / (name + ".stdout.log")).write_text(proc.stdout)
        (out / (name + ".stderr.log")).write_text(proc.stderr)
        execution["commands"].append({"argv": argv, "exit_code": proc.returncode,
                                      "wall_s": time.monotonic()-start})
        if proc.returncode:
            raise RuntimeError(f"COMMAND_FAILED:{name}:{proc.returncode}")
        return proc.stdout

    try:
        for name, expected in contract["bass_files"].items():
            check_hash(REPO / name, expected)
        rows, refs = extract(args.rei_source.resolve(), contract)
        payload = "".join("\t".join(format(v, ".17e") for v in row)+"\n" for row in rows)
        (out / "snapshots.tsv").write_text(payload)
        (out / "references.json").write_text(json.dumps(refs, indent=2)+"\n")
        manifest = str(REPO / "_rustcore/Cargo.toml")
        command(["rustc", "--version"], "rustc")
        command(["cargo", "--version"], "cargo")
        command(["cargo", "build", "--offline", "--locked", "--manifest-path", manifest,
                 "--example", "rei_pr96_snapshot_readback", "--target-dir", str(args.target_dir)], "build")
        binary = args.target_dir / "debug/examples/rei_pr96_snapshot_readback"
        output = command([str(binary)], "receiver", payload)
        errors, epochs = compare(output, rows, refs, contract["relative_tolerance"])
        execution["status"] = "PASS_SCOPED"
        execution["binary_sha256"] = digest(binary)
        validation = {"status": "PASS_SCOPED", "epoch_count": len(epochs),
                      "maximum_relative_errors": errors, "relative_tolerance": contract["relative_tolerance"],
                      "epochs": epochs, "claim_ceiling": contract["claim_ceiling"],
                      "independent_review": "PENDING", "global_physical_admission": "HOLD",
                      "source_hashes": contract["source_files"], "bass_hashes": contract["bass_files"],
                      "driver_sha256": digest(__file__), "contract_sha256": digest(HERE / "CONTRACT.json"),
                      "example_sha256": digest(REPO / "_rustcore/examples/rei_pr96_snapshot_readback.rs")}
        (out / "VALIDATION.json").write_text(json.dumps(validation, indent=2)+"\n")
        print(json.dumps({"status": execution["status"], "epoch_count": 17, "errors": errors}))
    except Exception as exc:
        execution["status"] = "FAIL"
        execution["failure"] = repr(exc)
        raise
    finally:
        (out / "EXECUTION.json").write_text(json.dumps(execution, indent=2)+"\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rei-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--target-dir", type=Path, required=True)
    run(parser.parse_args())
