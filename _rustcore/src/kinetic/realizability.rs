//! Necessary finite-moment checks from Dossier I §8.1, equations (64)–(68).
//!
//! `rho`, `q`, and `s` share energy-density units and velocities are divided by
//! the speed of light. A passing diagnostic does not establish realizability of
//! higher moments or construct a distribution. Caller data are never projected.

use nalgebra::{Matrix4, SymmetricEigen};

/// The trace constraint appropriate to the supplied species.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum MomentKind {
    /// Every particle has unit speed, so `tr S = rho`.
    Photons,
    /// Particle speeds are at most one, so `0 <= tr S <= rho`.
    MassiveOrMixed,
}

/// Invalid numerical control or nonfinite supplied moments.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum MomentError {
    InvalidTolerance,
    NonfiniteMoment,
}

impl std::fmt::Display for MomentError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{self:?}")
    }
}

impl std::error::Error for MomentError {}

/// Diagnostics in units of the largest absolute supplied matrix entry.
///
/// `min_eigenvalue_normalized` is the smallest eigenvalue of the symmetric
/// normalized joint matrix. It is `None` when the supplied stress is too
/// asymmetric to assign a symmetric-matrix eigenvalue. For symmetric input,
/// the eigensolver sees the arithmetic mean of opposite stress entries only
/// after their symmetry residual passes the requested tolerance.
#[derive(Clone, Copy, Debug)]
pub struct MomentDiagnostic {
    pub admissible: bool,
    pub min_eigenvalue_normalized: Option<f64>,
    pub trace_normalized: f64,
    pub symmetry_residual_normalized: f64,
}

/// Check necessary positivity and trace constraints without dividing by `rho`.
///
/// `relative_tolerance` is a finite, nonnegative numerical allowance in
/// normalized units, capped at `1e-6` so it cannot mask a material violation.
/// At exactly zero density, flux and stress must be exactly zero regardless of
/// tolerance. Finite but physically invalid moments return a negative verdict.
pub fn check_moments(
    rho: f64,
    q: [f64; 3],
    s: [[f64; 3]; 3],
    kind: MomentKind,
    relative_tolerance: f64,
) -> Result<MomentDiagnostic, MomentError> {
    if !relative_tolerance.is_finite() || !(0.0..=1e-6).contains(&relative_tolerance) {
        return Err(MomentError::InvalidTolerance);
    }
    if !rho.is_finite()
        || q.iter().any(|v| !v.is_finite())
        || s.iter().flatten().any(|v| !v.is_finite())
    {
        return Err(MomentError::NonfiniteMoment);
    }

    let mut scale = rho.abs();
    for &v in &q {
        scale = scale.max(v.abs());
    }
    for &v in s.iter().flatten() {
        scale = scale.max(v.abs());
    }
    if scale == 0.0 {
        return Ok(MomentDiagnostic {
            admissible: true,
            min_eigenvalue_normalized: Some(0.0),
            trace_normalized: 0.0,
            symmetry_residual_normalized: 0.0,
        });
    }

    let rn = rho / scale;
    let qn = q.map(|v| v / scale);
    let sn = s.map(|row| row.map(|v| v / scale));
    let trace = sn[0][0] + sn[1][1] + sn[2][2];
    let mut symmetry_residual = 0.0_f64;
    for (i, row) in sn.iter().enumerate() {
        for (j, other_row) in sn.iter().enumerate().skip(i + 1) {
            symmetry_residual = symmetry_residual.max((row[j] - other_row[i]).abs());
        }
    }
    let symmetric = symmetry_residual <= relative_tolerance;
    let min_eigenvalue = if symmetric {
        let mut joint = Matrix4::<f64>::zeros();
        joint[(0, 0)] = rn;
        for i in 0..3 {
            joint[(0, i + 1)] = qn[i];
            joint[(i + 1, 0)] = qn[i];
            for j in 0..3 {
                joint[(i + 1, j + 1)] = if i == j {
                    sn[i][j]
                } else {
                    // Only numerical asymmetry within tolerance is averaged.
                    0.5 * sn[i][j] + 0.5 * sn[j][i]
                };
            }
        }
        Some(
            SymmetricEigen::new(joint)
                .eigenvalues
                .iter()
                .copied()
                .fold(f64::INFINITY, f64::min),
        )
    } else {
        None
    };
    let vacuum_ok =
        rho != 0.0 || (q.iter().all(|&v| v == 0.0) && s.iter().flatten().all(|&v| v == 0.0));
    let trace_ok = trace >= -relative_tolerance
        && trace <= rn + relative_tolerance
        && (kind != MomentKind::Photons || (trace - rn).abs() <= relative_tolerance);
    Ok(MomentDiagnostic {
        admissible: vacuum_ok
            && rho >= 0.0
            && symmetric
            && trace_ok
            && min_eigenvalue.is_some_and(|v| v >= -relative_tolerance),
        min_eigenvalue_normalized: min_eigenvalue,
        trace_normalized: trace,
        symmetry_residual_normalized: symmetry_residual,
    })
}
