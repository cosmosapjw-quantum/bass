//! Type-II polarized Liouville characteristic reference lane.
//!
//! This module advances one homogeneous photon characteristic together with a
//! basis-free screen coherency tensor.  It deliberately stops before angular
//! remapping, PSTF/harmonic projection, collision composition, or observables.
//! The physical tensor carrier is inherited from `typeii_physical_guard`.

use super::typeii_physical_guard::{
    enforce_screen_state, max_screen_leakage, minimum_coherency_eigenvalue, project_screen_state,
    PhysicalCarrierError, ScreenInputPolicy,
};

pub type Mat3 = [[f64; 3]; 3];

pub const TYPEII_DIAGONAL_GAUGE_TOLERANCE: f64 = 1e-12;
pub const GEOMETRIC_TENSOR_TOLERANCE: f64 = 1e-10;

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct HomogeneousRayBackground {
    pub expansion: f64,
    pub shear: Mat3,
    pub structure_n: Mat3,
    pub class_b_a: [f64; 3],
    pub triad_rotation: [f64; 3],
}

impl HomogeneousRayBackground {
    pub const fn zero() -> Self {
        Self {
            expansion: 0.0,
            shear: [[0.0; 3]; 3],
            structure_n: [[0.0; 3]; 3],
            class_b_a: [0.0; 3],
            triad_rotation: [0.0; 3],
        }
    }

