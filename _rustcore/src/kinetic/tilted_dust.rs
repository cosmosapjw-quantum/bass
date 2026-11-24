//! Freely falling homogeneous massive streams. Frame signature (-,+,+,+).
//! p is orthonormal spatial four-velocity (gamma*beta); number density is
//! measured by the normal observers. eta is the normal e-fold time.
use super::lie_history::RayNode;
use nalgebra::{Matrix3, Vector3};

type Vec3 = Vector3<f64>;
type Mat3 = Matrix3<f64>;

#[derive(Debug, Clone, Copy)]
pub struct Stream {
    pub p: [f64; 3],
    /// ln(n_normal/n_normal_initial) for this stream.
    pub log_number_ratio: f64,
}

#[derive(Debug, Clone)]
pub struct Dust {
    pub streams: [Stream; 2],
    /// Per-stream initial rest mass times the normal-frame number density.
    mass_number_initial: [f64; 2],
}

#[derive(Debug, Clone, Copy)]
pub struct DustMoments {
    /// Normal-frame E, q and P in the same fixed units as supplied to opposed.
    pub energy: f64,
    pub flux: [f64; 3],
    pub pressure: [[f64; 3]; 3],
}

#[derive(Debug, Clone, Copy)]
pub struct DustBeam {
    /// Rest mass times normal-observer particle density (m n_normal), fixed energy units.
    pub normal_mass_density: f64,
    pub energy: f64,
    pub beta: [f64; 3],
    pub momentum_density: [f64; 3],
}

#[derive(Clone, Copy)]
struct Coeff {
    s: Mat3,
    n: Mat3,
    a: Vec3,
    r: Vec3,
}
impl Coeff {
    fn from_node(node: &RayNode) -> Result<Self, String> {
        let m = |rows: [[f64; 3]; 3]| Mat3::from_fn(|i, j| rows[i][j]);
        let c = Self {
            s: m(node.shear),
            n: m(node.n),
            a: node.a.into(),
            r: node.rotation.into(),
        };
        if !c
            .s
            .iter()
            .chain(c.n.iter())
            .chain(c.a.iter())
            .chain(c.r.iter())
            .all(|x| x.is_finite())
            || (c.n - c.n.transpose()).norm() > 1e-10 * (1. + c.n.norm())
            || (c.s - c.s.transpose()).norm() > 1e-10 * (1. + c.s.norm())
            || c.s.trace().abs() > 1e-10 * (1. + c.s.norm())
        {
            return Err("dust requires finite symmetric N and trace-free symmetric shear".into());
        }
        Ok(c)
    }
    fn lerp(self, right: Self, t: f64) -> Self {
        Self {
            s: self.s + (right.s - self.s) * t,
            n: self.n + (right.n - self.n) * t,
            a: self.a + (right.a - self.a) * t,
            r: self.r + (right.r - self.r) * t,
        }
    }
    fn norm_bound(self) -> f64 {
        self.s.norm() + self.a.norm() + self.n.norm() + self.r.norm()
    }
    /// The normal Hubble term -p is integrated by an exact integrating factor.
    /// For mass one, beta=p/sqrt(1+p²). (tr N)beta/2 drops out of beta x p.
    fn rates(self, p: Vec3) -> (Vec3, f64) {
        let gamma = 1f64.hypot(p[0]).hypot(p[1]).hypot(p[2]);
        let beta = p / gamma;
        let omega = self.r + self.a.cross(&beta) + self.n * beta;
        (-self.s * p + omega.cross(&p), -3. + 2. * self.a.dot(&beta))
    }
}

impl Dust {
    /// Two equal-energy, opposite-momentum streams. initial_energy is the
    /// sum of their normal-frame energies; it may be zero for the photon limit.
    pub fn opposed(initial_energy: f64, beta: [f64; 3]) -> Result<Self, String> {
        let beta = Vec3::from(beta);
        let speed = beta.norm();
        if !initial_energy.is_finite() || initial_energy < 0. || !speed.is_finite() || speed >= 1. {
            return Err("dust requires finite nonnegative energy and |beta| < 1".into());
        }
        let gamma = 1. / ((1. - speed) * (1. + speed)).sqrt();
        let p = gamma * beta;
        Ok(Self {
            streams: [
                Stream {
                    p: p.into(),
                    log_number_ratio: 0.,
                },
                Stream {
                    p: (-p).into(),
                    log_number_ratio: 0.,
                },
            ],
            mass_number_initial: [0.5 * initial_energy / gamma; 2],
        })
    }

