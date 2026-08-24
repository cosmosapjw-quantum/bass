//! R5b · **tilted 계층 전체를 Rust 로** — 식(12) 좌변 + 질량행렬 + RK4 루프를 한 호출로.
//!
//! R5a 가 텐서층만 옮겨 1.32배에 그친 이유는 (l,i) 조합마다 FFI 를 넘나들었기
//! 때문이었다.  여기서는 **루프 전체가 Rust 안에** 있고 J 가 Python 으로 돌아오지 않는다.
//!
//! ★ Python 에서 받아 쓰는 것 (다시 구현하지 않는다):
//!   · 시각별 기하 (사틀·접속·운동학) — `tilted._geometry` 는 sympy 로 만든 닫힌형이라
//!     포트 표면을 넓힐 이유가 없다.  RK4 가 쓰는 **스텝당 3 개** 시각을 미리 받는다
//!     (t, t+dt/2, t+dt — Python 이 쓰는 것과 **같은 부동소수 인자**로).
//!   · PSTF 사영 연산자 Q_l 과 PSTF 정규직교기저 B_l — **Python 것을 그대로** 받는다.
//!     기저는 SVD 라 구현마다 달라질 수 있는데, 같은 기저를 쓰면 질량행렬 좌표까지
//!     같아진다.
//!
//! ★ 부동소수 결합순서를 Python 과 **항별로 맞췄다** (H 항의 괄호, (D) 항의 항별 PSTF
//!   등).  선형해만 LAPACK `dgesv` 대신 여기의 부분추축 LU 다 — 그래서 비트-정확은
//!   기대하지 않는다 (R5a 와 다른 점).  대신 F 와 M 을 따로 노출해 **어디까지 정확히
//!   같은지** 시험이 가려낸다.
//!
//! ★ 범위: 기본 경로(`mode="ratio"`, `jdot_closure=true`, `n_star=None`)만 포트했다.
//!   다른 닫힘 모드는 Python 폴백 — 측정 결과가 전부 기본 경로에 걸려 있기 때문이다.

use crate::kinetic::tilted_terms::{self as tt, Geo};

/// `tilted_closure._TINY` 와 같은 값 (0 나눗셈 가드).
const TINY: f64 = 1e-300;

/// 시각 하나의 기하 (텐서층 + 계층식이 쓰는 운동학).
#[derive(Clone, Debug)]
pub struct HGeo {
    pub base: Geo,
    pub h: f64,
    pub sigma: [f64; 9],
    pub omega: [f64; 9],
    pub udot: [f64; 3],
    pub gamma: f64,
    pub v: [f64; 3],
}

impl HGeo {
    /// γ 와 v 는 **기하에서 되읽는다** (`tilted_mass.gamma_and_v`): 순수 boost 사틀에서
    /// E_A^t = γ v_A 이므로 인자와 기하가 어긋날 여지가 없다.
    pub fn finish(mut self) -> Self {
        self.gamma = self.base.uup[0];
        for a in 0..3 {
            self.v[a] = self.base.eup[a * 4] / self.gamma;
        }
        self
    }
}

/// 부호 규약 (`tilted.SIGNS`).
#[derive(Clone, Copy, Debug)]
pub struct Signs {
    pub a: f64,
    pub b: f64,
    pub c: f64,
    pub d: f64,
    pub e: f64,
    pub omega: f64,
    pub divcon: f64,
    pub divfree: f64,
}

impl Default for Signs {
    fn default() -> Self {
        Signs {
            a: 1.0,
            b: -1.0,
            c: -1.0,
            d: 1.0,
            e: -1.0,
            omega: 1.0,
            divcon: 1.0,
            divfree: -1.0,
        }
    }
}

/// (l, i) 격자.  i 는 −1 … i_max+2, l 은 0 … l_max+2.
#[derive(Clone)]
pub struct Grid {
    pub l_max: usize,
    pub i_max: usize,
    pub blocks: Vec<Vec<f64>>,
}

#[inline]
fn dim(l: usize) -> usize {
    3usize.pow(l as u32)
}

