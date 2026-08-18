//! Matrix-free exponential/phi1 action backend for generated Type-II runtime kernels.
//! G-RUNTIME-KATO-II reference implementation.

use nalgebra::DMatrix;

#[derive(Clone, Copy, Debug)]
pub struct KrylovOptions {
    pub m_max: usize,
    pub tol: f64,
    pub max_splits: usize,
}

impl KrylovOptions {
    pub fn full(n: usize) -> Self {
        Self {
            m_max: n.max(1),
            tol: 5e-14,
            max_splits: 12,
        }
    }
}

#[derive(Debug, Clone)]
pub enum RuntimeError {
    DimensionMismatch,
    OperatorDimensionMismatch,
    SingularPadeSolve,
    KrylovDidNotConverge { estimate: f64 },
    SubspaceTooSmall { requested: usize, dimension: usize },
}

fn dot(a: &[f64], b: &[f64]) -> f64 {
    a.iter().zip(b).map(|(x, y)| x * y).sum()
}

fn norm2(a: &[f64]) -> f64 {
    dot(a, a).sqrt()
}

fn matrix_one_norm(a: &DMatrix<f64>) -> f64 {
    (0..a.ncols())
        .map(|j| (0..a.nrows()).map(|i| a[(i, j)].abs()).sum::<f64>())
        .fold(0.0, f64::max)
}

fn expm_pade13(a: &DMatrix<f64>) -> Result<DMatrix<f64>, RuntimeError> {
    assert_eq!(a.nrows(), a.ncols());
    let n = a.nrows();
    if n == 0 {
        return Ok(DMatrix::zeros(0, 0));
    }
    let theta13 = 5.371_920_351_148_152_f64;
    let norm = matrix_one_norm(a);
    let s = if norm <= theta13 || norm == 0.0 {
        0_u32
    } else {
        (norm / theta13).log2().ceil().max(0.0) as u32
    };
    let scale = 2_f64.powi(-(s as i32));
    let aa = a * scale;
    let eye = DMatrix::<f64>::identity(n, n);
    let a2 = &aa * &aa;
    let a4 = &a2 * &a2;
    let a6 = &a4 * &a2;
    let b = [
        64_764_752_532_480_000.0,
        32_382_376_266_240_000.0,
        7_771_770_303_897_600.0,
        1_187_353_796_428_800.0,
        129_060_195_264_000.0,
        10_559_470_521_600.0,
        670_442_572_800.0,
        33_522_128_640.0,
        1_323_241_920.0,
        40_840_800.0,
        960_960.0,
        16_380.0,
        182.0,
        1.0,
    ];

    let u_inner = &a6 * (&a6 * b[13] + &a4 * b[11] + &a2 * b[9])
        + &a6 * b[7]
        + &a4 * b[5]
        + &a2 * b[3]
        + &eye * b[1];
    let u = &aa * u_inner;
    let v = &a6 * (&a6 * b[12] + &a4 * b[10] + &a2 * b[8])
        + &a6 * b[6]
        + &a4 * b[4]
        + &a2 * b[2]
        + &eye * b[0];
    let p = &v + &u;
    let q = &v - &u;
    let mut r = q.lu().solve(&p).ok_or(RuntimeError::SingularPadeSolve)?;
    for _ in 0..s {
        r = &r * &r;
    }
    Ok(r)
}

fn arnoldi_once<F>(
    apply: &F,
    y: &[f64],
    t: f64,
    options: KrylovOptions,
) -> Result<(Vec<f64>, f64), RuntimeError>
where
    F: Fn(&[f64]) -> Vec<f64>,
{
    let n = y.len();
    if n == 0 {
        return Ok((Vec::new(), 0.0));
    }
    let beta = norm2(y);
    if beta == 0.0 || t == 0.0 {
        return Ok((y.to_vec(), 0.0));
    }
    let m_cap = options.m_max.max(1).min(n);
    let mut basis: Vec<Vec<f64>> = vec![y.iter().map(|x| x / beta).collect()];
    let mut hess = DMatrix::<f64>::zeros(m_cap + 1, m_cap);
    let mut k = 0usize;
    let mut residual_h = 0.0;

    for j in 0..m_cap {
        let mut w = apply(&basis[j]);
        if w.len() != n {
            return Err(RuntimeError::OperatorDimensionMismatch);
        }
        // Two-pass MGS for a stable small reference Arnoldi factorization.
        for _ in 0..2 {
            for i in 0..=j {
                let hij = dot(&basis[i], &w);
                hess[(i, j)] += hij;
                for r in 0..n {
                    w[r] -= hij * basis[i][r];
                }
            }
        }
        let hn = norm2(&w);
        hess[(j + 1, j)] = hn;
        k = j + 1;
        residual_h = hn;
        if hn <= options.tol || k == m_cap {
            break;
        }
        basis.push(w.into_iter().map(|x| x / hn).collect());
    }

    let hk = hess.view((0, 0), (k, k)).into_owned();
    let exp_h = expm_pade13(&(hk * t))?;
    let mut out = vec![0.0; n];
    for i in 0..k {
        let coeff = beta * exp_h[(i, 0)];
        for r in 0..n {
            out[r] += coeff * basis[i][r];
        }
    }

    let estimate = if k < hess.nrows() && residual_h > 0.0 {
        beta * residual_h * t.abs() * exp_h[(k - 1, 0)].abs()
    } else {
        0.0
    };
    Ok((out, estimate))
}