    /// Two equal-weight streams with the same normal-frame bulk velocity.
    /// Their total normal momentum is initial_energy * beta; stream zero may
    /// be selected as the Thomson host independently after initialization.
    pub fn coflow(initial_energy: f64, beta: [f64; 3]) -> Result<Self, String> {
        let mut dust = Self::opposed(initial_energy, beta)?;
        dust.streams[1] = dust.streams[0];
        Ok(dust)
    }

    /// Two species with opposite total initial momentum. f_b is the fraction
    /// of the initial normal-observer rest-mass density m*n_normal, not
    /// the proper-density or energy fraction at finite relative velocity.
    pub fn opposed_species(
        initial_energy: f64,
        f_b: f64,
        beta_b: [f64; 3],
    ) -> Result<Self, String> {
        if !(0.0 < f_b && f_b < 1.0) {
            return Err("baryon fraction must lie strictly between zero and one".into());
        }
        let mut dust = Self::opposed(initial_energy, beta_b)?;
        if f_b == 0.5 {
            return Ok(dust);
        }
        let p_b = Vec3::from(dust.streams[0].p);
        let p_c = -(f_b / (1.0 - f_b)) * p_b;
        let gamma = |p: Vec3| 1f64.hypot(p[0]).hypot(p[1]).hypot(p[2]);
        let denom = f_b * gamma(p_b) + (1.0 - f_b) * gamma(p_c);
        let mass = initial_energy / denom;
        dust.streams[1].p = p_c.into();
        dust.mass_number_initial = [f_b * mass, (1.0 - f_b) * mass];
        if !denom.is_finite()
            || (initial_energy > 0. && dust.mass_number_initial.iter().any(|m| *m <= 0.))
        {
            return Err("species mass or momentum outside finite representable range".into());
        }
        dust.moments()?;
        Ok(dust)
    }

    /// Common velocity, independently partitioned normal rest-mass density.
    /// Preserves the Codazzi-required total flux E*beta.
    pub fn coflow_species(initial_energy: f64, f_b: f64, beta: [f64; 3]) -> Result<Self, String> {
        if !(0.0 < f_b && f_b < 1.0) {
            return Err("baryon fraction must lie strictly between zero and one".into());
        }
        let mut dust = Self::coflow(initial_energy, beta)?;
        if f_b == 0.5 {
            return Ok(dust);
        }
        let p = dust.streams[0].p;
        let gamma = 1f64.hypot(p[0]).hypot(p[1]).hypot(p[2]);
        let mass = initial_energy / gamma;
        dust.mass_number_initial = [f_b * mass, (1.0 - f_b) * mass];
        if initial_energy > 0. && dust.mass_number_initial.iter().any(|m| *m <= 0.) {
            return Err("species mass outside finite representable range".into());
        }
        dust.moments()?;
        Ok(dust)
    }

    /// Integrating-factor explicit midpoint for momentum, simultaneous midpoint
    /// for the proper continuity law. Endpoint geometry shares the normal frame.
    /// With Sigma=N=A=R=0 this gives p(a)=p0/a and n_normal(a)=n0/a³ exactly.
    pub fn advance(&self, left: &RayNode, right: &RayNode) -> Result<Self, String> {
        let dt = right.eta - left.eta;
        let c0 = Coeff::from_node(left)?;
        let c1 = Coeff::from_node(right)?;
        let bound = dt.abs() * c0.norm_bound().max(c1.norm_bound());
        if !dt.is_finite() || !bound.is_finite() || bound > 20000. {
            return Err("nonfinite or underresolved dust interval".into());
        }
        let count = (bound / 0.2).ceil().max(1.) as usize;
        let h = dt / count as f64;
        let half = (-0.5 * h).exp();
        let full = (-h).exp();
        let mut updated = self.clone();
        for k in 0..count {
            let start = c0.lerp(c1, k as f64 / count as f64);
            let mid = c0.lerp(c1, (k as f64 + 0.5) / count as f64);
            for stream in &mut updated.streams {
                let p = Vec3::from(stream.p);
                let (f0, _) = start.rates(p);
                let p_mid = half * (p + 0.5 * h * f0);
                let (f_mid, ln_n_dot) = mid.rates(p_mid);
                stream.p = (full * p + h * half * f_mid).into();
                stream.log_number_ratio += h * ln_n_dot;
                if !stream
                    .p
                    .iter()
                    .chain([&stream.log_number_ratio])
                    .all(|x| x.is_finite())
                {
                    return Err("dust step produced nonfinite particle or number density".into());
                }
            }
        }
        Ok(updated)
    }

