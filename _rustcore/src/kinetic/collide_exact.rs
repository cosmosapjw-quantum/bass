//! Q7 ★ **정확 충돌 지수** — 3항 닫힌 공식 (76차).
//!
//! Thomson 핵은 **정확히 l <= 2 대역제한**이다:
//!     K(x) = (3/16pi)(1 + x^2) = 1/(4pi) + (1/(8pi)) P_2(x)
//!     k_0 = 1,  k_1 = 0,  k_2 = 1/10,  k_{l>=3} = 0
//! 따라서 C = nu(K - I) 의 지수가 닫힌 형태로 떨어진다:
//!
//! ```text
//! exp(x C) f = P_0 f + e^{-x}(f - P_0 f - P_2 f) + e^{-0.9 x} P_2 f,  x = nu dt
//! ```
//!
//! 결과: Sinkhorn·행렬지수 기계 **폐기**, 비용 O(n_ang), 그리고 **강성 소멸**
//! (x -> inf 가 안정할 뿐 아니라 정확히 P_0 f 로 떨어진다).
//! 사전검증: audit/q_check_collision_exact.py — dense expm 대비 <= 2e-14.
//!
//! ★ k_l 은 하드코딩하지 않는다 — `kernel_eigenvalues` 가 수치 구적으로
//!   재계산하고 시험이 상시 대조한다 (계약 §2).

use crate::kinetic::sphere::{project_l, SphereGrid};

const PI: f64 = std::f64::consts::PI;

/// 충돌핵 종류.  각각 (l, k_l) 의 **유한 목록**으로 표현된다 (l >= cutoff 는 0).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Kernel {
    /// Thomson (비편광, 정지 전자):  k = (1, 0, 1/10, 0, ...)
    Thomson,
    /// BGK 등방:  k = (1, 0, 0, ...)   — 수 보존만
    BgkIsotropic,
    /// BGK 보존형: k = (1, 1, 0, ...)  — 수 + 운동량 보존
    BgkConservative,
}

impl Kernel {
    /// 0 이 아닌 고유값 목록 [(l, k_l)].
    pub fn active(&self) -> Vec<(usize, f64)> {
        match self {
            Kernel::Thomson => vec![(0, 1.0), (2, 0.1)],
            Kernel::BgkIsotropic => vec![(0, 1.0)],
            Kernel::BgkConservative => vec![(0, 1.0), (1, 1.0)],
        }
    }
}

/// Legendre P_l(x).
fn legendre(l: usize, x: f64) -> f64 {
    let (mut p0, mut p1) = (1.0f64, x);
    if l == 0 {
        return 1.0;
    }
    for k in 1..l {
        let kk = k as f64;
        let p2 = ((2.0 * kk + 1.0) * x * p1 - kk * p0) / (kk + 1.0);
        p0 = p1;
        p1 = p2;
    }
    p1
}

/// ★ k_l 을 **수치 구적으로 재계산** (하드코딩 방지 게이트의 본체).
pub fn kernel_eigenvalues(l_max: usize) -> Vec<f64> {
    let (x, w) = crate::kinetic::sphere::gauss_legendre(64);
    (0..=l_max)
        .map(|l| {
            let mut s = 0.0;
            for i in 0..x.len() {
                let k = (3.0 / (16.0 * PI)) * (1.0 + x[i] * x[i]);
                s += w[i] * k * legendre(l, x[i]);
            }
            2.0 * PI * s
        })
        .collect()
}

/// exp(nu_dt * C) f — **정확**.  f 는 한 장의 각분포 (길이 n_ang).
pub fn collide_exact(g: &SphereGrid, f: &[f64], nu_dt: f64, kernel: Kernel) -> Vec<f64> {
    let x = nu_dt;
    if x <= 0.0 {
        return f.to_vec();
    }
    let em = (-x).exp();
    let mut out: Vec<f64> = f.iter().map(|v| em * v).collect();
    for (l, kl) in kernel.active() {
        let pl = project_l(g, f, l);
        let c = (x * (kl - 1.0)).exp() - em;
        for i in 0..out.len() {
            out[i] += c * pl[i];
        }
    }
    out
}

/// Mode B — 반경 슬라이스마다 같은 연산 (핵이 lambda-무관: 에너지-교환 정리).
/// f 배치는 방향-주 f[i*n_p + j].
pub fn collide_exact_modeb(
    g: &SphereGrid,
    f: &[f64],
    n_p: usize,
    nu_dt: f64,
    kernel: Kernel,
) -> Vec<f64> {
    let m = g.len();
    let mut out = vec![0.0; m * n_p];
    let mut slice = vec![0.0; m];
    for j in 0..n_p {
        for i in 0..m {
            slice[i] = f[i * n_p + j];
        }
        let o = collide_exact(g, &slice, nu_dt, kernel);
        for i in 0..m {
            out[i * n_p + j] = o[i];
        }
    }
    out
}

