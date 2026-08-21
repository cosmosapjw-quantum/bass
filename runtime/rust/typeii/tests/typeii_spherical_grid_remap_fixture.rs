use bianchi_rustcore::generated::typeii_polarized_liouville::HomogeneousRayBackground;
use bianchi_rustcore::generated::typeii_polarized_remap::RemapOptions;
use bianchi_rustcore::generated::typeii_spherical_grid_remap::{
    semi_lagrangian_step, GridOptions, SemiLagrangianOptions, SphericalTriMesh,
};

mod fixture {
    include!("support/typeii_spherical_grid_fixture.rs");
}

fn projector(e: [f64; 3]) -> [[f64; 3]; 3] {
    let mut p = [[0.0; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            p[i][j] = if i == j { 1.0 } else { 0.0 } - e[i] * e[j];
        }
    }
    p
}

fn pack(m: &[[f64; 3]; 3]) -> [f64; 9] {
    [
        m[0][0],
        m[1][1],
        m[2][2],
        0.5 * (m[0][1] + m[1][0]),
        0.5 * (m[0][2] + m[2][0]),
        0.5 * (m[1][2] + m[2][1]),
        0.5 * (m[1][2] - m[2][1]),
        0.5 * (m[2][0] - m[0][2]),
        0.5 * (m[0][1] - m[1][0]),
    ]
}

fn intensity(e: [f64; 3]) -> f64 {
    1.2 + 0.25 * e[0] - 0.17 * e[1] + 0.11 * e[2]
}

fn unpolarized(e: [f64; 3], value: f64) -> [f64; 9] {
    let p = projector(e);
    let mut m = [[0.0; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            m[i][j] = 0.5 * value * p[i][j];
        }
    }
    pack(&m)
}

fn max_abs3(a: [f64; 3], b: [f64; 3]) -> f64 {
    a.iter()
        .zip(b)
        .map(|(x, y)| (x - y).abs())
        .fold(0.0, f64::max)
}

fn max_abs9(a: &[f64; 9], b: &[f64; 9]) -> f64 {
    a.iter()
        .zip(b)
        .map(|(x, y)| (x - y).abs())
        .fold(0.0, f64::max)
}

fn sorted_key(mut face: [usize; 3]) -> [usize; 3] {
    face.sort_unstable();
    face
}

#[test]
fn independently_reconstructed_qhull_face_set_matches_level1_runtime_mesh() {
    let mesh = SphericalTriMesh::icosphere(1, GridOptions::default()).unwrap();
    let mut keys: Vec<[usize; 3]> = mesh.faces().iter().copied().map(sorted_key).collect();
    keys.sort_unstable();
    assert_eq!(keys.as_slice(), &fixture::LEVEL1_FACE_KEYS);
}

#[test]
fn independent_qhull_locator_cases_match_runtime_face_and_weights() {
    let mesh = SphericalTriMesh::icosphere(1, GridOptions::default()).unwrap();
    for case in &fixture::LOCATOR_CASES {
        let stencil = mesh.locate(case.direction).unwrap();
        assert_eq!(stencil.face_key, case.face_key);
        assert_eq!(stencil.candidate_faces, case.candidate_faces);
        assert!((stencil.radial_scale - case.radial_scale).abs() < 2.0e-14);

        // Reorder runtime weights from oriented face order into the sorted Qhull key.
        let mut by_key = [0.0; 3];
        for (index, weight) in stencil.vertex_indices.into_iter().zip(stencil.weights) {
            let slot = case
                .face_key
                .iter()
                .position(|candidate| *candidate == index)
                .unwrap();
            by_key[slot] = weight;
        }
        assert!(
            max_abs3(by_key, case.weights) < 3.0e-14,
            "runtime={by_key:?}, oracle={:?}",
            case.weights
        );
    }
}

#[test]
fn solid_rotation_semi_lagrangian_witness_matches_independent_scipy_fixture() {
    let mesh = SphericalTriMesh::icosphere(2, GridOptions::default()).unwrap();
    let states: Vec<[f64; 9]> = mesh
        .vertices()
        .iter()
        .copied()
        .map(|e| unpolarized(e, intensity(e)))
        .collect();
    let background = HomogeneousRayBackground {
        triad_rotation: [0.0, 0.0, fixture::SOLID_OMEGA],
        ..HomogeneousRayBackground::zero()
    };
    let out = semi_lagrangian_step(
        &mesh,
        &states,
        fixture::SOLID_TARGET,
        &background,
        &background,
        fixture::SOLID_DT,
        SemiLagrangianOptions {
            characteristic_substeps: 4,
            endpoint_tolerance: 2.0e-12,
            remap: RemapOptions::default(),
        },
    )
    .unwrap();

    assert!(max_abs3(out.departure.direction, fixture::SOLID_DEPARTURE) < 4.0e-14);
    assert!(max_abs9(&out.packed, &fixture::SOLID_EXPECTED_PACKED) < 5.0e-13);
    let exact = unpolarized(fixture::SOLID_TARGET, intensity(fixture::SOLID_DEPARTURE));
    assert!((max_abs9(&out.packed, &exact) - fixture::SOLID_SPATIAL_ERROR).abs() < 5.0e-13);
}