impl Grid {
    pub fn new(l_max: usize, i_max: usize) -> Self {
        let nl = l_max + 3;
        let ni = i_max + 4; // i = −1 … i_max+2
        let mut blocks = Vec::with_capacity(nl * ni);
        for l in 0..nl {
            for _ in 0..ni {
                blocks.push(vec![0.0; dim(l)]);
            }
        }
        Grid {
            l_max,
            i_max,
            blocks,
        }
    }
    #[inline]
    fn idx(&self, l: usize, i: i32) -> usize {
        l * (self.i_max + 4) + (i + 1) as usize
    }
    #[inline]
    pub fn get(&self, l: usize, i: i32) -> &[f64] {
        &self.blocks[self.idx(l, i)]
    }
    #[inline]
    pub fn set(&mut self, l: usize, i: i32, v: Vec<f64>) {
        let k = self.idx(l, i);
        self.blocks[k] = v;
    }
    /// 상태 블록만 (l ≤ l_max, 0 ≤ i ≤ i_max) 평탄화 — Python 배치와 같은 순서.
    pub fn flatten_state(&self, out: &mut Vec<f64>) {
        for l in 0..=self.l_max {
            for i in 0..=(self.i_max as i32) {
                out.extend_from_slice(self.get(l, i));
            }
        }
    }
    pub fn from_state(l_max: usize, i_max: usize, flat: &[f64]) -> Self {
        let mut g = Grid::new(l_max, i_max);
        let mut p = 0usize;
        for l in 0..=l_max {
            let d = dim(l);
            for i in 0..=(i_max as i32) {
                g.set(l, i, flat[p..p + d].to_vec());
                p += d;
            }
        }
        g
    }
    pub fn state_len(l_max: usize, i_max: usize) -> usize {
        (0..=l_max).map(|l| dim(l) * (i_max + 1)).sum()
    }
}

// ═══════════════════════════════════════ 작은 텐서 연산 (hierarchy.py 미러)
/// (J·σ)_{A_{l−1} b} = J_{a A_{l−1}} σ_{b a}  — rank l → rank l.
fn contract_one(j: &[f64], l: usize, sig: &[f64; 9]) -> Vec<f64> {
    let rest = dim(l - 1);
    let mut out = vec![0.0; rest * 3];
    for a in 0..3 {
        for r in 0..rest {
            let x = j[a * rest + r];
            if x == 0.0 {
                continue;
            }
            for b in 0..3 {
                out[r * 3 + b] += x * sig[b * 3 + a];
            }
        }
    }
    out
}

/// J_{ab A_l} σ^{ab} — rank l+2 → rank l.
fn contract_two(j: &[f64], l_out: usize, sig: &[f64; 9]) -> Vec<f64> {
    let rest = dim(l_out);
    let mut out = vec![0.0; rest];
    for a in 0..3 {
        for b in 0..3 {
            let s = sig[a * 3 + b];
            if s == 0.0 {
                continue;
            }
            let base = (a * 3 + b) * rest;
            for r in 0..rest {
                out[r] += s * j[base + r];
            }
        }
    }
    out
}

/// J_{A_{l−2}} ⊗ σ  (PSTF 는 호출자가 적용).
fn outer_sigma(j: &[f64], sig: &[f64; 9]) -> Vec<f64> {
    let mut out = vec![0.0; j.len() * 9];
    for (r, &x) in j.iter().enumerate() {
        for k in 0..9 {
            out[r * 9 + k] = x * sig[k];
        }
    }
    out
}

/// J_{a A_l} w^a — 첫 지표를 벡터와 축약 (rank r → r−1).
fn contract_vec_first(j: &[f64], r: usize, w: &[f64; 3]) -> Vec<f64> {
    let rest = dim(r - 1);
    let mut out = vec![0.0; rest];
    for a in 0..3 {
        if w[a] == 0.0 {
            continue;
        }
        for k in 0..rest {
            out[k] += j[a * rest + k] * w[a];
        }
    }
    out
}

/// J_{A_{l−1}} ⊗ w  (PSTF 는 호출자가 적용).
fn outer_vec_last(j: &[f64], w: &[f64; 3]) -> Vec<f64> {
    let mut out = vec![0.0; j.len() * 3];
    for (r, &x) in j.iter().enumerate() {
        for a in 0..3 {
            out[r * 3 + a] = x * w[a];
        }
    }
    out
}

#[inline]
fn axpy(dst: &mut [f64], c: f64, src: &[f64]) {
    for (d, s) in dst.iter_mut().zip(src.iter()) {
        *d += c * *s;
    }
}

/// PSTF 사영 — Python 이 준 고정 연산자 Q_l (3^l × 3^l) 을 쓴다 (R3 의 `pstf_operator`).
fn pstf(x: &[f64], l: usize, ops: &[Vec<f64>]) -> Vec<f64> {
    if l < 2 {
        return x.to_vec();
    }
    let n = dim(l);
    let q = &ops[l];
    let mut out = vec![0.0; n];
    for r in 0..n {
        let mut acc = 0.0;
        let row = &q[r * n..(r + 1) * n];
        for c in 0..n {
            acc += row[c] * x[c];
        }
        out[r] = acc;
    }
    out
}

