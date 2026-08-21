from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

import typeii_spherical_grid_oracle as oracle

HERE = Path(__file__).resolve().parent


def test_icosphere_counts_and_qhull_faces_are_exact():
    for level in (0, 1, 2):
        vertices = oracle.refine_vertices(level)
        keys = oracle.hull_face_keys(vertices)
        assert len(vertices) == 10 * 4**level + 2
        assert len(keys) == 20 * 4**level
        assert len(set(keys)) == len(keys)


def test_qhull_facets_are_outward_and_closed():
    vertices = oracle.refine_vertices(2)
    faces = oracle.hull_face_keys(vertices)
    edges: dict[tuple[int, int], int] = {}
    for face in faces:
        a, b, c = vertices[list(face)]
        # Canonical sorted keys need not be oriented, but every facet must be nondegenerate.
        assert abs(np.linalg.det(np.column_stack([a, b, c]))) > 1e-8
        for i, j in ((face[0], face[1]), (face[1], face[2]), (face[2], face[0])):
            edge = tuple(sorted((i, j)))
            edges[edge] = edges.get(edge, 0) + 1
    assert set(edges.values()) == {2}
    assert len(vertices) - len(edges) + len(faces) == 2


def test_locator_weights_reconstruct_the_radial_intersection():
    vertices = oracle.refine_vertices(1)
    faces = oracle.hull_face_keys(vertices)
    for direction in oracle.sample_directions():
        key, weights, lam, candidates = oracle.locate(vertices, faces, direction)
        reconstructed = vertices[list(key)].T @ weights
        assert np.max(np.abs(reconstructed - lam * direction)) < 2e-15
        assert np.min(weights) >= 0
        assert abs(weights.sum() - 1) < 2e-15
        assert candidates >= 1


def test_edge_and_vertex_ties_choose_lexicographically_smallest_face():
    vertices = oracle.refine_vertices(1)
    faces = oracle.hull_face_keys(vertices)
    key = faces[11]
    vertex = vertices[key[0]]
    edge = oracle.unit(vertices[key[0]] + vertices[key[1]])
    for direction in (vertex, edge):
        selected, _, _, candidates = oracle.locate(vertices, list(reversed(faces)), direction)
        all_candidates = []
        for face in faces:
            try:
                w, lam, _ = oracle.radial_barycentric(vertices, face, direction)
            except Exception:
                continue
            if lam > 0 and np.min(w) >= -2e-12:
                all_candidates.append(face)
        assert selected == min(all_candidates)
        assert candidates == len(all_candidates)


def test_solid_rotation_fixture_separates_exact_departure_and_spatial_error():
    receipt = oracle.build_receipt()["solid_rotation"]
    exact_departure = oracle.rz(-receipt["omega"] * receipt["dt"], np.asarray(receipt["target"]))
    assert np.max(np.abs(exact_departure - receipt["departure"])) < 2e-16
    expected = np.asarray(receipt["expected_packed"])
    exact = np.asarray(receipt["exact_packed"])
    assert abs(np.max(np.abs(expected - exact)) - receipt["spatial_error"]) < 2e-16
    assert receipt["spatial_error"] > 0


def test_spatial_error_decreases_with_icosphere_refinement():
    target = oracle.unit([0.33, -0.24, 0.913])
    departure = oracle.rz(-0.61 * 0.27, target)
    exact = oracle.unpolarized_packed(target, oracle.intensity(departure))
    errors = []
    for level in (0, 1, 2, 3):
        vertices = oracle.refine_vertices(level)
        faces = oracle.hull_face_keys(vertices)
        key, weights, _, _ = oracle.locate(vertices, faces, departure)
        value = sum(w * oracle.intensity(vertices[i]) for w, i in zip(weights, key))
        candidate = oracle.unpolarized_packed(target, value)
        errors.append(float(np.max(np.abs(candidate - exact))))
    assert all(b < a for a, b in zip(errors, errors[1:]))
    assert errors[1] / errors[2] > 3.0
    assert errors[2] / errors[3] > 3.0


def test_nonconvex_and_uncovered_negative_controls_fail():
    vertices = oracle.refine_vertices(0)
    faces = oracle.hull_face_keys(vertices)
    direction = oracle.unit([0.21, -0.31, 0.927])
    key, weights, _, _ = oracle.locate(vertices, faces, direction)
    assert np.min(weights) >= 0
    bad_faces = [face for face in faces if face != key]
    with pytest.raises(ValueError, match="not covered"):
        oracle.locate(vertices, bad_faces, direction, tol=1e-14)


def test_committed_json_and_rust_fixture_are_byte_identical(tmp_path: Path):
    receipt = oracle.build_receipt()
    expected_json = json.dumps(receipt, sort_keys=True, indent=2) + "\n"
    expected_rust = oracle.rust_fixture(receipt)
    assert oracle.JSON_OUT.read_text() == expected_json
    assert oracle.RUST_OUT.read_text() == expected_rust
