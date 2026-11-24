//! Universal Lie-algebra data of a spatially homogeneous orthonormal frame.
//!
//! Every Bianchi type is a choice of structure constants
//! C^k_ij = eps_ijl N^lk + A_i delta^k_j - A_j delta^k_i with N symmetric and the
//! Jacobi identity N A = 0 (Dossier I (1.2), II ii:commutator). Every geometric and
//! kinetic operator of BASS is a polynomial in the Hubble-normalized data
//! (Sigma, N, A, Omega) and the matter moments, so a type is an initial condition,
//! not a code path. This module
//!
//! * builds canonical algebras of all families with a scale and an SO(3) orientation,
//! * classifies Lie data with the invariants preserved by the exact evolution
//!   (rank/inertia of N, A = 0 or not, h = A^2/(n2 n3); Dossier I (1.26)-(1.27)),
//! * generates the *type constants* of photon transport: the Y_LM coefficients
//!   (L <= 2) of the four potentials of Dossier II ii:hodge_potentials,
//!   R~ = -Sigma:ee, U = -Sigma:ee/2 - A.e, Z = -N_TF:ee/2 - Omega.e,
//!   omega = Omega.e + N_TF:ee - tr N/6,
//!   which are the only place where the algebra enters the radiation hierarchy
//!   (`kinetic::lie_hierarchy`).
//!
//! Y_LM are Condon-Shortley spherical harmonics, identical to `spin_sht` with s = 0.
use crate::geom::group::BianchiGroup;
use nalgebra::{Complex, Matrix3, Vector3};
use std::f64::consts::PI;

pub type C64 = Complex<f64>;
pub type Tensor = [[f64; 3]; 3];

/// Number of Y_LM coefficients with L <= 2 (flat index L*L + L + M).
pub const POTENTIAL_MODES: usize = 9;

#[inline]
pub fn potential_index(l: usize, m: i64) -> usize {
    ((l * l + l) as i64 + m) as usize
}

fn matrix(t: &Tensor) -> Matrix3<f64> {
    Matrix3::from_fn(|i, j| t[i][j])
}
fn tensor(m: &Matrix3<f64>) -> Tensor {
    std::array::from_fn(|i| std::array::from_fn(|j| m[(i, j)]))
}

/// Hubble-normalized Lie data of one slice in a right-handed orthonormal frame.
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct LieData {
    pub shear: Tensor,
    pub n: Tensor,
    pub a: [f64; 3],
    /// Angular velocity Omega of the triad (zero for Fermi propagation).
    pub rotation: [f64; 3],
}

impl LieData {
    pub fn lerp(&self, other: &Self, f: f64) -> Self {
        let b = |x: f64, y: f64| x + (y - x) * f;
        Self {
            shear: std::array::from_fn(|i| {
                std::array::from_fn(|j| b(self.shear[i][j], other.shear[i][j]))
            }),
            n: std::array::from_fn(|i| std::array::from_fn(|j| b(self.n[i][j], other.n[i][j]))),
            a: std::array::from_fn(|i| b(self.a[i], other.a[i])),
            rotation: std::array::from_fn(|i| b(self.rotation[i], other.rotation[i])),
        }
    }
    /// Active proper rotation of all tensors and vectors by `r`.
    pub fn rotated(&self, r: &Matrix3<f64>) -> Self {
        let t = |x: &Tensor| tensor(&(r * matrix(x) * r.transpose()));
        let v = |x: &[f64; 3]| (r * Vector3::from(*x)).into();
        Self {
            shear: t(&self.shear),
            n: t(&self.n),
            a: v(&self.a),
            rotation: v(&self.rotation),
        }
    }
    pub fn group(&self) -> BianchiGroup {
        let n = &self.n;
        BianchiGroup::new(
            [n[0][0], n[1][1], n[2][2], n[0][1], n[0][2], n[1][2]],
            self.a,
        )
    }
    /// Finite symmetric N, symmetric trace-free Sigma and the Jacobi identity.
    pub fn validate(&self) -> Result<(), String> {
        let s = matrix(&self.shear);
        let n = matrix(&self.n);
        let a = Vector3::from(self.a);
        if !s
            .iter()
            .chain(n.iter())
            .chain(a.iter())
            .all(|x| x.is_finite())
            || !self.rotation.iter().all(|x| x.is_finite())
        {
            return Err("Lie data must be finite".into());
        }
        if (s - s.transpose()).amax() > 1e-12 * (1.0 + s.amax())
            || s.trace().abs() > 1e-12 * (1.0 + s.amax())
            || (n - n.transpose()).amax() > 1e-12 * (1.0 + n.amax())
        {
            return Err("Sigma must be symmetric trace-free and N symmetric".into());
        }
        if (n * a).norm() > 1e-12 * (1.0 + n.norm() * a.norm()) {
            return Err("Lie data violate the Jacobi identity N A = 0".into());
        }
        Ok(())
    }
}

