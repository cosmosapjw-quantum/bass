//! Moving-support implicit KL derivative, inherited from the admitted S8 math.
//! This differentiates the smooth ideal positive P24 optimum at the stored
//! approximate solution. It does not differentiate binary64 stopping decisions.
use crate::core::{Cohort, Error, ordered_sum};

pub const COV_MIN_EIGENVALUE: f64 = 1e-10;
pub const COV_MAX_CONDITION: f64 = 1e8;
pub const TANGENT_MOMENT_ATOL: f64 = 1e-11;
pub const NORMALIZATION_DERIVATIVE_ATOL: f64 = 1e-12;

#[derive(Clone, Debug)]
#[cfg_attr(feature = "history", derive(serde::Serialize, serde::Deserialize))]
pub struct KlDiagnostics {
    pub lambda_b: [f64; 2],
    pub covariance: [[f64; 2]; 2],
    pub covariance_eigenvalues: [f64; 2],
    pub covariance_condition: f64,
    pub nonlinear_feature_mean_f64: [f64; 2],
    pub normalization_derivative: f64,
    pub moment_derivative_residual: [f64; 2],
    pub linear_solve_residual: [f64; 2],
}

#[derive(Clone, Debug)]
#[cfg_attr(feature = "history", derive(serde::Serialize, serde::Deserialize))]
pub struct Differential {
    pub mu_b: Vec<f64>,
    pub alpha_b: Vec<f64>,
    pub diagnostics: KlDiagnostics,
}

