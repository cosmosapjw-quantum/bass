//! Q5' ★ **공변(comoving) 운동량 프레임** — 76차 반증 이후의 정정 설계.
//!
//! ═══ 반증 기록 (이 모듈이 존재하는 이유) ═══
//! 계획 §0 은 "고정 tetrad 프레임 격자"를 택했다.  76차 실측이 그것을 기각한다:
//!   · Mixmaster 붕괴에서 축비가 τ=−25 까지 **2.2e28** 로 커진다.
//!   · 자유흐름 광자의 물리 각분포는 폭 ~1/축비 의 **연필빔**으로 집중한다.
//!   · 어떤 고정 각격자도 이를 표현할 수 없다 — 보간 횟수를 200배 줄여도
//!     (stride 1 → 200) 발산 크기가 3자리밖에 안 줄었다 ⇒ 보간 불안정이 아니라
//!     **표현 한계**.
//! 계획 §9 위험표가 미리 정해둔 판정법대로 **불변격자와의 하이브리드로 후퇴**한다.
//!
//! ═══ 정정 설계 ═══
//! 운동량을 공변좌표 q 로 잡는다:  p = M(τ) q,   dM/dτ = -(I + Sigma) M.
//!   · H, Sigma (그리고 원하면 R) 의 흐름이 **정확히 흡수**된다 — 보간 0회.
//!   · Bianchi I 은 수송이 **항등** (I2c 의 정확성 회복).
//!   · 나머지 유형은 곡률항 (n_ab, a_a) 만 잔여 흐름을 만든다 — 작고, 벽 근처에서만.
//!   · 격자점이 물리 프레임에서 **빔 쪽으로 모인다** — 피적분함수가 있는 곳에
//!     노드가 있다 (고정 프레임과 정반대).
//!
//! 물리 프레임 사상:  ê = M q̂ / mu,  mu = |M q̂|,  dOmega_phys/dOmega_com = det M / mu^3.
//!
//! 충돌은 Q7 의 3항 공식을 **물리 프레임 투영**으로 그대로 쓴다 (격자 무관 연산자
//! 항등이므로 공변격자 위에서도 정확).  Sinkhorn·행렬지수 불필요.

const PI: f64 = std::f64::consts::PI;

/// 공변 프레임 사상 M (행 우선 3x3).
#[derive(Clone, Copy, Debug)]
pub struct Frame {
    pub m: [f64; 9],
}

impl Frame {
    pub fn identity() -> Self {
        Frame {
            m: [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0],
        }
    }

    #[inline]
    pub fn apply(&self, q: &[f64; 3]) -> [f64; 3] {
        [
            self.m[0] * q[0] + self.m[1] * q[1] + self.m[2] * q[2],
            self.m[3] * q[0] + self.m[4] * q[1] + self.m[5] * q[2],
            self.m[6] * q[0] + self.m[7] * q[1] + self.m[8] * q[2],
        ]
    }

    pub fn det(&self) -> f64 {
        let m = &self.m;
        m[0] * (m[4] * m[8] - m[5] * m[7]) - m[1] * (m[3] * m[8] - m[5] * m[6])
            + m[2] * (m[3] * m[7] - m[4] * m[6])
    }

    /// dM/dtau = -(I + Sigma) M  (+ 회전 R 을 흡수하려면 sigma 에 -eps·R 를 더한다).
    /// sigma 는 대칭 6성분 (11,22,33,12,13,23), rot 는 3성분.
    fn rhs(&self, sigma: &[f64; 6], rot: &[f64; 3]) -> [f64; 9] {
        // A_ab = delta + Sigma_ab - eps_abc R_c   (프레임 co-rotation 흡수)
        let a = [
            1.0 + sigma[0],
            sigma[3] - rot[2],
            sigma[4] + rot[1],
            sigma[3] + rot[2],
            1.0 + sigma[1],
            sigma[5] - rot[0],
            sigma[4] - rot[1],
            sigma[5] + rot[0],
            1.0 + sigma[2],
        ];
        let mut out = [0.0; 9];
        for i in 0..3 {
            for j in 0..3 {
                let mut s = 0.0;
                for k in 0..3 {
                    s += a[3 * i + k] * self.m[3 * k + j];
                }
                out[3 * i + j] = -s;
            }
        }
        out
    }

