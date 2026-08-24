from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest
import sympy as sp


REPO = Path(__file__).resolve().parents[2]
PACKET = REPO / "compiler" / "wolfram" / "generic_bianchi_candidate"
MODULE_PATH = PACKET / "verify_result.py"
SPEC = importlib.util.spec_from_file_location("generic_bianchi_verify_result", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
VR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VR)


def fixture(name: str) -> dict:
    return VR.load_json(PACKET / "fixtures" / name)


def test_fixed_source_and_authority_boundaries():
    source = VR.load_json(PACKET / "SOURCE_REF.json")
    authority = VR.load_json(PACKET / "AUTHORITY_STATUS.json")
    assert source["base_commit"] == VR.BASE_COMMIT
    assert source["base_tree"] == VR.BASE_TREE
    assert authority["candidate_status"] == VR.AUTHORITY_STATUS
    assert authority["post_execution_ceiling"] == "VALIDATED_NEW_CANDIDATE"
    assert authority["historical_formula"] == {
        "is_dag_parent": False,
        "label_sha256": VR.HISTORICAL_FORMULA,
        "source_bytes": "ABSENT",
        "status": "UNRESOLVED_REFERENCE",
    }
    assert authority["workmode_receipt"]["id"] == "WOLFRAM-WORKMODE-20260824-R1"
    assert authority["workmode_receipt"]["project_replay"] is False


def test_json_schemas_are_local_parseable_and_cover_candidate_contract():
    spec_schema = VR.load_json(PACKET / "schemas" / "bianchi-spec-v1.schema.json")
    symir_schema = VR.load_json(PACKET / "schemas" / "symir-v2.schema.json")
    result_schema = VR.load_json(PACKET / "RESULT_SCHEMA.json")
    assert spec_schema["$schema"].endswith("2020-12/schema")
    assert {"structure_constants", "na_decomposition", "matrix_generators"} <= set(spec_schema["properties"])
    assert "invariant_embedding" in spec_schema["properties"]
    assert {"tensors", "expressions", "dependency_dag", "cse_temporaries", "adapters"} <= set(symir_schema["properties"])
    assert "formula_source_hashes" in symir_schema["required"]
    assert result_schema["properties"]["aggregate_status"]["const"] == "VALIDATED_NEW_CANDIDATE"


def test_all_focused_fixtures_validate_exactly_and_without_float_authority():
    records = VR.validate_packet_root(PACKET)
    assert set(records) == {
        "I", "II_equivalent", "VI_0", "VII_0", "VIII", "IX_D",
        "V_class_B", "VIstar_minus_1_9",
    }
    assert records["I"]["oracle"]["spatial_scalar_curvature"] == {"kind": "integer", "value": 0}
    assert "positive_definite_D_normalization" in records["IX_D"]["adapters"]
    assert records["V_class_B"]["adapters"] == ["class_B"]


def test_equivalent_c_na_and_adjoint_generator_representations_canonicalize_identically():
    full = fixture("II_equivalent.json")
    c_only = {k: v for k, v in full.items() if k not in {"na_decomposition", "matrix_generators", "generator_representation"}}
    na_only = {k: v for k, v in full.items() if k not in {"structure_constants", "matrix_generators", "generator_representation"}}
    g_only = {k: v for k, v in full.items() if k not in {"structure_constants", "na_decomposition"}}
    canonical = [VR.canonical_json_bytes(VR.validate_spec(value)) for value in (c_only, na_only, g_only)]
    assert canonical[0] == canonical[1] == canonical[2]


