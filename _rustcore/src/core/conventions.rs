//! 규약 패리티 층 — Python `bianchi.conventions` / `bianchi.rays.frame` 와 **비트-근접** 일치.
//!
//! 이 층의 존재 이유: 회전 부호·Levi-Civita·이중축약 P^a 는 "조용히 틀리는" 종류라,
//! Rust 포트가 Python 오라클과 정확히 같은 부호·순서를 쓰는지 속성테스트로 박제한다.

use nalgebra::{Matrix3, Vector3};

/// Levi-Civita eps_{ijk}, eps_{012}=+1.  Python EPS3[i,j,k]=(i-j)(j-k)(k-i)/2 와 동일.
/// (비대각 확장·미래 커널용 패리티 원소; 현재 직접 호출 없음.)
#[allow(dead_code)]
#[inline]
pub fn levi_civita(i: usize, j: usize, k: usize) -> f64 {
    let (i, j, k) = (i as i64, j as i64, k as i64);
    (((i - j) * (j - k) * (k - i)) as f64) / 2.0
}

/// COMMUTATOR 규약 회전행렬:  rotation_matrix(R) @ Y = R × Y  (= 표준 [R]_× 교차행렬).
/// Python `conventions.rotation_matrix(R)` (COMMUTATOR = -eps_abc R_c) 와 동일.
pub fn rotation_matrix_commutator(r: &Vector3<f64>) -> Matrix3<f64> {
    Matrix3::new(0.0, -r[2], r[1], r[2], 0.0, -r[0], -r[1], r[0], 0.0)
}

/// 독립 5성분에서 trace-free 대칭 3×3.  Python `tracefree_from_5` 와 동일 배치.
pub fn tracefree_from_5(s00: f64, s11: f64, s01: f64, s02: f64, s12: f64) -> Matrix3<f64> {
    Matrix3::new(s00, s01, s02, s01, s11, s12, s02, s12, -s00 - s11)
}

/// 3차원 접속 이중축약  P^a = A^a|x|² - (A·x)x^a + eps^a_bc x^b (Nx)^c.
/// eps 항 = (x × (N x))^a 이므로:  A(x·x) - (A·x)x + x×(Nx).
/// Python `frame.P_double(N, A, x)` 와 동일 (대칭축약이라 v2.0 규약수정과 무관).
pub fn p_double(n: &Matrix3<f64>, a: &Vector3<f64>, x: &Vector3<f64>) -> Vector3<f64> {
    a * x.dot(x) - x * a.dot(x) + x.cross(&(n * x))
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn levi_civita_signs() {
        assert_eq!(levi_civita(0, 1, 2), 1.0);
        assert_eq!(levi_civita(0, 2, 1), -1.0);
        assert_eq!(levi_civita(1, 1, 2), 0.0);
    }
    #[test]
    fn rotation_is_cross_product() {
        let r = Vector3::new(0.2, -0.5, 0.7);
        let y = Vector3::new(1.0, 2.0, -1.0);
        let m = rotation_matrix_commutator(&r);
        assert!((m * y - r.cross(&y)).norm() < 1e-15);
    }
}