    /// RK4 한 스텝 (배경 선형보간).
    pub fn step(
        &self,
        s0: &[f64; 6],
        r0: &[f64; 3],
        s1: &[f64; 6],
        r1: &[f64; 3],
        dtau: f64,
    ) -> Frame {
        let mid = |a: &[f64; 6], b: &[f64; 6]| {
            let mut o = [0.0; 6];
            for k in 0..6 {
                o[k] = 0.5 * (a[k] + b[k]);
            }
            o
        };
        let midr = |a: &[f64; 3], b: &[f64; 3]| {
            let mut o = [0.0; 3];
            for k in 0..3 {
                o[k] = 0.5 * (a[k] + b[k]);
            }
            o
        };
        let sm = mid(s0, s1);
        let rm = midr(r0, r1);
        let add = |f: &Frame, k: &[f64; 9], c: f64| {
            let mut o = [0.0; 9];
            for i in 0..9 {
                o[i] = f.m[i] + c * k[i];
            }
            Frame { m: o }
        };
        let k1 = self.rhs(s0, r0);
        let k2 = add(self, &k1, 0.5 * dtau).rhs(&sm, &rm);
        let k3 = add(self, &k2, 0.5 * dtau).rhs(&sm, &rm);
        let k4 = add(self, &k3, dtau).rhs(s1, r1);
        let mut o = [0.0; 9];
        for i in 0..9 {
            o[i] = self.m[i] + dtau / 6.0 * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i]);
        }
        Frame { m: o }
    }
}

/// 물리 방향 ê 와 배율 mu = |M q̂| (공변 단위벡터마다).
pub fn phys_dirs(f: &Frame, qhat: &[f64]) -> (Vec<f64>, Vec<f64>) {
    let n = qhat.len() / 3;
    let mut e = vec![0.0; 3 * n];
    let mut mu = vec![0.0; n];
    for i in 0..n {
        let q = [qhat[3 * i], qhat[3 * i + 1], qhat[3 * i + 2]];
        let p = f.apply(&q);
        let m = (p[0] * p[0] + p[1] * p[1] + p[2] * p[2]).sqrt();
        mu[i] = m;
        e[3 * i] = p[0] / m;
        e[3 * i + 1] = p[1] / m;
        e[3 * i + 2] = p[2] / m;
    }
    (e, mu)
}

/// ln(물리 구적 가중) = ln w_com + ln|det M| - 3 ln mu  — **로그공간** (범위 벽 제거).
pub fn ln_phys_weights(f: &Frame, w_com: &[f64], mu: &[f64]) -> Vec<f64> {
    let ld = f.det().abs().ln();
    (0..w_com.len())
        .map(|i| w_com[i].ln() + ld - 3.0 * mu[i].ln())
        .collect()
}

/// 물리 프레임 모멘트를 **로그-스케일 분리형**으로 반환:
///     (ln rho,  q_a / rho,  pi_ab / rho)
/// ★ rho 자체는 깊은 붕괴에서 double 범위를 넘는다 (ln rho ~ 900).  물리가
/// 필요로 하는 것은 Omega 와 Pi/Omega 같은 **비**이므로, 비는 항상 범위 안이고
/// 스케일은 ln 으로 나른다 — 이것이 LNA_WALL 을 완전히 없애는 방법이다.
pub fn moments_log(lw: &[f64], lg: &[f64], ehat: &[f64]) -> (f64, [f64; 3], [f64; 6]) {
    let n = lg.len();
    let mut mx = f64::NEG_INFINITY;
    for i in 0..n {
        let v = lw[i] + lg[i];
        if v > mx {
            mx = v;
        }
    }
    if !mx.is_finite() {
        return (f64::NEG_INFINITY, [0.0; 3], [0.0; 6]);
    }
    let wgt: Vec<f64> = (0..n).map(|i| (lw[i] + lg[i] - mx).exp()).collect();
    let s_rho: f64 = wgt.iter().sum();
    let ln_rho = mx + s_rho.ln();
    let mut q = [0.0; 3];
    for k in 0..3 {
        let s: f64 = (0..n).map(|i| wgt[i] * ehat[3 * i + k]).sum();
        q[k] = s / s_rho;
    }
    let pairs = [(0usize, 0usize), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2)];
    let mut pi = [0.0; 6];
    for (idx, (a, b)) in pairs.iter().enumerate() {
        let s: f64 = (0..n)
            .map(|i| {
                let v = ehat[3 * i + a] * ehat[3 * i + b];
                wgt[i] * if a == b { v - 1.0 / 3.0 } else { v }
            })
            .sum();
        pi[idx] = s / s_rho;
    }
    (ln_rho, q, pi)
}

