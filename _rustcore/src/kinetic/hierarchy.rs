//! Lewis-Challinor 다극 계층 — 균질·법선합동 축약의 RHS, 닫힘, RK4 적분.
//!
//! Python 오라클: `bianchi.matter.hierarchy`.  식 (12) (astro-ph/0203507v2) 의
//! 균질 축약 (공간미분=0 for Bianchi I, vorticity=0, 가속도=0 for u=e₀):
//!
//! ```text
//! J̇^(i)_{A_l} + H[(3+n)J^(i)_{A_l} + (1-n)J^(i+1)_{A_l}]
//!   + (l/(2l+3))[(2n+3)J^(i)_{a<A_{l-1}} + (2-2n)J^(i+1)_{a<A_{l-1}}] σ_{a_l>}{}^a   (A)
//!   + [(l-n)J^(i-1)_{abA_l} + (n-1)J^(i)_{abA_l}] σ^{ab}                              (B)
//!   + (l(l-1)/(4l²-1))[(n-1)J^(i+2)_{<A_{l-2}} - (l+n+1)J^(i+1)_{<A_{l-2}}] σ_{..>}   (C)
//!   = 0
//! ```
//! ★ σ-결합 부호 (A,B,C) = (+1,−1,−1) — 논문 (+---) ↔ 우리 (−+++) 변환을
//!   **정확 구적 오라클로 확정**했다 (유일성 마진 1.5e6배; audit/h_hierarchy.py).
//! ★ (l−n) = −2i 이므로 i=0 방정식은 J^(−1) 을 참조하지 않는다 → i 아래로 닫힘.
//! ★ i 위쪽 닫힘은 **기하 외삽** (0-절단은 무질량에서 7자리 열등: J^(i) 가 i 무관이므로).

use rayon::prelude::*;

use crate::kinetic::pstf;
use crate::kinetic::quad;

/// σ-결합 항군 전역부호 (오라클 확정).
pub const SIGN_A: f64 = 1.0;
pub const SIGN_B: f64 = -1.0;
pub const SIGN_C: f64 = -1.0;

/// (l,i) 격자 상태.  `j[l][i]` = 평탄 rank-l 텐서 (길이 3^l).
#[derive(Clone)]
pub struct State {
    pub l_max: usize,
    pub i_max: usize,
    pub j: Vec<Vec<Vec<f64>>>, // [l][i][flat]
}

impl State {
    pub fn zeros(l_max: usize, i_max: usize) -> Self {
        let j = (0..=l_max)
            .map(|l| (0..=i_max + 2).map(|_| vec![0.0; pstf::dim(l)]).collect())
            .collect();
        State { l_max, i_max, j }
    }

    /// 구적으로 초기조건 채우기 (i 는 0..=i_max+2 까지; 상위 2개는 닫힘이 덮어씀).
    pub fn from_quadrature(
        a_vec: &[f64; 3],
        mass: f64,
        l_max: usize,
        i_max: usize,
        dipole_eps: f64,
        dipole_axis: usize,
    ) -> Self {
        let mut s = State::zeros(l_max, i_max);
        for l in 0..=l_max {
            for i in 0..=i_max + 2 {
                s.j[l][i] = quad::j_moment(a_vec, mass, l, i as i32, dipole_eps, dipole_axis);
            }
        }
        s
    }

    #[inline]
    fn get(&self, l: usize, i: i32) -> &[f64] {
        &self.j[l][i as usize]
    }

    /// i 위쪽 기하 외삽 닫힘:  J^(i_max+1) = J^(i_max)·(J^(i_max)/J^(i_max−1)).
    /// 무질량(비=1)에서 정확, 유질량(비<1)에서 감쇠.
    pub fn close_i(&mut self) {
        for l in 0..=self.l_max {
            let im = self.i_max;
            let d = pstf::dim(l);
            let mut nxt = vec![0.0; d];
            let mut nxt2 = vec![0.0; d];
            for k in 0..d {
                let a = self.j[l][im][k];
                let b = self.j[l][im - 1][k];
                let ratio = if b.abs() > 1e-300 {
                    (a / b).clamp(-1.0, 1.0)
                } else {
                    0.0
                };
                nxt[k] = a * ratio;
                nxt2[k] = nxt[k] * ratio;
            }
            self.j[l][im + 1] = nxt;
            self.j[l][im + 2] = nxt2;
        }
    }
}

