//! 무충돌 구적 — Python `matter.freestream` + `matter.hierarchy.J_moment` 의 포트.
//!
//! 균질 Bianchi I 은 불변기저 운동량 p_i = const 이므로 모멘트가 **고정영역 구적**으로
//! 정확히 나온다 (k-모드 없음):
//!     P^i = p_i/a_i,   λ=|P|,   E=√(m²+λ²),   V = a₁a₂a₃
//!     J^(i)_{A_l} = ∫dλ dΩ λ² E (λ/E)^n e_{⟨A_l⟩} f / V,   n = l+2i
//!
//! ★ 정규화: 논문 식(10)의 4π(−2)^l(l!)²/(2l+1)! 는 PSTF 역변환 인자와 **상쇄**되므로
//!   계수 1 의 직접 모멘트다 (Python 쪽에서 ρ 비 = 1.000000000000 으로 확인).
//!
//! 격자: 반경은 Gauss-Legendre + (0,∞) 사상 q = L(1+x)/(1−x), 각도는 GL(cosθ)×균일(φ)
//! — Python `freestream._build_grid` 와 **같은 노드**를 쓴다 (차등테스트 비트-근접 조건).

use std::sync::OnceLock;

use crate::kinetic::pstf;
use crate::thermo::fd::gauss_legendre_nodes;

const NR: usize = 96;
const NANG: usize = 24;
const L_MAP: f64 = 3.0;

pub struct Grid {
    pub q: Vec<f64>,         // 반경 노드 (NR)
    pub dq: Vec<f64>,        // 반경 가중 (NR)
    pub nhat: Vec<[f64; 3]>, // 방향 (NANG*NANG)
    pub wang: Vec<f64>,      // 각 가중 (NANG*NANG)
}

fn grid() -> &'static Grid {
    static G: OnceLock<Grid> = OnceLock::new();
    G.get_or_init(|| {
        let (xr, wr) = gauss_legendre_nodes(NR);
        let (xc, wc) = gauss_legendre_nodes(NANG);
        let mut q = Vec::with_capacity(NR);
        let mut dq = Vec::with_capacity(NR);
        for k in 0..NR {
            let x = xr[k];
            q.push(L_MAP * (1.0 + x) / (1.0 - x));
            dq.push(wr[k] * 2.0 * L_MAP / ((1.0 - x) * (1.0 - x)));
        }
        let mut nhat = Vec::with_capacity(NANG * NANG);
        let mut wang = Vec::with_capacity(NANG * NANG);
        for c in 0..NANG {
            let ct = xc[c];
            let st = (1.0 - ct * ct).sqrt();
            for j in 0..NANG {
                // Python: phi = 2π (j+0.5)/NANG,  wphi = 2π/NANG
                let phi = 2.0 * std::f64::consts::PI * (j as f64 + 0.5) / NANG as f64;
                nhat.push([st * phi.cos(), st * phi.sin(), ct]);
                wang.push(wc[c] * 2.0 * std::f64::consts::PI / NANG as f64);
            }
        }
        Grid { q, dq, nhat, wang }
    })
}

/// 상대론적 페르미-디랙 (T=1) — Python `freestream.f_fermi_dirac`.
#[inline]
pub fn f_fermi_dirac(q: f64) -> f64 {
    1.0 / (q.min(700.0).exp() + 1.0)
}

/// flat 지표 → 성분 지표 테이블 (l 마다 1회 계산 후 캐시).
/// ★ 최적화: 이전 판은 (반경×각도×flat) 삼중 내부루프에서 매번 나눗셈으로 분해해
///   구적이 numpy 대비 2배밖에 못 냈다.  테이블화 + Rayon 으로 개선.
fn index_table(l: usize) -> &'static Vec<Vec<usize>> {
    static T: OnceLock<Vec<Vec<Vec<usize>>>> = OnceLock::new();
    let all = T.get_or_init(|| {
        (0..=pstf_gen_lmax())
            .map(|ll| {
                let d = pstf::dim(ll);
                (0..d)
                    .map(|flat| {
                        let mut idx = vec![0usize; ll];
                        let mut r = flat;
                        for k in (0..ll).rev() {
                            idx[k] = r % 3;
                            r /= 3;
                        }
                        idx
                    })
                    .collect()
            })
            .collect()
    });
    &all[l]
}

