//! G-POL-LIOUVILLE-II-B2: common-screen convex remap core.
//!
//! The production path never interpolates node-local Q/U components. Each packed
//! coherency tensor is first parallel transported along the unique shortest
//! great-circle arc to the common target direction, then convexly combined and
//! projected once onto the target screen. Exact/near antipodes fail closed.

pub type Mat3 = [[f64; 3]; 3];

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct RemapOptions {
    /// Absolute unit-vector validation tolerance.
    pub direction_tolerance: f64,
    /// Scale-aware source/output screen leakage tolerance.
    pub screen_tolerance: f64,
    /// Allowed absolute defect in sum(weights)=1.
    pub weight_tolerance: f64,
    /// Fail when dot(from,to) <= -1 + this margin.
    pub antipodal_margin: f64,
    /// Smallest source/target dot product supported by the caller's stencil.
    ///
    /// The default reproduces the historical antipodal-only guard exactly.
    /// Callers with a narrower interpolation support must opt into a stricter
    /// bound rather than merely inspecting `minimum_transport_dot` afterward.
    pub minimum_transport_dot: f64,
}

impl Default for RemapOptions {
    fn default() -> Self {
        Self {
            direction_tolerance: 1.0e-12,
            screen_tolerance: 2.0e-12,
            weight_tolerance: 2.0e-13,
            antipodal_margin: 1.0e-10,
            minimum_transport_dot: -1.0 + 1.0e-10,
        }
    }
}

