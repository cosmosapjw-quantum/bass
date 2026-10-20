//! Opt-in S10 callbacks. The original S9 crate remains the baseline authority.
//!
//! No new moment constraint, source closure, spectral operation or solver policy.
//! Every original scientific receipt field is retained. Timing is external to
//! the scientific comparison and is never inferred from work counts.
#![deny(unsafe_op_in_unsafe_fn)]

use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::str::FromStr;

pub use bass_s9_vigilode::{CallbackInput, CallbackQuery, Cohort, Evaluation,
    FrozenBank, Input, RunReceipt};

mod adapter;
mod kernel;
mod runner;
pub mod fixtures;

pub use kernel::{Backend, CacheCounters, Evaluator};

pub const IMPLEMENTATION: &str = "BASS_S10_ORDERED_CALLBACK_VARIANTS_V1";
pub const BASELINE_SOURCE_SHA256: &str =
    "204d3fa9dd4a5ed8400410ff1035c4771e11d6ff50d5267a3756a740cf9b731b";

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Mode { Baseline, Stream, Prepared, Cache, Simd, SimdCache }

impl Mode {
    pub const ALL: [Self; 6] = [Self::Baseline, Self::Stream, Self::Prepared,
        Self::Cache, Self::Simd, Self::SimdCache];
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Baseline => "baseline", Self::Stream => "stream",
            Self::Prepared => "prepared", Self::Cache => "cache",
            Self::Simd => "simd", Self::SimdCache => "simd_cache",
        }
    }
    pub(crate) fn prepared(self) -> bool {
        matches!(self, Self::Prepared | Self::Cache | Self::Simd | Self::SimdCache)
    }
    pub(crate) fn cached(self) -> bool { matches!(self, Self::Cache | Self::SimdCache) }
    pub(crate) fn simd(self) -> bool { matches!(self, Self::Simd | Self::SimdCache) }
}

impl FromStr for Mode {
    type Err = String;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        Self::ALL.into_iter().find(|m| m.as_str() == s)
            .ok_or_else(|| format!("OPTIMIZATION_MODE_DOMAIN: {s}"))
    }
}

/// Baseline calls the original run function. Candidate modes change only solver
/// callbacks in the provenanced copy; administrative observations/births retain
/// the original evaluator, certificate, projection and failure behavior.
pub fn run_with_mode(input: Input, mode: Mode) -> RunReceipt {
    if mode == Mode::Baseline { bass_s9_vigilode::run(input) }
    else { runner::run_candidate(input, mode) }
}

/// Independent histories only. No inner parallel moment reduction or global
/// pool. Indexed collection preserves input order for workers 1, 2 and 4.
pub fn run_independent(inputs: Vec<Input>, mode: Mode, workers: usize)
    -> Result<Vec<RunReceipt>, String>
{
    if !matches!(workers, 1 | 2 | 4) { return Err("WORKER_CAP_DOMAIN_1_2_4".into()); }
    let pool = rayon::ThreadPoolBuilder::new().num_threads(workers).build()
        .map_err(|e| format!("LOCAL_THREAD_POOL: {e}"))?;
    Ok(pool.install(|| inputs.into_par_iter().map(|i| run_with_mode(i, mode)).collect()))
}

/// All original fields except the explicitly non-scientific elapsed timer.
/// Serialize this Value to bytes to distinguish signed zero, too.
pub fn scientific_value(receipt: &RunReceipt) -> Value {
    let mut value = serde_json::to_value(receipt).expect("RunReceipt serialization");
    value.as_object_mut().expect("RunReceipt object").remove("elapsed_seconds");
    value
}

pub fn scientific_bytes(receipt: &RunReceipt) -> Vec<u8> {
    serde_json::to_vec(&scientific_value(receipt)).expect("scientific receipt serialization")
}

/// Original callback JSON shape; mode/backend belongs to the command or outer
/// benchmark receipt. No physics or signed-zero field is removed for comparison.
pub fn callbacks_with_mode(input: CallbackInput, mode: Mode) -> Result<Value, String> {
    if mode == Mode::Baseline { return bass_s9_vigilode::callbacks(input); }
    for c in &input.bank.cohorts { c.validate()?; }
    let evaluator = Evaluator::new(input.bank.clone(), mode);
    let mut rows = vec![];
    for q in input.queries {
        let ev = evaluator.eval(q.x, q.state)?;
        rows.push(json!({"x":q.x,"state":q.state,"direction":q.direction,"evaluation":ev,
            "jvp":evaluator.jvp(q.x,q.state,q.direction)?}));
    }
    Ok(json!({"algorithm":bass_s9_vigilode::ALGORITHM,"bank":input.bank,"rows":rows}))
}