pub fn implicit_p24(
    mu: &[f64],
    prior: &[f64],
    alpha: &[f64],
    multipliers: &[f64],
) -> Result<Differential, Error> {
    let n = mu.len();
    if prior.len() != n
        || alpha.len() != n
        || multipliers.len() != 2
        || multipliers.iter().any(|v| !v.is_finite())
        || prior.iter().any(|v| !v.is_finite() || *v <= 0.0)
        || prior.iter().zip(prior.iter().rev()).any(|(a, b)| a != b)
    {
        return Err(Error::new(
            "KL_DERIVATIVE_INPUT",
            "positive mirrored prior and two finite multipliers required",
        ));
    }
    Cohort {
        u: 0.0,
        b_birth: 0.0,
        energy_birth: 1.0,
        memory_theta: 0.0,
        mu: mu.to_vec(),
        alpha: alpha.to_vec(),
        mu_theta: vec![0.0; n],
        alpha_theta: vec![0.0; n],
    }
    .validate()?;
    let mass = ordered_sum(alpha.iter().copied());
    let qmass = ordered_sum(prior.iter().copied());
    if !qmass.is_finite() || qmass <= 0.0 {
        return Err(Error::new(
            "KL_DERIVATIVE_PRIOR_MASS",
            "finite positive prior mass required",
        ));
    }
    let mut features = Vec::with_capacity(n);
    let mut feature_b = Vec::with_capacity(n);
    let mut mu_b = Vec::with_capacity(n);
    for &m in mu {
        let z = m * m;
        let mb = -3.0 * m * (1.0 - z);
        mu_b.push(mb);
        features.push([(3.0 * z - 1.0) / 2.0, (35.0 * z * z - 30.0 * z + 3.0) / 8.0]);
        feature_b.push([3.0 * m * mb, (35.0 * m * m * m - 15.0 * m) * mb / 2.0]);
    }
    let mean: [f64; 2] =
        std::array::from_fn(|j| ordered_sum((0..n).map(|i| alpha[i] * features[i][j])) / mass);
    let qmean = ordered_sum((0..n).map(|i| prior[i] * features[i][0])) / qmass;
    let centered: Vec<[f64; 2]> = features
        .iter()
        .map(|f| [f[0] - mean[0], f[1] - mean[1]])
        .collect();
    let cross = ordered_sum((0..n).map(|i| alpha[i] * centered[i][0] * centered[i][1])) / mass;
    let covariance = [
        [
            ordered_sum((0..n).map(|i| alpha[i] * centered[i][0] * centered[i][0])) / mass,
            cross,
        ],
        [
            cross,
            ordered_sum((0..n).map(|i| alpha[i] * centered[i][1] * centered[i][1])) / mass,
        ],
    ];
    let local_score: Vec<f64> = (0..n)
        .map(|i| {
            6.0 * (features[i][0] - qmean)
                + multipliers[0] * feature_b[i][0]
                + multipliers[1] * feature_b[i][1]
        })
        .collect();
    let score_mean = ordered_sum((0..n).map(|i| alpha[i] * local_score[i])) / mass;
    let mean_fb: [f64; 2] =
        std::array::from_fn(|j| ordered_sum((0..n).map(|i| alpha[i] * feature_b[i][j])) / mass);
    let cov_fa: [f64; 2] = std::array::from_fn(|j| {
        ordered_sum((0..n).map(|i| alpha[i] * centered[i][j] * (local_score[i] - score_mean)))
            / mass
    });
    let rhs = [-mean_fb[0] - cov_fa[0], -mean_fb[1] - cov_fa[1]];

    let a = covariance[0][0];
    let c = covariance[1][1];
    let maximum = (a + c + (a - c).hypot(2.0 * cross)) / 2.0;
    let determinant = a * c - cross * cross;
    let minimum = determinant / maximum;
    let condition = maximum / minimum;
    if covariance
        .iter()
        .flatten()
        .chain(rhs.iter())
        .any(|v| !v.is_finite())
        || !maximum.is_finite()
        || !minimum.is_finite()
        || !condition.is_finite()
        || minimum < COV_MIN_EIGENVALUE
        || condition > COV_MAX_CONDITION
        || a <= 0.0
        || determinant <= 0.0
    {
        return Err(Error::new(
            "KL_COVARIANCE_RANK_OR_CONDITION",
            format!("eigenvalues=[{minimum:.17e},{maximum:.17e}], condition={condition:.17e}"),
        ));
    }
    let l00 = a.sqrt();
    let l10 = cross / l00;
    let diagonal = c - l10 * l10;
    if diagonal <= 0.0 || !diagonal.is_finite() {
        return Err(Error::new(
            "KL_COVARIANCE_CHOLESKY",
            "positive Cholesky pivot required; no clipping or pseudoinverse",
        ));
    }
    let l11 = diagonal.sqrt();
    let v0 = rhs[0] / l00;
    let v1 = (rhs[1] - l10 * v0) / l11;
    let lambda_b1 = v1 / l11;
    let lambda_b0 = (v0 - l10 * lambda_b1) / l00;
    let lambda_b = [lambda_b0, lambda_b1];
    let alpha_b: Vec<f64> = (0..n)
        .map(|i| {
            alpha[i]
                * (local_score[i] - score_mean
                    + centered[i][0] * lambda_b[0]
                    + centered[i][1] * lambda_b[1])
        })
        .collect();
    let normalization_derivative = ordered_sum(alpha_b.iter().copied());
    let moment_derivative_residual: [f64; 2] = std::array::from_fn(|j| {
        ordered_sum((0..n).map(|i| alpha_b[i] * features[i][j] + alpha[i] * feature_b[i][j]))
    });
    let linear_solve_residual = [
        a * lambda_b0 + cross * lambda_b1 - rhs[0],
        cross * lambda_b0 + c * lambda_b1 - rhs[1],
    ];
    if alpha_b
        .iter()
        .chain(mu_b.iter())
        .chain(lambda_b.iter())
        .chain(moment_derivative_residual.iter())
        .chain(linear_solve_residual.iter())
        .any(|v| !v.is_finite())
        || !normalization_derivative.is_finite()
        || normalization_derivative.abs() > NORMALIZATION_DERIVATIVE_ATOL
        || moment_derivative_residual
            .iter()
            .any(|v| v.abs() > TANGENT_MOMENT_ATOL)
    {
        return Err(Error::new(
            "KL_DERIVATIVE_RESIDUAL",
            format!(
                "normalization={normalization_derivative:.17e}, moments={moment_derivative_residual:?}"
            ),
        ));
    }
    if mu_b.iter().zip(mu_b.iter().rev()).any(|(a, b)| *a != -*b)
        || alpha_b
            .iter()
            .zip(alpha_b.iter().rev())
            .any(|(a, b)| a != b)
    {
        return Err(Error::new(
            "KL_DERIVATIVE_REFLECTION",
            "implicit derivative lost exact parity",
        ));
    }
    Ok(Differential {
        mu_b,
        alpha_b,
        diagnostics: KlDiagnostics {
            lambda_b,
            covariance,
            covariance_eigenvalues: [minimum, maximum],
            covariance_condition: condition,
            nonlinear_feature_mean_f64: mean,
            normalization_derivative,
            moment_derivative_residual,
            linear_solve_residual,
        },
    })
}
