#!/usr/bin/env python3
"""Static packet and Work-mode result verifier.

This module intentionally does not invoke Wolfram.  Its exact Python/SymPy
implementation is an independent selected-component oracle for the candidate
packet, not a production formula authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any, Iterable

import sympy as sp


AUTHORITY_STATUS = "CANDIDATE_UNPROMOTED_FORMULA_BYTES_ABSENT"
HISTORICAL_FORMULA = "3ecf0dbc8b47a8af83da81e9ed37823b6922e139e420c5bfa2e071b6bbabe361"
BASE_COMMIT = "f575e5c3b12701944f4745ef90f3bbcfe53facd6"
BASE_TREE = "1cbd9b6264ee3cf17019b81bbf0b3a180b70aea3"
SHA_RE = re.compile(r"^[0-9a-f]{64}$")


class PacketError(ValueError):
    """Fail-closed packet or result validation error."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise PacketError(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def reject_inexact_numbers(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise PacketError(f"inexact JSON float in authority data at {path}")
    if isinstance(value, dict):
        for key, child in value.items():
            reject_inexact_numbers(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_inexact_numbers(child, f"{path}[{index}]")


def decode_exact(value: dict[str, Any]) -> sp.Expr:
    if not isinstance(value, dict):
        raise PacketError("exact scalar must be a typed object")
    kind = value.get("kind")
    if kind == "integer" and set(value) == {"kind", "value"}:
        raw = value["value"]
        if isinstance(raw, bool) or not isinstance(raw, int):
            raise PacketError("integer exact scalar requires a JSON integer")
        return sp.Integer(raw)
    if kind == "rational" and set(value) == {"kind", "numerator", "denominator"}:
        num, den = value["numerator"], value["denominator"]
        if any(isinstance(v, bool) or not isinstance(v, int) for v in (num, den)):
            raise PacketError("rational numerator/denominator must be integers")
        if den <= 1 or math.gcd(num, den) != 1:
            raise PacketError("rational must be reduced with denominator > 1")
        return sp.Rational(num, den)
    if kind == "algebraic" and set(value) == {
        "kind", "minimal_polynomial", "isolating_interval", "root_index"
    }:
        coeffs = value["minimal_polynomial"]
        if (
            not isinstance(coeffs, list)
            or len(coeffs) < 2
            or any(isinstance(v, bool) or not isinstance(v, int) for v in coeffs)
            or coeffs[0] == 0
        ):
            raise PacketError("invalid primitive minimal polynomial")
        if math.gcd(*[abs(v) for v in coeffs]) != 1:
            raise PacketError("minimal polynomial must be primitive")
        interval = value["isolating_interval"]
        if not isinstance(interval, list) or len(interval) != 2:
            raise PacketError("algebraic scalar needs an exact isolating interval")
        lo, hi = (decode_exact(v) for v in interval)
        if not (lo.is_Rational and hi.is_Rational and lo < hi):
            raise PacketError("isolating interval must be increasing and rational")
        index = value["root_index"]
        roots = sp.Poly.from_list(coeffs, gens=sp.Symbol("x")).real_roots()
        if not isinstance(index, int) or index < 0 or index >= len(roots):
            raise PacketError("root selector does not identify an isolated real root")
        root = roots[index]
        if not bool(lo < root < hi) or sum(bool(lo < candidate < hi) for candidate in roots) != 1:
            raise PacketError("isolating interval does not contain exactly the selected real root")
        return root
    raise PacketError(f"unsupported or noncanonical exact scalar: {value!r}")


def encode_exact(value: sp.Expr) -> dict[str, Any]:
    value = sp.cancel(value)
    if value.is_Integer:
        return {"kind": "integer", "value": int(value)}
    if value.is_Rational:
        return {
            "denominator": int(value.q),
            "kind": "rational",
            "numerator": int(value.p),
        }
    if value.is_algebraic and value.is_real:
        symbol = sp.Symbol("x")
        polynomial = sp.Poly(sp.minimal_polynomial(value, symbol), symbol, domain=sp.ZZ)
        coeffs = [int(v) for v in polynomial.all_coeffs()]
        if coeffs[0] < 0:
            coeffs = [-v for v in coeffs]
            polynomial = -polynomial
        roots = polynomial.real_roots()
        matches = [index for index, root in enumerate(roots) if sp.simplify(root - value) == 0]
        if len(matches) != 1:
            raise PacketError(f"algebraic root is not uniquely selectable: {value}")
        index = matches[0]
        intervals = polynomial.intervals(eps=sp.Rational(1, 10**12))
        if len(intervals) != len(roots):
            raise PacketError(f"could not build a unique rational isolating interval: {value}")
        (lo, hi), multiplicity = intervals[index]
        if multiplicity != 1 or lo == hi:
            raise PacketError(f"non-simple or rational algebraic root: {value}")
        return {
            "isolating_interval": [encode_exact(sp.Rational(lo)), encode_exact(sp.Rational(hi))],
            "kind": "algebraic",
            "minimal_polynomial": coeffs,
            "root_index": index,
        }
    raise PacketError(f"derived exact scalar is not canonically serializable: {value}")


def tensor_from_sparse(obj: dict[str, Any], shape: tuple[int, ...]) -> sp.MutableDenseNDimArray:
    if not isinstance(obj, dict) or set(obj) != {"shape", "entries"}:
        raise PacketError("sparse tensor must contain only shape and entries")
    if obj["shape"] != list(shape):
        raise PacketError(f"expected tensor shape {list(shape)}, got {obj['shape']!r}")
    tensor = sp.MutableDenseNDimArray.zeros(*shape)
    previous: tuple[int, ...] | None = None
    for entry in obj["entries"]:
        if not isinstance(entry, dict) or set(entry) != {"indices", "value"}:
            raise PacketError("malformed sparse entry")
        indices = tuple(entry["indices"])
        if len(indices) != len(shape) or any(
            isinstance(i, bool) or not isinstance(i, int) or i < 0 or i >= shape[k]
            for k, i in enumerate(indices)
        ):
            raise PacketError(f"out-of-range sparse index: {indices}")
        if previous is not None and indices <= previous:
            raise PacketError("sparse entries must be unique and lexically sorted")
        previous = indices
        exact = decode_exact(entry["value"])
        if exact == 0:
            raise PacketError("zero sparse entries are noncanonical")
        tensor[indices] = exact
    return tensor


def sparse_from_tensor(tensor: sp.NDimArray) -> dict[str, Any]:
    shape = tuple(int(v) for v in tensor.shape)
    entries = []
    for indices in _index_product(shape):
        value = sp.cancel(tensor[indices])
        if value != 0:
            entries.append({"indices": list(indices), "value": encode_exact(value)})
    return {"entries": entries, "shape": list(shape)}


def _index_product(shape: tuple[int, ...]) -> Iterable[tuple[int, ...]]:
    if not shape:
        yield ()
        return
    import itertools

    yield from itertools.product(*(range(n) for n in shape))


def epsilon(i: int, j: int, k: int) -> sp.Integer:
    return sp.LeviCivita(i, j, k)


def derive_c_from_na(n: sp.NDimArray, a: sp.NDimArray) -> sp.MutableDenseNDimArray:
    c = sp.MutableDenseNDimArray.zeros(3, 3, 3)
    for upper, lower_b, lower_c in _index_product((3, 3, 3)):
        c[upper, lower_b, lower_c] = sp.expand(
            sum(epsilon(lower_b, lower_c, d) * n[d, upper] for d in range(3))
            + a[lower_b] * int(upper == lower_c)
            - a[lower_c] * int(upper == lower_b)
        )
    return c


def derive_na_from_c(c: sp.NDimArray) -> tuple[sp.MutableDenseNDimArray, sp.MutableDenseNDimArray]:
    a = sp.MutableDenseNDimArray.zeros(3)
    for i in range(3):
        a[i] = sp.Rational(1, 2) * sum(c[j, i, j] for j in range(3))
    n = sp.MutableDenseNDimArray.zeros(3, 3)
    for d, upper in _index_product((3, 3)):
        n[d, upper] = sp.Rational(1, 2) * sum(
            epsilon(d, i, j)
            * (
                c[upper, i, j]
                - a[i] * int(upper == j)
                + a[j] * int(upper == i)
            )
            for i in range(3)
            for j in range(3)
        )
    return n, a


def generators_from_c(c: sp.NDimArray) -> list[sp.Matrix]:
    return [sp.Matrix(3, 3, lambda upper, col: c[upper, b, col]) for b in range(3)]


def _tensor_equal(left: sp.NDimArray, right: sp.NDimArray) -> bool:
    return left.shape == right.shape and all(
        sp.expand(left[i] - right[i]) == 0 for i in _index_product(tuple(left.shape))
    )


def _check_antisymmetry(c: sp.NDimArray) -> None:
    for upper, b, d in _index_product((3, 3, 3)):
        if sp.expand(c[upper, b, d] + c[upper, d, b]) != 0:
            raise PacketError("structure constants violate lower-slot antisymmetry")


def _check_jacobi(c: sp.NDimArray) -> None:
    for upper, b, d, e in _index_product((3, 3, 3, 3)):
        residual = sum(
            c[m, d, e] * c[upper, b, m]
            + c[m, e, b] * c[upper, d, m]
            + c[m, b, d] * c[upper, e, m]
            for m in range(3)
        )
        if sp.expand(residual) != 0:
            raise PacketError("structure constants violate the exact Jacobi identity")


def _check_na(n: sp.NDimArray, a: sp.NDimArray) -> None:
    for i, j in _index_product((3, 3)):
        if sp.expand(n[i, j] - n[j, i]) != 0:
            raise PacketError("n decomposition is not symmetric")
    for i in range(3):
        if sp.expand(sum(n[i, j] * a[j] for j in range(3))) != 0:
            raise PacketError("n.a constraint is nonzero")


def _check_generator_closure(generators: list[sp.Matrix], c: sp.NDimArray) -> None:
    if len(generators) != 3 or len({matrix.shape for matrix in generators}) != 1:
        raise PacketError("matrix generator dimensions are inconsistent")
    dimension = generators[0].rows
    if any(matrix.cols != dimension for matrix in generators):
        raise PacketError("matrix generators must be square")
    for b, d in _index_product((3, 3)):
        lhs = generators[b] * generators[d] - generators[d] * generators[b]
        rhs = sum((c[m, b, d] * generators[m] for m in range(3)), sp.zeros(dimension, dimension))
        if any(sp.expand(v) != 0 for v in (lhs - rhs)):
            raise PacketError("matrix generators violate exact commutator closure")


def _recover_c_from_faithful_generators(generators: list[sp.Matrix]) -> sp.MutableDenseNDimArray:
    columns = sp.Matrix.hstack(*(matrix.reshape(matrix.rows * matrix.cols, 1) for matrix in generators))
    if columns.rank() != 3:
        raise PacketError("AMBIGUOUS_GENERATOR_REPRESENTATION")
    c = sp.MutableDenseNDimArray.zeros(3, 3, 3)
    gram_inverse = (columns.T * columns).inv()
    left_inverse = gram_inverse * columns.T
    for b, d in _index_product((3, 3)):
        commutator = generators[b] * generators[d] - generators[d] * generators[b]
        target = commutator.reshape(commutator.rows * commutator.cols, 1)
        coefficients = left_inverse * target
        if columns * coefficients != target:
            raise PacketError("matrix generators are not exactly closed in their span")
        for upper in range(3):
            c[upper, b, d] = sp.expand(coefficients[upper])
    return c


def validate_spec(spec: dict[str, Any]) -> dict[str, Any]:
    reject_inexact_numbers(spec)
    required = {
        "schema_version", "spec_id", "basis_dimension", "basis_id",
        "convention", "convention_hash"
    }
    if not required.issubset(spec):
        raise PacketError(f"missing BianchiSpec fields: {sorted(required - set(spec))}")
    if spec["schema_version"] != "bianchi-spec-v1" or spec["basis_dimension"] != 3:
        raise PacketError("unsupported BianchiSpec schema or dimension")
    expected_convention = sha256_bytes(canonical_json_bytes(spec["convention"]))
    if spec["convention_hash"] != expected_convention:
        raise PacketError("convention hash mismatch")
    if spec["convention"].get("commutator") != "[e_b,e_c]=C^a_bc e_a":
        raise PacketError("unsupported commutator convention")

    supplied_c = (
        tensor_from_sparse(spec["structure_constants"], (3, 3, 3))
        if "structure_constants" in spec else None
    )
    supplied_na = None
    if "na_decomposition" in spec:
        n = tensor_from_sparse(spec["na_decomposition"]["n"], (3, 3))
        a = tensor_from_sparse(spec["na_decomposition"]["a"], (3,))
        _check_na(n, a)
        supplied_na = (n, a)
        derived_c = derive_c_from_na(n, a)
        if supplied_c is not None and not _tensor_equal(supplied_c, derived_c):
            raise PacketError("C and (n,a) representations disagree")
        supplied_c = derived_c

    supplied_generators = None
    if "matrix_generators" in spec:
        generator_shape = spec["matrix_generators"].get("shape")
        if (
            not isinstance(generator_shape, list)
            or len(generator_shape) != 3
            or generator_shape[0] != 3
            or generator_shape[1] != generator_shape[2]
            or not isinstance(generator_shape[1], int)
            or generator_shape[1] < 1
        ):
            raise PacketError("invalid matrix-generator tensor shape")
        matrix_dimension = generator_shape[1]
        g_tensor = tensor_from_sparse(spec["matrix_generators"], tuple(generator_shape))
        supplied_generators = [
            sp.Matrix(matrix_dimension, matrix_dimension, lambda i, j: g_tensor[b, i, j])
            for b in range(3)
        ]
        representation = spec.get("generator_representation")
        if representation == "adjoint":
            if matrix_dimension != 3:
                raise PacketError("adjoint generators must have shape [3,3,3]")
            generator_c = sp.MutableDenseNDimArray.zeros(3, 3, 3)
            for b, upper, col in _index_product((3, 3, 3)):
                generator_c[upper, b, col] = g_tensor[b, upper, col]
        elif representation == "faithful_embedding":
            certificate = spec.get("representation_certificate")
            if not isinstance(certificate, dict) or certificate.get("faithful") is not True or certificate.get("uniquely_recoverable") is not True:
                raise PacketError("AMBIGUOUS_GENERATOR_REPRESENTATION")
            generator_c = _recover_c_from_faithful_generators(supplied_generators)
            expected_binding = sha256_bytes(canonical_json_bytes(sparse_from_tensor(generator_c)))
            if certificate.get("structure_constants_sha256") != expected_binding:
                raise PacketError("faithful generator certificate hash mismatch")
        else:
            raise PacketError("AMBIGUOUS_GENERATOR_REPRESENTATION")
        if supplied_c is not None and not _tensor_equal(supplied_c, generator_c):
            raise PacketError("matrix generators disagree with C")
        supplied_c = generator_c

    if supplied_c is None:
        raise PacketError("AMBIGUOUS_GENERATOR_REPRESENTATION")
    _check_antisymmetry(supplied_c)
    _check_jacobi(supplied_c)
    derived_n, derived_a = derive_na_from_c(supplied_c)
    _check_na(derived_n, derived_a)
    if supplied_na is not None and (
        not _tensor_equal(supplied_na[0], derived_n)
        or not _tensor_equal(supplied_na[1], derived_a)
    ):
        raise PacketError("C -> (n,a) round trip failed")
    generators = generators_from_c(supplied_c)
    if supplied_generators is not None:
        if spec.get("generator_representation") == "adjoint" and any(
            left != right for left, right in zip(supplied_generators, generators, strict=True)
        ):
            raise PacketError("C -> generator round trip failed")
        _check_generator_closure(supplied_generators, supplied_c)
    _check_generator_closure(generators, supplied_c)

    canonical_embedding = None
    if "invariant_embedding" in spec:
        embedding = spec["invariant_embedding"]
        if not isinstance(embedding, dict) or set(embedding) != {
            "frame_matrix", "coframe_matrix", "maurer_cartan_coefficients"
        }:
            raise PacketError("invalid invariant embedding fields")
        frame = tensor_from_sparse(embedding["frame_matrix"], (3, 3))
        coframe = tensor_from_sparse(embedding["coframe_matrix"], (3, 3))
        mc = tensor_from_sparse(embedding["maurer_cartan_coefficients"], (3, 3, 3))
        frame_matrix = sp.Matrix(3, 3, lambda i, j: frame[i, j])
        coframe_matrix = sp.Matrix(3, 3, lambda i, j: coframe[i, j])
        if frame_matrix * coframe_matrix != sp.eye(3) or coframe_matrix * frame_matrix != sp.eye(3):
            raise PacketError("frame/coframe embedding is not an exact inverse pair")
        expected_mc = sp.MutableDenseNDimArray.zeros(3, 3, 3)
        for upper, b, d in _index_product((3, 3, 3)):
            expected_mc[upper, b, d] = -sp.Rational(1, 2) * supplied_c[upper, b, d]
        if not _tensor_equal(mc, expected_mc):
            raise PacketError("invariant coframe fails exact Maurer-Cartan equation")
        canonical_embedding = {
            "coframe_matrix": sparse_from_tensor(coframe),
            "frame_matrix": sparse_from_tensor(frame),
            "maurer_cartan_coefficients": sparse_from_tensor(mc),
        }

    canonical = {
        "adapter_requests": spec.get("adapter_requests", {}),
        "basis_dimension": 3,
        "basis_id": spec["basis_id"],
        "convention": spec["convention"],
        "convention_hash": spec["convention_hash"],
        "matrix_generators": sparse_from_tensor(
            sp.MutableDenseNDimArray(
                [v for matrix in generators for v in matrix], (3, 3, 3)
            )
        ),
        "metadata": spec.get("metadata", {}),
        "na_decomposition": {
            "a": sparse_from_tensor(derived_a),
            "n": sparse_from_tensor(derived_n),
        },
        "schema_version": "bianchi-spec-v1",
        "spec_id": spec["spec_id"],
        "structure_constants": sparse_from_tensor(supplied_c),
    }
    if canonical_embedding is not None:
        canonical["invariant_embedding"] = canonical_embedding
    return canonical


def transform_na_orientation(
    n: sp.NDimArray, a: sp.NDimArray, frame_change: sp.Matrix
) -> tuple[sp.MutableDenseNDimArray, sp.MutableDenseNDimArray]:
    """Exact n pseudotensor / a vector transformation under an orthogonal frame."""
    if frame_change.shape != (3, 3) or frame_change.T * frame_change != sp.eye(3):
        raise PacketError("frame change must be exactly orthogonal")
    nm = sp.Matrix(3, 3, lambda i, j: n[i, j])
    av = sp.Matrix(3, 1, lambda i, _: a[i])
    transformed_n = sp.det(frame_change) * frame_change * nm * frame_change.T
    transformed_a = frame_change * av
    return (
        sp.MutableDenseNDimArray(list(transformed_n), (3, 3)),
        sp.MutableDenseNDimArray(list(transformed_a), (3,)),
    )


def codazzi_map(n: sp.NDimArray, a: sp.NDimArray) -> sp.Matrix:
    x11, x22, x12, x13, x23 = sp.symbols("x11 x22 x12 x13 x23")
    variables = [x11, x22, x12, x13, x23]
    shear = sp.Matrix([[x11, x12, x13], [x12, x22, x23], [x13, x23, -x11 - x22]])
    rows = []
    for upper in range(3):
        expression = 3 * sum(a[b] * shear[upper, b] for b in range(3))
        expression += sum(
            epsilon(upper, b, c) * n[b, d] * shear[c, d]
            for b, c, d in _index_product((3, 3, 3))
        )
        rows.append([sp.expand(expression).coeff(v) for v in variables])
    return sp.Matrix(rows)


def adapter_ids(canonical_spec: dict[str, Any]) -> list[str]:
    n = tensor_from_sparse(canonical_spec["na_decomposition"]["n"], (3, 3))
    a = tensor_from_sparse(canonical_spec["na_decomposition"]["a"], (3,))
    n_matrix = sp.Matrix(3, 3, lambda i, j: n[i, j])
    a_zero = all(a[i] == 0 for i in range(3))
    adapters = ["class_A" if a_zero else "class_B"]
    requests = canonical_spec.get("adapter_requests", {})
    if requests.get("D_normalization", False):
        principal = [n_matrix[:k, :k].det() for k in (1, 2, 3)]
        if n_matrix.rank() != 3 or not all(bool(v > 0) for v in principal):
            raise PacketError("D-normalization request failed exact rank/definiteness precondition")
        adapters.append("positive_definite_D_normalization")
    if not a_zero and codazzi_map(n, a).rank() < 3:
        adapters.append("exceptional_codazzi_rank_loss")
    if requests.get("rank_one_axis_projector", False):
        if a_zero and n_matrix.rank() == 1:
            adapters.append("rank_one_axis_projector")
    return adapters


def selected_oracle(canonical_spec: dict[str, Any]) -> dict[str, Any]:
    n = tensor_from_sparse(canonical_spec["na_decomposition"]["n"], (3, 3))
    a = tensor_from_sparse(canonical_spec["na_decomposition"]["a"], (3,))
    nm = sp.Matrix(3, 3, lambda i, j: n[i, j])
    av = sp.Matrix(3, 1, lambda i, _: a[i])
    scalar = sp.expand(-sp.trace(nm * nm) + sp.Rational(1, 2) * sp.trace(nm) ** 2 - 6 * (av.T * av)[0])
    return {"spatial_scalar_curvature": encode_exact(scalar)}


def validate_packet_root(root: Path, *, verify_manifest_file: bool = True) -> dict[str, Any]:
    source = load_json(root / "SOURCE_REF.json")
    authority = load_json(root / "AUTHORITY_STATUS.json")
    if source.get("base_commit") != BASE_COMMIT or source.get("base_tree") != BASE_TREE:
        raise PacketError("packet source identity drift")
    if authority.get("candidate_status") != AUTHORITY_STATUS:
        raise PacketError("candidate authority label drift")
    historical = authority.get("historical_formula", {})
    if historical != {
        "is_dag_parent": False,
        "label_sha256": HISTORICAL_FORMULA,
        "source_bytes": "ABSENT",
        "status": "UNRESOLVED_REFERENCE",
    }:
        raise PacketError("historical formula boundary drift")
    fixtures = {}
    for path in sorted((root / "fixtures").glob("*.json"), key=lambda p: p.name):
        spec = load_json(path)
        canonical = validate_spec(spec)
        fixtures[canonical["spec_id"]] = {
            "adapters": adapter_ids(canonical),
            "canonical_sha256": sha256_bytes(canonical_json_bytes(canonical)),
            "oracle": selected_oracle(canonical),
        }
    if len(fixtures) < 8:
        raise PacketError("focused fixture coverage is incomplete")
    registry = load_json(root / "FIXTURE_REGISTRY.json")
    expected_registry = {
        "fixtures": [
            {"spec_id": fixture_id, **record}
            for fixture_id, record in sorted(fixtures.items())
        ],
        "registry_version": "generic-bianchi-fixtures-v1",
    }
    if registry != expected_registry:
        raise PacketError("fixture registry is stale or does not match exact canonicalization")
    if "rank_one_axis_projector" not in fixtures["II_equivalent"]["adapters"]:
        raise PacketError("rank-one exact adapter did not activate for II fixture")
    for fixture_id in ("VI_0", "VII_0", "VIII"):
        if "rank_one_axis_projector" in fixtures[fixture_id]["adapters"]:
            raise PacketError("Type-II rank-one adapter leaked outside its exact predicate")
    if "exceptional_codazzi_rank_loss" not in fixtures["VIstar_minus_1_9"]["adapters"]:
        raise PacketError("exceptional exact-rank adapter did not activate")
    if verify_manifest_file:
        verify_manifest(root)
    return fixtures


def _manifest_paths(root: Path) -> list[str]:
    return sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
        and path.name != "MANIFEST.sha256"
        and "__pycache__" not in path.parts
    )


