//! General-frame Codazzi diagnostic; no chart restriction or external dependencies.
//! Row-major tensors; epsilon_012 = +1. This is not an evolution kernel.

pub fn codazzi_residual(
    sigma: &[f64; 9],
    n: &[f64; 9],
    a: &[f64; 3],
    q_flux: &[f64; 3],
) -> Result<[f64; 3], &'static str> {
    if !sigma
        .iter()
        .chain(n)
        .chain(a)
        .chain(q_flux)
        .all(|x| x.is_finite())
    {
        return Err("Codazzi inputs must be finite");
    }
    let mut out = [0.0; 3];
    for i in 0..3 {
        // The only nonzero epsilon entries at fixed i are (i,j,k) and (i,k,j).
        let j = (i + 1) % 3;
        let k = (i + 2) % 3;
        let mut shear_a = 0.0;
        let mut epsilon = 0.0;
        for d in 0..3 {
            shear_a += sigma[3 * i + d] * a[d];
            epsilon += n[3 * j + d] * sigma[3 * k + d] - n[3 * k + d] * sigma[3 * j + d];
        }
        out[i] = 3.0 * shear_a + epsilon - q_flux[i];
    }
    if !out.iter().all(|x| x.is_finite()) {
        return Err("Codazzi contraction overflowed");
    }
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;
    const ZERO: [f64; 9] = [0.0; 9];
    #[test]
    fn zero_geometry_subtracts_flux() {
        assert_eq!(
            codazzi_residual(&ZERO, &ZERO, &[0.; 3], &[1., -2., 3.]).unwrap(),
            [-1., 2., -3.]
        );
    }
    #[test]
    fn shear_a_contraction_preserves_row_order() {
        let sigma = [1., 2., 3., 4., 5., 6., 7., 8., 9.];
        assert_eq!(
            codazzi_residual(&sigma, &ZERO, &[2., -1., 3.], &[0.; 3]).unwrap(),
            [27., 63., 99.]
        );
    }
    #[test]
    fn epsilon_positive_orientation_and_noncommuting_symmetric_tensors() {
        let sigma = [0., 0., 0., 0., 0., 2., 0., 2., 0.];
        let n = [1., 0., 0., 0., 3., 0., 0., 0., 7.];
        assert_eq!(
            codazzi_residual(&sigma, &n, &[0.; 3], &[0.; 3]).unwrap(),
            [-8., 0., 0.]
        );
    }
    #[test]
    fn commuting_diagonal_tensors_have_zero_epsilon_term() {
        let sigma = [1., 0., 0., 0., -3., 0., 0., 0., 2.];
        let n = [4., 0., 0., 0., 5., 0., 0., 0., 6.];
        assert_eq!(
            codazzi_residual(&sigma, &n, &[0.; 3], &[0.; 3]).unwrap(),
            [0.; 3]
        );
    }
    #[test]
    fn nonfinite_inputs_rejected_in_every_argument() {
        for bad in [f64::NAN, f64::INFINITY, f64::NEG_INFINITY] {
            let mut matrix = ZERO;
            matrix[8] = bad;
            let vector = [bad, 0., 0.];
            assert!(codazzi_residual(&matrix, &ZERO, &[0.; 3], &[0.; 3]).is_err());
            assert!(codazzi_residual(&ZERO, &matrix, &[0.; 3], &[0.; 3]).is_err());
            assert!(codazzi_residual(&ZERO, &ZERO, &vector, &[0.; 3]).is_err());
            assert!(codazzi_residual(&ZERO, &ZERO, &[0.; 3], &vector).is_err());
        }
    }
    #[test]
    fn finite_inputs_with_overflow_are_rejected() {
        assert!(codazzi_residual(&[f64::MAX; 9], &ZERO, &[2.; 3], &[0.; 3]).is_err());
    }
}