fn pstf_gen_lmax() -> usize {
    crate::kinetic::pstf_gen::L_MAX
}

/// J^(i)_{A_l} 를 구적으로 계산.  `dipole_eps=0` 이면 등방.
/// 반환: 평탄 rank-l 텐서 (길이 3^l), PSTF 사영 적용.
pub fn j_moment(
    a_vec: &[f64; 3],
    mass: f64,
    l: usize,
    i: i32,
    dipole_eps: f64,
    dipole_axis: usize,
) -> Vec<f64> {
    use rayon::prelude::*;
    let g = grid();
    let v_vol = a_vec[0] * a_vec[1] * a_vec[2];
    let n = l as i32 + 2 * i;
    let d = pstf::dim(l);
    let tbl = index_table(l);

    // 반경 노드에 대해 병렬 축약 (각 노드가 독립적으로 부분합을 만든다)
    let out =
        g.q.par_iter()
            .zip(g.dq.par_iter())
            .map(|(&qr, &dqr)| {
                let wr = dqr * qr * qr / v_vol;
                let f_iso = f_fermi_dirac(qr);
                let mut acc = vec![0.0; d];
                for (m, nh) in g.nhat.iter().enumerate() {
                    let px = qr * nh[0] / a_vec[0];
                    let py = qr * nh[1] / a_vec[1];
                    let pz = qr * nh[2] / a_vec[2];
                    let p2 = px * px + py * py + pz * pz;
                    let lam = p2.sqrt();
                    let e = (mass * mass + p2).sqrt();
                    let fval = if dipole_eps == 0.0 {
                        f_iso
                    } else {
                        f_iso * (1.0 + dipole_eps * nh[dipole_axis])
                    };
                    let w = wr * g.wang[m] * fval;
                    let ratio = if e > 0.0 { lam / e } else { 0.0 };
                    let weight = w * e * ratio.powi(n);
                    if l == 0 {
                        acc[0] += weight;
                        continue;
                    }
                    let inv = 1.0 / lam.max(1e-300);
                    let eh = [px * inv, py * inv, pz * inv];
                    for (flat, idx) in tbl.iter().enumerate() {
                        let mut prod = weight;
                        for &k in idx {
                            prod *= eh[k];
                        }
                        acc[flat] += prod;
                    }
                }
                acc
            })
            .collect::<Vec<Vec<f64>>>();
    // ★ 비트 재현성: Rayon `reduce` 는 작업훔치기(work stealing)에 따라 축약 **트리
    //   모양이 실행마다 달라져** 부동소수 합산 순서가 바뀐다.  실제로 동시 부하 아래
    //   200회 호출에서 서로 다른 비트패턴 2개가 관측됐다(측정).  물리 코드에서
    //   "같은 입력 → 같은 출력" 은 지켜야 하므로, 부분합을 **노드 순서대로 수집한 뒤
    //   순차 합산**한다.  비용은 96×3^l 배열 하나 (무시할 수준).
    let mut acc = vec![0.0; d];
    for part in &out {
        for k in 0..d {
            acc[k] += part[k];
        }
    }
    let out = acc;
    if l >= 2 {
        pstf::project(&out, l)
    } else {
        out
    }
}

