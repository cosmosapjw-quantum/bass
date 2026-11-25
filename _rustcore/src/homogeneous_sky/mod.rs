//! Homogeneous Lagrangian photon bundle: bolometric transverse coherency, a
//! positive solid-angle measure, and independently specified material and observer frames.
use crate::kinetic::lie_history::{advance_ray, RayNode};
use crate::kinetic::sky_spectrum::SkySample;
use crate::kinetic::sphere::SphereGrid;
use nalgebra::{Matrix3, SMatrix, SVector, Vector3};
use std::f64::consts::{PI, SQRT_2};
pub mod field;
pub mod frames;
pub mod harmonic_collision;
pub mod ionization;
pub mod material;
pub mod rec_bridge;
mod recoil;
pub mod replay;
pub mod solve;
pub mod spectral;

type V = Vector3<f64>;
type M = Matrix3<f64>;
type Six = SVector<f64, 6>;
const GAIN: f64 = 3.0 / (8.0 * PI);
/// Alexander (1977) L-stable, stiffly accurate SDIRK2 diagonal coefficient.
const SDIRK_GAMMA: f64 = 1.0 - std::f64::consts::FRAC_1_SQRT_2;

#[derive(Clone, Debug)]
pub struct Photon {
    direction: V,
    weight: f64,
    screen: M,
}

impl Photon {
    /// Unit-intensity, unpolarized bolometric coherency for propagation `direction`.
    pub fn isotropic(direction: [f64; 3], weight: f64) -> Result<Self, String> {
        let e = V::from(direction);
        if !e.norm_squared().is_finite() || (e.norm_squared() - 1.0).abs() > 1e-9 {
            return Err("photon direction must be a unit vector".into());
        }
        if !weight.is_finite() || weight <= 0.0 {
            return Err("photon solid-angle weight must be finite and positive".into());
        }
        Ok(Self {
            direction: e,
            weight,
            screen: projector(&e) * 0.5,
        })
    }
    /// Normal-frame propagation direction.
    pub fn direction(&self) -> [f64; 3] {
        self.direction.into()
    }
    /// Lagrangian solid angle (observer frame after `observed_sky`).
    pub fn weight(&self) -> f64 {
        self.weight
    }
    /// Bolometric transverse coherency; its trace is the bolometric intensity.
    pub fn screen(&self) -> [[f64; 3]; 3] {
        rows(&self.screen)
    }
}

/// Time integrator of the frozen-coefficient Thomson subsystem on one depth cell.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub enum CollisionScheme {
    /// First-order, L-stable backward Euler (R109 default).
    #[default]
    BackwardEuler,
    /// Second-order, L-stable, stiffly accurate two-stage SDIRK (Alexander 1977).
    Sdirk2,
}

impl CollisionScheme {
    pub fn name(self) -> &'static str {
        match self {
            Self::BackwardEuler => "backward-euler",
            Self::Sdirk2 => "sdirk2",
        }
    }
    pub fn parse(s: &str) -> Result<Self, String> {
        match s {
            "backward-euler" => Ok(Self::BackwardEuler),
            "sdirk2" => Ok(Self::Sdirk2),
            _ => Err(format!(
                "unknown collision scheme {s} (backward-euler or sdirk2)"
            )),
        }
    }
}

/// Everything a single ray needs to repeat one accepted collision cell: the bare
/// normal-frame depth, the electron velocity, the optional discrete gain
/// normalization and the rest-frame bolometric source tensor of each implicit stage.
#[derive(Clone, Debug)]
pub struct CollisionEvent {
    pub depth: f64,
    pub beta: [f64; 3],
    pub gain_map: Option<[[f64; 3]; 3]>,
    pub scheme: CollisionScheme,
    pub sources: Vec<[[f64; 3]; 3]>,
}

fn rows(m: &M) -> [[f64; 3]; 3] {
    std::array::from_fn(|i| std::array::from_fn(|j| m[(i, j)]))
}
fn from_rows(r: &[[f64; 3]; 3]) -> M {
    M::from_fn(|i, j| r[i][j])
}

fn projector(e: &V) -> M {
    M::identity() - e * e.transpose()
}

