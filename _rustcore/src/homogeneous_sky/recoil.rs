//! Elastic Thomson scattering coupled to the first massive stream on its mass shell.
use super::{boost, projector, scatter_kernel, CollisionEvent, CollisionScheme, Photon, GAIN, M, V};
use crate::kinetic::tilted_dust::Dust;

fn gamma(p: V) -> f64 {
    1_f64.hypot(p.x).hypot(p.y).hypot(p.z)
}

/// Normalize the discretized positive Thomson gain, before solving its implicit
/// collision equation. In the continuum GAIN * integral(1-ee^T)dOmega = 1.
/// In the electron tetrad A = GAIN sum(w'_i P'_i); tr[A T S T]=tr[S] for
/// T=A^-1/2. Positive coherencies remain positive on anisotropic meshes.
fn gain_map(sky: &[Photon], beta: V) -> Result<M, String> {
    let mut angular = M::zeros();
    for p in sky {
        let (e, _, d) = boost(p.direction, beta)?;
        angular += (GAIN * p.weight / (d * d)) * projector(&e);
    }
    if !angular.iter().all(|x| x.is_finite()) {
        return Err("nonfinite electron-frame Thomson angular integral".into());
    }
    let eig = angular.symmetric_eigen();
    let low = eig.eigenvalues.min();
    let high = eig.eigenvalues.max();
    // Finite angular coverage guard. A resolved electron-rest sky has all
    // eigenvalues near one. Nearly unrepresented solid angles require refinement.
    if !low.is_finite() || !high.is_finite() || low < 0.125 || high > 8. || high / low > 32. {
        return Err(format!(
            "unresolved electron-frame angular gain ({low:e}, {high:e}); refine angular quadrature"
        ));
    }
    let inv = M::from_diagonal(&eig.eigenvalues.map(|v| 1. / v.sqrt()));
    Ok(eig.eigenvectors * inv * eig.eigenvectors.transpose())
}

/// Integrate the photon change first, avoiding subtraction of two large total
/// four-momenta. For each ray, collision leaves area and direction fixed.
fn exchange(before: &[Photon], after: &[Photon], scale: f64) -> (f64, V) {
    let mut de = 0.;
    let mut dp = V::zeros();
    for (a, b) in before.iter().zip(after) {
        let di = (b.screen - a.screen).trace();
        let w = scale * a.weight * di;
        de += w;
        dp += w * a.direction;
    }
    (de, dp)
}

struct Trial {
    sky: Vec<Photon>,
    photon_dp: V,
    photon_energy_change: f64,
    event: CollisionEvent,
}

fn trial(
    start: &[Photon],
    p0: V,
    mass: f64,
    depth: f64,
    scale: f64,
    scheme: CollisionScheme,
) -> Result<Option<Trial>, String> {
    let g0 = gamma(p0);
    let mut beta = p0 / g0;
    let mut output = start.to_vec();
    let mut previous: Option<(V, V)> = None;
    for _ in 0..18 {
        output.clone_from_slice(start);
        let map = gain_map(start, beta)?;
        let event = scatter_kernel(&mut output, depth, beta.into(), Some(&map), scheme)?;
        let (de, dp) = exchange(start, &output, scale);
        let p1 = (mass * p0 - dp) / mass;
        let g1 = gamma(p1);
        if !de.is_finite() || !g1.is_finite() {
            return Err("nonfinite radiation or host recoil".into());
        }
        // Resolve substantial changes in the stream separately and bound the
        // contraction iteration for a radiation-dominated light host.
        if (p1 - p0).norm() > 0.25 * g0 {
            return Ok(None);
        }
        let discrete_beta = (p0 + p1) / (g0 + g1);
        let frame_error = (discrete_beta - beta).norm();
        if frame_error <= 32. * f64::EPSILON * (1. + beta.norm()) {
            return Ok(Some(Trial {
                sky: output,
                photon_dp: dp,
                photon_energy_change: de,
                event,
            }));
        }
        // One-step Anderson acceleration of the three-component frame solve.
        // Fall back to the fixed point when the secant is large or leaves
        // the timelike domain.
        let residual = discrete_beta - beta;
        let mut next = discrete_beta;
        if let Some((old_residual, old_candidate)) = previous {
            let dr = residual - old_residual;
            let dr2 = dr.norm_squared();
            if dr2 > 0. {
                let correction = (discrete_beta - old_candidate) * (dr.dot(&residual) / dr2);
                let accelerated = discrete_beta - correction;
                if correction.norm() <= 2. * frame_error && accelerated.norm_squared() < 1. {
                    next = accelerated;
                }
            }
        }
        previous = Some((residual, discrete_beta));
        beta = next;
    }
    Ok(None)
}