    /// Read one beam's physical normal-frame moments on the same time slice.
    pub fn beam(&self, index: usize) -> Result<DustBeam, String> {
        let stream = self
            .streams
            .get(index)
            .ok_or("dust beam index out of range")?;
        if !stream
            .p
            .iter()
            .chain([&stream.log_number_ratio])
            .all(|x| x.is_finite())
        {
            return Err("nonfinite dust beam".into());
        }
        let initial_mass = self.mass_number_initial[index];
        let normal_mass_density = if initial_mass == 0. || stream.log_number_ratio == 0. {
            initial_mass
        } else {
            (initial_mass.ln() + stream.log_number_ratio).exp()
        };
        let p = Vec3::from(stream.p);
        let gamma = 1f64.hypot(p[0]).hypot(p[1]).hypot(p[2]);
        let energy = normal_mass_density * gamma;
        let beta = p / gamma;
        let q = normal_mass_density * p;
        if !gamma.is_finite()
            || !energy.is_finite()
            || !q.iter().all(|x| x.is_finite())
            || (initial_mass > 0. && normal_mass_density == 0.)
        {
            return Err("dust beam outside the finite density range".into());
        }
        Ok(DustBeam {
            normal_mass_density,
            energy,
            beta: beta.into(),
            momentum_density: q.into(),
        })
    }

    /// Transfer signed momentum density into a single beam on a fixed normal slice.
    /// Number is unchanged. The energy follows the massive mass shell; a caller
    /// enforcing material + photon energy conservation must use that energy change.
    pub fn kick(&mut self, index: usize, delta_flux: [f64; 3]) -> Result<(), String> {
        let b = self.beam(index)?;
        if !delta_flux.iter().all(|x| x.is_finite()) {
            return Err("nonfinite momentum transfer".into());
        }
        if delta_flux.iter().all(|&x| x == 0.) {
            return Ok(());
        }
        if b.normal_mass_density <= 0. {
            return Err("cannot kick a zero density beam".into());
        }
        let target = Vec3::from(b.momentum_density) + Vec3::from(delta_flux);
        let mut trial = self.clone();
        trial.streams[index].p = (target / b.normal_mass_density).into();
        trial.beam(index)?;
        self.streams[index] = trial.streams[index];
        Ok(())
    }

