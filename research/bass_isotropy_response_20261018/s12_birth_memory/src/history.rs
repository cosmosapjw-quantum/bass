//! S12 fixed-event full birth-memory history adapter.
//!
//! This is an isolated manufactured donor experiment. It does not change S9/S10,
//! the spectral owner, existing physical weights, event coordinates, or donor
//! amplitudes. Each segment owns a fresh immutable evaluator and upstream driver.
//! P24 births use the unchanged S11 projector and an exact binary64-input gate.
//! Checkpoints describe only completed boundaries, and are bound to the exact
//! source commit, input bytes and executable. Resuming never reconstructs a bank
//! from rounded observations or silently changes solver/input parameters.

use crate::birth::{Differential, implicit_p24};
use crate::core::{Bank, Cohort as CoreCohort, Error, Evaluation, Evaluator, Mode, ordered_sum};
use crate::projector;
use num_bigint::BigInt;
use num_rational::BigRational;
use num_traits::{One, Signed, ToPrimitive, Zero};
use rodas5p_core::{CoreError, CoreResult, LinearMethod, LinearSolverConfig};
use rodas5p_integrators::{
    AdaptiveStepConfig, MaxStepPolicy, OdeProblem, OutputSchedule, SmallProblem,
    integrate_rodas5p_fast_small_observed,
    integrate_rodas5p_mf_fast_observed_gmres_into_ls_workspace,
};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::fs::{self, OpenOptions};
use std::io::Write;
use std::path::{Path, PathBuf};
use std::sync::{Arc, Mutex};
use std::time::Instant;

pub const ALGORITHM: &str = "BASS_S12_FIXED_EVENT_FULL_BIRTH_MEMORY_V1";
pub const VIGILODE_SOURCE: &str = "a21d573980f66fe02891bd216153443b5352f921";
pub const SPECTRAL_OWNER: &str = "0e25846433170d0f420c4cda44a0bedbf02cd177";
pub const PROJECTOR_SHA256: &str =
    "1f937f16dcb5a7dbdce92a66881d45276b67b202c56bdc232c1d281ad7fc6fcb";
pub const MAX_INPUT_BYTES: u64 = 64 * 1024 * 1024;
pub const MAX_CHECKPOINT_BYTES: u64 = 256 * 1024 * 1024;

pub fn sha256(bytes: &[u8]) -> String {
    hex::encode(Sha256::digest(bytes))
}

