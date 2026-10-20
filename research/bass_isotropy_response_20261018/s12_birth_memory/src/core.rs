//! S12 full parameter tangent of an immutable, frozen cohort bank.
//!
//! State is [h,b,y,h_theta,b_theta,y_theta]. Event times, birth amplitudes,
//! donor normalization and Lambda have zero parameter derivative in this unit.
//! Only newly created cohorts receive birth-memory companions. Signed derivative
//! entries are not physical weights. No existing weight is normalized or changed.
//!
//! The baseline uses three explicit ray passes; fused uses one prepared-z pass.
//! Both use the same expressions and ordered compensated reductions. No SIMD,
//! approximate state cache, fast-math or tolerance fallback is used.

use std::fmt;

pub const MAX_RAYS: usize = 4096;
pub const MAX_COHORTS: usize = 2048;
pub const MAX_TOTAL_RAYS: usize = 1_048_576;
pub const NORMALIZATION_ATOL: f64 = 3e-15;
pub const DERIVATIVE_NORMALIZATION_ATOL: f64 = 1e-12;

#[derive(Clone, Debug)]
pub struct Error {
    pub code: &'static str,
    pub detail: String,
}

impl Error {
    pub fn new(code: &'static str, detail: impl Into<String>) -> Self {
        Self {
            code,
            detail: detail.into(),
        }
    }
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}: {}", self.code, self.detail)
    }
}
impl std::error::Error for Error {}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Mode {
    Baseline,
    Fused,
}

impl Mode {
    pub fn parse(s: &str) -> Result<Self, Error> {
        match s {
            "baseline" => Ok(Self::Baseline),
            "fused" => Ok(Self::Fused),
            _ => Err(Error::new("MODE_DOMAIN", "expected baseline or fused")),
        }
    }
    pub fn name(self) -> &'static str {
        match self {
            Self::Baseline => "baseline",
            Self::Fused => "fused",
        }
    }
}

#[derive(Clone, Copy, Debug, Default)]
pub struct Sum {
    sum: f64,
    correction: f64,
}

impl Sum {
    #[inline]
    pub fn add(&mut self, x: f64) {
        let t = self.sum + x;
        self.correction += if self.sum.abs() >= x.abs() {
            (self.sum - t) + x
        } else {
            (x - t) + self.sum
        };
        self.sum = t;
    }
    #[inline]
    pub fn value(self) -> f64 {
        self.sum + self.correction
    }
}

pub fn ordered_sum(values: impl IntoIterator<Item = f64>) -> f64 {
    let mut s = Sum::default();
    for x in values {
        s.add(x);
    }
    s.value()
}

#[derive(Clone, Debug)]
pub struct Cohort {
    pub u: f64,
    pub b_birth: f64,
    pub energy_birth: f64,
    /// Frozen B_j; explicit omission controls may supply zero in a new copy.
    pub memory_theta: f64,
    pub mu: Vec<f64>,
    pub alpha: Vec<f64>,
    pub mu_theta: Vec<f64>,
    pub alpha_theta: Vec<f64>,
}