def verify_manifest(root: Path) -> None:
    manifest = root / "MANIFEST.sha256"
    if not manifest.is_file():
        raise PacketError("MANIFEST.sha256 is absent")
    lines = manifest.read_text(encoding="utf-8").splitlines()
    parsed = []
    for line in lines:
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_./-]+)", line)
        if match is None:
            raise PacketError(f"malformed manifest line: {line!r}")
        parsed.append((match.group(2), match.group(1)))
    paths = [path for path, _ in parsed]
    if paths != sorted(paths) or len(paths) != len(set(paths)):
        raise PacketError("manifest paths are not unique lexical order")
    if paths != _manifest_paths(root):
        raise PacketError("manifest coverage does not match packet regular files")
    for relative, expected in parsed:
        if sha256_file(root / relative) != expected:
            raise PacketError(f"manifest hash mismatch: {relative}")


def validate_symir_v2(
    root: Path, fixture_id: str, symir: dict[str, Any], expected: dict[str, Any]
) -> None:
    required = {
        "schema_version", "authority_status", "historical_formula", "spec_id",
        "spec_hash", "convention_hash", "orientation_hash", "formula_source_hashes",
        "assumptions", "tensors", "expressions", "dependency_dag",
        "cse_temporaries", "adapters", "pass_receipts", "selected_oracle",
    }
    if set(symir) != required:
        raise PacketError(f"SymIR v2 fields do not match schema: {fixture_id}")
    reject_inexact_numbers(symir)
    if symir["schema_version"] != "symir-v2-candidate-1" or symir["authority_status"] != AUTHORITY_STATUS:
        raise PacketError(f"SymIR v2 schema or authority drift: {fixture_id}")
    if symir["historical_formula"] != {
        "is_dag_parent": False,
        "label_sha256": HISTORICAL_FORMULA,
        "status": "UNRESOLVED_REFERENCE",
    }:
        raise PacketError(f"fabricated historical formula edge: {fixture_id}")
    if symir["spec_id"] != fixture_id or symir["spec_hash"] != expected["canonical_sha256"]:
        raise PacketError(f"SymIR v2 spec binding mismatch: {fixture_id}")
    if not SHA_RE.fullmatch(symir["convention_hash"]) or not SHA_RE.fullmatch(symir["orientation_hash"]):
        raise PacketError(f"invalid convention/orientation digest: {fixture_id}")
    source_names = {
        "BianchiSpec.wl", "GenericFrameDerivation.wl", "GenericAdapters.wl",
        "SymIRV2Export.wl",
    }
    if set(symir["formula_source_hashes"]) != source_names:
        raise PacketError(f"incomplete formula source provenance: {fixture_id}")
    for name in source_names:
        if symir["formula_source_hashes"][name] != sha256_file(root / name):
            raise PacketError(f"formula source digest mismatch for {name}: {fixture_id}")
    if symir["selected_oracle"] != expected["oracle"]:
        raise PacketError(f"independent selected-component parity failed: {fixture_id}")

    adapter_ids_observed = [entry.get("adapter_id") for entry in symir["adapters"]]
    if adapter_ids_observed != sorted(expected["adapters"]):
        raise PacketError(f"exact adapter receipt mismatch: {fixture_id}")
    for entry in symir["adapters"]:
        if set(entry) != {"adapter_id", "predicate", "input_hash", "output_assumptions"}:
            raise PacketError(f"malformed adapter receipt: {fixture_id}")
        if entry["input_hash"] != symir["spec_hash"]:
            raise PacketError(f"adapter input is not bound to spec: {fixture_id}")

    tensor_ids = [entry.get("id") for entry in symir["tensors"]]
    expression_ids = [entry.get("id") for entry in symir["expressions"]]
    cse_ids = [entry.get("id") for entry in symir["cse_temporaries"]]
    if tensor_ids != sorted(tensor_ids) or len(tensor_ids) != len(set(tensor_ids)):
        raise PacketError(f"noncanonical tensor IDs: {fixture_id}")
    if expression_ids != sorted(expression_ids) or len(expression_ids) != len(set(expression_ids)):
        raise PacketError(f"noncanonical expression IDs: {fixture_id}")
    if cse_ids != sorted(cse_ids) or len(cse_ids) != len(set(cse_ids)):
        raise PacketError(f"noncanonical CSE IDs: {fixture_id}")
    if symir["assumptions"] != sorted(set(symir["assumptions"])):
        raise PacketError(f"assumptions are not canonical: {fixture_id}")

    seen: set[str] = set()
    for node in symir["dependency_dag"]:
        if set(node) != {"id", "dependencies"} or node["id"] in seen:
            raise PacketError(f"malformed or duplicate dependency node: {fixture_id}")
        if any(dep not in seen for dep in node["dependencies"]):
            raise PacketError(f"dependency DAG is not topologically ordered: {fixture_id}")
        seen.add(node["id"])
    if not set(tensor_ids + expression_ids).issubset(seen):
        raise PacketError(f"dependency DAG omits an emitted tensor/expression: {fixture_id}")
    receipts = symir["pass_receipts"]
    names = [entry.get("pass_name") for entry in receipts]
    if names != sorted(names) or set(names) != {
        "exact_adapter_specialization", "exact_spec_validation",
        "generic_frame_derivation", "typed_symir_v2_export",
    }:
        raise PacketError(f"pass receipt coverage/order mismatch: {fixture_id}")
    for receipt in receipts:
        if set(receipt) != {"pass_name", "pass_version", "input_hash", "output_hash"}:
            raise PacketError(f"malformed pass receipt: {fixture_id}")
        if not SHA_RE.fullmatch(receipt["input_hash"]) or not SHA_RE.fullmatch(receipt["output_hash"]):
            raise PacketError(f"invalid pass receipt digest: {fixture_id}")


