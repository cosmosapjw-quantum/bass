//! Exceptional class-B initial constraints in geometric length units.
//!
//! This rank-one utility applies only when `A != 0` and `BD-C² = -9A²` within
//! the caller's relative roundoff tolerance. It does not evolve the data or
//! impose material realizability. Every input and returned quantity must fit
//! in finite `f64`; an operation that rounds a nonzero product to zero is
//! rejected when that product is needed for the constraints. Inputs far beyond
//! the useful dynamic range of binary64 can therefore return `NonRepresentable`.

use std::fmt;

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Error {
    InvalidGeometry,
    InvalidTolerance,
    InvalidInput,
    IncompatibleFlux { range_residual: f64 },
    LongitudinalConstraint { residual: f64 },
    ConstraintResidual,
    NegativeHubbleSquare,
    NegativeAmplitudeBudget,
    NonRepresentable,
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{self:?}")
    }
}

impl std::error::Error for Error {}

#[derive(Debug, Clone, Copy)]
pub struct ExceptionalGeometry {
    a: f64,
    b: f64,
    c: f64,
    d: f64,
    scale: f64,
    l: [[f64; 2]; 2], // L / scale
    tolerance: f64,
}

#[derive(Debug, Clone, Copy)]
pub struct TransverseSolution {
    pub shear: [f64; 2],
    pub kernel: [f64; 2],
    pub image_projector: [[f64; 2]; 2],
    pub row_projector: [[f64; 2]; 2],
    pub range_residual: f64,
    pub constraint_residual: [f64; 2],
}

#[derive(Debug, Clone, Copy)]
pub struct CauchyData {
    pub in_plane: [f64; 3], // sigma11, sigma22, sigma23
    pub flux: [f64; 3],
    pub kappa: f64,
    pub rho: f64,
    pub lambda: f64,
}

#[derive(Debug, Clone, Copy)]
pub enum Expansion {
    Expanding,
    Contracting,
}

#[derive(Debug, Clone, Copy)]
pub struct InitialData {
    pub shear: [[f64; 3]; 3],
    pub hubble: f64,
    pub scalar_curvature: f64,
    pub momentum_residual: [f64; 3],
    pub hamiltonian_residual: f64,
}

fn finite(value: f64) -> Result<f64, Error> {
    if value.is_finite() {
        Ok(value)
    } else {
        Err(Error::NonRepresentable)
    }
}

fn product(a: f64, b: f64) -> Result<f64, Error> {
    let out = finite(a * b)?;
    if a != 0.0 && b != 0.0 && out == 0.0 {
        return Err(Error::NonRepresentable);
    }
    Ok(out)
}

fn sum(values: &[f64]) -> Result<f64, Error> {
    let mut out = 0.0;
    for &x in values {
        out = finite(out + x)?;
    }
    Ok(out)
}

fn norm2(x: f64, y: f64) -> Result<f64, Error> {
    finite(x.hypot(y))
}

fn tolerance_bound(tolerance: f64, magnitudes: &[f64]) -> Result<f64, Error> {
    let scale = sum(magnitudes)?;
    // Allow arithmetic roundoff in a sum of a few terms, including when the
    // requested geometric tolerance is zero. There is no dimensional floor.
    product(tolerance.max(32.0 * f64::EPSILON), scale)
}

impl ExceptionalGeometry {
    pub fn new(a: f64, b: f64, c: f64, d: f64, tolerance: f64) -> Result<Self, Error> {
        if ![a, b, c, d].iter().all(|v| v.is_finite()) || a == 0.0 {
            return Err(Error::InvalidGeometry);
        }
        if !tolerance.is_finite() || !(0.0..=1e-6).contains(&tolerance) {
            return Err(Error::InvalidTolerance);
        }
        let scale = a.abs().max(b.abs()).max(c.abs()).max(d.abs());
        let (an, bn, cn, dn) = (a / scale, b / scale, c / scale, d / scale);
        if [a, b, c, d]
            .into_iter()
            .zip([an, bn, cn, dn])
            .any(|(original, normalized)| original != 0.0 && normalized == 0.0)
        {
            return Err(Error::NonRepresentable);
        }
        let bd = bn * dn;
        let cc = cn * cn;
        let aa = 9.0 * an * an;
        let branch = bd - cc + aa;
        let branch_scale = bd.abs() + cc + aa;
        if branch_scale == 0.0 || branch.abs() > tolerance * branch_scale {
            return Err(Error::InvalidGeometry);
        }
        let l = [[-(3.0 * an + cn), -dn], [bn, cn - 3.0 * an]];
        if !l.iter().flatten().all(|v| v.is_finite()) {
            return Err(Error::NonRepresentable);
        }
        Ok(Self {
            a,
            b,
            c,
            d,
            scale,
            l,
            tolerance,
        })
    }

    fn validate_data(data: CauchyData) -> Result<(), Error> {
        if !data
            .in_plane
            .iter()
            .chain(data.flux.iter())
            .all(|v| v.is_finite())
            || !data.kappa.is_finite()
            || data.kappa <= 0.0
            || !data.rho.is_finite()
            || data.rho < 0.0
            || !data.lambda.is_finite()
        {
            return Err(Error::InvalidInput);
        }
        Ok(())
    }

