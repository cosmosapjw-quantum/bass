//! Exact frame quantities of a slice: the radiation energy (Landau) frame, the
//! material stream velocities and an observer, with relativistic relative
//! velocities. These separate a *local boost* (observer relative to the radiation
//! energy frame) from a *global tilt* (material velocity relative to the normal
//! congruence and to the radiation frame) without any multipole expansion
//! (R113 THEORY D8).
//!
//! The energy frame u_E = gamma (n + beta) solves T^a_b u^b = -rho_E u^a. With the
//! normal-frame flux f = q/E and normalized stress P = P/E this is
//! beta (1 - f.beta) = f - P beta. In u_E the bolometric flux, hence the dipole of
//! the bolometric intensity, vanishes. A boosted isotropic sky returns its boost.
use super::RadiationMoments;
use nalgebra::{Matrix3, Vector3};

type V = Vector3<f64>;
type M = Matrix3<f64>;

/// Normalized radiation moments: (energy, q/E, P/E).
pub type Normalized = (f64, [f64; 3], [[f64; 3]; 3]);

/// Energy-weighted total of several radiation species with scale factors.
pub fn combine(parts: &[(f64, &RadiationMoments)]) -> Result<Normalized, String> {
    let mut energy = 0.0;
    let mut flux = V::zeros();
    let mut pressure = M::zeros();
    for (scale, m) in parts {
        let e = scale * m.energy;
        if !e.is_finite() || e < 0.0 {
            return Err("species energy must be finite and nonnegative".into());
        }
        energy += e;
        flux += V::from(m.flux) * e;
        pressure += M::from_fn(|i, j| m.pressure[i][j]) * e;
    }
    if energy.is_nan() || energy <= 0.0 {
        return Err("radiation energy must be positive".into());
    }
    Ok((
        energy,
        (flux / energy).into(),
        std::array::from_fn(|i| std::array::from_fn(|j| pressure[(i, j)] / energy)),
    ))
}

/// Velocity of the energy frame of a stress tensor with normalized flux and stress.
pub fn energy_frame(
    flux_over_e: [f64; 3],
    pressure_over_e: [[f64; 3]; 3],
) -> Result<[f64; 3], String> {
    let f = V::from(flux_over_e);
    let p = M::from_fn(|i, j| pressure_over_e[i][j]);
    if !f.iter().chain(p.iter()).all(|x| x.is_finite()) || f.norm() >= 1.0 {
        return Err("energy frame needs finite moments with subluminal energy flow".into());
    }
    let mut b = f * 0.75;
    for _ in 0..64 {
        let fb = f.dot(&b);
        let g = b * (1.0 - fb) - f + p * b;
        if g.norm() <= 4.0 * f64::EPSILON * (1.0 + f.norm()) {
            break;
        }
        let j = M::identity() * (1.0 - fb) - b * f.transpose() + p;
        let db = j.lu().solve(&g).ok_or("singular energy-frame Jacobian")?;
        b -= db;
        if !b.iter().all(|x| x.is_finite()) || b.norm() >= 1.0 {
            return Err("energy-frame iteration left the timelike domain".into());
        }
    }
    let fb = f.dot(&b);
    if (b * (1.0 - fb) - f + p * b).norm() > 1e-12 * (1.0 + f.norm()) {
        return Err("energy-frame iteration did not converge".into());
    }
    Ok(b.into())
}

/// Velocity of `object` measured in the rest frame of `frame` (both relative to the
/// normal tetrad), using the pure boost of the normal tetrad to `frame`.
pub fn relative_velocity(frame: [f64; 3], object: [f64; 3]) -> Result<[f64; 3], String> {
    let bf = V::from(frame);
    let bo = V::from(object);
    if bf.norm_squared().is_nan()
        || bf.norm_squared() >= 1.0
        || bo.norm_squared().is_nan()
        || bo.norm_squared() >= 1.0
    {
        return Err("relative velocity needs subluminal velocities".into());
    }
    let gf = 1.0 / (1.0 - bf.norm_squared()).sqrt();
    let go = 1.0 / (1.0 - bo.norm_squared()).sqrt();
    let t = go;
    let x = bo * go;
    let t_prime = gf * (t - bf.dot(&x));
    let b2 = bf.norm_squared();
    let x_prime = if b2 > 0.0 {
        x + bf * ((gf - 1.0) / b2 * bf.dot(&x)) - bf * (gf * t)
    } else {
        x
    };
    Ok((x_prime / t_prime).into())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::homogeneous_sky::{initial_sky, moments, transformed};

    #[test]
    fn boosted_isotropic_sky_has_its_boost_as_energy_frame() {
        let sky = initial_sky(14, 32).unwrap();
        let rest = moments(&sky).unwrap();
        let b0 = energy_frame(rest.flux, rest.pressure).unwrap();
        assert!(V::from(b0).norm() < 1e-14);
        for beta in [[0.1, -0.05, 0.02], [0.0, 0.0, 0.6], [0.3, 0.2, -0.4]] {
            let seen: Vec<_> = sky
                .iter()
                .map(|p| transformed(p, V::from(beta)).unwrap())
                .collect();
            let m = moments(&seen).unwrap();
            let b = energy_frame(m.flux, m.pressure).unwrap();
            // In the observer frame the radiation frame moves with -beta.
            assert!(
                (V::from(b) + V::from(beta)).norm() < 1e-12,
                "{b:?} {beta:?}"
            );
        }
    }

    #[test]
    fn relative_velocity_inverts_and_composes_collinearly() {
        let b = [0.3, -0.2, 0.1];
        assert!(V::from(relative_velocity(b, b).unwrap()).norm() < 1e-16);
        assert_eq!(relative_velocity([0.0; 3], b).unwrap(), b);
        let r = relative_velocity([0.5, 0.0, 0.0], [0.8, 0.0, 0.0]).unwrap();
        assert!((r[0] - (0.8 - 0.5) / (1.0 - 0.4)).abs() < 1e-15 && r[1] == 0.0);
        assert!(relative_velocity([1.0, 0.0, 0.0], b).is_err());
    }
}
