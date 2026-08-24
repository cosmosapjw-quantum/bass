//! Q4 · **반경 격자 + 해석적 점근 닫힘** (76차).
//!
//! 균일 ln p 격자.  무질량 자유흐름은 p -> p·s(ê) 인 **순수 dilation** 이므로
//! ln p 에서는 방향마다 상수인 **시프트**가 된다  =>  스텐실을 방향당 한 번만
//! 만들어 전 반경 노드에 재사용 (Q5 성능의 절반이 여기서 나온다).
//!
//! ★ ln f 를 보간하면 **멱법칙이 정확**하다 (ln f = k ln p 는 ln p 의 1차):
//!   차수 K >= 2 의 Lagrange 로 기계정밀.  양수성도 구조적으로 따라온다.
//!
//! 경계는 자르지 않고 **해석 확장**:
//!   저에너지  ln f ~ linear in ln p   (Rayleigh-Jeans / 멱법칙)
//!   고에너지  ln f ~ linear in p      (Wien  f ~ e^{-p/T})
//! => 인공 경계가 없다 (계획 §Q4).

#[derive(Clone, Debug)]
pub struct RadialGrid {
    pub ln_p: Vec<f64>,
    pub dlnp: f64,
}

impl RadialGrid {
    /// [ln p_min, ln p_max] 균일 n 노드.
    pub fn new(lnp_min: f64, lnp_max: f64, n: usize) -> Self {
        assert!(n >= 2);
        let d = (lnp_max - lnp_min) / (n as f64 - 1.0);
        RadialGrid {
            ln_p: (0..n).map(|i| lnp_min + d * i as f64).collect(),
            dlnp: d,
        }
    }
    pub fn len(&self) -> usize {
        self.ln_p.len()
    }
    pub fn p(&self) -> Vec<f64> {
        self.ln_p.iter().map(|x| x.exp()).collect()
    }
}

/// 균일격자 시프트 스텐실.  f_new[i] = f_old(ln p_i - dln).
/// 반환 (offsets: 길이 K, weights: 길이 K) — **i 에 무관** (균일격자의 선물).
pub fn shift_stencil(g: &RadialGrid, dln: f64, order: usize) -> (Vec<i64>, Vec<f64>) {
    let k = order.max(2);
    let s = dln / g.dlnp; // 셀 단위 시프트
    let base = (-s).floor();
    let frac = -s - base; // [0,1)
                          // 중심 대칭 스텐실: base + j0 .. base + j0 + K - 1
    let j0 = -((k as i64) / 2 - 1);
    let offs: Vec<i64> = (0..k as i64).map(|j| base as i64 + j0 + j).collect();
    // Lagrange 가중 (노드 좌표 = offs - base, 목표 = frac)
    let xs: Vec<f64> = (0..k as i64).map(|j| (j0 + j) as f64).collect();
    let mut w = vec![0.0; k];
    for a in 0..k {
        let mut num = 1.0;
        for b in 0..k {
            if a != b {
                num *= (frac - xs[b]) / (xs[a] - xs[b]);
            }
        }
        w[a] = num;
    }
    (offs, w)
}

/// 고에너지 꼬리의 **명시적 모형** — 숨은 가정 금지 (계약 §3).
///   `Wien`     : ln f 가 p 에 선형 (열적 스펙트럼 f ~ e^{-p/T})
///   `PowerLaw` : ln f 가 ln p 에 선형 (비열적 멱법칙)
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Tail {
    Wien,
    PowerLaw,
}

/// 격자 밖 값의 **해석 확장** (인공 경계 없음).  로그값 반환.
/// 저에너지 쪽은 항상 멱법칙 (Rayleigh-Jeans 포함), 고에너지는 `tail` 이 정한다.
#[inline]
fn lnf_extend(lnf: &[f64], p: &[f64], i: i64, tail: Tail) -> f64 {
    let n = lnf.len() as i64;
    if i >= 0 && i < n {
        return lnf[i as usize];
    }
    let dl = p[1].ln() - p[0].ln();
    if i < 0 {
        // 멱법칙: ln f = ln f0 + k (ln p - ln p0)
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
                let m = (lnf[last] - lnf[last - 1]) / (p[last] - p[last - 1]);
                let pout = (p[last].ln() + dl * (i - (n - 1)) as f64).exp();
                lnf[last] + m * (pout - p[last])
            }
        }
    }
}

/// ln f 위에서의 시프트 (★ 기본 경로 — 멱법칙 정확, 양수성 구조적).
pub fn apply_shift_log(
    g: &RadialGrid,
    lnf: &[f64],
    st: &(Vec<i64>, Vec<f64>),
    tail: Tail,
) -> Vec<f64> {
    let n = lnf.len();
    let p = g.p();
    let mut out = vec![0.0; n];
    for (i, out_i) in out.iter_mut().enumerate() {
        let mut v = 0.0;
        for (o, w) in st.0.iter().zip(st.1.iter()) {
            v += w * lnf_extend(lnf, &p, i as i64 + o, tail);
        }
        *out_i = v;
    }
    out
}