/// (J·σ)_{A_{l-1} b} = J_{a A_{l-1}} σ_{b a}  — rank l → rank l.
fn contract_one(j: &[f64], l: usize, sigma: &[f64; 9]) -> Vec<f64> {
    let d = pstf::dim(l);
    let mut out = vec![0.0; d];
    let mut idx = [0usize; crate::kinetic::pstf::MAX_RANK];
    for flat in 0..d {
        let mut r = flat;
        for k in (0..l).rev() {
            idx[k] = r % 3;
            r /= 3;
        }
        // out[A_{l-1}, b] = Σ_a J[a, A_{l-1}] σ[b,a];  여기서 b = idx[l-1]
        let b = idx[l - 1];
        let mut acc = 0.0;
        for a in 0..3 {
            // src = (a, idx[0..l-1])
            let mut src = a;
            for k in 0..l - 1 {
                src = src * 3 + idx[k];
            }
            acc += j[src] * sigma[b * 3 + a];
        }
        out[flat] = acc;
    }
    out
}

/// J_{ab A_l} σ^{ab}  — rank l+2 → rank l.
fn contract_two(j: &[f64], l: usize, sigma: &[f64; 9]) -> Vec<f64> {
    let d = pstf::dim(l);
    let mut out = vec![0.0; d];
    for flat in 0..d {
        let mut acc = 0.0;
        for a in 0..3 {
            for b in 0..3 {
                let src = (a * 3 + b) * d + flat;
                acc += j[src] * sigma[a * 3 + b];
            }
        }
        out[flat] = acc;
    }
    out
}

/// J_{⟨A_{l-2}} σ_{a_{l-1}a_l⟩}  — rank l-2 ⊗ σ → PSTF rank l.
fn outer_sigma(j: &[f64], l: usize, sigma: &[f64; 9]) -> Vec<f64> {
    let d_low = pstf::dim(l - 2);
    let mut raw = vec![0.0; pstf::dim(l)];
    for base in 0..d_low {
        for a in 0..3 {
            for b in 0..3 {
                raw[(base * 3 + a) * 3 + b] = j[base] * sigma[a * 3 + b];
            }
        }
    }
    pstf::project(&raw, l)
}

/// 한 (l,i) 의 dJ/dt.
pub fn rhs_one(s: &State, h: f64, sigma: &[f64; 9], l: usize, i: i32) -> Vec<f64> {
    let n = l as f64 + 2.0 * i as f64;
    let d = pstf::dim(l);
    let mut out = vec![0.0; d];

    // H 항
    let cur = s.get(l, i);
    let nxt = s.get(l, i + 1);
    for k in 0..d {
        out[k] = -h * ((3.0 + n) * cur[k] + (1.0 - n) * nxt[k]);
    }

    // (A) l→l 지표교체 (l ≥ 1)
    if l >= 1 {
        let ca = l as f64 / (2.0 * l as f64 + 3.0);
        let t1 = contract_one(cur, l, sigma);
        let t2 = contract_one(nxt, l, sigma);
        let mut ta: Vec<f64> = (0..d)
            .map(|k| (2.0 * n + 3.0) * t1[k] + (2.0 - 2.0 * n) * t2[k])
            .collect();
        if l >= 2 {
            ta = pstf::project(&ta, l);
        }
        for k in 0..d {
            out[k] -= SIGN_A * ca * ta[k];
        }
    }

    // (B) l+2 → l  (l+2 가 격자 밖이면 단순절단 = 0)
    if l + 2 <= s.l_max {
        let cb_prev = l as f64 - n; // = -2i  → i=0 에서 0 (아래로 닫힘)
        let mut tb = contract_two(s.get(l + 2, i), l, sigma);
        for k in 0..d {
            tb[k] *= n - 1.0;
        }
        if cb_prev != 0.0 {
            let tprev = contract_two(s.get(l + 2, i - 1), l, sigma);
            for k in 0..d {
                tb[k] += cb_prev * tprev[k];
            }
        }
        for k in 0..d {
            out[k] -= SIGN_B * tb[k];
        }
    }

    // (C) l-2 → l  (l ≥ 2)
    if l >= 2 {
        let cc = l as f64 * (l as f64 - 1.0) / (4.0 * l as f64 * l as f64 - 1.0);
        let u2 = outer_sigma(s.get(l - 2, i + 2), l, sigma);
        let u1 = outer_sigma(s.get(l - 2, i + 1), l, sigma);
        for k in 0..d {
            out[k] -= SIGN_C * cc * ((n - 1.0) * u2[k] - (l as f64 + n + 1.0) * u1[k]);
        }
    }

    if l >= 2 {
        pstf::project(&out, l)
    } else {
        out
    }
}

/// 격자 전체의 dJ/dt (닫힘 적용).  Rayon 으로 (l,i) 병렬.
pub fn rhs_state(s: &State, h: f64, sigma: &[f64; 9]) -> Vec<Vec<Vec<f64>>> {
    let mut sc = s.clone();
    sc.close_i();
    (0..=s.l_max)
        .into_par_iter()
        .map(|l| {
            (0..=s.i_max)
                .map(|i| rhs_one(&sc, h, sigma, l, i as i32))
                .collect()
        })
        .collect()
}