// ═══════════════════════════════════════ ★★ 식 (12) 좌변
#[allow(clippy::too_many_arguments)]
pub fn equation_lhs(
    j: &Grid,
    dj: &Grid,
    g: &HGeo,
    l: usize,
    i: i32,
    s: &Signs,
    ops: &[Vec<f64>],
) -> Vec<f64> {
    let lf = l as f64;
    let n = lf + 2.0 * i as f64;
    let d = dim(l);
    // ⊥J̇ (사틀 회전항 포함)
    let mut out = tt::perp_dot(j.get(l, i), dj.get(l, i), l, &g.base);
    // H 항 — Python 은 H·((3+n)J + (1−n)J′) 로 **묶어서** 곱한다.
    {
        let (ja, jb) = (j.get(l, i), j.get(l, i + 1));
        for k in 0..d {
            out[k] += g.h * ((3.0 + n) * ja[k] + (1.0 - n) * jb[k]);
        }
    }
    // (div-con)  D^a J^(i)_{a A_l}
    let dc = tt::div_contracted(j.get(l + 1, i), dj.get(l + 1, i), l + 1, &g.base);
    axpy(&mut out, s.divcon, &dc);
    if l >= 1 {
        // (div-free)  −(l/(2l+1)) D_{⟨a_l} J^(i+1)_{A_{l−1}⟩}
        let raw = tt::div_free_raw(j.get(l - 1, i + 1), dj.get(l - 1, i + 1), l - 1, &g.base);
        let df = pstf(&raw, l, ops);
        axpy(&mut out, s.divfree * (-lf / (2.0 * lf + 1.0)), &df);
        // (Ω)  −l J^(i)_{a⟨A_{l−1}} ω_{a_l⟩}{}^a
        let to = pstf(&contract_one(j.get(l, i), l, &g.omega), l, ops);
        axpy(&mut out, s.omega * -lf, &to);
        // (D)  (l/(2l+1))[(l+n+1)J^(i) + (2−n)J^(i+1)]_{⟨A_{l−1}} u̇_{a_l⟩}
        //      ★ Python 의 `_outer_vec_last` 는 **항마다** PSTF 한다 — 그대로 맞춘다.
        let mut td = vec![0.0; d];
        axpy(
            &mut td,
            lf + n + 1.0,
            &pstf(&outer_vec_last(j.get(l - 1, i), &g.udot), l, ops),
        );
        axpy(
            &mut td,
            2.0 - n,
            &pstf(&outer_vec_last(j.get(l - 1, i + 1), &g.udot), l, ops),
        );
        axpy(&mut out, s.d * (lf / (2.0 * lf + 1.0)), &td);
        // (A)  (l/(2l+3))[(2n+3)J^(i) + (2−2n)J^(i+1)]_{a⟨A_{l−1}} σ_{a_l⟩}{}^a
        let mut ta = vec![0.0; d];
        axpy(
            &mut ta,
            2.0 * n + 3.0,
            &contract_one(j.get(l, i), l, &g.sigma),
        );
        axpy(
            &mut ta,
            2.0 - 2.0 * n,
            &contract_one(j.get(l, i + 1), l, &g.sigma),
        );
        let ta = pstf(&ta, l, ops);
        axpy(&mut out, s.a * (lf / (2.0 * lf + 3.0)), &ta);
    }
    // (E)  [(l−n)J^(i−1) + (n−2)J^(i)]_{a A_l} u̇^a       ★ (l−n) = −2i
    let mut te = vec![0.0; d];
    axpy(
        &mut te,
        n - 2.0,
        &contract_vec_first(j.get(l + 1, i), l + 1, &g.udot),
    );
    if (lf - n) != 0.0 {
        axpy(
            &mut te,
            lf - n,
            &contract_vec_first(j.get(l + 1, i - 1), l + 1, &g.udot),
        );
    }
    axpy(&mut out, s.e, &te);
    // (B)  [(l−n)J^(i−1) + (n−1)J^(i)]_{ab A_l} σ^{ab}
    let mut tb = vec![0.0; d];
    axpy(
        &mut tb,
        n - 1.0,
        &contract_two(j.get(l + 2, i), l, &g.sigma),
    );
    if (lf - n) != 0.0 {
        axpy(
            &mut tb,
            lf - n,
            &contract_two(j.get(l + 2, i - 1), l, &g.sigma),
        );
    }
    axpy(&mut out, s.b, &tb);
    // (C)  (l(l−1)/(4l²−1))[(n−1)J^(i+2) − (l+n+1)J^(i+1)]_{⟨A_{l−2}} σ_{a_{l−1}a_l⟩}
    if l >= 2 {
        let cc = lf * (lf - 1.0) / (4.0 * lf * lf - 1.0);
        let mut tc = vec![0.0; d];
        axpy(
            &mut tc,
            n - 1.0,
            &pstf(&outer_sigma(j.get(l - 2, i + 2), &g.sigma), l, ops),
        );
        axpy(
            &mut tc,
            -(lf + n + 1.0),
            &pstf(&outer_sigma(j.get(l - 2, i + 1), &g.sigma), l, ops),
        );
        axpy(&mut out, s.c * cc, &tc);
    }
    if l >= 2 {
        pstf(&out, l, ops)
    } else {
        out
    }
}

