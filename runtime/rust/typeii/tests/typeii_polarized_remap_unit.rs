use bianchi_rustcore::generated::typeii_physical_guard::{
    enforce_realizable_screen_state, validate_realizable_screen_state, PhysicalCarrierError,
    ScreenInputPolicy,
};
use bianchi_rustcore::generated::typeii_polarized_remap::{
    parallel_transport_matrix, remap_convex_packed, transport_packed_to_direction, Mat3,
    RemapError, RemapOptions,
};

fn dot(a: [f64; 3], b: [f64; 3]) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}

fn cross(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
}

fn norm(a: [f64; 3]) -> f64 {
    dot(a, a).sqrt()
}

fn normalize(a: [f64; 3]) -> [f64; 3] {
    let n = norm(a);
    [a[0] / n, a[1] / n, a[2] / n]
}

fn mm(a: &Mat3, b: &Mat3) -> Mat3 {
    let mut out = [[0.0; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            for k in 0..3 {
                out[i][j] += a[i][k] * b[k][j];
            }
        }
    }
    out
}

fn transpose(a: &Mat3) -> Mat3 {
    let mut out = [[0.0; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            out[i][j] = a[j][i];
        }
    }
    out
}

fn mat_vec(a: &Mat3, x: [f64; 3]) -> [f64; 3] {
    [dot(a[0], x), dot(a[1], x), dot(a[2], x)]
}

fn max_abs_vec(a: [f64; 3], b: [f64; 3]) -> f64 {
    (0..3).map(|i| (a[i] - b[i]).abs()).fold(0.0, f64::max)
}

fn max_abs9(a: &[f64; 9], b: &[f64; 9]) -> f64 {
    (0..9).map(|i| (a[i] - b[i]).abs()).fold(0.0, f64::max)
}