pub fn initial_sky(nmu: usize, nphi: usize) -> Result<Vec<Photon>, String> {
    if nmu < 3 || nphi < 5 {
        return Err("need at least 3 polar and 5 azimuthal nodes".into());
    }
    let grid = SphereGrid::new(nmu, nphi);
    Ok(grid
        .ehat
        .chunks_exact(3)
        .zip(grid.w)
        .map(|(e, weight)| {
            let direction = V::from_column_slice(e);
            Photon {
                direction,
                weight,
                screen: projector(&direction) * 0.5,
            }
        })
        .collect())
}

/// Spatial screen lifting under a pure boost. Fix the gauge of each boosted
/// polarization vector by subtracting its time component times (1,e').
fn boost(e: V, beta: V) -> Result<(V, M, f64), String> {
    let b2 = beta.norm_squared();
    if !(0.0..1.0).contains(&b2) {
        return Err("boost needs finite |v|/c < 1".into());
    }
    let g = 1.0 / (1.0 - b2).sqrt();
    let k = g * g / (1.0 + g);
    let be = beta.dot(&e);
    let d = g * (1.0 - be);
    let outgoing = (e + (k * be - g) * beta) / d;
    let lift = M::identity() + (k * beta + g * outgoing) * beta.transpose();
    Ok((outgoing, lift, d))
}

fn transformed(p: &Photon, beta: V) -> Result<Photon, String> {
    let (direction, j, d) = boost(p.direction, beta)?;
    Ok(Photon {
        direction,
        weight: p.weight / d.powi(2),
        screen: j * p.screen * j.transpose() * d.powi(4),
    })
}

fn pack(m: M) -> Six {
    Six::from_row_slice(&[
        m[(0, 0)],
        m[(1, 1)],
        m[(2, 2)],
        m[(0, 1)],
        m[(0, 2)],
        m[(1, 2)],
    ])
}
fn unpack(v: Six) -> M {
    M::new(v[0], v[3], v[4], v[3], v[1], v[5], v[4], v[5], v[2])
}

/// One backward-Euler electron-frame gain/loss step with normal-frame time.
/// The implicit global scattering source is a symmetric 3x3 tensor; six
/// unknowns replace an angular dense solve. This step is first order in depth.
pub fn scatter(sky: &mut [Photon], tau: f64, beta: [f64; 3]) -> Result<(), String> {
    scatter_kernel(sky, tau, beta, None, CollisionScheme::BackwardEuler).map(|_| ())
}

/// Same electron-frame collision with an explicit time integrator. The returned
/// event lets any other ray repeat this cell exactly (see [`replay_collision`]).
pub fn scatter_with(
    sky: &mut [Photon],
    tau: f64,
    beta: [f64; 3],
    scheme: CollisionScheme,
) -> Result<CollisionEvent, String> {
    scatter_kernel(sky, tau, beta, None, scheme)
}

/// Per-ray quantities of one collision cell that do not depend on the source.
struct RayTerms {
    e: V,
    d: f64,
    area: f64,
    rest: M,
    gain_projector: M,
}

fn ray_terms(p: &Photon, b: V, gain_map: Option<&M>) -> Result<RayTerms, String> {
    let (e, j, d) = boost(p.direction, b)?;
    let area = p.weight / (d * d);
    let rest = j * p.screen * j.transpose() * d.powi(4);
    let pe = projector(&e);
    let gain_projector = gain_map.map_or(pe, |map| pe * map);
    Ok(RayTerms {
        e,
        d,
        area,
        rest,
        gain_projector,
    })
}

/// Backward-Euler transmission and gain weights for bare depth `depth`.
fn stage_weights(depth: f64, d: f64) -> Result<(f64, f64), String> {
    let ray_depth = depth * d;
    if !ray_depth.is_finite() {
        return Err("ray depth overflow".into());
    }
    Ok((
        1.0 / (1.0 + ray_depth),
        ray_depth / (1.0 + ray_depth) * GAIN,
    ))
}

