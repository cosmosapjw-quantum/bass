//! Q1 · **11유형 통합 군 코어** — 유형별 차트로 흩어진 구조상수를 하나로.
//!
//! 계약 (docs/Q-CONTRACT.md §2):
//!   C^c_{ab} = eps_{abd} n^{dc} + a_a delta^c_b - a_b delta^c_a
//!   Jacobi  : n^{ab} a_b = 0
//!   n 포장  : (n11, n22, n33, n12, n13, n23)
//!
//! ★ 중복 금지 (53차 GateGuard 교훈): 분류 규칙 자체는 Python `bianchi.algebra`
//! 가 **단일 진실원**이고 여기는 그 포트다.  일치는 시험이 왕복으로 잰다
//! (tests/test_q1_group.py).  분류 임계 TOL 도 Python 과 같은 1e-10.

use nalgebra::{Matrix3, SymmetricEigen, Vector3};

pub const TOL: f64 = 1e-10;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum GroupClass {
    A,
    B,
}

#[derive(Clone, Debug)]
pub struct Classification {
    pub name: &'static str,
    pub class: GroupClass,
    pub kappa: Option<f64>,
    pub exceptional: bool,
    /// (n 고윳값 부호 정렬, sign(|a|))
    pub signature: ([i32; 3], i32),
}

#[derive(Clone, Copy, Debug)]
pub struct BianchiGroup {
    /// (n11, n22, n33, n12, n13, n23)
    pub n: [f64; 6],
    pub a: [f64; 3],
}

#[inline]
fn sgn(x: f64) -> i32 {
    if x.abs() < TOL {
        0
    } else if x > 0.0 {
        1
    } else {
        -1
    }
}

/// Levi-Civita eps_{ijk}, eps_{123} = +1 (규약: core::conventions 와 동일 식).
#[inline]
fn eps(i: usize, j: usize, k: usize) -> f64 {
    let (i, j, k) = (i as i64, j as i64, k as i64);
    (((i - j) * (j - k) * (k - i)) as f64) / 2.0
}

impl BianchiGroup {
    pub fn new(n: [f64; 6], a: [f64; 3]) -> Self {
        Self { n, a }
    }

    /// 대각 게이지 편의 생성자 (class A 관례).
    pub fn diag(n1: f64, n2: f64, n3: f64, a: [f64; 3]) -> Self {
        Self {
            n: [n1, n2, n3, 0.0, 0.0, 0.0],
            a,
        }
    }

    pub fn n_mat(&self) -> Matrix3<f64> {
        let [n11, n22, n33, n12, n13, n23] = self.n;
        Matrix3::new(n11, n12, n13, n12, n22, n23, n13, n23, n33)
    }

    pub fn a_vec(&self) -> Vector3<f64> {
        Vector3::new(self.a[0], self.a[1], self.a[2])
    }

    /// Jacobi 항등식 잔차 벡터 n^{ab} a_b (대칭 n 이므로 단순 곱).
    pub fn jacobi_residual(&self) -> [f64; 3] {
        let r = self.n_mat() * self.a_vec();
        [r[0], r[1], r[2]]
    }

    pub fn jacobi_norm(&self) -> f64 {
        let r = self.jacobi_residual();
        r.iter().fold(0.0f64, |m, x| m.max(x.abs()))
    }

    /// C^c_{ab} — 반환은 `[c][a][b]` (Python `algebra.structure_constants` 와 동일 배열).
    pub fn structure_constants(&self) -> [[[f64; 3]; 3]; 3] {
        let n = self.n_mat();
        let a = self.a_vec();
        let mut c = [[[0.0f64; 3]; 3]; 3];
        for k in 0..3 {
            for i in 0..3 {
                for j in 0..3 {
                    let mut s = 0.0;
                    for d in 0..3 {
                        s += eps(i, j, d) * n[(d, k)];
                    }
                    if k == j {
                        s += a[i];
                    }
                    if k == i {
                        s -= a[j];
                    }
                    c[k][i][j] = s;
                }
            }
        }
        c
    }

    /// gamma^c_{ab} == C^c_{ab} (같은 대상; Python `general._gamma_struct` 와 동일).
    fn gamma(&self) -> [[[f64; 3]; 3]; 3] {
        self.structure_constants()
    }

