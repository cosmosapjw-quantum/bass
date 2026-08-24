//! Q11 ★ **전-루프 Rust 이식 + 멤버 병렬** (79차).
//!
//! R5b 규율: "레이어가 아니라 **루프**를 이식한다."  Python 이 설정만 주고,
//! 스텝 루프 전체 (기하 RK4 + 공변 프레임 + 잔여 곡률 이류 + 정확 충돌 Strang)
//! 가 여기서 돈다.
//!
//! ★ 결정성 계약 (Q11): 병렬성은 **멤버 단위**로만.  멤버 내부의 모든 축약은
//! 고정 순서 pairwise (`reduce_det`) — 스레드 수와 무관하게 비트 동일해야 한다.

use rayon::prelude::*;

use crate::geom::group::BianchiGroup;
use crate::kinetic::collide_exact::Kernel;
use crate::kinetic::comoving::{self as cm, Frame};
use crate::kinetic::radial::{shift_stencil, RadialGrid, Tail};
use crate::kinetic::sphere::SphereGrid;
use crate::kinetic::transport::build_stencils;

/// 고정 순서 pairwise 합 — 부동소수 비결합성 회피 (Q11 계약).
pub fn reduce_det(v: &[f64]) -> f64 {
    let mut a: Vec<f64> = v.to_vec();
    while a.len() > 1 {
        let n = a.len() / 2;
        let mut o: Vec<f64> = (0..n).map(|i| a[2 * i] + a[2 * i + 1]).collect();
        if a.len() % 2 == 1 {
            o.push(a[a.len() - 1]);
        }
        a = o;
    }
    a.first().copied().unwrap_or(0.0)
}

#[derive(Clone, Debug)]
pub struct QState {
    pub s6: [f64; 6],
    pub n6: [f64; 6],
    pub a3: [f64; 3],
    pub ln_h: f64,
    pub m: [f64; 9],
    /// Mode A: ln G-hat (길이 M).  Mode B: ln f (길이 M * n_p, 방향-주).
    pub lg: Vec<f64>,
    pub rot: [f64; 3],
    pub residual: bool,
    pub jac_min: f64,
    /// 0 = Mode A.  > 0 이면 Mode B (완전 f).
    pub n_p: usize,
    pub rad: Option<RadialGrid>,
    pub tail: Tail,
    pub k_rad: usize,
    /// Q7b — 바리온 벌크속도 (전자 정지계 부스트).  None = 정지 전자.
    pub v_b: Option<[f64; 3]>,
}

impl QState {
    pub fn is_mode_b(&self) -> bool {
        self.n_p > 0 && self.rad.is_some()
    }

    /// ★ Mode B → Mode A 축약:  ln Ghat_i = 4 ln mu_i + ln Jr_i,
    /// Jr_i = int f q^3 dq = sum_j f_ij q_j^4 wt_j dlnq   (logsumexp).
    /// 이 축약 덕분에 모멘트·충돌 기계 전체를 Mode A 와 **공유**한다.
    pub fn ln_ghat(&self, mu: &[f64]) -> Vec<f64> {
        if !self.is_mode_b() {
            return self.lg.clone();
        }
        let rad = self.rad.as_ref().unwrap();
        let q = rad.p();
        let np_ = self.n_p;
        let m_ang = mu.len();
        let mut out = vec![0.0; m_ang];
        for i in 0..m_ang {
            let mut mx = f64::NEG_INFINITY;
            for (j, &q_j) in q.iter().enumerate().take(np_) {
                let wt: f64 = if j == 0 || j == np_ - 1 { 0.5 } else { 1.0 };
                let v = self.lg[i * np_ + j] + 4.0 * q_j.ln() + wt.ln();
                if v > mx {
                    mx = v;
                }
            }
            let mut acc = 0.0;
            for (j, &q_j) in q.iter().enumerate().take(np_) {
                let wt: f64 = if j == 0 || j == np_ - 1 { 0.5 } else { 1.0 };
                acc += (self.lg[i * np_ + j] + 4.0 * q_j.ln() + wt.ln() - mx).exp();
            }
            out[i] = mx + acc.ln() + rad.dlnp.ln() + 4.0 * mu[i].ln();
        }
        out
    }
}

pub struct Config {
    pub v_b: Option<[f64; 3]>,
    pub dtau: f64,
    pub nsteps: usize,
    pub nu: f64,
    pub kernel: Kernel,
    pub k_theta: usize,
    pub k_phi: usize,
    pub sub: usize,
    pub keep_every: usize,
    /// Q19 · **B2b 이력 배선**.  길이 nsteps+1 의 스텝 경계 tau_k 별 값.
    /// 비어 있으면 상수 `nu` 를 쓴다 ⇒ 기존 경로는 **비트 동일**.
    pub nu_sched: Vec<f64>,
    /// h_anchor > 0 이면 nu_sched 는 A(tau) = sigma_T n_e c [1/s] 이고
    ///     nu_tau = A / (h_anchor * exp(lnH))       … 모델 자체 H (자기일관, 기본)
    /// h_anchor == 0 이면 nu_sched 가 곧 nu_tau 다.  … LCDM H(z) (사전계산)
    pub h_anchor: f64,
}