impl Cohort {
    pub fn validate(&self) -> Result<(), Error> {
        let n = self.mu.len();
        if !(2..=MAX_RAYS).contains(&n)
            || [
                self.alpha.len(),
                self.mu_theta.len(),
                self.alpha_theta.len(),
            ]
            .iter()
            .any(|m| *m != n)
            || [self.u, self.b_birth, self.energy_birth, self.memory_theta]
                .iter()
                .any(|v| !v.is_finite())
            || self.energy_birth <= 0.0
        {
            return Err(Error::new(
                "COHORT_DOMAIN",
                "finite positive amplitude and matched ray arrays required",
            ));
        }
        for i in 0..n {
            if !self.mu[i].is_finite()
                || self.mu[i].abs() > 1.0
                || !self.alpha[i].is_finite()
                || self.alpha[i] <= 0.0
                || !self.mu_theta[i].is_finite()
                || !self.alpha_theta[i].is_finite()
                || (i > 0 && self.mu[i] <= self.mu[i - 1])
            {
                return Err(Error::new(
                    "COHORT_RAY_DOMAIN",
                    format!(
                        "ray {i}: strictly increasing nodes and positive physical weights required"
                    ),
                ));
            }
            let j = n - 1 - i;
            if self.mu[i] != -self.mu[j]
                || self.alpha[i] != self.alpha[j]
                || self.mu_theta[i] != -self.mu_theta[j]
                || self.alpha_theta[i] != self.alpha_theta[j]
            {
                return Err(Error::new(
                    "COHORT_REFLECTION",
                    format!("ray pair {i}/{j} does not have exact even/odd parity"),
                ));
            }
        }
        let norm = ordered_sum(self.alpha.iter().copied());
        let dnorm = ordered_sum(self.alpha_theta.iter().copied());
        if !norm.is_finite() || (norm - 1.0).abs() > NORMALIZATION_ATOL {
            return Err(Error::new(
                "COHORT_NORMALIZATION",
                format!("sum(alpha)={norm:.17e}"),
            ));
        }
        if !dnorm.is_finite() || dnorm.abs() > DERIVATIVE_NORMALIZATION_ATOL {
            return Err(Error::new(
                "COHORT_DERIVATIVE_NORMALIZATION",
                format!("sum(alpha_theta)={dnorm:.17e}"),
            ));
        }
        Ok(())
    }
}

#[derive(Clone, Debug)]
pub struct Bank {
    pub cohorts: Vec<Cohort>,
    pub donor0: f64,
    pub decay_lambda: f64,
    pub exposure: f64,
    pub cosmological_constant: f64,
}

impl Bank {
    pub fn validate(&self) -> Result<(), Error> {
        if self.cohorts.len() > MAX_COHORTS
            || [
                self.donor0,
                self.decay_lambda,
                self.exposure,
                self.cosmological_constant,
            ]
            .iter()
            .any(|x| !x.is_finite() || *x < 0.0)
        {
            return Err(Error::new(
                "BANK_DOMAIN",
                "nonnegative finite fixed donor parameters and bounded cohort count required",
            ));
        }
        let mut total = 0usize;
        for (i, c) in self.cohorts.iter().enumerate() {
            c.validate()
                .map_err(|e| Error::new(e.code, format!("cohort {i}: {}", e.detail)))?;
            total = total
                .checked_add(c.mu.len())
                .ok_or_else(|| Error::new("BANK_SIZE", "ray count overflow"))?;
            if total > MAX_TOTAL_RAYS {
                return Err(Error::new("BANK_SIZE", "total ray limit exceeded"));
            }
        }
        Ok(())
    }
}

#[derive(Clone, Debug)]
struct PreparedCohort {
    z: Vec<f64>,
}

#[derive(Clone, Copy, Debug)]
struct Ray {
    r: f64,
    d: f64,
    dd: f64,
    ddd: f64,
    r_mu: f64,
    d_mu: f64,
    dd_mu: f64,
}

#[inline]
fn ray(mu: f64, z: f64, perp: f64, para: f64) -> Ray {
    let w = perp * (1.0 - z);
    let v = para * z;
    let r = (w + v).sqrt();
    let r2 = r * r;
    let r3 = r2 * r;
    let r4 = r3 * r;
    let r5 = r4 * r;
    let d = (v - w / 2.0) / r;
    let n = w * w + 14.0 * w * v + 4.0 * v * v;
    let dd = -n / (2.0 * r3);
    let ddd = (-w * w * w + 60.0 * w * w * v - 12.0 * w * v * v + 8.0 * v * v * v) / (2.0 * r5);
    let r_mu = mu * (para - perp) / r;
    let d_mu = mu * (perp + 2.0 * para) / r - d * mu * (para - perp) / r2;
    let n_mu = 4.0 * mu * ((-perp + 7.0 * para) * w + (-7.0 * perp + 4.0 * para) * v);
    let dd_mu = -n_mu / (2.0 * r3) + 3.0 * n * r_mu / (2.0 * r4);
    Ray {
        r,
        d,
        dd,
        ddd,
        r_mu,
        d_mu,
        dd_mu,
    }
}

