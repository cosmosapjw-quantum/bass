"""Byte-level contracts for generated Rust data that previously drifted."""

from __future__ import annotations

from pathlib import Path
import re

from scripts import codegen_coeff_tables as coeff_codegen


ROOT = Path(__file__).resolve().parents[1]


def test_coefficient_generator_canonicalizes_zero_and_matches_checked_source():
    generated = coeff_codegen.generate()
    checked = (ROOT / "_rustcore/src/kinetic/coeff_tables.rs").read_text()

    assert generated == checked
    assert re.search(r"(?<![\d.])-0\.0(?=[,\]])", generated) is None
