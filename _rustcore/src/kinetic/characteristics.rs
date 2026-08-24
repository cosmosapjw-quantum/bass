//! Q2 · **특성곡선 커널** — 전 11유형 · 질량 포함 (76차).
//!
//! 유도·검증: `audit/q2_characteristics_general.py`
//!   (T1) dp_a/dl = C^c_{ba} p_c p^b
//!        = ((n p) x p)_a + (a·p) p_a - a_a |p|^2        ← sympy 항등
//!   좌표 측지선 (type V · type II, m = 0 과 0.5) 대비 실측 ≤ 2.1e-14.
//!
//! 정규직교틀 · 시간 t:
//!   dp̂_a/dt = -H p̂_a - sigma_ab p̂_b + (R x p̂)_a
//!             + (1/Ê)[ ((N̂ p̂) x p̂)_a + (Â·p̂) p̂_a - Â_a |p̂|^2 ]
//!
//! 방향·크기 분해 (p̂ = p ê):
//!   dln p/dt = -(H + sigma_ab ê^a ê^b)                      ← class B 에서도 불변
//!   dê_a/dt  = -(sigma·ê - (ê·sigma·ê)ê)_a + (R x ê)_a
//!              + (p/Ê)[ ((N̂ ê) x ê)_a - (Â - (Â·ê)ê)_a ]
//!
//! ★ 무질량이면 p/Ê = 1 이라 dê/dt 가 **p 에 무관 = 자율계** — Q5 의
//! "스텐실 한 번, 전 반경 재사용" 이 여기서 나온다.
//!
//! 포장: sigma·n 은 대칭 6성분 (11,22,33,12,13,23) — Q-CONTRACT §2.

#[derive(Clone, Copy, Debug, Default)]
pub struct Background {
    pub h: f64,
    pub sigma: [f64; 6],
    pub rot: [f64; 3],
    pub n: [f64; 6],
    pub a: [f64; 3],
}

impl Background {
    pub fn lerp(&self, other: &Background, s: f64) -> Background {
        let mix = |x: f64, y: f64| x + s * (y - x);
        let mut o = Background {
            h: mix(self.h, other.h),
            ..Default::default()
        };
        for k in 0..6 {
            o.sigma[k] = mix(self.sigma[k], other.sigma[k]);
            o.n[k] = mix(self.n[k], other.n[k]);
        }
        for k in 0..3 {
            o.rot[k] = mix(self.rot[k], other.rot[k]);
            o.a[k] = mix(self.a[k], other.a[k]);
        }
        o
    }
}

#[inline]
fn sym_apply(m: &[f64; 6], v: &[f64; 3]) -> [f64; 3] {
    // (11,22,33,12,13,23)
    [
        m[0] * v[0] + m[3] * v[1] + m[4] * v[2],
        m[3] * v[0] + m[1] * v[1] + m[5] * v[2],
        m[4] * v[0] + m[5] * v[1] + m[2] * v[2],
    ]
}

#[inline]
fn cross(u: &[f64; 3], v: &[f64; 3]) -> [f64; 3] {
    [
        u[1] * v[2] - u[2] * v[1],
        u[2] * v[0] - u[0] * v[2],
        u[0] * v[1] - u[1] * v[0],
    ]
}

#[inline]
fn dot(u: &[f64; 3], v: &[f64; 3]) -> f64 {
    u[0] * v[0] + u[1] * v[1] + u[2] * v[2]
}

/// dp̂_a/dt — 공변 정규직교 성분 형태 (I1a 축약 게이트용).
pub fn char_rhs_p(phat: &[f64; 3], mass: f64, bg: &Background) -> [f64; 3] {
    let p2 = dot(phat, phat);
    let e = (mass * mass + p2).sqrt();
    let np = sym_apply(&bg.n, phat);
    let cn = cross(&np, phat);
    let cr = cross(&bg.rot, phat);
    let sp = sym_apply(&bg.sigma, phat);
    let ap = dot(&bg.a, phat);
    let mut out = [0.0; 3];
    for k in 0..3 {
        out[k] = -bg.h * phat[k] - sp[k] + cr[k]
            + (cn[k] + ap * phat[k] - p2 * bg.a[k]) / e;
    }
    out
}

