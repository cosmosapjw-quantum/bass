//! Opt-in BASS original Type-II callback bridge, no RF-01/production dispatch mutation.
//! Authority: original 5-component generated source in generated/rust/typeii/typeii_background.rs.
//! Units: Hubble-normalized WE shear/curvature, derivative d/dtau with d tau = H dt.
//! Physical domain: 0 < gamma < 2, N1>0, |v2|<1, Omega>0, Codazzi=0.
//! N1=0 (Type I boundary) is deliberately excluded from this local chart.
use crate::core::conventions::tracefree_from_5;
use crate::geom::group::BianchiGroup;
use nalgebra::{Matrix3, Vector3};

#[path = "../../../generated/rust/typeii/typeii_background.rs"]
mod original_background;

const SQRT3: f64 = 1.7320508075688772935;
const TOL: f64 = 1.0e-12;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum WEFrame {
    Normal,
    ElectronRest,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum WENormalization {
    HubbleWE,
    Other,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum WEClock {
    HubbleTau,
    ProperSeconds,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum TypeIIHostError {
    NonFinite,
    InvalidGamma,
    SuperluminalTilt,
    TypeIBoundary,
    NonPositiveMatter,
    WrongFrame,
    WrongNormalization,
    WrongClock,
    OffTypeIISlice,
    CodazziViolation,
    GaussViolation,
    NonFiniteCallback,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct TypeIIState5 {
    /// (SigmaPlus, SigmaMinus, Sigma13, N1, v2) in BASS/WE normalization.
    pub x: [f64; 5],
    pub gamma: f64,
}

#[derive(Clone, Debug)]
pub struct TypeIIHostState {
    /// REAL RustCore generic STF shear matrix from tracefree_from_5.
    pub shear: Matrix3<f64>,
    /// REAL RustCore geometry BianchiGroup (n11,n22,n33,n12,n13,n23), a3.
    pub group: BianchiGroup,
    pub velocity: Vector3<f64>,
    pub omega: f64,
    pub gamma: f64,
    pub frame: WEFrame,
    pub normalization: WENormalization,
    pub clock: WEClock,
}

impl TypeIIState5 {
    pub fn omega(self) -> Result<f64, TypeIIHostError> {
        let [sp, sm, s13, n1, v2] = self.x;
        if !self.x.iter().all(|v| v.is_finite()) || !self.gamma.is_finite() {
            return Err(TypeIIHostError::NonFinite);
        }
        if !(self.gamma > 0.0 && self.gamma < 2.0) {
            return Err(TypeIIHostError::InvalidGamma);
        }
        if !(v2.abs() < 1.0) {
            return Err(TypeIIHostError::SuperluminalTilt);
        }
        if !(n1 > 0.0) {
            return Err(TypeIIHostError::TypeIBoundary);
        }
        let omega = 1.0 - sp * sp - sm * sm - s13 * s13 - n1 * n1 / 12.0;
        if !(omega > 0.0) {
            return Err(TypeIIHostError::NonPositiveMatter);
        }
        Ok(omega)
    }

    pub fn codazzi(self) -> Result<f64, TypeIIHostError> {
        let omega = self.omega()?;
        let [_, _, s13, n1, v2] = self.x;
        let gp = 1.0 + (self.gamma - 1.0) * v2 * v2;
        Ok(-SQRT3 * n1 * s13 - 3.0 * self.gamma * omega * v2 / gp)
    }

    pub fn validate(self) -> Result<f64, TypeIIHostError> {
        let omega = self.omega()?;
        if self.codazzi()?.abs() > TOL {
            return Err(TypeIIHostError::CodazziViolation);
        }
        Ok(omega)
    }

    /// Positive-energy four-free-coordinate chart; fixed gamma, N1>0 only.
    pub fn from_four(
        sp: f64,
        sm: f64,
        n1: f64,
        v2: f64,
        gamma: f64,
    ) -> Result<Self, TypeIIHostError> {
        if ![sp, sm, n1, v2, gamma].iter().all(|v| v.is_finite()) {
            return Err(TypeIIHostError::NonFinite);
        }
        if !(gamma > 0.0 && gamma < 2.0) {
            return Err(TypeIIHostError::InvalidGamma);
        }
        if !(v2.abs() < 1.0) {
            return Err(TypeIIHostError::SuperluminalTilt);
        }
        if !(n1 > 0.0) {
            return Err(TypeIIHostError::TypeIBoundary);
        }
        let a = 1.0 - sp * sp - sm * sm - n1 * n1 / 12.0;
        if !(a > 0.0) {
            return Err(TypeIIHostError::NonPositiveMatter);
        }
        let gp = 1.0 + (gamma - 1.0) * v2 * v2;
        let beta = 3.0 * gamma * gamma * v2 * v2 / (n1 * n1 * gp * gp);
        let om = 2.0 * a / (1.0 + (1.0 + 4.0 * beta * a).sqrt());
        let s13 = -SQRT3 * gamma * om * v2 / (n1 * gp);
        let state = Self {
            x: [sp, sm, s13, n1, v2],
            gamma,
        };
        state.validate()?;
        Ok(state)
    }

    pub fn to_host(self) -> Result<TypeIIHostState, TypeIIHostError> {
        let omega = self.validate()?;
        let [sp, sm, s13, n1, v2] = self.x;
        let shear = tracefree_from_5(-2.0 * sp, sp + SQRT3 * sm, 0.0, SQRT3 * s13, 0.0);
        let group = BianchiGroup::new([n1, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0; 3]);
        Ok(TypeIIHostState {
            shear,
            group,
            velocity: Vector3::new(0.0, v2, 0.0),
            omega,
            gamma: self.gamma,
            frame: WEFrame::Normal,
            normalization: WENormalization::HubbleWE,
            clock: WEClock::HubbleTau,
        })
    }

    /// Physical tangent lift from (delta SigmaPlus, delta SigmaMinus, delta N1, delta v2).
    /// Solves dCodazzi=0 after Gauss elimination, not an arbitrary 5D perturbation.
    pub fn tangent_lift(self, du: [f64; 4]) -> Result<[f64; 5], TypeIIHostError> {
        let omega = self.validate()?;
        if !du.iter().all(|v| v.is_finite()) {
            return Err(TypeIIHostError::NonFinite);
        }
        let [sp, sm, s13, n1, v2] = self.x;
        let gp = 1.0 + (self.gamma - 1.0) * v2 * v2;
        let c_s = -SQRT3 * n1 + 6.0 * self.gamma * s13 * v2 / gp;
        // On the positive-root chart this is -sqrt(3) N1 (1+2 beta Omega) < 0.
        if !(c_s < 0.0 && c_s.is_finite()) {
            return Err(TypeIIHostError::CodazziViolation);
        }
        let c_sp = 6.0 * self.gamma * sp * v2 / gp;
        let c_sm = 6.0 * self.gamma * sm * v2 / gp;
        let c_n = -SQRT3 * s13 + 0.5 * self.gamma * n1 * v2 / gp;
        let c_v = -3.0 * self.gamma * omega * (1.0 - (self.gamma - 1.0) * v2 * v2) / (gp * gp);
        let ds = -(c_sp * du[0] + c_sm * du[1] + c_n * du[2] + c_v * du[3]) / c_s;
        if !ds.is_finite() {
            return Err(TypeIIHostError::NonFinite);
        }
        Ok([du[0], du[1], ds, du[2], du[3]])
    }
}

impl TypeIIHostState {
    pub fn to_typeii(&self) -> Result<TypeIIState5, TypeIIHostError> {
        if self.frame != WEFrame::Normal {
            return Err(TypeIIHostError::WrongFrame);
        }
        if self.normalization != WENormalization::HubbleWE {
            return Err(TypeIIHostError::WrongNormalization);
        }
        if self.clock != WEClock::HubbleTau {
            return Err(TypeIIHostError::WrongClock);
        }
        if !self
            .shear
            .iter()
            .chain(self.group.n.iter())
            .chain(self.group.a.iter())
            .chain(self.velocity.iter())
            .chain([self.omega, self.gamma].iter())
            .all(|v| v.is_finite())
        {
            return Err(TypeIIHostError::NonFinite);
        }
        if self.group.n[1..]
            .iter()
            .chain(self.group.a.iter())
            .any(|v| v.abs() > TOL)
            || self.velocity[0].abs() > TOL
            || self.velocity[2].abs() > TOL
            || self.shear[(0, 1)].abs() > TOL
            || self.shear[(1, 2)].abs() > TOL
        {
            return Err(TypeIIHostError::OffTypeIISlice);
        }
        let s5 = [
            self.shear[(0, 0)],
            self.shear[(1, 1)],
            self.shear[(0, 1)],
            self.shear[(0, 2)],
            self.shear[(1, 2)],
        ];
        let reconstructed = tracefree_from_5(s5[0], s5[1], s5[2], s5[3], s5[4]);
        if self
            .shear
            .iter()
            .zip(reconstructed.iter())
            .any(|(a, b)| (a - b).abs() > TOL)
        {
            return Err(TypeIIHostError::OffTypeIISlice);
        }
        let sp = -self.shear[(0, 0)] / 2.0;
        let sm = (self.shear[(1, 1)] - sp) / SQRT3;
        let state = TypeIIState5 {
            x: [
                sp,
                sm,
                self.shear[(0, 2)] / SQRT3,
                self.group.n[0],
                self.velocity[1],
            ],
            gamma: self.gamma,
        };
        let omega = state.validate()?;
        if (omega - self.omega).abs() > TOL {
            return Err(TypeIIHostError::GaussViolation);
        }
        // Real RustCore spatial Ricci: K=-R3/(6 H^2)=N1^2/12 for Type II.
        let (k, _) = self.group.curvature();
        if (k - self.group.n[0] * self.group.n[0] / 12.0).abs() > TOL {
            return Err(TypeIIHostError::OffTypeIISlice);
        }
        Ok(state)
    }
}

/// Opt-in production-source callback, intentionally not installed as an RF-01 dispatcher.
/// Gamma is held fixed; input clock is dimensionless d tau=H dt.
/// The JVP acts in ambient 5D; use tangent_lift for physical chart variations.
pub struct OriginalTypeIIBackground;
impl OriginalTypeIIBackground {
    pub const FORMULA_SHA256: &'static str = original_background::FORMULA_AUTHORITY_SHA256;
    pub fn rhs(host: &TypeIIHostState) -> Result<[f64; 5], TypeIIHostError> {
        let s = host.to_typeii()?;
        let out = original_background::rhs(&s.x, s.gamma);
        if !out.iter().all(|x| x.is_finite()) {
            return Err(TypeIIHostError::NonFiniteCallback);
        }
        Ok(out)
    }
    pub fn jvp(host: &TypeIIHostState, d: [f64; 5]) -> Result<[f64; 5], TypeIIHostError> {
        let s = host.to_typeii()?;
        if !d.iter().all(|x| x.is_finite()) {
            return Err(TypeIIHostError::NonFinite);
        }
        let out = original_background::jvp(&s.x, s.gamma, &d);
        if !out.iter().all(|x| x.is_finite()) {
            return Err(TypeIIHostError::NonFiniteCallback);
        }
        Ok(out)
    }
    pub fn physical_rhs_four(host: &TypeIIHostState) -> Result<[f64; 4], TypeIIHostError> {
        let v = Self::rhs(host)?;
        Ok([v[0], v[1], v[3], v[4]])
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn sample() -> TypeIIState5 {
        TypeIIState5::from_four(0.2375, 0.0, 0.865, 0.05, 1.3).unwrap()
    }
    fn gap(x: &[f64; 5], y: &[f64; 5]) -> f64 {
        x.iter()
            .zip(y.iter())
            .map(|(a, b)| (a - b).abs())
            .fold(0.0, f64::max)
    }
    #[test]
    fn actual_rustcore_geometry_roundtrip() {
        let s = sample();
        let h = s.to_host().unwrap();
        assert_eq!(h.group.classify().name, "II");
        assert!((h.group.curvature().0 - s.x[3].powi(2) / 12.0).abs() < 1e-13);
        assert!(gap(&s.x, &h.to_typeii().unwrap().x) < 2e-15);
        assert!(h.group.jacobi_residual().iter().all(|v| v.abs() < 1e-15));
    }
    #[test]
    fn original_generated_callback_is_actually_called() {
        let s = sample();
        let h = s.to_host().unwrap();
        let rhs = OriginalTypeIIBackground::rhs(&h).unwrap();
        let source = original_background::rhs(&s.x, s.gamma);
        assert_eq!(rhs, source);
        let d = [1.0, -2.0, 3.0, -4.0, 5.0];
        let jvp = OriginalTypeIIBackground::jvp(&h, d).unwrap();
        assert_eq!(jvp, original_background::jvp(&s.x, s.gamma, &d));
        assert_eq!(
            OriginalTypeIIBackground::FORMULA_SHA256,
            "3ecf0dbc8b47a8af83da81e9ed37823b6922e139e420c5bfa2e071b6bbabe361"
        );
    }
    #[test]
    fn tangent_lift_matches_finite_chart_difference() {
        let s = sample();
        let du = [0.5, -0.3, 0.2, 0.1];
        let lift = s.tangent_lift(du).unwrap();
        let h = 1e-7;
        let xp = TypeIIState5::from_four(
            s.x[0] + h * du[0],
            s.x[1] + h * du[1],
            s.x[3] + h * du[2],
            s.x[4] + h * du[3],
            s.gamma,
        )
        .unwrap();
        let xm = TypeIIState5::from_four(
            s.x[0] - h * du[0],
            s.x[1] - h * du[1],
            s.x[3] - h * du[2],
            s.x[4] - h * du[3],
            s.gamma,
        )
        .unwrap();
        let fd = std::array::from_fn::<f64, 5, _>(|i| (xp.x[i] - xm.x[i]) / (2.0 * h));
        assert!(gap(&lift, &fd) < 2e-9, "{lift:?} {fd:?}");
    }
    #[test]
    fn original_typeii_rhs_is_tangent_to_codazzi() {
        for (sp, sm, n1, v2) in [
            (0.2375, 0.0, 0.865, 0.05),
            (0.08, -0.03, 0.8, -0.2),
            (0.03, 0.04, 1.0, 0.0),
        ] {
            let s = TypeIIState5::from_four(sp, sm, n1, v2, 1.3).unwrap();
            let h = s.to_host().unwrap();
            let rhs = OriginalTypeIIBackground::rhs(&h).unwrap();
            let lift = s.tangent_lift([rhs[0], rhs[1], rhs[3], rhs[4]]).unwrap();
            assert!(
                (lift[2] - rhs[2]).abs() < 5e-11,
                "source RHS not tangent: source={} chart={} at {:?}",
                rhs[2],
                lift[2],
                s.x
            );
        }
    }
    #[test]
    fn wrong_metadata_offslice_or_offchart_fails_closed() {
        let h = sample().to_host().unwrap();
        let mut bad = h.clone();
        bad.frame = WEFrame::ElectronRest;
        assert_eq!(bad.to_typeii().unwrap_err(), TypeIIHostError::WrongFrame);
        let mut bad = h.clone();
        bad.clock = WEClock::ProperSeconds;
        assert_eq!(bad.to_typeii().unwrap_err(), TypeIIHostError::WrongClock);
        let mut bad = h.clone();
        bad.normalization = WENormalization::Other;
        assert_eq!(
            bad.to_typeii().unwrap_err(),
            TypeIIHostError::WrongNormalization
        );
        let mut bad = h.clone();
        bad.group.n[1] = 0.1;
        assert_eq!(
            bad.to_typeii().unwrap_err(),
            TypeIIHostError::OffTypeIISlice
        );
        let mut bad = h.clone();
        bad.shear[(0, 2)] = -bad.shear[(0, 2)];
        assert_eq!(
            bad.to_typeii().unwrap_err(),
            TypeIIHostError::OffTypeIISlice
        );
        let mut bad = h.clone();
        bad.omega += 0.01;
        assert_eq!(
            bad.to_typeii().unwrap_err(),
            TypeIIHostError::GaussViolation
        );
        assert_eq!(
            TypeIIState5::from_four(0.0, 0.0, 0.0, 0.1, 1.3).unwrap_err(),
            TypeIIHostError::TypeIBoundary
        );
        assert_eq!(
            TypeIIState5::from_four(0.0, 0.0, 1.0, 1.0, 1.3).unwrap_err(),
            TypeIIHostError::SuperluminalTilt
        );
    }
}
