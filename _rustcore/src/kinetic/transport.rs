//! Q5 ★ **반-라그랑주 수송** — 이 계획의 핵심 커널 (76차).
//!
//! 고정 tetrad 격자 위에서 자유흐름을 역추적 + 보간으로 나른다.
//! I2c 불변격자의 축비 벽 (LNA_WALL = 300) 을 **구조적으로** 제거한다.
//!
//! 한 스텝의 구조:
//!   1. 각 출력 방향 ê_i 에서 (L2) 를 **역방향** 적분 → ê_back,i 와 (L1) 의
//!      누적 ln p 변화 ln_s_i.
//!      ★ 무질량이면 이 계산이 반경·종에 무관 → **스텝당 1회**.
//!   2. ê_back,i 의 보간 가중을 **희소 행렬로 굳혀** 재사용 (결정적 축약순서).
//!   3. Mode A:  G_new[i] = e^{n·ln_s_i} · (스텐실 적용)      ← 반경격자 불필요
//!      Mode B:  방향 스텐실을 n_p 슬라이스에 적용 후 방향별 반경 시프트.
//!
//! 저장 배치: f[i * n_p + j]  (방향-주).  방향 패스는 스텐실 점마다 길이 n_p 의
//! **연속 블록**을 읽고, 반경 패스는 같은 블록 위에서 돈다 — 두 패스 모두 최적.
//!
//! 각 보간: theta 는 GL 절점 위 Lagrange, phi 는 균일·주기 Lagrange.
//! 극을 넘는 지표는 (theta, phi) -> (-theta, phi + pi) 반사로 **정확히** 접는다
//! (스칼라장의 성질; 근사 아님).  n_phi 는 짝수를 요구한다.

use crate::kinetic::characteristics::{direction_map, Background};
use crate::kinetic::radial::{shift_stencil, RadialGrid, Tail};
use crate::kinetic::sphere::SphereGrid;

pub struct TransportPlan {
    pub n_ang: usize,
    pub s_ang: usize,
    pub ang_idx: Vec<u32>,
    pub ang_w: Vec<f64>,
    pub rad_off: Vec<i64>,
    pub rad_w: Vec<f64>,
    pub k_rad: usize,
    /// 특성곡선을 따른 ln p 의 **전방** 변화 (= -역추적 증분)
    pub ln_s: Vec<f64>,
    /// 방향맵 Jacobian 대용 최소값 (초점화 감시자)
    pub jac_min: f64,
}

/// theta 지표를 극 반사로 접는다.  반환 (접힌 지표, phi 를 pi 만큼 돌릴지).
#[inline]
fn fold_theta(j: i64, n: usize) -> (usize, bool) {
    let n = n as i64;
    if j < 0 {
        ((-1 - j) as usize, true)
    } else if j >= n {
        ((2 * n - 1 - j).max(0) as usize, true)
    } else {
        (j as usize, false)
    }
}

