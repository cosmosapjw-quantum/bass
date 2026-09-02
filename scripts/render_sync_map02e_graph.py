#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "docs/bass_master_ssot_v2/SYNC_MAP_02E/BASS_SHARED_FRAME_PHOTON_EXPORT.json"
DEFAULT_OUTPUT = ROOT / "docs/bass_master_ssot_v2/SYNC_MAP_02E/SHARED_FORMULA_DAG.svg"
SHORT = {
    "BASS.FRAME.DOPPLER_FACTOR.001": "Doppler factor",
    "BASS.FRAME.ABERRATED_DIRECTION.001": "Aberrated direction",
    "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001": "Solid-angle Jacobian",
    "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001": "Blackbody T pullback",
    "BASS.PHOTON.ENERGY_DRIFT.001": "Photon energy drift",
    "BASS.PHOTON.DIRECTION_FLOW.001": "Photon direction flow",
}
FORMULA_ORDER = [
    "BASS.FRAME.DOPPLER_FACTOR.001",
    "BASS.FRAME.ABERRATED_DIRECTION.001",
    "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
    "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001",
    "BASS.PHOTON.ENERGY_DRIFT.001",
    "BASS.PHOTON.DIRECTION_FLOW.001",
]
POSITIONS = {
    "BASS.FRAME.DOPPLER_FACTOR.001": (55, 145),
    "BASS.FRAME.ABERRATED_DIRECTION.001": (335, 90),
    "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001": (335, 200),
    "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001": (640, 90),
    "BASS.PHOTON.ENERGY_DRIFT.001": (55, 390),
    "BASS.PHOTON.DIRECTION_FLOW.001": (335, 390),
}
BOX_W = 205
BOX_H = 58


def rect(x: int, y: int, w: int, h: int, label: str, sub: str = "") -> str:
    lines = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" '
        'fill="white" stroke="#222" stroke-width="1.5"/>'
    ]
    lines.append(
        f'<text x="{x+w/2}" y="{y+24}" text-anchor="middle" '
        f'font-size="14" font-weight="600">{html.escape(label)}</text>'
    )
    if sub:
        lines.append(
            f'<text x="{x+w/2}" y="{y+44}" text-anchor="middle" '
            f'font-size="11">{html.escape(sub)}</text>'
        )
    return "\n".join(lines)


def arrow_path(d: str, dashed: bool = False) -> str:
    dash = ' stroke-dasharray="6 5"' if dashed else ""
    return (
        f'<path d="{d}" fill="none" stroke="#333" stroke-width="1.5" '
        f'marker-end="url(#arrow)"{dash}/>'
    )


def render(data: dict) -> str:
    by_id = {item["formula_id"]: item for item in data["formulas"]}
    consumers = ["rec_bianchi", "rei_bianchi", "htt_base"]
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="650" viewBox="0 0 1400 650">',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#333"/></marker></defs>',
        '<rect width="1400" height="650" fill="white"/>',
        '<text x="700" y="30" text-anchor="middle" font-size="19" font-weight="700">SYNC-MAP-02E shared frame/photon EquationIR export</text>',
        '<text x="55" y="64" font-size="15" font-weight="700">A. Formula and dependency graph</text>',
        '<text x="855" y="64" font-size="15" font-weight="700">B. Pinned-import consumer matrix</text>',
        '<text x="55" y="116" font-size="13" font-weight="700">BASS.FRAME</text>',
        '<text x="55" y="365" font-size="13" font-weight="700">BASS.PHOTON</text>',
    ]
    for fid in FORMULA_ORDER:
        x, y = POSITIONS[fid]
        out.append(rect(x, y, BOX_W, BOX_H, SHORT[fid], by_id[fid]["equation_ir"]["dimensions"]["target"]))

    # Solid arrows point from a dependent formula to the formula it requires.
    out.extend([
        arrow_path("M335,119 C310,119 292,145 260,160"),
        arrow_path("M335,229 C305,229 292,190 260,174"),
        arrow_path("M640,112 L540,112"),
        arrow_path("M640,100 C520,45 245,45 158,145"),
    ])

    # External BASS.GEO dependencies are kept separate from the internal six-node DAG.
    out.append(rect(640, 355, 190, 52, "Extrinsic/shear split", "BASS.GEO"))
    out.append(rect(640, 430, 190, 52, "Structure constants", "BASS.GEO"))
    out.extend([
        arrow_path("M260,419 C400,330 555,340 640,381", dashed=True),
        arrow_path("M540,412 C575,400 600,391 640,381", dashed=True),
        arrow_path("M540,433 C575,443 600,451 640,456", dashed=True),
    ])

    # Consumer matrix replaces a spaghetti edge fan-out.
    tx, ty = 855, 90
    label_w, cell_w, row_h = 205, 92, 50
    out.append(f'<rect x="{tx}" y="{ty}" width="{label_w+3*cell_w}" height="{row_h*7}" fill="white" stroke="#222" stroke-width="1.4"/>')
    for i in range(1, 7):
        y = ty + i * row_h
        out.append(f'<line x1="{tx}" y1="{y}" x2="{tx+label_w+3*cell_w}" y2="{y}" stroke="#777" stroke-width="1"/>')
    for i in range(4):
        x = tx + label_w + i * cell_w
        out.append(f'<line x1="{x}" y1="{ty}" x2="{x}" y2="{ty+row_h*7}" stroke="#777" stroke-width="1"/>')
    out.append(f'<text x="{tx+8}" y="{ty+31}" font-size="12" font-weight="700">Formula</text>')
    for j, consumer in enumerate(consumers):
        out.append(f'<text x="{tx+label_w+j*cell_w+cell_w/2}" y="{ty+31}" text-anchor="middle" font-size="11" font-weight="700">{consumer}</text>')
    for i, fid in enumerate(FORMULA_ORDER, start=1):
        y = ty + i * row_h
        out.append(f'<text x="{tx+8}" y="{y+31}" font-size="11">{html.escape(SHORT[fid])}</text>')
        allowed = set(by_id[fid]["consumer_repositories"])
        for j, consumer in enumerate(consumers):
            mark = "YES" if consumer in allowed else "—"
            out.append(f'<text x="{tx+label_w+j*cell_w+cell_w/2}" y="{y+31}" text-anchor="middle" font-size="11">{mark}</text>')

    out.extend([
        '<text x="55" y="540" font-size="12">Solid: internal six-formula dependency (dependent → required formula).</text>',
        '<text x="55" y="562" font-size="12">Dashed: dependency on the pre-existing BASS.GEO EquationIR registry.</text>',
        '<text x="55" y="604" font-size="11">Excluded by the scope firewall: numerical background provider, global matter tilt, finite-electron collision,</text>',
        '<text x="55" y="622" font-size="11">recombination/reionization microphysics, mask/beam/estimator response, solver runtime, likelihood and science promotion.</text>',
        '</svg>',
    ])
    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    data = json.loads(args.source.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(data), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
