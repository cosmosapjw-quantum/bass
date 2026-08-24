//! R1 · **type V 결합 진화의 노드 커널** — K5b/D2 의 병목을 Rust 로.
//!
//! Python 프로파일 (55296 노드, `evolve_coupled` 한 스텝 ≈ 68 ms):
//!     moments_from_nodes(l≤2,i≤1) 11.2 ms × 5,   kinetic_rhs 4.1 ms × 4
//! 둘 다 노드 배열을 여러 번 훑는 **메모리 대역폭** 문제라, 한 번의 융합 순회로
//! 바꾸면 크게 준다.  여기서는 RK4 한 스텝 전체(기하 + 운동론)를 Rust 안에서 돈다.
//!
//! ★ 물리는 Python 오라클(`bianchi.matter.type_v_coupled`)과 **차등테스트**로 대조한다.
//!   포트는 빠르게만 할 뿐 정확해지지 않는다 — 그래서 오라클을 지운 게 아니라 남겼고,
//!   `backend="python"` 으로 언제든 되돌릴 수 있다.
//!
//! 규약 (K5a 가 계량에서 확정):
//!     Friedmann F = 3H² − ρ − σ² − 3A²/a₁²
//!     Codazzi   C = 3σ₁A/a₁ + q₁
//!     공간      G_{îî} = A²/a₁² − u_j − u_k − h_jh_k = p + π_ii
//!     Liouville ṗ_i (특성곡선),  d ln W/dt = −2A p¹/E   (공변무게, V 는 밖에서)

use rayon::prelude::*;

/// 노드 한 점의 파생량 — 융합 순회에서 재사용한다.
#[inline]
fn node_geom(p: &[f64; 3], a: &[f64; 3], mass: f64) -> (f64, f64, [f64; 3]) {
    let pi = [p[0] / a[0], p[1] / a[1], p[2] / a[2]];
    let lam2 = pi[0] * pi[0] + pi[1] * pi[1] + pi[2] * pi[2];
    let lam = lam2.sqrt();
    let e = if lam > 0.0 {
        [pi[0] / lam, pi[1] / lam, pi[2] / lam]
    } else {
        [0.0, 0.0, 0.0]
    };
    ((mass * mass + lam2).sqrt(), lam, e)
}

/// ★ (ρ, 3p, q_a, π_ab) — **한 번의 순회**로.  측도 d³P = d³p/V 의 V 는 여기서 나눈다.
///
/// 반환 (rho, three_p, q[3], pi[9]).
pub fn moments(
    p: &[[f64; 3]],
    w: &[f64],
    a: &[f64; 3],
    mass: f64,
) -> (f64, f64, [f64; 3], [f64; 9]) {
    let v = a[0] * a[1] * a[2];
    let acc = p
        .par_iter()
        .zip(w.par_iter())
        .fold(
            || [0.0f64; 14],
            |mut s, (pp, ww)| {
                let (e, lam, ev) = node_geom(pp, a, mass);
                let x = if e > 0.0 { lam / e } else { 0.0 };
                let wu = *ww;
                let base = wu * e; // f·E     → J^(0)
                let l2 = base * x * x; // f·λ²/E  → 3p, π
                s[0] += base; // ρ
                s[1] += l2; // 3p
                for i in 0..3 {
                    s[2 + i] += base * x * ev[i]; // q_a  (l=1, i=0)
                    for j in 0..3 {
                        s[5 + i * 3 + j] += l2 * ev[i] * ev[j];
                    }
                }
                s
            },
        )
        .reduce(
            || [0.0f64; 14],
            |mut a1, b| {
                for k in 0..14 {
                    a1[k] += b[k];
                }
                a1
            },
        );
    let inv = 1.0 / v;
    let rho = acc[0] * inv;
    let three_p = acc[1] * inv;
    let q = [acc[2] * inv, acc[3] * inv, acc[4] * inv];
    let mut pi = [0.0f64; 9];
    let trace = (acc[5] + acc[5 + 4] + acc[5 + 8]) * inv / 3.0;
    for i in 0..3 {
        for j in 0..3 {
            pi[i * 3 + j] = acc[5 + i * 3 + j] * inv - if i == j { trace } else { 0.0 };
        }
    }
    (rho, three_p, q, pi)
}