/// Families accepted by [`canonical_diagonal`]; VIh and VIIh also accept ":h".
pub const FAMILIES: [&str; 13] = [
    "FLRW", "I", "II", "III", "IV", "V", "VI0", "VIh", "VIstar", "VII0", "VIIh", "VIII", "IX",
];

/// Unit-scale canonical representative (original BASS `bianchi/algebra.py`
/// CANONICAL; Dossier II table): diagonal N eigenvalues and A along e_1, with
/// h = A^2/(n2 n3). III = VI_-1, VIstar = VI*_-1/9; "VIh:h", "VIIh:h" select h
/// (defaults -1/4 and +1/4).
pub fn canonical_diagonal(family: &str) -> Result<([f64; 3], f64), String> {
    match family {
        "I" | "FLRW" => Ok(([0., 0., 0.], 0.)),
        "II" => Ok(([1., 0., 0.], 0.)),
        "III" => Ok(([0., 1., -1.], 1.)),
        "IV" => Ok(([0., 0., 1.], 1.)),
        "V" => Ok(([0., 0., 0.], 1.)),
        "VI0" => Ok(([0., 1., -1.], 0.)),
        "VIstar" => Ok(([0., 3., -3.], 1.)),
        "VII0" => Ok(([0., 1., 1.], 0.)),
        "VIII" => Ok(([-1., 1., 1.], 0.)),
        "IX" => Ok(([1., 1., 1.], 0.)),
        _ => {
            let (name, arg) = family.split_once(':').unwrap_or((family, ""));
            let sign = match name {
                "VIh" => -1.,
                "VIIh" => 1.,
                _ => return Err(format!("unknown Bianchi family {family}")),
            };
            let h = if !family.contains(':') {
                0.25 * sign
            } else {
                arg.parse::<f64>()
                    .map_err(|_| format!("invalid h in {family}"))?
            };
            if !h.is_finite() || sign * h <= 0. {
                return Err(format!("invalid h in {family}"));
            }
            Ok(([0., 1., sign], h.abs().sqrt()))
        }
    }
}

/// Canonical (N, A) of a family, multiplied by `scale` and actively rotated by `r`.
pub fn canonical_algebra(
    family: &str,
    scale: f64,
    r: &Matrix3<f64>,
) -> Result<(Tensor, [f64; 3]), String> {
    if !scale.is_finite() {
        return Err("structure-constant scale must be finite".into());
    }
    let (diag, a1) = canonical_diagonal(family)?;
    let n = r * Matrix3::from_diagonal(&Vector3::from(diag)) * r.transpose() * scale;
    let a = r * Vector3::new(a1, 0., 0.) * scale;
    Ok((tensor(&(0.5 * (n + n.transpose()))), a.into()))
}

/// Type invariants of Lie data, preserved by the exact (congruence) evolution.
#[derive(Clone, Debug)]
pub struct LieInvariants {
    pub name: &'static str,
    pub class_b: bool,
    /// h = A^2/(n2 n3) in class B when n2 n3 != 0 (h = 1/kappa).
    pub h: Option<f64>,
    pub exceptional: bool,
    /// Eigenvalues of N in increasing order.
    pub n_eigenvalues: [f64; 3],
    pub a_norm: f64,
    pub trace_n: f64,
    pub jacobi_norm: f64,
}

