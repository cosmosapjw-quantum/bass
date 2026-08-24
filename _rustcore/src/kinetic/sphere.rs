//! Q3 · **구면 표현층** — 고정 tetrad 구면 위의 격자 · 실수 구면조화 변환 (76차).
//!
//! 격자: Gauss-Legendre in cos(theta) x 균일 phi.  인덱스 i = it * n_phi + ip.
//! 가중: w_i = w_gl[it] * (2 pi / n_phi)   =>  sum w_i = 4 pi.
//!
//! 실수 구면조화 (직교정규, Condon-Shortley 포함):
//!     Y_{l0}     = Pbar_l^0(x)
//!     Y_{l,+m}   = sqrt(2) Pbar_l^m(x) cos(m phi)      (m > 0)
//!     Y_{l,-m}   = sqrt(2) Pbar_l^m(x) sin(m phi)
//! 계수 색인: idx(l,m) = l*l + (m + l),  총 (L+1)^2.
//!
//! ★ 규약을 문헌 표로 믿지 않는다 — 직교정규성을 시험이 수치로 잰다
//!   (tests/test_q3_sphere.py; J1 의 3j 교훈 승계).
//!
//! 비용: 분석·합성 모두 O(n_ang * L + n_theta * L^2).  FFT 대신 사전계산
//! cos/sin 표의 직접 합 — **결정적 축약순서**가 Q11 의 비트 재현에 필요하다.

const PI: f64 = std::f64::consts::PI;

/// Gauss-Legendre 절점·가중 (Newton, [-1,1]).
pub fn gauss_legendre(n: usize) -> (Vec<f64>, Vec<f64>) {
    let mut x = vec![0.0; n];
    let mut w = vec![0.0; n];
    for i in 0..n {
        // 초기 추정 (Chebyshev)
        let mut z = (PI * (i as f64 + 0.75) / (n as f64 + 0.5)).cos();
        for _ in 0..100 {
            let (mut p0, mut p1) = (1.0f64, 0.0f64);
            for j in 0..n {
                let p2 = p1;
                p1 = p0;
                let jj = j as f64;
                p0 = ((2.0 * jj + 1.0) * z * p1 - jj * p2) / (jj + 1.0);
            }
            let dp = (n as f64) * (z * p0 - p1) / (z * z - 1.0);
            let dz = p0 / dp;
            z -= dz;
            if dz.abs() < 1e-16 {
                break;
            }
        }
        let (mut p0, mut p1) = (1.0f64, 0.0f64);
        for j in 0..n {
            let p2 = p1;
            p1 = p0;
            let jj = j as f64;
            p0 = ((2.0 * jj + 1.0) * z * p1 - jj * p2) / (jj + 1.0);
        }
        let dp = (n as f64) * (z * p0 - p1) / (z * z - 1.0);
        x[i] = z;
        w[i] = 2.0 / ((1.0 - z * z) * dp * dp);
    }
    (x, w)
}

pub struct SphereGrid {
    pub n_theta: usize,
    pub n_phi: usize,
    pub ct: Vec<f64>, // cos(theta), 길이 n_theta
    pub st: Vec<f64>,
    pub wt: Vec<f64>, // GL 가중
    pub phi: Vec<f64>,
    pub ehat: Vec<f64>, // 3M
    pub w: Vec<f64>,    // M, 합 = 4 pi
}

impl SphereGrid {
    pub fn new(n_theta: usize, n_phi: usize) -> Self {
        let (x, wx) = gauss_legendre(n_theta);
        let dphi = 2.0 * PI / n_phi as f64;
        let phi: Vec<f64> = (0..n_phi).map(|k| dphi * k as f64).collect();
        let m = n_theta * n_phi;
        let mut ehat = vec![0.0; 3 * m];
        let mut w = vec![0.0; m];
        let mut st = vec![0.0; n_theta];
        for it in 0..n_theta {
            let s = (1.0 - x[it] * x[it]).max(0.0).sqrt();
            st[it] = s;
            for ip in 0..n_phi {
                let i = it * n_phi + ip;
                ehat[3 * i] = s * phi[ip].cos();
                ehat[3 * i + 1] = s * phi[ip].sin();
                ehat[3 * i + 2] = x[it];
                w[i] = wx[it] * dphi;
            }
        }
        SphereGrid {
            n_theta,
            n_phi,
            ct: x,
            st,
            wt: wx,
            phi,
            ehat,
            w,
        }
    }

