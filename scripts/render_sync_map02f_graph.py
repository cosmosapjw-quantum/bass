#!/usr/bin/env python3
from __future__ import annotations

import csv
import html
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "docs/bass_master_ssot_v2/SYNC_MAP_02F/CROSS_REPOSITORY_SEMANTIC_GRAPH.json"
OUT = ROOT / "artifacts/sync_map02f"


def main() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)

    class_counts = Counter(record["relation_class"] for record in graph["consumer_relations"])
    consumer_counts = Counter(record["consumer_repository"] for record in graph["consumer_relations"])
    with (OUT / "RELATION_CLASS_COUNTS.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["relation_class", "count"])
        for key in sorted(class_counts):
            writer.writerow([key, class_counts[key]])
    with (OUT / "CONSUMER_COUNTS.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["consumer_repository", "count"])
        for key in sorted(consumer_counts):
            writer.writerow([key, consumer_counts[key]])

    formulas = graph["authority_formulas"]
    relations = graph["consumer_relations"]
    consumers = ["rec_bianchi", "rei_bianchi", "htt_base"]
    width, height = 1500, 760
    formula_x, consumer_x = 420, 1120
    formula_y = {record["formula_id"]: 95 + 105 * index for index, record in enumerate(formulas)}
    consumer_y = {name: 180 + 190 * index for index, name in enumerate(consumers)}

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect x="0" y="0" width="1500" height="760" fill="white"/>',
        '<style>text{font-family:DejaVu Sans,Arial,sans-serif;fill:#111} .title{font-size:26px;font-weight:bold}.label{font-size:16px}.small{font-size:13px}.node{fill:#f5f5f5;stroke:#222;stroke-width:1.5}.edge{stroke:#555;stroke-width:1.4;fill:none}.dashed{stroke-dasharray:7 5}</style>',
        '<text x="750" y="38" text-anchor="middle" class="title">SYNC-MAP-02F bounded semantic relation graph</text>',
        '<text x="420" y="70" text-anchor="middle" class="label">BASS authoritative Formula IDs</text>',
        '<text x="1120" y="70" text-anchor="middle" class="label">consumer repositories</text>',
    ]

    for relation in relations:
        y1 = formula_y[relation["formula_id"]]
        y2 = consumer_y[relation["consumer_repository"]]
        dashed = " dashed" if relation["relation_class"] in {"ABSENT_REQUIRED_DEPENDENCY", "NON_EQUIVALENT_RESTRICTED_CONTROL"} else ""
        lines.append(f'<path d="M 720 {y1} C 850 {y1}, 900 {y2}, 1010 {y2}" class="edge{dashed}"/>')

    for record in formulas:
        y = formula_y[record["formula_id"]]
        lines.append(f'<rect x="120" y="{y-30}" width="600" height="60" rx="8" class="node"/>')
        lines.append(f'<text x="420" y="{y-3}" text-anchor="middle" class="label">{html.escape(record["formula_id"])}</text>')
        lines.append(f'<text x="420" y="{y+19}" text-anchor="middle" class="small">owner=bass; dim={html.escape(record["dimensions"])}</text>')

    for name in consumers:
        y = consumer_y[name]
        count = consumer_counts[name]
        lines.append(f'<rect x="1010" y="{y-42}" width="220" height="84" rx="8" class="node"/>')
        lines.append(f'<text x="1120" y="{y-3}" text-anchor="middle" class="label">{html.escape(name)}</text>')
        lines.append(f'<text x="1120" y="{y+21}" text-anchor="middle" class="small">{count} bounded relations</text>')

    lines.extend([
        '<line x1="1050" y1="700" x2="1100" y2="700" class="edge"/><text x="1110" y="705" class="small">equivalence/adapter/oracle relation</text>',
        '<line x1="1050" y1="728" x2="1100" y2="728" class="edge dashed"/><text x="1110" y="733" class="small">absent or non-equivalent restricted control</text>',
        '</svg>',
    ])
    (OUT / "SEMANTIC_GRAPH.svg").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "formula_count": len(formulas),
        "relation_count": len(relations),
        "class_counts": dict(sorted(class_counts.items())),
        "consumer_counts": dict(sorted(consumer_counts.items())),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