    fn lerp(&self, other: &Self, fraction: f64) -> Self {
        let mix = |a: f64, b: f64| a + fraction * (b - a);
        let mut out = Self::zero();
        out.expansion = mix(self.expansion, other.expansion);
        for i in 0..3 {
            out.class_b_a[i] = mix(self.class_b_a[i], other.class_b_a[i]);
            out.triad_rotation[i] = mix(self.triad_rotation[i], other.triad_rotation[i]);
            for j in 0..3 {
                out.shear[i][j] = mix(self.shear[i][j], other.shear[i][j]);
                out.structure_n[i][j] = mix(self.structure_n[i][j], other.structure_n[i][j]);
            }
        }
        out
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct LiouvilleCoefficients {
    pub direction_rate: [f64; 3],
    pub log_energy_rate: f64,
    pub log_bolometric_rate: f64,
    /// Angular velocity whose cross-product matrix transports the spatial
    /// screen tensor components in the declared tetrad gauge.
    pub transport_angular_velocity: [f64; 3],
    /// `omega_scr = e.W`; exposed as a diagnostic/adapter.  This first slice
    /// does not lower it to a sign-sensitive Q/U component convention.
    pub screen_connection_rate: f64,
}

#[derive(Clone, Debug, PartialEq)]
pub enum PolarizedLiouvilleError {
    Carrier(PhysicalCarrierError),
    InvalidSubsteps {
        requested: usize,
    },
    NonFiniteStep {
        step: f64,
    },
    NonFiniteBackground {
        endpoint: usize,
        index: usize,
    },
    InvalidDirection {
        norm_squared: f64,
    },
    BackgroundContractViolation {
        field: &'static str,
        defect: f64,
        tolerance: f64,
    },
    NonFiniteCoefficient,
    NonFiniteOutput {
        index: usize,
    },
    MidpointDidNotConverge {
        substep: usize,
        residual: f64,
    },
    DegenerateTypeIIGauge {
        n1: f64,
        sigma_13: f64,
        tolerance: f64,
    },
}

#[derive(Clone, Debug)]
pub struct PolarizedCharacteristicResult {
    pub direction: [f64; 3],
    pub coherency: Vec<f64>,
    pub log_energy_shift: f64,
    pub log_bolometric_shift: f64,
    pub screen_connection_integral: f64,
    /// Proper spatial transport accumulated from the initial tetrad components
    /// to the final tetrad components.  Its restriction to the photon screen is
    /// the physical SO(2) holonomy.
    pub spatial_transport: Mat3,
    pub transport_orthogonality_defect: f64,
    pub transport_determinant_defect: f64,
    pub max_screen_leakage: f64,
    pub minimum_coherency_eigenvalue: f64,
}

#[inline]
fn dot(a: [f64; 3], b: [f64; 3]) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
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
fn add(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [a[0] + b[0], a[1] + b[1], a[2] + b[2]]
}

#[inline]
fn scale(a: [f64; 3], factor: f64) -> [f64; 3] {
    [factor * a[0], factor * a[1], factor * a[2]]
}

#[inline]
fn mat_vec(matrix: &Mat3, vector: [f64; 3]) -> [f64; 3] {
    [
        dot(matrix[0], vector),
        dot(matrix[1], vector),
        dot(matrix[2], vector),
    ]
}

#[inline]
fn transpose(matrix: &Mat3) -> Mat3 {
    let mut out = [[0.0; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            out[i][j] = matrix[j][i];
        }
    }
    out
}

#[inline]
fn mm(left: &Mat3, right: &Mat3) -> Mat3 {
    let mut out = [[0.0; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            for k in 0..3 {
                out[i][j] += left[i][k] * right[k][j];
            }
        }
    }
    out
}

#[inline]
fn identity3() -> Mat3 {
    [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
}

#[inline]
fn determinant3(matrix: &Mat3) -> f64 {
    matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
}

#[inline]
fn orthogonality_defect(matrix: &Mat3) -> f64 {
    let gram = mm(&transpose(matrix), matrix);
    let mut defect = 0.0_f64;
    for i in 0..3 {
        for j in 0..3 {
            let expected = if i == j { 1.0 } else { 0.0 };
            defect = defect.max((gram[i][j] - expected).abs());
        }
    }
    defect
}

#[inline]
fn unpack9(packed: &[f64]) -> Mat3 {
    [
        [packed[0], packed[3] + packed[8], packed[4] - packed[7]],
        [packed[3] - packed[8], packed[1], packed[5] + packed[6]],
        [packed[4] + packed[7], packed[5] - packed[6], packed[2]],
    ]
}

#[inline]
fn pack9(matrix: &Mat3) -> [f64; 9] {
    [
        matrix[0][0],
        matrix[1][1],
        matrix[2][2],
        0.5 * (matrix[0][1] + matrix[1][0]),
        0.5 * (matrix[0][2] + matrix[2][0]),
        0.5 * (matrix[1][2] + matrix[2][1]),
        0.5 * (matrix[1][2] - matrix[2][1]),
        0.5 * (matrix[2][0] - matrix[0][2]),
        0.5 * (matrix[0][1] - matrix[1][0]),
    ]
}

fn validate_background(
    background: &HomogeneousRayBackground,
    endpoint: usize,
) -> Result<(), PolarizedLiouvilleError> {
    let mut values = Vec::with_capacity(25);
    values.push(background.expansion);
    for row in background.shear {
        values.extend(row);
    }
    for row in background.structure_n {
        values.extend(row);
    }
    values.extend(background.class_b_a);
    values.extend(background.triad_rotation);
    if let Some(index) = values.iter().position(|value| !value.is_finite()) {
        return Err(PolarizedLiouvilleError::NonFiniteBackground { endpoint, index });
    }
    let shear_trace = background.shear[0][0] + background.shear[1][1] + background.shear[2][2];
    if shear_trace.abs() > GEOMETRIC_TENSOR_TOLERANCE {
        return Err(PolarizedLiouvilleError::BackgroundContractViolation {
            field: "shear_trace",
            defect: shear_trace.abs(),
            tolerance: GEOMETRIC_TENSOR_TOLERANCE,
        });
    }
    let mut shear_asymmetry = 0.0_f64;
    let mut n_asymmetry = 0.0_f64;
    for i in 0..3 {
        for j in 0..3 {
            shear_asymmetry =
                shear_asymmetry.max((background.shear[i][j] - background.shear[j][i]).abs());
            n_asymmetry = n_asymmetry
                .max((background.structure_n[i][j] - background.structure_n[j][i]).abs());
        }
    }
    if shear_asymmetry > GEOMETRIC_TENSOR_TOLERANCE {
        return Err(PolarizedLiouvilleError::BackgroundContractViolation {
            field: "shear_symmetry",
            defect: shear_asymmetry,
            tolerance: GEOMETRIC_TENSOR_TOLERANCE,
        });
    }
    if n_asymmetry > GEOMETRIC_TENSOR_TOLERANCE {
        return Err(PolarizedLiouvilleError::BackgroundContractViolation {
            field: "structure_n_symmetry",
            defect: n_asymmetry,
            tolerance: GEOMETRIC_TENSOR_TOLERANCE,
        });
    }
    Ok(())
}

#[inline]
fn normalize(direction: [f64; 3]) -> [f64; 3] {
    let norm = dot(direction, direction).sqrt();
    scale(direction, 1.0 / norm)
}

#[inline]
fn checked_normalize(direction: [f64; 3]) -> Result<[f64; 3], PolarizedLiouvilleError> {
    let norm_squared = dot(direction, direction);
    if !norm_squared.is_finite() || norm_squared <= 0.0 {
        return Err(PolarizedLiouvilleError::InvalidDirection { norm_squared });
    }
    Ok(scale(direction, 1.0 / norm_squared.sqrt()))
}

/// Convert the generated Hubble-normalized Type-II chart
/// `(Sigma_+,Sigma_-,Sigma_13,N1,v2)` to the homogeneous ray coefficients.
/// `v2` is validated as part of the state but does not enter geometric
/// Liouville transport; it remains a global-electron/collision variable.
pub fn typeii_background_from_state(
    state: &[f64; 5],
) -> Result<HomogeneousRayBackground, PolarizedLiouvilleError> {
    if let Some(index) = state.iter().position(|value| !value.is_finite()) {
        return Err(PolarizedLiouvilleError::NonFiniteBackground { endpoint: 0, index });
    }
    let sqrt3 = 3.0_f64.sqrt();
    let sigma_p = state[0];
    let sigma_m = state[1];
    let sigma_13 = state[2];
    let n1 = state[3];
    let triad_rotation_y = if n1.abs() <= TYPEII_DIAGONAL_GAUGE_TOLERANCE {
        if sigma_13.abs() > TYPEII_DIAGONAL_GAUGE_TOLERANCE {
            return Err(PolarizedLiouvilleError::DegenerateTypeIIGauge {
                n1,
                sigma_13,
                tolerance: TYPEII_DIAGONAL_GAUGE_TOLERANCE,
            });
        }
        0.0
    } else {
        sqrt3 * sigma_13
    };
    Ok(HomogeneousRayBackground {
        expansion: 1.0,
        shear: [
            [-2.0 * sigma_p, 0.0, sqrt3 * sigma_13],
            [0.0, sigma_p + sqrt3 * sigma_m, 0.0],
            [sqrt3 * sigma_13, 0.0, sigma_p - sqrt3 * sigma_m],
        ],
        structure_n: [[n1, 0.0, 0.0], [0.0; 3], [0.0; 3]],
        class_b_a: [0.0; 3],
        // Co-rotating diagonal-n Type-II adapter: Omega_2 = Sigma_13(tensor).
        triad_rotation: [0.0, triad_rotation_y, 0.0],
    })
}

pub fn liouville_coefficients(
    direction: [f64; 3],
    background: &HomogeneousRayBackground,
) -> Result<LiouvilleCoefficients, PolarizedLiouvilleError> {
    validate_background(background, 0)?;
    let direction = checked_normalize(direction)?;
    let shear_e = mat_vec(&background.shear, direction);
    let shear_ee = dot(direction, shear_e);
    let shear_direction = add(scale(shear_e, -1.0), scale(direction, shear_ee));

    let n_e = mat_vec(&background.structure_n, direction);
    let tr_n =
        background.structure_n[0][0] + background.structure_n[1][1] + background.structure_n[2][2];
    let w = add(
        add(
            background.triad_rotation,
            cross(background.class_b_a, direction),
        ),
        add(n_e, scale(direction, -0.5 * tr_n)),
    );
    let transport_angular_velocity = add(w, cross(direction, shear_direction));
    let direction_rate = cross(transport_angular_velocity, direction);
    let log_energy_rate = -(background.expansion + shear_ee);
    let coefficients = LiouvilleCoefficients {
        direction_rate,
        log_energy_rate,
        log_bolometric_rate: 4.0 * log_energy_rate,
        transport_angular_velocity,
        screen_connection_rate: dot(direction, w),
    };
    let finite = coefficients
        .direction_rate
        .into_iter()
        .chain(coefficients.transport_angular_velocity)
        .chain([
            coefficients.log_energy_rate,
            coefficients.log_bolometric_rate,
            coefficients.screen_connection_rate,
        ])
        .all(f64::is_finite);
    if !finite {
        return Err(PolarizedLiouvilleError::NonFiniteCoefficient);
    }
    Ok(coefficients)
}

fn rotation_from_vector(rotation_vector: [f64; 3]) -> Mat3 {
    let theta2 = dot(rotation_vector, rotation_vector);
    let theta = theta2.sqrt();
    let (sinc, cosc) = if theta < 1e-7 {
        let theta4 = theta2 * theta2;
        (
            1.0 - theta2 / 6.0 + theta4 / 120.0,
            0.5 - theta2 / 24.0 + theta4 / 720.0,
        )
    } else {
        (theta.sin() / theta, (1.0 - theta.cos()) / theta2)
    };
    let [x, y, z] = rotation_vector;
    let k = [[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]];
    let k2 = mm(&k, &k);
    let mut out = [[0.0; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            out[i][j] = if i == j { 1.0 } else { 0.0 } + sinc * k[i][j] + cosc * k2[i][j];
        }
    }
    out
}

fn congruence(rotation: &Mat3, matrix: &Mat3) -> Mat3 {
    mm(&mm(rotation, matrix), &transpose(rotation))
}

/// Instantaneous bolometric tensor RHS in the tetrad representation.
pub fn polarized_bolometric_rhs(
    direction: [f64; 3],
    background: &HomogeneousRayBackground,
    coherency: &[f64],
    input_policy: ScreenInputPolicy,
) -> Result<([f64; 3], Vec<f64>, LiouvilleCoefficients), PolarizedLiouvilleError> {
    let physical = enforce_screen_state(&[direction], coherency, input_policy)
        .map_err(PolarizedLiouvilleError::Carrier)?;
    let coefficients = liouville_coefficients(direction, background)?;
    let matrix = unpack9(&physical);
    let g = coefficients.transport_angular_velocity;
    let k = [[0.0, -g[2], g[1]], [g[2], 0.0, -g[0]], [-g[1], g[0], 0.0]];
    let mut rhs = mm(&k, &matrix);
    let right = mm(&matrix, &transpose(&k));
    for i in 0..3 {
        for j in 0..3 {
            rhs[i][j] += right[i][j] + coefficients.log_bolometric_rate * matrix[i][j];
        }
    }
    Ok((
        coefficients.direction_rate,
        pack9(&rhs).to_vec(),
        coefficients,
    ))
}

#[allow(clippy::too_many_arguments)]
pub fn transport_characteristic_profile<F>(
    direction: [f64; 3],
    step: f64,
    substeps: usize,
    coherency: &[f64],
    input_policy: ScreenInputPolicy,
    background_at_fraction: F,
) -> Result<PolarizedCharacteristicResult, PolarizedLiouvilleError>
where
    F: Fn(f64) -> HomogeneousRayBackground,
{
    if !step.is_finite() {
        return Err(PolarizedLiouvilleError::NonFiniteStep { step });
    }
    if substeps == 0 {
        return Err(PolarizedLiouvilleError::InvalidSubsteps { requested: 0 });
    }
    validate_background(&background_at_fraction(0.0), 0)?;
    validate_background(&background_at_fraction(1.0), 1)?;
    let mut direction = checked_normalize(direction)?;
    let physical = enforce_screen_state(&[direction], coherency, input_policy)
        .map_err(PolarizedLiouvilleError::Carrier)?;
    let mut matrix = unpack9(&physical);
    let mut spatial_transport = identity3();
    let h = step / substeps as f64;
    let mut log_energy_shift = 0.0;
    let mut screen_connection_integral = 0.0;

    for substep in 0..substeps {
        let fraction_mid = (substep as f64 + 0.5) / substeps as f64;
        let background_mid = background_at_fraction(fraction_mid);
        validate_background(&background_mid, substep + 2)?;

        // Lie-group implicit midpoint.  The fixed point
        // e_m = exp[(h/2) Omega(e_m)] e_n makes the accepted rotation
        // self-adjoint under h -> -h for the same midpoint background.
        let first = liouville_coefficients(direction, &background_mid)?;
        let half_rotation = rotation_from_vector(scale(first.transport_angular_velocity, 0.5 * h));
        let mut direction_mid = normalize(mat_vec(&half_rotation, direction));
        let mut residual = f64::INFINITY;
        for _ in 0..32 {
            let midpoint_trial = liouville_coefficients(direction_mid, &background_mid)?;
            let trial_rotation =
                rotation_from_vector(scale(midpoint_trial.transport_angular_velocity, 0.5 * h));
            let candidate = normalize(mat_vec(&trial_rotation, direction));
            residual = candidate
                .iter()
                .zip(direction_mid)
                .map(|(a, b)| (a - b).abs())
                .fold(0.0, f64::max);
            direction_mid = candidate;
            if residual <= 8e-15 {
                break;
            }
        }
        if residual > 2e-13 {
            return Err(PolarizedLiouvilleError::MidpointDidNotConverge { substep, residual });
        }
        let midpoint = liouville_coefficients(direction_mid, &background_mid)?;
        let rotation = rotation_from_vector(scale(midpoint.transport_angular_velocity, h));
        direction = normalize(mat_vec(&rotation, direction));
        spatial_transport = mm(&rotation, &spatial_transport);

        let delta_log_energy = h * midpoint.log_energy_rate;
        let bolometric_factor = (4.0 * delta_log_energy).exp();
        matrix = congruence(&rotation, &matrix);
        for row in &mut matrix {
            for value in row {
                *value *= bolometric_factor;
            }
        }
        log_energy_shift += delta_log_energy;
        screen_connection_integral += h * midpoint.screen_connection_rate;
    }

    let packed = pack9(&matrix).to_vec();
    if let Some(index) = packed.iter().position(|value| !value.is_finite()) {
        return Err(PolarizedLiouvilleError::NonFiniteOutput { index });
    }
    let coherency =
        project_screen_state(&[direction], &packed).map_err(PolarizedLiouvilleError::Carrier)?;
    let leakage =
        max_screen_leakage(&[direction], &coherency).map_err(PolarizedLiouvilleError::Carrier)?;
    let minimum_eigenvalue = minimum_coherency_eigenvalue(&[direction], &coherency)
        .map_err(PolarizedLiouvilleError::Carrier)?;
    Ok(PolarizedCharacteristicResult {
        direction,
        coherency,
        log_energy_shift,
        log_bolometric_shift: 4.0 * log_energy_shift,
        screen_connection_integral,
        spatial_transport,
        transport_orthogonality_defect: orthogonality_defect(&spatial_transport),
        transport_determinant_defect: (determinant3(&spatial_transport) - 1.0).abs(),
        max_screen_leakage: leakage,
        minimum_coherency_eigenvalue: minimum_eigenvalue,
    })
}

#[allow(clippy::too_many_arguments)]
pub fn transport_characteristic(
    direction: [f64; 3],
    background_start: &HomogeneousRayBackground,
    background_end: &HomogeneousRayBackground,
    step: f64,
    substeps: usize,
    coherency: &[f64],
    input_policy: ScreenInputPolicy,
) -> Result<PolarizedCharacteristicResult, PolarizedLiouvilleError> {
    validate_background(background_start, 0)?;
    validate_background(background_end, 1)?;
    transport_characteristic_profile(
        direction,
        step,
        substeps,
        coherency,
        input_policy,
        |fraction| background_start.lerp(background_end, fraction),
    )
}

#[allow(clippy::too_many_arguments)]
pub fn transport_typeii_characteristic(
    direction: [f64; 3],
    state_start: &[f64; 5],
    state_end: &[f64; 5],
    step: f64,
    substeps: usize,
    coherency: &[f64],
    input_policy: ScreenInputPolicy,
) -> Result<PolarizedCharacteristicResult, PolarizedLiouvilleError> {
    let background_start = typeii_background_from_state(state_start)?;
    let background_end = typeii_background_from_state(state_end)?;
    transport_characteristic(
        direction,
        &background_start,
        &background_end,
        step,
        substeps,
        coherency,
        input_policy,
    )
}