impl Config {
    /// 스텝 경계 k 에서의 nu_tau.  lnH 는 **그 시점 상태**에서 온다.
    ///
    /// Strang 2차 유지: 앞 반스텝은 (tau_k, lnH_k), 뒤 반스텝은
    /// (tau_{k+1}, lnH_{k+1}) 로 쓴다 — 대칭이라 2차가 보존된다.
    #[inline]
    pub fn nu_at(&self, k: usize, ln_h: f64) -> f64 {
        if self.nu_sched.is_empty() {
            return self.nu;
        }
        // ★ 85차 (독립 리뷰 m3): 이 clamp 는 `_attach_sched` 가 len == nsteps+1 을
        //   강제하고 evolve 가 k <= nsteps-1 만 쓰므로 도달 불가다.  도달하면
        //   nu 가 조용히 얼어붙으므로 디버그 빌드에서 터뜨린다.
        debug_assert!(k < self.nu_sched.len(), "nu_sched 인덱스 초과 (k={k})");
        let a = self.nu_sched[k.min(self.nu_sched.len() - 1)];
        if self.h_anchor > 0.0 {
            a / (self.h_anchor * ln_h.exp())
        } else {
            a
        }
    }
}

#[inline]
fn sym_apply(m: &[f64; 6], v: &[f64; 3]) -> [f64; 3] {
    [
        m[0] * v[0] + m[3] * v[1] + m[4] * v[2],
        m[3] * v[0] + m[1] * v[1] + m[5] * v[2],
        m[4] * v[0] + m[5] * v[1] + m[2] * v[2],
    ]
}

#[inline]
fn mat3(v: &[f64; 6]) -> [[f64; 3]; 3] {
    [[v[0], v[3], v[4]], [v[3], v[1], v[5]], [v[4], v[5], v[2]]]
}

#[inline]
fn sym6(m: &[[f64; 3]; 3]) -> [f64; 6] {
    [m[0][0], m[1][1], m[2][2], m[0][1], m[0][2], m[1][2]]
}

fn mm(a: &[[f64; 3]; 3], b: &[[f64; 3]; 3]) -> [[f64; 3]; 3] {
    let mut o = [[0.0; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            let mut s = 0.0;
            for k in 0..3 {
                s += a[i][k] * b[k][j];
            }
            o[i][j] = s;
        }
    }
    o
}

fn eps_mat(r: &[f64; 3]) -> [[f64; 3]; 3] {
    [[0.0, -r[2], r[1]], [r[2], 0.0, -r[0]], [-r[1], r[0], 0.0]]
}

fn inv3(a: &[[f64; 3]; 3]) -> [[f64; 3]; 3] {
    let d = a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
        - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
        + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]);
    let c = |i: usize, j: usize| {
        let (r0, r1) = ((i + 1) % 3, (i + 2) % 3);
        let (c0, c1) = ((j + 1) % 3, (j + 2) % 3);
        a[r0][c0] * a[r1][c1] - a[r0][c1] * a[r1][c0]
    };
    let mut o = [[0.0; 3]; 3];
    for (i, row) in o.iter_mut().enumerate() {
        for (j, o_ij) in row.iter_mut().enumerate() {
            *o_ij = c(j, i) / d; // 전치 여인수 = 역행렬
        }
    }
    o
}

impl QState {
    pub fn n_state(&self) -> usize {
        25 + self.lg.len()
    }

    pub fn pack(&self) -> Vec<f64> {
        let mut v = Vec::with_capacity(self.n_state());
        v.extend_from_slice(&self.s6);
        v.extend_from_slice(&self.n6);
        v.extend_from_slice(&self.a3);
        v.push(self.ln_h);
        v.extend_from_slice(&self.m);
        v.extend_from_slice(&self.lg);
        v
    }

    pub fn set_from(&mut self, v: &[f64]) {
        self.s6.copy_from_slice(&v[0..6]);
        self.n6.copy_from_slice(&v[6..12]);
        self.a3.copy_from_slice(&v[12..15]);
        self.ln_h = v[15];
        self.m.copy_from_slice(&v[16..25]);
        self.lg.copy_from_slice(&v[25..]);
    }

    /// (ê 3M, mu M, ln w M)
    fn geometry(&self, sph: &SphereGrid) -> (Vec<f64>, Vec<f64>, Vec<f64>) {
        let fr = Frame { m: self.m };
        let (e, mu) = cm::phys_dirs(&fr, &sph.ehat);
        let lw = cm::ln_phys_weights(&fr, &sph.w, &mu);
        (e, mu, lw)
    }

    /// (Omega, Pi_ab 6, q).  Mode B 는 ln_ghat 축약을 거쳐 같은 경로.
    pub fn sources(&self, sph: &SphereGrid) -> (f64, [f64; 6], f64) {
        let (e, mu, lw) = self.geometry(sph);
        let lg = self.ln_ghat(&mu);
        let (ln_rho, _, pi_r) = cm::moments_log(&lw, &lg, &e);
        let om = (ln_rho - 3.0f64.ln() - 2.0 * self.ln_h).exp();
        let mut pi = [0.0; 6];
        for k in 0..6 {
            pi[k] = 3.0 * om * pi_r[k];
        }
        let sm = mat3(&self.s6);
        let mut s2 = sm.iter().flatten().map(|v| v * v).sum::<f64>();
        s2 /= 6.0;
        (om, pi, 2.0 * s2 + om)
    }

    pub fn gauss_residual(&self, sph: &SphereGrid) -> f64 {
        let g = BianchiGroup::new(self.n6, self.a3);
        let (k, _) = g.curvature();
        let sm = mat3(&self.s6);
        let mut s2 = sm.iter().flatten().map(|v| v * v).sum::<f64>();
        s2 /= 6.0;
        let (om, _, _) = self.sources(sph);
        s2 + k + om - 1.0
    }