    pub fn len(&self) -> usize {
        self.n_theta * self.n_phi
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }
}

/// 완전정규화 결합 Legendre Pbar_l^m(x), m 고정, l = m..=l_max.
/// 반환 길이 l_max+1 (l < m 은 0).
fn pbar_column(l_max: usize, m: usize, x: f64, s: f64) -> Vec<f64> {
    let mut out = vec![0.0; l_max + 1];
    if m > l_max {
        return out;
    }
    // Pbar_0^0 = 1/sqrt(4 pi)
    let mut pmm = 1.0 / (4.0 * PI).sqrt();
    for k in 1..=m {
        let kk = k as f64;
        pmm *= -((2.0 * kk + 1.0) / (2.0 * kk)).sqrt() * s;
    }
    out[m] = pmm;
    if m + 1 <= l_max {
        out[m + 1] = (2.0 * m as f64 + 3.0).sqrt() * x * pmm;
    }
    for l in (m + 2)..=l_max {
        let (lf, mf) = (l as f64, m as f64);
        let a = ((2.0 * lf - 1.0) * (2.0 * lf + 1.0) / ((lf - mf) * (lf + mf))).sqrt();
        let b = ((2.0 * lf + 1.0) * (lf + mf - 1.0) * (lf - mf - 1.0)
            / ((2.0 * lf - 3.0) * (lf - mf) * (lf + mf)))
            .sqrt();
        out[l] = a * x * out[l - 1] - b * out[l - 2];
    }
    out
}

#[inline]
pub fn idx(l: usize, m: i64) -> usize {
    l * l + (m + l as i64) as usize
}

pub fn n_coef(l_max: usize) -> usize {
    (l_max + 1) * (l_max + 1)
}

/// 임의 방향에서의 실수 구면조화 값 (길이 (L+1)^2).
pub fn ylm_at(l_max: usize, e: &[f64; 3]) -> Vec<f64> {
    let x = e[2].clamp(-1.0, 1.0);
    let s = (1.0 - x * x).max(0.0).sqrt();
    let phi = e[1].atan2(e[0]);
    let mut out = vec![0.0; n_coef(l_max)];
    let r2 = 2.0f64.sqrt();
    for m in 0..=l_max {
        let col = pbar_column(l_max, m, x, s);
        let (c, sn) = ((m as f64 * phi).cos(), (m as f64 * phi).sin());
        for l in m..=l_max {
            if m == 0 {
                out[idx(l, 0)] = col[l];
            } else {
                out[idx(l, m as i64)] = r2 * col[l] * c;
                out[idx(l, -(m as i64))] = r2 * col[l] * sn;
            }
        }
    }
    out
}

