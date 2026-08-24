//! G1b · 격자 충돌 커널 (73차) — G2 사다리의 Rust 판, **eigh 없이**.
//!
//! 병목 진단 (72차 실측): Strang 루프는 스텝마다 a(t) 가 바뀌어 물리 프레임
//! 핵 K(a) 를 새로 만든다 — Python 은 고유분해 O(N³)=1.9e8 를 스텝마다 치렀다.
//! 여기서는 **행렬-벡터만** 쓴다:
//!     exp(νdt(K−I))·g = e^{−νdt} Σ_m (νdt)^m/m! K^m g    (‖K‖_∞ = 1 수렴보장)
//! O(m·N²) — 절단 m 은 꼬리항 상대크기로 자동 (νdt ≤ 1 에서 m ≈ 12).
//! Sinkhorn 대칭 스케일링 (보존형: 행합 1 ∧ w-열합 1) 도 rayon 으로.
//!
//! R5b: Strang 루프째 (FFI 왕복 0).  자유흐름 팔은 해석 (μ 비의 거듭제곱).

use rayon::prelude::*;

/// Thomson 물리핵 + Sinkhorn 대칭 스케일링.  ehat: (n,3) row-major, w: (n,).
pub fn build_thomson(ehat: &[f64], w: &[f64], iters: usize, tol: f64) -> Vec<f64> {
    let n = w.len();
    let c = 3.0 / (16.0 * std::f64::consts::PI);
    let mut k = vec![0.0f64; n * n];
    k.par_chunks_mut(n).enumerate().for_each(|(i, row)| {
        let (ex, ey, ez) = (ehat[3 * i], ehat[3 * i + 1], ehat[3 * i + 2]);
        for (j, kv) in row.iter_mut().enumerate() {
            let mu = ex * ehat[3 * j] + ey * ehat[3 * j + 1] + ez * ehat[3 * j + 2];
            *kv = c * (1.0 + mu * mu);
        }
    });
    let mut d = vec![1.0f64; n];
    for _ in 0..iters {
        let r: Vec<f64> = k.par_chunks(n).enumerate().map(|(i, row)| {
            let s: f64 = row.iter().zip(w.iter()).zip(d.iter())
                .map(|((kv, wv), dv)| kv * wv * dv).sum();
            s * d[i]
        }).collect();
        let dev = r.iter().map(|x| (x - 1.0).abs()).fold(0.0, f64::max);
        d.par_iter_mut().zip(r.par_iter()).for_each(|(dv, rv)| *dv /= rv.sqrt());
        if dev < tol { break; }
    }
    let mut kk = vec![0.0f64; n * n];
    kk.par_chunks_mut(n).enumerate().for_each(|(i, row)| {
        for (j, v) in row.iter_mut().enumerate() {
            *v = d[i] * k[i * n + j] * d[j] * w[j];
        }
    });
    kk
}

fn matvec(k: &[f64], g: &[f64]) -> Vec<f64> {
    let n = g.len();
    k.par_chunks(n)
        .map(|row| row.iter().zip(g.iter()).map(|(a, b)| a * b).sum())
        .collect()
}

/// exp(νdt(K−I))·g — 테일러 (eigh 없음).  절단은 꼬리 상대크기 tol.
pub fn expm_apply(k: &[f64], g: &[f64], nu_dt: f64, tol: f64, m_max: usize)
    -> Vec<f64> {
    let n = g.len();
    let mut term = g.to_vec();
    let mut acc = g.to_vec();
    let scale0 = acc.iter().fold(0.0f64, |a, b| a.max(b.abs())).max(1e-300);
    for m in 1..=m_max {
        term = matvec(k, &term);
        let c = nu_dt / m as f64;
        term.par_iter_mut().for_each(|t| *t *= c);
        acc.par_iter_mut().zip(term.par_iter()).for_each(|(a, t)| *a += t);
        let tn = term.iter().fold(0.0f64, |a, b| a.max(b.abs()));
        if tn <= tol * scale0 { break; }
    }
    let e = (-nu_dt).exp();
    let mut out = acc;
    out.par_iter_mut().for_each(|v| *v *= e);
    let _ = n;
    out
}

/// Strang 루프째: ½충돌(a_k) → 자유흐름(μ_k→μ_{k+1}) → ½충돌(a_{k+1}).
/// ehat_seq/w_seq/mu_seq: 스텝 경계 (nsteps+1) × n 로 미리 준비 (Python 이
/// 물리 프레임을 만들어 넘긴다 — 좌표-동일 캐리, 규약원 단일).
#[allow(clippy::too_many_arguments)]
pub fn strang_evolve(g0: &[f64], ehat_seq: &[f64], w_seq: &[f64],
                     mu_seq: &[f64], nsteps: usize, nu: f64, h: f64,
                     n_pow: i32, tol: f64) -> Vec<f64> {
    let n = g0.len();
    let mut g = g0.to_vec();
    let half = 0.5 * nu * h;
    let mut k_cur = build_thomson(&ehat_seq[0..3 * n], &w_seq[0..n], 400, 1e-15);
    for s in 0..nsteps {
        g = expm_apply(&k_cur, &g, half, tol, 64);
        let (m0, m1) = (&mu_seq[s * n..(s + 1) * n], &mu_seq[(s + 1) * n..(s + 2) * n]);
        g.par_iter_mut().enumerate().for_each(|(i, v)| {
            *v *= (m1[i] / m0[i]).powi(n_pow + 4);
        });
        k_cur = build_thomson(&ehat_seq[3 * n * (s + 1)..3 * n * (s + 2)],
                              &w_seq[n * (s + 1)..n * (s + 2)], 400, 1e-15);
        g = expm_apply(&k_cur, &g, half, tol, 64);
    }
    g
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sinkhorn_doubly_stochastic() {
        // 등방 정사면체형 6점 (±축) + 균등 무게
        let e = [1.0, 0., 0., -1., 0., 0., 0., 1., 0., 0., -1., 0.,
                 0., 0., 1., 0., 0., -1.];
        let w = [4.0 * std::f64::consts::PI / 6.0; 6];
        let k = build_thomson(&e, &w, 400, 1e-15);
        for i in 0..6 {
            let rs: f64 = k[i * 6..(i + 1) * 6].iter().sum();
            assert!((rs - 1.0).abs() < 1e-13, "row {i} {rs}");
        }
        for j in 0..6 {
            let cs: f64 = (0..6).map(|i| w[i] * k[i * 6 + j]).sum::<f64>() / w[j];
            assert!((cs - 1.0).abs() < 1e-13, "col {j} {cs}");
        }
    }

    #[test]
    fn expm_preserves_constant() {
        let e = [1.0, 0., 0., -1., 0., 0., 0., 1., 0., 0., -1., 0.,
                 0., 0., 1., 0., 0., -1.];
        let w = [4.0 * std::f64::consts::PI / 6.0; 6];
        let k = build_thomson(&e, &w, 400, 1e-15);
        let g = vec![2.5; 6];
        let out = expm_apply(&k, &g, 0.7, 1e-16, 64);
        for v in out { assert!((v - 2.5).abs() < 1e-13); }
    }
}
