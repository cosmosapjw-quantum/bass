//! R1(완결) + R4 · 널 다발 광학 (Sachs/Jacobi) 와 각지름거리 d_A.
//!
//! Python `rays.optical.trace_optical_diag_bianchi` 의 정확한 포트 (3-패스 구조 유지):
//!   Pass 1  광선·스크린·배경 RK4 궤적 기록
//!   Pass 2  스텝별 조석행렬 T_AB
//!   Pass 3  Jacobi J'' = T J (RK4, 부분스텝마다 올바른 T: k1→T_i, k2/k3→중점, k4→T_{i+1})
//!           d_A = |det J|^{1/2},  dA 는 **스텝 전에** 기록해 E_i 와 짝을 맞춘다.
//!
//! ★ R4 (조석 평가의 탈-sympy):  Python 은 144성분 sympy pickle 을 lambdify/vmap 한다.
//!   대각 Bianchi I (N=A=R=0, ³R=0) 에서는 Gauss-Codazzi 로 프레임 Riemann 이 닫힌형이며
//!   (오라클 대조 4.4e-16 로 확인):
//!       K = Hδ + σ,   K̇ = Ḣδ + σ̇,   M = -(K̇ + K²)
//!       R_{0a0b} = M_ab,   R_{abcd} = K_ac K_bd - K_ad K_bc,   R_{0abc} = 0
//!   조석 축약을 더 줄이면 (오라클 대조 1.4e-14):
//!       w_A = α_A κ - k⁰ u_A          (E_A = (α_A, u_A),  k = (k⁰, κ))
//!       T_AB = -[ w_A·M w_B + (u_A·K u_B)(κ·Kκ) - (u_A·Kκ)(Kκ·u_B) ]
//!   → sympy/JAX 없이 순수 산술.  일반 유형(N,A,R≠0)은 후속 codegen 경로로 확장.

use nalgebra::{Matrix2, Matrix3, Vector3, Vector4};
use rayon::prelude::*;

/// RK4 상태 (Python dict keys 미러: E, nh, sc, H, sig, rho, lna, t).
#[derive(Clone, Copy)]
pub struct OState {
    pub e: f64,
    pub nh: Vector3<f64>,
    pub sc: [Vector4<f64>; 2],
    pub h: f64,
    pub sig: Vector3<f64>,
    pub rho: f64,
    pub lna: Vector3<f64>,
    pub t: f64,
}

impl OState {
    /// base + c*d  (Python `axpy`).
    fn axpy(&self, d: &OState, c: f64) -> OState {
        OState {
            e: self.e + c * d.e,
            nh: self.nh + c * d.nh,
            sc: [self.sc[0] + c * d.sc[0], self.sc[1] + c * d.sc[1]],
            h: self.h + c * d.h,
            sig: self.sig + c * d.sig,
            rho: self.rho + c * d.rho,
            lna: self.lna + c * d.lna,
            t: self.t + c * d.t,
        }
    }
}

/// 관측점 스크린 기저 (Python `screen_basis` 와 동일 분기·정규화).
pub fn screen_basis(nhat: &Vector3<f64>) -> [Vector4<f64>; 2] {
    let tmp = if nhat.dot(&Vector3::new(1.0, 0.0, 0.0)).abs() > 0.9 {
        Vector3::new(0.0, 1.0, 0.0)
    } else {
        Vector3::new(1.0, 0.0, 0.0)
    };
    let e1 = nhat.cross(&tmp).normalize();
    let e2 = nhat.cross(&e1);
    [
        Vector4::new(0.0, e1[0], e1[1], e1[2]),
        Vector4::new(0.0, e2[0], e2[1], e2[2]),
    ]
}

/// 대각 Bianchi I 프레임 접속의 축약 (Python `_conn_diag` + einsum 과 동일 결과).
/// 유일한 비영 블록 Γ⁰_ij = Γ^i_0j = K_ij 에서:
///   acc⁰ = -E²(n̂·K n̂),   acc^i = -E²(K n̂)^i
///   dsc_A⁰ = -(u_A·K n̂),  dsc_A^i = -α_A (K n̂)^i        (÷E 포함)
#[inline]
fn deriv(s: &OState, gamma: f64) -> OState {
    let k_mat = Matrix3::from_diagonal(&Vector3::new(
        s.h + s.sig[0],
        s.h + s.sig[1],
        s.h + s.sig[2],
    ));
    let e = s.e;
    let nh = s.nh;
    let knh = k_mat * nh;
    let n_k_n = nh.dot(&knh);

    // 광선: p = (E, E n̂)
    let de_dl = -e * e * n_k_n;
    let dp_dl = -(e * e) * knh;
    let dn = (dp_dl - nh * de_dl) / (e * e);

    // 스크린 4-벡터 평행이동 (÷E 로 우주시간 매개화)
    let mut dsc = [Vector4::zeros(); 2];
    for (a, dsc_a) in dsc.iter_mut().enumerate() {
        let alpha = s.sc[a][0];
        let u = Vector3::new(s.sc[a][1], s.sc[a][2], s.sc[a][3]);
        let d0 = -u.dot(&knh) * e / e; // = -(u·K n̂)
        let dsp = -alpha * knh * e / e; // = -α (K n̂)
        *dsc_a = Vector4::new(d0, dsp[0], dsp[1], dsp[2]);
    }

    // 배경
    let hd = -s.h * s.h - s.sig.dot(&s.sig) / 3.0 - (s.rho + 3.0 * (gamma - 1.0) * s.rho) / 6.0;
    OState {
        e: de_dl / e,
        nh: dn,
        sc: dsc,
        h: hd,
        sig: -3.0 * s.h * s.sig,
        rho: -3.0 * s.h * gamma * s.rho,
        lna: Vector3::new(s.h + s.sig[0], s.h + s.sig[1], s.h + s.sig[2]),
        t: 1.0,
    }
}