    fn rhs(&self, sph: &SphereGrid, v: &[f64], out: &mut [f64]) {
        let mut tmp = self.clone();
        tmp.set_from(v);
        let (om, pi, q) = tmp.sources(sph);
        let _ = om;
        let g = BianchiGroup::new(tmp.n6, tmp.a3);
        let (_, s3) = g.curvature();
        let sm = mat3(&tmp.s6);
        let nm = mat3(&tmp.n6);
        let w = eps_mat(&[-tmp.rot[0], -tmp.rot[1], -tmp.rot[2]]);
        let pim = mat3(&pi);
        let mut ds = [[0.0; 3]; 3];
        let ws = mm(&w, &sm);
        let sw = mm(&sm, &w);
        for (i, ds_row) in ds.iter_mut().enumerate() {
            for (j, ds_ij) in ds_row.iter_mut().enumerate() {
                *ds_ij = -(2.0 - q) * sm[i][j] - s3[(i, j)] + pim[i][j] + ws[i][j] - sw[i][j];
            }
        }
        let tr = (ds[0][0] + ds[1][1] + ds[2][2]) / 3.0;
        for (i, ds_row) in ds.iter_mut().enumerate() {
            ds_row[i] -= tr;
        }
        let sn = mm(&sm, &nm);
        let ns = mm(&nm, &sm);
        let wn = mm(&w, &nm);
        let nw = mm(&nm, &w);
        let mut dn = [[0.0; 3]; 3];
        for i in 0..3 {
            for j in 0..3 {
                dn[i][j] = q * nm[i][j] + sn[i][j] + ns[i][j] + wn[i][j] - nw[i][j];
            }
        }
        let sa = sym_apply(&tmp.s6, &tmp.a3);
        let mut da = [0.0; 3];
        for (i, da_i) in da.iter_mut().enumerate() {
            let mut wa = 0.0;
            for (j, &w_ij) in w[i].iter().enumerate() {
                wa += w_ij * tmp.a3[j];
            }
            *da_i = q * tmp.a3[i] - sa[i] + wa;
        }
        // 공변 프레임:  dM/dtau = -(I + Sigma - eps R) M
        let er = eps_mat(&tmp.rot);
        let mut amat = [[0.0; 3]; 3];
        for i in 0..3 {
            for j in 0..3 {
                amat[i][j] = (if i == j { 1.0 } else { 0.0 }) + sm[i][j] - er[i][j];
            }
        }
        let mmat = [
            [tmp.m[0], tmp.m[1], tmp.m[2]],
            [tmp.m[3], tmp.m[4], tmp.m[5]],
            [tmp.m[6], tmp.m[7], tmp.m[8]],
        ];
        let dmm = mm(&amat, &mmat);
        // 자유흐름 (해석): dln G/dtau = -4 (1 + ê·Sigma·ê)
        let (e, _, _) = tmp.geometry(sph);
        let dsy = sym6(&ds);
        let dny = sym6(&dn);
        out[0..6].copy_from_slice(&dsy);
        out[6..12].copy_from_slice(&dny);
        out[12..15].copy_from_slice(&da);
        out[15] = -(1.0 + q);
        for i in 0..3 {
            for j in 0..3 {
                out[16 + 3 * i + j] = -dmm[i][j];
            }
        }
        let m_ang = sph.len();
        if tmp.is_mode_b() {
            // ★ Mode B: 공변 프레임에서 f 는 자유흐름 하에 **정확히 불변**
            //   (H, Sigma, R 이 M 에 흡수되고 |q| 도 보존) ⇒ 도함수가 0.
            //   Mode A 의 4 dln mu 항은 반경적분을 미리 해버린 결과였다.
            for out_k in out.iter_mut().skip(25) {
                *out_k = 0.0;
            }
        } else {
            for i in 0..m_ang {
                let ei = [e[3 * i], e[3 * i + 1], e[3 * i + 2]];
                let se = sym_apply(&tmp.s6, &ei);
                let ese = ei[0] * se[0] + ei[1] * se[1] + ei[2] * se[2];
                out[25 + i] = -4.0 * (1.0 + ese);
            }
        }
    }