/// (dê/dt, dln p/dt) — 방향·크기 분해형 (Q5 가 쓰는 형태).
pub fn char_rhs_split(
    ehat: &[f64; 3],
    lnp: f64,
    mass: f64,
    bg: &Background,
) -> ([f64; 3], f64) {
    let p = lnp.exp();
    let e = (mass * mass + p * p).sqrt();
    let pe = p / e; // 무질량이면 정확히 1
    let se = sym_apply(&bg.sigma, ehat);
    let ese = dot(ehat, &se);
    let ne = sym_apply(&bg.n, ehat);
    let cn = cross(&ne, ehat);
    let cr = cross(&bg.rot, ehat);
    let ae = dot(&bg.a, ehat);
    let mut de = [0.0; 3];
    for k in 0..3 {
        de[k] = -(se[k] - ese * ehat[k]) + cr[k]
            + pe * (cn[k] - (bg.a[k] - ae * ehat[k]));
    }
    (de, -(bg.h + ese))
}

#[inline]
fn renorm(e: &mut [f64; 3]) {
    let n = (e[0] * e[0] + e[1] * e[1] + e[2] * e[2]).sqrt();
    if n > 0.0 {
        e[0] /= n;
        e[1] /= n;
        e[2] /= n;
    }
}

/// 한 노드의 특성곡선을 dt 만큼 적분 (RK4, substeps).  dt < 0 이면 역추적.
/// 배경은 bg0 → bg1 선형보간 (한 스텝 안에서).
/// 반환 (ê_end, ln p 증분).  `renormalize` 는 T3 의 수치판을 **강제**하지 않고
/// 재정규화로 덮는 옵션 — 기본 false (보존은 **측정 대상**이지 강제 대상이 아니다).
pub fn integrate_characteristic(
    ehat0: &[f64; 3],
    mass: f64,
    lnp0: f64,
    bg0: &Background,
    bg1: &Background,
    dt: f64,
    substeps: usize,
    renormalize: bool,
) -> ([f64; 3], f64) {
    let h = dt / substeps as f64;
    let mut e = *ehat0;
    let mut lp = lnp0;
    for k in 0..substeps {
        let s0 = k as f64 / substeps as f64;
        let sh = (k as f64 + 0.5) / substeps as f64;
        let s1 = (k as f64 + 1.0) / substeps as f64;
        let b0 = bg0.lerp(bg1, s0);
        let bh = bg0.lerp(bg1, sh);
        let b1 = bg0.lerp(bg1, s1);

        let f = |ee: &[f64; 3], ll: f64, b: &Background| char_rhs_split(ee, ll, mass, b);
        let (k1e, k1l) = f(&e, lp, &b0);
        let e2 = [
            e[0] + 0.5 * h * k1e[0],
            e[1] + 0.5 * h * k1e[1],
            e[2] + 0.5 * h * k1e[2],
        ];
        let (k2e, k2l) = f(&e2, lp + 0.5 * h * k1l, &bh);
        let e3 = [
            e[0] + 0.5 * h * k2e[0],
            e[1] + 0.5 * h * k2e[1],
            e[2] + 0.5 * h * k2e[2],
        ];
        let (k3e, k3l) = f(&e3, lp + 0.5 * h * k2l, &bh);
        let e4 = [
            e[0] + h * k3e[0],
            e[1] + h * k3e[1],
            e[2] + h * k3e[2],
        ];
        let (k4e, k4l) = f(&e4, lp + h * k3l, &b1);
        for j in 0..3 {
            e[j] += h / 6.0 * (k1e[j] + 2.0 * k2e[j] + 2.0 * k3e[j] + k4e[j]);
        }
        lp += h / 6.0 * (k1l + 2.0 * k2l + 2.0 * k3l + k4l);
        if renormalize {
            renorm(&mut e);
        }
    }
    (e, lp - lnp0)
}