/// ★ (Ṗ, Ẇ) — 특성곡선 + Liouville 측도 무게 (K4a/K5b).
pub fn kinetic_rhs(
    p: &[[f64; 3]],
    w: &[f64],
    a: &[f64; 3],
    mass: f64,
    av: f64,
    dp: &mut [[f64; 3]],
    dw: &mut [f64],
) {
    let a2 = [a[0] * a[0], a[1] * a[1], a[2] * a[2]];
    dp.par_iter_mut()
        .zip(dw.par_iter_mut())
        .zip(p.par_iter().zip(w.par_iter()))
        .for_each(|((op, ow), (pp, ww))| {
            let pu = [pp[0] / a2[0], pp[1] / a2[1], pp[2] / a2[2]];
            let e = (mass * mass + pp[0] * pu[0] + pp[1] * pu[1] + pp[2] * pu[2]).sqrt();
            let inv = 1.0 / e;
            op[0] = av * (pp[1] * pu[1] + pp[2] * pu[2]) * inv;
            op[1] = -av * pu[0] * pp[1] * inv;
            op[2] = -av * pu[0] * pp[2] * inv;
            *ow = *ww * (-2.0 * av * pu[0] * inv);
        });
}

/// ★ q₁ 과 그 원천항 — D2b 의 운동량 법칙 검사용 (유한차분 없이).
///
/// ```text
/// q̇₁ = −(h₁+3H)q₁ + (A/(a₁V)) Σ W λ²(1 − 3ê₁²)/E
/// ```
pub fn flux_rate(p: &[[f64; 3]], w: &[f64], a: &[f64; 3], mass: f64, av: f64) -> (f64, f64) {
    let v = a[0] * a[1] * a[2];
    let s = p
        .par_iter()
        .zip(w.par_iter())
        .fold(
            || (0.0f64, 0.0f64),
            |mut s, (pp, ww)| {
                let (e, lam, ev) = node_geom(pp, a, mass);
                s.0 += *ww * pp[0];
                s.1 += *ww * lam * lam * (1.0 - 3.0 * ev[0] * ev[0]) / e;
                s
            },
        )
        .reduce(|| (0.0, 0.0), |x, y| (x.0 + y.0, x.1 + y.1));
    (s.0 / (a[0] * v), s.1 * av / (a[0] * v))
}

// ═══════════════════════════════════════ 기하 (K5a 의 공간 Einstein 식)
/// u_i = ä_i/a_i — [[0,1,1],[1,0,1],[1,1,0]] 의 역: u_i = ½Σr − r_i.
pub fn accelerations(a: &[f64; 3], h: &[f64; 3], av: f64, p: f64, pid: &[f64; 3]) -> [f64; 3] {
    let c = av * av / (a[0] * a[0]);
    let r = [
        c - h[1] * h[2] - p - pid[0],
        c - h[0] * h[2] - p - pid[1],
        c - h[0] * h[1] - p - pid[2],
    ];
    let s = (r[0] + r[1] + r[2]) * 0.5;
    [s - r[0], s - r[1], s - r[2]]
}

/// (F, C) — Friedmann·Codazzi 잔차.
pub fn constraints(
    a: &[f64; 3],
    h: &[f64; 3],
    av: f64,
    rho: f64,
    q1: f64,
) -> (f64, f64, f64, [f64; 3]) {
    let hh = (h[0] + h[1] + h[2]) / 3.0;
    let sig = [h[0] - hh, h[1] - hh, h[2] - hh];
    let s2 = 0.5 * (sig[0] * sig[0] + sig[1] * sig[1] + sig[2] * sig[2]);
    let f = 3.0 * hh * hh - rho - s2 - 3.0 * av * av / (a[0] * a[0]);
    let c = 3.0 * sig[0] * av / a[0] + q1;
    (f, c, hh, sig)
}