/// RK4 적분.  H, σ 는 상수 배경 (ȧ_i = (H+σ_i)a_i).
/// 반환: 각 스텝의 (t, ρ, p, π_ab) 이력.
#[allow(clippy::too_many_arguments)]
pub fn integrate(
    a0: &[f64; 3],
    mass: f64,
    h: f64,
    sigma_diag: &[f64; 3],
    t_end: f64,
    nsteps: usize,
    l_max: usize,
    i_max: usize,
    dipole_eps: f64,
) -> (Vec<f64>, Vec<f64>, Vec<f64>, Vec<[f64; 9]>) {
    let sigma = [
        sigma_diag[0],
        0.0,
        0.0,
        0.0,
        sigma_diag[1],
        0.0,
        0.0,
        0.0,
        sigma_diag[2],
    ];
    let mut s = State::from_quadrature(a0, mass, l_max, i_max, dipole_eps, 2);
    let dt = t_end / nsteps as f64;
    let (mut ts, mut rhos, mut ps, mut pis) = (vec![], vec![], vec![], vec![]);

    let axpy = |base: &State, d: &Vec<Vec<Vec<f64>>>, c: f64| -> State {
        let mut o = base.clone();
        for l in 0..=base.l_max {
            for i in 0..=base.i_max {
                for k in 0..o.j[l][i].len() {
                    o.j[l][i][k] = base.j[l][i][k] + c * d[l][i][k];
                }
            }
        }
        o
    };

    for step in 0..=nsteps {
        ts.push(step as f64 * dt);
        rhos.push(s.j[0][0][0]);
        ps.push(s.j[0][1][0] / 3.0);
        let mut pi = [0.0f64; 9];
        if l_max >= 2 {
            pi.copy_from_slice(&s.j[2][0]);
        }
        pis.push(pi);
        if step == nsteps {
            break;
        }
        let k1 = rhs_state(&s, h, &sigma);
        let k2 = rhs_state(&axpy(&s, &k1, 0.5 * dt), h, &sigma);
        let k3 = rhs_state(&axpy(&s, &k2, 0.5 * dt), h, &sigma);
        let k4 = rhs_state(&axpy(&s, &k3, dt), h, &sigma);
        for l in 0..=l_max {
            for i in 0..=i_max {
                for k in 0..s.j[l][i].len() {
                    s.j[l][i][k] += dt / 6.0
                        * (k1[l][i][k] + 2.0 * k2[l][i][k] + 2.0 * k3[l][i][k] + k4[l][i][k]);
                }
            }
        }
    }
    (ts, rhos, ps, pis)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn trajectory_matches_quadrature_massless() {
        let a0 = [1.0, 1.0, 1.0];
        let sig = [0.06, -0.02, -0.04];
        let (ts, rhos, _, pis) = integrate(&a0, 0.0, 1.0, &sig, 0.3, 40, 4, 2, 0.0);
        // 마지막 시각의 정확 구적과 대조
        let t = *ts.last().unwrap();
        let a_t = [
            a0[0] * ((1.0 + sig[0]) * t).exp(),
            a0[1] * ((1.0 + sig[1]) * t).exp(),
            a0[2] * ((1.0 + sig[2]) * t).exp(),
        ];
        let (rho_e, _, pi_e) = quad::moments(&a_t, 0.0);
        let rho_h = *rhos.last().unwrap();
        assert!(
            (rho_h / rho_e - 1.0).abs() < 1e-6,
            "rho {rho_h:e} vs {rho_e:e}"
        );
        let pi_h = pis.last().unwrap();
        let worst = (0..9).fold(0.0f64, |a, k| a.max((pi_h[k] - pi_e[k]).abs()));
        let scale = pi_e
            .iter()
            .fold(0.0f64, |a, b| a.max(b.abs()))
            .max(1e-8 * rho_e);
        assert!(worst < 1e-6 * scale.max(1e-30) * 1e6, "pi {worst:e}");
    }

    #[test]
    fn isotropic_background_keeps_pi_zero() {
        let (_, rhos, _, pis) = integrate(
            &[1.0, 1.0, 1.0],
            0.5,
            1.0,
            &[0.0, 0.0, 0.0],
            0.4,
            20,
            4,
            2,
            0.0,
        );
        let rho0 = rhos[0];
        for pi in &pis {
            let w = pi.iter().fold(0.0f64, |a, b| a.max(b.abs()));
            assert!(w < 1e-9 * rho0, "pi={w:e}");
        }
    }
}