/// 분석: f (격자값) → a_lm.  O(n_ang * L + n_theta * L^2).
pub fn analyze(g: &SphereGrid, f: &[f64], l_max: usize) -> Vec<f64> {
    let mut a = vec![0.0; n_coef(l_max)];
    let r2 = 2.0f64.sqrt();
    let dphi = 2.0 * PI / g.n_phi as f64;
    // phi-방향 실수 푸리에 계수 (사전계산 표, 결정적 순서)
    let mut cosm = vec![0.0; (l_max + 1) * g.n_phi];
    let mut sinm = vec![0.0; (l_max + 1) * g.n_phi];
    for m in 0..=l_max {
        for ip in 0..g.n_phi {
            cosm[m * g.n_phi + ip] = (m as f64 * g.phi[ip]).cos();
            sinm[m * g.n_phi + ip] = (m as f64 * g.phi[ip]).sin();
        }
    }
    for it in 0..g.n_theta {
        let row = &f[it * g.n_phi..(it + 1) * g.n_phi];
        let wgt = g.wt[it] * dphi;
        for m in 0..=l_max {
            let mut fc = 0.0;
            let mut fs = 0.0;
            for ip in 0..g.n_phi {
                fc += row[ip] * cosm[m * g.n_phi + ip];
                fs += row[ip] * sinm[m * g.n_phi + ip];
            }
            let col = pbar_column(l_max, m, g.ct[it], g.st[it]);
            for l in m..=l_max {
                if m == 0 {
                    a[idx(l, 0)] += wgt * col[l] * fc;
                } else {
                    a[idx(l, m as i64)] += wgt * r2 * col[l] * fc;
                    a[idx(l, -(m as i64))] += wgt * r2 * col[l] * fs;
                }
            }
        }
    }
    a
}

/// 합성: a_lm → 격자값.
pub fn synthesize(g: &SphereGrid, a: &[f64], l_max: usize) -> Vec<f64> {
    let m_pts = g.len();
    let mut out = vec![0.0; m_pts];
    let r2 = 2.0f64.sqrt();
    let mut cosm = vec![0.0; (l_max + 1) * g.n_phi];
    let mut sinm = vec![0.0; (l_max + 1) * g.n_phi];
    for m in 0..=l_max {
        for ip in 0..g.n_phi {
            cosm[m * g.n_phi + ip] = (m as f64 * g.phi[ip]).cos();
            sinm[m * g.n_phi + ip] = (m as f64 * g.phi[ip]).sin();
        }
    }
    for it in 0..g.n_theta {
        // 각 m 마다 (cos, sin) 진폭을 모아 phi 합성
        let mut amp_c = vec![0.0; l_max + 1];
        let mut amp_s = vec![0.0; l_max + 1];
        for m in 0..=l_max {
            let col = pbar_column(l_max, m, g.ct[it], g.st[it]);
            let (mut ac, mut as_) = (0.0, 0.0);
            for l in m..=l_max {
                if m == 0 {
                    ac += a[idx(l, 0)] * col[l];
                } else {
                    ac += r2 * a[idx(l, m as i64)] * col[l];
                    as_ += r2 * a[idx(l, -(m as i64))] * col[l];
                }
            }
            amp_c[m] = ac;
            amp_s[m] = as_;
        }
        for ip in 0..g.n_phi {
            let mut v = 0.0;
            for m in 0..=l_max {
                v += amp_c[m] * cosm[m * g.n_phi + ip] + amp_s[m] * sinm[m * g.n_phi + ip];
            }
            out[it * g.n_phi + ip] = v;
        }
    }
    out
}

/// 임의 점들에서 합성 (반-라그랑주 보간의 스펙트럴 비교군).
pub fn synthesize_at(a: &[f64], l_max: usize, pts: &[f64]) -> Vec<f64> {
    let m = pts.len() / 3;
    let mut out = vec![0.0; m];
    for i in 0..m {
        let e = [pts[3 * i], pts[3 * i + 1], pts[3 * i + 2]];
        let y = ylm_at(l_max, &e);
        let mut v = 0.0;
        for k in 0..n_coef(l_max) {
            v += a[k] * y[k];
        }
        out[i] = v;
    }
    out
}

/// P_l f — 격자값.  l 만 남긴 투영 (충돌 지수의 P0/P2 가 이걸 쓴다).
pub fn project_l(g: &SphereGrid, f: &[f64], l: usize) -> Vec<f64> {
    let a = analyze(g, f, l);
    let mut a2 = vec![0.0; n_coef(l)];
    for m in -(l as i64)..=(l as i64) {
        a2[idx(l, m)] = a[idx(l, m)];
    }
    synthesize(g, &a2, l)
}