/// ★ D2 · 최소노름 Gauss-Newton 투영 (h 만 움직인다).
pub fn project(a: &[f64; 3], da: &mut [f64; 3], av: f64, rho: f64, q1: f64, iters: usize) {
    for _ in 0..iters {
        let h = [da[0] / a[0], da[1] / a[1], da[2] / a[2]];
        let (f, c, hh, sig) = constraints(a, &h, av, rho, q1);
        let j0 = [2.0 * hh - sig[0], 2.0 * hh - sig[1], 2.0 * hh - sig[2]];
        let k = 3.0 * av / a[0];
        let j1 = [k * (1.0 - 1.0 / 3.0), -k / 3.0, -k / 3.0];
        // JJᵀ (2×2)
        let a00 = j0[0] * j0[0] + j0[1] * j0[1] + j0[2] * j0[2];
        let a01 = j0[0] * j1[0] + j0[1] * j1[1] + j0[2] * j1[2];
        let a11 = j1[0] * j1[0] + j1[1] * j1[1] + j1[2] * j1[2];
        let det = a00 * a11 - a01 * a01;
        if det.abs() < 1e-300 {
            return;
        }
        let l0 = (a11 * f - a01 * c) / det;
        let l1 = (-a01 * f + a00 * c) / det;
        for i in 0..3 {
            da[i] -= (j0[i] * l0 + j1[i] * l1) * a[i];
        }
    }
}

// ═══════════════════════════════════════ ★★ 결합 진화 (RK4)
pub struct Record {
    pub t: Vec<f64>,
    pub a: Vec<[f64; 3]>,
    pub h: Vec<[f64; 3]>,
    pub sigma1: Vec<f64>,
    pub rho: Vec<f64>,
    pub q1: Vec<f64>,
    pub pi: Vec<[f64; 3]>,
    pub friedmann: Vec<f64>,
    pub codazzi: Vec<f64>,
    pub offdiag: Vec<f64>,
    pub hdot_spatial: Vec<f64>,
    pub hdot_ray: Vec<f64>,
    pub qdot_node: Vec<f64>,
    pub qdot_law: Vec<f64>,
    pub qdot_naive: Vec<f64>,
}

struct Stage {
    da: [f64; 3],
    acc: [f64; 3],
    dp: Vec<[f64; 3]>,
    dw: Vec<f64>,
}

fn rhs(a: &[f64; 3], da: &[f64; 3], p: &[[f64; 3]], w: &[f64], mass: f64, av: f64) -> Stage {
    let (_, three_p, _, pi) = moments(p, w, a, mass);
    let h = [da[0] / a[0], da[1] / a[1], da[2] / a[2]];
    let pid = [pi[0], pi[4], pi[8]];
    let u = accelerations(a, &h, av, three_p / 3.0, &pid);
    let mut dp = vec![[0.0f64; 3]; p.len()];
    let mut dw = vec![0.0f64; w.len()];
    kinetic_rhs(p, w, a, mass, av, &mut dp, &mut dw);
    Stage {
        da: *da,
        acc: [u[0] * a[0], u[1] * a[1], u[2] * a[2]],
        dp,
        dw,
    }
}