/// freestream 대응 (ρ, p, π_ab) — Python `freestream.moments` 와 같은 값.
pub fn moments(a_vec: &[f64; 3], mass: f64) -> (f64, f64, Vec<f64>) {
    let rho = j_moment(a_vec, mass, 0, 0, 0.0, 2)[0];
    let j1 = j_moment(a_vec, mass, 0, 1, 0.0, 2)[0];
    let pi = j_moment(a_vec, mass, 2, 0, 0.0, 2);
    (rho, j1 / 3.0, pi)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn massless_w_is_one_third() {
        let (rho, p, _) = moments(&[1.0, 1.0, 1.0], 0.0);
        assert!((3.0 * p / rho - 1.0).abs() < 1e-10);
    }

    #[test]
    fn isotropic_background_has_no_anisotropic_stress() {
        let (rho, _, pi) = moments(&[1.1, 1.1, 1.1], 0.4);
        let worst = pi.iter().fold(0.0f64, |a, b| a.max(b.abs()));
        assert!(worst < 1e-10 * rho, "pi={worst:e}");
    }

    #[test]
    fn odd_l_vanishes_for_isotropic_f0() {
        // f(p)=f(-p) ⇒ 홀수 l 항등적 0
        let rho = j_moment(&[1.0, 0.9, 1.15], 0.8, 0, 0, 0.0, 2)[0];
        for l in [1usize, 3] {
            let j = j_moment(&[1.0, 0.9, 1.15], 0.8, l, 0, 0.0, 2);
            let w = j.iter().fold(0.0f64, |a, b| a.max(b.abs()));
            assert!(w < 1e-12 * rho, "l={l} w={w:e}");
        }
    }

    #[test]
    fn dipole_activates_odd_l() {
        let rho = j_moment(&[1.0, 0.9, 1.15], 0.8, 0, 0, 0.4, 2)[0];
        let j1 = j_moment(&[1.0, 0.9, 1.15], 0.8, 1, 0, 0.4, 2);
        let w = j1.iter().fold(0.0f64, |a, b| a.max(b.abs()));
        assert!(w > 1e-3 * rho, "w={w:e}");
    }
}

// ════════════════════════════════════════ H5-e · tilted (boosted) 구적
//
// Bianchi I 정확해 f = f₀(q_i) 는 **법선** 프레임 것이고, tilted 관측자는 같은 f 를
// 다르게 분해할 뿐이다.  d³P/E 가 로런츠 불변이므로 d³P′ = (E′/E)d³P 이고,
// **같은 격자 위에서 피적분함수만 바꾸면** tilted 모멘트가 정확히 나온다:
//
//     J′^(i)_{A_l} = ∫ (d³q/V)·(E′/E)·E′(λ′/E′)^n·e′_{⟨A_l⟩}·f₀(q)
//     E′ = γ(E − v·P),   P′^A = P^A + v_A[k(v·P) − γE],   k = γ²/(γ+1)
//
// Python 오라클: `bianchi.matter.tilted_moments.J_moment_tilted`.

/// (γ, k) — k = γ²/(γ+1) = (γ−1)/v² (v→0 특이점을 제거한 형태).
#[inline]
pub fn boost_factors(v: &[f64; 3]) -> Option<(f64, f64)> {
    let v2 = v[0] * v[0] + v[1] * v[1] + v[2] * v[2];
    if v2 >= 1.0 {
        return None;
    }
    let gam = 1.0 / (1.0 - v2).sqrt();
    Some((gam, gam * gam / (gam + 1.0)))
}