// ═══════════════════════════════════════ 닫힘 (`tilted_closure` 전 모드)
/// `tilted_closure.MODES` 와 짝 — Python 이 코드로 넘긴다.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Mode {
    Frozen,
    Ratio,
    RatioScalar,
    Zero,
    PhysSqrt,
    Phys5w,
    PhysInterp,
}

impl Mode {
    pub fn from_code(c: usize) -> Option<Mode> {
        Some(match c {
            0 => Mode::Frozen,
            1 => Mode::Ratio,
            2 => Mode::RatioScalar,
            3 => Mode::Zero,
            4 => Mode::PhysSqrt,
            5 => Mode::Phys5w,
            6 => Mode::PhysInterp,
            _ => return None,
        })
    }
    fn is_phys(self) -> bool {
        matches!(self, Mode::PhysSqrt | Mode::Phys5w | Mode::PhysInterp)
    }
}

/// 절단·닫힘 설정 한 묶음.
#[derive(Clone, Copy, Debug)]
pub struct Closure {
    pub mode: Mode,
    pub jdot: bool,
    /// 삼각 절단 l + 2i ≤ n_*  (없으면 `None` → 직사각 절단).
    pub n_star: Option<i32>,
}

impl Closure {
    #[inline]
    pub fn keeps(&self, l: usize, i: i32) -> bool {
        match self.n_star {
            None => true,
            Some(ns) => l as i32 + 2 * i <= ns,
        }
    }
}

fn safe_ratio(a: &[f64], b: &[f64]) -> Vec<f64> {
    a.iter()
        .zip(b.iter())
        .map(|(&x, &y)| {
            if y.abs() > TINY {
                (x / y).clamp(-1.0, 1.0)
            } else {
                0.0
            }
        })
        .collect()
}

/// 노름 기반 **스칼라** 비 (`tilted_closure._norm_ratio`).
fn norm_ratio(a: &[f64], b: &[f64]) -> f64 {
    let na = a.iter().fold(0.0f64, |m, x| m.max(x.abs()));
    let nb = b.iter().fold(0.0f64, |m, x| m.max(x.abs()));
    if nb <= TINY {
        0.0
    } else {
        (na / nb).clamp(0.0, 1.0)
    }
}

/// (1−r) 기하외삽의 한 성분 — `tilted_closure.predict(mode="ratio")` 그대로.
#[inline]
fn ratio_ra_rb(r1: f64, r0: f64) -> (f64, f64) {
    let (d1, d0) = (1.0 - r1, 1.0 - r0);
    let rho = if d0.abs() > 1e-14 {
        (d1 / d0).clamp(0.0, 1.0)
    } else {
        1.0
    };
    (
        (1.0 - rho * d1).clamp(-1.0, 1.0),
        (1.0 - rho * rho * d1).clamp(-1.0, 1.0),
    )
}

/// 상태에서 w = p/ρ = J^(1)_{l=0} / (3 J^(0)_{l=0}).
fn w_from_state(j: &Grid) -> f64 {
    let rho = j.get(0, 0)[0];
    let j1 = j.get(0, 1)[0];
    if rho.abs() > TINY {
        j1 / (3.0 * rho)
    } else {
        0.0
    }
}

/// 문헌 처방의 비 (`tilted_closure.physical_ratio`).
fn physical_ratio(w: f64, mode: Mode) -> f64 {
    let t = (3.0 * w).max(0.0);
    match mode {
        Mode::PhysSqrt => t.sqrt(),
        Mode::Phys5w => 5.0 * w,
        Mode::PhysInterp => {
            if t <= 0.0 {
                0.0
            } else {
                (5.0f64 / 3.0).powf(1.0 - t) * t.powf((2.0 - t) / 2.0)
            }
        }
        _ => unreachable!(),
    }
}