/// 조석행렬 T_AB (R4 닫힌형).  `sig`, `sigd` 는 대각 성분.
#[inline]
fn tidal(
    h: f64,
    sig: &Vector3<f64>,
    hd: f64,
    sigd: &Vector3<f64>,
    k: &Vector4<f64>,
    sc: &[Vector4<f64>; 2],
) -> Matrix2<f64> {
    let k_mat = Matrix3::from_diagonal(&Vector3::new(h + sig[0], h + sig[1], h + sig[2]));
    let kd = Matrix3::from_diagonal(&Vector3::new(hd + sigd[0], hd + sigd[1], hd + sigd[2]));
    let m = -(kd + k_mat * k_mat);

    let k0 = k[0];
    let kap = Vector3::new(k[1], k[2], k[3]);
    let kkap = k_mat * kap;
    let k_kap_k = kap.dot(&kkap);

    let mut t = Matrix2::zeros();
    for a in 0..2 {
        let alpha_a = sc[a][0];
        let ua = Vector3::new(sc[a][1], sc[a][2], sc[a][3]);
        let wa = alpha_a * kap - k0 * ua;
        for b in 0..2 {
            let alpha_b = sc[b][0];
            let ub = Vector3::new(sc[b][1], sc[b][2], sc[b][3]);
            let wb = alpha_b * kap - k0 * ub;
            let val =
                wa.dot(&(m * wb)) + ua.dot(&(k_mat * ub)) * k_kap_k - ua.dot(&kkap) * kkap.dot(&ub);
            t[(a, b)] = -val;
        }
    }
    t
}

/// 광학 적분 결과.
#[derive(Clone, Default)]
pub struct OpticalResult {
    pub z: Vec<f64>,
    pub da: Vec<f64>,
    pub lna: Vec<[f64; 3]>,
    pub z_final: f64,
    pub da_final: f64,
    pub screen_ortho: f64,
}