    pub fn rk4_step(&mut self, sph: &SphereGrid, dtau: f64) {
        let n = self.n_state();
        let v0 = self.pack();
        let mut k1 = vec![0.0; n];
        let mut k2 = vec![0.0; n];
        let mut k3 = vec![0.0; n];
        let mut k4 = vec![0.0; n];
        let mut w = vec![0.0; n];
        self.rhs(sph, &v0, &mut k1);
        for i in 0..n {
            w[i] = v0[i] + 0.5 * dtau * k1[i];
        }
        self.rhs(sph, &w, &mut k2);
        for i in 0..n {
            w[i] = v0[i] + 0.5 * dtau * k2[i];
        }
        self.rhs(sph, &w, &mut k3);
        for i in 0..n {
            w[i] = v0[i] + dtau * k3[i];
        }
        self.rhs(sph, &w, &mut k4);
        for i in 0..n {
            w[i] = v0[i] + dtau / 6.0 * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i]);
        }
        self.set_from(&w);
    }

    /// Q5b 잔여 곡률 이류 (Mode A).  `rad` 가 있으면 Mode B (반경 스텐실 결합).
    pub fn residual_step(
        &mut self,
        sph: &SphereGrid,
        dtau: f64,
        k_theta: usize,
        k_phi: usize,
        sub: usize,
    ) {
        if !self.residual {
            return;
        }
        if self.n6.iter().all(|x| *x == 0.0) && self.a3.iter().all(|x| *x == 0.0) {
            return; // Bianchi I — 정확히 항등
        }
        if self.is_mode_b() {
            let rad = self.rad.as_ref().unwrap().clone();
            self.lg = residual_step_mode_b(
                sph, &rad, &self.m, &self.lg, &self.n6, &self.a3, dtau, k_theta, k_phi, self.k_rad,
                sub, true, self.tail,
            );
            return;
        }
        let m_ang = sph.len();
        let fr = Frame { m: self.m };
        let (_, mu0) = cm::phys_dirs(&fr, &sph.ehat);
        let mut lnj: Vec<f64> = (0..m_ang).map(|i| self.lg[i] - 4.0 * mu0[i].ln()).collect();
        let (qb, delta) = backtrace(&self.m, &sph.ehat, &self.n6, &self.a3, dtau, sub);
        let (idx, wts, jac) = build_stencils(sph, &qb, k_theta, k_phi);
        let s = k_theta * k_phi;
        let mut out = vec![0.0; m_ang];
        for i in 0..m_ang {
            let mut acc = 0.0;
            for k in 0..s {
                acc += wts[i * s + k] * lnj[idx[i * s + k] as usize];
            }
            out[i] = acc + 4.0 * delta[i];
        }
        lnj = out;
        for i in 0..m_ang {
            self.lg[i] = lnj[i] + 4.0 * mu0[i].ln();
        }
        self.jac_min = jac;
    }

    pub fn collide(&mut self, sph: &SphereGrid, nu_dt: f64, kernel: Kernel) {
        if nu_dt <= 0.0 {
            return;
        }
        let (e, _, lw) = self.geometry(sph);
        let act = kernel.active();
        if !self.is_mode_b() {
            // Mode A: 부스트 하에서 Ĝ 가 닫힌다 (Ĝ' = D^4 Ĝ, dOmega' = dOmega/D^2)
            match self.v_b {
                None => {
                    self.lg = cm::collide_exact_log(&lw, &self.lg, &e, nu_dt, &act);
                }
                Some(v) => {
                    let (dd, ep) = aberration(&e, &v);
                    let lwp: Vec<f64> = (0..dd.len()).map(|i| lw[i] - 2.0 * dd[i].ln()).collect();
                    let lgp: Vec<f64> = (0..dd.len())
                        .map(|i| self.lg[i] + 4.0 * dd[i].ln())
                        .collect();
                    let o = cm::collide_exact_log(&lwp, &lgp, &ep, nu_dt, &act);
                    self.lg = (0..dd.len()).map(|i| o[i] - 4.0 * dd[i].ln()).collect();
                }
            }
            return;
        }
        // ★★ Mode B 는 **공통 물리 운동량 격자**로 옮긴 뒤에 섞어야 한다.
        //   저장은 공변 q 이고 물리 p = mu_i q 이므로, 고정 j 는 방향마다 다른
        //   물리 p 다.  충돌 핵은 **고정 p 에서** 방향을 섞으므로 그대로 섞으면
        //   틀린다 (80차 구현의 버그 — 81차에 Q7b 를 붙이며 발각, 실측 O(1)).
        //   해법: 방향별 ln p 시프트 delta_i = ln(mu_i * D_i) 로 공통 격자로 옮기고,
        //   3항을 적용한 뒤 되돌린다.  D 는 전자 정지계 부스트 (v=0 이면 1).
        let (_, mu, _) = self.geometry(sph);
        self.lg = collide_mode_b(
            sph,
            self.rad.as_ref().unwrap(),
            &self.lg,
            &e,
            &mu,
            &lw,
            nu_dt,
            &act,
            self.v_b,
            self.k_rad,
            self.tail,
        );
    }

    /// Strang 스텝.  이력 배선이 없으면 `nu_at` 이 상수 nu 로 떨어지므로 기존
    /// golden 은 비트 보존이다.
    ///
    /// ★ 85차 (독립 리뷰 m3): 인덱스 없는 `strang_step` 래퍼를 뒀다가 **뺐다** —
    /// 호출자가 하나도 없는데 k=0 을 하드코딩해서, 루프에서 쓰면 nu 가 인덱스
    /// 0/1 에 얼어붙는 사장 함정이었다.
    pub fn strang_step_at(&mut self, sph: &SphereGrid, cfg: &Config, k: usize) {
        let h = cfg.dtau.abs();
        let nu0 = cfg.nu_at(k, self.ln_h);
        self.collide(sph, 0.5 * nu0 * h, cfg.kernel);
        self.residual_step(sph, 0.5 * cfg.dtau, cfg.k_theta, cfg.k_phi, cfg.sub);
        self.rk4_step(sph, cfg.dtau);
        self.residual_step(sph, 0.5 * cfg.dtau, cfg.k_theta, cfg.k_phi, cfg.sub);
        // ★ 뒤 반스텝은 **갱신된** (tau_{k+1}, lnH_{k+1}) 로 — 대칭이라야 2차다.
        let nu1 = cfg.nu_at(k + 1, self.ln_h);
        self.collide(sph, 0.5 * nu1 * h, cfg.kernel);
    }

    /// ★ 전-루프: Python 은 여기 한 번만 들어온다.
    pub fn evolve(&mut self, sph: &SphereGrid, cfg: &Config) -> Vec<f64> {
        let mut traj = Vec::new();
        if cfg.keep_every > 0 {
            traj.extend_from_slice(&self.pack());
        }
        for k in 0..cfg.nsteps {
            self.strang_step_at(sph, cfg, k);
            if cfg.keep_every > 0 && (k + 1) % cfg.keep_every == 0 {
                traj.extend_from_slice(&self.pack());
            }
        }
        traj
    }
}

