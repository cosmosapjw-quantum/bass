//! Boundary-valid ideal atomic H/He gas and explicit radiation-unit adapters.
//! No chemistry/cooling provider or physical temperature-fit domain is admitted.
use crate::coupled_primary::PrimaryPacket;
use crate::{
    CharacteristicRay, ForwardError, HHeModel, HHeState, PhotonNode, PhotonPacket, MPC_CM,
};

#[derive(Clone, Copy, Debug)]
pub struct IgmGasState {
    /// HII, HeII, HeIII; neutral fractions are complements, not independent data.
    pub fractions: [f64; 3],
    /// Thermal energy per hydrogen nucleus, erg/H (NOT existing PrimaryState's eV/H).
    pub w_erg_per_h: f64,
}
#[derive(Clone, Copy, Debug)]
pub struct IgmEos {
    pub electron_density_cm3: f64,
    pub temperature_k: f64,
    pub u_erg_cm3: f64,
}
fn invalid() -> ForwardError {
    ForwardError::InvalidInput("IGM_STATE_OR_UNIT_DOMAIN")
}
fn positive(x: f64) -> Result<f64, ForwardError> {
    if x.is_normal() && x > 0.0 {
        Ok(x)
    } else {
        Err(invalid())
    }
}
fn nonnegative(x: f64) -> Result<f64, ForwardError> {
    if x == 0.0 {
        Ok(x)
    } else {
        positive(x)
    }
}
fn product(x: f64, y: f64) -> Result<f64, ForwardError> {
    nonnegative(x)?;
    nonnegative(y)?;
    if x == 0.0 || y == 0.0 {
        Ok(0.0)
    } else {
        positive(x * y)
    }
}
fn ratio(x: f64, y: f64) -> Result<f64, ForwardError> {
    nonnegative(x)?;
    positive(y)?;
    if x == 0.0 {
        Ok(0.0)
    } else {
        positive(x / y)
    }
}
// Reuse the existing owner of kB/eV constants and the algebraic HHe EOS.
// Only validate_state/electron_density/temperature are invoked, never its
// synthetic coefficients, rate evaluation, photon energies or thermal solver.
fn eos_model(n_h: f64, n_he: f64) -> Result<HHeModel, ForwardError> {
    positive(n_h)?;
    nonnegative(n_he)?;
    let mut model = HHeModel::controlled_fixture();
    model.n_h_cm3 = n_h;
    model.n_he_cm3 = n_he;
    model.validate()?;
    Ok(model)
}
fn hhe_state(fractions: [f64; 3], u: f64) -> HHeState {
    HHeState {
        fractions,
        u_erg_cm3: u,
        photon_cm3: [0.0; 3],
        escaped_erg_cm3: 0.0,
    }
}

impl IgmGasState {
    pub fn new(fractions: [f64; 3], w_erg_per_h: f64) -> Result<Self, ForwardError> {
        positive(w_erg_per_h)?;
        eos_model(1.0, 0.0)?.validate_state(&hhe_state(fractions, 0.0))?;
        Ok(Self {
            fractions,
            w_erg_per_h,
        })
    }
    pub fn from_temperature(
        fractions: [f64; 3],
        n_h: f64,
        n_he: f64,
        t: f64,
    ) -> Result<Self, ForwardError> {
        positive(t)?;
        let model = eos_model(n_h, n_he)?;
        let ne = model.electron_density(&hhe_state(fractions, 0.0))?;
        let particles_per_h = positive((n_h + n_he + ne) / n_h)?;
        let w = positive(product(1.5 * model.kb_erg_k, t)? * particles_per_h)?;
        let state = Self::new(fractions, w)?;
        state.eos(n_h, n_he)?;
        Ok(state)
    }
    pub fn eos(&self, n_h: f64, n_he: f64) -> Result<IgmEos, ForwardError> {
        Self::new(self.fractions, self.w_erg_per_h)?;
        let model = eos_model(n_h, n_he)?;
        let u = positive(self.w_erg_per_h * n_h)?;
        let s = hhe_state(self.fractions, u);
        let ne = nonnegative(model.electron_density(&s)?)?;
        // Check positive species contributions so a subnormal product is not
        // silently rounded to zero by the legacy algebraic EOS.
        product(n_h, self.fractions[0])?;
        product(n_he, self.fractions[1] + 2.0 * self.fractions[2])?;
        // The legacy EOS permits subnormal denominators. Our explicit
        // normal-intermediate contract rejects that loss of relative precision.
        positive(3.0 * model.kb_erg_k * positive(n_h + n_he + ne)?)?;
        let t = positive(model.temperature(&s)?)?;
        Ok(IgmEos {
            electron_density_cm3: ne,
            temperature_k: t,
            u_erg_cm3: u,
        })
    }
    /// Exact monatomic adiabatic map at FIXED fractions: w and T scale as a^-2.
    /// No new chemistry evolution, adaptive integration or ledger is implied.
    pub fn adiabatic_to(&self, a0: f64, a1: f64) -> Result<Self, ForwardError> {
        Self::new(self.fractions, self.w_erg_per_h)?;
        let scale = positive(ratio(a0, a1)?)?;
        Self::new(
            self.fractions,
            positive(self.w_erg_per_h * positive(scale * scale)?)?,
        )
    }
}

pub fn w_erg_per_h_to_ev(w: f64) -> Result<f64, ForwardError> {
    ratio(w, HHeModel::controlled_fixture().ev_erg)
}
pub fn w_ev_per_h_to_erg(w: f64) -> Result<f64, ForwardError> {
    product(w, HHeModel::controlled_fixture().ev_erg)
}
fn validate_primary(p: &PrimaryPacket) -> Result<(), ForwardError> {
    positive(p.energy_ev)?;
    nonnegative(p.per_h)?;
    Ok(())
}
/// Count conversion uses nH0=nH(a)*a^3, NOT the proper endpoint density.
/// Ray occupation is set to zero: packet count is a distinct measure and is
/// never encoded as phase-space occupation by these adapters.
pub fn primary_to_photon_packet(
    p: &PrimaryPacket,
    n_h0: f64,
    direction: [f64; 3],
) -> Result<PhotonPacket, ForwardError> {
    validate_primary(p)?;
    positive(n_h0)?;
    PhotonPacket::new(
        CharacteristicRay::new(p.energy_ev, direction, 0.0)?,
        product(p.per_h, n_h0)?,
    )
}
pub fn photon_packet_to_primary(
    p: &PhotonPacket,
    n_h0: f64,
) -> Result<PrimaryPacket, ForwardError> {
    PhotonPacket::new(p.ray, p.comoving_count_cm3)?;
    positive(p.ray.energy_ev)?;
    Ok(PrimaryPacket {
        energy_ev: p.ray.energy_ev,
        per_h: ratio(p.comoving_count_cm3, n_h0)?,
    })
}
pub fn primary_to_photon_node(p: &PrimaryPacket, n_h0: f64) -> Result<PhotonNode, ForwardError> {
    validate_primary(p)?;
    positive(n_h0)?;
    Ok(PhotonNode {
        energy_ev: p.energy_ev,
        n_comoving_per_cmpc3: product(product(p.per_h, n_h0)?, MPC_CM.powi(3))?,
    })
}
pub fn photon_node_to_primary(p: &PhotonNode, n_h0: f64) -> Result<PrimaryPacket, ForwardError> {
    positive(p.energy_ev)?;
    Ok(PrimaryPacket {
        energy_ev: p.energy_ev,
        per_h: ratio(ratio(p.n_comoving_per_cmpc3, MPC_CM.powi(3))?, n_h0)?,
    })
}