/// (l, i_max+1), (l, i_max+2) 를 채운다 — `tilted_closure.predict` 의 분기 순서 그대로.
fn close_i(j: &mut Grid, l: usize, c: Closure) {
    let im = j.i_max as i32;
    // ★ Python 은 `predict` 안에서 매번 w 를 다시 읽는다 — 그 시점을 그대로 맞춘다.
    let phys_r = if c.mode.is_phys() {
        physical_ratio(w_from_state(j), c.mode)
    } else {
        0.0
    };
    let a = j.get(l, im).to_vec();
    let d = a.len();
    let (mut n1, mut n2) = (vec![0.0; d], vec![0.0; d]);
    if c.mode == Mode::Zero {
        j.set(l, im + 1, n1);
        j.set(l, im + 2, n2);
        return;
    }
    if c.mode.is_phys() {
        for k in 0..d {
            n1[k] = a[k] * phys_r;
            n2[k] = n1[k] * phys_r;
        }
    } else if c.mode == Mode::Frozen || j.i_max < 2 {
        let r = safe_ratio(&a, j.get(l, im - 1));
        for k in 0..d {
            n1[k] = a[k] * r[k];
            n2[k] = n1[k] * r[k];
        }
    } else {
        let (r1, r0) = if c.mode == Mode::RatioScalar {
            (
                vec![norm_ratio(&a, j.get(l, im - 1)); d],
                vec![norm_ratio(j.get(l, im - 1), j.get(l, im - 2)); d],
            )
        } else {
            (
                safe_ratio(&a, j.get(l, im - 1)),
                safe_ratio(j.get(l, im - 1), j.get(l, im - 2)),
            )
        };
        for k in 0..d {
            let (ra, rb) = ratio_ra_rb(r1[k], r0[k]);
            n1[k] = a[k] * ra;
            n2[k] = n1[k] * rb;
        }
    }
    j.set(l, im + 1, n1);
    j.set(l, im + 2, n2);
}

/// J̇ 닫힘에 쓸 비 r_l (`tilted_closure.jdot_ratio`).
///
/// ★ "ratio_scalar" 는 `predict` 와 달리 (1−r) 외삽을 **하지 않는다** — Python 이
///   그렇게 되어 있고, 그 비대칭을 여기서 그대로 옮긴다 (고치면 대조군이 달라진다).
fn jdot_ratio(j: &Grid, c: Closure) -> Vec<Vec<f64>> {
    let im = j.i_max as i32;
    let phys_r = if c.mode.is_phys() {
        physical_ratio(w_from_state(j), c.mode)
    } else {
        0.0
    };
    (0..=j.l_max)
        .map(|l| {
            let d = dim(l);
            if c.mode == Mode::Zero {
                return vec![0.0; d];
            }
            if c.mode.is_phys() {
                return vec![phys_r; d];
            }
            if c.mode == Mode::Frozen || j.i_max < 2 {
                return safe_ratio(j.get(l, im), j.get(l, im - 1));
            }
            if c.mode == Mode::RatioScalar {
                return vec![norm_ratio(j.get(l, im), j.get(l, im - 1)); d];
            }
            let r1 = safe_ratio(j.get(l, im), j.get(l, im - 1));
            let r0 = safe_ratio(j.get(l, im - 1), j.get(l, im - 2));
            r1.iter()
                .zip(r0.iter())
                .map(|(&x1, &x0)| ratio_ra_rb(x1, x0).0)
                .collect()
        })
        .collect()
}

/// 격자를 방정식이 요구하는 이웃까지 채운다 (l 위쪽은 0 절단).
fn closure(j: &Grid, c: Closure) -> Grid {
    if c.n_star.is_some() {
        // ★ L1 삼각 절단: 상태 블록만 남기고 나머지는 전부 0.
        let mut out = Grid::new(j.l_max, j.i_max);
        for l in 0..=j.l_max {
            for i in 0..=(j.i_max as i32) {
                if c.keeps(l, i) {
                    out.set(l, i, j.get(l, i).to_vec());
                }
            }
        }
        return out;
    }
    let mut out = j.clone();
    for l in 0..=j.l_max {
        close_i(&mut out, l, c);
    }
    for l in [j.l_max + 1, j.l_max + 2] {
        for i in -1..=(j.i_max as i32 + 2) {
            out.set(l, i, vec![0.0; dim(l)]);
        }
    }
    out
}