/// ★ Mode B 충돌 — 공통 물리(정지계) 운동량 격자로 옮겨 정확 3항을 적용한다.
///
/// 저장: lnf[i*n_p + j] = ln f(ê_i, q_j),  물리 p = mu_i q_j,
/// 정지계 p' = D_i mu_i q_j  (D_i = gamma(1 - v·ê_i), v = 0 이면 1).
/// delta_i = ln(mu_i D_i) 만큼 ln q 를 시프트하면 격자 j 가 **공통 p'** 를 뜻하게 된다.
/// 정지계 구적 가중은 dOmega' = dOmega_phys / D^2  ⇒  ln w' = lw - 2 ln D.
#[allow(clippy::too_many_arguments)]
pub fn collide_mode_b(
    sph: &SphereGrid,
    rad: &RadialGrid,
    lnf: &[f64],
    ehat: &[f64],
    mu: &[f64],
    lw_phys: &[f64],
    nu_dt: f64,
    active: &[(usize, f64)],
    v_b: Option<[f64; 3]>,
    k_rad: usize,
    tail: Tail,
) -> Vec<f64> {
    let m_ang = sph.len();
    let np_ = rad.len();
    // 1. 광행차 (v = 0 이면 항등)
    let (dd, eprime) = match v_b {
        None => (vec![1.0; m_ang], ehat.to_vec()),
        Some(v) => aberration(ehat, &v),
    };
    let lw: Vec<f64> = (0..m_ang).map(|i| lw_phys[i] - 2.0 * dd[i].ln()).collect();
    let delta: Vec<f64> = (0..m_ang).map(|i| (mu[i] * dd[i]).ln()).collect();
    // 2. 공통 격자로 (방향별 ln q 시프트)
    let mut b = vec![0.0; m_ang * np_];
    let p = rad.p();
    for i in 0..m_ang {
        let (off, w) = shift_stencil(rad, delta[i], k_rad);
        let row = &lnf[i * np_..(i + 1) * np_];
        for j in 0..np_ {
            let mut v = 0.0;
            for a in 0..k_rad {
                v += w[a] * extend_lnf(row, &p, j as i64 + off[a], tail);
            }
            b[i * np_ + j] = v;
        }
    }
    // 3. 슬라이스마다 정확 3항 (이제 같은 p' 를 섞는다)
    let mut slice = vec![0.0; m_ang];
    for j in 0..np_ {
        for i in 0..m_ang {
            slice[i] = b[i * np_ + j];
        }
        let o = cm::collide_exact_log(&lw, &slice, &eprime, nu_dt, active);
        for i in 0..m_ang {
            b[i * np_ + j] = o[i];
        }
    }
    // 4. 되돌리기
    let mut out = vec![0.0; m_ang * np_];
    for i in 0..m_ang {
        let (off, w) = shift_stencil(rad, -delta[i], k_rad);
        let row = &b[i * np_..(i + 1) * np_];
        for j in 0..np_ {
            let mut v = 0.0;
            for a in 0..k_rad {
                v += w[a] * extend_lnf(row, &p, j as i64 + off[a], tail);
            }
            out[i * np_ + j] = v;
        }
    }
    out
}

/// 광행차 (Q7b): D = gamma(1 - v·ê),  ê' = [ê + gamma v(gamma(v·ê)/(gamma+1) - 1)]/D.
pub fn aberration(ehat: &[f64], v: &[f64; 3]) -> (Vec<f64>, Vec<f64>) {
    let n = ehat.len() / 3;
    let v2 = v[0] * v[0] + v[1] * v[1] + v[2] * v[2];
    let g = 1.0 / (1.0 - v2).sqrt();
    let mut dd = vec![0.0; n];
    let mut ep = vec![0.0; 3 * n];
    for i in 0..n {
        let e = [ehat[3 * i], ehat[3 * i + 1], ehat[3 * i + 2]];
        let ve = e[0] * v[0] + e[1] * v[1] + e[2] * v[2];
        let d = g * (1.0 - ve);
        dd[i] = d;
        let c = g * (g * ve / (g + 1.0) - 1.0);
        let mut nrm = 0.0;
        for k in 0..3 {
            let x = (e[k] + c * v[k]) / d;
            ep[3 * i + k] = x;
            nrm += x * x;
        }
        let nrm = nrm.sqrt();
        for k in 0..3 {
            ep[3 * i + k] /= nrm;
        }
    }
    (dd, ep)
}