/// One implicit (backward-Euler) closure of depth `depth` applied to the
/// electron-rest coherencies `inputs`; returns the solved source and outputs.
fn implicit_stage(terms: &[RayTerms], inputs: &[M], depth: f64) -> Result<(M, Vec<M>), String> {
    let mut lhs = SMatrix::<f64, 6, 6>::identity();
    let mut rhs = M::zeros();
    let mut weights = Vec::with_capacity(terms.len());
    for (t, rest) in terms.iter().zip(inputs) {
        let (transmit, gain) = stage_weights(depth, t.d)?;
        rhs += t.area * transmit * *rest;
        // Symmetric congruence S -> P S Pᵀ in packed [xx,yy,zz,xy,xz,yz].
        // Off-diagonal components occur twice in the full input tensor.
        const PAIRS: [(usize, usize); 6] = [(0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2)];
        let w = t.area * gain;
        let gp = &t.gain_projector;
        for (row, &(i, j)) in PAIRS.iter().enumerate() {
            for (col, &(k, l)) in PAIRS.iter().enumerate() {
                let mut value = gp[(i, k)] * gp[(j, l)];
                if k != l {
                    value += gp[(i, l)] * gp[(j, k)];
                }
                lhs[(row, col)] -= w * value;
            }
        }
        weights.push((transmit, gain));
    }
    let source = unpack(
        lhs.lu()
            .solve(&pack(rhs))
            .ok_or("singular Thomson source closure")?,
    );
    let outputs = terms
        .iter()
        .zip(inputs)
        .zip(weights)
        .map(|((t, rest), (transmit, gain))| {
            *rest * transmit + t.gain_projector * source * t.gain_projector.transpose() * gain
        })
        .collect();
    Ok((source, outputs))
}

/// The same stage for one ray with a known source.
fn stage_ray(t: &RayTerms, rest: &M, depth: f64, source: &M) -> Result<M, String> {
    let (transmit, gain) = stage_weights(depth, t.d)?;
    Ok(*rest * transmit + t.gain_projector * source * t.gain_projector.transpose() * gain)
}

/// SDIRK2 second-stage input X + ((1-g)/g)(X1 - X) = -sqrt2 X + (1+sqrt2) X1.
fn sdirk_input(x0: &M, x1: &M) -> M {
    *x0 * (-SQRT_2) + *x1 * (1.0 + SQRT_2)
}

fn to_normal(t: &RayTerms, b: V, rest_new: &M) -> Result<M, String> {
    let (_, inv, inv_d) = boost(t.e, -b)?;
    let out = inv * rest_new * inv.transpose() * inv_d.powi(4);
    if !out.iter().all(|v| v.is_finite()) {
        return Err("nonfinite bolometric intensity; refine angular/depth mesh".into());
    }
    if out.trace() <= 0.0 {
        return Err("nonpositive bolometric intensity; refine angular/depth mesh".into());
    }
    Ok((out + out.transpose()) * 0.5)
}

fn validate_cell(tau: f64, b: &V) -> Result<(), String> {
    if !tau.is_finite() || tau < 0.0 || !(0.0..1.0).contains(&b.norm_squared()) {
        return Err("invalid proper Thomson depth or material velocity".into());
    }
    Ok(())
}

fn scatter_kernel(
    sky: &mut [Photon],
    tau: f64,
    beta: [f64; 3],
    gain_map: Option<&M>,
    scheme: CollisionScheme,
) -> Result<CollisionEvent, String> {
    let b = V::from(beta);
    validate_cell(tau, &b)?;
    let mut event = CollisionEvent {
        depth: tau,
        beta,
        gain_map: gain_map.map(rows),
        scheme,
        sources: Vec::new(),
    };
    if tau == 0.0 {
        return Ok(event);
    }
    let terms = sky
        .iter()
        .map(|p| ray_terms(p, b, gain_map))
        .collect::<Result<Vec<_>, _>>()?;
    let rests: Vec<M> = terms.iter().map(|t| t.rest).collect();
    let outputs = match scheme {
        CollisionScheme::BackwardEuler => {
            let (source, out) = implicit_stage(&terms, &rests, tau)?;
            event.sources.push(rows(&source));
            out
        }
        CollisionScheme::Sdirk2 => {
            let depth = SDIRK_GAMMA * tau;
            let (first, stage) = implicit_stage(&terms, &rests, depth)?;
            let second_input: Vec<M> = rests
                .iter()
                .zip(&stage)
                .map(|(x0, x1)| sdirk_input(x0, x1))
                .collect();
            let (second, out) = implicit_stage(&terms, &second_input, depth)?;
            event.sources.push(rows(&first));
            event.sources.push(rows(&second));
            out
        }
    };
    let screens = terms
        .iter()
        .zip(&outputs)
        .map(|(t, rest_new)| to_normal(t, b, rest_new))
        .collect::<Result<Vec<_>, _>>()?;
    for (p, screen) in sky.iter_mut().zip(screens) {
        p.screen = screen;
    }
    Ok(event)
}

