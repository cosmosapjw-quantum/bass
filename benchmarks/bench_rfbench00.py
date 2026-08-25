#!/usr/bin/env python3
"""Non-default RF-BENCH-00 capability and controlled-paired runner.

Probe and corpus-description modes are read-only.  Paired execution requires an
explicit ``--run`` and fails before candidate source resolution unless the
current host proves CONTROLLED_SHARED_PAIRED or stronger.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from benchmarks.rfbench.collector import CommandCollector
from benchmarks.rfbench.corpus import CORPUS_PATH, describe, load_registry, sha256_file
from benchmarks.rfbench.host import probe_host
from benchmarks.rfbench.runner import run_protocol, validate_host_probe, validate_run_config


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _emit(payload: dict[str, Any], output: Path | None) -> None:
    encoded = json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if output is None:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False))
        return
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.tmp-{os.getpid()}")
    temporary.write_text(encoded, encoding="utf-8")
    os.replace(temporary, output)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--probe", action="store_true", help="emit a read-only host receipt")
    mode.add_argument("--describe-corpus", action="store_true")
    mode.add_argument("--validate-config", type=Path)
    mode.add_argument("--run-paired", type=Path, metavar="CONFIG_JSON")
    parser.add_argument("--host-receipt", type=Path,
                        help="exact probe JSON required by --run-paired")
    parser.add_argument("--corpus", type=Path, default=CORPUS_PATH)
    parser.add_argument("--dedicated-attestation", type=Path,
                        help="structured operator facts; never bypasses observed blockers")
    parser.add_argument("--run", action="store_true",
                        help="required explicit opt-in for paired workload execution")
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    dedicated_attestation = (
        None if args.dedicated_attestation is None
        else _load_json(args.dedicated_attestation)
    )
    if args.probe:
        if args.run or args.host_receipt is not None:
            raise SystemExit("--probe does not accept --run or --host-receipt")
        payload = probe_host(dedicated_host_attestation=dedicated_attestation)
    elif args.describe_corpus:
        if args.run or args.host_receipt is not None or dedicated_attestation is not None:
            raise SystemExit("--describe-corpus accepts only --corpus and --output")
        payload = describe(args.corpus)
    elif args.validate_config is not None:
        if args.run or args.host_receipt is not None or dedicated_attestation is not None:
            raise SystemExit("--validate-config does not execute or accept host options")
        config = _load_json(args.validate_config)
        validate_run_config(config)
        registry = load_registry(args.corpus)
        if config["corpus_sha256"] != sha256_file(args.corpus):
            raise SystemExit("run config corpus_sha256 does not match --corpus")
        workload_ids = {item["id"] for item in registry["workloads"]}
        if config["workload_id"] not in workload_ids:
            raise SystemExit("run config workload_id is absent from the corpus")
        payload = {
            "schema": "bass-rfbench-config-validation-v1",
            "status": "PASS_STATIC_ONLY",
            "workload_id": config["workload_id"],
            "candidate_resolved": False,
            "workload_executed": False,
        }
    else:
        if not args.run:
            raise SystemExit("refusing paired execution without explicit --run")
        if args.host_receipt is None:
            raise SystemExit("--run-paired requires --host-receipt")
        config = _load_json(args.run_paired)
        host_receipt = _load_json(args.host_receipt)
        validate_host_probe(host_receipt)
        live_receipt = probe_host(dedicated_host_attestation=dedicated_attestation)
        # Construction reads only host metadata.  Candidate source resolution remains
        # inside run_protocol, after the capability gate.
        if live_receipt.get("claim_level") == "EXPLORATORY_ONLY":
            payload = run_protocol(
                config, host_receipt, live_host_probe=live_receipt,
                collector=None, corpus_path=args.corpus,  # type: ignore[arg-type]
            )
        else:
            collector = CommandCollector(live_receipt)
            payload = run_protocol(
                config, host_receipt, live_host_probe=live_receipt,
                collector=collector, corpus_path=args.corpus,
            )
    _emit(payload, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
