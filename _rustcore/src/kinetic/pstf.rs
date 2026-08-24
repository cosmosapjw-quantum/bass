//! PSTF (사영 대칭 무대각합) 사영 — 자동생성 데이터(`pstf_gen`)를 써서 적용.
//!
//! 대칭 rank-l 텐서는 PSTF ⊕ sym(δ⊗rank(l-2)) 로 **직교분해**되므로
//!     P T = T - A_l (S_l T),      S_l = (A_lᵀ A_l)⁻¹ A_lᵀ
//! 로 대각합 부분을 정확히 제거한다.
//! ★ Python 쪽 교훈: 반복 대각합 제거(계수 1/(2l-1))는 **l≥4 에서 수렴 실패**한다.
//!   직교사영만 쓴다.
//!
//! 텐서는 평탄 `Vec<f64>` (행우선, 길이 3^l) 로 다룬다.

use crate::kinetic::pstf_gen as G;

// ★ codegen 한계와 스택 버퍼 한계가 어긋나면 **컴파일 시** 실패시킨다
//   (세 곳에 흩어진 l 한계가 조용히 어긋나 panic 으로 드러났던 결함의 재발 방지).
const _: () = assert!(G::L_MAX <= MAX_RANK);

/// rank-l 텐서의 평탄 길이 3^l.
#[inline]
pub fn dim(l: usize) -> usize {
    3usize.pow(l as u32)
}

fn basis(l: usize) -> (&'static [f64], &'static [f64], usize) {
    match l {
        2 => (&G::A_2, &G::S_2, G::NB_2),
        3 => (&G::A_3, &G::S_3, G::NB_3),
        4 => (&G::A_4, &G::S_4, G::NB_4),
        5 => (&G::A_5, &G::S_5, G::NB_5),
        _ => panic!("PSTF: l={l} 미지원 (l≤{} — codegen 범위)", G::L_MAX),
    }
}

/// 최대 지표 수 — `symmetrize` 의 스택 버퍼 크기.  codegen L_MAX 보다 커야 한다.
/// ★ 이전 판은 `[0usize; 4]` 였고, l=5 에서 **경계 밖 쓰기로 panic** 했다
///   (pstf_gen 을 L_MAX=5 로 올려도 여기서 막혔다 — 한계가 세 곳에 흩어져 있었다).
pub const MAX_RANK: usize = 8;

/// 대칭화 — 모든 지표 순열 평균.  순열 수 l! 이므로 l ≤ 6 정도가 실용 한계.
pub fn symmetrize(t: &[f64], l: usize) -> Vec<f64> {
    let d = dim(l);
    debug_assert_eq!(t.len(), d);
    if l < 2 {
        return t.to_vec();
    }
    let perms = permutations(l);
    let mut out = vec![0.0; d];
    for p in &perms {
        for (flat, out_flat) in out.iter_mut().enumerate() {
            // flat 를 지표로 분해 → 순열 적용 → 원본 위치
            let mut idx = [0usize; MAX_RANK];
            let mut r = flat;
            for k in (0..l).rev() {
                idx[k] = r % 3;
                r /= 3;
            }
            let mut src = 0usize;
            for k in 0..l {
                src = src * 3 + idx[p[k]];
            }
            *out_flat += t[src];
        }
    }
    let n = perms.len() as f64;
    for v in out.iter_mut() {
        *v /= n;
    }
    out
}

fn permutations(l: usize) -> Vec<Vec<usize>> {
    let mut base: Vec<usize> = (0..l).collect();
    let mut out = Vec::new();
    permute(&mut base, 0, &mut out);
    out
}

fn permute(v: &mut Vec<usize>, k: usize, out: &mut Vec<Vec<usize>>) {
    if k == v.len() {
        out.push(v.clone());
        return;
    }
    for i in k..v.len() {
        v.swap(k, i);
        permute(v, k + 1, out);
        v.swap(k, i);
    }
}

/// PSTF 사영 (입력은 대칭화된다).  l<2 는 그대로 반환.
pub fn project(t: &[f64], l: usize) -> Vec<f64> {
    if l < 2 {
        return t.to_vec();
    }
    let sym = symmetrize(t, l);
    let (a, s, nb) = basis(l);
    let d = dim(l);
    // c = S sym   (nb)
    let mut c = vec![0.0; nb];
    for j in 0..nb {
        let mut acc = 0.0;
        for k in 0..d {
            acc += s[j * d + k] * sym[k];
        }
        c[j] = acc;
    }
    // out = sym - A c
    let mut out = sym;
    for k in 0..d {
        let mut acc = 0.0;
        for j in 0..nb {
            acc += a[k * nb + j] * c[j];
        }
        out[k] -= acc;
    }
    out
}

/// 진단: 마지막 두 지표 대각합의 최대 절대값 (0 이어야).
#[cfg(test)]
pub fn trace_residual(t: &[f64], l: usize) -> f64 {
    if l < 2 {
        return 0.0;
    }
    let d_low = dim(l - 2);
    let mut worst = 0.0f64;
    for base in 0..d_low {
        let mut acc = 0.0;
        for c in 0..3 {
            acc += t[(base * 3 + c) * 3 + c];
        }
        worst = worst.max(acc.abs());
    }
    worst
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn projection_removes_traces() {
        for l in 2..=4 {
            let d = dim(l);
            // 결정론적 '무작위' 텐서
            let t: Vec<f64> = (0..d).map(|k| ((k * 37 % 19) as f64) - 9.0).collect();
            let p = project(&t, l);
            let scale = p.iter().fold(0.0f64, |a, b| a.max(b.abs())).max(1e-300);
            assert!(trace_residual(&p, l) < 1e-10 * scale, "l={l}");
        }
    }

    #[test]
    fn projection_is_idempotent() {
        for l in 2..=4 {
            let d = dim(l);
            let t: Vec<f64> = (0..d).map(|k| ((k * 11 % 7) as f64) - 3.0).collect();
            let p1 = project(&t, l);
            let p2 = project(&p1, l);
            let scale = p1.iter().fold(0.0f64, |a, b| a.max(b.abs())).max(1e-300);
            let diff = p1
                .iter()
                .zip(p2.iter())
                .fold(0.0f64, |a, (x, y)| a.max((x - y).abs()));
            assert!(diff < 1e-10 * scale, "l={l}");
        }
    }
}