def test_antisymmetry_jacobi_and_generator_closure_fail_closed():
    raw = fixture("II_equivalent.json")
    raw.pop("na_decomposition")
    raw.pop("matrix_generators")
    raw.pop("generator_representation")
    one_sided = copy.deepcopy(raw)
    one_sided["structure_constants"]["entries"].pop()
    with pytest.raises(VR.PacketError, match="antisymmetry"):
        VR.validate_spec(one_sided)

    bad_jacobi = copy.deepcopy(raw)
    bad_jacobi["structure_constants"] = {
        "entries": [
            {"indices": [0, 0, 1], "value": {"kind": "integer", "value": 1}},
            {"indices": [0, 1, 0], "value": {"kind": "integer", "value": -1}},
            {"indices": [1, 1, 2], "value": {"kind": "integer", "value": 1}},
            {"indices": [1, 2, 1], "value": {"kind": "integer", "value": -1}},
        ],
        "shape": [3, 3, 3],
    }
    with pytest.raises(VR.PacketError, match="Jacobi"):
        VR.validate_spec(bad_jacobi)

    canonical = VR.validate_spec(fixture("II_equivalent.json"))
    c = VR.tensor_from_sparse(canonical["structure_constants"], (3, 3, 3))
    generators = VR.generators_from_c(c)
    generators[0][0, 0] = 1
    with pytest.raises(VR.PacketError, match="closure"):
        VR._check_generator_closure(generators, c)


def test_hash_float_and_ambiguous_generator_inputs_fail_closed():
    wrong_hash = fixture("I.json")
    wrong_hash["convention_hash"] = "0" * 64
    with pytest.raises(VR.PacketError, match="convention hash"):
        VR.validate_spec(wrong_hash)

    inexact = fixture("I.json")
    inexact["metadata"]["diagnostic"] = 0.0
    with pytest.raises(VR.PacketError, match="inexact JSON float"):
        VR.validate_spec(inexact)

    ambiguous = fixture("II_equivalent.json")
    ambiguous.pop("structure_constants")
    ambiguous.pop("na_decomposition")
    ambiguous["generator_representation"] = "faithful_embedding"
    with pytest.raises(VR.PacketError, match="AMBIGUOUS_GENERATOR_REPRESENTATION"):
        VR.validate_spec(ambiguous)


def test_exact_algebraic_root_selector_round_trips_canonically():
    encoded = {
        "isolating_interval": [
            {"kind": "integer", "value": 1},
            {"kind": "integer", "value": 2},
        ],
        "kind": "algebraic",
        "minimal_polynomial": [1, 0, -2],
        "root_index": 1,
    }
    value = VR.decode_exact(encoded)
    assert sp.simplify(value - sp.sqrt(2)) == 0
    assert VR.decode_exact(VR.encode_exact(value)) == value


def test_exact_faithful_matrix_representation_closes_and_binds_to_c():
    base = VR.validate_spec(fixture("V_class_B.json"))
    c = VR.tensor_from_sparse(base["structure_constants"], (3, 3, 3))
    generator_tensor = sp.MutableDenseNDimArray(
        [entry for matrix in VR.generators_from_c(c) for entry in matrix], (3, 3, 3)
    )
    raw = fixture("V_class_B.json")
    raw["generator_representation"] = "faithful_embedding"
    raw["matrix_generators"] = VR.sparse_from_tensor(generator_tensor)
    raw["representation_certificate"] = {
        "faithful": True,
        "structure_constants_sha256": VR.sha256_bytes(VR.canonical_json_bytes(raw["structure_constants"])),
        "uniquely_recoverable": True,
    }
    assert VR.validate_spec(raw)["structure_constants"] == base["structure_constants"]
    broken = copy.deepcopy(raw)
    broken["matrix_generators"]["entries"][0]["value"]["value"] += 1
    with pytest.raises(VR.PacketError, match="closed|disagree|certificate"):
        VR.validate_spec(broken)


def test_exact_invariant_embedding_and_maurer_cartan_fail_closed():
    valid = fixture("I.json")
    canonical = VR.validate_spec(valid)
    assert "invariant_embedding" in canonical
    invalid = copy.deepcopy(valid)
    invalid["invariant_embedding"]["maurer_cartan_coefficients"]["entries"] = [
        {"indices": [0, 1, 2], "value": {"kind": "integer", "value": 1}}
    ]
    with pytest.raises(VR.PacketError, match="Maurer-Cartan"):
        VR.validate_spec(invalid)


