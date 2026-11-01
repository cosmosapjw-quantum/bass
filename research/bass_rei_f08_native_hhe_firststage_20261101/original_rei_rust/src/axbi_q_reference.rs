//! Optional covariant-momentum photon reference for conditional AXBI source.
//! The original source spectral cells are used unchanged, so this is not a
//! continuous-blackbody quadrature or a coupled EoR solver.
use crate::axbi_sources::AxbiSource;
use crate::{
    Absorber, AtomicProvider, CharacteristicRay, ForwardError, GeometrySnapshot, HHeModel,
};

fn invalid() -> ForwardError {
    ForwardError::InvalidInput("AXBI_Q_REFERENCE_DOMAIN")
}
fn nonnegative(v: f64) -> bool {
    v.is_finite() && v >= 0.
}

/// k_i=c*q_i=a_i*E*n_i (eV), with physical q_i a covariant momentum.
#[derive(Clone, Copy, Debug)]
pub struct CovariantPhoton {
    pub k_ev: [f64; 3],
    pub photons_per_h: f64,
}
impl CovariantPhoton {
    pub fn from_local(
        g: &GeometrySnapshot,
        energy_ev: f64,
        direction: [f64; 3],
        photons_per_h: f64,
    ) -> Result<Self, ForwardError> {
        g.volume_factor()?;
        if !nonnegative(photons_per_h) {
            return Err(invalid());
        }
        let ray = CharacteristicRay::new(energy_ev, direction, 0.)?;
        let k_ev = std::array::from_fn(|i| g.scale_factors[i] * ray.energy_ev * ray.direction[i]);
        if !k_ev.iter().all(|v| v.is_finite()) {
            return Err(invalid());
        }
        Ok(Self {
            k_ev,
            photons_per_h,
        })
    }
    /// Exact source-free energy for supplied geometry snapshots.
    pub fn energy_at(&self, g: &GeometrySnapshot) -> Result<f64, ForwardError> {
        g.volume_factor()?;
        let p: [f64; 3] = std::array::from_fn(|i| self.k_ev[i] / g.scale_factors[i]);
        let e = p[0].hypot(p[1]).hypot(p[2]);
        if !e.is_finite() || e <= 0. {
            return Err(invalid());
        }
        Ok(e)
    }
    pub fn direction_at(&self, g: &GeometrySnapshot) -> Result<[f64; 3], ForwardError> {
        let e = self.energy_at(g)?;
        let d = std::array::from_fn(|i| (self.k_ev[i] / g.scale_factors[i]) / e);
        if !d.iter().all(|x| x.is_finite()) {
            return Err(invalid());
        }
        Ok(d)
    }
}

/// A bounded source cohort evaluated in the LOCAL emission frame. Direction
/// weights are already included in the native AxbiSource; no extra Jacobian.
pub fn emit_from_axbi_source(
    source: &AxbiSource,
    g: &GeometrySnapshot,
    redshift: f64,
    duration_s: f64,
) -> Result<Vec<CovariantPhoton>, ForwardError> {
    g.volume_factor()?;
    if !nonnegative(duration_s) {
        return Err(invalid());
    }
    let rate = source.at_redshift(redshift)?.per_h_s;
    let mut out = Vec::with_capacity(source.spectral_cells.len() * source.angular_cells.len());
    for ang in &source.angular_cells {
        let direction = [(1. - ang.mu * ang.mu).sqrt(), 0., ang.mu];
        for cell in &source.spectral_cells {
            let n = rate * duration_s * cell.photon_fraction * ang.count_fraction;
            out.push(CovariantPhoton::from_local(
                g,
                cell.energy_ev,
                direction,
                n,
            )?);
        }
    }
    Ok(out)
}

#[derive(Clone, Debug)]
pub struct FrozenAbsorption {
    pub final_packet: CovariantPhoton,
    /// HI, HeI, HeII photon counts per H.
    pub absorbed_per_h: [f64; 3],
    pub binding_ev_per_h: f64,
    pub heat_ev_per_h: f64,
}

/// Exact exponential photon loss at frozen proper gas density and geometry.
/// This is a reference ONE-STEP absorber, not moving-threshold integration
/// or the coupled chemistry/temperature solver.
pub fn absorb_frozen_gas(
    packet: &CovariantPhoton,
    g: &GeometrySnapshot,
    neutral_absorber_cm3: [f64; 3],
    duration_s: f64,
) -> Result<FrozenAbsorption, ForwardError> {
    if !nonnegative(duration_s)
        || !nonnegative(packet.photons_per_h)
        || !neutral_absorber_cm3.iter().all(|v| nonnegative(*v))
    {
        return Err(invalid());
    }
    let e = packet.energy_at(g)?;
    let model = HHeModel::controlled_fixture();
    let provider = AtomicProvider::reference();
    let species = [Absorber::HI, Absorber::HeI, Absorber::HeII];
    let mut rate = [0.; 3];
    for (i, a) in species.iter().enumerate() {
        rate[i] = model.c_cm_s * neutral_absorber_cm3[i] * provider.cross_section(*a, e)?;
        if !nonnegative(rate[i]) {
            return Err(invalid());
        }
    }
    let lambda: f64 = rate.iter().sum();
    if !nonnegative(lambda) {
        return Err(invalid());
    }
    let lost = if lambda > 0. {
        packet.photons_per_h * -(-lambda * duration_s).exp_m1()
    } else {
        0.
    };
    if !nonnegative(lost) {
        return Err(invalid());
    }
    let absorbed = std::array::from_fn(|i| {
        if lambda > 0. {
            lost * rate[i] / lambda
        } else {
            0.
        }
    });
    let mut binding = 0.;
    let mut heat = 0.;
    for (i, n) in absorbed.iter().enumerate() {
        binding += n * model.threshold_ev[i];
        heat += n * (e - model.threshold_ev[i]);
    }
    Ok(FrozenAbsorption {
        final_packet: CovariantPhoton {
            k_ev: packet.k_ev,
            photons_per_h: packet.photons_per_h - lost,
        },
        absorbed_per_h: absorbed,
        binding_ev_per_h: binding,
        heat_ev_per_h: heat,
    })
}