/// ★ 공변격자 위의 **정확 충돌 지수** (Q7 3항) — 물리 프레임 투영으로.
/// 입력·출력은 ln G (로그공간 상태).  kernel active = [(l, k_l)].
pub fn collide_exact_log(
    lw: &[f64],
    lg: &[f64],
    ehat: &[f64],
    nu_dt: f64,
    active: &[(usize, f64)],
) -> Vec<f64> {
    if nu_dt <= 0.0 {
        return lg.to_vec();
    }
    let n = lg.len();
    let em = (-nu_dt).exp();
    // 물리 프레임 저-l 투영: P_l G  (l = 0, 1, 2 만 필요)
    // a_lm = sum_i w_i G_i Y_lm(ê_i);  (P_l G)_i = sum_m a_lm Y_lm(ê_i)
    let mut out = vec![0.0; n];
    // 스케일 기준 (로그 범위 폭 흡수)
    let mut mx = f64::NEG_INFINITY;
    for i in 0..n {
        let v = lw[i] + lg[i];
        if v > mx {
            mx = v;
        }
    }
    let gs: Vec<f64> = (0..n).map(|i| (lg[i] - mx).exp()).collect(); // 스케일된 G
    let ws: Vec<f64> = (0..n).map(|i| lw[i].exp()).collect();

    let mut proj = vec![vec![0.0; n]; active.len()];
    for (ai, (l, _)) in active.iter().enumerate() {
        let nm = 2 * l + 1;
        let mut a = vec![0.0; nm];
        for i in 0..n {
            let y = real_ylm_l(*l, &[ehat[3 * i], ehat[3 * i + 1], ehat[3 * i + 2]]);
            let wg = ws[i] * gs[i];
            for m in 0..nm {
                a[m] += wg * y[m];
            }
        }
        for i in 0..n {
            let y = real_ylm_l(*l, &[ehat[3 * i], ehat[3 * i + 1], ehat[3 * i + 2]]);
            let mut v = 0.0;
            for m in 0..nm {
                v += a[m] * y[m];
            }
            proj[ai][i] = v;
        }
    }
    for i in 0..n {
        let mut v = em * gs[i];
        for (ai, (_, kl)) in active.iter().enumerate() {
            v += ((nu_dt * (kl - 1.0)).exp() - em) * proj[ai][i];
        }
        out[i] = v.max(1e-300).ln() + mx;
    }
    out
}