/// 등방화율 (l 별):  d ln |a_lm| / dt = nu (k_l - 1).
pub fn isotropization_rates(l_max: usize, kernel: Kernel) -> Vec<f64> {
    let act = kernel.active();
    (0..=l_max)
        .map(|l| {
            let kl = act.iter().find(|(a, _)| *a == l).map(|(_, k)| *k).unwrap_or(0.0);
            kl - 1.0
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn eigenvalues_are_recomputed_correctly() {
        let k = kernel_eigenvalues(5);
        assert!((k[0] - 1.0).abs() < 1e-13, "{:?}", k);
        assert!(k[1].abs() < 1e-13);
        assert!((k[2] - 0.1).abs() < 1e-13);
        for l in 3..=5 {
            assert!(k[l].abs() < 1e-13, "l={l} {:?}", k);
        }
    }

    #[test]
    fn matches_dense_matrix_exponential() {
        // dense: M_ij = w_j K(e_i . e_j);  exp(x(M - I)) 를 Taylor 로 (x 작게)
        let g = SphereGrid::new(16, 32);
        let n = g.len();
        let mut mm = vec![0.0; n * n];
        for i in 0..n {
            for j in 0..n {
                let c: f64 = (0..3).map(|k| g.ehat[3 * i + k] * g.ehat[3 * j + k]).sum();
                mm[i * n + j] = g.w[j] * (3.0 / (16.0 * PI)) * (1.0 + c * c);
            }
        }
        let f: Vec<f64> = (0..n).map(|i| 1.0 + 0.7 * ((i * 13 % 7) as f64 - 3.0)).collect();
        for x in [0.01f64, 0.1, 1.0, 5.0] {
            // Taylor:  e^{x(M-I)} f = e^{-x} sum x^k M^k f / k!
            let mut term = f.clone();
            let mut acc = f.clone();
            for k in 1..200 {
                let mut nx = vec![0.0; n];
                for i in 0..n {
                    let mut s = 0.0;
                    for j in 0..n {
                        s += mm[i * n + j] * term[j];
                    }
                    nx[i] = s * x / k as f64;
                }
                term = nx;
                let mut mx = 0.0f64;
                for i in 0..n {
                    acc[i] += term[i];
                    mx = mx.max(term[i].abs());
                }
                if mx < 1e-18 {
                    break;
                }
            }
            let em = (-x).exp();
            let refv: Vec<f64> = acc.iter().map(|v| em * v).collect();
            let got = collide_exact(&g, &f, x, Kernel::Thomson);
            let e = got
                .iter()
                .zip(&refv)
                .map(|(a, b)| (a - b).abs())
                .fold(0.0f64, f64::max);
            assert!(e < 1e-12, "x={x} err={e}");
        }
    }

    #[test]
    fn stiff_limit_is_exact_and_stable() {
        let g = SphereGrid::new(16, 32);
        let f: Vec<f64> = (0..g.len()).map(|i| 1.0 + 0.5 * (i as f64).cos()).collect();
        let out = collide_exact(&g, &f, 1e6, Kernel::Thomson);
        let p0 = project_l(&g, &f, 0);
        let e = out.iter().zip(&p0).map(|(a, b)| (a - b).abs()).fold(0.0f64, f64::max);
        assert!(e < 1e-12, "{e}");
        assert!(out.iter().all(|v| v.is_finite()));
    }

    #[test]
    fn number_is_conserved_exactly() {
        let g = SphereGrid::new(16, 32);
        let f: Vec<f64> = (0..g.len()).map(|i| 1.0 + 0.5 * (i as f64).sin()).collect();
        let n0: f64 = (0..g.len()).map(|i| g.w[i] * f[i]).sum();
        for x in [0.1f64, 3.0, 1e3] {
            let out = collide_exact(&g, &f, x, Kernel::Thomson);
            let n1: f64 = (0..g.len()).map(|i| g.w[i] * out[i]).sum();
            assert!((n1 - n0).abs() / n0.abs() < 1e-14, "x={x}");
        }
    }

    #[test]
    fn positivity_is_structural() {
        let g = SphereGrid::new(24, 48);
        // 강한 이방 (한쪽만 큰) 분포
        let f: Vec<f64> = (0..g.len())
            .map(|i| (10.0 * g.ehat[3 * i + 2]).exp())
            .collect();
        for x in [0.05f64, 1.0, 20.0, 1e4] {
            let out = collide_exact(&g, &f, x, Kernel::Thomson);
            assert!(out.iter().all(|v| *v > 0.0), "x={x} min={}",
                    out.iter().cloned().fold(f64::INFINITY, f64::min));
        }
    }
}