#[derive(Clone, Debug, PartialEq)]
pub enum RemapError {
    InvalidOptions,
    EmptyStencil,
    DimensionMismatch {
        directions: usize,
        states: usize,
        weights: usize,
    },
    NonFiniteDirection {
        source: Option<usize>,
        component: usize,
    },
    DirectionNotUnit {
        source: Option<usize>,
        norm_error: f64,
    },
    NonFiniteState {
        source: usize,
        component: usize,
    },
    NonFiniteWeight {
        index: usize,
    },
    NegativeWeight {
        index: usize,
        value: f64,
    },
    WeightSum {
        sum: f64,
    },
    AntipodalTransport {
        source: Option<usize>,
        dot: f64,
    },
    ScreenTransversalityViolation {
        source: usize,
        leakage: f64,
        intensity: f64,
        tolerance: f64,
    },
    NonRealizableSource {
        source: usize,
        minimum_eigenvalue: f64,
        intensity: f64,
        tolerance: f64,
    },
    TransportSupportViolation {
        source: Option<usize>,
        dot: f64,
        minimum_dot: f64,
    },
    TransportArithmeticNonFinite {
        source: Option<usize>,
        stage: &'static str,
    },
    TransportMapDefect {
        source: Option<usize>,
        map_defect: f64,
        orthogonality_defect: f64,
        determinant_defect: f64,
        tolerance: f64,
    },
    OutputScreenTransversalityViolation {
        leakage: f64,
        intensity: f64,
        tolerance: f64,
    },
    NonRealizableOutput {
        minimum_eigenvalue: f64,
        intensity: f64,
        tolerance: f64,
    },
    AccumulationArithmeticNonFinite,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct RemapDiagnostics {
    pub weight_sum: f64,
    pub max_input_screen_leakage: f64,
    pub output_screen_leakage: f64,
    pub minimum_transport_dot: f64,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct RemapOutput {
    pub packed: [f64; 9],
    pub diagnostics: RemapDiagnostics,
}

#[inline]
fn dot(a: [f64; 3], b: [f64; 3]) -> f64 {
    a[0].mul_add(b[0], a[1].mul_add(b[1], a[2] * b[2]))
}

#[inline]
fn cross(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
}

#[inline]
fn norm(a: [f64; 3]) -> f64 {
    dot(a, a).sqrt()
}

#[inline]
fn scale(a: [f64; 3], x: f64) -> [f64; 3] {
    [x * a[0], x * a[1], x * a[2]]
}

#[inline]
fn identity() -> Mat3 {
    [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
}

#[inline]
fn transpose(a: &Mat3) -> Mat3 {
    let mut out = [[0.0; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            out[i][j] = a[j][i];
        }
    }
    out
}

#[inline]
fn mm(a: &Mat3, b: &Mat3) -> Mat3 {
    let mut out = [[0.0; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            for k in 0..3 {
                out[i][j] = a[i][k].mul_add(b[k][j], out[i][j]);
            }
        }
    }
    out
}

#[inline]
fn mat_vec(a: &Mat3, x: [f64; 3]) -> [f64; 3] {
    [dot(a[0], x), dot(a[1], x), dot(a[2], x)]
}

#[inline]
fn trace(a: &Mat3) -> f64 {
    a[0][0] + a[1][1] + a[2][2]
}

#[inline]
fn determinant(a: &Mat3) -> f64 {
    a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
        - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
        + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0])
}

#[inline]
fn unpack9(p: &[f64; 9]) -> Mat3 {
    [
        [p[0], p[3] + p[8], p[4] - p[7]],
        [p[3] - p[8], p[1], p[5] + p[6]],
        [p[4] + p[7], p[5] - p[6], p[2]],
    ]
}

#[inline]
fn pack9(m: &Mat3) -> [f64; 9] {
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

fn validate_options(options: RemapOptions) -> Result<(), RemapError> {
    let finite = [
        options.direction_tolerance,
        options.screen_tolerance,
        options.weight_tolerance,
        options.antipodal_margin,
        options.minimum_transport_dot,
    ]
    .iter()
    .all(|x| x.is_finite());
    if !finite
        || !(options.direction_tolerance > 0.0 && options.direction_tolerance <= 1.0e-6)
        || !(options.screen_tolerance > 0.0 && options.screen_tolerance <= 1.0e-6)
        || !(options.weight_tolerance > 0.0 && options.weight_tolerance <= 1.0e-6)
        || !(options.antipodal_margin > 0.0 && options.antipodal_margin < 1.0)
        || !(options.minimum_transport_dot >= -1.0 + options.antipodal_margin
            && options.minimum_transport_dot <= 1.0)
    {
        return Err(RemapError::InvalidOptions);
    }
    Ok(())
}

fn validate_direction(
    e: [f64; 3],
    source: Option<usize>,
    options: RemapOptions,
) -> Result<[f64; 3], RemapError> {
    for (component, value) in e.into_iter().enumerate() {
        if !value.is_finite() {
            return Err(RemapError::NonFiniteDirection { source, component });
        }
    }
    let n = norm(e);
    let norm_error = (n - 1.0).abs();
    if !(n > 0.0 && n.is_finite()) || norm_error > options.direction_tolerance {
        return Err(RemapError::DirectionNotUnit { source, norm_error });
    }
    Ok(scale(e, 1.0 / n))
}

#[inline]
fn projector(e: [f64; 3]) -> Mat3 {
    let mut p = identity();
    for i in 0..3 {
        for j in 0..3 {
            p[i][j] -= e[i] * e[j];
        }
    }
    p
}

#[inline]
fn project_matrix(m: &Mat3, e: [f64; 3]) -> Mat3 {
    let p = projector(e);
    mm(&mm(&p, m), &p)
}

#[inline]
fn screen_leakage(m: &Mat3, e: [f64; 3]) -> f64 {
    let projected = project_matrix(m, e);
    let mut out = 0.0_f64;
    for i in 0..3 {
        for j in 0..3 {
            out = out.max((m[i][j] - projected[i][j]).abs());
        }
    }
    out
}

fn tangent_frame(e: [f64; 3]) -> ([f64; 3], [f64; 3]) {
    let mut axis = 0usize;
    if e[1].abs() < e[axis].abs() {
        axis = 1;
    }
    if e[2].abs() < e[axis].abs() {
        axis = 2;
    }
    let mut seed = [0.0; 3];
    seed[axis] = 1.0;
    let parallel = dot(seed, e);
    let mut u = [
        seed[0] - parallel * e[0],
        seed[1] - parallel * e[1],
        seed[2] - parallel * e[2],
    ];
    let u_norm = norm(u);
    u = scale(u, 1.0 / u_norm);
    (u, cross(e, u))
}

#[inline]
fn bilinear(left: [f64; 3], matrix: &Mat3, right: [f64; 3]) -> f64 {
    dot(left, mat_vec(matrix, right))
}

fn minimum_screen_eigenvalue(m: &Mat3, e: [f64; 3]) -> f64 {
    let (u, v) = tangent_frame(e);
    let a = bilinear(u, m, u);
    let d = bilinear(v, m, v);
    let uv = bilinear(u, m, v);
    let vu = bilinear(v, m, u);
    let symmetric = 0.5 * (uv + vu);
    let antisymmetric = 0.5 * (uv - vu);
    let discriminant =
        ((a - d) * (a - d) + 4.0 * (symmetric * symmetric + antisymmetric * antisymmetric)).sqrt();
    0.5 * (a + d - discriminant)
}

fn validate_source_coherency(
    m: &Mat3,
    e: [f64; 3],
    source: usize,
    options: RemapOptions,
) -> Result<(f64, f64), RemapError> {
    let physical = project_matrix(m, e);
    if !physical.iter().flatten().all(|value| value.is_finite()) {
        return Err(RemapError::TransportArithmeticNonFinite {
            source: Some(source),
            stage: "source_screen_projection",
        });
    }
    let leakage = screen_leakage(m, e);
    let intensity = trace(&physical);
    let minimum_eigenvalue = minimum_screen_eigenvalue(&physical, e);
    if !leakage.is_finite() || !intensity.is_finite() || !minimum_eigenvalue.is_finite() {
        return Err(RemapError::TransportArithmeticNonFinite {
            source: Some(source),
            stage: "source_coherency_metrics",
        });
    }

    // Homogeneous acceptance: tolerances scale with the physical screen trace,
    // never with a unit-dependent max(1) floor. Exact vacuum is accepted only
    // when it is exactly transverse and positive semidefinite; every non-zero
    // zero-trace state therefore fails closed below.
    let tolerance = if intensity > 0.0 {
        options.screen_tolerance * intensity
    } else {
        0.0
    };
    if leakage > tolerance {
        return Err(RemapError::ScreenTransversalityViolation {
            source,
            leakage,
            intensity,
            tolerance,
        });
    }
    if intensity < 0.0 || minimum_eigenvalue < -tolerance {
        return Err(RemapError::NonRealizableSource {
            source,
            minimum_eigenvalue,
            intensity,
            tolerance,
        });
    }
    Ok((leakage, intensity))
}

fn validate_output_coherency(
    m: &Mat3,
    e: [f64; 3],
    options: RemapOptions,
) -> Result<(f64, f64), RemapError> {
    let leakage = screen_leakage(m, e);
    let intensity = trace(m);
    let minimum_eigenvalue = minimum_screen_eigenvalue(m, e);
    if !leakage.is_finite() || !intensity.is_finite() || !minimum_eigenvalue.is_finite() {
        return Err(RemapError::TransportArithmeticNonFinite {
            source: None,
            stage: "output_coherency_metrics",
        });
    }
    let tolerance = if intensity > 0.0 {
        options.screen_tolerance * intensity
    } else {
        0.0
    };
    if leakage > tolerance {
        return Err(RemapError::OutputScreenTransversalityViolation {
            leakage,
            intensity,
            tolerance,
        });
    }
    if intensity < 0.0 || minimum_eigenvalue < -tolerance {
        return Err(RemapError::NonRealizableOutput {
            minimum_eigenvalue,
            intensity,
            tolerance,
        });
    }
    Ok((leakage, intensity))
}

fn validate_transport_support(
    c: f64,
    source: Option<usize>,
    options: RemapOptions,
) -> Result<(), RemapError> {
    if c <= -1.0 + options.antipodal_margin {
        return Err(RemapError::AntipodalTransport { source, dot: c });
    }
    if c < options.minimum_transport_dot {
        return Err(RemapError::TransportSupportViolation {
            source,
            dot: c,
            minimum_dot: options.minimum_transport_dot,
        });
    }
    Ok(())
}

/// Minimal proper rotation from `from` to `to`.
///
/// Acting on tangent vectors, this is Levi-Civita parallel transport along the
/// unique shortest great-circle segment. Near antipodes no unique segment
/// exists and the routine fails closed.
pub fn parallel_transport_matrix(
    from: [f64; 3],
    to: [f64; 3],
    options: RemapOptions,
) -> Result<Mat3, RemapError> {
    validate_options(options)?;
    let from = validate_direction(from, None, options)?;
    let to = validate_direction(to, None, options)?;
    let c = dot(from, to).clamp(-1.0, 1.0);
    validate_transport_support(c, None, options)?;
    let a = cross(from, to);
    let s = norm(a);
    if s <= 32.0 * f64::EPSILON && c > 0.0 {
        return Ok(identity());
    }
    if !(s > 0.0 && s.is_finite()) {
        return Err(RemapError::TransportArithmeticNonFinite {
            source: None,
            stage: "rotation_axis",
        });
    }
    let [x, y, z] = scale(a, 1.0 / s);
    let one_minus_c = 1.0 - c;
    let r = [
        [
            c + one_minus_c * x * x,
            one_minus_c * x * y - s * z,
            one_minus_c * x * z + s * y,
        ],
        [
            one_minus_c * y * x + s * z,
            c + one_minus_c * y * y,
            one_minus_c * y * z - s * x,
        ],
        [
            one_minus_c * z * x - s * y,
            one_minus_c * z * y + s * x,
            c + one_minus_c * z * z,
        ],
    ];
    if !r.iter().flatten().all(|x| x.is_finite()) {
        return Err(RemapError::TransportArithmeticNonFinite {
            source: None,
            stage: "rotation_matrix",
        });
    }
    let mapped = mat_vec(&r, from);
    let map_defect = (0..3)
        .map(|i| (mapped[i] - to[i]).abs())
        .fold(0.0, f64::max);
    let gram = mm(&transpose(&r), &r);
    let orthogonality_defect = (0..3)
        .flat_map(|i| (0..3).map(move |j| (gram[i][j] - if i == j { 1.0 } else { 0.0 }).abs()))
        .fold(0.0, f64::max);
    let determinant_defect = (determinant(&r) - 1.0).abs();
    let tolerance = 32.0 * options.direction_tolerance.max(f64::EPSILON);
    if map_defect > tolerance || orthogonality_defect > tolerance || determinant_defect > tolerance
    {
        return Err(RemapError::TransportMapDefect {
            source: None,
            map_defect,
            orthogonality_defect,
            determinant_defect,
            tolerance,
        });
    }
    Ok(r)
}

fn transport_validated(
    m: &Mat3,
    from: [f64; 3],
    to: [f64; 3],
    options: RemapOptions,
    source: Option<usize>,
) -> Result<(Mat3, f64, f64), RemapError> {
    let c = dot(from, to).clamp(-1.0, 1.0);
    validate_transport_support(c, source, options)?;
    let r = parallel_transport_matrix(from, to, options).map_err(|err| match err {
        RemapError::AntipodalTransport { dot, .. } => {
            RemapError::AntipodalTransport { source, dot }
        }
        RemapError::TransportSupportViolation {
            dot, minimum_dot, ..
        } => RemapError::TransportSupportViolation {
            source,
            dot,
            minimum_dot,
        },
        RemapError::TransportArithmeticNonFinite { stage, .. } => {
            RemapError::TransportArithmeticNonFinite { source, stage }
        }
        RemapError::TransportMapDefect {
            map_defect,
            orthogonality_defect,
            determinant_defect,
            tolerance,
            ..
        } => RemapError::TransportMapDefect {
            source,
            map_defect,
            orthogonality_defect,
            determinant_defect,
            tolerance,
        },
        other => other,
    })?;
    let transported = mm(&mm(&r, m), &transpose(&r));
    if !transported.iter().flatten().all(|x| x.is_finite()) {
        return Err(RemapError::TransportArithmeticNonFinite {
            source,
            stage: "transported_coherency",
        });
    }
    Ok((transported, c, screen_leakage(m, from)))
}

pub fn transport_packed_to_direction(
    packed: &[f64; 9],
    from: [f64; 3],
    to: [f64; 3],
    options: RemapOptions,
) -> Result<[f64; 9], RemapError> {
    validate_options(options)?;
    let from = validate_direction(from, Some(0), options)?;
    let to = validate_direction(to, None, options)?;
    for (component, value) in packed.iter().copied().enumerate() {
        if !value.is_finite() {
            return Err(RemapError::NonFiniteState {
                source: 0,
                component,
            });
        }
    }
    let m = unpack9(packed);
    validate_source_coherency(&m, from, 0, options)?;
    let (transported, _, _) = transport_validated(&m, from, to, options, Some(0))?;
    let projected = project_matrix(&transported, to);
    validate_output_coherency(&projected, to, options)?;
    Ok(pack9(&projected))
}

pub fn remap_convex_packed(
    source_directions: &[[f64; 3]],
    source_states: &[[f64; 9]],
    weights: &[f64],
    target_direction: [f64; 3],
    options: RemapOptions,
) -> Result<RemapOutput, RemapError> {
    validate_options(options)?;
    if source_directions.is_empty() {
        return Err(RemapError::EmptyStencil);
    }
    if source_directions.len() != source_states.len() || source_directions.len() != weights.len() {
        return Err(RemapError::DimensionMismatch {
            directions: source_directions.len(),
            states: source_states.len(),
            weights: weights.len(),
        });
    }
    let target = validate_direction(target_direction, None, options)?;
    let mut weight_sum = 0.0_f64;
    let mut weight_compensation = 0.0_f64;
    for (index, weight) in weights.iter().copied().enumerate() {
        if !weight.is_finite() {
            return Err(RemapError::NonFiniteWeight { index });
        }
        if weight < 0.0 {
            return Err(RemapError::NegativeWeight {
                index,
                value: weight,
            });
        }
        let tentative = weight_sum + weight;
        if weight_sum.abs() >= weight.abs() {
            weight_compensation += (weight_sum - tentative) + weight;
        } else {
            weight_compensation += (weight - tentative) + weight_sum;
        }
        weight_sum = tentative;
    }
    weight_sum += weight_compensation;
    if !weight_sum.is_finite() || (weight_sum - 1.0).abs() > options.weight_tolerance {
        return Err(RemapError::WeightSum { sum: weight_sum });
    }
    let inv_sum = 1.0 / weight_sum;
    let mut accum = [[0.0; 3]; 3];
    let mut max_input_screen_leakage = 0.0_f64;
    let mut minimum_transport_dot = 1.0_f64;

    for index in 0..source_directions.len() {
        let direction = validate_direction(source_directions[index], Some(index), options)?;
        for (component, value) in source_states[index].iter().copied().enumerate() {
            if !value.is_finite() {
                return Err(RemapError::NonFiniteState {
                    source: index,
                    component,
                });
            }
        }
        let m = unpack9(&source_states[index]);
        let (leakage, _) = validate_source_coherency(&m, direction, index, options)?;
        let (transported, transport_dot, _) =
            transport_validated(&m, direction, target, options, Some(index))?;
        max_input_screen_leakage = max_input_screen_leakage.max(leakage);
        minimum_transport_dot = minimum_transport_dot.min(transport_dot);
        let w = weights[index] * inv_sum;
        for i in 0..3 {
            for j in 0..3 {
                accum[i][j] = w.mul_add(transported[i][j], accum[i][j]);
            }
        }
    }

    if !accum.iter().flatten().all(|x| x.is_finite()) {
        return Err(RemapError::AccumulationArithmeticNonFinite);
    }
    let projected = project_matrix(&accum, target);
    let (output_screen_leakage, _) = validate_output_coherency(&projected, target, options)?;
    Ok(RemapOutput {
        packed: pack9(&projected),
        diagnostics: RemapDiagnostics {
            weight_sum,
            max_input_screen_leakage,
            output_screen_leakage,
            minimum_transport_dot,
        },
    })
}