pub fn invariants(n: &Tensor, a: &[f64; 3]) -> LieInvariants {
    let g = BianchiGroup::new([n[0][0], n[1][1], n[2][2], n[0][1], n[0][2], n[1][2]], *a);
    let c = g.classify();
    let mut ev: Vec<f64> = matrix(n)
        .symmetric_eigen()
        .eigenvalues
        .iter()
        .copied()
        .collect();
    ev.sort_by(|x, y| x.partial_cmp(y).unwrap_or(std::cmp::Ordering::Equal));
    let j = g.jacobi_residual();
    LieInvariants {
        name: c.name,
        class_b: c.class == crate::geom::group::GroupClass::B,
        h: c.kappa.filter(|k| *k != 0.0).map(|k| 1.0 / k),
        exceptional: c.exceptional,
        n_eigenvalues: [ev[0], ev[1], ev[2]],
        a_norm: Vector3::from(*a).norm(),
        trace_n: matrix(n).trace(),
        jacobi_norm: Vector3::from(j).norm(),
    }
}

/// Y_LM(e) for L <= 2 (Condon-Shortley), flat index L*L + L + M.
pub fn ylm2(e: [f64; 3]) -> [C64; POTENTIAL_MODES] {
    let [x, y, z] = e;
    let p = C64::new(x, y);
    let mut out = [C64::new(0., 0.); POTENTIAL_MODES];
    out[0] = C64::new(1.0 / (4.0 * PI).sqrt(), 0.);
    out[potential_index(1, 0)] = C64::new((3.0 / (4.0 * PI)).sqrt() * z, 0.);
    out[potential_index(1, 1)] = -(3.0 / (8.0 * PI)).sqrt() * p;
    out[potential_index(1, -1)] = (3.0 / (8.0 * PI)).sqrt() * p.conj();
    out[potential_index(2, 0)] = C64::new((5.0 / (16.0 * PI)).sqrt() * (3.0 * z * z - 1.0), 0.);
    out[potential_index(2, 1)] = -(15.0 / (8.0 * PI)).sqrt() * z * p;
    out[potential_index(2, -1)] = (15.0 / (8.0 * PI)).sqrt() * z * p.conj();
    out[potential_index(2, 2)] = (15.0 / (32.0 * PI)).sqrt() * p * p;
    out[potential_index(2, -2)] = (15.0 / (32.0 * PI)).sqrt() * p.conj() * p.conj();
    out
}

/// Y_LM coefficients of the constant c.
pub fn constant_coefficients(c: f64) -> [C64; POTENTIAL_MODES] {
    let mut out = [C64::new(0., 0.); POTENTIAL_MODES];
    out[0] = C64::new(c * (4.0 * PI).sqrt(), 0.);
    out
}

/// Y_LM coefficients of v.e.
pub fn linear_coefficients(v: &[f64; 3]) -> [C64; POTENTIAL_MODES] {
    let mut out = [C64::new(0., 0.); POTENTIAL_MODES];
    let c1 = (2.0 * PI / 3.0).sqrt();
    out[potential_index(1, 0)] = C64::new((4.0 * PI / 3.0).sqrt() * v[2], 0.);
    out[potential_index(1, 1)] = -c1 * C64::new(v[0], -v[1]);
    out[potential_index(1, -1)] = c1 * C64::new(v[0], v[1]);
    out
}

/// Y_LM coefficients of X:ee for a symmetric X (its trace enters L = 0).
pub fn quadratic_coefficients(x: &Tensor) -> [C64; POTENTIAL_MODES] {
    let t = x[0][0] + x[1][1] + x[2][2];
    let mut out = constant_coefficients(t / 3.0);
    let c1 = (8.0 * PI / 15.0).sqrt();
    let c2 = (2.0 * PI / 15.0).sqrt();
    out[potential_index(2, 0)] = C64::new(2.0 * (PI / 5.0).sqrt() * (x[2][2] - t / 3.0), 0.);
    out[potential_index(2, 1)] = -c1 * C64::new(x[0][2], -x[1][2]);
    out[potential_index(2, -1)] = c1 * C64::new(x[0][2], x[1][2]);
    out[potential_index(2, 2)] = c2 * C64::new(x[0][0] - x[1][1], -2.0 * x[0][1]);
    out[potential_index(2, -2)] = c2 * C64::new(x[0][0] - x[1][1], 2.0 * x[0][1]);
    out
}