    fn longitudinal(&self, data: CauchyData) -> Result<f64, Error> {
        let [s11, s22, s23] = data.in_plane;
        let terms = [
            product(-3.0 * self.a, s11)?,
            product(self.c, sum(&[s11, product(2.0, s22)?])?)?,
            product(finite(self.d - self.b)?, s23)?,
            product(data.kappa, data.flux[0])?,
        ];
        let residual = sum(&terms)?;
        let bound = tolerance_bound(self.tolerance, &terms.map(f64::abs))?;
        if residual.abs() > bound {
            return Err(Error::LongitudinalConstraint { residual });
        }
        Ok(residual)
    }

    fn scalar_curvature(&self) -> Result<f64, Error> {
        // Evaluate the quadratic form before multiplying by scale².
        let a = self.a / self.scale;
        let c = self.c / self.scale;
        let bd = self.b / self.scale - self.d / self.scale;
        let normalized = -6.0 * a * a - 0.5 * bd * bd - 2.0 * c * c;
        product(product(normalized, self.scale)?, self.scale)
    }

    pub fn solve_transverse(
        &self,
        flux: [f64; 2],
        kappa: f64,
        chi: f64,
    ) -> Result<TransverseSolution, Error> {
        if !flux.iter().all(|v| v.is_finite())
            || !kappa.is_finite()
            || kappa <= 0.0
            || !chi.is_finite()
        {
            return Err(Error::InvalidInput);
        }
        let l = self.l;
        let s_normalized = norm2(norm2(l[0][0], l[0][1])?, norm2(l[1][0], l[1][1])?)?;
        if s_normalized == 0.0 {
            return Err(Error::NonRepresentable);
        }
        let singular = product(self.scale, s_normalized)?;
        let col0 = norm2(l[0][0], l[1][0])?;
        let col1 = norm2(l[0][1], l[1][1])?;
        let col = if col0 >= col1 { 0 } else { 1 };
        let col_norm = if col == 0 { col0 } else { col1 };
        if col_norm == 0.0 {
            return Err(Error::NonRepresentable);
        }
        let u = [l[0][col] / col_norm, l[1][col] / col_norm];
        // The right singular vector carries the sign of the chosen column.
        let mut v = [
            (l[0][0] * u[0] + l[1][0] * u[1]) / s_normalized,
            (l[0][1] * u[0] + l[1][1] * u[1]) / s_normalized,
        ];
        let vnorm = norm2(v[0], v[1])?;
        if vnorm == 0.0 {
            return Err(Error::NonRepresentable);
        }
        v = [v[0] / vnorm, v[1] / vnorm];
        let mut kernel = [-v[1], v[0]];
        let preferred = if kernel[0].abs() >= kernel[1].abs() {
            0
        } else {
            1
        };
        if kernel[preferred].is_sign_negative() {
            kernel = [-kernel[0], -kernel[1]];
        }
        let image_projector = [[u[0] * u[0], u[0] * u[1]], [u[1] * u[0], u[1] * u[1]]];
        let row_projector = [[v[0] * v[0], v[0] * v[1]], [v[1] * v[0], v[1] * v[1]]];

        let qscale = flux[0].abs().max(flux[1].abs());
        let qn = if qscale == 0.0 {
            [0.0; 2]
        } else {
            [flux[0] / qscale, flux[1] / qscale]
        };
        // Check before multiplying by kappa: tiny incompatible flux must not
        // disappear when the physical forcing underflows.
        let perpendicular = u[1] * qn[0] - u[0] * qn[1];
        let range_bound = self.tolerance.max(32.0 * f64::EPSILON) * norm2(qn[0], qn[1])?;
        if perpendicular.abs() > range_bound {
            let range_residual = product(product(kappa, qscale)?, perpendicular.abs())?;
            return Err(Error::IncompatibleFlux { range_residual });
        }
        let forcing = product(kappa, qscale)?;
        let q_parallel = qn[0] * u[0] + qn[1] * u[1];
        let fixed = finite(-forcing / singular * q_parallel)?;
        if forcing != 0.0 && q_parallel != 0.0 && fixed == 0.0 {
            return Err(Error::NonRepresentable);
        }
        let shear = [
            finite(fixed * v[0] + chi * kernel[0])?,
            finite(fixed * v[1] + chi * kernel[1])?,
        ];
        let range_residual = product(forcing, perpendicular.abs())?;
        let mut constraint_residual = [0.0; 2];
        // Residuals refer to the supplied geometry, not its rounded normalized
        // representation used to compute the rank-one decomposition.
        let original_l = [
            [finite(-(3.0 * self.a + self.c))?, -self.d],
            [self.b, finite(self.c - 3.0 * self.a)?],
        ];
        for i in 0..2 {
            let terms = [
                product(original_l[i][0], shear[0])?,
                product(original_l[i][1], shear[1])?,
                product(kappa, flux[i])?,
            ];
            constraint_residual[i] = sum(&terms)?;
            if constraint_residual[i].abs() > tolerance_bound(self.tolerance, &terms.map(f64::abs))?
            {
                return Err(Error::ConstraintResidual);
            }
        }
        Ok(TransverseSolution {
            shear,
            kernel,
            image_projector,
            row_projector,
            range_residual,
            constraint_residual,
        })
    }