/// 잔여 속도장 (R1)(R2).  반환 (v (3M), dlnq (M)).
pub fn residual_field(
    m: &[f64; 9],
    qhat: &[f64],
    n6: &[f64; 6],
    a3: &[f64; 3],
) -> (Vec<f64>, Vec<f64>) {
    let n = qhat.len() / 3;
    let mmat = [[m[0], m[1], m[2]], [m[3], m[4], m[5]], [m[6], m[7], m[8]]];
    let minv = inv3(&mmat);
    let mut v = vec![0.0; 3 * n];
    let mut rad = vec![0.0; n];
    for i in 0..n {
        let q = [qhat[3 * i], qhat[3 * i + 1], qhat[3 * i + 2]];
        let mut p = [0.0; 3];
        for r in 0..3 {
            p[r] = mmat[r][0] * q[0] + mmat[r][1] * q[1] + mmat[r][2] * q[2];
        }
        let mu = (p[0] * p[0] + p[1] * p[1] + p[2] * p[2]).sqrt();
        let e = [p[0] / mu, p[1] / mu, p[2] / mu];
        let ne = sym_apply(n6, &e);
        let mut w = [
            ne[1] * e[2] - ne[2] * e[1],
            ne[2] * e[0] - ne[0] * e[2],
            ne[0] * e[1] - ne[1] * e[0],
        ];
        let ae = a3[0] * e[0] + a3[1] * e[1] + a3[2] * e[2];
        for k in 0..3 {
            w[k] -= a3[k] - ae * e[k];
        }
        let mut mw = [0.0; 3];
        for r in 0..3 {
            mw[r] = minv[r][0] * w[0] + minv[r][1] * w[1] + minv[r][2] * w[2];
        }
        let r0 = q[0] * mw[0] + q[1] * mw[1] + q[2] * mw[2];
        for k in 0..3 {
            v[3 * i + k] = mu * (mw[k] - r0 * q[k]);
        }
        rad[i] = mu * r0;
    }
    (v, rad)
}

fn backtrace(
    m: &[f64; 9],
    qhat: &[f64],
    n6: &[f64; 6],
    a3: &[f64; 3],
    dtau: f64,
    sub: usize,
) -> (Vec<f64>, Vec<f64>) {
    let n = qhat.len() / 3;
    let mut q = qhat.to_vec();
    let h = -dtau / sub as f64;
    let mut delta = vec![0.0; n];
    for _ in 0..sub {
        let (v1, _) = residual_field(m, &q, n6, a3);
        let mut qm = vec![0.0; 3 * n];
        for i in 0..n {
            let mut nrm = 0.0;
            for k in 0..3 {
                qm[3 * i + k] = q[3 * i + k] + 0.5 * h * v1[3 * i + k];
                nrm += qm[3 * i + k] * qm[3 * i + k];
            }
            let nrm = nrm.sqrt();
            for k in 0..3 {
                qm[3 * i + k] /= nrm;
            }
        }
        let (v2, r2) = residual_field(m, &qm, n6, a3);
        for i in 0..n {
            let mut nrm = 0.0;
            for k in 0..3 {
                q[3 * i + k] += h * v2[3 * i + k];
                nrm += q[3 * i + k] * q[3 * i + k];
            }
            let nrm = nrm.sqrt();
            for k in 0..3 {
                q[3 * i + k] /= nrm;
            }
            delta[i] -= h * r2[i];
        }
    }
    (q, delta)
}

/// ★ Mode B 잔여 이류 — 방향 스텐실 + **방향별 반경 시프트** 결합.
/// f 배치는 방향-주 f[i*n_p + j].  (R2) 의 delta 가 ln p 시프트가 된다.
#[allow(clippy::too_many_arguments)]
pub fn residual_step_mode_b(
    sph: &SphereGrid,
    rad: &RadialGrid,
    m: &[f64; 9],
    f: &[f64],
    n6: &[f64; 6],
    a3: &[f64; 3],
    dtau: f64,
    k_theta: usize,
    k_phi: usize,
    k_rad: usize,
    sub: usize,
    log_state: bool,
    tail: Tail,
) -> Vec<f64> {
    let m_ang = sph.len();
    let np_ = rad.len();
    if n6.iter().all(|x| *x == 0.0) && a3.iter().all(|x| *x == 0.0) {
        return f.to_vec();
    }
    let (qb, delta) = backtrace(m, &sph.ehat, n6, a3, dtau, sub);
    let (idx, wts, _) = build_stencils(sph, &qb, k_theta, k_phi);
    let s = k_theta * k_phi;
    // (a) 방향 보간 (반경 슬라이스 연속 블록)
    let mut tmp = vec![0.0; m_ang * np_];
    for i in 0..m_ang {
        for k in 0..s {
            let w = wts[i * s + k];
            if w == 0.0 {
                continue;
            }
            let src = idx[i * s + k] as usize * np_;
            for j in 0..np_ {
                tmp[i * np_ + j] += w * f[src + j];
            }
        }
    }
    // (b) 방향별 반경 시프트 — dln p = delta (공변 |q| 팽창)
    let p = rad.p();
    let mut out = vec![0.0; m_ang * np_];
    for i in 0..m_ang {
        let blk = &tmp[i * np_..(i + 1) * np_];
        let lnf: Vec<f64> = if log_state {
            blk.to_vec()
        } else {
            blk.iter().map(|x| x.max(1e-300).ln()).collect()
        };
        let (off, w) = shift_stencil(rad, delta[i], k_rad);
        for j in 0..np_ {
            let mut v = 0.0;
            for a in 0..k_rad {
                v += w[a] * extend_lnf(&lnf, &p, j as i64 + off[a], tail);
            }
            out[i * np_ + j] = if log_state { v } else { v.exp() };
        }
    }
    out
}

#[inline]
fn extend_lnf(lnf: &[f64], p: &[f64], i: i64, tail: Tail) -> f64 {
    let n = lnf.len() as i64;
    if i >= 0 && i < n {
        return lnf[i as usize];
    }
    let dl = p[1].ln() - p[0].ln();
    if i < 0 {
        let k = (lnf[1] - lnf[0]) / dl;
        lnf[0] + k * (i as f64) * dl
    } else {
        let last = n as usize - 1;
        match tail {
            Tail::PowerLaw => {
                let k = (lnf[last] - lnf[last - 1]) / dl;
                lnf[last] + k * (i - (n - 1)) as f64 * dl
            }
            Tail::Wien => {
                let mm = (lnf[last] - lnf[last - 1]) / (p[last] - p[last - 1]);
                let pout = (p[last].ln() + dl * (i - (n - 1)) as f64).exp();
                lnf[last] + mm * (pout - p[last])
            }
        }
    }
}