/// Y_LM coefficients (L <= 2) of the photon-generator potentials. `r` is the
/// anisotropic part -Sigma:ee of d ln E/d eta; the isotropic -1 is integrated
/// exactly by the transport.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct PhotonPotentials {
    pub r: [C64; POTENTIAL_MODES],
    pub u: [C64; POTENTIAL_MODES],
    pub z: [C64; POTENTIAL_MODES],
    pub omega: [C64; POTENTIAL_MODES],
}

impl PhotonPotentials {
    pub fn lerp(&self, other: &Self, f: f64) -> Self {
        let b = |x: &[C64; POTENTIAL_MODES], y: &[C64; POTENTIAL_MODES]| {
            std::array::from_fn(|k| x[k] + (y[k] - x[k]) * f)
        };
        Self {
            r: b(&self.r, &other.r),
            u: b(&self.u, &other.u),
            z: b(&self.z, &other.z),
            omega: b(&self.omega, &other.omega),
        }
    }
}

fn add(a: [C64; POTENTIAL_MODES], b: [C64; POTENTIAL_MODES], sb: f64) -> [C64; POTENTIAL_MODES] {
    std::array::from_fn(|k| a[k] + b[k] * sb)
}

/// Type constants of the photon sector for Hubble-normalized Lie data.
pub fn photon_potentials(d: &LieData) -> PhotonPotentials {
    let n = matrix(&d.n);
    let tr = n.trace();
    let n_tf = tensor(&(n - Matrix3::identity() * (tr / 3.0)));
    let zero = [C64::new(0., 0.); POTENTIAL_MODES];
    let sigma = quadratic_coefficients(&d.shear);
    let twist = quadratic_coefficients(&n_tf);
    let a = linear_coefficients(&d.a);
    let w = linear_coefficients(&d.rotation);
    PhotonPotentials {
        r: add(zero, sigma, -1.0),
        u: add(add(zero, sigma, -0.5), a, -1.0),
        z: add(add(zero, twist, -0.5), w, -1.0),
        omega: add(add(w, twist, 1.0), constant_coefficients(-tr / 6.0), 1.0),
    }
}

/// Pointwise (R~, U, Z, omega) at unit direction e, from the tensors directly.
pub fn potential_values(d: &LieData, e: [f64; 3]) -> [f64; 4] {
    let v = Vector3::from(e);
    let s = matrix(&d.shear);
    let n = matrix(&d.n);
    let tr = n.trace();
    let n_tf = n - Matrix3::identity() * (tr / 3.0);
    let see = v.dot(&(s * v));
    let tee = v.dot(&(n_tf * v));
    let a = Vector3::from(d.a).dot(&v);
    let w = Vector3::from(d.rotation).dot(&v);
    [-see, -0.5 * see - a, -0.5 * tee - w, w + tee - tr / 6.0]
}