/// ★ Q5b: 임의의 역추적점 `eb` (3M) 에서 각 보간 스텐실을 만든다.
/// plan_step 이 쓰던 루프를 그대로 뽑아낸 것 — 잔여 이류가 이걸 재사용한다.
pub fn build_stencils(
    sph: &SphereGrid,
    eb: &[f64],
    k_theta: usize,
    k_phi: usize,
) -> (Vec<u32>, Vec<f64>, f64) {
    let m = sph.len();
    assert!(sph.n_phi % 2 == 0, "n_phi 는 짝수");
    let s_ang = k_theta * k_phi;
    let mut ang_idx = vec![0u32; m * s_ang];
    let mut ang_w = vec![0.0f64; m * s_ang];
    let nt = sph.n_theta;
    let np_ = sph.n_phi;
    let dphi = 2.0 * std::f64::consts::PI / np_ as f64;
    for i in 0..m {
        let e = [eb[3 * i], eb[3 * i + 1], eb[3 * i + 2]];
        let nrm = (e[0] * e[0] + e[1] * e[1] + e[2] * e[2]).sqrt();
        let ct = (e[2] / nrm).clamp(-1.0, 1.0);
        let mut ph = (e[1]).atan2(e[0]);
        if ph < 0.0 {
            ph += 2.0 * std::f64::consts::PI;
        }
        let mut j0 = nt - 2;
        for j in 0..nt - 1 {
            if (ct - sph.ct[j]) * (ct - sph.ct[j + 1]) <= 0.0 {
                j0 = j;
                break;
            }
        }
        let tstart = j0 as i64 - (k_theta as i64 / 2 - 1);
        let u = ph / dphi;
        let p0 = u.floor();
        let pstart = p0 as i64 - (k_phi as i64 / 2 - 1);
        let target = (u - p0) - (pstart as f64 - p0);
        let mut wphi = vec![0.0; k_phi];
        for a in 0..k_phi {
            let mut v = 1.0;
            for b in 0..k_phi {
                if a != b {
                    v *= (target - b as f64) / (a as f64 - b as f64);
                }
            }
            wphi[a] = v;
        }
        let mut tj = vec![0usize; k_theta];
        let mut xs = vec![0.0; k_theta];
        let mut flip = vec![false; k_theta];
        for a in 0..k_theta {
            let (jf, fl) = fold_theta(tstart + a as i64, nt);
            tj[a] = jf;
            flip[a] = fl;
            xs[a] = if fl { -sph.ct[jf] } else { sph.ct[jf] };
        }
        let mut wth = vec![0.0; k_theta];
        for a in 0..k_theta {
            let mut num = 1.0;
            for b in 0..k_theta {
                if a != b {
                    num *= (ct - xs[b]) / (xs[a] - xs[b]);
                }
            }
            wth[a] = num;
        }
        for a in 0..k_theta {
            for b in 0..k_phi {
                let mut pj = pstart + b as i64;
                if flip[a] {
                    pj += (np_ as i64) / 2;
                }
                let pj = pj.rem_euclid(np_ as i64) as usize;
                let k = i * s_ang + a * k_phi + b;
                ang_idx[k] = (tj[a] * np_ + pj) as u32;
                ang_w[k] = wth[a] * wphi[b];
            }
        }
    }
    let mut jac_min = f64::INFINITY;
    for it in 0..nt {
        for ip in 0..np_ {
            let i = it * np_ + ip;
            let i2 = it * np_ + (ip + 1) % np_;
            let d0 = ang_dist(&sph.ehat, i, i2);
            let d1 = ang_dist(eb, i, i2);
            if d0 > 1e-14 {
                jac_min = jac_min.min(d1 / d0);
            }
        }
    }
    (ang_idx, ang_w, jac_min)
}

/// Q5b: 이미 계산된 역추적점 + ln 스케일로 계획을 만든다.
pub fn plan_from_points(
    sph: &SphereGrid,
    eb: &[f64],
    ln_s: &[f64],
    k_theta: usize,
    k_phi: usize,
) -> TransportPlan {
    let (ang_idx, ang_w, jac_min) = build_stencils(sph, eb, k_theta, k_phi);
    TransportPlan {
        n_ang: sph.len(),
        s_ang: k_theta * k_phi,
        ang_idx,
        ang_w,
        rad_off: vec![],
        rad_w: vec![],
        k_rad: 0,
        ln_s: ln_s.to_vec(),
        jac_min,
    }
}