/// ★★ K5b 의 `evolve_coupled` 전체 — 노드가 Python 으로 되돌아오지 않는다.
pub fn evolve(
    p0: &[[f64; 3]],
    w0: &[f64],
    a0: &[f64; 3],
    da0: &[f64; 3],
    mass: f64,
    av: f64,
    t_end: f64,
    nsteps: usize,
    do_project: bool,
) -> Record {
    let n = p0.len();
    let mut a = *a0;
    let mut da = *da0;
    let mut p = p0.to_vec();
    let mut w = w0.to_vec();
    let dt = t_end / nsteps as f64;
    let mut r = Record {
        t: vec![],
        a: vec![],
        h: vec![],
        sigma1: vec![],
        rho: vec![],
        q1: vec![],
        pi: vec![],
        friedmann: vec![],
        codazzi: vec![],
        offdiag: vec![],
        hdot_spatial: vec![],
        hdot_ray: vec![],
        qdot_node: vec![],
        qdot_law: vec![],
        qdot_naive: vec![],
    };
    let mut pa = vec![[0.0f64; 3]; n];
    let mut wa = vec![0.0f64; n];

    for k in 0..=nsteps {
        let (rho, three_p, q, pi) = moments(&p, &w, &a, mass);
        let h = [da[0] / a[0], da[1] / a[1], da[2] / a[2]];
        let (f, c, hh, sig) = constraints(&a, &h, av, rho, q[0]);
        let pid = [pi[0], pi[4], pi[8]];
        let u = accelerations(&a, &h, av, three_p / 3.0, &pid);
        let s2 = 0.5 * (sig[0] * sig[0] + sig[1] * sig[1] + sig[2] * sig[2]);
        let mut off: f64 = q[1].abs().max(q[2].abs());
        for i in 0..3 {
            for j in 0..3 {
                if i != j {
                    off = off.max(pi[i * 3 + j].abs());
                }
            }
        }
        let (qn, src) = flux_rate(&p, &w, &a, mass, av);
        r.t.push(k as f64 * dt);
        r.a.push(a);
        r.h.push(h);
        r.sigma1.push(sig[0]);
        r.rho.push(rho);
        r.q1.push(q[0]);
        r.pi.push(pid);
        r.friedmann.push(f);
        r.codazzi.push(c);
        r.offdiag.push(off / rho);
        r.hdot_spatial
            .push((u[0] + u[1] + u[2]) / 3.0 - (h[0] * h[0] + h[1] * h[1] + h[2] * h[2]) / 3.0);
        r.hdot_ray
            .push(-hh * hh - 2.0 / 3.0 * s2 - (rho + three_p) / 6.0);
        r.qdot_node.push(-(h[0] + 3.0 * hh) * qn + src);
        r.qdot_law
            .push(-(4.0 * hh + sig[0]) * qn - 3.0 * av / a[0] * pid[0]);
        r.qdot_naive.push(-(4.0 * hh + sig[0]) * qn);
        if k == nsteps {
            break;
        }

        // RK4 — 상태 (a, ȧ, P, W)
        let s1 = rhs(&a, &da, &p, &w, mass, av);
        let (a2, d2) = axpy2(&a, &da, &s1, 0.5 * dt);
        stage_state(&p, &w, &s1, 0.5 * dt, &mut pa, &mut wa);
        let s2s = rhs(&a2, &d2, &pa, &wa, mass, av);
        let (a3, d3) = axpy2(&a, &da, &s2s, 0.5 * dt);
        stage_state(&p, &w, &s2s, 0.5 * dt, &mut pa, &mut wa);
        let s3 = rhs(&a3, &d3, &pa, &wa, mass, av);
        let (a4, d4) = axpy2(&a, &da, &s3, dt);
        stage_state(&p, &w, &s3, dt, &mut pa, &mut wa);
        let s4 = rhs(&a4, &d4, &pa, &wa, mass, av);

        for i in 0..3 {
            a[i] += dt / 6.0 * (s1.da[i] + 2.0 * s2s.da[i] + 2.0 * s3.da[i] + s4.da[i]);
            da[i] += dt / 6.0 * (s1.acc[i] + 2.0 * s2s.acc[i] + 2.0 * s3.acc[i] + s4.acc[i]);
        }
        p.par_iter_mut()
            .zip(w.par_iter_mut())
            .enumerate()
            .for_each(|(j, (pp, ww))| {
                for c in 0..3 {
                    pp[c] += dt / 6.0
                        * (s1.dp[j][c] + 2.0 * s2s.dp[j][c] + 2.0 * s3.dp[j][c] + s4.dp[j][c]);
                }
                *ww += dt / 6.0 * (s1.dw[j] + 2.0 * s2s.dw[j] + 2.0 * s3.dw[j] + s4.dw[j]);
            });
        if do_project {
            let (rho2, _, q2, _) = moments(&p, &w, &a, mass);
            project(&a, &mut da, av, rho2, q2[0], 3);
        }
    }
    r
}

#[inline]
fn axpy2(a: &[f64; 3], da: &[f64; 3], s: &Stage, c: f64) -> ([f64; 3], [f64; 3]) {
    (
        [a[0] + c * s.da[0], a[1] + c * s.da[1], a[2] + c * s.da[2]],
        [
            da[0] + c * s.acc[0],
            da[1] + c * s.acc[1],
            da[2] + c * s.acc[2],
        ],
    )
}

#[inline]
fn stage_state(p: &[[f64; 3]], w: &[f64], s: &Stage, c: f64, pa: &mut [[f64; 3]], wa: &mut [f64]) {
    pa.par_iter_mut()
        .zip(wa.par_iter_mut())
        .enumerate()
        .for_each(|(j, (op, ow))| {
            for k in 0..3 {
                op[k] = p[j][k] + c * s.dp[j][k];
            }
            *ow = w[j] + c * s.dw[j];
        });
}

// ═══════════════════════════════════════ 단위시험 (Python 오라클과는 차등테스트)
#[cfg(test)]
mod tests {
    use super::*;

