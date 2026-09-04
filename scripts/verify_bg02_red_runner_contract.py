#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def verify(source: str) -> dict[str, object]:
    ancestry_assignment = 'PARENT_ANCESTRY_PASS=true' in source
    ancestry_condition = re.search(
        r'if \[ "\$PARENT_ANCESTRY_PASS" = true \] \\\n\s*&& \[ "\$RAW_RC" -eq 1 \]',
        source,
    ) is not None
    stale_head_condition = re.search(
        r'if \[ "\$HEAD" = "\$EXPECTED_HEAD" \] \\\n\s*&& \[ "\$RAW_RC" -eq 1 \]',
        source,
    ) is not None
    receipt_ancestry = '"scientific_parent_is_ancestor"' in source
    if not ancestry_assignment:
        raise ValueError("ancestry assignment missing")
    if not ancestry_condition:
        raise ValueError("expected-RED status does not consume ancestry gate")
    if stale_head_condition:
        raise ValueError("stale HEAD-equals-parent gate remains")
    if not receipt_ancestry:
        raise ValueError("ancestry receipt field missing")
    return {
        "schema_version": "1.0.0",
        "stage_id": "BG_02_RED_RUNNER_ANCESTRY_CONTRACT",
        "ancestry_assignment": ancestry_assignment,
        "ancestry_condition": ancestry_condition,
        "stale_head_condition": stale_head_condition,
        "receipt_ancestry": receipt_ancestry,
        "status": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runner", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = verify(args.runner.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