/// The incoming proper opacity depth excludes the directional Doppler factor.
/// The first stream owns the electron velocity; the second is a spectator.
/// Returns the signed photon + host energy change in the fixed units of
/// photon_scale. On error neither input is modified.
#[cfg(test)]
pub(super) fn scatter_with_recoil(
    sky: &mut [Photon],
    dust: &mut Dust,
    depth: f64,
    photon_scale: f64,
) -> Result<f64, String> {
    scatter_with_recoil_events(
        sky,
        dust,
        depth,
        photon_scale,
        CollisionScheme::BackwardEuler,
        &mut Vec::new(),
    )
}

/// As [`scatter_with_recoil`], appending each accepted trial's collision event
/// in time order. On error neither input nor `events` is modified.
pub(super) fn scatter_with_recoil_events(
    sky: &mut [Photon],
    dust: &mut Dust,
    depth: f64,
    photon_scale: f64,
    scheme: CollisionScheme,
    events: &mut Vec<CollisionEvent>,
) -> Result<f64, String> {
    if !depth.is_finite() || depth < 0. || !photon_scale.is_finite() || photon_scale < 0. {
        return Err("nonnegative finite Thomson depth and photon energy scale required".into());
    }
    if depth == 0. {
        return Ok(0.);
    }
    let mut accepted = Vec::new();
    let mass = dust.beam(0)?.normal_mass_density;
    if mass <= 0. || !mass.is_finite() {
        return Err("active scattering requires a finite positive host rest mass density".into());
    }
    let mut output = sky.to_vec();
    let mut updated = dust.clone();
    let mut pending = vec![(depth, 0usize)];
    let mut count = 0;
    let mut defect = 0.;
    while let Some((h, level)) = pending.pop() {
        count += 1;
        if count > 4095 {
            return Err("recoil exceeded 4095 trials; refine the depth grid".into());
        }
        let p0 = V::from(updated.streams[0].p);
        if let Some(proposed) = trial(&output, p0, mass, h, photon_scale, scheme)? {
            updated.kick(0, (-proposed.photon_dp).into())?;
            output = proposed.sky;
            accepted.push(proposed.event);
            // Read back the actually stored on-shell endpoint. The exact
            // divided difference avoids the cancellation in gamma1-gamma0.
            let p1 = V::from(updated.streams[0].p);
            let gradient = (p0 + p1) / (gamma(p0) + gamma(p1));
            defect += proposed.photon_energy_change + mass * gradient.dot(&(p1 - p0));
        } else {
            if level >= 24 || h * 0.5 == 0. {
                return Err(
                    "recoil cannot resolve the host acceleration; refine the depth grid".into(),
                );
            }
            pending.extend([(h * 0.5, level + 1); 2]);
        }
    }
    if !defect.is_finite() {
        return Err("nonfinite summed radiation-host energy defect".into());
    }
    sky.clone_from_slice(&output);
    *dust = updated;
    events.extend(accepted);
    Ok(defect)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::homogeneous_sky::{initial_sky, moments};
    use std::f64::consts::PI;

    #[test]
    fn comoving_and_zero_mass_limits_are_transactional() {
        let mut sky = initial_sky(5, 12).unwrap();
        let initial = sky.clone();
        let mut dust = Dust::opposed(0.5, [0.; 3]).unwrap();
        let error = scatter_with_recoil(&mut sky, &mut dust, 0.8, 0.5 / (4. * PI)).unwrap();
        assert!(error.abs() < 2e-15 && V::from(dust.streams[0].p).norm() < 1e-15);
        for (a, b) in sky.iter().zip(&initial) {
            assert!((a.screen - b.screen).norm() < 2e-15);
        }
        let mut zero = Dust::opposed(0., [0.; 3]).unwrap();
        let before = sky.clone();
        assert!(scatter_with_recoil(&mut sky, &mut zero, 0.1, 1.).is_err());
        assert_eq!(sky[0].screen, before[0].screen);
    }

    fn evolve(steps: usize) -> (f64, f64) {
        let mut sky = initial_sky(5, 12).unwrap();
        let mut dust = Dust::opposed(0.5, [0.25, -0.13, 0.08]).unwrap();
        let scale = 0.5 / (4. * PI);
        let p_initial = V::from(dust.streams[0].p);
        let initial = moments(&sky).unwrap();
        let spectator = dust.streams[1];
        let total_initial = initial.energy * scale + dust.moments().unwrap().energy;
        let mut work = 0.;
        for _ in 0..steps {
            work += scatter_with_recoil(&mut sky, &mut dust, 0.2 / steps as f64, scale).unwrap();
        }
        let m = moments(&sky).unwrap();
        let d = dust.moments().unwrap();
        let p = V::from(dust.streams[0].p);
        assert!((p - p_initial).dot(&p_initial) < 0.);
        assert_eq!(spectator.p, dust.streams[1].p);
        assert_eq!(spectator.log_number_ratio, dust.streams[1].log_number_ratio);
        let total_dp = V::from(m.flux) * m.energy * scale + V::from(d.flux)
            - V::from(initial.flux) * initial.energy * scale;
        assert!(total_dp.norm() < 3e-15, "momentum residual {total_dp:?}");
        let endpoint = m.energy * scale + d.energy - total_initial;
        assert!(
            work.abs() < 2e-14 && endpoint.abs() < 2e-14 && (work - endpoint).abs() < 3e-15,
            "{work:e} {endpoint:e}"
        );
        println!("recoil intervals {steps} final_p {:.15e} energy_work {work:e} endpoint {endpoint:e} momentum {:.3e}",p.norm(),total_dp.norm());
        (p.norm(), work)
    }
    #[test]
    fn moving_scatterer_drag_conservation_and_time_refinement() {
        let a = evolve(4).0;
        let b = evolve(8).0;
        let c = evolve(16).0;
        let d = evolve(32).0;
        assert!((c - d).abs() < (b - c).abs() && (b - c).abs() < (a - b).abs());
    }
    #[test]
    fn isotropic_normal_sky_has_the_covariant_thomson_drag_coefficient() {
        let beta = V::new(0.2, -0.1, 0.07);
        let g = 1.0 / (1.0 - beta.norm_squared()).sqrt();
        let rho_rad = 0.65;
        let mut dust = Dust::opposed(0.35, beta.into()).unwrap();
        let mass = dust.beam(0).unwrap().normal_mass_density;
        let p0 = V::from(dust.streams[0].p);
        let mut sky = initial_sky(12, 28).unwrap();
        let depth = 1e-6;
        scatter_with_recoil(&mut sky, &mut dust, depth, rho_rad / (4. * PI)).unwrap();
        let host_drag = (V::from(dust.streams[0].p) - p0) * mass / depth;
        let expected = -(4. / 3.) * rho_rad * g.powi(3) * beta;
        assert!(
            (host_drag - expected).norm() < 6e-6 * expected.norm(),
            "{host_drag:?} {expected:?}"
        );
    }

    #[test]
    fn radiation_dominated_step_resolves_host_acceleration() {
        let mut sky = initial_sky(5, 12).unwrap();
        let rho_rad = 0.98;
        let mut dust = Dust::opposed(1.0 - rho_rad, [0.4, 0., 0.]).unwrap();
        let initial =
            dust.moments().unwrap().energy + moments(&sky).unwrap().energy * rho_rad / (4. * PI);
        let error = scatter_with_recoil(&mut sky, &mut dust, 0.05, rho_rad / (4. * PI)).unwrap();
        let final_energy =
            dust.moments().unwrap().energy + moments(&sky).unwrap().energy * rho_rad / (4. * PI);
        assert!(error.abs() < 2e-14 && (final_energy - initial).abs() < 2e-14);
        assert!(dust.streams[0].p[0].abs() < 0.1);
    }

    #[test]
    fn tensor_gain_normalizes_distorted_rest_angles() {
        let mut sky = initial_sky(5, 12).unwrap();
        for p in &mut sky {
            p.weight *= 1. + 0.3 * p.direction.x * p.direction.y;
        }
        let b = V::new(0.22, 0.11, -0.14);
        let t = gain_map(&sky, b).unwrap();
        let mut a = M::zeros();
        for p in &sky {
            let (e, _, d) = boost(p.direction, b).unwrap();
            a += GAIN * p.weight / (d * d) * projector(&e);
        }
        assert!((t * a * t - M::identity()).norm() < 4e-15);
        let mut pencil = sky[0].clone();
        pencil.weight = 4. * PI;
        assert!(gain_map(&[pencil], V::zeros()).is_err());
    }
}
