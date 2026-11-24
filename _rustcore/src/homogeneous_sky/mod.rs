//! Homogeneous Lagrangian photon bundle: bolometric transverse coherency, a
//! positive solid-angle measure, and independently specified material and observer frames.
use crate::kinetic::lie_history::{advance_ray, RayNode};
use crate::kinetic::sky_spectrum::SkySample;
use crate::kinetic::sphere::SphereGrid;
use nalgebra::{Matrix3, SMatrix, SVector, Vector3};
use std::f64::consts::PI;
pub mod ionization;
pub mod material;
mod recoil;
pub mod solve;

type V = Vector3<f64>;
type M = Matrix3<f64>;
type Six = SVector<f64, 6>;
const GAIN: f64 = 3.0 / (8.0 * PI);

#[derive(Clone)]
pub struct Photon {
    direction: V,
    weight: f64,
    screen: M,
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
    scatter_kernel(sky, tau, beta, None)
}

fn scatter_kernel(
    sky: &mut [Photon],
    tau: f64,
    beta: [f64; 3],
    gain_map: Option<&M>,
) -> Result<(), String> {
    let b = V::from(beta);
    if !tau.is_finite() || tau < 0.0 || !(0.0..1.0).contains(&b.norm_squared()) {
        return Err("invalid proper Thomson depth or material velocity".into());
    }
    if tau == 0.0 {
        return Ok(());
    }
    let mut lhs = SMatrix::<f64, 6, 6>::identity();
    let mut rhs = M::zeros();
    let mut inputs = Vec::with_capacity(sky.len());
    for p in sky.iter() {
        let (e, j, d) = boost(p.direction, b)?;
        let area = p.weight / (d * d);
        let rest = j * p.screen * j.transpose() * d.powi(4);
        let depth = tau * d;
        if !depth.is_finite() {
            return Err("ray depth overflow".into());
        }
        let transmit = 1.0 / (1.0 + depth);
        let gain = depth / (1.0 + depth) * GAIN;
        let pe = projector(&e);
        let gain_projector = gain_map.map_or(pe, |map| pe * map);
        rhs += area * transmit * rest;
        // Symmetric congruence S -> P S Pᵀ in packed [xx,yy,zz,xy,xz,yz].
        // Off-diagonal components occur twice in the full input tensor.
        const PAIRS: [(usize, usize); 6] = [(0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2)];
        let w = area * gain;
        for (row, &(i, j)) in PAIRS.iter().enumerate() {
            for (col, &(k, l)) in PAIRS.iter().enumerate() {
                let mut value = gain_projector[(i, k)] * gain_projector[(j, l)];
                if k != l {
                    value += gain_projector[(i, l)] * gain_projector[(j, k)];
                }
                lhs[(row, col)] -= w * value;
            }
        }
        inputs.push((e, gain_projector, rest, transmit, gain));
    }
    let source = unpack(
        lhs.lu()
            .solve(&pack(rhs))
            .ok_or("singular Thomson source closure")?,
    );
    for (p, (e, gain_projector, rest, transmit, gain)) in sky.iter_mut().zip(inputs) {
        let rest_new =
            rest * transmit + gain_projector * source * gain_projector.transpose() * gain;
        let (_, inv, inv_d) = boost(e, -b)?;
        let out = inv * rest_new * inv.transpose() * inv_d.powi(4);
        if !out.iter().all(|v| v.is_finite()) || out.trace() <= 0.0 {
            return Err(
                "nonpositive/nonfinite bolometric intensity; refine angular/depth mesh".into(),
            );
        }
        p.screen = (out + out.transpose()) * 0.5;
    }
    Ok(())
}

fn geometric(sky: &mut [Photon], left: &RayNode, right: &RayNode) -> Result<(), String> {
    for p in sky {
        let step = advance_ray(left, right, p.direction.into())?;
        let r = M::from_fn(|i, j| step.rotation[i][j]);
        p.screen = (r * p.screen * r.transpose()) * (4.0 * step.log_energy).exp();
        p.weight *= step.log_area.exp();
        p.direction = V::from(step.e);
        if !p.weight.is_finite() || p.weight <= 0.0 || !p.screen.trace().is_finite() {
            return Err("geometric transport overflow".into());
        }
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
        .map(|p| {
            let n = -p.direction;
            let phi = n.y.atan2(n.x);
            let az = V::new(-phi.sin(), phi.cos(), 0.);
            let mer = az.cross(&n);
            let q = (mer.dot(&(p.screen * mer)) - az.dot(&(p.screen * az))) / (4.0 * ibar);
            let u = 2.0 * mer.dot(&(p.screen * az)) / (4.0 * ibar);
            SkySample {
                direction: n.into(),
                weight: p.weight,
                t: p.screen.trace().sqrt().sqrt() / tbar - 1.0,
                q,
                u,
            }
        })
        .collect())
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