def verify_result_manifest(result_dir: Path) -> None:
    manifest = result_dir / "RESULT_MANIFEST.sha256"
    if not manifest.is_file():
        raise PacketError("RESULT_MANIFEST.sha256 is absent")
    records: list[tuple[str, str]] = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_./-]+)", line)
        if match is None:
            raise PacketError(f"malformed result manifest line: {line!r}")
        records.append((match.group(2), match.group(1)))
    paths = [relative for relative, _ in records]
    actual = sorted(
        path.relative_to(result_dir).as_posix()
        for path in result_dir.rglob("*")
        if path.is_file() and path.name != "RESULT_MANIFEST.sha256"
    )
    if paths != sorted(paths) or len(paths) != len(set(paths)) or paths != actual:
        raise PacketError("result manifest order/coverage mismatch")
    for relative, expected in records:
        if sha256_file(result_dir / relative) != expected:
            raise PacketError(f"result manifest hash mismatch: {relative}")


def verify_workmode_result(root: Path, result_dir: Path) -> dict[str, Any]:
    fixtures = validate_packet_root(root)
    verify_result_manifest(result_dir)
    aggregate_path = result_dir / "aggregate_result.json"
    aggregate = load_json(aggregate_path)
    required = {
        "schema_version", "aggregate_status", "authority_status",
        "packet_manifest_sha256", "cold_warm_equal", "wolfram_environment", "fixtures",
        "acceptance_checks"
    }
    if set(aggregate) != required:
        raise PacketError("aggregate result fields do not match RESULT_SCHEMA")
    if aggregate["schema_version"] != "workmode-result-v1":
        raise PacketError("unsupported Work-mode result schema")
    if aggregate["aggregate_status"] != "VALIDATED_NEW_CANDIDATE":
        raise PacketError("Work-mode aggregate did not validate the new candidate")
    if aggregate["authority_status"] != AUTHORITY_STATUS or aggregate["cold_warm_equal"] is not True:
        raise PacketError("authority or cold/warm result boundary failed")
    if not aggregate["acceptance_checks"] or not all(aggregate["acceptance_checks"].values()):
        raise PacketError("one or more focused Work-mode acceptance checks failed")
    if aggregate["packet_manifest_sha256"] != sha256_file(root / "MANIFEST.sha256"):
        raise PacketError("aggregate is not bound to this packet manifest")
    seen = set()
    for entry in aggregate["fixtures"]:
        fixture_id = entry["fixture_id"]
        if fixture_id not in fixtures or fixture_id in seen:
            raise PacketError(f"unknown or duplicate result fixture: {fixture_id}")
        seen.add(fixture_id)
        cold = result_dir / entry["result_path"]
        warm = result_dir / "warm" / cold.name
        cold_bytes, warm_bytes = cold.read_bytes(), warm.read_bytes()
        if cold_bytes != warm_bytes:
            raise PacketError(f"cold/warm canonical bytes differ: {fixture_id}")
        digest = sha256_bytes(cold_bytes)
        if digest != entry["cold_sha256"] or digest != entry["warm_sha256"]:
            raise PacketError(f"cold/warm digest mismatch: {fixture_id}")
        symir = json.loads(cold_bytes, object_pairs_hook=_unique_object)
        if cold_bytes != canonical_json_bytes(symir):
            raise PacketError(f"result is not canonical UTF-8 JSON with one LF: {fixture_id}")
        validate_symir_v2(root, fixture_id, symir, fixtures[fixture_id])
    if seen != set(fixtures):
        raise PacketError("Work-mode result omitted focused fixtures")
    return aggregate


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet-root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--result-dir", type=Path)
    parser.add_argument("--self-check", action="store_true")
    return parser


def main() -> int:
    args = _parser().parse_args()
    root = args.packet_root.resolve()
    if args.self_check:
        fixtures = validate_packet_root(root)
        print(json.dumps({"fixture_count": len(fixtures), "status": "STATIC_PACKET_PASS"}, sort_keys=True))
        return 0
    if args.result_dir is None:
        raise SystemExit("--result-dir is required unless --self-check is used")
    aggregate = verify_workmode_result(root, args.result_dir.resolve())
    print(json.dumps({"fixture_count": len(aggregate["fixtures"]), "status": aggregate["aggregate_status"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