#[allow(clippy::too_many_arguments)]
pub fn plan_step(
    sph: &SphereGrid,
    rad: Option<&RadialGrid>,
    bg0: &Background,
    bg1: &Background,
    dt: f64,
    mass: f64,
    lnp_ref: f64,
    substeps: usize,
    k_theta: usize,
    k_phi: usize,
    k_rad: usize,
) -> TransportPlan {
    let m = sph.len();
    assert!(
        sph.n_phi % 2 == 0,
        "n_phi 는 짝수 (극 반사가 phi+pi 를 격자점으로 보내야 한다)"
    );
    // 1. 역추적: t+dt 의 격자점에서 t 로 (배경은 bg1 -> bg0 순서)
    let (eb, dlnp_back) = direction_map(&sph.ehat, mass, lnp_ref, bg1, bg0, -dt, substeps, false);
    let ln_s: Vec<f64> = dlnp_back.iter().map(|x| -x).collect();

    let s_ang = k_theta * k_phi;
    let mut ang_idx = vec![0u32; m * s_ang];
    let mut ang_w = vec![0.0f64; m * s_ang];
    let nt = sph.n_theta;
    let np_ = sph.n_phi;
    let dphi = 2.0 * std::f64::consts::PI / np_ as f64;

    for i in 0..m {
        let e = [eb[3 * i], eb[3 * i + 1], eb[3 * i + 2]];
        let nrm = (e[0] * e[0] + e[1] * e[1] + e[2] * e[2]).sqrt();
        let ct = (e[2] / nrm).clamp(-1.0, 1.0);
        let mut ph = e[1].atan2(e[0]);
        if ph < 0.0 {
            ph += 2.0 * std::f64::consts::PI;
        }
        // GL 절점은 x 내림차순 (ct[0] 최대) — 감싸는 구간을 선형 탐색
        let mut j0 = nt - 2;
        for j in 0..nt - 1 {
            if (ct - sph.ct[j]) * (ct - sph.ct[j + 1]) <= 0.0 {
                j0 = j;
                break;
            }
        }
        let tstart = j0 as i64 - (k_theta as i64 / 2 - 1);
        let u = ph / dphi;
        let p0 = u.floor();
        let pstart = p0 as i64 - (k_phi as i64 / 2 - 1);
        let target = (u - p0) - (pstart as f64 - p0);

        let mut wphi = vec![0.0; k_phi];
        for a in 0..k_phi {
            let mut v = 1.0;
            for b in 0..k_phi {
                if a != b {
                    v *= (target - b as f64) / (a as f64 - b as f64);
                }
            }
            wphi[a] = v;
        }

        let mut tj = vec![0usize; k_theta];
        let mut xs = vec![0.0; k_theta];
        let mut flip = vec![false; k_theta];
        for a in 0..k_theta {
            let (jf, fl) = fold_theta(tstart + a as i64, nt);
            tj[a] = jf;
            flip[a] = fl;
            xs[a] = if fl { -sph.ct[jf] } else { sph.ct[jf] };
        }
        let mut wth = vec![0.0; k_theta];
        for a in 0..k_theta {
            let mut num = 1.0;
            for b in 0..k_theta {
                if a != b {
                    num *= (ct - xs[b]) / (xs[a] - xs[b]);
                }
            }
            wth[a] = num;
        }

        for a in 0..k_theta {
            for b in 0..k_phi {
                let mut pj = pstart + b as i64;
                if flip[a] {
                    pj += (np_ as i64) / 2;
                }
                let pj = pj.rem_euclid(np_ as i64) as usize;
                let k = i * s_ang + a * k_phi + b;
                ang_idx[k] = (tj[a] * np_ + pj) as u32;
                ang_w[k] = wth[a] * wphi[b];
            }
        }
    }

    let (rad_off, rad_w, k_rad_eff) = if let Some(r) = rad {
        let mut off = vec![0i64; m * k_rad];
        let mut w = vec![0.0f64; m * k_rad];
        for i in 0..m {
            let (o, ww) = shift_stencil(r, ln_s[i], k_rad);
            for a in 0..k_rad {
                off[i * k_rad + a] = o[a];
                w[i * k_rad + a] = ww[a];
            }
        }
        (off, w, k_rad)
    } else {
        (vec![], vec![], 0)
    };

    let mut jac_min = f64::INFINITY;
    for it in 0..nt {
        for ip in 0..np_ {
            let i = it * np_ + ip;
            let i2 = it * np_ + (ip + 1) % np_;
            let d0 = ang_dist(&sph.ehat, i, i2);
            let d1 = ang_dist(&eb, i, i2);
            if d0 > 1e-14 {
                jac_min = jac_min.min(d1 / d0);
            }
        }
    }

    TransportPlan {
        n_ang: m,
        s_ang,
        ang_idx,
        ang_w,
        rad_off,
        rad_w,
        k_rad: k_rad_eff,
        ln_s,
        jac_min,
    }
}

#[inline]
fn ang_dist(e: &[f64], i: usize, j: usize) -> f64 {
    let d = [
        e[3 * i] - e[3 * j],
        e[3 * i + 1] - e[3 * j + 1],
        e[3 * i + 2] - e[3 * j + 2],
    ];
    (d[0] * d[0] + d[1] * d[1] + d[2] * d[2]).sqrt()
}

/// Mode A — 가중 각밀도 G(ê).  weight_n = 4 가 에너지밀도.
pub fn apply_mode_a(g: &[f64], plan: &TransportPlan, weight_n: f64) -> Vec<f64> {
    let m = plan.n_ang;
    let s = plan.s_ang;
    let mut out = vec![0.0; m];
    for i in 0..m {
        let mut v = 0.0;
        for k in 0..s {
            v += plan.ang_w[i * s + k] * g[plan.ang_idx[i * s + k] as usize];
        }
        out[i] = v * (weight_n * plan.ln_s[i]).exp();
    }
    out
}