    /// Koszul 접속 Gamma^k_{ij} = 1/2 (g^k_ij - g^i_jk + g^j_ki), 정규직교틀.
    fn connection(&self) -> [[[f64; 3]; 3]; 3] {
        let g = self.gamma();
        let mut gam = [[[0.0f64; 3]; 3]; 3];
        for k in 0..3 {
            for i in 0..3 {
                for j in 0..3 {
                    gam[k][i][j] = 0.5 * (g[k][i][j] - g[i][j][k] + g[j][k][i]);
                }
            }
        }
        gam
    }

    /// 3D Ricci (성분 상수).  Python `charts.general.ricci3` 와 같은 축약.
    ///   R_jk = G^m_jk G^i_im - G^m_ik G^i_jm - g^m_ij G^i_mk
    pub fn ricci3(&self) -> Matrix3<f64> {
        let g = self.gamma();
        let gg = self.connection();
        let mut r = Matrix3::zeros();
        for j in 0..3 {
            for k in 0..3 {
                let mut t1 = 0.0;
                let mut t2 = 0.0;
                let mut t3 = 0.0;
                for m in 0..3 {
                    for i in 0..3 {
                        t1 += gg[m][j][k] * gg[i][i][m];
                        t2 += gg[m][i][k] * gg[i][j][m];
                        t3 += g[m][i][j] * gg[i][m][k];
                    }
                }
                r[(j, k)] = t1 - t2 - t3;
            }
        }
        r
    }

    /// (K, ^3S_ab) — Hubble 정규화 기준 (Python `general.curvature` 와 동일).
    pub fn curvature(&self) -> (f64, Matrix3<f64>) {
        let ric = self.ricci3();
        let ric = 0.5 * (ric + ric.transpose());
        let r3 = ric.trace();
        let s3 = ric - Matrix3::identity() * (r3 / 3.0);
        (-r3 / 6.0, s3)
    }

    /// kappa = (1/2)[(tr N)^2 - tr(N^2)] / (A.A) — class B 만 유한.
    pub fn kappa(&self) -> Option<f64> {
        let a = self.a_vec();
        let a2 = a.dot(&a);
        if a2 < TOL * TOL {
            return None;
        }
        let n = self.n_mat();
        let second = 0.5 * (n.trace() * n.trace() - (n * n).trace());
        Some(second / a2)
    }

    /// det L = 3 (9 A^2 + n2 n3) — 0 이면 예외형 (구속 rank 저하).
    fn det_l(n2: f64, n3: f64, a_norm: f64) -> f64 {
        3.0 * (9.0 * a_norm * a_norm + n2 * n3)
    }