/// Sum of Y_LM coefficients at e (real part; the potentials are real).
pub fn evaluate(coeff: &[C64; POTENTIAL_MODES], e: [f64; 3]) -> f64 {
    let y = ylm2(e);
    coeff.iter().zip(y.iter()).map(|(c, y)| (c * y).re).sum()
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::runtime::typeii_photon_host::typeii_polarized_liouville::{
        liouville_coefficients, HomogeneousRayBackground,
    };
    use nalgebra::Rotation3;

    fn directions() -> Vec<[f64; 3]> {
        let mut out = Vec::new();
        for i in 0..7 {
            for j in 0..11 {
                let z = -0.95 + 1.9 * i as f64 / 6.0;
                let p = 0.3 + 2.0 * PI * j as f64 / 11.0;
                let r = (1.0 - z * z).sqrt();
                out.push([r * p.cos(), r * p.sin(), z]);
            }
        }
        out
    }

    fn generic(rotate: f64) -> LieData {
        let r = Rotation3::from_euler_angles(0.31 * rotate, -0.27, 0.6 * rotate);
        let n = r.matrix()
            * Matrix3::from_diagonal(&Vector3::new(0., 0.4, -0.25))
            * r.matrix().transpose();
        let a = r * Vector3::new(0.17, 0., 0.);
        LieData {
            shear: [
                [0.12, 0.05, -0.03],
                [0.05, -0.07, 0.04],
                [-0.03, 0.04, -0.05],
            ],
            n: tensor(&n),
            a: a.into(),
            rotation: [0.03, -0.08, 0.11],
        }
    }

    #[test]
    fn canonical_families_classify_after_rotation_and_keep_h() {
        let expect = [
            ("I", "I"),
            ("II", "II"),
            ("III", "III"),
            ("IV", "IV"),
            ("V", "V"),
            ("VI0", "VI_0"),
            ("VIh", "VI_h"),
            ("VIh:-0.6", "VI_h"),
            ("VIstar", "VI*_-1/9"),
            ("VII0", "VII_0"),
            ("VIIh", "VII_h"),
            ("VIIh:0.9", "VII_h"),
            ("VIII", "VIII"),
            ("IX", "IX"),
        ];
        let r = Rotation3::from_euler_angles(0.4, -1.1, 2.3);
        for (family, name) in expect {
            let (n, a) = canonical_algebra(family, 0.3, r.matrix()).unwrap();
            let inv = invariants(&n, &a);
            assert_eq!(inv.name, name, "{family}");
            assert!(inv.jacobi_norm < 1e-15);
            if let Some((_, h)) = family.split_once(':') {
                assert!((inv.h.unwrap() - h.parse::<f64>().unwrap()).abs() < 1e-12);
            }
        }
        let (n, a) = canonical_algebra("VIstar", 0.3, &Matrix3::identity()).unwrap();
        assert!((invariants(&n, &a).h.unwrap() + 1.0 / 9.0).abs() < 1e-15);
        assert!(canonical_algebra("X", 1.0, &Matrix3::identity()).is_err());
    }

    #[test]
    fn potentials_reproduce_pointwise_values_and_liouville_field() {
        for rotate in [0.0, 1.0] {
            let d = generic(rotate);
            d.validate().unwrap();
            let p = photon_potentials(&d);
            let bg = HomogeneousRayBackground {
                expansion: 1.0,
                shear: d.shear,
                structure_n: d.n,
                class_b_a: d.a,
                triad_rotation: d.rotation,
            };
            for e in directions() {
                let v = potential_values(&d, e);
                let from_coeff = [&p.r, &p.u, &p.z, &p.omega].map(|c| evaluate(c, e));
                for k in 0..4 {
                    assert!(
                        (v[k] - from_coeff[k]).abs() < 2e-15,
                        "{k}: {} {}",
                        v[k],
                        from_coeff[k]
                    );
                }
                let lc = liouville_coefficients(e, &bg).unwrap();
                // d ln E/d eta = -1 + R~ and omega = g.e (screen connection rate).
                assert!((lc.log_energy_rate - (-1.0 + v[0])).abs() < 1e-15);
                assert!((lc.screen_connection_rate - v[3]).abs() < 1e-15);
                // V = grad U + e x grad Z with the analytic sphere gradients.
                let ev = Vector3::from(e);
                let proj = |w: Vector3<f64>| w - ev * ev.dot(&w);
                let s = matrix(&d.shear);
                let n = matrix(&d.n);
                let n_tf = n - Matrix3::identity() * (n.trace() / 3.0);
                let grad_u = proj(-(s * ev) - Vector3::from(d.a));
                let grad_z = proj(-(n_tf * ev) - Vector3::from(d.rotation));
                let field = grad_u + ev.cross(&grad_z);
                assert!((field - Vector3::from(lc.direction_rate)).norm() < 1e-15);
            }
        }
    }
}