fn pack(m: &Mat3) -> [f64; 9] {
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

fn unpack(p: &[f64; 9]) -> Mat3 {
    [
        [p[0], p[3] + p[8], p[4] - p[7]],
        [p[3] - p[8], p[1], p[5] + p[6]],
        [p[4] + p[7], p[5] - p[6], p[2]],
    ]
}

fn projector(e: [f64; 3]) -> Mat3 {
    let mut p = [[0.0; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            p[i][j] = if i == j { 1.0 } else { 0.0 } - e[i] * e[j];
        }
    }
    p
}

fn canonical_dyad(e: [f64; 3]) -> ([f64; 3], [f64; 3]) {
    let e = normalize(e);
    let refs = [[0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]];
    let r = refs
        .into_iter()
        .min_by(|a, b| dot(*a, e).abs().total_cmp(&dot(*b, e).abs()))
        .unwrap();
    let s1 = normalize([
        r[0] - dot(r, e) * e[0],
        r[1] - dot(r, e) * e[1],
        r[2] - dot(r, e) * e[2],
    ]);
    let s2 = normalize(cross(e, s1));
    (s1, s2)
}

fn rotated_dyad(e: [f64; 3], psi: f64) -> ([f64; 3], [f64; 3]) {
    let (s1, s2) = canonical_dyad(e);
    let (sn, c) = psi.sin_cos();
    (
        [
            c * s1[0] + sn * s2[0],
            c * s1[1] + sn * s2[1],
            c * s1[2] + sn * s2[2],
        ],
        [
            -sn * s1[0] + c * s2[0],
            -sn * s1[1] + c * s2[1],
            -sn * s1[2] + c * s2[2],
        ],
    )
}

fn packed_from_stokes(e: [f64; 3], psi: f64, st: [f64; 4]) -> [f64; 9] {
    let (s1, s2) = rotated_dyad(e, psi);
    let [i, q, u, v] = st;
    let h11 = 0.5 * (i + q);
    let h22 = 0.5 * (i - q);
    // Remote B1 authority: H12=(U-iV)/2, H21=(U+iV)/2, p8=-V/2.
    let h12 = 0.5 * (u - v);
    let h21 = 0.5 * (u + v);
    let mut m = [[0.0; 3]; 3];
    for a in 0..3 {
        for b in 0..3 {
            m[a][b] = h11 * s1[a] * s1[b]
                + h22 * s2[a] * s2[b]
                + h12 * s1[a] * s2[b]
                + h21 * s2[a] * s1[b];
        }
    }
    pack(&m)
}

fn stokes_from_packed(e: [f64; 3], psi: f64, p: &[f64; 9]) -> [f64; 4] {
    let (s1, s2) = rotated_dyad(e, psi);
    let m = unpack(p);
    let bilinear = |a: [f64; 3], b: [f64; 3]| {
        let mb = mat_vec(&m, b);
        dot(a, mb)
    };
    let h11 = bilinear(s1, s1);
    let h22 = bilinear(s2, s2);
    let h12 = bilinear(s1, s2);
    let h21 = bilinear(s2, s1);
    [h11 + h22, h11 - h22, h12 + h21, h21 - h12]
}

fn axis_rotation(axis: [f64; 3], angle: f64) -> Mat3 {
    let [x, y, z] = normalize(axis);
    let (sn, c) = angle.sin_cos();
    let q = 1.0 - c;
    [
        [c + q * x * x, q * x * y - sn * z, q * x * z + sn * y],
        [q * y * x + sn * z, c + q * y * y, q * y * z - sn * x],
        [q * z * x - sn * y, q * z * y + sn * x, c + q * z * z],
    ]
}

fn rotate_packed(p: &[f64; 9], r: &Mat3) -> [f64; 9] {
    pack(&mm(&mm(r, &unpack(p)), &transpose(r)))
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

#[test]
fn minimal_rotation_maps_direction_and_roundtrips_tensor() {
    let opts = RemapOptions::default();
    let a = normalize([0.3, -0.4, 0.8]);
    let b = normalize([-0.2, 0.7, 0.5]);
    let r = parallel_transport_matrix(a, b, opts).unwrap();
    assert!(max_abs_vec(mat_vec(&r, a), b) < 2e-14);

    let p = packed_from_stokes(a, 0.31, [2.0, 0.5, -0.3, 0.2]);
    let pb = transport_packed_to_direction(&p, a, b, opts).unwrap();
    let pa = transport_packed_to_direction(&pb, b, a, opts).unwrap();
    let roundtrip = max_abs9(&pa, &p);
    println!("roundtrip_max_abs_error={roundtrip:.17e}");
    assert!(roundtrip < 4e-13);
}

#[test]
fn antipodal_and_nonphysical_inputs_fail_closed() {
    let opts = RemapOptions::default();
    let err = parallel_transport_matrix([0.0, 0.0, 1.0], [0.0, 0.0, -1.0], opts).unwrap_err();
    assert!(matches!(err, RemapError::AntipodalTransport { .. }));

    let mut bad = unpolarized([0.0, 0.0, 1.0], 1.0);
    bad[2] = 0.1; // longitudinal zz component
    let err =
        transport_packed_to_direction(&bad, [0.0, 0.0, 1.0], [1.0, 0.0, 0.0], opts).unwrap_err();
    assert!(matches!(
        err,
        RemapError::ScreenTransversalityViolation { .. }
    ));
}

#[test]
fn weights_are_strictly_convex_and_dimension_checked() {
    let opts = RemapOptions::default();
    let dirs = [[0.0, 0.0, 1.0], [1.0, 0.0, 0.0]];
    let states = [unpolarized(dirs[0], 1.0), unpolarized(dirs[1], 1.0)];
    let target = normalize([1.0, 0.0, 1.0]);

    let err = remap_convex_packed(&dirs, &states, &[0.6, 0.5], target, opts).unwrap_err();
    assert!(matches!(err, RemapError::WeightSum { .. }));
    let err = remap_convex_packed(&dirs, &states, &[1.1, -0.1], target, opts).unwrap_err();
    assert!(matches!(err, RemapError::NegativeWeight { .. }));
    let err = remap_convex_packed(&dirs, &states[..1], &[1.0], target, opts).unwrap_err();
    assert!(matches!(err, RemapError::DimensionMismatch { .. }));
}

#[test]
fn unpolarized_monopole_is_exact_for_any_convex_stencil() {
    let opts = RemapOptions::default();
    let dirs = [
        normalize([0.2, 0.1, 1.0]),
        normalize([-0.4, 0.3, 0.8]),
        normalize([0.1, -0.6, 0.7]),
    ];
    let states = dirs.map(|e| unpolarized(e, 2.4));
    let target = normalize([-0.3, 0.2, 0.9]);
    let out = remap_convex_packed(&dirs, &states, &[0.2, 0.35, 0.45], target, opts).unwrap();
    assert!(max_abs9(&out.packed, &unpolarized(target, 2.4)) < 3e-14);
    assert!(out.diagnostics.output_screen_leakage < 5e-15);
}

#[test]
fn covariantly_constant_polarized_tensor_is_exact() {
    let opts = RemapOptions::default();
    let target = normalize([0.2, -0.3, 0.93]);
    let target_state = packed_from_stokes(target, 0.27, [2.2, 0.55, -0.25, 0.18]);
    let dirs = [
        normalize([0.38, -0.21, 0.9]),
        normalize([-0.02, -0.42, 0.91]),
        normalize([0.12, -0.08, 0.99]),
    ];
    let mut states = [[0.0; 9]; 3];
    for i in 0..3 {
        states[i] = transport_packed_to_direction(&target_state, target, dirs[i], opts).unwrap();
    }
    let out = remap_convex_packed(&dirs, &states, &[0.15, 0.25, 0.60], target, opts).unwrap();
    assert!(max_abs9(&out.packed, &target_state) < 7e-13);
}

#[test]
fn common_screen_result_is_source_dyad_gauge_invariant_and_naive_qu_is_not() {
    let opts = RemapOptions::default();
    let target = [0.0, 0.0, 1.0];
    let target_state = packed_from_stokes(target, 0.0, [2.0, 0.8, 0.35, 0.0]);
    let r1 = axis_rotation([0.0, 1.0, 0.0], 0.35);
    let r2 = axis_rotation([1.0, 0.0, 0.0], -0.31);
    let dirs = [mat_vec(&r1, target), mat_vec(&r2, target)];
    let states = [
        rotate_packed(&target_state, &r1),
        rotate_packed(&target_state, &r2),
    ];

    let out = remap_convex_packed(&dirs, &states, &[0.5, 0.5], target, opts).unwrap();
    assert!(max_abs9(&out.packed, &target_state) < 5e-13);

    // Deliberately wrong: average node-local Q/U after unrelated gauge rotations.
    let a = stokes_from_packed(dirs[0], 0.63, &states[0]);
    let b = stokes_from_packed(dirs[1], -0.48, &states[1]);
    let naive = [
        0.5 * (a[0] + b[0]),
        0.5 * (a[1] + b[1]),
        0.5 * (a[2] + b[2]),
        0.5 * (a[3] + b[3]),
    ];
    let correct = stokes_from_packed(target, 0.0, &target_state);
    let qu_error = ((naive[1] - correct[1]).powi(2) + (naive[2] - correct[2]).powi(2)).sqrt();
    println!("naive_qu_gauge_error={qu_error:.17e}");
    assert!(qu_error > 0.2, "negative control was too weak: {qu_error}");
}

#[test]
fn convex_remap_preserves_v_zero_and_coherency_cone() {
    let opts = RemapOptions::default();
    let target = normalize([0.1, 0.2, 0.97]);
    let dirs = [normalize([0.35, 0.1, 0.93]), normalize([-0.2, 0.3, 0.93])];
    let states = [
        packed_from_stokes(dirs[0], 0.2, [2.0, 0.7, 0.2, 0.0]),
        packed_from_stokes(dirs[1], -0.4, [1.4, -0.3, 0.4, 0.0]),
    ];
    let out = remap_convex_packed(&dirs, &states, &[0.4, 0.6], target, opts).unwrap();
    let st = stokes_from_packed(target, 0.0, &out.packed);
    assert!(st[3].abs() < 3e-14);
    let cone = st[0] * st[0] - st[1] * st[1] - st[2] * st[2] - st[3] * st[3];
    assert!(cone >= -2e-13, "cone defect={cone}");
}

#[test]
fn symmetric_stencil_has_second_order_l1_and_spin2_amplitude_error() {
    let opts = RemapOptions::default();
    let target = [0.0, 0.0, 1.0];
    let base = packed_from_stokes(target, 0.0, [1.0, 0.35, -0.22, 0.0]);
    let hs = [0.2_f64, 0.1, 0.05, 0.025];
    let mut errors = Vec::new();
    for h in hs {
        let rp = axis_rotation([0.0, 1.0, 0.0], h);
        let rm = axis_rotation([0.0, 1.0, 0.0], -h);
        let dirs = [mat_vec(&rp, target), mat_vec(&rm, target)];
        let amp = |e: [f64; 3]| 1.0 + 0.3 * e[2]; // l=0 + l=1
        let mut states = [rotate_packed(&base, &rp), rotate_packed(&base, &rm)];
        for i in 0..2 {
            for x in &mut states[i] {
                *x *= amp(dirs[i]);
            }
        }
        let out = remap_convex_packed(&dirs, &states, &[0.5, 0.5], target, opts).unwrap();
        let mut exact = base;
        for x in &mut exact {
            *x *= amp(target);
        }
        errors.push(max_abs9(&out.packed, &exact));
    }
    println!("refinement_errors={errors:?}");
    for i in 0..errors.len() - 1 {
        let ratio = errors[i] / errors[i + 1];
        println!("refinement_ratio_{i}={ratio:.17e}");
        assert!(
            (3.85..4.15).contains(&ratio),
            "ratio={ratio}, errors={errors:?}"
        );
    }
}

#[test]
fn target_output_is_screen_projected_and_diagnostics_are_finite() {
    let opts = RemapOptions::default();
    let dirs = [normalize([0.2, 0.0, 1.0]), normalize([-0.1, 0.15, 1.0])];
    let states = [unpolarized(dirs[0], 1.0), unpolarized(dirs[1], 1.2)];
    let target = normalize([0.0, -0.1, 1.0]);
    let out = remap_convex_packed(&dirs, &states, &[0.3, 0.7], target, opts).unwrap();
    assert!(out.diagnostics.weight_sum.is_finite());
    assert!(out.diagnostics.minimum_transport_dot.is_finite());
    assert!(out.diagnostics.max_input_screen_leakage < 1e-14);
    assert!(out.diagnostics.output_screen_leakage < 1e-14);
}

#[test]
fn near_antipodal_and_nonfinite_paths_fail_closed() {
    let opts = RemapOptions::default();
    let eps = 1.0e-6;
    let near_antipode = normalize([eps, 0.0, -1.0]);
    let err = parallel_transport_matrix([0.0, 0.0, 1.0], near_antipode, opts).unwrap_err();
    assert!(matches!(err, RemapError::AntipodalTransport { .. }));

    let dirs = [[0.0, 0.0, 1.0]];
    let states = [unpolarized(dirs[0], 1.0)];
    let err = remap_convex_packed(&dirs, &states, &[f64::NAN], dirs[0], opts).unwrap_err();
    assert!(matches!(err, RemapError::NonFiniteWeight { .. }));

    let mut bad_state = states;
    bad_state[0][4] = f64::INFINITY;
    let err = remap_convex_packed(&dirs, &bad_state, &[1.0], dirs[0], opts).unwrap_err();
    assert!(matches!(err, RemapError::NonFiniteState { .. }));
}

#[test]
fn tolerated_roundoff_leakage_is_removed_on_output() {
    let opts = RemapOptions::default();
    let source = [0.0, 0.0, 1.0];
    let target = normalize([0.2, -0.1, 0.97]);
    let mut state = unpolarized(source, 1.0);
    state[2] = 5.0e-13; // below the scale-aware acceptance threshold
    let out = remap_convex_packed(&[source], &[state], &[1.0], target, opts).unwrap();
    assert!(out.diagnostics.output_screen_leakage < 3.0e-16);
    let expected = unpolarized(target, 1.0);
    assert!(max_abs9(&out.packed, &expected) < 2.0e-13);
}

#[test]
fn low_intensity_longitudinal_leakage_is_not_hidden_by_an_absolute_scale_floor() {
    // Production defect: max(trace, 1) makes the transversality tolerance depend
    // on the caller's intensity units and accepts a mostly-longitudinal faint state.
    let opts = RemapOptions::default();
    let source = [0.0, 0.0, 1.0];
    let mut state = unpolarized(source, 1.0e-15);
    state[2] = 1.0e-13;

    assert!(
        transport_packed_to_direction(&state, source, source, opts).is_err(),
        "trace-normalized transversality must reject leakage larger than the source intensity"
    );
}

#[test]
fn nonrealizable_screen_coherency_fails_closed() {
    // Production defect: a transverse but indefinite coherency matrix (I=0,
    // Q=1) used to pass because remap checked only J=PJP.
    let opts = RemapOptions::default();
    let source = [0.0, 0.0, 1.0];
    let indefinite = packed_from_stokes(source, 0.0, [0.0, 1.0, 0.0, 0.0]);

    assert!(
        transport_packed_to_direction(&indefinite, source, source, opts).is_err(),
        "a negative screen-coherency eigenvalue must be rejected"
    );
}

#[test]
fn compensated_weight_sum_accepts_a_large_exactly_uniform_convex_stencil() {
    // Production defect: linear summation drifts by more than the frozen
    // weight tolerance for a large, exactly uniform non-negative stencil.
    let opts = RemapOptions::default();
    let count = 50_000usize;
    let direction = [0.0, 0.0, 1.0];
    let directions = vec![direction; count];
    let states = vec![[0.0; 9]; count];
    let weights = vec![1.0 / count as f64; count];

    let out = remap_convex_packed(&directions, &states, &weights, direction, opts)
        .expect("compensated summation should accept the uniform convex stencil");
    assert_eq!(out.packed, [0.0; 9]);
    assert!((out.diagnostics.weight_sum - 1.0).abs() <= opts.weight_tolerance);
}

#[test]
fn explicit_transport_support_bound_is_enforced_without_changing_the_default() {
    // Production defect: minimum_transport_dot was diagnostic-only, so a
    // stencil could accept transport outside its declared support.
    let from = [0.0, 0.0, 1.0];
    let to = normalize([1.0, 0.0, 1.0]);
    parallel_transport_matrix(from, to, RemapOptions::default())
        .expect("the historical antipodal-only default must remain accepted");

    let opts = RemapOptions {
        minimum_transport_dot: 0.8,
        ..RemapOptions::default()
    };
    let err = parallel_transport_matrix(from, to, opts).unwrap_err();
    assert!(matches!(
        err,
        RemapError::TransportSupportViolation {
            source: None,
            dot,
            minimum_dot,
        } if (dot - 2.0_f64.sqrt().recip()).abs() < 2.0e-15
            && (minimum_dot - 0.8).abs() < f64::EPSILON
    ));
}

#[test]
fn carrier_projection_and_state_realizability_are_separate_contracts() {
    // Production defect: a transverse but indefinite screen state could be
    // reported as physical because only the carrier projection was checked.
    let direction = [0.0, 0.0, 1.0];
    let indefinite = packed_from_stokes(direction, 0.0, [0.0, 1.0, 0.0, 0.0]);
    assert!(matches!(
        validate_realizable_screen_state(&[direction], &indefinite, 2.0e-12),
        Err(PhysicalCarrierError::NonRealizableScreenState { node: 0, .. })
    ));
    assert!(matches!(
        enforce_realizable_screen_state(
            &[direction],
            &indefinite,
            ScreenInputPolicy::Project,
            2.0e-12,
        ),
        Err(PhysicalCarrierError::NonRealizableScreenState { node: 0, .. })
    ));

    let exact_vacuum = [0.0; 9];
    validate_realizable_screen_state(&[direction], &exact_vacuum, 2.0e-12)
        .expect("exact transverse vacuum has an unambiguous PSD limit");
}