/// Repeat one recorded collision cell on a single ray. With the same input ray
/// this performs the floating-point operations of the forward solve.
pub fn replay_collision(p: &mut Photon, event: &CollisionEvent) -> Result<(), String> {
    let b = V::from(event.beta);
    validate_cell(event.depth, &b)?;
    if event.depth == 0.0 {
        return Ok(());
    }
    let expected = match event.scheme {
        CollisionScheme::BackwardEuler => 1,
        CollisionScheme::Sdirk2 => 2,
    };
    if event.sources.len() != expected {
        return Err("collision event has the wrong number of stage sources".into());
    }
    let map = event.gain_map.as_ref().map(from_rows);
    let t = ray_terms(p, b, map.as_ref())?;
    let rest_new = match event.scheme {
        CollisionScheme::BackwardEuler => {
            stage_ray(&t, &t.rest, event.depth, &from_rows(&event.sources[0]))?
        }
        CollisionScheme::Sdirk2 => {
            let depth = SDIRK_GAMMA * event.depth;
            let x1 = stage_ray(&t, &t.rest, depth, &from_rows(&event.sources[0]))?;
            let y = sdirk_input(&t.rest, &x1);
            stage_ray(&t, &y, depth, &from_rows(&event.sources[1]))?
        }
    };
    p.screen = to_normal(&t, b, &rest_new)?;
    Ok(())
}

fn geometric(sky: &mut [Photon], left: &RayNode, right: &RayNode) -> Result<(), String> {
    for p in sky {
        geometric_one(p, left, right)?;
    }
    Ok(())
}

/// Free characteristic transport of one bundle across [left.eta, right.eta].
fn geometric_one(p: &mut Photon, left: &RayNode, right: &RayNode) -> Result<(), String> {
    let step = advance_ray(left, right, p.direction.into())?;
    let r = M::from_fn(|i, j| step.rotation[i][j]);
    p.screen = (r * p.screen * r.transpose()) * (4.0 * step.log_energy).exp();
    p.weight *= step.log_area.exp();
    p.direction = V::from(step.e);
    if !p.weight.is_finite() || p.weight <= 0.0 || !p.screen.trace().is_finite() {
        return Err("geometric transport overflow".into());
    }
    Ok(())
}

#[derive(Clone, Debug)]
pub struct RadiationMoments {
    pub area: f64,
    pub energy: f64,
    pub flux: [f64; 3],
    pub pressure: [[f64; 3]; 3],
    pub minimum_intensity: f64,
    pub minimum_screen_eigenvalue: f64,
    pub max_screen_leak: f64,
}

pub fn moments(sky: &[Photon]) -> Result<RadiationMoments, String> {
    let (mut area, mut energy) = (0.0, 0.0);
    let mut flux = V::zeros();
    let mut pressure = M::zeros();
    let mut min_i = f64::INFINITY;
    let mut min_eig = f64::INFINITY;
    let mut max_leak = 0.0_f64;
    for p in sky {
        let i = p.screen.trace();
        min_i = min_i.min(i);
        // Eigenvalues on the transverse plane, independent of a polar dyad.
        let discr = (2.0 * p.screen.norm_squared() - i * i).max(0.0).sqrt();
        min_eig = min_eig.min(0.5 * (i - discr));
        max_leak = max_leak.max((p.screen * p.direction).norm());
        let mass = p.weight * i;
        area += p.weight;
        energy += mass;
        flux += mass * p.direction;
        pressure += mass * p.direction * p.direction.transpose();
    }
    if !(energy.is_finite() && energy > 0.0 && area.is_finite() && area > 0.0)
        || min_eig < -1e-9 * min_i
    {
        return Err("invalid radiation integral or negative transverse eigenvalue".into());
    }
    Ok(RadiationMoments {
        area,
        energy,
        flux: (flux / energy).into(),
        pressure: std::array::from_fn(|i| std::array::from_fn(|j| pressure[(i, j)] / energy)),
        minimum_intensity: min_i,
        minimum_screen_eigenvalue: min_eig,
        max_screen_leak: max_leak,
    })
}