def test_type_labels_are_metadata_and_typeii_projector_does_not_leak():
    ii = VR.validate_spec(fixture("II_equivalent.json"))
    changed_label = copy.deepcopy(ii)
    changed_label["metadata"]["type_label"] = "VIII"
    assert VR.adapter_ids(changed_label) == VR.adapter_ids(ii)
    assert "rank_one_axis_projector" in VR.adapter_ids(ii)
    for name in ("VI_0.json", "VII_0.json", "VIII.json"):
        assert "rank_one_axis_projector" not in VR.adapter_ids(VR.validate_spec(fixture(name)))


def test_exceptional_adapter_uses_exact_codazzi_rank_loss():
    exceptional = VR.validate_spec(fixture("VIstar_minus_1_9.json"))
    n = VR.tensor_from_sparse(exceptional["na_decomposition"]["n"], (3, 3))
    a = VR.tensor_from_sparse(exceptional["na_decomposition"]["a"], (3,))
    assert VR.codazzi_map(n, a).rank() == 2
    assert "exceptional_codazzi_rank_loss" in VR.adapter_ids(exceptional)


def test_orientation_change_transforms_n_as_pseudotensor_and_changes_hash():
    canonical = VR.validate_spec(fixture("VI_0.json"))
    n = VR.tensor_from_sparse(canonical["na_decomposition"]["n"], (3, 3))
    a = VR.tensor_from_sparse(canonical["na_decomposition"]["a"], (3,))
    reflection = sp.diag(-1, 1, 1)
    transformed_n, transformed_a = VR.transform_na_orientation(n, a, reflection)
    expected = -reflection * sp.Matrix(n.tolist()) * reflection.T
    assert sp.Matrix(transformed_n.tolist()) == expected
    assert sp.Matrix(transformed_a.tolist()) == reflection * sp.Matrix(a.tolist())
    convention = copy.deepcopy(canonical["convention"])
    convention["epsilon_orientation"]["handedness"] = "left"
    convention["epsilon_orientation"]["epsilon_012"]["value"] = -1
    assert VR.sha256_bytes(VR.canonical_json_bytes(convention)) != canonical["convention_hash"]


def test_selected_component_oracle_matches_existing_independent_sympy_formula():
    # Load the source oracle directly: importing bianchi/__init__.py would pull
    # JAX, which is unrelated to this exact static compiler check.
    frame_path = REPO / "bianchi" / "symbolic" / "frame.py"
    frame_spec = importlib.util.spec_from_file_location("generic_packet_frame_oracle", frame_path)
    assert frame_spec is not None and frame_spec.loader is not None
    frame_module = importlib.util.module_from_spec(frame_spec)
    frame_spec.loader.exec_module(frame_module)
    R3_closed_form = frame_module.R3_closed_form
    for path in sorted((PACKET / "fixtures").glob("*.json")):
        canonical = VR.validate_spec(VR.load_json(path))
        n = VR.tensor_from_sparse(canonical["na_decomposition"]["n"], (3, 3))
        a = VR.tensor_from_sparse(canonical["na_decomposition"]["a"], (3,))
        expected = R3_closed_form(n.tolist(), a.tolist())
        assert VR.selected_oracle(canonical)["spatial_scalar_curvature"] == VR.encode_exact(expected)