#[inline]
fn memory_terms(c: &Cohort, i: usize, k: Ray) -> [f64; 3] {
    let w = c.alpha[i];
    let dw = c.alpha_theta[i];
    let bm = w * c.memory_theta;
    let mm = w * c.mu_theta[i];
    [
        dw * k.r - bm * (-2.0 * k.d) + mm * k.r_mu,
        dw * k.d - bm * k.dd + mm * k.d_mu,
        dw * k.dd - bm * k.ddd + mm * k.dd_mu,
    ]
}

fn moments_baseline(c: &Cohort, x: f64, b: f64) -> [f64; 7] {
    let d = b - c.b_birth;
    let (perp, para) = ((2.0 * d).exp(), (-4.0 * d).exp());
    let mut s = [Sum::default(); 7];
    for i in 0..c.mu.len() {
        let k = ray(c.mu[i], c.mu[i] * c.mu[i], perp, para);
        let w = c.alpha[i];
        s[0].add(w * k.r);
        s[1].add(w * k.d);
        s[2].add(w * k.dd);
        s[3].add(w * k.ddd);
    }
    for i in 0..c.mu.len() {
        let k = ray(c.mu[i], c.mu[i] * c.mu[i], perp, para);
        let m = memory_terms(c, i, k);
        s[4].add(m[0]);
        s[5].add(m[1]);
    }
    for i in 0..c.mu.len() {
        let k = ray(c.mu[i], c.mu[i] * c.mu[i], perp, para);
        s[6].add(memory_terms(c, i, k)[2]);
    }
    let factor = c.energy_birth * (-4.0 * (x - c.u)).exp();
    std::array::from_fn(|j| factor * s[j].value())
}

fn moments_fused(c: &Cohort, p: &PreparedCohort, x: f64, b: f64) -> [f64; 7] {
    let d = b - c.b_birth;
    let (perp, para) = ((2.0 * d).exp(), (-4.0 * d).exp());
    let mut s = [Sum::default(); 7];
    for i in 0..c.mu.len() {
        let k = ray(c.mu[i], p.z[i], perp, para);
        let w = c.alpha[i];
        let m = memory_terms(c, i, k);
        s[0].add(w * k.r);
        s[1].add(w * k.d);
        s[2].add(w * k.dd);
        s[3].add(w * k.ddd);
        s[4].add(m[0]);
        s[5].add(m[1]);
        s[6].add(m[2]);
    }
    let factor = c.energy_birth * (-4.0 * (x - c.u)).exp();
    std::array::from_fn(|j| factor * s[j].value())
}

#[derive(Clone, Debug)]
pub struct Evaluation {
    pub rhs: [f64; 6],
    pub jacobian: [[f64; 6]; 6],
    pub partial_t: [f64; 6],
    /// E, Pi, Pi_b, Pi_bb, ME, MP, MP_b, Ed, E_theta, Pi_theta.
    pub moments: [f64; 10],
}

impl Evaluation {
    pub fn jvp(&self, v: [f64; 6]) -> Result<[f64; 6], Error> {
        if v.iter().any(|x| !x.is_finite()) {
            return Err(Error::new(
                "JVP_DIRECTION_DOMAIN",
                "finite direction required",
            ));
        }
        let answer =
            std::array::from_fn(|i| ordered_sum((0..6).map(|j| self.jacobian[i][j] * v[j])));
        if answer.iter().any(|x| !x.is_finite()) {
            return Err(Error::new(
                "JVP_NONFINITE",
                "nonfinite matrix-vector product",
            ));
        }
        Ok(answer)
    }
}

/// A newly allocated immutable bank snapshot; constructing another snapshot at a
/// birth cannot modify this evaluator or any previously admitted cohort.
#[derive(Clone, Debug)]
pub struct Evaluator {
    mode: Mode,
    bank: Bank,
    prepared: Vec<PreparedCohort>,
}

impl Evaluator {
    pub fn new(bank: Bank, mode: Mode) -> Result<Self, Error> {
        bank.validate()?;
        let prepared = if mode == Mode::Fused {
            bank.cohorts
                .iter()
                .map(|c| PreparedCohort {
                    z: c.mu.iter().map(|m| m * m).collect(),
                })
                .collect()
        } else {
            Vec::new()
        };
        Ok(Self {
            mode,
            bank,
            prepared,
        })
    }