/// J′^(i)_{A_l} — tilted 사틀 성분, 정확 구적.  v = 0 이면 `j_moment` 와 **비트-정확**.
pub fn j_moment_tilted(
    a_vec: &[f64; 3],
    v: &[f64; 3],
    mass: f64,
    l: usize,
    i: i32,
    dipole_eps: f64,
    dipole_axis: usize,
) -> Vec<f64> {
    use rayon::prelude::*;
    let g = grid();
    let (gam, kk) = boost_factors(v).expect("|v| >= 1 은 물리적이지 않다");
    let v_vol = a_vec[0] * a_vec[1] * a_vec[2];
    let n = l as i32 + 2 * i;
    let d = pstf::dim(l);
    let tbl = index_table(l);

    let parts =
        g.q.par_iter()
            .zip(g.dq.par_iter())
            .map(|(&qr, &dqr)| {
                let wr = dqr * qr * qr / v_vol;
                let f_iso = f_fermi_dirac(qr);
                let mut acc = vec![0.0; d];
                for (m, nh) in g.nhat.iter().enumerate() {
                    let p = [
                        qr * nh[0] / a_vec[0],
                        qr * nh[1] / a_vec[1],
                        qr * nh[2] / a_vec[2],
                    ];
                    let p2 = p[0] * p[0] + p[1] * p[1] + p[2] * p[2];
                    let e = (mass * mass + p2).sqrt();
                    let vdp = v[0] * p[0] + v[1] * p[1] + v[2] * p[2];
                    let ep = gam * (e - vdp);
                    let shift = kk * vdp - gam * e;
                    let pp = [
                        p[0] + v[0] * shift,
                        p[1] + v[1] * shift,
                        p[2] + v[2] * shift,
                    ];
                    let lamp = (pp[0] * pp[0] + pp[1] * pp[1] + pp[2] * pp[2]).sqrt();
                    let fval = if dipole_eps == 0.0 {
                        f_iso
                    } else {
                        f_iso * (1.0 + dipole_eps * nh[dipole_axis])
                    };
                    // ★ 야코비안이 (E′/E) 하나로 압축된다 (d³P′ = (E′/E)d³P)
                    let w = wr * g.wang[m] * fval * (ep / e);
                    let ratio = if ep > 0.0 { lamp / ep } else { 0.0 };
                    let weight = w * ep * ratio.powi(n);
                    if l == 0 {
                        acc[0] += weight;
                        continue;
                    }
                    let inv = 1.0 / lamp.max(1e-300);
                    let eh = [pp[0] * inv, pp[1] * inv, pp[2] * inv];
                    for (flat, idx) in tbl.iter().enumerate() {
                        let mut prod = weight;
                        for &k in idx {
                            prod *= eh[k];
                        }
                        acc[flat] += prod;
                    }
                }
                acc
            })
            .collect::<Vec<Vec<f64>>>();
    // 비트 재현성: 순서대로 순차 합산 (위 j_moment 와 같은 이유)
    let mut acc = vec![0.0; d];
    for part in &parts {
        for k in 0..d {
            acc[k] += part[k];
        }
    }
    if l >= 2 {
        pstf::project(&acc, l)
    } else {
        acc
    }
}

/// tilted 관측자가 보는 (ρ′, p′, q′_A, π′_AB 평탄9).
pub fn moments_tilted(a_vec: &[f64; 3], v: &[f64; 3], mass: f64) -> (f64, f64, [f64; 3], Vec<f64>) {
    let rho = j_moment_tilted(a_vec, v, mass, 0, 0, 0.0, 2)[0];
    let p = j_moment_tilted(a_vec, v, mass, 0, 1, 0.0, 2)[0] / 3.0;
    let q = j_moment_tilted(a_vec, v, mass, 1, 0, 0.0, 2);
    let pi = j_moment_tilted(a_vec, v, mass, 2, 0, 0.0, 2);
    (rho, p, [q[0], q[1], q[2]], pi)
}

/// ★ boost 대수 자기검증: λ′² = E′² − m² 의 격자 전점 최대 상대잔차.
/// 유도를 믿지 않고 측정한다 — 부호 오타를 한 줄로 잡는 항등식.
pub fn boost_shell_residual(a_vec: &[f64; 3], v: &[f64; 3], mass: f64) -> f64 {
    let g = grid();
    let (gam, kk) = boost_factors(v).expect("|v| >= 1");
    let mut worst = 0.0f64;
    for (r, &qr) in g.q.iter().enumerate() {
        let _ = r;
        for nh in g.nhat.iter() {
            let p = [
                qr * nh[0] / a_vec[0],
                qr * nh[1] / a_vec[1],
                qr * nh[2] / a_vec[2],
            ];
            let p2 = p[0] * p[0] + p[1] * p[1] + p[2] * p[2];
            let e = (mass * mass + p2).sqrt();
            let vdp = v[0] * p[0] + v[1] * p[1] + v[2] * p[2];
            let ep = gam * (e - vdp);
            let shift = kk * vdp - gam * e;
            let pp = [
                p[0] + v[0] * shift,
                p[1] + v[1] * shift,
                p[2] + v[2] * shift,
            ];
            let lam2 = pp[0] * pp[0] + pp[1] * pp[1] + pp[2] * pp[2];
            worst = worst.max((lam2 - (ep * ep - mass * mass)).abs() / (ep * ep).max(1e-300));
        }
    }
    worst
}