/// 대각 Bianchi I 널 다발 광학 (Python `trace_optical_diag_bianchi` 정확 미러).
#[allow(clippy::too_many_arguments)]
pub fn trace_optical_diag(
    h0: f64,
    sigma0: &Vector3<f64>,
    omega0: f64,
    gamma: f64,
    nhat: &Vector3<f64>,
    t0: f64,
    t_end: f64,
    nsteps: usize,
) -> OpticalResult {
    let nh0 = nhat.normalize();
    let mut y = OState {
        e: 1.0,
        nh: nh0,
        sc: screen_basis(&nh0),
        h: h0,
        sig: sigma0 * h0,
        rho: 3.0 * h0 * h0 * omega0,
        lna: Vector3::zeros(),
        t: t0,
    };
    let dt = (t_end - t0) / nsteps as f64;

    // ---- Pass 1 + 2: 궤적 기록 + 조석행렬 (스텝마다 즉시 평가 — 별도 배치 불필요)
    let mut es: Vec<f64> = Vec::with_capacity(nsteps);
    let mut lnas: Vec<[f64; 3]> = Vec::with_capacity(nsteps);
    let mut t_all: Vec<Matrix2<f64>> = Vec::with_capacity(nsteps);
    let mut last_k = Vector4::zeros();
    let mut last_sc = [Vector4::zeros(); 2];

    for _ in 0..nsteps {
        let k1 = deriv(&y, gamma);
        let k2 = deriv(&y.axpy(&k1, 0.5 * dt), gamma);
        let k3 = deriv(&y.axpy(&k2, 0.5 * dt), gamma);
        let k4 = deriv(&y.axpy(&k3, dt), gamma);

        // 기록 (스텝 **전** 상태)
        let kvec = Vector4::new(y.e, y.e * y.nh[0], y.e * y.nh[1], y.e * y.nh[2]);
        let hd = -y.h * y.h - y.sig.dot(&y.sig) / 3.0 - (y.rho + 3.0 * (gamma - 1.0) * y.rho) / 6.0;
        let sigd = -3.0 * y.h * y.sig;
        t_all.push(tidal(y.h, &y.sig, hd, &sigd, &kvec, &y.sc));
        es.push(y.e);
        lnas.push([y.lna[0], y.lna[1], y.lna[2]]);
        last_k = kvec;
        last_sc = y.sc;

        // RK4 갱신
        let mut ynew = y;
        ynew.e = y.e + dt / 6.0 * (k1.e + 2.0 * k2.e + 2.0 * k3.e + k4.e);
        ynew.nh = y.nh + (k1.nh + 2.0 * k2.nh + 2.0 * k3.nh + k4.nh) * (dt / 6.0);
        for a in 0..2 {
            ynew.sc[a] =
                y.sc[a] + (k1.sc[a] + 2.0 * k2.sc[a] + 2.0 * k3.sc[a] + k4.sc[a]) * (dt / 6.0);
        }
        ynew.h = y.h + dt / 6.0 * (k1.h + 2.0 * k2.h + 2.0 * k3.h + k4.h);
        ynew.sig = y.sig + (k1.sig + 2.0 * k2.sig + 2.0 * k3.sig + k4.sig) * (dt / 6.0);
        ynew.rho = y.rho + dt / 6.0 * (k1.rho + 2.0 * k2.rho + 2.0 * k3.rho + k4.rho);
        ynew.lna = y.lna + (k1.lna + 2.0 * k2.lna + 2.0 * k3.lna + k4.lna) * (dt / 6.0);
        ynew.t = y.t + dt / 6.0 * (k1.t + 2.0 * k2.t + 2.0 * k3.t + k4.t);
        y = ynew;
        y.nh.normalize_mut();

        if y.h <= 0.0 || !y.h.is_finite() {
            break;
        }
    }

    // ---- Pass 3: Jacobi J'' = T J
    let n = es.len();
    let mut jm: Matrix2<f64> = Matrix2::zeros();
    let mut jp: Matrix2<f64> = Matrix2::identity();
    let mut da_hist: Vec<f64> = Vec::with_capacity(n);
    for i in 0..n {
        da_hist.push(jm.determinant().abs().sqrt()); // λ_i 의 J — Es[i] 와 짝
        if i + 1 >= n {
            break;
        }
        let e_mid = 0.5 * (es[i] + es[i + 1]);
        let (t0m, t1m) = (t_all[i], t_all[i + 1]);
        let tm = (t0m + t1m) * 0.5;
        let dlam = dt / e_mid;

        let a1j = jp;
        let a1p = t0m * jm;
        let a2j = jp + a1p * (0.5 * dlam);
        let a2p = tm * (jm + a1j * (0.5 * dlam));
        let a3j = jp + a2p * (0.5 * dlam);
        let a3p = tm * (jm + a2j * (0.5 * dlam));
        let a4j = jp + a3p * dlam;
        let a4p = t1m * (jm + a3j * dlam);
        jm += (a1j + a2j * 2.0 + a3j * 2.0 + a4j) * (dlam / 6.0);
        jp += (a1p + a2p * 2.0 + a3p * 2.0 + a4p) * (dlam / 6.0);
    }

    // ---- 출력 (stride 샘플링 + 종단값)
    let stride = (n / 400).max(1);
    let mut out = OpticalResult::default();
    let mut i = 0;
    while i < n {
        out.z.push(es[i] - 1.0);
        out.da.push(da_hist[i]);
        out.lna.push(lnas[i]);
        i += stride;
    }
    if n > 0 {
        out.z_final = es[n - 1] - 1.0;
        out.da_final = da_hist[n - 1];
        // 스크린 직교성 |k·η·E_A|  (η = diag(-1,1,1,1))
        let dot_eta = |a: &Vector4<f64>, b: &Vector4<f64>| -> f64 {
            -a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3]
        };
        out.screen_ortho = dot_eta(&last_k, &last_sc[0])
            .abs()
            .max(dot_eta(&last_k, &last_sc[1]).abs());
    }
    out
}

/// 배치: 방향별 (z_final, dA_final).  Rayon 데이터병렬.
#[allow(clippy::too_many_arguments)]
pub fn trace_optical_batch(
    h0: f64,
    sigma0: &Vector3<f64>,
    omega0: f64,
    gamma: f64,
    nhats: &[Vector3<f64>],
    t0: f64,
    t_end: f64,
    nsteps: usize,
) -> Vec<(f64, f64)> {
    nhats
        .par_iter()
        .map(|nh| {
            let r = trace_optical_diag(h0, sigma0, omega0, gamma, nh, t0, t_end, nsteps);
            (r.z_final, r.da_final)
        })
        .collect()
}