/// T is the dimensionless fourth-root bolometric temperature relative to its
/// observed monopole. Q,U use bolometric Stokes units divided by 4 <I>.
/// The meridian dyad is built from the outward sky direction, opposite propagation.
pub fn observed_sky(sky: &[Photon], beta: [f64; 3]) -> Result<Vec<SkySample>, String> {
    let seen: Vec<_> = sky
        .iter()
        .map(|p| transformed(p, V::from(beta)))
        .collect::<Result<_, _>>()?;
    let stats = moments(&seen)?;
    let tbar = seen
        .iter()
        .map(|p| p.weight * p.screen.trace().sqrt().sqrt())
        .sum::<f64>()
        / stats.area;
    let ibar = stats.energy / stats.area;
    Ok(seen
        .iter()
        .map(|p| sky_sample(-p.direction, &p.screen, p.weight, tbar, ibar))
        .collect())
}

/// Dimensionless T and Q,U of one observer-frame coherency at outward sky
/// direction `n`, in the right-handed (e_theta, e_phi) dyad; see `observed_sky`.
fn sky_sample(n: V, screen: &M, weight: f64, tbar: f64, ibar: f64) -> SkySample {
    let phi = n.y.atan2(n.x);
    let az = V::new(-phi.sin(), phi.cos(), 0.);
    let mer = az.cross(&n);
    let q = (mer.dot(&(screen * mer)) - az.dot(&(screen * az))) / (4.0 * ibar);
    let u = 2.0 * mer.dot(&(screen * az)) / (4.0 * ibar);
    SkySample {
        direction: n.into(),
        weight,
        t: screen.trace().sqrt().sqrt() / tbar - 1.0,
        q,
        u,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn finite_boost_solid_angle_energy_and_roundtrip() {
        let sky = initial_sky(16, 40).unwrap();
        let b = V::new(0.12, -0.33, 0.07);
        let seen: Vec<_> = sky.iter().map(|p| transformed(p, b).unwrap()).collect();
        let m = moments(&seen).unwrap();
        assert!((m.area / (4.0 * PI) - 1.0).abs() < 2e-13);
        assert!(
            (m.energy / (4.0 * PI) - (1.0 + b.norm_squared() / 3.) / (1. - b.norm_squared())).abs()
                < 2e-13
        );
        for (p, x) in sky.iter().zip(&seen) {
            let back = transformed(x, -b).unwrap();
            assert!((back.screen - p.screen).norm() < 4e-14);
            assert!((back.direction - p.direction).norm() < 4e-14);
        }
    }
    #[test]
    fn tilted_thomson_first_moment_and_energy_have_correct_sign_and_boost() {
        let mut sky = initial_sky(16, 40).unwrap();
        let b = V::new(0.2, 0.04, -0.01);
        let g = 1.0 / (1.0 - b.norm_squared()).sqrt();
        let dt = 1e-5;
        scatter(&mut sky, dt, b.into()).unwrap();
        let m = moments(&sky).unwrap();
        let gain = (m.energy / (4.0 * PI) - 1.0) / dt;
        let target = 4.0 / 3.0 * g * g * g * b.norm_squared();
        assert!((gain - target).abs() < 4e-6, "{gain} vs {target}");
        for k in 0..3 {
            assert!(
                (m.flux[k] * m.energy / (4. * PI) / dt - 4. / 3. * g.powi(3) * b[k]).abs() < 7e-6
            );
        }
    }
    #[test]
    fn isotropic_thick_rest_scattering_preserves_equilibrium() {
        let mut sky = initial_sky(8, 24).unwrap();
        let before = sky.clone();
        scatter(&mut sky, 100., [0.; 3]).unwrap();
        for (p, old) in sky.iter().zip(before) {
            assert!((p.screen - old.screen).norm() < 2e-12);
        }
        assert!(scatter(&mut sky, 0., [1., 0., 0.]).is_err());
    }
}