    fn toy() -> (Vec<[f64; 3]>, Vec<f64>) {
        let mut p = vec![];
        let mut w = vec![];
        for i in 0..40 {
            let t = i as f64 * 0.17;
            p.push([t.cos() * (1.0 + t), t.sin() * 0.8, (0.3 * t).cos() * 0.6]);
            w.push(0.01 + 0.001 * i as f64);
        }
        (p, w)
    }

    #[test]
    fn pi_is_traceless() {
        let (p, w) = toy();
        let a = [1.0, 0.9, 1.2];
        let (_, _, _, pi) = moments(&p, &w, &a, 0.6);
        assert!((pi[0] + pi[4] + pi[8]).abs() < 1e-12);
    }

    #[test]
    fn accelerations_invert_the_spatial_equations() {
        let a = [1.1, 0.9, 1.3];
        let h = [0.4, 0.2, 0.35];
        let u = [0.5, -0.3, 0.2];
        let av = 0.7;
        let c = av * av / (a[0] * a[0]);
        // G_ii = c − u_j − u_k − h_j h_k 로 물질을 역산
        let g = [
            c - u[1] - u[2] - h[1] * h[2],
            c - u[0] - u[2] - h[0] * h[2],
            c - u[0] - u[1] - h[0] * h[1],
        ];
        let p = (g[0] + g[1] + g[2]) / 3.0;
        let pid = [g[0] - p, g[1] - p, g[2] - p];
        let back = accelerations(&a, &h, av, p, &pid);
        for i in 0..3 {
            assert!((back[i] - u[i]).abs() < 1e-12, "{} {}", back[i], u[i]);
        }
    }

    #[test]
    fn projection_restores_both_constraints() {
        let a = [1.0, 0.95, 1.05];
        let mut da = [5.05, 4.68, 5.21];
        let (rho, q1, av) = (73.0, 0.004, 0.7);
        project(&a, &mut da, av, rho, q1, 6);
        let h = [da[0] / a[0], da[1] / a[1], da[2] / a[2]];
        let (f, c, _, _) = constraints(&a, &h, av, rho, q1);
        assert!(f.abs() / rho < 1e-14, "F {}", f);
        assert!(c.abs() / rho < 1e-14, "C {}", c);
    }

    #[test]
    fn zero_a_kills_the_weight_drift() {
        let (p, w) = toy();
        let a = [1.0, 0.9, 1.2];
        let mut dp = vec![[0.0; 3]; p.len()];
        let mut dw = vec![0.0; w.len()];
        kinetic_rhs(&p, &w, &a, 0.6, 0.0, &mut dp, &mut dw);
        assert!(dw.iter().all(|x| *x == 0.0));
        assert!(dp.iter().all(|v| v.iter().all(|x| *x == 0.0)));
    }
}

// ═══════════════════════════════════════ R2 · 특성곡선 적분 (배경 처방)
#[inline]
fn bg_a(a0: &[f64; 3], rate: &[f64; 3], t: f64) -> [f64; 3] {
    [
        a0[0] * (rate[0] * t).exp(),
        a0[1] * (rate[1] * t).exp(),
        a0[2] * (rate[2] * t).exp(),
    ]
}

#[inline]
fn char_rhs(p: &[[f64; 3]], a: &[f64; 3], mass: f64, av: f64, out: &mut [[f64; 3]]) {
    let a2 = [a[0] * a[0], a[1] * a[1], a[2] * a[2]];
    out.par_iter_mut().zip(p.par_iter()).for_each(|(o, pp)| {
        let pu = [pp[0] / a2[0], pp[1] / a2[1], pp[2] / a2[2]];
        let e = (mass * mass + pp[0] * pu[0] + pp[1] * pu[1] + pp[2] * pu[2]).sqrt();
        let inv = 1.0 / e;
        o[0] = av * (pp[1] * pu[1] + pp[2] * pu[2]) * inv;
        o[1] = -av * pu[0] * pp[1] * inv;
        o[2] = -av * pu[0] * pp[2] * inv;
    });
}