    /// 유형 분류.  Python `bianchi.algebra.classify` 의 포트 (단일 진실원은 Python).
    pub fn classify(&self) -> Classification {
        let n = self.n_mat();
        let a = self.a_vec();
        let eig = SymmetricEigen::new(n);
        let mut ev: Vec<f64> = eig.eigenvalues.iter().copied().collect();
        ev.sort_by(|x, y| x.partial_cmp(y).unwrap());
        let mut signs: Vec<i32> = ev.iter().map(|&x| sgn(x)).collect();
        signs.sort();
        let a_norm = a.norm();

        if a_norm < TOL {
            let pos = signs.iter().filter(|&&s| s > 0).count();
            let neg = signs.iter().filter(|&&s| s < 0).count();
            let zero = signs.iter().filter(|&&s| s == 0).count();
            let name = if zero == 3 {
                "I"
            } else if zero == 2 {
                "II"
            } else if zero == 1 {
                if pos == 1 && neg == 1 {
                    "VI_0"
                } else {
                    "VII_0"
                }
            } else if pos == 3 || neg == 3 {
                "IX"
            } else {
                "VIII"
            };
            return Classification {
                name,
                class: GroupClass::A,
                kappa: None,
                exceptional: false,
                signature: ([signs[0], signs[1], signs[2]], 0),
            };
        }

        // class B: a 방향에 직교하는 2x2 블록의 고윳값이 (n2, n3)
        let ahat = a / a_norm;
        let p = Matrix3::identity() - ahat * ahat.transpose();
        let sub = p * n * p;
        let se = SymmetricEigen::new(sub);
        let mut sev: Vec<f64> = se.eigenvalues.iter().copied().collect();
        // |고윳값| 최소인 것 (= a 방향의 0) 제거
        sev.sort_by(|x, y| x.abs().partial_cmp(&y.abs()).unwrap());
        let (n2, n3) = (sev[1], sev[2]);
        let kap = self.kappa();
        let (s2, s3) = (sgn(n2), sgn(n3));
        let exceptional =
            Self::det_l(n2, n3, a_norm).abs() < 1e-8 * (1.0f64).max(9.0 * a_norm * a_norm);

        let mut name = if s2 == 0 && s3 == 0 {
            "V"
        } else if s2 == 0 || s3 == 0 {
            "IV"
        } else if s2 * s3 < 0 {
            match kap {
                Some(k) if (k + 1.0).abs() < 1e-8 => "III",
                _ => "VI_h",
            }
        } else {
            "VII_h"
        };
        if exceptional {
            name = "VI*_-1/9";
        }
        let mut ss = [s2.min(s3), s2.max(s3), 0];
        ss[2] = 0;
        Classification {
            name,
            class: GroupClass::B,
            kappa: kap,
            exceptional,
            signature: (ss, 1),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn class_a_types() {
        let cases = [
            ([0.0, 0.0, 0.0], "I"),
            ([1.0, 0.0, 0.0], "II"),
            ([1.0, -1.0, 0.0], "VI_0"),
            ([1.0, 1.0, 0.0], "VII_0"),
            ([1.0, 1.0, -1.0], "VIII"),
            ([1.0, 1.0, 1.0], "IX"),
        ];
        for (nd, want) in cases {
            let g = BianchiGroup::diag(nd[0], nd[1], nd[2], [0.0; 3]);
            assert_eq!(g.classify().name, want, "{nd:?}");
            assert!(g.jacobi_norm() < 1e-15);
        }
    }

    #[test]
    fn jacobi_is_enforced_by_construction_in_class_b() {
        // a = (A,0,0), n = diag(0, n2, n3)  =>  n a = 0 정확히
        // kappa = -2  =>  VI_h  (kappa = -1 이면 III 별칭; 경계를 시험으로 못박는다)
        let g = BianchiGroup::diag(0.0, 2.0, -1.0, [1.0, 0.0, 0.0]);
        assert!(g.jacobi_norm() < 1e-15);
        let c = g.classify();
        assert_eq!(c.name, "VI_h");
        assert!((c.kappa.unwrap() + 2.0).abs() < 1e-12, "{c:?}");
        // kappa = -1 의 III 별칭
        let g3 = BianchiGroup::diag(0.0, 1.0, -1.0, [1.0, 0.0, 0.0]);
        assert_eq!(g3.classify().name, "III");
        // V / IV / VII_h
        assert_eq!(BianchiGroup::diag(0.0, 0.0, 0.0, [1.0, 0.0, 0.0]).classify().name, "V");
        assert_eq!(BianchiGroup::diag(0.0, 0.0, 1.0, [1.0, 0.0, 0.0]).classify().name, "IV");
        assert_eq!(BianchiGroup::diag(0.0, 1.0, 1.0, [0.5, 0.0, 0.0]).classify().name, "VII_h");
    }

    #[test]
    fn exceptional_is_detected_by_constraint_degeneracy() {
        // det L = 3(9A^2 + n2 n3) = 0  =>  n2 n3 = -9 A^2
        let a = 1.0f64;
        let (n2, n3) = (3.0, -3.0 * a * a);
        let g = BianchiGroup::diag(0.0, n2, n3, [a, 0.0, 0.0]);
        let c = g.classify();
        assert!(c.exceptional, "{c:?}");
        assert_eq!(c.name, "VI*_-1/9");
        assert!((c.kappa.unwrap() + 9.0).abs() < 1e-9, "{c:?}");
    }

    #[test]
    fn ricci_matches_closed_form_r3() {
        // ^3R = -tr(N^2) + (1/2)(tr N)^2 - 6 A.A
        let g = BianchiGroup::new([0.3, -1.1, 0.7, 0.2, 0.0, 0.0], [0.0, 0.0, 0.0]);
        let n = g.n_mat();
        let want = -(n * n).trace() + 0.5 * n.trace() * n.trace();
        let got = g.ricci3().trace();
        assert!((got - want).abs() < 1e-13, "{got} vs {want}");
    }
}
