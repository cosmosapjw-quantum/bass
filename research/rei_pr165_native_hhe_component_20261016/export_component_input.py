"""Bind the one-event component input to the validated PR164 BASS source."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SOURCE_DIR = Path(__file__).resolve().parents[1] / "rei_pr165_source_intake_20261016"
sys.path.insert(0, str(SOURCE_DIR))
from source_table import BackgroundTable, sha256  # noqa: E402

SOURCE_SHA = "5a7844834b50fbc046995678a6aaf936252a81e49de1593604eee30641274133"
RECEIPT_SHA = "98eddf4673780f0bbca711b373a3e0746cfafc8190674c8d2d6c4de658dc3eed"


def export(output: Path) -> str:
    source_csv = SOURCE_DIR / "source_pr164/PROPOSED_REI_BACKGROUND.csv"
    receipt = SOURCE_DIR / "source_pr164/PRODUCER_RECEIPT.json"
    table = BackgroundTable(receipt, source_csv)
    if table.source_sha256 != SOURCE_SHA or table.manifest_sha256 != RECEIPT_SHA:
        raise ValueError("PINNED_SOURCE_IDENTITY_MISMATCH")
    initial = table.point_at_x("COLD_FLRW", 0.0).as_native_background_point()
    endpoint = table.point_at_x("COLD_FLRW", 1e-4)
    if initial["a"] != 1 / 21 or initial["b"] != 0 or not endpoint.time_s > 0:
        raise ValueError("INITIAL_GEOMETRY_OR_CLOCK_MISMATCH")
    fields = {
        "schema": "bass.rei.pr165.hhe_component_input.v1",
        "case": "COLD_FLRW",
        "source_csv_sha256": table.source_sha256,
        "source_receipt_sha256": table.manifest_sha256,
        "initial_a": initial["a"],
        "initial_b": initial["b"],
        "initial_time_s": initial["time_s"],
        "initial_h_flrw_per_s": initial["h_flrw_per_s"],
        "initial_h_per_s": initial["h_per_s"],
        "initial_s_per_s": initial["s_per_s"],
        "initial_sigma_signed": initial["sigma"],
        "clock_delta_ln_a": 1e-4,
        "proper_dt_s": endpoint.time_s - initial["time_s"],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as handle:
        for key, value in fields.items():
            handle.write(f"{key}={format(value, '.17e') if isinstance(value, float) else value}\n")
    return sha256(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(export(args.output))
