#!/usr/bin/env python3
"""Generate deterministic SYNC-MAP-02C R3 SVG evidence from CSV/JSON inputs."""
from __future__ import annotations

import argparse
import csv
import html
import json
from pathlib import Path


COVERAGE_ORDER = (
    "RELATION_BEARING_SOURCE",
    "REI_NUMERICAL_OR_CLOSURE_EXCLUSION",
    "NONFORMULA_PROTOCOL_OR_TYPED_ABSENCE",
    "RUNNER_OR_LOCAL_STAGE_ONLY",
)
COVERAGE_LABELS = {
    "RELATION_BEARING_SOURCE": "Relation-bearing source",
    "REI_NUMERICAL_OR_CLOSURE_EXCLUSION": "REI numerical / closure exclusion",
    "NONFORMULA_PROTOCOL_OR_TYPED_ABSENCE": "Nonformula protocol / typed absence",
    "RUNNER_OR_LOCAL_STAGE_ONLY": "Runner or local stage only",
}


def load_counts(path: Path) -> dict[str, int]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    counts = {
        row["category"]: int(row["count"])
        for row in rows
        if row["category"] != "TOTAL_EXACT_REI_SOURCE_FILES"
    }
    if set(counts) != set(COVERAGE_ORDER):
        raise SystemExit(f"unexpected coverage categories: {sorted(counts)}")
    if sum(counts.values()) != 22:
        raise SystemExit(f"coverage total is {sum(counts.values())}, expected 22")
    return counts


