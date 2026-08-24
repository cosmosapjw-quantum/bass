from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lowering.rust_typeii import generate_typeii_rust_bundle

FORMULA = "3ecf0dbc8b47a8af83da81e9ed37823b6922e139e420c5bfa2e071b6bbabe361"


def test_generator_emits_expected_rust_modules(tmp_path):
    result = generate_typeii_rust_bundle(tmp_path, formula_authority_hash=FORMULA)
    assert set(result.files) == {
        "mod.rs",
        "typeii_background.rs",
        "typeii_kato.rs",
        "typeii_collision.rs",
        "manifest.json",
    }
    for name in result.files:
        assert (tmp_path / name).is_file()


def test_manifest_pins_formula_and_has_deterministic_hash(tmp_path):
    a = generate_typeii_rust_bundle(tmp_path / "a", formula_authority_hash=FORMULA)
    b = generate_typeii_rust_bundle(tmp_path / "b", formula_authority_hash=FORMULA)
    ma = json.loads((tmp_path / "a" / "manifest.json").read_text())
    mb = json.loads((tmp_path / "b" / "manifest.json").read_text())
    assert ma["formula_authority_sha256"] == FORMULA
    assert ma["bundle_content_sha256"] == mb["bundle_content_sha256"]


def test_background_module_contains_rhs_and_jvp(tmp_path):
    generate_typeii_rust_bundle(tmp_path, formula_authority_hash=FORMULA)
    text = (tmp_path / "typeii_background.rs").read_text()
    assert "pub fn rhs" in text
    assert "pub fn jvp" in text
    assert "[f64; 5]" in text


def test_kato_module_is_low_rank_not_dense(tmp_path):
    generate_typeii_rust_bundle(tmp_path, formula_authority_hash=FORMULA)
    text = (tmp_path / "typeii_kato.rs").read_text()
    assert "projector_apply" in text
    assert "projector_dv_apply" in text
    assert "kato_apply" in text
    assert "Vec<Vec<f64>>" not in text
    assert "Matrix" not in text


def test_collision_module_is_matrix_free_moment_action(tmp_path):
    generate_typeii_rust_bundle(tmp_path, formula_authority_hash=FORMULA)
    text = (tmp_path / "typeii_collision.rs").read_text()
    assert "collision_generator_apply" in text
    assert "moment" in text.lower()
    assert "Vec<Vec<f64>>" not in text


def test_generated_rust_preserves_multiplicative_grouping(tmp_path):
    generate_typeii_rust_bundle(tmp_path, formula_authority_hash=FORMULA)
    text = (tmp_path / "typeii_background.rs").read_text()
    # SymPy 1.14 Rust printer can misrender x*(g-1.0) unless the lowering
    # layer expands multiplication over sums before printing.
    assert "r2*gamma - 1.0;" not in text
    assert "gamma*r2 - 1.0*r2" in text or "r2*gamma - 1.0*r2" in text