def _wolfram_structural_scan(text: str) -> None:
    pairs = {"(": ")", "[": "]", "{": "}"}
    closers = {value: key for key, value in pairs.items()}
    stack: list[tuple[str, int]] = []
    comment_depth = 0
    in_string = False
    escaped = False
    index = 0
    while index < len(text):
        char = text[index]
        nxt = text[index : index + 2]
        if comment_depth:
            if nxt == "(*":
                comment_depth += 1
                index += 2
                continue
            if nxt == "*)":
                comment_depth -= 1
                index += 2
                continue
            index += 1
            continue
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue
        if nxt == "(*":
            comment_depth = 1
            index += 2
            continue
        if char == '"':
            in_string = True
        elif char in pairs:
            stack.append((char, index))
        elif char in closers:
            assert stack and stack[-1][0] == closers[char], f"mismatched {char} at {index}"
            stack.pop()
        index += 1
    assert comment_depth == 0, "unterminated Wolfram comment"
    assert not in_string, "unterminated Wolfram string"
    assert not stack, f"unclosed Wolfram delimiter: {stack[-1] if stack else None}"


def test_wolfram_sources_pass_structural_lint_and_bounded_token_contract():
    sources = {path.name: path.read_text(encoding="utf-8") for path in sorted(PACKET.glob("*.wl*"))}
    assert set(sources) == {
        "BianchiSpec.wl", "GenericAdapters.wl", "GenericFrameDerivation.wl",
        "SymIRV2Export.wl", "run_workmode_validation.wls",
    }
    for text in sources.values():
        _wolfram_structural_scan(text)
    joined = "\n".join(sources.values())
    for required in (
        "SparseArray", "BASSCheckJacobi", "BASSValidateGenerators", "ToCanonical",
        "MatrixRank", "BASSCodazziMap", "CANDIDATE_UNPROMOTED_FORMULA_BYTES_ABSENT",
        "COLD_WARM_CANONICAL_DRIFT", "AMBIGUOUS_GENERATOR_REPRESENTATION",
    ):
        assert required in joined
    for forbidden in (
        "FullSimplify", "ReplaceRepeated", "LaunchKernels", "ParallelSubmit",
        "RunProcess", "StartProcess", "RECOVERED_HISTORICAL_AUTHORITY",
    ):
        assert forbidden not in joined
    dispatch_sources = sources["GenericAdapters.wl"] + sources["GenericFrameDerivation.wl"]
    assert "type_label" not in dispatch_sources


def test_manifest_is_complete_sorted_and_secret_path_clean():
    VR.verify_manifest(PACKET)
    forbidden = (
        "/home/", "/tmp/", "ghp_", "github_pat_", "BEGIN PRIVATE KEY",
        "CARGO_REGISTRIES_CRATES_IO_TOKEN", ".netrc",
    )
    for relative in VR._manifest_paths(PACKET):
        data = (PACKET / relative).read_bytes()
        if b"\0" in data:
            continue
        text = data.decode("utf-8")
        assert not any(token in text for token in forbidden), relative


def test_handoff_workmode_line_budget_and_execution_boundary():
    text = (PACKET / "HANDOFF_WORKMODE.md").read_text(encoding="utf-8")
    assert len([line for line in text.splitlines() if line.strip()]) <= 40
    assert "do not rerun" in text
    assert "VALIDATED_NEW_CANDIDATE" in text
    assert "recovered historical authority" in text


