use bianchi_rustcore::generated::typeii_polarized_liouville::{
    typeii_background_from_state, HomogeneousRayBackground,
};
use bianchi_rustcore::generated::typeii_polarized_remap::RemapOptions;
use bianchi_rustcore::generated::typeii_spherical_grid_remap::{
    semi_lagrangian_step, semi_lagrangian_typeii_step, trace_departure, BoundaryClass, GridError,
    GridOptions, SemiLagrangianOptions, SphericalTriMesh,
};

fn dot(a: [f64; 3], b: [f64; 3]) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}

fn norm(a: [f64; 3]) -> f64 {
    dot(a, a).sqrt()
}

fn normalize(a: [f64; 3]) -> [f64; 3] {
    let n = norm(a);
    [a[0] / n, a[1] / n, a[2] / n]
}

fn cross(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
}

fn add(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [a[0] + b[0], a[1] + b[1], a[2] + b[2]]
}

fn scale(a: [f64; 3], s: f64) -> [f64; 3] {
    [s * a[0], s * a[1], s * a[2]]
}

fn rz(angle: f64, e: [f64; 3]) -> [f64; 3] {
    let (sn, c) = angle.sin_cos();
    [c * e[0] - sn * e[1], sn * e[0] + c * e[1], e[2]]
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

fn unpolarized(e: [f64; 3], intensity: f64) -> [f64; 9] {
    let p = projector(e);
    let mut m = [[0.0; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            m[i][j] = 0.5 * intensity * p[i][j];
        }
    }
    pack(&m)
}

fn max_abs9(a: &[f64; 9], b: &[f64; 9]) -> f64 {
    a.iter()
        .zip(b)
        .map(|(x, y)| (x - y).abs())
        .fold(0.0, f64::max)
}

fn max_abs3(a: [f64; 3], b: [f64; 3]) -> f64 {
    a.iter()
        .zip(b)
        .map(|(x, y)| (x - y).abs())
        .fold(0.0, f64::max)
}

fn intensity(e: [f64; 3]) -> f64 {
    1.2 + 0.25 * e[0] - 0.17 * e[1] + 0.11 * e[2]
}

fn solid_rotation_background(omega: f64) -> HomogeneousRayBackground {
    HomogeneousRayBackground {
        triad_rotation: [0.0, 0.0, omega],
        ..HomogeneousRayBackground::zero()
    }
}

fn semi_options() -> SemiLagrangianOptions {
    SemiLagrangianOptions {
        characteristic_substeps: 4,
        endpoint_tolerance: 2.0e-12,
        remap: RemapOptions::default(),
    }
}

#[test]
fn icosphere_counts_are_exact_and_mesh_is_closed() {
    for level in 0..=3 {
        let mesh = SphericalTriMesh::icosphere(level, GridOptions::default()).unwrap();
        let four = 4usize.pow(level as u32);
        assert_eq!(mesh.vertices().len(), 10 * four + 2);
        assert_eq!(mesh.faces().len(), 20 * four);
        assert_eq!(mesh.refinement_level(), Some(level));
        assert_eq!(mesh.edge_count(), 30 * four);
        assert!(mesh.maximum_unit_defect() < 3.0e-15);
        assert!(mesh.minimum_orientation() > 0.0);
    }
}

#[test]
fn locator_covers_fibonacci_directions_with_convex_weights() {
    let mesh = SphericalTriMesh::icosphere(2, GridOptions::default()).unwrap();
    let golden = (1.0 + 5.0_f64.sqrt()) / 2.0;
    for k in 0..1000 {
        let z = 1.0 - 2.0 * (k as f64 + 0.5) / 1000.0;
        let r = (1.0 - z * z).sqrt();
        let phi = 2.0 * std::f64::consts::PI * k as f64 / golden;
        let e = [r * phi.cos(), r * phi.sin(), z];
        let stencil = mesh.locate(e).unwrap();
        assert!(stencil.weights.iter().all(|w| *w >= 0.0));
        assert!((stencil.weights.iter().sum::<f64>() - 1.0).abs() < 3.0e-14);
        assert!(stencil.radial_scale > 0.0 && stencil.radial_scale <= 1.0 + 2.0e-14);
        assert!(stencil.candidate_faces >= 1);
    }
}

#[test]
fn edge_and_vertex_ties_are_independent_of_face_enumeration() {
    let opts = GridOptions::default();
    let mesh = SphericalTriMesh::icosphere(1, opts).unwrap();
    let mut reversed_faces = mesh.faces().to_vec();
    reversed_faces.reverse();
    let reversed =
        SphericalTriMesh::from_vertices_faces(mesh.vertices().to_vec(), reversed_faces, opts)
            .unwrap();

    let face = mesh.faces()[7];
    let vertex = mesh.vertices()[face[0]];
    let edge = normalize(add(mesh.vertices()[face[0]], mesh.vertices()[face[1]]));

    let a_vertex = mesh.locate(vertex).unwrap();
    let b_vertex = reversed.locate(vertex).unwrap();
    assert_eq!(a_vertex.face_key, b_vertex.face_key);
    assert_eq!(a_vertex.boundary, BoundaryClass::Vertex);
    assert_eq!(b_vertex.boundary, BoundaryClass::Vertex);

    let a_edge = mesh.locate(edge).unwrap();
    let b_edge = reversed.locate(edge).unwrap();
    assert_eq!(a_edge.face_key, b_edge.face_key);
    assert_eq!(a_edge.boundary, BoundaryClass::Edge);
    assert_eq!(b_edge.boundary, BoundaryClass::Edge);
    assert!(a_edge.candidate_faces >= 2);
    assert!(b_edge.candidate_faces >= 2);
}

#[test]
fn orientation_and_closed_manifold_mutations_fail_closed() {
    let opts = GridOptions::default();
    let mesh = SphericalTriMesh::icosphere(0, opts).unwrap();

    let mut flipped = mesh.faces().to_vec();
    flipped[0].swap(1, 2);
    let err =
        SphericalTriMesh::from_vertices_faces(mesh.vertices().to_vec(), flipped, opts).unwrap_err();
    assert!(matches!(err, GridError::InwardFace { .. }));

    let mut missing = mesh.faces().to_vec();
    missing.pop();
    let err =
        SphericalTriMesh::from_vertices_faces(mesh.vertices().to_vec(), missing, opts).unwrap_err();
    assert!(matches!(err, GridError::NonManifoldEdge { .. }));
}

#[test]
fn backward_departure_matches_analytic_solid_body_rotation() {
    let omega = 0.73;
    let dt = 0.31;
    let target = normalize([0.41, -0.37, 0.83]);
    let background = solid_rotation_background(omega);
    let trace = trace_departure(target, &background, &background, dt, 4).unwrap();
    let exact = rz(-omega * dt, target);
    assert!(max_abs3(trace.direction, exact) < 3.0e-14);
    assert!(trace.backward_orthogonality_defect < 3.0e-14);
    assert!(trace.backward_determinant_defect < 3.0e-14);
}

#[test]
fn grid_semi_lagrangian_error_is_spatial_and_second_order() {
    let omega = 0.61;
    let dt = 0.27;
    let background = solid_rotation_background(omega);
    let targets = [
        normalize([0.33, -0.24, 0.913]),
        normalize([-0.41, 0.22, 0.884]),
        normalize([0.13, 0.71, 0.692]),
        normalize([-0.62, -0.35, 0.72]),
        normalize([0.72, 0.18, -0.67]),
        normalize([-0.21, 0.53, -0.82]),
        normalize([0.54, -0.68, 0.49]),
        normalize([-0.75, 0.41, -0.52]),
    ];
    let mut errors = Vec::new();

    for level in 0..=3 {
        let mesh = SphericalTriMesh::icosphere(level, GridOptions::default()).unwrap();
        let source_states: Vec<[f64; 9]> = mesh
            .vertices()
            .iter()
            .copied()
            .map(|e| unpolarized(e, intensity(e)))
            .collect();
        let mut sum_squared = 0.0;
        for target in targets {
            let exact_departure = rz(-omega * dt, target);
            let expected = unpolarized(target, intensity(exact_departure));
            let out = semi_lagrangian_step(
                &mesh,
                &source_states,
                target,
                &background,
                &background,
                dt,
                semi_options(),
            )
            .unwrap();
            assert!(out.characteristic_roundtrip_defect < 2.0e-12);
            assert!(max_abs3(out.departure.direction, exact_departure) < 4.0e-14);
            let error = max_abs9(&out.packed, &expected);
            sum_squared += error * error;
        }
        errors.push((sum_squared / targets.len() as f64).sqrt());
    }

    println!("B2B_SPATIAL_RMS_ERRORS={errors:?}");
    assert!(errors.windows(2).all(|w| w[1] < 0.55 * w[0]), "{errors:?}");
    for pair in errors.windows(2).skip(1) {
        let ratio = pair[0] / pair[1];
        assert!(ratio > 3.0, "ratio={ratio}, errors={errors:?}");
    }
}

#[test]
fn combined_error_decomposes_into_characteristic_and_remap_parts() {
    let omega = -0.47;
    let dt = 0.19;
    let background = solid_rotation_background(omega);
    let target = normalize([-0.27, 0.44, 0.856]);
    let exact_departure = rz(-omega * dt, target);
    let mesh = SphericalTriMesh::icosphere(2, GridOptions::default()).unwrap();
    let source_states: Vec<[f64; 9]> = mesh
        .vertices()
        .iter()
        .copied()
        .map(|e| unpolarized(e, intensity(e)))
        .collect();

    let trace = trace_departure(target, &background, &background, dt, 4).unwrap();
    let characteristic_error = max_abs3(trace.direction, exact_departure);
    let exact_departure_state = unpolarized(exact_departure, intensity(exact_departure));
    let remapped = mesh
        .remap_packed(&source_states, exact_departure, RemapOptions::default())
        .unwrap();
    let remap_error = max_abs9(&remapped.packed, &exact_departure_state);
    let combined = semi_lagrangian_step(
        &mesh,
        &source_states,
        target,
        &background,
        &background,
        dt,
        semi_options(),
    )
    .unwrap();
    let combined_error = max_abs9(
        &combined.packed,
        &unpolarized(target, intensity(exact_departure)),
    );
    println!(
        "B2B_ERROR_SPLIT characteristic={characteristic_error:.17e} remap={remap_error:.17e} combined={combined_error:.17e}"
    );
    assert!(characteristic_error < 5.0e-14);
    assert!(combined_error <= 1.15 * remap_error + 2.0e-13);
    assert!(combined_error >= 0.5 * remap_error);
}

fn advance_grid(
    mesh: &SphericalTriMesh,
    states: &[[f64; 9]],
    background: &HomogeneousRayBackground,
    dt: f64,
) -> Vec<[f64; 9]> {
    mesh.vertices()
        .iter()
        .copied()
        .map(|target| {
            semi_lagrangian_step(
                mesh,
                states,
                target,
                background,
                background,
                dt,
                semi_options(),
            )
            .unwrap()
            .packed
        })
        .collect()
}

#[test]
fn forward_backward_diffusion_decreases_under_grid_refinement() {
    let background = solid_rotation_background(0.42);
    let dt = 0.16;
    let mut errors = Vec::new();
    for level in 0..=2 {
        let mesh = SphericalTriMesh::icosphere(level, GridOptions::default()).unwrap();
        let initial: Vec<[f64; 9]> = mesh
            .vertices()
            .iter()
            .copied()
            .map(|e| unpolarized(e, intensity(e)))
            .collect();
        let forward = advance_grid(&mesh, &initial, &background, dt);
        let back = advance_grid(&mesh, &forward, &background, -dt);
        let err = back
            .iter()
            .zip(&initial)
            .map(|(a, b)| max_abs9(a, b))
            .fold(0.0, f64::max);
        errors.push(err);
    }
    println!("B2B_ROUNDTRIP_DIFFUSION={errors:?}");
    assert!(errors[1] < 0.55 * errors[0], "{errors:?}");
    assert!(errors[2] < 0.55 * errors[1], "{errors:?}");
}

#[test]
fn dimension_and_invalid_option_paths_fail_closed() {
    let mesh = SphericalTriMesh::icosphere(0, GridOptions::default()).unwrap();
    let target = mesh.vertices()[0];
    let background = solid_rotation_background(0.1);
    let err = semi_lagrangian_step(
        &mesh,
        &[],
        target,
        &background,
        &background,
        0.1,
        semi_options(),
    )
    .unwrap_err();
    assert!(matches!(err, GridError::StateCountMismatch { .. }));

    let mut bad = semi_options();
    bad.characteristic_substeps = 0;
    let states: Vec<_> = mesh
        .vertices()
        .iter()
        .copied()
        .map(|e| unpolarized(e, 1.0))
        .collect();
    let err = semi_lagrangian_step(&mesh, &states, target, &background, &background, 0.1, bad)
        .unwrap_err();
    assert!(matches!(err, GridError::InvalidOptionsForStep));
}

#[test]
fn typeii_wrapper_matches_generic_background_adapter() {
    let mesh = SphericalTriMesh::icosphere(1, GridOptions::default()).unwrap();
    let source_states: Vec<[f64; 9]> = mesh
        .vertices()
        .iter()
        .copied()
        .map(|e| unpolarized(e, intensity(e)))
        .collect();
    let previous_state = [0.18, -0.04, 0.025, 0.72, 0.05];
    let next_state = [0.176, -0.037, 0.023, 0.716, 0.049];
    let target = normalize([0.31, -0.22, 0.925]);
    let step = 0.012;
    let options = semi_options();
    let previous = typeii_background_from_state(&previous_state).unwrap();
    let next = typeii_background_from_state(&next_state).unwrap();

    let generic = semi_lagrangian_step(
        &mesh,
        &source_states,
        target,
        &previous,
        &next,
        step,
        options,
    )
    .unwrap();
    let wrapped = semi_lagrangian_typeii_step(
        &mesh,
        &source_states,
        target,
        &previous_state,
        &next_state,
        step,
        options,
    )
    .unwrap();

    assert!(max_abs9(&generic.packed, &wrapped.packed) < 2.0e-15);
    assert!(max_abs3(generic.departure.direction, wrapped.departure.direction) < 2.0e-15);
    assert_eq!(generic.stencil.face_key, wrapped.stencil.face_key);
}

#[test]
fn face_centroid_reconstructs_from_reported_radial_barycentrics() {
    let mesh = SphericalTriMesh::icosphere(1, GridOptions::default()).unwrap();
    let face = mesh.faces()[13];
    let d = normalize(add(
        add(mesh.vertices()[face[0]], mesh.vertices()[face[1]]),
        mesh.vertices()[face[2]],
    ));
    let s = mesh.locate(d).unwrap();
    assert_eq!(s.boundary, BoundaryClass::Interior);
    let mut x = [0.0; 3];
    for (weight, index) in s.weights.into_iter().zip(s.vertex_indices) {
        x = add(x, scale(mesh.vertices()[index], weight));
    }
    let expected = scale(d, s.radial_scale);
    assert!(max_abs3(x, expected) < 5.0e-14);
    assert!(dot(
        cross(
            mesh.vertices()[s.vertex_indices[1]],
            mesh.vertices()[s.vertex_indices[2]]
        ),
        mesh.vertices()[s.vertex_indices[0]]
    )
    .is_finite());
}
