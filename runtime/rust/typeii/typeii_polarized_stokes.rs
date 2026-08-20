//! G-POL-LIOUVILLE-II-B1: finite tensor <-> local Stokes sign authority.
//!
//! The raw BASS carrier is the existing nine-real representation of a Hermitian
//! 3x3 coherency tensor: six symmetric components and three imaginary
//! antisymmetric components.  For a right-handed screen dyad (s1,s2,e), this
//! module fixes
//!
//! H = 1/2 [[I+Q, U-iV], [U+iV, I-Q]],
//! packed[8] = -V/2 on the canonical (x,y,z) screen,
//! (Q+iU)' = exp(-2 i psi)(Q+iU) for a passive basis rotation, and
//! (Q+iU)' = exp(+2 i psi)(Q+iU) for an active tensor rotation.

pub type Mat3 = [[f64; 3]; 3];

const DEFAULT_TOL: f64 = 1e-12;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Handedness {
    Right,
    Left,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Stokes {
    pub i: f64,
    pub q: f64,
    pub u: f64,
    pub v: f64,
}

impl Stokes {
    #[inline]
    pub fn is_finite(self) -> bool {
        self.i.is_finite() && self.q.is_finite() && self.u.is_finite() && self.v.is_finite()
    }

    #[inline]
    pub fn cone_scalar(self) -> f64 {
        self.i * self.i - self.q * self.q - self.u * self.u - self.v * self.v
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct ScreenDyad {
    e: [f64; 3],
    s1: [f64; 3],
    s2: [f64; 3],
    handedness: Handedness,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum StokesError {
    InvalidDyad,
    NonFiniteTensor,
    NonFiniteStokes,
    NonFiniteAngle,
    InvalidAxis,
}

#[inline]
fn dot(a: [f64; 3], b: [f64; 3]) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}

#[inline]
fn cross(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
}

#[inline]
fn norm(a: [f64; 3]) -> f64 {
    dot(a, a).sqrt()
}

#[inline]
fn scale(a: [f64; 3], x: f64) -> [f64; 3] {
    [x * a[0], x * a[1], x * a[2]]
}

#[inline]
fn sub(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
}

#[inline]
fn normalize(a: [f64; 3]) -> Option<[f64; 3]> {
    if !a.iter().all(|x| x.is_finite()) {
        return None;
    }
    let n = norm(a);
    if !(n > 0.0 && n.is_finite()) {
        return None;
    }
    Some(scale(a, 1.0 / n))
}

impl ScreenDyad {
    pub fn new(
        e: [f64; 3],
        s1: [f64; 3],
        s2: [f64; 3],
        tolerance: f64,
    ) -> Result<Self, StokesError> {
        if !(tolerance > 0.0 && tolerance.is_finite())
            || !e
                .iter()
                .chain(s1.iter())
                .chain(s2.iter())
                .all(|x| x.is_finite())
        {
            return Err(StokesError::InvalidDyad);
        }
        if (norm(e) - 1.0).abs() > tolerance
            || (norm(s1) - 1.0).abs() > tolerance
            || (norm(s2) - 1.0).abs() > tolerance
            || dot(e, s1).abs() > tolerance
            || dot(e, s2).abs() > tolerance
            || dot(s1, s2).abs() > tolerance
        {
            return Err(StokesError::InvalidDyad);
        }
        let orient = dot(cross(s1, s2), e);
        if (orient.abs() - 1.0).abs() > 8.0 * tolerance {
            return Err(StokesError::InvalidDyad);
        }
        Ok(Self {
            e,
            s1,
            s2,
            handedness: if orient >= 0.0 {
                Handedness::Right
            } else {
                Handedness::Left
            },
        })
    }

    /// Deterministic right-handed local screen.  This is a local chart helper,
    /// not a globally nonsingular dyad atlas.
    pub fn canonical(e: [f64; 3]) -> Result<Self, StokesError> {
        let e = normalize(e).ok_or(StokesError::InvalidDyad)?;
        let refs = [[0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]];
        let reference = refs
            .into_iter()
            .min_by(|a, b| dot(*a, e).abs().total_cmp(&dot(*b, e).abs()))
            .ok_or(StokesError::InvalidDyad)?;
        let s1 = normalize(sub(reference, scale(e, dot(reference, e))))
            .ok_or(StokesError::InvalidDyad)?;
        let s2 = normalize(cross(e, s1)).ok_or(StokesError::InvalidDyad)?;
        Self::new(e, s1, s2, 64.0 * f64::EPSILON)
    }

    #[inline]
    pub fn e(&self) -> [f64; 3] {
        self.e
    }

    #[inline]
    pub fn s1(&self) -> [f64; 3] {
        self.s1
    }

    #[inline]
    pub fn s2(&self) -> [f64; 3] {
        self.s2
    }

    #[inline]
    pub fn handedness(&self) -> Handedness {
        self.handedness
    }

    pub fn with_handedness(self, handedness: Handedness) -> Self {
        if self.handedness == handedness {
            self
        } else {
            Self {
                s2: scale(self.s2, -1.0),
                handedness,
                ..self
            }
        }
    }

    pub fn passive_rotated(self, psi: f64) -> Result<Self, StokesError> {
        if !psi.is_finite() {
            return Err(StokesError::NonFiniteAngle);
        }
        let (sn, c) = psi.sin_cos();
        let s1 = [
            c * self.s1[0] + sn * self.s2[0],
            c * self.s1[1] + sn * self.s2[1],
            c * self.s1[2] + sn * self.s2[2],
        ];
        let s2 = [
            -sn * self.s1[0] + c * self.s2[0],
            -sn * self.s1[1] + c * self.s2[1],
            -sn * self.s1[2] + c * self.s2[2],
        ];
        Self::new(self.e, s1, s2, 128.0 * f64::EPSILON)
    }
}

#[inline]
pub fn packed_to_matrix(p: &[f64; 9]) -> Result<Mat3, StokesError> {
    if !p.iter().all(|x| x.is_finite()) {
        return Err(StokesError::NonFiniteTensor);
    }
    Ok([
        [p[0], p[3] + p[8], p[4] - p[7]],
        [p[3] - p[8], p[1], p[5] + p[6]],
        [p[4] + p[7], p[5] - p[6], p[2]],
    ])
}

#[inline]
pub fn matrix_to_packed(m: &Mat3) -> Result<[f64; 9], StokesError> {
    if !m.iter().flatten().all(|x| x.is_finite()) {
        return Err(StokesError::NonFiniteTensor);
    }
    Ok([
        m[0][0],
        m[1][1],
        m[2][2],
        0.5 * (m[0][1] + m[1][0]),
        0.5 * (m[0][2] + m[2][0]),
        0.5 * (m[1][2] + m[2][1]),
        0.5 * (m[1][2] - m[2][1]),
        0.5 * (m[2][0] - m[0][2]),
        0.5 * (m[0][1] - m[1][0]),
    ])
}

#[inline]
fn bilinear(a: [f64; 3], m: &Mat3, b: [f64; 3]) -> f64 {
    let mut out = 0.0;
    for i in 0..3 {
        for j in 0..3 {
            out += a[i] * m[i][j] * b[j];
        }
    }
    out
}

pub fn packed_to_stokes(packed: &[f64; 9], dyad: &ScreenDyad) -> Result<Stokes, StokesError> {
    let m = packed_to_matrix(packed)?;
    let h11 = bilinear(dyad.s1, &m, dyad.s1);
    let h22 = bilinear(dyad.s2, &m, dyad.s2);
    let h12 = bilinear(dyad.s1, &m, dyad.s2);
    let h21 = bilinear(dyad.s2, &m, dyad.s1);
    let out = Stokes {
        i: h11 + h22,
        q: h11 - h22,
        u: h12 + h21,
        v: h21 - h12,
    };
    if out.is_finite() {
        Ok(out)
    } else {
        Err(StokesError::NonFiniteStokes)
    }
}

pub fn stokes_to_packed(stokes: Stokes, dyad: &ScreenDyad) -> Result<[f64; 9], StokesError> {
    if !stokes.is_finite() {
        return Err(StokesError::NonFiniteStokes);
    }
    let mut m = [[0.0; 3]; 3];
    let h11 = 0.5 * (stokes.i + stokes.q);
    let h22 = 0.5 * (stokes.i - stokes.q);
    let h12 = 0.5 * (stokes.u - stokes.v);
    let h21 = 0.5 * (stokes.u + stokes.v);
    for a in 0..3 {
        for b in 0..3 {
            m[a][b] = h11 * dyad.s1[a] * dyad.s1[b]
                + h22 * dyad.s2[a] * dyad.s2[b]
                + h12 * dyad.s1[a] * dyad.s2[b]
                + h21 * dyad.s2[a] * dyad.s1[b];
        }
    }
    matrix_to_packed(&m)
}

pub fn passive_rotate_stokes(stokes: Stokes, psi: f64) -> Result<Stokes, StokesError> {
    if !stokes.is_finite() {
        return Err(StokesError::NonFiniteStokes);
    }
    if !psi.is_finite() {
        return Err(StokesError::NonFiniteAngle);
    }
    let (sn, c) = (2.0 * psi).sin_cos();
    Ok(Stokes {
        i: stokes.i,
        q: c * stokes.q + sn * stokes.u,
        u: c * stokes.u - sn * stokes.q,
        v: stokes.v,
    })
}

pub fn active_rotate_stokes(stokes: Stokes, psi: f64) -> Result<Stokes, StokesError> {
    if !stokes.is_finite() {
        return Err(StokesError::NonFiniteStokes);
    }
    if !psi.is_finite() {
        return Err(StokesError::NonFiniteAngle);
    }
    let (sn, c) = (2.0 * psi).sin_cos();
    Ok(Stokes {
        i: stokes.i,
        q: c * stokes.q - sn * stokes.u,
        u: sn * stokes.q + c * stokes.u,
        v: stokes.v,
    })
}

#[inline]
fn transpose(a: &Mat3) -> Mat3 {
    let mut out = [[0.0; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            out[i][j] = a[j][i];
        }
    }
    out
}

#[inline]
fn mm(a: &Mat3, b: &Mat3) -> Mat3 {
    let mut out = [[0.0; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            for k in 0..3 {
                out[i][j] += a[i][k] * b[k][j];
            }
        }
    }
    out
}

fn rodrigues(axis: [f64; 3], angle: f64) -> Result<Mat3, StokesError> {
    if !angle.is_finite() {
        return Err(StokesError::NonFiniteAngle);
    }
    let axis = normalize(axis).ok_or(StokesError::InvalidAxis)?;
    if (norm(axis) - 1.0).abs() > DEFAULT_TOL {
        return Err(StokesError::InvalidAxis);
    }
    let (sn, c) = angle.sin_cos();
    let one = 1.0 - c;
    let [x, y, z] = axis;
    Ok([
        [c + one * x * x, one * x * y - sn * z, one * x * z + sn * y],
        [one * y * x + sn * z, c + one * y * y, one * y * z - sn * x],
        [one * z * x - sn * y, one * z * y + sn * x, c + one * z * z],
    ])
}

pub fn active_rotate_tensor(
    packed: &[f64; 9],
    axis: [f64; 3],
    angle: f64,
) -> Result<[f64; 9], StokesError> {
    let m = packed_to_matrix(packed)?;
    let r = rodrigues(axis, angle)?;
    matrix_to_packed(&mm(&mm(&r, &m), &transpose(&r)))
}