/// Mode B — 완전 f (방향-주 f[i*n_p + j]).  `log_state` 면 ln f 를 나른다.
pub fn apply_mode_b(
    f: &[f64],
    plan: &TransportPlan,
    rad: &RadialGrid,
    log_state: bool,
    tail: Tail,
) -> Vec<f64> {
    let m = plan.n_ang;
    let s = plan.s_ang;
    let np_ = rad.len();
    let mut tmp = vec![0.0; m * np_];
    for i in 0..m {
        let base = i * s;
        for k in 0..s {
            let w = plan.ang_w[base + k];
            if w == 0.0 {
                continue;
            }
            let src = plan.ang_idx[base + k] as usize * np_;
            let dst = i * np_;
            for j in 0..np_ {
                tmp[dst + j] += w * f[src + j];
            }
        }
    }
    let mut out = vec![0.0; m * np_];
    let p = rad.p();
    for i in 0..m {
        let blk = &tmp[i * np_..(i + 1) * np_];
        let lnf: Vec<f64> = if log_state {
            blk.to_vec()
        } else {
            blk.iter().map(|x| x.max(1e-300).ln()).collect()
        };
        for j in 0..np_ {
            let mut v = 0.0;
            for a in 0..plan.k_rad {
                let jj = j as i64 + plan.rad_off[i * plan.k_rad + a];
                v += plan.rad_w[i * plan.k_rad + a] * extend_lnf(&lnf, &p, jj, tail);
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

#[cfg(test)]
mod tests {
    use super::*;

    fn bg_i(sig: [f64; 6]) -> Background {
        Background {
            h: 1.0,
            sigma: sig,
            rot: [0.0; 3],
            n: [0.0; 6],
            a: [0.0; 3],
        }
    }

    #[test]
    fn identity_plan_when_no_direction_flow() {
        let sph = SphereGrid::new(16, 32);
        let bg = bg_i([0.0; 6]);
        let plan = plan_step(&sph, None, &bg, &bg, 0.05, 0.0, 0.0, 4, 4, 4, 8);
        let g: Vec<f64> = (0..sph.len())
            .map(|i| 1.0 + 0.1 * (i as f64).sin())
            .collect();
        let out = apply_mode_a(&g, &plan, 0.0);
        let e = g
            .iter()
            .zip(&out)
            .map(|(a, b)| (a - b).abs())
            .fold(0.0f64, f64::max);
        assert!(e < 1e-12, "{e}");
        assert!((plan.jac_min - 1.0).abs() < 1e-10, "{}", plan.jac_min);
    }

    #[test]
    fn isotropic_expansion_scales_mode_a_analytically() {
        let sph = SphereGrid::new(16, 32);
        let bg = bg_i([0.0; 6]);
        let dt = 0.3;
        let plan = plan_step(&sph, None, &bg, &bg, dt, 0.0, 0.0, 8, 4, 4, 8);
        let g = vec![1.0; sph.len()];
        let out = apply_mode_a(&g, &plan, 4.0);
        let want = (-4.0f64 * dt).exp();
        let e = out.iter().map(|x| (x - want).abs()).fold(0.0f64, f64::max);
        assert!(e < 1e-12, "{e} want {want}");
    }

    #[test]
    fn stencil_is_partition_of_unity() {
        let sph = SphereGrid::new(24, 48);
        let bg = Background {
            h: 0.5,
            sigma: [0.4, -0.25, -0.15, 0.05, 0.0, 0.0],
            rot: [0.1, 0.0, -0.05],
            n: [0.3, -0.2, 0.1, 0.0, 0.0, 0.0],
            a: [0.0; 3],
        };
        let plan = plan_step(&sph, None, &bg, &bg, 0.05, 0.0, 0.0, 4, 6, 6, 8);
        for i in 0..sph.len() {
            let s: f64 = (0..plan.s_ang)
                .map(|k| plan.ang_w[i * plan.s_ang + k])
                .sum();
            assert!((s - 1.0).abs() < 1e-11, "i={i} s={s}");
        }
    }
}