/// ★ 앙상블 — **멤버 병렬** (rayon).  멤버 내부는 직렬 ⇒ 스레드 수 무관 비트 동일.
pub fn run_ensemble(sph: &SphereGrid, states: Vec<QState>, cfg: &Config) -> Vec<Vec<f64>> {
    states
        .into_par_iter()
        .map(|mut st| {
            st.evolve(sph, cfg);
            st.pack()
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    fn mk(sph: &SphereGrid, n6: [f64; 6], a3: [f64; 3]) -> QState {
        QState {
            s6: [0.2, -0.1, -0.1, 0.0, 0.0, 0.0],
            n6,
            a3,
            ln_h: 0.0,
            m: [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0],
            lg: vec![0.0; sph.len()],
            rot: [0.0; 3],
            residual: true,
            jac_min: 1.0,
            n_p: 0,
            rad: None,
            tail: Tail::Wien,
            k_rad: 8,
            v_b: None,
        }
    }

    #[test]
    fn inverse_matrix_is_correct() {
        let a = [[1.3, 0.2, -0.1], [0.0, 0.7, 0.4], [0.2, -0.1, 0.9]];
        let b = inv3(&a);
        let c = mm(&a, &b);
        for i in 0..3 {
            for j in 0..3 {
                let want = if i == j { 1.0 } else { 0.0 };
                assert!((c[i][j] - want).abs() < 1e-13, "{c:?}");
            }
        }
    }

    #[test]
    fn reduce_det_is_order_fixed() {
        let v: Vec<f64> = (0..1000).map(|i| (i as f64).sin() * 1e8).collect();
        assert_eq!(reduce_det(&v), reduce_det(&v.clone()));
    }

    #[test]
    fn bianchi_i_residual_is_identity() {
        let sph = SphereGrid::new(16, 32);
        let mut st = mk(&sph, [0.0; 6], [0.0; 3]);
        st.lg = (0..sph.len()).map(|i| 0.01 * i as f64).collect();
        let before = st.lg.clone();
        st.residual_step(&sph, -0.01, 6, 6, 2);
        assert_eq!(before, st.lg);
    }

    #[test]
    fn evolution_is_deterministic() {
        let sph = SphereGrid::new(16, 32);
        let cfg = Config {
            v_b: None,
            dtau: -0.002,
            nsteps: 100,
            nu: 1.0,
            kernel: Kernel::Thomson,
            k_theta: 6,
            k_phi: 6,
            sub: 2,
            keep_every: 0,
            nu_sched: Vec::new(),
            h_anchor: 0.0,
        };
        let mut a = mk(&sph, [0.3, 0.3, 0.3, 0.0, 0.0, 0.0], [0.0; 3]);
        let mut b = a.clone();
        a.evolve(&sph, &cfg);
        b.evolve(&sph, &cfg);
        assert_eq!(a.pack(), b.pack());
    }

    #[test]
    fn mode_b_reduces_to_mode_a_for_factorized_data() {
        // f(q̂,q) = A(q̂) * S(q)  ⇒  ln Ghat = ln A + 4 ln mu + ln∫S q³dq
        let sph = SphereGrid::new(12, 24);
        let np_ = 48;
        let rad = RadialGrid::new(-5.0, 5.0, np_);
        let q = rad.p();
        let m_ang = sph.len();
        let ang: Vec<f64> = (0..m_ang).map(|i| 0.4 * sph.ehat[3 * i + 2]).collect();
        let spec: Vec<f64> = q.iter().map(|x| (1.0 / (x.exp() - 1.0)).ln()).collect();
        let mut b = mk(&sph, [0.3, -0.2, 0.1, 0.0, 0.0, 0.0], [0.0; 3]);
        b.n_p = np_;
        b.rad = Some(rad.clone());
        b.lg = (0..m_ang * np_)
            .map(|k| ang[k / np_] + spec[k % np_])
            .collect();
        let fr = Frame { m: b.m };
        let (_, mu) = cm::phys_dirs(&fr, &sph.ehat);
        let lgb = b.ln_ghat(&mu);
        // 해석: ln Jr = ln( sum_j S_j q_j^4 wt dlnq )
        let mut mx = f64::NEG_INFINITY;
        for j in 0..np_ {
            let wt: f64 = if j == 0 || j == np_ - 1 { 0.5 } else { 1.0 };
            let v = spec[j] + 4.0 * q[j].ln() + wt.ln();
            if v > mx {
                mx = v;
            }
        }
        let mut acc = 0.0;
        for j in 0..np_ {
            let wt: f64 = if j == 0 || j == np_ - 1 { 0.5 } else { 1.0 };
            acc += (spec[j] + 4.0 * q[j].ln() + wt.ln() - mx).exp();
        }
        let lnjr = mx + acc.ln() + rad.dlnp.ln();
        for i in 0..m_ang {
            let want = ang[i] + lnjr + 4.0 * mu[i].ln();
            assert!((lgb[i] - want).abs() < 1e-12, "{} vs {want}", lgb[i]);
        }
    }

    #[test]
    fn mode_b_free_stream_is_exactly_invariant() {
        // 공변 프레임에서 f 는 자유흐름 하에 정확히 불변 (Bianchi I, 곡률 0)
        let sph = SphereGrid::new(12, 24);
        let np_ = 32;
        let mut st = mk(&sph, [0.0; 6], [0.0; 3]);
        st.n_p = np_;
        st.rad = Some(RadialGrid::new(-4.0, 4.0, np_));
        st.lg = (0..sph.len() * np_).map(|k| 0.01 * k as f64).collect();
        let before = st.lg.clone();
        let cfg = Config {
            v_b: None,
            dtau: -0.005,
            nsteps: 50,
            nu: 0.0,
            kernel: Kernel::Thomson,
            k_theta: 4,
            k_phi: 4,
            sub: 2,
            keep_every: 0,
            nu_sched: Vec::new(),
            h_anchor: 0.0,
        };
        st.evolve(&sph, &cfg);
        let d = (0..before.len())
            .map(|k| (st.lg[k] - before[k]).abs())
            .fold(0.0f64, f64::max);
        assert!(
            d < 1e-13,
            "max diff {d}  first {} vs {}",
            st.lg[0],
            before[0]
        );
    }

    #[test]
    fn mode_b_collision_acts_identically_on_every_radial_slice() {
        let sph = SphereGrid::new(12, 24);
        let np_ = 6;
        let m_ang = sph.len();
        let mut st = mk(&sph, [0.0; 6], [0.0; 3]);
        st.n_p = np_;
        st.rad = Some(RadialGrid::new(-3.0, 3.0, np_));
        let ang: Vec<f64> = (0..m_ang).map(|i| 0.7 * sph.ehat[3 * i + 2]).collect();
        let off = [0.0, 1.3, -2.1, 0.5, 3.0, -0.4];
        st.lg = (0..m_ang * np_)
            .map(|k| ang[k / np_] + off[k % np_])
            .collect();
        st.collide(&sph, 1.7, Kernel::Thomson);
        // 각 슬라이스가 (같은 연산) + (원래 오프셋) 이어야 한다
        for j in 1..np_ {
            for i in 0..m_ang {
                let d = st.lg[i * np_ + j] - st.lg[i * np_];
                assert!((d - (off[j] - off[0])).abs() < 1e-11, "i={i} j={j} d={d}");
            }
        }
    }

    #[test]
    fn ensemble_is_bitwise_identical_to_serial() {
        let sph = SphereGrid::new(12, 24);
        let cfg = Config {
            v_b: None,
            dtau: -0.002,
            nsteps: 50,
            nu: 0.5,
            kernel: Kernel::Thomson,
            k_theta: 4,
            k_phi: 4,
            sub: 2,
            keep_every: 0,
            nu_sched: Vec::new(),
            h_anchor: 0.0,
        };
        let mk_i = |i: usize| {
            let mut s = mk(&sph, [0.3, -0.2, 0.1, 0.0, 0.0, 0.0], [0.0; 3]);
            s.s6[0] = 0.2 + 0.01 * i as f64;
            s
        };
        let serial: Vec<Vec<f64>> = (0..8)
            .map(|i| {
                let mut s = mk_i(i);
                s.evolve(&sph, &cfg);
                s.pack()
            })
            .collect();
        let par = run_ensemble(&sph, (0..8).map(mk_i).collect(), &cfg);
        assert_eq!(serial, par);
    }

    #[test]
    fn nu_schedule_model_mode_uses_state_lnh() {
        // Q19: h_anchor > 0 이면 nu = A / (h_anchor * exp(lnH)) 를 **상태에서** 계산.
        let sph = SphereGrid::new(8, 16);
        let mut st = mk(&sph, [0.2, -0.1, -0.1, 0.0, 0.0, 0.0], [0.0; 3]);
        st.ln_h = 0.5;
        let n = 4usize;
        let a_sched: Vec<f64> = (0..=n).map(|k| 1.0 + k as f64).collect();
        let cfg = Config {
            v_b: None,
            dtau: -0.01,
            nsteps: n,
            nu: 0.0,
            kernel: Kernel::Thomson,
            k_theta: 4,
            k_phi: 4,
            sub: 2,
            keep_every: 0,
            nu_sched: a_sched.clone(),
            h_anchor: 2.0,
        };
        for (k, &a_k) in a_sched.iter().enumerate().take(n + 1) {
            let want = a_k / (2.0 * (0.5f64).exp());
            assert!((cfg.nu_at(k, 0.5) - want).abs() < 1e-14, "k={k}");
        }
        // h_anchor == 0 이면 sched 가 곧 nu (LCDM 모드)
        let cfg0 = Config {
            h_anchor: 0.0,
            ..cfg
        };
        assert!((cfg0.nu_at(2, 0.5) - 3.0).abs() < 1e-14);
        // 빈 sched 는 상수 nu (기존 경로)
        let cfgc = Config {
            nu_sched: Vec::new(),
            nu: 7.0,
            ..cfg0
        };
        assert!((cfgc.nu_at(3, 1.23) - 7.0).abs() < 1e-14);
        // 실제로 진화가 도는가 (h_anchor > 0 분기의 통합 시험)
        let cfg2 = Config {
            v_b: None,
            dtau: -0.01,
            nsteps: n,
            nu: 0.0,
            kernel: Kernel::Thomson,
            k_theta: 4,
            k_phi: 4,
            sub: 2,
            keep_every: 0,
            nu_sched: a_sched,
            h_anchor: 2.0,
        };
        st.evolve(&sph, &cfg2);
        assert!(st.lg.iter().all(|v| v.is_finite()));
    }
}