// ═══════════════════════════════════════ 질량행렬 (PSTF 좌표)
/// M·J̇ 의 **한 블록 소스**가 낳는 (목표블록, 값) 들 — `tilted_mass.matvec` 의 포트.
///
/// ★ R5b 성능의 핵심: 소스 블록 하나는 목표를 **최대 셋**만 건드린다
/// (대각 / (div-con) l₀−1 / (div-free) l₀+1).  옛 판은 단위벡터마다 전 블록을 훑어
/// 빈 블록에도 PSTF 를 때렸다 — l_max=3, i_max=3 에서 열당 16 블록 × 64 열이었다.
/// 값은 그대로다 (건너뛴 블록은 pstf(0) = 0).
fn matvec_column(
    src_l: usize,
    src_i: i32,
    src: &[f64],
    g: &HGeo,
    s: &Signs,
    ir: Option<&[Vec<f64>]>,
    ops: &[Vec<f64>],
    l_max: usize,
    i_max: usize,
    mut emit: impl FnMut(usize, i32, Vec<f64>),
) {
    // 대각 (l₀, i₀) ← (l₀, i₀):  γ·P
    {
        let mut acc = vec![0.0; src.len()];
        axpy(&mut acc, g.gamma, src);
        emit(src_l, src_i, pstf(&acc, src_l, ops));
    }
    // (div-con)  (l₀−1, i₀) ← (l₀, i₀)
    if src_l >= 1 && src_l <= l_max {
        let l = src_l - 1;
        let mut acc = vec![0.0; dim(l)];
        let c = contract_vec_first(src, src_l, &g.v);
        axpy(&mut acc, s.divcon * g.gamma, &c);
        emit(l, src_i, pstf(&acc, l, ops));
    }
    // (div-free)  (l₀+1, i₀−1) ← (l₀, i₀)   그리고 i₀ = i_max 의 비-닫힘 갈래
    if src_l + 1 <= l_max {
        let l = src_l + 1;
        let lf = l as f64;
        let coef = s.divfree * (-lf / (2.0 * lf + 1.0)) * g.gamma;
        let mut targets: Vec<(i32, Vec<f64>)> = Vec::with_capacity(2);
        if src_i >= 1 {
            targets.push((src_i - 1, src.to_vec()));
        }
        if src_i == i_max as i32 {
            if let Some(rs) = ir {
                // J̇ 닫힘이 켜졌을 때만
                let r = &rs[src_l];
                targets.push((
                    i_max as i32,
                    src.iter().zip(r.iter()).map(|(&x, &y)| y * x).collect(),
                ));
            }
        }
        for (i, sv) in targets {
            let mut acc = vec![0.0; dim(l)];
            let t = pstf(&outer_vec_last(&sv, &g.v), l, ops);
            axpy(&mut acc, coef, &t);
            emit(l, i, pstf(&acc, l, ops));
        }
    }
}

/// 상태벡터 배치 (**PSTF 좌표**, 블록 크기 2l+1) — `tilted_mass.layout` 의 포트.
fn layout(l_max: usize, i_max: usize, c: Closure) -> (Vec<(usize, i32)>, Vec<usize>, usize) {
    let (mut keys, mut off, mut n) = (vec![], vec![], 0usize);
    for l in 0..=l_max {
        for i in 0..=(i_max as i32) {
            if !c.keeps(l, i) {
                continue;
            }
            keys.push((l, i));
            off.push(n);
            n += 2 * l + 1;
        }
    }
    (keys, off, n)
}

/// 텐서 → PSTF 좌표.  기저 B_l 은 Python 것 (행우선 (3^l, 2l+1)).
fn to_coef(x: &[f64], l: usize, bases: &[Vec<f64>]) -> Vec<f64> {
    let k = 2 * l + 1;
    let n = dim(l);
    let b = &bases[l];
    (0..k)
        .map(|c| (0..n).map(|r| b[r * k + c] * x[r]).sum())
        .collect()
}

fn to_tensor(c: &[f64], l: usize, bases: &[Vec<f64>]) -> Vec<f64> {
    let k = 2 * l + 1;
    let n = dim(l);
    let b = &bases[l];
    (0..n)
        .map(|r| (0..k).map(|j| b[r * k + j] * c[j]).sum())
        .collect()
}

/// 부분추축 LU (LAPACK `dgetf2` 와 같은 우향 알고리듬) — 제자리 분해 후 전·후치환.
///
/// ★ 자체 구현인 이유: 의존성이 아니라 **결정성** 때문이다.  BLAS 는 블록 크기와 FMA
///   사용이 빌드마다 달라 같은 기계에서도 재현이 보장되지 않는다.
fn lu_solve(mut a: Vec<f64>, mut b: Vec<f64>, n: usize) -> Vec<f64> {
    for k in 0..n {
        let (mut p, mut best) = (k, a[k * n + k].abs());
        for r in (k + 1)..n {
            let v = a[r * n + k].abs();
            if v > best {
                best = v;
                p = r;
            }
        }
        if best == 0.0 {
            return vec![f64::NAN; n];
        }
        if p != k {
            for c in 0..n {
                a.swap(k * n + c, p * n + c);
            }
            b.swap(k, p);
        }
        let piv = a[k * n + k];
        for r in (k + 1)..n {
            let f = a[r * n + k] / piv;
            a[r * n + k] = f;
            if f == 0.0 {
                continue;
            }
            for c in (k + 1)..n {
                a[r * n + c] -= f * a[k * n + c];
            }
            b[r] -= f * b[k];
        }
    }
    for k in (0..n).rev() {
        let mut acc = b[k];
        for c in (k + 1)..n {
            acc -= a[k * n + c] * b[c];
        }
        b[k] = acc / a[k * n + k];
    }
    b
}

