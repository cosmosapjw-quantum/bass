//! C1 · 일반유형(N, A, R ≠ 0) 조석행렬 — 자동생성 Riemann 을 축약.
//!
//! 대각 Bianchi I 은 `optical::tidal` 의 손유도 닫힌형(R4)이 더 빠르므로 그대로 쓰고,
//! 일반유형은 여기(codegen 경로)를 쓴다.  두 경로는 대각 극한에서 서로 일치해야 하며
//! 이는 차등테스트로 고정한다.
//!
//! T_AB = -R_{a m b n} k^m k^n E_A^a E_B^b     (Python `weyl.tidal_matrix` 와 동일)

use nalgebra::{Matrix2, Vector4};

use crate::rays::riemann_gen;

/// Python `weyl.pack_state` 와 동일한 24-인자 상태.
/// 순서: H, n00,n01,n02,n11,n12,n22, a0,a1,a2, s00,s01,s02,s11,s12, R0,R1,R2, Hd,
///       sd00,sd01,sd02,sd11,sd12
pub type Args24 = [f64; 24];

/// 일반유형 조석행렬 T_AB (스크린 4-벡터 2개).
pub fn tidal_general(p: &Args24, k: &Vector4<f64>, sc: &[Vector4<f64>; 2]) -> Matrix2<f64> {
    let mut rl = [0.0f64; 256];
    riemann_gen::riemann_low(p, &mut rl);

    // T_AB = - R_{a m b n} E_A^a k^m E_B^b k^n
    let mut t = Matrix2::zeros();
    for ai in 0..2 {
        for bi in 0..2 {
            let mut acc = 0.0;
            for a in 0..4 {
                let ea = sc[ai][a];
                if ea == 0.0 {
                    continue;
                }
                for m in 0..4 {
                    let km = k[m];
                    if km == 0.0 {
                        continue;
                    }
                    let base = a * 64 + m * 16;
                    for (b, &eb) in sc[bi].iter().enumerate() {
                        if eb == 0.0 {
                            continue;
                        }
                        let row = base + b * 4;
                        let mut inner = 0.0;
                        for n in 0..4 {
                            inner += rl[row + n] * k[n];
                        }
                        acc += ea * km * eb * inner;
                    }
                }
            }
            t[(ai, bi)] = -acc;
        }
    }
    t
}

/// Ricci 집속 점검용:  tr T = -R_{mn} k^m k^n  이어야 (D16 오라클).
/// 여기서는 R_{mn} = R^a_{man} 축약을 생성 Riemann 에서 직접 만든다.
pub fn ricci_kk(p: &Args24, k: &Vector4<f64>) -> f64 {
    let mut ru = [0.0f64; 256];
    riemann_gen::riemann_up(p, &mut ru);
    // R_{mn} = R^a_{m a n}
    let mut acc = 0.0;
    for m in 0..4 {
        for n in 0..4 {
            let mut rmn = 0.0;
            for a in 0..4 {
                rmn += ru[a * 64 + m * 16 + a * 4 + n];
            }
            acc += rmn * k[m] * k[n];
        }
    }
    acc
}