    pub fn initial_data(
        &self,
        data: CauchyData,
        chi: f64,
        expansion: Expansion,
    ) -> Result<InitialData, Error> {
        Self::validate_data(data)?;
        let longitudinal = self.longitudinal(data)?;
        let transverse = self.solve_transverse([data.flux[1], data.flux[2]], data.kappa, chi)?;
        let [s11, s22, s23] = data.in_plane;
        let [s12, s13] = transverse.shear;
        let s33 = finite(-sum(&[s11, s22])?)?;
        let shear = [[s11, s12, s13], [s12, s22, s23], [s13, s23, s33]];
        let scalar_curvature = self.scalar_curvature()?;
        let mut norm = 0.0;
        for row in shear {
            for x in row {
                norm = finite(norm + product(x, x)?)?;
            }
        }
        let matter = product(product(2.0, data.kappa)?, data.rho)?;
        let lambda = product(2.0, data.lambda)?;
        let h2 = finite(sum(&[matter, lambda, -scalar_curvature, norm])? / 6.0)?;
        if h2 < 0.0 {
            return Err(Error::NegativeHubbleSquare);
        }
        let unsigned_h = finite(h2.sqrt())?;
        let hubble = match expansion {
            Expansion::Expanding => unsigned_h,
            Expansion::Contracting => -unsigned_h,
        };
        let hamiltonian_terms = [product(6.0, h2)?, scalar_curvature, -matter, -lambda, -norm];
        let hamiltonian_residual = sum(&hamiltonian_terms)?;
        if hamiltonian_residual.abs()
            > tolerance_bound(self.tolerance, &hamiltonian_terms.map(f64::abs))?
        {
            return Err(Error::ConstraintResidual);
        }
        Ok(InitialData {
            shear,
            hubble,
            scalar_curvature,
            momentum_residual: [
                longitudinal,
                transverse.constraint_residual[0],
                transverse.constraint_residual[1],
            ],
            hamiltonian_residual,
        })
    }

    pub fn amplitude_budget(&self, data: CauchyData, hubble: f64) -> Result<f64, Error> {
        Self::validate_data(data)?;
        if !hubble.is_finite() {
            return Err(Error::InvalidInput);
        }
        self.longitudinal(data)?;
        let transverse = self.solve_transverse([data.flux[1], data.flux[2]], data.kappa, 0.0)?;
        let [s11, s22, s23] = data.in_plane;
        let s33 = finite(-sum(&[s11, s22])?)?;
        let d0 = sum(&[
            product(s11, s11)?,
            product(s22, s22)?,
            product(s33, s33)?,
            product(2.0, product(s23, s23)?)?,
        ])?;
        let minimum_norm = sum(&[
            product(transverse.shear[0], transverse.shear[0])?,
            product(transverse.shear[1], transverse.shear[1])?,
        ])?;
        let curvature = self.scalar_curvature()?;
        let matter = product(product(2.0, data.kappa)?, data.rho)?;
        let lambda = product(2.0, data.lambda)?;
        let baseline = finite(sum(&[matter, lambda, -curvature, d0])? / 2.0)?;
        let budget = sum(&[
            product(3.0, product(hubble, hubble)?)?,
            -baseline,
            -minimum_norm,
        ])?;
        if budget < 0.0 {
            return Err(Error::NegativeAmplitudeBudget);
        }
        // A numerically admitted near-branch geometry can support chi=0 but
        // fail its actual Codazzi equations for nonzero kernel amplitude.
        // Do not advertise either sign until both pass the original equations.
        let chi = budget.sqrt();
        self.solve_transverse([data.flux[1], data.flux[2]], data.kappa, chi)?;
        self.solve_transverse([data.flux[1], data.flux[2]], data.kappa, -chi)?;
        Ok(budget)
    }
}

#[cfg(test)]
mod regression_tests {
    use super::*;

    #[test]
    fn normalization_cannot_erase_a_nonzero_geometry_coefficient() {
        let a = 2_f64.powi(500);
        assert_eq!(
            ExceptionalGeometry::new(a, 2_f64.powi(1020), 3.0 * a, 2_f64.powi(-100), 2e-13)
                .unwrap_err(),
            Error::NonRepresentable
        );
    }

    #[test]
    fn positive_budget_cannot_advertise_an_unsupported_near_branch_amplitude() {
        let geometry = ExceptionalGeometry::new(1.0, 0.0, 3.0 + 1e-7, 0.0, 1e-6).unwrap();
        let data = CauchyData {
            in_plane: [0.0; 3],
            flux: [0.0; 3],
            kappa: 1.0,
            rho: 0.0,
            lambda: 0.0,
        };
        assert!(geometry
            .initial_data(data, 0.0, Expansion::Expanding)
            .is_ok());
        assert_eq!(
            geometry.amplitude_budget(data, 3.0),
            Err(Error::ConstraintResidual)
        );
    }
}
