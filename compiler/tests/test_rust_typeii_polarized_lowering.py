from __future__ import annotations
import json
from pathlib import Path
import tempfile
import os, shutil
from compiler.lowering.rust_typeii_polarized import generate, POL_AUTHORITY_SHA256

ROOT=Path(__file__).resolve().parents[2]
CHECKED=ROOT/'generated'/'rust'/'typeii'
RUSTFMT=os.environ.get('BASS_RUSTFMT') or shutil.which('rustfmt') or 'rustfmt'

def test_polarized_lowering_is_deterministic_and_matches_checked_source():
    with tempfile.TemporaryDirectory() as td:
        out=Path(td)
        manifest=generate(out,RUSTFMT)
        assert (out/'typeii_polarized.rs').read_bytes()==(CHECKED/'typeii_polarized.rs').read_bytes()
        assert manifest['polarization_authority_sha256']==POL_AUTHORITY_SHA256
        assert manifest['generated_files']['typeii_polarized.rs']==json.loads((CHECKED/'polarized_manifest.json').read_text())['generated_files']['typeii_polarized.rs']

def test_generated_source_keeps_load_bearing_semantics_explicit():
    s=(CHECKED/'typeii_polarized.rs').read_text()
    for token in ['collision_generator_apply_polarized','equilibrium_state_polarized','projector_dv_apply_polarized','kato_apply_polarized','d.powi(4)','weights[i] / d.powi(2)','3.0 / (8.0 * PI)']:
        assert token in s
