//! Metric-signature and finite-boost diagnostics for `[Omega,v1,v2,v3]`.

use crate::matter::{MatterError, MatterState};

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct TiltInvariants {
    pub lorentz_gamma: f64,
    pub u_norm_residual: f64,
    pub density_margin: f64,
    pub tilt_margin: f64,
}

pub fn tilt_invariants(state: MatterState) -> Result<TiltInvariants, MatterError> {
    state.validate()?;
    let v2 = state.v[0] * state.v[0] + state.v[1] * state.v[1] + state.v[2] * state.v[2];
    let tilt_margin = 1.0 - v2;
    let lorentz_gamma = 1.0 / tilt_margin.sqrt();
    let u_norm_residual = -lorentz_gamma * lorentz_gamma + lorentz_gamma * lorentz_gamma * v2 + 1.0;
    Ok(TiltInvariants {
        lorentz_gamma,
        u_norm_residual,
        density_margin: state.omega,
        tilt_margin,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rf03_tilt_normalization_uses_minus_plus_plus_plus_signature() {
        let state = MatterState::new(0.3, [0.2, -0.1, 0.05]).unwrap();
        let observed = tilt_invariants(state).unwrap();
        assert!(observed.u_norm_residual.abs() <= 4.0e-16);
        assert!(observed.density_margin >= 0.0);
        assert!(observed.tilt_margin > 0.0);
    }
}