fn err(code: &str, detail: impl std::fmt::Display) -> String {
    format!("{code}: {detail}")
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PhysicalCohort {
    pub u: f64,
    pub b_birth: f64,
    pub energy_birth: f64,
    pub mu: Vec<f64>,
    pub alpha: Vec<f64>,
    pub role: String,
}

impl PhysicalCohort {
    /// Exactly the S9 physical digest recipe. Companion derivatives are separate.
    pub fn digest(&self) -> String {
        let mut h = Sha256::new();
        for x in [self.u, self.b_birth, self.energy_birth]
            .iter()
            .chain(&self.mu)
            .chain(&self.alpha)
        {
            h.update(x.to_le_bytes());
        }
        h.update(self.role.as_bytes());
        hex::encode(h.finalize())
    }
    fn validate(&self) -> Result<(), String> {
        let n = self.mu.len();
        CoreCohort {
            u: self.u,
            b_birth: self.b_birth,
            energy_birth: self.energy_birth,
            memory_theta: 0.0,
            mu: self.mu.clone(),
            alpha: self.alpha.clone(),
            mu_theta: vec![0.0; n],
            alpha_theta: vec![0.0; n],
        }
        .validate()
        .map_err(|e| e.to_string())
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MemoryCohort {
    pub physical: PhysicalCohort,
    /// The actual tangent at birth, before any explicit omission control.
    pub birth_b_theta: f64,
    /// The B_j used by this fresh companion. Physical data are never changed.
    pub memory_theta: f64,
    pub mu_b: Vec<f64>,
    pub alpha_b: Vec<f64>,
    pub mu_theta: Vec<f64>,
    pub alpha_theta: Vec<f64>,
    pub physical_sha256: String,
    pub memory_sha256: String,
}

impl MemoryCohort {
    fn new(
        physical: PhysicalCohort,
        birth_b_theta: f64,
        mu_b: Vec<f64>,
        alpha_b: Vec<f64>,
        control: &str,
    ) -> Result<Self, String> {
        let memory_theta = if control == "omit_birth_memory" {
            0.0
        } else {
            birth_b_theta
        };
        let mu_theta = mu_b
            .iter()
            .map(|m| {
                if control == "omit_mu_b" {
                    0.0
                } else {
                    m * birth_b_theta
                }
            })
            .collect();
        let alpha_theta = alpha_b
            .iter()
            .map(|a| {
                if control == "omit_alpha_b" {
                    0.0
                } else {
                    a * birth_b_theta
                }
            })
            .collect();
        let physical_sha256 = physical.digest();
        let mut c = Self {
            physical,
            birth_b_theta,
            memory_theta,
            mu_b,
            alpha_b,
            mu_theta,
            alpha_theta,
            physical_sha256,
            memory_sha256: String::new(),
        };
        c.memory_sha256 = c.memory_digest();
        c.validate()?;
        Ok(c)
    }
    fn memory_digest(&self) -> String {
        let mut h = Sha256::new();
        h.update(self.physical_sha256.as_bytes());
        for x in [self.birth_b_theta, self.memory_theta]
            .iter()
            .chain(&self.mu_b)
            .chain(&self.alpha_b)
            .chain(&self.mu_theta)
            .chain(&self.alpha_theta)
        {
            h.update(x.to_le_bytes());
        }
        hex::encode(h.finalize())
    }
    fn core(&self) -> CoreCohort {
        CoreCohort {
            u: self.physical.u,
            b_birth: self.physical.b_birth,
            energy_birth: self.physical.energy_birth,
            memory_theta: self.memory_theta,
            mu: self.physical.mu.clone(),
            alpha: self.physical.alpha.clone(),
            mu_theta: self.mu_theta.clone(),
            alpha_theta: self.alpha_theta.clone(),
        }
    }
    fn validate(&self) -> Result<(), String> {
        let n = self.physical.mu.len();
        if !self.birth_b_theta.is_finite()
            || self.mu_b.len() != n
            || self.alpha_b.len() != n
            || self
                .mu_b
                .iter()
                .chain(&self.alpha_b)
                .any(|v| !v.is_finite())
            || self
                .mu_b
                .iter()
                .zip(self.mu_b.iter().rev())
                .any(|(a, b)| *a != -*b)
            || self
                .alpha_b
                .iter()
                .zip(self.alpha_b.iter().rev())
                .any(|(a, b)| a != b)
        {
            return Err(err(
                "MEMORY_DOMAIN",
                "finite matched derivatives with exact parity required",
            ));
        }
        self.core().validate().map_err(|e| e.to_string())?;
        if self.physical.digest() != self.physical_sha256
            || self.memory_digest() != self.memory_sha256
        {
            return Err(err(
                "FROZEN_COHORT_DIGEST",
                "physical or companion bytes differ from their admitted digest",
            ));
        }
        Ok(())
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct MomentCertificate {
    pub criterion: String,
    pub gate_rational: String,
    pub pass: bool,
    pub normalization_pass: bool,
    pub sum_alpha_exact: String,
    pub normalization_residual_exact: String,
    pub m2_exact: String,
    pub m4_exact: String,
    pub residual_f64: [f64; 3],
}

/// The exact products and sums of actual binary64 inputs; no normalized proxy.
pub fn exact_moment_certificate(mu: &[f64], alpha: &[f64]) -> Result<MomentCertificate, String> {
    if mu.is_empty() || mu.len() != alpha.len() {
        return Err(err(
            "EXACT_MOMENT_INPUT",
            "matched nonempty arrays required",
        ));
    }
    let (mut norm, mut m2, mut m4) = (
        BigRational::zero(),
        BigRational::zero(),
        BigRational::zero(),
    );
    let integer = |n: i64| BigRational::from_integer(BigInt::from(n));
    for (&m, &w) in mu.iter().zip(alpha) {
        if !m.is_finite() || m.abs() > 1.0 || !w.is_finite() || w <= 0.0 {
            return Err(err(
                "EXACT_MOMENT_INPUT",
                "finite nodes and positive physical weights required",
            ));
        }
        let fm = BigRational::from_float(m).ok_or("EXACT_MOMENT_NONFINITE")?;
        let fw = BigRational::from_float(w).ok_or("EXACT_MOMENT_NONFINITE")?;
        let z = &fm * &fm;
        m2 += &fw * (integer(3) * &z - integer(1)) / integer(2);
        m4 += &fw * (integer(35) * &z * &z - integer(30) * &z + integer(3)) / integer(8);
        norm += fw;
    }
    let dr = &norm - BigRational::one();
    let gate = BigRational::new(BigInt::from(3), BigInt::from(1_000_000_000_000_000_i64));
    let normalization_pass = dr.abs() <= gate;
    let pass = normalization_pass && m2.abs() <= gate && m4.abs() <= gate;
    let residual_f64 =
        [dr.to_f64(), m2.to_f64(), m4.to_f64()].map(|v| v.ok_or("EXACT_MOMENT_F64_DISPLAY"));
    let residual_f64 = [
        residual_f64[0].clone()?,
        residual_f64[1].clone()?,
        residual_f64[2].clone()?,
    ];
    Ok(MomentCertificate {
        criterion:
            "Exact unnormalized binary64-input polynomial sums; no continuum/spectral certificate"
                .into(),
        gate_rational: gate.to_string(),
        pass,
        normalization_pass,
        sum_alpha_exact: norm.to_string(),
        normalization_residual_exact: dr.to_string(),
        m2_exact: m2.to_string(),
        m4_exact: m4.to_string(),
        residual_f64,
    })
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CoordinateGrid {
    pub mu0: Vec<f64>,
    pub prior0: Vec<f64>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Config {
    pub k: usize,
    pub n: usize,
    pub b0: f64,
    pub y0: f64,
    pub donor0: f64,
    pub old_isotropic: f64,
    pub old_anisotropic: f64,
    pub cosmological_constant: f64,
    pub decay_lambda: f64,
    pub birth_end: f64,
    pub x_end: f64,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SolverConfig {
    pub arm: String,
    pub rtol: f64,
    pub atol: f64,
    pub initial_step: f64,
    pub max_step: f64,
    pub max_attempts: usize,
    pub linear_rtol: f64,
    pub linear_atol: f64,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Input {
    pub schema: String,
    pub config: Config,
    pub coordinate_grid: CoordinateGrid,
    pub initial_cohorts: Vec<PhysicalCohort>,
    pub expected_old_digests: Vec<String>,
    pub output_times: Vec<f64>,
    pub solver: SolverConfig,
    pub provenance: Value,
    pub parameter: String,
    pub birth_rule: String,
    pub control: String,
    pub mode: String,
}

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Binding {
    pub source_commit: String,
    pub input_sha256: String,
    pub binary_sha256: String,
}

#[derive(Clone, Debug)]
pub struct RunOptions {
    pub binding: Binding,
    pub checkpoint_path: Option<PathBuf>,
    pub resume_path: Option<PathBuf>,
}

fn valid_hex(s: &str, n: usize) -> bool {
    s.len() == n
        && s.bytes()
            .all(|b| b.is_ascii_hexdigit() && !b.is_ascii_uppercase())
}

fn validate_input(input: &Input, binding: &Binding) -> Result<(), String> {
    if input.schema != "BASS_S12_HISTORY_INPUT_V1"
        || !valid_hex(&binding.source_commit, 40)
        || !valid_hex(&binding.input_sha256, 64)
        || !valid_hex(&binding.binary_sha256, 64)
    {
        return Err(err(
            "INPUT_IDENTITY",
            "exact schema and lowercase source/input/binary hashes required",
        ));
    }
    let c = &input.config;
    if c.k > 2048
        || c.n != input.coordinate_grid.mu0.len()
        || !(4..=512).contains(&c.n)
        || c.n % 2 != 0
        || c.n != input.coordinate_grid.prior0.len()
        || !(0.0 < c.birth_end && c.birth_end <= c.x_end && c.x_end <= 8.0)
        || [
            c.b0,
            c.y0,
            c.donor0,
            c.old_isotropic,
            c.old_anisotropic,
            c.cosmological_constant,
            c.decay_lambda,
        ]
        .iter()
        .any(|v| !v.is_finite())
        || [
            c.donor0,
            c.old_isotropic,
            c.old_anisotropic,
            c.cosmological_constant,
            c.decay_lambda,
        ]
        .iter()
        .any(|v| *v < 0.0)
        || (c.k == 0 && c.donor0 * c.decay_lambda != 0.0)
        || input
            .initial_cohorts
            .len()
            .checked_add(c.k)
            .is_none_or(|n| n > crate::core::MAX_COHORTS)
    {
        return Err(err(
            "CONFIG_DOMAIN",
            "bounded finite fixed-event manufactured configuration required",
        ));
    }
    Mode::parse(&input.mode).map_err(|e| e.to_string())?;
    if !["y0", "b0"].contains(&input.parameter.as_str())
        || !["P24", "source_frame_GL"].contains(&input.birth_rule.as_str())
        || !["full", "omit_birth_memory", "omit_mu_b", "omit_alpha_b"]
            .contains(&input.control.as_str())
        || (input.parameter == "b0"
            && (input.birth_rule != "source_frame_GL" || input.control != "full"))
    {
        return Err(err(
            "PARAMETER_CONTRACT",
            "b0 gauge is only the full source-frame GL control",
        ));
    }
    if !["mf_into_ls6", "small_clock7"].contains(&input.solver.arm.as_str()) {
        return Err(err(
            "SOLVER_ARM_DOMAIN",
            "expected mf_into_ls6 or small_clock7",
        ));
    }
    if input.output_times.len() > 10000
        || input.output_times.first() != Some(&0.0)
        || input.output_times.last() != Some(&c.x_end)
        || input.output_times.iter().any(|x| !x.is_finite())
        || input.output_times.windows(2).any(|p| p[1] <= p[0])
    {
        return Err(err(
            "OUTPUT_TIME_DOMAIN",
            "strictly increasing finite schedule from zero through x_end required",
        ));
    }
    // Coordinate priors are the original S9 raw GL rule (normally mass two).
    // They are not physical cohort weights. Only a fresh birth is normalized.
    validate_grid(&input.coordinate_grid)?;
    if input.birth_rule == "source_frame_GL" {
        let (mu, alpha) = birth_support(c.b0, &input.coordinate_grid, &input.birth_rule)?;
        if !exact_moment_certificate(&mu, &alpha)?.pass {
            return Err(err(
                "SOURCE_FRAME_GRID_MOMENT_GATE",
                "fresh normalized source-frame quadrature failed exact P24 admission",
            ));
        }
    }
    let (mut iso, mut aniso) = (0.0, 0.0);
    for cohort in &input.initial_cohorts {
        cohort.validate()?;
        if cohort.u != 0.0 || cohort.b_birth != c.b0 {
            return Err(err(
                "INITIAL_STOCK_FRAME",
                "all old cohorts must be supplied in the declared initial source frame",
            ));
        }
        // Old physical stock keeps its original S9 normalization and ownership
        // checks. New-birth P24 admission is not imposed on historical weights.
        match cohort.role.as_str() {
            "old_isotropic" => {
                iso += cohort.energy_birth;
            }
            "old_physical_anisotropic" => aniso += cohort.energy_birth,
            _ => return Err(err("INITIAL_STOCK_ROLE", "unexpected old-stock role")),
        }
    }
    if iso != c.old_isotropic || aniso != c.old_anisotropic {
        return Err(err(
            "INITIAL_STOCK_ENERGY",
            "declared amplitudes and supplied physical cohorts differ",
        ));
    }
    if input
        .initial_cohorts
        .iter()
        .map(PhysicalCohort::digest)
        .collect::<Vec<_>>()
        != input.expected_old_digests
    {
        return Err(err(
            "OLD_STOCK_DIGEST_MISMATCH",
            "input physical bytes do not match fixed owner digests",
        ));
    }
    let h0 =
        (c.y0 * c.y0 + c.donor0 + c.old_isotropic + c.old_anisotropic + c.cosmological_constant)
            .sqrt();
    if !h0.is_finite() || h0 <= 0.0 {
        return Err(err(
            "INITIAL_BACKGROUND",
            "finite strictly positive h0 required",
        ));
    }
    Ok(())
}

fn validate_grid(grid: &CoordinateGrid) -> Result<f64, String> {
    let n = grid.mu0.len();
    if !(4..=512).contains(&n) || n % 2 != 0 || grid.prior0.len() != n {
        return Err(err(
            "COORDINATE_GRID_DOMAIN",
            "matched even raw prior arrays required",
        ));
    }
    for i in 0..n {
        let j = n - 1 - i;
        if !grid.mu0[i].is_finite()
            || grid.mu0[i].abs() > 1.0
            || !grid.prior0[i].is_finite()
            || grid.prior0[i] <= 0.0
            || (i > 0 && grid.mu0[i] <= grid.mu0[i - 1])
            || grid.mu0[i] != -grid.mu0[j]
            || grid.prior0[i] != grid.prior0[j]
        {
            return Err(err(
                "COORDINATE_GRID_DOMAIN",
                "strict nodes, positive raw priors and exact reflection required",
            ));
        }
    }
    let mass = ordered_sum(grid.prior0.iter().copied());
    if !mass.is_finite() || mass <= 0.0 {
        return Err(err(
            "COORDINATE_PRIOR_MASS",
            "finite positive raw prior mass required",
        ));
    }
    Ok(mass)
}

pub fn birth_support(
    b: f64,
    grid: &CoordinateGrid,
    rule: &str,
) -> Result<(Vec<f64>, Vec<f64>), String> {
    let raw_mass = validate_grid(grid)?;
    if rule == "source_frame_GL" {
        let alpha = grid.prior0.iter().map(|w| w / raw_mass).collect();
        return Ok((grid.mu0.clone(), alpha));
    }
    if rule != "P24" || !b.is_finite() || b.abs() > 2.0 {
        return Err(err(
            "BIRTH_COORDINATE_INPUT",
            "P24 support construction is limited to finite |b|<=2",
        ));
    }
    let mut mu = Vec::with_capacity(grid.mu0.len());
    let mut q = Vec::with_capacity(grid.mu0.len());
    let (ep, em, emhalf) = ((2.0 * b).exp(), (-4.0 * b).exp(), (-2.0 * b).exp());
    for (&m, &w) in grid.mu0.iter().zip(&grid.prior0) {
        let r = (ep * (1.0 - m * m) + em * m * m).sqrt();
        mu.push(m * emhalf / r);
        q.push(w / (r * r * r));
    }
    let total = ordered_sum(q.iter().copied());
    if !total.is_finite() || total <= 0.0 {
        return Err(err(
            "BIRTH_PRIOR_MASS",
            "finite positive fresh prior mass required",
        ));
    }
    for w in &mut q {
        *w /= total;
    }
    if mu.iter().chain(&q).any(|x| !x.is_finite()) {
        return Err(err(
            "BIRTH_SUPPORT_NONFINITE",
            "fresh support transform overflowed",
        ));
    }
    Ok((mu, q))
}

fn evaluator(input: &Input, cohorts: &[MemoryCohort], exposure: f64) -> Result<Evaluator, String> {
    for c in cohorts {
        c.validate()?;
    }
    Evaluator::new(
        Bank {
            cohorts: cohorts.iter().map(MemoryCohort::core).collect(),
            donor0: input.config.donor0,
            decay_lambda: input.config.decay_lambda,
            exposure,
            cosmological_constant: input.config.cosmological_constant,
        },
        Mode::parse(&input.mode).map_err(|e| e.to_string())?,
    )
    .map_err(|e| e.to_string())
}

fn core_error(e: Error) -> CoreError {
    CoreError::InvalidInput(e.to_string())
}
fn state6(z: &[f64]) -> CoreResult<[f64; 6]> {
    z.try_into()
        .map_err(|_| CoreError::Dimension("S12 augmented state must have dimension six".into()))
}

pub fn ode_problem(e: Arc<Evaluator>) -> CoreResult<OdeProblem> {
    let (rhs, jvp, pt) = (e.clone(), e.clone(), e);
    OdeProblem::new(
        "BASS S12 immutable full birth-memory parameter tangent",
        6,
        Arc::new(move |x, z, out| {
            out.copy_from_slice(&rhs.eval(x, state6(z)?).map_err(core_error)?.rhs);
            Ok(())
        }),
        None,
        None,
        Some(Arc::new(move |x, z, v, out| {
            out.copy_from_slice(
                &jvp.eval(x, state6(z)?)
                    .map_err(core_error)?
                    .jvp(state6(v)?)
                    .map_err(core_error)?,
            );
            Ok(())
        })),
        Some(Arc::new(move |x, z, out| {
            out.copy_from_slice(&pt.eval(x, state6(z)?).map_err(core_error)?.partial_t);
            Ok(())
        })),
        false,
        None,
        None,
    )
}

/// SmallProblem is autonomous. The seventh state is x, and its full Jacobian
/// column is analytic partial_x of all six augmented components.
pub struct ClockProblem {
    pub evaluator: Arc<Evaluator>,
    first_error: Mutex<Option<String>>,
}
impl ClockProblem {
    fn record(&self, e: Error) {
        if let Ok(mut stored) = self.first_error.lock() {
            if stored.is_none() {
                *stored = Some(e.to_string());
            }
        }
    }
    fn failure(&self) -> Option<String> {
        self.first_error.lock().ok().and_then(|g| g.clone())
    }
}
impl SmallProblem<7> for ClockProblem {
    fn rhs(&self, z: &[f64; 7], out: &mut [f64; 7]) {
        match self
            .evaluator
            .eval(z[6], [z[0], z[1], z[2], z[3], z[4], z[5]])
        {
            Ok(e) => {
                out[..6].copy_from_slice(&e.rhs);
                out[6] = 1.0;
            }
            Err(e) => {
                self.record(e);
                out.fill(f64::NAN);
            }
        }
    }
    fn jacobian(&self, z: &[f64; 7], out: &mut [[f64; 7]; 7]) {
        *out = [[0.0; 7]; 7];
        match self
            .evaluator
            .eval(z[6], [z[0], z[1], z[2], z[3], z[4], z[5]])
        {
            Ok(e) => {
                for i in 0..6 {
                    out[i][..6].copy_from_slice(&e.jacobian[i]);
                    out[i][6] = e.partial_t[i];
                }
            }
            Err(e) => {
                self.record(e);
                *out = [[f64::NAN; 7]; 7];
            }
        }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Observation {
    pub x: f64,
    pub state: [f64; 6],
    pub e_donor: f64,
    pub e_radiation: f64,
    pub pi: f64,
    pub me: f64,
    pub mp: f64,
    pub e_theta: f64,
    pub pi_theta: f64,
    pub sigma: f64,
    pub c: f64,
    pub c_relative: f64,
    pub c_theta: f64,
    pub c_theta_relative: f64,
    pub c_theta_propagation_residual: f64,
    pub c_theta_propagation_relative: f64,
    pub clock_error: f64,
}
fn observe(
    evaluator: &Evaluator,
    x: f64,
    state: [f64; 6],
    clock_error: f64,
) -> Result<Observation, String> {
    let e = evaluator.eval(x, state).map_err(|e| e.to_string())?;
    let [h, _, y, sh, sb, sy] = state;
    let [er, p, _, _, me, mp, _, ed, et, pt] = e.moments;
    let l = evaluator.bank().cosmological_constant;
    let c = h * h - y * y - ed - er - l;
    let scale = h * h + y * y + ed + er + l;
    let ct = 2.0 * h * sh - 2.0 * y * sy - et;
    let et_prime = -4.0 * et - 2.0 * (e.rhs[1] * pt + e.rhs[4] * p);
    let ct_prime = 2.0 * e.rhs[0] * sh + 2.0 * h * e.rhs[3]
        - 2.0 * e.rhs[2] * sy
        - 2.0 * y * e.rhs[5]
        - et_prime;
    let propagation = ct_prime + 2.0 * ct;
    if !scale.is_finite()
        || scale <= 0.0
        || [c, ct, propagation, clock_error, sb]
            .iter()
            .any(|v| !v.is_finite())
    {
        return Err(err(
            "OBSERVATION_NONFINITE",
            "finite constraints and positive scale required",
        ));
    }
    Ok(Observation {
        x,
        state,
        e_donor: ed,
        e_radiation: er,
        pi: p,
        me,
        mp,
        e_theta: et,
        pi_theta: pt,
        sigma: 3.0_f64.sqrt() * y.abs() / h,
        c,
        c_relative: c.abs() / scale,
        c_theta: ct,
        c_theta_relative: ct.abs() / scale,
        c_theta_propagation_residual: propagation,
        c_theta_propagation_relative: propagation.abs() / scale,
        clock_error,
    })
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct RunReceipt {
    pub schema: String,
    pub algorithm: String,
    pub vigilode_source: String,
    pub spectral_owner: String,
    pub projector_sha256: String,
    pub binding: Binding,
    pub input: Input,
    pub status: String,
    pub failure: Option<Value>,
    pub observations: Vec<Observation>,
    pub events: Vec<Value>,
    pub segments: Vec<Value>,
    pub final_cohorts: Vec<MemoryCohort>,
    pub old_stock_digests: Vec<String>,
    pub pending_birth: Option<Value>,
    pub checkpoint_writes: usize,
    pub resumed: bool,
    pub resume_boundary: Option<Value>,
    pub elapsed_seconds: f64,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Checkpoint {
    schema: String,
    binding: Binding,
    next_segment: usize,
    pending_event: Option<usize>,
    begin: f64,
    state: [f64; 6],
    exposure: f64,
    receipt: RunReceipt,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct CheckpointEnvelope {
    schema: String,
    payload_sha256: String,
    payload: Checkpoint,
}

fn atomic_write(path: &Path, bytes: &[u8]) -> Result<(), String> {
    let parent = path
        .parent()
        .filter(|p| !p.as_os_str().is_empty())
        .unwrap_or_else(|| Path::new("."));
    fs::create_dir_all(parent).map_err(|e| err("CHECKPOINT_DIRECTORY", e))?;
    let name = path
        .file_name()
        .ok_or("CHECKPOINT_FILENAME")?
        .to_string_lossy();
    let temp = parent.join(format!(".{name}.s12.{}.tmp", std::process::id()));
    let write = (|| -> std::io::Result<()> {
        let mut f = OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(&temp)?;
        f.write_all(bytes)?;
        f.sync_all()?;
        fs::rename(&temp, path)?;
        if let Ok(dir) = fs::File::open(parent) {
            dir.sync_all()?;
        }
        Ok(())
    })();
    if write.is_err() {
        let _ = fs::remove_file(&temp);
    }
    write.map_err(|e| err("CHECKPOINT_ATOMIC_WRITE", e))
}

struct Progress {
    next_segment: usize,
    pending_event: Option<usize>,
    begin: f64,
    state: [f64; 6],
    exposure: f64,
}

fn save_checkpoint(
    options: &RunOptions,
    progress: &Progress,
    receipt: &mut RunReceipt,
    start: &Instant,
    prior_elapsed: f64,
) -> Result<(), String> {
    let Some(path) = &options.checkpoint_path else {
        return Ok(());
    };
    let mut saved = receipt.clone();
    saved.checkpoint_writes += 1;
    saved.elapsed_seconds = prior_elapsed + start.elapsed().as_secs_f64();
    let payload = Checkpoint {
        schema: "BASS_S12_BOUNDARY_CHECKPOINT_V1".into(),
        binding: options.binding.clone(),
        next_segment: progress.next_segment,
        pending_event: progress.pending_event,
        begin: progress.begin,
        state: progress.state,
        exposure: progress.exposure,
        receipt: saved,
    };
    let data = serde_json::to_vec(&payload).map_err(|e| err("CHECKPOINT_SERIALIZE", e))?;
    let envelope = CheckpointEnvelope {
        schema: "BASS_S12_BOUNDARY_ENVELOPE_V1".into(),
        payload_sha256: sha256(&data),
        payload,
    };
    let bytes = serde_json::to_vec_pretty(&envelope).map_err(|e| err("CHECKPOINT_SERIALIZE", e))?;
    if bytes.len() as u64 > MAX_CHECKPOINT_BYTES {
        return Err(err("CHECKPOINT_SIZE", "boundary exceeds fixed byte cap"));
    }
    atomic_write(path, &bytes)?;
    receipt.checkpoint_writes += 1;
    Ok(())
}

fn load_checkpoint(
    path: &Path,
    input: &Input,
    binding: &Binding,
    births: &[f64],
    endpoints: &[f64],
) -> Result<(Progress, RunReceipt), String> {
    if fs::metadata(path)
        .map_err(|e| err("CHECKPOINT_READ", e))?
        .len()
        > MAX_CHECKPOINT_BYTES
    {
        return Err(err("CHECKPOINT_SIZE", "checkpoint exceeds fixed byte cap"));
    }
    let bytes = fs::read(path).map_err(|e| err("CHECKPOINT_READ", e))?;
    let env: CheckpointEnvelope =
        serde_json::from_slice(&bytes).map_err(|e| err("CHECKPOINT_JSON", e))?;
    if env.schema != "BASS_S12_BOUNDARY_ENVELOPE_V1"
        || sha256(&serde_json::to_vec(&env.payload).map_err(|e| err("CHECKPOINT_SERIALIZE", e))?)
            != env.payload_sha256
    {
        return Err(err(
            "CHECKPOINT_CHECKSUM",
            "serialized boundary payload does not match",
        ));
    }
    let cp = env.payload;
    if cp.schema != "BASS_S12_BOUNDARY_CHECKPOINT_V1"
        || cp.binding != *binding
        || cp.receipt.binding != *binding
        || cp.receipt.algorithm != ALGORITHM
        || cp.receipt.vigilode_source != VIGILODE_SOURCE
        || cp.receipt.spectral_owner != SPECTRAL_OWNER
        || cp.receipt.projector_sha256 != PROJECTOR_SHA256
        || serde_json::to_vec(&cp.receipt.input).map_err(|e| err("CHECKPOINT_SERIALIZE", e))?
            != serde_json::to_vec(input).map_err(|e| err("CHECKPOINT_SERIALIZE", e))?
    {
        return Err(err(
            "CHECKPOINT_BINDING",
            "source, exact input, binary, owner or algorithm differs",
        ));
    }
    if cp.next_segment > endpoints.len()
        || cp.state.iter().any(|v| !v.is_finite())
        || cp.state[0] <= 0.0
        || !cp.receipt.elapsed_seconds.is_finite()
        || cp.receipt.elapsed_seconds < 0.0
        || cp.receipt.failure.is_some()
        || cp.receipt.pending_birth.is_some()
        || !["incomplete", "completed"].contains(&cp.receipt.status.as_str())
        || cp.receipt.segments.len() != cp.next_segment
    {
        return Err(err(
            "CHECKPOINT_PROGRESS",
            "invalid completed-boundary shape",
        ));
    }
    let expected_begin = if cp.next_segment == 0 {
        0.0
    } else {
        endpoints[cp.next_segment - 1]
    };
    let expected_events = match cp.pending_event {
        Some(i) if i < births.len() && cp.next_segment == i + 1 => i,
        None => cp.next_segment.min(births.len()),
        _ => {
            return Err(err(
                "CHECKPOINT_EVENT",
                "pending event index is inconsistent",
            ));
        }
    };
    let du = if input.config.k == 0 {
        0.0
    } else {
        input.config.birth_end / input.config.k as f64
    };
    if cp.begin != expected_begin
        || cp.exposure != expected_events as f64 * du
        || cp.receipt.events.len() != expected_events
        || cp.receipt.final_cohorts.len() != input.initial_cohorts.len() + expected_events
        || cp.receipt.old_stock_digests != input.expected_old_digests
    {
        return Err(err(
            "CHECKPOINT_PREFIX",
            "birth/exposure/physical prefix differs",
        ));
    }
    for (i, c) in cp.receipt.final_cohorts.iter().enumerate() {
        c.validate()?;
        if i < input.initial_cohorts.len() {
            if c.physical_sha256 != input.expected_old_digests[i]
                || c.birth_b_theta != if input.parameter == "b0" { 1.0 } else { 0.0 }
                || c.memory_theta != c.birth_b_theta
                || c.mu_b
                    .iter()
                    .chain(&c.alpha_b)
                    .chain(&c.mu_theta)
                    .chain(&c.alpha_theta)
                    .any(|v| *v != 0.0)
            {
                return Err(err(
                    "CHECKPOINT_OLD_STOCK",
                    "old physical or companion contract differs",
                ));
            }
        } else {
            let j = i - input.initial_cohorts.len();
            let event = &cp.receipt.events[j];
            if c.physical.u != births[j]
                || event["u"].as_f64() != Some(births[j])
                || event["physical_sha256"].as_str() != Some(c.physical_sha256.as_str())
                || event["memory_sha256"].as_str() != Some(c.memory_sha256.as_str())
                || !exact_moment_certificate(&c.physical.mu, &c.physical.alpha)?.pass
            {
                return Err(err(
                    "CHECKPOINT_BIRTH",
                    "admitted birth record or exact moment gate differs",
                ));
            }
            let bm = if input.control == "omit_birth_memory" {
                0.0
            } else {
                c.birth_b_theta
            };
            if c.memory_theta != bm
                || c.mu_theta.iter().zip(&c.mu_b).any(|(v, m)| {
                    *v != if input.control == "omit_mu_b" {
                        0.0
                    } else {
                        m * c.birth_b_theta
                    }
                })
                || c.alpha_theta.iter().zip(&c.alpha_b).any(|(v, a)| {
                    *v != if input.control == "omit_alpha_b" {
                        0.0
                    } else {
                        a * c.birth_b_theta
                    }
                })
            {
                return Err(err(
                    "CHECKPOINT_MEMORY",
                    "omission rule or frozen derivative differs",
                ));
            }
        }
    }
    let last = cp
        .receipt
        .observations
        .last()
        .ok_or("CHECKPOINT_OBSERVATIONS_EMPTY")?;
    if last.x != cp.begin
        || last.state != cp.state
        || cp.receipt.observations.windows(2).any(|r| r[1].x <= r[0].x)
    {
        return Err(err(
            "CHECKPOINT_OBSERVATIONS",
            "last full state or schedule differs",
        ));
    }
    evaluator(input, &cp.receipt.final_cohorts, cp.exposure)?;
    let progress = Progress {
        next_segment: cp.next_segment,
        pending_event: cp.pending_event,
        begin: cp.begin,
        state: cp.state,
        exposure: cp.exposure,
    };
    let mut receipt = cp.receipt;
    receipt.resumed = true;
    receipt.resume_boundary = Some(json!({"checkpoint_payload_sha256":env.payload_sha256,
        "next_segment":progress.next_segment,"pending_event":progress.pending_event,
        "x":progress.begin,"state":progress.state,"exposure":progress.exposure}));
    Ok((progress, receipt))
}

fn evaluation_json(e: &Evaluation) -> Value {
    json!({"rhs":e.rhs,"jacobian":e.jacobian,"partial_t":e.partial_t,"moments":e.moments})
}
fn digest_pairs(cohorts: &[MemoryCohort]) -> Vec<(String, String)> {
    cohorts
        .iter()
        .map(|c| (c.physical_sha256.clone(), c.memory_sha256.clone()))
        .collect()
}

fn admit_event(
    input: &Input,
    index: usize,
    progress: &mut Progress,
    receipt: &mut RunReceipt,
) -> Result<(), String> {
    let c = &input.config;
    let du = c.birth_end / c.k as f64;
    let x = progress.begin;
    let z = progress.state;
    let before_bank = evaluator(input, &receipt.final_cohorts, progress.exposure)?;
    let before = before_bank.eval(x, z).map_err(|e| e.to_string())?;
    let before_digests = digest_pairs(&receipt.final_cohorts);
    let energy = before.moments[7] * (-(-c.decay_lambda * du).exp_m1());
    if !energy.is_finite() || energy <= 0.0 {
        return Err(err(
            "BIRTH_POSITIVE_TRANSFER",
            "analytic donor transfer is not finite and strictly positive",
        ));
    }
    receipt.pending_birth = Some(json!({"index":index,"u":x,"state":z,"energy_birth":energy,
        "stage":"construct_fresh_support","admitted":false}));
    let (mu, prior) = birth_support(z[1], &input.coordinate_grid, &input.birth_rule)?;
    receipt.pending_birth = Some(json!({"index":index,"u":x,"state":z,"energy_birth":energy,
        "mu":mu,"prior":prior,"stage":"project_fresh_isotropic_birth","admitted":false}));
    let (alpha, multipliers, projection) = if input.birth_rule == "P24" {
        let p = projector::project(&mu, &prior, 4, true).map_err(|e| err(e.status, e.message))?;
        let projection = json!({"algorithm":"S11_SIMULTANEOUS_NEWTON_P24",
            "source_sha256":PROJECTOR_SHA256,"order":4,"multipliers":p.lambda,
            "iterations":p.iterations,"f64_residuals":p.residuals,
            "support":{"distinct_squared_nodes":p.support.distinct_squared_nodes,
                "facet_count":p.support.facet_count,
                "minimum_certified_slack_lower":p.support.minimum_certified_slack_lower}});
        (p.weights, p.lambda, projection)
    } else {
        (
            prior.clone(),
            vec![],
            json!({"algorithm":"FIXED_SOURCE_FRAME_GL_CONTROL",
            "support_transformed":false,"fresh_prior_normalized":true,
            "KL_reweighted":false,"old_weights_modified":false}),
        )
    };
    let physical = PhysicalCohort {
        u: x,
        b_birth: z[1],
        energy_birth: energy,
        mu,
        alpha,
        role: if input.birth_rule == "P24" {
            "new_isotropic_P24"
        } else {
            "new_isotropic_source_frame_GL"
        }
        .into(),
    };
    physical.validate()?;
    let cert = exact_moment_certificate(&physical.mu, &physical.alpha)?;
    receipt.pending_birth = Some(json!({"index":index,"u":x,"state":z,
        "candidate_physical":physical,"exact_moment_certificate":cert,
        "projection":projection,"stage":"exact_moment_admission","admitted":false}));
    if !cert.pass {
        return Err(err(
            "EXACT_BIRTH_MOMENT_GATE",
            "new candidate failed fixed 3/10^15 gate",
        ));
    }
    let differential: Option<Differential> = if input.birth_rule == "P24" {
        Some(
            implicit_p24(&physical.mu, &prior, &physical.alpha, &multipliers)
                .map_err(|e| e.to_string())?,
        )
    } else {
        None
    };
    let n = physical.mu.len();
    let (mu_b, alpha_b) = differential
        .as_ref()
        .map(|d| (d.mu_b.clone(), d.alpha_b.clone()))
        .unwrap_or((vec![0.0; n], vec![0.0; n]));
    let cohort = MemoryCohort::new(physical, z[4], mu_b, alpha_b, &input.control)?;
    receipt.pending_birth = Some(
        json!({"index":index,"u":x,"state":z,"candidate_cohort":cohort,
        "exact_moment_certificate":cert,"projection":projection,
        "implicit_kl":differential.as_ref().map(|d|&d.diagnostics),
        "stage":"admit_frozen_physical_and_companion","admitted":false}),
    );
    let mut candidate = receipt.final_cohorts.clone();
    candidate.push(cohort.clone());
    let next_exposure = (index + 1) as f64 * du;
    let after_bank = evaluator(input, &candidate, next_exposure)?;
    let after = after_bank.eval(x, z).map_err(|e| e.to_string())?;
    if digest_pairs(&candidate[..before_digests.len()]) != before_digests {
        return Err(err(
            "STOCK_MUTATED_AT_BIRTH",
            "physical or memory prefix changed",
        ));
    }
    let energy_jump = after.moments[7] + after.moments[0] - before.moments[7] - before.moments[0];
    let et_jump = after.moments[8] - before.moments[8];
    let pt_jump = after.moments[9] - before.moments[9];
    let scale = before.moments[7] + before.moments[0];
    if !scale.is_finite() || scale <= 0.0 {
        return Err(err(
            "BIRTH_EVENT_SCALE",
            "positive transfer-ledger scale required",
        ));
    }
    let clock = receipt
        .observations
        .last()
        .ok_or("BIRTH_OUTPUT_MISSING")?
        .clock_error;
    let after_observation = observe(&after_bank, x, z, clock)?;
    receipt.events.push(json!({"index":index,"u":x,"state":z,"b_birth":z[1],
        "birth_b_theta":z[4],"energy_birth":energy,"exposure_before":progress.exposure,
        "exposure_after":next_exposure,"donor_before":before.moments[7],"donor_after":after.moments[7],
        "radiation_before":before.moments[0],"radiation_after":after.moments[0],
        "pi_before":before.moments[1],"pi_after":after.moments[1],
        "e_theta_before":before.moments[8],"e_theta_after":after.moments[8],
        "pi_theta_before":before.moments[9],"pi_theta_after":after.moments[9],
        "energy_jump":energy_jump,"energy_jump_relative":energy_jump.abs()/scale,
        "energy_theta_jump":et_jump,"energy_theta_jump_relative":et_jump.abs()/scale,
        "pi_theta_jump":pt_jump,"pi_theta_jump_relative":pt_jump.abs()/scale,
        "state_jump":[0.0,0.0,0.0,0.0,0.0,0.0],"before":evaluation_json(&before),"after":evaluation_json(&after),
        "exact_moment_certificate":cert,"projection":projection,
        "implicit_kl":differential.as_ref().map(|d|&d.diagnostics),
        "physical_sha256":cohort.physical_sha256,"memory_sha256":cohort.memory_sha256,
        "previous_physical_and_memory_digests_unchanged":true,
        "control":input.control,"admitted":true}));
    *receipt
        .observations
        .last_mut()
        .ok_or("BIRTH_OUTPUT_MISSING")? = after_observation;
    receipt.final_cohorts = candidate;
    receipt.pending_birth = None;
    progress.exposure = next_exposure;
    progress.pending_event = None;
    Ok(())
}

pub fn failure_kind(error: &str) -> &'static str {
    if error.starts_with("INFEASIBLE") {
        "support_feasibility"
    } else if error.starts_with("FEASIBILITY_UNRESOLVED") {
        "support_feasibility_unresolved"
    } else if error.contains("PRECISION") {
        "angular_numeric_precision"
    } else if error.contains("MOMENT_GATE") {
        "exact_moment_admission"
    } else if error.starts_with("KL_") {
        "implicit_KL_derivative"
    } else if error.starts_with("CHECKPOINT") {
        "checkpoint_contract"
    } else if error.starts_with("SOLVER") {
        "solver_failure"
    } else if error.contains("STOCK") || error.contains("COHORT") {
        "stock_contract"
    } else {
        "input_or_numeric_failure"
    }
}

pub fn run(input: Input, options: RunOptions) -> RunReceipt {
    let start = Instant::now();
    let mut receipt = RunReceipt {
        schema: "BASS_S12_HISTORY_RUN_V1".into(),
        algorithm: ALGORITHM.into(),
        vigilode_source: VIGILODE_SOURCE.into(),
        spectral_owner: SPECTRAL_OWNER.into(),
        projector_sha256: PROJECTOR_SHA256.into(),
        binding: options.binding.clone(),
        input: input.clone(),
        status: "incomplete".into(),
        failure: None,
        observations: vec![],
        events: vec![],
        segments: vec![],
        final_cohorts: vec![],
        old_stock_digests: input.expected_old_digests.clone(),
        pending_birth: None,
        checkpoint_writes: 0,
        resumed: false,
        resume_boundary: None,
        elapsed_seconds: 0.0,
    };
    let mut prior_elapsed = 0.0;
    let result = run_inner(&input, &options, &mut receipt, &start, &mut prior_elapsed);
    match result {
        Ok(()) => receipt.status = "completed".into(),
        Err(e) => {
            receipt.status = "failed".into();
            receipt.failure = Some(json!({"kind":failure_kind(&e),"error":e,
                "retained_segment_records":receipt.segments.len(),"admitted_births":receipt.events.len()}));
        }
    }
    receipt.elapsed_seconds = prior_elapsed + start.elapsed().as_secs_f64();
    receipt
}

fn run_inner(
    input: &Input,
    options: &RunOptions,
    receipt: &mut RunReceipt,
    start: &Instant,
    prior_elapsed: &mut f64,
) -> Result<(), String> {
    validate_input(input, &options.binding)?;
    if let Some(path) = &options.checkpoint_path {
        if path.exists() {
            let same = options
                .resume_path
                .as_ref()
                .and_then(|p| fs::canonicalize(p).ok())
                == fs::canonicalize(path).ok();
            if !same {
                return Err(err(
                    "CHECKPOINT_EXISTS",
                    "existing checkpoint may only be replaced by an explicit resume of that file",
                ));
            }
        }
    }
    let c = &input.config;
    let sc = &input.solver;
    let adaptive = AdaptiveStepConfig {
        rtol: sc.rtol,
        atol: sc.atol,
        initial_step: sc.initial_step,
        max_step: sc.max_step,
        max_attempts: sc.max_attempts,
        max_step_policy: MaxStepPolicy::StrictRepresentedCap,
        ..Default::default()
    };
    adaptive.validate().map_err(|e| err("SOLVER_CONFIG", e))?;
    let linear = LinearSolverConfig {
        method: LinearMethod::Gmres,
        rtol: sc.linear_rtol,
        atol: sc.linear_atol,
        restart: 8,
        maxiter: 40,
        ..Default::default()
    };
    linear
        .validate()
        .map_err(|e| err("SOLVER_LINEAR_CONFIG", e))?;
    let births: Vec<f64> = if c.donor0 * c.decay_lambda == 0.0 {
        vec![]
    } else {
        (0..c.k)
            .map(|i| (i as f64 + 0.5) * c.birth_end / c.k as f64)
            .collect()
    };
    let mut endpoints = births.clone();
    endpoints.push(c.x_end);
    let mut progress = if let Some(path) = &options.resume_path {
        let (p, r) = load_checkpoint(path, input, &options.binding, &births, &endpoints)?;
        *prior_elapsed = r.elapsed_seconds;
        *receipt = r;
        receipt.status = "incomplete".into();
        p
    } else {
        let old_b = if input.parameter == "b0" { 1.0 } else { 0.0 };
        for physical in &input.initial_cohorts {
            let n = physical.mu.len();
            receipt.final_cohorts.push(MemoryCohort::new(
                physical.clone(),
                old_b,
                vec![0.0; n],
                vec![0.0; n],
                "full",
            )?);
        }
        let h = (c.y0 * c.y0
            + c.donor0
            + c.old_isotropic
            + c.old_anisotropic
            + c.cosmological_constant)
            .sqrt();
        let state = if input.parameter == "y0" {
            [h, c.b0, c.y0, c.y0 / h, 0.0, 1.0]
        } else {
            [h, c.b0, c.y0, 0.0, 1.0, 0.0]
        };
        let e = evaluator(input, &receipt.final_cohorts, 0.0)?;
        receipt.observations.push(observe(&e, 0.0, state, 0.0)?);
        Progress {
            next_segment: 0,
            pending_event: None,
            begin: 0.0,
            state,
            exposure: 0.0,
        }
    };
    save_checkpoint(options, &progress, receipt, start, *prior_elapsed)?;
    loop {
        if let Some(index) = progress.pending_event {
            admit_event(input, index, &mut progress, receipt)?;
            save_checkpoint(options, &progress, receipt, start, *prior_elapsed)?;
            continue;
        }
        if progress.next_segment == endpoints.len() {
            break;
        }
        let index = progress.next_segment;
        let end = endpoints[index];
        let before_digests = digest_pairs(&receipt.final_cohorts);
        let shared = Arc::new(evaluator(input, &receipt.final_cohorts, progress.exposure)?);
        let mut times = vec![progress.begin];
        times.extend(
            input
                .output_times
                .iter()
                .copied()
                .filter(|x| *x > progress.begin && *x < end),
        );
        times.push(end);
        let schedule =
            OutputSchedule::new(times.clone()).map_err(|e| err("SOLVER_OUTPUT_SCHEDULE", e))?;
        let mut base = json!({"index":index,"begin":progress.begin,"end":end,
            "fresh_driver":true,"fresh_immutable_bank":true,
            "cohort_count":receipt.final_cohorts.len(),"exposure":progress.exposure,
            "physical_and_memory_digests":before_digests,"output_times":times,
            "start_state":progress.state,"mode":input.mode,"arm":sc.arm,"status":"started"});
        receipt.segments.push(base.clone());
        let result = if sc.arm == "mf_into_ls6" {
            let problem = ode_problem(shared.clone()).map_err(|e| err("SOLVER_PROBLEM", e))?;
            integrate_rodas5p_mf_fast_observed_gmres_into_ls_workspace(
                &problem,
                (progress.begin, end),
                &progress.state,
                &linear,
                &adaptive,
                &schedule,
            )
            .map(|r| {
                let meta = json!({"driver":r.driver,"attempts":r.attempts,
                        "accepted":r.accepted_steps,"rejected":r.rejected_steps,
                        "state_reuses":r.state_reuses,"krylov_workspace":r.krylov_workspace});
                (r.observed, meta, None)
            })
            .map_err(|e| err("SOLVER_UPSTREAM_ERROR", e))
        } else {
            let problem = ClockProblem {
                evaluator: shared.clone(),
                first_error: Mutex::new(None),
            };
            let z = progress.state;
            let result = integrate_rodas5p_fast_small_observed(
                &problem,
                (progress.begin, end),
                &[z[0], z[1], z[2], z[3], z[4], z[5], progress.begin],
                &adaptive,
                &schedule,
            );
            let callback_error = problem.failure();
            result
                .map(|r| {
                    let meta = json!({"driver":r.driver,"attempts":r.attempts,
                    "accepted":r.accepted_steps,"rejected":r.rejected_steps,
                    "jacobian_reuses":r.jacobian_reuses,"clock_augmentation":true,
                    "first_callback_error":callback_error});
                    (r.observed, meta, callback_error)
                })
                .map_err(|e| {
                    err(
                        "SOLVER_UPSTREAM_ERROR",
                        format!("{e}; first_callback_error={:?}", problem.failure()),
                    )
                })
        };
        let (observed, meta, callback_error) = match result {
            Ok(v) => v,
            Err(e) => {
                base["status"] = json!("upstream_error");
                base["error"] = json!(e);
                *receipt.segments.last_mut().ok_or("SOLVER_SEGMENT_RECORD")? = base;
                return Err(e);
            }
        };
        base["status"] = json!(if observed.success {
            "returned_success"
        } else {
            "returned_failure"
        });
        base["success"] = json!(observed.success);
        base["message"] = json!(observed.message);
        base["solver"] = meta;
        base["counters"] = json!(observed.counters);
        base["internal_steps"] = json!(observed.internal_steps);
        base["output_clipped_steps"] = json!(observed.output_clipped_steps);
        base["raw_times"] = json!(observed.t);
        base["raw_states"] = json!(observed.y);
        // JSON has no NaN/Inf literals; retain exact bits even on an upstream
        // failure so the raw failed state is recoverable without interpretation.
        base["raw_time_bits"] = json!(observed.t.iter().map(|v| v.to_bits()).collect::<Vec<_>>());
        base["raw_state_bits"] = json!(
            observed
                .y
                .iter()
                .map(|z| z.iter().map(|v| v.to_bits()).collect::<Vec<_>>())
                .collect::<Vec<_>>()
        );
        *receipt.segments.last_mut().ok_or("SOLVER_SEGMENT_RECORD")? = base;
        if observed.t.len() != observed.y.len()
            || observed.t.first() != Some(&progress.begin)
            || observed
                .y
                .first()
                .is_none_or(|z| z.len() != if sc.arm == "mf_into_ls6" { 6 } else { 7 })
            || observed.y.first().is_none_or(|z| z[..6] != progress.state)
        {
            return Err(err(
                "SOLVER_OUTPUT_SHAPE",
                "raw initial state or output lengths differ",
            ));
        }
        for (&x, z) in observed.t.iter().zip(&observed.y).skip(1) {
            if z.len() != if sc.arm == "mf_into_ls6" { 6 } else { 7 } {
                return Err(err("SOLVER_STATE_SHAPE", "unexpected augmented dimension"));
            }
            let state = [z[0], z[1], z[2], z[3], z[4], z[5]];
            let clock = if z.len() == 7 { z[6] - x } else { 0.0 };
            receipt
                .observations
                .push(observe(&shared, x, state, clock)?);
        }
        if let Some(e) = callback_error {
            return Err(err("SOLVER_CALLBACK_FAILURE", e));
        }
        if !observed.success {
            return Err(err("SOLVER_RETURNED_FAILURE", &observed.message));
        }
        if observed.t != times || observed.t.last() != Some(&end) {
            return Err(err(
                "SOLVER_EXACT_OUTPUT_SCHEDULE",
                "raw schedule differs from fixed requested endpoints",
            ));
        }
        let last = observed.y.last().ok_or("SOLVER_EMPTY_OUTPUT")?;
        progress.state = [last[0], last[1], last[2], last[3], last[4], last[5]];
        for cohort in &receipt.final_cohorts {
            cohort.validate()?;
        }
        if digest_pairs(&receipt.final_cohorts) != before_digests {
            return Err(err(
                "STOCK_MUTATED_DURING_SEGMENT",
                "frozen physical or memory prefix differs",
            ));
        }
        progress.begin = end;
        progress.next_segment += 1;
        progress.pending_event = if index < births.len() {
            Some(index)
        } else {
            None
        };
        save_checkpoint(options, &progress, receipt, start, *prior_elapsed)?;
    }
    if receipt
        .final_cohorts
        .iter()
        .take(input.initial_cohorts.len())
        .map(|c| c.physical_sha256.clone())
        .collect::<Vec<_>>()
        != input.expected_old_digests
    {
        return Err(err(
            "OLD_STOCK_FINAL_DIGEST",
            "old physical ownership changed",
        ));
    }
    receipt.status = "completed".into();
    save_checkpoint(options, &progress, receipt, start, *prior_elapsed)?;
    Ok(())
}