/// l = 0,1,2 의 실수 구면조화 (직교정규).  반환 길이 2l+1.
pub fn real_ylm_l(l: usize, e: &[f64; 3]) -> Vec<f64> {
    let (x, y, z) = (e[0], e[1], e[2]);
    match l {
        0 => vec![(1.0 / (4.0 * PI)).sqrt()],
        1 => {
            let c = (3.0 / (4.0 * PI)).sqrt();
            vec![c * y, c * z, c * x]
        }
        2 => {
            let c1 = 0.5 * (15.0 / PI).sqrt();
            let c2 = 0.25 * (5.0 / PI).sqrt();
            let c3 = 0.25 * (15.0 / PI).sqrt();
            vec![
                c1 * x * y,
                c1 * y * z,
                c2 * (3.0 * z * z - 1.0),
                c1 * x * z,
                c3 * (x * x - y * y),
            ]
        }
        _ => panic!("real_ylm_l 은 l<=2 만 (Thomson·BGK 핵의 대역)"),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::kinetic::sphere::SphereGrid;

    #[test]
    fn frame_reproduces_isotropic_expansion_at_fourth_order() {
        // dM/dtau = -M  =>  M(1) = e^{-1} I.  RK4 라 오차는 O(h^4) — 차수를 잰다.
        let want = (-1.0f64).exp();
        let run = |n: usize| {
            let mut f = Frame::identity();
            let (s, r) = ([0.0; 6], [0.0; 3]);
            let dt = 1.0 / n as f64;
            for _ in 0..n {
                f = f.step(&s, &r, &s, &r, dt);
            }
            (f.m[0] - want).abs()
        };
        let (e1, e2, e3) = (run(25), run(50), run(100));
        assert!((e1 / e2).log2() > 3.7, "{e1} {e2}");
        assert!((e2 / e3).log2() > 3.7, "{e2} {e3}");
        assert!(e3 < 1e-10, "{e3}");
    }

    #[test]
    fn ylm_l2_is_orthonormal_on_grid() {
        let g = SphereGrid::new(24, 48);
        for l in 0..=2 {
            let nm = 2 * l + 1;
            for a in 0..nm {
                for b in 0..nm {
                    let mut s = 0.0;
                    for i in 0..g.len() {
                        let y =
                            real_ylm_l(l, &[g.ehat[3 * i], g.ehat[3 * i + 1], g.ehat[3 * i + 2]]);
                        s += g.w[i] * y[a] * y[b];
                    }
                    let want = if a == b { 1.0 } else { 0.0 };
                    assert!((s - want).abs() < 1e-12, "l={l} {a},{b} = {s}");
                }
            }
        }
    }

    #[test]
    fn exact_collision_in_log_space_matches_linear_three_term() {
        let g = SphereGrid::new(16, 32);
        let n = g.len();
        let lg: Vec<f64> = (0..n).map(|i| 3.0 * g.ehat[3 * i + 2]).collect();
        let lw: Vec<f64> = g.w.iter().map(|x| x.ln()).collect();
        let active = [(0usize, 1.0f64), (2, 0.1)];
        for x in [0.05f64, 1.0, 7.0] {
            let out = collide_exact_log(&lw, &lg, &g.ehat, x, &active);
            // 선형 경로 (작은 범위라 안전)
            let f: Vec<f64> = lg.iter().map(|v| v.exp()).collect();
            let ref_ = crate::kinetic::collide_exact::collide_exact(
                &g,
                &f,
                x,
                crate::kinetic::collide_exact::Kernel::Thomson,
            );
            let e = (0..n)
                .map(|i| (out[i].exp() - ref_[i]).abs() / ref_[i].abs())
                .fold(0.0f64, f64::max);
            assert!(e < 1e-11, "x={x} err={e}");
        }
    }

    #[test]
    fn log_space_survives_extreme_dynamic_range() {
        let g = SphereGrid::new(16, 32);
        let n = g.len();
        // ln G 가 ±300 을 넘는 범위 (I2c 의 LNA_WALL 영역)
        let lg: Vec<f64> = (0..n).map(|i| 700.0 * g.ehat[3 * i + 2]).collect();
        let lw: Vec<f64> = g.w.iter().map(|x| x.ln()).collect();
        let (ln_rho, _, pi) = moments_log(&lw, &lg, &g.ehat);
        assert!(ln_rho.is_finite(), "ln_rho={ln_rho}");
        assert!(pi.iter().all(|v| v.is_finite()));
        let out = collide_exact_log(&lw, &lg, &g.ehat, 3.0, &[(0, 1.0), (2, 0.1)]);
        assert!(out.iter().all(|v| v.is_finite()));
    }
}