def render_coverage(counts: dict[str, int]) -> str:
    y_positions = (130, 210, 290, 370)
    text_y = (159, 239, 319, 399)
    bars: list[str] = []
    labels: list[str] = []
    values: list[str] = []
    for category, y, ty in zip(COVERAGE_ORDER, y_positions, text_y, strict=True):
        count = counts[category]
        width = count * 60
        labels.append(
            f'    <text x="410" y="{ty}" text-anchor="end">'
            f'{html.escape(COVERAGE_LABELS[category])}</text>'
        )
        bars.append(f'    <rect x="430" y="{y}" width="{width}" height="42"/>')
        values.append(f'    <text x="{445 + width}" y="{ty}">{count}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="520" viewBox="0 0 1100 520" role="img" aria-labelledby="title desc">
  <title id="title">SYNC-MAP-02C R3 exact REI source coverage</title>
  <desc id="desc">Horizontal bars show seven relation-bearing sources, eight REI numerical or closure exclusions, four nonformula protocol or typed-absence sources, and three runner-only sources, totaling twenty-two exact files.</desc>
  <rect x="0" y="0" width="1100" height="520" fill="white"/>
  <text x="550" y="42" text-anchor="middle" font-family="DejaVu Sans, sans-serif" font-size="26" font-weight="700">SYNC-MAP-02C R3 — exact REI source coverage</text>
  <text x="550" y="72" text-anchor="middle" font-family="DejaVu Sans, sans-serif" font-size="17">Every PR #32 src file has a named relation or machine-bound exclusion</text>
  <line x1="430" y1="110" x2="1030" y2="110" stroke="#222" stroke-width="2"/>
  <line x1="430" y1="110" x2="430" y2="430" stroke="#222" stroke-width="2"/>
  <g font-family="DejaVu Sans, sans-serif" font-size="15" fill="#222">
    <text x="430" y="455" text-anchor="middle">0</text>
    <text x="550" y="455" text-anchor="middle">2</text>
    <text x="670" y="455" text-anchor="middle">4</text>
    <text x="790" y="455" text-anchor="middle">6</text>
    <text x="910" y="455" text-anchor="middle">8</text>
    <text x="730" y="495" text-anchor="middle" font-size="18">Number of exact source files</text>
  </g>
  <g stroke="#c7c7c7" stroke-width="1">
    <line x1="550" y1="110" x2="550" y2="430"/>
    <line x1="670" y1="110" x2="670" y2="430"/>
    <line x1="790" y1="110" x2="790" y2="430"/>
    <line x1="910" y1="110" x2="910" y2="430"/>
  </g>
  <g font-family="DejaVu Sans, sans-serif" font-size="17" fill="#111">
{chr(10).join(labels)}
  </g>
  <g fill="#555" stroke="#222" stroke-width="1.5">
{chr(10).join(bars)}
  </g>
  <g font-family="DejaVu Sans, sans-serif" font-size="19" font-weight="700" fill="#111">
{chr(10).join(values)}
  </g>
  <text x="1030" y="495" text-anchor="end" font-family="DejaVu Sans, sans-serif" font-size="16" font-weight="700">Total: 22 / 22</text>
</svg>
'''


def render_gate(classification: dict[str, object]) -> str:
    gate = classification["next_stage_gate"]
    if not isinstance(gate, dict):
        raise SystemExit("next_stage_gate is not an object")
    if gate.get("status") != "HELD_UNTIL_02C_AND_02D_FROZEN_READBACK":
        raise SystemExit("02E gate status is not the held R3 contract")
    union = classification["shared_formula_consumer_union"]
    if not isinstance(union, dict) or len(union) != 6:
        raise SystemExit("shared formula union is not six records")
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="1160" height="470" viewBox="0 0 1160 470" role="img" aria-labelledby="title desc">
  <title id="title">SYNC-MAP-02C and 02D jointly gate the six-formula 02E export</title>
  <desc id="desc">The repaired REI relation map and verified HTT relation map both point to a held six-formula shared export, which then points to the semantic graph and three consumer bindings before the manual gate.</desc>
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#222"/>
    </marker>
  </defs>
  <rect width="1160" height="470" fill="white"/>
  <text x="580" y="38" text-anchor="middle" font-family="DejaVu Sans, sans-serif" font-size="25" font-weight="700">Post-R3 federation gate</text>
  <text x="580" y="67" text-anchor="middle" font-family="DejaVu Sans, sans-serif" font-size="16">02E consumes the six-record REC + REI + HTT union; neither predecessor may be bypassed</text>

  <g font-family="DejaVu Sans, sans-serif" text-anchor="middle">
    <rect x="55" y="105" width="235" height="92" rx="10" fill="#f2f2f2" stroke="#222" stroke-width="2"/>
    <text x="172" y="137" font-size="19" font-weight="700">02C — REI</text>
    <text x="172" y="164" font-size="15">22-path R3 candidate</text>
    <text x="172" y="185" font-size="14">exact-head readback required</text>

    <rect x="55" y="260" width="235" height="92" rx="10" fill="#f2f2f2" stroke="#222" stroke-width="2"/>
    <text x="172" y="292" font-size="19" font-weight="700">02D — HTT</text>
    <text x="172" y="319" font-size="15">exact-head workflow PASS</text>
    <text x="172" y="340" font-size="14">frozen acceptance readback required</text>

    <rect x="385" y="165" width="285" height="128" rx="10" fill="#e8e8e8" stroke="#111" stroke-width="3"/>
    <text x="527" y="198" font-size="20" font-weight="700">02E — shared export</text>
    <text x="527" y="226" font-size="17">6 BASS-owned Formula IDs</text>
    <text x="527" y="253" font-size="16" font-weight="700">HELD</text>
    <text x="527" y="277" font-size="13">frame / photon only; no background provider</text>

    <rect x="760" y="181" width="185" height="96" rx="10" fill="#f2f2f2" stroke="#222" stroke-width="2"/>
    <text x="852" y="217" font-size="20" font-weight="700">02F</text>
    <text x="852" y="244" font-size="15">semantic graph</text>
    <text x="852" y="265" font-size="13">exact imports only</text>

    <rect x="990" y="105" width="130" height="62" rx="8" fill="#f6f6f6" stroke="#333"/>
    <text x="1055" y="132" font-size="15" font-weight="700">SYNC REC</text>
    <text x="1055" y="153" font-size="12">consumer pin</text>
    <rect x="990" y="198" width="130" height="62" rx="8" fill="#f6f6f6" stroke="#333"/>
    <text x="1055" y="225" font-size="15" font-weight="700">SYNC REI</text>
    <text x="1055" y="246" font-size="12">consumer pin</text>
    <rect x="990" y="291" width="130" height="62" rx="8" fill="#f6f6f6" stroke="#333"/>
    <text x="1055" y="318" font-size="15" font-weight="700">SYNC HTT</text>
    <text x="1055" y="339" font-size="12">consumer pin</text>

    <rect x="760" y="365" width="360" height="66" rx="9" fill="#e8e8e8" stroke="#111" stroke-width="2"/>
    <text x="940" y="393" font-size="17" font-weight="700">SYNC-GATE-01 — MANUAL ONLY</text>
    <text x="940" y="416" font-size="13">no automatic provider, merge, or science promotion</text>
  </g>

  <g stroke="#222" stroke-width="2.5" fill="none" marker-end="url(#arrow)">
    <path d="M290 151 C335 151,340 197,385 207"/>
    <path d="M290 306 C335 306,340 261,385 250"/>
    <path d="M670 229 L760 229"/>
    <path d="M945 214 C970 190,975 150,990 137"/>
    <path d="M945 229 L990 229"/>
    <path d="M945 244 C970 268,975 310,990 322"/>
    <path d="M1055 167 L1055 365"/>
    <path d="M1055 260 L1055 365"/>
    <path d="M1055 353 L1055 365"/>
  </g>

  <text x="55" y="432" font-family="DejaVu Sans, sans-serif" font-size="14">Forbidden shortcut: 02B REC → four-formula export</text>
</svg>
'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    root = Path("docs/bass_master_ssot_v2/SYNC_MAP_02C")
    parser.add_argument("--coverage-summary", type=Path, default=root / "R3_SOURCE_COVERAGE_SUMMARY.csv")
    parser.add_argument("--classification", type=Path, default=root / "REI_RELATION_CLASSIFICATION_R3.json")
    parser.add_argument("--output-dir", type=Path, default=root)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    counts = load_counts(args.coverage_summary)
    classification = json.loads(args.classification.read_text(encoding="utf-8"))
    (args.output_dir / "R3_SOURCE_COVERAGE_SUMMARY.svg").write_text(
        render_coverage(counts), encoding="utf-8"
    )
    (args.output_dir / "R3_FEDERATION_GATE.svg").write_text(
        render_gate(classification), encoding="utf-8"
    )
    print(json.dumps({"status": "PASS", "source_total": sum(counts.values()), "shared_formula_count": 6}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
