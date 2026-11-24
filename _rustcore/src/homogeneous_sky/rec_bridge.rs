//! Material-rest-frame input of a directional Planck/Sobolev closure.
//! The geometric rate is exact for the supplied beta and beta' (eta clock).
//! Bolometric temperatures are an approximation once spectra mix.
use super::{boost, Photon, V};
use crate::kinetic::characteristics::{char_rhs_split, Background};
use crate::kinetic::lie_history::RayNode;

fn packed(m: [[f64; 3]; 3]) -> [f64; 6] {
    [m[0][0], m[1][1], m[2][2], m[0][1], m[0][2], m[1][2]]
}
/// -(d ln E_material / dt_ray_material)/H_normal; includes the derivative of
/// the local Doppler factor. beta_prime is d beta/d eta, including recoil
/// and tetrad rotation if present. Not an atom proper-time derivative.
/// A negative rate is permitted here but rejected by the Sobolev assembler.
pub fn material_expansion_factor(
    node: &RayNode,
    e: [f64; 3],
    beta: [f64; 3],
    beta_prime: [f64; 3],
) -> Result<f64, String> {
    let e = V::from(e);
    let b = V::from(beta);
    let db = V::from(beta_prime);
    if !e.norm_squared().is_finite()
        || (e.norm_squared() - 1.).abs() > 1e-9
        || !db.iter().all(|x| x.is_finite())
        || !node
            .shear
            .iter()
            .flatten()
            .chain(node.n.iter().flatten())
            .chain(&node.a)
            .chain(&node.rotation)
            .all(|x| x.is_finite())
    {
        return Err("invalid material-frame geometry, direction or velocity derivative".into());
    }
    let (_, _, d) = boost(e, b)?;
    let bg = Background {
        h: 1.,
        sigma: packed(node.shear),
        n: packed(node.n),
        rot: node.rotation,
        a: node.a,
    };
    let (de, log_e) = char_rhs_split(&e.into(), 0., 0., &bg);
    let gamma2 = 1. / (1. - b.norm_squared());
    let log_d = gamma2 * b.dot(&db) - (db.dot(&e) + b.dot(&V::from(de))) / (1. - b.dot(&e));
    let rate = -(log_e + log_d) / d;
    if rate.is_finite() {
        Ok(rate)
    } else {
        Err("nonfinite material expansion rate".into())
    }
}

#[derive(Debug, Clone)]
pub struct MaterialDirectionalSky {
    pub weights: Vec<f64>,
    pub temperature_k: Vec<f64>,
    pub expansion_factor: Vec<f64>,
}
/// Unit bolometric intensity corresponds to t_unit_k. This is the absolute
/// emission temperature for the standard unit-intensity initial sky.
/// No renormalization to the instantaneous monopole is made.
pub fn material_directional_sky(
    rays: &[Photon],
    node: &RayNode,
    beta: [f64; 3],
    beta_prime: [f64; 3],
    t_unit_k: f64,
) -> Result<MaterialDirectionalSky, String> {
    if rays.is_empty() || !t_unit_k.is_finite() || t_unit_k <= 0. {
        return Err("material sky needs rays and a positive absolute temperature scale".into());
    }
    let mut out = MaterialDirectionalSky {
        weights: Vec::with_capacity(rays.len()),
        temperature_k: Vec::with_capacity(rays.len()),
        expansion_factor: Vec::with_capacity(rays.len()),
    };
    for p in rays {
        let (_, _, d) = boost(p.direction, V::from(beta))?;
        let w = p.weight / d.powi(2);
        let t = t_unit_k * p.screen.trace().sqrt().sqrt() * d;
        let f = material_expansion_factor(node, p.direction(), beta, beta_prime)?;
        if !w.is_finite() || w <= 0. || !t.is_finite() || t <= 0. || f <= 0. {
            return Err(
                "positive finite material weights, temperature and Sobolev expansion required"
                    .into(),
            );
        }
        out.weights.push(w);
        out.temperature_k.push(t);
        out.expansion_factor.push(f);
    }
    Ok(out)
}

impl MaterialDirectionalSky {
    /// Evaluate the pinned original REC Rust source in the material frame.
    /// n_h is proper number density, H is the normal expansion in s^-1.
    /// This remains a pointwise Planck/TLA closure, not an integrated history.
    pub fn rec_source(
        &self,
        n_h_m3: f64,
        hubble_s: f64,
        state: rec_microphysics::hydrogen_peebles::RetainedState,
        matter_temperature_k: f64,
    ) -> Result<
        rec_microphysics::anisotropic::AnisotropicSource,
        rec_microphysics::anisotropic::AnisotropyError,
    > {
        use rec_microphysics::anisotropic::{anisotropic_two_temperature_source, DirectionalSky};
        let sky = DirectionalSky {
            weights: &self.weights,
            temperature_k: &self.temperature_k,
            expansion_factor: &self.expansion_factor,
        };
        anisotropic_two_temperature_source(&sky, n_h_m3, hubble_s, state, matter_temperature_k)
    }
}
