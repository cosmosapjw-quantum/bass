#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs/bass_master_ssot_v2/SYNC_MAP_02F/EXTERNAL_CAS_MATRIX.json"
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_expression(value: str) -> str:
    value = ANSI.sub("", value).strip().rstrip(";").strip()
    value = re.sub(r"\s+", "", value)
    return value


def parse_log(text: str) -> tuple[dict[str, bool], dict[str, bool], list[str]]:
    identities: dict[str, bool] = {}
    mutations: dict[str, bool] = {}
    evidence: list[str] = []
    for raw in text.splitlines():
        line = ANSI.sub("", raw)
        for marker, target in (("CHECK|", identities), ("MUTATION|", mutations)):
            pos = line.find(marker)
            if pos >= 0:
                parts = line[pos:].strip().split("|", 3)
                if len(parts) >= 3:
                    target[parts[1]] = parts[2].strip().upper() == "PASS"
                    evidence.append(line[pos:].strip())
        for marker, target, expect_zero in (
            ("EXPR_CHECK|", identities, True),
            ("EXPR_MUTATION|", mutations, False),
        ):
            pos = line.find(marker)
            if pos >= 0:
                parts = line[pos:].strip().split("|", 2)
                if len(parts) == 3:
                    expression = clean_expression(parts[2])
                    is_zero = expression in {"0", "+0", "-0", "0.0"}
                    target[parts[1]] = is_zero if expect_zero else not is_zero
                    evidence.append(line[pos:].strip())
    return identities, mutations, evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--version-file", type=Path, required=True)
    parser.add_argument("--downloads", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--process-exit-code", type=int, required=True)
    parser.add_argument("--allow-failure", action="store_true")
    args = parser.parse_args()

    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    engine_rows = [row for row in matrix["engines"] if row["engine"] == args.engine]
    if len(engine_rows) != 1:
        raise SystemExit(f"engine contract not unique: {args.engine}")
    contract = engine_rows[0]
    required = bool(contract["required_for_axis_closeout"])

    log_text = args.log.read_text(encoding="utf-8", errors="replace") if args.log.exists() else ""
    version = (
        args.version_file.read_text(encoding="utf-8", errors="replace").strip()
        if args.version_file.exists()
        else "VERSION_UNAVAILABLE"
    )
    identities, mutations, evidence = parse_log(log_text)
    expected_identity_ids = list(contract["expected_identity_ids"])
    hostile_mutations = list(contract["hostile_mutations"])
    missing_identities = sorted(set(expected_identity_ids) - set(identities))
    missing_mutations = sorted(set(hostile_mutations) - set(mutations))
    failed_identities = sorted(key for key in expected_identity_ids if identities.get(key) is False)
    escaped_mutations = sorted(key for key in hostile_mutations if mutations.get(key) is False)

    download_sha256: dict[str, str] = {}
    if args.downloads.exists():
        for path in sorted(p for p in args.downloads.rglob("*") if p.is_file()):
            download_sha256[path.relative_to(args.downloads).as_posix()] = sha256(path)

    pass_contract = (
        args.process_exit_code == 0
        and not missing_identities
        and not missing_mutations
        and not failed_identities
        and not escaped_mutations
        and bool(download_sha256)
        and version not in {"", "VERSION_UNAVAILABLE"}
    )
    if pass_contract:
        status = "PASS"
    elif required:
        status = "FAIL"
    else:
        status = "EXPLORATORY_UNAVAILABLE_OR_EXECUTION_FAILED"

    receipt = {
        "schema_version": "1.0.0",
        "stage_id": matrix["stage_id"],
        "engine": args.engine,
        "implementation_family": contract["implementation_family"],
        "required_for_axis_closeout": required,
        "status": status,
        "authority_effect": "NONE",
        "acquisition": contract["acquisition"],
        "version": version,
        "process_exit_code": args.process_exit_code,
        "expected_identity_ids": expected_identity_ids,
        "identity_results": identities,
        "hostile_mutations": hostile_mutations,
        "mutation_results": mutations,
        "missing_identities": missing_identities,
        "failed_identities": failed_identities,
        "missing_mutations": missing_mutations,
        "escaped_mutations": escaped_mutations,
        "download_sha256": download_sha256,
        "raw_evidence_lines": evidence,
        "claim_effect": "NONE",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))

    if required and not pass_contract and not args.allow_failure:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