/// (rho, q_a(3), pi_ab(6 대칭포장)) — 절단 없는 정확 구적.
pub fn moments(g: &SphereGrid, f: &[f64]) -> (f64, [f64; 3], [f64; 6]) {
    let mut rho = 0.0;
    let mut q = [0.0; 3];
    let mut pi = [0.0; 6];
    for i in 0..g.len() {
        let wf = g.w[i] * f[i];
        let e = [g.ehat[3 * i], g.ehat[3 * i + 1], g.ehat[3 * i + 2]];
        rho += wf;
        for k in 0..3 {
            q[k] += wf * e[k];
        }
        pi[0] += wf * (e[0] * e[0] - 1.0 / 3.0);
        pi[1] += wf * (e[1] * e[1] - 1.0 / 3.0);
        pi[2] += wf * (e[2] * e[2] - 1.0 / 3.0);
        pi[3] += wf * e[0] * e[1];
        pi[4] += wf * e[0] * e[2];
        pi[5] += wf * e[1] * e[2];
    }
    (rho, q, pi)
}

/// 스펙트럼 꼬리 에너지 비율 (l > l_cut) — 격자 열화의 **상시 지표**.
pub fn tail_energy(g: &SphereGrid, f: &[f64], l_cut: usize, l_max: usize) -> f64 {
    let a = analyze(g, f, l_max);
    let mut tot = 0.0;
    let mut tail = 0.0;
    for l in 0..=l_max {
        for m in -(l as i64)..=(l as i64) {
            let v = a[idx(l, m)] * a[idx(l, m)];
            tot += v;
            if l > l_cut {
                tail += v;
            }
        }
    }
    if tot <= 0.0 {
        0.0
    } else {
        tail / tot
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn gl_weights_sum_and_exactness() {
        let (x, w) = gauss_legendre(24);
        let s: f64 = w.iter().sum();
        assert!((s - 2.0).abs() < 1e-14, "{s}");
        // degree 2n-1 = 47 까지 정확: ∫ x^10 dx = 2/11
        let m: f64 = x.iter().zip(&w).map(|(a, b)| a.powi(10) * b).sum();
        assert!((m - 2.0 / 11.0).abs() < 1e-14, "{m}");
    }

    #[test]
    fn weights_sum_to_four_pi() {
        let g = SphereGrid::new(16, 32);
        let s: f64 = g.w.iter().sum();
        assert!((s - 4.0 * PI).abs() < 1e-13, "{s}");
    }

    #[test]
    fn spherical_harmonics_are_orthonormal() {
        let g = SphereGrid::new(24, 48);
        let l_max = 8;
        let nc = n_coef(l_max);
        // <Y_k, Y_j> = delta
        let mut ys = vec![vec![0.0; g.len()]; nc];
        for i in 0..g.len() {
            let e = [g.ehat[3 * i], g.ehat[3 * i + 1], g.ehat[3 * i + 2]];
            let y = ylm_at(l_max, &e);
            for k in 0..nc {
                ys[k][i] = y[k];
            }
        }
        for k in 0..nc {
            for j in 0..nc {
                let v: f64 = (0..g.len()).map(|i| g.w[i] * ys[k][i] * ys[j][i]).sum();
                let want = if k == j { 1.0 } else { 0.0 };
                assert!((v - want).abs() < 1e-12, "k={k} j={j} v={v}");
            }
        }
    }

    #[test]
    fn analyze_synthesize_roundtrip() {
        let g = SphereGrid::new(24, 48);
        let l_max = 8;
        // 대역제한 f 를 만들고 왕복
        let mut a = vec![0.0; n_coef(l_max)];
        for (k, v) in a.iter_mut().enumerate() {
            *v = ((k * 37 % 11) as f64 - 5.0) / 7.0;
        }
        let f = synthesize(&g, &a, l_max);
        let a2 = analyze(&g, &f, l_max);
        let e = a
            .iter()
            .zip(&a2)
            .map(|(p, q)| (p - q).abs())
            .fold(0.0f64, f64::max);
        assert!(e < 1e-12, "{e}");
    }
}