#[cfg(test)]
mod tilted_tests {
    use super::*;

    #[test]
    fn boost_preserves_mass_shell() {
        for m in [0.0, 0.7, 3.0] {
            let r = boost_shell_residual(&[1.0, 0.9, 1.2], &[0.15, -0.1, 0.2], m);
            assert!(r < 1e-13, "m={m} shell={r:e}");
        }
    }

    #[test]
    fn zero_tilt_is_bit_exact() {
        for (l, i) in [(0usize, 0i32), (0, 1), (1, 0), (2, 0), (3, 0), (4, 0)] {
            let a = j_moment(&[1.0, 0.9, 1.2], 0.7, l, i, 0.0, 2);
            let b = j_moment_tilted(&[1.0, 0.9, 1.2], &[0.0; 3], 0.7, l, i, 0.0, 2);
            assert_eq!(a, b, "(l,i)=({l},{i})");
        }
    }

    #[test]
    fn boost_activates_odd_l_without_dipole() {
        // ★ 등방 f₀ + 등방 a_vec 에서도 boost 가 홀수 l 을 켠다 (인공 쌍극자 불필요)
        let iso = [1.0, 1.0, 1.0];
        let rho = j_moment_tilted(&iso, &[0.0, 0.0, 0.25], 0.0, 0, 0, 0.0, 2)[0];
        for l in [1usize, 3] {
            let j = j_moment_tilted(&iso, &[0.0, 0.0, 0.25], 0.0, l, 0, 0.0, 2);
            let w = j.iter().fold(0.0f64, |a, b| a.max(b.abs()));
            assert!(w > 1e-6 * rho, "l={l} w={w:e}");
            // 법선 프레임에서는 항등적 0
            let j0 = j_moment(&iso, 0.0, l, 0, 0.0, 2);
            let w0 = j0.iter().fold(0.0f64, |a, b| a.max(b.abs()));
            assert!(w0 < 1e-14 * rho, "l={l} 법선 w={w0:e}");
        }
    }

    #[test]
    fn dipole_matches_closed_form() {
        // |q′|/ρ′ = v(ρ+p)/(ρ+pv²)  — 구적 미사용 독립 검산
        let iso = [1.0, 1.0, 1.0];
        for s in [0.05, 0.2, 0.4, 0.7] {
            let v = [0.0, 0.0, s];
            let rho = j_moment(&iso, 0.0, 0, 0, 0.0, 2)[0];
            let p = j_moment(&iso, 0.0, 0, 1, 0.0, 2)[0] / 3.0;
            let (rt, _, qt, _) = moments_tilted(&iso, &v, 0.0);
            let got = qt.iter().fold(0.0f64, |a, b| a.max(b.abs())) / rt;
            let want = s * (rho + p) / (rho + p * s * s);
            assert!((got - want).abs() < 1e-12, "v={s} {got} vs {want}");
        }
    }

    #[test]
    fn tilted_energy_density_exceeds_normal() {
        let (rt, _, _, _) = moments_tilted(&[1.0, 0.9, 1.2], &[0.15, -0.1, 0.2], 0.7);
        let rn = j_moment(&[1.0, 0.9, 1.2], 0.7, 0, 0, 0.0, 2)[0];
        assert!(rt > rn, "{rt} !> {rn}");
    }
}