/// M·J̇ = F 를 PSTF 좌표에서 푼다.  `mat_out` 이 있으면 조립한 M 을 복사해 둔다.
#[allow(clippy::too_many_arguments)]
fn solve(
    f: &Grid,
    g: &HGeo,
    s: &Signs,
    ir: Option<&[Vec<f64>]>,
    ops: &[Vec<f64>],
    bases: &[Vec<f64>],
    l_max: usize,
    i_max: usize,
    c: Closure,
    mat_out: Option<&mut Vec<f64>>,
) -> Grid {
    let (keys, off, n) = layout(l_max, i_max, c);
    let mut block_of = vec![usize::MAX; (l_max + 1) * (i_max + 1)];
    for (bj, &(l, i)) in keys.iter().enumerate() {
        block_of[l * (i_max + 1) + i as usize] = bj;
    }
    let mut m = vec![0.0f64; n * n];
    for (bi, &(l0, i0)) in keys.iter().enumerate() {
        let k0 = 2 * l0 + 1;
        for jcol in 0..k0 {
            let mut unit = vec![0.0; k0];
            unit[jcol] = 1.0;
            let src = to_tensor(&unit, l0, bases);
            matvec_column(l0, i0, &src, g, s, ir, ops, l_max, i_max, |l1, i1, val| {
                let bj = block_of[l1 * (i_max + 1) + i1 as usize];
                if bj == usize::MAX {
                    return;
                } // 절단 밖 목표
                let cf = to_coef(&val, l1, bases);
                for (t, &v) in cf.iter().enumerate() {
                    m[(off[bj] + t) * n + off[bi] + jcol] = v;
                }
            });
        }
    }
    let mut rhs = vec![0.0f64; n];
    for (bj, &(l1, i1)) in keys.iter().enumerate() {
        let c = to_coef(f.get(l1, i1), l1, bases);
        for (t, &val) in c.iter().enumerate() {
            rhs[off[bj] + t] = val;
        }
    }
    if let Some(dst) = mat_out {
        dst.clear();
        dst.extend_from_slice(&m);
    }
    let x = lu_solve(m, rhs, n);
    let mut out = Grid::new(l_max, i_max);
    for (bj, &(l1, i1)) in keys.iter().enumerate() {
        let c: Vec<f64> = (0..2 * l1 + 1).map(|t| x[off[bj] + t]).collect();
        out.set(l1, i1, to_tensor(&c, l1, bases));
    }
    out
}

/// 좌변 F = −LHS(J, 0) — 상태 블록만.
#[allow(clippy::too_many_arguments)]
fn force(
    jc: &Grid,
    g: &HGeo,
    s: &Signs,
    ops: &[Vec<f64>],
    l_max: usize,
    i_max: usize,
    c: Closure,
    zero: &Grid,
) -> Grid {
    let mut f = Grid::new(l_max, i_max);
    for l in 0..=l_max {
        for i in 0..=(i_max as i32) {
            if !c.keeps(l, i) {
                continue;
            }
            let mut v = equation_lhs(jc, zero, g, l, i, s, ops);
            for x in v.iter_mut() {
                *x = -*x;
            }
            f.set(l, i, v);
        }
    }
    f
}

/// ★★ J̇ = M⁻¹F — 한 스텝의 RHS (닫힘 → 좌변 → 선형해).
pub fn rhs(
    j: &Grid,
    g: &HGeo,
    s: &Signs,
    ops: &[Vec<f64>],
    bases: &[Vec<f64>],
    c: Closure,
) -> Grid {
    let (l_max, i_max) = (j.l_max, j.i_max);
    let jc = closure(j, c);
    let zero = Grid::new(l_max, i_max);
    let f = force(&jc, g, s, ops, l_max, i_max, c, &zero);
    let ir = if c.jdot && c.n_star.is_none() {
        Some(jdot_ratio(&jc, c))
    } else {
        None
    };
    solve(&f, g, s, ir.as_deref(), ops, bases, l_max, i_max, c, None)
}

/// 진단용: 한 스텝의 (F, M) 을 그대로 돌려준다 (Python 과 **어디까지 같은지** 가리려고).
pub fn force_and_matrix(
    j: &Grid,
    g: &HGeo,
    s: &Signs,
    ops: &[Vec<f64>],
    bases: &[Vec<f64>],
    c: Closure,
) -> (Vec<f64>, Vec<f64>) {
    let (l_max, i_max) = (j.l_max, j.i_max);
    let jc = closure(j, c);
    let zero = Grid::new(l_max, i_max);
    let f = force(&jc, g, s, ops, l_max, i_max, c, &zero);
    let ir = if c.jdot && c.n_star.is_none() {
        Some(jdot_ratio(&jc, c))
    } else {
        None
    };
    let mut m = Vec::new();
    solve(
        &f,
        g,
        s,
        ir.as_deref(),
        ops,
        bases,
        l_max,
        i_max,
        c,
        Some(&mut m),
    );
    let mut flat = Vec::new();
    f.flatten_state(&mut flat);
    (flat, m)
}