    pub fn bank(&self) -> &Bank {
        &self.bank
    }
    pub fn mode(&self) -> Mode {
        self.mode
    }

    pub fn eval(&self, x: f64, z: [f64; 6]) -> Result<Evaluation, Error> {
        if !x.is_finite() || z.iter().any(|v| !v.is_finite()) || z[0] <= 0.0 {
            return Err(Error::new(
                "BACKGROUND_DOMAIN",
                "finite state and positive h required",
            ));
        }
        if self.bank.cohorts.iter().any(|c| x < c.u) {
            return Err(Error::new(
                "FUTURE_COHORT",
                "an active frozen bank cannot be evaluated before one of its births",
            ));
        }
        let [h, b, y, sh, sb, sy] = z;
        let mut sums = [Sum::default(); 7];
        for (i, c) in self.bank.cohorts.iter().enumerate() {
            let m = match self.mode {
                Mode::Baseline => moments_baseline(c, x, b),
                Mode::Fused => moments_fused(c, &self.prepared[i], x, b),
            };
            for j in 0..7 {
                sums[j].add(m[j]);
            }
        }
        let [e, p, pb, pbb, me, mp, mpb] = sums.map(Sum::value);
        let ed = self.bank.donor0 * (-3.0 * x - self.bank.decay_lambda * self.bank.exposure).exp();
        let fh = (-h * h - 2.0 * y * y - 0.5 * ed - e + self.bank.cosmological_constant) / h;
        let h2 = h * h;
        let h3 = h2 * h;
        let j = [
            [-2.0 - fh / h, 2.0 * p / h, -4.0 * y / h],
            [-y / h2, 0.0, 1.0 / h],
            [-p / h2, pb / h, -3.0],
        ];
        let s = [sh, sb, sy];
        let memory = [-me / h, 0.0, mp / h];
        let mut rhs = [fh, y / h, -3.0 * y + p / h, 0.0, 0.0, 0.0];
        for i in 0..3 {
            rhs[i + 3] = ordered_sum((0..3).map(|k| j[i][k] * s[k])) + memory[i];
        }

        let a = 2.0 * y * y + 0.5 * ed + e - self.bank.cosmological_constant;
        let lower = [
            [
                -2.0 * a * sh / h3 - 2.0 * p * sb / h2 + 4.0 * y * sy / h2 + me / h2,
                -2.0 * p * sh / h2 + 2.0 * pb * sb / h + 2.0 * mp / h,
                4.0 * y * sh / h2 - 4.0 * sy / h,
            ],
            [2.0 * y * sh / h3 - sy / h2, 0.0, -sh / h2],
            [
                2.0 * p * sh / h3 - pb * sb / h2 - mp / h2,
                -pb * sh / h2 + pbb * sb / h + mpb / h,
                0.0,
            ],
        ];
        let mut jacobian = [[0.0; 6]; 6];
        for i in 0..3 {
            for k in 0..3 {
                jacobian[i][k] = j[i][k];
                jacobian[i + 3][k] = lower[i][k];
                jacobian[i + 3][k + 3] = j[i][k];
            }
        }
        let partial_t = [
            (1.5 * ed + 4.0 * e) / h,
            0.0,
            -4.0 * p / h,
            (-1.5 * ed - 4.0 * e) * sh / h2 - 8.0 * p * sb / h + 4.0 * me / h,
            0.0,
            4.0 * p * sh / h2 - 4.0 * pb * sb / h - 4.0 * mp / h,
        ];
        let moments = [
            e,
            p,
            pb,
            pbb,
            me,
            mp,
            mpb,
            ed,
            -2.0 * p * sb + me,
            pb * sb + mp,
        ];
        if rhs
            .iter()
            .chain(jacobian.iter().flatten())
            .chain(partial_t.iter())
            .chain(moments.iter())
            .any(|v| !v.is_finite())
        {
            return Err(Error::new(
                "KERNEL_NONFINITE",
                "angular or augmented derivative evaluation was not finite",
            ));
        }
        Ok(Evaluation {
            rhs,
            jacobian,
            partial_t,
            moments,
        })
    }
}
