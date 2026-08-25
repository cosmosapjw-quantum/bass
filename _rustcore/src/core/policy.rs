//! Immutable RF-01 plan configuration and scalar dispatch policy.

use std::fmt;

pub const DEFAULT_FIXTURE_SIZE: u64 = 64;
pub const MAX_FIXTURE_SIZE: u64 = 16 * 1024 * 1024;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum CpuVariant {
    Scalar,
}

impl CpuVariant {
    pub fn parse(value: &str) -> Result<Self, PolicyError> {
        match value {
            "scalar" => Ok(Self::Scalar),
            other => Err(PolicyError::UnsupportedCpuVariant(other.to_owned())),
        }
    }

    pub const fn as_str(self) -> &'static str {
        match self {
            Self::Scalar => "scalar",
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct PlanConfig {
    pub thread_count: usize,
    pub fixture_size: usize,
    pub require_finite: bool,
    pub cpu_variant: CpuVariant,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum PolicyError {
    InvalidThreadCount(String),
    InvalidFixtureSize(String),
    UnsupportedCpuVariant(String),
}

impl fmt::Display for PolicyError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InvalidThreadCount(message) | Self::InvalidFixtureSize(message) => {
                formatter.write_str(message)
            }
            Self::UnsupportedCpuVariant(value) => write!(
                formatter,
                "cpu_variant {value:?} is unsupported; RF-01 permits only scalar"
            ),
        }
    }
}

impl PlanConfig {
    pub fn validate(
        thread_count: i64,
        fixture_size: u64,
        require_finite: bool,
        cpu_variant: &str,
    ) -> Result<Self, PolicyError> {
        if thread_count <= 0 {
            return Err(PolicyError::InvalidThreadCount(
                "thread_count must be a positive integer".to_owned(),
            ));
        }
        let thread_count = usize::try_from(thread_count).map_err(|_| {
            PolicyError::InvalidThreadCount("thread_count exceeds this host ABI".to_owned())
        })?;
        let maximum = rayon::max_num_threads();
        if thread_count > maximum {
            return Err(PolicyError::InvalidThreadCount(format!(
                "thread_count {thread_count} exceeds the Rayon limit {maximum}"
            )));
        }
        if fixture_size == 0 || fixture_size > MAX_FIXTURE_SIZE {
            return Err(PolicyError::InvalidFixtureSize(format!(
                "fixture_size must be in 1..={MAX_FIXTURE_SIZE}"
            )));
        }
        let fixture_size = usize::try_from(fixture_size).map_err(|_| {
            PolicyError::InvalidFixtureSize("fixture_size exceeds this host ABI".to_owned())
        })?;
        fixture_size.checked_mul(4).ok_or_else(|| {
            PolicyError::InvalidFixtureSize(
                "fixture_size overflows the four-stage workspace".to_owned(),
            )
        })?;
        Ok(Self {
            thread_count,
            fixture_size,
            require_finite,
            cpu_variant: CpuVariant::parse(cpu_variant)?,
        })
    }

    pub fn canonical_fingerprint(&self) -> String {
        let canonical = format!(
            "schema=bass-runtime-plan-v1;threads={};fixture_size={};finite={};cpu={};tables=rf01-synthetic-v1",
            self.thread_count,
            self.fixture_size,
            self.require_finite,
            self.cpu_variant.as_str(),
        );
        let hash = canonical
            .as_bytes()
            .iter()
            .fold(0xcbf29ce484222325_u64, |hash, byte| {
                (hash ^ u64::from(*byte)).wrapping_mul(0x100000001b3)
            });
        format!("bass-runtime-plan-v1:fnv1a64:{hash:016x}")
    }
}