/// ★★ RK4 적분 — J 가 Python 으로 **돌아오지 않는다**.
///
/// `geos` 는 스텝마다 3 개 (t, t+dt/2, t+dt) 로 `3·nsteps` 개.
/// 반환: (nsteps+1) × state_len 평탄 이력.
#[allow(clippy::too_many_arguments)]
pub fn integrate(
    j0: &Grid,
    geos: &[HGeo],
    nsteps: usize,
    dt: f64,
    s: &Signs,
    ops: &[Vec<f64>],
    bases: &[Vec<f64>],
    c: Closure,
) -> Vec<f64> {
    let (l_max, i_max) = (j0.l_max, j0.i_max);
    let mut j = j0.clone();
    let mut hist = Vec::with_capacity((nsteps + 1) * Grid::state_len(l_max, i_max));
    j.flatten_state(&mut hist);
    let axpy_grid = |base: &Grid, d: &Grid, c: f64| -> Grid {
        let mut o = Grid::new(l_max, i_max);
        for l in 0..=l_max {
            for i in 0..=(i_max as i32) {
                let v: Vec<f64> = base
                    .get(l, i)
                    .iter()
                    .zip(d.get(l, i).iter())
                    .map(|(&x, &y)| x + c * y)
                    .collect();
                o.set(l, i, v);
            }
        }
        o
    };
    for step in 0..nsteps {
        let (g0, gh, g1) = (&geos[3 * step], &geos[3 * step + 1], &geos[3 * step + 2]);
        let k1 = rhs(&j, g0, s, ops, bases, c);
        let k2 = rhs(&axpy_grid(&j, &k1, 0.5 * dt), gh, s, ops, bases, c);
        let k3 = rhs(&axpy_grid(&j, &k2, 0.5 * dt), gh, s, ops, bases, c);
        let k4 = rhs(&axpy_grid(&j, &k3, dt), g1, s, ops, bases, c);
        for l in 0..=l_max {
            for i in 0..=(i_max as i32) {
                let (a1, a2, a3, a4) = (k1.get(l, i), k2.get(l, i), k3.get(l, i), k4.get(l, i));
                let cur = j.get(l, i);
                let v: Vec<f64> = (0..dim(l))
                    .map(|t| cur[t] + dt / 6.0 * (a1[t] + 2.0 * a2[t] + 2.0 * a3[t] + a4[t]))
                    .collect();
                j.set(l, i, v);
            }
        }
        j.flatten_state(&mut hist);
    }
    hist
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn grid_indexing_round_trips() {
        let mut g = Grid::new(2, 1);
        g.set(2, 1, vec![7.0; 9]);
        assert_eq!(g.get(2, 1)[0], 7.0);
        assert_eq!(g.get(2, 0)[0], 0.0);
        assert_eq!(g.get(0, -1).len(), 1);
    }

    #[test]
    fn contract_two_matches_a_hand_case() {
        // J_{ab} σ^{ab} 에서 J = σ 면 tr(σ²)
        let sig = [1.0, 0.2, 0.0, 0.2, -0.5, 0.1, 0.0, 0.1, -0.5];
        let out = contract_two(&sig, 0, &sig);
        let want: f64 = sig.iter().map(|x| x * x).sum();
        assert!((out[0] - want).abs() < 1e-13);
    }

    #[test]
    fn safe_ratio_clamps_and_guards_zero() {
        let r = safe_ratio(&[1.0, 5.0, 1.0], &[2.0, 1.0, 0.0]);
        assert!((r[0] - 0.5).abs() < 1e-15);
        assert_eq!(r[1], 1.0);
        assert_eq!(r[2], 0.0);
    }

    #[test]
    fn lu_solve_recovers_a_known_solution() {
        // 추축이 필요한 행렬 (첫 성분이 0) — 부분추축이 실제로 동작하는지.
        let a = vec![0.0, 2.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 3.0];
        let want = [1.0, -2.0, 0.5];
        let mut b = vec![0.0; 3];
        for r in 0..3 {
            b[r] = (0..3).map(|c| a[r * 3 + c] * want[c]).sum();
        }
        let x = lu_solve(a, b, 3);
        for (g, w) in x.iter().zip(want.iter()) {
            assert!((g - w).abs() < 1e-13, "{g} {w}");
        }
    }

    #[test]
    fn state_flattening_round_trips() {
        let mut g = Grid::new(2, 1);
        g.set(1, 1, vec![1.0, 2.0, 3.0]);
        g.set(2, 0, (0..9).map(|k| k as f64).collect());
        let mut flat = Vec::new();
        g.flatten_state(&mut flat);
        assert_eq!(flat.len(), Grid::state_len(2, 1));
        let back = Grid::from_state(2, 1, &flat);
        assert_eq!(back.get(1, 1), &[1.0, 2.0, 3.0]);
        assert_eq!(back.get(2, 0)[8], 8.0);
    }
}