/// ★ K4b 의 **역방향 특성곡선** — 시각 t 의 P 를 t=0 까지 거슬러 적분 (RK4, 음의 스텝).
pub fn back_trace(
    p0: &[[f64; 3]],
    a0: &[f64; 3],
    rate: &[f64; 3],
    mass: f64,
    av: f64,
    t: f64,
    nsteps: usize,
) -> Vec<[f64; 3]> {
    let n = p0.len();
    let mut p = p0.to_vec();
    let dt = -t / nsteps as f64;
    let (mut k1, mut k2, mut k3, mut k4) = (
        vec![[0.0; 3]; n],
        vec![[0.0; 3]; n],
        vec![[0.0; 3]; n],
        vec![[0.0; 3]; n],
    );
    let mut tmp = vec![[0.0f64; 3]; n];
    for step in 0..nsteps {
        let s = t + step as f64 * dt;
        char_rhs(&p, &bg_a(a0, rate, s), mass, av, &mut k1);
        blend(&p, &k1, 0.5 * dt, &mut tmp);
        char_rhs(&tmp, &bg_a(a0, rate, s + 0.5 * dt), mass, av, &mut k2);
        blend(&p, &k2, 0.5 * dt, &mut tmp);
        char_rhs(&tmp, &bg_a(a0, rate, s + 0.5 * dt), mass, av, &mut k3);
        blend(&p, &k3, dt, &mut tmp);
        char_rhs(&tmp, &bg_a(a0, rate, s + dt), mass, av, &mut k4);
        p.par_iter_mut().enumerate().for_each(|(j, pp)| {
            for c in 0..3 {
                pp[c] += dt / 6.0 * (k1[j][c] + 2.0 * k2[j][c] + 2.0 * k3[j][c] + k4[j][c]);
            }
        });
    }
    p
}

#[inline]
fn blend(p: &[[f64; 3]], k: &[[f64; 3]], c: f64, out: &mut [[f64; 3]]) {
    out.par_iter_mut().enumerate().for_each(|(j, o)| {
        for i in 0..3 {
            o[i] = p[j][i] + c * k[j][i];
        }
    });
}

/// ★ K5b 의 순방향 Liouville 밀기 — (P, W) 를 t 까지 (배경 처방).
pub fn push_nodes(
    p0: &[[f64; 3]],
    w0: &[f64],
    a0: &[f64; 3],
    rate: &[f64; 3],
    mass: f64,
    av: f64,
    t: f64,
    nsteps: usize,
    measure: bool,
) -> (Vec<[f64; 3]>, Vec<f64>) {
    let n = p0.len();
    let mut p = p0.to_vec();
    let mut w = w0.to_vec();
    let dt = t / nsteps as f64;
    let mut kp = vec![vec![[0.0f64; 3]; n]; 4];
    let mut kw = vec![vec![0.0f64; n]; 4];
    let (mut tp, mut tw) = (vec![[0.0f64; 3]; n], vec![0.0f64; n]);
    for step in 0..nsteps {
        let s = step as f64 * dt;
        let cs = [0.0, 0.5 * dt, 0.5 * dt, dt];
        let ts = [s, s + 0.5 * dt, s + 0.5 * dt, s + dt];
        for stage in 0..4 {
            if stage == 0 {
                tp.copy_from_slice(&p);
                tw.copy_from_slice(&w);
            } else {
                let (pk, wk) = (&kp[stage - 1], &kw[stage - 1]);
                tp.par_iter_mut()
                    .zip(tw.par_iter_mut())
                    .enumerate()
                    .for_each(|(j, (op, ow))| {
                        for i in 0..3 {
                            op[i] = p[j][i] + cs[stage] * pk[j][i];
                        }
                        *ow = w[j] + cs[stage] * wk[j];
                    });
            }
            let a = bg_a(a0, rate, ts[stage]);
            if measure {
                let (dp, dw) = (&mut kp[stage], &mut kw[stage]);
                kinetic_rhs(&tp, &tw, &a, mass, av, dp, dw);
            } else {
                char_rhs(&tp, &a, mass, av, &mut kp[stage]);
                kw[stage].iter_mut().for_each(|x| *x = 0.0);
            }
        }
        p.par_iter_mut()
            .zip(w.par_iter_mut())
            .enumerate()
            .for_each(|(j, (pp, ww))| {
                for c in 0..3 {
                    pp[c] += dt / 6.0
                        * (kp[0][j][c] + 2.0 * kp[1][j][c] + 2.0 * kp[2][j][c] + kp[3][j][c]);
                }
                *ww += dt / 6.0 * (kw[0][j] + 2.0 * kw[1][j] + 2.0 * kw[2][j] + kw[3][j]);
            });
    }
    (p, w)
}