/// 선형 f 위에서의 시프트 (비교군 — 수렴차수 비교용).
pub fn apply_shift_linear(
    g: &RadialGrid,
    f: &[f64],
    st: &(Vec<i64>, Vec<f64>),
    tail: Tail,
) -> Vec<f64> {
    let n = f.len();
    let lnf: Vec<f64> = f.iter().map(|x| x.max(1e-300).ln()).collect();
    let p = g.p();
    let mut out = vec![0.0; n];
    for (i, out_i) in out.iter_mut().enumerate() {
        let mut v = 0.0;
        for (o, w) in st.0.iter().zip(st.1.iter()) {
            let j = i as i64 + o;
            let val = if j >= 0 && j < n as i64 {
                f[j as usize]
            } else {
                lnf_extend(&lnf, &p, j, tail).exp()
            };
            v += w * val;
        }
        *out_i = v;
    }
    out
}

/// 꼬리 적합 (저에너지 멱지수, 고에너지 온도).
pub fn tail_fit(g: &RadialGrid, f: &[f64]) -> (f64, f64) {
    let n = f.len();
    let p = g.p();
    let lnf: Vec<f64> = f.iter().map(|x| x.max(1e-300).ln()).collect();
    let k = (lnf[1] - lnf[0]) / (p[1].ln() - p[0].ln());
    let m = (lnf[n - 1] - lnf[n - 2]) / (p[n - 1] - p[n - 2]);
    (k, if m < 0.0 { -1.0 / m } else { f64::INFINITY })
}

/// 에너지 모멘트 int f p^k dp/p  (균일 ln p 라 사다리꼴이 지수적으로 정확).
pub fn moment(g: &RadialGrid, f: &[f64], k: i32) -> f64 {
    let p = g.p();
    let n = f.len();
    let mut s = 0.0;
    for i in 0..n {
        let wt = if i == 0 || i == n - 1 { 0.5 } else { 1.0 };
        s += wt * f[i] * p[i].powi(k);
    }
    s * g.dlnp
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn power_law_shift_is_exact_in_log_space() {
        let g = RadialGrid::new(-6.0, 6.0, 96);
        let kpow = -2.5;
        let lnf: Vec<f64> = g.ln_p.iter().map(|l| kpow * l).collect();
        for dln in [0.31, -0.77, 2.4] {
            let st = shift_stencil(&g, dln, 8);
            let got = apply_shift_log(&g, &lnf, &st, Tail::PowerLaw);
            let want: Vec<f64> = g.ln_p.iter().map(|l| kpow * (l - dln)).collect();
            let e = got
                .iter()
                .zip(&want)
                .map(|(a, b)| (a - b).abs())
                .fold(0.0f64, f64::max);
            assert!(e < 1e-11, "dln={dln} err={e}");
        }
    }

    #[test]
    fn stencil_weights_sum_to_one() {
        let g = RadialGrid::new(-4.0, 4.0, 64);
        for dln in [0.0, 0.13, -1.9, 5.5] {
            let (_, w) = shift_stencil(&g, dln, 8);
            let s: f64 = w.iter().sum();
            assert!((s - 1.0).abs() < 1e-12, "{s}");
        }
    }

    #[test]
    fn planck_shift_converges_at_high_order() {
        let dln = 0.23_f64;
        let mut errs = vec![];
        for n in [48usize, 96, 192, 384] {
            let g = RadialGrid::new(-5.0, 5.0, n);
            let lnf: Vec<f64> = g
                .ln_p
                .iter()
                .map(|l| {
                    let p = l.exp();
                    (1.0 / (p.exp() - 1.0)).ln()
                })
                .collect();
            let st = shift_stencil(&g, dln, 8);
            let got = apply_shift_log(&g, &lnf, &st, Tail::Wien);
            let want: Vec<f64> = g
                .ln_p
                .iter()
                .map(|l| {
                    let p = (l - dln).exp();
                    (1.0 / (p.exp() - 1.0)).ln()
                })
                .collect();
            // 경계 스텐실 폭 밖의 내부만 (외삽은 별도 게이트)
            let k = 8;
            let e = (k..n - k)
                .map(|i| (got[i] - want[i]).abs())
                .fold(0.0f64, f64::max);
            errs.push(e);
        }
        let orders: Vec<f64> = (0..errs.len() - 1)
            .map(|i| (errs[i] / errs[i + 1]).log2())
            .collect();
        assert!(orders[0] > 6.0, "orders {orders:?} errs {errs:?}");
    }
}