    pub fn moments(&self) -> Result<DustMoments, String> {
        let mut energy = 0.;
        let mut flux = Vec3::zeros();
        let mut pressure = Mat3::zeros();
        for index in 0..self.streams.len() {
            let b = self.beam(index)?;
            let q = Vec3::from(b.momentum_density);
            energy += b.energy;
            flux += q;
            pressure += q * Vec3::from(b.beta).transpose();
        }
        if !energy.is_finite() || !flux.iter().chain(pressure.iter()).all(|x| x.is_finite()) {
            return Err("dust stress-energy is outside the numeric range".into());
        }
        Ok(DustMoments {
            energy,
            flux: flux.into(),
            pressure: std::array::from_fn(|i| std::array::from_fn(|j| pressure[(i, j)])),
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn eps(i: usize, j: usize, k: usize) -> f64 {
        let (i, j, k) = (i as i32, j as i32, k as i32);
        f64::from((i - j) * (j - k) * (k - i)) / 2.
    }

    #[test]
    fn flrw_massive_redshift_number_and_stress_exact() {
        let start = RayNode::default();
        let end = RayNode {
            eta: 0.8,
            ..start.clone()
        };
        let dust = Dust::opposed(0.6, [0.7, -0.1, 0.02]).unwrap();
        let aimed = dust.advance(&start, &end).unwrap();
        let p0 = Vec3::from(dust.streams[0].p);
        let p1 = Vec3::from(aimed.streams[0].p);
        assert!((p1 - (-0.8f64).exp() * p0).norm() < 2e-15);
        assert!((aimed.streams[0].log_number_ratio + 2.4).abs() < 1e-15);
        let m = aimed.moments().unwrap();
        let expected = 0.6 * (-2.4f64).exp() * (1. + p1.norm_squared()).sqrt()
            / (1. + p0.norm_squared()).sqrt();
        assert!((m.energy - expected).abs() < 2e-15);
        assert_eq!(m.flux, [0.; 3]);
        let tr = m.pressure[0][0] + m.pressure[1][1] + m.pressure[2][2];
        assert!((tr / m.energy - p1.norm_squared() / (1. + p1.norm_squared())).abs() < 3e-16);
        assert_eq!(
            Dust::opposed(0., [0.9, 0., 0.])
                .unwrap()
                .moments()
                .unwrap()
                .energy,
            0.
        );
    }

    #[test]
    fn coflow_supplies_signed_normal_flux_and_preserves_partition() {
        let beta = [0.6, -0.3, 0.2];
        let dust = Dust::coflow(2.4, beta).unwrap();
        let m = dust.moments().unwrap();
        assert!((m.energy - 2.4).abs() < 1e-15);
        assert!((Vec3::from(m.flux) - 2.4 * Vec3::from(beta)).norm() < 1e-15);
        assert_eq!(
            dust.beam(0).unwrap().momentum_density,
            dust.beam(1).unwrap().momentum_density
        );
        let expected = 2.4 * Vec3::from(beta) * Vec3::from(beta).transpose();
        assert!((Mat3::from_fn(|i, j| m.pressure[i][j]) - expected).norm() < 1e-15);
    }

    #[test]
    fn one_beam_kick_preserves_number_mass_shell_and_other_stream() {
        let mut d = Dust::opposed(1.7, [0.45, -0.2, 0.25]).unwrap();
        let before = d.beam(0).unwrap();
        let other = d.beam(1).unwrap();
        let delta = [-0.013, 0.027, 0.04];
        d.kick(0, delta).unwrap();
        let b = d.beam(0).unwrap();
        assert_eq!(before.normal_mass_density, b.normal_mass_density);
        assert_eq!(other.momentum_density, d.beam(1).unwrap().momentum_density);
        let q = Vec3::from(b.momentum_density);
        assert!((q - Vec3::from(before.momentum_density) - Vec3::from(delta)).norm() < 1e-15);
        assert!(
            (b.energy * b.energy - q.norm_squared() - b.normal_mass_density.powi(2)).abs() < 1e-15
        );
        assert!(d.kick(0, [f64::NAN, 0., 0.]).is_err());
        assert!(d.kick(8, [0.; 3]).is_err());
        assert_eq!(b.momentum_density, d.beam(0).unwrap().momentum_density);
        assert!(Dust::opposed(0., [0.; 3]).unwrap().kick(0, delta).is_err());
    }

    #[test]
    fn independent_timelike_koszul_and_number_contraction() {
        let node = RayNode {
            shear: [[0.1, 0.13, 0.02], [0.13, -0.27, -0.16], [0.02, -0.16, 0.17]],
            n: [[0., 0., 0.], [0., -0.25, 0.1], [0., 0.1, 0.3]],
            a: [0.2, 0., 0.],
            rotation: [0.003, 0.07, -0.08],
            ..Default::default()
        };
        let p = Vec3::new(-0.8, 0.4, 1.4);
        let gamma = (1. + p.norm_squared()).sqrt();
        let c = Coeff::from_node(&node).unwrap();
        let (lhs, ln_n) = c.rates(p);
        // Calculate the spatial 3-connection from [e_i,e_j] and Koszul,
        // independently of the cross-product ray equation.
        let bracket = |k: usize, i: usize, j: usize| {
            let structure: f64 = (0..3).map(|d| eps(i, j, d) * node.n[d][k]).sum();
            structure + (if k == j { node.a[i] } else { 0. })
                - (if k == i { node.a[j] } else { 0. })
        };
        let connection = |k, i, j| 0.5 * (bracket(k, i, j) - bracket(i, j, k) + bracket(j, k, i));
        let mut geodesic = -c.s * p + c.r.cross(&p);
        let mut spatial_div = 0.;
        for i in 0..3 {
            for j in 0..3 {
                spatial_div += connection(i, i, j) * p[j] / gamma;
                for k in 0..3 {
                    geodesic[i] -= connection(i, j, k) * p[j] * p[k] / gamma;
                }
            }
        }
        assert!((lhs - geodesic).norm() < 8e-16);
        assert!((ln_n + 3. + spatial_div).abs() < 8e-16);
    }

    #[test]
    fn counterstream_class_b_creates_flux_and_positive_stress() {
        let d = Dust::opposed(1., [0., 0.6, 0.]).unwrap();
        let start = RayNode {
            a: [0.22, 0., 0.],
            ..Default::default()
        };
        let end = RayNode {
            eta: 0.15,
            ..start.clone()
        };
        let evolved = d.advance(&start, &end).unwrap();
        let m = evolved.moments().unwrap();
        assert!(m.flux[0] < 0. && m.flux[1].abs() < 1e-14 && m.energy > 0.);
        assert!(m.pressure[0][0] > 0. && m.pressure[1][1] > 0. && m.pressure[2][2] == 0.);
        let d = Dust::opposed(1., [0.5, 0., 0.])
            .unwrap()
            .advance(&start, &end)
            .unwrap();
        assert!(d.streams[0].log_number_ratio > d.streams[1].log_number_ratio);
        assert!(Dust::opposed(1., [1., 0., 0.]).is_err());
    }
}