fn expm_action_split<F>(
    apply: &F,
    y: &[f64],
    t: f64,
    options: KrylovOptions,
    _depth: usize,
) -> Result<Vec<f64>, RuntimeError>
where
    F: Fn(&[f64]) -> Vec<f64>,
{
    // G-RUNTIME-KATO-II is a reference-level backend.  A truncated/restarted
    // Krylov basis is deliberately fail-closed until an adaptive phipm/KIOPS-
    // class error controller is implemented and independently verified.
    if options.m_max < y.len() {
        return Err(RuntimeError::SubspaceTooSmall {
            requested: options.m_max,
            dimension: y.len(),
        });
    }
    let (out, _) = arnoldi_once(apply, y, t, options)?;
    Ok(out)
}

pub fn expm_action<F>(
    apply: &F,
    y: &[f64],
    t: f64,
    options: KrylovOptions,
) -> Result<Vec<f64>, RuntimeError>
where
    F: Fn(&[f64]) -> Vec<f64>,
{
    expm_action_split(apply, y, t, options, 0)
}

pub fn phi1_action<F>(
    apply: &F,
    b: &[f64],
    t: f64,
    options: KrylovOptions,
) -> Result<Vec<f64>, RuntimeError>
where
    F: Fn(&[f64]) -> Vec<f64>,
{
    if t == 0.0 {
        return Ok(b.to_vec());
    }
    let n = b.len();
    let aug_apply = |z: &[f64]| -> Vec<f64> {
        assert_eq!(z.len(), n + 1);
        let mut top = apply(&z[..n]);
        assert_eq!(top.len(), n);
        let s = z[n];
        for i in 0..n {
            top[i] += b[i] * s;
        }
        top.push(0.0);
        top
    };
    let mut init = vec![0.0; n + 1];
    init[n] = 1.0;
    let aug_options = KrylovOptions {
        m_max: (options.m_max + 1).min(n + 1),
        ..options
    };
    let out = expm_action(&aug_apply, &init, t, aug_options)?;
    Ok(out[..n].iter().map(|x| x / t).collect())
}

pub fn transport_apply(
    directions: &[[f64; 3]],
    state: &[f64; 5],
    y: &[f64],
) -> Result<Vec<f64>, RuntimeError> {
    if directions.len() != y.len() {
        return Err(RuntimeError::DimensionMismatch);
    }
    let sigma_p = state[0];
    let sigma_m = state[1];
    let sigma_13 = state[2];
    let sqrt3 = 3.0_f64.sqrt();
    let s00 = -2.0 * sigma_p;
    let s11 = sigma_p + sqrt3 * sigma_m;
    let s22 = sigma_p - sqrt3 * sigma_m;
    let s02 = sqrt3 * sigma_13;
    Ok(directions
        .iter()
        .zip(y)
        .map(|(e, yi)| {
            let see =
                s00 * e[0] * e[0] + s11 * e[1] * e[1] + s22 * e[2] * e[2] + 2.0 * s02 * e[0] * e[2];
            -4.0 * (1.0 + see) * yi
        })
        .collect())
}

#[allow(clippy::too_many_arguments)]
pub fn kato_aem2_step(
    directions: &[[f64; 3]],
    weights: &[f64],
    axis: usize,
    gamma: f64,
    h: f64,
    opacity_scale: f64,
    state_q1: &[f64; 5],
    state_mid: &[f64; 5],
    state_q3: &[f64; 5],
    opacity_mid: f64,
    y: &[f64],
    options: KrylovOptions,
) -> Result<Vec<f64>, RuntimeError> {
    use super::typeii_background;
    use super::typeii_collision;
    use super::typeii_kato;

    if directions.len() != weights.len() || directions.len() != y.len() {
        return Err(RuntimeError::DimensionMismatch);
    }

    let vd1 = typeii_background::rhs(state_q1, gamma)[4];
    let k1 = |x: &[f64]| typeii_kato::kato_apply(directions, weights, state_q1[4], vd1, axis, x);
    let ym = expm_action(&k1, y, 0.5 * h, options)?;

    let vdm = typeii_background::rhs(state_mid, gamma)[4];
    let km = |x: &[f64]| typeii_kato::kato_apply(directions, weights, state_mid[4], vdm, axis, x);
    let aeff = |x: &[f64]| -> Vec<f64> {
        let mut a =
            transport_apply(directions, state_mid, x).expect("validated transport dimensions");
        let k = km(x);
        for i in 0..a.len() {
            a[i] -= k[i];
        }
        a
    };
    let collision_scale = opacity_scale * opacity_mid;
    let c = |x: &[f64]| -> Vec<f64> {
        typeii_collision::collision_generator_apply(directions, weights, state_mid[4], axis, x)
            .into_iter()
            .map(|z| collision_scale * z)
            .collect()
    };

    let e_half = expm_action(&c, &ym, 0.5 * h, options)?;
    let a_ybar = aeff(&e_half);
    let phi_half = phi1_action(&c, &a_ybar, 0.5 * h, options)?;
    let mut y_mid = e_half.clone();
    for i in 0..y_mid.len() {
        y_mid[i] += 0.5 * h * phi_half[i];
    }

    let e_full = expm_action(&c, &ym, h, options)?;
    let a_mid = aeff(&y_mid);
    let phi_full = phi1_action(&c, &a_mid, h, options)?;
    let mut y_tilde = e_full;
    for i in 0..y_tilde.len() {
        y_tilde[i] += h * phi_full[i];
    }

    let vd3 = typeii_background::rhs(state_q3, gamma)[4];
    let k3 = |x: &[f64]| typeii_kato::kato_apply(directions, weights, state_q3[4], vd3, axis, x);
    expm_action(&k3, &y_tilde, 0.5 * h, options)
}