def test_synthetic_workmode_result_parser_checks_cold_warm_and_oracle(tmp_path: Path):
    records = VR.validate_packet_root(PACKET)
    (tmp_path / "cold").mkdir()
    (tmp_path / "warm").mkdir()
    entries = []
    for fixture_id, record in sorted(records.items()):
        source_hashes = {
            name: VR.sha256_file(PACKET / name)
            for name in (
                "BianchiSpec.wl", "GenericAdapters.wl",
                "GenericFrameDerivation.wl", "SymIRV2Export.wl",
            )
        }
        spec_hash = record["canonical_sha256"]
        receipt_hash = "1" * 64
        obj = {
            "adapters": [
                {
                    "adapter_id": adapter_id,
                    "input_hash": spec_hash,
                    "output_assumptions": ["synthetic parser fixture"],
                    "predicate": {"args": [], "op": "ExactSynthetic", "value": True},
                }
                for adapter_id in sorted(record["adapters"])
            ],
            "assumptions": ["synthetic parser fixture"],
            "authority_status": VR.AUTHORITY_STATUS,
            "convention_hash": "2" * 64,
            "cse_temporaries": [
                {"expr": {"args": [], "op": "Exact", "value": {"kind": "integer", "value": 0}}, "id": "t000"}
            ],
            "dependency_dag": [
                {"dependencies": [], "id": "C"},
                {"dependencies": ["C"], "id": "selected"},
            ],
            "expressions": [
                {"expr": {"args": [], "op": "Ref", "value": "C"}, "id": "selected", "units": "1"}
            ],
            "formula_source_hashes": source_hashes,
            "historical_formula": {"is_dag_parent": False, "label_sha256": VR.HISTORICAL_FORMULA, "status": "UNRESOLVED_REFERENCE"},
            "orientation_hash": "3" * 64,
            "pass_receipts": [
                {"input_hash": spec_hash, "output_hash": receipt_hash, "pass_name": name, "pass_version": "synthetic"}
                for name in (
                    "exact_adapter_specialization", "exact_spec_validation",
                    "generic_frame_derivation", "typed_symir_v2_export",
                )
            ],
            "schema_version": "symir-v2-candidate-1",
            "selected_oracle": record["oracle"],
            "spec_hash": spec_hash,
            "spec_id": fixture_id,
            "tensors": [
                {"entries": [], "id": "C", "index_domains": ["spatial", "spatial", "spatial"], "shape": [3, 3, 3], "symmetries": ["antisymmetric(lower_1,lower_2)"], "variance": ["up", "down", "down"]}
            ],
        }
        data = VR.canonical_json_bytes(obj)
        name = f"{fixture_id}.symir-v2.json"
        (tmp_path / "cold" / name).write_bytes(data)
        (tmp_path / "warm" / name).write_bytes(data)
        digest = VR.sha256_bytes(data)
        entries.append({"cold_sha256": digest, "fixture_id": fixture_id, "result_path": f"cold/{name}", "warm_sha256": digest})
    aggregate = {
        "acceptance_checks": {
            "antisymmetry_failure_fail_closed": True,
            "canonical_output_deterministic": True,
            "closure_failure_fail_closed": True,
            "equivalent_representations_equal": True,
            "exceptional_adapter_exact": True,
            "jacobi_failure_fail_closed": True,
            "selected_oracle_emitted": True,
            "typeii_specialization_no_leak": True,
        },
        "aggregate_status": "VALIDATED_NEW_CANDIDATE",
        "authority_status": VR.AUTHORITY_STATUS,
        "cold_warm_equal": True,
        "fixtures": entries,
        "packet_manifest_sha256": VR.sha256_file(PACKET / "MANIFEST.sha256"),
        "schema_version": "workmode-result-v1",
        "wolfram_environment": {"kernel_version": "synthetic-not-executed", "system_id": "test", "xact_version": "synthetic"},
    }
    (tmp_path / "aggregate_result.json").write_bytes(VR.canonical_json_bytes(aggregate))
    result_paths = sorted(
        path.relative_to(tmp_path).as_posix()
        for path in tmp_path.rglob("*")
        if path.is_file() and path.name != "RESULT_MANIFEST.sha256"
    )
    (tmp_path / "RESULT_MANIFEST.sha256").write_text(
        "".join(f"{VR.sha256_file(tmp_path / relative)}  {relative}\n" for relative in result_paths),
        encoding="utf-8",
    )
    assert VR.verify_workmode_result(PACKET, tmp_path)["cold_warm_equal"] is True
    first = tmp_path / entries[0]["result_path"]
    first.write_bytes(first.read_bytes() + b" ")
    (tmp_path / "RESULT_MANIFEST.sha256").write_text(
        "".join(f"{VR.sha256_file(tmp_path / relative)}  {relative}\n" for relative in result_paths),
        encoding="utf-8",
    )
    with pytest.raises(VR.PacketError, match="cold/warm canonical bytes differ"):
        VR.verify_workmode_result(PACKET, tmp_path)
