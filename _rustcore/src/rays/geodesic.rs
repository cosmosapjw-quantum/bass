//! R1 · 널 측지선 전송 (대각 Bianchi 배경) — Python `rays.geodesics` 의 **정확한** 포트.
//!
//! ★ Python `trace_ray_diag_bianchi` 은 docstring 과 달리 **전방 Euler** 이다
//!   (deriv 1회 호출 + `st += dt*d`).  차등테스트 비트-근접을 위해 Euler 를 그대로 옮긴다.
//! ★ 대각 배경: N=A=R=0 → P_double=0, (R×n)=0.  일반 커널 photon_rhs 는 N/A/R 를 받아
//!   비대각 확장에 재사용된다 (설계: 질량입자 특성곡선과 공유).

use nalgebra::{Matrix3, Vector3};
use rayon::prelude::*;

use crate::core::conventions::p_double;

/// 광자 전송 RHS.  반환 (dE/dt, dn̂/dt).  n̂ 단위벡터.
/// dE = -E(H + σ_ab n̂n̂),  dn̂ = -(σn̂ - (n̂σn̂)n̂) + (R×n̂) - (P - (n̂·P)n̂),  P=P_double(N,A,n̂).
pub fn photon_rhs(
    e: f64,
    nhat: &Vector3<f64>,
    h: f64,
    sigma: &Matrix3<f64>,
    n: &Matrix3<f64>,
    a: &Vector3<f64>,
    r: &Vector3<f64>,
) -> (f64, Vector3<f64>) {
    let sn = sigma * nhat;
    let n_sn = nhat.dot(&sn);
    let p = p_double(n, a, nhat);
    let de = -e * (h + n_sn);
    let rxn = r.cross(nhat);
    let dn = -(sn - n_sn * nhat) + rxn - (p - nhat.dot(&p) * nhat);
    (de, dn)
}

/// 기록된 광선 히스토리 (Python hist 리스트에 대응).
#[derive(Clone, Default)]
pub struct RayHistory {
    pub t: Vec<f64>,
    pub z: Vec<f64>,
    pub h: Vec<f64>,
    pub nh: Vec<[f64; 3]>,
    pub lna: Vec<[f64; 3]>,
}

#[derive(Clone, Copy, Debug)]
pub struct RayTraceConfig {
    pub h0: f64,
    pub omega0: f64,
    pub gamma: f64,
    pub t0: f64,
    pub t_end: f64,
    pub nsteps: usize,
}

/// 대각 Bianchi 배경 광선추적 (Euler; Python `trace_ray_diag_bianchi` 정확 미러).
///
/// 초기: H=h0, σ(차원량)=Σ0·h0, ρ=3h0²Ω0, lna=0, E=1, n̂=nhat/|nhat|, t=t0.
/// dt=(t_end-t0)/nsteps.  갱신 순서·기록 간격(max(1,nsteps/400))·break(H≤0 또는 비유한)를
/// Python 과 성분별로 일치시킨다.  z = E - 1 (과거로 E 증가).
pub fn trace_ray_diag(
    sigma0: &Vector3<f64>,
    nhat: &Vector3<f64>,
    config: &RayTraceConfig,
) -> RayHistory {
    let RayTraceConfig {
        h0,
        omega0,
        gamma,
        t0,
        t_end,
        nsteps,
    } = *config;
    let mut h = h0;
    let mut sig = sigma0 * h0; // 차원량 shear (대각)
    let mut rho = 3.0 * h0 * h0 * omega0;
    let mut lna = Vector3::zeros();
    let mut e = 1.0_f64;
    let mut nh = nhat.normalize();
    let mut t = t0;

    let dt = (t_end - t0) / nsteps as f64;
    let stride = (nsteps / 400).max(1);
    let zero_m = Matrix3::zeros();
    let zero_v = Vector3::zeros();
    let mut hist = RayHistory::default();

    for i in 0..nsteps {
        // deriv(현재 상태): 대각 → S=diag(sig), N=A=R=0
        let s_mat = Matrix3::from_diagonal(&sig);
        let (de, dn) = photon_rhs(e, &nh, h, &s_mat, &zero_m, &zero_v, &zero_v);
        let hd = -h * h - sig.dot(&sig) / 3.0 - (rho + 3.0 * (gamma - 1.0) * rho) / 6.0;
        let dsig = -3.0 * h * sig;
        let drho = -3.0 * h * gamma * rho;
        let dlna = Vector3::new(h + sig[0], h + sig[1], h + sig[2]);

        // Euler 갱신 — Python 순서: E,H,rho,t → nh(정규화) → sig → lna
        e += dt * de;
        h += dt * hd;
        rho += dt * drho;
        t += dt; // d(t)/dt = 1
        nh += dt * dn;
        nh.normalize_mut();
        sig += dt * dsig;
        lna += dt * dlna;

        if h <= 0.0 || !h.is_finite() {
            break;
        }
        if i % stride == 0 {
            hist.t.push(t);
            hist.z.push(e - 1.0);
            hist.h.push(h);
            hist.nh.push([nh[0], nh[1], nh[2]]);
            hist.lna.push([lna[0], lna[1], lna[2]]);
        }
    }
    hist
}

/// 배치: 방향마다 광선추적 후 **마지막 기록 z** (CMB 패턴이 쓰는 z(n̂)) 반환.
/// Rayon 데이터병렬 over 방향 — 방향별 이질적 조기종료(H≤0)를 native 처리 (계획 §1 근거).
pub fn trace_rays_batch_final_z(
    sigma0: &Vector3<f64>,
    nhats: &[Vector3<f64>],
    config: &RayTraceConfig,
) -> Vec<f64> {
    nhats
        .par_iter()
        .map(|nh| {
            let hist = trace_ray_diag(sigma0, nh, config);
            *hist.z.last().unwrap_or(&f64::NAN)
        })
        .collect()
}
