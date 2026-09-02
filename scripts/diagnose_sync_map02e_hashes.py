#!/usr/bin/env python3
"""Print recorded and independently recomputed SYNC-MAP-02E hashes."""
from __future__ import annotations

import json

from scripts.verify_sync_map02e_shared_export import (
    EXPORT_PATH,
    _semantic_hash,
    load_export,
)


def main() -> int:
    export = load_export(EXPORT_PATH)
    rows = []
    mismatch = False
    for formula in sorted(export["formulas"], key=lambda item: item["formula_id"]):
        computed = _semantic_hash(formula["equation_ir"])
        recorded = formula["semantic_hash"]
        same = computed == recorded
        mismatch = mismatch or not same
        rows.append(
            {
                "formula_id": formula["formula_id"],
                "recorded": recorded,
                "computed": computed,
                "same": same,
            }
        )
    print(json.dumps(rows, indent=2, sort_keys=True))
    return int(mismatch)


if __name__ == "__main__":
    raise SystemExit(main())