/// 전 방향격자를 한 번에 (Q5 의 TransportPlan 이 부르는 진입점).
/// 반환 (ê_out 평탄화 3M, dln p M).
pub fn direction_map(
    ehat: &[f64],
    mass: f64,
    lnp: f64,
    bg0: &Background,
    bg1: &Background,
    dt: f64,
    substeps: usize,
    renormalize: bool,
) -> (Vec<f64>, Vec<f64>) {
    let m = ehat.len() / 3;
    let mut eo = vec![0.0; 3 * m];
    let mut dl = vec![0.0; m];
    for i in 0..m {
        let e0 = [ehat[3 * i], ehat[3 * i + 1], ehat[3 * i + 2]];
        let (e, d) =
            integrate_characteristic(&e0, mass, lnp, bg0, bg1, dt, substeps, renormalize);
        eo[3 * i] = e[0];
        eo[3 * i + 1] = e[1];
        eo[3 * i + 2] = e[2];
        dl[i] = d;
    }
    (eo, dl)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn bg_test() -> Background {
        Background {
            h: 0.7,
            sigma: [0.3, -0.2, -0.1, 0.05, -0.02, 0.07],
            rot: [0.1, -0.3, 0.2],
            n: [0.9, -0.4, 0.3, 0.1, 0.0, -0.05],
            a: [0.2, -0.1, 0.05],
        }
    }

    #[test]
    fn split_form_agrees_with_covariant_form() {
        let bg = bg_test();
        let e = {
            let mut v = [0.3, -0.7, 0.5];
            renorm(&mut v);
            v
        };
        for (lnp, mass) in [(0.0f64, 0.0f64), (0.5, 0.0), (-0.3, 0.8)] {
            let p = lnp.exp();
            let ph = [p * e[0], p * e[1], p * e[2]];
            let dp = char_rhs_p(&ph, mass, &bg);
            let (de, dl) = char_rhs_split(&e, lnp, mass, &bg);
            // dp̂ = (dp) ê + p dê  =>  분해 재조립
            for k in 0..3 {
                let want = dl * p * e[k] + p * de[k];
                assert!((want - dp[k]).abs() < 1e-13, "{want} vs {}", dp[k]);
            }
        }
    }

    #[test]
    fn norm_is_preserved_by_n_and_a_terms() {
        // sigma, H, R 를 끄면 |ê| 가 정확 보존 (T3 + Q-T3)
        let bg = Background {
            h: 0.0,
            sigma: [0.0; 6],
            rot: [0.0; 3],
            n: [0.9, -0.4, 0.3, 0.1, 0.0, -0.05],
            a: [0.2, -0.1, 0.05],
        };
        let mut e = [0.3, -0.7, 0.5];
        renorm(&mut e);
        let (de, _) = char_rhs_split(&e, 0.0, 0.0, &bg);
        let d = e[0] * de[0] + e[1] * de[1] + e[2] * de[2];
        assert!(d.abs() < 1e-15, "{d}");
    }

    #[test]
    fn massless_direction_flow_is_p_independent() {
        let bg = bg_test();
        let mut e = [0.1, 0.9, -0.4];
        renorm(&mut e);
        let (d1, _) = char_rhs_split(&e, -3.0, 0.0, &bg);
        let (d2, _) = char_rhs_split(&e, 5.0, 0.0, &bg);
        for k in 0..3 {
            assert!((d1[k] - d2[k]).abs() < 1e-15);
        }
    }

    #[test]
    fn rk4_is_fourth_order() {
        let bg = bg_test();
        let mut e = [0.2, -0.5, 0.8];
        renorm(&mut e);
        let run = |n: usize| integrate_characteristic(&e, 0.0, 0.0, &bg, &bg, 1.0, n, false).0;
        let r = [run(8), run(16), run(32), run(1024)];
        let err = |x: [f64; 3]| {
            (0..3).map(|k| (x[k] - r[3][k]).abs()).fold(0.0f64, f64::max)
        };
        let (e0, e1, e2) = (err(r[0]), err(r[1]), err(r[2]));
        let o1 = (e0 / e1).log2();
        let o2 = (e1 / e2).log2();
        assert!((o1 - 4.0).abs() < 0.3, "order {o1}");
        assert!((o2 - 4.0).abs() < 0.3, "order {o2}");
    }
}
