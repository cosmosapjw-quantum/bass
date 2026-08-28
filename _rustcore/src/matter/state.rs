//! Immutable RF-03 state and fixed-context validation.

use std::error::Error;
use std::fmt::{Display, Formatter};

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum MatterError {
    Model(String),
    Input(String),
    Domain(String),
}

impl Display for MatterError {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> std::fmt::Result {
        let (code, detail) = match self {
            Self::Model(detail) => ("RF03_MODEL_ERROR", detail),
            Self::Input(detail) => ("RF03_INPUT_ERROR", detail),
            Self::Domain(detail) => ("RF03_DOMAIN_ERROR", detail),
        };
        write!(formatter, "{code}: {detail}")
    }
}

impl Error for MatterError {}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct MatterState {
    pub omega: f64,
    pub v: [f64; 3],
}

impl MatterState {
    pub fn new(omega: f64, v: [f64; 3]) -> Result<Self, MatterError> {
        let state = Self { omega, v };
        state.validate()?;
        Ok(state)
    }

    pub fn validate(self) -> Result<(), MatterError> {
        if !self.omega.is_finite() || self.v.iter().any(|value| !value.is_finite()) {
            return Err(MatterError::Domain(
                "Omega and every tilt component must be finite".to_string(),
            ));
        }
        if self.omega < 0.0 {
            return Err(MatterError::Domain("Omega must be nonnegative".to_string()));
        }
        let v2 = dot(self.v, self.v);
        if !v2.is_finite() || v2 >= 1.0 {
            return Err(MatterError::Domain(format!(
                "tilt must satisfy v_i v^i < 1; observed {v2}"
            )));
        }
        Ok(())
    }

    #[inline]
    pub fn as_array(self) -> [f64; 4] {
        [self.omega, self.v[0], self.v[1], self.v[2]]
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct MatterDirection {
    pub omega: f64,
    pub v: [f64; 3],
}

impl MatterDirection {
    pub fn new(omega: f64, v: [f64; 3]) -> Result<Self, MatterError> {
        if !omega.is_finite() || v.iter().any(|value| !value.is_finite()) {
            return Err(MatterError::Input(
                "every JVP direction component must be finite".to_string(),
            ));
        }
        Ok(Self { omega, v })
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct MatterContext {
    pub sigma: [[f64; 3]; 3],
    pub n: [[f64; 3]; 3],
    pub a: [f64; 3],
    pub r: [f64; 3],
    pub q: f64,
}

impl MatterContext {
    pub fn new(
        sigma: [[f64; 3]; 3],
        n: [[f64; 3]; 3],
        a: [f64; 3],
        r: [f64; 3],
        q: f64,
    ) -> Result<Self, MatterError> {
        let all_finite = sigma
            .iter()
            .flatten()
            .chain(n.iter().flatten())
            .chain(a.iter())
            .chain(r.iter())
            .all(|value| value.is_finite())
            && q.is_finite();
        if !all_finite {
            return Err(MatterError::Input(
                "Sigma, N, A, R, and q must be finite".to_string(),
            ));
        }
        Ok(Self { sigma, n, a, r, q })
    }

    pub(crate) fn interpolate(self, other: Self, fraction: f64) -> Self {
        let blend = |left: f64, right: f64| left + fraction * (right - left);
        Self {
            sigma: std::array::from_fn(|row| {
                std::array::from_fn(|column| {
                    blend(self.sigma[row][column], other.sigma[row][column])
                })
            }),
            n: std::array::from_fn(|row| {
                std::array::from_fn(|column| blend(self.n[row][column], other.n[row][column]))
            }),
            a: std::array::from_fn(|index| blend(self.a[index], other.a[index])),
            r: std::array::from_fn(|index| blend(self.r[index], other.r[index])),
            q: blend(self.q, other.q),
        }
    }
}

#[inline]
pub(crate) fn dot(left: [f64; 3], right: [f64; 3]) -> f64 {
    left[0] * right[0] + left[1] * right[1] + left[2] * right[2]
}

#[inline]
pub(crate) fn cross(left: [f64; 3], right: [f64; 3]) -> [f64; 3] {
    [
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    ]
}

#[inline]
pub(crate) fn mat_vec(matrix: [[f64; 3]; 3], vector: [f64; 3]) -> [f64; 3] {
    [
        matrix[0][0] * vector[0] + matrix[0][1] * vector[1] + matrix[0][2] * vector[2],
        matrix[1][0] * vector[0] + matrix[1][1] * vector[1] + matrix[1][2] * vector[2],
        matrix[2][0] * vector[0] + matrix[2][1] * vector[1] + matrix[2][2] * vector[2],
    ]
}
