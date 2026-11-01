//! Homogeneous diagonal Bianchi-I geometry and collisionless photon characteristics.
use crate::ForwardError;

fn invalid(tag: &'static str) -> ForwardError {
    ForwardError::InvalidInput(tag)
}

fn positive_finite(x: f64, tag: &'static str) -> Result<f64, ForwardError> {
    if x.is_finite() && x > 0.0 {
        Ok(x)
    } else {
        Err(invalid(tag))
    }
}

fn finite(x: f64, tag: &'static str) -> Result<f64, ForwardError> {
    if x.is_finite() {
        Ok(x)
    } else {
        Err(invalid(tag))
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct GeometrySnapshot {
    pub scale_factors: [f64; 3],
    pub hubble_per_s: [f64; 3],
}

impl GeometrySnapshot {
    pub fn new(scale_factors: [f64; 3], hubble_per_s: [f64; 3]) -> Result<Self, ForwardError> {
        let snapshot = Self {
            scale_factors,
            hubble_per_s,
        };
        snapshot.validate()?;
        Ok(snapshot)
    }

    fn validate(&self) -> Result<(), ForwardError> {
        for a in self.scale_factors {
            positive_finite(a, "BianchiScale")?;
        }
        for h in self.hubble_per_s {
            finite(h, "BianchiHubble")?;
        }
        self.volume_factor()?;
        Ok(())
    }

    pub fn volume_factor(&self) -> Result<f64, ForwardError> {
        for a in self.scale_factors {
            positive_finite(a, "BianchiScale")?;
        }
        for h in self.hubble_per_s {
            finite(h, "BianchiHubble")?;
        }
        let v = self.scale_factors.iter().product();
        positive_finite(v, "BianchiVolume")
    }
}

pub trait GeometryBackground {
    fn snapshot(&self, t: f64) -> Result<GeometrySnapshot, ForwardError>;
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct ConstantHubbleBackground {
    pub initial_scale_factors: [f64; 3],
    pub hubble_per_s: [f64; 3],
}

/// A prescribed axisymmetric Bianchi-I point in proper-time units.
///
/// The two transverse scale factors are `a exp(-b)` and the longitudinal
/// factor is `a exp(2b)`, so the volume remains `a^3`.  This is a geometry
/// adapter only: it supplies neither a physical source nor gas initial data.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct AxisymmetricPoint {
    pub mean_scale_factor: f64,
    pub anisotropy: f64,
    pub mean_hubble_per_s: f64,
    pub shear_per_s: f64,
}

impl AxisymmetricPoint {
    pub fn new(
        mean_scale_factor: f64,
        anisotropy: f64,
        mean_hubble_per_s: f64,
        shear_per_s: f64,
    ) -> Result<Self, ForwardError> {
        positive_finite(mean_scale_factor, "AxisymMeanScale")?;
        finite(anisotropy, "AxisymAnisotropy")?;
        finite(mean_hubble_per_s, "AxisymMeanHubble")?;
        finite(shear_per_s, "AxisymShear")?;
        let point = Self {
            mean_scale_factor,
            anisotropy,
            mean_hubble_per_s,
            shear_per_s,
        };
        point.snapshot()?;
        Ok(point)
    }

    pub fn snapshot(&self) -> Result<GeometrySnapshot, ForwardError> {
        let transverse = positive_finite(
            self.mean_scale_factor * (-self.anisotropy).exp(),
            "AxisymTransverseScale",
        )?;
        let longitudinal = positive_finite(
            self.mean_scale_factor * (2.0 * self.anisotropy).exp(),
            "AxisymLongitudinalScale",
        )?;
        GeometrySnapshot::new(
            [transverse, transverse, longitudinal],
            [
                finite(
                    self.mean_hubble_per_s - self.shear_per_s,
                    "AxisymTransverseHubble",
                )?,
                finite(
                    self.mean_hubble_per_s - self.shear_per_s,
                    "AxisymTransverseHubble",
                )?,
                finite(
                    self.mean_hubble_per_s + 2.0 * self.shear_per_s,
                    "AxisymLongitudinalHubble",
                )?,
            ],
        )
    }
}

/// Analytic prescribed axisymmetric geometry over a finite proper-time domain.
///
/// It deliberately has no `ln(a)` inverse: `H=0` is a valid proper-time
/// background, while an inverse chart would be singular there.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct ConstantAxisymmetricBackground {
    pub reference_time_s: f64,
    pub reference_point: AxisymmetricPoint,
    pub time_domain_s: [f64; 2],
}

impl ConstantAxisymmetricBackground {
    pub fn new(
        reference_time_s: f64,
        reference_point: AxisymmetricPoint,
        time_domain_s: [f64; 2],
    ) -> Result<Self, ForwardError> {
        finite(reference_time_s, "AxisymReferenceTime")?;
        let background = Self {
            reference_time_s,
            reference_point,
            time_domain_s,
        };
        background.validate_time_domain()?;
        Ok(background)
    }

    fn validate_time_domain(&self) -> Result<(), ForwardError> {
        finite(self.time_domain_s[0], "AxisymTimeDomain")?;
        finite(self.time_domain_s[1], "AxisymTimeDomain")?;
        if self.time_domain_s[0] > self.time_domain_s[1] {
            return Err(invalid("AxisymTimeDomain"));
        }
        Ok(())
    }
}

impl GeometryBackground for ConstantAxisymmetricBackground {
    fn snapshot(&self, t: f64) -> Result<GeometrySnapshot, ForwardError> {
        finite(t, "AxisymTime")?;
        self.validate_time_domain()?;
        if t < self.time_domain_s[0] || t > self.time_domain_s[1] {
            return Err(invalid("AxisymTimeDomain"));
        }
        let dt = finite(t - self.reference_time_s, "AxisymTime")?;
        AxisymmetricPoint::new(
            positive_finite(
                self.reference_point.mean_scale_factor
                    * finite(
                        self.reference_point.mean_hubble_per_s * dt,
                        "AxisymExponent",
                    )?
                    .exp(),
                "AxisymMeanScale",
            )?,
            finite(
                self.reference_point.anisotropy
                    + finite(self.reference_point.shear_per_s * dt, "AxisymAnisotropy")?,
                "AxisymAnisotropy",
            )?,
            self.reference_point.mean_hubble_per_s,
            self.reference_point.shear_per_s,
        )?
        .snapshot()
    }
}

impl ConstantHubbleBackground {
    pub fn new(
        initial_scale_factors: [f64; 3],
        hubble_per_s: [f64; 3],
    ) -> Result<Self, ForwardError> {
        GeometrySnapshot::new(initial_scale_factors, hubble_per_s)?;
        Ok(Self {
            initial_scale_factors,
            hubble_per_s,
        })
    }
}

impl GeometryBackground for ConstantHubbleBackground {
    fn snapshot(&self, t: f64) -> Result<GeometrySnapshot, ForwardError> {
        finite(t, "BianchiTime")?;
        GeometrySnapshot::new(self.initial_scale_factors, self.hubble_per_s)?;
        let mut a = [0.0; 3];
        for (i, output) in a.iter_mut().enumerate() {
            let ht = finite(self.hubble_per_s[i] * t, "BianchiExponent")?;
            *output = positive_finite(self.initial_scale_factors[i] * ht.exp(), "BianchiScale")?;
        }
        GeometrySnapshot::new(a, self.hubble_per_s)
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct CharacteristicRay {
    pub energy_ev: f64,
    pub direction: [f64; 3],
    pub occupation: f64,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct RayDerivative {
    pub energy_dot_ev_s: f64,
    pub direction_dot_per_s: [f64; 3],
}

impl CharacteristicRay {
    pub fn new(energy_ev: f64, direction: [f64; 3], occupation: f64) -> Result<Self, ForwardError> {
        positive_finite(energy_ev, "RayEnergy")?;
        if !occupation.is_finite() || occupation < 0.0 {
            return Err(invalid("RayOccupation"));
        }
        for component in direction {
            finite(component, "RayDirection")?;
        }
        let norm = direction[0].hypot(direction[1]).hypot(direction[2]);
        if !norm.is_finite() || (norm - 1.0).abs() > 1e-12 {
            return Err(invalid("RayUnitDirection"));
        }
        let normalized = direction.map(|component| component / norm);
        Ok(Self {
            energy_ev,
            direction: normalized,
            occupation,
        })
    }

    fn scaled_components(
        &self,
        g0: &GeometrySnapshot,
        g1: &GeometrySnapshot,
    ) -> Result<([f64; 3], f64), ForwardError> {
        let ray = Self::new(self.energy_ev, self.direction, self.occupation)?;
        g0.validate()?;
        g1.validate()?;
        let mut q = [0.0; 3];
        let mut direct = true;
        for (i, component) in q.iter_mut().enumerate() {
            let ratio = g0.scale_factors[i] / g1.scale_factors[i];
            *component = ray.direction[i] * ratio;
            direct &= ratio.is_finite()
                && ratio > 0.0
                && component.is_finite()
                && (*component != 0.0 || ray.direction[i] == 0.0);
        }
        let r = q[0].hypot(q[1]).hypot(q[2]);
        if direct && r.is_finite() && r > 0.0 {
            let direction = q.map(|value| value / r);
            if direction
                .iter()
                .zip(ray.direction)
                .all(|(a, b)| a.is_finite() && (*a != 0.0 || b == 0.0))
            {
                return Ok((direction, r));
            }
        }
        // A scaled component can underflow while its normalized direction is
        // representable. Rescale before exponentiation rather than losing it.
        let logs: [f64; 3] = std::array::from_fn(|i| {
            if ray.direction[i] == 0.0 {
                f64::NEG_INFINITY
            } else {
                ray.direction[i].abs().ln() + g0.scale_factors[i].ln() - g1.scale_factors[i].ln()
            }
        });
        let largest = logs.iter().copied().fold(f64::NEG_INFINITY, f64::max);
        let scaled = logs.map(|value| (value - largest).exp());
        let norm = scaled[0].hypot(scaled[1]).hypot(scaled[2]);
        let r = positive_finite((largest + norm.ln()).exp(), "RayRedshift")?;
        let mut direction = [0.0; 3];
        for i in 0..3 {
            direction[i] = (logs[i] - largest).exp() / norm * ray.direction[i].signum();
            if !direction[i].is_finite() || (direction[i] == 0.0 && ray.direction[i] != 0.0) {
                return Err(invalid("RayDirectionUnderflow"));
            }
        }
        Ok((direction, r))
    }

    pub fn pullback(
        &self,
        g0: &GeometrySnapshot,
        g1: &GeometrySnapshot,
    ) -> Result<Self, ForwardError> {
        let (direction, r) = self.scaled_components(g0, g1)?;
        let energy = positive_finite(self.energy_ev * r, "RayTransportEnergy")?;
        Self::new(energy, direction, self.occupation)
    }

    pub fn solid_angle_jacobian(
        &self,
        g0: &GeometrySnapshot,
        g1: &GeometrySnapshot,
    ) -> Result<f64, ForwardError> {
        let (_, r) = self.scaled_components(g0, g1)?;
        let log_j = g0
            .scale_factors
            .iter()
            .zip(g1.scale_factors)
            .map(|(a, b)| a.ln() - b.ln())
            .sum::<f64>()
            - 3.0 * r.ln();
        positive_finite(log_j.exp(), "RaySolidAngleJacobian")
    }

    pub fn derivative(&self, g: &GeometrySnapshot) -> Result<RayDerivative, ForwardError> {
        let ray = Self::new(self.energy_ev, self.direction, self.occupation)?;
        g.validate()?;
        let reference = g.hubble_per_s[0];
        let mut shear_projection = 0.0;
        for i in 0..3 {
            shear_projection = finite(
                shear_projection
                    + ray.direction[i] * ray.direction[i] * (g.hubble_per_s[i] - reference),
                "RayHubbleProjection",
            )?;
        }
        let hd = finite(reference + shear_projection, "RayHubbleProjection")?;
        let energy_dot_ev_s = finite(-self.energy_ev * hd, "RayEnergyDerivative")?;
        let mut direction_dot_per_s = [0.0; 3];
        for (i, derivative) in direction_dot_per_s.iter_mut().enumerate() {
            let difference = shear_projection - (g.hubble_per_s[i] - reference);
            *derivative = finite(ray.direction[i] * difference, "RayDirectionDerivative")?;
        }
        Ok(RayDerivative {
            energy_dot_ev_s,
            direction_dot_per_s,
        })
    }
}
